#!/usr/bin/env python3
"""
s5_quality.py — 健壮的「录制格式 / 录制质量」设置器（解决 err_reject / ok 假成功 / a6k 改容器）

背景（2026-10-14 实测，DC-S5 / VD4.30）
--------------------------------------
`cam.cgi?mode=setsetting&type=videoquality&value=<名字>` 的返回码**不能直接采信**：

  1. `err_reject`  = 「参数格式对，但相机当前状态不接受」——**不是失败**。
                     授权状态在 ok / 受限 之间翻动，退避重试即可撞进 ok 窗口。
                     实测 `mov_50p_200mbps_4k_10bit` 第 5 次才成功。
  2. `err_busy`    = 相机忙，退避重试。
  3. `err_critical`= 严重状态；有时重试也能成功（实测 `camcmd&value=recmode` 即如此）。
  4. **`ok` 不等于生效** —— 今天至少 6 次「返回 ok 但画质没变」或「ok 却改成了别的档」。
     唯一可信的判据是 **回读 `getsetting&type=videoquality`** 与目标逐字相符。
  5. ⛔ **`a6k` 家族有静默副作用**：返回 `ok`，却把 `videoformat` 从 `mov` 悄悄改成 `avchd`。
     本工具默认拒绝该家族，并在任何设置后校验容器，发现被改就自动恢复。

菜单变灰的精确条件
------------------
`videoquality` **不在 `allmenu` 里** ⇒ 机身【录制质量】整项变灰不可用。
菜单读的是 **RAM 值**（不是 flash 值），所以「flash 存安全值 + RAM 上隐藏档」的双轨方案不成立。
本工具用 `--allow-grey` 才允许写 allmenu 之外的档。而 curmenu 独有 ≠ 可用：
`curmenu` 声明 126 条 mov 档，`allmenu` 只有 106 条，机身实际可选仅 17 条。

不可达的档（固件按机型故意过滤，任何主机侧手段都拿不到）
--------------------------------------------------------
`5_9k` / `6k` / `100p` / `120p` / `400mbps` 均为「其他机型占位，本机恒隐藏」。
已在 PAL + NTSC、视频模式 + 6K PHOTO 模式、每档最多 12 次退避重试下穷尽验证，全部失败。
（依据：`04_工具与脚本/campaign2/隐藏格式持久化_成果.md` 第 131 行。）

用法
----
    python3 s5_quality.py status                 # 只读：当前 live / blob 状态
    python3 s5_quality.py list [--grep 200mbps]  # 列出 allmenu 内（菜单安全）的档
    python3 s5_quality.py list --all             # 列出全部已声明档并标注安全/会灰/不可达
    python3 s5_quality.py set mov_60p_200mbps_4k_10bit
    python3 s5_quality.py set mov_60p_200mbps_c4k_10bit --allow-grey
    python3 s5_quality.py safe                   # 恢复到 allmenu 安全的 200Mbps 4K 10bit

安全说明
--------
本工具**只做 RAM 设置**（`setsetting`），**不写 flash**。断电即复原。
需要跨断电持久化请用 `persist.py`（那条路径会写 flash，属高风险操作，须接 AC 电源）。
"""

import argparse
import os
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

IP = "192.168.1.131"  # ← 相机内网地址，请按你的网络环境修改
UA = "LUMIX Sync"

# 与 persist.py 保持一致：blob 内质量码偏移与已确认的码表
VQ_OFF = 6986
VQ_CODE2NAME = {
    0x8b: "mov_60p_200mbps_c4k_10bit",
    0x92: "mov_60p_150mbps_c4k",
    0x94: "mov_30p_150mbps_c4k_10bit",
    0x96: "mov_24p_150mbps_c4k_10bit",
    0x97: "mov_24p_100mbps_c4k",
    0x9b: "mov_60p_200mbps_4k_10bit",
    0xc0: "(unset/disabled)",
    0xc1: "mp4_30p_20mbps",
}

# 固件按机型故意过滤的档族：本机恒隐藏，试了也是错，直接拦掉省时间
UNREACHABLE_PAT = re.compile(r"(5_9k|_6k_|_a6k|_400mbps|_100p_|_120p_)")

# 静默副作用家族：返回 ok 却会把 videoformat 改成 avchd
DANGEROUS_PAT = re.compile(r"_a6k")

ALLMENU = os.path.join(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))),
    "06_数据与证据", "camera_settings", "allmenu.xml",
)
CURMENU = ALLMENU.replace("allmenu.xml", "curmenu.xml")


