---
id: stage0
title: "Stage 0: AI Conversation & Prompt Fundamentals"
sidebar_label: "Stage 0: Vibecoding"
slug: /roadmap/stage0
sidebar_position: 1
keywords: [AI coding, office workers, prompt engineering, office automation, ChatGPT, Claude]
---

import VideoEmbed from '@site/src/components/VideoEmbed';

# Stage 0: AI Conversation & Prompt Fundamentals

**Welcome to your AI office automation journey!**

## Why Choose AI Tools?

AI tools have transformed the way we work. Without learning complex programming, you can simply describe your needs in natural language and let AI help you:
- Automate repetitive office tasks (data cleaning, format conversion, file processing)
- Generate weekly reports, summaries, email templates
- Process Excel spreadsheets, generate SQL scripts
- Batch rename files, convert image formats
- Create office utilities and scripts

<VideoEmbed
  videoId="PLKrSVuT-Dg"
  title="How to make vibe coding not suck…"
  caption="Watch this 5-minute Fireship intro video to understand how AI coding assistants work and learn practical tips to avoid common pitfalls."
  linkText="Watch on YouTube"
  linkUrl="https://www.youtube.com/watch?v=PLKrSVuT-Dg"
  aspectRatio="16/9"
/>

## Learning Outcomes

In this stage, you will learn to:
- Use AI (ChatGPT, Claude, etc.) to solve everyday office problems
- Describe your needs through simple conversations to get working solutions
- Understand the basic capabilities and limitations of AI tools
- Master effective prompt techniques
- Get started quickly without any programming background

## Why "Minimum Necessary Knowledge"?

You **don't need to**:
- Learn programming language syntax
- Understand algorithms and data structures
- Become a technical expert
- Spend months learning

You **only need**:
- The ability to clearly describe your needs
- Willingness to try and adjust
- Basic computer operation skills
- 30 minutes to 2 hours of learning time

## 📈 Track Your Progress

**Recommended:** Use GitHub Projects to visualize your learning journey

