"""Table display helpers."""

from __future__ import annotations

from dataclasses import dataclass
from html import escape

import pandas as pd
import streamlit as st


@dataclass(frozen=True)
class TablePreset:
    """Reusable display contract for a dashboard table."""

    columns: list[str]
    rename_map: dict[str, str]
    truncate_columns: list[str] | None = None


FIXTURE_EQUITY_RENAME_MAP = {
    "team": "Team",
    "fixture_equity_risk_score": "Risk Score",
    "games_played": "Games",
    "home_games": "Home",
    "away_games": "Away",
    "home_away_differential": "Home-Away Diff.",
    "short_break_games": "Short Breaks",
    "five_day_breaks": "5-Day Breaks",
    "six_day_breaks": "6-Day Breaks",
    "consecutive_away_games": "Max Away Run",
    "consecutive_interstate_away_games": "Max Interstate Away Run",
    "fixture_equity_notes": "Notes",
}

TRAVEL_LOAD_RENAME_MAP = {
    "team": "Team",
    "travel_load_score": "Travel Score",
    "interstate_away_games": "Interstate Away",
    "interstate_home_games": "Interstate Home",
    "neutral_state_games": "Neutral State Games",
    "estimated_travel_km": "Estimated Travel Km",
    "long_haul_trips": "Long-Haul Trips",
    "short_break_after_interstate_trip": "Short Break After Travel",
    "travel_load_notes": "Notes",
}

COMMERCIAL_RENAME_MAP = {
    "home_team": "Home",
    "away_team": "Away",
    "venue": "Venue",
    "broadcast_window": "Window",
    "commercial_opportunity_score": "Commercial Score",
    "fixture_attractiveness_score": "Attractiveness",
    "estimated_capacity_utilisation": "Capacity Use",
    "opportunity_category": "Category",
    "opportunity_notes": "Notes",
}

FAN_GROWTH_RENAME_MAP = {
    "home_team": "Home",
    "away_team": "Away",
    "venue": "Venue",
    "market_type": "Market",
    "fan_growth_opportunity_score": "Fan Growth Score",
    "growth_market_flag": "Growth Market",
    "regional_or_special_event_flag": "Regional/Special",
    "opportunity_category": "Category",
    "opportunity_notes": "Notes",
}

COMPACT_OPPORTUNITY_RENAME_MAP = {
    "fixture": "Fixture",
    "venue": "Venue",
    "commercial_opportunity_score": "Commercial Score",
    "fan_growth_opportunity_score": "Fan Growth Score",
    "short_category": "Category",
}

COMPETITIVE_BALANCE_RENAME_MAP = {
    "games": "Games",
    "average_margin": "Average Margin",
    "median_margin": "Median Margin",
    "close_games": "Close Games",
    "close_game_rate": "Close-Game Rate",
    "blowout_games": "Blowout Games",
    "blowout_game_rate": "Blowout Rate",
}

TEAM_TRAVEL_GAME_RENAME_MAP = {
    "team": "Team",
    "opponent": "Opponent",
    "date": "Date",
    "venue": "Venue",
    "venue_state": "Venue State",
    "team_state": "Team State",
    "is_home": "Home",
    "is_interstate_away": "Interstate Away",
    "is_interstate_travel": "Interstate Travel",
    "estimated_return_travel_km": "Estimated Return Km",
    "days_since_previous_game": "Days Since Previous Game",
    "short_break_after_interstate_trip": "Short Break After Travel",
}

FIXTURE_EQUITY_TABLE = TablePreset(
    columns=[
        "team",
        "fixture_equity_risk_score",
        "games_played",
        "home_games",
        "away_games",
        "home_away_differential",
        "short_break_games",
        "consecutive_interstate_away_games",
    ],
    rename_map=FIXTURE_EQUITY_RENAME_MAP,
)

TRAVEL_LOAD_TABLE = TablePreset(
    columns=[
        "team",
        "travel_load_score",
        "interstate_away_games",
        "estimated_travel_km",
        "long_haul_trips",
        "short_break_after_interstate_trip",
    ],
    rename_map=TRAVEL_LOAD_RENAME_MAP,
)

COMMERCIAL_OPPORTUNITY_TABLE = TablePreset(
    columns=[
        "fixture",
        "venue",
        "broadcast_window",
        "commercial_opportunity_score",
        "fixture_attractiveness_score",
        "short_category",
    ],
    rename_map={**COMMERCIAL_RENAME_MAP, **COMPACT_OPPORTUNITY_RENAME_MAP},
)

