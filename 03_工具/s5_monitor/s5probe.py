#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
s5probe.py — DC-S5 设置组合枚举测试器

用途：在**你手动改动相机某一项设置**之后，跑一次本工具，
      它会同时测出两件事并追加到 CSV：

        ① 【控制面】camctrl 是否可用（逐条命令实测）
        ② 【取景面】30 秒流的真实质量（到达速率 / 空档 / 丢弃 / 抖动 / 最大帧间隔）

从而找出「哪一组相机设置能让触摸对焦可用 + 画面不卡不跳帧」。

前置：s5monitor.py 已在运行（默认 127.0.0.1:8080）

用法：
    python3 s5probe.py --label "触摸设置=AF+AE, 对焦=AFS"
    python3 s5probe.py --label "省电=OFF" --secs 20
    python3 s5probe.py --csv /tmp/s5_probe.csv --label "..."   # 指定结果文件
    python3 s5probe.py --report                                # 只打印已收集的结果表
"""

import argparse
import csv
import json
import os
import statistics
import time
import urllib.request

DEF_CSV = "/tmp/s5_probe_results.csv"
FIELDS = ["label", "time", "camctrl_ok", "camctrl_total",
          "arrival_fps", "pace_fps", "reserve", "dropped",
          "underrun", "max_gap_ms", "cli_fps", "cli_max_ms", "cli_jitter_ms",
          "slow_writes", "cli_gaps_gt120", "verdict"]


def jget(url, timeout=90):
    try:
        with urllib.request.urlopen(url, timeout=timeout) as r:
            return json.load(r)
    except Exception as e:
        print("   !! 请求失败 %s: %s" % (url, e))
        return None


def measure_stream(base, secs):
    """直接读 /stream，测量【浏览器侧】真实帧间隔"""
    times = []
    buf = b""
    t0 = time.time()
    try:
        with urllib.request.urlopen(base + "/stream", timeout=12) as r:
            while time.time() - t0 < secs:
                c = r.read(16384)
                if not c:
                    break
                buf += c
                while True:
                    h = buf.find(b"Content-Length: ")
                    if h < 0:
                        break
                    e = buf.find(b"\r\n\r\n", h)
                    if e < 0:
                        break
                    n = int(buf[h + 16:e])
                    st = e + 4
                    if len(buf) < st + n:
                        break
                    times.append(time.time() - t0)
                    buf = buf[st + n:]
    except Exception as e:
        print("   !! 读流失败: %s" % e)
    if len(times) < 5:
        print("   !! 只收到 %d 帧 —— 取景流可能已断（相机需要重启？）" % len(times))
        return dict(cli_fps=0, cli_max_ms=0, cli_jitter_ms=0, cli_gaps_gt120=0)
    gaps = sorted((times[i + 1] - times[i]) * 1000 for i in range(len(times) - 1))
    return dict(
        cli_fps=round(len(times) / secs, 1),
        cli_max_ms=int(gaps[-1]),
        cli_jitter_ms=int(statistics.pstdev(gaps)),
        cli_gaps_gt120=len([g for g in gaps if g > 120]),
    )


def run_one(base, label, secs):
    print("=" * 74)
    print(" 测试: %s" % label)
    print("=" * 74)

    d0 = jget(base + "/api/diag") or {}
    s0 = d0.get("summary", {})

    # 确保流是活的
    jget(base + "/api/stream?action=start", timeout=20)
    time.sleep(4)
    print(" [1/3] 采集 %.0f 秒取景流（浏览器侧真实帧间隔）…" % secs)
    cli = measure_stream(base, secs)

    d1 = jget(base + "/api/diag") or {}
    s1 = d1.get("summary", {})

    def dv(k):
        return int(s1.get(k, 0)) - int(s0.get(k, 0))

    # ★ 关键：测控制面之前【先停流】，避免取景流抢占相机；测完自动恢复
    print(" [2/3] 暂停取景流（给 camctrl 让路）…")
    jget(base + "/api/stream?action=stop", timeout=20)
    time.sleep(3)
    print("       逐条测试 camctrl…")
    ct = jget(base + "/api/ctrltest", timeout=120) or {}
    print(" [3/3] 恢复取景流…")
    jget(base + "/api/stream?action=start", timeout=20)
    time.sleep(3)
    ok = ct.get("ok", 0)
    total = ct.get("total", 0)

    row = {
        "label": label,
        "time": time.strftime("%F %T"),
        "camctrl_ok": ok,
        "camctrl_total": total,
        "arrival_fps": s1.get("camera_arrival_fps", 0),
        "pace_fps": s1.get("pacing_fps_adaptive", 0),
        "reserve": s1.get("queue_reserve", 0),
        "dropped": dv("frames_dropped_queue_full"),
        "underrun": dv("pacing_underrun"),
        "max_gap_ms": s1.get("max_camera_gap_ms", 0),
        "slow_writes": dv("http_slow_writes"),
        **{k: cli[k] for k in ("cli_fps", "cli_max_ms", "cli_jitter_ms", "cli_gaps_gt120")},
    }
    # 判定
    smooth = (row["cli_gaps_gt120"] == 0 and row["cli_max_ms"] < 120
              and row["dropped"] == 0)
    ctrl = (total > 0 and ok == total)
    row["verdict"] = ("✅ 控制面全通 + 画面流畅" if (ctrl and smooth)
                      else ("⚠️ 控制面 %d/%d" % (ok, total)) + ("，画面流畅" if smooth else "，画面仍有卡顿"))
    return row


def save_row(path, row):
    new = not os.path.exists(path)
    with open(path, "a", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=FIELDS, extrasaction="ignore")
        if new:
            w.writeheader()
        w.writerow(row)
    print("\n 已追加到: %s" % path)


def report(path):
    if not os.path.exists(path):
        print("还没有结果文件: %s" % path)
        return
    rows = list(csv.DictReader(open(path, encoding="utf-8")))
    if not rows:
        print("结果文件为空")
        return
    print("=" * 110)
    print(" 设置组合枚举结果（共 %d 组）" % len(rows))
    print("=" * 110)
    print(" %-34s %-7s %-7s %-6s %-6s %-8s %-7s %s"
          % ("设置", "camctrl", "到达fps", "丢弃", "抖动ms", "最大间隔", ">120ms", "判定"))
    print("-" * 110)
    for r in rows:
        print(" %-34s %-7s %-7s %-6s %-6s %-8s %-7s %s" % (
            r["label"][:34], "%s/%s" % (r["camctrl_ok"], r["camctrl_total"]),
            r["arrival_fps"], r["dropped"], r["cli_jitter_ms"],
            r["cli_max_ms"], r["cli_gaps_gt120"], r["verdict"]))
    # 找出最佳的
    best = [r for r in rows if r["camctrl_ok"] == r["camctrl_total"]
            and r["cli_gaps_gt120"] == "0" and r["dropped"] == "0"]
    print("-" * 110)
    if best:
        print(" ★ 完美组合: " + " | ".join(b["label"] for b in best))
    else:
        print(" 尚未找到完美组合（camctrl 全通 且 无卡顿无跳帧）")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default="http://127.0.0.1:8080")
    ap.add_argument("--label", default="", help="本次测试的设置描述")
    ap.add_argument("--secs", type=float, default=30.0, help="取景流采样秒数")
    ap.add_argument("--csv", default=DEF_CSV)
    ap.add_argument("--report", action="store_true", help="只打印已收集的结果表")
    a = ap.parse_args()

    if a.report:
        report(a.csv)
        return

    # ★ 预检：服务必须在线，否则直接退出（不记录垃圾数据）
    pre = jget(a.base + "/api/state", timeout=8)
    if pre is None:
        print()
        print("=" * 74)
        print(" ❌ 连不上监看服务：%s" % a.base)
        print("=" * 74)
        print(" 请先在另一个终端启动服务：")
        print()
        print("   cd \"%s\"" % os.path.dirname(os.path.abspath(__file__)))
        print("   ./run.sh 192.168.1.131")
        print()
        print(" 等终端打印出「打开浏览器： http://...」之后再跑本探针。")
        print(" 如果服务启动时报 startstream err_busy ⇒ 需要【相机断电重启】。")
        print("=" * 74)
        return
    st = pre
    if not st.get("streaming") and st.get("frames", 0) == 0:
        print(" ⚠️ 服务在线，但取景流尚未出帧（fps=%s frames=%s）—— 继续测量可能全 0"
              % (st.get("fps"), st.get("frames")))

    if not a.label:
        print("请用 --label 描述本次的相机设置，例如：")
        print('  python3 s5probe.py --label "触摸设置=AF+AE, 对焦=AFS, 省电=OFF"')
        return
    row = run_one(a.base, a.label, a.secs)
    save_row(a.csv, row)
    print()
    print(" 本次结果:")
    for k in FIELDS:
        if k in row:
            print("   %-16s %s" % (k, row[k]))
    print()
    report(a.csv)


if __name__ == "__main__":
    main()
