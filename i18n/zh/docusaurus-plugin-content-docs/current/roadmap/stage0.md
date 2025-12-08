---
id: stage0
title: "Stage 0: AI 对话与提示基础"
slug: /roadmap/stage0
sidebar_position: 1
keywords: [AI编程, 上班族, 提示工程, 办公自动化, ChatGPT, Claude]
---

import VideoEmbed from '@site/src/components/VideoEmbed';

# Stage 0: AI 对话与提示基础

**欢迎开启 AI 办公自动化之旅！**

## 为什么选择 AI 工具？

AI 工具已经改变了办公方式。无需学习复杂编程，仅需几句自然语言的描述，就能让 AI 帮你完成：
- 自动化重复的办公任务（数据清理、格式转换、文件处理）
- 生成周报、总结、邮件模板
- 处理 Excel 表格、生成 SQL 脚本
- 批量重命名文件、转换图片格式
- 创建办公小工具和脚本

<VideoEmbed
  videoId="PLKrSVuT-Dg"
  title="How to make vibe coding not suck…"
  caption="观看这个5分钟的 Fireship 介绍视频，了解 AI 编程助手的工作原理，学习实用技巧避免常见陷阱。"
  linkText="在 YouTube 观看"
  linkUrl="https://www.youtube.com/watch?v=PLKrSVuT-Dg"
  aspectRatio="16/9"
/>

## 学习成果

在这个阶段，你将学会：
- 使用 AI（ChatGPT、Claude 等）解决日常办公问题
- 通过简单的对话描述需求，获得可用的解决方案
- 理解 AI 工具的基本能力和局限
- 掌握有效的提示词（Prompt）技巧
- 不需要编程基础也能快速上手

## 为什么是"最小必要知识"？

你**不需要**：
- 学习编程语言语法
- 理解算法和数据结构
- 成为技术专家
- 花费数月学习

你**只需要**：
- 能清楚描述你的需求
- 愿意尝试和调整
- 基本的计算机操作能力
- 30 分钟到 2 小时的学习时间

## 立即开始

### 第一步：选择 AI 工具

最推荐的三个：

**1. ChatGPT（最易上手）**
- 网址：https://chat.openai.com
- 优点：界面友好，效果稳定，中文支持好
- 适合：日常办公任务、文本生成、Excel 建议

**2. Claude（最强逻辑）**
- 网址：https://claude.ai
- 优点：理解长文档，编程能力强，中文流畅
- 适合：代码编写、数据处理、复杂任务

**3. Copilot（微软生态）**
- 网址：https://copilot.microsoft.com
- 优点：免费，集成 Office，可联网搜索
- 适合：已有 Office 订阅的用户

### 第二步：学会提问

**不好的提问方式：**
> "帮我写代码"

**好的提问方式：**
> "我有一个 Excel 表格，包含员工名单（列：姓名、部门、入职日期）。我需要按部门分组，统计每个部门的人数，然后生成一个简单的汇总表。用什么方法最简单？"

**更好的方式：**
> "我有一个 Excel 表格。
> 表头：姓名、部门、入职日期、薪资
> 数据量：约 500 人
> 需求：按部门统计人数和平均薪资，输出为新的 Excel 表格或 CSV 文件
> 我不懂 Python，但愿意学习一个简单脚本。应该如何处理？"

### 第三步：尝试常见办公任务

#### 任务 1：生成周报框架
```
提示词：请为我生成一个周报模板，包含以下内容：
- 本周完成的主要工作（5-10 项）
- 遇到的问题和解决方案（2-3 项）
- 下周计划（3-5 项）
- 需要支持的事项（1-2 项）

要求：格式清晰，可直接复制到 Word 或 Email
```

#### 任务 2：清理 Excel 数据
```
提示词：我有一个 Excel 文件，内容如下：
[粘贴前几行数据]

问题：
- 有些单元格有空格
- 日期格式不统一（有"2025-01-01"和"1/1/2025"两种）
- 部分数据有重复

用简单方法如何在 Excel 中快速清理？如果需要代码，用什么语言最简单？
```

#### 任务 3：生成 SQL 脚本
```
提示词：我需要从数据库中查询员工信息。

表结构：
- 表名：employees
- 字段：id, name, department, hire_date, salary

需求：查询在 IT 部门工作，薪资超过 10000 的员工，按入职日期排序

请给我 SQL 查询语句（我可以直接在数据库工具中运行）
```

## 推荐学习资源

### 视频教程

1. **[Fireship: I built 10 web apps... with AI (in 14 minutes)](https://www.youtube.com/watch?v=UG3YC_jqPDg)**
   - *推荐理由:* 快节奏演示展示 AI 编程的可能性 - 非常适合初学者激励
   - 时长: 14 分钟

2. **[freeCodeCamp: AI-Powered Coding for Beginners](https://www.youtube.com/watch?v=X4H4MjrTvH0)**
   - *推荐理由:* 全面的初学者友好教程，涵盖 AI 辅助编程基础
   - 时长: 2 小时

3. **[Cursor IDE Tutorial for Beginners](https://www.youtube.com/watch?v=4q0ekTZqZZM)**
   - *推荐理由:* 最流行的 AI 编程编辑器的分步指南
   - 时长: 25 分钟

### AI 工具指南

4. **[GitHub Copilot Getting Started](https://docs.github.com/en/copilot/quickstart)**
   - *推荐理由:* 最易用的 AI 编程工具之一的官方文档

5. **[ChatGPT for Coding: Complete Guide](https://www.youtube.com/watch?v=jRAAaDll34Q)**
   - *推荐理由:* 学习如何有效使用 ChatGPT 进行编程问题和代码生成
   - 时长: 45 分钟

## 关键概念

### 什么是提示词（Prompt）？

提示词就是你对 AI 的指令。越清楚，结果越好。

**三要素：**
1. **背景信息** - "我是项目经理，需要..."
2. **具体需求** - "生成一个 2 小时的会议议程，包括..."
3. **期望格式** - "输出为 Markdown 表格"

### 为什么 AI 有时候失败？

- **信息不足** - AI 不知道你的确切需求
- **语言歧义** - 同一句话可能有多个理解
- **超出能力范围** - 某些任务确实需要编程或专业工具
- **幻觉（Hallucination）** - AI 有时会自信地给出错误答案

**解决方案：** 问问题、验证结果、逐步调整

## 常见问题

**Q: AI 生成的代码可以直接用吗？**
A: 通常可以，但要检查。对于简单脚本（Excel、批量处理）很可靠。对于生产系统代码，需要审查。

**Q: 免费还是付费工具更好？**
A: 免费版足够学习和日常使用。付费版主要优势是速度和无限次数。建议先用免费版。

**Q: 多久能学会日常应用？**
A: 2-3 小时就能完成基本任务。1-2 周能掌握大部分常见场景。

**Q: 会不会被 AI 替代？**
A: 不会。AI 是工具，不是替代品。真正值钱的是会**用** AI 的人。

## 下一步

完成这个阶段后，你将：
- ✓ 能用 AI 处理日常办公任务
- ✓ 理解 AI 的能力和局限
- ✓ 掌握基本的提示词技巧
- ✓ 准备好学习 **Stage 1: AI 现实与局限**

**[开始 Stage 1 →](./stage1)**

---

**需要帮助？** 查看我们的 [快速入门](/docs/intro) 或 [资源库](/resources)！
