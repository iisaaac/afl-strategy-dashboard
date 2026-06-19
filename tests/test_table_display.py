"""Tests for curated dashboard table presentation helpers."""

from __future__ import annotations

import pandas as pd

from afl_strategy_dashboard.components.tables import (
    OVERVIEW_COMMERCIAL_TABLE,
    OVERVIEW_FAN_GROWTH_TABLE,
    OVERVIEW_FIXTURE_EQUITY_TABLE,
    OVERVIEW_TRAVEL_LOAD_TABLE,
    build_html_table,
    prepare_display_table,
    prettify_column_name,
    truncate_text,
)


def test_prettify_column_name_uses_readable_labels() -> None:
    assert prettify_column_name("fixture_equity_risk_score") == "Risk Score"
    assert (
        prettify_column_name("consecutive_interstate_away_games")
        == "Max Interstate Away Run"
    )
    assert prettify_column_name("custom_metric_name") == "Custom Metric Name"


def test_truncate_text_shortens_long_values_and_preserves_short_values() -> None:
    assert truncate_text("Short note", max_length=20) == "Short note"

    truncated = truncate_text("This note is far too long for a compact table", 24)

    assert truncated == "This note is far too..."
    assert len(truncated) <= 24


def test_prepare_display_table_selects_available_columns_only() -> None:
    df = pd.DataFrame(
        {
            "team": ["Fremantle"],
            "fixture_equity_risk_score": [18.5],
            "internal_field": ["hidden"],
        }
    )

    display = prepare_display_table(
        df,
        ["team", "fixture_equity_risk_score", "missing_column"],
        rename_map={"team": "Team", "fixture_equity_risk_score": "Risk Score"},
    )

    assert list(display.columns) == ["Team", "Risk Score"]
    assert "internal_field" not in display.columns


def test_prepare_display_table_applies_rename_map_and_truncates_notes() -> None:
    df = pd.DataFrame(
        {
            "team": ["West Coast"],
            "travel_load_notes": [
                "Multiple interstate away games and long-haul travel create a "
                "visible public-data review signal."
            ],
        }
    )

    display = prepare_display_table(
        df,
        ["team", "travel_load_notes"],
        rename_map={"team": "Team", "travel_load_notes": "Notes"},
        truncate_columns=["travel_load_notes"],
        max_text_length=45,
    )

    assert list(display.columns) == ["Team", "Notes"]
    assert len(display.loc[0, "Notes"]) <= 45
    assert display.loc[0, "Notes"].endswith("...")


def test_prepare_display_table_formats_boolean_and_percentage_values() -> None:
    df = pd.DataFrame(
        {
            "growth_market_flag": [True],
            "estimated_capacity_utilisation": [0.734],
        }
    )

    display = prepare_display_table(
        df,
        ["growth_market_flag", "estimated_capacity_utilisation"],
        rename_map={
            "growth_market_flag": "Growth Market",
            "estimated_capacity_utilisation": "Capacity Use",
        },
    )

    assert display.loc[0, "Growth Market"] == "Yes"
    assert display.loc[0, "Capacity Use"] == "73%"


def test_overview_presets_do_not_include_raw_note_columns() -> None:
    presets = [
        OVERVIEW_FIXTURE_EQUITY_TABLE,
        OVERVIEW_TRAVEL_LOAD_TABLE,
        OVERVIEW_COMMERCIAL_TABLE,
        OVERVIEW_FAN_GROWTH_TABLE,
    ]

    for preset in presets:
        assert "fixture_equity_notes" not in preset.columns
        assert "travel_load_notes" not in preset.columns
        assert "opportunity_notes" not in preset.columns


def test_html_table_renderer_escapes_cell_values() -> None:
    df = pd.DataFrame(
        {
            "team": ["<script>alert(1)</script>"],
            "fixture_equity_risk_score": [44.0],
        }
    )

    html = build_html_table(
        df,
        ["team", "fixture_equity_risk_score"],
        rename_map={"team": "Team"},
    )

    assert "&lt;script&gt;alert(1)&lt;/script&gt;" in html
    assert "<script>" not in html


def test_html_table_renderer_truncates_configured_columns() -> None:
    df = pd.DataFrame(
        {
            "team": ["Sydney"],
            "fixture_equity_notes": ["A very long operational note that should fit"],
        }
    )

    html = build_html_table(
        df,
        ["team", "fixture_equity_notes"],
        truncate_columns=["fixture_equity_notes"],
        max_text_length=20,
    )

    assert "A very long opera..." in html
    assert "A very long operational note" not in html


def test_html_table_renderer_handles_missing_columns_gracefully() -> None:
    df = pd.DataFrame({"team": ["Adelaide"]})

    html = build_html_table(df, ["missing_column"])

    assert "No records are available" in html
    assert "executive-table-wrap" in html
