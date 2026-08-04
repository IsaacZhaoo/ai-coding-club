---
title: "AI Agent 工程师面试与求职指南：能力地图、面试题与项目准备"
description: "从 AI Agent、Applied AI 与 Agent Systems 职责出发，建立能力地图、面试练习、作品集证据链和可执行求职准备路线。"
keywords:
  - AI Agent interview
  - AI Agent engineer interview
  - Agent Engineer interview questions
  - LLM Agent jobs
  - AI Agent 面试
  - AI Agent 工程师
sidebar_position: 27
tags: [tutorial, career, agent-engineering, interviews]
---
# AI Agent 工程师面试与求职指南：能力地图、面试题与项目准备

---

如果你已经学过 Prompt 设计、MCP、Memory 管理和 Agent 框架，也做过自己的 Agent 项目，但面对 AI Agent 工程岗位的 JD 时仍然感到不确定——不清楚岗位职责是怎么分的、面试会考什么、手上的项目经验该如何转化成可说清楚的证据——这篇指南正是为这个阶段准备的。

AI Agent 工程岗位的职位名称是分散的，但背后的职责方向可以归纳。本文参考七个官方职位样本，整理出一张跨岗位的能力地图，说明这类岗位在职责层面真正关注什么，以及如何把已有的技术知识组织成面试中可解释的素材。

准备这类岗位面试的核心工作是：把模型、上下文、工具、循环、权限、观察和评测组织成一个可解释、可验证的系统，再用同一个项目的证据说明这些工程决策。技术知识和项目经验需要同时具备，两者缺一都难以应对有深度的追问。

指南结构如下：先从七个岗位样本读出四类职责方向和五个能力域，再展开每个域的工程边界，然后给出六类准备场景、15 道代表性练习题，以及作品集证据链的最小要求。最后说明如何把同一份材料复用在简历、介绍和 STAR 回答里。

---

## 一、先看清楚岗位在考什么

### 职位名称是分散的，职责方向是可归类的

这份能力地图参考了以下官方职位：

- OpenAI, AI Systems Engineer, Codex Agents
- OpenAI, Applied AI Engineer, Codex Core Agent
- Anthropic, Research Engineer, Model Evaluations
- LangChain, Deployed Engineer, Early Career
- LangChain, Fullstack Software Engineer, Applied AI
- Cognition, Applied AI Engineer
- Sierra, Software Engineer, Agent

名称各异，但职责段落展示出可归纳的结构。读 JD 最有效的方式是先看职责的对象是什么、运行环境是什么、失败责任落在谁身上、要求用什么动词来描述过去的工作——标题用于搜索，职责段落才是判断方向的依据。

根据这七个样本，职责方向大致分为四类。这四类是阅读这七个 JD 的分析坐标，允许重叠；同一职位可以跨两个方向，阅读时需要结合职责段落综合判断。

**Agent Systems / Harness**：负责执行框架本身的设计和可靠性。OpenAI Codex Agents 职位的核心责任落在 harness、execution loop、sandbox、orchestration 和生产可靠性上，是这一方向的典型样本。

**Applied AI / Product Agent**：负责把模型能力落地成有用的产品特性。OpenAI Codex Core Agent 职位强调 real-world coding tasks、prompt/tool/context 实验、eval 和 measurable improvement。Cognition 职位同时带有 Applied AI 和客户部署特征，职位强调 playbook、adoption 和 measurable impact，准备时可以重点练习实验循环和可量化改进的表达。

**Deployed / Customer Agent Engineering**：负责把 Agent 系统部署到真实用户或客户环境中。LangChain Deployed Engineer 职位的职责明确涉及 production Agent、multi-step workflow、failure handling、架构沟通和客户交付；LangChain Fullstack Applied AI 职位则侧重 end-to-end Agent、evaluation pipeline、monitoring、production deployment 和跨团队沟通，与 Deployed 职位有重叠但不完全相同。

**Agent Research / Evals**：负责评测框架和研究方向。Anthropic Research Engineer, Model Evaluations 职位的核心职责包括设计针对 agentic behavior 的评测、加固分布式评测执行平台、调试异常 eval 结果（区分模型变化与 harness/data/infrastructure 问题），以及改进 eval 工具链。Sierra Software Engineer, Agent 职位的重心在 production-grade Agent 与完整 Agent development lifecycle，eval/RAG/prompt 是其中的技术基础，侧重生产交付而非研究评测。

### 五个能力域：跨岗位的准备地图

