from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import get_current_user

from app.models.user import User
from app.schemas.budget_schema import BudgetUpdate

from app.services.budget_service import (
    get_budget_summary,
    save_budget,
    generate_ai_budget
)

router = APIRouter(
    prefix="/api/budget",
    tags=["Budget"]
)


@router.get("/")
def get_budget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_budget_summary(
        current_user.id,
        db
    )


@router.post("/generate")
def generate_budget(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return generate_ai_budget(
        current_user.id,
        db
    )


@router.put("/")
def update_budget(
    budget: BudgetUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    save_budget(
        current_user.id,
        budget,
        db
    )

    return {
        "message": "Budget Updated"
    }