import json
import re
from google import genai
from google.genai import types
from app.config import GEMINI_API_KEY, GEMINI_MODELS

client = genai.Client(api_key=GEMINI_API_KEY)

ALLOWED = {
    "Food", "Transport", "Shopping", "Entertainment", "Bills",
    "Healthcare", "Education", "Salary", "Investment", "Travel",
    "Fuel", "Groceries", "Rent", "Other"
}

BUDGET_CATEGORIES = [
    "Food",
    "Groceries",
    "Transport",
    "Fuel",
    "Shopping",
    "Bills",
    "Entertainment",
    "Healthcare",
    "Education",
    "Travel",
    "Rent",
    "Other"
]

# Simple in-memory cache (swap for a DB table if you want it to persist
# across server restarts — see note below)
_category_cache: dict[str, str] = {}

def _normalize(description: str) -> str:
    """Strip trailing reference numbers/IDs so 'STARBUCKS #4521' and
    'STARBUCKS #7788' hit the same cache entry."""
    desc = description.strip().upper()
    desc = re.sub(r"#?\d{3,}", "", desc)  # drop long numeric IDs
    return re.sub(r"\s+", " ", desc).strip()

CLASSIFICATION_RULES = """
Decision rules (apply these strictly and consistently):

- Coffee shops, cafes, restaurants, fast food, food delivery apps (Starbucks, 
  McDonald's, Zomato, Swiggy, Domino's, etc.) -> Food
- Supermarkets, grocery stores, kirana stores (BigBasket, DMart, local grocers) -> Groceries
- Cabs, buses, metro, ride-hailing (Uber, Ola, public transit) -> Transport
- Petrol pumps, fuel stations -> Fuel
- Clothing, electronics, general e-commerce (Amazon, Flipkart, Myntra) -> Shopping
- Movies, streaming, games, concerts (Netflix, Spotify, BookMyShow) -> Entertainment
- Electricity, water, internet, phone, insurance premiums -> Bills
- Hospitals, pharmacies, clinics, doctor fees -> Healthcare
- Tuition, courses, books, school/college fees -> Education
- Monthly salary credit, payroll -> Salary
- Mutual funds, credit, freelance, stocks, SIPs, fixed deposits -> Investment
- Flights, hotels, holiday bookings -> Travel
- House rent, landlord payments -> Rent
- Anything that doesn't clearly match the above -> Other

If a merchant could plausibly fit two categories, always pick the SAME one 
every time by using the FIRST matching rule above, top to bottom.
"""

def _build_prompt(numbered: str) -> str:
    return f"""
You are a deterministic financial transaction classifier. You must be 
perfectly consistent: the same transaction description must always map to 
the same category, every single time you are asked.

Categories (use EXACTLY these labels, nothing else):
{", ".join(sorted(ALLOWED))}

{CLASSIFICATION_RULES}

Return ONLY valid JSON, no markdown, no explanation, in this exact shape:
{{"1": "Food", "2": "Shopping", "3": "Bills"}}

Transactions:
{numbered}
"""

def categorize_transactions(descriptions: list[str]) -> list[str]:
    results: list[str | None] = [None] * len(descriptions)

    # 1. Fill in anything we've already classified before
    to_query: list[tuple[int, str]] = []
    for i, desc in enumerate(descriptions):
        key = _normalize(desc)
        if key in _category_cache:
            results[i] = _category_cache[key]
        else:
            to_query.append((i, desc))

    # 2. Only ask Gemini about genuinely new descriptions
    batch_size = 10
    for start in range(0, len(to_query), batch_size):
        batch = to_query[start:start + batch_size]
        numbered = "\n".join(f"{n+1}. {desc}" for n, (_, desc) in enumerate(batch))
        prompt = _build_prompt(numbered)

        response = None
        for model in GEMINI_MODELS:
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        temperature=0,   # <-- deterministic
                        top_p=1,
                        top_k=1,
                    ),
                )
                break
            except Exception as e:
                print(f"{model} failed -> {e}")

        if response is None:
            for idx, desc in batch:
                results[idx] = "Other"
            continue

        try:
            cleaned = response.text.strip().strip("`").removeprefix("json").strip()
            parsed = json.loads(cleaned)
        except Exception as e:
            print(f"JSON parse failed: {e}\nRaw: {response.text}")
            parsed = {}

        for n, (idx, desc) in enumerate(batch):
            category = parsed.get(str(n + 1), "Other")
            category = category.strip().title()
            if category not in ALLOWED:
                category = "Other"
            results[idx] = category
            _category_cache[_normalize(desc)] = category  # cache it

    return results  # type: ignore

def categorize_transaction(description: str) -> str:
    return categorize_transactions([description])[0]

def generate_budget(
    average_income,
    average_expense,
    category_expense,
    health
):

    categories = "\n".join(BUDGET_CATEGORIES)

    prompt = f"""
You are an expert personal finance advisor.

A user has the following financial profile.

Average Monthly Income:
₹{round(average_income, 2)}

Average Monthly Expenses:
₹{round(average_expense, 2)}

Financial Health Score:
{health}/100

Average Monthly Spending by Category:

{json.dumps(category_expense, indent=2)}

Generate a practical monthly budget.

Rules:

- Use ONLY these categories:

{categories}

- Do NOT invent new categories.
- Return every category exactly once.
- Essential categories (Rent, Bills, Groceries, Healthcare) should remain close to historical spending.
- Non-essential categories (Shopping, Entertainment, Travel) may be reduced if spending appears excessive.
- The total recommended budget should generally remain below the user's average monthly income.
- Return ONLY valid JSON.
- No markdown.
- No explanation.
- Generate a monthly budget ONLY for these expense categories.

Do NOT include:

- Salary
- Investment
- Savings

These are not expense budgets.
Example:

{{
    "Food": 7000,
    "Groceries": 4500,
    "Transport": 3000,
    "Fuel": 2000,
    "Shopping": 3500,
    "Bills": 9000,
    "Entertainment": 2500,
    "Healthcare": 1500,
    "Education": 3000,
    "Travel": 2000,
    "Rent": 18000,
    "Other": 1000
}}
"""

    response = None

    for model in GEMINI_MODELS:

        try:

            response = client.models.generate_content(
                model=model,
                contents=prompt,
                config=types.GenerateContentConfig(
                    temperature=0.2
                )
            )

            break

        except Exception as e:

            print(f"{model} failed -> {e}")

    if response is None:
        return {}

    try:

        cleaned = (
            response.text
            .strip()
            .strip("`")
            .removeprefix("json")
            .strip()
        )

        return json.loads(cleaned)

    except Exception as e:

        print("Budget JSON Parse Error:", e)
        print(response.text)

        return {}