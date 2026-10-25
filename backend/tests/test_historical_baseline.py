from decimal import Decimal
from types import SimpleNamespace

from app.detectors.historical_baseline import (
    DEVIATION_MULTIPLIER,
    MIN_HISTORY_COUNT,
    HistoricalBaselineDetector,
)


class FakeQuery:
    def __init__(self, row):
        self.row = row

    def filter(self, *args):
        return self

    def first(self):
        return self.row


class FakeDB:
    def __init__(self, row):
        self.row = row

    def query(self, *args):
        return FakeQuery(self.row)


def make_detector(history: dict[int, tuple[Decimal, int]]) -> HistoricalBaselineDetector:
    detector = HistoricalBaselineDetector(db=None)
    detector._get_historical_average = lambda account_id: history.get(
        account_id, (Decimal("0"), 0)
    )
    return detector


def make_txn(ref: str, sender: int, amount: str) -> SimpleNamespace:
    return SimpleNamespace(
        transaction_reference=ref,
        sender_account_id=sender,
        amount=Decimal(amount),
    )


AVG = Decimal("100")


def test_empty_transactions_returns_no_signals():
    assert make_detector({}).detect([]) == []


def test_history_below_minimum_is_not_trusted():
    detector = make_detector({1: (AVG, MIN_HISTORY_COUNT - 1)})
    assert detector.detect([make_txn("T1", 1, "100000")]) == []


def test_no_history_returns_nothing():
    assert make_detector({}).detect([make_txn("T1", 1, "100000")]) == []


def test_exactly_min_history_with_big_amount_is_flagged():
    detector = make_detector({1: (AVG, MIN_HISTORY_COUNT)})
    signals = detector.detect([make_txn("T1", 1, "301")])

    assert len(signals) == 1
    assert signals[0].detector_name == "historical_baseline"
    assert signals[0].severity == "medium"
    assert "T1" in signals[0].description
    assert "3x" in signals[0].description


def test_exactly_multiplier_is_not_flagged():
    detector = make_detector({1: (AVG, 10)})
    amount = str(AVG * DEVIATION_MULTIPLIER)
    assert detector.detect([make_txn("T1", 1, amount)]) == []


def test_normal_amount_is_not_flagged():
    detector = make_detector({1: (AVG, 10)})
    assert detector.detect([make_txn("T1", 1, "120")]) == []


def test_each_sender_is_checked_with_own_baseline():
    detector = make_detector({1: (AVG, 10), 2: (Decimal("1000"), 10)})
    txns = [make_txn("T1", 1, "500"), make_txn("T2", 2, "500")]
    signals = detector.detect(txns)

    assert len(signals) == 1
    assert "T1" in signals[0].description


def test_only_first_transaction_per_sender_is_checked_known_gap():
    # Known gap: later transactions from the same sender are skipped.
    # When fixed, this should return 1 signal for T2 and the assertion must change.
    detector = make_detector({1: (AVG, 10)})
    txns = [make_txn("T1", 1, "100"), make_txn("T2", 1, "10000")]

    assert detector.detect(txns) == []


def test_historical_average_handles_no_rows():
    detector = HistoricalBaselineDetector(FakeDB((None, None)))
    assert detector._get_historical_average(1) == (Decimal("0"), 0)


def test_historical_average_returns_db_values():
    detector = HistoricalBaselineDetector(FakeDB((Decimal("250.50"), 7)))
    assert detector._get_historical_average(1) == (Decimal("250.50"), 7)