from datetime import datetime

from pydantic import BaseModel, ConfigDict


class ReportResponse(BaseModel):
    id: int
    investigation_id: int
    summary_text: str
    severity_breakdown: dict
    total_evidence_count: int
    risk_score_snapshot: float
    generated_at: datetime

    model_config = ConfigDict(from_attributes=True)