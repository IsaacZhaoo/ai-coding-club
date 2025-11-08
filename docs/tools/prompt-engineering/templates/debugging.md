---
title: Debugging Prompts
description: Ready-to-use prompts for debugging code issues
---

# Debugging Prompt Templates

**Fix bugs faster with structured prompts**

These templates help you communicate bugs effectively to AI assistants, resulting in faster and more accurate solutions.

---

## 🎯 Basic Debugging Template

```markdown
**Problem**: [Brief description of the issue]

**Error Message**:
```
[Full error message with stack trace]
```

**Relevant Code**:
```[language]
[Code that's causing the issue]
```

**What I Expected**: [Desired behavior]

**What Actually Happens**: [Actual behavior]

**Steps to Reproduce**:
1. [Step 1]
2. [Step 2]
3. [Error occurs]

**Environment**:
- Language/Framework: [e.g., React 19, Python 3.12]
- OS: [e.g., macOS, Windows, Linux]
- Related packages: [e.g., Next.js 15, FastAPI 0.104]

**What I've Tried**:
- [Attempt 1]
- [Attempt 2]

Help me identify the root cause and suggest a solution.
```

---

## 🔥 Quick Debug Prompts

### Syntax Error
```
I'm getting this syntax error:

[ERROR MESSAGE]

In this code:
[CODE]

Please identify the syntax issue and show the corrected version.
```

### Runtime Error
```
My code compiles but crashes at runtime with:

[ERROR MESSAGE]

Here's the code:
[CODE]

Context: [What the code is supposed to do]

Help me understand why it's failing and how to fix it.
```

### Logic Error
```
My code runs without errors but produces incorrect output.

Expected output: [EXPECTED]
Actual output: [ACTUAL]

Code:
[CODE]

Test case:
[INPUT] -> should produce [EXPECTED] but produces [ACTUAL]

Help me find the logical error.
```

### Performance Issue
```
This code is too slow:

[CODE]

Context:
- Input size: [e.g., 10,000 items]
- Current performance: [e.g., 5 seconds]
- Target performance: [e.g., < 1 second]

Profile the code and suggest optimizations.
```

---

## 🎓 Advanced Debugging Templates

### Memory Leak Investigation
```
I suspect a memory leak in this code:

[CODE]

Symptoms:
- Memory usage starts at [X MB]
- After [Y] operations: [Z MB]
- Memory never decreases

Environment: [Node.js version / Browser]

Help me identify potential leaks and fix them.
```

### Race Condition Debug
```
I'm experiencing intermittent failures that suggest a race condition:

[CODE WITH ASYNC OPERATIONS]

Symptoms:
- Fails randomly, not consistently
- More likely to fail under load
- Error: [ERROR MESSAGE]

Help me identify and fix race conditions.
```

### Network Request Debugging
```
This API call is failing:

Endpoint: [URL]
Method: [GET/POST/etc]
Request body: [JSON/form data]

Error: [ERROR MESSAGE or status code]

Code:
[CODE]

Expected: [EXPECTED RESPONSE]
Actual: [ACTUAL RESPONSE or error]

Help me diagnose the API issue.
```

---

## 💡 Debugging Strategies Prompts

### Root Cause Analysis
```
Help me trace the root cause of this issue:

Error: [ERROR MESSAGE]
Code: [CODE]

Guide me through:
1. Understanding the error message
2. Identifying where it originated
3. Finding the root cause
4. Suggesting a fix
```

### Rubber Duck Debugging
```
Let me explain my code to you step by step:

[CODE]

Here's what I think is happening:
1. [Your understanding of step 1]
2. [Your understanding of step 2]
3. [Where you think it breaks]

Am I understanding this correctly? Where's my mistake?
```

### Binary Search Debugging
```
Help me narrow down where this bug occurs:

Full code: [CODE]

The bug is somewhere in this file. Let's binary search:
1. Does it happen in the first half or second half?
2. [Continue narrowing]

Error: [ERROR]
```

---

## 🛠️ Framework-Specific Templates

### React Debugging
```
React component not rendering correctly:

Component: [COMPONENT CODE]

Issue:
- Expected: [EXPECTED RENDER]
- Actual: [ACTUAL RENDER]

React DevTools shows: [STATE/PROPS INFO]

Console errors: [ANY ERRORS]

Help me debug this React issue.
```

### Python Exception Handling
```
Getting this Python exception:

```python
[FULL TRACEBACK]
```

Code causing the exception:
```python
[CODE]
```

Help me:
1. Understand the exception
2. Fix the immediate issue
3. Add proper error handling
```

### Database Query Issues
```
This SQL/database query is not working as expected:

Query:
```sql
[QUERY]
```

Expected result: [DESCRIBE EXPECTED]
Actual result: [DESCRIBE ACTUAL]

Schema:
[RELEVANT TABLE STRUCTURES]

Help me fix the query.
```

---

## 📊 When to Use Each Template

| Situation | Template | Best For |
|-----------|----------|----------|
| Clear error message | Basic Template | Most bugs |
| Code runs but wrong output | Logic Error | Algorithm bugs |
| Intermittent failures | Race Condition | Async issues |
| Slow performance | Performance Issue | Optimization |
| No clear error | Rubber Duck | Understanding |
| Large codebase | Binary Search | Narrowing scope |

---

## ✅ Checklist Before Debugging

Before using any template, gather:
- [ ] Full error message and stack trace
- [ ] Minimal code that reproduces the issue
- [ ] Expected vs actual behavior
- [ ] Environment details (versions, OS)
- [ ] What you've already tried

---

## 💡 Pro Tips

1. **Minimal Reproducible Example**: Reduce code to the smallest example that shows the bug
2. **One Bug at a Time**: Don't combine multiple issues in one prompt
3. **Include Error Messages**: Always paste the full error, not just a description
4. **Version Information**: Specific versions matter (e.g., "React 19" not "React")
5. **What You've Tried**: Show you've made an effort; AI provides better help

---

## 🔄 Iterative Debugging

If the first solution doesn't work:

```
I tried your suggestion:

[WHAT YOU TRIED]

New error/issue:
[NEW ERROR]

The original problem was: [ORIGINAL ISSUE]

What should I try next?
```

---

## 📚 Related Resources

- [Refactoring Templates](/docs/tools/prompt-engineering/templates/refactoring)
- [Testing Templates](/docs/tools/prompt-engineering/templates/testing)
<!-- Phase 2 course link - Coming soon
- [Course: Debugging with AI](/docs/course/02-essential-skills/06-debugging-with-ai)
-->

---

## 🤝 Contribute

Have a debugging prompt that works great? [Share it →](https://github.com/IsaacZhaoo/ai-coding-club/discussions)
