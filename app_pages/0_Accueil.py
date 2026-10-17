from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.layout import card, kpi_grid, ok_box, page_header, section, warn_box
from core.i18n import get_lang, t
from core.scoring import sort_findings

_lang = get_lang()
page_header(t("brand_name", lang=_lang), t("home_subtitle", lang=_lang))

section(t("sec_how", lang=_lang))
steps = "".join(f"<li>{t(k, lang=_lang)}</li>" for k in ("guide_1", "guide_2", "guide_3"))
card(f"<ol>{steps}</ol>")

section(t("sec_session", lang=_lang))
if "analysis" not in st.session_state:
    kpi_grid([
        {"label": "BASELINE ROWS", "value": "-", "tone": "neutral"},
        {"label": "COMPARE ROWS", "value": "-", "tone": "neutral"},
        {"label": "COMMON COLS", "value": "-", "tone": "neutral"},
        {"label": "FINDINGS", "value": "-", "tone": "neutral"},
    ])
    warn_box(t("home_no_analysis_msg", lang=_lang))
else:
    a = st.session_state["analysis"]
    findings = sort_findings(a["findings"])
    common = len([m for m in a["mappings"] if m.baseline_column and m.compare_column])
    rb = a.get("meta_baseline", {}).get("rows", "-")
    rc = a.get("meta_compare", {}).get("rows", "-")
    kpi_grid([
        {"label": "BASELINE ROWS", "value": f"{rb:,}".replace(",", " ") if isinstance(rb, int) else str(rb), "tone": "neutral"},
        {"label": "COMPARE ROWS", "value": f"{rc:,}".replace(",", " ") if isinstance(rc, int) else str(rc), "tone": "neutral"},
        {"label": "COMMON COLS", "value": str(common), "tone": "neutral"},
        {"label": "FINDINGS", "value": str(len(findings)), "tone": "neutral"},
    ])
    critical = sum(1 for f in findings if f.severity == "critical")
    ok_box(t("home_has_analysis_2", lang=_lang, total=len(findings), critical=critical))

