---
id: cursor-prompts
title: Cursor 系统提示词深度解析
sidebar_label: Cursor 提示词分析
description: 深入剖析 Cursor AI 编程助手的系统提示词设计,学习其核心模式和最佳实践
---

# Cursor 系统提示词深度解析

> 理解 Cursor 如何通过精心设计的提示词实现智能代码协作

Cursor 是目前最流行的 AI 编程助手之一。本文通过分析其系统提示词,揭示 Cursor 如何实现高效的 AI-人类协作编程体验。

**学习目标**:
- 理解 Cursor 的核心设计哲学
- 掌握 5 个关键提示词模式
- 学会将这些模式应用到自己的 AI 工作流中

---

## 核心设计哲学

Cursor 的提示词设计体现了三大核心原则:

### 1. 上下文优先 (Context-First)

**设计理念**: AI 需要"看到"开发者看到的一切

Cursor 自动附加丰富的上下文信息:
- **当前文件**: 用户正在编辑的文件
- **光标位置**: 精确到行和列
- **打开的文件**: 最近查看的相关文件
- **编辑历史**: 会话中的修改记录
- **Linter 错误**: 实时的代码质量问题

**为什么重要?**
人类开发者依赖视觉和记忆来保持开发上下文,而 AI 需要显式提供这些信息。Cursor 通过自动化上下文收集,让 AI "看到"完整的开发场景。

**如何应用?**
在自定义 AI 工作流中:
```markdown
当你请求 AI 帮助时,始终提供:
- 相关代码文件
- 错误信息的完整堆栈
- 你正在尝试的操作
- 之前的尝试和结果
```

---

### 2. 工具透明化 (Tool Transparency)

**设计理念**: 用户不需要知道 AI 如何工作,只需看到结果

Cursor 明确指示 AI:
> **NEVER refer to tool names when speaking to the USER**

例如:
- ❌ "I need to use the `edit_file` tool to edit your file"
- ✅ "I will edit your file"

**为什么重要?**
保持对话的自然性。用户关心的是"做什么",而不是"用什么工具做"。

**如何应用?**
在编写自定义规则时:
```markdown
规则: 在解释操作时,使用自然语言而非技术术语
- 说"我会搜索代码库"而非"我将调用 codebase_search 函数"
- 说"让我读取那个文件"而非"执行 read_file 操作"
```

---

### 3. 主动执行 (Proactive Execution)

**设计理念**: 计划好后立即执行,不等待确认

Cursor 的关键指令:
> If you make a plan, **immediately follow it**, do not wait for the user to confirm or tell you to go ahead.

**唯一的停止条件**:
1. 需要用户提供额外信息
2. 有多个选项需要用户决策

**为什么重要?**
减少来回确认,提升开发速度。传统编程助手常陷入"计划 → 等待确认 → 执行"的低效循环。

**如何应用?**
在 Cursor Rules 中:
```markdown
当你制定了完整的实施计划时:
- 立即开始第一步
- 只在遇到模糊选择时询问
- 完成每一步后直接进入下一步
```

---

## 五大关键提示词模式

### 模式 1: 语义搜索优先 (Semantic Search First)

**Cursor 的工具选择逻辑**:

```
codebase_search (语义搜索):
  用途: 通过含义查找代码
  场景: "在哪里实现了用户认证?"

grep (精确文本搜索):
  用途: 查找确切的字符串
  场景: "找到所有 console.log 调用"

read_file (直接读取):
  用途: 已知文件路径,需要内容
  场景: "读取 auth.ts 文件"
```

**核心原则**: 优先使用语义搜索理解代码意图,而非机械的文本匹配

**实战示例**:

**❌ 糟糕的查询**:
```
Query: "MyInterface frontend"
问题: 过于简短,缺乏上下文
```

**✅ 优秀的查询**:
```
Query: "Where is MyInterface implemented in the frontend?"
优点: 完整的问题,明确的上下文
```

**如何应用?**
当你需要 AI 理解代码时:
- 用完整的问题,而非关键词
- 包含具体的上下文 (frontend/backend/特定模块)
- 描述你要找的行为,而非代码片段

---

