#!/usr/bin/env python3
"""
Git Analytics - 个人代码习惯体检工具
扫描本地 Git 仓库，生成跨项目的个人开发画像
"""

import os
import json
import subprocess
import re
from datetime import datetime, timedelta
from collections import defaultdict, Counter
from pathlib import Path

# ============================================================
# 配置
# ============================================================
DEFAULT_SCAN_DIR = os.path.expanduser("~/Desktop")
OUTPUT_DATA = "data.json"
OUTPUT_REPORT = "report.html"

# commit message 低信息量关键词
LOW_INFO_PATTERNS = [
    r'^update$', r'^fix$', r'^wip$', r'^temp$', r'^misc$',
    r'^test$', r'^debug$', r'^tmp$', r'^save$', r'^checkpoint$',
    r'^\.+$', r'^merge', r'^revert'
]

# 测试文件模式
TEST_PATTERNS = [
    r'test[/\\]', r'tests[/\\]', r'__tests__[/\\]',
    r'\.spec\.', r'\.test\.', r'_test\.', r'test_',
    r'pytest', r'jest', r'vitest', r'unittest'
]

# 文档文件模式
DOC_PATTERNS = [
    r'README', r'docs[/\\]', r'\.md$', r'CHANGELOG',
    r'CONTRIBUTING', r'\.rst$', r'\.txt$'
]

# AI 工具痕迹
AI_PATTERNS = [
    r'\.claude[/\\]', r'\.cursor[/\\]', r'\.github[/\\]copilot',
    r'CLAUDE\.md', r'AGENTS\.md', r'Generated with Claude',
    r'Co-Authored-By.*Claude', r'Co-Authored-By.*Copilot'
]


# ============================================================
# Git 仓库发现
# ============================================================
def find_git_repos(scan_dir, max_depth=3):
    """扫描目录，找到所有 Git 仓库"""
    repos = []
    scan_dir = os.path.expanduser(scan_dir)

    for root, dirs, files in os.walk(scan_dir):
        # 计算当前深度
        depth = root.replace(scan_dir, '').count(os.sep)
        if depth > max_depth:
            dirs.clear()
            continue

        if '.git' in dirs:
            repos.append(root)
            dirs.remove('.git')  # 不递归进入 .git

    return repos


# ============================================================
# Git 数据收集
# ============================================================
def run_git(repo_path, args):
    """在指定仓库执行 git 命令"""
    try:
        result = subprocess.run(
            ['git'] + args,
            cwd=repo_path,
            capture_output=True,
            text=True,
            timeout=30
        )
        return result.stdout.strip()
    except Exception:
        return ""


