#!/usr/bin/env python3
"""
Git Analytics - 分享卡片生成器
从 data.json 读取数据，生成可分享的代码画像图片
"""

import json
import argparse
import os
import sys
from datetime import datetime

try:
    from PIL import Image, ImageDraw, ImageFont
except ImportError:
    print("需要安装 Pillow 才能生成 PNG 分享卡片。")
    print("运行: pip install git-analytics-cli[share-card]")
    sys.exit(1)


# --- 默认配色方案 ---
THEMES = {
    'default': {
        'bg_top': (15, 12, 41),       # 深紫
        'bg_bot': (36, 36, 62),       # 深蓝紫
        'accent1': (167, 139, 250),   # 紫
        'accent2': (96, 165, 250),    # 蓝
        'gold': (251, 191, 36),       # 金色
    },
    'ocean': {
        'bg_top': (10, 25, 49),
        'bg_bot': (15, 50, 80),
        'accent1': (72, 209, 204),
        'accent2': (100, 181, 246),
        'gold': (255, 214, 110),
    },
    'forest': {
        'bg_top': (15, 32, 20),
        'bg_bot': (25, 55, 35),
        'accent1': (129, 199, 132),
        'accent2': (165, 214, 167),
        'gold': (255, 213, 79),
    },
    'sunset': {
        'bg_top': (45, 10, 25),
        'bg_bot': (75, 20, 45),
        'accent1': (255, 138, 101),
        'accent2': (255, 183, 77),
        'gold': (255, 235, 59),
    },
    'minimal': {
        'bg_top': (30, 30, 30),
        'bg_bot': (50, 50, 50),
        'accent1': (200, 200, 200),
        'accent2': (160, 160, 160),
        'gold': (255, 255, 255),
    },
}


def load_font(size):
    """加载中文字体"""
    paths = [
        "/System/Library/Fonts/PingFang.ttc",
        "/System/Library/Fonts/STHeiti Medium.ttc",
        "/System/Library/Fonts/Hiragino Sans GB.ttc",
    ]
    for p in paths:
        try:
            return ImageFont.truetype(p, size)
        except Exception:
            continue
    return ImageFont.load_default()


def load_data(data_path):
    """加载分析数据"""
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_date_range(data, since=None, until=None):
    """获取时间范围文本"""
    if since and until:
        return f"{since} ~ {until}"

    # 从数据中提取
    projects = data.get('projects', [])
    all_first = []
    all_last = []
    for p in projects:
        if p.get('first_commit'):
            all_first.append(p['first_commit'])
        if p.get('last_commit'):
            all_last.append(p['last_commit'])

    if all_first and all_last:
        start = min(all_first)
        end = max(all_last)
        # 格式化为简短日期
        start_fmt = datetime.strptime(start, '%Y-%m-%d').strftime('%Y.%m.%d')
        end_fmt = datetime.strptime(end, '%Y-%m-%d').strftime('%Y.%m.%d')
        return f"{start_fmt} ~ {end_fmt}"

    return "全部时间"


