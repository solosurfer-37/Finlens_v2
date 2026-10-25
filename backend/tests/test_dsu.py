from types import SimpleNamespace

from app.detectors.dsu import DSU, MIN_CLUSTER_SIZE, DSUDetector


def make_txn(sender: int, receiver: int) -> SimpleNamespace:
    return SimpleNamespace(sender_account_id=sender, receiver_account_id=receiver)


def chain(start: int, size: int) -> list[SimpleNamespace]:
    return [make_txn(start + i, start + i + 1) for i in range(size - 1)]


def test_dsu_find_creates_singleton():
    dsu = DSU()
    assert dsu.find(7) == 7


def test_dsu_union_joins_two_accounts():
    dsu = DSU()
    dsu.union(1, 2)
    assert dsu.find(1) == dsu.find(2)


def test_dsu_union_is_transitive():
    dsu = DSU()
    dsu.union(1, 2)
    dsu.union(2, 3)
    assert dsu.find(1) == dsu.find(3)


def test_dsu_separate_sets_stay_separate():
    dsu = DSU()
    dsu.union(1, 2)
    dsu.union(10, 11)
    assert dsu.find(1) != dsu.find(10)


def test_empty_transactions_returns_no_signals():
    assert DSUDetector().detect([]) == []


def test_below_min_cluster_size_not_flagged():
    txns = chain(1, MIN_CLUSTER_SIZE - 1)
    assert DSUDetector().detect(txns) == []


def test_exactly_min_cluster_size_is_flagged():
    signals = DSUDetector().detect(chain(1, MIN_CLUSTER_SIZE))

    assert len(signals) == 1
    assert signals[0].detector_name == "dsu"
    assert signals[0].severity == "medium"
    assert f"{MIN_CLUSTER_SIZE} accounts" in signals[0].description


def test_direction_does_not_matter():
    txns = [make_txn(i + 1, 1) for i in range(1, MIN_CLUSTER_SIZE)]
    signals = DSUDetector().detect(txns)

    assert len(signals) == 1


def test_only_large_cluster_is_flagged_when_two_exist():
    txns = chain(1, MIN_CLUSTER_SIZE) + chain(100, 2)
    signals = DSUDetector().detect(txns)

    assert len(signals) == 1
    assert f"{MIN_CLUSTER_SIZE} accounts" in signals[0].description


def test_two_small_clusters_are_not_merged():
    txns = chain(1, 3) + chain(100, 3)
    assert DSUDetector().detect(txns) == []


def test_self_loop_is_single_account_cluster():
    assert DSUDetector().detect([make_txn(1, 1)]) == []