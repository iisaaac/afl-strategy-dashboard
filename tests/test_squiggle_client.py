import pandas as pd

from afl_strategy_dashboard.data.squiggle_client import normalise_games


def test_normalise_games_creates_internal_schema() -> None:
    raw = pd.DataFrame(
        [
            {
                "id": 123,
                "year": 2025,
                "round": 1,
                "roundname": "Round 1",
                "date": "2025-03-14 19:40:00",
                "venue": "M.C.G.",
                "hteam": "Carlton",
                "ateam": "Collingwood",
                "hscore": 82,
                "ascore": 78,
                "complete": 100,
                "is_final": 0,
            }
        ]
    )

    result = normalise_games(raw)

    assert result.loc[0, "game_id"] == 123
    assert result.loc[0, "round_name"] == "Round 1"
    assert result.loc[0, "home_team"] == "Carlton"
    assert result.loc[0, "away_score"] == 78
    assert result.loc[0, "winner"] == "Carlton"
    assert result.loc[0, "margin"] == 4
    assert result.loc[0, "season_phase"] == "home_and_away"
    assert result.loc[0, "source"] == "Squiggle API"
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_normalise_games_creates_stable_game_id_when_missing() -> None:
    raw = pd.DataFrame(
        [
            {
                "year": 2025,
                "round": 2,
                "hteam": "Sydney",
                "ateam": "Carlton",
                "hscore": None,
                "ascore": None,
            }
        ]
    )

    result = normalise_games(raw, year=2025)

    assert result.loc[0, "game_id"] == "2025-2-Sydney-Carlton"
    assert pd.isna(result.loc[0, "margin"])
