#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_ap_pair.py — 复现 LUMIX Sync 的 Wi-Fi 访问控制配对（SoftAP 侧）。

依据 APK 逆向（com/panasonic/jp/service/c.java:738-757、p168v5/a.java:U()/T()）：

  - app 的身份 UUID = "4D454930-0100-1000-8001-" + Dlna_UUID_Seed
    同一个 seed 也用于 BLE 侧写入的 DLNA_UUID_APS（H5/p.java:272 / 1515）
  - 链路为明文(open)  -> type=req_acc   ，UUID/名字原样
  - 链路为加密(encrypt)-> type=req_acc_e ，UUID/名字经 H5.s.b(str, key) 编码
                        key = req_acc_g 应答里第 2 个逗号字段（十六进制）
  - 端口 60606 上跑的是 "/Lumix/Server0/ddd"（p168v5/a.java:T()）

本脚本流程：
  0) 基线
  1) req_acc_g 各种变体（只读，取加密密钥）
  2) 60606 / 50001 服务探测（含 /Lumix/Server0/ddd）
  3) req_acc（明文）发起授权请求
  4) 轮询状态最长 150s —— 用户请在机身上点"允许"
  5) 一旦授权成功，立即复测读端点
  6) req_acc_can 清理
"""
import json
import re
import socket
import sys
import time
import urllib.request
import urllib.error

UA = "LUMIX Sync"
LOG = []
OUT = {}
UUID_SEED = "020000025AD6"          # 与项目既有记录一致的 seed（可换）
UUID = "4D454930-0100-1000-8001-" + UUID_SEED
NAME = "MacProbe"


def say(s):
    print(s, flush=True)
    LOG.append(s)


def http(url, timeout=10, read=800, ua=UA, method="GET", data=None, ctype=None):
    hdr = {"User-Agent": ua} if ua else {}
    if ctype:
        hdr["Content-Type"] = ctype
    try:
        req = urllib.request.Request(url, headers=hdr, method=method, data=data)
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
    outfile = sys.argv[1]
    cam = sys.argv[2] if len(sys.argv) > 2 else "192.168.54.1"
    base = "http://%s/cam.cgi" % cam
    say("### SoftAP 配对复现 @ %s   cam=%s" % (time.strftime("%F %T"), cam))
    say("    身份 UUID = %s   name = %s" % (UUID, NAME))

    # ---- 0 基线 ----
    st, _, b = http(base + "?mode=accctrl&type=req_acc", timeout=6)
    say("\n[0] 基线 req_acc -> %s" % brief(b, 140))
    OUT["baseline"] = brief(b, 200)

    # ---- 1 取加密密钥 ----
    say("\n[1] 尝试取加密密钥 req_acc_g")
    for label, q in [("裸 req_acc_g", "mode=accctrl&type=req_acc_g"),
                     ("带 value", "mode=accctrl&type=req_acc_g&value=%s" % UUID),
                     ("req_acc_g+value2", "mode=accctrl&type=req_acc_g&value=%s&value2=%s" % (UUID, NAME))]:
        st, _, b = http(base + "?" + q, timeout=8, read=1000)
        say("    %-18s -> HTTP %s | %s" % (label, st, brief(b, 160)))
        OUT["req_acc_g_" + label] = brief(b, 400)

    # ---- 2 新端口服务探测 ----
    say("\n[2] 60606 / 50001 服务探测")
    for port, paths in [(60606, ["/", "/Lumix/Server0/ddd", "/Lumix/", "/Lumix/Server0/",
                                 "/Lumix/Server0/ddd/", "/Server0/ddd"]),
                        (50001, ["/", "/Lumix/Server0/ddd"])]:
        say("  -- port %d --" % port)
        for p in paths:
            url = "http://%s:%d%s" % (cam, port, p)
            st, h, b = http(url, timeout=5, read=600)
            tag = "%-28s" % p
            if st:
                say("     %s -> %s | Server=%s | %s" % (tag, st, h.get("Server", "-"), brief(b, 120)))
                OUT["p%d%s" % (port, p.replace("/", "_"))] = {"status": st, "body": brief(b, 400),
                                                              "hdrs": {k: v for k, v in h.items()}}
            else:
                say("     %s -> 无响应 (%s)" % (tag, brief(b, 60)))
        # POST 一个空体试试
        st, h, b = http("http://%s:%d/Lumix/Server0/ddd" % (cam, port), timeout=5,
                        method="POST", data=b"", ctype="application/octet-stream")
        say("     POST /Lumix/Server0/ddd -> %s | %s" % (st, brief(b, 120)))
        OUT["p%d_POST" % port] = brief(b, 300)

    # ---- 3 发起授权 ----
    say("\n[3] 发起授权请求 req_acc（明文路径，UUID=%s）" % UUID)
    st, _, b = http(base + "?mode=accctrl&type=req_acc&value=%s&value2=%s" % (UUID, NAME),
                    timeout=12, read=1000)
    say("    -> HTTP %s | %s" % (st, brief(b, 200)))
    OUT["req_acc_send"] = brief(b, 300)

    # ---- 4 轮询等待机身确认 ----
    say("\n[4] 轮询授权状态（最长 150s）——请留意机身屏幕并点“允许”")
    granted = False
    t0 = time.time()
    while time.time() - t0 < 150:
        st, _, b = http(base + "?mode=accctrl&type=req_acc", timeout=6, read=400)
        txt = brief(b, 140)
        el = int(time.time() - t0)
        say("    +%3ds  %s" % (el, txt))
        OUT["poll_%d" % el] = txt
        low = txt.lower()
        if "err_user_refused" in low:
            say("    -> 相机报告【用户拒绝】")
        if low.startswith("ok") and "err_" not in low:
            granted = True
            say("    -> 状态 ok，判定已授权")
            break
        time.sleep(3)

    # ---- 5 授权后复测 ----
    say("\n[5] 复测读端点（无论是否判定授权都测，看真实门状态）")
    for name, q in [("getstate", "mode=getstate"),
                    ("getinfo capability", "mode=getinfo&type=capability"),
                    ("getinfo allmenu", "mode=getinfo&type=allmenu"),
                    ("getinfo curmenu", "mode=getinfo&type=curmenu"),
                    ("getinfo lens", "mode=getinfo&type=lens"),
                    ("getsetting videoformat", "mode=getsetting&type=videoformat"),
                    ("startsenddata", "mode=startsenddata&type=camsetting&value=65533")]:
        st, _, b = http(base + "?" + q, timeout=10, read=400)
        say("    %-24s -> %s" % (name, brief(b, 130)))
        OUT["after_" + name] = brief(b, 300)

    # ---- 6 清理 ----
    say("\n[6] req_acc_can 清理")
    st, _, b = http(base + "?mode=accctrl&type=req_acc_can&value=%s&value2=" % UUID, timeout=8)
    say("    -> %s" % brief(b, 140))

    OUT["granted"] = granted
    json.dump({"log": LOG, "results": OUT}, open(outfile, "w"),
              ensure_ascii=False, indent=2)
    say("\n### 配对复现结束 -> %s" % outfile)
    return 0


if __name__ == "__main__":
    sys.exit(main())
