---
title: "AI Agent 故障分析与评测面试：怎样从 Trace 找到失败，再把失败变成 Eval"
description: "从真实 Trace 区分工具事件、Turn 与任务结果，把确认的失败转成 Eval case、grader、suite 和持续 Gate。"
keywords:
  - AI Agent failure analysis
  - AI Agent eval interview
  - Agent trace debugging
  - LLM evals interview
  - AI Agent 故障分析
  - Agent 评测面试
sidebar_position: 30
tags: [tutorial, career, agent-engineering, evals]
---
# AI Agent 故障分析与评测面试：怎样从 Trace 找到失败，再把失败变成 Eval

---

先看这四行记录：

```
tool: python  → exit 127
tool: python3 → exit 1 / ZeroDivisionError
tool: read source → exit 0
turn: completed
```

这是一次受控诊断任务留下的关键事件片段。任务要求：运行聚焦单元测试，读取最小相关源码，诊断精确原因，全程禁止修改任何文件，最后用一句话说清失败行为和最小修复方向。

整条记录包含 5 次工具调用，其中 3 次成功、2 次失败。最终答案正确指出了空列表触发除零，并给出预期 `ValueError("at least one value")` 的最小修复方向。

**这次 Agent 到底失败了几次？**

在给出答案之前，先问自己：你在判断哪一层？是单次工具事件的协议完成情况，是控制轮次的结束状态，还是整个任务合同是否被满足？不同层的答案可以同时为真，也可以同时不足以证明任何一项。把这三层混在同一个"成功率"里，会直接遮蔽故障定位所需的层级信息。

---

## 把三个结果层级分开

| 层级 | 判断对象 | 本案例 |
|------|---------|-------|
| Event / Tool | 单次调用是否按协议完成 | 2 个 command items 为 failed |
| Turn / Run status | 客户端控制轮次怎样结束 | `turn.completed` |
| Task outcome | 任务合同是否被满足 | 由诊断内容、禁止写入和任务专用 grader 共同判断 |

`turn.completed` 只说明控制轮次正常结束，单独不足以证明答案正确、约束得到遵守或用户目标完成。`exit 127` 说明当前环境找不到 `python` 启动器。`python3` 启动器可用，测试到达应用层并暴露异常，随后诊断流程继续——这两件事同时成立。`exit 1` 是工具进程返回值，同时也是这次诊断任务需要的有效证据——没有它，测试行为就是不可见的。

这意味着：child tool failure 与 parent task failure 需要独立判断。exit code、span status、turn status 和 task outcome 各自记录各自的含义，任何一项都无法替代其他三项。

---

## 重建可见时间线

完整记录包含 17 个 events、5 个 tool calls、4 条 Agent messages。逐步展开：

| 顺序 | 动作 | 结果 | 能支持的判断 |
|------|------|------|------------|
| 1 | 定位规则与聚焦测试 | exit `0` | 确认只读约束和测试合同 |
| 2 | 读取规则与测试 | exit `0` | 测试期待 `ValueError("at least one value")` |
| 3 | 用 `python` 运行聚焦测试 | exit `127` | 当前环境缺少 `python` 启动器 |
| 4 | 用 `python3` 重试同一测试 | exit `1`，`ZeroDivisionError` | 启动器可用，测试到达应用层并暴露异常 |
| 5 | 读取 `calculator.py` | exit `0` | 实现直接执行 `total / len(values)` |
| 6 | 返回一句诊断 | turn `completed` | 答案指出除零和最小 guard；仍需 grader 判断 task outcome |

`python3` 这次执行，原始记录里没有显式的 `retry_of` 字段，也没有 parent-linked span hierarchy。但工具调用顺序和 Agent message 共同支持这个判断——它属于 **Derived**，由证据推导而来，同时有别于直接的 **Recorded** 字段。

### 已记录、已推导与不可知

拿到一条 trace 之后，第一件事是把证据分区：

- **Recorded（已记录）**：thread id、turn events、item id、Agent messages、完整 command 内容、aggregated output、exit code、item status、turn status、token usage。
- **Derived（已推导）**：`python3` 是对 `python` 失败的 retry，由事件顺序与 Agent message 支持。
- **Unavailable（不可知）**：event timestamp、duration、dollar cost、handoff event、Skill-load event、model field、显式 parent / retry relation。

不可知字段必须保留为空白。记录中某字段缺失，与"该事件从未发生"之间存在根本区别——前者是采集边界，后者需要独立证据支撑。无法从缺失字段推断内部动作从未发生，也无法估算耗时与成本。现有记录可以回答 token usage，但无法回答 duration、dollar cost 或显式 handoff / parent / retry relation。如果分析流程依赖这些字段，下一步行动是改进采集，而非估算填坑。

---

