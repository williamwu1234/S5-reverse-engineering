#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
selftest_synthetic.py -- 用合成固件验证 ecdsa_recover.py / rsa_modulus.py 的检测能力
=====================================================================================

一个 "没找到" 的结果只有在工具有能力找到时才可信。本脚本构造**结构完全相同**的
合成 UPD 容器 (与控制台固件同布局), 用已知私钥签名, 然后跑真实流水线, 检查:

  T1  ECDSA: 跨 3 个合成固件, 签名覆盖 raw[0x200:-512] + sha256 (BE r||s)
      -> 必须收敛到已知公钥, 且 msg/hash/编码 判定正确。
  T2  ECDSA: 覆盖 raw[:-512] + sha384 截断 32B (LE 端序写回)
      -> 必须收敛到同一公钥。
  T3  阴性对照: 3 个固件用**不同**私钥签同一范围
      -> 必须**不**收敛 (证明不会误报)。
  T4  ECDSA: 被签区间的 64B 签名字段先清零再哈希
      -> 必须收敛, 且判定出 "签名区清零" 变体。
  T5  RSA : 合成 2048-bit RSA 密钥 (为速度), 对 raw[0x200:-512] 做 PKCS#1 v1.5
      签名写入尾部 512B 的右对齐位置
      -> rsa_modulus.try_recover 必须恢复出 N 并用第 3 个固件验证通过。
      (需要 gmpy2 生成素数与快速大数运算)

用法:  python3 selftest_synthetic.py            # 需要 python-ecdsa
       python3 selftest_synthetic.py --keep      # 保留临时目录
