#!/bin/bash
# hold_then_ap.sh — 【BLE 全程保持】+ 同时连它开的热点 + accctrl
#
# 依据用户实测：相机在"配对模式"下无法手动开 Wi-Fi；
#   必须先与相机完成 BLE 握手，相机会【自动开启 Wi-Fi】，且该热点只在 BLE 会话期间在线。
#   ⇒ BLE 必须【全程不断】，否则热点立即消失（这就是之前 "Could not find network" 的真因）。
#
# 流程：
#   1) 后台启动 ble_hold（握手后保持连接，写 /tmp/ble_hold_ready）
#   2) 等就绪标记
#   3) 立刻连 S5-XXXXXX（BLE 仍在保持）
#   4) accctrl 配对（s5_ap_pair.py）
#   5) 结束 ble_hold、切回家网
#
# 用法: ( nohup bash hold_then_ap.sh <结果目录> >/dev/null 2>&1 & )

set -u
IFACE=en0
CAM_SSID="S5-XXXXXX"
HERE="$(cd "$(dirname "$0")" && pwd)"
OUTDIR="${1:-${HERE}/out/s5_hold}"
HOME_GW="${HOME_GW:-192.168.1.1}"
READY="/tmp/ble_hold_ready"
mkdir -p "${OUTDIR}"
LOG="${OUTDIR}/run.log"
exec >>"${LOG}" 2>&1

echo "==================================================="
echo "### hold_then_ap.sh 启动 $(date '+%F %T')"
echo "==================================================="
ORIG_IP=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
echo "[orig] ip=${ORIG_IP:-none}"
LEFT_HOME=0
BLEPID=""

restore_net() {
  [ "${LEFT_HOME}" = "0" ] && { echo "[restore] 未离开家网，跳过"; return 0; }
  echo "[restore] 切回家网…"
  for r in 1 2 3; do
    for net in "2401-5G" "2401"; do
      networksetup -setairportnetwork ${IFACE} "${net}" >/dev/null 2>&1
      for i in $(seq 1 8); do
        sleep 2
        ping -c1 -W1000 "${HOME_GW}" >/dev/null 2>&1 && { echo "[restore] 成功 -> ${net} ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null)"; return 0; }
      done
    done
  done
  echo "[restore] !! 失败，请手动选回"
  return 1
}
cleanup() {
  [ -n "${BLEPID}" ] && kill ${BLEPID} 2>/dev/null
  pkill -9 -f ble_hold 2>/dev/null
  rm -f "${OUTDIR}/.watch"
}
trap 'echo "[trap] 退出"; cleanup; restore_net' EXIT

# ---- 1) BLE 握手 + 全程保持 ----
rm -f "${READY}" "${READY}.lost"
echo ""
echo "=============== [1] BLE 握手并保持 $(date '+%F %T') ==============="
( "${HERE}/ble_hold" 300 "${READY}" >"${OUTDIR}/ble_hold.log" 2>&1 ) &
BLEPID=$!
echo "[ble] ble_hold pid=${BLEPID}，等待就绪标记 ${READY}…"

for i in $(seq 1 90); do
  [ -f "${READY}" ] && { echo "[ble] t+${i}s 握手完成（热点应已开启）"; break; }
  [ -f "${READY}.lost" ] && { echo "[ble] !! BLE 已断链，放弃"; exit 1; }
  sleep 1
done
[ -f "${READY}" ] || { echo "[ble] !! 90s 内未完成握手"; exit 1; }
sleep 2

# ---- 2) 立刻连热点（BLE 仍在保持） ----
echo ""
echo "=============== [2] 连接热点（BLE 保持中） $(date '+%F %T') ==============="
CAM_IP=""
for t in $(seq 1 15); do
  networksetup -setairportnetwork ${IFACE} "${CAM_SSID}" 2>&1 | sed "s/^/[ap t${t}] /"
  for i in $(seq 1 4); do
    sleep 1
    CAM_IP=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
    case "${CAM_IP}" in 192.168.54.*) break 2 ;; esac
  done
done
CAM_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
case "${CAM_GW}" in ""|none) CAM_GW="192.168.54.1" ;; esac
echo "[ap] ip=${CAM_IP:-none} gw=${CAM_GW}"
[ -z "${CAM_IP}" ] && { echo "[ap] !! 连不上热点（BLE 保持中仍失败）"; exit 1; }
LEFT_HOME=1

touch "${OUTDIR}/.watch"
( while [ -f "${OUTDIR}/.watch" ]; do
    ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
    case "${ip}" in 192.168.54.*) ;; *) networksetup -setairportnetwork ${IFACE} "${CAM_SSID}" >/dev/null 2>&1 ;; esac
    sleep 2
  done ) &
WATCHPID=$!

# ---- 3) accctrl 配对 ----
echo ""
echo "=============== [3] accctrl 配对 $(date '+%F %T') ==============="
echo "[ble] 保活中? $(kill -0 ${BLEPID} 2>/dev/null && echo yes || echo no)"
/usr/bin/python3 "${HERE}/s5_ap_pair.py" "${OUTDIR}/pair.json" "${CAM_GW}" 2>&1 | grep -avE "<title|<language|<menuset|titlelist"

kill ${WATCHPID} 2>/dev/null; rm -f "${OUTDIR}/.watch"
echo ""
restore_net
echo "[final] ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null) 联网=$(curl -s -m 8 -o /dev/null -w '%{http_code}' https://api.github.com)"
echo "DONE $(date '+%F %T')" > "${OUTDIR}/DONE"
echo "### 完成 $(date '+%F %T')"
