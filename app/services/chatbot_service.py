import re

from calendar import monthrange
from datetime import date

from google import genai
from sqlalchemy.orm import Session

from app.config import GEMINI_API_KEY, GEMINI_MODELS
from app.services.finance_engine import get_financial_context


# =====================================
# Gemini Client
# =====================================

client = genai.Client(
    api_key=GEMINI_API_KEY
)


# =====================================
# Detect Custom Date Range
# =====================================

def detect_custom_date_range(question: str):

    question = question.lower().strip()

    months = {
        "january": 1,
        "february": 2,
        "march": 3,
        "april": 4,
        "may": 5,
        "june": 6,
        "july": 7,
        "august": 8,
        "september": 9,
        "october": 10,
        "november": 11,
        "december": 12,
    }

    # =====================================
    # DD/MM/YYYY or DD-MM-YYYY
    # =====================================

    date_match = re.search(
        r"\b(\d{1,2})[/-](\d{1,2})[/-](20\d{2})\b",
        question
    )

    if date_match:

        day = int(date_match.group(1))
        month = int(date_match.group(2))
        year = int(date_match.group(3))

        try:

            selected_date = date(
                year,
                month,
                day
            )

            return {
                "start_date": selected_date,
                "end_date": selected_date,
                "label": selected_date.strftime(
                    "%d %B %Y"
                ),
            }

        except ValueError:
            return None


    # =====================================
    # Month Name Detection
    # =====================================

    for month_name, month_number in months.items():

        if month_name in question:

            # Detect year
            year_match = re.search(
                r"\b(20\d{2})\b",
                question
            )

            year = (
                int(year_match.group())
                if year_match
                else date.today().year
            )

            # Detect:
            # 17 July
            # July 17
            day_match = re.search(
                rf"\b(?:"
                rf"(\d{{1,2}})\s+{month_name}"
                rf"|"
                rf"{month_name}\s+(\d{{1,2}})"
                rf")\b",
                question
            )

            if day_match:

                day = int(
                    day_match.group(1)
                    or day_match.group(2)
                )

                try:

                    selected_date = date(
                        year,
                        month_number,
                        day
                    )

                    return {
                        "start_date": selected_date,
                        "end_date": selected_date,
                        "label": selected_date.strftime(
                            "%d %B %Y"
                        ),
                    }

                except ValueError:
                    return None


            # Entire month
            last_day = monthrange(
                year,
                month_number
            )[1]

            start_date = date(
                year,
                month_number,
                1
            )

            end_date = date(
                year,
                month_number,
                last_day
            )

            return {
                "start_date": start_date,
                "end_date": end_date,
                "label": start_date.strftime(
                    "%B %Y"
                ),
            }

    return None


# =====================================
# Detect Financial Period
# =====================================

def detect_financial_period(question: str):

    question = question.lower()

    # Last month
    last_month_keywords = [
        "last month",
        "previous month",
    ]

    # All-time
    all_time_keywords = [
        "all time",
        "all-time",
        "overall",
        "total",
        "ever",
        "so far",
        "entire",
        "lifetime",
        "all my",
    ]

    # Current month
    current_month_keywords = [
        "this month",
        "current month",
        "monthly",
        "this month's",
    ]

    if any(
        keyword in question
        for keyword in last_month_keywords
    ):
        return "last_month"

    if any(
        keyword in question
        for keyword in all_time_keywords
    ):
        return "all_time"

    if any(
        keyword in question
        for keyword in current_month_keywords
    ):
        return "current_month"

    return "current_month"


# =====================================
# Chat With AI
# =====================================

