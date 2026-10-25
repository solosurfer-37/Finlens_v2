from decimal import Decimal

import pytest

from app.engine.evidence_engine import MAX_RISK_SCORE, EvidenceEngine
from app.engine.fraud_signal import FraudSignal
from app.models.evidence import Evidence
from app.models.investigation import Investigation
from app.models.user import User


def make_investigation(db) -> int:
    user = User(email="ev@finlens.com", hashed_password="x")
    db.add(user)
    db.commit()
    inv = Investigation(user_id=user.id, filename="ev.csv")
    db.add(inv)
    db.commit()
    return inv.id


def sig(severity: str, name: str = "test") -> FraudSignal:
    return FraudSignal(detector_name=name, description=f"{severity} signal", severity=severity)


def test_no_signals_gives_zero_and_completed(db):
    inv_id = make_investigation(db)
    score = EvidenceEngine(db).process(inv_id, [])

    assert score == Decimal("0")
    inv = db.get(Investigation, inv_id)
    assert inv.risk_score == 0.0
    assert inv.status == "Completed"


@pytest.mark.parametrize(
    "severity,expected",
    [("low", "5"), ("medium", "15"), ("high", "30")],
)
def test_single_signal_score_per_severity(db, severity, expected):
    inv_id = make_investigation(db)
    score = EvidenceEngine(db).process(inv_id, [sig(severity)])

    assert score == Decimal(expected)


def test_mixed_signals_are_summed(db):
    inv_id = make_investigation(db)
    score = EvidenceEngine(db).process(inv_id, [sig("low"), sig("medium"), sig("high")])

    assert score == Decimal("50")


def test_score_exactly_at_cap_is_not_changed(db):
    inv_id = make_investigation(db)
    signals = [sig("high")] * 3 + [sig("low")] * 2
    score = EvidenceEngine(db).process(inv_id, signals)

    assert score == MAX_RISK_SCORE


def test_score_is_capped_at_100(db):
    inv_id = make_investigation(db)
    score = EvidenceEngine(db).process(inv_id, [sig("high")] * 4)

    assert score == MAX_RISK_SCORE
    assert db.get(Investigation, inv_id).risk_score == 100.0


def test_evidence_rows_are_persisted(db):
    inv_id = make_investigation(db)
    EvidenceEngine(db).process(inv_id, [sig("high", "fan_out"), sig("low", "benford")])

    rows = db.query(Evidence).filter_by(investigation_id=inv_id).all()
    assert len(rows) == 2
    assert {r.detector_name for r in rows} == {"fan_out", "benford"}
    assert {r.risk_score_contribution for r in rows} == {Decimal("30"), Decimal("5")}


def test_unknown_severity_raises_key_error_known_gap(db):
    # Known gap: an unexpected severity crashes the pipeline.
    # When fixed (validate/skip), this assertion must change.
    inv_id = make_investigation(db)
    with pytest.raises(KeyError):
        EvidenceEngine(db).process(inv_id, [sig("critical")])