"""Attendance data helpers for optional public-data enrichment."""

from __future__ import annotations

from io import StringIO
from pathlib import Path

import pandas as pd

from afl_strategy_dashboard.utils.venues import normalise_venue_name

ATTENDANCE_COLUMNS = [
    "year",
    "round",
    "date",
    "home_team",
    "away_team",
    "venue",
    "crowd",
    "source",
]

TEAM_ALIASES = {
    "adelaide crows": "Adelaide",
    "brisbane": "Brisbane Lions",
    "brisbane lions": "Brisbane Lions",
    "carlton": "Carlton",
    "collingwood": "Collingwood",
    "essendon": "Essendon",
    "fremantle": "Fremantle",
    "geelong": "Geelong",
    "gcfc": "Gold Coast",
    "gold coast": "Gold Coast",
    "gold coast suns": "Gold Coast",
    "greater western sydney": "Greater Western Sydney",
    "gws": "Greater Western Sydney",
    "hawthorn": "Hawthorn",
    "melbourne": "Melbourne",
    "north melbourne": "North Melbourne",
    "port adelaide": "Port Adelaide",
    "richmond": "Richmond",
    "st kilda": "St Kilda",
    "sydney": "Sydney",
    "sydney swans": "Sydney",
    "west coast": "West Coast",
    "west coast eagles": "West Coast",
    "western bulldogs": "Western Bulldogs",
    "footscray": "Western Bulldogs",
}


class AttendanceDataError(ValueError):
    """Raised when attendance data cannot be loaded cleanly."""


def normalise_team_name(name: object) -> str:
    """Return a canonical team name for matching."""
    if not isinstance(name, str) or not name.strip():
        return ""
    cleaned = " ".join(name.strip().split())
    return TEAM_ALIASES.get(cleaned.lower(), cleaned)


def load_attendance_csv(path: str | Path) -> pd.DataFrame:
    """Load and clean local attendance CSV data."""
    csv_path = Path(path)
    if not csv_path.exists():
        raise AttendanceDataError(f"Attendance CSV does not exist: {csv_path}")
    try:
        raw = pd.read_csv(csv_path)
    except Exception as exc:  # pragma: no cover - pandas exception surface varies.
        raise AttendanceDataError(f"Attendance CSV could not be read: {exc}") from exc
    return clean_attendance_dataframe(raw)


def clean_attendance_dataframe(attendance: pd.DataFrame) -> pd.DataFrame:
    """Clean an already-loaded attendance DataFrame."""
    if "crowd" not in attendance.columns:
        raise AttendanceDataError("Attendance data must include a `crowd` column.")

    result = attendance.copy()
    for column in ATTENDANCE_COLUMNS:
        if column not in result.columns:
            result[column] = pd.NA

    result["year"] = pd.to_numeric(result["year"], errors="coerce")
    result["round"] = result["round"].astype("string")
    result["date"] = pd.to_datetime(result["date"], errors="coerce")
    result["home_team"] = result["home_team"].map(normalise_team_name)
    result["away_team"] = result["away_team"].map(normalise_team_name)
    result["venue"] = result["venue"].map(normalise_venue_name)
    result["crowd"] = pd.to_numeric(
        result["crowd"].astype("string").str.replace(",", "", regex=False),
        errors="coerce",
    )
    result["source"] = result["source"].fillna("Local attendance CSV")
    return result[ATTENDANCE_COLUMNS]


