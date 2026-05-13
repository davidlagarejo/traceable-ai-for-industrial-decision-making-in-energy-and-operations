"""V7 P4 — Hybrid Justification Narrative Emitter.

V7 Final Curation prompt § 1.B: cuando un híbrido cross-asset-family
se admite, NO basta con un booleano `hybrid_admissible=True`. El
framework debe emitir una explicación de PORQUÉ se activa la lógica
secundaria — la "frase canónica WHY_THIS_LOGIC_IS_ACTIVE".

Forma canónica:

    "This facility activates {secondary} logic because {evidence_chain}
     suggests cross-system operation beyond {primary}-only deployment.
     {rationale_from_hybrid_spec}"

Reglas:
  - Tokens listados son los `justification_triggers` que SÍ aparecieron
    en `motor_007.target_definition_contract.facility_evidence_tokens`
    o equivalente. Si no hay matched tokens (raro: el hybrid no debería
    haberse admitido), usar fallback "process-routing evidence".
  - rationale viene del spec del hybrid (`asset_family_hybrids.json`).
  - El narrador (motor_019) DEBE usar este string verbatim cuando se le
    expone; no puede generar otra justificación libre.

Phase 0 anchor: el LLM no inventa la WHY. El framework la dicta.
"""
from __future__ import annotations

from typing import Any, Mapping, Sequence


_DEFAULT_EVIDENCE_FALLBACK = "process-routing evidence"
_MAX_TOKENS_IN_NARRATIVE = 5


def _normalize_token(t: str) -> str:
    """Turn `cook_chill_present` into `cook chill present` for prose."""
    return str(t or "").strip().replace("_", " ")


def build_hybrid_narrative(
    *,
    hybrid: Mapping[str, Any] | None,
    matched_evidence_tokens: Sequence[str] | None = None,
) -> str:
    """Build the canonical WHY string for an admissible hybrid.

    Args:
      hybrid: dict from `asset_family_hybrids.json` (with primary,
        secondary, rationale, justification_triggers).
      matched_evidence_tokens: the subset of `justification_triggers`
        that actually appeared in the facility's evidence registers.

    Returns:
      The canonical string, or "" if the hybrid is malformed.
    """
    if not isinstance(hybrid, Mapping):
        return ""
    primary = str(hybrid.get("primary", "") or "").strip()
    secondary = str(hybrid.get("secondary", "") or "").strip()
    if not primary or not secondary:
        return ""

    rationale = str(hybrid.get("rationale", "") or "").strip()

    tokens = [
        _normalize_token(t)
        for t in (matched_evidence_tokens or [])
        if t
    ]
    if not tokens:
        evidence_chain = _DEFAULT_EVIDENCE_FALLBACK
    else:
        evidence_chain = ", ".join(tokens[:_MAX_TOKENS_IN_NARRATIVE])

    parts = [
        f"This facility activates {secondary} logic because "
        f"{evidence_chain} suggests cross-system operation beyond "
        f"{primary}-only deployment."
    ]
    if rationale:
        parts.append(rationale)
    return " ".join(parts)


def match_evidence_against_hybrid(
    hybrid: Mapping[str, Any],
    evidence_tokens: Sequence[str] | set[str],
) -> list[str]:
    """Return the subset of hybrid.justification_triggers that appear in
    the provided evidence_tokens (case-insensitive, trimmed)."""
    if not isinstance(hybrid, Mapping):
        return []
    triggers = [
        str(t).strip().lower()
        for t in (hybrid.get("justification_triggers") or [])
        if t
    ]
    evidence_lower = {str(t).strip().lower() for t in (evidence_tokens or []) if t}
    matched: list[str] = []
    for trig in triggers:
        if trig and trig in evidence_lower:
            matched.append(trig)
    return matched
