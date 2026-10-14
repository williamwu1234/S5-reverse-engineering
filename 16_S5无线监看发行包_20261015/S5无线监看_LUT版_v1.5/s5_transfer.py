#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_transfer.py — 统一文件传输管理器（DC-S5 无线取片）

前提知识（实测定因）
    · DLNA 内容树（60606 Browse）在 **accctrl=ok** 时放行；
    · 原图/视频从 **50001 端口**下载（`DO<id>.JPG/MP4/MOV`）；
    · 内容树只在**回放模式**下有内容（家网实测）；「一边录制一边发送图像」
      在热点下是否让 rec 模式也有内容 —— **尚未定论**，watch 模式就是为此准备的。

用法
    python3 s5_transfer.py list  --cam 192.168.54.1                      # 列举全部
    python3 s5_transfer.py list  --cam ... --video                       # 只看视频
    python3 s5_transfer.py get   --cam ... --newest --lut vlog_to_709_33.cube \
                                 --base vlog_to_709_33.cube              # 最新一张照片+还原
    python3 s5_transfer.py get   --cam ... --all-videos --out VIDEOS     # 拉全部视频
    python3 s5_transfer.py watch --cam ... --out BAKED \
                                 --lut "VOL19 TXD GLOD 200T V2.cube" \
                                 --base vlog_to_709_33.cube              # 新照片一出现就下载+套LUT

安全
    只读：只发 SOAP Browse 与 HTTP GET 下载。不 setsetting、不删相机文件。
