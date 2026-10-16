#!/usr/bin/env python3
"""
受控复现 crash 001（StartingIndex=2147483647 → 疑似 dlna 崩溃）。

背景：
  2026-10-16 04:34 v1 fuzzer 记录 crash_cases/001_type_StartingIndex_2147483647.xml：
  发送合法 SOAP（仅 StartingIndex=INT32_MAX）后出现连接级异常，健康检查判死。
  但该判定未经"整机 vs dlna 进程 vs 挂起"分类，也未复现确认 ⇒ 本脚本做受控复现。

判据（三通道 + 计时）：
  cam80      = GET /cam.cgi?mode=getstate（相机 HTTP 栈活着？）
  dlna60606  = BrowseMetadata（dlna 进程活着？授权态？）
  计时       = 每个请求的响应秒数（>15s 记 hang）

流程：
  1. 基线：两次合法 BrowseMetadata（记录正常响应时间基线）。
  2. 复现：发送 001 原始 payload（30s 超时），记录精确结果。
  3. 梯度：围绕触发值扫 StartingIndex / RequestedCount 变体，定位边界。
  4. 每轮之间 5s 冷却；全程绝不发 req_acc（授权掉了就停，等物理重启）。

用法：
  python3 -u repro_crash.py <cam_ip> [--rounds N]   # N=重复原 payload 次数（默认 3）
输出：
  repro_log.jsonl（全量）+ 控制台摘要。崩溃输入另存 crash_cases/。
"""
import sys
import time
import json
import os
import re

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from fuzz_dlna import (http_post, make_body, raw_http, triad_health, auth_status,
                       tcp_alive, save_crash, DLNA_PORT, SERVICE)


def send_case(cam, case, body, timeout=30):
    if isinstance(body, str):
        body = body.encode("utf-8")
    req = (
        f"POST /Server0/CDS_control HTTP/1.1\r\nHost: {cam}:{DLNA_PORT}\r\n"
        "Accept-Charset: UTF-8\r\n"
        'Content-Type: text/xml; charset="utf-8"\r\n'
        f'SOAPAction: "{SERVICE}#Browse"\r\n'
        "User-Agent: Panasonic MIL DLNA CP UPnP/1.0\r\n"
        f"Content-Length: {len(body)}\r\n"
        "Connection: close\r\n\r\n"
    ).encode() + body
    return raw_http(cam, DLNA_PORT, req, timeout=timeout)


def classify(cam, after_err):
    """连接异常后的分类（简化版 on_connection_error，不复盘等待）。"""
    time.sleep(3.0)
    h = triad_health(cam)
    if h["dlna60606"] == "ok":
        return "alive(瞬时抖动)", h
    if h["cam80"] != "ok":
        return "CRASH(整机死)", h
    if h["dlna60606"] in ("CONNREFUSED", "CONNRESET"):
        return "DLNA_DOWN(dlna进程死,相机活)", h
    if h["dlna60606"] == "TIMEOUT":
        return "HANG(端口活无响应)", h
    return f"OTHER({h['dlna60606']})", h


def wait_recover(cam, tag, timeout_s=180):
    t0 = time.time()
    while time.time() - t0 < timeout_s:
        time.sleep(5)
        h = triad_health(cam)
        if h["dlna60606"] == "ok" and h["cam80"] == "ok":
            print(f"      [{int(time.time()-t0)}s] 已恢复")
            return True
    print("      超时未恢复 —— 需物理断电重启相机。")
    return False


