#!/bin/bash
# s5gate_test.sh —— 判定「取景流是否独占相机、导致 camctrl 全部 err_busy」
#
# 做法：在【停流 / 开流】两个状态下分别测 camctrl，对照结果即可定论。
# 前提：先给相机断电重启（清掉所有残留流会话），再启动服务（建议 --no-stream）。
#
# 用法:  ./s5gate_test.sh            # 默认测 127.0.0.1:8080 的服务
set -u
BASE="${1:-http://127.0.0.1:8080}"
CGI="http://192.168.1.131/cam.cgi"

probe() {   # $1=标签
  printf "  %-40s" "$1"
  local out
  out=$(curl -s --max-time 8 "$CGI?mode=camctrl&type=af_ae_lock&value=on")
  case "$out" in
    *"<result>ok</result>"*)        echo "✅ ok" ;;
    *"<result>err_busy</result>"*)  echo "❌ err_busy（相机忙）" ;;
    *"<result>err_reject</result>"*)echo "❌ err_reject（会话未批准/被拒）" ;;
    *"<result>err_critical</result>"*) echo "❌ err_critical" ;;
    *) echo "? ${out:0:60}" ;;
  esac
  sleep 1
}

echo "=================================================================="
echo " 关键实验：取景流 vs camctrl"
echo "=================================================================="
echo " 服务状态："
curl -s --max-time 6 "$BASE/api/state" | python3 -c "
import sys,json
try:
    d=json.load(sys.stdin)
    print('   权限=%s  流=%s  fps=%s  帧数=%s' % (d.get('access_mode'),d.get('streaming'),d.get('fps'),d.get('frames')))
except Exception: print('   !! 服务未响应（先启动 s5monitor.py）')
" 2>/dev/null

echo
echo "--- A) 当前状态（如果正在推流，就是「有流」）---"
probe "camctrl af_ae_lock（当前）"

echo
echo "--- B) 停掉取景流后 ---"
curl -s --max-time 15 "$BASE/api/stream?action=stop" >/dev/null
sleep 4
probe "camctrl af_ae_lock（停流后）"
probe "camctrl touch 320/216（停流后）"

echo
echo "--- C) 重新开流后 ---"
curl -s --max-time 25 "$BASE/api/stream?action=start" >/dev/null
sleep 6
probe "camctrl af_ae_lock（开流后）"

echo
echo "--- D) 收尾：再停流 ---"
curl -s --max-time 15 "$BASE/api/stream?action=stop" >/dev/null
sleep 3
probe "camctrl af_ae_lock（再次停流后）"

echo "=================================================================="
echo " 判读："
echo "   B/D 为 ok、A/C 为 err_busy  ⇒ 【取景流独占相机】是根因"
echo "                                ⇒ 需要"控制时暂停取景"或改用 camcmd 路线"
echo "   全部 err_busy             ⇒ 与流无关，是相机会话/固件层的门控"
echo "   全部 err_reject           ⇒ 会话没被批准（去相机屏幕点「允许」）"
echo "=================================================================="
