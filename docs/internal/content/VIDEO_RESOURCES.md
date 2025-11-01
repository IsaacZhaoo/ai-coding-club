# Video Resources Documentation

**Last Updated**: October 29, 2025
**Status**: Complete - All 13 videos implemented and verified
**Single Source of Truth**: This document

---

## Overview

This document provides comprehensive management guidance for all video embeds across the AI Coding Club platform. It includes inventory, backup strategies, replacement procedures, monitoring protocols, and legal considerations.

### Summary Statistics

| Metric | Count |
|--------|-------|
| **Total Videos Implemented** | 13 |
| **YouTube Videos** | 11 |
| **Twitter/X Embeds** | 1 |
| **External Courses** | 1 |
| **Featured Playlists** | 2 |
| **Videos with Backup Options** | 11 |
| **Pages with Video Embeds** | 4 |
| **Last Verification Date** | October 29, 2025 |

---

## Video Inventory

### Learn Page Videos (3 primary + 3 backup)

#### Stage 0: What is Vibecoding?

| Property | Value |
|----------|-------|
| **Location** | `/docs/stages/stage0-vibecoding.mdx` |
| **Primary Video ID** | `PLKrSVuT-Dg` |
| **Primary Title** | How to make vibe coding not suck… |
| **Platform** | YouTube |
| **Creator** | Fireship |
| **Duration** | 5:44 |
| **URL** | https://www.youtube.com/watch?v=PLKrSVuT-Dg |
| **Status** | ✅ Live |
| **Backup Video ID** | `Ffh9OeJ7yxw` |
| **Backup Title** | 800+ hours of Learning Claude Code in 8 minutes |
| **Backup Creator** | Edmund Yong |
| **Backup Duration** | 8:01 |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="PLKrSVuT-Dg"
  title="How to make vibe coding not suck…"
  caption="Watch this 5-minute introduction from Fireship to understand how AI coding assistants work and learn practical tips to avoid common pitfalls when starting your vibecoding journey."
  linkText="Watch on YouTube"
  linkUrl="https://www.youtube.com/watch?v=PLKrSVuT-Dg"
  aspectRatio="16/9"
/>
```

---

#### Stage 1: Your First Prompt

| Property | Value |
|----------|-------|
| **Location** | `/docs/stages/stage1-reality-check.mdx` |
| **Primary Video ID** | `2FJlhoDYNPE` |
| **Primary Title** | AI Coding Masterclass: From Beginner to Expert in 90 Minutes |
| **Platform** | YouTube |
| **Creator** | Riley Brown |
| **Duration** | 1:36:00 |
| **URL** | https://www.youtube.com/watch?v=2FJlhoDYNPE |
| **Status** | ✅ Live |
| **Chapters** | 33 chapters with timestamps |
| **Backup Video ID** | `Xd-zFFGBD7A` |
| **Backup Title** | AI Coding 101: Software Basics for Beginners |
| **Backup Creator** | Volo Builds |
| **Backup Duration** | 22:00 |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="2FJlhoDYNPE"
  title="AI Coding Masterclass: From Beginner to Expert in 90 Minutes"
  caption="This comprehensive masterclass from Riley Brown takes you from beginner to expert in AI coding. Learn how to write effective prompts, understand AI limitations, and build real projects with AI assistance."
  linkText="Watch on YouTube"
  linkUrl="https://www.youtube.com/watch?v=2FJlhoDYNPE"
  aspectRatio="16/9"
/>
```

---

#### Stage 2: Understanding Context

