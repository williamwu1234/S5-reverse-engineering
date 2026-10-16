#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5monitor.py — DC-S5 无线监看 + 触摸对焦（复刻 LUMIX 官方取景逻辑）

设计目标：**尽量还原官方的操作逻辑**，并且**零第三方依赖**（只用 Python 标准库）。

官方逻辑链路（本项目逆向所得，与 pylumix / LUMIX Sync 一致）：
    ① accctrl type=req_acc   value=<device_id>  value2=<device_name>    ← 申请访问（配对）
    ② camcmd  value=recmode                                            ← 切到拍摄模式
    ③ startstream value=<UDP端口 49152-65535>                          ← 相机把取景流发到该端口
    ④ UDP 上收到的是 **MJPEG**（每包含 JPEG：SOI \\xff\\xd8 … EOI \\xff\\xd9）
    ⑤ 期间必须周期性 getstate 心跳，否则相机会停流                     ← 官方 App 也这么做
    ⑥ camctrl type=touch / pinch / change_disp_mag ...                 ← 触摸对焦 / 缩放
    ⑦ camcmd  value=capture / video_recstart / video_recstop           ← 拍照 / 录像
    ⑧ stopstream                                                       ← 停流

本工具再做一层桥接，让**任意浏览器的 <img> 标签**就能看：
    UDP(MJPEG) ──► 本进程 ──► HTTP multipart/x-mixed-replace ──► 手机/电脑浏览器

用法：
    python3 s5monitor.py                      # 默认 host 192.168.54.1（相机 SoftAP 网关）
    python3 s5monitor.py --host 192.168.1.131 # 家庭网内的相机 IP
    python3 s5monitor.py --no-stream          # 只起控制台，不自动开始取景
    然后：手机/电脑浏览器打开  http://<本机IP>:8080

安全声明：本工具只发送【已验证的只读/常规控制】命令：
    accctrl(req_acc) / getstate / getinfo / getsetting / setsetting(白名单) /
    camcmd(recmode/capture/video_recstart/video_recstop/pictmode/playmode) /
    camctrl(touch/touch_trace/pinch/change_disp_mag/asst_disp/af_ae_lock) /
    startstream / stopstream / playcmd
