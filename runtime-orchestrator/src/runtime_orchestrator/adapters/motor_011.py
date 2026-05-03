"""Adapter for motor_011 — Scope-Aware Library Curation Engine.

Curates deduplicated objects into a library that carries:

- entity typing
- scope boundary
- default field target
- admissibility default
- contamination sensitivity
"""
from __future__ import annotations

from typing import Any

from .base import BaseMotorAdapter

_TERM_TO_ENTITY_TYPE = {
    "facility_prior": "Facility",
    "Class_A_trophy": "Facility",
    "REIT": "Organization",
    "NOI": "FinancialMetric",
    "cap_rate": "FinancialMetric",
    "FFO": "FinancialMetric",
    "LTV": "FinancialMetric",
    "occupancy_rate": "OperationalMetric",
    "tenant_concentration": "RiskFactor",
    "LL97_compliance": "RegulatoryContext",
    "LEED_Gold": "CertificationContext",
    "vintage_risk": "RiskFactor",
    "observatory_revenue": "RevenueStream",
    "ASHRAE_4A": "ClimateContext",
    "sq_ft": "SizeMetric",
    "SEC_EDGAR": "DataSource",
    "validation_urgency": "AnalyticalPriority",
    "evidence_gap": "AnalyticalGap",
    "CapEx": "FinancialMetric",
    "inference_case": "AnalyticalUnit",
}


def _classify_entity_type(canonical_terms: list[str]) -> str:
    for term in canonical_terms:
        if term in _TERM_TO_ENTITY_TYPE:
            return _TERM_TO_ENTITY_TYPE[term]
    return "GenericObject"


def _scope_boundary(entity: dict[str, Any], dedup_obj: dict[str, Any]) -> str:
    return str(
        entity.get("scope_boundary")
        or dedup_obj.get("source_scope")
        or entity.get("source_scope")
        or "UNKNOWN_SCOPE"
    ).strip().upper()


def _field_target(entity_type: str, scope_boundary: str, canonical_terms: list[str]) -> str:
    if scope_boundary == "ENTITY_LEVEL":
        return "issuer_context"
    if scope_boundary == "PORTFOLIO_LEVEL":
        return "portfolio_context"
    if scope_boundary == "JURISDICTION_LEVEL":
        return "jurisdiction_context"
    if scope_boundary == "BENCHMARK_LEVEL":
        return "benchmark_context"
    if entity_type == "Facility":
        return "asset_identity"
    if entity_type == "SizeMetric":
        return "geometry_size"
    if entity_type == "OperationalMetric":
        return "operating_regime"
    if entity_type == "ClimateContext":
        return "climate_context"
    if entity_type == "RegulatoryContext":
        return "regulatory_applicability"
    if entity_type == "CertificationContext":
        return "asset_performance_record"
    if entity_type in {"RiskFactor", "AnalyticalGap"}:
        return "evidence_gap"
    if "sq_ft" in canonical_terms:
        return "geometry_size"
    return "asset_context"


def _admissibility_default(scope_boundary: str, confidence_tier: str, asset_level_eligible: bool) -> str:
    if scope_boundary == "ENTITY_LEVEL":
        return "ENTITY_CONTEXT_ONLY"
    if scope_boundary == "PORTFOLIO_LEVEL":
        return "PORTFOLIO_CONTEXT_ONLY"
    if scope_boundary == "JURISDICTION_LEVEL":
        return "JURISDICTION_CONTEXT_ONLY"
    if scope_boundary == "BENCHMARK_LEVEL":
        return "BENCHMARK_ONLY"
    if not asset_level_eligible:
        return "INFERRED_ASSET_LEVEL"
    if confidence_tier == "high":
        return "CONFIRMED_ASSET_LEVEL"
    if confidence_tier == "medium":
        return "OBSERVED_PUBLIC_ASSET_LEVEL"
    return "INFERRED_ASSET_LEVEL"


