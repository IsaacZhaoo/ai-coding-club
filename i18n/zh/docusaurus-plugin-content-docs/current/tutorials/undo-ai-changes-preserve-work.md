---
title: "在 Git 中精准“撤回”：保留你的手改，筛掉 AI 的错误"
sidebar_label: "撤回 AI 改动，保留自己的工作"
description: "通过可复现的 Git 小练习，检查工作区与暂存区，逐块撤回 AI 错误改动，同时保留自己的修改和未跟踪笔记。"
keywords: ["撤回 AI 改动", "git restore patch", "Git 选择性恢复", "保留暂存修改"]
sidebar_position: 50
tags: ["tutorial", "coding-assistant", "agent-engineering", "git"]
---

# 在 Git 中精准“撤回”：保留你的手改，筛掉 AI 的错误

当你正在和 AI 编程助手协作时，最理想的情况是它每次生成的代码都是完美的。但现实往往是：AI 很热情，经常在你还没反应过来时就把整段逻辑重写了一遍——结果把你自己原本写好的地方也“顺便”覆盖了。

程序输出不对，但同文件里却既混着想要保留的 EUR 改动，又夹杂着不想保留的 `* 100` 错误行。若直接对整个文件执行恢复，很可能把这两块一并撤回；此外，已经提交的修改范围也需先检查清楚，避免误伤原有逻辑。

这篇文章不讲“如何避免 AI 犯错”——那是另一篇长文的任务。我们只解决一个非常实际的问题：**当你确认某些修改是错的，但同一份文件里又混进了你真正想要的改动时，如何用 Git 精准地“筛”掉错误，同时保留自己的手笔。**

我们将通过一个小练习一步步来：先保存状态，再检查差异，最后逐块选择性地恢复。读完并跟着做一遍后，你将能清晰地回答：**在 AI 协作中，如何安全地回滚错误而不牺牲工作。**

---

## 一、准备一个迷你实验仓库

为了避免在你现有的项目中试错（比如误删了某个重要提交），我们先在临时目录里建一个“安全沙盒”。这个小仓库会模拟你日常使用 Git 和 AI 助手时常见的修改状态。

### 1. 运行 setup 脚本

接下来验证练习环境：你已准备好运行 Git 2.43、Python 3、Linux 或 WSL 的 Bash。把 <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/efa81171466cc01774c91c3890ca169c50d92df9/examples/ai-rollback/setup-lab.py">setup-lab.py</a> 保存到一个文件夹，进入这个文件夹打开终端即可。下面的已有代码会自动创建临时目录并传入目标路径，你只需直接运行它，无需在此处增加任何初始化命令。

```bash
lab_dir=$(mktemp -d -t ai-rollback-XXXXXXXX)
python3 ./setup-lab.py "$lab_dir/project"
cd "$lab_dir/project"
```

这个脚本会：
- 创建一个全新的、空的 Git 仓库；
- 提交一个名为 `expense_report.py` 的基础版本（标记为 `before-ai`）；
- 在“你”的模拟操作下，先暂存一个正确的改动（货币单位改为 EUR），再在未暂存状态下混入一个 AI 风格的错误改动（总和乘以 100）；
- 同时创建一个未跟踪的 `notes.txt` 作为你的个人笔记。

### 2. 检查当前状态

```bash
git status --short
python3 expense_report.py
```

执行初始化后，你会看到如下状态：
```text
MM expense_report.py
?? notes.txt
My trip | EUR 2500
```
第一列的 `M` 表示暂存区（index）相对 HEAD 的修改；第二列的 `M` 表示工作区相对暂存区的修改。双问号 `??` 代表未跟踪文件。这些符号反映变更位置，绝非时间、速度或作者标记，据此无法推断操作者是人还是 AI。

### 3. 创建完整的本地副本（你的“时间胶囊”）

在执行任何恢复操作之前，我们先把整个仓库（包括 `.git` 配置和未跟踪文件）拷贝一份到旁边。这**不是**生产环境的备份方案，也不同于 worktree 或子模块机制，它只是一个用于对比练习的快照：

```bash
test ! -e ../recovery-copy && cp -a . ../recovery-copy
```

