from collections import Counter

from sqlalchemy.orm import Session

from app.models.evidence import Evidence
from app.models.report import Report
from app.repositories.investigation_repository import InvestigationRepository
from app.repositories.report_repository import ReportRepository
from app.ai.report_generator import AIReportGenerator

class ReportEngine:
    """Compiles Evidence records into a structured, human-readable investigation report."""

    def __init__(self, db: Session):
        self.db = db
        self.report_repo = ReportRepository(db)
        self.investigation_repo = InvestigationRepository(db)
        self.ai_generator = AIReportGenerator()

    def generate(self, investigation_id: int, evidence_list: list[Evidence]) -> Report:
        investigation = self.investigation_repo.get_by_id(investigation_id)

        severity_counts = Counter(e.severity for e in evidence_list)
        severity_breakdown = {
            "high": severity_counts.get("high", 0),
            "medium": severity_counts.get("medium", 0),
            "low": severity_counts.get("low", 0),
        }

        fallback_text = self._build_summary_text(
            investigation.filename,
            investigation.risk_score,
            severity_breakdown,
            evidence_list,
        )

        summary_text = self.ai_generator.generate_narrative(
            filename=investigation.filename,
            risk_score=investigation.risk_score,
            evidence_list=evidence_list,
            fallback_text=fallback_text,
        )

        report = Report(
            investigation_id=investigation_id,
            summary_text=summary_text,
            severity_breakdown=severity_breakdown,
            total_evidence_count=len(evidence_list),
            risk_score_snapshot=investigation.risk_score,
        )

        return self.report_repo.create(report)

    def _build_summary_text(
        self,
        filename: str,
        risk_score: float,
        severity_breakdown: dict,
        evidence_list: list[Evidence],
    ) -> str:
        lines = [
            f"Investigation Report for '{filename}'",
            f"Overall Risk Score: {risk_score}/100",
            "",
            f"Findings: {severity_breakdown['high']} high severity, "
            f"{severity_breakdown['medium']} medium severity, "
            f"{severity_breakdown['low']} low severity.",
            "",
            "Detailed Findings:",
        ]

        for evidence in evidence_list:
            lines.append(f"- [{evidence.severity.upper()}] {evidence.detector_name}: {evidence.description}")

        return "\n".join(lines)