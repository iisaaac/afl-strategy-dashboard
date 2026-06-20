# Project Case Study

## Problem

AFL fixture strategy needs to balance sporting fairness, player travel burden, venue availability, broadcast appeal, commercial outcomes and long-term fan growth. Public data cannot reproduce internal AFL decision systems, but it can demonstrate how transparent analytics can frame better business questions.

## Approach

This project translates public fixture, result, venue and optional attendance-context data into a multipage executive dashboard. It separates regular-season fixture and travel analysis from finals context, then presents findings through KPI cards, Plotly charts, ranked tables and cautious recommendations.

## Data

The dashboard uses the public Squiggle API for fixture, result and ladder context. Optional attendance context can be supplied through a local CSV. The included sample attendance file is synthetic demo data and is not official AFL attendance data.

## Dashboard Outputs

The dashboard provides views for overview KPIs, fixture equity, travel load, competitive balance, fan-growth and commercial opportunity, methodology, and executive brief export. The export page generates standalone HTML and Markdown reports from the current filters.

## Technical Implementation

The codebase is a modular Python package with a cache-aware API client, normalised game schema, pandas feature modules, a shared `DashboardState`, reusable Streamlit components, a custom Plotly template and pytest coverage.

## Limitations

Scores are transparent heuristics for review-priority ranking. The project does not use private AFL, club, Champion Data, ticketing, commercial, broadcast or player-welfare data. Venue capacities and travel distances are approximate public assumptions.

## Future Enhancements

The next analytical priority is a focused public attendance and venue-utilisation
feature, subject to source terms and data quality. Later work could separate
retrospective opportunity analysis from time-valid pre-fixture planning, version
venue-capacity assumptions, add AFLW support where suitable public data exists and
add PDF export only if a reliable dependency is justified.

## AFL Graduate Program Relevance

The project demonstrates applied analytical thinking across strategy, data, operations, commercial, fan growth and technology audiences. It is designed to show how technical execution can be paired with careful business judgement and responsible data use.