**绝不发送**：startsenddata/senddata（上传）、camcmd=poweroff、0x9406 类子码、格式化、重置、固件升级。
"""

import argparse
import collections
import atexit
import json
import os
import signal
import socket
import sys
import threading
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

# ---------------------------------------------------------------- 常量

DEFAULT_HOST = "192.168.54.1"      # 相机 SoftAP 网关（实测）
UDP_PORT = 49152                   # 取景流端口（官方允许 49152–65535）
BOUNDARY = b"--frame\r\n"
PACING_MODE = "fixed"              # ★ "fixed" = 官方风格：固定帧率 + 只取最新帧（推荐）
                                   #   "adaptive" = 队列反馈控制（追相机到达速率）
PACING_FPS = 18.0                  # ★ 官方 App 的取景流标准：640p @ 18fps
FIXED_KEEP = 3                     # 固定模式下最多保留 3 帧（≈170ms），抗短空档而不积延迟
PACING_SAFETY = 0.85               # （保留，供参考；现由队列反馈控制主导）
RESERVE_TARGET = 8                 # ★ 目标队列储备（帧）≈ 8/30fps ≈ 270ms 延迟
                                   #   调大=更抗卡顿但延迟更高；调小=更跟手但易定住
PACING_KP = 0.6                    # ★ 反馈比例系数（越大纠偏越快，过大会抖）
ARRIVAL_EMA = 0.25                 # ★ 到达速率平滑系数（越小越平滑，抗突发虚高）
PACING_MIN_FPS = 8.0               # 自适应下限
PACING_MAX_FPS = 60.0              # 自适应上限（放开，让控制器能把积压的队列排空）
PACING_BUF = 40                    # ★ 缓冲上限（40 帧 ≈ 1.3 秒；超过即丢最老帧，防止延迟堆积）
REPUBLISH_ON_UNDERRUN = True       # 空档时重播最后一帧，保证浏览器 MJPEG 不断流
KEEPALIVE_SEC = 10.0               # ★ 心跳间隔（实测最优值）
                                   #   实测结论（2026-10-13）：
                                   #   · 完全不发心跳 ⇒ 相机约 13 秒后【停流】
                                   #   · 每次 getstate 耗时约 1–3 秒，期间取景流被挤停
                                   #   · 10 秒一次 ⇒ 流稳定 18.7fps，【零停顿】
                                   #   · 关键前提：/api/state 必须走服务端缓存，
                                   #     否则浏览器每 3 秒轮询一次就会把相机打到持续繁忙

# 身份格式来自逆向：H5/p.java
#   "4D454930-0100-1000-8001-" + <seed>
# seed 用固定值也能工作（pylumix 即用固定值）
DEFAULT_DEVICE_ID = "4D454930-0100-1000-8001-020A0003BD13"
DEFAULT_DEVICE_NAME = "S5Monitor"

# 只允许这些 camcmd（白名单，杜绝误触危险动作）
ALLOWED_CAMCMD = {
    "recmode", "capture", "video_recstart", "video_recstop",
    "pictmode", "playmode", "burst", "recstop",
    # 变焦（来自 camcmdlist，capability 里已列出）
    "tele-normal", "tele-fast", "wide-normal", "wide-fast",
    "focus-stop",          # 焦点驱动停止
}
# 只允许这些 camctrl
ALLOWED_CAMCTRL = {
    # ★ 参数格式严格按官方 App（p168v5/a.java 与 liveview/i.java）还原：
    "touch",              # value=<x>/<y>  value2=on|off   ← 触摸对焦（斜杠分隔！）
    "touch_trace",        # value=<x>/<y>
    "touchaf_chg_pos",    # value=<x>/<y>
    "touchaf_chg_area",   # value=up|down
    "touchae_ctrl",       # value=on|off
    "touchcapt_ctrl",     # value=enable|disable|off   （触摸快门）
    "focus",              # value=tele-normal|tele-fast|wide-normal|wide-fast|focus-stop（★ 变焦）
    "pinch",              # value=...
    "change_disp_mag",    # 放大辅助
    "asst_disp",          # 峰值/辅助显示
    "af_ae_lock",         # value=on|off
    "frame_ctrl",         # 帧控制（变焦方向）
}


# ---------------------------------------------------------------- 相机客户端

class Lumix:
    """极简 cam.cgi 客户端（纯标准库）"""

    def __init__(self, host, device_id, device_name, verbose=True):
        self.host = host
        self.base = "http://%s/cam.cgi" % host
        self.device_id = device_id
        self.device_name = device_name
        self.verbose = verbose
        self.lock = threading.Lock()
        self.last_error = ""
        self.access_raw = ""           # ★ accctrl 原始回复
        self.access_mode = "unknown"   # ★ ok / ok_under_research_no_msg / ...
        self.access_fields = []
        self.auto_ctrl_test = []       # ★ 启动时自动跑的 camctrl 自检结果

    def _get_recover(self, mode, timeout=5.0, **kw):
        """★ 会话自愈：遇到 err_reject 时重做 req_acc 再试一次
           （实测相机只认一个已授权会话，且会因高频请求而拒绝）"""
        r = self._get(mode, timeout=timeout, **kw)
        if r and "err_reject" in r and mode != "accctrl":
            print("[accctrl] 收到 err_reject，自动重新申请访问…")
            self.req_acc()
            time.sleep(1.2)
            r2 = self._get(mode, timeout=timeout, **kw)
            if r2 and "err_reject" not in r2:
                return r2
            return r2 or r
        return r

    def _get(self, mode, timeout=5.0, **kw):
        params = {"mode": mode}
        params.update({k: v for k, v in kw.items() if v is not None})
        url = self.base + "?" + urllib.parse.urlencode(params)
        req = urllib.request.Request(url, headers={"User-Agent": "LUMIX Sync"})
        try:
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode("utf-8", "replace")
        except urllib.error.HTTPError as e:
            return "<!--HTTPError %s-->%s" % (e.code, e.read().decode("utf-8", "replace"))
        except Exception as e:
            self.last_error = str(e)
            return ""

    # -- 基础 --
    def getstate(self, timeout=2.5):
        """心跳用短超时：绝不拖住收流线程"""
        return self._get("getstate", timeout=timeout)

    def camcmd(self, value, value2=None, retries=3):
        if value not in ALLOWED_CAMCMD:
            self.last_error = "blocked: camcmd %r 不在白名单" % value
            return None            # None = 被安全白名单拦截
        r = ""
        for i in range(retries):
            r = self._get_recover("camcmd", value=value, value2=value2, timeout=4.0)
            if not r or (("err_busy" not in r) and ("err_reject" not in r)):
                return r
            time.sleep(0.6 + 0.6 * i)
        return r

    def camctrl(self, ctype, value=None, value2=None, retries=8):
        """★ 关键：相机的授权状态在 ok / ok_under_research_no_msg 之间【不断翻动】，
           camctrl 只有在"恰好是 ok"的那一瞬间才会成功。
           ⇒ 因此 err_busy 与 err_reject 都必须【退避重试】，直到撞上 ok 的窗口。
        """
        if ctype not in ALLOWED_CAMCTRL:
            self.last_error = "blocked: camctrl %r 不在白名单" % ctype
            return None
        r = ""
        for i in range(retries):
            r = self._get_recover("camctrl", type=ctype, value=value, value2=value2, timeout=4.0)
            if not r:
                return r
            if ("err_busy" not in r) and ("err_reject" not in r):
                return r                       # ok（或其他非忙错误）
            time.sleep(0.5 + 0.35 * i)         # 退避：0.5/0.85/1.2/… 秒
        return r

    def getinfo(self, itype):
        return self._get("getinfo", type=itype, timeout=20.0)

    def getsetting(self, stype):
        return self._get("getsetting", type=stype)

    def setsetting(self, stype, value):
        return self._get("setsetting", type=stype, value=value)

    # -- 配对（官方第一步）--
    def note_access(self, txt):
        """★ 解析并记录 accctrl 状态 —— 这是 camctrl 能否使用的关键门控"""
        t = (txt or "").strip()
        if not t:
            return
        self.access_raw = t
        parts = t.split(",")
        self.access_mode = parts[0].strip()
        self.access_fields = [x.strip() for x in parts[1:]]
        if self.verbose:
            print("[accctrl] 状态 = %s   字段 = %s" % (self.access_mode, self.access_fields))
            if self.access_mode != "ok":
                print("[accctrl] ⚠️ 非完整授权！相机上可能有【允许连接？】待批准的对话框，")
                print("[accctrl]    请在相机屏幕上点【允许/是】。否则 camctrl（触摸对焦等）会被拒绝。")

    def req_acc(self):
        txt = self._get("accctrl", type="req_acc",
                        value=self.device_id, value2=self.device_name)
        self.note_access(txt)
        return txt

    def ensure_access(self, wait_approve_sec=180):
        """★ 正确握手（2026-10-13 实测，血泪教训）：

            相机对 req_acc 有【频率/次数保护】：
              短时间多次 req_acc  ⇒ 相机弹出「智能手机应用程序需要更新」
                                    ⇒ invalid login ⇒ 必须重启相机 ❌

            因此正确做法是：
              · req_acc 【只发一次】
              · 然后只轮询 getstate（不再重发 req_acc）等待用户点「允许」
              · 最多再补一次 req_acc（间隔 20 秒），之后无论结果都不再打扰相机
        """
        st = self.getstate()
        already = "<result>ok</result>" in st.replace(" ", "")
        if already:
            self.req_acc()
            if self.access_mode == "ok":
                if self.verbose:
                    print("[accctrl] 已处于完整授权（ok）")
                return True
            print("[accctrl] 当前为受限授权（%s）—— 需在相机上批准一次" % self.access_mode)

        print("[accctrl] 👉 相机屏幕上会弹出「允许连接？」—— 请点【允许 / 是】")
        self.req_acc()                      # ★ 第 1 次（也是唯一一次主动请求）
        t0 = time.time()
        last_extra = t0
        while time.time() - t0 < wait_approve_sec:
            time.sleep(2.0)
            st = self.getstate()
            if "<result>ok</result>" in st.replace(" ", ""):
                if self.access_mode == "ok":
                    print("[accctrl] ✅ 已获得完整授权（ok）")
                    return True
                # getstate 通了但权限等级未知 ⇒ 允许补一次确认请求（总量极少）
                if time.time() - last_extra > 20:
                    last_extra = time.time()
                    self.req_acc()
                    if self.access_mode == "ok":
                        print("[accctrl] ✅ 已获得完整授权（ok）")
                        return True
            if self.verbose and int(time.time() - t0) % 10 == 0:
                print("[accctrl]    等待你在相机上点「允许」…（已等 %ds，当前 %s）"
                      % (int(time.time() - t0), self.access_mode))
        print("[accctrl] ⚠️ 等待超时。")
        print("[accctrl]    取景流 / 拍照 / 录像不受影响；camctrl（触摸对焦等）可能不可用。")
        print("[accctrl]    ⚠️ 切勿反复重试 req_acc —— 会被相机判为异常 App 并触发 invalid login！")
        return self.access_mode == "ok"

    # -- 取景流 --
    def start_stream(self, port, retries=4):
        """★ 相机强制【单流会话】：若上一会话没停干净会返回 err_busy。
           所以先 stopstream 清场，再 startstream；仍 busy 就退避重试。"""
        self.camcmd("recmode")
        time.sleep(0.3)
        self._get("stopstream")           # 清掉可能残留的旧会话
        time.sleep(0.6)
        for i in range(retries):
            r = self._get("startstream", value=port)
            if r and "err_busy" not in r:
                return r
            print("[stream] startstream 返回 err_busy，第 %d 次重试…" % (i + 1))
            self._get("stopstream")
            time.sleep(1.2 + i * 0.8)     # 退避
        return r

    def stop_stream(self):
        return self._get("stopstream")

    # -- 状态解析（简单文本抽取，避免依赖 XML 库的行为差异）--
    def state_dict(self):
        txt = self.getstate()
        out = {"raw_ok": "<result>ok</result>" in txt.replace(" ", "")}
        for key in ("batt", "battery", "sdcardstatus", "sd_access", "remaining",
                    "capacity", "rec", "recstate", "moviestate", "cammode",
                    "iso", "fnumber", "shutterspeed", "exposure", "zoom",
                    "lens", "temps", "curmenu"):
            a = txt.find("<%s>" % key)
            if a >= 0:
                b = txt.find("</%s>" % key, a)
                if b > 0:
                    out[key] = txt[a + len(key) + 2:b].strip()
        return out


# ---------------------------------------------------------------- 流桥接

class StreamBridge:
    """UDP(MJPEG) ──► 内存里保存最新帧 ──► HTTP 端按需推送"""

    def __init__(self, cam, port, keepalive=KEEPALIVE_SEC, verbose=True,
                 pacing_mode=PACING_MODE, pacing_fps=PACING_FPS):
        self.cam = cam
        self.port = port
        self.keepalive = keepalive
        self.verbose = verbose
        self.pacing_mode = pacing_mode
        self.pacing_fps_fixed = pacing_fps
        self.frame = None
        self.frame_id = 0
        self.cond = threading.Condition()
        self.running = False
        self.sock = None
        self.last_packet = 0.0
        self.fps = 0.0
        self._fps_mark = time.time()
        self._fps_cnt = 0
        self.state_cache = {}          # ★ 服务端缓存：/api/state 不再直接打相机
        self.cam_busy_ms = 0           # 最近一次 getstate 耗时（诊断用）
        # ★ 节奏器：相机流是"突发式"的，这里把它抹平成匀速流
        self.q = collections.deque(maxlen=PACING_BUF)
        self.paced_frame = None
        self.paced_id = 0
        self.underrun = 0
        self.pacing = True
        # ★ 卡顿诊断日志（每个卡顿一条，含归因）
        self.stalls = collections.deque(maxlen=200)
        self._last_rx = 0.0
        self._last_paced_push = 0.0
        self._gap_run = None
        self.rx_gaps = collections.Counter()      # 相机侧空档
        self.http_slow = 0
        self.max_gap_ms = 0
        self.pacing_fps = PACING_FPS
        self.arrival_fps = 0.0
        self.thinned = 0
        self.queue_reserve = 0
        self.dropped = 0
        self.rx_count = 0          # ★ 单调收帧计数（用于准确算到达速率）
        self._rx_at_win = 0
        self.paused_at = 0.0       # ★ 最近一次暂停取景的时刻（用于排除假空档）

    # -- 心跳线程（★ 必须独立：心跳绝不能占用收流循环）--
    def refresh_state(self):
        """向相机取一次状态并缓存（会短暂影响流，所以要少调用）"""
        t0 = time.time()
        try:
            st = self.cam.state_dict()
            # ★ 顺带读对焦模式（getsetting focusmode）—— 决定放大辅助/触摸对焦是否适用
            try:
                fm = self.cam.getsetting("focusmode")
                import re as _r
                m = _r.search(r'focusmode="([^"]*)"', fm or "")
                if m:
                    st["focusmode"] = m.group(1).upper()
            except Exception:
                pass
            st["fps"] = round(self.fps, 1)
            st["frames"] = self.frame_id
            st["streaming"] = self.running
            st["host"] = self.cam.host
            st["cam_latency_ms"] = int((time.time() - t0) * 1000)
            self.state_cache = st
        except Exception:
            pass
        self.cam_busy_ms = int((time.time() - t0) * 1000)

    def _beat(self):
        if self.keepalive <= 0:
            print("[beat] 心跳已关闭（--keepalive 0）")
            return
        while self.running:
            time.sleep(self.keepalive)
            if not self.running:
                break
            self.refresh_state()

    # -- 收流线程 --
    def _rx(self):
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        # ★ 加大接收缓冲，抗突发丢帧（macOS 上内核会翻倍）
        for bufsz in (8 << 20, 4 << 20, 2 << 20, 1 << 20):
            try:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, bufsz)
                break
            except OSError:
                continue
        try:
            s.bind(("0.0.0.0", self.port))
        except OSError as e:
            print("!! 无法绑定 UDP %d: %s" % (self.port, e))
            self.running = False
            return
        s.settimeout(1.0)
        self.sock = s
        print("[stream] UDP %d 已监听，向相机请求取景流…" % self.port)
        r = self.cam.start_stream(self.port)
        if self.verbose and r:
            print("[stream] startstream -> %s" % r.strip()[:80])
        # ★ 心跳独立线程
        threading.Thread(target=self._beat, daemon=True).start()
        n = 0
        drop = 0
        while self.running:
            try:
                data, _ = s.recvfrom(65536)
                s0 = data.find(b"\xff\xd8")
                e0 = data.find(b"\xff\xd9")
                if s0 != -1 and e0 != -1 and e0 > s0:
                    jpg = data[s0:e0 + 2]
                    n += 1
                    self.rx_count += 1
                    # ★ 诊断：相机侧帧间隔
                    now = time.time()
                    # ★ 静默期（暂停取景/自检中）不计入空档统计
                    if self.paused_at and (now - self.paused_at) < 120:
                        self._last_rx = now
                        continue_rx = True
                    if self._last_rx:
                        gap = (now - self._last_rx) * 1000
                        if gap > 150 and not (self.paused_at and (now - self.paused_at) < 120):
                            self.stalls.append({
                                "t": time.strftime("%H:%M:%S"),
                                "kind": "★相机侧空档",
                                "ms": int(gap),
                                "detail": "UDP 连续 %d ms 没收到帧（相机突发式推流）" % int(gap),
                                "cam_latency_ms": self.cam_busy_ms,
                            })
                            self.rx_gaps[int(gap) // 100] += 1
                            self.max_gap_ms = max(self.max_gap_ms, int(gap))
                    self._last_rx = now
                    if self.pacing:
                        if len(self.q) >= PACING_BUF:
                            self.dropped += 1     # ★ 队列满导致的丢帧（跳帧来源）
                        self.q.append(jpg)        # ★ 交给节奏器
                    else:
                        with self.cond:
                            self.frame = jpg
                            self.frame_id += 1
                            self.cond.notify_all()
                    self._fps_cnt += 1
                    if time.time() - self._fps_mark >= 1.0:
                        self.fps = self._fps_cnt / (time.time() - self._fps_mark)
                        self._fps_cnt = 0
                        self._fps_mark = time.time()
                else:
                    drop += 1
                self.last_packet = time.time()
            except socket.timeout:
                pass
            except Exception:
                if not self.running:
                    break
        try:
            self.cam.stop_stream()
        except Exception:
            pass
        try:
            s.close()
        except Exception:
            pass
        print("[stream] 已停止（收到 %d 帧，丢弃 %d 个非帧包；节奏空档重播 %d 次）"
              % (n, drop, self.underrun))

    def pause(self):
        """暂停取景（进回放前必须调用）"""
        if not self.running:
            return
        self.running = False
        self.paused_at = time.time()
        try:
            self.cam.stop_stream()
        except Exception:
            pass
        time.sleep(0.5)
        print("[stream] 已暂停（为回放模式让路）")

    def resume(self):
        if not self.running:
            self.start()

    # -- ★ 节奏器：以固定帧率把队列里的帧匀速发布（空档时重播上一帧）--
    def _pacer(self):
        """★ 自适应节奏器：
           关键洞察 —— 相机平均 ~19fps 但【突发式】；若我们按 20fps 播放，
           消耗快于供给 ⇒ 队列被抽干 ⇒ 空档只能垫帧（画面定住 = 卡顿）。
           解法：播放帧率=相机到达速率 × PACING_SAFETY(0.92)，让队列始终有储备，
                 从而用缓冲区"吸收"相机的空档 ⇒ 画面真正匀速流畅。"""
        dt = 1.0 / max(1.0, self.pacing_fps_fixed if self.pacing_mode == "fixed" else PACING_FPS)
        nxt = time.time()
        win_t = time.time()
        win_n = 0
        while self.running:
            nxt += dt
            frame = None
            if self.pacing and self.pacing_mode == "fixed":
                # ★ 官方风格：只保留最新几帧，其余主动抽掉 ⇒ 延迟极低、节奏恒定
                while len(self.q) > FIXED_KEEP:
                    try:
                        self.q.popleft()
                        self.dropped += 1
                        self.thinned += 1
                    except IndexError:
                        break
            # ★ 延迟硬上限：积压过多就直接丢到目标值，防止延迟无限堆积
            if self.pacing and self.pacing_mode != "fixed" and len(self.q) > RESERVE_TARGET * 4:
                drop_n = len(self.q) - RESERVE_TARGET
                for _ in range(drop_n):
                    try:
                        self.q.popleft()
                        self.dropped += 1
                    except IndexError:
                        break
            if self.q:
                frame = self.q.popleft()
            elif self.paced_frame is not None:
                if REPUBLISH_ON_UNDERRUN:
                    frame = self.paced_frame     # ★ 重播：保证浏览器画面不断
                    self.underrun += 1
                    if self.underrun % 10 == 1:
                        self.stalls.append({
                            "t": time.strftime("%H:%M:%S"),
                            "kind": "节奏器垫帧",
                            "ms": 0,
                            "detail": "队列空，重播上一帧（累计第 %d 次）" % self.underrun,
                            "queue": len(self.q),
                        })
            if frame is not None:
                is_new = (frame is not self.paced_frame)     # ★ 垫帧不算"到达"
                with self.cond:
                    self.paced_frame = frame
                    self.paced_id += 1
                    self.frame = frame
                    self.frame_id = self.paced_id
                    self.cond.notify_all()
                if is_new:
                    win_n += 1                                # ★ 只统计真实新帧
            # ★ 每 0.5 秒做一次【队列长度反馈控制】：
            #   目标是把储备锁在 RESERVE_TARGET 附近 ——
            #   队列偏满 ⇒ 播快点（避免溢出丢帧）；队列偏空 ⇒ 播慢点（避免抽干垫帧）
            if self.pacing_mode != "fixed" and time.time() - win_t >= 0.5:
                now = time.time()
                # ★ 用单调计数差分算真实到达帧数（旧算法混入了队列存量，会虚高）
                arrived = self.rx_count - self._rx_at_win
                self._rx_at_win = self.rx_count
                span = now - win_t
                if span > 0:
                    rate = arrived / span
                    if rate > 1.0:
                        # ★ EMA 平滑，抑制突发造成的速率虚高
                        self.arrival_fps = (self.arrival_fps * (1 - ARRIVAL_EMA)
                                            + rate * ARRIVAL_EMA) if self.arrival_fps else rate
                    base = max(PACING_MIN_FPS, self.arrival_fps or PACING_FPS)
                else:
                    base = self.arrival_fps or PACING_FPS
                # ★ 比例控制：被控量只有【当前队列长度】（不含已发布帧，否则会误判为满而超速）
                err = (len(self.q) - RESERVE_TARGET) / max(1.0, float(RESERVE_TARGET))
                target = base * (1.0 + PACING_KP * err)
                target = max(PACING_MIN_FPS, min(PACING_MAX_FPS, target))
                dt = dt * 0.4 + (1.0 / target) * 0.6     # 平滑过渡，避免抖动
                self.pacing_fps = round(target, 1)
                self.queue_reserve = len(self.q)
                self.dropped = getattr(self, "dropped", 0)
                win_t = now; win_n = 0
            sl = nxt - time.time()
            if sl > 0:
                time.sleep(sl)
            else:
                nxt = time.time()                # 落后了，重新对齐

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._rx, daemon=True).start()
        if self.pacing:
            threading.Thread(target=self._pacer, daemon=True).start()

    def stop(self):
        self.running = False

    def wait_frame(self, last_id, timeout=10.0):
        with self.cond:
            if self.frame_id == last_id:
                self.cond.wait(timeout)
            return self.frame_id, self.frame


# ---------------------------------------------------------------- SSDP "alive" 上报
# 官方 App 的 DlnaWrapper.advertisementStart()（native dlnaCore）等价物：
#   向 239.255.255.250:1900 发 SSDP NOTIFY(ssdp:alive)，并周期性重发。
#   本工具此前只做 accctrl，从未做这一步 —— 疑似正是 camctrl 的准入条件。
SSDP_ADDR = ("239.255.255.250", 1900)


class SSDPAdvertiser:
    def __init__(self, uuid, port, verbose=True, interval=20.0):
        self.uuid = uuid
        self.port = port
        self.verbose = verbose
        self.interval = interval
        self.running = False
        self.sent = 0
        self.local_ip = self._detect_ip()

    @staticmethod
    def _detect_ip():
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.connect(("192.168.1.1", 80))
            ip = s.getsockname()[0]
            s.close()
            return ip
        except Exception:
            return "127.0.0.1"

    def _msg(self, nts="ssdp:alive"):
        ip = self.local_ip
        location = "http://%s:%d/desc.xml" % (ip, self.port)
        lines = [
            "NOTIFY * HTTP/1.1",
            "HOST: 239.255.255.250:1900",
            "CACHE-CONTROL: max-age=1800",
            "LOCATION: " + location,
            "SERVER: Linux/3.18 UPnP/1.0 LUMIX/1.0",
            "NT: upnp:rootdevice",
            "NTS: " + nts,
            "USN: uuid:%s::upnp:rootdevice" % self.uuid,
            "X-DLNA-DEVICE-UUID: " + self.uuid,
            "",
            "",
        ]
        return "\r\n".join(lines).encode()

    def _msearch(self):
        """同时发一次 M-SEARCH，主动找相机（官方 deviceSearch 的等价物）"""
        lines = [
            "M-SEARCH * HTTP/1.1",
            "HOST: 239.255.255.250:1900",
            'MAN: "ssdp:discover"',
            "MX: 2",
            "ST: ssdp:all",
            "",
            "",
        ]
        return "\r\n".join(lines).encode()

    def send_once(self):
        try:
            s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 4)
            s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_IF,
                         socket.inet_aton(self.local_ip))
            s.sendto(self._msg("ssdp:alive"), SSDP_ADDR)
            s.sendto(self._msearch(), SSDP_ADDR)
            s.close()
            self.sent += 1
            return True
        except Exception as e:
            if self.verbose:
                print("[ssdp] 发送失败: %s" % e)
            return False

    def _loop(self):
        while self.running:
            self.send_once()
            for _ in range(int(self.interval * 2)):
                if not self.running:
                    break
                time.sleep(0.5)

    def start(self):
        if self.running:
            return
        self.running = True
        threading.Thread(target=self._loop, daemon=True).start()
        if self.verbose:
            print("[ssdp] 已启动 alive 上报：uuid=%s  location=http://%s:%d/desc.xml"
                  % (self.uuid, self.local_ip, self.port))

    def stop(self):
        self.running = False


# ---------------------------------------------------------------- HTTP 服务

class Handler(BaseHTTPRequestHandler):
    server_version = "s5monitor"
    cam = None
    bridge = None
    www = None

    def log_message(self, fmt, *a):
        pass  # 静音

    # ---- 工具 ----
    def _send(self, code, ctype, body, extra=None):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        for k, v in (extra or {}).items():
            self.send_header(k, v)
        self.end_headers()
        if body:
            self.wfile.write(body)

    def _json(self, obj, code=200):
        self._send(code, "application/json; charset=utf-8",
                   json.dumps(obj, ensure_ascii=False).encode())

    # ---- 路由 ----
    def do_GET(self):
        u = urllib.parse.urlparse(self.path)
        p = u.path
        q = urllib.parse.parse_qs(u.query)

        if p in ("/", "/index.html"):
            path = os.path.join(self.www, "index.html")
            try:
                with open(path, "rb") as f:
                    self._send(200, "text/html; charset=utf-8", f.read())
            except Exception:
                self._send(404, "text/plain", b"index.html missing")
            return

        if p == "/desc.xml":
            body = ("""<?xml version="1.0"?>
