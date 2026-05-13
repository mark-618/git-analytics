#!/bin/bash
# Git Analytics - 一键运行脚本
# 用法: ./run.sh [项目目录]

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
SCAN_DIR="${1:-$HOME/Desktop}"

echo "🚀 Git Analytics - 代码习惯分析工具"
echo "===================================="
echo ""

# 1. 运行 Python CLI
python3 "$SCRIPT_DIR/run.py" "$SCAN_DIR" --output-dir "$SCRIPT_DIR"

echo ""

# 2. 打开报告
if [ -f "$SCRIPT_DIR/report.html" ]; then
    echo "🌐 正在打开报告..."
    open "$SCRIPT_DIR/report.html"
fi

echo ""
echo "✨ 完成!"
echo "📁 数据文件: $SCRIPT_DIR/data.json"
echo "📊 报告文件: $SCRIPT_DIR/report.html"
