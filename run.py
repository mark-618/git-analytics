#!/usr/bin/env python3
"""
Git Analytics - 一键运行
扫描本地 Git 仓库，生成个人代码习惯体检报告
"""

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(description='Git Analytics - 个人代码习惯体检工具')
    parser.add_argument('scan_dir', nargs='?', default=os.path.expanduser("~/Desktop"),
                        help='扫描目录（默认桌面）')
    parser.add_argument('--since', help='起始日期，如 2024-01-01')
    parser.add_argument('--until', help='截止日期，如 2024-12-31')
    parser.add_argument('--project', help='只分析指定项目（支持模糊匹配）')
    args = parser.parse_args()

    script_dir = os.path.dirname(os.path.abspath(__file__))

    print("=" * 60)
    print("🔍 Git Analytics - 个人代码习惯体检工具")
    print("=" * 60)
    print(f"扫描目录: {args.scan_dir}")
    if args.since or args.until:
        print(f"时间范围: {args.since or '起始'} ~ {args.until or '至今'}")
    if args.project:
        print(f"指定项目: {args.project}")
    print()

    # 构建参数
    extra_args = f'"{args.scan_dir}"'
    if args.since:
        extra_args += f' --since {args.since}'
    if args.until:
        extra_args += f' --until {args.until}'
    if args.project:
        extra_args += f' --project "{args.project}"'

    # 1. 收集数据
    print("📊 第一步：收集 Git 仓库数据...")
    os.system(f'python3 "{script_dir}/git_analytics.py" {extra_args}')

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
