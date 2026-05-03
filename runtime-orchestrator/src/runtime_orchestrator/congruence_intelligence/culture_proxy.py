from __future__ import annotations

from typing import Any

from .schemas import text


def _source_family_set(source_register: list[dict[str, Any]]) -> set[str]:
    return {
        text(row.get("source_family"))
        for row in source_register
        if text(row.get("source_family"))
    }


def build_culture_execution_proxy_register(
    *,
    asset_family_research_profile: dict[str, Any],
    operational_intake_pack: dict[str, Any],
    source_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    if text(asset_family_research_profile.get("route_state")) != "operational_asset_candidate":
        return []

    source_families = _source_family_set(source_register)
    maintenance_state = text((operational_intake_pack.get("maintenance_maturity_pack", {}) or {}).get("current_state"))
    schedule_state = text((operational_intake_pack.get("schedule_and_utilization_pack", {}) or {}).get("current_state"))
    evidence_state = "WEAK_SIGNAL"
    if {"operator_input_record", "cmms_record", "maintenance_log_record"} & source_families:
        evidence_state = "CONDITIONAL_HYPOTHESIS"
    return [
        {
            "proxy_name": "execution_discipline_proxy",
            "proxy_signal": "The case may have stronger or weaker operational ownership depending on whether schedule, maintenance and basic operating records are surfaced.",
            "evidence_state": evidence_state,
            "why_it_matters": "Missing ownership of maintenance, schedule or utility evidence can itself be a structural bottleneck.",
            "supporting_context": {
                "maintenance_state": maintenance_state or "not_yet_evidenced",
                "schedule_state": schedule_state or "not_yet_evidenced",
            },
            "allowed_use": "Use as a weak or conditional proxy for execution discipline.",
            "prohibited_use": "Do not claim strong or weak culture as observed fact without direct organizational evidence.",
        }
    ]
