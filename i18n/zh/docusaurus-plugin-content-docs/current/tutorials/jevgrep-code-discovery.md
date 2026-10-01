---
title: "用 Jevgrep 按行为找到代码，再交给编程 Agent 修改"
sidebar_label: "Jevgrep 行为代码定位"
description: "使用 Jevgrep 按行为定位代码，回读源码证据，再把明确的修改任务交给编程 Agent。"
keywords: ["Jevgrep", "semantic code search", "AI coding agent", "code discovery"]
sidebar_position: 42
tags: ["tutorial", "agent-engineering"]
---

# 用 Jevgrep 按行为找到代码，再交给编程 Agent 修改

欢迎来到 AI Coding Club 的实战技巧专栏。作为一名正在阅读或修改不熟悉的代码仓库的开发者，你是否遇到过这样的时刻：你知道代码里必须有一个“请求鉴权”、“遥测事件记录”或“超时重试”的逻辑，但就是不知道它藏在哪些文件里？

如果你手里已经有一个编程 Agent（比如来自你常用的 AI 服务商），那么今天我们要介绍的 **Jevgrep** 将是你最得力的侦察兵。

在把它交给 Agent 修改之前，我们需要先让它帮你把地扫一遍，把**行为特征、原样源码和行号坐标**精准地摆在你面前。这篇教程将引导你完成从检索到对接 Agent 的全过程。

---

## 1. 准备阶段：环境搭建与连接

Jevgrep 不仅仅是一个文本搜索工具，它是一个利用 AI 判断代码相关性的智能检索 CLI。为了让它理解你的业务逻辑并产出高质量的线索，我们需要先安装它并配置 AI 网关。

### 环境要求
- **操作系统**：macOS 或 Linux（Windows 用户可通过 WSL 使用）。
- **运行时**：Node.js 22+。
- **依赖包**：无需额外安装 Python、Bun 或 ripgrep，Node + npm 足矣。

### 安装与检查

打开终端，运行以下命令确认环境并安装工具：

```sh
# 1. 检查 Node 版本
node --version

# 2. 全局安装 Jevgrep (版本 0.7.1)
npm install --global @dzhng/jevgrep@0.7.1

# 3. 验证安装
jg --version
```

### 配置 AI 网关 (`jg auth`)

Jevgrep 在分析代码时会将匹配的内容发送给后端进行语义判断。你需要先连接一个可信的 AI 网关。

```sh
jg auth
```

交互界面会提供多个选项：Vercel AI Gateway、TypeSafe、OpenRouter、OpenCode Zen，或者自定义 endpoint。
- **推荐**：对于日常开发，直接选择预设选项（如 `vercel` 或 `typesafe`），Jevgrep 会自动保存凭证到本地。
- **凭证位置**：配置默认保存在 `$XDG_CONFIG_HOME/jevgrep/credentials.json`。若未设置环境变量，则默认为 `~/.config/jevgrep/credentials.json`。

### 健康检查 (`jg doctor`)

在开始大规模搜索前，建议运行一次诊断，确保连接正常且 Key 有效：

```sh
jg doctor
```
如果这里报错（如余额不足或权限缺失等），请阅读服务商返回的具体错误说明并相应调整。只有当凭证本身无效、过期，或选定的 provider 配置确实不匹配时，才需要回到 `jg auth` 重新选择或更新凭证。

---

## 2. 侦察：理解你的搜索范围

在 Jevgrep 中，jg files 子命令专为本地文件范围预览而生，它能在不触碰任何外部服务的前提下，快速统计符合搜索规则的文件数量、总字节数及顶层目录分布，同时清晰展示被过滤规则跳过的路径数量。该功能完全依赖本地计算，无需服务商 API key，也不会向任何 provider 发送请求，从而在保障效率的同时守住数据边界；其内置的默认过滤机制会自动规避明显敏感文件与依赖构建内容，但需谨记：统计结果仅反映当前扫描范围的文件特征，并不能证明源码中已无秘密信息，最终的外发范围仍应由项目所有者根据具体场景审慎界定。

### 查看可读取文件统计

使用 `jg files` 命令快速预览当前目录的结构和规模：

```sh
# 统计根目录下的可读取文件数与字节数，并按顶层目录汇总
jg files ./my-project --exclude 'src/generated/'
```

