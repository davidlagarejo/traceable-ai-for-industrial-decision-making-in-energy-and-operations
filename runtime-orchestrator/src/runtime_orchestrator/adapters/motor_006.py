"""Adapter for motor_006 — Entity Identity / Resolution Engine."""
from __future__ import annotations
import hashlib
import re
from typing import Any

from ..asset_contracts import (
    derive_subject_contract_admissibility,
    derive_subject_definition,
    derive_target_definition,
)
from .base import BaseMotorAdapter


_OFFICE_SUITE_RE = re.compile(r"\b(suite|ste\.?|floor|fl\b|unit|apt|#)\b", re.IGNORECASE)
_MAILING_RE = re.compile(r"\b(p\.?\s*o\.?\s*box|po box|mail(ing)?)\b", re.IGNORECASE)


def _hash_id(prefix: str, raw: str) -> str:
    return f"{prefix}:" + hashlib.sha256(raw.encode()).hexdigest()[:12]


def _address_semantics(
    address_raw: str,
    *,
    subject_kind: str,
    asset_anchor_type: str,
    asset_identity_evidence_class: str,
    owner_entity: str,
) -> str:
    if not address_raw:
        return "unresolved"
    if _MAILING_RE.search(address_raw):
        return "mailing_address"
    if _OFFICE_SUITE_RE.search(address_raw):
        return "office_suite"
    if asset_identity_evidence_class == "issuer_address_only" or (subject_kind == "issuer" and owner_entity):
        return "issuer_hq"
    if asset_anchor_type in {"benchmark_record", "facility_registry_id", "permit_record", "building_name_plus_address"}:
        return "candidate_building"
    if asset_anchor_type in {"parcel_id", "assessor_record", "lat_lon", "postal_address"}:
        return "candidate_site"
    return "unresolved"


def _subject_resolution_state(
    *,
    subject_kind: str,
    subject_contract_admissibility: str,
    address_semantics: str,
    asset_identity_evidence_class: str,
) -> str:
    if subject_contract_admissibility == "invalid_for_asset_pipeline":
        return "unresolved"
    if subject_contract_admissibility == "issuer_only":
        return "issuer_address_only"
    if address_semantics == "mailing_address":
        return "mailing_address_only"
    if address_semantics == "office_suite":
        return "office_suite_only"
    if address_semantics == "issuer_hq":
        return "issuer_address_only"
    if asset_identity_evidence_class in {"benchmark_record_linked", "local_asset_record_linked", "multi-source_asset_bounded"}:
        return "bounded_asset"
    if subject_kind == "asset_candidate":
        return "asset_candidate"
    if address_semantics == "candidate_building":
        return "asset_candidate"
    if address_semantics == "candidate_site":
        return "site_candidate"
    return "unresolved"


def _physical_anchor_strength(
    *,
    asset_anchor_type: str,
    asset_identity_evidence_class: str,
) -> str:
    if asset_identity_evidence_class == "multi-source_asset_bounded":
        return "high"
    if asset_identity_evidence_class in {
        "benchmark_record_linked",
        "local_asset_record_linked",
        "parcel_or_record_linked",
    }:
        return "medium"
    if asset_anchor_type in {"lat_lon", "building_name_plus_address", "postal_address"}:
        return "low"
    if asset_identity_evidence_class in {"issuer_address_only", "none"}:
        return "none"
    return "low"


def _issuer_vs_asset_signals(
    *,
    address_semantics: str,
    subject_kind: str,
    subject_origin: str,
    physical_anchor_strength: str,
    asset_identity_evidence_class: str,
) -> dict[str, Any]:
    corporate_hq_signal = address_semantics in {"issuer_hq", "office_suite"}
    mailing_signal = address_semantics == "mailing_address"
    operating_asset_signal = physical_anchor_strength in {"medium", "high"} and asset_identity_evidence_class not in {
        "issuer_address_only",
        "none",
    }
    return {
        "corporate_hq_signal": corporate_hq_signal,
        "mailing_signal": mailing_signal,
        "operating_asset_signal": operating_asset_signal,
        "issuer_seed_signal": subject_kind == "issuer" or subject_origin in {"issuer_seed", "issuer_plus_address_seed"},
        "declared_only_signal": asset_identity_evidence_class == "declared_only",
        "physical_anchor_strength": physical_anchor_strength,
    }


