from __future__ import annotations

from itertools import combinations
from typing import Any, Mapping

from .asset_context_vector import build_context_differentiator_register


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _normalized_set(values: list[str] | set[str] | tuple[str, ...] | None) -> set[str]:
    return {_text(value).lower() for value in list(values or []) if _text(value)}


def _slug(value: Any) -> str:
    text_value = _text(value).lower()
    chars: list[str] = []
    previous_dash = False
    for ch in text_value:
        safe = ch if ch.isalnum() else "-"
        if safe == "-":
            if previous_dash:
                continue
            previous_dash = True
        else:
            previous_dash = False
        chars.append(safe)
    return "".join(chars).strip("-")


_PATTERN_LAYER_HINTS = {
    "warehouse_mhe_charging_demand_peak": "physical_process_layer",
    "warehouse_dock_infiltration_loss": "physical_process_layer",
    "cold_chain_status_unknown": "asset_archetype_layer",
    "value_boundary_leakage_owner_operator": "financial_capture_boundary_layer",
    "demand_charge_exposure_unknown": "utility_tariff_energy_layer",
    "reactive_power_exposure": "utility_tariff_energy_layer",
    "fair_comparison_invalid_area_metric": "comparison_normalization_layer",
    "benchmark_denominator_error": "comparison_normalization_layer",
    "digital_twin_prematurity": "measurement_regulatory_governance_layer",
    "sensor_prematurity": "measurement_regulatory_governance_layer",
    "maintenance_maturity_not_evidenced": "maintenance_reliability_layer",
    "maintenance_hidden_value_driver": "maintenance_reliability_layer",
    "compressed_air_leak_plausibility": "physical_process_layer",
    "process_load_vs_waste": "physical_process_layer",
    "procurement_vs_lifecycle_cost": "financial_capture_boundary_layer",
    "procurement_vs_maintenance_conflict": "financial_capture_boundary_layer",
    "hvac_schedule_drift": "operations_controls_layer",
    "tenant_operator_boundary_unresolved": "financial_capture_boundary_layer",
    "compliance_vs_control_mismatch": "measurement_regulatory_governance_layer",
    "high_bay_lighting_waste": "physical_process_layer",
    "steam_trap_failure_plausibility": "maintenance_reliability_layer",
    "boiler_degradation_plausibility": "maintenance_reliability_layer",
    "chiller_degradation_plausibility": "maintenance_reliability_layer",
}


def _infer_pattern_layer(pattern_id: str, spec: Mapping[str, Any] | None = None) -> str:
    explicit = _PATTERN_LAYER_HINTS.get(_text(pattern_id))
    if explicit:
        return explicit
    knowledge_types = {_text(value).upper() for value in list((spec or {}).get("knowledge_type", []) or []) if _text(value)}
    if "FAIR_COMPARISON_RULE" in knowledge_types:
        return "comparison_normalization_layer"
    if "MEASUREMENT_MINIMALITY_RULE" in knowledge_types or "REGULATORY_PHYSICAL_SIGNAL" in knowledge_types:
        return "measurement_regulatory_governance_layer"
    if "MAINTENANCE_REALITY_PATTERN" in knowledge_types:
        return "maintenance_reliability_layer"
    if "FINANCIAL_TRANSLATION" in knowledge_types:
        return "financial_capture_boundary_layer"
    if "PROCESS_LOGIC" in knowledge_types or "LOSS_PATTERN" in knowledge_types:
        return "physical_process_layer"
    return "asset_archetype_layer"


def build_combination_activation_register(
    *,
    registry_bundle: dict[str, Any],
    active_pattern_ids: list[str] | set[str] | tuple[str, ...],
    anti_trigger_signals: list[str] | set[str] | tuple[str, ...] | None = None,
) -> list[dict[str, Any]]:
    combinations = list((registry_bundle or {}).get("combinations", []) or [])
    pattern_ids = _normalized_set(active_pattern_ids)
    anti_triggers = _normalized_set(anti_trigger_signals)
    rows: list[dict[str, Any]] = []

    for spec in combinations:
        required_ids = [_text(value) for value in list(spec.get("pattern_ids", []) or []) if _text(value)]
        required_set = {value.lower() for value in required_ids}
        if not required_set.issubset(pattern_ids):
            continue
        combination_anti_triggers = _normalized_set(spec.get("anti_triggers", []))
        matched_anti_triggers = sorted(combination_anti_triggers.intersection(anti_triggers))
        if matched_anti_triggers:
            continue
        rows.append(
            {
                "combination_id": _text(spec.get("id")),
                "combination_name": _text(spec.get("name")),
                "pattern_ids": required_ids,
                "activation_state": "candidate",
                "combined_hypothesis": _text(spec.get("combined_hypothesis")),
                "strategic_risk": _text(spec.get("strategic_risk")),
                "minimum_evidence": list(spec.get("minimum_evidence", []) or []),
                "financial_exposure": list(spec.get("financial_exposure", []) or []),
                "tad_action": _text(spec.get("tad_action")),
                "prohibited_claims": list(spec.get("prohibited_claims", []) or []),
                "allowed_language": _text(spec.get("allowed_language")),
                "source_basis": list(spec.get("source_basis", []) or []),
                "evidence_state_ceiling": _text(spec.get("confidence_ceiling")),
                "adjudication_required": bool(spec.get("adjudication_required", False)),
                "validator_state": "not_run",
                "matched_anti_triggers": matched_anti_triggers,
                "candidate_origin": "registry_exact",
            }
        )
    return rows


