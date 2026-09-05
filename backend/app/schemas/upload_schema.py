from pydantic import BaseModel


class UploadResponse(BaseModel):
    investigation_id: int
    total_transactions: int
    risk_score: float
    message: str