---
title: "Hermes Agent 入门：从安装配置到第一次本地项目阅读"
description: "安装 Hermes Agent、配置模型提供商与本地终端，在五文件 Python 练习中核对源码引用和命令预测，再学习退出、恢复会话与常见问题排查。"
keywords:
  - "Hermes Agent 入门"
  - "Hermes Agent 安装"
  - "Hermes CLI"
  - "本地代码阅读"
  - "Hermes 模型配置"
sidebar_position: 36
tags: [tutorial, agent-engineering, hermes]
---

# Hermes Agent 入门：从安装配置到第一次本地项目阅读

本文面向已在 Linux、macOS 或 WSL2 终端中熟练使用 Bash/Zsh，拥有一个模型提供商账户与一个小项目的开发者。目标是让你在一篇教程里完成：安装并检查 Hermes CLI、完成 provider/model 配置、核对工作目录和工具、完成一次带文件依据的阅读任务，并掌握如何退出、恢复会话以及处理常见配置问题。

读完应能做到的事情：
- 用一条命令安装 Hermes Agent（跳过浏览器组件与交互式 setup）。
- 在会话外完成提供商/模型认证与选择。
- 设置终端 backend 为本地执行，确保命令在本机权限下运行。
- 在一个真实项目中启动会话，让 Hermes 真正读取项目文件。
- 给出一个可对照源码检查的提问示例，并用另外的命令行结果来验证。
- 知道如何退出会话、继续上一轮会话以及排查“找不到命令”、“读不到文件”等常见问题。

> 注：Hermes Agent 是可接入不同提供商和模型的 Agent 应用。模型能力（包括上下文长度、工具调用支持）与服务费用取决于你选择的提供商与模型。本文以 OpenRouter 为例说明配置流程，你可以替换为自己的提供商。

---

## 一、安装 Hermes Agent（POSIX/WSL2 风格）

