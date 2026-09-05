from fastapi import APIRouter, Depends, UploadFile, File
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.controllers.upload_controller import UploadController
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.upload_schema import UploadResponse

router = APIRouter(prefix="/upload", tags=["Upload"])


@router.post("/", response_model=UploadResponse)
def upload_csv(
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    controller = UploadController(db)
    return controller.handle_upload(file)
