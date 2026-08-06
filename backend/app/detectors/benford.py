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

        leading_digits = [int(str(abs(txn.amount))[0]) for txn in transactions]
        counts = Counter(leading_digits)
        total = len(leading_digits)

        signals = []
        for digit in range(1, 10):
            observed = counts.get(digit, 0) / total
            expected = BENFORD_EXPECTED[digit]
            deviation = abs(observed - expected)

            if deviation > DEVIATION_THRESHOLD:
                signals.append(
                    FraudSignal(
                        detector_name="benford",
                        description=f"Leading digit {digit} appears {observed:.1%} of the time (expected {expected:.1%}) — possible manipulated data",
                        severity="medium",
                    )
                )

        return signals