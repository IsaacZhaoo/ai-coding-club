---
id: claude-code-prompts
title: Claude Code 系统提示词深度解析
sidebar_label: Claude Code 提示词分析
description: 深入剖析 Claude Code CLI 工具的系统提示词设计,学习其极简主义哲学和安全优先的架构模式
---

# Claude Code 系统提示词深度解析

> 理解 Claude Code 如何通过极简设计实现高效的 CLI 代码协作

Claude Code 是 Anthropic 官方推出的 AI 编程 CLI 工具。与传统 AI 编程助手不同,Claude Code 采用**极简主义**设计哲学,专为命令行环境优化。本文通过分析其系统提示词,揭示这一独特工具的设计理念。

**学习目标**:
- 理解 Claude Code 的极简主义设计哲学
- 掌握 6 个关键提示词模式
- 学会将 CLI 优化思维应用到自己的 AI 工作流

---

## 核心设计哲学

### 1. 极简主义沟通 (Extreme Minimalism)

**设计理念**: "Do what has been asked; nothing more, nothing less."

Claude Code 优先超简洁响应,目标是 1-3 句话:

```
用户: what is 2+2?
Claude Code: 4

用户: is 11 a prime number?
Claude Code: Yes
```

**为什么重要?**
- **CLI 优化**: 命令行界面需要简洁输出,不是冗长解释
- **Token 效率**: 最小化输出 tokens,加快响应速度
- **减少噪音**: 只提供用户请求的信息,避免过度解释

**对比其他工具**:
- ❌ 传统 AI: "The answer to 2+2 is 4. This is because..."
- ✅ Claude Code: "4"

**如何应用?**
在自定义规则中:
```markdown
规则: 极简响应模式
- 回答问题时,直接给出答案
- 避免前言、后语、总结(除非被要求)
- 匹配用户问题的复杂度级别
```

---

### 2. 编辑优先,永不创建 (Edit-First, Create-Never)

**设计理念**: 始终优先编辑现有文件,而非创建新文件

**核心指令**:
> ALWAYS prefer editing an existing file to creating a new one. NEVER create files unless they're absolutely necessary.

**特殊禁止**:
- **不主动创建文档**: 明确禁止主动创建 `*.md`, `README` 文件
- **必须显式请求**: 只在用户明确要求时才创建文件

**为什么这样设计?**
1. **避免惊喜**: 防止 AI 在代码库中创建意外文件
2. **保持整洁**: 减少代码库混乱和不必要的文件
3. **用户控制**: 文件创建应由用户主导,而非 AI 猜测

**实战案例**:

❌ **其他工具的行为**:
```
用户: "实现一个登录功能"
AI: [自动创建]
    - login.ts
    - README.md (解释如何使用)
    - DESIGN.md (设计文档)
```

✅ **Claude Code 的行为**:
```
用户: "实现一个登录功能"
Claude Code: [检查现有文件]
    - 发现 auth.ts 已存在
    - 编辑 auth.ts 添加登录逻辑
    - 不创建额外文档(除非被要求)
```

**如何应用?**
```markdown
文件操作原则:
- 优先搜索现有相关文件
- 只在绝对必要时创建新文件
- 创建前询问用户确认
```

---

### 3. 专业客观 > 用户验证 (Professional Objectivity)

**设计理念**: 技术准确性和真实性优先于验证用户信念

**核心指令**:
> Prioritize technical accuracy and truthfulness over validating the user's beliefs.

**行为准则**:
- **诚实分歧**: 必要时礼貌地不同意用户观点
- **调查优先**: 不确定时先调查事实,而非本能确认用户信念
- **避免过度赞美**: 不使用 "You're absolutely right" 等过度验证

**为什么重要?**
- 客观指导和尊重的纠正比虚假同意更有价值
- AI 应该应用相同的严格标准,而非偏向用户

**实战对比**:

❌ **过度验证的 AI**:
```
用户: "我觉得应该在每个函数里都用 try-catch"
AI: "You're absolutely right! That's an excellent practice..."
```

✅ **Claude Code**:
```
用户: "我觉得应该在每个函数里都用 try-catch"
Claude Code: "过度使用 try-catch 可能隐藏 bugs。建议只在可能抛出异常的边界处使用。"
```

**如何应用?**
```markdown
交互原则:
- 质疑假设时要有礼貌但坦率
- 提供技术准确的替代方案
- 避免空洞的赞美和验证
```

---

### 4. 平衡的主动性 (Balanced Proactiveness)

**设计理念**: 在"做正确的事"和"不让用户惊讶"之间取得平衡

