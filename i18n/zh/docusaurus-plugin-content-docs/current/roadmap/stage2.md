---
title: "Stage 2: 上下文与架构"
sidebar_position: 3
keywords: [AI编程, 上下文, 项目架构, 提示工程, RAG]
---

import VideoEmbed from '@site/src/components/VideoEmbed';

# Stage 2: 上下文与架构

**掌握如何为 AI 提供有效上下文，获得更好的代码**

## 为什么上下文很重要？

AI 编程助手的表现完全取决于你提供的上下文。这个阶段教你如何组织项目和提示词，让 AI 发挥最大效能。

<VideoEmbed
  videoId="dJhlMn2otxA"
  title="Learn to Code using AI - ChatGPT Programming Tutorial"
  caption="这个来自 freeCodeCamp 的完整课程教你如何有效使用 AI 进行编程。学习如何提供正确的上下文、结构化提示词、利用 AI 工具构建真实应用。"
  linkText="在 YouTube 观看"
  linkUrl="https://www.youtube.com/watch?v=dJhlMn2otxA"
  aspectRatio="16/9"
/>

## 学习成果

在这个阶段，你将：
- 设计 AI 友好的项目架构
- 在提示词中提供有效上下文
- 了解 RAG（检索增强生成）技术
- 组织代码让 AI 更好理解
- 善用文档和示例

## 上下文的三个层次

### 1. 即时上下文 (Immediate Context)

**当前对话中直接提供的信息**

```
好的即时上下文示例：

"我正在开发一个 Python 脚本处理 Excel 文件。
当前代码：
[粘贴代码]

问题：运行时报错 'KeyError: 部门'
Excel 文件的列名：姓名, 部门名称, 入职日期

请帮我修复这个问题。"
```

### 2. 项目上下文 (Project Context)

**项目结构、技术栈、已有代码**

```
项目结构示例：
my-automation/
├── scripts/
│   ├── excel_processor.py
│   └── email_sender.py
├── data/
│   └── employees.xlsx
├── config.yaml
└── README.md

告诉 AI：
"这是一个 Python 自动化项目，使用 pandas 处理数据，
配置在 config.yaml 中，请按照现有代码风格..."
```

### 3. 领域上下文 (Domain Context)

**业务规则、行业术语、特定约束**

```
领域上下文示例：

"我们公司的业务规则：
- 员工分为 A/B/C 三个级别
- A 级员工年假 15 天，B 级 10 天，C 级 7 天
- 入职不满一年的按比例计算
- 每月 25 日前必须提交考勤

请根据这些规则帮我写一个年假计算函数。"
```

## 提供上下文的技巧

### 技巧 1：给 AI 角色设定

```
"你是一位经验丰富的 Python 开发者，专注于数据处理和办公自动化。
你的代码风格注重可读性和简洁性，偏好使用 pandas 和 openpyxl。
请帮我..."
```

### 技巧 2：提供示例

```
输入示例：
| 姓名 | 部门 | 销售额 |
|------|------|--------|
| 张三 | 华东 | 50000  |
| 李四 | 华南 | 30000  |

期望输出：
| 部门 | 总销售额 | 人数 | 平均销售额 |
|------|----------|------|------------|
| 华东 | 50000    | 1    | 50000      |
| 华南 | 30000    | 1    | 30000      |
```

### 技巧 3：分步骤请求

```
不要：
"帮我写一个完整的报表生成系统"

要这样：
"Step 1: 先帮我写一个读取 Excel 的函数
Step 2: 然后写一个数据清洗函数
Step 3: 最后写一个汇总统计函数"
```

### 技巧 4：说明约束条件

```
约束条件示例：

"请帮我写一个数据导出脚本，要求：
- Python 3.8 兼容
- 不能使用第三方库（只能用标准库）
- 内存占用不超过 100MB
- 处理时间不超过 5 分钟
- 支持中断恢复"
```

## 项目架构最佳实践

### 清晰的文件结构

