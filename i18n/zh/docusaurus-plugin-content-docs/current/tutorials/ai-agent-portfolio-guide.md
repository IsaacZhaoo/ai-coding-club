---
title: "AI Agent 求职作品集：用一个可验证项目证明系统设计、评测与交付能力"
description: "用一个可验证的 AI Agent 项目组织架构、任务集、Trace、Eval、安全边界、失败记录与项目 Deep Dive 证据。"
keywords:
  - AI Agent portfolio
  - LLM engineer portfolio
  - AI Agent project
  - Agent project deep dive
  - AI Agent 作品集
  - AI Agent 项目
sidebar_position: 28
tags: [tutorial, career, agent-engineering, portfolio]
---
# AI Agent 求职作品集：用一个可验证项目证明系统设计、评测与交付能力

把你的 Agent 仓库交给一个完全不了解这个项目的人。请他在不联系你的情况下检查四个问题：这个系统处理什么任务，成功标准是什么；Agent 被允许执行哪些动作；失败发生在哪里，留下了什么记录；问题是如何修复的，证据在哪里。

如果他的回答需要你在旁边现场补充，仓库就还缺一条可追溯的证据链。

这是 AI Agent 作品集真正的评价难点。项目可以很复杂，代码可以很漂亮，架构图可以很清晰，但当一次运行、一次失败、一次修复都没有可以独立检验的 artifact，第三方就无法重建你在整个过程中做出的工程判断。这套证据适合用于准备 Project Deep Dive——它要求你能证明哪些地方会出错、为什么会出错，以及你的修复有没有经过检验。

---

## 证据图：演示、意图、运行与回归的四个层级

一个经得起第三方检查的 Agent 作品集，把所有文件堆进仓库还远远不够，需要在四个层级上各有证据：

**演示**告诉别人系统大致在做什么。它能引起兴趣，但无法证明任何工程决定。

**架构意图**解释每个组件负责什么，为什么这样划分，以及权限边界从哪里到哪里。它把一堆代码文件变成一张责任图。

**运行证据**显示某次实际执行发生了什么——调用了哪些工具，在哪一步出错，错误数据传到了哪里，最终返回了什么。它是调查故障的第一手材料。

**回归证据**检查修复是否有效，并防止同类问题在未来的运行中重新出现。它是让"我修好了"变成可核查声明的机制。

这四个层级的证据相互依赖，不能互相替代。把架构图当作运行证据，把演示视频当作回归证据，会形成明显的作品集漏洞。

下面这张图描述了九个证据要素之间的因果关系：

```
Task Set
  ├─> Tool Contract ─┐
  └─> Bounded Loop ──┴─> Trace ─> Failure Log ─> Eval Case / Trials ─> Suite / Gate

Architecture Map 负责索引责任边界
Security Boundary 包住 Tool、Loop 与 Workspace，并进入 Trace / Eval
README + Commands 把整条链交给第三方复现
```

整条链的根是 **Task Set**。没有任务定义，trace 和 eval 就没有共同基准；没有共同基准，评测数字就没有意义。

---

## 选一个有边界的仓库维护 Agent 作为旗舰项目

本文推荐用一个有边界的仓库维护 / Coding Agent 作为旗舰项目，原因在于它的输入、执行范围和输出都可以被精确约定，每个层级的证据都有自然的落地点。

这类项目的典型结构如下：

**输入**是一份 task contract，包含仓库范围、局部目标、禁止改动的文件或区域、验收条件和权限。这份合同是整条证据链的根。

**执行**由 harness 负责组装——它处理上下文、调用 model/provider、分发工具、管理状态和控制运行流。Agent 通过声明过的 read / search / edit / command 类工具完成诊断或小型修改。所有写入和命令发生在隔离 workspace；越权动作、目标变化或高风险操作进入拒绝、审批或结构化 handoff。

**输出**包含 structured result、diff、validation evidence、trace identity、eval result 和 known limits。

**主动排除**也要明确写出来：这个项目不负责跨仓库迁移、不执行生产部署、不管理密钥轮换。把"不做什么"写清楚，比把边界说含糊更有助于第三方评估你的系统设计判断。

一个窄范围的任务可以同时展示 context、harness、tool、loop、security、trace、eval 和 README——这是它作为旗舰项目的工程价值所在。

---

