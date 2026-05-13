#!/bin/bash
# Git Analytics - 一键运行脚本
# 用法: ./run.sh [项目目录]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCAN_DIR="${1:-$HOME/Desktop}"

echo "🚀 Git Analytics - 代码习惯分析工具"
echo "===================================="
echo ""

# 1. 收集数据
echo "📊 步骤 1/2: 收集 Git 数据..."
bash "$SCRIPT_DIR/collect_data.sh" "$SCAN_DIR"

echo ""

# 2. 生成报告
echo "🎨 步骤 2/2: 生成 HTML 报告..."
python3 "$SCRIPT_DIR/generate_report.py" "$SCRIPT_DIR/data.json"

echo ""

# 3. 打开报告
if [ -f "$SCRIPT_DIR/report.html" ]; then
    echo "🌐 正在打开报告..."
    open "$SCRIPT_DIR/report.html"
fi

echo ""
echo "✨ 完成!"
echo "📁 数据文件: $SCRIPT_DIR/data.json"
echo "📊 报告文件: $SCRIPT_DIR/report.html"
