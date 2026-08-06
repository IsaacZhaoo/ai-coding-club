---
title: "DeepSeek V4-Flash 接入 Codex CLI 教程：配置方法、兼容性与开源架构"
description: "本教程介绍 DeepSeek V4-Flash 接入 Codex CLI 的完整配置方法，包括 model catalog、named profile、API Key、验证、切换、回退与 Responses API 兼容边界。"
keywords:
  - DeepSeek V4 Codex
  - DeepSeek V4-Flash Codex CLI
  - Codex 接入 DeepSeek
  - Codex 切换 DeepSeek
  - DeepSeek Responses API
  - Codex 自定义 Provider
sidebar_position: 31
tags: [tutorial, coding-assistant, agent-engineering, deepseek, codex]
---

# DeepSeek V4-Flash 接入 Codex CLI 教程：配置方法、兼容性与开源架构

*作者：有光*

本教程帮你完成一件具体的事：在不覆盖现有 Codex 默认配置的情况下，建立一套可验证、可切换、可回退的 DeepSeek V4-Flash × Codex CLI 配置。完成后，你会新增两个文件——一个 model catalog JSON 和一个 named profile TOML——同时学会如何在任何时候通过普通的 `codex` 命令回到原来的 provider。

配置路径跑通以后，教程会解释 DeepSeek Responses API 兼容性的实际边界，再用五层架构说清开放权重、托管推理、协议、Agent harness 和本地执行各自的替换权与控制边界。

---

## 前置条件

在开始之前，确认以下几项：

