# Selective Git restore exercise / Git 选择性恢复练习

Use Git 2.43 and Python 3 in Bash on Linux or WSL. Save `setup-lab.py` in a
folder and open a terminal there. The destination must not already exist.

使用 Linux 或 WSL 的 Bash、Git 2.43 与 Python 3。将 `setup-lab.py` 保存到一个
文件夹，在该文件夹中打开终端；目标目录必须尚不存在。

```bash
lab_dir=$(mktemp -d -t ai-rollback-XXXXXXXX)
python3 ./setup-lab.py "$lab_dir/project"
cd "$lab_dir/project"
git status --short
python3 expense_report.py
```

The script creates a standalone repository with a staged USD→EUR edit, an
unstaged simulated calculation error, and an untracked note. It refuses an
existing destination and does not require an AI service or Python dependencies.

脚本创建独立仓库，包含已暂存的 USD→EUR 修改、未暂存的模拟计算错误及未跟踪
笔记。脚本拒绝覆盖已有目标；无需 AI 服务或额外 Python 依赖。

Follow the tutorial for inspection, preserving a recovery copy, interactive
restoration, and verification:

- [English tutorial](https://aicoding.club/docs/tutorials/undo-ai-changes-preserve-work/)
- [中文教程](https://aicoding.club/zh/docs/tutorials/undo-ai-changes-preserve-work/)

To check the fixture automatically, save both Python files in the same directory
and choose an output path that does not already exist:

自动核验时，将两个 Python 文件放在同一目录，选择尚不存在的结果文件路径：

```bash
python3 verify-lab.py --output /tmp/ai-rollback-verification.json
```

The verifier uses its own temporary repository and removes it after the checks.
核验脚本使用自己的临时仓库，检查结束后自动清理。
