#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
wifi_lut.py — WiFi 取片 + 实时套 LUT（初代 S5 无实时 LUT，这是唯一的"实时"路径）

背景
    · 机内：S5 无 Real Time LUT（官方三机对比表否证），只能 [V-Log View Assist] 监看。
    · BLE：实测只暴露凭据面，带宽 ~KB/s 级，**传照片都不现实**，更别说视频。
    · WiFi：唯一可行通道。但 60606 的 DLNA 控制面在 station 模式下实测 **403**，
      项目自有 iOS App 也**从无 Browse 成功证据**（审计发现 E-3）。
      ⇒ 所以本工具第一步是 **probe：把能想到的取片路径全部试一遍，找出真正可用的那条**。

用法
    python3 wifi_lut.py probe  --cam 192.168.1.131
    python3 wifi_lut.py list   --cam 192.168.1.131
    python3 wifi_lut.py watch  --cam 192.168.1.131 --lut lut/vlog_to_709_17.vlt --out ~/Pictures/LUT_baked

设计
    · 纯只读：只发 GET / SOAP Browse（查询动作），不 setsetting、不写相机
    · 串行 + 间隔（并发会触发 invalid login / 需重启）
    · 找到可用路径后，watch 模式轮询新文件 → 下载 → 调 ./bake 烧录 → 落盘（可选自动打开）