**输出解读：**
- **文件数/字节数**：大致了解仓库体量。
- **Top-level dirs**：看到代码主要分布在 `src`、`lib` 等区域。
- **Skipped by filters**：关键指标，告诉你有多少文件因为规则被跳过了（如 `.git`、`node_modules` 或你指定的生成目录）。

> **重要原则**：`jg files` 仅在本地运行，无需网络请求，是安全的预演。请使用与后续搜索相同的根目录和 `--exclude` 参数，以便让 Jevgrep 对“搜索范围”有准确的预期。

---

## 3. 核心动作：按行为提问 (The Prompting Phase)

现在让我们进入正题。Jevgrep 的精髓在于：**它不只是搜索关键词，它是搜索“意图”**。

### 示例问题

假设你接手了一个后端服务，需要确认鉴权和遥测逻辑。你可以尝试以下提问（以当前目录为上下文）：

```sh
# 1. 寻找请求鉴权逻辑
jg "Where is authentication checked before a request reaches a handler?" . --exclude 'tests/'

# 2. 寻找遥测事件记录与发送机制
jg "How are telemetry events recorded and sent?" . --exclude 'src/generated/'
```

### 如何构建一个好的 Prompt？
- **描述行为**：动词很重要（"checked", "recorded", "sent", "retrying"）。
- **提供上下文**：如果知道大致模块，可以加入（如 "in the payment gateway flow"）。
- **排除噪音**：熟练使用 `--exclude` 过滤测试代码、生成代码和构建产物。

---

## 4. 阅读线索：解读搜索结果

Jevgrep 的 CLI 命令为 `jg`。它不只是返回一堆链接，而是基于 Jev 模型对目录、文件、声明与行为问题之间的相关性进行判断后，将结果结构化地呈现出来。理解这些输出结构，是回读源码、验证假设的关键第一步。

### 4.1 标准输出与保存

- `jg` 默认将结果输出到标准输出（stdout），不会自动创建报告文件。
- 若需持久化结果，可使用 Shell 重定向：

  ```bash
  jg "How are telemetry events recorded and sent?" ./my-project > telemetry-search.txt
  ```

- 官方示例输出可参考：  
  https://github.com/dzhng/jevgrep/blob/c9c70c448842297093e9f1187c493cdf9fa69d7b/specs/done/jevgrep/assets/stdout-example.txt

### 4.2 结果呈现顺序

CLI 按以下顺序组织信息，帮助读者从宏观到微观逐步聚焦：

- **相关文件摘要**：简要说明每个文件与查询问题的关联。
- **紧凑文件列表**：列出涉及的文件路径，便于快速定位。
- **带行号的原样源码**：展示关键代码片段，保留原始格式。
- **声明与可能的局部调用位置**：指出函数、类或接口的定义及其被调用的上下文。

### 4.3 解读局部调用线索

在“局部调用位置”部分，Jevgrep 有时会标注类似 `runtime dispatch not verified` 的提示。这表示：

- CLI 基于静态结构给出推测位置；
- 最终是否正确仍需回到源码与运行时行为判断。

**正确做法：**

1. 记下该提示对应的函数名或调用点；
2. 回到源码，按行号定位相关实现；
3. 结合测试或日志验证运行时行为。

必须顺着 CLI 的静态结构顺藤摸瓜，在真实代码里核对 runtime dispatch 的实际行为。

### 4.4 多语言支持策略

Jevgrep 对以下语言提供声明解析能力：

- Python
- TypeScript / JavaScript
- Go
- Rust

对于其他文本类型（如 Markdown、配置文件、文档等），则使用 fallback 策略：

- 可能只返回文件位置；

**应对方式：**

- 若结果仅包含文件路径，直接打开该文件，按 Jevgrep 提示的行号或上下文手动阅读；
- 结合查询关键词在编辑器中搜索，快速定位相关逻辑。

### 4.5 以官方遥测记录为例的回读流程

假设你关注“telemetry events 如何被记录与发送”，可按照以下路径操作：

1. **按行号查看源码**  
   - `src/backend/events.ts`：找到 `BackendTelemetry.recordEvent`，确认其调用 `return super.recordEvent(name)`。
   - `src/telemetry.ts`：定位 `Telemetry.recordEvent` 的实现，观察其返回 `{ name, recorded: true }`。
   - 对比两者，理解父类委托与事件名称保留的机制。

