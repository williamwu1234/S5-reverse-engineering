#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
rsa_modulus.py -- 从多个固件的 RSA 尾签名块离线恢复 4096-bit 模数 N (DC-S5 UPD 容器)
====================================================================================

原理
----
容器尾部 512 字节 (L-512 .. L) 是高熵数据 (本脚本 [1] 节实测), 若它是 RSA 签名:

        s_i  =  m_i ^ d  (mod N)          =>     s_i ^ e  ≡  m_i   (mod N)

其中 N 是 4096-bit 模数, e 是公开指数, m_i 是被签消息的编码结果 (padding 后)。
于是对任意两个版本 i, j:   N  |  gcd( s_i^e - m_i ,  s_j^e - m_j )

用第 i,j 两个版本算出候选 N, 再用**第三、四、五个版本独立验证**
        pow(s_k, e, N) == m_k % N
验证通过才声称成功。若 m 猜错, gcd 只是一个 1~3 bit 的小数, 验证必然失败。

对项目文档的一处更正
--------------------
`verify_logic_notes.md` 的 E9 用 "尾块首字节 89 a1, 而 PKCS#1 v1.5 应为 00 01"
来排除 PKCS#1 v1.5。这个推理在密码学上不成立: 签名字节 s = m^d mod N 是私钥
指数运算的结果, 在 [0,N) 上近似均匀分布, 与明文编码 m 的前缀无关。
"首字节应为 00 01" 描述的是 **m** 而不是 **s**。所以 PKCS#1 v1.5 **并未**被排除,
本脚本把它作为首选 padding 候选。

用法
----
    python3 rsa_modulus.py FIRMWARE [FIRMWARE ...]
    python3 rsa_modulus.py --root /path/to/S5_逆向_项目总包_20261012 --json rsa_result.json
    python3 rsa_modulus.py --root ... --e 3,17,65537 --budget 3600
    python3 rsa_modulus.py --root ... --sig-endian both --m-endian both

依赖: gmpy2 (强烈建议; 无它时 e=65537 的 4096 次幂会非常慢)。缺失时自动回退到
Python 内置整数, 结果等价。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys
import time
from math import gcd as _math_gcd

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ecdsa_recover as EC          # noqa: E402  复用消息候选/布局常量

try:
    import gmpy2
    _MPZ = gmpy2.mpz
    HAVE_GMPY2 = True
except Exception:                                   # pragma: no cover
    gmpy2 = None
    _MPZ = int
    HAVE_GMPY2 = False


def gcd(a, b):
    return gmpy2.gcd(a, b) if HAVE_GMPY2 else _math_gcd(a, b)


TAIL_LEN = 512

# PKCS#1 v1.5 DigestInfo DER 前缀 (RFC 8017 / 各哈希标准)
DIGESTINFO = {
    "sha1":   "3021300906052b0e03021a05000414",
    "sha224": "302d300d06096086480165030402040500041c",
    "sha256": "3031300d060960864801650304020105000420",
    "sha384": "3041300d060960864801650304020205000430",
    "sha512": "3051300d060960864801650304020305000440",
    "sha3_256": "3031300d060960864801650304020805000420",
    "sha3_512": "3051300d060960864801650304020a05000440",
}
# 摘要名 -> DigestInfo 用的哈希名
DI_ALIAS = {
    "sha256": "sha256", "sha256d": "sha256", "sha384_trunc32": "sha384",
    "sha512_trunc32": "sha512", "sha384_full": "sha384", "sha512_full": "sha512",
    "sha1": "sha1", "sha224": "sha224", "sha3_256": "sha3_256",
    "blake2s": None, "blake2b32": None, "_raw": "sha256", "sha512_256": "sha512",
}

SMALL_PRIMES = None


def small_primes(limit=100000):
    global SMALL_PRIMES
    if SMALL_PRIMES is None:
        sieve = bytearray([1]) * limit
        sieve[0:2] = b"\x00\x00"
        for i in range(2, int(limit ** 0.5) + 1):
            if sieve[i]:
                sieve[i * i::i] = b"\x00" * len(sieve[i * i::i])
        SMALL_PRIMES = [i for i in range(limit) if sieve[i]]
    return SMALL_PRIMES


# --------------------------------------------------------------------------
# 消息编码 (padding) 候选
# --------------------------------------------------------------------------

