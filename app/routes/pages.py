from fastapi import APIRouter, Request, Cookie
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from jose import JWTError, jwt

from app.config import SECRET_KEY, ALGORITHM

router = APIRouter()

templates = Jinja2Templates(directory="app/templates")


# ==========================
# Home Route
# ==========================

@router.get("/")
def home():
    return RedirectResponse(url="/login")


# ==========================
# Login Page
# ==========================

@router.get("/login")
def login_page(request: Request):
    return templates.TemplateResponse(
        "login.html",
        {"request": request}
    )


# ==========================
# Register Page
# ==========================

@router.get("/register")
def register_page(request: Request):
    return templates.TemplateResponse(
        "register.html",
        {"request": request}
    )


# ==========================
# Protected Dashboard
# ==========================

@router.get("/dashboard")
def dashboard(
    request: Request,
    access_token: str = Cookie(default=None)
):

    if access_token is None:
        return RedirectResponse(url="/login")

    try:
        jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except JWTError:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request
        }
    )


# ==========================
# Transactions Page
# ==========================

@router.get("/transactions")
def transactions(
    request: Request,
    access_token: str = Cookie(default=None)
):

    if access_token is None:
        return RedirectResponse(url="/login")

    try:
        jwt.decode(
            access_token,
            SECRET_KEY,
            algorithms=[ALGORITHM]
        )

    except JWTError:
        return RedirectResponse(url="/login")

    return templates.TemplateResponse(
        "transactions.html",
        {
            "request": request
        }
    )

@router.get("/forgot-password")
def forgot_password(request: Request):
    return templates.TemplateResponse(
        "forgot_password.html",
        {"request": request}
    )

@router.get("/upload")
def upload_page(
    request: Request,
    access_token: str = Cookie(default=None)
):
    ...
    return templates.TemplateResponse(
        "upload.html",
        {"request": request}
    )