以下五个能力域是针对七个样本整体整理的准备地图，它们是能力维度，不同 JD 覆盖不同的域，准备时对照自己的目标岗位方向调整权重。

**域一：系统基础** — model、provider、context window、memory 和 harness 各自负责什么，边界在哪里。

**域二：工具与协议** — tool schema、tool contract、MCP、hook 和副作用如何设计和验证。

**域三：运行与编排** — loop 如何停止、graph 如何传状态、并行子任务如何隔离。

**域四：可靠性与安全** — trace 和 span 如何结构化、eval 如何持续运行、权限边界如何在运行时执行。

**域五：交付与维护** — Agent 如何部署到真实环境、如何响应后续需求变化、如何向团队和客户交付可解释的结果。

读 JD 时，先判断岗位方向，再对照五域评估自己的准备权重。

---

## 二、五个能力域的工程边界

### 域一：系统基础

Agent 系统的第一层工程能力，是能清楚说明各组件的职责边界。

Harness 是本文采用的一种执行层工作模型——把 model 调用、工具分发、状态管理和循环控制组织在一起的执行容器——各团队术语可能不同。Memory 在工程上是一个关于"什么信息在什么时候对模型可见"的设计决策，数据库是可能的存储实现之一，关注点在信息可见性策略而非存储介质本身。两者的职责边界是常见的理解模糊点，准备时可以练习画出组件图并解释每一条箭头代表什么交互。

### 域二：工具与协议

工具是 Agent 与外部世界交互的接口，一个没有明确 contract 的工具调用是未经控制的副作用来源。需要区分清楚四件事：

- **Schema**：负责输入输出的结构校验，确保调用参数格式正确。
- **Tool contract**：在 schema 之上还要说明语义、错误行为、幂等性和副作用——两者不能混用。
- **Authorization / policy guard / approval / sandbox / audit**：负责运行时的权限边界，决定工具能不能被调用、被谁调用，以及调用后留下什么审计记录。这一层在工具执行前实施边界，与 fixture/eval 属于不同层次。
- **Fixture / eval**：覆盖正常 case 和失败 case，验证实现是否满足 contract——它们是验证机制，不替代运行时控制。

Cognition 职位明确提到 MCP integration。MCP 规范了 host/client 与 server 之间的交互协议，让不同系统之间的工具描述有共同格式；但 MCP 不会自动提供业务语义、授权、幂等性或副作用治理，这些仍然需要在 tool contract 层面明确处理。

### 域三：运行与编排

Loop 的终止条件是这一域需要重点练习的设计点。模型的完成判断必须经过独立守卫逻辑校验。

OpenAI Codex Agents 职位强调 orchestration 和 sandbox，指向一类工程问题：在多步骤、多组件的系统里，状态正确传递，并把失败限制在各自边界内。

并行任务的隔离值得重点练习。Git worktree、sandbox 边界、并发写入冲突的处理方式，都需要有具体实现经验或设计决策来支撑，仅凭概念描述难以应对深入追问。

### 域四：可靠性与安全

这是区分"能搭原型"和"能交付生产系统"的核心能力域。

**Trace** 的工程目标是：在关键失败发生时能够重建因果链，定位根因。实现方式是保存足够的关联字段——identity、parent、tool call、retry、handoff 等——来重建关键事件序列，同时显式记录 telemetry gap，说明哪些环节的观察是缺失的。Trace 能重建什么范围由埋点与关联字段决定，单行 `print` 语句无法承担这一任务。

**Eval** 的工程模型需要说明：task/case 的定义、grader 的设计（如何判断输出是否达标）、重复 trial 的次数、suite 的组织方式，以及 gate（什么条件下 CI 会拦截合并）。Eval 既可以检查最终 outcome，也可以约束关键 trajectory。单次手动测试缺少 suite、trial 与 gate，在追问中很难支撑关于 eval pipeline 的讨论。

Anthropic Research Engineer, Model Evaluations 职位的一个典型职责场景是：eval suite 在训练过程中返回异常数字，需要在时间压力下判断原因是模型变化、harness、data 还是 infrastructure 问题——这类调试判断与 Domain 4 的能力高度重合，是值得重点练习的场景。

**Security boundary** 约束系统允许执行的动作范围，在运行时必须有独立的执行机制：声明权限范围，在调用时校验，越权操作被拦截并记录到 audit log。Trace 记录实际执行路径与 telemetry gap，eval 检查 outcome 与关键 trajectory，三者互相提供证据。任何一项都不保证模型行为本身天然可预期，这三个机制是互补关系，不能相互替代。

