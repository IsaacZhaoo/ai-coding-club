---
title: "Agent Skills 测试指南：如何测触发准确率、误触和上下文成本"
description: "用规范检查、目录预算、description 重叠、近似负例和真实激活记录，审计整套 Agent Skills 负载。"
keywords:
  - Agent Skills 测试
  - Skill 触发准确率
  - Agent Skills 误触
  - Skill description 重叠
  - Skills 上下文成本
sidebar_position: 21
tags: [tutorial, coding-assistant, agent-engineering, agent-skills]
---

# Agent Skills 测试指南：如何测触发准确率、误触和上下文成本

[上一篇博客](/zh/blog/too-many-agent-skills/)最后落到一个判断：**Skills 目录是一套路由界面，不是能力陈列柜**。

这句话听起来抽象，直到一套负载里的几个 description 开始竞争同一类请求——"帮我修一下这段 Python 代码"可能触发测试修复 Skill，也可能落到代码审查 Skill，还可能什么都不触发。装进去的每一个 Skill 都在重塑整套路由，而你并不知道装之前的平衡是什么，装之后打破了什么。

这篇教程要补上的就是这块：**不是怎么测单个 Skill，而是怎么审计整套负载之间的竞争关系**，并且用一个可跨客户端记录激活结果的 JSONL 合同替代对着文件猜谁会赢。

## 整套负载应该测什么

直接给结论，四层，从里到外：

| 层次 | 问题 | 工具 |
|------|------|------|
| **规范正确** | name 格式、description 长度、父目录一致 | `skills-ref validate` + 本文夹具 |
| **目录成本** | 整套 Skills 的字符数与本地 Token 估算 | 夹具 audit 命令 |
| **description 竞争** | 多个 description 对同一请求的静态重叠 | 夹具重叠检测 + lexical smoke test |
| **真实激活** | Agent 实际选了哪个 Skill、有没有选错 | 客户端证据写入激活 JSONL + score 命令 |

不要只做第一层。规范正确只代表文件满足格式；目录成本给出 progressive disclosure 第一层元数据的本地估算；description 竞争暴露静态词汇边界；真实激活是唯一不能被猜测替代的证据。夹具实现前三层，并对你从真实客户端记录的第四层数据进行评分；它不会替所有 Agent 客户端自动抓取激活事件。

---

## 先跑，后解释

配套夹具的发布下载地址是 <a href="/examples/agent-skills-loadout-audit.zip">/examples/agent-skills-loadout-audit.zip</a>。夹具目录包含 5 个有效 Skills、`skill_loadout.py`、`test_skill_loadout.py`、`cases.jsonl`（20 条）和 `activations.example.jsonl`（合成数据，不代表真实 Agent 表现）。

第一步，验证夹具自身：

```bash
python3 -m unittest -v test_skill_loadout.py
```

预期：**10 个测试全部通过**。我重新运行后的结果是 10 个测试通过。

第二步，跑整套负载审计：

```bash
python3 skill_loadout.py audit \
  --skills-dir skills \
  --cases cases.jsonl \
  --max-estimated-tokens 300
```

原命令输出 JSON。关键字段如下：

```text
catalog.skill_count = 5
catalog.catalog_chars = 1065
catalog.estimated_catalog_tokens = 267
catalog.overlap_pairs = []
budget_passed = true

lexical_smoke_test.total = 20
lexical_smoke_test.correct = 18
lexical_smoke_test.accuracy = 0.9
lexical_smoke_test.failures = [
  near-api-implementation → api-documentation
  near-python-debug → python-test-fixer
]
```

**先记住这两个错误，先别急着修它们**。后面会解释它们在说什么。

---

## 四层的第一层：规范正确

官方规范是确定的：

- 一个有效 Skill 至少需要包含 `name` 与 `description` 的 `SKILL.md`。
- `name`：1–64 字符，只能用小写字母、数字和连字符；不能以连字符开始或结束；不能连续使用连字符；名称应与父目录一致。
- `description`：1–1024 字符，应说明 Skill 做什么、什么时候使用。

夹具的格式检查对应这些规则，但它不替代 `skills-ref validate`——官方参考验证器有更完整的边缘覆盖，本文夹具只做补充。

下面是 `skill_loadout.py` 里的实际检查片段：

```python
if len(name) > 64 or re.fullmatch(
    r"[a-z0-9]+(?:-[a-z0-9]+)*", name
) is None:
    diagnostics.append(Diagnostic("invalid_name", path, "..."))
if name != path.parent.name:
    diagnostics.append(Diagnostic("name_mismatch", path, "..."))
if len(description) > 1024:
    diagnostics.append(Diagnostic("description_too_long", path, "..."))
```

