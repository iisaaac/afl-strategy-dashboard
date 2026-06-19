"""Client for the public Squiggle AFL API."""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

import pandas as pd
import requests

from afl_strategy_dashboard.data.cache import get_or_create_dataframe

DEFAULT_USER_AGENT = "afl-strategy-dashboard/0.1"
BASE_URL = "https://api.squiggle.com.au/"
NORMALISED_GAME_COLUMNS = [
    "game_id",
    "year",
    "round",
    "round_name",
    "date",
    "venue",
    "home_team",
    "away_team",
    "home_score",
    "away_score",
    "winner",
    "complete",
    "is_final",
    "season_phase",
    "margin",
    "predicted_home_win_probability",
    "predicted_away_win_probability",
    "source",
]


class SquiggleAPIError(RuntimeError):
    """Raised when Squiggle data cannot be fetched or parsed."""


@dataclass
class SquiggleClient:
    """Responsible, cache-aware Squiggle API client."""

    base_url: str = BASE_URL
    timeout_seconds: int = 20
    session: requests.Session = field(default_factory=requests.Session)

    @property
    def user_agent(self) -> str:
        """Return the configured User-Agent."""
        return os.getenv("AFL_DASHBOARD_USER_AGENT", DEFAULT_USER_AGENT)

    def fetch_games(self, year: int, *, refresh: bool = False) -> pd.DataFrame:
        """Fetch AFL games for a season year."""
        cache_name = f"squiggle_games_{year}"
        return get_or_create_dataframe(
            cache_name,
            lambda: self._fetch_query("games", {"year": year}, expected_key="games"),
            refresh=refresh,
        )

    def fetch_games_normalised(
        self, year: int, *, refresh: bool = False
    ) -> pd.DataFrame:
        """Fetch and normalise AFL games into the dashboard schema."""
        cache_name = f"squiggle_games_normalised_{year}"
        games = get_or_create_dataframe(
            cache_name,
            lambda: normalise_games(self.fetch_games(year, refresh=refresh), year=year),
            layer="processed",
            refresh=refresh,
        )
        return _coerce_normalised_types(games)

    def fetch_ladder(self, year: int, *, refresh: bool = False) -> pd.DataFrame:
        """Fetch AFL standings for a season year where supported by Squiggle."""
        cache_name = f"squiggle_standings_{year}"
        return get_or_create_dataframe(
            cache_name,
            lambda: self._fetch_query(
                "standings", {"year": year}, expected_key="standings"
            ),
            refresh=refresh,
        )

    def _fetch_query(
        self,
        query: str,
        params: dict[str, Any] | None = None,
        *,
        expected_key: str,
    ) -> pd.DataFrame:
        request_params = {"q": query}
        if params:
            request_params.update(params)

        try:
            response = self.session.get(
                self.base_url,
                params=request_params,
                headers={"User-Agent": self.user_agent},
                timeout=self.timeout_seconds,
            )
            response.raise_for_status()
        except requests.Timeout as exc:
            raise SquiggleAPIError("Squiggle API request timed out.") from exc
        except requests.HTTPError as exc:
            status = exc.response.status_code if exc.response is not None else "unknown"
            raise SquiggleAPIError(
                f"Squiggle API returned an HTTP error: {status}."
            ) from exc
        except requests.RequestException as exc:
            raise SquiggleAPIError("Squiggle API request failed.") from exc

        try:
            payload = response.json()
        except ValueError as exc:
            raise SquiggleAPIError("Squiggle API returned invalid JSON.") from exc

        records = payload.get(expected_key)
        if records is None:
            # Some endpoints return a single top-level list or use the query as a key.
            records = payload.get(query, payload if isinstance(payload, list) else None)

        if records is None:
            keys = ", ".join(payload.keys()) if isinstance(payload, dict) else "none"
            raise SquiggleAPIError(
                f"Squiggle response did not include `{expected_key}`. Keys: {keys}."
            )

        return pd.json_normalize(records)


def normalise_games(games: pd.DataFrame, *, year: int | None = None) -> pd.DataFrame:
    """Normalise Squiggle game data into a stable internal schema."""
    if games.empty:
        return pd.DataFrame(columns=NORMALISED_GAME_COLUMNS)

    normalised = pd.DataFrame(index=games.index)
    normalised["game_id"] = _column_or_na(games, ("id", "game_id"))
    normalised["year"] = _column_or_value(games, ("year",), year)
    normalised["round"] = _column_or_na(games, ("round",))
    normalised["round_name"] = _column_or_na(
        games, ("roundname", "round_name", "roundName")
    )
    normalised["date"] = pd.to_datetime(
        _column_or_na(games, ("date", "localtime", "timestr")), errors="coerce"
    )
    normalised["venue"] = _column_or_na(games, ("venue", "venue_name", "ground"))
    normalised["home_team"] = _column_or_na(games, ("hteam", "home_team", "home"))
    normalised["away_team"] = _column_or_na(games, ("ateam", "away_team", "away"))
    normalised["home_score"] = pd.to_numeric(
        _column_or_na(games, ("hscore", "home_score", "homeScore")), errors="coerce"
    )
    normalised["away_score"] = pd.to_numeric(
        _column_or_na(games, ("ascore", "away_score", "awayScore")), errors="coerce"
    )
    normalised["winner"] = _winner(games, normalised)
    normalised["complete"] = _column_or_na(games, ("complete",))
    normalised["is_final"] = _normalise_bool(_column_or_na(games, ("is_final",)))
    normalised["season_phase"] = [
        classify_season_phase(round_value, round_name)
        for round_value, round_name in zip(
            normalised["round"], normalised["round_name"], strict=False
        )
    ]
    normalised["margin"] = (normalised["home_score"] - normalised["away_score"]).abs()
    normalised["predicted_home_win_probability"] = pd.to_numeric(
        _column_or_na(
            games,
            (
                "predicted_home_win_probability",
                "hconfidence",
                "home_win_probability",
            ),
        ),
        errors="coerce",
    )
    normalised["predicted_away_win_probability"] = pd.to_numeric(
        _column_or_na(
            games,
            (
                "predicted_away_win_probability",
                "aconfidence",
                "away_win_probability",
            ),
        ),
        errors="coerce",
    )
    normalised["source"] = "Squiggle API"

    missing_ids = normalised["game_id"].isna()
    if missing_ids.any():
        stable_ids = (
            normalised.loc[missing_ids, "year"].astype("string").fillna("")
            + "-"
            + normalised.loc[missing_ids, "round"].astype("string").fillna("")
            + "-"
            + normalised.loc[missing_ids, "home_team"].astype("string").fillna("")
            + "-"
            + normalised.loc[missing_ids, "away_team"].astype("string").fillna("")
        )
        normalised.loc[missing_ids, "game_id"] = stable_ids.str.replace(
            r"\s+", "-", regex=True
        )

    for column in NORMALISED_GAME_COLUMNS:
        if column not in normalised.columns:
            normalised[column] = pd.NA
    return _coerce_normalised_types(normalised[NORMALISED_GAME_COLUMNS])


