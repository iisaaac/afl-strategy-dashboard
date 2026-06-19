"""Custom Streamlit CSS theme."""

from __future__ import annotations

import streamlit as st

PALETTE = {
    "background": "#F7F8FA",
    "surface": "#FFFFFF",
    "primary": "#0B1F3A",
    "accent": "#C8A24A",
    "text": "#172033",
    "muted": "#5B6472",
    "success": "#1F7A5C",
    "warning": "#B7791F",
    "danger": "#A33A3A",
    "border": "#E1E5EA",
    "info": "#2F5D7C",
}


def apply_custom_css() -> None:
    """Apply modest, reusable dashboard CSS."""
    st.markdown(
        f"""
        <style>
        .stApp {{
            background: {PALETTE["background"]};
            color: {PALETTE["text"]};
        }}
        .block-container {{
            padding-top: 1.25rem;
            padding-bottom: 3rem;
            max-width: 1320px;
        }}
        h1, h2, h3 {{
            color: {PALETTE["primary"]};
            letter-spacing: 0;
        }}
        .afl-page-header {{
            padding: 1.25rem 0 0.85rem;
            border-bottom: 1px solid {PALETTE["border"]};
            margin-top: 0;
            margin-bottom: 0.75rem;
            overflow: visible;
        }}
        .afl-page-header h1 {{
            font-size: 2.25rem;
            line-height: 1.1;
            margin: 0 0 0.45rem;
        }}
        .afl-page-header p {{
            color: {PALETTE["muted"]};
            font-size: 1.02rem;
            max-width: 980px;
            margin: 0;
        }}
        .afl-eyebrow {{
            display: block;
            color: {PALETTE["accent"]};
            font-size: 0.78rem;
            font-weight: 700;
            line-height: 1.35;
            margin-bottom: 0.6rem;
            overflow: visible;
            text-transform: uppercase;
            letter-spacing: 0.12em;
        }}
        .afl-sidebar-heading {{
            color: {PALETTE["primary"]};
            font-size: 0.94rem;
            font-weight: 760;
            margin: 0.2rem 0 0.4rem;
        }}
        [data-testid="stSidebar"] [data-testid="stVerticalBlock"] {{
            gap: 0.45rem;
        }}
        [data-testid="stSidebar"] label,
        [data-testid="stSidebar"] p {{
            font-size: 0.84rem;
        }}
        .afl-section-header {{
            margin: 1.4rem 0 0.65rem;
        }}
        .afl-section-header h2 {{
            font-size: 1.2rem;
            margin-bottom: 0.15rem;
        }}
        .afl-section-subtitle {{
            color: {PALETTE["muted"]};
            margin: 0;
        }}
        .afl-spacer {{
            display: block;
            width: 100%;
        }}
        .afl-spacer--sm {{
            height: 0.55rem;
        }}
        .afl-spacer--md {{
            height: 1rem;
        }}
        .afl-spacer--lg {{
            height: 1.55rem;
        }}
        .afl-chart-spacer {{
            height: 0.75rem;
        }}
        .afl-content-divider {{
            border-top: 1px solid {PALETTE["border"]};
            margin: 1.1rem 0 1.25rem;
            width: 100%;
        }}
        .afl-card {{
            background: {PALETTE["surface"]};
            border: 1px solid {PALETTE["border"]};
            border-radius: 8px;
            padding: 1rem;
            box-shadow: 0 1px 2px rgba(11, 31, 58, 0.04);
            min-height: 130px;
            margin-bottom: 0.75rem;
        }}
        .afl-card-title {{
            color: {PALETTE["muted"]};
            font-size: 0.78rem;
            font-weight: 700;
            text-transform: uppercase;
            letter-spacing: 0.04em;
        }}
        .afl-card-value {{
            color: {PALETTE["primary"]};
            font-size: 1.55rem;
            font-weight: 760;
            line-height: 1.2;
            margin-top: 0.45rem;
            overflow-wrap: anywhere;
        }}
        .afl-card-subtitle,
        .afl-card-body,
        .afl-card-status {{
            color: {PALETTE["muted"]};
            font-size: 0.92rem;
            margin-top: 0.45rem;
        }}
        .executive-table-wrap {{
            width: 100%;
            max-width: 100%;
            overflow: hidden;
            background: {PALETTE["surface"]};
            border: 1px solid {PALETTE["border"]};
            border-radius: 8px;
            box-shadow: 0 1px 2px rgba(11, 31, 58, 0.04);
            margin: 0.45rem 0 0.85rem;
        }}
        .executive-table-title {{
            color: {PALETTE["primary"]};
            font-size: 0.92rem;
            font-weight: 760;
            padding: 0.78rem 0.85rem 0.55rem;
            border-bottom: 1px solid {PALETTE["border"]};
        }}
        .executive-table {{
            width: 100%;
            table-layout: fixed;
            border-collapse: collapse;
            font-size: 0.78rem;
            line-height: 1.25;
        }}
        .executive-table th {{
            color: {PALETTE["muted"]};
            background: #FAFBFC;
            border-bottom: 1px solid {PALETTE["border"]};
            font-size: 0.68rem;
            font-weight: 760;
            letter-spacing: 0.03em;
            padding: 0.52rem 0.62rem;
            text-align: left;
            text-transform: uppercase;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .executive-table td {{
            color: {PALETTE["text"]};
            border-bottom: 1px solid #EEF1F4;
            padding: 0.5rem 0.62rem;
            vertical-align: middle;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .executive-table tbody tr:last-child td {{
            border-bottom: 0;
        }}
        .executive-table .num {{
            color: {PALETTE["primary"]};
            font-variant-numeric: tabular-nums;
            text-align: right;
        }}
        .executive-table .muted {{
            color: {PALETTE["muted"]};
        }}
        .executive-table .tag,
        .executive-detail-card .tag {{
            display: inline-flex;
            max-width: 100%;
            align-items: center;
            border-radius: 999px;
            border: 1px solid #D8E1EA;
            background: #F4F7FA;
            color: {PALETTE["info"]};
            font-size: 0.7rem;
            font-weight: 760;
            line-height: 1.2;
            padding: 0.18rem 0.44rem;
            white-space: nowrap;
            overflow: hidden;
            text-overflow: ellipsis;
        }}
        .executive-detail-grid {{
            display: grid;
            grid-template-columns: repeat(2, minmax(0, 1fr));
            gap: 0.85rem;
            margin: 0.75rem 0 0.6rem;
        }}
        .executive-detail-card {{
            background: {PALETTE["surface"]};
            border: 1px solid {PALETTE["border"]};
            border-radius: 12px;
            padding: 1rem;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.04);
            min-width: 0;
        }}
        .executive-detail-title {{
            color: {PALETTE["primary"]};
            font-size: 0.92rem;
            font-weight: 700;
            line-height: 1.25;
            margin-bottom: 0.45rem;
            overflow-wrap: anywhere;
        }}
        .executive-detail-note {{
            color: {PALETTE["muted"]};
            font-size: 0.92rem;
            line-height: 1.45;
            margin-bottom: 0.55rem;
            overflow-wrap: anywhere;
        }}
        .afl-badge-row {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.45rem;
            margin: 0.6rem 0 1rem;
        }}
        .afl-badge {{
            display: inline-flex;
            align-items: center;
            border-radius: 999px;
            padding: 0.28rem 0.62rem;
            font-size: 0.76rem;
            font-weight: 700;
            border: 1px solid {PALETTE["border"]};
            background: #FFFFFF;
            color: {PALETTE["muted"]};
            margin-right: 0.35rem;
            margin-bottom: 0.35rem;
        }}
        .afl-badge--premium {{
            color: {PALETTE["primary"]};
            background: #F7F0DE;
            border-color: #E8D6A5;
        }}
        .afl-badge--success {{
            color: {PALETTE["success"]};
            background: #EAF5F0;
            border-color: #CDE5DB;
        }}
        .afl-badge--warning {{
            color: {PALETTE["warning"]};
            background: #FFF4DE;
            border-color: #E9D2A2;
        }}
        .afl-badge--risk {{
            color: {PALETTE["danger"]};
            background: #FBEAEA;
            border-color: #E7C4C4;
        }}
        .afl-badge--info {{
            color: {PALETTE["info"]};
            background: #EAF2F7;
            border-color: #C9DAE5;
        }}
        .afl-callout,
        .afl-interpretation,
        .afl-recommendations,
        .afl-empty-state {{
            background: {PALETTE["surface"]};
            border: 1px solid {PALETTE["border"]};
            border-radius: 8px;
            padding: 0.9rem 1rem;
            color: {PALETTE["text"]};
        }}
        .afl-callout,
        .afl-interpretation {{
            border-left: 4px solid {PALETTE["accent"]};
            color: {PALETTE["muted"]};
        }}
        .afl-recommendations ol {{
            margin-bottom: 0;
            padding-left: 1.2rem;
        }}
        .afl-recommendations li {{
            margin-bottom: 0.55rem;
        }}
        .context-strip {{
            display: flex;
            flex-wrap: wrap;
            gap: 0.55rem 0.9rem;
            align-items: center;
            max-width: 1040px;
            margin: 0 0 1rem;
            padding: 0.62rem 0.82rem;
            background: {PALETTE["surface"]};
            border: 1px solid {PALETTE["border"]};
            border-radius: 12px;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.03);
        }}
        .context-pill {{
            display: inline-flex;
            gap: 0.35rem;
            align-items: center;
            color: {PALETTE["muted"]};
            font-size: 0.86rem;
            line-height: 1.2;
        }}
        .context-pill strong {{
            color: {PALETTE["primary"]};
            font-weight: 700;
        }}
        @media (max-width: 900px) {{
            .executive-detail-grid {{
                grid-template-columns: 1fr;
            }}
            .context-strip {{
                max-width: 100%;
            }}
        }}
        .afl-empty-title {{
            color: {PALETTE["primary"]};
            font-weight: 760;
            margin-bottom: 0.3rem;
        }}
        [data-testid="stMetricValue"] {{
            color: {PALETTE["primary"]};
        }}
        h1 a, h2 a, h3 a {{
            display: none;
        }}
        [data-testid="stHeaderActionElements"] {{
            display: none !important;
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )
