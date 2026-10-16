---
title: "分层审查与合并：当计价逻辑变了，Checkout 却还在传 0.2"
sidebar_label: "Agent 依赖改动与分层审查"
description: "通过 Git 与 Python 本地练习，分层审查相互依赖的 Agent 改动，复现无冲突 rebase 后的语义错误，并重建 squash 合并后的审查基线。"
keywords: ["stacked PR", "Agent 协作", "代码审查", "git rebase", "squash 合并"]
sidebar_position: 49
tags: ["tutorial", "coding-assistant", "agent-engineering", "git"]
---

# 分层审查与合并：当计价逻辑变了，Checkout 却还在传 0.2

如果你正用多个编程 Agent 同时修改一个项目，很快就会遇到这类场景：

- A 层（比如计价逻辑）是待合并的依赖层；
- B 层（比如结账消费者）在另一条分支上被审查并依赖 A；
- 某天上游语义变了（比如折扣从“比例”变成“百分数”），B 层却还在用旧约定调用；
- 你把 B 层重放到新的 A 基线上，“无冲突 rebase”，运行测试才发现：行为全错了。

本文通过一个可复现的 Git + Python 例子，带你看清：

- 两层功能各自的 `base` / `head` 到底指什么；
- 为什么“patch 没变、rebase 无冲突”不等于“语义正确”；
- 如何在 squash 合并后，仍然保持一个清晰、可审查的下游比较范围。

示例仓库只需 Git 与 Python 3，本地即可操作，无需联网或 GitHub 账号。

---

## 一、场景：两层相互依赖的功能

想象一个最小项目：

- `pricing.py`：负责折扣计算；
- `test_pricing.py`：针对它的单元测试；
- `checkout.py`：消费计价结果，完成最终金额；
- `test_checkout.py`：针对 checkout 的测试。

main 仅提交.gitignore；创建 feature/pricing 后提交 pricing.py 与 test_pricing.py；打 lab/parent-v1；从 A（feature/pricing）创建 feature/checkout 后提交 checkout.py 与 test_checkout.py。

1. **A 层：`feature/pricing`**
   - 修改计价逻辑；
   - 审查结论是“折扣从比例改为百分数”。

2. **B 层：`feature/checkout`**
   - 基于 A 层，增加消费者；
   - 审查结论是“结账流程能正常返回预期金额”。

关键约束：

- B 层在审查时，A 层本身也处于“待合并”状态（stacked feature）；
- A 层语义改变后，B 层即使没有代码改动，行为也会错；
- 我们要学会：只审每层自己的变化，但必须在新基线上核验组合行为。

---

## 二、初始化仓库与分支结构（你可以直接执行）

以下命令在干净目录执行，会生成一个可复现的练习仓库。

```bash
mkdir git-layer-demo && cd git-layer-demo
git init -b main

# 设置本地 Git 信息（仅用于本次练习）
git config user.name "Lab Agent"
git config user.email "lab@example.com"

printf "__pycache__/\n" > .gitignore
git add .gitignore
git commit -m "Initial main checkpoint"
git switch -c feature/pricing
```

### 1. 修改 A 层代码

创建 `pricing.py` 和 `test_pricing.py`：

```bash
cat > pricing.py << 'EOF'
def discounted_total(subtotal, discount):
    if not 0 <= discount <= 1:
        raise ValueError('discount out of range')
    return round(subtotal * (1 - discount), 2)
EOF

cat > test_pricing.py << 'EOF'
import unittest
from pricing import discounted_total

class PricingTests(unittest.TestCase):
    def test_twenty_percent(self):
        self.assertEqual(discounted_total(100, 0.2), 80)
    def test_no_discount(self):
        self.assertEqual(discounted_total(100, 0), 100)
    def test_full_discount(self):
        self.assertEqual(discounted_total(100, 1), 0)
    def test_invalid_discount(self):
        for value in (-1, 1.1):
            with self.subTest(value=value), self.assertRaises(ValueError):
                discounted_total(100, value)
EOF

git add pricing.py test_pricing.py
git commit -m "Initial: basic pricing logic"
```

