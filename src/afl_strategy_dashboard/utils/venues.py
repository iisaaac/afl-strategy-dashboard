"""Venue capacity and market-context assumptions.

Capacities are approximate public-data assumptions for portfolio analysis.
Actual event capacity can vary by configuration, construction works, ticketing
holds and event operations.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd


@dataclass(frozen=True)
class VenueInfo:
    venue: str
    canonical_venue: str
    city: str
    state: str
    capacity: int | None
    is_major_stadium: bool
    is_regional_or_special_event: bool
    market_type: str


VENUE_INFO: dict[str, VenueInfo] = {
    "MCG": VenueInfo(
        "MCG", "MCG", "Melbourne", "VIC", 100_000, True, False, "traditional_major"
    ),
    "M.C.G.": VenueInfo(
        "M.C.G.", "MCG", "Melbourne", "VIC", 100_000, True, False, "traditional_major"
    ),
    "Marvel Stadium": VenueInfo(
        "Marvel Stadium",
        "Marvel Stadium",
        "Melbourne",
        "VIC",
        53_000,
        True,
        False,
        "traditional_major",
    ),
    "Docklands": VenueInfo(
        "Docklands",
        "Marvel Stadium",
        "Melbourne",
        "VIC",
        53_000,
        True,
        False,
        "traditional_major",
    ),
    "GMHBA Stadium": VenueInfo(
        "GMHBA Stadium",
        "GMHBA Stadium",
        "Geelong",
        "VIC",
        40_000,
        False,
        False,
        "traditional_regional",
    ),
    "Kardinia Park": VenueInfo(
        "Kardinia Park",
        "GMHBA Stadium",
        "Geelong",
        "VIC",
        40_000,
        False,
        False,
        "traditional_regional",
    ),
    "Adelaide Oval": VenueInfo(
        "Adelaide Oval",
        "Adelaide Oval",
        "Adelaide",
        "SA",
        53_500,
        True,
        False,
        "traditional_major",
    ),
    "Optus Stadium": VenueInfo(
        "Optus Stadium",
        "Optus Stadium",
        "Perth",
        "WA",
        60_000,
        True,
        False,
        "traditional_major",
    ),
    "Perth Stadium": VenueInfo(
        "Perth Stadium",
        "Optus Stadium",
        "Perth",
        "WA",
        60_000,
        True,
        False,
        "traditional_major",
    ),
    "Gabba": VenueInfo(
        "Gabba", "Gabba", "Brisbane", "QLD", 37_000, True, False, "growth_market"
    ),
    "Carrara": VenueInfo(
        "Carrara",
        "Carrara",
        "Gold Coast",
        "QLD",
        25_000,
        False,
        False,
        "growth_market",
    ),
    "People First Stadium": VenueInfo(
        "People First Stadium",
        "Carrara",
        "Gold Coast",
        "QLD",
        25_000,
        False,
        False,
        "growth_market",
    ),
    "SCG": VenueInfo(
        "SCG", "SCG", "Sydney", "NSW", 48_000, True, False, "growth_market"
    ),
    "S.C.G.": VenueInfo(
        "S.C.G.", "SCG", "Sydney", "NSW", 48_000, True, False, "growth_market"
    ),
    "Sydney Cricket Ground": VenueInfo(
        "Sydney Cricket Ground",
        "SCG",
        "Sydney",
        "NSW",
        48_000,
        True,
        False,
        "growth_market",
    ),
    "Giants Stadium": VenueInfo(
        "Giants Stadium",
        "Giants Stadium",
        "Sydney",
        "NSW",
        24_000,
        False,
        False,
        "growth_market",
    ),
    "Sydney Showground": VenueInfo(
        "Sydney Showground",
        "Giants Stadium",
        "Sydney",
        "NSW",
        24_000,
        False,
        False,
        "growth_market",
    ),
    "Manuka Oval": VenueInfo(
        "Manuka Oval",
        "Manuka Oval",
        "Canberra",
        "ACT",
        13_500,
        False,
        True,
        "special_event",
    ),
    "UTAS Stadium": VenueInfo(
        "UTAS Stadium",
        "UTAS Stadium",
        "Launceston",
        "TAS",
        20_000,
        False,
        True,
        "special_event",
    ),
    "York Park": VenueInfo(
        "York Park",
        "UTAS Stadium",
        "Launceston",
        "TAS",
        20_000,
        False,
        True,
        "special_event",
    ),
    "Bellerive Oval": VenueInfo(
        "Bellerive Oval",
        "Bellerive Oval",
        "Hobart",
        "TAS",
        20_000,
        False,
        True,
        "special_event",
    ),
    "Blundstone Arena": VenueInfo(
        "Blundstone Arena",
        "Bellerive Oval",
        "Hobart",
        "TAS",
        20_000,
        False,
        True,
        "special_event",
    ),
    "Marrara Oval": VenueInfo(
        "Marrara Oval",
        "Marrara Oval",
        "Darwin",
        "NT",
        12_500,
        False,
        True,
        "special_event",
    ),
    "Traeger Park": VenueInfo(
        "Traeger Park",
        "Traeger Park",
        "Alice Springs",
        "NT",
        10_000,
        False,
        True,
        "special_event",
    ),
    "Norwood Oval": VenueInfo(
        "Norwood Oval",
        "Norwood Oval",
        "Adelaide",
        "SA",
        15_000,
        False,
        True,
        "special_event",
    ),
    "Barossa Park": VenueInfo(
        "Barossa Park",
        "Barossa Park",
        "Barossa",
        "SA",
        8_000,
        False,
        True,
        "special_event",
    ),
    "Stadium Australia": VenueInfo(
        "Stadium Australia",
        "Stadium Australia",
        "Sydney",
        "NSW",
        83_500,
        True,
        False,
        "growth_market",
    ),
}


def normalise_venue_name(name: object) -> str:
    """Return a canonical venue name where known."""
    if not isinstance(name, str) or not name.strip():
        return ""
    stripped = " ".join(name.strip().split())
    if stripped in VENUE_INFO:
        return VENUE_INFO[stripped].canonical_venue
    lower_name = stripped.lower()
    for venue, info in VENUE_INFO.items():
        if venue.lower() == lower_name or info.canonical_venue.lower() == lower_name:
            return info.canonical_venue
    return stripped


def get_venue_info(venue: object) -> VenueInfo | None:
    """Return venue information by alias or canonical name."""
    canonical = normalise_venue_name(venue)
    for info in VENUE_INFO.values():
        if info.canonical_venue == canonical:
            return info
    return None


def get_venue_capacity(venue: str) -> int | None:
    """Return an approximate venue capacity where mapped."""
    info = get_venue_info(venue)
    return info.capacity if info else None


def get_venue_market_type(venue: str) -> str | None:
    """Return the venue market type where mapped."""
    info = get_venue_info(venue)
    return info.market_type if info else None


def is_regional_or_special_event_venue(venue: str) -> bool:
    """Return whether the venue is treated as regional or special-event."""
    info = get_venue_info(venue)
    return bool(info and info.is_regional_or_special_event)


def is_major_stadium(venue: str) -> bool:
    """Return whether the venue is treated as a major stadium."""
    info = get_venue_info(venue)
    return bool(info and info.is_major_stadium)


def venue_mapping_dataframe() -> pd.DataFrame:
    """Return venue mapping assumptions as a DataFrame."""
    unique_infos = {info.canonical_venue: info for info in VENUE_INFO.values()}
    return pd.DataFrame([info.__dict__ for info in unique_infos.values()])
