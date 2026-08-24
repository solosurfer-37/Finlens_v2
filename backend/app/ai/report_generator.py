from app.ai.gemini_client import GeminiClient
from app.ai.prompts import build_report_prompt
from app.models.evidence import Evidence


class AIReportGenerator:
    """Generates a natural-language investigation narrative using Gemini, with a safe fallback."""

    def __init__(self):
        self.client = GeminiClient()

    def generate_narrative(
        self,
        filename: str,
        risk_score: float,
        evidence_list: list[Evidence],
        fallback_text: str,
    ) -> str:
        if not evidence_list:
            return fallback_text

        prompt = build_report_prompt(filename, risk_score, evidence_list)

        try:
            return self.client.generate(prompt)
        except Exception:
            return fallback_text