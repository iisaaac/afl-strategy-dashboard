"""Fixture equity feature engineering."""

from __future__ import annotations

import pandas as pd

from afl_strategy_dashboard.utils.geography import (
    TEAM_HOME_LOCATIONS,
    VENUE_LOCATIONS,
    get_location,
)

HOME_COLUMNS = ("home_team", "hteam", "home", "homeTeam", "home_team_name")
AWAY_COLUMNS = ("away_team", "ateam", "away", "awayTeam", "away_team_name")
DATE_COLUMNS = ("date", "localtime", "timestr", "datetime")


def _first_existing_column(df: pd.DataFrame, candidates: tuple[str, ...]) -> str:
    for column in candidates:
        if column in df.columns:
            return column
    raise KeyError(f"Expected one of these columns: {', '.join(candidates)}")


def _team_columns(df: pd.DataFrame) -> tuple[str, str]:
    return _first_existing_column(df, HOME_COLUMNS), _first_existing_column(
        df, AWAY_COLUMNS
    )


def calculate_team_games_played(games: pd.DataFrame) -> pd.DataFrame:
    """Calculate total games played by team."""
    home_col, away_col = _team_columns(games)
    teams = pd.concat([games[home_col], games[away_col]], ignore_index=True)
    return (
        teams.dropna()
        .value_counts()
        .rename_axis("team")
        .reset_index(name="games_played")
        .sort_values(["games_played", "team"], ascending=[False, True])
        .reset_index(drop=True)
    )


def calculate_home_away_counts(games: pd.DataFrame) -> pd.DataFrame:
    """Calculate home and away fixture counts by team."""
    home_col, away_col = _team_columns(games)
    home = games[home_col].dropna().value_counts().rename("home_games")
    away = games[away_col].dropna().value_counts().rename("away_games")
    counts = pd.concat([home, away], axis=1).fillna(0).astype(int)
    counts.index.name = "team"
    counts = counts.reset_index()
    counts["total_games"] = counts["home_games"] + counts["away_games"]
    counts["home_away_diff"] = counts["home_games"] - counts["away_games"]
    return counts.sort_values("team").reset_index(drop=True)


def identify_short_turnarounds(
    games: pd.DataFrame,
    *,
    threshold_days: int = 6,
) -> pd.DataFrame:
    """Identify team-level games played after a short break."""
    if games.empty:
        return pd.DataFrame()

    home_col, away_col = _team_columns(games)
    date_col = _first_existing_column(games, DATE_COLUMNS)
    working = games.copy()
    working["game_date"] = pd.to_datetime(working[date_col], errors="coerce")
    working = working.dropna(subset=["game_date"])

    home = working.assign(
        team=working[home_col],
        opponent=working[away_col],
        is_home=True,
    )
    away = working.assign(
        team=working[away_col],
        opponent=working[home_col],
        is_home=False,
    )
    team_games = pd.concat([home, away], ignore_index=True)
    team_games = team_games.sort_values(["team", "game_date"]).copy()
    team_games["previous_game_date"] = team_games.groupby("team")["game_date"].shift(1)
    team_games["days_between_games"] = (
        team_games["game_date"] - team_games["previous_game_date"]
    ).dt.days
    team_games["short_turnaround"] = team_games["days_between_games"].notna() & (
        team_games["days_between_games"] <= threshold_days
    )
    return team_games.loc[team_games["short_turnaround"]].reset_index(drop=True)


def summarise_fixture_balance(games: pd.DataFrame) -> pd.DataFrame:
    """Summarise starter fixture balance metrics by team."""
    if "home_team" in games.columns and "away_team" in games.columns:
        equity = summarise_fixture_equity(games)
        return equity.rename(
            columns={
                "home_away_differential": "home_away_diff",
                "short_break_games": "short_turnaround_games",
            }
        )

    counts = calculate_home_away_counts(games)
    try:
        short_turnarounds = identify_short_turnarounds(games)
        short_counts = (
            short_turnarounds.groupby("team")
            .size()
            .reset_index(name="short_turnaround_games")
        )
    except KeyError:
        short_counts = pd.DataFrame(columns=["team", "short_turnaround_games"])

    summary = counts.merge(short_counts, on="team", how="left")
    summary["short_turnaround_games"] = (
        summary["short_turnaround_games"].fillna(0).astype(int)
    )
    return summary.sort_values("team").reset_index(drop=True)


def summarise_fixture_equity(games: pd.DataFrame) -> pd.DataFrame:
    """Summarise fixture equity risk metrics by team.

    The risk score is a transparent heuristic. It increases when teams have
    repeated short breaks, a larger home/away imbalance, consecutive away runs
    and consecutive interstate-away exposure.
    """
    team_games = build_team_game_fixture_view(games)
    if team_games.empty:
        return pd.DataFrame(
            columns=[
                "team",
                "games_played",
                "home_games",
                "away_games",
                "neutral_games",
                "home_away_differential",
                "short_break_games",
                "five_day_breaks",
                "six_day_breaks",
                "average_days_between_games",
                "min_days_between_games",
                "max_days_between_games",
                "consecutive_away_games",
                "consecutive_interstate_away_games",
                "fixture_equity_risk_score",
                "fixture_equity_notes",
            ]
        )

    summary = (
        team_games.groupby("team", dropna=False)
        .agg(
            games_played=("team", "size"),
            home_games=("counts_as_home", "sum"),
            away_games=("counts_as_away", "sum"),
            neutral_games=("is_neutral_state_game", "sum"),
            short_break_games=("is_short_break", "sum"),
            five_day_breaks=("is_five_day_break", "sum"),
            six_day_breaks=("is_six_day_break", "sum"),
            average_days_between_games=("days_between_games", "mean"),
            min_days_between_games=("days_between_games", "min"),
            max_days_between_games=("days_between_games", "max"),
            consecutive_away_games=("away_streak", "max"),
            consecutive_interstate_away_games=("interstate_away_streak", "max"),
        )
        .reset_index()
    )
    int_columns = [
        "games_played",
        "home_games",
        "away_games",
        "neutral_games",
        "short_break_games",
        "five_day_breaks",
        "six_day_breaks",
        "consecutive_away_games",
        "consecutive_interstate_away_games",
    ]
    summary[int_columns] = summary[int_columns].fillna(0).astype(int)
    summary["home_away_differential"] = summary["home_games"] - summary["away_games"]
    summary["fixture_equity_risk_score"] = summary.apply(
        _fixture_equity_risk_score, axis=1
    )
    summary["fixture_equity_notes"] = summary.apply(_fixture_equity_notes, axis=1)
    return summary.sort_values(
        ["fixture_equity_risk_score", "team"], ascending=[False, True]
    ).reset_index(drop=True)


