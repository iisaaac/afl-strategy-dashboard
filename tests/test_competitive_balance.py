import pandas as pd

from afl_strategy_dashboard.features.competitive_balance import (
    add_upset_indicators,
    calculate_match_margins,
    count_blowout_games,
    count_close_games,
    season_competitive_balance_summary,
)


def test_margin_calculations() -> None:
    games = pd.DataFrame(
        [
            {"hteam": "Carlton", "ateam": "Collingwood", "hscore": 80, "ascore": 75},
            {"hteam": "Essendon", "ateam": "Richmond", "hscore": 60, "ascore": 100},
        ]
    )

    result = calculate_match_margins(games)

    assert result["margin_abs"].tolist() == [5, 40]
    assert result["winning_team"].tolist() == ["Carlton", "Richmond"]


def test_close_game_and_blowout_logic() -> None:
    games = pd.DataFrame(
        [
            {"hteam": "A", "ateam": "B", "hscore": 80, "ascore": 75},
            {"hteam": "C", "ateam": "D", "hscore": 60, "ascore": 100},
            {"hteam": "E", "ateam": "F", "hscore": 90, "ascore": 70},
        ]
    )

    assert count_close_games(games, threshold=12) == 1
    assert count_blowout_games(games, threshold=40) == 1


def test_upset_indicators_when_prediction_exists() -> None:
    games = pd.DataFrame(
        [
            {
                "hteam": "Carlton",
                "ateam": "Collingwood",
                "hscore": 80,
                "ascore": 75,
                "tip": "Collingwood",
            }
        ]
    )

    result = add_upset_indicators(games)

    assert bool(result["is_upset"].iloc[0]) is True


def test_season_competitive_balance_summary() -> None:
    games = pd.DataFrame(
        [
            {"hteam": "A", "ateam": "B", "hscore": 80, "ascore": 75},
            {"hteam": "C", "ateam": "D", "hscore": 60, "ascore": 100},
        ]
    )

    summary = season_competitive_balance_summary(games)

    assert summary.iloc[0]["games"] == 2
    assert summary.iloc[0]["close_games"] == 1
    assert summary.iloc[0]["blowout_games"] == 1
