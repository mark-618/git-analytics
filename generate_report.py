#!/usr/bin/env python3
"""
Git Analytics - 个人代码习惯体检报告生成器
使用 Chart.js 生成可视化报告，支持交互式筛选
"""

import json
import os

OUTPUT_FILE = "report.html"


def load_data(data_path="data.json"):
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_score_color(score):
    if score >= 80: return '#1a7f37'
    elif score >= 60: return '#bf8700'
    else: return '#cf222e'


def get_score_label(score):
    if score >= 80: return '优秀'
    elif score >= 60: return '良好'
    elif score >= 40: return '一般'
    else: return '需改进'


# ============================================================
# CSS 样式（独立字符串，无 f-string 转义问题）
# ============================================================
CSS = """
* { margin: 0; padding: 0; box-sizing: border-box; }
body {
    font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', system-ui, sans-serif;
    background: #f6f8fa; color: #1f2328; line-height: 1.6; padding: 40px 20px;
}
.container { max-width: 1100px; margin: 0 auto; }
.header { text-align: center; margin-bottom: 32px; }
.header h1 { font-size: 2.4em; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 8px; color: #1f2328; }
.header p { color: #656d76; font-size: 1.1em; }
.stats-row { display: grid; grid-template-columns: repeat(4, 1fr); gap: 16px; margin-bottom: 40px; }
.stat-card { background: #fff; border-radius: 6px; padding: 24px; text-align: center; border: 1px solid #d0d7de; }
.stat-number { font-size: 2.4em; font-weight: 700; color: #0969da; }
.stat-label { color: #656d76; font-size: 0.85em; margin-top: 4px; }
.section { margin-bottom: 40px; }
.section-title {
    font-size: 1.4em; font-weight: 600; margin-bottom: 16px; color: #1f2328;
    display: flex; align-items: center; gap: 8px;
    padding-bottom: 8px; border-bottom: 1px solid #d8dee4;
}
.card { background: #fff; border-radius: 6px; padding: 24px; border: 1px solid #d0d7de; margin-bottom: 16px; }
.card h3 { font-size: 1em; font-weight: 600; margin-bottom: 16px; color: #1f2328; }
.chart-container { position: relative; height: 300px; }
.insight-card {
    background: #f6f8fa; border-left: 3px solid #0969da;
    border-radius: 0 6px 6px 0; padding: 14px 16px; margin: 16px 0 0;
    font-size: 0.9em; color: #656d76;
}
.insight-card strong { color: #0969da; }
.footer { text-align: center; margin-top: 48px; padding: 24px; color: #656d76; font-size: 0.8em; border-top: 1px solid #d8dee4; }
.two-cols { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.filter-bar {
    background: #fff; border: 1px solid #d0d7de; border-radius: 6px;
    padding: 16px 20px; margin-bottom: 32px;
    display: flex; align-items: center; gap: 16px; flex-wrap: wrap;
}
.filter-bar label { font-size: 0.85em; color: #656d76; font-weight: 600; }
.filter-bar select, .filter-bar input {
    padding: 6px 10px; border: 1px solid #d0d7de; border-radius: 6px;
    font-size: 0.9em; background: #fff; color: #1f2328;
}
.filter-bar select:focus, .filter-bar input:focus { outline: none; border-color: #0969da; }
.filter-bar button {
    padding: 6px 16px; background: #0969da; color: #fff; border: none;
    border-radius: 6px; font-size: 0.9em; cursor: pointer; font-weight: 600;
}
.filter-bar button:hover { background: #0550ae; }
.filter-bar .reset-btn { background: #fff; color: #656d76; border: 1px solid #d0d7de; }
.filter-bar .reset-btn:hover { background: #f6f8fa; }

/* 维度光谱 */
.dim-item { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 12px; }
.dim-head { display: flex; align-items: center; justify-content: space-between; gap: 8px; margin-bottom: 8px; }
.dim-name { font-size: 0.74em; color: #656d76; font-weight: 600; }
.dim-codepair { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 0.78em; color: #656d76; }
.dim-active { display: flex; align-items: baseline; gap: 8px; margin-bottom: 8px; }
.dim-active-code { font-family: ui-monospace, SFMono-Regular, Menlo, monospace; font-size: 1.65em; font-weight: 800; color: #0969da; line-height: 1; }
.dim-active-name { font-size: 0.95em; font-weight: 700; color: #1f2328; }
.dim-row { display: flex; align-items: center; gap: 8px; }
.dim-label { font-size: 0.72em; min-width: 58px; color: #656d76; }
.dim-label.active { color: #1f2328; font-weight: 700; }
.dim-bar { flex: 1; height: 6px; background: #d8dee4; border-radius: 3px; position: relative; }
.dim-bar-fill { position: absolute; left: 0; top: 0; height: 100%; background: #0969da; border-radius: 3px; }
.dim-pct { font-size: 0.72em; color: #656d76; margin-top: 5px; }
.dim-desc { font-size: 0.72em; color: #656d76; margin-top: 6px; line-height: 1.4; }

/* 分数维度条 */
.score-dim-row { display: flex; align-items: center; gap: 12px; margin-bottom: 12px; }
.score-dim-name { width: 70px; font-size: 0.85em; color: #656d76; }
.score-dim-bar { flex: 1; height: 8px; background: #d8dee4; border-radius: 4px; overflow: hidden; }
.score-dim-bar-fill { height: 100%; border-radius: 4px; }
.score-dim-val { width: 80px; font-size: 0.85em; color: #1f2328; text-align: right; }
.score-dim-pct { color: #656d76; font-size: 0.8em; }

/* 标签 */
.tag-item { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 14px; text-align: center; }
.tag-icon { font-size: 1.5em; margin-bottom: 4px; }
.tag-name { font-weight: 600; font-size: 0.85em; margin-bottom: 2px; }
.tag-desc { font-size: 0.7em; color: #656d76; }

/* 工程健康 */
.eng-health-grid { display: grid; grid-template-columns: repeat(2, 1fr); gap: 16px; }
.eng-item { text-align: center; padding: 20px 12px; background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; }
.eng-val { font-size: 2em; font-weight: 700; }
.eng-label { font-size: 0.85em; font-weight: 600; color: #1f2328; margin-top: 4px; }
.eng-desc { font-size: 0.72em; color: #656d76; margin-top: 2px; }

/* 提交类型条 */
.type-bar-row { display: flex; align-items: center; gap: 12px; margin-bottom: 10px; }
.type-bar-name { width: 70px; font-size: 0.85em; color: #656d76; }
.type-bar-track { flex: 1; height: 8px; background: #d8dee4; border-radius: 4px; overflow: hidden; }
.type-bar-fill { height: 100%; border-radius: 4px; }
.type-bar-val { width: 90px; font-size: 0.85em; color: #1f2328; text-align: right; }

/* 项目排行榜 */
.rank-row { display: flex; align-items: center; gap: 14px; padding: 12px 0; }
.rank-row + .rank-row { border-top: 1px solid #d8dee4; }
.rank-num { width: 24px; height: 24px; background: #0969da; color: #fff; border-radius: 4px; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 0.8em; }
.rank-info { flex: 1; }
.rank-name { font-weight: 600; font-size: 0.95em; }
.rank-meta { display: flex; gap: 10px; font-size: 0.75em; color: #656d76; margin-top: 2px; }
.rank-commits { font-size: 1em; font-weight: 700; color: #0969da; }

/* 建议 */
.sug-tabs { display: flex; gap: 8px; margin-bottom: 16px; flex-wrap: wrap; }
.sug-tab { padding: 8px 16px; border: 1px solid #d0d7de; border-radius: 20px; background: #f6f8fa; color: #656d76; font-size: 0.85em; cursor: pointer; transition: all 0.2s; }
.sug-tab:hover { background: #eaeef2; color: #1f2328; }
.sug-tab.active { background: #0969da; color: #fff; border-color: #0969da; }
.sug-panel { display: none; }
.sug-panel.active { display: block; }
.sug-item { display: flex; gap: 12px; margin-bottom: 10px; padding: 12px 14px; background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; }
.sug-num { width: 20px; height: 20px; background: #1a7f37; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7em; font-weight: 700; flex-shrink: 0; }
.sug-text { font-size: 0.9em; color: #1f2328; }

/* AI Impact */
.ai-visual-grid { display: grid; grid-template-columns: minmax(240px, 0.85fr) minmax(280px, 1.15fr); gap: 16px; margin-top: 16px; }
.ai-score-box, .ai-chart-box { background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; padding: 16px; }
.ai-box-title { font-weight: 600; margin-bottom: 10px; color: #1f2328; }
.ai-score-track { height: 12px; display: flex; background: #d8dee4; border-radius: 999px; overflow: hidden; margin: 12px 0 10px; }
.ai-score-explicit { background: #0969da; }
.ai-score-tooling { background: #8250df; }
.ai-score-row { display: flex; justify-content: space-between; gap: 12px; font-size: 0.82em; color: #656d76; margin-top: 6px; }
.ai-score-row strong { color: #1f2328; }
.ai-trend-wrap { position: relative; height: 220px; }
.ai-trend-empty { display: none; align-items: center; justify-content: center; height: 100%; color: #656d76; font-size: 0.9em; }

@media (max-width: 768px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .two-cols { grid-template-columns: 1fr; }
    .header h1 { font-size: 1.8em; }
    .filter-bar { flex-direction: column; align-items: stretch; }
    .eng-health-grid { grid-template-columns: 1fr; }
    .ai-visual-grid { grid-template-columns: 1fr; }
}
"""


