from ml.cache import (cached_recovery, cached_risk, cached_root_cause, cached_forecast)

# ============================================================
# TOOL 1: PAYMENT RISK ANALYSIS
# ============================================================

def get_payment_risk():

    anomalies = cached_risk()

    detected = anomalies[
        anomalies["anomaly"] == "anomaly"
    ]

    root_cause = cached_root_cause()

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

    result = {

        "anomalies": int(
            len(detected)
        ),

        "failure_rate": round(
            failure_rate,
            2
        ),

        "failed_transactions":
            failed_transactions,

        "top_failure_reason":
            root_cause.get(
                "top_failure_reason",
                "Unknown"
            ),

        "top_failure_percentage":
            round(
                float(
                    root_cause.get(
                        "top_failure_percentage",
                        0
                    )
                ),
                2
            )
    }

    return result


# ============================================================
# TOOL 2: REVENUE RECOVERY ANALYSIS
# ============================================================

def get_recovery_opportunities():

    recovery = cached_recovery()

    high_probability = recovery[
        recovery["recovery_probability"] >= 0.70
    ]

    estimated_recovery = float(
        high_probability[
            "potential_recovery"
        ].sum()
    )

    return {

        "opportunities":
            int(
                len(high_probability)
            ),

        "estimated_recovery":
            round(
                estimated_recovery,
                2
            ),

        "total_failed_amount":
            round(
                float(
                    recovery["amount"].sum()
                ),
                2
            )
    }


# ============================================================
# TOOL 3: REVENUE FORECAST
# ============================================================

def get_revenue_forecast():

    forecast = cached_forecast()

    if forecast is None or len(forecast) == 0:

        return {

            "forecast_available":
                False,

            "average_daily_revenue":
                0.0
        }

    average_revenue = float(
        forecast[
            "predicted_revenue"
        ].mean()
    )

    total_forecast_revenue = float(
        forecast[
            "predicted_revenue"
        ].sum()
    )

    return {

        "forecast_available":
            True,

        "forecast_days":
            7,

        "average_daily_revenue":
            round(
                average_revenue,
                2
            ),

        "total_forecast_revenue":
            round(
                total_forecast_revenue,
                2
            )
    }


# ============================================================
# TOOL 4: ROOT CAUSE ANALYSIS
# ============================================================

def get_root_cause():

    result = cached_root_cause()

    return {

        "top_failure_reason":
            result.get(
                "top_failure_reason",
                "Unknown"
            ),

        "top_failure_percentage":
            round(
                float(
                    result.get(
                        "top_failure_percentage",
                        0
                    )
                ),
                2
            )
    }


# ============================================================
# INTENT DETECTION
# ============================================================

def detect_intent(question):

    question = question.lower().strip()


    # Recovery

    if any(
        word in question
        for word in [
            "recover",
            "recovery",
            "recoverable",
            "lost revenue",
            "failed payment",
            "failed payments"
        ]
    ):

        return "recovery"


    # Risk

    if any(
        word in question
        for word in [
            "risk",
            "failure",
            "failures",
            "problem",
            "issue",
            "payment problem"
        ]
    ):

        return "risk"


    # Revenue forecast

    if any(
        word in question
        for word in [
            "revenue forecast",
            "forecast",
            "future revenue",
            "predict revenue",
            "predicted revenue"
        ]
    ):

        return "forecast"


    # Root cause

    if any(
        word in question
        for word in [
            "why",
            "root cause",
            "reason",
            "failure reason",
            "why payments fail"
        ]
    ):

        return "root_cause"


    # General finance controller

    if any(
        word in question
        for word in [
            "today",
            "focus",
            "priority",
            "prioritize",
            "what should",
            "recommend",
            "recommendation",
            "what do",
            "action"
        ]
    ):

        return "general"


    return "general"


# ============================================================
# LOCAL AI RESPONSE GENERATOR
# ============================================================