def parse_afl_tables_crowds_html(html: str, year: int) -> pd.DataFrame:
    """Parse an already-supplied AFL Tables-style crowds HTML string.

    This helper does not fetch live data. It is an optional public-data enrichment
    path for users who separately save or provide suitable HTML.
    """
    if not html.strip():
        return pd.DataFrame(columns=ATTENDANCE_COLUMNS)

    try:
        tables = pd.read_html(StringIO(html))
    except (ImportError, ValueError):
        return pd.DataFrame(columns=ATTENDANCE_COLUMNS)

    for table in tables:
        normalised_columns = {str(col).strip().lower(): col for col in table.columns}
        crowd_col = next(
            (
                normalised_columns[col]
                for col in ("crowd", "attendance", "att")
                if col in normalised_columns
            ),
            None,
        )
        if crowd_col is None:
            continue

        parsed = pd.DataFrame()
        parsed["year"] = year
        parsed["round"] = _optional_column(table, normalised_columns, ("round", "rnd"))
        parsed["date"] = _optional_column(table, normalised_columns, ("date",))
        parsed["home_team"] = _optional_column(
            table, normalised_columns, ("home_team", "home", "team")
        )
        parsed["away_team"] = _optional_column(
            table, normalised_columns, ("away_team", "away", "opponent")
        )
        parsed["venue"] = _optional_column(
            table, normalised_columns, ("venue", "ground")
        )
        parsed["crowd"] = table[crowd_col]
        parsed["source"] = "AFL Tables public HTML"
        try:
            return clean_attendance_dataframe(parsed)
        except AttendanceDataError:
            return pd.DataFrame(columns=ATTENDANCE_COLUMNS)

    return pd.DataFrame(columns=ATTENDANCE_COLUMNS)


def merge_attendance_with_games(
    games: pd.DataFrame, attendance: pd.DataFrame
) -> pd.DataFrame:
    """Merge attendance context onto normalised fixture data."""
    result = games.copy()
    result["crowd"] = pd.NA
    result["attendance_source"] = pd.NA
    result["attendance_match_confidence"] = "unmatched"
    if games.empty or attendance.empty:
        return result

    attendance_clean = clean_attendance_dataframe(attendance)
    attendance_records = attendance_clean.to_dict("records")

    for game_index, game in result.iterrows():
        match = _best_attendance_match(game, attendance_records)
        if match is None:
            continue
        record, confidence = match
        result.at[game_index, "crowd"] = record.get("crowd")
        result.at[game_index, "attendance_source"] = record.get("source")
        result.at[game_index, "attendance_match_confidence"] = confidence

    result["crowd"] = pd.to_numeric(result["crowd"], errors="coerce")
    return result


def _best_attendance_match(
    game: pd.Series, attendance_records: list[dict[str, object]]
) -> tuple[dict[str, object], str] | None:
    game_year = int(game["year"]) if pd.notna(game.get("year")) else None
    game_date = pd.to_datetime(game.get("date"), errors="coerce")
    game_home = normalise_team_name(game.get("home_team"))
    game_away = normalise_team_name(game.get("away_team"))
    game_venue = normalise_venue_name(game.get("venue"))

    best: tuple[dict[str, object], int] | None = None
    for record in attendance_records:
        if game_year is not None and pd.notna(record.get("year")):
            if int(record["year"]) != game_year:
                continue
        if normalise_team_name(record.get("home_team")) != game_home:
            continue
        if normalise_team_name(record.get("away_team")) != game_away:
            continue

        score = 2
        record_venue = normalise_venue_name(record.get("venue"))
        if record_venue and game_venue and record_venue == game_venue:
            score += 2
        record_date = pd.to_datetime(record.get("date"), errors="coerce")
        if pd.notna(record_date) and pd.notna(game_date):
            date_delta = abs((record_date.date() - game_date.date()).days)
            if date_delta == 0:
                score += 3
            elif date_delta <= 1:
                score += 1
        if best is None or score > best[1]:
            best = (record, score)

    if best is None:
        return None
    confidence = "high" if best[1] >= 7 else "medium" if best[1] >= 4 else "low"
    return best[0], confidence


def _optional_column(
    table: pd.DataFrame,
    columns: dict[str, object],
    candidates: tuple[str, ...],
) -> pd.Series:
    for candidate in candidates:
        if candidate in columns:
            return table[columns[candidate]]
    return pd.Series(pd.NA, index=table.index)
