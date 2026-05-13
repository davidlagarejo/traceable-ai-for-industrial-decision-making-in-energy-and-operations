"""V5 P1 — phase_registry coherence tests.

Ensures every motor in the catalog has an explicit Phase (0-8) or None
assignment, every Phase carries the canonical unit name from its master
document, and the layer_registry + phase_registry are mutually
consistent (no Phase 3 motor is in Layer A, no Phase 1 motor in Layer E, etc.).

Source of truth:
  - governanza/automation-base/motor_dependencies.json (catalog)
  - Phases/phase-{N}/docs/es/{N}_Documento_Maestro_Fase_{N}.md (constitution)
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime_orchestrator.layer_registry import MOTOR_LAYER_MAP
from runtime_orchestrator.phase_registry import (
    MOTOR_PHASE_MAP,
    PHASE_CANONICAL_UNIT,
    PHASE_NAME,
    canonical_unit_for_phase,
    motors_in_phase,
    phase_name,
    phase_of,
)


_REPO_ROOT = Path(__file__).resolve().parents[2]
_DEPS = _REPO_ROOT / "governanza" / "automation-base" / "motor_dependencies.json"


def _catalog_motor_ids() -> set[str]:
    data = json.loads(_DEPS.read_text(encoding="utf-8"))
    return set(data["motors"].keys())


def test_every_catalog_motor_has_a_phase_entry():
    catalog = _catalog_motor_ids()
    registered = set(MOTOR_PHASE_MAP.keys())
    missing = catalog - registered
    extra = registered - catalog
    assert not missing, f"motors missing from phase_registry: {sorted(missing)}"
    assert not extra, f"motors in phase_registry but not in catalog: {sorted(extra)}"


def test_phase_registry_matches_layer_registry_motor_set():
    """The two registries must cover the exact same motor set so the bus
    and the constitutional view stay in sync."""
    layer_motors = set(MOTOR_LAYER_MAP.keys())
    phase_motors = set(MOTOR_PHASE_MAP.keys())
    assert layer_motors == phase_motors, (
        f"divergence: in layer only={sorted(layer_motors - phase_motors)}, "
        f"in phase only={sorted(phase_motors - layer_motors)}"
    )


def test_phase_of_raises_for_unknown_motor():
    with pytest.raises(KeyError, match=r"motor_999"):
        phase_of("motor_999")


def test_each_phase_1_to_8_has_at_least_one_motor():
    for phase_id in range(1, 9):
        motors = motors_in_phase(phase_id)
        assert motors, f"Phase {phase_id} has no motors assigned"


def test_each_phase_has_canonical_unit_name():
    for phase_id in range(0, 9):
        unit = canonical_unit_for_phase(phase_id)
        assert unit, f"Phase {phase_id} missing canonical_unit string"
        name = phase_name(phase_id)
        assert name, f"Phase {phase_id} missing name string"


def test_phase_3_motors_live_in_composer_or_upstream_planner():
    """Reporting motors live in Composer (E), Validators (F), or are
    upstream planners (Layer B) that shape what Phase 3 will compose.

    motor_060 (Report Diversity Engine) sits in Layer B because it emits
    a diversity_axis_plan that constrains Phase 2 hypothesis generation
    AND Phase 3 composition. Phase 3 affiliation reflects its constitutional
    purpose (governing report diversity), Layer B reflects its bus
    position (read by Phase 2 + 3 motors).

    motor_027 (delivery) is Phase 3 but unassigned at the layer level.
    """
    for motor_id in motors_in_phase(3):
        layer = MOTOR_LAYER_MAP[motor_id]
        if motor_id == "motor_027":
            continue
        assert layer in ("B", "E", "F"), (
            f"Phase 3 motor {motor_id} in unexpected layer {layer}"
        )


def test_motor_019_is_phase_3_narrator():
    """motor_019 (LLM Writing) must live in Phase 3. It is the ONLY LLM
    in the framework's analytical chain. Phase 0 constitutional rule."""
    assert phase_of("motor_019") == 3


def test_motor_028_is_phase_1_discovery():
    """motor_028 is the public-data discovery layer (Census/SEC/NYC/EPA/web)."""
    assert phase_of("motor_028") == 1


def test_motor_025_is_phase_0_governance():
    """motor_025 is the Epistemic Governance Layer that owns the 9-state ladder."""
    assert phase_of("motor_025") == 0


def test_motor_014_is_phase_2_decision_core():
    """motor_014 (Decision Core) produces inference_records + tension_map etc."""
    assert phase_of("motor_014") == 2


def test_motor_034_is_phase_4_verification_bridge():
    assert phase_of("motor_034") == 4


def test_motor_045_is_phase_5_probabilistic_finance():
    assert phase_of("motor_045") == 5


def test_motor_053_is_phase_6_regulatory():
    assert phase_of("motor_053") == 6


def test_motor_054_is_phase_7_cognitive():
    assert phase_of("motor_054") == 7


def test_motor_033_is_phase_8_tad():
    assert phase_of("motor_033") == 8


def test_canonical_units_match_master_docs():
    """Verify the canonical units recorded here match the Phase master docs."""
    expected = {
        1: "facility_prior",
        2: "inference_case",
        3: "output_block + report_package",
        4: "claim_upgrade_candidate",
        5: "financial_exposure_case",
        6: "compliance_applicability_case",
        7: "belief_revision_event",
        8: "decision_admissibility_case",
    }
    for phase_id, expected_unit in expected.items():
        assert canonical_unit_for_phase(phase_id) == expected_unit, (
            f"Phase {phase_id} canonical unit mismatch"
        )