## 用 Failure Taxonomy 产生假设

遇到失败，直接宣布根因会跳过验证环节。先用分类框架生成候选假设，再用证据逐一检验。

本案例涉及的层级：

**Runtime / Infrastructure**：`exit 127` 最直接的解释是当前环境缺少 `python` 二进制。这是 runtime / environment 层的直接失败。Agent 选择调用 `python`、tool policy 配置以及 harness configuration 对此也可能有影响，这些上游原因保留为待验证假设，暂时无法从现有记录中确认或排除。

**Tool（工具层）**：`python3` 的 `exit 1` 是 tool process result，同时也是 application failure evidence。`ZeroDivisionError` 是运行时异常，属于应用层错误，而非工具协议错误。

**Requirement / Product**：focused test 文件期待 `average([])` 抛出 `ValueError("at least one value")`。当前源码实现里，`average([])` 直接执行 `total / len(values)`，除数为零，触发 `ZeroDivisionError`，缺少前置 guard。这是实现与 focused test 期待之间可测量的缺口。

**Observability Gap**：duration、dollar cost、handoff event 和显式 parent / retry relation 不可用。追问"这次诊断耗费了多少时间或成本"或"模型是否经历了内部重试"时，现有记录无法回答。这个缺口本身需要单独记录，并决定是否值得改进采集方案。

把这些层级摆出来，目的在于确认：哪些已经有记录支撑，哪些只是相关性，哪些需要新证据才能推进判断。

---

## 从现象到根因的距离

分析者容易做的事：看到 `ZeroDivisionError` 就宣布"模型没有处理边界条件"。这里有两个跳跃：第一，把运行时异常归因给模型推理；第二，在没有源码的情况下宣布机制。

正确的推进顺序：

1. **复现最窄失败**：输入是 `average([])`，环境是只读 ephemeral sandbox，focused test 期待行为是抛出 `ValueError("at least one value")`，实际行为是 `ZeroDivisionError`。
2. **找到直接机制**：读取 `calculator.py`，确认实现为 `total / len(values)`，没有对空列表做前置检查。源码是直接证据。
3. **检验替代假设**：是否是测试写错了？focused test 明确期待 `ValueError("at least one value")`，task prompt 则要求运行测试、诊断原因、保持只读并给出最小修复——两者各自有明确分工。是否是环境问题导致执行失败？`python3` 启动器可用，测试到达应用层并暴露异常，该 command item 以 exit `1` / failed 结束。launcher issue 在此已不再阻止症状复现；源码解释了当前异常；若要确认测试代表真实产品合同，还需要独立需求证据。
4. **最小修复方向**：在 `total / len(values)` 之前加 `if not values: raise ValueError("at least one value")`。这个方向来自 focused test 的 expected behavior；task prompt 要求给出最小修复，未要求实际应用修复。
5. **尚未完成的部分**：这次 run 是只读的，修复没有被应用，也没有被测试验证。正文可以解释修复方向，但该修复在这次运行中未经测试确认。

---

## 把确认的失败编码成 Eval

故障分析完成的标志，是将该失败场景转化为可在下一次配置变更时自动触发的回归检测用例。

### 五个层级

| 概念 | 工作定义 | 本案例 |
|------|---------|-------|
| Case | 冻结输入、环境、成功合同与评分要求 | 诊断 `average([])`，禁止修改文件 |
| Trial | 某配置对一个 case 的一次尝试 | 保存的 Codex diagnosis baseline |
| Grader | 把 trial evidence 映射成结果 | 答案、turn、tool budget、unexpected writes 检查 |
| Suite | 面向一个能力的多个 cases / graders | 由历史失败、边界条件和安全场景持续扩展 |
| Gate | 根据预先声明结果决定继续、阻断或人工复核 | 可进入 CI、release 或 rollout decision |

### 把这次 trace 变成 case

**Case 定义**：输入为 `average([])`，环境为只读 ephemeral sandbox，任务合同要求答案包含失败原因（除零）和最小修复方向（guard 空列表），不得写入任何文件，工具调用总数不超过 case policy 上限。

**Baseline trial**：保存的这次受控诊断记录，通过当前教学 gate，CLI exit `0`。

**Grader 需要检查的维度**：

- 答案是否包含"除零"或等价描述？
- 答案是否给出了最小修复方向？
- turn status 是否为 `completed`（而非 `incomplete` 或 error）？
- tool 调用总数是否在 budget 内？
- 是否有 unexpected writes（违反只读约束）？

每个维度独立记录，不合并成单一总分。grader 自身也可能成为一个 failure layer——substring answer check 是最低限度的确定性教学检查，在这个受控 case 内可以区分正确诊断与错误答案，但无法代表充分的语义评分能力。

### 三个对照 trial 的教学价值

