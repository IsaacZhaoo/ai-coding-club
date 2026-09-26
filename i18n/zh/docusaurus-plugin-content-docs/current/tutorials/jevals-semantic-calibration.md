---
title: "为 Agent 工具调用设阈值：用 jevals + 人工标注把“看得到”变成“看得准”"
description: "用 jevals 和本地 Kev 检查 Agent 是否利用工具结果，添加人工标签、读懂校准指标，再选定阈值并在留出记录上复查。"
keywords:
  - "jevals 教程"
  - "UsedToolResult"
  - "Agent 评估"
  - "语义评估阈值"
  - "人工标注校准"
sidebar_position: 34
tags: [tutorial, agent-engineering, evals]
---

# 为 Agent 工具调用设阈值：用 jevals + 人工标注把“看得到”变成“看得准”

如果你已经有 Agent 的对话记录，也跑着本地 Kev 服务（`http://localhost:8009`），但还在犹豫“工具调用结果到底有没有被真正用到”，这篇文章会给你一套可落地的方法：用 jevals 跑一次语义评估、对照人工标注选出合适的通过阈值，并在新的数据上复查效果。

## 一、为什么光靠字符串检查不够

大多数 Agent 的监控只停留在：

- 是否调用了工具？
- 工具响应非空否？
- 日志里有没有错误关键字？

这当然重要，但还有一个更关键的问题：Agent 听完工具回答后，有没有“听懂”，有没有忽略、有没有自相矛盾。

例如一条天气查询记录：

- 工具返回：“San Francisco, today: sunny, high 68F, low 54F, wind 12 mph from the west.”
- Agent 最终回答：引用了当天旧金山晴天、最高68°F最低54°F，还额外说了“整周都会晴”（对应英文原意的 all week 指整周）。

系统通过UsedToolResult校验步骤，评估模型回答是否正确引用工具返回信息，并识别是否存在遗漏或矛盾情况。

Grounded 评估器逐句判断最终回答的各个断言是否得到工具返回内容的支持。

## 二、准备：项目与依赖

我们基于 openlayer-ai/jevals 的已发布版本 0.1.4（Python 3.10+）：

```bash
python -m pip install jevals==0.1.4
```

你的环境里已经有一台本地 Kev 服务在 `http://localhost:8009`。在本教程中，我们显式指定后端为 `kev://localhost:8009`，避免被环境变量里的 API 密钥牵走。

> 注：本站 Kev 本地模型安装与配置参考：https://aicoding.club/zh/docs/tutorials/kev-local-decision-model/

## 三、核心评估器：UsedToolResult 是什么

jevals 里有一个专门针对“工具信息是否被有效利用”的评估器：`UsedToolResult`。它的核心思想是：

- 从对话轨迹中，把工具调用的结果（tool message）和最终 assistant 回答关联起来；
- 判断最终回答是否真正利用了这些结果，而不是“假装用了一下”或“自说自话”。

它的评分逻辑（内部由 Jev 风格决策后端完成）会给出：

- **score** = `p` (UsedToolResult 字段)  
- **probability** = `p` (命题“最终回答利用了工具返回的信息”成立)  
- **passed** = `true`（若 p ≥ 0.5）或 `false`（若 p < 0.5，默认 threshold=0.5）

关键代码行：

```python
from jevals.agent import UsedToolResult
```

UsedToolResult.applicable 方法会检查 messages 和 tool_results 是否存在，若缺少必要的消息或工具结果则直接跳过评估。但这并非对轨迹格式或调用配对的完整验证，因此错误配对并不一定能被自动识别。

源码参考：

- 评估器逻辑：https://github.com/openlayer-ai/jevals/blob/main/src/jevals/agent/_evals.py
- 通用评估框架：https://github.com/openlayer-ai/jevals/blob/main/src/jevals/_eval.py

## 四、一个完整示例轨迹

示例出处：https://github.com/openlayer-ai/jevals/blob/main/examples/quickstart.py

下面是一个可直接用于评估的对话记录（保存为 `trace.json`）：

