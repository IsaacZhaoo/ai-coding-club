# Translation Guide

**Version:** 1.1
**Last Updated:** 2025-11-03
**Status:** Active

## Overview

This guide provides comprehensive instructions for translating AI Coding Club content from English to Chinese (and future languages). Our translation infrastructure is built on Docusaurus i18n capabilities with custom tooling for consistency and quality.

## Table of Contents

1. [Translation Philosophy](#translation-philosophy)
2. [Using the Glossary](#using-the-glossary)
3. [File Structure](#file-structure)
4. [Translation Workflow](#translation-workflow)
5. [Quality Standards](#quality-standards)
6. [Common Patterns](#common-patterns)
7. [Troubleshooting](#troubleshooting)

---

## Translation Philosophy

### Core Principles

1. **Accuracy over literal translation**: Convey meaning and intent, not word-for-word translation
2. **Technical precision**: Use established technical terminology consistently
3. **Cultural adaptation**: Adjust examples and references for target audience when appropriate
4. **Maintain brand voice**: Keep the friendly, accessible tone of AI Coding Club
5. **Preserve functionality**: Never translate code, URLs, or technical identifiers

### What NOT to Translate

- Brand names (ChatGPT, Claude, Cursor, GitHub, etc.)
- Code examples and snippets
- Function names and API endpoints
- File paths and URLs
- Technical acronyms (API, IDE, LLM, etc.)
- Project-specific stage names (can add translation in parentheses for clarity)

---

## Using the Glossary

### Glossary Location

The translation glossary is located at:
```
content/i18n/glossary.json
```

### Glossary Structure

The glossary contains 90+ English-Chinese term pairs organized into categories:

```json
{
  "version": "1.0.0",
  "terms": [
    {
      "category": "tool-names",
      "en": "ChatGPT",
      "zh": "ChatGPT",
      "notes": "Keep in English - brand name"
    },
    {
      "category": "programming-concepts",
      "en": "Frontend",
      "zh": "前端",
      "notes": "Standard translation"
    }
  ],
  "categories": {
    "tool-names": {
      "description": "Brand names of AI tools...",
      "translationGuideline": "Do not translate..."
    }
  }
}
```

### Categories

The glossary includes these categories:

1. **tool-names**: AI tools, IDEs, platforms (ChatGPT, Cursor, VS Code, etc.)
2. **programming-concepts**: General programming terms (Frontend, API, Database, etc.)
3. **ui-ux-terms**: Interface elements (Homepage, Search, Navigation, etc.)
4. **educational-terms**: Learning content terms (Tutorial, Course, Roadmap, etc.)
5. **ai-specific-terms**: AI/ML terminology (Prompt, LLM, Context window, etc.)
6. **action-verbs**: Common action verbs (Build, Create, Deploy, Learn, etc.)
7. **project-specific**: AI Coding Club specific terms (Vibecoding, Reality Check, etc.)

### How to Use the Glossary

#### Before Translation

1. **Review the glossary**: Familiarize yourself with standard translations
2. **Check category guidelines**: Understand the translation approach for each category
3. **Search for terms**: Use Ctrl+F to find terms in the glossary file

#### During Translation

1. **Lookup terms**: When encountering technical terms, check glossary first
2. **Follow notes**: Pay attention to the "notes" field for context-specific guidance
3. **Maintain consistency**: Always use the glossary translation, not variations

#### Example Usage

**English text:**
```markdown
Learn how to use ChatGPT and Claude for prompt engineering
to build your first frontend application.
```

**Checking glossary:**
- "ChatGPT" → Keep in English (tool-names)
- "Claude" → Keep in English (tool-names)
- "prompt engineering" → "提示词工程" (ai-specific-terms)
- "build" → "构建" (action-verbs)
- "frontend" → "前端" (programming-concepts)

**Correct translation:**
```markdown
学习如何使用 ChatGPT 和 Claude 进行提示词工程，构建你的第一个前端应用。
```

### Updating the Glossary

When you encounter new technical terms not in the glossary:

1. **Document the term**: Note it during translation
2. **Research standard translation**: Check established Chinese tech resources
3. **Propose addition**: Submit PR with glossary update
4. **Include context**: Add category and usage notes

**Example glossary addition:**
```json
{
  "category": "programming-concepts",
  "en": "Middleware",
  "zh": "中间件",
  "notes": "Standard translation in web development context"
}
```

---

## File Structure

### Markdown Content Translation

**English source files:**
```
content/docs/intro.md
content/blog/2025-10-31-welcome.md
content/docs/course/foundations/lesson-01.md
```

**Chinese translation files:**
```
content/i18n/zh/docusaurus-plugin-content-docs/current/intro.md
content/i18n/zh/docusaurus-plugin-content-blog/2025-10-31-welcome.md
content/i18n/zh/docusaurus-plugin-content-docs/current/course/foundations/lesson-01.md
```

**Key rules:**
- Maintain identical file names
- Preserve directory structure
- Keep file extensions unchanged
- Place in appropriate i18n plugin directory

### Component Text Translation

**Translation files for React components:**
```
i18n/zh/code.json                              # Custom components
i18n/zh/docusaurus-theme-classic/navbar.json  # Navigation bar
i18n/zh/docusaurus-theme-classic/footer.json  # Footer
i18n/zh/docusaurus-plugin-content-docs/current.json  # Docs metadata
```

**Component usage:**
```tsx
import Translate from '@docusaurus/Translate';

// In component
<Translate id="homepage.hero.title">
  Build Your First Script with AI in 30 Seconds
</Translate>

// In i18n/zh/code.json
{
  "homepage.hero.title": {
    "message": "30秒用AI创建你的第一个脚本"
  }
}
```

---

## Translation Workflow

### Step 1: Preparation

1. **Read the English source**: Understand context and purpose
2. **Review glossary**: Check for relevant technical terms
3. **Check existing translations**: Look at similar translated content for consistency

### Step 2: Translate Markdown Content

#### A. Setup Translation File (Automated)

**Using the translation-setup script (Recommended):**

```bash
# Automatically create translation file structure
npm run translation:setup content/docs/intro.md

# This will:
# 1. Create target i18n directory structure
# 2. Copy frontmatter from source file
# 3. Add translation placeholder comments
# 4. Preserve original content as reference
```

**Example output:**
```
🌐 Setting up translation file structure...

📄 Source file: content/docs/intro.md
📂 Content type: docs
🎯 Target path: content/i18n/zh/docusaurus-plugin-content-docs/current/intro.md
✅ Translation file created

🎉 Translation setup complete!
```

**Supported content types:**
- Documentation: `content/docs/`
- Blog posts: `content/blog/`
- Course lessons: `content/docs/course/`

**Manual alternative (if needed):**

```bash
# Example: Translating intro.md
mkdir -p content/i18n/zh/docusaurus-plugin-content-docs/current
cp content/docs/intro.md \
   content/i18n/zh/docusaurus-plugin-content-docs/current/intro.md
```

#### B. Translate Content

**Important**: Keep frontmatter keys in English, translate only values

```markdown
---
# ❌ WRONG - Don't translate keys
标题: 快速入门
sidebar_position: 1

# ✅ CORRECT - Translate values only
title: 快速入门
sidebar_position: 1
description: AI Coding Club 新手指南
---

# 欢迎来到AI Coding Club

这是您开始AI辅助编程之旅的地方...
```

#### C. Handle Special Elements

**Code blocks** - Do not translate:
```markdown
# ✅ CORRECT - Code stays in English
```python
def hello_world():
    print("Hello, World!")
```
```

**Links** - Update to localized version:
```markdown
# ❌ WRONG
[查看教程](/docs/tutorial)

# ✅ CORRECT
[查看教程](/zh/docs/tutorial)
```

**Images** - Update alt text only:
```markdown
# ❌ WRONG
![示例图片](/img/example.png)

# ✅ CORRECT
![示例图片](/img/example.png)
```

### Step 3: Translate Component Strings

For hardcoded text in React components:

1. **Wrap with Translate component:**
```tsx
// Before
<h1>AI Coding Tools</h1>

// After
import Translate from '@docusaurus/Translate';

<h1>
  <Translate id="tools.heading">AI Coding Tools</Translate>
</h1>
```

2. **Add translation to code.json:**
```json
{
  "tools.heading": {
    "message": "AI编程工具",
    "description": "Main heading for tools page"
  }
}
```

### Step 4: Verification

```bash
# Test translation locally
npm start
# Visit http://localhost:3000/zh/docs/intro

# Build and verify
npm run build
npm run serve
```

**Checklist:**
- [ ] Translation displays correctly
- [ ] Links work properly
- [ ] Images load correctly
- [ ] Code blocks render properly
- [ ] No broken links (build will fail if links broken)
- [ ] Language switcher works

### Step 5: Quality Review

Before submitting:
- [ ] Technical terms use glossary translations
- [ ] Tone matches AI Coding Club voice
- [ ] Grammar and spelling correct
- [ ] Links point to localized versions
- [ ] Frontmatter structure preserved
- [ ] No untranslated strings (except brand names, code)

---

## Quality Standards

### Technical Accuracy

**Use glossary consistently:**
```markdown
# ❌ WRONG - Inconsistent translations
使用 ChatGPT 和 Claude 进行提示工程
使用 ChatGPT 和 Claude 进行提示词工程化
使用 ChatGPT 和 Claude 做 prompt engineering

# ✅ CORRECT - Use glossary translation
使用 ChatGPT 和 Claude 进行提示词工程
```

### Natural Language Flow

**Adapt for Chinese readability:**
```markdown
# ❌ WRONG - Too literal
你将学习如何去使用AI工具来进行编程

# ✅ CORRECT - Natural Chinese
你将学习如何使用AI工具编程
```

### Preserve Meaning

**Keep educational intent:**
```markdown
# Original
This hands-on demo shows how AI can automate tasks in 30 seconds.

# ❌ WRONG - Loses impact
这个演示展示AI可以自动化任务在30秒内

# ✅ CORRECT - Preserves impact
这个实战演示展示了AI如何在30秒内自动化任务
```

### Brand Voice

Maintain AI Coding Club's friendly, accessible, beginner-focused tone:

```markdown
# ❌ TOO FORMAL
本平台致力于为初学者提供基于人工智能的编程教学服务

# ✅ FRIENDLY & ACCESSIBLE
我们帮助编程新手，用AI来学习编程
```

---

## Common Patterns

### Pattern 1: Tool Names + Actions

**Template:**
```
使用 [Tool Name] [进行/来] [Action]
```

**Examples:**
- "Use ChatGPT for prompt engineering" → "使用 ChatGPT 进行提示词工程"
- "Build with Cursor" → "使用 Cursor 构建"
- "Deploy to GitHub" → "部署到 GitHub"

### Pattern 2: Learning Objectives

**Template:**
```
学习如何 [Action] / 了解 [Concept]
```

**Examples:**
- "Learn how to debug" → "学习如何调试"
- "Understand APIs" → "了解 API"
- "Master frontend development" → "掌握前端开发"

### Pattern 3: Call to Action (CTA)

**Template:**
```
[Action Verb] → / 查看[Content]
```

**Examples:**
- "Get Started →" → "开始 →"
- "View Demo →" → "查看演示 →"
- "Learn More →" → "了解更多 →"

### Pattern 4: Descriptions with Technical Terms

**Keep English terms, add Chinese explanation:**
```markdown
# Pattern
[English Term]([Chinese explanation]) - [Description in Chinese]

# Examples
- "API (应用程序接口) - 让程序之间互相通信的方式"
- "Frontend (前端) - 用户直接看到和交互的界面部分"
```

### Pattern 5: Lists with Actions

**Maintain parallel structure:**
```markdown
# English
- Build your first app
- Deploy to production
- Share with users

# Chinese - Keep parallel structure
- 构建你的第一个应用
- 部署到生产环境
- 分享给用户
```

---

## Troubleshooting

### Issue: Build Fails After Translation

**Possible causes:**
1. Broken internal links
2. Incorrect file structure
3. Invalid frontmatter syntax

**Solution:**
```bash
# Check build output for errors
npm run build 2>&1 | grep -i "error"

# Common fixes:
# - Update links to include /zh/ prefix
# - Verify frontmatter YAML syntax
# - Check file is in correct i18n directory
```

### Issue: Translation Not Showing

**Possible causes:**
1. File in wrong directory
2. Docusaurus cache issue
3. Missing frontmatter

**Solution:**
```bash
# Clear cache and rebuild
npm run clear
npm start

# Verify file location
# Should be: content/i18n/zh/docusaurus-plugin-content-docs/current/...
```

### Issue: Search Not Working in Chinese

**Note:** This is expected behavior in dev mode.

**Solution:**
```bash
# Search only works in production build
npm run build
npm run serve

# Visit http://localhost:3000/zh/
# Search should work now
```

### Issue: Mixed Languages Appearing

**Possible causes:**
1. Incomplete translation
2. Hardcoded strings without Translate component
3. Missing translation in code.json

**Solution:**
1. Check if all strings use `<Translate>` component
2. Verify all translation keys exist in i18n/zh/code.json
3. Run: `npm run write-translations -- --locale zh` to generate missing keys

---

## Best Practices Summary

### Do's ✅

- **Do** check the glossary before translating technical terms
- **Do** maintain consistent terminology throughout
- **Do** preserve frontmatter structure (keys in English)
- **Do** update internal links to localized versions
- **Do** keep code examples in English
- **Do** test translations locally before committing
- **Do** use natural, conversational Chinese
- **Do** preserve the friendly, beginner-focused tone

### Don'ts ❌

- **Don't** translate brand names or tool names
- **Don't** translate code, function names, or APIs
- **Don't** create new technical terms without glossary check
- **Don't** translate URLs or file paths
- **Don't** use inconsistent terminology
- **Don't** over-formalize the language
- **Don't** literal word-for-word translation
- **Don't** skip quality verification

---

## Resources

### Internal Documentation

- **Glossary**: `/content/i18n/glossary.json`
- **Translation Plan**: `/I18N_TRANSLATION_PLAN.md`
- **Existing Translations**: `/content/i18n/zh/` and `/i18n/zh/`

### Docusaurus Documentation

- [Docusaurus i18n Guide](https://docusaurus.io/docs/i18n/introduction)
- [i18n Tutorial](https://docusaurus.io/docs/i18n/tutorial)
- [Translation File Structure](https://docusaurus.io/docs/i18n/introduction#translation-files-location)

### Tools

- **Translation setup**: `npm run translation:setup <file-path>` - Automate translation file creation
- **Glossary search**: Use Ctrl+F in glossary.json
- **Translation check**: `npm run check:translations`
- **Generate templates**: `npm run write-translations -- --locale zh`

#### Translation Setup Script

The `translation:setup` script automates the tedious process of creating translation files:

```bash
# Usage
npm run translation:setup content/docs/intro.md

# What it does:
# 1. Validates source file exists and is in content/ directory
# 2. Determines content type (docs/blog/course)
# 3. Creates target i18n directory structure
# 4. Copies frontmatter and preserves structure
# 5. Adds translation placeholder with original content as reference
```

**Features:**
- Automatic path mapping based on content type
- Preserves frontmatter structure
- Includes original content as commented reference
- Error handling for invalid paths
- Shows helpful next steps

**Path mappings:**
- `content/docs/` → `content/i18n/zh/docusaurus-plugin-content-docs/current/`
- `content/blog/` → `content/i18n/zh/docusaurus-plugin-content-blog/`

**Script location:** `/scripts/translation-setup.js`
**Tests:** Run `npm run test:translation-setup` to verify functionality

---

## Getting Help

### For Translation Questions

1. Check this guide and the glossary
2. Review existing translations for similar content
3. Ask in project Discord/Slack (if available)
4. Create GitHub issue with `i18n` label

### For Technical Issues

1. Check [Troubleshooting](#troubleshooting) section
2. Verify file structure and syntax
3. Test with production build
4. Create GitHub issue with build error details

---

## Version History

- **1.1** (2025-11-03): Added translation-setup automation script
  - Implemented `translation:setup` script for automated file creation
  - Added 17 comprehensive tests for translation workflow
  - Updated workflow documentation with automated approach
  - Added script documentation to Tools section
- **1.0** (2025-11-03): Initial translation guide with glossary integration
  - Created comprehensive glossary with 90+ terms
  - Established translation workflow
  - Added quality standards and common patterns
  - Documented best practices and troubleshooting

---

**Maintained by:** AI Coding Club Team
**Questions?** Create an issue with the `i18n` label
