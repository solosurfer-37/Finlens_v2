from types import SimpleNamespace

from app.detectors.fan_out import FAN_OUT_THRESHOLD, FanOutDetector


def make_txn(sender: int, receiver: int, txn_id: int) -> SimpleNamespace:
    return SimpleNamespace(id=txn_id, sender_account_id=sender, receiver_account_id=receiver)


def fan_out_txns(sender: int, receiver_count: int, start_id: int = 1) -> list[SimpleNamespace]:
    return [make_txn(sender, 100 + i, start_id + i) for i in range(receiver_count)]


def test_empty_transactions_returns_no_signals():
    assert FanOutDetector().detect([]) == []


def test_below_threshold_not_flagged():
    txns = fan_out_txns(1, FAN_OUT_THRESHOLD - 1)
    assert FanOutDetector().detect(txns) == []


def test_exactly_threshold_is_flagged():
    txns = fan_out_txns(1, FAN_OUT_THRESHOLD)
    signals = FanOutDetector().detect(txns)

    assert len(signals) == 1
    assert signals[0].detector_name == "fan_out"
    assert signals[0].severity == "medium"
    assert "Account 1" in signals[0].description


def test_above_threshold_is_flagged_once():
    txns = fan_out_txns(1, FAN_OUT_THRESHOLD + 1)
    signals = FanOutDetector().detect(txns)

    assert len(signals) == 1
    assert f"{FAN_OUT_THRESHOLD + 1} unique accounts" in signals[0].description


def test_repeat_transfers_to_same_receivers_not_counted_twice():
    txns = [make_txn(1, 200 + (i % 2), i) for i in range(20)]
    assert FanOutDetector().detect(txns) == []


def test_senders_are_counted_independently():
    txns = fan_out_txns(1, FAN_OUT_THRESHOLD) + fan_out_txns(2, FAN_OUT_THRESHOLD - 1, start_id=100)
    signals = FanOutDetector().detect(txns)

    assert len(signals) == 1
    assert "Account 1" in signals[0].description


def test_related_account_ids_are_sender_and_all_receivers():
    signals = FanOutDetector().detect(fan_out_txns(1, FAN_OUT_THRESHOLD))

    expected = [1] + [100 + i for i in range(FAN_OUT_THRESHOLD)]
    assert signals[0].related_account_ids == expected


def test_related_transaction_ids_only_include_flagged_senders_transactions():
    txns = fan_out_txns(1, FAN_OUT_THRESHOLD) + fan_out_txns(2, 2, start_id=100)
    signals = FanOutDetector().detect(txns)

    assert signals[0].related_transaction_ids == list(range(1, FAN_OUT_THRESHOLD + 1))