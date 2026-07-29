from datetime import datetime

from fastapi import APIRouter, Depends, File, UploadFile
from sqlalchemy.orm import Session

from app.auth_dependencies import get_current_user
from app.database import get_db
from app.models.transactions import Transaction
from app.models.user import User
from app.services.ai_service import categorize_transactions
from app.services.csv_service import read_csv

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    df = read_csv(file)

    descriptions = df["description"].astype(str).tolist()

    categories = categorize_transactions(descriptions)

    count = 0

    for (_, row), category in zip(df.iterrows(), categories):

        transaction = Transaction(

            user_id=current_user.id,

            date=datetime.strptime(
                row["date"],
                "%Y-%m-%d"
            ).date(),

            description=row["description"],

            amount=float(row["amount"]),

            transaction_type=row["transaction_type"],

            category=category,

            merchant=row["description"]

        )

        db.add(transaction)

        count += 1

    db.commit()

    return {
        "message": "CSV imported successfully",
        "rows": count
    }