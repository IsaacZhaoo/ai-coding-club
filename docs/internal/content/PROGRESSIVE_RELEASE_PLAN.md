# Progressive Content Release Plan

> Strategy for gradually releasing course content and translations using Docusaurus `unlisted` feature

## Overview

**Goal**: Publish high-quality, well-tested content progressively rather than all at once
**Method**: Use `unlisted: true` frontmatter to soft-launch content, then remove it to make content public
**Timeline**: 8-week phased rollout

## How It Works

### Initial State (Week 0)
- All 31 course lessons exist in production build
- All marked as `unlisted: true`
- Accessible via direct URL for testing
- Hidden from:
  - Sidebar navigation
  - Search results (Pagefind)
  - Sitemap (no SEO indexing)

### Publication Process
1. Review and polish content
2. Remove `unlisted: true` from frontmatter
3. Commit and push
4. Content automatically appears in sidebar and search

### Rollback Process
If issues are found after publication:
1. Add `unlisted: true` back to frontmatter
2. Commit and push
3. Content disappears from public view but URL still works

## Release Schedule

### Week 1 (2025-11-04): Core Navigation & Foundation
**Goal**: Establish basic structure and publish first lesson

#### Content to Publish
- [ ] `docs/course/index.md` - Course overview page
- [ ] `docs/course/01-foundations/what-is-ai-coding.md` - Most important first lesson

#### Tasks
- [ ] Polish English content
- [ ] Add call-to-action for joining community
- [ ] Test all internal links
- [ ] Remove `unlisted: true` from above files
- [ ] Deploy and verify

**Success Metrics**: Users can find and read the course overview and first lesson

---

### Week 2 (2025-11-11): Complete Phase 1 - Foundations
**Goal**: Publish entire foundations phase (6 lessons)

#### Content to Publish
- [ ] `docs/course/01-foundations/choosing-tools.md`
- [ ] `docs/course/01-foundations/setting-up.md`
- [ ] `docs/course/01-foundations/first-project.md`
- [ ] `docs/course/01-foundations/understanding-prompts.md`
- [ ] `docs/course/01-foundations/debugging-basics.md`

#### Tasks
- [ ] Review all Phase 1 lessons for consistency
- [ ] Ensure code examples are tested and working
- [ ] Check cross-references between lessons
- [ ] Remove `unlisted: true` from all Phase 1 lessons
- [ ] Update course index page to highlight Phase 1 completion

**Success Metrics**: Complete beginner-friendly learning path established

---

### Week 3 (2025-11-18): Phase 2 Part 1 - Essential Skills (4 lessons)
**Goal**: Start publishing intermediate content

#### Content to Publish
- [ ] `docs/course/02-essential-skills/version-control.md`
- [ ] `docs/course/02-essential-skills/reading-docs.md`
- [ ] `docs/course/02-essential-skills/testing-basics.md`
- [ ] `docs/course/02-essential-skills/code-review.md`

#### Tasks
- [ ] Verify all code examples
- [ ] Add practical exercises
- [ ] Remove `unlisted: true`

---

### Week 4 (2025-11-25): Phase 2 Part 2 - Essential Skills (3 lessons)
**Goal**: Complete essential skills phase

#### Content to Publish
- [ ] `docs/course/02-essential-skills/debugging-advanced.md`
- [ ] `docs/course/02-essential-skills/performance.md`
- [ ] `docs/course/02-essential-skills/security-basics.md`

#### Tasks
- [ ] Complete Phase 2
- [ ] Update course roadmap to show 2 phases completed

---

### Week 5 (2025-12-02): Phase 3 Part 1 - Building Projects (4 lessons)
**Goal**: Start project-based learning

#### Content to Publish
- [ ] `docs/course/03-building-projects/project-planning.md`
- [ ] `docs/course/03-building-projects/architecture.md`
- [ ] `docs/course/03-building-projects/frontend.md`
- [ ] `docs/course/03-building-projects/backend.md`

#### Tasks
- [ ] Ensure project templates are available
- [ ] Test all project examples
- [ ] Remove `unlisted: true`

---

### Week 6 (2025-12-09): Phase 3 Part 2 - Building Projects (4 lessons)
**Goal**: Complete building projects phase

#### Content to Publish
- [ ] `docs/course/03-building-projects/database.md`
- [ ] `docs/course/03-building-projects/deployment.md`
- [ ] `docs/course/03-building-projects/monitoring.md`
- [ ] `docs/course/03-building-projects/portfolio.md`

#### Tasks
- [ ] Complete Phase 3
- [ ] Verify deployment guides work

---

### Week 7 (2025-12-16): Phase 4 - Specialization (5 lessons)
**Goal**: Publish advanced specialization content