FAN_GROWTH_TABLE = TablePreset(
    columns=[
        "fixture",
        "venue",
        "market_type",
        "fan_growth_opportunity_score",
        "short_category",
    ],
    rename_map={**FAN_GROWTH_RENAME_MAP, **COMPACT_OPPORTUNITY_RENAME_MAP},
)

OVERVIEW_FIXTURE_EQUITY_TABLE = TablePreset(
    columns=[
        "team",
        "fixture_equity_risk_score",
        "short_break_games",
        "consecutive_interstate_away_games",
    ],
    rename_map=FIXTURE_EQUITY_RENAME_MAP,
)

OVERVIEW_TRAVEL_LOAD_TABLE = TablePreset(
    columns=[
        "team",
        "travel_load_score",
        "interstate_away_games",
        "estimated_travel_km",
    ],
    rename_map=TRAVEL_LOAD_RENAME_MAP,
)

OVERVIEW_COMMERCIAL_TABLE = TablePreset(
    columns=[
        "fixture",
        "venue",
        "commercial_opportunity_score",
        "short_category",
    ],
    rename_map=COMPACT_OPPORTUNITY_RENAME_MAP,
)

OVERVIEW_FAN_GROWTH_TABLE = TablePreset(
    columns=[
        "fixture",
        "venue",
        "fan_growth_opportunity_score",
        "short_category",
    ],
    rename_map=COMPACT_OPPORTUNITY_RENAME_MAP,
)


SPECIAL_COLUMN_LABELS = {
    **FIXTURE_EQUITY_RENAME_MAP,
    **TRAVEL_LOAD_RENAME_MAP,
    **COMMERCIAL_RENAME_MAP,
    **FAN_GROWTH_RENAME_MAP,
    **COMPACT_OPPORTUNITY_RENAME_MAP,
    **COMPETITIVE_BALANCE_RENAME_MAP,
    **TEAM_TRAVEL_GAME_RENAME_MAP,
}

SHORT_CATEGORY_LABELS = {
    "Marquee commercial fixture": "Marquee",
    "Growth market opportunity": "Growth",
    "Regional/community engagement opportunity": "Regional",
    "Under-utilised attendance opportunity": "Utilisation",
    "Competitive balance showcase": "Competitive",
    "Standard fixture": "Standard",
}

NUMERIC_COLUMNS = {
    "fixture_equity_risk_score",
    "travel_load_score",
    "commercial_opportunity_score",
    "fan_growth_opportunity_score",
    "fixture_attractiveness_score",
    "average_margin",
    "median_margin",
    "games",
    "games_played",
    "home_games",
    "away_games",
    "home_away_differential",
    "short_break_games",
    "five_day_breaks",
    "six_day_breaks",
    "consecutive_away_games",
    "consecutive_interstate_away_games",
    "interstate_away_games",
    "interstate_home_games",
    "neutral_state_games",
    "estimated_travel_km",
    "estimated_return_travel_km",
    "long_haul_trips",
    "short_break_after_interstate_trip",
    "close_games",
    "blowout_games",
    "days_since_previous_game",
}

INTEGER_COLUMNS = {
    "games",
    "games_played",
    "home_games",
    "away_games",
    "home_away_differential",
    "short_break_games",
    "five_day_breaks",
    "six_day_breaks",
    "consecutive_away_games",
    "consecutive_interstate_away_games",
    "interstate_away_games",
    "interstate_home_games",
    "neutral_state_games",
    "estimated_travel_km",
    "estimated_return_travel_km",
    "long_haul_trips",
    "short_break_after_interstate_trip",
    "close_games",
    "blowout_games",
    "days_since_previous_game",
}

PERCENTAGE_COLUMNS = {
    "estimated_capacity_utilisation",
    "close_game_rate",
    "blowout_game_rate",
}


def prettify_column_name(column: str) -> str:
    """Return a human-readable label for a dataframe column."""
    if column in SPECIAL_COLUMN_LABELS:
        return SPECIAL_COLUMN_LABELS[column]
    return column.replace("_", " ").title()


def truncate_text(value: object, max_length: int = 90) -> str:
    """Return display-safe text with long values shortened."""
    if _is_missing(value):
        return ""
    text = str(value).strip()
    if len(text) <= max_length:
        return text
    return text[: max_length - 3].rstrip() + "..."