def _target_classification_hypothesis(
    *,
    subject_kind: str,
    subject_resolution_state: str,
    address_semantics: str,
    asset_identity_evidence_class: str,
    issuer_vs_asset_signals: dict[str, Any],
) -> dict[str, Any]:
    if issuer_vs_asset_signals.get("mailing_signal"):
        return {
            "target_type": "REGISTERED_AGENT_OR_MAILING_ADDRESS",
            "classification_confidence": "high",
            "reason": "Address semantics indicate a mailing or administrative address.",
        }
    if issuer_vs_asset_signals.get("corporate_hq_signal"):
        return {
            "target_type": "CORPORATE_HEADQUARTERS",
            "classification_confidence": "high",
            "reason": "Address semantics indicate headquarters, executive-office, or office-suite context.",
        }
    if subject_kind == "issuer":
        return {
            "target_type": "PORTFOLIO_ENTITY",
            "classification_confidence": "medium",
            "reason": "Only issuer-level context is currently resolved.",
        }
    if subject_resolution_state == "bounded_asset":
        return {
            "target_type": "OPERATING_ASSET",
            "classification_confidence": "high",
            "reason": "Asset identity is bounded by public physical anchors.",
        }
    if subject_kind == "asset_candidate" or address_semantics == "candidate_building":
        return {
            "target_type": "PROPERTY_LISTING",
            "classification_confidence": "medium",
            "reason": "A candidate building-like target exists, but asset identity remains unbounded.",
        }
    if subject_resolution_state in {"site_candidate", "asset_candidate"} or asset_identity_evidence_class in {
        "parcel_or_record_linked",
        "local_asset_record_linked",
        "benchmark_record_linked",
    }:
        return {
            "target_type": "AMBIGUOUS_TARGET",
            "classification_confidence": "medium",
            "reason": "A physical site candidate exists, but operating-asset identity is not yet fully bounded.",
        }
    if subject_kind == "address_candidate":
        return {
            "target_type": "AMBIGUOUS_TARGET",
            "classification_confidence": "low",
            "reason": "Only address-level evidence exists; target remains ambiguous.",
        }
    return {
        "target_type": "INVALID_TARGET",
        "classification_confidence": "low",
        "reason": "The resolved subject does not yet support an admissible asset hypothesis.",
    }


