#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验 3：跨版本密文一致性（V29 vs V24，附 V11/V20/V23）
======================================================
对应项目结论："41 个 IV 逐版本全变、同偏移密文相等率 ≈ 0.4% ⇒ 排除 ECB / 版本稳定 keystream"
（`S5_AES破解可行性评估_20261011.md:103-114`，脚本 `xver2.py` / `xver_fixed.py`）

本脚本用 upd_table 单一真源重算：同一分区在【错误偏移】与【正确偏移】下的
  * IV 是否跨版本变化（元数据，与偏移无关）
  * 记录 SHA 是否跨版本相同（= 明文是否相同；该字段的语义已被 7/7 判决实验确证）
  * 同"分区内相对偏移"处密文的逐字节相等率
并对所有版本先跑 type=2 判决实验，确认偏移模型跨版本成立。

用法: python3 exp3_cross_version.py
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upd_table as U

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(HERE, "out")

FW = {
    "V11": "02_固件二进制/DC-S5_版本历史/S5___V11.bin",
    "V20": "02_固件二进制/DC-S5_版本历史/S5___V20.bin",
    "V23": "02_固件二进制/DC-S5_版本历史/S5___V23.bin",
    "V24": "02_固件二进制/DC-S5_版本历史/S5___V24.bin",
    "V29": "02_固件二进制/DC-S5/S5___V29.bin",
}
PAIR = ("V29", "V24")   # 任务书要求的对照
SPOTLIGHT = ["program", "zimage", "rootfs1", "rootfs2", "postboot3", "loader2", "dtb",
             "eep_ow_a", "eep_ow_b", "eep_act_a", "eep_act_b", "history", "ipu_data"]


def eq_rate(a, b):
    n = min(len(a), len(b))
    if n == 0:
        return 0.0
    x = int.from_bytes(a[:n], "big") ^ int.from_bytes(b[:n], "big")
    return x.to_bytes(n, "big").count(0) / n