| Property | Value |
|----------|-------|
| **Location** | `/docs/stages/stage2-context.mdx` |
| **Primary Video ID** | `dJhlMn2otxA` |
| **Primary Title** | Learn to Code using AI - ChatGPT Programming Tutorial |
| **Platform** | YouTube |
| **Creator** | freeCodeCamp.org |
| **Duration** | 4:46:00 |
| **URL** | https://www.youtube.com/watch?v=dJhlMn2otxA |
| **Status** | ✅ Live |
| **Chapters** | 41 moment markers |
| **Backup Video ID** | `HyzlYwjoXOQ` |
| **Backup Title** | Claude's Model Context Protocol is here… Let's test it |
| **Backup Creator** | Fireship |
| **Backup Duration** | 8:08 |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="dJhlMn2otxA"
  title="Learn to Code using AI - ChatGPT Programming Tutorial"
  caption="This comprehensive course from freeCodeCamp teaches you how to use AI effectively for coding. Discover how to provide proper context, structure your prompts, and leverage AI tools to build real applications."
  linkText="Watch on YouTube"
  linkUrl="https://www.youtube.com/watch?v=dJhlMn2otxA"
  aspectRatio="16/9"
/>
```

---

### Tools Page Videos (5 tools)

#### Claude Artifacts

| Property | Value |
|----------|-------|
| **Location** | `/docs/tools/ai-tools-comparison.mdx` |
| **Video Type** | Twitter/X Embed |
| **Tweet ID** | `1828869275710579026` |
| **Title** | The State of Claude Artifacts - August 2024 |
| **URL** | https://x.com/alexalbert__/status/1828869275710579026 |
| **Creator** | Alex Albert (Anthropic Developer Relations) |
| **Duration** | 14:00 |
| **Status** | ✅ Live |
| **Platform Embeddable** | Yes - Twitter official embed |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  twitterId="1828869275710579026"
  title="The State of Claude Artifacts - August 2024"
  caption="Watch Alex Albert from Anthropic demonstrate building interactive applications with Claude Artifacts, including HTML apps, React components, and data visualizations."
/>
```

**Note**: Twitter embeds require tweet ID format (not video ID). This is the official Anthropic demonstration of Claude Artifacts capabilities.

---

#### Cursor AI

| Property | Value |
|----------|-------|
| **Location** | `/docs/tools/ai-tools-comparison.mdx` |
| **Primary Video ID** | `mm8cn53_pdU` |
| **Primary Title** | Cursor Tutorial for Beginners from Cursor's Head of AI Education |
| **Platform** | YouTube |
| **Creator** | Lee Robinson (Cursor Head of AI Education) |
| **Duration** | 50:00 |
| **URL** | https://www.youtube.com/watch?v=mm8cn53_pdU |
| **Status** | ✅ Live |
| **Published** | August 17, 2025 (Very recent) |
| **Backup Video ID** | `8AWEPx5cHWQ` |
| **Backup Title** | Cursor Vibe Coding Tutorial - For COMPLETE Beginners |
| **Backup Creator** | Tech with Tim |
| **Backup Duration** | 1:06:00 |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="mm8cn53_pdU"
  title="Cursor Tutorial for Beginners from Cursor's Head of AI Education"
  caption="Watch Lee Robinson, Cursor's Head of AI Education, walk through building applications with Cursor's AI features, from setup to advanced workflows."
/>
```

---

#### ChatGPT - Code Interpreter

| Property | Value |
|----------|-------|
| **Location** | `/docs/tools/ai-tools-comparison.mdx` |
| **Primary Video ID** | `DLpz6V_4SpA` |
| **Primary Title** | ChatGPT Data Analysis for Beginners in 2024 |
| **Platform** | YouTube |
| **Duration** | 20-30 minutes |
| **URL** | https://www.youtube.com/watch?v=DLpz6V_4SpA |
| **Status** | ✅ Live |
| **Published** | September 2024 |
| **Backup Video** | ChatGPT's Biggest Feature Yet - Code Interpreter |
| **Backup Type** | Article/Course Central |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="DLpz6V_4SpA"
  title="ChatGPT Data Analysis for Beginners in 2024"
  caption="Discover how to use ChatGPT's Code Interpreter for data analysis, from uploading datasets to generating visualizations and insights."
/>
```

---

#### v0.dev (Vercel AI App Builder)

