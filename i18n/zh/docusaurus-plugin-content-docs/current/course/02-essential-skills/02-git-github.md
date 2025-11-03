---
sidebar_position: 2
sidebar_label: 'Git & GitHub 101：像专业人士一样保存你的工作'
title: 'Git & GitHub 101：像专业人士一样保存你的工作'
description: 'Git & GitHub 101：像专业人士一样保存你的工作'
---

你是否曾经害怕改变你的代码因为你可能会破坏它？版本控制是答案。把它想象成你的代码的"存档"系统。Git是最受欢迎的版本控制系统，GitHub是一个存储你的Git项目在线的网站。

### 什么是版本控制?

版本控制跟踪你的文件随时间的变化。这意味着你可以：

- 看到谁改变了什么和什么时候。
- 如果你犯了错误，回到之前的版本。
- 与其他人在同一个项目上协作，而不会覆盖彼此的工作。

### Git基础：你的本地仓库

Git在你的本地机器上工作。这是最常见的命令：

- **`git init`**：在你的项目文件夹中初始化一个新的Git仓库。
- **`git status`**：显示你的更改的状态。
- **`git add <file>`**：将文件添加到"暂存区"，这是你想保存的更改列表。使用`git add .`添加所有文件。
- **`git commit -m "Your message"`**：用描述性消息保存暂存的更改。
- **`git log`**：显示所有提交的历史记录。

### GitHub：你的远程仓库

GitHub是在云中托管你的Git仓库的平台。这允许你备份你的代码并与他人协作。

1. **创建GitHub账户**：转到[https://github.com](https://github.com)并注册。
2. **创建新仓库**：在你的GitHub仪表板上单击"新建"按钮。
3. **推送你的代码**：按照GitHub上的说明连接你的本地Git仓库到远程GitHub仓库并"推送"你的提交。

### AI用于提交消息

编写好的提交消息是重要的。如果你被卡住，你的AI可以帮助！

> "为以下更改写一个简短的、必要的git提交消息：[粘贴`git diff`的输出]"

### 你的转向：推送到GitHub

1. 转到你在上一课创建的`my-first-project`目录。
2. 运行`git init`。
3. 创建一个`README.md`文件并写下你的项目的简短描述。
4. 运行`git status`以查看你的新文件。
5. 运行`git add README.md`。
6. 运行`git commit -m "Add initial README file"`。
7. 在GitHub上创建一个新的仓库并推送你的第一次提交！

这是所有现代开发者的基本工作流程。
