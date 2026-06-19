# Deployment

This project is deployment-ready for Streamlit Community Cloud. It uses public data only and does not require private credentials, protected AFL data, club data or Champion Data sources.

## Recommended Target

Deploy the app on Streamlit Community Cloud from a GitHub repository.

## App Entrypoint

```bash
streamlit run src/afl_strategy_dashboard/app.py
```

Use this path as the Streamlit app file:

```text
src/afl_strategy_dashboard/app.py
```

## Dependencies

Streamlit Community Cloud can install the runtime dependencies from:

```text
requirements.txt
```

The runtime dependencies mirror the project dependencies in `pyproject.toml`. Development dependencies such as `pytest`, `ruff` and `black` are kept in the optional `dev` extra.

## Python Version

The project requires Python 3.10 or newer. Set the cloud Python version to match local development where possible.

## Optional User-Agent

The app uses public Squiggle API data and sends a default User-Agent. No secret is required.

For clearer API identification, optionally set `AFL_DASHBOARD_USER_AGENT`.

Local shell example:

```bash
export AFL_DASHBOARD_USER_AGENT="your-name-afl-strategy-dashboard/0.1"
```

In Streamlit Community Cloud, add the same value as a secret or environment variable. Do not commit `.streamlit/secrets.toml`.

## Verification

After deployment, open the public app URL and check:

1. Overview loads with public or sample data.
2. Fixture Equity renders KPI cards, charts and tables.
3. Travel Load renders travel exposure outputs.
4. Fan Growth & Commercial renders opportunity outputs.
5. Export Brief previews the brief and provides HTML and Markdown downloads.
6. Methodology communicates public-data caveats clearly.

## README Live Demo Link

After deployment, replace `Live demo: coming soon` in `README.md` with the public Streamlit app URL.

## Checklist

1. Push repo to GitHub.
2. Confirm `requirements.txt` exists.
3. Confirm app entrypoint is `src/afl_strategy_dashboard/app.py`.
4. Deploy on Streamlit Community Cloud.
5. Set Python version to match local development where possible.
6. Optionally set `AFL_DASHBOARD_USER_AGENT` as a secret/environment variable.
7. Test Overview, Fixture Equity, Travel Load, Fan Growth & Commercial, Export Brief.
8. Copy live URL into README.
