from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Account(Base):
    """
    Represents a bank account involved in one or more investigations.

    An account can act as a sender or receiver
    in multiple transactions.
    """

    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    account_number: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
        index=True,
    )

    account_holder: Mapped[str] = mapped_column(
        String(255),
        nullable=False,
    )

    bank_name: Mapped[str] = mapped_column(
        String(150),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    sent_transactions: Mapped[list["Transaction"]] = relationship(
        foreign_keys="Transaction.sender_account_id",
        back_populates="sender_account",
        lazy="raise",
    )

    received_transactions: Mapped[list["Transaction"]] = relationship(
        foreign_keys="Transaction.receiver_account_id",
        back_populates="receiver_account",
        lazy="raise",
    )