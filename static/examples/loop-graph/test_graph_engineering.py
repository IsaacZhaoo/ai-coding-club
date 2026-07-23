import unittest
from threading import Barrier, Lock, current_thread

from loop_engineering import (
    ActionDecision,
    AuthorityScope,
    Evaluation,
    EvaluationStatus,
    LoopContract,
    RetryFeatureState,
)

from graph_engineering import (
    ExecutionMode,
    GraphDefinition,
    GraphEdge,
    GraphNode,
    GraphOutcome,
    GovernorAction,
    GovernorDecision,
    NodeResult,
    SignalKind,
    build_feature_change_graph,
    run_graph,
)


class GraphEngineeringTests(unittest.TestCase):
    def test_serial_execution_respects_dependency_order(self) -> None:
        graph = GraphDefinition(
            aim="Prepare, implement, and verify a feature change.",
            nodes=(
                GraphNode("context", lambda context: NodeResult("context ready")),
                GraphNode("implementation", lambda context: NodeResult("patch ready")),
                GraphNode("tests", lambda context: NodeResult("tests pass")),
            ),
            edges=(
                GraphEdge("context", "implementation"),
                GraphEdge("implementation", "tests"),
            ),
        )

        result = run_graph(graph, ExecutionMode.SERIAL)

        self.assertEqual(result.outcome, GraphOutcome.SUCCESS)
        self.assertEqual(result.execution_order, ("context", "implementation", "tests"))
        self.assertEqual(
            result.execution_batches,
            (("context",), ("implementation",), ("tests",)),
        )
        self.assertEqual(result.outputs["tests"].value, "tests pass")

    def test_parallel_execution_runs_independent_branches_in_one_batch(self) -> None:
        graph = GraphDefinition(
            aim="Verify a feature through independent checks.",
            nodes=(
                GraphNode("implementation", lambda context: NodeResult("patch ready")),
                GraphNode(
                    "tests",
                    lambda context: NodeResult(f"tested {context.outputs['implementation'].value}"),
                ),
                GraphNode(
                    "review",
                    lambda context: NodeResult(f"reviewed {context.outputs['implementation'].value}"),
                ),
                GraphNode("merge", lambda context: NodeResult("checks merged")),
            ),
            edges=(
                GraphEdge("implementation", "tests"),
                GraphEdge("implementation", "review"),
                GraphEdge("tests", "merge"),
                GraphEdge("review", "merge"),
            ),
        )

        result = run_graph(graph, ExecutionMode.PARALLEL)

        self.assertEqual(
            result.execution_batches,
            (("implementation",), ("tests", "review"), ("merge",)),
        )
        self.assertEqual(result.outputs["tests"].value, "tested patch ready")
        self.assertEqual(result.outputs["review"].value, "reviewed patch ready")

    def test_parallel_mode_uses_multiple_workers_for_independent_nodes(self) -> None:
        barrier = Barrier(2, timeout=2)
        worker_names = set()
        worker_names_lock = Lock()

        def branch(context):
            with worker_names_lock:
                worker_names.add(current_thread().name)
            barrier.wait()
            return NodeResult("done")

        graph = GraphDefinition(
            aim="Run independent work concurrently.",
            nodes=(GraphNode("left", branch), GraphNode("right", branch)),
            edges=(),
        )

        result = run_graph(graph, ExecutionMode.PARALLEL)

        self.assertEqual(result.execution_batches, (("left", "right"),))
        self.assertEqual(len(worker_names), 2)

    def test_feature_graph_merges_verified_branch_outputs(self) -> None:
        graph = build_feature_change_graph(
            lambda context: GovernorDecision(GovernorAction.APPROVE, "Verified change approved.")
        )

        result = run_graph(graph, ExecutionMode.SERIAL)

        self.assertEqual(
            result.outputs["merge"].value,
            {
                "retry_limit": 3,
                "validation_added": True,
                "tests_passed": True,
                "review_status": "ok",
            },
        )

    def test_hard_veto_stops_before_merge_and_governor_approval(self) -> None:
        governor_calls = []
        graph = build_feature_change_graph(
            lambda context: governor_calls.append(context)
            or GovernorDecision(GovernorAction.APPROVE, "Should not be called."),
            review_signal=SignalKind.HARD_VETO,
        )

        result = run_graph(graph, ExecutionMode.PARALLEL)

        self.assertEqual(result.outcome, GraphOutcome.HARD_VETOED)
        self.assertNotIn("merge", result.outputs)
        self.assertNotIn("approval", result.outputs)
        self.assertEqual(governor_calls, [])
        self.assertEqual(
            tuple((signal.node, signal.kind) for signal in result.signals),
            (("review", SignalKind.HARD_VETO),),
        )

    def test_soft_objection_reaches_the_governor_without_blocking_merge(self) -> None:
        received_signals = []
        expected_decision = GovernorDecision(
            GovernorAction.APPROVE,
            "Approve now and track the review note separately.",
        )

        def governor(context):
            received_signals.extend(context.signals)
            return expected_decision

        graph = build_feature_change_graph(governor, review_signal=SignalKind.SOFT_OBJECTION)

        result = run_graph(graph, ExecutionMode.PARALLEL)

        self.assertEqual(result.outcome, GraphOutcome.SUCCESS)
        self.assertEqual(result.governor_decision, expected_decision)
        self.assertEqual(result.outputs["merge"].value["review_status"], "soft_objection")
        self.assertEqual(
            tuple((signal.node, signal.kind) for signal in received_signals),
            (("review", SignalKind.SOFT_OBJECTION),),
        )

    def test_escalation_routes_to_an_injected_governor_who_may_change_the_goal(self) -> None:
        escalating_contract = LoopContract(
            local_aim="Preserve compatibility while adding bounded retries.",
            initial_state=RetryFeatureState(),
            action_policy=lambda context: ActionDecision(
                action="propose_goal_change",
                next_state=context.state,
                proposed_goal_change="Replace compatibility with a migration requirement.",
            ),
            evaluator=lambda state: Evaluation(EvaluationStatus.CONTINUE, "Goal change required."),
            budget=1,
            stopping_condition=lambda evaluation: evaluation.status is EvaluationStatus.SUCCESS,
            authority_scope=AuthorityScope(frozenset({"edit_implementation", "edit_tests"})),
        )
        received_signals = []
        expected_decision = GovernorDecision(
            GovernorAction.CHANGE_GOAL,
            "The owner approved a migration instead of compatibility.",
            new_goal="Add bounded retries and provide a migration path.",
        )

        def governor(context):
            received_signals.extend(context.signals)
            return expected_decision

        graph = build_feature_change_graph(governor, implementation_contract=escalating_contract)

        result = run_graph(graph, ExecutionMode.SERIAL)

        self.assertEqual(result.outcome, GraphOutcome.GOAL_CHANGED)
        self.assertEqual(result.final_aim, expected_decision.new_goal)
        self.assertEqual(result.execution_order, ("context", "implementation", "approval"))
        self.assertNotIn("tests", result.outputs)
        self.assertEqual(result.governor_decision, expected_decision)
        self.assertEqual(
            tuple((signal.node, signal.kind, signal.proposed_goal_change) for signal in received_signals),
            (
                (
                    "implementation",
                    SignalKind.ESCALATION,
                    "Replace compatibility with a migration requirement.",
                ),
            ),
        )

    def test_same_feature_topology_runs_serially_or_in_parallel(self) -> None:
        governor = lambda context: GovernorDecision(
            GovernorAction.APPROVE, "Verified change approved."
        )

        serial = run_graph(build_feature_change_graph(governor), ExecutionMode.SERIAL)
        parallel = run_graph(build_feature_change_graph(governor), ExecutionMode.PARALLEL)

        self.assertEqual(serial.outcome, GraphOutcome.SUCCESS)
        self.assertEqual(parallel.outcome, GraphOutcome.SUCCESS)
        self.assertEqual(serial.outputs["merge"].value, parallel.outputs["merge"].value)
        self.assertEqual(
            parallel.execution_batches,
            (
                ("context",),
                ("implementation",),
                ("tests", "review"),
                ("merge",),
                ("approval",),
            ),
        )


if __name__ == "__main__":
    unittest.main()
