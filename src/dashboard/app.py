import streamlit as st
import os
import sys

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if ROOT not in sys.path:
    sys.path.insert(0, ROOT)
st.set_page_config(
    page_title="N100 Financial Intelligence Platform",
    page_icon="📈",
    layout="wide"
)

st.markdown("""
<style>
/* Your existing CSS */
</style>
""", unsafe_allow_html=True)

st.title("📈 N100 Financial Intelligence Platform")

st.write(
    """
Welcome to the **N100 Financial Intelligence Platform**.

Use the **sidebar** to navigate through:

- 🏠 Home
- 🏢 Company Analysis
- 🔎 Stock Screener
- 👥 Peer Analysis
- 🏭 Sector Analysis
- 💼 Portfolio
- 📑 Reports
- ⚙️ Settings
"""
)