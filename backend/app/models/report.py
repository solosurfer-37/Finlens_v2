from datetime import datetime

from sqlalchemy import String, DateTime, ForeignKey, JSON, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.sql import func

from app.database.base import Base


class Report(Base):
    __tablename__ = "reports"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    investigation_id: Mapped[int] = mapped_column(ForeignKey("investigations.id"), index=True)

    summary_text: Mapped[str] = mapped_column(Text)
    severity_breakdown: Mapped[dict] = mapped_column(JSON)
    total_evidence_count: Mapped[int] = mapped_column()
    risk_score_snapshot: Mapped[float] = mapped_column()

    generated_at: Mapped[datetime] = mapped_column(DateTime, server_default=func.now())

    investigation = relationship("Investigation", lazy="raise")