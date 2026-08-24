from app.models.evidence import Evidence


def build_report_prompt(
    filename: str,
    risk_score: float,
    evidence_list: list[Evidence],
) -> str:
    """Builds the prompt sent to Gemini for generating a report narrative."""

    findings_text = "\n".join(
        f"- [{e.severity.upper()}] {e.detector_name}: {e.description}"
        for e in evidence_list
    )

    return f"""You are a financial crime investigator writing a professional report summary.

Investigation file: {filename}
Overall Risk Score: {risk_score}/100

Findings detected by the automated fraud detection system:
{findings_text}

Write a concise, professional narrative (3-5 paragraphs) summarizing this investigation.
Explain the significance of the findings, how they relate to each other if applicable,
and what risk they represent. Write in a formal, objective tone suitable for a financial
crime investigation report. Do not use bullet points — write in flowing paragraphs.
"""