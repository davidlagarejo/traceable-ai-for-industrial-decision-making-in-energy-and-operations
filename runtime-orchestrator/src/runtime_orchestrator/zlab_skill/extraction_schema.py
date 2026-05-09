from __future__ import annotations

from typing import Any, Mapping

from .schema import (
    ALLOWED_KNOWLEDGE_TYPES,
    ALLOWED_PATTERN_CONFIDENCE_CEILINGS,
    RegistryValidationError,
)


ALLOWED_EXTRACTION_REVIEW_STATUSES = {
    "auto_draft",
    "draft",
    "needs_review",
    "approved",
    "rejected",
}

_REQUIRED_KNOWLEDGE_ATOM_FIELDS = {
    "id",
    "knowledge_type",
    "statement",
    "asset_types",
    "applicable_industries",
    "applicable_contexts",
    "anti_triggers",
    "falsification_conditions",
    "minimum_evidence",
    "financial_mechanism",
    "supporting_excerpt",
    "source_locator",
    "confidence_ceiling",
}

_REQUIRED_PATTERN_CANDIDATE_FIELDS = {
    "id",
    "derived_from_atom_ids",
    "name",
    "knowledge_types",
    "asset_types",
    "applicable_contexts",
    "hypothesis",
    "minimum_evidence",
    "anti_triggers",
    "falsification_conditions",
    "financial_mechanism",
    "source_locator",
    "confidence_ceiling",
}

_REQUIRED_COMBINATION_CANDIDATE_FIELDS = {
    "id",
    "derived_from_pattern_candidate_ids",
    "name",
    "combined_hypothesis",
    "minimum_evidence",
    "financial_exposure",
    "prohibited_claims",
    "source_locator",
    "confidence_ceiling",
}

