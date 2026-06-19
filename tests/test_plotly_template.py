"""Tests for dashboard Plotly styling."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

from afl_strategy_dashboard.styling.plotly_template import (
    DASHBOARD_TEMPLATE_NAME,
    apply_dashboard_template,
    register_dashboard_template,
)


def test_template_registration() -> None:
    name = register_dashboard_template()

    assert name == DASHBOARD_TEMPLATE_NAME
    assert DASHBOARD_TEMPLATE_NAME in pio.templates


def test_apply_dashboard_template_sets_template_name() -> None:
    fig = apply_dashboard_template(go.Figure())

    assert fig.layout.template.layout.font.family == "Arial, sans-serif"
    assert fig.layout.hovermode == "closest"
    assert fig.layout.template.layout.height == 420
    assert fig.layout.template.layout.margin.l == 80
