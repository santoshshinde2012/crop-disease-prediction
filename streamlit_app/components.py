"""Reusable premium UI components for the Crop Disease Classifier."""
import streamlit as st

from styles import COLORS


def page_header(title: str, subtitle: str = ""):
    """Render a styled page header with gradient accent bar."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-header"><h1>{title}</h1>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def section_header(title: str):
    """Render a styled section header with green dot accent."""
    st.markdown(
        f'<div class="section-header"><h3>{title}</h3></div>',
        unsafe_allow_html=True,
    )


def divider():
    """Render a subtle gradient divider."""
    st.markdown('<div class="divider"></div>', unsafe_allow_html=True)


def metric_card(label: str, value: str, col=None):
    """Render a premium metric card with top gradient accent."""
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)


def confidence_bar(class_name: str, probability: float, is_top: bool = False):
    """Render a sleek confidence bar with label and percentage."""
    pct = probability * 100
    weight = "700" if is_top else "400"
    bg = (
        f"linear-gradient(90deg, {COLORS['primary']}, {COLORS['primary_light']})"
        if is_top
        else "#e2e8f0"
    )
    st.markdown(f"""
    <div class="confidence-bar-container">
        <div class="confidence-bar-label">
            <span style="font-weight:{weight}">{class_name}</span>
            <span style="font-weight:{weight}">{pct:.1f}%</span>
        </div>
        <div class="confidence-bar-track">
            <div class="confidence-bar-fill" style="width:{pct}%; background:{bg}"></div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def severity_badge(severity: str) -> str:
    """Return an HTML string for a colored severity pill badge."""
    css_class = {
        "High": "severity-high",
        "Moderate": "severity-moderate",
        "Low": "severity-low",
        "None": "severity-none",
    }.get(severity, "severity-low")
    return f'<span class="severity-badge {css_class}">Severity: {severity}</span>'


def disease_card(name: str, details: dict):
    """Render a premium disease information card."""
    badge = severity_badge(details["severity"])
    symptoms_html = "".join(f"<li>{s}</li>" for s in details["symptoms"])
    prevention_items = details.get("prevention", [])
    prevention_html = ""
    if prevention_items:
        items = "".join(f"<li>{p}</li>" for p in prevention_items)
        prevention_html = (
            '<div class="card-section-title">Prevention</div>'
            f'<ul>{items}</ul>'
        )

    st.markdown(f"""
    <div class="disease-card">
        <div style="display:flex; justify-content:space-between; align-items:flex-start; flex-wrap:wrap; gap:0.5rem">
            <h3 style="margin:0">{name}</h3>
            {badge}
        </div>
        <div class="card-section-title">Symptoms</div>
        <ul>{symptoms_html}</ul>
        <div class="card-section-title">Treatment</div>
        <p style="margin:0">{details["treatment"]}</p>
        {prevention_html}
    </div>
    """, unsafe_allow_html=True)


def steps_row(steps: list[tuple[str, str]]):
    """Render a compact horizontal how-it-works strip.

    Args:
        steps: list of (title, description) tuples.
    """
    items = []
    for i, (title, desc) in enumerate(steps, 1):
        items.append(
            f'<div class="step-item">'
            f'<div class="step-num">{i}</div>'
            f'<div class="step-text"><h4>{title}</h4><p>{desc}</p></div>'
            f'</div>'
        )
    st.markdown(
        f'<div class="steps-row">{"".join(items)}</div>',
        unsafe_allow_html=True,
    )


def step_card(icon: str, title: str, description: str, number: int = 0, col=None):
    """Render an instructional step card with optional step number."""
    number_html = f'<div class="step-number">{number}</div>' if number else ""
    html = f"""
    <div class="step-card">
        {number_html}
        <div class="step-icon">{icon}</div>
        <h4>{title}</h4>
        <p>{description}</p>
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)


def mode_selector_card(icon: str, title: str, description: str, tag: str,
                       tag_class: str, is_active: bool = False, col=None):
    """Render a mode selection card (Local Model / TFLite / Online API)."""
    active_cls = "active" if is_active else ""
    html = f"""
    <div class="mode-card {active_cls}">
        <div class="mode-icon">{icon}</div>
        <h4>{title}</h4>
        <p>{description}</p>
        <span class="mode-tag {tag_class}">{tag}</span>
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)


def sidebar_brand():
    """Render premium sidebar branding with stats."""
    st.markdown("""
    <div class="sidebar-brand">
        <h2>Crop Disease Classifier</h2>
        <span class="brand-tag">AI-POWERED DIAGNOSTICS</span>
        <div class="sidebar-stats">
            <div class="sidebar-stat">
                <div class="stat-value">97.8%</div>
                <div class="stat-label">Accuracy</div>
            </div>
            <div class="sidebar-stat">
                <div class="stat-value">15</div>
                <div class="stat-label">Classes</div>
            </div>
            <div class="sidebar-stat">
                <div class="stat-value">~9ms</div>
                <div class="stat-label">Speed</div>
            </div>
        </div>
    </div>
    """, unsafe_allow_html=True)


def status_pill(label: str, is_online: bool) -> str:
    """Return HTML for a colored status indicator pill."""
    dot_color = "#16a34a" if is_online else "#dc2626"
    css_class = "status-online" if is_online else "status-offline"
    return (
        f'<span class="status-pill {css_class}">'
        f'<span style="width:6px;height:6px;border-radius:50%;background:{dot_color};display:inline-block"></span> '
        f'{label}</span>'
    )
