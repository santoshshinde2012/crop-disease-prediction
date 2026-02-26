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
    confidence_bar, severity_badge,
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


# ── Render a single compact result card (no top-5) ────────────

def _render_compact_card(mode: str, result: dict):
    """Render a compact result card for one mode (card only, no top-5)."""
    meta = MODE_META[mode]

    if result.get("error"):
        st.error(f"**{meta['short']}** failed:\n\n{result['error']}")
        return

    disease_name = result["top_class"]
    details = DISEASE_DETAILS.get(disease_name, {})
    severity = details.get("severity", "Unknown")
    elapsed = result.get("elapsed_ms", 0)

    st.markdown(f"""
    <div class="result-card">
        <div class="result-card-header">
            <div class="result-card-mode">
                <span class="mode-dot" style="background:{meta['color']}"></span>
                <span class="mode-tag {meta['tag_class']}">{meta['short']}</span>
            </div>
            <span class="result-card-time">{elapsed:.0f} ms</span>
        </div>
        <h2 class="result-card-disease">{disease_name}</h2>
        <div class="result-card-meta">
            {severity_badge(severity)}
        </div>
        <div class="result-card-confidence">{result['confidence']:.1%}</div>
        <p class="result-card-label">Confidence</p>
    </div>
    """, unsafe_allow_html=True)


# ── Prediction chart ──────────────────────────────────────────

def _render_prediction_chart(result: dict):
    """Render a donut chart and model comparison metrics."""
    import plotly.graph_objects as go

    top_k = result.get("top_k_probs", {})
    if not top_k:
        return

    labels = list(top_k.keys())
    values = [v * 100 for v in top_k.values()]

    short_labels = [l.split(": ")[-1] if ": " in l else l for l in labels]

    colors = ['#16a34a', '#86efac', '#bbf7d0', '#dcfce7', '#f0fdf4']

    fig = go.Figure(data=[go.Pie(
        labels=short_labels,
        values=values,
        hole=0.7,
        marker=dict(
            colors=colors[:len(labels)],
            line=dict(color='#ffffff', width=2),
        ),
        textinfo='none',
        hovertemplate='<b>%{label}</b><br>%{value:.1f}%<extra></extra>',
        pull=[0.03] + [0] * (len(labels) - 1),
        direction='clockwise',
        sort=False,
    )])

    top_conf = result.get("confidence", 0) * 100
    disease = result.get("top_class", "")
    short_disease = disease.split(": ")[-1] if ": " in disease else disease

    fig.update_layout(
        showlegend=False,
        annotations=[
            dict(
                text=(
                    f'<b style="font-size:28px;color:#16a34a">{top_conf:.1f}%</b>'
                    f'<br><span style="font-size:11px;color:#94a3b8">confidence</span>'
                ),
                x=0.5, y=0.5,
                font=dict(size=14, family='Inter'),
                showarrow=False,
            )
        ],
        margin=dict(t=10, b=10, l=10, r=10),
        height=280,
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
    )

    st.plotly_chart(fig, use_container_width=True, config={'displayModeBar': False})

    # Legend below chart
    legend_html = []
    for label, value, color in zip(short_labels, values, colors[:len(labels)]):
        legend_html.append(
            f'<div class="chart-legend-item">'
            f'<span class="chart-legend-dot" style="background:{color}"></span>'
            f'<span class="chart-legend-label">{label}</span>'
            f'<span class="chart-legend-value">{value:.1f}%</span>'
            f'</div>'
        )
    st.markdown(
        f'<div class="chart-legend">{"".join(legend_html)}</div>',
        unsafe_allow_html=True,
    )


# ── Treatment columns ────────────────────────────────────────

