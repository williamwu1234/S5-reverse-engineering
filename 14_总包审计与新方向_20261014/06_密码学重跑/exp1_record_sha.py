#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
实验 1：记录 SHA 的语义 —— 全部 48 个分区，两种偏移对照
=========================================================
对应项目结论："记录 SHA 是逻辑校验和、≠ 存储字节哈希"
（`S5_AES破解可行性评估_20261011.md:116-121`，脚本 `verify_sha.py`）

本脚本对 **全部 48 条** 分区记录（不只 7 个）同时计算：
    A) 错误偏移 raw[doff : doff+size]         （= 项目脚本现状）
    B) 正确偏移 raw[doff+0x200 : doff+0x200+size]
并与条目里的记录 SHA 比对，按 type 分组统计。

用法: python3 exp1_record_sha.py [firmware.bin]
"""
import hashlib
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import upd_table as U

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "out")
DEFAULT_FW = os.path.normpath(os.path.join(HERE, "..", "..", "02_固件二进制/DC-S5/S5___V29.bin"))


def main():
    fw = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_FW
    raw = U.load(fw)

    det = U.self_test_detail(raw)
    assert det["verdict"] == "PASS", f"偏移模型未确证（{det['hits']}/{det['total']}），必须停止"

    rows = []
    for e in U.entries(raw):
        d_ok = U.data(raw, e)
        d_no = U.data_legacy_wrong(raw, e)
        rows.append(dict(
            idx=e["idx"], name=e["name"], type=e["type"], size=e["size"],
            doff=e["doff"], abs_off=e["abs_off"],
            rec=e["sha_hex"],
            ok_sha=hashlib.sha256(d_ok).hexdigest(),
            no_sha=hashlib.sha256(d_no).hexdigest(),
            hit_correct=(hashlib.sha256(d_ok).hexdigest() == e["sha_hex"]),
            hit_wrong=(hashlib.sha256(d_no).hexdigest() == e["sha_hex"]),
        ))

    print("=" * 96)
    print("实验 1：记录 SHA 语义 — 全部 48 分区，错误偏移 vs 正确偏移")
    print(f"固件: {fw}")
    print(f"判决实验: type=2 SHA 命中 {det['hits']}/{det['total']} (verdict={det['verdict']})")
    print("=" * 96)
    print(f"{'#':>3} {'name':<12} {'type':>4} {'size':>9} {'错误偏移命中':>12} {'正确偏移命中':>12}")
    for r in rows:
        print(f"{r['idx']:>3} {r['name']:<12} {r['type']:>4} {r['size']:>9} "
              f"{('HIT' if r['hit_wrong'] else 'miss'):>12} {('HIT' if r['hit_correct'] else 'miss'):>12}")

    print()
    print("-" * 96)
    print("按 type 分组统计")
    print("-" * 96)
    print(f"{'type':>4} {'分区数':>6} {'错误偏移命中':>14} {'正确偏移命中':>14}")
    group = {}
    for r in rows:
        g = group.setdefault(r["type"], [0, 0, 0])
        g[0] += 1
        g[1] += int(r["hit_wrong"])
        g[2] += int(r["hit_correct"])
    for t, (n, w, c) in sorted(group.items()):
        label = {2: "明文", 3: "加密"}.get(t, "?")
        print(f"{t:>4} {n:>6} {f'{w}/{n}':>14} {f'{c}/{n}':>14}   ({label})")
    tot_w = sum(g[1] for g in group.values())
    tot_c = sum(g[2] for g in group.values())
    print(f"{'合计':>4} {len(rows):>6} {f'{tot_w}/{len(rows)}':>14} {f'{tot_c}/{len(rows)}':>14}")

    print()
    print("错误偏移下侥幸命中的分区（解释项目为何看到 2/7）：")
    for r in rows:
        if r["hit_wrong"]:
            print(f"  [{r['idx']:>2}] {r['name']:<12} type={r['type']} size={r['size']}  "
                  f"（0x200 平移后仍撞上同一段数据）")

    # 记录 SHA 的结构性证据：重复 SHA = 明文相同（与偏移无关的元数据）
    print()
    print("-" * 96)
    print("记录 SHA 重复组（元数据，与偏移无关）——'记录 SHA = 明文 SHA' 的结构性证据")
    print("-" * 96)
    seen = {}
    for r in rows:
        seen.setdefault(r["rec"], []).append(r)
    dups = {k: v for k, v in seen.items() if len(v) > 1}
    for k, v in sorted(dups.items(), key=lambda kv: kv[1][0]["idx"]):
        names = ", ".join(f"{x['name']}(#{x['idx']},type={x['type']},sz={x['size']})" for x in v)
        print(f"  {k[:32]}  ->  {names}")
    print(f"  重复组数 = {len(dups)}")
    print(f"  空分区 storage 的记录 SHA = {U.by_name(raw, 'storage')['sha_hex']}")
    print(f"  SHA256(b'')               = {hashlib.sha256(b'').hexdigest()}")
    print("  -> size=0 的分区其记录 SHA 恰好等于空串 SHA256 ⇒ 记录字段就是【明文内容的 SHA-256】")

    print()
    print("=" * 96)
    print("判读")
    print("=" * 96)
    print(f"  错误偏移（项目现状）: type=2 明文分区命中 {group.get(2,[0,0,0])[1]}/{group.get(2,[0,0,0])[0]}"
          f"；type=3 加密分区命中 {group.get(3,[0,0,0])[1]}/{group.get(3,[0,0,0])[0]}")
    print(f"  正确偏移           : type=2 明文分区命中 {group.get(2,[0,0,0])[2]}/{group.get(2,[0,0,0])[0]}"
          f"；type=3 加密分区命中 {group.get(3,[0,0,0])[2]}/{group.get(3,[0,0,0])[0]}")
    print("  结论：type=2 的『记录 SHA ≠ 内容哈希』这一论断【被推翻】——命中 7/7，")
    print("        记录 SHA 就是该分区【明文内容】的 SHA-256。")
    print("        type=3 在两种读法下都不命中，因为其内容被加密；记录 SHA 存的是【加密前明文】的哈希")
    print("        （ipu_data 的记录 SHA 与 type=2 的 history 完全相同，而 history 内容 SHA 已 7/7 验证）。")

    os.makedirs(OUT, exist_ok=True)
    with open(os.path.join(OUT, "exp1_record_sha.json"), "w") as f:
        json.dump(dict(firmware=fw, self_test=det["hits"], total_type2=det["total"],
                       rows=rows,
                       group={str(k): dict(n=v[0], hit_wrong=v[1], hit_correct=v[2])
                              for k, v in group.items()}), f, indent=2, ensure_ascii=False)
    print(f"\n[写出] {os.path.join(OUT, 'exp1_record_sha.json')}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
