from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.investigation_repository import InvestigationRepository
from app.schemas.evidence_schema import EvidenceResponse


class EvidenceController:
    """
    Handles orchestration for evidence-related read operations.
    No business logic here - only wiring + ownership check.
    """

    def __init__(self, db: Session):
        self.repository = EvidenceRepository(db)
        self.investigation_repo = InvestigationRepository(db)

    def list_evidence(
        self, investigation_id: int, user_id: int
    ) -> list[EvidenceResponse]:
        investigation = self.investigation_repo.get_by_id_for_user(
            investigation_id, user_id
        )
        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail=f"Investigation with id {investigation_id} not found",
            )

        evidence_list = self.repository.get_by_investigation(investigation_id)
        return [EvidenceResponse.model_validate(e) for e in evidence_list]