import pandas as pd

from afl_strategy_dashboard.features.fan_growth import (
    classify_broadcast_window,
    is_rivalry_fixture,
    score_fan_growth_opportunities,
)


def test_rivalry_flag_detection() -> None:
    assert is_rivalry_fixture("Collingwood", "Carlton") is True
    assert is_rivalry_fixture("Gold Coast", "St Kilda") is False


def test_broadcast_window_classification() -> None:
    assert classify_broadcast_window("2025-03-14 19:40") == "Friday night"
    assert classify_broadcast_window("2025-03-15 13:20") == "Saturday day"
    assert classify_broadcast_window(None) == "Other / unknown"


def test_capacity_utilisation_and_category() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "year": 2025,
                "round": 1,
                "date": "2025-03-14 19:40",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "MCG",
                "home_score": 82,
                "away_score": 78,
                "margin": 4,
                "crowd": 82000,
            }
        ]
    )

    result = score_fan_growth_opportunities(games)

    assert round(result.loc[0, "estimated_capacity_utilisation"], 2) == 0.82
    assert bool(result.loc[0, "rivalry_flag"]) is True
    assert result.loc[0, "opportunity_category"] == "Marquee commercial fixture"


def test_commercial_score_increases_for_prime_rivalry_major_fixture() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "year": 2025,
                "date": "2025-03-14 19:40",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "MCG",
                "margin": 4,
                "crowd": 82000,
            },
            {
                "game_id": 2,
                "year": 2025,
                "date": "2025-03-16 13:20",
                "home_team": "Gold Coast",
                "away_team": "St Kilda",
                "venue": "Carrara",
                "margin": 35,
                "crowd": 12000,
            },
        ]
    )

    result = score_fan_growth_opportunities(games)
    commercial = dict(
        zip(
            result["game_id"],
            result["commercial_opportunity_score"],
            strict=False,
        )
    )

    assert commercial[1] > commercial[2]


def test_fan_growth_score_increases_for_growth_market_under_utilised_fixture() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "year": 2025,
                "date": "2025-03-16 13:20",
                "home_team": "Gold Coast",
                "away_team": "Brisbane Lions",
                "venue": "Carrara",
                "margin": 6,
                "crowd": 10000,
            },
            {
                "game_id": 2,
                "year": 2025,
                "date": "2025-03-16 13:20",
                "home_team": "Geelong",
                "away_team": "St Kilda",
                "venue": "GMHBA Stadium",
                "margin": 30,
                "crowd": 35000,
            },
        ]
    )

    result = score_fan_growth_opportunities(games)
    fan_growth = dict(
        zip(
            result["game_id"],
            result["fan_growth_opportunity_score"],
            strict=False,
        )
    )

    assert fan_growth[1] > fan_growth[2]


def test_scoring_works_without_crowd_data() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "year": 2025,
                "date": "2025-03-14 19:40",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "MCG",
                "margin": 4,
            }
        ]
    )

    result = score_fan_growth_opportunities(games)

    assert pd.isna(result.loc[0, "estimated_capacity_utilisation"])
    assert result.loc[0, "fixture_attractiveness_score"] > 0
