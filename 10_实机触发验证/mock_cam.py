#!/usr/bin/env python3
"""
mock_cam.py —— DC-S5 离线靶机（无相机时验证整条 fuzz/复现流水线）

为什么需要它：
  · 14:52:34 那次会话是**完全可用**的（getstate=ok + dlna 200），却因为 repro_crash.py
    自身的一个 bug（bytes.encode）在第一个用例就崩了 —— 会话白白浪费。
  · 相机不在线时（如 2026-10-16 15:48 已完全离线），无法回归验证工具链。
  ⇒ 本地用 127.0.0.1 起一个"行为等价的假相机"：同样接受 :801 的 cam.cgi 与 :60606 的
    dlna SOAP，并按需**注入故障**（INT32_MAX 触发连接复位 / dlna 进程死 / 静默 403），
    用来回归验证 repro_crash.py 的三通道分类、崩溃落盘、恢复等待，以及 fuzz 全家桶。

实现的是**协议形状与状态机**（不是相机固件行为）：
  cam.cgi :  getstate / accctrl(req_acc,req_acc_can) / camcmd&value=playmode /
             getinfo[&type=capability|allmenu] / getcurmenu / getsetting
  dlna    :  POST /Server0/CDS_control → 未握手=403；已握手=200 + BrowseResponse XML
  50001   :  只开 TCP（供 tcp_alive 判据）

故障注入：
  --crash-on-intmax     body 含 StartingIndex=2147483647 时：不回包直接 RST，并让 dlna 端口
                        进入"死"状态（cam.cgi 仍活）⇒ 触发 repro_crash 的 DLNA_DOWN 分类
  --crash-on-intmax-hard 同上但连 cam.cgi 也 shutdown ⇒ 触发 CRASH 分类
  --silence-403 N      距上次 dlna 请求超过 N 秒后强制 403（复刻 14:52 的"静默即死"）
  --no-accctrl-ok      req_acc 一律回 ok_under_research_no_msg（复刻 15:09 的现象）

用法：
  python3 mock_cam.py --http-port 18080 --dlna-port 16066 --img-port 15001 --crash-on-intmax
  # 另一个终端（端口用环境变量对齐）：
  S5_HTTP_PORT=18080 S5_DLNA_PORT=16066 S5_IMG_PORT=15001 python3 handshake.py 127.0.0.1
"""
import argparse
import socket
import threading
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

STATE = {
    "armed": False,          # 是否已在"等待WiFi连接"状态
    "paired": False,         # 是否已配对（getstate=ok）
    "req_acc_seen": 0,
    "last_dlna": 0.0,
    "dlna_dead": False,
    "dlna_dead_hard": False,
    "accctrl_ok": True,
    "silence_403": 0,
    "crash_on_intmax": False,
    "crash_on_intmax_hard": False,
    "log": [],
}

BROWSE_RESP = (
    '<?xml version="1.0"?><s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/">'
    '<s:Body><u:BrowseResponse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">'
    "<Result>&lt;DIDL-Lite&gt;&lt;/DIDL-Lite&gt;</Result><NumberReturned>0</NumberReturned>"
    "<TotalMatches>0</TotalMatches><UpdateID>1</UpdateID>"
    "</u:BrowseResponse></s:Body></s:Envelope>"
)


def camrply(result):
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<camrply><result>%s</result></camrply>' % result).encode()


class CamHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def _send(self, code, body, ctype="text/xml"):
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Connection", "close")
        self.end_headers()
        try:
            self.wfile.write(body)
        except Exception:
            pass

    def do_GET(self):
        q = self.path.split("/cam.cgi?", 1)[-1] if "cam.cgi" in self.path else self.path.lstrip("/")
        STATE["log"].append(("cam", q, self.headers.get("User-Agent")))
        p = dict()
        for kv in q.split("&"):
            if "=" in kv:
                k, v = kv.split("=", 1)
                p.setdefault(k, v)
        mode = p.get("mode", "")
        typ = p.get("type", "")

        if mode == "getstate":
            return self._send(200, camrply("ok" if STATE["paired"] else "err_critical"))
        if mode == "accctrl":
            if typ == "req_acc":
                STATE["req_acc_seen"] += 1
                if STATE["req_acc_seen"] > 1:
                    return self._send(200, camrply("err_others_requesting"))
                if not STATE["accctrl_ok"]:
                    return self._send(200, camrply("ok_under_research_no_msg"))
                STATE["paired"] = True
                return self._send(200, ("<?xml version=\"1.0\"?><camrply><result>ok</result>"
                                        "<uuid>%s</uuid><type>remote</type><state>open</state>"
                                        "</camrply>" % p.get("value", ""))[:200].encode())
            if typ == "req_acc_can":
                STATE["paired"] = False
                return self._send(200, camrply("ok"))
            return self._send(200, camrply("err_param"))
        if mode == "camcmd":
            if p.get("value") == "playmode" and STATE["paired"]:
                STATE["armed"] = True
                return self._send(200, camrply("ok"))
            return self._send(200, camrply("err_critical" if not STATE["paired"] else "ok"))
        if mode == "getinfo":
            if typ == "capability":
                return self._send(200, (
                    '<?xml version="1.0" encoding="UTF-8"?>\n<camrply><result>ok</result>'
                    '<contents_action_info model="DC-S5" version="1.0" date="20130723">'
                    '<functablist version="1.0" date="20131017">'
                    '<func id="photo_style" enable="yes" func_type="sp_embeded_ph_sty11"/>'
                    "</functablist></contents_action_info></camrply>").encode())
            return self._send(200, (
                '<?xml version="1.0" encoding="UTF-8"?>\n<camrply><result>ok</result>'
                "<productinfo><modelname>DC-S5</modelname><modelNumber>MC801</modelNumber>"
                "</productinfo></camrply>").encode())
        if mode in ("getcurmenu", "getsetting"):
            return self._send(200, ('<?xml version="1.0" encoding="UTF-8"?>\n<camrply><result>ok</result>'
                                    "<menuinfo model=\"DC-S5\" version=\"2.0\"><mainmenu>"
                                    "<item id=\"menu_item_id_photo_style\" enable=\"yes\" value=\"std\"/>"
                                    "</mainmenu></menuinfo></camrply>").encode())
        return self._send(200, camrply("err_param"))