**Baseline**：这次保存的记录，通过当前教学 gate 所有 grader 检查。

**Synthetic wrong-fix**：如果答案改为"空列表返回 0"，`answer_contains_all` 检查失败，gate 拒绝，CLI exit `1`。这表明该 grader 在这个具体错误答案上能够拒绝通过；substring check 作为最低限度的确定性检查，在语义区分能力上存在固有边界。

**Cleaner candidate**：如果一个配置只用 3 次 tool calls、0 次 failed tools 就给出正确答案和正确约束，它同样通过 gate。grader 不要求复刻 baseline 的失败路径。这是 outcome-first 原则的直接体现：评的是用户可见结果，而非历史轨迹。

---

## Repeated Trials、Suite 与 Gate

一个 case 在一次 trial 里通过，不能由此判断这个能力具有稳定性。模型输出会随运行变化，环境条件也会变化。

**Repeated trials**：重复次数按风险、波动与成本预先声明，使用 `[真实 trial 数]` 占位。每次 trial 从干净隔离状态开始，冻结：case、repository / base commit、environment、Agent / model / harness config、tools / skills、permission、network、budget 和 reset rule。

**Suite 的生长方式**：从真实任务分布、历史 failure log、边界条件、安全路径和高代价场景中添加。边界和安全场景与 happy path 同等重要。对这次诊断案例来说，下一批 case 候选可以是：输入为 `average([0])`（单元素列表，返回 0 是否被正确描述）、输入为包含非数字元素的列表（TypeError 路径）、Agent 尝试写入文件但被阻断（约束检查）。

**Gate 的预先声明**：gate 在运行之前就要确定 hard veto 条件（例如 unexpected writes 一票否决）、可接受阈值（例如在 `[真实 trial 数]` 次 trials 中，结果达到预先声明的 `[门禁阈值]`）、需要人工复核的灰色区域和 evidence retention 要求。gate 结果指导继续、阻断或人工复核，标准在运行前确定，运行后不再调整。

**上线之后**：保留 rollout、fallback、rollback 与 monitoring signal。latency、token、cost、error 与 human intervention 只在真实暴露时记录，缺字段写 `N/A`，不估算，不用一次 run 的数据外推典型表现。

---

## 七道职责归纳练习

以下七题由公开岗位重复职责与教学内容归纳，统一标为职责归纳教学练习，不归因给具体公司或真实题库。

---

**练习 1**

> Trace 中 2 个 tool events failed，最终 turn completed。怎样判断 task outcome？

**分析观察点**

先确认 task contract 定义了什么算成功——是答案内容、功能结果、约束遵守，还是三者同时满足？失败的 tool events 有没有 parent scope 能吸收它们的影响？本案例里，`exit 127` 被 `python3` 可用这一事实所替代，诊断流程继续，诊断结论仍然可以成立。`turn.completed` 说明控制轮次结束，单独不足以证明任何任务维度的成功。最终判断需要 task-specific grader，在 residual uncertainty 无法消除时，需要人工复核作为最后一道检查。

---

**练习 2**

> Final answer 合理，但现有记录只有 `turn.completed`。还需要什么证据？

**分析观察点**

`turn.completed` 是控制状态，表达轮次结束而非质量结果。还需要确认：任务 outcome（答案是否满足 contract）、约束遵守（只读约束是否被执行、tool budget 是否超限）、artifact 完整性（是否有写入、是否有遗漏步骤）。grader 用 counterexample 和人工判断校准之前，final answer 与 `turn.completed` 的组合仍不足以证明整体正确。

---

**练习 3**

> Trace 缺 duration、cost、handoff 和 parent relation。怎样继续？

**分析观察点**

把字段归入 recorded / derived / inferred / unavailable 四类，不估算不可知字段。在当前可用证据下推进分析，同时记录哪些问题无法在现有 trace 中回答。telemetry gap 本身是一个 action item：评估改进采集的成本和价值，决定是否在下一个 run 开启更完整的 instrumentation。字段缺失与分析能否继续是两个独立判断，缺口本身需要记录而非忽略。

---

**练习 4**

> Context compression 后偶发使用过期状态。怎样定位？

**分析观察点**

需要在失败前后各拿一份 context snapshot，比对 memory provenance——Agent 使用的状态是从哪个时间点压缩进来的？authoritative state 在压缩后还能重建吗？设计 control trial：关掉压缩，复现是否消失？再做 ablation：逐步缩小压缩比，观察失败的临界点。多次 repeated trials 才能区分随机波动和系统性问题。单次失败复现不足以确认根因。

---

**练习 5**

> 设计一个允许不同有效路径、同时阻断越权写入的 grader。

**分析观察点**

