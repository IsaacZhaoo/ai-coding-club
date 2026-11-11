---
title: "Add Verifiable Data Backup & Restore to Your AI Coding Club Tool"
sidebar_label: "HTML Tool Backup & Restore"
description: "Add JSON backup and restore to a single-file HTML expense tracker, then verify three records, CNY 25.50, repeat imports, cancellation, and invalid files."
keywords: ["HTML tool backup", "localStorage JSON export", "restore browser data", "AI coding practice"]
sidebar_position: 51
tags: ["tutorial", "coding-assistant", "html", "backup"]
---

# Add Verifiable Data Backup & Restore to Your AI Coding Club Tool

Many small HTML tools you keep locally work beautifully—until you need to move them, test on another machine, or simply ensure nothing is lost if something goes wrong. Browser storage (localStorage) is convenient for daily use, but it stays tied to your current browser profile and origin. That means renaming a file, opening it in a different window, or using a private session can silently change what data you see—at least some of the time. Ordinary windows and tabs that share the same HTTP origin and browser profile do share their storage, so just changing the URL path isn’t enough to isolate data. For a direct local file, whether its storage “follows” the file is undefined across browsers, so renaming or moving it is not a guaranteed way to preserve its backing store. A separate profile or private context is genuinely different. See https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage for the exact rules.

This tutorial shows you how to add real backup and restore to a single HTML tool. The result: one tool that exports a portable JSON snapshot, restores records exactly as stored (no doubling, no leaks), and safely rejects bad files so your current notes never disappear.

We’ll use:
- Starter tool: <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/starter.html">starter.html</a>
- Reference completion: <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/expense-tool.html">expense-tool.html</a>
- Sample backup: <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/sample-backup.json">sample-backup.json</a>

No programming degrees required—just a terminal, a browser, and curiosity.

---

## 1. Set Up a Local Practice Environment

We’ll run the tool from your own folder so every step is reproducible and safe to break.

### Step-by-Step Setup

1. Create a new folder on your computer, e.g.:
   - Windows: `C:\Users\You\AI-CodingClub-Practice`
   - macOS/Linux: `/Users/you/AI-CodingClub-Practice`

2. Copy both starter and reference HTML files into this folder:
   - <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/starter.html">starter.html</a>
   - <a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/expense-tool.html">expense-tool.html</a>

3. Open a terminal in that folder. You must have Python 3 already installed on your system; if not, install it first. Then continue with your usual Python 3 commands.

   ```bash
   python3 -m http.server 8765 --bind 127.0.0.1
   ```

4. Keep this terminal running. In your browser, open:
   - Starter: `http://127.0.0.1:8765/starter.html`
   - Reference: `http://127.0.0.1:8765/expense-tool.html`

Notes:
- The server runs locally on your machine only. 127.0.0.1 means “this computer,” not the internet.
- Changing just the URL path (e.g., /starter.html vs /expense-tool.html) does NOT create separate localStorage at the same origin.
- For a true “empty environment” test later, open an empty private/incognito window and go to the same URL.

When done, stop the server with Ctrl+C.

---

## 2. Understand What We’re Adding: Backup vs Browser Storage

Your starter tool already saves records using localStorage under the key `aicodingclub-expenses-v1`. That’s fine for quick notes—but it’s not a backup you can:
- Download and keep separately.
- Move to another machine.
- Use in private windows without clearing your normal profile.

We want two things:
1. Export: a single JSON file that contains all current records, with metadata (app, version, currency).
2. Restore: a safe, verified import that replaces the entire current snapshot—after you confirm—so there’s no accidental merging or data loss.

The reference tool (<a href="https://raw.githubusercontent.com/IsaacZhaoo/ai-coding-club/f4546897549e20afde5d76e3ddf2ac5b6d668207/examples/html-tool-backup-restore/expense-tool.html">expense-tool.html</a>) implements this behavior. We’ll use it as the working model while we add the feature to our own copy.

---

## 3. Prepare Test Data: Three Exact Records in CNY

We’ll use a fixed set of three records so results are verifiable every time.

| Date       | Description | Amount (CNY) |
|------------|-------------|--------------|
| 2026-11-01 | Lunch       | 12.50        |
| 2026-11-02 | Bus         | 8.00         |
| 2026-11-03 | Notebook    | 5.00         |

Total: CNY 25.50
Count: 3

### Add the Records in Starter.html

In your browser, at `http://127.0.0.1:8765/starter.html`:

1. Add “Lunch”, amount 12.50, date 2026-11-01.
2. Add “Bus”, amount 8.00, date 2026-11-02.
3. Add “Notebook”, amount 5.00, date 2026-11-03.

Then refresh the page (same URL). You should still see the 3 entries, totaling CNY 25.50. This confirms localStorage persistence is working within the same profile and origin.

