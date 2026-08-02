from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AccountCreate(BaseModel):
    """Data required to create a new account (e.g. parsed from CSV row)."""
    account_number: str
    account_holder: str
    bank_name: str


class AccountResponse(BaseModel):
    id: int
    account_number: str
    account_holder: str
    bank_name: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)