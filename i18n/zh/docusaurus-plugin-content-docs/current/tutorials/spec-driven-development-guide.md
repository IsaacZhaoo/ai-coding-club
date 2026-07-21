---
title: "用 GitHub Spec Kit 做规格驱动开发：从需求到 Spec、Plan 和 Tasks"
description: "通过 GitHub Spec Kit 实践规格驱动开发，从 Constitution、Spec、Plan、Tasks 到 Implementation 与人工审阅关卡。"
keywords:
  - 规格驱动开发
  - GitHub Spec Kit
  - Spec Kit 教程
  - Spec-Driven Development
  - AI 编程工作流
sidebar_position: 14
tags: [tutorial, agent-engineering, workflow, spec-kit]
---

# 用 GitHub Spec Kit 做规格驱动开发：从需求到 Spec、Plan 和 Tasks

**作者：有光 | 2026-07-21**

---

## 一句话没说清楚的功能需求

产品经理发来一条消息：

> "用户应该能够导出报表。"

读起来完整，甚至显得很明确。但等团队坐下来讨论，决定就一个接一个地涌出来：

- 导出哪种格式？CSV、Excel、PDF，还是三个都要？
- 谁能导出？所有用户，还是只有管理员？
- 数据量大的时候怎么办——是同步返回还是异步任务加通知？
- 文件放在哪里，本地下载还是上传到对象存储？
- 如果用户在导出进行中关掉浏览器，任务继续还是中止？

这五个问题不是实现细节，每一个都是真正的产品决策或架构决策。但代码往往在这些问题还没有明确答案时就开始写了——尤其当 Coding Agent 在场的时候，它会根据某种"合理假设"填满空白，安安静静地把一个隐藏在需求里的架构决定变成一堆已提交的代码。

等问题浮出水面，改动的代价已经不是改需求，而是改现有实现。

这就是规格驱动开发想要对付的矛盾：**不是 Agent 一定写不好代码，而是团队还没同意代码应该表达什么，实现就已经开始了。**

---

## 规格驱动开发是什么

规格驱动开发（Spec-Driven Development，SDD）的核心逻辑很简单：在写代码之前，先把需求、约束和设计决策变成可以被人类审阅和签字的关卡。只有关卡通过，才进入下一阶段。

这不是新思路——软件工程里的 Design Doc、RFC、ADR 本质上都在做类似的事。SDD 的独特之处在于把这条链和 AI Coding Agent 的工作流对接起来，让 Agent 在写代码之前先生成、等待审阅、然后执行，而不是一步到底。

GitHub Spec Kit 是一个把这条链具体化的工具。它把完整流程分成五种 Artifact：

| Artifact | 作用 | 主要审阅责任 |
|----------|------|------------|
| **Constitution** | 全局工程原则与约束（技术栈、代码风格、架构守则） | 技术负责人在项目开始时确认，之后只在重大决策变化时修改 |
| **Specification** | 单个功能的需求、验收标准、边界案例 | 产品 + 技术共同确认，重点是"做什么"和"不做什么" |
| **Plan** | 实现路径与架构决策（数据模型、接口设计、依赖选择） | 技术审阅，重点是"怎么做"以及与现有系统的关系 |
| **Tasks** | 被分解成小单元的可执行步骤列表 | 可以是人工审阅，也可以只做概览检查 |
| **Implementation** | 实际代码 | 标准 Code Review |

每一层向下移交时，都要求上一层已经经过人类确认。这是"关卡"的实质含义。

---

## 安装：官方方式与我的 Fallback

### 官方推荐安装方式

