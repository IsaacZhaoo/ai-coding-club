---
title: "AI Agent Portfolio Guide: Project Evidence"
description: "Build one verifiable AI Agent portfolio project with architecture, tasks, traces, evals, security boundaries, failure logs, and deep-dive evidence."
keywords:
  - AI Agent portfolio
  - LLM engineer portfolio
  - AI Agent project
  - Agent project deep dive
  - AI Agent 作品集
  - AI Agent 项目
sidebar_position: 28
tags: [tutorial, career, agent-engineering, portfolio]
---
# AI Agent Portfolio Guide: Prove System Design, Evals, and Delivery with One Verifiable Project

Hand your agent repository to someone who knows nothing about the project. Ask them to answer four questions without contacting you: what task the system handles and how success is defined; which actions the agent is allowed to take; where a failure occurred and what record it left; how the problem was fixed and where the evidence is.

If answering any of those questions requires you to stand next to them and explain, the repository is missing a traceable evidence chain.

This is the real evaluation challenge for an AI agent portfolio. The project can be complex, the code can be clean, and the architecture diagram can be precise—but when a single run, a single failure, and a single fix have no independently inspectable artifact, a third party cannot reconstruct the engineering judgment you exercised throughout the process. A strong AI agent portfolio lets a third party reconstruct and verify the engineering judgment behind task boundaries, execution traces, failures, evals, permissions, and delivery artifacts. This is also the kind of evidence that supports a Project Deep Dive: you need to demonstrate what can go wrong, why it goes wrong, and whether your fix has been tested.

---

## Evidence Map: Four Levels—Demo, Intent, Runtime, and Regression

Packing every file into a repository is nowhere near enough for a portfolio that holds up to third-party inspection. You need evidence at four distinct levels.

**A demo** tells someone roughly what the system is doing. It generates interest. It does not prove any engineering decision.

**Architectural intent** explains what each component is responsible for, why the system is divided that way, and where the permission boundary starts and ends. It turns a collection of source files into a responsibility map.

**Runtime evidence** shows what actually happened during a specific execution—which tools were called, where the error occurred, where the bad data traveled, and what was ultimately returned. It is the primary material for investigating a failure.

**Regression evidence** checks that a fix held and prevents the same class of problem from reappearing in future runs. It is the mechanism that turns "I fixed it" into a verifiable claim.

These four levels are mutually dependent and cannot substitute for one another. Treating an architecture diagram as runtime evidence or a demo video as regression evidence creates an obvious gap in the portfolio.

The diagram below describes the causal relationships among the nine evidence elements:

```
Task Set
  ├─> Tool Contract ─┐
  └─> Bounded Loop ──┴─> Trace ─> Failure Log ─> Eval Case / Trials ─> Suite / Gate

Architecture Map   indexes responsibility and permission boundaries
Security Boundary  wraps Tool, Loop, and Workspace; feeds into Trace / Eval
README + Commands  hands the full chain to a third party for reproduction
```

The root of the entire chain is the **Task Set**. Without a task definition, traces and evals share no common baseline; without a common baseline, evaluation numbers have no meaning.

---

## Choose a Bounded Repository-Maintenance Agent as the Flagship Project

This guide recommends a bounded repository-maintenance / coding agent as the flagship project. The reason is precision: the input, execution scope, and output can all be specified exactly, and each evidence level has a natural landing point.

The typical structure of this kind of project looks like this.

**Input** is a task contract that specifies repository scope, a local objective, files or areas that must not be modified, acceptance criteria, and permissions. This contract is the root of the entire evidence chain.

**Execution** is managed by a harness that assembles context, calls the model/provider, dispatches tools, manages state, and controls the execution flow. The agent performs diagnosis or small modifications through declared tool classes—read, search, edit, and command. All writes and commands occur in an isolated workspace. Out-of-scope actions, objective changes, and high-risk operations route to refusal, an approval step, or a structured handoff.

**Output** includes a structured result, a diff, validation evidence, trace identity, an eval result, and known limits.

**Active exclusions** must also be stated explicitly: this project does not handle cross-repository migrations, does not execute production deployments, and does not manage credential rotation. Writing out what the system does not do is more useful for third-party assessment of your system-design judgment than leaving boundaries vague.

A narrowly scoped task can simultaneously demonstrate context, harness, tool, loop, security, trace, eval, and README. That is the engineering value of using it as the flagship project.

---

## Nine Evidence Elements, in Dependency Order