Now we’ll export this snapshot and prove it can restore exactly into a fresh environment.

---

## 4. Export: Create a Portable JSON Snapshot

We don’t need to build an upload server—exports and imports are entirely in the browser using JavaScript APIs that run inside your tool page.

### What a Valid Backup Looks Like

The reference tool saves backups as JSON with this structure:

```json
{
  "app": "aicodingclub-expenses",
  "version": 1,
  "currency": "CNY",
  "records": [
    {
      "id": "sample-1",
      "date": "2026-11-01",
      "label": "Lunch",
      "amountCents": 1250
    },
    {
      "id": "sample-2",
      "date": "2026-11-02",
      "label": "Bus",
      "amountCents": 800
    },
    {
      "id": "sample-3",
      "date": "2026-11-03",
      "label": "Notebook",
      "amountCents": 500
    }
  ]
}
```

Key points:
- `app` and `version` identify which tool created this snapshot.
- `currency` is stored so the tool knows how to interpret amounts.
- Each record has:
  - `id`: unique for that snapshot (IDs do not have to match sample-1/2/3).
  - `date`: real YYYY-MM-DD format.
  - `label`: nonempty description.
  - `amountCents`: positive integer representing cents (e.g., 1250 = CNY 12.50).

Constraints the reference enforces:
- At most 1,000 records per snapshot.
- Label ≤ 80 characters.
- Amount ≤ CNY 1,000,000 per record.
- File size ≤ 1 MiB.
- Only one supported app/version/currency combination.

### How to Export (Using the Reference as a Guide)

If you want to see this in action:

1. Open `http://127.0.0.1:8765/expense-tool.html`.
2. Click **Export backup**.
3. The browser downloads `expenses-backup.json` into Downloads.
4. Confirm the file exists by opening your system’s download folder.

That file is your portable snapshot. You can now close all tabs, clear your cache (images/resources), rename your HTML files, or open the tool in a different device entirely—provided that device runs a compatible version of this same app.

The export is purely client-side:
- Uses `Blob` and `URL.createObjectURL` to create a downloadable file.
- Saves the validated snapshot before writing to localStorage again (applies to restore, not export).
Export itself reads only the current in‑memory records, serializes them to a Blob, and requests a JSON download. It does not write to localStorage. The “write storage first, then change display” ordering applies when restoring, not when exporting.
- No server upload needed.

---

## 5. Restore: Safely Replace Your Current Data

Restoring is where safety matters most. We want:
- Validation first: no junk data written.
- A confirmation step: you choose “replace” or cancel.
- All-or-nothing: either the snapshot replaces everything, or nothing changes.

### What Happens on a Successful Restore

1. You choose **Choose a JSON backup to restore**.
2. The tool reads the selected file as text and validates it against the expected schema and constraints.
3. If valid, a dialog appears: “Restore this snapshot will replace all current records.”
4. On confirm:
   - The entire localStorage snapshot is replaced with the imported data.
   - The UI updates to show 3 records totaling CNY 25.50.

No merging, no partial writes, no silent overwrites.

### What Happens on Failure or Cancellation

- Wrong app/version/currency → rejected before confirmation.
- Missing fields (e.g., no `date` or `amountCents`) → rejected.
- Invalid JSON syntax → rejected.
- Duplicate IDs within the same snapshot → rejected.
- Oversized input or record limits exceeded → rejected.
- Storage write fails (quota, permission) → rejected.

In all these cases:
- Your current records stay intact.
- The display does not flicker into an empty state.
- Refreshing the page keeps your original data.

---

## 6. Live Proof: Export → Empty Profile → Restore → Verify

Now we’ll run a complete end-to-end test that you can reproduce yourself.

### Step 1: Export from a Known State

1. Make sure starter.html still shows exactly the 3 test records.
2. Open http://127.0.0.1:8765/expense-tool.html in the same normal browser profile and origin (use one editing tab). Share the records across tabs, then export from expense-tool.html there. The downloaded backup is named expenses-backup.json.
3. Download the file and confirm it exists in your Downloads folder (name may vary). Keep the original browser data intact.

This downloaded JSON is your “source of truth.”

### Step 2: Open a Fresh Environment

We need an environment that starts with zero records.

**Option A (recommended):** Use an empty private/incognito window.
1. Open a new private window in the same browser.
2. Navigate to `http://127.0.0.1:8765/expense-tool.html`.
   - It should display 0 records and total CNY 0.00.

**Option B (if you trust your own tool):** Use a fresh, identical copy of the HTML file in a separate browser profile, open the same reference URL there, and clear localStorage only in that new profile for that origin. This isolates the test environment without touching your original records. Private windows are simpler and safer. Never clear the only records from your main profile just to “prove” a backup works.

