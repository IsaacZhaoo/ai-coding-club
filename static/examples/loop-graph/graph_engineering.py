"""Graph execution engine and public API for the shared tutorial example."""

from __future__ import annotations

from concurrent.futures import ThreadPoolExecutor

from feature_graph import build_feature_change_graph
from graph_model import (
    EdgeRelation,
    ExecutionMode,
    GovernorAction,
    GovernorDecision,
    GraphContext,
    GraphDefinition,
    GraphEdge,
    GraphNode,
    GraphOutcome,
    GraphResult,
    NodeResult,
    SignalKind,
    SignalRecord,
)


__all__ = [
    "EdgeRelation",
    "ExecutionMode",
    "GovernorAction",
    "GovernorDecision",
    "GraphContext",
    "GraphDefinition",
    "GraphEdge",
    "GraphNode",
    "GraphOutcome",
    "GraphResult",
    "NodeResult",
    "SignalKind",
    "SignalRecord",
    "build_feature_change_graph",
    "run_graph",
]


def _interpret_governor_decision(
    initial_aim: str, decision: GovernorDecision
) -> tuple[GraphOutcome, str]:
    if decision.action is GovernorAction.REJECT:
        return GraphOutcome.REJECTED, initial_aim
    if decision.action is GovernorAction.CHANGE_GOAL:
        if decision.new_goal is None:
            raise ValueError("a goal-change decision must provide new_goal")
        return GraphOutcome.GOAL_CHANGED, decision.new_goal
    return GraphOutcome.SUCCESS, initial_aim


def _run_batch(
    definition: GraphDefinition,
    node_by_name: dict[str, GraphNode],
    batch: list[str],
    outputs: dict[str, NodeResult],
    signals: list[SignalRecord],
    mode: ExecutionMode,
) -> dict[str, NodeResult]:
    context = GraphContext(
        aim=definition.aim,
        outputs=dict(outputs),
        signals=tuple(signals),
    )
    if mode is ExecutionMode.PARALLEL and len(batch) > 1:
        with ThreadPoolExecutor(
            max_workers=len(batch), thread_name_prefix="graph-worker"
        ) as executor:
            futures = {
                name: executor.submit(node_by_name[name].handler, context)
                for name in batch
            }
            return {name: futures[name].result() for name in batch}
    return {name: node_by_name[name].handler(context) for name in batch}


def _finish_escalation(
    definition: GraphDefinition,
    node_by_name: dict[str, GraphNode],
    outputs: dict[str, NodeResult],
    signals: list[SignalRecord],
    execution_order: list[str],
    execution_batches: list[tuple[str, ...]],
) -> GraphResult:
    if definition.governor_node is None:
        return GraphResult(
            outcome=GraphOutcome.ESCALATED,
            initial_aim=definition.aim,
            final_aim=definition.aim,
            execution_order=tuple(execution_order),
            execution_batches=tuple(execution_batches),
            outputs=outputs,
            signals=tuple(signals),
        )

    governor_name = definition.governor_node
    governor_result = node_by_name[governor_name].handler(
        GraphContext(
            aim=definition.aim,
            outputs=dict(outputs),
            signals=tuple(signals),
        )
    )
    if not isinstance(governor_result.value, GovernorDecision):
        raise TypeError("governor node must return a GovernorDecision")
    outputs[governor_name] = governor_result
    execution_order.append(governor_name)
    execution_batches.append((governor_name,))
    outcome, final_aim = _interpret_governor_decision(
        definition.aim, governor_result.value
    )
    return GraphResult(
        outcome=outcome,
        initial_aim=definition.aim,
        final_aim=final_aim,
        execution_order=tuple(execution_order),
        execution_batches=tuple(execution_batches),
        outputs=outputs,
        signals=tuple(signals),
        governor_decision=governor_result.value,
    )


def run_graph(
    definition: GraphDefinition, mode: ExecutionMode = ExecutionMode.SERIAL
) -> GraphResult:
    """Execute ``definition`` while preserving dependency and governance semantics."""

    node_by_name = {node.name: node for node in definition.nodes}
    if len(node_by_name) != len(definition.nodes):
        raise ValueError("graph node names must be unique")
    if definition.governor_node is not None and definition.governor_node not in node_by_name:
        raise ValueError("governor_node must reference an existing node")

    dependencies = {name: set() for name in node_by_name}
    for edge in definition.edges:
        if edge.source not in node_by_name or edge.target not in node_by_name:
            raise ValueError("graph edges must reference existing nodes")
        dependencies[edge.target].add(edge.source)

    pending = [node.name for node in definition.nodes]
    outputs: dict[str, NodeResult] = {}
    signals: list[SignalRecord] = []
    execution_order: list[str] = []
    execution_batches: list[tuple[str, ...]] = []

    while pending:
        ready = [name for name in pending if dependencies[name].issubset(outputs)]
        if not ready:
            raise ValueError("graph contains a dependency cycle")
        batch = ready if mode is ExecutionMode.PARALLEL else ready[:1]
        batch_results = _run_batch(
            definition, node_by_name, batch, outputs, signals, mode
        )

        execution_batches.append(tuple(batch))
        for name in batch:
            result = batch_results[name]
            outputs[name] = result
            pending.remove(name)
            execution_order.append(name)
            if result.signal is not SignalKind.OK:
                signals.append(
                    SignalRecord(
                        node=name,
                        kind=result.signal,
                        reason=result.reason,
                        proposed_goal_change=result.proposed_goal_change,
                    )
                )

        if any(signal.kind is SignalKind.HARD_VETO for signal in signals):
            return GraphResult(
                outcome=GraphOutcome.HARD_VETOED,
                initial_aim=definition.aim,
                final_aim=definition.aim,
                execution_order=tuple(execution_order),
                execution_batches=tuple(execution_batches),
                outputs=outputs,
                signals=tuple(signals),
            )
        if any(signal.kind is SignalKind.ESCALATION for signal in signals):
            return _finish_escalation(
                definition,
                node_by_name,
                outputs,
                signals,
                execution_order,
                execution_batches,
            )

    governor_decision: GovernorDecision | None = None
    outcome = GraphOutcome.SUCCESS
    final_aim = definition.aim
    if definition.governor_node is not None:
        governor_result = outputs.get(definition.governor_node)
        if governor_result is None or not isinstance(
            governor_result.value, GovernorDecision
        ):
            raise TypeError("governor node must return a GovernorDecision")
        governor_decision = governor_result.value
        outcome, final_aim = _interpret_governor_decision(
            definition.aim, governor_decision
        )

    return GraphResult(
        outcome=outcome,
        initial_aim=definition.aim,
        final_aim=final_aim,
        execution_order=tuple(execution_order),
        execution_batches=tuple(execution_batches),
        outputs=outputs,
        signals=tuple(signals),
        governor_decision=governor_decision,
    )
