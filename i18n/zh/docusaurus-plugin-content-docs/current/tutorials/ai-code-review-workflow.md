---
title: "AI Code Review 工作流：合并之前，Agent 到底该检查什么？"
description: "建立一套可追溯的 AI Code Review 工作流，在合并前检查改动意图、运行时行为、测试证据、风险边界和最新 diff。"
keywords:
  - AI Code Review 工作流
  - AI 代码审查清单
  - AI Pull Request Review
  - Coding Agent Review
  - 合并代码前检查什么
sidebar_position: 9
tags: [tutorial, coding-assistant, agent-engineering, code-review]
---
# AI Code Review 工作流：合并之前，Agent 到底该检查什么？

上周我在 AI Coding Club 的仓库里处理了一个统计修正，改动本身不复杂。有一条 `href="#"` 的同页 roadmap 链接，在原有分类逻辑下可能被算作外部 roadmap conversion——在原有分类逻辑下，同页锚点跳转可能被当成目标页面的增长事件。修复思路是：把当前页面的 pathname 传给目标分类器，对来源和目标 pathname 做标准化比较；如果目标仍然是同一页面，就不再把它算作增长目标。

改完之后我看了一眼测试结果，九项针对性检查全部通过。那一刻我差点就直接提 merge。

然后我停了下来，因为我知道"测试绿了"和"改动可以合并"之间有一段距离，而填满这段距离的工作，才是 AI code review 真正该做的事。

如果你想把这套证据模型落到具体语言和工具链，可以继续看[如何验证 Coding Agent 生成的 Go 代码](/zh/docs/tutorials/verify-ai-generated-go-code/)：它会把应用契约、可执行检查和残余风险组织成一套可复现的 Go 验证流程。

---

## 先给一个直接答案

很多开发者已经在用 Claude Code、Codex、GitHub Copilot 或其他 Agent 来帮忙写代码、修 bug、审查 PR，但遇到的困境大多相似：Agent 给出的结论要么是"LGTM"加几句泛泛的表扬，要么是一份从代码里逐行扒出来的问题清单，却没有说清楚"到底能不能合并"。

合并之前，一个 Agent review 应该能够回答这五个问题：

1. **改动意图和范围**：这个 diff 想改变什么行为，哪些行为必须保持不变？
2. **真实行为变化**：顺着 caller 和系统上下文，运行时实际改变了什么？
3. **验证是否有效**：这些测试不只是通过了，而且在问题重现时真的会失败？
4. **风险边界在哪里**：改动有没有触及不能用自动工具安全判断的领域？
5. **结论针对最新 diff**：review 之后又有新的 push 了吗？还有哪些重要假设没有验证？

这五项责任不是某家公司的官方方法论，是我在持续维护真实仓库的过程中形成的综合判断——一个 Agent 的结论，只有能够追溯到预期行为、可执行证据、最新 diff 和明确写出的不确定性，才真正有用。

---

## 一：先确认改动意图，而不是直接看 diff

我回到那个统计修正的 PR，第一件事不是打开 diff，而是把改动意图写出来：

> **预期改变的行为**：同页跳转（`href="#"` 或指向相同 pathname 的链接）不再被分类为外部 roadmap 目标；合法的跨页 roadmap 链接必须继续被追踪。
>
> **必须保持不变的行为**：点击一个跨页 roadmap 链接时，事件仍然应该触发并被正确分类。

这两句话写出来之后，我才去看 diff。

很多人习惯倒过来做：先看 diff 再推断意图。这在自己写的代码里有时候没问题，但当 Agent 生成或修改代码时，diff 和需求之间的漂移经常在细节里。如果意图本身就是模糊的，Agent 只能猜测成功标准。一旦意图不清楚，所有后续的验证都变成了对猜测的验证。

另一个值得检查的问题是 diff 的边界：这次改动有没有混入与需求无关的内容？比如顺手改了缩进、重命名了变量、调整了函数签名。这些本身可能没有问题，但它们模糊了"这个改动究竟证明了什么"——review 是对 diff 整体做的，不只是对那几行关键逻辑做的。

---

## 二：顺着 caller 追行为，不只是读 diff

分类器函数本身改起来不难，但我需要知道调用方传进来的是什么。

在这个统计修正里，click handler 传给分类器的是浏览器解析后的绝对 `link.href`，而不是 HTML 里的原始 `href` 字符串。这一点很重要：`href="#"` 在浏览器里解析出来是完整的当前页面 URL 加上一个 fragment，不是字符串 `"#"`。

