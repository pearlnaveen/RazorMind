from ml.anomaly_detection import detect_anomalies
from ml.recovery_prediction import predict_recovery
from ml.revenue_prediction import predict_next_days
from ml.root_cause import analyze_failure_reasons
from ml.priority import calculate_priority


def generate_recommendations():

    recommendations = []

    # ==========================================
    # 1. ANOMALY ANALYSIS
    # ==========================================

    anomalies = detect_anomalies()

    detected = anomalies[
        anomalies["anomaly"] == "anomaly"
    ]

    if len(detected) > 0:

        latest = detected.iloc[-1]

        failure_rate = float(
            latest["failure_rate"] * 100
        )

        failed_transactions = int(
            latest["failed_transactions"]
        )

        recommendations.append({

            "priority": "HIGH",

            "category": "Payment Risk",

            "title":
                "Unusual payment failure activity",

            "description":
                (
                    f"Payment failure rate reached "
                    f"{failure_rate:.2f}% with "
                    f"{failed_transactions} "
                    f"failed transactions."
                ),

            "action":
                (
                    "Investigate the dominant failure "
                    "reason and prioritize payment retries."
                )
        })


    # ==========================================
    # 2. ROOT CAUSE ANALYSIS
    # ==========================================

    root_cause = analyze_failure_reasons()

    if "top_failure_reason" in root_cause:

        reason = root_cause[
            "top_failure_reason"
        ]

        percentage = root_cause[
            "top_failure_percentage"
        ]

        recommendations.append({

            "priority": "HIGH",

            "category": "Root Cause",

            "title":
                "Payment failure root cause identified",

            "description":
                (
                    f"{reason} accounts for "
                    f"{percentage:.2f}% of failed payments."
                ),

            "action":
                (
                    f"Investigate {reason} as the primary "
                    f"payment failure source and prioritize "
                    f"mitigation."
                )
        })


    # ==========================================
    # 3. RECOVERY ANALYSIS
    # ==========================================

    recovery = predict_recovery()

    high_probability = recovery[
        recovery["recovery_probability"] >= 0.70
    ]

    potential_recovery = float(
        high_probability["potential_recovery"].sum()
    )

    if len(high_probability) > 0:

        # Find highest-value opportunity
        top_transaction = high_probability.loc[
            high_probability["potential_recovery"].idxmax()
        ]

        top_priority = calculate_priority(
            recovery_probability=float(
                top_transaction["recovery_probability"]
            ),
            amount=float(
                top_transaction["amount"]
            )
        )

        recommendations.append({

            "priority": top_priority["priority"],

            "priority_score":
                top_priority["score"],

            "category":
                "Revenue Recovery",

            "title":
                "High-probability recovery opportunities",

            "description":
                (
                    f"{len(high_probability)} failed payments "
                    f"have recovery probability above 70%, "
                    f"representing an estimated "
                    f"₹{potential_recovery:,.2f} opportunity."
                ),

            "action":
                (
                    "Prioritize retry attempts beginning "
                    "with the highest-value recoverable payments."
                ),

            "potential_recovery":
                round(
                    potential_recovery,
                    2
                ),

            "top_transaction_amount":
                float(
                    top_transaction["amount"]
                ),

            "top_recovery_probability":
                round(
                    float(
                        top_transaction[
                            "recovery_probability"
                        ]
                    ) * 100,
                    2
                )
        })


    # ==========================================
    # 4. REVENUE FORECAST
    # ==========================================

    forecast = predict_next_days(7)

    if len(forecast) > 0:

        predicted_revenue = float(
            forecast[
                "predicted_revenue"
            ].mean()
        )

        recommendations.append({

            "priority": "MEDIUM",

            "category": "Revenue Planning",

            "title":
                "7-day revenue forecast available",

            "description":
                (
                    f"Expected average daily revenue is "
                    f"₹{predicted_revenue:,.2f}."
                ),

            "action":
                (
                    "Use the forecast to plan cash flow, "
                    "payment operations and recovery targets."
                )
        })


    # ==========================================
    # 5. FINAL RESPONSE
    # ==========================================

    return {

        "recommendation_count":
            len(recommendations),

        "recommendations":
            recommendations
    }


# ==========================================
# TESTING
# ==========================================

if __name__ == "__main__":

    result = generate_recommendations()

    print(
        "\n========== RAZORMIND "
        "RECOMMENDATIONS ==========\n"
    )

    print(
        "Total Recommendations:",
        result["recommendation_count"]
    )

    print()

    for recommendation in result[
        "recommendations"
    ]:

        print(
            f"[{recommendation['priority']}] "
            f"{recommendation['title']}"
        )

        print(
            "Category:",
            recommendation["category"]
        )

        print(
            "Description:",
            recommendation["description"]
        )

        print(
            "Action:",
            recommendation["action"]
        )

        if "potential_recovery" in recommendation:

            print(
                "Potential Recovery: ₹",
                recommendation[
                    "potential_recovery"
                ]
            )

        print(
            "-" * 60
        )