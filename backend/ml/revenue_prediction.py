import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from database import engine


def load_data():

    query = """
    SELECT amount, status, created_at
    FROM transactions
    """

    df = pd.read_sql(query, engine)

    df["created_at"] = pd.to_datetime(df["created_at"])

    return df


def prepare_data(df):

    # Only successful payments count as revenue
    success = df[df["status"] == "success"].copy()

    success["date"] = success["created_at"].dt.date

    daily = (
        success.groupby("date")["amount"]
        .sum()
        .reset_index()
    )

    daily["date"] = pd.to_datetime(daily["date"])

    daily = daily.sort_values("date")

    # Time-based features
    daily["day_number"] = range(len(daily))

    daily["day_of_week"] = daily["date"].dt.dayofweek

    daily["month"] = daily["date"].dt.month

    return daily


def train_model():

    df = load_data()

    daily = prepare_data(df)

    if len(daily) < 10:
        raise ValueError(
            "Not enough daily data to train the model."
        )

    features = [
        "day_number",
        "day_of_week",
        "month"
    ]

    X = daily[features]

    y = daily["amount"]

    model = RandomForestRegressor(
        n_estimators=200,
        random_state=42
    )

    model.fit(X, y)

    return model, daily


def predict_next_days(days=7):

    model, daily = train_model()

    last_day = daily["date"].max()

    future_dates = pd.date_range(
        start=last_day + pd.Timedelta(days=1),
        periods=days
    )

    future = pd.DataFrame()

    future["date"] = future_dates

    future["day_number"] = range(
        len(daily),
        len(daily) + days
    )

    future["day_of_week"] = future["date"].dt.dayofweek

    future["month"] = future["date"].dt.month

    features = [
        "day_number",
        "day_of_week",
        "month"
    ]

    predictions = model.predict(
        future[features]
    )

    future["predicted_revenue"] = predictions

    return future


if __name__ == "__main__":

    predictions = predict_next_days(7)

    print("\nRevenue Forecast\n")

    for _, row in predictions.iterrows():

        print(
            f"{row['date'].date()} : "
            f"₹{row['predicted_revenue']:,.2f}"
        )