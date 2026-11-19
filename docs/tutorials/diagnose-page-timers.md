---
title: "Diagnosing a Timer Left Running When Exiting a Page"
description: "Reproduce an interval that keeps firing after leaving a view. Compare Chrome Performance traces and verify that timer cleanup stops the callbacks."
tags: ["tutorial", "coding-assistant"]
---

# Diagnosing a Timer Left Running When Exiting a Page

## 🔬 Lab Setup: The Timer Exercise

Start by **<a href="/examples/diagnose-page-timers/timers.html.download" download="timers.html">downloading the timer lab</a>**. This simple HTML page includes two buttons labeled **Enter** and **Leave**. We’ll use them repeatedly to simulate real-world user behavior while we run diagnostics.

Before you begin, make sure Chrome’s DevTools are open (`F12`) so we can monitor CPU and timers in real time.

## 📋 Execution Protocol: Three Rounds of Enter/Leave

This is where precision matters. Follow these steps exactly to reproduce the leak condition consistently:

1. Focus on **one foreground tab only**. No navigation away.
2. **CLICK Enter once**, then immediately **CLICK Leave once**. That’s one complete round.
3. Repeat this pair **exactly three times** in total.

## 📊 Step 1: Capture the Leak

After completing your three rounds, pause and observe the metrics panel instrumented by the page:

- You’ll see **3 active timers** still running.
- Their tick counters keep rising even though no user interaction is occurring.

This confirms a classic symptom: intervals are scheduled but never cleared when the user leaves.

## 🛠️ Step 2: Apply the Fix – Fixed Lifecycle Mode

Now let’s test a corrected implementation:

1. **Refresh** the page.
2. Change the toggle setting from *Leaky* to **Fixed**.
3. Repeat the exact same three Enter/Leave pairs.

Observe the results:

- **Active timers**: 0 after each Leave.
- **Tick counters**: Stop incrementing after Leave.
- No lingering callbacks, no phantom scheduling.
## 🎬 Step 3: Record Chrome Performance Traces

To see what’s actually happening under the hood, let’s capture two performance traces:

1. Open **Performance → Record**.
2. Start recording before each Enter/Leave sequence.
3. Keep recording for about one second after the final button click to catch any late callbacks.
4. Repeat this for both Leaky and Fixed modes.

Focus your analysis on **“Timer Fired” callbacks** during that final quiet second:

- **Leaky run**: 12 callbacks fired.
- **Fixed run**: 0 callbacks.

## 💡 Why Clearing on Leave Matters

The core issue lies in lifecycle management:

- In the *leaky* version, intervals are scheduled with `setInterval` but never cleared when the user leaves.
Save each interval handle when creating it.

```js
clearInterval(current);
handles.delete(current);
```

## 🤖 Prompting an AI Assistant

If you’re asking an AI to refactor the lab code, keep it scoped and surgical:

> “Change only the interval lifecycle management in the timer logic. Ensure each interval handle is saved and explicitly cleared when the Leave action occurs. Do not modify other behaviors or UI elements.”

Then re-run your three-round test and compare traces again. The result should match the Fixed mode: zero callbacks, zero active timers.
- The active timer count shown here is **instrumented by the page itself**—it’s a reliable metric for this demo.
