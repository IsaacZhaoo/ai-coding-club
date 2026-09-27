---
title: "用 OpenAI Agents API 做一个真正“活”的编程助手：从创建脚本到断线续写"
description: "使用 OpenAI Agents API 在托管沙箱中创建并运行脚本，在持久会话里继续修改，核对执行输出、下载产物，并在事件流中断后恢复工作。"
keywords:
  - OpenAI Agents API 教程
  - 持久化编程助手
  - OpenAI 托管沙箱
  - Agents API Python
  - Agents API 产物下载
sidebar_position: 39
tags: [tutorial, openai, agent-engineering]
---

# 用 OpenAI Agents API 做一个真正“活”的编程助手：从创建脚本到断线续写

> 适合读者：会用 Python、有 OpenAI Platform 项目经验的开发者  
> 读完你将能够：在托管沙箱里生成并运行一个脚本，查看真实输出；接着在同一会话里加入 `--max-depth` 选项、运行验证、下载更新后的文件；即便事件流中断，也能从保存的 session 和 items 中找回工作。

---

## 一、为什么是“Agents API”而不是“普通 Chat”？

OpenAI 的 Agents API 本质上不是另一个聊天层：它是一个**可编排、可持久化的编程工作台**。  
当你调用它时：

- 你在应用层调用的是托管的 Codex harness；
- 你的代码负责：创建会话、提交输入、消费事件流、下载产物；
- 沙箱工作区的文件在沙箱生命周期存续期间会在沙箱内保留；本教程所生成的产物（artifact）则是独立副本，即使沙箱过期仍可下载访问。


关键直觉：**你不再只是“问问题”，而是在“指挥一个带记忆的工作台”**。  
接下来的教程将带你走通这条主线：

1. 创建第一个 session，生成并运行 `tree.py`
2. 在同一 session 里继续迭代，添加 `--max-depth` 参数
3. 下载已发布到 `/workspace/outputs/tree.py` 的产物
4. 从保存的状态恢复并验证结果

全程使用 Python SDK：  
```bash
pip install --upgrade openai
```  
确保你的应用 API key 拥有以下权限（在 OpenAI Platform 中配置）：

- `api.agents.read`
- `api.agents.write`
- `api.responses.write`

Agents API 于 2026 年 9 月 10 日进入公开 beta。官方 quickstart 示例使用 gpt-6-astra 模型，确保你的环境拥有对该模型的访问权限。SDK 在调用时会自动添加 OpenAI-Beta: agents=v1 头信息。沙箱的推理与托管费用由模型用量和托管时长分别计费。运行代码前，请在应用终端设置环境变量 OPENAI_API_KEY，密钥由调用端提供，沙箱进程不需要它：

- Linux/macOS/WSL：`export OPENAI_API_KEY="your-api-key"`

---

## 二、初始化与核心事件消费工具

下面这段代码是后续所有操作的基础：创建会话、启动流、并定义一个通用的“事件消费者”。

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()

def consume(events):
    for event in events:
        # 调试用：打印 JSON，生产环境可改为 logger
        print(event.to_json(indent=None), flush=True)

        if event.type == "agent.session.created":
            Path("session-id.txt").write_text(event.session.id)

        if event.type == "error":
            raise RuntimeError(event.error.message)

        # 沙箱或会话本身失败，立刻上报
        if event.type in {"agent.session.failed", "agent.session.environment.failed"}:
            raise RuntimeError(event.type)

        # 主 turn 失败或取消时提前终止
        if event.type in {
            "agent.session.turn.failed",
            "agent.session.turn.cancelled",
            "agent.session.turn.completed",
        } and event.turn.subagent_id is None:
            if event.type != "agent.session.turn.completed":
                raise RuntimeError(event.type)
            # 主 turn 完成，返回 turn ID；实际输出另行核对
            return event.turn.id

    raise RuntimeError("Stream ended early; retrieve the saved session and items.")
```

**几个设计判断：**

- `session-id.txt`：在应用侧持久化 session ID，避免依赖内存变量。
- 一旦遇到非成功的 turn 事件，立即抛错，而不是继续消费。
- 使用 `to_json(indent=None)` 保证输出紧凑，便于日志管道处理。

---

## 三、第一轮任务：创建 `tree.py` 并运行它

### 3.1 调用会话接口

```python
with client.beta.agents.sessions.create(
    agent={
        "model": "gpt-6-astra",
        "instructions": "Write clean code, run it, and report the actual output.",
    },
    environment={"type": "openai_hosted"},
    input="Create tree.py, a Python script that prints a readable tree of the files in the current directory. Run it and show me the output.",
    stream=True,
) as events:
    first_turn_id = consume(events)
