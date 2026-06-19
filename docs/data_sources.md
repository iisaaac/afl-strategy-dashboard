# Data Sources

## Squiggle API

The MVP uses the public Squiggle API at `https://api.squiggle.com.au/`.

The client currently supports:

- `q=games` filtered by AFL season year.
- `q=standings` filtered by AFL season year, where supported by the API response.

Squiggle provides basic public AFL data such as fixtures, scores, venues, standings and some prediction-related fields. It does not provide advanced private data such as Champion Data event-level statistics.

## Normalised Game Schema

Raw Squiggle game responses are cached and then normalised into an internal dashboard schema:

```text
game_id
year
round
round_name
date
venue
home_team
away_team
home_score
away_score
winner
complete
is_final
margin
predicted_home_win_probability
predicted_away_win_probability
season_phase
source
```

Fields that are not available in a Squiggle response are filled with `pd.NA`, `None`-like values or sensible derived values. Dates are parsed to pandas datetime values. If a source game ID is unavailable, a stable ID is derived from season, round and teams.

## Season Phase Classification

The normalisation layer classifies each game as `home_and_away`, `finals` or `unknown` using public `round` and `round_name` fields. Finals labels include common public forms such as Elimination Final, Qualifying Final, Semi Final, Preliminary Final, Grand Final and abbreviated labels such as EF, QF, SF, PF and GF.

Numeric rounds and standard round labels are treated as home-and-away where they are clearly regular-season rounds. Ambiguous or missing public labels are classified as `unknown` rather than forced into a conclusion.

## Public Data Only

This project only uses data that is publicly available. It should not be extended with private club data, protected AFL data or licensed Champion Data sources unless the owner has explicit permission.

## Attendance Context

Attendance context is optional and local-first. Users can load a CSV with:

```text
year
round
date
home_team
away_team
venue
crowd
source
```

The loader normalises team and venue names, parses dates, converts crowd to numeric values and labels the source. The dashboard also includes `data/raw/sample_attendance.csv` for demo and test use; it is synthetic sample data.

The sample strategy brief under `docs/assets/reports/` is generated from synthetic/demo fixture data and this synthetic sample attendance workflow. It is included to demonstrate reporting output only and should not be read as official AFL attendance analysis.

An optional AFL Tables-style parser can parse an already-supplied HTML string into the same schema. It does not fetch live data by default and tests do not depend on live scraping.

## Venue Capacity And Market Context

Venue capacity and market context are maintained assumptions in code. They include approximate capacity, city, state, market type, major-stadium flag and regional/special-event flag.

Capacities are approximate and may vary by event configuration, redevelopment works, ticketing holds and stadium operations. They support relative strategy analysis only.

## Caching Approach

API responses are converted to pandas DataFrames and cached as CSV files under:

- `data/raw` for direct API-shaped data.
- `data/processed` for derived data that can be rebuilt.

The cache can be bypassed with the dashboard refresh control or by passing `refresh=True` in the client.

## Distance Assumptions

Travel distances are approximate return kilometres calculated from mapped team home and venue coordinates using Haversine distance. They are useful for relative comparison, but they are not actual club itineraries, flight paths, recovery windows or player welfare measures.

## Responsible API Use

The Squiggle client sends a clear User-Agent. Set `AFL_DASHBOARD_USER_AGENT` to identify yourself when running the project:

```bash
export AFL_DASHBOARD_USER_AGENT="your-name-afl-strategy-dashboard/0.1"
```

For Streamlit Community Cloud, set `AFL_DASHBOARD_USER_AGENT` as an optional secret or environment variable. Do not commit `.streamlit/secrets.toml`.

Local caching is used to avoid unnecessary repeated requests.
