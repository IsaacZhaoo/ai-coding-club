---
id: cline-prompts
title: Cline 系统提示词深度解析
sidebar_label: Cline 提示词分析
description: 深入剖析 Cline 开源 AI 编程助手的系统提示词设计,学习其用户审批工作流和安全优先的架构
---

import FAQSchema from '@site/src/components/FAQSchema';

# Cline 系统提示词深度解析

> 理解 Cline 如何通过开源透明和强制审批机制实现安全可控的 AI 协作

Cline 是一款开源的 VSCode 集成 AI 编程助手。与其他工具不同,Cline 强调**逐步执行**和**强制用户审批**,每个操作都需要用户确认。本文通过分析其系统提示词,揭示这一开源工具如何平衡自动化与用户控制。

<FAQSchema
  items={[
    {
      question: '为什么要分析 Cline 的系统提示词？',
      answer: '可以学习强审批与透明机制如何降低 AI 协作风险。',
    },
    {
      question: '与 Cursor 或 Claude Code 最大差异是什么？',
      answer: 'Cline 强调强制用户审批与慢速可控执行。',
    },
    {
      question: '如何把这些理念用到自己的流程？',
      answer: '设置明确的审批门槛，关键改动分步执行并验证。',
    },
  ]}
/>

**学习目标**:
- 理解 Cline 的用户审批优先设计哲学
- 掌握 6 个关键提示词模式
- 学会将安全审批机制应用到自己的 AI 工具开发

---

## 核心设计哲学

### 1. 强制审批的迭代执行 (Mandatory Confirmation)

**设计理念**: 每一步都需要用户确认,防止 AI 失控

**核心指令**:
> "You use tools step-by-step to accomplish a given task, with each tool use informed by the result of the previous tool use"
> "ALWAYS wait for user confirmation after each tool use before proceeding"

**这是 Cline 的核心特征** - 与其他自主执行的 AI 助手完全不同。

**工作流示例**:
```
1. Cline 提议使用工具 → 用户在 VSCode 中看到请求
2. 用户批准/拒绝 → 工具执行(或不执行)
3. 用户收到结果 → 结果发送回 Cline
4. Cline 分析结果 → 提议下一个操作
5. 重复直到任务完成
```

**关键安全机制**:
```
不能使用 attempt_completion,直到:
- 已从用户确认之前的工具使用成功
- 检查 <thinking> 标签: "我是否已确认用户之前的工具使用成功?"

违反将导致: "代码损坏和系统故障"
```

**为什么重要?**
- **防止失控**: AI 不能连续执行多个操作而不检查
- **可见性**: 用户看到每个操作的意图和结果
- **控制权**: 用户可以在任何时候介入和纠正

**如何应用?**
```markdown
安全审批模式:
1. 提议操作前,在 <thinking> 中验证参数
2. 等待用户确认
3. 执行并报告结果
4. 确认成功后再继续
```

---

### 2. 单工具原则 (One Tool Per Message)

**设计理念**: 一次消息只使用一个工具

**核心约束**:
> "You can use one tool per message"

**为什么这样设计?**
1. **强制慎重**: 每个操作都是独立、可审查的单元
2. **防止批量错误**: 不能一次性执行多个可能失败的操作
3. **清晰责任**: 每个操作的结果明确归因

**对比其他工具**:
- ❌ Claude Code: 允许并行调用多个工具
- ❌ Cursor: 批量执行独立操作
- ✅ Cline: 严格的单工具限制

**权衡**:
- ✅ 更安全、更可控
- ❌ 更慢、需要更多轮交互

**如何应用?**
```markdown
操作分解原则:
- 将复杂任务分解为单一工具步骤
- 每步验证成功后再进行下一步
- 接受较慢的速度换取更高的安全性
```

---

### 3. 任务导向,非对话式 (Task-Focused, Not Conversational)

**设计理念**: 直达目标,不闲聊

**核心指令**:
> "Your goal is to try to accomplish the user's task, NOT engage in a back and forth conversation"
> "STRICTLY FORBIDDEN from starting messages with 'Great', 'Certainly', 'Okay', 'Sure'"

