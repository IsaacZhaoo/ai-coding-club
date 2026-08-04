---
title: "AI Agent 系统设计面试：从 Context、Tools 到 Loop、Graph 与权限边界"
description: "用逐步增加约束的练习题，准备 AI Agent 系统设计面试中的 Context、Tools、State、Loop、Graph、安全与验证。"
keywords:
  - AI Agent system design interview
  - Agent architecture interview
  - LLM system design
  - AI Agent 系统设计面试
  - Agent 架构
sidebar_position: 29
tags: [tutorial, career, agent-engineering, architecture]
---
# AI Agent 系统设计面试：从 Context、Tools 到 Loop、Graph 与权限边界

---

## 练习题

> **教学练习（合成题，不归因于任何公司）**
>
> 设计一个 Agent，能够接收仓库任务、读取代码、调用工具，并返回可验证的操作证据。

先别动手画组件。看一眼题目，你会发现它缺少几乎所有关键信息：任务由谁发起？输入是否有歧义？成功、拒绝和升级分别怎样定义？工具有哪些？哪些动作只读，哪些有写入副作用，哪些需要审批或可以回滚？发生错误时需要重建哪些事件？什么样的验证结果才能接受上线？

面对这类开放式题，一拿到就堆组件（"用 LangGraph 加 memory 加 MCP 服务"）的回答，会在后续追问中快速暴露：组件放在那里，但无法解释它们如何应对具体的失败模式。

本文的工作方式：**先把题目补成约束合同，再逐层推导架构**。每引入一个组件，都要回答它解决哪个约束、由谁负责、失败时怎样暴露、怎样验证。

---

## 决定链：贯穿全文的核心模型

有说服力的系统设计答案，应当让每一个工程决定都能追溯到一条链：

```text
Constraint
  → Decision
  → Owner / Component
  → Failure Mode
  → Evidence
  → Trade-off / Known Limit
```

这条链要求你把"我们需要 memory"变成：**什么约束驱动了 memory？由谁管理检索与保留策略？memory stale 时失败怎样暴露？靠什么证据验证？引入 memory 的代价是什么？**

组件名称可以作为讨论的索引，但答案还需要责任边界、失败路径和可验证的证据；仅仅列出名称，没有设计价值。

下面是一张可复用的答题模板，贯穿七轮演进：

| Constraint | Decision | Owner | Failure Mode | Evidence | Trade-off |
|---|---|---|---|---|---|
| `[题目中的真实约束]` | `[设计决定]` | `[model / harness / tool / state / runtime / human]` | `[可达失败]` | `[trace / eval / audit / diff / runtime signal]` | `[代价与残余风险]` |

---

## 第一步：先补成约束合同

在动手设计之前，先问清楚影响架构的问题：

**用户与任务层**：谁发起任务，输入格式是否固定，成功、拒绝和升级分别怎样定义？任务是否允许部分完成？

**时间、规模与质量层**：单轮还是 long-horizon？主要压力来自请求量、任务长度、tool calls、并发还是 state？latency、cost、failure 和人工介入的预算各是多少？

**环境、数据与副作用层**：代码、私有数据、外部服务、网络和凭据在哪里？哪些动作只读、哪些有写入副作用、哪些需要审批、哪些可以回滚？

**证据层**：发生错误时需要重建哪些事件？什么样的 eval / audit / runtime signal 才能接受上线？

当题目信息不足时，正确的做法是：陈述合理假设，并说明如果假设变化，设计怎样随之改变。比如，"如果任务是只读诊断，架构可以保持较小规模，重点放在 task contract、context selection、source reference、completion criteria 与 trace；加入写入后再扩展 tool enforcement、rollback 与 approval 路径"。

以下七轮演进，都在同一个合成练习系统上递进加条件。

---

## 参考架构（工作模型）

