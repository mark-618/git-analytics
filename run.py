#!/usr/bin/env python3
"""
Git Analytics - 一键运行
扫描本地 Git 仓库，生成个人代码习惯体检报告
"""

import os
import sys

def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))

    # 默认扫描桌面
    scan_dir = sys.argv[1] if len(sys.argv) > 1 else os.path.expanduser("~/Desktop")

    print("=" * 60)
    print("🔍 Git Analytics - 个人代码习惯体检工具")
    print("=" * 60)
    print(f"扫描目录: {scan_dir}")
    print()

    # 1. 收集数据
    print("📊 第一步：收集 Git 仓库数据...")
    os.system(f'python3 "{script_dir}/git_analytics.py" "{scan_dir}"')

    print()
    print("📝 第二步：生成体检报告...")
    os.system(f'python3 "{script_dir}/generate_report.py"')

    print()
    print("=" * 60)
    print("✅ 完成！")
    print(f"📄 报告文件: {os.path.join(script_dir, 'report.html')}")
    print(f"📊 数据文件: {os.path.join(script_dir, 'data.json')}")
    print()
    print("用浏览器打开 report.html 查看你的代码习惯体检报告")
    print("=" * 60)


if __name__ == '__main__':
    main()
