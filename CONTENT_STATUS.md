# Content Status

**Last Updated**: 2025-11-07

## Branch Structure

### `main` (Production)
**Purpose**: Production-ready content deployed to https://aicoding.club

**Current Content**:
- ✅ Phase 1: Foundations (8 lessons) - **LIVE**
- 🔜 Phase 2-5: Coming Soon alerts visible to users

**Actual Files**:
- `docs/course/01-foundations/` (8 lesson files)
- `docs/course/index.md` (with Coming Soon alerts for Phase 2-5)

**What's NOT in main**:
- ❌ Phase 2-5 actual course content (moved to develop)

**Latest Commit**: `5b126f8` - Refactor: Move Phase 2-5 courses to develop branch

---

### `develop` (Staging/WIP)
**Purpose**: Work-in-progress content not yet ready for release

**Current Content**:
- ✅ Phase 1: Foundations (8 lessons)
- ✅ Phase 2: Essential Skills (8 lessons) - **DRAFT**
- ✅ Phase 3: Building Projects (7 lessons) - **DRAFT**
- ✅ Phase 4: Specialization (6 lessons) - **DRAFT**
- ✅ Phase 5: Career (2 lessons) - **DRAFT**

**Total**: 31 lesson files (27 in Phase 2-5)

**Latest Commit**: `d62a0f2` - Add: Branching strategy documentation

---

## Content Differences

**Between `main` and `develop`**:

```bash
# main branch: Only Phase 1
docs/course/
├── 01-foundations/ (8 lessons)
└── index.md (Coming Soon alerts)

# develop branch: All phases
docs/course/
├── 01-foundations/ (8 lessons)
├── 02-essential-skills/ (8 lessons) ← Only in develop
├── 03-building-projects/ (7 lessons) ← Only in develop
├── 04-specialization/ (6 lessons) ← Only in develop
├── 05-career/ (2 lessons) ← Only in develop
└── index.md (Coming Soon alerts)
```

**File Count Difference**: +27 files in `develop` vs `main`

---

## Release Strategy

### Current State (Gradual Release via Sidebar)
**Navigation Control**: `sidebars.ts` in main repository

```typescript
// Only Phase 1 visible in sidebar
courseSidebar: [
  'course/index',
  { category: 'Phase 1: Foundations', items: [...] }, // ✅ Visible
  // Phase 2-5 commented out ❌ Hidden
]
```

**User Experience**:
- ✅ Users see "Coming Soon" alerts for Phase 2-5
- ✅ Users can access Phase 1 via sidebar
- ✅ Direct URLs to Phase 2-5 return 404 (files don't exist in main)
- ✅ No accidental content leakage

### Future Release Process

**When Phase 2 is ready**:

1. **In content submodule (develop branch)**:
   ```bash
   cd content
   git checkout develop
   # Review and finalize Phase 2 content
   # Test locally
   ```

2. **Merge to main**:
   ```bash
   git checkout main
   git merge develop --no-ff -m "Release: Phase 2 Essential Skills"
   git push origin main
   ```

3. **In main repository**:
   ```bash
   cd ..
   git submodule update --remote content
   git add content
   git commit -m "Deploy: Phase 2 Essential Skills"
   git push origin main
   ```

4. **Update sidebar** (in main repo `sidebars.ts`):
   ```typescript
   courseSidebar: [
     'course/index',
     { category: 'Phase 1: Foundations', items: [...] },
     { category: 'Phase 2: Essential Skills', items: [...] }, // ✅ Uncomment
   ]
   ```

5. **Cloudflare Pages** automatically builds and deploys

---

## Main Repository Submodule Reference

**Current Pointer**: `3993ade` (old version, before branch restructure)

**Why not updated yet?**:
- Waiting for阶段 3: Scripts creation
- Will test deployment flow in阶段 6
- Manual control to avoid accidental deployment

**To update manually**:
```bash
cd content && git checkout main && git pull
cd .. && git add content
git commit -m "Update: Sync content submodule"
git push origin main
```

---

## Coming Soon Content

**Location**: `docs/course/index.md` (present in both branches)

**Content**:
- Phase 2: Essential Skills - Coming Soon alert
- Phase 3: Building Projects - Coming Soon alert
- Phase 4: Specialization - Coming Soon alert
- Phase 5: Career - Coming Soon alert

**Purpose**:
- Inform users about upcoming content
- Build anticipation
- Link to GitHub Discussions for updates

**When to Remove**:
- After Phase 2-5 are released
- Replace Coming Soon with actual course links

---

## Quality Assurance

### Pre-Release Checklist for Phase 2-5

- [ ] Content reviewed for accuracy
- [ ] All lesson frontmatter correct
- [ ] Links within lessons tested
- [ ] Chinese translations complete (if applicable)
- [ ] Local build test passed
- [ ] Sidebar configuration prepared
- [ ] Coming Soon alerts removed/updated

### Testing Commands

```bash
# Test local build
cd <main-repo>
npm run build

# Preview locally
npm run serve

# Check for broken links (build will fail)
# Docusaurus has onBrokenLinks: 'throw'
```

---

## Notes

- **Security**: Phase 2-5 content NOT accessible via direct URLs in production
- **SEO**: No accidental indexing of draft content
- **Git History**: Content preserved in develop branch, can always merge back
- **Flexibility**: Can selectively release phases (e.g., Phase 2 only, then Phase 3 later)

## Questions?

See `BRANCHING_STRATEGY.md` for detailed workflow documentation.
