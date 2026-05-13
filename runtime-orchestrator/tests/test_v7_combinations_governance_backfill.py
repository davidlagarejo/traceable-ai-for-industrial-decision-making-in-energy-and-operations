"""V7 P2 — verify the 4 registry-level combinations carry the V6/V7
governance fields after backfill.

Cada combination en `zlab_skill/registry/combinations/*.json` debe declarar:
  - required_asset_family    (1 family from ALL_KNOWN_ASSET_FAMILIES)
  - allowed_claim_ceiling    (L0 / L1 / L2)
  - required_evidence_pack   (non-empty id string)
  - tad_mapping              (subset of 8 canonical action families)
  - allowed_render_modes     (subset of 8 publication states)
  - forbidden_render_modes   (subset of 8 publication states)
  - falsification            (non-empty narrative)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime_orchestrator.industrial_research_engine.family_scope import (
    ALL_KNOWN_ASSET_FAMILIES,
)

_CANONICAL_ACTION_FAMILIES = frozenset({
    "inspect", "measure", "classify", "pilot",
    "design", "procure", "implement", "defer",
})
_VALID_RENDER_MODES = frozenset({
    "internal_debug_only", "exploratory_prior",
    "structural_hypothesis", "bounded_peer_analysis",
    "evidence_discrimination", "decision_blocked",
    "publish_bounded", "client_safe",
})
_ALLOWED_CLAIM_CEILINGS = frozenset({"L0", "L1", "L2"})

_REGISTRY = (
    Path(__file__).resolve().parents[1] / "zlab_skill" / "registry" / "combinations"
)


def _all_combos() -> list[dict]:
    rows = []
    for path in sorted(_REGISTRY.glob("*.v1.json")):
        rows.append(json.loads(path.read_text(encoding="utf-8")))
    return rows


@pytest.fixture(scope="module")
def combos():
    return _all_combos()


def test_exactly_four_combinations_in_registry(combos):
    """V7 doctrine: keep the catalog at 4. Growth pauses during hardening."""
    assert len(combos) == 4
    ids = {c["id"] for c in combos}
    assert ids == {
        "process_heat_unbounded_duty_combo",
        "manufacturing_support_utility_maintenance_combo",
        "warehouse_tariff_boundary_area_combo",
        "office_after_hours_phantom_load_combo",
    }


def test_every_combo_declares_required_asset_family(combos):
    for c in combos:
        af = c.get("required_asset_family", "")
        assert af, f"{c['id']} missing required_asset_family"
        assert af in ALL_KNOWN_ASSET_FAMILIES, (
            f"{c['id']}.required_asset_family={af!r} not in canonical taxonomy"
        )


def test_every_combo_declares_allowed_claim_ceiling(combos):
    for c in combos:
        cc = c.get("allowed_claim_ceiling", "")
        assert cc in _ALLOWED_CLAIM_CEILINGS, (
            f"{c['id']}.allowed_claim_ceiling={cc!r} not in {sorted(_ALLOWED_CLAIM_CEILINGS)}"
        )


def test_every_combo_declares_evidence_pack(combos):
    for c in combos:
        ep = c.get("required_evidence_pack", "")
        assert ep and isinstance(ep, str), (
            f"{c['id']} missing required_evidence_pack"
        )


def test_every_combo_evidence_pack_is_unique(combos):
    """V7 doctrine: no shared evidence pack between combinations."""
    packs = [c["required_evidence_pack"] for c in combos]
    assert len(packs) == len(set(packs)), (
        f"evidence_pack ids must be unique across combinations: {packs}"
    )


def test_every_combo_tad_mapping_canonical(combos):
    for c in combos:
        tm = c.get("tad_mapping", [])
        assert tm, f"{c['id']} missing tad_mapping"
        unknown = sorted(set(tm) - _CANONICAL_ACTION_FAMILIES)
        assert not unknown, (
            f"{c['id']}.tad_mapping has non-canonical actions: {unknown}"
        )


def test_every_combo_render_modes_valid(combos):
    for c in combos:
        allowed = set(c.get("allowed_render_modes", []) or [])
        forbidden = set(c.get("forbidden_render_modes", []) or [])
        assert allowed, f"{c['id']} missing allowed_render_modes"
        unknown_a = sorted(allowed - _VALID_RENDER_MODES)
        unknown_f = sorted(forbidden - _VALID_RENDER_MODES)
        assert not unknown_a, f"{c['id']}.allowed_render_modes invalid: {unknown_a}"
        assert not unknown_f, f"{c['id']}.forbidden_render_modes invalid: {unknown_f}"
        overlap = allowed & forbidden
        assert not overlap, (
            f"{c['id']}: modes in BOTH allowed and forbidden: {sorted(overlap)}"
        )


def test_every_combo_forbids_client_safe(combos):
    """V7 P2: the 4 pre-V7 combinations cap at publish_bounded.
    Promotion to client_safe requires evidence not yet bound to a combo."""
    for c in combos:
        forbidden = set(c.get("forbidden_render_modes", []) or [])
        assert "client_safe" in forbidden, (
            f"{c['id']} must forbid client_safe until promoted via V8"
        )


def test_every_combo_has_falsification(combos):
    for c in combos:
        f = c.get("falsification", "")
        assert f and isinstance(f, str), (
            f"{c['id']} missing falsification narrative"
        )


def test_every_combo_has_minimum_two_pattern_ids(combos):
    for c in combos:
        pids = c.get("pattern_ids", [])
        assert len(pids) >= 2, (
            f"{c['id']} must combine ≥2 patterns (V6 strict); has {len(pids)}"
        )


def test_combos_still_load_via_registry_loader():
    """The runtime loader continues to validate them as combination_spec."""
    from runtime_orchestrator.zlab_skill.loader import load_combination_specs
    rows = load_combination_specs()
    assert len(rows) == 4
    for row in rows:
        assert row["id"].endswith("_combo")
