---
title: "给单文件 HTML 记账小工具加分类：验证旧数据不被误改"
description: "给单文件 HTML 账本加分类，用旧备份验证首次保存、刷新和退回旧版后记录是否完整。"
tags: ["tutorial", "html", "backup"]
---

# 给单文件 HTML 记账小工具加分类：验证旧数据不被误改

## 准备环境

请先<a href="/examples/html-tool-upgrade-compatibility/expense-upgrade-exercise.zip" download="expense-upgrade-exercise.zip">下载练习包</a>，解压到一个空文件夹，并确保环境有 Python 3。在该目录下运行 `python3 -m http.server 8765 --bind 127.0.0.1`，用浏览器访问 `http://127.0.0.1:8765/v1.html`。每次练习请使用全新的浏览器配置，且全程只在一个标签页切换路径。进入 v1.html 后，用恢复文件控件选择 sample-backup.json，确认替换生效，你应该能看到三笔记录，合计 CNY 25.50。

## 第一轮：沿用旧格式版本号，看看会发生什么

第一轮验证“旧记录不被误写”的机制。在 same-version.html 中，用日期 2026-11-04、说明 Coffee、金额 2.00 添加一条记录，程序会自动将其归类为 general。接着在 v1.html 中用相同日期和说明 Snack、金额 2.00 再添加一笔。

打开 v1.html 本身不会改写存储。你在 v1.html 添加 Snack 并保存时，旧版重写记录，只留下原有字段，因此已有 Coffee 的 general 分类也丢了。回到 same-version.html，你会发现共有五笔，合计 CNY 29.50，但注意 Coffee 和其他所有记录的分类现在都显示为 uncategorized，这是因为旧版保存逻辑只写旧字段，不保留新版分类信息。

## 第二轮：显式版本号与格式升级（v2）

第二轮观察“新结构首次写入”的过程。在另一个干净的浏览器配置中从 v1.html 恢复同一份备份，然后打开 v2.html 查看三笔记录及默认分类，此时尚未写入任何新数据。用同样的日期、说明 Coffee、金额 2.00 在 v2.html 中添加一条记录，系统将自动将其归类为 general。首次成功写入后，同样的存储键会保存版本 2；刷新页面可以看到四笔记录，合计 CNY 27.50，旧字段和 Coffee 的分类得以保留。

再次打开 v1.html 时，这四笔新数据不会出现，且编辑与恢复功能被停用；重新回到 v2.html，四笔记录依然可见。

这意味着旧版 HTML 搭配旧备份只能还原到当时的三笔记录状态，后续新增内容必须从新版单独导出。

完成后 Ctrl+C。

## 验收你自己的改动清单

逐条核对 ID、字段和默认值，重点测试初读数据、首次保存、刷新保持以及保存后回退的稳定性。务必保留旧文件与旧备份以便对比验证。完成后可继续参考[备份恢复教程](https://aicoding.club/zh/docs/tutorials/html-tool-backup-restore/)与[部署课程](https://aicoding.club/zh/docs/course/building-projects/deployment/)，把这套单文件 HTML 工具真正集成到你的项目中。
