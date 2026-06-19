"""Methodology page."""

from __future__ import annotations

import streamlit as st

from afl_strategy_dashboard.components.layout import (
    render_dashboard_context,
    render_methodology_callout,
    render_page_header,
    render_section_header,
)
from afl_strategy_dashboard.data.dashboard_state import DashboardState


def render(state: DashboardState) -> None:
    """Render methodology documentation inside the app."""
    render_page_header(
        "Methodology",
        "Transparent public-data methods, scoring caveats and responsible-use "
        "notes for the dashboard.",
        eyebrow="Data and methodology",
    )
    render_dashboard_context(state)

    sections = [
        (
            "Data Sources",
            "The primary source is the public Squiggle API, normalised into a stable "
            "game schema and cached locally. Optional attendance context can be "
            "loaded from a user-supplied local CSV or the labelled synthetic sample.",
        ),
        (
            "Public Data Only",
            "The prototype does not use private AFL, club or Champion Data sources. "
            "Outputs are suitable for portfolio demonstration and strategy "
            "discussion, not official decision-making.",
        ),
        (
            "Season-Phase Handling",
            "Games are classified as home-and-away, finals or unknown. Fixture "
            "equity and travel load default to home-and-away because finals "
            "participation and venue allocation are performance-dependent.",
        ),
        (
            "Fixture Equity Methodology",
            "The fixture equity risk score increases with short breaks, five-day "
            "and six-day breaks, home/away imbalance, consecutive away-game runs "
            "and consecutive interstate-away exposure.",
        ),
        (
            "Travel-Load Methodology",
            "Travel load uses public team and venue geography to estimate interstate "
            "exposure, approximate return kilometres, long-haul trips and short "
            "breaks following interstate travel.",
        ),
        (
            "Competitive Balance Methodology",
            "Competitive balance uses score-derived absolute margins, average and "
            "median margin, close-game counts, blowout counts and upset indicators "
            "where public prediction fields exist.",
        ),
        (
            "Fan-Growth Scoring",
            "Fan-growth opportunity increases with growth-market venue context, "
            "regional or special-event context, competitive match profile, "
            "under-utilised capacity, fixture attractiveness and prime timing.",
        ),
        (
            "Commercial Opportunity Scoring",
            "Commercial opportunity considers approximate venue capacity, utilisation "
            "where attendance exists, rivalry context, broad broadcast-window style "
            "timing, large-market teams and regional or special-event context.",
        ),
        (
            "Attendance-Context Workflow",
            "Attendance data is optional and local-first. When present, it is cleaned "
            "and merged onto fixtures to support utilisation views. When absent, "
            "opportunity scoring continues using fixture and venue signals.",
        ),
        (
            "Limitations",
            "Travel distances are approximate, venue capacities are public "
            "assumptions, attendance context can be incomplete and the scoring "
            "models are deliberately simple heuristics.",
        ),
        (
            "Responsible Data Use",
            "The dashboard avoids private or protected data and frames outputs as "
            "review priorities. Internal AFL attendance, ticketing, broadcast, "
            "digital, commercial and operations data would be required for "
            "decision-grade modelling.",
        ),
    ]

    for title, body in sections:
        render_section_header(title)
        st.write(body)

    render_methodology_callout(
        "Scores are designed to identify questions worth reviewing, not to prove "
        "fixture fairness, travel impact, commercial value or future fan-growth "
        "outcomes."
    )
    with st.expander("Current data status", expanded=False):
        st.write(state.data_note)
        st.write(state.attendance_note)
        st.write(f"Current phase: {state.controls.season_phase_label}")
        st.write(f"Current team filter: {state.controls.selected_team}")
