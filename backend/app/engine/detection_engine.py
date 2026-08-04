from sqlalchemy.orm import Session

from app.engine.fraud_signal import FraudSignal
from app.detectors.large_transfer import LargeTransferDetector
from app.models.transaction import Transaction


class DetectionEngine:
    def __init__(self, db: Session):
        self.db = db
        self.detectors = [
            LargeTransferDetector(),
        ]

    def run(self, transactions: list[Transaction]) -> list[FraudSignal]:
        signals: list[FraudSignal] = []
        for detector in self.detectors:
            signals.extend(detector.detect(transactions))
        return signals