创建 `checkout.py` 和 `test_checkout.py`：

```bash
git tag lab/parent-v1 feature/pricing
git switch -c feature/checkout

cat > checkout.py << 'EOF'
from pricing import discounted_total

def checkout_total(subtotal):
    return discounted_total(subtotal, 0.2)
EOF

cat > test_checkout.py << 'EOF'
import unittest
from checkout import checkout_total

class CheckoutTests(unittest.TestCase):
    def test_twenty_percent_checkout(self):
        self.assertEqual(checkout_total(100), 80)
    def test_zero_subtotal(self):
        self.assertEqual(checkout_total(0), 0)
EOF

git add checkout.py test_checkout.py
git commit -m "Add checkout consumer (hardcoded 20% discount)"
```

运行全部测试（六个）：

```bash
python3 -m unittest discover -v
```

### 2. 建立两层分支，并打上“检查点”标签

main 仅提交.gitignore；创建 feature/pricing 后提交 pricing.py 与 test_pricing.py；打 lab/parent-v1；从 A（feature/pricing）创建 feature/checkout 后提交 checkout.py 与 test_checkout.py。

```bash
git diff --name-only feature/pricing...feature/checkout
# checkout.py, test_checkout.py
git diff --name-only main...feature/checkout
# checkout.py, pricing.py, test_checkout.py, test_pricing.py
```

---

## 三、A 层审查：从“比例折扣”变成“百分数折扣”

现在你是 A 层的编程 Agent。你发现业务规则变化：

- 折扣不再传入 0.2 这样的比例；
- 而是传入 20（代表 20%）；
- 范围上限从 1 变为 100；
- 计算方式同步更新。

你的目标：**只改计价逻辑层，不碰 consumer**。

### 1. 修改 A 层代码

编辑 `pricing.py`：先切换到对应分支，再修改文件：

```bash
git switch feature/pricing
# 现在可以编辑 `pricing.py`
```

```python
def discounted_total(subtotal, discount):
    if not 0 <= discount <= 100:
        raise ValueError('discount out of range')
    return round(subtotal * (1 - discount / 100), 2)
```

编辑 `test_pricing.py`，适配新约定（金额仍应为 80）：

```python
import unittest
from pricing import discounted_total

class PricingTests(unittest.TestCase):
    def test_twenty_percent(self):
        # 20% -> discount=20, 100*(1-20/100)=80
        self.assertEqual(discounted_total(100, 20), 80)
    def test_no_discount(self):
        self.assertEqual(discounted_total(100, 0), 100)
    def test_full_discount(self):
        # 100% -> discount=100
        self.assertEqual(discounted_total(100, 100), 0)
    def test_invalid_discount(self):
        for value in (-1, 101):
            with self.subTest(value=value), self.assertRaises(ValueError):
                discounted_total(100, value)
```

提交 A 层改动，并打上“语义变更”的标签：

```bash
git add pricing.py test_pricing.py
git commit -m "A: change discount API from ratio to percentage"
git tag lab/parent-v2 feature/pricing
```

单独运行 A 层测试（四个）：

```bash
python3 -m unittest discover -v --pattern="test_pricing.py"
```

预期：全部通过。

### 2. 观察 B 层的“无冲突”陷阱

现在回到 `feature/checkout`，执行重放：

```bash
git checkout feature/checkout
git rebase --onto feature/pricing lab/parent-v1
```

说明一下 Git 语义（防止术语混淆）：

- `lab/parent-v1` 是 A 层在“改动前”的稳定锚点；
- `feature/pricing` 是当前的上游 HEAD；
- `--onto ...` 把 B 层的提交重新放到新的 base 上；
- 此例中没有文本冲突，所以 rebase 看起来“很完美”。

此时运行全部测试：

```bash
python3 -m unittest discover -v
```

你很可能看到类似：

```text
AssertionError: 99.8 != 80
```

**关键现象：**

