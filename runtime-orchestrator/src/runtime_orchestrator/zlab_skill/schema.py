from __future__ import annotations

from typing import Any, Iterable, Mapping

ALLOWED_KNOWLEDGE_TYPES = {
    "ASSET_ARCHETYPE",
    "PROCESS_LOGIC",
    "LOSS_PATTERN",
    "FINANCIAL_TRANSLATION",
    "FAIR_COMPARISON_RULE",
    "MAINTENANCE_REALITY_PATTERN",
    "MEASUREMENT_MINIMALITY_RULE",
    "REGULATORY_PHYSICAL_SIGNAL",
    "CULTURE_EXECUTION_PROXY",
    "GOLD_NUGGET_TEMPLATE",
}

ALLOWED_PATTERN_CONFIDENCE_CEILINGS = {"L0", "L1", "L2"}
ALLOWED_MEMORY_TYPES = {
    "pattern_memory",
    "validation_memory",
    "company_memory",
    "source_memory",
    "contradiction_memory",
}
ALLOWED_MEMORY_POLICY_SCOPES = {
    "global_structured_prior",
    "company_confined",
    "run_confined",
    "provider_family",
    "asset_confined",
}
ALLOWED_MEMORY_TRANSFER_RULES = {
    "priority_only_cross_company",
    "same_company_only",
    "same_run_only",
    "provider_family_only",
    "same_asset_only",
}
ALLOWED_MEMORY_USE_MODES = {
    "priority_only",
    "context_only",
    "routing_only",
}
ALLOWED_COMBINATION_DECISIONS = {
    "candidate",
    "blocked_by_validator",
    "accepted_for_case_use",
    "rejected_for_case_use",
    "needs_review",
}

_REQUIRED_PATTERN_FIELDS = {
    "id",
    "version",
    "name",
    "knowledge_type",
    "asset_types",
    "applicable_industries",
    "applicable_contexts",
    "trigger_conditions",
    "anti_triggers",
    "physical_basis",
    "operational_basis",
    "financial_mechanism",
    "typical_false_assumption",
    "hypothesis",
    "rival_hypotheses",
    "evidence_required",
    "minimum_evidence_to_activate",
    "minimum_evidence_to_confirm",
    "falsification_conditions",
    "allowed_claim_language",
    "prohibited_claim_language",
    "financial_exposure_if_true",
    "financial_exposure_if_false",
    "tad_actions",
    "stop_conditions",
    "escalation_conditions",
    "source_basis",
    "confidence_ceiling",
    "claim_permissions_impact",
    "example_outputs",
    "tests",
}

_REQUIRED_COMBINATION_FIELDS = {
    "id",
    "version",
    "name",
    "pattern_ids",
    "trigger_logic",
    "anti_triggers",
    "combined_hypothesis",
    "strategic_risk",
    "minimum_evidence",
    "financial_exposure",
    "tad_action",
    "prohibited_claims",
    "allowed_language",
    "source_basis",
    "confidence_ceiling",
    "adjudication_required",
    "tests",
}

# V3 G7: combination schema v2 — optional fields that, when present,
# unlock richer activation semantics. All retro-compatible: existing
# combinations without these fields still validate.
_OPTIONAL_COMBINATION_FIELDS_V2 = {
    "evidence_pack",       # dict: {cheapest_valid_path, escalation_path, stop_condition, local_intake_trigger}
    "falsification",       # str — what would falsify the combined_hypothesis
    "gold_nugget",         # str — generated nugget when combination activates
    "comparison_impact",   # str — what fair-comparison rule this changes
    "preconditions",       # list[str] — pattern_ids that must be bounded BEFORE this combination activates
    "conditional_clause",  # str — natural-language "matters only if X is bounded"
    "layers_combined",     # list[str] — subset of [physics, ops, maintenance, finance, tariffs, reliability, control, regulation]
}

_ALLOWED_COMBINATION_LAYERS = {
    "physics", "ops", "maintenance", "finance",
    "tariffs", "reliability", "control", "regulation",
}

_REQUIRED_SOURCE_BASIS_FIELDS = {
    "id",
    "version",
    "source_family",
    "providers",
    "access_model",
    "provenance_requirements",
    "allowed_use",
    "prohibited_use",
    "evidence_ceiling",
    "extraction_rules",
}

