# Git Analytics

[![CI](https://github.com/mark-618/git-analytics/actions/workflows/ci.yml/badge.svg)](https://github.com/mark-618/git-analytics/actions/workflows/ci.yml)

**扫描本地 Git 仓库，生成你的开发者人格画像和代码习惯体检报告。**

不只统计 commits 和 lines——它告诉你：你是什么类型的开发者，你的代码习惯健康吗。

## 安装

```bash
pip install git-analytics-cli
```

> **Package name vs command name**: PyPI package name is `git-analytics-cli`, CLI command is `git-analytics`.

## 30 秒快速开始

```bash
# 运行交互式向导，选目录、选参数，一键出报告
git-analytics

# 或者直接指定扫描目录
git-analytics ~/Projects
```

向导会引导你选择扫描目录、扫描深度、输出目录等，不需要记任何参数。

## Interactive Wizard

运行 `git-analytics` 不带参数时，会启动交互式向导：

1. 选择扫描目录（当前目录、Desktop、Projects 等）
2. 选择扫描深度（3 或 5）
3. 输入输出目录
4. 是否自动打开报告
5. 是否生成分享卡片设计器

向导会显示配置摘要，确认后开始扫描。输入 `q` 可随时退出。

## CLI 用法

```bash
# 交互式向导（默认）
git-analytics

# 扫描指定目录
git-analytics ~/Projects

# 同时扫描多个目录
git-analytics ~/Projects ~/Work ~/Side-projects

# 关闭向导，适合脚本 / CI
git-analytics --no-wizard

# 指定输出目录 + 自动打开报告 + 生成分享卡片设计器
git-analytics ~/Projects --output-dir ./out --open --share-card

# 限定时间范围
git-analytics ~/Projects --since 2024-01-01 --until 2024-12-31

# 只分析特定项目（模糊匹配）
git-analytics ~/Projects --project my-app

# 增加扫描深度（默认 3）
git-analytics ~/Projects --max-depth 5
```

### 参数一览

| 参数 | 说明 |
|------|------|
| `scan_dir` | 扫描目录，可传多个（默认当前目录） |
| `--no-wizard` | 关闭交互式向导 |
| `--output-dir` | 输出目录（默认当前目录） |
| `--max-depth` | 扫描目录深度（默认 3） |
| `--since` / `--until` | 时间范围过滤 |
| `--project` | 只分析指定项目（模糊匹配） |
| `--open` | 生成后自动打开报告 |
| `--share-card` | 同时输出分享卡片设计器 HTML |

## 输出文件

| 文件 | 说明 |
|------|------|
| `report.html` | 代码习惯体检报告，用浏览器打开 |
| `data.json` | 原始分析数据（JSON） |
| `share-card.html` | 分享卡片设计器（使用 `--share-card` 时生成） |

## 它分析什么

- **开发者人格**：6 维度光谱分类（时间偏好、节奏风格、专注程度、开发风格、工程取向、AI 协作）
- **习惯健康分**：0-100 分，覆盖提交粒度、测试意识、文档意识、作息规律、项目聚焦度
- **时间习惯**：24 小时热力图、最活跃时段、周末工作指数
- **工程健康**：测试覆盖、文档投入、commit 类型分布、低信息量 commit 占比
- **AI 使用痕迹**：检测 commit 中的 AI 工具信号（Claude、Copilot、Cursor 等）
- **项目聚焦度**：Top 3 项目占比、多项目切换分析

## 本地隐私

- **完全本地运行**，不上传任何代码或数据
- 不需要 GitHub Token
- 可分析私有项目、实验项目、未发布项目
- 所有数据只存在你的电脑上

## 分享卡片

运行 `git-analytics --share-card` 生成 `share-card.html`，浏览器打开后可预览、选主题、导出 PNG。

也可以命令行直接生成 PNG：

```bash
python3 -m gen_share_card --data data.json --output card.png
```

## 为什么不是全盘扫描

默认只扫描你指定的目录，不会遍历整个磁盘。原因：

1. 安全：避免意外扫描包含敏感数据的目录
2. 性能：全盘扫描耗时太长
3. 聚焦：你只关心自己的项目目录

## FAQ

### 扫描不到仓库？

- 确认目录下有 `.git` 文件夹
- 增加 `--max-depth`（默认 3，可以试 5）
- 检查目录路径是否正确

### 报告打不开？

- 用浏览器直接打开 `report.html` 文件
- 确保文件有读取权限
- 检查文件大小是否为 0（可能扫描没找到数据）

### 如何扫多个目录？

```bash
git-analytics ~/Projects ~/Work ~/Code
```

多个目录直接用空格分隔。

### 和 GitStats 有什么区别？

GitStats 告诉你一个仓库发生了什么；Git Analytics 告诉你你是一个什么样的开发者。

## 技术栈

- Python 3.8+
- Pillow（分享卡片 PNG 生成）
- Chart.js 可视化报告
- 本地运行，不上传任何数据

## License

MIT