```
推荐的项目结构：

office-automation/
├── README.md           # 项目说明（AI 首先读取）
├── requirements.txt    # 依赖列表
├── config/
│   └── settings.yaml   # 配置文件
├── src/
│   ├── __init__.py
│   ├── excel_handler.py    # Excel 处理
│   ├── email_sender.py     # 邮件发送
│   └── report_generator.py # 报表生成
├── templates/
│   └── email_template.html
├── tests/
│   └── test_excel_handler.py
└── data/
    └── .gitkeep
```

### 有意义的命名

```python
# 不好的命名
def process(d):
    return d['a'] + d['b']

# 好的命名
def calculate_total_sales(sales_record):
    """计算销售记录的总销售额"""
    return sales_record['base_sales'] + sales_record['bonus_sales']
```

### 自文档化代码

```python
# 好的文档字符串帮助 AI 理解代码意图
def generate_monthly_report(
    data_file: str,
    output_path: str,
    month: int,
    include_charts: bool = True
) -> str:
    """
    生成月度销售报告

    Args:
        data_file: 输入的 Excel 文件路径
        output_path: 输出目录
        month: 报告月份 (1-12)
        include_charts: 是否包含图表

    Returns:
        生成的报告文件路径

    Example:
        >>> generate_monthly_report('sales.xlsx', './reports', 12)
        './reports/2025-12-report.xlsx'
    """
    pass
```

## 推荐资源

### 提示工程指南

1. **[Anthropic's Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)**
   - *推荐理由:* Claude 创建者的官方有效提示技术综合指南

2. **[LangChain Prompt Engineering](https://python.langchain.com/docs/modules/model_io/prompts/)**
   - *推荐理由:* 生产应用中结构化提示的实用模式

3. **[OpenAI Cookbook: Code Generation](https://cookbook.openai.com/)**
   - *推荐理由:* 代码生成的真实示例和最佳实践

### 上下文与架构

4. **[Anthropic: Long Context Window Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips)**
   - *推荐理由:* 有效使用长上下文窗口处理整个代码库的技术

5. **[GitHub: Awesome AI Coding](https://github.com/sourcegraph/awesome-ai-coding)**
   - *推荐理由:* AI 辅助开发的工具、模式和最佳实践精选列表

6. **[Cursor Composer: Multi-File Editing Patterns](https://docs.cursor.com/context/rules-for-ai)**
   - *推荐理由:* 为多文件 AI 编辑组织项目的官方指南

### 高级技术

7. **[RAG for Code: Retrieval-Augmented Generation](https://blog.langchain.dev/code-understanding-with-langchain/)**
   - *推荐理由:* 从大型代码库提供相关上下文的技术

## 实用模板

### 任务请求模板

```markdown
## 任务描述
[清晰描述你想要实现的功能]

## 背景信息
- 项目类型：[如：Python 办公自动化]
- 技术栈：[如：pandas, openpyxl]
- 运行环境：[如：Windows 10, Python 3.9]

## 输入数据
[提供示例数据或数据结构说明]

## 预期输出
[描述期望的结果格式]

## 约束条件
[列出任何限制或要求]

## 现有代码
[如有相关代码，粘贴在此]
```

### README 模板

```markdown
# 项目名称

## 概述
[一句话描述项目用途]

## 功能
- 功能 1
- 功能 2

## 技术栈
- Python 3.9+
- pandas, openpyxl

## 安装
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## 使用方法
\`\`\`bash
python main.py --input data.xlsx --output report.xlsx
\`\`\`

## 配置
编辑 config.yaml 设置参数

## 文件结构
[简要说明主要文件]
```

## 下一步

恭喜！你已完成基础学习路线的三个阶段：

- ✓ **Stage 0**: 掌握 AI 对话与提示基础
- ✓ **Stage 1**: 理解 AI 的现实与局限
- ✓ **Stage 2**: 学会提供有效上下文

### 继续学习

- 探索 [工作流教程](/docs/workflows/) - 实际办公场景的完整解决方案
- 查看 [脚本片段库](/docs/snippets/) - 可直接复用的代码模板
- 浏览 [AI 工具指南](/docs/tools/ai-tools-comparison) - 了解更多 AI 工具

---

**需要帮助？** 查看我们的 [快速入门](/docs/intro) 或 [资源库](/resources)！
