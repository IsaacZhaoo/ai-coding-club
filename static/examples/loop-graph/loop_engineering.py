"""A deterministic, API-free example of a bounded coding-agent loop."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import Callable, Generic, TypeVar


StateT = TypeVar("StateT")


class EvaluationStatus(str, Enum):
    CONTINUE = "continue"
    SUCCESS = "success"
    ESCALATE = "escalate"


class LoopOutcome(str, Enum):
    SUCCESS = "success"
    BUDGET_EXHAUSTED = "budget_exhausted"
    ESCALATED = "escalated"


@dataclass(frozen=True)
class AuthorityScope:
    allowed_actions: frozenset[str]
    goal_change_authority: str = "graph_governor"


@dataclass(frozen=True)
class LoopContext(Generic[StateT]):
    local_aim: str
    state: StateT
    attempt: int
    last_feedback: str | None
    authority_scope: AuthorityScope


@dataclass(frozen=True)
class ActionDecision(Generic[StateT]):
    action: str
    next_state: StateT | None = None
    proposed_goal_change: str | None = None


@dataclass(frozen=True)
class Evaluation:
    status: EvaluationStatus
    feedback: str
    proposed_goal_change: str | None = None


@dataclass(frozen=True)
class EscalationResult:
    reason: str
    required_authority: str
    proposed_goal_change: str | None = None


@dataclass(frozen=True)
class LoopContract(Generic[StateT]):
    local_aim: str
    initial_state: StateT
    action_policy: Callable[[LoopContext[StateT]], ActionDecision[StateT]]
    evaluator: Callable[[StateT], Evaluation]
    budget: int
    stopping_condition: Callable[[Evaluation], bool]
    authority_scope: AuthorityScope


@dataclass(frozen=True)
class LoopResult(Generic[StateT]):
    outcome: LoopOutcome
    local_aim: str
    final_state: StateT
    attempts: int
    evaluations: tuple[Evaluation, ...]
    escalation: EscalationResult | None = None


@dataclass(frozen=True)
class RetryFeatureState:
    retry_limit: int | None = None
    validation_added: bool = False


def run_loop(contract: LoopContract[StateT]) -> LoopResult[StateT]:
    """Run the bounded loop described by ``contract``."""

    if contract.budget < 1:
        raise ValueError("budget must be at least 1")

    state = contract.initial_state
    evaluations: list[Evaluation] = []
    last_feedback: str | None = None

    for attempt in range(1, contract.budget + 1):
        decision = contract.action_policy(
            LoopContext(
                local_aim=contract.local_aim,
                state=state,
                attempt=attempt,
                last_feedback=last_feedback,
                authority_scope=contract.authority_scope,
            )
        )
        if decision.proposed_goal_change is not None or decision.action not in contract.authority_scope.allowed_actions:
            return LoopResult(
                outcome=LoopOutcome.ESCALATED,
                local_aim=contract.local_aim,
                final_state=state,
                attempts=attempt,
                evaluations=tuple(evaluations),
                escalation=EscalationResult(
                    reason="The proposed action is outside the Loop's authority scope.",
                    required_authority=contract.authority_scope.goal_change_authority,
                    proposed_goal_change=decision.proposed_goal_change,
                ),
            )
        if decision.next_state is None:
            raise ValueError("an in-scope action must provide next_state")

        state = decision.next_state
        evaluation = contract.evaluator(state)
        evaluations.append(evaluation)
        last_feedback = evaluation.feedback

        if evaluation.status is EvaluationStatus.ESCALATE:
            return LoopResult(
                outcome=LoopOutcome.ESCALATED,
                local_aim=contract.local_aim,
                final_state=state,
                attempts=attempt,
                evaluations=tuple(evaluations),
                escalation=EscalationResult(
                    reason=evaluation.feedback,
                    required_authority=contract.authority_scope.goal_change_authority,
                    proposed_goal_change=evaluation.proposed_goal_change,
                ),
            )

        if contract.stopping_condition(evaluation):
            return LoopResult(
                outcome=LoopOutcome.SUCCESS,
                local_aim=contract.local_aim,
                final_state=state,
                attempts=attempt,
                evaluations=tuple(evaluations),
            )

    return LoopResult(
        outcome=LoopOutcome.BUDGET_EXHAUSTED,
        local_aim=contract.local_aim,
        final_state=state,
        attempts=contract.budget,
        evaluations=tuple(evaluations),
        escalation=EscalationResult(
            reason="Loop budget exhausted before the stopping condition was met.",
            required_authority=contract.authority_scope.goal_change_authority,
        ),
    )


def retry_feature_contract(budget: int = 3) -> LoopContract[RetryFeatureState]:
    """Build the tutorial's deterministic feature-change contract."""

    def action_policy(context: LoopContext[RetryFeatureState]) -> ActionDecision[RetryFeatureState]:
        if context.attempt == 1:
            return ActionDecision(
                action="edit_implementation",
                next_state=RetryFeatureState(retry_limit=5, validation_added=False),
            )
        return ActionDecision(
            action="edit_implementation",
            next_state=RetryFeatureState(retry_limit=3, validation_added=True),
        )

    def evaluator(state: RetryFeatureState) -> Evaluation:
        if state.retry_limit is not None and state.retry_limit <= 3 and state.validation_added:
            return Evaluation(EvaluationStatus.SUCCESS, "Feature constraints pass.")
        return Evaluation(
            EvaluationStatus.CONTINUE,
            "Retry limit must be at most 3 and validation must be present.",
        )

    return LoopContract(
        local_aim="Add a bounded retry setting without changing compatibility requirements.",
        initial_state=RetryFeatureState(),
        action_policy=action_policy,
        evaluator=evaluator,
        budget=budget,
        stopping_condition=lambda evaluation: evaluation.status is EvaluationStatus.SUCCESS,
        authority_scope=AuthorityScope(frozenset({"edit_implementation", "edit_tests"})),
    )
