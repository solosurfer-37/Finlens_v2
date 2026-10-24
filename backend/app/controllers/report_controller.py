from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.cache import get_cache, set_cache
from app.repositories.investigation_repository import InvestigationRepository
from app.repositories.report_repository import ReportRepository
from app.schemas.report_schema import ReportResponse


class ReportController:
    """
    Handles orchestration for report-related read operations.
    No business logic here - only wiring + error translation.
    Ownership is verified before the cache is consulted.
    Results are cached in Redis per user since AI-generated reports are static.
    """

    def __init__(self, db: Session):
        self.repository = ReportRepository(db)
        self.investigation_repo = InvestigationRepository(db)

    def get_report(self, investigation_id: int, user_id: int) -> ReportResponse:
        investigation = self.investigation_repo.get_by_id_for_user(
            investigation_id, user_id
        )
        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail=f"Investigation with id {investigation_id} not found",
            )

        cache_key = f"report:{user_id}:{investigation_id}"
        cached = get_cache(cache_key)
        if cached is not None:
            return ReportResponse.model_validate(cached)

        report = self.repository.get_by_investigation(investigation_id)

        if report is None:
            raise HTTPException(
                status_code=404,
                detail=f"No report found for investigation {investigation_id}",
            )

        response = ReportResponse.model_validate(report)
        set_cache(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
        return response