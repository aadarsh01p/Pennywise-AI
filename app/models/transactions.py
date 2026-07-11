from sqlalchemy import Column, Integer, String, Float, Date, ForeignKey
from sqlalchemy.orm import relationship

from app.database import Base


class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    date = Column(Date, nullable=False)

    description = Column(String, nullable=False)

    amount = Column(Float, nullable=False)

    category = Column(
        String,
        default="Uncategorized"
    )

    transaction_type = Column(
        String,
        default="Expense"
    )

    merchant = Column(
        String,
        nullable=True
    )

    user = relationship(
        "User",
        back_populates="transactions"
    )