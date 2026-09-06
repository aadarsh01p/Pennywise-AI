from collections import defaultdict
from datetime import date, timedelta

from sqlalchemy.orm import Session

from app.models.transactions import Transaction
from app.models.budget import Budget


# =====================================
# Helper: Get Date Range
# =====================================

def get_date_range(period: str):

    today = date.today()

    # Current month
    if period == "current_month":

        start_date = today.replace(day=1)

        return start_date, today

    # Last month
    if period == "last_month":

        first_day_current_month = today.replace(day=1)

        last_day_previous_month = (
            first_day_current_month
            - timedelta(days=1)
        )

        first_day_previous_month = (
            last_day_previous_month.replace(day=1)
        )

        return (
            first_day_previous_month,
            last_day_previous_month
        )

    # All time
    return None, None


# =====================================
# Helper: Get User Transactions
# =====================================

def get_user_transactions(
    user_id: int,
    db: Session,
    period: str = "current_month",
    start_date=None,
    end_date=None
):

    query = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id
        )
    )

    # Custom date range takes priority
    if start_date is not None:

        query = query.filter(
            Transaction.date >= start_date
        )

    if end_date is not None:

        query = query.filter(
            Transaction.date <= end_date
        )

    # If custom dates are not provided,
    # use the normal period
    if start_date is None and end_date is None:

        period_start, period_end = (
            get_date_range(period)
        )

        if period_start is not None:

            query = query.filter(
                Transaction.date >= period_start
            )

        if period_end is not None:

            query = query.filter(
                Transaction.date <= period_end
            )

    return query.all()


# =====================================
# Financial Summary
# =====================================

def get_financial_summary(
    user_id: int,
    db: Session,
    period: str = "current_month",
    start_date=None,
    end_date=None
):

    transactions = get_user_transactions(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    income = sum(
        transaction.amount
        for transaction in transactions
        if str(
            transaction.transaction_type
        ).strip().lower() == "income"
    )

    expenses = sum(
        transaction.amount
        for transaction in transactions
        if str(
            transaction.transaction_type
        ).strip().lower() == "expense"
    )

    savings = income - expenses

    savings_rate = (
        savings / income * 100
        if income > 0
        else 0
    )

    return {
        "income": round(income, 2),
        "expenses": round(expenses, 2),
        "savings": round(savings, 2),
        "savings_rate": round(
            savings_rate,
            2
        ),
    }


# =====================================
# Category Spending
# =====================================

def get_category_spending(
    user_id: int,
    db: Session,
    period: str = "current_month",
    start_date=None,
    end_date=None
):

    transactions = get_user_transactions(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    categories = defaultdict(float)

    for transaction in transactions:

        transaction_type = (
            str(
                transaction.transaction_type
            )
            .strip()
            .lower()
        )

        if transaction_type == "expense":

            category = (
                transaction.category
                or "Other"
            )

            categories[category] += (
                transaction.amount
            )

    return {
        category: round(amount, 2)
        for category, amount
        in categories.items()
    }


# =====================================
# Budget Status
# =====================================

def get_budget_status(
    user_id: int,
    db: Session,
    period: str = "current_month",
    start_date=None,
    end_date=None
):

    spending = get_category_spending(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    budgets = (
        db.query(Budget)
        .filter(
            Budget.user_id == user_id
        )
        .all()
    )

    result = []

    for budget in budgets:

        spent = spending.get(
            budget.category,
            0
        )

        result.append({
            "category": budget.category,

            "budget": round(
                budget.budget_amount,
                2
            ),

            "spent": round(
                spent,
                2
            ),

            "remaining": round(
                budget.budget_amount - spent,
                2
            ),
        })

    return result


# =====================================
# Financial Health
# =====================================

def get_financial_health(
    user_id: int,
    db: Session,
    period: str = "current_month",
    start_date=None,
    end_date=None
):

    summary = get_financial_summary(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    score = 50

    if summary["savings_rate"] >= 20:

        score += 30

    elif summary["savings_rate"] >= 10:

        score += 20

    elif summary["savings_rate"] > 0:

        score += 10

    else:

        score -= 20

    score = max(
        0,
        min(score, 100)
    )

    return {
        "score": score,
        "savings_rate":
            summary["savings_rate"],
    }


# =====================================
# Monthly Expenses Chart
# =====================================

def get_monthly_expenses(
    user_id: int,
    db: Session
):

    today = date.today()
    current_year = today.year

    transactions = (
        db.query(Transaction)
        .filter(
            Transaction.user_id == user_id
        )
        .all()
    )

    monthly = defaultdict(float)

    for transaction in transactions:

        transaction_type = (
            str(
                transaction.transaction_type
            )
            .strip()
            .lower()
        )

        if (
            transaction_type == "expense"
            and transaction.date.year
            == current_year
        ):

            month = (
                transaction.date
                .strftime("%b")
            )

            monthly[month] += (
                transaction.amount
            )

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
        "Dec"
    ]

    return [
        {
            "month": month,

            "expense": round(
                monthly.get(
                    month,
                    0
                ),
                2
            ),
        }

        for month in month_order
    ]


# =====================================
# Complete Financial Context
# =====================================

def get_financial_context(
    user_id: int,
    db: Session,
    period: str = "current_month",
    start_date=None,
    end_date=None
):

    summary = get_financial_summary(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    categories = get_category_spending(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    budgets = get_budget_status(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    health = get_financial_health(
        user_id=user_id,
        db=db,
        period=period,
        start_date=start_date,
        end_date=end_date
    )

    return {
        "period": period,
        "summary": summary,
        "category_spending": categories,
        "budget_status": budgets,
        "financial_health": health,
    }