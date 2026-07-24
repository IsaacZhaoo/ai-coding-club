---
title: "Coding Agent Evals 教程：把 Trace 变成数据集和质量门禁"
description: "把保存的 Coding Agent Trace 变成本地 JSONL 数据集、确定性检查、机器可读报告和 CI 质量门禁。"
keywords:
  - Coding Agent Evals 教程
  - Coding Agent 评测框架
  - Agent Evals 工具
  - Eval-Driven Development
  - Coding Agent 质量门禁
sidebar_position: 20
tags: [tutorial, coding-assistant, agent-engineering, evals]
---

# Coding Agent Evals 教程：把 Trace 变成数据集和质量门禁

> **下载夹具**：<a href="/examples/coding-agent-eval-gate.zip">/examples/coding-agent-eval-gate.zip</a>

---

上一篇 [Coding Agent Observability 教程](/zh/docs/tutorials/coding-agent-observability-guide/)里，我把一次真实的 Codex CLI 诊断记录完整保存了下来：工具调用序列、turn 状态、answer 文本，都落在本地的 JSONL 文件里。那篇到此为止——它解决的是"看见发生了什么"。

本篇解决的是下一个问题：**怎么让这份记录变成一个可反复执行的质量断言，并在 CI 里产生机器可读的通过/失败决定。**

我不会再重讲 Observability 接入、事件流结构或 Dashboard 搭建。如果你还没做过那一步，先去读上一篇，把那份 Codex 事件流保存好再回来。

---

## 一句话中心

> 有用的 Coding Agent Eval 会把任务和真实观测证据变成明确的 outcome 检查，以及有理由的资源或安全限制，然后输出机器可读的 gate 决定，而不是逼未来 Agent 重演某一条历史轨迹。

这句话驱动了下面所有的设计选择。

---

## 先跑起来：20 个测试 + 两条 Gate 命令

在展开任何设计细节之前，先验证本地环境可以跑通。夹具只依赖 Python 标准库，不需要安装任何第三方包。

### 运行单元测试

```bash
python3 -m unittest -v test_eval_gate.py
```

预期结果：**20 个测试全部通过**，无 SKIP，无 ERROR。

### 运行归一后的真实 Baseline

```bash
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials baseline-trials.example.jsonl
```

预期输出（节选）：

```json
{
  "case_count": 1,
  "trial_count": 1,
  "passed_trials": 1,
  "failed_trials": 0,
  "gate_passed": true,
  "results": [
    {
      "case_id": "average-empty-diagnosis",
      "trial_id": "codex-diagnosis-20260723",
      "passed": true,
      "failed_checks": []
    }
  ]
}
```

进程退出码：`0`。

### 运行故意写错的 Synthetic Regression

> ⚠️ 下面这条命令使用的是**合成测试数据**（`synthetic: true`），每条记录都明确标注。它的目的是演示 gate 在候选答案错误时产生非零退出。

```bash
python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials regression-trials.synthetic.jsonl
```

预期输出（节选）：

```json
{
  "case_count": 1,
  "trial_count": 1,
  "passed_trials": 0,
  "failed_trials": 1,
  "gate_passed": false,
  "results": [
    {
      "case_id": "average-empty-diagnosis",
      "trial_id": "synthetic-wrong-fix",
      "passed": false,
      "failed_checks": ["answer_contains_all"]
    }
  ]
}
```

进程退出码：`1`。

两条命令都能跑通，说明本地环境准备好了。

---

## 夹具文件一览

下载包里有五个核心文件，另附一份 README，职责各自独立：

| 文件 | 职责 |
|---|---|
| `eval_gate.py` | Gate 主逻辑：读 case、读 trial、逐项检查、输出 JSON 报告 |
| `test_eval_gate.py` | 20 个单元测试，覆盖通过路径、失败路径和非法输入 |
| `eval-cases.example.jsonl` | Case 定义：期望 outcome + 策略上限 |
| `baseline-trials.example.jsonl` | 归一自真实 Trace 的 trial record（1 条） |
| `regression-trials.synthetic.jsonl` | 合成的错误答案 trial，用于演示失败路径（`synthetic: true`） |

