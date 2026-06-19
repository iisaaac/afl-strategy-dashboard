import pandas as pd

from afl_strategy_dashboard.features.travel_load import (
    calculate_basic_travel_counts,
    flag_interstate_travel_games,
    summarise_travel_load,
)
from afl_strategy_dashboard.utils.geography import (
    TEAM_HOME_LOCATIONS,
    VENUE_LOCATIONS,
    haversine_km,
)


def test_interstate_travel_flagging() -> None:
    games = pd.DataFrame(
        [
            {
                "id": 1,
                "hteam": "Carlton",
                "ateam": "West Coast",
                "venue": "M.C.G.",
            }
        ]
    )

    result = flag_interstate_travel_games(games)
    west_coast = result.loc[result["team"] == "West Coast"].iloc[0]
    carlton = result.loc[result["team"] == "Carlton"].iloc[0]

    assert bool(west_coast["is_interstate_travel"]) is True
    assert bool(carlton["is_interstate_travel"]) is False


def test_basic_travel_counts() -> None:
    games = pd.DataFrame(
        [
            {
                "id": 1,
                "hteam": "Carlton",
                "ateam": "West Coast",
                "venue": "M.C.G.",
            },
            {
                "id": 2,
                "hteam": "West Coast",
                "ateam": "Fremantle",
                "venue": "Optus Stadium",
            },
        ]
    )

    result = calculate_basic_travel_counts(games)
    west_coast = result.loc[result["team"] == "West Coast"].iloc[0]

    assert west_coast["interstate_travel_games"] == 1
    assert west_coast["total_games"] == 2


def test_haversine_distance_calculation() -> None:
    distance = haversine_km(
        TEAM_HOME_LOCATIONS["West Coast"],
        VENUE_LOCATIONS["M.C.G."],
    )

    assert 2700 < distance < 2800


def test_travel_load_summary_metrics() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "date": "2025-03-01",
                "home_team": "Carlton",
                "away_team": "West Coast",
                "venue": "M.C.G.",
            },
            {
                "game_id": 2,
                "date": "2025-03-06",
                "home_team": "West Coast",
                "away_team": "Fremantle",
                "venue": "M.C.G.",
            },
            {
                "game_id": 3,
                "date": "2025-03-12",
                "home_team": "West Coast",
                "away_team": "Carlton",
                "venue": "Optus Stadium",
            },
        ]
    )

    result = summarise_travel_load(games)
    west_coast = result.loc[result["team"] == "West Coast"].iloc[0]

    assert west_coast["interstate_away_games"] == 1
    assert west_coast["interstate_home_games"] == 1
    assert west_coast["estimated_travel_km"] > 10000
    assert west_coast["long_haul_trips"] == 2
    assert west_coast["short_break_after_interstate_trip"] == 2


def test_travel_load_score_increases_with_risk_factors() -> None:
    low_risk_games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "date": "2025-03-01",
                "home_team": "West Coast",
                "away_team": "Fremantle",
                "venue": "Optus Stadium",
            }
        ]
    )
    high_risk_games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "date": "2025-03-01",
                "home_team": "Carlton",
                "away_team": "West Coast",
                "venue": "M.C.G.",
            },
            {
                "game_id": 2,
                "date": "2025-03-06",
                "home_team": "Sydney",
                "away_team": "West Coast",
                "venue": "SCG",
            },
        ]
    )

    low_score = (
        summarise_travel_load(low_risk_games)
        .loc[lambda df: df["team"] == "West Coast", "travel_load_score"]
        .iloc[0]
    )
    high_score = (
        summarise_travel_load(high_risk_games)
        .loc[lambda df: df["team"] == "West Coast", "travel_load_score"]
        .iloc[0]
    )

    assert high_score > low_score
