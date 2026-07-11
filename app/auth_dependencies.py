from fastapi import Depends, Cookie, HTTPException
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.user import User
from app.utils.auth import verify_token


def get_current_user(
    access_token: str = Cookie(None),
    db: Session = Depends(get_db)
):

    if not access_token:
        raise HTTPException(
            status_code=401,
            detail="Login required"
        )

    payload = verify_token(access_token)

    if not payload:
        raise HTTPException(
            status_code=401,
            detail="Invalid Token"
        )

    user = db.query(User).filter(
        User.email == payload["sub"]
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user