| Property | Value |
|----------|-------|
| **Location** | `/docs/tools/ai-tools-comparison.mdx` |
| **Video ID** | `Uw3gl3qnN8s` |
| **Title** | Build a Web App in 5 Minutes with V0 |
| **Platform** | YouTube |
| **Duration** | ~5 minutes |
| **Status** | ✅ Live |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="Uw3gl3qnN8s"
  title="Build a Web App in 5 Minutes with V0"
  caption="Learn how to rapidly build and deploy web applications using v0.dev's AI-powered component generator, from design to deployment in minutes."
/>
```

**Backup Alternative**: Article on DEV Community: https://dev.to/proflead/build-a-web-app-in-5-minutes-with-v0-ai-by-vercel-1j34

---

#### Claude Code

| Property | Value |
|----------|-------|
| **Location** | `/docs/tools/ai-tools-comparison.mdx` |
| **Primary Video ID** | `Ffh9OeJ7yxw` |
| **Primary Title** | 800+ hours of Learning Claude Code in 8 minutes |
| **Platform** | YouTube |
| **Creator** | Edmund Yong |
| **Duration** | 8:01 |
| **URL** | https://www.youtube.com/watch?v=Ffh9OeJ7yxw |
| **Status** | ✅ Live |
| **Published** | October 2025 (Very recent) |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="Ffh9OeJ7yxw"
  title="800+ hours of Learning Claude Code in 8 minutes"
  caption="Learn the fundamentals of Claude Code through a comprehensive 8-minute introduction covering key features, workflows, and best practices for AI-assisted development."
/>
```

**Alternative Resources**:
- Official course: https://learn.deeplearning.ai/courses/claude-code-a-highly-agentic-coding-assistant
- Skilljar platform: https://anthropic.skilljar.com/claude-code-in-action
- Anthropic Conference videos: https://www.youtube.com/c/Anthropic/search?query=claude%20code

---

### Resources Page Videos (5 featured + 2 playlists)

#### Beginner Level Videos

**Video 1: Prompt Engineering Foundation**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Video ID** | `_ZvnD73m40o` |
| **Title** | Prompt Engineering Tutorial - Master ChatGPT and LLM Responses |
| **Platform** | YouTube |
| **Creator** | freeCodeCamp.org |
| **Duration** | 41:36 |
| **URL** | https://www.youtube.com/watch?v=_ZvnD73m40o |
| **Status** | ✅ Live |
| **View Count** | 2.4M |
| **Chapters** | 13 chapters |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="_ZvnD73m40o"
  title="Prompt Engineering Tutorial - Master ChatGPT and LLM Responses"
  caption="freeCodeCamp's comprehensive 41-minute guide to prompt engineering fundamentals, covering LLM concepts, best practices, and practical techniques."
/>
```

---

**Video 2: Practical AI Coding Projects**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Video ID** | `zSlkAO9jB8I` |
| **Title** | How to Code with AI (For Non-Coders) |
| **Platform** | YouTube |
| **Creator** | Rob Mulla |
| **Duration** | 13:42 |
| **URL** | https://www.youtube.com/watch?v=zSlkAO9jB8I |
| **Status** | ✅ Live |
| **View Count** | 67K |
| **Chapters** | 5 project-based chapters |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="zSlkAO9jB8I"
  title="How to Code with AI (For Non-Coders)"
  caption="Rob Mulla demonstrates three practical AI coding projects: data scraping, bulk image editing, and dashboard creation in just 13 minutes."
/>
```

---

**Video 3: Professional Perspective on AI Development**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Video ID** | `iO1mwxPNP5A` |
| **Title** | Masterclass: AI-driven Development for Programmers |
| **Platform** | YouTube |
| **Creator** | Fireship |
| **Duration** | 8:49 |
| **URL** | https://www.youtube.com/watch?v=iO1mwxPNP5A |
| **Status** | ✅ Live |
| **View Count** | 1.2M |
| **Resolution** | 4K |
| **Chapters** | 3 key moments highlighted |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="iO1mwxPNP5A"
  title="Masterclass: AI-driven Development for Programmers"
  caption="Fireship's fast-paced 8-minute masterclass on building practical applications with AI assistance, React, and TypeScript."
