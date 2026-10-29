from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Investigation(Base):
    """
    Represents a single financial investigation.

    Every uploaded CSV creates one Investigation.
    All transactions, evidence, reports, and fraud signals
    belong to an investigation.
    """

    __tablename__ = "investigations"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id"),
        nullable=False,
        index=True,
    )

    filename: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    status: Mapped[str] = mapped_column(
        String(50),
        default="Processing",
        nullable=False,
    )

    total_transactions: Mapped[int] = mapped_column(
        Integer,
        default=0,
        nullable=False,
    )

    risk_score: Mapped[float] = mapped_column(
        Float,
        default=0.0,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=utc_now,
        onupdate=utc_now,
        nullable=False,
    )

    transactions: Mapped[list["Transaction"]] = relationship(
        back_populates="investigation",
        lazy="raise",
    )