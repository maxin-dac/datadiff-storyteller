from __future__ import annotations

import json
import re
from html import escape
from pathlib import Path
from typing import Any

import streamlit as st

from components.icons import icon
from core.i18n import get_lang, t
from models.schemas import Finding

ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT / "assets" / "logo.svg"
VERSION_PATH = ROOT / "VERSION"

BRAND_LOGO_SVG = """
<svg viewBox="0 0 64 64" width="42" height="42" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Logo">
  <defs>
    <linearGradient id="ddsBrandGrad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
      <stop stop-color="#6366f1"/>
      <stop offset="1" stop-color="#4f46e5"/>
    </linearGradient>
  </defs>
  <rect x="1" y="1" width="62" height="62" rx="15" fill="url(#ddsBrandGrad)"/>
  <path d="M17 23c0-2.76 5.37-5 12-5s12 2.24 12 5-5.37 5-12 5-12-2.24-12-5Z" fill="#FFFFFF" fill-opacity="0.95"/>
  <path d="M17 23v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
  <path d="M17 32v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-opacity="0.72"/>
  <path d="M43 18l5 5-5 5" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 23H39" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
</svg>
"""

CATEGORY_ICONS = {
    "schema": "schema",
    "volume": "database",
    "nulls": "quality",
    "distribution": "distribution",
    "outliers": "anomaly",
    "duplicates": "warning",
    "quality": "check",
    "business_rule": "warning",
}

SEVERITY_LABELS = {
    "fr": {
        "critical": "Critique",
        "high": "Élevé",
        "medium": "Moyen",
        "low": "Faible",
        "info": "Info",
    },
    "en": {
        "critical": "Critical",
        "high": "High",
        "medium": "Medium",
        "low": "Low",
        "info": "Info",
    },
}


def _html(html: str) -> None:
    if hasattr(st, "html"):
        st.html(html)
    else:
        st.markdown(html, unsafe_allow_html=True)


def html_block(html: str) -> None:
    _html(html)


def _minify_svg(svg: str) -> str:
    return " ".join(svg.split())


def _read_version() -> str:
    try:
        value = VERSION_PATH.read_text(encoding="utf-8").strip()
        return value or "0.0.0"
    except Exception:
        return "0.0.0"


def inline_logo(size: int = 32, css_class: str = "app-logo") -> str:
    return f'<span class="{css_class}" style="--logo-size:{size}px">{_minify_svg(LOGO_SVG) if False else ""}</span>'


LOGO_SVG = """
<svg viewBox="0 0 64 64" width="100%" height="100%" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="2" y="2" width="60" height="60" rx="15" fill="currentColor" fill-opacity="0.12"/>
  <path d="M17 23c0-2.76 5.37-5 12-5s12 2.24 12 5-5.37 5-12 5-12-2.24-12-5Z" fill="currentColor" fill-opacity="0.95"/>
  <path d="M17 23v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <path d="M17 32v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-opacity="0.72"/>
  <path d="M43 18l5 5-5 5" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 23H39" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
</svg>
"""


def _severity_label(severity: str, lang: str) -> str:
    return SEVERITY_LABELS.get(lang, SEVERITY_LABELS["fr"]).get(severity, severity)


def _format_metric_value(value: Any) -> str:
    if hasattr(value, "item"):
        try:
            value = value.item()
        except Exception:
            pass

    if value is None:
        return "n/a"

    if isinstance(value, bool):
        return "true" if value else "false"

    if isinstance(value, int):
        return f"{value:,}"

    if isinstance(value, float):
        if value != value:
            return "n/a"
        if float(value).is_integer():
            return f"{int(value):,}"
        return f"{value:,.4f}".rstrip("0").rstrip(".")

    if isinstance(value, (list, tuple, set)):
        return ", ".join(_format_metric_value(item) for item in value)

    if isinstance(value, dict):
        return json.dumps(value, ensure_ascii=False, default=str)

    return str(value)


def _metrics_details(metrics: dict, lang: str) -> str:
    if not metrics:
        return ""

    rows = []
    for key, value in metrics.items():
        rows.append(
            "".join([
                "<tr>",
                f"<th>{escape(str(key))}</th>",
                f"<td>{escape(_format_metric_value(value))}</td>",
                "</tr>",
            ])
        )

    return "".join([
        '<details class="dds-details">',
        f'<summary>{escape(t("doc_metrics", lang=lang))}</summary>',
        '<table class="dds-mini-table"><tbody>',
        "".join(rows),
        "</tbody></table>",
        "</details>",
    ])


def _evidence_details(evidence: dict, lang: str) -> str:
    if not evidence:
        return ""

    try:
        payload = json.dumps(evidence, ensure_ascii=False, indent=2, default=str)
    except Exception:
        payload = str(evidence)

    if len(payload) > 4000:
        payload = payload[:4000] + "..."

    return "".join([
        '<details class="dds-details">',
        f'<summary>{escape(t("doc_evidence", lang=lang))}</summary>',
        f'<pre class="dds-pre">{escape(payload)}</pre>',
        "</details>",
    ])


