from sqlalchemy import Column, Integer, String
from app.database import Base
from sqlalchemy.orm import relationship

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, nullable=False)
    full_name = Column(String, nullable=True)
    email = Column(String, unique=True, nullable=False)
    password = Column(String, nullable=False)
    transactions = relationship(
    "Transaction",
    back_populates="user",
    cascade="all, delete-orphan"
    )