```text
Task Contract
  → Harness / Orchestrator
      ├─ Context Builder ← Memory / Durable Instructions
      ├─ Task State / Checkpoint Store
      ├─ Model / Action Policy ← Provider Boundary
      ├─ Tool Gateway → Sandbox / External Services
      ├─ Evaluator / Stop Guard / Retry Policy
      └─ Approval / Governor / Handoff
  → Structured Result

Trace / Audit 覆盖关键路径
Eval / Rollout 检查 outcome、关键 trajectory 与回归
```

这是本文的教学工作模型，各团队的实现术语可能不同。图中的每个节点都需要一条决定链；单独列出名称，不说明职责边界，没有设计价值。

---

## 四组技术边界：必须讲透

### 1. Model / Provider / Harness / Framework

这四个词经常被混用，但它们的职责截然不同：

- **Model**：根据当前 context 产生判断、计划或候选动作。context 影响 model 能判断什么；Tool gateway、runtime policy 与 authority scope 决定系统允许执行什么——可见范围与执行权限需要分开理解。
- **Provider**：负责模型访问与推理服务；provider 边界决定了哪些 API 特性可用，哪些限制需要 harness 处理。
- **Harness**：本文把 context、tools、state、control flow、permission 与 verification 的组织责任放在 harness。
- **Framework**（如 LangGraph、AutoGen 等）：实现选择，框架名称不能替代对以上职责的明确分配。

面试中说"我会用 LangGraph 管理这个流程"然后停在那里，等价于说"我会用 Python 解决这个问题"——它描述了工具，没有描述工程决定。

### 2. Context / Memory / State

- **Context**：一次模型调用真正可见的信息；窗口有限，选什么进去是核心工程判断。
- **Memory**：跨调用或跨会话保留与检索的信息；需要明确 scope（对谁可见）、provenance（来源与可信度）、retention（保留多久）和 staleness policy（过期如何处理）。
- **State**：任务进度、已执行动作、结果、checkpoint 和控制决定的权威记录；State 是恢复的基础，memory stale 不等于 state 错误。
- **Durable Instructions**：用于保存较稳定的规则和策略；被加载时成为 context 中的规则来源。

*以上是本文的工作定义，不代表行业统一标准。*

### 3. Tool / MCP / Runtime Enforcement

Tool contract 除 schema 之外，还需要说明语义、错误处理、idempotency（可否安全重试）和 side effect（写入范围）。Runtime enforcement 由授权检查、approval 流程、policy guard 和 sandbox 共同完成；fixture 和 eval 检查工具的实现和行为，但无法替代运行时的执行拦截。

MCP 规范 Tool 的交互协议与描述格式，但不自动提供授权控制、containment、业务语义校验和副作用治理。当前 MCP 规范中的 Tool annotations（如 `readOnlyHint`）是 hints，权限由 runtime enforcement 执行，两者职责不同，依赖 hints 作为安全边界是一个值得主动检查的误判。

### 4. Loop / Graph / Parallelism

本文用八字段描述 Loop：**aim**（这个 loop 在解决什么问题）、**state**（记录当前任务状态、已执行动作、evaluation 与剩余 budget）、**action policy**（基于当前 state 与 evaluator / environment feedback 选择下一步手段）、**evaluator**（持有独立于 executor 的 evaluation contract，可由确定性检查、规则、另一模型或人实现）、**budget**（最多多少轮或多少成本）、**stopping condition**（触发结束的具体条件）、**authority scope**（限定 loop 被允许触碰的动作、资源与目标边界）、**escalation**（超出 authority scope 或 budget 时的移交路径）。Runner 执行控制合同：调用 action policy、应用 evaluator 与 stopping condition、消耗 budget、检查 authority / escalation，并返回结构化 outcome；下一步手段由 action policy 提议或选择。

本文的 Graph 工作模型管理工作单元之间的 dependency、routing、merge、veto、approval 和 governor；图的节点可以是 Agent、函数、工具、evaluator 或审批步骤。并行条件来自 dependency graph 中可独立执行的分支；单纯增加 Agent 数量无法建立隔离或 merge authority，反而会扩大风险面。git worktree 只隔离 linked working tree 的 Git 状态；端口、数据库、cache、临时文件、credential 和外部资源仍需单独隔离。

