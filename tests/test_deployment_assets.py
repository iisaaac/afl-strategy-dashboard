"""Tests for deployment readiness assets."""

from __future__ import annotations

from pathlib import Path


def test_deployment_files_exist_and_are_non_empty() -> None:
    required_files = [
        Path("requirements.txt"),
        Path("docs/deployment.md"),
        Path(".github/workflows/tests.yml"),
    ]

    for path in required_files:
        assert path.exists(), f"Missing deployment file: {path}"
        assert path.stat().st_size > 0, f"Empty deployment file: {path}"


def test_readme_does_not_include_local_absolute_paths() -> None:
    readme = Path("README.md").read_text(encoding="utf-8")
    local_path_prefix = "/" + "Users" + "/" + "isaacdibona"

    assert local_path_prefix not in readme


def test_deployed_export_page_has_no_development_only_controls() -> None:
    export_page = Path(
        "src/afl_strategy_dashboard/pages/export_brief.py"
    ).read_text(encoding="utf-8")

    assert "Local development only" not in export_page
    assert "outputs/reports" not in export_page


def test_deployment_portfolio_assets_exist() -> None:
    required_assets = [
        Path("docs/assets/screenshots/01_overview.png"),
        Path("docs/assets/screenshots/02_fixture_equity.png"),
        Path("docs/assets/screenshots/03_travel_load.png"),
        Path("docs/assets/screenshots/04_fan_growth_commercial.png"),
        Path("docs/assets/screenshots/05_export_brief.png"),
        Path("docs/assets/screenshots/06_methodology.png"),
        Path("docs/assets/reports/sample_strategy_brief.html"),
        Path("docs/assets/reports/sample_strategy_brief.md"),
    ]

    for path in required_assets:
        assert path.exists(), f"Missing deployment asset: {path}"
        assert path.stat().st_size > 0, f"Empty deployment asset: {path}"
