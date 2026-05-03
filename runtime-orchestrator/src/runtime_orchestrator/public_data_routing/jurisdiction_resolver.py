from __future__ import annotations

from .schemas import AssetType, JurisdictionClass, JurisdictionResolution
from .target_taxonomy import normalize_asset_type


STATE_ALIASES = {
    "NEW YORK": "NY",
    "NY": "NY",
    "CALIFORNIA": "CA",
    "CA": "CA",
    "TEXAS": "TX",
    "TX": "TX",
}


def _normalize_state_code(value: str | None) -> str:
    return STATE_ALIASES.get(str(value or "").strip().upper(), str(value or "").strip().upper())


def _normalize_city(value: str | None) -> str:
    raw = str(value or "").strip().upper()
    aliases = {
        "NYC": "NEW YORK",
        "NEW YORK CITY": "NEW YORK",
        "SAN FRANCISCO": "SAN FRANCISCO",
        "SF": "SAN FRANCISCO",
        "LOS ANGELES": "LOS ANGELES",
        "LA": "LOS ANGELES",
        "OAKLAND": "OAKLAND",
        "SAN DIEGO": "SAN DIEGO",
        "SAN JOSE": "SAN JOSE",
        "BERKELEY": "BERKELEY",
        "HOUSTON": "HOUSTON",
        "AUSTIN": "AUSTIN",
        "DALLAS": "DALLAS",
        "TEMPLE": "TEMPLE",
    }
    return aliases.get(raw, raw.title().upper()).title()


def _industrial_like(asset_type: AssetType | str | None) -> bool:
    normalized = normalize_asset_type(asset_type)
    return normalized == AssetType.INDUSTRIAL_FACILITY


