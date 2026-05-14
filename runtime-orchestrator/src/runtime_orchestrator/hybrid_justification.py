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


def build_hybrid_governance_object(
    *,
    hybrid: Mapping[str, Any] | None,
    matched_evidence_tokens: Sequence[str] | None = None,
) -> dict[str, Any]:
    """V8 P3 — Build the full structured Hybrid Governance Object the
    Chief QA Architect prompt § 3 + § C requires.

    Required fields (10):
      1. primary_asset_family
      2. secondary_asset_family
      3. trigger_evidence       (matched triggers from the spec)
      4. why_secondary_logic_is_allowed  (= narrative WHY string)
      5. scope_allowed                   (= spec.scope_allowed)
      6. scope_prohibited                (= spec.scope_prohibited)
      7. evidence_to_confirm             (= spec.evidence_to_confirm)
      8. evidence_to_falsify             (= spec.evidence_to_falsify)
      9. report_sections_allowed         (= spec.report_sections_allowed)
     10. report_sections_blocked         (= spec.report_sections_blocked)
       + tad_impact                      (= spec.tad_impact)

    Returns an empty dict {} when hybrid is malformed or None.
    """
    if not isinstance(hybrid, Mapping):
        return {}
    primary = str(hybrid.get("primary", "") or "").strip()
    secondary = str(hybrid.get("secondary", "") or "").strip()
    if not primary or not secondary:
        return {}
    narrative = build_hybrid_narrative(
        hybrid=hybrid, matched_evidence_tokens=matched_evidence_tokens
    )
    return {
        "primary_asset_family":      primary,
        "secondary_asset_family":    secondary,
        "trigger_evidence":          list(matched_evidence_tokens or []),
        "why_secondary_logic_is_allowed": narrative,
        "scope_allowed":             list(hybrid.get("scope_allowed", []) or []),
        "scope_prohibited":          list(hybrid.get("scope_prohibited", []) or []),
        "evidence_to_confirm":       list(hybrid.get("evidence_to_confirm", []) or []),
        "evidence_to_falsify":       list(hybrid.get("evidence_to_falsify", []) or []),
        "report_sections_allowed":   list(hybrid.get("report_sections_allowed", []) or []),
        "report_sections_blocked":   list(hybrid.get("report_sections_blocked", []) or []),
        "tad_impact":                list(hybrid.get("tad_impact", []) or []),
    }


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
