import pandas as pd

from database import engine, Base
from models import Transaction


Base.metadata.create_all(bind=engine)

df = pd.read_csv("../data/transactions.csv")

df["created_at"] = pd.to_datetime(df["created_at"])

df.to_sql(
    "transactions",
    engine,
    if_exists="append",
    index=False
)

print("Data loaded successfully!")