def _contamination_sensitivity(scope_boundary: str, field_target: str) -> str:
    if scope_boundary in {"ASSET_LEVEL", "JURISDICTION_LEVEL"}:
        return "high"
    if field_target in {"asset_identity", "regulatory_applicability", "geometry_size"}:
        return "high"
    if scope_boundary in {"ENTITY_LEVEL", "PORTFOLIO_LEVEL"}:
        return "medium"
    return "low"


class Motor011Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_011"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_003", "motor_005", "motor_006", "motor_007", "motor_008", "motor_010"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        term_index = inputs.get("motor_003", {}).get("term_index", {})
        evaluated = inputs.get("motor_007", {}).get("evaluated_entities", [])
        dedup_objects = inputs.get("motor_010", {}).get("dedup_objects", [])
        source_registry = inputs.get("motor_008", {}).get("source_registry", {})

        dedup_index = {o.get("source_id", ""): o for o in dedup_objects}
        library_objects: list[dict[str, Any]] = []
        library_by_type: dict[str, list[str]] = {}
        library_by_scope: dict[str, list[str]] = {}
        admissibility_counts: dict[str, int] = {}

        for entity in evaluated:
            if entity.get("fitness_status") == "unfit":
                continue

            sid = entity.get("source_id", "")
            canonical_terms = entity.get("resolved_terms", entity.get("canonical_terms", []))
            entity_type = _classify_entity_type(canonical_terms)
            fitness = entity.get("fitness_score", 0.0)
            confidence_tier = "high" if fitness >= 0.8 else "medium" if fitness >= 0.5 else "low"
            dedup_obj = dedup_index.get(sid, {})
            source_profile = source_registry.get(sid, {}) if isinstance(source_registry, dict) else {}
            scope_boundary = _scope_boundary(entity, dedup_obj)
            field_target = _field_target(entity_type, scope_boundary, canonical_terms)
            asset_level_eligible = bool(
                dedup_obj.get("source_scope") == "ASSET_LEVEL"
                or source_profile.get("asset_level_eligible")
            )
            admissibility_default = _admissibility_default(scope_boundary, confidence_tier, asset_level_eligible)
            contamination_sensitivity = _contamination_sensitivity(scope_boundary, field_target)

            content = dedup_obj.get("parsed_content", entity.get("parsed_content", {}))
            lib_obj = {
                "library_object_id": f"lib:{entity.get('entity_id', sid)}",
                "source_id": sid,
                "entity_id": entity.get("entity_id", ""),
                "entity_type": entity_type,
                "canonical_terms": canonical_terms,
                "confidence_tier": confidence_tier,
                "fitness_score": fitness,
                "fitness_status": entity.get("fitness_status"),
                "content_ref": content,
                "metadata": entity.get("metadata", {}),
                "scope_boundary": scope_boundary,
                "field_target": field_target,
                "admissibility_default": admissibility_default,
                "contamination_sensitivity": contamination_sensitivity,
                "source_authority_score": dedup_obj.get("source_authority_score") or source_profile.get("authority_score", ""),
                "source_family": dedup_obj.get("source_family") or source_profile.get("source_family", ""),
                "source_recency": dedup_obj.get("source_recency") or source_profile.get("recency", ""),
                "asset_level_eligible": asset_level_eligible,
                "dedup_status": dedup_obj.get("dedup_status", ""),
                "produced_by_motor": "motor_011",
            }

            library_objects.append(lib_obj)
            library_by_type.setdefault(entity_type, []).append(lib_obj["library_object_id"])
            library_by_scope.setdefault(scope_boundary, []).append(lib_obj["library_object_id"])
            admissibility_counts[admissibility_default] = admissibility_counts.get(admissibility_default, 0) + 1

        return {
            "library_objects": library_objects,
            "library_by_type": library_by_type,
            "library_by_scope": library_by_scope,
            "total_curated": len(library_objects),
            "entity_type_counts": {k: len(v) for k, v in library_by_type.items()},
            "admissibility_counts": admissibility_counts,
            "term_coverage": len(term_index),
        }
