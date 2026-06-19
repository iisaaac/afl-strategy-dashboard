"""Travel load page."""

from __future__ import annotations

import streamlit as st

from afl_strategy_dashboard.components.cards import render_kpi_grid
from afl_strategy_dashboard.components.charts import render_chart
from afl_strategy_dashboard.components.layout import (
    empty_state_text,
    render_content_divider,
    render_dashboard_context,
    render_empty_state,
    render_methodology_callout,
    render_page_header,
)
from afl_strategy_dashboard.components.narrative import render_interpretation
from afl_strategy_dashboard.components.tables import (
    TEAM_TRAVEL_GAME_RENAME_MAP,
    TRAVEL_LOAD_TABLE,
    render_dataframe_with_caption,
    render_notes_detail,
    render_preset_table,
)
from afl_strategy_dashboard.data.dashboard_state import DashboardState, top_team_label
from afl_strategy_dashboard.visualisation.charts import (
    estimated_travel_km_chart,
    travel_load_score_chart,
)


def render(state: DashboardState) -> None:
    """Render travel load analysis."""
    render_page_header(
        "Travel Load",
        "Public team and venue geography translated into interstate exposure, "
        "estimated return kilometres and short recovery-window signals.",
        eyebrow="Operations and player movement lens",
    )
    render_dashboard_context(state)
    travel_load = state.travel_load
    if travel_load.empty:
        render_empty_state("No travel rows", empty_state_text("team"))
        return

    metrics = [
        {
            "title": "Highest travel-load club",
            "value": top_team_label(travel_load, "travel_load_score"),
            "subtitle": "Composite travel exposure score",
        },
        {
            "title": "Total interstate away games",
            "value": f"{travel_load['interstate_away_games'].sum():.0f}",
            "subtitle": "Filtered selection",
        },
        {
            "title": "Estimated return kilometres",
            "value": f"{travel_load['estimated_travel_km'].sum():,.0f}",
            "subtitle": "Approximate public-data distance",
        },
    ]
    render_kpi_grid(metrics)

    col_one, col_two = st.columns(2)
    with col_one:
        render_chart(estimated_travel_km_chart(travel_load), height=360)
    with col_two:
        render_chart(travel_load_score_chart(travel_load), height=360)

    render_content_divider()
    render_preset_table(
        travel_load,
        TRAVEL_LOAD_TABLE,
        "Ranked Travel Load Table",
        top_n=len(travel_load),
        height=500,
    )
    render_notes_detail(
        travel_load,
        ["team", "travel_load_score"],
        "travel_load_notes",
        title="Detailed Travel Load Notes",
        top_n=len(travel_load),
        score_column="travel_load_score",
    )
    with st.expander("Full travel load data", expanded=False):
        st.dataframe(travel_load, use_container_width=True, hide_index=True)
    leader = travel_load.iloc[0]
    render_interpretation(
        f"{leader['team']} has the highest visible travel-load score in the "
        "selected data. This may warrant further internal review with player "
        "welfare, venue availability and broadcast planning inputs."
    )
    with st.expander("Team-game travel flags", expanded=False):
        render_dataframe_with_caption(
            state.team_travel_games,
            "Expanded team-game view used to calculate interstate travel exposure.",
            columns=[
                "team",
                "opponent",
                "date",
                "venue",
                "venue_state",
                "team_state",
                "is_home",
                "is_interstate_away",
                "estimated_return_travel_km",
                "days_since_previous_game",
                "short_break_after_interstate_trip",
            ],
            rename_map=TEAM_TRAVEL_GAME_RENAME_MAP,
            height=420,
        )
    render_methodology_callout(
        "Travel distance uses approximate return kilometres between mapped team "
        "home locations and venues. It does not model flight routes, recovery "
        "quality, time zones or actual itineraries."
    )
