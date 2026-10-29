from datetime import datetime
from decimal import Decimal
from types import SimpleNamespace

from app.detectors.structuring import (
    REPORTING_THRESHOLD,
    STRUCTURING_LOWER_BOUND,
    StructuringDetector,
)


def make_txn(txn_id, amount, sender=1, receiver=2, when="2026-01-01 10:00:00"):
    return SimpleNamespace(
        id=txn_id,
        amount=Decimal(amount),
        sender_account_id=sender,
        receiver_account_id=receiver,
        transaction_time=datetime.fromisoformat(when),
    )


def near_threshold_batch(count, **kwargs):
    return [make_txn(i, "900000", **kwargs) for i in range(1, count + 1)]


def test_two_near_threshold_transactions_not_flagged():
    assert StructuringDetector().detect(near_threshold_batch(2)) == []


def test_three_near_threshold_transactions_flagged():
    signals = StructuringDetector().detect(near_threshold_batch(3))
    assert len(signals) == 1


def test_lower_bound_is_inclusive():
    txns = [make_txn(i, str(STRUCTURING_LOWER_BOUND)) for i in range(1, 4)]
    assert len(StructuringDetector().detect(txns)) == 1


def test_upper_bound_is_exclusive():
    txns = [make_txn(i, str(REPORTING_THRESHOLD)) for i in range(1, 4)]
    assert StructuringDetector().detect(txns) == []


def test_below_lower_bound_not_counted():
    txns = [make_txn(i, "849999.99") for i in range(1, 4)]
    assert StructuringDetector().detect(txns) == []


def test_different_days_or_receivers_do_not_group():
    different_days = [
        make_txn(1, "900000", when="2026-01-01 10:00:00"),
        make_txn(2, "900000", when="2026-01-02 10:00:00"),
        make_txn(3, "900000", when="2026-01-03 10:00:00"),
    ]
    different_receivers = [make_txn(i, "900000", receiver=i + 10) for i in range(1, 4)]
    assert StructuringDetector().detect(different_days) == []
    assert StructuringDetector().detect(different_receivers) == []


def test_signal_fields_and_related_ids():
    signal = StructuringDetector().detect(near_threshold_batch(3))[0]
    assert signal.detector_name == "structuring"
    assert signal.severity == "high"
    assert "2700000" in signal.description
    assert signal.related_account_ids == [1, 2]
    assert sorted(signal.related_transaction_ids) == [1, 2, 3]