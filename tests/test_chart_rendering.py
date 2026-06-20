"""Tests for chart rendering helpers."""

from __future__ import annotations

import plotly.graph_objects as go

from afl_strategy_dashboard.components.charts import (
    DEFAULT_PLOTLY_CONFIG,
    apply_chart_height,
)
from afl_strategy_dashboard.visualisation.charts import (
    BLUE,
    GOLD,
    leader_highlight_colours,
)


def test_default_plotly_config_hides_modebar() -> None:
    assert DEFAULT_PLOTLY_CONFIG["displayModeBar"] is False
    assert DEFAULT_PLOTLY_CONFIG["responsive"] is True


def test_apply_chart_height_sets_layout_height() -> None:
    fig = apply_chart_height(go.Figure(), 480)

    assert fig.layout.height == 480


def test_apply_chart_height_leaves_default_when_none() -> None:
    fig = apply_chart_height(go.Figure(), None)

    assert fig.layout.height is None


def test_leader_highlight_colours_emphasise_final_ascending_bar() -> None:
    assert leader_highlight_colours(3, BLUE) == [BLUE, BLUE, GOLD]


def test_leader_highlight_colours_handle_empty_chart() -> None:
    assert leader_highlight_colours(0, BLUE) == []