class DlnaHandler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, *a):
        pass

    def do_POST(self):
        n = int(self.headers.get("Content-Length") or 0)
        body = self.rfile.read(n) if n else b""
        STATE["log"].append(("dlna", self.path, self.headers.get("User-Agent"),
                             body[:80].decode("latin1", "replace")))
        # 静默即死（复刻 14:52：约 30s 无 dlna 活动 ⇒ 403 且不可恢复）
        gap = time.time() - STATE["last_dlna"]
        STATE["last_dlna"] = time.time()
        if STATE["silence_403"] and gap > STATE["silence_403"]:
            STATE["paired"] = False
        if STATE["dlna_dead_hard"] or not STATE["paired"]:
            resp = b"HTTP/1.1 403 Forbidden\r\nContent-Length: 0\r\nConnection: close\r\n\r\n"
            self.send_response if False else None
            try:
                self.wfile.write(resp)
            except Exception:
                pass
            return
        if STATE["dlna_dead"]:
            # 模拟 dlna 进程死：RST
            try:
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                           b"\x01\x00\x00\x00\x00\x00\x00\x00")
                self.connection.close()
            except Exception:
                pass
            return
        if STATE["crash_on_intmax"] and b"2147483647" in body:
            STATE["dlna_dead"] = True          # dlna 进程死（cam.cgi 仍活）
            try:
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                           b"\x01\x00\x00\x00\x00\x00\x00\x00")
                self.connection.close()
            except Exception:
                pass
            return
        if STATE["crash_on_intmax_hard"] and b"2147483647" in body:
            STATE["dlna_dead_hard"] = True
            STATE["paired"] = False
            try:
                self.connection.setsockopt(socket.SOL_SOCKET, socket.SO_LINGER,
                                           b"\x01\x00\x00\x00\x00\x00\x00\x00")
                self.connection.close()
            except Exception:
                pass
            return
        b = BROWSE_RESP.encode()
        self.send_response(200)
        self.send_header("Content-Type", 'text/xml; charset="utf-8"')
        self.send_header("EXT", "")
        self.send_header("Content-Length", str(len(b)))
        self.send_header("Connection", "close")
        self.end_headers()
        self.wfile.write(b)


class PlainTCP(threading.Thread):
    """50001 取图口：只接受 TCP 连接（给 tcp_alive 一个 'open'）。"""

    def __init__(self, port):
        super().__init__(daemon=True)
        self.port = port

    def run(self):
        s = socket.socket()
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(("127.0.0.1", self.port))
        s.listen(16)
        while True:
            try:
                c, _ = s.accept()
                c.settimeout(0.2)
                try:
                    c.recv(64)
                except Exception:
                    pass
                try:
                    c.sendall(b"HTTP/1.1 200 OK\r\nContent-Length: 0\r\nConnection: close\r\n\r\n")
                except Exception:
                    pass
                c.close()
            except Exception:
                break


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--http-port", type=int, default=18080)
    ap.add_argument("--dlna-port", type=int, default=16066)
    ap.add_argument("--img-port", type=int, default=15001)
    ap.add_argument("--crash-on-intmax", action="store_true")
    ap.add_argument("--crash-on-intmax-hard", action="store_true")
    ap.add_argument("--silence-403", type=int, default=0, help="dlna 静默超过 N 秒 → 403（0=关）")
    ap.add_argument("--no-accctrl-ok", action="store_true")
    ap.add_argument("--seconds", type=int, default=0, help="0 = 一直跑")
    a = ap.parse_args()

    STATE["crash_on_intmax"] = a.crash_on_intmax
    STATE["crash_on_intmax_hard"] = a.crash_on_intmax_hard
    STATE["silence_403"] = a.silence_403
    STATE["accctrl_ok"] = not a.no_accctrl_ok

    cam = ThreadingHTTPServer(("127.0.0.1", a.http_port), CamHandler)
    dlna = ThreadingHTTPServer(("127.0.0.1", a.dlna_port), DlnaHandler)
    for srv in (cam, dlna):
        srv.daemon_threads = True
    PlainTCP(a.img_port).start()
    threading.Thread(target=cam.serve_forever, daemon=True).start()
    threading.Thread(target=dlna.serve_forever, daemon=True).start()
    print("[mock] cam.cgi :%d  dlna :%d  img :%d   intmax=%s/%s silence403=%s accctrl_ok=%s"
          % (a.http_port, a.dlna_port, a.img_port, a.crash_on_intmax,
             a.crash_on_intmax_hard, a.silence_403, STATE["accctrl_ok"]), flush=True)
    if a.seconds:
        time.sleep(a.seconds)
    else:
        while True:
            time.sleep(3600)


if __name__ == "__main__":
    main()