## 九个证据要素，按依赖顺序

以下是九个证据要素的必答问题、建议 artifact 和依赖关系。文件名是教学模板，不要求照搬，但 artifact 之间的链接关系不可省略——task ID、trace ID、failure ID、eval case ID 应当能互相追踪。

| 要素 | 必须回答的问题 | 建议 artifact | 依赖与缺失风险 |
|---|---|---|---|
| Architecture Map | 谁负责 context、决策、工具、状态、验证和权限 | `docs/architecture.md` + 责任图 | 依赖项目边界；缺失后所有技术名词没有归属 |
| Task Set | 系统处理什么，success / refusal / escalation 怎样定义 | `tasks/` 或结构化 case 文件 | 整条链的根；缺失后指标、trace 和 eval 没有共同基准 |
| Tool Contract | schema、语义、错误、幂等性、副作用分别是什么 | `contracts/tools/` + 正常/错误 fixture | 依赖任务；schema 格式约束之外，authorization、业务校验和副作用治理需要独立覆盖 |
| Bounded Loop | aim、state、policy、evaluator、budget、stop、authority、escalation 如何组合 | `docs/loop-contract.md` 或配置 | 依赖 task/tool；缺失后重试、完成和越权没有可解释规则 |
| Trace | 这次实际发生了什么，哪些地方仍不可见 | `traces/<trace-id>.jsonl` + 字段说明 | 依赖稳定 identity/parent/event；缺失后故障叙述只能靠记忆 |
| Failure Log | 预期与实际差异、调查依据、根因、修复和残余风险是什么 | `failures/<case-id>.md` | 依赖 trace；缺失后仓库只展示成功路径，无法证明调试判断 |
| Eval Suite | case、grader、trial、suite、gate 怎样验证修复并防回归 | `evals/` + baseline / candidate records | 依赖 task/failure；单 case 或单 trial 不能支持可靠性结论 |
| Security Boundary | direct execution、workspace write、host trust、approval 和 audit 怎样约束动作 | `security/boundary.md` + policy/config | 包住 tool/loop/workspace；缺失后"安全"只剩架构图上的标签 |
| Reproducibility Package | 陌生人怎样运行、查看证据、确认贡献与限制 | `README.md` + 可执行命令 + artifact index | 依赖全部上游；缺失后证据只能由作者现场演示 |

### Architecture Map

Architecture Map 让第三方无需猜测每个组件负责什么判断、组件之间的接口是什么、权限边界从哪里到哪里，直接把代码文件对应到系统意图。

缺少 Architecture Map 的后果是显而易见的：你说"harness 管 context"，对方问"哪个文件"；你说"loop 有 budget 限制"，对方问"budget 怎么计算，超出了怎么处理"。技术名词在没有归属的情况下无法成为证据。

### Task Set

Task Set 定义系统处理什么，以及三类结果怎样区分：success（任务在边界内完成）、refusal（任务越出权限被主动拒绝）、escalation（系统识别出自己无法处理并移交人工）。

这三类结果都要有对应的 task case，否则 eval 只能验证成功路径，项目追问也可能继续进入 refusal 和 escalation。

### Tool Contract

Tool Contract 比 schema 多一层：schema 负责格式和结构约束，contract 还要覆盖语义、错误处理、幂等性和副作用。

MCP Tool annotations 是 hints，例如 `readOnlyHint: true` 表明工具的读写意图，供客户端参考——但这个字段不在运行时执行 authorization 或 containment。authorization 和 runtime guard 需要单独实现并单独测试。fixture 要同时覆盖正常路径和错误路径，否则工具合同只有一半被验证。

### Bounded Loop

Loop 是一个局部控制合同，需要同时定义：

- **aim**：这一轮要完成什么；
- **state**：当前进度如何追踪；
- **action policy**：根据当前 state 和反馈选择下一步手段；
- **evaluator**：如何判断是否完成；
- **budget**：最多消耗多少步骤或 token；
- **stop**：在哪些条件下停止；
- **authority**：允许执行哪些类型的动作；
- **escalation**：当 evaluator 无法判定或动作越权时，移交给谁。

runner 依据这些合同字段综合返回结果——success、continue、budget exhausted 或 escalation。无限重试缺少工程边界。一个 loop 如果没有明确的 stop 条件和 authority 定义，在项目追问中很难解释清楚"这个系统知道自己什么时候该停下来"。

