from sqlalchemy.orm import Session

from app.models.report import Report


class ReportRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, report: Report) -> Report:
        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)
        return report

    def get_by_investigation(self, investigation_id: int) -> Report | None:
        return self.db.query(Report).filter(
            Report.investigation_id == investigation_id
        ).order_by(Report.generated_at.desc()).first()