缺失的 `name` 与 `description` 会在这段代码之前直接产生诊断。这一层能发现的错误很具体：字段缺失、格式违规、名称和目录不一致。发现了就修，没有歧义。

---

## 四层的第二层：目录成本

progressive disclosure 的设计是 Agent 启动时先加载所有可用 Skill 的目录元数据，激活后再加载完整 `SKILL.md`。不同客户端怎样管理后续上下文可能不同。

`catalog_chars: 1065` 是 5 个 Skills 的 `name` 与 `description` 字符数之和。`estimated_catalog_tokens: 267` 来自"四个字符约等于一个 Token"的粗略估算，并使用向上取整：

```python
catalog_chars = sum(
    len(skill.name) + len(skill.description)
    for skill in skills
)
estimated_catalog_tokens = math.ceil(catalog_chars / 4)
```

**必须说清楚**：这个估算不是精确 tokenizer，也不是账单值。不同模型、不同语言、不同 tokenizer 的实际结果可能不同。四字符估算是本地启发式，用来在 CI 里设一个稳定的目录预算信号，不是用来对账单的。

`--max-estimated-tokens 300` 在审计中触发预算检查。当前 267 的估算没有超标，因此 `budget_passed` 为 `true`。

---

## 四层的第三层：description 竞争

重叠检测遍历所有 description 两两对，对经过统一分词和停用词过滤后的词集计算 Jaccard 相似度：

```python
left_terms = _description_terms(left.description)
right_terms = _description_terms(right.description)
union = left_terms | right_terms
similarity = (
    len(left_terms & right_terms) / len(union)
    if union else 0.0
)
```

audit 命令的默认阈值是 `0.45`，也可以通过 `--overlap-threshold` 修改。当前 5 个 Skills 在默认阈值下没有报告重叠对。

高 Jaccard 值本身不是路由错误，但它是一个检查信号：两个 description 共享较多归一化词汇，需要结合近似负例继续观察。Agent 不是 Jaccard 计算器，这个数值不能冒充 Agent 的实际选择。

**lexical smoke test** 更直接：它用 case 里的每一条 prompt，与 Skills 的 description 做词项交集计分；只有唯一最高分达到最低分数时才选择 Skill。这是纯机械路由，不涉及模型推理。

audit 的 20 条 case 里有 18 条正确，两个失败条目是：

**误触一**：`near-api-implementation`

原始 prompt 是：

```text
Implement a new API endpoint for creating invoices and add authentication.
```

它被送给了 `api-documentation`。静态规则命中了 `api`、`authentication`、`creating`、`endpoint` 四个词，但请求意图是实现，不是写文档。

**误触二**：`near-python-debug`

原始 prompt 是：

```text
Debug this Python cache bug; there is no failing test yet.
```

它被送给了 `python-test-fixer`。静态规则命中了 `failing` 与 `python`，却无法理解"还没有失败测试"这个否定边界。

这两个错误必须保留在 `cases.jsonl` 里。它们在说：**静态 lexical 路由不能模拟 Agent 的完整决策，audit 的 accuracy 不代表 Agent 的 accuracy**。

---

## 四层的第四层：真实激活记录

lexical smoke test 之后，剩下的问题只有一个：**真实 Agent 面对这些 prompt，会激活哪个 Skill**？

夹具使用的激活记录格式是 JSONL，每行包含 case id、运行编号、选中的 Skill 和客户端标签：

```jsonl
{"case_id":"python-pytest-failure","run":1,"selected_skill":"python-test-fixer","agent":"codex-cli"}
{"case_id":"near-api-implementation","run":1,"selected_skill":null,"agent":"codex-cli"}
```

`selected_skill` 为 `null` 表示 Agent 没有激活任何 Skill。客户端是否真的读取了相应 `SKILL.md`，需要由保留下来的客户端事件流或验证记录证明；紧凑的 JSONL 只保存可评分的路由结论。

评分命令：

```bash
python3 skill_loadout.py score \
  --cases cases.jsonl \
  --activations activations.codex-smoke-20260723.jsonl
```

项目里保存的 Codex 烟雾测试只有两次：

- **pytest 正例**：Codex 明确说使用 `python-test-fixer`，随后事件流显示它读取了对应 `SKILL.md`。
- **API 实现近似负例**：Codex 明确说没有合适 Skill，也没有加载 `api-documentation`。

两次在机械计算上完全正确，但两次没有统计意义，不能写"准确率 100%"，也不能由此推断 Agent 面对 20 条 case 会有怎样的整体表现。

`activations.example.jsonl` 是夹具里附带的合成数据，用来验证评分数学能否跑通，不代表任何真实 Agent 的表现。

