from typing import Literal

from pydantic import BaseModel, Field


class GoalCreate(BaseModel):

    goal_name: str = Field(
        min_length=1,
        max_length=100
    )

    target_amount: float = Field(gt=0)

    duration_months: int = Field(gt=0)

    priority: Literal["High", "Medium", "Low"] = "Medium"


class GoalUpdate(BaseModel):

    goal_name: str = Field(
        min_length=1,
        max_length=100
    )

    target_amount: float = Field(gt=0)

    duration_months: int = Field(gt=0)

    priority: Literal["High", "Medium", "Low"]