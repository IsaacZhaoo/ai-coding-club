---
title: "AI Code Review Workflow: What Should an Agent Check Before You Merge?"
description: "Build an evidence-based AI code review workflow that checks intent, runtime behavior, tests, risk boundaries, and the latest diff before merge."
keywords:
  - AI code review workflow
  - AI code review checklist
  - AI pull request review
  - coding agent review
  - what to check before merging code
sidebar_position: 9
tags: [tutorial, coding-assistant, agent-engineering, code-review]
---
# AI Code Review Workflow: What Should an Agent Check Before You Merge?

---

I almost counted a same-page anchor click as a roadmap conversion.

The AI Coding Club analytics pipeline had a classifier that determined whether a user's click on a link was a legitimate cross-page roadmap destination. It was supposed to fire only when someone navigated to a different page to read the roadmap. But there was a case where a link on the roadmap page itself used `href="#"` — a same-page fragment — and the classifier could treat it as a valid outbound roadmap destination. Any click on that link could be tallied as a conversion event.

The fix was straightforward in hindsight: pass the current page's pathname into the classifier, normalize both the source and destination pathnames, and ignore any destination that resolves to the same page the user is already on. The caller matters here — the click handler supplied the browser-resolved absolute `link.href`, not merely the raw `href` attribute sitting in the HTML. That distinction changes what the classifier actually receives at runtime.

Nine focused regression checks covered the cases: a same-page base URL, a same-page fragment URL, and a legitimate cross-page roadmap destination. On 2026-07-20, a fresh local run passed all nine.

And here is the thing that made me stop before merging: passing nine focused checks is evidence, but it is not the review. Reading the diff, tracing the caller, and checking whether the assertions actually proved both the failure and the preservation case — that was the review. The nine green checkmarks were one input to a decision, not the decision itself.

That tension is what this article is about.

---

## What an Agent Should Actually Do Before It Recommends Merging

An agent should not recommend a merge because the diff looks plausible or the tests are green. It should connect the requirement, changed behavior, executable evidence, risk surface, and unresolved uncertainty into one review verdict.

Here is the responsibility structure I use:

1. **Establish the intended change and its scope.** What is supposed to change, and what must stay the same?
2. **Trace the actual behavior change through callers and system context.** What changes at runtime, not just in the edited lines?
3. **Inspect the quality and relevance of the verification, not only whether it passed.** Would the test catch a regression? Does it prove what it claims to prove?
4. **Identify risk boundaries and call for a qualified reviewer when the change exceeds a general reviewer's competence.** Some areas require specialist judgment.
5. **Confirm that the verdict applies to the latest diff and name every important assumption that remains unverified.** A review of an earlier push is not a review of the current one.

These five responsibilities are AI Coding Club's synthesis, not a GitHub or Google standard. They do not need five equal sections, and they are not always sequential. What they are is a framework for producing a verdict that is honest about what it knows and what it does not.

---

## Responsibility One: Establish the Intended Change and Its Scope

Before looking at a single changed line, an agent — or a human reviewer — needs a concrete statement of intent. Not "improve analytics" or "fix a bug," but: which behavior changes, and which behavior must remain unchanged?

For the analytics correction, the requirement was precise:
- **Change**: same-page navigation must not be counted as an external roadmap destination.
- **Preserve**: legitimate cross-page roadmap clicks must still be classified and recorded.

This matters because a vague requirement makes the review impossible. If the requirement is "make the analytics more accurate," there is no way to verify whether the diff achieves it. If the requirement is "a link to `#` on the roadmap page must not fire a conversion event, and a link to `/docs/roadmap/` from another page must still fire one," you can inspect the diff and the tests against that specific claim.

The reviewer also has to ask: does the diff contain work unrelated to the stated requirement? If the classifier change also touched the event-batching logic or the session-ID handling, those are different review surfaces that need their own examination. A large diff that mixes concerns is harder to review and harder to attribute if something breaks.

