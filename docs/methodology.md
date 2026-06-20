# Methodology

This dashboard is a public-data prototype. Metrics are intended to support strategy discussion, not to make definitive claims about AFL fixture design or commercial performance.

## Interface And Presentation Layer

The Streamlit interface is organised as a multipage executive dashboard. The Overview page provides the recruiter-facing landing view, while dedicated pages separate fixture equity, travel load, competitive balance, fan-growth and commercial opportunity, and methodology.

Reusable components provide consistent KPI cards, badges, insight panels, tables, empty states and methodology caveats. The visual theme uses a restrained executive palette and a shared Plotly template so chart styling is consistent across pages.

The presentation layer does not alter the analytical calculations. It consumes the same feature outputs and frames them as public-data review priorities for further internal review.

## Executive Brief Export

The dashboard can generate a concise executive strategy brief from the current sidebar filters. The export reflects the selected season, season phase, team filter, live or sample data mode, completed-games setting and attendance-context settings active at the time of generation.

HTML and Markdown exports are supported. The HTML report uses embedded styling so it can open cleanly outside Streamlit, while the Markdown report provides a portable fallback. Downloads are generated directly from the current dashboard context.

PDF export is not currently implemented because the project does not include a reliable PDF rendering dependency. This is future work rather than a core methodology requirement.

The brief uses the same transparent feature tables and recommendation outputs as the dashboard. It is intended for recruiter-ready communication and interview discussion, not as a production AFL planning document.

## Season Phase Handling

Games are classified into:

- `home_and_away`
- `finals`
- `unknown`

Fixture equity and travel load default to home-and-away season only. This is a methodological choice: those models are designed to assess the regular-season fixture allocated to clubs. Finals participation is performance-dependent, and finals venue allocation follows different sporting, operational and commercial constraints.

Finals remain relevant for competitive balance, fan-growth and commercial opportunity analysis when selected explicitly. They should not be mixed into regular-season equity conclusions without clear labelling.

## Fixture Equity

Fixture equity metrics currently include one row per team with:

- Team games played.
- Home, away and neutral-state game counts.
- Home-away differential.
- Short-break games, including five-day and six-day breaks.
- Average, minimum and maximum days between games.
- Maximum consecutive away-game streak.
- Maximum consecutive interstate-away-game streak.
- A fixture equity risk score.
- A concise public-data interpretation note.

Short breaks are identified by ordering each team's matches by date and flagging games played fewer than seven days after the club's previous match. Neutral-state games are flagged where public venue/team mapping suggests neither team is in its normal home state or where the mapping is incomplete. This view should generally be interpreted using the home-and-away season filter.

The fixture equity risk score is a transparent heuristic. It increases with:

- Short-break games.
- Five-day and six-day breaks.
- Away-game imbalance.
- Consecutive away-game streaks.
- Consecutive interstate-away-game streaks.

The score is designed to rank public-data review priorities. It is not a definitive fairness judgement.

The implemented weighting is:

```text
2.0 x short-break games
+ 1.5 x five-day breaks
+ 1.0 x six-day breaks
+ 1.5 x away-game imbalance (away games above home games only)
+ 1.0 x away-run games above the first consecutive away game
+ 2.0 x interstate-away-run games above the first consecutive game
```

Five-day and six-day breaks are subsets of short breaks, so their additional terms
deliberately give those exposures more weight. The score is unbounded and should be
used for ranking within a comparable fixture selection, not as a percentage or an
absolute risk scale.

## Travel Load

Travel load uses public team and venue geography:

- Each team is mapped to a home city and state.
- Each major venue is mapped to a city, state and approximate latitude/longitude.
- A team-game is flagged as interstate travel when the venue state differs from the team's home state.
- Approximate return kilometres are estimated with Haversine distance between the team's home location and venue location.
- Long-haul trips are flagged above 2,000km return.
- Short-break-after-interstate-trip exposure is flagged when the team plays again fewer than seven days after an interstate trip.

The travel load score is a transparent heuristic. It increases with interstate away games, home-listed interstate games, long-haul trips, short breaks after interstate travel and total estimated travel kilometres.

The implemented weighting is:

```text
2.0 x interstate away games
+ 1.0 x home-listed interstate games
+ 2.0 x long-haul trips
+ 2.5 x short breaks after an interstate trip
+ estimated return kilometres / 2,500
```

The score is unbounded and supports relative ranking within a comparable selection;
it is not a player-welfare or fatigue scale.

This does not estimate actual flight routing, time zones, travel day timing, recovery quality or player welfare impact. Like fixture equity, this view should generally be interpreted using the home-and-away season filter.

## Competitive Balance

Competitive balance uses score-derived match margins:

