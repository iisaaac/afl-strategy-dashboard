# Screenshot Guide

Use this guide to capture consistent, professional screenshots for the portfolio README.

## Recommended Setup

- Run the dashboard locally with `streamlit run src/afl_strategy_dashboard/app.py`.
- Use sample-data mode for consistent screenshots.
- Recommended browser size: `1440 x 1000`.
- Use a clean browser window with no developer console, error overlays or debug traces.
- Capture the app content area below the browser toolbar, and crop out the
  browser/tab bar for README screenshots.
- Collapse or hide unnecessary sidebar sections where practical while keeping the active filters understandable.
- Ensure at least one screenshot shows the public-data prototype or methodology caveat.
- The local Streamlit config sets `toolbarMode = "minimal"`. If the browser still
  shows deployment controls or top chrome in your Streamlit version, crop the
  screenshot to the app content area below the browser and Streamlit toolbar.

## Recommended Screenshots

1. Overview page hero and KPI cards.
2. Fixture Equity page showing the risk chart and ranked table.
3. Travel Load page showing travel score and estimated kilometres.
4. Fan Growth & Commercial page showing opportunity leaderboards.
5. Export Brief page showing report preview and download buttons.
6. Methodology page showing public-data caveats.

## Naming Convention

Save screenshots under:

```text
docs/assets/screenshots/01_overview.png
docs/assets/screenshots/02_fixture_equity.png
docs/assets/screenshots/03_travel_load.png
docs/assets/screenshots/04_fan_growth_commercial.png
docs/assets/screenshots/05_export_brief.png
docs/assets/screenshots/06_methodology.png
```

## Capture Notes

- Use sample-data mode so charts, tables and exported report previews are stable.
- If attendance context is shown, use `data/raw/sample_attendance.csv` and keep the synthetic/demo wording visible where possible.
- Avoid screenshots with browser errors, local stack traces or missing chart renders.
- Prefer screenshots that show both business framing and analytical output, not only controls.
