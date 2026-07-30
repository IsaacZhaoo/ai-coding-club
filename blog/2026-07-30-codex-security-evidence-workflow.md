---
title: "Codex Security Connects Policy, History, and Findings Into a Case File"
slug: codex-security-evidence-workflow
description: "Codex Security now connects repository policy, scan history, coverage, and validation evidence. Here is why a missing finding is not proof of a fix."
authors: [isaac]
tags: [tools]
keywords:
  - Codex Security
  - Codex Security Plugin
  - AI security code review
  - SECURITY.md policy
  - security scan history
  - vulnerability validation
  - security scan coverage
---

import ArticleSchema from '@site/src/components/ArticleSchema';

<ArticleSchema
  headline="Codex Security Connects Policy, History, and Findings Into a Case File"
  description="Codex Security now connects repository policy, scan history, coverage, and validation evidence. Here is why a missing finding is not proof of a fix."
  datePublished="2026-07-30"
  dateModified="2026-07-30"
  authorName="Isaac Zhao"
/>

# Codex Security Connects Policy, History, and Findings Into a Case File

I read the July 28 changelog on a quiet Tuesday morning, expecting to skim it in thirty seconds. New scan command, faster results, some UX polish—the usual. What actually stopped me were two features that would not make a good demo reel: saved scan history with comparison, and scoped `SECURITY.md` policy. I closed the tab, reopened it, and read more slowly. These are not glamorous additions. They are the sign of a product that has started taking seriously the question I have been asking since AI security tools first appeared: *how do you know the result is real, and how do you know it will still be real next week?*

<!--truncate-->

---

A single vulnerability flag is easy to produce. Any scanner—static or otherwise—can hand you a highlighted line and a severity label. The flag is not the hard part. The hard part is everything that has to be true for the flag to mean something: the tool understood what the repository considers dangerous in the first place, it validated the finding against actual code behavior rather than pattern proximity, it covered the path where the issue lives, and when you revisit in two weeks after a fix, it can actually tell you whether the fix holds. Without those properties, a green result is not a result. It is a mood.

OpenAI describes Codex Security as an application security agent that helps teams find, confirm, and fix vulnerabilities. The local plugin quickstart is specific about what confirmation means in this context: the scan validates plausible findings and provides evidence and remediation guidance for reportable issues. That language—"validates plausible findings," "evidence"—carries real weight if the product means it. A tool that flags and a tool that validates are different products. Validation implies the agent looked at the claim, checked it against what the code actually does, and decided it is worth surfacing. Evidence implies there is something to show a colleague, not just a probability score to argue about.

But validation and evidence only mean something if the tool knows what it is validating against. Which brings me to the scoped `SECURITY.md` policy, and why I think it is the more important July 28 addition.

---

The policy file, as the documentation describes it, can define trust boundaries, security invariants, reportable findings, severity classifications, exclusions, and accepted risk. The closest applicable policy file is used for any given scan. Read that list slowly. These are not configuration knobs for tuning noise thresholds. They are a record of what a specific team, in a specific repository, with a specific threat model, has decided matters. An invariant is a statement about what must always be true. An accepted risk is a deliberate judgment that a known condition is tolerable given other constraints. Exclusions are not gaps—they are decisions.

Every real security review I have participated in has these things, and they almost never live anywhere findable. They are in a Confluence page nobody links to, or in the original architect's head, or scattered across a dozen pull-request discussions. When a new tool joins the review, it brings its own implicit model of what is dangerous—usually something close to OWASP plus whatever its training data emphasized—and it does not know what the team already decided to accept, or why. The result is a report full of findings that are technically correct and practically useless, because half of them reflect accepted risk the team documented years ago.

A repository-specific policy that the agent actually reads before scanning is not a minor UX feature. It is the difference between a tool that knows the domain and a tool that does not. And the fact that the cloud path—which works with connected GitHub repositories and is currently in research preview—explicitly uses repository-specific threat-model context suggests OpenAI understands this distinction. The cloud analysis validates high-signal issues in an isolated environment before surfacing them, with evidence and suggested fixes. That isolation step is what separates validation from flagging. It also means the tool is doing more work before it tells you something, which is the correct trade-off.

---

The scan history and comparison feature is what makes the policy file consequential over time. Without history, a security posture is a snapshot. With history, it becomes a record. Version 0.1.14 adds saved-scan reruns, comparison between runs, and stable repository and finding identities. The stability of identities matters more than it sounds: if the same finding cannot be recognized across two scans, you cannot build a timeline, and a timeline is what distinguishes "this was fixed" from "this was not found this time."

