"""Streamlit app for the AFL Strategy Dashboard."""

from __future__ import annotations

import sys
from collections.abc import Callable
from io import StringIO
from pathlib import Path

import pandas as pd
import streamlit as st

if __package__ is None or __package__ == "":
    sys.path.append(str(Path(__file__).resolve().parents[1]))

from afl_strategy_dashboard.data.attendance import (  # noqa: E402
    AttendanceDataError,
    clean_attendance_dataframe,
    load_attendance_csv,
)
from afl_strategy_dashboard.data.dashboard_state import (  # noqa: E402
    DashboardControls,
    DashboardState,
    available_teams,
    build_dashboard_state,
    load_public_or_sample_data,
)
from afl_strategy_dashboard.pages import (  # noqa: E402
    competitive_balance,
    export_brief,
    fan_growth,
    fixture_equity,
    methodology,
    overview,
    travel_load,
)
from afl_strategy_dashboard.styling.plotly_template import (  # noqa: E402
    register_dashboard_template,
)
from afl_strategy_dashboard.styling.theme import apply_custom_css  # noqa: E402

PAGE_RENDERERS: dict[str, Callable[[DashboardState], None]] = {
    "Overview": overview.render,
    "Fixture Equity": fixture_equity.render,
    "Travel Load": travel_load.render,
    "Competitive Balance": competitive_balance.render,
    "Fan Growth & Commercial": fan_growth.render,
    "Export Brief": export_brief.render,
    "Methodology": methodology.render,
}

PAGE_URL_PATHS = {
    "Overview": "overview",
    "Fixture Equity": "fixture-equity",
    "Travel Load": "travel-load",
    "Competitive Balance": "competitive-balance",
    "Fan Growth & Commercial": "fan-growth-commercial",
    "Export Brief": "export-brief",
    "Methodology": "methodology",
}


def main() -> None:
    """Run the Streamlit dashboard."""
    st.set_page_config(
        page_title="AFL Strategy & Fan Growth Analytics Dashboard",
        layout="wide",
    )
    register_dashboard_template()
    apply_custom_css()

    year, refresh, use_sample = _render_primary_sidebar_controls()
    raw_games, ladder, data_note = load_dashboard_data(year, refresh, use_sample)
    selected_team = _render_team_filter(raw_games)
    attendance, attendance_note, controls = _render_secondary_sidebar_controls(
        year=year,
        refresh=refresh,
        use_sample=use_sample,
        selected_team=selected_team,
    )
    state = build_dashboard_state(
        controls=controls,
        raw_games=raw_games,
        ladder=ladder,
        data_note=data_note,
        attendance=attendance,
        attendance_note=attendance_note,
    )
    _render_navigation(state)


@st.cache_data(show_spinner=False)
def load_dashboard_data(
    year: int,
    refresh: bool,
    use_sample: bool,
) -> tuple[pd.DataFrame, pd.DataFrame, str]:
    """Load public or sample data through a Streamlit cache wrapper."""
    return load_public_or_sample_data(year, refresh, use_sample)


def _render_primary_sidebar_controls() -> tuple[int, bool, bool]:
    with st.sidebar:
        st.markdown(
            '<div class="afl-sidebar-heading">AFL Strategy Dashboard</div>',
            unsafe_allow_html=True,
        )
        year = st.selectbox(
            "Season",
            options=list(range(2026, 2014, -1)),
            index=1,
            help="Season to analyse.",
        )
        use_sample = st.toggle(
            "Use sample data",
            value=False,
            help="Use labelled synthetic data.",
        )
        refresh = st.toggle(
            "Refresh cache",
            value=False,
            help="Fetch fresh public data.",
            disabled=use_sample,
        )
    return year, refresh, use_sample


def _render_team_filter(games: pd.DataFrame) -> str:
    teams = available_teams(games)
    with st.sidebar:
        st.divider()
        st.markdown(
            '<div class="afl-sidebar-heading">Analysis Controls</div>',
            unsafe_allow_html=True,
        )
        selected_team = st.selectbox(
            "Team filter",
            options=["All teams", *teams],
            index=0,
            help="Limit views to one club.",
        )
    return selected_team