### 域五：交付与维护

LangChain Deployed Engineer 职位的职责涉及架构沟通与客户交付。Cognition 职位强调 playbook、adoption 和 measurable impact。这说明部分 Agent 工程岗位的核心交付包括写代码、把 Agent 系统嵌入真实团队的工作流、维护和反馈闭环，并产生可量化的改变。

准备时可以重点练习：说清楚系统在部署后如何被使用、如何被维护、如何响应真实用户反馈，以及如何向非工程背景的人解释系统行为。LangChain Fullstack Applied AI 职位的职责包含 monitoring 和 evaluation pipeline，可以用来检查自己的回答是否覆盖了持续运维的维度。

---

## 三、六类准备场景

以下六类准备场景是根据这七个岗位的职责要求转换出来的，供定向练习参考，不代表任何公司已采用的面试流程或题型设计。

**1. 概念问题**

核心工程概念的准确边界和 trade-off，比定义本身更重要。准备时可以重点练习从"是什么"过渡到"和什么不同、代价是什么、在什么条件下成立"。例如，"Harness 是什么"是起点，"Harness 和 Agent loop 的边界是什么、哪些逻辑不应该放进 loop 内部"才是需要练习的回答深度。

**2. 系统设计问题**

给一个具体场景，要求设计方案并说明工程决策。准备时可以重点练习主动说明组件边界、失败模式、可观察性点和扩展路径。"我会用 X 框架"覆盖的只是选型，还需要继续说明边界与失败；"在这个场景里我需要隔离三件事，原因是……"才是需要练习的表达结构。

**3. 故障分析问题**

给出 trace 日志或 eval 结果变化，要求定位根因。OpenAI Applied AI Engineer, Codex Core Agent 职位强调 failure analysis、feedback loop 和 measurable improvement；OpenAI AI Systems Engineer, Codex Agents 职位强调从 evidence 调试端到端失败。两者共同支持把 evidence-based debugging 作为准备方向，但均不代表公司真实面试流程。可以据此模拟追问，练习从 trace 重建事件序列、从 eval 指标变化推断改动影响的系统性调试思维。

**4. Hands-on 编码**

这类练习是根据七个职位职责设计的定向练习，补充 Agent 专门能力，与通用算法和软件工程准备并行，不推断真实编码面试形式。重点练习在真实或模拟的 Agent 代码库上做具体修改：实现带有 retry 逻辑的工具调用、为工具写 verified fixture，或者在 loop 中加入终止守卫逻辑。

**5. 项目 Deep Dive**

这类准备的核心是：确保自己的项目证据能支撑具体的工程追问。可以用以下问题检查项目覆盖度：为什么选这个 memory 架构？工具调用失败时系统会怎样？eval 覆盖了哪些场景？如果要上生产你会先改什么？缺乏具体证据的项目在这种追问下很难支撑。

**6. 行为问题**

准备时可以重点练习把技术细节嵌入 STAR 格式。"描述一次你发现 Agent 行为和预期不一致的情况，你是怎么定位和修复的"——Situation 和 Action 里需要有具体的技术细节，例如你看了哪层 trace、修改了什么 guard 逻辑、用哪个 eval case 验证了修复。

---

## 四、15 道代表性准备题

以下问题是基于七个岗位样本职责归纳的准备题，不归因于任何公司的面试题库，也不代表真实面试流程。每题后标注了需要说明的边界、trade-off 或 evidence，可以用来检查回答是否覆盖关键维度。

### 系统基础

**Q1. 在你设计的 Agent 系统中，harness 和 Agent loop 各自负责什么？它们通过什么接口通信？**
→ 说明职责边界、状态传递方式，以及哪些逻辑不应该放进 loop 内部。

**Q2. 当 context window 接近上限时，你的系统会怎么处理？memory 压缩的策略是什么？**
→ 说明压缩触发时机、哪些信息优先保留、压缩对任务连续性的影响。

**Q3. 如何向一个新加入项目的工程师解释你的 Agent 系统的整体架构？**
→ 练习用准确但不过度复杂的语言描述模块边界，是系统理解深度的一个检验点。

### 工具与协议

**Q4. 设计一个工具契约时，你会包含哪些要素？schema 和 contract 的边界在哪里？如何验证工具的副作用在预期范围内？**
→ 说明 schema / contract / authorization / fixture 四层各自负责什么，不能混用。

