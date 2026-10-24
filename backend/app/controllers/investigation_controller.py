from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.core.cache import get_cache, set_cache
from app.repositories.investigation_repository import InvestigationRepository
from app.schemas.investigation_schema import InvestigationResponse


class InvestigationController:
    """
    Handles orchestration for investigation-related read operations.
    No business logic here - only wiring + error translation.
    """

    def __init__(self, db: Session):
        self.repository = InvestigationRepository(db)

    def get_investigation(
        self, investigation_id: int, user_id: int
    ) -> InvestigationResponse:
        cache_key = f"investigation:{user_id}:{investigation_id}"
        cached = get_cache(cache_key)
        if cached is not None:
            return InvestigationResponse.model_validate(cached)

        investigation = self.repository.get_by_id_for_user(investigation_id, user_id)

        if investigation is None:
            raise HTTPException(
                status_code=404,
                detail=f"Investigation with id {investigation_id} not found",
            )

        response = InvestigationResponse.model_validate(investigation)
        set_cache(cache_key, response.model_dump(mode="json"), ttl_seconds=300)
        return response

    def list_investigations(self, user_id: int) -> list[InvestigationResponse]:
        investigations = self.repository.get_all_for_user(user_id)
        return [InvestigationResponse.model_validate(inv) for inv in investigations]