"""Chart rendering helpers for Streamlit pages."""

from __future__ import annotations

import streamlit as st
from plotly.graph_objects import Figure

DEFAULT_PLOTLY_CONFIG = {
    "displayModeBar": False,
    "responsive": True,
}


def apply_chart_height(fig: Figure, height: int | None = None) -> Figure:
    """Apply a stable chart height when provided."""
    if height is not None:
        fig.update_layout(height=height)
    return fig


def render_chart(
    fig: Figure, *, key: str | None = None, height: int | None = None
) -> None:
    """Render a Plotly chart with screenshot-friendly defaults."""
    st.plotly_chart(
        apply_chart_height(fig, height),
        use_container_width=True,
        config=DEFAULT_PLOTLY_CONFIG,
        key=key,
    )
    st.markdown('<div class="afl-chart-spacer"></div>', unsafe_allow_html=True)