def _context_summary(asset_context_vector: Mapping[str, Any] | None) -> tuple[list[str], str]:
    differentiators = build_context_differentiator_register(asset_context_vector=asset_context_vector)
    implications = [_text(row.get("implication")) for row in differentiators if _text(row.get("implication"))]
    summary = " ".join(implications[:2]).strip()
    return implications, summary


def _candidate_family(layers: list[str]) -> str:
    layer_set = set(layers)
    if "physical_process_layer" in layer_set and "utility_tariff_energy_layer" in layer_set:
        return "driver_exposure"
    if "physical_process_layer" in layer_set and "financial_capture_boundary_layer" in layer_set:
        return "driver_boundary"
    if "physical_process_layer" in layer_set and "comparison_normalization_layer" in layer_set:
        return "driver_comparison"
    if "maintenance_reliability_layer" in layer_set and "financial_capture_boundary_layer" in layer_set:
        return "maintenance_financial"
    if "measurement_regulatory_governance_layer" in layer_set:
        return "decision_governance"
    return "cross_layer_structural"


def _evidence_weight(value: Any) -> int:
    label = _slug(value)
    if label in {"verified", "field_verified", "independent_verified", "l4"}:
        return 4
    if label in {"asset_supported", "asset_specific_public", "operator_evidence", "l3", "observed"}:
        return 3
    if label in {"structurally_plausible", "conditional_hypothesis", "comparison_not_yet_valid", "critical", "high", "structured_prior_from_research"}:
        return 2
    if label in {"weakly_activated", "weak_signal", "l1"}:
        return 1
    return 0


def _context_alignment_breakdown(
    *,
    unique_layers: list[str],
    asset_context_vector: Mapping[str, Any] | None,
) -> dict[str, int]:
    vector = dict(asset_context_vector or {})
    layer_set = set(unique_layers)
    breakdown = {
        "tariff_alignment": 0,
        "boundary_alignment": 0,
        "operations_alignment": 0,
        "solar_alignment": 0,
        "service_alignment": 0,
    }
    utility_tariff_context = _text(vector.get("utility_tariff_context"))
    if utility_tariff_context and "utility_tariff_energy_layer" in layer_set:
        breakdown["tariff_alignment"] = 2
    control_boundary = _text(vector.get("control_boundary"))
    if control_boundary and "financial_capture_boundary_layer" in layer_set:
        breakdown["boundary_alignment"] = 2
    operating_rhythm = _text(vector.get("operating_rhythm"))
    if operating_rhythm and (
        "operations_controls_layer" in layer_set
        or "physical_process_layer" in layer_set
    ):
        breakdown["operations_alignment"] = 1
    solar_profile = _text(vector.get("solar_profile"))
    if solar_profile and "physical_process_layer" in layer_set:
        breakdown["solar_alignment"] = 1
    service_intensity = _text(vector.get("service_intensity"))
    if service_intensity and "comparison_normalization_layer" in layer_set:
        breakdown["service_alignment"] = 1
    return breakdown


