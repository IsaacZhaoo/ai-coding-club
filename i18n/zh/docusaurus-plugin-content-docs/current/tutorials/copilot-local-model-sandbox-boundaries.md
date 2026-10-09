---
title: "GitHub Copilot CLI 边界实验：本地沙箱与离线模式的确定性验证指南"
sidebar_label: "Copilot CLI 沙箱边界实验"
description: "用 Copilot CLI 1.0.94 与可下载实验包，对照本地沙箱策略、离线模式、文件读取和工具网络访问的实际边界。"
keywords: ["Copilot CLI", "本地沙箱", "离线模式", "本地模型", "沙箱策略"]
sidebar_position: 48
tags: ["tutorial", "coding-assistant", "agent-engineering"]
---

# GitHub Copilot CLI 边界实验：本地沙箱与离线模式的确定性验证指南

> **适用对象**：熟练使用 Linux/WSL 终端的开发者  
> **核心目标**：通过一套可重复运行的协议 fixture，直观理解 Copilot CLI 中“离线模式”、“本地沙箱策略”和“真实本地模型接入”之间的边界关系。  
> **交付物**：一次完整的实验执行 + 结果解读清单 + 部署本地模型前的检查要点

---

## 一、为什么需要这个实验？

GitHub Copilot CLI 的文档告诉你：“可以运行本地模型”、“支持离线”、“沙箱能限制网络访问”。但这些能力：
- **并不自动生效**：默认安装是“联网 + 调用 GitHub 云端 LLM + 关闭沙箱策略”。
- **彼此独立**：启用 `--sandbox` 不等于启用离线；接入本地 Ollama 模型也不等于沙箱生效。
- **容易误解**：很多用户以为 `COPILOT_OFFLINE=true` 就等于完全断网，或者认为 `/sandbox policy` 一定能阻止所有 subprocess 的网络调用。

本实验用一套**确定性协议 fixture**（不是真实 LLM，也不是复杂工作流）来验证这三者的交互。你只需要按顺序执行三个命令，就能得到清晰、可对比的 JSON 结果。

---

## 二、准备阶段

1. 下载与解压
- 获取实验包：
  <a href="/examples/copilot-boundary-lab.zip">下载边界实验包</a>
- 解压并进入目录：
  ```bash
  unzip copilot-boundary-lab.zip
  cd copilot-boundary-lab
  ```
- ZIP 内仅含三个文件，后续所有命令均在此目录下执行：
  - provider.py
  - probe.py
  - run_lab.py

2. 系统要求（最小集）
- 操作系统：Linux 或 WSL（需支持 unshare/nsenter）。
- 运行环境：Python 3.x、Node.js/npm。
- 沙箱相关：
  - bubblewrap ≥ 0.5.0（命令名：bwrap）
- 网络工具：slirp4netns。
*   对于`util-linux`包组（版本 ≥2.35），其提供的关键辅助程序为 `unshare` 与 `nsenter`，用于构建基础的命名空间环境。
*   网络策略所需的 `iptables`、`ip6tables`、`iptables-restore` 及 `ip6tables-restore` 工具则属于独立组件，并非由 `util-linux` 包组提供。
- TUN/TAP：/dev/net/tun 可读可写。
- 端口：回环地址 18761 空闲（provider 监听端口）。
- 重要提示：bwrap 的存在不代表沙箱一定能启动。若启动失败，请按实际错误信息补充缺失依赖或调整配置。

下一章将给出完整安装与执行流程；本章仅作环境与材料准备。

## 三、实验执行

下面是一次性执行所需的完整终端会话（确保仍在 copilot-boundary-lab/目录下）：

```sh
npm install --prefix runtime @github/copilot@1.0.94 --no-audit --no-fund
python3 run_lab.py --copilot ./runtime/node_modules/.bin/copilot
python3 -m json.tool lab-output/results.json
```