That distinction is not editorial caution. The official Codex Security CLI FAQ states it plainly: AI-assisted scans can vary even with the same configuration. Finding matching can identify a shared root cause across runs, but it does not make scans deterministic. A finding that disappears from a later scan has not been proven fixed. For that to be a real conclusion, the later scan must have covered the original target and the affected path, and the original finding must have been directly rechecked. Coverage can be complete, partial, or unknown. If the coverage is partial or unknown, the absence of a finding tells you nothing about whether the vulnerability is still there.

I find this honest and unusual. Most tools prefer to let a clean result speak for itself. Explicitly surfacing coverage states and warning that a missing finding is not proof of remediation is a product making space for the human judgment it knows it cannot replace. OpenAI's own materials are direct about this: Codex Security complements SAST. It does not replace manual review, code-level validation, exploitability checks, or human threat assessment.

---

The access landscape is worth a brief orientation, because the word "Codex Security" covers several different things at different stages of maturity. The local plugin—the surface the July 28 changelog describes—runs inside Codex and is available through the hosted plugin catalog. The catalog showed 0.1.14 as the latest release; the public Codex CLI plugin marketplace showed 0.1.11 as of July 29. These differ by installation source, and version 0.1.14 is the one with the new history and policy features. Not every installation will already have it.

The standalone `codex-security` CLI and the TypeScript SDK are in limited beta for approved customers and partners. The documentation shows commands, but limited beta is not general availability. The cloud path, which enables repository-level threat-model context and isolated environment validation, is in research preview via connected GitHub. These three surfaces share a name and a direction; they do not share release state, access path, or capability set. The review-before-tracking step in the plugin—the deliberate pause between "finding surfaced" and "issue tracked"—is appropriate for the maturity stage. It is also a good habit that should not be automated away even when the product matures.

---

What I keep returning to is the question of what it takes to say "fixed" with confidence.

The plugin's false-positive workflow makes an interesting move here. When a finding is marked as a false positive, the reason becomes context for future scans. But it does not suppress the vulnerability class, the path, or the rule. Future scans still recheck current source and reachability. The tool remembers the judgment without treating it as permanently settled. That is the right epistemic posture. A false positive today could become a true positive in six months if the code around it changes. Suppressing a rule because a human once reviewed it is how vulnerabilities hide in the seam between the old review and the new code.

The condition for saying "fixed" is correspondingly precise. A later scan with complete coverage of the original path, finding matching that confirms the same root cause was reached, and a direct recheck of the original finding—that is the evidence. Not a green dashboard. Not an absence of alerts. An affirmative trace through the same path that found the issue, returning a different result, with documented coverage. The case file closes when the evidence in it is complete, not when the summary looks clean.

That is what the July 28 release is building toward. Saved history, stable identities, scoped policy, coverage states, review-before-tracking—none of these are features you add to make a demo impressive. They are features you add because you have seen what happens when a security result cannot be explained, reproduced, or traced back to an assumption. The scan command is the easy part. Producing something that survives a second look is the product.

---

**Sources used:**

- OpenAI. *Codex Security*. [https://learn.chatgpt.com/docs/security](https://learn.chatgpt.com/docs/security)
- OpenAI. *Codex Security plugin changelog*. [https://learn.chatgpt.com/docs/security/plugin/changelog](https://learn.chatgpt.com/docs/security/plugin/changelog)
- OpenAI. *Codex Security plugin quickstart*. [https://learn.chatgpt.com/docs/security/plugin](https://learn.chatgpt.com/docs/security/plugin)
- OpenAI. *Codex Security CLI FAQ*. [https://learn.chatgpt.com/docs/security/cli/faq](https://learn.chatgpt.com/docs/security/cli/faq)
- OpenAI. *Codex Security cloud FAQ*. [https://learn.chatgpt.com/docs/security/faq](https://learn.chatgpt.com/docs/security/faq)
---

## Related Reading

- [AI Code Review Workflow: What Should an Agent Check Before You Merge?](/docs/tutorials/ai-code-review-workflow/)
- [Coding Agent Sandbox Security: What the Boundary Protects—and What Can Still Escape](/docs/tutorials/coding-agent-sandbox-security/)
- [MCP Server Security Checklist: What to Verify Before You Connect](/docs/tutorials/mcp-server-security-checklist/)