def collect_repo_data(repo_path, since=None, until=None):
    """收集单个仓库的详细数据"""
    repo_name = os.path.basename(repo_path)

    # 获取所有 commit 的详细信息
    # 格式: hash|timestamp|message
    log_cmd = ['log', '--all', '--format=%H|%at|%s', '--no-merges']
    if since:
        log_cmd.append(f'--since={since}')
    if until:
        log_cmd.append(f'--until={until}')
    log_output = run_git(repo_path, log_cmd)

    if not log_output:
        return None

    commits = []
    for line in log_output.split('\n'):
        if '|' not in line:
            continue
        parts = line.split('|', 2)
        if len(parts) < 3:
            continue
        hash_val, timestamp, message = parts
        try:
            ts = int(timestamp)
            dt = datetime.fromtimestamp(ts)
            commits.append({
                'hash': hash_val,
                'timestamp': ts,
                'datetime': dt,
                'hour': dt.hour,
                'weekday': dt.weekday(),  # 0=Monday
                'month': dt.strftime('%Y-%m'),
                'date': dt.strftime('%Y-%m-%d'),
                'message': message.strip()
            })
        except (ValueError, OSError):
            continue

    if not commits:
        return None

    # 获取文件类型统计（最近 100 个 commit）
    file_extensions = Counter()
    file_changes = []

    # 获取最近 commit 的文件变更
    recent_hashes = [c['hash'] for c in commits[:100]]
    for hash_val in recent_hashes[:20]:  # 只采样 20 个 commit
        diff_output = run_git(repo_path, [
            'diff-tree', '--no-commit-id', '-r', '--name-only', hash_val
        ])
        if diff_output:
            for f in diff_output.split('\n'):
                f = f.strip()
                if f:
                    file_changes.append(f)
                    ext = Path(f).suffix.lower()
                    if ext:
                        file_extensions[ext] += 1

    # 判断主要语言
    lang_map = {
        '.py': 'Python', '.js': 'JavaScript', '.ts': 'TypeScript',
        '.tsx': 'TypeScript', '.jsx': 'JavaScript', '.go': 'Go',
        '.rs': 'Rust', '.java': 'Java', '.cpp': 'C++', '.c': 'C',
        '.rb': 'Ruby', '.php': 'PHP', '.swift': 'Swift',
        '.kt': 'Kotlin', '.scala': 'Scala', '.sh': 'Shell',
        '.ipynb': 'Jupyter', '.md': 'Markdown', '.yaml': 'YAML',
        '.yml': 'YAML', '.json': 'JSON', '.html': 'HTML', '.css': 'CSS'
    }

    lang_counter = Counter()
    for ext, count in file_extensions.items():
        lang = lang_map.get(ext, 'Other')
        lang_counter[lang] += count

    main_language = lang_counter.most_common(1)[0][0] if lang_counter else 'Unknown'

    # 分析 commit 类型（基于 message）
    def classify_commit(msg):
        msg = msg.lower()
        if any(msg.startswith(p) for p in ['feat', 'feature', 'add', 'new']):
            return 'feat'
        elif any(msg.startswith(p) for p in ['fix', 'bug', 'patch', 'hotfix']):
            return 'fix'
        elif any(msg.startswith(p) for p in ['doc', 'readme', 'comment']):
            return 'docs'
        elif any(msg.startswith(p) for p in ['test', 'spec']):
            return 'test'
        elif any(msg.startswith(p) for p in ['refactor', 'clean', 'restructure']):
            return 'refactor'
        elif any(msg.startswith(p) for p in ['chore', 'build', 'ci', 'deps']):
            return 'chore'
        else:
            return 'other'

    commit_types = Counter()
    for c in commits:
        c['type'] = classify_commit(c['message'])
        commit_types[c['type']] += 1

    # 时间分布
    hourly = [0] * 24
    weekly = defaultdict(int)
    monthly = defaultdict(int)
    daily_commits = defaultdict(int)

    for c in commits:
        hourly[c['hour']] += 1
        weekly[c['weekday']] += 1
        monthly[c['month']] += 1
        daily_commits[c['date']] += 1

    # 活跃天数
    active_days = len(daily_commits)

    # 日期范围
    dates = sorted(daily_commits.keys())
    first_commit = dates[0] if dates else None
    last_commit = dates[-1] if dates else None

    # 测试/文档/重构意识（基于文件路径）
    test_files = 0
    doc_files = 0
    for f in file_changes:
        if any(re.search(p, f, re.I) for p in TEST_PATTERNS):
            test_files += 1
        if any(re.search(p, f, re.I) for p in DOC_PATTERNS):
            doc_files += 1

    # AI 痕迹检测
    ai_signals = []
    for c in commits[:50]:  # 检查最近 50 个 commit
        if any(re.search(p, c['message'], re.I) for p in AI_PATTERNS):
            ai_signals.append(c['message'])

    # 检查是否有 AI 相关文件
    for f in file_changes:
        if any(re.search(p, f, re.I) for p in AI_PATTERNS):
            ai_signals.append(f"AI file: {f}")

    return {
        'name': repo_name,
        'path': repo_path,
        'total_commits': len(commits),
        'first_commit': first_commit,
        'last_commit': last_commit,
        'active_days': active_days,
        'main_language': main_language,
        'commit_types': dict(commit_types),
        'hourly': hourly,
        'weekly': dict(weekly),
        'monthly': dict(monthly),
        'daily_commits': dict(daily_commits),
        'file_extensions': dict(file_extensions.most_common(20)),
        'test_files': test_files,
        'doc_files': doc_files,
        'total_file_changes': len(file_changes),
        'ai_signals': ai_signals[:10],
        'low_info_commits': sum(1 for c in commits if any(
            re.match(p, c['message'].lower()) for p in LOW_INFO_PATTERNS
        )),
        'commit_messages': [c['message'] for c in commits[:50]],
        'commits': [{'ts': c['timestamp'], 'hour': c['hour'], 'weekday': c['weekday'],
                      'month': c['month'], 'type': c['type']} for c in commits]
    }


