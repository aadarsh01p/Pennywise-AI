from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database import get_db
from app.auth_dependencies import get_current_user
from app.models.user import User
from app.services.csv_service import read_csv

router = APIRouter(
    prefix="/upload",
    tags=["Upload"]
)


@router.post("/csv")
async def upload_csv(
    file: UploadFile = File(...),
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):

   df = read_csv(file)

   return {
        "rows": len(df),
        "columns": list(df.columns)
    }