```json
{
  "tools": [
    {
      "type": "function",
      "function": {
        "name": "search",
        "description": "Web search for live information",
        "parameters": {
          "type": "object",
          "properties": {
            "q": {
              "type": "string"
            }
          }
        }
      }
    }
  ],
  "messages": [
    {
      "role": "system",
      "content": "You are a weather assistant."
    },
    {
      "role": "user",
      "content": "What's the weather in San Francisco today?"
    },
    {
      "role": "assistant",
      "content": null,
      "tool_calls": [
        {
          "id": "c1",
          "type": "function",
          "function": {
            "name": "search",
            "arguments": "{\"q\": \"San Francisco weather today\"}"
          }
        }
      ]
    },
    {
      "role": "tool",
      "tool_call_id": "c1",
      "content": "San Francisco, today: sunny, high 68F, low 54F, wind 12 mph from the west."
    },
    {
      "role": "assistant",
      "content": "It's sunny in San Francisco today with a high of 68F and a low of 54F. Winds are light from the west, and it will stay sunny all week."
    }
  ]
}
```

这条记录里：

- 有一个工具调用（c1）；
- 有一个清晰的 tool message；
- Assistant 在回答中重述了部分信息，并额外加上了“all week”。

接下来我们用 jevals 跑一次评估。

## 五、用本地 Kev 跑一次自动评分

全局配置 `--backend` 放在子命令之前：

```bash
jevals --backend kev://localhost:8009 check trace.json \
  --evals agent.used_tool_result \
  --json
```

检查报告路径为 `results.used_tool_result`。请首先确认当前记录的分数字段（score）非空、状态标记 skipped 为 false、错误字段 error 为 null，之后再读取 passed 值。若该结果包含有效分数且 passed 为 false，check 将退出码 1；而 skipped 或 error 存在的记录也可能导致 check 退出码 0，因此不能仅凭退出码 0 就认定评分成功。

> 注：CLI 实现参考：https://github.com/openlayer-ai/jevals/blob/main/src/jevals/cli.py

## 六、人工标注：准备 labeled.jsonl

自动评分只是起点，真正的“阈值校准”需要人工判断作为参照系。

你需要准备一个 JSONL 文件（例如 `labeled.jsonl`），每一条是一行完整的轨迹对象，并在顶层增加一个字段：

- `human_used_tool`：true/false，表示你认为该轨迹中，“Agent 确实有效利用了工具返回的信息”。

```python
import json
from pathlib import Path

sample = json.loads(Path("trace.json").read_text(encoding="utf-8"))
sample["human_used_tool"] = True  # 或 False，由你按该条记录判定
with open("labeled.jsonl", "a", encoding="utf-8") as f:
    f.write(json.dumps(sample, ensure_ascii=False) + "\n")
```

- 使用真实保存的不同业务 trace（trace.json）逐条处理；
- 每次读取一条完整的轨迹，设置其 `human_used_tool` 后追加写入 JSONL；
- 不要对同一条记录重复写入当成新样本；每条记录的布尔值由读者根据上面口径人工决定。

标注员需阅读保存的Agent完整轨迹，并在最外层添加human_used_tool布尔字段：若最终回答利用了工具信息且未与其矛盾则填true，反之则填false。

标注样例设计建议包含：

- 正确改述：把工具数字换成人话；
- 忽略工具：工具给了数据，回答里没影儿；
- 与工具矛盾：温度、时间、地点写错或自相矛盾；

另外，**务必留出一些不同的轨迹**用于后续阈值选定后的复查。

## 七、校准：让 jevals 告诉你不同阈值下的表现

有了人工标注，就可以做“校准”。jevals 提供了一个 `calibrate` 命令，专门做这件事：

```bash
jevals --backend kev://localhost:8009 \
  calibrate labeled.jsonl \
  --eval agent.used_tool_result \
  --label human_used_tool
```

Jevals calibrate读取 labeled.jsonl 的完整轨迹和人工标签，构建评估样本集。移除 human_used_tool 字段后启动 Kev 评分，确保其无法看到人工标注以避免偏差。Jevals 将评分结果与人工标签对比并输出阈值表，整个过程仅用于分析而不更新评估器配置或训练模型。

| 列名 | 计算 | 含义 |
|---|---|---|
| auto-pass | (TP+FP)/N | 全部有效样本中被判通过的比例。 |
| wrong passes | FP/N | 全部有效样本中被错误判通过的比例。 |
| missed passes | FN/N | 全部有效样本中被错误判不通过的比例。 |

N为有效标注结果总数，TP是正确通过数，FP是错误通过数，FN是错误拒绝数。

