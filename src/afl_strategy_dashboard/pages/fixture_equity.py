"""Fixture equity page."""

from __future__ import annotations

import streamlit as st

from afl_strategy_dashboard.components.cards import render_kpi_grid
from afl_strategy_dashboard.components.charts import render_chart
from afl_strategy_dashboard.components.layout import (
    empty_state_text,
    render_content_divider,
    render_dashboard_context,
    render_empty_state,
    render_executive_takeaway,
    render_methodology_callout,
    render_page_header,
)
from afl_strategy_dashboard.components.narrative import render_interpretation
from afl_strategy_dashboard.components.tables import (
    FIXTURE_EQUITY_TABLE,
    render_notes_detail,
    render_preset_table,
)
from afl_strategy_dashboard.data.dashboard_state import DashboardState, top_team_label
from afl_strategy_dashboard.visualisation.charts import (
    home_away_differential_chart,
    short_break_games_chart,
)


def render(state: DashboardState) -> None:
    """Render fixture equity analysis."""
    render_page_header(
        "Fixture Equity",
        "Team-level view of home/away balance, short breaks and away-game exposure "
        "using transparent public-data heuristics.",
        eyebrow="Fixture strategy",
    )
    render_dashboard_context(state)
    fixture_equity = state.fixture_equity
    if fixture_equity.empty:
        render_empty_state("No fixture equity rows", empty_state_text("team"))
        return

    leader = fixture_equity.iloc[0]
    render_executive_takeaway(
        f"{leader['team']} has the highest visible fixture-equity review score, "
        "with the ranking driven by public-data scheduling exposure rather than a "
        "standalone fairness conclusion."
    )

    metrics = [
        {
            "title": "Highest risk club",
            "value": top_team_label(fixture_equity, "fixture_equity_risk_score"),
            "subtitle": "Public-data review priority",
        },
        {
            "title": "Average short-break games",
            "value": f"{fixture_equity['short_break_games'].mean():.1f}",
            "subtitle": "Across filtered clubs",
        },
        {
            "title": "Largest home-away differential",
            "value": f"{fixture_equity['home_away_differential'].abs().max():.0f}",
            "subtitle": "Absolute game difference",
        },
    ]
    render_kpi_grid(metrics)

    col_one, col_two = st.columns(2)
    with col_one:
        render_chart(home_away_differential_chart(fixture_equity), height=360)
    with col_two:
        render_chart(short_break_games_chart(fixture_equity), height=360)

    render_content_divider()
    render_preset_table(
        fixture_equity,
        FIXTURE_EQUITY_TABLE,
        "Ranked Fixture Equity Table",
        top_n=len(fixture_equity),
        height=500,
    )
    render_notes_detail(
        fixture_equity,
        ["team", "fixture_equity_risk_score"],
        "fixture_equity_notes",
        title="Detailed Fixture Equity Notes",
        top_n=len(fixture_equity),
        score_column="fixture_equity_risk_score",
    )
    with st.expander("Full fixture equity data", expanded=False):
        st.dataframe(fixture_equity, use_container_width=True, hide_index=True)
    render_interpretation(
        f"{leader['team']} has the highest visible fixture equity risk score in "
        "the selected data. The score is a review-priority signal and should be "
        "read alongside stadium, broadcast, commercial and operational constraints."
    )
    if state.controls.season_phase == "finals":
        render_interpretation(
            "Finals analysis is available for context, but regular-season fixture "
            "equity conclusions should generally use the home-and-away phase."
        )
    render_methodology_callout(
        "Fixture equity combines short breaks, five-day and six-day breaks, "
        "home/away imbalance, consecutive away runs and consecutive interstate-away "
        "exposure. It is not an official fairness model."
    )
