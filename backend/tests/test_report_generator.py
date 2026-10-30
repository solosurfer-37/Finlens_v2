import logging
from types import SimpleNamespace

from app.ai.report_generator import AIReportGenerator

FALLBACK = "fallback report text"


def make_evidence():
    return [SimpleNamespace(severity="high", detector_name="large_transfer", description="big move")]


def test_gemini_failure_returns_fallback_and_logs_warning(caplog):
    with caplog.at_level(logging.WARNING, logger="app.ai.report_generator"):
        text = AIReportGenerator().generate_narrative("f.csv", 30.0, make_evidence(), FALLBACK)

    assert text == FALLBACK
    assert any("using fallback text" in r.getMessage() for r in caplog.records)


def test_gemini_success_returns_generated_text(monkeypatch):
    monkeypatch.setattr(
        "app.ai.gemini_client.GeminiClient.generate",
        lambda self, prompt: "generated narrative",
    )
    text = AIReportGenerator().generate_narrative("f.csv", 30.0, make_evidence(), FALLBACK)

    assert text == "generated narrative"


def test_empty_evidence_returns_fallback_without_calling_gemini(caplog):
    with caplog.at_level(logging.WARNING, logger="app.ai.report_generator"):
        text = AIReportGenerator().generate_narrative("f.csv", 0.0, [], FALLBACK)

    assert text == FALLBACK
    assert caplog.records == []