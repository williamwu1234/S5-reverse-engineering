#!/bin/bash
# ─────────────────────────────────────────────────────────────
# 启动 DC-S5 无线监看（双击运行）
#
#   用法：
#     双击本文件                        → 询问相机 IP（默认热点网关）
#     ./启动.command 192.168.54.1       → 直接指定相机 IP
#
#   网络选择（重要）：
#     · 相机【热点模式】（推荐，最流畅）：相机开启 Wi-Fi 遥控/发送图像后，
#       Mac 连上相机热点，相机 IP 就是 192.168.54.1 —— 直连低延迟
#     · 家网模式：相机与电脑连同一路由器，用相机在家网里的 IP
# ─────────────────────────────────────────────────────────────
cd "$(dirname "$0")" || exit 1

# ── 挑解释器：.venv 优先 → 系统里第一个带 numpy+PIL 的 → 普通 python3 ──
PY=""
if [ -x .venv/bin/python3 ] && .venv/bin/python3 -c "import numpy, PIL" >/dev/null 2>&1; then
  PY=".venv/bin/python3"
else
  for c in "$(command -v python3 2>/dev/null)" /opt/homebrew/bin/python3 \
           /usr/local/bin/python3 /usr/bin/python3; do
    [ -x "$c" ] || continue
    if "$c" -c "import numpy, PIL" >/dev/null 2>&1; then PY="$c"; break; fi
    [ -z "$PY" ] && PY="$c"
  done
fi
if [ -z "$PY" ]; then
  echo "❌ 找不到 python3。请先运行「首次运行_安装依赖.command」"
  exit 1
fi

if "$PY" -c "import numpy, PIL" >/dev/null 2>&1; then
  echo "✅ 解释器: $PY（含 numpy/Pillow ⇒ LUT 面板可用）"
else
  echo "⚠️  $PY 缺 numpy/Pillow ⇒ LUT 面板将禁用（监看/对焦/拍照不受影响）"
  echo "   想启用 LUT：先双击「首次运行_安装依赖.command」"
fi

# ── 相机 IP ──
CAM="${1:-}"
if [ -z "$CAM" ]; then
  printf "相机 IP [默认 192.168.54.1（热点网关）]: "
  read -r CAM
  [ -z "$CAM" ] && CAM="192.168.54.1"
fi
case "$CAM" in
  ''|*[!0-9.]*) echo "IP 不合法，使用默认 192.168.54.1"; CAM="192.168.54.1" ;;
esac

echo
echo "🎥 相机 $CAM    本机界面 http://127.0.0.1:8080"
echo "   启动后等 10–20 秒让授权完成（顶栏显示 access=ok）。"
echo "   ⚠️ 切勿反复重启本程序 —— 相机会判定为异常 App（详见 README 铁律）。"
echo

exec "$PY" -u s5monitor.py --host "$CAM" --port 8080 --device-name "LUMIX Sync"
