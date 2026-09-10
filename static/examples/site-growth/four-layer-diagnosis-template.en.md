# Four-layer site diagnosis worksheet

Use this worksheet with data you can access. Keep account identifiers and individual visitor data out of it. See the [fictional worked example](./four-layer-diagnosis-fictional-example.en.md).

## 1. Define the question and dates

- Question to investigate: ____
- Site or page scope, including hostname and language: ____
- Target observation dates, inclusive: ____ to ____
- Optional comparison dates, inclusive and equal in calendar-day count: ____ to ____
- Calendar-day count and weekday mix in each period: ____
- Collection timestamp, including time zone: ____

Matching date labels does not align different time zones. Record each report's actual boundaries below. If you only have daily totals, do not claim an exact time-zone conversion. Keep incomplete recent days outside a trend comparison, or mark the period provisional.

## 2. Record the actual report scope

| Source | Observation / comparison dates actually selected | Reporting time zone and actual start/end boundaries | Latest complete date / data-quality notice | Filters and page mapping | Local evidence reference |
| --- | --- | --- | --- | --- | --- |
| GSC | ____ | ____; daily reporting uses Pacific Time | ____ | Property coverage; Search type; canonical page URL; country; device; query filter, including “none”: ____ | ____ |
| Bing Webmaster Tools, if available | ____ | ____; record “unverified” if unknown | ____ | Search traffic source; site; page; keyword; country/device filters actually available: ____ | ____ |
| GA4 | ____ | Property reporting time zone: ____ | ____ | Hostname; landing page; Session source / medium; country/device; comparisons; internal/test traffic treatment: ____ | ____ |
| Task-event report | ____ | ____ | ____ | Event name and trigger; page and source scope; count unit; instrumentation version / effective date; test traffic treatment: ____ | ____ |

Write filters exactly as used. For Google organic sessions, record `Session source = google` and `Session medium = organic`; an `Organic Search` channel total can include other search engines. First-user acquisition answers a different question from session acquisition. Keep GSC's canonical URL and GA4's observed landing page distinct, and describe any mapping between them.

If source and page totals came from separate tables, keep them separate. They do not establish the source for a particular landing page. Record “not collected” if the required joint report is unavailable.

Bing's `All` and `Web and Chat` selections can cover more than conventional Web search. Its keyword and page tables cover Web traffic only. Preserve the selected source and table scope when recording chart totals and rows.

## 3. Fill each evidence layer

Use one row per platform, metric, and filter scope. Duplicate a row when needed; keep Google and Bing separate. A measured zero is valid only when the report actually returned zero for that scope.

| Layer / source | Metric and count unit | Observation | Comparison, optional | Evidence status and comparability | What this supports | What this does not establish |
| --- | --- | --- | --- | --- | --- | --- |
| 1. Search impressions / Google | Impressions | ____ | ____ | ____ | ____ | ____ |
| 1. Search impressions / Bing, optional | Impressions | ____ | ____ | ____ | ____ | ____ |
| 2. Search clicks / Google | Clicks | ____ | ____ | ____ | ____ | ____ |
| 2. Search clicks / Bing, optional | Clicks | ____ | ____ | ____ | ____ | ____ |
| 3. Visits by source / GA4 | Sessions; exact Session source / medium: ____ | ____ | ____ | ____ | ____ | ____ |
| 4. Task evidence / event report | Event name: ____; unit: events / users / sessions with event: ____ | ____ | ____ | ____ | ____ | ____ |

Evidence status: **observed**, **not collected**, **not instrumented**, **unavailable**, or **not comparable**. A blank cell, missing row, or unavailable account is not a zero. Record chart totals and exported row sums separately when they differ; query tables can omit rows.

An event count measures its configured trigger. A link click or download initiation does not establish that a file was saved, the template was filled, or the reader completed a task. Record the strongest outcome the event actually verifies.

Do not add impressions, clicks, sessions, and events into a traffic total. Do not divide counts from separate platforms into a conversion rate or assume they track the same people. Only compare an event rate when its numerator, denominator, scope, dates, and instrumentation are compatible and documented.

## 4. Choose the next evidence to collect

- Comparable observations within one source: ____
- Unresolved differences in dates, filters, attribution, page mapping, or measurement: ____
- Narrow conclusion currently supported: ____
- Main evidence gap: ____
- One next check, with the question it should resolve: ____
- What result would change the conclusion: ____
- When to check again, after allowing for processing: ____

The worksheet is complete when the remaining uncertainty and next check are explicit. A cause for the traffic change may still be unknown.
