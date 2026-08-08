from sqlalchemy.orm import Session

from app.engine.fraud_signal import FraudSignal
from app.models.account import Account
from app.models.transaction import Transaction
from app.repositories.watchlist_repository import WatchlistRepository

class WatchlistDetector:
    """Flags transactions involving accounts on the watchlist."""

    def __init__(self, db: Session):
        self.db = db
        self.watchlist_repo = WatchlistRepository(db)

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        flagged_numbers = self.watchlist_repo.get_all_flagged_numbers()
        if not flagged_numbers:
            return []

        signals = []
        for txn in transactions:
            sender = self.db.get(Account, txn.sender_account_id)
            receiver = self.db.get(Account, txn.receiver_account_id)

            if sender and sender.account_number in flagged_numbers:
                signals.append(
                    FraudSignal(
                        detector_name="watchlist",
                        description=f"Transaction {txn.transaction_reference} involves watchlisted sender {sender.account_number}",
                        severity="high",
                    )
                )

            if receiver and receiver.account_number in flagged_numbers:
                signals.append(
                    FraudSignal(
                        detector_name="watchlist",
                        description=f"Transaction {txn.transaction_reference} involves watchlisted receiver {receiver.account_number}",
                        severity="high",
                    )
                )

        return signals