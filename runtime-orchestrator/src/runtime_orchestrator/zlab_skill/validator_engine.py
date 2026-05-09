from __future__ import annotations

from typing import Any


_FALLBACK_COMBINATION_VALIDATOR_SPECS = [
    {
        "validator_name": "SourceTraceabilityValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "required_list_non_empty",
        "target_fields": ["source_basis"],
        "message": "Combination is missing source_basis provenance.",
    },
    {
        "validator_name": "PatternToClaimValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "required_text_non_empty",
        "target_fields": ["allowed_language"],
        "message": "Combination is missing bounded allowed_language.",
    },
    {
        "validator_name": "FairComparisonValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "required_list_non_empty",
        "target_fields": ["prohibited_claims"],
        "message": "Combination is missing prohibited_claims constraints.",
    },
    {
        "validator_name": "ClaimGovernorValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "required_list_non_empty",
        "target_fields": ["minimum_evidence"],
        "message": "Combination is missing minimum_evidence.",
    },
    {
        "validator_name": "TADConsistencyValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "required_text_non_empty",
        "target_fields": ["tad_action"],
        "message": "Combination is missing tad_action.",
    },
    {
        "validator_name": "CombinationUseValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "allowed_values",
        "target_fields": ["evidence_state_ceiling"],
        "allowed_values": ["L0", "L1", "L2"],
        "message": "Combination ceiling must stay in L0/L1/L2.",
    },
    {
        "validator_name": "FinancialOutputValidator",
        "scope": "combination_review",
        "enabled": True,
        "severity": "error",
        "rule_type": "forbidden_terms_absent",
        "target_fields": ["combined_hypothesis", "strategic_risk", "allowed_language"],
        "forbidden_terms": ["roi", "irr", "npv", "payback"],
        "message": "Combination field contains forbidden financial term.",
    },
]

_FALLBACK_MEMORY_SCOPE_VALIDATOR_SPECS = [
    {
        "validator_name": "MemoryScopeValidator",
        "scope": "memory_scope",
        "enabled": True,
        "severity": "error",
        "rule_type": "required_text_non_empty",
        "target_fields": ["scope"],
        "message": "Memory record is missing scope.",
    }
]


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _contains_forbidden_term(value: str, forbidden_terms: list[str]) -> str:
    lowered = _text(value).lower()
    for token in list(forbidden_terms or []):
        normalized = _text(token).lower()
        if normalized and normalized in lowered:
            return normalized
    return ""


def _validator_specs_for_scope(
    *,
    registry_bundle: dict[str, Any] | None,
    scope: str,
) -> list[dict[str, Any]]:
    rows = [
        dict(row)
        for row in list((registry_bundle or {}).get("validators", []) or [])
        if _text(row.get("scope")) == _text(scope) and bool(row.get("enabled", False))
    ]
    if rows:
        return rows
    fallback_specs: list[dict[str, Any]] = []
    if _text(scope) == "combination_review":
        fallback_specs = _FALLBACK_COMBINATION_VALIDATOR_SPECS
    elif _text(scope) == "memory_scope":
        fallback_specs = _FALLBACK_MEMORY_SCOPE_VALIDATOR_SPECS
    return [dict(row) for row in fallback_specs if _text(row.get("scope")) == _text(scope)]


def _run_validator_spec(
    row: dict[str, Any],
    validator_spec: dict[str, Any],
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    validator_name = _text(validator_spec.get("validator_name")) or "Validator"
    severity = _text(validator_spec.get("severity")) or "error"
    rule_type = _text(validator_spec.get("rule_type"))
    target_fields = list(validator_spec.get("target_fields", []) or [])
    message = _text(validator_spec.get("message")) or f"{validator_name} failed."

    if rule_type == "required_list_non_empty":
        for field_name in target_fields:
            if list(row.get(field_name, []) or []):
                continue
            findings.append(
                {
                    "validator": validator_name,
                    "severity": severity,
                    "message": message,
                    "field": _text(field_name),
                }
            )
            break
    elif rule_type == "required_text_non_empty":
        for field_name in target_fields:
            if _text(row.get(field_name)):
                continue
            findings.append(
                {
                    "validator": validator_name,
                    "severity": severity,
                    "message": message,
                    "field": _text(field_name),
                }
            )
            break
    elif rule_type == "allowed_values":
        allowed_values = {_text(value) for value in list(validator_spec.get("allowed_values", []) or []) if _text(value)}
        for field_name in target_fields:
            current = _text(row.get(field_name))
            if current in allowed_values:
                continue
            findings.append(
                {
                    "validator": validator_name,
                    "severity": severity,
                    "message": f"{message} Got {current or 'empty'}.",
                    "field": _text(field_name),
                }
            )
            break
    elif rule_type == "forbidden_terms_absent":
        forbidden_terms = list(validator_spec.get("forbidden_terms", []) or [])
        for field_name in target_fields:
            token = _contains_forbidden_term(_text(row.get(field_name)), forbidden_terms)
            if not token:
                continue
            findings.append(
                {
                    "validator": validator_name,
                    "severity": severity,
                    "message": f"{message} Field {field_name} contains {token}.",
                    "field": _text(field_name),
                }
            )
            break
    return findings


def validate_combination_row(
    row: dict[str, Any],
    *,
    registry_bundle: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return validate_row_for_scope(
        row,
        scope="combination_review",
        registry_bundle=registry_bundle,
    )


def validate_row_for_scope(
    row: dict[str, Any],
    *,
    scope: str,
    registry_bundle: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    findings: list[dict[str, Any]] = []
    for validator_spec in _validator_specs_for_scope(
        registry_bundle=registry_bundle,
        scope=scope,
    ):
        findings.extend(_run_validator_spec(row, validator_spec))
    return findings


def apply_combination_validators(
    combination_activation_register: list[dict[str, Any]] | None,
    *,
    registry_bundle: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    return apply_validators_for_scope(
        combination_activation_register,
        scope="combination_review",
        registry_bundle=registry_bundle,
    )


def apply_validators_for_scope(
    rows_to_validate: list[dict[str, Any]] | None,
    *,
    scope: str,
    registry_bundle: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for row in list(rows_to_validate or []):
        normalized = dict(row)
        findings = validate_row_for_scope(
            normalized,
            scope=scope,
            registry_bundle=registry_bundle,
        )
        normalized["validator_findings"] = findings
        normalized["validator_state"] = "blocked" if findings else "passed"
        rows.append(normalized)
    return rows
