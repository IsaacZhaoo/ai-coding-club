from loop_engineering import retry_feature_contract, run_loop


def main() -> None:
    contract = retry_feature_contract()
    result = run_loop(contract)

    print(f"aim: {result.local_aim}")
    print(f"outcome: {result.outcome.value}")
    print(f"attempts: {result.attempts}/{contract.budget}")
    print(f"final state: {result.final_state}")
    for attempt, evaluation in enumerate(result.evaluations, start=1):
        print(f"evaluation {attempt}: {evaluation.status.value} — {evaluation.feedback}")


if __name__ == "__main__":
    main()
