"""Predict page: upload a leaf image and get disease diagnosis."""
import io

import requests
import streamlit as st
from PIL import Image

from src.inference.predictor import DiseasePredictor
from components import page_header, confidence_bar, severity_badge, disease_card, step_card
from src.data.disease_info import DISEASE_DETAILS

DEFAULT_API_URL = "http://localhost:8000"


@st.cache_resource
def _load_predictor():
    return DiseasePredictor()


def _check_api_health(base_url: str) -> bool:
    """Return True if the REST API is reachable."""
    try:
        r = requests.get(f"{base_url}/api/v1/health", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _predict_online(image: Image.Image, base_url: str) -> dict:
    """Send an image to the REST API and return a result dict matching the offline format."""
    buf = io.BytesIO()
    image.save(buf, format="JPEG")
    buf.seek(0)
    r = requests.post(
        f"{base_url}/api/v1/predict",
        files={"file": ("leaf.jpg", buf, "image/jpeg")},
        timeout=30,
    )
    r.raise_for_status()
    data = r.json()
    return {
        "top_class": data["prediction"],
        "confidence": data["confidence"],
        "top_k_probs": {p["class_name"]: p["confidence"] for p in data["top_k"]},
        "recommendation": data["treatment"],
    }


def show():
    page_header(
        "Crop Disease Diagnosis",
        "Upload a photo of a Tomato, Potato, or Corn leaf to identify diseases "
        "and get treatment recommendations.",
    )

    # ── Inference mode selector ──────────────────────────────────
    mode_col, status_col = st.columns([2, 1])
    with mode_col:
        inference_mode = st.radio(
            "Inference Mode",
            ["Offline (Local Model)", "Online (REST API)"],
            horizontal=True,
        )
    is_online = inference_mode == "Online (REST API)"

    api_url = DEFAULT_API_URL
    if is_online:
        with status_col:
            api_url = st.text_input("API URL", value=DEFAULT_API_URL)
            healthy = _check_api_health(api_url)
            if healthy:
                st.success("API connected", icon="✅")
            else:
                st.error(f"Cannot reach API at {api_url}", icon="❌")

    st.markdown("---")

    # ── Image upload ─────────────────────────────────────────────
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

    col_img, col_result = st.columns([1, 1], gap="large")

    with col_img:
        st.image(image, caption="Uploaded Image", use_container_width=True)

    with col_result:
        spinner_msg = "Sending to API..." if is_online else "Analyzing leaf..."
        with st.spinner(spinner_msg):
            if is_online:
                try:
                    result = _predict_online(image, api_url)
                except requests.ConnectionError:
                    st.error("Could not reach the API server. Is it running?")
                    return
                except requests.HTTPError as e:
                    st.error(f"API error: {e.response.status_code} — {e.response.text}")
                    return
            else:
                predictor = _load_predictor()
                result = predictor.predict(image)

        disease_name = result["top_class"]
        details = DISEASE_DETAILS.get(disease_name, {})
        severity = details.get("severity", "Unknown")

        # Diagnosis header
        st.markdown(f"### {disease_name}")
        st.markdown(severity_badge(severity), unsafe_allow_html=True)
        st.markdown(f"**Confidence: {result['confidence']:.1%}**")

        # Source indicator
        source_label = "REST API" if is_online else "Local Model"
        st.caption(f"Source: {source_label}")

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
