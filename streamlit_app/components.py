"""Reusable Streamlit UI components."""
import streamlit as st

from styles import COLORS


def page_header(title: str, subtitle: str = ""):
    """Render a styled page header with green bottom border."""
    subtitle_html = f"<p>{subtitle}</p>" if subtitle else ""
    st.markdown(
        f'<div class="page-header"><h1>{title}</h1>{subtitle_html}</div>',
        unsafe_allow_html=True,
    )


def metric_card(label: str, value: str, col=None):
    """Render a styled metric card with left accent border.

    Pass a st.columns cell as ``col`` to render inside a column.
    """
    html = f"""
    <div class="metric-card">
        <div class="metric-label">{label}</div>
        <div class="metric-value">{value}</div>
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)


def confidence_bar(class_name: str, probability: float, is_top: bool = False):
    """Render a horizontal confidence bar with label and percentage."""
    pct = probability * 100
    weight = "700" if is_top else "400"
    bg = f"linear-gradient(90deg, {COLORS['primary_light']}, {COLORS['primary']})" if is_top else COLORS["accent"]
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
    """Return an HTML string for a colored severity badge."""
    css_class = {
        "High": "severity-high",
        "Moderate": "severity-moderate",
        "Low": "severity-low",
        "None": "severity-none",
    }.get(severity, "severity-low")
    return f'<span class="severity-badge {css_class}">Severity: {severity}</span>'


def disease_card(name: str, details: dict):
    """Render a full disease information card with symptoms, treatment, and prevention."""
    badge = severity_badge(details["severity"])
    symptoms_html = "".join(f"<li>{s}</li>" for s in details["symptoms"])
    prevention_items = details.get("prevention", [])
    prevention_html = ""
    if prevention_items:
        items = "".join(f"<li>{p}</li>" for p in prevention_items)
        prevention_html = f"<p><strong>Prevention</strong></p><ul>{items}</ul>"

    st.markdown(f"""
    <div class="disease-card">
        <h3>{name}</h3>
        {badge}
        <p style="margin-top:0.8rem"><strong>Symptoms</strong></p>
        <ul>{symptoms_html}</ul>
        <p><strong>Treatment</strong></p>
        <p>{details["treatment"]}</p>
        {prevention_html}
    </div>
    """, unsafe_allow_html=True)


def step_card(icon: str, title: str, description: str, col=None):
    """Render an instructional step card (used in the upload placeholder)."""
    html = f"""
    <div class="step-card">
        <div class="step-icon">{icon}</div>
        <h4>{title}</h4>
        <p>{description}</p>
    </div>
    """
    target = col if col is not None else st
    target.markdown(html, unsafe_allow_html=True)