**Q5. 工具调用遇到网络超时或服务不可用时，你的 retry 策略是什么？幂等性前提如何确保？**
→ 说明 backoff 策略、超时上限、幂等性假设、状态恢复机制。

**Q6. MCP 在多系统工具集成中规范了什么？它在哪些方面需要额外的工程处理？**
→ 说明协议标准化的价值边界，以及授权、幂等性和副作用治理仍需在哪层处理。

### 运行与编排

**Q7. Agent loop 的终止条件应该由谁决定？如果模型判断任务完成但实际上没有完成，你如何检测？**
→ 说明终止条件的来源、独立守卫逻辑的设计、eval 如何验证终止决策的质量。

**Q8. 并行处理多个子任务时，你如何确保各任务之间的状态不互相污染？**
→ 说明隔离机制（如 worktree、sandbox）、共享状态的访问控制、合并冲突处理。

**Q9. 多步骤任务在中间步骤失败后，你如何决定是重试、回滚还是中止？**
→ 说明失败分类逻辑、补偿操作、检查点机制、人工介入的触发条件。

### 可靠性与安全

**Q10. 描述你设计的 eval suite 的结构：覆盖了什么场景，用什么指标衡量，如何在代码改动后自动运行？**
→ 说明 task set 设计、grader 逻辑、重复 trial 次数、suite 组织方式、CI gate 条件，以及 eval 结果如何与历史基线对比。

**Q11. 生产环境出现一个难以复现的失败，你从哪里开始调查？trace 在其中起什么作用？**
→ 说明 trace 的结构和粒度、关联字段的选择、事件序列重建路径、telemetry gap 的处理方式。

**Q12. Agent 被要求执行一个超出预期权限范围的操作时，你的系统如何检测和阻断？**
→ 说明权限声明机制、运行时校验、audit log 记录、人工审查的触发条件。

### 交付与维护

**Q13. 如何判断当前 Agent 系统是否可以交付给真实用户？上线前会检查哪些项目？**
→ 说明检查清单内容、eval 达标标准、可观察性覆盖、回滚方案。

**Q14. 用户对 Agent 的输出提出投诉，你如何追溯问题根源？**
→ 说明从用户反馈到 trace 的链路、失败分类方式、修复—验证—发布循环。

**Q15. 如何比较两个不同版本的 Agent（例如修改了 prompt 或换了 memory 策略）的表现？**
→ 说明受控实验设计、相同 task set 的使用、可量化指标、比较结论的可信度前提。

---

## 五、主作品集项目的证据链

简历上写"构建了一个 AI Agent 系统"在深入追问下没有支撑力。

一个能经得起追问的项目，不需要规模庞大，但需要证据完整。最小证据合同包括八类材料、九个要素（README 与可复现命令合为一类）：

### 九个要素

**Architecture 文档**：一张组件图，说明 model、harness、memory、工具和外部服务之间的关系，以及每条连线代表什么交互。不需要精美，但必须准确，且能在追问时直接引用。

**Task Set**：一组定义明确的任务，说明系统被期望完成什么、在什么条件下被认为成功。Task set 是整个证据链的起点，没有它，eval 就失去了基准。

**Tool Contract**：每个工具的完整契约，包括 schema 定义、语义说明、错误行为、幂等性标注和副作用声明。对应的 fixture/eval 覆盖正常 case 和失败 case，验证实现是否满足 contract；运行时的 validator、authorization、policy guard 在工具执行前实施边界——这两层各有分工，不能混用。

**Trace 样本**：一条包含关键关联字段、关键事件和显式 telemetry gap 的 trace 样本，展示从任务输入到关键节点的事件序列，包括工具调用、中间状态和决策节点。Trace 能重建什么范围由埋点与关联字段决定，telemetry gap 需要显式标记。这是失败调查的原材料，也是追问时最有说服力的具体证据。

**Eval 结果**：量化的评测结果，说明 task set、grader 设计、重复 trial 次数和 suite 覆盖范围。如果有多次运行的对比（例如修改 prompt 之后的前后对比），说明 eval pipeline 在持续使用中而不只是一次性展示。数值必须来自自己保存的真实测试记录，使用 `[基线] → [复测结果]` 的结构占位，不填没有依据的数字。

**Security Boundary 说明**：权限模型的说明，包括 Agent 被允许调用什么、被禁止调用什么，以及这个边界如何在运行时被执行。Security boundary 约束允许的动作范围；trace 记录实际执行路径与 telemetry gap；eval 检查 outcome 与关键 trajectory——三者互相提供证据，但任何一项都不保证模型行为天然可预期，需要分开说明。如果有 sandbox 配置文件或权限声明，直接附上是最清晰的证据。