def _render_secondary_sidebar_controls(
    *,
    year: int,
    refresh: bool,
    use_sample: bool,
    selected_team: str,
) -> tuple[pd.DataFrame, str, DashboardControls]:
    with st.sidebar:
        completed_only = st.toggle(
            "Completed games only",
            value=True,
            help="Use fixtures with scores.",
        )
        season_phase_label = st.selectbox(
            "Season phase",
            options=[
                "Home-and-away season",
                "Finals only",
                "Full season",
            ],
            index=0,
            help="Choose the fixture phase.",
        )
        with st.expander("Attendance context", expanded=False):
            include_attendance = st.toggle(
                "Include attendance data",
                value=False,
                help="Merge optional public or sample crowd data.",
            )
            attendance_upload = st.file_uploader(
                "Upload public attendance CSV",
                type=["csv"],
                help="Upload a public-data CSV you are authorised to use.",
                disabled=not include_attendance,
            )
            use_sample_attendance = st.toggle(
                "Use sample attendance CSV",
                value=False,
                help="Use the included synthetic crowd data.",
                disabled=not include_attendance,
            )
            crowd_only = st.toggle(
                "Only fixtures with crowd data",
                value=False,
                help="Restrict to matched crowd rows.",
                disabled=not include_attendance,
            )

    attendance, attendance_note = load_attendance_context(
        include_attendance=include_attendance,
        attendance_upload=attendance_upload,
        use_sample_attendance=use_sample_attendance,
    )
    controls = DashboardControls(
        year=year,
        refresh=refresh,
        completed_only=completed_only,
        season_phase_label=season_phase_label,
        selected_team=selected_team,
        use_sample=use_sample,
        include_attendance=include_attendance,
        crowd_only=crowd_only,
    )
    return attendance, attendance_note, controls


def load_attendance_context(
    *,
    include_attendance: bool,
    attendance_upload,
    use_sample_attendance: bool,
) -> tuple[pd.DataFrame, str]:
    """Load optional attendance context without breaking normal app use."""
    if not include_attendance:
        return pd.DataFrame(), "Attendance context is not enabled."

    try:
        if attendance_upload is not None:
            text = attendance_upload.getvalue().decode("utf-8")
            attendance = clean_attendance_dataframe(pd.read_csv(StringIO(text)))
            return attendance, "Using uploaded attendance CSV data."
        if use_sample_attendance:
            sample_path = Path("data/raw/sample_attendance.csv")
            attendance = load_attendance_csv(sample_path)
            return (
                attendance,
                "Using synthetic sample attendance data for demonstration.",
            )
    except (AttendanceDataError, UnicodeDecodeError) as exc:
        return pd.DataFrame(), f"Attendance data could not be loaded: {exc}"

    return (
        pd.DataFrame(),
        "Attendance context is enabled, but no attendance CSV has been supplied.",
    )


def _render_navigation(state: DashboardState) -> None:
    """Render Streamlit navigation with a clean radio fallback."""
    if hasattr(st, "navigation") and hasattr(st, "Page"):
        st.session_state["dashboard_state"] = state
        pages = [
            st.Page(
                _page_callable(page_name),
                title=page_name,
                url_path=PAGE_URL_PATHS[page_name],
                default=page_name == "Overview",
            )
            for page_name in PAGE_RENDERERS
        ]
        page = st.navigation(pages, position="sidebar")
        page.run()
        return

    with st.sidebar:
        selected_page = st.radio(
            "Section",
            options=list(PAGE_RENDERERS),
            index=0,
        )
    PAGE_RENDERERS[selected_page](state)


def _page_callable(page_name: str) -> Callable[[], None]:
    def render_page() -> None:
        PAGE_RENDERERS[page_name](st.session_state["dashboard_state"])

    return render_page


if __name__ == "__main__":
    main()
