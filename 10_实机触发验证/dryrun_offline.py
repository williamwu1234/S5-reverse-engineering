#!/usr/bin/env python3
"""
dryrun_offline.py —— 无相机全链路回归（mock_cam.py 驱动）

目的：把"必须有相机才能验证"的部分（握手 → 复现 crash 001 → 全策略 fuzz → 机型身份 fuzz）
搬到本地假相机上跑通，用于**证明工具链本身没有 bug**。
动机：14:52:34 那次会话完全可用，却因 repro_crash.py 的 `bytes.encode` bug 在第 1 个用例即崩
（见 repro_run2.log / pag_run2.log）—— 会话浪费掉。此类问题必须离线可复现。

跑 5 个阶段，逐条判定 PASS/FAIL：
  P1  握手链（handshake.py）           期望：getstate=ok 且 dlna 放行
  P2  复现链（repro_crash.py）         期望：INT32_MAX 用例被识别为 DLNA_DOWN 并落盘 crash_cases/
  P3  全策略 fuzz（fuzz_dlna.py）      期望：跑完且 JSONL 日志里出现 dlna 心跳条目
  P4  机型身份 fuzz（fuzz_model.py）   期望：跑完且生成差异表（DIFF 计数 >= 1）
  P5  静默即死复刻（--silence-403 25） 期望：技能保活（dlna_touch）下会话不被误杀

用法：python3 -u dryrun_offline.py [--keep]
输出：dryrun_<时间戳>/ 目录（各阶段日志 + 判定汇总），退出码 0=全 PASS。
"""
import argparse
import os
import re
import shutil
import socket
import subprocess
import sys
import time

HERE = os.path.dirname(os.path.abspath(__file__))
PY = sys.executable
HTTP_PORT = 18080
DLNA_PORT = 16066
IMG_PORT = 15001
CAM = "127.0.0.1"
ENV = dict(os.environ, S5_HTTP_PORT=str(HTTP_PORT), S5_DLNA_PORT=str(DLNA_PORT),
           S5_IMG_PORT=str(IMG_PORT), S5_DLNA_GAP="5")

RESULTS = []


def run(label, argv, outdir, timeout=180, expect_pattern=None, forbid_pattern=None):
    fn = os.path.join(outdir, label + ".log")
    t0 = time.time()
    try:
        p = subprocess.run(argv, cwd=HERE, env=ENV, capture_output=True, text=True, timeout=timeout)
        out = (p.stdout or "") + (p.stderr or "")
        rc = p.returncode
    except subprocess.TimeoutExpired as e:
        out = (e.stdout or "") + (e.stderr or "") + "\n[TIMEOUT]"
        rc = -9
    open(fn, "w").write(out)
    ok = True
    why = []
    if rc not in (0, 1, 3):          # 1/3 = 脚本自身的判定性退出（未授予/未恢复），不算工具崩
        ok = False; why.append("rc=%s" % rc)
    if "Traceback (most recent call last)" in out:
        ok = False; why.append("有 Python 异常")
    if expect_pattern and not re.search(expect_pattern, out):
        ok = False; why.append("缺少期望输出 /%s/" % expect_pattern)
    if forbid_pattern and re.search(forbid_pattern, out):
        ok = False; why.append("出现禁忌输出 /%s/" % forbid_pattern)
    print("  %-34s %-5s rc=%-3s %.1fs  %s" % (label, "PASS" if ok else "FAIL", rc,
                                              time.time() - t0, ";".join(why)))
    if not ok:
        print("      ---- 日志尾部 ----")
        for l in out.strip().splitlines()[-12:]:
            print("      " + l)
    RESULTS.append((label, ok, ";".join(why)))
    return rc, out


def wait_port(host, port, timeout=10):
    t0 = time.time()
    while time.time() - t0 < timeout:
        s = socket.socket(); s.settimeout(0.5)
        try:
            s.connect((host, port)); return True
        except OSError:
            time.sleep(0.2)
        finally:
            s.close()
    return False


