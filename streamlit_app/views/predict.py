"""Predict page: upload a leaf image and get disease diagnosis.

Supports three inference modes (multi-select for comparison):
  1. Local Model — Full PyTorch MobileNetV2
  2. TFLite      — Lightweight TensorFlow Lite runtime
  3. Online API  — Remote REST API endpoint
"""
import io
import time

import requests
import streamlit as st
from PIL import Image

from src.inference.predictor import DiseasePredictor
from components import (
    page_header, section_header, divider,
    confidence_bar, severity_badge, disease_card,
    steps_row, status_pill,
)
from src.data.disease_info import DISEASE_DETAILS

DEFAULT_API_URL = "http://localhost:8000"

MODE_LOCAL = "Local Model (PyTorch)"
MODE_TFLITE = "TFLite (Lightweight)"
MODE_ONLINE = "Online (REST API)"

MODE_META = {
    MODE_LOCAL: {"icon": "🧠", "short": "PyTorch", "tag_class": "mode-tag-pytorch", "color": "#2563eb"},
    MODE_TFLITE: {"icon": "⚡", "short": "TFLite", "tag_class": "mode-tag-tflite", "color": "#d97706"},
    MODE_ONLINE: {"icon": "🌐", "short": "REST API", "tag_class": "mode-tag-api", "color": "#7c3aed"},
}


# ── Cached model loaders ──────────────────────────────────────

@st.cache_resource
def _load_predictor():
    return DiseasePredictor()


@st.cache_resource
def _load_tflite_predictor():
    from src.inference.tflite_predictor import TFLitePredictor
    return TFLitePredictor()


# ── API helpers ───────────────────────────────────────────────

def _check_api_health(base_url: str) -> bool:
    try:
        r = requests.get(f"{base_url}/api/v1/health", timeout=3)
        return r.status_code == 200
    except requests.RequestException:
        return False


def _predict_online(image: Image.Image, base_url: str) -> dict:
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


def _run_inference(mode: str, image: Image.Image, api_url: str) -> dict:
    """Run inference for a single mode. Returns result dict or error dict."""
    t0 = time.perf_counter()
    try:
        if mode == MODE_ONLINE:
            result = _predict_online(image, api_url)
        elif mode == MODE_TFLITE:
            predictor = _load_tflite_predictor()
            result = predictor.predict(image)
        else:
            predictor = _load_predictor()
            result = predictor.predict(image)
        elapsed = (time.perf_counter() - t0) * 1000
        result["elapsed_ms"] = elapsed
        result["error"] = None
        return result
    except Exception as e:
        return {"error": str(e), "elapsed_ms": 0}


# ── Compact mode chip row ─────────────────────────────────────

def _render_mode_chips(local_on: bool, tflite_on: bool, online_on: bool):
    """Render compact inline mode selector chips."""
    modes = [
        ("#2563eb", "Local Model", "PyTorch", local_on),
        ("#d97706", "TFLite", "Lightweight", tflite_on),
        ("#7c3aed", "Online API", "REST", online_on),
    ]
    chips_html = []
    for color, title, desc, active in modes:
        cls = "mode-chip active" if active else "mode-chip"
        check = "&#10003;" if active else ""
        chips_html.append(
            f'<div class="{cls}">'
            f'<span class="chip-dot" style="background:{color}"></span>'
            f'<div class="chip-info">'
            f'<div class="chip-title">{title}</div>'
            f'<div class="chip-desc">{desc}</div>'
            f'</div>'
            f'<div class="chip-check">{check}</div>'
            f'</div>'
        )

    st.markdown(
        f'<div class="mode-selector-row">{"".join(chips_html)}</div>',
        unsafe_allow_html=True,
    )


# ── Render a single result column ─────────────────────────────