之后你可以用 `cmp` 验证复制是否完整：

```bash
cmp expense_report.py ../recovery-copy/expense_report.py
cmp notes.txt ../recovery-copy/notes.txt
```

复制环节必须分步确认：首先确保文件成功复制；随后只对 `expense_report.py` 和 `notes.txt` 这两份文件与其副本做两次对比，只有两项比较都通过才继续操作。这两个 `cmp` 验证的是特定文件的字节一致性，并不代表已逐一检查了整个目录下的所有文件。如果任何一次结果不符，请先停下检查差异，并保留副本作为后续对照。

---

## 二、理解当前有哪些“修改层”

理解 Git 的三个核心层：
- **工作区**：磁盘上的实际文件内容。
- **暂存区（Index）**：准备纳入下一次 commit 的快照缓冲区。
- **HEAD**：指向当前提交的指针。

注意：是否 `push` 是另一个维度的概念，切勿将暂存区称为“未推送的版本”。在本例中，我们首先创建了一个正确版本并提交（标记为 `before-ai`），随后人工将 USD 改为 EUR 并暂存，最后加入尚未暂存的错误数据（* 100）。未跟踪的 `notes.txt` 仅存在于磁盘上，并未进入 index。`before-ai` 只是一个标签（tag），指向当前 HEAD 所在的那个提交快照。

现在用三个 `git diff` 命令把这三层关系看清楚：

```bash
git diff before-ai -- expense_report.py
git diff --cached -- expense_report.py
git diff -- expense_report.py
```

输出会告诉你：

- **第一个 diff**：工作区相对 `before-ai` 的总变化。你会看到两个独立的差异块（hunk）：
  - 一个把 CURRENCY 从 USD 改成了 EUR；
  - 另一个把 `return sum(amounts)` 改成了 `return sum(amounts) * 100`。
- **第二个 diff**：暂存区相对 HEAD 的变化。这里只有 EUR 那个改动，因为它是你之前 add 的。
- **第三个 diff**：工作区相对暂存区的变化。这里只有 `* 100` 那一块，因为它是还没 add 的错误。

关键认知点：**整文件恢复到 `before-ai`，会连同 EUR 这个正确的修改一起被撤回**。这就是为什么我们需要更精细的控制——回到下一个章节。

---

## 三、精准恢复：用 patch 模式逐块选择

本例工作区里恰好包含想保留和想撤回的两块内容，而整文件恢复会把它们一起抹去。因此需要逐块选择：仅凭“都是 AI 改的”不足以断言整文件恢复就安全，还必须核对暂存区以及其他要保留的内容是否依然完整。下一节将演示如何安全地处理这种混合变更。

```bash
git restore --source=before-ai --patch --worktree -- expense_report.py
```

- `--source=before-ai`：以这个提交的快照为“参考基准”。
- `--patch`：交互模式。Git 会把每个差异块（hunk）显示给你，让你逐个决定“要还是不要”。
- `--worktree`：只影响当前工作区文件，不影响暂存区或 HEAD。

当 Git 在终端里问你类似：

```text
Apply this hunk to worktree? [y/n/q]
```

你只需要根据眼前的差异内容回答即可：**依据是“这行代码是我想要的吗？”，而不是“这段是 AI 写的吗？”**（因为 Git 并不知道作者身份）。

按照练习脚本设计的顺序，你会看到两个差异块：

1. **第一块（EUR 改动）**：
   - 把 `CURRENCY = "USD"` 改成了 `CURRENCY = "EUR"`。
   - 这是你要保留的你自己手动做的选择，所以回答 `n`（不要恢复）。

2. **第二块（* 100 错误）**：
   - 把 `return sum(amounts)` 改成了 `return sum(amounts) * 100`。
   - 这是 AI 顺手加的多余计算，所以要恢复回去，回答 `y`。

如果你不确定某段改动是否可靠，使用 q 可以终止后续提示，但已确认接受的块不会撤销。恢复前已经保存的副本会被完整保留，方便你对比或人工重建分支差异。当差异可以清晰拆成多个独立块时，Git 仍能辅助定位，但它无法自动判断“谁改了哪一行”；同一行内交织的修改不能仅靠猜测去回答或拆分，避免引入新的混乱。

