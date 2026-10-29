from types import SimpleNamespace

from app.detectors.watchlist import WatchlistDetector


class FakeAccountRepo:
    def __init__(self, accounts: dict[int, str]):
        self.accounts = {i: SimpleNamespace(id=i, account_number=n) for i, n in accounts.items()}
        self.calls = 0

    def get_by_ids(self, account_ids):
        self.calls += 1
        return {i: self.accounts[i] for i in account_ids if i in self.accounts}


class FakeRepo:
    def __init__(self, flagged: set[str]):
        self.flagged = flagged

    def get_all_flagged_numbers(self) -> set[str]:
        return self.flagged


def make_detector(accounts: dict[int, str], flagged: set[str]):
    detector = WatchlistDetector(None)
    detector.watchlist_repo = FakeRepo(flagged)
    detector.account_repo = FakeAccountRepo(accounts)
    return detector, detector.account_repo


def make_txn(ref: str, sender: int, receiver: int, txn_id: int = 0) -> SimpleNamespace:
    return SimpleNamespace(
        id=txn_id,
        transaction_reference=ref,
        sender_account_id=sender,
        receiver_account_id=receiver,
    )


ACCOUNTS = {1: "ACC-001", 2: "ACC-002", 3: "ACC-003"}


def test_empty_watchlist_returns_nothing_and_skips_lookups():
    detector, account_repo = make_detector(ACCOUNTS, set())

    assert detector.detect([make_txn("T1", 1, 2)]) == []
    assert account_repo.calls == 0


def test_accounts_are_fetched_in_one_bulk_call():
    detector, account_repo = make_detector(ACCOUNTS, {"ACC-001"})
    txns = [make_txn("T1", 1, 2), make_txn("T2", 2, 3), make_txn("T3", 3, 1)]

    detector.detect(txns)

    assert account_repo.calls == 1


def test_no_watchlisted_accounts_returns_nothing():
    detector, _ = make_detector(ACCOUNTS, {"ACC-999"})
    assert detector.detect([make_txn("T1", 1, 2)]) == []


def test_watchlisted_sender_is_flagged():
    detector, _ = make_detector(ACCOUNTS, {"ACC-001"})
    signals = detector.detect([make_txn("T1", 1, 2)])

    assert len(signals) == 1
    assert signals[0].detector_name == "watchlist"
    assert signals[0].severity == "high"
    assert "watchlisted sender ACC-001" in signals[0].description
    assert "T1" in signals[0].description


def test_watchlisted_receiver_is_flagged():
    detector, _ = make_detector(ACCOUNTS, {"ACC-002"})
    signals = detector.detect([make_txn("T1", 1, 2)])

    assert len(signals) == 1
    assert "watchlisted receiver ACC-002" in signals[0].description


def test_both_sides_watchlisted_gives_two_signals():
    detector, _ = make_detector(ACCOUNTS, {"ACC-001", "ACC-002"})
    signals = detector.detect([make_txn("T1", 1, 2)])

    assert len(signals) == 2


def test_missing_account_does_not_crash():
    detector, _ = make_detector(ACCOUNTS, {"ACC-001"})
    assert detector.detect([make_txn("T1", 42, 43)]) == []


def test_each_transaction_is_flagged_separately():
    detector, _ = make_detector(ACCOUNTS, {"ACC-001"})
    txns = [make_txn("T1", 1, 2), make_txn("T2", 3, 1)]
    signals = detector.detect(txns)

    assert len(signals) == 2
    assert "T1" in signals[0].description
    assert "T2" in signals[1].description


def test_related_ids_cover_both_accounts_and_the_transaction():
    detector, _ = make_detector(ACCOUNTS, {"ACC-001"})
    signals = detector.detect([make_txn("T1", 1, 2, txn_id=77)])

    assert signals[0].related_account_ids == [1, 2]
    assert signals[0].related_transaction_ids == [77]