---
title: "How to Run Parallel Coding Agents Without Merge Chaos"
description: "Run parallel Coding Agents with isolated worktrees, runtime state, evidence, and merge authority so concurrency does not become integration chaos."
keywords:
  - parallel coding agents
  - git worktree coding agents
  - coding agents worktrees
  - multi-agent coding workflow
  - coding agent merge conflicts
sidebar_position: 23
tags: [tutorial, coding-assistant, agent-engineering, git]
---

# How to Run Parallel Coding Agents Without Merge Chaos

*By Youguang*

Parallel Coding Agents have saved me real hours. They have also handed me integration work that erased those savings so completely that I stopped thinking of the conflicts as bad luck. When the same pattern repeats—apparent progress in two windows, then a merge session that neither Agent can finish—it starts looking less like coincidence and more like a missing operating system.

The system I was missing is not a dedicated orchestration product. It is a set of isolation decisions made before the Agents start, held consistently through the run, and enforced at the point where the branches meet. Git worktrees handle the checkout layer. Everything else is up to the person running the session.

---

## Why Checkout Isolation Is Only the First Layer

When I open two Agent sessions against the same working tree, edits collide at the file level. One session rewrites a file while the other reads a stale version. The index state becomes ambiguous. Neither Agent knows what the other has staged. This is the most visible conflict class, and it is the one that worktrees solve directly.

Git officially supports multiple working trees attached to one repository. Each linked worktree has its own `HEAD` and its own index, while sharing the repository's object store and refs. The stable command form is:

```bash
git worktree add -b <branch> <path> <base-commit>
```

After that, each Agent runs inside its own directory. Direct checkout collisions stop. Anthropic's Claude Code documentation recommends this pattern for parallel sessions so concurrent edits do not collide.

But a worktree manages Git checkout state. It does not allocate a unique application port, a separate database, an isolated cache, a distinct temporary directory, a separate set of credentials, or a private test account. Two Agents in separate worktrees can still speak to the same running service, hit the same database schema, run migrations against the same state, or write to the same generated artifact directory. Separate paths do not prove behavioral independence. That distinction matters more than any Git command, and I have had to learn it more than once.

---

## Deciding Whether Tasks Are Actually Independent

The first question to answer before spinning up two sessions is not "how do I create the worktrees?" It is "do these tasks share anything that will break if both Agents touch it?"

The check I run covers four areas:

**Owned paths.** Each task should have a set of files it writes exclusively. If both tasks need to modify the same module, the same configuration file, or the same generated output directory, they are not independent. Running them in parallel just moves the conflict from the file system to the merge.

**Shared contracts.** An API contract, a database schema, a type definition, or a shared interface is a coordination point. If one task changes the shape of a response and the other task builds a consumer expecting the old shape, the integration failure is not a merge conflict—it is a semantic mismatch that neither Agent will catch on its own.

**Generated artifacts.** Build outputs, lockfiles, migration files, and code-generated types are particularly dangerous. Two Agents may produce migrations with conflicting order. The branches may return incompatible lockfiles. These conflicts are hard to resolve and easy to miss.

**Runtime state.** If both tasks run tests, start a dev server, or seed a database, and those operations share infrastructure, the results are not independent. One Agent's test run can leave state that causes the other Agent's assertions to fail or pass incorrectly.

If any of these areas shows overlap, the tasks are not genuinely parallel. I either split them more carefully, make one task explicitly read-only in the shared area, or run them serially. The temptation to parallelize anyway and "fix it in merge" is where the hours go.

---

## Setting Up the Worktrees

Once I am confident the tasks are independent enough, the setup is straightforward. I pick a stable base commit—usually the tip of the main branch at the moment I start, not a moving target—and create a linked worktree for each task:

```bash
git worktree add -b <branch-a> <path-a> <base-commit>
git worktree add -b <branch-b> <path-b> <base-commit>
```

Both branches start from the same point. This matters for the integration step: if they diverge from different bases, comparing their changes later is harder.

I can check what I have with:

```bash
git worktree list
```

And when I am done with a worktree:

```bash
git worktree remove <path>
git worktree prune
```

The Git documentation at git-scm.com covers the full command surface including locking worktrees and handling bare repositories. For parallel Agent sessions, the above commands are the ones that matter.

---

