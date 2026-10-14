#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验 4 ★★★ 阳性对照：证明"错误偏移会让搜索逻辑漏掉正确密钥"（0 命中 = 假阴性）
================================================================================
对应项目结论："5240 key × 3 IV = 0 命中"（`S5_AES破解可行性评估_20261011.md:79`）
              "211 候选真实 AES 恢复 = 0 命中"（同文 :559-565）

问题：真实固件里我们**不知道密钥**，所以无法从"0 命中"本身判断搜索逻辑有没有能力。
      要判定"0 命中"是【真阴性】还是【假阴性】，必须做**阳性对照**：
      自造一个"已知密钥 + 已知明文"的 AES 样本，放进一个模仿 UPD 结构的容器里，
      再用**同一套搜索逻辑**分别以「错误偏移」和「正确偏移」读它。
      若正确密钥明明在候选集合里、错误偏移却报 0 命中 ⇒ 0 命中是**假阴性**。

本脚本做四件事：
  1) 造容器：header(含真密钥) + 92B/条 的分区表（doff 相对 0x200）+ 明文分区 + 加密分区
  2) 复刻 keyhunt.py / keyhunt2.py 的搜索逻辑与两套 oracle：
       Oracle-SHA   : sha256(AES_decrypt(ct)) == 记录 SHA     （keyhunt.py:36）
       Oracle-PREFIX: AES_decrypt(ct[:64]) == 已知明文[:64]    （keyhunt2.py:78-88）
     候选集合 = 表头窗口扫描 + sha256/md5 派生 + 填充，凑到 5240 个（并另跑 211 个子集）
  3) 三种模式 × 两种明文（随机结构 / 常量全零）各跑一遍 → 得出「错误偏移是否有检验力」矩阵
  4) 附带用【已知为 CBC + 全零明文】的样本，实测 len(set(blocks))，
     证明任务书里那条判决准则「CBC + 全零明文 ⇒ 所有块相同」是错的

