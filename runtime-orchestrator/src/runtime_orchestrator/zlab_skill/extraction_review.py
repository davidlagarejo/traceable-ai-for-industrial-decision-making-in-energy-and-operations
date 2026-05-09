from __future__ import annotations

from typing import Any

from .schema import validate_combination_spec, validate_pattern_spec


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def build_extraction_review_register(
    extraction_records: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for record in list(extraction_records or []):
        rows.append(
            {
                "extraction_id": _text(record.get("id")),
                "document_title": _text(record.get("document_title")),
                "document_ref": _text(record.get("document_ref")),
                "provider_key": _text(record.get("provider_key")),
                "source_basis_id": _text(record.get("source_basis_id")),
                "retrieval_purpose": _text(record.get("retrieval_purpose")),
                "review_status": _text(record.get("review_status")) or "draft",
                "evidence_ceiling": _text(record.get("evidence_ceiling")) or "L2",
                "knowledge_atom_count": len(list(record.get("knowledge_atoms", []) or [])),
                "pattern_candidate_count": len(list(record.get("pattern_candidate_records", []) or [])),
                "combination_candidate_count": len(list(record.get("combination_candidate_records", []) or [])),
                "structured_prior_only": bool(record.get("structured_prior_only", True)),
                "notes": _text(record.get("notes")),
            }
        )
    return rows


def _slug(value: Any) -> str:
    text = _text(value).lower()
    chars: list[str] = []
    previous_dash = False
    for ch in text:
        safe = ch if ch.isalnum() else "-"
        if safe == "-":
            if previous_dash:
                continue
            previous_dash = True
        else:
            previous_dash = False
        chars.append(safe)
    return "".join(chars).strip("-")


def _pattern_id_from_candidate(candidate_id: Any, fallback_name: Any) -> str:
    candidate_text = _text(candidate_id)
    if candidate_text.startswith("pattern_candidate::"):
        candidate_text = candidate_text.split("pattern_candidate::", 1)[1]
    return _slug(candidate_text) or _slug(fallback_name) or "promoted-pattern"


def _combination_id_from_candidate(candidate_id: Any, fallback_name: Any) -> str:
    candidate_text = _text(candidate_id)
    if candidate_text.startswith("combination_candidate::"):
        candidate_text = candidate_text.split("combination_candidate::", 1)[1]
    return _slug(candidate_text) or _slug(fallback_name) or "promoted-combination"


def _promotion_state_from_review_status(
    *,
    review_status: str,
    already_registered: bool,
) -> str:
    status = _text(review_status)
    if status == "approved":
        return "already_registered" if already_registered else "ready_for_registry_review"
    if status in {"auto_draft", "needs_review"}:
        return "auto_draft_review_required"
    return "draft_only"


def _supporting_atom_map(extraction_record: dict[str, Any]) -> dict[str, dict[str, Any]]:
    return {
        _text(row.get("id")): dict(row)
        for row in list(extraction_record.get("knowledge_atoms", []) or [])
        if _text(row.get("id"))
    }


def _industries_from_atoms(atom_ids: list[str], atom_map: dict[str, dict[str, Any]]) -> list[str]:
    rows: list[str] = []
    seen: set[str] = set()
    for atom_id in list(atom_ids or []):
        atom = dict(atom_map.get(_text(atom_id), {}) or {})
        for item in list(atom.get("applicable_industries", []) or []):
            text = _text(item)
            if text and text not in seen:
                seen.add(text)
                rows.append(text)
    return rows or ["cross_industry_structured_prior"]


def build_pattern_spec_proposal_from_candidate(
    *,
    extraction_record: dict[str, Any],
    candidate_record: dict[str, Any],
) -> dict[str, Any]:
    atom_map = _supporting_atom_map(extraction_record)
    atom_ids = [_text(item) for item in list(candidate_record.get("derived_from_atom_ids", []) or []) if _text(item)]
    first_atom = dict(atom_map.get(atom_ids[0], {}) or {}) if atom_ids else {}
    pattern_id = _text(candidate_record.get("matched_registry_pattern_id")) or _pattern_id_from_candidate(
        candidate_record.get("id"),
        candidate_record.get("name"),
    )
    knowledge_types = list(candidate_record.get("knowledge_types", []) or [])
    hypothesis = _text(candidate_record.get("hypothesis"))
    minimum_evidence = list(candidate_record.get("minimum_evidence", []) or [])
    financial_mechanism = _text(candidate_record.get("financial_mechanism")) or _text(first_atom.get("financial_mechanism"))
    source_locator = _text(candidate_record.get("source_locator")) or _text(first_atom.get("source_locator"))
    pattern_spec = {
        "id": pattern_id,
        "version": "1.0.0-candidate",
        "name": _text(candidate_record.get("name")) or pattern_id.replace("-", " ").title(),
        "knowledge_type": knowledge_types,
        "asset_types": list(candidate_record.get("asset_types", []) or []),
        "applicable_industries": _industries_from_atoms(atom_ids, atom_map),
        "applicable_contexts": list(candidate_record.get("applicable_contexts", []) or []),
        "trigger_conditions": list(candidate_record.get("applicable_contexts", []) or []) or ["relevant asset/context present"],
        "anti_triggers": list(candidate_record.get("anti_triggers", []) or []),
        "physical_basis": _text(first_atom.get("statement")) or hypothesis,
        "operational_basis": hypothesis,
        "financial_mechanism": financial_mechanism or "Structural prior suggests a financial consequence but does not prove local truth.",
        "typical_false_assumption": "A reviewed pattern candidate can be treated as local diagnosis without case evidence.",
        "hypothesis": hypothesis,
        "rival_hypotheses": [
            "The visible symptom reflects the real dominant variable.",
            "A different structural driver or control boundary explains the case better.",
        ],
        "evidence_required": minimum_evidence,
        "minimum_evidence_to_activate": minimum_evidence[: max(1, min(2, len(minimum_evidence)))] or minimum_evidence,
        "minimum_evidence_to_confirm": minimum_evidence,
        "falsification_conditions": list(candidate_record.get("falsification_conditions", []) or []),
        "allowed_claim_language": f"{hypothesis} is a structured prior requiring falsification before local diagnosis.",
        "prohibited_claim_language": f"This asset has {_text(candidate_record.get('name')).lower() or 'the promoted pattern'} as confirmed local truth.",
        "financial_exposure_if_true": [
            financial_mechanism or "Capital and sequencing decisions may target the wrong variable."
        ],
        "financial_exposure_if_false": [
            "Evidence effort should move to rival hypotheses instead of hardening the current pattern."
        ],
        "tad_actions": (
            ["VALIDATE_LOSS_PATTERN"]
            if "LOSS_PATTERN" in knowledge_types
            else ["REQUEST_MINIMUM_EVIDENCE"]
        ),
        "stop_conditions": [
            "Stop when asset-specific evidence either supports or falsifies the structural prior.",
        ],
        "escalation_conditions": [
            "Escalate to registry review if the candidate is repeatedly approved across independent extractions.",
        ],
        "source_basis": [_text(extraction_record.get("source_basis_id"))],
        "confidence_ceiling": _text(candidate_record.get("confidence_ceiling")) or "L2",
        "claim_permissions_impact": ["hypothesis_only", "no_local_diagnosis"],
        "example_outputs": [
            f"{hypothesis} Evidence required: {', '.join(minimum_evidence)}."
        ],
        "tests": [f"approved_extraction::{_text(extraction_record.get('id'))}::{_text(candidate_record.get('id'))}"],
        "proposed_from_source_locator": source_locator,
    }
    return validate_pattern_spec(pattern_spec)


def build_combination_spec_proposal_from_candidate(
    *,
    extraction_record: dict[str, Any],
    candidate_record: dict[str, Any],
    promoted_pattern_ids_by_candidate: dict[str, str],
) -> dict[str, Any]:
    combination_id = _text(candidate_record.get("matched_registry_combination_id")) or _combination_id_from_candidate(
        candidate_record.get("id"),
        candidate_record.get("name"),
    )
    combination_spec = {
        "id": combination_id,
        "version": "1.0.0-candidate",
        "name": _text(candidate_record.get("name")) or combination_id.replace("-", " ").title(),
        "pattern_ids": [
            promoted_pattern_ids_by_candidate[_text(item)]
            for item in list(candidate_record.get("derived_from_pattern_candidate_ids", []) or [])
            if _text(item) in promoted_pattern_ids_by_candidate
        ],
        "trigger_logic": ["all_linked_pattern_promotions_approved"],
        "anti_triggers": ["validator_blocked", "missing_pattern_promotion"],
        "combined_hypothesis": _text(candidate_record.get("combined_hypothesis")),
        "strategic_risk": "Multiple structural priors may interact and make generic capital logic unsafe.",
        "minimum_evidence": list(candidate_record.get("minimum_evidence", []) or []),
        "financial_exposure": list(candidate_record.get("financial_exposure", []) or []),
        "tad_action": "REQUEST_MINIMUM_EVIDENCE",
        "prohibited_claims": list(candidate_record.get("prohibited_claims", []) or []),
        "allowed_language": (
            f"{_text(candidate_record.get('combined_hypothesis'))} is a bounded combination requiring discriminating evidence."
        ),
        "source_basis": [_text(extraction_record.get("source_basis_id"))],
        "confidence_ceiling": _text(candidate_record.get("confidence_ceiling")) or "L2",
        "adjudication_required": True,
        "tests": [f"approved_extraction::{_text(extraction_record.get('id'))}::{_text(candidate_record.get('id'))}"],
        "proposed_from_source_locator": _text(candidate_record.get("source_locator")),
    }
    return validate_combination_spec(combination_spec)


def build_extraction_promotion_registers(
    extraction_records: list[dict[str, Any]] | None,
    *,
    registry_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    bundle = dict(registry_bundle or {})
    existing_pattern_ids = set(dict(bundle.get("patterns_by_id", {}) or {}))
    existing_combination_ids = set(dict(bundle.get("combinations_by_id", {}) or {}))
    pattern_rows: list[dict[str, Any]] = []
    combination_rows: list[dict[str, Any]] = []

    for extraction_record in list(extraction_records or []):
        record = dict(extraction_record or {})
        review_status = _text(record.get("review_status"))
        if review_status not in {"approved", "auto_draft", "needs_review"}:
            continue
        promoted_pattern_ids_by_candidate: dict[str, str] = {}
        for candidate in list(record.get("pattern_candidate_records", []) or []):
            candidate_row = dict(candidate or {})
            proposed_spec = build_pattern_spec_proposal_from_candidate(
                extraction_record=record,
                candidate_record=candidate_row,
            )
            proposed_id = _text(proposed_spec.get("id"))
            promoted_pattern_ids_by_candidate[_text(candidate_row.get("id"))] = proposed_id
            pattern_rows.append(
                {
                    "promotion_id": f"pattern_promotion::{_text(record.get('id'))}::{_text(candidate_row.get('id'))}",
                    "extraction_id": _text(record.get("id")),
                    "candidate_id": _text(candidate_row.get("id")),
                    "document_ref": _text(record.get("document_ref")),
                    "source_basis_id": _text(record.get("source_basis_id")),
                    "review_status": review_status,
                    "proposed_pattern_id": proposed_id,
                    "pattern_id": proposed_id,
                    "promotion_state": _promotion_state_from_review_status(
                        review_status=review_status,
                        already_registered=proposed_id in existing_pattern_ids,
                    ),
                    "proposed_spec": proposed_spec,
                }
            )
        for candidate in list(record.get("combination_candidate_records", []) or []):
            candidate_row = dict(candidate or {})
            proposed_spec = build_combination_spec_proposal_from_candidate(
                extraction_record=record,
                candidate_record=candidate_row,
                promoted_pattern_ids_by_candidate=promoted_pattern_ids_by_candidate,
            )
            proposed_id = _text(proposed_spec.get("id"))
            combination_rows.append(
                {
                    "promotion_id": f"combination_promotion::{_text(record.get('id'))}::{_text(candidate_row.get('id'))}",
                    "extraction_id": _text(record.get("id")),
                    "candidate_id": _text(candidate_row.get("id")),
                    "document_ref": _text(record.get("document_ref")),
                    "source_basis_id": _text(record.get("source_basis_id")),
                    "review_status": review_status,
                    "proposed_combination_id": proposed_id,
                    "combination_id": proposed_id,
                    "promotion_state": _promotion_state_from_review_status(
                        review_status=review_status,
                        already_registered=proposed_id in existing_combination_ids,
                    ),
                    "proposed_spec": proposed_spec,
                }
            )

    return {
        "approved_pattern_promotion_register": pattern_rows,
        "approved_combination_promotion_register": combination_rows,
    }