def _on_lang_change() -> None:
    from core.analysis import has_inputs, run_analysis

    if has_inputs():
        try:
            run_analysis(get_lang())
        except Exception:
            pass


def sidebar_brand() -> None:
    lang = get_lang()
    version = _read_version()
    logo = _minify_svg(BRAND_LOGO_SVG)

    body = "".join([
        f'<div class="idcard">',
        f'<div class="logo-wrap">{logo}</div>',
        '<div class="idmeta">',
        f'<div class="idtitle">{escape(t("brand_name", lang=lang))}</div>',
        f'<div class="idsub">{escape(t("brand_sub", lang=lang))}</div>',
        f'<span class="idver">v{escape(version)}</span>',
        "</div>",
        "</div>",
        f'<div class="lang-label">{escape(t("lang_label", lang=lang))}</div>',
    ])

    st.sidebar.markdown(body, unsafe_allow_html=True)

    labels = {"fr": "FR", "en": "EN"}
    order = ["fr", "en"]
    index = order.index(lang) if lang in order else 0

    st.sidebar.radio(
        t("lang_label", lang=lang),
        options=order,
        index=index,
        format_func=lambda x: labels[x],
        key="lang",
        horizontal=True,
        label_visibility="collapsed",
        on_change=_on_lang_change,
    )


def load_css() -> None:
    css_path = ROOT / "assets" / "styles.css"

    if not css_path.exists():
        return

    css = css_path.read_text(encoding="utf-8")
    css = re.sub(r"/\*.*?\*/", "", css, flags=re.S)
    css = " ".join(css.split())

    st.markdown(f"<style>{css}</style>", unsafe_allow_html=True)


def page_header(title: str, subtitle: str) -> None:
    _html(
        "".join([
            '<div class="pg-h">',
            f"<h1>{escape(title)}</h1>",
            f"<p>{escape(subtitle)}</p>",
            "</div>",
        ])
    )


def section(title: str, icon_name: str | None = None) -> None:
    icon_html = icon(icon_name, size=18) if icon_name else ""
    _html(
        "".join([
            '<div class="sec-h">',
            icon_html,
            f"<span>{escape(title)}</span>",
            "</div>",
        ])
    )


def kpi_card(label: str, value: str, helper: str = "", tone: str = "neutral") -> str:
    return "".join([
        f'<div class="kvcell tone-{escape(tone)}">',
        f'<div class="k">{escape(label)}</div>',
        f'<div class="v">{escape(value)}</div>',
        f'<div class="note">{escape(helper)}</div>',
        "</div>",
    ])


def kpi_grid(items: list[dict]) -> None:
    cards = "".join(
        kpi_card(
            label=str(item.get("label", "")),
            value=str(item.get("value", "")),
            helper=str(item.get("helper", "")),
            tone=str(item.get("tone", "neutral")),
        )
        for item in items
    )

    _html(f'<div class="kvgrid">{cards}</div>')


def finding_card(finding: Finding) -> None:
    lang = get_lang()
    icon_name = CATEGORY_ICONS.get(finding.category, "info")
    severity_label = _severity_label(finding.severity, lang)
    category_label = t(f"cat_{finding.category}", lang=lang)

    chips = []

    if finding.columns:
        for column in finding.columns:
            chips.append(f'<span class="dds-chip">{escape(str(column))}</span>')

    chips.append(f'<span class="dds-chip dds-chip-category">{escape(category_label)}</span>')

    parts = [
        f'<div class="dds-finding severity-{escape(finding.severity)}">',
        '<header class="dds-finding-header">',
        '<div class="dds-finding-title">',
        icon(icon_name, size=18),
        f'<h3 class="dds-finding-heading">{escape(finding.title)}</h3>',
        "</div>",
        f'<span class="dds-badge badge-{escape(finding.severity)}">{escape(severity_label)}</span>',
        "</header>",
        f'<p class="dds-finding-narrative">{escape(finding.narrative)}</p>',
        '<div class="dds-finding-meta">',
        "".join(chips),
        "</div>",
    ]

    if finding.recommendation:
        parts.append(
            "".join([
                '<div class="dds-recommendation">',
                f'<span class="dds-recommendation-label">{escape(t("card_recommendation", lang=lang))}</span>',
                f"<span>{escape(finding.recommendation)}</span>",
                "</div>",
            ])
        )

    parts.append(_metrics_details(finding.metrics or {}, lang))
    parts.append(_evidence_details(finding.evidence or {}, lang))
    parts.append("</div>")

    _html("".join(parts))


def empty_state(title: str, message: str, icon_name: str = "upload") -> None:
    _html(
        "".join([
            '<div class="dds-empty">',
            '<div class="dds-empty-art">',
            icon(icon_name, 42),
            "</div>",
            f"<h3>{escape(title)}</h3>",
            f"<p>{escape(message)}</p>",
            "</div>",
        ])
    )


def require_analysis() -> dict:
    if "analysis" not in st.session_state:
        lang = get_lang()
        empty_state(
            t("home_no_analysis", lang=lang),
            t("home_no_analysis_msg", lang=lang),
            icon_name="upload",
        )
        st.stop()

    return st.session_state["analysis"]
