---
sidebar_position: 6
sidebar_label: 'Deploying Your Project: Going Live'
title: 'Deploying Your Project: Going Live'
description: 'Drop a plain folder onto Netlify and share a link that works for anyone without needing Git or build tools.'
---

> TL;DR: Drag your HTML folder onto Netlify, wait for the URL to appear, and test it in a fresh browser profile.

## Key steps
1. Prepare a clean project folder with index.html at the root.
2. Upload the whole folder to Netlify via the manual drop interface.
3. Make the site public and verify it opens without login for a new visitor.
4. Confirm where your saved data lives (localStorage) and how to export/restore across profiles.

## Practice
- Publish a simple HTML/CSS/JS project you created, write down its final URL, and test it in an Incognito window and a fresh browser profile on another device (if possible).

What good is a great tool if you can’t share it? Deployment is simply making your application reachable by others over the internet. For static frontends—HTML, CSS, JavaScript—you do not need complex pipelines or a Git repository. A simple folder upload works, and for this lesson we’ll use Netlify’s manual drop method.

### Why Netlify for this example
Netlify lets you deploy a plain HTML project from your computer without Node.js, build steps, or configuration. It’s fast, supports HTTPS out of the box, and keeps the example focused on publishing a working link and understanding what travels with it (and what doesn’t).

- You’ll keep using one main production URL.
- The steps mirror real workflows (drop folder → wait → open URL).
- We’ll clarify data boundaries: your saved records live in the visitor’s browser, not in the deployed files.

### Prepare your project folder
1. Create a fresh folder named `expense-site`.
2. Place `index.html` in the root directory of a single folder. You may include additional assets (CSS, JS, images) alongside it, but keep them within this same folder.
3. Include all referenced CSS, JavaScript, and images inside that same folder structure with matching casing.
4. Ensure the main file is named `index.html` (not `index.html.txt`).

For this tutorial, use a complete single-file HTML example so no assets get lost. You can save the following source directly as `expense-site/index.html`:

- Source: https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/expense-tool.html
  - Click the link to view raw HTML.
  - Save it as `index.html` in your `expense-site` folder.

This file includes inline CSS and JavaScript, so it will work immediately when deployed.

