from types import SimpleNamespace

from app.detectors.cycle_detection import CycleDetectionDetector


def make_txn(sender: int, receiver: int) -> SimpleNamespace:
    return SimpleNamespace(sender_account_id=sender, receiver_account_id=receiver)


def edges(*pairs: tuple[int, int]) -> list[SimpleNamespace]:
    return [make_txn(s, r) for s, r in pairs]


def test_empty_transactions_returns_no_signals():
    assert CycleDetectionDetector().detect([]) == []


def test_linear_chain_has_no_cycle():
    txns = edges((1, 2), (2, 3), (3, 4))
    assert CycleDetectionDetector().detect(txns) == []


def test_two_node_cycle_is_flagged():
    signals = CycleDetectionDetector().detect(edges((1, 2), (2, 1)))

    assert len(signals) == 1
    assert signals[0].detector_name == "cycle_detection"
    assert signals[0].severity == "high"
    assert "1 -> 2" in signals[0].description


def test_three_node_cycle_is_flagged_once():
    signals = CycleDetectionDetector().detect(edges((1, 2), (2, 3), (3, 1)))

    assert len(signals) == 1
    assert "1 -> 2 -> 3" in signals[0].description


def test_self_loop_is_ignored():
    assert CycleDetectionDetector().detect(edges((1, 1))) == []


def test_node_feeding_into_cycle_is_not_flagged():
    txns = edges((4, 1), (1, 2), (2, 3), (3, 1))
    signals = CycleDetectionDetector().detect(txns)

    assert len(signals) == 1
    assert "4" not in signals[0].description


def test_two_disjoint_cycles_give_two_signals():
    txns = edges((1, 2), (2, 1), (10, 11), (11, 10))
    signals = CycleDetectionDetector().detect(txns)

    assert len(signals) == 2


def test_duplicate_edges_do_not_create_extra_signals():
    txns = edges((1, 2), (2, 1), (1, 2), (2, 1), (1, 2))
    assert len(CycleDetectionDetector().detect(txns)) == 1