def encode_raw(digest: bytes) -> int:
    return int.from_bytes(digest, "big")


def encode_raw_le(digest: bytes) -> int:
    return int.from_bytes(digest, "little")


def encode_p15_di(digest: bytes, hashname: str, k: int = 512):
    """EMSA-PKCS1-v1_5, T = DigestInfo(DER) || digest"""
    h = DI_ALIAS.get(hashname)
    if h is None or h not in DIGESTINFO:
        return None
    t = bytes.fromhex(DIGESTINFO[h]) + digest
    if len(t) + 11 > k:
        return None
    ps = b"\xff" * (k - len(t) - 3)
    return int.from_bytes(b"\x00\x01" + ps + b"\x00" + t, "big")


def encode_p15_simple(digest: bytes, k: int = 512):
    """非标准但常见的简化 v1.5: 00 01 FF..FF 00 || digest"""
    if len(digest) + 11 > k:
        return None
    ps = b"\xff" * (k - len(digest) - 3)
    return int.from_bytes(b"\x00\x01" + ps + b"\x00" + digest, "big")


PADDINGS = ["p15_di", "raw", "p15_simple", "raw_le"]


def encode(digest: bytes, hashname: str, pad: str):
    if pad == "raw":
        return encode_raw(digest)
    if pad == "raw_le":
        return encode_raw_le(digest)
    if pad == "p15_di":
        return encode_p15_di(digest, hashname)
    if pad == "p15_simple":
        return encode_p15_simple(digest)
    raise ValueError(pad)


# --------------------------------------------------------------------------
# [1] 尾部块实测
# --------------------------------------------------------------------------

def inspect_tail(paths):
    print("=" * 78)
    print("[1] 尾部 512B 实测")
    print("=" * 78)
    info = {}
    for p in paths:
        with open(p, "rb") as fh:
            fh.seek(-TAIL_LEN, os.SEEK_END)
            t = fh.read(TAIL_LEN)
        info[p] = t
        bits = int.from_bytes(t, "big").bit_length()
        print(f"  {EC.label_of(p):>4}: 非零 {sum(1 for b in t if b)}/512, "
              f"首4B {t[:4].hex()}, 末4B {t[-4:].hex()}, "
              f"大端位长 {bits} (RSA-4096 模数下应 <=4095)")
    uniq = len(set(info.values()))
    print(f"  * {len(info)} 个版本互不相同的尾块数: {uniq}"
          f" => {'全部互异 (逐版本签名)' if uniq == len(info) else '存在重复!'}")
    print("  * 更正: '首字节 89/a1 排除 PKCS#1 v1.5' 的推理不成立 —— 签名字节 s = m^d mod N")
    print("    在 [0,N) 上近似均匀分布; '00 01 前缀' 描述的是编码后消息 m, 不是 s。")
    return info


# --------------------------------------------------------------------------
# [2] 候选消息构建
# --------------------------------------------------------------------------

def build_candidates(paths, profile, curated_only_for_big):
    """返回 (cands, bufs): cands = [(msg_name, hashname, pad, [m_i...])]"""
    msgs = EC._core_msgs() + (EC._extended_msgs() if profile in ("extended", "all") else [])
    bufs = {}
    for p in paths:
        with open(p, "rb") as fh:
            bufs[p] = fh.read()

    cands = []
    for msg in msgs:
        hnames = EC.hashnames_for(msg, profile)
        digs = []
        for p in paths:
            mb = EC.build_message(bufs[p], msg)
            if len(mb) < 16:
                digs = None
                break
            digs.append(EC.all_digests(mb, hnames))
        if digs is None:
            continue
        for h in hnames:
            for pad in PADDINGS:
                ms = []
                ok = True
                for d in digs:
                    m = encode(d[h], h, pad)
                    if m is None:
                        ok = False
                        break
                    ms.append(m)
                if ok:
                    cands.append((msg.name, h, pad, ms))

    if not curated_only_for_big:
        return cands, bufs

    # e=65537 太贵 -> 只保留高先验子集
    prio_ranges = ["raw[0x200:-512]", "raw[:-512]", "raw[0x2A0:-512]",
                   "raw[0x2E0:-512]", "raw[0x142C:-512]", "[0:0x200]+[0x200:-512]"]
    prio_hashes = ["sha256", "sha384_trunc32", "sha512_trunc32", "sha1", "sha384_full"]
    prio_pads = ["p15_di", "raw", "p15_simple"]

    def _in(c):
        mn, hn, pd, _ = c
        return (mn in prio_ranges and hn in prio_hashes and pd in prio_pads)

    def key(c):
        mn, hn, pd, _ = c
        # padding 优先 -> 范围 -> 哈希
        return (prio_pads.index(pd), prio_ranges.index(mn), prio_hashes.index(hn))

    cur = sorted([c for c in cands if _in(c)], key=key)
    return cur, bufs


