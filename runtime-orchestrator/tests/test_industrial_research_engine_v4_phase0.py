"""V4 Phase 0 infrastructure tests.

Covers schemas, validators, family_scope, source_confidence, taxonomy,
routing, memory, and engine. Real extraction stays a stub (raises
NotImplementedError) — this test confirms it.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime_orchestrator.industrial_research_engine import (
    CLAIM_CEILINGS,
    KNOWLEDGE_KINDS,
    INDUSTRIAL_TAXONOMY,
    KnowledgeObject,
    KnowledgeValidationError,
    MemoryState,
    NotImplementedExtractor,
    enforce_family_scope,
    extract_knowledge,
    families_conflict,
    family_for_topic,
    list_in_state,
    propose_knowledge,
    research_priority_for,
    source_confidence_for,
    topics_for_family,
    validate_combination,
    validate_knowledge,
)
from runtime_orchestrator.industrial_research_engine.source_confidence import (
    aggregate_confidence,
)


def _good_payload(combo=False) -> dict:
    base = {
        "id": "test_knowledge_x" if not combo else "test_combo_y",
        "version": "1.0.0",
        "knowledge_kind": "pattern" if not combo else "combination",
        "asset_families": ["manufacturing_facility"],
        "anti_families": ["datacenter"],
        "trigger_conditions": ["process heat plausible"],
        "anti_triggers": ["thermal duty already bounded"],
        "falsification_conditions": ["thermal share below 20% of total kWh"],
        "evidence_required": ["thermal map", "fuel profile"],
        "financial_translation": "Process duty drives capital allocation logic.",
        "tad_actions": ["VALIDATE_LOSS_PATTERN"],
        "allowed_language": "Process thermal duty is structurally plausible and requires evidence.",
        "prohibited_language": ["guaranteed savings", "ROI claim"],
        "claim_ceiling": "L2",
        "source_basis": [{"source_id": "iiar_bulletin_109", "confidence": "high"}],
    }
    if combo:
        base.update({
            "required_patterns": ["thermal_duty_a", "uptime_b"],
            "combined_hypothesis": "Combined thermal-duty + uptime drives the dominant variable.",
            "evidence_pack": {"cheapest_valid_path": "thermal map"},
            "prohibited_claims": ["uptime is solved"],
            "preconditions": ["thermal_bounded"],
        })
    return base


# ── Schemas ────────────────────────────────────────────────────────────


def test_knowledge_kinds_has_12_entries():
    assert len(KNOWLEDGE_KINDS) == 12


def test_claim_ceilings_capped_at_L2():
    assert CLAIM_CEILINGS == ("L0", "L1", "L2")
    assert "L3" not in CLAIM_CEILINGS


# ── Validator: base knowledge ─────────────────────────────────────────


def test_validate_knowledge_happy_path():
    obj = validate_knowledge(_good_payload())
    assert isinstance(obj, KnowledgeObject)
    assert obj.id == "test_knowledge_x"
    assert obj.knowledge_kind == "pattern"


def test_validate_knowledge_rejects_missing_falsification():
    p = _good_payload()
    p["falsification_conditions"] = []
    with pytest.raises(KnowledgeValidationError, match="falsification_conditions"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_unknown_kind():
    p = _good_payload()
    p["knowledge_kind"] = "snake_oil"
    with pytest.raises(KnowledgeValidationError, match="knowledge_kind"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_claim_ceiling_above_L2():
    p = _good_payload()
    p["claim_ceiling"] = "L3"
    with pytest.raises(KnowledgeValidationError, match="claim_ceiling"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_prohibited_language_in_allowed():
    p = _good_payload()
    p["allowed_language"] = "This will reduce energy use guaranteed savings of 20%."
    with pytest.raises(KnowledgeValidationError, match="prohibited closure language"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_empty_asset_families():
    p = _good_payload()
    p["asset_families"] = []
    with pytest.raises(KnowledgeValidationError, match="asset_family"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_unknown_asset_family():
    p = _good_payload()
    p["asset_families"] = ["unicorn_factory"]
    with pytest.raises(KnowledgeValidationError, match="unknown asset family"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_family_conflict():
    p = _good_payload()
    p["asset_families"] = ["manufacturing_facility"]
    p["anti_families"] = ["manufacturing_facility"]
    with pytest.raises(KnowledgeValidationError, match="disjoint"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_empty_source_basis():
    p = _good_payload()
    p["source_basis"] = []
    with pytest.raises(KnowledgeValidationError, match="source_basis"):
        validate_knowledge(p)


def test_validate_knowledge_rejects_source_basis_without_source_id():
    p = _good_payload()
    p["source_basis"] = [{"confidence": "high"}]
    with pytest.raises(KnowledgeValidationError, match="source_id"):
        validate_knowledge(p)


def test_validate_knowledge_routes_combination_to_combination_validator():
    p = _good_payload(combo=True)
    with pytest.raises(KnowledgeValidationError, match="validate_combination"):
        validate_knowledge(p)


# ── Validator: combination ────────────────────────────────────────────


def test_validate_combination_happy_path():
    obj = validate_combination(_good_payload(combo=True))
    assert obj.knowledge_kind == "combination"
    assert obj.required_patterns == ["thermal_duty_a", "uptime_b"]
    assert obj.evidence_pack["cheapest_valid_path"] == "thermal map"


def test_validate_combination_rejects_empty_required_patterns():
    p = _good_payload(combo=True)
    p["required_patterns"] = []
    with pytest.raises(KnowledgeValidationError, match="required_patterns"):
        validate_combination(p)


def test_validate_combination_rejects_evidence_pack_as_list():
    p = _good_payload(combo=True)
    p["evidence_pack"] = ["not", "a", "dict"]
    with pytest.raises(KnowledgeValidationError, match="evidence_pack"):
        validate_combination(p)


def test_validate_combination_rejects_non_combination_kind():
    p = _good_payload(combo=True)
    p["knowledge_kind"] = "pattern"
    with pytest.raises(KnowledgeValidationError, match="combination"):
        validate_combination(p)


# ── family_scope ──────────────────────────────────────────────────────


def test_families_conflict_finds_intersection():
    assert families_conflict(["a", "b"], ["b", "c"]) == ["b"]


def test_enforce_family_scope_normalizes_and_dedupes():
    af, nf = enforce_family_scope(
        ["manufacturing_facility", "manufacturing_facility"],
        ["datacenter"],
    )
    assert af == ["manufacturing_facility"]
    assert nf == ["datacenter"]


# ── source_confidence ─────────────────────────────────────────────────


def test_source_confidence_for_known_catalog_id():
    info = source_confidence_for("iiar_bulletin_109")
    assert info is not None
    assert info["authority_tier"] == 1
    assert info["confidence_band"] == "high"
    assert info["permits_closure"] is True


def test_source_confidence_for_unknown_returns_none():
    assert source_confidence_for("not_a_real_source") is None


def test_aggregate_confidence_picks_highest_tier():
    # Tier 1 dominates
    assert aggregate_confidence(["iiar_bulletin_109", "danfoss_industrial_refrigeration_handbook"]) == "high"
    # Only tier 3
    assert aggregate_confidence(["danfoss_industrial_refrigeration_handbook"]) == "medium"
    # Unknown
    assert aggregate_confidence(["not_a_source"]) == "unknown"


# ── taxonomy ──────────────────────────────────────────────────────────


def test_industrial_taxonomy_has_11_topics():
    assert len(INDUSTRIAL_TAXONOMY) == 11
    for topic, info in INDUSTRIAL_TAXONOMY.items():
        assert "keywords" in info
        assert "machines" in info
        assert "systems" in info


def test_topics_for_family_default_empty():
    """V4 P0 leaves per-family priorities unset (content-adjacent)."""
    assert topics_for_family("manufacturing_facility") == []


def test_family_for_topic_returns_empty_in_phase_0():
    """Same reason: priorities not registered yet."""
    assert family_for_topic("thermal_process") == []


# ── routing ───────────────────────────────────────────────────────────


def test_routing_returns_full_plan_structure():
    plan = research_priority_for("manufacturing_facility")
    assert "topics_ordered" in plan
    assert "sources_per_topic" in plan
    assert "clue_weights" in plan
    assert len(plan["topics_ordered"]) == 11  # uses INDUSTRIAL_TAXONOMY keys when no family priority


def test_routing_re_ranks_topics_by_clue_match():
    plan = research_priority_for(
        "manufacturing_facility",
        thermal_clues=["process heat", "curing"],
    )
    # thermal_process should bubble up
    assert plan["topics_ordered"][0] == "thermal_process"


def test_routing_sources_per_topic_uses_catalog():
    plan = research_priority_for("cold_chain_facility")
    # At least one topic has a non-empty source list
    assert any(srcs for srcs in plan["sources_per_topic"].values())


def test_not_implemented_extractor_raises():
    with pytest.raises(NotImplementedError, match="not implemented in V4 Phase 0"):
        NotImplementedExtractor().extract("http://x", "thermal_process")


def test_extract_knowledge_stub_raises():
    with pytest.raises(NotImplementedError):
        extract_knowledge("http://x", "thermal_process")


# ── memory state transitions ──────────────────────────────────────────


@pytest.fixture
def tmp_memory(tmp_path, monkeypatch):
    """Redirect engine + memory paths to a tmp tree for isolated tests."""
    from runtime_orchestrator.industrial_research_engine import engine, memory
    pending = tmp_path / "knowledge_pending"
    mem = tmp_path / "knowledge_memory"
    for kind in KNOWLEDGE_KINDS:
        (pending / kind).mkdir(parents=True, exist_ok=True)
    for st in MemoryState:
        (mem / st.value).mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(engine, "_PENDING_ROOT", pending)
    monkeypatch.setattr(engine, "_AUDIT_LOG", pending / "knowledge_proposal_log.jsonl")
    monkeypatch.setattr(memory, "_PENDING_ROOT", pending)
    monkeypatch.setattr(memory, "_MEMORY_ROOT", mem)
    monkeypatch.setattr(memory, "_AUDIT_LOG", mem / "knowledge_memory_log.jsonl")
    return tmp_path, pending, mem


def test_propose_knowledge_writes_to_pending(tmp_memory):
    tmp_path, pending, mem = tmp_memory
    out = propose_knowledge(_good_payload(), proposed_by="claude_test")
    file_path = pending / "pattern" / "test_knowledge_x.v1.json"
    assert file_path.exists()
    assert out["__proposed_by__"] == "claude_test"


def test_propose_knowledge_refuses_duplicate_across_kinds(tmp_memory):
    propose_knowledge(_good_payload())
    with pytest.raises(FileExistsError, match="already pending"):
        propose_knowledge(_good_payload())


def test_promote_to_memory_moves_pending_to_approved(tmp_memory):
    from runtime_orchestrator.industrial_research_engine.memory import promote_to_memory
    tmp_path, pending, mem = tmp_memory
    propose_knowledge(_good_payload())
    promote_to_memory("test_knowledge_x", kind="pattern", reviewer="david")
    assert not (pending / "pattern" / "test_knowledge_x.v1.json").exists()
    assert (mem / "approved" / "test_knowledge_x.v1.json").exists()


def test_reject_moves_pending_to_rejected_with_reason(tmp_memory):
    from runtime_orchestrator.industrial_research_engine.memory import reject
    tmp_path, pending, mem = tmp_memory
    propose_knowledge(_good_payload())
    reject("test_knowledge_x", kind="pattern", reviewer="david", reason="duplicates existing pattern")
    rejected_path = mem / "rejected" / "test_knowledge_x.v1.json"
    assert rejected_path.exists()
    payload = json.loads(rejected_path.read_text())
    assert "duplicates" in payload["__rejection_reason__"]


def test_deprecate_moves_approved_to_deprecated(tmp_memory):
    from runtime_orchestrator.industrial_research_engine.memory import (
        deprecate, promote_to_memory,
    )
    tmp_path, pending, mem = tmp_memory
    propose_knowledge(_good_payload())
    promote_to_memory("test_knowledge_x", kind="pattern", reviewer="david")
    deprecate("test_knowledge_x", reviewer="david", reason="obsolete")
    assert (mem / "deprecated" / "test_knowledge_x.v1.json").exists()
    assert not (mem / "approved" / "test_knowledge_x.v1.json").exists()


def test_supersede_moves_old_to_superseded(tmp_memory):
    from runtime_orchestrator.industrial_research_engine.memory import (
        promote_to_memory, supersede,
    )
    tmp_path, pending, mem = tmp_memory
    propose_knowledge(_good_payload())
    promote_to_memory("test_knowledge_x", kind="pattern", reviewer="d")
    # second version
    p2 = _good_payload()
    p2["id"] = "test_knowledge_x_v2"
    propose_knowledge(p2)
    promote_to_memory("test_knowledge_x_v2", kind="pattern", reviewer="d")
    supersede("test_knowledge_x", "test_knowledge_x_v2", reviewer="d")
    assert (mem / "superseded" / "test_knowledge_x.v1.json").exists()
    assert (mem / "approved" / "test_knowledge_x_v2.v1.json").exists()


def test_list_in_state_returns_summaries(tmp_memory):
    from runtime_orchestrator.industrial_research_engine.memory import promote_to_memory
    propose_knowledge(_good_payload())
    promote_to_memory("test_knowledge_x", kind="pattern", reviewer="david")
    rows = list_in_state(MemoryState.APPROVED)
    assert len(rows) == 1
    assert rows[0]["id"] == "test_knowledge_x"
    assert rows[0]["approved_by"] == "david"


# ── Safety: invalid knowledge_id rejected ─────────────────────────────


def test_propose_knowledge_rejects_path_traversal_in_id(tmp_memory):
    p = _good_payload()
    p["id"] = "../evil"
    with pytest.raises((KnowledgeValidationError, ValueError)):
        propose_knowledge(p)