- Absolute match margin.
- Average and median margin.
- Close-game count and rate.
- Blowout count and rate.
- Upset indicators where public prediction fields are available.

Default thresholds are 12 points for close games and 40 points for blowouts.

## Fan Growth Scoring

Fixture attractiveness is a heuristic score based on public fixture fields:

- Rivalry-style team pairings.
- Significant or major venues.
- Top-ladder teams where ladder data is available.
- Close-game or balanced-probability competitive profile.
- Broadcast-window style timing such as Thursday night, Friday night and Saturday night.
- High capacity utilisation where crowd and approximate venue capacity data are available.

Scores are designed to rank fixtures for further investigation, not to replace attendance, ticketing, broadcast or digital engagement data.

The fixture-attractiveness score has a maximum of 100 points: rivalry (30), prime
timing (20), major stadium (15), close-game or balanced-probability signal (15),
top-four ladder/form signal (10), and at least 75% estimated utilisation (10).

## Attendance And Venue Utilisation

Attendance context is optional. The dashboard can merge an uploaded public-data CSV
onto normalised fixtures using year, teams, venue and date where available. Match
confidence is labelled as high, medium, low or unmatched.

Estimated capacity utilisation is calculated as:

```text
crowd / approximate venue capacity
```

Venue capacities are maintained assumptions from public context. They are not official operating capacities and may vary by configuration, event, redevelopment works, ticketing holds and stadium operations.

An optional parser can process an already-supplied AFL Tables-style HTML string. The app does not depend on live scraping.

When no attendance data is loaded, utilisation charts are hidden and the opportunity model continues to use fixture, venue, rivalry, timing and market-context signals. This keeps the app usable without implying crowd-data completeness.

## Broadcast-Window Classification

Fixture date/time is classified into broad timing buckets:

- Thursday night.
- Friday night.
- Saturday day.
- Saturday twilight.
- Saturday night.
- Sunday day.
- Sunday twilight.
- Other / unknown.

These buckets are descriptive only. They do not represent internal broadcast strategy, rights value or audience forecasts.

## Fan Growth Opportunity Score

The fan-growth opportunity score is a transparent heuristic that increases with:

- Growth-market venue context.
- Regional or special-event venue context.
- Competitive match profile.
- Under-utilised venue where crowd and capacity data exist.
- Fixture attractiveness.
- Prime broadcast-window style timing.

This score is intended to identify fixtures that may warrant deeper internal review for audience, attendance, community or participation objectives.

The score adds 25% of fixture attractiveness, growth-market context (25), regional
or special-event context (20), a competitive profile (15), estimated utilisation
below 65% (15), and prime timing (10). Its theoretical maximum is 110. It is a
ranking index, not a probability or percentage.

## Commercial Opportunity Score

The commercial opportunity score is a transparent heuristic that increases with:

- Approximate venue capacity.
- High estimated capacity utilisation where crowd data exists.
- Rivalry or marquee fixture context.
- Prime broadcast-window style timing.
- Large-market team combinations.
- Regional or special-event fixture context.

The score is not an official revenue forecast and does not use ticketing, sponsorship, broadcast contract or internal commercial data.

The score adds approximate capacity divided by 2,500, capped at 25 points; estimated
utilisation of at least 75% (20); rivalry context (15); prime timing (15); five
points for each listed large-market team; and regional or special-event context
(10). Its theoretical maximum is 95. The maintained team grouping is a modelling
assumption, not an official AFL market classification.

## Retrospective And Forward-Looking Use

For completed fixtures, the competitive signal can use the realised match margin
and the ladder input can reflect a later season state. Attendance utilisation is
also observed after the event. These are retrospective descriptive inputs and must
not be presented as information that was available before the fixture.

For incomplete fixtures, the model can use public probability fields where present,
but it remains a simple heuristic rather than a forecast. A decision-grade planning
version would require time-stamped ladder/form inputs, documented prediction
provenance and a strict as-at date to avoid hindsight leakage.

## Limitations

- Public data is incomplete for internal AFL business decisions.
- Venue and team geography mappings need ongoing maintenance.
- The scoring model is transparent but simple.
- Scores use different scales and should not be compared directly with one another.
- Executive brief exports reflect the current dashboard filters and are not versioned decision records.
- Internal AFL attendance, ticketing, broadcast, stadium operations and player welfare data would be needed for decision-grade modelling.
- Crowd size alone is not treated as the only measure of strategic value because regional, community, participation and growth-market objectives may matter even when crowd scale is modest.
- The prototype avoids private or protected Champion Data sources.
- The interface is recruiter-ready for portfolio demonstration, but it should not be described as a production-grade AFL planning platform.
