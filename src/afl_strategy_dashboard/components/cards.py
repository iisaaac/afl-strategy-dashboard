"""Card components for executive dashboard views."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_metric_card(
    title: str,
    value: str,
    subtitle: str | None = None,
    status: str | None = None,
) -> None:
    """Render a compact KPI card."""
    subtitle_html = (
        f'<div class="afl-card-subtitle">{escape(subtitle)}</div>' if subtitle else ""
    )
    status_html = (
        f'<div class="afl-card-status">{escape(status)}</div>' if status else ""
    )
    st.markdown(
        f"""
        <div class="afl-card afl-metric-card">
            <div class="afl-card-title">{escape(title)}</div>
            <div class="afl-card-value">{escape(value)}</div>
            {subtitle_html}
            {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_insight_card(
    title: str,
    body: str,
    status: str | None = None,
) -> None:
    """Render an executive insight card."""
    status_html = (
        f'<div class="afl-card-status">{escape(status)}</div>' if status else ""
    )
    st.markdown(
        f"""
        <div class="afl-card afl-insight-card">
            <div class="afl-card-title">{escape(title)}</div>
            <div class="afl-card-body">{escape(body)}</div>
            {status_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_kpi_grid(metrics: list[dict[str, str]], columns: int = 3) -> None:
    """Render KPI cards across a responsive Streamlit column grid."""
    if not metrics:
        return
    for start in range(0, len(metrics), columns):
        row = metrics[start : start + columns]
        cols = st.columns(len(row))
        for col, metric in zip(cols, row, strict=False):
            with col:
                render_metric_card(
                    title=metric.get("title", ""),
                    value=metric.get("value", ""),
                    subtitle=metric.get("subtitle"),
                    status=metric.get("status"),
                )
