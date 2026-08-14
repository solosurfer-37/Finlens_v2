from sqlalchemy.orm import Session

from app.models.evidence import Evidence


class EvidenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def bulk_create(self, evidence_list: list[Evidence]) -> list[Evidence]:
        self.db.add_all(evidence_list)
        self.db.commit()
        return evidence_list

    def get_by_investigation(self, investigation_id: int) -> list[Evidence]:
        return self.db.query(Evidence).filter(
            Evidence.investigation_id == investigation_id
        ).all()