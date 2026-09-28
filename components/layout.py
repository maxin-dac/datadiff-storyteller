from __future__ import annotations

import re
from html import escape
from pathlib import Path

import streamlit as st

from components.icons import icon
from core.i18n import AVAILABLE_LANGS, get_lang, t
from models.schemas import Finding

ROOT = Path(__file__).resolve().parents[1]
LOGO_PATH = ROOT / "assets" / "logo.svg"

LOGO_SVG = r'''
<svg viewBox="0 0 64 64" width="100%" height="100%" fill="none" xmlns="http://www.w3.org/2000/svg" aria-hidden="true">
  <rect x="2" y="2" width="60" height="60" rx="15" fill="currentColor" fill-opacity="0.12"/>
  <path d="M17 23c0-2.76 5.37-5 12-5s12 2.24 12 5-5.37 5-12 5-12-2.24-12-5Z" fill="currentColor" fill-opacity="0.95"/>
  <path d="M17 23v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
  <path d="M17 32v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-opacity="0.72"/>
  <path d="M43 18l5 5-5 5" stroke="currentColor" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 23H39" stroke="currentColor" stroke-width="3" stroke-linecap="round"/>
</svg>
'''

BRAND_LOGO_SVG = r'''
<svg viewBox="0 0 64 64" width="100%" height="100%" fill="none" xmlns="http://www.w3.org/2000/svg" role="img" aria-label="Logo DataDiff Storyteller">
  <defs>
    <linearGradient id="ddsBrandGrad" x1="0" y1="0" x2="64" y2="64" gradientUnits="userSpaceOnUse">
      <stop stop-color="#2563EB"/><stop offset="1" stop-color="#7C3AED"/>
    </linearGradient>
  </defs>
  <rect width="64" height="64" rx="16" fill="url(#ddsBrandGrad)"/>
  <path d="M17 23c0-2.76 5.37-5 12-5s12 2.24 12 5-5.37 5-12 5-12-2.24-12-5Z" fill="#FFFFFF" fill-opacity="0.95"/>
  <path d="M17 23v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
  <path d="M17 32v9c0 2.76 5.37 5 12 5s12-2.24 12-5v-9" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-opacity="0.72"/>
  <path d="M43 18l5 5-5 5" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round" stroke-linejoin="round"/>
  <path d="M48 23H39" stroke="#FFFFFF" stroke-width="3" stroke-linecap="round"/>
</svg>
'''

BRAND_STYLE = r'''
<style>
.sidebar-brand{display:flex;align-items:center;gap:.7rem;padding:.8rem .75rem;margin:.15rem 0 .35rem;border-radius:14px;background:linear-gradient(135deg,#eef2ff,#f5f3ff);border:1px solid #e2e8f0;box-shadow:0 1px 2px rgba(15,23,42,.05);}
.sidebar-brand-logo{width:40px;height:40px;flex:0 0 auto;display:inline-flex;}
.sidebar-brand-logo svg{width:100%;height:100%;display:block;}
.sidebar-brand-text{min-width:0;}
.sidebar-brand-name{font-size:1.04rem;font-weight:800;letter-spacing:-.02em;color:#0f172a;line-height:1.15;}
.sidebar-brand-sub{font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.09em;color:#64748b;margin-top:.18rem;}
hr.sidebar-brand-divider{border:none;border-top:1px solid #e2e8f0;margin:.1rem .25rem .35rem;}
.lang-row{display:flex;align-items:center;gap:.5rem;padding:0 .25rem .55rem;}
.lang-row-label{font-size:.66rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:#64748b;white-space:nowrap;}
</style>
'''

BRAND_BODY = r'''
<div class="sidebar-brand">
  <span class="sidebar-brand-logo">__LOGO__</span>
  <span class="sidebar-brand-text">
    <span class="sidebar-brand-name">__NAME__</span>
    <span class="sidebar-brand-sub">__SUB__</span>
  </span>
</div>
<hr class="sidebar-brand-divider">
'''

