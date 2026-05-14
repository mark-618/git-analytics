# Git Analytics

本地优先的个人代码习惯分析工具。

它不会只告诉你"你提交了多少代码"，而是回答：

- 你通常什么时候写代码？
- 你是小步快跑型，还是大包提交型？
- 你是否经常半夜爆肝？
- 你在哪些项目上投入最多？
- 你的项目切换是否过度？
- 你是否重视测试、文档和重构？
- AI 工具是否改变了你的开发节奏？

## 核心特色

### 跨项目个人画像

扫描本地多个 Git 仓库，生成跨项目的个人开发画像，而不是只分析单个 repo。

### 本地隐私优先

无需 GitHub Token，不上传代码，可分析私有项目、实验项目、未发布项目。

### Developer Habit Score

从提交粒度、测试意识、文档意识、作息规律、项目聚焦度等维度生成代码习惯健康分（0-100）。

### 开发者类型标签

自动识别你的开发风格：

- 🌙 夜间爆发型：22:00 以后提交占比高
- 🏃 周末冲刺型：周末提交占比异常高
- ⚡ 小步快跑型：单次提交改动小，commit 频率高
- 📦 大包提交型：单次提交文件多、行数大
- 🚀 功能优先型：feat/fix 很多，test/docs 很少
- 🏕️ 项目游牧型：频繁在多个 repo 之间切换
- 🔧 维护型工程师：fix/refactor 占比高
- ⚠️ 测试薄弱型：测试文件变更占比低
- 🤖 AI 辅助开发型：检测到 AI 工具使用痕迹

### 行为洞察

不是统计图表，而是诊断报告：

- 24 小时热力图 + 最活跃时段分析
- 星期提交分布 + 周末工作指数
- 项目排行榜 + 聚焦度分析
- Commit 类型分布 + 质量评估
- 测试/文档/重构意识评估

## 快速开始

```bash
# 本地开发方式（默认扫描当前目录，输出到当前目录）
python3 run.py

# 指定扫描目录
python3 run.py ~/Projects

# 同时扫描多个目录
python3 run.py ~/Projects ~/Work

# 指定输出目录
python3 run.py ~/Projects --output-dir ./out

# 生成后自动打开报告，并输出分享卡片设计器
python3 run.py ~/Projects --open --share-card
```

## 安装后使用

```bash
# 从项目目录安装
pip install .

# 生成报告（默认扫描当前目录，输出到当前目录）
git-analytics

# 指定扫描目录和输出目录
git-analytics ~/Projects --output-dir ./out

# 同时扫描多个目录
git-analytics ~/Projects ~/Work --output-dir ./out

# 增加扫描深度
git-analytics ~/Projects --max-depth 5

# 生成后自动打开报告，并输出分享卡片设计器
git-analytics ~/Projects --open --share-card
```

## 输出

- `report.html` - 个人代码习惯体检报告（用浏览器打开）
- `data.json` - 原始分析数据
- `share-card.html` - PNG 分享卡片设计器（使用 `--share-card` 时生成）

默认输出到运行命令时所在的当前目录，也可以通过 `--output-dir` 指定。

## 产品定位

**GitStats 告诉你一个仓库发生了什么；Git Analytics 告诉你你是一个什么样的开发者。**

| 普通竞品 | Git Analytics |
|---------|---------------|
| 单仓库统计 | 本地多仓库个人画像 |
| commits / lines / authors | 习惯、节奏、健康度 |
| 图表展示 | 诊断报告 |
| 公开 GitHub 数据 | 私有本地项目也能分析 |
| 活动统计 | 开发者类型识别 |
| 时间分布 | 深度工作和项目切换 |
| commit 分类 | 工程习惯评估 |
| 无 AI 维度 | AI Coding Impact |

## 技术栈

- Python 3.8+
- Python 标准库（无 runtime dependencies）
- HTML/CSS/Chart.js 报告
- 本地运行，不上传代码

## License

MIT
