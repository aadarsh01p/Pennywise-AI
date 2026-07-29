from collections import defaultdict

from sqlalchemy.orm import Session

from app.models.goal import Goal
from app.models.transactions import Transaction


PRIORITY_ORDER = {
    "High": 0,
    "Medium": 1,
    "Low": 2
}


def _monthly_summary(user_id, db):

    monthly_income = defaultdict(float)
    monthly_expense = defaultdict(float)

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )

    for t in transactions:

        month = t.date.strftime("%Y-%m")

        if t.transaction_type == "Income":
            monthly_income[month] += t.amount

        elif t.transaction_type == "Expense":
            monthly_expense[month] += t.amount

    months = max(len(monthly_income), 1)

    avg_income = sum(monthly_income.values()) / months
    avg_expense = sum(monthly_expense.values()) / months

    avg_savings = max(
        0,
        avg_income - avg_expense
    )

    return round(avg_savings, 2)

def get_goals(user_id, db):

    goals = (
        db.query(Goal)
        .filter(Goal.user_id == user_id)
        .all()
    )

    average_monthly_savings = _monthly_summary(
        user_id,
        db
    )

    goals.sort(
        key=lambda g: (
            PRIORITY_ORDER.get(g.priority, 1),
            g.duration_months
        )
    )

    remaining_pool = average_monthly_savings

    data = []

    for goal in goals:

        required = round(
            goal.target_amount /
            goal.duration_months,
            2
        )

        allocated = min(
            required,
            remaining_pool
        )

        remaining_pool -= allocated

        progress = (
            allocated / required * 100
            if required else 100
        )

        if allocated >= required:

            status = "On Schedule"

        elif allocated >= required * 0.70:

            status = "Slight Delay"

        else:

            status = "Delayed"

        estimated = (
            round(goal.target_amount / allocated, 1)
            if allocated else None
        )

        data.append({

            "id": goal.id,

            "goal_name": goal.goal_name,

            "target_amount": goal.target_amount,

            "priority": goal.priority,

            "duration_months": goal.duration_months,

            "required_per_month": required,

            "allocated_per_month": allocated,

            "progress": round(progress, 1),

            "estimated_completion": estimated,

            "status": status

        })

    return {
        "average_monthly_savings": average_monthly_savings,
        "available_savings": round(remaining_pool, 2),
        "goals": data
    }

def create_goal(user_id, goal, db):

    db.add(

        Goal(

            user_id=user_id,

            goal_name=goal.goal_name,

            target_amount=goal.target_amount,

            duration_months=goal.duration_months,

            priority=goal.priority

        )

    )

    db.commit()

    return get_goals(user_id, db)

def update_goal(user_id, goal_id, goal, db):

    existing = (

        db.query(Goal)

        .filter(

            Goal.id == goal_id,

            Goal.user_id == user_id

        )

        .first()

    )

    if not existing:

        return None

    existing.goal_name = goal.goal_name
    existing.target_amount = goal.target_amount
    existing.duration_months = goal.duration_months
    existing.priority = goal.priority

    db.commit()

    return get_goals(user_id, db)

def delete_goal(user_id, goal_id, db):

    (

        db.query(Goal)

        .filter(

            Goal.id == goal_id,

            Goal.user_id == user_id

        )

        .delete()

    )

    db.commit()

    return get_goals(user_id, db)