**对比传统 AI**:
```
❌ ChatGPT 风格:
"Certainly! I'd be happy to help you with that. Let me start by..."

✅ Cline 风格:
<read_file><path>src/auth.ts</path></read_file>
```

**为什么这样设计?**
- **效率优先**: 不浪费 tokens 在客套话上
- **行动导向**: 用户要的是结果,不是对话
- **减少噪音**: 保持输出简洁清晰

**如何应用?**
```markdown
沟通原则:
- 直接行动,不解释意图
- 禁止: "好的", "当然", "没问题"
- 只在需要信息时提问
- 完成后简短报告结果
```

---

### 4. 安全默认的文件操作 (Safe File Operations)

**设计理念**: 优先使用精确编辑,避免完全覆写

**工具选择逻辑**:
```
默认: replace_in_file (定向编辑 - 更安全、更精确)
仅当: write_to_file (创建新文件或必须完全重写)
```

**`replace_in_file` 特性**:
- 使用 Git 风格的冲突标记: `<<<<<<< SEARCH` / `=======` / `>>>>>>> REPLACE`
- **逐字符匹配**: "SEARCH content must match...character-for-character including whitespace"
- **完整行**: "Each line must be complete. Never truncate lines mid-way"

**自动格式化感知**:
```
关键: 编辑后,编辑器可能自动格式化文件
工具响应会包含: "the final state of the file after any auto-formatting"

格式化示例:
- 行分隔符调整
- 缩进修改
- 引号样式统一
- 导入语句排序
- 尾随逗号
```

**为什么重要?**
- **防止意外覆写**: 完整重写文件风险更高
- **精确修改**: 只改变需要改变的部分
- **可审查**: 小范围修改更容易验证

**如何应用?**
```markdown
文件修改策略:
1. 默认使用 replace_in_file
2. 将大修改分解为多个小块
3. 每块必须逐字符匹配(包括空白)
4. 考虑自动格式化的影响
```

---

### 5. 强制思考标签 (Required Thinking Tags)

**设计理念**: 调用工具前必须在 `<thinking>` 标签中分析

**核心指令**:
> "Before calling a tool, do some analysis within <thinking></thinking> tags"

**必须验证**:
```
检查清单:
- [ ] 用户是否直接提供了所有必需参数?
- [ ] 能否从上下文推断参数值?
- [ ] 如果缺少参数,必须询问用户

禁止: 使用缺失参数调用工具
```

**示例思考过程**:
```xml
<thinking>
用户要求读取 auth.ts 文件
- path 参数: 用户提到 "auth.ts"
- 需要完整路径: src/auth.ts (从环境详情推断)
- 所有参数就绪,可以调用工具
</thinking>

<read_file>
<path>src/auth.ts</path>
</read_file>
```

**为什么重要?**
- **防止盲目执行**: 强制 AI 验证参数
- **减少错误**: 提前发现缺失信息
- **可调试**: 思考过程可见,便于理解 AI 决策

**如何应用?**
```markdown
工具调用前检查:
1. 在 <thinking> 中列出所有参数
2. 验证每个参数的来源
3. 如果缺失,询问用户而非猜测
4. 确认后再调用工具
```

---

## 六大关键提示词模式

### 模式 1: 双模式架构 (PLAN vs ACT)

**核心机制**: 分离规划和执行阶段

**PLAN 模式**:
```
工具: plan_mode_respond
功能: 协作规划,不修改文件
用途: 收集上下文 → 设计架构 → 获得批准
```

**ACT 模式**:
```
工具: 完整工具集(11 个核心工具)
功能: 执行实际修改
用途: 实施已批准的计划
```

**典型工作流**:
```
1. PLAN 模式:
   - 收集上下文(文件列表、代码定义)
   - 架构设计
   - 提出实施计划
   - 用户批准计划

2. 切换到 ACT 模式

3. ACT 模式:
   - 逐步实施计划
   - 每步等待确认
   - 完成后报告
```

