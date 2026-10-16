#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验 5 ★★  用【修正后的 +0x200 偏移】在真实 S5 固件上重跑密钥搜索
================================================================================
对应项目待办（唯一权威文档 §7-2 #4）：
    「修 +0x200 后重跑密码学脚本 —— 让『0 命中』首次具检验力」

背景（14_.../06_密码学重跑/结论.md）：
  * 项目旧结论「5240 key × 3 IV = 0 命中 ⇒ 密钥非文件内派生」与
    「211 候选 = 0 命中」已被判定为【假阴性】——旧脚本把密文整体读错 512 B，
    即使正确密钥就在候选集合里也必然漏检（阳性对照 12/12 全部漏检）。
  * 但那次阳性对照用的是【合成样本】；真实固件上的搜索【从未用正确偏移重跑过】。
  * 本实验补上这一步。

本实验做四件事：
  1) 闸门：跑 upd_table.self_test，type=2 分区 sha256(data)==记录 SHA 必须 7/7，否则中止。
  2) 已知明文侦察：对全部 type=3 加密分区，比对「记录 SHA == 同长度可猜内容的 SHA256」，
     自动找出【明文已知】的加密分区（这是本次搜索唯一可用的 oracle 来源）。
  3) 真实搜索：复刻 keyhunt.py / keyhunt2.py 的候选密钥集合（表头窗口 / 摘要派生 /
     ECDSA 签名区 / PTool 表方案 / 填充），对每个已知明文目标，以
     {CBC, ECB, CTR×2 约定} x {记录 IV, 全零 IV, 表头 IV} x 密钥长度 {16,24,32} 穷举，
     oracle 用 256 字节前缀比对（2^-2048 假阳性），命中后再做整分区 SHA-256 确认。
     同时并行跑【错误偏移臂】(data_legacy_wrong)，对照修正前后的差异。
  4) 阳性对照（内联）：在【同一段搜索代码】上放一个仿 UPD 结构的合成样本（目标分区
     同样 256 KiB、明文全零、真密钥藏在表头），确认修正偏移能捞出真密钥、
     错误偏移漏检 —— 这样真实固件的任何「0 命中」才有检验力。

全程只读固件、不联网、不连接相机。

用法:
    python3 exp5_real_key_search_corrected.py [S5___V29.bin ...]
    # 不带参数时按候选路径列表自动查找 5 个 S5 版本固件
