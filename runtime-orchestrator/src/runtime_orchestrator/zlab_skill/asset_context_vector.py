from __future__ import annotations

from typing import Any, Mapping


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalize_label(value: Any) -> str:
    text_value = _text(value).lower()
    chars: list[str] = []
    for ch in text_value:
        chars.append(ch if ch.isalnum() else " ")
    return " ".join("".join(chars).split())


def _value_from_sources(sources: list[Mapping[str, Any]], *keys: str) -> str:
    for source in sources:
        for key in keys:
            value = _text(source.get(key))
            if value:
                return value
    return ""


def _infer_solar_profile(*, orientation: str, solar_profile: str) -> str:
    explicit = _normalize_label(solar_profile)
    if explicit:
        if "morning" in explicit or "east" in explicit:
            return "morning_solar_peak"
        if "afternoon" in explicit or "west" in explicit:
            return "afternoon_solar_peak"
        return explicit.replace(" ", "_")
    orientation_label = _normalize_label(orientation)
    if "east" in orientation_label:
        return "morning_solar_peak"
    if "west" in orientation_label:
        return "afternoon_solar_peak"
    return ""


def _infer_operating_rhythm(value: str) -> str:
    label = _normalize_label(value)
    if not label:
        return ""
    if "24 7" in label or "continuous" in label:
        return "continuous_operation"
    if "early" in label or "morning" in label or "first shift" in label:
        return "early_shift_weighted"
    if "night" in label or "overnight" in label or "third shift" in label:
        return "night_shift_weighted"
    if "batch" in label:
        return "batch_operation"
    return label.replace(" ", "_")


def _infer_tariff_context(value: str) -> str:
    label = _normalize_label(value)
    if not label:
        return ""
    if "demand" in label or "kw" in label or "peak" in label:
        return "demand_sensitive_tariff"
    if "time of use" in label or "tou" in label:
        return "time_of_use_tariff"
    return label.replace(" ", "_")


def _infer_control_boundary(value: str) -> str:
    label = _normalize_label(value)
    if not label:
        return ""
    if any(term in label for term in ("owner operator", "tenant", "landlord", "split incentive", "lease")):
        return "owner_operator_split"
    if "single owner operator" in label or "fully aligned" in label:
        return "aligned_single_operator"
    return label.replace(" ", "_")


def _token(value: str, fallback: str = "unknown") -> str:
    label = _normalize_label(value).replace(" ", "_")
    return label or fallback


