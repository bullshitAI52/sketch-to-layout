#!/bin/bash
# ==============================================
#   香蕉模型 草图 → 布局图  一键启动脚本
# ==============================================

set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo ""
echo "🍌  香蕉模型 草图 → 布局图"
echo "──────────────────────────────"

# 创建必要目录
mkdir -p uploads outputs

# 检查 Python3
if ! command -v python3 &>/dev/null; then
    echo "❌  未检测到 python3，请先安装 Python 3.9+"
    exit 1
fi

# 检查/创建虚拟环境
if [ ! -d ".venv" ]; then
    echo "📦  正在创建虚拟环境..."
    python3 -m venv .venv
fi

source .venv/bin/activate

# 安装依赖
echo "📥  检查并安装依赖..."
pip install -q -r requirements.txt

echo ""
echo "✅  依赖就绪！正在启动服务..."
echo "🌐  打开浏览器访问: http://127.0.0.1:5050"
echo "    (按 Ctrl+C 停止服务)"
echo ""

# 启动 Flask
python3 app.py