安装 POSIX 源码时需要 Git、curl、tar 与 SHA-256 校验工具；部分系统还需编译器或开发库。安装器会自动管理所需的 Python 和 Node，默认跟踪 main 分支，可用 `hermes --version` 查看实际版本。原生 Windows 同样支持 Hermes，对应方法请查阅 [https://hermes-agent.nousresearch.com/docs/getting-started/installation](https://hermes-agent.nousresearch.com/docs/getting-started/installation)。

Hermes 提供官方安装脚本，能自动管理 Python、Node 等运行依赖。我们采用最精简的 POSIX 安装方式，跳过浏览器组件下载与交互式 setup/gateway 阶段：

```bash
curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser --non-interactive
```

安装完成后：
- 默认 launcher：`~/.local/bin/hermes`
- 程序源码：`~/.hermes/hermes-agent/`
- 数据目录：`~/.hermes/`

由于只加了 `~/.local/bin` 到 PATH，你可能需要重新加载 shell 配置或新开终端：

```bash
# Bash 用户
source ~/.bashrc

# Zsh 用户
source ~/.zshrc
```

如果不确定是否生效，直接测试：

```bash
hermes --version
```

若提示“command not found”，请检查 `~/.local/bin` 是否在 `$PATH` 中，或重新加载配置。

---

## 二、完成模型提供商与模型选择（会话外配置）

在正式用 Hermes 聊项目之前，先在会话外配置好模型：

```bash
hermes model
```

你会被引导：
1. 选择已支持的提供商（例如 OpenRouter）。
2. 完成该提供商的认证（OpenRouter 需要你输入/确认 API key）。
3. 选择具体的模型。

关键要求（官方文档中的硬性条件）：
- 模型必须支持工具调用（tool calling）。
- 上下文长度至少 64,000 tokens。

在终端运行 `hermes model` 选择提供商（本文以 OpenRouter 为例），输入该提供商的 API key，并从当前可用列表中挑选支持工具调用、上下文不少于 64,000 tokens 的模型。配置会立即保存，后续会话自动复用；若需更换 provider 或认证方式，再在外部执行 `hermes model`，而会话内的 `/model` 仅用于切换已配置好的模型。

配置完成后，Hermes 会把 provider/auth 信息持久化在：
- 常规配置：`~/.hermes/config.yaml`
- API secrets：通常保存在 `~/.hermes/.env`
- OAuth 状态：对应提供商的认证文件

---

## 三、设置终端 backend 与工作目录

### 3.1 本地终端 backend

Hermes 支持多种终端 backend（例如 Docker、Sandbox 等），本篇采用“local”模式：即所有命令在本机当前用户权限下执行，适合个人开发场景和可控的小项目。

设置方式：

```bash
hermes config set terminal.backend local
```

说明：
- `local` 表示使用本机 shell 执行终端命令，适合常规编程与文件操作。
- 设置 backend 为 local 时，终端命令将以本机当前用户的权限运行。进入项目目录、以及“只分析不改文件”的提示，本质上都不是操作系统权限隔离；请求约定了本次任务的目标与操作边界。
- 你可用一个可恢复的小项目完成第一次任务，避免误删重要代码。

### 3.2 确认配置

可以检查一下当前配置摘要：

```bash
hermes doctor
```

它会提示依赖与常见配置问题（如有）。如果一切正常，继续下一步。

---

## 四、在真实项目中启动 Hermes 会话

### 4.1 进入你的项目目录

打开终端，进入你希望 Hermes 分析的实际项目：

```bash
cd /path/to/your/project
```

替换为真实路径。例如：

```bash
cd ~/projects/my-python-tool
```

### 4.2 启动会话

在项目目录下执行：

```bash
hermes
```

欢迎信息会显示：
- 当前使用的模型（取决于你刚才的配置）
- Terminal backend（应显示 local）
- 工作目录（应为你当前的 `/path/to/your/project`）
- 可用工具列表（包括文件读取、终端命令等）

如果工作目录不是预期的项目目录，请确认：
- 是否真的 `cd` 到了目标目录
- `terminal.backend` 是否设置为 `local`
- 会话内输入 `/tools` 查看当前启用的工具（需要文件读取与终端能力）

---

## 五、第一次任务：让 Hermes 阅读并解释你的项目

现在我们来做一个“可对照源码检查”的任务。

### 5.1 推荐提问方式

在会话中输入如下指令（可根据你的项目微调）：

```text
请基于当前工作目录的项目结构，完成以下任务（本次只分析，不修改任何文件）：

1）用“文件:行号”的格式列出你认为最关键的文件：
   - main / entry point
   - 配置与数据结构定义
   - 核心逻辑流程

2）解释现有运行方式（如：如何启动、输入是什么、输出是什么）。

3）预测执行以下两个命令后可能得到的结果，并说明依据：
   - python3 main.py
   - python3 main.py --status done

4）指出与 Hermes 能进一步协助的相关接口或任务定义（例如 tasks.json / query 逻辑等），让后续问题更有针对性。
```

这个提问的设计要点：
- 明确要求“只分析，不修改文件”，避免误触变更代码。
- 要求“文件:行号”格式，便于你对照源码检查。
- 让模型给出“预测结果”，然后你在另一个终端运行真实命令进行对比，这是验证其理解是否准确的关键步骤。

### 5.2 对照结果：用本站 AI Coding Club 练习 ZIP 检验思路

如果你还没有合适的项目，可以用本站提供的五文件练习（适合第一次熟悉）：

- 下载链接：<a href="https://aicoding.club/examples/codebase-reading-lab.zip">代码阅读练习 ZIP</a>
- 解压后进入包含 `main.py` 的目录。

项目结构大致如下：
- `main.py`
- `repository.py`
- `query.py`
- `tasks.json`
- `README.md`

运行逻辑（作为对照基准，后面你可以验证）：
- `main()` 读取命令行参数，默认 `--status open`。
- 通过 `repository.py` 的 `load_tasks` 读取 UTF-8 JSON。
- 由 `query.py` 的 `select_tasks` 按状态过滤、按 id 排序。
- 最后输出 JSON。

真实命令对照（在另一个终端中执行）：

```bash
# 默认 open 状态
python3 main.py

# 只选择 done 状态的
python3 main.py --status done
```

预期结果（id 序列）：
- `--status open`：T1、T3
- `--status done`：T2

你可以在 Hermes 会话中让模型先“预测”，然后再运行上述命令，对比它列出的 id 是否一致。不一致的地方往往是理解偏差的线索。

### 5.3 检查文件读取是否真正生效

你可以进一步追问：

```text
请分别引用以下三个文件的关键内容（文件:行号）来支撑你的解释：
- main.py 中的参数解析部分
- repository.py 中的 load_tasks 函数入口
- query.py 中的 select_tasks 过滤逻辑
```

核对结果时先查看实际触发的工具调用及返回的文件内容，再逐条对照文件名、行号及运行结果。文件工具的可用性以 `/tools` 为准；仅给出正确文字不足以证明启用了哪一种具体文件工具。

---

## 六、退出会话与继续/恢复会话

### 6.1 正常退出

在会话内输入：

```text
/quit
```

这会结束当前聊天会话，并保存状态到本地会话文件。

注意：
- `Ctrl+C` 是在执行中中断当前命令/任务，并不等于“退出整个程序”；在某些上下文下可能只是切回 shell。

### 6.2 查看与恢复会话

之后回到同一个项目目录，可以用以下方式继续：

```bash
# 查看所有会话（按时间或 ID）
hermes sessions list

# 继续当前工作区最相关的会话（优先匹配终端/目录上下文）
hermes --continue

# 或按实际 session_id 恢复
hermes --resume <session_id>
```

提示：
- `--continue` 会优先选择与当前终端/工作区上下文匹配的会话，而不是无条件选全局最近一次聊天。
- 若不确定 ID，先用 `sessions list` 查看。

---

## 七、常用配置与工具命令速览

### 7.1 会话外配置

```bash
# 模型/提供商配置
hermes model

# 检查配置与依赖（适合排错）
hermes doctor

# 更新 Hermes（可选，先做通第一次任务再按需更新）
hermes update --check      # 只检查是否有更新
hermes update              # 执行更新
```

### 7.2 会话内命令

```text
/model          # 切换已配置的模型
/tools          # 查看当前启用的工具列表
/quit           # 退出会话
```

### 7.3 会话外工具配置

若发现能聊天但读不到文件，或工具能力异常：

```bash
hermes tools      # 配置启用的工具（包括 read_file、terminal 等）
```

结合 `doctor` 的输出一起判断。

---

## 八、常见问题排查

按症状快速定位：

1. **找不到命令 `hermes`**
   - 检查 `~/.local/bin` 是否在 `$PATH` 中。
   - 重新加载 shell 配置（Bash：`source ~/.bashrc`；Zsh：`source ~/.zshrc`）。
   - 确认安装脚本执行成功（`hermes --version` 回显）。

2. **认证通过但模型不响应**
   - 回到会话外：`hermes model`，检查是否选对提供商与模型 ID。
   - 核对 API key 是否有效（必要时在提供商官网验证）。
   - 确认模型支持工具调用和足够上下文长度。

3. **能聊天但没读项目文件**
   - 确认 `cd` 到了正确的项目目录。
   - 检查 `terminal.backend` 是否为 `local`。
   - 会话内输入 `/tools` 确认 read_file / terminal 已启用。
   - 必要时退出后用 `hermes tools` 重新配置。

4. **自定义 endpoint 或自托管模型**
   - 核对 URL、model ID、工具调用格式与上下文长度。
   - 查看官方文档中关于自定义 provider 的字段要求（integration schema）。
   - 使用 `doctor` 查看连接测试日志。

---

## 九、小结

- 用一条命令安装 Hermes，跳过浏览器组件：`curl -fsSL https://hermes-agent.nousresearch.com/install.sh | bash -s -- --skip-browser --non-interactive`
- 在会话外完成模型配置：`hermes model`（provider/auth + model）
- 设置终端 backend 为 `local`，确保命令在本机执行。
- 在真实项目目录下启动会话：`cd /path/to/project && hermes`
- 用“文件:行号”+“预测结果”的提问方式，结合另一个终端的真实运行进行对照验证。
- 退出用 `/quit`；继续会话用 `hermes --continue` 或 `--resume <session_id>`。
- 排错按症状：PATH → `hermes model` → work directory/backend → `/tools` → `hermes doctor`

完成这篇教程，你已具备了使用 Hermes Agent 在本地环境中进行可信项目阅读、命令预测与代码解释的基本能力。下一步，你可以尝试更复杂的任务：比如让 Hermes 生成测试用例、分析性能瓶颈、或基于项目结构提出重构建议——但前提始终是：始终对照源码与真实命令行结果进行校验，让模型成为“可验证的协作者”，而不是“黑盒答案机”。

## 延伸阅读

- [AI 编程 Agent 新手路线](/zh/docs/tutorials/ai-coding-agent-beginner-guide/)
- [读懂陌生代码库：沿一个命令找到调用链](/zh/docs/tools/prompt-engineering/templates/#read-codebase)
- [用 Jevgrep 按行为定位代码](/zh/docs/tutorials/jevgrep-code-discovery/)
