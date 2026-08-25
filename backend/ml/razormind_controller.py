from ml.anomaly_detection import detect_anomalies
from ml.recovery_prediction import predict_recovery
from ml.root_cause import analyze_failure_reasons
from ml.revenue_prediction import predict_next_days

def get_razormind_insight():

    print("\n========== RAZORMIND CONTROLLER ==========")

    # =====================================================
    # 1. ANOMALY DETECTION
    # =====================================================

    print("STEP 1: Anomaly detection...")

    anomalies = detect_anomalies()

    detected = anomalies[
        anomalies["anomaly"] == "anomaly"
    ]

    print("STEP 1 DONE")


    # =====================================================
    # 2. ROOT CAUSE
    # =====================================================

    print("STEP 2: Root cause analysis...")

    root_cause = analyze_failure_reasons()

    print("STEP 2 DONE")


    # =====================================================
    # PAYMENT RISK
    # =====================================================

    failure_rate = 0.0
    failed_transactions = 0

    if len(detected) > 0:

        latest = detected.iloc[-1]

        failure_rate = float(
            latest["failure_rate"]
        ) * 100

        failed_transactions = int(
            latest["failed_transactions"]
        )


    top_failure_reason = root_cause.get(
        "top_failure_reason",
        "Unknown"
    )

    top_failure_percentage = root_cause.get(
        "top_failure_percentage",
        0
    )


    # =====================================================
    # 3. RECOVERY PREDICTION
    # =====================================================

    print("STEP 3: Recovery prediction...")

    recovery = predict_recovery()

    print("STEP 3 DONE")


    high_probability = recovery[
        recovery["recovery_probability"] >= 0.70
    ]


    recovery_count = len(
        high_probability
    )


    potential_recovery = float(
        high_probability[
            "potential_recovery"
        ].sum()
    )


    # =====================================================
    # 4. REVENUE FORECAST
    # =====================================================

    print("STEP 4: Revenue forecast...")

    forecast = predict_next_days(7)

    print("STEP 4 DONE")


    average_daily_revenue = 0.0

    if len(forecast) > 0:

        average_daily_revenue = float(
            forecast[
                "predicted_revenue"
            ].mean()
        )


    # =====================================================
    # 5. PRIORITY ENGINE
    # =====================================================

    if potential_recovery > 0:

        priority = "HIGH"

        title = (
            "Prioritize revenue recovery"
        )

        action = (
            "Prioritize retry attempts for "
            "failed payments with recovery "
            "probability above 70%, starting "
            "with the highest-value transactions."
        )

    elif len(detected) > 0:

        priority = "HIGH"

        title = (
            "Investigate payment failures"
        )

        action = (
            "Investigate the dominant payment "
            "failure reason and implement "
            "mitigation measures."
        )

    else:

        priority = "MEDIUM"

        title = (
            "Monitor payment performance"
        )

        action = (
            "Continue monitoring payment "
            "success rates and revenue trends."
        )


    # =====================================================
    # 6. FINAL DASHBOARD RESPONSE
    # =====================================================

    insight = {

        "status": "success",

        "priority": priority,

        "title": title,


        "payment_risk": {

            "failure_rate":
                round(
                    failure_rate,
                    2
                ),

            "failed_transactions":
                failed_transactions,

            "top_failure_reason":
                top_failure_reason,

            "top_failure_percentage":
                round(
                    float(
                        top_failure_percentage
                    ),
                    2
                )
        },


        "recovery": {

            "opportunities":
                recovery_count,

            "potential_recovery":
                round(
                    potential_recovery,
                    2
                )
        },


        "forecast": {

            "average_daily_revenue":
                round(
                    average_daily_revenue,
                    2
                )
        },


        "recommended_action":
            action
    }


    print("STEP 5: Controller response generated.")

    print(
        "==========================================\n"
    )

    return insight