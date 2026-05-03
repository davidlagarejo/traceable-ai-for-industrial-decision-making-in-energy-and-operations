"""Adapter for motor_007 — Quality / Fitness Evaluation Engine."""
from __future__ import annotations
from typing import Any

from ..asset_contracts import (
    derive_asset_context_readiness,
    derive_dominant_evidence_scope,
    derive_report_identity_state,
    derive_target_type_classification_seed,
    missing_observable_clusters,
)
from ..output_taxonomy import canonicalize_output_mode, canonicalize_output_mode_list, output_mode_alias_policy
from .base import BaseMotorAdapter


def _target_admissibility_state(
    *,
    subject_contract_admissibility: str,
    subject_resolution_state: str,
    asset_context_readiness: str,
) -> tuple[str, bool, list[dict[str, Any]]]:
    reasons: list[dict[str, Any]] = []

    def _reason(code: str, message: str, *, severity: str = "warning") -> None:
        reasons.append({
            "code": code,
            "severity": severity,
            "message": message,
        })

    if subject_contract_admissibility == "invalid_for_asset_pipeline":
        _reason("invalid_subject_contract", "The declared subject is not admissible for the asset pipeline.", severity="error")
        return "invalid_for_asset_pipeline", False, reasons
    if subject_contract_admissibility == "issuer_only":
        _reason("issuer_context_only", "The case still resolves only to issuer context, not to an admissible physical asset.")
        return "issuer_context_only", False, reasons
    if subject_resolution_state in {"issuer_address_only", "mailing_address_only", "office_suite_only"}:
        _reason("address_not_yet_asset", f"Address semantics resolved as {subject_resolution_state}; this is not yet a bounded asset.")
        return "address_candidate_only", False, reasons
    if subject_resolution_state == "site_candidate":
        _reason("site_candidate_only", "The target resolves only to a site candidate; asset identity remains unbounded.")
        return "site_candidate_only", False, reasons
    if subject_resolution_state in {"asset_candidate", "unresolved"}:
        _reason("asset_candidate_unbounded", "Asset candidate exists, but identity evidence is still insufficient for bounded asset admission.")
        return "asset_candidate_but_unbounded", False, reasons
    if subject_resolution_state == "bounded_asset":
        if asset_context_readiness in {"asset_context_operable", "asset_context_hardened"}:
            return "bounded_asset_with_operable_context", True, reasons
        if asset_context_readiness in {"asset_context_minimal", "asset_context_insufficient", "location_only"}:
            _reason("bounded_asset_but_thin_context", f"Asset identity is bounded, but context readiness is only {asset_context_readiness}.")
            return "bounded_asset", True, reasons
        return "bounded_asset", True, reasons

    _reason("unresolved_subject_state", "Subject resolution state is unresolved or unsupported.", severity="error")
    return "invalid_for_asset_pipeline", False, reasons


def _allowed_report_classes(target_admissibility_state: str) -> list[str]:
    mapping = {
        "invalid_for_asset_pipeline": ["Issuer Context Memo"],
        "issuer_context_only": ["Issuer Context Memo"],
        "address_candidate_only": ["Address Candidate Brief", "Issuer Context Memo"],
        "site_candidate_only": ["Site Candidate Brief", "Asset Context Insufficiency Brief"],
        "asset_candidate_but_unbounded": ["Asset Context Insufficiency Brief"],
        "bounded_asset": [
            "Asset Context Insufficiency Brief",
            "Pre-Verification Asset Brief",
            "Decision-Blocked Asset Brief",
            "Exploratory Prior Brief",
            "Compliance / Investment Screening Brief",
        ],
        "bounded_asset_with_operable_context": [
            "Pre-Verification Asset Brief",
            "Decision-Blocked Asset Brief",
            "Exploratory Prior Brief",
            "Compliance / Investment Screening Brief",
            "Full Technical Decision Intelligence Report",
            "TDIR Preliminary",
            "Decision-Grade TDIR",
        ],
    }
    return mapping.get(target_admissibility_state, ["Issuer Context Memo"])


def _enforced_report_identity(
    target_admissibility_state: str,
    derived_report_identity_state: str,
) -> str:
    if target_admissibility_state == "invalid_for_asset_pipeline":
        return "Issuer Context Memo"
    if target_admissibility_state == "issuer_context_only":
        return "Issuer Context Memo"
    if target_admissibility_state == "address_candidate_only":
        return "Address Candidate Brief"
    if target_admissibility_state == "site_candidate_only":
        return "Site Candidate Brief"
    if target_admissibility_state == "asset_candidate_but_unbounded":
        return "Asset Context Insufficiency Brief"
    if target_admissibility_state == "bounded_asset":
        if derived_report_identity_state in {"TDIR Preliminary", "Decision-Grade TDIR"}:
            return "Pre-Verification Asset Brief"
    return derived_report_identity_state


