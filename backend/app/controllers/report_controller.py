from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.repositories.report_repository import ReportRepository
from app.schemas.report_schema import ReportResponse


class ReportController:
    """
    Handles orchestration for report-related read operations.
    No business logic here — only wiring + error translation.
    """

    def __init__(self, db: Session):
        self.repository = ReportRepository(db)

    def get_report(self, investigation_id: int) -> ReportResponse:
        report = self.repository.get_by_investigation(investigation_id)

        if report is None:
            raise HTTPException(
                status_code=404,
                detail=f"No report found for investigation {investigation_id}",
            )

        return ReportResponse.model_validate(report)