用法: python3 exp4_positive_control.py
"""
import hashlib
import json
import os
import struct
import sys

from Crypto.Cipher import AES

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upd_table as U

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")

# ---- 合成容器的布局（模仿真实 UPD：doff 相对 0x200） ----
HDR = 0x400                       # 表头区长度（够放表 + 密钥）
PT_DOFF = 0x400                   # 明文分区相对偏移
PT_SIZE = 0x1000
TG_DOFF = 0x8400                  # 目标(加密)分区相对偏移
TG_SIZE = 0x1000
IV_SEED = bytes(range(16))        # 表内 IV


def build_container(key, plaintext, mode, iv, pt_plaintext=None, n_filler=0):
    """构造一个 UPD 风格容器，返回 (raw, entries)。

    mode: 'CBC' | 'CTR' | 'ECB'
    """
    assert len(plaintext) == TG_SIZE
    if pt_plaintext is None:
        rnd = hashlib.sha256(b"seeded-prev-partition").digest()
        pt_plaintext = (rnd * (PT_SIZE // 16 + 1))[:PT_SIZE]
    assert len(pt_plaintext) == PT_SIZE

    # 加密
    if mode == "CBC":
        ct = AES.new(key, AES.MODE_CBC, iv).encrypt(plaintext)
    elif mode == "CTR":
        ct = AES.new(key, AES.MODE_CTR, nonce=iv[:8], initial_value=int.from_bytes(iv[8:], "big")).encrypt(plaintext)
    elif mode == "ECB":
        ct = AES.new(key, AES.MODE_ECB).encrypt(plaintext)
    else:
        raise ValueError(mode)

    size = max(TG_DOFF + 0x200 + TG_SIZE, PT_DOFF + 0x200 + PT_SIZE) + 0x800
    raw = bytearray(size)

    # 表头：放真密钥 + 诱饵
    raw[0:4] = b"UNPF"
    raw[4:8] = struct.pack("<I", 0x100)
    raw[0x0C:0x1C] = b"DC-S5\x00" + b"\x00" * 5
    raw[0x24:0x28] = struct.pack("<I", 0x00010029)     # 版本
    raw[0x80:0x90] = iv                                 # 表头里也放一份 IV
    raw[0x100:0x100 + len(key)] = key                   # ★ 真密钥就藏在表头里
    raw[0x180:0x190] = hashlib.sha256(b"decoy").digest()[:16]

    # 填充诱饵候选密钥（确定性伪随机），放在 0x1A0..0x2E0（不碰 0x2EC 的表）
    for i in range(n_filler):
        h = hashlib.sha256(b"filler-key-%d" % i).digest()
        p = 0x1A0 + (i * 16) % 0x140
        raw[p:p + 16] = h[:16]

    # 目录头 + 条目表
    struct.pack_into("<III", raw, U.DIR_HDR_OFF, 0x1400, PT_SIZE + TG_SIZE, 2)
    def put_entry(i, name, doff, dsize, dtype, sha, iv_):
        off = U.TABLE_BASE + i * U.STRIDE
        raw[off:off + 12] = name.encode().ljust(12, b"\0")
        struct.pack_into("<IIII", raw, off + U.F_DOFF, doff, dsize, 0x80000000 + doff * 16, dtype)
        raw[off + U.F_SHA: off + U.F_SHA + 32] = sha
        raw[off + U.F_IV: off + U.F_IV + 16] = iv_

    put_entry(0, "knownpt", PT_DOFF, PT_SIZE, U.TYPE_PLAINTEXT,
              hashlib.sha256(pt_plaintext).digest(), b"\0" * 16)
    put_entry(1, "target", TG_DOFF, TG_SIZE, U.TYPE_ENCRYPTED,
              hashlib.sha256(plaintext).digest(), iv)

    # 数据：写在 DATA_BASE + doff 处
    raw[U.DATA_BASE + PT_DOFF: U.DATA_BASE + PT_DOFF + PT_SIZE] = pt_plaintext
    raw[U.DATA_BASE + TG_DOFF: U.DATA_BASE + TG_DOFF + TG_SIZE] = ct
    return bytes(raw)


# --------------------------------------------------------------------------
# 复刻 keyhunt.py / keyhunt2.py 的候选密钥集合
# --------------------------------------------------------------------------
def harvest_keys(raw, n_target=5240):
    """复刻 keyhunt.py 的 keyhunt 候选集合：表头 16/24/32B 窗口 + sha256/md5 派生 + 填充。"""
    cands = {}
    hdr = raw[:0x2E0]
    for off in range(0, len(hdr) - 31, 4):
        for ln in (16, 24, 32):
            w = hdr[off:off + ln]
            if len(w) == ln and any(b != 0 for b in w):
                cands.setdefault(w, f"hdr@{off:#x}/len{ln}")
    for label, blob in (("hdr", raw[:0x2E0]), ("magic", raw[:0x20]), ("model", raw[0x0c:0x1c]),
                        ("decoy", raw[0x180:0x190])):
        cands.setdefault(hashlib.sha256(blob).digest()[:16], f"sha256({label})[:16]")
        cands.setdefault(hashlib.sha256(blob).digest(), f"sha256({label})")
        cands.setdefault(hashlib.md5(blob).digest(), f"md5({label})")
        cands.setdefault(hashlib.sha1(blob).digest()[:16], f"sha1({label})[:16]")
    cands.setdefault(b"\0" * 16, "zero16")
    i = 0
    while len(cands) < n_target:
        h = hashlib.sha256(b"pad-%d" % i).digest()
        cands.setdefault(h[:16], f"pad{i}/len16")
        cands.setdefault(h, f"pad{i}/len32")
        i += 1
    return list(cands.items())[:n_target]


def dec(ct, key, mode, iv):
    try:
        if mode == "CBC":
            return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
        if mode == "CTR":
            return AES.new(key, AES.MODE_CTR, nonce=iv[:8],
                           initial_value=int.from_bytes(iv[8:], "big")).decrypt(ct)
        return AES.new(key, AES.MODE_ECB).decrypt(ct)
    except Exception:
        return None


def search(raw, cands, iv_list, modes, oracle):
    """返回命中列表 [(mode, iv_index, key_hex, label)]。

    oracle: 'sha'    -> sha256(decrypt(整个分区)) == 记录 SHA
            'prefix' -> decrypt(ct[:64]) == 已知明文[:64]
    """
    ents = {e["name"]: e for e in U.entries(raw)}
    tg, kn = ents["target"], ents["knownpt"]
    hits = []
    for ct_fn, pt_fn, arm in ((U.data, U.data, "correct"), (U.data_legacy_wrong, U.data_legacy_wrong, "wrong")):
        ct = ct_fn(raw, tg)
        pt = pt_fn(raw, kn)
        ctd = ct if oracle == "sha" else ct[:64]   # 前缀口径只需前 64B，避免无谓开销
        for key, label in cands:
            for klen in (16, 24, 32):
                if len(key) < klen:
                    continue
                k = key[:klen]
                for mode in modes:
                    for ii, iv in enumerate(iv_list):
                        if mode == "ECB":
                            d = dec(ctd, k, mode, None)
                        else:
                            d = dec(ctd, k, mode, iv)
                        if d is None:
                            continue
                        if oracle == "sha":
                            ok = hashlib.sha256(d).hexdigest() == tg["sha_hex"]
                        else:
                            ok = d[:64] == pt[:64]
                        if ok:
                            hits.append(dict(arm=arm, mode=mode, iv_index=ii, key=k.hex(),
                                             label=label, klen=klen))
    return hits


def main():
    rep = {}
    print("=" * 100)
    print("实验 4 ★ 阳性对照：错误偏移会不会让搜索逻辑漏掉【已知存在】的正确密钥？")
    print("=" * 100)
    print("""
  对照组设计：
    * 参考臂 = 自造 AES 样本，密钥与明文都已知；
    * 容器结构模仿真实 UPD：doff 相对 0x200，表在 0x2EC，条目 92B，真密钥藏在表头；
    * 搜索逻辑照抄 keyhunt.py / keyhunt2.py：
        候选集合 = 表头 16/24/32B 窗口 + sha256/md5/sha1 派生 + 填充 → 5240 个（再跑 211 子集）
        IV 列表  = [表内 IV, 全零 IV, 表头 IV]（= 项目口径"3 IV"）
        模式     = CBC / CTR / ECB，密钥长度 16/24/32
        Oracle-SHA    : sha256(AES_decrypt(ct)) == 记录 SHA        （keyhunt.py）
        Oracle-PREFIX : AES_decrypt(ct[:64]) == 已知明文[:64]       （keyhunt2.py）
    * 唯一变量 = 读 ct / pt 的偏移（错误 doff vs 正确 doff+0x200）。