def main():
    data = {}
    print("=" * 100)
    print("实验 3：跨版本密文一致性")
    print("=" * 100)
    print("\n[0] 各版本先跑偏移模型判决实验（type=2 分区 sha256(data)==记录sha）")
    for v, rel in FW.items():
        p = os.path.join(ROOT, rel)
        if not os.path.exists(p):
            print(f"  {v}: 缺失 {p}")
            continue
        raw = U.load(p)
        det = U.self_test_detail(raw)
        data[v] = dict(raw=raw, ents=U.entries(raw), by={e["name"]: e for e in U.entries(raw)},
                       selftest=det)
        print(f"  {v}: {det['hits']}/{det['total']}  verdict={det['verdict']}  "
              f"条目数={U.entry_count(raw)}  文件={len(raw)}")
    bad = [v for v, d in data.items() if d["selftest"]["verdict"] != "PASS"]
    assert not bad, f"偏移模型在版本 {bad} 上未确证，停止"
    print("  ⇒ 偏移模型在全部版本上成立（单源 upd_table 跨版本自洽）")

    va, vb = PAIR
    A, B = data[va], data[vb]
    common = [e["name"] for e in A["ents"] if e["name"] in B["by"]]
    print(f"\n[1] {va} vs {vb}：共同分区名 {len(common)} 个")

    rows = []
    for nm in common:
        ea, eb = A["by"][nm], B["by"][nm]
        rowa = dict(name=nm, type=ea["type"], size_a=ea["size"], size_b=eb["size"],
                    iv_same=(ea["iv"] == eb["iv"]), sha_same=(ea["sha_hex"] == eb["sha_hex"]))
        # 只比较两版本都存在、且长度相同的公共前缀
        n = min(ea["size"], eb["size"])
        if n == 0:
            rowa.update(n=0, eq_correct=1.0, eq_wrong=1.0)
        else:
            ca = U.data(A["raw"], ea)[:n]
            cb = U.data(B["raw"], eb)[:n]
            wa = U.data_legacy_wrong(A["raw"], ea)[:n]
            wb = U.data_legacy_wrong(B["raw"], eb)[:n]
            rowa.update(n=n, eq_correct=eq_rate(ca, cb), eq_wrong=eq_rate(wa, wb))
        rows.append(rowa)

    print(f"\n{'分区':<13} {'type':>4} {'对比字节':>9} {'IV跨版本同':>9} {'记录SHA同(明文同)':>16} "
          f"{'密文相等率(错偏移)':>17} {'密文相等率(正确偏移)':>19}")
    for r in rows:
        print(f"{r['name']:<13} {r['type']:>4} {r['n']:>9} {str(r['iv_same']):>9} {str(r['sha_same']):>16} "
              f"{r['eq_wrong']*100:>16.4f}% {r['eq_correct']*100:>18.4f}%")

    n_iv_same = sum(1 for r in rows if r["iv_same"])
    n_sha_same = sum(1 for r in rows if r["sha_same"])
    print(f"\n  IV 跨版本相同: {n_iv_same}/{len(rows)}   记录SHA(明文)跨版本相同: {n_sha_same}/{len(rows)}")

    # 关键判定：明文同 + IV 同 → 密文同 ⇒ 密钥同；密文不同 ⇒ 密钥不同
    key_same = key_diff = 0
    verdicts = []
    for r in rows:
        if not (r["sha_same"] and r["iv_same"]):
            continue
        same_ct = (r["eq_correct"] == 1.0)
        key_same += int(same_ct)
        key_diff += int(not same_ct)
        verdicts.append((r["name"], same_ct))
    print(f"  明文&IV 均跨版本相同（可直接判定密钥）: {len(verdicts)} 个"
          f" → 密钥相同 {key_same} / 密钥不同 {key_diff}")
    for nm, s in verdicts:
        print(f"     {nm}: 密文{'相同 ⇒ 密钥跨版本相同' if s else '不同 ⇒ 密钥跨版本不同'}")

    # 报告口径：加密大分区的"同偏移密文相等率"（复现原表并给出修正值）
    print(f"\n[2] 重点加密分区：同『分区内相对偏移』处密文的逐字节相等率（{va} vs {vb}）")
    print(f"{'分区':<13} {'minsz':>9} {'错误偏移(原表口径)':>18} {'正确偏移':>12} {'≈随机基线1/256':>14}")
    spot = []
    for nm in SPOTLIGHT:
        r = next((x for x in rows if x["name"] == nm), None)
        if not r or r["n"] == 0:
            continue
        spot.append(r)
        print(f"{nm:<13} {r['n']:>9} {r['eq_wrong']*100:>17.4f}% {r['eq_correct']*100:>11.4f}% "
              f"{100/256:>13.4f}%")

    enc = [r for r in rows if r["type"] == 3 and r["n"] >= 4096]
    if enc:
        avg_w = sum(r["eq_wrong"] for r in enc) / len(enc)
        avg_c = sum(r["eq_correct"] for r in enc) / len(enc)
        print(f"\n  type=3 且对比长度≥4KB 的分区共 {len(enc)} 个：")
        print(f"    平均相等率  错误偏移 = {avg_w*100:.4f}%   正确偏移 = {avg_c*100:.4f}%   "
              f"随机基线 = {100/256:.4f}%")

    print("""
  判读（本项）：
    * IV 逐版本全变、同偏移密文相等率 ≈0.4%（= 1/256 随机基线）——这两条【推翻 ECB / 版本稳定
      keystream】的论断【维持】。IV 是元数据，不受 0x200 修正影响；密文相等率修正后数值变化很小
      （两个版本同时平移 512B ⇒ 对比仍然对齐），量级不变。
    * 但原表把"相等率≈0.4%"当作"密文与随机不可区分"的证据时，前提是【明文相同】。原脚本用固定的
      脚本硬编码偏移、且只比前 8KB，属于"位置对得上但语义未证"；现在这一前提由记录 SHA 字段
      承担，而该字段语义已由 7/7 判决实验确证（记录 SHA = 明文 SHA）。
    * 附带修正：项目报告称"41 个 IV 逐版本全变"。以 V29/V24 实测（本表）与 5 版 IV 稳定性统计为准。
""")

    rep = dict(pair=list(PAIR), selftest={v: d["selftest"]["hits"] for v, d in data.items()},
               rows=[{k: (round(v, 8) if isinstance(v, float) else v) for k, v in r.items()} for r in rows],
               n_iv_same=n_iv_same, n_sha_same=n_sha_same, common=len(rows),
               key_same=key_same, key_diff=key_diff)
    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp3_cross_version.json"), "w") as f:
        json.dump(rep, f, indent=2, ensure_ascii=False)
    print(f"[写出] {os.path.join(OUT, 'exp3_cross_version.json')}")

    # 5 版 IV 稳定性（附）
    print("\n[3] 附：5 个版本 IV 稳定性（按分区名对齐）")
    allnames = sorted({e["name"] for v in data for e in data[v]["ents"]})
    cnt_var = cnt_stable = cnt_partial = 0
    lines = []
    for nm in allnames:
        ivs = {}
        for v in FW:
            e = data.get(v, {}).get("by", {}).get(nm)
            if e:
                ivs[v] = e["iv_hex"]
        if len(ivs) < 2:
            continue
        u = len(set(ivs.values()))
        tag = "全变" if u == len(ivs) else ("全同" if u == 1 else f"部分({u}/{len(ivs)})")
        if u == len(ivs):
            cnt_var += 1
        elif u == 1:
            cnt_stable += 1
        else:
            cnt_partial += 1
        lines.append(f"  {nm:<13} 版本数={len(ivs)} 唯一IV={u} {tag}")
    print("\n".join(lines))
    print(f"\n  统计：IV 逐版本全变 {cnt_var} 个 / 全同 {cnt_stable} 个 / 部分变化 {cnt_partial} 个")
    return 0


if __name__ == "__main__":
    sys.exit(main())