---

## Case 定义长什么样

一条 case 包含两类字段：**outcome 要求**和**策略上限**。

```jsonc
{
  "case_id": "average-empty-diagnosis",
  "task": "Diagnose why average([]) violates the focused test without modifying files.",
  "expect": {
    "turn_status": "completed",
    "answer_contains_all": [
      "ZeroDivisionError",
      "ValueError(\"at least one value\")"
    ],
    "max_tool_calls": 5,
    "max_failed_tool_calls": 2,
    "modified_files": []
  }
}
```

几个设计选择值得说明：

**`answer_contains_all`** 是 substring 检查，不是语义评分。它足够验证"Agent 说出了关键词"，但不足以替代生产环境的语义质量判断。我在这里用它，是因为它确定性强、可回放、不依赖模型调用——这对一个教学 gate 来说优先级更高。

**`max_tool_calls` 和 `max_failed_tool_calls`** 是这个教学 case 的本地策略上限，不是行业标准。它们的意义是"如果 Agent 超出这个预算，本 case 认为路径有问题"——这是一个有意识的工程决定，不是从一次真实 trial 自动推导出来的。

**`modified_files`** 设为空列表，表示这是只读诊断任务，Agent 不应该修改任何源码文件。如果 trial 里出现了意外的文件修改，gate 会判为失败。

两个上限字段（`max_tool_calls`、`max_failed_tool_calls`）都必须是非负整数。Gate 还会在评分前校验状态、答案、必含片段与修改文件列表的类型。对于 trial，`failed_tool_calls` 还不能大于 `tool_calls`，否则 gate 会把输入视为无效记录。

---

## Trial Record 长什么样

一条 trial record 是对一次 Agent 运行的标准化快照：

```jsonc
{
  "trial_id": "codex-diagnosis-20260723",
  "case_id": "average-empty-diagnosis",
  "turn_status": "completed",
  "answer": "average([]) divides by zero and raises ZeroDivisionError; the smallest fix is an empty-input guard that raises ValueError(\"at least one value\") before division.",
  "tool_calls": 5,
  "failed_tool_calls": 2,
  "modified_files": [],
  "synthetic": false,
  "source": "preserved Codex CLI 0.145.0 event stream from 2026-07-23"
}
```

`synthetic: false` 表示这条记录归一自真实的 Agent 运行，不是为演示目的构造的。

对应的合成 regression trial：

```jsonc
{
  "trial_id": "synthetic-wrong-fix",
  "case_id": "average-empty-diagnosis",
  "turn_status": "completed",
  "answer": "Return 0 when the list is empty.",
  "tool_calls": 3,
  "failed_tool_calls": 0,
  "modified_files": [],
  "synthetic": true,
  "source": "synthetic regression used to exercise the failing gate"
}
```

`synthetic: true` 明确标注这条记录是合成测试数据。它的 answer 提议对空列表返回 `0`，缺少 case 要求的 `ZeroDivisionError` 和 `ValueError("at least one value")` 两个证据片段，会触发 `answer_contains_all` 检查失败。

---

## Trace → Trial 的 Adapter 边界

真实的 Codex CLI 事件流不是 trial record。保存的 JSONL 包含工具调用事件、状态，以及命令执行记录里捕获到的输出。把它归一成一条 trial record，需要一个 adapter 层做字段映射。

这个 adapter 层应该做的事：

- 从事件流里找最终的 turn status（`completed` / `error` / `cancelled`）
- 统计工具调用总数和失败次数
- 提取最终的 answer 文本
- 记录运行中实际写入的文件列表
- 写入来源标记（agent 版本、运行时间、事件流文件路径）

这个 adapter 层**不应该做**的事：

- 补写 Trace 里缺失的字段（不能编造 Agent 没有产生的观测）
- 从一次 trial 推导通过率、pass@k 或速度成本
- 把历史路径的具体步骤序列写进 case 定义

