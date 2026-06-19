"""Generate a portfolio sample executive brief from synthetic demo data."""

from __future__ import annotations

import sys
from datetime import datetime
from pathlib import Path

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1] / "src"))

from afl_strategy_dashboard.data.attendance import load_attendance_csv
from afl_strategy_dashboard.data.dashboard_state import (
    DashboardControls,
    build_dashboard_state,
    sample_data,
)
from afl_strategy_dashboard.reporting.executive_brief import (
    build_executive_brief_context,
    render_executive_brief_html,
    render_executive_brief_markdown,
)

DEFAULT_REPORT_DIR = Path("docs/assets/reports")
SAMPLE_HTML_NAME = "sample_strategy_brief.html"
SAMPLE_MARKDOWN_NAME = "sample_strategy_brief.md"


def generate_sample_strategy_brief(
    output_dir: str | Path = DEFAULT_REPORT_DIR,
) -> dict[str, Path]:
    """Generate fixed-name HTML and Markdown sample reports from demo data."""
    games, ladder = sample_data()
    attendance = load_attendance_csv("data/raw/sample_attendance.csv")
    controls = DashboardControls(
        year=2025,
        refresh=False,
        completed_only=True,
        season_phase_label="Home-and-away season",
        selected_team="All teams",
        use_sample=True,
        include_attendance=True,
        crowd_only=False,
    )
    state = build_dashboard_state(
        controls=controls,
        raw_games=games,
        ladder=ladder,
        data_note=(
            "Using synthetic/demo sample fixture data for portfolio demonstration."
        ),
        attendance=attendance,
        attendance_note="Using synthetic sample attendance CSV for demonstration.",
    )
    context = build_executive_brief_context(
        state,
        generated_at=datetime.now().astimezone(),
    )
    _label_context_as_sample(context)
    html = render_executive_brief_html(context)
    markdown = render_executive_brief_markdown(context)

    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    html_path = output_path / SAMPLE_HTML_NAME
    markdown_path = output_path / SAMPLE_MARKDOWN_NAME
    html_path.write_text(html, encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return {"html": html_path, "markdown": markdown_path}


def _label_context_as_sample(context: dict) -> None:
    context["data_mode"] = "Synthetic/demo sample data"
    existing_sources = [
        source
        for source in context["data_sources"]
        if "synthetic sample attendance" not in source.lower()
    ]
    context["data_sources"] = [
        (
            "Generated from synthetic/demo sample dashboard data for portfolio "
            "demonstration."
        ),
        (
            "Synthetic sample attendance CSV is included only to demonstrate "
            "attendance-context workflow."
        ),
        *existing_sources,
    ]
    context["limitations"] = [
        (
            "This sample report does not contain official AFL attendance, ticketing, "
            "commercial or broadcast data."
        ),
        *context["limitations"],
    ]


def main() -> None:
    saved = generate_sample_strategy_brief()
    print(f"HTML sample brief: {saved['html']}")
    print(f"Markdown sample brief: {saved['markdown']}")


if __name__ == "__main__":
    main()
