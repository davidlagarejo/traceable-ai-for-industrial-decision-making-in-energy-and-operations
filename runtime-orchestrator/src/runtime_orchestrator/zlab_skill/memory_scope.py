from __future__ import annotations

from typing import Any, Mapping

from .schema import (
    ALLOWED_MEMORY_POLICY_SCOPES,
    ALLOWED_MEMORY_TRANSFER_RULES,
    ALLOWED_MEMORY_TYPES,
    ALLOWED_PATTERN_CONFIDENCE_CEILINGS,
    RegistryValidationError,
)
from .validator_engine import validate_row_for_scope


ALLOWED_MEMORY_RECORD_STATUSES = {
    "active",
    "reversed",
}

_REQUIRED_MEMORY_RECORD_FIELDS = {
    "id",
    "version",
    "memory_type",
    "policy_id",
    "scope",
    "subject_key",
    "source_refs",
    "reason",
    "reversible",
    "created_at",
    "status",
}

_EVIDENCE_ORDER = {
    "L0": 0,
    "L1": 1,
    "L2": 2,
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


def _policy_for_record(
    *,
    name: str,
    policy_id: str,
    registry_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    bundle = dict(registry_bundle or {})
    policy = dict((bundle.get("memory_policies_by_id", {}) or {}).get(policy_id, {}) or {})
    if not policy:
        raise RegistryValidationError(f"{name}.policy_id references unknown memory policy: {policy_id}")
    return policy


def _ceiling_not_above_policy(record_ceiling: str, policy_ceiling: str) -> bool:
    return _EVIDENCE_ORDER.get(record_ceiling, -1) <= _EVIDENCE_ORDER.get(policy_ceiling, -1)


def validate_memory_record(
    payload: Mapping[str, Any],
    *,
    registry_bundle: dict[str, Any] | None = None,
) -> dict[str, Any]:
    name = _text(payload.get("id")) or "memory_record"
    _require_fields(name, payload, _REQUIRED_MEMORY_RECORD_FIELDS)

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
    normalized["policy_id"] = _ensure_non_empty_text(name, "policy_id", payload.get("policy_id"))
    normalized["scope"] = _ensure_non_empty_text(name, "scope", payload.get("scope"))
    if normalized["scope"] not in ALLOWED_MEMORY_POLICY_SCOPES:
        raise RegistryValidationError(f"{name}.scope contains unsupported value: {normalized['scope']}")
    normalized["subject_key"] = _ensure_non_empty_text(name, "subject_key", payload.get("subject_key"))
    normalized["source_refs"] = _ensure_text_list(name, "source_refs", payload.get("source_refs"))
    normalized["reason"] = _ensure_non_empty_text(name, "reason", payload.get("reason"))
    normalized["reversible"] = reversible
    normalized["created_at"] = _ensure_non_empty_text(name, "created_at", payload.get("created_at"))
    normalized["status"] = _ensure_non_empty_text(name, "status", payload.get("status"))
    if normalized["status"] not in ALLOWED_MEMORY_RECORD_STATUSES:
        raise RegistryValidationError(
            f"{name}.status must be one of: {', '.join(sorted(ALLOWED_MEMORY_RECORD_STATUSES))}"
        )
    normalized["company_id"] = _text(payload.get("company_id"))
    normalized["asset_id"] = _text(payload.get("asset_id"))
    normalized["run_id"] = _text(payload.get("run_id"))
    normalized["provider_key"] = _text(payload.get("provider_key"))
    normalized["pattern_ids"] = _ensure_text_list(name, "pattern_ids", payload.get("pattern_ids", []), allow_empty=True)
    normalized["contradiction_tags"] = _ensure_text_list(
        name,
        "contradiction_tags",
        payload.get("contradiction_tags", []),
        allow_empty=True,
    )
    normalized["validation_outcome"] = _text(payload.get("validation_outcome"))
    normalized["reversal_reason"] = _text(payload.get("reversal_reason"))
    normalized["notes"] = _text(payload.get("notes"))

    policy = _policy_for_record(
        name=name,
        policy_id=normalized["policy_id"],
        registry_bundle=registry_bundle,
    )
    normalized["policy_name"] = _text(policy.get("name"))
    normalized["transfer_rule"] = _text(policy.get("transfer_rule"))
    if normalized["transfer_rule"] not in ALLOWED_MEMORY_TRANSFER_RULES:
        raise RegistryValidationError(
            f"{name}.transfer_rule contains unsupported value: {normalized['transfer_rule']}"
        )
    normalized["use_mode"] = _text(policy.get("use_mode"))
    normalized["default_priority_effect"] = _text(policy.get("default_priority_effect"))
    normalized["truth_promotion_allowed"] = bool(policy.get("truth_promotion_allowed", False))
    if normalized["truth_promotion_allowed"]:
        raise RegistryValidationError(f"{name} cannot allow truth promotion.")
    if normalized["memory_type"] != _text(policy.get("memory_type")):
        raise RegistryValidationError(
            f"{name}.memory_type does not match policy {normalized['policy_id']}"
        )
    if normalized["scope"] != _text(policy.get("admissibility_scope")):
        raise RegistryValidationError(
            f"{name}.scope must match policy admissibility_scope {policy.get('admissibility_scope')}"
        )
    if bool(policy.get("reversible", False)) and not normalized["reversible"]:
        raise RegistryValidationError(f"{name}.reversible must stay true under policy {normalized['policy_id']}")
    for required_field in list(policy.get("required_record_fields", []) or []):
        field_name = _text(required_field)
        if not field_name:
            continue
        field_value = normalized.get(field_name)
        if isinstance(field_value, list):
            if field_value:
                continue
        elif _text(field_value):
            continue
        elif isinstance(field_value, bool):
            continue
        raise RegistryValidationError(f"{name} is missing policy-required field content: {field_name}")

    normalized["evidence_ceiling"] = _text(payload.get("evidence_ceiling")) or _text(policy.get("evidence_ceiling"))
    if normalized["evidence_ceiling"] not in ALLOWED_PATTERN_CONFIDENCE_CEILINGS:
        raise RegistryValidationError(
            f"{name}.evidence_ceiling must stay within L0/L1/L2, got {normalized['evidence_ceiling']}"
        )
    if not _ceiling_not_above_policy(normalized["evidence_ceiling"], _text(policy.get("evidence_ceiling"))):
        raise RegistryValidationError(
            f"{name}.evidence_ceiling cannot exceed policy ceiling {policy.get('evidence_ceiling')}"
        )
    if normalized["status"] == "reversed" and not normalized["reversal_reason"]:
        raise RegistryValidationError(f"{name}.reversal_reason is required when status is reversed")

    if normalized["memory_type"] in {"validation_memory", "company_memory", "contradiction_memory"} and not normalized["company_id"]:
        raise RegistryValidationError(f"{name}.company_id is required for {normalized['memory_type']}")
    if normalized["scope"] == "run_confined" and not normalized["run_id"]:
        raise RegistryValidationError(f"{name}.run_id is required for run-confined memory")
    if normalized["scope"] == "provider_family" and not normalized["provider_key"]:
        raise RegistryValidationError(f"{name}.provider_key is required for provider-family memory")

    validator_findings = validate_row_for_scope(
        normalized,
        scope="memory_scope",
        registry_bundle=registry_bundle,
    )
    normalized["memory_validator_findings"] = validator_findings
    normalized["memory_validator_state"] = "blocked" if validator_findings else "passed"
    return normalized


def evaluate_memory_record_scope(
    memory_record: Mapping[str, Any],
    *,
    current_context: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    record = dict(memory_record)
    context = dict(current_context or {})

    current_company_id = _text(context.get("company_id"))
    current_asset_id = _text(context.get("asset_id"))
    current_run_id = _text(context.get("run_id"))
    provider_keys = {
        _text(value)
        for value in list(context.get("provider_keys", []) or [])
        if _text(value)
    }
    if _text(context.get("provider_key")):
        provider_keys.add(_text(context.get("provider_key")))

    company_match = bool(record.get("company_id")) and _text(record.get("company_id")) == current_company_id
    asset_match = bool(record.get("asset_id")) and _text(record.get("asset_id")) == current_asset_id
    run_match = bool(record.get("run_id")) and _text(record.get("run_id")) == current_run_id
    provider_match = bool(record.get("provider_key")) and (
        not provider_keys or _text(record.get("provider_key")) in provider_keys
    )

    admissibility_state = "admissible"
    blocked_reason = ""
    match_basis = "global_prior"

    if _text(record.get("status")) != "active":
        admissibility_state = "blocked"
        blocked_reason = "Memory record is not active."
        match_basis = "inactive"
    elif _text(record.get("memory_validator_state")) == "blocked":
        admissibility_state = "blocked"
        blocked_reason = "Memory record failed memory-scope validators."
        match_basis = "validator_block"
    else:
        transfer_rule = _text(record.get("transfer_rule"))
        if transfer_rule == "priority_only_cross_company":
            match_basis = "cross_company_structured_prior"
        elif transfer_rule == "same_company_only":
            if company_match:
                match_basis = "same_company"
            else:
                admissibility_state = "blocked"
                blocked_reason = "Cross-company transfer is not allowed for this memory."
                match_basis = "cross_company_blocked"
        elif transfer_rule == "same_asset_only":
            if asset_match:
                match_basis = "same_asset"
            else:
                admissibility_state = "blocked"
                blocked_reason = "Memory is asset-confined and asset did not match."
                match_basis = "asset_mismatch"
        elif transfer_rule == "same_run_only":
            if run_match:
                match_basis = "same_run"
            else:
                admissibility_state = "blocked"
                blocked_reason = "Memory is run-confined and run_id did not match."
                match_basis = "run_mismatch"
        elif transfer_rule == "provider_family_only":
            if provider_match:
                match_basis = "provider_family"
            else:
                admissibility_state = "blocked"
                blocked_reason = "Memory is provider-scoped and provider did not match."
                match_basis = "provider_mismatch"
        else:
            admissibility_state = "blocked"
            blocked_reason = f"Unsupported transfer rule: {transfer_rule}"
            match_basis = "unsupported_rule"

    return {
        "memory_id": _text(record.get("id")),
        "memory_type": _text(record.get("memory_type")),
        "policy_id": _text(record.get("policy_id")),
        "policy_name": _text(record.get("policy_name")),
        "subject_key": _text(record.get("subject_key")),
        "scope": _text(record.get("scope")),
        "admissibility_state": admissibility_state,
        "use_mode": _text(record.get("use_mode")) or "context_only",
        "certainty_effect": "no_truth_upgrade",
        "truth_promotion_allowed": False,
        "evidence_ceiling": _text(record.get("evidence_ceiling")) or "L2",
        "default_priority_effect": _text(record.get("default_priority_effect")),
        "blocked_reason": blocked_reason,
        "match_basis": match_basis,
        "company_match": company_match,
        "asset_match": asset_match,
        "run_match": run_match,
        "provider_match": provider_match,
        "source_refs": list(record.get("source_refs", []) or []),
        "pattern_ids": list(record.get("pattern_ids", []) or []),
        "contradiction_tags": list(record.get("contradiction_tags", []) or []),
        "reason": _text(record.get("reason")),
        "validation_outcome": _text(record.get("validation_outcome")),
        "memory_validator_state": _text(record.get("memory_validator_state")) or "not_run",
        "memory_validator_findings": list(record.get("memory_validator_findings", []) or []),
    }
