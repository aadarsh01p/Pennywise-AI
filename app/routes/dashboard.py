from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import get_current_user
from app.models.user import User
from app.models.transactions import Transaction

from app.services.finance_engine import (
    get_monthly_summary,
    get_category_spending,
    get_financial_health,
    get_monthly_expenses,
)

router = APIRouter(tags=["Dashboard"])


@router.get("/api/dashboard")
def get_dashboard(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    user_id = current_user.id

    # =====================================
    # Financial Intelligence
    # =====================================

    summary = get_monthly_summary(user_id, db)
    categories = get_category_spending(user_id, db)
    health = get_financial_health(user_id, db)
    monthly = get_monthly_expenses(user_id, db)
    # =====================================
    # Recent Transactions
    # =====================================

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .order_by(Transaction.date.desc())
        .all()
    )

    recent_transactions = [
        {
            "id": transaction.id,
            "date": str(transaction.date),
            "description": transaction.description,
            "amount": transaction.amount,
            "category": transaction.category,
            "type": transaction.transaction_type,
        }
        for transaction in transactions[:5]
    ]

    # =====================================
    # Dashboard Response
    # =====================================

    return {
        "user": {
            "username": current_user.username,
            "full_name": current_user.full_name,
        },
        "income": summary["income"],
        "expense": summary["expenses"],
        "savings": summary["savings"],
        "health": health["score"],
        "categories": categories,
        "monthly": monthly,
        "recent": recent_transactions,
    }
