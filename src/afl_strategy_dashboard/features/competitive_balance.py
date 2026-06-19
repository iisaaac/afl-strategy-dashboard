"""Competitive balance feature engineering."""

from __future__ import annotations

import pandas as pd

from afl_strategy_dashboard.features.fixture_equity import (
    AWAY_COLUMNS,
    HOME_COLUMNS,
    _first_existing_column,
)

HOME_SCORE_COLUMNS = ("home_score", "hscore", "homeScore")
AWAY_SCORE_COLUMNS = ("away_score", "ascore", "awayScore")
WINNER_COLUMNS = ("winner", "winning_team")
TIP_COLUMNS = ("tip", "predicted_winner", "model_winner")


def calculate_match_margins(games: pd.DataFrame) -> pd.DataFrame:
    """Add absolute and signed margin fields to a games DataFrame."""
    home_score_col = _first_existing_column(games, HOME_SCORE_COLUMNS)
    away_score_col = _first_existing_column(games, AWAY_SCORE_COLUMNS)
    home_col = _first_existing_column(games, HOME_COLUMNS)
    away_col = _first_existing_column(games, AWAY_COLUMNS)

    result = games.copy()
    result["home_score_numeric"] = pd.to_numeric(
        result[home_score_col], errors="coerce"
    )
    result["away_score_numeric"] = pd.to_numeric(
        result[away_score_col], errors="coerce"
    )
    result["margin_signed_home"] = (
        result["home_score_numeric"] - result["away_score_numeric"]
    )
    result["margin_abs"] = result["margin_signed_home"].abs()
    result["winning_team"] = pd.NA
    result.loc[result["margin_signed_home"] > 0, "winning_team"] = result[home_col]
    result.loc[result["margin_signed_home"] < 0, "winning_team"] = result[away_col]
    result.loc[result["margin_signed_home"] == 0, "winning_team"] = "Draw"
    return result


def average_margin(games: pd.DataFrame) -> float:
    """Return average absolute match margin."""
    with_margins = _ensure_margins(games)
    return float(with_margins["margin_abs"].dropna().mean())


def count_close_games(games: pd.DataFrame, *, threshold: int = 12) -> int:
    """Count games decided by threshold points or fewer."""
    with_margins = _ensure_margins(games)
    return int((with_margins["margin_abs"] <= threshold).sum())


def count_blowout_games(games: pd.DataFrame, *, threshold: int = 40) -> int:
    """Count games decided by threshold points or more."""
    with_margins = _ensure_margins(games)
    return int((with_margins["margin_abs"] >= threshold).sum())


def add_upset_indicators(games: pd.DataFrame) -> pd.DataFrame:
    """Add upset indicators where prediction fields are present."""
    result = _ensure_margins(games)
    prediction_col = next((col for col in TIP_COLUMNS if col in result.columns), None)
    winner_col = next((col for col in WINNER_COLUMNS if col in result.columns), None)
    if winner_col is None:
        winner_col = "winning_team"

    if prediction_col is None:
        result["predicted_winner"] = pd.NA
        result["is_upset"] = pd.NA
        return result

    result["predicted_winner"] = result[prediction_col]
    result["is_upset"] = (
        result[winner_col].notna()
        & result["predicted_winner"].notna()
        & (result[winner_col] != "Draw")
        & (result[winner_col] != result["predicted_winner"])
    )
    return result


def season_competitive_balance_summary(
    games: pd.DataFrame,
    *,
    close_threshold: int = 12,
    blowout_threshold: int = 40,
) -> pd.DataFrame:
    """Return a one-row season-level competitive balance summary."""
    with_upsets = add_upset_indicators(games)
    completed = with_upsets.dropna(subset=["margin_abs"])
    game_count = len(completed)
    close_games = int((completed["margin_abs"] <= close_threshold).sum())
    blowouts = int((completed["margin_abs"] >= blowout_threshold).sum())
    upset_count = (
        int(completed["is_upset"].eq(True).sum())  # noqa: E712
        if "is_upset" in completed.columns
        else 0
    )

    return pd.DataFrame(
        [
            {
                "games": game_count,
                "average_margin": completed["margin_abs"].mean(),
                "median_margin": completed["margin_abs"].median(),
                "close_games": close_games,
                "close_game_rate": close_games / game_count if game_count else 0,
                "blowout_games": blowouts,
                "blowout_game_rate": blowouts / game_count if game_count else 0,
                "upset_games": upset_count,
            }
        ]
    )


def _ensure_margins(games: pd.DataFrame) -> pd.DataFrame:
    if "margin_abs" in games.columns:
        return games.copy()
    return calculate_match_margins(games)
