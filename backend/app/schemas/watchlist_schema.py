from datetime import datetime

from pydantic import BaseModel, ConfigDict


class WatchlistEntryCreate(BaseModel):
    account_number: str
    reason: str


class WatchlistEntryResponse(BaseModel):
    id: int
    account_number: str
    reason: str
    added_at: datetime

    model_config = ConfigDict(from_attributes=True)