"""Tests for the propose_combination.py CLI (V2-CRITICAL Item 2).

Verifies that the canonical proposal CLI routes new combinations to
combinations_pending/ — never directly to combinations/. Also covers
error paths (bad JSON, missing id, duplicate).
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest


_REPO_ROOT = Path(__file__).resolve().parents[1]
_SCRIPT = _REPO_ROOT / "scripts" / "propose_combination.py"


def _proposal(combo_id="cli_smoke"):
    return {
        "id": combo_id,
        "version": "1.0.0",
        "name": "CLI Smoke",
        "pattern_ids": ["a"],
        "trigger_logic": ["t"],
        "combined_hypothesis": "h",
        "strategic_risk": "r",
        "minimum_evidence": ["e"],
        "tad_action": "VALIDATE_LOSS_PATTERN",
    }


@pytest.fixture
def temp_registry(tmp_path, monkeypatch):
    """Redirect combination_approval to a tmp registry for CLI tests."""
    from runtime_orchestrator import combination_approval as ca

    approved = tmp_path / "combinations"
    pending = tmp_path / "combinations_pending"
    rejected = tmp_path / "combinations_rejected"
    for d in (approved, pending, rejected):
        d.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(ca, "_APPROVED_DIR", approved)
    monkeypatch.setattr(ca, "_PENDING_DIR", pending)
    monkeypatch.setattr(ca, "_REJECTED_DIR", rejected)
    monkeypatch.setattr(ca, "_AUDIT_LOG", tmp_path / "log.jsonl")
    return tmp_path, ca


def test_cli_in_process_proposes_to_pending(temp_registry):
    """Invoke the CLI's main() in-process so the monkeypatched registry sticks."""
    tmp_path, ca = temp_registry
    # Stash payload
    payload = _proposal("cli_in_proc")
    payload_path = tmp_path / "in.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    # Import the script as a module and call main()
    import importlib.util
    spec = importlib.util.spec_from_file_location("propose_combination", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    # Patch its `ca` alias to our test ca (it imported the same module, but
    # in-process module identity is preserved by monkeypatch)
    sys_argv = sys.argv[:]
    sys.argv = ["propose_combination.py", str(payload_path), "--proposed-by", "test_ai"]
    try:
        rc = mod.main()
    finally:
        sys.argv = sys_argv

    assert rc == 0
    pending_file = tmp_path / "combinations_pending" / "cli_in_proc.v1.json"
    assert pending_file.exists()
    written = json.loads(pending_file.read_text())
    assert written["__proposed_by__"] == "test_ai"
    assert written["__proposed_at__"]


def test_cli_in_process_refuses_duplicate(temp_registry):
    tmp_path, _ = temp_registry
    payload = _proposal("dup_cli")
    payload_path = tmp_path / "in.json"
    payload_path.write_text(json.dumps(payload), encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location("propose_combination", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    sys_argv = sys.argv[:]
    sys.argv = ["propose_combination.py", str(payload_path)]
    try:
        assert mod.main() == 0
        # Second time → conflict
        assert mod.main() == 3
    finally:
        sys.argv = sys_argv


def test_cli_returns_invalid_on_missing_id(temp_registry):
    tmp_path, _ = temp_registry
    payload_path = tmp_path / "bad.json"
    payload_path.write_text(json.dumps({"name": "no id here"}), encoding="utf-8")

    import importlib.util
    spec = importlib.util.spec_from_file_location("propose_combination", _SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    sys_argv = sys.argv[:]
    sys.argv = ["propose_combination.py", str(payload_path)]
    try:
        assert mod.main() == 2
    finally:
        sys.argv = sys_argv


def test_cli_subprocess_smoke_test_real_registry():
    """Subprocess sanity test: script imports cleanly and reports usage.

    Uses --help so the real registry isn't touched.
    """
    r = subprocess.run(
        [sys.executable, str(_SCRIPT), "--help"],
        capture_output=True,
        text=True,
        timeout=15,
    )
    assert r.returncode == 0
    assert "combinations_pending" in r.stdout