---

## 七轮约束演进：同一系统如何生长

### 第 1 轮：只读诊断

**加入约束**：Agent 只能读取仓库内容，返回结构化诊断报告，不修改任何文件。

| Constraint | Decision | Owner | Failure Mode | Evidence | Trade-off |
|---|---|---|---|---|---|
| 只读，输出诊断报告 | 定义 task contract，明确 success / refusal / escalation | harness | 任务目标模糊，Agent 返回无法验证的"完成" | structured outcome，source reference，基础 trace | contract 越严格，处理边缘 input 的灵活性越低 |
| model 看不到全部代码 | context builder 只选相关文件片段，配合 completion criteria 判断输出是否满足 task contract | harness | 上下文缺失，引用错误，缺少 completion criteria 导致无法判断任务是否真正完成 | source reference 与 outcome 对照，完成条件检查记录 | 更多 context 提高覆盖，也增加 token 成本与噪声 |
| 需要区分 model 判断与 harness 控制 | 将 model、provider 和 harness 职责显式分开 | harness / provider adapter | 把框架名当答案，失去责任边界 | harness 日志独立于 model output | 分层增加实现复杂度，但减少调试盲区 |

这一轮架构可以保持较小规模，重点放在 task contract 定义清晰、context selection 可追溯、source reference 与 structured outcome 可对照、trace 覆盖调用路径。加入写入之后，才需要扩展 tool enforcement、rollback 与 approval。

---

### 第 2 轮：加入小型代码修改

**加入约束**：允许 Agent 对指定范围内的文件进行小型修改，但必须提供 diff 和验证结果。

引入写入的那一刻，三件事需要同时到位：allow scope（明确只允许修改哪些路径，harness 负责在工具执行前检查）、idempotency（tool contract 声明动作是否可以安全重试，写入前保存 rollback point），以及 runtime validation（写入后由 harness 执行 lint / compile / test，结果保存为 diff 和 tool event）。

这三层——allow scope 的边界定义、authorization 的运行时检查、fixture / eval 的行为验证——职责不同，不能互相替代。意外写入 allow scope 外的文件，或在 partial side effect 之后执行非幂等重试，是这一轮最直接的失败路径。Trade-off 是：allow scope 越窄越安全，但处理边界情况的灵活性随之下降；rollback point 增加存储和 state 复杂度；runtime validation 覆盖越全面，时间成本越高。

---

### 第 3 轮：任务跨多轮并接近 Context 上限

**加入约束**：任务需要多轮才能完成，单次 context 窗口装不下所有历史信息。

这一轮暴露了混淆 context、memory 和 state 的代价。

**Context selection**（Constraint：窗口有限；Owner：harness）：每轮只装当前决策需要的信息，多余历史不进入 context。失败路径是关键信息被截断，模型在错误前提下继续执行。Evidence 是 context diff 与 trace 对照 outcome。Trade-off：更紧的 selection 降低成本，但可能丢失需要的历史片段。

**Memory**（Constraint：跨轮次需要历史信息；Owner：harness）：保存可检索历史与长期信息，需要 provenance 和 staleness policy。失败路径是 stale memory 导致错误恢复，过期信息干扰新决策。Evidence 是 memory provenance record 与 staleness check。Trade-off：memory 检索增加延迟和复杂度，provenance 缺失时历史信息难以被审计。

**State**（Constraint：任务中断需要可恢复；Owner：harness）：保存权威任务进度与 checkpoint，与 memory 分开维护。失败路径是 state 丢失后无法从断点恢复，重启时重复副作用。Evidence 是 state transition log 与 resume record。Trade-off：state store 需要单独的持久化与一致性保证。

关键工程判断：把对话历史当权威任务状态（conversation-as-state 反模式）会导致中断恢复时状态不一致；memory stale 和 state 丢失是两种不同的失败，需要分开的检测和恢复路径。

---

### 第 4 轮：允许自动修正失败