def _scope_fitness(target_admissibility_state: str, asset_context_readiness: str) -> float:
    if target_admissibility_state == "invalid_for_asset_pipeline":
        return 0.0
    if target_admissibility_state == "issuer_context_only":
        return 0.1
    if target_admissibility_state == "address_candidate_only":
        return 0.25
    if target_admissibility_state == "site_candidate_only":
        return 0.45
    if target_admissibility_state == "asset_candidate_but_unbounded":
        return 0.55
    if target_admissibility_state == "bounded_asset":
        return 0.7 if asset_context_readiness == "asset_context_minimal" else 0.6
    if target_admissibility_state == "bounded_asset_with_operable_context":
        if asset_context_readiness == "asset_context_hardened":
            return 1.0
        if asset_context_readiness == "asset_context_operable":
            return 0.9
        return 0.8
    return 0.0


def _technical_substrate_readiness(asset_context_readiness: str) -> str:
    if asset_context_readiness in {"asset_context_operable", "asset_context_hardened"}:
        return "sufficient"
    if asset_context_readiness == "asset_context_minimal":
        return "partial"
    return "insufficient"


def _target_classification_object(
    *,
    subject_gate_passed: bool,
    target_admissibility_state: str,
    target_definition: dict[str, Any],
    asset_identity_resolution: dict[str, Any],
    asset_context_readiness: str,
    missing_clusters: list[str],
) -> tuple[dict[str, Any], bool, bool]:
    subject_contract = asset_identity_resolution.get("subject_definition_contract", {})
    target_seed = derive_target_type_classification_seed(subject_contract, target_definition)
    hypothesis = asset_identity_resolution.get("target_classification_hypothesis", {})
    target_type = str(hypothesis.get("target_type") or target_seed.get("target_type_classification") or "AMBIGUOUS_TARGET").strip()
    classification_confidence = str(hypothesis.get("classification_confidence") or target_seed.get("classification_confidence") or "low").strip()
    reason = str(hypothesis.get("reason") or target_seed.get("reason") or "").strip()
    physical_anchor_strength = str(asset_identity_resolution.get("physical_anchor_strength", "")).strip()
    asset_authenticity_state = str(asset_identity_resolution.get("asset_authenticity_state", "")).strip()
    issuer_vs_asset_signals = asset_identity_resolution.get("issuer_vs_asset_signals", {})
    evidence_register = asset_identity_resolution.get("asset_identity_evidence_register", [])

    asset_level_evidence_found = bool(
        physical_anchor_strength in {"medium", "high"}
        and asset_authenticity_state not in {"issuer_address_only", "none"}
    )
    issuer_only_evidence_found = bool(
        target_type in {"CORPORATE_HEADQUARTERS", "PORTFOLIO_ENTITY", "REGISTERED_AGENT_OR_MAILING_ADDRESS"}
        or issuer_vs_asset_signals.get("issuer_seed_signal")
    )
    if not issuer_only_evidence_found and str(target_definition.get("owner_entity", "")).strip():
        if target_admissibility_state in {"issuer_context_only", "address_candidate_only"}:
            issuer_only_evidence_found = True

    if target_admissibility_state in {"issuer_context_only", "invalid_for_asset_pipeline"}:
        asset_level_evidence_found = False
        issuer_only_evidence_found = True
    elif target_admissibility_state == "address_candidate_only":
        asset_level_evidence_found = False
    elif target_admissibility_state in {"site_candidate_only", "asset_candidate_but_unbounded"} and physical_anchor_strength in {"medium", "high"}:
        asset_level_evidence_found = True

    technical_substrate_readiness = _technical_substrate_readiness(asset_context_readiness)
    if target_type == "OPERATING_ASSET" and not subject_gate_passed:
        target_type = "AMBIGUOUS_TARGET"
        classification_confidence = "medium" if classification_confidence == "high" else classification_confidence
        reason = (
            reason
            or "Physical signals exist, but the subject gate has not yet admitted the case as a bounded operating asset."
        )

    return ({
        "target_type": target_type,
        "classification_confidence": classification_confidence,
        "asset_identity_status": str(target_seed.get("asset_identity_status") or "ambiguous"),
        "reason": reason,
        "supporting_sources": [entry.get("evidence_type") for entry in evidence_register if entry.get("evidence_type")],
        "rejected_sources": [],
        "asset_level_evidence_found": asset_level_evidence_found,
        "issuer_only_evidence_found": issuer_only_evidence_found,
        "technical_substrate_readiness": technical_substrate_readiness,
        "target_admissibility_state": target_admissibility_state,
        "missing_observable_clusters": missing_clusters,
    }, asset_level_evidence_found, issuer_only_evidence_found)


