import random
from datetime import datetime, timedelta

from app.models.password_reset import PasswordReset


# ==============================
# Generate 4-digit OTP
# ==============================
def generate_otp():

    return str(random.randint(1000, 9999))


# ==============================
# Save OTP to Database
# ==============================
def save_otp(db, user_id: int, otp: str):

    # Remove any old OTPs for this user
    db.query(PasswordReset).filter(
        PasswordReset.user_id == user_id
    ).delete()

    reset = PasswordReset(
        user_id=user_id,
        otp=otp,
        expires_at=datetime.utcnow() + timedelta(minutes=5)
    )

    db.add(reset)
    db.commit()

    return reset


# ==============================
# Verify OTP
# ==============================
def verify_otp(db, user_id: int, otp: str):

    record = db.query(PasswordReset).filter(
        PasswordReset.user_id == user_id,
        PasswordReset.otp == otp
    ).first()

    if not record:
        return False

    if datetime.utcnow() > record.expires_at:
        db.delete(record)
        db.commit()
        return False

    return True


# ==============================
# Delete OTP
# ==============================
def delete_otp(db, user_id: int):

    db.query(PasswordReset).filter(
        PasswordReset.user_id == user_id
    ).delete()

    db.commit()