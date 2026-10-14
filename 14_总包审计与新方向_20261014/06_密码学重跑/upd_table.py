#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
upd_table.py —— S5 (DC-S5 / MC801) UPD 固件分区表的【单一真源】(single source of truth)
=====================================================================================

背景（2026-10-14 审计 S2 / R4，已独立复算确认）
------------------------------------------------
UPD 分区表条目里的 `doff` **不是文件绝对偏移**，而是**相对数据基址 0x200 的相对偏移**：

        绝对偏移 abs_off = doff + DATA_BASE(0x200)

项目在 2026-10-14 的勘误 E1 里自己承认了这一点，但**只修了 `parse_upd.py` 一个文件**；
其余 7~9 个脚本仍用 `raw[doff:]`，导致：

  * type=2（明文）分区「记录 SHA == 内容 SHA」只有 2/7 命中（正确模型 7/7）；
  * `keyhunt.py` / `keyhunt2.py` 的**密文与明文用了同一个错误偏移**，
    即使正确密钥出现，解密的也是错位的 512 字节 ⇒ 结果必为垃圾 ⇒
    「0 命中」是**假阴性**，对假设零检验力。

本模块的目的
------------
把「偏移模型」收敛成**唯一入口**，任何后续脚本都不允许再手写 `raw[off:]`：

    e = upd_table.entries(raw)[i]      # 元数据（含唯一的 abs_off 定义）
    d = upd_table.data(raw, e)         # ★ 唯一的取数入口（正确偏移）
    w = upd_table.data_legacy_wrong(raw, e)   # 仅供"错误偏移对照臂"使用，显式命名

被判定的模型（判决实验）
------------------------
    self_test(raw) == (type=2 分区数)   # V29 上期望 7/7

用法
----
    python3 upd_table.py [firmware.bin]        # 打印分区表 + 判决实验
    import upd_table as U
