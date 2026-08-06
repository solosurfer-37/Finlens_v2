from collections import defaultdict
from datetime import timedelta

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

VELOCITY_WINDOW = timedelta(hours=1)
VELOCITY_THRESHOLD = 5  # 5+ transactions within the window = suspicious


class VelocityDetector:
    """Flags accounts making an unusually high number of transactions in a short time window."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        sender_txns = defaultdict(list)

        for txn in transactions:
            sender_txns[txn.sender_account_id].append(txn)

        signals = []
        for sender_id, txns in sender_txns.items():
            txns.sort(key=lambda t: t.transaction_time)

            for i in range(len(txns)):
                window_txns = [
                    t for t in txns
                    if txns[i].transaction_time <= t.transaction_time <= txns[i].transaction_time + VELOCITY_WINDOW
                ]
                if len(window_txns) >= VELOCITY_THRESHOLD:
                    signals.append(
                        FraudSignal(
                            detector_name="velocity",
                            description=f"Account {sender_id} made {len(window_txns)} transactions within 1 hour",
                            severity="medium",
                        )
                    )
                    break  # one signal per account is enough

        return signals