def chat_with_ai(
    user_id: int,
    message: str,
    db: Session
):

    question = message.lower().strip()

    # =====================================
    # Check Custom Date First
    # =====================================

    custom_date = detect_custom_date_range(
        question
    )

    if custom_date:

        context = get_financial_context(
            user_id=user_id,
            db=db,
            start_date=custom_date["start_date"],
            end_date=custom_date["end_date"]
        )

        period_name = custom_date["label"]

    else:

        # Normal period detection
        period = detect_financial_period(
            question
        )

        context = get_financial_context(
            user_id=user_id,
            db=db,
            period=period
        )

        if period == "current_month":

            period_name = "this month"

        elif period == "last_month":

            period_name = "last month"

        else:

            period_name = "overall"


    # =====================================
    # Financial Data
    # =====================================

    summary = context["summary"]

    categories = context[
        "category_spending"
    ]

    budgets = context[
        "budget_status"
    ]

    health = context[
        "financial_health"
    ]


    # =====================================
    # Income Questions
    # =====================================

    income_keywords = [
        "income",
        "earn",
        "earned",
        "earning",
        "salary",
    ]

    if any(
        keyword in question
        for keyword in income_keywords
    ):

        return (
            f"Your income for "
            f"{period_name} is "
            f"₹{summary['income']:,.2f}."
        )


    # =====================================
    # Expense Questions
    # =====================================

    expense_keywords = [
        "expense",
        "expenses",
        "spend",
        "spent",
        "spending",
    ]

    if any(
        keyword in question
        for keyword in expense_keywords
    ):

        # Check category first
        for category, amount in categories.items():

            if category.lower() in question:

                return (
                    f"You spent "
                    f"₹{amount:,.2f} on "
                    f"{category} for "
                    f"{period_name}."
                )

        return (
            f"Your expenses for "
            f"{period_name} are "
            f"₹{summary['expenses']:,.2f}."
        )


    # =====================================
    # Savings Questions
    # =====================================

    if (
        "saving" in question
        or "savings" in question
    ):

        return (
            f"Your savings for "
            f"{period_name} are "
            f"₹{summary['savings']:,.2f}, "
            f"with a savings rate of "
            f"{summary['savings_rate']}%."
        )


    # =====================================
    # Financial Health
    # =====================================

    if (
        "health" in question
        or "score" in question
    ):

        return (
            f"Your financial health score for "
            f"{period_name} is "
            f"{health['score']}/100, "
            f"with a savings rate of "
            f"{health['savings_rate']}%."
        )


    # =====================================
    # Category Questions
    # =====================================

    for category, amount in categories.items():

        if category.lower() in question:

            # Category Budget
            if "budget" in question:

                budget = next(
                    (
                        b
                        for b in budgets
                        if b["category"].lower()
                        == category.lower()
                    ),
                    None
                )

                if budget:

                    return (
                        f"Your {category} budget is "
                        f"₹{budget['budget']:,.2f}. "
                        f"You spent "
                        f"₹{budget['spent']:,.2f} "
                        f"for {period_name}, with "
                        f"₹{budget['remaining']:,.2f} "
                        f"remaining."
                    )

            return (
                f"You spent "
                f"₹{amount:,.2f} on "
                f"{category} for "
                f"{period_name}."
            )


    # =====================================
    # Highest Spending Category
    # =====================================

    if (
        "highest" in question
        or "most" in question
        or "biggest" in question
    ):

        if categories:

            category = max(
                categories,
                key=categories.get
            )

            return (
                f"Your highest spending category "
                f"for {period_name} is "
                f"{category}, where you spent "
                f"₹{categories[category]:,.2f}."
            )

        return (
            f"I couldn't find any spending "
            f"data for {period_name}."
        )


    # =====================================
    # Budget Questions
    # =====================================

    if "budget" in question:

        if budgets:

            over_budget = [
                budget
                for budget in budgets
                if budget["remaining"] < 0
            ]

            if over_budget:

                categories_over = ", ".join(
                    budget["category"]
                    for budget in over_budget
                )

                return (
                    f"You are over budget in: "
                    f"{categories_over}."
                )

            return (
                "You are currently within all "
                "your set budgets. Great job!"
            )

        return (
            "You haven't set any budgets yet."
        )


    # =====================================
    # Gemini For Complex Questions
    # =====================================

    prompt = f"""
You are PennyWise AI, a personal finance assistant
for users in India.

The financial data below represents:
{period_name}.

All monetary values are in Indian Rupees (INR).

Always use the ₹ symbol.
Never use $, USD, or dollars.

Financial summary:
- Income: ₹{summary['income']:,.2f}
- Expenses: ₹{summary['expenses']:,.2f}
- Savings: ₹{summary['savings']:,.2f}
- Savings rate: {summary['savings_rate']}%
- Financial health score: {health['score']}/100

Category spending:
{categories}

Budget status:
{budgets}

User question:
{message}

Instructions:
- Answer using the financial data provided.
- Give practical and personalized financial advice.
- Keep the response concise and easy to understand.
- Always use ₹ for money.
- Never invent financial data.
- If data is unavailable, say so clearly.
- The financial data represents {period_name}.
"""

    response = client.models.generate_content(
        model=GEMINI_MODELS[0],
        contents=prompt
    )

    return response.text