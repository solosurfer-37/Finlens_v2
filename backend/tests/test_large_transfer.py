from decimal import Decimal
from types import SimpleNamespace

from app.detectors.large_transfer import (
    LARGE_TRANSFER_THRESHOLD,
    LargeTransferDetector,
)


def make_txn(txn_id, amount, ref="TX", sender=1, receiver=2):
    return SimpleNamespace(
        id=txn_id,
        transaction_reference=ref,
        amount=Decimal(amount),
        sender_account_id=sender,
        receiver_account_id=receiver,
    )


def test_below_threshold_not_flagged():
    signals = LargeTransferDetector().detect([make_txn(1, "999999.99")])
    assert signals == []


def test_exactly_threshold_is_flagged():
    signals = LargeTransferDetector().detect([make_txn(1, str(LARGE_TRANSFER_THRESHOLD))])
    assert len(signals) == 1


def test_signal_fields_are_correct():
    txn = make_txn(7, "1200000", ref="TX-BIG", sender=10, receiver=20)
    signal = LargeTransferDetector().detect([txn])[0]
    assert signal.detector_name == "large_transfer"
    assert signal.severity == "high"
    assert signal.related_account_ids == [10, 20]
    assert signal.related_transaction_ids == [7]
    assert "TX-BIG" in signal.description


def test_only_large_transactions_flagged_in_mixed_list():
    txns = [make_txn(1, "500"), make_txn(2, "2000000"), make_txn(3, "10")]
    signals = LargeTransferDetector().detect(txns)
    assert [s.related_transaction_ids for s in signals] == [[2]]
    assert LargeTransferDetector().detect([]) == []