- **Codex CLI 版本 0.144.0 或更高**。DeepSeek model catalog 要求这个最低版本。运行 `codex --version` 检查。
- **DeepSeek API Key**。前往 [DeepSeek 开放平台](https://platform.deepseek.com/) 申请，目前 V4-Flash API 处于公开 Beta 阶段（2026-07-31 发布）。
- **操作系统**：Bash/macOS/Linux/WSL。本教程中的 shell 命令针对这些环境编写。
- **网络可访问 `api.deepseek.com`**。配置中使用的是 DeepSeek 官方托管推理端点，不是本地部署。

---

## 第一步：确认 Codex 配置目录

Codex 的配置目录默认在 `~/.codex/`。如果你是第一次配置，目录可能尚未存在：

```bash
mkdir -p ~/.codex
ls ~/.codex/
```

本教程会在这个目录下新增两个文件。如果目录里已有 `config.toml`，它是你的默认 Codex 配置，**本教程不会修改它**。

---

## 第二步：获取并保存完整的 DeepSeek Model Catalog

Codex 通过 `model_catalog_json` 字段读取外部 model catalog 文件，以识别新 provider 提供的模型。你需要从 DeepSeek 官方 Codex 文档获取这份 JSON，并保存为本地文件。

前往 DeepSeek Codex 集成文档：

> **[https://api-docs.deepseek.com/quick_start/agent_integrations/codex](https://api-docs.deepseek.com/quick_start/agent_integrations/codex)**

文档页面提供了完整的 model catalog JSON 内容。将完整内容复制，保存为：

```bash
~/.codex/deepseek-models.json
```

**不要裁剪 catalog 内容**。Profile 中的 `model_catalog_json` 字段会引用这个文件，Codex 在启动时会解析它，catalog 残缺会导致模型无法识别。

保存后，验证文件存在且 JSON 格式可解析：

```bash
# 检查文件是否存在
ls -lh ~/.codex/deepseek-models.json

# 验证 JSON 可解析（不打印内容，只检查格式）
python3 -m json.tool ~/.codex/deepseek-models.json > /dev/null && echo "JSON valid"
# 或者使用 jq
jq empty ~/.codex/deepseek-models.json && echo "JSON valid"
```

如果命令返回 `JSON valid`，文件已就位。

---

## 第三步：新建独立 Named Profile

Codex 支持通过 named profile 切换不同的模型和 provider 配置。Named profile 文件的路径格式为：

```
$CODEX_HOME/<profile>.config.toml
```

`CODEX_HOME` 默认指向 `~/.codex/`。新建一个专用 profile，不覆盖任何已有配置：

```bash
touch ~/.codex/deepseek-v4.config.toml
```

将以下内容写入该文件：

```toml
# ~/.codex/deepseek-v4.config.toml
model = "deepseek-v4-flash"
model_provider = "deepseek"
model_reasoning_effort = "high"
model_catalog_json = "~/.codex/deepseek-models.json"

[model_providers.deepseek]
name = "DeepSeek"
base_url = "https://api.deepseek.com/"
wire_api = "responses"
env_key = "DEEPSEEK_API_KEY"
```

几项说明：

- `model = "deepseek-v4-flash"`：对应 DeepSeek V4-Flash API 的 model identifier。
- `wire_api = "responses"`：告知 Codex 使用 Responses 协议与该 provider 通信，这是 DeepSeek 官方声明的兼容路径。
- `env_key = "DEEPSEEK_API_KEY"`：Codex 会从该环境变量名读取 API Key，**明文 Key 不写入 TOML 文件**。
- `model_catalog_json`：指向第二步保存的外部 catalog 文件。
- `model_reasoning_effort = "high"`：按 DeepSeek 官方 Codex 指南配置，可根据任务调整。

**这个 Profile 文件只有 named profile 才会加载**。运行普通的 `codex` 命令不受影响。

---

## 第四步：Shell 范围注入 API Key 并启动

**不要把 Key 写入文件，不要 `export` 到全局 shell 配置（`~/.bashrc`、`~/.zshrc`）**。使用 shell 范围注入，Key 只在当前 shell 会话有效：

```bash
read -rsp "DeepSeek API Key: " DEEPSEEK_API_KEY
export DEEPSEEK_API_KEY
printf '\n'
codex --profile deepseek-v4
```

- `read -rsp`：以静默模式读取输入，不会在终端回显 Key 内容。
- `export DEEPSEEK_API_KEY`：将 Key 导出为环境变量，只在当前 shell 会话有效。
- `codex --profile deepseek-v4`：加载 `~/.codex/deepseek-v4.config.toml`，使用其中的配置启动 Codex。

---

## 第五步：验证——三个确认层级

启动 Codex 后，有三个层级的确认，代表不同的验证程度。

### 层级 1：配置文件就位（本地可确认）

以下检查不会触碰 API，只验证本地配置文件和环境变量是否就位：

```bash
# 确认 profile 文件存在
ls -lh ~/.codex/deepseek-v4.config.toml

# 确认 catalog 文件存在且 JSON 可解析
ls -lh ~/.codex/deepseek-models.json
python3 -m json.tool ~/.codex/deepseek-models.json > /dev/null && echo "Catalog OK"

# 确认环境变量非空（绝不打印 Key 值）
[ -n "$DEEPSEEK_API_KEY" ] && echo "DEEPSEEK_API_KEY is set" || echo "DEEPSEEK_API_KEY is NOT set"
```

以上三项全部通过，只说明文件与环境变量已就位，Key 也已注入当前 shell。

### 层级 2：通过一次请求确认 API 鉴权

向 DeepSeek endpoint 发起请求时，可能收到正常响应、鉴权错误或其他 API / 网络错误。如果看到 `401 Unauthorized` 或类似报错，先检查环境变量是否正确 export，再确认 Key 本身是否有效。收到正常响应则说明鉴权通过，Codex 可以正常与 DeepSeek API 通信。

### 层级 3：小型任务验证端到端链路

从第一个小任务开始是个好习惯——比如让 Codex 读取并描述一个小文件——优先确认整条链路（profile → Key → API → 响应 → tool loop）通畅，再处理复杂任务。任务能否成功取决于任务本身、模型能力、工具兼容性和本地执行环境，是配置层之外的判断范围。

---

## 第六步：切换与回退

### 回到默认 Codex Provider

退出 DeepSeek 会话后，运行普通的 `codex` 命令即可回到你原来的默认配置——named profile 不影响默认路径：

```bash
# 退出 DeepSeek 会话后，清除 Key
unset DEEPSEEK_API_KEY

# 使用默认 provider 启动 Codex
codex
```

### 只有确认不再使用时才删除新增文件

本教程只新增了两个文件：`~/.codex/deepseek-models.json` 和 `~/.codex/deepseek-v4.config.toml`。如果确认不再需要，可以删除：

```bash
rm ~/.codex/deepseek-models.json
rm ~/.codex/deepseek-v4.config.toml
```

删除之前建议先确认：这两个文件没有被其他 profile 引用。

---

## DeepSeek Responses API 兼容性：兼容是梯度，支持有上下界

DeepSeek 官方声明 V4-Flash 原生支持 Responses API，并专门适配 Codex。Profile 中的 `wire_api = "responses"` 正是基于这一声明的配置路径。但"兼容"不是二元判断，Responses API 的支持范围有明确的上下界。

以下是 DeepSeek V4-Flash Responses API 的实际支持范围：

| 功能 / 字段 | 状态 | 说明 |
| --- | --- | --- |
| Function tools | ✅ 支持 | 标准函数调用，Codex 工具循环的核心依赖 |
| Server-side web search | ✅ 支持 | DeepSeek 托管的搜索能力 |
| `apply_patch` | ✅ 支持 | Codex 兼容的补丁工具，文件修改的关键路径 |
| `previous_response_id` | ❌ 不支持 | 多轮对话的状态链接，服务端响应链不可用 |
| Conversation / store | ❌ 不支持 | 服务端会话管理不可用 |
| Background mode | ❌ 不支持 | 异步后台任务不可用 |
| Built-in `file_search` | 🚫 被忽略 | 请求字段存在但 API 不处理 |
| Built-in `code_interpreter` | 🚫 被忽略 | 同上 |
| Built-in `computer_use` | 🚫 被忽略 | 同上 |
| Built-in `mcp` tool type | 🚫 被忽略 | API 层面被忽略；Codex 本地 MCP 是否可用取决于客户端工具转译路径 |
| 不支持的参数字段 | ⚠️ 可能 silent ignore | 字段不报错，但不生效 |

**关于 `apply_patch`**：这是 Codex × DeepSeek 兼容路径的核心。`apply_patch` 是 Codex 写入文件变更的工具，DeepSeek 显式声明支持它，说明双方在文件修改这条关键路径上有明确的协议对齐。

**关于 built-in `mcp` 被忽略**：DeepSeek Responses API 不处理 built-in `mcp` tool type。Codex 本地 MCP 配置是否仍然可用，取决于客户端工具是否在发送请求前将 MCP tool 转译为普通 function calls。转译路径的实际行为可以结合客户端工具类型和运行日志来判断，不是一个可以直接从 API 文档读出答案的是非题。

**关于 silent ignore**：Responses API 的某些不支持字段在请求时不会返回错误，而是静默忽略。你可能看不到明显的失败信号，但功能并没有生效。调试时值得留意这个细节，尤其是在追查某个预期行为没有触发时。

---

## DeepSeek V4-Flash × Codex CLI 的五层架构

配置背后是一套可组合的 Coding Agent 系统。把它拆成五层来看，能清楚地知道哪里可以替换、哪里有约束、哪里的控制权在你手上。

| 层 | 本文组件 | 开放或可替换 | 约束 |
| --- | --- | --- | --- |
| **Model weights** | DeepSeek V4-Flash | Repo + weights MIT | 约 304B 参数；权重可用不等于本地可运行 |
| **Inference** | DeepSeek hosted API | Codex provider 可切换 | 官方接入路径是托管推理，self-host 另有工程成本 |
| **Protocol** | Responses subset + `apply_patch` | 跨公司连接 | 兼容性是梯度，部分字段/工具 silent ignore 或不支持 |
| **Agent harness** | Codex CLI / `codex-core` | Apache-2.0，可检查修改 | Harness 定义 tool loop、context、retries、sandbox、approvals |
| **Execution** | Local repo + sandbox + approvals | 用户控制本地动作 | 输入仍跨越 inference boundary，本地执行不等于本地推理 |

翻开这两份许可证是件有意思的事：一份来自中国 AI 团队，一份来自美国大型科技公司，都落地在宽松的开放许可证上，都允许检查、修改和商业组合，没有强制 copyleft 约束。两份许可证都允许组合。

---

### 许可证确立的是组合权，技术兼容性另有边界

MIT 权重和 Apache-2.0 harness 解决的是**法律层面的组合权**。MIT 权重不能证明 DeepSeek API 与 Codex 在协议层面完全兼容，也不保证任务行为。许可证是前提条件，不是技术能力证明。

这条分界线有实际意义：你看到两份开放许可证，知道可以自由组合；但你还需要翻兼容性表格，才知道哪些字段实际生效、哪些会被 silent ignore。许可证和协议是不同层面的事情，各自回答不同的问题。

---

### 协议对齐的是互操作，不是统一行为

Codex 使用 `wire_api = "responses"` 与 provider 通信。DeepSeek 需要"说 Responses 的语言"，并为 Codex 明确适配 `apply_patch`，这是双方在协议层的主动对齐。

但从兼容表可以看到，`previous_response_id` 不支持意味着跨请求的状态链接无法通过 API 维护；built-in tool types 被忽略意味着 Codex 与某些 OpenAI 原生工具的交互路径在 DeepSeek 端不生效。**兼容是梯度**，不是全量支持。

---

### 推理服务决定运行控制

官方接入路径使用 `https://api.deepseek.com/`，即 DeepSeek 托管推理。本教程的配置完全建立在这条路径上。

MIT 权重理论上允许 self-host，但官方 vLLM 示例使用一台 4×GB300 节点作为参考配置，这说明官方 recipe 对应的算力规模。304B 参数规模的本地部署是另一项独立的工程，与本教程无关，不在此展开。

**核心结论**：模型权重开放不等于运行控制在本地。使用托管 API 时，推理过程在 DeepSeek 服务端执行，你的输入跨越了 inference boundary。Codex 在本地控制的是 tool loop、sandbox、approvals 和文件执行，不是模型推理本身。

---

### Harness 决定 Agent 行为，也决定评测单位

`codex-core` 的 README 说明它实现供 Rust Codex UIs 使用的业务逻辑；`codex-protocol` 定义 core/TUI internal types 和 app-server external types。这意味着 tool loop 的调度方式、上下文管理策略、重试逻辑、sandbox 策略和 approval 流程都在 Codex CLI harness 层定义，不在模型层定义。

**一个重要推论**：DeepSeek 官方 Agent benchmark 使用 DeepSeek Harness（minimal mode）运行，不是 Codex CLI。因此官方 Agent 评分的单位是 model + DeepSeek harness + tools + 测试环境，不能直接对应成 Codex CLI 的预期表现。

正确的评测单位应该是：**model + harness + tools + environment**。把 harness 换成 Codex，即使模型相同，行为也未必相同。这既是架构理解的关键，也是不要凭 benchmark 数字预测 Codex 表现的原因。

---

## 配置核对与五层 Ownership Checklist

完成本教程后，用以下清单确认你的配置状态和对各层的控制权理解：

### 配置核对

- [ ] `codex --version` 显示 0.144.0 或更高
- [ ] `~/.codex/deepseek-models.json` 存在，内容来自 DeepSeek 官方 Codex 文档，JSON 可解析
- [ ] `~/.codex/deepseek-v4.config.toml` 存在，包含完整的 `[model_providers.deepseek]` 配置块
- [ ] Profile TOML 中没有任何明文 API Key
- [ ] 使用 `read -rsp` 注入 Key，只在当前 shell 会话有效
- [ ] `[ -n "$DEEPSEEK_API_KEY" ] && echo "set"` 返回 `set`，但没有打印 Key 值
- [ ] 运行过 `codex --profile deepseek-v4` 确认 profile 被读取
- [ ] 原有的 `~/.codex/config.toml`（如有）未被修改
- [ ] 知道退出会话后运行 `unset DEEPSEEK_API_KEY`
- [ ] 知道运行普通 `codex` 可回到默认 provider

### 五层 Ownership 核对

| 层 | 你控制什么 | 你不控制什么 |
| --- | --- | --- |
| **Model weights** | 可查阅、引用、修改权重（MIT）| 推理计算在托管端执行 |
| **Inference** | 选择 provider（切换 profile）| 推理服务运行在 DeepSeek 服务端 |
| **Protocol** | 配置 `wire_api`，选择使用哪些 Responses 功能 | 部分不支持的参数可能被 API 静默忽略 |
| **Agent harness** | 可审查和修改 Codex 源码（Apache-2.0）| Harness 逻辑决定 tool loop 和 context 行为 |
| **Execution** | 本地 sandbox、approvals、repo 文件 | 执行前的推理决策在 inference boundary 之外 |

---

## 官方参考资料

- DeepSeek V4-Flash model repository & MIT license：[https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731](https://huggingface.co/deepseek-ai/DeepSeek-V4-Flash-0731)
- DeepSeek Codex 集成指南（model catalog 来源）：[https://api-docs.deepseek.com/quick_start/agent_integrations/codex](https://api-docs.deepseek.com/quick_start/agent_integrations/codex)
- DeepSeek Responses API 文档（兼容性范围）：[https://api-docs.deepseek.com/guides/responses_api](https://api-docs.deepseek.com/guides/responses_api)
- Codex CLI repository & Apache-2.0：[https://github.com/openai/codex](https://github.com/openai/codex)
- Codex Core README（harness 业务逻辑）：[https://github.com/openai/codex/blob/main/codex-rs/core/README.md](https://github.com/openai/codex/blob/main/codex-rs/core/README.md)
- Codex Protocol README（internal/external types）：[https://github.com/openai/codex/blob/main/codex-rs/protocol/README.md](https://github.com/openai/codex/blob/main/codex-rs/protocol/README.md)
- Codex Advanced Configuration（named profile 与 custom provider）：[https://learn.chatgpt.com/docs/config-file/config-advanced](https://learn.chatgpt.com/docs/config-file/config-advanced)

---

## 相关阅读

- [Codex 新手指南](/zh/docs/tutorials/codex-guide/)
- [Coding Agent Harness 完整指南](/zh/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent 沙箱安全](/zh/docs/tutorials/coding-agent-sandbox-security/)
- [Coding Agent 工程：从 Prompt 到 Graph](/zh/docs/agent-engineering/)
