#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_content.py — 通过 WiFi 访问 S5 机身存储（内容列举 / 下载 / 诊断）

问题背景（本项目实测）
    60606 的 DLNA **控制面**（ContentDirectory#Browse）在 station（家网）模式下
    对第三方客户端一律 **403**；而静态资源（设备描述、SCPD）却是 200。
    官方 LUMIX Sync 的请求格式已从 APK 反编译取出（见下），
    **逐字节照抄仍然 403** ⇒ 不是请求格式问题，是相机侧对该客户端不放行。

已从官方 APK 取出的**确切**请求（`p168v5/a.java:212-213`、`p168v5/m.java:83-87`）
    URL      : http://<ip>:60606/Server0/CDS_control
    Headers  : Accept-Charset: UTF-8
               Content-Type: text/xml; charset="utf-8"
               SOAPAction: urn:schemas-upnp-org:service:ContentDirectory:1#Browse
               User-Agent: Panasonic MIL DLNA CP UPnP/1.0
               Host: <ip>:60606
    Body     : 单行无空白；子元素**不带 s: 前缀**；含松下私有扩展
               <pana:X_FromCP>LumixLink2.0</pana:X_FromCP>
               xmlns:pana="urn:schemas-panasonic-com:pana"

本模块做三件事
    1) `diagnose()`：把**所有可能影响放行的因素**逐项测一遍并给出结论，
       包括一个极易被忽略的状态：**机身菜单开着时端点会回 `err_reject`**
       （本项目 `01_研究报告/07_…:121`、`25_…:19` 均有记载）。
    2) `browse()`：用官方确切格式列举内容；拿到 `res` URL 后 `download()`。
    3) `sample()`：从取景流抓一帧当"取片通道不可用时的替代可视化"。