夹具里的 `baseline-trials.example.jsonl` 就是这个 adapter 产出的标准形态：它归一自 2026-07-23 保存的 Codex CLI 0.145.0 事件流，包含 5 次工具调用、2 次失败工具调用，最终 turn 为 `completed`，answer 覆盖了 `ZeroDivisionError` 和 `ValueError` 两个关键词。只读任务没有修改源码文件。

---

## Gate 的每个确定性检查

`eval_gate.py` 对每条 trial 执行以下检查，全部通过才算该 trial 通过：

### 1. `turn_status`

比较 `trial.turn_status` 和 `case.expect.turn_status`。严格字符串相等。

这是最基础的 outcome 检查：如果 Agent 没有完成任务（`error`、`cancelled` 或意外终止），后续所有检查都没有意义。

### 2. `answer_contains_all`

遍历 `case.expect.answer_contains_all` 里的每个证据片段，检查它是否出现在 trial 的 answer 文本里（子串检查）。任意一个片段缺失，检查失败，报告 `answer_contains_all`。

再次强调：这是教学 gate 的简化实现。它验证关键词存在，不验证语义正确性。

### 3. `max_tool_calls`

`trial.tool_calls <= case.expect.max_tool_calls`。超出上限报告 `max_tool_calls`。

### 4. `max_failed_tool_calls`

`trial.failed_tool_calls <= case.expect.max_failed_tool_calls`。

### 5. `modified_files`

`trial.modified_files` 必须与 `case.expect.modified_files` 列表完全一致。不同就报告 `modified_files`。

---

## 机器可读报告与退出码

Gate 的输出是标准 JSON，打印到 stdout：

```json
{
  "case_count": 1,
  "trial_count": 1,
  "passed_trials": 1,
  "failed_trials": 0,
  "gate_passed": true,
  "results": [...]
}
```

每条 result 里的 `failed_checks` 是一个字符串列表，列出所有未通过的检查名称。全部通过时为空列表。这个格式让下游脚本可以用 `jq` 或任何 JSON 解析器提取失败原因，不需要解析人类可读文本。

进程退出码有三种语义：

| 退出码 | 含义 |
|---|---|
| `0` | 所有 trial 通过，`gate_passed: true` |
| `1` | 评测完成，但有 trial 未通过，`gate_passed: false` |
| `2` | 输入非法，评测未执行，错误信息以 JSON 格式打印到 stderr |

退出码 `2` 专门给无效输入：非法 JSON、`NaN`/`Infinity` 等非标准常量、重复的 case ID、未知的 case 引用、空 case 集或空 trial 集、没有任何 trial 对应的 case，以及评分字段类型错误。

退出码 `1` 和 `2` 的区分很重要：`1` 表示"评测跑完了，结论是不通过"；`2` 表示"评测根本没法跑，输入有问题"。CI 脚本可以分别处理这两种情况。

非标准 JSON 常量（`NaN`、`Infinity`、`-Infinity`）在标准 JSON 里不合法。即使这些字段不参与评分，gate 也会拒绝并返回退出码 `2`。

非法 JSON 错误会报告来源文件、行号和列号，方便快速定位。

---

## 展示保存的真实 Baseline 通过

来源：2026-07-23 保存的 Codex CLI 0.145.0 事件流。

这次诊断任务的上下文：给定一段 Python 代码，Agent 需要找出运行时错误的根因。真实运行产生了 5 次工具调用，其中 2 次失败：`python` 命令不存在并退出 `127`，随后 `python3` 运行聚焦测试并退出 `1`，暴露了 `ZeroDivisionError`。最终 turn 状态为 `completed`，answer 里明确指出了 `ZeroDivisionError` 和 `ValueError("at least one value")` guard。因为是只读诊断，没有修改任何文件。

把这次运行归一成一条 trial record，用上面的 baseline 命令跑 gate，结果是退出码 `0`，`gate_passed: true`，`failed_checks` 为空。

