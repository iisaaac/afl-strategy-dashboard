"""Templates and constants for executive brief exports."""

from __future__ import annotations

BRIEF_TITLE = "AFL Strategy & Fan Growth Analytics Brief"
BRIEF_SUBTITLE = (
    "Public-data prototype assessing fixture equity, travel load, competitive "
    "balance, venue utilisation, fan-growth opportunity and commercial activation "
    "signals."
)
METHODOLOGY_CAVEAT = (
    "This brief is generated from public data and transparent heuristic scoring. "
    "It is intended to identify review priorities and demonstrate analytical "
    "thinking, not to reproduce official AFL fixture, commercial, attendance, "
    "broadcast or player-welfare models."
)
HTML_REPORT_CSS = """
    :root {
        --background: #F7F8FA;
        --surface: #FFFFFF;
        --primary: #0B1F3A;
        --accent: #C8A24A;
        --text: #172033;
        --muted: #5B6472;
        --border: #E1E5EA;
        --risk: #B7791F;
        --opportunity: #1F7A5C;
    }
    * { box-sizing: border-box; }
    body {
        margin: 0;
        background: var(--background);
        color: var(--text);
        font-family: Arial, Helvetica, sans-serif;
        line-height: 1.45;
    }
    .brief {
        max-width: 1100px;
        margin: 0 auto;
        padding: 32px;
    }
    .header {
        border-bottom: 3px solid var(--accent);
        padding-bottom: 18px;
        margin-bottom: 22px;
    }
    .eyebrow {
        color: var(--accent);
        font-size: 12px;
        font-weight: 700;
        letter-spacing: 0.08em;
        text-transform: uppercase;
    }
    h1 {
        color: var(--primary);
        font-size: 34px;
        line-height: 1.08;
        margin: 6px 0 8px;
    }
    h2 {
        color: var(--primary);
        font-size: 18px;
        margin: 24px 0 10px;
    }
    p { margin: 0 0 10px; }
    .subtitle {
        color: var(--muted);
        font-size: 15px;
        max-width: 850px;
    }
    .meta {
        display: grid;
        grid-template-columns: repeat(5, 1fr);
        gap: 8px;
        margin-top: 18px;
    }
    .meta-item, .metric-card, .section, .caveat {
        background: var(--surface);
        border: 1px solid var(--border);
        border-radius: 8px;
    }
    .meta-item {
        padding: 10px 12px;
        min-height: 70px;
    }
    .label {
        color: var(--muted);
        display: block;
        font-size: 11px;
        font-weight: 700;
        letter-spacing: 0.04em;
        text-transform: uppercase;
    }
    .value {
        color: var(--primary);
        display: block;
        font-size: 14px;
        font-weight: 700;
        margin-top: 5px;
    }
    .metrics {
        display: grid;
        grid-template-columns: repeat(3, 1fr);
        gap: 10px;
    }
    .metric-card {
        padding: 14px;
        min-height: 96px;
    }
    .metric-card .value {
        font-size: 20px;
        overflow-wrap: anywhere;
    }
    .section {
        padding: 16px;
        margin-top: 12px;
    }
    ol {
        margin: 0;
        padding-left: 22px;
    }
    li { margin-bottom: 8px; }
    .table-grid {
        display: grid;
        grid-template-columns: repeat(2, minmax(0, 1fr));
        gap: 12px;
    }
    table {
        border-collapse: collapse;
        width: 100%;
        font-size: 12px;
    }
    th, td {
        border-bottom: 1px solid var(--border);
        padding: 7px 6px;
        text-align: left;
        vertical-align: top;
    }
    th {
        color: var(--muted);
        font-size: 11px;
        text-transform: uppercase;
    }
    .caveat {
        border-left: 4px solid var(--accent);
        color: var(--muted);
        margin-top: 18px;
        padding: 14px 16px;
    }
    .sources {
        color: var(--muted);
        font-size: 12px;
        margin-top: 14px;
    }
    @media print {
        body { background: #FFFFFF; }
        .brief { padding: 18px; }
        .section, .metric-card, .meta-item, .caveat { break-inside: avoid; }
    }
    @media (max-width: 860px) {
        .meta, .metrics, .table-grid { grid-template-columns: 1fr; }
        .brief { padding: 18px; }
    }
"""
