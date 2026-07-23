# Loop and Graph Engineering Example

> Stage: Loop and Graph foundations complete and locally verified.

This directory contains the deterministic, API-free example shared by the Loop Engineering and Graph Engineering tutorials. The Loop changes a retry-setting feature, evaluates each attempt, stops on success, and hands decisions outside its authority to a Graph governor. The Graph adds explicit nodes, typed relationships, serial and parallel execution, merge behavior, vetoes, objections, escalation, and an injected governor decision.

## Run It

```bash
python3 demo.py
python3 graph_demo.py
python3 -m unittest discover . -p 'test_*.py'
```

The example uses only the Python standard library.

## Contract Map

| Loop concept | Code |
| --- | --- |
| Local aim | `LoopContract.local_aim` |
| State | `RetryFeatureState` |
| Action policy | `LoopContract.action_policy` |
| Evaluator | `LoopContract.evaluator` |
| Budget | `LoopContract.budget` |
| Stopping condition | `LoopContract.stopping_condition` |
| Authority scope | `AuthorityScope` |
| Escalation result | `EscalationResult` |

The example keeps the local aim immutable. The Loop may change implementation tactics within `allowed_actions`, but a proposed goal change is returned as an escalation for `graph_governor`; the Loop does not silently apply it.

## Graph Topology

```text
context
  -> implementation Loop
       -> tests -----\
       -> review -----> merge -> approval governor
```

The same `GraphDefinition` supports two execution modes:

- `serial`: one worker traverses ready nodes one at a time;
- `parallel`: independent ready nodes such as `tests` and `review` run in the same worker batch.

The Graph distinguishes four node signals: `ok`, `soft_objection`, `hard_veto`, and `escalation`. A hard veto stops before merge. A soft objection reaches the governor without blocking merge. An escalation routes directly to the injected governor, who may approve, reject, or change the Graph aim.

## Verified Behaviors

- success after evaluator feedback;
- budget exhaustion with a structured handoff;
- escalation before an out-of-scope goal change is applied;
- evaluator-triggered escalation after inspecting an in-scope change.
- dependency order under serial execution;
- independent branches under real standard-library worker concurrency;
- equivalent merged output from the same topology in serial and parallel modes;
- hard veto before merge and approval;
- soft objection routing;
- escalation and an injected governor goal-change decision.

## File Map

- `loop_engineering.py`: bounded Loop contract and runner.
- `graph_model.py`: Graph types, signals, decisions, and results.
- `graph_engineering.py`: dependency scheduler, parallel executor, and governance routing.
- `feature_graph.py`: shared retry-feature topology and node handlers.
- `demo.py` / `graph_demo.py`: runnable Loop and Graph demonstrations.
- `test_loop_engineering.py` / `test_graph_engineering.py`: behavior tests.
