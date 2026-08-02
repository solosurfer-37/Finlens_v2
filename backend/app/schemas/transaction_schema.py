from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, Field


class TransactionCreate(BaseModel):
    """Data required to create a transaction (e.g. from parsed CSV row)."""
    transaction_reference: str
    investigation_id: int
    sender_account_id: int
    receiver_account_id: int
    amount: Decimal = Field(gt=0)
    currency: str = "INR"
    transaction_time: datetime


class TransactionResponse(BaseModel):
    id: int
    transaction_reference: str
    investigation_id: int
    sender_account_id: int
    receiver_account_id: int
    amount: Decimal
    currency: str
    transaction_time: datetime
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)