- `checkout_total(100)` 仍传 0.2 给计价函数；
- 计价函数现在把 0.2 理解为“百分之零点二”，所以只扣了 0.2%：
  - 100 * (1 - 0.2 / 100) = 99.8；
- B 层的代码本身没变，但上游约定变了，语义就错位了。

这就是本文的核心结论之一：

> patch 没变、rebase 无冲突 ≠ 行为正确。  
> 输入单位、API 契约、默认值等“上游约定”变了，下游即使零改动也会错。

---

## 四、修复 B 层消费者：最小改动 + 新基线证据

现在你是 B 层的编程 Agent。你的任务：

- 在已经 rebase 到新版 A 的 `feature/checkout` 上；
- 只修消费者调用，使其在新约定下仍返回 80；
- 留下清晰的审查边界（base / head）。

### 1. 最小修复 checkout.py

```bash
# 在 feature/checkout 分支上
sed -i 's/discounted_total(subtotal, 0.2)/discounted_total(subtotal, 20)/' checkout.py
git add checkout.py
git commit -m "B: adapt consumer to new percentage-based discount"
```

再次运行全部测试：

```bash
python3 -m unittest discover -v
```

预期：六个测试全部通过。

### 2. 理解 base / head 的关系（审查范围）

在修复后的 `feature/checkout` 上，你可以这样理解审查范围：

- A 层审查
  - base: main, head: feature/pricing
  - 变更文件：pricing.py, test_pricing.py（共两份）
  - lab/parent-v1 → lab/parent-v2 仅用于 A 内部单位修订比对，不是整个 A 功能层的 PR 范围。

- **B 层审查**：
  - base：`feature/pricing`（当前 A 层 HEAD，已包含百分数约定）；
  - head：`HEAD`（修复后的 checkout）；
  - 文件范围：`checkout.py`, `test_checkout.py`。

用 Git 命令直观查看（以修复后为例）：

```bash
git diff --name-only feature/pricing...feature/checkout
```

在本地 Git 中，`A...B` 表示从 A 与 B 的 merge-base 到 B 的变化。这里你会看到：

- 只列出 `checkout.py`, `test_checkout.py`；
- 这正对应“本层自己的变化”。

而对比到初始线：

```bash
git diff --name-only main...feature/checkout
```

则会包含四份文件（pricing + checkout），这是因为合并基线 `main` 早于 A、B 所有改动。这个输出**不能**用来定义 B 层的审查范围，它只是“从最初到当前”的全量差异。

---

## 五、底层 squash：如何保持清晰的下游比较范围？

很多团队喜欢用 `git merge --squash` 把一堆提交压成一个，以简化历史。问题在于：

- 如果基线没对齐，`git diff main...feature/checkout` 看起来像“多了很多文件”；
- 容易误以为 A 层被“合并消失”了，或 B 层的依赖关系不清晰。

下面演示一个干净的整合路径（完全本地流程）：

### 1. 在 clean main 上做 squash，只保留 A 的语义

```bash
git checkout main
git merge --squash feature/pricing
git commit -m "A: change discount API from ratio to percentage [squashed]"
```

squash 完成后：

```bash
git diff --name-only main feature/checkout
git diff --name-only main...feature/checkout
```

- `git diff main feature/checkout` 比较两树尖端，通常只显示 checkout.py 和 test_checkout.py。
- `git diff main...feature/checkout` 在旧 merge-base 与当前之间展开合并范围，会显示四份业务文件（pricing、test_pricing、checkout、test_checkout）。
- 二者结果同时正确；A 的内容并未丢失，只是 squash 提交没有把 A 的原始记录成合并祖先。
参考：https://git-scm.com/docs/git-diff, https://git-scm.com/docs/git-merge

### 2. 在 feature/checkout 上重放 B 到新的 main

回到修复好的 B 层：

```bash
git checkout feature/checkout
# 可选：为将来需要回退而保留快照
git branch backup/checkout-before-restack
```

现在重放 B 的两个提交（消费者 + 修复）到 squash 后的 main：

```bash
git rebase --onto main lab/parent-v2 feature/checkout
```

解释：

