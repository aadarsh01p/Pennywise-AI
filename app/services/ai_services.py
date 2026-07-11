import google.generativeai as genai

from app.config import GEMINI_API_KEY

genai.configure(api_key=GEMINI_API_KEY)

model = genai.GenerativeModel("gemini-2.5-flash")


def categorize_transaction(description: str):

    prompt = f"""
You are a financial expense categorization AI.

Categorize the following transaction into ONLY ONE of these categories:

Food
Transport
Shopping
Entertainment
Bills
Healthcare
Education
Salary
Investment
Travel
Fuel
Groceries
Rent
Other

Transaction:
{description}

Return ONLY the category name.
"""

    try:

        response = model.generate_content(prompt)

        return response.text.strip()

    except Exception:

        return "Other"