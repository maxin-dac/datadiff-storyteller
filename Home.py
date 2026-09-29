from __future__ import annotations

import runpy
from pathlib import Path

import streamlit as st

ROOT = Path(__file__).resolve().parent
LOGO_PATH = ROOT / "assets" / "logo.svg"

st.set_page_config(
    page_title="DataDiff Storyteller",
    page_icon=str(LOGO_PATH) if LOGO_PATH.exists() else None,
    layout="wide",
    initial_sidebar_state="auto",
)

from components.layout import load_css, sidebar_brand
from core.i18n import get_lang, t

load_css()
sidebar_brand()

_lang = get_lang()
VIEW_PATHS = {
    "page_home": "pages/0_Accueil.py",
    "page_upload": "pages/1_Upload.py",
    "page_overview": "pages/2_Overview.py",
    "page_schema": "pages/3_Schema.py",
    "page_quality": "pages/4_Quality.py",
    "page_distributions": "pages/5_Distributions.py",
    "page_anomalies": "pages/6_Anomalies.py",
    "page_report": "pages/7_Rapport.py",
}


def render_selected_view() -> None:
    with st.container(key="dds-top-nav"):
        view_key = st.segmented_control(
            t("nav_views", lang=_lang),
            options=list(VIEW_PATHS),
            format_func=lambda key: t(key, lang=_lang),
            default="page_upload",
            key="active_view",
            label_visibility="collapsed",
            width="stretch",
            required=True,
        )
    runpy.run_path(str(ROOT / VIEW_PATHS[view_key]), run_name="__main__")


selected = st.navigation(
    [st.Page(render_selected_view, title="DataDiff Storyteller", default=True)],
    position="hidden",
)
selected.run()