def generate_report(data):
    summary = data['summary']
    habit_score = data['habit_score']
    persona = data.get('persona', {})
    tags = data['developer_tags']
    hourly = data['hourly']
    weekly = data['weekly']
    monthly = data['monthly']
    projects = data['projects']
    commit_types = data['commit_types']
    health = data['engineering_health']
    ai = data['ai_signals']
    peak_hours = data['peak_hours']
    peak_weekdays = data['peak_weekdays']
    all_commits = data.get('all_commits', [])

    project_names = [p['name'] for p in projects]
    project_meta = {
        p['name']: {
            'language': p.get('language', 'Unknown'),
            'active_days': p.get('active_days', 0)
        }
        for p in projects
    }
    for c in all_commits:
        meta = project_meta.get(c.get('project'), {})
        c.setdefault('language', meta.get('language', 'Unknown'))

    # 月度数据
    monthly_sorted = sorted(monthly.items())
    month_labels = [m[0] for m in monthly_sorted]

    # 月份显示标签（跨年时带年份）
    years = set(m[:4] for m in month_labels)
    multi_year = len(years) > 1
    def fmt_month(m):
        return f'{m[:4]}年{m[5:]}月' if multi_year else f'{m[5:]}月'
    month_display = [fmt_month(m) for m in month_labels]

    # 项目堆叠数据（Top 7）
    top_projects = [p for p in projects if p['commits'] >= 10][:7]
    colors = ['#0969da', '#8250df', '#bf3989', '#cf222e', '#1a7f37', '#bf8700', '#0550ae', '#6e7781']

    stack_datasets = []
    for i, proj in enumerate(top_projects):
        proj_monthly = proj.get('monthly', {})
        proj_data = [proj_monthly.get(m, 0) for m in month_labels]
        stack_datasets.append({
            'label': proj['name'],
            'data': proj_data,
            'backgroundColor': colors[i % len(colors)]
        })

    other_projects = [p for p in projects if p['commits'] < 10]
    if other_projects:
        other_data = [0] * len(month_labels)
        for p in other_projects:
            for j, m in enumerate(month_labels):
                other_data[j] += p.get('monthly', {}).get(m, 0)
        if any(v > 0 for v in other_data):
            stack_datasets.append({'label': '其他', 'data': other_data, 'backgroundColor': '#9ca3af'})

    # 气泡图数据（月份标签作为 x，分类轴）
    bubble_datasets = []
    for i, proj in enumerate(projects):
        if proj['commits'] < 5:
            continue
        points = []
        for m, label in zip(month_labels, month_display):
            count = proj.get('monthly', {}).get(m, 0)
            if count > 0:
                points.append({'x': label, 'y': count, 'r': min(max(count ** 0.5 * 2.5, 4), 30)})
        if points:
            bubble_datasets.append({
                'label': proj['name'],
                'data': points,
                'backgroundColor': f'{colors[i % len(colors)]}b3'
            })

    # Commit 类型
    type_labels = ['feat', 'fix', 'docs', 'test', 'refactor', 'chore', 'other']
    type_names = ['功能开发', 'Bug 修复', '文档', '测试', '重构', '构建/CI', '其他']
    type_colors = ['#0969da', '#cf222e', '#1a7f37', '#bf8700', '#8250df', '#6e7781', '#afb8c1']
    type_values = [commit_types.get(t, 0) for t in type_labels]

    # 语言分布
    lang_counter = {}
    for p in projects:
        lang = p.get('language', 'Unknown')
        lang_counter[lang] = lang_counter.get(lang, 0) + 1
    lang_labels = list(lang_counter.keys())
    lang_values = list(lang_counter.values())

    # Top3 聚焦度
    top3_commits = sum(p['commits'] for p in projects[:3])
    top3_ratio = top3_commits / max(summary['total_commits'], 1) * 100

    # 维度
    dims = persona.get('dimensions', {})
    dim_keys = ['time', 'rhythm', 'focus', 'style', 'engineering', 'ai']
    dim_names = {'time': '时间偏好', 'rhythm': '节奏风格', 'focus': '专注程度',
                 'style': '开发风格', 'engineering': '工程取向', 'ai': 'AI 协作'}

    # ============================================================
    # 构建 HTML 片段（Python 变量，避免在 f-string 中拼接）
    # ============================================================

    # 统计卡片
    stats_html = f'''
    <div class="stats-row">
        <div class="stat-card"><div class="stat-number" id="statScore">{habit_score['total']}</div><div class="stat-label">习惯健康分</div></div>
        <div class="stat-card"><div class="stat-number" id="statProjects">{summary['total_projects']}</div><div class="stat-label">项目总数</div></div>
        <div class="stat-card"><div class="stat-number" id="statCommits">{summary['total_commits']}</div><div class="stat-label">总提交数</div></div>
        <div class="stat-card"><div class="stat-number" id="statDaily">{summary['avg_commits_per_day']}</div><div class="stat-label">日均提交</div></div>
    </div>'''

    # 开发者人格
    persona_html = f'''
    <div class="card">
        <h3>你的开发者人格</h3>
        <div style="display:flex;align-items:center;gap:40px;padding:10px 0;">
            <div style="text-align:center;" id="personaCard">
                <div style="font-size:3em;margin-bottom:8px;">{persona.get('icon', '❓')}</div>
                <div style="font-size:1.6em;font-weight:700;color:#1f2328;">{persona.get('name', '未知')}</div>
                <div style="font-size:1.1em;color:#0969da;font-weight:600;margin-top:4px;font-family:monospace;">{persona.get('code', '????')}</div>
                <div style="color:#1f2328;font-size:0.95em;margin-top:8px;font-weight:500;">{persona.get('desc', '')}</div>
                <div style="color:#656d76;font-size:0.85em;margin-top:4px;">{persona.get('detail', '')}</div>
            </div>
            <div style="flex:1;">
                <div style="display:grid;grid-template-columns:repeat(3,1fr);gap:12px;" id="dimsDetail">{_build_dims_html(dims, dim_keys, dim_names)}</div>
            </div>
        </div>
    </div>'''

    # Habit Score
    score_dims = [
        ('提交粒度', habit_score['granularity'], 30),
        ('测试意识', habit_score['test_awareness'], 20),
        ('文档意识', habit_score['doc_awareness'], 15),
        ('作息规律', habit_score['schedule'], 20),
        ('项目聚焦', habit_score['focus'], 15),
    ]
    score_html = f'''
    <div class="card">
        <h3>Developer Habit Score</h3>
        <div style="display:flex;align-items:center;gap:30px;">
            <div style="text-align:center;" id="scoreCircle">
                <div style="font-size:4em;font-weight:700;color:{get_score_color(habit_score['total'])};line-height:1;" id="scoreNumber">{habit_score['total']}</div>
                <div style="color:#656d76;font-size:0.9em;margin-top:4px;" id="scoreLabel">/ 100 · {get_score_label(habit_score['total'])}</div>
            </div>
            <div style="flex:1;" id="scoreDims">{_build_score_dims_html(score_dims)}</div>
        </div>
    </div>'''

    # 标签
    tags_html = f'''
    <div class="card">
        <h3>特征标签</h3>
        <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;" id="tagsGrid">{_build_tags_html(tags)}</div>
    </div>'''

    # 24小时
    hour_chart_html = f'''
    <div class="card">
        <h3>24 小时提交分布</h3>
        <div class="chart-container"><canvas id="hourChart"></canvas></div>
        <div class="insight-card" id="insightHour">
            <strong>洞察：</strong>最活跃时段 {', '.join([f'{h}:00' for h in peak_hours])}。
            {'夜间提交占比 ' + str(health['night_ratio']) + '%，属于夜间爆发型。' if health['night_ratio'] > 25 else '作息相对规律。'}
        </div>
    </div>'''

    # 星期
    week_chart_html = f'''
    <div class="card">
        <h3>星期提交分布</h3>
        <div class="chart-container" style="height:260px;"><canvas id="weekChart"></canvas></div>
        <div class="insight-card" id="insightWeek">
            <strong>洞察：</strong>最活跃 {', '.join(peak_weekdays)}。
            {'周末提交占比 ' + str(health['weekend_ratio']) + '%。' if health['weekend_ratio'] > 20 else '以工作日为主。'}
        </div>
    </div>'''

    # 每月项目投入
    monthly_chart_html = f'''
    <div class="card">
        <h3>每月项目投入</h3>
        <div class="chart-container" style="height:380px;"><canvas id="monthlyChart"></canvas></div>
        <div class="insight-card" id="insightMonthly">
            <strong>洞察：</strong>Top 3 项目占据 {top3_ratio:.0f}% 的提交。
            {'专注度高。' if top3_ratio > 60 else '精力较分散。'}
        </div>
    </div>'''

    # 气泡图
    bubble_chart_html = '''
    <div class="card">
        <h3>项目时间线</h3>
        <div class="chart-container" style="height:350px;"><canvas id="bubbleChart"></canvas></div>
    </div>'''

    # 项目排行榜
    projects_html = _build_projects_html(projects)
    projects_ranking_html = f'''
    <div class="card">
        <h3>项目排行榜</h3>
        <div id="projectsRanking">{projects_html}</div>
    </div>'''

    # Commit 类型
    type_chart_html = '''
    <div class="card">
        <h3>Commit 类型分布</h3>
        <div class="chart-container"><canvas id="typeChart"></canvas></div>
    </div>'''

    lang_chart_html = '''
    <div class="card">
        <h3>语言分布</h3>
        <div class="chart-container"><canvas id="langChart"></canvas></div>
    </div>'''

    # 提交类型详情
    type_detail_html = f'''
    <div class="card">
        <h3>提交类型详情</h3>
        <div id="typeBars"></div>
        <div class="insight-card" id="insightTypes">
            <strong>洞察：</strong>
            功能开发占比 {health['feat_ratio']}%，测试 {health['test_ratio']}%，文档 {health['doc_ratio']}%。
            {'测试投入偏低。' if health['test_ratio'] < 5 else ''}
            {'低信息量 commit 占比 ' + str(health['low_info_ratio']) + '%。' if health['low_info_ratio'] > 15 else ''}
        </div>
    </div>'''

    # 工程健康
    eng_health_html = _build_eng_health_html(health)
    eng_insight_html = _build_eng_insight(health)

    eng_section_html = f'''
    <div class="card">
        <div class="eng-health-grid" id="engHealthGrid">{eng_health_html}</div>
    </div>
    <div class="insight-card" id="insightEng"><strong>洞察：</strong>{eng_insight_html}</div>'''

    # AI
    if ai['detected']:
        # 构建工具分布 HTML
        tools_html = ''
        if ai.get('tools'):
            tool_items = []
            for tool, count in ai['tools'].items():
                tool_items.append(f'<span style="background:#e8f5e9;padding:4px 10px;border-radius:12px;font-size:0.85em;">{tool}: {count}</span>')
            tools_html = f'''<div style="margin-top:12px;display:flex;gap:8px;justify-content:center;flex-wrap:wrap;">
                {''.join(tool_items)}
            </div>'''

        # 生成 AI 洞察文字
        ai_insight_parts = []
        if ai['ai_commit_ratio'] >= 30:
            ai_insight_parts.append(f'AI 使用率 {ai["ai_commit_ratio"]}%，你是 AI 协作开发的重度用户。')
        elif ai['ai_commit_ratio'] >= 10:
            ai_insight_parts.append(f'AI 使用率 {ai["ai_commit_ratio"]}%，AI 已成为你的开发助手。')
        else:
            ai_insight_parts.append(f'AI 使用率 {ai["ai_commit_ratio"]}%，你主要依靠手工编码。')

        if ai.get('tools'):
            top_tool = max(ai['tools'], key=ai['tools'].get)
            ai_insight_parts.append(f'最常用工具: {top_tool}。')

        ai_insight_html = ' '.join(ai_insight_parts)

        ai_html = f'''
        <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:16px;">
            <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:20px;text-align:center;">
                <div style="font-size:2em;margin-bottom:4px;">🤖</div>
                <div style="font-size:1.8em;font-weight:700;color:#1f2328;">{ai['ai_commit_ratio']}%</div>
                <div style="color:#656d76;font-size:0.85em;">AI 明确信号率</div>
            </div>
            <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:20px;text-align:center;">
                <div style="font-size:2em;margin-bottom:4px;">📊</div>
                <div style="font-size:1.8em;font-weight:700;color:#1f2328;">{ai['ai_commit_count']}</div>
                <div style="color:#656d76;font-size:0.85em;">AI 明确信号提交</div>
            </div>
            <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:20px;text-align:center;">
                <div style="font-size:2em;margin-bottom:4px;">🔧</div>
                <div style="font-size:1.8em;font-weight:700;color:#1f2328;">{ai.get('ai_influence_score', 0)}</div>
                <div style="color:#656d76;font-size:0.85em;">AI 影响分</div>
            </div>
        </div>
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:16px;">
            <div style="font-weight:600;margin-bottom:8px;">使用的 AI 工具</div>
            {tools_html if tools_html else '<div style="color:#656d76;">无详细工具信息</div>'}
        </div>
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:16px;margin-top:12px;">
            <div style="font-weight:600;margin-bottom:8px;">AI 使用趋势</div>
            <canvas id="aiTrendChart" height="200"></canvas>
        </div>
        <div class="insight-card"><strong>洞察：</strong>{ai_insight_html}</div>'''
    else:
        ai_html = '''
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:24px;text-align:center;">
            <div style="color:#656d76;">未检测到明显的 AI 辅助开发痕迹</div>
        </div>'''
        ai_insight_html = '你目前主要依靠手工编码，没有检测到 AI 辅助开发的痕迹。'

    # 建议
    sug_html = _build_suggestions_html(habit_score, health, data)

    # ============================================================
    # 嵌入的 JSON 数据
    # ============================================================
    all_commits_json = json.dumps(all_commits, ensure_ascii=False)
    project_names_json = json.dumps(project_names, ensure_ascii=False)
    project_meta_json = json.dumps(project_meta, ensure_ascii=False)
    month_labels_json = json.dumps(month_labels)
    type_labels_json = json.dumps(type_labels)
    type_names_json = json.dumps(type_names)
    type_colors_json = json.dumps(type_colors)
    colors_json = json.dumps(colors)
    lang_labels_json = json.dumps(lang_labels)
    lang_values_json = json.dumps(lang_values)

    # Python 常量（JS 无法重算）
    eng_spectrum = dims.get('engineering', {}).get('spectrum', 50)
    ai_spectrum = dims.get('ai', {}).get('spectrum', 0)
    test_ratio = health['test_ratio']
    doc_ratio = health['doc_ratio']
    ai_detected = 'true' if ai['detected'] else 'false'
    ai_count = ai['count']
    low_info_ratio = health['low_info_ratio']

    # AI 月度趋势数据
    monthly_ai = ai.get('monthly_ai', {})
    monthly_ai_json = json.dumps(monthly_ai)

    # ============================================================
    # JS 脚本（独立字符串，无 f-string 转义问题）
    # ============================================================
    js = _build_js(
        all_commits_json, project_names_json, project_meta_json,
        month_labels_json, type_labels_json, type_names_json, type_colors_json,
        colors_json, lang_labels_json, lang_values_json,
        eng_spectrum, ai_spectrum, test_ratio, doc_ratio,
        ai_detected, ai_count, low_info_ratio,
        json.dumps(hourly),
        json.dumps([weekly.get(str(i), 0) for i in range(7)]),
        json.dumps(type_values),
        json.dumps(stack_datasets),
        json.dumps(bubble_datasets),
        json.dumps(month_display),
        'true' if multi_year else 'false',
        monthly_ai_json,
    )

    # ============================================================
    # 组装完整 HTML
    # ============================================================
    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git Analytics - 代码习惯体检报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>{CSS}</style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>代码习惯体检报告</h1>
            <p id="headerSubtitle">{summary['total_projects']} 个项目 · {summary['total_commits']} 次提交 · {summary['total_active_days']} 天活跃</p>
        </div>

        <div class="filter-bar">
            <label>项目</label>
            <select id="filterProject"><option value="all">全部项目</option></select>
            <label>时间</label>
            <select id="filterRange" onchange="applyPresetRange()">
                <option value="all">全部时间</option>
                <option value="1m">近一个月</option>
                <option value="6m">近半年</option>
                <option value="1y">近一年</option>
                <option value="custom">自定义</option>
            </select>
            <label>从</label>
            <input type="date" id="filterSince" onchange="markCustomRange()">
            <label>至</label>
            <input type="date" id="filterUntil" onchange="markCustomRange()">
            <button onclick="applyFilters()">筛选</button>
            <button class="reset-btn" onclick="resetFilters()">重置</button>
        </div>

        {stats_html}

        <!-- 总览 -->
        <div class="section">
            <div class="section-title">📊 总览</div>
            {persona_html}
            <div class="two-cols">{score_html}{tags_html}</div>
        </div>

        <!-- 时间习惯 -->
        <div class="section">
            <div class="section-title">⏰ 时间习惯</div>
            {hour_chart_html}
            {week_chart_html}
        </div>

        <!-- 项目投入 -->
        <div class="section">
            <div class="section-title">🎯 项目投入</div>
            {monthly_chart_html}
            {bubble_chart_html}
            {projects_ranking_html}
        </div>

        <!-- 提交习惯 -->
        <div class="section">
            <div class="section-title">📝 提交习惯</div>
            <div class="two-cols">{type_chart_html}{lang_chart_html}</div>
            {type_detail_html}
        </div>

        <!-- 工程健康 -->
        <div class="section">
            <div class="section-title">🏥 工程健康</div>
            {eng_section_html}
        </div>

        <!-- AI Impact -->
        <div class="section">
            <div class="section-title">🤖 AI Coding Impact</div>
            <div class="card" id="aiImpact">{ai_html}</div>
        </div>

        <!-- 建议 -->
        <div class="section">
            <div class="section-title">💡 改进建议</div>
            <div class="card" id="suggestions">{sug_html}</div>
        </div>

        <div class="footer">
            <p>生成时间: {data['generated_at']}</p>
            <p style="margin-top:6px;">Git Analytics - 本地优先的个人代码习惯分析工具</p>
        </div>
    </div>

    <script>{js}</script>