"""
import argparse, json, os, re, subprocess, sys, time, urllib.request, urllib.error

HERE = os.path.dirname(os.path.abspath(__file__))
BAKE = os.path.join(HERE, "bake")
PY = sys.executable
DLNA_UA = "Panasonic MIL DLNA CP UPnP/1.0"
LUMIX_UA = "LUMIX Sync"

# ---------------------------------------------------------------- HTTP 基础
def http(url, method="GET", headers=None, body=None, timeout=10, ua=None):
    h = {"User-Agent": ua or LUMIX_UA}
    if headers: h.update(headers)
    data = body.encode() if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), e.read() or b""
    except Exception as e:
        return 0, {}, str(e).encode()

def ssdp_discover(timeout=3.0):
    import socket
    msg = ('M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: "ssdp:discover"\r\nMX: 2\r\n'
           'ST: urn:schemas-upnp-org:device:MediaServer:1\r\n\r\n').encode()
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM, socket.IPPROTO_UDP)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 2)
    s.settimeout(1.0)
    found = []
    try:
        s.sendto(msg, ("239.255.255.250", 1900))
        t0 = time.time()
        while time.time() - t0 < timeout:
            try:
                data, addr = s.recvfrom(4096)
                txt = data.decode("utf-8", "replace")
                server = ""
                m = re.search(r"(?im)^SERVER:\s*(.*)$", txt)
                if m: server = m.group(1).strip()
                loc = ""
                m2 = re.search(r"(?im)^LOCATION:\s*(.*)$", txt)
                if m2: loc = m2.group(1).strip()
                found.append((addr[0], f"{server} {loc}".strip()))
            except socket.timeout:
                continue
    except Exception:
        pass
    finally:
        s.close()
    return found

def cam_cgi(cam, mode, **kw):
    q = "".join(f"&{k}={v}" for k, v in kw.items())
    return http(f"http://{cam}/cam.cgi?mode={mode}{q}", ua=LUMIX_UA, timeout=8)

# ---------------------------------------------------------------- 取片策略
def browse_envelope(obj="0", flag="BrowseDirectChildren", count=0):
    return f'''<?xml version="1.0" encoding="utf-8"?>
<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" s:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">
  <s:Body>
    <u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1">
      <s:ObjectID>{obj}</s:ObjectID>
      <s:BrowseFlag>{flag}</s:BrowseFlag>
      <s:Filter>*</s:Filter>
      <s:StartingIndex>0</s:StartingIndex>
      <s:RequestedCount>{count}</s:RequestedCount>
      <s:SortCriteria></s:SortCriteria>
    </u:Browse>
  </s:Body>
</s:Envelope>'''

def try_dlna(cam, port=60606):
    """DLNA ContentDirectory Browse：多组 header/body 变体，找出 200 的那一组"""
    base = f"http://{cam}:{port}"
    sa = "urn:schemas-upnp-org:service:ContentDirectory:1#Browse"
    variants = [
        ("标准（无引号 SA + DLNA UA）", {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": sa, "User-Agent": DLNA_UA}),
        ("SA 带引号",                  {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": f'"{sa}"', "User-Agent": DLNA_UA}),
        ("无 UA",                      {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": sa}),
        ("加 Connection: close",       {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": sa, "User-Agent": DLNA_UA, "Connection": "close"}),
        ("Host 带端口 + X-AV-Client",  {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": sa, "User-Agent": DLNA_UA, "Host": f"{cam}:{port}", "X-AV-Client-Info": "av=1.0"}),
        ("DLNA 客户端完整头",          {"Content-Type": 'text/xml; charset="utf-8"', "SOAPAction": sa, "User-Agent": DLNA_UA, "X-AV-Client-Info": "av=1.0", "Accept": "*/*"}),
    ]
    paths = ["/Server0/CDS_control", "/Lumix/Server0/CDS_control"]
    out = []
    for path in paths:
        for name, hh in variants:
            st, hdr, body = http(base + path, "POST", hh, browse_envelope())
            out.append((path, name, st, len(body), body[:200]))
            if st == 200 and body:
                return True, (path, name, body)
            time.sleep(0.4)
    return False, out

def try_content_info(cam):
    """cam.cgi get_content_info（App 用它列目录）"""
    res = []
    for v in ["0", "1", "", "DCIM", "100_PANA"]:
        st, hdr, body = cam_cgi(cam, "get_content_info", value=v)
        res.append((v, st, body[:300]))
        time.sleep(0.4)
    return res

def try_cam_cgi_reads(cam):
    """把可能列出内容的 cam.cgi 读取端点扫一遍"""
    res = []
    for mode, kw in [("getinfo", {"type": "media"}), ("getinfo", {"type": "contentlist"}),
                     ("getinfo", {"type": "storage"}), ("getinfo", {"type": "capability"}),
                     ("getprogress", {}), ("notify", {"type": "transfer"})]:
        st, hdr, body = cam_cgi(cam, mode, **kw)
        res.append((mode, kw, st, body[:200]))
        time.sleep(0.4)
    return res

# ---------------------------------------------------------------- probe
def cmd_probe(a):
    cam = a.cam
    print(f"=== 0) 相机在线？ {cam}")
    st, hdr, body = cam_cgi(cam, "getstate")
    print(f"  getstate -> HTTP {st}  {body[:160].decode('utf-8','replace')}")
    if st != 200:
        print("  ❌ 相机不可达。请确认：相机 Wi-Fi 已连到同一网络、且处于开机状态。")
        return 1

    print("\n=== 0.5) SSDP 发现（确认相机在网络里）===")
    ssdp = ssdp_discover()
    for ip, txt in ssdp:
        mark = "  ← 相机?" if "Lumix" in txt or "MediaServer" in txt else ""
        print(f"  {ip}: {txt[:110]}{mark}")
    if not ssdp:
        print("  （无响应）")

    print("\n=== 0.6) 本机挂载的卷（若相机以 USB 存储接入，会出现在这里）===")
    for v in os.listdir("/Volumes"):
        if v in ("Macintosh HD", "Recovery"): continue
        p = os.path.join("/Volumes", v)
        try:
            has_dcim = os.path.isdir(os.path.join(p, "DCIM"))
            print(f"  /Volumes/{v}  {'（含 DCIM ⇒ 像是相机卡）' if has_dcim else ''}")
        except Exception:
            pass

    print("\n=== 1) DLNA 60606（控制面）===")
    ok, info = try_dlna(cam)
    if ok:
        path, name, body = info
        print(f"  ✅ 可用！path={path}  变体={name}  {len(body)} 字节")
        open(os.path.join(HERE, "dlna_browse_sample.xml"), "wb").write(body)
        print("     已存 dlna_browse_sample.xml")
        return 0
    for path, name, st, ln, _ in info:
        print(f"  ❌ {path:32s} {name:26s} HTTP {st}")

    print("\n=== 2) cam.cgi get_content_info ===")
    for v, st, body in try_content_info(cam):
        print(f"  value={v!r:12s} HTTP {st}  {body.decode('utf-8','replace')[:120]}")

    print("\n=== 3) 其它 cam.cgi 读取端点 ===")
    for mode, kw, st, body in try_cam_cgi_reads(cam):
        print(f"  {mode}{kw} -> HTTP {st}  {body.decode('utf-8','replace')[:110]}")

    print("""
=== 结论怎么读 ===
  · 若 1) 里有 200 → 直接 `watch`，走 DLNA 取片。
  · 若 1) 全 403 且 2)/3) 无内容列表 → **station 模式下没有可用的取片通道**。可选：
      a) 把相机切到 **SoftAP 模式**（相机自己发热点），电脑连它，再跑 probe——
         项目实测 60606 在 SoftAP 下设备描述可用，控制面值得重测；
      b) **USB 连接**：相机设成 USB 存储/PC 模式，卡会以磁盘挂载 ⇒ 直接用
         `watch_bake.py` 监视挂载点（**这是唯一真正"拍摄即烧"的路径**）；
      c) 用官方 LUMIX Sync 把照片导到某个文件夹，再用 `watch_bake.py` 监视那个文件夹。