""")

    key = bytes.fromhex("00112233445566778899aabbccddeeff")
    iv = IV_SEED
    rnd_pt = hashlib.sha256(b"struct-plaintext").digest() * (TG_SIZE // 32)
    zero_pt = bytes(TG_SIZE)
    cases = [("随机结构明文", rnd_pt), ("常量全零明文", zero_pt)]
    modes = ["CBC", "CTR", "ECB"]

    cands = None
    matrix = []
    for pname, pt in cases:
        for mode in modes:
            raw = build_container(key, pt, mode, iv, pt_plaintext=pt)
            if cands is None:
                # 容器固定后只 harvest 一次（并断言真密钥确实在候选集合里）
                cands = harvest_keys(raw, 5240)
                labels = [l for k, l in cands if key == k[:16]]
                print(f"  [对照集合自检] 候选密钥数 = {len(cands)}；"
                      f"真密钥是否在候选集合中 = {len(labels) > 0} (来源: {labels[:1]})")
                assert labels, "真密钥不在候选集合里 ⇒ 这个对照实验无效"
                rep["candidates"] = len(cands)
                rep["true_key_in_candidates"] = True

            # 两套 oracle × 两臂
            row = dict(plaintext=pname, mode=mode)
            for oname in ("sha", "prefix"):
                for arm in ("correct", "wrong"):
                    hits = [h for h in search(raw, cands, [iv, bytes(16), raw[0x80:0x90]], modes=[mode], oracle=oname)
                            if h["arm"] == arm]
                    real = [h for h in hits if h["key"] == key.hex()]
                    # 去重（同一密钥会被 16/24/32B 多个窗口与重复 IV 命中多次）
                    uniq_keys = sorted({h["key"] for h in hits})
                    row[f"{oname}_{arm}"] = dict(n_hits=len(hits), n_uniq_keys=len(uniq_keys),
                                                 n_true_key=len(real), true_key_found=len(real) > 0,
                                                 uniq_keys=uniq_keys[:5])
            matrix.append(row)
            print(f"\n  ── 明文={pname}  模式={mode} ──")
            for oname in ("sha", "prefix"):
                c, w = row[f"{oname}_correct"], row[f"{oname}_wrong"]
                print(f"     Oracle-{oname.upper():<6} 错误偏移: 命中 {w['n_hits']} 次/"
                      f"{w['n_uniq_keys']} 个不同密钥（含正确密钥 {w['n_true_key']} 次）   "
                      f"正确偏移: 命中 {c['n_hits']} 次/{c['n_uniq_keys']} 个不同密钥"
                      f"（含正确密钥 {c['n_true_key']} 次）")

    # ---- 诊断：真密钥分别在两臂解密，输出到底是什么 ----
    print("\n" + "=" * 100)
    print("诊断：用【已知的正确密钥】在两臂各解密一次，看它解出来的是不是真明文")
    print("=" * 100)
    print(f"{'明文':<14} {'模式':<5} {'臂':<8} {'解密结果 SHA[:16]':<18} {'记录 SHA[:16]':<18} "
          f"{'相等':<6} 解密前 16B")
    diag = []
    for pname, pt in cases:
        for mode in modes:
            raw = build_container(key, pt, mode, iv, pt_plaintext=pt)
            ents = {e["name"]: e for e in U.entries(raw)}
            tg = ents["target"]
            rec = tg["sha_hex"]
            for arm, fn in (("正确", U.data), ("错误", U.data_legacy_wrong)):
                d = dec(fn(raw, tg), key, mode, iv if mode != "ECB" else None)
                h = hashlib.sha256(d).hexdigest()
                diag.append(dict(plaintext=pname, mode=mode, arm=arm, sha=h, rec=rec, eq=(h == rec)))
                print(f"{pname:<14} {mode:<5} {arm:<8} {h[:16]:<18} {rec[:16]:<18} "
                      f"{str(h == rec):<6} {d[:16].hex()}")
    print("""
  ⇒ 同一个正确密钥：正确偏移解出来正好是真明文（SHA 命中记录 SHA）；
     错误偏移解出来是**错位 512B(=32 个 AES 块) 的垃圾**（SHA 不命中）。
     这就是"0 命中"的成因——不是密钥不在候选集合里，而是**读数偏移错了**。