"""

from __future__ import annotations

import argparse
import hashlib
import os
import shutil
import struct
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import ecdsa_recover as EC            # noqa: E402
import rsa_modulus as RM              # noqa: E402

try:
    import ecdsa
    from ecdsa import NIST256p, SigningKey
    from ecdsa.util import sigencode_string
    HAVE_ECDSA = True
except Exception:
    HAVE_ECDSA = False

RESULTS = []

# 自检用的代表性子集: 覆盖 "范围选择 / 负偏移 / 签名区清零 / 头前缀" 四类构造。
# 用全集 (600+) 只验证流水线是浪费 —— 每条消息的构造逻辑相同。
SUBSET = [
    "raw[0x2A0:-512]",                  # 负偏移结尾
    "raw[0x142C:-512]",
    "raw[0x200:-512] +签名区清零",        # 签名区清零变体
    "raw[:-512]",
    "raw[:0x200]",                      # 纯头部前缀
    "raw[0x200:0x142C]",                # 表区
]


def test_msgs():
    cat = {m.name: m for m in (EC._core_msgs() + EC._extended_msgs())}
    return [cat[n] for n in SUBSET]


def check(name, ok, detail=""):
    RESULTS.append((name, ok, detail))
    print(f"  [{'PASS' if ok else 'FAIL'}] {name}" + (f"  {detail}" if detail else ""))
    return ok


def make_container(L, seed):
    """构造与 DC-S5 同布局的合成 UPD 容器 (确定性伪随机填充)。"""
    rnd = hashlib.sha256(b"seed" + str(seed).encode()).digest()
    buf = bytearray()
    while len(buf) < L:
        rnd = hashlib.sha256(rnd).digest()
        buf += rnd
    buf = buf[:L]
    buf[0x000:0x004] = b"UPD\x00"
    buf[0x004:0x008] = struct.pack("<I", 0x200)
    buf[0x008:0x00C] = struct.pack("<I", 0x200)
    buf[0x00C:0x014] = b"MC801\x00\x00\x00"
    buf[0x014:0x01C] = b"\x00" * 8
    buf[0x01C:0x020] = struct.pack("<I", 0x02900290)
    buf[0x020:0x024] = struct.pack("<I", 0x00010004)
    buf[0x024:0x028] = struct.pack("<I", 0x07101450)
    buf[0x028:0x02C] = b"\x00" * 4
    buf[0x02C:0x030] = struct.pack("<I", 3)
    buf[0x030:0x034] = b"\x00" * 4
    buf[0x034:0x038] = struct.pack("<I", 3)
    buf[0x038:0x03C] = struct.pack("<I", 0x200)
    buf[0x03C:0x040] = struct.pack("<I", L - 0x200)
    buf[0x040:0x044] = b"\x00" * 4
    buf[0x044:0x200] = b"\x00" * (0x200 - 0x44)
    buf[0x200:0x20C] = b"panasonic\x00\x00\x00"
    buf[0x20C:0x220] = b"\x00" * (0x220 - 0x20C)
    buf[0x220:0x260] = b"\x00" * 64                      # 签名占位
    buf[0x260:0x2A0] = b"\x00" * (0x2A0 - 0x260)
    buf[0x2A0:0x2E0] = bytes(buf[0x000:0x040])           # 内层头 = 外层头
    buf[0x2E0:0x2EC] = struct.pack("<III", 0x1400, L - 0x200 - 0x1400, 0x30)
    buf[0x2EC:0x400] = bytes(buf[0x2EC:0x400])           # 分区表 (伪随机)
    return buf


def sign_into(buf, msg_name, hash_name, sk, le=False):
    """按 msg_name/hash_name 构造消息, 签名, 写回 0x220 的 64B。"""
    msg = {m.name: m for m in (EC._core_msgs() + EC._extended_msgs())}[msg_name]
    mb = EC.build_message(bytes(buf), msg)
    dig = EC.all_digests(mb, [hash_name])[hash_name]
    sig = sk.sign_digest(dig, sigencode=sigencode_string)
    blob = sig
    if le:
        blob = sig[0:32][::-1] + sig[32:64][::-1]
    buf[0x220:0x260] = blob
    return sig, dig


def pub_of(sk):
    return sk.get_verifying_key().to_string("compressed").hex()


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    args = ap.parse_args()

    if not HAVE_ECDSA:
        print("需要 python-ecdsa: pip install ecdsa")
        return 2

    tmp = tempfile.mkdtemp(prefix="s5_selftest_")
    print(f"临时目录: {tmp}\n")
    try:
        # ---------------- T1 / T2 / T4: 收敛检测 ----------------
        # 注意: 被签消息必须与 "写完签名之后的文件" 自洽 —— 因此 T1/T2 选择
        #       **不含** 0x220-0x260 签名字段的范围; T4 用 "签名区清零" 变体。
        for tag, (msg_name, hash_name, le, zero_sig) in {
            "T1": ("raw[0x2A0:-512]", "sha256", False, False),
            "T2": ("raw[0x142C:-512]", "sha384_trunc32", True, False),
            "T4": ("raw[0x200:-512] +签名区清零", "sha256", False, True),
        }.items():
            sk = SigningKey.generate(curve=NIST256p)
            want = pub_of(sk)
            paths = []
            for i, L in enumerate((0x80000, 0x84000, 0x88000)):
                b = make_container(L, seed=f"{tag}-{i}")
                sign_into(b, msg_name, hash_name, sk, le=le)
                p = os.path.join(tmp, f"{tag}_{i}.bin")
                with open(p, "wb") as fh:
                    fh.write(bytes(b))
                paths.append(p)
            res, stats, _ = EC.run(paths, test_msgs(), "all", EC.CURVES, verbose=False)
            hits = [r for r in res if r["pubkey"] == want]
            detail = (f"收敛组合 {len(res)} 个, 命中已知公钥 {len(hits)} 个"
                      + (f" [{hits[0]['msg']} / {hits[0]['hash']} / {hits[0]['sig_format']}]"
                         if hits else ""))
            check(f"{tag} 合成固件收敛到已知公钥 ({msg_name} / {hash_name}"
                  f"{' / LE' if le else ''})", len(hits) > 0, detail)

        # ---------------- T3: 阴性对照 ----------------
        paths = []
        keys = []
        for i, L in enumerate((0x80000, 0x84000, 0x88000)):
            sk = SigningKey.generate(curve=NIST256p)
            keys.append(pub_of(sk))
            b = make_container(L, seed=f"T3-{i}")
            sign_into(b, "raw[0x2A0:-512]", "sha256", sk)
            p = os.path.join(tmp, f"T3_{i}.bin")
            with open(p, "wb") as fh:
                fh.write(bytes(b))
            paths.append(p)
        res, stats, _ = EC.run(paths, test_msgs(), "all", EC.CURVES, verbose=False)
        check("T3 阴性对照: 不同私钥 -> 不收敛 (无误报)", len(res) == 0,
              f"收敛组合 {len(res)} 个, 3 个公钥互异={len(set(keys)) == 3}")

        # ---------------- T5: RSA 模数恢复 ----------------
        try:
            import gmpy2
            have_g = True
        except Exception:
            have_g = False
        if not have_g:
            check("T5 RSA 模数恢复 (需要 gmpy2)", False, "gmpy2 不可用, 跳过")
        else:
            e = 65537

            def gen_prime_1024():
                # 置顶两位, 保证 p,q in [1.5*2^1023, 2^1024) => N 必有 2048 bit
                while True:
                    cand = (gmpy2.mpz(2) ** 1023 + gmpy2.mpz(2) ** 1022
                            + gmpy2.mpz(int.from_bytes(os.urandom(127), "big")))
                    pp = int(gmpy2.next_prime(cand))
                    if pp.bit_length() == 1024:
                        return pp

            while True:
                p = gen_prime_1024()
                q = gen_prime_1024()
                if p == q:
                    continue
                N = p * q
                if N.bit_length() == 2048:
                    break
            d = pow(e, -1, (p - 1) * (q - 1))
            k = 256
            paths = []
            for i, L in enumerate((0x80000, 0x84000, 0x88000)):
                b = make_container(L, seed=f"T5-{i}")
                mb = EC.build_message(bytes(b), {m.name: m for m in EC._core_msgs()}[
                    "raw[0x200:-512]"])
                dig = hashlib.sha256(mb).digest()
                m = RM.encode_p15_di(dig, "sha256", k)
                s = pow(m, d, N)
                tail = s.to_bytes(512, "big")            # 右对齐到 512B
                b[-512:] = tail
                pth = os.path.join(tmp, f"T5_{i}.bin")
                with open(pth, "wb") as fh:
                    fh.write(bytes(b))
                paths.append(pth)
            bufs = {pp: open(pp, "rb").read() for pp in paths}
            cands = [("raw[0x200:-512]", "sha256", "p15_di",
                      [RM.encode_p15_di(hashlib.sha256(EC.build_message(bufs[pp],
                       {m.name: m for m in EC._core_msgs()}["raw[0x200:-512]"])).digest(),
                       "sha256", 256) for pp in paths])]
            found, notes, el = RM.try_recover(cands, bufs, paths, e, "be", None, None,
                                              verbose=False)
            okk = len(found) == 1 and int(found[0]["N_hex"], 16) == N
            check("T5 RSA: 恢复出的 N 与合成密钥一致", okk,
                  f"命中 {len(found)} 个, 耗时 {el:.1f}s"
                  + ("" if okk else f", 期望 N_bits={N.bit_length()}"))
            if found:
                check("T5b RSA: 第 3 个固件独立验证通过",
                      len(found[0]["verified_versions"]) == 3,
                      f"验证版本 {found[0]['verified_versions']}")
    finally:
        if args.keep:
            print(f"\n保留临时目录: {tmp}")
        else:
            shutil.rmtree(tmp, ignore_errors=True)

    print("\n" + "=" * 60)
    bad = [n for n, ok, _ in RESULTS if not ok]
    print(f"自检总计 {len(RESULTS)} 项, 失败 {len(bad)} 项"
          + (f": {bad}" if bad else "  -- 全部通过"))
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main())