安全：**纯只读**。不 setsetting、不写相机、不删文件。
"""
from __future__ import annotations
import http.client, io, os, re, socket, time, urllib.request, urllib.error

DLNA_PORT = 60606
UA_DLNA = "Panasonic MIL DLNA CP UPnP/1.0"
UA_LUMIX = "LUMIX Sync"


# ---------------------------------------------------------------- HTTP
def _http(url, method="GET", headers=None, body=None, timeout=12):
    h = {}
    if headers:
        h.update(headers)
    data = body.encode("utf-8") if isinstance(body, str) else body
    req = urllib.request.Request(url, data=data, headers=h, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, dict(r.headers), r.read()
    except urllib.error.HTTPError as e:
        return e.code, dict(e.headers or {}), (e.read() or b"")
    except Exception as e:
        return 0, {}, str(e).encode()


def cam_cgi(cam, mode, timeout=8, **kw):
    q = "".join(f"&{k}={v}" for k, v in kw.items())
    return _http(f"http://{cam}/cam.cgi?mode={mode}{q}",
                 headers={"User-Agent": UA_LUMIX}, timeout=timeout)


def txt(b):
    return b.decode("utf-8", "replace") if isinstance(b, (bytes, bytearray)) else str(b)


def result_of(body: str) -> str:
    m = re.search(r"<result>([^<]*)</result>", body or "")
    return m.group(1) if m else "(无 result)"


# ---------------------------------------------------------------- 官方 Browse
def official_browse_body(object_id="0", start=0, count=0,
                         flag="BrowseDirectChildren", filter_="*") -> str:
    """逐字节复刻官方 App（`p168v5/a.java:212`）——注意：无 s: 前缀、单行、含 pana 扩展。"""
    return ('<?xml version="1.0" encoding="utf-8"?>'
            '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
            's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
            '<s:Body>'
            '<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1" '
            'xmlns:pana="urn:schemas-panasonic-com:pana">'
            f'<ObjectID>{object_id}</ObjectID>'
            f'<BrowseFlag>{flag}</BrowseFlag>'
            f'<Filter>{filter_}</Filter>'
            f'<StartingIndex>{start}</StartingIndex>'
            f'<RequestedCount>{count}</RequestedCount>'
            '<SortCriteria></SortCriteria>'
            '<pana:X_FromCP>LumixLink2.0</pana:X_FromCP>'
            '</u:Browse></s:Body></s:Envelope>')


def browse(cam, object_id="0", start=0, count=0, timeout=20,
           flag="BrowseDirectChildren"):
    """返回 (status, body_text)。status==200 时 body 为 DIDL-Lite XML。

    ★ flag='BrowseMetadata' 是关键补充（2026-10-14 实测）：
      · BrowseDirectChildren id=0 → **500 + 701**（固件对"空根"返回 701 而非空列表）
      · BrowseMetadata      id=0 → **200 + <container id="0"><dc:title>root</dc:title>**
      ⇒ 用 BrowseMetadata 才能区分「门没开(403)」/「根不存在(701)」/「根存在但无子项」。
    """
    st, hdr, body = _http(
        f"http://{cam}:{DLNA_PORT}/Server0/CDS_control", "POST",
        {"Accept-Charset": "UTF-8",
         "Content-Type": 'text/xml; charset="utf-8"',
         "SOAPAction": "urn:schemas-upnp-org:service:ContentDirectory:1#Browse",
         "User-Agent": UA_DLNA,
         "Host": f"{cam}:{DLNA_PORT}"},
        official_browse_body(object_id, start, count, flag=flag), timeout)
    return st, txt(body)


def service_action(cam, action, inner="", service="ContentDirectory",
                   control="CDS_control", timeout=15):
    """调任意 CDS/CMS action（GetSystemUpdateID / GetProtocolInfo 等）。"""
    st, hdr, body = _http(
        f"http://{cam}:{DLNA_PORT}/Server0/{control}", "POST",
        {"Accept-Charset": "UTF-8",
         "Content-Type": 'text/xml; charset="utf-8"',
         "SOAPAction": f'"urn:schemas-upnp-org:service:{service}:1#{action}"',
         "User-Agent": UA_DLNA,
         "Host": f"{cam}:{DLNA_PORT}"},
        '<?xml version="1.0" encoding="utf-8"?>'
        '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
        's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/"><s:Body>'
        f'<u:{action} xmlns:u="urn:schemas-upnp-org:service:{service}:1" '
        'xmlns:pana="urn:schemas-panasonic-com:pana">'
        f'{inner}</u:{action}></s:Body></s:Envelope>', timeout)
    return st, txt(body)


def get_cam_mode(cam):
    st, _, b = cam_cgi(cam, "getstate")
    m = re.search(r"<cammode>([^<]*)</cammode>", txt(b))
    return m.group(1) if m else None


def require_play_mode(cam, verbose=True):
    """★ DLNA 内容树**只在回放模式下才有内容**（2026-10-14 实测定因）。

    拍摄（rec）模式下：Browse 返回 200 但 NumberReturned=0 / 或 701。
    切到回放（play）模式后：立刻返回 16 个条目（原图 + 缩略图 + 中图三种 res）。
    """
    cur = get_cam_mode(cam)
    if verbose:
        print(f"   当前 cammode = {cur}")
    if cur == "play":
        return True, cur
    st, _, b = cam_cgi(cam, "camcmd", value="playmode")
    if verbose:
        print(f"   camcmd playmode -> {result_of(txt(b))}")
    time.sleep(3.0)
    return get_cam_mode(cam) == "play", get_cam_mode(cam)


def list_photos(cam, object_id="0", verbose=True, ensure_play=True):
    """一步到位：确保回放模式 → Browse → 解析。返回条目列表。"""
    if ensure_play:
        ok, mode = require_play_mode(cam, verbose)
        if not ok and verbose:
            print(f"   ⚠️ 仍未进入回放模式（{mode}）——内容树大概率为空")
    st, body = browse(cam, object_id, count=0)
    items = parse_items(body)
    if verbose:
        fault = parse_fault(body)
        print(f"   Browse -> HTTP {st}  条目 {len(items)}" +
              (f"  fault {fault}" if fault else ""))
    return items


def probe_root(cam):
    """★ 三层判定：门开没开 / 根存不存在 / 有没有内容。"""
    out = {}
    st, body = browse(cam, "0", flag="BrowseDirectChildren")
    out["children_http"], out["children_fault"] = st, parse_fault(body)
    out["children"] = parse_items(body)
    time.sleep(1.0)
    st2, body2 = browse(cam, "0", flag="BrowseMetadata")
    out["meta_http"], out["meta_fault"] = st2, parse_fault(body2)
    m = re.search(r"&lt;dc:title&gt;([^&]*)", body2)
    out["root_title"] = m.group(1) if m else None
    time.sleep(1.0)
    st3, body3 = service_action(cam, "GetSystemUpdateID")
    m3 = re.search(r"<Id>(\d+)</Id>", body3)
    out["system_update_id"] = int(m3.group(1)) if m3 else None
    out["gate_open"] = (st != 403)
    out["root_exists"] = (st2 == 200 and out["root_title"] is not None)
    out["has_children"] = bool(out["children"])
    if not out["gate_open"]:
        out["verdict"] = "accctrl 未达 ok ⇒ 403（门关着）"
    elif out["root_exists"] and not out["has_children"]:
        out["verdict"] = ("门已开、根容器存在，但内容树为空 ⇒ **相机当前不在回放模式**"
                          "（拍摄模式下 DLNA 不导出内容）。跑 list_photos() 会自动切 playmode。")
    elif out["has_children"]:
        out["verdict"] = f"✅ 可访问，%d 项" % len(out["children"])
    else:
        out["verdict"] = "根容器不存在或响应异常"
    return out


def parse_items(xml: str):
    """解析 DIDL-Lite：兼容 <D-Item> / <item> / <container>。

    ★ 必须先做 HTML 反转义：SOAP 响应把 DIDL 放在 <Result> 里**转义**了
      （`&lt;item id=&quot;...&quot;&gt;`）。早期版本直接对原文做正则 ⇒ 0 条目，
      一度误判为"内容树为空"。这是本工具曾走过的弯路。
    """
    if not xml:
        return []
    if "&lt;" in xml:
        import html as _html
        m = re.search(r"<Result>([\s\S]*?)</Result>", xml)
        xml = _html.unescape(m.group(1) if m else xml)
    out = []
    for m in re.finditer(r"<(D-Item|item|container)\b([\s\S]*?)</\1>", xml):
        blk = m.group(0)
        def tag(t):
            r = re.search(rf"<{t}[^>]*>([^<]*)</{t}>", blk)
            return r.group(1) if r else ""
        def attr(t):
            r = re.search(rf'{t}="([^"]*)"', blk)
            return r.group(1) if r else ""
        res = re.search(r"<res[^>]*>([^<]*)</res>", blk)
        out.append(dict(kind=m.group(1), id=attr("id"),
                        parent=attr("parentID"),
                        title=tag("dc:title") or tag("title"),
                        cls=tag("upnp:class"),
                        res=(res.group(1) if res else "")))
    return out


def download(cam, res_url, dst_path, timeout=120):
    st, hdr, body = _http(res_url, headers={"User-Agent": UA_DLNA}, timeout=timeout)
    if st == 200 and body:
        os.makedirs(os.path.dirname(os.path.abspath(dst_path)) or ".", exist_ok=True)
        with open(dst_path, "wb") as f:
            f.write(body)
        return True, len(body)
    return False, 0


# ---------------------------------------------------------------- UPnP Fault
def parse_fault(xml: str):
    """解析 UPnP SOAP Fault。返回 (errorCode, errorDescription) 或 None。
    ★ 能收到 Fault 本身就是**好消息**：说明控制面已放行（403 时根本没有响应体）。"""
    m = re.search(r"<errorCode>(\d+)</errorCode>", xml or "")
    if not m:
        return None
    d = re.search(r"<errorDescription>([^<]*)</errorDescription>", xml or "")
    return int(m.group(1)), (d.group(1) if d else "")


# Panasonic LumixLink 的内容树根对象 ID 不是标准 UPnP 的 "0"。
# 实测 ObjectID=0 在已授权时返回 701 No such object ⇒ 需要扫描。
CANDIDATE_OBJECT_IDS = ["0", "1", "2", "3", "4", "10", "100",
                        "Lumix", "LUMIX", "LumixLink", "LumixLink2.0",
                        "DCIM", "100_PANA", "PRIVATE", "Content", "Browse"]


def sweep_object_ids(cam, ids=None, verbose=True, delay=1.2):
    """在**已授权（ok）**的前提下扫 ObjectID，找出能返回条目/不同错误码的那个。"""
    ids = ids or CANDIDATE_OBJECT_IDS
    hits = []
    for oid in ids:
        st, body = browse(cam, object_id=oid)
        fault = parse_fault(body)
        n = len(parse_items(body))
        if verbose:
            desc = f"HTTP {st}"
            if fault:
                desc += f"  UPnP {fault[0]} {fault[1]}"
            if n:
                desc += f"  ★条目 {n}"
            print(f"    ObjectID={oid:<12s} {desc}")
        if n or (fault and fault[0] != 701):
            hits.append((oid, st, fault, n))
        time.sleep(delay)
    return hits


def accctrl_cleanup(cam, uuid, verbose=True):
    """★ 清理陈旧 pending 请求 —— 解决相机报「智能手机应用程序需要更新 / invalid login」。
    规则（来自本项目 04_工具与脚本/campaign2/safe_handshake.py 的实战结论）：
      · 必须用**发起请求时那个同一 UUID**
      · **绝不**在 err_others_requesting（别人占着会话）时发，避免误伤他人请求
      · **绝不**用它去打断一个已 ok 的会话
    """
    st, _, b = cam_cgi(cam, "accctrl", type="req_acc")
    cur = txt(b).strip()
    if verbose:
        print(f"   清理前 accctrl = {cur}")
    if "others" in cur.lower():
        if verbose:
            print("   ⚠️ 检测到 err_others_requesting（别的客户端占着会话）—— 按规则**不清理**，")
            print("      请在手机/其它工具上断开连接后重试。")
        return False, cur
    if cur.startswith("ok,"):
        if verbose:
            print("   当前已是完整授权 ok —— 按规则**不清理**（以免打断可用会话）。")
        return True, cur
    st2, _, b2 = cam_cgi(cam, "accctrl", type="req_acc_can", value=uuid, value2="")
    if verbose:
        print(f"   req_acc_can({uuid}) -> {result_of(txt(b2))}")
    time.sleep(2)
    st3, _, b3 = cam_cgi(cam, "accctrl", type="req_acc")
    after = txt(b3).strip()
    if verbose:
        print(f"   清理后 accctrl = {after}")
    return after.startswith("ok,"), after


# ---------------------------------------------------------------- 诊断
def diagnose(cam, verbose=True):
    """逐项测所有可能影响"能否访问机身存储"的因素，返回结构化结论。"""
    R = {}

    def log(*a):
        if verbose:
            print(*a)

    log(f"=== S5 机身存储访问诊断  目标 {cam} ===")

    # 0) 在线
    st, _, b = cam_cgi(cam, "getstate")
    body0 = txt(b)
    r0 = result_of(body0)
    # ★ HTTP 200 = 相机可达；但 <result> 可能是 err_reject（菜单开启/占用）而非 ok
    R["reachable"] = (st == 200)
    R["getstate_result"] = r0
    R["online"] = (st == 200 and r0 == "ok")
    tag = "✅ ok" if R["online"] else ("⚠️ 可达但被拒" if st == 200 else "❌ 不可达")
    log(f"\n[0] 可达性    : {tag}  HTTP {st}  <result>{r0}</result>")
    if not R["reachable"]:
        R["verdict"] = "相机不可达（检查 Wi-Fi / 是否关机）"
        return R
    if not R["online"]:
        log("    ⚠️  getstate 非 ok ⇒ 相机当前处于**拒绝服务状态**：")
        log("        本项目记载的触发条件：**机身菜单开着** / 有陈旧 pending 请求 / 相机休眠。")
        log("        ⇒ 请**退出机身菜单、停在普通拍摄或回放画面**，再重测。")
        log("        这不是权限问题，是状态问题——也是『无线连不上相机存储』最常见的表象。")
    m = re.search(r"<cammode>([^<]*)</cammode>", txt(b))
    R["cammode"] = m.group(1) if m else "?"
    log(f"    cammode   : {R['cammode']}")

    # 1) 菜单是否开着 —— 最容易被忽略的 err_reject 来源
    st, _, b = cam_cgi(cam, "getinfo", type="camsetting")
    cs_res = result_of(txt(b))
    R["camsetting"] = cs_res
    menu_open = (cs_res == "err_reject")
    R["menu_open_suspected"] = menu_open
    log(f"\n[1] menu 状态 : getinfo camsetting -> {cs_res}")
    if menu_open:
        log("    ⚠️  **机身菜单很可能开着**（err_reject 是本项目记载的菜单开启特征）。")
        log("        ⇒ 请把相机退出菜单、停在普通拍摄/回放画面后重测。")
    else:
        log("    ✅ 菜单应为关闭（err_reject 未出现）")

    # 2) accctrl 状态
    st, _, b = cam_cgi(cam, "accctrl", type="req_acc")
    R["accctrl"] = txt(b).strip()
    log(f"\n[2] accctrl   : {R['accctrl']}")
    log("    字段 = <状态>,<相机名>,<模式>,<链路加密>；`ok` 才是完整授权（需机身上按【允许】）")

    # 3) 内容列举端点（存在性 vs 被拒）
    log("\n[3] 内容列举端点：")
    for v in ("0", "1"):
        st, _, b = cam_cgi(cam, "get_content_info", value=v)
        r = result_of(txt(b))
        R[f"get_content_info_{v}"] = r
        verdict = {"err_param": "端点不存在",
                   "err_reject": "★端点存在但被拒（状态问题，非缺权限）",
                   "ok": "✅ 可用"}.get(r, "其它")
        log(f"    get_content_info value={v} -> {r:14s} {verdict}")
        time.sleep(0.6)

    # 4) DLNA：静态 vs 控制
    log("\n[4] DLNA（60606）：")
    st_d, _, bd = _http(f"http://{cam}:{DLNA_PORT}/Lumix/Server0/ddd", timeout=8)
    st_s, _, bs = _http(f"http://{cam}:{DLNA_PORT}/Server0/CDS_SCPD", timeout=8)
    st_c, body_c = browse(cam)
    R["dlna_desc"], R["dlna_scpd"], R["dlna_browse"] = st_d, st_s, st_c
    log(f"    GET  设备描述 /Lumix/Server0/ddd -> HTTP {st_d}  ({len(bd)} B)")
    log(f"    GET  SCPD     /Server0/CDS_SCPD  -> HTTP {st_s}  ({len(bs)} B)")
    log(f"    POST Browse   /Server0/CDS_control -> HTTP {st_c}  ({len(body_c)} B)")
    if st_c == 200:
        items = parse_items(body_c)
        R["item_count"] = len(items)
        log(f"    ✅ **取片通道可用**！发现 {len(items)} 项")
        for it in items[:10]:
            log(f"        [{it['id']:>6}] {it['title'][:36]:38s} {it['cls'][:26]}")
        R["verdict"] = "可访问机身存储"
        return R
    fault = parse_fault(body_c)
    if st_c == 500 and fault:
        log(f"    ★★ 控制面已放行！UPnP Fault {fault[0]} {fault[1]}")
        log("        （能收到 Fault 就说明相机在**处理**我们的请求；403 时是连处理都不处理）")
        log(f"        {fault[0]} = No such object ⇒ 需要换 ObjectID，见 sweep_object_ids()")
        R["verdict"] = "控制面已放行（ok 授权生效），待确定 ObjectID"
        return R
    log("    ❌ 控制面被拒（静态资源却 200）")

    # 5) 结论
    log("\n=== 结论 ===")
    if menu_open:
        R["verdict"] = "疑似机身菜单开着 ⇒ 退出菜单后重测（最高优先级）"
        log("  ★ **先退出机身菜单再重测** —— `err_reject` 是本项目记载的菜单开启特征，")
        log("     而它同时影响 get_content_info 等多个端点。这是最可能、且零成本的一步。")
    else:
        R["verdict"] = "accctrl 未达 ok ⇒ DLNA 控制面 403（门未开）"
        log("  ★ **已实测确证的机制**：DLNA 控制面的门就是 accctrl 的 `ok` 状态 ——")
        log("      · accctrl = ok                      ⇒ Browse 返回 500 + UPnP Fault（服务已处理）")
        log("      · accctrl = ok_under_research_no_msg ⇒ Browse 返回 403（门关着）")
        log("  ⇒ 要先拿到 `ok`：见 accctrl_cleanup()（用同一 UUID 发 req_acc_can 清陈旧 pending），")
        log("     然后**只发一次** req_acc。❗切勿反复重发 req_acc —— 会触发")
        log("     「智能手机应用程序需要更新 / invalid login」（相机的频率保护）。")
        log("  拿到 ok 后：sweep_object_ids() 找内容树根对象（0 返回 701 No such object）。")
        log("  另注：相机侧有 **DMS（Digital Media Server）** 开关（APK 字符串 DMS Enabled/Disabled），")
        log("      若内容树为空也可能需要让相机进入 DLNA 服务状态。")
    return R


# ---------------------------------------------------------------- 取景帧替代
def sample(cam, port=49152, timeout=12):
    """从 UDP 取景流抓一帧（取片通道不可用时的替代可视化通道）。"""
    st, _, b = cam_cgi(cam, "startstream", value=str(port))
    if result_of(txt(b)) != "ok":
        return None, f"startstream -> {result_of(txt(b))}"
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.bind(("0.0.0.0", port)); s.settimeout(timeout)
    buf, frame = [], None
    try:
        while True:
            data, _ = s.recvfrom(65536)
            if data[:2] == b"\xff\xd8":
                buf = [data]
            elif buf:
                buf.append(data)
                if data[-2:] == b"\xff\xd9":
                    frame = b"".join(buf); break
    except socket.timeout:
        pass
    finally:
        s.close()
        cam_cgi(cam, "stopstream")
    return frame, ("ok" if frame else "未取到帧")


if __name__ == "__main__":
    import argparse, json
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", nargs="?", default="diagnose",
                    choices=["diagnose", "list", "sample", "sweep", "cleanup", "probe"])
    ap.add_argument("--cam", default="192.168.54.1")
    ap.add_argument("--out", default=".")
    ap.add_argument("--uuid", default="4D454930-0100-1000-8001-020A0003BD13",
                    help="清理用的 UUID —— 必须是**当初发起 req_acc 时用的那个**")
    a = ap.parse_args()
    if a.cmd == "diagnose":
        r = diagnose(a.cam)
        print("\n(JSON) " + json.dumps(r, ensure_ascii=False))
    elif a.cmd == "probe":
        r = probe_root(a.cam)
        print("=== DLNA 根对象三层判定 ===")
        print(f"  门是否开   : {'✅' if r['gate_open'] else '❌'} (children HTTP {r['children_http']})")
        print(f"  根是否存在 : {'✅' if r['root_exists'] else '❌'} title={r['root_title']!r} (HTTP {r['meta_http']})")
        print(f"  SystemUpdateID = {r['system_update_id']}")
        print(f"  子项数     : {len(r['children'])}")
        print(f"\n  ⇒ {r['verdict']}")
    elif a.cmd == "cleanup":
        # 用**同一 UUID**清理陈旧 pending，解决「需要更新app / invalid login」
        uid = a.uuid
        ok, cur = accctrl_cleanup(a.cam, uid)
        print("\n结果：", "✅ 已是/已恢复 ok" if ok else f"⚠️ {cur}")
        print("提示：清理成功后，请**只发一次** req_acc 再取 ok；切勿反复重发。")
    elif a.cmd == "sweep":
        st, _ = browse(a.cam)
        if st == 403:
            print("❌ 控制面 403 ⇒ accctrl 未达 ok。先跑 `cleanup`，再跑 `diagnose`。")
        else:
            print(f"控制面 HTTP {st} ⇒ 已放行，开始扫 ObjectID：")
            hits = sweep_object_ids(a.cam)
            print("\n命中：", hits if hits else "（无；可能内容树为空 / DMS 未启动）")
    elif a.cmd == "list":
        st, body = browse(a.cam)
        print("HTTP", st, len(body), "B")
        for it in parse_items(body)[:40]:
            print(f"  [{it['id']:>6}] {it['title'][:40]:42s} {it['res'][:80]}")
    else:
        f, msg = sample(a.cam)
        if f:
            p = os.path.join(a.out, "liveview_sample.jpg")
            open(p, "wb").write(f); print(f"✅ {msg}  {len(f)} B → {p}")
        else:
            print("❌", msg)
