from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.layout import empty_state, html_block, page_header, section
from core.i18n import get_lang, t
from core.scoring import sort_findings
_lang = get_lang()
page_header(t("home_title", lang=_lang), t("home_subtitle", lang=_lang))
section(t("sec_how", lang=_lang), "info")
html_block("".join(['<div class="objective-card">', '<ol class="guide-list">',
    f'<li>{t("guide_1", lang=_lang)}</li>', f'<li>{t("guide_2", lang=_lang)}</li>', f'<li>{t("guide_3", lang=_lang)}</li>',
    '</ol>', '</div>']))
section(t("sec_session", lang=_lang), "database")
if "analysis" not in st.session_state:
    empty_state(t("home_no_analysis", lang=_lang), t("home_no_analysis_msg", lang=_lang), icon_name="upload")
else:
    findings = sort_findings(st.session_state["analysis"]["findings"])
    critical = sum(1 for f in findings if f.severity == "critical")
    html_block("".join(['<div class="objective-card">',
        f'<p>{t("home_has_analysis_1", lang=_lang)}</p>',
        f'<p>{t("home_has_analysis_2", lang=_lang, total=len(findings), critical=critical)}</p>',
        f'<p>{t("home_has_analysis_3", lang=_lang)}</p>', '</div>']))
