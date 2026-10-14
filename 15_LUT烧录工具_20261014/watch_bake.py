#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
watch_bake.py — 监视目录，新素材一落地就自动套 LUT（“实时烧录”）

典型用法
    # ① 卡还插在电脑上：新拍的素材一出现在卡上就自动烧录
    python3 watch_bake.py --lut lut/vlog_to_709_17.vlt \
        --src /Volumes/LUMIX/DCIM --out ~/Pictures/LUT_baked

    # ② 只用 LUMIX Sync / 访达 把照片拖进某个中转目录，拖进来即烧录
    python3 watch_bake.py --lut lut/vlog_to_709_17.vlt \
        --src ~/Downloads/LUMIX --out ~/Pictures/LUT_baked

    # ③ 只跑一遍（给 cron / 快捷指令用）
    python3 watch_bake.py --lut ... --src ... --out ... --once

设计要点
    · **等文件写完**：连续两次采样 大小+mtime 不变，再等 --settle 秒才动手（相机/拷贝过程会分块写入）
    · **幂等**：状态文件记录 已处理文件 → (size, mtime)；同一文件不会重复烧
    · **风格自检**：默认开启；若判为“普通风格”会**警告但仍然烧**（可用 --skip-normal 直接跳过）
    · **不写源目录**：产物一律写到 --out，绝不碰卡
"""
import argparse, hashlib, json, os, shutil, subprocess, sys, time

IMG = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".heic", ".heif"}
VID = {".mp4", ".mov", ".m4v"}
HERE = os.path.dirname(os.path.abspath(__file__))
BAKE = os.path.join(HERE, "bake")
PY = sys.executable

def log(msg):
    print(f"[{time.strftime('%H:%M:%S')}] {msg}", flush=True)

def fingerprint(path):
    try:
        st = os.stat(path)
        return (st.st_size, int(st.st_mtime))
    except OSError:
        return None

def wait_stable(path, settle, timeout=600):
    """等文件写完：连续 2 次采样 (size, mtime) 相同后再等 settle 秒"""
    last = None
    t0 = time.time()
    while time.time() - t0 < timeout:
        fp = fingerprint(path)
        if fp is None:
            return False
        if fp == last and fp[0] > 0:
            time.sleep(settle)
            if fingerprint(path) == fp:
                return True
        last = fp
        time.sleep(0.7)
    return False

def run_bake(lut, src, dst, vlt_axis):
    ext = os.path.splitext(dst)[1].lower()
    cmd = [BAKE, "image" if ext in IMG else "video", lut, src, dst, "--vlt-axis", vlt_axis]
    r = subprocess.run(cmd, capture_output=True, text=True)
    return r.returncode == 0, (r.stdout + r.stderr).strip()

def check_style(path):
    r = subprocess.run([PY, os.path.join(HERE, "check_style.py"), "--json", path],
                       capture_output=True, text=True)
    try:
        d = json.loads(r.stdout)
        return list(d.values())[0]
    except Exception:
        return None

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--lut", required=True, help=".cube 或 .vlt")
    ap.add_argument("--src", required=True, help="监视目录（如 SD 卡 /Volumes/LUMIX/DCIM）")
    ap.add_argument("--out", required=True, help="产物目录（绝不写源目录）")
    ap.add_argument("--interval", type=float, default=2.0, help="扫描间隔秒（默认 2）")
    ap.add_argument("--settle", type=float, default=2.0, help="写完后再等几秒（默认 2）")
    ap.add_argument("--vlt-axis", default="variCam", choices=["variCam", "cube"])
    ap.add_argument("--include", default="jpg,jpeg,png,tif,tiff,heic,heif,mp4,mov,m4v")
    ap.add_argument("--once", action="store_true", help="只跑一遍")
    ap.add_argument("--no-style-check", action="store_true")
    ap.add_argument("--skip-normal", action="store_true", help="判为普通风格就跳过（默认仍烧但警告）")
    ap.add_argument("--state", default=os.path.join(HERE, ".watch_state.json"))
    a = ap.parse_args()

    if not os.path.exists(BAKE):
        log(f"❌ 找不到烧录器 {BAKE}（先编译：swiftc -O bake.swift -o bake）"); sys.exit(1)
    if not os.path.isdir(a.src):
        log(f"❌ 源目录不存在：{a.src}"); sys.exit(1)
    os.makedirs(a.out, exist_ok=True)
    exts = {"." + x.strip().lower().lstrip(".") for x in a.include.split(",") if x.strip()}

    state = {}
    if os.path.exists(a.state):
        try: state = json.load(open(a.state))
        except Exception: state = {}

    log(f"监视 {a.src}")
    log(f"   LUT   {a.lut}")
    log(f"   产物  {a.out}")
    log(f"   间隔 {a.interval}s / 静默 {a.settle}s / 轴序 {a.vlt_axis} / 类型 {sorted(exts)}")
    log("按 Ctrl-C 停止\n")

    n_ok = n_skip = 0
    try:
        while True:
            found = []
            for root, dirs, files in os.walk(a.src):
                dirs[:] = [d for d in dirs if not d.startswith(".")]
                for f in files:
                    if f.startswith("._") or f.startswith("."):
                        continue
                    if os.path.splitext(f)[1].lower() in exts:
                        found.append(os.path.join(root, f))
            for src in sorted(found):
                key = os.path.abspath(src)
                fp = fingerprint(src)
                if fp is None or state.get(key) == list(fp):
                    continue
                log(f"发现新素材 {os.path.relpath(src, a.src)}  ({fp[0]/1e6:.1f} MB)")
                if not wait_stable(src, a.settle):
                    log("   ⏳ 仍在写入，稍后重试"); continue
                if not a.no_style_check:
                    st = check_style(src)
                    if st and "verdict" in st:
                        v = st["verdict"]
                        log(f"   风格自检: {v.upper()}  (黑位P1={st['percentiles'].get('P1')}, "
                            f"真黑占比={st.get('black_fraction')})")
                        if v == "normal":
                            log(f"   ⚠️  {st.get('advice','')}")
                            if a.skip_normal:
                                log("   ⏭  按 --skip-normal 跳过"); state[key] = list(fingerprint(src)); continue
                base = os.path.basename(src)
                dst = os.path.join(a.out, base)
                if os.path.exists(dst):
                    stem, ext = os.path.splitext(base)
                    dst = os.path.join(a.out, f"{stem}_{int(time.time())}{ext}")
                ok, msg = run_bake(a.lut, src, dst, a.vlt_axis)
                if ok:
                    n_ok += 1
                    log(f"   ✅ 烧录完成 → {os.path.relpath(dst, a.out)}")
                    state[key] = list(fingerprint(src))
                else:
                    n_skip += 1
                    log(f"   ❌ 失败：{msg[:200]}")
                    state[key] = list(fingerprint(src))
                json.dump(state, open(a.state, "w"))
            if a.once:
                break
            time.sleep(a.interval)
    except KeyboardInterrupt:
        log("已停止")
    log(f"完成：成功 {n_ok}，失败 {n_skip}")

if __name__ == "__main__":
    main()