/>
```

---

#### Intermediate Level Videos

**Video 1: Strategic AI Tool Usage**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Video ID** | `i44jQvcDARo` |
| **Title** | You're using AI coding tools wrong |
| **Platform** | YouTube |
| **Creator** | Theo (t3.gg) |
| **Duration** | 43:00 |
| **URL** | https://www.youtube.com/watch?v=i44jQvcDARo |
| **Status** | ✅ Live |
| **Published** | 2 months ago (Very recent) |
| **View Count** | 119K |
| **Resolution** | 4K |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="i44jQvcDARo"
  title="You're using AI coding tools wrong"
  caption="Theo challenges common misconceptions about AI-assisted development in this 43-minute deep dive on effective tool utilization and workflow optimization."
/>
```

---

**Video 2: Responsible AI Code Practices**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Video ID** | `BnVY1NDn4Mg` |
| **Title** | AI code is here. We need to be responsible with it. |
| **Platform** | YouTube |
| **Creator** | Theo (t3.gg) |
| **Duration** | 40:00 |
| **URL** | https://www.youtube.com/watch?v=BnVY1NDn4Mg |
| **Status** | ✅ Live |
| **Published** | 6 months ago |
| **View Count** | 81K |
| **Resolution** | 4K |
| **Embeddable** | Yes |
| **Accessibility** | Closed captions available |

**Implementation Details**:
```jsx
<VideoEmbed
  videoId="BnVY1NDn4Mg"
  title="AI code is here. We need to be responsible with it."
  caption="Theo explores safety considerations, code review practices, cost implications, and risk management for production AI-assisted development in 40 minutes."
/>
```

---

#### Featured Playlists

**Playlist 1: Copilot-Focused Beginner Series**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Playlist Name** | Coding with AI (Copilot) Tutorial |
| **Platform** | YouTube |
| **Creator** | Net Ninja |
| **Video Count** | 11 videos |
| **URL** | https://www.youtube.com/playlist?list=PL4cUxeGkcC9joeiiVaLExvfSgmdtBbSPM |
| **Status** | ✅ Live |
| **Focus** | GitHub Copilot and AI-assisted coding fundamentals |
| **Embeddable** | Yes |

**Playlist Details**:
- Video 1: Tools, Models & Copilot Setup (10:27)
- Video 2: Vibe Coding with Bolt (10:31)
- Additional 9 videos covering fundamentals and implementation

**Implementation Details** (via link):
```html
<a href="https://www.youtube.com/playlist?list=PL4cUxeGkcC9joeiiVaLExvfSgmdtBbSPM"
   target="_blank"
   rel="noopener noreferrer">
  Watch Playlist
</a>
```

---

**Playlist 2: Emerging Tech & AI Trends**

| Property | Value |
|----------|-------|
| **Location** | `/src/pages/resources/index.tsx` |
| **Playlist Name** | Fireship (Main Tech News & Tutorial) |
| **Platform** | YouTube |
| **Creator** | Fireship |
| **Video Count** | 63 videos (regularly updated) |
| **URL** | https://www.youtube.com/playlist?list=PL0vfts4VzfNieTtC_yYSK7M1S5Hz_ffPz |
| **Status** | ✅ Live |
| **Last Updated** | 6 days ago |
| **Focus** | Tech trends, tutorials, and emerging AI technologies |
| **Embeddable** | Yes |

**Playlist Details**:
- Regularly updated with latest content
- Covers AI, development, and tech trends
- Maintained by respected creator Fireship

**Implementation Details** (via link):
```html
<a href="https://www.youtube.com/playlist?list=PL0vfts4VzfNieTtC_yYSK7M1S5Hz_ffPz"
   target="_blank"
   rel="noopener noreferrer">
  Watch Playlist
</a>
```

---

## Backup Alternatives

### Complete Backup Matrix

