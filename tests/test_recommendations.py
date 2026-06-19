import pandas as pd

from afl_strategy_dashboard.insights.recommendations import (
    generate_fan_growth_recommendations,
    generate_strategy_recommendations,
)


def test_recommendation_generation() -> None:
    fixture_balance = pd.DataFrame(
        [
            {
                "team": "Carlton",
                "home_games": 2,
                "away_games": 1,
                "home_away_diff": 1,
            }
        ]
    )
    travel_counts = pd.DataFrame(
        [
            {
                "team": "West Coast",
                "interstate_travel_games": 2,
                "total_games": 3,
            }
        ]
    )
    competitive_summary = pd.DataFrame(
        [
            {
                "close_game_rate": 0.33,
                "blowout_game_rate": 0.1,
            }
        ]
    )
    attractiveness = pd.DataFrame(
        [
            {
                "home_team_normalised": "Carlton",
                "away_team_normalised": "Collingwood",
                "fixture_attractiveness_score": 75,
            }
        ]
    )

    recommendations = generate_strategy_recommendations(
        fixture_balance=fixture_balance,
        travel_counts=travel_counts,
        competitive_summary=competitive_summary,
        fixture_attractiveness=attractiveness,
    )

    combined = " ".join(recommendations)
    assert "West Coast" in combined
    assert "Carlton v Collingwood" in combined
    assert "public data only" in combined


def test_fixture_travel_recommendations_are_cautious() -> None:
    fixture_equity = pd.DataFrame(
        [
            {
                "team": "Carlton",
                "fixture_equity_risk_score": 8.5,
                "home_away_differential": -2,
            }
        ]
    )
    travel_load = pd.DataFrame(
        [
            {
                "team": "West Coast",
                "travel_load_score": 12.0,
                "interstate_away_games": 3,
            }
        ]
    )

    recommendations = generate_strategy_recommendations(
        fixture_equity=fixture_equity,
        travel_load=travel_load,
    )
    combined = " ".join(recommendations)

    assert recommendations
    assert "Fixture equity" in combined
    assert "Travel load" in combined
    assert "appears" in combined or "may warrant review" in combined
    assert "must" not in combined.lower()


def test_fan_growth_recommendations_are_cautious() -> None:
    opportunities = pd.DataFrame(
        [
            {
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "commercial_opportunity_score": 75,
                "fan_growth_opportunity_score": 45,
                "growth_market_flag": False,
                "regional_or_special_event_flag": False,
                "estimated_capacity_utilisation": 0.82,
                "fixture_attractiveness_score": 80,
            },
            {
                "home_team": "Gold Coast",
                "away_team": "Brisbane Lions",
                "commercial_opportunity_score": 45,
                "fan_growth_opportunity_score": 65,
                "growth_market_flag": True,
                "regional_or_special_event_flag": False,
                "estimated_capacity_utilisation": 0.5,
                "fixture_attractiveness_score": 50,
            },
        ]
    )

    recommendations = generate_fan_growth_recommendations(opportunities)
    combined = " ".join(recommendations).lower()

    assert recommendations
    assert "may" in combined or "appears" in combined or "suggesting" in combined
    assert "public" in combined
    assert "must" not in combined
    assert "guarantees" not in combined
