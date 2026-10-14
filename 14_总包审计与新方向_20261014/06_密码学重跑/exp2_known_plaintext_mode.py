#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验 2：已知明文 / keystream / 加密模式判决（CBC vs 流式）
==========================================================
对应项目结论：
  * "唯一例外 ipu_data 的明文可经 history 得知（≈全零、仅 508 字节非零）→ 已提取 256KB 真实 keystream"
    （`S5_AES破解可行性评估_20261011.md:12,77`、`ks_extract.py`）
  * "若为 CBC 且明文全零 ⇒ 所有 16 字节密文块必须相同"（本次任务书给出的判决准则）

本脚本同时给出「错误偏移（项目现状）」与「正确偏移」两臂结果。

用法: python3 exp2_known_plaintext_mode.py [firmware.bin]
"""
import hashlib
import json
import math
import os
import sys
from collections import Counter

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upd_table as U

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEFAULT_FW = os.path.normpath(os.path.join(HERE, "..", "..", "02_固件二进制/DC-S5/S5___V29.bin"))


def entropy(b):
    if not b:
        return 0.0
    c = Counter(b)
    L = len(b)
    return -sum((n / L) * math.log(n / L, 2) for n in c.values() if n)


def zero_ratio(b):
    return (sum(1 for x in b if x == 0) / len(b)) if b else 0.0


def self_period(x, p, cap=1 << 20):
    n = min(cap, len(x))
    if n <= p:
        return None
    return sum(1 for i in range(p, n) if x[i] == x[i - p]) / (n - p)


def blocks_of(x, bs=16):
    return [x[i:i + bs] for i in range(0, len(x) - len(x) % bs, bs)]


def eq_rate(a, b):
    """快速逐字节相等率（用大整数 XOR，C 速度）。"""
    n = min(len(a), len(b))
    x = int.from_bytes(a[:n], "big") ^ int.from_bytes(b[:n], "big")
    z = x.to_bytes(n, "big").count(0)
    return z / n


def main():
    fw = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FW
    raw = U.load(fw)
    det = U.self_test_detail(raw)
    assert det["verdict"] == "PASS", f"偏移模型未确证（{det['hits']}/{det['total']}），必须停止"
    ents = U.entries(raw)
    by = {e["name"]: e for e in ents}
    rep = {}

    print("=" * 100)
    print("实验 2：已知明文 / keystream / 模式判决")
    print(f"固件: {fw}")
    print(f"判决实验: type=2 SHA 命中 {det['hits']}/{det['total']} (PASS)")
    print("=" * 100)

    # ---------------------------------------------------------------- A
    print("\n" + "=" * 100)
    print("A) 可猜明文扫描：41 个 type=3 分区的记录 SHA 是否 == 某个可猜内容(同长度)的 SHA256")
    print("=" * 100)

    def candidates(n):
        c = {
            "全零 0x00": bytes(n),
            "全FF 0xFF": b"\xff" * n,
            "全 0x55": b"\x55" * n,
            "全 0xAA": b"\xaa" * n,
            "递增 0..255 循环": (bytes(range(256)) * (n // 256 + 1))[:n],
            "512B 零块重复": bytes((512 if n >= 512 else n)),
        }
        return c

    print(f"{'#':>3} {'name':<12} {'type':>4} {'size':>9}  {'命中候选':<20}")
    hits = []
    for e in ents:
        if e["type"] != U.TYPE_ENCRYPTED or e["size"] == 0:
            continue
        cand = candidates(e["size"])
        # 与 type=2 分区的真实内容交叉比对（内容已 7/7 验证）
        for pe in ents:
            if pe["type"] == U.TYPE_PLAINTEXT and pe["size"] == e["size"]:
                cand[f"== {pe['name']} 的内容"] = U.data(raw, pe)
        found = [k for k, v in cand.items() if hashlib.sha256(v).hexdigest() == e["sha_hex"]]
        if found:
            hits.append((e, found))
            print(f"{e['idx']:>3} {e['name']:<12} {e['type']:>4} {e['size']:>9}  {'/'.join(found):<20}")
    if not hits:
        print("  (无命中)")
    print(f"\n  → 已知明文的 type=3 分区数 = {len(hits)} / 41")

    # ipu_data 专项
    ip = by["ipu_data"]
    hist = by["history"]
    pt_true = bytes(ip["size"])           # 正确偏移下 history 内容 = 全零（见下）
    assert hashlib.sha256(pt_true).hexdigest() == ip["sha_hex"], "ipu_data 明文不是全零？"
    assert hashlib.sha256(U.data(raw, hist)).hexdigest() == hist["sha_hex"]
    print(f"\n  ipu_data 的明文 = history 的内容 = {ip['size']} 字节全零（双重验证：")
    print(f"    history 内容 SHA 命中其记录 SHA（type=2 判决实验内），且 ipu_data 记录 SHA == history 记录 SHA）")

    # ---------------------------------------------------------------- B
    print("\n" + "=" * 100)
    print("B) ipu_data 的已知明文与 keystream：错误偏移 vs 正确偏移")
    print("=" * 100)
    ct_ok = U.data(raw, ip)
    ct_no = U.data_legacy_wrong(raw, ip)
    pt_ok = U.data(raw, hist)                 # 正确偏移：全零
    pt_no = U.data_legacy_wrong(raw, hist)    # 错误偏移：项目当年读到的"明文"

    rows = []
    for label, ct, pt in (("错误偏移（项目现状）", ct_no, pt_no),
                          ("正确偏移（本次修正）", ct_ok, pt_ok)):
        ks = bytes(x ^ y for x, y in zip(ct, pt))
        nz = sum(1 for b in pt if b)
        rows.append((label, ct, pt, ks))
        print(f"\n  [{label}]")
        print(f"    明文 pt  : {len(pt)} 字节，非零 {nz} 字节（{nz/len(pt)*100:.4f}%），"
              f"熵={entropy(pt):.4f}，全零={nz==0}")
        print(f"    密文 ct  : 熵={entropy(ct):.4f}，零字节比例={zero_ratio(ct):.4f}")
        print(f"    ks=ct^pt : 熵={entropy(ks):.4f}，零字节比例={zero_ratio(ks):.4f}，"
              f"16B 自周期率={self_period(ks,16):.4f}")
        print(f"    ct 与 ks 是否逐字节相同: {ct == ks}"
              f"  ← {'明文全零 ⇒ 密文本身就是 keystream' if ct == ks else '明文非零 ⇒ ks 是修正后的流'}")

    ks_no = rows[0][3]
    ks_ok = rows[1][3]
    sh = min(len(ks_no), len(ks_ok))
    same_shift = eq_rate(ks_no[:sh], ks_ok[:sh])
    # ks_wrong[i] = ct_wrong[i]^pt_wrong[i] = raw[a+i]^raw[b+i]
    # ks_ok[i]   = ct_ok[i]   ^pt_ok[i]      = raw[a+0x200+i]^raw[b+0x200+i]
    # ⇒ ks_wrong[i] == ks_ok[i-0x200]
    rel = eq_rate(ks_no[0x200:], ks_ok[:sh - 0x200])
    print(f"\n  两臂 keystream 关系：同位置逐字节相等率 = {same_shift*100:.4f}%（≈随机，位置整体错开）")
    print(f"  ks_wrong[i] == ks_correct[i-0x200]（= 真 keystream 整体右移 512B）成立率 = {rel*100:.4f}%")
    print("  → 项目手上的『256KB keystream』是**真 keystream 平移 512 字节后的版本**：")
    print(f"     其中 {100*(1-0x200/len(ks_no)):.2f}% 的字节逐个都是【正确的 keystream 值】，只是位置错了 512B；")
    print("     但它把『明文里那 508 个非零字节』当成了真实明文——那 508 字节是错位读出来的（正确偏移下为 0）。")
    rep["B_keystream"] = dict(
        pt_nonzero_wrong=sum(1 for b in pt_no if b), pt_nonzero_correct=sum(1 for b in pt_ok if b),
        ent_ks_wrong=entropy(ks_no), ent_ks_correct=entropy(ks_ok),
        eq_rate_wrong_vs_correct=same_shift,
        shift_relation_rate=rel,
        ct_equals_ks_correct=(ct_ok == ks_ok), ct_equals_ks_wrong=(ct_no == ks_no))

    # ---------------------------------------------------------------- C
    print("\n" + "=" * 100)
    print("C) 模式判决：CBC 还是流式？—— 先纠正判决准则")
    print("=" * 100)
    print("""
  任务书给出的准则：「若为 CBC 且明文全零 ⇒ 所有 16 字节密文块必须相同」——**这条是错的**。
  正确的分组密码语义：
    * ECB + 常量明文 : C_i = E_K(P)            ⇒ 所有块【相同】  ✔ 这是"块全同"的正确含义
    * CBC + 全零明文 : C_0 = E_K(IV), C_i = E_K(C_{i-1})  ⇒ 迭代加密链，块【基本全不同】
    * CTR/流式       : C_i = P_i ^ KS_i        ⇒ 块【全不同】
  所以"块是否全同"只能【排除 ECB】，**不能区分 CBC 与 CTR**。
  （exp4 会用自造的已知 CBC+全零明文样本实测证明这条准则错误。）