### Trace

Trace 在已采集范围内重建关键事件序列：哪个工具被调用，参数是什么，返回了什么，下一步是什么。它是你调查故障时的重要材料，也是支撑项目叙述的关键证据来源之一。

Trace 的证明范围取决于你的埋点。必须显式记录 telemetry gap——哪些调用没有进入 trace，哪些字段目前为空。gap 本身可以接受，无法定位 gap 才是问题。

稳定的 trace identity（trace ID、parent span ID、event 类型）让 trace 和 failure log、eval case 可以互相追踪。没有稳定 identity 的 trace 只是日志，不足以作为证据。

### Failure Log

Failure Log 是仓库里容易被省略，却能直接展示调试判断的 artifact。

它记录的内容包括：预期行为和实际行为的具体差异；用哪些 trace 字段支持了哪个根因假设；修复改动了什么，为什么这个改动是对的；修复之后还剩下哪些残余风险。

一个只有成功路径的仓库，无法证明作者有调试判断能力。Failure Log 的价值在于展示你对失败的思考过程——这套证据能够支撑 STAR 与项目追问，让调查路径和判断依据变得可检查。

### Eval Suite

Eval 有五个层级需要区分：

**case** 定义一个任务和成功标准——这是 eval 的原子单位；\
**trial** 是 case 在某个配置下的一次运行——同一个 case 可以有多个 trial；\
**grader** 检查 trial 的结果是否满足 case 的成功标准；\
**suite** 把相关的 case 组织在一起；\
**gate** 根据 suite 的结果决定是否接受某次改动。

概率性行为需要重复 trials，并保存 model/provider、prompt/tool 版本、环境和 grader 配置。单次通过无法上升为可靠性结论。基线结果和复测结果分别使用 `[基线]` 和 `[复测结果]` 占位——任何出现在简历或介绍中的数字，都要能定位到具体的 trial artifact。

先检查 outcome，再谨慎加入关键 trajectory constraint；把历史路径的每个动作都锁死，eval 会在第一次重构后集体失效。

### Security Boundary

Security Boundary 需要具体回答五个问题：

**direct execution**：Agent 能直接启动哪些进程、发起哪些网络连接、调用哪些系统工具；

**workspace writes**：Agent 能写哪些代码、配置、hook、Git 状态和生成文件——写 `.github/workflows/` 和写 `README.md` 的影响半径完全不同；

**host trust**：哪些宿主组件、socket、daemon、已登录 CLI 或凭据会消费 Agent 写入的状态——容器里的 Agent 如果有挂载的 Git 配置或 socket，host trust 边界就与容器边界不同；

**approval / audit**：什么动作需要人工确认，完整调用、参数、cwd、配置和副作用怎样进入审计记录；

**isolation**：临时容器或 worktree 是常见的隔离手段，但名称本身不等于强隔离——挂载策略、凭据传入方式、特权配置和 host socket 可达性都要逐项检查。

把越权拒绝和升级路径放进 task set、trace 和 eval，就能形成可验证的安全边界，而不只是架构图上的一个标签。

### Reproducibility Package

README 是证据链的交付界面，建议包含：任务边界的简洁说明、架构图链接、quickstart、task/eval 的可执行命令、artifact 索引（trace、failure、eval 各在哪里）、权限模型说明、贡献说明（自己做了什么，别人做了什么）、主要 trade-offs 和 known limits。

可执行命令的意思是：从零开始，按 README 的步骤执行，能到达一个有意义的状态。如果需要内部访问权限或私有数据，明确写出来，避免让陌生人静默失败。

---

## 一条失败链：证据怎样从错误生长成回归防护

下面用一个标为"示例"的无数字链条，说明九个要素怎样互相咬合：

```
（示例）某个工具返回了结构合法但语义不合法的数据
→ trace 显示错误数据进入了下一步决策
→ failure log 记录：tool contract 覆盖了 schema，但没有覆盖业务语义校验
→ 修复：在工具调用之后加入 runtime validator，拒绝语义不合法的返回值
→ 从该失败生成一个 eval case，包含触发该错误的 task 和 grader
→ 重新运行 trial，记录修复前和修复后的 grader 结果
→ 把该 case 加入 suite，gate 在未来的改动中自动检查同类回归
```

