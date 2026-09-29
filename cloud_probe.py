import sys

import streamlit as st

st.set_page_config(page_title="DataDiff Cloud probe")
st.title("Streamlit startup probe")
st.write(f"Python: {sys.version}")
st.write(f"Streamlit: {st.__version__}")