from pydantic import BaseModel
import datetime
from typing import Optional


class TransactionCreate(BaseModel):
    date: datetime.date
    description: str
    amount: float
    category: Optional[str] = "Uncategorized"
    transaction_type: str
    merchant: Optional[str] = None


class TransactionUpdate(BaseModel):
    date: Optional[datetime.date] = None
    description: Optional[str] = None
    amount: Optional[float] = None
    category: Optional[str] = None
    transaction_type: Optional[str] = None
    merchant: Optional[str] = None


class TransactionResponse(BaseModel):
    id: int
    user_id: int
    date: datetime.date
    description: str
    amount: float
    category: str
    transaction_type: str
    merchant: Optional[str] = None

    class Config:
        from_attributes = True