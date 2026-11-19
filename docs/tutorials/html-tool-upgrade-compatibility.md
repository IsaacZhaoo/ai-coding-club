---
title: "V1 vs. V2: Spotting When Added Fields Break Compatibility in Your HTML Tool"
description: "Add a category to a single-file HTML expense tracker. Test an old backup, the first save, and what happens when you reopen the previous version."
tags: ["tutorial", "html", "backup"]
---

# V1 vs. V2: Spotting When Added Fields Break Compatibility in Your HTML Tool

This tutorial shows you how to restore a backup, add rows safely, and understand what happens when an old tool reads new data.

## Setup

1. Download the practice files: <a href="/examples/html-tool-upgrade-compatibility/expense-upgrade-exercise.zip" download="expense-upgrade-exercise.zip">expense-upgrade-exercise.zip</a>
2. Unzip into an empty folder.
3. In that folder, run: `python3 -m http.server 8765 --bind 127.0.0.1` (requires Python 3).
4. Open your browser at: `http://127.0.0.1:8765`.
5. For each trial, use a fresh browser profile and keep only one editing tab open.
6. After both trials, stop the server with Ctrl+C.

Every trial begins by opening **v1.html** in your new profile’s editing tab, then selecting **sample-backup.json** via the restore chooser and confirming replacement. You must verify these three facts before proceeding:

- The page loads with existing rows intact.
- The total shows CNY 25.50.
- Three rows are visible.

For adding a row in either trial, use:
- Date: `2026-11-04`
- Amount: `2.00`
Click Add; the revised page will set the category for you automatically.

## Trial 1: Understand Category Loss When Saving from v1

1. Open **same-version.html** in the same tab.
2. Add Coffee (date 2026-11-04, amount 2.00).
3. See Coffee appear as `general` by default.
4. Now open **v1.html** again and save Snack using the same date/amount settings.
5. Go back to **same-version.html**.

You should now see:
- Five rows total.
- A new total of CNY 29.50.
- Every category showing as `uncategorized`.

Key insight: Saving from v1 drops categories because v1 saves only the fields it recognizes. Merely opening v1 leaves stored data untouched; saving is what breaks the link to known categories.

## Trial 2: How Version 2 Protects Against Old Saves

Start a fresh browser profile.

1. Restore in **v1.html** again as before.
2. Open **v2.html**; it displays the three existing rows with default category `uncategorized` without saving anything.
3. Visit v1 again immediately—it still shows the three rows (no data lost yet).
4. In v2.html, include a Coffee item dated 2026-11-04 with amount 2.00 and then press Add, which automatically saves the updated record under the current storage key without requiring a separate Save button. This writes numeric version 2 under the same key.
5. Reload **v2.html**. Now you have four rows totaling CNY 27.50; original fields are intact and Coffee is `general`.
6. Open **v1.html** now. It cannot read those new rows, disables both editing and restore, but stored data remains untouched.
7. Return to **v2.html**; all four rows are still present.

The old HTML plus an old backup in a fresh profile give you the old snapshot. Use V2’s export to keep a copy of records added since then.

## Quick Checklist

- [ ] Same origin and browser profile used throughout
- [ ] Only one active editing tab at a time
- [ ] Known old data and backup available before testing
- [ ] Correct IDs/fields/default values set for new rows
- [ ] First read confirmed, then save, reload, and reopen the old tool

For more, see: [backup and restore](https://aicoding.club/docs/tutorials/html-tool-backup-restore/) and [deploying your project](https://aicoding.club/docs/course/building-projects/deployment/).
