#!/usr/bin/env python3
"""
DC-S5 一次性正确握手脚本（血泪教训版 v2，2026-10-16）。

关键教训（勿再犯）：
  · req_acc 是【一次性握手】，不是状态查询。短时间连发 → 相机弹"连接失败"/
    err_user_refused / invalid login → 必须重启相机。
  · ★ v2 修复：设备名用权威口径 "LUMIX Sync"（v1 错用 "S5Monitor"）。
  · ★ v2 新增：幂等预检 —— 若 dlna 已放行（200/500）则直接跳过 req_acc，
    杜绝"已授权还发 req_acc"的重复握手。
  · 正确顺序（在超时窗口内一气呵成）：
      ① req_acc（唯一一次）
      ② camcmd playmode（紧接着发，电脑指令让相机进回放）
      ③ 轮询 getstate 直到 <result>ok</result>
  · "连接失败" = 超时 = 电脑没在超时窗口内完成 ①②。

用法（相机已重启、进入"等待WiFi连接"状态后）：
  python3 handshake.py <相机IP> [--device-id UUID] [--device-name 名] [--cleanup]
  --cleanup: 先单发一次 req_acc_can（同一 UUID）清陈旧 pending —— 仅确认无其他客户端时用。

判据：
  getstate 返回 <result>ok</result> = 会话建立成功。
  之后 dlna BrowseMetadata 应返回 200（放行），即可开始 fuzz。
"""
import os
import sys
import time
import urllib.parse
import urllib.request

DEFAULT_ID = "4D454930-0100-1000-8001-020A0003BD13"
DEFAULT_NAME = "LUMIX Sync"
UA = {"User-Agent": "LUMIX Sync", "Accept-Charset": "UTF-8"}
# 端口可由环境变量覆盖（S5_HTTP_PORT）—— 用途：接 mock_cam.py 做离线 dry-run
HTTP_PORT = int(os.environ.get("S5_HTTP_PORT", "80"))


def cam_base(cam):
    return "http://%s" % (cam if HTTP_PORT == 80 else "%s:%d" % (cam, HTTP_PORT))


def get(cam, path, timeout=8):
    url = f"{cam_base(cam)}/cam.cgi?{path}"
    req = urllib.request.Request(url, headers=UA)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.read().decode("utf-8", "replace")
    except Exception as e:
        return f"__ERR__ {e}"


def main():
    if len(sys.argv) < 2:
        print("usage: python3 handshake.py <cam_ip> [--device-id UUID] [--device-name 名] [--cleanup]")
        sys.exit(1)
    cam = sys.argv[1]
    devid = DEFAULT_ID
    devname = DEFAULT_NAME
    cleanup = False
    args = sys.argv[2:]
    i = 0
    while i < len(args):
        if args[i] == "--device-id":
            devid = args[i + 1]; i += 2
        elif args[i] == "--device-name":
            devname = args[i + 1]; i += 2
        elif args[i] == "--cleanup":
            cleanup = True; i += 1
        else:
            i += 1

    print(f"[*] 目标 {cam}，device_id={devid}，device_name={devname}")
    print("[*] 前置确认：相机已重启、进入「等待WiFi连接」状态、Mac 已连上热点\n")

    # 0. 幂等预检（只读，不发 accctrl）：dlna 已放行则直接跳过 req_acc
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    from fuzz_dlna import auth_status
    a, d = auth_status(cam)
    if a == "ok":
        print(f"[0] dlna 已放行（HTTP {d}）→ 跳过 req_acc（幂等，绝不重发）。")
        r = get(cam, "mode=getstate")
        if "<result>ok</result>" in r.replace(" ", ""):
            print("✅ 会话已就绪，直接开始 fuzz：python3 -u fuzz_dlna.py %s --strategy all" % cam)
            return
        print("    dlna 放行但 getstate 非 ok，继续 ②③ 走流程（仍不发 req_acc）。")
        skip_acc = True
    elif a == "dead":
        print(f"[0] 相机不可达（{d}）—— 检查热点连接/相机状态。退出。")
        sys.exit(1)
    else:
        skip_acc = False
        print(f"[0] dlna 403 未放行 → 需要完整握手。")

    if cleanup and not skip_acc:
        print("[0b] --cleanup：单发 req_acc_can（同一 UUID，仅一次）清陈旧 pending...")
        r = get(cam, urllib.parse.urlencode(
            {"mode": "accctrl", "type": "req_acc_can", "value": devid, "value2": ""}))
        print(f"    响应: {r.strip()}")
        time.sleep(2)

    if not skip_acc:
        # ① req_acc（唯一一次）
        print("[1] req_acc（唯一一次握手）...")
        r = get(cam, urllib.parse.urlencode(
            {"mode": "accctrl", "type": "req_acc", "value": devid, "value2": devname}))
        print(f"    accctrl 响应: {r.strip()}")

    # ② 紧接着 camcmd playmode（进回放）
    print("[2] camcmd playmode（电脑指令进回放）...")
    r2 = get(cam, "mode=camcmd&value=playmode")
    print(f"    camcmd 响应: {r2.strip()}")

    # ③ 轮询 getstate（只轮询，绝不再发 req_acc）
    print("[3] 轮询 getstate（最多 90s，不发 req_acc）...")
    ok = False
    for i in range(45):
        time.sleep(2)
        st = get(cam, "mode=getstate", timeout=6)
        is_ok = "<result>ok</result>" in st.replace(" ", "")
        if i == 0 or i % 5 == 0 or is_ok:
            print(f"    [{i*2}s] getstate = {st.strip()}")
        if is_ok:
            print("\n✅ getstate=ok，握手成功！可以开始 fuzz。")
            ok = True
            break

    if not ok:
        print("\n⚠️ 90s 内 getstate 未变 ok。")
        print("   可能原因：① 相机不在「等待WiFi连接」状态 ② UUID 不匹配 ③ 相机拒绝")
        print("   请【重启相机】重新进等待状态，再跑本脚本一次。切勿手动连发 req_acc！")
        sys.exit(2)

    # ④ 验证 dlna 放行
    print("[4] 验证 dlna BrowseMetadata ...")
    from fuzz_dlna import http_post, make_body
    err, status = http_post(cam, make_body(BrowseFlag="BrowseMetadata"), timeout=8)
    print(f"    dlna BrowseMetadata: err={err} http={status}")
    if status in (200, 500):
        print("✅ dlna 放行，可开始 fuzz：python3 -u fuzz_dlna.py %s --strategy all" % cam)
        print("   （500 = SOAP Fault 701 也是放行；403 才是未放行）")
    elif status == 403:
        print("⚠️ dlna 仍未放行（403）。getstate ok 但 DLNA 受限（ok_under_research）？")
        print("   按权威文档 §2-4：ok_under_research_no_msg ⇒ 403。请在相机屏幕确认已【允许】，")
        print("   或重启相机重跑。切勿再发 req_acc。")
    else:
        print("⚠️ dlna 异常（%s / %s）。先跑 repro_crash.py 检查相机健康。" % (err, status))


if __name__ == "__main__":
    main()
