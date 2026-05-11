from __future__ import annotations

from typing import Any

from ..public_data_routing import build_routing_bundle
from ..source_catalog import routing_for_family
from .base import BaseMotorAdapter


# Per-tier caps prevent the routing payload from ballooning when a family
# matches many vendor sources. tier_1 (regulatory/standards) is allowed the
# most because each item is materially distinct evidence.
_INDUSTRIAL_AUTHORITY_TIER_CAPS = {1: 40, 2: 25, 3: 15}


def _build_industrial_authority_routing(asset_family: str) -> dict[str, Any]:
    """Gap D: bucket industrial sources by authority_tier for this family.

    Returns a compact projection of the 139-source catalog (tier_1 first):
      {
        "asset_family": "cold_chain_facility",
        "tier_1": [{source_id, name, publisher, citation_format}, ...],
        "tier_2": [...],
        "tier_3": [...],
        "total_sources": N,
      }

    Empty when asset_family is unknown or carries no matching entries.
    """
    if not asset_family:
        return {}
    buckets = routing_for_family(asset_family)
    projection: dict[str, Any] = {"asset_family": asset_family}
    total = 0
    for tier_int, key in ((1, "tier_1"), (2, "tier_2"), (3, "tier_3")):
        entries = buckets.get(tier_int, [])[: _INDUSTRIAL_AUTHORITY_TIER_CAPS[tier_int]]
        projection[key] = [
            {
                "source_id": e.get("source_id", ""),
                "name": e.get("name", ""),
                "publisher": e.get("publisher", ""),
                "type": e.get("type", ""),
                "topic_tags": list(e.get("topic_tags", []) or []),
                "citation_format": e.get("citation_format", ""),
            }
            for e in entries
        ]
        total += len(entries)
    projection["total_sources"] = total
    return projection


class Motor035Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_035"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_006", "motor_007"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        m1 = inputs.get("motor_001", {})
        m6 = inputs.get("motor_006", {})
        m7 = inputs.get("motor_007", {})
        identity_resolution = m6.get("asset_identity_resolution", {}) if isinstance(m6.get("asset_identity_resolution", {}), dict) else {}

        subject_definition_contract = (
            m7.get("subject_definition_contract")
            or identity_resolution.get("subject_definition_contract")
            or m1.get("subject_definition_contract")
            or {}
        )
        target_definition_contract = (
            m7.get("target_definition_contract")
            or identity_resolution.get("target_definition_contract")
            or m1.get("target_definition_contract")
            or {}
        )
        target_classification_object = m7.get("target_classification_object", {}) if isinstance(m7.get("target_classification_object", {}), dict) else {}
        observable_clusters = m7.get("observable_cluster_register", {}) if isinstance(m7.get("observable_cluster_register", {}), dict) else {}
        if not observable_clusters:
            observable_clusters = (
                identity_resolution.get("intake_observables", {}).get("observable_clusters", {})
                if isinstance(identity_resolution.get("intake_observables", {}), dict)
                else {}
            )

        bundle = build_routing_bundle(
            target_definition=target_definition_contract,
            subject_definition=subject_definition_contract,
            target_classification_object=target_classification_object,
            subject_gate_passed=bool(m7.get("subject_gate_passed")),
            technical_substrate_readiness=str(m7.get("technical_substrate_readiness") or "insufficient"),
            observable_clusters=observable_clusters,
            upstream_recommended_report_type=m7.get("recommended_report_type"),
            upstream_prohibited_report_types=list(m7.get("prohibited_report_types", []) or []),
        )

        asset_family_for_routing = (
            str(target_definition_contract.get("asset_family") or "").strip()
            or str(target_definition_contract.get("target_type") or "").strip()
        )
        industrial_authority_routing = _build_industrial_authority_routing(asset_family_for_routing)

        source_plan = bundle.get("source_routing_plan", {})
        report_switch = bundle.get("report_type_switch_recommendation", {})
        target_classification_result = bundle.get("target_classification_result", {})
        jurisdiction_resolution = bundle.get("jurisdiction_resolution", {})
        critical_field_summary = bundle.get("critical_field_summary", {})
        routing_eligibility = bundle.get("routing_eligibility", {})

        return {
            **bundle,
            "target_type_classification": target_classification_result.get("target_type"),
            "asset_type": source_plan.get("asset_type") or target_definition_contract.get("target_type", ""),
            "decision_type": routing_eligibility.get("decision_type", target_definition_contract.get("decision_intent", "target_identification")),
            "routing_ready": bool(target_classification_result.get("technical_scraping_allowed")),
            "jurisdiction_class": jurisdiction_resolution.get("jurisdiction_class", ""),
            "regulatory_stack": jurisdiction_resolution.get("regulatory_stack", []),
            "mandatory_sources": source_plan.get("mandatory_sources", []),
            "high_priority_sources": source_plan.get("high_priority_sources", []),
            "optional_sources": source_plan.get("optional_sources", []),
            "disallowed_substitutions": source_plan.get("disallowed_substitutions", []),
            "missing_critical_fields": critical_field_summary.get("missing_critical_fields", 0),
            "report_type_allowed": report_switch.get("recommended_report_type", ""),
            "report_type_prohibited": report_switch.get("prohibited_report_types", []),
            "industrial_authority_routing": industrial_authority_routing,
        }