def _report_type_recommendation(
    *,
    target_classification_object: dict[str, Any],
    technical_substrate_readiness: str,
) -> dict[str, Any]:
    target_type = str(target_classification_object.get("target_type", "")).strip()
    reason = str(target_classification_object.get("reason", "")).strip()
    recommended_report_type_raw = ""
    prohibited_report_types_raw: list[str] = []
    if target_type == "OPERATING_ASSET" and technical_substrate_readiness == "sufficient":
        recommended_report_type_raw = "Full Technical Decision Intelligence Report"
        prohibited_report_types_raw = ["Entity Address Classification Brief", "Target Clarification Brief"]
    elif target_type == "OPERATING_ASSET" and technical_substrate_readiness == "partial":
        recommended_report_type_raw = "Exploratory Prior / Minimum Evidence Report"
        prohibited_report_types_raw = ["Entity Address Classification Brief", "Target Clarification Brief", "Decision-Grade TDIR"]
    elif target_type == "OPERATING_ASSET":
        recommended_report_type_raw = "Decision-Blocked Asset Brief"
        prohibited_report_types_raw = ["Full Technical Decision Intelligence Report", "Decision-Grade TDIR"]
    elif target_type == "CORPORATE_HEADQUARTERS":
        recommended_report_type_raw = "Entity Address Classification Brief"
        prohibited_report_types_raw = ["Full Technical Decision Intelligence Report", "Pre-Verification Asset Brief", "TDIR Preliminary", "Decision-Grade TDIR"]
    elif target_type == "REGISTERED_AGENT_OR_MAILING_ADDRESS":
        recommended_report_type_raw = "Entity Address Classification Brief"
        prohibited_report_types_raw = ["Full Technical Decision Intelligence Report", "Pre-Verification Asset Brief", "TDIR Preliminary", "Decision-Grade TDIR"]
    elif target_type == "PORTFOLIO_ENTITY":
        recommended_report_type_raw = "Issuer Context Memo"
        prohibited_report_types_raw = ["Full Technical Decision Intelligence Report", "Exploratory Prior / Minimum Evidence Report", "Pre-Verification Asset Brief", "TDIR Preliminary", "Decision-Grade TDIR"]
    elif target_type in {"PROPERTY_LISTING", "AMBIGUOUS_TARGET"}:
        recommended_report_type_raw = "Target Clarification Brief"
        prohibited_report_types_raw = ["Full Technical Decision Intelligence Report", "Pre-Verification Asset Brief", "TDIR Preliminary", "Decision-Grade TDIR"]
    else:
        recommended_report_type_raw = "No Technical Asset Report"
        prohibited_report_types_raw = ["Full Technical Decision Intelligence Report", "Exploratory Prior / Minimum Evidence Report", "Decision-Blocked Asset Brief", "Pre-Verification Asset Brief", "TDIR Preliminary", "Decision-Grade TDIR"]
    return {
        "recommended_report_type": recommended_report_type_raw,
        "recommended_report_type_visible": canonicalize_output_mode(recommended_report_type_raw),
        "recommended_report_type_alias_policy": output_mode_alias_policy(recommended_report_type_raw),
        "reason": reason or "Report type recommendation derived from subject admissibility and technical substrate readiness.",
        "prohibited_report_types": prohibited_report_types_raw,
        "prohibited_report_types_visible": canonicalize_output_mode_list(prohibited_report_types_raw),
        "prohibited_report_type_alias_policies": [output_mode_alias_policy(item) for item in prohibited_report_types_raw],
    }