### Step 3: Restore from the Exported File

1. In the private window, click **Choose a JSON backup to restore**.
2. Select the exported `expenses-backup.json`.
3. Read the confirmation dialog carefully; it should state that this will replace all current records.
4. Confirm.

### Step 4: Verify the Results

After restoration:

- Record count: 3
- Total amount: CNY 25.50
- Each record’s fields:
  - Date, description, and amount exactly match the test set.
- Refresh the page (same URL in private window). The data persists.

This proves:
- The export captured the correct state.
- The restore replaced the empty environment precisely.
- No records were lost or duplicated.

### Step 5: Test Idempotency and Safety

1. Try importing the same backup again.
   - Result: still 3 records, CNY 25.50. No duplication.
2. Add a new record (e.g., “Coffee” CNY 4.00).
3. Now import the *old* backup again after confirming.
   - The snapshot replaces everything, including your new “Coffee” entry.
   - You should see back to exactly the 3 original records at CNY 25.50.
4. To keep both:
   - Before restoring an older snapshot, export your current state first.

### Step 6: Test Rejection of Invalid Files

To prove the tool never silently corrupts data:

1. Copy your valid `expenses-backup.json` to a new file called `bad-backup.json`.
2. Edit it slightly:
   - Change the existing `"version"` value from 1 to 2 in a copy (do not add a second duplicate version key), or
   - Remove the final `}` to break JSON syntax.
3. In a private window with 3 test records, try importing `bad-backup.json`.
4. Expected:
   - The tool rejects the file before confirming.
   - Your original 3 records remain visible.
   - After refresh, they’re still there.

This demonstrates that validation + cancellation = zero-data-loss behavior.

---

## 7. How to Ask an AI Coding Assistant for This Feature

If you want your own small tool to gain this behavior (like the reference), you can give an AI a complete copy of your HTML and ask it to add export and restore. A good prompt looks like:

> “Here is my self-contained HTML expense tool. Please add JSON export/restore with:
> - Export: save a validated snapshot including app='aicodingclub-expenses', version=1, currency=CNY, and all current records as a Blob download named expenses-backup.json.
> - Restore: read the uploaded file, validate schema (app/version/currency match, required fields, ID uniqueness, size limits), then ask user for explicit confirmation before replacing localStorage entirely.
> - On any validation or write error, keep current data and display intact; never auto-merge or partially update.”

Important reminders when working with an AI:
- Attach or paste the full HTML text—paths alone don’t help.
- Ask for a single HTML file with no external dependencies.
- Test by exporting from the main profile, then restoring in an independent empty profile or private window. Keep the downloaded backup and the original records intact.

The reference tool is one working example; results can vary depending on how the AI interprets your starter code.

---

## 8. Key Concepts in Plain Language

- **localStorage**: A browser feature that keeps small amounts of data tied to a specific website origin and browser profile. It persists across sessions but lives only as long as you don’t clear it, except when the browser or system removes it for other reasons. See https://developer.mozilla.org/en-US/docs/Web/API/Window/localStorage. Importantly, localStorage is not an independent backup; it can be lost without warning.
- **Origin**: The URL’s scheme + host + port, e.g., `http://127.0.0.1:8765`. Changing just the path (like /starter.html) does not separate storage.
- **Profile vs Private Session**: Normal tabs share localStorage; private/incognito windows usually keep their own isolated storage that disappears when the last private tab closes.
- **Snapshot Replacement**: Restore does not merge with existing records; it swaps the entire dataset, like replacing a notebook page instead of writing notes alongside them.
- **Validation**: Before touching your data, the tool checks that the backup is well-formed and compatible. This prevents corrupted or wrong-tool backups from breaking anything.

---

## 9. Best Practices for Using Backups

- Keep dated copies: `expenses-backup-2026-11-01.json`, etc., especially after major changes.
- Store backups in a safe place; they’re plain text, not encrypted.
- Test restores with fictional data before relying on them with important records.
- Remember: this setup adds no cloud sync, login recovery, or cross-device automatic sync. It gives you portable, verifiable snapshots of your local tool’s state.

---

## 10. Final Checklist

- [ ] Starter tool shows 3 test records totaling CNY 25.50.
- [ ] Exported JSON file exists in Downloads.
- [ ] Private window starts with 0 records.
- [ ] Restored snapshot shows exactly 3 records, correct fields and total.
- [ ] Refreshing preserves restored data.
- [ ] Re-importing the same backup keeps the same 3 records (no duplicates).
- [ ] Invalid backup is rejected and original data remains unchanged.

You now have a small HTML tool with verifiable data backup and restore—provable through export, restore into an empty environment, and safe rejection of bad files.
