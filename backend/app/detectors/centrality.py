from collections import defaultdict

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

MIN_CONNECTIONS = 8  # accounts connected to 8+ unique accounts are hub candidates


class CentralityDetector:
    """Flags accounts that act as a hub — connected to an unusually high number of unique accounts."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        connections = defaultdict(set)

        for txn in transactions:
            connections[txn.sender_account_id].add(txn.receiver_account_id)
            connections[txn.receiver_account_id].add(txn.sender_account_id)

        signals = []
        for account_id, connected_accounts in connections.items():
            degree = len(connected_accounts)
            if degree >= MIN_CONNECTIONS:
                signals.append(
                    FraudSignal(
                        detector_name="centrality",
                        description=f"Account {account_id} is a hub connected to {degree} unique accounts",
                        severity="high",
                    )
                )

        return signals