def draw_card(data, theme_colors, output_path, date_range=None):
    """绘制分享卡片"""
    W, H = 420, 720

    # 解包颜色
    bg_top = theme_colors['bg_top']
    bg_bot = theme_colors['bg_bot']
    accent1 = theme_colors['accent1']
    accent2 = theme_colors['accent2']
    gold = theme_colors['gold']

    white = (255, 255, 255)
    white_80 = (255, 255, 255, 204)
    white_50 = (255, 255, 255, 128)
    white_30 = (255, 255, 255, 77)
    white_10 = (255, 255, 255, 26)
    glass_bg = (255, 255, 255, 15)
    glass_border = (255, 255, 255, 26)

    # 提取数据
    summary = data.get('summary', {})
    persona = data.get('persona', {})
    score = data.get('habit_score', {}).get('total', 0)
    tags = data.get('developer_tags', [])
    dimensions = persona.get('dimensions', {})

    commits = str(summary.get('total_commits', 0))
    active_days = str(summary.get('total_active_days', 0))
    projects = str(summary.get('total_projects', 0))
    persona_icon = persona.get('icon', '?')
    persona_name = persona.get('name', '未知')
    persona_code = persona.get('code', '??????')

    # 维度标签
    dim_list = []
    dim_names = {
        'time': '时间偏好', 'rhythm': '节奏风格', 'focus': '专注程度',
        'style': '开发风格', 'engineering': '工程取向', 'ai': 'AI 协作'
    }
    dim_traits = {
        'time': {'D': '白天型', 'N': '夜猫型'},
        'rhythm': {'S': '冲刺型', 'M': '马拉松型'},
        'focus': {'C': '核心深挖', 'D': '多线并行'},
        'style': {'P': '功能开拓', 'G': '系统守护'},
        'engineering': {'Q': '质量洁癖', 'R': '快速迭代'},
        'ai': {'A': 'AI 搭子', 'H': '纯手工'},
    }
    dim_icons = {
        'time': '☀️', 'rhythm': '⚡', 'focus': '🎯',
        'style': '🚀', 'engineering': '✨', 'ai': '🤖'
    }
    for key in ['time', 'rhythm', 'focus', 'style', 'engineering', 'ai']:
        dim = dimensions.get(key, {})
        code = dim.get('code', '?')
        trait = dim_traits.get(key, {}).get(code, '未知')
        icon = dim_icons.get(key, '?')
        dim_list.append((icon, dim_names.get(key, key), trait))

    # 标签药丸
    tag_texts = []
    for t in tags[1:6]:  # 跳过主标签，取最多5个
        icon = t.get('icon', '')
        name = t.get('name', '')
        tag_texts.append(f"{icon} {name}")

    # 时间范围
    if not date_range:
        date_range = get_date_range(data)

    # --- 加载字体 ---
    font_title = load_font(18)
    font_persona_name = load_font(32)
    font_persona_code = load_font(14)
    font_stat_val = load_font(30)
    font_stat_label = load_font(11)
    font_dim_label = load_font(9)
    font_dim_val = load_font(11)
    font_score_val = load_font(48)
    font_score_label = load_font(12)
    font_tag = load_font(11)
    font_footer = load_font(10)
    font_date = load_font(11)

    # --- 创建画布 ---
    img = Image.new("RGBA", (W, H), bg_top)
    draw = ImageDraw.Draw(img)

    # 渐变背景
    for y in range(H):
        ratio = y / H
        r = int(bg_top[0] + (bg_bot[0] - bg_top[0]) * ratio)
        g = int(bg_top[1] + (bg_bot[1] - bg_top[1]) * ratio)
        b = int(bg_top[2] + (bg_bot[2] - bg_top[2]) * ratio)
        draw.line([(0, y), (W, y)], fill=(r, g, b, 255))

    # --- 辅助函数 ---
    def center_text(text, font, y_pos, color=white):
        bbox = draw.textbbox((0, 0), text, font=font)
        tw = bbox[2] - bbox[0]
        x = (W - tw) // 2
        draw.text((x, y_pos), text, fill=color, font=font)

    def draw_rounded_rect(xy, radius, fill=None, outline=None, width=1):
        draw.rounded_rectangle(xy, radius=radius, fill=fill, outline=outline, width=width)

    # --- 绘制内容 ---
    pad = 36
    y = 36

    # 人格图标
    center_text(persona_icon, font_persona_name, y, white)
    y += 44

    # 标题
    center_text("我的代码画像", font_title, y, accent1)
    y += 28

    # 人格名称
    center_text(persona_name, font_persona_name, y, white)
    y += 42

    # 代码
    center_text(persona_code, font_persona_code, y, white_50)
    y += 28

    # --- 时间范围 ---
    center_text(date_range, font_date, y, white_30)
    y += 24

    # --- 三个数据卡片 ---
    stat_y = y
    stat_w = (W - pad * 2 - 20) // 3
    stat_items = [
        (commits, "次提交"),
        (active_days, "天活跃"),
        (projects, "个项目"),
    ]
    for i, (val, label) in enumerate(stat_items):
        sx = pad + i * (stat_w + 10)
        draw_rounded_rect((sx, stat_y, sx + stat_w, stat_y + 80), radius=12, fill=glass_bg, outline=glass_border)
        # 数值
        bbox = draw.textbbox((0, 0), val, font=font_stat_val)
        tw = bbox[2] - bbox[0]
        draw.text((sx + (stat_w - tw) // 2, stat_y + 14), val, fill=accent2, font=font_stat_val)
        # 标签
        bbox = draw.textbbox((0, 0), label, font=font_stat_label)
        tw = bbox[2] - bbox[0]
        draw.text((sx + (stat_w - tw) // 2, stat_y + 52), label, fill=white_50, font=font_stat_label)

    y = stat_y + 96

    # --- 六个维度芯片 ---
    dim_y = y
    dim_w = (W - pad * 2 - 16) // 3
    dim_h = 64
    for i, (icon, label, val) in enumerate(dim_list):
        col = i % 3
        row = i // 3
        dx = pad + col * (dim_w + 8)
        dy = dim_y + row * (dim_h + 8)
        draw_rounded_rect((dx, dy, dx + dim_w, dy + dim_h), radius=10, fill=glass_bg, outline=glass_border)
        # 标签
        bbox = draw.textbbox((0, 0), label, font=font_dim_label)
        tw = bbox[2] - bbox[0]
        draw.text((dx + (dim_w - tw) // 2, dy + 10), label, fill=white_30, font=font_dim_label)
        # 值
        bbox = draw.textbbox((0, 0), val, font=font_dim_val)
        tw = bbox[2] - bbox[0]
        draw.text((dx + (dim_w - tw) // 2, dy + 32), val, fill=white_80, font=font_dim_val)

    y = dim_y + 2 * (dim_h + 8) + 16

    # --- 分数条 ---
    score_y = y
    draw_rounded_rect((pad, score_y, W - pad, score_y + 80), radius=14, fill=glass_bg, outline=glass_border)

    # 分数数字
    draw.text((pad + 24, score_y + 12), str(score), fill=gold, font=font_score_val)

    # 右侧
    rx = pad + 100
    draw.text((rx, score_y + 18), "习惯健康分 / 100", fill=white_50, font=font_score_label)

    # 进度条
    bar_y = score_y + 44
    bar_w = W - pad * 2 - 120
    bar_x = rx
    draw_rounded_rect((bar_x, bar_y, bar_x + bar_w, bar_y + 6), radius=3, fill=white_10)
    fill_w = int(bar_w * score / 100)
    draw_rounded_rect((bar_x, bar_y, bar_x + fill_w, bar_y + 6), radius=3, fill=gold)

    y = score_y + 96

    # --- 标签药丸 ---
    if tag_texts:
        tag_y = y
        tag_gap = 8
        tag_widths = []
        for t in tag_texts:
            bbox = draw.textbbox((0, 0), t, font=font_tag)
            tag_widths.append(bbox[2] - bbox[0] + 20)

        total_w = sum(tag_widths) + tag_gap * (len(tag_texts) - 1)
        tx = (W - total_w) // 2

        for i, t in enumerate(tag_texts):
            tw = tag_widths[i]
            draw_rounded_rect((tx, tag_y, tx + tw, tag_y + 28), radius=14, fill=glass_bg, outline=glass_border)
            draw.text((tx + 10, tag_y + 6), t, fill=white_80, font=font_tag)
            tx += tw + tag_gap

        y = tag_y + 44

    # --- 分割线 ---
    draw.line([(pad, y), (W - pad, y)], fill=white_10, width=1)
    y += 16

    # --- 底部品牌 ---
    center_text("Git Analytics · 代码习惯体检", font_footer, y, white_30)

    # --- 保存 ---
    img = img.convert("RGB")
    img.save(output_path, "PNG")
    print(f"✅ 卡片已保存: {output_path}")


def main():
    parser = argparse.ArgumentParser(description='生成代码画像分享卡片')
    parser.add_argument('--data', default='data.json', help='数据文件路径 (默认: data.json)')
    parser.add_argument('--output', default='share_card.png', help='输出图片路径 (默认: share_card.png)')
    parser.add_argument('--theme', choices=list(THEMES.keys()), default='default',
                        help='配色主题 (默认: default)')
    parser.add_argument('--since', help='起始日期 (如: 2024-01-01)')
    parser.add_argument('--until', help='截止日期 (如: 2025-12-31)')
    args = parser.parse_args()

    # 加载数据
    data_path = os.path.abspath(args.data)
    if not os.path.exists(data_path):
        print(f"❌ 数据文件不存在: {data_path}")
        print("请先运行 git_analytics.py 生成数据")
        return

    data = load_data(data_path)

    # 构建时间范围文本
    date_range = None
    if args.since or args.until:
        since = args.since or '...'
        until = args.until or '至今'
        date_range = f"{since} ~ {until}"

    # 获取主题颜色
    theme_colors = THEMES[args.theme]

    # 生成卡片
    output_path = os.path.abspath(args.output)
    draw_card(data, theme_colors, output_path, date_range)


if __name__ == '__main__':
    main()
