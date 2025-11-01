# Cloudflare Pages Deployment Guide

This document provides complete instructions for deploying the AI Coding Club website to Cloudflare Pages.

## Table of Contents

1. [Overview](#overview)
2. [Prerequisites](#prerequisites)
3. [Initial Setup](#initial-setup)
4. [Deployment Configuration](#deployment-configuration)
5. [Build Process](#build-process)
6. [Environment Variables](#environment-variables)
7. [Verification Steps](#verification-steps)
8. [Troubleshooting](#troubleshooting)
9. [Build Performance](#build-performance)
10. [Continuous Deployment](#continuous-deployment)

## Overview

The AI Coding Club website is deployed to **Cloudflare Pages**, a JAMstack platform that:

- Automatically deploys on every `git push` to the `main` branch
- Provides instant previews for pull requests
- Uses global CDN for fast content delivery
- Includes DDoS protection and security features
- Offers free tier with 500 builds per month

**Current Status:**
- Production URL: `https://aicodingclub-xxx.pages.dev` (to be bound to custom domain)
- Build time: ~3-5 minutes
- Deployment frequency: Automatic on every push to main

## Prerequisites

### Required Accounts
- **Cloudflare Account**: Free tier or higher (https://dash.cloudflare.com)
- **GitHub Account**: With access to `IsaacZhaoo/aicodingclub` repository

### Local Requirements
- **Node.js**: v20 LTS or higher
- **npm**: v9 or higher
- **Git**: For version control

### Repository Requirements
- Repository must be public OR Cloudflare GitHub app must have access to private repos
- `main` branch must be stable and buildable
- `package-lock.json` must be committed (ensures reproducible builds)

## Initial Setup

### Step 1: Authorize Cloudflare GitHub App

1. Go to https://dash.cloudflare.com
2. Navigate to **Pages** in the sidebar
3. Click **Create a project** > **Connect to Git**
4. Select **GitHub** as the Git provider
5. Click **Authorize GitHub** (if not already authorized)
6. In GitHub, authorize Cloudflare to access your repositories
   - For **public repos**: automatic access
   - For **private repos**: grant explicit access during authorization

### Step 2: Connect Repository

1. In Cloudflare Pages, click **Connect to Git**
2. Search for `aicodingclub` repository
3. Select `IsaacZhaoo/aicodingclub`
4. Click **Connect**

### Step 3: Configure Build Settings

Cloudflare Pages will show a configuration form. Use these exact settings:

| Setting | Value | Notes |
|---------|-------|-------|
| **Project name** | `aicodingclub` | Used in preview URLs |
| **Production branch** | `main` | Only main branch triggers production deploy |
| **Build command** | `npm ci && npm run build && npx pagefind --site build` | See Build Process section |
| **Build output directory** | `build` | Docusaurus output directory |
| **Root directory** | (leave empty) | Use repository root |

### Step 4: Set Environment Variables

Click **Advanced** > **Environment variables** and add:

| Name | Value | Environment |
|------|-------|-------------|
| `NODE_VERSION` | `20` | Production & Preview |
| `NPM_FLAGS` | `--prefer-offline --no-audit` | Production & Preview |

**Why these variables?**
- `NODE_VERSION=20`: Ensures v20 LTS is used (matches our `package.json` requirement)
- `NPM_FLAGS`: Speeds up builds by using cache and skipping audit

### Step 5: Save and Deploy

1. Click **Save and Deploy**
2. Cloudflare immediately triggers the first build
3. Watch build logs in real-time
4. First build typically completes in 3-5 minutes

**Build URL Format:** `https://aicodingclub-[hash].pages.dev`

Save this URL! It's your preview/production site.

## Deployment Configuration

### Configuration Files

This project uses minimal configuration to work with Cloudflare Pages:

**wrangler.toml** (Cloudflare configuration)
```toml
name = "aicodingclub"
[build]
command = "npm ci && npm run build && npx pagefind --site build"
output_dir = "build"
[env.production]
vars = { NODE_VERSION = "20", NPM_FLAGS = "--prefer-offline --no-audit" }
```

**package.json** (Build scripts)
```json
{
  "scripts": {
    "build": "docusaurus build"
  },
  "engines": {
    "node": ">=20.0"
  }
}
```

### No Additional Configuration Needed

Unlike Vercel or Netlify, Cloudflare Pages requires minimal configuration:
- No `vercel.json` or `netlify.toml` required
- Settings are configured in Cloudflare dashboard
- GitHub integration is automatic via Cloudflare GitHub app
- Environment variables are stored securely in Cloudflare

## Build Process

### Build Command Breakdown

```bash
npm ci && npm run build && npx pagefind --site build
```

This command runs three steps in sequence:

#### 1. `npm ci` (Clean Install)
```bash
npm ci
```
- Installs dependencies using exact versions from `package-lock.json`
- Faster and more reliable than `npm install`
- Ensures reproducible builds across environments
- Takes ~1-2 minutes

**Why `npm ci` instead of `npm install`?**
- `npm install` can upgrade packages, causing non-deterministic builds
- `npm ci` uses locked versions from `package-lock.json`
- Cloudflare caches `node_modules`, so ci is very fast on rebuilds

#### 2. `npm run build` (Docusaurus Build)
```bash
npm run build
```
- Runs Docusaurus build script (defined in `package.json`)
- Converts Markdown files to static HTML
- Bundles CSS, JavaScript, and assets
- Outputs to `build/` directory
- Takes ~1-2 minutes

**What gets built:**
- Static HTML pages for all documentation
- Blog posts from `blog/` directory
- React components from `src/pages/`
- CSS and JavaScript bundles
- Optimized images (using Docusaurus plugin)

#### 3. `npx pagefind --site build` (Search Indexing)
```bash
npx pagefind --site build
```
- Generates static search index
- Creates `build/pagefind/` directory with search data
- Enables client-side search without backend
- Takes ~30 seconds

**Note:** Pagefind runs now but won't be used until search page is implemented in a future task.

### Total Build Time

- **First build**: 3-5 minutes (includes npm install from scratch)
- **Subsequent builds**: 1-3 minutes (cached `node_modules`)
- **SLA target**: < 5 minutes

If build exceeds 5 minutes, check:
1. Network connectivity in Cloudflare
2. Cloudflare status page for incidents
3. Local build time: run `npm run build` locally to compare

## Environment Variables

### Production Environment

Set in Cloudflare Pages dashboard under project settings:

| Variable | Value | Purpose |
|----------|-------|---------|
| `NODE_VERSION` | `20` | Ensures Node v20 LTS is used |
| `NPM_FLAGS` | `--prefer-offline --no-audit` | Speeds up builds |

### Preview Environment

- Pull request deployments inherit production environment variables
- Can be overridden per-branch in Cloudflare dashboard (advanced)

### Application-Level Variables (Optional)

For Docusaurus-specific configuration, edit `docusaurus.config.ts`:

```typescript
export default {
  baseUrl: process.env.BASE_URL || '/',
  projectName: process.env.PROJECT_NAME || 'aicodingclub',
  // ...
}
```

Then add to Cloudflare environment variables:
```
BASE_URL = /
PROJECT_NAME = aicodingclub
```

Currently not needed, but available for future customization.

## Verification Steps

### After Deployment

Follow these steps to verify your deployment:

#### 1. Check Build Status

1. Go to https://dash.cloudflare.com
2. Click **Pages** > **aicodingclub**
3. View **Deployments** tab
4. Click most recent deployment
5. Check status:
   - ✅ **Success**: Build completed without errors
   - 🔄 **In Progress**: Still building (wait for completion)
   - ❌ **Failed**: See troubleshooting section

#### 2. Review Build Logs

1. Click deployment to view logs
2. Look for:
   - ✅ `npm ci` completed successfully
   - ✅ `npm run build` completed successfully
   - ✅ `pagefind` completed successfully
   - ⚠️ Any warnings (usually safe to ignore)
   - ❌ Any errors (see troubleshooting)

#### 3. Test Preview URL

1. Find preview URL in deployment details
   - Format: `https://aicodingclub-[hash].pages.dev`
2. Visit the URL in browser
3. Check:
   - [ ] Homepage loads correctly
   - [ ] CSS styles are applied
   - [ ] Navigation works
   - [ ] Images load properly
   - [ ] No broken links (404 errors)
   - [ ] No errors in browser console (F12)

#### 4. Check Browser Console

1. Open deployment URL
2. Press `F12` to open browser console
3. Check for errors:
   - Red errors: Indicate problems
   - Yellow warnings: Usually safe to ignore
   - Blue messages: Informational

**Common safe warnings:**
```
[Deprecation] Non-Error promise rejections are deprecated in Chrome and will be disallowed in error...
```

**Errors to investigate:**
```
Failed to load resource: the server responded with a status of 404
Uncaught TypeError: Cannot read property '...' of undefined
```

#### 5. Test Key Features

- [ ] Click links to ensure routing works
- [ ] Check English and Chinese versions
- [ ] Test search (once implemented)
- [ ] Test responsive design (mobile, tablet, desktop)

### Continuous Monitoring

After initial verification, monitor:

1. **Build Success Rate**: Should be 95%+ (target 100%)
2. **Build Time**: Should be < 5 minutes consistently
3. **Error Logs**: Review after each significant code change
4. **Uptime**: Cloudflare dashboard shows uptime statistics

## Troubleshooting

### Build Fails: Module Not Found

**Error Message:**
```
npm ERR! code E404
npm ERR! 404 Not Found - GET https://registry.npmjs.org/@docusaurus%2Fcore
```

**Causes:**
- Network issue in Cloudflare environment
- `npm ci` failed before build command
- Corrupted `package-lock.json`

**Solutions:**
1. Check Cloudflare status page for incidents
2. Verify `package-lock.json` is committed to repo
3. Rebuild in Cloudflare dashboard (click **Retry build**)
4. Run `npm install` locally and recommit `package-lock.json`:
   ```bash
   npm install
   git add package-lock.json
   git commit -m "Update package-lock.json"
   git push
   ```

### Build Timeout (> 10 minutes)

**Cause:** Large dependencies or network issues

**Solutions:**
1. Check network connectivity: Use faster NPM mirror
   ```bash
   npm config set registry https://registry.npmmirror.com
   npm install
   ```
2. Increase build timeout in Cloudflare (if available)
3. Check if dependencies have issues: run locally
   ```bash
   time npm ci
   ```

### Pagefind Not Found

**Error Message:**
```
npm ERR! 404 Not Found - GET https://registry.npmjs.org/pagefind
```

**Cause:** Pagefind not installed or not in `package.json`

**Solution:** Verify pagefind is in `devDependencies`:
```bash
npm install --save-dev pagefind
npm install
git add package-lock.json package.json
git commit -m "Add pagefind to devDependencies"
git push
```

### Preview URL Shows 404

**Cause:** Incorrect build output directory

**Solutions:**
1. Verify output directory is `build` in Cloudflare settings
2. Check Docusaurus outputs to correct directory:
   ```bash
   npm run build
   ls -la build/   # Should contain index.html
   ```
3. If Docusaurus outputs elsewhere, check `docusaurus.config.ts`

### Site Styles Missing (Broken CSS)

**Symptoms:** Site loads but looks unstyled

**Causes:**
- Incorrect base URL
- CSS not compiled during build
- Asset paths broken

**Solutions:**
1. Check `docusaurus.config.ts` for correct `baseUrl`
2. Verify `npm run build` includes CSS:
   ```bash
   npm run build
   ls -la build/assets/  # Should contain .css files
   ```
3. Check browser network tab (F12 > Network) for 404s on CSS files

### Build Takes Too Long

**Target:** < 5 minutes per build

**If builds are slower:**
1. Check if dependencies are increasing unnecessarily
2. Review recent commits for large additions
3. Check Cloudflare dashboard for system issues
4. Consider splitting into smaller build steps

**Optimization tips:**
- Use `npm ci` (✓ already doing)
- Keep dependencies minimal
- Use tree-shaking for unused code
- Enable gzip compression in Cloudflare

### Deployment Shows as Stalled

**Symptoms:** Build shows "In Progress" for > 10 minutes

**Solutions:**
1. Wait up to 15 minutes (sometimes slow)
2. Click **Rebuild** in Cloudflare dashboard
3. Check repository for large files being pushed
4. Contact Cloudflare support if persistent

## Build Performance

### Current Performance

- **Average build time**: 3-4 minutes
- **First build**: 4-5 minutes (fresh `node_modules`)
- **Rebuilds**: 2-3 minutes (cached `node_modules`)
- **Target SLA**: < 5 minutes

### Performance Metrics

Track in Cloudflare dashboard:
1. Click **Pages** > **aicodingclub** > **Analytics**
2. View:
   - Build count per month
   - Average build time
   - Build success rate
   - Total build minutes used

### Optimization Opportunities

**Current:** No optimization implemented (keep simple initially)

**Future optimizations** (if needed):
1. Monorepo structure (split docs and blog)
2. Incremental builds (Docusaurus 4.0+)
3. Parallel build steps
4. External asset CDN (for images)
5. Server-side search indexing

## Continuous Deployment

### Automatic Deployments

Every `git push` to `main` branch triggers:
1. GitHub webhook to Cloudflare
2. Build starts immediately
3. Build logs stream to Cloudflare dashboard
4. Upon success, deployment goes live

**Deployment is immediate** - no manual steps required!

### Pull Request Previews

Every pull request automatically gets:
1. Unique preview URL (e.g., `pr-123.aicodingclub-xxx.pages.dev`)
2. Automatic build with same configuration
3. Comment on PR with preview link
4. Automatic cleanup when PR closes

**To test PR previews:**
1. Create feature branch
2. Make changes and commit
3. Push to GitHub: `git push origin feature-branch`
4. Open pull request
5. Cloudflare bot comments with preview URL
6. Click preview link to test changes

### Manual Trigger

To manually rebuild without new commits:
1. Go to https://dash.cloudflare.com
2. Click **Pages** > **aicodingclub** > **Deployments**
3. Find deployment to rebuild
4. Click **...** > **Retry build**

### Rollback

To rollback to previous deployment:
1. Go to **Deployments** tab
2. Find desired previous deployment
3. Click **...** > **Rollback to this deployment**
4. Site immediately switches to previous version

**Note:** Rollback doesn't revert git history, just points CDN to previous build.

## Next Steps

1. **Verify** first deployment using Verification Steps above
2. **Test** by visiting preview URL in browser
3. **Monitor** build logs for 24 hours
4. **Document** preview URL in project README
5. **Next task:** Bind custom domain `aicoding.club` (Task #4)

## Support & Resources

### Cloudflare Documentation
- [Cloudflare Pages Docs](https://developers.cloudflare.com/pages/)
- [Build Configuration](https://developers.cloudflare.com/pages/configuration/build-configuration/)
- [Deployments](https://developers.cloudflare.com/pages/platform/deployments/)
- [Custom Domains](https://developers.cloudflare.com/pages/configuration/custom-domains/)

### Docusaurus Documentation
- [Docusaurus Deployment](https://docusaurus.io/docs/deployment)
- [Docusaurus Build](https://docusaurus.io/docs/docusaurus-core#build)

### Local Testing

Test the build process locally:

```bash
# Install dependencies
npm ci

# Build Docusaurus
npm run build

# Generate search index
npx pagefind --site build

# Test locally
npm run serve
```

Visit `http://localhost:3000` to test production build locally.

## Contact

For issues or questions:
1. Check this guide's troubleshooting section
2. Review Cloudflare build logs
3. Check GitHub Actions logs (if using CI/CD)
4. Contact project maintainers

---

## Additional External Services Setup

### Domain Setup

**Required for Production:**
1. Purchase domain `aicoding.club` from Cloudflare Registrar (~$12/year)
2. Add custom domain in Cloudflare Pages dashboard
3. Cloudflare automatically configures DNS and HTTPS

### Substack Newsletter

**Optional but Recommended:**
1. Create account at https://substack.com
2. Setup newsletter: "AI Coding Club Newsletter"
3. Get embed code from Settings → Publication details
4. Add to `docusaurus.config.ts` footer section

### Resource Database (Notion/Airtable)

**For Content Management:**

**Notion Option:**
- Create database with columns: URL, Title, Stage, Rating, Why Recommended, Category
- Share with team for collaborative curation
- Free tier sufficient

**Airtable Option:**
- Similar schema to Notion
- Better for collaboration and API integration
- Free tier includes 1,200 records

**Database Schema:**
```
- URL (URL type)
- Title (Title/Text)
- Stage (Select: Stage 0, Stage 1, Stage 2)
- Rating (Select: ⭐⭐⭐⭐⭐, ⭐⭐⭐⭐, ⭐⭐⭐)
- Why Recommended (Long text)
- Category (Multi-select: Video, Article, Tutorial, Tool)
- Duration (Text) - for videos
- Platform (Text)
- Date Added (Date)
```

### Cost Summary

| Service | Cost | Frequency |
|---------|------|-----------|
| Cloudflare Pages | $0 | Free tier |
| Domain (optional) | $12 | Annual |
| Substack | $0 | Free |
| Notion/Airtable | $0 | Free tier |
| **Total** | **$0-12** | **Annual** |

---

**Last Updated:** October 26, 2025
**Deployment Platform:** Cloudflare Pages
**Node Version:** 20 LTS
**Build Command:** `npm ci && npm run build && npx pagefind --site build`