</body>
</html>'''

    return html


# ============================================================
# HTML 片段构建函数（纯 Python，无 f-string 嵌套问题）
# ============================================================

def _build_dims_html(dims, dim_keys, dim_names):
    dim_meta = {
        'time': {'left_code': 'D', 'right_code': 'N', 'left_trait': '日间掌控者', 'right_trait': '夜间爆发者',
                 'left_desc': '白天更容易进入状态，节奏清晰。', 'right_desc': '安静时段更容易输出，灵感来得晚。'},
        'rhythm': {'left_code': 'M', 'right_code': 'S', 'left_trait': '长线推进者', 'right_trait': '冲刺迭代者',
                   'left_desc': '偏稳定推进，提交更像长跑。', 'right_desc': '偏高频推进，短时间爆发强。'},
        'focus': {'left_code': 'D', 'right_code': 'C', 'left_trait': '多线调度者', 'right_trait': '核心深挖者',
                  'left_desc': '能在多个项目间切换上下文。', 'right_desc': '精力更集中在核心项目。'},
        'style': {'left_code': 'G', 'right_code': 'P', 'left_trait': '系统守护者', 'right_trait': '功能开拓者',
                  'left_desc': '更常维护、修复和打磨系统。', 'right_desc': '更常推进新功能和新想法。'},
        'engineering': {'left_code': 'R', 'right_code': 'Q', 'left_trait': '快速试错派', 'right_trait': '质量洁癖派',
                        'left_desc': '偏速度和反馈，先跑起来。', 'right_desc': '偏测试、文档和工程质量。'},
        'ai': {'left_code': 'H', 'right_code': 'A', 'left_trait': '手作掌控派', 'right_trait': 'AI 搭子派',
               'left_desc': '主要靠自己手工推进。', 'right_desc': '会把 AI 当成结对伙伴。'},
    }
    html = ""
    for dim_key in dim_keys:
        dim = dims.get(dim_key, {})
        meta = dim_meta.get(dim_key, {})
        spectrum = dim.get('spectrum', 50)
        left_label = dim.get('left', '')
        right_label = dim.get('right', '')
        dim_name = dim_names[dim_key]
        left_code = meta.get('left_code', '')
        right_code = meta.get('right_code', '')
        active_code = dim.get('code') or (right_code if spectrum > 50 else left_code)
        is_right = active_code == right_code
        pct = spectrum if is_right else (100 - spectrum)
        active_trait = meta.get('right_trait' if is_right else 'left_trait', right_label if is_right else left_label)
        active_desc = meta.get('right_desc' if is_right else 'left_desc', '')
        align = 'right' if is_right else 'left'
        left_active = ' active' if not is_right else ''
        right_active = ' active' if is_right else ''
        html += f'''
        <div class="dim-item">
            <div class="dim-head">
                <div class="dim-name">{dim_name}</div>
                <div class="dim-codepair">{left_code}/{right_code}</div>
            </div>
            <div class="dim-active">
                <span class="dim-active-code">{active_code}</span>
                <span class="dim-active-name">{active_trait}</span>
            </div>
            <div class="dim-row">
                <span class="dim-label{left_active}" style="text-align:right;">{left_label}</span>
                <div class="dim-bar"><div class="dim-bar-fill" style="width:{spectrum}%;"></div></div>
                <span class="dim-label{right_active}">{right_label}</span>
            </div>
            <div class="dim-pct" style="text-align:{align};">倾向 {pct}%</div>
            <div class="dim-desc">{active_desc}</div>
        </div>'''
    return html


def _build_score_dims_html(score_dims):
    html = ""
    for name, score, max_score in score_dims:
        pct = score / max_score * 100
        color = get_score_color(pct)
        html += f'''
        <div class="score-dim-row">
            <div class="score-dim-name">{name}</div>
            <div class="score-dim-bar"><div class="score-dim-bar-fill" style="width:{pct}%;background:{color};"></div></div>
            <div class="score-dim-val">{score}/{max_score} <span class="score-dim-pct">({pct:.0f}%)</span></div>
        </div>'''
    return html


def _build_tags_html(tags):
    html = ""
    for tag in tags[1:]:
        html += f'''
        <div class="tag-item">
            <div class="tag-icon">{tag['icon']}</div>
            <div class="tag-name">{tag['name']}</div>
            <div class="tag-desc">{tag['desc']}</div>
        </div>'''
    return html


def _build_projects_html(projects):
    html = ""
    for i, p in enumerate(projects[:8], 1):
        html += f'''
        <div class="rank-row">
            <div class="rank-num">{i}</div>
            <div class="rank-info">
                <div class="rank-name">{p['name']}</div>
                <div class="rank-meta"><span>{p['language']}</span><span>{p['active_days']} 天活跃</span></div>
            </div>
            <div class="rank-commits">{p['commits']}</div>
        </div>'''
    return html


def _build_eng_health_html(health):
    items = [
        ('测试覆盖', '改代码时有改测试吗', health['test_ratio'], '#1a7f37' if health['test_ratio'] >= 10 else '#cf222e'),
        ('文档覆盖', '改代码时有更新文档吗', health['doc_ratio'], '#1a7f37' if health['doc_ratio'] >= 5 else '#bf8700'),
        ('功能开发', '写新功能的时间占比', health['feat_ratio'], '#0969da'),
        ('Bug 修复', '修 bug 的时间占比', health['fix_ratio'], '#cf222e'),
        ('重构', '优化老代码的时间占比', health['refactor_ratio'], '#8250df'),
        ('夜间提交', '深夜写的代码占比', health['night_ratio'], '#bf8700' if health['night_ratio'] > 25 else '#656d76'),
        ('周末提交', '周末写的代码占比', health['weekend_ratio'], '#8250df' if health['weekend_ratio'] > 25 else '#656d76'),
        ('低信息量', 'commit 信息够详细吗', health['low_info_ratio'], '#cf222e' if health['low_info_ratio'] > 20 else '#1a7f37'),
    ]
    html = ""
    for label, desc, val, color in items:
        html += f'''
        <div class="eng-item">
            <div class="eng-val" style="color:{color};">{val}%</div>
            <div class="eng-label">{label}</div>
            <div class="eng-desc">{desc}</div>
        </div>'''
    return html


def _build_eng_insight(health):
    parts = []
    if health['test_ratio'] < 5:
        parts.append('很少写测试，建议为新功能补充测试用例。')
    elif health['test_ratio'] >= 10:
        parts.append('测试习惯不错。')
    if health['doc_ratio'] < 3:
        parts.append('文档更新较少，建议定期维护 README。')
    if health['night_ratio'] > 30:
        parts.append('深夜写代码比例较高，注意休息。')
    if health['low_info_ratio'] > 15:
        parts.append('有些 commit 描述太简略，不利于后期回溯。')
    return ' '.join(parts) if parts else '各项指标正常。'


def _build_suggestions_html(habit_score, health, data):
    # 分类建议结构
    categories = {
        'commit': {'name': '提交习惯', 'icon': '📝', 'items': []},
        'test': {'name': '测试质量', 'icon': '✅', 'items': []},
        'doc': {'name': '文档维护', 'icon': '📚', 'items': []},
        'schedule': {'name': '作息健康', 'icon': '⏰', 'items': []},
        'project': {'name': '项目管理', 'icon': '🎯', 'items': []},
        'ai': {'name': 'AI 协作', 'icon': '🤖', 'items': []},
    }

    summary = data.get('summary', {})
    ai = data.get('ai_signals', {})
    avg_daily = summary.get('avg_commits_per_day', 0)
    hourly = data.get('hourly', [])
    weekly = data.get('weekly', {})
    peak_hours = data.get('peak_hours', [])
    commit_types = data.get('commit_types', {})
    total_commits = summary.get('total_commits', 0)
    total_active_days = summary.get('total_active_days', 0)
    total_projects = summary.get('total_projects', 0)
    projects = data.get('projects', [])

    # ============================================================
    # 提交习惯 (最多 6 条)
    # ============================================================
    if habit_score['granularity'] < 15:
        categories['commit']['items'].append("优化提交粒度：粒度得分仅 {}/40，建议保持稳定的提交频率".format(habit_score['granularity']))
    if avg_daily < 1:
        categories['commit']['items'].append("提高提交频率：日均仅 {:.1f} 次提交，建议小步快跑、勤提交".format(avg_daily))
    elif avg_daily > 8:
        categories['commit']['items'].append("优化提交粒度：日均 {:.1f} 次提交偏多，考虑合并相关改动".format(avg_daily))
    if health['low_info_ratio'] > 15:
        categories['commit']['items'].append("优化 Commit Message：{:.0f}% 的提交缺少描述，建议使用 Conventional Commits 规范".format(health['low_info_ratio']))
    elif health['low_info_ratio'] > 5:
        categories['commit']['items'].append("完善提交描述：部分 commit 信息过于简略，建议写清楚改动原因")
    if total_commits > 0:
        other_c = commit_types.get('other', 0)
        other_pct = other_c / total_commits * 100
        if other_pct > 30:
            categories['commit']['items'].append("提交分类不清：{:.0f}% 归为 other，建议使用 feat/fix/refactor 等标准类型".format(other_pct))
    if total_active_days > 0 and total_commits > 0:
        commits_per_active_day = total_commits / total_active_days
        if commits_per_active_day > 10:
            categories['commit']['items'].append("控制单日提交量：活跃日均提交 {:.0f} 次，建议拆分为更小的改动".format(commits_per_active_day))

    # 正面反馈
    if health['low_info_ratio'] < 3:
        categories['commit']['items'].append("Commit 质量高：{:.0f}% 的提交有详细描述，继续保持！".format(100 - health['low_info_ratio']))
    if avg_daily >= 2 and avg_daily <= 5:
        categories['commit']['items'].append("提交频率适中：日均 {:.1f} 次提交，节奏良好".format(avg_daily))

    # ============================================================
    # 测试质量 (最多 5 条)
    # ============================================================
    if habit_score['test_awareness'] < 10:
        categories['test']['items'].append("提高测试意识：尝试为每个新功能编写测试用例，目标覆盖率 10%+")
    elif health['test_ratio'] < 8:
        categories['test']['items'].append("增加测试投入：当前测试文件占比仅 {:.0f}%，建议补充单元测试".format(health['test_ratio']))
    if total_commits > 0:
        test_count = commit_types.get('test', 0)
        if test_count / total_commits < 0.05 and total_commits > 50:
            categories['test']['items'].append("增加测试提交：测试相关提交仅占 {:.0f}%，建议为新功能编写测试".format(test_count / total_commits * 100))
    if health['fix_ratio'] > 20:
        categories['test']['items'].append("提升代码质量：Bug 修复占比 {:.0f}%，建议加强测试和 Code Review".format(health['fix_ratio']))

    # 正面反馈
    if health['test_ratio'] >= 30:
        categories['test']['items'].append("测试做得好：测试文件占比 {:.0f}%，继续保持！".format(health['test_ratio']))

    # ============================================================
    # 文档维护 (最多 5 条)
    # ============================================================
    if habit_score['doc_awareness'] < 10:
        categories['doc']['items'].append("增加文档投入：定期更新 README 和 API 文档")
    elif health['doc_ratio'] < 5:
        categories['doc']['items'].append("完善文档：文档变更占比 {:.0f}%，重要功能应有文档说明".format(health['doc_ratio']))
    if total_commits > 0:
        docs_count = commit_types.get('docs', 0)
        if docs_count / total_commits < 0.05 and total_commits > 50:
            categories['doc']['items'].append("增加文档提交：文档相关提交仅占 {:.0f}%，建议及时更新文档".format(docs_count / total_commits * 100))

    # 正面反馈
    if health['doc_ratio'] >= 15:
        categories['doc']['items'].append("文档做得好：文档变更占比 {:.0f}%，继续保持！".format(health['doc_ratio']))

    # ============================================================
    # 作息健康 (最多 5 条)
    # ============================================================
    if habit_score['schedule'] < 10:
        categories['schedule']['items'].append("改善作息规律：作息得分仅 {}/20，夜间和周末提交较多".format(habit_score['schedule']))
    if health['night_ratio'] > 25:
        categories['schedule']['items'].append("注意作息健康：夜间提交占比 {:.0f}%，建议调整为白天工作".format(health['night_ratio']))
    if health['weekend_ratio'] > 25:
        categories['schedule']['items'].append("平衡工作生活：周末提交占比 {:.0f}%，注意适当休息".format(health['weekend_ratio']))
    if hourly:
        late_night = sum(hourly[0:6])
        total = sum(hourly)
        if total > 0 and late_night / total > 0.15:
            categories['schedule']['items'].append("减少深夜编码：凌晨 0-6 点提交占比 {:.0f}%，长期熬夜影响代码质量".format(late_night / total * 100))
    if peak_hours:
        if 22 in peak_hours or 23 in peak_hours:
            categories['schedule']['items'].append("调整工作节奏：深夜是你最活跃的时段，建议将核心工作移到白天")

    # 正面反馈
    if health['night_ratio'] < 15 and health['weekend_ratio'] < 15:
        categories['schedule']['items'].append("工作生活平衡：夜间和周末提交都很少，作息健康")

    # ============================================================
    # 项目管理 (最多 6 条)
    # ============================================================
    if habit_score['focus'] < 10:
        categories['project']['items'].append("提升专注度：项目聚焦得分仅 {}/15，建议减少同时维护的项目数".format(habit_score['focus']))
    focus_index = data.get('focus_index', 100)
    if focus_index < 60:
        categories['project']['items'].append("提高项目聚焦度：精力较分散，建议集中精力在 1-2 个核心项目上")
    if total_projects > 15:
        categories['project']['items'].append("精简项目数量：同时维护 {} 个项目，建议聚焦核心项目提升效率".format(total_projects))
    if projects and total_commits > 0:
        active_projects = sum(1 for p in projects if isinstance(p, dict) and p.get('commits', 0) > 10)
        if active_projects <= 2 and total_projects > 5:
            categories['project']['items'].append("项目活跃度不均：{} 个项目中仅 {} 个活跃，建议清理不活跃项目".format(total_projects, active_projects))
    if health['refactor_ratio'] < 10 and health['feat_ratio'] > 50:
        categories['project']['items'].append("关注技术债：功能开发占比高但重构不足，建议定期安排重构时间")
    if total_commits > 0:
        feat_c = commit_types.get('feat', 0)
        fix_c = commit_types.get('fix', 0)
        refactor_c = commit_types.get('refactor', 0)
        maintenance = fix_c + refactor_c
        if feat_c > 0 and maintenance > 0:
            ratio = feat_c / maintenance
            if ratio > 5:
                categories['project']['items'].append("功能远超维护：功能/维护比 {:.1f}:1，注意技术债积累".format(ratio))

    # 正面反馈
    if total_projects <= 3 and total_commits > 100:
        categories['project']['items'].append("项目聚焦度高：仅维护 {} 个项目，精力集中".format(total_projects))
    if health['refactor_ratio'] >= 10:
        categories['project']['items'].append("重构做得好：重构占比 {:.0f}%，代码质量持续改善".format(health['refactor_ratio']))

    # ============================================================
    # AI 协作 (最多 4 条)
    # ============================================================
    ai_ratio = ai.get('ai_commit_ratio', 0)
    if ai_ratio > 40:
        categories['ai']['items'].append("善用 AI：AI 占比超过 40%，建议仔细审查 AI 生成的代码")
    elif ai_ratio > 0 and ai_ratio < 15:
        categories['ai']['items'].append("探索 AI 工具：当前 AI 使用率 {:.0f}%，可尝试 Copilot/Cursor 提升效率".format(ai_ratio))
    ai_influence = ai.get('ai_influence_score', 0)
    if ai_influence > 70:
        categories['ai']['items'].append("AI 深度协作：AI 影响分 {}，建议定期审查 AI 生成的代码".format(ai_influence))
    ai_tools = ai.get('tools', {})
    if len(ai_tools) >= 3:
        categories['ai']['items'].append("AI 工具多样化：使用了 {} 种 AI 工具，建议固定 1-2 种核心工具".format(len(ai_tools)))

    # 正面反馈
    if ai_ratio >= 20 and ai_ratio <= 40:
        categories['ai']['items'].append("AI 使用适中：AI 占比 {:.0f}%，人机协作良好".format(ai_ratio))

    # ============================================================
    # 构建 HTML（带 tab 切换）
    # ============================================================
    # 过滤空分类
    active_cats = [(k, v) for k, v in categories.items() if v['items']]

    if not active_cats:
        return '<div class="sug-item"><div class="sug-text">继续保持良好的开发习惯！各项指标都很健康</div></div>'

    html = '<div class="sug-tabs">'
    for i, (cat_key, cat) in enumerate(active_cats):
        active_class = ' active' if i == 0 else ''
        html += f'<button class="sug-tab{active_class}" data-cat="{cat_key}">{cat["icon"]} {cat["name"]} ({len(cat["items"])})</button>'
    html += '</div>'

    for i, (cat_key, cat) in enumerate(active_cats):
        active_class = ' active' if i == 0 else ''
        html += f'<div class="sug-panel{active_class}" data-cat="{cat_key}">'
        for j, item in enumerate(cat['items'], 1):
            html += f'<div class="sug-item"><div class="sug-num">{j}</div><div class="sug-text">{item}</div></div>'
        html += '</div>'

    return html


# ============================================================
# JS 脚本构建（普通字符串，不需要 f-string 转义）
# ============================================================

def _build_js(all_commits_json, project_names_json, project_meta_json,
              month_labels_json, type_labels_json, type_names_json, type_colors_json,
              colors_json, lang_labels_json, lang_values_json,
              eng_spectrum, ai_spectrum, test_ratio, doc_ratio,
              ai_detected, ai_count, low_info_ratio,
              init_hourly_json, init_weekly_json, init_type_values_json,
              init_stack_json, init_bubble_json, init_month_labels_json,
              multi_year, monthly_ai_json):

    return f"""
        // 原始数据
        const allCommits = {all_commits_json};
        const projectNames = {project_names_json};
        const projectMeta = {project_meta_json};
        const typeLabels = {type_labels_json};
        const typeNames = {type_names_json};
        const MULTI_YEAR = {multi_year};
        const typeColors = {type_colors_json};
        const COLORS = {colors_json};
        const langLabels = {lang_labels_json};
        const langValues = {lang_values_json};

        // 月份格式化（跨年时带年份）
        function fmtMonth(m) {{
            return MULTI_YEAR ? m.slice(0, 4) + '年' + m.slice(5, 7) + '月' : m.slice(5, 7) + '月';
        }}

        // 旧数据兜底默认值
        const ORIG_ENG_SPECTRUM = {eng_spectrum};
        const ORIG_AI_SPECTRUM = {ai_spectrum};
        const ORIG_TEST_RATIO = {test_ratio};
        const ORIG_DOC_RATIO = {doc_ratio};
        const ORIG_AI_DETECTED = {ai_detected};
        const ORIG_AI_COUNT = {ai_count};
        const ORIG_LOW_INFO_RATIO = {low_info_ratio};

        // AI 月度趋势数据
        const monthlyAI = {monthly_ai_json};

        allCommits.forEach(c => {{
            const meta = projectMeta[c.project] || {{}};
            if (!c.language) c.language = meta.language || 'Unknown';
            c.fileChangeCount = Number(c.file_change_count ?? c.fileChangeCount ?? 0);
            c.testFiles = Number(c.test_files ?? c.testFiles ?? 0);
            c.docFiles = Number(c.doc_files ?? c.docFiles ?? 0);
            c.lowInfo = Boolean(c.low_info ?? c.lowInfo ?? false);
            c.aiSignal = Boolean(c.ai_signal ?? c.aiSignal ?? false);
            c.repoAiSignal = Boolean(c.repo_ai_signal ?? c.repoAiSignal ?? false);
            c.classificationConfidence = c.classification_confidence || c.classificationConfidence || 'low';
        }});

        function dateStartTs(dateText) {{
            return new Date(dateText + 'T00:00:00').getTime() / 1000;
        }}

        function dateEndTs(dateText) {{
            return new Date(dateText + 'T23:59:59').getTime() / 1000;
        }}

        function dateTextFromTs(ts) {{
            return formatDateInput(new Date(ts * 1000));
        }}

        function getProjectCommits(project) {{
            return project === 'all' ? allCommits : allCommits.filter(c => c.project === project);
        }}

        function syncDateInputsToCommits(commits) {{
            const sinceInput = document.getElementById('filterSince');
            const untilInput = document.getElementById('filterUntil');
            if (!commits.length) {{
                sinceInput.value = '';
                untilInput.value = '';
                return;
            }}
            const timestamps = commits.map(c => c.ts);
            sinceInput.value = dateTextFromTs(Math.min(...timestamps));
            untilInput.value = dateTextFromTs(Math.max(...timestamps));
        }}

        function formatDateInput(date) {{
            const y = date.getFullYear();
            const m = String(date.getMonth() + 1).padStart(2, '0');
            const d = String(date.getDate()).padStart(2, '0');
            return `${{y}}-${{m}}-${{d}}`;
        }}

        function shiftMonths(date, months) {{
            const shifted = new Date(date);
            const originalDay = shifted.getDate();
            shifted.setMonth(shifted.getMonth() + months);
            if (shifted.getDate() !== originalDay) shifted.setDate(0);
            return shifted;
        }}

        function markCustomRange() {{
            document.getElementById('filterRange').value = 'custom';
        }}

        function applyPresetRange() {{
            const range = document.getElementById('filterRange').value;
            const sinceInput = document.getElementById('filterSince');
            const untilInput = document.getElementById('filterUntil');

            if (range === 'all') {{
                const project = document.getElementById('filterProject').value;
                syncDateInputsToCommits(getProjectCommits(project));
            }} else if (range !== 'custom') {{
                const until = new Date();
                const since = range === '1m'
                    ? shiftMonths(until, -1)
                    : range === '6m'
                        ? shiftMonths(until, -6)
                        : shiftMonths(until, -12);
                sinceInput.value = formatDateInput(since);
                untilInput.value = formatDateInput(until);
            }}

            applyFilters();
        }}

        // 填充项目下拉
        const select = document.getElementById('filterProject');
        projectNames.forEach(name => {{
            const opt = document.createElement('option');
            opt.value = name;
            opt.textContent = name;
            select.appendChild(opt);
        }});

        // Chart.js 配置
        const chartDefaults = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ labels: {{ padding: 14, usePointStyle: true, font: {{ size: 11 }} }} }} }}
        }};
        const charts = {{}};

        // 工具函数
        function getScoreColor(score) {{
            if (score >= 80) return '#1a7f37';
            if (score >= 60) return '#bf8700';
            return '#cf222e';
        }}
        function getScoreLabel(score) {{
            if (score >= 80) return '优秀';
            if (score >= 60) return '良好';
            if (score >= 40) return '一般';
            return '需改进';
        }}

        // 人格名称映射（MBTI 风格）
        const FRONTEND_LANGUAGES = new Set(['JavaScript', 'TypeScript', 'HTML', 'CSS']);

        function pickPersona(agg, personaCode, timeSpectrum, rhythmSpectrum, focusSpectrum, styleSpectrum) {{
            const projectCount = Object.keys(agg.projectCounts).length;
            const frontendCommits = Object.entries(agg.languageCounts)
                .filter(([lang]) => FRONTEND_LANGUAGES.has(lang))
                .reduce((sum, [, count]) => sum + count, 0);
            const frontendRatio = agg.total > 0 ? frontendCommits / agg.total : 0;
            const choreRatio = agg.total > 0 ? (agg.types.chore || 0) / agg.total : 0;

            const topHackerScore = (agg.total >= 200) + (agg.avgPerDay >= 2) + (projectCount >= 5) + (agg.engSpectrum >= 50);
            const personas = [
                {{name: '顶级黑客', icon: '⚡', desc: '跨项目、高频率、能交付也能打磨，像是把工程现场当主场。', score: topHackerScore >= 3 ? topHackerScore : 0}},
                {{name: '前端狂魔', icon: '🎨', desc: 'UI、交互和产品触感占据主舞台，对用户看到的那一面格外敏感。', score: frontendRatio >= 0.35 ? 1 : 0}},
                {{name: '基建达人', icon: '🏗️', desc: '热衷把脚手架、依赖、CI 和工程底座收拾顺手，别人开工会更舒服。', score: choreRatio >= 0.18 ? 1 : 0}},
                {{name: '测试守门人', icon: '✅', desc: '不太信任“应该没问题”，更喜欢让测试替自己站岗。', score: agg.testRatio >= 0.20 ? 1 : 0}},
                {{name: '文档布道者', icon: '📚', desc: '知道未来的自己也会忘，所以愿意把上下文写清楚。', score: agg.docRatio >= 0.18 ? 1 : 0}},
                {{name: 'Bug 猎手', icon: '🎯', desc: '对异常、回归和边界条件很敏感，擅长把系统拉回正轨。', score: agg.fixRatio >= 0.25 ? 1 : 0}},
                {{name: '重构外科医生', icon: '🔧', desc: '看不得结构别扭，喜欢在不惊动用户的地方让代码重新呼吸。', score: agg.refactorRatio >= 0.10 ? 1 : 0}},
                {{name: '产品推进器', icon: '🚀', desc: '目标感强，喜欢把想法迅速推到可运行、可体验的状态。', score: agg.featRatio >= 0.35 ? 1 : 0}},
                {{name: '多仓调度大师', icon: '🧭', desc: '能在多个项目之间切换上下文，脑内自带任务看板。', score: projectCount >= 10 && agg.focusIndex < 0.70 ? 1 : 0}},
                {{name: '深夜黑客', icon: '🌙', desc: '夜深后状态更容易上线，安静时间是你的高产窗口。', score: agg.nightRatio >= 0.35 ? 1 : 0}},
                {{name: 'AI 搭子型开发者', icon: '🤖', desc: '会把 AI 当成结对伙伴，用它放大探索、实现和整理能力。', score: agg.aiDetected ? 1 : 0}},
                {{name: '长期主义维护者', icon: '🛠️', desc: '节奏稳、耐心足，愿意把项目长期照看在可维护状态。', score: 1}},
            ];
            const selected = personas.reduce((best, item) => item.score > best.score ? item : best, personas[0]);

            const sideTags = [];
            if (selected.name !== '前端狂魔' && frontendRatio >= 0.25) sideTags.push('前端狂魔');
            if (selected.name !== '基建达人' && choreRatio >= 0.12) sideTags.push('基建达人');
            if (selected.name !== '多仓调度大师' && projectCount >= 10) sideTags.push('多仓调度大师');
            if (selected.name !== 'AI 搭子型开发者' && agg.aiDetected) sideTags.push('AI 搭子');
            if (selected.name !== '测试守门人' && agg.testRatio >= 0.15) sideTags.push('测试守门人');
            if (selected.name !== '文档布道者' && agg.docRatio >= 0.10) sideTags.push('文档布道者');
            if (selected.name !== '深夜黑客' && agg.nightRatio >= 0.30) sideTags.push('深夜黑客');

            const descParts = [];
            descParts.push(personaCode[0] === 'N' ? `夜间 ${{timeSpectrum}}%` : `白天 ${{100 - timeSpectrum}}%`);
            descParts.push(personaCode[1] === 'S' ? `高频提交 ${{rhythmSpectrum}}%` : `稳定推进 ${{100 - rhythmSpectrum}}%`);
            descParts.push(personaCode[2] === 'C' ? `核心项目 ${{focusSpectrum}}%` : `多项目并行 ${{100 - focusSpectrum}}%`);
            descParts.push(personaCode[3] === 'P' ? `新功能 ${{styleSpectrum}}%` : `维护系统 ${{100 - styleSpectrum}}%`);
            let detail = descParts.join('，');
            if (sideTags.length) detail += '；副人格：' + sideTags.slice(0, 3).join(' / ');
            detail += `；证据：${{projectCount}} 个项目、${{agg.total}} 次提交、日均 ${{agg.avgPerDay.toFixed(1)}} 次`;

            return {{...selected, detail}};
        }};

        // ============================================================
        // 图表初始化
        // ============================================================
        function initCharts(hourly, weekly, typeValues, stackData, bubbleData, monthLabels) {{
            // 24小时
            charts.hour = new Chart(document.getElementById('hourChart'), {{
                type: 'bar',
                data: {{
                    labels: Array.from({{length: 24}}, (_, i) => i.toString().padStart(2, '0') + ':00'),
                    datasets: [{{
                        data: hourly,
                        backgroundColor: hourly.map(v => {{
                            const max = Math.max(...hourly, 1);
                            return `rgba(9,105,218,${{0.2 + v/max*0.8}})`;
                        }}),
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    ...chartDefaults,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }},
                        x: {{ grid: {{ display: false }}, ticks: {{ font: {{ size: 10 }} }} }}
                    }}
                }}
            }});

            // 星期
            charts.week = new Chart(document.getElementById('weekChart'), {{
                type: 'bar',
                data: {{
                    labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                    datasets: [{{
                        data: weekly,
                        backgroundColor: ['#0969da','#0969da','#0969da','#0969da','#0969da','#8250df','#8250df'],
                        borderRadius: 6
                    }}]
                }},
                options: {{
                    ...chartDefaults,
                    plugins: {{ legend: {{ display: false }} }},
                    scales: {{
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }},
                        x: {{ grid: {{ display: false }} }}
                    }}
                }}
            }});

            // 每月堆叠
            charts.monthly = new Chart(document.getElementById('monthlyChart'), {{
                type: 'bar',
                data: {{ labels: monthLabels, datasets: stackData }},
                options: {{
                    ...chartDefaults,
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ padding: 12, usePointStyle: true, font: {{ size: 11 }} }} }},
                        tooltip: {{ mode: 'index', intersect: false }}
                    }},
                    scales: {{
                        x: {{ stacked: true, grid: {{ display: false }} }},
                        y: {{ stacked: true, beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }}
                    }}
                }}
            }});

            // 气泡图
            charts.bubble = new Chart(document.getElementById('bubbleChart'), {{
                type: 'bubble',
                data: {{ labels: monthLabels, datasets: bubbleData }},
                options: {{
                    ...chartDefaults,
                    plugins: {{
                        legend: {{ position: 'bottom', labels: {{ padding: 10, usePointStyle: true, font: {{ size: 10 }} }} }},
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{
                                    return ctx.dataset.label + ': ' + (ctx.parsed.y) + ' 次';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ type: 'category', offset: true, grid: {{ display: false }} }},
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }}
                    }}
                }}
            }});

            // Commit 类型
            charts.type = new Chart(document.getElementById('typeChart'), {{
                type: 'doughnut',
                data: {{
                    labels: typeNames,
                    datasets: [{{ data: typeValues, backgroundColor: typeColors, borderWidth: 0 }}]
                }},
                options: {{
                    ...chartDefaults,
                    plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 12, usePointStyle: true }} }} }},
                    cutout: '60%'
                }}
            }});

            // 语言分布
            charts.lang = new Chart(document.getElementById('langChart'), {{
                type: 'doughnut',
                data: {{
                    labels: langLabels,
                    datasets: [{{ data: langValues, backgroundColor: COLORS, borderWidth: 0 }}]
                }},
                options: {{
                    ...chartDefaults,
                    plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 12, usePointStyle: true }} }} }},
                    cutout: '60%'
                }}
            }});

            // AI 趋势图
            const aiTrendCanvas = document.getElementById('aiTrendChart');
            if (aiTrendCanvas && Object.keys(monthlyAI).length > 0) {{
                const sortedMonths = Object.keys(monthlyAI).sort();
                const aiData = sortedMonths.map(m => monthlyAI[m]);
                const monthLabels2 = sortedMonths.map(fmtMonth);

                charts.aiTrend = new Chart(aiTrendCanvas, {{
                    type: 'line',
                    data: {{
                        labels: monthLabels2,
                        datasets: [{{
                            label: 'AI 辅助提交',
                            data: aiData,
                            borderColor: '#10b981',
                            backgroundColor: 'rgba(16, 185, 129, 0.1)',
                            fill: true,
                            tension: 0.3,
                            pointRadius: 4,
                            pointHoverRadius: 6
                        }}]
                    }},
                    options: {{
                        ...chartDefaults,
                        plugins: {{
                            legend: {{ display: false }},
                            tooltip: {{
                                callbacks: {{
                                    label: function(ctx) {{
                                        return ctx.parsed.y + ' 次 AI 辅助提交';
                                    }}
                                }}
                            }}
                        }},
                        scales: {{
                            x: {{ grid: {{ display: false }} }},
                            y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }}
                        }}
                    }}
                }});
            }}
        }}

        // ============================================================
        // 筛选逻辑
        // ============================================================
        function applyFilters() {{
            const project = document.getElementById('filterProject').value;
            const range = document.getElementById('filterRange').value;
            const since = document.getElementById('filterSince').value;
            const until = document.getElementById('filterUntil').value;

            let filtered = getProjectCommits(project);
            if (range === 'all') {{
                syncDateInputsToCommits(filtered);
            }} else {{
                if (since) {{
                    const ts = dateStartTs(since);
                    filtered = filtered.filter(c => c.ts >= ts);
                }}
                if (until) {{
                    const ts = dateEndTs(until);
                    filtered = filtered.filter(c => c.ts <= ts);
                }}
            }}
            if (filtered.length === 0) {{ alert('没有符合条件的数据'); return; }}
            updateAll(filtered, project);
        }}

        function resetFilters() {{
            document.getElementById('filterProject').value = 'all';
            document.getElementById('filterRange').value = 'all';
            syncDateInputsToCommits(allCommits);
            updateAll(allCommits, 'all');
        }}

        // ============================================================
        // 聚合计算
        // ============================================================
        function aggregate(commits) {{
            const total = commits.length;
            const hourly = new Array(24).fill(0);
            const weekly = new Array(7).fill(0);
            const monthly = {{}};
            const types = {{}};
            const projectCounts = {{}};
            const languageCounts = {{}};
            const projectActiveDays = {{}};
            const activeDays = new Set();
            let fileChanges = 0;
            let testFiles = 0;
            let docFiles = 0;
            let lowInfoCommits = 0;
            let aiSignalCount = 0;
            let aiToolingSignalCount = 0;
            const confidenceCounts = {{high: 0, medium: 0, low: 0}};

            commits.forEach(c => {{
                const language = c.language || (projectMeta[c.project] || {{}}).language || 'Unknown';
                hourly[c.hour]++;
                weekly[c.weekday]++;
                monthly[c.month] = (monthly[c.month] || 0) + 1;
                types[c.type] = (types[c.type] || 0) + 1;
                projectCounts[c.project] = (projectCounts[c.project] || 0) + 1;
                languageCounts[language] = (languageCounts[language] || 0) + 1;
                const dayKey = Math.floor(c.ts / 86400);
                activeDays.add(dayKey);
                if (!projectActiveDays[c.project]) projectActiveDays[c.project] = new Set();
                projectActiveDays[c.project].add(dayKey);
                fileChanges += c.fileChangeCount || 0;
                testFiles += c.testFiles || 0;
                docFiles += c.docFiles || 0;
                if (c.lowInfo) lowInfoCommits++;
                if (c.aiSignal) aiSignalCount++;
                if (c.repoAiSignal) aiToolingSignalCount++;
                confidenceCounts[c.classificationConfidence] = (confidenceCounts[c.classificationConfidence] || 0) + 1;
            }});

            const days = activeDays.size || 1;
            const avgPerDay = total / days;
            const nightCommits = hourly.slice(22).reduce((a, b) => a + b, 0) + hourly.slice(0, 5).reduce((a, b) => a + b, 0);
            const nightRatio = total > 0 ? nightCommits / total : 0;
            const dayCommits = hourly.slice(8, 20).reduce((a, b) => a + b, 0);
            const lateCommits = hourly.slice(20, 24).reduce((a, b) => a + b, 0) + hourly.slice(0, 6).reduce((a, b) => a + b, 0);
            const weekendCommits = weekly[5] + weekly[6];
            const weekendRatio = total > 0 ? weekendCommits / total : 0;
            const featRatio = total > 0 ? (types.feat || 0) / total : 0;
            const fixRatio = total > 0 ? (types.fix || 0) / total : 0;
            const refactorRatio = total > 0 ? (types.refactor || 0) / total : 0;
            const maintenanceRatio = fixRatio + refactorRatio + (total > 0 ? (types.chore || 0) / total : 0);
            const testRatio = fileChanges > 0 ? testFiles / fileChanges : ORIG_TEST_RATIO / 100;
            const docRatio = fileChanges > 0 ? docFiles / fileChanges : ORIG_DOC_RATIO / 100;
            const lowInfoRatio = total > 0 ? lowInfoCommits / total : ORIG_LOW_INFO_RATIO / 100;
            const lowConfidenceRatio = total > 0 ? confidenceCounts.low / total : 0;
            const engSpectrum = Math.round(Math.min((testRatio + docRatio) / 0.25 * 100, 100));
            const aiDetected = aiSignalCount >= 3 || aiToolingSignalCount > 0;
            const aiCommitRatio = total > 0 ? aiSignalCount / total : 0;
            const aiToolingRatio = total > 0 ? aiToolingSignalCount / total : 0;
            const aiSpectrum = Math.round(Math.min(aiCommitRatio * 300 + Math.min(aiToolingRatio * 15, 15), 100));

            const projSorted = Object.entries(projectCounts).sort((a, b) => b[1] - a[1]);
            const top3Commits = projSorted.slice(0, 3).reduce((a, b) => a + b[1], 0);
            const focusIndex = total > 0 ? top3Commits / total : 0;

            return {{
                total, hourly, weekly, monthly, types, projectCounts, languageCounts, projectActiveDays, activeDays, days,
                avgPerDay, nightRatio, dayCommits, lateCommits, weekendRatio,
                featRatio, fixRatio, refactorRatio, maintenanceRatio,
                testRatio, docRatio, lowInfoRatio, lowConfidenceRatio, confidenceCounts, engSpectrum, aiDetected, aiSignalCount, aiToolingSignalCount, aiCommitRatio, aiToolingRatio, aiSpectrum,
                projSorted, top3Commits, focusIndex
            }};
        }}

        // ============================================================
        // 更新统计卡片
        // ============================================================
        function updateStats(agg, project) {{
            document.getElementById('statCommits').textContent = agg.total;
            document.getElementById('statProjects').textContent = project === 'all' ? Object.keys(agg.projectCounts).length : 1;
            document.getElementById('statDaily').textContent = agg.avgPerDay.toFixed(1);
            const projText = project === 'all' ? Object.keys(agg.projectCounts).length + ' 个项目' : project;
            document.getElementById('headerSubtitle').textContent = `${{projText}} · ${{agg.total}} 次提交 · ${{agg.days}} 天活跃`;
        }}

        // ============================================================
        // 更新 DevPersona
        // ============================================================
        function updatePersona(agg) {{
            const timeSpectrum = Math.round(agg.lateCommits / Math.max(agg.dayCommits + agg.lateCommits, 1) * 100);
            const rhythmSpectrum = Math.round(Math.min(agg.avgPerDay / 5 * 100, 100));
            const focusSpectrum = Math.round(agg.focusIndex * 100);
            const styleSpectrum = Math.round(agg.featRatio / Math.max(agg.featRatio + agg.maintenanceRatio, 0.01) * 100);

            const t = timeSpectrum > 50 ? 'N' : 'D';
            const r = rhythmSpectrum > 50 ? 'S' : 'M';
            const f = focusSpectrum > 50 ? 'C' : 'D';
            const s = styleSpectrum > 50 ? 'P' : 'G';
            const e = agg.engSpectrum > 50 ? 'Q' : 'R';
            const a = agg.aiSpectrum > 50 ? 'A' : 'H';
            const personaCode = t + r + f + s + e + a;
            const personaInfo = pickPersona(agg, personaCode, timeSpectrum, rhythmSpectrum, focusSpectrum, styleSpectrum);

            document.getElementById('personaCard').innerHTML = `
                <div style="font-size:3em;margin-bottom:8px;">${{personaInfo.icon}}</div>
                <div style="font-size:1.6em;font-weight:700;color:#1f2328;">${{personaInfo.name}}</div>
                <div style="font-size:1.1em;color:#0969da;font-weight:600;margin-top:4px;font-family:monospace;">${{personaCode}}</div>
                <div style="color:#1f2328;font-size:0.95em;margin-top:8px;font-weight:500;">${{personaInfo.desc}}</div>
                <div style="color:#656d76;font-size:0.85em;margin-top:4px;">${{personaInfo.detail}}</div>
            `;

            // 维度光谱
            const dims = [
                {{key: 'time', name: '时间偏好', code: t, spectrum: timeSpectrum, left: '白天型', right: '夜猫型', leftCode: 'D', rightCode: 'N', leftTrait: '日间掌控者', rightTrait: '夜间爆发者', leftDesc: '白天更容易进入状态，节奏清晰。', rightDesc: '安静时段更容易输出，灵感来得晚。'}},
                {{key: 'rhythm', name: '节奏风格', code: r, spectrum: rhythmSpectrum, left: '马拉松型', right: '冲刺型', leftCode: 'M', rightCode: 'S', leftTrait: '长线推进者', rightTrait: '冲刺迭代者', leftDesc: '偏稳定推进，提交更像长跑。', rightDesc: '偏高频推进，短时间爆发强。'}},
                {{key: 'focus', name: '专注程度', code: f, spectrum: focusSpectrum, left: '分散型', right: '专注型', leftCode: 'D', rightCode: 'C', leftTrait: '多线调度者', rightTrait: '核心深挖者', leftDesc: '能在多个项目间切换上下文。', rightDesc: '精力更集中在核心项目。'}},
                {{key: 'style', name: '开发风格', code: s, spectrum: styleSpectrum, left: '守护型', right: '先锋型', leftCode: 'G', rightCode: 'P', leftTrait: '系统守护者', rightTrait: '功能开拓者', leftDesc: '更常维护、修复和打磨系统。', rightDesc: '更常推进新功能和新想法。'}},
                {{key: 'engineering', name: '工程取向', code: e, spectrum: agg.engSpectrum, left: '快速迭代', right: '质量导向', leftCode: 'R', rightCode: 'Q', leftTrait: '快速试错派', rightTrait: '质量洁癖派', leftDesc: '偏速度和反馈，先跑起来。', rightDesc: '偏测试、文档和工程质量。'}},
                {{key: 'ai', name: 'AI 协作', code: a, spectrum: agg.aiSpectrum, left: '手工型', right: 'AI 协作型', leftCode: 'H', rightCode: 'A', leftTrait: '手作掌控派', rightTrait: 'AI 搭子派', leftDesc: '主要靠自己手工推进。', rightDesc: '会把 AI 当成结对伙伴。'}},
            ];
            document.getElementById('dimsDetail').innerHTML = dims.map(d => {{
                const isRight = d.code === d.rightCode;
                const pct = isRight ? d.spectrum : (100 - d.spectrum);
                const align = isRight ? 'right' : 'left';
                const activeTrait = isRight ? d.rightTrait : d.leftTrait;
                const activeDesc = isRight ? d.rightDesc : d.leftDesc;
                const leftActive = isRight ? '' : ' active';
                const rightActive = isRight ? ' active' : '';
                return `<div class="dim-item">
                    <div class="dim-head">
                        <div class="dim-name">${{d.name}}</div>
                        <div class="dim-codepair">${{d.leftCode}}/${{d.rightCode}}</div>
                    </div>
                    <div class="dim-active">
                        <span class="dim-active-code">${{d.code}}</span>
                        <span class="dim-active-name">${{activeTrait}}</span>
                    </div>
                    <div class="dim-row">
                        <span class="dim-label${{leftActive}}" style="text-align:right;">${{d.left}}</span>
                        <div class="dim-bar"><div class="dim-bar-fill" style="width:${{d.spectrum}}%;"></div></div>
                        <span class="dim-label${{rightActive}}">${{d.right}}</span>
                    </div>
                    <div class="dim-pct" style="text-align:${{align}};">倾向 ${{pct}}%</div>
                    <div class="dim-desc">${{activeDesc}}</div>
                </div>`;
            }}).join('');
        }}

        // ============================================================
        // 更新 Habit Score
        // ============================================================
        function updateHabitScore(agg) {{
            const granularity = Math.round(Math.min(40, agg.avgPerDay / 4.5 * 40));
            const schedule = Math.round(Math.min(20, Math.max(0, (1 - agg.nightRatio / 0.4)) * 20));
            const focusScore = Math.round(Math.min(15, agg.focusIndex / 0.7 * 15));
            const testAwareness = Math.round(Math.min(10, agg.testRatio / 0.15 * 10));
            const docAwareness = Math.round(Math.min(15, agg.docRatio / 0.10 * 15));
            const totalScore = granularity + testAwareness + docAwareness + schedule + focusScore;
            agg.habitScore = {{totalScore, granularity, testAwareness, docAwareness, schedule, focusScore}};

            document.getElementById('statScore').textContent = totalScore;
            document.getElementById('scoreNumber').textContent = totalScore;
            document.getElementById('scoreNumber').style.color = getScoreColor(totalScore);
            document.getElementById('scoreLabel').textContent = `/ 100 · ${{getScoreLabel(totalScore)}}`;

            const scoreDims = [
                ['提交粒度', granularity, 40],
                ['测试意识', testAwareness, 10],
                ['文档意识', docAwareness, 15],
                ['作息规律', schedule, 20],
                ['项目聚焦', focusScore, 15],
            ];
            document.getElementById('scoreDims').innerHTML = scoreDims.map(([name, score, max]) => {{
                const pct = (score / max * 100).toFixed(0);
                const color = getScoreColor(score / max * 100);
                return `<div class="score-dim-row">
                    <div class="score-dim-name">${{name}}</div>
                    <div class="score-dim-bar"><div class="score-dim-bar-fill" style="width:${{pct}}%;background:${{color}};"></div></div>
                    <div class="score-dim-val">${{score}}/${{max}} <span class="score-dim-pct">(${{pct}}%)</span></div>
                </div>`;
            }}).join('');
        }}

        // ============================================================
        // 更新标签
        // ============================================================
        function updateTags(agg) {{
            const tags = [];
            const testPct = agg.testRatio * 100;
            const docPct = agg.docRatio * 100;
            if (agg.weekendRatio >= 0.3) tags.push({{icon: '📅', name: '周末战士', desc: `周末提交占比 ${{(agg.weekendRatio*100).toFixed(0)}}%`}});
            if (agg.aiDetected) tags.push({{icon: '🤖', name: 'AI 协作者', desc: '使用 AI 工具辅助开发'}});
            if (testPct >= 15) tags.push({{icon: '✅', name: '测试达人', desc: `测试覆盖 ${{testPct.toFixed(0)}}%`}});
            else if (testPct < 5) tags.push({{icon: '⚠️', name: '测试待加强', desc: `测试覆盖仅 ${{testPct.toFixed(0)}}%`}});
            if (docPct >= 10) tags.push({{icon: '📚', name: '文档之星', desc: '文档维护优秀'}});
            else if (docPct < 3) tags.push({{icon: '📝', name: '文档债务', desc: '文档投入不足'}});
            if (Object.keys(agg.projectCounts).length >= 10) tags.push({{icon: '🎪', name: '多面手', desc: `同时维护 ${{Object.keys(agg.projectCounts).length}} 个项目`}});
            if (agg.lateCommits > agg.dayCommits) tags.push({{icon: '🌙', name: '夜猫子', desc: '夜间比白天更活跃'}});
            if (agg.avgPerDay >= 5) tags.push({{icon: '🏃', name: '暴风提交', desc: `日均提交 ${{agg.avgPerDay.toFixed(1)}} 次`}});
            else if (agg.avgPerDay < 0.5) tags.push({{icon: '🦥', name: '佛系开发', desc: `日均提交仅 ${{agg.avgPerDay.toFixed(1)}} 次`}});
            if (agg.refactorRatio >= 0.1) tags.push({{icon: '🔧', name: '重构狂魔', desc: `重构占比 ${{(agg.refactorRatio*100).toFixed(0)}}%`}});

            document.getElementById('tagsGrid').innerHTML = tags.slice(0, 5).map(tag => `
                <div class="tag-item">
                    <div class="tag-icon">${{tag.icon}}</div>
                    <div class="tag-name">${{tag.name}}</div>
                    <div class="tag-desc">${{tag.desc}}</div>
                </div>
            `).join('');
        }}

        // ============================================================
        // 更新图表
        // ============================================================
        function updateCharts(agg, project) {{
            // 24小时
            charts.hour.data.datasets[0].data = agg.hourly;
            const maxH = Math.max(...agg.hourly, 1);
            charts.hour.data.datasets[0].backgroundColor = agg.hourly.map(v => `rgba(9,105,218,${{0.2 + v/maxH*0.8}})`);
            charts.hour.update();

            // 星期
            charts.week.data.datasets[0].data = agg.weekly;
            charts.week.update();

            // 每月堆叠
            const sortedMonths = Object.keys(agg.monthly).sort();
            const projList = project === 'all'
                ? agg.projSorted.slice(0, 7)
                : [[project, agg.total]];
            const stackData = projList.map(([name, _], i) => {{
                const pm = {{}};
                agg.commits.filter(c => c.project === name).forEach(c => {{ pm[c.month] = (pm[c.month] || 0) + 1; }});
                return {{ label: name, data: sortedMonths.map(m => pm[m] || 0), backgroundColor: COLORS[i % COLORS.length] }};
            }});
            if (project === 'all' && agg.projSorted.length > 7) {{
                const topNames = projList.map(p => p[0]);
                const om = {{}};
                agg.commits.filter(c => !topNames.includes(c.project)).forEach(c => {{ om[c.month] = (om[c.month] || 0) + 1; }});
                if (Object.keys(om).length > 0) stackData.push({{ label: '其他', data: sortedMonths.map(m => om[m] || 0), backgroundColor: '#9ca3af' }});
            }}
            charts.monthly.data.labels = sortedMonths.map(fmtMonth);
            charts.monthly.data.datasets = stackData;
            charts.monthly.update();

            // 气泡图
            const bubbleProjList = project === 'all'
                ? agg.projSorted.filter(([_, c]) => c >= 5).slice(0, 10)
                : [[project, agg.total]];
            const sortedMonthsForBubble = Object.keys(agg.monthly).sort();
            charts.bubble.data.labels = sortedMonthsForBubble.map(fmtMonth);
            const bubbleData = bubbleProjList.map(([name, _], i) => {{
                const pm = {{}};
                agg.commits.filter(c => c.project === name).forEach(c => {{ pm[c.month] = (pm[c.month] || 0) + 1; }});
                const points = sortedMonthsForBubble.map(m => pm[m] ? {{ x: fmtMonth(m), y: pm[m], r: Math.min(Math.max(pm[m] ** 0.5 * 2.5, 4), 30) }} : null).filter(Boolean);
                return {{ label: name, data: points, backgroundColor: COLORS[i % COLORS.length] + 'b3' }};
            }});
            charts.bubble.data.datasets = bubbleData;
            charts.bubble.update();

            // 类型环形图
            const typeValues = typeLabels.map(t => agg.types[t] || 0);
            charts.type.data.datasets[0].data = typeValues;
            charts.type.update();

            // 语言分布
            const langEntries = Object.entries(agg.languageCounts).sort((a, b) => b[1] - a[1]);
            charts.lang.data.labels = langEntries.map(([name]) => name);
            charts.lang.data.datasets[0].data = langEntries.map(([, count]) => count);
            charts.lang.data.datasets[0].backgroundColor = langEntries.map((_, i) => COLORS[i % COLORS.length]);
            charts.lang.update();
        }}

        // ============================================================
        // 更新洞察文字
        // ============================================================
        function updateInsights(agg) {{
            // 24小时洞察
            const peakHours = agg.hourly.map((v, i) => ({{v, i}})).sort((a, b) => b.v - a.v).slice(0, 3).map(x => x.i);
            document.getElementById('insightHour').innerHTML = `<strong>洞察：</strong>最活跃时段 ${{peakHours.map(h => h + ':00').join(', ')}}。${{agg.nightRatio > 0.25 ? '夜间提交占比 ' + (agg.nightRatio*100).toFixed(1) + '%。' : '作息相对规律。'}}`;

            // 星期洞察
            const weekdayNames = ['周一', '周二', '周三', '周四', '周五', '周六', '周日'];
            const peakWeekdays = agg.weekly.map((v, i) => ({{v, i}})).sort((a, b) => b.v - a.v).slice(0, 3).map(x => weekdayNames[x.i]);
            document.getElementById('insightWeek').innerHTML = `<strong>洞察：</strong>最活跃 ${{peakWeekdays.join(', ')}}。${{agg.weekendRatio > 0.2 ? '周末提交占比 ' + (agg.weekendRatio*100).toFixed(1) + '%。' : '以工作日为主。'}}`;

            // 每月洞察
            const top3Ratio = (agg.top3Commits / agg.total * 100).toFixed(0);
            document.getElementById('insightMonthly').innerHTML = `<strong>洞察：</strong>Top 3 项目占据 ${{top3Ratio}}% 的提交。${{top3Ratio > 60 ? '专注度高。' : '精力较分散。'}}`;

            // 类型洞察
            document.getElementById('insightTypes').innerHTML = `<strong>洞察：</strong>功能开发占比 ${{(agg.featRatio*100).toFixed(1)}}%，测试 ${{(agg.testRatio*100).toFixed(1)}}%，文档 ${{(agg.docRatio*100).toFixed(1)}}%。${{agg.lowInfoRatio > 0.15 ? ' 低信息量 commit 占比 ' + (agg.lowInfoRatio*100).toFixed(1) + '%。' : ''}}${{agg.lowConfidenceRatio > 0.3 ? ' Commit 类型分类置信度偏低，已优先使用文件路径兜底。' : ''}}`;

            // 工程健康洞察
            const engInsight = [];
            if (agg.testRatio < 0.05) engInsight.push('很少写测试，建议为新功能补充测试用例。');
            else if (agg.testRatio >= 0.10) engInsight.push('测试习惯不错。');
            if (agg.docRatio < 0.03) engInsight.push('文档更新较少，建议定期维护 README。');
            if (agg.nightRatio > 0.3) engInsight.push('深夜写代码比例较高，注意休息。');
            if (agg.lowInfoRatio > 0.15) engInsight.push('有些 commit 描述太简略，不利于后期回溯。');
            document.getElementById('insightEng').innerHTML = `<strong>洞察：</strong>${{engInsight.length ? engInsight.join(' ') : '各项指标正常。'}}`;
        }}

        // ============================================================
        // 更新工程健康
        // ============================================================
        function updateEngHealth(agg) {{
            const testPct = agg.testRatio * 100;
            const docPct = agg.docRatio * 100;
            const lowInfoPct = agg.lowInfoRatio * 100;
            const engItems = [
                {{label: '测试覆盖', desc: '改代码时有改测试吗', val: testPct.toFixed(1), color: testPct >= 10 ? '#1a7f37' : '#cf222e'}},
                {{label: '文档覆盖', desc: '改代码时有更新文档吗', val: docPct.toFixed(1), color: docPct >= 5 ? '#1a7f37' : '#bf8700'}},
                {{label: '功能开发', desc: '写新功能的时间占比', val: (agg.featRatio*100).toFixed(1), color: '#0969da'}},
                {{label: 'Bug 修复', desc: '修 bug 的时间占比', val: (agg.fixRatio*100).toFixed(1), color: '#cf222e'}},
                {{label: '重构', desc: '优化老代码的时间占比', val: (agg.refactorRatio*100).toFixed(1), color: '#8250df'}},
                {{label: '夜间提交', desc: '深夜写的代码占比', val: (agg.nightRatio*100).toFixed(1), color: agg.nightRatio > 0.25 ? '#bf8700' : '#656d76'}},
                {{label: '周末提交', desc: '周末写的代码占比', val: (agg.weekendRatio*100).toFixed(1), color: agg.weekendRatio > 0.25 ? '#8250df' : '#656d76'}},
                {{label: '低信息量', desc: 'commit 信息够详细吗', val: lowInfoPct.toFixed(1), color: lowInfoPct > 20 ? '#cf222e' : '#1a7f37'}},
            ];
            document.getElementById('engHealthGrid').innerHTML = engItems.map(item =>
                `<div class="eng-item">
                    <div class="eng-val" style="color:${{item.color}};">${{item.val}}%</div>
                    <div class="eng-label">${{item.label}}</div>
                    <div class="eng-desc">${{item.desc}}</div>
                </div>`
            ).join('');
        }}

        // ============================================================
        // 更新排行榜
        // ============================================================
        function updateRanking(agg) {{
            document.getElementById('projectsRanking').innerHTML = agg.projSorted.slice(0, 8).map(([name, count], i) => {{
                const meta = projectMeta[name] || {{}};
                const activeDays = agg.projectActiveDays[name] ? agg.projectActiveDays[name].size : 0;
                return `<div class="rank-row">
                    <div class="rank-num">${{i + 1}}</div>
                    <div class="rank-info">
                        <div class="rank-name">${{name}}</div>
                        <div class="rank-meta"><span>${{meta.language || 'Unknown'}}</span><span>${{activeDays}} 天活跃</span></div>
                    </div>
                    <div class="rank-commits">${{count}}</div>
                </div>`;
            }}).join('');
        }}

        // ============================================================
        // 更新提交类型条形图
        // ============================================================
        function updateTypeBars(agg) {{
            const typeValues = typeLabels.map(t => agg.types[t] || 0);
            document.getElementById('typeBars').innerHTML = typeValues.map((val, i) => {{
                const pct = (val / agg.total * 100).toFixed(1);
                return `<div class="type-bar-row">
                    <div class="type-bar-name">${{typeNames[i]}}</div>
                    <div class="type-bar-track"><div class="type-bar-fill" style="width:${{pct}}%;background:${{typeColors[i]}};"></div></div>
                    <div class="type-bar-val">${{val}} (${{pct}}%)</div>
                </div>`;
            }}).join('');
        }}

        function buildAiMonthly(commits) {{
            const monthly = {{}};
            commits.forEach(c => {{
                if (c.aiSignal) monthly[c.month] = (monthly[c.month] || 0) + 1;
            }});
            return monthly;
        }}

        function renderAiTrend(agg) {{
            const canvas = document.getElementById('aiTrendChart');
            const empty = document.getElementById('aiTrendEmpty');
            if (!canvas) return;
            if (charts.aiTrend) {{
                charts.aiTrend.destroy();
                delete charts.aiTrend;
            }}

            const aiMonthly = buildAiMonthly(agg.commits);
            const sortedMonths = Object.keys(aiMonthly).sort();
            if (!sortedMonths.length) {{
                canvas.style.display = 'none';
                if (empty) empty.style.display = 'flex';
                return;
            }}

            canvas.style.display = 'block';
            if (empty) empty.style.display = 'none';
            charts.aiTrend = new Chart(canvas, {{
                type: 'line',
                data: {{
                    labels: sortedMonths.map(fmtMonth),
                    datasets: [{{
                        label: 'AI 明确信号提交',
                        data: sortedMonths.map(m => aiMonthly[m]),
                        borderColor: '#0969da',
                        backgroundColor: 'rgba(9, 105, 218, 0.10)',
                        fill: true,
                        tension: 0.3,
                        pointRadius: 4,
                        pointHoverRadius: 6
                    }}]
                }},
                options: {{
                    ...chartDefaults,
                    plugins: {{
                        legend: {{ display: false }},
                        tooltip: {{
                            callbacks: {{
                                label: function(ctx) {{
                                    return ctx.parsed.y + ' 次 AI 明确信号提交';
                                }}
                            }}
                        }}
                    }},
                    scales: {{
                        x: {{ grid: {{ display: false }} }},
                        y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }}
                    }}
                }}
            }});
        }}

        // ============================================================
        // 更新 AI Impact
        // ============================================================
        function updateAiImpact(agg) {{
            if (charts.aiTrend) {{
                charts.aiTrend.destroy();
                delete charts.aiTrend;
            }}
            if (agg.aiDetected) {{
                const ratio = (agg.aiCommitRatio * 100).toFixed(1);
                const toolingRatio = (agg.aiToolingRatio * 100).toFixed(1);
                const explicitScore = Math.min(agg.aiCommitRatio * 300, 100);
                const toolingScore = Math.min(agg.aiToolingRatio * 15, 15);
                let insight = '';
                if (agg.aiSpectrum > 50) {{
                    insight = `AI 影响分 ${{agg.aiSpectrum}}，明确信号率 ${{ratio}}%，AI tooling 覆盖 ${{toolingRatio}}%。`;
                }} else {{
                    insight = `AI 明确信号率 ${{ratio}}%，AI tooling 覆盖 ${{toolingRatio}}%。tooling 只按弱信号计分，当前证据还不足以判成 AI 协作型。`;
                }}

                document.getElementById('aiImpact').innerHTML = `
                    <div style="display:grid;grid-template-columns:repeat(auto-fit,minmax(200px,1fr));gap:16px;margin-bottom:16px;">
                        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:20px;text-align:center;">
                            <div style="font-size:2em;margin-bottom:4px;">🤖</div>
                            <div style="font-size:1.8em;font-weight:700;color:#1f2328;">${{ratio}}%</div>
                            <div style="color:#656d76;font-size:0.85em;">AI 明确信号率</div>
                        </div>
                        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:20px;text-align:center;">
                            <div style="font-size:2em;margin-bottom:4px;">📊</div>
                            <div style="font-size:1.8em;font-weight:700;color:#1f2328;">${{agg.aiSignalCount}}</div>
                            <div style="color:#656d76;font-size:0.85em;">AI 明确信号提交</div>
                        </div>
                        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:20px;text-align:center;">
                            <div style="font-size:2em;margin-bottom:4px;">🔧</div>
                            <div style="font-size:1.8em;font-weight:700;color:#1f2328;">${{agg.aiSpectrum}}</div>
                            <div style="color:#656d76;font-size:0.85em;">AI 影响分</div>
                        </div>
                    </div>
                    <div class="ai-visual-grid">
                        <div class="ai-score-box">
                            <div class="ai-box-title">AI 影响分拆解</div>
                            <div class="ai-score-track">
                                <div class="ai-score-explicit" style="width:${{explicitScore}}%;"></div>
                                <div class="ai-score-tooling" style="width:${{toolingScore}}%;"></div>
                            </div>
                            <div class="ai-score-row"><span>明确信号贡献</span><strong>${{explicitScore.toFixed(0)}} / 100</strong></div>
                            <div class="ai-score-row"><span>tooling 弱信号贡献</span><strong>${{toolingScore.toFixed(0)}} / 15</strong></div>
                        </div>
                        <div class="ai-chart-box">
                            <div class="ai-box-title">AI 明确信号趋势</div>
                            <div class="ai-trend-wrap">
                                <canvas id="aiTrendChart"></canvas>
                                <div class="ai-trend-empty" id="aiTrendEmpty">当前筛选范围只有 AI tooling 弱信号，暂无明确 AI commit 趋势</div>
                            </div>
                        </div>
                    </div>
                    <div class="insight-card"><strong>洞察：</strong>${{insight}}</div>`;
                renderAiTrend(agg);
            }} else {{
                document.getElementById('aiImpact').innerHTML = `
                    <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:24px;text-align:center;">
                        <div style="color:#656d76;">未检测到明显的 AI 辅助开发痕迹</div>
                    </div>
                    <div class="insight-card"><strong>洞察：</strong>你目前主要依靠手工编码，没有检测到 AI 辅助开发的痕迹。</div>`;
            }}
        }}

        // ============================================================
        // 更新建议
        // ============================================================
        function updateSuggestions(agg) {{
            const categories = {{
                'commit': {{name: '提交习惯', icon: '📝', items: []}},
                'test': {{name: '测试质量', icon: '✅', items: []}},
                'doc': {{name: '文档维护', icon: '📚', items: []}},
                'schedule': {{name: '作息健康', icon: '⏰', items: []}},
                'project': {{name: '项目管理', icon: '🎯', items: []}},
                'ai': {{name: 'AI 协作', icon: '🤖', items: []}},
            }};

            const avgDaily = agg.avgPerDay || 0;
            const aiRatio = agg.aiCommitRatio || 0;
            const hourly = agg.hourly || [];
            const totalProjects = Object.keys(agg.projectCounts).length;
            const weekdayNames = ['周日', '周一', '周二', '周三', '周四', '周五', '周六'];

            // ============================================================
            // 提交习惯 (最多 6 条)
            // ============================================================
            if (agg.habitScore.granularity < 15) categories.commit.items.push(`优化提交粒度：粒度得分仅 ${{agg.habitScore.granularity}}/40，建议保持稳定的提交频率`);
            if (avgDaily < 1) categories.commit.items.push(`提高提交频率：日均仅 ${{avgDaily.toFixed(1)}} 次提交，建议小步快跑、勤提交`);
            else if (avgDaily > 8) categories.commit.items.push(`优化提交粒度：日均 ${{avgDaily.toFixed(1)}} 次提交偏多，考虑合并相关改动`);
            if (agg.lowInfoRatio > 0.15) categories.commit.items.push(`优化 Commit Message：${{(agg.lowInfoRatio*100).toFixed(0)}}% 的提交缺少描述，建议使用 Conventional Commits 规范`);
            else if (agg.lowInfoRatio > 0.05) categories.commit.items.push('完善提交描述：部分 commit 信息过于简略，建议写清楚改动原因');
            if (agg.total > 0) {{
                const otherRatio = (agg.types.other || 0) / agg.total;
                if (otherRatio > 0.25) categories.commit.items.push(`提交分类不清：${{(otherRatio*100).toFixed(0)}}% 归为 other，建议使用 feat/fix/refactor 等标准类型`);
            }}
            if (agg.activeDays > 0 && agg.total > 0) {{
                const commitsPerActiveDay = agg.total / agg.activeDays;
                if (commitsPerActiveDay > 10) categories.commit.items.push(`控制单日提交量：活跃日均提交 ${{commitsPerActiveDay.toFixed(0)}} 次，建议拆分为更小的改动`);
            }}

            // 正面反馈
            if (agg.lowInfoRatio < 0.03) categories.commit.items.push(`Commit 质量高：${{((1-agg.lowInfoRatio)*100).toFixed(0)}}% 的提交有详细描述，继续保持！`);
            if (avgDaily >= 2 && avgDaily <= 5) categories.commit.items.push(`提交频率适中：日均 ${{avgDaily.toFixed(1)}} 次提交，节奏良好`);

            // ============================================================
            // 测试质量 (最多 5 条)
            // ============================================================
            if (agg.habitScore.testAwareness < 10) categories.test.items.push('提高测试意识：尝试为每个新功能编写测试用例，目标覆盖率 10%+');
            else if (agg.testRatio < 0.08) categories.test.items.push(`增加测试投入：当前测试文件占比仅 ${{(agg.testRatio*100).toFixed(0)}}%，建议补充单元测试`);
            if (agg.total > 50) {{
                const testRatio = (agg.types.test || 0) / agg.total;
                if (testRatio < 0.05) categories.test.items.push(`增加测试提交：测试相关提交仅占 ${{(testRatio*100).toFixed(0)}}%，建议为新功能编写测试`);
            }}
            if (agg.fixRatio > 0.20) categories.test.items.push(`提升代码质量：Bug 修复占比 ${{(agg.fixRatio*100).toFixed(0)}}%，建议加强测试和 Code Review`);

            // 正面反馈
            if (agg.testRatio >= 0.30) categories.test.items.push(`测试做得好：测试文件占比 ${{(agg.testRatio*100).toFixed(0)}}%，继续保持！`);

            // ============================================================
            // 文档维护 (最多 5 条)
            // ============================================================
            if (agg.habitScore.docAwareness < 10) categories.doc.items.push('增加文档投入：定期更新 README 和 API 文档');
            else if (agg.docRatio < 0.05) categories.doc.items.push(`完善文档：文档变更占比 ${{(agg.docRatio*100).toFixed(0)}}%，重要功能应有文档说明`);
            if (agg.total > 50) {{
                const docsRatio = (agg.types.docs || 0) / agg.total;
                if (docsRatio < 0.05) categories.doc.items.push(`增加文档提交：文档相关提交仅占 ${{(docsRatio*100).toFixed(0)}}%，建议及时更新文档`);
            }}

            // 正面反馈
            if (agg.docRatio >= 0.15) categories.doc.items.push(`文档做得好：文档变更占比 ${{(agg.docRatio*100).toFixed(0)}}%，继续保持！`);

            // ============================================================
            // 作息健康 (最多 5 条)
            // ============================================================
            if (agg.habitScore.schedule < 10) categories.schedule.items.push(`改善作息规律：作息得分仅 ${{agg.habitScore.schedule}}/20，夜间和周末提交较多`);
            if (agg.nightRatio > 0.25) categories.schedule.items.push(`注意作息健康：夜间提交占比 ${{(agg.nightRatio*100).toFixed(0)}}%，建议调整为白天工作`);
            if (agg.weekendRatio > 0.25) categories.schedule.items.push(`平衡工作生活：周末提交占比 ${{(agg.weekendRatio*100).toFixed(0)}}%，注意适当休息`);
            if (hourly.length === 24) {{
                const lateNight = hourly.slice(0, 6).reduce((a, b) => a + b, 0);
                const total = hourly.reduce((a, b) => a + b, 0);
                if (total > 0 && lateNight / total > 0.15) categories.schedule.items.push(`减少深夜编码：凌晨 0-6 点提交占比 ${{(lateNight/total*100).toFixed(0)}}%，长期熬夜影响代码质量`);
            }}
            if (agg.weekly.length === 7) {{
                const peakWeekdays = agg.weekly.map((v, i) => ({{v, i}})).sort((a, b) => b.v - a.v).slice(0, 3).map(x => weekdayNames[x.i]);
                const weekendDays = peakWeekdays.filter(d => d === '周六' || d === '周日');
                if (weekendDays.length >= 2) categories.schedule.items.push(`调整工作节奏：最活跃的 3 天中有 ${{weekendDays.length}} 天是周末，建议以工作日为主`);
            }}

            // 正面反馈
            if (agg.nightRatio < 0.15 && agg.weekendRatio < 0.15) categories.schedule.items.push('工作生活平衡：夜间和周末提交都很少，作息健康');

            // ============================================================
            // 项目管理 (最多 6 条)
            // ============================================================
            if (agg.habitScore.focus < 10) categories.project.items.push(`提升专注度：项目聚焦得分仅 ${{agg.habitScore.focus}}/15，建议减少同时维护的项目数`);
            if (agg.focusIndex < 0.60) categories.project.items.push('提高项目聚焦度：精力较分散，建议集中精力在 1-2 个核心项目上');
            if (totalProjects > 15) categories.project.items.push(`精简项目数量：同时维护 ${{totalProjects}} 个项目，建议聚焦核心项目提升效率`);
            if (totalProjects > 5 && agg.total > 0) {{
                const activeProjects = Object.values(agg.projectCounts).filter(c => c > 10).length;
                if (activeProjects <= 2) categories.project.items.push(`项目活跃度不均：${{totalProjects}} 个项目中仅 ${{activeProjects}} 个活跃，建议清理不活跃项目`);
            }}
            if (agg.refactorRatio < 0.10 && agg.featRatio > 0.50) categories.project.items.push('关注技术债：功能开发占比高但重构不足，建议定期安排重构时间');
            if (agg.total > 0) {{
                const featC = agg.types.feat || 0;
                const fixC = agg.types.fix || 0;
                const refactorC = agg.types.refactor || 0;
                const maintenance = fixC + refactorC;
                if (featC > 0 && maintenance > 0) {{
                    const ratio = featC / maintenance;
                    if (ratio > 5) categories.project.items.push(`功能远超维护：功能/维护比 ${{ratio.toFixed(1)}}:1，注意技术债积累`);
                }}
            }}

            // 正面反馈
            if (totalProjects <= 3 && agg.total > 100) categories.project.items.push(`项目聚焦度高：仅维护 ${{totalProjects}} 个项目，精力集中`);
            if (agg.refactorRatio >= 0.10) categories.project.items.push(`重构做得好：重构占比 ${{(agg.refactorRatio*100).toFixed(0)}}%，代码质量持续改善`);

            // ============================================================
            // AI 协作 (最多 4 条)
            // ============================================================
            if (aiRatio > 0.40) categories.ai.items.push('善用 AI：AI 占比超过 40%，建议仔细审查 AI 生成的代码');
            else if (aiRatio > 0 && aiRatio < 0.15) categories.ai.items.push(`探索 AI 工具：当前 AI 使用率 ${{(aiRatio*100).toFixed(0)}}%，可尝试 Copilot/Cursor 提升效率`);

            // 正面反馈
            if (aiRatio >= 0.20 && aiRatio <= 0.40) categories.ai.items.push(`AI 使用适中：AI 占比 ${{(aiRatio*100).toFixed(0)}}%，人机协作良好`);

            // ============================================================
            // 构建 HTML（带 tab 切换）
            // ============================================================
            const activeCats = Object.entries(categories).filter(([k, v]) => v.items.length > 0);
            let html = '';

            if (activeCats.length === 0) {{
                html = '<div class="sug-item"><div class="sug-text">继续保持良好的开发习惯！各项指标都很健康</div></div>';
            }} else {{
                // Tab 按钮
                html += '<div class="sug-tabs">';
                activeCats.forEach(([key, cat], i) => {{
                    const activeClass = i === 0 ? ' active' : '';
                    html += `<button class="sug-tab${{activeClass}}" data-cat="${{key}}">${{cat.icon}} ${{cat.name}} (${{cat.items.length}})</button>`;
                }});
                html += '</div>';

                // Tab 内容
                activeCats.forEach(([key, cat], i) => {{
                    const activeClass = i === 0 ? ' active' : '';
                    html += `<div class="sug-panel${{activeClass}}" data-cat="${{key}}">`;
                    cat.items.forEach((item, j) => {{
                        html += `<div class="sug-item"><div class="sug-num">${{j + 1}}</div><div class="sug-text">${{item}}</div></div>`;
                    }});
                    html += '</div>';
                }});
            }}

            document.getElementById('suggestions').innerHTML = html;

            // 绑定 tab 切换事件
            document.querySelectorAll('.sug-tab').forEach(tab => {{
                tab.addEventListener('click', () => {{
                    const cat = tab.dataset.cat;
                    document.querySelectorAll('.sug-tab').forEach(t => t.classList.remove('active'));
                    document.querySelectorAll('.sug-panel').forEach(p => p.classList.remove('active'));
                    tab.classList.add('active');
                    document.querySelector(`.sug-panel[data-cat="${{cat}}"]`).classList.add('active');
                }});
            }});
        }}

        // ============================================================
        // 主更新函数
        // ============================================================
        function updateAll(commits, project) {{
            const agg = aggregate(commits);
            agg.commits = commits;  // 保留原始数据用于图表过滤

            updateStats(agg, project);
            updatePersona(agg);
            updateHabitScore(agg);
            updateTags(agg);
            updateCharts(agg, project);
            updateInsights(agg);
            updateEngHealth(agg);
            updateRanking(agg);
            updateTypeBars(agg);
            updateAiImpact(agg);
            updateSuggestions(agg);
        }}

        // ============================================================
        // 初始化
        // ============================================================
        const initHourly = {init_hourly_json};
        const initWeekly = {init_weekly_json};
        document.getElementById('filterProject').value = 'all';
        document.getElementById('filterRange').value = 'all';
        syncDateInputsToCommits(allCommits);
        initCharts(initHourly, initWeekly, {init_type_values_json}, {init_stack_json}, {init_bubble_json}, {init_month_labels_json});
        updateAll(allCommits, 'all');
    """


def main(data_path=None, output_path=None):
    if data_path is None:
        data_path = 'data.json'
    if output_path is None:
        output_path = OUTPUT_FILE

    data_path = os.path.abspath(os.path.expanduser(data_path))
    output_path = os.path.abspath(os.path.expanduser(output_path))
    os.makedirs(os.path.dirname(output_path), exist_ok=True)

    print("📊 加载分析数据...")
    data = load_data(data_path)

    print("📝 生成报告...")
    html = generate_report(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 报告已生成: {output_path}")
    return output_path


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('data_path', nargs='?', default=None, help='数据文件路径')
    parser.add_argument('--output', default=None, help='报告输出路径')
    args = parser.parse_args()
    main(data_path=args.data_path, output_path=args.output)
