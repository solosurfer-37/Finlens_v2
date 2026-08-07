from collections import defaultdict
from decimal import Decimal

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

REPORTING_THRESHOLD = Decimal("1000000")  # 10 lakh
STRUCTURING_LOWER_BOUND = REPORTING_THRESHOLD * Decimal("0.85")  # 85% of threshold
MIN_TRANSACTIONS_FOR_PATTERN = 3


class StructuringDetector:
    """Flags multiple near-threshold transactions between the same sender-receiver pair on the same day."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        pair_day_txns = defaultdict(list)

        for txn in transactions:
            if STRUCTURING_LOWER_BOUND <= txn.amount < REPORTING_THRESHOLD:
                key = (txn.sender_account_id, txn.receiver_account_id, txn.transaction_time.date())
                pair_day_txns[key].append(txn)

        signals = []
        for (sender_id, receiver_id, day), txns in pair_day_txns.items():
            if len(txns) >= MIN_TRANSACTIONS_FOR_PATTERN:
                total = sum(t.amount for t in txns)
                signals.append(
                    FraudSignal(
                        detector_name="structuring",
                        description=f"Account {sender_id} sent {len(txns)} near-threshold transactions to {receiver_id} on {day} (total: {total})",
                        severity="high",
                    )
                )

        return signals