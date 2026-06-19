# Architecture

```mermaid
flowchart TD
    A["Squiggle API<br/>Optional local attendance CSV"] --> B["data<br/>Cache + normalisation layer"]
    B --> C["features<br/>Fixture equity<br/>Travel load<br/>Competitive balance<br/>Fan-growth and commercial scoring"]
    C --> D["insights<br/>Recommendation engine"]
    C --> E["visualisation<br/>Plotly chart helpers"]
    D --> F["pages<br/>Streamlit multipage dashboard"]
    E --> F
    G["components<br/>Reusable cards, tables, badges and narrative blocks"] --> F
    H["styling<br/>Streamlit CSS theme + Plotly template"] --> F
    F --> I["reporting<br/>HTML / Markdown executive brief export"]
```

## Major Modules

- `data`: Squiggle client, local caching, attendance CSV support and dashboard state assembly.
- `features`: public-data fixture equity, travel load, competitive balance, fan-growth and commercial scoring.
- `insights`: cautious executive recommendation generation.
- `visualisation`: Plotly chart helpers using the shared dashboard template.
- `pages`: multipage Streamlit interface.
- `reporting`: executive brief context, HTML rendering and Markdown rendering.
- `components`: reusable UI cards, badges, layout, tables and narrative blocks.
- `styling`: Streamlit CSS theme and Plotly template.
