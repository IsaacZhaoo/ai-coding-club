---
id: stage2
title: "Stage 2: Context & Architecture"
slug: /roadmap/stage2
sidebar_position: 3
keywords: [AI coding, context, project architecture, prompt engineering, RAG]
---

import VideoEmbed from '@site/src/components/VideoEmbed';

# Stage 2: Context & Architecture

**Master how to provide effective context to AI for better code**

## Why Context Matters

AI coding assistants' performance depends entirely on the context you provide. This stage teaches you how to organize projects and prompts to maximize AI effectiveness.

<VideoEmbed
  videoId="dJhlMn2otxA"
  title="Learn to Code using AI - ChatGPT Programming Tutorial"
  caption="This complete course from freeCodeCamp teaches you how to effectively use AI for programming. Learn how to provide the right context, structure prompts, and leverage AI tools to build real applications."
  linkText="Watch on YouTube"
  linkUrl="https://www.youtube.com/watch?v=dJhlMn2otxA"
  aspectRatio="16/9"
/>

## Learning Outcomes

In this stage, you will:
- Design AI-friendly project architecture
- Provide effective context in prompts
- Understand RAG (Retrieval-Augmented Generation) techniques
- Organize code for better AI comprehension
- Make good use of documentation and examples

## Three Levels of Context

### 1. Immediate Context

**Information provided directly in the current conversation**

```
Good immediate context example:

"I'm developing a Python script to process Excel files.
Current code:
[paste code]

Problem: Getting error 'KeyError: Department' when running
Excel file columns: Name, Department Name, Hire Date

Please help me fix this issue."
```

### 2. Project Context

**Project structure, tech stack, existing code**

```
Project structure example:
my-automation/
├── scripts/
│   ├── excel_processor.py
│   └── email_sender.py
├── data/
│   └── employees.xlsx
├── config.yaml
└── README.md

Tell AI:
"This is a Python automation project using pandas for data processing,
configuration is in config.yaml, please follow the existing code style..."
```

### 3. Domain Context

**Business rules, industry terminology, specific constraints**

```
Domain context example:

"Our company's business rules:
- Employees are divided into A/B/C levels
- Level A employees get 15 days annual leave, B gets 10 days, C gets 7 days
- Less than one year of employment is calculated proportionally
- Attendance must be submitted before the 25th of each month

Please help me write an annual leave calculation function based on these rules."
```

## Tips for Providing Context

### Tip 1: Give AI a Role

```
"You are an experienced Python developer focused on data processing and office automation.
Your coding style emphasizes readability and simplicity, preferring pandas and openpyxl.
Please help me..."
```

### Tip 2: Provide Examples

```
Input example:
| Name | Region | Sales |
|------|--------|-------|
| John | East   | 50000 |
| Jane | South  | 30000 |

Expected output:
| Region | Total Sales | Count | Average Sales |
|--------|-------------|-------|---------------|
| East   | 50000       | 1     | 50000         |
| South  | 30000       | 1     | 30000         |
```

### Tip 3: Request in Steps

```
Don't:
"Help me write a complete report generation system"

Do this instead:
"Step 1: First help me write a function to read Excel
Step 2: Then write a data cleaning function
Step 3: Finally write a summary statistics function"
```

### Tip 4: Specify Constraints

```
Constraint example:

"Please help me write a data export script with these requirements:
- Python 3.8 compatible
- Cannot use third-party libraries (standard library only)
- Memory usage under 100MB
- Processing time under 5 minutes
- Support for interrupt recovery"
```

## Project Architecture Best Practices

### Clear File Structure

```
Recommended project structure:

office-automation/
├── README.md           # Project description (AI reads first)
├── requirements.txt    # Dependency list
├── config/
│   └── settings.yaml   # Configuration file
├── src/
│   ├── __init__.py
│   ├── excel_handler.py    # Excel processing
│   ├── email_sender.py     # Email sending
│   └── report_generator.py # Report generation
├── templates/
│   └── email_template.html
├── tests/
│   └── test_excel_handler.py
└── data/
    └── .gitkeep
```

