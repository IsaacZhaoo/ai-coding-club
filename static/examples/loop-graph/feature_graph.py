"""The shared retry-feature scenario used by the Graph tutorial."""

from __future__ import annotations

from graph_model import (
    EdgeRelation,
    Governor,
    GraphContext,
    GraphDefinition,
    GraphEdge,
    GraphNode,
    NodeResult,
    SignalKind,
)
from loop_engineering import (
    LoopContract,
    LoopOutcome,
    LoopResult,
    RetryFeatureState,
    retry_feature_contract,
    run_loop,
)


def build_feature_change_graph(
    governor: Governor,
    *,
    review_signal: SignalKind = SignalKind.OK,
    implementation_contract: LoopContract[RetryFeatureState] | None = None,
) -> GraphDefinition:
    """Build the tutorial graph around the verified retry-feature Loop."""

    contract = implementation_contract or retry_feature_contract()

    def prepare_context(context: GraphContext) -> NodeResult:
        return NodeResult({"compatibility_required": True, "max_retry_limit": 3})

    def implement(context: GraphContext) -> NodeResult:
        loop_result = run_loop(contract)
        if loop_result.outcome in {LoopOutcome.BUDGET_EXHAUSTED, LoopOutcome.ESCALATED}:
            escalation = loop_result.escalation
            return NodeResult(
                loop_result,
                signal=SignalKind.ESCALATION,
                reason=escalation.reason if escalation else "The implementation Loop escalated.",
                proposed_goal_change=escalation.proposed_goal_change if escalation else None,
            )
        return NodeResult(loop_result)

    def run_tests(context: GraphContext) -> NodeResult:
        loop_result = context.outputs["implementation"].value
        if not isinstance(loop_result, LoopResult):
            raise TypeError("implementation node must return a LoopResult")
        return NodeResult({"passed": loop_result.outcome is LoopOutcome.SUCCESS})

    def review(context: GraphContext) -> NodeResult:
        reasons = {
            SignalKind.OK: "Review found no blocking issue.",
            SignalKind.SOFT_OBJECTION: (
                "Review requests a follow-up note but does not block the change."
            ),
            SignalKind.HARD_VETO: (
                "Review found a compatibility regression and vetoed the change."
            ),
        }
        return NodeResult(
            {"reviewed": True},
            signal=review_signal,
            reason=reasons.get(review_signal, "Review escalated the change."),
        )

    def merge(context: GraphContext) -> NodeResult:
        loop_result = context.outputs["implementation"].value
        if not isinstance(loop_result, LoopResult) or not isinstance(
            loop_result.final_state, RetryFeatureState
        ):
            raise TypeError("implementation node must return the retry-feature LoopResult")
        test_result = context.outputs["tests"].value
        if not isinstance(test_result, dict):
            raise TypeError("tests node must return a result mapping")
        return NodeResult(
            {
                "retry_limit": loop_result.final_state.retry_limit,
                "validation_added": loop_result.final_state.validation_added,
                "tests_passed": test_result["passed"],
                "review_status": context.outputs["review"].signal.value,
            }
        )

    def approve(context: GraphContext) -> NodeResult:
        return NodeResult(governor(context))

    return GraphDefinition(
        aim=contract.local_aim,
        nodes=(
            GraphNode("context", prepare_context),
            GraphNode("implementation", implement),
            GraphNode("tests", run_tests),
            GraphNode("review", review),
            GraphNode("merge", merge),
            GraphNode("approval", approve),
        ),
        edges=(
            GraphEdge("context", "implementation", EdgeRelation.HANDOFF),
            GraphEdge("implementation", "tests", EdgeRelation.DATA_FLOW),
            GraphEdge("implementation", "review", EdgeRelation.HANDOFF),
            GraphEdge("tests", "merge", EdgeRelation.DEPENDENCY),
            GraphEdge("review", "merge", EdgeRelation.VETO),
            GraphEdge("merge", "approval", EdgeRelation.APPROVAL),
        ),
        governor_node="approval",
    )
