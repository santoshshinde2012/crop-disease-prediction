"""Predict page: upload a leaf image and get disease diagnosis."""
import streamlit as st
from PIL import Image

from src.inference.predictor import DiseasePredictor
from components import page_header, confidence_bar, severity_badge, disease_card, step_card
from src.data.disease_info import DISEASE_DETAILS


@st.cache_resource
def _load_predictor():
    return DiseasePredictor()


def show():
    page_header(
        "Crop Disease Diagnosis",
        "Upload a photo of a Tomato, Potato, or Corn leaf to identify diseases "
        "and get treatment recommendations.",
    )

    uploaded_file = st.file_uploader(
        "Choose a leaf image...", type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is None:
        # Instructional placeholder
        st.markdown("<br>", unsafe_allow_html=True)
        c1, c2, c3 = st.columns(3, gap="medium")
        step_card("1.", "Upload", "Take or select a photo of a crop leaf", col=c1)
        step_card("2.", "Analyze", "Our AI model identifies the disease in seconds", col=c2)
        step_card("3.", "Get Results", "Receive diagnosis with treatment recommendations", col=c3)
        return

    image = Image.open(uploaded_file).convert("RGB")
    predictor = _load_predictor()

    col_img, col_result = st.columns([1, 1], gap="large")

    with col_img:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col_result:
        with st.spinner("Analyzing leaf..."):
            result = predictor.predict(image)

        disease_name = result["top_class"]
        details = DISEASE_DETAILS.get(disease_name, {})
        severity = details.get("severity", "Unknown")

        # Diagnosis header
        st.markdown(f"### {disease_name}")
        st.markdown(severity_badge(severity), unsafe_allow_html=True)
        st.markdown(f"**Confidence: {result['confidence']:.1%}**")

        st.markdown("---")

        # Top-5 confidence bars
        st.markdown("**Top-5 Predictions**")
        for i, (cls, prob) in enumerate(result["top_k_probs"].items()):
            confidence_bar(cls, prob, is_top=(i == 0))

    # Full-width treatment section
    st.markdown("---")
    st.subheader("Treatment & Prevention")
    if details:
        disease_card(disease_name, details)
    else:
        st.info(result["recommendation"])
