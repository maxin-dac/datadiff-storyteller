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
from core.scoring import calculate_health_score, sort_findings
load_css()
_lang = get_lang()
page_header(t("overview_title", lang=_lang), t("overview_subtitle", lang=_lang))
analysis = require_analysis()
findings = sort_findings(analysis["findings"])
score, grade = calculate_health_score(findings)
mb = analysis["meta_baseline"]; mc = analysis["meta_compare"]
pb = analysis["profile_baseline"]; pc = analysis["profile_compare"]
rb = int(mb.get("rows", 0)); rc = int(mc.get("rows", 0)); dr = rc - rb
dp = dr / rb if rb else None
cb = int(mb.get("columns", 0)); cc = int(mc.get("columns", 0))
crit = sum(1 for f in findings if f.severity == "critical")
high = sum(1 for f in findings if f.severity == "high")
med = sum(1 for f in findings if f.severity == "medium")
section(t("sec_kpi", lang=_lang), "database")
kpi_grid([
    {"label": t("kpi_health", lang=_lang), "value": f"{score}/100", "helper": t("kpi_grade", lang=_lang, grade=grade), "tone": "info" if score >= 75 else "medium" if score >= 50 else "critical"},
    {"label": t("kpi_rows", lang=_lang), "value": f"{rc:,}".replace(",", " "), "helper": t("kpi_rows_baseline", lang=_lang, value=f"{rb:,}".replace(",", " ")), "tone": "neutral"},
    {"label": t("kpi_volume_change", lang=_lang), "value": (f"{dp:+.1%}" if dp is not None else "n/a"), "helper": t("kpi_rows_delta", lang=_lang, value=f"{dr:+,}".replace(",", " ")), "tone": "high" if abs(dp or 0) >= 0.2 else "low" if abs(dp or 0) >= 0.05 else "info"},
    {"label": t("kpi_columns", lang=_lang), "value": f"{cc}", "helper": t("kpi_rows_baseline", lang=_lang, value=f"{cb}"), "tone": "neutral"},
])
kpi_grid([
    {"label": t("kpi_critical", lang=_lang), "value": str(crit), "helper": t("kpi_critical_help", lang=_lang), "tone": "critical" if crit else "info"},
    {"label": t("kpi_high", lang=_lang), "value": str(high), "helper": t("kpi_high_help", lang=_lang), "tone": "high" if high else "info"},
    {"label": t("kpi_medium", lang=_lang), "value": str(med), "helper": t("kpi_medium_help", lang=_lang), "tone": "medium" if med else "info"},
    {"label": t("kpi_total", lang=_lang), "value": str(len(findings)), "helper": t("kpi_total_help", lang=_lang), "tone": "neutral"},
])
section(t("sec_exec_summary", lang=_lang), "report")
st.markdown(analysis["summary"])
section(t("sec_null_rates", lang=_lang), "quality")
rows = []
for m in analysis["mappings"]:
    if not m.baseline_column or not m.compare_column:
        continue
    rows.append({"column": m.compare_column, "baseline": float(pb["column_profiles"].get(m.baseline_column, {}).get("null_rate", 0.0)), "compare": float(pc["column_profiles"].get(m.compare_column, {}).get("null_rate", 0.0))})
if rows:
    ndf = pd.DataFrame(rows).melt(id_vars="column", var_name="version", value_name="null_rate")
    st.plotly_chart(grouped_bar(ndf, x="column", y="null_rate", color="version", title=t("chart_null_title", lang=_lang)), use_container_width=True)
else:
    st.info(t("info_no_common_col", lang=_lang))
section(t("sec_top_findings", lang=_lang), "anomaly")
if findings:
    for f in findings[:10]:
        finding_card(f)
else:
    st.success(t("success_no_finding", lang=_lang))
