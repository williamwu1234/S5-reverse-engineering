#!/usr/bin/env python3
"""
fuzz_model.py —— 机型 / 客户端身份面 fuzzer（DC-S5，2026-10-16）

为什么有这条线（离线证据，见 ../15_机型身份面_离线反汇编证据_20261016/NOTES.md）：
  · dlna 的 SOAP 体里 `<pana:X_FromCP>` 是被显式 strcmp 匹配并取值存进会话结构的
    **客户端身份字段**（dlna 0xe7834 / 0xe7860）。
  · dlna 另有一个身份注册函数，对身份串做 **9 字节前缀比对 "LumixLink"**，
    命中/未命中走两套分支（能力字继承与否，dlna 0x13ef8 / 0x13f38）。
  · dlna 解析 6 个 Panasonic 私有 HTTP 头：X_Panasonic_Cam_{VRec,PictBrst,Sync,PRec,Req,Transfer}。
  · psm 的**机型能力面** = `cam.cgi?mode=getinfo&type=capability`，且它是**整串比较分派**
    （psm 0x3f630，对照串 cam.cgi?mode=camcmd&value=recmode）。
  ⇒ 这些都是"相机按客户端机型/身份改变行为"的门 ⇒ 用不同身份串打同一请求，看响应是否分化。

两档（默认只跑 A 档）：
  A 档（默认，红线安全，纯只读）：
    A1 fromcp   —— 变换 SOAP 的 <pana:X_FromCP>（前缀命中/大小写垃圾/超长/截断/编码/XML 注入）
    A2 headers  —— 6 个 X_Panasonic_Cam_* 私有头的存在性/取值/重复/超长/大小写
    A3 query    —— cam.cgi 查询串分派一致性（mode/getinfo&type=capability 的换序/编码/多余参数）
    A4 ua       —— User-Agent / 机型名伪装（DC-S5 / DC-S5M2 / DC-S1H / DMC-MC801 / LUMIX Sync / Image App …）
  B 档（--tier b --confirm-accctrl，**每个会话窗口至多发一次 req_acc**）：
    B1 用变体 value/value2 做 accctrl 身份枚举，看相机是否按身份授予不同权限。

红线（继承权威文档 §4-1）：
  · 绝不在 A 档发任何 accctrl；
  · B 档每窗口 req_acc 至多一次、req_acc_can 至多一次、且必须显式 --confirm-accctrl；
  · 只发 HTTP，不写 flash、不刷固件、不发 0x9406 子码/0x9422/0x9423/0x940d；
  · 掉线即停（不重发任何握手）。
  · ★ 会话保活：dlna 静默 ≈30s 即 403 且不可恢复（14:52 实证）⇒ 本脚本所有非 dlna 档
    每 ≤10s 自动补一次 BrowseMetadata 心跳（复用 fuzz_dlna.dlna_touch）。

用法：
  python3 -u fuzz_model.py <cam_ip> --strategy all              # A 档全跑（默认，只读）
  python3 -u fuzz_model.py <cam_ip> --strategy fromcp --dry-run # 只列用例不发
  python3 -u fuzz_model.py <cam_ip> --strategy ua --diff        # 打印身份→响应差异表
  python3 -u fuzz_model.py <cam_ip> --tier b --confirm-accctrl --value2 "DC-S5M2" --strategy accctrl

输出：model_log_*.jsonl（每条：case/身份/状态码/响应长度/响应摘要/耗时）
       身份差异表直接打到控制台（--diff 时落盘 model_diff_*.txt）。
"""
import hashlib
import json
import os
import re
import socket
import sys
import time
import urllib.parse

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_dlna import (DLNA_PORT, CAM_HTTP_PORT, CONTROL, SERVICE, UA_DLNA,
                       make_body, raw_http, http_post, dlna_touch, auth_status,
                       tcp_alive, ACC_UUID, DEV_NAME)

# ---------------------------------------------------------------- 身份数据

