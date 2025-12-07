---
title: "Stage 1: AI 现实与局限"
sidebar_position: 2
keywords: [AI编程, 局限性, 最佳实践, 幻觉, 提示工程]
---

import VideoEmbed from '@site/src/components/VideoEmbed';

# Stage 1: AI 现实与局限

**理解 AI 编程的能力边界与最佳实践**

## 为什么这个阶段很重要？

在体验了 AI 工具的神奇之后，了解它的局限性同样重要。这个阶段帮助你建立合理的预期，避免常见陷阱。

<VideoEmbed
  videoId="2FJlhoDYNPE"
  title="AI Coding Masterclass: From Beginner to Expert in 90 Minutes"
  caption="这个来自 Riley Brown 的大师课将带你从初学者到专家。学习如何写有效的提示词、理解 AI 局限、用 AI 辅助构建真实项目。"
  linkText="在 YouTube 观看"
  linkUrl="https://www.youtube.com/watch?v=2FJlhoDYNPE"
  aspectRatio="16/9"
/>

## 学习成果

在这个阶段，你将：
- 理解 AI 编程的局限
- 学会何时依赖 AI、何时依赖自己
- 识别 AI 幻觉和错误
- 掌握更好的提示技巧
- 知道 AI 何时在帮忙、何时在添乱

## AI 的优势与局限

### AI 擅长的领域

| 任务类型 | 示例 | 可靠度 |
|---------|------|--------|
| 样板代码 | 生成 CRUD 函数、表单验证 | ⭐⭐⭐⭐⭐ |
| 常见模式 | SQL 查询、正则表达式、Excel 公式 | ⭐⭐⭐⭐⭐ |
| 快速原型 | 小工具、脚本、自动化 | ⭐⭐⭐⭐ |
| 代码解释 | 阅读和解释现有代码 | ⭐⭐⭐⭐ |
| 格式转换 | JSON 到 CSV、数据清洗 | ⭐⭐⭐⭐ |

### AI 不擅长的领域

| 任务类型 | 为什么困难 | 建议做法 |
|---------|-----------|----------|
| 复杂架构设计 | 需要全局视角和业务理解 | 先自己规划，再让 AI 实现细节 |
| 新颖问题解决 | AI 依赖训练数据中的模式 | 分解问题，逐步验证 |
| 安全关键代码 | 可能有隐藏漏洞 | 人工审查+安全测试 |
| 性能优化 | 缺乏运行时上下文 | 使用 profiler，针对性优化 |
| 最新 API | 训练数据可能过时 | 查阅官方文档验证 |

## 什么是 AI 幻觉？

**幻觉 (Hallucination)** 是指 AI 自信地给出错误或虚构的信息。

### 常见幻觉类型

1. **虚构 API/函数**
   ```python
   # AI 可能生成不存在的函数
   import pandas as pd
   df.auto_clean_data()  # 这个函数不存在！
   ```

2. **过时信息**
   - 推荐已废弃的库版本
   - 使用已移除的语法
   - 引用不再存在的文档链接

3. **逻辑看似正确但有 bug**
   ```python
   # AI 生成的代码可能有边界条件问题
   def divide(a, b):
       return a / b  # 没有处理 b=0 的情况
   ```

### 如何识别幻觉

- **问 AI 来源**：让它提供参考链接，然后验证
- **交叉验证**：用搜索引擎或官方文档核实
- **运行测试**：生成的代码一定要运行测试
- **保持怀疑**：AI 越自信，越要小心验证

## 办公场景的最佳实践

### Excel/数据处理

**好的做法：**
```
✅ 给 AI 具体的数据样例（前5行）
✅ 明确说明预期输出格式
✅ 小批量测试后再处理全部数据
✅ 保留原始数据备份
```

**避免的做法：**
```
❌ 直接在原文件上运行 AI 生成的脚本
❌ 假设 AI 理解你的业务逻辑
❌ 跳过结果验证
```

### 报告/邮件生成

**好的做法：**
```
✅ 提供具体的背景信息
✅ 给出风格样例或模板
✅ 审查敏感信息后再发送
✅ 检查数据和事实的准确性
```

**避免的做法：**
```
❌ 盲目复制粘贴
❌ 包含机密信息给 AI
❌ 发送前不检查内容
```

### 代码/脚本生成

**好的做法：**
```
✅ 先在测试环境运行
✅ 理解代码在做什么（即使只是大概）
✅ 添加错误处理和日志
✅ 版本控制（可以回滚）
```

**避免的做法：**
```
❌ 在生产环境直接运行
❌ 运行不理解的代码
❌ 忽略错误信息
```

## 推荐资源

### 理解 AI 编程局限

1. **[Andrej Karpathy on AI Coding](https://twitter.com/karpathy/status/1748863275736449258)**
   - *推荐理由:* 来自顶级 AI 研究者的直接见解，关于 AI 编程助手的真实能力和局限

2. **[Simon Willison: Things I learned about LLMs](https://simonwillison.net/2023/Aug/3/weird-world-of-llms/)**
   - *推荐理由:* 来自每天使用 LLM 编程的人的实践经验

3. **[The False Promise of AI Coding Assistants](https://stackoverflow.blog/2024/06/10/generative-ai-is-not-going-to-build-your-engineering-team-for-you/)**
   - *推荐理由:* Stack Overflow 关于 AI 能否替代软件开发的现实视角

### 最佳实践

4. **[GitHub Copilot Best Practices](https://github.blog/developer-skills/github/how-to-write-better-prompts-for-github-copilot/)**
   - *推荐理由:* 来自 GitHub 的官方有效 AI 编程实践指南

5. **[OpenAI's Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)**
   - *推荐理由:* 从 AI 模型获得更好结果的基础技术

### 批判性思维

6. **[The Danger of Trusting AI Code Blindly](https://blog.humphd.org/chasing-the-bear/)**
   - *推荐理由:* 关于盲目接受 AI 生成代码风险的真实案例研究

7. **[Testing AI-Generated Code](https://martinfowler.com/articles/exploring-gen-ai.html)**
   - *推荐理由:* Martin Fowler 关于验证 AI 生成代码的见解

## 实用检查清单

### 使用 AI 生成代码前

- [ ] 我清楚地描述了需求吗？
- [ ] 我提供了足够的上下文吗？
- [ ] 我知道预期输出是什么吗？

### 收到 AI 输出后

- [ ] 代码能运行吗？
- [ ] 有没有明显的错误或 bug？
- [ ] 是否处理了边界情况？
- [ ] 我理解代码在做什么吗？

### 准备使用/部署前

- [ ] 在测试数据上验证了吗？
- [ ] 有备份/回滚方案吗？
- [ ] 敏感信息安全吗？

## 下一步

完成这个阶段后，你将：
- ✓ 能识别 AI 的优势和局限
- ✓ 知道如何验证 AI 输出
- ✓ 掌握办公场景的最佳实践
- ✓ 准备好学习 **Stage 2: 上下文与架构**

**[开始 Stage 2 →](./stage2)**

---

**需要帮助？** 查看我们的 [快速入门](/docs/intro) 或 [资源库](/resources)！
