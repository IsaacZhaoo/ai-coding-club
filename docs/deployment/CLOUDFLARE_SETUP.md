# Cloudflare Pages Setup Guide

This guide provides step-by-step instructions to connect the AI Coding Club repository to Cloudflare Pages for automatic deployments.

## Prerequisites

- Cloudflare account (free tier sufficient)
- GitHub account with access to `IsaacZhaoo/aicodingclub` repository
- Browser (Chrome, Firefox, Safari, or Edge)

**Time required:** ~10 minutes

## Step-by-Step Setup

### Step 1: Access Cloudflare Dashboard

1. Go to https://dash.cloudflare.com/
2. Log in with your Cloudflare account
   - If you don't have an account, click **Sign up** and create one (free)
3. You should see the main dashboard

### Step 2: Navigate to Pages

1. In the left sidebar, click **Pages**
2. Click **Create a project** button
3. Select **Connect to Git**

### Step 3: Authorize GitHub

1. Click **GitHub** as the Git provider
2. Click **Authorize GitHub**
3. You'll be redirected to GitHub OAuth authorization screen
4. Click **Authorize cloudflare**
5. Enter your GitHub password if prompted
6. Review permissions (Cloudflare needs access to your repositories)
   - **For public repos**: Automatically granted
   - **For private repos**: You must grant explicit access to `IsaacZhaoo/aicodingclub`
7. Click **Authorize cloudflare**
8. Return to Cloudflare Pages

### Step 4: Select Repository

1. Search for **aicodingclub** repository
2. Click on `IsaacZhaoo/aicodingclub` to select it
3. Click **Connect**

### Step 5: Configure Build Settings

Cloudflare will show a configuration form. Fill in these exact values:

| Field | Value |
|-------|-------|
| **Project name** | `aicodingclub` |
| **Production branch** | `main` |
| **Build command** | `npm ci && npm run build && npx pagefind --site build` |
| **Build output directory** | `build` |
| **Root directory** | (leave empty) |

**Important:** Copy the build command exactly as shown above (no modifications).

### Step 6: Set Environment Variables

1. Scroll down to **Advanced build settings**
2. Click **Environment variables**
3. Add two environment variables:

**Variable 1: NODE_VERSION**
- Name: `NODE_VERSION`
- Value: `20`
- Environment: `Production` and `Preview`

**Variable 2: NPM_FLAGS**
- Name: `NPM_FLAGS`
- Value: `--prefer-offline --no-audit`
- Environment: `Production` and `Preview`

**Why these variables?**
- `NODE_VERSION=20`: Ensures Node.js v20 LTS is used (required by our project)
- `NPM_FLAGS`: Optimizes build performance by using cached packages and skipping npm audit

### Step 7: Save and Deploy

1. Click **Save and Deploy** button
2. Cloudflare immediately triggers the first build
3. You'll see the build status page with real-time logs
4. Wait for the build to complete (typically 3-5 minutes)

**Build statuses:**
- 🟦 **Blue (In Progress)**: Build is running
- 🟩 **Green (Success)**: Build completed successfully
- 🟥 **Red (Failed)**: Build encountered an error

### Step 8: Get Your Preview URL

1. Once the build succeeds (green status), you'll see:
   ```
   Your site is live at: https://aicodingclub-[random-hash].pages.dev
   ```
2. **Save this URL!** This is your preview/production website.
3. Click the URL to open your site in a new tab

### Step 9: Verify the Deployment

Visit your deployment URL and verify:

- [ ] Homepage loads without errors
- [ ] Styles are applied (not plain white with black text)
- [ ] Images load correctly
- [ ] Navigation links work
- [ ] No errors in browser console (F12 > Console tab)

## What Happens Now

### Automatic Deployments

Every time you push to the `main` branch:
1. GitHub sends webhook to Cloudflare
2. Cloudflare automatically starts a build
3. Build command runs: `npm ci && npm run build && npx pagefind --site build`
4. Upon success, changes go live immediately
5. No manual steps required!

