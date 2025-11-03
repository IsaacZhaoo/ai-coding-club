---
sidebar_position: 3
sidebar_label: '后端专业化：API和数据库与AI'
title: '后端专业化：API和数据库与AI'
description: '后端专业化：API和数据库与AI'
---

欢迎来到后端专业化路径！如果你对逻辑、数据和应用在幕后的工作方式感到着迷，后端对你来说很合适。在这篇文章中，我们将为我们的任务管理器构建一个健壮的后端，包括一个真实的数据库和API。

### 什么是后端？

后端是应用中在服务器上运行的部分。它负责存储和检索数据、处理业务逻辑和响应来自前端的请求。我们的原始任务管理器在浏览器的 `localStorage` 中存储数据，这不是持久或可共享的。一个真实的后端解决了这个。

### RESTful API设计

API（应用编程接口）是前端与后端通信的方式。RESTful API是使用HTTP方法设计API的标准方式：

- **`GET /tasks`**: 获取所有任务的列表。
- **`POST /tasks`**: 创建新任务。
- **`PUT /tasks/:id`**: 更新任务。
- **`DELETE /tasks/:id`**: 删除任务。

你可以要求你的AI帮助你设计你的API：

> "我正在为一个任务管理器构建后端。你能为它设计一个RESTful API吗？"

### 数据库建模

我们需要一个数据库来存储我们的任务。我们有两个主要选择：

- **SQL（关系型）：** 如PostgreSQL或MySQL。数据存储在带行和列的表中。非常结构化。
- **NoSQL（非关系型）：** 如MongoDB。数据存储在灵活的文档中（通常是JSON类）。

对于我们的任务管理器，简单的SQL表是一个很好的选择。你可以要求你的AI设计它：

> "设计一个简单的PostgreSQL表来存储任务。每个任务应该有一个ID、一个文本描述和一个布尔值表示它是否完成。"

### 使用Node.js和Express构建API

Node.js是用于后端的JavaScript运行时，Express是使用它构建API的流行框架。你可以要求你的AI为你生成样板代码。

> "生成一个简单的Express.js服务器，有一个端点从PostgreSQL数据库获取所有任务。"

### 轮到你了：构建后端

你的目标是为你的任务管理器构建一个真实的后端。

1. 在像 [Supabase](https://supabase.com/) 或 [Render](https://render.com/) 这样的平台上设置一个免费的PostgreSQL数据库。
2. 初始化一个新的Node.js项目（`npm init -y`）并安装Express和用于PostgreSQL的 `pg` 库。
3. 要求你的AI帮助你编写代码来连接到你的数据库。
4. 为你的任务创建四个RESTful API端点（GET、POST、PUT、DELETE）。
5. （高级）要求你的AI帮助你添加简单的用户身份验证，以便用户只能看到自己的任务。

这是一个具有挑战性但非常有收获的项目。完成后，你可以将上一课的React前端连接到这个新后端，创建一个真正的全栈应用。
