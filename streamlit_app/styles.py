"""Premium CSS and color palette for the Crop Disease Classifier."""
import streamlit as st

COLORS = {
    "primary": "#16a34a",
    "primary_light": "#22c55e",
    "primary_dark": "#15803d",
    "primary_darker": "#0f5132",
    "accent": "#86efac",
    "accent_muted": "#bbf7d0",
    "bg_card": "#ffffff",
    "bg_subtle": "#f0fdf4",
    "bg_page": "#fafbfc",
    "text_primary": "#0f172a",
    "text_secondary": "#64748b",
    "border": "#e2e8f0",
    "severity_high": "#dc2626",
    "severity_moderate": "#ea580c",
    "severity_low": "#ca8a04",
    "severity_none": "#16a34a",
}

CUSTOM_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap');

    /* ── Global ── */
    .stApp {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
        background: #fafbfc;
    }

    /* ── Page Header ── */
    .page-header {
        padding: 1.5rem 0 1.2rem 0;
        margin-bottom: 1.5rem;
        position: relative;
    }
    .page-header::after {
        content: '';
        position: absolute;
        bottom: 0;
        left: 0;
        width: 60px;
        height: 3px;
        background: linear-gradient(90deg, #16a34a, #22c55e);
        border-radius: 2px;
    }
    .page-header h1 {
        color: #0f172a;
        font-weight: 800;
        font-size: 1.75rem;
        margin: 0;
        letter-spacing: -0.025em;
    }
    .page-header p {
        color: #64748b;
        font-size: 0.95rem;
        margin-top: 0.4rem;
        font-weight: 400;
        line-height: 1.6;
    }

    /* ── Section Headers ── */
    .section-header {
        display: flex;
        align-items: center;
        gap: 0.45rem;
        margin: 1.2rem 0 0.8rem 0;
        padding-bottom: 0.5rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .section-header::before {
        content: '';
        width: 6px;
        height: 6px;
        border-radius: 50%;
        background: #16a34a;
        flex-shrink: 0;
    }
    .section-header h3 {
        margin: 0;
        font-size: 0.9rem;
        font-weight: 700;
        color: #1e293b;
        letter-spacing: -0.01em;
    }

    /* ── Dividers ── */
    .divider {
        height: 1px;
        background: linear-gradient(90deg, transparent, #e2e8f0, transparent);
        margin: 1.5rem 0;
    }

    /* ── Metric Cards ── */
    .metric-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.25rem 1.25rem 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.25s ease;
        position: relative;
        overflow: hidden;
    }
    .metric-card::before {
        content: '';
        position: absolute;
        top: 0;
        left: 0;
        right: 0;
        height: 3px;
        background: linear-gradient(90deg, #16a34a, #22c55e, #86efac);
    }
    .metric-card:hover {
        transform: translateY(-2px);
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        border-color: #bbf7d0;
    }
    .metric-card .metric-label {
        font-size: 0.7rem;
        color: #94a3b8;
        text-transform: uppercase;
        letter-spacing: 0.08em;
        font-weight: 600;
        margin-bottom: 0.4rem;
    }
    .metric-card .metric-value {
        font-size: 1.8rem;
        font-weight: 800;
        color: #15803d;
        letter-spacing: -0.02em;
        line-height: 1.2;
    }

    /* ── Confidence Bars ── */
    .confidence-bar-container {
        margin: 0.5rem 0;
    }
    .confidence-bar-label {
        display: flex;
        justify-content: space-between;
        font-size: 0.82rem;
        margin-bottom: 0.25rem;
        color: #334155;
    }
    .confidence-bar-track {
        background: #f1f5f9;
        border-radius: 6px;
        height: 8px;
        overflow: hidden;
    }
    .confidence-bar-fill {
        height: 100%;
        border-radius: 6px;
        transition: width 0.6s cubic-bezier(0.4, 0, 0.2, 1);
    }

    /* ── Disease Cards ── */
    .disease-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1.5rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        margin-bottom: 0.8rem;
        transition: all 0.25s ease;
    }
    .disease-card:hover {
        box-shadow: 0 6px 16px rgba(0,0,0,0.06);
        border-color: #bbf7d0;
    }
    .disease-card h3 {
        color: #0f172a;
        margin-top: 0;
        font-weight: 700;
        font-size: 1.05rem;
    }
    .disease-card .card-section-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin: 1rem 0 0.35rem;
    }
    .disease-card ul {
        padding-left: 1.2rem;
        color: #475569;
        margin: 0;
    }
    .disease-card li {
        margin-bottom: 0.25rem;
        line-height: 1.5;
        font-size: 0.88rem;
    }
    .disease-card p {
        color: #475569;
        font-size: 0.88rem;
        line-height: 1.6;
    }

    /* ── Severity Badges ── */
    .severity-badge {
        display: inline-flex;
        align-items: center;
        gap: 0.35rem;
        padding: 0.25rem 0.75rem;
        border-radius: 100px;
        font-size: 0.75rem;
        font-weight: 600;
        letter-spacing: 0.02em;
    }
    .severity-high { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }
    .severity-moderate { background: #fff7ed; color: #ea580c; border: 1px solid #fed7aa; }
    .severity-low { background: #fefce8; color: #ca8a04; border: 1px solid #fde68a; }
    .severity-none { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }

    /* ── How-it-works steps (inline row) ── */
    .steps-row {
        display: flex;
        gap: 0;
        margin: 0.8rem 0;
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        overflow: hidden;
    }
    .step-item {
        flex: 1;
        display: flex;
        align-items: center;
        gap: 0.75rem;
        padding: 1rem 1.2rem;
        position: relative;
    }
    .step-item:not(:last-child)::after {
        content: '';
        position: absolute;
        right: 0;
        top: 20%;
        height: 60%;
        width: 1px;
        background: #e2e8f0;
    }
    .step-item .step-num {
        flex-shrink: 0;
        width: 28px;
        height: 28px;
        border-radius: 50%;
        background: linear-gradient(135deg, #16a34a, #22c55e);
        color: #ffffff;
        font-weight: 700;
        font-size: 0.78rem;
        display: flex;
        align-items: center;
        justify-content: center;
    }
    .step-item .step-text h4 {
        margin: 0;
        font-size: 0.85rem;
        font-weight: 700;
        color: #0f172a;
        line-height: 1.3;
    }
    .step-item .step-text p {
        margin: 0;
        font-size: 0.75rem;
        color: #94a3b8;
        line-height: 1.4;
    }

    /* ── Checkbox as toggle cards ── */
    [data-testid="stCheckbox"] {
        background: #ffffff;
        border: 1.5px solid #e2e8f0;
        border-radius: 12px;
        padding: 0.65rem 0.85rem !important;
        transition: all 0.2s ease;
    }
    [data-testid="stCheckbox"]:hover {
        border-color: #16a34a;
        box-shadow: 0 2px 8px rgba(22,163,74,0.08);
    }
    [data-testid="stCheckbox"]:has(input:checked) {
        border-color: #16a34a;
        background: #f0fdf4;
        box-shadow: 0 2px 8px rgba(22,163,74,0.1);
    }

    /* Legacy mode-tag (used in result headers) */
    .mode-tag-pytorch { background: #eff6ff; color: #2563eb; }
    .mode-tag-tflite { background: #fef3c7; color: #d97706; }
    .mode-tag-api { background: #f3e8ff; color: #7c3aed; }
    .mode-tag {
        display: inline-block;
        padding: 0.15rem 0.55rem;
        border-radius: 100px;
        font-size: 0.68rem;
        font-weight: 600;
    }

    /* ── Result Card (redesigned) ── */
    .result-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        margin-bottom: 1rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.25s ease;
    }
    .result-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        border-color: #bbf7d0;
    }
    .result-card-header {
        display: flex;
        align-items: center;
        justify-content: space-between;
        margin-bottom: 0.75rem;
    }
    .result-card-mode {
        display: flex;
        align-items: center;
        gap: 0.5rem;
    }
    .mode-dot {
        width: 8px;
        height: 8px;
        border-radius: 50%;
        display: inline-block;
    }
    .result-card-time {
        color: #94a3b8;
        font-size: 0.72rem;
        font-weight: 500;
        background: #f8fafc;
        padding: 0.2rem 0.6rem;
        border-radius: 100px;
    }
    .result-card-disease {
        color: #0f172a;
        margin: 0 0 0.5rem 0;
        font-weight: 800;
        font-size: 1.2rem;
        letter-spacing: -0.02em;
    }
    .result-card-meta {
        margin: 0.4rem 0;
    }
    .result-card-confidence {
        font-size: 2.5rem;
        font-weight: 800;
        color: #16a34a;
        letter-spacing: -0.03em;
        line-height: 1.1;
        margin-top: 0.5rem;
    }
    .result-card-label {
        color: #94a3b8;
        font-size: 0.75rem;
        margin: 0.15rem 0 0 0;
        font-weight: 500;
    }

    /* ── Model Comparison Card ── */
    .compare-card {
        background: #f8fafc;
        border: 1px solid #e2e8f0;
        border-radius: 14px;
        padding: 1rem 1.25rem;
        margin-top: 0.5rem;
    }
    .compare-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin-bottom: 0.6rem;
    }
    .compare-row {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        padding: 0.45rem 0;
        border-bottom: 1px solid #f1f5f9;
    }
    .compare-row:last-child { border-bottom: none; }
    .compare-mode {
        font-weight: 600;
        font-size: 0.82rem;
        color: #334155;
        flex: 1;
    }
    .compare-conf {
        font-weight: 700;
        font-size: 0.82rem;
        color: #16a34a;
    }
    .compare-time {
        font-size: 0.72rem;
        color: #94a3b8;
        min-width: 42px;
        text-align: right;
    }
    .compare-error {
        font-size: 0.78rem;
        color: #dc2626;
        font-weight: 600;
    }

    /* ── Chart Container ── */
    .chart-container-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.25rem;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
    }
    .chart-title {
        font-size: 0.72rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #94a3b8;
        margin: 0 0 0.25rem 0;
        text-align: center;
    }
    .chart-legend {
        display: flex;
        flex-direction: column;
        gap: 0.35rem;
        padding: 0.5rem 0.25rem 0;
    }
    .chart-legend-item {
        display: flex;
        align-items: center;
        gap: 0.5rem;
        font-size: 0.78rem;
    }
    .chart-legend-dot {
        width: 10px;
        height: 10px;
        border-radius: 3px;
        flex-shrink: 0;
    }
    .chart-legend-label {
        color: #475569;
        flex: 1;
        font-weight: 500;
    }
    .chart-legend-value {
        color: #16a34a;
        font-weight: 700;
        font-size: 0.78rem;
    }

    /* ── Treatment Columns ── */
    .treatment-header-row {
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 0.5rem;
        margin-bottom: 1rem;
    }
    .treatment-header-row h3 {
        margin: 0;
        font-weight: 700;
        color: #0f172a;
        font-size: 1.1rem;
    }
    .treatment-col-card {
        background: #ffffff;
        border: 1px solid #e2e8f0;
        border-radius: 16px;
        padding: 1.5rem;
        height: 100%;
        box-shadow: 0 1px 3px rgba(0,0,0,0.04);
        transition: all 0.25s ease;
    }
    .treatment-col-card:hover {
        box-shadow: 0 8px 24px rgba(0,0,0,0.06);
        transform: translateY(-2px);
    }
    .treatment-col-highlight {
        background: linear-gradient(135deg, #f0fdf4, #ffffff);
        border-color: #bbf7d0;
    }
    .treatment-col-header {
        display: flex;
        align-items: center;
        gap: 0.6rem;
        margin-bottom: 1rem;
        padding-bottom: 0.75rem;
        border-bottom: 1px solid #f1f5f9;
    }
    .treatment-col-icon-wrap {
        width: 36px;
        height: 36px;
        border-radius: 10px;
        display: flex;
        align-items: center;
        justify-content: center;
        flex-shrink: 0;
    }
    .symptoms-icon { background: #fff7ed; }
    .treatment-icon { background: #f0fdf4; }
    .prevention-icon { background: #eff6ff; }
    .treatment-col-title {
        font-size: 0.78rem;
        font-weight: 700;
        text-transform: uppercase;
        letter-spacing: 0.06em;
        color: #64748b;
    }
    .treatment-col-list {
        padding-left: 1.1rem;
        margin: 0;
        color: #475569;
    }
    .treatment-col-list li {
        margin-bottom: 0.5rem;
        line-height: 1.55;
        font-size: 0.85rem;
    }
    .treatment-col-text {
        color: #475569;
        font-size: 0.85rem;
        line-height: 1.65;
        margin: 0;
    }

    /* ── Status indicators ── */
    .status-pill {
        display: inline-flex;
        align-items: center;
        gap: 0.4rem;
        padding: 0.3rem 0.8rem;
        border-radius: 100px;
        font-size: 0.78rem;
        font-weight: 600;
    }
    .status-online { background: #f0fdf4; color: #16a34a; border: 1px solid #bbf7d0; }
    .status-offline { background: #fef2f2; color: #dc2626; border: 1px solid #fecaca; }

    /* ── Upload area ── */
    [data-testid="stFileUploader"] {
        border: 1.5px dashed #cbd5e1;
        border-radius: 12px;
        padding: 0.8rem;
        background: #ffffff;
        transition: all 0.25s ease;
    }
    [data-testid="stFileUploader"]:hover {
        border-color: #16a34a;
        background: #fafffe;
    }

    /* ═══════════════════════════════════════════════════════════
       SIDEBAR — dark green theme with visible navigation
       ═══════════════════════════════════════════════════════════ */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #052e16 0%, #14532d 50%, #166534 100%) !important;
    }
    [data-testid="stSidebar"] > div:first-child {
        background: transparent !important;
    }

    /* ── Navigation link styling ── */
    [data-testid="stSidebar"] a,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"],
    [data-testid="stSidebar"] nav a,
    [data-testid="stSidebar"] ul[role="listbox"] li a,
    [data-testid="stSidebar"] ul li a {
        color: rgba(255,255,255,0.8) !important;
        border-radius: 10px !important;
        margin: 1px 4px !important;
        transition: all 0.2s ease !important;
        font-weight: 500 !important;
        font-size: 0.9rem !important;
    }
    [data-testid="stSidebar"] a:hover,
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"]:hover,
    [data-testid="stSidebar"] nav a:hover,
    [data-testid="stSidebar"] ul li a:hover {
        background: rgba(255,255,255,0.1) !important;
        color: #ffffff !important;
    }
    /* Active/selected nav link */
    [data-testid="stSidebar"] a[aria-selected="true"],
    [data-testid="stSidebar"] [data-testid="stSidebarNavLink"][aria-selected="true"],
    [data-testid="stSidebar"] nav a[aria-selected="true"],
    [data-testid="stSidebar"] ul li a[aria-selected="true"] {
        background: rgba(255,255,255,0.15) !important;
        color: #ffffff !important;
        font-weight: 700 !important;
    }

    /* All text within nav links — spans, p, divs */
    [data-testid="stSidebar"] a span,
    [data-testid="stSidebar"] a p,
    [data-testid="stSidebar"] a div,
    [data-testid="stSidebar"] nav span,
    [data-testid="stSidebar"] nav p,
    [data-testid="stSidebar"] li span,
    [data-testid="stSidebar"] li p {
        color: rgba(255,255,255,0.8) !important;
    }
    [data-testid="stSidebar"] a[aria-selected="true"] span,
    [data-testid="stSidebar"] a[aria-selected="true"] p,
    [data-testid="stSidebar"] a[aria-selected="true"] div {
        color: #ffffff !important;
    }

    /* Force all sidebar markdown text white */
    [data-testid="stSidebar"] [data-testid="stMarkdown"] {
        color: #ffffff;
    }
    [data-testid="stSidebar"] [data-testid="stMarkdown"] p,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] li,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] strong,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] em,
    [data-testid="stSidebar"] [data-testid="stMarkdown"] span {
        color: #ffffff !important;
    }
    [data-testid="stSidebar"] hr {
        border-color: rgba(255,255,255,0.1);
    }

    /* Sidebar brand */
    .sidebar-brand {
        text-align: center;
        padding: 0.8rem 0;
    }
    .sidebar-brand h2 {
        color: #ffffff;
        font-weight: 800;
        font-size: 1.15rem;
        margin: 0 0 0.3rem 0;
        letter-spacing: -0.01em;
    }
    .sidebar-brand .brand-tag {
        display: inline-block;
        background: rgba(134,239,172,0.2);
        color: #86efac;
        padding: 0.2rem 0.7rem;
        border-radius: 100px;
        font-size: 0.65rem;
        font-weight: 600;
        letter-spacing: 0.04em;
    }
    .sidebar-stats {
        display: flex;
        justify-content: space-between;
        gap: 0.4rem;
        margin-top: 0.8rem;
    }
    .sidebar-stat {
        text-align: center;
        flex: 1;
        background: rgba(255,255,255,0.06);
        border-radius: 10px;
        padding: 0.55rem 0.25rem;
        border: 1px solid rgba(255,255,255,0.06);
    }
    .sidebar-stat .stat-value {
        font-size: 1rem;
        font-weight: 700;
        color: #86efac;
    }
    .sidebar-stat .stat-label {
        font-size: 0.6rem;
        color: rgba(255,255,255,0.5);
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }

    /* ── Tab overrides ── */
    .stTabs [data-baseweb="tab"] {
        font-weight: 600;
        font-size: 0.88rem;
    }

    /* ── Checkbox label styling ── */
    [data-testid="stCheckbox"] label {
        gap: 0.4rem !important;
    }
    [data-testid="stCheckbox"] label p {
        font-weight: 600;
        font-size: 0.82rem;
    }

    /* ── Warning / Alert box ── */
    [data-testid="stAlert"] {
        border-radius: 12px;
    }

    /* ── Selectbox / inputs ── */
    [data-testid="stSelectbox"] label p,
    [data-testid="stTextInput"] label p {
        font-weight: 600;
        font-size: 0.85rem;
        color: #475569;
    }

    /* ── Dataframe styling ── */
    [data-testid="stDataFrame"] {
        border-radius: 12px;
        overflow: hidden;
    }

    /* ── General polish ── */
    .block-container {
        max-width: 1200px;
        padding-top: 2rem;
    }

    /* Section subheading override (Streamlit ##### ) */
    .stMarkdown h5 {
        font-size: 0.95rem !important;
        font-weight: 700 !important;
        color: #1e293b !important;
        letter-spacing: -0.01em;
    }
</style>
"""


def inject_css():
    """Inject custom CSS into the Streamlit app. Call once in app.py."""
    st.markdown(CUSTOM_CSS, unsafe_allow_html=True)
