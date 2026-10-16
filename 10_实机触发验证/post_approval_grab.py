#!/usr/bin/env python3
"""
post_approval_grab.py —— 用户已在相机上批准过配对（14:46:40 对话框点【允许】）后的窗口抢占。

与 deep_reset_session.py 的区别：
  · 优先路径：getstate 若一开始就是 ok（配对已持久化）→ 不发任何 accctrl，
    直接 playmode + dlna 检查 → 成功即 exec repro_crash.py
  · 兜底路径：getstate=err_critical → 核清理(空值 can, 一次) + req_acc(一次)，
    然后轮询；若 req_acc 回 ok_under_research（带消息）→ 提示用户再次批准
  · 红线不变：每窗口 req_acc 至多一次、can 至多一次、掉线立即停

用法：python3 -u post_approval_grab.py <cam_ip> [--wait-s 600] [--rounds 4]
"""
import sys
import os
import re
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
    m = re.search(r"<result>([^<]*)</result>", st)
    return m.group(1) if m else st[:60]


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


def dlna_check(cam):
    for i in range(10):
        a, d = auth_status(cam)
        log(f"  dlna: {a} ({d})")
        if a == "ok":
            return True
        time.sleep(2)
    return False


def poll_getstate(cam, max_s=60):
    t0 = time.time()
    while time.time() - t0 < max_s:
        time.sleep(2)
        st = get(cam, "mode=getstate", timeout=5)
        code = short(st)
        if int((time.time() - t0) // 5) != int(((time.time() - t0) - 2) // 5):
            log(f"  getstate: {code}")
        if code == "ok":
            return True
        if st.startswith("__ERR__"):
            log(f"  相机掉线（{st}）")
            return None
    return False


def grab(cam):
    log("== 窗口开始 ==")
    st = get(cam, "mode=getstate")
    code = short(st)
    log(f"  初始 getstate: {code}")

    if st.startswith("__ERR__"):
        return False
    if code == "ok":
        log("  ★ 配对已持久化（getstate 直接 ok），不发 accctrl ★")
    else:
        r = get(cam, urllib.parse.urlencode(
            {"mode": "accctrl", "type": "req_acc_can", "value": "", "value2": ""}))
        log(f"  核清理(空值 can, 一次): {short(r)}")
        time.sleep(2)
        r = get(cam, urllib.parse.urlencode(
            {"mode": "accctrl", "type": "req_acc", "value": ACC_UUID, "value2": DEV_NAME}))
        log(f"  req_acc(一次): {r[:100]}")
        with_msg = ("ok_under_research" in r) and ("no_msg" not in r)
        if with_msg:
            log("  ⚠ 对话框应已弹出 → 请用户点【允许/是】（轮询 150s）")
    r = get(cam, "mode=camcmd&value=playmode")
    log(f"  camcmd playmode: {short(r)}")
    ok = poll_getstate(cam, 150 if with_msg else 30)
    if ok is None:
        return False
    if not ok:
        log("  getstate 未达 ok")
        return False
    log("  getstate=ok！dlna 放行检查...")
    if dlna_check(cam):
        log("  ✅ 会话完全可用")
        return True
    return False


def main():
    cam = sys.argv[1] if len(sys.argv) > 1 else "192.168.54.1"
    wait_s, rounds = 600, 4
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--wait-s":
            wait_s = int(args[i + 1]); i += 2
        elif args[i] == "--rounds":
            rounds = int(args[i + 1]); i += 2
        else:
            i += 1
    log(f"目标 {cam}  轮数 {rounds}")
    for rnd in range(rounds):
        log(f"\n########## 第 {rnd+1}/{rounds} 轮 ##########")
        if not wait_online(cam, wait_s):
            log(f"  等待 {wait_s}s 相机仍未上线，本轮放弃")
            continue
        log("  相机上线")
        if grab(cam):
            log("\n★★★ 会话建立成功，开始受控复现 crash 001 ★★★")
            os.execv(sys.executable, [sys.executable,
                      os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "repro_crash.py"), cam, "--rounds", "3"])
        log("  本窗口失败，等相机掉线进下一窗口（最多 10 分钟）...")
        t0 = time.time()
        while time.time() - t0 < 600 and tcp80(cam):
            time.sleep(5)
    log("\n全部轮次失败。")
    sys.exit(2)


if __name__ == "__main__":
    main()
