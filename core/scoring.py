from __future__ import annotations

from models.schemas import Finding

SEVERITY_RANK = {
    "critical": 0,
    "high": 1,
    "medium": 2,
    "low": 3,
    "info": 4,
}

SEVERITY_PENALTY = {
    "critical": 18,
    "high": 10,
    "medium": 4,
    "low": 1,
    "info": 0,
}


def sort_findings(findings: list[Finding]) -> list[Finding]:
    return sorted(
        findings,
        key=lambda f: (
            SEVERITY_RANK.get(f.severity, 99),
            f.category,
            f.title,
        ),
    )


def calculate_health_score(findings: list[Finding]) -> tuple[int, str]:
    penalty = sum(SEVERITY_PENALTY.get(f.severity, 0) for f in findings)
    score = max(0, 100 - penalty)

    if score >= 90:
        grade = "A"
    elif score >= 75:
        grade = "B"
    elif score >= 60:
        grade = "C"
    elif score >= 40:
        grade = "D"
    else:
        grade = "E"

    return score, grade