### 模式 2: 简化代码编辑格式 (Simplified Edit Format)

**Cursor 的创新**: 差异式代码编辑

传统方式需要重写整个文件,Cursor 只显示变更:

```typescript
// ... existing code ...
{{ edit_1 }}
// ... existing code ...
{{ edit_2 }}
// ... existing code ...
```

**为什么这样设计?**

1. **节省 Token**: 不重复显示未修改的代码
2. **用户友好**: 开发者快速定位变更
3. **Apply Model 友好**: 专门的小模型易于解析和应用

**实战对比**:

**传统方式** (200 行文件修改 2 行):
```typescript
// 完整显示 200 行代码
function authenticate(user) {
  // ... 198 行 ...
}
```
Token 消耗: ~2000

**Cursor 方式**:
```typescript
function authenticate(user) {
  // ... existing code ...

  if (!user.email) {
    throw new Error('Email is required');  // 新增
  }

  // ... existing code ...
}
```
Token 消耗: ~200 (节省 90%)

**如何应用?**
在 Cursor Rules 中添加:
```markdown
代码编辑规则:
- 只显示需要修改的代码块
- 用 "// ... existing code ..." 标记未变更区域
- 始终包含足够的上下文让我定位修改位置
```

---

### 模式 3: 结构化工具调用 (Structured Tool Calling)

**Cursor 的严格规则**:

```
1. ALWAYS follow the tool call schema exactly
2. NEVER call tools that are no longer available
3. Prefer tools over asking user if you can get info yourself
4. Only use standard tool call format
```

**关键洞察**: 工具调用是协议,不是建议

**Example: File Reading**

```json
{
  "function": "read_file",
  "parameters": {
    "path": "src/auth.ts",
    "explanation": "Reading auth module to understand current implementation"
  }
}
```

**必须包含 explanation**: 为什么使用这个工具,如何帮助完成任务

**如何应用?**
当定义自定义工具时:
- 明确每个参数的类型和用途
- 要求 AI 解释工具调用的理由
- 设置工具选择的优先级规则

---

### 模式 4: 智能上下文管理 (Smart Context Management)

**Cursor 如何决定包含什么?**

```xml
<attached_files>
  <file_contents path="api.py" lines="1-7">
    import vllm
    model = vllm.LLM(...)
  </file_contents>
</attached_files>
```

**策略**:
- **Relevance First**: 只包含与任务相关的文件
- **Snippets Over Full**: 优先显示关键代码片段
- **Recent Activity**: 最近查看/编辑的文件优先

**Token 预算管理**:

假设上下文窗口 = 200k tokens
- System Prompt: ~5k
- User Messages: ~10k
- **可用于上下文**: ~185k

Cursor 智能分配:
- 当前文件: 全部内容
- 相关文件: 关键片段
- 历史对话: 最近 N 轮

**如何应用?**
优化你的 AI 对话:
```markdown
主动管理上下文:
- 新任务开始时,清理不相关的历史
- 使用 @file 精确指定需要的文件
- 避免一次性附加整个代码库
```

---

### 模式 5: 渐进式信息收集 (Progressive Information Gathering)

**Cursor 的指导原则**:

> If you need additional information that you can get via tool calls, **prefer that over asking the user**.

**决策树**:

```
需要信息?
  ├─ 能通过工具获取? → 调用工具 (read_file, grep, codebase_search)
  └─ 无法通过工具获取? → 询问用户

工具调用后:
  ├─ 信息充足? → 继续执行
  └─ 仍需更多? → 调用更多工具或询问用户
```

**实战案例**:

**场景**: 用户要求 "优化数据库查询"

**❌ 低效方式**:
```
AI: "请问你想优化哪个查询?在哪个文件?"
[等待用户回复]
```

**✅ Cursor 方式**:
```
AI: [自动执行]
1. codebase_search("database query performance slow")
2. grep("SELECT.*FROM.*WHERE")
3. 分析结果,发现 3 个潜在优化点
4. 向用户展示发现并建议优化
```

**如何应用?**
训练你的 AI 交互习惯:
- 提出问题时,包含足够背景让 AI 自己探索
- 鼓励 AI 主动使用工具而非被动等待
- 只在 AI 真正无法获取信息时提供输入