def _render_result(mode: str, result: dict):
    """Render a single mode's result inside a column."""
    meta = MODE_META[mode]

    if result.get("error"):
        st.error(f"**{meta['short']}** failed:\n\n{result['error']}")
        return

    disease_name = result["top_class"]
    details = DISEASE_DETAILS.get(disease_name, {})
    severity = details.get("severity", "Unknown")
    elapsed = result.get("elapsed_ms", 0)

    # Result card
    st.markdown(f"""
    <div class="result-header">
        <div style="display:flex;align-items:center;gap:0.5rem;margin-bottom:0.5rem">
            <span style="width:8px;height:8px;border-radius:50%;background:{meta['color']};display:inline-block"></span>
            <span class="mode-tag {meta['tag_class']}">{meta['short']}</span>
            <span style="color:#94a3b8;font-size:0.72rem;margin-left:auto">{elapsed:.0f} ms</span>
        </div>
        <h2>{disease_name}</h2>
        <div style="margin-top:0.4rem">{severity_badge(severity)}</div>
        <div class="result-confidence" style="margin-top:0.4rem">{result['confidence']:.1%}</div>
        <p style="color:#94a3b8;font-size:0.75rem;margin:0.2rem 0 0 0">Confidence</p>
    </div>
    """, unsafe_allow_html=True)

    # Top-5 predictions
    st.markdown("**Top-5 Predictions**")
    for i, (cls, prob) in enumerate(result["top_k_probs"].items()):
        confidence_bar(cls, prob, is_top=(i == 0))


# ── Page entry point ─────────────────────────────────────────

def show():
    page_header(
        "Crop Disease Diagnosis",
        "Upload a photo of a Tomato, Potato, or Corn leaf to identify diseases "
        "and get treatment recommendations.",
    )

    # ── Inference mode selector (compact) ─────────────────────
    st.markdown(
        '<p style="font-size:0.8rem;font-weight:600;color:#64748b;text-transform:uppercase;'
        'letter-spacing:0.06em;margin:0 0 0.2rem">Inference Mode</p>',
        unsafe_allow_html=True,
    )

    mc1, mc2, mc3 = st.columns(3, gap="small")
    with mc1:
        use_local = st.checkbox("Local Model", value=True, key="cb_local")
    with mc2:
        use_tflite = st.checkbox("TFLite", value=False, key="cb_tflite")
    with mc3:
        use_online = st.checkbox("Online API", value=False, key="cb_online")

    selected_modes = []
    if use_local:
        selected_modes.append(MODE_LOCAL)
    if use_tflite:
        selected_modes.append(MODE_TFLITE)
    if use_online:
        selected_modes.append(MODE_ONLINE)

    # Compact visual mode chips
    _render_mode_chips(use_local, use_tflite, use_online)

    # API URL input when online mode selected
    api_url = DEFAULT_API_URL
    if use_online:
        url_col, status_col = st.columns([3, 1])
        with url_col:
            api_url = st.text_input("API Endpoint URL", value=DEFAULT_API_URL)
        with status_col:
            st.markdown("<br>", unsafe_allow_html=True)
            healthy = _check_api_health(api_url)
            pill_html = status_pill("Connected" if healthy else "Unreachable", healthy)
            st.markdown(pill_html, unsafe_allow_html=True)

    if not selected_modes:
        st.warning("Please select at least one inference mode above.")
        return

    divider()

    # ── Image upload ──────────────────────────────────────────
    uploaded_file = st.file_uploader(
        "Upload a leaf image", type=["jpg", "jpeg", "png"],
    )

    if uploaded_file is None:
        steps_row([
            ("Upload", "Take or select a clear photo of a crop leaf"),
            ("Analyze", "AI model identifies the disease in seconds"),
            ("Results", "Get diagnosis with treatment recommendations"),
        ])
        return

    image = Image.open(uploaded_file).convert("RGB")

    # ── Show uploaded image ───────────────────────────────────
    img_col, spacer = st.columns([2, 3])
    with img_col:
        st.image(image, caption="Uploaded Leaf Image", use_column_width=True)

    divider()

    # ── Run inference for all selected modes ──────────────────
    section_header("Diagnosis Results")

    results = {}
    with st.spinner(f"Running {len(selected_modes)} model(s)..."):
        for mode in selected_modes:
            results[mode] = _run_inference(mode, image, api_url)

    # ── Render comparison columns ─────────────────────────────
    n = len(selected_modes)
    if n == 1:
        _render_result(selected_modes[0], results[selected_modes[0]])
    else:
        cols = st.columns(n, gap="medium")
        for col, mode in zip(cols, selected_modes):
            with col:
                _render_result(mode, results[mode])

    # ── Treatment section (from first successful result) ──────
    first_result = None
    for mode in selected_modes:
        r = results[mode]
        if not r.get("error"):
            first_result = r
            break

    if first_result is None:
        return

    disease_name = first_result["top_class"]
    details = DISEASE_DETAILS.get(disease_name, {})

    divider()

    if details:
        section_header("Treatment & Prevention")
        disease_card(disease_name, details)
    else:
        section_header("Treatment & Prevention")
        st.info(first_result["recommendation"])