def main():
    if len(sys.argv) < 2:
        print("usage: python3 -u repro_crash.py <cam_ip> [--rounds N]")
        sys.exit(1)
    cam = sys.argv[1]
    rounds = 3
    if "--rounds" in sys.argv:
        rounds = int(sys.argv[sys.argv.index("--rounds") + 1])

    os.makedirs("crash_cases", exist_ok=True)
    logfn = f"repro_log_{time.strftime('%Y%m%d_%H%M%S')}.jsonl"

    def L(**d):
        d["ts"] = time.time()
        with open(logfn, "a") as f:
            f.write(json.dumps(d, ensure_ascii=False) + "\n")

    print(f"[*] 目标 {cam}  复现轮数 {rounds}  日志 {logfn}")

    # 0. 授权检查（只读）
    a, d = auth_status(cam)
    print(f"[*] 授权态: {a} ({d})")
    if a == "dead":
        print("[!] 相机不可达。退出。")
        sys.exit(1)
    if a == "denied":
        print("[!] 403 未放行：先跑 handshake.py（本脚本不发 req_acc）。退出。")
        sys.exit(1)

    # 1. 基线
    print("[1] 基线（2 次合法 BrowseMetadata）...")
    base = []
    for i in range(2):
        e, st, _, dt = send_case(cam, "baseline", make_body(BrowseFlag="BrowseMetadata"))
        base.append(dt)
        print(f"    baseline#{i+1}: err={e} status={st} dt={dt:.3f}s")
        L(case="baseline", err=e, status=st, dt=dt)
        time.sleep(2)
    base_t = max(base) if base else 0.5
    print(f"    基线响应时间 ≈ {base_t:.2f}s\n")

    # 2. 复现原始 001 payload
    orig = open("crash_cases/001_type_StartingIndex_2147483647.xml", "rb").read()
    print(f"[2] 复现原始 payload（{rounds} 轮，30s 超时）...")
    for r in range(rounds):
        print(f"    round {r+1}/{rounds}: 发送 StartingIndex=2147483647 ...")
        e, st, head, dt = send_case(cam, "repro_orig", orig, timeout=30)
        verdict = "ok"
        if e:
            verdict, h = classify(cam, e)
            L(case="repro_orig", round=r + 1, err=e, status=st, dt=dt, verdict=verdict, health=h)
        else:
            L(case="repro_orig", round=r + 1, err=None, status=st, dt=dt, verdict=verdict)
        print(f"        结果: err={e} status={st} dt={dt:.2f}s → {verdict}")
        if "CRASH" in verdict or "DLNA_DOWN" in verdict or "HANG" in verdict:
            save_crash(verdict.split("(")[0].lower(), f"repro_orig_r{r+1}", orig)
            if "CRASH" in verdict or "DLNA_DOWN" in verdict:
                print("      等待恢复...")
                ok = wait_recover(cam, verdict)
                if not ok:
                    print("[!] 未恢复，本会话中止。请断电重启相机后再跑。")
                    sys.exit(3)
                # 恢复后确认授权（403 也可能：dlna 重启后会话在，授权通常还在）
                a2, d2 = auth_status(cam)
                print(f"      恢复后授权态: {a2} ({d2})")
                if a2 != "ok":
                    print("[!] 恢复后未放行 —— 需物理重启 + handshake。中止。")
                    sys.exit(3)
            time.sleep(10)
        else:
            time.sleep(5)

    # 3. 变体梯度（定位触发边界）
    variants = [
        ("idx_2p31-1",  dict(StartingIndex="2147483647")),
        ("idx_2p31-2",  dict(StartingIndex="2147483646")),
        ("idx_2p31",    dict(StartingIndex="2147483648")),
        ("idx_2p32-1",  dict(StartingIndex="4294967295")),
        ("idx_2p32",    dict(StartingIndex="4294967296")),
        ("idx_2p33",    dict(StartingIndex="8589934592")),
        ("idx_neg1",    dict(StartingIndex="-1")),
        ("idx_neg2",    dict(StartingIndex="-2")),
        ("idx_i32min",  dict(StartingIndex="-2147483648")),
        ("idx_huge19",  dict(StartingIndex="999999999999999999")),
        ("idx_big_cnt1", dict(StartingIndex="2147483647", RequestedCount="1")),
        ("idx_big_cnt100", dict(StartingIndex="2147483647", RequestedCount="100")),
        ("idx_big_cnt_max", dict(StartingIndex="2147483647", RequestedCount="4294967295")),
        ("cnt_max",     dict(RequestedCount="4294967295")),
        ("cnt_2p31",    dict(RequestedCount="2147483648")),
    ]
    print(f"\n[3] 变体梯度（{len(variants)} 个，5s 冷却）...")
    for name, kw in variants:
        body = make_body(BrowseFlag="BrowseMetadata", **kw)
        e, st, head, dt = send_case(cam, name, body, timeout=30)
        verdict = "ok"
        if e:
            verdict, h = classify(cam, e)
            L(case=name, err=e, status=st, dt=dt, verdict=verdict, health=h)
        else:
            L(case=name, err=None, status=st, dt=dt, verdict=verdict)
        mark = "  <<< 慢!" if dt > base_t * 3 and not e else ""
        print(f"    {name:18s} err={str(e):12s} status={st} dt={dt:7.2f}s {verdict}{mark}")
        if "CRASH" in verdict or "DLNA_DOWN" in verdict or "HANG" in verdict:
            save_crash(verdict.split("(")[0].lower(), f"variant_{name}", body)
            ok = wait_recover(cam, verdict)
            if not ok:
                sys.exit(3)
            a2, d2 = auth_status(cam)
            if a2 != "ok":
                print("[!] 恢复后未放行 —— 需物理重启 + handshake。中止。")
                sys.exit(3)
        time.sleep(5)

    print(f"\n[*] 完成。全量日志: {logfn}")
    print("    判读：CRASH=整机重启 · DLNA_DOWN=dlna 进程崩溃 · HANG=解析器挂起 · ok=存活")
    print("    若全部 ok 且无慢响应 ⇒ 001 是 v1 误报（当时相机本就处于 err_critical 异常态）。")


if __name__ == "__main__":
    main()
