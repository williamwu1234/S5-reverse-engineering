#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_selfcheck.py — 「一边录制一边发送图像」模式自检（**离线自包含，不依赖任何会话**）

什么时候用它
    当 Mac 连到相机的热点（SSID 形如 S5-XXXXXX）时，**家庭网络会断开**，
    远程协助会失效。所以这个脚本把该做的检查全打包好，你本地一条命令跑完。

怎么用
    # 自动找相机（先试家网地址，再试热点网关）
    python3 s5_selfcheck.py

    # 或显式指定
    python3 s5_selfcheck.py --cam 192.168.54.1      # 相机热点模式（网关）
    python3 s5_selfcheck.py --cam 192.168.1.100     # 家庭局域网模式

它会回答三个问题
    ① 相机当前在哪个模式（rec / play）？
    ② **在 rec 模式下，DLNA 内容树有没有内容？**  ← 「边录边发」是否生效的关键
    ③ 如果有内容，第一张照片能否下载、大小对不对？

安全
    只发只读请求（getstate / getinfo / SOAP Browse / HTTP GET），
    **不 setsetting、不写相机、不删文件**。
"""
import argparse, html, os, re, socket, sys, time, urllib.error, urllib.request

DLNA_PORT = 60606
UA_DLNA = "Panasonic MIL DLNA CP UPnP/1.0"
UA_LUMIX = "LUMIX Sync"


# ---------------------------------------------------------------- HTTP
def http(url, method="GET", headers=None, body=None, timeout=12):
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, headers=headers or {}, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read()
    except urllib.error.HTTPError as e:
        return e.code, (e.read() or b"")
    except Exception as e:
        return 0, str(e).encode()


def cam_cgi(cam, mode, **kw):
    q = "".join(f"&{k}={v}" for k, v in kw.items())
    return http(f"http://{cam}/cam.cgi?mode={mode}{q}",
                headers={"User-Agent": UA_LUMIX}, timeout=8)


def txt(b):
    return b.decode("utf-8", "replace") if isinstance(b, (bytes, bytearray)) else str(b)


def result_of(s):
    m = re.search(r"<result>([^<]*)</result>", s or "")
    return m.group(1) if m else "(无)"


# ---------------------------------------------------------------- 自动找相机
def find_camera(explicit=None, verbose=True):
    cands = [explicit] if explicit else []
    cands += ["192.168.54.1",                       # 相机热点网关（松下默认）
              "192.168.0.1", "192.168.1.1"]          # 常见路由器地址
    seen = set()
    for c in cands:
        if not c or c in seen:
            continue
        seen.add(c)
        st, b = cam_cgi(c, "getstate")
        r = result_of(txt(b))
        if verbose:
            print(f"  试 {c:16s} getstate -> {r}")
        if r in ("ok", "err_reject", "err_busy", "err_unsuitable_app",
                 "err_others_requesting", "err_critical"):
            return c, r                    # 有回话就说明是相机
    return None, None


# ---------------------------------------------------------------- DLNA
def browse(cam, object_id="0", flag="BrowseDirectChildren", count=0):
    body = ('<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
            's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
            '<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1" '
            'xmlns:pana="urn:schemas-panasonic-com:pana">'
            f'<ObjectID>{object_id}</ObjectID><BrowseFlag>{flag}</BrowseFlag>'
            f'<Filter>*</Filter><StartingIndex>0</StartingIndex>'
            f'<RequestedCount>{count}</RequestedCount><SortCriteria></SortCriteria>'
            '<pana:X_FromCP>LumixLink2.0</pana:X_FromCP></u:Browse>'
            '</s:Body></s:Envelope>')
    return http(f"http://{cam}:{DLNA_PORT}/Server0/CDS_control", "POST",
                {"Accept-Charset": "UTF-8",
                 "Content-Type": 'text/xml; charset="utf-8"',
                 "SOAPAction": "urn:schemas-upnp-org:service:ContentDirectory:1#Browse",
                 "User-Agent": UA_DLNA, "Host": f"{cam}:{DLNA_PORT}"}, body, timeout=20)


def parse_items(xml):
    """★ 必须先 HTML 反转义：SOAP 把 DIDL 转义在 <Result> 里，否则 0 条目。"""
    if not xml:
        return []
    if "&lt;" in xml:
        m = re.search(r"<Result>([\s\S]*?)</Result>", xml)
        xml = html.unescape(m.group(1) if m else xml)
    out = []
    for m in re.finditer(r"<(item|container)\b([\s\S]*?)</\1>", xml):
        blk = m.group(0)
        def tag(t):
            r = re.search(rf"<{t}[^>]*>([^<]*)</{t}>", blk)
            return r.group(1) if r else ""
        res = re.search(r"<res[^>]*>([^<]*)</res>", blk)
        out.append(dict(kind=m.group(1), title=tag("dc:title"),
                        cls=tag("upnp:class"), res=res.group(1) if res else ""))
    return out


# ---------------------------------------------------------------- 主流程
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", default=None, help="相机 IP（默认自动探测）")
    ap.add_argument("--out", default=".", help="下载目录")
    ap.add_argument("--no-download", action="store_true", help="只列举不下载")
    a = ap.parse_args()

    print("=" * 62)
    print(" DC-S5 「一边录制一边发送图像」自检")
    print("=" * 62)

    print("\n[1] 找相机")
    cam, first = find_camera(a.cam)
    if not cam:
        print("\n  ❌ 找不到相机。请确认：")
        print("     · 相机已开机、Wi-Fi 已连（热点或家网）")
        print("     · Mac 与相机在同一网络")
        print("     · 若连的是相机热点，网关通常是 192.168.54.1")
        return 1
    print(f"  ✅ 相机 = {cam}")

    print("\n[2] 相机状态")
    st, b = cam_cgi(cam, "getstate")
    s = txt(b)
    mode = (re.search(r"<cammode>([^<]*)</cammode>", s) or [None, "?"])[1]
    batt = (re.search(r"<batt>([^<]*)</batt>", s) or [None, "?"])[1]
    print(f"  getstate  -> {result_of(s)}")
    print(f"  cammode   = {mode}      ← rec=拍摄 / play=回放")
    print(f"  电量       = {batt}")

    print("\n[3] ★ 关键测试：rec 模式下的 DLNA 内容树")
    if mode == "rec":
        print("  （相机正在拍摄模式 —— 若「边录边发」生效，这里就应该有内容）")
    else:
        print(f"  （相机在 {mode} 模式；本测试的目的是看 **rec 模式** 下有没有内容）")

    st_c, body_c = browse(cam, "0")
    st_m, body_m = browse(cam, "0", flag="BrowseMetadata")
    items = parse_items(txt(body_c))
    root = re.search(r"&lt;dc:title&gt;([^&]*)", txt(body_m))
    fault = re.search(r"<errorCode>(\d+)</errorCode>", txt(body_c))

    print(f"  BrowseDirectChildren -> HTTP {st_c}" +
          (f"   UPnP {fault.group(1)}" if fault else ""))
    print(f"  BrowseMetadata       -> HTTP {st_m}   root title = "
          f"{root.group(1) if root else 'None'}")
    print(f"  ★ 内容条目数 = {len(items)}")

    if st_c == 403:
        print("\n  ❌ 403 = accctrl 未达 ok（授权问题，不是模式问题）")
        print("     → 用监看工具拿一次 ok（启动后等 10–20 秒），再重跑本脚本")
        return 2

    if not items:
        print("\n  ⚠️ 有响应但**没有内容**。可能原因：")
        print("     ① 相机没开启「一边录制一边发送图像」")
        print("     ② 该模式需要在**相机热点**下才生效（家网下不导出）")
        print("     ③ 卡上确实没有可发送的照片")
        print("\n  建议：开启该选项后重跑；若家网下始终为空，再试连相机热点。")
        return 3

    print("\n  ✅✅ **内容树有内容！「边录边发」生效！**")
    for it in items[:8]:
        print(f"     {it['title']:16s} {it['cls'][:26]:28s} {it['res'][:64]}")

    if a.no_download:
        return 0

    print("\n[4] 下载第一张验证")
    it = items[0]
    dst = os.path.join(a.out, (it["title"] or "photo") + os.path.splitext(it["res"])[1])
    st_d, data = http(it["res"], headers={"User-Agent": UA_DLNA}, timeout=120)
    if st_d == 200 and data:
        open(dst, "wb").write(data)
        print(f"  ✅ HTTP {st_d}  {len(data):,} 字节  →  {dst}")
        try:
            from PIL import Image
            im = Image.open(dst)
            print(f"     图片: {im.size[0]}x{im.size[1]}  {im.format}")
        except Exception:
            pass
        print("\n  ⇒ 结论：**可以在拍摄模式下无线取片**，"
              "配合 LUT 烧录即可实现「边录边套 LUT」")
    else:
        print(f"  ❌ 下载失败 HTTP {st_d}")
        return 4
    return 0


if __name__ == "__main__":
    sys.exit(main())
