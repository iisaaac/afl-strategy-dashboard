"""Fan growth and commercial opportunity page."""

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
    render_section_header,
)
from afl_strategy_dashboard.components.narrative import (
    render_interpretation,
    render_recommendations,
)
from afl_strategy_dashboard.components.tables import (
    COMMERCIAL_OPPORTUNITY_TABLE,
    FAN_GROWTH_TABLE,
    render_notes_detail,
    render_preset_table,
    render_ranked_table,
)
from afl_strategy_dashboard.data.dashboard_state import (
    DashboardState,
    top_fixture_label,
)
from afl_strategy_dashboard.visualisation.charts import (
    average_crowd_by_venue_chart,
    commercial_opportunity_leaderboard_chart,
    fan_growth_opportunity_leaderboard_chart,
    opportunity_category_count_chart,
    venue_capacity_utilisation_chart,
)


def render(state: DashboardState) -> None:
    """Render fan-growth and commercial opportunity analysis."""
    render_page_header(
        "Fan Growth & Commercial",
        "Fixture, venue, timing, rivalry and optional attendance-context signals "
        "translated into public-data opportunity leaderboards.",
        eyebrow="Growth and commercial lens",
    )
    render_dashboard_context(state)
    opportunities = state.opportunities
    if opportunities.empty:
        render_empty_state("No opportunity rows", empty_state_text("chart"))
        return

    top_commercial_fixture = top_fixture_label(
        opportunities, "commercial_opportunity_score"
    )
    top_fan_growth_fixture = top_fixture_label(
        opportunities, "fan_growth_opportunity_score"
    )
    render_executive_takeaway(
        f"{top_commercial_fixture} leads the commercial opportunity signals, while "
        f"{top_fan_growth_fixture} leads the fan-growth review priorities."
    )

    utilisation = opportunities["estimated_capacity_utilisation"].dropna()
    regional_fixture_count = int(
        opportunities["regional_or_special_event_flag"].fillna(False).sum()
    )
    attendance_enabled = state.controls.include_attendance
    if not attendance_enabled:
        utilisation_value = "Not enabled"
        utilisation_subtitle = "Optional public attendance context"
    elif utilisation.empty:
        utilisation_value = "Unavailable"
        utilisation_subtitle = "No matched attendance rows"
    else:
        utilisation_value = f"{utilisation.mean():.0%}"
        utilisation_subtitle = "Matched attendance rows only"

    metrics = [
        {
            "title": "Top commercial fixture",
            "value": top_commercial_fixture,
            "subtitle": "Venue and market-context score",
        },
        {
            "title": "Top fan-growth fixture",
            "value": top_fan_growth_fixture,
            "subtitle": "Audience-growth lens",
        },
        {
            "title": "Average capacity utilisation",
            "value": utilisation_value,
            "subtitle": utilisation_subtitle,
        },
        {
            "title": "Growth-market fixtures",
            "value": f"{int(opportunities['growth_market_flag'].fillna(False).sum())}",
            "subtitle": "Venue market context",
        },
        {
            "title": "Regional / special-event fixtures",
            "value": f"{regional_fixture_count}",
            "subtitle": "Community and event context",
        },
        {
            "title": "Rivalry fixtures",
            "value": f"{int(opportunities['rivalry_flag'].fillna(False).sum())}",
            "subtitle": "Maintained rivalry mapping",
        },
    ]
    render_kpi_grid(metrics)

    render_chart(commercial_opportunity_leaderboard_chart(opportunities), height=440)
    col_one, col_two = st.columns(2)
    with col_one:
        render_chart(
            fan_growth_opportunity_leaderboard_chart(opportunities), height=360
        )
    with col_two:
        render_chart(opportunity_category_count_chart(opportunities), height=360)

    attendance_rows = opportunities.dropna(subset=["estimated_capacity_utilisation"])
    if not attendance_rows.empty:
        col_one, col_two = st.columns(2)
        with col_one:
            render_chart(venue_capacity_utilisation_chart(attendance_rows), height=360)
        with col_two:
            render_chart(average_crowd_by_venue_chart(attendance_rows), height=360)
    else:
        render_empty_state("Attendance context", empty_state_text("attendance"))

    render_content_divider()
    render_section_header("Opportunity Tables")
    commercial_top = opportunities.sort_values(
        "commercial_opportunity_score",
        ascending=False,
    )
    fan_top = opportunities.sort_values(
        "fan_growth_opportunity_score",
        ascending=False,
    )
    low_utilisation = opportunities[
        opportunities["estimated_capacity_utilisation"].lt(0.65)
        & opportunities["fixture_attractiveness_score"].ge(35)
    ].sort_values("fixture_attractiveness_score", ascending=False)
    regional = opportunities.loc[
        opportunities["regional_or_special_event_flag"].fillna(False)
    ]
    tab_one, tab_two, tab_three, tab_four = st.tabs(
        [
            "Top Commercial",
            "Top Fan Growth",
            "Low Utilisation Upside",
            "Regional / Special Event",
        ]
    )
    with tab_one:
        render_preset_table(
            commercial_top,
            COMMERCIAL_OPPORTUNITY_TABLE,
            top_n=10,
            height=420,
        )
        render_notes_detail(
            commercial_top,
            ["home_team", "away_team", "commercial_opportunity_score"],
            "opportunity_notes",
            title="Detailed Commercial Opportunity Notes",
            top_n=10,
            score_column="commercial_opportunity_score",
        )
    with tab_two:
        render_preset_table(
            fan_top,
            FAN_GROWTH_TABLE,
            top_n=10,
            height=420,
        )
        render_notes_detail(
            fan_top,
            ["home_team", "away_team", "fan_growth_opportunity_score"],
            "opportunity_notes",
            title="Detailed Fan Growth Opportunity Notes",
            top_n=10,
            score_column="fan_growth_opportunity_score",
        )
    with tab_three:
        render_ranked_table(
            low_utilisation,
            [
                "fixture",
                "venue",
                "estimated_capacity_utilisation",
                "fixture_attractiveness_score",
                "short_category",
            ],
            rename_map={
                "venue": "Venue",
                "fixture": "Fixture",
                "estimated_capacity_utilisation": "Capacity Use",
                "fixture_attractiveness_score": "Attractiveness",
                "short_category": "Category",
            },
            top_n=10,
            empty_message=(
                "No low-utilisation, high-attractiveness fixtures are available for "
                "the current selection."
            ),
        )
    with tab_four:
        render_ranked_table(
            regional,
            [
                "fixture",
                "venue",
                "market_type",
                "fan_growth_opportunity_score",
                "commercial_opportunity_score",
                "short_category",
            ],
            rename_map={
                "fixture": "Fixture",
                "venue": "Venue",
                "market_type": "Market",
                "fan_growth_opportunity_score": "Fan Growth Score",
                "commercial_opportunity_score": "Commercial Score",
                "short_category": "Category",
            },
            top_n=10,
            empty_message=(
                "No regional or special-event fixtures are available for the "
                "current selection."
            ),
        )
    with st.expander("Full opportunity data", expanded=False):
        st.dataframe(opportunities, use_container_width=True, hide_index=True)

    leader = commercial_top.iloc[0]
    render_interpretation(
        f"{leader['home_team']} v {leader['away_team']} currently leads the "
        "commercial opportunity view. This reflects public-data fixture, venue and "
        "attendance-context signals, not internal AFL commercial priorities."
    )
    render_recommendations(
        state.fan_growth_recommendations,
        "Fan Growth & Commercial Recommendations",
    )
    render_methodology_callout(
        "Opportunity scores are transparent heuristics using public fixture, venue, "
        "timing, rivalry and optional attendance-context fields. They are "
        "prioritisation prompts for further internal review."
    )
