from collections import defaultdict
from sqlalchemy.orm import Session

from app.models.transactions import Transaction
from io import BytesIO
from reportlab.lib.units import inch
from reportlab.pdfgen import canvas
from fastapi.responses import StreamingResponse

def get_report_data(user_id: int, db: Session):

    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == user_id)
        .all()
    )

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

    if income > 0:
        health = round((savings / income) * 100)
    else:
        health = 0

    health = max(0, min(100, health))

    monthly = defaultdict(float)

    for t in transactions:

        if t.transaction_type == "Expense":

            month = t.date.strftime("%b")

            monthly[month] += t.amount

    monthly_expenses = [
        {
            "month": month,
            "amount": amount
        }
        for month, amount in monthly.items()
    ]

    categories = defaultdict(float)

    for t in transactions:

        if t.transaction_type == "Expense":

            categories[t.category] += t.amount

    category_totals = [
        {
            "category": category,
            "amount": amount
        }
        for category, amount in categories.items()
    ]

    expenses = [
        t
        for t in transactions
        if t.transaction_type == "Expense"
    ]

    expenses.sort(
        key=lambda x: x.amount,
        reverse=True
    )

    top_expenses = []

    for t in expenses[:5]:

        top_expenses.append({

            "date": str(t.date),

            "description": t.description,

            "category": t.category,

            "amount": t.amount

        })

    insights = []

    if savings > 0:
        insights.append(f"You saved ₹{savings} this month.")

    if expense > income * 0.8:
        insights.append("Expenses are very high.")

    if health >= 70:
        insights.append("Your financial health is good.")
    else:
        insights.append("Try reducing unnecessary expenses.")

    return {
        "income": income,
        "expense": expense,
        "savings": savings,
        "health": health,
        "monthly": monthly_expenses,
        "categories": category_totals,
        "top_expenses": top_expenses,
        "insights": insights
    }

def generate_pdf(current_user, db):

    report = get_report_data(current_user.id, db)

    buffer = BytesIO()

    pdf = canvas.Canvas(buffer)

    y = 800

    pdf.setFont("Helvetica-Bold", 18)
    pdf.drawString(50, y, "PennyWise AI Report")

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Financial Summary")

    y -= 25

    pdf.setFont("Helvetica", 12)
    pdf.drawString(60, y, f"Income   : ₹{report['income']}")

    y -= 20
    pdf.drawString(60, y, f"Expense : ₹{report['expense']}")

    y -= 20
    pdf.drawString(60, y, f"Savings : ₹{report['savings']}")

    y -= 40

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Category Summary")

    y -= 25

    pdf.setFont("Helvetica", 12)

    for category in report["categories"]:

        pdf.drawString(
            60,
            y,
            f"{category['category']} : ₹{category['amount']}"
        )

        y -= 18

    y -= 20

    pdf.setFont("Helvetica-Bold", 14)
    pdf.drawString(50, y, "Top Expenses")

    y -= 25

    pdf.setFont("Helvetica", 12)

    for transaction in report["top_expenses"]:

        pdf.drawString(
            60,
            y,
            f"{transaction['date']} | "
            f"{transaction['description']} | "
            f"₹{transaction['amount']}"
        )

        y -= 18

        if y < 60:
            pdf.showPage()
            y = 800
            pdf.setFont("Helvetica", 12)

    pdf.save()

    buffer.seek(0)

    return StreamingResponse(
        buffer,
        media_type="application/pdf",
        headers={
            "Content-Disposition":
            "attachment; filename=PennyWise_Report.pdf"
        }
    )