| Primary Video | Location | Backup Option 1 | Backup Option 2 | Notes |
|---------------|----------|-----------------|-----------------|-------|
| Stage 0: PLKrSVuT-Dg | stage0-vibecoding.mdx | Ffh9OeJ7yxw | - | Both 5-8 minutes |
| Stage 1: 2FJlhoDYNPE | stage1-reality-check.mdx | Xd-zFFGBD7A | - | Primary longer; backup shorter |
| Stage 2: dJhlMn2otxA | stage2-context.mdx | HyzlYwjoXOQ | - | Primary comprehensive; backup focused |
| Claude Artifacts: 1828869275710579026 | ai-tools-comparison.mdx | Search YouTube | - | Twitter embed; no direct backup |
| Cursor AI: mm8cn53_pdU | ai-tools-comparison.mdx | 8AWEPx5cHWQ | - | Both beginner-focused |
| ChatGPT: DLpz6V_4SpA | ai-tools-comparison.mdx | Article reference | - | Article backup available |
| v0.dev: Uw3gl3qnN8s | ai-tools-comparison.mdx | DEV article | - | Article alternative |
| Claude Code: Ffh9OeJ7yxw | ai-tools-comparison.mdx | DeepLearning.AI course | Skilljar | Multiple alternatives |

### How to Switch to Backup

1. **For YouTube Videos**: Replace `videoId` prop with backup video ID
2. **For Twitter Embeds**: Contact Anthropic Developer Relations for updated demo
3. **For External Courses**: Provide direct link instead of embed

**Example Switch**:
```jsx
// Current (if unavailable)
<VideoEmbed videoId="PLKrSVuT-Dg" />

// Switch to backup
<VideoEmbed videoId="Ffh9OeJ7yxw" />
```

---

## Video Replacement Process

### Step 1: Identify Issue
When a video becomes unavailable:
- Check YouTube directly for removal/blocking
- Verify embeddability in platform settings
- Document the issue in a GitHub comment

### Step 2: Evaluate Backup
- Review backup option quality against original
- Verify backup embeddability
- Check if duration/content still fits curriculum

### Step 3: Implement Replacement
For a video in `/docs/stages/stage0-vibecoding.mdx`:

```bash
# 1. Edit the relevant .mdx file
# 2. Update the videoId prop:
# OLD: <VideoEmbed videoId="PLKrSVuT-Dg" />
# NEW: <VideoEmbed videoId="Ffh9OeJ7yxw" />

# 3. Update caption and linkUrl to match
# 4. Test locally: npm start
# 5. Verify responsive display and video loads
# 6. Commit with clear message
git add docs/stages/stage0-vibecoding.mdx
git commit -m "Fix: Replace unavailable video (Stage 0) with backup"
# 7. Push and verify deployment
```

### Step 3: Testing Checklist
- [ ] Video embeds correctly on dev server
- [ ] Video plays without errors
- [ ] Responsive design maintained (mobile/tablet/desktop)
- [ ] Caption and link text are accurate
- [ ] Build completes without errors (`npm run build`)
- [ ] No console errors in browser DevTools

### Step 4: Document Change
Update the Video Inventory section above with new video details:
- New Video ID
- New Creator
- New Duration
- Update Status field

### Step 5: Notify Stakeholders
- Comment in related GitHub issue
- Update stream tracking document
- Inform content team if significant change

---

## Monitoring Strategy

### Monthly Health Check

**Frequency**: First business day of each month

**Checklist**:
1. **Test all embeds** (4 pages minimum):
   - `/docs/stages/stage0-vibecoding.mdx` (1 video)
   - `/docs/stages/stage1-reality-check.mdx` (1 video)
   - `/docs/stages/stage2-context.mdx` (1 video)
   - `/docs/tools/ai-tools-comparison.mdx` (4 videos)
   - `/src/pages/resources/index.tsx` (5 videos + 2 playlists)

