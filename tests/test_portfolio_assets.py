"""Tests for portfolio documentation assets."""

from __future__ import annotations

from pathlib import Path

EXPECTED_ASSETS = [
    Path("docs/assets/screenshots/01_overview.png"),
    Path("docs/assets/screenshots/02_fixture_equity.png"),
    Path("docs/assets/screenshots/03_travel_load.png"),
    Path("docs/assets/screenshots/04_fan_growth_commercial.png"),
    Path("docs/assets/screenshots/05_export_brief.png"),
    Path("docs/assets/screenshots/06_methodology.png"),
    Path("docs/assets/reports/sample_strategy_brief.html"),
    Path("docs/assets/reports/sample_strategy_brief.md"),
    Path("docs/assets/diagrams/architecture.md"),
    Path("docs/project_case_study.md"),
]


def test_portfolio_assets_exist_and_are_non_empty() -> None:
    for asset_path in EXPECTED_ASSETS:
        assert asset_path.exists(), f"Missing portfolio asset: {asset_path}"
        assert asset_path.stat().st_size > 0, f"Empty portfolio asset: {asset_path}"
