# Content Workflow: English-First Strategy

## 🎯 Core Philosophy

**All content is created in English first, then translated to other languages.**

### Why English-First?

1. **AI resources are primarily in English** - OpenAI, Anthropic, Google, Cursor docs
2. **Technical accuracy** - AI terminology is most precise in English
3. **Global reach** - English speakers: 1.5B+ vs Chinese: 1.2B
4. **Translation efficiency** - EN→ZH easier than ZH→EN (more reference materials)
5. **SEO advantage** - Higher search volume for English AI coding terms

## 📝 Content Creation Workflow

### Stage 1: Research & Collection (English Sources)

```
Sources Priority:
1. Official documentation (OpenAI, Anthropic, Cursor)
2. Research papers (arXiv, Google Research)
3. Community discussions (Reddit, HN, GitHub)
4. Video content (YouTube tech channels)
5. Blog posts (high-authority only)

Tools:
- Claude/GPT-4 for summarization
- Perplexity for research
- Notion/Obsidian for note-taking
```

### Stage 2: Content Creation (English)

**Process:**
1. Outline the tutorial structure in English
2. Write the full content in English
   - Use AI assistance (Claude Code, ChatGPT)
   - Focus on clarity and precision
   - Include code examples with comments
3. Review and edit
   - Technical accuracy check
   - Grammar check (Grammarly, LanguageTool)
   - Readability check (Hemingway Editor)

**File Structure:**
```
docs/
├── tutorial-name.md         # English (master version)
└── tutorial-name.zh.md      # Will be created in Stage 3
```

**Content Template:**
```markdown
---
title: Tutorial Title
description: Brief description for SEO
keywords: [ai, coding, prompt engineering]
---

# Tutorial Title

## What You'll Learn
- Learning objective 1
- Learning objective 2

## Prerequisites
- Prerequisite 1
- Prerequisite 2

## Step 1: Introduction
[Content in English...]

## Step 2: Implementation
[Code examples with comments...]

## Conclusion
[Summary and next steps...]
```

### Stage 3: Translation (English → Chinese)

**Translation Methods:**

#### Method A: AI-Assisted Translation (Recommended)
```bash
# Use Claude/GPT-4 with specialized prompt
# See docs/internal/i18n/TRANSLATION_GUIDE.md for detailed prompts
```

**Example Prompt:**
```
You are a professional translator specializing in technical documentation.
Translate the following AI coding tutorial from English to Chinese.

Requirements:
1. Maintain technical terms in English with Chinese explanation in parentheses
   Example: "Prompt Engineering (提示词工程)"
2. Keep code examples unchanged
3. Adapt idioms and metaphors to Chinese culture
4. Maintain the same markdown structure
5. Preserve all links and formatting

Source text:
[Paste English content here]
```

#### Method B: Human Translation (For Critical Content)
1. Native Chinese speaker translates
2. Technical reviewer validates accuracy
3. Editor polishes the language

**Quality Checklist:**
- [ ] Technical terms translated correctly
- [ ] Code examples unchanged
- [ ] Links work properly
- [ ] Formatting preserved
- [ ] Natural Chinese expression
- [ ] SEO keywords adapted

### Stage 4: Review & Publish

1. **Side-by-side comparison**
   - English version (master)
   - Chinese version (translation)
   - Ensure consistency

2. **Build test**
   ```bash
   npm run build
   # Check for broken links, missing translations
   ```

3. **Commit with clear message**
   ```bash
   git add .
   git commit -m "Add: [Tutorial Name] in EN and ZH"
   ```

## 🌍 Future Language Expansion

### Expansion Priority (Based on Market Demand)

| Language | Target Date | Market Size | Community Lead |
|----------|-------------|-------------|----------------|
| Spanish  | Month 6     | 500M        | TBD            |
| Portuguese| Month 8    | 250M        | TBD            |
| Hindi    | Month 10    | 600M        | TBD            |
| Japanese | Month 12    | 120M        | TBD            |

### Adding a New Language

1. **Update config**
   ```typescript
   // docusaurus.config.ts
   locales: ['en', 'zh', 'es'], // Add new language
   ```

2. **Create language directory**
   ```bash
   mkdir -p i18n/es/docusaurus-plugin-content-docs/current
   mkdir -p i18n/es/docusaurus-plugin-content-blog
   ```

3. **Translate core content**
   - Homepage
   - Navigation
   - Top 5 tutorials

4. **Find community translator**
   - Native speaker
   - Technical background
   - Ongoing commitment

5. **Launch & iterate**

## 🔄 Content Update Workflow

When updating English content:

1. **Update English version first** (master)
2. **Mark translations as outdated**
   ```markdown
   <!-- Translation outdated: last updated 2024-01-15 -->
   ```
3. **Update translations** (within 1 week)
4. **Remove outdated marker**

## 📊 Content Quality Standards

### English Content (Master)
- [ ] Technically accurate (verified with official docs)
- [ ] Clear and concise (reading level: 8th grade)
- [ ] Code examples tested and working
- [ ] SEO optimized (meta description, keywords)
- [ ] Grammar checked (Grammarly score > 90)

### Chinese Translation
- [ ] Technical terms handled correctly
- [ ] Natural Chinese expression
- [ ] Cultural adaptation where needed
- [ ] Same information depth as English
- [ ] SEO keywords localized

## 🛠 Tools & Resources

### Content Creation
- **Writing**: Claude Code, ChatGPT, Notion
- **Code Testing**: VS Code, online REPLs
- **Diagrams**: Excalidraw, Mermaid

### Translation
- **AI Translation**: Claude, GPT-4, DeepL
- **Human Review**: Native speaker network
- **Terminology**: Maintain glossary in `/docs/glossary.md`

### Quality Assurance
- **Grammar**: Grammarly, LanguageTool
- **Readability**: Hemingway Editor
- **SEO**: Ahrefs, Google Search Console
- **Build**: Docusaurus build warnings

## 📚 Terminology Guidelines

### Keep in English + Chinese Explanation
- Prompt Engineering (提示词工程)
- AI Coding (AI辅助编程)
- Large Language Model (大语言模型/LLM)
- GitHub Copilot (保持英文)

### Translate Completely
- Tutorial → 教程
- Example → 示例
- Step-by-step → 分步指南

### Glossary
Maintain a central glossary at `/docs/glossary.md`:
```markdown
| English | 中文 | Notes |
|---------|------|-------|
| Prompt Engineering | 提示词工程 | Keep EN term in first mention |
| Token | 令牌/Token | Can use either |
```

## 🚀 Quick Start for Contributors

1. **Find English source material** (OpenAI docs, Anthropic blog, etc.)
2. **Create English tutorial** using template above
3. **Submit PR for English version only**
4. **Translation team will handle Chinese version**
5. **Review both versions together**

## 📞 Questions?

- Open a [Discussion](https://github.com/IsaacZhaoo/aicodingclub/discussions)
- Tag `@IsaacZhaoo` for content strategy questions
- Join our Discord `#content-creation` channel

---

**Remember**: Quality over quantity. One excellent English tutorial properly translated to Chinese is worth more than ten rushed bilingual posts.