def format_fixture_label(home: object, away: object) -> str:
    """Return a compact fixture label as Home v Away."""
    home_text = "" if _is_missing(home) else str(home).strip()
    away_text = "" if _is_missing(away) else str(away).strip()
    if home_text and away_text:
        return f"{home_text} v {away_text}"
    return home_text or away_text


def compact_fixture_label(row: pd.Series) -> str:
    """Return compact fixture text as Home v Away."""
    return format_fixture_label(row.get("home_team", ""), row.get("away_team", ""))


def shorten_opportunity_category(category: object) -> str:
    """Return a compact opportunity category label for narrow tables."""
    if _is_missing(category):
        return "Standard"
    text = str(category).strip()
    if not text:
        return "Standard"
    return SHORT_CATEGORY_LABELS.get(text, truncate_text(text, max_length=24))


def short_opportunity_category(category: object) -> str:
    """Backward-compatible alias for compact opportunity labels."""
    return shorten_opportunity_category(category)


def format_number(value: object, decimals: int = 1) -> str:
    """Format a numeric value for executive table display."""
    if _is_missing(value):
        return ""
    try:
        return f"{float(value):,.{decimals}f}"
    except (TypeError, ValueError):
        return str(value)


def format_integer(value: object) -> str:
    """Format an integer-like value for executive table display."""
    if _is_missing(value):
        return ""
    try:
        return f"{float(value):,.0f}"
    except (TypeError, ValueError):
        return str(value)


def format_percentage(value: object) -> str:
    """Format a percentage stored as a ratio."""
    if _is_missing(value):
        return ""
    try:
        return f"{float(value):.0%}"
    except (TypeError, ValueError):
        return str(value)


def add_compact_opportunity_columns(df: pd.DataFrame) -> pd.DataFrame:
    """Add compact fixture and category fields when source columns are available."""
    result = df.copy()
    if "fixture" not in result.columns and {"home_team", "away_team"}.issubset(result):
        result["fixture"] = result.apply(compact_fixture_label, axis=1)
    if "short_category" not in result.columns and "opportunity_category" in result:
        result["short_category"] = result["opportunity_category"].map(
            shorten_opportunity_category
        )
    return result


def prepare_display_table(
    df: pd.DataFrame,
    columns: list[str],
    rename_map: dict[str, str] | None = None,
    truncate_columns: list[str] | None = None,
    max_text_length: int = 90,
) -> pd.DataFrame:
    """Select, format and label dataframe columns for executive display."""
    if df.empty:
        return pd.DataFrame()
    df = add_compact_opportunity_columns(df)
    selected = [column for column in columns if column in df.columns]
    if not selected:
        return pd.DataFrame()

    display = df.loc[:, selected].copy()
    for column in display.columns:
        if pd.api.types.is_bool_dtype(display[column]):
            display[column] = display[column].map({True: "Yes", False: "No"})
        if column in {
            "estimated_capacity_utilisation",
            "close_game_rate",
            "blowout_game_rate",
        }:
            display[column] = display[column].map(format_percentage)

    for column in truncate_columns or []:
        if column in display.columns:
            display[column] = display[column].map(
                lambda value: truncate_text(value, max_text_length)
            )

    label_map = {
        column: (rename_map or {}).get(column, prettify_column_name(column))
        for column in display.columns
    }
    return display.rename(columns=label_map)


def render_ranked_table(
    df: pd.DataFrame,
    columns: list[str],
    title: str | None = None,
    top_n: int = 10,
    rename_map: dict[str, str] | None = None,
    truncate_columns: list[str] | None = None,
    height: int | None = None,
    empty_message: str = "No ranked rows are available for the current selection.",
) -> None:
    """Render a consistently ordered, compact ranked table."""
    del height
    render_html_table(
        df,
        columns=columns,
        rename_map=rename_map,
        title=title,
        top_n=top_n,
        truncate_columns=truncate_columns,
        empty_message=empty_message,
    )


def render_preset_table(
    df: pd.DataFrame,
    preset: TablePreset,
    title: str | None = None,
    top_n: int = 10,
    height: int | None = None,
    empty_message: str = "No rows are available for the current selection.",
) -> None:
    """Render a dataframe using a reusable table preset."""
    render_ranked_table(
        df,
        preset.columns,
        title=title,
        top_n=top_n,
        rename_map=preset.rename_map,
        truncate_columns=preset.truncate_columns,
        height=height,
        empty_message=empty_message,
    )