def build_latent_combination_candidate_register(
    *,
    registry_bundle: dict[str, Any],
    active_pattern_ids: list[str] | set[str] | tuple[str, ...],
    active_pattern_rows: list[dict[str, Any]] | None = None,
    asset_context_vector: Mapping[str, Any] | None = None,
    knowledge_atom_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    active_pattern_id_rows = [_text(value) for value in list(active_pattern_ids or []) if _text(value)]
    patterns_by_id = dict((registry_bundle or {}).get("patterns_by_id", {}) or {})
    active_rows_by_id = {
        _text(row.get("pattern_id")): dict(row or {})
        for row in list(active_pattern_rows or [])
        if _text(row.get("pattern_id"))
    }
    atom_rows = list(knowledge_atom_register or [])
    atom_supported_pattern_ids = sorted({
        _text(pattern_id)
        for row in atom_rows
        for pattern_id in list(row.get("supported_pattern_ids", []) or [])
        if _text(pattern_id) in patterns_by_id
    })
    pattern_ids = sorted(set(active_pattern_id_rows).union(atom_supported_pattern_ids))
    for pattern_id in atom_supported_pattern_ids:
        if pattern_id in active_rows_by_id:
            continue
        spec = dict(patterns_by_id.get(pattern_id, {}) or {})
        if not spec:
            continue
        active_rows_by_id[pattern_id] = {
            "pattern_id": pattern_id,
            "pattern_name": _text(spec.get("name")) or pattern_id,
            "activation_state": "structurally_plausible",
            "evidence_state": "structured_prior_from_research",
            "minimum_evidence_to_confirm": (
                list(spec.get("minimum_evidence_to_confirm", []) or [])
                or list(spec.get("evidence_required", []) or [])
            ),
        }
    context_implications, context_summary = _context_summary(asset_context_vector)
    context_signature = _text((asset_context_vector or {}).get("context_signature"))
    context_specificity_score = int((asset_context_vector or {}).get("context_specificity_score", 0) or 0)
    rows: list[dict[str, Any]] = []

    seen_ids: set[str] = set()
    for size in (2, 3):
        for group in combinations(pattern_ids, size):
            specs = [dict(patterns_by_id.get(pattern_id, {}) or {}) for pattern_id in group]
            layers = [_infer_pattern_layer(pattern_id, spec) for pattern_id, spec in zip(group, specs)]
            unique_layers = sorted({layer for layer in layers if layer})
            if len(unique_layers) < 2:
                continue
            context_suffix = _slug(_text((asset_context_vector or {}).get("solar_profile")) or context_signature) or "generic"
            candidate_id = f"latent::{_slug('__'.join(group))}::{context_suffix}"
            if candidate_id in seen_ids:
                continue
            seen_ids.add(candidate_id)

            pattern_names = [
                _text(active_rows_by_id.get(pattern_id, {}).get("pattern_name"))
                or _text(spec.get("name"))
                or pattern_id
                for pattern_id, spec in zip(group, specs)
            ]
            family = _candidate_family(unique_layers)
            non_template_divergence_strength = 1 if context_implications else 0
            evidence_support_score = sum(
                _evidence_weight(active_rows_by_id.get(pattern_id, {}).get("activation_state"))
                + _evidence_weight(active_rows_by_id.get(pattern_id, {}).get("evidence_state"))
                for pattern_id in group
            )
            source_basis_score = sum(
                min(len(list(spec.get("source_basis", []) or [])), 2)
                for spec in specs
            )
            supporting_atoms = [
                dict(row)
                for row in atom_rows
                if set(list(row.get("supported_pattern_ids", []) or [])).intersection(group)
            ]
            supporting_atom_ids = sorted({
                _text(row.get("atom_id"))
                for row in supporting_atoms
                if _text(row.get("atom_id"))
            })
            supporting_document_refs = sorted({
                _text(row.get("document_ref"))
                for row in supporting_atoms
                if _text(row.get("document_ref"))
            })
            supporting_provider_keys = sorted({
                _text(row.get("provider_key"))
                for row in supporting_atoms
                if _text(row.get("provider_key"))
            })
            knowledge_atom_support_score = (
                min(len(supporting_atom_ids), 4)
                + min(len(supporting_document_refs), 2)
                + (1 if set(group).issubset({
                    _text(pattern_id)
                    for row in supporting_atoms
                    for pattern_id in list(row.get("supported_pattern_ids", []) or [])
                    if _text(pattern_id)
                }) else 0)
            )
            source_diversity_score = min(len(supporting_provider_keys), 2)
            context_alignment = _context_alignment_breakdown(
                unique_layers=unique_layers,
                asset_context_vector=asset_context_vector,
            )
            context_alignment_score = sum(context_alignment.values())
            score = (
                len(unique_layers) * 3
                + context_specificity_score
                + len(context_implications)
                + evidence_support_score
                + source_basis_score
                + knowledge_atom_support_score
                + source_diversity_score
                + context_alignment_score
            )
            why_not_generic = (
                context_summary
                or "This candidate is retained only as a latent structural prior and still needs stronger asset-specific context."
            )
            hypothesis = (
                f"For this asset, {' + '.join(pattern_names)} may interact as a {family.replace('_', ' ')} combination. "
                f"{context_summary}".strip()
            )
            rows.append(
                {
                    "combination_id": candidate_id,
                    "combination_name": f"Latent {family.replace('_', ' ').title()}",
                    "candidate_origin": "latent_synthesis",
                    "pattern_ids": list(group),
                    "pattern_layers": unique_layers,
                    "combination_family": family,
                    "activation_state": "latent_candidate",
                    "combined_hypothesis": hypothesis,
                    "strategic_risk": "Broader structural interaction remains plausible but not yet promoted to local truth.",
                    "minimum_evidence": sorted(
                        {
                            item
                            for row in [active_rows_by_id.get(pattern_id, {}) for pattern_id in group]
                            for item in list(row.get("minimum_evidence_to_confirm", []) or [])
                            if _text(item)
                        }
                    ),
                    "financial_exposure": [],
                    "tad_action": "VALIDATE_FIRST",
                    "prohibited_claims": [
                        "Do not state that this latent combination is a verified local diagnosis.",
                    ],
                    "allowed_language": "This is a latent cross-layer combination requiring asset-specific falsification.",
                    "source_basis": sorted(
                        {
                            item
                            for spec in specs
                            for item in list(spec.get("source_basis", []) or [])
                            if _text(item)
                        }
                    ),
                    "supporting_atom_ids": supporting_atom_ids,
                    "supporting_document_refs": supporting_document_refs,
                    "supporting_provider_keys": supporting_provider_keys,
                    "knowledge_atom_count": len(supporting_atom_ids),
                    "evidence_state_ceiling": "L2",
                    "adjudication_required": True,
                    "validator_state": "not_run",
                    "matched_anti_triggers": [],
                    "asset_context_vector": dict(asset_context_vector or {}),
                    "context_differentiators": context_implications,
                    "why_this_asset_is_not_generic": why_not_generic,
                    "rejected_generic_templates": [
                        "Generic family-level combination reused without asset-context rebinding.",
                    ],
                    "score": score,
                    "score_breakdown": {
                        "cross_layer_span": len(unique_layers),
                        "asset_context_specificity": context_specificity_score,
                        "non_template_divergence_strength": non_template_divergence_strength,
                        "evidence_support_score": evidence_support_score,
                        "source_basis_score": source_basis_score,
                        "knowledge_atom_support_score": knowledge_atom_support_score,
                        "source_diversity_score": source_diversity_score,
                        "context_alignment_score": context_alignment_score,
                        **context_alignment,
                    },
                    "asset_context_specificity": context_specificity_score,
                    "non_template_divergence_strength": non_template_divergence_strength,
                    "context_binding_insufficiency_risk": (
                        "raised" if context_specificity_score <= 1 and not context_implications else "clear"
                    ),
                }
            )
    rows.sort(
        key=lambda row: (
            -int(row.get("score", 0) or 0),
            -len(list(row.get("pattern_ids", []) or [])),
            _text(row.get("combination_id")),
        )
    )
    return rows


def build_admissible_combination_review_register(
    *,
    latent_combination_candidate_register: list[dict[str, Any]],
    default_decision: str = "needs_review",
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(latent_combination_candidate_register or []):
        score = int(row.get("score", 0) or 0)
        context_specificity = int(row.get("asset_context_specificity", 0) or 0)
        if score < 7:
            continue
        operator_decision = _text(default_decision) or "needs_review"
        if context_specificity <= 1 and not list(row.get("context_differentiators", []) or []):
            operator_decision = "needs_review"
        rows.append(
            {
                "combination_id": _text(row.get("combination_id")),
                "combination_name": _text(row.get("combination_name")),
                "pattern_ids": list(row.get("pattern_ids", []) or []),
                "pattern_layers": list(row.get("pattern_layers", []) or []),
                "combined_hypothesis": _text(row.get("combined_hypothesis")),
                "strategic_risk": _text(row.get("strategic_risk")),
                "minimum_evidence": list(row.get("minimum_evidence", []) or []),
                "financial_exposure": list(row.get("financial_exposure", []) or []),
                "tad_action": _text(row.get("tad_action")),
                "prohibited_claims": list(row.get("prohibited_claims", []) or []),
                "allowed_language": _text(row.get("allowed_language")),
                "evidence_state_ceiling": _text(row.get("evidence_state_ceiling")) or "L2",
                "validator_state": _text(row.get("validator_state")) or "not_run",
                "validator_findings": list(row.get("validator_findings", []) or []),
                "operator_decision": operator_decision,
                "decision_reason": "",
                "candidate_origin": _text(row.get("candidate_origin")) or "latent_synthesis",
                "asset_context_vector": dict(row.get("asset_context_vector", {}) or {}),
                "context_differentiators": list(row.get("context_differentiators", []) or []),
                "why_this_asset_is_not_generic": _text(row.get("why_this_asset_is_not_generic")),
                "score": score,
                "score_breakdown": dict(row.get("score_breakdown", {}) or {}),
                "supporting_atom_ids": list(row.get("supporting_atom_ids", []) or []),
                "supporting_document_refs": list(row.get("supporting_document_refs", []) or []),
                "supporting_provider_keys": list(row.get("supporting_provider_keys", []) or []),
                "knowledge_atom_count": int(row.get("knowledge_atom_count", 0) or 0),
            }
        )
    return rows


def build_latent_combination_cluster_register(
    *,
    latent_combination_candidate_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    clusters: dict[str, dict[str, Any]] = {}
    for row in list(latent_combination_candidate_register or []):
        context_signature = _text((row.get("asset_context_vector", {}) or {}).get("context_signature"))
        family = _text(row.get("combination_family")) or "cross_layer_structural"
        cluster_id = f"cluster::{_slug(family)}::{_slug(context_signature or 'generic')}"
        bucket = clusters.setdefault(
            cluster_id,
            {
                "cluster_id": cluster_id,
                "combination_family": family,
                "context_signature": context_signature,
                "candidate_ids": [],
                "pattern_ids": set(),
                "top_score": 0,
                "context_binding_insufficiency_risk": "clear",
            },
        )
        bucket["candidate_ids"].append(_text(row.get("combination_id")))
        bucket["pattern_ids"].update(list(row.get("pattern_ids", []) or []))
        bucket["top_score"] = max(int(bucket.get("top_score", 0) or 0), int(row.get("score", 0) or 0))
        if _text(row.get("context_binding_insufficiency_risk")) == "raised":
            bucket["context_binding_insufficiency_risk"] = "raised"

    rows: list[dict[str, Any]] = []
    for cluster in clusters.values():
        rows.append(
            {
                "cluster_id": _text(cluster.get("cluster_id")),
                "combination_family": _text(cluster.get("combination_family")),
                "context_signature": _text(cluster.get("context_signature")),
                "candidate_count": len(list(cluster.get("candidate_ids", []) or [])),
                "candidate_ids": list(cluster.get("candidate_ids", []) or []),
                "pattern_ids": sorted(set(cluster.get("pattern_ids", set()) or set())),
                "top_score": int(cluster.get("top_score", 0) or 0),
                "context_binding_insufficiency_risk": _text(cluster.get("context_binding_insufficiency_risk")) or "clear",
            }
        )
    rows.sort(key=lambda row: (-int(row.get("top_score", 0) or 0), -int(row.get("candidate_count", 0) or 0), _text(row.get("cluster_id"))))
    return rows


def build_combination_review_register(
    *,
    combination_activation_register: list[dict[str, Any]],
    default_decision: str = "candidate",
) -> list[dict[str, Any]]:
    decision = _text(default_decision) or "candidate"
    rows: list[dict[str, Any]] = []
    for row in list(combination_activation_register or []):
        validator_state = _text(row.get("validator_state")) or "not_run"
        operator_decision = "blocked_by_validator" if validator_state == "blocked" else decision
        rows.append(
            {
                "combination_id": _text(row.get("combination_id")),
                "combination_name": _text(row.get("combination_name")),
                "pattern_ids": list(row.get("pattern_ids", []) or []),
                "combined_hypothesis": _text(row.get("combined_hypothesis")),
                "strategic_risk": _text(row.get("strategic_risk")),
                "minimum_evidence": list(row.get("minimum_evidence", []) or []),
                "financial_exposure": list(row.get("financial_exposure", []) or []),
                "tad_action": _text(row.get("tad_action")),
                "prohibited_claims": list(row.get("prohibited_claims", []) or []),
                "allowed_language": _text(row.get("allowed_language")),
                "evidence_state_ceiling": _text(row.get("evidence_state_ceiling")),
                "validator_state": validator_state,
                "validator_findings": list(row.get("validator_findings", []) or []),
                "operator_decision": operator_decision,
                "decision_reason": "",
                "candidate_origin": _text(row.get("candidate_origin")) or "registry_exact",
            }
        )
    return rows