def generate_response(
    question,
    intent,
    context
):

    # ========================================================
    # RECOVERY RESPONSE
    # ========================================================

    if intent == "recovery":

        recovery = context["recovery"]

        opportunities = recovery[
            "opportunities"
        ]

        estimated = recovery[
            "estimated_recovery"
        ]

        return (
            "INSIGHT:\n"
            f"RazorMind identified "
            f"{opportunities} high-probability "
            f"recovery opportunities.\n\n"

            "EVIDENCE:\n"
            f"The estimated potential recovery "
            f"is ₹{estimated:,.2f}.\n\n"

            "RECOMMENDED ACTION:\n"
            "Prioritize retry attempts for failed "
            "payments with recovery probability "
            "above 70%, starting with the "
            "highest-value transactions."
        )


    # ========================================================
    # RISK RESPONSE
    # ========================================================

    if intent == "risk":

        risk = context["risk"]

        failure_rate = risk[
            "failure_rate"
        ]

        failed = risk[
            "failed_transactions"
        ]

        reason = risk[
            "top_failure_reason"
        ]

        percentage = risk[
            "top_failure_percentage"
        ]

        anomalies = risk[
            "anomalies"
        ]

        return (
            "INSIGHT:\n"
            "RazorMind detected payment risk "
            "in the transaction system.\n\n"

            "EVIDENCE:\n"
            f"Failure rate: {failure_rate:.2f}%.\n"
            f"Failed transactions: {failed}.\n"
            f"Detected anomalous periods: "
            f"{anomalies}.\n"
            f"Dominant failure reason: {reason} "
            f"({percentage:.2f}% of failures).\n\n"

            "RECOMMENDED ACTION:\n"
            f"Investigate {reason} as the primary "
            "failure source and prioritize "
            "mitigation and retry strategies."
        )


    # ========================================================
    # FORECAST RESPONSE
    # ========================================================

    if intent == "forecast":

        forecast = context["forecast"]

        if not forecast[
            "forecast_available"
        ]:

            return (
                "INSIGHT:\n"
                "A revenue forecast could not "
                "be generated.\n\n"

                "EVIDENCE:\n"
                "There is insufficient transaction "
                "data available for forecasting.\n\n"

                "RECOMMENDED ACTION:\n"
                "Collect additional transaction "
                "history before making revenue "
                "planning decisions."
            )

        average = forecast[
            "average_daily_revenue"
        ]

        total = forecast[
            "total_forecast_revenue"
        ]

        return (
            "INSIGHT:\n"
            f"RazorMind predicts average daily "
            f"revenue of approximately "
            f"₹{average:,.2f} for the next "
            f"7 days.\n\n"

            "EVIDENCE:\n"
            f"Projected 7-day revenue: "
            f"₹{total:,.2f}.\n\n"

            "RECOMMENDED ACTION:\n"
            "Use the forecast for short-term "
            "cash-flow planning and compare "
            "actual revenue against predicted "
            "revenue to detect deviations."
        )


    # ========================================================
    # ROOT CAUSE RESPONSE
    # ========================================================

    if intent == "root_cause":

        root = context["root_cause"]

        reason = root[
            "top_failure_reason"
        ]

        percentage = root[
            "top_failure_percentage"
        ]

        return (
            "INSIGHT:\n"
            f"The dominant payment failure reason "
            f"is {reason}.\n\n"

            "EVIDENCE:\n"
            f"{reason} accounts for "
            f"{percentage:.2f}% of failed "
            "payments.\n\n"

            "RECOMMENDED ACTION:\n"
            f"Investigate the {reason} failure "
            "category and prioritize corrective "
            "measures to reduce payment failures."
        )


    # ========================================================
    # GENERAL FINANCE CONTROLLER
    # ========================================================

    recovery = context["recovery"]
    risk = context["risk"]
    forecast = context["forecast"]

    opportunities = recovery[
        "opportunities"
    ]

    estimated_recovery = recovery[
        "estimated_recovery"
    ]

    failure_rate = risk[
        "failure_rate"
    ]

    reason = risk[
        "top_failure_reason"
    ]

    percentage = risk[
        "top_failure_percentage"
    ]

    average_revenue = forecast[
        "average_daily_revenue"
    ]


    # Determine highest priority

    if estimated_recovery > 0:

        priority = "HIGH"

        action = (
            "Prioritize high-probability payment "
            "retries, starting with the highest-value "
            "transactions."
        )

        title = (
            "Revenue recovery is the immediate priority."
        )

    elif failure_rate > 0:

        priority = "HIGH"

        action = (
            f"Investigate {reason} and implement "
            "mitigation measures."
        )

        title = (
            "Payment failure risk requires attention."
        )

    else:

        priority = "MEDIUM"

        action = (
            "Continue monitoring payment "
            "performance and revenue trends."
        )

        title = (
            "Payment performance is currently stable."
        )


    return (
        f"PRIORITY: {priority}\n\n"

        "INSIGHT:\n"
        f"{title}\n\n"

        "EVIDENCE:\n"
        f"Potential recovery: "
        f"₹{estimated_recovery:,.2f}.\n"
        f"Recovery opportunities: "
        f"{opportunities}.\n"
        f"Failure rate: "
        f"{failure_rate:.2f}%.\n"
        f"Main failure reason: "
        f"{reason} ({percentage:.2f}%).\n"
        f"Average predicted daily revenue: "
        f"₹{average_revenue:,.2f}.\n\n"

        "RECOMMENDED ACTION:\n"
        f"{action}"
    )


# ============================================================
# MAIN AI CONTROLLER
# ============================================================

def ask_ai(question):

    if not question or not question.strip():

        return {

            "success":
                False,

            "error":
                "Question cannot be empty."
        }


    question = question.strip()

    intent = detect_intent(
        question
    )


    # ========================================================
    # RUN ONLY REQUIRED ANALYSIS
    # ========================================================

    context = {}


    if intent == "recovery":

        context["recovery"] = (
            get_recovery_opportunities()
        )


    elif intent == "risk":

        context["risk"] = (
            get_payment_risk()
        )


    elif intent == "forecast":

        context["forecast"] = (
            get_revenue_forecast()
        )


    elif intent == "root_cause":

        context["root_cause"] = (
            get_root_cause()
        )


    else:

        # General question requires
        # the complete financial picture.

        context["risk"] = (
            get_payment_risk()
        )

        context["recovery"] = (
            get_recovery_opportunities()
        )

        context["forecast"] = (
            get_revenue_forecast()
        )


    # ========================================================
    # GENERATE RESPONSE
    # ========================================================

    answer = generate_response(
        question,
        intent,
        context
    )


    return {

        "success":
            True,

        "question":
            question,

        "intent":
            intent,

        "answer":
            answer,

        "data":
            context
    }


# ============================================================
# TERMINAL TEST
# ============================================================

if __name__ == "__main__":

    print(
        "\n=========================================="
    )

    print(
        "        RAZORMIND AI FINANCE CONTROLLER"
    )

    print(
        "==========================================\n"
    )


    while True:

        question = input(
            "Ask RazorMind "
            "(type 'exit' to quit): "
        )


        if question.lower().strip() == "exit":

            print(
                "\nRazorMind stopped."
            )

            break


        try:

            result = ask_ai(
                question
            )


            if result["success"]:

                print(
                    "\n"
                    + result["answer"]
                )

                print(
                    "\n------------------------------------------\n"
                )

            else:

                print(
                    "\nERROR:",
                    result["error"]
                )


        except Exception as e:

            print(
                "\nERROR:",
                str(e)
            )