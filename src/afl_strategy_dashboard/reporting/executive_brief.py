"""Executive strategy brief generation."""

from __future__ import annotations

from datetime import datetime
from html import escape
from pathlib import Path
from typing import Any

import pandas as pd

from afl_strategy_dashboard.data.dashboard_state import (
    average_margin_label,
    top_fixture_label,
    top_team_label,
)
from afl_strategy_dashboard.reporting.templates import (
    BRIEF_SUBTITLE,
    BRIEF_TITLE,
    HTML_REPORT_CSS,
    METHODOLOGY_CAVEAT,
)

PROJECT_TITLE = "AFL Strategy & Fan Growth Analytics Dashboard"
DEFAULT_OUTPUT_DIR = Path("outputs/reports")


def build_executive_brief_context(
    state: Any,
    generated_at: datetime | None = None,
) -> dict[str, Any]:
    """Build a report context from a DashboardState-like object."""
    controls = getattr(state, "controls", None)
    generated = generated_at or datetime.now().astimezone()
    fixture_equity = _dataframe_from_state(state, "fixture_equity")
    travel_load = _dataframe_from_state(state, "travel_load")
    opportunities = _dataframe_from_state(state, "opportunities")
    competitive_summary = _dataframe_from_state(state, "competitive_summary")
    games = _dataframe_from_state(state, "games")
    recommendations = list(getattr(state, "recommendations", []) or [])[:5]
    attendance_note = str(getattr(state, "attendance_note", "") or "")

    commercial_opportunities = _sorted_table(
        opportunities,
        "commercial_opportunity_score",
        [
            ("Fixture", _fixture_value),
            ("Venue", "venue"),
            ("Score", "commercial_opportunity_score"),
            ("Category", "opportunity_category"),
        ],
    )
    fan_growth_opportunities = _sorted_table(
        opportunities,
        "fan_growth_opportunity_score",
        [
            ("Fixture", _fixture_value),
            ("Venue", "venue"),
            ("Score", "fan_growth_opportunity_score"),
            ("Category", "opportunity_category"),
        ],
    )

    context = {
        "project_title": PROJECT_TITLE,
        "brief_title": BRIEF_TITLE,
        "brief_subtitle": BRIEF_SUBTITLE,
        "generated_at": generated.strftime("%Y-%m-%d %H:%M %Z"),
        "generated_slug": generated.strftime("%Y%m%d_%H%M%S"),
        "season": _control_value(controls, "year", "n/a"),
        "season_phase": _control_value(controls, "season_phase_label", "n/a"),
        "team_filter": _control_value(controls, "selected_team", "All teams"),
        "data_mode": _data_mode(state),
        "games_analysed": f"{len(games):,}",
        "average_margin": average_margin_label(competitive_summary),
        "highest_fixture_equity_team": top_team_label(
            fixture_equity,
            "fixture_equity_risk_score",
        ),
        "highest_travel_load_team": top_team_label(travel_load, "travel_load_score"),
        "highest_commercial_fixture": top_fixture_label(
            opportunities,
            "commercial_opportunity_score",
        ),
        "highest_fan_growth_fixture": top_fixture_label(
            opportunities,
            "fan_growth_opportunity_score",
        ),
        "top_fixture_equity_risks": _sorted_table(
            fixture_equity,
            "fixture_equity_risk_score",
            [
                ("Club", "team"),
                ("Risk score", "fixture_equity_risk_score"),
                ("Short breaks", "short_break_games"),
                ("Home-away diff", "home_away_differential"),
            ],
        ),
        "top_travel_loads": _sorted_table(
            travel_load,
            "travel_load_score",
            [
                ("Club", "team"),
                ("Travel score", "travel_load_score"),
                ("Interstate away", "interstate_away_games"),
                ("Est. km", "estimated_travel_km"),
            ],
        ),
        "top_commercial_opportunities": commercial_opportunities,
        "top_fan_growth_opportunities": fan_growth_opportunities,
        "competitive_balance_summary": _competitive_summary(competitive_summary),
        "recommendations": recommendations
        or [
            "Recommendations are limited because no analytical rows are available "
            "for the selected filters."
        ],
        "methodology_caveats": METHODOLOGY_CAVEAT,
        "data_sources": _data_sources(state, attendance_note),
        "limitations": [
            "Scores are transparent heuristics for review-priority ranking.",
            "Travel distances use approximate public team and venue geography.",
            "Venue capacities are maintained assumptions and may vary by event.",
            "Internal AFL attendance, ticketing, broadcast, commercial, digital and "
            "player-welfare data would be needed for decision-grade modelling.",
        ],
        "pdf_available": False,
    }
    return context


