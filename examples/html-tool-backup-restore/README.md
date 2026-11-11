# Expense backup practice

Save `starter.html` and `expense-tool.html` in a practice folder. With Python 3 available, open a terminal there:

```bash
python3 -m http.server 8765 --bind 127.0.0.1
```

Open <http://127.0.0.1:8765/starter.html>. Keep the terminal running and use one editing tab. Stop with Ctrl+C. Serve only practice files. Open the completed reference at <http://127.0.0.1:8765/expense-tool.html>. They deliberately share the same storage key within this origin/profile. UI language is switchable, or start with `?lang=zh`.

Add Lunch 12.50 (2026-11-01), Bus 8.00 (2026-11-02), Notebook 5.00 (2026-11-03). Expect three records and CNY 25.50. Export from the completion, confirm the JSON file exists, and import it in a separate empty browser profile at the same URL. Check every field, count, total and refresh. Import again: still three records, CNY 25.50. The provided `sample-backup.json` contains the same values and fixed IDs; manually added records have generated IDs.

Restore replaces the whole snapshot after confirmation; it does not merge. Export current records separately before replacing if you need them. Cancel or rejected JSON leaves current data unchanged. Version/app/currency, record structure, real dates, integer cents, duplicate IDs and limits are checked before saving. Limits: 1 MiB import, 1000 records, 80-character descriptions, positive amounts up to CNY 1,000,000 each. Save failures preserve stored/displayed state; unreadable existing storage disables editing. Unsupported versions need a separate conversion.

The HTML contains the program, not the browser records. Direct file opening can work in a given browser but storage behavior is not guaranteed across browsers or file moves. Use fictional data for practice. JSON is readable and unencrypted. There is no cloud sync or account recovery.
