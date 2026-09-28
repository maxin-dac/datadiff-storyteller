from __future__ import annotations
import sys
from pathlib import Path
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.charts import grouped_bar
from components.layout import finding_card, kpi_grid, load_css, page_header, require_analysis, section
from core.i18n import get_lang, t
load_css()
_lang = get_lang()
page_header(t("quality_title", lang=_lang), t("quality_subtitle", lang=_lang))
analysis = require_analysis()
findings = analysis["findings"]; pb = analysis["profile_baseline"]; pc = analysis["profile_compare"]; mappings = analysis["mappings"]
section(t("sec_quality_kpi", lang=_lang), "quality")
rdb = float(pb.get("row_duplicate_rate", 0.0)); rdc = float(pc.get("row_duplicate_rate", 0.0))
nf = [f for f in findings if f.category == "nulls"]; df_ = [f for f in findings if f.category == "duplicates"]; qf = [f for f in findings if f.category == "quality"]
kpi_grid([
    {"label": t("kpi_dup_rows_baseline", lang=_lang), "value": f"{rdb:.2%}", "helper": t("kpi_dup_rows_lines", lang=_lang, value=pb.get("row_duplicate_count", 0)), "tone": "neutral"},
    {"label": t("kpi_dup_rows_compare", lang=_lang), "value": f"{rdc:.2%}", "helper": t("kpi_dup_rows_lines", lang=_lang, value=pc.get("row_duplicate_count", 0)), "tone": "high" if rdc > rdb + 0.01 else "info"},
    {"label": t("kpi_null_findings", lang=_lang), "value": str(len(nf)), "helper": t("kpi_null_findings_help", lang=_lang), "tone": "medium" if nf else "info"},
    {"label": t("kpi_quality_findings", lang=_lang), "value": str(len(qf)), "helper": t("kpi_quality_findings_help", lang=_lang), "tone": "medium" if qf else "info"},
])
section(t("sec_null_compare", lang=_lang), "distribution")
rows = []
for m in mappings:
    if not m.baseline_column or not m.compare_column:
        continue
    br = float(pb["column_profiles"].get(m.baseline_column, {}).get("null_rate", 0.0)); cr = float(pc["column_profiles"].get(m.compare_column, {}).get("null_rate", 0.0))
    rows.append({"column": m.compare_column, "baseline": br, "compare": cr, "delta": cr - br})
if rows:
    qdf = pd.DataFrame(rows).sort_values("delta", ascending=False)
    st.dataframe(qdf, use_container_width=True, hide_index=True, column_config={"baseline": st.column_config.NumberColumn(t("col_baseline", lang=_lang), format="percent"), "compare": st.column_config.NumberColumn(t("col_compare", lang=_lang), format="percent"), "delta": st.column_config.NumberColumn(t("col_delta", lang=_lang), format="percent")})
    cdf = qdf.melt(id_vars="column", var_name="version", value_name="null_rate")
    st.plotly_chart(grouped_bar(cdf, x="column", y="null_rate", color="version", title=t("chart_null_by_col", lang=_lang)), use_container_width=True)
else:
    st.info(t("info_no_common_col", lang=_lang))
section(t("sec_quality_findings", lang=_lang), "warning")
rel = nf + df_ + qf
if rel:
    for f in rel:
        finding_card(f)
else:
    st.success(t("success_no_quality", lang=_lang))