# 机型族（Panasonic 相机机身名 / 厂商名 / 家族名）—— 仅作"身份伪装"用，不做任何写入
PANASONIC_MODELS = [
    "DC-S5", "DC-S5M2", "DC-S5M2X", "DC-S1", "DC-S1R", "DC-S1H", "DC-S9",
    "DC-GH5", "DC-GH6", "DC-G9", "DC-G100", "DMC-MC801", "DMC-CM1",
]
APP_IDENTITIES = [
    "LUMIX Sync", "LUMIX Sync2", "Panasonic Image App", "LUMIX Sync for iOS",
    "LUMIX Sync/1.0", "Panasonic Image App/2.0", "Panasonic MIL DLNA CP",
]
# X_FromCP 前缀门的变体（离线证据 A1/A3：9 字节 "LumixLink" 前缀）
FROMCP_VARIANTS = [
    "LumixLink2.0", "LumixLink", "LumixLink1.0", "LumixLink9.9",
    "LumixLink2.1", "LumixLinkX", "LumixLin", "LumixLink2.0 ",
    "lumixlink2.0", "LUMIXLINK2.0", "Lumixlink2.0",
    "", " ", "0", "-1", "null", "true",
    "LumixLink2.0" + "A" * 64, "LumixLink2.0" + "A" * 1024,
    "A" * 30, "A" * 64, "A" * 300,
    "%s%s%s%s%s%s%s%s%s%s", "../../../../etc/passwd",
    "LumixLink2.0\x00XXXX", "LumixLink2.0\r\nX-Injected: 1",
    "LumixLink2.0</pana:X_FromCP><u:Browse><ObjectID>0</ObjectID>",
    "ＬｕｍｉｘＬｉｎｋ２．０", "\u0000\u0001\u0002",
]
# 私有头取值
HDR_VALUES = [
    "1", "0", "-1", "2", "true", "yes", "0x1", "4294967295",
    "A" * 32, "A" * 256, "A" * 4096,
    "%s%s%s%s", "..%2f..%2f", "<x/>", "' OR 1=1--", "\xff\xfe",
]
VENDOR_HEADERS = ["X_Panasonic_Cam_Sync", "X_Panasonic_Cam_Req", "X_Panasonic_Cam_Transfer",
                  "X_Panasonic_Cam_PRec", "X_Panasonic_Cam_VRec", "X_Panasonic_Cam_PictBrst",
                  "X_DeviceName"]
# cam.cgi 只读查询面（★ 只允许这些，任何含 accctrl/setsetting/camcmd 的写动作一律不出现在 A 档）
SAFE_QUERIES = [
    "mode=getstate", "mode=getinfo", "mode=getinfo&type=capability",
    "mode=getinfo&type=allmenu", "mode=getinfo&type=menulist",
    "mode=getinfo&type=version", "mode=getinfo&type=modelname",
    "mode=getcurmenu", "mode=getsetting",
]
# 分派一致性变体（psm 0x3f630 是整串比较）
QUERY_MUTATIONS = [
    ("cap_swap",         "type=capability&mode=getinfo"),
    ("cap_upper_mode",   "mode=GETINFO&type=capability"),
    ("cap_upper_type",   "mode=getinfo&type=CAPABILITY"),
    ("cap_extra",        "mode=getinfo&type=capability&x=1"),
    ("cap_trailing_amp", "mode=getinfo&type=capability&"),
    ("cap_dup_mode",     "mode=getinfo&mode=getinfo&type=capability"),
    ("cap_plus_space",   "mode=getinfo&type=capability+"),
    ("cap_pct2b",        "mode=getinfo&type=capability%2b"),
    ("cap_pct00",        "mode=getinfo&type=capability%00"),
    ("cap_semispace",    "mode=getinfo;&type=capability"),
    ("cap_type_first_dq", "mode=getinfo&type=\"capability\""),
    ("cap_longpad",      "mode=getinfo&type=capability&pad=" + "A" * 2048),
    ("cap_nul_after",    "mode=getinfo%00&type=capability"),
    ("model_x_formcp_ua", "mode=getinfo&type=capability"),
]

STATES = {"sent": 0, "diff": 0}