### Deploy with Netlify (manual drop)
1. Open [https://app.netlify.com/drop](https://app.netlify.com/drop).
2. Log in to the Netlify team where you’ll manage this project.
3. Drag the entire `expense-site` folder into the Drop zone. Important: upload the `expense-site` folder itself, not a parent folder that contains another nested structure.
4. Wait for the deployment to finish (usually a minute or two).
5. Netlify will display your project’s main HTTPS URL ending in `netlify.app`; open that link to verify it loads correctly.

That’s it—your tool is now live on the web.

### Make sure visitors can actually see it
Your site’s public or private status is controlled by your Netlify team’s project defaults and plan; new projects can start private, so a successful deploy alone does not guarantee visitors can see it.

1. Go to your project in [https://app.netlify.com](https://app.netlify.com).
2. If the site shows a lock icon or login prompt to visitors:
   - Select **Make public** for the current production deployment, or
   - Navigate to **Project configuration → General → Visitor access → Project visibility** and set it to public.
3. Choose your project name before creating example records, because changing the hostname changes the storage origin; if you need to move them, export from the old address/profile and explicitly restore at the new address.

### Verify with a real visitor (or “fresh” browser)
Share the final Netlify URL and confirm it works for someone without your credentials:

1. Open the main production URL in:
   - Another browser, or
   - A separate browser profile not logged into Netlify.
2. The page should load completely with styles and script behavior intact.
3. Add a few fictional records using the tool:
   - 2026-11-01 / Lunch / 12.50
   - 2026-11-02 / Bus / 8.00
   - 2026-11-03 / Notebook / 5.00
4. Confirm the total reflects CNY 25.50.
5. Refresh and check again to ensure data persists.

Now try it from a different browser profile (or Incognito window) at the same URL:

- You should start with an empty list.
- This confirms that saved records are tied to a specific browser profile, not to the deployed site itself.

### What travels and what doesn’t
Only the program files travel to Netlify: the HTML and any CSS, JavaScript, or images bundled in the uploaded folder. In this expense-tool reference, that’s just `index.html` containing the page logic.

Your saved expense records live separately as browser `localStorage` data tied to your current profile and origin. Uploading this reference `index.html` does not upload those previously saved browser records.

If you export your data, you get a readable JSON file. That export does not automatically upload or sync with the deployed site. Keep any exported JSON outside the uploaded folder.

Other apps might embed records in source files or send records over the network; that behavior is up to those apps. This reference’s simple “index.html only” pattern doesn’t define how more complex tools handle persistence.

### Where your saved records live
localStorage is scoped by:

- Origin (scheme + hostname + port)
- Browser profile
- Not by URL path alone—changing only the path does not create separate storage.
- Local file mode behavior depends on the browser; don’t generalize it to production hosting.

Key rules for your tests and real use:

- A new browser profile at the same Netlify URL starts empty.
- A second tab in the same profile is not an independent data test.
- localhost, file:// URLs, and HTTPS production sites do not share localStorage automatically.
- Separate devices, custom domains, or HTTP vs HTTPS also isolate storage.

### Exporting and restoring records (brief)
1. In the old/original browser profile, open the original expense-tool address and export your records to a JSON file on disk. Save that JSON outside the expense-site folder.
2. In your destination browser profile, locate and open the published main URL from Netlify; if that profile already contains the specific records you intend to keep, export them immediately—these are the pre-existing destination records, distinct from any data in the old source browser—before choosing a backup file to restore.
3. In the tool’s restore control, select the saved JSON. Confirm and note: restore replaces the entire current snapshot—it does not merge with existing records.
4. After restoring, carefully check every field, counts, and the CNY total. Refresh the page to ensure consistency.
5. Remember: your exported JSON is readable and unencrypted. Friends testing the tool can enter their own fictional records; you don’t need to share your personal data.

For more details on backup strategies with this kind of local-storage tool, see: https://aicoding.club/docs/tutorials/html-tool-backup-restore/

### Updating your deployed project
When you change the HTML/JS/CSS:

1. Update `index.html` (and assets) in your local `expense-site` folder.
2. Go to your Netlify project’s **Deploys** page.
3. Drag the updated `expense-site` folder into the deploy dropzone for that same project.
4. Open the main URL again, check the visible change, and repeat a data check if needed.
5. Keep a copy of the previous working version before updating.

Important notes on updates:

- An update is not a backup. Always export any important user records first (if applicable).
- If you change storage keys or formats in the tool, existing localStorage may become invalid.
- Compatibility and graceful behavior are your responsibility when evolving the app.

### Troubleshooting checklist
Use this when something doesn’t behave as expected:

- **404 or blank page**:
  - Confirm `index.html` exists at the upload root with lowercase spelling.
  - Check that all deployed files (CSS, JS, images) are present and reachable via browser dev tools.
- **Missing styles/images**:
  - Ensure all assets are included in the same relative folder structure.
  - Pay attention to filename casing; paths are case-sensitive on most servers.
- **Login screen for a visitor**:
  - Project visibility is private; set it to public (see earlier step).
- **Records missing after moving profiles or addresses**:
  - localStorage is tied to the original origin and profile; use export/restore to move data intentionally.
- **AI assistance**:
  - If you ask an AI for help, provide: exact visible error, folder tree, main URL, asset paths that fail, and steps to reproduce. Keep credentials and personal data out.

### Final check and next action
You now have:

- A live Netlify URL reachable by anyone without logging in.
- A clear understanding of where saved records live and how to move them safely.

**Next actions:**
1. Open your new site’s main URL in a fresh browser profile and confirm it works.
2. Add a couple of test records, then export and restore them into a different profile.
3. Update the HTML (e.g., add a new input or layout tweak), re-deploy using the same Netlify project, and verify that old records still appear if you remain on the same origin/profile with an unchanged storage key and compatible format.

That’s deployment done: you’ve published a tool, checked its reachability, and mapped its data boundary with real behavior in hand.
