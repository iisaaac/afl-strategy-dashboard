"""Executive-style recommendation generation."""

from __future__ import annotations

import pandas as pd


def generate_strategy_recommendations(
    fixture_balance: pd.DataFrame | None = None,
    travel_counts: pd.DataFrame | None = None,
    competitive_summary: pd.DataFrame | None = None,
    fixture_attractiveness: pd.DataFrame | None = None,
    fixture_equity: pd.DataFrame | None = None,
    travel_load: pd.DataFrame | None = None,
) -> list[str]:
    """Convert feature outputs into cautious executive recommendations."""
    recommendations: list[str] = []
    fixture_table = fixture_equity if fixture_equity is not None else fixture_balance
    travel_table = travel_load if travel_load is not None else travel_counts

    if fixture_table is not None and not fixture_table.empty:
        risk_col = (
            "fixture_equity_risk_score"
            if "fixture_equity_risk_score" in fixture_table.columns
            else None
        )
        if risk_col:
            leaders = fixture_table.sort_values(risk_col, ascending=False).head(3)
            teams = ", ".join(leaders["team"].dropna().astype(str))
            recommendations.append(
                "Fixture equity risk appears concentrated among "
                f"{teams}, mainly reflecting the public-data heuristic for "
                "short-break exposure, home-away balance and away-game sequences. "
                "This may warrant review alongside commercial, stadium and "
                "broadcast constraints."
            )
        else:
            diff_col = (
                "home_away_differential"
                if "home_away_differential" in fixture_table.columns
                else "home_away_diff"
            )
            if diff_col in fixture_table.columns:
                most_imbalanced = fixture_table.assign(
                    imbalance=fixture_table[diff_col].abs()
                ).sort_values("imbalance", ascending=False)
                top_team = str(most_imbalanced.iloc[0]["team"])
                recommendations.append(
                    "Home and away balance shows the largest visible variation for "
                    f"{top_team}. This should be treated as a public-data flag for "
                    "deeper fixture review rather than a standalone fairness "
                    "conclusion."
                )

    if travel_table is not None and not travel_table.empty:
        if "travel_load_score" in travel_table.columns:
            leaders = travel_table.sort_values(
                "travel_load_score", ascending=False
            ).head(3)
            teams = ", ".join(leaders["team"].dropna().astype(str))
            recommendations.append(
                "Travel load appears highest for "
                f"{teams}, particularly where interstate trips, long-haul travel "
                "and shorter recovery windows overlap. Further internal review "
                "could combine this lens with player welfare, venue availability "
                "and broadcast considerations."
            )
        elif "interstate_travel_games" in travel_table.columns:
            leaders = travel_table.sort_values(
                "interstate_travel_games", ascending=False
            ).head(3)
            teams = ", ".join(leaders["team"].dropna().astype(str))
            recommendations.append(
                "Interstate travel load appears concentrated among "
                f"{teams}, suggesting fixture equity could be reviewed alongside "
                "commercial, venue and broadcast objectives."
            )

    if (
        fixture_table is not None
        and not fixture_table.empty
        and "home_away_differential" in fixture_table.columns
    ):
        average_away_imbalance = fixture_table["home_away_differential"].lt(0).sum()
        recommendations.append(
            "Home and away balance varies across clubs, with "
            f"{average_away_imbalance} clubs showing more away than home games in "
            "the filtered dataset. This public-data model should be considered "
            "alongside commercial, stadium and broadcast objectives before drawing "
            "firm conclusions."
        )

    if (
        fixture_table is None
        or fixture_table.empty
        or travel_table is None
        or travel_table.empty
    ):
        recommendations.append(
            "Fixture equity and travel-load recommendations are limited because "
            "one or more analytical tables are empty for the selected filters."
        )

    if competitive_summary is not None and not competitive_summary.empty:
        row = competitive_summary.iloc[0]
        close_rate = float(row.get("close_game_rate", 0))
        blowout_rate = float(row.get("blowout_game_rate", 0))
        recommendations.append(
            "Close-game frequency is currently estimated at "
            f"{close_rate:.0%}, while blowout frequency is estimated at "
            f"{blowout_rate:.0%}. This gives a starting point for assessing "
            "engagement windows and broadcast promotion opportunities."
        )

    if fixture_attractiveness is not None and not fixture_attractiveness.empty:
        top_fixture = fixture_attractiveness.iloc[0]
        home = top_fixture.get("home_team_normalised", top_fixture.get("hteam", "home"))
        away = top_fixture.get("away_team_normalised", top_fixture.get("ateam", "away"))
        recommendations.append(
            f"The highest-ranked public-data fan-growth fixture is {home} v {away}. "
            "Venue concentration and rivalry signals may create opportunities for "
            "targeted campaigns around high-interest fixtures."
        )

    recommendations.append(
        "This prototype uses public data only. Recommendations should be validated "
        "with internal AFL attendance, ticketing, broadcast, digital and operations "
        "data before decisions are made."
    )
    unique = _deduplicate(recommendations)
    if len(unique) > 5:
        unique = [*unique[:4], unique[-1]]
    return unique


def generate_fan_growth_recommendations(opportunities: pd.DataFrame) -> list[str]:
    """Generate cautious fan-growth and commercial opportunity recommendations."""
    if opportunities is None or opportunities.empty:
        return [
            "Fan-growth recommendations are limited because no fixture opportunity "
            "table is available for the selected filters."
        ]

    recommendations: list[str] = []
    top_commercial = opportunities.sort_values(
        "commercial_opportunity_score", ascending=False
    ).head(3)
    if not top_commercial.empty:
        fixtures = ", ".join(
            top_commercial.apply(
                lambda row: f"{row['home_team']} v {row['away_team']}", axis=1
            )
        )
        recommendations.append(
            "Several high-scoring fixtures combine commercial context with venue "
            f"and timing signals, led by {fixtures}. These may be suitable for "
            "premium fan-engagement or commercial activation planning."
        )

    growth_count = int(opportunities["growth_market_flag"].fillna(False).sum())
    if growth_count:
        recommendations.append(
            f"Growth-market fixtures appear in {growth_count} cases in the selected "
            "data. They may be most useful when paired with competitive match "
            "profiles and clear attendance upside, but this public-data prototype "
            "cannot assess local campaign performance."
        )

    regional_count = int(
        opportunities["regional_or_special_event_flag"].fillna(False).sum()
    )
    if regional_count:
        recommendations.append(
            f"Regional and special-event fixtures appear in {regional_count} cases. "
            "They could be assessed using broader community, participation and "
            "venue objectives, as crowd size alone may understate strategic value."
        )

    low_util_high_interest = opportunities[
        opportunities["estimated_capacity_utilisation"].lt(0.65)
        & opportunities["fixture_attractiveness_score"].ge(35)
    ]
    if not low_util_high_interest.empty:
        recommendations.append(
            "Some attractive fixtures show lower estimated venue utilisation, "
            "suggesting attendance-growth or targeted local activation opportunities "
            "may warrant deeper internal review."
        )

    recommendations.append(
        "Public attendance context is incomplete and venue capacities are approximate. "
        "These outputs should be read as prioritisation prompts, not official AFL "
        "commercial forecasts."
    )
    return _deduplicate(recommendations)[:5]


def _deduplicate(recommendations: list[str]) -> list[str]:
    unique: list[str] = []
    seen: set[str] = set()
    for recommendation in recommendations:
        if recommendation not in seen:
            unique.append(recommendation)
            seen.add(recommendation)
    return unique
