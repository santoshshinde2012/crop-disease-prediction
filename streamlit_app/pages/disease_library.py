"""Disease Library page: browse all 15 crop disease classes."""
import streamlit as st

from components import page_header, disease_card
from src.data.disease_info import DISEASE_DETAILS


def show():
    page_header(
        "Disease Library",
        "Browse all 15 crop disease classes with symptoms, treatment, and prevention.",
    )

    # ── Filter by crop ──
    crops = ["All", "Corn", "Potato", "Tomato"]
    selected_crop = st.selectbox("Filter by crop", crops, index=0)

    if selected_crop == "All":
        filtered = DISEASE_DETAILS
    else:
        filtered = {
            k: v for k, v in DISEASE_DETAILS.items() if v["crop"] == selected_crop
        }

    st.markdown(f"**Showing {len(filtered)} of {len(DISEASE_DETAILS)} classes**")
    st.markdown("---")

    # ── Two-column card grid ──
    items = list(filtered.items())
    for i in range(0, len(items), 2):
        cols = st.columns(2, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(items):
                name, details = items[i + j]
                with col:
                    disease_card(name, details)
