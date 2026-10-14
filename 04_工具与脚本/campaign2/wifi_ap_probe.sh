#!/bin/bash
# wifi_ap_probe.sh — 一次性完成：连相机热点 → 只读取证 → 自动切回原网络
#
# 为什么必须这样：Mac 一旦切到相机热点，就与家庭网络断开，
# 而 AI 会话（模型 API）依赖家庭网络。所以整个"切换-取证-切回"必须
# 由一个后台脚本原子完成，人不在场也不会把机器留在相机热点上。
#
# 用法： setsid nohup bash wifi_ap_probe.sh <结果目录> >/dev/null 2>&1 &
# 结果： <结果目录>/ap_probe.log    —— 全程日志
#        <结果目录>/ap_probe.json   —— 结构化结果
#        <结果目录>/DONE            —— 完成标记

set -u
IFACE=en0
CAM_SSID="S5-XXXXXX"
OUTDIR="${1:-/tmp/s5_ap}"
GRACE="${2:-20}"          # 开跑前的缓冲秒数（让 AI 把话说完）
mkdir -p "$OUTDIR"
LOG="$OUTDIR/ap_probe.log"
exec >>"$LOG" 2>&1

echo "==================================================="
echo "### wifi_ap_probe.sh 启动 $(date '+%F %T')"
echo "### 缓冲 ${GRACE}s 后开始切换网络"
echo "==================================================="

# ---------- 记录原始网络状态 ----------
ORIG_IP=$(ipconfig getifaddr $IFACE 2>/dev/null)
ORIG_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
ORIG_PREFIX=$(echo "${ORIG_IP:-0.0.0.0}" | cut -d. -f1-3)
echo "[orig] ip=${ORIG_IP:-none} gw=${ORIG_GW:-none} prefix=${ORIG_PREFIX}"

CANDIDATES=$(networksetup -listpreferredwirelessnetworks $IFACE 2>/dev/null | tail -n +2 | sed 's/^[[:space:]]*//' | grep -v "^$")
echo "[orig] 首选网络候选:"; echo "$CANDIDATES" | sed 's/^/        /'

# ---------- 恢复函数 ----------
restore_net() {
  echo "[restore] 开始切回原网络（目标网关 $ORIG_GW）"
  for round in 1 2 3; do
    for net in $CANDIDATES; do
      [ "$net" = "$CAM_SSID" ] && continue
      networksetup -setairportnetwork $IFACE "$net" >/dev/null 2>&1
      for i in $(seq 1 8); do
        sleep 2
        ip=$(ipconfig getifaddr $IFACE 2>/dev/null)
        if [ -n "${ip:-}" ] && [ "${ip%.*}" != "${CAM_PREFIX:-x}" ]; then
          if ping -c1 -W1000 "$ORIG_GW" >/dev/null 2>&1; then
            echo "[restore] 成功: \"$net\" ip=$ip (第${round}轮)"
            return 0
          fi
        fi
      done
    done
    echo "[restore] 第${round}轮未成功，重试…"
  done
  echo "[restore] !! 自动恢复失败，请手动切回 Wi-Fi"
  return 1
}

trap 'echo "[trap] 异常退出，尝试恢复网络"; restore_net; echo "[trap] done"' EXIT

sleep "$GRACE"

# ---------- 切换到相机热点 ----------
echo ""
echo "=============== 切换网络 $(date '+%F %T') ==============="
networksetup -setairportnetwork $IFACE "$CAM_SSID"
for i in $(seq 1 20); do
  sleep 2
  CAM_IP=$(ipconfig getifaddr $IFACE 2>/dev/null)
  [ -n "${CAM_IP:-}" ] && break
done
CAM_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
CAM_PREFIX="${CAM_IP%.*}"
echo "[ap] 已连 $CAM_SSID  ip=${CAM_IP:-none}  gw=${CAM_GW:-none}"

if [ -z "${CAM_IP:-}" ]; then
  echo "[ap] !! 未取得 IP —— 相机热点可能已关闭或不在范围内"
  echo "[ap] 记录一次当前扫描以便排查"
  /tmp/wifiscan 2>&1 | head -20
  exit 1
fi

ipconfig getpacket $IFACE 2>/dev/null | head -20

# ---------- 只读取证 ----------
echo ""
echo "=============== 取证开始 $(date '+%F %T') ==============="
PY=/usr/bin/python3
"$PY" "$(dirname "$0")/s5_ap_probe.py" "$OUTDIR/ap_probe.json" "$CAM_GW" 2>&1
echo "=============== 取证结束 $(date '+%F %T') ==============="

# ---------- 切回 ----------
echo ""
restore_net
RC=$?
echo ""
echo "[final] ip=$(ipconfig getifaddr $IFACE 2>/dev/null) gw=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')"
echo "[final] 联网自检: $(curl -s -m 8 -o /dev/null -w '%{http_code}' https://api.github.com 2>/dev/null)"
echo "DONE $(date '+%F %T') rc=$RC" > "$OUTDIR/DONE"
echo "### 全部完成 $(date '+%F %T')"
