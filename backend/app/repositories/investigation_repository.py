from sqlalchemy.orm import Session

from app.models.investigation import Investigation
from app.schemas.investigation_schema import InvestigationCreate


class InvestigationRepository:
    """
    Handles all direct database access for Investigation.
    No business logic here — only queries.
    """

    def __init__(self, db: Session):
        self.db = db

    def create(self, data: InvestigationCreate) -> Investigation:
        investigation = Investigation(filename=data.filename)
        self.db.add(investigation)
        self.db.commit()
        self.db.refresh(investigation)
        return investigation

    def get_by_id(self, investigation_id: int) -> Investigation | None:
        return self.db.get(Investigation, investigation_id)

    def get_all(self) -> list[Investigation]:
        return self.db.query(Investigation).all()

    def update_transaction_count(self, investigation_id: int, count: int) -> None:
        investigation = self.db.get(Investigation, investigation_id)
        if investigation:
            investigation.total_transactions = count
            self.db.commit()

    def delete(self, investigation: Investigation) -> None:
        self.db.delete(investigation)
        self.db.commit()