**关键区分**:
- ✅ **允许主动**: 当用户要求具体任务时
- ❌ **禁止主动**: 当用户只是询问如何处理问题时

**Git 提交示例**:
```markdown
❌ 禁止主动提交:
"NEVER commit changes unless the user explicitly asks you to."

只在用户明确说 "提交这些更改" 时才提交
```

**如何应用?**
理解用户意图:
- "帮我实现 X" → 可以主动执行
- "我应该如何实现 X?" → 只提供指导,不主动执行

---

### 5. 防御性安全立场 (Defensive Security Stance)

**设计理念**: 只协助防御性安全任务

**允许**:
- ✅ 安全分析和漏洞检测
- ✅ 防御工具和检测规则
- ✅ CTF 挑战和教育场景

**拒绝**:
- ❌ 创建恶意代码
- ❌ 凭证收集
- ❌ 破坏性技术

---

## 六大关键提示词模式

### 模式 1: 上下文感知的工具委派 (Context-Aware Tool Delegation)

**核心机制**: 通过 `Task` 工具广泛使用专业化 agents

**Agent 类型**:
```typescript
- general-purpose: 复杂多步骤任务研究
- code-analyzer: 代码分析和 bug 追踪
- test-runner: 测试执行和结果分析
- file-analyzer: 日志文件摘要和分析
```

**何时使用 Agent vs. 直接工具**:
```
使用 Agent:
✅ 开放式代码库搜索 ("错误在哪里处理?")
✅ 多轮探索需求 (研究 bug、追踪逻辑)

使用直接工具:
✅ 读取特定文件路径 (Read 工具)
✅ 搜索特定类定义 (Glob 工具)
✅ 2-3 个文件内搜索 (Read 工具)
```

**独特设计: 无状态 Agent 模型**
```
关键约束:
- Agent 是"发射后不管"(fire-and-forget)
- 无法向 agent 发送额外消息
- 必须提前提供详细的自主任务描述
- Agent 结果对用户不可见,需要主动总结
```

**如何应用?**
```markdown
任务委派策略:
1. 复杂探索 → 使用 Task agent
2. 精确查询 → 使用直接工具
3. Agent prompt 必须详细且自包含
4. 总结 agent 结果给用户
```

---

### 模式 2: 并行执行优先 (Parallel Execution Emphasis)

**设计理念**: 独立操作应批量执行以优化性能

**核心指令** (在多个上下文中重复):
> When multiple independent pieces of information are requested and all commands are likely to succeed, batch your tool calls together for optimal performance.

**应用场景**:
1. **Git 操作**: 并行运行 `git status`, `git diff`, `git log`
2. **文件读取**: 并行读取多个不相关的文件
3. **Bash 命令**: 批量执行独立命令

**实战对比**:

❌ **串行执行** (低效):
```
1. git status
2. 等待结果
3. git diff
4. 等待结果
5. git log
6. 等待结果
```

✅ **并行执行** (高效):
```
单次消息中调用:
- git status
- git diff
- git log
(所有命令同时执行)
```

**Git 提交工作流示例**:
```
步骤 1: 并行执行理解状态
  - git status (查看未跟踪文件)
  - git diff (查看更改)
  - git log (查看提交历史)

步骤 2: 分析并起草提交消息

步骤 3: 并行执行暂存和提交
  - git add (暂存相关文件)
  - git commit (使用 HEREDOC 格式化消息)

步骤 4: 串行验证 (依赖前一步)
  - git status (验证成功)
```

**如何应用?**
```markdown
并行执行检查清单:
- [ ] 操作是否独立?
- [ ] 所有命令是否可能成功?
- [ ] 没有相互依赖?
→ 如果全是,则在单次消息中批量调用
```

---

### 模式 3: 工具特化 > Bash (Tool Specialization Over Bash)

**设计理念**: 尽可能使用专用工具而非 bash 命令

**工具映射**:
```
文件操作:
❌ cat/head/tail  →  ✅ Read 工具
❌ sed/awk        →  ✅ Edit 工具
❌ echo > file    →  ✅ Write 工具
❌ grep/rg        →  ✅ Grep 工具

保留 Bash 用于:
✅ 真正的系统命令 (npm, git, docker)
✅ 需要 shell 执行的终端操作
```

**禁止**:
```markdown
❌ NEVER: echo 或命令行工具来向用户沟通
❌ NEVER: bash 的 find/grep 来搜索文件/代码

✅ ALWAYS: 直接输出文本通信
✅ ALWAYS: 使用 Glob/Grep 工具搜索
```