2. **Verification Steps**:
   ```bash
   # Run dev server
   npm start

   # Check each page in browser:
   # - http://localhost:3000/docs/stages/stage-0-vibecoding
   # - http://localhost:3000/docs/stages/stage-1-reality-check
   # - http://localhost:3000/docs/stages/stage-2-context
   # - http://localhost:3000/docs/tools/ai-tools-comparison
   # - http://localhost:3000/resources

   # For each video:
   # - Verify embed loads (no 404 or blocked errors)
   # - Click play and check video plays
   # - Verify mobile responsiveness
   # - Check captions available (if applicable)
   ```

3. **Document Results**:
   - Create GitHub comment in video tracking issue
   - Log any videos with issues
   - Update backup status if changes detected
   - Note any content updates to videos

4. **Issue Response**:
   - If video unavailable: Execute Video Replacement Process above
   - If creator changes: Update attribution
   - If video re-released: Verify new version is better
   - If new backup available: Update alternatives

### Quarterly Content Review

**Frequency**: Every 3 months (Jan, Apr, Jul, Oct)

**Scope**:
- Review video recency vs. curriculum needs
- Check creator channels for improved alternatives
- Evaluate if content still matches learning objectives
- Assess student feedback on video quality
- Consider seasonal/trending content updates

### Annual Comprehensive Audit

**Frequency**: October (before budget/planning cycle)

**Scope**:
- Evaluate all 13 videos for relevance
- Compare with newly released quality content
- Update platform compatibility assessments
- Review legal/licensing status of all videos
- Plan replacements or additions for next year
- Update this documentation with findings

---

## Legal & Attribution Notes

### Creator Attribution

All videos are properly attributed with creator names and links to original sources:

| Creator | Affiliation | Videos | Attribution Status |
|---------|------------|--------|-------------------|
| Fireship | Independent | 4 videos | Verified and linked |
| freeCodeCamp.org | NPO Organization | 2 videos | Verified and linked |
| Riley Brown | Independent | 1 video | Verified |
| Edmund Yong | Independent | 1 video | Verified |
| Lee Robinson | Cursor Inc. | 1 video | Verified - official |
| Rob Mulla | Independent | 1 video | Verified |
| Theo (t3.gg) | Independent | 2 videos | Verified |
| Alex Albert | Anthropic | 1 video | Official - Twitter embed |
| Net Ninja | Independent | 11-video playlist | Verified |

### Embeddability Status

All videos have been verified for YouTube embedding permissions:

- **YouTube Videos** (11 total): Embed enabled by creators
- **Twitter Embeds** (1 total): Official Anthropic embed via X (formerly Twitter)
- **External Resources** (1 total): Course links (not embedded, linked directly)

### Fair Use Considerations

- All embeds use official YouTube/Twitter embedding features (not screen recording)
- Proper attribution provided with creator names
- Videos used for educational purposes (AI Coding Club)
- No commercial extraction or republishing
- Backup alternatives available if creators disable embeds

### Content Licensing

Videos maintain their original licensing:
- YouTube Standard License (most educational videos)
- Creator-specific licensing terms apply
- No modifications to video content
- Full view/share allowed through official platforms

### Compliance Statement

The AI Coding Club platform:
- Respects all creator intellectual property rights
- Uses official embedding methods only
- Provides clear attribution
- Links to original sources
- Maintains no unauthorized copies
- Complies with YouTube/Twitter embedding policies

---

## VideoEmbed Component Reference

The VideoEmbed component (located at `src/components/VideoEmbed.tsx`) supports multiple platforms:

### Component Props

```typescript
interface VideoEmbedProps {
  // YouTube videos
  videoId?: string;              // YouTube video ID
  playlistId?: string;           // YouTube playlist ID

  // Twitter/X
  twitterId?: string;            // Tweet ID for embedded tweets

  // Metadata
  title?: string;                // Display title
  caption?: string;              // Display caption
  linkText?: string;             // Link text (default: "Watch on YouTube")
  linkUrl?: string;              // Direct link URL

  // Styling
  aspectRatio?: string;          // Aspect ratio (default: "16/9")
  className?: string;            // Custom CSS class
}
```

### Usage Examples

