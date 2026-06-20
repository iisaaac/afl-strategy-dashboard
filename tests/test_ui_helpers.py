"""Tests for pure UI helper formatting."""

from __future__ import annotations

from afl_strategy_dashboard.components.badges import (
    badge_html,
    format_opportunity_badge,
    format_risk_badge,
)
from afl_strategy_dashboard.components.layout import (
    build_context_strip_html,
    empty_state_text,
)
from afl_strategy_dashboard.components.tables import (
    compact_fixture_label,
    format_fixture_label,
    short_opportunity_category,
    shorten_opportunity_category,
)
from afl_strategy_dashboard.data.dashboard_state import average_margin_label
from afl_strategy_dashboard.styling.theme import PALETTE


def _relative_luminance(hex_colour: str) -> float:
    channels = [int(hex_colour[index : index + 2], 16) / 255 for index in (1, 3, 5)]
    linear = [
        value / 12.92 if value <= 0.04045 else ((value + 0.055) / 1.055) ** 2.4
        for value in channels
    ]
    return 0.2126 * linear[0] + 0.7152 * linear[1] + 0.0722 * linear[2]


def _contrast_ratio(foreground: str, background: str) -> float:
    lighter, darker = sorted(
        (_relative_luminance(foreground), _relative_luminance(background)),
        reverse=True,
    )
    return (lighter + 0.05) / (darker + 0.05)


def test_small_text_palette_colours_meet_wcag_aa_contrast() -> None:
    assert _contrast_ratio(PALETTE["accent"], PALETTE["background"]) >= 4.5
    assert _contrast_ratio(PALETTE["warning"], "#FFF4DE") >= 4.5


def test_badge_html_escapes_labels() -> None:
    html = badge_html("<script>alert(1)</script>", "unknown")

    assert "&lt;script&gt;" in html
    assert "afl-badge--neutral" in html


def test_risk_badge_categories() -> None:
    assert "High review priority" in format_risk_badge(25)
    assert "Monitor" in format_risk_badge(12)
    assert "Lower visible risk" in format_risk_badge(4)


def test_opportunity_badge_categories() -> None:
    assert "Premium opportunity" in format_opportunity_badge(70)
    assert "Growth opportunity" in format_opportunity_badge(40)
    assert "Standard signal" in format_opportunity_badge(20)


def test_empty_state_text_for_attendance() -> None:
    text = empty_state_text("attendance")

    assert "No attendance data is available" in text
    assert "fixture, venue, rivalry and timing signals" in text


def test_context_strip_html_escapes_values_and_compacts_status() -> None:
    html = build_context_strip_html(
        data_note="Using public Squiggle API data for 2025, with local cache enabled.",
        attendance_note="Attendance context is not enabled.",
        phase_label="Home-and-away <season>",
        selected_team="All teams & clubs",
        season=2025,
    )

    assert "context-strip" in html
    assert "Season" in html
    assert "<strong>2025</strong>" in html
    assert "<strong>Squiggle API</strong>" in html
    assert "<strong>Off</strong>" in html
    assert "Home-and-away &lt;season&gt;" in html
    assert "All teams &amp; clubs" in html
    assert "<season>" not in html


def test_average_margin_label_handles_missing_summary() -> None:
    import pandas as pd

    assert average_margin_label(pd.DataFrame()) == "n/a"


def test_compact_fixture_label_formats_home_away() -> None:
    import pandas as pd

    row = pd.Series({"home_team": "Carlton", "away_team": "Collingwood"})

    assert compact_fixture_label(row) == "Carlton v Collingwood"


def test_format_fixture_label_formats_home_away() -> None:
    assert format_fixture_label("Home", "Away") == "Home v Away"


def test_short_opportunity_category_known_labels() -> None:
    assert short_opportunity_category("Marquee commercial fixture") == "Marquee"
    assert short_opportunity_category("Growth market opportunity") == "Growth"
    assert (
        short_opportunity_category("Regional/community engagement opportunity")
        == "Regional"
    )
    assert (
        short_opportunity_category("Under-utilised attendance opportunity")
        == "Utilisation"
    )
    assert short_opportunity_category("Competitive balance showcase") == "Competitive"


def test_shorten_opportunity_category_known_labels() -> None:
    assert shorten_opportunity_category("Marquee commercial fixture") == "Marquee"
    assert shorten_opportunity_category("Growth market opportunity") == "Growth"


def test_short_opportunity_category_unknown_fallback() -> None:
    assert short_opportunity_category("Experimental audience segment") == (
        "Experimental audience..."
    )