**这只代表一次 trial。** 不能从这个结果推导通过率或 pass@k。Agent 有波动，一次成功说明这条路径可行，不说明下一次也一定可行。Anthropic 的工程实践里明确建议用多个 trial 处理 Agent 波动——这是扩充路径里的内容，后面会提到。

---

## 展示 Synthetic Regression 失败

> ⚠️ 本节使用的是**合成测试数据**，`synthetic: true`，为教学目的构造，不代表任何真实 Agent 运行。

Synthetic regression trial 的 answer 是 `"Return 0 when the list is empty."`。这个 answer 的 turn status 正确（`completed`），工具调用在预算内（3 次，0 次失败），没有修改文件——但它缺少 case 要求的两个证据片段。

`answer_contains_all` 检查失败，gate 输出 `gate_passed: false`，进程退出码 `1`。

退出码 `1` 就是 CI 的接口信号。任何检查非零退出的 CI 步骤都会在这里停下来，阻止这次变更合入。这是设计意图：**gate 失败等于变更被阻止，不需要人工去读日志**。

---

## Outcome-First，而不是轨迹重演

Anthropic 在 Agent Eval 工程实践里有一条明确警告：过度严格地检查 trajectory 会惩罚 Eval 作者没有预料到的有效路径。

这个 gate 的设计选择体现了这个原则：

**Case 定义要求**：
- turn 状态是什么（outcome）
- answer 包含哪些证据（outcome）
- 工具调用不超过多少次（资源策略上限）
- 失败工具调用不超过多少次（质量上限）
- 修改了哪些文件（安全边界）

**Case 定义不要求**：
- 第几步调用哪个工具
- 工具调用的具体参数
- 中间状态的顺序

20 个测试里有一个专门验证这一点：如果候选 Agent 用更干净的路径（3 次工具调用、0 次失败）得到了同样正确的 answer 和 turn status，它仍然通过。历史 Trace 里用了 5 次工具，但 gate 不要求复刻失败过程；当前 case 将 5 次设为本地上限。

同样，gate 不要求退出码 `127`、也不要求复刻 `python` → `python3` 这样的命令顺序。这些是历史轨迹的细节，不是 outcome 的一部分。

**一条历史轨迹是 Eval 的来源证据，不是 Eval 的评分标准。** 混淆这两者，会让你的 Eval 在 Agent 版本升级或换了沙箱环境后立刻变脆。

---

## 20 个测试覆盖了什么

当前 20 个测试覆盖以下场景：

**通过路径**
- 真实 baseline trial 通过
- 更干净路径（3 次工具、0 次失败）通过

**失败路径**
- Synthetic wrong fix：`answer_contains_all` 失败
- 超出 tool budget：`max_tool_calls` 失败
- turn status 不对：`turn_status` 失败
- failed-tool budget 超限：`max_failed_tool_calls` 失败
- 意外修改文件：`modified_files` 失败

**CLI 退出码**
- 通过时退出 `0`
- 失败时退出 `1`
- 无效输入退出 `2`，并向 stderr 输出 JSON 错误

**输入验证**
- 重复 case ID 拒绝（退出 `2`）
- 重复 trial ID 拒绝（退出 `2`）
- 未知 case 引用拒绝（退出 `2`）
- 空 case set 拒绝（退出 `2`）
- 空 trial set 拒绝（退出 `2`）
- 没有任何 trial 的 case 拒绝（退出 `2`）
- 工具计数非负整数校验（负数拒绝，退出 `2`）
- 不可能的 failed-tool 计数拒绝（`failed > total`，退出 `2`）
- 非标准 JSON 常量拒绝（`NaN`/`Infinity`，退出 `2`）
- 非法 JSON 报告来源文件、行和列

这个测试覆盖面的设计意图：**gate 本身是信任链的一部分**，它的输入验证必须和它的评分逻辑一样严格。一个接受 `NaN` 作为工具计数的 gate，不值得信任。

---

## 最小 CI 集成示例

