---
title: 文档提示词
description: 用于编写与改进技术文档的提示词模板
---

import FAQSchema from '@site/src/components/FAQSchema';

# 文档提示词模板

**让文档更清晰、与代码一致，并减少重复答疑**

<FAQSchema
  items={[
    {
      question: '如何避免文档写错？',
      answer: '提供真实代码/接口，并要求引用具体符号（函数名/字段）来写文档。',
    },
    {
      question: '最推荐的文档结构是什么？',
      answer: '先 TL;DR，再给可运行示例、配置、常见坑与排错步骤。',
    },
    {
      question: '文档里一定要包含什么？',
      answer: '至少一个可运行示例 + 一个简短 troubleshooting 段落。',
    },
  ]}
/>

---

## 1) README 段落（安装 + 用法）

```text
为这个模块写一段 README。

包含：
- TL;DR（1-2 句）
- 安装步骤
- 基础用法（可运行示例）
- 配置项
- 常见坑

模块信息：
[粘贴代码或 API]
```

## 2) Docstring / JSDoc 生成

```text
为以下代码补充 docstring/JSDoc。

规则：
- 解释输入/输出
- 提到关键边界情况
- 给一个使用示例

代码：
[粘贴代码]
```

## 3) Troubleshooting（排错指南）

```text
为这个功能写一段 troubleshooting。

包含：
- Top 5 故障模式
- 表现/症状
- 可能原因
- 修复步骤

功能描述：
[描述功能]
```

## 4) API 文档（接口/函数）

```text
为以下接口写简洁的 API 文档。

包含：
- 概述
- 参数与类型
- 示例 request/response 或用法
- 错误情况

API：
[粘贴接口]
```

## 5) Release notes / Changelog

```text
基于这份变更摘要写 release notes。

包含：
- 变更内容
- 变更原因
- 升级方式
- Breaking changes（如有）

变更摘要：
[粘贴摘要]
```

---

## FAQ

### 如何避免文档写错？

给真实代码/接口，并让 AI 引用具体符号来写说明。

### 最推荐的文档结构是什么？

TL;DR → 示例 → 配置 → 常见坑 → 排错。

### 文档里一定要包含什么？

至少一个可运行示例 + 一个简短 troubleshooting。

