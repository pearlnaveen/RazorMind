from ml.anomaly_detection import detect_anomalies
from ml.recovery_prediction import predict_recovery
from ml.root_cause import analyze_failure_reasons
from ml.revenue_prediction import predict_next_days


def ask_finance_controller(question):

    question = question.lower().strip()


    # ==========================================
    # RECOVERY
    # ==========================================

    if (
        "recover" in question
        or "recovery" in question
    ):

        recovery = predict_recovery()

        high_probability = recovery[
            recovery["recovery_probability"] >= 0.70
        ]

        potential_recovery = float(
            high_probability[
                "potential_recovery"
            ].sum()
        )

        return {

            "question": question,

            "answer": (
                f"There are "
                f"{len(high_probability)} "
                f"high-probability recovery "
                f"opportunities. The estimated "
                f"recovery opportunity is "
                f"₹{potential_recovery:,.2f}. "
                f"Prioritize high-value failed "
                f"payments with recovery probability "
                f"above 70%."
            ),

            "data": {

                "recovery_transactions":
                    len(high_probability),

                "estimated_recovery":
                    round(
                        potential_recovery,
                        2
                    )
            }
        }


    # ==========================================
    # PAYMENT RISK
    # ==========================================

    if (
        "risk" in question
        or "failure" in question
        or "fail" in question
        or "problem" in question
    ):

        anomalies = detect_anomalies()

        detected = anomalies[
            anomalies["anomaly"] == "anomaly"
        ]

        root_cause = (
            analyze_failure_reasons()
        )

        latest_failure_rate = 0
        failed_transactions = 0

        if len(detected) > 0:

            latest = detected.iloc[-1]

            latest_failure_rate = round(
                float(
                    latest["failure_rate"]
                ) * 100,
                2
            )

            failed_transactions = int(
                latest[
                    "failed_transactions"
                ]
            )

        reason = root_cause.get(
            "top_failure_reason",
            "Unknown"
        )

        percentage = root_cause.get(
            "top_failure_percentage",
            0
        )

        return {

            "question": question,

            "answer": (
                f"The latest detected failure "
                f"rate is {latest_failure_rate}%. "
                f"The dominant failure reason is "
                f"{reason}, accounting for "
                f"{percentage}% of failed payments. "
                f"There are "
                f"{len(detected)} anomalous periods."
            ),

            "data": {

                "failure_rate":
                    latest_failure_rate,

                "failed_transactions":
                    failed_transactions,

                "top_failure_reason":
                    reason,

                "top_failure_percentage":
                    percentage,

                "anomalies":
                    len(detected)
            }
        }


    # ==========================================
    # REVENUE
    # ==========================================

    if (
        "revenue" in question
        or "forecast" in question
        or "future" in question
    ):

        forecast = predict_next_days(7)

        if len(forecast) == 0:

            return {
                "question": question,
                "answer":
                    "There is not enough data "
                    "to generate a revenue forecast.",
                "data": {}
            }

        average_revenue = float(
            forecast[
                "predicted_revenue"
            ].mean()
        )

        return {

            "question": question,

            "answer": (
                f"The predicted average daily "
                f"revenue for the next 7 days "
                f"is approximately "
                f"₹{average_revenue:,.2f}."
            ),

            "data": {

                "average_daily_revenue":
                    round(
                        average_revenue,
                        2
                    )
            }
        }


    # ==========================================
    # GENERAL FINANCE QUESTION
    # ==========================================

    if (
        "today" in question
        or "focus" in question
        or "priority" in question
        or "prioritize" in question
    ):

        anomalies = detect_anomalies()

        detected = anomalies[
            anomalies["anomaly"] == "anomaly"
        ]

        root_cause = (
            analyze_failure_reasons()
        )

        recovery = predict_recovery()

        high_probability = recovery[
            recovery["recovery_probability"] >= 0.70
        ]

        potential_recovery = float(
            high_probability[
                "potential_recovery"
            ].sum()
        )

        reason = root_cause.get(
            "top_failure_reason",
            "Unknown"
        )

        if potential_recovery > 0:

            answer = (
                f"Your highest immediate priority "
                f"should be revenue recovery. "
                f"There are "
                f"{len(high_probability)} "
                f"high-probability recovery "
                f"opportunities worth approximately "
                f"₹{potential_recovery:,.2f}. "
                f"Also investigate {reason}, "
                f"which is the leading payment failure "
                f"reason."
            )

        elif len(detected) > 0:

            answer = (
                "Your immediate priority should be "
                "investigating unusual payment failure "
                "activity."
            )

        else:

            answer = (
                "No major financial risk was detected "
                "by the current analysis."
            )

        return {

            "question": question,

            "answer": answer,

            "data": {

                "recovery_opportunities":
                    len(high_probability),

                "potential_recovery":
                    round(
                        potential_recovery,
                        2
                    ),

                "anomalies":
                    len(detected),

                "top_failure_reason":
                    reason
            }
        }


    # ==========================================
    # UNKNOWN
    # ==========================================

    return {

        "question": question,

        "answer": (
            "I can analyze payment failures, "
            "recovery opportunities, revenue "
            "forecasts and financial risks. "
            "Try asking: "
            "'How much can we recover?', "
            "'What is the biggest payment risk?', "
            "'What is the revenue forecast?', "
            "or 'What should I focus on today?'"
        ),

        "data": {}
    }


# ==========================================
# TEST
# ==========================================

if __name__ == "__main__":

    test_questions = [

        "How much can we recover?",

        "What is the biggest payment risk?",

        "What is the revenue forecast?",

        "What should I focus on today?"
    ]


    for question in test_questions:

        print(
            "\n================================"
        )

        print(
            "QUESTION:",
            question
        )

        result = ask_finance_controller(
            question
        )

        print(
            "\nANSWER:"
        )

        print(
            result["answer"]
        )