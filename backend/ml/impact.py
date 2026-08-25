from ml.recovery_prediction import predict_recovery


def calculate_recovery_impact():

    result = predict_recovery()

    high_confidence = result[
        result["recovery_probability"] >= 0.70
    ]

    failed_amount = float(
        result["amount"].sum()
    )

    high_confidence_amount = float(
        high_confidence["amount"].sum()
    )

    estimated_recovery = float(
        high_confidence["potential_recovery"].sum()
    )

    return {

        "total_failed_amount":
            round(failed_amount, 2),

        "high_confidence_failed_amount":
            round(high_confidence_amount, 2),

        "estimated_recovery":
            round(estimated_recovery, 2),

        "high_confidence_transactions":
            len(high_confidence)
    }


if __name__ == "__main__":

    result = calculate_recovery_impact()

    print("\nRecovery Impact\n")

    for key, value in result.items():

        print(
            f"{key}: {value}"
        )