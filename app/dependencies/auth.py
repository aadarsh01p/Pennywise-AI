from fastapi import Depends, Cookie, HTTPException
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from app.config import SECRET_KEY, ALGORITHM
from app.database import get_db
from app.models.user import User


def get_current_user(
    db: Session = Depends(get_db),
    access_token: str = Cookie(default=None),
):

    if access_token is None:
        raise HTTPException(
            status_code=401,
            detail="Not authenticated"
        )

    try:

        payload = jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

        email = payload.get("sub")

        if email is None:
            raise HTTPException(
                status_code=401,
                detail="Invalid token"
            )

        user = (
            db.query(User)
            .filter(User.email == email)
            .first()
        )

        if user is None:
            raise HTTPException(
                status_code=401,
                detail="User not found"
            )

        return user

    except JWTError:

        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )