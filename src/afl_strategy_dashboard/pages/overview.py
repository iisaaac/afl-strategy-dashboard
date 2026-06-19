"""Overview dashboard page."""

from __future__ import annotations

import streamlit as st

from afl_strategy_dashboard.components.badges import badge_row
from afl_strategy_dashboard.components.cards import render_kpi_grid
from afl_strategy_dashboard.components.layout import (
    render_dashboard_context,
    render_methodology_callout,
    render_page_header,
    render_section_header,
)
from afl_strategy_dashboard.components.narrative import render_recommendations
from afl_strategy_dashboard.components.tables import (
    OVERVIEW_COMMERCIAL_TABLE,
    OVERVIEW_FAN_GROWTH_TABLE,
    OVERVIEW_FIXTURE_EQUITY_TABLE,
    OVERVIEW_TRAVEL_LOAD_TABLE,
    render_preset_table,
)
from afl_strategy_dashboard.data.dashboard_state import (
    DashboardState,
    average_margin_label,
    top_fixture_label,
    top_team_label,
)


def render(state: DashboardState) -> None:
    """Render recruiter-facing overview."""
    render_page_header(
        "AFL Strategy & Fan Growth Analytics Dashboard",
        "Public-data prototype for analysing fixture equity, travel load, "
        "competitive balance, venue utilisation, fan-growth opportunity and "
        "commercial activation signals.",
        eyebrow="Executive strategy prototype",
    )
    st.markdown(
        badge_row(
            [
                ("Public data only", "info"),
                ("Streamlit + Python", "neutral"),
                ("Fixture strategy", "premium"),
                ("Fan growth", "success"),
                ("Commercial lens", "premium"),
            ]
        ),
        unsafe_allow_html=True,
    )
    render_dashboard_context(state)

    metrics = [
        {
            "title": "Games analysed",
            "value": f"{len(state.games):,.0f}",
            "subtitle": state.controls.season_phase_label,
        },
        {
            "title": "Average margin",
            "value": average_margin_label(state.competitive_summary),
            "subtitle": "Completed games in selection",
        },
        {
            "title": "Highest fixture-equity risk club",
            "value": top_team_label(
                state.fixture_equity,
                "fixture_equity_risk_score",
            ),
            "subtitle": "Public-data review priority",
        },
        {
            "title": "Highest travel-load club",
            "value": top_team_label(state.travel_load, "travel_load_score"),
            "subtitle": "Travel exposure signal",
        },
        {
            "title": "Highest commercial opportunity fixture",
            "value": top_fixture_label(
                state.opportunities,
                "commercial_opportunity_score",
            ),
            "subtitle": "Venue, timing and market context",
        },
        {
            "title": "Highest fan-growth opportunity fixture",
            "value": top_fixture_label(
                state.opportunities,
                "fan_growth_opportunity_score",
            ),
            "subtitle": "Growth-market and fixture signal",
        },
    ]
    render_kpi_grid(metrics)

    render_recommendations(state.recommendations[:5], "Executive Insight Panel")

    render_section_header(
        "Snapshot Views",
        "Compact leaderboards for quick orientation. Open each specialist page for "
        "full charts, tables and interpretation.",
    )
    col_one, col_two = st.columns(2)
    with col_one:
        render_preset_table(
            state.fixture_equity,
            OVERVIEW_FIXTURE_EQUITY_TABLE,
            "Fixture equity risk top 5",
            top_n=5,
            height=280,
        )
        st.caption("Open Fixture Equity for detailed exposure drivers.")
        render_preset_table(
            state.opportunities.sort_values(
                "commercial_opportunity_score",
                ascending=False,
            ),
            OVERVIEW_COMMERCIAL_TABLE,
            "Commercial opportunity top 5",
            top_n=5,
            height=280,
        )
        st.caption("Open Fan Growth & Commercial for the full opportunity view.")
    with col_two:
        render_preset_table(
            state.travel_load,
            OVERVIEW_TRAVEL_LOAD_TABLE,
            "Travel load top 5",
            top_n=5,
            height=280,
        )
        st.caption("Open Travel Load for detailed travel exposure.")
        render_preset_table(
            state.opportunities.sort_values(
                "fan_growth_opportunity_score",
                ascending=False,
            ),
            OVERVIEW_FAN_GROWTH_TABLE,
            "Fan-growth opportunity top 5",
            top_n=5,
            height=280,
        )
        st.caption("Open Fan Growth & Commercial for attendance-context detail.")

    render_methodology_callout(
        "This is a public-data strategy prototype. Scores are transparent "
        "heuristics intended to identify review priorities, not official AFL "
        "decisions or forecasts."
    )
