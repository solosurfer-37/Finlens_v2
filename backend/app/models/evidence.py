from datetime import datetime
from decimal import Decimal

from sqlalchemy import String, DateTime, Numeric, ForeignKey, ARRAY, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Evidence(Base):
    __tablename__ = "evidence"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)

    detector_name: Mapped[str] = mapped_column(String)
    description: Mapped[str] = mapped_column(String)
    severity: Mapped[str] = mapped_column(String)
    risk_score_contribution: Mapped[Decimal] = mapped_column(Numeric(5, 2))

    related_account_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)
    related_transaction_ids: Mapped[list[int]] = mapped_column(ARRAY(Integer), default=list)

    created_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    investigation = relationship("Investigation", lazy="raise")