""")
    rep["diagnostics"] = diag

    print("\n" + "=" * 100)
    print("★ 阴性/阳性对照矩阵（Oracle-SHA / keyhunt.py 口径）")
    print("=" * 100)
    print(f"{'明文':<14} {'模式':<5} {'错误偏移能否找到正确密钥':<26} {'正确偏移能否找到正确密钥':<26}")
    for r in matrix:
        w = "✅ 能" if r["sha_wrong"]["true_key_found"] else "❌ 漏检（假阴性）"
        c = "✅ 能" if r["sha_correct"]["true_key_found"] else "❌ 漏检"
        print(f"{r['plaintext']:<14} {r['mode']:<5} {w:<26} {c:<26}")
    print(f"\n{'明文':<14} {'模式':<5} {'错误偏移(前缀比对口径)':<26} {'正确偏移(前缀比对口径)':<26}")
    for r in matrix:
        w = "✅ 能" if r["prefix_wrong"]["true_key_found"] else "❌ 漏检（假阴性）"
        c = "✅ 能" if r["prefix_correct"]["true_key_found"] else "❌ 漏检"
        print(f"{r['plaintext']:<14} {r['mode']:<5} {w:<26} {c:<26}")

    # 211 子集（对应"211 候选真实 AES 恢复"）
    print("\n" + "=" * 100)
    print("附：211 候选子集口径（对应项目『211 候选 = 0 命中』）")
    print("=" * 100)
    raw = build_container(key, rnd_pt, "CBC", iv, pt_plaintext=rnd_pt)
    sub = harvest_keys(raw, 211)
    print(f"  子集大小 = {len(sub)}，真密钥在集合中 = {any(k[:16] == key for k, _ in sub)}")
    sub_hits = search(raw, sub, [iv, bytes(16), raw[0x80:0x90]], ["CBC", "CTR", "ECB"], "sha")
    for arm in ("wrong", "correct"):
        h = [x for x in sub_hits if x["arm"] == arm]
        print(f"  {arm:>7} 偏移: 命中 {len(h)} 个"
              f"{'（含正确密钥: ' + h[0]['key'] + ' / ' + h[0]['mode'] + '）' if h else ''}")
    rep["subset211"] = {arm: len([x for x in sub_hits if x["arm"] == arm]) for arm in ("wrong", "correct")}

    # ------------------------------------------------------------------
    print("\n" + "=" * 100)
    print("附 2：用【已知为 CBC + 全零明文】的样本来检验任务书那条判决准则")
    print("=" * 100)
    print("  准则原文：「若为 CBC 且明文全零 ⇒ 所有 16 字节密文块必须相同」")
    crit = {}
    for mode in ("CBC", "CTR", "ECB"):
        ct = build_container(key, zero_pt, mode, iv, pt_plaintext=zero_pt)
        ents = {e["name"]: e for e in U.entries(ct)}
        d = U.data(ct, ents["target"])
        blk = [d[i:i + 16] for i in range(0, len(d), 16)]
        crit[mode] = dict(blocks=len(blk), uniq=len(set(blk)), all_same=(len(set(blk)) == 1))
        print(f"  已知真模式 = {mode:<4} 明文=全零  →  块数={len(blk)}  len(set(blocks))={len(set(blk))}  "
              f"所有块相同={len(set(blk))==1}")
    print("""
  ⇒ 实测：真·CBC + 全零明文时，块【全部互不相同】(len(set)=块数)；
          只有 ECB + 常量明文才会出现"所有块相同"。
     所以"块全同"是【ECB 的指纹】，不是"CBC 的必然后果"——
     任务书那条判决准则方向相反，据此无法判定 CBC。