def logline(d, logfile):
    if logfile:
        d = dict(ts=time.time(), **d)
        with open(logfile, "a") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


# ---------------------------------------------------------------- 用例生成（A 档）

def make_fromcp_body(val):
    """把模板里的 X_FromCP 取值替换掉（模板固定，替换点唯一）。"""
    return make_body(BrowseFlag="BrowseMetadata").replace(
        "<pana:X_FromCP>LumixLink2.0</pana:X_FromCP>",
        "<pana:X_FromCP>%s</pana:X_FromCP>" % val)


def _dlna_raw(extra_headers, cam="CAMIP", body=None):
    body = body if body is not None else make_body(BrowseFlag="BrowseMetadata")
    body_b = body.encode() if isinstance(body, str) else body
    hdrs = "".join("%s: %s\r\n" % (k, v) for k, v in extra_headers.items())
    return (("POST %s HTTP/1.1\r\nHost: %s:%d\r\n"
             "Accept-Charset: UTF-8\r\n"
             'Content-Type: text/xml; charset="utf-8"\r\n'
             'SOAPAction: "%s#Browse"\r\n'
             "User-Agent: %s\r\n%s"
             "Content-Length: %d\r\nConnection: close\r\n\r\n")
            % (CONTROL, cam, DLNA_PORT, SERVICE, UA_DLNA, hdrs, len(body_b))).encode() + body_b


def mutate_model(cam):
    """给 fuzz_dlna.py --strategy model 用的生成器：yield (name, (kind, payload))。"""
    yield ("model_baseline_fromcp", ("dl", make_body(BrowseFlag="BrowseMetadata")))
    # A1 X_FromCP
    for i, v in enumerate(FROMCP_VARIANTS):
        yield ("model_fromcp_%02d_%s" % (i, re.sub(r"[^A-Za-z0-9]", "", v)[:16] or "empty"),
               ("dl", make_fromcp_body(v)))
    # A2 私有头
    for h in VENDOR_HEADERS:
        yield ("model_hdr_%s_absent_probe" % h, ("raw", {"raw": _dlna_raw({}), "port": DLNA_PORT, "timeout": 15}))
        for j, val in enumerate(HDR_VALUES):
            yield ("model_hdr_%s_%02d" % (h, j),
                   ("raw", {"raw": _dlna_raw({h: val}), "port": DLNA_PORT, "timeout": 15}))
        yield ("model_hdr_%s_dup" % h,
               ("raw", {"raw": _dlna_raw({h: "1", h + "_2": "2"}), "port": DLNA_PORT, "timeout": 15}))
    # A3 cam.cgi 分派一致性
    for name, q in QUERY_MUTATIONS:
        yield ("model_query_" + name, ("camcgi", {"query": q, "ua": "LUMIX Sync"}))
    for q in SAFE_QUERIES:
        yield ("model_query_read_" + re.sub(r"[^A-Za-z0-9]", "_", q),
               ("camcgi", {"query": q, "ua": "LUMIX Sync"}))
    # A4 UA / 机型伪装（打在 cam.cgi 只读面与 dlna 面各一次）
    for m in PANASONIC_MODELS + APP_IDENTITIES:
        tag = re.sub(r"[^A-Za-z0-9]", "_", m)
        yield ("model_ua_camcgi_" + tag, ("camcgi", {"query": "mode=getinfo", "ua": m}))
        yield ("model_ua_dlna_" + tag,
               ("raw", {"raw": _dlna_raw({"User-Agent-x": ""}).replace(
                   ("User-Agent: %s" % UA_DLNA).encode(), ("User-Agent: %s" % m).encode()),
                   "port": DLNA_PORT, "timeout": 15}))


# ---------------------------------------------------------------- 独立运行器（身份差异表）

