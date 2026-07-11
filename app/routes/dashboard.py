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
    db: Session = Depends(get_db)
):

    transactions = db.query(Transaction).filter(
        Transaction.user_id == current_user.id
    ).all()

    income = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Income"
    )

    expense = sum(
        t.amount
        for t in transactions
        if t.transaction_type == "Expense"
    )

    savings = income - expense

    health = 0

    if income > 0:
        health = round((savings / income) * 100)

    health = max(0, min(100, health))

    return {
        "user": {
            "username": current_user.username,
            "full_name": current_user.full_name
        },
        "income": income,
        "expense": expense,
        "savings": savings,
        "health": health
    }