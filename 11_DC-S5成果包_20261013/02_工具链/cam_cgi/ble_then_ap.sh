#!/bin/bash
# ble_then_ap.sh — 正确顺序：先 BLE 唤醒热点，再连热点，再 accctrl
#
# 依据实测（2026-10-13 07:44）：
#   相机处于蓝牙配对模式时，它的 Wi-Fi 热点是【关闭】的；
#   BLE 握手（写身份 + 读 SSID/密码）之后约 20-25 秒，热点才出现。
#   ⇒ 必须 "先 BLE、后连热点"，否则 join 必然 -3970。
#
# 用法： ( nohup bash ble_then_ap.sh <结果目录> >/dev/null 2>&1 & )

set -u
IFACE=en0
CAM_SSID="S5-XXXXXX"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUTDIR="${1:-${HERE}/out/s5_ble_ap}"
HOME_GW="${HOME_GW:-192.168.1.1}"
mkdir -p "${OUTDIR}"
LOG="${OUTDIR}/run.log"
exec >>"${LOG}" 2>&1

echo "==================================================="
echo "### ble_then_ap.sh 启动 $(date '+%F %T')"
echo "==================================================="

ORIG_IP=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
echo "[orig] ip=${ORIG_IP:-none}"
LEFT_HOME=0

restore_net() {
  [ "${LEFT_HOME}" = "0" ] && { echo "[restore] 未离开家网，跳过"; return 0; }
  echo "[restore] 切回家网…"
  for r in 1 2 3; do
    for net in "2401-5G" "2401"; do
      networksetup -setairportnetwork ${IFACE} "${net}" >/dev/null 2>&1
      for i in $(seq 1 8); do
        sleep 2
        if ping -c1 -W1000 "${HOME_GW}" >/dev/null 2>&1; then
          echo "[restore] 成功 -> ${net} ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null)"
          return 0
        fi
      done
    done
  done
  echo "[restore] !! 失败，请手动选回 Wi-Fi"
  return 1
}
trap 'echo "[trap] 退出，执行恢复"; restore_net' EXIT

# ---------------------------------------------------------------
# 1) BLE 握手（不切网）—— 这一步会把相机的 Wi-Fi 热点"唤醒"
# ---------------------------------------------------------------
echo ""
echo "=============== [1] BLE 握手 $(date '+%F %T') ==============="
"${HERE}/ble_wr" 45 2>&1 | grep -aE "步骤|写回调|读回调|会话密钥|SSID|PASSWORD|断链|结束" || true

# ---------------------------------------------------------------
# 2) 等热点出现（最多 90s）
# ---------------------------------------------------------------
echo ""
echo "=============== [2] 等待相机热点 $(date '+%F %T') ==============="
FOUND=0
for i in $(seq 1 30); do
  if /tmp/wifiscan 2>&1 | grep -q "open=YES"; then
    echo "[ap] t+$((i*3))s 检测到开放热点"
    FOUND=1; break
  fi
  sleep 3
done
[ "${FOUND}" = "0" ] && { echo "[ap] !! 90s 内未出现热点，放弃"; exit 1; }

# ---------------------------------------------------------------
# 3) 连热点（带重试）
# ---------------------------------------------------------------
echo ""
echo "=============== [3] 连接热点 $(date '+%F %T') ==============="
CAM_IP=""
for t in $(seq 1 12); do
  networksetup -setairportnetwork ${IFACE} "${CAM_SSID}" 2>&1 | sed "s/^/[ap t${t}] /"
  for i in $(seq 1 4); do
    sleep 2
    CAM_IP=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
    case "${CAM_IP}" in 192.168.54.*) break 2 ;; esac
  done
done
CAM_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
case "${CAM_GW}" in ""|none) CAM_GW="192.168.54.1" ;; esac
echo "[ap] ip=${CAM_IP:-none} gw=${CAM_GW}"
if [ -z "${CAM_IP}" ]; then echo "[ap] !! 连不上热点"; exit 1; fi
LEFT_HOME=1

# 看门狗：防止 macOS 回落到家网
touch "${OUTDIR}/.watch"
( while [ -f "${OUTDIR}/.watch" ]; do
    ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
    case "${ip}" in 192.168.54.*) ;; *) networksetup -setairportnetwork ${IFACE} "${CAM_SSID}" >/dev/null 2>&1 ;; esac
    sleep 3
  done ) &
WATCHPID=$!

# ---------------------------------------------------------------
# 4) accctrl 配对
# ---------------------------------------------------------------
echo ""
echo "=============== [4] accctrl 配对 $(date '+%F %T') ==============="
/usr/bin/python3 "${HERE}/s5_ap_pair.py" "${OUTDIR}/pair.json" "${CAM_GW}" 2>&1 | grep -avE "<title|<language|<menuset|titlelist"

rm -f "${OUTDIR}/.watch"; kill ${WATCHPID} 2>/dev/null
echo ""
restore_net
echo "[final] ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null) 联网=$(curl -s -m 8 -o /dev/null -w '%{http_code}' https://api.github.com)"
echo "DONE $(date '+%F %T')" > "${OUTDIR}/DONE"
echo "### 完成 $(date '+%F %T')"
