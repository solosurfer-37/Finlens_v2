from datetime import datetime

from decimal import Decimal

from sqlalchemy import (
    DateTime,
    ForeignKey,
    Integer,
    Numeric,
    String,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database.base import Base




class Transaction(Base):
    """
    Represents a single financial transaction.
    """

    __tablename__ = "transactions"

    __table_args__ = (
        UniqueConstraint(
            "investigation_id",
            "transaction_reference",
            name="uq_investigation_transaction_reference",
        ),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
        index=True,
    )

    transaction_reference: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
        index=True,
    )

    investigation_id: Mapped[int] = mapped_column(
        ForeignKey("investigations.id"),
        nullable=False,
        index=True,
    )

    sender_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )

    receiver_account_id: Mapped[int] = mapped_column(
        ForeignKey("accounts.id"),
        nullable=False,
        index=True,
    )

    amount: Mapped[Decimal] = mapped_column(
        Numeric(18, 2),
        nullable=False,
    )

    currency: Mapped[str] = mapped_column(
        String(10),
        default="INR",
        nullable=False,
    )

    transaction_time: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )


from sqlalchemy.orm import relationship

investigation: Mapped["Investigation"] = relationship(
    back_populates="transactions",
    lazy="raise",
)

sender_account: Mapped["Account"] = relationship(
    foreign_keys="Transaction.sender_account_id",
    back_populates="sent_transactions",
    lazy="raise",
)

receiver_account: Mapped["Account"] = relationship(
    foreign_keys="Transaction.receiver_account_id",
    back_populates="received_transactions",
    lazy="raise",
)