class Motor007Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_007"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_006"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        resolved = inputs.get("motor_006", {}).get("resolved_entities", [])
        asset_identity_resolution = inputs.get("motor_006", {}).get("asset_identity_resolution", {})
        intake_observables = asset_identity_resolution.get("intake_observables", {})
        target_definition_contract = asset_identity_resolution.get("target_definition_contract", {})
        subject_definition_contract = asset_identity_resolution.get("subject_definition_contract", {})
        subject_contract_admissibility = asset_identity_resolution.get("subject_contract_admissibility", "")
        subject_resolution_state = asset_identity_resolution.get("subject_resolution_state", "unresolved")
        observable_clusters = intake_observables.get("observable_clusters", {})

        evaluated = []
        for entity in resolved:
            terms = entity.get("resolved_terms", [])
            has_entity_id = bool(entity.get("entity_id"))
            has_lineage = bool(entity.get("lineage_ref"))
            has_terms = len(terms) > 0

            score = sum([has_entity_id, has_lineage, has_terms]) / 3.0
            fitness = "fit" if score >= 0.67 else "marginal" if score >= 0.33 else "unfit"

            evaluated.append({
                **entity,
                "fitness_score": round(score, 2),
                "fitness_status": fitness,
                "quality_checks": {
                    "has_entity_id": has_entity_id,
                    "has_lineage": has_lineage,
                    "has_canonical_terms": has_terms,
                },
                "produced_by_motor": "motor_007",
            })

        fit_count = sum(1 for e in evaluated if e["fitness_status"] == "fit")
        asset_context_readiness = derive_asset_context_readiness(
            inputs.get("__pipeline__", {}),
            target_definition=target_definition_contract,
            clusters=observable_clusters,
        )
        report_identity_state = derive_report_identity_state(
            target_definition_contract,
            asset_context_readiness,
        )
        dominant_evidence_scope = derive_dominant_evidence_scope(
            target_definition_contract,
            asset_context_readiness,
        )
        missing_clusters = missing_observable_clusters(observable_clusters)
        target_admissibility_state, subject_gate_passed, subject_gate_reason_register = _target_admissibility_state(
            subject_contract_admissibility=subject_contract_admissibility,
            subject_resolution_state=subject_resolution_state,
            asset_context_readiness=asset_context_readiness,
        )
        allowed_report_classes = _allowed_report_classes(target_admissibility_state)
        report_identity_state = _enforced_report_identity(
            target_admissibility_state,
            report_identity_state,
        )
        scope_fitness = _scope_fitness(target_admissibility_state, asset_context_readiness)
        target_classification_object, asset_level_evidence_found, issuer_only_evidence_found = _target_classification_object(
            subject_gate_passed=subject_gate_passed,
            target_admissibility_state=target_admissibility_state,
            target_definition=target_definition_contract,
            asset_identity_resolution=asset_identity_resolution,
            asset_context_readiness=asset_context_readiness,
            missing_clusters=missing_clusters,
        )
        technical_substrate_readiness = _technical_substrate_readiness(asset_context_readiness)
        report_type_recommendation = _report_type_recommendation(
            target_classification_object=target_classification_object,
            technical_substrate_readiness=technical_substrate_readiness,
        )
        return {
            "evaluated_entities": evaluated,
            "total_evaluated": len(evaluated),
            "total_fit": fit_count,
            "fitness_rate": round(fit_count / len(evaluated), 2) if evaluated else 0.0,
            "subject_definition_contract": subject_definition_contract,
            "subject_contract_admissibility": subject_contract_admissibility,
            "target_definition_contract": target_definition_contract,
            "target_admissibility_state": target_admissibility_state,
            "subject_gate_passed": subject_gate_passed,
            "subject_gate_reason_register": subject_gate_reason_register,
            "allowed_report_classes": allowed_report_classes,
            "allowed_report_classes_visible": canonicalize_output_mode_list(allowed_report_classes),
            "target_classification_object": target_classification_object,
            "target_type_classification": target_classification_object.get("target_type"),
            "classification_confidence": target_classification_object.get("classification_confidence"),
            "asset_identity_status": target_classification_object.get("asset_identity_status"),
            "asset_level_evidence_found": asset_level_evidence_found,
            "issuer_only_evidence_found": issuer_only_evidence_found,
            "technical_substrate_readiness": technical_substrate_readiness,
            "report_type_recommendation": report_type_recommendation,
            "recommended_report_type": report_type_recommendation.get("recommended_report_type"),
            "recommended_report_type_visible": report_type_recommendation.get("recommended_report_type_visible"),
            "recommended_report_type_alias_policy": report_type_recommendation.get("recommended_report_type_alias_policy", {}),
            "prohibited_report_types": report_type_recommendation.get("prohibited_report_types", []),
            "prohibited_report_types_visible": report_type_recommendation.get("prohibited_report_types_visible", []),
            "visible_output_taxonomy_policy": {
                "canonical_visible_labels_only": True,
                "compatibility_aliases_internal_only": True,
                "policy": "Compatibility aliases may be preserved in raw fields, but visible runtime/report/manifest surfaces must use canonical labels only.",
            },
            "asset_context_readiness": asset_context_readiness,
            "observable_cluster_register": observable_clusters,
            "missing_observable_clusters": missing_clusters,
            "target_scope_fitness": round(scope_fitness, 2),
            "dominant_evidence_scope": dominant_evidence_scope,
            "report_identity_state": report_identity_state,
            "asset_identity_resolution": asset_identity_resolution,
        }