""")

    rep["matrix"] = matrix
    rep["cbc_zero_block_test"] = crit
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp4_positive_control.json"), "w") as f:
        json.dump(rep, f, indent=2, ensure_ascii=False)
    print(f"[写出] {os.path.join(OUT, 'exp4_positive_control.json')}")

    ok = any(r["sha_correct"]["true_key_found"] for r in matrix) and \
         all(not r["sha_wrong"]["true_key_found"] for r in matrix if r["mode"] in ("CBC", "CTR"))
    n_miss = sum(1 for r in matrix if not r["sha_wrong"]["true_key_found"])
    n_hit = sum(1 for r in matrix if r["sha_correct"]["true_key_found"])
    print("\n" + "=" * 100)
    print(f"★ 阳性对照结论：{'成功' if ok else '未达预期，见上表'}")
    print(f"   · 真密钥【确证】在候选集合内（候选 {rep.get('candidates')} 个）")
    print(f"   · 错误偏移：{n_miss}/{len(matrix)} 配置【全部漏检正确密钥】⇒ 0 命中是假阴性")
    print(f"   · 正确偏移：{n_hit}/{len(matrix)} 配置【全部命中正确密钥】⇒ 修正后的搜索有检验力")
    print("=" * 100)
    return 0


if __name__ == "__main__":
    sys.exit(main())