jevals calibrate默认扫描0.50、0.55、0.60、0.65、0.70、0.75、0.80、0.85、0.90、0.95这些阈值。

Brier分数、预期校准误差（ECE）及AUROC均为整批评分指标，不随单行阈值变化而改变；当仅存一个标签类别时，AUROC不予显示。统计前会剔除缺失标签、标记为skipped、error或无score的记录。

Wrong passes（FP/N）衡量的是错误通过占所有有效标注结果的比率，而FP/(TP+FP)则衡量的是在系统判定为通过的结果中，错误通过的占比。

当同一批有效评分保持不变时，提高判定阈值将产生以下效果：auto-pass 不会增加；wrong passes（误放）不会增加；missed passes（误拒）不会减少。各项指标的变化也可能为零。因此，阈值的设定应综合权衡误放与误拒的实际业务代价。

## 八、选定阈值后：在真实数据上复查

假设你根据任务特点决定采用 `threshold=0.80`。这只是一个参考点，必须在你自己的数据上验证。

### 1）用 Python 显式配置阈值

```python
import json
from pathlib import Path
from jevals import evaluate
from jevals.agent import UsedToolResult

sample = json.loads(Path("trace.json").read_text(encoding="utf-8"))
report = evaluate(
    sample,
    [UsedToolResult(threshold=0.80)],
    backend="kev://localhost:8009"
)
print(report.used_tool_result.score, report.used_tool_result.passed)
```

- 如果你希望更严格：把 `threshold` 调高；
- 如果你担心误杀太多“真正用了工具”的记录：先降低阈值，用校准表里的 FP/FN 比例辅助决策。

### 2）在复查集上跑一轮对比

对另一批未参与阈值校准的轨迹（例如 `review.jsonl`），使用上述选定好的 0.80 阈值，以公开API评估多行数据：

```python
from jevals import evaluate_dataset
from jevals.agent import UsedToolResult

report = evaluate_dataset(
    "review.jsonl",
    [UsedToolResult(threshold=0.80)],
    backend="kev://localhost:8009",
)
report.write_jsonl("review-results.jsonl")
```

`review-results.jsonl` 文件中每行的 `index` 对应输入记录的顺序，各项评分与处理状态均位于 `results.used_tool_result` 对象内，请将有效评分与留出记录的人工判断进行对照，以核查是否存在误放或误拒。

人工抽检几条“passed=true”和“passed=false”的样本：

- 若发现大量“显然用了工具却被判 false”：说明阈值偏高或模型对某些表达方式不敏感；
- 若发现大量“没怎么用到工具却被判 true”：说明阈值偏低或模型对泛化语句过于宽容。

## 九、常见坑与检查清单

- **别把 skipped / error 当成分数**：在分析时先过滤掉 skipped=True 或 error 不为空的条目；它们不代表“坏样本”，只表示不适用或未知。
- **校准命令里要统一后端**：不同后端（或不同模型配置）可能给出不同的 score，务必在校准和上线评估时使用同一套 `backend`。
- **阈值是业务决策，不是统计最优**：如果你的业务更怕漏掉“真正用了工具”的样本，宁可多放一点（阈值低些）；如果更怕把“瞎凑答案”的当合格，就提高阈值。
- **人工标注口径要稳定**：如果以后更换标注人，最好给出一个简单的判断指南，并抽样复核一致率。
- **不要一劳永逸**：Agent 提示词、工具结构变化后，建议用同样的流程重新跑一轮校准。

## 十、总结：你读完能完成什么

读完这篇教程，你应该能够：

1. 用 `UsedToolResult` 评估完整的工具调用轨迹；
2. 整理一份带 `human_used_tool` 人工标签的 JSONL；
3. 读懂校准表，理解不同阈值下的误放/漏放比例与 AUROC；
4. 显式配置选定阈值（例如 `threshold=0.80`）并在新的记录上复查；
5. 形成一套可在离线评估中复用的配置方案。

工具调用的“看得到”不等于“看得准”。用 jevals + 人工标注，把语义层的判断变成可衡量、可重复的阈值，才是一步步靠近可靠 Agent 的正确姿势。

## 延伸阅读

- [在本地运行 Kev：用一个 Choice 请求给客服工单分类](/zh/docs/tutorials/kev-local-decision-model/)
- [Coding Agent Evals 教程：把 Trace 变成数据集和质量门禁](/zh/docs/tutorials/coding-agent-evals-guide/)