**为什么重要?**
- **分离关注点**: 思考与行动分开
- **早期验证**: 在编码前验证方向
- **防止浪费**: 避免实施错误方案

**实战案例**:

**场景**: 用户要求"添加身份验证功能"

**PLAN 模式对话**:
```
Cline: [收集上下文]
   - 检查现有 auth 相关文件
   - 列出代码定义
   - 搜索现有身份验证模式

Cline: [提出计划]
   建议实施:
   1. 创建 src/auth/middleware.ts
   2. 更新 src/server.ts 添加中间件
   3. 添加测试
   4. 更新 .env.example

   是否批准此计划?

用户: 批准,但将中间件放在 src/middleware/auth.ts

Cline: 理解,已更新计划
```

**切换到 ACT 模式后**:
```
Cline: [步骤 1]
<write_to_file>
<path>src/middleware/auth.ts</path>
<content>...</content>
</write_to_file>

[等待用户确认]
```

**如何应用?**
```markdown
双模式工作流:
1. 复杂任务从 PLAN 模式开始
2. 使用 plan_mode_respond 展示方案
3. 获得批准后切换到 ACT
4. ACT 模式逐步执行
```

---

### 模式 2: 渐进式上下文收集 (Progressive Context Gathering)

**设计理念**: 从概览到细节,按需加载上下文

**上下文收集层次**:

**层次 1: 文件结构概览** (自动注入)
```
environment_details 包含:
- 递归文件列表
- 当前工作目录
- 活动终端
```

**层次 2: 代码结构** (按需)
```
工具: list_code_definition_names
用途: 获取类/函数/方法签名
示例输出:
  src/auth.ts:
    - class AuthService
    - function validateToken
    - function refreshToken
```

**层次 3: 模式搜索** (按需)
```
工具: search_files
用途: 在代码库中查找模式
示例: search_files("token validation")
```

**层次 4: 深度分析** (仅在必要时)
```
工具: read_file
用途: 读取完整文件内容
原则: 只读取需要深度分析的特定文件
```

**为什么重要?**
- **Token 效率**: 不一次性加载所有内容
- **相关性**: 只加载任务相关的上下文
- **渐进式**: 从粗到细,按需深入

**实战示例**:

**任务**: "优化数据库查询"

```
步骤 1: 检查文件结构
→ 发现 src/db/ 目录

步骤 2: 列出代码定义
list_code_definition_names(src/db/)
→ 发现 queryUser, queryPosts, etc.

步骤 3: 搜索慢查询模式
search_files("SELECT.*JOIN")
→ 找到 5 个可能的慢查询

步骤 4: 只读取包含慢查询的文件
read_file("src/db/posts.ts")
→ 深度分析特定查询
```

**如何应用?**
```markdown
上下文收集策略:
1. 始于全局概览(environment_details)
2. 使用 list_code_definition_names 获取结构
3. 使用 search_files 定位相关代码
4. 使用 read_file 仅读取必要文件
```

---

### 模式 3: 审批分层 (Approval Stratification)

**设计理念**: 根据风险级别分层审批

**`execute_command` 的 `requires_approval` 参数**:

**需要审批 (true)**:
```
高风险操作:
✓ 安装包 (npm install, pip install)
✓ 删除文件 (rm, git rm)
✓ 系统配置更改 (chmod, systemctl)
✓ 网络操作 (curl, wget)
```

**无需审批 (false)**:
```
低风险操作:
✓ 读取文件 (cat, less)
✓ 运行开发服务器 (npm run dev)
✓ 构建项目 (npm run build)
✓ 运行测试 (npm test)
```

**自动批准模式**:
```
用户可以启用"自动批准模式":
- 只对 requires_approval: false 的操作有效
- 高风险操作仍需手动批准
- 平衡速度和安全
```

**实战案例**:

**场景**: 添加新依赖并测试

```
步骤 1: 安装包 (需要审批)
<execute_command>
<command>npm install axios</command>
<requires_approval>true</requires_approval>
</execute_command>

[Cline 等待用户批准]
用户: 批准
[执行安装]

步骤 2: 运行测试 (无需审批)
<execute_command>
<command>npm test</command>
<requires_approval>false</requires_approval>
</execute_command>

[如果启用自动批准,立即执行]
```

