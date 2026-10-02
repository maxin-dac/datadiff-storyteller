from __future__ import annotations
import sys
from io import BytesIO
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.layout import page_header, section
from core.analysis import run_analysis, store_inputs
from core.i18n import get_lang, t
from core.ingest import load_csv
_lang = get_lang()
page_header(t("upload_title", lang=_lang), t("upload_subtitle", lang=_lang))
with st.expander(t("sidebar_import_settings", lang=_lang), expanded=False):
    max_rows = st.number_input(t("opt_max_rows", lang=_lang), min_value=100, max_value=2000000, value=200000, step=10000, help=t("opt_max_rows_help", lang=_lang))
    sep_map = {"sep_auto": "auto", "sep_comma": ",", "sep_semicolon": ";", "sep_tab": "\t", "sep_pipe": "|"}
    sep_label = st.selectbox(t("opt_separator", lang=_lang), list(sep_map.keys()), index=0, help=t("opt_separator_help", lang=_lang))
    enc_options = ["auto", "utf-8", "utf-8-sig", "latin1", "cp1252"]
    enc_value = st.selectbox(t("opt_encoding", lang=_lang), enc_options, index=0, help=t("opt_encoding_help", lang=_lang))
    use_duckdb = st.checkbox(t("opt_duckdb", lang=_lang), value=False, help=t("opt_duckdb_help", lang=_lang))
sep_value = sep_map[sep_label]
section(t("sec_files", lang=_lang), "upload")
col1, col2 = st.columns(2)
with col1:
    file_baseline = st.file_uploader(t("file_baseline", lang=_lang), type=["csv"], key="file_baseline", help=t("file_baseline_help", lang=_lang))
with col2:
    file_compare = st.file_uploader(t("file_compare", lang=_lang), type=["csv"], key="file_compare", help=t("file_compare_help", lang=_lang))
section(t("sec_run", lang=_lang), "quality")
if st.button(t("btn_analyze", lang=_lang), type="primary", width="stretch"):
    if file_baseline is None or file_compare is None:
        st.error(t("err_two_files", lang=_lang)); st.stop()
    try:
        raw_b = file_baseline.getvalue(); raw_c = file_compare.getvalue()
        with st.spinner(t("spinner_analyzing", lang=_lang)):
            df_b, meta_b = load_csv(BytesIO(raw_b), max_rows=int(max_rows), sep=sep_value, encoding=enc_value)
            df_c, meta_c = load_csv(BytesIO(raw_c), max_rows=int(max_rows), sep=sep_value, encoding=enc_value)
            meta_b["name"] = file_baseline.name; meta_c["name"] = file_compare.name
            store_inputs(df_b, df_c, meta_b, meta_c, use_duckdb=use_duckdb)
            analysis = run_analysis(_lang)
        common = [m for m in analysis["mappings"] if m.baseline_column and m.compare_column]
        if not common:
            st.warning(t("warn_no_common", lang=_lang))
        st.success(t("success_done", lang=_lang))
    except Exception as exc:
        st.error(t("err_analysis", lang=_lang, error=exc))
section(t("sec_current_session", lang=_lang), "report")
if "analysis" in st.session_state:
    a = st.session_state["analysis"]
    common = len([m for m in a["mappings"] if m.baseline_column and m.compare_column])
    st.write({t("kpi_baseline", lang=_lang): a["meta_baseline"], t("kpi_compare", lang=_lang): a["meta_compare"], t("kpi_findings_count", lang=_lang): len(a["findings"]), t("kpi_common_columns", lang=_lang): common})
    if st.button(t("btn_reset", lang=_lang)):
        st.session_state.pop("analysis", None); st.session_state.pop("inputs", None); st.rerun()
else:
    st.info(t("info_no_analysis_yet", lang=_lang))
