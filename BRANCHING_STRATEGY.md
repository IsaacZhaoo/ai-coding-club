# Branching Strategy

## Overview

This repository uses a simple, manual-control branching model optimized for content management and gradual releases.

## Branch Structure

```
main (production)
  ↑ Production content deployed to aicoding.club
  ↑ Only updated through manual merge from develop
  │
develop (staging)
  ↑ Daily development and testing
  ↑ Safe place to experiment with content
  │
feature/* (work branches)
  ↑ Individual features or content updates
  ↑ Merged into develop when ready
```

## Branch Purposes

### `main` (Production)
- **Purpose**: Production-ready content
- **Deployed to**: https://aicoding.club
- **Update frequency**: Only when intentionally releasing content
- **Protection**: Should have branch protection enabled (manual merges only)
- **Triggers**: Updating this branch triggers Cloudflare Pages deployment

### `develop` (Staging)
- **Purpose**: Daily development work and content testing
- **Deployed to**: Not deployed (local testing only)
- **Update frequency**: As often as needed
- **Protection**: None (free to push)
- **Use for**: Testing, drafting, experimentation

### `feature/*` (Feature branches)
- **Purpose**: Individual features, lessons, or content updates
- **Naming examples**:
  - `feature/coming-soon-phase-2`
  - `feature/lesson-git-basics`
  - `feature/tools-documentation`
- **Lifecycle**: Created → Merged to develop → Deleted
- **Protection**: None

## Workflows

### Daily Development
```bash
# Work on develop branch
git checkout develop
git pull origin develop

# Make changes, commit, push
git add .
git commit -m "Update: ..."
git push origin develop

# Test locally before releasing
```

### Feature Development
```bash
# Create feature branch from develop
git checkout develop
git checkout -b feature/my-feature

# Work on feature
git add .
git commit -m "Add: ..."
git push origin feature/my-feature

# Merge to develop when ready
git checkout develop
git merge feature/my-feature
git push origin develop

# Delete feature branch
git branch -d feature/my-feature
git push origin --delete feature/my-feature
```

### Release to Production
```bash
# Review changes
git checkout develop
git log main..develop --oneline

# Merge to main (manually)
git checkout main
git pull origin main
git merge develop --no-ff -m "Release: Description"

# Push to trigger deployment
git push origin main

# ⚠️ This triggers Cloudflare Pages deployment
# Main repo submodule must be updated separately
```

## Best Practices

### DO:
- ✅ Always work on `develop` or `feature/*` branches
- ✅ Test locally before merging to main
- ✅ Write descriptive commit messages
- ✅ Use `--no-ff` when merging to main (preserves history)
- ✅ Review changes with `git diff` before committing

### DON'T:
- ❌ Never push directly to `main` (always merge from develop)
- ❌ Don't merge unfinished work to `main`
- ❌ Don't force push to `main` or `develop`
- ❌ Don't delete `main` or `develop` branches

## Integration with Main Repository

This repository is a **Git submodule** of the main `aiCodingClub` repository.

### Deployment Process:
1. Content updated in this repo's `main` branch
2. Main repository manually updates submodule pointer
3. Main repository pushes to its `main` branch
4. Cloudflare Pages builds and deploys

**Note**: Changes to this repo do NOT automatically deploy. The main repository must explicitly update the submodule reference.

## Emergency Procedures

### Rollback Production
```bash
# Option 1: Revert last merge
git checkout main
git revert -m 1 HEAD
git push origin main

# Option 2: Reset to previous commit (⚠️ use with caution)
git checkout main
git reset --hard <commit-hash>
git push origin main --force
```

### Fix Broken Develop
```bash
# Reset develop to main
git checkout develop
git reset --hard main
git push origin develop --force
```

## Questions?

See the main repository's deployment documentation for the complete workflow.
