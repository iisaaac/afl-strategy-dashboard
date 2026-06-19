"""Badge formatting and rendering helpers."""

from __future__ import annotations

from html import escape

import streamlit as st

BADGE_TONES = {
    "neutral",
    "risk",
    "warning",
    "success",
    "info",
    "premium",
}


def badge_html(label: str, tone: str = "neutral") -> str:
    """Return safe HTML for a styled badge."""
    safe_tone = tone if tone in BADGE_TONES else "neutral"
    return f'<span class="afl-badge afl-badge--{safe_tone}">{escape(label)}</span>'


def render_badge(label: str, tone: str = "neutral") -> None:
    """Render a badge in Streamlit."""
    st.markdown(badge_html(label, tone), unsafe_allow_html=True)


def format_risk_badge(value: float) -> str:
    """Format a fixture or travel risk score as a safe badge."""
    if value >= 20:
        return badge_html("High review priority", "risk")
    if value >= 10:
        return badge_html("Monitor", "warning")
    return badge_html("Lower visible risk", "success")


def format_opportunity_badge(value: float) -> str:
    """Format a fan-growth or commercial opportunity score as a safe badge."""
    if value >= 60:
        return badge_html("Premium opportunity", "premium")
    if value >= 35:
        return badge_html("Growth opportunity", "success")
    return badge_html("Standard signal", "neutral")


def badge_row(badges: list[tuple[str, str]]) -> str:
    """Return one line of safe badge HTML."""
    return (
        '<div class="afl-badge-row">'
        + "".join(badge_html(label, tone) for label, tone in badges)
        + "</div>"
    )