CATEGORY_ICONS = {
    "schema": "schema", "volume": "database", "nulls": "quality", "distribution": "distribution",
    "outliers": "anomaly", "duplicates": "warning", "quality": "check", "business_rule": "warning",
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


def inline_logo(size: int = 32, css_class: str = "app-logo") -> str:
    return f'<span class="{css_class}" style="--logo-size:{size}px">{_minify_svg(LOGO_SVG)}</span>'


def _on_lang_change() -> None:
    from core.analysis import has_inputs, run_analysis
    if has_inputs():
        try:
            run_analysis(get_lang())
        except Exception:
            pass


def sidebar_brand() -> None:
    lang = get_lang()
    body = (
        BRAND_BODY
        .replace("__LOGO__", _minify_svg(BRAND_LOGO_SVG))
        .replace("__NAME__", escape(t("brand_name", lang=lang)))
        .replace("__SUB__", escape(t("brand_sub", lang=lang)))
    )
    st.sidebar.markdown(BRAND_STYLE + body, unsafe_allow_html=True)

    labels = {"fr": "FR", "en": "EN"}
    order = ["fr", "en"]
    index = order.index(lang) if lang in order else 0
    st.sidebar.markdown(
        f'<div class="lang-row"><span class="lang-row-label">{escape(t("lang_label", lang=lang))}</span></div>',
        unsafe_allow_html=True,
    )
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
            '<div class="dds-header">',
            '<div class="dds-header-brand">',
            inline_logo(42),
            '<div class="dds-header-text">',
            f'<div class="dds-title">{escape(title)}</div>',
            f'<div class="dds-subtitle">{escape(subtitle)}</div>',
            '</div>', '</div>', '</div>',
        ])
    )


def section(title: str, icon_name: str | None = None) -> None:
    icon_html = icon(icon_name, size=18) if icon_name else ""
    _html("".join(['<div class="dds-section-title">', icon_html, f'<span>{escape(title)}</span>', '</div>']))


def kpi_card(label: str, value: str, helper: str = "", tone: str = "neutral") -> str:
    return "".join([
        f'<div class="kpi-card tone-{escape(tone)}">',
        f'<div class="kpi-label">{escape(label)}</div>',
        f'<div class="kpi-value">{escape(value)}</div>',
        f'<div class="kpi-helper">{escape(helper)}</div>',
        '</div>',
    ])


def kpi_grid(items: list[dict]) -> None:
    cards = "".join(
        kpi_card(
            label=str(item.get("label", "")), value=str(item.get("value", "")),
            helper=str(item.get("helper", "")), tone=str(item.get("tone", "neutral")),
        )
        for item in items
    )
    _html(f'<div class="kpi-grid">{cards}</div>')


def finding_card(finding: Finding) -> None:
    lang = get_lang()
    icon_name = CATEGORY_ICONS.get(finding.category, "info")
    columns = ", ".join(finding.columns) if finding.columns else t("card_na", lang=lang)
    recommendation = finding.recommendation or t("card_no_reco", lang=lang)
    _html(
        "".join([
            f'<article class="finding-card severity-{escape(finding.severity)}">',
            '<header class="finding-card-header">',
            '<div class="finding-card-title">',
            icon(icon_name, size=18),
            f'<strong>{escape(finding.title)}</strong>',
            '</div>',
            f'<span class="badge badge-{escape(finding.severity)}">{escape(finding.severity)}</span>',
            '</header>',
            f'<p class="finding-narrative">{escape(finding.narrative)}</p>',
            '<div class="finding-meta">',
            f'<span><strong>{escape(t("card_columns", lang=lang))}</strong> {escape(columns)}</span>',
            f'<span><strong>{escape(t("card_category", lang=lang))}</strong> {escape(finding.category)}</span>',
            '</div>',
            f'<p class="finding-recommendation"><strong>{escape(t("card_recommendation", lang=lang))}</strong> {escape(recommendation)}</p>',
            '</article>',
        ])
    )


def empty_state(title: str, message: str, icon_name: str = "upload") -> None:
    _html("".join(['<div class="empty-state">', icon(icon_name, size=42), f'<h3>{escape(title)}</h3>', f'<p>{escape(message)}</p>', '</div>']))


def require_analysis() -> dict:
    if "analysis" not in st.session_state:
        lang = get_lang()
        empty_state(t("home_no_analysis", lang=lang), t("home_no_analysis_msg", lang=lang), icon_name="upload")
        st.stop()
    return st.session_state["analysis"]
