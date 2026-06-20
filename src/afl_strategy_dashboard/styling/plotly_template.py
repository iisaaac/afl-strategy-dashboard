"""Plotly template registration for the dashboard."""

from __future__ import annotations

import plotly.graph_objects as go
import plotly.io as pio

DASHBOARD_TEMPLATE_NAME = "afl_strategy_dashboard"
CHART_COLOURWAY = [
    "#0B1F3A",
    "#7A5E12",
    "#1F7A5C",
    "#2F5D7C",
    "#805411",
    "#A33A3A",
    "#5B6472",
]


def build_dashboard_template() -> go.layout.Template:
    """Build the shared executive Plotly template."""
    return go.layout.Template(
        layout=go.Layout(
            font={"family": "Arial, sans-serif", "color": "#172033", "size": 13},
            title={
                "font": {"size": 18, "color": "#0B1F3A"},
                "x": 0,
                "xanchor": "left",
            },
            colorway=CHART_COLOURWAY,
            paper_bgcolor="rgba(255,255,255,0)",
            plot_bgcolor="#FFFFFF",
            height=420,
            margin={"l": 80, "r": 30, "t": 50, "b": 60},
            hoverlabel={
                "bgcolor": "#0B1F3A",
                "bordercolor": "#0B1F3A",
                "font": {"color": "#FFFFFF", "family": "Arial, sans-serif"},
            },
            xaxis={
                "gridcolor": "#E8ECF1",
                "linecolor": "#D8DEE6",
                "zerolinecolor": "#B8C0CC",
                "title_font": {"color": "#5B6472"},
                "tickfont": {"color": "#5B6472"},
            },
            yaxis={
                "gridcolor": "#F0F2F5",
                "linecolor": "#D8DEE6",
                "zerolinecolor": "#B8C0CC",
                "title_font": {"color": "#5B6472"},
                "tickfont": {"color": "#5B6472"},
            },
            legend={
                "orientation": "h",
                "yanchor": "bottom",
                "y": 1.02,
                "xanchor": "right",
                "x": 1,
            },
        )
    )


def register_dashboard_template(set_default: bool = False) -> str:
    """Register the dashboard Plotly template and optionally make it default."""
    pio.templates[DASHBOARD_TEMPLATE_NAME] = build_dashboard_template()
    if set_default:
        pio.templates.default = DASHBOARD_TEMPLATE_NAME
    return DASHBOARD_TEMPLATE_NAME


def apply_dashboard_template(fig: go.Figure) -> go.Figure:
    """Apply the shared template and common layout polish to a figure."""
    register_dashboard_template()
    fig.update_layout(template=DASHBOARD_TEMPLATE_NAME)
    fig.update_layout(
        bargap=0.22,
        hovermode="closest",
        title_pad={"b": 12},
    )
    return fig