**加入约束**：允许 Agent 在验证失败后自动尝试修正，但需要有上限和退出路径。

这一轮引入 bounded Loop，需要同时定义全部八个字段才能让 Loop 可控。**Aim** 固定为修正某类验证失败；扩大成宽泛的"让任务完成"会失去局部边界。**State** 记录当前任务状态、已执行的修正动作、evaluation 结果与剩余 budget，是恢复和审计的依据。**Action policy** 基于当前 state 与 evaluator / environment feedback 选择下一步修正手段。**Evaluator** 持有独立于 executor 的 evaluation contract——完成判断不能只依赖 executor 的自报；evaluator 可以由确定性检查（lint 通过、测试通过）、规则、另一模型或人工审核实现，只有使用额外模型或服务时才引入对应的推理成本，确定性 evaluator 有实现与维护成本但没有额外推理开销。

**Budget** 和 **stopping condition** 共同决定退出时机：budget 是硬上限（最大尝试次数或成本），stopping condition 是触发结束的具体条件（evaluator 通过、budget 耗尽、达到特定错误状态）。**Authority scope** 限定 loop 被允许触碰的动作、资源和目标边界——loop 在重试压力下修改任务目标（为了让 evaluator 通过而改变 aim 定义）是越权行为。**Escalation** 在 budget 耗尽或 authority scope 被突破时触发，产生 structured handoff，避免任务静默失败。Runner 执行控制合同：调用 action policy、应用 evaluator 与 stopping condition、消耗 budget、检查 authority / escalation，并返回结构化 outcome。

Retry precondition 检查动作是否幂等、side effect 是否可重做；在非幂等动作上自动重试会造成重复副作用和状态不一致，需要退出当前 Loop，进入 approval 或 escalation。Evidence 包括 attempt trace、evaluation record 和 budget / escalation outcome。

---

### 第 5 轮：独立子任务需要并行

**加入约束**：仓库中有多个互相独立的模块需要同时检查或修改。

先画 dependency，再决定是否并行。有 schema migration 顺序、强依赖关系、根因不明的 debug 场景，或 merge authority 尚未定义时，串行更安全。

确认独立分支后，隔离有两层需求：git worktree 隔离 linked working tree 的 Git 状态，但端口、数据库、cache、credential 和外部资源仍需单独隔离——仅使用 worktree 而不处理运行时资源，隔离会留下实质漏洞。

合并阶段需要显式的治理策略。本文为这个练习场景选择一种显式治理策略：指定 merge authority 负责最终决定，允许节点提出 hard veto（阻塞合并）和 soft objection（记录但不阻塞），governor 负责在 veto 或异常时触发升级。这是本文的示例策略，团队可以使用不同命名，但必须回答：谁有合并决定权、什么条件阻塞合并、什么情况触发升级。

这一轮的核心 Trade-off：更大的 parallelism 可能减少等待时间，同时扩大副作用范围、隔离成本、合并复杂度和联合验证负担。并行条件来自 dependency graph 中可独立执行的分支；单纯增加 Agent 数量无法建立隔离或 merge authority，反而会扩大风险面。Evidence 包括 dependency record、branch contract、base commit、handoff 记录和 merge + combined-check result。

---

### 第 6 轮：加入高风险外部 Tool

**加入约束**：某些工具需要访问外部服务、执行系统命令或接触敏感凭据。

权限最小化（least authority）是这一轮的起点：每个工具只获取完成其声明职责所需的最小权限，credential scope 跟随 Tool contract 与任务职责，不跟随 Agent 身份整体授予。失败路径是 credential 泄漏或权限范围超出实际需要，evidence 是 permission check record 和 audit log。

高风险动作在执行前触发 approval flow（Owner：harness + human）；approval 被绕过或 Agent 直接执行未审批动作，是这一类失败的直接形式，evidence 是 approval record 和 denied action trace。

