from collections import defaultdict

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import get_current_user
from app.models.user import User
from app.models.transactions import Transaction

router = APIRouter(tags=["Dashboard"])


@router.get("/api/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    # =====================================
    # Get User Transactions
    # =====================================

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .order_by(Transaction.date)
        .all()
    )

    # =====================================
    # Summary Cards
    # =====================================

    income = sum(
        t.amount
        for t in transactions
        if str(t.transaction_type).strip().lower() == "income"
    )

    expense = sum(
        t.amount
        for t in transactions
        if str(t.transaction_type).strip().lower() == "expense"
    )

    savings = income - expense

    # =====================================
    # Financial Health Score
    # =====================================

    if income > 0:
        health = round((savings / income) * 100)
    else:
        health = 0

    health = max(0, min(100, health))

    # =====================================
    # Expense Categories
    # =====================================

    categories = defaultdict(float)

    for transaction in transactions:

        if str(transaction.transaction_type).strip().lower() == "expense":

            category = transaction.category or "Other"

            categories[category] += transaction.amount

    # =====================================
    # Monthly Expenses
    # =====================================

    monthly = defaultdict(float)

    for transaction in transactions:

        if str(transaction.transaction_type).strip().lower() == "expense":

            month = transaction.date.strftime("%b")

            monthly[month] += transaction.amount

    # =====================================
    # Keep Months Ordered
    # =====================================

    month_order = [
        "Jan",
        "Feb",
        "Mar",
        "Apr",
        "May",
        "Jun",
        "Jul",
        "Aug",
        "Sep",
        "Oct",
        "Nov",
        "Dec",
    ]

    monthly_data = []

    for month in month_order:

        monthly_data.append(
            {
                "month": month,
                "expense": monthly.get(month, 0),
            }
        )

    # =====================================
    # Recent Transactions
    # =====================================

    recent_transactions = []

    recent = sorted(
        transactions,
        key=lambda x: x.date,
        reverse=True,
    )[:5]

    for transaction in recent:

        recent_transactions.append(
            {
                "id": transaction.id,
                "date": str(transaction.date),
                "description": transaction.description,
                "amount": transaction.amount,
                "category": transaction.category,
                "type": transaction.transaction_type,
            }
        )

    # =====================================
    # Dashboard Response
    # =====================================

    return {
        "user": {
            "username": current_user.username,
            "full_name": current_user.full_name,
        },
        "income": income,
        "expense": expense,
        "savings": savings,
        "health": health,
        "categories": dict(categories),
        "monthly": monthly_data,
        "recent": recent_transactions,
    }