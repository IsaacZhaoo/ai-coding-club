"""Data model shared by the graph runner and tutorial scenario."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Callable, Mapping


class ExecutionMode(str, Enum):
    SERIAL = "serial"
    PARALLEL = "parallel"


class EdgeRelation(str, Enum):
    DEPENDENCY = "dependency"
    HANDOFF = "handoff"
    DATA_FLOW = "data_flow"
    VETO = "veto"
    APPROVAL = "approval"


class SignalKind(str, Enum):
    OK = "ok"
    SOFT_OBJECTION = "soft_objection"
    HARD_VETO = "hard_veto"
    ESCALATION = "escalation"


class GovernorAction(str, Enum):
    APPROVE = "approve"
    REJECT = "reject"
    CHANGE_GOAL = "change_goal"


class GraphOutcome(str, Enum):
    SUCCESS = "success"
    HARD_VETOED = "hard_vetoed"
    REJECTED = "rejected"
    GOAL_CHANGED = "goal_changed"
    ESCALATED = "escalated"


@dataclass(frozen=True)
class GovernorDecision:
    action: GovernorAction
    reason: str
    new_goal: str | None = None


@dataclass(frozen=True)
class NodeResult:
    value: object = None
    signal: SignalKind = SignalKind.OK
    reason: str = ""
    proposed_goal_change: str | None = None


@dataclass(frozen=True)
class SignalRecord:
    node: str
    kind: SignalKind
    reason: str
    proposed_goal_change: str | None = None


@dataclass(frozen=True)
class GraphContext:
    aim: str
    outputs: Mapping[str, NodeResult]
    signals: tuple[SignalRecord, ...]


NodeHandler = Callable[[GraphContext], NodeResult]
Governor = Callable[[GraphContext], GovernorDecision]


@dataclass(frozen=True)
class GraphNode:
    name: str
    handler: NodeHandler


@dataclass(frozen=True)
class GraphEdge:
    source: str
    target: str
    relation: EdgeRelation = EdgeRelation.DEPENDENCY


@dataclass(frozen=True)
class GraphDefinition:
    aim: str
    nodes: tuple[GraphNode, ...]
    edges: tuple[GraphEdge, ...]
    governor_node: str | None = None


@dataclass(frozen=True)
class GraphResult:
    outcome: GraphOutcome
    initial_aim: str
    final_aim: str
    execution_order: tuple[str, ...]
    execution_batches: tuple[tuple[str, ...], ...]
    outputs: Mapping[str, NodeResult] = field(default_factory=dict)
    signals: tuple[SignalRecord, ...] = ()
    governor_decision: GovernorDecision | None = None
