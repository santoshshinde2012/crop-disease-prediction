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
from pages import predict, dashboard, disease_library

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
    st.Page(predict.show, title="Diagnosis", icon="🔬", default=True),
    st.Page(dashboard.show, title="Model Performance", icon="📊"),
    st.Page(disease_library.show, title="Disease Library", icon="📚"),
])

# ── Sidebar branding (shown on every page) ───────────────────
with st.sidebar:
    st.markdown("---")
    st.markdown(
        "**Crop Disease Classifier**\n\n"
        "MobileNetV2 | 97.8% Accuracy\n\n"
        "PlantVillage Dataset | 15 Classes\n\n"
        "Built with Streamlit\n\n")

# ── Run selected page ────────────────────────────────────────
pages.run()