这条链揭示了三层防护的分工：

Tool Contract 说明预期语义——这是设计时的规格；\
Runtime validator / authorization 在执行时阻断不合法行为——这是运行时的实施；\
Fixture / eval case 检查实现是否符合规格——这是回归时的验证。

三层缺一不可。"写了 schema"只覆盖了格式，不覆盖语义、authorization 和副作用。把 schema 当作全部正确性和安全性的证明，是作品集里一类典型的工程误判。

这条链同时体现了 security 的交叉验证：runtime validator 的存在本身需要进入 tool contract，validator 拒绝的事件需要进入 trace，trace 里的拒绝事件需要进入 eval case。security boundary 贯穿 tool、loop、trace 和 eval，而不只是一个单独的文件。

---

## README、Artifact Index 与 Ownership Ledger

一个完整的 README 结构：

```
项目名称
├── 任务边界（一句话：处理什么，不处理什么）
├── 架构图链接
├── Quickstart（从零到运行的最短路径）
├── Task 命令（怎样运行一个 task case）
├── Eval 命令（怎样运行 eval suite 和 gate）
├── Artifact Index
│   ├── traces/        → trace 文件位置和字段说明
│   ├── failures/      → failure log 文件位置
│   └── evals/         → eval case、trial 和 baseline 位置
├── 权限模型（允许和禁止的动作）
├── Ownership（谁做了什么，可检查证据在哪里）
├── Trade-offs（做了哪些权衡，为什么）
└── Known Limits（已知的边界和未解决的问题）
```

**Ownership Ledger** 是其中容易被忽略的部分。为项目 Deep Dive 做准备时，要能说明个人贡献、过程、遇到的障碍和处理方式——一个简洁的 ownership 表格正是承接这类追问的结构：

| 工程决定或 artifact | 我的具体贡献 | 可检查证据 | Known limit |
|---|---|---|---|
| `[项目中的真实决定]` | `[设计 / 实现 / 评测 / 运维责任]` | `[文件、trace 或 eval 路径]` | `[仍未解决的边界]` |

这个表格有两个功能：对内，它迫使你在整理作品集时澄清哪些地方你真正做了决定，哪些地方是框架默认行为或协作者的工作；对外，它让第三方知道从哪里找到可以核查的证据，也知道你对自己工作的边界有清晰认知。

ownership 里只记录你实际承担的内容。如果项目是个人项目，就如实写个人项目；如果有协作者，说清楚各自负责什么，不要虚构团队合作、客户影响或生产责任。

---

## 把同一份证据包转成四种求职表达

证据链整理好之后，可以从同一份材料生成四种不同场景下的表达。

### Resume Bullet

Resume bullet 负责索引证据，无法替代证据本身。一个有效的 bullet 包含：动作 + 任务/边界 + 工程决定 + 验证方式 + 真实结果。

格式示例（所有数值使用占位符）：

> 为 `[任务范围]` 设计带 `[权限/停止边界]` 的 Agent harness，通过 `[suite / grader]` 对 `[真实 trial 数]` 次运行进行回归，将 `[指标]` 从 `[基线]` 改善到 `[复测结果]`；证据见 `[artifact]`。

框架名（LangGraph、CrewAI、LangChain 等）可以作为实现背景出现在 bullet 里，但框架名称无法代替工程决定和验证方式。"使用 LangGraph 构建 Agent"和"为该 Agent 设计了 loop 的 stop 条件和 authority 边界"是两件完全不同的事。

### 五分钟项目介绍

五分钟介绍依靠清楚的叙述顺序，无需覆盖所有文件。建议的顺序：

**任务与范围**——先说系统处理什么，边界在哪里。\
**架构和个人贡献**——聚焦自己负责的部分，无需铺开整个系统。\
**最关键的 trade-off**——说出一个你在设计时做出的权衡，以及为什么选择这一侧。\
**一条失败及调查**——具体说一个失败，trace 显示了什么，你的假设是什么，最终根因是什么。\
**eval/security 证据**——简述 eval suite 如何验证修复，security boundary 在哪里设置了什么约束。\
**Known limits 与下一步**——用 known limits 结尾，比用"下一步要做什么"更有说服力，因为它证明你对系统有清醒的认知。

平均介绍所有文件，在五分钟内听起来像目录朗读。