- `lab/parent-v2` 是 A 层语义完成后的锚点；
- `feature/checkout` 当前 HEAD 上已经包含 B 的两步改动；
- `--onto main` 把这两步放到新的 main 之后。

再次运行测试（确保组合行为依然正确）：

```bash
python3 -m unittest discover -v
```

预期：六个测试通过，checkout_total(100) 仍为 80。

### 3. 整合到 main，并验证 diff 范围

在真正快进合并前，先确认 `git diff --name-only main...feature/checkout` 仅包含 checkout 相关两份：

```bash
git diff --name-only main...feature/checkout
git rev-parse main feature/checkout
```

记录好确切的 base/head 后再执行 main 快进合并。

在本地 main 上执行快进合并（仅用于演示完整流程）：

```bash
git checkout main
git merge --ff-only feature/checkout
```

此时：

- `main` 历史包含了 A 的语义提交 + B 的消费者提交；
- `feature/checkout` 可以被删除或保留作归档。

检查比较范围（在本地 main 上）：

```bash
git diff --name-only HEAD...feature/checkout
```

由于已经 ff 合并，main 与 feature/checkout 指向同一提交：`git diff` 为空，证明两分支文件树一致；特定金额行为由刚才六项组合测试支持，空 diff 本身不证明所有真实业务完全正确。

如果你在某一步想回退，请使用 `git rebase --abort`，但它只适用于仍在进行的 rebase（例如遇到冲突后停止）。已完成的 rebase 不能靠它撤销；备份分支 backup/checkout-before-restack 保留了旧提交，完成后的恢复需结合当前未提交工作与分支状态另行处理。参考：https://git-scm.com/docs/git-rebase

**重要经验：**

- 重放前务必保存精确 commit 引用及固定 tag/backup 分支；commit message 与 worktree 本身不能替代稳定旧 parent。
- 每层的审查结论同时依赖于：**本层改动** + **检查时的上游约定**；
- squash 合并不会抹掉语义，但会改变比较基线，因此要在新基线上重新验证行为。

---

## 六、总结：给多层 Agent 协作的几条可操作原则

1. A 整层 base/head 是 main / feature/pricing，B 是当前 A tip/消费者 head（feature/checkout）。lab/parent-v1 → v2 仅用于 A 单位修订检查；用精确 commit 或固定引用记录，不依赖 commit message。

2. **无冲突 rebase ≠ 语义一致**  
   - 当上游 API、单位、默认值变化时，下游即使 patch 完全不变也会错；
   - Agent 材料应包含：parent commit、层头、约定变化、实际失败与重试命令。

3. **审查范围 ≠ Git diff 输出**  
   - `git diff A...B` 用于技术比较；
   - “本层文件 + 本层测试”才是语义边界；
   - 不要拿全量差异去解释跨层依赖。

4. 保留 tag 或 backup 分支，改写前确认拥有该分支的 worktree、暂停其他 Agent 编辑。

5. **组合测试是最终仲裁**  
   - 每层单元测试只是局部验证；
   - 必须在新基线上运行 A + B 的组合测试，确保金额等关键行为仍为预期（如 80）。

---

## 七、下一步：从本地练习到真实工作流

- 若你使用 GitHub 的 stacked PR：官方原生 Stack 要求同仓库，合并从最低未合并层向上连续推进，不能单独取中间层排除下面依赖；参考：https://docs.github.com/en/pull-requests/how-tos/merge-and-close-pull-requests/merging-stacked-pull-requests

- 相关阅读（按需跳转）：
  - worktrees 任务隔离与整合责任：https://aicoding.club/zh/docs/tutorials/parallel-coding-agents-worktrees/
  - AI 代码审查工作流（证据与职责）：https://aicoding.club/zh/docs/tutorials/ai-code-review-workflow/

现在你已经拥有了一套可复现的最小案例，以及清晰的判断框架：在分层 Agent 协作中，语义审查永远比 patch 比对更重要；而 Git 的正确用法，是帮助你把这两者可靠地拼起来，而不是被它的比较输出带偏。