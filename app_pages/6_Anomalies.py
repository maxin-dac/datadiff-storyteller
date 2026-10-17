from __future__ import annotations
import sys
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.layout import finding_card, page_header, require_analysis, section
from core.i18n import get_lang, t
_lang = get_lang()
page_header(t("anom_title", lang=_lang), t("anom_subtitle", lang=_lang))
analysis = require_analysis()
af = [f for f in analysis["findings"] if f.category in {"outliers", "business_rule"}]
section(t("sec_anom_summary", lang=_lang), "anomaly")
if not af:
    st.success(t("success_no_anom", lang=_lang))
else:
    st.write(t("anom_count", lang=_lang, value=len(af)))
section(t("sec_anom_details", lang=_lang), "warning")
for f in af:
    finding_card(f)
    if f.evidence:
        with st.expander(t("exp_sample_values", lang=_lang)):
            st.json(f.evidence)
