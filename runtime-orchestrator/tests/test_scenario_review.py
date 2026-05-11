"""Tests for the scenario review workflow (V2-CRITICAL course correction).

The PDF is the clean reader deliverable. Review and approval of scenarios
(with their 5 justification fields) happens in the dashboard BEFORE the
PDF renders. This test suite covers the per-case scenario lifecycle.
"""
from __future__ import annotations

import json

import pytest

from runtime_orchestrator import scenario_review as sr


@pytest.fixture
def temp_reviews(tmp_path, monkeypatch):
    """Redirect the scenario_review storage to a tmp directory."""
    reviews = tmp_path / "scenario_reviews"
    reviews.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(sr, "_REVIEWS_DIR", reviews)
    monkeypatch.setattr(sr, "_AUDIT_LOG", reviews / "log.jsonl")
    return tmp_path, reviews


def _scenario(letter="A", **extra):
    base = {
        "scenario": f"{letter}. Energy intensity drives the load",
        "plausibility_status": "Plausible but unsupported",
        "trigger": "Operating schedule unresolved",
        "source": "doe_iac_database",
        "process_clue": "Throughput drives kWh",
        "industrial_reason": "DOE IAC datasets confirm",
        "asset_family_reason": "Logistics nodes are throughput-driven",
    }
    base.update(extra)
    return base


# ── case_id safety ──────────────────────────────────────────────────────


def test_safe_case_id_rejects_traversal(temp_reviews):
    with pytest.raises(ValueError, match="invalid"):
        sr.upsert_scenarios("../evil", [_scenario()])


def test_safe_case_id_accepts_normal_ids(temp_reviews):
    sr.upsert_scenarios("ZLab-asset-cold-chain-lakeshore-2026", [_scenario()])
    cases = sr.list_cases()
    assert any(c["case_id"] == "ZLab-asset-cold-chain-lakeshore-2026" for c in cases)


# ── upsert_scenarios ────────────────────────────────────────────────────


def test_upsert_seeds_all_scenarios_as_pending(temp_reviews):
    sr.upsert_scenarios("case_x", [_scenario("A"), _scenario("B"), _scenario("C"), _scenario("D")])
    case = sr.get_case("case_x")
    assert len(case["scenarios"]) == 4
    for sc in case["scenarios"].values():
        assert sc["state"] == "pending"


def test_upsert_preserves_existing_state_on_refresh(temp_reviews):
    sr.upsert_scenarios("case_y", [_scenario("A"), _scenario("B")])
    sr.approve("case_y", "A", reviewer="david")
    # Re-seed (e.g., second pipeline run) — A stays approved
    sr.upsert_scenarios("case_y", [_scenario("A", trigger="updated trigger"), _scenario("B")])
    case = sr.get_case("case_y")
    assert case["scenarios"]["A"]["state"] == "approved"
    # Justification fields ARE refreshed even when state is preserved
    assert case["scenarios"]["A"]["trigger"] == "updated trigger"


def test_upsert_threads_asset_family(temp_reviews):
    sr.upsert_scenarios("case_z", [_scenario()], asset_family="cold_chain_facility")
    case = sr.get_case("case_z")
    assert case["asset_family"] == "cold_chain_facility"


# ── approve / reject / edit ─────────────────────────────────────────────