def render_executive_brief_html(context: dict[str, Any]) -> str:
    """Render a standalone HTML executive brief."""
    snapshot = [
        ("Games analysed", context["games_analysed"]),
        ("Average margin", context["average_margin"]),
        ("Highest fixture-equity risk club", context["highest_fixture_equity_team"]),
        ("Highest travel-load club", context["highest_travel_load_team"]),
        (
            "Highest commercial opportunity fixture",
            context["highest_commercial_fixture"],
        ),
        (
            "Highest fan-growth opportunity fixture",
            context["highest_fan_growth_fixture"],
        ),
    ]
    fixture_equity_table = _table_panel_html(
        "Fixture equity risk",
        context["top_fixture_equity_risks"],
    )
    travel_load_table = _table_panel_html("Travel load", context["top_travel_loads"])
    commercial_table = _table_panel_html(
        "Commercial opportunity",
        context["top_commercial_opportunities"],
    )
    fan_growth_table = _table_panel_html(
        "Fan-growth opportunity",
        context["top_fan_growth_opportunities"],
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{escape(str(context["brief_title"]))}</title>
<style>{HTML_REPORT_CSS}</style>
</head>
<body>
<main class="brief">
    <header class="header">
        <div class="eyebrow">Executive strategy brief</div>
        <h1>{escape(str(context["brief_title"]))}</h1>
        <p class="subtitle">{escape(str(context["brief_subtitle"]))}</p>
        {_metadata_html(context)}
    </header>
    <section>
        <h2>Executive Snapshot</h2>
        <div class="metrics">{_metric_cards_html(snapshot)}</div>
    </section>
    <section class="section">
        <h2>Key Findings</h2>
        {_list_html(context["recommendations"])}
    </section>
    <section>
        <h2>Priority Tables</h2>
        <div class="table-grid">
            {fixture_equity_table}
            {travel_load_table}
            {commercial_table}
            {fan_growth_table}
        </div>
    </section>
    <section class="section">
        <h2>Competitive Balance Summary</h2>
        {_key_value_table_html(context["competitive_balance_summary"])}
    </section>
    <section class="caveat">
        <strong>Methodology Caveat.</strong>
        {escape(str(context["methodology_caveats"]))}
    </section>
    <section class="sources">
        <h2>Data Sources</h2>
        {_list_html(context["data_sources"])}
        <h2>Limitations</h2>
        {_list_html(context["limitations"])}
    </section>
</main>
</body>
</html>
"""


def render_executive_brief_markdown(context: dict[str, Any]) -> str:
    """Render a recruiter-readable Markdown executive brief."""
    snapshot = [
        ("Games analysed", context["games_analysed"]),
        ("Average margin", context["average_margin"]),
        ("Highest fixture-equity risk club", context["highest_fixture_equity_team"]),
        ("Highest travel-load club", context["highest_travel_load_team"]),
        (
            "Highest commercial opportunity fixture",
            context["highest_commercial_fixture"],
        ),
        (
            "Highest fan-growth opportunity fixture",
            context["highest_fan_growth_fixture"],
        ),
    ]
    sections = [
        f"# {context['brief_title']}",
        str(context["brief_subtitle"]),
        "",
        "## Brief Header",
        f"- Project: {context['project_title']}",
        f"- Season: {context['season']}",
        f"- Season phase: {context['season_phase']}",
        f"- Team filter: {context['team_filter']}",
        f"- Generated: {context['generated_at']}",
        f"- Data mode: {context['data_mode']}",
        "",
        "## Executive Snapshot",
        _markdown_table(["Metric", "Value"], snapshot),
        "",
        "## Key Findings",
        _markdown_list(context["recommendations"]),
        "",
        "## Priority Tables",
        "### Fixture Equity Risk",
        _markdown_records_table(context["top_fixture_equity_risks"]),
        "",
        "### Travel Load",
        _markdown_records_table(context["top_travel_loads"]),
        "",
        "### Commercial Opportunity",
        _markdown_records_table(context["top_commercial_opportunities"]),
        "",
        "### Fan-Growth Opportunity",
        _markdown_records_table(context["top_fan_growth_opportunities"]),
        "",
        "## Competitive Balance Summary",
        _markdown_table(
            ["Metric", "Value"],
            list(context["competitive_balance_summary"].items()),
        ),
        "",
        "## Methodology Caveat",
        context["methodology_caveats"],
        "",
        "## Data Sources",
        _markdown_list(context["data_sources"]),
        "",
        "## Limitations",
        _markdown_list(context["limitations"]),
    ]
    return "\n".join(sections).strip() + "\n"


def save_executive_brief(
    html: str,
    markdown: str,
    output_dir: str | Path = DEFAULT_OUTPUT_DIR,
    filename_prefix: str = "afl_strategy_brief",
) -> dict[str, Path]:
    """Save HTML and Markdown brief files under the given output directory."""
    output_path = Path(output_dir)
    output_path.mkdir(parents=True, exist_ok=True)
    timestamp = datetime.now().astimezone().strftime("%Y%m%d_%H%M%S")
    html_path = output_path / f"{filename_prefix}_{timestamp}.html"
    markdown_path = output_path / f"{filename_prefix}_{timestamp}.md"
    html_path.write_text(html, encoding="utf-8")
    markdown_path.write_text(markdown, encoding="utf-8")
    return {
        "html": html_path,
        "markdown": markdown_path,
    }


def _dataframe_from_state(state: Any, name: str) -> pd.DataFrame:
    value = getattr(state, name, pd.DataFrame())
    return value if isinstance(value, pd.DataFrame) else pd.DataFrame()


def _control_value(controls: Any, name: str, default: Any) -> Any:
    return getattr(controls, name, default) if controls is not None else default


def _data_mode(state: Any) -> str:
    controls = getattr(state, "controls", None)
    if bool(_control_value(controls, "use_sample", False)):
        return "Synthetic sample data"
    data_note = str(getattr(state, "data_note", "") or "")
    if "sample" in data_note.lower() or "synthetic" in data_note.lower():
        return "Synthetic sample data"
    return "Live public data with local cache"


def _data_sources(state: Any, attendance_note: str) -> list[str]:
    controls = getattr(state, "controls", None)
    sources = [
        "Squiggle API for public fixture, result and ladder context.",
        "Maintained public venue-capacity and market-context assumptions.",
    ]
    if bool(_control_value(controls, "include_attendance", False)):
        if (
            "sample" in attendance_note.lower()
            or "synthetic" in attendance_note.lower()
        ):
            sources.append("Synthetic sample attendance CSV for demonstration.")
        else:
            sources.append("Optional local attendance CSV supplied through the app.")
    else:
        sources.append("No attendance CSV is active for this export.")
    return sources


def _competitive_summary(summary: pd.DataFrame) -> dict[str, str]:
    if summary.empty:
        return {
            "Games": "0",
            "Average margin": "n/a",
            "Median margin": "n/a",
            "Close-game rate": "n/a",
            "Blowout rate": "n/a",
        }
    row = summary.iloc[0]
    return {
        "Games": _format_value(row.get("games")),
        "Average margin": _format_value(row.get("average_margin")),
        "Median margin": _format_value(row.get("median_margin")),
        "Close-game rate": _format_percent(row.get("close_game_rate")),
        "Blowout rate": _format_percent(row.get("blowout_game_rate")),
    }


def _sorted_table(
    df: pd.DataFrame,
    sort_column: str,
    columns: list[tuple[str, str | Any]],
    limit: int = 5,
) -> list[dict[str, str]]:
    if df.empty:
        return []
    working = df.copy()
    if sort_column in working.columns:
        working = working.sort_values(sort_column, ascending=False)
    records: list[dict[str, str]] = []
    for _, row in working.head(limit).iterrows():
        record = {}
        for label, source in columns:
            value = source(row) if callable(source) else row.get(source)
            record[label] = _format_value(value)
        records.append(record)
    return records


def _fixture_value(row: pd.Series) -> str:
    return f"{row.get('home_team', 'n/a')} v {row.get('away_team', 'n/a')}"


def _format_value(value: Any) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if isinstance(value, int):
        return f"{value:,}"
    if isinstance(value, float):
        if value.is_integer():
            return f"{value:,.0f}"
        return f"{value:,.1f}"
    return str(value)


def _format_percent(value: Any) -> str:
    if value is None or pd.isna(value):
        return "n/a"
    return f"{float(value):.0%}"


def _metadata_html(context: dict[str, Any]) -> str:
    items = [
        ("Project", context["project_title"]),
        ("Season", context["season"]),
        ("Phase", context["season_phase"]),
        ("Team filter", context["team_filter"]),
        ("Generated", context["generated_at"]),
        ("Data mode", context["data_mode"]),
    ]
    return (
        '<div class="meta">'
        + "".join(
            f'<div class="meta-item"><span class="label">{escape(label)}</span>'
            f'<span class="value">{escape(str(value))}</span></div>'
            for label, value in items
        )
        + "</div>"
    )


def _metric_cards_html(items: list[tuple[str, Any]]) -> str:
    return "".join(
        f'<div class="metric-card"><span class="label">{escape(label)}</span>'
        f'<span class="value">{escape(str(value))}</span></div>'
        for label, value in items
    )


def _list_html(items: list[str]) -> str:
    list_items = "".join(f"<li>{escape(str(item))}</li>" for item in items)
    return f"<ol>{list_items}</ol>"


def _table_panel_html(title: str, records: list[dict[str, str]]) -> str:
    table = _records_table_html(records)
    return f'<div class="section"><h2>{escape(title)}</h2>{table}</div>'


def _records_table_html(records: list[dict[str, str]]) -> str:
    if not records:
        return "<p>No rows available for the current filters.</p>"
    headers = list(records[0])
    head = "".join(f"<th>{escape(header)}</th>" for header in headers)
    rows = "".join(
        "<tr>"
        + "".join(
            f"<td>{escape(str(record.get(header, '')))}</td>" for header in headers
        )
        + "</tr>"
        for record in records
    )
    return f"<table><thead><tr>{head}</tr></thead><tbody>{rows}</tbody></table>"


def _key_value_table_html(values: dict[str, str]) -> str:
    records = [{"Metric": key, "Value": value} for key, value in values.items()]
    return _records_table_html(records)


def _markdown_list(items: list[str]) -> str:
    return "\n".join(f"- {item}" for item in items)


def _markdown_table(headers: list[str], rows: list[tuple[Any, ...]]) -> str:
    escaped_headers = [_markdown_escape(str(header)) for header in headers]
    lines = [
        "| " + " | ".join(escaped_headers) + " |",
        "| " + " | ".join("---" for _ in headers) + " |",
    ]
    for row in rows:
        lines.append(
            "| " + " | ".join(_markdown_escape(str(value)) for value in row) + " |"
        )
    return "\n".join(lines)


def _markdown_records_table(records: list[dict[str, str]]) -> str:
    if not records:
        return "No rows available for the current filters."
    headers = list(records[0])
    rows = [tuple(record.get(header, "") for header in headers) for record in records]
    return _markdown_table(headers, rows)


def _markdown_escape(value: str) -> str:
    return value.replace("|", "\\|")
