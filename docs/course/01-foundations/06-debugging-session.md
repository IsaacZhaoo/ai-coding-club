---
sidebar_position: 6
sidebar_label: 'Lesson 6: Debugging AI-Generated Code'
title: 'Spotting the Glitch: How to Debug AI-Generated Code'
description: 'Spotting the Glitch: How to Debug AI-Generated Code'
---

> TL;DR: Debug with AI using minimal repro + expected vs actual + verification.

## Key steps
1. Capture the error message and the smallest reproducible code.
2. Ask for hypotheses and concrete checks.
3. Apply one fix at a time and re-test.

## Practice
- Break a small script on purpose, then ask AI to fix it using a minimal repro.

We've established that AI-generated code can be flawed. So, what do you do when the code your AI assistant provides looks perfect but throws an error, or worse, fails silently? You debug it. 

Here are practical techniques for debugging and verifying code that came from your AI co-pilot.


### 1. Run it Immediately

This sounds obvious, but it's the most important step. Before you integrate the AI's code into your main project, run it in isolation. If it's a function, call it with some sample inputs. If it's a component, render it on a blank page. The faster you can confirm it works (or doesn't), the better.

### 2. Ask the AI to Write Tests

One of the most powerful uses of AI is to test its own work. If an AI gives you a function, your next prompt should be:

**Your Prompt:**
```
Great. Now, can you write a set of unit tests for the function you just gave me? Please include tests for edge cases, such as null inputs and empty arrays.
```

This forces the AI to "think" through its own logic and often reveals flaws before you even run the code.

### 3. Use the AI as a Debugging Partner

When you get an error, don't just try to fix it yourself. Bring the AI into the loop. Copy the entire error message and paste it back into the chat.

**Your Prompt:**
```
I ran the code you provided and got the following error. What does it mean, and how can we fix it?

[Paste the full error message here]
```

The AI is often very good at explaining error messages and suggesting fixes. This turns a frustrating bug into a learning opportunity.

### 4. Isolate and Question

If a larger block of AI-generated code isn't working, don't try to debug it all at once. Isolate smaller pieces. Ask the AI to explain its own code, line by line.

**Your Prompt:**
```
Can you explain this line of code to me? What is it supposed to do?

[Paste a specific line of code here]
```

By treating the AI's output with healthy skepticism and using the AI itself as part of your verification process, you can catch errors early and build confidence in your AI-assisted workflow.

Next, we'll dive into the single most important skill for getting high-quality results from your AI: mastering the art of context.
