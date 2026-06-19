"""Competitive balance page."""

from __future__ import annotations

from afl_strategy_dashboard.components.cards import render_kpi_grid
from afl_strategy_dashboard.components.charts import render_chart
from afl_strategy_dashboard.components.layout import (
    render_content_divider,
    render_dashboard_context,
    render_methodology_callout,
    render_page_header,
    render_section_header,
)
from afl_strategy_dashboard.components.narrative import render_interpretation
from afl_strategy_dashboard.components.tables import (
    COMPETITIVE_BALANCE_RENAME_MAP,
    render_html_table,
)
from afl_strategy_dashboard.data.dashboard_state import (
    DashboardState,
    average_margin_label,
)
from afl_strategy_dashboard.visualisation.charts import (
    margin_distribution_chart,
)


def render(state: DashboardState) -> None:
    """Render competitive balance analysis."""
    render_page_header(
        "Competitive Balance",
        "Score-derived match margin profile for close games, blowouts and broad "
        "engagement-window context.",
        eyebrow="Competition health lens",
    )
    render_dashboard_context(state)
    summary = state.competitive_summary.iloc[0]
    metrics = [
        {
            "title": "Completed games",
            "value": f"{summary['games']:,.0f}",
            "subtitle": "Games with score-derived margins",
        },
        {
            "title": "Average margin",
            "value": average_margin_label(state.competitive_summary),
            "subtitle": "Points",
        },
        {
            "title": "Close-game rate",
            "value": f"{summary['close_game_rate']:.0%}",
            "subtitle": "12 points or fewer",
        },
        {
            "title": "Blowout rate",
            "value": f"{summary['blowout_game_rate']:.0%}",
            "subtitle": "40 points or more",
        },
    ]
    render_kpi_grid(metrics, columns=4)
    render_section_header(
        "Match Margin Distribution",
        "Competitive balance metrics use completed fixtures with available score "
        "fields. Future or incomplete fixtures are excluded when completed-games "
        "filtering is enabled.",
    )
    render_chart(margin_distribution_chart(state.games_with_margins), height=500)

    render_content_divider()
    render_html_table(
        state.competitive_summary,
        columns=[
            "games",
            "average_margin",
            "median_margin",
            "close_games",
            "close_game_rate",
            "blowout_games",
            "blowout_game_rate",
        ],
        rename_map=COMPETITIVE_BALANCE_RENAME_MAP,
        title="Match Margin Summary",
    )
    render_interpretation(
        f"Close-game frequency is currently {summary['close_game_rate']:.0%}, while "
        f"blowout frequency is {summary['blowout_game_rate']:.0%}. These are "
        "public-data indicators for engagement and broadcast review, not definitive "
        "competition health conclusions."
    )
    render_methodology_callout(
        "Competitive balance uses absolute score margins, with default thresholds "
        "of 12 points for close games and 40 points for blowouts."
    )
