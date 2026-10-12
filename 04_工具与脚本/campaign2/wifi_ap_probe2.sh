#!/bin/bash
# wifi_ap_probe2.sh — 第二轮：连相机热点 → 访问控制握手 + 新端口深挖 → 自动切回
#
# 与第一版的区别：
#   1) 修掉变量 bug —— 原版 "$ORIG_GW）" 这类"变量紧跟全角字符"会被 bash 当成变量名的一部分
#      （报 ORIG_GW<乱码>: unbound variable），导致自动切回从未执行。现在全部用 ${VAR}。
#   2) 恢复逻辑更硬：多轮、逐网关验证、失败后继续重试。
#   3) 调用 s5_ap_probe2.py 做第二轮取证。
#
# 用法： ( nohup bash wifi_ap_probe2.sh <结果目录> <缓冲秒> >/dev/null 2>&1 & )

set -u
IFACE=en0
CAM_SSID="S5-70E253"
OUTDIR="${1:-/tmp/s5_ap2}"
GRACE="${2:-45}"
mkdir -p "${OUTDIR}"
LOG="${OUTDIR}/ap_probe2.log"
exec >>"${LOG}" 2>&1

echo "==================================================="
echo "### wifi_ap_probe2.sh 启动 $(date '+%F %T')  缓冲 ${GRACE}s"
echo "==================================================="

LEFT_HOME=0          # 是否真的切到了相机热点（没切成就不要瞎恢复）
ORIG_IP=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
ORIG_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
echo "[orig] ip=${ORIG_IP:-none} gw=${ORIG_GW:-none}"

CANDIDATES=$(networksetup -listpreferredwirelessnetworks ${IFACE} 2>/dev/null | tail -n +2 | sed 's/^[[:space:]]*//' | grep -v "^$")
echo "[orig] 候选网络数: $(echo "${CANDIDATES}" | wc -l | tr -d ' ')"

restore_net() {
  if [ "${LEFT_HOME}" = "0" ]; then
    echo "[restore] 从未离开原网络（切换失败），跳过恢复"
    return 0
  fi
  echo "[restore] === 开始切回原网络，目标网关 ${ORIG_GW} ==="
  local round net i ip
  for round in 1 2 3 4 5; do
    while IFS= read -r net; do
      [ -z "${net}" ] && continue
      [ "${net}" = "${CAM_SSID}" ] && continue
      networksetup -setairportnetwork ${IFACE} "${net}" >/dev/null 2>&1
      for i in $(seq 1 6); do
        sleep 2
        ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
        if [ -n "${ip}" ] && [ "${ip}" != "${CAM_IP:-}" ]; then
          if ping -c1 -W1000 "${ORIG_GW}" >/dev/null 2>&1; then
            echo "[restore] 成功 -> \"${net}\" ip=${ip} (第${round}轮)"
            return 0
          fi
        fi
      done
    done <<< "$(printf '2401-5G\n2401\n%s\n' "${CANDIDATES}")"
    echo "[restore] 第${round}轮未成功，继续…"
  done
  echo "[restore] !! 自动恢复失败，请手动选回 Wi-Fi"
  return 1
}

trap 'echo "[trap] 异常退出，执行恢复"; restore_net; echo "[trap] 恢复流程结束"' EXIT

sleep "${GRACE}"

echo ""
echo "=============== 切换网络 $(date '+%F %T') ==============="
CAM_IP=""
ATTEMPT=0
for ATTEMPT in $(seq 1 15); do
  networksetup -setairportnetwork ${IFACE} "${CAM_SSID}" 2>&1 | sed "s/^/[ap t${ATTEMPT}] /"
  for i in $(seq 1 5); do
    sleep 2
    CAM_IP=$(ipconfig getifaddr ${IFACE} 2>/dev/null || true)
    if [ -n "${CAM_IP}" ] && [ "${CAM_IP}" != "${ORIG_IP}" ]; then break 2; fi
  done
  echo "[ap] 第 ${ATTEMPT} 次未连上，2s 后重试（热点可能刚上线/在跳信道）…"
  sleep 2
done
CAM_GW=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')
echo "[ap] SSID=${CAM_SSID} ip=${CAM_IP:-none} gw=${CAM_GW:-none}"
if [ -n "${CAM_IP}" ] && [ "${CAM_IP}" != "${ORIG_IP}" ]; then LEFT_HOME=1; fi
echo "[ap] LEFT_HOME=${LEFT_HOME}"

if [ -z "${CAM_IP}" ]; then
  echo "[ap] !! 未取得 IP（相机热点可能已关闭）"
  /tmp/wifiscan 2>&1 | head -15
  exit 1
fi

echo ""
echo "=============== 第二轮取证 $(date '+%F %T') ==============="
/usr/bin/python3 "$(dirname "$0")/s5_ap_probe2.py" "${OUTDIR}/ap_probe2.json" "${CAM_GW}"
echo "=============== 取证结束 $(date '+%F %T') ==============="

echo ""
restore_net
RC=$?
echo ""
echo "[final] ip=$(ipconfig getifaddr ${IFACE} 2>/dev/null) gw=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')"
echo "[final] 联网自检 HTTP=$(curl -s -m 10 -o /dev/null -w '%{http_code}' https://api.github.com 2>/dev/null)"
echo "DONE $(date '+%F %T') rc=${RC}" > "${OUTDIR}/DONE"
echo "### 全部完成 $(date '+%F %T')"
