---
title: "在本地运行 Kev：用一个 Choice 请求给客服工单分类"
description: "在 Apple Silicon Mac 上本地部署 Kev-0.8B，通过 Choice API 给客服工单分类，查看模型信息，理解概率、confidence 与应用分流方式。"
keywords:
  - "Kev 本地部署"
  - "Kev-0.8B"
  - "Apple Silicon"
  - "本地决策模型"
  - "工单分类"
sidebar_position: 33
tags: [tutorial, agent-engineering, local-models]
---

# 在本地运行 Kev：用一个 Choice 请求给客服工单分类

如果你的应用或 Agent 需要在本机把一段文本迅速“分派”到不同的处理分支，而又不想依赖外部 SaaS 或暴露私有数据，Kev-0.8B 是一个极轻量的选择。它基于 Qwen/Qwen3.5-0.8B-Base，返回结构化判断，非常适合用来做客服工单分类、路由判断这类“一锤定音”的决策点。

本教程的目标非常具体：

- 在 Apple Silicon Mac 上本地启动 Kev-0.8B（Kev 官方还另有 4B、9B 等版本）。
- 通过 HTTP 发送一个 Choice 请求，模拟一条真实的客服工单。
- 解读模型返回的部门、概率分布以及 confidence 字段，判断是否适合自动分流。
- 读完并能直接在你的本地环境中复现整个过程，并快速改为你自己的业务规则。

## 前置准备：工具与环境

开始前请确认你手头有以下东西：

- Apple Silicon Mac（M1/M2/M3 等）
- Git
- uv（推荐 Python 包管理工具）
- Python 3.12 或 3.13
- 至少一次下载模型所需的稳定网络环境

在终端中快速检查一遍：

```bash
git --version
uv --version
python3 --version
```

如果某项缺失，先补齐。本文示例基于 Kev-0.8B，官方说明它能在 M 系列芯片上轻松运行；如果你打算后续升级到 4B，再参考 32 GB RAM 的硬件建议。

## 第一步：克隆并安装服务依赖

Kev 是一个 Python 项目，结构清晰，启动过程也很直接。先把它拉下来：

```bash
git clone https://github.com/jaredpalmer/kev.git
cd kev
```

这里的关键命令是 `uv sync --extra serve`，它会根据仓库的 `.python-version`（3.13）同步项目依赖，并额外安装服务所需的环境：

```bash
uv sync --extra serve
```

在 Apple Silicon 上这一步会自动包含 MLX 相关依赖；首次运行服务时，Kev 会自动下载适配器和基础模型文件。请确保网络连接通畅，耐心等待几到十几分钟。

## 第二步：启动本地 Kev 服务

在**第一个终端窗口**中运行以下命令（端口示例为 8009）：

```bash
uv run --extra serve python -m kev.serve \
  --run jaredpalmer/kev-0.8b \
  --port 8009
```

服务启动后，你会看到类似这样的日志：

- 模型已加载（Apple Silicon 使用 mlx 后端）
- 监听地址与端口（默认绑定 127.0.0.1）

保持这个终端在前台运行，它是整个实验的“后台引擎”。

## 第三步：确认服务与模型状态

打开**第二个终端窗口**，用 curl 查看模型注册信息：

```bash
curl http://127.0.0.1:8009/v1/models
```

你会看到类似 JSON 数组的回包，其中包含：

- `name`：模型标识
- `run` / `base`：底层 checkpoint 信息
- `device` / `backend` / `dtype`：硬件与后端类型

示例片段（结构示意）：

```json
{
  "models": [
    {
      "name": "jev-latest",
      "run": "jaredpalmer/kev-0.8b",
      "base": "Qwen/Qwen3.5-0.8B-Base",
      "device": "mps",
      "backend": "mlx",
      "dtype": "bfloat16"
    }
  ]
}
```

这个步骤不需要你写代码，但很重要：它让你看到服务真的在跑、模型也在正确加载。后续所有请求都默认绑定 `http://127.0.0.1:8009`。

## 第四步：构造一个“客服工单”Choice 请求

现在进入核心部分：用一个真实的工单文本测试分类能力。下面示例来自社区实践，模拟一位客户因重复扣款和退款未到账而投诉的工单。

我们在 `/v1/systemone` 端点使用 JSON 格式传入：

- `model`：指定模型选择 `jev-latest`（与本地 checkpoint 对应）
- `state`：待判断的原始文本
- `questions`：一组问题 ID；本题只为团队分类，用 `choice` 类型并给出候选准则

curl 命令如下（将整段 JSON 作为 `-d` 的内容传入）：

```bash
curl http://127.0.0.1:8009/v1/systemone \
  -H 'Content-Type: application/json' \
  --data-binary @- <<'JSON'
{
  "model": "jev-latest",
  "state": "Hi, I was charged twice for my March invoice (order #4471) and the refund I was promised last week still hasn't arrived. I've emailed three times. Please fix this today or I will dispute the charge with my bank.",
  "questions": {
    "team": {
      "type": "choice",
      "instructions": "Which team should handle this ticket?",
      "criteria": {
        "Billing": "Payments, invoices, refunds",
        "Technical": "Bugs, outages, integrations",
        "Sales": "Pricing questions, upgrades, new contracts"
      }
    }
  }
}
JSON
```

第一次运行时，你会看到：

