#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_ap_probe.py — 从"相机热点(SoftAP)侧"对 DC-S5 做只读取证。

用 01_研究报告_全集/17_相机热点与蓝牙Windows侧勘察_20261013.md 提供的线索：
  - 相机热点 SSID = S5-XXXXXX，**开放网络（无加密）**
  - 预期网关：相机自身（实测拿到 IP 后自动判定）

目的（回答三个问题）：
  Q1 开放热点是否等价于开放控制面？—— cam.cgi 在没有做过任何 App/accctrl 握手时是否应答
  Q2 User-Agent: LUMIX Sync 是否仍是唯一"门槛"（伪造即通 = 无认证）
  Q3 是否可 CSRF —— 纯 GET + 外部 Referer/Origin 是否仍执行

红线：除一次可逆的 camcmd 模式切换（用于证明"无认证控制"）外，不做任何写入。
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
OUT = {}
LOG = []


def say(s):
    print(s, flush=True)
    LOG.append(s)


def http(url, ua=UA, extra=None, timeout=8, read=600):
    hdr = {}
    if ua:
        hdr["User-Agent"] = ua
    if extra:
        hdr.update(extra)
    try:
        req = urllib.request.Request(url, headers=hdr)
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read(read)
    except urllib.error.HTTPError as e:
        return e.code, e.read(read)
    except Exception as e:
        return None, str(e).encode()


def brief(b, n=200):
    try:
        s = b.decode("utf-8", "replace")
    except Exception:
        return repr(b[:n])
    return re.sub(r"\s+", " ", s.strip())[:n]


def find_camera(candidates):
    say("== 寻找相机（cam.cgi getstate） ==")
    for ip in candidates:
        st, b = http("http://%s/cam.cgi?mode=getstate" % ip, timeout=4)
        say("  %-16s -> %s | %s" % (ip, st, brief(b, 90)))
        if st == 200 and b"camrply" in b:
            return ip
    return None


def portscan(ip, ports):
    say("== 端口扫描 %s ==" % ip)

    def t(p):
        s = socket.socket()
        s.settimeout(0.6)
        try:
            s.connect((ip, p))
            return p
        except Exception:
            return None
        finally:
            s.close()

    with ThreadPoolExecutor(max_workers=120) as ex:
        hits = [p for p in ex.map(t, ports) if p]
    say("  开放: %s" % (hits if hits else "(无)"))
    return hits


