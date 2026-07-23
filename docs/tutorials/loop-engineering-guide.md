---
title: "Loop Engineering Guide: Build a Bounded Coding Agent Loop"
description: "Build a bounded Coding Agent Loop with an explicit local aim, evaluator, budget, stopping condition, authority scope, and escalation path."
keywords:
  - loop engineering
  - coding agent loop
  - bounded agent loop
  - agent evaluator
  - agent loop governance
sidebar_position: 17
tags: [tutorial, coding-assistant, agent-engineering, loop-engineering]
---

# Loop Engineering Guide: Build a Bounded Coding Agent Loop

*By Youguang*

---

A work goal and a Loop are not the same thing. I kept treating them as equivalent until the mismatch became impossible to ignore. I would hand a large task to a coding agent, watch it run, and eventually get back something that looked finished. Sometimes it was. Often it had wandered—changed a requirement it had no business changing, retried the same failing approach a dozen times, or reported "done" without producing any verifiable evidence that the aim had been met.

The fix was not a better model. The fix was treating the Loop as a design problem.

---

## What Loop Engineering Actually Means

Addy Osmani's 2026 writing on Loop Engineering describes replacing the manual cycle of prompting, checking, and re-prompting with a deliberately designed system. The warning is direct: unattended loops can make unattended mistakes and consume substantial tokens. That framing is honest and important, because the word "loop" in most coding-agent conversations is doing too much work. It means everything from "call the LLM twice" to "run until it passes CI." Neither definition tells you when to stop, what counts as success, or what the agent is and is not allowed to change.

Anthropic's *Building effective agents* draws a useful distinction between workflows—systems with predetermined control flow—and agents—systems that determine their own steps. It recommends starting simple, composing small patterns, and adding complexity only when simpler approaches fall short. It also explicitly names maximum iteration limits and environmental ground truth as necessary guardrails, not optional polish. The evaluator-optimizer pattern it describes, where one process evaluates another's output and feeds that judgment back into a retry, is close to what I am formalizing here.

My own synthesis from organizing real agent work is this:

> A useful Coding Agent Loop is a bounded local control contract: it changes tactics within an explicit authority scope, evaluates every attempt, stops on success or budget exhaustion, and escalates goal changes instead of silently applying them.

The key word is *bounded*. An unbounded Loop is not a Loop; it is a hope.

---

## The "Goal Equals Loop" Mistake

Here is the assumption I want to correct before anything else: one work goal does not naturally equal one Loop.

A goal like "add a bounded retry setting to this module" contains several distinct units of work that may need different local aims, different stopping conditions, and different authority boundaries. If you feed the whole goal to a single Loop with no structure, you get a process that can silently change the goal when it hits resistance, retry endlessly on a failing evaluator, or succeed at the wrong thing and call it done.

Once I started treating each unit of agent work as requiring its own explicit local contract—with a defined aim, a defined evaluator, a defined budget, and a defined boundary—the behavior became predictable. The Loop either converged, or it handed back evidence of exactly where it got stuck.

---

## The Eight-Field Contract

A Loop, concretely, is a structure with eight fields. I want to explain these through a working example rather than eight equal textbook definitions, because the fields only make sense in relation to each other.

The contract shape in the downloadable example looks like this:

```python
@dataclass(frozen=True)
class LoopContract(Generic[StateT]):
    local_aim: str
    initial_state: StateT
    action_policy: Callable[[LoopContext[StateT]], ActionDecision[StateT]]
    evaluator: Callable[[StateT], Evaluation]
    budget: int
    stopping_condition: Callable[[Evaluation], bool]
    authority_scope: AuthorityScope
```

The example models a small feature change: add a bounded retry setting without changing compatibility requirements. Let me walk through each field using that concrete task.

**`local_aim`** is the specific, immutable goal for this Loop. Not the project goal—the *local* goal. Here it is: "add a retry limit setting to the feature, with validation, without breaking compatibility." This string does not change during the run. If the aim needs to change, that is an escalation, not a retry.

**`initial_state`** is where the Loop starts. In this example it is a `RetryFeatureState` with `retry_limit=None` and `validation_added=False`. Every action the Loop takes produces a new state; the runner threads that state through to the next iteration.

**`action_policy`** is the function that, given the current context, decides what to do next. In the example, attempt one sets a retry limit of 5 without adding validation. That is a legal action within the authority scope—but the evaluator will have an opinion about it.

**`evaluator`** is the function that inspects the current state and returns a judgment. After attempt one, the evaluator sees `retry_limit=5` and `validation_added=False` and returns `continue`. The aim was not met. After attempt two, the policy sets the limit to 3 and adds validation. The evaluator returns `success`.

**`budget`** is the maximum number of attempts the Loop may make. It is not a polite suggestion. When the budget is exhausted, the Loop stops and returns a structured result indicating budget exhaustion. It does not retry. It does not extend its own budget.

**`stopping_condition`** is a predicate over the evaluation result. Here it fires when the evaluation is `success`. The Loop ends. This separates the question "what counts as done?" from the evaluator's job of judging current state.

**`authority_scope`** defines what the Loop is allowed to do. In this example, the Loop may edit implementation or tests inside `allowed_actions`. It may propose a goal change. It may not apply a goal change itself.

**`escalation_result`** (the eighth conceptual field, returned from the runner) is what happens when an action or evaluation crosses the authority boundary. The Loop stops and returns an `EscalationResult` with a reason, the required authority level, and an optional proposal. The decision goes to the relevant Graph governor.

---

## Running the Example

[Download the verified Loop and Graph example](/examples/loop-graph-engineering-example.zip). It uses only the Python standard library. To run the Loop demo:

```bash
python3 demo.py
```

To run the tests:

```bash
python3 -m unittest discover . -p 'test_*.py'
```

The top-level usage is intentionally simple:

```python
contract = retry_feature_contract()
result = run_loop(contract)

print(result.outcome.value)
print(result.attempts)
print(result.final_state)
```

The verified output:

```text
success
2
RetryFeatureState(retry_limit=3, validation_added=True)
```

Two attempts. The first attempt was a legal move that the evaluator rejected. The second attempt satisfied the evaluator, the stopping condition fired, and the Loop returned. The runner itself never changes between runs—you can replace the action policy, the evaluator, or both, and the runner stays unchanged. That separability is the point.

---

## The Three Outcomes

Every run of this Loop ends in one of three outcomes.

**`success`** means the evaluator accepted the state and the stopping condition fired. This is not "the model said it was done." It is "the evaluator—a deterministic function with access to ground truth—confirmed the aim was met."

**`budget_exhausted`** means the attempt limit was reached before the evaluator returned success. The aim stayed unchanged. The Loop returned its final state and the number of attempts made. This is not a failure to hide—it is evidence. If a Loop hits its budget on every run, that is a signal that the aim is poorly specified, the evaluator is too strict, the budget is too small, or the action policy is not learning. Budget exhaustion is useful information, not permission to retry forever.

**`escalated`** means an action or requirement crossed the Loop's authority boundary. The Loop stopped and returned an `EscalationResult`. In this example, the relevant authority level is the `graph_governor`—a role name belonging to this example's design, not a universal framework API. The general lesson is that something in the Loop encountered a decision that belongs at a higher level of the system, and instead of making that decision silently, the Loop surfaced it explicitly.

Unlimited retries hide design failure. A Loop that reports "done" without evidence of evaluation is not a Loop; it is a while-true with a success string glued to the exit.

---

## Replacing the Policy or Evaluator

One of the practical benefits of expressing the Loop as a contract is that the action policy and evaluator are first-class, swappable values.

Try tightening the accepted retry limit. In the evaluator, the condition that triggers `success` checks that `retry_limit <= 3` and `validation_added is True`. Change the upper bound to 2 and run again. Neither fixed policy state satisfies both checks, so the Loop exhausts its three-attempt budget and returns `final_state=RetryFeatureState(retry_limit=3, validation_added=True)`.

Try forcing `budget=1`. The first attempt sets `retry_limit=5` and `validation_added=False`. The evaluator returns `continue`. But the budget is exhausted after one attempt, so the Loop exits with `outcome=budget_exhausted`. No second chance. The final state shows exactly where the process stopped. You do not need to invent output—the runner returns a structured result you can inspect.

These modifications do not require touching the runner. That is the design contract working as intended.

---

## The Action Policy Is Not an Agent

I want to be explicit about something the example does not do: the action policy in the demo is a deterministic function. It is not an agent. It does not call a model. It follows a fixed sequence of moves designed to exercise the contract.

This is intentional. The contract can later host one Agent, several Agents, tools, or functions. The runner does not care. What matters is that the action policy accepts a `LoopContext` and returns an `ActionDecision`, and that the evaluator accepts a state and returns an `Evaluation`. The architecture is the same whether the action policy is a three-line function or a call to a frontier model with tool use.

The point of this example is to show the contract shape without the noise of model latency, nondeterminism, or API keys. Once the contract is clear, putting an agent inside it is a substitution, not a redesign.

Similarly, not every task needs a Loop. A simple, single-step operation with a deterministic result does not benefit from a retry contract. Loops are for tasks where the path to success is not fixed in advance—where a policy needs to adapt across attempts and an evaluator needs to confirm arrival.

---

## Where the Loop Ends and the Graph Begins

A Loop is a local control structure. It governs one unit of agent work: one aim, one evaluator, one budget, one authority scope. When the aim is met, the Loop exits cleanly. When the budget is exhausted, the Loop hands back evidence. When the authority boundary is crossed, the Loop escalates.

What the Loop does not govern is what happens next. Cross-Loop dependencies—"this Loop's output is the next Loop's input"—belong to [Graph-level design](/docs/tutorials/graph-engineering-guide/). Goal changes discovered mid-run—"the aim itself turns out to be wrong"—must be decided by Graph governance, not silently absorbed by the Loop that discovered the problem.

This boundary matters practically. A Loop that accepts goal changes from within its own action policy has no meaningful authority scope. It can redefine success whenever convergence is difficult. The contract becomes advisory. The `EscalationResult` pattern exists precisely to enforce this: the Loop can *propose* a goal change and explain why, but it cannot *apply* one. The local aim is immutable in all verified tests.

Local convergence belongs to the Loop. Cross-Loop coordination and final goal changes belong to Graph governance. Keeping those two concerns separate is what makes either of them tractable.

---

## Primary Sources

- Addy Osmani, *Loop Engineering* (2026). Description of replacing manual prompt-check-iterate cycles with a designed loop system; warnings on unattended execution and token consumption.
- Anthropic, *Building effective agents* (Anthropic documentation). Simple, composable patterns; workflow vs. agent distinction; evaluator-optimizer pattern; maximum iteration limits; guardrails and environmental ground truth.

---

*The downloadable example for this tutorial contains `demo.py`, the contract module, and `test_loop_engineering.py`. Run `python3 -m unittest discover . -p 'test_*.py'` to verify the contract behavior before modifying it.*
