#!/usr/bin/env python3
"""
Git Analytics - 一键运行
扫描本地 Git 仓库，生成个人代码习惯体检报告
"""

import argparse
import os

from generate_report import main as generate_report
from git_analytics import OUTPUT_DATA, OUTPUT_REPORT, main as collect_data


def main():
    parser = argparse.ArgumentParser(description='Git Analytics - 个人代码习惯体检工具')
    parser.add_argument('scan_dir', nargs='?', default=os.path.expanduser("~/Desktop"),
                        help='扫描目录（默认桌面）')
    parser.add_argument('--since', help='起始日期，如 2024-01-01')
    parser.add_argument('--until', help='截止日期，如 2024-12-31')
    parser.add_argument('--project', help='只分析指定项目（支持模糊匹配）')
    parser.add_argument('--output-dir', default=os.getcwd(), help='输出目录（默认当前目录）')
    args = parser.parse_args()

    output_dir = os.path.abspath(os.path.expanduser(args.output_dir))
    data_path = os.path.join(output_dir, OUTPUT_DATA)
    report_path = os.path.join(output_dir, OUTPUT_REPORT)

    print("=" * 60)
    print("🔍 Git Analytics - 个人代码习惯体检工具")
    print("=" * 60)
    print(f"扫描目录: {args.scan_dir}")
    print(f"输出目录: {output_dir}")
    if args.since or args.until:
        print(f"时间范围: {args.since or '起始'} ~ {args.until or '至今'}")
    if args.project:
        print(f"指定项目: {args.project}")
    print()

    # 1. 收集数据
    print("📊 第一步：收集 Git 仓库数据...")
    analysis = collect_data(
        scan_dir=args.scan_dir,
        since=args.since,
        until=args.until,
        project=args.project,
        output_dir=output_dir,
    )
    if analysis is None:
        raise SystemExit(1)

    print()
    print("📝 第二步：生成体检报告...")
    generate_report(data_path=data_path, output_path=report_path)

    print()
    print("=" * 60)
    print("✅ 完成！")
    print(f"📄 报告文件: {report_path}")
    print(f"📊 数据文件: {data_path}")
    print()
    print("用浏览器打开 report.html 查看你的代码习惯体检报告")
    print("=" * 60)


if __name__ == '__main__':
    main()