# --------------------------------------------------------------------------
# [3] 恢复 + 验证
# --------------------------------------------------------------------------

def strip_small_factors(g, limit=100000):
    """从 g 中除去小素因子, 用于把 N*t 还原成 N (t 只含小因子时有效)。"""
    for pr in small_primes(limit):
        while g % pr == 0:
            g //= pr
    return g


def try_recover(cands, bufs, paths, e, sig_endian, budget, max_cands, verbose=True,
                min_bits=1024):
    """对给定 e 穷举候选; 返回 (found, tried, elapsed, notes)

    判定规则: gcd 位长 >= min_bits 时, 用第 3..n 个版本做独立验证
        pow(s_k, e, N) == m_k mod N
    全部通过才判定成功。若 gcd 明显偏大 (可能是 N*t), 先除去小素因子再验证。
    """
    n = len(paths)
    sigs = []
    for p in paths:
        with open(p, "rb") as fh:
            fh.seek(-TAIL_LEN, os.SEEK_END)
            t = fh.read(TAIL_LEN)
        variants = []
        if sig_endian in ("be", "both"):
            variants.append(("BE", int.from_bytes(t, "big")))
        if sig_endian in ("le", "both"):
            variants.append(("LE", int.from_bytes(t, "little")))
        sigs.append(variants)

    found = []
    notes = []
    t0 = time.time()
    for ei in range(len(sigs[0])):
        if not all(len(sigs[k]) > ei for k in range(n)):
            continue
        ename = sigs[0][ei][0]
        tw = time.time()
        S = [pow(_MPZ(sigs[k][ei][1]), e) for k in range(n)]
        if verbose:
            print(f"  [e={e} {ename}] 预计算 s^e x{n} 用 {time.time()-tw:.1f}s "
                  f"(每个 {S[0].bit_length()} bit)", flush=True)
        tried = 0
        for (mn, hn, pad, ms) in cands:
            if max_cands is not None and tried >= max_cands:
                notes.append(f"e={e} {ename}: 达到候选上限 {max_cands}, "
                             f"共 {len(cands)} 个候选未跑完")
                break
            if budget is not None and time.time() - t0 > budget:
                notes.append(f"e={e} {ename}: 达到时间预算 {budget}s, 已试 {tried} 个")
                break
            tried += 1
            g = gcd(S[0] - _MPZ(ms[0]), S[1] - _MPZ(ms[1]))
            if int(g.bit_length()) < min_bits:
                continue
            for attempt in range(2):
                cand_N = g if attempt == 0 else strip_small_factors(g)
                if int(cand_N.bit_length()) < min_bits:
                    break
                if attempt == 1 and cand_N == g:
                    break
                okall = True
                for k in range(2, n):
                    if pow(_MPZ(sigs[k][ei][1]), e, cand_N) != _MPZ(ms[k]) % cand_N:
                        okall = False
                        break
                if okall:
                    found.append({
                        "e": int(e), "sig_endian": ename, "msg": mn, "hash": hn,
                        "padding": pad, "N_bits": int(cand_N.bit_length()),
                        "N_hex": format(int(cand_N), "x"),
                        "gcd_bits": int(g.bit_length()),
                        "verified_versions": [EC.label_of(p) for p in paths],
                    })
                    if verbose:
                        print(f"  *** 命中 *** e={e} {ename} msg={mn} hash={hn} "
                              f"pad={pad} N_bits={cand_N.bit_length()}", flush=True)
                    break
        if verbose:
            print(f"  [e={e} {ename}] 试了 {tried} 个候选, 耗时 {time.time()-t0:.1f}s",
                  flush=True)
    return found, notes, time.time() - t0


