#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ecdsa_recover.py -- 离线 ECDSA 公钥恢复 / 签名覆盖范围判定 (DC-S5 UPD 容器)
===========================================================================

对象: Panasonic LUMIX DC-S5 "UPD" 固件容器 (芯片 MC801), 例如 S5___V29.bin。

纯离线数学。不连接任何设备, 不解密任何数据, 不上传任何东西。

容器结构 (项目已证实, 本脚本仅按事实引用; 所有偏移均在本脚本 [1] 节实测复现):
    0x000-0x200  外层 UPD 头 (512B, 含 0x1C 机型/版本 id, 0x24 BCD 时间戳, 0x40 CRC32)
    0x200-0x20C  b"panasonic"
    0x20C-0x220  全 0
    0x220-0x260  64 字节高熵区   <-- 假定为 ECDSA (r,s)
    0x260-0x2A0  全 0
    0x2A0-0x2E0  内层 UPD 头
    0x2E0-0x2EC  目录头
    0x2EC-0x142C 分区表 (48 x 92B)
    0x142C-...   分区数据
    L-512-L      RSA-4096 尾签名块

方法 (为什么这样做就能判定覆盖范围)
------------------------------------
ECDSA 公钥恢复公式:  Q = r^-1 (s*R - e*G)   (e = 被签消息的摘要标量)

给定 (r,s) 和**猜测的**摘要 e, 上式总能算出一个"公钥"Q。只有当 e 真的是签名时
使用的那个摘要时, Q 才是真实公钥; 否则 Q 是一个无意义的随机点。

判据: 同一台相机、同一把私钥对 5 个固件版本各签了一次。若某个 (消息范围, 哈希,
编码端序, 曲线) 组合是**正确**的, 则 5 个版本必须恢复出**同一个** Q。
反之, 两个错误猜测给出相同 Q 的概率约为 2^-256。这是个近乎零误报的判定。

用法
----
    python3 ecdsa_recover.py FIRMWARE [FIRMWARE ...] [--profile core|extended|all]
    python3 ecdsa_recover.py --root /path/to/S5_逆向_项目总包_20261012
    python3 ecdsa_recover.py --root ... --json result.json

依赖: python-ecdsa (pip install ecdsa)。若缺失, 脚本对 P-256 自动回退到内置纯
Python 实现, 结果等价 (只是慢), 因此无第三方库时仍可重跑。
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import sys

# --------------------------------------------------------------------------
# 一、P-256 常量 + 内置纯 Python 实现 (无第三方依赖的兜底 & 独立交叉验证)
# --------------------------------------------------------------------------

P256_P = 0xFFFFFFFF00000001000000000000000000000000FFFFFFFFFFFFFFFFFFFFFFFF
P256_A = P256_P - 3
P256_B = 0x5AC635D8AA3A93E7B3EBBD55769886BC651D06B0CC53B0F63BCE3C3E27D2604B
P256_N = 0xFFFFFFFF00000000FFFFFFFFFFFFFFFFBCE6FAADA7179E84F3B9CAC2FC632551
P256_G = (0x6B17D1F2E12C4247F8BCE6E563A440F277037D812DEB33A0F4A13945D898C296,
          0x4FE342E2FE1A7F9B8EE7EB4A7C0F9E162BCE33576B315ECECBB6406837BF51F5)


def _pt_add(p1, p2):
    if p1 is None:
        return p2
    if p2 is None:
        return p1
    x1, y1 = p1
    x2, y2 = p2
    if x1 == x2 and (y1 + y2) % P256_P == 0:
        return None
    if p1 == p2:
        lam = (3 * x1 * x1 + P256_A) * pow(2 * y1, P256_P - 2, P256_P) % P256_P
    else:
        lam = (y2 - y1) * pow(x2 - x1, P256_P - 2, P256_P) % P256_P
    x3 = (lam * lam - x1 - x2) % P256_P
    return (x3, (lam * (x1 - x3) - y1) % P256_P)


def _pt_mul(k, pt):
    k %= P256_N
    if k == 0 or pt is None:
        return None
    r = None
    while k:
        if k & 1:
            r = _pt_add(r, pt)
        pt = _pt_add(pt, pt)
        k >>= 1
    return r


def _pt_on_curve(pt):
    if pt is None:
        return False
    x, y = pt
    if not (0 <= x < P256_P and 0 <= y < P256_P):
        return False
    return (y * y - (x * x * x + P256_A * x + P256_B)) % P256_P == 0


