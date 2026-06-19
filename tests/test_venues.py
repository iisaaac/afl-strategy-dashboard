from afl_strategy_dashboard.utils.venues import (
    get_venue_capacity,
    get_venue_info,
    get_venue_market_type,
    is_regional_or_special_event_venue,
    normalise_venue_name,
)


def test_venue_name_normalisation() -> None:
    assert normalise_venue_name("M.C.G.") == "MCG"
    assert normalise_venue_name("Sydney Showground") == "Giants Stadium"


def test_venue_capacity_lookup() -> None:
    assert get_venue_capacity("MCG") == 100000
    assert get_venue_capacity("Unknown Ground") is None


def test_regional_and_growth_market_classification() -> None:
    assert is_regional_or_special_event_venue("Traeger Park") is True
    assert get_venue_market_type("Carrara") == "growth_market"
    assert get_venue_info("Adelaide Oval").is_major_stadium is True