def main():
    if len(sys.argv) < 2:
        print("usage: s5_ap_probe.py <out.json> [camera_ip]")
        return 2
    outfile = sys.argv[1]
    cam = sys.argv[2] if len(sys.argv) > 2 else None

    say("### S5 SoftAP 侧只读取证 @ %s" % time.strftime("%Y-%m-%d %H:%M:%S"))

    if not cam:
        cam = find_camera(["192.168.54.1", "192.168.0.1", "10.0.0.1",
                           "172.16.0.1", "192.168.1.1", "192.168.4.1", "192.168.8.1"])
    if not cam:
        say("!! 未找到 cam.cgi")
        json.dump({"log": LOG}, open(outfile, "w"), ensure_ascii=False, indent=2)
        return 1
    say("== 相机 = %s ==" % cam)
    OUT["camera_ip"] = cam

    base = "http://%s/cam.cgi" % cam

    # ---- Q2: User-Agent 是否是唯一门槛 ----
    say("\n== Q2: UA 门槛测试 ==")
    for label, ua in [("带 UA(LUMIX Sync)", UA), ("不带 UA", None),
                      ("伪造其他 UA(Chrome)", "Mozilla/5.0")]:
        st, b = http(base + "?mode=getstate", ua=ua, timeout=6)
        say("  %-22s -> HTTP %s | %s" % (label, st, brief(b, 80)))
        OUT["ua_%s" % label] = brief(b, 200)

    # ---- Q1: 未做任何握手，只读端点是否可用 ----
    say("\n== Q1: 只读端点(未做任何 App 握手) ==")
    reads = [
        ("getinfo capability", "mode=getinfo&type=capability"),
        ("getinfo allmenu", "mode=getinfo&type=allmenu"),
        ("getinfo curmenu", "mode=getinfo&type=curmenu"),
        ("getinfo lens", "mode=getinfo&type=lens"),
        ("getsetting videoformat", "mode=getsetting&type=videoformat"),
        ("getsetting ntcs_pal", "mode=getsetting&type=ntcs_pal"),
        ("accctrl req_acc", "mode=accctrl&type=req_acc"),
        ("camctrl", "mode=camctrl&type=startstream"),
    ]
    for name, q in reads:
        st, b = http(base + "?" + q, timeout=8, read=400)
        say("  %-24s -> HTTP %s | %s" % (name, st, brief(b, 110)))
        OUT[name] = brief(b, 400)

    # ---- Q3: CSRF —— 外部来源头是否被拦截 ----
    say("\n== Q3: CSRF（外部 Referer/Origin） ==")
    evil = {"Referer": "http://evil.example/attack.html",
            "Origin": "http://evil.example"}
    st, b = http(base + "?mode=getstate", extra=evil, timeout=6)
    say("  带外部 Referer/Origin -> HTTP %s | %s" % (st, brief(b, 80)))
    OUT["csrf_getstate"] = brief(b, 200)
    st, b = http(base + "?mode=getinfo&type=lens", extra=evil, timeout=6)
    say("  带外部头读 lens        -> HTTP %s | %s" % (st, brief(b, 80)))
    OUT["csrf_lens"] = brief(b, 200)

    # ---- 无认证控制测试（可逆：切 play 再切回 rec） ----
    say("\n== 无认证控制测试（可逆模式切换） ==")
    st, b = http(base + "?mode=camcmd&value=playmode", timeout=8)
    say("  camcmd playmode (无任何握手/凭据) -> HTTP %s | %s" % (st, brief(b, 90)))
    OUT["camcmd_playmode"] = brief(b, 200)
    time.sleep(2)
    st, b = http(base + "?mode=camcmd&value=recmode", timeout=8)
    say("  camcmd recmode (复位)             -> HTTP %s | %s" % (st, brief(b, 90)))
    OUT["camcmd_recmode"] = brief(b, 200)

    # ---- 端口扫描 ----
    say("")
    OUT["open_ports"] = portscan(cam, list(range(1, 1025)) + [5000, 6060, 8080, 8443, 9000, 50001, 60606])

    # ---- 全量配置块下载（只读） ----
    say("\n== 全量 camsetting 下载（65,533 B） ==")
    try:
        st, b = http(base + "?mode=startsenddata&type=camsetting&value=65533", timeout=15, read=2000)
        say("  startsenddata -> HTTP %s | %s" % (st, brief(b, 160)))
        OUT["startsenddata"] = brief(b, 400)
        m = re.search(rb"bufsize>(\d+)", b)
        size = int(m.group(1)) if m else 0
        payload = b""
        chunk = size - 268 if size > 268 else 61460 - 268
        got = 0
        while got < size:
            need = min(chunk, size - got)
            st, d = http(base + "?mode=requestsenddata&value=%d" % need, timeout=90, read=need + 64)
            if st != 200 or not d:
                say("  requestsenddata 失败 @%d" % got)
                break
            payload += d
            got = len(payload)
            say("    got %d / %d" % (got, size))
        st, b2 = http(base + "?mode=endsenddata", timeout=15, read=500)
        say("  endsenddata -> %s" % brief(b2, 100))
        if payload:
            open(outfile + ".camsetting.bin", "wb").write(payload)
            say("  已保存 %d B -> %s.camsetting.bin" % (len(payload), outfile))
            OUT["camsetting_len"] = len(payload)
    except Exception as e:
        say("  下载异常: %s" % e)

    json.dump({"log": LOG, "results": OUT}, open(outfile, "w"),
              ensure_ascii=False, indent=2)
    say("\n== 取证完成 -> %s ==" % outfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
