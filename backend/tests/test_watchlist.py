from types import SimpleNamespace

from app.detectors.watchlist import WatchlistDetector


class FakeDB:
    def __init__(self, accounts: dict[int, str]):
        self.accounts = {i: SimpleNamespace(account_number=n) for i, n in accounts.items()}
        self.get_calls = 0

    def get(self, model, account_id):
        self.get_calls += 1
        return self.accounts.get(account_id)


class FakeRepo:
    def __init__(self, flagged: set[str]):
        self.flagged = flagged

    def get_all_flagged_numbers(self) -> set[str]:
        return self.flagged


def make_detector(accounts: dict[int, str], flagged: set[str]):
    db = FakeDB(accounts)
    detector = WatchlistDetector(db)
    detector.watchlist_repo = FakeRepo(flagged)
    return detector, db


def make_txn(ref: str, sender: int, receiver: int) -> SimpleNamespace:
    return SimpleNamespace(
        transaction_reference=ref,
        sender_account_id=sender,
        receiver_account_id=receiver,
    )


ACCOUNTS = {1: "ACC-001", 2: "ACC-002", 3: "ACC-003"}


def test_empty_watchlist_returns_nothing_and_skips_lookups():
    detector, db = make_detector(ACCOUNTS, set())

    assert detector.detect([make_txn("T1", 1, 2)]) == []
    assert db.get_calls == 0


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