The table below lists the required question, suggested artifact, and dependency for each of the nine evidence elements. The file names are teaching templates, not required paths—but the links between artifacts are not optional. Task IDs, trace IDs, failure IDs, and eval case IDs must be cross-traceable.

| Element | Required question | Suggested artifact | Dependencies and risk of omission |
|---|---|---|---|
| Architecture Map | Who is responsible for context, decisions, tools, state, validation, and permissions | `docs/architecture.md` + responsibility diagram | Depends on project boundary; without it, every technical term is unattributed |
| Task Set | What does the system handle, and how are success / refusal / escalation defined | `tasks/` or structured case files | Root of the entire chain; without it, metrics, traces, and evals share no baseline |
| Tool Contract | What are the schema, semantics, error behavior, idempotency, and side effects | `contracts/tools/` + normal/error fixtures | Depends on Task Set; authorization, business validation, and side-effect governance require coverage beyond schema format constraints |
| Bounded Loop | How aim, state, policy, evaluator, budget, stop condition, authority, and escalation are combined | `docs/loop-contract.md` or config | Depends on task/tool; without it, retries, completion, and out-of-scope actions have no explainable rules |
| Trace | What actually happened during this execution, and what remains invisible | `traces/<trace-id>.jsonl` + field glossary | Depends on stable identity/parent/event; without it, failure accounts rely on memory alone |
| Failure Log | What is the specific gap between expected and actual behavior, what is the root cause, what was fixed, and what residual risk remains | `failures/<case-id>.md` | Depends on Trace; without it, the repository shows only the success path and cannot demonstrate debugging judgment |
| Eval Suite | How case, grader, trial, suite, and gate verify the fix and prevent regression | `evals/` + baseline / candidate records | Depends on task/failure; a single case or a single trial cannot support a reliability conclusion |
| Security Boundary | How direct execution, workspace writes, host trust, approval, and audit constrain actions | `security/boundary.md` + policy/config | Wraps tool/loop/workspace; without it, "secure" is just a label on the architecture diagram |
| Reproducibility Package | How a stranger runs the project, inspects the evidence, and confirms contributions and limits | `README.md` + executable commands + artifact index | Depends on all upstream elements; without it, the evidence can only be demonstrated live by the author |

### Architecture Map

The Architecture Map lets a third party skip the guesswork about what each component decides, what the interfaces between components are, and where the permission boundary runs—and map source files directly to system intent.

The consequence of omitting it is predictable. You say "the harness manages context," and the reviewer asks "which file?" You say "the loop has a budget limit," and the reviewer asks "how is budget calculated, and what happens when it's exceeded?" Technical terms without attributed ownership cannot serve as evidence.

### Task Set

The Task Set defines what the system handles and how three outcome types are distinguished: **success** (the task is completed within boundaries), **refusal** (the task exceeds permissions and is actively declined), and **escalation** (the system recognizes it cannot handle the situation and hands off to a human).

All three outcomes need corresponding task cases. Without them, evals can only verify the success path, and project deep-dive questions about refusal and escalation will have no coverage.

### Tool Contract

The Tool Contract goes one layer beyond schema: a schema handles format and structural constraints, while a contract also covers semantics, error handling, idempotency, and side effects.

MCP Tool annotations are hints. `readOnlyHint: true`, for example, expresses the tool's read/write intent for client reference—but that field does not execute authorization or containment at runtime. Authorization and runtime guards require separate implementation and separate testing. Fixtures must cover both the normal path and error paths; otherwise, only half of the tool contract is verified.

### Bounded Loop

A loop is a local control contract that must define all of the following together:

- **aim**: what this iteration is trying to accomplish;
- **state**: how current progress is tracked;
- **action policy**: how the next step is selected based on current state and feedback;
- **evaluator**: how completion is determined;
- **budget**: the maximum number of steps or tokens allowed;
- **stop**: the conditions under which the loop halts;
- **authority**: which categories of action are permitted;
- **escalation**: who receives control when the evaluator cannot decide or an action exceeds authority.

The runner combines these contract fields to return one of: success, continue, budget exhausted, or escalation. Unlimited retries have no engineering boundary. A loop without explicit stop conditions and authority definitions is very hard to explain under project deep-dive questioning when someone asks "how does this system know when to stop?"

### Trace

A trace reconstructs the sequence of key events within the scope of what was captured: which tool was called, what the parameters were, what was returned, and what happened next. It is the primary material for investigating a failure and one of the core evidence sources that supports project narrative.