### 评分指标

| 指标 | 问题 |
|------|------|
| **accuracy** | 所有记录中，选择与预期完全一致的比例 |
| **precision** | Skill 被激活时，激活的是预期 Skill 的比例 |
| **recall** | 应该触发时，预期 Skill 真的触发了的比例 |
| **误触** | 不应激活时激活了 |
| **漏触** | 应该激活时没有激活 |
| **错选** | 触发了，但选错了 Skill |

precision 回答"Skill 触发后，有多少次触发的是预期 Skill"；recall 回答"应该触发时，它有多少次真的触发"。近似负例是发现 precision 问题的关键材料。

---

## 关于 case 设计：正例与近似负例

官方 description 优化指南建议从约 20 个真实查询开始，包含 8–10 个正例与 8–10 个近似负例，重复运行，并保留训练集与验证集。

夹具的每一条 case 都有 `id`、`prompt`、`expected_skill` 和 `split`。`expected_skill` 为 `null` 的 10 条是近似负例，另外 10 条是正例；`split` 为 `train` 或 `validation`。

**近似负例的价值在"近似"二字**。不要用"给我讲个故事"这种完全不相关的 prompt 测 `python-test-fixer`——Agent 不触发也不能说明边界写得好。近似负例应该和 Skill 的核心词汇相邻，但意图不同，就像那个"还没有失败测试的 Python cache bug"。

`train`／`validation` 的分离用来减少过拟合：如果反复用同一批 case 调整 description，最终可能只是在优化对这批 case 的响应，而不是在提升对新表达的泛化。

---

## 一个小练习

在这里停一下，做一个具体实验：

1. 新增一个 description 与 `api-documentation` 明显重叠的 Skill，例如专门编写 HTTP request 示例的 Skill。
2. 增加一条位于两个 description 边界附近的 case，并写下你真正希望得到的 `expected_skill`。
3. 重新跑 audit，同时观察 `catalog.overlap_pairs` 与 lexical smoke test 的选择。

不要预设新 Skill 一定会跨过默认 `0.45` 阈值，也不要预设 lexical smoke test 一定选谁。这个练习的目的，是亲眼看到 description、阈值和 case 文本怎样共同改变报告。

---

## 目录预算与 CI

把 `--max-estimated-tokens` 加进 CI 流水线是夹具里最容易落地的一步：

```yaml
# .github/workflows/skills-audit.yml（示意，非完整配置）
- name: Skills Loadout Audit
  run: |
    python3 skill_loadout.py audit \
      --skills-dir skills \
      --cases cases.jsonl \
      --max-estimated-tokens 300
```

如果估算超过限制，JSON 里的 `budget_passed` 会变成 `false`；在没有其他 diagnostics 的有效目录中，命令退出码为 `2`。当前夹具在 300 下通过，在 250 下失败。

这不是精确计费，是量级预警。换成真实负载后，阈值应该根据自己的目录与上下文预算重新设定。

规范检查适合放在同一个 CI 阶段。但重叠检测和 lexical smoke test 更适合作为诊断信号，不应把一个 Jaccard 阈值或静态路由结果直接当成真实 Agent 的通用门禁。

---

## 下一个工程问题

现在假设你已经做完了四层审计，也收集了一些真实激活记录。剩下最硬的问题：**怎么系统性地拿到激活记录**？

如果客户端没有直接暴露 Skill 加载事件，你需要主动观测：

- 哪次调用触发了 Skill，而不是 MCP 工具或 Hook？
- Skill 加载后，上下文实际增加了多少？
- 如果多次工具调用串联，哪一步失败了，失败的代价是什么？

这是 [**Coding Agent Observability**](/zh/docs/tutorials/coding-agent-observability-guide/) 要解决的问题域：追踪 Agent 的工具选择、Skills 激活路径、handoff 链路、Token 成本和失败点。如果激活记录难以采集，审计就会停留在 lexical smoke test 层，无法进入真实激活这一层。

不是装了 Skill 就用上了，不是用上了就用对了。从 description 竞争到真实激活，中间缺的那一块，就是可观测性。

---

## 一手来源

- [Agent Skills 官方规范](https://agentskills.io/specification)
- [Agent Skills description 优化指南](https://agentskills.io/skill-creation/optimizing-descriptions)
- [Agent Skills 输出评测指南](https://agentskills.io/skill-creation/evaluating-skills)
- [`skills-ref` 官方参考验证器](https://github.com/agentskills/agentskills/tree/main/skills-ref)
- 配套夹具：<a href="/examples/agent-skills-loadout-audit.zip">/examples/agent-skills-loadout-audit.zip</a>