"""
from __future__ import annotations

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

# ---------------------------------------------------------------------------
# 目标固件（原项目大资产，本包只放指针；路径不存在会自动跳过）
# ---------------------------------------------------------------------------
ORIG = "/Users/<user>/Documents/ChatGPT/S5_逆向_项目总包_20261012"
FW_CANDIDATES = [
    os.path.join(ORIG, "02_固件二进制/DC-S5/S5___V29.bin"),
    os.path.join(ORIG, "02_固件二进制/DC-S5_版本历史/S5___V24.bin"),
    os.path.join(ORIG, "02_固件二进制/DC-S5_版本历史/S5___V23.bin"),
    os.path.join(ORIG, "02_固件二进制/DC-S5_版本历史/S5___V20.bin"),
    os.path.join(ORIG, "02_固件二进制/DC-S5_版本历史/S5___V11.bin"),
]

PREFIX = 256          # 前缀比对字节数（16 个 AES 块 = 2^-2048 假阳性）
HDR_END = 0x2E0       # 表头区上界（0x2E0 起是目录头，0x2EC 起是条目表）
PAD_TARGET = 5240     # 与项目「5240 候选」口径对齐的填充目标（成分分别统计）

PLAINTEXT_TEMPLATES = [
    ("all-0x00", lambda n: bytes(n)),
    ("all-0xFF", lambda n: b"\xFF" * n),
    ("all-0x55", lambda n: b"\x55" * n),
    ("all-0xAA", lambda n: b"\xAA" * n),
    ("increasing", lambda n: bytes(i & 0xFF for i in range(n))),
]


# ===========================================================================
# 候选密钥集合（复刻 keyhunt.py / keyhunt2.py，并补 PTool 表方案）
# ===========================================================================
def harvest_keys(raw: bytes, pad_target: int = PAD_TARGET):
    """返回 (cands, stats)；cands = [(key_bytes, label), ...]（按插入顺序去重）。"""
    cands = {}
    stats = dict(hdr_windows=0, ecdsa_windows=0, digests=0, ptool=0, strings=0, pad=0)

    def add(k, label):
        if not k or all(b == 0 for b in k):
            return False
        if k in cands:
            return False
        cands[k] = label
        return True

    hdr = raw[:HDR_END]

    # 1) 表头 16/24/32B 滑动窗口（keyhunt2 口径：逐字节步长）
    for off in range(0, len(hdr) - 15):
        for ln in (16, 24, 32):
            if off + ln <= len(hdr):
                if add(hdr[off:off + ln], "hdr@%#x/len%d" % (off, ln)):
                    stats["hdr_windows"] += 1

    # 2) ECDSA 签名区 0x220..0x280 窗口（keyhunt2 口径）
    sig = raw[0x220:0x280]
    for off in range(0, len(sig) - 15):
        if add(sig[off:off + 16], "ecdsa@%#x/len16" % (0x220 + off)):
            stats["ecdsa_windows"] += 1

    # 3) 摘要派生（sha256/md5/sha1 的多种截断）
    blobs = [
        ("hdr", raw[:HDR_END]),
        ("rsa_tail", raw[-512:]),
        ("magic", raw[:0x20]),
        ("chip", raw[0x0C:0x14]),
    ]
    for label, blob in blobs:
        for tag, d in (("sha256", hashlib.sha256(blob).digest()),
                       ("md5", hashlib.md5(blob).digest()),
                       ("sha1", hashlib.sha1(blob).digest())):
            if add(d[:16], "%s(%s)[:16]" % (tag, label)):
                stats["digests"] += 1
            if add(d, "%s(%s)" % (tag, label)):
                stats["digests"] += 1

    # 4) 明文常量（模型名等）
    for s in (b"panasonic", b"Panasonic", b"MC801", b"mc801", b"S5", b"DC-S5"):
        if add(s.ljust(16, b"\0"), "string:" + s.decode()):
            stats["strings"] += 1

    # 5) PTool 表方案（key[i] = file[base + i*0x200 + table[i]]）
    table = [77, 350, 198, 71, 290, 98, 136, 184, 206, 301, 281, 147, 611, 239, 8, 84]
    for base in (0x0, 0x200, 0x400, 0x800, 0x1000, 0x1400):
        k = bytearray(16)
        ok = True
        for i in range(16):
            o = base + i * 0x200 + table[i]
            if 0 <= o < len(raw):
                k[i] = raw[o]
            else:
                ok = False
                break
        if ok and add(bytes(k), "ptool(base=%#x)" % base):
            stats["ptool"] += 1

    # 6) 确定性填充至 pad_target（与项目「5240 候选」口径可比；单独统计）
    i = 0
    while len(cands) < pad_target:
        d = hashlib.sha256(b"pad-%d" % i).digest()
        if add(d[:16], "pad%d/len16" % i):
            stats["pad"] += 1
        if len(cands) < pad_target and add(d, "pad%d/len32" % i):
            stats["pad"] += 1
        i += 1

    return list(cands.items()), stats


# ===========================================================================
# 加解密辅助
# ===========================================================================
def decrypt(ct, key, mode, iv):
    if len(key) not in (16, 24, 32):
        return None
    try:
        if mode == "CBC":
            return AES.new(key, AES.MODE_CBC, iv).decrypt(ct)
        if mode == "ECB":
            return AES.new(key, AES.MODE_ECB).decrypt(ct)
        if mode == "CTR(nonce=IV[0:8],ctr=IV[8:16])":
            c = AES.new(key, AES.MODE_CTR, nonce=iv[:8],
                        initial_value=int.from_bytes(iv[8:], "big"))
            return c.decrypt(ct)
        if mode == "CTR(nonce=IV[0:8],ctr=0)":
            c = AES.new(key, AES.MODE_CTR, nonce=iv[:8], initial_value=0)
            return c.decrypt(ct)
    except Exception:
        return None
    return None


MODES = ["CBC", "ECB", "CTR(nonce=IV[0:8],ctr=IV[8:16])", "CTR(nonce=IV[0:8],ctr=0)"]


def iv_list_for(raw, entry):
    """3 IV 口径：记录 IV / 全零 IV / 表头 IV（与 exp4 一致）。"""
    return [("rec", entry["iv"]), ("zero", bytes(16)), ("hdr", raw[0x80:0x90])]


# ===========================================================================
# 搜索：对单个「已知明文」目标分区
# ===========================================================================
def search_target(raw, entry, plaintext, cands, arm):
    """arm: 'correct' | 'wrong'。oracle = 256B 前缀；命中后整分区 SHA-256 确认。"""
    read = U.data if arm == "correct" else U.data_legacy_wrong
    ct = read(raw, entry)
    if len(ct) < PREFIX:
        return [], 0
    ct_pre = ct[:PREFIX]
    pt_pre = plaintext[:PREFIX]
    ivs = iv_list_for(raw, entry)
    hits = []
    tested = 0
    for key, label in cands:
        for klen in (16, 24, 32):
            if len(key) < klen:
                continue
            k = key[:klen]
            for mode in MODES:
                for ivname, iv in ivs:
                    if mode == "ECB":
                        if ivname != "rec":
                            continue      # ECB 与 IV 无关，只跑一次
                        d = decrypt(ct_pre, k, mode, None)
                    else:
                        d = decrypt(ct_pre, k, mode, iv)
                    tested += 1
                    if d is None or d != pt_pre:
                        continue
                    full = decrypt(ct, k, mode, None if mode == "ECB" else iv)
                    sha_ok = (full is not None and
                              hashlib.sha256(full).hexdigest() == entry["sha_hex"])
                    hits.append(dict(arm=arm, mode=mode, iv=ivname, klen=klen,
                                     key=k.hex(), label=label,
                                     prefix_ok=True, sha_confirm=sha_ok))
    return hits, tested


# ===========================================================================
# 阳性对照：仿 UPD 容器（目标 256 KiB、明文全零、真密钥藏表头）
# ===========================================================================
TRUE_KEY = bytes.fromhex("00112233445566778899aabbccddeeff")
TRUE_IV = bytes(range(16))
TGT_SIZE = 0x40000          # 与 ipu_data 一致


def build_synthetic(mode, plaintext, key=TRUE_KEY, iv=TRUE_IV):
    """构造一个模仿 S5 UPD 的容器：表在 0x2EC、条目 92B、doff 相对 0x200。"""
    pt_part = bytes(0x1000)
    if mode == "CBC":
        ct = AES.new(key, AES.MODE_CBC, iv).encrypt(plaintext)
    elif mode == "ECB":
        ct = AES.new(key, AES.MODE_ECB).encrypt(plaintext)
    else:
        ct = AES.new(key, AES.MODE_CTR, nonce=iv[:8],
                     initial_value=int.from_bytes(iv[8:], "big")).encrypt(plaintext)

    pt_doff, tg_doff = 0x400, 0x4400
    size = U.DATA_BASE + tg_doff + TGT_SIZE + 0x1000
    raw = bytearray(size)
    raw[0:4] = b"UNPF"
    raw[0x0C:0x1C] = b"DC-S5\x00" + b"\x00" * 5
    raw[0x80:0x90] = iv                                  # 表头 IV
    raw[0x100:0x100 + len(key)] = key                    # ★ 真密钥藏在表头
    for i in range(24):                                  # 诱饵候选
        raw[0x1A0 + i * 12:0x1A0 + i * 12 + 12] = hashlib.sha256(b"decoy%d" % i).digest()[:12]

    struct.pack_into("<III", raw, U.DIR_HDR_OFF, 0x1400, 0x1000 + TGT_SIZE, 2)

    def put(i, name, doff, dsz, ty, sha, iv_):
        off = U.TABLE_BASE + i * U.STRIDE
        raw[off:off + 12] = name.encode().ljust(12, b"\0")
        struct.pack_into("<IIII", raw, off + U.F_DOFF, doff, dsz, 0x80000000, ty)
        raw[off + U.F_SHA:off + U.F_SHA + 32] = sha
        raw[off + U.F_IV:off + U.F_IV + 16] = iv_

    put(0, "knownpt", pt_doff, 0x1000, U.TYPE_PLAINTEXT,
        hashlib.sha256(pt_part).digest(), bytes(16))
    put(1, "ipu_data", tg_doff, TGT_SIZE, U.TYPE_ENCRYPTED,
        hashlib.sha256(plaintext).digest(), iv)

    raw[U.DATA_BASE + pt_doff:U.DATA_BASE + pt_doff + 0x1000] = pt_part
    raw[U.DATA_BASE + tg_doff:U.DATA_BASE + tg_doff + TGT_SIZE] = ct
    return bytes(raw), U.by_name(bytes(raw), "ipu_data")


def positive_control():
    print("=" * 100)
    print("阳性对照（内联）：同一段搜索代码，能否在【已知密钥】的合成样本上捞出真密钥？")
    print("=" * 100)
    results = []
    in_set = False
    for mode, pname, plain in (("CBC", "all-0x00", bytes(TGT_SIZE)),
                               ("CTR", "all-0x00", bytes(TGT_SIZE)),
                               ("CBC", "random",
                                hashlib.sha256(b"seed").digest() * (TGT_SIZE // 32))):
        raw, entry = build_synthetic(mode, plain)
        cands, _ = harvest_keys(raw)
        in_set = in_set or any(k[:16] == TRUE_KEY for k, _ in cands)
        for arm in ("correct", "wrong"):
            hits, tested = search_target(raw, entry, plain, cands, arm)
            true_hits = [h for h in hits if h["key"] == TRUE_KEY.hex()]
            results.append(dict(mode=mode, plaintext=pname, arm=arm,
                                n_hits=len(hits), true_found=bool(true_hits),
                                tested=tested))
            print("  模式=%-4s 明文=%-8s 臂=%-8s 命中=%3d 其中真密钥=%d  %s"
                  % (mode, pname, arm, len(hits), len(true_hits),
                     "OK" if true_hits else "漏检"))
    print("  [自检] 真密钥是否在候选集合中 = %s" % in_set)
    ok = in_set and any(r["true_found"] for r in results if r["arm"] == "correct")
    print("  => 阳性对照%s；错误偏移臂真密钥命中 = %d"
          % ("成功：正确偏移有检验力" if ok else "未达预期",
             sum(1 for r in results if r["arm"] == "wrong" and r["true_found"])))
    print()
    return results, ok


# ===========================================================================
# 真实容器灵敏度对照：把已知密钥「种」进真实 V29 的表头，再跑同一段搜索
# ===========================================================================
def sensitivity_on_real(path):
    """在【真实固件容器】上做灵敏度对照：
       把 ipu_data 的密文换成 AES-CBC(TRUE_KEY, 记录IV) 加密的全零，
       并把 TRUE_KEY 种进表头 —— 然后跑同一段搜索代码，看能否捞回真密钥。
    这比合成样本更强：用的是真实条目表、真实候选来源（含 0x220 签名区）。"""
    print("=" * 100)
    print("真实容器灵敏度对照：把已知密钥种进真实 %s 的表头，搜索能否捞回？"
          % os.path.basename(path))
    print("=" * 100)
    if not os.path.exists(path):
        print("  [跳过] 文件不存在\n")
        return None
    raw = bytearray(U.load(path))
    e = U.by_name(bytes(raw), "ipu_data")
    size, iv = e["size"], e["iv"]
    raw[e["abs_off"]:e["abs_off"] + size] = \
        AES.new(TRUE_KEY, AES.MODE_CBC, iv).encrypt(bytes(size))
    raw[0x100:0x110] = TRUE_KEY                       # 种进表头（仅内存，不落盘）
    mod = bytes(raw)
    cands, stats = harvest_keys(mod)
    out = {}
    for arm in ("correct", "wrong"):
        hits, tested = search_target(mod, e, bytes(size), cands, arm)
        true_hits = [h for h in hits if h["key"] == TRUE_KEY.hex()]
        out[arm] = dict(n_hits=len(hits), true_found=bool(true_hits), tested=tested)
        print("  臂=%-8s 试解 %8d 次  命中 %d  其中真密钥 %d  %s"
              % (arm, tested, len(hits), len(true_hits),
                 "OK" if true_hits else "漏检"))
    ok = out["correct"]["true_found"]
    print("  => 真实容器上%s（若通过，则本次 0 命中不是搜索代码/候选来源的问题）\n"
          % ("灵敏度对照通过" if ok else "灵敏度对照未通过"))
    return dict(ok=ok, arms=out, candidates=len(cands), stats=stats)


# ===========================================================================
# 已知明文侦察
# ===========================================================================
def find_known_plaintext(raw):
    """返回 [(entry, template_name, plaintext_bytes), ...] —— 仅 type=3 且命中模板者。"""
    found = []
    for e in U.entries(raw):
        if e["type"] != U.TYPE_ENCRYPTED or e["size"] == 0:
            continue
        for name, fn in PLAINTEXT_TEMPLATES:
            if hashlib.sha256(fn(e["size"])).hexdigest() == e["sha_hex"]:
                found.append((e, name, fn(e["size"])))
                break
    return found


# ===========================================================================
# 主流程
# ===========================================================================
def run_one(path):
    print("=" * 100)
    print("固件：%s" % path)
    print("=" * 100)
    if not os.path.exists(path):
        print("  [跳过] 文件不存在\n")
        return None
    raw = U.load(path)
    tag = os.path.basename(path).replace("S5___", "").replace(".bin", "")
    rec = dict(file=path, tag=tag, size=len(raw))

    det = U.self_test_detail(raw)
    print("  [闸门] type=2 sha256(data)==记录SHA 命中 %d/%d  verdict=%s"
          % (det["hits"], det["total"], det["verdict"]))
    rec["gate"] = dict(hits=det["hits"], total=det["total"], verdict=det["verdict"])
    if det["verdict"] != "PASS":
        print("  => 闸门未过，跳过该固件的搜索\n")
        return rec

    known = find_known_plaintext(raw)
    print("  [已知明文] type=3 分区 41 个中命中模板者 = %d" % len(known))
    for e, nm, _ in known:
        print("      idx=%2d %-12s size=0x%x  模板=%s" % (e["idx"], e["name"], e["size"], nm))
    rec["known_plaintext"] = [dict(idx=e["idx"], name=e["name"], size=e["size"],
                                   template=nm, iv=e["iv_hex"]) for e, nm, _ in known]
    if not known:
        print("  => 无已知明文，无法做密钥搜索\n")
        return rec

    cands, cstats = harvest_keys(raw)
    print("  [候选] 共 %d 个  明细=%s" % (len(cands), cstats))
    rec["candidates"] = dict(total=len(cands), stats=cstats)

    arms = {}
    for e, nm, plain in known:
        for arm in ("correct", "wrong"):
            hits, tested = search_target(raw, e, plain, cands, arm)
            arms.setdefault(arm, []).extend([dict(target=e["name"], **h) for h in hits])
            print("  [搜索] %-12s 臂=%-8s 试解 %8d 次  命中 %d"
                  % (e["name"], arm, tested, len(hits)))
    rec["search"] = {arm: arms.get(arm, []) for arm in ("correct", "wrong")}
    rec["unique_keys_correct"] = sorted({h["key"] for h in arms.get("correct", [])})
    print("  => 正确偏移臂唯一命中密钥数 = %d" % len(rec["unique_keys_correct"]))
    print()
    return rec


def main(argv):
    paths = argv[1:] or FW_CANDIDATES
    os.makedirs(OUT, exist_ok=True)
    report = dict(prefix_bytes=PREFIX, modes=MODES, pad_target=PAD_TARGET, firmwares=[])

    pc_results, pc_ok = positive_control()
    report["positive_control"] = dict(ok=pc_ok, results=pc_results)

    real_ctrl = sensitivity_on_real(paths[0])
    report["real_container_sensitivity"] = real_ctrl
    if real_ctrl is None:
        real_ctrl = dict(ok=False)

    total_correct = 0
    for p in paths:
        r = run_one(p)
        if r is None:
            continue
        report["firmwares"].append(r)
        total_correct += len(r.get("unique_keys_correct", []) or [])

    print("=" * 100)
    print("总结")
    print("=" * 100)
    print("  阳性对照（合成样本，搜索逻辑有检验力） = %s" % pc_ok)
    print("  真实容器灵敏度对照（种入密钥能否捞回） = %s" % real_ctrl["ok"])
    print("  真实固件【正确偏移】臂命中密钥总数 = %d" % total_correct)
    if pc_ok and real_ctrl["ok"] and total_correct == 0:
        print("  => 结论：修正偏移后、在【已知有检验力】的搜索下，真实固件仍 0 命中 ——")
        print("     这是一次真阴性：文件内派生候选密钥（表头窗口/摘要派生/签名区/PTool 表）")
        print("     中没有任何一个是这些加密分区的 AES 密钥。")
    print("=" * 100)

    with open(os.path.join(OUT, "exp5_real_key_search.json"), "w") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print("[写出] %s" % os.path.join(OUT, "exp5_real_key_search.json"))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