**如何应用?**
```markdown
审批策略设计:
1. 分类操作风险级别
2. 高风险 → 强制审批
3. 低风险 → 可选自动批准
4. 明确告知用户操作影响
```

---

### 模式 4: 搜索/替换块系统 (Search/Replace Block System)

**设计理念**: 使用严格匹配的块系统进行精确编辑

**格式**: Git 风格冲突标记
```
<<<<<<< SEARCH
要替换的确切内容
(必须逐字符匹配,包括空白)
=======
新内容
>>>>>>> REPLACE
```

**关键规则**:

**1. 逐字符匹配**:
```
❌ 错误: 忽略空白差异
function foo(){
    return 42;
}

✅ 正确: 精确匹配缩进
function foo() {
  return 42;
}
```

**2. 完整行**:
```
❌ 错误: 截断行
<<<<<<< SEARCH
function processUser(user
=======

✅ 正确: 完整行
<<<<<<< SEARCH
function processUser(user) {
=======
```

**3. 小块策略**:
```
大修改分解为多个小块:

块 1: 修改函数签名
块 2: 修改函数体第一部分
块 3: 修改函数体第二部分
```

**为什么重要?**
- **防止部分匹配**: 避免意外替换
- **可验证**: 小块更容易审查
- **容错性**: 一个块失败不影响其他块

**实战示例**:

**任务**: 更新 API 端点

❌ **错误方式** (大块,可能失败):
```
<<<<<<< SEARCH
[整个 50 行函数]
=======
[修改后的 50 行函数]
>>>>>>> REPLACE
```

✅ **正确方式** (小块,精确):
```
块 1: 更新导入
<<<<<<< SEARCH
import { Request } from 'express';
=======
import { Request, Response } from 'express';
>>>>>>> REPLACE

块 2: 更新函数签名
<<<<<<< SEARCH
export async function handleUser(req: Request) {
=======
export async function handleUser(req: Request, res: Response) {
>>>>>>> REPLACE

块 3: 添加错误处理
<<<<<<< SEARCH
  const user = await getUser(req.params.id);
  return user;
=======
  try {
    const user = await getUser(req.params.id);
    return user;
  } catch (error) {
    res.status(500).json({ error: 'Failed to fetch user' });
  }
>>>>>>> REPLACE
```

**如何应用?**
```markdown
搜索/替换最佳实践:
1. 将大修改分解为小块
2. 每块必须逐字符匹配
3. 包含完整行,不截断
4. 一次一个块,验证成功后继续
```

---

### 模式 5: 任务交接 (Task Handoff)

**设计理念**: 为长期项目创建上下文边界

**`new_task` 工具**:
```
功能: 创建新对话线程并预加载上下文
用途: 防止上下文窗口耗尽
```

**必需上下文**:
```
1. 已完成的工作
2. 具体的下一步
3. 关键信息(不在代码库中)
```

**交接格式**:
> "Akin to a long handoff file, enough for a totally new developer"

**实战案例**:

**场景**: 大型重构项目,上下文接近限制

**当前任务状态**:
```
已完成:
- ✅ 重构 auth 模块 (3 个文件)
- ✅ 更新测试
- ✅ 迁移数据库 schema

待办:
- [ ] 重构 user profile 模块
- [ ] 更新 API 文档
- [ ] 部署到 staging
```

**Cline 创建任务交接**:
```xml
<new_task>
<task_description>
继续身份验证系统重构 - Phase 2

## 已完成(Phase 1)
- 重构 src/auth/middleware.ts (新的 token 验证)
- 更新 src/auth/service.ts (使用 bcrypt 替代 crypto)
- 迁移数据库: users 表添加 refresh_token_hash 列
- 所有测试通过 (npm test)

## 下一步(Phase 2)
1. 重构 src/user/profile.ts
   - 更新 updateProfile 使用新 auth middleware
   - 添加 validateProfileData 辅助函数
2. 更新 API 文档反映新端点
3. 部署到 staging 环境验证

## 关键信息
- 新 token 格式: JWT with HS256
- Refresh token 有效期: 7 天
- 数据库迁移已应用(migration 003)
- Staging URL: https://staging.example.com

## 重要文件
- src/auth/middleware.ts (新实现)
- docs/API.md (需要更新)
- .env.staging (部署配置)
</task_description>
</new_task>
```

