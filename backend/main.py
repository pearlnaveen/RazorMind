from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from sqlalchemy import func

from database import engine, Base, SessionLocal
from models import Transaction

from ml.anomaly_detection import detect_anomalies
from ml.revenue_prediction import predict_next_days
from ml.recovery_prediction import predict_recovery
from ml.impact import calculate_recovery_impact
from ml.recommendations import generate_recommendations
from ml.root_cause import analyze_failure_reasons
from ml.razormind_controller import get_razormind_insight
from datetime import datetime, timedelta

from ml.ai_agent import ask_ai
from ml.cache import clear_cache


# =========================================================
# FASTAPI APPLICATION
# =========================================================

app = FastAPI(
    title="RazorMind AI CFO API",
    description="AI-powered financial intelligence for merchants",
    version="1.0.0"
)


# =========================================================
# CORS
# =========================================================

app.add_middleware(
    CORSMiddleware,

    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000"
    ],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"],
)


# =========================================================
# DATABASE
# =========================================================

Base.metadata.create_all(bind=engine)


def get_db():

    db = SessionLocal()

    try:
        yield db

    finally:
        db.close()


# =========================================================
# HOME
# =========================================================

@app.get("/")
def home():

    return {
        "project": "RazorMind",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy",
        "service": "RazorMind API"
    }
# =========================================================
# ANALYTICS - OVERVIEW
# =========================================================

@app.get("/analytics/overview")
def overview(
    db: Session = Depends(get_db)
):

    total_transactions = (
        db.query(Transaction).count()
    )

    successful_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.status == "success"
        )
        .count()
    )

    failed_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.status == "failed"
        )
        .count()
    )

    refunded_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.status == "refunded"
        )
        .count()
    )

    total_revenue = (
        db.query(
            func.sum(Transaction.amount)
        )
        .filter(
            Transaction.status == "success"
        )
        .scalar()
    ) or 0

    failed_amount = (
        db.query(
            func.sum(Transaction.amount)
        )
        .filter(
            Transaction.status == "failed"
        )
        .scalar()
    ) or 0

    refunded_amount = (
        db.query(
            func.sum(Transaction.amount)
        )
        .filter(
            Transaction.status == "refunded"
        )
        .scalar()
    ) or 0

    success_rate = (

        successful_transactions
        / total_transactions
        * 100

        if total_transactions > 0
        else 0
    )

    return {

        "total_transactions":
            total_transactions,

        "successful_transactions":
            successful_transactions,

        "failed_transactions":
            failed_transactions,

        "refunded_transactions":
            refunded_transactions,

        "total_revenue":
            round(total_revenue, 2),

        "failed_amount":
            round(failed_amount, 2),

        "refunded_amount":
            round(refunded_amount, 2),

        "success_rate":
            round(success_rate, 2)
    }


# =========================================================
# ANALYTICS - REVENUE
# =========================================================