## What Each Agent Is Allowed to Do

Telling an Agent to "work on the authentication module" is not a task boundary. It is a topic. A task boundary specifies what the Agent may write, what it may read without writing, and what it must not touch.

The form I use is a short contract written before the session starts:

```
Task: <short description>
Branch: <branch-a>
Worktree path: <path-a>
Base commit: <base-commit>

May write:
  - <list of paths or directories>

May read:
  - <list of shared interfaces or contracts>

Must not edit:
  - <list of paths owned by the other task or shared infrastructure>

Acceptance conditions:
  - <specific tests that must pass>
  - <specific behaviors that must be observable>
  - <anything the reviewer will check>
```

This is not bureaucracy. It is the information the Agent needs to avoid making a reasonable-looking change that breaks the other task. Without it, the Agent makes scope decisions on its own, and those decisions are invisible until merge time.

The "may read" section is particularly easy to skip. This records a dependency the controller must refresh. Otherwise it builds against a snapshot and the divergence is silent.

---

## Isolating Runtime Resources

This is the section I wish I had read earlier.

If both Agents run a development server, give them different ports. If both tasks hit a database, use separate databases or separate schemas. If there is a cache layer—Redis, a filesystem cache, an in-memory store—each task needs its own instance or namespace. Temporary directories should be task-specific. Test accounts, API credentials scoped to a test environment, and browser profiles for end-to-end tests should not be shared.

None of this is handled by the worktree. The worktree gives each task a separate directory. The application running inside that directory still connects to whatever the environment points it at.

In practice, I set environment variables explicitly for each session before starting the Agent:

```bash
# Terminal for task A
export PORT=<port-a>
export DATABASE_URL=<db-url-a>
export CACHE_NAMESPACE=<namespace-a>
export TMPDIR=<tmp-path-a>
```

If the project uses a `.env` file, I create task-specific variants and tell the Agent which one to use. If there is a Docker Compose setup, I use separate service namespaces or profiles.

The failure mode when I skip this is subtle. Task A's test run leaves rows in the database that cause Task B's assertions to see unexpected state. Task B's dev server claims a port that Task A needs. The errors look like flaky tests or environment issues, not like a parallelism problem. By the time I realize what happened, I have spent time debugging something that was never a code bug.

---

## What the Agent Must Return

An Agent that finishes and says "done" has not finished. The Agent has finished writing code. I have not finished running a parallel session.

What I need from each Agent before I consider its task complete:

- **Branch name and final commit hash.** Not just the branch—the specific commit. If I need to reconstruct what happened, I need a fixed point.
- **Base commit.** Which commit did the Agent start from? This confirms it started where I intended.
- **Changed files.** A list, not a summary. I want to see the actual paths so I can check for overlap with the other task.
- **Verification commands and results.** The exact commands the Agent ran to verify correctness, and their output. Not a statement that tests pass—the command and the result I can reproduce.
- **Assumptions.** What did the Agent assume about the shared contracts or the other task's behavior? These are the integration risks.
- **Unresolved risks.** What did the Agent notice that might be wrong but did not fix? This is the most useful output and the one most often omitted.

I ask for this explicitly in the task contract, not as an afterthought. If the Agent does not produce it, I ask before declaring the task done. The evidence is what makes integration manageable.

---

## Merge Authority and Integration Order

Two tasks finishing is not the same as the work being done. Integration is its own step, and it belongs to one controller—me, or whoever is running the session—not to either Agent.

I do not ask the Agents to merge each other's branches. Each Agent has incomplete visibility into what the other did. An Agent that merges a branch it did not write is making decisions about code it did not reason about. The merge step is where I apply the evidence both Agents returned and decide on order, conflict resolution, and combined verification.

The order matters. If Task A changes a shared type and Task B consumes it, A merges first. If a migration must run before a feature that depends on it, the migration merges first. This is not always obvious before the tasks start, which is why I check the evidence and assumptions before choosing order.

After both branches are merged, I run combined verification. This is not redundant. Each Agent's tests were valid in isolation. Combined tests check behaviors that only exist when both changes are present. I have found integration failures at this stage that neither Agent's individual verification caught.

---

## Where Parallelism Should Stop

Some work is inherently serial and should stay that way.