"""

from __future__ import annotations

import hashlib
import struct
import sys

# ---------------------------------------------------------------------------
# 单一真源：所有常量只在这里定义一次
# ---------------------------------------------------------------------------

DATA_BASE = 0x200   # ★ 数据基址：doff 是相对它的偏移，abs_off = DATA_BASE + doff
TABLE_BASE = 0x2EC  # 条目表起点
STRIDE = 92         # 每条条目 92 字节
COUNT_OFF = 0x2E8   # 条目数字段（u32 LE）——不要硬编码 48
DIR_HDR_OFF = 0x2E0  # 数据目录头 (data_start, data_total, entry_count) 三连 u32

COUNT_FALLBACK = 48          # 条目数不合理时的兜底值
COUNT_SANE_MAX = 512         # 合理性上界

# 条目内部字段偏移（相对 STRIDE 块起点）
F_NAME = 0x00   # 12B ASCII 名字，\0 结尾
F_DOFF = 0x0C   # u32 相对数据基址的偏移
F_SIZE = 0x10   # u32 数据长度
F_ADDR = 0x14   # u32 load address
F_TYPE = 0x18   # u32 类型：2=明文, 3=加密
F_SHA = 0x1C    # 32B SHA-256
F_IV = 0x3C     # 16B AES IV

TYPE_PLAINTEXT = 2
TYPE_ENCRYPTED = 3


# ---------------------------------------------------------------------------
# 解析
# ---------------------------------------------------------------------------

def entry_count(raw: bytes) -> int:
    """从 0x2E8 读条目数（不硬编码 48），带合理性兜底。"""
    if len(raw) < COUNT_OFF + 4:
        return 0
    n = struct.unpack_from("<I", raw, COUNT_OFF)[0]
    if not (0 < n <= COUNT_SANE_MAX):
        return COUNT_FALLBACK
    return n


def entries(raw: bytes):
    """返回分区表条目列表（dict）。

    每条至少包含：
        idx, name, doff, size, addr, type, abs_off, sha, iv
    其中 abs_off = doff + DATA_BASE 是**唯一**的绝对偏移定义；
    sha / iv 为 bytes（sha_hex / iv_hex 为对应的 hex 字符串）。
    """
    out = []
    for i in range(entry_count(raw)):
        off = TABLE_BASE + i * STRIDE
        if off + STRIDE > len(raw):
            break
        name = raw[off + F_NAME: off + F_NAME + 12].rstrip(b"\0").decode("ascii", "replace")
        doff, dsize, daddr, dtype = struct.unpack_from("<IIII", raw, off + F_DOFF)
        sha = raw[off + F_SHA: off + F_SHA + 32]
        iv = raw[off + F_IV: off + F_IV + 16]
        out.append(dict(
            idx=i,
            name=name,
            doff=doff,
            size=dsize,
            addr=daddr,
            type=dtype,
            abs_off=DATA_BASE + doff,   # ★ 唯一的绝对偏移定义
            sha=sha,
            iv=iv,
            sha_hex=sha.hex(),
            iv_hex=iv.hex(),
            iv_zero=(iv == b"\0" * 16),
            table_off=off,
        ))
    return out


def by_name(raw: bytes, name: str):
    for e in entries(raw):
        if e["name"] == name:
            return e
    return None


# ---------------------------------------------------------------------------
# 取数：唯一入口
# ---------------------------------------------------------------------------

def data(raw: bytes, e: dict) -> bytes:
    """★ 唯一的取数入口。正确偏移：raw[abs_off : abs_off+size]。"""
    s = e["abs_off"]
    return raw[s: s + e["size"]]


def data_legacy_wrong(raw: bytes, e: dict) -> bytes:
    """【仅用于对照臂】项目脚本的历史行为：raw[doff : doff+size]（错，少 0x200）。

    任何"错误偏移结果"都必须通过这个函数产生，以便审计者可复现。
    """
    s = e["doff"]
    return raw[s: s + e["size"]]


# ---------------------------------------------------------------------------
# 判决实验（self test）
# ---------------------------------------------------------------------------

def self_test_detail(raw: bytes):
    """对所有 type=2（明文）分区验证 sha256(data)==记录sha。

    返回 dict：
        hits, total, rows=[{idx,name,size,ok,rec_sha,calc_sha}], verdict
    """
    rows = []
    hits = 0
    for e in entries(raw):
        if e["type"] != TYPE_PLAINTEXT:
            continue
        d = data(raw, e)
        calc = hashlib.sha256(d).hexdigest()
        ok = (calc == e["sha_hex"])
        hits += int(ok)
        rows.append(dict(idx=e["idx"], name=e["name"], size=e["size"], ok=ok,
                         rec_sha=e["sha_hex"], calc_sha=calc))
    total = len(rows)
    if total == 0:
        verdict = "NO_PLAINTEXT_PARTITION"
    elif hits == total:
        verdict = "PASS"          # 偏移模型确证，可以做后续实验
    else:
        verdict = "FAIL"          # 模型仍不完整 ⇒ 立即停止，不要跑密钥搜索
    return dict(hits=hits, total=total, rows=rows, verdict=verdict)


def self_test(raw: bytes) -> int:
    """返回 type=2 分区的 SHA 命中数（V29 上期望 7）。"""
    return self_test_detail(raw)["hits"]


# ---------------------------------------------------------------------------
# 便捷函数
# ---------------------------------------------------------------------------

def load(path: str) -> bytes:
    with open(path, "rb") as f:
        return f.read()


def sha256(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def table_summary(raw: bytes):
    """按 type 分组统计（含 IV 零/唯一性），供实验 1/3 复用。"""
    es = entries(raw)
    groups = {}
    for e in es:
        g = groups.setdefault(e["type"], dict(n=0, iv_zero=0, ivs=set(), total_size=0))
        g["n"] += 1
        g["iv_zero"] += int(e["iv_zero"])
        if not e["iv_zero"]:
            g["ivs"].add(e["iv_hex"])
        g["total_size"] += e["size"]
    for g in groups.values():
        g["iv_unique_nonzero"] = len(g["ivs"])
        g.pop("ivs")
    return groups


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

DEFAULT_FW = "02_固件二进制/DC-S5/S5___V29.bin"


def main(argv):
    path = argv[1] if len(argv) > 1 else DEFAULT_FW
    raw = load(path)
    det = self_test_detail(raw)
    print(f"# upd_table.py 单一真源  DATA_BASE=0x{DATA_BASE:x} TABLE_BASE=0x{TABLE_BASE:x} STRIDE={STRIDE}")
    print(f"# 固件: {path}")
    print(f"# 大小: {len(raw)} bytes (0x{len(raw):x})  条目数@0x{COUNT_OFF:x} = {entry_count(raw)}")
    ds, dt, ev = struct.unpack_from("<III", raw, DIR_HDR_OFF)
    print(f"# 目录头: data_start=0x{ds:x} data_total=0x{dt:x} entry_field=0x{ev:x}")
    print()
    print(f"{'#':>3} {'name':<12} {'doff':>9} {'size':>9} {'abs_off':>9} {'type':>4} {'iv0':>3}  {'sha(rec)[:16]':<16}")
    for e in entries(raw):
        print(f"{e['idx']:>3} {e['name']:<12} {e['doff']:>9x} {e['size']:>9x} {e['abs_off']:>9x} "
              f"{e['type']:>4} {str(e['iv_zero']):>3}  {e['sha_hex'][:16]}")
    print()
    print("=== 判决实验：type=2 分区 sha256(data)==记录sha ===")
    for r in det["rows"]:
        print(f"  [{r['idx']:>2}] {r['name']:<12} size={r['size']:>8} rec={r['rec_sha'][:16]}.. "
              f"calc={r['calc_sha'][:16]}..  {'OK' if r['ok'] else 'MISMATCH'}")
    print(f"  命中 {det['hits']}/{det['total']}  verdict={det['verdict']}")
    print()
    print("=== 按 type 分组 ===")
    for t, g in sorted(table_summary(raw).items()):
        print(f"  type={t}: n={g['n']:>2}  iv_zero={g['iv_zero']:>2}  "
              f"iv_unique(非零)={g['iv_unique_nonzero']:>2}  total_size=0x{g['total_size']:x}")
    return 0 if det["verdict"] == "PASS" else 1


if __name__ == "__main__":
    import os
    here = os.path.dirname(os.path.abspath(__file__))
    if len(sys.argv) == 1:
        cand = os.path.normpath(os.path.join(here, "..", "..", DEFAULT_FW))
        if os.path.exists(cand):
            sys.argv.append(cand)
    sys.exit(main(sys.argv))
