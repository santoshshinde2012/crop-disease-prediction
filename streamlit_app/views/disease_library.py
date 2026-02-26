"""Disease Library page: browse all 15 crop disease classes."""
import streamlit as st

from components import page_header, section_header, divider, disease_card
from src.data.disease_info import DISEASE_DETAILS


def show():
    page_header(
        "Disease Library",
        "Browse all 15 crop disease classes with symptoms, treatment, and prevention.",
    )

    # ── Filter controls ──
    section_header("Filter & Search")

    filter_col, search_col, count_col = st.columns([1, 2, 1], gap="medium")

    with filter_col:
        crops = ["All Crops", "Corn", "Potato", "Tomato"]
        selected_crop = st.selectbox("Filter by crop", crops, index=0)

    with search_col:
        search_query = st.text_input("Search diseases...", placeholder="e.g. blight, rust, mold")

    # Apply filters
    if selected_crop == "All Crops":
        filtered = DISEASE_DETAILS
    else:
        filtered = {
            k: v for k, v in DISEASE_DETAILS.items() if v["crop"] == selected_crop
        }

    if search_query:
        query = search_query.lower()
        filtered = {
            k: v for k, v in filtered.items()
            if query in k.lower() or query in v.get("treatment", "").lower()
        }

    with count_col:
        st.markdown("<br>", unsafe_allow_html=True)
        st.markdown(
            f'<span style="color:#64748b;font-size:0.85rem">'
            f'Showing <strong>{len(filtered)}</strong> of <strong>{len(DISEASE_DETAILS)}</strong> classes'
            f'</span>',
            unsafe_allow_html=True,
        )

    divider()

    if not filtered:
        st.info("No diseases match your search criteria.")
        return

    # ── Two-column card grid ──
    items = list(filtered.items())
    for i in range(0, len(items), 2):
        cols = st.columns(2, gap="medium")
        for j, col in enumerate(cols):
            if i + j < len(items):
                name, details = items[i + j]
                with col:
                    disease_card(name, details)