The proof scope of a trace is bounded by your instrumentation. Telemetry gaps must be recorded explicitly—which calls did not enter the trace, and which fields are currently empty. A gap itself is acceptable. Being unable to locate the gap is the problem.

Stable trace identity—trace ID, parent span ID, event type—makes traces cross-traceable to failure logs and eval cases. A trace without stable identity is just a log file; it is not sufficient to serve as evidence.

### Failure Log

The Failure Log is the artifact most often omitted from a repository, yet it directly demonstrates debugging judgment.

It records the specific difference between expected and actual behavior; which trace fields supported which root-cause hypothesis; what the fix changed and why that change is correct; and what residual risk remains after the fix.

A repository that shows only the success path cannot demonstrate that the author has debugging judgment. The value of the Failure Log is that it shows your reasoning process about failure. This evidence supports STAR responses and project deep dives by making the investigation path and the basis for judgment independently inspectable.

### Eval Suite

Evals have five levels that must be kept distinct:

**case** defines a task and its success criterion—this is the atomic unit of evaluation;\
**trial** is one execution of a case under a specific configuration—the same case can have multiple trials;\
**grader** checks whether a trial's result meets the case's success criterion;\
**suite** organizes related cases together;\
**gate** uses the suite's results to decide whether to accept a given change.

Probabilistic behavior requires repeated trials, and each trial must retain a record of its model/provider, prompt and tool versions, environment, and grader configuration. A single pass cannot be elevated into a reliability conclusion. Baseline results and retest results use `[baseline]` and `[retest result]` as placeholders—any number that appears in a resume bullet or project introduction must be traceable to a specific trial artifact.

Check outcomes first, then cautiously add only the trajectory constraints that are truly critical; locking every historical action into an eval will cause that eval to break on the first refactor.

### Security Boundary

The Security Boundary must concretely answer five questions:

**Direct execution**: Which processes can the agent start directly, which network connections can it initiate, and which system tools can it call?

**Workspace writes**: Which code, configuration, hooks, Git state, and generated files can the agent write? Writing to `.github/workflows/` and writing to `README.md` have entirely different blast radii.

**Host trust**: Which host components, sockets, daemons, logged-in CLIs, or credentials will consume state the agent has written? An agent running in a container that has a mounted Git config or socket has a host trust boundary that differs from its container boundary.

**Approval / audit**: Which actions require human confirmation, and how do complete calls, parameters, cwd, configuration, and side effects enter the audit record?

**Isolation**: Ephemeral containers or worktrees are common isolation mechanisms, but the name alone is not strong isolation. Mount policies, how credentials are passed in, privileged settings, and host socket reachability must each be examined separately.

Routing out-of-scope refusals and escalation paths into the task set, trace, and eval produces a verifiable security boundary rather than just a label on an architecture diagram.

### Reproducibility Package

The README is the delivery interface for the entire evidence chain. Recommended contents: a concise statement of task boundaries, a link to the architecture diagram, a quickstart, executable commands for tasks and evals, an artifact index (where traces, failure logs, and eval records are stored), a description of the permission model, contribution notes (what you did versus what someone else did), key trade-offs, and known limits.

"Executable commands" means that starting from zero and following the README steps produces a meaningful state. If internal access permissions or private data are required, state that explicitly rather than letting a stranger fail silently.

---

## One Failure Chain: How Evidence Grows from an Error into Regression Protection

The following example chain contains no invented numerical values or metrics, and shows how the nine elements interlock:

```
(Example) A tool returns data that is structurally valid but semantically invalid
→ Trace shows the invalid data entered the next decision step
→ Failure log records: tool contract covered the schema but not business-semantic validation
→ Fix: add a runtime validator after the tool call that rejects semantically invalid returns
→ Generate an eval case from this failure, including the task that triggered the error and a grader
→ Re-run the trial; record grader results before and after the fix
→ Add the case to the suite; the gate automatically checks for the same regression in future changes
```

This chain reveals the division of responsibility across three layers of protection:

The **Tool Contract** specifies expected semantics—this is a design-time specification.\
The **runtime validator / authorization** blocks invalid behavior at execution time—this is runtime enforcement.\
**Fixtures / eval cases** check whether the implementation matches the specification—this is regression verification.

All three layers are necessary. "I wrote a schema" covers only format. It does not cover semantics, authorization, or side effects. Treating a schema as complete proof of correctness and security is a characteristic portfolio engineering error.

