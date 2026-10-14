#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
check_style.py — 判断素材是不是 Log（V-Log/HLG）拍的，避免套错 LUT

为什么需要
    把 V-Log 的 LUT 套到 Standard/普通风格素材上，画面只会**变暗、变得更糟**。
    （实测：夜景 Standard 素材整体均值 8.3/255 → 套 VLog→709 后 5.8/255）
    Log 素材的指纹是：**黑位被抬高、对比度低、直方图挤在中间**；
    普通风格素材：黑位贴近 0、动态范围铺满。

判据（对亮度通道）
    · 黑位 P1 / 白位 P99
    · 中间调占比（P10..P90 之间的像素比例）
    · 低对比指标 (P99-P1)
    Log 的典型值：P1 ≥ 24、P99 ≤ 210、(P99-P1) ≤ 170、中间调占比高
    普通风格：P1 ≤ 12、P99 ≥ 230、(P99-P1) ≥ 200

用法
    python3 check_style.py <图片或视频...>          # 逐个给判定
    python3 check_style.py --json <file>            # 机器可读
视频会抽一帧（需要同目录的 ./build/grab，或系统有 ffmpeg）
"""
import argparse, json, os, subprocess, sys

def _luma(img):
    import numpy as np
    a = np.asarray(img.convert("RGB"), dtype=np.float32)
    return (0.2126 * a[:, :, 0] + 0.7152 * a[:, :, 1] + 0.0722 * a[:, :, 2]).ravel()

def analyze_image(path):
    import numpy as np
    from PIL import Image
    y = _luma(Image.open(path))
    return _stats(y)

def _stats(y):
    """判据核心：**Log 不可能有真黑**
    Panasonic V-Log 的黑位是 0.125（≈32/255），HLG 亦不下潜到 0。
    普通风格（Standard/CineLike…）黑位贴近 0。因此「是否存在真黑像素」是最稳的单一判据，
    在极端低调画面（大面积黑）上也不会失效。
    """
    import numpy as np
    p = {q: float(np.percentile(y, q)) for q in (0.1, 1, 5, 10, 50, 90, 95, 99, 99.9)}
    rng = p[99] - p[1]
    black_frac = float(np.mean(y < 16))          # 真黑像素占比
    # 只看「非黑」部分的中调集中度，避免大面积黑把指标带偏
    nz = y[y >= 16]
    mid = float(np.mean(nz <= p[90])) if nz.size > 500 else 0.0

    if black_frac > 0.005:
        verdict = "normal"
        advice = (f"像普通风格（{black_frac*100:.1f}% 的像素是真黑，Log 不可能有真黑）"
                  f" ⇒ 不要套 V-Log LUT，会变暗")
        score = 0
    elif p[1] >= 24 and p[99] <= 218:
        verdict = "log"
        advice = "很像 Log（黑位被抬高到 %.0f 且白位压到 %.0f）⇒ 需要套 Log→709 的 LUT" % (p[1], p[99])
        score = 8
    else:
        verdict = "uncertain"
        advice = "不确定 ⇒ 看黑位是否明显高于 16（Log）或贴 0（普通）"
        score = 4
    return dict(verdict=verdict, score=score, advice=advice,
                percentiles={f"P{k}": round(v, 1) for k, v in p.items()},
                black_fraction=round(black_frac, 4),
                midtone_ratio=round(mid, 3), range_P1_P99=round(rng, 1),
                mean=round(float(np.mean(y)), 1))


def _grab_video_frame(path, tmpdir):
    """用同目录的 build/grab 抽帧；失败则退回 ffmpeg"""
    here = os.path.dirname(os.path.abspath(__file__))
    grab = os.path.join(here, "build", "grab")
    out = os.path.join(tmpdir, "grabbed.jpg")
    if os.path.exists(grab):
        r = subprocess.run([grab, path, out], capture_output=True, text=True, timeout=180)
        if os.path.exists(out):
            return out
    try:
        r = subprocess.run(["ffmpeg", "-y", "-v", "error", "-ss", "1", "-i", path,
                            "-frames:v", "1", out], capture_output=True, timeout=180)
        if os.path.exists(out):
            return out
    except Exception:
        pass
    return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("files", nargs="+")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args()
    import tempfile
    results = {}
    with tempfile.TemporaryDirectory() as td:
        for f in a.files:
            ext = os.path.splitext(f)[1].lower()
            try:
                if ext in (".mp4", ".mov", ".m4v"):
                    fr = _grab_video_frame(f, td)
                    if not fr:
                        results[f] = {"error": "抽帧失败（缺 build/grab 与 ffmpeg）"}
                        continue
                    results[f] = analyze_image(fr)
                else:
                    results[f] = analyze_image(f)
            except Exception as e:
                results[f] = {"error": str(e)}
    if a.json:
        print(json.dumps(results, ensure_ascii=False, indent=2)); return
    for f, r in results.items():
        print(f"\n=== {os.path.basename(f)}")
        if "error" in r:
            print("  ⚠️", r["error"]); continue
        icon = {"log": "🟦", "normal": "🟩", "uncertain": "🟨"}[r["verdict"]]
        print(f"  {icon} 判定: {r['verdict'].upper()}  (Log 分 {r['score']}/8)")
        print(f"     黑位P1={r['percentiles']['P1']}  白位P99={r['percentiles']['P99']}  "
              f"跨度={r['range_P1_P99']}  中间调占比={r['midtone_ratio']}  均值={r['mean']}")
        print(f"     ⇒ {r['advice']}")

if __name__ == "__main__":
    main()