---

## 实际应用场景

### 场景 1: 重构代码

**传统对话**:
```
User: 重构这个函数
AI: 好的,请问你想怎么重构?
User: 让它更模块化
AI: 理解了,请问具体要拆分成几个函数?
[来回多轮]
```

**应用 Cursor 模式后**:
```
User: 重构 processUser 函数,让它更模块化 @src/user.ts

AI: [立即执行]
1. 读取 user.ts
2. 分析函数职责
3. 自动拆分为:
   - validateUser()
   - saveUser()
   - notifyUser()
4. 展示重构后的代码
```

**关键应用**:
- ✅ 模式 3: 主动执行,不等待确认
- ✅ 模式 5: 渐进式信息收集

---

### 场景 2: Bug 排查

**应用 Cursor 模式**:
```
User: 用户登录失败,错误信息是 "Invalid token" @logs/error.log

AI: [分析流程]
1. 语义搜索: "token validation authentication"
2. 读取相关文件: auth.ts, middleware.ts
3. 检查 error.log 中的堆栈信息
4. 发现问题: Token 过期时间配置错误
5. 展示修复方案
```

**关键应用**:
- ✅ 模式 1: 语义搜索优先
- ✅ 模式 4: 智能上下文管理
- ✅ 模式 5: 主动工具调用

---

## 可操作的最佳实践

基于 Cursor 的提示词设计,这里是你可以立即应用的技巧:

### ✅ DO (推荐做法)

1. **提供完整上下文**
   ```markdown
   ❌ "这个函数有 bug"
   ✅ "processPayment 函数在处理退款时抛出 NullPointerException @src/payment.ts"
   ```

2. **使用语义化问题**
   ```markdown
   ❌ "找 API"
   ✅ "在哪里定义了用户认证相关的 API 端点?"
   ```

3. **明确期望的行动**
   ```markdown
   ❌ "看看这个"
   ✅ "分析这个性能瓶颈并提供优化建议 @profile.json"
   ```

4. **允许 AI 主动探索**
   ```markdown
   ✅ "帮我理解购物车功能的实现逻辑"
   (让 AI 自己搜索和阅读相关代码)
   ```

### ❌ DON'T (避免做法)

1. **不要过度解释技术细节**
   ```markdown
   ❌ "使用 codebase_search 工具查找..."
   ✅ "找到处理文件上传的代码"
   ```

2. **不要要求重复显示未改代码**
   ```markdown
   ❌ "重写整个文件"
   ✅ "只显示需要修改的部分"
   ```

3. **不要手动提供 AI 能获取的信息**
   ```markdown
   ❌ "这个文件的内容是... [粘贴 500 行]"
   ✅ "分析 @src/大文件.ts 的性能问题"
   ```

---

## 总结: 从 Cursor 学到的核心教训

### 关键洞察

1. **上下文 > 一切**: 丰富的上下文是高质量 AI 输出的基础
2. **自然 > 技术**: 保持对话自然,隐藏实现细节
3. **行动 > 计划**: 减少确认环节,提升执行效率
4. **语义 > 文本**: 优先理解意图,而非精确匹配
5. **工具 > 询问**: 能自动获取的信息就不要问用户

### 应用到你的工作流

**立即可做**:
1. 更新你的 Cursor Rules,加入上述模式
2. 训练自己提供更完整的上下文
3. 允许 AI 更自主地探索和执行

**持续优化**:
- 观察哪些对话模式最高效
- 记录重复的低效交互
- 迭代你的提示词规则

---

## 延伸阅读

- [Cursor 官方文档](https://docs.cursor.com)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)
- [AI Coding Club: Vibe Coding 工作流](/docs/zh/vibe/03-vibe-coding-workflow)

---

## 资源与归属

**提示词来源**: [system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools)
**分析版本**: Cursor Agent Prompt 2.0 (2024)
**最后更新**: 2025-11-17

**免责声明**: 本文仅用于教育目的,分析公开可获取的系统提示词。所有权利归 Cursor/Anysphere 所有。
