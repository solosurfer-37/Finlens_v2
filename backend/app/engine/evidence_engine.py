
from decimal import Decimal

from sqlalchemy.orm import Session

from app.engine.fraud_signal import FraudSignal
from app.models.evidence import Evidence
from app.repositories.evidence_repository import EvidenceRepository
from app.repositories.investigation_repository import InvestigationRepository

SEVERITY_SCORES = {
    "low": Decimal("5"),
    "medium": Decimal("15"),
    "high": Decimal("30"),
}

MAX_RISK_SCORE = Decimal("100")


class EvidenceEngine:
    """Converts fraud signals into persisted Evidence records and updates the investigation risk score."""

    def __init__(self, db: Session):
        self.db = db
        self.evidence_repo = EvidenceRepository(db)
        self.investigation_repo = InvestigationRepository(db)

    def process(self, investigation_id: int, signals: list[FraudSignal]) -> Decimal:
        """
        Persists all signals as evidence, updates investigation risk score,
        and returns the final risk score.
        """
        evidence_list = [
            Evidence(
                investigation_id=investigation_id,
                detector_name=signal.detector_name,
                description=signal.description,
                severity=signal.severity,
                risk_score_contribution=SEVERITY_SCORES[signal.severity],
                related_account_ids=signal.related_account_ids,
                related_transaction_ids=signal.related_transaction_ids,
            )
            for signal in signals
        ]

        self.evidence_repo.bulk_create(evidence_list)

        total_score = sum((e.risk_score_contribution for e in evidence_list), Decimal("0"))
        final_score = min(total_score, MAX_RISK_SCORE)

        investigation = self.investigation_repo.get_by_id(investigation_id)
        investigation.risk_score = float(final_score)
        investigation.status = "Completed"
        self.db.commit()

        return final_score
