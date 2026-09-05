from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.report_controller import ReportController
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.report_schema import ReportResponse

router = APIRouter(prefix="/investigations", tags=["Report"])


@router.get("/{investigation_id}/report", response_model=ReportResponse)
def get_report(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    controller = ReportController(db)
    return controller.get_report(investigation_id)