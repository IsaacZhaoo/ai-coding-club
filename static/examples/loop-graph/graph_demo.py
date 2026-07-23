from graph_engineering import (
    ExecutionMode,
    GovernorAction,
    GovernorDecision,
    build_feature_change_graph,
    run_graph,
)


def approve_change(context):
    return GovernorDecision(
        GovernorAction.APPROVE,
        "Tests and review evidence are sufficient for approval.",
    )


def main() -> None:
    graph = build_feature_change_graph(approve_change)

    for mode in (ExecutionMode.SERIAL, ExecutionMode.PARALLEL):
        result = run_graph(graph, mode)
        print(f"mode: {mode.value}")
        print(f"outcome: {result.outcome.value}")
        print(f"batches: {result.execution_batches}")
        print(f"merged state: {result.outputs['merge'].value}")
        print()


if __name__ == "__main__":
    main()