If the requirement is not specific enough to review — if the agent is guessing at what "correct" means — that is a finding in itself. Returning to the author for a clearer requirement statement is a valid action, and sometimes the most useful one.

---

## Responsibility Two: Trace the Actual Behavior Change

The diff shows which lines changed. The review has to establish what those changes do at runtime.

In the analytics case, the critical detail was the caller. The click handler supplying the URL to the classifier was passing `link.href` — the browser-resolved absolute URL, not the raw `href` attribute from the HTML. That matters because the classifier receives a browser-resolved absolute URL rather than the raw fragment string, making pathname comparison the relevant runtime behavior. The fix works because it operates on the resolved pathname, not the raw attribute. A reviewer who only read the classifier diff without asking "what type does this function actually receive?" might have missed that the fix was correctly targeted at the resolved value.

The questions I work through here are:
- Who calls the changed code, and what types or transformations reach it?
- What will users, stored data, APIs, analytics, or downstream systems observe as a result of this change?
- Which edge cases or preservation cases follow from that runtime context?

For the analytics fix, the preservation case was specific: a user on a different page who clicks a link to `/docs/roadmap/` should still generate a conversion event. The classifier must distinguish "same page, different fragment" from "different page entirely." The fact that both involve a `/docs/roadmap/` URL in the destination makes this a meaningful test, not an obvious one.

Tracing callers is where many surface-level reviews fail. An agent that reads only the utility function diff may report that the logic is correct in isolation while missing that the function's callers supply data in a different format than the function assumes.

---

## Responsibility Three: Inspect the Verification

Nine checks passed. That is evidence. But before treating it as sufficient evidence, a reviewer needs to ask harder questions about the checks themselves.

Google's engineering review practices make this explicit: tests themselves must be reviewed. A useful test should exercise the intended behavior and should fail when the implementation is broken. A test that passes unconditionally, that asserts only the absence of an exception, or that covers only the happy path without exercising the failure mode is not a useful test for the behavior under review — regardless of whether it is green.

For the analytics case, the relevant questions are:
- Do the focused cases cover the specific classification scenarios that the requirement describes? (They do: same-page base URL, same-page fragment URL, cross-page roadmap destination.)
- Would the tests fail if the fix were reverted — if the same-page check were removed? (This is the regression-catch question, and it matters more than whether the tests currently pass.)
- Is there a preservation assertion — a case that must continue to work after the change? (The cross-page roadmap case serves this role.)
- Does a fresh run on the current commit confirm the result? (Yes: 2026-07-20, all nine focused checks passed.)

What the focused test does not establish is also part of the review:
- It does not prove that every analytics event in the application fires correctly.
- It does not prove browser interaction behavior across different browsers or devices.
- It does not prove deployment behavior or production metrics.
- It does not prove that the normalized pathname comparison handles every possible URL format that could arrive from the browser.

A reviewer who does not state these residual boundaries is delivering an overconfident verdict.

Beyond the focused test, a reviewer should ask whether other check categories are relevant: lint, type-checking, build, integration tests, browser tests, or deployment checks. For an analytics classifier, type-checking is a relevant general check. However, whether the caller supplies a browser-resolved URL rather than a raw href string is a matter of caller inspection and runtime behavior, not something the TypeScript type system can enforce — and that is a risk the focused unit test does not cover.

---

## Responsibility Four: Identify Risk Boundaries and Escalate

Some changes can be reviewed with general software-engineering judgment. Others require specialist knowledge.

The analytics fix is a relatively contained change: a conditional check on a pathname comparison inside a client-side event classifier. The risk surface is the accuracy of conversion tracking. A general reviewer can assess whether the logic is correct and whether the tests are adequate for the stated behavior.

But not every change is like this. Changes that affect:

- Authentication or authorization
- Secrets handling or credential storage
- Payment flows
- Personal data collection, storage, or deletion
- Database migrations or schema changes
- Concurrency or shared state
- External dependencies or infrastructure configuration
- Accessibility requirements
- Internationalization logic

