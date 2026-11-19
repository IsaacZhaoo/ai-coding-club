---
title: "揭秘 AI 计时器页面：为何退出后“幽灵回调”仍在运行？"
description: "复现退出页面视图后继续触发的计时器，对比 Chrome Performance 录制并验证清理效果。"
tags: ["tutorial", "coding-assistant"]
---

# 揭秘 AI 计时器页面：为何退出后“幽灵回调”仍在运行？

打开 Chrome，在本地加载练习页 <a href="/examples/diagnose-page-timers/timers.html.download" download="timers.html">timers.html</a>。

## 第一步：复现“Leaky 模式”的异常行为
1. 页面加载时默认是 Leaky 模式。点击 **Enter**，再点 **Leave**，这算一轮。重复三轮。
2. 观察屏幕：Active timers 会显示为 **3**。
3. 停止所有操作（保持页面在前台），盯着 Ticks 数值的变动。你立刻会发现，即使不触发任何事件，Ticks 仍然在增长——意味着后台定时器仍在累积时间。

## 第二步：对比“Fixed 模式”的正常状态
1. 刷新页面，切换模式为 **Fixed**。
2. 同样执行三轮 Enter/Leave 操作。此时 Active timers 显示为 **0**。
3. 再次停止操作后观察 Ticks，它完全静止。说明此时的定时器句柄已被正确清除。

## 第三步：用 Performance 工具“抓”回调证据
1. 打开开发者工具，进入 Performance 面板。
2. 录制模式：
   - Leaky：录三轮操作 + 约 1 秒空闲。
   - Fixed：同样三轮 + 空闲时段。
3. 停止录制并切换视图到 Call Tree 或 Flame Graph。重点观察空闲时段（没有任何点击操作）的 **Timer Fired** 回调次数。
   - Leaky 的空闲段中，本次录制有 **12 次** 回调执行。
   - Fixed 的空闲段中，回调为 **0**。

## 第四步：向 AI 发出精准修复指令
将以下要求发给你的 AI 编程助手：

> “当前 Leaky 模式在点击 Leave 后，未调用 clearInterval 并从内部 handles 集合中移除句柄，导致 Active timers 滞留为 3，且空闲时段仍触发约 12 次多余回调。请修复 Leave 逻辑：调用 clearInterval 并从 handles 集合移除对应句柄。”

## 第五步：验证修复是否成功
1. 重新加载页面，切换回 Leaky 模式（或 AI 修复后的版本）。
2. 执行三轮 Enter/Leave 操作。
3. 观察 Active timers 是否在 Leave 后归零，且 Ticks 停止增长。
4. 再次用 Performance 录制空闲时段：理想情况下，回调次数应接近 **0**。

## 关键细节与失败判断
- 按钮组合才算一轮：**Enter → Leave** 连续点击，不是键盘 Enter 或切换标签。
- 始终保持在**前台页面**，避免页面挂起导致行为不一致。
- 250 毫秒是每个定时器的预设间隔，计数由页面自身维护，不要误认为是全局数据。
- 仅凭本测试，你只能证实“多余回调”的存在；不要直接推断内存泄漏或线程问题——那些需要更复杂的工具链验证。