def build_team_game_fixture_view(games: pd.DataFrame) -> pd.DataFrame:
    """Expand fixture rows into one row per team per game."""
    if games.empty:
        return pd.DataFrame()

    home_col, away_col = _team_columns(games)
    date_col = _first_existing_column(games, DATE_COLUMNS)
    venue_col = _first_existing_column(games, ("venue", "venue_name", "ground"))
    game_id_col = next((col for col in ("game_id", "id") if col in games.columns), None)

    records: list[dict[str, object]] = []
    for index, game in games.iterrows():
        venue = game.get(venue_col)
        venue_location = get_location(VENUE_LOCATIONS, venue)
        home_team = game.get(home_col)
        away_team = game.get(away_col)
        home_location = get_location(TEAM_HOME_LOCATIONS, home_team)
        away_location = get_location(TEAM_HOME_LOCATIONS, away_team)
        venue_state = venue_location.state if venue_location else None
        home_state = home_location.state if home_location else None
        away_state = away_location.state if away_location else None
        is_neutral = (
            venue_state is None
            or home_state is None
            or away_state is None
            or (venue_state != home_state and venue_state != away_state)
        )
        game_id = game.get(game_id_col) if game_id_col else index
        for is_listed_home, team, opponent, team_state in (
            (True, home_team, away_team, home_state),
            (False, away_team, home_team, away_state),
        ):
            is_interstate = (
                venue_state is not None
                and team_state is not None
                and venue_state != team_state
            )
            records.append(
                {
                    "game_id": game_id,
                    "team": team,
                    "opponent": opponent,
                    "date": pd.to_datetime(game.get(date_col), errors="coerce"),
                    "venue": venue,
                    "venue_state": venue_state,
                    "team_state": team_state,
                    "is_listed_home": is_listed_home,
                    "is_listed_away": not is_listed_home,
                    "is_neutral_state_game": is_neutral,
                    "is_interstate_game": is_interstate,
                    "counts_as_home": is_listed_home and not is_neutral,
                    "counts_as_away": (not is_listed_home) and not is_neutral,
                    "is_interstate_away": (not is_listed_home) and is_interstate,
                }
            )

    team_games = pd.DataFrame(records)
    if team_games.empty:
        return team_games

    team_games = team_games.sort_values(["team", "date", "game_id"]).copy()
    team_games["previous_game_date"] = team_games.groupby("team")["date"].shift(1)
    team_games["days_between_games"] = (
        team_games["date"] - team_games["previous_game_date"]
    ).dt.days
    team_games["is_short_break"] = team_games["days_between_games"].lt(7).fillna(False)
    team_games["is_five_day_break"] = team_games["days_between_games"].eq(5)
    team_games["is_six_day_break"] = team_games["days_between_games"].eq(6)
    team_games["away_streak"] = _streak_by_team(team_games, "counts_as_away")
    team_games["interstate_away_streak"] = _streak_by_team(
        team_games, "is_interstate_away"
    )
    return team_games


def _streak_by_team(team_games: pd.DataFrame, flag_column: str) -> pd.Series:
    streaks = pd.Series(0, index=team_games.index, dtype="int64")
    for _, group in team_games.groupby("team", dropna=False, sort=False):
        current_streak = 0
        values: list[int] = []
        for flag in group[flag_column].fillna(False):
            current_streak = current_streak + 1 if bool(flag) else 0
            values.append(current_streak)
        streaks.loc[group.index] = values
    return streaks


def _fixture_equity_risk_score(row: pd.Series) -> float:
    away_imbalance = max(0, -int(row["home_away_differential"]))
    score = (
        int(row["short_break_games"]) * 2.0
        + int(row["five_day_breaks"]) * 1.5
        + int(row["six_day_breaks"]) * 1.0
        + away_imbalance * 1.5
        + max(0, int(row["consecutive_away_games"]) - 1) * 1.0
        + max(0, int(row["consecutive_interstate_away_games"]) - 1) * 2.0
    )
    return round(score, 2)


def _fixture_equity_notes(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["short_break_games"] >= 2:
        reasons.append("repeated short-break exposure")
    elif row["short_break_games"] == 1:
        reasons.append("some short-break exposure")
    if row["home_away_differential"] <= -2:
        reasons.append("elevated away-game imbalance")
    if row["consecutive_away_games"] >= 3:
        reasons.append("a sustained away-game sequence")
    if row["consecutive_interstate_away_games"] >= 2:
        reasons.append("consecutive interstate away-game exposure")
    if not reasons:
        return "Lower visible fixture equity risk in this public-data heuristic."
    return (
        "Higher fixture load risk due to "
        + ", ".join(reasons)
        + ". This remains a public-data heuristic."
    )
