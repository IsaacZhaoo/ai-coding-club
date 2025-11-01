# Progressive Release Quick Start Guide

Quick reference for managing progressive content release using `unlisted` feature.

## Current Status

Run this command anytime to check status:

```bash
npm run content:status
```

Output shows:
- ✅ Published files (visible to users)
- 🔒 Unlisted files (hidden from navigation/search)

## Check Translation Coverage

```bash
npm run i18n:coverage
```

Shows which files have Chinese translations.

## Initial Setup (Week 0)

Mark all content as unlisted except the overview page:

```bash
# Mark all course files as unlisted
npm run content:mark-unlisted "course/**/*.md"

# Publish only the overview
npm run content:publish "course/index.md"
```

## Weekly Publishing Workflow

### Week 1: Publish Phase 1 Overview + First Lesson

```bash
# Check current status
npm run content:status

# Publish specific files
npm run content:publish "course/01-foundations/index.md"
npm run content:publish "course/01-foundations/01-welcome.md"

# Verify changes
git diff

# Commit
git add .
git commit -m "Week 1: Publish course overview and first lesson"
git push
```

### Week 2: Publish Remaining Phase 1

```bash
# Publish all Phase 1 lessons
npm run content:publish "course/01-foundations/*.md"

# Check status
npm run content:status

# Commit
git add .
git commit -m "Week 2: Publish complete Phase 1 (Foundations)"
git push
```

### Weeks 3-8: Continue Pattern

```bash
# Week 3: Phase 2 Part 1
npm run content:publish "course/02-essential-skills/01-command-line.md"
npm run content:publish "course/02-essential-skills/02-git-github.md"
# ... etc

# Week 4: Phase 2 Part 2
npm run content:publish "course/02-essential-skills/*.md"

# Week 5: Phase 3 Part 1
# Week 6: Phase 3 Part 2
# Week 7: Phase 4
# Week 8: Phase 5
```

## Emergency Rollback

If you need to hide published content:

```bash
# Hide a specific file
npm run content:mark-unlisted "course/02-essential-skills/01-command-line.md"

# Hide entire phase
npm run content:mark-unlisted "course/03-building-projects/*.md"

# Commit immediately
git add .
git commit -m "Emergency: Hide problematic content"
git push
```

## Translation Workflow

### Check What Needs Translation

```bash
npm run i18n:coverage
```

### Add Translation

1. Create translation file:
```bash
# Create directory if needed
mkdir -p i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations

# Create translation file
# File: i18n/zh/docusaurus-plugin-content-docs/current/course/01-foundations/01-welcome.md
```

2. Add content (copy frontmatter from English, translate body)

3. Commit:
```bash
git add i18n/zh/
git commit -m "i18n(zh): Translate 01-welcome lesson"
git push
```

## Useful Commands Reference

| Command | Purpose |
|---------|---------|
| `npm run content:status` | Check publication status of all content |
| `npm run content:publish "<pattern>"` | Publish (unhide) content matching pattern |
| `npm run content:mark-unlisted "<pattern>"` | Hide content matching pattern |
| `npm run i18n:coverage` | Check translation coverage |

## Pattern Examples

```bash
# Publish all files in a directory
npm run content:publish "course/01-foundations/*.md"

# Publish specific file
npm run content:publish "course/01-foundations/01-welcome.md"

# Publish ALL course content (use carefully!)
npm run content:publish "course/**/*.md"

# Publish just index files
npm run content:publish "course/*/index.md"
```

## Testing Before Deploy

Always test locally before pushing:

```bash
# Build production version
npm run build

# Serve locally
npm run serve

# Visit http://localhost:3000
# Test in both English and Chinese
```

## Troubleshooting

### Script doesn't find files

Make sure pattern is quoted:
```bash
# Wrong
npm run content:publish course/*.md

# Correct
npm run content:publish "course/*.md"
```

### Changes not visible after deploy

1. Check git status: `git status`
2. Ensure changes were committed and pushed
3. Wait for Cloudflare deployment (~1-2 minutes)
4. Hard refresh browser (Ctrl+Shift+R)

### Want to see what would change

```bash
# Dry run: manually check which files match
ls -la docs/course/01-foundations/*.md
```

## Quick Release Checklist

Before each weekly release:

- [ ] Run `npm run content:status` to see current state
- [ ] Review content quality for files to be published
- [ ] Run `npm run content:publish "<pattern>"` for this week's content
- [ ] Run `git diff` to review changes
- [ ] Test locally: `npm run build && npm run serve`
- [ ] Check both English and Chinese versions
- [ ] Commit and push
- [ ] Verify deployment on live site
- [ ] Update `PROGRESSIVE_RELEASE_PLAN.md` with completion status

---

**Pro Tip**: Keep the `PROGRESSIVE_RELEASE_PLAN.md` document open and check off items as you complete them each week!
