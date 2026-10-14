#!/bin/bash
# ─────────────────────────────────────────────────────────────
# 首次运行：安装依赖（双击运行一次即可）
#
#   LUT 实时套用需要 numpy + Pillow；本脚本会在这包旁边创建
#   一个独立的虚拟环境 .venv，不污染系统 Python。
#   · 已装好 → 校验后直接退出
#   · 安装失败 → 自动换国内镜像重试
#   · 若以后移动了本文件夹 → 删除 .venv 后重跑本脚本
# ─────────────────────────────────────────────────────────────
cd "$(dirname "$0")" || exit 1

PY=""
for c in python3 /usr/bin/python3 /opt/homebrew/bin/python3 /usr/local/bin/python3; do
  if command -v "$c" >/dev/null 2>&1; then PY="$c"; break; fi
done
if [ -z "$PY" ]; then
  echo "❌ 找不到 python3。请先安装命令行工具："
  echo "   xcode-select --install"
  exit 1
fi
echo "使用解释器: $PY"

if [ -x .venv/bin/python3 ]; then
  if .venv/bin/python3 -c "import numpy, PIL" >/dev/null 2>&1; then
    echo "✅ 依赖已就绪，无需重装。"
    echo "   （如需强制重装：删除本目录下的 .venv 再双击本脚本）"
    exit 0
  fi
  echo "⚠️ .venv 存在但依赖缺失，重建环境…"
  rm -rf .venv
fi

echo "创建虚拟环境 .venv …"
if ! "$PY" -m venv .venv; then
  echo "❌ 创建虚拟环境失败。"
  echo "   备选方案：手动执行  python3 -m pip install --user numpy pillow"
  exit 1
fi

echo "安装 numpy + Pillow …"
if .venv/bin/python3 -m pip install --quiet --disable-pip-version-check numpy pillow 2>/dev/null; then
  echo "✅ 官方源安装完成"
else
  echo "  官方源失败，尝试清华镜像…"
  if .venv/bin/python3 -m pip install --quiet --disable-pip-version-check \
       -i https://pypi.tuna.tsinghua.edu.cn/simple numpy pillow; then
    echo "✅ 镜像安装完成"
  else
    echo "❌ 安装失败。请手动执行："
    echo "   .venv/bin/python3 -m pip install numpy pillow"
    exit 1
  fi
fi

if .venv/bin/python3 -c "import numpy, PIL; print('✅ 验证通过：numpy %s · Pillow %s' % (numpy.__version__, PIL.__version__))"; then
  echo
  echo "安装完成！以后直接双击「启动.command」即可（会自动使用 .venv）。"
else
  echo "❌ 验证失败，请检查网络后重试。"
  exit 1
fi
