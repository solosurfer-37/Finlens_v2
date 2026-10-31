from types import SimpleNamespace

from app.detectors.cycle_detection import MAX_CYCLES, CycleDetectionDetector


def make_txn(sender: int, receiver: int, txn_id: int) -> SimpleNamespace:
    return SimpleNamespace(id=txn_id, sender_account_id=sender, receiver_account_id=receiver)


def edges(*pairs: tuple[int, int]) -> list[SimpleNamespace]:
    return [make_txn(s, r, i + 1) for i, (s, r) in enumerate(pairs)]


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


def test_related_account_ids_are_the_cycle_nodes():
    signals = CycleDetectionDetector().detect(edges((1, 2), (2, 3), (3, 1)))

    assert signals[0].related_account_ids == [1, 2, 3]


def test_related_transaction_ids_cover_all_cycle_edges():
    signals = CycleDetectionDetector().detect(edges((1, 2), (2, 3), (3, 1)))

    assert sorted(signals[0].related_transaction_ids) == [1, 2, 3]


def test_transaction_feeding_into_cycle_is_not_related():
    txns = edges((4, 1), (1, 2), (2, 3), (3, 1))
    signals = CycleDetectionDetector().detect(txns)

    assert 1 not in signals[0].related_transaction_ids
    assert sorted(signals[0].related_transaction_ids) == [2, 3, 4]


def test_multiple_cycles_through_same_start_node_are_all_found():
    signals = CycleDetectionDetector().detect(edges((1, 2), (2, 1), (1, 3), (3, 1)))
    descriptions = [s.description for s in signals]

    assert len(signals) == 2
    assert any("1 -> 2" in d for d in descriptions)
    assert any("1 -> 3" in d for d in descriptions)


def test_cycles_with_same_nodes_but_different_order_are_distinct():
    txns = edges((1, 2), (2, 3), (3, 4), (4, 1), (1, 3), (3, 2), (2, 4))
    signals = CycleDetectionDetector().detect(txns)
    paths = {tuple(s.related_account_ids) for s in signals}

    assert (1, 2, 3, 4) in paths
    assert (1, 3, 2, 4) in paths


def test_cycle_count_is_capped():
    nodes = range(1, 8)
    pairs = [(a, b) for a in nodes for b in nodes if a != b]
    signals = CycleDetectionDetector().detect(edges(*pairs))

    assert len(signals) == MAX_CYCLES