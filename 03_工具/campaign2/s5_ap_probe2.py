#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_ap_probe2.py — SoftAP 侧第二轮：访问控制握手 + 新端口深挖。

第一轮结论（out/s5_ap/ap_probe.log）：
  - macOS 能连上相机热点（192.168.54.10 / gw 192.168.54.1）→ Windows MT7921 连不上是主机侧问题
  - 除 accctrl 外所有端点返回 err_critical → API 被访问控制门挡住
  - accctrl req_acc 返回 ok_under_research,S5-XXXXXX,remote,**open**（家网侧是 encrypted）
  - 端口：80 / 50001 / 60606（家网侧只有 80）

本轮：
  1) accctrl req_acc_g（只读，取 32 字节握手密钥）
  2) accctrl req_acc(value=uuid, value2=name) → 请求访问 → 复测读端点
  3) accctrl req_acc_can(value=uuid) → 清理 pending
  4) 50001 / 60606 服务识别（HTTP 头、banner、常见路径）
  5) 全端口扫描 1-65535
"""
import json
import re
import socket
import sys
import time
import urllib.request
import urllib.error
from concurrent.futures import ThreadPoolExecutor

UA = "LUMIX Sync"
LOG = []
OUT = {}


def say(s):
    print(s, flush=True)
    LOG.append(s)


def http(url, ua=UA, timeout=8, read=800, method="GET"):
    hdr = {"User-Agent": ua} if ua else {}
    try:
        req = urllib.request.Request(url, headers=hdr, method=method)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read(read)
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers), e.read(read)
    except Exception as e:
        return None, {}, str(e).encode()


def brief(b, n=200):
    try:
        s = b.decode("utf-8", "replace")
    except Exception:
        return repr(b[:n])
    return re.sub(r"\s+", " ", s.strip())[:n]


def main():
    if len(sys.argv) < 2:
        print("usage: s5_ap_probe2.py <out.json> [cam_ip]")
        return 2
    outfile = sys.argv[1]
    cam = sys.argv[2] if len(sys.argv) > 2 else "192.168.54.1"
    base = "http://%s/cam.cgi" % cam
    say("### SoftAP 第二轮 @ %s  cam=%s" % (time.strftime("%F %T"), cam))

    # ---- 0. 基线 ----
    st, _, b = http(base + "?mode=getstate", timeout=6)
    say("[0] getstate -> %s" % brief(b, 120))
    st, _, b = http(base + "?mode=accctrl&type=req_acc", timeout=6)
    say("[0] accctrl req_acc -> %s" % brief(b, 120))
    OUT["baseline_accctrl"] = brief(b, 200)

    # ---- 1. req_acc_g：只读取握手密钥 ----
    say("\n[1] accctrl req_acc_g（只读，取握手密钥）")
    st, h, b = http(base + "?mode=accctrl&type=req_acc_g", timeout=8, read=2000)
    say("    HTTP %s | %s" % (st, brief(b, 300)))
    if b and len(b) > 20:
        hx = b.decode("utf-8", "replace").strip()
        say("    原始长度 %d" % len(hx))
        OUT["req_acc_g"] = brief(b, 2000)

    # ---- 2. req_acc：请求访问 ----
    uuid = "4D454930-0100-1000-8001-%012x" % int(time.time() * 1000) % (1 << 48) if False else \
           "4D454930-0100-1000-8001-%012x" % (int(time.time()) & 0xFFFFFFFFFFFF)
    say("\n[2] accctrl req_acc  value=%s value2=MacProbe" % uuid)
    q = "mode=accctrl&type=req_acc&value=%s&value2=MacProbe" % uuid
    st, _, b = http(base + "?" + q, timeout=10, read=1000)
    say("    HTTP %s | %s" % (st, brief(b, 200)))
    OUT["req_acc_request"] = brief(b, 300)

    for i in (1, 2, 3):
        time.sleep(3)
        st, _, b2 = http(base + "?mode=accctrl&type=req_acc", timeout=6)
        say("    +%ds 后 req_acc 状态 -> %s" % (i * 3, brief(b2, 120)))

    # ---- 3. 请求后复测读端点 ----
    say("\n[3] 请求访问后复测读端点")
    for name, qq in [("getstate", "mode=getstate"),
                     ("getinfo capability", "mode=getinfo&type=capability"),
                     ("getinfo lens", "mode=getinfo&type=lens"),
                     ("getsetting videoformat", "mode=getsetting&type=videoformat"),
                     ("startsenddata", "mode=startsenddata&type=camsetting&value=65533")]:
        st, _, b3 = http(base + "?" + qq, timeout=10, read=500)
        say("    %-24s -> %s" % (name, brief(b3, 130)))
        OUT["post_" + name] = brief(b3, 300)

    # ---- 4. 清理 pending ----
    say("\n[4] accctrl req_acc_can（清理 pending）")
    st, _, b = http(base + "?mode=accctrl&type=req_acc_can&value=%s&value2=" % uuid, timeout=8)
    say("    HTTP %s | %s" % (st, brief(b, 150)))

    # ---- 5. 新端口服务识别 ----
    say("\n[5] 新端口服务识别")
    for port in (50001, 60606):
        say("  -- port %d --" % port)
        # banner
        try:
            s = socket.create_connection((cam, port), timeout=3)
            s.settimeout(3)
            try:
                s.sendall(b"GET / HTTP/1.0\r\nHost: %s\r\n\r\n" % cam.encode())
                data = s.recv(1200)
            except Exception:
                data = b""
            s.close()
            say("     HTTP/raw: %s" % brief(data, 400))
            OUT["port%d_raw" % port] = brief(data, 800)
        except Exception as e:
            say("     连接失败: %s" % e)
        for path in ("/", "/index.html", "/rootDesc.xml", "/description.xml",
                     "/upnp/control/content_directory", "/cgi-bin/magicBox.cgi?action=getDeviceInfo"):
            url = "http://%s:%d%s" % (cam, port, path)
            st, h, b = http(url, timeout=4, read=500)
            if st:
                key = "port%d%s" % (port, path.replace("/", "_"))
                OUT[key] = {"status": st, "server": h.get("Server", ""),
                            "body": brief(b, 300)}
                say("     %-46s -> %s | Server=%s | %s"
                    % (path, st, h.get("Server", "-"), brief(b, 120)))

    # ---- 6. 全端口扫描 ----
    say("\n[6] 全端口扫描 1-65535（并行）")

    def t(p):
        s = socket.socket()
        s.settimeout(0.5)
        try:
            s.connect((cam, p))
            return p
        except Exception:
            return None
        finally:
            s.close()

    with ThreadPoolExecutor(max_workers=600) as ex:
        hits = [p for p in ex.map(t, range(1, 65536)) if p]
    say("    开放端口: %s" % hits)
    OUT["all_open_ports"] = hits

    json.dump({"log": LOG, "results": OUT}, open(outfile, "w"),
              ensure_ascii=False, indent=2)
    say("\n### 第二轮完成 -> %s" % outfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