Allowlist 需要检查完整 invocation，覆盖 arguments、cwd、config 与 side effects，只检查命令名会放行参数或 cwd 导致的越权执行。sandbox 的有效边界取决于实际隔离机制、workspace writes 检查、host trust 边界、凭据管控和可达资源；仅凭名称无法证明边界有效，缺少这些检查会留下安全盲区，evidence 是 security eval case 和 host access log。

Trade-off：细粒度权限控制增加配置复杂度；完整 allowlist 检查维护成本更高；审批增加 latency，需要提前定义哪些动作必须经过审批，避免审批路径在生产中成为瓶颈。

---

### 第 7 轮：准备交付真实用户

**加入约束**：系统需要在真实用户环境中运行，有 latency、cost 和可靠性要求，需要支持回滚。

**可观测性**（Constraint：需要在故障时重建事件序列；Owner：harness + infra）：部署 trace 和 telemetry，覆盖关键路径；主动识别 telemetry gap（哪些路径缺少足够观测）。故障发生但缺少信息定位根因，会让调试依赖猜测。Evidence 是 trace coverage report 和 telemetry gap list。Trade-off：更全面的 trace 增加存储成本和数据处理负担。

**Eval 体系**（Constraint：质量回退需要被发现；Owner：harness + eval pipeline）：采用 outcome-first 原则设计 eval suite；trajectory constraint 只覆盖安全和质量关键路径，过细的 trajectory 约束会固化偶然执行路径，并把模型与 API 之间的真实差异压平成最低公分母。Evaluation contract 与执行策略分离，可以提供超出 executor 自报的检查证据；evaluator 可以由确定性检查、规则、另一模型、人或组合实现。Evidence 使用 case / trial results、suite result、gate decision 与 regression record；所有成功率目标使用 `[目标]` 占位，不预设数值。

**上线与回滚**（Constraint：预算失控和质量回退需要可控；Owner：harness + infra）：设计 rollout（分批灰度）、fallback（降级路径）和 rollback signal（触发回滚的条件与阈值）。SLO、cost 和 baseline 全部使用 `[目标]` / `[预算]` / `[真实记录]` 占位；在没有真实测量数据时，先建立测量机制，再做预算决定。Trade-off：过度 provider abstraction 提供可替换性，代价是把模型和 API 的真实差异统一成最低公分母，过度 trajectory constraint 有同样的压平效应。

---

## 取舍必须具体化

三个贯穿全文的核心取舍，在"看场景"之外说明改变决定的条件：

**Context 与 Memory**：两者提供信息覆盖和跨轮次延续，同时引入噪声成本、provenance 管理、retention 策略和 staleness 风险。**改变条件**：如果任务是单轮、输入已充分结构化，减少 memory 层级可以降低复杂度；如果任务跨越多个会话，memory 的 staleness policy 成为关键设计决定。

**自治范围与 Parallelism**：更大的自治范围和更多并行可能减少等待时间，同时扩大副作用范围、隔离成本、合并复杂度和联合验证负担。**改变条件**：有 schema migration 顺序、强依赖关系、根因不明的 debug 场景，或 merge authority 未定义时，串行更安全。

**Trajectory Constraint 与 Provider Abstraction**：两者都能提供控制或可替换性；过度使用会固化偶然的执行路径，或把模型和 API 的真实差异压平成最低公分母。**改变条件**：如果只有一个 provider，抽象层增加成本而减少收益；如果安全关键路径已有明确的 pass / fail 定义，trajectory constraint 才有清晰的执行基础。

---

## 答题时值得主动检查的设计陷阱

这些陷阱在七轮演进中已经出现过，列在这里供答题时对照：

**Framework-first**：题目信息不足就先选框架，框架名替代了对 harness 职责的说明。框架是实现选择，选择之前需要先回答架构问题。

**Conversation-as-state**：把对话历史当任务状态的权威来源。对话历史可能不完整、不一致、无法支持 checkpoint 恢复；state 需要单独维护。

**Schema-as-permission**：把 Tool schema 或 MCP annotations（如 `readOnlyHint`）当授权机制。Schema 描述结构，permission 由 runtime enforcement 执行，两者职责不同，不能互相替代。