**Failure Log**：至少一条失败案例的记录：失败发生的条件、实际行为与预期行为的差异、调查过程（具体看了哪层 trace、发现了什么）和最终修复。如果调查发现返回值缺少运行时 schema validation，修复应当针对 runtime validator 或 guard，并在 fixture/eval 中增加对应的 case——这和 contract 文档本身是不同层次的工作。这是展示调试能力最直接的素材，也是 STAR 行为问题的原材料。

**README 与可复现命令**：一个清晰的 README，说明如何在新环境中启动系统、如何运行 eval、如何查看 trace。可复现性是系统工程能力的基础信号，可复现命令是项目"过程"最直接的证明。

### 九个要素如何互相校验

Task set 定义成功标准，所有后续的评测都必须对照它。Trace 重建一次具体运行，能解释在哪个步骤发生了什么、为什么失败。Failure log 把 trace 里发现的失败沉淀成新的具名案例，让它从一次偶发事件变成可以被 eval 覆盖的已知场景。Eval 在修复后重新运行，对比修复前后的指标，并在后续每次代码改动后自动回归。Security boundary 限制系统能做什么，trace 和 eval 则从不同角度提供行为证据，但三者都不保证模型行为本身可预期。README 和命令把这些证据交给第三方复现，而不只是听候选人描述。

当追问"你的 eval 覆盖了哪些场景"时，答案可以直接引用 task set 里的定义；追问"这个失败是怎么发现的"时，答案可以从 trace 追溯到 failure log；追问"修复后怎么验证"时，答案可以直接引用 eval 对比数据。

---

## 六、把同一份证据包转化成不同用途

一套完整的项目证据，可以在求职的不同环节被复用，不需要为每个场景重新准备材料。

### 简历 Bullet

框架名称本身不说明任何工程决策。改写方向是"动作 + 边界/任务 + 真实测量 + 验证方式"。例如：

- 设计了支持并行工具调用的 Agent harness，将任务成功率从 `[基线]` 提升到 `[复测结果]`（来自 eval pipeline 记录）
- 构建了覆盖 `[真实任务数]` 个场景的 eval suite，集成到 CI 流水线，每次 PR 自动回归
- 实现了运行时权限声明与校验机制，audit log 完整记录工具调用边界执行情况

每个 bullet 里的数字必须来自自己保存的真实测试记录。记录工具经历；能力由工程决策和证据来体现。

### 五分钟项目介绍

结构建议：

1. **任务背景（30 秒）**：系统被设计来解决什么实际问题？
2. **架构决策（90 秒）**：最核心的两三个工程决策是什么？选择这个方案的条件和代价是什么？
3. **验证方式（60 秒）**：你怎样知道它是有效的？eval 说明了什么？
4. **关键失败（60 秒）**：你遇到过什么重要的失败？是怎么调查和修复的？
5. **如果继续做（30 秒）**：你会先改什么？

选择仍有不确定性的决策来讨论，比选择已经完美的部分更能展示工程判断力。

### 深入追问应对

当追问到"为什么这样设计"时，有效的回答结构是：条件 → 决策 → trade-off → 验证。

例如："因为任务之间没有共享状态（条件），我选择了进程级隔离（决策）。代价是启动开销增加了（trade-off，填入真实测量值），但 eval 显示这对任务成功率没有负面影响（验证，引用具体 eval 结果）。"

这个结构的每一步都需要真实支撑，不能用未经验证的数字填充。

### STAR 素材

把 Failure Log 里的每一条记录重新组织成 STAR 格式：

- **Situation**：当时系统的状态和任务背景
- **Task**：需要解决的具体问题
- **Action**：具体做了什么调查和修改（这里必须有技术细节：看了哪层 trace、发现了什么、修改了哪个 guard 逻辑、在 eval suite 里新增了什么 case）
- **Result**：最终结果和可量化的改进，直接引用 eval 对比数据

Action 部分的技术细节是区分点。空泛的 Action 描述无法支撑追问。例如："我从 trace 里发现第三步工具调用的返回值缺少运行时 schema validation 就直接传入了下一步，随后修改了 runtime validator 增加了校验逻辑，并在 eval suite 里新增了这个边界场景作为回归 case"——这才是可以支撑追问的 Action。

---

## 七、一个阶段式准备循环