官方来源是 [`github/spec-kit`](https://github.com/github/spec-kit) 和项目内的 `spec-driven.md`。官方推荐用 `uv` 安装 `specify-cli`：

```bash
# 官方安装方式
uv tool install specify-cli
specify init
```

如果你的机器上已经装了 `uv`，这是最干净的方式，不会污染系统 Python 环境。

### 我实际用的 Fallback

我的机器上当时没有 `uv`。为了测试，我用 Python venv 手动安装了 `specify-cli==0.13.0`（写稿时的最新版本，发布于 2026-07-17）：

```bash
# ⚠️ 这是我的测试 fallback，不是推荐方式
python3 -m venv .venv
source .venv/bin/activate
pip install specify-cli==0.13.0
```

安装完成后，`specify` 命令可以正常调用。官方版本号在发布节奏较快，实际使用前建议查看 [Releases 页面](https://github.com/github/spec-kit/releases) 确认最新版本。

> **✅ 已测试**：以上安装步骤在我本机均可执行，`specify --version` 返回正常。

---

## 初始化：`specify init` 生成了什么

```bash
specify init
```

初始化时使用了 Codex + shell integration 模式。成功执行后，确认生成了以下几类内容：

```
Spec Kit scaffold
├── Constitution、Spec、Plan、Tasks 模板
├── Shell workflow scripts
├── Workflow registry metadata
└── Codex integration：十个 Spec Kit Skill
```

初始化生成了十个 Spec Kit Skill。Codex 使用 `$speckit-*` 形式调用它们，但 `$` 是调用语法，不是文件名的一部分。Workflow registry 的完整运行时行为没有直接测试。

> **✅ 已测试**：目录结构和文件均在初始化后确认存在。Skill 文件内容为官方模板，尚未针对具体项目定制。

---

## 一个小功能穿越完整流程

以下用"报表导出"这个功能串联完整工作流，说明每个阶段应该发生什么。**标注清楚哪些是我实测的，哪些是基于官方文档和模板结构的预期行为。**

---

### 第一关：Constitution（全局约束）

Constitution 是最早被确认的一层，通常在项目开始时由技术负责人填写并签字。它不针对任何单一功能，而是对整个项目有效的工程原则。

一份合理的 Constitution 会写明：

```markdown
## 技术栈
- 后端：Python 3.12 + FastAPI
- 数据库：PostgreSQL 15，ORM 使用 SQLAlchemy 2.x
- 异步任务：Celery + Redis（已有基础设施）
- 文件存储：AWS S3，本地开发使用 MinIO

## 代码原则
- 所有 API 接口必须有 OpenAPI 注释
- 数据库迁移使用 Alembic，禁止在代码中直接 ALTER TABLE
- 导出任务若预计超过 5 秒，必须走异步路径

## 禁止事项
- 禁止引入新的消息队列（如 RabbitMQ、Kafka），现有 Celery 已满足需求
```

Constitution 里的每一条，在后续的 Plan 里都会作为约束出现。这就是为什么"异步任务必须用 Celery"这个决定属于 Constitution 而不是 Plan——它是全局有效的工程原则，不是这个功能特有的选择。

> **⚠️ 未完整测试**：以上是基于模板结构写出的示例。Constitution 文件的模板字段和实际生成格式已确认，但填写并流转至下一关的全流程未在真实功能中验证。

---

### 第二关：Specification（功能规格）

回到"用户应该能够导出报表"这句话。Spec 阶段的任务是把它变成：

```markdown
## 功能名称
报表导出

## 目标用户
具有 viewer 及以上角色的已登录用户。

## 功能范围（In Scope）
- 支持 CSV 和 Excel（.xlsx）两种格式
- 按当前筛选条件导出当前报表
- 导出数据行数上限：100,000 行

## 功能范围（Out of Scope）
- PDF 格式（计划在下一版本考虑）
- 定时导出 / 邮件推送
- 跨报表合并导出

## 验收标准
1. 用户点击"导出"后，若数据量 ≤ 1,000 行，5 秒内直接下载文件
2. 数据量 > 1,000 行，显示"正在生成"提示，任务完成后在通知中心提供下载链接
3. 任务失败时，通知中心显示错误信息，不显示下载链接
4. 导出文件名格式为：`report_{report_id}_{timestamp}.{ext}`

## 边界案例
- 用户导出过程中登出：任务继续执行，下载链接仍有效（有效期 24 小时）
- 用户连续点击导出：去重，不重复创建相同参数的任务（5 分钟内）
```

注意 Spec 里最重要的部分往往是"Out of Scope"和"边界案例"。这两块明确了 Agent 不应该做什么，防止它在没人要求的情况下"贴心地"实现 PDF 导出。

**这里是第一个必须停下来的地方**：Spec 必须由产品和技术共同确认后才能进入 Plan。如果"100,000 行上限"是技术团队单方面加的，产品侧不知道，那么最终的争论会在验收时爆发。

---

### 第三关：Plan（实现计划）

Plan 的核心是架构决策。基于已确认的 Spec 和 Constitution，Plan 回答的是"怎么做"：

```markdown
## 数据模型
新增 ExportJob 表：
- id, report_id, user_id, format, status, created_at, completed_at, file_url, error_msg

## 接口设计
POST /api/v1/reports/{report_id}/export
- 请求体：{ "format": "csv" | "xlsx" }
- 响应（同步路径）：{ "status": "completed", "download_url": "..." }
- 响应（异步路径）：{ "status": "pending", "job_id": "..." }

GET /api/v1/export-jobs/{job_id}
- 查询任务状态

## 同步 / 异步判断逻辑
查询行数 ≤ 1,000：同步生成，直接返回文件流
查询行数 > 1,000：创建 Celery 任务，返回 job_id

## 依赖
- openpyxl 用于 xlsx 生成（新增依赖，需要 review）
- boto3 已有，用于 S3 上传
```

**这里是第二个必须停下来的地方**：Plan 里引入了新依赖（openpyxl），需要技术审阅。如果 Constitution 里写着"禁止引入新的文件处理库"，那么 Plan 必须被驳回，让 Agent 换一个方案。这个对话必须发生在代码写出来之前。

> **⚠️ 未测试**：以上 Plan 内容是基于已确认 Spec 和模板结构写出的示例，未在真实功能中用 `$speckit-plan` Skill 生成并流转。

---

### 第四关：Tasks（任务分解）

Plan 通过后，由 Agent 将其分解成具体可执行的任务单元：

```markdown
- [ ] T01：创建 ExportJob 数据模型，编写 Alembic 迁移文件
- [ ] T02：实现行数预查询逻辑（SELECT COUNT）
- [ ] T03：实现同步路径 CSV 生成
- [ ] T04：实现同步路径 xlsx 生成（使用 openpyxl）
- [ ] T05：实现 S3 上传工具函数
- [ ] T06：实现 Celery 任务（异步路径）
- [ ] T07：实现 POST /export 接口，含同步/异步路由判断
- [ ] T08：实现 GET /export-jobs/{job_id} 接口
- [ ] T09：实现去重逻辑（5 分钟内相同参数不重复创建）
- [ ] T10：单元测试：同步路径（< 1,000 行）
- [ ] T11：集成测试：异步路径（mock Celery）
- [ ] T12：API 文档更新（OpenAPI 注释）
```

Tasks 的分解方式本身也是一个值得审阅的决策。T01 单独列出数据库迁移，是因为 Constitution 里写了"禁止在代码中直接 ALTER TABLE"——这条约束在任务分解时被显式落地了。如果 Agent 把 T01 和 T07 合并，那条约束实际上就消失了。

**这里是第三个必须停下来的地方**：检查任务切分是否遗漏了边界案例。"登出后任务继续"（Spec 里的边界案例）在 Tasks 里没有出现——这是一个隐患，必须在这里被发现，而不是在实现后被测出来。

---

### 第五关：Implementation（代码）

只有 Tasks 经过人类确认（或至少快速过目）后，Agent 才开始逐条执行。具体状态更新与校验行为取决于当前版本；本文没有直接运行 Implementation 阶段。

最终提交的代码处于 Constitution、Spec、Plan、Tasks 的全部约束之下，Code Review 的注意力可以集中在"实现是否符合 Plan"，而不是"Plan 是否正确"——那个问题已经在第三关被解决了。

> **⚠️ 未测试**：Implementation 阶段未在真实功能中执行，以上描述基于官方文档的预期行为。

---

## 人类介入的四个关键点

把上面的流程整理成一张表：

| 关卡 | 歧义类型 | 不介入的代价 |
|------|----------|------------|
| **Spec 确认** | 功能边界、验收标准、Out of Scope | Agent 实现了产品不需要的功能，或遗漏了关键边界案例 |
| **Plan 审阅** | 架构决策、新依赖、接口设计 | 不符合架构原则的代码进入代码库，修改成本极高 |
| **Tasks 检查** | 任务切分遗漏、顺序错误 | 边界案例在实现层被遗忘，测试时才发现 |
| **需求变更** | 任何导致 Spec 变化的新输入 | 代码和 Spec 开始分叉，技术债从这一刻开始积累 |

最后一点值得单独说：**需求变更是 Spec 变更，不是代码变更**。如果产品临时说"再加个 PDF 格式"，正确的处理是回到 Spec 层重新确认，而不是让 Agent 直接加实现。这不是流程主义，而是防止"我们的 Spec 说不做 PDF，但代码里有 PDF 逻辑"这种情况出现。

---

## 常见的失败方式

在工具本身运行正常的前提下，SDD 流程通常在以下几个地方失效：

**1. Spec 写成了实现细节**

"用户点击导出按钮，系统调用 `/api/v1/export`，使用 openpyxl 生成 xlsx 文件，上传到 S3 bucket `reports-export`，返回预签名 URL。"

这是 Plan，不是 Spec。Spec 应该描述用户行为和验收结果，而不是实现路径。把两者混在 Spec 里，Plan 阶段的审阅就失去了意义。

**2. 边界案例全部推迟**

"边界案例后面再补。" 补的时机通常是测试时或者上线后。SDD 的价值之一就是强迫边界案例在 Spec 阶段被识别——哪怕写"此版本不处理"也好过完全不出现。

**3. 人类签字变成走形式**

流程有关卡，但每次确认都是"看起来没问题，过"。这让 Constitution 里的约束慢慢失去约束力，直到某一天有人提 PR 引入了 Kafka，而 Constitution 明确禁止。

**4. 需求变更绕开 Spec**

产品直接找 Agent 说"在这里加一个字段"，Agent 修改了代码，但 Spec 没有更新。一个月后，没有人能从 Spec 里还原出当前代码的真实行为。

---

## 这个流程什么时候太重

不是所有功能都适合走完整的五层流程。以下情况可以考虑只取子集：

- **一个人的项目、一次性脚本**：Constitution 和完整的 Spec 通常过重。保留 Plan（写下关键架构选择）和 Tasks（自己的 TODO 清单）即可。
- **明确的小改动**（改一个字段名、修一个 UI 样式）：直接到 Tasks 层，或者根本不需要 Spec Kit 介入。
- **探索性原型**：先写代码，跑通后再用 Spec 记录下来你做了什么决定——倒序填写也有价值。

官方工具支持按需使用各层 Skill，不强制走完整链路。比如只用 `$speckit-specify` 生成 Spec 模板而不走后续流程，也是合法的用法。

真正需要完整流程的，是这样的情况：**多人协作，决策需要留痕，未来需要修改，Agent 会生成大量代码。** 在这种情况下，每省掉一个关卡，就是在把一个将来会浮出的决定埋进代码里。

---

## 我测试了什么，没测试什么

为了诚实起见，显式列出：

| 内容 | 状态 |
|------|------|
| Python venv 安装 `specify-cli==0.13.0` | ✅ 已测试 |
| `specify init` 完整执行 | ✅ 已测试 |
| 生成目录结构与十个 Skill | ✅ 已确认存在 |
| Constitution 填写并流转至 Spec | ⚠️ 未完整测试 |
| `$speckit-specify` 生成真实 Spec | ⚠️ 未测试 |
| `$speckit-plan` 生成 Plan 并触发审阅 | ⚠️ 未测试 |
| `$speckit-tasks` 分解 Tasks | ⚠️ 未测试 |
| `$speckit-implement` 执行代码生成 | ⚠️ 未测试 |
| `workflow-registry.json` 状态跟踪完整流程 | ⚠️ 未测试 |

所以这篇文章能告诉你的是：工具能安装，初始化能运行，生成的骨架是什么样的，以及流程的设计逻辑是什么。它不能告诉你"走完整流程能节省多少时间"或者"这个工具适合你的团队"——那需要你自己在真实功能上跑一遍。

---

## 最后

"用户应该能够导出报表"这句话藏了多少决定，只有当你试图在代码里落地的时候才会知道。规格驱动开发的思路是：在代码开始之前，先把这些决定暴露出来、讨论清楚、签字确认。

GitHub Spec Kit 给这条链提供了一组具体的工具：五种 Artifact 类型、十个 Skill、一个 workflow-registry 追踪状态。工具本身安装简单，初始化顺畅。流程能不能起作用，取决于人类是否真的在每一个关卡停下来做决定——而不是把"确认"变成走形式的按钮。

这是 Spec-Driven Development 真正的赌注：不是工具有多强大，而是团队愿不愿意在写代码之前先把话说清楚。

---

**参考资料**

- [github/spec-kit](https://github.com/github/spec-kit)
- [spec-driven.md（项目内文档）](https://github.com/github/spec-kit/blob/main/spec-driven.md)
- specify-cli 最新版本：v0.13.0（2026-07-17 发布，使用前请查看 [Releases](https://github.com/github/spec-kit/releases) 确认最新版本）

## 相关指南

- [AI Code Review 工作流](/zh/docs/tutorials/ai-code-review-workflow/)
- [AGENTS.md 完整指南](/zh/docs/tutorials/agents-md-guide/)
