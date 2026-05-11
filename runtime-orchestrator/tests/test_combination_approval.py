"""Tests for the combination approval workflow (V2-LIVE Item 7).

The flow:
  AI proposes  → combinations_pending/   (NOT loaded by skill)
  User approves → combinations/          (loaded by skill)
  User rejects → combinations_rejected/  (audit only)

Tests cover the full lifecycle + edge cases. Uses a temporary registry
root via monkeypatching to avoid touching the real registry directories.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime_orchestrator import combination_approval as ca


@pytest.fixture
def temp_registry(tmp_path, monkeypatch):
    """Redirect the module-level registry paths to a temp directory."""
    approved = tmp_path / "combinations"
    pending = tmp_path / "combinations_pending"
    rejected = tmp_path / "combinations_rejected"
    audit = tmp_path / "combination_approval_log.jsonl"
    for d in (approved, pending, rejected):
        d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ca, "_APPROVED_DIR", approved)
    monkeypatch.setattr(ca, "_PENDING_DIR", pending)
    monkeypatch.setattr(ca, "_REJECTED_DIR", rejected)
    monkeypatch.setattr(ca, "_AUDIT_LOG", audit)
    return tmp_path


def _proposal(combo_id="test_combo", **extra):
    base = {
        "id": combo_id,
        "version": "1.0.0",
        "name": "Test Combination",
        "pattern_ids": ["pattern_a", "pattern_b"],
        "trigger_logic": ["asset family active", "evidence missing"],
        "combined_hypothesis": "Test hypothesis text",
        "strategic_risk": "Test risk text",
        "minimum_evidence": ["evidence_1", "evidence_2"],
        "tad_action": "VALIDATE_LOSS_PATTERN",
    }
    base.update(extra)
    return base


# ── Safety: combination_id validation ────────────────────────────────────


def test_rejects_combination_id_with_path_traversal(temp_registry):
    with pytest.raises(ValueError, match="invalid"):
        ca.propose({"id": "../evil"})


def test_rejects_combination_id_with_slashes(temp_registry):
    with pytest.raises(ValueError, match="invalid"):
        ca.propose({"id": "foo/bar"})


def test_rejects_empty_combination_id(temp_registry):
    with pytest.raises(ValueError, match="required"):
        ca.propose({"id": ""})


def test_rejects_combination_id_with_special_chars(temp_registry):
    with pytest.raises(ValueError, match="alnum"):
        ca.propose({"id": "foo-bar"})


# ── propose ─────────────────────────────────────────────────────────────


def test_propose_writes_to_pending_dir(temp_registry):
    out = ca.propose(_proposal("warehouse_combo_v2"), proposed_by="ai")
    assert out["combination_id"] == "warehouse_combo_v2"
    assert (temp_registry / "combinations_pending" / "warehouse_combo_v2.v1.json").exists()


def test_propose_stamps_proposed_at_and_by(temp_registry):
    out = ca.propose(_proposal(), proposed_by="claude")
    assert out["proposed_by"] == "claude"
    assert out["proposed_at"]


def test_propose_refuses_duplicate_in_any_state(temp_registry):
    ca.propose(_proposal("dup_combo"))
    with pytest.raises(FileExistsError):
        ca.propose(_proposal("dup_combo"))


# ── list_pending / list_approved / list_rejected / summary ──────────────


def test_list_pending_returns_summaries(temp_registry):
    ca.propose(_proposal("a_combo"))
    ca.propose(_proposal("b_combo"))
    pending = ca.list_pending()
    assert len(pending) == 2
    ids = {row["combination_id"] for row in pending}
    assert ids == {"a_combo", "b_combo"}


def test_summary_counts_each_state(temp_registry):
    ca.propose(_proposal("c1"))
    ca.propose(_proposal("c2"))
    ca.propose(_proposal("c3"))
    ca.approve("c1", reviewer="david")
    ca.reject("c2", reviewer="david", reason="duplicates an existing pattern")
    s = ca.summary()
    assert s == {"pending_count": 1, "approved_count": 1, "rejected_count": 1}


# ── approve ─────────────────────────────────────────────────────────────


def test_approve_moves_pending_to_approved(temp_registry):
    ca.propose(_proposal("good_combo"))
    out = ca.approve("good_combo", reviewer="david")
    assert out["approved_by"] == "david"
    assert (temp_registry / "combinations" / "good_combo.v1.json").exists()
    assert not (temp_registry / "combinations_pending" / "good_combo.v1.json").exists()


def test_approve_requires_pending_entry(temp_registry):
    with pytest.raises(FileNotFoundError):
        ca.approve("ghost_combo", reviewer="david")


def test_approve_refuses_if_already_approved(temp_registry):
    ca.propose(_proposal("once"))
    ca.approve("once", reviewer="david")
    # Re-propose with same id is blocked by propose() itself
    with pytest.raises(FileExistsError):
        ca.propose(_proposal("once"))


# ── reject ──────────────────────────────────────────────────────────────


def test_reject_moves_to_rejected_with_reason(temp_registry):
    ca.propose(_proposal("bad_combo"))
    out = ca.reject("bad_combo", reviewer="david", reason="duplicates existing combination")
    assert out["rejected_by"] == "david"
    assert "duplicates" in out["rejection_reason"]
    assert (temp_registry / "combinations_rejected" / "bad_combo.v1.json").exists()
    assert not (temp_registry / "combinations_pending" / "bad_combo.v1.json").exists()


def test_reject_requires_non_empty_reason(temp_registry):
    ca.propose(_proposal("x"))
    with pytest.raises(ValueError, match="reason"):
        ca.reject("x", reviewer="david", reason="")


def test_reject_truncates_very_long_reason(temp_registry):
    ca.propose(_proposal("x"))
    long_reason = "x" * 5000
    out = ca.reject("x", reviewer="david", reason=long_reason)
    assert len(out["rejection_reason"]) <= 1000


# ── reset_to_pending ────────────────────────────────────────────────────


def test_reset_moves_rejected_back_to_pending(temp_registry):
    ca.propose(_proposal("revive_combo"))
    ca.reject("revive_combo", reviewer="david", reason="not now")
    ca.reset_to_pending("revive_combo", reviewer="david")
    assert (temp_registry / "combinations_pending" / "revive_combo.v1.json").exists()
    pending = ca.list_pending()
    assert any(row["combination_id"] == "revive_combo" for row in pending)


def test_reset_clears_rejection_metadata(temp_registry):
    ca.propose(_proposal("r"))
    ca.reject("r", reviewer="david", reason="duplicate")
    ca.reset_to_pending("r", reviewer="david")
    full = ca.get_full("r", state="pending")
    assert "__rejection_reason__" not in full
    assert "__rejected_by__" not in full


# ── audit log ───────────────────────────────────────────────────────────


def test_audit_log_appends_one_line_per_event(temp_registry):
    ca.propose(_proposal("audit_combo"))
    ca.approve("audit_combo", reviewer="david")
    log_path = temp_registry / "combination_approval_log.jsonl"
    assert log_path.exists()
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    assert len(lines) == 2
    events = [json.loads(line)["event"] for line in lines]
    assert events == ["propose", "approve"]


def test_audit_log_records_reject_with_reason(temp_registry):
    ca.propose(_proposal("a"))
    ca.reject("a", reviewer="david", reason="bad idea")
    log_path = temp_registry / "combination_approval_log.jsonl"
    lines = log_path.read_text(encoding="utf-8").strip().splitlines()
    reject_event = json.loads(lines[-1])
    assert reject_event["event"] == "reject"
    assert "bad idea" in reject_event["reason"]


# ── get_full ────────────────────────────────────────────────────────────


def test_get_full_returns_complete_payload(temp_registry):
    ca.propose(_proposal("full_combo", pattern_ids=["x", "y", "z"]))
    full = ca.get_full("full_combo", state="pending")
    assert full["id"] == "full_combo"
    assert full["pattern_ids"] == ["x", "y", "z"]
    assert full["__filename__"] == "full_combo.v1.json"


def test_get_full_raises_on_unknown_state(temp_registry):
    with pytest.raises(ValueError, match="unknown state"):
        ca.get_full("x", state="nonsense")


def test_get_full_raises_when_not_present(temp_registry):
    with pytest.raises(FileNotFoundError):
        ca.get_full("ghost", state="pending")
