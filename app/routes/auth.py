from fastapi import APIRouter, Depends, HTTPException, Response
from sqlalchemy.orm import Session
from sqlalchemy import or_

from app.database import get_db
from app.models.user import User

from app.schemas.user_schemas import UserRegister, UserLogin
from app.schemas.password_reset_schemas import (
    SendOTPRequest,
    ResetPasswordRequest
)

from app.utils.auth import (
    hash_password,
    verify_password,
    create_access_token,
)

from app.services.email_service import send_email
from app.services.otp_service import (
    generate_otp,
    save_otp,
    verify_otp,
    delete_otp,
)

router = APIRouter(
    prefix="/auth",
    tags=["Authentication"]
)

@router.post("/register")
def register(user: UserRegister, db: Session = Depends(get_db)):

    # Check if email already exists
    if db.query(User).filter(User.email == user.email).first():
        raise HTTPException(
            status_code=400,
            detail="Email already registered"
        )

    # Check if username already exists
    if db.query(User).filter(User.username == user.username).first():
        raise HTTPException(
            status_code=400,
            detail="Username already taken"
        )

    # Create new user
    new_user = User(
        username=user.username,
        full_name=user.full_name,
        email=user.email,
        password=hash_password(user.password)
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)

    return {
        "success": True,
        "message": "Registration successful"
    }

@router.post("/login")
def login(
    response: Response,
    user: UserLogin,
    db: Session = Depends(get_db)
):

    # Find user by email
    db_user = db.query(User).filter(
        or_(
        User.email == user.username_or_email,
        User.username == user.username_or_email
    )
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    # Verify password
    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=401,
            detail="Invalid password"
        )

    # Generate JWT Token
    token = create_access_token(
        {"sub": db_user.email}
    )
    response.set_cookie(
    key="access_token",
    value=token,
    httponly=True,
    samesite="lax",
    secure=False  # Change to True when using HTTPS
    )

    return {
    "success": True,
    "message": "Login successful",
    "user": {
        "id": db_user.id,
        "username": db_user.username,
        "full_name": db_user.full_name,
        "email": db_user.email
    }
}

# ==========================================
# Send Password Reset OTP
# ==========================================
@router.post("/send-otp")
def send_otp(
    request: SendOTPRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="Email not registered."
        )

    otp = generate_otp()
    save_otp(db, user.id, otp)

    subject = "PennyWise AI - Password Reset OTP"

    body = f"""
Hello {user.username},

Your password reset OTP is:

{otp}

This OTP is valid for 5 minutes.

Regards,
PennyWise AI
"""

    if not send_email(request.email, subject, body):
        raise HTTPException(
            status_code=500,
            detail="Failed to send email."
        )

    return {"message": "OTP sent successfully."}

@router.post("/reset-password")
def reset_password(
    request: ResetPasswordRequest,
    db: Session = Depends(get_db)
):

    user = db.query(User).filter(
        User.email == request.email
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    if not verify_otp(db, user.id, request.otp):
        raise HTTPException(
            status_code=400,
            detail="Invalid or expired OTP"
        )

    user.password = hash_password(request.new_password)

    delete_otp(db, user.id)

    db.commit()

    return {
        "message": "Password updated successfully"
    }

@router.post("/logout")
def logout(response: Response):

    response.delete_cookie(
        key="access_token",
        samesite="lax",
        secure=False
    )

    return {
        "success": True,
        "message": "Logged out successfully"
    }