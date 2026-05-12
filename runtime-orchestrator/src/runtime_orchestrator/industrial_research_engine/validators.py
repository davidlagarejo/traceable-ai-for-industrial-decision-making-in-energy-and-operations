"""Knowledge schema validator (V4 P0 item 4).

Enforces the rules in RECOVERY_V4_PHASE0_BACKLOG.md "Reglas absolutas":
  - every entry has `falsification_conditions` (non-empty)
  - every combination has `evidence_pack` (dict)
  - `claim_ceiling` capped at L2
  - asset_families / anti_families enforced via family_scope
  - prohibited_language defaults block ROI / savings tokens
  - source_basis is non-empty and well-formed

This is the only gate between a JSON file and knowledge_pending/. The
CLI (propose_knowledge.py) and the engine.propose_knowledge() function
both call validate_knowledge() / validate_combination().

V4 P0 design rule: the validator is strict but content-blind. It does
NOT decide WHICH falsification conditions are valid — only that some
are declared. The framework's downstream consumers (motor_054 +
motor_062) judge content quality.
"""
from __future__ import annotations

from typing import Any

from .family_scope import enforce_family_scope, is_known_family
from .schemas import (
    CLAIM_CEILINGS,
    KNOWLEDGE_KINDS,
    CombinationObject,
    KnowledgeObject,
)


class KnowledgeValidationError(ValueError):
    """Raised when a knowledge payload fails the validator."""


# Tokens that must NOT appear in `allowed_language` (V4 P0 §1 rule 5).
# Closing on these terms = framework-level violation.
_PROHIBITED_TOKENS_IN_ALLOWED_LANGUAGE: tuple[str, ...] = (
    "guaranteed savings",
    "% savings",
    "roi will be",
    "guaranteed roi",
    "payback within",
    "this will reduce",
    "this saves",
    "definite savings",
)


def _require_non_empty_text(name: str, field: str, value: Any) -> str:
    s = str(value or "").strip()
    if not s:
        raise KnowledgeValidationError(f"{name}.{field} must be non-empty text")
    return s


def _require_non_empty_list(name: str, field: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise KnowledgeValidationError(f"{name}.{field} must be a list")
    rows = [str(item).strip() for item in value if str(item).strip()]
    if not rows:
        raise KnowledgeValidationError(
            f"{name}.{field} must contain at least one non-empty value"
        )
    return rows


def _require_list(name: str, field: str, value: Any) -> list[str]:
    if not isinstance(value, list):
        raise KnowledgeValidationError(f"{name}.{field} must be a list")
    return [str(item).strip() for item in value if str(item).strip()]


def _require_dict(name: str, field: str, value: Any) -> dict[str, Any]:
    if not isinstance(value, dict):
        raise KnowledgeValidationError(f"{name}.{field} must be a dict")
    return dict(value)


def _check_prohibited_tokens_absent(name: str, field: str, text: str) -> None:
    lower = (text or "").lower()
    for token in _PROHIBITED_TOKENS_IN_ALLOWED_LANGUAGE:
        if token in lower:
            raise KnowledgeValidationError(
                f"{name}.{field} contains prohibited closure language "
                f"({token!r}). Framework does not permit ROI/savings closure."
            )


def _validate_source_basis(name: str, raw: Any) -> list[dict[str, Any]]:
    if not isinstance(raw, list) or not raw:
        raise KnowledgeValidationError(
            f"{name}.source_basis must be a non-empty list of "
            "{source_id, confidence} entries"
        )
    out: list[dict[str, Any]] = []
    for idx, entry in enumerate(raw):
        if not isinstance(entry, dict):
            raise KnowledgeValidationError(
                f"{name}.source_basis[{idx}] must be a dict with "
                "source_id + confidence"
            )
        sid = str(entry.get("source_id", "")).strip()
        if not sid:
            raise KnowledgeValidationError(
                f"{name}.source_basis[{idx}].source_id must be non-empty"
            )
        out.append({
            "source_id": sid,
            "confidence": str(entry.get("confidence", "medium")).strip().lower(),
            **{k: v for k, v in entry.items() if k not in {"source_id", "confidence"}},
        })
    return out


def _validate_base(payload: dict[str, Any]) -> dict[str, Any]:
    """Shared validation between knowledge objects and combinations."""
    name = str(payload.get("id") or "knowledge")
    out: dict[str, Any] = {}

    out["id"] = _require_non_empty_text(name, "id", payload.get("id"))
    out["version"] = _require_non_empty_text(name, "version", payload.get("version"))

    kind = _require_non_empty_text(name, "knowledge_kind", payload.get("knowledge_kind"))
    if kind not in KNOWLEDGE_KINDS:
        raise KnowledgeValidationError(
            f"{name}.knowledge_kind {kind!r} not in {KNOWLEDGE_KINDS}"
        )
    out["knowledge_kind"] = kind

    # asset_families + anti_families via family_scope (raises ValueError on bad data)
    try:
        af, nf = enforce_family_scope(
            payload.get("asset_families", []) or [],
            payload.get("anti_families", []) or [],
        )
    except ValueError as exc:
        raise KnowledgeValidationError(f"{name}.{exc}") from exc
    out["asset_families"] = af
    out["anti_families"] = nf

    # epistemic surface (mandatory)
    out["falsification_conditions"] = _require_non_empty_list(
        name, "falsification_conditions", payload.get("falsification_conditions")
    )
    out["evidence_required"] = _require_non_empty_list(
        name, "evidence_required", payload.get("evidence_required")
    )
    out["trigger_conditions"] = _require_non_empty_list(
        name, "trigger_conditions", payload.get("trigger_conditions")
    )
    out["anti_triggers"] = _require_list(name, "anti_triggers", payload.get("anti_triggers", []))

    # claim ceiling capped at L2
    ceiling = str(payload.get("claim_ceiling", "L2")).strip().upper()
    if ceiling not in CLAIM_CEILINGS:
        raise KnowledgeValidationError(
            f"{name}.claim_ceiling {ceiling!r} not in {CLAIM_CEILINGS} "
            "(L2 is the absolute cap)"
        )
    out["claim_ceiling"] = ceiling

    # TAD actions (allowed to be empty for non-actionable knowledge)
    out["tad_actions"] = _require_list(name, "tad_actions", payload.get("tad_actions", []))

    # financial_translation
    out["financial_translation"] = str(payload.get("financial_translation", "")).strip()

    # allowed_language (mandatory) — prohibited tokens checked
    allowed = _require_non_empty_text(name, "allowed_language", payload.get("allowed_language"))
    _check_prohibited_tokens_absent(name, "allowed_language", allowed)
    out["allowed_language"] = allowed

    # prohibited_language list
    out["prohibited_language"] = _require_list(
        name, "prohibited_language", payload.get("prohibited_language", [])
    )

    # source_basis (mandatory, validated)
    out["source_basis"] = _validate_source_basis(name, payload.get("source_basis", []))

    # extraction_metadata + notes (free-form, optional)
    out["extraction_metadata"] = dict(payload.get("extraction_metadata", {}) or {})
    out["notes"] = str(payload.get("notes", "")).strip()
    return out


def validate_knowledge(payload: dict[str, Any]) -> KnowledgeObject:
    """Validate a base knowledge object payload. Returns the dataclass."""
    if not isinstance(payload, dict):
        raise KnowledgeValidationError("payload must be a JSON object (dict)")
    if str(payload.get("knowledge_kind", "")).strip() == "combination":
        raise KnowledgeValidationError(
            "use validate_combination() for combination payloads"
        )
    normalized = _validate_base(payload)
    return KnowledgeObject.from_dict(normalized)


def validate_combination(payload: dict[str, Any]) -> CombinationObject:
    """Validate a combination payload. Combinations must additionally
    declare `required_patterns`, `combined_hypothesis`, and `evidence_pack`."""
    if not isinstance(payload, dict):
        raise KnowledgeValidationError("payload must be a JSON object (dict)")
    if str(payload.get("knowledge_kind", "")).strip() != "combination":
        raise KnowledgeValidationError(
            "validate_combination() requires knowledge_kind=='combination'"
        )
    normalized = _validate_base(payload)
    name = normalized["id"]

    # combination-specific fields
    normalized["required_patterns"] = _require_non_empty_list(
        name, "required_patterns", payload.get("required_patterns")
    )
    normalized["combined_hypothesis"] = _require_non_empty_text(
        name, "combined_hypothesis", payload.get("combined_hypothesis")
    )
    normalized["evidence_pack"] = _require_dict(
        name, "evidence_pack", payload.get("evidence_pack")
    )
    # gold_nugget is optional at proposal time (the framework can derive it)
    normalized["gold_nugget"] = str(payload.get("gold_nugget", "")).strip()
    normalized["prohibited_claims"] = _require_list(
        name, "prohibited_claims", payload.get("prohibited_claims", [])
    )
    normalized["preconditions"] = _require_list(
        name, "preconditions", payload.get("preconditions", [])
    )
    normalized["conditional_clause"] = str(payload.get("conditional_clause", "")).strip()
    normalized["layers_combined"] = _require_list(
        name, "layers_combined", payload.get("layers_combined", [])
    )
    return CombinationObject.from_dict(normalized)
