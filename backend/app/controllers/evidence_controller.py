from sqlalchemy.orm import Session

from app.repositories.evidence_repository import EvidenceRepository
from app.schemas.evidence_schema import EvidenceResponse


class EvidenceController:
    """
    Handles orchestration for evidence-related read operations.
    No business logic here — only wiring.
    """

    def __init__(self, db: Session):
        self.repository = EvidenceRepository(db)

    def list_evidence(self, investigation_id: int) -> list[EvidenceResponse]:
        evidence_list = self.repository.get_by_investigation(investigation_id)
        return [EvidenceResponse.model_validate(e) for e in evidence_list]
