from __future__ import annotations

import inspect
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

from components.layout import sidebar_brand
from core.i18n import get_lang, t

# Rail de marque + selecteur de langue dans le sidebar.
# La navigation, elle, est rendue en haut (voir st.navigation plus bas).
sidebar_brand()

if not (hasattr(st, "navigation") and hasattr(st, "Page")):
    st.error('Streamlit trop ancien. Executez : pip install --upgrade "streamlit>=1.49.0"')
    st.stop()

_lang = get_lang()
_page_params = set(inspect.signature(st.Page).parameters)
_supports_group = "group" in _page_params
_supports_default = "default" in _page_params


def make_page(path, title_key, url_path, group_key, default=False):
    kwargs = {"page": path, "title": t(title_key, lang=_lang), "url_path": url_path}
    if _supports_group:
        kwargs["group"] = t(group_key, lang=_lang)
    if _supports_default and default:
        kwargs["default"] = True
    return st.Page(**kwargs)


pages = [
    make_page("pages/0_Accueil.py", "page_home", "accueil", "nav_group_start", False),
    make_page("pages/1_Upload.py", "page_upload", "importer", "nav_group_start", True),
    make_page("pages/2_Overview.py", "page_overview", "vue-ensemble", "nav_group_analysis", False),
    make_page("pages/3_Schema.py", "page_schema", "schema", "nav_group_analysis", False),
    make_page("pages/4_Quality.py", "page_quality", "qualite", "nav_group_analysis", False),
    make_page("pages/5_Distributions.py", "page_distributions", "distributions", "nav_group_analysis", False),
    make_page("pages/6_Anomalies.py", "page_anomalies", "anomalies", "nav_group_analysis", False),
    make_page("pages/7_Rapport.py", "page_report", "rapport", "nav_group_export", False),
]

# Cascade robuste : barre horizontale en haut si la version le permet,
# sinon repli sur le sidebar (comportement precedent).
selected = None
for attempt in (
    lambda: st.navigation(pages, position="top"),
    lambda: st.navigation(pages, position="sidebar", view="expanded"),
    lambda: st.navigation(pages, position="sidebar"),
):
    try:
        selected = attempt()
        break
    except (TypeError, ValueError):
        continue

if selected is None:
    st.error("Impossible d'initialiser la navigation. Mets a jour Streamlit : pip install --upgrade streamlit")
    st.stop()

selected.run()