...require either a reviewer with relevant specialist knowledge or an explicit escalation step. OWASP's code review guidance treats manual security code review as an important part of a secure development lifecycle even as automated scanners improve — because scanners identify patterns, not intent. A scanner cannot tell you whether a new data field should have been encrypted, because that depends on what the field contains and what the application is required to do with it.

"Needs specialist review" is a valid verdict. It is not a failure of the workflow. It is the honest answer when a change's risk surface exceeds a general reviewer's competence, and it is more useful than a confident approval that ignores the specialist risk.

---

## Responsibility Five: Confirm the Latest Diff and Name the Residuals

A review of an earlier push is not a review of the current one.

This is a practical problem with iterative development. A pull request goes through several rounds of edits. A reviewer comments on a draft. The author pushes a revision. If the agent or the reviewer does not re-examine the diff after that push, the approval — or the comment — applies to a version that no longer exists.

GitHub Copilot's documentation is specific about this: unless automatic review of new pushes is configured, later changes require Copilot review to be requested again. Copilot also leaves a `Comment` review rather than `Approve` or `Request changes`, which means the review does not count toward required approvals under branch protection rules and does not itself block merging. The merge gate is a separate system — branch protection rules, required status checks, resolved conversations, and repository configuration — not the content of the agent's review comment.

This distinction matters: an agent review is a findings report. It is not a merge gate.

For the analytics case, the latest-diff check is: was the nine-check result from 2026-07-20 run against the current commit? If the author made further changes after that run, the check result applies to a previous state. The review should state which commit it examined.

The residual uncertainty, even for an otherwise complete review, should be named explicitly. For the analytics change, one residual is: the focused checks verify classification logic under the named URL inputs; they do not verify that the browser environment always resolves URLs in the way the test fixtures assume. That is a small residual risk for a client-side analytics classifier, but naming it is more honest than pretending it does not exist.

---

## The Four Layers That Are Not Interchangeable

One compact table clarifies what each layer of the review process produces and what it cannot substitute for:

| Layer | What it produces | What it cannot replace |
|---|---|---|
| Automated checks (CI, lint, type, tests) | Bounded, reproducible evidence about named scenarios | Judgment about intent, context, and adequacy of the checks themselves |
| Agent review | An interpretation of requirement, diff, context, and evidence | Human accountability, specialist expertise, and formal approval |
| Human or specialist reviewer | Judgment for high-risk surfaces and contextual accountability | Automated coverage across every changed line |
| Repository rules (branch protection, required checks) | The technical merge gate based on configured policy | A verification that the evidence is actually sufficient |

None of these is a substitute for the others. An agent review that interprets everything correctly but runs against the wrong commit is still a flawed review. A CI suite that passes all checks does not validate that the checks were the right ones to write. Branch protection that requires two human approvals does not verify that either approver understood the change.

To turn this review sequence into a reusable procedure or attach automatic checks at defined events, see [Claude Code Skills, Hooks, and MCP](/docs/tutorials/claude-code-skills-hooks-mcp/).

If you are already using coding agents in your review workflow, the [AI Coding Best Practices](/docs/best-practices) page covers the broader safety and professional-use considerations for keeping human judgment appropriately in the loop.

---

## The Reusable Review Output

Here is the compact contract I ask an agent to fill in when reviewing a pull request:

```text
Verdict: block / ready after named checks / needs specialist review
Intended change:
Observed behavior change:
Checks run and results:
Blocking findings:
Non-blocking findings:
Unverified assumptions or residual risk:
```

A few notes on how to use this:

**On the verdict options**: `block` means a finding prevents merging. `ready after named checks` means the change is otherwise sound but a specific check has not run — name the check. `needs specialist review` means the risk surface requires expertise this review does not cover. I avoid a bare `approve` verdict because approval in the sense of "I have verified this is correct" is a strong claim that an agent review rarely fully earns.

**On the verdict being evidence-specific**: the verdict should name the commit it applies to. If the author pushes after this review, the verdict is stale.

**On residual risk**: even a `ready after named checks` verdict should name the unverified assumptions. For the analytics case, a reasonable verdict might be:

