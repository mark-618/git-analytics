#!/usr/bin/env python3
"""
Git Analytics - 一键运行
扫描本地 Git 仓库，生成个人代码习惯体检报告
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

from generate_report import main as generate_report
from git_analytics import OUTPUT_DATA, OUTPUT_REPORT, main as collect_data


def _open_file(path):
    if sys.platform == 'darwin':
        subprocess.run(['open', path], check=False)
    elif os.name == 'nt':
        os.startfile(path)  # type: ignore[attr-defined]
    else:
        subprocess.run(['xdg-open', path], check=False)


def _find_share_card_template():
    candidates = [
        Path(__file__).resolve().with_name('share-card.html'),
        Path(sys.prefix) / 'share' / 'git-analytics' / 'share-card.html',
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    return None


def _is_interactive():
    return sys.stdin.isatty() and sys.stdout.isatty()


def _button_choice(title, options, default=1):
    print(title)
    for idx, (label, desc) in enumerate(options, 1):
        suffix = "  ← 默认" if idx == default else ""
        print(f"  [{idx}] {label}{suffix}")
        if desc:
            print(f"      {desc}")
    raw = input(f"选择 [{default}]: ").strip()
    if not raw:
        return default
    try:
        value = int(raw)
    except ValueError:
        return default
    if 1 <= value <= len(options):
        return value
    return default


def _confirm(title, default=True):
    default_text = "Y/n" if default else "y/N"
    raw = input(f"{title} [{default_text}]: ").strip().lower()
    if not raw:
        return default
    return raw in {"y", "yes", "1", "true"}


def _path_label(path):
    return os.path.abspath(os.path.expanduser(path))


def _existing_path(path):
    expanded = os.path.abspath(os.path.expanduser(path))
    return expanded if os.path.isdir(expanded) else None


def _run_wizard(args):
    home = os.path.expanduser("~")
    current = os.getcwd()
    candidates = [
        ("当前目录", current),
        ("Desktop", os.path.join(home, "Desktop")),
        ("Projects", os.path.join(home, "Projects")),
        ("Code", os.path.join(home, "Code")),
        ("自定义路径", None),
    ]
    options = []
    values = []
    for label, path in candidates:
        if path is None:
            options.append((label, "输入一个或多个目录，用逗号分隔"))
            values.append(None)
            continue
        existing = _existing_path(path)
        if existing:
            options.append((label, existing))
            values.append(existing)

    print()
    print("Git Analytics Setup")
    print("像选开关一样跑一次，不用记命令参数。")
    print()

    choice = _button_choice("扫描哪里？", options, default=1)
    selected = values[choice - 1]
    if selected is None:
        raw = input("输入扫描目录（多个目录用逗号分隔）: ").strip()
        scan_dirs = [p.strip() for p in raw.split(",") if p.strip()]
        if not scan_dirs:
            scan_dirs = [current]
    else:
        scan_dirs = [selected]

    depth_choice = _button_choice(
        "扫描深度？",
        [
            ("标准", "max-depth = 3，适合大多数项目目录"),
            ("更深", "max-depth = 5，适合 repo 放得更散的目录"),
            ("自定义", "手动输入深度"),
        ],
        default=1,
    )
    if depth_choice == 1:
        max_depth = 3
    elif depth_choice == 2:
        max_depth = 5
    else:
        raw = input("输入 max-depth [3]: ").strip()
        try:
            max_depth = int(raw) if raw else 3
        except ValueError:
            max_depth = 3

    output_raw = input(f"输出目录 [{os.getcwd()}]: ").strip()
    output_dir = output_raw or os.getcwd()

    args.scan_dir = scan_dirs
    args.max_depth = max_depth
    args.output_dir = output_dir
    args.open = _confirm("生成后自动打开报告？", default=True)
    args.share_card = _confirm("同时生成分享卡片设计器？", default=True)
    print()
    return args


def main():
    parser = argparse.ArgumentParser(description='Git Analytics - 个人代码习惯体检工具')
    parser.add_argument('scan_dir', nargs='*',
                        help='扫描目录，可传多个；默认扫描当前目录')
    parser.add_argument('--since', help='起始日期，如 2024-01-01')
    parser.add_argument('--until', help='截止日期，如 2024-12-31')
    parser.add_argument('--project', help='只分析指定项目（支持模糊匹配）')
    parser.add_argument('--output-dir', default=os.getcwd(), help='输出目录（默认当前目录）')
    parser.add_argument('--max-depth', type=int, default=3, help='扫描目录深度（默认 3）')
    parser.add_argument('--open', action='store_true', help='生成后自动打开报告')
    parser.add_argument('--share-card', action='store_true', help='同时输出 PNG 分享卡片设计器')
    parser.add_argument('--no-wizard', action='store_true', help='关闭交互式向导，直接使用默认参数')
    args = parser.parse_args()

    if not args.scan_dir and not args.no_wizard and _is_interactive():
        args = _run_wizard(args)

    scan_dirs = args.scan_dir or [os.getcwd()]
    output_dir = os.path.abspath(os.path.expanduser(args.output_dir))
    data_path = os.path.join(output_dir, OUTPUT_DATA)
    report_path = os.path.join(output_dir, OUTPUT_REPORT)
    share_card_path = os.path.join(output_dir, 'share-card.html')

    print("=" * 60)
    print("🔍 Git Analytics - 个人代码习惯体检工具")
    print("=" * 60)
    print("扫描目录:")
    for item in scan_dirs:
        print(f"  - {os.path.abspath(os.path.expanduser(item))}")
    print(f"扫描深度: {args.max_depth}")
    print(f"输出目录: {output_dir}")
    if args.since or args.until:
        print(f"时间范围: {args.since or '起始'} ~ {args.until or '至今'}")
    if args.project:
        print(f"指定项目: {args.project}")
    print()

    # 1. 收集数据
    print("📊 第一步：收集 Git 仓库数据...")
    analysis = collect_data(
        scan_dir=scan_dirs,
        since=args.since,
        until=args.until,
        project=args.project,
        output_dir=output_dir,
        max_depth=args.max_depth,
    )
    if analysis is None:
        raise SystemExit(1)

    print()
    print("📝 第二步：生成体检报告...")
    generate_report(data_path=data_path, output_path=report_path)

    if args.share_card:
        template = _find_share_card_template()
        if template:
            shutil.copyfile(template, share_card_path)
        else:
            print("⚠️ 未找到 share-card.html 模板，跳过分享器输出")

    if args.open:
        _open_file(report_path)

    print()
    print("=" * 60)
    print("✅ 完成！")
    print(f"📄 报告文件: {report_path}")
    print(f"📊 数据文件: {data_path}")
    if args.share_card and os.path.exists(share_card_path):
        print(f"🖼️ 分享器: {share_card_path}")
    print()
    print("用浏览器打开 report.html 查看你的代码习惯体检报告")
    print("=" * 60)


if __name__ == '__main__':
    main()