def probe(cam, name, query=None, raw=None, port=None, ua="LUMIX Sync", timeout=10):
    """发一个只读探测，返回 dict（含响应长度/摘要/hash）。"""
    if raw is not None:
        e, st, head, dt = raw_http(cam, port, raw, timeout=timeout)
        body = head
    else:
        host = cam if CAM_HTTP_PORT == 80 else "%s:%d" % (cam, CAM_HTTP_PORT)
        req = ("GET /cam.cgi?%s HTTP/1.1\r\nHost: %s\r\nUser-Agent: %s\r\n"
               "Accept-Charset: UTF-8\r\nConnection: close\r\n\r\n"
               % (query, host, ua)).encode()
        e, st, head, dt = raw_http(cam, CAM_HTTP_PORT, req, timeout=timeout)
        body = head
    return {"case": name, "err": e, "status": st, "len": len(body or b""),
            "sha": hashlib.sha256(body or b"").hexdigest()[:16],
            "snippet": (body or b"")[:120].decode("latin1", "replace").replace("\r\n", " "),
            "dt": round(dt, 3), "query": query}


def run_runner(cam, strategy, diff, dry_run, logfile):
    """A 档独立运行器：逐用例只读探测 + 身份差异表。"""
    cases = []
    if strategy in ("all", "fromcp"):
        cases += [("fromcp_%02d" % i, dict(raw=make_fromcp_body(v).encode(), port=DLNA_PORT))
                  for i, v in enumerate(FROMCP_VARIANTS)]
    if strategy in ("all", "headers"):
        for h in VENDOR_HEADERS:
            for j, val in enumerate(HDR_VALUES):
                cases.append(("hdr_%s_%02d" % (h, j),
                              dict(raw=_dlna_raw({h: val}, cam=cam), port=DLNA_PORT)))
    if strategy in ("all", "query"):
        cases += [("q_" + n, dict(query=q)) for n, q in QUERY_MUTATIONS]
        cases += [("q_read_" + re.sub(r"[^A-Za-z0-9]", "_", q), dict(query=q)) for q in SAFE_QUERIES]
    if strategy in ("all", "ua"):
        for m in PANASONIC_MODELS + APP_IDENTITIES:
            cases.append(("ua_cam_%s" % re.sub(r"[^A-Za-z0-9]", "_", m),
                          dict(query="mode=getinfo", ua=m)))

    print("[*] 目标 %s  strategy=%s  用例 %d  tier=A(只读)  dry_run=%s"
          % (cam, strategy, len(cases), dry_run))
    if dry_run:
        for n, kw in cases:
            print("    %-46s %s" % (n, {k: (v[:60] if isinstance(v, bytes) else v)
                                        for k, v in kw.items()}))
        print("[*] dry-run 结束，未发任何请求。")
        return 0

    # 授权确认（只读判据）
    a, d = auth_status(cam)
    print("[*] dlna 授权态: %s (%s)" % (a, d))
    if a != "ok":
        print("[!] dlna 未放行（%s）。A 档只读探测也建议先跑 handshake.py 建立会话。" % a)
    if a == "dead":
        print("[!] 相机不可达。退出。")
        return 2

    base = None
    rows = []
    for n, kw in cases:
        dlna_touch(cam)
        r = probe(cam, n, **kw)
        logline(r, logfile)
        if base is None:
            base = r
        same = (r["sha"] == base["sha"] and r["status"] == base["status"])
        if not same:
            STATES["diff"] += 1
        rows.append((n, r, same))
        if not same or STATES["sent"] % 20 == 0:
            print("    %-46s st=%-5s len=%-6d dt=%5.2fs %s"
                  % (n, r["status"], r["len"], r["dt"], "" if same else "★与基线不同"))
        STATES["sent"] += 1

    print("\n[*] 完成 %d 个用例，其中 %d 个响应与基线不同。" % (len(rows), STATES["diff"]))
    if diff:
        fn = "model_diff_%s.txt" % time.strftime("%Y%m%d_%H%M%S")
        with open(fn, "w") as f:
            f.write("# 身份差异表（基线 = 第一个用例）\n")
            f.write("# 基线: %s st=%s len=%d sha=%s\n" % (base["case"], base["status"], base["len"], base["sha"]))
            for n, r, same in rows:
                f.write("%-46s st=%-5s len=%-6d sha=%-16s %s  %s\n"
                        % (n, r["status"], r["len"], r["sha"], "SAME" if same else "DIFF", r["snippet"][:60]))
        print("    差异表已存 %s" % fn)
    print("    判读：DIFF 集中出现的身份族 = 相机按该身份改变了行为（机型门的直接证据）。")
    return 0


