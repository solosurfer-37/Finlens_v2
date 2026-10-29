from decimal import Decimal
from types import SimpleNamespace

from app.detectors.benford import MIN_TRANSACTIONS, BenfordDetector

NATURAL_COUNTS = {1: 30, 2: 18, 3: 12, 4: 10, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4}


def build_txns(counts: dict[int, int], template: str = "{d}.00") -> list[SimpleNamespace]:
    txns = []
    txn_id = 0
    for d, n in counts.items():
        for _ in range(n):
            txn_id += 1
            txns.append(
                SimpleNamespace(
                    id=txn_id,
                    sender_account_id=txn_id,
                    receiver_account_id=1000 + txn_id,
                    amount=Decimal(template.format(d=d)),
                )
            )
    return txns


def flagged_digits(signals) -> set[int]:
    return {int(s.description.split()[2]) for s in signals}


def signal_for(signals, digit: int):
    return next(s for s in signals if int(s.description.split()[2]) == digit)


def test_below_min_transactions_returns_nothing_even_if_skewed():
    txns = build_txns({9: MIN_TRANSACTIONS - 1})
    assert BenfordDetector().detect(txns) == []


def test_exactly_min_transactions_is_checked():
    txns = build_txns({9: MIN_TRANSACTIONS})
    signals = BenfordDetector().detect(txns)

    assert flagged_digits(signals) == {1, 2, 9}


def test_natural_distribution_is_not_flagged():
    assert BenfordDetector().detect(build_txns(NATURAL_COUNTS)) == []


def test_skewed_signals_have_expected_fields():
    signals = BenfordDetector().detect(build_txns({9: 50}))

    assert all(s.detector_name == "benford" for s in signals)
    assert all(s.severity == "medium" for s in signals)


def test_negative_amounts_use_absolute_value():
    txns = build_txns(NATURAL_COUNTS, template="-{d}.00")
    assert BenfordDetector().detect(txns) == []


def test_missing_digit_two_is_flagged_by_absolute_deviation():
    counts = {1: 40, 3: 20, 4: 10, 5: 10, 6: 8, 7: 6, 8: 4, 9: 2}
    signals = BenfordDetector().detect(build_txns(counts))

    assert 2 in flagged_digits(signals)


def test_sub_one_amounts_use_first_significant_digit():
    # Same natural distribution, scaled to 0.d0. Should look identical to Benford.
    txns = build_txns(NATURAL_COUNTS, template="0.{d}0")
    assert BenfordDetector().detect(txns) == []


def test_over_represented_digit_lists_its_transactions_and_accounts():
    signals = BenfordDetector().detect(build_txns({9: MIN_TRANSACTIONS}))
    signal = signal_for(signals, 9)

    assert signal.related_transaction_ids == list(range(1, MIN_TRANSACTIONS + 1))
    assert 1 in signal.related_account_ids
    assert 1001 in signal.related_account_ids


def test_under_represented_digit_has_no_related_ids():
    signals = BenfordDetector().detect(build_txns({9: MIN_TRANSACTIONS}))
    signal = signal_for(signals, 1)

    assert signal.related_transaction_ids == []
    assert signal.related_account_ids == []