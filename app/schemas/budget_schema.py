from pydantic import BaseModel


class BudgetUpdate(BaseModel):
    category: str
    budget_amount: float


class BudgetResponse(BaseModel):
    category: str
    budget_amount: float

    class Config:
        from_attributes = True