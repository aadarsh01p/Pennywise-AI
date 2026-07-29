from collections import defaultdict
from datetime import date

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.transactions import Transaction
from app.models.budget import Budget

def get_monthly_summary(user_id: int, db: Session):
    today = date.today()
    start_date = today.replace(day=1)

    income = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "Income",
            Transaction.date >= start_date,
            Transaction.date <= today,
        )
        .scalar()
    )

    expenses = (
        db.query(func.coalesce(func.sum(Transaction.amount), 0))
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "Expense",
            Transaction.date >= start_date,
            Transaction.date <= today,
        )
        .scalar()
    )

    savings = income - expenses
    savings_rate = (savings / income * 100) if income else 0

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "savings": round(savings, 2),
        "savings_rate": round(savings_rate, 2),
    }

def get_category_spending(user_id: int, db: Session):
    today = date.today()
    start_date = today.replace(day=1)

    results = (
        db.query(
            Transaction.category,
            func.sum(Transaction.amount).label("total"),
        )
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "Expense",
            Transaction.date >= start_date,
            Transaction.date <= today,
        )
        .group_by(Transaction.category)
        .all()
    )

    return {
        category or "Other": round(total, 2)
        for category, total in results
    }

def get_budget_status(user_id: int, db: Session):
    spending = get_category_spending(user_id, db)

    budgets = (
        db.query(Budget)
        .filter(Budget.user_id == user_id)
        .all()
    )

    return [
        {
            "category": budget.category,
            "budget": round(budget.budget_amount, 2),
            "spent": round(spending.get(budget.category, 0), 2),
            "remaining": round(
                budget.budget_amount - spending.get(
                    budget.category, 0
                ),
                2,
            ),
        }
        for budget in budgets
    ]

def get_financial_health(user_id: int, db: Session):
    summary = get_monthly_summary(user_id, db)

    score = 50

    if summary["savings_rate"] >= 20:
        score += 30
    elif summary["savings_rate"] >= 10:
        score += 20
    elif summary["savings_rate"] > 0:
        score += 10
    else:
        score -= 20

    score = max(0, min(score, 100))

    return {
        "score": score,
        "savings_rate": summary["savings_rate"],
    }

def get_monthly_expenses(user_id: int, db: Session):
    today = date.today()
    current_year = today.year

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id,
            Transaction.transaction_type == "Expense",
        )
        .all()
    )

    monthly = defaultdict(float)

    for transaction in transactions:
        if transaction.date.year == current_year:
            month = transaction.date.strftime("%b")
            monthly[month] += transaction.amount

    month_order = [
        "Jan", "Feb", "Mar", "Apr",
        "May", "Jun", "Jul", "Aug",
        "Sep", "Oct", "Nov", "Dec"
    ]

    return [
        {
            "month": month,
            "expense": round(monthly.get(month, 0), 2),
        }
        for month in month_order
    ]

def get_financial_context(user_id: int, db: Session):
    return {
        "summary": get_monthly_summary(user_id, db),
        "category_spending": get_category_spending(user_id, db),
        "budget_status": get_budget_status(user_id, db),
        "financial_health": get_financial_health(user_id, db),
    }