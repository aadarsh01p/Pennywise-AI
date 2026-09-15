# PennyWise AI

**Personal finance tracking, budgeting, and AI assistance.**

PennyWise AI is a personal finance web app that helps users track income and expenses, plan budgets, and set savings goals. It brings transactions, charts, reports, and an AI assistant into one place, making it easier to understand where money is going.

I built this project to put Python backend development into practice and explore how AI can help with everyday financial tasks.

## Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Project Structure](#project-structure)
- [Getting Started](#getting-started)
- [CSV Upload](#csv-upload)
- [How It Works](#how-it-works)
- [AI Assistant](#ai-assistant)
- [Project Notes](#project-notes)
- [Planned Improvements](#planned-improvements)

## Features

- **Account management:** Register, log in, and reset a password through an email OTP.
- **Dashboard:** View income, expenses, savings, spending charts, and recent transactions.
- **Transactions:** Add or delete transactions and automatically categorize them with Gemini.
- **CSV upload:** Import statements with a loading animation and a success message.
- **Budgets:** Generate a budget from spending history and adjust category limits.
- **Savings goals:** Set a target, timeframe, and priority to estimate how much to save each month.
- **Reports:** Review spending summaries and download a PDF report.
- **AI assistant:** Ask questions about financial data for a particular month or day, or across all recorded transactions.

All amounts are displayed in Indian Rupees (₹).

## Tech Stack

| Part | Technologies |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn |
| Frontend | HTML, CSS, JavaScript, Bootstrap |
| Database | SQLite, SQLAlchemy |
| Authentication | JWT, Passlib, bcrypt |
| Charts | Chart.js |
| AI | Google Gemini through the Google Gen AI SDK |
| CSV and PDF | pandas, ReportLab |

The frontend uses plain HTML pages served by FastAPI. Although the files are in `app/templates/`, the project does not use Jinja templates.

## Project Structure

| Path | What it contains |
| --- | --- |
| `app/main.py` | Application setup and router registration |
| `app/config.py` | Environment settings and Gemini model configuration |
| `app/database.py` | Database connection and sessions |
| `app/models/` | Database models |
| `app/schemas/` | Request and response validation |
| `app/routes/` | Page routes and API endpoints |
| `app/services/` | Finance calculations, AI, CSV, reports, and email logic |
| `app/utils/` | Password hashing and JWT helpers |
| `app/templates/` | HTML pages |
| `app/static/` | CSS, JavaScript, and favicon |
| `run.py` | Starts the development server |
| `requirements.txt` | Python dependencies |

## Getting Started

### 1. Create a virtual environment

Extract the project and open a terminal in its root folder:

```bash
cd Pennywise-AI-main
python -m venv .venv
```

Activate the virtual environment:

**Windows PowerShell**

```powershell
.\.venv\Scripts\Activate.ps1
```

**macOS / Linux**

```bash
source .venv/bin/activate
```

### 2. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 3. Configure environment variables

Create a `.env` file in the project root:

```dotenv
SECRET_KEY=your_random_secret_key
GEMINI_API_KEY=your_gemini_api_key
EMAIL_ADDRESS=your_email@gmail.com
EMAIL_PASSWORD=your_smtp_app_password
```

Set the Gemini key before starting the app because the AI clients initialize at startup. Email credentials are needed for password reset; the current email service uses Gmail SMTP.

You can generate a secret key with:

```bash
python -c "import secrets; print(secrets.token_hex(32))"
```

Keep your `.env` file and personal database out of version control.

### 4. Start the application

```bash
python run.py
```

| Open | Address |
| --- | --- |
| Application | [http://127.0.0.1:8000](http://127.0.0.1:8000) |
| API documentation | [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs) |

Run the server from the project root and use `127.0.0.1:8000` consistently. The database and tables are created automatically on startup.

## CSV Upload

Use these exact column names and date format:

```csv
date,description,amount,transaction_type
2026-08-01,Monthly salary,30000,Income
2026-08-02,House rent,8000,Expense
2026-08-03,DMart groceries,1800,Expense
```

- **Date:** Use `YYYY-MM-DD`.
- **Amount:** Enter a positive number without currency symbols.
- **Type:** Use exactly `Income` or `Expense`.
- **Category:** Assigned automatically by the application.

> Upload each statement only once. Duplicate detection is not implemented yet.

## How It Works

1. **Sign in:** The backend verifies the credentials and sets an HTTP-only JWT cookie.
2. **Add transactions:** Enter them manually or import a CSV. Gemini assigns categories.
3. **Review finances:** FastAPI retrieves the user's records from SQLite and calculates summaries, budgets, and goal estimates.
4. **Explore the results:** JavaScript displays the data in charts, tables, and reports.

## AI Assistant

The chatbot answers recognized financial questions from calculated data and uses Gemini for more complex questions.

Try asking:

- “What is my income this month?”
- “How much did I spend in August 2026?”
- “What were my expenses on 17/07/2026?”
- “What are my overall savings?”

## Project Notes

- **Time periods:** Dashboard and report totals are all-time; the chatbot defaults to the current month.
- **Goal progress:** Shows estimated monthly funding coverage, not actual deposits.
- **Health scores:** The dashboard and chatbot currently use different formulas.
- **Password reset:** Available in the login modal; the separate reset page is missing.
- **Chatbot logout:** Its request URL needs correcting to `/auth/logout`.