"""Travel load feature engineering."""

from __future__ import annotations

import pandas as pd

from afl_strategy_dashboard.features.fixture_equity import (
    AWAY_COLUMNS,
    HOME_COLUMNS,
    _first_existing_column,
)
from afl_strategy_dashboard.utils.geography import (
    TEAM_HOME_LOCATIONS,
    VENUE_LOCATIONS,
    get_location,
    mapping_to_dataframe,
    return_distance_km,
)

VENUE_COLUMNS = ("venue", "venue_name", "ground")


def get_team_home_locations() -> pd.DataFrame:
    """Return starter team home city/state mappings."""
    return mapping_to_dataframe(TEAM_HOME_LOCATIONS, "team")


def get_venue_locations() -> pd.DataFrame:
    """Return starter venue city/state mappings."""
    return mapping_to_dataframe(VENUE_LOCATIONS, "venue")


def flag_interstate_travel_games(games: pd.DataFrame) -> pd.DataFrame:
    """Return team-game rows with an interstate-travel flag."""
    home_col = _first_existing_column(games, HOME_COLUMNS)
    away_col = _first_existing_column(games, AWAY_COLUMNS)
    venue_col = _first_existing_column(games, VENUE_COLUMNS)
    date_col = next(
        (col for col in ("date", "localtime", "timestr") if col in games),
        None,
    )
    game_id_col = next((col for col in ("game_id", "id") if col in games.columns), None)

    records: list[dict[str, object]] = []
    for index, game in games.iterrows():
        venue = game.get(venue_col)
        venue_location = get_location(VENUE_LOCATIONS, venue)
        venue_city = venue_location.city if venue_location else None
        venue_state = venue_location.state if venue_location else None
        home_team = game.get(home_col)
        away_team = game.get(away_col)
        home_location = get_location(TEAM_HOME_LOCATIONS, home_team)
        away_location = get_location(TEAM_HOME_LOCATIONS, away_team)
        home_state = home_location.state if home_location else None
        away_state = away_location.state if away_location else None
        is_neutral_state_game = (
            venue_state is None
            or home_state is None
            or away_state is None
            or (venue_state != home_state and venue_state != away_state)
        )

        for is_home, team_col, opponent_col in (
            (True, home_col, away_col),
            (False, away_col, home_col),
        ):
            team = game.get(team_col)
            team_location = get_location(TEAM_HOME_LOCATIONS, team)
            team_state = team_location.state if team_location else None
            is_interstate = (
                venue_state is not None
                and team_state is not None
                and venue_state != team_state
            )
            travel_km = (
                return_distance_km(team_location, venue_location)
                if is_interstate
                else 0.0
            )
            records.append(
                {
                    "game_id": game.get(game_id_col) if game_id_col else index,
                    "team": team,
                    "opponent": game.get(opponent_col),
                    "date": (
                        pd.to_datetime(game.get(date_col), errors="coerce")
                        if date_col
                        else pd.NaT
                    ),
                    "is_home": is_home,
                    "is_away": not is_home,
                    "venue": venue,
                    "venue_city": venue_city,
                    "venue_state": venue_state,
                    "team_city": team_location.city if team_location else None,
                    "team_state": team_state,
                    "is_interstate_travel": is_interstate,
                    "is_interstate_away": (not is_home) and is_interstate,
                    "is_interstate_home": is_home and is_interstate,
                    "is_neutral_state_game": is_neutral_state_game,
                    "estimated_return_travel_km": round(travel_km, 1),
                }
            )

    result = pd.DataFrame(records)
    if result.empty:
        return result
    result = result.sort_values(["team", "date", "game_id"]).copy()
    result["previous_was_interstate_trip"] = (
        result.groupby("team")["is_interstate_travel"].shift(1).eq(True)
    )
    result["days_since_previous_game"] = (
        result["date"] - result.groupby("team")["date"].shift(1)
    ).dt.days
    result["short_break_after_interstate_trip"] = result[
        "previous_was_interstate_trip"
    ] & result["days_since_previous_game"].lt(7).fillna(False)
    return result


