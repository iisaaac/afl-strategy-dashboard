"""Lightweight deployment smoke checks for the dashboard."""

from __future__ import annotations

import sys
from pathlib import Path
from types import SimpleNamespace

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
SRC_ROOT = PROJECT_ROOT / "src"

if str(SRC_ROOT) not in sys.path:
    sys.path.insert(0, str(SRC_ROOT))

REQUIRED_PATHS = [
    PROJECT_ROOT / "docs/assets/reports/sample_strategy_brief.html",
    PROJECT_ROOT / "docs/assets/reports/sample_strategy_brief.md",
    PROJECT_ROOT / "docs/assets/screenshots/01_overview.png",
    PROJECT_ROOT / "docs/assets/screenshots/02_fixture_equity.png",
    PROJECT_ROOT / "docs/assets/screenshots/03_travel_load.png",
    PROJECT_ROOT / "docs/assets/screenshots/04_fan_growth_commercial.png",
    PROJECT_ROOT / "docs/assets/screenshots/05_export_brief.png",
    PROJECT_ROOT / "docs/assets/screenshots/06_methodology.png",
    PROJECT_ROOT / "data/raw/sample_attendance.csv",
]


def main() -> int:
    """Run import, asset and reporting checks."""
    _check_imports()
    _check_required_paths()
    _check_report_rendering()
    print("Deployment smoke check passed.")
    return 0


def _check_imports() -> None:
    import afl_strategy_dashboard  # noqa: F401
    import afl_strategy_dashboard.app  # noqa: F401


def _check_required_paths() -> None:
    missing = [
        path.relative_to(PROJECT_ROOT)
        for path in REQUIRED_PATHS
        if not path.exists() or path.stat().st_size == 0
    ]
    if missing:
        formatted = ", ".join(str(path) for path in missing)
        raise FileNotFoundError(f"Missing required deployment assets: {formatted}")


def _check_report_rendering() -> None:
    from afl_strategy_dashboard.reporting.executive_brief import (
        build_executive_brief_context,
        render_executive_brief_html,
        render_executive_brief_markdown,
    )

    state = SimpleNamespace(
        controls=SimpleNamespace(
            year=2025,
            season_phase_label="Home-and-away season",
            selected_team="All teams",
            use_sample=True,
            include_attendance=False,
        ),
        data_note="Using synthetic sample data for deployment smoke check.",
        attendance_note="Attendance context is not enabled.",
        games=pd.DataFrame({"game_id": [1]}),
        fixture_equity=pd.DataFrame(),
        travel_load=pd.DataFrame(),
        opportunities=pd.DataFrame(),
        competitive_summary=pd.DataFrame(),
        recommendations=[
            "Sample data appears suitable for confirming report rendering."
        ],
    )
    context = build_executive_brief_context(state)
    html = render_executive_brief_html(context)
    markdown = render_executive_brief_markdown(context)
    if "Executive Snapshot" not in html or "## Executive Snapshot" not in markdown:
        raise RuntimeError("Synthetic executive brief did not render as expected.")


if __name__ == "__main__":
    raise SystemExit(main())