#### Content to Publish
- [ ] `docs/course/04-specialization/web-development.md`
- [ ] `docs/course/04-specialization/mobile-development.md`
- [ ] `docs/course/04-specialization/data-science.md`
- [ ] `docs/course/04-specialization/devops.md`
- [ ] `docs/course/04-specialization/ai-ml.md`

#### Tasks
- [ ] Review specialization paths
- [ ] Update with latest tools and frameworks
- [ ] Remove `unlisted: true`

---

### Week 8 (2025-12-23): Phase 5 - Career (4 lessons)
**Goal**: Complete full curriculum

#### Content to Publish
- [ ] `docs/course/05-career/job-search.md`
- [ ] `docs/course/05-career/interviews.md`
- [ ] `docs/course/05-career/freelancing.md`
- [ ] `docs/course/05-career/continuous-learning.md`

#### Tasks
- [ ] Complete all 5 phases
- [ ] Update homepage to announce full curriculum
- [ ] Celebrate launch! 🎉

---

## Parallel Track: Chinese Translation

### Translation Schedule (Starting Week 2)

**Week 2-3**: Translate Phase 1 (foundations)
**Week 4-5**: Translate Phase 2 (essential skills)
**Week 6-7**: Translate Phase 3 (building projects)
**Week 8**: Translate Phases 4-5 (specialization + career)

### Translation Workflow
1. Use AI translation (Claude/ChatGPT) for first draft
2. Human review and cultural adaptation
3. Add translation metadata to frontmatter:
   ```yaml
   ---
   translation_date: 2025-11-11
   translation_status: reviewed
   ---
   ```
4. Create file: `i18n/zh/docusaurus-plugin-content-docs/current/course/[path].md`
5. Commit and deploy

## Implementation Tools

### Scripts to Create

#### 1. Content Status Checker
**File**: `scripts/content/check-unlisted-status.js`

```javascript
// List all courses and their unlisted status
// Usage: npm run content:status
```

#### 2. Batch Unlister
**File**: `scripts/content/mark-unlisted.js`

```javascript
// Add unlisted: true to specified files
// Usage: npm run content:mark-unlisted "docs/course/04-*"
```

#### 3. Batch Publisher
**File**: `scripts/content/publish.js`

```javascript
// Remove unlisted: true from specified files
// Usage: npm run content:publish "docs/course/01-*"
```

#### 4. Translation Coverage Report
**File**: `scripts/i18n/coverage-report.js`

```javascript
// Show which files have Chinese translations
// Usage: npm run i18n:coverage
```

### Package.json Scripts

```json
{
  "scripts": {
    "content:status": "node scripts/content/check-unlisted-status.js",
    "content:mark-unlisted": "node scripts/content/mark-unlisted.js",
    "content:publish": "node scripts/content/publish.js",
    "i18n:coverage": "node scripts/i18n/coverage-report.js"
  }
}
```

## Quality Checklist

Before removing `unlisted: true` from any lesson:

### Content Quality
- [ ] Grammar and spelling checked
- [ ] Code examples tested and working
- [ ] All images/assets loading correctly
- [ ] Internal links verified
- [ ] External links checked (not broken)

### Technical Quality
- [ ] TypeScript types correct
- [ ] No console errors in dev/production
- [ ] Mobile responsive
- [ ] Accessible (WCAG AA)

### SEO & Discovery
- [ ] Meta description compelling
- [ ] Title optimized for search
- [ ] Proper heading hierarchy (h1 → h2 → h3)

### User Experience
- [ ] Clear learning objectives
- [ ] Practical examples included
- [ ] Next steps obvious
- [ ] Call-to-action present

## Monitoring & Feedback

### Metrics to Track
- Page views per lesson (Plausible Analytics)
- Time on page
- Bounce rate
- Community feedback (GitHub discussions)

### Feedback Loop
- Weekly review of published content performance
- Monthly content quality audit
- Quarterly curriculum update based on user feedback

## Emergency Procedures

### If Major Issue Found After Publication
1. Immediately add `unlisted: true` to affected file
2. Create GitHub issue documenting problem
3. Fix issue
4. Test fix thoroughly
5. Remove `unlisted: true` when ready

### If Translation Issue Found
1. Add note to Chinese version: "翻译更新中，请参考英文版"
2. Fix translation
3. Remove note

## Success Criteria

### Week 8 Goals
- ✅ All 31 lessons published (unlisted removed)
- ✅ At least Phase 1 translated to Chinese
- ✅ No broken links or errors
- ✅ Positive community feedback
- ✅ Search functionality working perfectly

### Long-term Goals (3 months)
- All content translated to Chinese
- User testimonials collected
- 1000+ unique visitors
- Active community discussions

## Notes

- This is a living document - adjust timeline based on reality
- Quality over speed - delay publication if content not ready
- Listen to user feedback and adapt
- Celebrate small wins along the way!

---

**Last Updated**: 2025-11-01
**Owner**: Project maintainer
**Status**: Active planning phase
