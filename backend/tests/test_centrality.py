from types import SimpleNamespace

from app.detectors.centrality import MIN_CONNECTIONS, CentralityDetector


def make_txn(sender: int, receiver: int, txn_id: int = 0) -> SimpleNamespace:
    return SimpleNamespace(id=txn_id, sender_account_id=sender, receiver_account_id=receiver)


def outgoing(hub: int, count: int, base: int = 100, start_id: int = 1) -> list[SimpleNamespace]:
    return [make_txn(hub, base + i, start_id + i) for i in range(count)]


def incoming(hub: int, count: int, base: int = 100, start_id: int = 1) -> list[SimpleNamespace]:
    return [make_txn(base + i, hub, start_id + i) for i in range(count)]


def test_empty_transactions_returns_no_signals():
    assert CentralityDetector().detect([]) == []


def test_below_threshold_not_flagged():
    assert CentralityDetector().detect(outgoing(1, MIN_CONNECTIONS - 1)) == []


def test_exactly_threshold_flags_only_the_hub():
    signals = CentralityDetector().detect(outgoing(1, MIN_CONNECTIONS))

    assert len(signals) == 1
    assert signals[0].detector_name == "centrality"
    assert signals[0].severity == "high"
    assert "Account 1 " in signals[0].description
    assert f"{MIN_CONNECTIONS} unique accounts" in signals[0].description


def test_above_threshold_is_flagged():
    signals = CentralityDetector().detect(outgoing(1, MIN_CONNECTIONS + 1))

    assert len(signals) == 1
    assert f"{MIN_CONNECTIONS + 1} unique accounts" in signals[0].description


def test_incoming_connections_count_too():
    signals = CentralityDetector().detect(incoming(1, MIN_CONNECTIONS))

    assert len(signals) == 1
    assert "Account 1 " in signals[0].description


def test_mixed_direction_connections_are_combined():
    half = MIN_CONNECTIONS // 2
    txns = outgoing(1, half) + incoming(1, MIN_CONNECTIONS - half, base=500, start_id=50)
    signals = CentralityDetector().detect(txns)

    assert len(signals) == 1


def test_repeat_transfers_with_same_neighbour_not_counted_twice():
    txns = [make_txn(1, 100 + (i % 2), i) for i in range(30)]
    assert CentralityDetector().detect(txns) == []


def test_two_way_traffic_with_one_neighbour_counts_once():
    txns = outgoing(1, MIN_CONNECTIONS - 1) + [make_txn(100, 1, 99)]
    assert CentralityDetector().detect(txns) == []


def test_two_hubs_give_two_signals():
    txns = outgoing(1, MIN_CONNECTIONS) + outgoing(2, MIN_CONNECTIONS, base=1000, start_id=50)
    signals = CentralityDetector().detect(txns)

    assert len(signals) == 2


def test_related_account_ids_are_hub_first_then_neighbours():
    signals = CentralityDetector().detect(outgoing(1, MIN_CONNECTIONS))

    assert signals[0].related_account_ids == [1] + [100 + i for i in range(MIN_CONNECTIONS)]


def test_related_transaction_ids_include_incoming_and_outgoing():
    txns = outgoing(1, MIN_CONNECTIONS - 1) + [make_txn(500, 1, 99)]
    signals = CentralityDetector().detect(txns)

    assert len(signals) == 1
    assert sorted(signals[0].related_transaction_ids) == list(range(1, MIN_CONNECTIONS)) + [99]