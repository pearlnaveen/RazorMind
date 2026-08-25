import pandas as pd

from sklearn.ensemble import RandomForestClassifier

from database import engine


# =========================================================
# LOAD DATA
# =========================================================

def load_data(days=None):

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
    if days is not None:
        latest_date = df["created_at"].max()

        start_date = (
            latest_date
            - pd.Timedelta(days=days)
        )

        df = df[
            df["created_at"] >= start_date
        ].copy()

    df = df.sort_values(
        ["customer_id", "created_at"]
    ).reset_index(drop=True)

    return df


# =========================================================
# CREATE FEATURES
# =========================================================

def create_features(df):

    data = df.copy()

    # -----------------------------------------------------
    # Previous transaction count
    # -----------------------------------------------------

    data["previous_transactions"] = (
        data.groupby("customer_id")
        .cumcount()
    )


    # -----------------------------------------------------
    # Previous successful transactions
    # -----------------------------------------------------

    data["previous_successes"] = (

        data["status"]
        .eq("success")
        .astype(int)

        .groupby(
            data["customer_id"]
        )

        .cumsum()

        .shift(1)

        .fillna(0)
    )


    # -----------------------------------------------------
    # Previous success rate
    # -----------------------------------------------------

    data["previous_success_rate"] = 0.0

    mask = (
        data["previous_transactions"] > 0
    )

    data.loc[mask, "previous_success_rate"] = (

        data.loc[
            mask,
            "previous_successes"
        ]

        /

        data.loc[
            mask,
            "previous_transactions"
        ]
    )


    # -----------------------------------------------------
    # Recovery target
    #
    # A failed transaction is considered recovered
    # if the same customer has a successful transaction
    # within the following 7 days.
    # -----------------------------------------------------

    successful = data[
        data["status"] == "success"
    ][
        [
            "customer_id",
            "created_at"
        ]
    ].copy()


    successful = successful.rename(
        columns={
            "created_at":
                "success_time"
        }
    )


    # -----------------------------------------------------
    # Efficient recovery calculation
    # -----------------------------------------------------

    data["recovered"] = 0


    for customer_id, group in successful.groupby(
        "customer_id"
    ):

        success_times = (
            group["success_time"]
            .sort_values()
            .tolist()
        )

        failed_indices = data.index[
            (data["customer_id"] == customer_id) &
            (data["status"] == "failed")
        ]

        for index in failed_indices:

            transaction_time = (
                data.loc[
                    index,
                    "created_at"
                ]
            )

            future_limit = (
                transaction_time
                + pd.Timedelta(days=7)
            )

            recovered = any(
                transaction_time < success_time
                <= future_limit
                for success_time
                in success_times
            )

            if recovered:

                data.loc[
                    index,
                    "recovered"
                ] = 1


    return data


# =========================================================
# TRAIN MODEL
# =========================================================
def train_model(days=None):

    df = load_data(days)

    failed = df[
        df["status"] == "failed"
    ].copy()


    if len(failed) < 20:

        raise ValueError(
            "Not enough failed transactions "
            "to train recovery model."
        )


    dataset = create_features(df)


    dataset = dataset[
        dataset["status"] == "failed"
    ].copy()


    # -----------------------------------------------------
    # Select model features
    # -----------------------------------------------------

    dataset = pd.get_dummies(

        dataset,

        columns=[
            "payment_method",
            "failure_reason"
        ],

        dtype=int
    )


    X = dataset.drop(

        columns=[
            "transaction_id",
            "customer_id",
            "status",
            "created_at",
            "previous_successes",
            "recovered"
        ],

        errors="ignore"
    )


    y = dataset["recovered"]


    # -----------------------------------------------------
    # Model
    # -----------------------------------------------------

    model = RandomForestClassifier(

        n_estimators=100,

        random_state=42,

        class_weight="balanced",

        n_jobs=-1
    )


    model.fit(
        X,
        y
    )


    return model, X.columns


# =========================================================
# PREDICTION
# =========================================================

def predict_recovery(days=None):

    df = load_data(days)


    failed = df[
        df["status"] == "failed"
    ].copy()


    if len(failed) == 0:

        return pd.DataFrame(
            columns=[
                "transaction_id",
                "customer_id",
                "amount",
                "payment_method",
                "failure_reason",
                "recovery_probability",
                "potential_recovery"
            ]
        )


    model, training_columns = (
        train_model(days)
    )


    dataset = create_features(df)


    dataset = dataset[
        dataset["status"] == "failed"
    ].copy()


    transaction_ids = (
        dataset["transaction_id"]
    )


    # -----------------------------------------------------
    # Encode categorical columns
    # -----------------------------------------------------

    dataset = pd.get_dummies(

        dataset,

        columns=[
            "payment_method",
            "failure_reason"
        ],

        dtype=int
    )


    # -----------------------------------------------------
    # Prepare prediction features
    # -----------------------------------------------------

    dataset = dataset.drop(

        columns=[
            "transaction_id",
            "customer_id",
            "status",
            "created_at",
            "previous_successes",
            "recovered"
        ],

        errors="ignore"
    )


    # -----------------------------------------------------
    # Match training columns
    # -----------------------------------------------------

    dataset = dataset.reindex(

        columns=training_columns,

        fill_value=0
    )


    # -----------------------------------------------------
    # Predict
    # -----------------------------------------------------

    probabilities = (

        model
        .predict_proba(dataset)[:, 1]
    )


    # -----------------------------------------------------
    # Result
    # -----------------------------------------------------

    result = failed[
        [
            "transaction_id",
            "customer_id",
            "amount",
            "payment_method",
            "failure_reason"
        ]
    ].copy()


    result["recovery_probability"] = (
        probabilities
    )


    result["potential_recovery"] = (

        result["amount"]

        *

        result["recovery_probability"]
    )

    # =====================================================
# PRIORITY ENGINE
# =====================================================

    def calculate_priority(row):

        probability = row["recovery_probability"]
        potential = row["potential_recovery"]

        if probability >= 0.80 and potential >= 5000:
            return "HIGH"

        elif probability >= 0.60 and potential >= 2000:
            return "MEDIUM"

        else:
            return "LOW"


    result["priority"] = result.apply(
        calculate_priority,
        axis=1
    )
    result = result.sort_values(

        "recovery_probability",

        ascending=False
    )


    return result


# =========================================================
# TEST
# =========================================================

if __name__ == "__main__":

    print(
        "\n========== RECOVERY MODEL ==========\n"
    )

    result = predict_recovery()

    if result.empty:

        print("No failed transactions found.")

    else:

        print(
            result.head(20).to_string(
                index=False
            )
        )

        print(
            "\nTotal failed amount: "
            f"₹{result['amount'].sum():,.2f}"
        )

        print(
            "Total potential recovery: "
            f"₹{result['potential_recovery'].sum():,.2f}"
        )