# ---------------------------------------------------------------- HTTP 层
def cgi(path, timeout=12.0):
    """GET /cam.cgi?<path> -> (status|None, text). UA 必须伪装成官方 App。"""
    url = "http://%s/cam.cgi?%s" % (IP, path)
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        with urllib.request.urlopen(req, timeout=timeout) as r:
            return r.status, r.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode("utf-8", "replace")
    except Exception as e:                      # 连接失败 / 超时
        return None, str(e)


def result_of(text):
    m = re.search(r"<result>([^<]*)</result>", text or "")
    return m.group(1) if m else None


def value_of(text, key):
    m = re.search(r'<settingvalue\s+%s="([^"]*)"' % re.escape(key), text or "")
    if m:
        return m.group(1)
    m = re.search(r"<%s>([^<]*)</%s>" % (re.escape(key), re.escape(key)), text or "")
    return m.group(1) if m else None


def get_state():
    st, txt = cgi("mode=getstate")
    if st != 200:
        return {}
    return {k: v for k, v in re.findall(r"<([a-z0-9_]+)>([^<]*)</\1>", txt)}


def get_setting(name):
    st, txt = cgi("mode=getsetting&type=%s" % name)
    return value_of(txt, name) if st == 200 else None


def health():
    """相机整体健康：getstate 返回 ok 即认为可用。"""
    st, txt = cgi("mode=getstate")
    return st == 200 and result_of(txt) == "ok"


# ---------------------------------------------------------------- 菜单数据
#
# ⚠️ 口径说明（10-14 复核更正，别再犯）：
#   `allmenu` 与 `curmenu` 是【性质不同的两份东西】，绝不能拿名字做朴素差集：
#     · allmenu  = 相机【菜单树】。可执行项形如
#                  <item cmd_type="videoquality" cmd_value="mov_...">
#                  它是「相机能渲染哪些条目」的定义。共 44 个质量项（mov 31 + mp4 13）。
#     · curmenu  = 【App 侧可见性快照】。形如
#                  <item id="menu_item_id_v_quality_mov_..." enable="yes|no"/>
#                  【没有 cmd_value】。它是「当前状态下真正可选哪些档」的第一手判据，
#                  且与状态强相关（容器 + 制式）：
#                     MP4 态抓 → mov 项 enable=yes 为 0，mp4 有 5
#                     mov 态抓 → mov 项 enable=yes 为 18，mp4 为 0
#   curmenu 里的 mov_* 字符串大多出自 title_id / img / id 等【标签标识符】，
#   不是可执行档。早期版本正是拿它们做差集，算出「curmenu 独有 95 条」这种伪结论。
#
# 菜单变灰的真正条件：
#   当前 videoquality【在当前 curmenu 里 enable=yes】但【不在 allmenu 声明中】
#   ⇒ 菜单找不到条目可渲染 ⇒ 整项变灰。目前恰好只有 `mov_60p_200mbps_c4k_10bit`(0x8b) 一个。

def _read(path):
    try:
        with open(path, encoding="utf-8", errors="replace") as f:
            return f.read()
    except OSError:
        return ""


def allmenu_quality_names():
    """allmenu（菜单树）里声明为可执行 videoquality 的档名集合。"""
    txt = _read(ALLMENU)
    return set(re.findall(r'cmd_type="videoquality"\s+cmd_value="([a-zA-Z0-9_]+)"', txt)) \
         | set(re.findall(r'cmd_value="([a-zA-Z0-9_]+)"\s+cmd_type="videoquality"', txt))


def live_menu_flags():
    """实时抓 curmenu，返回 {档名: bool(enable)}。这是"当前真正可选"的权威判据。"""
    st, txt = cgi("mode=getinfo&type=curmenu", timeout=25)
    if st != 200 or not txt:
        return {}
    out = {}
    for m in re.finditer(r'<item\s+id="menu_item_id_v_quality_([a-zA-Z0-9_]+)"([^/]*)/>', txt):
        name, attrs = m.group(1), m.group(2)
        out[name] = 'enable="yes"' in attrs
    return out


