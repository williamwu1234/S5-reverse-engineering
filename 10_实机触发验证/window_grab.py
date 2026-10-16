#!/usr/bin/env python3
"""
window_grab.py —— 抢占 SoftAP 重启用窗口的"清 pending + 握手"一体脚本。

背景（2026-10-16 14:20 实测）：
  相机停在「等待WiFi连接」画面、屏幕稳定不重启，但 SoftAP 约每 2 分钟重启一次
  （Mac 侧 en0 每 2 分钟 media inactive），离线 1-9 分钟后自动恢复。
  在线窗口内 getstate 恒 err_critical，疑为 04:34 v1 会话残留的 stale pending
  跨 flash 持久化，污染每个新窗口。

流程（每个新窗口内一气呵成，全部带时间戳日志）：
  A. 等相机上线（TCP :80，最多 wait_s）
  B. req_acc_can（同一 UUID，仅一次）—— 清陈旧 pending（权威文档 §4-1 允许的清理路径）
  C. req_acc（同一 UUID，仅一次）
  D. camcmd playmode
  E. 快轮询 getstate（1.5s 间隔，最多 poll_s）
  F. dlna BrowseMetadata 放行检查
  G. 成功 → 直接衔接 repro_crash.py；失败 → 等待下一个窗口重试（最多 rounds 轮）

红线：每个窗口 req_acc 至多一次；req_acc_can 每轮至多一次；绝不轮询重发。
用法：python3 -u window_grab.py <cam_ip> [--wait-s 300] [--poll-s 60] [--rounds 3] [--no-cleanup]
"""
import sys
import os
import time
import socket
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_dlna import auth_status, make_body, http_post

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


def grab(cam, do_cleanup):
    """一个窗口内的一整套动作。返回 True=会话可用。"""
    log("== 窗口开始 ==")
    st = get(cam, "mode=getstate")
    log(f"  初始 getstate: {st[:80]}")

    if do_cleanup:
        r = get(cam, urllib.parse.urlencode(
            {"mode": "accctrl", "type": "req_acc_can", "value": ACC_UUID, "value2": ""}))
        log(f"  B. req_acc_can(清 pending, 仅一次): {r[:80]}")
        time.sleep(2)
        st = get(cam, "mode=getstate")
        log(f"     清后 getstate: {st[:80]}")

    r = get(cam, urllib.parse.urlencode(
        {"mode": "accctrl", "type": "req_acc", "value": ACC_UUID, "value2": DEV_NAME}))
    log(f"  C. req_acc(仅一次): {r[:100]}")

    r = get(cam, "mode=camcmd&value=playmode")
    log(f"  D. camcmd playmode: {r[:80]}")

    ok = False
    for i in range(40):
        time.sleep(1.5)
        st = get(cam, "mode=getstate", timeout=5)
        is_ok = "<result>ok</result>" in st.replace(" ", "")
        if i == 0 or i % 4 == 0 or is_ok:
            log(f"  E. [{i*1.5:.0f}s] getstate: {st[:80]}")
        if is_ok:
            ok = True
            break
    if not ok:
        log("  getstate 未达 ok（本窗口失败，不重发 req_acc）")
        return False

    log("  F. dlna 放行检查...")
    for i in range(10):
        a, d = auth_status(cam)
        log(f"     dlna: {a} ({d})")
        if a == "ok":
            log("  ✅ 会话可用（getstate=ok 且 dlna 放行）")
            return True
        time.sleep(2)
    log("  getstate=ok 但 dlna 未放行（ok_under_research* 翻动中？）")
    return False


def main():
    cam = sys.argv[1] if len(sys.argv) > 1 else "192.168.54.1"
    wait_s, poll_s, rounds = 300, 60, 3
    do_cleanup = True
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--wait-s":
            wait_s = int(args[i + 1]); i += 2
        elif args[i] == "--poll-s":
            poll_s = int(args[i + 1]); i += 2
        elif args[i] == "--rounds":
            rounds = int(args[i + 1]); i += 2
        elif args[i] == "--no-cleanup":
            do_cleanup = False; i += 1
        else:
            i += 1

    log(f"目标 {cam}  等待窗口上限 {wait_s}s  轮数 {rounds}  cleanup={do_cleanup}")
    for rnd in range(rounds):
        log(f"\n########## 第 {rnd+1}/{rounds} 轮 ##########")
        if not wait_online(cam, wait_s):
            log(f"  等待 {wait_s}s 相机仍未上线，本轮放弃")
            continue
        log("  相机上线")
        if grab(cam, do_cleanup):
            log("\n★★★ 会话建立成功，开始受控复现 crash 001 ★★★")
            os.execv(sys.executable, [sys.executable,
                      os.path.join(os.path.dirname(os.path.abspath(__file__)),
                                   "repro_crash.py"), cam, "--rounds", "3"])
        # 失败：等相机掉线→下一窗口
        log("  本窗口失败，等待相机掉线进入下一窗口（最多 10 分钟）...")
        t0 = time.time()
        while time.time() - t0 < 600:
            if not tcp80(cam):
                log("  相机已掉线，等下一窗口")
                break
            time.sleep(5)
    log("\n全部轮次失败。")
    log("建议：① 相机接 AC 供电（电池可能触发 WiFi 省电重启）")
    log("      ② 在相机上退出等待画面再重新进入（重新武装 SoftAP）")
    log("      ③ 或断电 30s 冷启动后停在等待画面再试")
    sys.exit(2)


if __name__ == "__main__":
    main()