def calculate_basic_travel_counts(games: pd.DataFrame) -> pd.DataFrame:
    """Calculate interstate travel counts by team."""
    team_games = flag_interstate_travel_games(games)
    if team_games.empty:
        return pd.DataFrame(columns=["team", "interstate_travel_games", "total_games"])

    summary = (
        team_games.groupby("team", dropna=False)
        .agg(
            interstate_travel_games=("is_interstate_travel", "sum"),
            total_games=("team", "size"),
        )
        .reset_index()
    )
    summary["interstate_travel_share"] = (
        summary["interstate_travel_games"] / summary["total_games"]
    )
    return summary.sort_values(
        ["interstate_travel_games", "team"], ascending=[False, True]
    ).reset_index(drop=True)


def summarise_travel_load(
    games: pd.DataFrame,
    *,
    long_haul_threshold_km: float = 2000.0,
) -> pd.DataFrame:
    """Summarise travel load by team using public venue and team mappings."""
    team_games = flag_interstate_travel_games(games)
    if team_games.empty:
        return pd.DataFrame(
            columns=[
                "team",
                "interstate_away_games",
                "interstate_home_games",
                "neutral_state_games",
                "estimated_travel_km",
                "average_travel_km_per_game",
                "long_haul_trips",
                "short_break_after_interstate_trip",
                "travel_load_score",
                "travel_load_notes",
            ]
        )

    team_games["is_long_haul_trip"] = (
        team_games["estimated_return_travel_km"] >= long_haul_threshold_km
    )
    summary = (
        team_games.groupby("team", dropna=False)
        .agg(
            games_played=("team", "size"),
            interstate_away_games=("is_interstate_away", "sum"),
            interstate_home_games=("is_interstate_home", "sum"),
            neutral_state_games=("is_neutral_state_game", "sum"),
            estimated_travel_km=("estimated_return_travel_km", "sum"),
            long_haul_trips=("is_long_haul_trip", "sum"),
            short_break_after_interstate_trip=(
                "short_break_after_interstate_trip",
                "sum",
            ),
        )
        .reset_index()
    )
    int_columns = [
        "games_played",
        "interstate_away_games",
        "interstate_home_games",
        "neutral_state_games",
        "long_haul_trips",
        "short_break_after_interstate_trip",
    ]
    summary[int_columns] = summary[int_columns].fillna(0).astype(int)
    summary["estimated_travel_km"] = summary["estimated_travel_km"].round(1)
    summary["average_travel_km_per_game"] = (
        summary["estimated_travel_km"] / summary["games_played"].clip(lower=1)
    ).round(1)
    summary["travel_load_score"] = summary.apply(_travel_load_score, axis=1)
    summary["travel_load_notes"] = summary.apply(_travel_load_notes, axis=1)
    return summary.sort_values(
        ["travel_load_score", "estimated_travel_km", "team"],
        ascending=[False, False, True],
    ).reset_index(drop=True)


def _travel_load_score(row: pd.Series) -> float:
    score = (
        int(row["interstate_away_games"]) * 2.0
        + int(row["interstate_home_games"]) * 1.0
        + int(row["long_haul_trips"]) * 2.0
        + int(row["short_break_after_interstate_trip"]) * 2.5
        + float(row["estimated_travel_km"]) / 2500.0
    )
    return round(score, 2)


def _travel_load_notes(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["interstate_away_games"] >= 2:
        reasons.append("multiple interstate away games")
    elif row["interstate_away_games"] == 1:
        reasons.append("one interstate away game")
    if row["long_haul_trips"] >= 2:
        reasons.append("repeated long-haul travel")
    elif row["long_haul_trips"] == 1:
        reasons.append("one long-haul trip")
    if row["short_break_after_interstate_trip"] >= 1:
        reasons.append("short recovery after interstate travel")
    if row["interstate_home_games"] >= 1:
        reasons.append("home-listed travel outside the club's home state")
    if not reasons:
        return "Lower visible travel load in this public-data heuristic."
    return (
        "Higher travel load appears linked to "
        + ", ".join(reasons)
        + ". Distances are approximate."
    )