- Kev 返回 JSON 结果（服务启动日志会报告 checkpoint、设备、backend、dtype 和监听地址）
- curl 返回 JSON 结果

下面重点解读这个 JSON 结果。

## 第五步：读懂返回结果——choice、probabilities 与 confidence

在 mandu5 于 2026 年 9 月 24 日使用 Apple M1 Pro（16 GB 内存，MLX bfloat16）运行 Kev-0.8B 的一次典型实验中（公开记录参见 https://github.com/mandu5/jevcompat/blob/main/results/kev/report.json），其返回的 JSON 回包中的 `answers` 部分呈现如下特征：概率为 0.9671、置信度为 0.9507。

```json
{
  "answers": {
    "team": {
      "type": "choice",
      "choice": "Billing",
      "confidence": 0.9507,
      "probabilities": {
        "Billing": 0.9671,
        "Technical": 0.0142,
        "Sales": 0.0187
      }
    }
  }
}
```

这几个字段的含义与应用方式非常关键：

- `answers.team.type`：始终为 `"choice"`，表示这是一个多候选选择问题。
- `answers.team.choice`：**核心字段**。模型最终选定的部门标签，这里是 `"Billing"`。你的应用读取这个值来决定路由或触发后续流程。
- `probabilities`：每个候选标签对应的概率分布。三个候选加起来约等于 1.0（浮点误差范围内）。
- `confidence`：对“集中程度”的度量。它的计算逻辑大致为：

  - 若 n 为候选数，则基础均匀概率 p_uniform = 1 / n
  - confidence ≈ (max_prob − p_uniform) / (1 − p_uniform)

  在示例中：
  - max_prob = 0.9671
  - n = 3 → p_uniform ≈ 0.3333
  - confidence ≈ (0.9671 − 0.3333) / (1 − 0.3333) ≈ 0.9507

  这个字段帮助你快速判断“模型是否非常明确”：
  - 高 confidence（如 > 0.9）→ 适合自动分流
  - 低 confidence（如 < 0.6）→ 更适合标注人工复核，或要求用户补充信息

注意：**business accuracy**（业务准确率）不是由 confidence 直接保证的；你需要用带正确答案的历史样本去验证阈值。confidence 只表示模型内部概率分布有多“笃定”。

## 第六步：把接口接入到你的应用或 Agent

一旦本地跑通，接入方式就很简单：在你的 Python/JS/Go/Rust 等应用中发起 JSON POST 到 `/v1/systemone`。伪代码示例（Python + requests）：

```python
import requests

payload = {
    "model": "jev-latest",
    "state": "Hi, I was charged twice for my March invoice...",
    "questions": {
        "team": {
            "type": "choice",
            "instructions": "Which team should handle this ticket?",
            "criteria": {
                "Billing": "Payments, invoices, refunds",
                "Technical": "Bugs, outages, integrations",
                "Sales": "Pricing questions, upgrades, new contracts"
            }
        }
    }
}

resp = requests.post(
    "http://127.0.0.1:8009/v1/systemone",
    json=payload,
)
data = resp.json()

team_choice = data["answers"]["team"]["choice"]
conf = data["answers"]["team"]["confidence"]

if conf > 0.85:
    # 自动分流
    route_to_team(team_choice)
else:
    # 人工复核或二次确认
    send_to_human_review(data)
```

对于 Agent 或 Workflow 引擎，你可以：

- 将 `answers.team.choice` 映射为状态机中的 `next_state`。
- 用 `confidence` 作为是否触发“不确定路径”的判断条件。
- 把 `criteria` 做成可配置 JSON，无需改代码就能调整业务规则。

## 第七步：从 0.8B 到更大模型的选择

本教程从 0.8B 起步，因为：

- 在 M 系列 Mac 上启动快、内存占用低
- 对“明确分类任务”已经足够好
- 官方建议从 4B 开始用于更复杂任务；若你机器合适（约 32 GB RAM），只需把启动参数中的 `--run` 换成：

  ```bash
  --run jaredpalmer/kev-4b
  ```

核心接入逻辑完全一致。

## 总结与下一步

读完这篇教程，你应该已经能够：

1. 在本地 Mac 上从零启动 Kev 服务（含模型下载）。
2. 通过 `/v1/models` 查看加载的模型及后端信息。
3. 构造一个 Choice 请求，把一段工单文本发送给 Kev。
4. 从返回结果中准确读取：
   - `answers.<question_id>.choice`：自动分流的目标标签
   - `probabilities`：各候选分布
   - `confidence`：判断是否适合完全自动化
5. 在自己的应用或 Agent 中接入这一接口，并根据 confidence 设置“自动 vs 人工”的分界条件。

下一步你可以：

- 替换 `state` 为你们真实的客服工单样例，观察分类稳定性。
- 调整 `criteria`，扩展更多业务维度（如优先级、SLA 等级等）。
- 当需要处理更复杂的多意图判断时，可将 Kev 作为决策节点嵌入由应用程序或 Agent harness 编排的 Jev 工作流中，利用其返回的结构化决策输出驱动后续动作。

本地跑通 Choice 请求，就是让模型真正从“可聊的玩具”变成“可信的组件”的第一步。

## 延伸阅读

- [Jev 能帮 Coding Agent 做什么？](/zh/blog/jev-coding-agent-workflow/)
- [Coding Agent Evals Guide](/zh/docs/tutorials/coding-agent-evals-guide/)
