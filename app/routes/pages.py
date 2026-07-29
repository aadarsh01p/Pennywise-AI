from fastapi import APIRouter, Cookie
from fastapi.responses import FileResponse, RedirectResponse, HTMLResponse
from jose import jwt, JWTError
import os

from app.config import SECRET_KEY, ALGORITHM

router = APIRouter(tags=["Pages"])

BASE_DIR = os.path.join("app", "templates")


def is_authenticated(access_token: str | None):

    if access_token is None:
        return False

    try:
        jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )
        return True

    except JWTError:
        return False


@router.get("/")
def home():
    return RedirectResponse(url="/login")


@router.get("/login")
def login_page():

    return FileResponse(
        os.path.join(BASE_DIR, "login.html")
    )


@router.get("/register")
def register_page():

    return FileResponse(
        os.path.join(BASE_DIR, "register.html")
    )


@router.get("/forgot-password")
def forgot_password():

    return FileResponse(
        os.path.join(BASE_DIR, "forgot_password.html")
    )


@router.get("/dashboard")
def dashboard(
    access_token: str = Cookie(default=None)
):

    if not is_authenticated(access_token):
        return RedirectResponse(url="/login")

    return FileResponse(
        os.path.join(BASE_DIR, "dashboard.html")
    )


@router.get("/transactions")
def transactions(
    access_token: str = Cookie(default=None)
):

    if not is_authenticated(access_token):
        return RedirectResponse(url="/login")

    return FileResponse(
        os.path.join(BASE_DIR, "transactions.html")
    )


@router.get("/upload")
def upload_page(
    access_token: str = Cookie(default=None)
):

    if not is_authenticated(access_token):
        return RedirectResponse(url="/login")

    return FileResponse(
        os.path.join(BASE_DIR, "upload.html")
    )


@router.get("/reports")
def reports_page(
    access_token: str = Cookie(default=None)
):

    if not is_authenticated(access_token):
        return RedirectResponse(url="/login")

    return FileResponse(
        os.path.join(BASE_DIR, "reports.html")
    )

@router.get("/budget")
def budget_page():
    return FileResponse(
        os.path.join("app", "templates", "budget.html")
    )

@router.get("/goals")
def goals_page(
    access_token: str = Cookie(default=None)
):

    if not is_authenticated(access_token):
        return RedirectResponse(url="/login")

    return FileResponse(
        os.path.join(BASE_DIR, "goals.html")
    )