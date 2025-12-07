---
slug: example-draft-post
title: 示例草稿文章 - 即将推出
authors: [isaac]
tags: [announcement, draft-example]
draft: true
---

这是一个示例草稿博客文章。它演示了如何使用 `draft: true` 前置元数据在生产环境中隐藏文章,同时在开发环境中保持可见。

<!--truncate-->

## 草稿文章如何工作

当你在前置元数据中设置 `draft: true`:

- **开发模式**(`npm start`):文章可见
- **生产构建**(`npm run build`):文章被隐藏
- **GitHub 仓库**:源文件对所有人可见

## 发布工作流程

要发布这篇文章:

1. 从前置元数据中删除 `draft: true`
2. 提交并推送到内容仓库
3. 部署到生产环境

## 这种方法的好处

- 按自己的节奏写内容
- 发布前审查和完善
- 保持透明的开发过程
- 社区可以看到即将推出的内容(对教育内容来说可接受)