def decompress_point(comp: bytes):
    if len(comp) != 33 or comp[0] not in (2, 3):
        return None
    x = int.from_bytes(comp[1:], "big")
    if x >= P256_P:
        return None
    rhs = (pow(x, 3, P256_P) + P256_A * x + P256_B) % P256_P
    y = pow(rhs, (P256_P + 1) // 4, P256_P)          # p == 3 (mod 4)
    if (y * y - rhs) % P256_P != 0:
        return None
    if (y & 1) != (comp[0] & 1):
        y = P256_P - y
    return (x, y)


def pure_verify(comp_pub: bytes, r: int, s: int, e: int) -> bool:
    """完全独立的纯 Python P-256 ECDSA 验签 (不依赖任何第三方库)。"""
    if not (1 <= r < P256_N and 1 <= s < P256_N):
        return False
    q = decompress_point(comp_pub)
    if q is None or not _pt_on_curve(q):
        return False
    try:
        w = pow(s, -1, P256_N)
    except ValueError:
        return False
    x = _pt_add(_pt_mul(e * w % P256_N, P256_G), _pt_mul(r * w % P256_N, q))
    return x is not None and x[0] % P256_N == r


def pure_recover(r: int, s: int, e: int):
    """纯 Python P-256 公钥恢复 -> 压缩点 bytes 列表 (覆盖全部 4 个 recid)。"""
    if not (1 <= r < P256_N and 1 <= s < P256_N):
        return []
    out = []
    r_inv = pow(r, -1, P256_N)
    for j in range(4):
        x = r + (j >> 1) * P256_N
        if x >= P256_P:
            continue
        rhs = (pow(x, 3, P256_P) + P256_A * x + P256_B) % P256_P
        y = pow(rhs, (P256_P + 1) // 4, P256_P)
        if (y * y - rhs) % P256_P != 0:
            continue
        if (y & 1) != (j & 1):
            y = P256_P - y
        R = (x, y)
        if _pt_mul(P256_N, R) is not None:
            continue
        sR = _pt_mul(s, R)
        eG = _pt_mul(e % P256_N, P256_G)
        Q = _pt_mul(r_inv, _pt_add(sR, None if eG is None else (eG[0], (-eG[1]) % P256_P)))
        if Q is None:
            continue
        comp = bytes([2 + (Q[1] & 1)]) + Q[0].to_bytes(32, "big")
        if pure_verify(comp, r, s, e):
            out.append(comp)
    return out


# --------------------------------------------------------------------------
# 二、可选加速库 python-ecdsa (支持多曲线)
# --------------------------------------------------------------------------

try:
    import ecdsa as _ecdsa
    from ecdsa import VerifyingKey
    from ecdsa.util import sigdecode_string
    HAVE_ECDSA = True
except Exception:                                        # pragma: no cover
    _ecdsa = None
    HAVE_ECDSA = False


def _list_curves():
    """返回 [(显示名, curve对象或None)]；curve 为 None 表示用内置纯 Python P-256。"""
    out = []
    if HAVE_ECDSA:
        for nm in ("NIST256p", "SECP256k1", "BRAINPOOLP256r1"):
            c = getattr(_ecdsa, nm, None)
            if c is not None:
                out.append((nm, c))
    else:
        out.append(("NIST256p", None))
    return out


CURVES = _list_curves()


def lib_recover(sig64: bytes, digest: bytes, curve):
    """python-ecdsa 公钥恢复 -> 压缩点 bytes 列表。"""
    try:
        keys = VerifyingKey.from_public_key_recovery_with_digest(
            sig64, digest, curve, sigdecode=sigdecode_string, allow_truncate=True)
    except Exception:
        return []
    try:
        return [k.to_string("compressed") for k in keys]
    except Exception:
        # BRAINPOOLP256r1 等曲线的 to_string("compressed") 需要曲线支持压缩点
        return [b"\x04" + k.to_string("uncompressed") for k in keys]


# --------------------------------------------------------------------------
# 三、容器布局常量 (实测)
# --------------------------------------------------------------------------

SIG_FIELD = (0x220, 0x260)          # 64B: 假定 r(32) || s(32)
OUTER_HDR = (0x000, 0x200)
INNER_HDR = (0x2A0, 0x2E0)
DIR_HDR = (0x2E0, 0x2EC)
PART_TABLE = (0x2EC, 0x142C)
PART_ENTRY = 92
PART_DIGEST_OFF = 0x1C              # 条目内 SHA-256(明文) 偏移
PART_NAME_LEN = 12
TAIL_LEN = 512

# 需要裁决的 "版本字段" 所在区间
VERSION_FIELDS = [
    ("0x1C u32 机型/版本 id", 0x1C, 0x20),
    ("0x24 u32 BCD 构建时间戳", 0x24, 0x28),
    ("0x40 u32 CRC32", 0x40, 0x44),
]

EOF = object()


# --------------------------------------------------------------------------
# 四、消息候选 (被 ECDSA 签名的字节串) 框架
# --------------------------------------------------------------------------

class Msg:
    """一条 "被签名字节串" 候选。

    segs  : [(start, end)] 顺序拼接; end 可为 EOF(到文件尾) 或负数(相对文件尾)
    zero  : [(a, b)] 绝对偏移窗口, 拼接后清零 (模拟 "签名字段/CRC 字段先置零")
    direct: 直接给出摘要字节 (不做哈希), 例如分区表里的 SHA-256
    """

    __slots__ = ("name", "segs", "zero", "direct", "profile")

    def __init__(self, name, segs, zero=(), direct=None, profile="core"):
        self.name = name
        self.segs = segs
        self.zero = tuple(zero)
        self.direct = direct
        self.profile = profile

    def build(self, buf: bytes):
        """返回待哈希的字节串 (bytes/bytearray)；direct 时返回 None。"""
        if self.direct is not None:
            return None
        L = len(buf)
        parts, track = [], []
        pos = 0
        for a, b in self.segs:
            bb = L if b is EOF else (L + b if (isinstance(b, int) and b < 0) else b)
            bb = min(L, bb)
            aa = L + a if (isinstance(a, int) and a < 0) else a   # 支持负起点(尾部锚定)
            aa = max(0, min(L, aa))
            if bb <= aa:
                continue
            seg = bytearray(buf[aa:bb])
            parts.append(seg)
            track.append((pos, aa, bb - aa))
            pos += bb - aa
        if not parts:
            return b""
        if self.zero:
            joined = bytearray().join(parts)
            for za, zb in self.zero:
                for out_off, abs_off, ln in track:
                    s = max(za, abs_off)
                    e = min(zb, abs_off + ln)
                    if e > s:
                        joined[out_off + (s - abs_off): out_off + (e - abs_off)] = \
                            b"\x00" * (e - s)
            return joined
        return parts[0] if len(parts) == 1 else bytearray().join(parts)


def _core_msgs():
    seg = lambda *s: list(s)
    m = []
    simple = [
        ("raw",                [(0x000, EOF)]),
        ("raw[0x200:]",        [(0x200, EOF)]),
        ("raw[0x2A0:]",        [(0x2A0, EOF)]),
        ("raw[0x2E0:]",        [(0x2E0, EOF)]),
        ("raw[0x142C:]",       [(0x142C, EOF)]),
        ("raw[:-512]",         [(0x000, -512)]),
        ("raw[0x200:-512]",    [(0x200, -512)]),
        ("raw[0x2A0:-512]",    [(0x2A0, -512)]),
        ("raw[0x2E0:-512]",    [(0x2E0, -512)]),
        ("raw[0x142C:-512]",   [(0x142C, -512)]),
        ("raw[:0x200]",        [(0x000, 0x200)]),
        ("raw[:0x2A0]",        [(0x000, 0x2A0)]),
        ("raw[:0x2E0]",        [(0x000, 0x2E0)]),
        ("raw[:0x142C]",       [(0x000, 0x142C)]),
        ("raw[0x200:0x2A0]",   [(0x200, 0x2A0)]),
        ("raw[0x200:0x2E0]",   [(0x200, 0x2E0)]),
        ("raw[0x200:0x142C]",  [(0x200, 0x142C)]),
        ("raw[0x200:0x2DC]",   [(0x200, 0x2DC)]),
        ("raw[0x2A0:0x2DC]",   [(0x2A0, 0x2DC)]),
        ("raw[0x2A0:0x142C]",  [(0x2A0, 0x142C)]),
        ("raw[0x2E0:0x142C]",  [(0x2E0, 0x142C)]),
        ("raw[:0x40]",         [(0x000, 0x40)]),
        ("raw[:0x220]",        [(0x000, 0x220)]),
        ("raw[0x260:0x2A0]",   [(0x260, 0x2A0)]),
    ]
    for nm, sg in simple:
        m.append(Msg(nm, sg))
        if any(a < SIG_FIELD[1] and (b is EOF or (b < 0) or b > SIG_FIELD[0])
               for a, b in sg):
            m.append(Msg(nm + " +签名区清零", sg, zero=[SIG_FIELD]))
    return m


def _extended_msgs():
    """扩展候选: 复合段 / 头部字段清零 / 直接摘要 (分区表 SHA-256)。"""
    m = []
    # --- 复合拼接 ---
    comp = [
        ("[0:0x40]+[0x2A0:0x2E0]",        [(0x0, 0x40), (0x2A0, 0x2E0)]),
        ("[0:0x200]+[0x2A0:0x2E0]",       [(0x0, 0x200), (0x2A0, 0x2E0)]),
        ("[0:0x200]+[0x2A0:0x2EC]",       [(0x0, 0x200), (0x2A0, 0x2EC)]),
        ("[0:0x200]+[0x2A0:0x142C]",      [(0x0, 0x200), (0x2A0, 0x142C)]),
        ("[0:0x200]+[0x2A0:-512]",        [(0x0, 0x200), (0x2A0, -512)]),
        ("[0:0x200]+[0x200:-512]",        [(0x0, 0x200), (0x200, -512)]),
        ("[0:0x220]+[0x260:0x2A0]",       [(0x0, 0x220), (0x260, 0x2A0)]),
        ("[0:0x220]+[0x260:-512]",        [(0x0, 0x220), (0x260, -512)]),
        ("[0:0x220]+[0x260:]",            [(0x0, 0x220), (0x260, EOF)]),
        ("[0x200:0x220]+[0x260:-512]",    [(0x200, 0x220), (0x260, -512)]),
        ("[0x200:0x220]+[0x260:]",        [(0x200, 0x220), (0x260, EOF)]),
        ("[0:0x200]+[0x2EC:0x142C]",      [(0x0, 0x200), (0x2EC, 0x142C)]),
        ("[0x2EC:0x142C]",                [(0x2EC, 0x142C)]),
        ("[0x0:0x142C]",                  [(0x0, 0x142C)]),
        ("[0x40:0x200]",                  [(0x40, 0x200)]),
        ("[0x0:0x1C]",                    [(0x0, 0x1C)]),
        ("[0x20:0x40]",                   [(0x20, 0x40)]),
        ("[0x44:0x200]",                  [(0x44, 0x200)]),
    ]
    for nm, sg in comp:
        m.append(Msg(nm, sg, profile="extended"))
        if any(a < SIG_FIELD[1] and (b is EOF or (b < 0) or b > SIG_FIELD[0])
               for a, b in sg):
            m.append(Msg(nm + " +签名区清零", sg, zero=[SIG_FIELD], profile="extended"))

    # --- 头部字段清零变体 (对以 0 开头、覆盖头部的消息) ---
    zero_sets = [
        ("CRC置零", [(0x40, 0x44)]),
        ("机型id置零", [(0x1C, 0x20)]),
        ("时间戳置零", [(0x24, 0x28)]),
        ("长度字段置零", [(0x3C, 0x40)]),
        ("CRC+签名区置零", [(0x40, 0x44), SIG_FIELD]),
    ]
    bases = [
        ("raw",            [(0x000, EOF)]),
        ("raw[0x200:]",    [(0x200, EOF)]),
        ("raw[:-512]",     [(0x000, -512)]),
        ("raw[0x200:-512]", [(0x200, -512)]),
        ("raw[:0x200]",    [(0x000, 0x200)]),
        ("raw[:0x2A0]",    [(0x000, 0x2A0)]),
    ]
    for bn, sg in bases:
        for zn, zw in zero_sets:
            m.append(Msg(f"{bn} +{zn}", sg, zero=zw, profile="extended"))

    # --- 尾部锚定区间 (覆盖 "ECDSA 签的是 RSA 尾块本身" 这类双签名设计) ---
    for nm, a in [("raw[-512:]", -512), ("raw[-1024:]", -1024),
                  ("raw[-4096:]", -4096)]:
        m.append(Msg(nm, [(a, EOF)], profile="extended"))
        m.append(Msg(nm + " 签名清零", [(a, EOF)], zero=[SIG_FIELD],
                     profile="extended"))

    # --- 直接摘要: 分区表条目里的 32B SHA-256 ---
    for i in range(48):
        m.append(Msg(f"PT[{i}].sha256(直接)", [], direct=("pt_digest", i),
                     profile="extended"))
    m.append(Msg("sha256(48x分区摘要拼接)", [], direct=("pt_digest_cat", None),
                 profile="extended"))
    m.append(Msg("48x分区摘要拼接(直接)", [], direct=("pt_digest_cat_raw", None),
                 profile="extended"))
    return m


def _deep_msgs():
    """深度候选: 头部可变字段的**全部子集清零** (规范化后再签名是常见做法)。

    可变字段: 0x1C 机型/版本 id, 0x24 BCD 时间戳, 0x3C 数据总长, 0x40 CRC32。
    每个基范围 x 16 个清零子集 x {签名区原样, 签名区清零}。
    """
    import itertools
    fields = [(0x1C, 0x20), (0x24, 0x28), (0x3C, 0x40), (0x40, 0x44)]
    bases = [
        ("raw",              [(0x000, EOF)]),
        ("raw[:-512]",       [(0x000, -512)]),
        ("raw[0x200:]",      [(0x200, EOF)]),
        ("raw[0x200:-512]",  [(0x200, -512)]),
        ("raw[:0x200]",      [(0x000, 0x200)]),
        ("raw[:0x2A0]",      [(0x000, 0x2A0)]),
        ("raw[:0x2E0]",      [(0x000, 0x2E0)]),
        ("raw[0x2A0:0x142C]", [(0x2A0, 0x142C)]),
    ]
    out = []
    for bn, sg in bases:
        covers_sig = any(a < SIG_FIELD[1] and (b is EOF or (b < 0) or b > SIG_FIELD[0])
                         for a, b in sg)
        for r in range(1 << len(fields)):
            zs = [fields[i] for i in range(len(fields)) if (r >> i) & 1]
            tag = "+".join(f"0x{a:X}" for a, _ in zs) if zs else "无清零"
            out.append(Msg(f"{bn} [清{tag}]", sg, zero=zs, profile="deep"))
            if covers_sig:
                out.append(Msg(f"{bn} [清{tag}+签名区]", sg, zero=zs + [SIG_FIELD],
                               profile="deep"))
    return out


# 容器里所有 "结构边界" 偏移 (用于穷尽式连续区间扫描)
BOUNDARIES = [0x000, 0x040, 0x200, 0x20C, 0x220, 0x240, 0x260, 0x2A0, 0x2BC,
              0x2C4, 0x2E0, 0x2EC, 0x1400, 0x142C, -512, EOF]


def _exhaustive_msgs():
    """穷尽式扫描: 由结构边界两两组成的**所有**连续区间, 每个区间再叠加
    {原样, 签名区清零, 签名区移除} 三种处理。

    这是对 "签名覆盖哪个连续字节区间" 的一次穷尽搜索 (在结构边界粒度上),
    比人工挑选的范围列表强得多。
    """
    out = []
    bnd = []
    for b in BOUNDARIES:
        bnd.append(b)
    for i in range(len(bnd)):
        for j in range(len(bnd)):
            a, b = bnd[i], bnd[j]
            if a is EOF or b is EOF:
                continue
            if not (isinstance(a, int) and isinstance(b, int)):
                continue
            if a < 0 or b < 0:
                continue
            if b <= a:
                continue
            name = f"[0x{a:X}:0x{b:X}]"
            segs = [(a, b)]
            covers_sig = a < SIG_FIELD[1] and b > SIG_FIELD[0]
            out.append(Msg(name, segs, profile="exh"))
            if covers_sig:
                out.append(Msg(name + " 签名清零", segs, zero=[SIG_FIELD],
                               profile="exh"))
                out.append(Msg(name + " 签名移除",
                               [(a, SIG_FIELD[0]), (SIG_FIELD[1], b)], profile="exh"))
    # 结尾为文件尾/尾块前的区间
    for a in BOUNDARIES[:-1]:
        if not isinstance(a, int) or a < 0:
            continue
        for b in (-512, EOF):
            if b is EOF and a == 0:
                continue
            name = f"[0x{a:X}:{'EOF' if b is EOF else 'L-512'}]"
            out.append(Msg(name, [(a, b)], profile="exh"))
            if a < SIG_FIELD[1]:
                out.append(Msg(name + " 签名清零", [(a, b)], zero=[SIG_FIELD],
                               profile="exh"))
                out.append(Msg(name + " 签名移除", [(a, SIG_FIELD[0]),
                                                    (SIG_FIELD[1], b)], profile="exh"))
    return out


# --------------------------------------------------------------------------
# 五、哈希 / 编码候选
# --------------------------------------------------------------------------

HASHES = {
    "sha256":         lambda b: hashlib.sha256(b).digest(),
    "sha256d":        lambda b: hashlib.sha256(hashlib.sha256(b).digest()).digest(),
    "sha384_trunc32": lambda b: hashlib.sha384(b).digest()[:32],
    "sha512_trunc32": lambda b: hashlib.sha512(b).digest()[:32],
    "sha384_full":    lambda b: hashlib.sha384(b).digest(),
    "sha512_full":    lambda b: hashlib.sha512(b).digest(),
    "sha1":           lambda b: hashlib.sha1(b).digest(),
    "sha224":         lambda b: hashlib.sha224(b).digest(),
    "_raw":           lambda b: bytes(b),          # 仅用于 direct 型 (字节即摘要)
}
EXTRA_HASHES = {}
for _n, _c in (("sha3_256", "sha3_256"), ("blake2s", "blake2s"),
               ("sha512_256", "sha512_256"), ("sm3", "sm3")):
    try:
        hashlib.new(_c)
        EXTRA_HASHES[_n] = (lambda c: (lambda b: hashlib.new(c, b).digest()))(_c)
    except Exception:
        pass
# BLAKE2b 输出 32 字节
try:
    EXTRA_HASHES["blake2b32"] = lambda b: hashlib.blake2b(b, digest_size=32).digest()
except Exception:
    pass

SIG_FORMATS = [
    ("BE r||s", lambda b: b),
    ("LE r||s", lambda b: b[0:32][::-1] + b[32:64][::-1]),
    ("BE s||r", lambda b: b[32:64] + b[0:32]),
    ("LE s||r", lambda b: b[32:64][::-1] + b[0:32][::-1]),
]

# 哈希集: core 用任务指定的 8 种; extended 用 6 种 (含 sha3/blake2), 控制算力
CORE_HASHNAMES = ["sha256", "sha256d", "sha384_trunc32", "sha512_trunc32",
                  "sha384_full", "sha512_full", "sha1", "sha224"]
EXTENDED_HASHNAMES = ["sha256", "sha256d", "sha384_trunc32", "sha512_trunc32",
                      "sha3_256", "blake2s"]
DEEP_HASHNAMES = ["sha256", "sha256d", "sha384_trunc32", "sha512_trunc32"]
EXH_HASHNAMES = ["sha256", "sha256d", "sha384_trunc32", "sha512_trunc32"]
DIRECT_HASHNAMES = ["_raw", "sha256", "sha256d", "sha384_trunc32", "sha512_trunc32"]


WIDE = False          # --wide-hashes: 对所有消息族都使用全部 11 种哈希


def hashnames_for(msg, profile):
    if WIDE:
        return DIRECT_HASHNAMES if msg.direct is not None else \
            CORE_HASHNAMES + list(EXTRA_HASHES.keys())
    if msg.direct is not None:
        return DIRECT_HASHNAMES
    if msg.profile in ("deep", "exh"):
        return DEEP_HASHNAMES
    if msg.profile == "core":
        return CORE_HASHNAMES + (list(EXTRA_HASHES.keys()) if profile == "all" else [])
    return EXTENDED_HASHNAMES


def all_digests(msg_bytes: bytes, hashnames):
    return {h: HASHES[h](msg_bytes) if h in HASHES else EXTRA_HASHES[h](msg_bytes)
            for h in hashnames}


# --------------------------------------------------------------------------
# 六、主流程
# --------------------------------------------------------------------------

def discover_default(root: str):
    cand = [os.path.join(root, "02_固件二进制", "DC-S5", "S5___V29.bin")]
    for v in ("V24", "V23", "V20", "V11"):
        cand.append(os.path.join(root, "02_固件二进制", "DC-S5_版本历史", f"S5___{v}.bin"))
    return [c for c in cand if os.path.isfile(c)]


def label_of(path):
    return os.path.basename(path).replace("S5___", "").replace(".bin", "")


def direct_bytes(buf, spec):
    """direct 型候选 -> 摘要字节。"""
    kind, arg = spec
    L = len(buf)
    if kind == "pt_digest":
        off = PART_TABLE[0] + arg * PART_ENTRY + PART_DIGEST_OFF
        return bytes(buf[off:off + 32])
    if kind == "pt_digest_cat":
        n = int.from_bytes(buf[0x2E8:0x2EC], "little")
        n = 48 if not (0 < n < 4096) else n
        cat = b"".join(bytes(buf[PART_TABLE[0] + i * PART_ENTRY + PART_DIGEST_OFF:
                                  PART_TABLE[0] + i * PART_ENTRY + PART_DIGEST_OFF + 32])
                       for i in range(n))
        return hashlib.sha256(cat).digest()
    if kind == "pt_digest_cat_raw":
        n = int.from_bytes(buf[0x2E8:0x2EC], "little")
        n = 48 if not (0 < n < 4096) else n
        return (b"".join(bytes(buf[PART_TABLE[0] + i * PART_ENTRY + PART_DIGEST_OFF:
                                    PART_TABLE[0] + i * PART_ENTRY + PART_DIGEST_OFF + 32])
                         for i in range(n)))[:32]
    if kind == "raw_len_prefix":
        return int(L).to_bytes(8, "little") + bytes(buf[SIG_FIELD[0] + 64:SIG_FIELD[0] + 96])
    raise ValueError(kind)


def build_message(buf, msg: Msg):
    if msg.direct is not None:
        return direct_bytes(buf, msg.direct)
    return bytes(msg.build(buf))


def run(paths, msgs, profile, curves, verbose=True):
    """对每个消息候选 x 哈希 x 编码 x 曲线 做恢复, 求跨固件交集。"""
    bufs = {}
    results = []
    stats = {"msgs": 0, "combos": 0, "msg_empty": 0, "bytes_hashed": 0}
    shape = {}

    for mi, msg in enumerate(msgs):
        hnames = hashnames_for(msg, profile)
        # 1) 构造消息 + 摘要 (每个固件一次)
        per_file = {}
        ok = True
        for p in paths:
            if p not in bufs:
                with open(p, "rb") as fh:
                    bufs[p] = fh.read()
            try:
                mb = build_message(bufs[p], msg)
            except Exception:
                ok = False
                break
            if len(mb) < 16:
                ok = False
                break
            per_file[p] = all_digests(mb, hnames)
            stats["bytes_hashed"] += len(mb) * len(hnames)
        if not ok:
            stats["msg_empty"] += 1
            continue
        stats["msgs"] += 1
        shape[msg.name] = [len(build_message(bufs[p], msg)) for p in paths]

        # 2) 逐 (曲线, 哈希, 编码) 求交集
        sigs = {}
        for p in paths:
            with open(p, "rb") as fh:
                fh.seek(SIG_FIELD[0])
                sigs[p] = fh.read(64)

        for cname, curve in curves:
            for hname in hnames:
                for fname00, fmt in SIG_FORMATS:
                    stats["combos"] += 1
                    inter = None
                    for p in paths:
                        blob = fmt(sigs[p])
                        dig = per_file[p][hname]
                        if curve is None:                    # 内置纯 P-256
                            r = int.from_bytes(blob[0:32], "big")
                            s = int.from_bytes(blob[32:64], "big")
                            keys = pure_recover(r, s, int.from_bytes(dig[:32], "big"))
                        else:
                            keys = lib_recover(blob, dig, curve)
                        sset = set(keys)
                        inter = sset if inter is None else (inter & sset)
                        if not inter:
                            break
                    if inter:
                        for k in sorted(inter):
                            results.append({
                                "msg": msg.name, "hash": hname, "sig_format": fname00,
                                "curve": cname, "pubkey": k.hex(),
                                "msg_len_ref": shape[msg.name][-1],
                            })
        if verbose and (mi + 1) % 10 == 0:
            print(f"    ... {mi+1}/{len(msgs)} 消息候选, 累计组合 {stats['combos']}, "
                  f"已哈希 {stats['bytes_hashed']/1e9:.1f} GB", flush=True)
    return results, stats, shape


def verify_all(paths, results):
    out = []
    msgmap = {m.name: m for m in (_core_msgs() + _extended_msgs())}
    for res in results:
        msg = msgmap[res["msg"]]
        comp = bytes.fromhex(res["pubkey"])
        per, allok = {}, True
        for p in paths:
            with open(p, "rb") as fh:
                buf = fh.read()
                fh.seek(SIG_FIELD[0])
                raw64 = fh.read(64)
            blob = dict(SIG_FORMATS)[res["sig_format"]](raw64)
            if msg.direct is not None:
                dig = direct_bytes(buf, msg.direct)
            else:
                dig = all_digests(build_message(buf, msg), [res["hash"]])[res["hash"]]
            r = int.from_bytes(blob[0:32], "big")
            s = int.from_bytes(blob[32:64], "big")
            e = int.from_bytes(dig[:32], "big")
            okp = pure_verify(comp, r, s, e) if res["curve"] == "NIST256p" else None
            okl = None
            if HAVE_ECDSA:
                try:
                    curve = dict((n, c) for n, c in CURVES)[res["curve"]]
                    vk = VerifyingKey.from_string(comp, curve=curve)
                    vk.verify_digest(blob, dig, sigdecode=sigdecode_string)
                    okl = True
                except Exception:
                    okl = False
            per[label_of(p)] = {"pure_python_verify": okp, "python_ecdsa_verify": okl}
            if okp is False or okl is False:
                allok = False
        out.append({**res, "verify_per_firmware": per, "all_verified": allok})
    return out


def uncompressed_of(comp):
    if len(comp) == 65:
        return comp.hex()
    q = decompress_point(comp)
    if q is None:
        return "(非 P-256 压缩点)"
    return "04" + q[0].to_bytes(32, "big").hex() + q[1].to_bytes(32, "big").hex()


def direct_digest_probe(paths, msgs, verbose=True):
    """[4] 直接摘要相等性检验。

    0x220-0x260 未必是签名 —— 也可能是**存放的摘要**(例如 SHA-512 正好 64 字节,
    或两个 SHA-256)。这类假设可以被直接证伪/证实, 不需要公钥:
        比较 sig[0:32] / sig[32:64] / sig[0:64] 与 各种 (范围, 哈希) 的计算结果。
    """
    print("\n" + "=" * 78)
    print("[4] 直接摘要相等性检验 (64B 区是否就是存放的摘要?)")
    print("=" * 78)
    bufs = {}
    for p in paths:
        with open(p, "rb") as fh:
            bufs[p] = fh.read()
    hashnames = CORE_HASHNAMES + list(EXTRA_HASHES.keys())
    hits = []
    for msg in msgs:
        for p in paths:
            try:
                mb = build_message(bufs[p], msg)
            except Exception:
                continue
            if len(mb) < 16:
                continue
            digs = all_digests(mb, hashnames)
            with open(p, "rb") as fh:
                fh.seek(SIG_FIELD[0])
                blk = fh.read(64)
            for h, d in digs.items():
                targets = {
                    "sig[0:32]": blk[0:32], "sig[32:64]": blk[32:64],
                    "sig64": blk if len(d) == 64 else None,
                }
                for tn, tv in targets.items():
                    if tv is None:
                        continue
                    if d == tv:
                        hits.append((msg.name, h, tn, "直序", EC_label(p)))
                    elif d[::-1] == tv:
                        hits.append((msg.name, h, tn, "逆序", EC_label(p)))
    if hits:
        for h in hits[:80]:
            print(f"  *** 命中 ***  {h}")
        print(f"  共 {len(hits)} 条命中")
    else:
        print("  没有任何 (范围, 哈希) 的计算结果等于 0x220-0x260 的任一半或其逆序。")
        print("  => '该 64B 是明文存放的摘要' 这一族假设被排除 (SHA-512 64B 全长亦已检验)。")
    return hits


def coverage_chain_facts(paths):
    """[5] 覆盖链事实核验 —— 与签名方案无关的、可数学确证的事实。

    只依赖 CRC32 (无密钥) 与头部复制关系, 因此结论是 "数学上确证" 级别, 不依赖
    ECDSA/RSA 的任何假设。
    """
    import zlib
    print("\n" + "=" * 78)
    print("[5] 覆盖链事实核验 (与签名方案无关, 可确证)")
    print("=" * 78)
    rows = []
    for p in paths:
        with open(p, "rb") as fh:
            d = fh.read()
        L = len(d)
        crc_stored = int.from_bytes(d[0x40:0x44], "little")
        crc_calc = zlib.crc32(d[0x200:]) & 0xFFFFFFFF
        inner_eq_outer = bytes(d[0x2A0:0x2E0]) == bytes(d[0:0x40])
        lenfield = int.from_bytes(d[0x3C:0x40], "little")
        rows.append((label_of(p), L, crc_stored == crc_calc, inner_eq_outer,
                     lenfield == L - 0x200))
    print("  版本  | 文件长   | CRC32==crc32(data[0x200:]) | 内层头==外层头[0:0x40] | 0x3C==L-0x200")
    for r in rows:
        print(f"  {r[0]:>4}  | 0x{r[1]:08X} | {str(r[2]):<25} | {str(r[3]):<21} | {r[4]}")
    allcrc = all(r[2] for r in rows)
    allhdr = all(r[3] for r in rows)
    print(f"\n  * CRC32 覆盖 = [0x200, EOF) 且与内层头复制关系: "
          f"CRC全部吻合={allcrc}, 头部复制全部一致={allhdr}")
    print("  * 由此**可确证**的覆盖关系 (无需任何签名假设):")
    fields = [("外层 0x1C 机型/版本 id", 0x1C, 0x20),
              ("外层 0x24 BCD 时间戳", 0x24, 0x28),
              ("内层 0x2BC 机型/版本 id 副本", 0x2BC, 0x2C0),
              ("内层 0x2C4 时间戳副本", 0x2C4, 0x2C8),
              ("外层 0x40 CRC32", 0x40, 0x44),
              ("签名区 0x220-0x260", 0x220, 0x260),
              ("RSA 尾块 L-512..L", -512, 0)]
    for name, a, b in fields:
        in_crc = (a >= 0x200) if a >= 0 else True       # 负偏移单独处理
        if a < 0:
            in_crc = True                                # 尾块在 [0x200,EOF) 内
            rng = f"[L-512, L)"
        else:
            rng = f"[0x{a:X}, 0x{b:X})"
        print(f"      {name:<28} {rng:<22} 在 CRC32 覆盖内: {in_crc}")
    print("\n  * 关键推论: 外层 0x1C / 0x24 位于 [0x0,0x200), **不在 CRC32 覆盖内**;")
    print("    它们的副本 0x2BC / 0x2C4 位于 [0x200,EOF), **在 CRC32 覆盖内**。")
    print("    因此 '改版本字段会不会被检出' 完全取决于 [0x0,0x200) 是否被某个**带密钥**")
    print("    的签名覆盖 —— 这一步无法用离线数学确证 (见 [2]/[4] 的排除结果)。")
    return rows


def EC_label(p):
    return os.path.basename(p).replace("S5___", "").replace(".bin", "")


def inspect_layout(paths):
    print("=" * 78)
    print("[1] 签名布局实测 (0x200-0x300)")
    print("=" * 78)
    info = {}
    for p in paths:
        with open(p, "rb") as fh:
            head = fh.read(0x300)
        info[p] = {"len": os.path.getsize(p), "sig64": head[0x220:0x260]}
        print(f"\n  {label_of(p)}  ({os.path.basename(p)}, {info[p]['len']} B = 0x{info[p]['len']:X})")
        for off in range(0x200, 0x300, 16):
            tag = {0x220: "  <- r 起始", 0x240: "  <- s 起始",
                   0x260: "  <- 64B 签名区结束"}.get(off, "")
            print(f"    0x{off:03X}  {head[off:off+16].hex(' ')}{tag}")
    return info


def layout_verdict(info):
    print("\n" + "-" * 78)
    print("[1b] 布局判定")
    print("-" * 78)
    uniq = len(set(v["sig64"] for v in info.values()))
    print(f"  * 0x220-0x260 在 {len(info)} 个固件中互不相同的取值有 {uniq} 个 "
          f"=> {'全部互异 (高熵逐版本数据)' if uniq == len(info) else '存在重复!'}")
    for p, v in info.items():
        s = v["sig64"]
        print(f"      {label_of(p):>4}: 非零字节 {sum(1 for b in s if b)}/64")
    print("  * (r,s) 作为大端标量落在 [1, P-256 n-1] 内:")
    for p, v in info.items():
        s = v["sig64"]
        r = int.from_bytes(s[0:32], "big"); ss = int.from_bytes(s[32:64], "big")
        print(f"      {label_of(p):>4}: r<n={r < P256_N} s<n={ss < P256_N} "
              f"r!=0={r != 0} s!=0={ss != 0}")
    print("      注意: 随机 256-bit 值 < n 的概率 ≈ 1-2^-32, 所以 '5/5 合法' 几乎无信息量,")
    print("            不构成 P-256 的证据 (项目文档 E 系列中此推论偏强)。")
    # Ed25519 排他性检验
    L_ed = 2 ** 252 + 27742317777372353535851937790883648493
    p_ed = 2 ** 255 - 19
    cnt_s = 0
    cnt_r = 0
    for v in info.values():
        blk = v["sig64"]
        if int.from_bytes(blk[32:64], "little") < L_ed:
            cnt_s += 1
        y = int.from_bytes(blk[0:32], "little") & ((1 << 255) - 1)
        if y < p_ed:
            cnt_r += 1
    print(f"  * Ed25519 (同为 64B 签名 R||S, 小端) 排他性检验: S<L 的有 {cnt_s}/{len(info)}"
          f" (随机期望 1/16), R 可解码的有 {cnt_r}/{len(info)}")
    print("      => " + ("不支持 Ed25519 (S<L 比例与随机一致)"
                         if cnt_s <= max(1, len(info) // 8) else "需进一步考察 Ed25519"))
    return uniq == len(info)


def report(results, stats, paths):
    print("\n" + "=" * 78)
    print("[3] 签名覆盖范围裁决")
    print("=" * 78)
    print(f"  已试消息候选 {stats['msgs']} 个 (空/非法跳过 {stats['msg_empty']}), "
          f"总组合 {stats['combos']} 个, 曲线 {len(CURVES)} 条")
    if not results:
        print("  未找到任何跨固件收敛的公钥。")
        print("  => 真实签名覆盖范围/哈希/曲线落在本次候选空间之外 (见 结论.md 的已排除清单)。")
        return
    seen = set()
    for r in results:
        key = (r["msg"], r["hash"], r["sig_format"], r["curve"])
        if key in seen:
            continue
        seen.add(key)
        print(f"\n  *** 收敛 ***  消息={r['msg']}  哈希={r['hash']}  "
              f"编码={r['sig_format']}  曲线={r['curve']}")
        print(f"      公钥(压缩)  : {r['pubkey']}")
        print(f"      公钥(未压缩): {uncompressed_of(bytes.fromhex(r['pubkey']))}")
        print(f"      5 版独立验签 : {'全部通过' if r['all_verified'] else '存在失败'}")
        for k, v in r["verify_per_firmware"].items():
            print(f"         {k:>4}: pure={v['pure_python_verify']} lib={v['python_ecdsa_verify']}")
    print("\n  对版本字段的覆盖关系 (按每一条收敛组合):")
    for r in results:
        print(f"    - {r['msg']}: 见脚本 JSON 中的消息定义")


def main(argv=None):
    ap = argparse.ArgumentParser(
        description="DC-S5 UPD 容器 ECDSA 公钥恢复 / 覆盖范围判定 (纯离线)")
    ap.add_argument("firmware", nargs="*", help="固件路径 (可多个); 省略则用 --root 自动发现")
    ap.add_argument("--root", default=os.getcwd(), help="项目根目录 (自动发现固件)")
    ap.add_argument("--profile", choices=["none", "core", "extended", "all"], default="all",
                    help="候选空间: core=任务指定集合, extended=扩充集合, all=全部")
    ap.add_argument("--deep", action="store_true",
                    help="追加深度候选: 头部可变字段全部子集清零 (慢, 约 +10 分钟)")
    ap.add_argument("--exhaustive", action="store_true",
                    help="追加穷尽候选: 所有结构边界两两组成的连续区间 (推荐)")
    ap.add_argument("--json", default=None, help="结果写入 JSON")
    ap.add_argument("--mode", choices=["recover", "probe", "both"], default="both",
                    help="recover=公钥恢复穷举; probe=直接摘要相等性检验")
    ap.add_argument("--wide-hashes", action="store_true",
                    help="所有消息族都用全部 11 种哈希 (更彻底, 更慢)")
    ap.add_argument("--quiet", action="store_true")
    args = ap.parse_args(argv)

    global WIDE
    WIDE = bool(args.wide_hashes)
    paths = [os.path.abspath(p) for p in (args.firmware or discover_default(args.root))]
    missing = [p for p in paths if not os.path.isfile(p)]
    if missing:
        print("固件不存在: " + ", ".join(missing), file=sys.stderr)
        return 2
    if len(paths) < 2:
        print("警告: 少于 2 个固件, 无法做跨版本收敛判定。", file=sys.stderr)

    msgs = []
    if args.profile in ("core", "all"):
        msgs += _core_msgs()
    if args.profile in ("extended", "all"):
        msgs += _extended_msgs()
    if args.deep:
        msgs += _deep_msgs()
    if args.exhaustive:
        msgs += _exhaustive_msgs()

    print(f"参与固件 ({len(paths)}):")
    for p in paths:
        print(f"   - {p}  ({os.path.getsize(p)} B)")
    print(f"python-ecdsa 可用: {HAVE_ECDSA};  曲线候选: {[c[0] for c in CURVES]}")
    print(f"候选空间: {len(msgs)} 条消息 x (每种哈希集) x "
          f"{len(SIG_FORMATS)} 种编码 x {len(CURVES)} 条曲线")

    info = inspect_layout(paths)
    hi = layout_verdict(info)

    print("\n" + "=" * 78)
    print("[2] 公钥恢复穷举")
    print("=" * 78)
    probe_hits = []
    if args.mode in ("recover", "both"):
        results, stats, shape = run(paths, msgs, args.profile, CURVES,
                                    verbose=not args.quiet)
        if results:
            results = verify_all(paths, results)
        report(results, stats, paths)
    else:
        results, stats, shape = [], {"msgs": 0, "combos": 0, "msg_empty": 0,
                                     "bytes_hashed": 0}, {}
    if args.mode in ("probe", "both"):
        probe_hits = direct_digest_probe(paths, msgs, verbose=not args.quiet)
    chain_rows = coverage_chain_facts(paths)

    payload = {
        "firmware": paths,
        "firmware_len": {label_of(p): os.path.getsize(p) for p in paths},
        "python_ecdsa_available": HAVE_ECDSA,
        "curves": [c[0] for c in CURVES],
        "hash_sets": {"core": CORE_HASHNAMES, "extended": EXTENDED_HASHNAMES,
                      "direct": DIRECT_HASHNAMES,
                      "extra_available": list(EXTRA_HASHES.keys())},
        "profile": args.profile,
        "signature_field": list(SIG_FIELD),
        "stats": stats,
        "msg_len_shape": shape,
        "msg_catalog": [{"name": m.name, "profile": m.profile,
                         "segs": [[a, ("EOF" if b is EOF else b)] for a, b in m.segs],
                         "zero": [list(z) for z in m.zero],
                         "direct": (None if m.direct is None else [m.direct[0],
                                                                   m.direct[1]])}
                        for m in msgs],
        "signature_region_distinct": hi,
        "converged": results,
        "direct_digest_probe_hits": probe_hits,
    }
    if args.json:
        with open(args.json, "w") as fh:
            json.dump(payload, fh, indent=2, ensure_ascii=False)
        print(f"\n  JSON 结果已写入 {args.json}")
    return 0 if results else 1


if __name__ == "__main__":
    sys.exit(main())
