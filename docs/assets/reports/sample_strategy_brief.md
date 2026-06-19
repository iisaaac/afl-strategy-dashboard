# AFL Strategy & Fan Growth Analytics Brief
Public-data prototype assessing fixture equity, travel load, competitive balance, venue utilisation, fan-growth opportunity and commercial activation signals.

## Brief Header
- Project: AFL Strategy & Fan Growth Analytics Dashboard
- Season: 2025
- Season phase: Home-and-away season
- Team filter: All teams
- Generated: 2026-06-19 18:47 AWST
- Data mode: Synthetic/demo sample data

## Executive Snapshot
| Metric | Value |
| --- | --- |
| Games analysed | 6 |
| Average margin | 19.0 |
| Highest fixture-equity risk club | Sydney |
| Highest travel-load club | Brisbane |
| Highest commercial opportunity fixture | Carlton v Collingwood |
| Highest fan-growth opportunity fixture | Sydney v Carlton |

## Key Findings
- Fixture equity risk appears concentrated among Sydney, Brisbane, Adelaide, mainly reflecting the public-data heuristic for short-break exposure, home-away balance and away-game sequences. This may warrant review alongside commercial, stadium and broadcast constraints.
- Travel load appears highest for Brisbane, Sydney, Carlton, particularly where interstate trips, long-haul travel and shorter recovery windows overlap. Further internal review could combine this lens with player welfare, venue availability and broadcast considerations.
- Home and away balance varies across clubs, with 2 clubs showing more away than home games in the filtered dataset. This public-data model should be considered alongside commercial, stadium and broadcast objectives before drawing firm conclusions.
- Close-game frequency is currently estimated at 50%, while blowout frequency is estimated at 17%. This gives a starting point for assessing engagement windows and broadcast promotion opportunities.
- This prototype uses public data only. Recommendations should be validated with internal AFL attendance, ticketing, broadcast, digital and operations data before decisions are made.

## Priority Tables
### Fixture Equity Risk
| Club | Risk score | Short breaks | Home-away diff |
| --- | --- | --- | --- |
| Sydney | 3.5 | 1 | 0 |
| Brisbane | 3 | 1 | 0 |
| Adelaide | 1.5 | 0 | -1 |
| Fremantle | 1.5 | 0 | -1 |
| Carlton | 0 | 0 | 0 |

### Travel Load
| Club | Travel score | Interstate away | Est. km |
| --- | --- | --- | --- |
| Brisbane | 5.1 | 1 | 2,747.9 |
| Sydney | 5.1 | 1 | 1,461.9 |
| Carlton | 2.6 | 1 | 1,425.8 |
| Adelaide | 0 | 0 | 0 |
| Collingwood | 0 | 0 | 0 |

### Commercial Opportunity
| Fixture | Venue | Score | Category |
| --- | --- | --- | --- |
| Carlton v Collingwood | MCG | 70 | Marquee commercial fixture |
| West Coast v Fremantle | Optus Stadium | 64 | Marquee commercial fixture |
| Port Adelaide v Adelaide | Adelaide Oval | 41.4 | Competitive balance showcase |
| Collingwood v Brisbane | MCG | 30 | Competitive balance showcase |
| Sydney v Carlton | SCG | 29.2 | Growth market opportunity |

### Fan-Growth Opportunity
| Fixture | Venue | Score | Category |
| --- | --- | --- | --- |
| Sydney v Carlton | SCG | 46.2 | Growth market opportunity |
| Carlton v Collingwood | MCG | 35 | Marquee commercial fixture |
| Brisbane v Sydney | Gabba | 31.2 | Standard fixture |
| Port Adelaide v Adelaide | Adelaide Oval | 30 | Competitive balance showcase |
| Collingwood v Brisbane | MCG | 25 | Competitive balance showcase |

## Competitive Balance Summary
| Metric | Value |
| --- | --- |
| Games | 6 |
| Average margin | 19 |
| Median margin | 14.5 |
| Close-game rate | 50% |
| Blowout rate | 17% |

## Methodology Caveat
This brief is generated from public data and transparent heuristic scoring. It is intended to identify review priorities and demonstrate analytical thinking, not to reproduce official AFL fixture, commercial, attendance, broadcast or player-welfare models.

## Data Sources
- Generated from synthetic/demo sample dashboard data for portfolio demonstration.
- Synthetic sample attendance CSV is included only to demonstrate attendance-context workflow.
- Squiggle API for public fixture, result and ladder context.
- Maintained public venue-capacity and market-context assumptions.

## Limitations
- This sample report does not contain official AFL attendance, ticketing, commercial or broadcast data.
- Scores are transparent heuristics for review-priority ranking.
- Travel distances use approximate public team and venue geography.
- Venue capacities are maintained assumptions and may vary by event.
- Internal AFL attendance, ticketing, broadcast, commercial, digital and player-welfare data would be needed for decision-grade modelling.
