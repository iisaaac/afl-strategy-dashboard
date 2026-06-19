"""Fan-growth and commercial opportunity feature engineering."""

from __future__ import annotations

import pandas as pd

from afl_strategy_dashboard.features.competitive_balance import calculate_match_margins
from afl_strategy_dashboard.features.fixture_equity import (
    AWAY_COLUMNS,
    HOME_COLUMNS,
    _first_existing_column,
)
from afl_strategy_dashboard.features.travel_load import VENUE_COLUMNS
from afl_strategy_dashboard.utils.venues import (
    get_venue_capacity,
    get_venue_info,
    get_venue_market_type,
    is_major_stadium,
    normalise_venue_name,
)

RIVALRY_PAIRS = {
    frozenset(("Carlton", "Collingwood")),
    frozenset(("Collingwood", "Essendon")),
    frozenset(("Carlton", "Essendon")),
    frozenset(("Fremantle", "West Coast")),
    frozenset(("Adelaide", "Port Adelaide")),
    frozenset(("Brisbane", "Gold Coast")),
    frozenset(("Brisbane Lions", "Gold Coast")),
    frozenset(("Greater Western Sydney", "Sydney")),
    frozenset(("GWS", "Sydney")),
    frozenset(("Geelong", "Hawthorn")),
    frozenset(("Richmond", "Carlton")),
    frozenset(("Collingwood", "Richmond")),
    frozenset(("Melbourne", "Collingwood")),
}

SIGNIFICANT_VENUES = {
    "MCG",
    "Marvel Stadium",
    "Adelaide Oval",
    "Optus Stadium",
    "SCG",
    "Gabba",
}

PRIME_BROADCAST_WINDOWS = {"Thursday night", "Friday night", "Saturday night"}
LARGE_MARKET_TEAMS = {
    "Carlton",
    "Collingwood",
    "Essendon",
    "Richmond",
    "Melbourne",
    "Hawthorn",
    "Geelong",
    "Sydney",
    "West Coast",
    "Adelaide",
}

OPPORTUNITY_COLUMNS = [
    "game_id",
    "year",
    "round",
    "date",
    "venue",
    "home_team",
    "away_team",
    "crowd",
    "venue_capacity",
    "estimated_capacity_utilisation",
    "broadcast_window",
    "market_type",
    "rivalry_flag",
    "top_ladder_or_form_flag",
    "close_game_or_competitive_flag",
    "growth_market_flag",
    "regional_or_special_event_flag",
    "fixture_attractiveness_score",
    "fan_growth_opportunity_score",
    "commercial_opportunity_score",
    "opportunity_category",
    "opportunity_notes",
]


def identify_marquee_style_fixtures(
    games: pd.DataFrame,
    ladder: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Flag simple public-data signals of high-interest fixtures."""
    scored = generate_fixture_attractiveness_score(games, ladder=ladder)
    return scored.loc[scored["marquee_signal_count"] > 0].reset_index(drop=True)


def generate_fixture_attractiveness_score(
    games: pd.DataFrame,
    ladder: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Create a transparent starter fixture attractiveness score."""
    scored = score_fan_growth_opportunities(games, ladder=ladder)
    result = games.copy().reset_index(drop=True)
    result["home_team_normalised"] = scored["home_team"].astype(str)
    result["away_team_normalised"] = scored["away_team"].astype(str)
    result["is_rivalry"] = scored["rivalry_flag"]
    result["is_significant_venue"] = scored["venue"].isin(SIGNIFICANT_VENUES)
    result["has_top_ladder_team"] = scored["top_ladder_or_form_flag"]
    result["close_recent_form_signal"] = scored["close_game_or_competitive_flag"]
    result["marquee_signal_count"] = result[
        [
            "is_rivalry",
            "is_significant_venue",
            "has_top_ladder_team",
            "close_recent_form_signal",
        ]
    ].sum(axis=1)
    result["fixture_attractiveness_score"] = scored["fixture_attractiveness_score"]
    return result.sort_values(
        ["fixture_attractiveness_score", "marquee_signal_count"],
        ascending=[False, False],
    ).reset_index(drop=True)


def rank_high_interest_fixtures(
    games: pd.DataFrame,
    ladder: pd.DataFrame | None = None,
    *,
    top_n: int = 10,
) -> pd.DataFrame:
    """Return a ranked table of high-interest fixtures."""
    ranked = generate_fixture_attractiveness_score(games, ladder=ladder)
    columns = [
        col
        for col in [
            "game_id",
            "id",
            "year",
            "round",
            "date",
            "home_team_normalised",
            "away_team_normalised",
            "venue",
            "fixture_attractiveness_score",
            "is_rivalry",
            "has_top_ladder_team",
            "is_significant_venue",
            "close_recent_form_signal",
        ]
        if col in ranked.columns
    ]
    return ranked[columns].head(top_n)


def score_fan_growth_opportunities(
    games: pd.DataFrame,
    ladder: pd.DataFrame | None = None,
) -> pd.DataFrame:
    """Score fixture-level fan-growth and commercial opportunity."""
    if games.empty:
        return pd.DataFrame(columns=OPPORTUNITY_COLUMNS)

    home_col = _first_existing_column(games, HOME_COLUMNS)
    away_col = _first_existing_column(games, AWAY_COLUMNS)
    venue_col = _first_existing_column(games, VENUE_COLUMNS)
    result = pd.DataFrame(index=games.index)
    result["game_id"] = _column_or_value(games, ("game_id", "id"), pd.NA)
    result["year"] = _column_or_value(games, ("year",), pd.NA)
    result["round"] = _column_or_value(games, ("round",), pd.NA)
    result["date"] = pd.to_datetime(_column_or_value(games, ("date",), pd.NaT))
    result["venue"] = games[venue_col].map(normalise_venue_name)
    result["home_team"] = games[home_col].astype("string")
    result["away_team"] = games[away_col].astype("string")
    result["crowd"] = pd.to_numeric(_column_or_value(games, ("crowd",), pd.NA))
    result["venue_capacity"] = result["venue"].map(get_venue_capacity)
    result["estimated_capacity_utilisation"] = (
        result["crowd"] / result["venue_capacity"]
    )
    result.loc[
        result["crowd"].isna() | result["venue_capacity"].isna(),
        "estimated_capacity_utilisation",
    ] = pd.NA
    result["broadcast_window"] = result["date"].map(classify_broadcast_window)
    result["market_type"] = result["venue"].map(get_venue_market_type)
    result["rivalry_flag"] = result.apply(
        lambda row: is_rivalry_fixture(row["home_team"], row["away_team"]), axis=1
    )
    result["top_ladder_or_form_flag"] = _has_top_ladder_or_form_signal(
        games, result, ladder
    )
    result["close_game_or_competitive_flag"] = _competitive_fixture_signal(games)
    result["growth_market_flag"] = result["market_type"].eq("growth_market")
    result["regional_or_special_event_flag"] = result["venue"].map(
        lambda venue: bool(
            (info := get_venue_info(venue)) and info.is_regional_or_special_event
        )
    )
    result["fixture_attractiveness_score"] = result.apply(
        _fixture_attractiveness_score, axis=1
    )
    result["fan_growth_opportunity_score"] = result.apply(
        _fan_growth_opportunity_score, axis=1
    )
    result["commercial_opportunity_score"] = result.apply(
        _commercial_opportunity_score, axis=1
    )
    result["opportunity_category"] = result.apply(_opportunity_category, axis=1)
    result["opportunity_notes"] = result.apply(_opportunity_notes, axis=1)
    return (
        result[OPPORTUNITY_COLUMNS]
        .sort_values(
            ["commercial_opportunity_score", "fan_growth_opportunity_score"],
            ascending=[False, False],
        )
        .reset_index(drop=True)
    )


def classify_broadcast_window(value: object) -> str:
    """Classify fixture timing into broad broadcast-window style buckets."""
    date = pd.to_datetime(value, errors="coerce")
    if pd.isna(date):
        return "Other / unknown"

    day_name = date.day_name()
    hour = date.hour
    if day_name == "Thursday" and hour >= 18:
        return "Thursday night"
    if day_name == "Friday" and hour >= 18:
        return "Friday night"
    if day_name == "Saturday":
        if hour < 16:
            return "Saturday day"
        if hour < 18:
            return "Saturday twilight"
        return "Saturday night"
    if day_name == "Sunday":
        if hour < 16:
            return "Sunday day"
        return "Sunday twilight"
    return "Other / unknown"


def is_rivalry_fixture(home_team: object, away_team: object) -> bool:
    """Return whether a fixture is in the maintained rivalry mapping."""
    if not isinstance(home_team, str) or not isinstance(away_team, str):
        return False
    return frozenset((home_team, away_team)) in RIVALRY_PAIRS


def _has_top_ladder_or_form_signal(
    games: pd.DataFrame,
    result: pd.DataFrame,
    ladder: pd.DataFrame | None,
) -> pd.Series:
    if ladder is not None and not ladder.empty:
        team_col = next(
            (col for col in ("team", "team_name", "name") if col in ladder.columns),
            None,
        )
        rank_col = next(
            (
                col
                for col in ("rank", "position", "standing", "place")
                if col in ladder.columns
            ),
            None,
        )
        if team_col and rank_col:
            ladder_working = ladder[[team_col, rank_col]].copy()
            ladder_working[rank_col] = pd.to_numeric(
                ladder_working[rank_col], errors="coerce"
            )
            top_teams = set(ladder_working.loc[ladder_working[rank_col] <= 4, team_col])
            return result["home_team"].isin(top_teams) | result["away_team"].isin(
                top_teams
            )

    rank_columns = [
        col
        for col in (
            "home_ladder_rank",
            "away_ladder_rank",
            "home_rank",
            "away_rank",
        )
        if col in games.columns
    ]
    if len(rank_columns) >= 2:
        ranks = games[rank_columns].apply(pd.to_numeric, errors="coerce")
        return ranks.le(4).any(axis=1)
    return pd.Series(False, index=games.index)


def _competitive_fixture_signal(games: pd.DataFrame) -> pd.Series:
    if "margin" in games.columns:
        margins = pd.to_numeric(games["margin"], errors="coerce")
    else:
        try:
            margins = calculate_match_margins(games)["margin_abs"]
        except KeyError:
            margins = pd.Series(pd.NA, index=games.index)

    completed_signal = margins.le(12).fillna(False)
    home_prob = pd.to_numeric(
        _column_or_value(
            games,
            ("predicted_home_win_probability", "hconfidence", "home_win_probability"),
            pd.NA,
        ),
        errors="coerce",
    )
    away_prob = pd.to_numeric(
        _column_or_value(
            games,
            ("predicted_away_win_probability", "aconfidence", "away_win_probability"),
            pd.NA,
        ),
        errors="coerce",
    )
    probability_signal = home_prob.between(0.4, 0.6) | away_prob.between(0.4, 0.6)
    return completed_signal | probability_signal.fillna(False)


def _fixture_attractiveness_score(row: pd.Series) -> float:
    utilisation = _utilisation(row)
    score = 0.0
    score += 30 if row["rivalry_flag"] else 0
    score += 20 if row["broadcast_window"] in PRIME_BROADCAST_WINDOWS else 0
    score += 15 if is_major_stadium(row["venue"]) else 0
    score += 15 if row["close_game_or_competitive_flag"] else 0
    score += 10 if row["top_ladder_or_form_flag"] else 0
    score += 10 if utilisation is not None and utilisation >= 0.75 else 0
    return round(score, 2)


def _fan_growth_opportunity_score(row: pd.Series) -> float:
    utilisation = _utilisation(row)
    score = row["fixture_attractiveness_score"] * 0.25
    score += 25 if row["growth_market_flag"] else 0
    score += 20 if row["regional_or_special_event_flag"] else 0
    score += 15 if row["close_game_or_competitive_flag"] else 0
    score += 15 if utilisation is not None and utilisation < 0.65 else 0
    score += 10 if row["broadcast_window"] in PRIME_BROADCAST_WINDOWS else 0
    return round(score, 2)


def _commercial_opportunity_score(row: pd.Series) -> float:
    utilisation = _utilisation(row)
    capacity = row["venue_capacity"] if pd.notna(row["venue_capacity"]) else 0
    large_market_teams = int(row["home_team"] in LARGE_MARKET_TEAMS) + int(
        row["away_team"] in LARGE_MARKET_TEAMS
    )
    score = 0.0
    score += min(float(capacity) / 2500, 25)
    score += 20 if utilisation is not None and utilisation >= 0.75 else 0
    score += 15 if row["rivalry_flag"] else 0
    score += 15 if row["broadcast_window"] in PRIME_BROADCAST_WINDOWS else 0
    score += large_market_teams * 5
    score += 10 if row["regional_or_special_event_flag"] else 0
    return round(score, 2)


def _opportunity_category(row: pd.Series) -> str:
    utilisation = _utilisation(row)
    if row["commercial_opportunity_score"] >= 60 and row["rivalry_flag"]:
        return "Marquee commercial fixture"
    if row["growth_market_flag"] and row["fan_growth_opportunity_score"] >= 35:
        return "Growth market opportunity"
    if row["regional_or_special_event_flag"]:
        return "Regional/community engagement opportunity"
    if (
        utilisation is not None
        and utilisation < 0.65
        and row["fixture_attractiveness_score"] >= 35
    ):
        return "Under-utilised attendance opportunity"
    if row["close_game_or_competitive_flag"]:
        return "Competitive balance showcase"
    return "Standard fixture"


def _opportunity_notes(row: pd.Series) -> str:
    reasons: list[str] = []
    if row["rivalry_flag"]:
        reasons.append("rivalry context")
    if row["broadcast_window"] in PRIME_BROADCAST_WINDOWS:
        reasons.append("prime broadcast-window style timing")
    if row["growth_market_flag"]:
        reasons.append("growth-market venue context")
    if row["regional_or_special_event_flag"]:
        reasons.append("regional or special-event venue context")
    utilisation = _utilisation(row)
    if utilisation is not None and utilisation < 0.65:
        reasons.append("visible attendance upside against approximate capacity")
    if not reasons:
        return "Standard public-data opportunity profile."
    return (
        "Opportunity signal reflects "
        + ", ".join(reasons)
        + ". Scores are heuristic and not official AFL priorities."
    )


def _utilisation(row: pd.Series) -> float | None:
    value = row.get("estimated_capacity_utilisation")
    if pd.isna(value):
        return None
    return float(value)


def _column_or_value(
    games: pd.DataFrame, candidates: tuple[str, ...], value: object
) -> pd.Series:
    for column in candidates:
        if column in games.columns:
            return games[column]
    return pd.Series(value, index=games.index)