**新任务启动时**:
- 新对话线程创建
- 上下文预加载
- 完整背景信息可用
- 可以继续工作无需重新解释

**为什么重要?**
- **防止上下文耗尽**: 长项目分段处理
- **清晰交接**: 新"开发者"(新线程)完全了解背景
- **可恢复**: 可以暂停和恢复长期项目

**如何应用?**
```markdown
任务交接策略:
1. 监控上下文使用
2. 接近限制时规划交接点
3. 记录所有关键信息
4. 明确下一步行动
5. 创建新任务继续
```

---

### 模式 6: 环境详情自动注入 (Environment Details Auto-Injection)

**设计理念**: 自动提供文件系统和环境上下文

**自动注入内容**:
```
每条用户消息后自动接收:
- 递归文件列表
- 当前工作目录
- 活动运行的终端
- 系统信息
```

**关键约束**:
> "This information is not written by the user themselves, but is auto-generated"

**用户可能不知道这些详情** → Cline 需要清楚解释操作

**environment_details 示例**:
```xml
<environment_details>
<current_working_directory>/home/user/project</current_working_directory>
<files>
src/
  auth/
    middleware.ts
    service.ts
  user/
    profile.ts
tests/
  auth.test.ts
package.json
</files>
<active_terminals>
Terminal 1: npm run dev (running)
Terminal 2: (inactive)
</active_terminals>
</environment_details>
```

**为什么重要?**
- **无需重复询问**: 文件结构自动可用
- **上下文感知**: 知道哪些终端在运行
- **减少来回**: 不需要先列出文件再操作

**使用策略**:
```
1. 检查 environment_details 中的文件结构
2. 决定使用相对路径还是绝对路径
3. 意识到哪些终端正在运行
4. 不能 cd - 使用绝对路径或命令链
```

**实战案例**:

**场景**: 用户要求"运行测试"

**Cline 检查 environment_details**:
```
发现:
- tests/ 目录存在
- package.json 存在
- Terminal 1 正在运行 dev server
```

**Cline 操作**:
```xml
<thinking>
需要运行测试
package.json 应该有 test script
Terminal 1 正在使用,使用 Terminal 2
不需要 cd,可以直接运行 npm test
</thinking>

<execute_command>
<command>npm test</command>
<requires_approval>false</requires_approval>
</execute_command>
```

**如何应用?**
```markdown
环境感知最佳实践:
1. 始终检查 environment_details
2. 利用文件结构信息规划操作
3. 意识到活动终端避免冲突
4. 不假设用户知道自动注入的信息
```

---

## 与 Cursor/Claude Code 的核心区别

### 对比表

| 特性 | Cline | Cursor | Claude Code |
|------|-------|--------|-------------|
| **审批机制** | 每步强制审批 | 自主执行 | 自主执行 |
| **工具并行** | 单工具/消息 | 支持并行 | 积极并行 |
| **沟通风格** | 任务导向 | 解释性 | 极简主义 |
| **开源性** | 完全开源 | 专有 | 专有 |
| **VSCode 集成** | 原生深度 | 深度 | CLI,轻度 |
| **规划模式** | 双模式(PLAN/ACT) | 单模式 | 单模式 |
| **执行速度** | 较慢(审批) | 快 | 最快(并行) |
| **用户控制** | 最高 | 中 | 中 |
| **透明度** | 最高(开源) | 低 | 低 |

---

### 1. 审批工作流差异

**Cline**: 强制用户确认
```
Cline: 我将读取 auth.ts
      [等待批准]
用户: 批准
Cline: [读取文件]
      文件内容: ...
      [等待下一步指示]
```