### Pull Request Previews

Every pull request gets:
1. Automatic build with preview URL
2. Preview URL posted as comment on PR
3. Anyone can click preview URL to test changes
4. No special configuration needed

### Manual Rebuild

To rebuild without new commits:
1. Go to https://dash.cloudflare.com
2. Click **Pages** > **aicodingclub**
3. Click **Deployments** tab
4. Find a deployment
5. Click **...** (three dots)
6. Select **Retry build**

## Troubleshooting

### Authorization Failed: "Insufficient permissions"

**Cause:** Cloudflare GitHub app doesn't have access to the repository

**Solution:**
1. Go to GitHub Settings > Developer settings > OAuth Apps
2. Find "Cloudflare Pages"
3. Click to manage
4. Grant access to `IsaacZhaoo/aicodingclub`

Alternatively:
1. Go to your GitHub repository settings
2. **Settings** > **Integrations & services**
3. Look for Cloudflare and verify it's authorized

### Build Fails: "npm ci: Module not found"

**Cause:** Dependencies not installing properly

**Solution:**
1. Ensure `package-lock.json` is committed to the repository
2. Try rebuilding in Cloudflare dashboard (Retry build)
3. If still failing, run locally and recommit package-lock.json:
   ```bash
   npm install
   git add package-lock.json
   git commit -m "Update package-lock.json"
   git push
   ```

### Build Fails: "pagefind: command not found"

**Cause:** Pagefind not installed in `devDependencies`

**Solution:**
```bash
npm install --save-dev pagefind
npm install
git add package-lock.json package.json
git commit -m "Add pagefind to devDependencies"
git push
```

### Preview URL Shows 404

**Cause:** Build output directory configured incorrectly

**Solution:**
1. In Cloudflare, verify **Build output directory** is set to `build`
2. Run build locally to verify:
   ```bash
   npm run build
   ls build/index.html  # Should exist
   ```

### How Long Does It Take?

- **Initial setup:** ~10 minutes
- **First build:** 3-5 minutes
- **Subsequent builds:** 2-3 minutes
- **After live:** Automatic on every push

## What's Next?

1. ✅ Repository connected to Cloudflare Pages
2. ✅ Build configured and working
3. ⏳ Test the preview URL from Step 8
4. 📝 Share preview URL with team (format: `https://aicodingclub-[hash].pages.dev`)
5. 🔗 Next task: Bind custom domain `aicoding.club` (Task #4)

## Advanced: CLI Setup (Optional)

If you prefer command-line setup, you can use Wrangler CLI:

```bash
# Install Wrangler
npm install --save-dev wrangler

# Authenticate with Cloudflare
npx wrangler login

# Deploy to Pages
npx wrangler pages deploy build
```

However, **GitHub integration is recommended** for automatic deployments.

## Support & Documentation

- **Cloudflare Pages Docs:** https://developers.cloudflare.com/pages/
- **Cloudflare GitHub Integration:** https://developers.cloudflare.com/pages/configuration/git-integration/
- **Build Configuration:** https://developers.cloudflare.com/pages/configuration/build-configuration/
- **Troubleshooting:** https://developers.cloudflare.com/pages/troubleshooting/

## Summary

After completing these steps:
- ✅ GitHub repository connected to Cloudflare Pages
- ✅ Build command configured: `npm ci && npm run build && npx pagefind --site build`
- ✅ Environment variables set (Node 20, npm flags)
- ✅ First deployment successful
- ✅ Preview URL available
- ✅ Automatic deployments on every git push

**All configuration is complete!** Your site is now automatically deploying whenever you push to `main`.

---

**Document Version:** 1.0
**Last Updated:** October 25, 2025
**Repository:** IsaacZhaoo/aicodingclub
**Deployment Platform:** Cloudflare Pages
