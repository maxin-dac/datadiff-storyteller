from __future__ import annotations

from typing import Optional

import streamlit as st

from core.align import build_column_mappings
from core.diff_engine import generate_findings
from core.narrative import build_executive_summary
from core.profile import profile_dataframe


def store_inputs(df_baseline, df_compare, meta_baseline, meta_compare, use_duckdb: bool = False) -> None:
    st.session_state["inputs"] = {
        "df_baseline": df_baseline,
        "df_compare": df_compare,
        "meta_baseline": meta_baseline,
        "meta_compare": meta_compare,
        "profile_baseline": profile_dataframe(df_baseline),
        "profile_compare": profile_dataframe(df_compare),
        "mappings": build_column_mappings(df_baseline, df_compare),
    }


def run_analysis(lang: Optional[str] = None) -> dict:
    lang = lang or st.session_state.get("lang", "fr")
    inputs = st.session_state.get("inputs")
    if inputs is None:
        raise RuntimeError("No inputs stored in session.")

    findings = generate_findings(
        inputs["df_baseline"],
        inputs["df_compare"],
        inputs["profile_baseline"],
        inputs["profile_compare"],
        inputs["mappings"],
        inputs["meta_baseline"],
        inputs["meta_compare"],
        lang=lang,
    )
    summary = build_executive_summary(
        inputs["meta_baseline"],
        inputs["meta_compare"],
        findings,
        lang=lang,
    )

    analysis = dict(inputs)
    analysis["findings"] = findings
    analysis["summary"] = summary
    analysis["lang"] = lang
    st.session_state["analysis"] = analysis
    return analysis


def has_inputs() -> bool:
    return "inputs" in st.session_state
