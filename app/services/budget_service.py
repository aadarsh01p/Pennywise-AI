from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.transactions import Transaction
from app.models.budget import Budget

from app.services.ai_service import generate_budget

def get_budget_summary(user_id: int, db: Session):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    monthly_income = defaultdict(float)
    monthly_expense = defaultdict(float)
    category_expense = defaultdict(float)

    for t in transactions:

        month = t.date.strftime("%Y-%m")

        if t.transaction_type == "Income":
            monthly_income[month] += t.amount

        elif t.transaction_type == "Expense":

            if t.category == "Investment":
                continue

            monthly_expense[month] += t.amount
            category_expense[t.category] += t.amount
    months = max(len(monthly_income), 1)

    average_income = round(sum(monthly_income.values()) / months, 2)
    average_expense = round(sum(monthly_expense.values()) / months, 2)

    health = (
        max(
            0,
            min(
                100,
                round(((average_income - average_expense) / average_income) * 100)
            )
        )
        if average_income else 0
    )

    average_category_expense = {
        c: round(a / months, 2)
        for c, a in category_expense.items()
    }

    budget_lookup = {
        b.category: b.budget_amount
        for b in db.query(Budget).filter(Budget.user_id == user_id).all()
    }

    categories = []

    for category, avg in average_category_expense.items():

        budget = budget_lookup.get(category, 0)
        diff = round(budget - avg, 2)
        FIXED_CATEGORIES = {
            "Rent",
            "Bills"
        }

        if category in FIXED_CATEGORIES:

            status = "Fixed"

        elif avg == 0:

            status = "Good"

        elif abs(diff) <= avg * 0.10:

            status = "On Track"

        elif diff > 0:

            status = "Good"

        else:

            status = "Reduce"

        categories.append({
            "category": category,
            "average_spend": avg,
            "budget": budget,
            "difference": diff,
            "status": status
        })

    return {
        "average_income": average_income,
        "average_expense": average_expense,
        "months": months,
        "health": health,
        "category_expense": average_category_expense,
        "has_budget": bool(budget_lookup),
        "categories": sorted(categories, key=lambda x: x["category"])
    }

def generate_ai_budget(user_id: int, db: Session):

    summary = get_budget_summary(user_id, db)

    budgets = generate_budget(
        summary["average_income"],
        summary["average_expense"],
        summary["category_expense"],
        summary["health"]
    )

    if not budgets:
        return {"message": "Budget generation failed."}

    db.query(Budget).filter(Budget.user_id == user_id).delete()

    db.add_all(
        Budget(
            user_id=user_id,
            category=category,
            budget_amount=float(amount)
        )
        for category, amount in budgets.items()
    )

    db.commit()

    return get_budget_summary(user_id, db)

def save_budget(user_id: int, data, db: Session):

    budget = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id,
            Budget.category == data.category
        )
        .first()
    )

    if budget:
        budget.budget_amount = data.budget_amount
    else:
        db.add(
            Budget(
                user_id=user_id,
                category=data.category,
                budget_amount=data.budget_amount
            )
        )

    db.commit()