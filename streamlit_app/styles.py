"""Custom CSS and color palette for the Streamlit app."""
import streamlit as st

COLORS = {
    "primary": "#2E7D32",
    "primary_light": "#4CAF50",
    "primary_dark": "#1B5E20",
    "accent": "#81C784",
    "bg_card": "#FFFFFF",
    "bg_subtle": "#F1F8E9",
    "text_primary": "#1B1B1B",
    "text_secondary": "#5F6368",
    "severity_high": "#D32F2F",
    "severity_moderate": "#F57C00",
    "severity_low": "#FBC02D",
    "severity_none": "#2E7D32",
}

CUSTOM_CSS = """
<style>
    /* ── Page header ── */
    .page-header {
        padding: 1.5rem 0 1rem 0;
        border-bottom: 3px solid #2E7D32;
        margin-bottom: 2rem;
    }
    .page-header h1 {
        color: #1B5E20;
        font-weight: 700;
        margin: 0;
    }
    .page-header p {
        color: #5F6368;
        font-size: 1.1rem;
        margin-top: 0.3rem;
    }

    /* ── Metric cards ── */
    .metric-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-left: 4px solid #2E7D32;
        border-radius: 8px;
        padding: 1.2rem 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.08);
    }
    .metric-card .metric-value {
        font-size: 2rem;
        font-weight: 700;
        color: #1B5E20;
    }
    .metric-card .metric-label {
        font-size: 0.85rem;
        color: #5F6368;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── Confidence bars ── */
    .confidence-bar-container {
        margin: 0.4rem 0;
    }
    .confidence-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.9rem;
        margin-bottom: 0.2rem;
    }
    .confidence-bar-track {
        background: #E8F5E9;
        border-radius: 4px;
        height: 22px;
        overflow: hidden;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 4px;
        transition: width 0.5s ease;
    }

    /* ── Disease cards ── */
    .disease-card {
        background: #FFFFFF;
        border: 1px solid #E0E0E0;
        border-radius: 10px;
        padding: 1.5rem;
        box-shadow: 0 2px 6px rgba(0,0,0,0.06);
        margin-bottom: 1rem;
    }
    .disease-card h3 {
        color: #1B5E20;
        margin-top: 0;
    }

    /* ── Severity badges ── */
    .severity-badge {
        display: inline-block;
        padding: 0.2rem 0.8rem;
        border-radius: 12px;
        font-size: 0.8rem;
        font-weight: 600;
    }
    .severity-high { background: #FFEBEE; color: #D32F2F; }
    .severity-moderate { background: #FFF3E0; color: #F57C00; }
    .severity-low { background: #FFFDE7; color: #F9A825; }
    .severity-none { background: #E8F5E9; color: #2E7D32; }

    /* ── Instruction steps ── */
    .step-card {
        text-align: center;
        padding: 2rem 1rem;
        background: #F1F8E9;
        border-radius: 10px;
        border: 1px solid #C8E6C9;
    }
    .step-card .step-icon {
        font-size: 2.5rem;
        margin-bottom: 0.5rem;
    }
    .step-card h4 {
        color: #1B5E20;
        margin: 0.5rem 0 0.3rem 0;
    }
    .step-card p {
        color: #5F6368;
        font-size: 0.9rem;
        margin: 0;
    }

    /* ── Upload area ── */
    [data-testid="stFileUploader"] {
        border: 2px dashed #81C784;
        border-radius: 10px;
        padding: 1rem;
    }

    /* ── Sidebar branding ── */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #1B5E20 0%, #2E7D32 100%);
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #FFFFFF;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] li,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] strong,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] em {
        color: #FFFFFF !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.2);
    }

    /* ── General polish ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
    }
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app. Call once in app.py."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
