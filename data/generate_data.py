import pandas as pd
import numpy as np
from datetime import datetime, timedelta

np.random.seed(42)

n = 5000

payment_methods = ["upi", "card", "netbanking", "wallet"]

statuses = np.random.choice(
    ["success", "failed", "refunded"],
    size=n,
    p=[0.82, 0.14, 0.04]
)

amounts = np.random.randint(200, 15000, n)

customers = [
    f"C{np.random.randint(1, 1001):04d}"
    for _ in range(n)
]

methods = np.random.choice(
    payment_methods,
    size=n,
    p=[0.55, 0.30, 0.10, 0.05]
)

failure_reasons = [
    "insufficient_funds",
    "bank_declined",
    "network_error",
    "invalid_card"
]

reasons = []

for status in statuses:
    if status == "failed":
        reasons.append(np.random.choice(failure_reasons))
    else:
        reasons.append("")

dates = [
    datetime(2026, 7, 1) +
    timedelta(
        minutes=np.random.randint(0, 60 * 24 * 60)
    )
    for _ in range(n)
]

df = pd.DataFrame({
    "transaction_id": [f"TXN{i:05d}" for i in range(1, n + 1)],
    "customer_id": customers,
    "amount": amounts,
    "payment_method": methods,
    "status": statuses,
    "failure_reason": reasons,
    "created_at": dates
})

df.to_csv("transactions.csv", index=False)

print("Generated:", len(df), "transactions")
print(df.head())