把两条已验证命令放进 CI，退出码处理就够了。

### Shell 示例

```bash
#!/bin/bash
set -euo pipefail

echo "=== Running eval gate ==="

python3 eval_gate.py \
  --cases eval-cases.example.jsonl \
  --trials baseline-trials.example.jsonl

# 如果 gate 非零退出，set -e 会在此处阻止后续步骤
echo "Gate passed. Proceeding with merge."
```

### GitHub Actions YAML 示例

```yaml
name: Eval Gate

on:
  pull_request:
    branches: [main]

jobs:
  eval-gate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: "3.12"

      - name: Run unit tests
        run: python3 -m unittest -v test_eval_gate.py

      - name: Run eval gate (baseline)
        run: |
          python3 eval_gate.py \
            --cases eval-cases.example.jsonl \
            --trials baseline-trials.example.jsonl
        # 退出码 1 时此步骤失败，PR 被阻止
        # 退出码 2 时此步骤也失败，报告输入问题
```

没有额外的脚本。退出码是 CI 的唯一接口——这是设计意图，不是简化。

---

## 扩充路径

以上是最小可用的 gate。下面按优先级列出扩充方向：

### 1. 积累真实失败案例

每次 Agent 在生产环境产生错误答案，就用那条 Trace 新建或收紧一个 case 合同，再让未来的候选 trial 对这个 case 运行。原始失败应作为负向证据保存，并用于断言 gate 会退出 `1`；不要把它放进要求所有 trial 通过的合并门禁，让 CI 永久变红。随着真实失败案例增加，你的数据集的代表性会远超合成数据。

### 2. 添加正反 Case

目前只有一个 case。加入负面 case（Agent 不应该做的事情）能让 gate 更完整：例如"不应该修改源码文件"、"不应该在 answer 里输出凭证"。

### 3. 隔离沙箱环境

如果你在 CI 里实际运行 Agent（而不是重放已有 trial），需要隔离的执行环境。文件系统写入、网络访问、命令执行都需要有明确边界，否则 trial 的 `modified_files` 字段就没有可信度。

### 4. 多次 Trial 处理 Agent 波动

Agent 有随机性。一次 trial 通过不代表每次都通过。Anthropic 的建议是对同一个 case 运行多次 trial，用通过率而不是单次结果做判断。具体多少次 trial 才有统计意义，取决于你的 case 复杂度和可接受的假阳性率。

### 5. 引入经过人工校准的 Model Grader

当 substring 检查不够用的时候（例如需要判断答案的语义正确性、推理链合理性），才考虑引入 model grader。

引入 model grader 之前，需要先有一个人工标注的黄金答案集，用它校准 model grader 的判断——如果 grader 和人工判断的一致率不够高，grader 的结论不可信。

这一步放在最后，是因为它的成本最高：需要人工标注时间、需要校准实验、需要定期重新校准（模型更新后 grader 行为也会变）。在早期阶段，确定性检查往往能覆盖大多数有价值的断言。

---

## 小结

这篇教程走完了从 Trace 到 Gate 的完整路径：

1. 上一篇保存的真实事件流，经过 adapter 层归一成 trial record
2. Case 定义分离了 outcome 要求和策略上限，不绑定历史轨迹细节
3. Gate 执行确定性检查，输出机器可读 JSON，用退出码做 CI 接口
4. 20 个测试覆盖通过路径、失败路径和当前实现的重要输入边界
5. 退出码 `0` / `1` / `2` 三种语义让下游 CI 可以精确处理不同情况

下载夹具，把它接进你自己的 CI，把你保存的第一条 Trace 归一进去，看看它通过还是失败——那是比读这篇教程更有价值的一步。

---

*夹具下载：<a href="/examples/coding-agent-eval-gate.zip">/examples/coding-agent-eval-gate.zip</a>*
*夹具依赖：Python 标准库，无第三方依赖*
*验证环境：Python 3.12；baseline 来源为 Codex CLI 0.145.0 的保存事件流*
