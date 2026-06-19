import pandas as pd

from afl_strategy_dashboard.features.fixture_equity import (
    calculate_home_away_counts,
    identify_short_turnarounds,
    summarise_fixture_balance,
    summarise_fixture_equity,
)


def test_home_away_calculations() -> None:
    games = pd.DataFrame(
        [
            {"hteam": "Carlton", "ateam": "Collingwood"},
            {"hteam": "Carlton", "ateam": "Essendon"},
            {"hteam": "Essendon", "ateam": "Carlton"},
        ]
    )

    result = calculate_home_away_counts(games)
    carlton = result.loc[result["team"] == "Carlton"].iloc[0]

    assert carlton["home_games"] == 2
    assert carlton["away_games"] == 1
    assert carlton["total_games"] == 3
    assert carlton["home_away_diff"] == 1


def test_short_turnarounds_are_identified() -> None:
    games = pd.DataFrame(
        [
            {
                "date": "2025-03-01",
                "hteam": "Carlton",
                "ateam": "Collingwood",
            },
            {
                "date": "2025-03-06",
                "hteam": "Essendon",
                "ateam": "Carlton",
            },
            {
                "date": "2025-03-20",
                "hteam": "Carlton",
                "ateam": "Richmond",
            },
        ]
    )

    result = identify_short_turnarounds(games, threshold_days=6)

    assert len(result.loc[result["team"] == "Carlton"]) == 1
    days_between_games = result.loc[
        result["team"] == "Carlton", "days_between_games"
    ].iloc[0]
    assert int(days_between_games) == 5


def test_fixture_balance_includes_short_turnaround_count() -> None:
    games = pd.DataFrame(
        [
            {"date": "2025-03-01", "hteam": "Carlton", "ateam": "Collingwood"},
            {"date": "2025-03-06", "hteam": "Essendon", "ateam": "Carlton"},
        ]
    )

    result = summarise_fixture_balance(games)
    carlton = result.loc[result["team"] == "Carlton"].iloc[0]

    assert carlton["short_turnaround_games"] == 1


def test_fixture_equity_summary_metrics() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "date": "2025-03-01",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "M.C.G.",
            },
            {
                "game_id": 2,
                "date": "2025-03-06",
                "home_team": "Sydney",
                "away_team": "Carlton",
                "venue": "SCG",
            },
            {
                "game_id": 3,
                "date": "2025-03-12",
                "home_team": "Brisbane",
                "away_team": "Carlton",
                "venue": "Gabba",
            },
            {
                "game_id": 4,
                "date": "2025-03-21",
                "home_team": "Carlton",
                "away_team": "Essendon",
                "venue": "M.C.G.",
            },
        ]
    )

    result = summarise_fixture_equity(games)
    carlton = result.loc[result["team"] == "Carlton"].iloc[0]

    assert carlton["games_played"] == 4
    assert carlton["home_games"] == 2
    assert carlton["away_games"] == 2
    assert carlton["home_away_differential"] == 0
    assert carlton["short_break_games"] == 2
    assert carlton["five_day_breaks"] == 1
    assert carlton["six_day_breaks"] == 1
    assert carlton["consecutive_away_games"] == 2
    assert carlton["consecutive_interstate_away_games"] == 2


def test_fixture_equity_score_increases_with_risk_factors() -> None:
    low_risk_games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "date": "2025-03-01",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "M.C.G.",
            },
            {
                "game_id": 2,
                "date": "2025-03-09",
                "home_team": "Carlton",
                "away_team": "Essendon",
                "venue": "M.C.G.",
            },
        ]
    )
    high_risk_games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "date": "2025-03-01",
                "home_team": "Collingwood",
                "away_team": "Carlton",
                "venue": "M.C.G.",
            },
            {
                "game_id": 2,
                "date": "2025-03-06",
                "home_team": "Sydney",
                "away_team": "Carlton",
                "venue": "SCG",
            },
            {
                "game_id": 3,
                "date": "2025-03-12",
                "home_team": "Brisbane",
                "away_team": "Carlton",
                "venue": "Gabba",
            },
        ]
    )

    low_score = (
        summarise_fixture_equity(low_risk_games)
        .loc[lambda df: df["team"] == "Carlton", "fixture_equity_risk_score"]
        .iloc[0]
    )
    high_score = (
        summarise_fixture_equity(high_risk_games)
        .loc[lambda df: df["team"] == "Carlton", "fixture_equity_risk_score"]
        .iloc[0]
    )

    assert high_score > low_score
