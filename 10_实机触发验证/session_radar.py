#!/usr/bin/env python3
"""
session_radar.py —— dlna 授权维持机制探测（间隙测量），2026-10-16 15:00。

背景（14:52 窗口实证）：
  · 新武装等待画面 → req_acc → 裸 ok → playmode → dlna 200
  · 30s 完全静默后 dlna 403 且不可恢复（getstate 心跳救不回）
  · 相机等待画面随后自己跳回菜单 ⇒ 授予寿命 ≈ 授权→画面退出（~60-90s）

本脚本在【一个新鲜窗口】内测量 dlna 静默间隙的死亡阈值：
  前置：用户已重新武装等待画面（Mac 已连热点）
  流程：
    1. 等相机上线
    2. req_acc（一次）→ 期望裸 ok
    3. camcmd playmode
    4. 连续活动 30s：getstate 每 3s + BrowseMetadata 每 10s（确认授予存活）
    5. 间隙阶梯（getstate 心跳持续，dlna 静默）：
       10s → browse / 20s → browse / 40s → browse / 80s → browse
       记录每档 200/500 vs 403 vs 超时
  输出：dlna 最大存活间隙 → fuzzer 心跳设计常数

红线：req_acc 一次；全程只读；相机掉线即停。
用法：python3 -u session_radar.py <cam_ip> [--wait-s 900]
"""
import sys
import os
import re
import time
import socket
import threading
import urllib.parse
import urllib.request

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_dlna import make_body, raw_http, http_post

ACC_UUID = "4D454930-0100-1000-8001-020A0003BD13"
DEV_NAME = "LUMIX Sync"
UA = {"User-Agent": "LUMIX Sync", "Accept-Charset": "UTF-8"}
RESULTS = []


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
    return m.group(1) if m else st[:50]


def tcp80(cam, timeout=3):
    s = socket.socket(); s.settimeout(timeout)
    try:
        s.connect((cam, 80)); return True
    except OSError:
        return False
    finally:
        s.close()


def wait_online(cam, wait_s):
    t0 = time.time()
    while time.time() - t0 < wait_s:
        if tcp80(cam):
            return True
        time.sleep(5)
    return False


def dlna_browse(cam, label):
    body = make_body(BrowseFlag="BrowseMetadata").encode()
    e, st, head, dt = raw_http(cam, 60606, body, timeout=8)
    verdict = e or st
    log(f"  [dlna] {label}: {verdict}")
    RESULTS.append((label, verdict))
    return verdict


def main():
    cam = sys.argv[1] if len(sys.argv) > 1 else "192.168.54.1"
    wait_s = 900
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--wait-s":
            wait_s = int(args[i + 1]); i += 2
        else:
            i += 1

    log(f"目标 {cam}。等相机上线（用户需已重新武装等待画面）...")
    if not wait_online(cam, wait_s):
        log("相机未上线，退出"); sys.exit(2)
    log("相机上线，开始窗口内测量")

    st = get(cam, "mode=getstate")
    log(f"  初始 getstate: {short(st)}")

    r = get(cam, urllib.parse.urlencode(
        {"mode": "accctrl", "type": "req_acc", "value": ACC_UUID, "value2": DEV_NAME}))
    log(f"  req_acc(一次): {r[:90]}")
    if "<result>ok</result>" not in r.replace(" ", "") and "ok,S5-" not in r and "ok,4D" not in r:
        log("  req_acc 未达裸 ok，窗口作废（不再重发）"); sys.exit(3)

    r = get(cam, "mode=camcmd&value=playmode")
    log(f"  camcmd playmode: {short(r)}")

    # 停止条件
    stop = threading.Event()

    def heartbeat():
        while not stop.is_set():
            s = get(cam, "mode=getstate", timeout=5)
            if s.startswith("__ERR__"):
                log(f"  [hb] getstate 掉线: {s}"); stop.set(); return
            time.sleep(3)

    th = threading.Thread(target=heartbeat, daemon=True)
    th.start()

    log("  阶段A：连续活动 30s（dlna 每 10s）")
    for t in (0, 10, 20, 30):
        dlna_browse(cam, f"A@{t}s")
        if stop.is_set():
            break
    if stop.is_set():
        log("  掉线，测量终止"); sys.exit(4)

    log("  阶段B：dlna 静默间隙阶梯（getstate 心跳持续）")
    for gap in (10, 20, 40, 80):
        if stop.is_set():
            break
        log(f"  静默 {gap}s（仅 getstate 心跳）...")
        time.sleep(gap)
        dlna_browse(cam, f"B-gap{gap}s")
        v = RESULTS[-1][1]
        if isinstance(v, int) and v in (200, 500):
            log(f"  → 存活（{v}），继续加大间隙")
        else:
            log(f"  → 死亡（{v}）！dlna 最大存活间隙 < {gap}s（在上一档 {RESULTS[-2][0] if len(RESULTS)>1 else '?'} 还活着）")
            break

    stop.set()
    log("\n===== 结果汇总 =====")
    for label, v in RESULTS:
        print(f"  {label}: {v}")
    log("设计常数：fuzzer 的 dlna 心跳间隔必须 < 死亡间隙；建议取死亡间隙的 1/2。")
    sys.exit(0)


if __name__ == "__main__":
    main()
