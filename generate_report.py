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
.dim-name { font-size: 0.8em; color: #656d76; margin-bottom: 6px; }
.dim-row { display: flex; align-items: center; gap: 8px; }
.dim-label { font-size: 0.8em; min-width: 52px; }
.dim-bar { flex: 1; height: 6px; background: #d8dee4; border-radius: 3px; position: relative; }
.dim-bar-fill { position: absolute; left: 0; top: 0; height: 100%; background: #0969da; border-radius: 3px; }
.dim-pct { font-size: 0.75em; color: #656d76; margin-top: 4px; }

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
.sug-item { display: flex; gap: 12px; margin-bottom: 10px; padding: 12px 14px; background: #f6f8fa; border: 1px solid #d0d7de; border-radius: 6px; }
.sug-num { width: 20px; height: 20px; background: #1a7f37; color: #fff; border-radius: 50%; display: flex; align-items: center; justify-content: center; font-size: 0.7em; font-weight: 700; flex-shrink: 0; }
.sug-text { font-size: 0.9em; color: #1f2328; }

@media (max-width: 768px) {
    .stats-row { grid-template-columns: repeat(2, 1fr); }
    .two-cols { grid-template-columns: 1fr; }
    .header h1 { font-size: 1.8em; }
    .filter-bar { flex-direction: column; align-items: stretch; }
    .eng-health-grid { grid-template-columns: 1fr; }
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
        ai_html = f'''
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:24px;text-align:center;">
            <div style="font-size:2.2em;margin-bottom:8px;">🤖</div>
            <div style="font-weight:700;font-size:1.05em;color:#1f2328;">检测到 AI 辅助开发</div>
            <div style="color:#656d76;font-size:0.85em;margin-top:4px;">发现 {ai['count']} 个 AI 工具使用信号</div>
        </div>'''
    else:
        ai_html = '''
        <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:24px;text-align:center;">
            <div style="color:#656d76;">未检测到明显的 AI 辅助开发痕迹</div>
        </div>'''

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
    html = ""
    for dim_key in dim_keys:
        dim = dims.get(dim_key, {})
        spectrum = dim.get('spectrum', 50)
        left_label = dim.get('left', '')
        right_label = dim.get('right', '')
        dim_name = dim_names[dim_key]
        is_right = spectrum > 50
        pct = spectrum if is_right else (100 - spectrum)
        left_color = '#656d76' if is_right else '#1f2328'
        left_weight = '400' if is_right else '600'
        right_color = '#1f2328' if is_right else '#656d76'
        right_weight = '600' if is_right else '400'
        align = 'right' if is_right else 'left'
        html += f'''
        <div class="dim-item">
            <div class="dim-name">{dim_name}</div>
            <div class="dim-row">
                <span class="dim-label" style="text-align:right;color:{left_color};font-weight:{left_weight};">{left_label}</span>
                <div class="dim-bar"><div class="dim-bar-fill" style="width:{spectrum}%;"></div></div>
                <span class="dim-label" style="color:{right_color};font-weight:{right_weight};">{right_label}</span>
            </div>
            <div class="dim-pct" style="text-align:{align};">{pct}%</div>
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
    suggestions = []
    if habit_score['test_awareness'] < 10:
        suggestions.append("提高测试意识：尝试为每个新功能编写测试用例")
    if habit_score['doc_awareness'] < 10:
        suggestions.append("增加文档投入：定期更新 README 和文档")
    if health['night_ratio'] > 30:
        suggestions.append("注意作息健康：夜间提交比例较高，建议调整节奏")
    if health['low_info_ratio'] > 20:
        suggestions.append("优化 Commit Message：建议使用 Conventional Commits 规范")
    if data['focus_index'] < 50:
        suggestions.append("提高项目聚焦度：建议集中精力在核心项目上")
    if not suggestions:
        suggestions.append("继续保持良好的开发习惯！")

    html = ""
    for i, s in enumerate(suggestions, 1):
        html += f'''
        <div class="sug-item">
            <div class="sug-num">{i}</div>
            <div class="sug-text">{s}</div>
        </div>'''
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
              multi_year):

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

        allCommits.forEach(c => {{
            const meta = projectMeta[c.project] || {{}};
            if (!c.language) c.language = meta.language || 'Unknown';
            c.fileChangeCount = Number(c.file_change_count ?? c.fileChangeCount ?? 0);
            c.testFiles = Number(c.test_files ?? c.testFiles ?? 0);
            c.docFiles = Number(c.doc_files ?? c.docFiles ?? 0);
            c.lowInfo = Boolean(c.low_info ?? c.lowInfo ?? false);
            c.aiSignal = Boolean(c.ai_signal ?? c.aiSignal ?? false);
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

        // 人格名称映射（核心人格）
        const CORE_PERSONA = {{
            'NS': {{name: '深夜闪电侠', icon: '⚡', desc: '凌晨两点还在敲代码，提交速度飞快，是夜晚效率之王'}},
            'NM': {{name: '午夜造物主', icon: '🌌', desc: '深夜独处时灵感爆发，从零开始构建一切，享受安静的创造'}},
            'DS': {{name: '晨曦突击手', icon: '🚀', desc: '早上开工就是一顿猛冲，快速迭代是你的核心竞争力'}},
            'DM': {{name: '日光打磨者', icon: '☀️', desc: '白天稳步推进，像匠人一样打磨每一行代码，稳健是你的代名词'}},
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
            const aiDetected = aiSignalCount >= 3;
            const aiSpectrum = aiDetected ? 100 : 0;

            const projSorted = Object.entries(projectCounts).sort((a, b) => b[1] - a[1]);
            const top3Commits = projSorted.slice(0, 3).reduce((a, b) => a + b[1], 0);
            const focusIndex = total > 0 ? top3Commits / total : 0;

            return {{
                total, hourly, weekly, monthly, types, projectCounts, languageCounts, projectActiveDays, activeDays, days,
                avgPerDay, nightRatio, dayCommits, lateCommits, weekendRatio,
                featRatio, fixRatio, refactorRatio, maintenanceRatio,
                testRatio, docRatio, lowInfoRatio, lowConfidenceRatio, confidenceCounts, engSpectrum, aiDetected, aiSignalCount, aiSpectrum,
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
            const coreKey = t + r;
            const core = CORE_PERSONA[coreKey] || {{name: '独特开发者', icon: '💻', desc: '你的开发风格独一无二'}};

            // 风格修饰语
            let styleMod = '';
            if (s === 'P') {{ styleMod = t === 'N' ? '黑客' : '创造者'; }}
            else {{ styleMod = '工匠'; }}
            // 工程修饰语
            let engMod = '';
            if (e === 'Q') {{ engMod = f === 'D' ? '全能' : '质量派'; }}
            // 组合名称
            let personaName = core.name;
            if (styleMod) personaName += ' · ' + styleMod;
            if (engMod) personaName += ' · ' + engMod;

            const descParts = [];
            descParts.push(timeSpectrum > 50 ? `夜间 ${{timeSpectrum}}%` : `白天 ${{100 - timeSpectrum}}%`);
            descParts.push(rhythmSpectrum > 50 ? `高频提交 ${{rhythmSpectrum}}%` : `深度专注 ${{100 - rhythmSpectrum}}%`);
            descParts.push(focusSpectrum > 50 ? `专注核心 ${{focusSpectrum}}%` : `多项目并行 ${{100 - focusSpectrum}}%`);
            descParts.push(styleSpectrum > 50 ? `推进新功能 ${{styleSpectrum}}%` : `维护系统 ${{100 - styleSpectrum}}%`);

            document.getElementById('personaCard').innerHTML = `
                <div style="font-size:3em;margin-bottom:8px;">${{core.icon}}</div>
                <div style="font-size:1.6em;font-weight:700;color:#1f2328;">${{personaName}}</div>
                <div style="font-size:1.1em;color:#0969da;font-weight:600;margin-top:4px;font-family:monospace;">${{personaCode}}</div>
                <div style="color:#1f2328;font-size:0.95em;margin-top:8px;font-weight:500;">${{core.desc}}</div>
                <div style="color:#656d76;font-size:0.85em;margin-top:4px;">${{descParts.join('，')}}</div>
            `;

            // 维度光谱
            const dims = [
                {{key: 'time', name: '时间偏好', spectrum: timeSpectrum, left: '白天型', right: '夜猫型'}},
                {{key: 'rhythm', name: '节奏风格', spectrum: rhythmSpectrum, left: '马拉松型', right: '冲刺型'}},
                {{key: 'focus', name: '专注程度', spectrum: focusSpectrum, left: '分散型', right: '专注型'}},
                {{key: 'style', name: '开发风格', spectrum: styleSpectrum, left: '守护型', right: '先锋型'}},
                {{key: 'engineering', name: '工程取向', spectrum: agg.engSpectrum, left: '快速迭代', right: '质量导向'}},
                {{key: 'ai', name: 'AI 协作', spectrum: agg.aiSpectrum, left: '手工型', right: 'AI 协作型'}},
            ];
            document.getElementById('dimsDetail').innerHTML = dims.map(d => {{
                const isRight = d.spectrum > 50;
                const pct = isRight ? d.spectrum : (100 - d.spectrum);
                const lc = isRight ? '#656d76' : '#1f2328';
                const lw = isRight ? '400' : '600';
                const rc = isRight ? '#1f2328' : '#656d76';
                const rw = isRight ? '600' : '400';
                const align = isRight ? 'right' : 'left';
                return `<div class="dim-item">
                    <div class="dim-name">${{d.name}}</div>
                    <div class="dim-row">
                        <span class="dim-label" style="text-align:right;color:${{lc}};font-weight:${{lw}};">${{d.left}}</span>
                        <div class="dim-bar"><div class="dim-bar-fill" style="width:${{d.spectrum}}%;"></div></div>
                        <span class="dim-label" style="color:${{rc}};font-weight:${{rw}};">${{d.right}}</span>
                    </div>
                    <div class="dim-pct" style="text-align:${{align}};">${{pct}}%</div>
                </div>`;
            }}).join('');
        }}

        // ============================================================
        // 更新 Habit Score
        // ============================================================
        function updateHabitScore(agg) {{
            const granularity = Math.round(Math.min(30, agg.avgPerDay / 4.5 * 30));
            const schedule = Math.round(Math.min(20, Math.max(0, (1 - agg.nightRatio / 0.4)) * 20));
            const focusScore = Math.round(Math.min(15, agg.focusIndex / 0.7 * 15));
            const testAwareness = Math.round(Math.min(20, agg.testRatio / 0.15 * 20));
            const docAwareness = Math.round(Math.min(15, agg.docRatio / 0.10 * 15));
            const totalScore = granularity + testAwareness + docAwareness + schedule + focusScore;
            agg.habitScore = {{totalScore, granularity, testAwareness, docAwareness, schedule, focusScore}};

            document.getElementById('statScore').textContent = totalScore;
            document.getElementById('scoreNumber').textContent = totalScore;
            document.getElementById('scoreNumber').style.color = getScoreColor(totalScore);
            document.getElementById('scoreLabel').textContent = `/ 100 · ${{getScoreLabel(totalScore)}}`;

            const scoreDims = [
                ['提交粒度', granularity, 30],
                ['测试意识', testAwareness, 20],
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

        // ============================================================
        // 更新 AI Impact
        // ============================================================
        function updateAiImpact(agg) {{
            document.getElementById('aiImpact').innerHTML = agg.aiDetected ? `
                <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:24px;text-align:center;">
                    <div style="font-size:2.2em;margin-bottom:8px;">🤖</div>
                    <div style="font-weight:700;font-size:1.05em;color:#1f2328;">检测到 AI 辅助开发</div>
                    <div style="color:#656d76;font-size:0.85em;margin-top:4px;">发现 ${{agg.aiSignalCount}} 个 AI 工具使用信号</div>
                </div>` : `
                <div style="background:#f6f8fa;border:1px solid #d0d7de;border-radius:6px;padding:24px;text-align:center;">
                    <div style="color:#656d76;">未检测到明显的 AI 辅助开发痕迹</div>
                </div>`;
        }}

        // ============================================================
        // 更新建议
        // ============================================================
        function updateSuggestions(agg) {{
            const suggestions = [];
            if (agg.habitScore.testAwareness < 10) suggestions.push('提高测试意识：尝试为每个新功能编写测试用例');
            if (agg.habitScore.docAwareness < 10) suggestions.push('增加文档投入：定期更新 README 和文档');
            if (agg.nightRatio > 0.30) suggestions.push('注意作息健康：夜间提交比例较高，建议调整节奏');
            if (agg.lowInfoRatio > 0.20) suggestions.push('优化 Commit Message：建议使用 Conventional Commits 规范');
            if (agg.focusIndex < 0.50) suggestions.push('提高项目聚焦度：建议集中精力在核心项目上');
            if (!suggestions.length) suggestions.push('继续保持良好的开发习惯！');

            document.getElementById('suggestions').innerHTML = suggestions.map((s, i) => `
                <div class="sug-item">
                    <div class="sug-num">${{i + 1}}</div>
                    <div class="sug-text">${{s}}</div>
                </div>`).join('');
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
        syncDateInputsToCommits(allCommits);
        initCharts(initHourly, initWeekly, {init_type_values_json}, {init_stack_json}, {init_bubble_json}, {init_month_labels_json});
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
