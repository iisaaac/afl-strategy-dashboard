"""Tests for executive detail-card HTML helpers."""

from __future__ import annotations

import inspect

import pandas as pd

from afl_strategy_dashboard.components import tables
from afl_strategy_dashboard.components.tables import (
    build_note_cards_html,
    render_note_cards,
)


def test_build_note_cards_html_escapes_values_and_uses_card_classes() -> None:
    df = pd.DataFrame(
        {
            "team": ["<script>Alert</script>"],
            "travel_load_score": [42.5],
            "travel_load_notes": ["Review <venue> exposure & short breaks."],
        }
    )

    html = build_note_cards_html(
        df,
        title_columns=["team", "travel_load_score"],
        note_column="travel_load_notes",
        score_column="travel_load_score",
    )

    assert "executive-detail-grid" in html
    assert "executive-detail-card" in html
    assert "&lt;script&gt;Alert&lt;/script&gt;" in html
    assert "Review &lt;venue&gt; exposure &amp; short breaks." in html
    assert "<script>" not in html


def test_build_note_cards_html_empty_state_is_polished_and_escaped() -> None:
    html = build_note_cards_html(
        pd.DataFrame(),
        title_columns=["team"],
        note_column="travel_load_notes",
        empty_message="No <notes> available.",
    )

    assert "afl-empty-state" in html
    assert "No &lt;notes&gt; available." in html
    assert "<notes>" not in html


def test_build_note_cards_html_does_not_call_streamlit_debug_output() -> None:
    source = inspect.getsource(tables.build_note_cards_html)

    assert "st." not in source
    assert "st.code" not in source
    assert "st.write" not in source
    assert "st.text" not in source


def test_render_note_cards_returns_none(monkeypatch) -> None:
    calls = []

    def fake_markdown(html: str, unsafe_allow_html: bool = False) -> None:
        calls.append((html, unsafe_allow_html))

    monkeypatch.setattr(tables.st, "markdown", fake_markdown)

    result = render_note_cards(
        pd.DataFrame({"team": ["Fremantle"], "notes": ["Operational review note."]}),
        title_columns=["team"],
        note_column="notes",
    )

    assert result is None
    assert calls
    assert calls[0][1] is True
