from __future__ import annotations

from models.schemas import Category, Finding, Severity


def make_finding(
    finding_id: str,
    category: Category,
    severity: Severity,
    title: str,
    narrative: str,
    columns: list[str] | None = None,
    metrics: dict | None = None,
    recommendation: str | None = None,
    evidence: dict | None = None,
) -> Finding:
    return Finding(
        id=finding_id,
        category=category,
        severity=severity,
        title=title,
        narrative=narrative,
        columns=columns or [],
        metrics=metrics or {},
        recommendation=recommendation,
        evidence=evidence,
    )