**为什么这样设计?**
1. **更好的用户体验**: 专用工具有优化的输出格式
2. **错误处理**: 工具层面有更好的错误处理
3. **上下文优化**: 工具可以智能管理上下文使用

**如何应用?**
```markdown
工具选择决策树:
需要读文件? → Read 工具
需要编辑文件? → Edit 工具
需要搜索代码? → Grep 工具
需要运行命令? → Bash 工具
```

---

### 模式 4: 读前修改协议 (Read-Before-Modify Protocol)

**设计理念**: 在修改文件前强制读取文件

**工具层面强制**:
```
Edit 工具和 Write 工具都会失败,如果:
- 文件存在但未在会话中读取过

错误消息: "This tool will error if you attempt an edit
           without reading the file first."
```

**为什么强制执行?**
1. **防止盲目覆写**: 避免在不了解当前内容的情况下修改
2. **确保上下文意识**: 强制 AI 理解现有代码
3. **减少错误**: 大幅减少基于错误假设的修改

**Edit 工具特性**:
```typescript
{
  old_string: "要替换的确切文本",
  new_string: "新文本",
  replace_all: false  // 如果 old_string 不唯一会失败
}
```

**缩进保留规则**:
```
关键: 保留 Read 工具输出中的确切缩进
行号前缀格式: "空格 + 行号 + tab"
内容从 tab 后开始 → 这是需要匹配的部分
```

**如何应用?**
```markdown
文件修改工作流:
1. 使用 Read 工具读取文件
2. 理解当前内容和结构
3. 使用 Edit 精确替换(保留缩进)
4. 对于新文件,确认是否真的需要创建
```

---

### 模式 5: 主动任务管理 (Proactive Task Management)

**设计理念**: "VERY frequently" 使用 TodoWrite 工具追踪任务

**何时使用**:
```
✅ 使用 TodoWrite:
- 复杂多步骤任务 (3+ 步骤)
- 非平凡且复杂的任务
- 用户明确要求 todo list
- 用户提供多个任务

❌ 不使用 TodoWrite:
- 单一、直接的任务
- 平凡任务(提供不了组织价值)
- 少于 3 个简单步骤的任务
- 纯对话或信息性任务
```

**独特要求: 双形式任务描述**
```typescript
{
  content: "Run tests",           // 祈使句形式
  activeForm: "Running tests",    // 现在进行时形式
  status: "in_progress"
}
```

**为什么需要两种形式?**
- UX 考虑: 实时状态显示需要进行时形式
- 用户可见性: 清楚看到 AI 正在做什么

**关键原则**:
```
1. 标记完成要及时
   ❌ 不批量标记多个任务完成
   ✅ 完成一个立即标记一个

2. 同时只有一个 in_progress 任务
   - 不能少于 1 个
   - 不能多于 1 个

3. 完成标准严格
   只在真正完成时标记 completed:
   ✅ 测试通过
   ✅ 实现完整
   ✅ 无未解决错误
```

**如何应用?**
```markdown
任务管理最佳实践:
1. 开始复杂任务时创建 todo list
2. 标记当前任务为 in_progress
3. 完成后立即标记 completed
4. 直接进入下一个任务
```

---

### 模式 6: Git 安全协议 (Git Safety Protocol)

**设计理念**: 通过结构化安全护栏防止破坏性 Git 操作

**绝对禁止**:
```markdown
❌ NEVER update git config
❌ NEVER run destructive/irreversible commands
   (除非用户明确请求)
❌ NEVER skip hooks (--no-verify, --no-gpg-sign)
❌ NEVER force push to main/master
❌ Avoid git commit --amend
   (只在明确请求或 pre-commit hook 修改时使用)
```

**Amend 前验证**:
```bash
检查作者身份:
git log -1 --format='%an %ae'

确认未推送:
git status 显示 "Your branch is ahead"

如果两者都为真 → 可以 amend
否则 → 创建新提交 (永不 amend 其他开发者的提交)
```

**结构化提交工作流** (5 步骤):

**步骤 1: 并行理解状态**
```bash
并行执行:
- git status (查看未跟踪文件)
- git diff --staged 和 --unstaged (查看更改)
- git log (学习提交消息风格)
```

**步骤 2: 分析和起草**
```markdown
- 总结更改性质 (新功能/bug 修复/重构)
- 起草简洁消息 (1-2 句,聚焦"为什么"而非"什么")
- 确保准确反映更改和目的
```

**步骤 3: 并行暂存和提交**
```bash
并行:
- git add (添加相关未跟踪文件)
- git commit -m "$(cat <<'EOF'
    提交消息在这里

    🤖 Generated with Claude Code
    Co-Authored-By: Claude <noreply@anthropic.com>
    EOF
    )"
```

