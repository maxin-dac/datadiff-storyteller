from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Optional

from jinja2 import Environment, FileSystemLoader, select_autoescape

from core.i18n import t
from models.schemas import Finding

ROOT = Path(__file__).resolve().parents[1]

LABEL_KEYS = [
    "doc_app_title", "doc_subtitle", "doc_baseline", "doc_compare", "doc_baseline_rows",
    "doc_compare_rows", "doc_generated_at", "doc_exec_summary", "doc_changes", "doc_no_change",
    "doc_columns", "doc_category", "doc_recommendation", "doc_metrics", "doc_evidence", "doc_footer",
    "brand_name",
]


def _labels(lang: str) -> dict:
    return {key: t(key, lang=lang) for key in LABEL_KEYS}


def build_markdown_report(summary, findings, meta_baseline, meta_compare, lang: Optional[str] = None) -> str:
    lang = lang or "fr"
    lb = _labels(lang)
    lines = [f"# {lb['doc_app_title']}", ""]
    lines.append(f"- {lb['doc_baseline']} : {meta_baseline.get('name', 'n/a')}")
    lines.append(f"- {lb['doc_compare']} : {meta_compare.get('name', 'n/a')}")
    lines.append(f"- {lb['doc_generated_at']} : {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")
    lines.append(f"## {lb['doc_exec_summary']}")
    lines.append("")
    lines.append(summary)
    lines.append("")
    lines.append(f"## {lb['doc_changes']}")
    lines.append("")
    if not findings:
        lines.append(lb["doc_no_change"])
    else:
        for finding in findings:
            lines.append(f"### [{finding.severity.upper()}] {finding.title}")
            lines.append("")
            lines.append(finding.narrative)
            lines.append("")
            if finding.columns:
                lines.append(f"{lb['doc_columns']} : {', '.join(finding.columns)}")
                lines.append("")
            if finding.metrics:
                lines.append(f"{lb['doc_metrics']} :")
                lines.append("")
                for key, value in finding.metrics.items():
                    if isinstance(value, (dict, list)):
                        value = json.dumps(value, ensure_ascii=False)
                    lines.append(f"- `{key}` : {value}")
                lines.append("")
            if finding.recommendation:
                lines.append(f"{lb['doc_recommendation']} : {finding.recommendation}")
                lines.append("")
            if finding.evidence:
                lines.append(f"{lb['doc_evidence']} :")
                lines.append("")
                lines.append(f"```json\n{json.dumps(finding.evidence, ensure_ascii=False, indent=2)}\n```")
                lines.append("")
    return "\n".join(lines)


def render_html_report(summary, findings, meta_baseline, meta_compare, lang: Optional[str] = None) -> str:
    lang = lang or "fr"
    lb = _labels(lang)
    css_path = ROOT / "assets" / "report.css"
    css = css_path.read_text(encoding="utf-8") if css_path.exists() else ""
    env = Environment(loader=FileSystemLoader(str(ROOT / "templates")), autoescape=select_autoescape(["html", "xml"]))
    template = env.get_template("report.html")
    meta = {
        "baseline_name": meta_baseline.get("name", "version 1"),
        "compare_name": meta_compare.get("name", "version 2"),
        "baseline_rows": meta_baseline.get("rows", "n/a"),
        "compare_rows": meta_compare.get("rows", "n/a"),
        "generated_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
    }
    return template.render(summary=summary, findings=[f.to_dict() for f in findings], meta=meta, css=css, lb=lb)
