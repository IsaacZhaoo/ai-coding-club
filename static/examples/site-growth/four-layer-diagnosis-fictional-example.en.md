# Four-layer worksheet: fictional worked example

**Every site detail, date, number, report state, and event below is invented for this fictional exercise. This is not an anonymized account, a real incident, or a growth benchmark.** `example.org` is a placeholder. No report or account was accessed to produce these values.

## 1. Question and dates — fictional

- Question: Do fewer reported search clicks establish that fewer readers completed the worksheet?
- Page scope: English page `https://example.org/guide/`, one hostname.
- Target observation period: August 17–30, 2026, inclusive.
- Comparison period: August 3–16, 2026, inclusive.
- Each period: 14 calendar days, two occurrences of every weekday.
- Illustrative collection timestamp: September 3, 2026, 12:00 UTC.

## 2. Actual report scope — fictional

| Source | Observation / comparison dates | Reporting time zone and boundaries | Processing / filters | Local evidence |
| --- | --- | --- | --- | --- |
| GSC | Aug 17–30 / Aug 3–16 | Pacific Time; UTC−07:00 on these dates. Observation: Aug 17 00:00 to Aug 31 00:00, exclusive end; comparison: Aug 3 00:00 to Aug 17 00:00, exclusive end | Assume both periods complete; Web search; exact canonical page above; all countries/devices; no query filter | Fictional values only |
| Bing Webmaster Tools | Not collected | Unverified | No search-source or page filters verified | None; leave both layers unfilled |
| GA4 sessions | Aug 17–30 / Aug 3–16 | UTC. Observation: Aug 17 00:00 to Aug 31 00:00, exclusive end; comparison: Aug 3 00:00 to Aug 17 00:00, exclusive end | Assume both periods complete; joint scope: hostname `example.org`, landing page `/guide/`, Session source `google`, Session medium `organic`; all countries/devices; test traffic excluded consistently | Fictional values only |
| Task-event report | Aug 17–30; comparison unavailable | UTC; same date boundaries as GA4 | Custom event `worksheet_download_started`, version 1 active from Aug 17 00:00 UTC; fires when a download action is initiated. Event count on `/guide/`, all traffic sources; test traffic excluded | Fictional event definition and values |

GSC's observation interval corresponds to August 17 07:00–August 31 07:00 UTC. GA4's interval starts and ends seven hours earlier. Daily totals cannot precisely repair those unmatched edges. The same difference applies to the comparison interval. Trends remain readable within each source; these are not identical cross-platform time windows.

The task-event row also covers all sources, whereas the GA4 session row covers Google organic sessions. The two rows do not describe the same cohort.

## 3. Four evidence layers — fictional numbers

| Layer / source | Metric | Observation | Comparison | Evidence status and comparability | Supported reading | Not established |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Impressions / Google | Impressions | 1,200 | 1,600 | Observed; same fictional GSC filters | Fewer reported impressions in this scope | The cause, or all-engine visibility |
| 1. Impressions / Bing | Impressions | Not collected | Not collected | Missing evidence | No finding | Zero impressions |
| 2. Clicks / Google | Clicks | 60 | 80 | Observed; same fictional GSC filters | Fewer reported clicks in this scope | The same number of GA4 sessions or people |
| 2. Clicks / Bing | Clicks | Not collected | Not collected | Missing evidence | No finding | Zero clicks |
| 3. Visits by source / GA4 | Google organic sessions | 50 | 65 | Observed; same fictional GA4 filters; different time zone from GSC | Fewer measured sessions in this scope | Why the count differs from GSC clicks |
| 4. Task evidence | `worksheet_download_started` event count, all sources | 4 | Not instrumented | No comparable previous-period event data | Four recorded download initiations | Four unique readers, saved files, filled worksheets, or a change in completion |

Within this fictional GSC scope, CTR is `60 / 1,200 = 5%` and `80 / 1,600 = 5%`. That is a valid within-platform metric, but it does not explain the decline. A rate of `4 / 50` would mix different source scopes; a rate of `4 / 60` would also cross platforms. Neither is used here.

## 4. Next check — fictional conclusion

- Supported conclusion: this example shows fewer GSC impressions/clicks and fewer measured GA4 Google organic sessions in their respective windows. It cannot establish a decrease in worksheet completion.
- Main gap: the task event was introduced only in the observation period and records download initiation, with a broader source scope than the session row.
- Next check: verify what happens when the download action succeeds or fails and confirm when the event fires, keeping test observations distinguishable. Record exactly which outcome the event can support.
- What would change the conclusion: evidence that the event fires without a download initiation would invalidate its present meaning. Confirmed initiation still would not prove a saved file or a completed worksheet.
- Follow-up: inspect processed reports after allowing for data freshness; compare only later complete periods with unchanged event definitions and compatible filters. Earlier uninstrumented completion remains unknown.

Use the [empty worksheet](./four-layer-diagnosis-template.en.md) for your own observation. Keep the invented values out of your real records.