The chain also illustrates how security intersects with every layer: the existence of the runtime validator needs to appear in the Tool Contract; events the validator rejects need to appear in the trace; those rejection events in the trace need to appear as eval cases. Security Boundary runs through tool, loop, trace, and eval—not only through a single separate file.

---

## README, Artifact Index, and Ownership Ledger

A complete README structure:

```
Project name
├── Task boundary (one sentence: what it handles and what it does not)
├── Architecture diagram link
├── Quickstart (shortest path from zero to running)
├── Task commands (how to run a task case)
├── Eval commands (how to run the eval suite and gate)
├── Artifact Index
│   ├── traces/     → trace file locations and field glossary
│   ├── failures/   → failure log file locations
│   └── evals/      → eval case, trial, and baseline locations
├── Permission model (allowed and disallowed actions)
├── Ownership (who did what and where the verifiable evidence is)
├── Trade-offs (what trade-offs were made and why)
└── Known Limits (known boundaries and unresolved problems)
```

The **Ownership Ledger** is the part most likely to be overlooked. For project deep-dive preparation, be ready to explain your personal contribution, the process you followed, the obstacles you encountered, and how you handled them. A concise ownership table is exactly the structure that fits this kind of preparation:

| Engineering decision or artifact | My specific contribution | Verifiable evidence | Known limit |
|---|---|---|---|
| `[actual decision in the project]` | `[design / implementation / eval / operational responsibility]` | `[file, trace, or eval path]` | `[boundary that remains unresolved]` |

This table serves two purposes. Internally, it forces you to clarify during portfolio organization which decisions you actually made versus which are framework defaults or a collaborator's work. Externally, it tells a third party where to find inspectable evidence and signals that you have a clear view of the boundaries of your own contribution.

Include only what you actually did. If the project is a solo effort, record it as one. If there are collaborators, explain who was responsible for what. Do not fabricate team collaboration, client impact, or production responsibility.

---

## Turning the Same Evidence Package into Four Job-Facing Expressions

Once the evidence chain is organized, the same material generates four distinct expressions for different contexts.

### Resume Bullet

A resume bullet indexes the evidence; it cannot replace the evidence. An effective bullet contains: action + task/boundary + engineering decision + verification method + concrete result.

Format example (all values are placeholders):

> Designed an agent harness for `[task scope]` with `[permission/stop boundary]`, ran regression over `[actual trial count]` trials through `[suite / grader]`, improved `[metric]` from `[baseline]` to `[retest result]`; evidence at `[artifact]`.

Framework names (LangGraph, CrewAI, LangChain, and others) can appear in a bullet as implementation context, but a framework name cannot substitute for an engineering decision and a verification method. "Built an agent using LangGraph" and "designed the loop's stop conditions and authority boundaries for that agent" are two entirely different claims.

### Five-Minute Project Introduction

A five-minute introduction relies on a clear narrative order; it does not need to cover every file. Recommended sequence:

**Task and scope**—start with what the system handles and where the boundaries are.\
**Architecture and personal contribution**—focus on the part you were responsible for; there is no need to lay out the whole system.\
**The most important trade-off**—name one trade-off you made during design and explain why you chose that side.\
**One failure and the investigation**—describe a specific failure concretely: what the trace showed, what your hypothesis was, and what the root cause turned out to be.\
**Eval and security evidence**—briefly describe how the eval suite verified the fix and what constraint the security boundary set.\
**Known limits and next steps**—ending with known limits is more credible than ending with a future roadmap, because it demonstrates that you have a clear-eyed understanding of the system.

Walking through every file at equal weight sounds like a table of contents being read aloud. That does not fit in five minutes.

### Project Deep Dive

This evidence package is well suited for preparing a Project Deep Dive. For each core decision, prepare a set of condition → decision → cost → evidence → residual risk:

- **Condition**: what constraint you were operating under when you made this decision;
- **Decision**: what option you specifically chose;
- **Cost**: what this choice gave up;
- **Evidence**: which artifact shows the effect of this decision and where to find it;
- **Residual risk**: what problems this decision still leaves unresolved.

During deep-dive follow-up questions, you can return to specific artifacts. Follow-ups may go into tool error handling, loop stop conditions, trace gaps, grader bias, host trust boundaries, or personal contribution. If any follow-up question leaves you unable to point to a specific artifact, that is where your evidence coverage has a gap.

### STAR

For this flagship project, the Failure Log is one of the most stable sources of STAR material—it simultaneously preserves task boundary, investigation path, and verification result.

