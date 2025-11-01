# AI Coding Club: Content Reference & Patterns

## Quick Navigation

All content files are in `/home/zhao/workspace4work/aicodingclub-website/docs/`

```
docs/
├── intro.md                          # Welcome page (learning stages overview)
├── ai-coding-roadmap.mdx             # 36-week structured learning path
├── prompt-engineering-101.mdx        # 5 core prompt templates (learning resource)
├── csv-to-markdown-demo.mdx          # Interactive 30-second demo (first "aha!")
│
├── stages/                           # Learning progression (3 stages)
│   ├── stage0-vibecoding.md          # Build immediately with AI
│   ├── stage1-reality-check.md       # Understand AI limitations
│   └── stage2-context.md             # Master architecture & context
│
├── tools/
│   └── ai-tools-comparison.md        # 10 tools reviewed (opinionated)
│
├── community/                        # Placeholder (empty, future section)
└── experts/                          # Placeholder (empty, future section)
```

## Resource Annotation Template

Every external resource in Stages follows this pattern:

```markdown
## [Number]. **[Link Text with Full URL]**
   - *Why recommended:* [Relevance + positioning for this stage]
   - Category: [Type of content]
   - Duration: [Time commitment if applicable]
   - Platform: [Web/Desktop/IDE/etc.]
```

**Example from Stage 0:**
```markdown
1. **[Fireship: I built 10 web apps... with AI (in 14 minutes)](https://www.youtube.com/watch?v=UG3YC_jqPDg)**
   - *Why recommended:* Fast-paced demonstration showing what's possible with AI coding - perfect motivation for beginners
   - Category: Web Development
   - Duration: 14 minutes
```

## Stage Structure Template

Each stage file follows this pattern:

```markdown
# Stage [N]: [Name]

**[Tagline/Subtitle]**

## Why This Stage Matters
[Explains the transition/motivation]

## What You'll Learn
[Bulleted learning outcomes]

## Key Concepts
### [Concept 1]
- Bullet points
### [Concept 2]
- Bullet points

## Recommended Resources
[10-ish resources with annotations]

## Tips for [Stage] Success
[Practical advice, typically 4-5 subsections]

## What's Next?
[Directional pointer to next stage]

**Need help?** Check our [Resources](/resources) page for additional learning materials!
```

## Content Tone Examples

**From Intro (Motivational):**
> "AI Coding Club is a carefully curated platform designed to help you learn coding with AI assistance. We cut through the noise and provide only the best resources, guides, and tools to accelerate your learning journey."

**From Stage 1 (Realistic):**
> "After the excitement of vibecoding, it's crucial to understand what AI can and cannot do. This stage helps you develop realistic expectations and avoid common pitfalls."

**From Tools Comparison (Opinionated):**
> "Our Take: If you're serious about AI-assisted coding, Cursor is currently the gold standard. The context awareness and composer features make complex refactoring tasks significantly easier."

**From Blog (Philosophical):**
> "AI won't replace you. But programmers who use AI will replace those who don't."

## Design Patterns

### Call-to-Action Pattern
- Links at END of sections: `[Learn More →](/path)`
- Action verbs: "Ready to begin?", "Get Started", "Explore"
- Clear next steps

### Progressive Disclosure Pattern
- Summary first, details in sections
- Stages increase in sophistication (motivation → discernment → mastery)
- Each content builds on previous

### Accessibility Pattern
- No jargon or explained when used
- Time commitments explicit (36 weeks, 2-5 hours/day, 30 seconds)
- Multiple learning modalities (video, interactive, project-based, text)

### Curation Pattern
- Not comprehensive (25 resources, not 100+)
- Each resource: *Why recommended* (not just a link)
- Clear positioning (best for X, duration, platform)

### Comparison Pattern
- Opinionated recommendations ("Our Take")
- Realistic messaging (not "best", but "best FOR...")
- Decision framework (Price, Features, Use Case)

## Key Numbers

- **3** stages (progression)
- **4** main sections in roadmap (Foundations, Building Projects, Web Development, Advanced)
- **5** core prompt templates
- **6-10** portfolio projects expected
- **8-10** resources per stage
- **10** AI tools compared
- **25** total curated resources (approximate)
- **36** weeks to job-ready
- **2-5** hours/day time commitment

## Narrative Arc

1. **Stage 0**: "You can build something TODAY" (remove fear)
2. **Stage 1**: "But understand what you're doing" (build judgment)
3. **Stage 2**: "Master the craft and go deeper" (sophistication)

Then: **Tutorials** (guided implementation), **Tools** (equipment choice), **Community** (peer support)

## Missing Narrative Arcs (Content Gaps)

These stories aren't told yet:

1. **"Debug Like a Pro"** - How to work with AI when something breaks
2. **"From Portfolio to Interview"** - Career progression narrative
3. **"Domain Deep Dives"** - Web development, backend, data, mobile stories
4. **"Peer Learning"** - Community showcase, "how I built X" stories
5. **"Tool Mastery"** - Beyond comparison (Cursor deep dive, Copilot mastery, etc.)

## Writing Checklist for New Content

When adding content, ensure:

- [ ] Target audience clear (absolute beginners assumed)
- [ ] "Why does this matter?" answered early
- [ ] External links include *Why recommended* explanation
- [ ] Time commitment stated (if applicable)
- [ ] Next step clear (what to do after)
- [ ] Tone: opinionated but not arrogant
- [ ] Tone: encouraging but realistic
- [ ] No jargon or jargon explained
- [ ] Uses analogies where helpful
- [ ] Short paragraphs (2-3 sentences max)
- [ ] Clear section headers (H2/H3, not H1)
- [ ] Call-to-action at end (not in every section)
- [ ] Links use relative paths (`/docs/...` not full URLs)
- [ ] Matches existing resource annotation format

## File Formats

- **`.md`** - Static markdown (stages, intro, tools)
- **`.mdx`** - Markdown with interactive components (roadmap, prompt engineering, demo)
- **Blog**: Files in `/blog/` with date prefix and `.md` extension

## Sidebar Navigation

Configured in `sidebars.ts`:
```
intro (Welcome)
├── Learning Stages
│   ├── Stage 0: Vibecoding
│   ├── Stage 1: Reality Check
│   └── Stage 2: Context
├── Core Tutorials
│   ├── AI Coding Roadmap
│   ├── Prompt Engineering 101
│   └── CSV → Markdown Demo
```

Community and Experts sections exist but not added to sidebar (empty, placeholder for future).

## SEO & Metadata

Each file should have frontmatter:

```markdown
---
id: unique-identifier           # Optional, defaults to filename
title: Human Readable Title     # Shown in browser/search
description: Brief summary      # 160 char for search results
sidebar_position: 1             # Order in sidebar
keywords: [tag1, tag2]          # For search
---
```

Example from existing files:
```markdown
---
id: prompt-engineering-101
title: Prompt Engineering 101 - Essential Templates for Coding
description: Master the art of writing effective prompts to get better code from ChatGPT, Claude, and other AI coding assistants
keywords: [prompt engineering, chatgpt, claude, ai coding, prompt templates, debugging]
---
```

## Translation Strategy (Future)

- English-first (all content created in English)
- Chinese translation planned (infrastructure in place)
- File naming: `tutorial.md` (English) → `tutorial.zh.md` (Chinese)
- Future languages: Spanish, Portuguese, Hindi, Japanese, Arabic, French, German

Currently: Only English (`en`) and Chinese (`zh`) active in `docusaurus.config.ts`