首先检查 outcome：答案内容、功能结果和约束遵守分列评分，不合并。negative side effect 检查（unexpected writes）独立设置 hard veto，一票否决，不参与加权平均。trajectory 只约束关键安全路径，不锁定 command order 或 tool count。用 counterexample 验证 grader：把一个正确答案但有写入的 trial 输入，grader 应该拒绝；把一个错误答案但零写入的 trial 输入，grader 应该因答案质量失败而非因路径问题失败。grader 自身也需要校准，自动 grader 的误判和漏判是一个独立 failure layer。

---

**练习 6**

> 一次线上失败怎样转成持续门禁？

**分析观察点**

第一步是在隔离环境里复现：确认输入、环境、配置和 task contract。复现成功后，把这次失败冻结成一个 case，配上对应 grader，记录一次 baseline trial。然后把 case 加入 suite，suite 要涵盖这次失败的变体和边界条件，持续扩展而非仅作归档。gate 预先声明 hard veto、阈值和人工复核规则，并接入 CI 或 release 决策流程。上线后继续保留 rollout 信号，监控新失败是否出现，随时准备 rollback。gate 随 suite 增长和产品变化持续维护。

---

**练习 7**

> 怎样公平比较两个 Agent 配置？

**分析观察点**

先冻结所有共同字段：task、base commit、环境、prompt、权限、budget、重置方式和重复次数。然后记录无法消除的产品差异（例如工具集不同、模型不同），这些差异不能被控制，只能透明保存。结果多维分列：功能 outcome、diff / review burden、operational failure rate、权限事件、latency / token / cost 各自独立记录，不用一个总分掩盖 hard veto。缺少实测字段的维度写 `N/A`，不估算。`[真实 trial 数]` 和 `[复测结果]` 用占位符标明，待实际运行后填入。公开 benchmark 可以作为基线或初筛，无法预测某个私有仓库在特定配置下的最佳表现。

---

## 统一答题纸

面对任何 Agent 故障记录，六个步骤：

```
重建可见范围
  → 分层判断结果
  → 分类并提出根因假设
  → 用复现、对照或 ablation 验证
  → 把确认失败编码为 Eval case
  → 用 suite、gate 与 rollout 信号持续守住
```

每一步回答三个问题：已记录证据是什么？缺失字段是什么？哪种新证据会推翻当前判断？

---

## 从这里开始

拿你项目里的一条真实失败记录，不需要完整，哪怕只有一行 exit code 和一行 Agent message，试着写出：

1. 这条记录里，什么是 Recorded，什么是 Derived，什么是 Unavailable？
2. 失败发生在哪个层级？是 event、turn 还是 task outcome？
3. 你能提出几个互相竞争的根因假设？
4. 什么样的新证据能排除其中一个？
5. 如果要把这次失败变成一个 regression case，grader 需要检查哪些维度？

这五个问题本身，就是把失败分析练熟的路径。

---

## 深入学习

### 官方职位（参考准备维度，不代表真实题目或录取标准）

- [OpenAI, AI Systems Engineer, Codex Agents](https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588)
- [OpenAI, Applied AI Engineer, Codex Core Agent](https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c)
- [Anthropic, Research Engineer, Model Evaluations](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- [LangChain, Deployed Engineer, Early Career](https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522)
- [LangChain, Fullstack Software Engineer, Applied AI](https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d)
- [Sierra, Software Engineer, Agent](https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d)

### 官方技术资料

- [OpenTelemetry — Traces](https://opentelemetry.io/docs/concepts/signals/traces/)
- [OpenAI — Evaluation best practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- [Anthropic — Demystifying evals for AI agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- [SWE-bench — Dataset guide](https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/datasets.md)
- [SWE-bench — Evaluation guide](https://github.com/SWE-bench/SWE-bench/blob/main/docs/guides/evaluation.md)

### AI Coding Club 深入学习入口

- [Agent Engineering Hub](/zh/docs/agent-engineering/)
- [Coding Agent Observability](/zh/docs/tutorials/coding-agent-observability-guide/)
- [Coding Agent Evals](/zh/docs/tutorials/coding-agent-evals-guide/)
- [Coding Agent Benchmark](/zh/docs/tutorials/coding-agent-benchmark-guide/)
- [AI Code Review Workflow](/zh/docs/tutorials/ai-code-review-workflow/)
- [Browser Verification](/zh/docs/tutorials/coding-agent-browser-testing/)

---

## 继续阅读 AI Agent 面试系列

- [面试与求职指南](/zh/docs/tutorials/ai-agent-interview-guide/)
- [求职作品集](/zh/docs/tutorials/ai-agent-portfolio-guide/)
- [系统设计面试](/zh/docs/tutorials/ai-agent-system-design-interview/)
- [故障分析与评测面试](/zh/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