@app.get("/analytics/revenue")
def revenue_analytics(
    days: int = 30,
    db: Session = Depends(get_db)
):

    if days not in [7, 14, 30, 60, 90]:
        days = 30

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    revenue = (
        db.query(
            func.date(Transaction.created_at).label("date"),
            func.sum(Transaction.amount).label("revenue")
        )
        .filter(
            Transaction.status == "success",
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
        .group_by(
            func.date(Transaction.created_at)
        )
        .order_by(
            func.date(Transaction.created_at)
        )
        .all()
    )

    return [
        {
            "date": str(row.date),
            "revenue": round(
                float(row.revenue or 0),
                2
            )
        }
        for row in revenue
    ]


# =========================================================
# ANALYTICS - CUSTOMERS
# =========================================================

@app.get("/analytics/customers")
def customer_analytics(
    db: Session = Depends(get_db)
):

    customers = (

        db.query(

            Transaction.customer_id,

            func.count(
                Transaction.id
            ).label("transactions"),

            func.sum(
                Transaction.amount
            ).label("total_amount")
        )

        .filter(
            Transaction.status == "success"
        )

        .group_by(
            Transaction.customer_id
        )

        .order_by(
            func.sum(
                Transaction.amount
            ).desc()
        )

        .limit(10)

        .all()
    )

    return [

        {
            "customer_id":
                row.customer_id,

            "transactions":
                row.transactions,

            "total_spend":
                round(
                    row.total_amount,
                    2
                )
        }

        for row in customers
    ]


# =========================================================
# ANALYTICS - PAYMENT METHODS
# =========================================================

@app.get("/analytics/payment-methods")
def payment_methods(
    db: Session = Depends(get_db)
):

    methods = (

        db.query(

            Transaction.payment_method,

            func.count(
                Transaction.id
            ).label("transactions"),

            func.sum(
                Transaction.amount
            ).label("amount")
        )

        .filter(
            Transaction.status == "success"
        )

        .group_by(
            Transaction.payment_method
        )

        .all()
    )

    return [

        {
            "payment_method":
                row.payment_method,

            "transactions":
                row.transactions,

            "amount":
                round(
                    row.amount,
                    2
                )
        }

        for row in methods
    ]


# =========================================================
# ANALYTICS - ANOMALIES
# =========================================================

@app.get("/analytics/anomalies")
def financial_anomalies():

    result = detect_anomalies()

    anomalies = result[
        result["anomaly"] == "anomaly"
    ]

    output = []

    for _, row in anomalies.iterrows():

        output.append({

            "date":
                str(row["date"]),

            "total_transactions":
                int(
                    row["total_transactions"]
                ),

            "total_amount":
                round(
                    float(
                        row["total_amount"]
                    ),
                    2
                ),

            "failed_transactions":
                int(
                    row["failed_transactions"]
                ),

            "refunded_transactions":
                int(
                    row["refunded_transactions"]
                ),

            "failure_rate":
                round(
                    float(
                        row["failure_rate"] * 100
                    ),
                    2
                ),

            "message":
                (
                    "Unusual financial activity "
                    "detected."
                )
        })

    return {

        "anomalies_detected":
            len(output),

        "anomalies":
            output
    }


# =========================================================
# ANALYTICS - REVENUE FORECAST
# =========================================================

@app.get("/analytics/revenue-forecast")
def revenue_forecast():

    predictions = predict_next_days(7)

    
    return [

        {
            "date":
                str(
                    row["date"].date()
                ),

            "predicted_revenue":
                round(
                    float(
                        row["predicted_revenue"]
                    ),
                    2
                )
        }

        for _, row in predictions.iterrows()
    ]


# =========================================================
# ANALYTICS - RECOVERY OPPORTUNITIES
# =========================================================

@app.get("/analytics/recovery-opportunities")
def recovery_opportunities(days: int = 30):

    result = predict_recovery(days)

    top = result.head(20)

    return {

        "total_failed_amount":
            round(
                float(
                    result["amount"].sum()
                ),
                2
            ),

        "potential_recovery":
            round(
                float(
                    result[
                        "potential_recovery"
                    ].sum()
                ),
                2
            ),

       "opportunities": [

    {
        "transaction_id":
            row["transaction_id"],

        "customer_id":
            row["customer_id"],

        "amount":
            round(
                float(row["amount"]),
                2
            ),

        "payment_method":
            row["payment_method"],

        "failure_reason":
            row["failure_reason"],

        "recovery_probability":
            round(
                float(
                    row["recovery_probability"] * 100
                ),
                2
            ),

        "potential_recovery":
            round(
                float(
                    row["potential_recovery"]
                ),
                2
            ),

        "priority":
            row["priority"]
    }

    for _, row in top.iterrows()
]
    }


# =========================================================
# ANALYTICS - RECOVERY IMPACT
# =========================================================

@app.get("/analytics/recovery-impact")
def recovery_impact():

    return calculate_recovery_impact()


# =========================================================
# ANALYTICS - ROOT CAUSE
# =========================================================

@app.get("/analytics/root-cause")
def root_cause(
    days: int = 30,
    db: Session = Depends(get_db)
):

    if days not in [7, 14, 30, 60, 90]:
        days = 30

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    failed = (
        db.query(Transaction)
        .filter(
            Transaction.status == "failed",
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
        .all()
    )

    total_failed = len(failed)

    if total_failed == 0:

        return {
            "period_days": days,
            "total_failed_transactions": 0,
            "top_failure_reason": "None",
            "top_failure_percentage": 0,
            "breakdown": []
        }

    breakdown = {}

    for transaction in failed:

        reason = (
            transaction.failure_reason
            or "Unknown"
        )

        if reason not in breakdown:

            breakdown[reason] = {
                "failures": 0,
                "failed_amount": 0
            }

        breakdown[reason]["failures"] += 1

        breakdown[reason]["failed_amount"] += (
            float(transaction.amount or 0)
        )

    result = []

    for reason, values in breakdown.items():

        percentage = (
            values["failures"]
            / total_failed
            * 100
        )

        result.append({
            "failure_reason": reason,
            "failures": values["failures"],
            "failed_amount": round(
                values["failed_amount"],
                2
            ),
            "percentage": round(
                percentage,
                2
            )
        })

    result.sort(
        key=lambda x: x["failures"],
        reverse=True
    )

    top = result[0]

    return {

        "period_days": days,

        "total_failed_transactions":
            total_failed,

        "top_failure_reason":
            top["failure_reason"],

        "top_failure_percentage":
            top["percentage"],

        "breakdown":
            result
    }

# =========================================================
# AI - RECOMMENDATIONS
# =========================================================

@app.get("/ai/recommendations")
def ai_recommendations():

    return generate_recommendations()


# =========================================================
# AI - ASK RAZORMIND
# =========================================================

@app.get("/ai/ask")
def ask_razormind(question: str):

    result = ask_ai(question)

    print("RAZORMIND AI RESULT:")
    print(result)

    return result

# =========================================================
# AI - EXECUTIVE CONTROLLER
# =========================================================

@app.get("/ai/controller")
def razormind_controller(
    days: int = 30,
    db: Session = Depends(get_db)
):

    # Allowed periods
    if days not in [7, 14, 30, 60, 90]:
        days = 30

    # Date range
    end_date = datetime.now()

    start_date = (
        end_date - timedelta(days=days)
    )

    # =====================================================
    # BASIC TRANSACTION METRICS
    # =====================================================

    total_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date
        )
        .count()
    )

    failed_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date,
            Transaction.status == "failed"
        )
        .count()
    )

    successful_transactions = (
        db.query(Transaction)
        .filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date,
            Transaction.status == "success"
        )
        .count()
    )

    # =====================================================
    # FAILURE RATE
    # =====================================================

    failure_rate = (
        failed_transactions / total_transactions * 100
        if total_transactions > 0
        else 0
    )

    # =====================================================
    # REVENUE
    # =====================================================

    total_revenue = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date,
            Transaction.status == "success"
        )
        .scalar()
    ) or 0

    # =====================================================
    # FAILED AMOUNT
    # =====================================================

    failed_amount = (
        db.query(func.sum(Transaction.amount))
        .filter(
            Transaction.created_at >= start_date,
            Transaction.created_at <= end_date,
            Transaction.status == "failed"
        )
        .scalar()
    ) or 0

    # =====================================================
    # RETURN DASHBOARD
    # =====================================================

    return {

        "status": "success",

        "period": {
            "days": days,
            "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat()
        },

        "priority": (
            "HIGH"
            if failure_rate >= 5
            else "MEDIUM"
        ),

        "title": (
            "Prioritize revenue recovery"
            if failure_rate >= 5
            else "Monitor payment performance"
        ),

        "payment_risk": {

            "failure_rate": round(
                failure_rate,
                2
            ),

            "failed_transactions":
                failed_transactions,

            "successful_transactions":
                successful_transactions
        },

        "recovery": {

            "opportunities":
                failed_transactions,

            "potential_recovery":
                round(
                    float(failed_amount),
                    2
                )
        },

        "forecast": {

            "average_daily_revenue":
                round(
                    float(total_revenue) / days,
                    2
                )
        },

        "recommended_action": (
            "Prioritize high-probability "
            "failed payment retries."
            if failure_rate >= 5
            else
            "Continue monitoring payment performance."
        )
    }

# =========================================================
# AI - REFRESH
# =========================================================

@app.post("/ai/refresh")
def refresh_ai():

    clear_cache()

    return {

        "success":
            True,

        "message":
            "RazorMind analysis cache cleared."
    }