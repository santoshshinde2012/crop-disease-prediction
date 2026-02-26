"""
Crop Disease Classification — Streamlit App

Usage: streamlit run streamlit_app/app.py
"""
import sys
from pathlib import Path

# Add project root to sys.path so `from src.*` imports work
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import streamlit as st

from styles import inject_css
from views import predict, dashboard, disease_library
from components import sidebar_brand

# ── Page config (must be the first Streamlit command) ─────────
st.set_page_config(
    page_title="Crop Disease Classifier",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ── Global CSS ────────────────────────────────────────────────
inject_css()

# ── Multi-page navigation ────────────────────────────────────
pages = st.navigation([
    st.Page(predict.show, title="Diagnosis", icon="🔬", default=True, url_path="diagnosis"),
    st.Page(dashboard.show, title="Dashboard", icon="📊", url_path="dashboard"),
    st.Page(disease_library.show, title="Disease Library", icon="📚", url_path="disease-library"),
])

# ── Sidebar branding (shown on every page) ───────────────────
with st.sidebar:
    sidebar_brand()
    st.markdown("---")
    st.markdown(
        "**MobileNetV2** architecture trained on the "
        "**PlantVillage** dataset covering **3 crops** "
        "and **15 disease classes**."
    )
    st.markdown(
        "<br><span style='font-size:0.75rem;opacity:0.5'>"
        "Built with Streamlit + PyTorch</span>",
        unsafe_allow_html=True,
    )

# ── Run selected page ────────────────────────────────────────
pages.run()
