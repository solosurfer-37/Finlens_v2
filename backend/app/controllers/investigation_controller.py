from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.investigation_repository import InvestigationRepository
from app.schemas.investigation_schema import InvestigationResponse


class InvestigationController:
    """
    Handles orchestration for investigation-related read operations.
    No business logic here — only wiring + error translation.
    """

    def __init__(self, db: Session):
        self.repository = InvestigationRepository(db)

    def get_investigation(self, investigation_id: int) -> InvestigationResponse:
        investigation = self.repository.get_by_id(investigation_id)

        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail=f"Investigation with id {investigation_id} not found",
            )

        return InvestigationResponse.model_validate(investigation)