```text
Verdict: ready after named checks
Intended change: Prevent same-page navigation from being counted as a cross-page roadmap conversion; preserve cross-page conversion tracking.
Observed behavior change: Classifier now receives source pathname and compares normalized source and destination pathnames. Same-page destinations (base and fragment) are excluded. Cross-page destinations are unchanged.
Checks run and results: Nine focused classification checks, fresh run 2026-07-20, all passing. No integration or browser tests examined.
Blocking findings: None found against the current classification logic.
Non-blocking findings: The focused test does not exercise URL formats that differ from the fixtures' assumptions.
Unverified assumptions or residual risk: (1) No browser integration test confirms that the browser-resolved href always matches the format assumed in the test fixtures. (2) No check confirms the full analytics event pipeline beyond the classifier logic itself.
```

This is the author's proposed evidence packet, not a GitHub review status and not an official industry template. It is meant to make the review's evidentiary scope explicit so that the person who decides to merge understands exactly what has and has not been verified.

---

## The Difference Between a Plausible Diff and a Reviewable Change

The analytics correction is a small change. The classifier gained a source-path parameter, a pathname normalization step, and a same-page exclusion condition. Reading the diff, the logic looks correct. And here is the failure mode I am trying to prevent: a review that reports "looks correct" on the basis of reading the diff, without tracing the caller to confirm what type of URL actually arrives, without verifying that the test cases cover both the failure and the preservation scenario, and without stating what the focused tests do not prove.

That kind of review is confidence without evidence. The diff might genuinely be correct, but the reviewer cannot know that from diff-reading alone.

The nine passing checks are evidence. The caller's use of the browser-resolved URL is context. The cross-page preservation test is the case that matters most for the stated requirement. The absence of browser integration tests is a named residual. The combination of these four pieces is an evidence packet. A confidence score — "looks good," seven out of ten, high confidence — is not.

If you are newer to the sequence of editing code, inspecting diffs, and running checks before committing to a review judgment, the [AI Coding Agent Beginner Route](/docs/tutorials/ai-coding-agent-beginner-guide/) covers that foundational sequence. The workflow described in this article builds on top of it.

---

## One Practical Action Before Your Next Merge

Pick one pull request you are currently working on — one where a coding agent has either made changes or offered a review.

Write down:
1. The intended behavior change, in one sentence specific enough that you could write a test for it.
2. The preservation case — the thing that must continue to work.
3. The narrowest meaningful check you could run to test both.
4. The residual uncertainty that would remain even if that check passed.

Do not merge until you have named the residual uncertainty. Not because a named uncertainty blocks the merge — sometimes the residual is small enough that it does not — but because naming it forces the review to be honest about what it knows.

An agent should not recommend a merge because the diff looks plausible or the tests are green. It should give you an evidence packet that makes the review's scope and limits visible. That is the difference between a review and a confidence score.

---

## References

- GitHub Copilot Code Review — Concepts: [https://docs.github.com/en/copilot/concepts/agents/code-review](https://docs.github.com/en/copilot/concepts/agents/code-review)
- GitHub Copilot Code Review — Usage: [https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review](https://docs.github.com/en/copilot/how-tos/use-copilot-agents/request-a-code-review/use-code-review)
- GitHub Pull-Request Reviews: [https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews](https://docs.github.com/en/pull-requests/collaborating-with-pull-requests/reviewing-changes-in-pull-requests/about-pull-request-reviews)
- GitHub Protected Branches: [https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches](https://docs.github.com/en/repositories/configuring-branches-and-merges-in-your-repository/managing-protected-branches/about-protected-branches)
- Google Engineering Practices — What to Look For in a Code Review: [https://google.github.io/eng-practices/review/reviewer/looking-for.html](https://google.github.io/eng-practices/review/reviewer/looking-for.html)
- OWASP Code Review Guide: [https://owasp.org/www-project-code-review-guide/](https://owasp.org/www-project-code-review-guide/)