<root xmlns="urn:schemas-upnp-org:device-1-0">
  <specVersion><major>1</major><minor>0</minor></specVersion>
  <device>
    <deviceType>urn:schemas-upnp-org:device:MediaServer:1</deviceType>
    <friendlyName>S5Monitor</friendlyName>
    <manufacturer>research</manufacturer>
    <modelName>S5 Monitor</modelName>
    <UDN>uuid:%s</UDN>
  </device>
</root>""" % self.cam.device_id).encode()
            self._send(200, "text/xml; charset=utf-8", body)
            return

        if p == "/stream":
            self._mjpeg()
            return

        if p == "/api/state":
            # ★ 默认走缓存，绝不因为浏览器轮询而打断取景流
            if (q.get("refresh") or ["0"])[0] in ("1", "true"):
                self.bridge.refresh_state()
            elif not self.bridge.state_cache:
                self.bridge.refresh_state()
            st = dict(self.bridge.state_cache)
            st["fps"] = round(self.bridge.fps, 1)
            st["frames"] = self.bridge.frame_id
            st["streaming"] = self.bridge.running
            st["keepalive_sec"] = self.bridge.keepalive
            st["access_mode"] = self.cam.access_mode
            st["access_raw"] = self.cam.access_raw
            st["camctrl_ok"] = (self.cam.access_mode == "ok")
            self._json(st)
            return

        if p == "/api/cmd":
            v = (q.get("value") or [""])[0]
            v2 = (q.get("value2") or [None])[0]
            r = self.cam.camcmd(v, v2)
            if r is None:
                self._json({"sent": v, "blocked": True,
                            "why": "该命令不在安全白名单内（本工具永不发送关机/上传/升级/格式化类命令）"})
            else:
                self._json({"sent": v, "blocked": False, "reply": r.strip()[:200]})
            return

        if p == "/api/ctrl":
            t = (q.get("type") or [""])[0]
            v = (q.get("value") or [None])[0]
            v2 = (q.get("value2") or [None])[0]
            r = self.cam.camctrl(t, v, v2)
            if r is None:
                self._json({"sent": t, "value": v, "blocked": True,
                            "why": "该 camctrl 类型不在安全白名单内"})
            else:
                self._json({"sent": t, "value": v, "blocked": False, "reply": r.strip()[:200]})
            return

        if p == "/api/access":
            # ★★★ 重要：绝不在这里重发 req_acc！
            #     每次 req_acc 都会在相机上产生一条"待批准"消息 ⇒ 会话退回受限模式
            #     ⇒ camctrl（触摸对焦等）会全部 err_busy。
            #     所以 req_acc 只在【服务启动时发一次】，之后只读状态。
            # ★ 谁连着相机？（capability 里的 appname 就是当前连接的 App 名）
            cap = self.cam.getinfo("capability")
            import re as _re
            am = _re.search(r"<appname>([^<]*)</appname>", cap or "")
            mm = _re.search(r"<modelname>([^<]*)</modelname>", cap or "")
            appname = (am.group(1) if am else "?")
            # ★ 只有【确实读到了】一个非官方 App 名时才报警；未知(?)不算
            known_ok = ("lumix_sync", "lumixtether", "s5monitor", "", "?")
            others = bool(appname.strip()) and appname.strip().lower() not in known_ok
            self._json({
                "current_app_on_camera": appname,
                "modelname": mm.group(1) if mm else "?",
                "other_app_connected": bool(others),
                "mode": self.cam.access_mode,
                "raw": self.cam.access_raw,
                "fields": self.cam.access_fields,
                "camctrl_expected": self.cam.access_mode == "ok",
                "hint": (("⚠️ 相机上当前连接的 App 是【%s】—— 可能是它占着实时控制通道" % appname)
                         if others else
                         ("✅ 完整授权（camctrl 应可用）" if self.cam.access_mode == "ok"
                          else "⚠️ 受限授权 —— 请在【相机屏幕上】点「允许/是」批准连接")),
            })
            return

        if p == "/api/ctrltest":
            import re as _re
            if q.get("auto") and self.cam.auto_ctrl_test:
                res = [{"what": w, "code": c} for w, c in self.cam.auto_ctrl_test]
                ok = sum(1 for x in res if x["code"] == "ok")
                self._json({"results": res, "ok": ok, "total": len(res),
                            "hint": ("✅ 启动时自检通过（camctrl 可用）" if ok else
                                     "❌ 启动时自检未通过；注意：本端点若反复调用会发 req_acc 而破坏会话")})
                return
            out = []
            seq = [
                ("camcmd recmode",        "cmd",  "recmode",        None),
                ("camctrl touch 中心",    "ctrl", "touch",         ("320/216", "on")),
                ("camctrl touch 释放",    "ctrl", "touch",         ("0/0", "off")),
                ("camctrl touchaf_chg_pos","ctrl","touchaf_chg_pos",("400/300", None)),
                ("camctrl touchaf_chg_area","ctrl","touchaf_chg_area",("up", None)),
                ("camctrl af_ae_lock on", "ctrl", "af_ae_lock",    ("on", None)),
                ("camctrl af_ae_lock off","ctrl", "af_ae_lock",    ("off", None)),
                ("camcmd tele-normal",    "cmd",  "tele-normal",   None),
                ("camcmd wide-normal",    "cmd",  "wide-normal",   None),
            ]
            for label, kind, name, params in seq:
                if kind == "cmd":
                    r = self.cam.camcmd(name, retries=1)      # ★ 自检不重试，快速返回
                else:
                    v, v2 = params
                    r = self.cam.camctrl(name, v, v2, retries=1)
                if r is None:
                    code = "blocked"
                elif not r:
                    code = "no-reply"
                else:
                    m = _re.search(r"<result>([^<]*)</result>", r)
                    code = m.group(1) if m else r.strip()[:40]
                out.append({"what": label, "code": code})
                time.sleep(3.0)          # ★ 放慢：实测 camctrl 连发必 busy
            ok = sum(1 for x in out if x["code"] == "ok")
            self._json({"results": out, "ok": ok, "total": len(out),
                        "hint": ("✅ 全部可用" if ok == len(out) else
                                 "❌ 有失败项。若多为 err_reject/err_busy ⇒ "
                                 "① 在相机屏幕上点一下唤醒实时取景 ② 或重启相机后再试")})
            return

        if p == "/api/diag":
            b = self.bridge
            try:
                qlen = len(b.q)
            except Exception:
                qlen = -1
            agg = {}
            for k, v in b.rx_gaps.items():
                agg["%d00-%d00ms" % (k, k + 1)] = v
            self._json({
                "summary": {
                    "frames_received": b.frame_id,
                    "fps_now": round(b.fps, 1),
                    "pacing_mode": b.pacing_mode,
                    "pacing_fps_fixed": (b.pacing_fps_fixed if b.pacing_mode == "fixed" else None),
                    "pacing_fps_adaptive": b.pacing_fps,
                    "fixed_keep": (FIXED_KEEP if b.pacing_mode == "fixed" else None),
                    "frames_thinned": b.thinned,
                    "camera_arrival_fps": round(b.arrival_fps, 1),
                    "queue_reserve": b.queue_reserve,
                    "est_latency_ms": int(1000.0 * b.queue_reserve / max(1.0, b.pacing_fps)),
                    "frames_dropped_queue_full": b.dropped,
                    "pacing_underrun": b.underrun,
                    "max_camera_gap_ms": b.max_gap_ms,
                    "smooth_mode": ("官方模式 固定%.0ffps 取最新%d帧" % (b.pacing_fps_fixed, FIXED_KEEP)
                                    if b.pacing_mode == "fixed" else
                                    "自适应 buffer=%d帧 target=%d帧" % (PACING_BUF, RESERVE_TARGET)),
                    "http_slow_writes": b.http_slow,
                    "queue_len": qlen,
                    "keepalive_sec": b.keepalive,
                    "ssdp_sent": getattr(Handler, "ssdp_sent", 0),
                    "cam_latency_ms": b.cam_busy_ms,
                },
                "camera_gap_histogram": agg,
                "recent_stalls": list(b.stalls)[-40:],
                "verdict": (
                    "✅ 服务端与相机侧均无卡顿（抖动 <50ms）" if b.max_gap_ms < 150
                    else "⚠️ 相机侧有 %d ms 空档 → 突发式推流，已由节奏器垫帧抹平" % b.max_gap_ms
                ),
            })
            return

        if p == "/api/mode":
            m = (q.get("value") or ["rec"])[0]
            if m == "play":
                # ★ 官方顺序：先停流，再切回放（回放模式没有实时取景）
                self.bridge.pause()
                r = self.cam.camcmd("playmode")
                self._json({"mode": "play", "reply": (r or "").strip()[:120],
                            "note": "回放模式无实时取景，画面已冻结"})
            else:
                r = self.cam.camcmd("recmode")
                time.sleep(0.6)
                self.bridge.resume()
                self._json({"mode": "rec", "reply": (r or "").strip()[:120]})
            return

        if p == "/api/stream":
            act = (q.get("action") or ["start"])[0]
            if act == "start":
                self.bridge.start()
            else:
                self.bridge.stop()
            self._json({"action": act, "running": self.bridge.running})
            return

        if p == "/api/info":
            t = (q.get("type") or ["capability"])[0]
            self._json({"type": t, "reply": self.cam.getinfo(t)[:2000]})
            return

        if p == "/api/setting":
            t = (q.get("type") or [""])[0]
            if "value" in q:
                self._json({"set": t, "reply": self.cam.setsetting(t, q["value"][0]).strip()[:200]})
            else:
                self._json({"get": t, "reply": self.cam.getsetting(t)[:2000]})
            return

        self._send(404, "text/plain", b"not found")

    def do_POST(self):
        self.do_GET()

    # ---- MJPEG 推送 ----
    def _mjpeg(self):
        try:
            self.connection.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)   # ★ 关 Nagle
        except Exception:
            pass
        self.send_response(200)
        self.send_header("Age", "0")
        self.send_header("Cache-Control", "no-cache, private")
        self.send_header("Pragma", "no-cache")
        self.send_header("Content-Type",
                         "multipart/x-mixed-replace; boundary=frame")
        self.end_headers()
        last = -1
        try:
            while True:
                fid, jpg = self.bridge.wait_frame(last, timeout=10.0)
                if jpg is None:
                    # 还没首帧：发个占位，避免浏览器卡住
                    time.sleep(0.2)
                    continue
                last = fid
                import time as _t
                _w0 = _t.time()
                # ★ 单次 write：减少 syscall 与分片
                self.wfile.write(BOUNDARY
                                 + b"Content-Type: image/jpeg\r\n"
                                 + b"Content-Length: %d\r\n\r\n" % len(jpg)
                                 + jpg + b"\r\n")
                _dt = (_t.time() - _w0) * 1000
                if _dt > 200:
                    self.bridge.http_slow += 1
                    self.bridge.stalls.append({
                        "t": _t.strftime("%H:%M:%S"), "kind": "★下发慢",
                        "ms": int(_dt),
                        "detail": "向浏览器写一帧耗时过长（链路/浏览器侧）"})
        except (BrokenPipeError, ConnectionResetError):
            pass
        except Exception:
            pass


# ---------------------------------------------------------------- 入口

def main():
    ap = argparse.ArgumentParser(description="DC-S5 wireless monitor (official logic replica)")
    ap.add_argument("--host", default=DEFAULT_HOST, help="相机 IP（默认 SoftAP 网关 192.168.54.1）")
    ap.add_argument("--port", type=int, default=8080, help="本机 HTTP 端口（默认 8080）")
    ap.add_argument("--udp", type=int, default=UDP_PORT, help="取景流 UDP 端口（49152-65535）")
    ap.add_argument("--device-id", default=DEFAULT_DEVICE_ID)
    ap.add_argument("--device-name", default=DEFAULT_DEVICE_NAME)
    ap.add_argument("--no-stream", action="store_true", help="不自动开始取景")
    ap.add_argument("--pacing-mode", choices=["fixed", "adaptive"], default=PACING_MODE,
                    help="fixed=官方风格固定帧率取最新帧(默认)；adaptive=队列反馈控制")
    ap.add_argument("--pacing-fps", type=float, default=PACING_FPS,
                    help="fixed 模式下的输出帧率（默认 18，官方标准）")
    ap.add_argument("--keepalive", type=float, default=KEEPALIVE_SEC,
                    help="心跳间隔秒（默认 10，实测最优；0=关闭会约 13 秒后停流）")
    a = ap.parse_args()

    www = os.path.join(os.path.dirname(os.path.abspath(__file__)), "www")
    cam = Lumix(a.host, a.device_id, a.device_name)
    bridge = StreamBridge(cam, a.udp, keepalive=a.keepalive,
                          pacing_mode=a.pacing_mode, pacing_fps=a.pacing_fps)

    print("=" * 62)
    print(" DC-S5 无线监看  (官方逻辑复刻)")
    print("=" * 62)
    print(" 相机      : %s" % a.host)
    print(" 取景流    : UDP %d" % a.udp)
    print(" 身份      : %s / %s" % (a.device_id, a.device_name))
    print(" 节奏模式  : %s%s" % (a.pacing_mode,
          ("  固定 %.0f fps（官方 640p 标准）" % a.pacing_fps) if a.pacing_mode == "fixed" else ""))
    print("-" * 62)
    print(" 打开浏览器：  http://<本机IP>:%d" % a.port)
    print(" （iPhone/iPad/Android/电脑均可，无需装 App）")
    print("=" * 62)

    ssdp = SSDPAdvertiser(a.device_id, a.port)
    ssdp.start()                       # ★ 官方 App 的 "alive" 上报

    Handler.cam = cam
    Handler.bridge = bridge
    Handler.www = www
    # ★ 端口占用时给出清晰提示（而不是直接抛 traceback）
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", a.port), Handler)
    except OSError as e:
        if getattr(e, "errno", None) == 48:
            import subprocess
            who = ""
            try:
                out = subprocess.run(["lsof", "-nP", "-iTCP:%d" % a.port, "-sTCP:LISTEN"],
                                     capture_output=True, text=True, timeout=5).stdout
                who = "\n".join(out.splitlines()[1:4])
            except Exception:
                pass
            print()
            print("=" * 62)
            print(" ❌ 端口 %d 已被占用 —— 多半是上一次的 s5monitor 还在跑。" % a.port)
            if who:
                print(" 占用者：")
                for l in who.splitlines():
                    print("   " + l.strip()[:100])
            print()
            print(" 解决办法（任选其一）：")
            print("   ① 干掉旧实例：  pkill -9 -f s5monitor.py")
            print("   ② 或换个端口：  ./run.sh 192.168.1.131 8090")
            print("=" * 62)
            raise SystemExit(1)
        raise

    # ★ 先把 HTTP 服务跑起来，配对/等待批准放到后台线程 ——
    #   否则"等待批准"期间浏览器打不开（之前的 UX 问题）
    def _bringup():
        print("[ 1/3] 配对（accctrl req_acc，只发一次）…")
        cam.ensure_access()
        print("[ 2/3] 切拍摄模式（camcmd recmode）…")
        cam.camcmd("recmode")
        # ★★★ 批准后【立刻】自动测一次 camctrl ——
        #     关键：此后绝不再发 req_acc（重发会把会话打回受限模式）
        if cam.access_mode == "ok":
            print("[ 3/4] 已获完整授权 ⇒ 自动自检 camctrl（此后不再重发 req_acc）…")
            import re as _re
            res = []
            for label, fn in [
                ("camctrl af_ae_lock on",  lambda: cam.camctrl("af_ae_lock", "on", retries=1)),
                ("camctrl af_ae_lock off", lambda: cam.camctrl("af_ae_lock", "off", retries=1)),
                ("camctrl touch 320/216",  lambda: cam.camctrl("touch", "320/216", "on", retries=1)),
                ("camctrl touch 0/0 off",  lambda: cam.camctrl("touch", "0/0", "off", retries=1)),
                ("camctrl touchaf_chg_pos", lambda: cam.camctrl("touchaf_chg_pos", "400/300", retries=1)),
            ]:
                r = fn() or ""
                m = _re.search(r"<result>([^<]*)</result>", r)
                code = m.group(1) if m else "?"
                res.append((label, code))
                print("        %s %-28s %s" % ("✅" if code == "ok" else "❌", label, code))
                time.sleep(3.0)
            okn = sum(1 for _, c in res if c == "ok")
            print("        ⇒ camctrl 自检 %d/%d" % (okn, len(res)))
            if okn:
                print("        ✅ camctrl 可用！（请在浏览器里试触摸对焦）")
            else:
                print("        ❌ camctrl 仍被拒 —— 门控不在会话层，需继续排查")
            cam.auto_ctrl_test = res
        else:
            cam.auto_ctrl_test = []
        if not a.no_stream:
            print("[ 4/4] 请求取景流（startstream）…")
            bridge.start()
        print("=" * 62)
        print(" 就绪。若 camctrl 类功能报 err_busy/err_reject，")
        print(" 请在相机屏幕上点「允许」后重新点界面上的 🧪 控制自检。")
        print("=" * 62)

    threading.Thread(target=_bringup, daemon=True).start()

    def _cleanup(*_):
        print("\n退出：停流…")
        bridge.stop()
        time.sleep(0.5)
        try:
            cam.stop_stream()
        except Exception:
            pass
        os._exit(0)
    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n退出：停流…")
    finally:
        bridge.stop()
        time.sleep(0.5)
        try:
            cam.stop_stream()
        except Exception:
            pass
        srv.server_close()


if __name__ == "__main__":
    main()
    ssdp = SSDPAdvertiser(a.device_id, a.port)
    ssdp.start()                       # ★ 官方 App 的 "alive" 上报

    Handler.cam = cam
    Handler.bridge = bridge
    Handler.www = www
    # ★ 端口占用时给出清晰提示（而不是直接抛 traceback）
    try:
        srv = ThreadingHTTPServer(("0.0.0.0", a.port), Handler)
    except OSError as e:
        if getattr(e, "errno", None) == 48:
            import subprocess
            who = ""
            try:
                out = subprocess.run(["lsof", "-nP", "-iTCP:%d" % a.port, "-sTCP:LISTEN"],
                                     capture_output=True, text=True, timeout=5).stdout
                who = "\n".join(out.splitlines()[1:4])
            except Exception:
                pass
            print()
            print("=" * 62)
            print(" ❌ 端口 %d 已被占用 —— 多半是上一次的 s5monitor 还在跑。" % a.port)
            if who:
                print(" 占用者：")
                for l in who.splitlines():
                    print("   " + l.strip()[:100])
            print()
            print(" 解决办法（任选其一）：")
            print("   ① 干掉旧实例：  pkill -9 -f s5monitor.py")
            print("   ② 或换个端口：  ./run.sh 192.168.1.131 8090")
            print("=" * 62)
            raise SystemExit(1)
        raise
    def _cleanup(*_):
        print("\n退出：停流…")
        bridge.stop()
        time.sleep(0.5)
        try:
            cam.stop_stream()
        except Exception:
            pass
        os._exit(0)
    signal.signal(signal.SIGINT, _cleanup)
    signal.signal(signal.SIGTERM, _cleanup)

    try:
        srv.serve_forever()
    except KeyboardInterrupt:
        print("\n退出：停流…")
    finally:
        bridge.stop()
        time.sleep(0.5)
        try:
            cam.stop_stream()
        except Exception:
            pass
        srv.server_close()


if __name__ == "__main__":
    main()