""")
    blk_ok = blocks_of(ct_ok)
    blk_no = blocks_of(ct_no)
    print(f"  ipu_data 密文块统计（明文 = 全零，已证）")
    print(f"    正确偏移: 块数={len(blk_ok)}  len(set(blocks))={len(set(blk_ok))}  "
          f"唯一率={len(set(blk_ok))/len(blk_ok)*100:.2f}%")
    print(f"    错误偏移: 块数={len(blk_no)}  len(set(blocks))={len(set(blk_no))}  "
          f"唯一率={len(set(blk_no))/len(blk_no)*100:.2f}%")
    print(f"    → 两种读法都【全块唯一】⇒ 排除『ECB + 常量明文』，但 CBC/CTR 仍不可分")

    print("\n  真正有判别力的实验：同明文 + 不同 IV 的密文对照")
    print("  （这对分区的『同明文』现在是【已证】的：记录 SHA 完全相同，而记录 SHA 字段已被 7/7 判决实验证明为明文 SHA）")
    pair_rows = []
    for na, nb in (("eep_ow_a", "eep_ow_b"), ("eep_act_a", "eep_act_b")):
        ea, eb = by[na], by[nb]
        for arm, fn in (("错误偏移", U.data_legacy_wrong), ("正确偏移", U.data)):
            a, b = fn(raw, ea), fn(raw, eb)
            er = eq_rate(a, b)
            x = bytes(p ^ q for p, q in zip(a, b))
            pair_rows.append(dict(pair=f"{na}/{nb}", arm=arm, same_sha=(ea["sha_hex"] == eb["sha_hex"]),
                                  same_iv=(ea["iv"] == eb["iv"]), size=len(a),
                                  eq_rate=er, ct_identical=(a == b), xor_entropy=entropy(x),
                                  xor_zero_ratio=zero_ratio(x)))
            print(f"    {na}/{nb:<12} [{arm}] 记录SHA相同={ea['sha_hex']==eb['sha_hex']} "
                  f"IV相同={ea['iv']==eb['iv']} 逐字节相等率={er*100:.4f}% "
                  f"密文完全相同={a==b} XOR熵={entropy(x):.4f} XOR零比例={zero_ratio(x):.4f}")
    print("    ECB            ⇒ 相等率应为 100%        （实测 ≈0.37%，排除）")
    print("    固定 XOR 流     ⇒ XOR 应恒为 0          （实测 XOR 熵 ≈8，排除）")
    print("    CBC/CTR + 随机IV ⇒ 逐字节相等率 ≈ 1/256 = 0.3906%，XOR 熵 ≈ 8  ✔ 与实测一致")

    bad = [(e["name"], e["size"]) for e in ents if e["type"] == 3 and e["size"] % 16]
    print(f"\n  结构约束：type=3 分区 size 非 16 倍数的 = {bad if bad else '无'}"
          f"（全部为 16 的倍数 —— 与分组密码一致，但不构成证明：CTR 也可选 16 倍长度）")

    print("""
  判读（本项）：
    * 「CBC ⇔ 全零明文 ⇒ 块全同」这条判决准则【错误】，据此得出的任何"是 CBC"结论都不成立；
      实测 len(set(blocks)) = 16384/16384（全唯一）只说明【不是 ECB+常量明文】。
    * 用真正有判别力的"同明文不同 IV"对照，可以排除 ECB 与固定 XOR 流；
      **CBC 与 CTR/流式 在本数据上不可区分**（两者在"全零明文"下都输出块全唯一的随机密文）。
      ⇒ 项目把它命名为"真实 keystream"是【术语错误】（只有 CTR 下 ct 才叫 keystream），
        但这不影响熵 7.999 的观测本身。
    * 明文修正：history/ipu_data 的明文是【纯全零】，不是"≈全零、仅 508 字节非零"。
      那 508 个非零字节是错误偏移读出来的（本次已逐字节复现：错误偏移下恰为 508 个）。
    * 已知明文的信息量：全零明文 ⇒ 已知明文不提供任何信息（ks = ct），
      这与项目"信息量低"的判断方向一致但更强：**信息量为 0**（就 keystream 而言）。
""")
    rep["C_mode"] = dict(blocks_correct=len(blk_ok), uniq_blocks_correct=len(set(blk_ok)),
                         blocks_wrong=len(blk_no), uniq_blocks_wrong=len(set(blk_no)),
                         pairs=pair_rows, size_mod16_all_zero=(not bad))
    rep["A_known_plaintext"] = dict(hits=[dict(name=e["name"], idx=e["idx"], size=e["size"], found=f)
                                          for e, f in hits], n_enc=41)

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp2_known_plaintext_mode.json"), "w") as f:
        json.dump(rep, f, indent=2, ensure_ascii=False)
    print(f"[写出] {os.path.join(OUT, 'exp2_known_plaintext_mode.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