# ============================================================
# 习惯分析引擎
# ============================================================
def analyze_habits(all_repos):
    """分析所有仓库的数据，生成习惯画像"""

    # 汇总数据
    total_commits = sum(r['total_commits'] for r in all_repos)
    total_projects = len(all_repos)

    # 合并时间分布
    total_hourly = [0] * 24
    total_weekly = defaultdict(int)
    total_monthly = defaultdict(int)

    for r in all_repos:
        for h in range(24):
            total_hourly[h] += r['hourly'][h]
        for k, v in r['weekly'].items():
            total_weekly[k] += v
        for k, v in r['monthly'].items():
            total_monthly[k] += v

    # 合并 commit 类型
    total_types = Counter()
    for r in all_repos:
        for k, v in r['commit_types'].items():
            total_types[k] += v

    # 合并文件统计
    total_test_files = sum(r['test_files'] for r in all_repos)
    total_doc_files = sum(r['doc_files'] for r in all_repos)
    total_file_changes = sum(r['total_file_changes'] for r in all_repos)

    # 合并低信息量 commit
    total_low_info = sum(r['low_info_commits'] for r in all_repos)

    # 合并 AI 信号
    all_ai_signals = []
    for r in all_repos:
        all_ai_signals.extend(r['ai_signals'])

    # ============================================================
    # 计算 Developer Habit Score
    # ============================================================

    # 1. 提交粒度得分 (30分)
    # 小步快跑 = 高分，大包提交 = 低分，线性插值
    avg_commits_per_day = total_commits / max(sum(r['active_days'] for r in all_repos), 1)
    granularity_score = round(min(30, avg_commits_per_day / 4.5 * 30))

    # 2. 测试意识得分 (20分)
    test_ratio = total_test_files / max(total_file_changes, 1)
    test_score = round(min(20, test_ratio / 0.15 * 20))

    # 3. 文档意识得分 (15分)
    doc_ratio = total_doc_files / max(total_file_changes, 1)
    doc_score = round(min(15, doc_ratio / 0.10 * 15))

    # 4. 作息规律得分 (20分)
    # 夜间提交 (22:00-04:00) 占比，越规律分越高
    night_commits = sum(total_hourly[h] for h in range(22, 24)) + sum(total_hourly[h] for h in range(0, 5))
    night_ratio = night_commits / max(total_commits, 1)
    schedule_score = round(min(20, max(0, (1 - night_ratio / 0.4)) * 20))

    # 5. 项目聚焦度得分 (15分)
    # Focus Index = Top 3 项目提交数 / 总提交数
    sorted_repos = sorted(all_repos, key=lambda x: x['total_commits'], reverse=True)
    top3_commits = sum(r['total_commits'] for r in sorted_repos[:3])
    focus_index = top3_commits / max(total_commits, 1)
    focus_score = round(min(15, focus_index / 0.7 * 15))

    total_score = granularity_score + test_score + doc_score + schedule_score + focus_score

    # ============================================================
    # 开发者人格系统 (DevPersona) - 6 维度光谱分类
    # ============================================================

    # 计算各维度指标
    # 1. 时间维度 (T): D=Day 白天型, N=Night 夜猫型
    #    spectrum: 0=纯白天, 100=纯夜间
    day_commits = sum(total_hourly[h] for h in range(8, 20))
    night_commits = sum(total_hourly[h] for h in range(20, 24)) + sum(total_hourly[h] for h in range(0, 6))
    time_spectrum = round(night_commits / max(day_commits + night_commits, 1) * 100)
    time_type = 'N' if time_spectrum > 50 else 'D'

    # 2. 节奏维度 (R): S=Sprint 冲刺型, M=Marathon 马拉松型
    #    spectrum: 0=极慢, 100=极速(5次/天)
    rhythm_spectrum = round(min(avg_commits_per_day / 5 * 100, 100))
    rhythm_type = 'S' if rhythm_spectrum > 50 else 'M'

    # 3. 专注维度 (F): C=Concentrated 专注型, D=Distributed 分散型
    #    spectrum: 0=极度分散, 100=极度集中
    focus_spectrum = round(focus_index * 100)
    focus_type = 'C' if focus_spectrum > 50 else 'D'

    # 4. 风格维度 (S): P=Pioneer 先锋型, G=Guardian 守护型
    #    spectrum: 0=纯维护, 100=纯新功能
    feat_ratio = total_types.get('feat', 0) / max(total_commits, 1)
    fix_ratio = total_types.get('fix', 0) / max(total_commits, 1)
    refactor_ratio = total_types.get('refactor', 0) / max(total_commits, 1)
    maintenance_ratio = (fix_ratio + refactor_ratio + total_types.get('chore', 0) / max(total_commits, 1))
    style_spectrum = round(feat_ratio / max(feat_ratio + maintenance_ratio, 0.01) * 100)
    style_type = 'P' if style_spectrum > 50 else 'G'

    # 5. 工程维度 (E): R=Rapid 快速迭代, Q=Quality 质量导向
    #    spectrum: 0=纯速度, 100=纯质量(测试+文档占比25%为满分)
    eng_spectrum = round(min((test_ratio + doc_ratio) / 0.25 * 100, 100))
    eng_type = 'Q' if eng_spectrum > 50 else 'R'

    # 6. AI 维度 (A): H=Handcraft 手工型, A=AI-assisted AI 协作型
    #    spectrum: 0=纯手工, 100=AI 辅助
    ai_detected = len(all_ai_signals) >= 3
    ai_spectrum = 100 if ai_detected else 0
    ai_type = 'A' if ai_spectrum > 50 else 'H'

    # 组合人格类型 (6位)
    persona_code = time_type + rhythm_type + focus_type + style_type + eng_type + ai_type

    # 基于主要特征生成人格名称（简化版，不穷举 64 种）
    def generate_persona_name(code):
        """根据 6 位代码生成人格名称"""
        t, r, f, s, e, a = code[0], code[1], code[2], code[3], code[4], code[5]

        # 核心类型（基于时间 + 节奏）
        core_map = {
            'DS': '晨曦冲刺者',
            'DM': '深度工匠',
            'NS': '深夜闪电侠',
            'NM': '午夜造物主',
        }
        core = core_map.get(t + r, '独特开发者')

        # 风格修饰
        style_map = {
            'P': '开拓',
            'G': '守护',
        }

        # 图标
        icon_map = {
            'DS': '🌅',
            'DM': '🔨',
            'NS': '⚡',
            'NM': '🌌',
        }
        icon = icon_map.get(t + r, '💻')

        # 描述生成（带光谱百分比）
        desc_parts = []
        desc_parts.append(f'夜间 {time_spectrum}%' if t == 'N' else f'白天 {100 - time_spectrum}%')
        desc_parts.append(f'高频提交 {rhythm_spectrum}%' if r == 'S' else f'深度专注 {100 - rhythm_spectrum}%')
        desc_parts.append(f'专注核心 {focus_spectrum}%' if f == 'C' else f'多项目并行 {100 - focus_spectrum}%')
        desc_parts.append(f'推进新功能 {style_spectrum}%' if s == 'P' else f'维护系统 {100 - style_spectrum}%')
        desc_parts.append(f'注重质量 {eng_spectrum}%' if e == 'Q' else f'快速迭代 {100 - eng_spectrum}%')
        desc_parts.append(f'善用 AI' if a == 'A' else f'纯手工开发')

        return {
            'name': core,
            'icon': icon,
            'desc': '，'.join(desc_parts[:4])  # 取前 4 个特征
        }

    persona_info = generate_persona_name(persona_code)
    persona = {
        'code': persona_code,
        'name': persona_info['name'],
        'icon': persona_info['icon'],
        'desc': persona_info['desc']
    }

    # 基础标签
    developer_tags = [
        {
            'icon': persona['icon'],
            'name': persona['name'],
            'desc': persona['desc'],
            'code': persona_code,
            'is_primary': True
        }
    ]

    # 补充标签（额外特征）
    weekend_commits = total_weekly.get(5, 0) + total_weekly.get(6, 0)
    weekend_ratio = weekend_commits / max(total_commits, 1)

    if weekend_ratio >= 0.3:
        developer_tags.append({'icon': '📅', 'name': '周末战士', 'desc': f'周末提交占比 {weekend_ratio*100:.0f}%'})

    if ai_detected:
        developer_tags.append({'icon': '🤖', 'name': 'AI 协作者', 'desc': '使用 AI 工具辅助开发'})

    if test_ratio >= 0.15:
        developer_tags.append({'icon': '✅', 'name': '测试达人', 'desc': f'测试覆盖 {test_ratio*100:.0f}%'})
    elif test_ratio < 0.05:
        developer_tags.append({'icon': '⚠️', 'name': '测试待加强', 'desc': f'测试覆盖仅 {test_ratio*100:.0f}%'})

    if doc_ratio >= 0.10:
        developer_tags.append({'icon': '📚', 'name': '文档之星', 'desc': '文档维护优秀'})
    elif doc_ratio < 0.03:
        developer_tags.append({'icon': '📝', 'name': '文档债务', 'desc': '文档投入不足'})

    if total_projects >= 10:
        developer_tags.append({'icon': '🎪', 'name': '多面手', 'desc': f'同时维护 {total_projects} 个项目'})

    if night_commits > day_commits:
        developer_tags.append({'icon': '🌙', 'name': '夜猫子', 'desc': '夜间比白天更活跃'})

    if avg_commits_per_day >= 5:
        developer_tags.append({'icon': '🏃', 'name': '暴风提交', 'desc': f'日均提交 {avg_commits_per_day:.1f} 次'})
    elif avg_commits_per_day < 0.5:
        developer_tags.append({'icon': '🦥', 'name': '佛系开发', 'desc': f'日均提交仅 {avg_commits_per_day:.1f} 次'})

    if refactor_ratio >= 0.1:
        developer_tags.append({'icon': '🔧', 'name': '重构狂魔', 'desc': f'重构占比 {refactor_ratio*100:.0f}%'})

    low_info_ratio = total_low_info / max(total_commits, 1)
    if low_info_ratio < 0.05:
        developer_tags.append({'icon': '✍️', 'name': '精确提交', 'desc': 'Commit 信息质量高'})
    elif low_info_ratio > 0.3:
        developer_tags.append({'icon': '😶', 'name': '沉默提交', 'desc': f'{low_info_ratio*100:.0f}% 的 commit 缺少描述'})

    if feat_ratio >= 0.5:
        developer_tags.append({'icon': '🚀', 'name': '功能先锋', 'desc': f'功能开发占比 {feat_ratio*100:.0f}%'})

    if weekend_ratio >= 0.3 and night_commits > day_commits:
        developer_tags.append({'icon': '💀', 'name': '爆肝战士', 'desc': '周末 + 深夜双杀'})

    # 限制标签数量
    developer_tags = developer_tags[:6]

    # ============================================================
    # 项目排行榜 + 原始 commit 数据
    # ============================================================
    project_ranking = []
    all_commits = []
    for r in sorted_repos:
        project_ranking.append({
            'name': r['name'],
            'commits': r['total_commits'],
            'language': r['main_language'],
            'active_days': r['active_days'],
            'first_commit': r['first_commit'],
            'last_commit': r['last_commit'],
            'hourly': r['hourly'],
            'monthly': r['monthly'],
            'raw_commits': r.get('commits', [])
        })
        for c in r.get('commits', []):
            all_commits.append({**c, 'project': r['name']})

    # ============================================================
    # 时间习惯分析
    # ============================================================

    # 最活跃时段
    peak_hours = sorted(range(24), key=lambda h: total_hourly[h], reverse=True)[:3]

    # 最活跃星期
    weekday_names = ['周一', '周二', '周三', '周四', '周五', '周六', '周日']
    peak_weekdays = sorted(range(7), key=lambda d: total_weekly.get(d, 0), reverse=True)[:3]

    # ============================================================
    # 构建最终数据
    # ============================================================

    analysis = {
        'generated_at': datetime.now().strftime('%Y-%m-%dT%H:%M:%SZ'),
        'scan_dir': DEFAULT_SCAN_DIR,

        # 总览
        'summary': {
            'total_projects': total_projects,
            'total_commits': total_commits,
            'total_active_days': sum(r['active_days'] for r in all_repos),
            'avg_commits_per_day': round(avg_commits_per_day, 1)
        },

        # Developer Habit Score
        'habit_score': {
            'total': total_score,
            'granularity': granularity_score,
            'test_awareness': test_score,
            'doc_awareness': doc_score,
            'schedule': schedule_score,
            'focus': focus_score
        },

        # 开发者人格类型 (DevPersona)
        'persona': {
            'code': persona_code,
            'name': persona['name'],
            'icon': persona['icon'],
            'desc': persona['desc'],
            'dimensions': {
                'time': {'code': time_type, 'spectrum': time_spectrum, 'left': '白天型', 'right': '夜猫型'},
                'rhythm': {'code': rhythm_type, 'spectrum': rhythm_spectrum, 'left': '马拉松型', 'right': '冲刺型'},
                'focus': {'code': focus_type, 'spectrum': focus_spectrum, 'left': '分散型', 'right': '专注型'},
                'style': {'code': style_type, 'spectrum': style_spectrum, 'left': '守护型', 'right': '先锋型'},
                'engineering': {'code': eng_type, 'spectrum': eng_spectrum, 'left': '快速迭代', 'right': '质量导向'},
                'ai': {'code': ai_type, 'spectrum': ai_spectrum, 'left': '手工型', 'right': 'AI 协作型'}
            }
        },

        # 开发者类型标签
        'developer_tags': developer_tags,

        # 时间分布
        'hourly': total_hourly,
        'weekly': dict(total_weekly),
        'monthly': dict(total_monthly),
        'peak_hours': peak_hours,
        'peak_weekdays': [weekday_names[d] for d in peak_weekdays],

        # 项目数据
        'projects': project_ranking,

        # Commit 类型
        'commit_types': dict(total_types),

        # 工程健康
        'engineering_health': {
            'test_ratio': round(test_ratio * 100, 1),
            'doc_ratio': round(doc_ratio * 100, 1),
            'feat_ratio': round(feat_ratio * 100, 1),
            'fix_ratio': round(fix_ratio * 100, 1),
            'refactor_ratio': round(refactor_ratio * 100, 1),
            'night_ratio': round(night_ratio * 100, 1),
            'weekend_ratio': round(weekend_ratio * 100, 1),
            'low_info_ratio': round(total_low_info / max(total_commits, 1) * 100, 1)
        },

        # AI 信号
        'ai_signals': {
            'detected': len(all_ai_signals) >= 3,
            'count': len(all_ai_signals),
            'examples': all_ai_signals[:5]
        },

        # 项目聚焦度
        'focus_index': round(focus_index * 100, 1),

        # 夜猫指数
        'night_owl_index': round(night_ratio * 100, 1),

        # 原始 commit 数据（用于前端筛选）
        'all_commits': all_commits
    }

    return analysis