---

## 四、验证：错误没了，手改还在

恢复完成后，我们用和前面类似的命令来确认结果：

```bash
python3 expense_report.py
git diff --exit-code
git diff --cached -- expense_report.py
git status --short
cmp notes.txt ../recovery-copy/notes.txt
```

你应看到：

- 程序输出变为 `My trip | EUR 25`（错误被修正，EUR 仍然保留）。
- `git diff --exit-code` 以 0 退出且无输出，说明被跟踪的工作区内容与 index 完全一致；未跟踪的 `notes.txt` 不参与此项检查。
- `git diff --cached` 仍然显示 USD → EUR 这一行，说明暂存区没被 touched。
- 状态显示：`M  expense_report.py`（相对于 HEAD 仍有暂存改动）和 `?? notes.txt`（未跟踪文件保留）。
- `cmp notes.txt ...` 无输出，表示笔记完整保留。

总结这一轮操作的影响范围：

- ✅ 工作区：精准移除了 `* 100`，同时保留了 EUR 改动。
- ✅ 暂存区：完全不受影响（仍然只有 USD → EUR）。
- ✅ HEAD：仍然指向 `before-ai` 这个原始提交，没有被移动或覆盖。
- ✅ 未跟踪文件：个人笔记 `notes.txt` 始终维持原样。

---

## 五、把这套思路迁移到自己的项目

1. 这是一个小型、独立停止写入的仓库演练。你的项目往往仍有多个开发者或持续变更，先评估影响范围：是否还有其他人在写？主分支是否仍在“热更”？

2. 保存你想保留的工作后，再选一个可信参考。记住：`commit` 只记录已暂存内容；`tag` 和 `branch` 只是对提交的引用，不会保存未提交的文件或 index 里新增的内容。因此，“打标签”不能替代“提交”或“备份”。

3. 把状态拆成四块看：工作区/index、index/HEAD、参考版本/当前文件、以及未跟踪文件。提交会携带作者元数据；而本地混合改动没有自动的人或 AI 归属标签，需要靠你的注释或约定来解释。

4. **错误已暂存时的局限**：本文的 `worktree-only` 命令会留下 index 中的错误版本，并非完整解决方案。提交前必须单独核对它。

5. 面对已提交或共享的修改：先检查里面是否包含你真正想保留的工作，再考虑经审阅的 `revert` 或局部修正。混合改动不能整笔盲撤；保留共享历史比强行抹平更稳妥。`checkout` 不带参考版本的文件恢复默认来自 index，并非“一键回到任意旧提交”的快捷键。

6. 即使没有 tag，项目可能已有提交、编辑器历史或备份文件，需要逐一核对。从未保存、未纳入跟踪的内容没有任何机制能“保证找回”，所以关键改动尽量先有意识暂存或提交。

如需深入，可查阅 [git restore](https://git-scm.com/docs/git-restore)、[git diff](https://git-scm.com/docs/git-diff)、[git revert](https://git-scm.com/docs/git-revert)，以及 [Git 基础](/zh/docs/course/essential-skills/git-github/)与 [Agent 入门](/zh/docs/tutorials/ai-coding-agent-beginner-guide/)的相关章节。

## 六、小结：AI 协作下的 Git 恢复心法

- **问题本质**：同一段文件里混有“你想要的修改”和“AI 顺手加的改动”。
- **核心工具**：`git restore --source=<checkpoint> --patch --worktree`，配合 `git diff` 系列命令。
- **操作心法**：
  - 一切恢复前，先建立可信参考版本；
  - 用 patch 模式逐个差异块决策，根据眼前内容判断；
  - 不盲目整文件回滚，尤其当暂存区或提交历史也被涉及时；
  - 始终在工作区、暂存区、HEAD 三个层面分别验证。

AI 是强大的副驾驶，但方向盘和刹车永远在你手里。学会用 Git 做你的“导航仪”，在复杂的路径中找到那条既保留你手改、又筛掉杂乱的路线——这就是现代开发者与智能工具共处的基本功。