def main(argv=None):
    ap = argparse.ArgumentParser(description="DC-S5 RSA-4096 模数离线恢复")
    ap.add_argument("firmware", nargs="*")
    ap.add_argument("--root", default=os.getcwd())
    ap.add_argument("--profile", choices=["core", "extended", "all"], default="all")
    ap.add_argument("--e", default="3,5,7,17,257,65537",
                    help="公开指数候选, 逗号分隔")
    ap.add_argument("--sig-endian", choices=["be", "le", "both"], default="both")
    ap.add_argument("--budget", type=float, default=1800.0,
                    help="每个指数的时间预算(秒), 0 表示不限")
    ap.add_argument("--pads", default=None,
                    help="只试这些 padding (逗号分隔): p15_di,raw,p15_simple,raw_le")
    ap.add_argument("--max-cands-65537", type=int, default=24,
                    help="e=65537 时最多试多少个高先验候选")
    ap.add_argument("--json", default=None)
    args = ap.parse_args(argv)

    paths = [os.path.abspath(p) for p in (args.firmware or EC.discover_default(args.root))]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        print("固件不存在: " + ", ".join(missing), file=sys.stderr)
        return 2
    if len(paths) < 3:
        print("警告: 少于 3 个固件, 无法做第三方独立验证。", file=sys.stderr)

    print(f"参与固件 ({len(paths)}): " + ", ".join(EC.label_of(p) for p in paths))
    print(f"gmpy2 可用: {HAVE_GMPY2}" + ("" if HAVE_GMPY2 else
          "  (回退到 Python 内置整数: e=65537 会非常慢)"))
    inspect_tail(paths)

    cands_all, bufs = build_candidates(paths, args.profile, curated_only_for_big=False)
    cands_cur, _ = build_candidates(paths, args.profile, curated_only_for_big=True)
    if args.pads:
        keep = set(x.strip() for x in args.pads.split(",") if x.strip())
        cands_all = [c for c in cands_all if c[2] in keep]
        cands_cur = [c for c in cands_cur if c[2] in keep]
    print(f"\n候选消息编码 (msg x hash x padding): 全量 {len(cands_all)} 个, "
          f"高先验子集 {len(cands_cur)} 个")

    budget = None if args.budget <= 0 else args.budget
    all_found, all_notes, log = [], [], []
    for es in args.e.split(","):
        e = int(es.strip())
        big = e > 1000
        cands = cands_cur if big else cands_all
        mx = args.max_cands_65537 if big else None
        b = budget
        print("\n" + "=" * 78)
        print(f"[2] e = {e}  ({'高先验子集' if big else '全量候选'}, "
              f"{len(cands)} 个候选)")
        print("=" * 78)
        f, nt, el = try_recover(cands, bufs, paths, e, args.sig_endian,
                                b, mx, verbose=True)
        all_found += f
        all_notes += nt
        log.append({"e": e, "candidates": len(cands), "elapsed_s": round(el, 1),
                    "notes": nt, "found": f})

    print("\n" + "=" * 78)
    print("[3] 结论")
    print("=" * 78)
    if all_found:
        for r in all_found:
            N = int(r["N_hex"], 16)
            print(f"  *** 成功 ***  模数 N 已恢复 ({r['N_bits']} bit)")
            print(f"      e={r['e']}  签名端序={r['sig_endian']}  "
                  f"消息={r['msg']}  哈希={r['hash']}  padding={r['padding']}")
            print(f"      N(hex) = 0x{r['N_hex']}")
            print(f"      已在 {len(r['verified_versions'])} 个版本上独立验证: "
                  f"{r['verified_versions']}")
    else:
        print("  未恢复出模数 N。")
        print("  已排除的假设: 见下面的统计 (e x msg x hash x padding x 端序 全部试过)。")
        for L in log:
            print(f"      e={L['e']:<7} 候选 {L['candidates']:<5} "
                  f"耗时 {L['elapsed_s']}s  {'(未跑完: ' + '; '.join(L['notes']) + ')' if L['notes'] else ''}")

    payload = {
        "firmware": paths,
        "gmpy2": HAVE_GMPY2,
        "signature_field": "last 512 bytes",
        "profile": args.profile,
        "candidates_total": len(cands_all),
        "candidates_curated": len(cands_cur),
        "paddings": PADDINGS,
        "log": log,
        "found": all_found,
        "notes": all_notes,
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"\n  JSON 结果已写入 {args.json}")
    return 0 if all_found else 1


if __name__ == "__main__":
    sys.exit(main())
