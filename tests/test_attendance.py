from pathlib import Path

import pandas as pd
import pytest

from afl_strategy_dashboard.data.attendance import (
    AttendanceDataError,
    load_attendance_csv,
    merge_attendance_with_games,
    parse_afl_tables_crowds_html,
)


def test_load_attendance_csv_parses_valid_data(tmp_path: Path) -> None:
    path = tmp_path / "attendance.csv"
    path.write_text(
        "year,round,date,home_team,away_team,venue,crowd,source\n"
        '2025,1,2025-03-14 19:40,Carlton,Collingwood,M.C.G.,"82,000",Sample\n'
    )

    result = load_attendance_csv(path)

    assert result.loc[0, "crowd"] == 82000
    assert result.loc[0, "venue"] == "MCG"
    assert pd.api.types.is_datetime64_any_dtype(result["date"])


def test_load_attendance_csv_handles_invalid_crowd(tmp_path: Path) -> None:
    path = tmp_path / "attendance.csv"
    path.write_text(
        "year,date,home_team,away_team,venue,crowd\n"
        "2025,2025-03-14,Carlton,Collingwood,MCG,not-known\n"
    )

    result = load_attendance_csv(path)

    assert pd.isna(result.loc[0, "crowd"])


def test_load_attendance_csv_requires_crowd(tmp_path: Path) -> None:
    path = tmp_path / "attendance.csv"
    path.write_text("year,home_team,away_team\n2025,Carlton,Collingwood\n")

    with pytest.raises(AttendanceDataError):
        load_attendance_csv(path)


def test_parse_afl_tables_style_html() -> None:
    html = """
    <table>
      <tr><th>Round</th><th>Date</th><th>Home</th><th>Away</th><th>Venue</th><th>Crowd</th></tr>
      <tr><td>1</td><td>2025-03-14</td><td>Carlton</td><td>Collingwood</td><td>MCG</td><td>82000</td></tr>
    </table>
    """

    result = parse_afl_tables_crowds_html(html, 2025)

    assert len(result) == 1
    assert result.loc[0, "year"] == 2025
    assert result.loc[0, "crowd"] == 82000
    assert result.loc[0, "source"] == "AFL Tables public HTML"


def test_merge_attendance_with_games_matches_and_tolerates_unmatched() -> None:
    games = pd.DataFrame(
        [
            {
                "game_id": 1,
                "year": 2025,
                "date": "2025-03-14 19:40",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "M.C.G.",
            },
            {
                "game_id": 2,
                "year": 2025,
                "date": "2025-03-15",
                "home_team": "Sydney",
                "away_team": "Gold Coast",
                "venue": "SCG",
            },
        ]
    )
    attendance = pd.DataFrame(
        [
            {
                "year": 2025,
                "date": "2025-03-14",
                "home_team": "Carlton",
                "away_team": "Collingwood",
                "venue": "MCG",
                "crowd": 82000,
                "source": "Sample",
            }
        ]
    )

    result = merge_attendance_with_games(games, attendance)

    assert result.loc[0, "crowd"] == 82000
    assert result.loc[0, "attendance_match_confidence"] == "high"
    assert result.loc[1, "attendance_match_confidence"] == "unmatched"
