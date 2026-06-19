"""Plotly chart helpers for the dashboard."""

from __future__ import annotations

import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

from afl_strategy_dashboard.styling.plotly_template import apply_dashboard_template

BLUE = "#163A5F"
GOLD = "#D6A419"
TEAL = "#216869"
GREY = "#59656F"
MUTED_RED = "#9B4D4D"
STANDARD_CHART_HEIGHT = 440
COMPACT_CHART_HEIGHT = 360
FULL_WIDTH_CHART_HEIGHT = 500
STANDARD_MARGIN = {"l": 80, "r": 30, "t": 50, "b": 60}
HORIZONTAL_MARGIN = {"l": 132, "r": 30, "t": 50, "b": 60}
LONG_LABEL_MARGIN = {"l": 190, "r": 30, "t": 50, "b": 60}


def home_away_balance_chart(fixture_balance: pd.DataFrame) -> go.Figure:
    """Create a grouped home/away balance bar chart."""
    chart_data = fixture_balance.melt(
        id_vars="team",
        value_vars=["home_games", "away_games"],
        var_name="fixture_type",
        value_name="games",
    )
    fig = px.bar(
        chart_data,
        x="team",
        y="games",
        color="fixture_type",
        barmode="group",
        labels={"team": "Team", "games": "Games", "fixture_type": "Fixture type"},
        color_discrete_map={"home_games": BLUE, "away_games": GOLD},
    )
    fig.update_layout(title="Home vs Away Balance", xaxis_tickangle=-45)
    return _finalise_chart(fig, margin=STANDARD_MARGIN)


