from __future__ import annotations

from collections import defaultdict
from typing import Optional

from core.i18n import category_label, t
from core.scoring import sort_findings
from models.schemas import Finding

PRIORITY_CATEGORIES = [
    "schema",
    "volume",
    "nulls",
    "distribution",
    "outliers",
    "business_rule",
    "duplicates",
    "quality",
]


def build_executive_summary(
    meta_baseline: dict,
    meta_compare: dict,
    findings: list[Finding],
    lang: Optional[str] = None,
) -> str:
    lang = lang or "fr"

    if not findings:
        return t("nar_none", lang=lang)

    ordered = sort_findings(findings)
    baseline_name = meta_baseline.get("name", "version 1")
    compare_name = meta_compare.get("name", "version 2")
    baseline_rows = meta_baseline.get("rows", "n/a")
    compare_rows = meta_compare.get("rows", "n/a")

    paragraphs = [
        t("nar_intro", lang=lang, a=baseline_name, b=compare_name, ra=baseline_rows, rb=compare_rows, n=len(ordered))
    ]

    by_category: dict[str, list[Finding]] = defaultdict(list)
    for finding in ordered:
        if finding.severity in {"critical", "high", "medium"}:
            by_category[finding.category].append(finding)

    for category in PRIORITY_CATEGORIES:
        category_findings = by_category.get(category, [])
        if not category_findings:
            continue
        label = category_label(category, lang=lang)
        lines = [t("nar_regarding", lang=lang, label=label)]
        for finding in category_findings[:3]:
            lines.append(f"- {finding.narrative}")
        paragraphs.append("\n".join(lines))

    recommendations: list[str] = []
    for finding in ordered:
        if finding.recommendation and finding.recommendation not in recommendations:
            recommendations.append(finding.recommendation)
        if len(recommendations) >= 5:
            break

    if recommendations:
        lines = [t("nar_reco_title", lang=lang)]
        lines.extend(f"- {rec}" for rec in recommendations)
        paragraphs.append("\n".join(lines))

    return "\n\n".join(paragraphs)
