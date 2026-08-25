import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import (
    accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score
)

from database import engine


def load_data():

    query = """
    SELECT
        transaction_id,
        customer_id,
        amount,
        payment_method,
        status,
        failure_reason,
        created_at
    FROM transactions
    """

    df = pd.read_sql(query, engine)

    df["created_at"] = pd.to_datetime(
        df["created_at"]
    )

    return df.sort_values(
        ["customer_id", "created_at"]
    )


def create_dataset(df):

    failed = df[
        df["status"] == "failed"
    ].copy()

    records = []

    for _, row in failed.iterrows():

        history = df[
            (df["customer_id"] == row["customer_id"]) &
            (df["created_at"] < row["created_at"])
        ]

        previous_transactions = len(history)

        previous_successes = (
            history["status"] == "success"
        ).sum()

        if previous_transactions > 0:

            success_rate = (
                previous_successes /
                previous_transactions
            )

        else:

            success_rate = 0.0

        future = df[
            (df["customer_id"] == row["customer_id"]) &
            (df["created_at"] > row["created_at"]) &
            (
                df["created_at"]
                <= row["created_at"]
                + pd.Timedelta(days=7)
            )
        ]

        recovered = int(
            (
                future["status"] == "success"
            ).any()
        )

        records.append({

            "amount": row["amount"],

            "previous_transactions":
                previous_transactions,

            "previous_success_rate":
                success_rate,

            "payment_method":
                row["payment_method"],

            "failure_reason":
                row["failure_reason"],

            "recovered":
                recovered
        })

    return pd.DataFrame(records)


def evaluate_recovery_model():

    df = load_data()

    dataset = create_dataset(df)

    if len(dataset) < 20:

        raise ValueError(
            "Not enough failed transactions "
            "for evaluation."
        )

    dataset = pd.get_dummies(
        dataset,
        columns=[
            "payment_method",
            "failure_reason"
        ],
        dtype=int
    )

    X = dataset.drop(
        columns=["recovered"]
    )

    y = dataset["recovered"]

    X_train, X_test, y_train, y_test = train_test_split(
        X,
        y,
        test_size=0.2,
        random_state=42,
        stratify=y
    )

    model = RandomForestClassifier(
        n_estimators=200,
        random_state=42,
        class_weight="balanced"
    )

    model.fit(
        X_train,
        y_train
    )

    predictions = model.predict(
        X_test
    )

    probabilities = model.predict_proba(
        X_test
    )[:, 1]

    accuracy = accuracy_score(
        y_test,
        predictions
    )

    precision = precision_score(
        y_test,
        predictions,
        zero_division=0
    )

    recall = recall_score(
        y_test,
        predictions,
        zero_division=0
    )

    f1 = f1_score(
        y_test,
        predictions,
        zero_division=0
    )

    # ROC-AUC requires both classes
    if len(y_test.unique()) == 2:

        roc_auc = roc_auc_score(
            y_test,
            probabilities
        )

    else:

        roc_auc = None

    return {
        "accuracy": round(
            accuracy, 4
        ),

        "precision": round(
            precision, 4
        ),

        "recall": round(
            recall, 4
        ),

        "f1_score": round(
            f1, 4
        ),

        "roc_auc": (
            round(roc_auc, 4)
            if roc_auc is not None
            else None
        )
    }


if __name__ == "__main__":

    metrics = evaluate_recovery_model()

    print("\nRecovery Prediction Model Evaluation\n")

    for name, value in metrics.items():

        print(
            f"{name}: {value}"
        )