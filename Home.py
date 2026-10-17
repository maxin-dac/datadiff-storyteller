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
    initial_sidebar_state="expanded",
)

from components.layout import load_css, on_language_change, render_brand
from core.i18n import get_lang, t

load_css()

VIEW_PATHS = {
    "page_home": "app_pages/0_Accueil.py",
    "page_upload": "app_pages/1_Upload.py",
    "page_overview": "app_pages/2_Overview.py",
    "page_schema": "app_pages/3_Schema.py",
    "page_quality": "app_pages/4_Quality.py",
    "page_distributions": "app_pages/5_Distributions.py",
    "page_anomalies": "app_pages/6_Anomalies.py",
    "page_report": "app_pages/7_Rapport.py",
}


def render_selected_view() -> None:
    lang = get_lang()
    with st.container(key="suite-topbar"):
        nav_col, language_col, brand_col = st.columns([6.7, 1.1, 2.2])
        with nav_col:
            view_key = st.segmented_control(
                t("nav_views", lang=lang),
                options=list(VIEW_PATHS),
                format_func=lambda key: t(key, lang=lang),
                default=st.session_state.get("active_view", "page_home"),
                key="suite-nav",
                required=True,
                label_visibility="collapsed",
                width="stretch",
            )
        with language_col:
            st.segmented_control(
                t("lang_label", lang=lang),
                options=["fr", "en"],
                format_func=lambda value: value.upper(),
                key="lang",
                required=True,
                label_visibility="collapsed",
                on_change=on_language_change,
            )
        with brand_col:
            render_brand()
    st.session_state.active_view = view_key
    runpy.run_path(str(ROOT / VIEW_PATHS[view_key]), run_name="__main__")


selected = st.navigation(
    [st.Page(render_selected_view, title="DataDiff Storyteller", default=True)],
    position="hidden",
)
selected.run()