**Situation**: what the task was, what the boundaries were, and why you were working within those boundaries.\
**Task**: what you personally were responsible for in this work and what your initial understanding of the problem was.\
**Action**: this is the substance. Explain what the trace showed, what your first hypothesis was, which fields you used to test the hypothesis, what the root cause was, what you changed, why that change was correct, and which eval case you added to prevent regression.\
**Result**: cite only real retest results and residual risk. Do not invent success rates or latency improvement numbers.

When Action is written too thinly, the STAR response loses its technical foundation—just saying "found the problem and fixed it" without explaining the investigation path and the basis for judgment. Technical detail is the substance of Action.

---

## Where to Act: Fill the Upstream Gap First

Locate the most upstream gap before deciding which files to add.

If there is no clear task contract—add the Task Set first. Everything else takes it as its baseline.\
If there is a task but no trace—add trace instrumentation first. Without a trace, failure logs and evals have no foundation.\
If there is a trace but no failure log—document one real failure case, even if it is only one.\
If there is a failure log but no corresponding eval case—convert that failure into a case and add it to the gate.\
If eval and trace are both present but the Security Boundary has no concrete action constraints—check direct execution, workspace writes, and host trust one item at a time.\
If all artifacts are present but the README has no executable commands—start with the quickstart and verify that a stranger can get to a meaningful state.

This sequence asks you to walk down from the root of the full chain first and confirm that every layer of evidence can stand independently of a live explanation from you.

When a third party can use your repository to answer the four questions at the start—what the task is, what is allowed, where it failed, and whether the fix is credible—the engineering proof in that portfolio is complete.

---

## Sources

**Official roles**

- Anthropic, Research Engineer, Model Evaluations — [https://job-boards.greenhouse.io/anthropic/jobs/5198255008](https://job-boards.greenhouse.io/anthropic/jobs/5198255008)
- OpenAI, AI Systems Engineer, Codex Agents — [https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588](https://jobs.ashbyhq.com/openai/de06790a-7243-4e33-a6f1-e7bd34009588)
- OpenAI, Applied AI Engineer, Codex Core Agent — [https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c](https://jobs.ashbyhq.com/openai/577e6673-0a4a-491b-9a0d-facbdd3bdf3c)
- LangChain, Deployed Engineer, Early Career — [https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522](https://jobs.ashbyhq.com/langchain/0f35c8e1-9318-411d-929b-04c60e6d8522)
- LangChain, Fullstack Software Engineer, Applied AI — [https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d](https://jobs.ashbyhq.com/langchain/c75915ba-a32b-4e17-873d-19b47564170d)
- Cognition, Applied AI Engineer — [https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d](https://jobs.ashbyhq.com/cognition/811c3f5a-b26d-4162-b49b-93890a91794d)
- Sierra, Software Engineer, Agent — [https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d](https://jobs.ashbyhq.com/sierra/631848ec-1a74-4067-8b9f-cd04a71aab6d)

**Official technical sources**

- Anthropic, Building effective agents — [https://www.anthropic.com/research/building-effective-agents](https://www.anthropic.com/research/building-effective-agents)
- Anthropic, Demystifying evals for AI agents — [https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents](https://www.anthropic.com/engineering/demystifying-evals-for-ai-agents)
- Anthropic, Writing effective tools for agents — [https://www.anthropic.com/engineering/writing-tools-for-agents](https://www.anthropic.com/engineering/writing-tools-for-agents)
- OpenAI, Evaluation best practices — [https://developers.openai.com/api/docs/guides/evaluation-best-practices](https://developers.openai.com/api/docs/guides/evaluation-best-practices)
- OpenTelemetry, Traces — [https://opentelemetry.io/docs/concepts/signals/traces/](https://opentelemetry.io/docs/concepts/signals/traces/)
- MCP, Tools specification — [https://modelcontextprotocol.io/specification/2026-07-28/server/tools](https://modelcontextprotocol.io/specification/2026-07-28/server/tools)

**AI Coding Club**

- Agent Engineering Hub — [/docs/agent-engineering/](/docs/agent-engineering/)
- Portfolio and interview foundation — [/docs/course/career/portfolio-interviews/](/docs/course/career/portfolio-interviews/)

---

## Continue the AI Agent interview series

- [Interview Hub](/docs/tutorials/ai-agent-interview-guide/)
- [Portfolio](/docs/tutorials/ai-agent-portfolio-guide/)
- [System Design](/docs/tutorials/ai-agent-system-design-interview/)
- [Failure Analysis and Evals](/docs/tutorials/ai-agent-failure-analysis-evals-interview/)
