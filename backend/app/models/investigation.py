from datetime import datetime

from sqlalchemy import DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base


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
        default=datetime.utcnow,
        nullable=False,
    )

    updated_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow,
        nullable=False,
    )