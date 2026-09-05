from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.evidence_controller import EvidenceController
from app.database.session import get_db
from app.dependencies.auth import get_current_user
from app.models.user import User
from app.schemas.evidence_schema import EvidenceResponse

router = APIRouter(prefix="/investigations", tags=["Evidence"])


@router.get("/{investigation_id}/evidence", response_model=list[EvidenceResponse])
def list_evidence(
    investigation_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    controller = EvidenceController(db)
    return controller.list_evidence(investigation_id)