**Cursor/Claude Code**: 自主执行
```
AI: [读取 auth.ts]
    [分析代码]
    [提出修改]
    [应用修改]
    [报告完成]
```

---

### 2. 执行速度 vs 控制权

**Cline 的权衡**:
- ✅ 用户完全控制每一步
- ✅ 可以在任何时候介入纠正
- ❌ 需要更多用户交互
- ❌ 任务完成时间更长

**Cursor/Claude Code 的权衡**:
- ✅ 快速自主执行
- ✅ 减少用户交互
- ❌ 可能在错误方向上走太远
- ❌ 用户需要信任"黑盒"AI

---

### 3. 开源透明度

**Cline 的优势**:
```
✅ 完整系统提示词公开
✅ 社区可以理解确切行为规则
✅ 可以修改和贡献提示词
✅ 适合学习 AI 工具设计
```

**专有工具的限制**:
```
❌ 系统提示词保密
❌ 行为规则不透明
❌ 用户只能猜测内部逻辑
```

---

### 4. 工具架构对比

**Cline**: XML 风格工具调用
```xml
<read_file>
<path>src/main.ts</path>
</read_file>
```

**Cursor/Claude Code**: JSON 函数调用
```json
{
  "tool": "read_file",
  "parameters": {
    "path": "src/main.ts"
  }
}
```

**Cline 的优势**:
- 更简单的解析
- 更人类可读
- 适合教学和学习

---

## 实际应用场景

### 场景 1: 安全重构

**Cline 的优势情景**:
```
用户: 重构整个身份验证系统

Cline: [PLAN 模式]
      分析现有实现...
      提出 12 步重构计划

      计划:
      1. 备份现有 auth 文件
      2. 创建新 auth/v2 目录
      3. 迁移 validateToken
      ...

      批准此计划?

用户: [审查计划]
      批准,但跳过步骤 5

Cline: [ACT 模式]
      [步骤 1] 备份...
      [等待确认]

      [步骤 2] 创建目录...
      [等待确认]

      ...
```

**为什么 Cline 适合**:
- 每步验证防止破坏性更改
- 用户可以在任何时候调整方向
- 高风险操作(删除文件)需要审批

---

### 场景 2: 探索性编程

**Cline 的使用方式**:
```
用户: 我想优化这个慢查询,但不确定最佳方法

Cline: [PLAN 模式]
      [收集上下文]
      list_code_definition_names(src/db/)
      search_files("SELECT.*JOIN")

      [分析]
      发现 3 个潜在瓶颈:
      1. posts.ts:45 - N+1 查询
      2. users.ts:78 - 缺失索引
      3. comments.ts:112 - 笛卡尔积

      建议优化顺序:
      1 → 2 → 3 (按影响排序)

      想先处理哪个?

用户: 先看看 #1

Cline: read_file("src/db/posts.ts")
      [显示问题代码]

      建议使用 JOIN 替代循环查询
      是否实施?
```

**为什么 Cline 适合**:
- PLAN 模式允许探索和讨论
- 用户保持完全控制方向
- 不会盲目应用可能不合适的优化

---

### 场景 3: 学习和理解

**Cline 作为教学工具**:
```
用户: 帮我理解这个复杂的 React 组件

Cline: [逐步分析]
      [步骤 1] 读取组件文件
      [等待确认]

      [步骤 2] 列出所有 hooks 使用
      list_code_definition_names(component.tsx)
      [显示: useState, useEffect, useContext...]

      [步骤 3] 解释每个 hook
      想深入了解哪个 hook?
```

**为什么 Cline 适合**:
- 逐步展开,不会信息过载
- 用户控制学习节奏
- 可以在任何点深入或继续

---

## 可操作的最佳实践

### ✅ DO (推荐做法)

1. **拥抱审批循环**
   ```markdown
   ✅ 充分利用 Cline 的安全审批机制
   ✅ 审查每个操作的意图和结果
   ✅ 在高风险操作前暂停思考
   ```

2. **使用 PLAN 模式规划复杂任务**
   ```markdown
   ✅ 复杂重构从 PLAN 模式开始
   ✅ 讨论和验证方法后再执行
   ✅ 批准计划后切换到 ACT 模式
   ```

