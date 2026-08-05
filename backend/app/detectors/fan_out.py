from collections import defaultdict

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

FAN_OUT_THRESHOLD = 5  # sender sending to 5+ unique receivers = suspicious


class FanOutDetector:
    """Flags accounts that send money to an unusually high number of unique receivers."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        sender_to_receivers = defaultdict(set)

        for txn in transactions:
            sender_to_receivers[txn.sender_account_id].add(txn.receiver_account_id)

        signals = []
        for sender_id, receivers in sender_to_receivers.items():
            if len(receivers) >= FAN_OUT_THRESHOLD:
                signals.append(
                    FraudSignal(
                        detector_name="fan_out",
                        description=f"Account {sender_id} sent money to {len(receivers)} unique accounts",
                        severity="medium",
                    )
                )

        return signals