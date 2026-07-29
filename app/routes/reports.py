from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from fastapi.responses import FileResponse
import os
from app.database import get_db
from app.auth_dependencies import get_current_user

from app.models.user import User
from app.services.report_service import get_report_data
from app.services.report_service import (
    get_report_data,
    generate_pdf
)

router = APIRouter(
    prefix="/api/reports",
    tags=["Reports"]
)

@router.get("/reports")
def reports_page():
    return FileResponse(
        os.path.join("app", "templates", "reports.html")
    )

@router.get("/")
def get_reports(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    """
    Returns all report data required by reports.js
    """

    return get_report_data(
        user_id=current_user.id,
        db=db
    )

@router.get("/pdf")
def download_report(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

    return generate_pdf(current_user, db)