"""
import argparse, os, re, sys, time, urllib.error, urllib.request

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

import s5_content as C

try:
    import numpy as np
    from PIL import Image
    import s5_lut as L
    _LUT_OK = True
except Exception:
    _LUT_OK = False


# ---------------------------------------------------------------- 列举
def list_items(cam):
    st, body = C.browse(cam, "0", count=0)
    items = C.parse_items(body)
    fault = C.parse_fault(body)
    return st, fault, items


def is_video(it):
    return "videoItem" in it["cls"]


# ---------------------------------------------------------------- 下载（带进度）
def download_with_progress(cam, res_url, dst, label=""):
    """分块下载并打印进度。返回 (ok, bytes)。"""
    req = urllib.request.Request(res_url, headers={"User-Agent": C.UA_DLNA})
    try:
        r = urllib.request.urlopen(req, timeout=60)
        total = int(r.headers.get("Content-Length") or 0)
        os.makedirs(os.path.dirname(os.path.abspath(dst)) or ".", exist_ok=True)
        done = 0
        t0 = time.time()
        with open(dst, "wb") as f:
            while True:
                chunk = r.read(262144)
                if not chunk:
                    break
                f.write(chunk)
                done += len(chunk)
                if total and time.time() - t0 > 0.8:
                    pct = done * 100.0 / total
                    mbps = done / 1e6 / max(time.time() - t0, 0.01)
                    print(f"\r    {label} {pct:5.1f}%  {done/1e6:6.1f}/{total/1e6:.1f} MB "
                          f"({mbps:4.1f} MB/s)   ", end="", flush=True)
                    t0 = time.time()
        if total:
            print(f"\r    {label} 100.0%  {done/1e6:6.1f} MB  ✅             ", flush=True)
        return True, done
    except Exception as e:
        print(f"\r    {label} ❌ {e}")
        return False, 0


# ---------------------------------------------------------------- LUT 烘焙
def bake_photo(src, dst, lut_name, base_name, strength):
    """对照片套 LUT（串联 + 强度）。视频直接原样返回。"""
    if not lut_name:
        return None
    if not _LUT_OK:
        print("    ⚠️ 缺 numpy/Pillow，跳过 LUT")
        return None
    lib = L.LutLibrary(os.path.join(HERE, "lut"))
    try:
        lib.select(lut_name, base=base_name)
        lib.set_strength(strength)
    except Exception as e:
        print(f"    ⚠️ LUT 加载失败: {e}")
        return None
    try:
        im = Image.open(src).convert("RGB")
        arr = np.asarray(im, dtype=np.uint8)
        out = lib.apply_rgb(arr)
        Image.fromarray(out).save(dst, quality=95)
        return dst
    except Exception as e:
        print(f"    ⚠️ 烘焙失败: {e}")
        return None


# ---------------------------------------------------------------- 子命令
def cmd_list(a):
    st, fault, items = list_items(a.cam)
    print(f"Browse -> HTTP {st}" + (f"  UPnP {fault}" if fault else ""))
    if st != 200 or fault:
        if st == 403:
            print("403 = accctrl 未达 ok（授权门关着）。先让监视器拿到 ok 再试。")
        elif st == 0:
            print("HTTP 0 = 相机 60606 无响应（相机可能需要断电重启）。")
        return 1
    photos = [i for i in items if not is_video(i)]
    videos = [i for i in items if is_video(i)]
    print(f"共 {len(items)} 项：照片 {len(photos)} · 视频 {len(videos)}\n")
    rows = photos + videos
    for k, it in enumerate(rows):
        tag = "🎞" if is_video(it) else "📷"
        ext = os.path.splitext(it["res"].split("?")[0])[1].upper() or "?"
        print(f"  [{k:2d}] {tag} {it['title']:16s} {ext:5s}  {it['res'][:60]}")
    return 0


def _pick(items, a):
    """按参数选要下载的条目。"""
    rows = items
    sel = []
    if a.newest:
        photos = [i for i in items if not is_video(i)]
        if photos:
            sel = [max(photos, key=lambda x: x["id"])]
    if a.index is not None:
        if 0 <= a.index < len(rows):
            sel = [rows[a.index]]
        else:
            print(f"❌ index {a.index} 超出范围（共 {len(rows)} 项）")
            return []
    if a.all_photos:
        sel += [i for i in items if not is_video(i)]
    if a.all_videos:
        sel += [i for i in items if is_video(i)]
    if a.all:
        sel = list(items)
    # 去重保序
    seen, out = set(), []
    for i in sel:
        if i["id"] not in seen:
            seen.add(i["id"]); out.append(i)
    return out


def cmd_get(a):
    st, fault, items = list_items(a.cam)
    if st != 200 or fault:
        print(f"Browse 失败 HTTP {st} {fault}（先确认 accctrl=ok）")
        return 1
    sel = _pick(items, a)
    if not sel:
        print("没有选中任何条目（用 --newest/--index/--all-photos/--all-videos/--all）")
        return 2
    os.makedirs(a.out, exist_ok=True)
    print(f"下载 {len(sel)} 项 → {a.out}\n")
    n_ok = 0
    for it in sel:
        ext = os.path.splitext(it["res"].split("?")[0])[1] or ".bin"
        dst = os.path.join(a.out, it["title"] + ext)
        label = ("🎞 " if is_video(it) else "📷 ") + it["title"]
        ok, n = download_with_progress(a.cam, it["res"], dst, label)
        if ok:
            n_ok += 1
            if not is_video(it) and a.lut:
                baked = bake_photo(dst, os.path.splitext(dst)[0] + "_LUT.jpg",
                                   a.lut, a.base, a.strength)
                if baked:
                    print(f"      LUT → {os.path.basename(baked)}")
    print(f"\n完成：成功 {n_ok}/{len(sel)}")
    return 0


def cmd_watch(a):
    os.makedirs(a.out, exist_ok=True)
    state_file = os.path.join(a.out, ".seen.json")
    seen = set()
    if os.path.exists(state_file):
        try:
            seen = set(__import__("json").load(open(state_file)))
        except Exception:
            pass
    print(f"监视模式：{a.cam} → {a.out}   每 {a.interval}s 检查一次")
    if a.lut and not _LUT_OK:
        print("  ⚠️ 缺 numpy/Pillow，LUT 烘焙将跳过")
    print("  （若 rec 模式下始终无内容 ⇒ 「一边录制一边发送图像」在该配置下不导出）\n")
    n = 0
    while True:
        try:
            st, fault, items = list_items(a.cam)
        except Exception as e:
            print(f"  [{time.strftime('%H:%M:%S')}] 列举失败: {e}")
            items = []
        if st == 200 and not fault:
            for it in items:
                if it["id"] in seen:
                    continue
                is_v = is_video(it)
                if a.photos_only and is_v:
                    continue
                if a.videos_only and not is_v:
                    continue
                ext = os.path.splitext(it["res"].split("?")[0])[1] or ".bin"
                dst = os.path.join(a.out, it["title"] + ext)
                label = ("🎞 " if is_v else "📷 ") + it["title"]
                print(f"[{time.strftime('%H:%M:%S')}] ★ 发现新条目 {label}")
                ok, _ = download_with_progress(a.cam, it["res"], dst, label)
                if ok:
                    seen.add(it["id"])
                    n += 1
                    if not is_v and a.lut:
                        baked = bake_photo(dst, os.path.splitext(dst)[0] + "_LUT.jpg",
                                           a.lut, a.base, a.strength)
                        if baked:
                            print(f"      LUT → {os.path.basename(baked)}")
                    try:
                        import json
                        json.dump(sorted(seen), open(state_file, "w"))
                    except Exception:
                        pass
        if a.once:
            break
        time.sleep(a.interval)
    print(f"结束：新下载 {n} 项")
    return 0


def main():
    ap = argparse.ArgumentParser(description="DC-S5 无线文件传输")
    sub = ap.add_subparsers(dest="cmd", required=True)

    p = sub.add_parser("list"); p.add_argument("--cam", default="192.168.54.1")
    p.add_argument("--video", action="store_true")
    p.set_defaults(fn=cmd_list)

    g = sub.add_parser("get"); g.add_argument("--cam", default="192.168.54.1")
    g.add_argument("--out", default="downloads")
    g.add_argument("--index", type=int, default=None)
    g.add_argument("--newest", action="store_true")
    g.add_argument("--all", action="store_true")
    g.add_argument("--all-photos", action="store_true")
    g.add_argument("--all-videos", action="store_true")
    g.add_argument("--lut", default=None, help="对照片套的 LUT（不传=不套）")
    g.add_argument("--base", default="", help="前置还原（V-Log 素材时选 vlog_to_709_33.cube）")
    g.add_argument("--strength", type=float, default=1.0)
    g.set_defaults(fn=cmd_get)

    w = sub.add_parser("watch"); w.add_argument("--cam", default="192.168.54.1")
    w.add_argument("--out", default="baked")
    w.add_argument("--interval", type=float, default=5.0)
    w.add_argument("--photos-only", action="store_true")
    w.add_argument("--videos-only", action="store_true")
    w.add_argument("--once", action="store_true")
    w.add_argument("--lut", default=None)
    w.add_argument("--base", default="")
    w.add_argument("--strength", type=float, default=1.0)
    w.set_defaults(fn=cmd_watch)

    a = ap.parse_args()
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
