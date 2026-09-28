from __future__ import annotations
import json
import sys
from pathlib import Path
import streamlit as st
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from components.layout import finding_card, load_css, page_header, require_analysis, section
from core.i18n import get_lang, t
from core.report_builder import build_markdown_report, render_html_report
from core.scoring import sort_findings
load_css()
_lang = get_lang()
page_header(t("report_title", lang=_lang), t("report_subtitle", lang=_lang))
analysis = require_analysis()
findings = sort_findings(analysis["findings"]); summary = analysis["summary"]; mb = analysis["meta_baseline"]; mc = analysis["meta_compare"]
section(t("sec_exec_summary", lang=_lang), "report")
st.markdown(summary)
section(t("sec_report_findings", lang=_lang), "quality")
if findings:
    for f in findings:
        finding_card(f)
else:
    st.success(t("success_no_finding", lang=_lang))
section(t("sec_exports", lang=_lang), "report")
md = build_markdown_report(summary, findings, mb, mc, lang=_lang)
js = json.dumps({"meta": {"baseline": mb, "compare": mc}, "summary": summary, "findings": [f.to_dict() for f in findings]}, ensure_ascii=False, indent=2)
html = render_html_report(summary, findings, mb, mc, lang=_lang)
c1, c2, c3 = st.columns(3)
with c1:
    st.download_button(label=t("btn_md", lang=_lang), data=md, file_name="datadiff_report.md", mime="text/markdown", use_container_width=True)
with c2:
    st.download_button(label=t("btn_json", lang=_lang), data=js, file_name="datadiff_report.json", mime="application/json", use_container_width=True)
with c3:
    st.download_button(label=t("btn_html", lang=_lang), data=html, file_name="datadiff_report.html", mime="text/html", use_container_width=True)
