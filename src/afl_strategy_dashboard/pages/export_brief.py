"""Executive brief export page."""

from __future__ import annotations

from datetime import datetime

import streamlit as st
import streamlit.components.v1 as components

from afl_strategy_dashboard.components.cards import render_kpi_grid
from afl_strategy_dashboard.components.layout import (
    render_dashboard_context,
    render_methodology_callout,
    render_page_header,
    render_section_header,
)
from afl_strategy_dashboard.components.narrative import render_interpretation
from afl_strategy_dashboard.data.dashboard_state import DashboardState
from afl_strategy_dashboard.reporting.executive_brief import (
    build_executive_brief_context,
    render_executive_brief_html,
    render_executive_brief_markdown,
)


def render(state: DashboardState) -> None:
    """Render the executive brief export workflow."""
    render_page_header(
        "Export Brief",
        "Generate a recruiter-ready AFL strategy brief from the current season, "
        "phase, team and attendance-context filters.",
        eyebrow="Executive reporting",
    )
    render_dashboard_context(state)
    context = build_executive_brief_context(state)
    html = render_executive_brief_html(context)
    markdown = render_executive_brief_markdown(context)

    render_kpi_grid(
        [
            {
                "title": "Season",
                "value": str(context["season"]),
                "subtitle": str(context["season_phase"]),
            },
            {
                "title": "Team filter",
                "value": str(context["team_filter"]),
                "subtitle": "Current sidebar selection",
            },
            {
                "title": "Data mode",
                "value": str(context["data_mode"]),
                "subtitle": "Export reflects active controls",
            },
        ]
    )
    render_interpretation(
        "The generated brief reflects the current sidebar filters and active data "
        "mode. Refresh controls, season phase, team filtering and attendance-context "
        "settings are captured in the export context."
    )

    render_section_header("Download Brief")
    st.caption(
        "Downloads are generated from the current sidebar filters and active "
        "attendance-context settings."
    )
    col_one, col_two = st.columns(2)
    with col_one:
        st.download_button(
            "Download HTML",
            data=html,
            file_name=_download_name(context, "html"),
            mime="text/html",
            use_container_width=True,
        )
    with col_two:
        st.download_button(
            "Download Markdown",
            data=markdown,
            file_name=_download_name(context, "md"),
            mime="text/markdown",
            use_container_width=True,
        )
    st.caption(
        "PDF export is future work. This public deployment supports portable HTML "
        "and Markdown downloads without requiring system-level PDF rendering "
        "dependencies."
    )

    render_methodology_callout(str(context["methodology_caveats"]))

    render_section_header(
        "Preview",
        "Standalone HTML preview using the same embedded styling as the exported file.",
    )
    components.html(html, height=980, scrolling=True)


def _download_name(context: dict, extension: str) -> str:
    season = _slug_part(str(context.get("season", "season")))
    phase = _slug_part(str(context.get("season_phase", "phase")))
    generated_slug = str(context.get("generated_slug", "")).strip()
    timestamp = generated_slug or datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    return f"afl_strategy_brief_{season}_{phase}_{timestamp}.{extension}"


def _slug_part(value: str) -> str:
    cleaned = "".join(
        character.lower() if character.isalnum() else "_" for character in value
    )
    return "_".join(part for part in cleaned.split("_") if part)