执行说明（关键行为与细节）：
- 第一条：需联网拉取运行时，本地 runtime 目录不会污染你现有的 CLI 安装。
- driver（run_lab.py）会创建一个新的 lab-output/目录（含 work/outside/config），并启动一个 provider。
- 实验室逻辑分两个独立 CLI 会话运行：
  - 先以 --no-sandbox 执行；
  - 再以 --sandbox 执行。
- 两会话共用同一套隔离于用户设置的 COPILOT_HOME=config 与 COPILOT_OFFLINE=true，并非每次会话都生成不同 home。
*   执行流由 `provider.py` 发起，向 Copilot CLI 返回固定的 bash 工具调用请求，CLI 随后启动 shell 执行 `probe.py`，待实验结束则由 `run_lab.py` 停止 `provider` 进程。
- 若 lab-output/已存在，重跑时会报错拒绝覆盖；此时需用 --output 指定新的输出目录。

## 四、结果解读

### 1. 实验结论对照（JSON 原样）

```json
{
  "version": "GitHub Copilot CLI 1.0.94.",
  "baseline": {
    "sandboxed": false,
    "outside_read": "OUTSIDE_SENTINEL_NOT_SECRET",
    "tool_network": "LOCAL_PROVIDER_REACHED",
    "workspace_read": "LOCAL_BOUNDARY_OK"
  },
  "sandbox": {
    "sandboxed": true,
    "outside_read": "FileNotFoundError",
    "tool_network": "URLError",
    "workspace_read": "LOCAL_BOUNDARY_OK"
  },
  "provider_requests": 4,
  "passed": true
}
```

### 2. 字段含义（直接对比）

- version：使用的 CLI 版本。
- baseline（--no-sandbox）：
  - sandboxed: false，明确未启用沙箱。
  - outside_read: 能读到预先放入的假标记 OUTSIDE_SENTINEL_NOT_SECRET。
  - tool_network: 成功触达本地 provider（LOCAL_PROVIDER_REACHED）。
  - workspace_read: 本地工作区读取正常（LOCAL_BOUNDARY_OK）。
- sandbox（--sandbox）：
  - sandboxed: true，启用沙箱策略。
  - outside_read: FileNotFoundError，表示隔离生效；对“外部标记”的访问被拒绝。
- `tool_network: URLError` → probe.py 中执行的 `GET http://127.0.0.1:18761/ping` 被策略拦截，无法到达 provider。
  - workspace_read: LOCAL_BOUNDARY_OK，本地工作区仍在允许范围内。

### 3. 行为解读（不夸大）

- “hello”测试只验证“读”的边界，不涉及写权限测试；因此结果仅说明“可被读取”与“不可被读取/访问”的两类情况。
- outside 文件是我们预先写入的假标记：读不到它，不代表所有外部或敏感数据都会被同等处理；也不代表任意被读文件都“不敏感”。
- FileNotFoundError 是当前 Linux+unshare/namespace 组合下的观察结果；并非所有平台在访问拒绝时都必须抛出该错误。
- loopback GET（内部回环请求）：
  - baseline 下可到达；
  - sandbox 下被策略拒绝（体现为 URLError）。
- provider_requests = 4，代表两个会话中共同向模型协议发起的 4 个 POST 请求，GET 不计入。

### 4. 通过标准（仅本实验）

要判定“本次实验”通过，需同时满足：
- 精确读出对应字段值（如 outside_read、tool_network、sandboxed 标记等）；
- sandboxed: true 在 --sandbox 会话中成立；
- provider_requests ≥ 4 且有回执。

注意：以上仅针对“文件/回环边界”的单一示例，并不等同于对外网访问或写权限的全面审计结论。

### 5. 配置结构说明（供理解用）

实验的隔离策略由 lab-output/config/settings.json 控制，主干结构如下（路径为示例占位，应以实际生成的文件为准）：

```json
{
  "sandbox": {
    "enabled": true,
    "allowBypass": false,
    "allowDevToolAccess": false,
    "auth": {
      "git": false,
      "gh": false
    },
    "userPolicy": {
      "filesystem": {
        "deniedPaths": [
          "/absolute/path/to/lab-output/outside"
        ]
      },
      "network": {
        "allowOutbound": false,
        "allowLocalNetwork": false
      }
    }
  }
}
```

这些是本实验显式施加的限制。产品本地沙箱默认通常是关闭的；启用后的默认策略一般允许 outbound 及 bypass 请求；仅加 --sandbox 不会自动复制上述全部限制。临时目录可能本身具备访问权限，因此本案例通过 deniedPaths 明确划出禁区。

## 五、核心结论

- 本实验展示的是“策略层边界”：通过 COPILOT_OFFLINE=true 关闭 GitHub 认证、遥测、web 工具调用、内置 GitHub MCP 与更新，但仍会向配置的 provider 发送提示词；若 remote provider 已联网，它仍可能接收上下文。
本实验的进程边界清晰地划分为三层：OS 沙箱内运行着 CLI 启动的 Shell 进程及其受支持的本地工具；OS 沙箱外则是 CLI 主进程负责调度以及 `provider.py` 提供的服务进程。内置的文件工具直接在 CLI 主进程内部调用，虽按策略执行最佳努力检查，但并不经过 OS 沙箱的文件操作拦截机制。最终结果表现为：位于沙箱内的 `probe.py` 无法访问 本地 provider，而位于沙箱外的 CLI 主进程依然能够正常建立与外部 `provider` 的连接。
- CLI 内置的文件工具在“主进程内”按策略 best-effort 检查路径，并非 OS 级别的隔离保障；因此其防护效果依赖配置正确与环境配合。

## 六、当你打算使用真实本地模型前

### 1. 前提条件（必须）
- 你的 provider 进程已经运行。
- 已安装目标模型，且该模型支持工具调用（tool calling）与流式输出。
- COPILOT_PROVIDER_BASE_URL 指向其 API 端点；COPILOT_MODEL 使用其准确标识名。

### 2. 会话内可用命令（在交互窗口中输入，不是 shell 子命令）
- /model：从 1.0.94-0 起可发现 Ollama 已有的受支持模型；需确认添加或切换模型，不会自动下载安装。
- /sandbox status：查看当前沙箱状态与策略摘要。
- /sandbox policy：查看当前生效的策略（不执行预览命令）。

### 3. 启动方式
- --sandbox 是会话级启动标记（flag），用于启用隔离；但具体限制仍需配合策略配置。
- 真实 provider 的协议错误不能靠“削弱沙箱”解决；需检查其是否支持预期的提示词/工具调用格式与流式响应。

### 4. 文档参考（描述性引用）
- [自定义模型及离线模式](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models)
- [本地沙箱](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)

使用上述资源前，请结合你的实际 provider 能力与组织策略进行验证。

## 七、官方参考（快速跳转）

- [GitHub Copilot CLI: Customize Copilot](https://docs.github.com/en/copilot/how-tos/copilot-cli/customize-copilot/use-byok-models)
- [Security, Governance & Network Settings](https://docs.github.com/en/copilot/concepts/security-governance-and-network-settings/about-cloud-and-local-sandboxes)
- [Using Local Sandboxing](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/using-local-sandboxing)
- [Configuring Local Sandbox Settings](https://docs.github.com/en/copilot/how-tos/cloud-and-local-sandboxes/configuring-local-sandbox-settings)
- [Discover Local Models in GitHub Copilot CLI](https://github.blog/changelog/2026-10-07-discover-local-models-in-github-copilot-cli/)

---

## 八、一句话总结（方便收藏）

**运行一次实验：** 三个命令 → **对比 baseline vs sandbox**：无沙箱时 subprocess 可访问外部路径与 localhost，启用策略后文件与网络被显式拒绝。  
**理解本质：** `COPILOT_OFFLINE` ≠ 断网/本地模型；`--sandbox` + 正确配置 = 真正的安全边界；真实本地模型需 provider 已就绪并支持 tool calling/streaming。
