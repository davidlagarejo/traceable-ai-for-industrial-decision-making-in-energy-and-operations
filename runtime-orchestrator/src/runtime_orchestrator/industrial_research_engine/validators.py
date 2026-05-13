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


# V6 P6 — Combination Governance schema gate.
#
# Per V6 Stability prompt item 7: every combination must declare an
# extended schema before propose-time. Existing 4 combinations may not
# have all V6 fields (they were authored pre-V6); strict mode rejects
# any new combination that doesn't.

# 8 canonical action families (V5 P11 Phase 8 §7.2)
_CANONICAL_ACTION_FAMILIES: frozenset[str] = frozenset({
    "inspect", "measure", "classify", "pilot",
    "design", "procure", "implement", "defer",
})

_VALID_RENDER_MODES: frozenset[str] = frozenset({
    "exploratory_prior", "structural_hypothesis", "bounded_peer_analysis",
    "evidence_discrimination", "decision_blocked",
    "publish_bounded", "client_safe", "internal_debug_only",
})


def validate_combination_v6_strict(payload: dict[str, Any]) -> CombinationObject:
    """V6 P6 strict schema gate. Every combination MUST declare:

      - required_patterns (≥2)               ← validate_combination already
      - required_asset_family (str)          ← NEW V6
      - allowed_claim_ceiling ∈ {L0,L1,L2}   ← NEW V6
      - required_evidence_pack (str ref)     ← NEW V6
      - financial_translation (non-empty)    ← NEW V6
      - tad_mapping (list of action_family)  ← NEW V6, ∈ 8 canónicos
      - allowed_render_modes (list)          ← NEW V6
      - forbidden_render_modes (list)        ← NEW V6
      - combined_hypothesis (non-empty)      ← validate_combination already

    Reject if any field missing or malformed. Used by
    scripts/propose_combination.py at write-time so new combinations
    can never leak unchecked into combinations_pending/.

    The existing `validate_combination()` keeps its current behavior
    for backward compat with pre-V6 combinations (4 in registry today).
    """
    base = validate_combination(payload)  # delegates to standard validator
    name = base.id

    # NEW V6 fields:
    family = str(payload.get("required_asset_family", "")).strip()
    if not family:
        raise KnowledgeValidationError(
            f"{name}.required_asset_family is required (V6 P6 schema)"
        )

    ceiling = str(payload.get("allowed_claim_ceiling", "")).strip()
    if ceiling not in ("L0", "L1", "L2"):
        raise KnowledgeValidationError(
            f"{name}.allowed_claim_ceiling must be one of {{L0,L1,L2}} (got {ceiling!r})"
        )

    pack = str(payload.get("required_evidence_pack", "")).strip()
    if not pack:
        raise KnowledgeValidationError(
            f"{name}.required_evidence_pack is required (V6 P6 schema). "
            f"Provide an evidence_pack identifier (e.g., 'mhe_charging_pack')."
        )

    fin = str(payload.get("financial_translation", "")).strip()
    if not fin:
        raise KnowledgeValidationError(
            f"{name}.financial_translation is required (V6 P6 schema)"
        )

    tad_mapping = list(payload.get("tad_mapping", []) or [])
    if not tad_mapping:
        raise KnowledgeValidationError(
            f"{name}.tad_mapping is required (V6 P6 schema). "
            f"List of action_family values ∈ {sorted(_CANONICAL_ACTION_FAMILIES)}."
        )
    invalid_actions = [
        a for a in tad_mapping
        if str(a).strip().lower() not in _CANONICAL_ACTION_FAMILIES
    ]
    if invalid_actions:
        raise KnowledgeValidationError(
            f"{name}.tad_mapping contains non-canonical action families: "
            f"{invalid_actions}. Valid: {sorted(_CANONICAL_ACTION_FAMILIES)}"
        )

    allowed_modes = list(payload.get("allowed_render_modes", []) or [])
    if not allowed_modes:
        raise KnowledgeValidationError(
            f"{name}.allowed_render_modes is required (V6 P6 schema). "
            f"Valid modes: {sorted(_VALID_RENDER_MODES)}"
        )
    invalid_modes = [
        m for m in allowed_modes if str(m).strip() not in _VALID_RENDER_MODES
    ]
    if invalid_modes:
        raise KnowledgeValidationError(
            f"{name}.allowed_render_modes contains invalid modes: {invalid_modes}. "
            f"Valid: {sorted(_VALID_RENDER_MODES)}"
        )

    forbidden_modes = list(payload.get("forbidden_render_modes", []) or [])
    invalid_forbidden = [
        m for m in forbidden_modes if str(m).strip() not in _VALID_RENDER_MODES
    ]
    if invalid_forbidden:
        raise KnowledgeValidationError(
            f"{name}.forbidden_render_modes contains invalid modes: {invalid_forbidden}. "
            f"Valid: {sorted(_VALID_RENDER_MODES)}"
        )
    overlap = set(allowed_modes) & set(forbidden_modes)
    if overlap:
        raise KnowledgeValidationError(
            f"{name} has render modes in BOTH allowed and forbidden lists: {overlap}"
        )

    # required_patterns must have ≥2 (combination by definition)
    if len(base.required_patterns) < 2:
        raise KnowledgeValidationError(
            f"{name}.required_patterns must have ≥2 patterns (got {len(base.required_patterns)}). "
            "A combination by definition needs multiple co-occurring patterns."
        )

    return base

