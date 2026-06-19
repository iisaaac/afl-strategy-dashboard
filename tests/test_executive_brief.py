"""Tests for executive brief export generation."""

from __future__ import annotations

from datetime import datetime, timezone
from types import SimpleNamespace

import pandas as pd

from afl_strategy_dashboard.reporting.executive_brief import (
    build_executive_brief_context,
    render_executive_brief_html,
    render_executive_brief_markdown,
    save_executive_brief,
)


def test_context_builder_handles_populated_state_like_object() -> None:
    state = _populated_state()

    context = build_executive_brief_context(
        state,
        generated_at=datetime(2026, 6, 14, 12, 0, tzinfo=timezone.utc),
    )

    assert context["season"] == 2025
    assert context["games_analysed"] == "2"
    assert context["average_margin"] == "18.5"
    assert context["highest_fixture_equity_team"] == "Essendon"
    assert context["highest_travel_load_team"] == "West Coast"
    assert context["highest_commercial_fixture"] == "Carlton v Collingwood"
    assert len(context["top_fixture_equity_risks"]) == 2
    assert context["pdf_available"] is False


def test_context_builder_handles_empty_tables() -> None:
    controls = SimpleNamespace(
        year=2025,
        season_phase_label="Finals only",
        selected_team="All teams",
        use_sample=True,
        include_attendance=False,
    )
    state = SimpleNamespace(
        controls=controls,
        data_note="Using synthetic sample data for offline demonstration.",
        attendance_note="Attendance context is not enabled.",
        games=pd.DataFrame(),
        fixture_equity=pd.DataFrame(),
        travel_load=pd.DataFrame(),
        opportunities=pd.DataFrame(),
        competitive_summary=pd.DataFrame(),
        recommendations=[],
    )

    context = build_executive_brief_context(state)

    assert context["data_mode"] == "Synthetic sample data"
    assert context["games_analysed"] == "0"
    assert context["average_margin"] == "n/a"
    assert context["top_commercial_opportunities"] == []
    assert "limited" in context["recommendations"][0]


def test_html_renderer_includes_key_sections() -> None:
    context = build_executive_brief_context(_populated_state())

    html = render_executive_brief_html(context)

    assert "AFL Strategy &amp; Fan Growth Analytics Brief" in html
    assert "Executive Snapshot" in html
    assert "Key Findings" in html
    assert "Priority Tables" in html
    assert "Methodology Caveat" in html
    assert "Squiggle API" in html


def test_markdown_renderer_includes_key_sections() -> None:
    context = build_executive_brief_context(_populated_state())

    markdown = render_executive_brief_markdown(context)

    assert "# AFL Strategy & Fan Growth Analytics Brief" in markdown
    assert "## Executive Snapshot" in markdown
    assert "## Key Findings" in markdown
    assert "### Fixture Equity Risk" in markdown
    assert "## Data Sources" in markdown


def test_renderers_preserve_cautious_wording() -> None:
    context = build_executive_brief_context(_populated_state())
    combined = (
        render_executive_brief_html(context) + render_executive_brief_markdown(context)
    ).lower()

    assert "appears" in combined
    assert "may warrant" in combined
    for prohibited in [
        "proves",
        "guarantees",
        "must",
        "definitely",
        "betting",
        "gambling",
        "fantasy",
        "tipping",
    ]:
        assert prohibited not in combined


def test_save_executive_brief_writes_files(tmp_path) -> None:
    saved = save_executive_brief(
        "<html><body>Brief</body></html>",
        "# Brief\n",
        output_dir=tmp_path,
        filename_prefix="test_brief",
    )

    assert saved["html"].parent == tmp_path
    assert saved["markdown"].parent == tmp_path
    assert saved["html"].read_text(encoding="utf-8").startswith("<html>")
    assert saved["markdown"].read_text(encoding="utf-8").startswith("# Brief")


def test_report_does_not_claim_private_or_protected_data() -> None:
    context = build_executive_brief_context(_populated_state())

    markdown = render_executive_brief_markdown(context).lower()

    assert "private afl data" not in markdown
    assert "protected afl data" not in markdown
    assert "champion data" not in markdown


def _populated_state() -> SimpleNamespace:
    controls = SimpleNamespace(
        year=2025,
        season_phase_label="Home-and-away season",
        selected_team="All teams",
        use_sample=False,
        include_attendance=True,
    )
    return SimpleNamespace(
        controls=controls,
        data_note="Using public Squiggle API data for 2025, with local cache enabled.",
        attendance_note="Using uploaded attendance CSV data.",
        games=pd.DataFrame({"game_id": [1, 2]}),
        fixture_equity=pd.DataFrame(
            [
                {
                    "team": "Essendon",
                    "fixture_equity_risk_score": 22.4,
                    "short_break_games": 5,
                    "home_away_differential": -2,
                },
                {
                    "team": "Melbourne",
                    "fixture_equity_risk_score": 17.2,
                    "short_break_games": 4,
                    "home_away_differential": 1,
                },
            ]
        ),
        travel_load=pd.DataFrame(
            [
                {
                    "team": "West Coast",
                    "travel_load_score": 31.1,
                    "interstate_away_games": 9,
                    "estimated_travel_km": 42000.5,
                },
                {
                    "team": "Fremantle",
                    "travel_load_score": 28.5,
                    "interstate_away_games": 8,
                    "estimated_travel_km": 39000.0,
                },
            ]
        ),
        opportunities=pd.DataFrame(
            [
                {
                    "home_team": "Carlton",
                    "away_team": "Collingwood",
                    "venue": "MCG",
                    "commercial_opportunity_score": 72.0,
                    "fan_growth_opportunity_score": 42.0,
                    "opportunity_category": "Marquee commercial fixture",
                },
                {
                    "home_team": "Brisbane",
                    "away_team": "Gold Coast",
                    "venue": "Gabba",
                    "commercial_opportunity_score": 51.0,
                    "fan_growth_opportunity_score": 58.5,
                    "opportunity_category": "Growth market opportunity",
                },
            ]
        ),
        competitive_summary=pd.DataFrame(
            [
                {
                    "games": 2,
                    "average_margin": 18.5,
                    "median_margin": 18.5,
                    "close_game_rate": 0.5,
                    "blowout_game_rate": 0.0,
                }
            ]
        ),
        recommendations=[
            "Fixture equity risk appears concentrated among Essendon and Melbourne. "
            "This may warrant review alongside commercial and stadium constraints.",
            "Travel load appears highest for West Coast and Fremantle, suggesting "
            "further internal review could be explored.",
        ],
    )
