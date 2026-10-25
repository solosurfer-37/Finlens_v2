from decimal import Decimal
from types import SimpleNamespace

from app.detectors.benford import MIN_TRANSACTIONS, BenfordDetector

NATURAL_COUNTS = {1: 30, 2: 18, 3: 12, 4: 10, 5: 8, 6: 7, 7: 6, 8: 5, 9: 4}


def make_txn(amount: Decimal) -> SimpleNamespace:
    return SimpleNamespace(amount=amount)


def build_txns(counts: dict[int, int], template: str = "{d}.00") -> list[SimpleNamespace]:
    return [
        make_txn(Decimal(template.format(d=d)))
        for d, n in counts.items()
        for _ in range(n)
    ]


def flagged_digits(signals) -> set[int]:
    return {int(s.description.split()[2]) for s in signals}


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