""")
    return 2

# ---------------------------------------------------------------- list / watch
def fetch_index(cam, strategy):
    if strategy == "dlna":
        ok, info = try_dlna(cam)
        if not ok: return []
        _, _, body = info
        xml = body.decode("utf-8", "replace")
        items = []
        for m in re.finditer(r"<D-Item[\s\S]*?</D-Item>|<item[\s\S]*?</item>", xml):
            blk = m.group(0)
            g = lambda t: (re.search(rf"<{t}>([^<]*)</{t}>", blk) or [None, ""])[1]
            res = re.search(r"<res[^>]*>([^<]*)</res>", blk)
            items.append(dict(title=g("dc:title") or g("title"),
                              cls=g("upnp:class"), res=res.group(1) if res else "",
                              id=(re.search(r'id="([^"]*)"', blk) or [None, ""])[1]))
        return items
    return []

def dlna_download(cam, res_url, dst):
    st, hdr, body = http(res_url, ua=DLNA_UA, timeout=60)
    if st == 200 and body:
        open(dst, "wb").write(body); return True, len(body)
    return False, 0

def cmd_list(a):
    items = fetch_index(a.cam, a.strategy)
    if not items:
        print("未取到列表（DLNA 控制面可能仍 403）。先跑 probe。"); return 2
    print(f"共 {len(items)} 项：")
    for it in items[:50]:
        print(f"  [{it['id']:>6}] {it['title'][:40]:42s} {it['cls'][:28]:30s} {it['res'][:70]}")
    return 0

def cmd_watch(a):
    os.makedirs(a.out, exist_ok=True)
    seen = set()
    state = os.path.join(HERE, ".wifi_state.json")
    if os.path.exists(state):
        try: seen = set(json.load(open(state)))
        except Exception: pass
    print(f"WiFi 实时管线启动：{a.cam}  策略={a.strategy}  产物={a.out}")
    print("  注意：机内不能烧 LUT，这里是**下载后立刻烧**（照片几秒内出片）\n")
    n = 0
    while True:
        try:
            items = fetch_index(a.cam, a.strategy)
        except Exception as e:
            print("  取列表失败：", e); items = []
        for it in items:
            if not it["res"] or it["id"] in seen: continue
            ext = os.path.splitext(it["res"].split("?")[0])[1].lower()
            if a.types and ext.lstrip(".") not in a.types: continue
            raw = os.path.join(a.out, "_raw_" + (it["title"] or it["id"]) + ext)
            ok, ln = dlna_download(a.cam, it["res"], raw)
            if not ok:
                print(f"  ❌ 下载失败 {it['title']}"); continue
            seen.add(it["id"])
            json.dump(sorted(seen), open(state, "w"))
            baked = os.path.join(a.out, (it["title"] or it["id"]) + ext)
            r = subprocess.run([BAKE, "image" if ext in (".jpg", ".jpeg", ".png") else "video",
                                a.lut, raw, baked], capture_output=True, text=True)
            if r.returncode == 0:
                os.remove(raw); n += 1
                print(f"  ✅ {it['title']}  ({ln/1e6:.1f} MB 下载 → 已套 LUT)")
            else:
                print(f"  ⚠️ 烧录失败，原片留在 {raw}：{r.stderr[:120]}")
        if a.once: break
        time.sleep(a.interval)
    print(f"完成，共处理 {n} 个")
    return 0

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["probe", "list", "watch"])
    ap.add_argument("--cam", default="192.168.1.131")
    ap.add_argument("--lut", default=os.path.join(HERE, "lut", "vlog_to_709_17.vlt"))
    ap.add_argument("--out", default=os.path.expanduser("~/Pictures/LUT_baked_wifi"))
    ap.add_argument("--strategy", default="dlna", choices=["dlna"])
    ap.add_argument("--interval", type=float, default=5.0)
    ap.add_argument("--types", default="jpg,jpeg,png")
    ap.add_argument("--once", action="store_true")
    a = ap.parse_args()
    a.types = [x.strip().lower().lstrip(".") for x in a.types.split(",") if x.strip()]
    sys.exit({"probe": cmd_probe, "list": cmd_list, "watch": cmd_watch}[a.cmd](a))

if __name__ == "__main__":
    main()