3. **分解大任务为小步骤**
   ```markdown
   ✅ 每步独立、可验证
   ✅ 小范围修改更容易审查
   ✅ 失败时容易回滚
   ```

4. **利用环境详情**
   ```markdown
   ✅ 检查自动注入的文件结构
   ✅ 意识到活动终端避免冲突
   ✅ 使用绝对路径提高可靠性
   ```

5. **长期项目使用任务交接**
   ```markdown
   ✅ 监控上下文使用
   ✅ 规划合理的交接点
   ✅ 记录所有关键决策和状态
   ```

---

### ❌ DON'T (避免做法)

1. **不要期待快速执行**
   ```markdown
   ❌ Cline 设计为安全,非速度
   ❌ 接受较慢的速度换取控制权
   ✅ 用于高风险或不确定的任务
   ```

2. **不要跳过思考标签验证**
   ```markdown
   ❌ 盲目批准没有 <thinking> 的操作
   ✅ 确保 AI 已验证参数和逻辑
   ```

3. **不要对小修改使用 write_to_file**
   ```markdown
   ❌ 完全重写文件进行小修改
   ✅ 使用 replace_in_file 进行精确编辑
   ```

4. **不要忽略自动格式化**
   ```markdown
   ❌ 假设文件保持你编辑的格式
   ✅ 考虑编辑器自动格式化的影响
   ```

5. **不要在 ACT 模式下规划**
   ```markdown
   ❌ ACT 模式中讨论多个方案
   ✅ 回到 PLAN 模式重新规划
   ```

---

## 总结: 从 Cline 学到的核心教训

### 关键洞察

1. **用户控制 > 自动化速度**: 安全和可控性优先于执行速度
2. **透明度 = 信任**: 开源提示词让用户理解确切行为
3. **逐步验证**: 每步确认防止连锁错误
4. **规划与执行分离**: PLAN 模式允许无风险探索
5. **审批分层**: 根据风险智能决定何时需要确认
6. **精确编辑 > 完全重写**: 小范围修改更安全可靠

### 应用到你的工作流

**立即可做**:
1. 为自己的 AI 工具添加审批机制
2. 在执行前强制验证参数
3. 实施 PLAN/ACT 分离模式
4. 根据操作风险分层审批

**持续优化**:
- 观察哪些操作经常失败
- 识别需要更多用户控制的场景
- 建立渐进式上下文收集策略
- 练习将大任务分解为小步骤

### Cline 最适合的场景

✅ **高风险重构**: 需要每步验证
✅ **探索性编程**: 方向不确定
✅ **学习和理解**: 逐步深入代码库
✅ **安全第一**: 不能承受错误的场景

❌ **不适合的场景**:
❌ 简单重复任务(太慢)
❌ 需要快速原型(审批拖慢速度)
❌ 用户完全信任 AI 的场景

---

## 延伸阅读

- [Cline GitHub 仓库](https://github.com/cline/cline) (开源代码和提示词)
- [Cursor 系统提示词分析](/docs/tools/prompt-engineering/tools/cursor-prompts) (对比自主执行)
- [Claude Code 系统提示词分析](/docs/tools/prompt-engineering/tools/claude-code-prompts) (对比 CLI 优化)
- [Model Context Protocol (MCP)](https://modelcontextprotocol.io) (扩展 Cline 能力)

---

## 资源与归属

**提示词来源**: [system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools)
**分析版本**: Cline Prompt.txt (607 行,开源版本)
**最后更新**: 2025-11-17

**免责声明**: 本文仅用于教育目的,分析公开可获取的系统提示词。Cline 是开源项目,欢迎社区贡献。

---

## FAQ

### 为什么要分析 Cline 的系统提示词？

可以学习强审批与透明机制如何降低 AI 协作风险。

### 与 Cursor 或 Claude Code 最大差异是什么？

Cline 强调强制用户审批与慢速可控执行。

### 如何把这些理念用到自己的流程？

设置明确的审批门槛，关键改动分步执行并验证。
