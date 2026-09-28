from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.layout import finding_card, load_css, page_header, require_analysis, section
from core.i18n import get_lang, t
load_css()
_lang = get_lang()
page_header(t("schema_title", lang=_lang), t("schema_subtitle", lang=_lang))
analysis = require_analysis()
mappings = analysis["mappings"]; findings = analysis["findings"]
rows = [{"baseline_column": m.baseline_column or "", "compare_column": m.compare_column or "", "mapping_type": m.mapping_type, "confidence": round(m.confidence, 3)} for m in mappings]
section(t("sec_mappings", lang=_lang), "schema")
if rows:
    st.dataframe(pd.DataFrame(rows), width="stretch", hide_index=True, column_config={"confidence": st.column_config.NumberColumn(t("col_confidence", lang=_lang), min_value=0.0, max_value=1.0, format="percent")})
else:
    st.info(t("info_no_mapping", lang=_lang))
section(t("sec_schema_findings", lang=_lang), "warning")
sf = [f for f in findings if f.category == "schema"]
if sf:
    for f in sf:
        finding_card(f)
else:
    st.success(t("success_no_schema", lang=_lang))
