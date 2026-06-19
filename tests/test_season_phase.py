import pandas as pd

from afl_strategy_dashboard.data.squiggle_client import classify_season_phase
from afl_strategy_dashboard.features.season_phase import filter_by_season_phase


def test_numeric_home_and_away_rounds() -> None:
    assert classify_season_phase(1, "Round 1") == "home_and_away"
    assert classify_season_phase(0, "Opening Round") == "home_and_away"
    assert classify_season_phase(23, None) == "home_and_away"


def test_finals_round_names() -> None:
    assert classify_season_phase(24, "Elimination Final") == "finals"
    assert classify_season_phase(25, "Qualifying Final") == "finals"
    assert classify_season_phase(26, "Semi Final") == "finals"
    assert classify_season_phase(27, "Preliminary Final") == "finals"
    assert classify_season_phase(28, "Grand Final") == "finals"


def test_abbreviated_finals_labels() -> None:
    assert classify_season_phase("EF", None) == "finals"
    assert classify_season_phase("QF", None) == "finals"
    assert classify_season_phase("SF", None) == "finals"
    assert classify_season_phase("PF", None) == "finals"
    assert classify_season_phase("GF", None) == "finals"


def test_unknown_round_labels() -> None:
    assert classify_season_phase(None, None) == "unknown"
    assert classify_season_phase("TBC", "To be confirmed") == "unknown"
    assert classify_season_phase(99, None) == "unknown"


def test_filter_home_and_away_only() -> None:
    games = _phase_games()

    result = filter_by_season_phase(games, "home_and_away")

    assert result["game_id"].tolist() == [1]


def test_filter_finals_only() -> None:
    games = _phase_games()

    result = filter_by_season_phase(games, "finals")

    assert result["game_id"].tolist() == [2]


def test_filter_full_season() -> None:
    games = _phase_games()

    result = filter_by_season_phase(games, "full_season")

    assert result["game_id"].tolist() == [1, 2, 3]


def test_filter_missing_season_phase_column_does_not_crash() -> None:
    games = pd.DataFrame([{"game_id": 1}, {"game_id": 2}])

    result = filter_by_season_phase(games, "home_and_away")

    assert result.equals(games)


def test_filter_unknown_only() -> None:
    games = _phase_games()

    result = filter_by_season_phase(games, "unknown")

    assert result["game_id"].tolist() == [3]


def _phase_games() -> pd.DataFrame:
    return pd.DataFrame(
        [
            {"game_id": 1, "season_phase": "home_and_away"},
            {"game_id": 2, "season_phase": "finals"},
            {"game_id": 3, "season_phase": "unknown"},
        ]
    )
