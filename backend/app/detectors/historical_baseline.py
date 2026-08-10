from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

DEVIATION_MULTIPLIER = Decimal("3")  # 3x above account's historical average = suspicious
MIN_HISTORY_COUNT = 5  # need at least 5 past transactions to trust the baseline


class HistoricalBaselineDetector:
    """Flags transactions that deviate significantly from an account's historical average."""

    def __init__(self, db: Session):
        self.db = db

    def _get_historical_average(self, account_id: int) -> tuple[Decimal, int]:
        result = (
            self.db.query(
                func.avg(Transaction.amount),
                func.count(Transaction.id),
            )
            .filter(Transaction.sender_account_id == account_id)
            .first()
        )
        avg_amount, count = result
        return (avg_amount or Decimal("0"), count or 0)

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        signals = []
        checked_accounts = set()

        for txn in transactions:
            if txn.sender_account_id in checked_accounts:
                continue
            checked_accounts.add(txn.sender_account_id)

            avg_amount, history_count = self._get_historical_average(txn.sender_account_id)

            if history_count < MIN_HISTORY_COUNT:
                continue  # not enough history to trust this baseline

            if txn.amount > avg_amount * DEVIATION_MULTIPLIER:
                signals.append(
                    FraudSignal(
                        detector_name="historical_baseline",
                        description=f"Transaction {txn.transaction_reference} of {txn.amount} is {DEVIATION_MULTIPLIER}x above account {txn.sender_account_id}'s historical average ({avg_amount:.2f})",
                        severity="medium",
                    )
                )

        return signals