### Meaningful Naming

```python
# Bad naming
def process(d):
    return d['a'] + d['b']

# Good naming
def calculate_total_sales(sales_record):
    """Calculate total sales for a sales record"""
    return sales_record['base_sales'] + sales_record['bonus_sales']
```

### Self-Documenting Code

```python
# Good docstrings help AI understand code intent
def generate_monthly_report(
    data_file: str,
    output_path: str,
    month: int,
    include_charts: bool = True
) -> str:
    """
    Generate monthly sales report

    Args:
        data_file: Input Excel file path
        output_path: Output directory
        month: Report month (1-12)
        include_charts: Whether to include charts

    Returns:
        Path to generated report file

    Example:
        >>> generate_monthly_report('sales.xlsx', './reports', 12)
        './reports/2025-12-report.xlsx'
    """
    pass
```

## Recommended Resources

### Prompt Engineering Guides

1. **[Anthropic's Prompt Engineering Guide](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview)**
   - *Why recommended:* Comprehensive guide on effective prompting techniques from Claude's creators

2. **[LangChain Prompt Engineering](https://python.langchain.com/docs/modules/model_io/prompts/)**
   - *Why recommended:* Practical patterns for structured prompting in production applications

3. **[OpenAI Cookbook: Code Generation](https://cookbook.openai.com/)**
   - *Why recommended:* Real-world examples and best practices for code generation

### Context & Architecture

4. **[Anthropic: Long Context Window Best Practices](https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/long-context-tips)**
   - *Why recommended:* Techniques for effectively using long context windows for entire codebases

5. **[GitHub: Awesome AI Coding](https://github.com/sourcegraph/awesome-ai-coding)**
   - *Why recommended:* Curated list of tools, patterns, and best practices for AI-assisted development

6. **[Cursor Composer: Multi-File Editing Patterns](https://docs.cursor.com/context/rules-for-ai)**
   - *Why recommended:* Official guide on organizing projects for multi-file AI editing

### Advanced Techniques

7. **[RAG for Code: Retrieval-Augmented Generation](https://blog.langchain.dev/code-understanding-with-langchain/)**
   - *Why recommended:* Techniques for providing relevant context from large codebases

## Practical Templates

### Task Request Template

```markdown
## Task Description
[Clearly describe what you want to achieve]

## Background Information
- Project type: [e.g., Python office automation]
- Tech stack: [e.g., pandas, openpyxl]
- Environment: [e.g., Windows 10, Python 3.9]

## Input Data
[Provide sample data or data structure description]

## Expected Output
[Describe the desired result format]

## Constraints
[List any limitations or requirements]

## Existing Code
[Paste relevant code here if any]
```

### README Template

```markdown
# Project Name

## Overview
[One-sentence description of what the project does]

## Features
- Feature 1
- Feature 2

## Tech Stack
- Python 3.9+
- pandas, openpyxl

## Installation
\`\`\`bash
pip install -r requirements.txt
\`\`\`

## Usage
\`\`\`bash
python main.py --input data.xlsx --output report.xlsx
\`\`\`

## Configuration
Edit config.yaml to set parameters

## File Structure
[Brief description of main files]
```

## Next Steps

Congratulations! You've completed the three stages of the foundational learning path:

- ✓ **Stage 0**: Mastered AI conversation and prompt fundamentals
- ✓ **Stage 1**: Understood AI's reality and limitations
- ✓ **Stage 2**: Learned to provide effective context

### Continue Learning

- Explore [AI Coding Tools](/docs/tools) - Discover powerful AI coding assistants
- Check out [Prompt Engineering](/docs/tools/prompt-engineering) - Master the art of prompting
- Browse our [Course](/docs/course) - Deep-dive into AI coding fundamentals

---

**Need help?** Check out our [Quick Start](/docs/intro) or [Resources](/resources)!
