#!/bin/bash
# s5ctl.sh — 统一控制所有 S5 后台取证脚本（解决"脚本失控干扰输出"的问题）
#
#   ./s5ctl.sh start ap_pair    [grace]   # 启动配对复现（连相机热点）
#   ./s5ctl.sh start ap_probe2  [grace]   # 启动第二轮端口/服务取证
#   ./s5ctl.sh stop                       # 立刻停掉所有后台脚本 + 切回家网
#   ./s5ctl.sh status                     # 看谁在跑、日志在哪
#   ./s5ctl.sh tail ap_pair               # 看某次任务的日志尾部
#   ./s5ctl.sh ble                        # 跑一次 BLE 扫描（不切网，安全）
#
# 实现要点：
#   * 每个任务写一个 PID 文件到 out/.run/<name>.pid，stop 按 PID 精确杀
#   * 所有联网切换脚本都被要求监听 out/.run/STOP —— 见 stop 文件机制
#   * stop 会验证网络是否回到家庭网关，没回来就主动连 2401-5G

set -u
HERE="$(cd "$(dirname "$0")" && pwd)"
RUNDIR="${HERE}/out/.run"
HOME_SSID="${HOME_SSID:-2401-5G}"
HOME_GW="${HOME_GW:-192.168.1.1}"
mkdir -p "${RUNDIR}"

usage() { sed -n '2,20p' "$0"; exit 2; }

ensure_home() {
  echo "[ctl] 检查是否在家庭网络（网关 ${HOME_GW}）…"
  if ping -c1 -W1000 "${HOME_GW}" >/dev/null 2>&1; then
    echo "[ctl] 已在家庭网络 ip=$(ipconfig getifaddr en0 2>/dev/null)"
    return 0
  fi
  echo "[ctl] 不在家庭网络，尝试连回 ${HOME_SSID}"
  networksetup -setairportnetwork en0 "${HOME_SSID}" >/dev/null 2>&1
  for i in $(seq 1 12); do
    sleep 2
    if ping -c1 -W1000 "${HOME_GW}" >/dev/null 2>&1; then
      echo "[ctl] 已恢复 ip=$(ipconfig getifaddr en0 2>/dev/null)"
      return 0
    fi
  done
  echo "[ctl] !! 未能自动恢复，请手动选回 Wi-Fi"
  return 1
}

do_stop() {
  touch "${RUNDIR}/STOP"
  local any=0
  for f in "${RUNDIR}"/*.pid; do
    [ -e "${f}" ] || continue
    p=$(cat "${f}" 2>/dev/null)
    name=$(basename "${f}" .pid)
    if [ -n "${p}" ] && kill -0 "${p}" 2>/dev/null; then
      echo "[ctl] 停止 ${name} (pid ${p})"
      kill "${p}" 2>/dev/null
      sleep 1
      kill -9 "${p}" 2>/dev/null
      any=1
    fi
    rm -f "${f}"
  done
  # 兜底：按名字杀
  pkill -9 -f "wifi_ap_probe" 2>/dev/null
  pkill -9 -f "wifi_ap_pair" 2>/dev/null
  pkill -9 -f "s5_ap_" 2>/dev/null
  [ "${any}" = "0" ] && echo "[ctl] 没有登记在跑的任务（已做兜底清理）"
  rm -f "${RUNDIR}/STOP"
  ensure_home
}

do_status() {
  echo "[ctl] 任务状态："
  local found=0
  for f in "${RUNDIR}"/*.pid; do
    [ -e "${f}" ] || continue
    found=1
    p=$(cat "${f}" 2>/dev/null); name=$(basename "${f}" .pid)
    if kill -0 "${p}" 2>/dev/null; then echo "   RUNNING  ${name}  pid=${p}"; else echo "   STALE    ${name}  pid=${p}"; fi
  done
  [ "${found}" = "0" ] && echo "   （无登记任务）"
  echo "[ctl] 其它可能相关进程："
  pgrep -fl "wifi_ap_|s5_ap_" | sed 's/^/   /' || echo "   （无）"
  echo "[ctl] 当前网络：ip=$(ipconfig getifaddr en0 2>/dev/null) gw=$(netstat -rn -f inet 2>/dev/null | awk '/^default/{print $2; exit}')"
}

do_start() {
  local name="$1" grace="${2:-30}" script outdir
  case "${name}" in
    ap_pair)   script="wifi_ap_pair.sh";   outdir="${HERE}/out/s5_ap_pair" ;;
    ap_probe2) script="wifi_ap_probe2.sh"; outdir="${HERE}/out/s5_ap2" ;;
    *) echo "[ctl] 未知任务: ${name}（可用: ap_pair / ap_probe2）"; exit 2 ;;
  esac
  # 先清干净
  pkill -9 -f "${script}" 2>/dev/null
  rm -rf "${outdir}"; mkdir -p "${outdir}"
  ( nohup bash "${HERE}/${script}" "${outdir}" "${grace}" >/dev/null 2>&1 & echo $! > "${RUNDIR}/${name}.pid" )
  sleep 2
  local p; p=$(cat "${RUNDIR}/${name}.pid" 2>/dev/null)
  echo "[ctl] 已启动 ${name}  pid=${p}  outdir=${outdir}"
  echo "[ctl] 日志: ${outdir}/$(echo "${script}" | sed 's/wifi_ap_probe2.sh/ap_probe2.log/; s/wifi_ap_pair.sh/ap_pair.log/; s/wifi_ap_probe.sh/ap_probe.log/')"
  echo "[ctl] 随时可用: $(basename "$0") stop"
}

case "${1:-}" in
  start)  shift; do_start "${1:?任务名}" "${2:-30}" ;;
  stop)   do_stop ;;
  status) do_status ;;
  tail)   n="${2:?任务名}"; shift 2 2>/dev/null
          case "${n}" in
            ap_pair)   f="${HERE}/out/s5_ap_pair/ap_pair.log" ;;
            ap_probe2) f="${HERE}/out/s5_ap2/ap_probe2.log" ;;
            ap)        f="${HERE}/out/s5_ap/ap_probe.log" ;;
            *) f="${n}" ;;
          esac
          echo "== ${f} =="; tail -n "${1:-40}" "${f}" 2>/dev/null || echo "(无日志)" ;;
  ble)    cd "${HERE}" && ./ble_scan "${2:-15}" ;;
  *)      usage ;;
esac