**Shared schema changes.** If two tasks both need to alter a database schema, running them in parallel creates a high risk of migration conflict. The migration files will have ordering issues, the schema state will be ambiguous, and one task's migration may silently invalidate the other's assumptions. Run schema changes serially, in the order they need to apply.

**Root-cause debugging.** When something is broken and the cause is unknown, parallelizing the investigation usually means each Agent is exploring a different hypothesis without awareness of what the other is learning. The information needed to find the root cause is often in the interaction between the hypotheses. Keep debugging serial until the root cause is confirmed.

**Shared lockfile updates.** Two Agents that each run install in their worktrees will each produce a lockfile. Merging them is not always clean, and the result may not match what either Agent tested against. If both tasks need dependency changes, coordinate the lockfile update explicitly.

**Decisions that affect the other task.** If Task A discovers that the API contract needs to change to make its work clean, that decision cannot be made unilaterally while Task B is building against the old contract. Stop, surface the decision, and restart from the new agreement.

The rule I apply: if one task's correct execution depends on knowing the result of the other task, those tasks are not parallel—one is a dependency of the other. Run the dependency first.

---

## Before Removing the Worktrees

Before I run `git worktree remove`, I make sure the evidence is preserved. The useful commits stay on branches. If the integration failed and I need to revisit, I want to be able to check out the Agent's exact state, not reconstruct it from memory.

If a task failed and the branch is not worth keeping, I note what the Agent tried, what it found, and why it did not work. It is for the next time I try to parallelize similar work and need to know whether a conflict class is structural or incidental.

After removing both worktrees:

```bash
git worktree prune
```

This cleans up administrative files for worktrees that no longer exist on disk.

---

## A Pre-Launch Checklist for Two Parallel Tasks

Before starting the sessions:

- [ ] Both tasks have non-overlapping write paths confirmed.
- [ ] Shared contracts (APIs, types, schemas) are read-only for at least one task, or not touched by either.
- [ ] No generated artifacts, lockfiles, or migration files are written by both tasks.
- [ ] A stable base commit is identified and recorded.
- [ ] Runtime resources (ports, databases, caches, temp directories, credentials) are assigned per-task.
- [ ] Each task has a written contract: may write, may read, must not edit, acceptance conditions.
- [ ] Each task is expected to return: branch, commit, base commit, changed files, verification output, assumptions, unresolved risks.
- [ ] One controller is identified as merge authority.
- [ ] Combined verification is planned.

During the session:

- [ ] If one task discovers a shared-contract change is needed, pause and surface it before continuing.
- [ ] If runtime state from one task is affecting the other, stop and fix the isolation before interpreting the results.

At integration:

- [ ] Review both tasks' evidence before choosing merge order.
- [ ] Run combined verification after both branches are merged.
- [ ] Preserve branches until combined verification passes.

---

Parallel Coding Agents are worth running. The wall-clock savings are real when the tasks are genuinely independent. The cost of getting the isolation wrong is also real—not in any specific incident I can cite with numbers, but in the repeated experience of converting apparent progress into integration work that no Agent can finish on its own.

The operating system that makes parallelism useful is not the worktrees. The worktrees are one layer—the checkout layer, the one that stops file-level collisions and gives each Agent a clean index to work against. The rest is decisions: which tasks are independent, what each Agent owns, how runtime resources are separated, what evidence comes back, and who controls the merge. When all of those decisions are made before the sessions start, two Agents finishing their work actually means the work is close to done. When any of them are skipped, finishing becomes the beginning of the hard part.

---

## References

- Git project. *git-worktree – Manage multiple working trees*. [https://git-scm.com/docs/git-worktree](https://git-scm.com/docs/git-worktree)
- Anthropic. *Claude Code Common Workflows – Run parallel sessions with worktrees*. [https://code.claude.com/docs/en/common-workflows#run-parallel-sessions-with-worktrees](https://code.claude.com/docs/en/common-workflows#run-parallel-sessions-with-worktrees)

---

## Related Guides

- [Coding Agent Engineering: From Prompt to Graph](/docs/agent-engineering/)
- [Graph Engineering Guide](/docs/tutorials/graph-engineering-guide/)
- [AI Code Review Workflow](/docs/tutorials/ai-code-review-workflow/)
- [Coding Agent Sandbox Security](/docs/tutorials/coding-agent-sandbox-security/)