def render_dataframe_with_caption(
    df: pd.DataFrame,
    caption: str,
    columns: list[str] | None = None,
    rename_map: dict[str, str] | None = None,
    truncate_columns: list[str] | None = None,
    height: int | None = None,
) -> None:
    """Render a dataframe with a professional caption."""
    st.caption(caption)
    display = prepare_display_table(
        df,
        columns or list(df.columns),
        rename_map=rename_map,
        truncate_columns=truncate_columns,
    )
    if display.empty:
        st.info("No rows are available for the current selection.")
        return
    st.dataframe(
        display,
        use_container_width=True,
        hide_index=True,
        height=height,
        column_config=_column_config(display),
    )


def render_note_cards(
    df: pd.DataFrame,
    title_columns: list[str],
    note_column: str,
    score_column: str | None = None,
    top_n: int = 10,
    empty_message: str = "No detailed notes are available for the current selection.",
) -> None:
    """Render long note fields as compact executive cards."""
    html = build_note_cards_html(
        df=df,
        title_columns=title_columns,
        note_column=note_column,
        score_column=score_column,
        top_n=top_n,
        empty_message=empty_message,
    )
    st.markdown(html, unsafe_allow_html=True)


def build_note_cards_html(
    df: pd.DataFrame,
    title_columns: list[str],
    note_column: str,
    score_column: str | None = None,
    top_n: int = 10,
    empty_message: str = "No detailed notes are available for the current selection.",
) -> str:
    """Build escaped HTML for long note fields without rendering it."""
    if df.empty or note_column not in df.columns:
        return f'<div class="afl-empty-state">{escape(empty_message)}</div>'

    rows = df.head(top_n)
    cards = []
    for _, row in rows.iterrows():
        note = row.get(note_column)
        if not truncate_text(note, max_length=400):
            continue
        title = _format_note_card_title(row, title_columns, score_column)
        score_value = _format_cell(row.get(score_column), score_column)
        score_html = ""
        if score_column and score_value:
            score_html = (
                f'<span class="tag">{escape(prettify_column_name(score_column))}: '
                f"{escape(score_value)}</span>"
            )
        cards.append(
            '<div class="executive-detail-card">'
            f'<div class="executive-detail-title">{escape(title)}</div>'
            f'<div class="executive-detail-note">{escape(str(note).strip())}</div>'
            f"{score_html}"
            "</div>"
        )
    if not cards:
        return f'<div class="afl-empty-state">{escape(empty_message)}</div>'

    return '<div class="executive-detail-grid">' + "".join(cards) + "</div>"


def render_notes_detail(
    df: pd.DataFrame,
    label_columns: list[str],
    note_column: str,
    title: str = "Detailed Notes",
    top_n: int = 10,
    score_column: str | None = None,
) -> None:
    """Render long notes in expandable card sections."""
    with st.expander(title, expanded=False):
        render_note_cards(
            df,
            title_columns=label_columns,
            note_column=note_column,
            score_column=score_column or _infer_score_column(label_columns),
            top_n=top_n,
        )


def render_html_table(
    df: pd.DataFrame,
    columns: list[str],
    rename_map: dict[str, str] | None = None,
    title: str | None = None,
    top_n: int | None = None,
    truncate_columns: list[str] | None = None,
    max_text_length: int = 70,
    compact: bool = True,
    numeric_formats: dict[str, str] | None = None,
    empty_message: str = "No records are available for the current selection.",
) -> None:
    """Render a curated dataframe slice as a responsive executive HTML table."""
    html = build_html_table(
        df=df,
        columns=columns,
        rename_map=rename_map,
        title=title,
        top_n=top_n,
        truncate_columns=truncate_columns,
        max_text_length=max_text_length,
        compact=compact,
        numeric_formats=numeric_formats,
        empty_message=empty_message,
    )
    st.markdown(html, unsafe_allow_html=True)


