import unittest

from loop_engineering import (
    ActionDecision,
    AuthorityScope,
    Evaluation,
    EvaluationStatus,
    LoopContract,
    LoopOutcome,
    RetryFeatureState,
    retry_feature_contract,
    run_loop,
)


class LoopEngineeringTests(unittest.TestCase):
    def test_loop_stops_after_the_feature_passes_evaluation(self) -> None:
        result = run_loop(retry_feature_contract())

        self.assertEqual(result.outcome, LoopOutcome.SUCCESS)
        self.assertEqual(result.attempts, 2)
        self.assertEqual(result.final_state, RetryFeatureState(retry_limit=3, validation_added=True))
        self.assertEqual(
            tuple(evaluation.status for evaluation in result.evaluations),
            (EvaluationStatus.CONTINUE, EvaluationStatus.SUCCESS),
        )

    def test_loop_reports_budget_exhaustion_without_changing_the_aim(self) -> None:
        contract = retry_feature_contract(budget=1)

        result = run_loop(contract)

        self.assertEqual(result.outcome, LoopOutcome.BUDGET_EXHAUSTED)
        self.assertEqual(result.local_aim, contract.local_aim)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.final_state, RetryFeatureState(retry_limit=5, validation_added=False))
        self.assertIsNotNone(result.escalation)
        assert result.escalation is not None
        self.assertEqual(result.escalation.required_authority, "graph_governor")
        self.assertEqual(
            result.escalation.reason,
            "Loop budget exhausted before the stopping condition was met.",
        )

    def test_loop_escalates_a_goal_change_instead_of_applying_it(self) -> None:
        initial_state = RetryFeatureState()
        contract = LoopContract(
            local_aim="Preserve compatibility while adding bounded retries.",
            initial_state=initial_state,
            action_policy=lambda context: ActionDecision(
                action="propose_goal_change",
                next_state=context.state,
                proposed_goal_change="Remove the compatibility requirement.",
            ),
            evaluator=lambda state: Evaluation(EvaluationStatus.CONTINUE, "Goal change required."),
            budget=1,
            stopping_condition=lambda evaluation: evaluation.status is EvaluationStatus.SUCCESS,
            authority_scope=AuthorityScope(frozenset({"edit_implementation", "edit_tests"})),
        )

        result = run_loop(contract)

        self.assertEqual(result.outcome, LoopOutcome.ESCALATED)
        self.assertEqual(result.local_aim, contract.local_aim)
        self.assertEqual(result.final_state, initial_state)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(result.evaluations, ())
        self.assertIsNotNone(result.escalation)
        assert result.escalation is not None
        self.assertEqual(result.escalation.required_authority, "graph_governor")
        self.assertEqual(
            result.escalation.proposed_goal_change,
            "Remove the compatibility requirement.",
        )

    def test_evaluator_can_escalate_after_inspecting_an_in_scope_change(self) -> None:
        changed_state = RetryFeatureState(retry_limit=3, validation_added=False)
        contract = LoopContract(
            local_aim="Preserve compatibility while adding bounded retries.",
            initial_state=RetryFeatureState(),
            action_policy=lambda context: ActionDecision(
                action="edit_implementation",
                next_state=changed_state,
            ),
            evaluator=lambda state: Evaluation(
                EvaluationStatus.ESCALATE,
                "The compatibility rule conflicts with the requested validation.",
                proposed_goal_change="Let the governor choose which requirement wins.",
            ),
            budget=2,
            stopping_condition=lambda evaluation: evaluation.status is EvaluationStatus.SUCCESS,
            authority_scope=AuthorityScope(frozenset({"edit_implementation", "edit_tests"})),
        )

        result = run_loop(contract)

        self.assertEqual(result.outcome, LoopOutcome.ESCALATED)
        self.assertEqual(result.final_state, changed_state)
        self.assertEqual(result.attempts, 1)
        self.assertEqual(len(result.evaluations), 1)
        self.assertIsNotNone(result.escalation)
        assert result.escalation is not None
        self.assertEqual(
            result.escalation.reason,
            "The compatibility rule conflicts with the requested validation.",
        )


if __name__ == "__main__":
    unittest.main()
