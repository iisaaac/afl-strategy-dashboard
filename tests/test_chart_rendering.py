"""Tests for chart rendering helpers."""

from __future__ import annotations

import plotly.graph_objects as go

from afl_strategy_dashboard.components.charts import (
    DEFAULT_PLOTLY_CONFIG,
    apply_chart_height,
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