def build_asset_context_vector(
    *,
    asset_family_research_profile: Mapping[str, Any] | None = None,
    runtime_context: Mapping[str, Any] | None = None,
    motor_051_output: Mapping[str, Any] | None = None,
    motor_052_output: Mapping[str, Any] | None = None,
    motor_053_output: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    profile = dict(asset_family_research_profile or {})
    runtime = dict(runtime_context or {})
    m51 = dict(motor_051_output or {})
    m52 = dict(motor_052_output or {})
    m53 = dict(motor_053_output or {})
    sources = [runtime, profile]

    asset_family = (
        _value_from_sources(sources, "asset_family", "target_type_hint", "target_type")
        or _text((m51.get("fair_comparison_profile", {}) or {}).get("asset_family"))
    )
    geography = _value_from_sources(sources, "geography", "jurisdiction", "location", "address_raw")
    climate_zone = _value_from_sources(sources, "climate_zone", "climate", "weather_zone")
    orientation = _value_from_sources(sources, "orientation", "facade_orientation", "solar_exposure")
    solar_profile = _infer_solar_profile(
        orientation=orientation,
        solar_profile=_value_from_sources(sources, "solar_profile", "solar_gain_profile", "solar_timing"),
    )
    operating_rhythm = _infer_operating_rhythm(
        _value_from_sources(sources, "operating_rhythm", "schedule_profile", "shift_profile", "occupancy_profile")
    )
    utility_tariff_context = _infer_tariff_context(
        _value_from_sources(sources, "utility_tariff_context", "tariff_profile", "rate_structure")
    )
    control_boundary = _infer_control_boundary(
        _value_from_sources(sources, "control_boundary", "owner_operator_split", "lease_boundary")
    )
    service_intensity = _value_from_sources(sources, "service_intensity", "service_level_intensity", "throughput_profile")
    evidence_maturity = _value_from_sources(sources, "evidence_maturity", "asset_context_readiness", "evidence_mode_state")

    if not utility_tariff_context and list(m52.get("activated_pattern_register", []) or []):
        pattern_names = " ".join(
            _normalize_label(row.get("pattern_name"))
            for row in list(m52.get("activated_pattern_register", []) or [])
        )
        if any(term in pattern_names for term in ("charging", "demand spike", "forklift", "schedule")):
            utility_tariff_context = "demand_sensitive_tariff"

    if not control_boundary and list(m53.get("value_leakage_register", []) or []):
        control_boundary = "owner_operator_split"

    dimensions = {
        "asset_family": asset_family,
        "geography": geography,
        "climate_zone": climate_zone,
        "orientation": orientation,
        "solar_profile": solar_profile,
        "operating_rhythm": operating_rhythm,
        "utility_tariff_context": utility_tariff_context,
        "control_boundary": control_boundary,
        "service_intensity": service_intensity,
        "evidence_maturity": evidence_maturity,
    }
    populated_dimensions = [key for key, value in dimensions.items() if _text(value)]
    context_signature = "|".join(
        [
            f"family:{_token(asset_family)}",
            f"solar:{_token(solar_profile)}",
            f"ops:{_token(operating_rhythm)}",
            f"tariff:{_token(utility_tariff_context)}",
            f"boundary:{_token(control_boundary)}",
            f"service:{_token(service_intensity)}",
        ]
    )
    return {
        **dimensions,
        "context_signature": context_signature,
        "context_specificity_score": len(populated_dimensions),
        "populated_dimensions": populated_dimensions,
    }


def build_context_differentiator_register(
    *,
    asset_context_vector: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    vector = dict(asset_context_vector or {})
    rows: list[dict[str, Any]] = []

    def _push(dimension: str, signal: str, implication: str) -> None:
        rows.append({"dimension": dimension, "signal": signal, "implication": implication})

    solar_profile = _text(vector.get("solar_profile"))
    if solar_profile == "morning_solar_peak":
        _push("solar_profile", solar_profile, "Morning solar timing may change thermal peak and occupancy overlap.")
    elif solar_profile == "afternoon_solar_peak":
        _push("solar_profile", solar_profile, "Afternoon solar timing may shift thermal peak later and alter demand overlap.")

    operating_rhythm = _text(vector.get("operating_rhythm"))
    if operating_rhythm == "early_shift_weighted":
        _push("operating_rhythm", operating_rhythm, "Early-shift operation changes when schedule, charging, and solar effects overlap.")
    elif operating_rhythm == "night_shift_weighted":
        _push("operating_rhythm", operating_rhythm, "Night-weighted operation changes the relevance of daytime climate and tariff windows.")
    elif operating_rhythm == "continuous_operation":
        _push("operating_rhythm", operating_rhythm, "Continuous operation weakens simplistic after-hours narratives.")

    utility_tariff_context = _text(vector.get("utility_tariff_context"))
    if utility_tariff_context == "demand_sensitive_tariff":
        _push("utility_tariff_context", utility_tariff_context, "Demand-sensitive billing changes the priority of timing and overlap versus annual kWh alone.")
    elif utility_tariff_context == "time_of_use_tariff":
        _push("utility_tariff_context", utility_tariff_context, "Time-of-use exposure changes the relevance of schedule and temporal load shaping.")

    control_boundary = _text(vector.get("control_boundary"))
    if control_boundary == "owner_operator_split":
        _push("control_boundary", control_boundary, "Owner/operator split changes who controls and captures the value driver.")

    service_intensity = _text(vector.get("service_intensity"))
    if service_intensity:
        _push("service_intensity", service_intensity, "Service or throughput intensity changes whether generic comparisons remain meaningful.")

    return rows