def build_html_table(
    df: pd.DataFrame,
    columns: list[str],
    rename_map: dict[str, str] | None = None,
    title: str | None = None,
    top_n: int | None = None,
    truncate_columns: list[str] | None = None,
    max_text_length: int = 70,
    compact: bool = True,
    numeric_formats: dict[str, str] | None = None,
    empty_message: str = "No records are available for the current selection.",
) -> str:
    """Build escaped HTML for a curated executive table."""
    working = add_compact_opportunity_columns(df)
    selected = [column for column in columns if column in working.columns]
    title_html = (
        f'<div class="executive-table-title">{escape(title)}</div>' if title else ""
    )
    compact_class = " executive-table--compact" if compact else ""

    if working.empty or not selected:
        return (
            f'<div class="executive-table-wrap{compact_class}">'
            f"{title_html}"
            f'<div class="afl-empty-state">{escape(empty_message)}</div>'
            "</div>"
        )

    display = (
        working.loc[:, selected].head(top_n).copy()
        if top_n
        else working.loc[:, selected].copy()
    )
    labels = [
        escape((rename_map or {}).get(column, prettify_column_name(column)))
        for column in selected
    ]
    header = "".join(f"<th>{label}</th>" for label in labels)
    truncate_set = set(truncate_columns or [])

    body_rows = []
    for _, row in display.iterrows():
        cells = []
        for column in selected:
            value = _format_cell(
                row.get(column),
                column,
                numeric_formats=numeric_formats,
            )
            if column in truncate_set:
                value = truncate_text(value, max_text_length)
            class_names = []
            if column in NUMERIC_COLUMNS or column in PERCENTAGE_COLUMNS:
                class_names.append("num")
            if column == "short_category":
                class_names.append("tag-cell")
                cell_value = f'<span class="tag">{escape(value)}</span>'
            else:
                cell_value = escape(value)
            class_attr = f' class="{" ".join(class_names)}"' if class_names else ""
            cells.append(f"<td{class_attr}>{cell_value}</td>")
        body_rows.append("<tr>" + "".join(cells) + "</tr>")

    return (
        f'<div class="executive-table-wrap{compact_class}">'
        f"{title_html}"
        '<table class="executive-table">'
        f"<thead><tr>{header}</tr></thead>"
        f"<tbody>{''.join(body_rows)}</tbody>"
        "</table>"
        "</div>"
    )


def _column_config(df: pd.DataFrame) -> dict[str, object]:
    config: dict[str, object] = {}
    for column in df.columns:
        if column in {
            "Risk Score",
            "Travel Score",
            "Commercial Score",
            "Fan Growth Score",
            "Attractiveness",
            "Average Margin",
            "Median Margin",
        }:
            config[column] = st.column_config.NumberColumn(column, format="%.1f")
        elif column in {"Estimated Travel Km", "Estimated Return Km"}:
            config[column] = st.column_config.NumberColumn(column, format="%d")
        elif column == "Notes":
            config[column] = st.column_config.TextColumn(column, width="medium")
        elif column in {"Fixture"}:
            config[column] = st.column_config.TextColumn(column, width="medium")
        elif column in {"Venue", "Category", "Window", "Market"}:
            config[column] = st.column_config.TextColumn(column, width="small")
    return config


def _format_cell(
    value: object,
    column: str | None,
    numeric_formats: dict[str, str] | None = None,
) -> str:
    if _is_missing(value):
        return ""
    if isinstance(value, bool):
        return "Yes" if value else "No"
    if column in PERCENTAGE_COLUMNS:
        return format_percentage(value)
    if column in INTEGER_COLUMNS:
        return format_integer(value)
    if column in NUMERIC_COLUMNS:
        decimals = 1
        if numeric_formats and column in numeric_formats:
            spec = numeric_formats[column]
            try:
                return format(float(value), spec)
            except (TypeError, ValueError):
                return str(value)
        return format_number(value, decimals=decimals)
    return str(value).strip()


def _format_note_card_title(
    row: pd.Series,
    title_columns: list[str],
    score_column: str | None,
) -> str:
    if {"home_team", "away_team"}.issubset(row.index):
        title = format_fixture_label(row.get("home_team"), row.get("away_team"))
    elif "fixture" in row.index:
        title = str(row.get("fixture")).strip()
    else:
        title_parts = [
            _format_cell(row.get(column), column)
            for column in title_columns
            if column != score_column and column in row.index
        ]
        title = " / ".join(part for part in title_parts if part)
    if not title:
        title = "Detail"
    if score_column and score_column in row.index:
        score = _format_cell(row.get(score_column), score_column)
        if score:
            return f"{title} - {prettify_column_name(score_column)} {score}"
    return title


def _infer_score_column(columns: list[str]) -> str | None:
    for column in columns:
        if column.endswith("_score"):
            return column
    return None


def _is_missing(value: object) -> bool:
    if value is None:
        return True
    try:
        return bool(pd.isna(value))
    except (TypeError, ValueError):
        return False
