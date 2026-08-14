from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict


class EvidenceResponse(BaseModel):
    id: int
    investigation_id: int
    detector_name: str
    description: str
    severity: str
    risk_score_contribution: Decimal
    related_account_ids: list[int]
    related_transaction_ids: list[int]
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)