from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.core.time import utc_now
from app.database.base import Base

if TYPE_CHECKING:
    from app.models.transaction import Transaction


class Account(Base):
    """
    Represents a bank account owned by one user's data scope.

    The same account number may exist for different users;
    it is unique only within a single user.
    """

    __tablename__ = "accounts"

    __table_args__ = (
        UniqueConstraint(
            "user_id",
            "account_number",
            name="uq_account_user_account_number",
        ),
    )

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

    account_number: Mapped[str] = mapped_column(
        String(100),
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
        default=utc_now,
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