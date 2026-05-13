#!/usr/bin/env python3
"""
Git Analytics - 个人代码习惯体检报告生成器
使用 Chart.js 生成可视化报告
"""

import json
import os

OUTPUT_FILE = "report.html"


def load_data(data_path="data.json"):
    with open(data_path, 'r', encoding='utf-8') as f:
        return json.load(f)


def get_score_color(score):
    if score >= 80: return '#10b981'
    elif score >= 60: return '#f59e0b'
    else: return '#ef4444'


def get_score_label(score):
    if score >= 80: return '优秀'
    elif score >= 60: return '良好'
    elif score >= 40: return '一般'
    else: return '需改进'


def generate_report(data):
    summary = data['summary']
    habit_score = data['habit_score']
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

    # 准备月度数据
    monthly_sorted = sorted(monthly.items())
    month_labels = [m[0] for m in monthly_sorted]
    month_values = [m[1] for m in monthly_sorted]

    # 准备项目堆叠数据（Top 7）
    top_projects = [p for p in projects if p['commits'] >= 10][:7]
    colors = ['#667eea', '#f44336', '#9c27b0', '#2196f3', '#00bcd4', '#ff9800', '#e91e63', '#795548', '#607d8b']

    stack_datasets = []
    for i, proj in enumerate(top_projects):
        proj_monthly = proj.get('monthly', {})
        proj_data = [proj_monthly.get(m, 0) for m in month_labels]
        stack_datasets.append({
            'label': proj['name'],
            'data': proj_data,
            'backgroundColor': colors[i % len(colors)]
        })

    # 其他项目
    other_projects = [p for p in projects if p['commits'] < 10]
    if other_projects:
        other_data = [0] * len(month_labels)
        for p in other_projects:
            for j, m in enumerate(month_labels):
                other_data[j] += p.get('monthly', {}).get(m, 0)
        if any(v > 0 for v in other_data):
            stack_datasets.append({'label': '其他', 'data': other_data, 'backgroundColor': '#9ca3af'})

    # 项目气泡图数据
    bubble_datasets = []
    for i, proj in enumerate(projects):
        if proj['commits'] < 5:
            continue
        points = []
        for m_idx, m in enumerate(month_labels):
            count = proj.get('monthly', {}).get(m, 0)
            if count > 0:
                points.append({'x': m_idx, 'y': count, 'r': min(max(count ** 0.5 * 2.5, 4), 30)})
        if points:
            bubble_datasets.append({
                'label': proj['name'],
                'data': points,
                'backgroundColor': f'{colors[i % len(colors)]}b3'
            })

    # Commit 类型数据
    type_labels = ['feat', 'fix', 'docs', 'test', 'refactor', 'chore', 'other']
    type_names = ['功能开发', 'Bug 修复', '文档', '测试', '重构', '构建/CI', '其他']
    type_colors = ['#667eea', '#ef4444', '#10b981', '#f59e0b', '#8b5cf6', '#6b7280', '#d1d5db']
    type_values = [commit_types.get(t, 0) for t in type_labels]

    # 语言分布（从项目数据聚合）
    lang_counter = {}
    for p in projects:
        lang = p.get('language', 'Unknown')
        lang_counter[lang] = lang_counter.get(lang, 0) + 1
    lang_labels = list(lang_counter.keys())
    lang_values = list(lang_counter.values())
    lang_colors = ['#3776ab', '#f7df1e', '#3178c6', '#ff9800', '#10b981', '#ef4444', '#8b5cf6']

    # 分数维度
    score_dims = [
        ('提交粒度', habit_score['granularity'], 30),
        ('测试意识', habit_score['test_awareness'], 20),
        ('文档意识', habit_score['doc_awareness'], 15),
        ('作息规律', habit_score['schedule'], 20),
        ('项目聚焦', habit_score['focus'], 15),
    ]

    dims_html = ""
    for name, score, max_score in score_dims:
        pct = score / max_score * 100
        color = get_score_color(pct)
        dims_html += f'''
        <div style="display:flex;align-items:center;gap:12px;margin-bottom:14px;">
            <div style="width:70px;font-size:0.9em;color:#6b7280;">{name}</div>
            <div style="flex:1;height:6px;background:#e5e7eb;border-radius:3px;overflow:hidden;">
                <div style="width:{pct}%;height:100%;background:{color};border-radius:3px;"></div>
            </div>
            <div style="width:50px;font-size:0.9em;color:#374151;text-align:right;">{score}/{max_score}</div>
        </div>'''

    # 开发者标签
    tags_html = ""
    for tag in tags:
        tags_html += f'''
        <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;padding:20px;text-align:center;">
            <div style="font-size:2em;margin-bottom:8px;">{tag['icon']}</div>
            <div style="font-weight:600;font-size:0.95em;margin-bottom:4px;">{tag['name']}</div>
            <div style="font-size:0.8em;color:#6b7280;">{tag['desc']}</div>
        </div>'''

    # 项目排行榜
    projects_html = ""
    for i, p in enumerate(projects[:8], 1):
        projects_html += f'''
        <div style="display:flex;align-items:center;gap:16px;padding:14px 0;{'border-top:1px solid #f1f5f9;' if i > 1 else ''}">
            <div style="width:28px;height:28px;background:#667eea;color:#fff;border-radius:6px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:0.85em;">{i}</div>
            <div style="flex:1;">
                <div style="font-weight:600;">{p['name']}</div>
                <div style="display:flex;gap:12px;font-size:0.8em;color:#6b7280;margin-top:2px;">
                    <span>{p['language']}</span>
                    <span>{p['active_days']} 天活跃</span>
                </div>
            </div>
            <div style="font-size:1.1em;font-weight:700;color:#667eea;">{p['commits']}</div>
        </div>'''

    # 建议
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

    sug_html = ""
    for i, s in enumerate(suggestions, 1):
        sug_html += f'''
        <div style="display:flex;gap:12px;margin-bottom:12px;padding:14px 16px;background:#f0fdf4;border-radius:10px;">
            <div style="width:22px;height:22px;background:#10b981;color:#fff;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:0.75em;font-weight:700;flex-shrink:0;">{i}</div>
            <div style="font-size:0.9em;">{s}</div>
        </div>'''

    # AI 信号
    if ai['detected']:
        ai_html = f'''
        <div style="background:linear-gradient(135deg,#ede9fe,#ddd6fe);border-radius:12px;padding:24px;text-align:center;">
            <div style="font-size:2.5em;margin-bottom:8px;">🤖</div>
            <div style="font-weight:700;font-size:1.1em;color:#5b21b6;">检测到 AI 辅助开发</div>
            <div style="color:#6b7280;font-size:0.9em;margin-top:4px;">发现 {ai['count']} 个 AI 工具使用信号</div>
        </div>'''
    else:
        ai_html = '''
        <div style="background:#f8fafc;border:1px solid #e5e7eb;border-radius:12px;padding:24px;text-align:center;">
            <div style="color:#6b7280;">未检测到明显的 AI 辅助开发痕迹</div>
        </div>'''

    # Top3 聚焦度
    top3_commits = sum(p['commits'] for p in projects[:3])
    top3_ratio = top3_commits / max(summary['total_commits'], 1) * 100

    # 月度标签简化
    month_short = [m[-2:] + '月' for m in month_labels]

    html = f'''<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Git Analytics - 代码习惯体检报告</title>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <style>
        * {{ margin: 0; padding: 0; box-sizing: border-box; }}
        body {{
            font-family: -apple-system, BlinkMacSystemFont, 'SF Pro Display', 'PingFang SC', system-ui, sans-serif;
            background: #fafafa;
            color: #1d1d1f;
            line-height: 1.6;
            padding: 60px 20px;
        }}
        .container {{ max-width: 1100px; margin: 0 auto; }}
        .header {{ text-align: center; margin-bottom: 60px; }}
        .header h1 {{ font-size: 2.8em; font-weight: 700; letter-spacing: -0.02em; margin-bottom: 10px; }}
        .header p {{ color: #86868b; font-size: 1.15em; }}
        .stats-row {{ display: grid; grid-template-columns: repeat(4, 1fr); gap: 20px; margin-bottom: 50px; }}
        .stat-card {{
            background: #fff; border-radius: 16px; padding: 28px; text-align: center;
            box-shadow: 0 1px 12px rgba(0,0,0,0.04);
        }}
        .stat-number {{
            font-size: 2.8em; font-weight: 700;
            background: linear-gradient(135deg, #667eea, #764ba2);
            -webkit-background-clip: text; -webkit-text-fill-color: transparent;
        }}
        .stat-label {{ color: #86868b; font-size: 0.9em; margin-top: 4px; }}
        .section {{ margin-bottom: 50px; }}
        .section-title {{
            font-size: 1.6em; font-weight: 600; margin-bottom: 20px;
            display: flex; align-items: center; gap: 10px;
        }}
        .card {{
            background: #fff; border-radius: 16px; padding: 28px;
            box-shadow: 0 1px 12px rgba(0,0,0,0.04); margin-bottom: 20px;
        }}
        .card h3 {{ font-size: 1.1em; font-weight: 600; margin-bottom: 18px; color: #374151; }}
        .chart-container {{ position: relative; height: 320px; }}
        .insight-card {{
            background: #f8fafc; border-left: 3px solid #667eea;
            border-radius: 0 12px 12px 0; padding: 16px 20px; margin: 18px 0 0;
            font-size: 0.92em; color: #4b5563;
        }}
        .insight-card strong {{ color: #667eea; }}
        .footer {{ text-align: center; margin-top: 60px; padding: 30px; color: #9ca3af; font-size: 0.85em; }}
        .two-cols {{ display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; }}
        @media (max-width: 768px) {{
            .stats-row {{ grid-template-columns: repeat(2, 1fr); }}
            .two-cols {{ grid-template-columns: 1fr; }}
            .header h1 {{ font-size: 2em; }}
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>代码习惯体检报告</h1>
            <p>{summary['total_projects']} 个项目 · {summary['total_commits']} 次提交 · {summary['total_active_days']} 天活跃</p>
        </div>

        <div class="stats-row">
            <div class="stat-card">
                <div class="stat-number">{habit_score['total']}</div>
                <div class="stat-label">习惯健康分</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary['total_projects']}</div>
                <div class="stat-label">项目总数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary['total_commits']}</div>
                <div class="stat-label">总提交数</div>
            </div>
            <div class="stat-card">
                <div class="stat-number">{summary['avg_commits_per_day']}</div>
                <div class="stat-label">日均提交</div>
            </div>
        </div>

        <!-- 总览 -->
        <div class="section">
            <div class="section-title">📊 总览</div>
            <div class="two-cols">
                <div class="card">
                    <h3>Developer Habit Score</h3>
                    <div style="display:flex;align-items:center;gap:30px;">
                        <div style="text-align:center;">
                            <div style="font-size:4em;font-weight:700;color:{get_score_color(habit_score['total'])};line-height:1;">{habit_score['total']}</div>
                            <div style="color:#6b7280;font-size:0.9em;margin-top:4px;">/ 100 · {get_score_label(habit_score['total'])}</div>
                        </div>
                        <div style="flex:1;">{dims_html}</div>
                    </div>
                </div>
                <div class="card">
                    <h3>你的开发者类型</h3>
                    <div style="display:grid;grid-template-columns:repeat(2,1fr);gap:10px;">{tags_html}</div>
                </div>
            </div>
        </div>

        <!-- 时间习惯 -->
        <div class="section">
            <div class="section-title">⏰ 时间习惯</div>
            <div class="card">
                <h3>24 小时提交分布</h3>
                <div class="chart-container">
                    <canvas id="hourChart"></canvas>
                </div>
                <div class="insight-card">
                    <strong>洞察：</strong>最活跃时段 {', '.join([f'{h}:00' for h in peak_hours])}。
                    {'夜间提交占比 ' + str(health['night_ratio']) + '%，属于夜间爆发型。' if health['night_ratio'] > 25 else '作息相对规律。'}
                </div>
            </div>
            <div class="card">
                <h3>星期提交分布</h3>
                <div class="chart-container" style="height:260px;">
                    <canvas id="weekChart"></canvas>
                </div>
                <div class="insight-card">
                    <strong>洞察：</strong>最活跃 {', '.join(peak_weekdays)}。
                    {'周末提交占比 ' + str(health['weekend_ratio']) + '%。' if health['weekend_ratio'] > 20 else '以工作日为主。'}
                </div>
            </div>
        </div>

        <!-- 项目投入 -->
        <div class="section">
            <div class="section-title">🎯 项目投入</div>
            <div class="card">
                <h3>每月项目投入</h3>
                <div class="chart-container" style="height:380px;">
                    <canvas id="monthlyChart"></canvas>
                </div>
                <div class="insight-card">
                    <strong>洞察：</strong>Top 3 项目占据 {top3_ratio:.0f}% 的提交。
                    {'专注度高。' if top3_ratio > 60 else '精力较分散。'}
                </div>
            </div>
            <div class="card">
                <h3>项目时间线</h3>
                <div class="chart-container" style="height:350px;">
                    <canvas id="bubbleChart"></canvas>
                </div>
            </div>
            <div class="card">
                <h3>项目排行榜</h3>
                {projects_html}
            </div>
        </div>

        <!-- 提交习惯 -->
        <div class="section">
            <div class="section-title">📝 提交习惯</div>
            <div class="two-cols">
                <div class="card">
                    <h3>Commit 类型分布</h3>
                    <div class="chart-container">
                        <canvas id="typeChart"></canvas>
                    </div>
                </div>
                <div class="card">
                    <h3>语言分布</h3>
                    <div class="chart-container">
                        <canvas id="langChart"></canvas>
                    </div>
                </div>
            </div>
            <div class="card">
                <h3>提交类型详情</h3>
                <div id="typeBars"></div>
                <div class="insight-card">
                    <strong>洞察：</strong>
                    功能开发占比 {health['feat_ratio']}%，测试 {health['test_ratio']}%，文档 {health['doc_ratio']}%。
                    {'测试投入偏低。' if health['test_ratio'] < 5 else ''}
                    {'低信息量 commit 占比 ' + str(health['low_info_ratio']) + '%。' if health['low_info_ratio'] > 15 else ''}
                </div>
            </div>
        </div>

        <!-- 工程健康 -->
        <div class="section">
            <div class="section-title">🏥 工程健康</div>
            <div class="two-cols">
                <div class="card">
                    <h3>测试意识</h3>
                    <div style="text-align:center;padding:20px 0;">
                        <div style="font-size:3.5em;font-weight:700;color:{get_score_color(health['test_ratio'] * 5)};">{health['test_ratio']}%</div>
                        <div style="color:#6b7280;margin-top:6px;">测试文件变更占比</div>
                    </div>
                    <div class="insight-card">
                        {'测试覆盖偏低，建议为每个功能编写测试。' if health['test_ratio'] < 5 else '测试意识良好。'}
                    </div>
                </div>
                <div class="card">
                    <h3>文档意识</h3>
                    <div style="text-align:center;padding:20px 0;">
                        <div style="font-size:3.5em;font-weight:700;color:{get_score_color(health['doc_ratio'] * 8)};">{health['doc_ratio']}%</div>
                        <div style="color:#6b7280;margin-top:6px;">文档文件变更占比</div>
                    </div>
                    <div class="insight-card">
                        {'文档投入不足。' if health['doc_ratio'] < 3 else '文档维护不错。'}
                    </div>
                </div>
            </div>
        </div>

        <!-- AI Impact -->
        <div class="section">
            <div class="section-title">🤖 AI Coding Impact</div>
            <div class="card">{ai_html}</div>
        </div>

        <!-- 建议 -->
        <div class="section">
            <div class="section-title">💡 改进建议</div>
            <div class="card">{sug_html}</div>
        </div>

        <div class="footer">
            <p>生成时间: {data['generated_at']}</p>
            <p style="margin-top:6px;">Git Analytics - 本地优先的个人代码习惯分析工具</p>
        </div>
    </div>

    <script>
        const chartDefaults = {{
            responsive: true,
            maintainAspectRatio: false,
            plugins: {{ legend: {{ labels: {{ padding: 14, usePointStyle: true, font: {{ size: 11 }} }} }} }}
        }};

        // 24小时分布
        new Chart(document.getElementById('hourChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps([f'{h:02d}:00' for h in range(24)])},
                datasets: [{{
                    data: {json.dumps(hourly)},
                    backgroundColor: {json.dumps([f'rgba(102,126,234,{0.2 + v/max(hourly)*0.8})' if max(hourly) > 0 else 'rgba(102,126,234,0.2)' for v in hourly])},
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

        // 星期分布
        new Chart(document.getElementById('weekChart'), {{
            type: 'bar',
            data: {{
                labels: ['周一', '周二', '周三', '周四', '周五', '周六', '周日'],
                datasets: [{{
                    data: {[weekly.get(str(i), 0) for i in range(7)]},
                    backgroundColor: ['#667eea', '#667eea', '#667eea', '#667eea', '#667eea', '#f59e0b', '#f59e0b'],
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

        // 每月堆叠图
        new Chart(document.getElementById('monthlyChart'), {{
            type: 'bar',
            data: {{
                labels: {json.dumps(month_short)},
                datasets: {json.dumps(stack_datasets)}
            }},
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

        // 项目气泡图
        new Chart(document.getElementById('bubbleChart'), {{
            type: 'bubble',
            data: {{ datasets: {json.dumps(bubble_datasets)} }},
            options: {{
                ...chartDefaults,
                plugins: {{
                    legend: {{ position: 'bottom', labels: {{ padding: 10, usePointStyle: true, font: {{ size: 10 }} }} }},
                    tooltip: {{
                        callbacks: {{
                            label: function(ctx) {{
                                const months = {json.dumps(month_short)};
                                return ctx.dataset.label + ': ' + months[ctx.parsed.x] + ' ' + ctx.parsed.y + ' 次';
                            }}
                        }}
                    }}
                }},
                scales: {{
                    x: {{
                        type: 'linear', min: -0.5, max: {len(month_labels) - 0.5},
                        ticks: {{ stepSize: 1, callback: function(val) {{ return {json.dumps(month_short)}[val] || ''; }} }},
                        grid: {{ display: false }}
                    }},
                    y: {{ beginAtZero: true, grid: {{ color: 'rgba(0,0,0,0.04)' }} }}
                }}
            }}
        }});

        // Commit 类型环形图
        new Chart(document.getElementById('typeChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(type_names)},
                datasets: [{{ data: {json.dumps(type_values)}, backgroundColor: {json.dumps(type_colors)}, borderWidth: 0 }}]
            }},
            options: {{
                ...chartDefaults,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 12, usePointStyle: true }} }} }},
                cutout: '60%'
            }}
        }});

        // 语言分布环形图
        new Chart(document.getElementById('langChart'), {{
            type: 'doughnut',
            data: {{
                labels: {json.dumps(lang_labels)},
                datasets: [{{ data: {json.dumps(lang_values)}, backgroundColor: {json.dumps(lang_colors[:len(lang_labels)])}, borderWidth: 0 }}]
            }},
            options: {{
                ...chartDefaults,
                plugins: {{ legend: {{ position: 'bottom', labels: {{ padding: 12, usePointStyle: true }} }} }},
                cutout: '60%'
            }}
        }});

        // 类型条形图
        const typeData = {json.dumps(list(zip(type_names, type_values, type_colors)))};
        const maxType = Math.max(...typeData.map(d => d[1]));
        document.getElementById('typeBars').innerHTML = typeData.map(([name, val, color]) => {{
            const pct = (val / {max(summary['total_commits'], 1)} * 100).toFixed(1);
            return `<div style="display:flex;align-items:center;gap:12px;margin-bottom:10px;">
                <div style="width:70px;font-size:0.85em;color:#6b7280;">${{name}}</div>
                <div style="flex:1;height:8px;background:#e5e7eb;border-radius:4px;overflow:hidden;">
                    <div style="width:${{pct}}%;height:100%;background:${{color}};border-radius:4px;"></div>
                </div>
                <div style="width:90px;font-size:0.85em;color:#374151;text-align:right;">${{val}} (${{pct}}%)</div>
            </div>`;
        }}).join('');
    </script>
</body>
</html>'''

    return html


def main():
    script_dir = os.path.dirname(os.path.abspath(__file__))
    data_path = os.path.join(script_dir, 'data.json')
    output_path = os.path.join(script_dir, OUTPUT_FILE)

    print("📊 加载分析数据...")
    data = load_data(data_path)

    print("📝 生成报告...")
    html = generate_report(data)

    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html)

    print(f"✅ 报告已生成: {output_path}")


if __name__ == '__main__':
    main()