```

这里的关键点：

- `model`: 必须使用已授权的模型（示例为官方 quickstart 使用的 `gpt-6-astra`）。
- `environment.type`: 设为 `openai_hosted`，表示使用托管 Linux 工作区。
- 托管环境的工作目录是 /workspace（并非文件系统根目录）。


### 3.2 查看沙箱中的实际结果

事件流结束后，不要仅凭 `agent.session.turn.completed` 就断定成功：

1. 登录应用终端或查看日志，确认：
   - 脚本被创建为 `/workspace/tree.py`
   - Python 已运行 `python tree.py`
   - 输出被完整打印（通常是当前目录的树状结构）
2. 检查沙箱文件是否存在且可读。

**注意：**  
`turn.completed` 只表示“逻辑上该 turn 已结束”，并不保证内部工具调用 100% 无损耗。因此，任何可靠流程都应该结合实际输出校验。

---

## 四、继续任务：在同一 session 里添加 `--max-depth` 选项

### 4.1 确认会话处于 `idle` 状态

```python
session_id = Path("session-id.txt").read_text().strip()

if client.beta.agents.sessions.retrieve(session_id).status != "idle":
    raise RuntimeError(
        "Inspect the session and wait for idle before the follow-up."
    )
```

这是防运行时冲突的简单但重要的检查。只有当会话处于 `idle` 时，提交新输入才不会干扰正在执行的 turn。

### 4.2 提交第二轮输入

```python
text = (
    "Add a --max-depth option to tree.py. Run python tree.py --max-depth 2 "
    "and report the actual output. Copy the updated script to "
    "/workspace/outputs/tree.py so I can download it."
)

with client.beta.agents.sessions.events.stream(session_id) as events:
    client.beta.agents.sessions.events.create(
        session_id,
        events=[{
            "type": "agent.session.input.message",
            "input": [{"role": "user", "content": [{"type": "input_text", "text": text}]}],
        }],
    )
    completed_turn_id = consume(events)
```

**要点：**

- 再次使用 `events.stream(session_id)`，而不是重新创建会话。
- 通过 `events.create` 向该 session 追加一条新消息。
- 同样用 `consume` 消费事件，拿到新的 `completed_turn_id`。

### 4.3 验证实际运行与文件产出

1. 查看第二轮的终端输出，确认：
   - `tree.py` 已被修改（例如增加 `argparse` 解析 `--max-depth`）
   - 命令 `python tree.py --max-depth 2` 被执行
   - 输出确实只展示两层深度
2. 检查 `/workspace/outputs/tree.py` 是否存在：
   - 当 agent 在第二轮将更新脚本复制到 `/workspace/outputs/tree.py` 时，该本轮（turn）结束即意味着文件固化；后续所有版本选取均依据 `turn_id` 加上完整路径进行，确保 `tree.py` 在 turn 完成后作为不可变 artifact 发布。

   - artifact 与 `turn_id` 和 `path` 绑定，不会随 session 刷新而改变。

---

## 五、下载产物：从 `/workspace/outputs/tree.py` 获取本地副本

```python
def download_artifact(client, session_id, turn_id, path, destination):
    # 查找匹配该 turn 和路径的 artifact
    for artifact in client.beta.agents.sessions.artifacts.list(session_id):
        if artifact.turn_id != turn_id or artifact.path != path:
            continue
        with client.beta.agents.sessions.artifacts.with_streaming_response.content(
            artifact.id, session_id=session_id
        ) as response:
            response.stream_to_file(destination)
        return
    raise FileNotFoundError(
        f"No artifact for {path!r} in turn {turn_id}"
    )

download_artifact(
    client, session_id, completed_turn_id, "/workspace/outputs/tree.py", "tree.py"
)
```

下载与输出相关的使用：

- download_artifact：通过 turn_id 和路径定位并拉取沙箱中的产物。
- stream_to_file：将响应流式写入指定的本地文件，支持断点续接逻辑由应用层实现（SDK 本身不保证断线续传）。
- 若未找到对应的产物，此处抛出 Python 内置 FileNotFoundError，以便你的主程序统一处理缺失产物。

下载 `tree.py` 后，请运行以下命令进行验收：

```bash
python tree.py --max-depth 2
```
该命令可验证脚本对输出深度的控制是否生效；请注意，`tree.py` 展示的是其运行时当前目录的文件树，沙箱环境与本地目录内容本就不相同，核对重点是“深度限制”而非文件名称的一致性。

---

## 六、断线恢复：从保存的 session 和 items 找回工作

### 6.1 什么是“断线”场景？

在实际部署中，可能遇到：

- 事件流连接断开（网络抖动、超时）
- 长期运行后进程被重启或调度器回收

恢复/重连会话时，分别读取以下内容：

- session：保存会话上下文与 agent 配置。
- items：保存消息记录、工具调用及其结果（用于还原对话状态）。
- 工作区文件：依赖沙箱生命周期；沙箱过期后不再保留。
- 已发布的 artifact：是独立快照，可通过 ID 和 turn_id 下载复用。

### 6.2 断线后恢复的基本流程

1. 使用单独 Python 进程或模块加载 `client` 并读取 `session-id.txt`
2. 查看会话状态和保存的 items：

```python
from pathlib import Path
from openai import OpenAI