2. **验证测试用例**  
   - 打开 `tests/telemetry.test.ts`，查找 `testEventName` 测试；
   - 确认传入 `opened` 后，返回的 `name` 仍为 `opened`，验证名称未被意外修改。

3. **交给 Agent 具体任务**  
   - 基于上述理解，向 Agent 下达明确指令，例如：  
     “在保留父类委托逻辑的前提下，为 `BackendTelemetry.recordEvent` 添加结构化日志输出。”

### 4.6 小结

- Jevgrep 的输出是“线索地图”，不是最终答案；
- 核心工作在于：按行号读源码 → 对照测试验证 → 必要时人工核对运行时行为；
- 遇到 `runtime dispatch not verified` 等提示时，务必回归代码确认；
- 对于非解析语言的结果，直接打开文件，结合关键词搜索定位。

掌握这一流程，你就能高效利用 Jevgrep 的搜索结果，将模型洞察转化为可验证的代码理解。

---

## 5. 证据移交：赋能编程 Agent

现在你手里有了具体的文件名、行号和逻辑细节。接下来就是利用你手中的编程 Agent 来完成修改和测试。

### 安装 Jevgrep Skill (可选但推荐)

如果你希望 Agent 在对话中直接调起 Jevgrep，你需要安装对应的 Skill。在项目根目录执行：

```sh
jg skill
```
> **注意**：该命令通过 `npx skills` 安装，需要网络。这不同于安装 CLI 本身，也不同于配置 API Key。

### 向 Agent 汇报证据

将以下信息整理发送给 Agent：

1.  **检索范围**：说明你使用了相同的 `--exclude` 规则。
2.  **核心文件与行号**：引用 Jevgrep 返回的源码片段（直接粘贴给 Agent 看，确保上下文一致）。
3.  **具体需求**：基于这些线索，提出明确的修改目标。

**示例对话（你发给 Agent）：**

> “我已经用 Jevgrep 确认了鉴权逻辑在 `src/middleware/auth.ts` 的第 45-50 行。
> **现状**：它目前只检查 Token 是否存在，未做白名单校验。
> **任务**：请在第 48 行之后加入白名单匹配逻辑（参数名为 `allowedRoles`），并更新单元测试以覆盖新分支。”

### 闭环验证

Agent 修改后，不要仅依赖 `jg files`（它只统计搜索范围），而应通过版本控制核对变更。建议使用 `git diff` 查看具体改动，并运行与修改行为相关的测试套件；Jevgrep 输出的测试位置可作为进一步定位的线索。

---

## 6. 高级技巧与故障排除

### 并发控制
如果网络环境不稳定，Jevgrep 默认并发数较高（32）。你可以限制同时发送的请求数以换取稳定性：

```sh
# 限制为串行执行
jg "..." --concurrency 1

# 限制为 4 个并发
jg "..." --concurrency 4
```

### 输出状态码与缓存
- **退出码**：`0` 完整，`1` 失败，`2` 不完整（服务缺口、预算上限耗尽、文件读取失败等），`130` 中断。
- **智能缓存**：有效的模型答案默认本地缓存，网络恢复后重跑会自动复用，节省 Token 和时间。若需强制刷新：

```sh
jg "..." --no-cache
```

### 精确搜索补位
如果 Jevgrep 的模糊结果不够精确，已知符号或路径时，回归经典的工具往往更快：
- 直接 `cat` 文件。
- 使用 `ripgrep` (`rg`) 进行精确字符串匹配。

---

## 7. 总结

Jevgrep 将“行为搜索”这一概念落地为可执行的 CLI 流程。它填补了从“我知道要改什么功能”到“我在哪里改代码”之间的认知鸿沟。

**最佳实践路径：**
1.  **配置**：确保 `jg auth` 连通可靠的服务商网关。
2.  **预览**：用 `jg files` 确认搜索边界，尊重你的项目约束。
3.  **提问**：用自然语言描述“行为”，而非“文件名”。
4.  **审阅**：仔细阅读返回的源码片段和行号线索，不要只看标题。
5.  **赋能**：将整理好的证据直接喂给你的编程 Agent，让它专注于实现修改与测试。

现在，打开你的终端，去扫描那个让你头疼的仓库吧。Jevgrep 会帮你把迷雾拨开一角，剩下的交给代码和 AI 来完成。