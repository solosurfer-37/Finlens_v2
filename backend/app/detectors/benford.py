import math
from collections import Counter

from app.engine.fraud_signal import FraudSignal
from app.models.transaction import Transaction

# Benford's expected probability for each leading digit (1-9)
BENFORD_EXPECTED = {d: math.log10(1 + 1 / d) for d in range(1, 10)}

DEVIATION_THRESHOLD = 0.15  # 15% deviation from expected = suspicious
MIN_TRANSACTIONS = 30  # Benford's law needs a reasonable sample size


class BenfordDetector:
    """Flags investigations where transaction amounts deviate from Benford's Law."""

    def detect(self, transactions: list[Transaction]) -> list[FraudSignal]:
        if len(transactions) < MIN_TRANSACTIONS:
            return []  # not enough data for a statistically meaningful check

        txns_with_digit = [
            (txn, self._leading_digit(txn.amount)) for txn in transactions
        ]
        txns_with_digit = [(txn, d) for txn, d in txns_with_digit if d]
        total = len(txns_with_digit)
        if total == 0:
            return []  # all amounts were zero, nothing to analyse

        counts = Counter(d for _, d in txns_with_digit)

        signals = []
        for digit in range(1, 10):
            observed = counts.get(digit, 0) / total
            expected = BENFORD_EXPECTED[digit]
            deviation = abs(observed - expected)

            if deviation > DEVIATION_THRESHOLD:
                account_ids: list[int] = []
                txn_ids: list[int] = []
                if observed > expected:
                    # Only over-represented digits point at concrete transactions.
                    flagged = [txn for txn, d in txns_with_digit if d == digit]
                    txn_ids = [txn.id for txn in flagged]
                    account_ids = sorted(
                        {a for txn in flagged for a in (txn.sender_account_id, txn.receiver_account_id)}
                    )
                signals.append(
                    FraudSignal(
                        detector_name="benford",
                        description=f"Leading digit {digit} appears {observed:.1%} of the time (expected {expected:.1%}) - possible manipulated data",
                        severity="medium",
                        related_account_ids=account_ids,
                        related_transaction_ids=txn_ids,
                    )
                )

        return signals

    @staticmethod
    def _leading_digit(amount) -> int:
        """First significant (non-zero) digit of the absolute amount, 0 if none."""
        for ch in str(abs(amount)):
            if ch in "123456789":
                return int(ch)
        return 0