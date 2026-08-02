from datetime import datetime

from pydantic import BaseModel, ConfigDict


class InvestigationCreate(BaseModel):
    """Data required to create a new investigation (e.g. on CSV upload)."""
    filename: str


class InvestigationResponse(BaseModel):
    """Data sent back to client — never expose raw ORM object directly."""
    id: int
    filename: str
    status: str
    total_transactions: int
    risk_score: float
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)