def resolve_us_jurisdiction(
    *,
    state: str | None,
    city: str | None,
    county: str | None = None,
    asset_type: AssetType | str | None = None,
) -> JurisdictionResolution:
    state_code = _normalize_state_code(state)
    city_name = _normalize_city(city)
    county_name = str(county or "").strip()
    industrial_like = _industrial_like(asset_type)

    if state_code == "NY" and city_name == "New York":
        return JurisdictionResolution(
            country="US",
            state="NY",
            city="New York",
            county=county_name or "New York County",
            utility_territory="ConEdison",
            climate_zone_ashrae="4A",
            jurisdiction_class=JurisdictionClass.HIGH_DATA_AVAILABILITY_BUILDING,
            regulatory_stack=[
                "NYC LL84 benchmarking",
                "NYC LL97 covered buildings",
                "NYC DOB permits and filings",
                "NYC DOF / BBL property anchor",
            ],
        )

    if state_code == "CA" and city_name == "San Francisco":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city="San Francisco",
            county=county_name or "San Francisco County",
            utility_territory="PG&E",
            climate_zone_ashrae="3C",
            jurisdiction_class=JurisdictionClass.HIGH_DATA_AVAILABILITY_BUILDING,
            regulatory_stack=[
                "San Francisco Existing Buildings benchmarking",
                "Title 24",
                "CALGreen",
                "California utility and permitting context",
            ],
        )

    if state_code == "CA" and city_name == "Los Angeles":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city="Los Angeles",
            county=county_name or "Los Angeles County",
            utility_territory="LADWP_or_SCE",
            climate_zone_ashrae="3B",
            jurisdiction_class=JurisdictionClass.HIGH_DATA_AVAILABILITY_BUILDING,
            regulatory_stack=[
                "Los Angeles EBEWE benchmarking",
                "Title 24",
                "CALGreen",
                "California utility and permitting context",
            ],
        )

    if state_code == "CA" and city_name == "Berkeley":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city="Berkeley",
            county=county_name or "Alameda County",
            utility_territory="PG&E",
            climate_zone_ashrae="3C",
            jurisdiction_class=JurisdictionClass.HIGH_DATA_AVAILABILITY_BUILDING,
            regulatory_stack=[
                "Berkeley benchmarking or building performance routing",
                "Title 24",
                "CALGreen",
            ],
        )

    if state_code == "CA" and city_name == "Oakland":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city="Oakland",
            county=county_name or "Alameda County",
            utility_territory="PG&E",
            climate_zone_ashrae="3C",
            jurisdiction_class=JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=[
                "Alameda County property-search routing",
                "Oakland permit portal routing",
                "Title 24",
                "CALGreen",
                "PG&E utility context",
            ],
        )

    if state_code == "CA" and city_name == "San Jose":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city="San Jose",
            county=county_name or "Santa Clara County",
            utility_territory="PG&E",
            climate_zone_ashrae="3C",
            jurisdiction_class=JurisdictionClass.HIGH_DATA_AVAILABILITY_BUILDING,
            regulatory_stack=[
                "San Jose benchmarking or local building-performance routing",
                "Title 24",
                "CALGreen",
            ],
        )

    if state_code == "CA" and city_name == "San Diego":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city="San Diego",
            county=county_name or "San Diego County",
            utility_territory="SDG&E",
            climate_zone_ashrae="3B",
            jurisdiction_class=JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=[
                "San Diego permit portal routing",
                "Title 24",
                "CALGreen",
                "SDG&E utility context",
            ],
        )

    if state_code == "TX" and city_name == "Houston":
        return JurisdictionResolution(
            country="US",
            state="TX",
            city="Houston",
            county=county_name or "Harris County",
            utility_territory="CenterPoint_or_ERCOT",
            climate_zone_ashrae="2A",
            jurisdiction_class=JurisdictionClass.INDUSTRIAL_REGULATED if industrial_like else JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=[
                "ERCOT market and load context",
                "TCEQ permits and emissions",
                "County appraisal district property anchor",
                "City permitting context",
            ],
        )

    if state_code == "TX" and city_name == "Austin":
        return JurisdictionResolution(
            country="US",
            state="TX",
            city="Austin",
            county=county_name or "Travis County",
            utility_territory="Austin_Energy_or_ERCOT",
            climate_zone_ashrae="2A",
            jurisdiction_class=JurisdictionClass.INDUSTRIAL_REGULATED if industrial_like else JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=[
                "Austin Energy or ERCOT utility context",
                "County appraisal routing",
                "City permitting context",
                "TCEQ permits and emissions",
            ],
        )

    if state_code == "TX" and city_name == "Dallas":
        return JurisdictionResolution(
            country="US",
            state="TX",
            city="Dallas",
            county=county_name or "Dallas County",
            utility_territory="Oncor_or_ERCOT",
            climate_zone_ashrae="3A",
            jurisdiction_class=JurisdictionClass.INDUSTRIAL_REGULATED if industrial_like else JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=[
                "Oncor or ERCOT utility context",
                "County appraisal routing",
                "City permitting context",
                "TCEQ permits and emissions",
            ],
        )

    if state_code == "TX" and city_name == "Temple":
        return JurisdictionResolution(
            country="US",
            state="TX",
            city="Temple",
            county=county_name or "Bell County",
            utility_territory="TX_utility_territory_unresolved",
            climate_zone_ashrae="2A",
            jurisdiction_class=JurisdictionClass.INDUSTRIAL_REGULATED if industrial_like else JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=[
                "Bell County appraisal district property-search routing",
                "ERCOT or local utility context",
                "City permitting or records context",
                "TCEQ permits and emissions",
            ],
        )

    if state_code == "CA":
        return JurisdictionResolution(
            country="US",
            state="CA",
            city=city_name or "Unknown",
            county=county_name or "Unknown",
            utility_territory="CA_utility_territory_unresolved",
            climate_zone_ashrae="unknown",
            jurisdiction_class=JurisdictionClass.INDUSTRIAL_REGULATED if industrial_like else JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=["CEC benchmarking", "Title 24", "CALGreen", "CPUC utility context"],
        )

    if state_code == "TX":
        return JurisdictionResolution(
            country="US",
            state="TX",
            city=city_name or "Unknown",
            county=county_name or "Unknown",
            utility_territory="TX_utility_territory_unresolved",
            climate_zone_ashrae="unknown",
            jurisdiction_class=JurisdictionClass.INDUSTRIAL_REGULATED if industrial_like else JurisdictionClass.UTILITY_AND_PERMIT_BUILDING,
            regulatory_stack=["ERCOT", "TCEQ", "County appraisal district", "City permits"],
        )

    if state_code == "NY":
        return JurisdictionResolution(
            country="US",
            state="NY",
            city=city_name or "Unknown",
            county=county_name or "Unknown",
            utility_territory="NY_utility_territory_unresolved",
            climate_zone_ashrae="unknown",
            jurisdiction_class=JurisdictionClass.LOW_PUBLIC_DATA_ASSET,
            regulatory_stack=["State and local property or permitting context"],
        )

    return JurisdictionResolution(
        country="US",
        state=state_code or "UNKNOWN",
        city=city_name or "Unknown",
        county=county_name or "Unknown",
        utility_territory="unresolved",
        climate_zone_ashrae="unknown",
        jurisdiction_class=JurisdictionClass.AMBIGUOUS_JURISDICTION,
        regulatory_stack=[],
    )


def routing_keys_for_resolution(
    resolution: JurisdictionResolution,
    asset_type: AssetType | str | None = None,
) -> list[str]:
    keys = ["US"]
    normalized = normalize_asset_type(asset_type)

    if resolution.state == "NY" and resolution.city == "New York":
        keys.append("US-NY-NYC")
    elif resolution.state == "CA":
        keys.append("US-CA")
        if resolution.city == "San Francisco":
            keys.append("US-CA-SF")
        elif resolution.city == "Los Angeles":
            keys.append("US-CA-LA")
        elif resolution.city == "Berkeley":
            keys.append("US-CA-BERKELEY")
        elif resolution.city == "Oakland":
            keys.append("US-CA-OAKLAND")
        elif resolution.city == "San Jose":
            keys.append("US-CA-SANJOSE")
        elif resolution.city == "San Diego":
            keys.append("US-CA-SANDIEGO")
    elif resolution.state == "TX":
        keys.append("US-TX")
        if resolution.city == "Houston":
            keys.append("US-TX-HOUSTON")
        elif resolution.city == "Austin":
            keys.append("US-TX-AUSTIN")
        elif resolution.city == "Dallas":
            keys.append("US-TX-DALLAS")
        elif resolution.city == "Temple":
            keys.append("US-TX-TEMPLE")

    if normalized == AssetType.INDUSTRIAL_FACILITY:
        keys.append("US-INDUSTRIAL")

    return keys