def classify(name):
    """-> ('safe'|'grey'|'off'|'unknown', reason)

    safe = allmenu 已声明（菜单能渲染，不会变灰）
    grey = allmenu 未声明，但当前 curmenu 里 enable=yes ⇒ 会变灰
    off  = 当前状态下相机根本没启用它 ⇒ 设了也白设
    """
    allm = allmenu_quality_names()
    live = live_menu_flags()
    if not allm:
        return "unknown", "读不到 allmenu.xml（%s），无法判定菜单安全性" % ALLMENU
    if name in allm:
        return "safe", "在 allmenu 内 ⇒ 菜单可正常渲染"
    if live and live.get(name):
        return "grey", "allmenu 未声明、但当前 curmenu enable=yes ⇒ 会变灰（已知仅 0x8b 属此类）"
    if live and name in live and not live[name]:
        return "off", "当前状态下 curmenu enable=no ⇒ 相机未启用该档（如制式/容器不匹配）"
    if live:
        return "unknown", "当前 curmenu 里没有该项；allmenu 也未声明 ⇒ 名字可能有误"
    return "unknown", "抓不到 live curmenu；仅知它不在 allmenu 内（大概率会让菜单变灰）"


# ---------------------------------------------------------------- 核心：带重试与校验的设置
def set_quality(name, retries=12, delay=2.0, allow_grey=False,
                allow_unreachable=False, auto_restore=True, quiet=False):
    """设置 videoquality 并【回读校验】。返回 (成功?, 说明)。"""

    def say(msg):
        if not quiet:
            print(msg, flush=True)

    # --- 前置拦截 -------------------------------------------------
    if DANGEROUS_PAT.search(name) and not allow_unreachable:
        return False, ("拒绝执行：`%s` 属于 a6k 家族 —— 实测返回 ok 却会把 videoformat "
                       "静默改成 avchd。如确要尝试，加 --allow-unreachable。" % name)

    if UNREACHABLE_PAT.search(name) and not allow_unreachable:
        return False, ("拒绝执行：`%s` 属于固件按机型过滤的档族（5.9K/6K/a6k/400Mbps/100p/120p），"
                       "本机恒隐藏，已在 PAL+NTSC、视频模式+6K PHOTO 下穷尽验证不可达。"
                       "如仍要试，加 --allow-unreachable。" % name)

    kind, reason = classify(name)
    if kind == "grey" and not allow_grey:
        return False, ("拒绝执行：`%s` %s。这会让机身【录制质量】整项变灰不可用。"
                       "如接受该代价，加 --allow-grey。" % (name, reason))
    if kind == "unknown":
        say("提示：%s" % reason)

    if not health():
        return False, "相机 health 不是 ok，先检查连接再试。"

    vf_before = get_setting("videoformat")
    original = get_setting("videoquality")

    # --- 带退避重试的设置 -----------------------------------------
    q = urllib.parse.quote(name, safe="")
    last = None
    for attempt in range(1, retries + 1):
        st, txt = cgi("mode=setsetting&type=videoquality&value=%s" % q)
        last = result_of(txt) if st == 200 else "HTTP(%s)" % st
        time.sleep(0.8)
        now = get_setting("videoquality")

        # ★ 唯一可信判据：回读与目标逐字相符
        if now == name:
            say("  第 %-2d 次: %-12s 回读=%-32s ✅ 生效" % (attempt, last, now))
            break

        say("  第 %-2d 次: %-12s 回读=%-32s %s" % (
            attempt, last, now,
            "（ok 但未生效，继续重试）" if last == "ok" else "（重试）"))
        time.sleep(delay)
    else:
        # 全部尝试后仍未生效 —— 检查容器是否被带偏
        vf_now = get_setting("videoformat")
        if auto_restore and vf_now != vf_before:
            say("  ⚠️ 容器被改成 %s（原 %s），自动恢复…" % (vf_now, vf_before))
            _restore_container(original, quiet=quiet)
        return False, ("%d 次尝试后仍未生效（最后返回 %s）。原始画质 %s 未改变。"
                       % (retries, last, original))

    # --- 成功后的容器校验 + 副作用恢复 ----------------------------
    vf_after = get_setting("videoformat")
    if vf_after != vf_before:
        say("  ⚠️ 容器被副带改成 %s（原 %s）" % (vf_after, vf_before))
        if auto_restore:
            say("  → 已回滚到原画质 %s 以恢复容器" % original)
            _restore_container(original, quiet=quiet)
            return False, ("设置 %s 生效，但它把 videoformat 从 %s 改成了 %s；"
                           "已回滚。该档不可用。" % (name, vf_before, vf_after))
        return True, ("⚠️ 已生效，但 videoformat 被改成 %s（--no-restore 未回滚）" % vf_after)

    # --- 稳定性确认：等一会儿再回读一次 ---------------------------
    time.sleep(5)
    settled = get_setting("videoquality")
    if settled != name:
        return False, ("设置 %s 曾生效，但 5 秒后回退为 %s ⇒ 该档不稳定。" % (name, settled))

    extra = ""
    if kind == "grey":
        extra = " ⚠️ 该档不在 allmenu ⇒ 机身菜单此时是灰的"
    return True, "✅ %s 已生效并稳定（容器 %s）%s" % (name, vf_after, extra)


