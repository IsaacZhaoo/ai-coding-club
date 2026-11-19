---
title: "用 tmux 为 AI 编写长任务设立“人工监督站”"
description: "用小脚本练习 tmux 分离和接回，再用日志、Git 改动和测试结果验收 Claude Code 长任务。"
tags: ["tutorial", "coding-assistant"]
---

# 用 tmux 为 AI 编写长任务设立“人工监督站”

下载 <a href="/examples/resume-claude-code-tmux/checkpoint.sh" download="checkpoint.sh">checkpoint.sh</a> 到一个空文件夹（比如 `~/ai-club-demo`），确保环境里有 Bash 和 tmux。

```sh
cd ~/ai-club-demo
```

然后执行 `tmux new -s lesson` 创建一个名为 `lesson` 的空会话。

在会话里运行 `bash checkpoint.sh`。按 `Ctrl+b` 松开手，接着按 `d`：你被“分离”了。终端画面消失，但会话仍在服务器端运行。

如何用肉眼确认分离没出问题？打开任意其他终端，输入 `tmux ls`，你会看到 `lesson` 依然存活。再执行 `tmux attach -t lesson`，立刻回到脚本现场。

约八秒后，在会话内执行 `cat progress.log`，确认包含 `ready`；再执行 `cat result.txt`，应该显示 `42`。这就是你在验证会话和脚本都按预期工作。

现在把注意力转向 Claude。在你的本地 Git 仓库中，用 `claude` 代替 checkpoint.sh：让它只读取一个文件（比如 `src/utils.ts`），做一处安全变更，执行已有的测试，最后汇报结果并停止。

> “在 `src/utils.ts` 中为函数 `normalizeId` 添加类型注解与边界检查，确保输入为空时返回 `null`。修改后运行 `npm test`，报告通过/失败的测试数量及任何错误信息。”

Claude 完成操作后，回到终端复核：`git status --short` 应显示一个修改文件；`git diff` 展示变更范围（注意它不会列出未跟踪文件，如需查看请另行打开）。最后亲手再跑一遍 `npm test`，确保结果一致。

练习结束前，在 tmux 会话内输入 `exit`。
