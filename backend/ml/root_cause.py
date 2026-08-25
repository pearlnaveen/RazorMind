from database import engine
import pandas as pd


def analyze_failure_reasons():

    query = """
    SELECT
        failure_reason,
        COUNT(*) AS failures,
        SUM(amount) AS failed_amount
    FROM transactions
    WHERE status = 'failed'
    GROUP BY failure_reason
    ORDER BY failures DESC
    """

    df = pd.read_sql(query, engine)

    if df.empty:
        return {
            "message": "No failed transactions found."
        }

    total_failures = df["failures"].sum()

    df["percentage"] = (
        df["failures"] /
        total_failures
    ) * 100

    top_reason = df.iloc[0]

    return {
        "total_failed_transactions": int(
            total_failures
        ),

        "top_failure_reason":
            str(top_reason["failure_reason"]),

        "top_failure_percentage":
            round(
                float(top_reason["percentage"]),
                2
            ),

        "breakdown":
            df.to_dict(orient="records")
    }


if __name__ == "__main__":

    result = analyze_failure_reasons()

    print("\n========== FAILURE ROOT CAUSE ==========\n")

    print(
        "Top failure reason:",
        result["top_failure_reason"]
    )

    print(
        "Percentage:",
        result["top_failure_percentage"],
        "%"
    )

    print("\nBreakdown:")

    for row in result["breakdown"]:

        print(
            row["failure_reason"],
            "→",
            row["failures"],
            "failures"
        )