# ---------------------------------------------------------------- B 档：accctrl 身份枚举

def run_tier_b(cam, value, value2, confirm, logfile):
    """每个会话窗口只发一次 req_acc（红线），用变体身份，看授权结果是否分化。"""
    if not confirm:
        print("[!] B 档会触碰 accctrl（红线面）。必须显式加 --confirm-accctrl 才会执行。")
        return 3
    print("[*] B 档：单次 req_acc 身份枚举  value=%r  value2=%r" % (value, value2))
    a, d = auth_status(cam)
    print("[*] 预检 dlna: %s (%s)" % (a, d))
    if a == "ok":
        print("[0] dlna 已放行 ⇒ 跳过 req_acc（幂等，绝不重发）。")
        return 0
    if a == "dead":
        print("[!] 相机不可达。退出。")
        return 2

    host = cam if CAM_HTTP_PORT == 80 else "%s:%d" % (cam, CAM_HTTP_PORT)
    url = "http://%s/cam.cgi?%s" % (host, urllib.parse.urlencode(
        {"mode": "accctrl", "type": "req_acc", "value": value, "value2": value2}))
    import urllib.request as U
    try:
        r = U.urlopen(U.Request(url, headers={"User-Agent": "LUMIX Sync"}), timeout=8).read()
        r = r.decode("utf-8", "replace")
    except Exception as ex:
        print("[!] req_acc 发送失败: %s" % ex)
        r = "__ERR__ %s" % ex
    print("    req_acc 响应: %s" % r.strip()[:200])
    logline({"case": "tierB_req_acc", "value": value, "value2": value2, "resp": r}, logfile)
    # playmode + 只轮询
    try:
        U.urlopen(U.Request("http://%s/cam.cgi?mode=camcmd&value=playmode" % host,
                            headers={"User-Agent": "LUMIX Sync"}), timeout=8).read()
    except Exception:
        pass
    for i in range(30):
        time.sleep(2)
        s = auth_status(cam)
        if s[0] == "ok":
            print("    ✅ 该身份被授予（dlna %s）—— 记住此身份变体，作为对照。" % (s[1],))
            logline({"case": "tierB_result", "value2": value2, "auth": "ok"}, logfile)
            return 0
        if s[0] == "dead":
            print("    [!] 掉线。停止（不重发 req_acc）。")
            return 2
    print("    ✗ 30 次轮询后仍 403（该身份未被授予，或需在相机屏幕点【允许】）。")
    print("      红线：本窗口不再发 req_acc。换身份 = 重启相机后再来一轮。")
    return 1


# ---------------------------------------------------------------- main

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    cam = sys.argv[1]
    strategy = "all"
    tier = "a"
    diff = False
    dry_run = False
    confirm = False
    value = ACC_UUID
    value2 = DEV_NAME
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        k = args[i]
        if k == "--strategy":
            strategy = args[i + 1]; i += 2
        elif k == "--tier":
            tier = args[i + 1]; i += 2
        elif k == "--diff":
            diff = True; i += 1
        elif k == "--dry-run":
            dry_run = True; i += 1
        elif k == "--confirm-accctrl":
            confirm = True; i += 1
        elif k == "--value":
            value = args[i + 1]; i += 2
        elif k == "--value2":
            value2 = args[i + 1]; i += 2
        else:
            i += 1

    logfile = None
    if not dry_run:
        logfile = "model_log_%s.jsonl" % time.strftime("%Y%m%d_%H%M%S")
    print("[*] 日志: %s" % logfile)
    if tier == "b" or strategy == "accctrl":
        return run_tier_b(cam, value, value2, confirm, logfile)
    return run_runner(cam, strategy, diff, dry_run, logfile)


if __name__ == "__main__":
    sys.exit(main())
