from __future__ import annotations
import sys
from pathlib import Path
from typing import Any
import pandas as pd
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.charts import box_compare, categorical_compare, histogram_compare
from components.layout import finding_card, load_css, page_header, require_analysis, section
from core.i18n import get_lang, t
load_css()
_lang = get_lang()
page_header(t("dist_title", lang=_lang), t("dist_subtitle", lang=_lang))
analysis = require_analysis()
df_b = analysis["df_baseline"]; df_c = analysis["df_compare"]; pb = analysis["profile_baseline"]; pc = analysis["profile_compare"]; mappings = analysis["mappings"]; findings = analysis["findings"]
common = [m for m in mappings if m.baseline_column and m.compare_column]
if not common:
    st.info(t("info_no_common_col", lang=_lang)); st.stop()
options = {f"{m.compare_column} ({m.mapping_type})": m for m in common}
sel = st.selectbox(t("sel_column", lang=_lang), list(options.keys()))
mapping: Any = options[sel]
bcol, ccol = mapping.baseline_column, mapping.compare_column
bprof = pb["column_profiles"].get(bcol, {}); cprof = pc["column_profiles"].get(ccol, {})
section(t("sec_dist_stats", lang=_lang), "distribution")
if "numeric" in bprof and "numeric" in cprof:
    keys = ["count", "min", "max", "mean", "std", "q05", "q25", "q50", "q75", "q95", "outlier_rate"]
    sdf = pd.DataFrame([{"metric": k, "baseline": bprof["numeric"].get(k), "compare": cprof["numeric"].get(k)} for k in keys])
    sdf["delta"] = pd.to_numeric(sdf["compare"], errors="coerce") - pd.to_numeric(sdf["baseline"], errors="coerce")
    st.dataframe(sdf, width="stretch", hide_index=True)
    bv = pd.to_numeric(df_b[bcol], errors="coerce").dropna().astype(float); cv = pd.to_numeric(df_c[ccol], errors="coerce").dropna().astype(float)
    if bv.empty or cv.empty:
        st.info(t("info_not_enough_numeric", lang=_lang))
    else:
        n = 25000
        if len(bv) > n: bv = bv.sample(n, random_state=1)
        if len(cv) > n: cv = cv.sample(n, random_state=1)
        st.plotly_chart(histogram_compare(bv, cv, ccol, title=t("chart_hist_title", lang=_lang, column=ccol), y_title=t("axis_density", lang=_lang)), width="stretch")
        box_df = pd.DataFrame({ccol: pd.concat([bv, cv], ignore_index=True), "version": [t("legend_baseline", lang=_lang)] * len(bv) + [t("legend_compare", lang=_lang)] * len(cv)})
        st.plotly_chart(box_compare(box_df, value_column=ccol, version_column="version", column=ccol, title=t("chart_box_title", lang=_lang, column=ccol)), width="stretch")
elif "categorical" in bprof and "categorical" in cprof:
    bs = bprof["categorical"].get("category_shares", {}); cs = cprof["categorical"].get("category_shares", {})
    cats = sorted(set(bs) | set(cs))[:20]
    if not cats:
        st.info(t("info_no_category", lang=_lang))
    else:
        rows = []
        for cat in cats:
            rows.append({"category": cat, "version": t("legend_baseline", lang=_lang), "share": float(bs.get(cat, 0.0))})
            rows.append({"category": cat, "version": t("legend_compare", lang=_lang), "share": float(cs.get(cat, 0.0))})
        cdf = pd.DataFrame(rows)
        st.dataframe(cdf, width="stretch", hide_index=True)
        st.plotly_chart(categorical_compare(cdf, value_column="category", share_column="share", version_column="version", column=ccol, title=t("chart_cat_title", lang=_lang, column=ccol), y_title=t("axis_share", lang=_lang), x_title=t("axis_category", lang=_lang)), width="stretch")
else:
    st.info(t("info_no_profile", lang=_lang))
section(t("sec_dist_findings", lang=_lang), "warning")
cf = [f for f in findings if f.category == "distribution" and ccol in f.columns]
if cf:
    for f in cf:
        finding_card(f)
else:
    st.success(t("success_no_dist", lang=_lang))
