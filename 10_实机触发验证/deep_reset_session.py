#!/usr/bin/env python3
"""
deep_reset_session.py —— 深度会话重置（核清理版），2026-10-16。

依据：
  · safe_handshake.py 头注：相机 accctrl 只有一个"待批复"槽；未清理的 req_acc 留下
    陈旧 pending → 后续 req_acc 撞上 → 会话污染 → invalid login / err_critical。
  · 04:34 v1 fuzzer 会话用了【每轮随机 UUID + 匿名 req_acc】，陈旧 pending 可能挂在
    我们不知道 UUID 的条目下 ⇒ 同 UUID 的 req_acc_can 清不掉（已在窗口 1 实证：
    清后 getstate 仍 err_critical）。
  · 权威文档 §4-1 #2：req_acc_can 用【空 UUID】会清空授权状态（更强清理）；
    gate_probe.py:64 历史上就用过无 value 的 req_acc_can。

流程（每个新 SoftAP 窗口内一气呵成）：
  A. 等相机上线
  B. req_acc_can value=空（核清理，仅一次）
  C. req_acc 官方 UUID（仅一次）
  D. camcmd playmode
  E. 快轮询 getstate
  F. dlna 放行检查 → 成功则 exec repro_crash.py

红线：B/C 各一次；相机一掉线立即停手等下一窗口；最多 rounds 轮。
用法：python3 -u deep_reset_session.py <cam_ip> [--wait-s 600] [--rounds 4] [--skip-nuke]
"""
import sys
import os
import time
import socket
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_dlna import auth_status

ACC_UUID = "4D454930-0100-1000-8001-020A0003BD13"
DEV_NAME = "LUMIX Sync"
UA = {"User-Agent": "LUMIX Sync", "Accept-Charset": "UTF-8"}


def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)


def get(cam, query, timeout=6):
    url = f"http://{cam}/cam.cgi?{query}"
    try:
        with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
            return r.read().decode("utf-8", "replace").strip()
    except Exception as e:
        return f"__ERR__ {e}"


def short(st):
    import re
    m = re.search(r"<result>([^<]*)</result>", st)
    if m:
        return m.group(1)
    return st[:60]


def tcp80(cam, timeout=3):
    s = socket.socket()
    s.settimeout(timeout)
    try:
        s.connect((cam, 80))
        return True
    except OSError:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def wait_online(cam, wait_s):
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if tcp80(cam):
            return True
        time.sleep(5)
    return False


def grab(cam, do_nuke):
    log("== 窗口开始 ==")
    log(f"  初始 getstate: {short(get(cam, 'mode=getstate'))}")

    if do_nuke:
        r = get(cam, urllib.parse.urlencode(
            {"mode": "accctrl", "type": "req_acc_can", "value": "", "value2": ""}))
        log(f"  B. 核清理 req_acc_can(空值, 仅一次): {short(r)}")
        time.sleep(2)
        log(f"     清后 getstate: {short(get(cam, 'mode=getstate'))}")

    r = get(cam, urllib.parse.urlencode(
        {"mode": "accctrl", "type": "req_acc", "value": ACC_UUID, "value2": DEV_NAME}))
    log(f"  C. req_acc(官方UUID, 仅一次): {r[:100]}")

    r = get(cam, "mode=camcmd&value=playmode")
    log(f"  D. camcmd playmode: {short(r)}")

    ok = False
    for i in range(30):
        time.sleep(1.5)
        st = get(cam, "mode=getstate", timeout=5)
        code = short(st)
        if i % 3 == 0 or code == "ok":
            log(f"  E. [{(i+1)*1.5:.0f}s] getstate: {code}")
        if code == "ok":
            ok = True
            break
        if st.startswith("__ERR__"):
            log(f"  相机掉线（{st}）——本窗口中止（不重发 req_acc）")
            return False
    if not ok:
        log("  getstate 未达 ok")
        return False

    log("  F. dlna 放行检查...")
    for i in range(10):
        a, d = auth_status(cam)
        log(f"     dlna: {a} ({d})")
        if a == "ok":
            log("  ✅ 会话可用！")
            return True
        time.sleep(2)
    log("  getstate=ok 但 dlna 未放行")
    return False


def main():
    cam = sys.argv[1] if len(sys.argv) > 1 else "192.168.54.1"
    wait_s, rounds, do_nuke = 600, 4, True
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--wait-s":
            wait_s = int(args[i + 1]); i += 2
        elif args[i] == "--rounds":
            rounds = int(args[i + 1]); i += 2
        elif args[i] == "--skip-nuke":
            do_nuke = False; i += 1
        else:
            i += 1

    log(f"目标 {cam}  轮数 {rounds}  核清理={do_nuke}")
    for rnd in range(rounds):
        log(f"\n########## 第 {rnd+1}/{rounds} 轮 ##########")
        if not wait_online(cam, wait_s):
            log(f"  等待 {wait_s}s 相机仍未上线，本轮放弃")
            continue
        log("  相机上线")
        if grab(cam, do_nuke):
            log("\n★★★ 会话建立成功，开始受控复现 crash 001 ★★★")
            os.execv(sys.executable, [sys.executable,
                      os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "repro_crash.py"), cam, "--rounds", "3"])
        log("  本窗口失败，等相机掉线进下一窗口（最多 10 分钟）...")
        t0 = time.time()
        while time.time() - t0 < 600:
            if not tcp80(cam):
                break
            time.sleep(5)
    log("\n全部轮次失败。建议：相机接 AC；或在相机上退出等待画面重新进入；或断电 30s 冷启动。")
    sys.exit(2)


if __name__ == "__main__":
    main()