_REQUIRED_EXTRACTION_RECORD_FIELDS = {
    "id",
    "version",
    "source_basis_id",
    "provider_key",
    "document_title",
    "document_ref",
    "retrieval_purpose",
    "extraction_mode",
    "evidence_ceiling",
    "structured_prior_only",
    "provenance_manifest",
    "knowledge_atoms",
    "pattern_candidate_records",
    "combination_candidate_records",
    "review_status",
    "notes",
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _require_fields(name: str, payload: Mapping[str, Any], required: set[str]) -> None:
    missing = sorted(key for key in required if key not in payload)
    if missing:
        raise RegistryValidationError(f"{name} is missing required fields: {', '.join(missing)}")


def _ensure_non_empty_text(name: str, field_name: str, value: Any) -> str:
    text_value = _text(value)
    if not text_value:
        raise RegistryValidationError(f"{name}.{field_name} must be non-empty")
    return text_value


def _ensure_text_list(name: str, field_name: str, value: Any, *, allow_empty: bool = False) -> list[str]:
    if not isinstance(value, list):
        raise RegistryValidationError(f"{name}.{field_name} must be a list")
    rows = [_text(item) for item in value if _text(item)]
    if not rows and not allow_empty:
        raise RegistryValidationError(f"{name}.{field_name} must contain at least one non-empty value")
    return rows


def _ensure_confidence_ceiling(name: str, field_name: str, value: Any) -> str:
    ceiling = _ensure_non_empty_text(name, field_name, value)
    if ceiling not in ALLOWED_PATTERN_CONFIDENCE_CEILINGS:
        raise RegistryValidationError(f"{name}.{field_name} must stay within L0/L1/L2, got {ceiling}")
    return ceiling


def _ensure_knowledge_types(name: str, field_name: str, value: Any) -> list[str]:
    rows = _ensure_text_list(name, field_name, value)
    unknown = sorted(set(rows).difference(ALLOWED_KNOWLEDGE_TYPES))
    if unknown:
        raise RegistryValidationError(f"{name}.{field_name} contains unsupported values: {', '.join(unknown)}")
    return rows


def validate_knowledge_atom(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "knowledge_atom"
    _require_fields(name, payload, _REQUIRED_KNOWLEDGE_ATOM_FIELDS)
    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["knowledge_type"] = _ensure_knowledge_types(name, "knowledge_type", [payload.get("knowledge_type")])
    normalized["knowledge_type"] = normalized["knowledge_type"][0]
    normalized["statement"] = _ensure_non_empty_text(name, "statement", payload.get("statement"))
    normalized["asset_types"] = _ensure_text_list(name, "asset_types", payload.get("asset_types"))
    normalized["applicable_industries"] = _ensure_text_list(name, "applicable_industries", payload.get("applicable_industries"))
    normalized["applicable_contexts"] = _ensure_text_list(name, "applicable_contexts", payload.get("applicable_contexts"))
    normalized["anti_triggers"] = _ensure_text_list(name, "anti_triggers", payload.get("anti_triggers"))
    normalized["falsification_conditions"] = _ensure_text_list(name, "falsification_conditions", payload.get("falsification_conditions"))
    normalized["minimum_evidence"] = _ensure_text_list(name, "minimum_evidence", payload.get("minimum_evidence"))
    normalized["financial_mechanism"] = _ensure_non_empty_text(name, "financial_mechanism", payload.get("financial_mechanism"))
    normalized["supporting_excerpt"] = _ensure_non_empty_text(name, "supporting_excerpt", payload.get("supporting_excerpt"))
    normalized["source_locator"] = _ensure_non_empty_text(name, "source_locator", payload.get("source_locator"))
    normalized["confidence_ceiling"] = _ensure_confidence_ceiling(name, "confidence_ceiling", payload.get("confidence_ceiling"))
    return normalized


def validate_pattern_candidate_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "pattern_candidate"
    _require_fields(name, payload, _REQUIRED_PATTERN_CANDIDATE_FIELDS)
    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["derived_from_atom_ids"] = _ensure_text_list(name, "derived_from_atom_ids", payload.get("derived_from_atom_ids"))
    normalized["name"] = _ensure_non_empty_text(name, "name", payload.get("name"))
    normalized["knowledge_types"] = _ensure_knowledge_types(name, "knowledge_types", payload.get("knowledge_types"))
    normalized["asset_types"] = _ensure_text_list(name, "asset_types", payload.get("asset_types"))
    normalized["applicable_contexts"] = _ensure_text_list(name, "applicable_contexts", payload.get("applicable_contexts"))
    normalized["hypothesis"] = _ensure_non_empty_text(name, "hypothesis", payload.get("hypothesis"))
    normalized["minimum_evidence"] = _ensure_text_list(name, "minimum_evidence", payload.get("minimum_evidence"))
    normalized["anti_triggers"] = _ensure_text_list(name, "anti_triggers", payload.get("anti_triggers"))
    normalized["falsification_conditions"] = _ensure_text_list(name, "falsification_conditions", payload.get("falsification_conditions"))
    normalized["financial_mechanism"] = _ensure_non_empty_text(name, "financial_mechanism", payload.get("financial_mechanism"))
    normalized["source_locator"] = _ensure_non_empty_text(name, "source_locator", payload.get("source_locator"))
    normalized["confidence_ceiling"] = _ensure_confidence_ceiling(name, "confidence_ceiling", payload.get("confidence_ceiling"))
    return normalized


def validate_combination_candidate_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "combination_candidate"
    _require_fields(name, payload, _REQUIRED_COMBINATION_CANDIDATE_FIELDS)
    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["derived_from_pattern_candidate_ids"] = _ensure_text_list(
        name,
        "derived_from_pattern_candidate_ids",
        payload.get("derived_from_pattern_candidate_ids"),
    )
    normalized["name"] = _ensure_non_empty_text(name, "name", payload.get("name"))
    normalized["combined_hypothesis"] = _ensure_non_empty_text(name, "combined_hypothesis", payload.get("combined_hypothesis"))
    normalized["minimum_evidence"] = _ensure_text_list(name, "minimum_evidence", payload.get("minimum_evidence"))
    normalized["financial_exposure"] = _ensure_text_list(name, "financial_exposure", payload.get("financial_exposure"))
    normalized["prohibited_claims"] = _ensure_text_list(name, "prohibited_claims", payload.get("prohibited_claims"))
    normalized["source_locator"] = _ensure_non_empty_text(name, "source_locator", payload.get("source_locator"))
    normalized["confidence_ceiling"] = _ensure_confidence_ceiling(name, "confidence_ceiling", payload.get("confidence_ceiling"))
    return normalized


def validate_knowledge_extraction_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "knowledge_extraction_record"
    _require_fields(name, payload, _REQUIRED_EXTRACTION_RECORD_FIELDS)

    review_status = _ensure_non_empty_text(name, "review_status", payload.get("review_status"))
    if review_status not in ALLOWED_EXTRACTION_REVIEW_STATUSES:
        raise RegistryValidationError(
            f"{name}.review_status must be one of: {', '.join(sorted(ALLOWED_EXTRACTION_REVIEW_STATUSES))}"
        )

    structured_prior_only = payload.get("structured_prior_only")
    if not isinstance(structured_prior_only, bool):
        raise RegistryValidationError(f"{name}.structured_prior_only must be a boolean")

    provenance_manifest = payload.get("provenance_manifest")
    if not isinstance(provenance_manifest, Mapping):
        raise RegistryValidationError(f"{name}.provenance_manifest must be an object")

    knowledge_atoms_raw = payload.get("knowledge_atoms")
    if not isinstance(knowledge_atoms_raw, list):
        raise RegistryValidationError(f"{name}.knowledge_atoms must be a list")
    knowledge_atoms = [validate_knowledge_atom(row) for row in knowledge_atoms_raw]

    pattern_candidates_raw = payload.get("pattern_candidate_records")
    if not isinstance(pattern_candidates_raw, list):
        raise RegistryValidationError(f"{name}.pattern_candidate_records must be a list")
    pattern_candidates = [validate_pattern_candidate_record(row) for row in pattern_candidates_raw]

    combination_candidates_raw = payload.get("combination_candidate_records")
    if not isinstance(combination_candidates_raw, list):
        raise RegistryValidationError(f"{name}.combination_candidate_records must be a list")
    combination_candidates = [validate_combination_candidate_record(row) for row in combination_candidates_raw]

    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["version"] = _ensure_non_empty_text(name, "version", payload.get("version"))
    normalized["source_basis_id"] = _ensure_non_empty_text(name, "source_basis_id", payload.get("source_basis_id"))
    normalized["provider_key"] = _ensure_non_empty_text(name, "provider_key", payload.get("provider_key"))
    normalized["document_title"] = _ensure_non_empty_text(name, "document_title", payload.get("document_title"))
    normalized["document_ref"] = _ensure_non_empty_text(name, "document_ref", payload.get("document_ref"))
    normalized["retrieval_purpose"] = _ensure_non_empty_text(name, "retrieval_purpose", payload.get("retrieval_purpose"))
    normalized["extraction_mode"] = _ensure_non_empty_text(name, "extraction_mode", payload.get("extraction_mode"))
    normalized["evidence_ceiling"] = _ensure_confidence_ceiling(name, "evidence_ceiling", payload.get("evidence_ceiling"))
    normalized["structured_prior_only"] = structured_prior_only
    normalized["provenance_manifest"] = dict(provenance_manifest)
    normalized["knowledge_atoms"] = knowledge_atoms
    normalized["pattern_candidate_records"] = pattern_candidates
    normalized["combination_candidate_records"] = combination_candidates
    normalized["review_status"] = review_status
    normalized["notes"] = _text(payload.get("notes"))
    return normalized
