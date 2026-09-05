from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.controllers.investigation_controller import InvestigationController
from app.database.session import get_db
from app.schemas.investigation_schema import InvestigationResponse

router = APIRouter(prefix="/investigations", tags=["Investigations"])


@router.get("/", response_model=list[InvestigationResponse])
def list_investigations(db: Session = Depends(get_db)):
    controller = InvestigationController(db)
    return controller.list_investigations()


@router.get("/{investigation_id}", response_model=InvestigationResponse)
def get_investigation(investigation_id: int, db: Session = Depends(get_db)):
    controller = InvestigationController(db)
    return controller.get_investigation(investigation_id)