def _render_treatment_columns(disease_name: str, details: dict):
    """Render treatment info in 3 premium columns."""
    severity = details.get("severity", "Unknown")
    badge = severity_badge(severity)

    st.markdown(f"""
    <div class="treatment-header-row">
        <h3>{disease_name}</h3>
        {badge}
    </div>
    """, unsafe_allow_html=True)

    sym_col, treat_col, prev_col = st.columns(3, gap="medium")

    with sym_col:
        symptoms_html = "".join(f"<li>{s}</li>" for s in details.get("symptoms", []))
        st.markdown(f"""
        <div class="treatment-col-card">
            <div class="treatment-col-header">
                <span class="treatment-col-icon-wrap symptoms-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#ea580c" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><circle cx="12" cy="12" r="10"/><line x1="12" y1="8" x2="12" y2="12"/><line x1="12" y1="16" x2="12.01" y2="16"/></svg>
                </span>
                <span class="treatment-col-title">Symptoms</span>
            </div>
            <ul class="treatment-col-list">{symptoms_html}</ul>
        </div>
        """, unsafe_allow_html=True)

    with treat_col:
        st.markdown(f"""
        <div class="treatment-col-card treatment-col-highlight">
            <div class="treatment-col-header">
                <span class="treatment-col-icon-wrap treatment-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#16a34a" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
                </span>
                <span class="treatment-col-title">Treatment</span>
            </div>
            <p class="treatment-col-text">{details.get("treatment", "N/A")}</p>
        </div>
        """, unsafe_allow_html=True)

    with prev_col:
        prevention_html = "".join(f"<li>{p}</li>" for p in details.get("prevention", []))
        st.markdown(f"""
        <div class="treatment-col-card">
            <div class="treatment-col-header">
                <span class="treatment-col-icon-wrap prevention-icon">
                    <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="#2563eb" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/><polyline points="9 12 12 15 16 10"/></svg>
                </span>
                <span class="treatment-col-title">Prevention</span>
            </div>
            <ul class="treatment-col-list">{prevention_html}</ul>
        </div>
        """, unsafe_allow_html=True)


# ── Page entry point ─────────────────────────────────────────

def show():
    page_header(
        "Crop Disease Diagnosis",
        "Upload a photo of a Tomato, Potato, or Corn leaf to identify diseases "
        "and get treatment recommendations.",
    )

    # ── Inference mode selector (clean, single row) ───────────
    mc1, mc2, mc3 = st.columns(3, gap="small")
    with mc1:
        use_local = st.checkbox("Local Model (PyTorch)", value=True, key="cb_local")
    with mc2:
        use_tflite = st.checkbox("TFLite (Lightweight)", value=False, key="cb_tflite")
    with mc3:
        use_online = st.checkbox("Online API (REST)", value=False, key="cb_online")

    selected_modes = []
    if use_local:
        selected_modes.append(MODE_LOCAL)
    if use_tflite:
        selected_modes.append(MODE_TFLITE)
    if use_online:
        selected_modes.append(MODE_ONLINE)

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

    # ── Image upload + preview in same row ─────────────────────
    upload_col, preview_col = st.columns(2, gap="large")

    with upload_col:
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

    with preview_col:
        st.image(image, caption="Uploaded Leaf Image", use_column_width=True)

    divider()

    # ── Run inference for all selected modes ───────────────────
    section_header("Diagnosis Results")

    results = {}
    with st.spinner(f"Running {len(selected_modes)} model(s)..."):
        for mode in selected_modes:
            results[mode] = _run_inference(mode, image, api_url)

    # Find first successful result
    first_result = None
    first_mode = None
    for mode in selected_modes:
        r = results[mode]
        if not r.get("error"):
            first_result = r
            first_mode = mode
            break

    # ── All model result cards in a row ──────────────────────────
    n = len(selected_modes)
    cols = st.columns(n, gap="medium")
    for col, mode in zip(cols, selected_modes):
        with col:
            _render_compact_card(mode, results[mode])

    # ── Top-5 predictions + chart below ──────────────────────
    if first_result:
        detail_col, chart_col = st.columns([3, 2], gap="large")

        with detail_col:
            st.markdown("**Top-5 Predictions**")
            for i, (cls, prob) in enumerate(first_result["top_k_probs"].items()):
                confidence_bar(cls, prob, is_top=(i == 0))

        with chart_col:
            st.markdown(
                '<p class="chart-title">Prediction Distribution</p>',
                unsafe_allow_html=True,
            )
            _render_prediction_chart(first_result)

    if first_result is None:
        return

    disease_name = first_result["top_class"]
    details = DISEASE_DETAILS.get(disease_name, {})

    divider()

    # ── Treatment & Prevention in 3 columns ────────────────────
    if details:
        section_header("Treatment & Prevention")
        _render_treatment_columns(disease_name, details)
    else:
        section_header("Treatment & Prevention")
        st.info(first_result.get("recommendation", "No treatment information available."))