def _column_or_na(games: pd.DataFrame, candidates: tuple[str, ...]) -> pd.Series:
    for column in candidates:
        if column in games.columns:
            return games[column]
    return pd.Series(pd.NA, index=games.index)


def _column_or_value(
    games: pd.DataFrame, candidates: tuple[str, ...], value: object
) -> pd.Series:
    for column in candidates:
        if column in games.columns:
            return games[column]
    return pd.Series(value, index=games.index)


def _winner(games: pd.DataFrame, normalised: pd.DataFrame) -> pd.Series:
    winner = _column_or_na(games, ("winner", "winning_team"))
    missing_winner = winner.isna() | (winner.astype("string").str.len() == 0)
    derived = pd.Series(pd.NA, index=games.index, dtype="object")
    derived.loc[normalised["home_score"] > normalised["away_score"]] = normalised.loc[
        normalised["home_score"] > normalised["away_score"], "home_team"
    ]
    derived.loc[normalised["away_score"] > normalised["home_score"]] = normalised.loc[
        normalised["away_score"] > normalised["home_score"], "away_team"
    ]
    derived.loc[normalised["home_score"] == normalised["away_score"]] = "Draw"
    winner = winner.copy()
    winner.loc[missing_winner] = derived.loc[missing_winner]
    return winner


def _normalise_bool(values: pd.Series) -> pd.Series:
    true_values = {"1", "true", "yes", "y"}
    false_values = {"0", "false", "no", "n"}
    result = values.copy()
    if result.empty:
        return result.astype("boolean")
    text = result.astype("string").str.lower()
    bools = pd.Series(pd.NA, index=values.index, dtype="boolean")
    bools.loc[text.isin(true_values)] = True
    bools.loc[text.isin(false_values)] = False
    bools.loc[values == 1] = True
    bools.loc[values == 0] = False
    return bools


def classify_season_phase(
    round_value: object,
    round_name: object | None = None,
) -> str:
    """Classify a fixture as home-and-away, finals or unknown."""
    text_values = [
        str(value).strip()
        for value in (round_name, round_value)
        if value is not None and pd.notna(value) and str(value).strip()
    ]
    combined = " ".join(text_values).lower()
    if not combined:
        return "unknown"

    finals_terms = (
        "elimination final",
        "qualifying final",
        "semi final",
        "semi-final",
        "preliminary final",
        "grand final",
        "finals",
        "final",
    )
    if any(term in combined for term in finals_terms):
        return "finals"

    tokens = {token.strip(" .,-_/()[]").upper() for token in combined.split()}
    if tokens.intersection({"EF", "QF", "SF", "PF", "GF"}):
        return "finals"

    if "round" in combined or "opening round" in combined:
        return "home_and_away"

    numeric_round = pd.to_numeric(pd.Series([round_value]), errors="coerce").iloc[0]
    if pd.notna(numeric_round) and 0 <= float(numeric_round) <= 30:
        return "home_and_away"

    return "unknown"


def _coerce_normalised_types(games: pd.DataFrame) -> pd.DataFrame:
    normalised = games.copy()
    if "date" in normalised.columns:
        normalised["date"] = pd.to_datetime(normalised["date"], errors="coerce")
    for column in (
        "year",
        "round",
        "home_score",
        "away_score",
        "complete",
        "margin",
        "predicted_home_win_probability",
        "predicted_away_win_probability",
    ):
        if column in normalised.columns:
            normalised[column] = pd.to_numeric(normalised[column], errors="coerce")
    if "is_final" in normalised.columns:
        normalised["is_final"] = _normalise_bool(normalised["is_final"])
    if "season_phase" not in normalised.columns:
        normalised["season_phase"] = [
            classify_season_phase(round_value, round_name)
            for round_value, round_name in zip(
                normalised.get("round", pd.Series(pd.NA, index=normalised.index)),
                normalised.get("round_name", pd.Series(pd.NA, index=normalised.index)),
                strict=False,
            )
        ]
    else:
        normalised["season_phase"] = normalised["season_phase"].fillna("unknown")
    return normalised
