from datetime import datetime, timedelta
from decimal import Decimal
from types import SimpleNamespace

from app.detectors.velocity import VELOCITY_WINDOW, VelocityDetector

BASE = datetime.fromisoformat("2026-01-01 10:00:00")


def make_txn(txn_id, offset_minutes, sender=1, receiver=2):
    return SimpleNamespace(
        id=txn_id,
        amount=Decimal("100"),
        sender_account_id=sender,
        receiver_account_id=receiver,
        transaction_time=BASE + timedelta(minutes=offset_minutes),
    )


def burst(count, step_minutes=1, sender=1):
    return [make_txn(i, i * step_minutes, sender=sender) for i in range(count)]


def test_four_transactions_in_window_not_flagged():
    assert VelocityDetector().detect(burst(4)) == []


def test_five_transactions_in_window_flagged():
    assert len(VelocityDetector().detect(burst(5))) == 1


def test_window_end_is_inclusive():
    # first at 0 min, fifth exactly at 60 min -> still inside the window
    minutes = [0, 15, 30, 45, int(VELOCITY_WINDOW.total_seconds() // 60)]
    txns = [make_txn(i, m) for i, m in enumerate(minutes)]
    assert len(VelocityDetector().detect(txns)) == 1


def test_just_outside_window_not_flagged():
    minutes = [0, 15, 30, 45, 61]
    txns = [make_txn(i, m) for i, m in enumerate(minutes)]
    assert VelocityDetector().detect(txns) == []


def test_one_signal_per_account_even_with_many_transactions():
    assert len(VelocityDetector().detect(burst(10))) == 1


def test_different_senders_do_not_mix():
    txns = [make_txn(i, i, sender=i) for i in range(1, 6)]
    assert VelocityDetector().detect(txns) == []


def test_unsorted_input_is_handled():
    txns = list(reversed(burst(5)))
    assert len(VelocityDetector().detect(txns)) == 1


def test_signal_fields_and_known_gap_in_related_ids():
    signal = VelocityDetector().detect(burst(5))[0]
    assert signal.detector_name == "velocity"
    assert signal.severity == "medium"
    assert "5 transactions" in signal.description
    # Known tech debt: velocity does not populate related ids yet.
    assert not signal.related_account_ids
    assert not signal.related_transaction_ids