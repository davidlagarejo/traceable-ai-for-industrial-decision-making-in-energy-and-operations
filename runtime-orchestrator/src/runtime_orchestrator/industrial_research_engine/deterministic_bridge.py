"""V5 P3 — bridge from zlab_skill deterministic extraction → propose_knowledge.

`zlab_skill.local_pdf_autodraft` reads a PDF deterministically and emits
`pattern_candidate_records` + `combination_candidate_records` by matching
keyword rules against `registry["patterns"]`. Those candidates live in
the zlab_skill `extraction_review_register` surface.

V5 P3 also wants those candidates to land in the IRE `knowledge_pending/`
surface so the dashboard `/revisar` page shows them in one place.

This module is the bridge. It converts a registry pattern spec
(supplemented by the extractor's match evidence) into a canonical
KnowledgeObject payload and routes it through `propose_knowledge`.

Phase 0 anchor: no LLM is used. The bridge is a deterministic
field-mapping function from the existing registry pattern spec
(authored once, frozen as scaffolding in AI_SCAFFOLDING_REGISTRY S4)
plus the PDF-derived provenance (source_id + supporting excerpt +
source_locator) coming from the deterministic extractor.

A bridged proposal records its origin in `extraction_metadata`:
  - extraction_path = "deterministic_pdf_autodraft"
  - matched_terms = the keyword hits that confirmed presence
  - supporting_excerpt = a span of the PDF that triggered the match
  - source_locator = the PDF location identifier

Approval still happens in the dashboard, never automatically.
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any, Mapping

from ..source_catalog import source_by_id
from .engine import propose_knowledge
from .schemas import KNOWLEDGE_KINDS
from .validators import KnowledgeValidationError


def _text(value: Any) -> str:
    return str(value or "").strip()


# V5 P3 compatibility layer — registry patterns (S4 scaffolding) carry
# legacy asset_type strings that pre-date the 16 canonical asset_families.
# This map normalizes them. Long-term these should be fixed in the
# registry JSONs themselves (an S9 follow-up cleanup).
_LEGACY_ASSET_FAMILY_MAP: dict[str, str | None] = {
    "industrial_facility": "manufacturing_facility",
    "large_commercial_building": "commercial_building",
    "thermal_process_site": "thermal_process_facility",
    "logistics_hub": "logistics_terminal",
    # Non-asset-family attributes — drop entirely (not a family)
    "leased_asset": None,
    "all_operational_assets": None,
}


def _normalize_asset_family(raw: str) -> str | None:
    """Map a possibly-legacy asset_type string to a canonical family.

    Returns None if the raw value is a non-asset-family attribute that
    should be dropped (e.g. 'leased_asset' which is a tenure attribute,
    not a family).
    """
    s = _text(raw)
    if not s:
        return None
    if s in _LEGACY_ASSET_FAMILY_MAP:
        return _LEGACY_ASSET_FAMILY_MAP[s]  # may be None on purpose
    return s  # pass-through if already canonical (or unknown — validator catches)


def _asset_families_from_pattern_spec(
    pattern_spec: Mapping[str, Any],
) -> list[str]:
    """Use `asset_types` from the registry pattern as `asset_families`.

    The registry uses `asset_types` (matches the framework's family
    taxonomy). KnowledgeObject uses `asset_families` (same vocabulary).
    Legacy values are normalized via _LEGACY_ASSET_FAMILY_MAP; values
    that map to None are dropped (non-asset-family attributes).
    """
    out: list[str] = []
    for raw in pattern_spec.get("asset_types", []) or []:
        normalized = _normalize_asset_family(raw)
        if normalized and normalized not in out:
            out.append(normalized)
    return out


def _pattern_id_to_kind(pattern_spec: Mapping[str, Any]) -> str:
    """Map a registry pattern to one of the canonical knowledge kinds.

    `knowledge_type` in the registry can be e.g.
    ['LOSS_PATTERN', 'ASSET_ARCHETYPE']. We map the first one to a
    canonical KNOWLEDGE_KINDS value.
    """
    types = [_text(t).upper() for t in pattern_spec.get("knowledge_type", []) or []]
    if "PROCESS_LOGIC" in types:
        return "process_logic"
    if "ASSET_ARCHETYPE" in types:
        return "archetype"
    # Default to "pattern" (covers LOSS_PATTERN, OPERATIONAL_PATTERN, etc.)
    return "pattern"


def pattern_spec_to_knowledge_object(
    *,
    pattern_spec: Mapping[str, Any],
    source_id: str,
    supporting_excerpt: str = "",
    source_locator: str = "",
    matched_terms: list[str] | None = None,
    pdf_path: str = "",
    override_id: str = "",
) -> dict[str, Any]:
    """Convert a registry pattern spec + extractor provenance into a
    canonical KnowledgeObject payload (dict-form, ready for
    propose_knowledge).

    The KnowledgeObject's epistemic surface (trigger_conditions,
    falsification_conditions, evidence_required, anti_triggers,
    financial_translation, allowed_language, prohibited_language) is
    taken directly from the registry pattern spec. The deterministic
    extractor's contribution is purely PROVENANCE — it confirms the
    pattern's presence in an authoritative source PDF.

    Args:
      pattern_spec: registry pattern JSON dict
      source_id: catalog source_id that owns this PDF
      supporting_excerpt: PDF text span that triggered the match
      source_locator: identifier string for the source location
      matched_terms: keyword hits that activated the rule
      pdf_path: absolute path of the PDF on disk
      override_id: optional alternate id (default: pattern_spec["id"])

    Returns:
      a dict ready to pass to propose_knowledge()
    """
    base_id = _text(override_id or pattern_spec.get("id"))
    if not base_id:
        raise ValueError("pattern_spec must have an 'id'")

    kind = _pattern_id_to_kind(pattern_spec)

    # Asset families with fallback chain:
    # 1. Normalize pattern_spec.asset_types (drops legacy universals)
    # 2. If empty (e.g. 'all_operational_assets' dropped), fall back to
    #    the source's asset_families from the catalog
    asset_families = _asset_families_from_pattern_spec(pattern_spec)
    if not asset_families and source_id:
        catalog_entry = source_by_id(source_id) or {}
        asset_families = [
            f for f in (catalog_entry.get("asset_families") or [])
            if _text(f)
        ]

    return {
        "id": base_id,
        "version": _text(pattern_spec.get("version") or "1.0.0"),
        "knowledge_kind": kind,
        "asset_families": asset_families,
        "anti_families": list(pattern_spec.get("anti_families", []) or []),
        "trigger_conditions": list(
            pattern_spec.get("trigger_conditions", []) or []
        ) or list(pattern_spec.get("applicable_contexts", []) or []),
        "anti_triggers": list(pattern_spec.get("anti_triggers", []) or []),
        "falsification_conditions": list(
            pattern_spec.get("falsification_conditions", []) or []
        ),
        "evidence_required": (
            list(pattern_spec.get("evidence_required", []) or [])
            or list(pattern_spec.get("minimum_evidence_to_activate", []) or [])
        ),
        "financial_translation": _text(pattern_spec.get("financial_mechanism")),
        "tad_actions": list(pattern_spec.get("tad_actions", []) or []),
        "allowed_language": _text(pattern_spec.get("allowed_claim_language"))
                            or _text(pattern_spec.get("hypothesis")),
        "prohibited_language": (
            [_text(pattern_spec.get("prohibited_claim_language"))]
            if _text(pattern_spec.get("prohibited_claim_language"))
            else list(pattern_spec.get("prohibited_language", []) or [])
        ),
        "claim_ceiling": _text(pattern_spec.get("confidence_ceiling")) or "L2",
        "source_basis": [
            {
                "source_id": source_id,
                "confidence": "high",
                "supporting_excerpt": supporting_excerpt[:500],
                "source_locator": source_locator,
            }
        ],
        "extraction_metadata": {
            "extraction_path": "deterministic_pdf_autodraft",
            "extracted_from_pdf": pdf_path or source_locator,
            "matched_terms": list(matched_terms or []),
            "source_id": source_id,
            "supporting_excerpt": supporting_excerpt[:500],
            "extractor_module": "zlab_skill.local_pdf_autodraft",
            "extractor_version": "v1",
        },
        "notes": (
            "Bridged from deterministic PDF autodraft. Confirmed by "
            f"keyword matches against {len(matched_terms or [])} required "
            "groups + optional terms. Spec body comes from the framework's "
            "frozen registry pattern (see AI_SCAFFOLDING_REGISTRY S4). The "
            "PDF excerpt provides the authoritative-source provenance link."
        ),
    }


def propose_extracted_pattern(
    *,
    pattern_spec: Mapping[str, Any],
    source_id: str,
    supporting_excerpt: str = "",
    source_locator: str = "",
    matched_terms: list[str] | None = None,
    pdf_path: str = "",
    proposed_by: str = "deterministic_pdf_autodraft",
    override_id: str = "",
) -> dict[str, Any]:
    """End-to-end: pattern_spec + provenance → propose_knowledge.

    Returns the stamped, validated payload. Raises:
      - KnowledgeValidationError on schema failure
      - ValueError on missing id
      - FileExistsError on duplicate id in any pending state
    """
    payload = pattern_spec_to_knowledge_object(
        pattern_spec=pattern_spec,
        source_id=source_id,
        supporting_excerpt=supporting_excerpt,
        source_locator=source_locator,
        matched_terms=matched_terms,
        pdf_path=pdf_path,
        override_id=override_id,
    )
    return propose_knowledge(
        payload,
        kind=payload["knowledge_kind"],
        proposed_by=proposed_by,
    )


def load_pattern_spec(pattern_id: str) -> dict[str, Any] | None:
    """Look up a registry pattern by id. Returns None if not found."""
    repo_root = Path(__file__).resolve().parents[4]
    candidates = list(
        (repo_root / "runtime-orchestrator" / "zlab_skill" / "registry" / "patterns")
        .glob(f"{pattern_id}.*.json")
    )
    if not candidates:
        return None
    try:
        return json.loads(candidates[0].read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError):
        return None