采用可反复迭代的循环，本文不作固定周期承诺。每一圈的目标是让证据包更完整、工程决策更有支撑。

**补知识缺口**：对照五个能力域评估自己的薄弱点。对 Observability 的理解停留在概念层面，就去实际配置一次 trace 系统并记录输出。还没有设计过 eval suite，就用现有项目补一个。知识缺口通过一个具体的小实现来验证，比通过阅读文档更有效。

**选一个主项目并补齐证据**：选一个已有项目，对照九个要素，把缺少的 trace 样本、eval 结果、failure log 和 security boundary 说明补上。一个证据完整的中等项目，远比十个没有验证的 demo 更有价值。

**保存可检索的证据**：把 trace 样本、eval 结果和 failure log 以文件形式保存在项目仓库里，而不只存在记忆中。能调出一条真实的 trace，比描述"我曾经看到过一次这样的失败"有效得多。

**模拟追问**：针对每一个简历 bullet 和项目介绍段落进行反复追问。追问的三个核心问题是："这个方案的条件和代价是什么？""你怎么知道这个决策是对的？""如果这个假设是错的，系统会怎样？"能回答这三个追问的设计决策，才是真正可以写进简历和说进面试的内容。

**改表达**：追问过程会暴露哪些表达是模糊的、哪些 trade-off 还没想清楚、哪些证据是以为有但实际上没有的。把这些发现带回第一步。

---

## 八、关于框架名堆满简历这件事

"熟练使用 LangGraph、AutoGen、CrewAI 和 DSPy"这一行字，不回答任何能力域的问题，不提供任何工程决策的证据，不说明任何关于系统设计的判断。

框架名是工具。说你用过某个框架，和说你能解释在什么条件下应该用它、它的哪些设计决策是你有异议的、你曾经因为它的某个限制做了什么样的变通——这是两件完全不同的事情。

后者需要的是具体的工程决策、有来源的 trade-off 分析、可引用的项目证据——也就是这篇文章一直在说的那些东西。

---

## 九、三个值得继续深入的方向

这篇文章的重点是面试准备层面的能力地图。有三个方向在这七个样本岗位的职责里反复出现，值得单独展开：

一是**作品集、简历与项目 Deep Dive 的完整准备**：如何把单个项目的证据链组织成面试材料，如何练习说明个人贡献、过程、障碍和处理方式。

二是 **Agent 系统设计面试**：如何针对"设计一个能处理并行任务的 Agent harness"这类开放问题，系统地说明组件边界、失败模式和扩展路径——答案需要超出框架选型，继续说明边界与失败处理。

三是**故障分析、Observability 与 Evals 面试**：如何建立一个可以在生产失败时重建因果链的 trace 系统，如何设计一个能在 CI 里自动运行并提供量化信号的 eval pipeline，以及如何在面试中用具体证据回答这类追问。

这三个方向覆盖五个能力域的不同侧面：系统设计横跨域一到域三，故障分析与 Evals 集中在域四，作品集与 Deep Dive 则需要把所有域的证据组织成可以在面试中表达的素材。

---

## 来源

### 官方职位样本

- OpenAI AI Systems Engineer, Codex Agents: [https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588](https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588)
- OpenAI Applied AI Engineer, Codex Core Agent: [https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c](https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c)
- Anthropic Research Engineer, Model Evaluations: [https://job-boards.greenhouse.io/anthropic/jobs/5198255008](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- LangChain Deployed Engineer, Early Career: [https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522](https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522)
- LangChain Fullstack Software Engineer, Applied AI: [https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d](https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d)
- Cognition Applied AI Engineer: [https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d](https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d)
- Sierra Software Engineer, Agent: [https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d](https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d)

### 教学资料

- AI Coding Club Agent Engineering: [/zh/docs/agent-engineering/](/zh/docs/agent-engineering/)
- AI Coding Club 作品集与面试基础: [/zh/docs/course/career/portfolio-interviews/](/zh/docs/course/career/portfolio-interviews/)

---

*以上岗位仅用于归纳职责方向，不代表行业整体趋势、岗位增长率或薪资水平。*

---

## 继续阅读 AI Agent 面试系列

- [面试与求职指南](/zh/docs/tutorials/ai-agent-interview-guide/)
- [求职作品集](/zh/docs/tutorials/ai-agent-portfolio-guide/)
- [系统设计面试](/zh/docs/tutorials/ai-agent-system-design-interview/)
- [故障分析与评测面试](/zh/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