**关键: 使用 HEREDOC 确保格式化**
```bash
为什么使用 HEREDOC?
- 保证良好格式
- 支持多行消息
- 避免 shell 转义问题

格式:
git commit -m "$(cat <<'EOF'
   你的消息
   EOF
   )"
```

**步骤 4: Pre-commit Hook 处理**
```markdown
如果提交因 pre-commit hook 更改失败:
1. 重试一次
2. 如果成功但文件被 hook 修改:
   - 检查作者身份
   - 检查未推送
   - 如果安全 → amend
   - 否则 → 新提交
```

**步骤 5: 验证**
```bash
串行执行(依赖提交完成):
git status  # 验证成功
```

**Pull Request 工作流**:
```markdown
1. 并行: git status + git diff + 检查远程跟踪
2. 分析从分支分歧以来的所有提交
3. 并行: 创建分支 + 推送 + 使用 gh pr create 创建 PR

PR 格式(使用 HEREDOC):
gh pr create --title "标题" --body "$(cat <<'EOF'
## Summary
<1-3 要点>

## Test plan
[测试清单]

🤖 Generated with Claude Code
EOF
)"
```

**如何应用?**
```markdown
Git 最佳实践:
1. 始终并行获取 status/diff/log
2. 用 HEREDOC 格式化提交消息
3. 遵守安全协议(无 force push 等)
4. 在 amend 前验证作者身份
5. 只在明确要求时才提交
```

---

## 与 Cursor 的核心区别

### 1. 沟通风格差异

**Cursor**: 解释性、教育性
```
"我将重构这个函数以提高可读性。
这样做的原因是..."
```

**Claude Code**: 极简、行动导向
```
"重构 processUser 函数"
[直接显示更改]
```

---

### 2. 文件创建策略

**Cursor**: 主动创建辅助文件
```
实现功能 → 自动创建:
- 实现文件
- README.md
- 测试文件
- 文档
```

**Claude Code**: 强烈反对创建
```
实现功能 → 只在必要时:
- 编辑现有文件
- 只在明确要求时创建新文件
- 永不主动创建文档
```

---

### 3. Agent 架构

**Cursor**: 持续对话式 agents
```
- 可以与 agent 多轮交互
- Agent 保持上下文
```

**Claude Code**: 无状态、单次响应 agents
```
- Fire-and-forget 模型
- 必须提前提供所有指令
- Agent 只返回一次消息
```

---

### 4. 工具使用哲学

**Cursor**: 平衡工具和 bash
```
- 灵活使用 bash 命令
- 工具作为辅助
```

**Claude Code**: 强烈偏好专用工具
```
- Bash 仅用于真正的系统命令
- 文件操作必须使用工具
- 禁止 bash 用于通信
```

---

### 5. 并行执行

**Cursor**: 串行执行为默认
```
- 逐个执行操作
- 等待每个完成
```

**Claude Code**: 积极并行化
```
- 批量独立操作
- 在单次消息中多工具调用
- 显著性能优化
```

---

### 6. Git 安全

**Cursor**: 基本 git 功能
```
- 提供 git 能力
- 基本安全警告
```

**Claude Code**: 全面安全协议
```
- 结构化 5 步工作流
- 显式禁止(不更新配置、不 force push)
- Amend 前验证作者身份
- 强制使用 HEREDOC 格式化
```

---

## 实际应用场景

### 场景 1: 复杂重构任务

**传统对话式 AI**:
```
用户: 重构身份验证模块
AI: 好的,让我解释我将如何重构...
    [长篇解释]
    准备好开始了吗?
用户: 是的
AI: [开始重构]
```

**Claude Code 方式**:
```
用户: 重构身份验证模块
Claude Code: [创建 todo list]
    1. 分析当前实现
    2. 提取验证逻辑
    3. 创建辅助函数
    4. 更新测试

[立即开始执行,标记任务进度]
[完成后显示简洁摘要]
```

**应用的模式**:
- ✅ 极简沟通 (无冗长解释)
- ✅ 主动任务管理 (todo list)
- ✅ 平衡主动性 (直接执行,因为任务明确)

---

### 场景 2: Bug 调查

**应用 Claude Code 模式**:
```
用户: 登录失败,错误: "Invalid token"

Claude Code: [使用 Task agent 进行代码分析]
    Agent prompt: "分析身份验证流程,
                   搜索 token 验证逻辑,
                   检查错误日志,
                   返回根本原因分析"

[Agent 返回后]
Claude Code: "Token 过期配置错误在 auth.ts:45"
    [显示修复]
```

