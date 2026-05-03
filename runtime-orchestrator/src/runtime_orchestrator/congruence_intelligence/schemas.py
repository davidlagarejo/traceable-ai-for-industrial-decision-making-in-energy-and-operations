from __future__ import annotations

from typing import Any

RESEARCH_MODES = (
    "public_only_screening",
    "hybrid_diligence",
    "operator_integrated_congruence",
)

ASSET_FAMILIES = (
    "commercial_building",
    "industrial_manufacturing",
    "logistics_warehouse",
    "cold_chain",
    "thermal_process_site",
    "infrastructure_node",
    "utility_heavy_site",
    "generic_operational_asset",
)

SOURCE_TIERS = (
    "tier_1_authoritative_public",
    "tier_local_operator_evidence",
    "tier_2_sectoral_guidance",
    "tier_3_vendor_or_secondary",
)

INTAKE_PACK_STATES = (
    "not_primary",
    "public_context_only",
    "requested_but_absent",
    "uploaded_but_unparsed",
    "parsed_but_weak",
    "partially_evidenced",
    "evidenced",
)

DILIGENCE_PACK_NAMES = (
    "utility_bill_pack",
    "utility_tariff_pack",
    "throughput_schedule_pack",
    "equipment_inventory_pack",
    "metering_boundary_pack",
    "lease_responsibility_pack",
    "maintenance_proof_pack",
    "bms_or_controls_pack",
    "cmms_or_workorder_pack",
    "permit_detail_pack",
)


def text(value: Any) -> str:
    return str(value or "").strip()


def list_text(values: Any) -> list[str]:
    if isinstance(values, list):
        return [text(value) for value in values if text(value)]
    single = text(values)
    return [single] if single else []


def dedupe(values: list[str]) -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for value in values:
        normalized = text(value)
        if not normalized or normalized in seen:
            continue
        seen.add(normalized)
        out.append(normalized)
    return out


def build_diligence_pack(
    *,
    pack_name: str,
    current_state: str,
    decision_relevance: str,
    expected_local_sources: list[str] | None = None,
    present_source_families: list[str] | None = None,
    binding_needed: list[str] | None = None,
    family_specific_focus: str = "",
    allowed_without_local_binding: list[str] | None = None,
) -> dict[str, Any]:
    return {
        "pack_name": text(pack_name),
        "current_state": text(current_state),
        "decision_relevance": text(decision_relevance),
        "expected_local_sources": dedupe(list_text(expected_local_sources or [])),
        "present_source_families": dedupe(list_text(present_source_families or [])),
        "binding_needed": dedupe(list_text(binding_needed or [])),
        "family_specific_focus": text(family_specific_focus),
        "allowed_without_local_binding": dedupe(list_text(allowed_without_local_binding or [])),
    }
