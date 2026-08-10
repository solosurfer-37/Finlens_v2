from sqlalchemy.orm import Session
from app.detectors.fan_out import FanOutDetector
from app.engine.fraud_signal import FraudSignal
from app.detectors.large_transfer import LargeTransferDetector
from app.models.transaction import Transaction
from app.detectors.velocity import VelocityDetector
from app.detectors.cycle_detection import CycleDetectionDetector
from app.detectors.benford import BenfordDetector
from app.detectors.structuring import StructuringDetector
from app.detectors.dsu import DSUDetector
from app.detectors.centrality import CentralityDetector
from app.detectors.watchlist import WatchlistDetector
from app.detectors.historical_baseline import HistoricalBaselineDetector

class DetectionEngine:
    def __init__(self, db: Session):
        self.db = db
        self.detectors = [
           LargeTransferDetector(),
           FanOutDetector(),
           VelocityDetector(),
           CycleDetectionDetector(),
           BenfordDetector(),
           StructuringDetector(),
           DSUDetector(),
           CentralityDetector(),
           WatchlistDetector(self.db),
           HistoricalBaselineDetector(self.db),

        ]

    def run(self, transactions: list[Transaction]) -> list[FraudSignal]:
        signals: list[FraudSignal] = []
        for detector in self.detectors:
            signals.extend(detector.detect(transactions))
        return signals