def interstate_travel_count_chart(travel_counts: pd.DataFrame) -> go.Figure:
    """Create an interstate travel count bar chart."""
    fig = px.bar(
        travel_counts.sort_values("interstate_travel_games", ascending=True),
        x="interstate_travel_games",
        y="team",
        orientation="h",
        labels={
            "team": "Team",
            "interstate_travel_games": "Interstate travel games",
        },
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(title="Interstate Travel Count By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def margin_distribution_chart(games_with_margins: pd.DataFrame) -> go.Figure:
    """Create a margin distribution histogram."""
    fig = px.histogram(
        games_with_margins.dropna(subset=["margin_abs"]),
        x="margin_abs",
        nbins=20,
        labels={"margin_abs": "Absolute margin"},
        color_discrete_sequence=[GREY],
    )
    fig.update_layout(title="Match Margin Distribution", yaxis_title="Games")
    return _finalise_chart(
        fig,
        height=FULL_WIDTH_CHART_HEIGHT,
        margin={"l": 70, "r": 30, "t": 50, "b": 70},
    )


def fixture_attractiveness_leaderboard_chart(ranked: pd.DataFrame) -> go.Figure:
    """Create a fan-growth fixture attractiveness leaderboard chart."""
    chart_data = ranked.copy()
    home_col = (
        "home_team_normalised"
        if "home_team_normalised" in chart_data.columns
        else "home_team"
    )
    away_col = (
        "away_team_normalised"
        if "away_team_normalised" in chart_data.columns
        else "away_team"
    )
    chart_data["fixture"] = (
        chart_data[home_col].astype(str) + " v " + chart_data[away_col].astype(str)
    )
    fig = px.bar(
        chart_data.sort_values("fixture_attractiveness_score", ascending=True),
        x="fixture_attractiveness_score",
        y="fixture",
        orientation="h",
        labels={
            "fixture_attractiveness_score": "Attractiveness score",
            "fixture": "Fixture",
        },
        color_discrete_sequence=[GREY],
    )
    fig.update_layout(title="Fixture Attractiveness Leaderboard")
    return _finalise_chart(fig, margin=LONG_LABEL_MARGIN)


def fan_growth_opportunity_leaderboard_chart(opportunities: pd.DataFrame) -> go.Figure:
    """Create a fan-growth opportunity leaderboard."""
    chart_data = _fixture_labels(opportunities).head(12)
    fig = px.bar(
        chart_data.sort_values("fan_growth_opportunity_score", ascending=True),
        x="fan_growth_opportunity_score",
        y="fixture",
        orientation="h",
        labels={
            "fan_growth_opportunity_score": "Fan-growth opportunity score",
            "fixture": "Fixture",
        },
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(title="Fan Growth Opportunity Leaderboard")
    return _finalise_chart(fig, margin=LONG_LABEL_MARGIN)


def commercial_opportunity_leaderboard_chart(opportunities: pd.DataFrame) -> go.Figure:
    """Create a commercial opportunity leaderboard."""
    chart_data = _fixture_labels(opportunities).head(12)
    fig = px.bar(
        chart_data.sort_values("commercial_opportunity_score", ascending=True),
        x="commercial_opportunity_score",
        y="fixture",
        orientation="h",
        labels={
            "commercial_opportunity_score": "Commercial opportunity score",
            "fixture": "Fixture",
        },
        color_discrete_sequence=[BLUE],
    )
    fig.update_layout(title="Commercial Opportunity Leaderboard")
    return _finalise_chart(fig, margin=LONG_LABEL_MARGIN)


def venue_capacity_utilisation_chart(opportunities: pd.DataFrame) -> go.Figure:
    """Create a venue capacity utilisation chart where attendance exists."""
    chart_data = _fixture_labels(
        opportunities.dropna(subset=["estimated_capacity_utilisation"])
    ).copy()
    fig = px.bar(
        chart_data.sort_values("estimated_capacity_utilisation", ascending=True),
        x="estimated_capacity_utilisation",
        y="fixture",
        orientation="h",
        labels={
            "estimated_capacity_utilisation": "Estimated capacity utilisation",
            "fixture": "Fixture",
        },
        color_discrete_sequence=[GREY],
    )
    fig.update_xaxes(tickformat=".0%")
    fig.update_layout(title="Estimated Venue Capacity Utilisation")
    return _finalise_chart(fig, margin=LONG_LABEL_MARGIN)


def average_crowd_by_venue_chart(opportunities: pd.DataFrame) -> go.Figure:
    """Create an average crowd by venue chart where attendance exists."""
    chart_data = (
        opportunities.dropna(subset=["crowd"])
        .groupby("venue", as_index=False)
        .agg(average_crowd=("crowd", "mean"))
    )
    fig = px.bar(
        chart_data.sort_values("average_crowd", ascending=True),
        x="average_crowd",
        y="venue",
        orientation="h",
        labels={"average_crowd": "Average crowd", "venue": "Venue"},
        color_discrete_sequence=[GOLD],
    )
    fig.update_layout(title="Average Crowd By Venue")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def opportunity_category_count_chart(opportunities: pd.DataFrame) -> go.Figure:
    """Create an opportunity category count chart."""
    chart_data = (
        opportunities["opportunity_category"]
        .value_counts()
        .rename_axis("opportunity_category")
        .reset_index(name="fixtures")
    )
    fig = px.bar(
        chart_data.sort_values("fixtures", ascending=True),
        x="fixtures",
        y="opportunity_category",
        orientation="h",
        labels={"fixtures": "Fixtures", "opportunity_category": "Category"},
        color_discrete_sequence=[GREY],
    )
    fig.update_layout(title="Opportunity Category Count")
    return _finalise_chart(fig, margin=LONG_LABEL_MARGIN)


def fixture_equity_risk_chart(fixture_equity: pd.DataFrame) -> go.Figure:
    """Create a fixture equity risk score chart."""
    fig = px.bar(
        fixture_equity.sort_values("fixture_equity_risk_score", ascending=True),
        x="fixture_equity_risk_score",
        y="team",
        orientation="h",
        labels={
            "fixture_equity_risk_score": "Fixture equity risk score",
            "team": "Team",
        },
        color_discrete_sequence=[BLUE],
    )
    fig.update_layout(title="Fixture Equity Risk By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def home_away_differential_chart(fixture_equity: pd.DataFrame) -> go.Figure:
    """Create a home-away differential chart."""
    column = (
        "home_away_differential"
        if "home_away_differential" in fixture_equity.columns
        else "home_away_diff"
    )
    chart_data = fixture_equity.sort_values(column, ascending=True)
    fig = px.bar(
        chart_data,
        x=column,
        y="team",
        orientation="h",
        labels={column: "Home games minus away games", "team": "Team"},
        color_discrete_sequence=[GREY],
    )
    fig.add_vline(x=0, line_width=1, line_color="#9AA5B1")
    fig.update_layout(title="Home-Away Differential By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def short_break_games_chart(fixture_equity: pd.DataFrame) -> go.Figure:
    """Create a short-break games chart."""
    fig = px.bar(
        fixture_equity.sort_values("short_break_games", ascending=True),
        x="short_break_games",
        y="team",
        orientation="h",
        labels={"short_break_games": "Short-break games", "team": "Team"},
        color_discrete_sequence=[MUTED_RED],
    )
    fig.update_layout(title="Short-Break Games By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def interstate_away_games_chart(travel_load: pd.DataFrame) -> go.Figure:
    """Create an interstate away games chart."""
    fig = px.bar(
        travel_load.sort_values("interstate_away_games", ascending=True),
        x="interstate_away_games",
        y="team",
        orientation="h",
        labels={"interstate_away_games": "Interstate away games", "team": "Team"},
        color_discrete_sequence=[TEAL],
    )
    fig.update_layout(title="Interstate Away Games By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def estimated_travel_km_chart(travel_load: pd.DataFrame) -> go.Figure:
    """Create an estimated travel kilometres chart."""
    fig = px.bar(
        travel_load.sort_values("estimated_travel_km", ascending=True),
        x="estimated_travel_km",
        y="team",
        orientation="h",
        labels={"estimated_travel_km": "Estimated return travel km", "team": "Team"},
        color_discrete_sequence=[GREY],
    )
    fig.update_layout(title="Estimated Travel Kilometres By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def travel_load_score_chart(travel_load: pd.DataFrame) -> go.Figure:
    """Create a travel load score chart."""
    fig = px.bar(
        travel_load.sort_values("travel_load_score", ascending=True),
        x="travel_load_score",
        y="team",
        orientation="h",
        labels={"travel_load_score": "Travel load score", "team": "Team"},
        color_discrete_sequence=[BLUE],
    )
    fig.update_layout(title="Travel Load Score By Team")
    return _finalise_chart(fig, margin=HORIZONTAL_MARGIN)


def _fixture_labels(opportunities: pd.DataFrame) -> pd.DataFrame:
    chart_data = opportunities.copy()
    chart_data["fixture"] = (
        chart_data["home_team"].astype(str)
        + " v "
        + chart_data["away_team"].astype(str)
    )
    return chart_data


def _finalise_chart(
    fig: go.Figure,
    *,
    height: int = STANDARD_CHART_HEIGHT,
    margin: dict[str, int] | None = None,
) -> go.Figure:
    fig = apply_dashboard_template(fig)
    fig.update_layout(height=height, margin=margin or STANDARD_MARGIN)
    return fig
