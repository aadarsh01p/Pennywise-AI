from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import get_current_user

from app.models.user import User

from app.schemas.goal_schema import (
    GoalCreate,
    GoalUpdate
)

from app.services.goal_service import (
    get_goals,
    create_goal,
    update_goal,
    delete_goal
)

router = APIRouter(
    prefix="/api/goals",
    tags=["Goals"]
)


@router.get("/")
def goals(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return get_goals(
        current_user.id,
        db
    )


@router.post("/")
def add_goal(
    goal: GoalCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return create_goal(
        current_user.id,
        goal,
        db
    )


@router.put("/{goal_id}")
def edit_goal(
    goal_id: int,
    goal: GoalUpdate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return update_goal(
        current_user.id,
        goal_id,
        goal,
        db
    )


@router.delete("/{goal_id}")
def remove_goal(
    goal_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return delete_goal(
        current_user.id,
        goal_id,
        db
    )