_REQUIRED_MEMORY_POLICY_FIELDS = {
    "id",
    "version",
    "memory_type",
    "name",
    "description",
    "admissibility_scope",
    "transfer_rule",
    "evidence_ceiling",
    "use_mode",
    "truth_promotion_allowed",
    "reversible",
    "default_priority_effect",
    "required_record_fields",
    "tests",
}

_ALLOWED_VALIDATOR_SCOPES = {
    "combination_review",
    "report_output",
    "memory_scope",
    "scenario_review",
}

_ALLOWED_VALIDATOR_RULE_TYPES = {
    "required_list_non_empty",
    "required_text_non_empty",
    "allowed_values",
    "forbidden_terms_absent",
}

_REQUIRED_VALIDATOR_FIELDS = {
    "id",
    "version",
    "validator_name",
    "scope",
    "enabled",
    "severity",
    "rule_type",
    "description",
    "target_fields",
    "message",
    "tests",
}


class RegistryValidationError(ValueError):
    pass


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


def _ensure_list_of_text(name: str, field_name: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise RegistryValidationError(f"{name}.{field_name} must be a list")
    rows = [_text(item) for item in value if _text(item)]
    if not rows:
        raise RegistryValidationError(f"{name}.{field_name} must contain at least one non-empty value")
    return rows


def _ensure_non_empty_text(name: str, field_name: str, value: Any) -> str:
    text_value = _text(value)
    if not text_value:
        raise RegistryValidationError(f"{name}.{field_name} must be non-empty")
    return text_value


def _ensure_knowledge_types(name: str, values: Iterable[str]) -> list[str]:
    rows = [_text(item) for item in values if _text(item)]
    unknown = sorted(set(rows).difference(ALLOWED_KNOWLEDGE_TYPES))
    if unknown:
        raise RegistryValidationError(f"{name}.knowledge_type contains unsupported values: {', '.join(unknown)}")
    return rows


def validate_pattern_spec(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "pattern"
    _require_fields(name, payload, _REQUIRED_PATTERN_FIELDS)
    knowledge_type = _ensure_knowledge_types(name, _ensure_list_of_text(name, "knowledge_type", payload.get("knowledge_type")))
    confidence_ceiling = _ensure_non_empty_text(name, "confidence_ceiling", payload.get("confidence_ceiling"))
    if confidence_ceiling not in ALLOWED_PATTERN_CONFIDENCE_CEILINGS:
        raise RegistryValidationError(
            f"{name}.confidence_ceiling must stay within L0/L1/L2, got {confidence_ceiling}"
        )
    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["version"] = _ensure_non_empty_text(name, "version", payload.get("version"))
    normalized["name"] = _ensure_non_empty_text(name, "name", payload.get("name"))
    normalized["knowledge_type"] = knowledge_type
    normalized["asset_types"] = _ensure_list_of_text(name, "asset_types", payload.get("asset_types"))
    normalized["applicable_industries"] = _ensure_list_of_text(name, "applicable_industries", payload.get("applicable_industries"))
    normalized["applicable_contexts"] = _ensure_list_of_text(name, "applicable_contexts", payload.get("applicable_contexts"))
    normalized["trigger_conditions"] = _ensure_list_of_text(name, "trigger_conditions", payload.get("trigger_conditions"))
    normalized["anti_triggers"] = _ensure_list_of_text(name, "anti_triggers", payload.get("anti_triggers"))
    normalized["physical_basis"] = _ensure_non_empty_text(name, "physical_basis", payload.get("physical_basis"))
    normalized["operational_basis"] = _ensure_non_empty_text(name, "operational_basis", payload.get("operational_basis"))
    normalized["financial_mechanism"] = _ensure_non_empty_text(name, "financial_mechanism", payload.get("financial_mechanism"))
    normalized["typical_false_assumption"] = _ensure_non_empty_text(name, "typical_false_assumption", payload.get("typical_false_assumption"))
    normalized["hypothesis"] = _ensure_non_empty_text(name, "hypothesis", payload.get("hypothesis"))
    normalized["rival_hypotheses"] = _ensure_list_of_text(name, "rival_hypotheses", payload.get("rival_hypotheses"))
    normalized["evidence_required"] = _ensure_list_of_text(name, "evidence_required", payload.get("evidence_required"))
    normalized["minimum_evidence_to_activate"] = _ensure_list_of_text(name, "minimum_evidence_to_activate", payload.get("minimum_evidence_to_activate"))
    normalized["minimum_evidence_to_confirm"] = _ensure_list_of_text(name, "minimum_evidence_to_confirm", payload.get("minimum_evidence_to_confirm"))
    normalized["falsification_conditions"] = _ensure_list_of_text(name, "falsification_conditions", payload.get("falsification_conditions"))
    normalized["allowed_claim_language"] = _ensure_non_empty_text(name, "allowed_claim_language", payload.get("allowed_claim_language"))
    normalized["prohibited_claim_language"] = _ensure_non_empty_text(name, "prohibited_claim_language", payload.get("prohibited_claim_language"))
    normalized["financial_exposure_if_true"] = _ensure_list_of_text(name, "financial_exposure_if_true", payload.get("financial_exposure_if_true"))
    normalized["financial_exposure_if_false"] = _ensure_list_of_text(name, "financial_exposure_if_false", payload.get("financial_exposure_if_false"))
    normalized["tad_actions"] = _ensure_list_of_text(name, "tad_actions", payload.get("tad_actions"))
    normalized["stop_conditions"] = _ensure_list_of_text(name, "stop_conditions", payload.get("stop_conditions"))
    normalized["escalation_conditions"] = _ensure_list_of_text(name, "escalation_conditions", payload.get("escalation_conditions"))
    normalized["source_basis"] = _ensure_list_of_text(name, "source_basis", payload.get("source_basis"))
    normalized["confidence_ceiling"] = confidence_ceiling
    normalized["claim_permissions_impact"] = _ensure_list_of_text(name, "claim_permissions_impact", payload.get("claim_permissions_impact"))
    normalized["example_outputs"] = _ensure_list_of_text(name, "example_outputs", payload.get("example_outputs"))
    normalized["tests"] = _ensure_list_of_text(name, "tests", payload.get("tests"))
    return normalized


def validate_combination_spec(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "combination"
    _require_fields(name, payload, _REQUIRED_COMBINATION_FIELDS)
    confidence_ceiling = _ensure_non_empty_text(name, "confidence_ceiling", payload.get("confidence_ceiling"))
    if confidence_ceiling not in ALLOWED_PATTERN_CONFIDENCE_CEILINGS:
        raise RegistryValidationError(
            f"{name}.confidence_ceiling must stay within L0/L1/L2, got {confidence_ceiling}"
        )
    adjudication_required = payload.get("adjudication_required")
    if not isinstance(adjudication_required, bool):
        raise RegistryValidationError(f"{name}.adjudication_required must be a boolean")
    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["version"] = _ensure_non_empty_text(name, "version", payload.get("version"))
    normalized["name"] = _ensure_non_empty_text(name, "name", payload.get("name"))
    normalized["pattern_ids"] = _ensure_list_of_text(name, "pattern_ids", payload.get("pattern_ids"))
    normalized["trigger_logic"] = _ensure_list_of_text(name, "trigger_logic", payload.get("trigger_logic"))
    normalized["anti_triggers"] = _ensure_list_of_text(name, "anti_triggers", payload.get("anti_triggers"))
    normalized["combined_hypothesis"] = _ensure_non_empty_text(name, "combined_hypothesis", payload.get("combined_hypothesis"))
    normalized["strategic_risk"] = _ensure_non_empty_text(name, "strategic_risk", payload.get("strategic_risk"))
    normalized["minimum_evidence"] = _ensure_list_of_text(name, "minimum_evidence", payload.get("minimum_evidence"))
    normalized["financial_exposure"] = _ensure_list_of_text(name, "financial_exposure", payload.get("financial_exposure"))
    normalized["tad_action"] = _ensure_non_empty_text(name, "tad_action", payload.get("tad_action"))
    normalized["prohibited_claims"] = _ensure_list_of_text(name, "prohibited_claims", payload.get("prohibited_claims"))
    normalized["allowed_language"] = _ensure_non_empty_text(name, "allowed_language", payload.get("allowed_language"))
    normalized["source_basis"] = _ensure_list_of_text(name, "source_basis", payload.get("source_basis"))
    normalized["confidence_ceiling"] = confidence_ceiling
    normalized["adjudication_required"] = adjudication_required
    normalized["tests"] = _ensure_list_of_text(name, "tests", payload.get("tests"))

    # V3 G7: validate optional v2 fields if present. Silently ignored when absent.
    if "evidence_pack" in payload:
        ep = payload.get("evidence_pack")
        if not isinstance(ep, dict):
            raise RegistryValidationError(f"{name}.evidence_pack must be a dict")
        normalized["evidence_pack"] = ep
    if "falsification" in payload:
        normalized["falsification"] = _ensure_non_empty_text(name, "falsification", payload.get("falsification"))
    if "gold_nugget" in payload:
        normalized["gold_nugget"] = _ensure_non_empty_text(name, "gold_nugget", payload.get("gold_nugget"))
    if "comparison_impact" in payload:
        normalized["comparison_impact"] = _ensure_non_empty_text(name, "comparison_impact", payload.get("comparison_impact"))
    if "preconditions" in payload:
        normalized["preconditions"] = _ensure_list_of_text(name, "preconditions", payload.get("preconditions"))
    if "conditional_clause" in payload:
        normalized["conditional_clause"] = _ensure_non_empty_text(name, "conditional_clause", payload.get("conditional_clause"))
    if "layers_combined" in payload:
        layers = _ensure_list_of_text(name, "layers_combined", payload.get("layers_combined"))
        unknown = sorted(set(layers) - _ALLOWED_COMBINATION_LAYERS)
        if unknown:
            raise RegistryValidationError(
                f"{name}.layers_combined contains unknown layer(s): {unknown}. "
                f"Allowed: {sorted(_ALLOWED_COMBINATION_LAYERS)}"
            )
        normalized["layers_combined"] = layers

    return normalized


def validate_source_basis_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "source_basis"
    _require_fields(name, payload, _REQUIRED_SOURCE_BASIS_FIELDS)
    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["version"] = _ensure_non_empty_text(name, "version", payload.get("version"))
    normalized["source_family"] = _ensure_non_empty_text(name, "source_family", payload.get("source_family"))
    normalized["providers"] = _ensure_list_of_text(name, "providers", payload.get("providers"))
    normalized["access_model"] = _ensure_non_empty_text(name, "access_model", payload.get("access_model"))
    normalized["provenance_requirements"] = _ensure_list_of_text(name, "provenance_requirements", payload.get("provenance_requirements"))
    normalized["allowed_use"] = _ensure_list_of_text(name, "allowed_use", payload.get("allowed_use"))
    normalized["prohibited_use"] = _ensure_list_of_text(name, "prohibited_use", payload.get("prohibited_use"))
    normalized["evidence_ceiling"] = _ensure_non_empty_text(name, "evidence_ceiling", payload.get("evidence_ceiling"))
    normalized["extraction_rules"] = _ensure_list_of_text(name, "extraction_rules", payload.get("extraction_rules"))
    return normalized


def validate_memory_policy_record(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "memory_policy"
    _require_fields(name, payload, _REQUIRED_MEMORY_POLICY_FIELDS)

    truth_promotion_allowed = payload.get("truth_promotion_allowed")
    if not isinstance(truth_promotion_allowed, bool):
        raise RegistryValidationError(f"{name}.truth_promotion_allowed must be a boolean")

    reversible = payload.get("reversible")
    if not isinstance(reversible, bool):
        raise RegistryValidationError(f"{name}.reversible must be a boolean")

    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["version"] = _ensure_non_empty_text(name, "version", payload.get("version"))
    normalized["memory_type"] = _ensure_non_empty_text(name, "memory_type", payload.get("memory_type"))
    if normalized["memory_type"] not in ALLOWED_MEMORY_TYPES:
        raise RegistryValidationError(
            f"{name}.memory_type contains unsupported value: {normalized['memory_type']}"
        )
    normalized["name"] = _ensure_non_empty_text(name, "name", payload.get("name"))
    normalized["description"] = _ensure_non_empty_text(name, "description", payload.get("description"))
    normalized["admissibility_scope"] = _ensure_non_empty_text(
        name,
        "admissibility_scope",
        payload.get("admissibility_scope"),
    )
    if normalized["admissibility_scope"] not in ALLOWED_MEMORY_POLICY_SCOPES:
        raise RegistryValidationError(
            f"{name}.admissibility_scope contains unsupported value: {normalized['admissibility_scope']}"
        )
    normalized["transfer_rule"] = _ensure_non_empty_text(name, "transfer_rule", payload.get("transfer_rule"))
    if normalized["transfer_rule"] not in ALLOWED_MEMORY_TRANSFER_RULES:
        raise RegistryValidationError(
            f"{name}.transfer_rule contains unsupported value: {normalized['transfer_rule']}"
        )
    normalized["evidence_ceiling"] = _ensure_non_empty_text(name, "evidence_ceiling", payload.get("evidence_ceiling"))
    if normalized["evidence_ceiling"] not in ALLOWED_PATTERN_CONFIDENCE_CEILINGS:
        raise RegistryValidationError(
            f"{name}.evidence_ceiling must stay within L0/L1/L2, got {normalized['evidence_ceiling']}"
        )
    normalized["use_mode"] = _ensure_non_empty_text(name, "use_mode", payload.get("use_mode"))
    if normalized["use_mode"] not in ALLOWED_MEMORY_USE_MODES:
        raise RegistryValidationError(
            f"{name}.use_mode contains unsupported value: {normalized['use_mode']}"
        )
    normalized["truth_promotion_allowed"] = truth_promotion_allowed
    normalized["reversible"] = reversible
    normalized["default_priority_effect"] = _ensure_non_empty_text(
        name,
        "default_priority_effect",
        payload.get("default_priority_effect"),
    )
    normalized["required_record_fields"] = _ensure_list_of_text(
        name,
        "required_record_fields",
        payload.get("required_record_fields"),
    )
    normalized["tests"] = _ensure_list_of_text(name, "tests", payload.get("tests"))
    return normalized


def validate_validator_spec(payload: Mapping[str, Any]) -> dict[str, Any]:
    name = _text(payload.get("id")) or "validator"
    _require_fields(name, payload, _REQUIRED_VALIDATOR_FIELDS)
    enabled = payload.get("enabled")
    if not isinstance(enabled, bool):
        raise RegistryValidationError(f"{name}.enabled must be a boolean")

    normalized = dict(payload)
    normalized["id"] = _ensure_non_empty_text(name, "id", payload.get("id"))
    normalized["version"] = _ensure_non_empty_text(name, "version", payload.get("version"))
    normalized["validator_name"] = _ensure_non_empty_text(name, "validator_name", payload.get("validator_name"))
    normalized["scope"] = _ensure_non_empty_text(name, "scope", payload.get("scope"))
    if normalized["scope"] not in _ALLOWED_VALIDATOR_SCOPES:
        raise RegistryValidationError(
            f"{name}.scope contains unsupported value: {normalized['scope']}"
        )
    normalized["enabled"] = enabled
    normalized["severity"] = _ensure_non_empty_text(name, "severity", payload.get("severity"))
    normalized["rule_type"] = _ensure_non_empty_text(name, "rule_type", payload.get("rule_type"))
    if normalized["rule_type"] not in _ALLOWED_VALIDATOR_RULE_TYPES:
        raise RegistryValidationError(
            f"{name}.rule_type contains unsupported value: {normalized['rule_type']}"
        )
    normalized["description"] = _ensure_non_empty_text(name, "description", payload.get("description"))
    normalized["target_fields"] = _ensure_list_of_text(name, "target_fields", payload.get("target_fields"))
    normalized["message"] = _ensure_non_empty_text(name, "message", payload.get("message"))
    normalized["tests"] = _ensure_list_of_text(name, "tests", payload.get("tests"))
    normalized["allowed_values"] = _ensure_list_of_text(name, "allowed_values", payload.get("allowed_values")) if "allowed_values" in payload else []
    normalized["forbidden_terms"] = _ensure_list_of_text(name, "forbidden_terms", payload.get("forbidden_terms")) if "forbidden_terms" in payload else []
    return normalized
