from sqlalchemy.orm import Session

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction
from app.repositories.account_repository import AccountRepository
from app.repositories.watchlist_repository import WatchlistRepository


class WatchlistDetector:
    """Flags transactions involving accounts on the watchlist."""

    def __init__(self, db: Session):
        self.db = db
        self.watchlist_repo = WatchlistRepository(db)
        self.account_repo = AccountRepository(db)

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        flagged_numbers = self.watchlist_repo.get_all_flagged_numbers()
        if not flagged_numbers:
            return []

        account_ids = set()
        for txn in transactions:
            account_ids.add(txn.sender_account_id)
            account_ids.add(txn.receiver_account_id)
        accounts = self.account_repo.get_by_ids(account_ids)

        signals = []
        for txn in transactions:
            sender = accounts.get(txn.sender_account_id)
            receiver = accounts.get(txn.receiver_account_id)
            related_accounts = [txn.sender_account_id, txn.receiver_account_id]

            if sender and sender.account_number in flagged_numbers:
                signals.append(
                    FraudSignal(
                        detector_name="watchlist",
                        description=f"Transaction {txn.transaction_reference} involves watchlisted sender {sender.account_number}",
                        severity="high",
                        related_account_ids=related_accounts,
                        related_transaction_ids=[txn.id],
                    )
                )

            if receiver and receiver.account_number in flagged_numbers:
                signals.append(
                    FraudSignal(
                        detector_name="watchlist",
                        description=f"Transaction {txn.transaction_reference} involves watchlisted receiver {receiver.account_number}",
                        severity="high",
                        related_account_ids=related_accounts,
                        related_transaction_ids=[txn.id],
                    )
                )

        return signals