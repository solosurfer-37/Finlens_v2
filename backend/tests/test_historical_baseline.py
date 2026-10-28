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
    detector.lookups = []

    def fake_average(account_id):
        detector.lookups.append(account_id)
        return history.get(account_id, (Decimal("0"), 0))

    detector._get_historical_average = fake_average
    return detector


def make_txn(ref: str, sender: int, amount: str, receiver: int = 99, txn_id: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        id=txn_id,
        transaction_reference=ref,
        sender_account_id=sender,
        receiver_account_id=receiver,
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


def test_every_transaction_of_a_sender_is_checked():
    detector = make_detector({1: (AVG, 10)})
    txns = [make_txn("T1", 1, "100"), make_txn("T2", 1, "10000")]
    signals = detector.detect(txns)

    assert len(signals) == 1
    assert "T2" in signals[0].description


def test_baseline_is_looked_up_once_per_sender():
    detector = make_detector({1: (AVG, 10)})
    txns = [make_txn(f"T{i}", 1, "100") for i in range(5)]
    detector.detect(txns)

    assert detector.lookups == [1]


def test_related_ids_cover_sender_receiver_and_transaction():
    detector = make_detector({1: (AVG, 10)})
    signals = detector.detect([make_txn("T1", 1, "10000", receiver=7, txn_id=42)])

    assert signals[0].related_account_ids == [1, 7]
    assert signals[0].related_transaction_ids == [42]


def test_historical_average_handles_no_rows():
    detector = HistoricalBaselineDetector(FakeDB((None, None)))
    assert detector._get_historical_average(1) == (Decimal("0"), 0)


def test_historical_average_returns_db_values():
    detector = HistoricalBaselineDetector(FakeDB((Decimal("250.50"), 7)))
    assert detector._get_historical_average(1) == (Decimal("250.50"), 7)