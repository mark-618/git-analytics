#!/bin/bash
# Git Analytics - 数据收集脚本
# 用法: ./collect_data.sh [项目目录]

set -e

# 默认扫描桌面所有项目
SCAN_DIR="${1:-$HOME/Desktop}"
OUTPUT_DIR="$(cd "$(dirname "$0")" && pwd)"
DATA_FILE="$OUTPUT_DIR/data.json"

echo "🔍 扫描目录: $SCAN_DIR"
echo "📁 输出目录: $OUTPUT_DIR"

# 收集所有 git 仓库
repos=()
for dir in "$SCAN_DIR"/*/; do
    if [ -d "$dir/.git" ]; then
        repos+=("$dir")
    fi
done

echo "📊 找到 ${#repos[@]} 个 Git 项目"

# 开始生成 JSON
echo "{" > "$DATA_FILE"
echo '  "generated_at": "'$(date -u +"%Y-%m-%dT%H:%M:%SZ")'",' >> "$DATA_FILE"
echo '  "scan_dir": "'$SCAN_DIR'",' >> "$DATA_FILE"
echo '  "projects": [' >> "$DATA_FILE"

first=true
total_commits=0
total_active_days=0

for repo in "${repos[@]}"; do
    repo_name=$(basename "$repo")
    cd "$repo"

    echo "  📦 处理: $repo_name"

    # 基本统计
    commit_count=$(git rev-list --count HEAD 2>/dev/null || echo "0")
    first_commit=$(git log --reverse --format="%ad" --date=format:"%Y-%m-%d" -1 2>/dev/null || echo "")
    last_commit=$(git log --format="%ad" --date=format:"%Y-%m-%d" -1 2>/dev/null || echo "")
    active_days=$(git log --format="%ad" --date=format:"%Y-%m-%d" --since="2025-01-01" 2>/dev/null | sort -u | wc -l | tr -d ' ')

    total_commits=$((total_commits + commit_count))
    total_active_days=$((total_active_days + active_days))

    # 主要语言
    main_lang=""
    py_count=$(find . -name "*.py" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
    js_count=$(find . -name "*.js" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
    ts_count=$(find . -name "*.ts" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')
    rs_count=$(find . -name "*.rs" -not -path "./.git/*" 2>/dev/null | wc -l | tr -d ' ')

    if [ "$py_count" -gt "$js_count" ] && [ "$py_count" -gt "$ts_count" ] && [ "$py_count" -gt "$rs_count" ]; then
        main_lang="Python"
    elif [ "$js_count" -gt "$ts_count" ]; then
        main_lang="JavaScript"
    elif [ "$ts_count" -gt 0 ]; then
        main_lang="TypeScript"
    elif [ "$rs_count" -gt 0 ]; then
        main_lang="Rust"
    else
        main_lang="Other"
    fi

    # 提交类型统计
    feat_count=$(git log --format="%s" --since="2025-01-01" 2>/dev/null | grep -ciE "(feat|feature|add|新增|添加)" 2>/dev/null | tr -d '\n' || echo "0")
    fix_count=$(git log --format="%s" --since="2025-01-01" 2>/dev/null | grep -ciE "(fix|bug|修复|bugfix)" 2>/dev/null | tr -d '\n' || echo "0")
    docs_count=$(git log --format="%s" --since="2025-01-01" 2>/dev/null | grep -ciE "(doc|文档|readme)" 2>/dev/null | tr -d '\n' || echo "0")
    test_count=$(git log --format="%s" --since="2025-01-01" 2>/dev/null | grep -ciE "(test|测试|spec)" 2>/dev/null | tr -d '\n' || echo "0")
    refactor_count=$(git log --format="%s" --since="2025-01-01" 2>/dev/null | grep -ciE "(refactor|重构|优化|perf)" 2>/dev/null | tr -d '\n' || echo "0")

    # 每月提交分布
    monthly_json="{"
    monthly_first=true
    for month_data in $(git log --format="%ad" --date=format:"%Y-%m" --since="2025-01-01" 2>/dev/null | sort | uniq -c | awk '{print $2":"$1}'); do
        if [ "$monthly_first" = true ]; then
            monthly_first=false
        else
            monthly_json+=","
        fi
        monthly_json+="\"${month_data%%:*}\":${month_data##*:}"
    done
    monthly_json+="}"

    # 每小时提交分布
    hourly_json="["
    for h in $(seq 0 23); do
        hour_str=$(printf "%02d" $h)
        count=$(git log --format="%ad" --date=format:"%H" --since="2025-01-01" 2>/dev/null | awk -v h="$hour_str" 'BEGIN{c=0} $1==h{c++} END{print c}')
        if [ "$h" -gt 0 ]; then
            hourly_json+=","
        fi
        hourly_json+="$count"
    done
    hourly_json+="]"

    # 每周提交分布
    weekly_json="{"
    weekly_first=true
    for day_data in $(git log --format="%ad" --date=format:"%u:%A" --since="2025-01-01" 2>/dev/null | sort | uniq -c | awk '{print $2":"$1}'); do
        if [ "$weekly_first" = true ]; then
            weekly_first=false
        else
            weekly_json+=","
        fi
        weekly_json+="\"${day_data%%:*}\":${day_data##*:}"
    done
    weekly_json+="}"

    # 输出 JSON
    if [ "$first" = true ]; then
        first=false
    else
        echo "    ," >> "$DATA_FILE"
    fi

    cat >> "$DATA_FILE" << EOF
    {
      "name": "$repo_name",
      "commits": $commit_count,
      "first_commit": "$first_commit",
      "last_commit": "$last_commit",
      "active_days": $active_days,
      "main_language": "$main_lang",
      "commit_types": {
        "feat": $feat_count,
        "fix": $fix_count,
        "docs": $docs_count,
        "test": $test_count,
        "refactor": $refactor_count
      },
      "monthly": $monthly_json,
      "hourly": $hourly_json,
      "weekly": $weekly_json
    }
EOF
done

echo '  ],' >> "$DATA_FILE"
echo '  "summary": {' >> "$DATA_FILE"
echo '    "total_projects": '${#repos[@]}',' >> "$DATA_FILE"
echo '    "total_commits": '$total_commits',' >> "$DATA_FILE"
echo '    "total_active_days": '$total_active_days >> "$DATA_FILE"
echo '  }' >> "$DATA_FILE"
echo '}' >> "$DATA_FILE"

echo ""
echo "✅ 数据收集完成!"
echo "📊 总计: ${#repos[@]} 个项目, $total_commits 次提交"
echo "📁 数据文件: $DATA_FILE"
