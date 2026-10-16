#!/bin/bash
# S5 Monitor 便捷启动
#   用法:  ./run.sh [相机IP] [本机端口]
#   例:    ./run.sh
#          ./run.sh 192.168.1.131
#          ./run.sh 192.168.1.131 8080
# 注意: 本脚本会忽略任何以 # 开头的参数（防止把注释复制进来）
set -u

# 过滤掉注释与空白参数
ARGS=()
for a in "$@"; do
  case "$a" in
    \#*) break ;;          # 遇到 # 就停止（后面都是注释）
    "") ;;
    *) ARGS+=("$a") ;;
  esac
done

HOST="${ARGS[0]:-192.168.54.1}"
PORT="${ARGS[1]:-8080}"

# 参数校验：端口必须是数字
case "$PORT" in
  ''|*[!0-9]*) echo "!! 端口 '$PORT' 不是数字，改用默认 8080"; PORT=8080 ;;
esac
# 相机 IP 粗校验
case "$HOST" in
  *[!0-9.]*) echo "!! 相机 IP '$HOST' 看起来不像 IP，改用默认 192.168.54.1"; HOST=192.168.54.1 ;;
esac

IP=$(ipconfig getifaddr en0 2>/dev/null || ipconfig getifaddr en1 2>/dev/null || echo "本机IP")

echo "=============================================================="
echo " DC-S5 无线监看"
echo "=============================================================="
echo " 相机 IP    : $HOST"
if ping -c1 -W1 "$HOST" >/dev/null 2>&1; then
  echo " 连通性     : OK  能 ping 通相机"
else
  echo " 连通性     : 失败 —— 请让本机连上相机 Wi-Fi，或确认相机在局域网内的 IP"
fi
echo " 监视器地址 : http://${IP}:${PORT}"
echo "=============================================================="
echo
# ★ 默认走"官方标准"：固定 18fps（相机 640p 取景流的官方帧率）
MODE="${ARGS[2]:-fixed}"
FPS="${ARGS[3]:-18}"
echo " 节奏模式   : $MODE ($FPS fps)"
echo
exec python3 "$(dirname "$0")/s5monitor.py" --host "$HOST" --port "$PORT" \
     --pacing-mode "$MODE" --pacing-fps "$FPS" --device-name "LUMIX Sync"
