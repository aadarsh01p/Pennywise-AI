from google import genai
from sqlalchemy.orm import Session

from app.config import GEMINI_API_KEY, GEMINI_MODELS
from app.services.finance_engine import get_financial_context


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def chat_with_ai(
    user_id: int,
    message: str,
    db: Session
):
    context = get_financial_context(user_id, db)

    question = message.lower().strip()

    summary = context["summary"]
    categories = context["category_spending"]
    budgets = context["budget_status"]
    health = context["financial_health"]

    # =========================
    # Basic financial questions
    # =========================

    if "income" in question:
        return f"Your current income is ₹{summary['income']:,.2f}."

    if "expense" in question or "spending" in question:
        return f"Your current expenses are ₹{summary['expenses']:,.2f}."

    if "saving" in question:
        return (
            f"Your current savings are ₹{summary['savings']:,.2f}, "
            f"with a savings rate of {summary['savings_rate']}%."
        )

    if "health" in question or "score" in question:
        return (
            f"Your financial health score is "
            f"{health['score']}/100, with a savings rate of "
            f"{health['savings_rate']}%."
        )

    # =========================
    # Category questions
    # =========================

    for category, amount in categories.items():

        if category.lower() in question:

            if "budget" in question:

                budget = next(
                    (
                        b for b in budgets
                        if b["category"].lower() == category.lower()
                    ),
                    None
                )

                if budget:
                    return (
                        f"Your {category} budget is "
                        f"₹{budget['budget']:,.2f}. "
                        f"You have spent ₹{budget['spent']:,.2f}, "
                        f"with ₹{budget['remaining']:,.2f} remaining."
                    )

            return (
                f"You spent ₹{amount:,.2f} on "
                f"{category}."
            )

    # =========================
    # Highest spending category
    # =========================

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
                f"Your highest spending category is "
                f"{category}, where you spent "
                f"₹{categories[category]:,.2f}."
            )

    # =========================
    # Budget questions
    # =========================

    if "budget" in question:

        if budgets:

            over_budget = [
                b for b in budgets
                if b["remaining"] < 0
            ]

            if over_budget:

                categories_over = ", ".join(
                    b["category"]
                    for b in over_budget
                )

                return (
                    f"You are currently over budget in: "
                    f"{categories_over}."
                )

            return (
                "You are currently within all your "
                "set budgets. Great job!"
            )

    # =========================
    # Gemini for complex advice
    # =========================

    prompt = f"""
You are PennyWise AI, a personal finance assistant
for users in India.

All monetary values are in Indian Rupees (INR).
Always use the ₹ symbol. Never use $, USD, or dollars.

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
- Give practical and personalized financial advice.
- Keep the response concise.
- Always use ₹ for money.
- Do not invent financial data.
- Use the provided financial information.
- If information is unavailable, say so clearly.
"""

    response = client.models.generate_content(
        model=GEMINI_MODELS[0],
        contents=prompt
    )

    return response.text