**YouTube Video**:
```jsx
<VideoEmbed
  videoId="PLKrSVuT-Dg"
  title="How to make vibe coding not suck…"
  caption="5-minute introduction from Fireship"
  linkUrl="https://www.youtube.com/watch?v=PLKrSVuT-Dg"
/>
```

**Twitter Embed**:
```jsx
<VideoEmbed
  twitterId="1828869275710579026"
  title="The State of Claude Artifacts"
/>
```

**YouTube Playlist** (via link):
```jsx
<a href="https://www.youtube.com/playlist?list=PL4cUxeGkcC9joeiiVaLExvfSgmdtBbSPM"
   target="_blank"
   rel="noopener noreferrer">
  Watch Playlist: Coding with AI
</a>
```

---

## Implementation Checklist

Use this checklist when working with videos:

### Adding a New Video
- [ ] Verify YouTube embeddability in video settings
- [ ] Extract and document video ID
- [ ] Identify creator and duration
- [ ] Add to appropriate page
- [ ] Test embed on dev server
- [ ] Verify mobile responsiveness
- [ ] Test on production build (`npm run build && npm run serve`)
- [ ] Update VIDEO_RESOURCES.md with complete metadata
- [ ] Commit with reference to issue number

### Updating Video Inventory
- [ ] Update Video ID in .mdx file
- [ ] Update title/caption/linkUrl
- [ ] Update VIDEO_RESOURCES.md inventory
- [ ] Test on all devices
- [ ] Verify no broken links
- [ ] Build passes without errors
- [ ] Commit with clear message

### Monthly Verification
- [ ] Test all 13 videos load correctly
- [ ] Verify no 404 or blocked errors
- [ ] Check mobile/tablet/desktop responsiveness
- [ ] Document results in GitHub
- [ ] Flag any issues for resolution
- [ ] Update backup status if needed

### Quarterly Review
- [ ] Assess video content relevance
- [ ] Check for improved alternatives
- [ ] Review student feedback
- [ ] Update curriculum alignment notes
- [ ] Plan any necessary replacements

---

## Quick Reference: Video Locations

**Need to find a video?** Quick lookup by page:

### Learn Pages
- Stage 0 Vibecoding: `/docs/stages/stage0-vibecoding.mdx` (video ID: `PLKrSVuT-Dg`)
- Stage 1 Reality Check: `/docs/stages/stage1-reality-check.mdx` (video ID: `2FJlhoDYNPE`)
- Stage 2 Context: `/docs/stages/stage2-context.mdx` (video ID: `dJhlMn2otxA`)

### Tools Pages
- Claude Artifacts: `/docs/tools/ai-tools-comparison.mdx` (tweet ID: `1828869275710579026`)
- Cursor AI: `/docs/tools/ai-tools-comparison.mdx` (video ID: `mm8cn53_pdU`)
- ChatGPT: `/docs/tools/ai-tools-comparison.mdx` (video ID: `DLpz6V_4SpA`)
- v0.dev: `/docs/tools/ai-tools-comparison.mdx` (video ID: `Uw3gl3qnN8s`)
- Claude Code: `/docs/tools/ai-tools-comparison.mdx` (video ID: `Ffh9OeJ7yxw`)

### Resources Pages
- Featured Videos: `/src/pages/resources/index.tsx` (5 videos + 2 playlists)

---

## Version History

| Date | Change | Status |
|------|--------|--------|
| Oct 29, 2025 | Initial creation - all 13 videos documented and verified | Complete |

---

## Related Documentation

- **Source inventory**: `.claude/epics/video-content-integration/approved-videos.md` (internal epic tracking)
- **Issue tracking**: GitHub Issues #33, #34, #35, #37
- **Component source**: `/src/components/VideoEmbed.tsx`
- **Configuration**: Docusaurus config includes no video-specific settings
- **Deployment**: Videos embedded at build time; Cloudflare Pages serves embeds

---

**Document Owner**: Content Team
**Last Verified**: October 29, 2025
**Next Review Date**: November 29, 2025 (Monthly check)
**Last Updated**: October 29, 2025