### Project Deep Dive

这套证据适合用于准备 Project Deep Dive。为每个核心决定准备一组"条件 → 决定 → 代价 → 证据 → 残余风险"：

- **条件**：在什么约束下做这个决定；
- **决定**：具体选择了什么方案；
- **代价**：这个选择放弃了什么；
- **证据**：这个决定的效果在哪个 artifact 里可以检查；
- **残余风险**：这个决定仍然遗留了哪些未解决的问题。

面对 Deep Dive 追问时，可以回到具体 artifact。追问可能进入 tool error handling、loop stop 条件、trace gap、grader 偏差、host trust 边界或个人贡献。如果任意一个追问让你无法指向具体 artifact，就说明那个位置的证据还没有覆盖到。

### STAR

对于这个旗舰项目，Failure Log 是最稳定的 STAR 原材料之一——它同时保存了任务边界、调查路径和验证结果。

**Situation**：任务是什么，边界是什么，为什么在这个边界里工作。\
**Task**：你个人在这件事上负责什么，你当时对问题的初始理解是什么。\
**Action**：这是主体。说清楚 trace 显示了什么，你的第一个假设是什么，验证假设用了哪些字段，根因是什么，修改了哪里，为什么这个修改是对的，加入了哪个 eval case 来防止回归。\
**Result**：只引用真实的复测结果和残余风险，不要编造成功率或延迟改善数字。

Action 写得太薄时，STAR 会失去关键的技术依据——只说"找到了问题，修复了它"，没有说调查路径和判断依据。技术细节是 Action 的主体。

---

## 行动建议：先补最上游的缺口

先定位最上游缺口，再决定要补哪些文件。

如果没有明确的 task contract——先补 Task Set。其他一切都以它为基准。\
如果有 task 但没有 trace——先补 trace 埋点。没有 trace，failure log 和 eval 都无从着手。\
如果有 trace 但没有 failure log——整理一个真实的失败案例，即使只有一条。\
如果有 failure log 但没有对应的 eval case——把这个失败转换成一个 case，并加入 gate。\
如果 eval 和 trace 都有，但 security boundary 没有具体的动作约束——逐项检查 direct execution、workspace writes 和 host trust。\
如果所有 artifact 都在，但 README 里没有可执行命令——从 quickstart 开始，验证一个陌生人能跑起来。

这条顺序要求你先从整条链的根往下走，确保每一层的证据都能独立于你本人的现场解释。

当第三方能用你的仓库回答最开始那四个问题——任务是什么、允许什么、哪里失败了、修复是否可信——这份作品集的工程证明就算完整了。

---

## 来源

**官方职位**

- Anthropic, Research Engineer, Model Evaluations — https://job-boards.greenhouse.io/anthropic/jobs/5198255008
- OpenAI, AI Systems Engineer, Codex Agents — https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588
- OpenAI, Applied AI Engineer, Codex Core Agent — https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c
- LangChain, Deployed Engineer, Early Career — https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522
- LangChain, Fullstack Software Engineer, Applied AI — https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d
- Cognition, Applied AI Engineer — https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d
- Sierra, Software Engineer, Agent — https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d

**官方技术资料**

- Anthropic, Building effective agents — https://www.anthropic.com/research/building-effective-agents
- Anthropic, Demystifying evals for AI agents — https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents
- Anthropic, Writing effective tools for agents — https://www.anthropic.com/engineering/writing-tools-for-agents
- OpenAI, Evaluation best practices — https://developers.openai.com/api/docs/guides/evaluation-best-practices
- OpenTelemetry, Traces — https://opentelemetry.io/docs/concepts/signals/traces/
- MCP, Tools specification — https://modelcontextprotocol.io/specification/2026-07-28/server/tools

**AI Coding Club**

- Agent Engineering Hub — /zh/docs/agent-engineering/
- Career 基础页 — /zh/docs/course/career/portfolio-interviews/

---

## 继续阅读 AI Agent 面试系列

- [面试与求职指南](/zh/docs/tutorials/ai-agent-interview-guide/)
- [求职作品集](/zh/docs/tutorials/ai-agent-portfolio-guide/)
- [系统设计面试](/zh/docs/tutorials/ai-agent-system-design-interview/)
- [故障分析与评测面试](/zh/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
