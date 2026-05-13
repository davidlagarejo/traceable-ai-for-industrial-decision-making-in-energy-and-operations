"""V6 P6 — combination governance strict schema tests."""
from __future__ import annotations

import pytest

from runtime_orchestrator.industrial_research_engine import (
    KnowledgeValidationError,
    validate_combination,
    validate_combination_v6_strict,
)


def _good_v6_combination() -> dict:
    return {
        "id": "test_v6_combo",
        "version": "1.0.0",
        "knowledge_kind": "combination",
        "asset_families": ["cold_chain_facility"],
        "anti_families": [],
        "trigger_conditions": ["refrigerated zone present"],
        "anti_triggers": [],
        "falsification_conditions": ["duty already characterized"],
        "evidence_required": ["compressor inventory"],
        "financial_translation": "Mis-characterized duty mis-prioritizes CAPEX.",
        "tad_actions": ["MEASURE_DUTY", "INSPECT_INVENTORY"],
        "allowed_language": "Combination drives refrigeration prioritization.",
        "prohibited_language": ["bankable savings"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "iiar_bulletin_109", "confidence": "high"}],
        # ── combination-specific (validate_combination requires)
        "required_patterns": ["refrigeration_duty", "compressor_staging"],
        "combined_hypothesis": "Refrigeration duty + compressor staging together drive cold-chain logic.",
        "evidence_pack": {"id": "cold_chain_pack", "items": ["compressor inv", "setpoint log"]},
        "prohibited_claims": [],
        "preconditions": [],
        "layers_combined": ["physical_process", "asset_archetype"],
        # ── V6 P6 strict schema (NEW)
        "required_asset_family": "cold_chain_facility",
        "allowed_claim_ceiling": "L2",
        "required_evidence_pack": "cold_chain_refrigeration_pack",
        "tad_mapping": ["measure", "inspect"],
        "allowed_render_modes": ["exploratory_prior", "publish_bounded", "client_safe"],
        "forbidden_render_modes": ["internal_debug_only"],
    }


# ── Happy path ─────────────────────────────────────────────────────


def test_v6_strict_accepts_well_formed_combination():
    combo = validate_combination_v6_strict(_good_v6_combination())
    assert combo.id == "test_v6_combo"
    assert combo.knowledge_kind == "combination"


# ── Required V6 fields ─────────────────────────────────────────────


def test_v6_strict_rejects_missing_required_asset_family():
    p = _good_v6_combination()
    del p["required_asset_family"]
    with pytest.raises(KnowledgeValidationError, match=r"required_asset_family"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_invalid_allowed_claim_ceiling():
    p = _good_v6_combination()
    p["allowed_claim_ceiling"] = "L5"
    with pytest.raises(KnowledgeValidationError, match=r"allowed_claim_ceiling"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_missing_evidence_pack():
    p = _good_v6_combination()
    del p["required_evidence_pack"]
    with pytest.raises(KnowledgeValidationError, match=r"required_evidence_pack"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_missing_financial_translation():
    p = _good_v6_combination()
    p["financial_translation"] = ""
    with pytest.raises(KnowledgeValidationError, match=r"financial_translation"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_missing_tad_mapping():
    p = _good_v6_combination()
    p["tad_mapping"] = []
    with pytest.raises(KnowledgeValidationError, match=r"tad_mapping"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_non_canonical_action_family():
    p = _good_v6_combination()
    p["tad_mapping"] = ["measure", "bogus_action"]
    with pytest.raises(KnowledgeValidationError, match=r"non-canonical action families"):
        validate_combination_v6_strict(p)


def test_v6_strict_accepts_all_8_canonical_action_families():
    p = _good_v6_combination()
    p["tad_mapping"] = [
        "inspect", "measure", "classify", "pilot",
        "design", "procure", "implement", "defer",
    ]
    combo = validate_combination_v6_strict(p)
    assert combo.id == "test_v6_combo"


# ── render modes ───────────────────────────────────────────────────


def test_v6_strict_rejects_missing_allowed_render_modes():
    p = _good_v6_combination()
    p["allowed_render_modes"] = []
    with pytest.raises(KnowledgeValidationError, match=r"allowed_render_modes"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_invalid_render_mode():
    p = _good_v6_combination()
    p["allowed_render_modes"] = ["bogus_mode"]
    with pytest.raises(KnowledgeValidationError, match=r"invalid modes"):
        validate_combination_v6_strict(p)


def test_v6_strict_rejects_render_mode_in_both_lists():
    p = _good_v6_combination()
    p["allowed_render_modes"] = ["client_safe"]
    p["forbidden_render_modes"] = ["client_safe"]  # contradiction
    with pytest.raises(KnowledgeValidationError, match=r"BOTH allowed and forbidden"):
        validate_combination_v6_strict(p)


# ── required_patterns minimum ──────────────────────────────────────


def test_v6_strict_rejects_single_required_pattern():
    p = _good_v6_combination()
    p["required_patterns"] = ["only_one_pattern"]
    with pytest.raises(KnowledgeValidationError, match=r"≥2 patterns"):
        validate_combination_v6_strict(p)


# ── Backward compat: standard validate_combination unchanged ───────


def test_standard_validate_combination_accepts_pre_v6_payload():
    """The non-strict validate_combination must still accept pre-V6 combos
    that lack the V6 fields. Backward compat for the 4 existing combos."""
    p = _good_v6_combination()
    # Remove V6 fields — standard validator should still pass
    for f in (
        "required_asset_family", "allowed_claim_ceiling",
        "required_evidence_pack", "tad_mapping",
        "allowed_render_modes", "forbidden_render_modes",
    ):
        p.pop(f, None)
    combo = validate_combination(p)
    assert combo.id == "test_v6_combo"


# ── Inherits base validation errors ────────────────────────────────


def test_v6_strict_inherits_base_falsification_check():
    p = _good_v6_combination()
    p["falsification_conditions"] = []
    with pytest.raises(KnowledgeValidationError, match=r"falsification"):
        validate_combination_v6_strict(p)


def test_v6_strict_inherits_combined_hypothesis_check():
    p = _good_v6_combination()
    p["combined_hypothesis"] = ""
    with pytest.raises(KnowledgeValidationError, match=r"combined_hypothesis"):
        validate_combination_v6_strict(p)
