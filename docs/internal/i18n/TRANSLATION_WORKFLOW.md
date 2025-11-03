# Translation Workflow

**Version:** 1.0
**Last Updated:** 2025-11-04
**Status:** Active

## Overview

This guide walks translators through the day-to-day process of translating content for AI Coding Club. It covers the complete workflow from setup through verification, using the glossary, automation tools, and quality checks.

## Table of Contents

1. [Prerequisites](#prerequisites)
2. [Workflow Overview](#workflow-overview)
3. [Step-by-Step Process](#step-by-step-process)
4. [Using Translation Tools](#using-translation-tools)
5. [Quality Assurance](#quality-assurance)
6. [Committing Translations](#committing-translations)
7. [Common Workflows](#common-workflows)
8. [Troubleshooting](#troubleshooting)

---

## Prerequisites

Before you start translating, ensure you have:

### Required Setup

1. **Node.js and npm** installed
   ```bash
   node --version  # Should be v18+
   npm --version
   ```

2. **Repository cloned with submodules**
   ```bash
   git clone --recurse-submodules https://github.com/IsaacZhaoo/aiCodingClub.git
   cd aiCodingClub
   npm install
   ```

3. **Development environment ready**
   ```bash
   npm start  # Should run without errors
   ```

### Optional but Recommended

- **OpenAI or Anthropic API key** for AI-assisted translation (set in `.env`)
- **Text editor with Markdown support** (VS Code, Sublime, etc.)
- **Git knowledge** for committing translations

---

## Workflow Overview

The typical translation workflow follows these phases:

```
1. Identify File      List files that need translation
   ↓
2. Setup File         Create translation file structure
   ↓
3. Translate          Translate the content
   ↓
4. Use Glossary       Ensure consistent terminology
   ↓
5. Validate           Check quality and links
   ↓
6. Test               Verify in dev/prod build
   ↓
7. Commit            Push translations to repository
```

---

## Step-by-Step Process

### Phase 1: Identify Files to Translate

#### Option A: Check Current Coverage

```bash
# See which files still need translation
npm run check:translations

# Output shows priority levels:
# P0 (Critical) - Core content like intro, roadmap, foundations
# P1 (High)     - Popular tools, essential lessons
# P2 (Medium)   - Secondary content
# P3 (Low)      - Optional content
```

#### Option B: Pick from Missing Files

From the coverage report, select a file to translate:
- Start with **P0** files (if any remain) for critical content
- Then **P1** files for high-impact content
- P2/P3 files for broader coverage

#### Option C: Translate Specific Content Type

**Translate a single blog post:**
```bash
# Find the file
ls content/blog/2025-10-*.md

# Pick one to translate (e.g., 2025-10-31-ai-coding-philosophy.md)
```

**Translate a course lesson:**
```bash
# Find lessons in specific phase (e.g., foundations)
ls content/docs/course/01-foundations/

# Pick a lesson (e.g., lesson-01.md)
```

**Translate a tools page:**
```bash
# Find tool documentation
ls content/docs/tools/

# Pick a tool (e.g., ai-tools-comparison.mdx)
```

### Phase 2: Setup Translation File

#### Automatic Setup (Recommended)

Use the `translation:setup` script to create the file structure:

```bash
# For a specific file
npm run translation:setup content/docs/course/01-foundations/lesson-01.md

# Script will output:
# 🌐 Setting up translation file structure...
# 📄 Source file: content/docs/course/01-foundations/lesson-01.md
# 📂 Content type: docs (course)
# 🎯 Target path: content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md
# ✅ Translation file created
# 🎉 Translation setup complete!
```

The script automatically:
- Creates the correct directory structure
- Copies the source file as a reference
- Preserves the frontmatter
- Shows the target file path

#### Manual Setup (If Needed)

```bash
# Identify the source path
SOURCE="content/docs/course/01-foundations/lesson-01.md"

# Determine content type (docs, blog, etc.)
# For docs: content/i18n/zh/docusaurus-plugin-content-docs/current/
# For blog: content/i18n/zh/docusaurus-plugin-content-blog/

# Create target directory
mkdir -p "content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/"

# Copy source as reference
cp "$SOURCE" "content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md"
```

### Phase 3: Translate the Content

#### A. Open the Translation File

```bash
# Use your favorite editor
code "content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md"
```

#### B. Keep Frontmatter (File Metadata)

The frontmatter (YAML at the top) has **English keys** and **translated values**:

```markdown
---
title: 快速入门指南        # Translate only the value
description: 学习AI编程基础 # Keep English keys
sidebar_position: 1         # Don't change
---
```

#### C. Translate the Content

Work through the file section by section:

**Headings:**
```markdown
# ❌ WRONG
# 快速入门
# ✅ CORRECT
# 快速入门指南
```

**Paragraphs:**
```markdown
# ❌ Too literal
这将使你能够编写代码通过使用AI工具。

# ✅ Natural flow
这将让你学会用AI工具编写代码。
```

**Lists (maintain structure):**
```markdown
- Build your first app
- Deploy to production
- Share with users

# Becomes:
- 构建你的第一个应用
- 部署到生产环境
- 分享给用户
```

### Phase 4: Use the Glossary

#### A. Consult the Glossary

Before translating technical terms, check the glossary:

```bash
# Open the glossary file
code content/i18n/glossary.json

# Or search for specific terms
grep -A 2 '"en": "ChatGPT"' content/i18n/glossary.json
```

#### B. Apply Glossary Terms Consistently

When you encounter a term in the English content:

1. **Search in glossary** for the exact term
2. **Use the zh value** provided in the glossary
3. **Keep consistency** with all other occurrences

**Example:**
```markdown
# Original English
Learn how to use ChatGPT and Claude for prompt engineering.

# Step 1: Check glossary
# ChatGPT → "ChatGPT" (don't translate - brand name)
# Claude → "Claude" (don't translate - brand name)
# prompt engineering → "提示词工程" (from glossary)

# Correct translation
学习如何使用 ChatGPT 和 Claude 进行提示词工程。
```

#### C. Handle Missing Terms

If you encounter a term not in the glossary:

1. **Document it**: Note the term and context
2. **Create a reasonable translation**: Use established resources
3. **Propose an addition**: Add to glossary in future PR
4. **Stay consistent**: Use the same translation throughout the file

**Example of term not in glossary:**
```
English: "middleware"
Not found in glossary.json
Research: Standard Chinese tech term is "中间件"
Use in translation: "中间件" consistently
Later: Propose adding to glossary
```

### Phase 5: Handle Special Elements

#### Code Blocks (Don't Translate)

```markdown
# ✅ CORRECT - Keep code in English
```python
def hello_world():
    print("Hello, World!")
```

# Translate only the explanation:
这个函数打印出"Hello, World!"。
```

#### Internal Links (Add /zh/)

For links to other AI Coding Club pages:

```markdown
# ❌ WRONG - Missing /zh/
[查看教程](/docs/tutorial)

# ✅ CORRECT - Added /zh/
[查看教程](/zh/docs/tutorial)
```

#### External Links (Keep As-Is)

```markdown
# ✅ CORRECT - Don't change external links
[Learn more](https://example.com)
[中文阅读](https://chinese-example.com)
```

#### Images (Translate Alt Text Only)

```markdown
# ❌ WRONG
![示例图片](/img/example.png)

# ✅ CORRECT - Alt text translated, image path same
![示例图片](/img/example.png)
```

#### Callouts and Special Markdown

```markdown
# ✅ CORRECT - Translate the content
> 这是一个重要提示
> 请仔细阅读

:::info 重要
这是一条信息框。
:::
```

### Phase 6: Validate Quality

#### A. Check Consistency

```bash
# Verify file syntax is valid
npm run build

# If there are errors, fix them and rebuild
```

#### B. Review Against Original

Compare your translation with the English source:

1. Have you translated everything (except code, brand names)?
2. Is the tone friendly and beginner-focused?
3. Are technical terms from the glossary?
4. Do links point to `/zh/` versions?
5. Is the meaning preserved (not just literal)?

#### C. Spelling and Grammar

- Use a spell checker if available
- Read aloud to check flow
- Ask a native Chinese speaker if possible

### Phase 7: Test the Translation

#### A. Local Testing

```bash
# Start dev server
npm start

# Navigate to the translated page
# Example: http://localhost:3000/zh/docs/course/01-foundations/lesson-01/

# Check:
# [ ] Page loads without errors
# [ ] Text appears correctly
# [ ] Links work (especially /zh/ links)
# [ ] Images display
# [ ] Code blocks render properly
# [ ] Language switcher works
```

#### B. Production Build Testing

```bash
# Build for production (includes search indexing)
npm run build

# Serve the production build locally
npm run serve

# Test at http://localhost:3000/zh/
# Verify search indexing works for Chinese terms
```

---

## Using Translation Tools

### Tool 1: translation:setup Script

**Purpose:** Automatically create translation file structure

**Usage:**
```bash
npm run translation:setup <path-to-source-file>
```

**Example:**
```bash
npm run translation:setup content/blog/2025-10-31-ai-coding-philosophy.md
```

**What it does:**
- Creates target i18n directory structure
- Copies source file (preserving frontmatter)
- Adds helpful comments about what to translate
- Outputs the target file path

**Supported file types:**
- `content/docs/` → docs
- `content/blog/` → blog
- `content/docs/course/` → docs (course)

### Tool 2: check-translations.js Script

**Purpose:** Report translation coverage and identify missing files

**Usage:**
```bash
npm run check:translations
```

**Output shows:**
- Coverage by content type (Docs, Blog, Course, Tools)
- Priority-based coverage (P0, P1, P2, P3)
- Percentage complete
- List of missing files
- Clear next steps

**Example output:**
```
📊 ZH Translation Coverage:

❌ Blog    : 0% (0/3)
✅ Docs    : 100% (15/15)
🟡 Course  : 45% (17/37)
⚠️  Tools   : 79% (19/24)

🎯 Priority Coverage:
✅ P0 (Critical): 100% (7/7)
🔴 P1 (High)    : 27% (15/55)
```

### Tool 3: ai-translate.js Script (Optional)

**Purpose:** Generate AI-assisted translation drafts (requires API key)

**Setup:**
```bash
# Create .env file with API key
cp .env.example .env

# Add your API key:
# OPENAI_API_KEY=sk-xxx...
# OR
# ANTHROPIC_API_KEY=sk-ant-xxx...
```

**Usage:**
```bash
# Generate translation draft for a single file
npm run ai:translate content/docs/intro.md

# The script will:
# 1. Read the English source
# 2. Use AI to generate Chinese translation
# 3. Save to the correct i18n path
# 4. Show which parts were translated
# 5. Ask for review before final save
```

**Important Notes:**
- AI translations are **drafts** - always review and edit
- Still use the glossary for consistency
- This tool saves time but doesn't replace human review
- Costs depend on file size and API chosen

---

## Quality Assurance

### Pre-Commit Checklist

Before pushing your translation, verify:

- [ ] **Completeness**: All text translated (except code/brand names)
- [ ] **Glossary**: Technical terms use glossary translations
- [ ] **Links**: Internal links point to `/zh/` versions
- [ ] **Tone**: Maintains friendly, beginner-focused voice
- [ ] **Grammar**: No spelling or grammar errors
- [ ] **Formatting**: Markdown syntax preserved
- [ ] **Images**: Alt text translated, paths unchanged
- [ ] **Code**: Code blocks unchanged, explanations translated
- [ ] **Build**: `npm run build` passes without errors
- [ ] **Test**: Dev server shows correct translation

### Common Issues and Fixes

**Issue: Page doesn't display**
```bash
# Clear cache and rebuild
npm run clear
npm run build
```

**Issue: Links are broken**
- Check for `/zh/` prefix on internal links
- Verify the target page exists
- Test in production build: `npm run serve`

**Issue: Text looks wrong in browser**
- Check if you're on the zh locale page
- Verify frontmatter syntax (YAML)
- Look for incomplete translations

**Issue: Inconsistent terminology**
- Search the file for all instances
- Replace with glossary version
- Check other translated files for consistency

---

## Committing Translations

### Prepare Your Commits

**For a single translated file:**
```bash
# Stage the translation
cd content
git add i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md

# Commit with descriptive message
git commit -m "i18n: Translate course lesson 01 to Chinese"

# Push to content repo
git push origin main
```

**For multiple files:**
```bash
cd content

# Stage all translations
git add i18n/

# Commit by category for clarity
git commit -m "i18n: Translate 5 blog posts to Chinese"

# Push
git push origin main
```

**Update main repo reference:**
```bash
# Go back to main repo
cd ..

# Update submodule reference
git add content
git commit -m "Update content submodule: Add Chinese translations"
git push
```

### Commit Message Format

Follow this format for clear history:

```
i18n: [Scope] [What was translated]

Examples:
- i18n: Translate course lesson 01 (foundations)
- i18n: Translate 3 blog posts about AI philosophy
- i18n: Translate tools comparison page
- i18n: Translate roadmap documentation
```

---

## Common Workflows

### Workflow A: Translate a Single Blog Post

```bash
# 1. Check coverage to find a blog post to translate
npm run check:translations

# 2. Setup the file structure
npm run translation:setup content/blog/2025-10-31-ai-coding-philosophy.md

# 3. Open the created file
code content/i18n/zh/docusaurus-plugin-content-blog/2025-10-31-ai-coding-philosophy.md

# 4. Translate it (use glossary for consistency)

# 5. Test locally
npm start
# Visit http://localhost:3000/zh/blog/2025-10-31-ai-coding-philosophy/

# 6. Build and test production version
npm run build
npm run serve

# 7. Commit (from content directory)
cd content
git add i18n/
git commit -m "i18n: Translate AI coding philosophy blog post"
git push origin main

# 8. Update main repo
cd ..
git add content
git commit -m "Update content: Add blog post translation"
git push
```

### Workflow B: Translate a Course Lesson

```bash
# 1. Navigate to content directory
cd content

# 2. Check course lesson files
ls docs/course/01-foundations/

# 3. Go back and setup
cd ..
npm run translation:setup content/docs/course/01-foundations/lesson-01.md

# 4. Translate (usually longer than blog posts)
code content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md

# 5. Test thoroughly
npm start
# Visit http://localhost:3000/zh/docs/course/01-foundations/lesson-01/

# 6. Verify all links work (especially navigation to next lesson)

# 7. Commit
cd content
git add i18n/
git commit -m "i18n: Translate course lesson 01 - foundations phase"
git push

# 8. Update main repo reference
cd ..
git add content
git commit -m "Update content: Add lesson translation"
git push
```

### Workflow C: Batch Translate Tool Pages

```bash
# 1. Check which tool pages need translation
npm run check:translations

# 2. List available tools
ls content/docs/tools/

# 3. Setup multiple files
npm run translation:setup content/docs/tools/chatgpt-guide.md
npm run translation:setup content/docs/tools/claude-guide.md
npm run translation:setup content/docs/tools/cursor-guide.md

# 4. Translate each file
code content/i18n/zh/docusaurus-plugin-content-docs/current/tools/chatgpt-guide.md
# (repeat for each tool)

# 5. Test all tools pages
npm start
# Visit http://localhost:3000/zh/docs/tools/

# 6. Commit as batch
cd content
git add i18n/zh/docusaurus-plugin-content-docs/current/tools/
git commit -m "i18n: Translate tool documentation (5 pages)"
git push

# 7. Update main repo
cd ..
git add content
git commit -m "Update content: Add tool documentation translations"
git push
```

---

## Troubleshooting

### Build Fails After Translation

**Symptom:** `npm run build` fails with errors

**Solution:**
1. Check the error message for the file name
2. Verify the file is in the correct directory
3. Check frontmatter YAML syntax (no missing colons)
4. Look for broken links (should have `/zh/` prefix)

**Debug:**
```bash
# Clear cache
npm run clear

# Try building again with verbose output
npm run build 2>&1 | grep -A 5 "error"
```

### Translation Not Showing on Page

**Symptom:** Page shows English instead of Chinese

**Solution:**
1. Verify you're on the `/zh/` version of the page
2. Check the file is in the correct i18n directory
3. Clear browser cache and refresh
4. Try `npm run clear` and restart dev server

**Debug:**
```bash
# Verify file exists at correct path
ls "content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md"

# Check file is not empty
wc -l "content/i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/lesson-01.md"
```

### Search Not Working in Chinese

**Symptom:** Full-text search doesn't find Chinese content

**Note:** This is expected behavior. Search only works in production builds.

**Solution:**
```bash
# Search only works after production build
npm run build

# Then serve the build
npm run serve

# Visit http://localhost:3000/zh/ and try search
```

### Glossary Term Not Found

**Symptom:** You encounter a technical term not in the glossary

**Solution:**
1. Research the term in established sources (Wikipedia, tech sites, etc.)
2. Use a reasonable translation
3. Stay consistent with that translation
4. Propose adding it to glossary in a future PR

**Example:**
```
Term: "microservices"
Glossary check: Not found
Research: Standard translation is "微服务"
Use: "微服务" consistently in this file
Propose: Add to glossary later
```

### Merge Conflicts in i18n Files

**Symptom:** Git merge conflict when pulling latest translations

**Solution:**
```bash
# Update submodules to latest
git submodule update --remote content

# Or resolve manually and then rebuild
npm run clear
npm run build
```

---

## Resources

### Glossary Reference
- **Location**: `content/i18n/glossary.json`
- **Format**: JSON with English-Chinese term pairs
- **Categories**: 7 categories (tool-names, programming-concepts, etc.)

### Translation Guide
- **Location**: `content/docs/internal/i18n/TRANSLATION_GUIDE.md`
- **Content**: Comprehensive translation philosophy and best practices

### Docusaurus i18n Documentation
- [Docusaurus i18n Guide](https://docusaurus.io/docs/i18n/introduction)
- [File Location Convention](https://docusaurus.io/docs/i18n/introduction#translation-files-location)
- [Tutorial](https://docusaurus.io/docs/i18n/tutorial)

### AI Translation Tools
- [OpenAI API Documentation](https://platform.openai.com/docs)
- [Anthropic Claude API](https://docs.anthropic.com/)
- [Local AI Translation with Ollama](https://ollama.ai/)

---

## Getting Help

**For translation questions:**
1. Check the Glossary (`content/i18n/glossary.json`)
2. Review TRANSLATION_GUIDE.md for detailed guidance
3. Look at existing translations for similar content
4. Create a GitHub issue with `i18n` label

**For technical issues:**
1. Check the [Troubleshooting](#troubleshooting) section
2. Run `npm run build` to identify specific errors
3. Check that files are in correct i18n directories
4. Create GitHub issue with build error details

**For workflow questions:**
1. Refer back to this document
2. Check common workflows section
3. Ask maintainers for clarification

---

## Quick Reference: Command Summary

```bash
# Check translation status
npm run check:translations

# Setup translation file structure
npm run translation:setup <file-path>

# Translate with AI assistance (requires API key)
npm run ai:translate <file-path>

# Test locally
npm start

# Build for production
npm run build

# Serve production build locally
npm run serve

# Clear Docusaurus cache
npm run clear

# Run translation script tests
npm run test:translation-setup
```

---

**Maintained by:** AI Coding Club Team
**Questions?** Create an issue with `i18n` label or check TRANSLATION_GUIDE.md