def test_approve_marks_scenario_approved(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    out = sr.approve("c", "A", reviewer="david")
    assert out["scenarios"]["A"]["state"] == "approved"
    assert out["scenarios"]["A"]["reviewer"] == "david"


def test_approve_requires_reviewer(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    with pytest.raises(ValueError, match="reviewer"):
        sr.approve("c", "A", reviewer="")


def test_approve_raises_when_scenario_missing(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    with pytest.raises(FileNotFoundError):
        sr.approve("c", "Z", reviewer="d")


def test_reject_records_reason(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    out = sr.reject("c", "A", reviewer="d", reason="dominant variable already framed differently")
    assert out["scenarios"]["A"]["state"] == "rejected"
    assert "dominant variable" in out["scenarios"]["A"]["rejection_reason"]


def test_reject_requires_reason(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    with pytest.raises(ValueError, match="reason"):
        sr.reject("c", "A", reviewer="d", reason="")


def test_edit_updates_justification_fields(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    out = sr.edit("c", "A", reviewer="d", patch={
        "trigger": "Refined trigger",
        "source": "ashrae_handbook_refrigeration",
    })
    assert out["scenarios"]["A"]["state"] == "edited"
    assert out["scenarios"]["A"]["trigger"] == "Refined trigger"
    assert out["scenarios"]["A"]["source"] == "ashrae_handbook_refrigeration"
    assert out["scenarios"]["A"]["edit_count"] == 1


def test_edit_drops_unknown_keys(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    sr.edit("c", "A", reviewer="d", patch={
        "trigger": "ok",
        "evil_field": "drop_me",
    })
    case = sr.get_case("c")
    assert "evil_field" not in case["scenarios"]["A"]


def test_edit_refuses_when_patch_has_no_editable_keys(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    with pytest.raises(ValueError, match="no editable fields"):
        sr.edit("c", "A", reviewer="d", patch={"evil_only": 1})


def test_edit_then_approve_keeps_edits(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A")])
    sr.edit("c", "A", reviewer="d", patch={"trigger": "x"})
    sr.approve("c", "A", reviewer="d")
    case = sr.get_case("c")
    assert case["scenarios"]["A"]["state"] == "approved"
    assert case["scenarios"]["A"]["trigger"] == "x"


# ── ready_to_render gate ─────────────────────────────────────────────────


def test_ready_to_render_false_when_pending(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A"), _scenario("B")])
    assert sr.ready_to_render("c") is False


def test_ready_to_render_true_when_all_approved(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A"), _scenario("B")])
    sr.approve("c", "A", reviewer="d")
    sr.approve("c", "B", reviewer="d")
    assert sr.ready_to_render("c") is True


def test_ready_to_render_true_when_mix_approved_and_rejected(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A"), _scenario("B")])
    sr.approve("c", "A", reviewer="d")
    sr.reject("c", "B", reviewer="d", reason="not applicable")
    assert sr.ready_to_render("c") is True


def test_ready_to_render_false_when_any_edited(temp_reviews):
    """Edited scenarios are still pending — they need approval after edit."""
    sr.upsert_scenarios("c", [_scenario("A"), _scenario("B")])
    sr.approve("c", "A", reviewer="d")
    sr.edit("c", "B", reviewer="d", patch={"trigger": "x"})
    assert sr.ready_to_render("c") is False


def test_ready_to_render_false_for_empty_case(temp_reviews):
    """Empty case must not be marked ready — guards against false positives."""
    assert sr.ready_to_render("nonexistent") is False


# ── approve_all (convenience) ───────────────────────────────────────────


def test_approve_all_marks_every_non_rejected_approved(temp_reviews):
    sr.upsert_scenarios("c", [_scenario("A"), _scenario("B"), _scenario("C")])
    sr.reject("c", "C", reviewer="d", reason="exclude")
    sr.approve_all("c", reviewer="d")
    case = sr.get_case("c")
    assert case["scenarios"]["A"]["state"] == "approved"
    assert case["scenarios"]["B"]["state"] == "approved"
    # rejected stays rejected
    assert case["scenarios"]["C"]["state"] == "rejected"


# ── auto-approve for regression ─────────────────────────────────────────


def test_auto_approve_for_regression_seeds_and_approves(temp_reviews):
    out = sr.auto_approve_for_regression(
        "regression_case",
        [_scenario("A"), _scenario("B")],
        asset_family="cold_chain_facility",
    )
    assert out["ready_to_render"] is True
    assert all(sc["state"] == "approved" for sc in out["scenarios"].values())


# ── list_cases summary ──────────────────────────────────────────────────


def test_list_cases_returns_per_state_counts(temp_reviews):
    sr.upsert_scenarios("c1", [_scenario("A"), _scenario("B"), _scenario("C"), _scenario("D")])
    sr.approve("c1", "A", reviewer="d")
    sr.approve("c1", "B", reviewer="d")
    sr.reject("c1", "C", reviewer="d", reason="x")
    summary = sr.list_cases()
    c1 = next(c for c in summary if c["case_id"] == "c1")
    assert c1["scenario_count"] == 4
    assert c1["approved_count"] == 2
    assert c1["rejected_count"] == 1
    assert c1["pending_count"] == 1
    assert c1["ready_to_render"] is False


# ── audit log ───────────────────────────────────────────────────────────


def test_audit_log_appends_every_transition(temp_reviews):
    tmp_path, reviews = temp_reviews
    sr.upsert_scenarios("c", [_scenario("A")])
    sr.edit("c", "A", reviewer="d", patch={"trigger": "x"})
    sr.approve("c", "A", reviewer="d")
    log = (reviews / "log.jsonl").read_text(encoding="utf-8").splitlines()
    events = [json.loads(line)["event"] for line in log]
    assert events == ["edit", "approve"]
