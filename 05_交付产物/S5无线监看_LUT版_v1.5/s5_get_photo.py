#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5_get_photo.py — 从相机无线取一张照片并套上我们的还原 LUT（一条命令）

用法
    python3 s5_get_photo.py                    # 取最新一张
    python3 s5_get_photo.py --index 0          # 取列表第 0 张
    python3 s5_get_photo.py --no-lut           # 只下载不套 LUT
    python3 s5_get_photo.py --lut vlog_to_709_17.cube
    python3 s5_get_photo.py --shoot            # 先拍一张再取（当前照片风格需为 V-Log）

它会做什么
    ① 列出相机内容（**自动切回放模式** —— DLNA 内容只在回放模式导出）
    ② 下载指定/最新一张（原图，非缩略图）
    ③ 判风格（黑位判据）→ 套对应 LUT → 存对比图
    ④ 若用了 --shoot，办完自动切回拍摄模式

★ 照片风格必须匹配 LUT
    · 相机 `[照片风格]=V-Log`  → 用 `vlog_to_709_*.cube`（V-Log 黑位 ≈ 32/255）
    · 普通风格（Standard 等）  → **不要套 V-Log LUT**，只会变暗/过饱和
    本脚本会自动判定并给出警告。
"""
import argparse, os, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)

try:
    import numpy as np
    from PIL import Image
    import s5_lut as L
    import s5_content as C
except Exception as e:
    print(f"缺少依赖或模块：{e}")
    print("（需要 numpy + Pillow；它们在本项目自带运行时里都有）")
    sys.exit(1)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--cam", default="192.168.54.1")
    ap.add_argument("--lut", default="vlog_to_709_33.cube")
    ap.add_argument("--index", type=int, default=-1, help="-1=最新一张")
    ap.add_argument("--out", default="downloads")
    ap.add_argument("--no-lut", action="store_true")
    ap.add_argument("--shoot", action="store_true", help="先拍一张再取")
    a = ap.parse_args()
    os.makedirs(a.out, exist_ok=True)

    # ---- 可选：先拍一张 ----
    if a.shoot:
        print("[1] 切拍摄模式并拍一张…")
        C.cam_cgi(a.cam, "camcmd", value="recmode"); time.sleep(5)
        C.cam_cgi(a.cam, "camcmd", value="capture"); time.sleep(7)
        print("    完成")

    # ---- 切回放并列举 ----
    print("[2] 切回放模式并列举内容…")
    C.cam_cgi(a.cam, "camcmd", value="playmode"); time.sleep(4)
    st, body = C.browse(a.cam, "0", count=0)
    items = C.parse_items(body)
    photos = sorted([i for i in items if i["cls"].startswith("object.item.imageItem")],
                    key=lambda x: x["id"])
    if not photos:
        print(f"    ❌ 没列出照片（HTTP {st}）。先确认 accctrl 已达 ok。")
        return 2
    it = photos[a.index]
    print(f"    照片 {len(photos)} 张，选 {it['title']}（原图 res）")

    # ---- 下载 ----
    ext = os.path.splitext(it["res"])[1] or ".JPG"
    dst = os.path.join(a.out, it["title"] + ext)
    print(f"[3] 下载 → {dst}")
    t0 = time.time(); ok, n = C.download(a.cam, it["res"], dst); dt = time.time() - t0
    if not ok:
        print("    ❌ 下载失败"); return 3
    print(f"    ✅ {n:,} 字节  {dt:.1f}s  ({n*8/dt/1e6:.1f} Mbps)")

    if a.no_lut:
        print("[4] 按要求跳过 LUT"); return 0

    # ---- 判风格 + 套 LUT ----
    print("[4] 判风格并套 LUT…")
    im = Image.open(dst).convert("RGB")
    arr = np.asarray(im, dtype=np.uint8)
    y = np.asarray(im.convert("L"), dtype=np.float32).ravel()
    p1 = float(np.percentile(y, 1)); black = float((y < 16).mean())
    is_log = p1 >= 24 and black <= 0.005
    print(f"    黑位 P1={p1:.0f}  真黑占比={black*100:.1f}%  →  "
          f"{'🟦 LOG（适合 V-Log LUT）' if is_log else '🟩 普通风格'}")
    if not is_log and "vlog" in a.lut.lower():
        print("    ⚠️  这张**不是 V-Log**，套 V-Log LUT 会变暗/过饱和。")
        print("        想正确还原，请把相机 [照片风格] 设为 V-Log 后重拍。")

    lib = L.LutLibrary(os.path.join(HERE, "lut"))
    info = lib.select(a.lut)
    t0 = time.time(); out = lib.apply_rgb(arr); dt = (time.time() - t0) * 1000
    d = np.abs(arr.astype(np.int16) - out.astype(np.int16))
    print(f"    {info['name']} (N={info['size']})  全尺寸 {im.size[0]}x{im.size[1]}: "
          f"{dt:.0f} ms  平均像素差 {d.mean():.1f}")

    stem = os.path.splitext(dst)[0]
    Image.fromarray(out).save(stem + "_LUT.jpg", quality=95)
    t = im.copy(); t.thumbnail((1800, 1800))
    Image.fromarray(np.asarray(t, dtype=np.uint8)).save(stem + "_原图预览.jpg", quality=93)
    tb = lib.apply_rgb(np.asarray(t, dtype=np.uint8))
    Image.fromarray(tb).save(stem + "_套LUT预览.jpg", quality=93)
    print(f"    ✅ 产出：")
    print(f"       {stem}_LUT.jpg          （全尺寸还原）")
    print(f"       {stem}_原图预览.jpg      /  {stem}_套LUT预览.jpg（对比）")

    if a.shoot:
        print("[5] 切回拍摄模式…")
        C.cam_cgi(a.cam, "camcmd", value="recmode")
    return 0


if __name__ == "__main__":
    sys.exit(main())
