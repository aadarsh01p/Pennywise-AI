from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from app.database import Base


class Goal(Base):
    __tablename__ = "goals"

    id = Column(Integer, primary_key=True, index=True)

    user_id = Column(
        Integer,
        ForeignKey("users.id"),
        nullable=False
    )

    goal_name = Column(String, nullable=False)

    target_amount = Column(Float, nullable=False)

    duration_months = Column(Integer, nullable=False)

    priority = Column(
        String,
        default="Medium"
    )

    created_at = Column(
        DateTime(timezone=True),
        server_default=func.now()
    )

    user = relationship("User")