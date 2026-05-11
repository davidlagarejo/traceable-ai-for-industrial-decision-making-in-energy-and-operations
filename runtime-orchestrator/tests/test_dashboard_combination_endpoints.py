"""End-to-end tests for the dashboard combination approval endpoints
(V2-LIVE Item 7). Boots the Flask app via test client; redirects the
filesystem to a tmp registry so we don't pollute the real one.
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest


@pytest.fixture
def client(tmp_path, monkeypatch):
    from runtime_orchestrator import combination_approval as ca
    approved = tmp_path / "combinations"
    pending = tmp_path / "combinations_pending"
    rejected = tmp_path / "combinations_rejected"
    for d in (approved, pending, rejected):
        d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ca, "_APPROVED_DIR", approved)
    monkeypatch.setattr(ca, "_PENDING_DIR", pending)
    monkeypatch.setattr(ca, "_REJECTED_DIR", rejected)
    monkeypatch.setattr(ca, "_AUDIT_LOG", tmp_path / "combination_approval_log.jsonl")

    # Import dashboard AFTER monkeypatching so its module-level alias _ca
    # points at the same (patched) module.
    import importlib
    import dashboard  # noqa: F401
    importlib.reload(dashboard)
    dashboard.app.config["TESTING"] = True
    return dashboard.app.test_client(), ca


def _proposal(combo_id="ui_test_combo"):
    return {
        "id": combo_id,
        "version": "1.0.0",
        "name": "UI Test Combination",
        "pattern_ids": ["pattern_x", "pattern_y"],
        "trigger_logic": ["a", "b"],
        "combined_hypothesis": "Test hypothesis",
        "strategic_risk": "Test risk",
        "minimum_evidence": ["e1"],
        "tad_action": "VALIDATE_LOSS_PATTERN",
    }


# ── GET endpoints ──────────────────────────────────────────────────────


def test_get_pending_returns_empty_when_no_proposals(client):
    c, _ = client
    r = c.get("/api/combinations/pending")
    assert r.status_code == 200
    assert r.get_json() == []


def test_get_summary_shows_zero_counts(client):
    c, _ = client
    r = c.get("/api/combinations/summary")
    assert r.status_code == 200
    assert r.get_json() == {"pending_count": 0, "approved_count": 0, "rejected_count": 0}


def test_get_pending_returns_proposed_combination(client):
    c, ca = client
    ca.propose(_proposal(), proposed_by="ai")
    r = c.get("/api/combinations/pending")
    rows = r.get_json()
    assert len(rows) == 1
    assert rows[0]["combination_id"] == "ui_test_combo"


def test_get_full_by_state_returns_complete_payload(client):
    c, ca = client
    ca.propose(_proposal("zoom_combo"), proposed_by="ai")
    r = c.get("/api/combinations/pending/zoom_combo")
    assert r.status_code == 200
    full = r.get_json()
    assert full["id"] == "zoom_combo"
    assert full["pattern_ids"] == ["pattern_x", "pattern_y"]


def test_get_full_returns_404_when_missing(client):
    c, _ = client
    r = c.get("/api/combinations/pending/ghost")
    assert r.status_code == 404


def test_get_full_returns_400_on_bad_state(client):
    c, _ = client
    r = c.get("/api/combinations/whatever/x")
    assert r.status_code == 400


# ── Approve ────────────────────────────────────────────────────────────


def test_approve_moves_pending_to_approved(client):
    c, ca = client
    ca.propose(_proposal("good_combo"), proposed_by="ai")
    r = c.post(
        "/api/combinations/approve",
        json={"combination_id": "good_combo", "reviewer": "david"},
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "approved"
    assert body["combination"]["combination_id"] == "good_combo"
    assert body["combination"]["approved_by"] == "david"
    # Now appears in approved, not pending
    assert c.get("/api/combinations/pending").get_json() == []
    assert len(c.get("/api/combinations/approved").get_json()) == 1


def test_approve_requires_combination_id(client):
    c, _ = client
    r = c.post("/api/combinations/approve", json={})
    assert r.status_code == 400


def test_approve_returns_404_when_no_pending_match(client):
    c, _ = client
    r = c.post("/api/combinations/approve", json={"combination_id": "ghost"})
    assert r.status_code == 404


# ── Reject ─────────────────────────────────────────────────────────────


def test_reject_requires_reason(client):
    c, ca = client
    ca.propose(_proposal())
    r = c.post(
        "/api/combinations/reject",
        json={"combination_id": "ui_test_combo", "reviewer": "david"},
    )
    assert r.status_code == 400


def test_reject_records_reason_and_reviewer(client):
    c, ca = client
    ca.propose(_proposal("bad_combo"))
    r = c.post(
        "/api/combinations/reject",
        json={
            "combination_id": "bad_combo",
            "reviewer": "david",
            "reason": "duplicates an existing pattern in the registry",
        },
    )
    assert r.status_code == 200
    body = r.get_json()
    assert body["status"] == "rejected"
    assert "duplicates" in body["combination"]["rejection_reason"]


# ── Reset ──────────────────────────────────────────────────────────────


def test_reset_moves_rejected_back_to_pending(client):
    c, ca = client
    ca.propose(_proposal("revive_combo"))
    ca.reject("revive_combo", reviewer="david", reason="not now")
    r = c.post(
        "/api/combinations/reset",
        json={"combination_id": "revive_combo", "reviewer": "david"},
    )
    assert r.status_code == 200
    pending = c.get("/api/combinations/pending").get_json()
    assert any(row["combination_id"] == "revive_combo" for row in pending)


# ── UI page is reachable ──────────────────────────────────────────────


def test_combinations_html_page_renders(client):
    c, _ = client
    r = c.get("/combinations")
    assert r.status_code == 200
    body = r.data.decode("utf-8")
    assert "Combination Approval" in body
    # Endpoint references are constructed in JS as '/api/combinations/'+state
    assert "/api/combinations/" in body
    assert "loadState('pending')" in body