def start_mock(outdir, extra, tag):
    logf = open(os.path.join(outdir, "mock_%s.log" % tag), "w")
    cmd = [PY, os.path.join(HERE, "mock_cam.py"),
           "--http-port", str(HTTP_PORT), "--dlna-port", str(DLNA_PORT),
           "--img-port", str(IMG_PORT)] + extra
    p = subprocess.Popen(cmd, cwd=HERE, stdout=logf, stderr=subprocess.STDOUT)
    if not wait_port(CAM, HTTP_PORT) or not wait_port(CAM, DLNA_PORT):
        print("  [!] mock 未起来")
    return p, logf


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--keep", action="store_true")
    a = ap.parse_args()

    outdir = "dryrun_%s" % time.strftime("%Y%m%d_%H%M%S")
    os.makedirs(outdir, exist_ok=True)
    print("[*] 离线全链路回归，产物目录 %s" % outdir)
    print("[*] 端口 cam=%d dlna=%d img=%d（环境变量对齐）" % (HTTP_PORT, DLNA_PORT, IMG_PORT))

    # ---------------- 阶段 1+2：正常靶机（INT32_MAX → dlna 进程死）
    mock, logf = start_mock(outdir, ["--crash-on-intmax"], "p12")
    try:
        print("\n== P1 握手链 ==")
        run("p1_handshake", [PY, "-u", "handshake.py", CAM], outdir,
            expect_pattern=r"getstate=ok|握手成功")
        print("\n== P2 复现链（注入 dlna 进程死）==")
        run("p2_repro", [PY, "-u", "repro_crash.py", CAM, "--rounds", "1"], outdir, timeout=300,
            expect_pattern=r"DLNA_DOWN|dlna_down|整机崩溃|dlna进程崩溃")
    finally:
        mock.terminate(); logf.close()
    # 校验 crash 落盘
    cds = [f for f in os.listdir(os.path.join(HERE, "crash_cases")) if f.startswith("dlna_down_")
           or f.startswith("d_")]
    print("  %-34s %-5s 落盘: %s" % ("p2_crashcase_saved", "PASS" if cds else "FAIL", cds))
    RESULTS.append(("p2_crashcase_saved", bool(cds), str(cds)))

    # ---------------- 阶段 3+4：正常靶机（纯只读 fuzz）
    mock, logf = start_mock(outdir, [], "p34")
    try:
        print("\n== P3 全策略 fuzz（限量）==")
        rc, out = run("p3_fuzz_all", [PY, "-u", "fuzz_dlna.py", CAM, "--strategy", "all",
                                      "--count", "60"], outdir, timeout=420,
                      expect_pattern=r"完成：共")
        logs = sorted([f for f in os.listdir(HERE) if f.startswith("fuzz_log_")])
        hb = False
        if logs:
            hb = "dlna_heartbeat" in open(os.path.join(HERE, logs[-1])).read()
        print("  %-34s %-5s 最新日志 %s 含心跳=%s"
              % ("p3_heartbeat_present", "PASS" if hb else "FAIL", logs[-1] if logs else "-", hb))
        RESULTS.append(("p3_heartbeat_present", hb, logs[-1] if logs else "-"))

        print("\n== P4 机型身份 fuzz ==")
        run("p4_model_fuzz", [PY, "-u", "fuzz_model.py", CAM, "--strategy", "all", "--diff"],
            outdir, timeout=420, expect_pattern=r"身份差异表已存")
        diffs = sorted([f for f in os.listdir(HERE) if f.startswith("model_diff_")])
        ndiff = 0
        if diffs:
            txt = open(os.path.join(HERE, diffs[-1])).read()
            ndiff = txt.count("DIFF")
        print("  %-34s %-5s %s DIFF=%d"
              % ("p4_diff_table", "PASS" if ndiff >= 1 else "FAIL", diffs[-1] if diffs else "-", ndiff))
        RESULTS.append(("p4_diff_table", ndiff >= 1, "DIFF=%d" % ndiff))
    finally:
        mock.terminate(); logf.close()

    # ---------------- 阶段 5：静默即死 + 心跳保活
    mock, logf = start_mock(outdir, ["--silence-403", "25"], "p5")
    try:
        print("\n== P5 静默即死复刻（保活必须生效）==")
        run("p5_handshake", [PY, "-u", "handshake.py", CAM], outdir, expect_pattern=r"dlna 放行")
        rc, out = run("p5_model_nodlna", [PY, "-u", "fuzz_model.py", CAM,
                                          "--strategy", "query"], outdir, timeout=300,
                      expect_pattern=r"完成 \d+ 个用例")
        killed = "保活异常" in out
        print("  %-34s %-5s 保活异常出现=%s（False 才是全对）"
              % ("p5_keepalive_protected", "PASS" if not killed else "FAIL", killed))
        RESULTS.append(("p5_keepalive_protected", not killed, "killed=%s" % killed))
    finally:
        mock.terminate(); logf.close()

    # ---------------- 汇总
    npass = sum(1 for _, ok, _ in RESULTS if ok)
    print("\n===== 汇总 %d/%d PASS =====" % (npass, len(RESULTS)))
    for label, ok, why in RESULTS:
        print("  [%s] %-34s %s" % ("PASS" if ok else "FAIL", label, why))
    open(os.path.join(outdir, "SUMMARY.txt"), "w").write(
        "\n".join("%s\t%s\t%s" % ("PASS" if ok else "FAIL", l, w) for l, ok, w in RESULTS) + "\n")
    print("    明细: %s/" % outdir)
    if not a.keep:
        print("    （--keep 可保留 mock 日志；本目录默认保留）")
    return 0 if npass == len(RESULTS) else 1


if __name__ == "__main__":
    sys.exit(main())
