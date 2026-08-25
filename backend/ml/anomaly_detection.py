import pandas as pd
from sklearn.ensemble import IsolationForest
from database import engine


def load_transactions():

    query = """
    SELECT
        amount,
        status,
        payment_method,
        created_at
    FROM transactions
    """

    return pd.read_sql(query, engine)


def prepare_daily_data(df):

    df["created_at"] = pd.to_datetime(df["created_at"])

    df["date"] = df["created_at"].dt.date

    daily = df.groupby("date").agg(
        total_transactions=("amount", "count"),
        total_amount=("amount", "sum"),
        successful_transactions=(
            "status",
            lambda x: (x == "success").sum()
        ),
        failed_transactions=(
            "status",
            lambda x: (x == "failed").sum()
        ),
        refunded_transactions=(
            "status",
            lambda x: (x == "refunded").sum()
        )
    ).reset_index()

    daily["failure_rate"] = (
        daily["failed_transactions"]
        / daily["total_transactions"]
    )

    daily["success_rate"] = (
        daily["successful_transactions"]
        / daily["total_transactions"]
    )

    return daily


def detect_anomalies():

    df = load_transactions()

    daily = prepare_daily_data(df)

    features = [
        "total_transactions",
        "total_amount",
        "failed_transactions",
        "refunded_transactions",
        "failure_rate"
    ]

    model = IsolationForest(
        contamination=0.10,
        random_state=42
    )

    daily["anomaly"] = model.fit_predict(
        daily[features]
    )

    daily["anomaly"] = daily["anomaly"].map({
        1: "normal",
        -1: "anomaly"
    })

    return daily


if __name__ == "__main__":

    result = detect_anomalies()

    print("\nFinancial Anomaly Detection\n")
    print(result.to_string(index=False))

    print("\nDetected anomalies:\n")

    print(
        result[
            result["anomaly"] == "anomaly"
        ].to_string(index=False)
    )