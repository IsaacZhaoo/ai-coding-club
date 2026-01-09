# Content Status

**Last Updated**: 2026-01-09

## Current State

### Course Content (All Phases Live)
- ✅ Phase 1: Foundations (8 lessons) - **LIVE**
- ✅ Phase 2: Essential Skills (8 lessons) - **LIVE**
- ✅ Phase 3: Building Projects (7 lessons) - **LIVE**
- ✅ Phase 4: Specialization (6 lessons) - **LIVE**
- ✅ Phase 5: Career (2 lessons) - **LIVE**

**Total**: 31 lessons across 5 phases

### Content Structure

```
docs/course/
├── index.md (Course overview with links to all phases)
├── 01-foundations/ (8 lessons)
├── 02-essential-skills/ (8 lessons)
├── 03-building-projects/ (7 lessons)
├── 04-specialization/ (6 lessons)
└── 05-career/ (2 lessons)
```

### Other Content Sections
- ✅ Tools & Resources - Active
- ✅ Tutorials - Active
- ✅ Best Practices - Active
- ✅ Roadmap - Active
- 🚧 LLM Inference (zh) - Under development
- 📝 Workflows/AIcoding/Snippets - Draft (hidden in production)

---

## Branch Strategy

**Single Branch**: `main`
- All content is in the main branch
- No separate develop branch needed
- Draft content uses `draft: true` frontmatter

---

## Deployment

**Platform**: Cloudflare Pages
- Auto-deploys on push to `main`
- Main site: https://aicoding.club

**Submodule**: Content is managed as a git submodule
- Repository: https://github.com/IsaacZhaoo/ai-coding-club

---

## Draft Content

Pages with `draft: true` in frontmatter are hidden in production:
- `docs/workflows/index.md`
- `docs/aicoding/index.md`
- `docs/snippets/index.md`
- Corresponding Chinese translations

These pages contain planned content and will be published when ready.

---

## Quality Assurance

### Before Publishing New Content

- [ ] Content reviewed for accuracy
- [ ] Frontmatter correct (title, description, sidebar_position)
- [ ] Links tested
- [ ] Chinese translations complete (if applicable)
- [ ] Local build test passed (`npm run build`)

### Testing Commands

```bash
# Test local build
cd <main-repo>
npm run build

# Preview locally
npm run start

# Check for broken links (build will fail)
# Docusaurus has onBrokenLinks: 'throw'
```

---

## Notes

- **i18n**: English and Chinese versions maintained in parallel
- **SEO**: No draft content indexed (draft pages excluded from sitemap)
- **Git History**: All content changes tracked in version control
