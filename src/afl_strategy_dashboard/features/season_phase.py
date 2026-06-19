"""Season phase filtering helpers."""

from __future__ import annotations

import pandas as pd


def filter_by_season_phase(
    games: pd.DataFrame,
    season_phase: str = "home_and_away",
) -> pd.DataFrame:
    """Filter games by normalised season phase without crashing on old data."""
    if games.empty or "season_phase" not in games.columns:
        return games.copy()

    phase = season_phase.lower().strip()
    if phase in {"full_season", "all"}:
        return games.copy().reset_index(drop=True)
    if phase not in {"home_and_away", "finals", "unknown"}:
        return games.copy().reset_index(drop=True)

    return games.loc[games["season_phase"].eq(phase)].reset_index(drop=True)
