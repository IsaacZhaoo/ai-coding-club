---
title: "Build Your Own Six-Card AI Picture Quiz (Offline)"
description: "Download a six-card HTML picture quiz, try it offline and customize the answers with AI. Check retry, scoring and restart on a mobile browser."
tags: ["tutorial", "coding-assistant"]
---

# Build Your Own Six-Card AI Picture Quiz (Offline)

Bring a tiny AI-style picture quiz straight to your phone without Wi‑Fi, servers, or installations. You’ll make a single HTML file with six emoji cards (cat, dog, apple, bus, fish, sun), two answer buttons per question, and immediate feedback—perfect for learning on the go.

## 1. What You’ll Have
- Exactly two buttons per question: one correct, one distractor.
- First picture is 🐈; clicking Dog keeps score at 0 with “Try again”; clicking Cat advances and awards a point.

## 2. Download the Ready-to-Run File
- <a href="/examples/offline-picture-quiz/cards.html" download="cards.html">Download cards.html</a>

Save it locally using your browser’s download dialog. Do not rely on an attachment preview—preview windows often restrict JavaScript. On mobile, tap the file and choose “Open in Chrome/Safari” or equivalent; behavior varies by device, so treat this as a test you’ll run yourself.

## 3. Run It Offline (Step-by-Step)
1. Open cards.html locally (double-click on desktop or use a local file picker on mobile).
2. No network is needed after download. Reloading the saved file always resets to card one.

## 4. How the Quiz Works
- Correct answers advance to the next card; incorrect answers show “Try again” and keep score unchanged.
- After six cards, you hit Restart to begin again.

## 5. Customize with AI (One Prompt)
Ask an AI model this exact prompt to rewrite the content while preserving offline behavior:

> Rewrite the quiz so the six embedded emoji pictures are [emoji1], [emoji2], [emoji3], [emoji4], [emoji5], [emoji6] in order, and the answer choices use the same two-button pattern per question. Keep the retry logic, restart flow, and single HTML file structure unchanged.

## 6. Acceptance Test on Your Phone
1. Save cards.html to your device.
2. Turn off Wi‑Fi/mobile data.
3. Open the saved file and verify: first picture is 🐈; Dog shows “Try again”; Cat advances.
4. Complete six cards, note score progression, then Restart.
