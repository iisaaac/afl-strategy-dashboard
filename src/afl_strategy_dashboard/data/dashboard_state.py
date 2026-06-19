"""Shared dashboard state and filtering helpers."""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from afl_strategy_dashboard.data.attendance import merge_attendance_with_games
from afl_strategy_dashboard.data.squiggle_client import SquiggleAPIError, SquiggleClient
from afl_strategy_dashboard.features.competitive_balance import (
    calculate_match_margins,
    season_competitive_balance_summary,
)
from afl_strategy_dashboard.features.fan_growth import (
    rank_high_interest_fixtures,
    score_fan_growth_opportunities,
)
from afl_strategy_dashboard.features.fixture_equity import summarise_fixture_equity
from afl_strategy_dashboard.features.season_phase import filter_by_season_phase
from afl_strategy_dashboard.features.travel_load import (
    flag_interstate_travel_games,
    summarise_travel_load,
)
from afl_strategy_dashboard.insights.recommendations import (
    generate_fan_growth_recommendations,
    generate_strategy_recommendations,
)

SEASON_PHASE_OPTIONS = {
    "Home-and-away season": "home_and_away",
    "Finals only": "finals",
    "Full season": "full_season",
}


@dataclass(frozen=True)
class DashboardControls:
    """User-selected dashboard controls."""

    year: int
    refresh: bool
    completed_only: bool
    season_phase_label: str
    selected_team: str
    use_sample: bool
    include_attendance: bool
    crowd_only: bool

    @property
    def season_phase(self) -> str:
        return SEASON_PHASE_OPTIONS.get(
            self.season_phase_label,
            "home_and_away",
        )


@dataclass(frozen=True)
class DashboardState:
    """Calculated data needed by every dashboard page."""

    controls: DashboardControls
    data_note: str
    attendance_note: str
    raw_games: pd.DataFrame
    ladder: pd.DataFrame
    games: pd.DataFrame
    attendance: pd.DataFrame
    fixture_equity: pd.DataFrame
    travel_load: pd.DataFrame
    team_travel_games: pd.DataFrame
    games_with_margins: pd.DataFrame
    competitive_summary: pd.DataFrame
    ranked_fixtures: pd.DataFrame
    opportunities: pd.DataFrame
    recommendations: list[str]
    fan_growth_recommendations: list[str]