如果我只看 utility diff，我看到的是"函数多了一个参数，多了一个比较逻辑"，我不会看到"调用方实际传入的是绝对 URL，所以标准化步骤是必要的，不是可选的"。

顺着 caller 追行为，最终要问的是：用户、存储数据、分析系统或下游系统会观察到什么变化？这次修正之后，同页目标不再进入 roadmap 分类，跨页目标保持不变。这是预期的行为变化，不是 bug。但如果我没有把这个变化明确写出来，任何看这个 PR 的人都可能把分类结果变化当成新的问题。

从上下文出发，也可以推出边缘场景：

- 同页的基础 URL（没有 fragment）：不应该算 conversion。
- 同页的 fragment URL（`/page#section`）：不应该算 conversion。
- 跨页的 roadmap 目标：应该继续算 conversion。

这三类行为都必须在验证里被明确覆盖。

---

## 三：验证本身是否有效，而不只是看它有没有通过

"九项针对性检查全部通过"这句话让我停下来是有原因的：测试通过是一个事实，测试对目标行为有效是一个需要独立判断的问题。

本地命令共通过九项检查；以下三项直接针对本次修正，并非全部九项：

- 同页基础地址的场景：正确，应该返回 `null`（不是 roadmap conversion），断言覆盖了。
- 同页 fragment URL 的场景：正确，应该返回 `null`，断言覆盖了。
- 跨页 roadmap 目标的场景：正确，应该返回 `'roadmap'`（是 roadmap conversion），断言覆盖了。

保留场景被覆盖了，这一点很关键。只测试"错误场景被修复了"而不测试"正确行为没有被破坏"，是测试有效性最常见的漏洞。

但我也写下来了这组检查**没有证明什么**：

- 所有可能的 analytics event 类型。
- 浏览器实际的交互行为（这是 focused unit test，不是 browser test）。
- 部署之后生产数据的变化。
- 分类器被其他 caller 调用时的行为。

2026-07-20 的一次本地重新验证，这九项检查全部通过。这是支持合并的证据，不是合并的充分条件。

---

## 四：识别风险边界，知道什么需要升级

这次统计修正触及的是分析数据的分类逻辑。风险边界包括：

- **统计一致性**：如果分析基础设施依赖历史分类数据做对比，可能需要评估潜在影响。

在这个具体案例里，改动范围比较清晰，我没有触及认证、支付、个人数据或数据库 migration。但这个评估本身就是 review 的一部分，而不是默认可以跳过的步骤。

Google Engineering Practices 明确要求 reviewer 检查的范围包括：design、functionality、complexity、tests、naming、comments、style，以及更广的系统上下文。OWASP Code Review Guide 指出，即使自动安全扫描在持续进步，manual security code review 仍然是安全开发生命周期的重要组成部分。

对于涉及认证、授权、secret 管理、支付流程、个人数据、并发控制、基础设施变更、无障碍合规或其他高风险边界的改动，自动工具能帮助到一定程度，但最终判断必须由人或具备资质的专业 reviewer 完成。

"`needs specialist review`"是一个诚实且有效的结论，不代表工作流失败，也不代表 Agent 做错了什么。它代表这段判断超出了自动检查和通用 review 可以安全覆盖的范围。

---

## 五：结论针对最新 diff，还有哪些假设没有验证

这是最容易被忽略的一步，也是让我觉得很多 AI review 工具目前做得最差的地方。

GitHub Copilot 的 code review 工作方式是提交 `Comment`，而不是 `Approve` 或 `Request changes`。这意味着 Copilot 的 review 不计入仓库要求的 required approvals，也不会自行阻止合并。如果在 Copilot review 之后又有新的 push 进来，而没有重新请求 review，之前的 finding 就可能已经不再针对最新的代码状态。

这不是 Copilot 的特有问题，而是任何 Agent review 都必须面对的一致性问题：我的结论是基于哪一个 commit 的？这个 commit 还是最新的吗？

在我的统计修正里，2026-07-20 重新验证时，上述九项检查在当时本地代码状态上全部通过；这次重新验证的证据范围仅限于该次本地运行，不覆盖后续新的 push。

但我还是写下了未解决的假设：

- **生产验证**：九项 focused classification test 通过了，但完整 analytics event pipeline、browser 交互和 deployment 行为未被覆盖——这是部署后需要观测的，不是 review 阶段能够关闭的风险。

把这些假设明确写出来，不是在说"这个 PR 不能合并"，而是在说"合并之后还需要做这些事"。这种诚实比一个宽泛的"LGTM"有价值得多。