def _restore_container(quality, quiet=False):
    for _ in range(8):
        cgi("mode=setsetting&type=videoquality&value=%s" % urllib.parse.quote(quality, safe=""))
        time.sleep(1.5)
        if get_setting("videoformat") == "mov" or get_setting("videoquality") == quality:
            break


# ---------------------------------------------------------------- 子命令
def cmd_status(_):
    st = get_state()
    print("health      : %s" % ("ok" if st.get("result") == "ok" or st else "?"))
    print("cammode     : %s   rec=%s   temperature=%s" % (
        st.get("cammode"), st.get("rec"), st.get("temperature")))
    for k in ("ntsc_pal", "videoformat", "videoquality"):
        print("%-12s: %s" % (k, get_setting(k)))

    name = get_setting("videoquality")
    if name:
        kind, reason = classify(name)
        print("菜单安全性  : %s —— %s" % (kind, reason))
    print()
    print("提示：getsetting 读的是【RAM 副本】。只有断电重启后的值才代表 flash 内容。")


def cmd_list(a):
    allm = allmenu_quality_names()
    live = live_menu_flags()
    if not allm and not live:
        print("读不到 allmenu.xml 也抓不到 curmenu，无法列出。")
        return

    names = sorted(set(allm) | set(live))
    for n in names:
        if n.endswith("_q"):
            continue
        if a.grep and a.grep not in n:
            continue
        if n in allm:
            tag = "safe"
        elif live.get(n):
            tag = "GREY"
        elif n in live:
            tag = "off "
        else:
            continue
        if not a.all and tag != "safe":
            continue
        warn = " ⛔不可达" if UNREACHABLE_PAT.search(n) else ""
        cur = " ←当前" if n == get_setting("videoquality") else ""
        print("  %-4s %s%s%s" % (tag, n, warn, cur))

    en = sum(1 for v in live.values() if v)
    print("\n  allmenu 声明的可执行 videoquality 项 : %d" % len(allm))
    print("  当前 curmenu 里 enable=yes 的项      : %d" % en)
    print("  safe = allmenu 已声明（菜单不会灰） | GREY = 未声明但启用（会灰） | off = 当前未启用")
    print("  ⛔ = 固件按机型过滤，本机恒隐藏")


def cmd_set(a):
    ok, msg = set_quality(a.name, retries=a.retries, allow_grey=a.allow_grey,
                          allow_unreachable=a.allow_unreachable)
    print(("✅ " if ok else "❌ ") + msg)
    sys.exit(0 if ok else 1)


def cmd_safe(_):
    """恢复到 allmenu 安全的 200Mbps 4K 10bit（按当前制式选 50p/60p）。"""
    pal = get_setting("ntsc_pal")
    name = "mov_50p_200mbps_4k_10bit" if pal == "pal" else "mov_60p_200mbps_4k_10bit"
    print("制式=%s ⇒ 目标 %s" % (pal, name))
    ok, msg = set_quality(name)
    print(("✅ " if ok else "❌ ") + msg)
    sys.exit(0 if ok else 1)


def main():
    global IP
    p = argparse.ArgumentParser(description="S5 录制质量健壮设置器（只写 RAM）")
    p.add_argument("--ip", default=IP)
    sub = p.add_subparsers(dest="cmd", required=True)

    sub.add_parser("status", help="只读：当前状态").set_defaults(fn=cmd_status)

    pl = sub.add_parser("list", help="列出档位")
    pl.add_argument("--all", action="store_true", help="连会变灰 / 未启用的也列")
    pl.add_argument("--grep", default=None, help="按子串过滤")
    pl.set_defaults(fn=cmd_list)

    ps = sub.add_parser("set", help="设置某个录制质量")
    ps.add_argument("name")
    ps.add_argument("--retries", type=int, default=12, help="退避重试次数（默认 12）")
    ps.add_argument("--allow-grey", action="store_true", help="允许写会让菜单变灰的档")
    ps.add_argument("--allow-unreachable", action="store_true",
                    help="允许尝试已知不可达 / 有副作用的档族")
    ps.set_defaults(fn=cmd_set)

    sub.add_parser("safe", help="恢复到 allmenu 安全的 200Mbps 4K 10bit").set_defaults(fn=cmd_safe)

    a = p.parse_args()
    IP = a.ip
    a.fn(a)


if __name__ == "__main__":
    main()