**Quick Setup (5 minutes):**
1. Create a new [GitHub Project](https://github.com/features/issues) in your account
2. Add cards: "Level 0.1", "Level 0.2", "Level 0.3", "Level 0.4", "Stage 0 Project"
3. Create columns: "Not Started" | "In Progress" | "Done"
4. Move cards as you complete each level

**Why this works:**
- ✅ Visual progress = motivation boost
- ✅ Easy to share with friends or recruiters
- ✅ Syncs naturally with your GitHub commits

**Alternative:** Notion template (coming soon)

:::tip Optional
Progress tracking is a tool, not a requirement. Use what works for you, or skip it entirely. The goal is learning, not checking boxes.
:::

## Get Started Now

### Step 1: Choose an AI Tool

The three most recommended:

**1. ChatGPT (Easiest to start)**
- URL: https://chat.openai.com
- Pros: User-friendly interface, stable results, good language support
- Best for: Daily office tasks, text generation, Excel advice

**2. Claude (Strongest reasoning)**
- URL: https://claude.ai
- Pros: Understands long documents, strong coding ability, fluent responses
- Best for: Code writing, data processing, complex tasks

**3. Copilot (Microsoft ecosystem)**
- URL: https://copilot.microsoft.com
- Pros: Free, integrates with Office, can search the web
- Best for: Users with Office subscriptions

### Step 2: Learn to Ask Questions

**Bad way to ask:**
> "Help me write code"

**Good way to ask:**
> "I have an Excel spreadsheet with an employee list (columns: Name, Department, Hire Date). I need to group by department, count the number of people in each department, and generate a simple summary table. What's the easiest method?"

**Even better:**
> "I have an Excel spreadsheet.
> Headers: Name, Department, Hire Date, Salary
> Data size: About 500 people
> Need: Count people and average salary by department, output as a new Excel file or CSV
> I don't know Python, but I'm willing to learn a simple script. How should I handle this?"

### Step 3: Try Common Office Tasks

#### Task 1: Generate a Weekly Report Template
```
Prompt: Please generate a weekly report template for me, including:
- Main work completed this week (5-10 items)
- Problems encountered and solutions (2-3 items)
- Plans for next week (3-5 items)
- Items needing support (1-2 items)

Requirements: Clear format, can be directly copied to Word or Email
```

#### Task 2: Clean Excel Data
```
Prompt: I have an Excel file with the following content:
[Paste first few rows of data]

Problems:
- Some cells have extra spaces
- Date formats are inconsistent ("2025-01-01" and "1/1/2025")
- Some data is duplicated

How can I quickly clean this in Excel? If code is needed, what language is simplest?
```

#### Task 3: Generate SQL Script
```
Prompt: I need to query employee information from a database.

Table structure:
- Table name: employees
- Fields: id, name, department, hire_date, salary

Need: Query employees in IT department with salary over 10000, sorted by hire date

Please give me the SQL query (I can run it directly in a database tool)
```

## Recommended Learning Resources

### Video Tutorials

1. **[Fireship: I built 10 web apps... with AI (in 14 minutes)](https://www.youtube.com/watch?v=UG3YC_jqPDg)**
   - *Why recommended:* Fast-paced demo showing AI coding possibilities - great for beginner motivation
   - Duration: 14 minutes

2. **[freeCodeCamp: AI-Powered Coding for Beginners](https://www.youtube.com/watch?v=X4H4MjrTvH0)**
   - *Why recommended:* Comprehensive beginner-friendly tutorial covering AI-assisted coding basics
   - Duration: 2 hours

3. **[Cursor IDE Tutorial for Beginners](https://www.youtube.com/watch?v=4q0ekTZqZZM)**
   - *Why recommended:* Step-by-step guide to the most popular AI coding editor
   - Duration: 25 minutes

### AI Tool Guides

4. **[GitHub Copilot Getting Started](https://docs.github.com/en/copilot/quickstart)**
   - *Why recommended:* Official documentation for one of the easiest AI coding tools

5. **[ChatGPT for Coding: Complete Guide](https://www.youtube.com/watch?v=jRAAaDll34Q)**
   - *Why recommended:* Learn how to effectively use ChatGPT for coding questions and code generation
   - Duration: 45 minutes

## Key Concepts

### What is a Prompt?

A prompt is your instruction to the AI. The clearer it is, the better the result.

**Three elements:**
1. **Context** - "I'm a project manager, I need..."
2. **Specific requirements** - "Generate a 2-hour meeting agenda, including..."
3. **Expected format** - "Output as a Markdown table"

### Why Does AI Sometimes Fail?

- **Insufficient information** - AI doesn't know your exact needs
- **Language ambiguity** - The same sentence can have multiple interpretations
- **Beyond capabilities** - Some tasks really do require programming or specialized tools
- **Hallucination** - AI sometimes confidently gives wrong answers

**Solution:** Ask questions, verify results, adjust step by step

## FAQ

**Q: Can I use AI-generated code directly?**
A: Usually yes, but always check. For simple scripts (Excel, batch processing) it's quite reliable. For production system code, review is needed.

**Q: Are free or paid tools better?**
A: Free versions are sufficient for learning and daily use. Paid versions mainly offer speed and unlimited usage. We recommend starting with free versions.

**Q: How long to learn everyday applications?**
A: 2-3 hours to complete basic tasks. 1-2 weeks to master most common scenarios.

**Q: Will I be replaced by AI?**
A: No. AI is a tool, not a replacement. What's truly valuable is people who know how to **use** AI.

## 🎉 Congratulations! Stage 0 Complete

You just learned to code with AI in 2-4 weeks. What's next? **The choice is yours.**

### Choose Your Path

**Option A: Continue Web Development**
You enjoyed building web projects. Let's go deeper.
→ Continue to [Stage 1](/docs/roadmap/stage1) (React, APIs, Databases)

**Option B: Explore Computer Science Theory**
You want to understand how things work under the hood.
→ [CS50 (Harvard)](https://cs50.harvard.edu) | [MIT OpenCourseWare](https://ocw.mit.edu) | [freeCodeCamp](https://freecodecamp.org)

**Option C: Apply Coding to Your Field**
You want to use coding in your existing domain:
- **Data Science:** [Python for Data Analysis](https://www.oreilly.com/library/view/python-for-data/9781491957653/) | [Kaggle Learn](https://www.kaggle.com/learn)
- **Design:** [Frontend Masters](https://frontendmasters.com) | [CSS-Tricks](https://css-tricks.com)
- **Marketing:** [Zapier Automation](https://zapier.com/learn) | [Google Analytics API](https://developers.google.com/analytics)
- **Research:** [Jupyter Notebooks](https://jupyter.org/try) | [matplotlib tutorials](https://matplotlib.org/stable/tutorials/index.html)

**Option D: Use AI Tools Like a Pro**
You just want to use AI tools effectively:
→ [Cursor Tips & Tricks](https://cursor.sh/docs) | [GitHub Copilot Guide](https://docs.github.com/copilot) | [Prompt Engineering 101](/docs/prompt-engineering-101)

**No wrong choice!** The roadmap sparked your interest. Now explore what excites you.

:::tip Optional Feedback
[Tell us which path you chose](https://forms.gle/placeholder) (1 minute, helps us improve)
:::

---

**Need help?** Check out our [Quick Start](/docs/intro) or [Resources](/resources)!