client = OpenAI()
session_id = Path("session-id.txt").read_text().strip()

print(client.beta.agents.sessions.retrieve(session_id).to_json())

for item in client.beta.agents.sessions.items.list(session_id, order="asc", limit=100):
    print(item.to_json())
```

使用持久数据重建任务流程：

- items：检查已保存的消息、工具调用及其实际输出，判断当前应处的对话位置。
- session.status：读取状态是否为 idle，以决定是否可以继续输入或发起新 turn。
- turns：获取每个 turn 的状态、耗时与错误信息，辅助断点续传与审计。
- artifact IDs、turn_id、path：从 client.beta.agents.sessions.artifacts.list(session_id) 获取。
- 是否已下载产物由你的本地应用自行记录；此处只需按保存结果选择继续输入或调用 download_artifact / stream_to_file。

### 6.3 沙箱生命周期与 artifact 副本

根据官方文档，托管沙箱的生命周期遵循：

- 活跃期：只要有活动或 keep-alive 心跳，即可维持。
- 空闲超时：活动和 keep-alive 都停止约**一小时后**，沙箱可能被删除。
- 会话持久化 ≠ 文件系统永远在线；但已发布的 artifact 副本可独立下载。

因此，最佳实践是：

- 对每个关键版本（尤其是产出文件），立刻下载并记录 `turn_id` + `path`
- 在 session 彻底删除前，完成所有必要导出

---

## 七、事件流与状态检查的“坑”总结

| 现象 | 含义 | 应对 |
|------|------|------|
| 流关闭 | 仅断开客户端连接 | 可重新 `events.stream(session_id)`，但不会补回漏事件 |
| `agent.session.turn.completed` | 逻辑上该 turn 结束 | 仍需检查终端输出、文件是否存在、artifact 是否发布 |
| session 进入 `idle` | 可安全提交新输入 | 在继续第二轮前必须校验此状态 |
| HTTP 409 删除会话 | 设置/执行尚未完全结束 | 短暂等待后重试（建议上限如 3 次），并明确捕获其他错误先检查 |

### 取消当前 turn 但不销毁 session

```python
client.beta.agents.sessions.events.create(
    session_id,
    events=[{"type": "agent.session.input.cancel"}]
)
```

发送 agent.session.input.cancel 以取消正在运行的 turn，同时保留整个 session 以便后续恢复。等待 session.status 回到 idle 后再继续任务。

### 清理会话资源

在保存必要文件后调用：

```python
client.beta.agents.sessions.delete(session_id)
```

若删除时收到 HTTP 409 且设置/执行仍在运行，则短暂重试（最多三次）；其他错误请先排查。即使删除调用成功，服务端的物理清理仍可能异步继续，因此无需额外等待。

清理失败时建议保留 session ID。


---

## 八、从教程到真实任务：你可以怎么延伸？

上面的例子只是入口，Agents API 适合的场景包括：

- 交互调试与代码生成的链条在本方案下可以稳定构建。
- 数据工程类的工作文件仅在沙箱存续期间保留；关键版本应写入 /workspace/outputs 并发布为 artifact 或下载至本地长期存储。
- 审计流程可以结合 events 流与会话日志（session/items）建立，但需注意流中断导致的中间事件可能丢失且无法保证完整回放。

在替换为你自己的编程任务时，请保留三个明确的设计点：

1. **始终记录并校验“实际运行结果”**（stdout、exit code、文件变化）
2. **固定产物路径与 turn ID**，方便下载与版本追踪
3. **在长时间运行中定期保存 session ID 和关键 items 快照**，以应对断线或重启

---

## 九、官方参考索引

- Quickstart & 基础用法：[Agents API Quickstart](https://developers.openai.com/api/docs/guides/agents-api/quickstart)
- Session 管理与状态：[Sessions Guide](https://developers.openai.com/api/docs/guides/agents-api/sessions)
- 事件流与恢复策略：[Events and Recovery](https://developers.openai.com/api/docs/guides/agents-api/sessions/events)
- 文件与 Artifact 机制：[Files & Artifacts](https://developers.openai.com/api/docs/guides/agents-api/environments/files)
- 托管沙箱生命周期：[Hosted Sandbox Lifetime](https://developers.openai.com/api/docs/guides/agents-api/environments/openai-hosted)
- 会话管理最佳实践：[Manage Sessions](https://developers.openai.com/api/docs/guides/agents-api/sessions/manage)
- API 变更与版本记录：[API Changelog](https://developers.openai.com/api/docs/changelog)

## 延伸阅读

- [Coding Agent Harness 完整指南](/zh/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent Evals：把 Trace 变成质量门禁](/zh/docs/tutorials/coding-agent-evals-guide/)
