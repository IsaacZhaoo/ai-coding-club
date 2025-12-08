---
id: stage1
title: "Stage 1: AI Reality & Limitations"
slug: /roadmap/stage1
sidebar_position: 2
keywords: [AI coding, limitations, best practices, hallucination, prompt engineering]
---

import VideoEmbed from '@site/src/components/VideoEmbed';

# Stage 1: AI Reality & Limitations

**Understanding AI coding's capability boundaries and best practices**

## Why Is This Stage Important?

After experiencing the magic of AI tools, understanding their limitations is equally important. This stage helps you build realistic expectations and avoid common pitfalls.

<VideoEmbed
  videoId="2FJlhoDYNPE"
  title="AI Coding Masterclass: From Beginner to Expert in 90 Minutes"
  caption="This masterclass from Riley Brown will take you from beginner to expert. Learn how to write effective prompts, understand AI limitations, and build real projects with AI assistance."
  linkText="Watch on YouTube"
  linkUrl="https://www.youtube.com/watch?v=2FJlhoDYNPE"
  aspectRatio="16/9"
/>

## Learning Outcomes

In this stage, you will:
- Understand AI coding limitations
- Learn when to rely on AI and when to rely on yourself
- Identify AI hallucinations and errors
- Master better prompting techniques
- Know when AI is helping and when it's causing problems

## AI Strengths and Limitations

### What AI Excels At

| Task Type | Examples | Reliability |
|-----------|----------|-------------|
| Boilerplate code | Generate CRUD functions, form validation | ⭐⭐⭐⭐⭐ |
| Common patterns | SQL queries, regex, Excel formulas | ⭐⭐⭐⭐⭐ |
| Quick prototypes | Small tools, scripts, automation | ⭐⭐⭐⭐ |
| Code explanation | Reading and explaining existing code | ⭐⭐⭐⭐ |
| Format conversion | JSON to CSV, data cleaning | ⭐⭐⭐⭐ |

### What AI Struggles With

| Task Type | Why It's Difficult | Recommended Approach |
|-----------|-------------------|---------------------|
| Complex architecture | Requires global perspective and business understanding | Plan yourself first, then have AI implement details |
| Novel problem solving | AI relies on patterns in training data | Break down problems, verify step by step |
| Security-critical code | May have hidden vulnerabilities | Manual review + security testing |
| Performance optimization | Lacks runtime context | Use profiler, targeted optimization |
| Latest APIs | Training data may be outdated | Verify with official documentation |

## What is AI Hallucination?

**Hallucination** refers to AI confidently providing incorrect or fabricated information.

### Common Types of Hallucinations

1. **Fabricated APIs/Functions**
   ```python
   # AI might generate non-existent functions
   import pandas as pd
   df.auto_clean_data()  # This function doesn't exist!
   ```

2. **Outdated Information**
   - Recommending deprecated library versions
   - Using removed syntax
   - Referencing documentation links that no longer exist

3. **Logically Seems Correct but Has Bugs**
   ```python
   # AI-generated code might have boundary condition issues
   def divide(a, b):
       return a / b  # Doesn't handle b=0 case
   ```

### How to Identify Hallucinations

- **Ask AI for sources**: Have it provide reference links, then verify
- **Cross-validate**: Check with search engines or official documentation
- **Run tests**: Always test generated code
- **Stay skeptical**: The more confident AI is, the more carefully you should verify

## Best Practices for Office Scenarios

### Excel/Data Processing

**Good practices:**
```
✅ Give AI specific data samples (first 5 rows)
✅ Clearly specify expected output format
✅ Test on small batch before processing all data
✅ Keep backup of original data
```

**Avoid:**
```
❌ Running AI-generated scripts directly on original files
❌ Assuming AI understands your business logic
❌ Skipping result verification
```

### Report/Email Generation

**Good practices:**
```
✅ Provide specific background information
✅ Give style samples or templates
✅ Review sensitive information before sending
✅ Check data and fact accuracy
```

**Avoid:**
```
❌ Blindly copy-paste
❌ Including confidential information in AI prompts
❌ Not checking content before sending
```

### Code/Script Generation

**Good practices:**
```
✅ Run in test environment first
✅ Understand what the code does (even roughly)
✅ Add error handling and logging
✅ Use version control (can rollback)
```

**Avoid:**
```
❌ Running directly in production
❌ Running code you don't understand
❌ Ignoring error messages
```

## Recommended Resources

### Understanding AI Coding Limitations

1. **[Andrej Karpathy on AI Coding](https://twitter.com/karpathy/status/1748863275736449258)**
   - *Why recommended:* Direct insights from a top AI researcher about the real capabilities and limitations of AI coding assistants

2. **[Simon Willison: Things I learned about LLMs](https://simonwillison.net/2023/Aug/3/weird-world-of-llms/)**
   - *Why recommended:* Practical experience from someone who uses LLMs for coding daily

3. **[The False Promise of AI Coding Assistants](https://stackoverflow.blog/2024/06/10/generative-ai-is-not-going-to-build-your-engineering-team-for-you/)**
   - *Why recommended:* Stack Overflow's realistic perspective on whether AI can replace software development

### Best Practices

4. **[GitHub Copilot Best Practices](https://github.blog/developer-skills/github/how-to-write-better-prompts-for-github-copilot/)**
   - *Why recommended:* Official guide from GitHub on effective AI coding practices

5. **[OpenAI's Prompt Engineering Guide](https://platform.openai.com/docs/guides/prompt-engineering)**
   - *Why recommended:* Foundational techniques for getting better results from AI models

### Critical Thinking

6. **[The Danger of Trusting AI Code Blindly](https://blog.humphd.org/chasing-the-bear/)**
   - *Why recommended:* Real case study about the risks of blindly accepting AI-generated code

7. **[Testing AI-Generated Code](https://martinfowler.com/articles/exploring-gen-ai.html)**
   - *Why recommended:* Martin Fowler's insights on validating AI-generated code

## Practical Checklist

### Before Using AI to Generate Code

- [ ] Have I clearly described my requirements?
- [ ] Have I provided enough context?
- [ ] Do I know what output to expect?

### After Receiving AI Output

- [ ] Does the code run?
- [ ] Are there obvious errors or bugs?
- [ ] Are edge cases handled?
- [ ] Do I understand what the code does?

### Before Using/Deploying

- [ ] Validated on test data?
- [ ] Is there a backup/rollback plan?
- [ ] Is sensitive information secure?

## Next Steps

After completing this stage, you will:
- ✓ Be able to identify AI's strengths and limitations
- ✓ Know how to verify AI output
- ✓ Master best practices for office scenarios
- ✓ Be ready to learn **Stage 2: Context & Architecture**

**[Start Stage 2 →](./stage2)**

---

**Need help?** Check out our [Quick Start](/docs/intro) or [Resources](/resources)!