---

## 四种角色，四种责任

在一个真实的 PR 流程里，有四个角色，它们的责任不能互相替代：

| 角色 | 主要责任 |
|---|---|
| **自动检查**（lint、typecheck、CI、test suite） | 在边界明确的场景下产生可重复的机械证据 |
| **Agent review**（Claude Code、Copilot 等） | 结合需求、diff、上下文和证据，报告 finding 与合并结论 |
| **Human reviewer / specialist** | 承担不能安全委托给自动工具或通用 Agent 的判断 |
| **仓库规则**（branch protection、required checks） | 决定技术上是否允许合并 |

很多开发者在用 Agent 的时候会不自觉地把这四个角色压缩成一个：只要 Agent 说没问题，CI 也绿了，就直接 merge。问题是，Agent 的 `Comment` 不是 required approval，CI 通过不等于行为正确，仓库规则里启用了哪些保护取决于配置，而不是默认就有。

把这四个角色分开，不是在加重负担，而是在明确每一步工作的依据和边界。

如果你想把这套 review 顺序封装成可复用流程，或者在明确事件上增加自动检查，可以继续看 [Claude Code 的 Skills、Hooks 和 MCP](/zh/docs/tutorials/claude-code-skills-hooks-mcp/)。

如果你需要更广的安全、隐私和专业使用边界，可以参考 [AI 编程最佳实践](/zh/docs/best-practices/)。

---

## 可复用的 Review 输出格式

合并之前，我会要求 Agent 填写这个格式：

```
Verdict: block / ready after named checks / needs specialist review

Intended change:
（预期改变的行为，以及哪些行为必须保持不变）

Observed behavior change:
（运行时实际改变了什么，包括 caller 上下文和下游影响）

Checks run and results:
（运行了哪些检查，具体覆盖了什么场景，结果如何）

Blocking findings:
（阻止合并的问题，需要解决后重新 review）

Non-blocking findings:
（建议改进但不阻止合并的问题）

Unverified assumptions or residual risk:
（合并后仍需验证的重要假设或已知但可接受的残余风险）
```

这是我提出的"合并证据包"格式，不是 GitHub review status，也不是行业官方模板。

避免只有一句 `approve` 或 `looks good`。如果是否 ready 取决于一个还没有运行的检查，就写 `ready after named checks`，并明确说出检查名称——比如 `ready after browser integration test`，而不是一个空洞的放行判断。

用这个格式回到统计修正案例，结论大致是：

```
Verdict: ready after named checks

Intended change:
同页跳转不再被分类为外部 roadmap conversion；
跨页 roadmap 链接继续被追踪。

Observed behavior change:
分类器接收 caller 传入的浏览器解析后绝对 URL，
通过 pathname 标准化比较判断是否为同页链接；
同页目标返回 null，不进入 roadmap 分类；
合法跨页 roadmap 目标仍返回 'roadmap'，保持不变。

Checks run and results:
9 项针对性检查（2026-07-20 本地验证），全部通过；
覆盖：同页基础 URL、同页 fragment、跨页 roadmap 三类场景。

Blocking findings: 无

Non-blocking findings:
无

Unverified assumptions or residual risk:
- 完整 analytics event pipeline 未被覆盖
- browser 交互行为未被覆盖
- deployment 行为未被覆盖
```

这不是信心分数，是可追溯的证据集合。

---

如果你还在建立从给出任务、检查 diff 到运行验证的基础流程，可以先看 [AI 编程 Agent 新手路线](/zh/docs/tutorials/ai-coding-agent-beginner-guide/)。

---

## 给你的下一步

选一个你手头正在 review 的 PR，或者让 Agent 正在处理的改动：

1. 用一两句话写出**预期改变的行为**和**必须保持不变的行为**。
2. 顺着 caller 追一遍，确认运行时实际改变了什么。
3. 找到最窄但有意义的检查——不是所有测试，是明确覆盖目标行为和保留场景的那几个。
4. 在合并之前，记录下**仍未解决的不确定性**，哪怕只有一条。

这四步会让"可以合并了"这句话变得有依据。

---

## 参考资料

- [GitHub Copilot Code Review — Concepts](https://docs.github.com/en/copilot/concepts/agents/code-review)
- [GitHub Copilot Code Review — Use Code Review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review)
- [GitHub — About Pull Request Reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
- [GitHub — About Protected Branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- [Google Engineering Practices — What to Look For in a Code Review](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- [OWASP Code Review Guide](https://owasp.org/www-project-code-review-guide/)
