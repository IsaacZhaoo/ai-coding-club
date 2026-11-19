---
title: "零门槛 AI 小应用制作：六图卡离线测验"
description: "下载单文件 HTML 识物游戏，断网测试六道题，再用 AI 换题并检查重试、得分和重新开始。"
tags: ["tutorial", "coding-assistant"]
---

# 零门槛 AI 小应用制作：六图卡离线测验

如果你从未写过一行代码，这个 <a href="/examples/offline-picture-quiz/cards.html.download" download="cards.html">六张图卡小游戏</a>就是你的第一个“AI 作品”。下载后，在 Android 的“文件”应用中找到 Download/cards.html，点击并选择 Chrome 打开（或任何能运行 HTML 的浏览器）。网络关闭也能正常答题，真正完全离线。

## 玩一玩，先体验再动手

游戏按顺序给出六张图卡：猫、狗、苹果、公交、鱼、太阳。每屏只显示一张 emoji 和两个按钮（首题是 Cat / Dog）。先错误地点击 Dog，会得 0 分并显示“Try again”，重选 Cat 得 1 分；六题答完出现 6/6 与 Restart，重启后分数归零重新从猫开始；刷新页面同样回到第一题。所有逻辑都由内嵌 JavaScript 控制，无需服务器。

## 断网验证，避免缓存干扰

某些附件预览不会执行脚本。确保：在文件管理器选中 cards.html，打开一个可运行 HTML 的浏览器；关闭 Wi-Fi/移动数据后重新加载该文件才算有效验证，不要依赖网站缓存或在线预览。

## 想改题？把你的新需求交给 AI

把完成的 cards.html 发给 AI，并附上这句提示：  
“把六题换成六种交通工具的 emoji 和对应英文答案，保留两个选项、选错重试、得分、重新开始；只交付这一份可断网打开的 HTML。”  
AI 会替你生成新版本（类似 transport.html）。另存为新版文件，再用同样的断网方式验证一次即可。改题不需要 Python，也不需要外部图片资源，全部通过 emoji + 原生 JavaScript 完成。
