"""Layout helpers for the Streamlit dashboard."""

from __future__ import annotations

from html import escape

import streamlit as st


def render_page_header(
    title: str,
    subtitle: str,
    eyebrow: str | None = None,
) -> None:
    """Render a consistent page header."""
    eyebrow_html = (
        f'<div class="afl-eyebrow">{escape(eyebrow)}</div>' if eyebrow else ""
    )
    st.markdown(
        f"""
        <section class="afl-page-header">
            {eyebrow_html}
            <h1>{escape(title)}</h1>
            <p>{escape(subtitle)}</p>
        </section>
        """,
        unsafe_allow_html=True,
    )


def render_section_header(title: str, subtitle: str | None = None) -> None:
    """Render a section heading."""
    subtitle_html = (
        f'<p class="afl-section-subtitle">{escape(subtitle)}</p>' if subtitle else ""
    )
    st.markdown(
        f"""
        <div class="afl-section-header">
            <h2>{escape(title)}</h2>
            {subtitle_html}
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_vertical_spacer(size: str = "md") -> None:
    """Render a small flow spacer between dense dashboard sections."""
    if size not in {"sm", "md", "lg"}:
        size = "md"
    st.markdown(
        f'<div class="afl-spacer afl-spacer--{size}"></div>', unsafe_allow_html=True
    )


def render_content_divider() -> None:
    """Render a subtle divider between major content blocks."""
    st.markdown('<div class="afl-content-divider"></div>', unsafe_allow_html=True)


def render_methodology_callout(text: str) -> None:
    """Render a methodology caveat callout."""
    st.markdown(
        f'<div class="afl-callout"><strong>Methodology caveat.</strong> '
        f"{escape(text)}</div>",
        unsafe_allow_html=True,
    )


def render_data_status_bar(
    data_note: str,
    attendance_note: str,
    phase_label: str,
    selected_team: str,
    season: int | str,
) -> None:
    """Render compact global context."""
    st.markdown(
        build_context_strip_html(
            data_note=data_note,
            attendance_note=attendance_note,
            phase_label=phase_label,
            selected_team=selected_team,
            season=season,
        ),
        unsafe_allow_html=True,
    )


def build_context_strip_html(
    data_note: str,
    attendance_note: str,
    phase_label: str,
    selected_team: str,
    season: int | str,
) -> str:
    """Build escaped HTML for the compact dashboard context strip."""
    items = [
        ("Season", str(season)),
        ("Phase", phase_label),
        ("Team", selected_team),
        ("Source", _compact_data_source(data_note)),
        ("Attendance", _compact_attendance_status(attendance_note)),
    ]
    pills = "".join(
        '<span class="context-pill">'
        f"<span>{escape(label)}</span><strong>{escape(value)}</strong>"
        "</span>"
        for label, value in items
    )
    return f'<div class="context-strip">{pills}</div>'


def render_dashboard_context(state) -> None:
    """Render the active dashboard context immediately below a page header."""
    render_data_status_bar(
        data_note=state.data_note,
        attendance_note=state.attendance_note,
        phase_label=state.controls.season_phase_label,
        selected_team=state.controls.selected_team,
        season=state.controls.year,
    )


def _compact_data_source(data_note: str) -> str:
    note = data_note.lower()
    if "synthetic" in note or "sample" in note:
        return "Sample data"
    if "squiggle" in note:
        return "Squiggle API"
    if "could not be loaded" in note or "error" in note:
        return "Fallback data"
    return "Public data"


def _compact_attendance_status(attendance_note: str) -> str:
    note = attendance_note.lower()
    if not attendance_note or "not enabled" in note:
        return "Off"
    if "could not be loaded" in note or "no attendance csv" in note:
        return "Unavailable"
    if "sample" in note or "synthetic" in note:
        return "Sample"
    return "On"


def empty_state_text(context: str) -> str:
    """Return professional empty-state copy for known dashboard contexts."""
    messages = {
        "attendance": (
            "No attendance data is available for the current selection. The "
            "opportunity model is still using fixture, venue, rivalry and timing "
            "signals."
        ),
        "crowd": (
            "No matched crowd data is available for the current selection, so "
            "utilisation charts are hidden."
        ),
        "finals": (
            "No finals fixtures are available in the selected data. Switch to the "
            "full season or home-and-away view for broader analysis."
        ),
        "team": ("The selected team has no games in the current phase and filter set."),
        "chart": (
            "No chart data is available after the current filters. Adjust the "
            "selection or use sample data for a demonstration."
        ),
        "api": (
            "Live public API data is unavailable. The dashboard can continue using "
            "local cache or synthetic sample data."
        ),
    }
    return messages.get(context, messages["chart"])


def render_empty_state(title: str, body: str) -> None:
    """Render an empty-state panel."""
    st.markdown(
        f"""
        <div class="afl-empty-state">
            <div class="afl-empty-title">{escape(title)}</div>
            <div>{escape(body)}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )
