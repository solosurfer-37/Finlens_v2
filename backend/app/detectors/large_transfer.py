from decimal import Decimal

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

LARGE_TRANSFER_THRESHOLD = Decimal("1000000")


class LargeTransferDetector:
    """Flags any single transaction above a fixed threshold."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        signals = []

        for txn in transactions:
            if txn.amount >= LARGE_TRANSFER_THRESHOLD:
                signals.append(
                    FraudSignal(
                        detector_name="large_transfer",
                        description=f"Transaction {txn.transaction_reference} of amount {txn.amount} exceeds threshold",
                        severity="high",
                        related_account_ids=[txn.sender_account_id, txn.receiver_account_id],
                        related_transaction_ids=[txn.id],
                    )
                )

        return signals