def load_public_or_sample_data(
    year: int,
    refresh: bool,
    use_sample: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Load live public data or synthetic sample data with the existing fallback."""
    if use_sample:
        games, ladder = sample_data()
        return games, ladder, "Using synthetic sample data for offline demonstration."

    client = SquiggleClient()
    try:
        games = client.fetch_games_normalised(year, refresh=refresh)
        try:
            ladder = client.fetch_ladder(year, refresh=refresh)
        except SquiggleAPIError:
            ladder = pd.DataFrame()
        return (
            games,
            ladder,
            f"Using public Squiggle API data for {year}, with local cache enabled.",
        )
    except SquiggleAPIError as exc:
        games, ladder = sample_data()
        return (
            games,
            ladder,
            "Live Squiggle data could not be loaded. "
            f"Showing synthetic sample data instead. Error: {exc}",
        )


def build_dashboard_state(
    *,
    controls: DashboardControls,
    raw_games: pd.DataFrame,
    ladder: pd.DataFrame,
    data_note: str,
    attendance: pd.DataFrame | None = None,
    attendance_note: str = "",
) -> DashboardState:
    """Apply global filters once and build all page-level analytical outputs."""
    attendance = attendance if attendance is not None else pd.DataFrame()
    games = filter_by_season_phase(raw_games, controls.season_phase)
    if controls.completed_only:
        games = filter_completed_games(games)
    games = filter_games_by_team(games, controls.selected_team)

    if controls.include_attendance and not attendance.empty:
        games = merge_attendance_with_games(games, attendance)
    if controls.crowd_only:
        games = games.loc[games.get("crowd", pd.Series(index=games.index)).notna()]
        games = games.reset_index(drop=True)

    fixture_equity = filter_team_table(
        summarise_fixture_equity(games),
        controls.selected_team,
    )
    travel_load = filter_team_table(
        summarise_travel_load(games),
        controls.selected_team,
    )
    team_travel_games = flag_interstate_travel_games(games)
    games_with_margins = calculate_match_margins(games)
    competitive_summary = season_competitive_balance_summary(games)
    ranked_fixtures = rank_high_interest_fixtures(games, ladder=ladder, top_n=10)
    opportunities = score_fan_growth_opportunities(games, ladder=ladder)
    recommendations = generate_strategy_recommendations(
        fixture_equity=fixture_equity,
        travel_load=travel_load,
        competitive_summary=competitive_summary,
        fixture_attractiveness=ranked_fixtures,
    )
    fan_growth_recommendations = generate_fan_growth_recommendations(opportunities)

    return DashboardState(
        controls=controls,
        data_note=data_note,
        attendance_note=attendance_note,
        raw_games=raw_games,
        ladder=ladder,
        games=games,
        attendance=attendance,
        fixture_equity=fixture_equity,
        travel_load=travel_load,
        team_travel_games=team_travel_games,
        games_with_margins=games_with_margins,
        competitive_summary=competitive_summary,
        ranked_fixtures=ranked_fixtures,
        opportunities=opportunities,
        recommendations=recommendations,
        fan_growth_recommendations=fan_growth_recommendations,
    )


def available_teams(games: pd.DataFrame) -> list[str]:
    """Return sorted team names from normalised or Squiggle-shaped game data."""
    home_col = "home_team" if "home_team" in games.columns else "hteam"
    away_col = "away_team" if "away_team" in games.columns else "ateam"
    if home_col not in games.columns or away_col not in games.columns:
        return []
    teams = pd.concat([games[home_col], games[away_col]], ignore_index=True)
    return sorted(teams.dropna().astype(str).unique())


def filter_completed_games(games: pd.DataFrame) -> pd.DataFrame:
    """Filter to completed fixtures while retaining empty selections gracefully."""
    if games.empty:
        return games
    result = games.copy()
    completed = pd.Series(True, index=result.index)
    if "complete" in result.columns:
        completed = pd.to_numeric(result["complete"], errors="coerce").ge(100)
    score_columns = [
        col for col in ("home_score", "away_score", "hscore", "ascore") if col in result
    ]
    if score_columns:
        completed = completed & result[score_columns].notna().all(axis=1)
    return result.loc[completed].reset_index(drop=True)


def filter_games_by_team(games: pd.DataFrame, selected_team: str) -> pd.DataFrame:
    """Filter games to one club when selected."""
    if selected_team == "All teams" or games.empty:
        return games
    home_col = "home_team" if "home_team" in games.columns else "hteam"
    away_col = "away_team" if "away_team" in games.columns else "ateam"
    if home_col not in games.columns or away_col not in games.columns:
        return games
    mask = games[home_col].eq(selected_team) | games[away_col].eq(selected_team)
    return games.loc[mask].reset_index(drop=True)


def filter_team_table(table: pd.DataFrame, selected_team: str) -> pd.DataFrame:
    """Filter a team-level table to one club when selected."""
    if selected_team == "All teams" or table.empty or "team" not in table.columns:
        return table
    return table.loc[table["team"].eq(selected_team)].reset_index(drop=True)


def top_team_label(table: pd.DataFrame, score_column: str) -> str:
    """Return the highest scoring team label for KPI cards."""
    if table.empty or score_column not in table.columns:
        return "n/a"
    row = table.sort_values(score_column, ascending=False).iloc[0]
    return str(row["team"])


def top_fixture_label(opportunities: pd.DataFrame, score_column: str) -> str:
    """Return the highest scoring fixture label for KPI cards."""
    if opportunities.empty or score_column not in opportunities.columns:
        return "n/a"
    row = opportunities.sort_values(score_column, ascending=False).iloc[0]
    return f"{row['home_team']} v {row['away_team']}"


def average_margin_label(competitive_summary: pd.DataFrame) -> str:
    """Return a display-ready average margin label."""
    if competitive_summary.empty:
        return "n/a"
    value = competitive_summary.iloc[0].get("average_margin")
    if pd.isna(value):
        return "n/a"
    return f"{float(value):.1f}"


def sample_data() -> tuple[pd.DataFrame, pd.DataFrame]:
    """Return labelled synthetic data for offline demonstrations."""
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "year": 2025,
                "round": 1,
                "round_name": "Round 1",
                "date": "2025-03-14",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "home_score": 82,
                "away_score": 78,
                "winner": "Carlton",
                "complete": 100,
                "is_final": False,
                "season_phase": "home_and_away",
                "margin": 4,
                "venue": "M.C.G.",
                "predicted_home_win_probability": pd.NA,
                "predicted_away_win_probability": pd.NA,
                "source": "Synthetic sample",
            },
            {
                "game_id": 2,
                "year": 2025,
                "round": 1,
                "round_name": "Round 1",
                "date": "2025-03-15",
                "home_team": "West Coast",
                "away_team": "Fremantle",
                "home_score": 70,
                "away_score": 95,
                "winner": "Fremantle",
                "complete": 100,
                "is_final": False,
                "season_phase": "home_and_away",
                "margin": 25,
                "venue": "Optus Stadium",
                "predicted_home_win_probability": pd.NA,
                "predicted_away_win_probability": pd.NA,
                "source": "Synthetic sample",
            },
            {
                "game_id": 3,
                "year": 2025,
                "round": 1,
                "round_name": "Round 1",
                "date": "2025-03-16",
                "home_team": "Brisbane",
                "away_team": "Sydney",
                "home_score": 101,
                "away_score": 65,
                "winner": "Brisbane",
                "complete": 100,
                "is_final": False,
                "season_phase": "home_and_away",
                "margin": 36,
                "venue": "Gabba",
                "predicted_home_win_probability": pd.NA,
                "predicted_away_win_probability": pd.NA,
                "source": "Synthetic sample",
            },
            {
                "game_id": 4,
                "year": 2025,
                "round": 2,
                "round_name": "Round 2",
                "date": "2025-03-20",
                "home_team": "Port Adelaide",
                "away_team": "Adelaide",
                "home_score": 90,
                "away_score": 88,
                "winner": "Port Adelaide",
                "complete": 100,
                "is_final": False,
                "season_phase": "home_and_away",
                "margin": 2,
                "venue": "Adelaide Oval",
                "predicted_home_win_probability": pd.NA,
                "predicted_away_win_probability": pd.NA,
                "source": "Synthetic sample",
            },
            {
                "game_id": 5,
                "year": 2025,
                "round": 2,
                "round_name": "Round 2",
                "date": "2025-03-21",
                "home_team": "Sydney",
                "away_team": "Carlton",
                "home_score": 77,
                "away_score": 120,
                "winner": "Carlton",
                "complete": 100,
                "is_final": False,
                "season_phase": "home_and_away",
                "margin": 43,
                "venue": "SCG",
                "predicted_home_win_probability": pd.NA,
                "predicted_away_win_probability": pd.NA,
                "source": "Synthetic sample",
            },
            {
                "game_id": 6,
                "year": 2025,
                "round": 2,
                "round_name": "Round 2",
                "date": "2025-03-22",
                "home_team": "Collingwood",
                "away_team": "Brisbane",
                "home_score": 84,
                "away_score": 80,
                "winner": "Collingwood",
                "complete": 100,
                "is_final": False,
                "season_phase": "home_and_away",
                "margin": 4,
                "venue": "M.C.G.",
                "predicted_home_win_probability": pd.NA,
                "predicted_away_win_probability": pd.NA,
                "source": "Synthetic sample",
            },
        ]
    )
    games["date"] = pd.to_datetime(games["date"])
    ladder = pd.DataFrame(
        [
            {"team": "Collingwood", "rank": 1},
            {"team": "Brisbane", "rank": 2},
            {"team": "Carlton", "rank": 3},
            {"team": "Sydney", "rank": 4},
        ]
    )
    return games, ladder
