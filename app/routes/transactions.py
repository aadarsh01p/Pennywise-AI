from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.dependencies.auth import get_current_user

from app.models.transactions import Transaction
from app.models.user import User

from app.schemas.transaction_schemas import (
    TransactionCreate,
    TransactionResponse,
)
from app.services.ai_service import categorize_transaction

router = APIRouter(
    prefix="/api/transactions",
    tags=["Transactions"]
)


# =====================================
# Get Logged-in User Transactions
# =====================================

@router.get("/", response_model=list[TransactionResponse])
def get_transactions(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    print("Current User ID:", current_user.id)
    print("Current User Email:", current_user.email)
    transactions = (
        db.query(Transaction)
        .filter(Transaction.user_id == current_user.id)
        .all()
    )

    return transactions


# =====================================
# Create Transaction
# =====================================

@router.post("/", response_model=TransactionResponse)
def create_transaction(
    transaction: TransactionCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    new_transaction = Transaction(
        user_id=current_user.id,
        date=transaction.date,
        description=transaction.description,
        amount=transaction.amount,
        category=categorize_transaction(transaction.description),
        transaction_type=transaction.transaction_type,
        merchant=transaction.merchant,
    )

    db.add(new_transaction)
    db.commit()
    db.refresh(new_transaction)

    return new_transaction


# =====================================
# Delete Transaction
# =====================================

@router.delete("/{transaction_id}")
def delete_transaction(
    transaction_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db),
):

    transaction = (
        db.query(Transaction)
        .filter(
            Transaction.id == transaction_id,
            Transaction.user_id == current_user.id
        )
        .first()
    )

    if transaction is None:
        raise HTTPException(
            status_code=404,
            detail="Transaction not found"
        )

    db.delete(transaction)
    db.commit()

    return {
        "message": "Transaction deleted successfully"
    }