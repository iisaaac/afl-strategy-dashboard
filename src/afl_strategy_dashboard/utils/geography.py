"""Geography mappings and distance helpers for AFL teams and venues."""

from __future__ import annotations

from dataclasses import dataclass
from math import asin, cos, radians, sin, sqrt

import pandas as pd


@dataclass(frozen=True)
class Location:
    city: str
    state: str
    latitude: float | None = None
    longitude: float | None = None


CITY_LOCATIONS: dict[str, Location] = {
    "Adelaide": Location("Adelaide", "SA", -34.9285, 138.6007),
    "Alice Springs": Location("Alice Springs", "NT", -23.6980, 133.8807),
    "Brisbane": Location("Brisbane", "QLD", -27.4698, 153.0251),
    "Canberra": Location("Canberra", "ACT", -35.2809, 149.1300),
    "Darwin": Location("Darwin", "NT", -12.4634, 130.8456),
    "Geelong": Location("Geelong", "VIC", -38.1499, 144.3617),
    "Gold Coast": Location("Gold Coast", "QLD", -28.0167, 153.4000),
    "Hobart": Location("Hobart", "TAS", -42.8821, 147.3272),
    "Launceston": Location("Launceston", "TAS", -41.4332, 147.1441),
    "Melbourne": Location("Melbourne", "VIC", -37.8136, 144.9631),
    "Perth": Location("Perth", "WA", -31.9523, 115.8613),
    "Sydney": Location("Sydney", "NSW", -33.8688, 151.2093),
}


TEAM_HOME_LOCATIONS: dict[str, Location] = {
    "Adelaide": CITY_LOCATIONS["Adelaide"],
    "Adelaide Crows": CITY_LOCATIONS["Adelaide"],
    "Brisbane": CITY_LOCATIONS["Brisbane"],
    "Brisbane Lions": CITY_LOCATIONS["Brisbane"],
    "Carlton": CITY_LOCATIONS["Melbourne"],
    "Collingwood": CITY_LOCATIONS["Melbourne"],
    "Essendon": CITY_LOCATIONS["Melbourne"],
    "Footscray": CITY_LOCATIONS["Melbourne"],
    "Fremantle": CITY_LOCATIONS["Perth"],
    "Geelong": CITY_LOCATIONS["Geelong"],
    "GCFC": CITY_LOCATIONS["Gold Coast"],
    "Gold Coast": CITY_LOCATIONS["Gold Coast"],
    "Gold Coast Suns": CITY_LOCATIONS["Gold Coast"],
    "Greater Western Sydney": CITY_LOCATIONS["Sydney"],
    "GWS": CITY_LOCATIONS["Sydney"],
    "Hawthorn": CITY_LOCATIONS["Melbourne"],
    "Melbourne": CITY_LOCATIONS["Melbourne"],
    "North Melbourne": CITY_LOCATIONS["Melbourne"],
    "Port Adelaide": CITY_LOCATIONS["Adelaide"],
    "Richmond": CITY_LOCATIONS["Melbourne"],
    "St Kilda": CITY_LOCATIONS["Melbourne"],
    "Sydney": CITY_LOCATIONS["Sydney"],
    "Sydney Swans": CITY_LOCATIONS["Sydney"],
    "West Coast": CITY_LOCATIONS["Perth"],
    "West Coast Eagles": CITY_LOCATIONS["Perth"],
    "Western Bulldogs": CITY_LOCATIONS["Melbourne"],
}

VENUE_LOCATIONS: dict[str, Location] = {
    "Adelaide Oval": Location("Adelaide", "SA", -34.9156, 138.5961),
    "Bellerive Oval": Location("Hobart", "TAS", -42.8773, 147.3737),
    "Blundstone Arena": Location("Hobart", "TAS", -42.8773, 147.3737),
    "Carrara": Location("Gold Coast", "QLD", -28.0067, 153.3670),
    "Cazaly's Stadium": Location("Cairns", "QLD", -16.9340, 145.7470),
    "Docklands": Location("Melbourne", "VIC", -37.8165, 144.9475),
    "Eureka Stadium": Location("Ballarat", "VIC", -37.5400, 143.8480),
    "Gabba": Location("Brisbane", "QLD", -27.4858, 153.0381),
    "Giants Stadium": Location("Sydney", "NSW", -33.8430, 151.0672),
    "GMHBA Stadium": Location("Geelong", "VIC", -38.1582, 144.3548),
    "Kardinia Park": Location("Geelong", "VIC", -38.1582, 144.3548),
    "Manuka Oval": Location("Canberra", "ACT", -35.3182, 149.1347),
    "Marrara Oval": Location("Darwin", "NT", -12.4000, 130.8870),
    "M.C.G.": Location("Melbourne", "VIC", -37.8199, 144.9834),
    "MCG": Location("Melbourne", "VIC", -37.8199, 144.9834),
    "Marvel Stadium": Location("Melbourne", "VIC", -37.8165, 144.9475),
    "Norwood Oval": Location("Adelaide", "SA", -34.9210, 138.6330),
    "Optus Stadium": Location("Perth", "WA", -31.9510, 115.8890),
    "Perth Stadium": Location("Perth", "WA", -31.9510, 115.8890),
    "People First Stadium": Location("Gold Coast", "QLD", -28.0067, 153.3670),
    "S.C.G.": Location("Sydney", "NSW", -33.8917, 151.2249),
    "SCG": Location("Sydney", "NSW", -33.8917, 151.2249),
    "Sydney Cricket Ground": Location("Sydney", "NSW", -33.8917, 151.2249),
    "Sydney Showground": Location("Sydney", "NSW", -33.8430, 151.0672),
    "Traeger Park": Location("Alice Springs", "NT", -23.7042, 133.8806),
    "UTAS Stadium": Location("Launceston", "TAS", -41.4258, 147.1386),
    "York Park": Location("Launceston", "TAS", -41.4258, 147.1386),
}


def get_location(mapping: dict[str, Location], name: object) -> Location | None:
    """Return a mapped location by exact or case-insensitive name."""
    if not isinstance(name, str):
        return None
    if name in mapping:
        return mapping[name]
    lower_name = name.lower()
    for key, value in mapping.items():
        if key.lower() == lower_name:
            return value
    return None


def mapping_to_dataframe(
    mapping: dict[str, Location],
    name_column: str,
) -> pd.DataFrame:
    """Convert a location mapping to a DataFrame."""
    return pd.DataFrame(
        [
            {
                name_column: name,
                "city": location.city,
                "state": location.state,
                "latitude": location.latitude,
                "longitude": location.longitude,
            }
            for name, location in mapping.items()
        ]
    )


def haversine_km(origin: Location | None, destination: Location | None) -> float:
    """Calculate approximate one-way distance between two locations in kilometres."""
    if (
        origin is None
        or destination is None
        or origin.latitude is None
        or origin.longitude is None
        or destination.latitude is None
        or destination.longitude is None
    ):
        return 0.0

    earth_radius_km = 6371.0
    origin_lat = radians(origin.latitude)
    destination_lat = radians(destination.latitude)
    delta_lat = radians(destination.latitude - origin.latitude)
    delta_lon = radians(destination.longitude - origin.longitude)
    a = (
        sin(delta_lat / 2) ** 2
        + cos(origin_lat) * cos(destination_lat) * sin(delta_lon / 2) ** 2
    )
    return 2 * earth_radius_km * asin(sqrt(a))


def return_distance_km(origin: Location | None, destination: Location | None) -> float:
    """Calculate approximate return travel distance in kilometres."""
    return haversine_km(origin, destination) * 2
