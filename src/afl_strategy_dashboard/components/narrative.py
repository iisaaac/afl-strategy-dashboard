"""Narrative and recommendation components."""

from __future__ import annotations

from html import escape

import streamlit as st

from afl_strategy_dashboard.components.layout import render_section_header


def render_recommendations(
    recommendations: list[str],
    title: str = "Executive Recommendations",
) -> None:
    """Render generated recommendations in an executive panel."""
    render_section_header(title)
    if not recommendations:
        st.info("No recommendations are available for the current selection.")
        return
    items = "".join(f"<li>{escape(item)}</li>" for item in recommendations)
    st.markdown(
        f'<div class="afl-recommendations"><ol>{items}</ol></div>',
        unsafe_allow_html=True,
    )


def render_interpretation(text: str) -> None:
    """Render an interpretation note."""
    st.markdown(
        f'<div class="afl-interpretation">{escape(text)}</div>',
        unsafe_allow_html=True,
    )