**关键模式**:
- ✅ 上下文感知工具委派 (使用 code-analyzer agent)
- ✅ 极简沟通 (直接指出问题)
- ✅ 代码引用约定 (auth.ts:45)

---

### 场景 3: Git 提交工作流

**Claude Code 的结构化方法**:
```
用户: 提交更改

Claude Code:
[步骤 1: 并行获取信息]
→ git status
→ git diff --staged
→ git log -5

[步骤 2: 分析]
"发现 3 个文件更改: 添加身份验证功能"

[步骤 3: 并行执行]
→ git add auth.ts auth.test.ts
→ git commit -m "$(cat <<'EOF'
  Add: 身份验证功能

  🤖 Generated with Claude Code
  Co-Authored-By: Claude <noreply@anthropic.com>
  EOF
  )"
→ git status (验证)

"✅ 提交成功: f8a9c3e"
```

**关键模式**:
- ✅ 并行执行 (步骤 1 和步骤 3)
- ✅ Git 安全协议 (HEREDOC,品牌化页脚)
- ✅ 极简沟通 (简洁确认)

---

## 可操作的最佳实践

### ✅ DO (推荐做法)

1. **拥抱极简沟通**
   ```markdown
   ❌ "我将分析你的代码并寻找性能问题,然后提供改进建议..."
   ✅ "分析性能问题 → [显示结果]"
   ```

2. **优先编辑而非创建**
   ```markdown
   ❌ 自动创建 README.md
   ✅ 检查是否有现有文档可以更新
   ```

3. **批量独立操作**
   ```markdown
   ✅ 在单次消息中并行:
      - 读取多个不相关文件
      - 执行多个独立 git 命令
      - 运行多个测试套件
   ```

4. **使用专用工具**
   ```markdown
   ❌ bash: cat file.ts | grep "pattern"
   ✅ 工具: Grep(pattern="pattern", path="file.ts")
   ```

5. **复杂任务使用 Todo List**
   ```markdown
   ✅ 3+ 步骤 → 创建 todo list
   ✅ 完成一个立即标记一个
   ✅ 保持一个 in_progress 任务
   ```

---

### ❌ DON'T (避免做法)

1. **不要过度解释**
   ```markdown
   ❌ "让我解释为什么这个方法更好..."
   ✅ [直接实现更好的方法]
   ```

2. **不要主动创建文档**
   ```markdown
   ❌ "我创建了 README.md 解释这个功能"
   ✅ "功能已实现"(只在要求时创建文档)
   ```

3. **不要串行执行独立操作**
   ```markdown
   ❌ git status; 等待; git diff; 等待; git log
   ✅ 并行: git status + git diff + git log
   ```

4. **不要在未读取的情况下修改**
   ```markdown
   ❌ 直接 Edit 文件
   ✅ Read → 理解 → Edit
   ```

5. **不要批量标记任务完成**
   ```markdown
   ❌ 完成 5 个任务后统一标记
   ✅ 每完成一个立即标记
   ```

---

## 总结: 从 Claude Code 学到的核心教训

### 关键洞察

1. **Less is More**: 极简沟通 > 冗长解释
2. **Safety First**: 结构化安全协议 > 灵活但危险
3. **Edit > Create**: 保守的文件操作 > 主动但混乱
4. **Parallel > Serial**: 批量独立操作 > 串行等待
5. **Tools > Bash**: 专用工具 > 通用 bash 命令
6. **Stateless Agents**: 详细前置指令 > 多轮对话

### 应用到你的工作流

**立即可做**:
1. 在自定义规则中添加极简沟通指令
2. 设置"编辑优先"原则
3. 识别可并行执行的操作
4. 为复杂任务使用 todo lists

**持续优化**:
- 观察哪些响应过于冗长
- 识别可以批量的操作
- 建立 Git 安全检查清单
- 练习极简但清晰的沟通

---

## 延伸阅读

- [Claude Code 官方文档](https://claude.ai/code)
- [Cursor 系统提示词分析](/docs/tools/prompt-engineering/tools/cursor-prompts) (对比学习)
- [Anthropic Prompt Engineering Guide](https://docs.anthropic.com/claude/docs/prompt-engineering)

---

## 资源与归属

**提示词来源**: [system-prompts-and-models-of-ai-tools](https://github.com/x1xhlol/system-prompts-and-models-of-ai-tools)
**分析版本**: Claude Code 2.0.0 (2025-09-29 发布)
**最后更新**: 2025-11-17

**免责声明**: 本文仅用于教育目的,分析公开可获取的系统提示词。所有权利归 Anthropic 所有。