# ============================================================
# 主函数
# ============================================================
def main(scan_dir=None, since=None, until=None, project=None):
    """主函数"""
    if scan_dir is None:
        scan_dir = DEFAULT_SCAN_DIR

    print(f"🔍 扫描目录: {scan_dir}")
    if since or until:
        print(f"📅 时间范围: {since or '起始'} ~ {until or '至今'}")
    if project:
        print(f"🎯 指定项目: {project}")
    print("=" * 50)

    # 1. 发现 Git 仓库
    repos = find_git_repos(scan_dir)

    # 项目筛选（模糊匹配）
    if project:
        repos = [r for r in repos if project.lower() in os.path.basename(r).lower()]
        if not repos:
            print(f"❌ 未找到匹配 '{project}' 的项目")
            return

    print(f"📁 发现 {len(repos)} 个 Git 仓库")

    if not repos:
        print("❌ 未发现任何 Git 仓库")
        return

    # 2. 收集每个仓库的数据
    all_repos = []
    for i, repo_path in enumerate(repos, 1):
        repo_name = os.path.basename(repo_path)
        print(f"[{i}/{len(repos)}] 分析: {repo_name}...", end=" ")

        data = collect_repo_data(repo_path, since=since, until=until)
        if data:
            all_repos.append(data)
            print(f"✓ ({data['total_commits']} commits)")
        else:
            print("✗ (无数据)")

    if not all_repos:
        print("❌ 未收集到任何数据")
        return

    # 3. 分析习惯
    print("\n" + "=" * 50)
    print("📊 分析开发习惯...")
    analysis = analyze_habits(all_repos)

    # 保存筛选条件到数据中
    analysis['filters'] = {
        'since': since,
        'until': until,
        'project': project,
        'scan_dir': scan_dir
    }

    # 4. 保存数据
    output_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), OUTPUT_DATA)
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(analysis, f, ensure_ascii=False, indent=2)

    print(f"\n✅ 数据已保存到: {output_path}")
    print(f"📊 总计: {analysis['summary']['total_projects']} 个项目, {analysis['summary']['total_commits']} 次提交")
    print(f"🏆 Developer Habit Score: {analysis['habit_score']['total']}/100")

    return analysis


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('scan_dir', nargs='?', default=None)
    parser.add_argument('--since', help='起始日期')
    parser.add_argument('--until', help='截止日期')
    parser.add_argument('--project', help='指定项目')
    args = parser.parse_args()
    main(scan_dir=args.scan_dir, since=args.since, until=args.until, project=args.project)