class Motor006Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_006"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_005", "motor_003", "motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        normalized = inputs.get("motor_005", {}).get("normalized_objects", [])
        intake_observables = inputs.get("motor_005", {}).get("normalized_intake_observables", {})
        term_index = inputs.get("motor_003", {}).get("term_index", {})
        target_definition_contract = inputs.get("motor_003", {}).get("target_definition_contract", {})
        subject_definition_contract = inputs.get("motor_001", {}).get("subject_definition_contract", {})
        subject_contract_admissibility = inputs.get("motor_001", {}).get("subject_contract_admissibility", "")

        resolved = []
        for obj in normalized:
            source_id = obj.get("source_id", "")
            canonical_terms = obj.get("canonical_terms", [])
            entity_id = _hash_id("entity", source_id + "|".join(sorted(canonical_terms)))

            resolved.append({
                **obj,
                "entity_id": entity_id,
                "resolved_terms": canonical_terms,
                "resolution_status": "resolved",
                "produced_by_motor": "motor_006",
            })

        pipeline = inputs.get("__pipeline__", {})
        if not target_definition_contract:
            target_definition_contract = derive_target_definition(pipeline)
        if not subject_definition_contract:
            subject_definition_contract = derive_subject_definition(pipeline)
        if not subject_contract_admissibility:
            subject_contract_admissibility, _ = derive_subject_contract_admissibility(
                subject_definition_contract,
                target_definition_contract,
            )

        address_raw = str(
            subject_definition_contract.get("address_raw")
            or target_definition_contract.get("address_raw", "")
        ).strip()
        owner_entity = str(target_definition_contract.get("owner_entity", "")).strip()
        subject_kind = str(subject_definition_contract.get("subject_kind", "")).strip()
        asset_anchor_type = str(subject_definition_contract.get("asset_anchor_type", "")).strip()
        asset_anchor_value = str(subject_definition_contract.get("asset_anchor_value", "")).strip()
        asset_identity_evidence_class = str(
            subject_definition_contract.get("asset_identity_evidence_class", "")
        ).strip()

        address_semantics = _address_semantics(
            address_raw,
            subject_kind=subject_kind,
            asset_anchor_type=asset_anchor_type,
            asset_identity_evidence_class=asset_identity_evidence_class,
            owner_entity=owner_entity,
        )
        subject_resolution_state = _subject_resolution_state(
            subject_kind=subject_kind,
            subject_contract_admissibility=subject_contract_admissibility,
            address_semantics=address_semantics,
            asset_identity_evidence_class=asset_identity_evidence_class,
        )
        physical_anchor_strength = _physical_anchor_strength(
            asset_anchor_type=asset_anchor_type,
            asset_identity_evidence_class=asset_identity_evidence_class,
        )
        issuer_vs_asset_signals = _issuer_vs_asset_signals(
            address_semantics=address_semantics,
            subject_kind=subject_kind,
            subject_origin=str(subject_definition_contract.get("subject_origin", "")).strip(),
            physical_anchor_strength=physical_anchor_strength,
            asset_identity_evidence_class=asset_identity_evidence_class,
        )
        target_classification_hypothesis = _target_classification_hypothesis(
            subject_kind=subject_kind,
            subject_resolution_state=subject_resolution_state,
            address_semantics=address_semantics,
            asset_identity_evidence_class=asset_identity_evidence_class,
            issuer_vs_asset_signals=issuer_vs_asset_signals,
        )

        site_key = "|".join(
            [
                address_raw,
                str(target_definition_contract.get("target_type", "")),
                owner_entity,
            ]
        )
        site_candidate_id = _hash_id("site", address_raw or site_key)
        asset_candidate_id = (
            _hash_id("asset-candidate", site_key + "|" + asset_anchor_type + "|" + asset_anchor_value)
            if address_raw or asset_anchor_value
            else ""
        )
        bounded_asset_id = (
            _hash_id("asset", site_key + "|" + asset_anchor_type + "|" + asset_anchor_value)
            if subject_resolution_state == "bounded_asset"
            else ""
        )
        issuer_entity_id = _hash_id("issuer", owner_entity or target_definition_contract.get("operator_entity", "") or "unknown-issuer")

        if address_semantics in {"issuer_hq", "mailing_address", "office_suite"}:
            site_vs_issuer_disambiguation = "issuer_address_not_asset"
        elif subject_resolution_state == "bounded_asset":
            site_vs_issuer_disambiguation = "asset_bounded"
        elif subject_resolution_state in {"site_candidate", "asset_candidate"}:
            site_vs_issuer_disambiguation = "candidate_site_not_yet_bounded"
        else:
            site_vs_issuer_disambiguation = "unresolved"

        asset_identity_evidence_register = []
        if asset_anchor_type or asset_anchor_value:
            asset_identity_evidence_register.append({
                "evidence_type": asset_anchor_type or "undeclared_anchor",
                "evidence_value": asset_anchor_value or address_raw,
                "evidence_class": asset_identity_evidence_class or "none",
                "confidence": subject_definition_contract.get("asset_anchor_confidence", "none"),
                "origin": subject_definition_contract.get("subject_origin", "unknown"),
            })
        if address_raw:
            asset_identity_evidence_register.append({
                "evidence_type": "address_semantics",
                "evidence_value": address_raw,
                "evidence_class": address_semantics,
                "confidence": "derived",
                "origin": "motor_006",
            })

        asset_identity_resolution = {
            "subject_definition_contract": subject_definition_contract,
            "subject_contract_admissibility": subject_contract_admissibility,
            "target_definition_contract": target_definition_contract,
            "subject_resolution_state": subject_resolution_state,
            "asset_authenticity_state": asset_identity_evidence_class or "none",
            "address_semantics": address_semantics,
            "site_vs_issuer_disambiguation": site_vs_issuer_disambiguation,
            "asset_identity_evidence_register": asset_identity_evidence_register,
            "physical_anchor_strength": physical_anchor_strength,
            "issuer_vs_asset_signals": issuer_vs_asset_signals,
            "target_classification_hypothesis": target_classification_hypothesis,
            "asset_entity_id": bounded_asset_id,
            "site_entity_id": site_candidate_id,
            "site_candidate_id": site_candidate_id,
            "asset_candidate_id": asset_candidate_id,
            "bounded_asset_id": bounded_asset_id,
            "issuer_entity_id": issuer_entity_id,
            "resolution_status": subject_resolution_state,
            "intake_observables": intake_observables,
        }

        return {
            "resolved_entities": resolved,
            "total_resolved": len(resolved),
            "asset_identity_resolution": asset_identity_resolution,
        }