**Executor self-grading**：完全依赖 executor 自报是否完成任务。evaluation contract 与执行策略分离，可以提供超出 executor 自报的检查证据；evaluator 可以由确定性检查、规则、另一模型、人或组合实现。

**Unbounded retry**：缺少 budget、stopping condition 和 escalation path，loop 在没有进展时继续消耗资源，或在压力下修改 aim 来让 evaluator 通过。

**Parallel-everything**：把 Agent 数量当并行的来源，缺少 dependency 分析、隔离机制、merge authority 和 combined verification。

**Sandbox-without-checks**：仅凭组件名称宣称隔离，缺少 workspace writes 检查、host trust 验证和可达资源审计，会留下安全盲区。

**Final-answer-only**：只返回结论，不保存 trace、audit、diff 或 eval record；发生错误时无法重建事件序列。

---

## 相关岗位职责（准备维度参考）

以下岗位职责来自公开职位描述，用于说明本文覆盖的准备维度。这些信息只反映公开职责的相关性，不代表真实面试题目、流程或评分标准。

- **OpenAI AI Systems Engineer, Codex Agents**：关注 harness、execution loop、sandbox、orchestration、evals、observability 与生产可靠性。
- **OpenAI Applied AI Engineer, Codex Core Agent**：关注 real-world tasks、prompt / tool / context 实验、failure analysis 与 feedback loop。
- **Anthropic Research Engineer, Model Evaluations**：关注针对 agentic behavior 的评测设计、分布式评测执行平台加固、异常 eval 结果调试（区分模型变化与 harness/data/infrastructure 问题），以及 eval 工具链改进。
- **LangChain Deployed / Applied AI**：关注 multi-step workflow、orchestration、failure handling、monitoring、evaluation pipeline 与架构沟通。
- **Cognition Applied AI Engineer / Sierra Software Engineer, Agent**：关注 MCP integration、production Agent workflow、Agent lifecycle 与持续迭代。

---

## 延伸阅读

### 官方职位

- [OpenAI, AI Systems Engineer, Codex Agents](https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588)
- [OpenAI, Applied AI Engineer, Codex Core Agent](https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c)
- [Anthropic, Research Engineer, Model Evaluations](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- [LangChain, Deployed Engineer, Early Career](https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522)
- [LangChain, Fullstack Software Engineer, Applied AI](https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d)
- [Cognition, Applied AI Engineer](https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d)
- [Sierra, Software Engineer, Agent](https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d)

### 官方技术资料

- [Anthropic, Building effective agents](https://www.anthropic.com/research/building-effective-agents)
- [Anthropic, Writing effective tools for agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- [MCP, Tools specification](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)
- [Git, git-worktree documentation](https://git-scm.com/docs/git-worktree)
- [OpenTelemetry, Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenAI, Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)

### AI Coding Club 学习入口

- [Agent Engineering Hub](/zh/docs/agent-engineering/)
- [Coding Agent Harness](/zh/docs/tutorials/coding-agent-harness-explained/)
- [Coding Agent Memory](/zh/docs/tutorials/coding-agent-memory/)
- [MCP Tool Design](/zh/docs/tutorials/mcp-tool-design-guide/)
- [Loop Engineering](/zh/docs/tutorials/loop-engineering-guide/)
- [Graph Engineering](/zh/docs/tutorials/graph-engineering-guide/)
- [Parallel Agents With Worktrees](/zh/docs/tutorials/parallel-coding-agents-worktrees/)
- [Coding Agent Sandbox Security](/zh/docs/tutorials/coding-agent-sandbox-security/)

---

## 继续阅读 AI Agent 面试系列

- [面试与求职指南](/zh/docs/tutorials/ai-agent-interview-guide/)
- [求职作品集](/zh/docs/tutorials/ai-agent-portfolio-guide/)
- [系统设计面试](/zh/docs/tutorials/ai-agent-system-design-interview/)
- [故障分析与评测面试](/zh/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
