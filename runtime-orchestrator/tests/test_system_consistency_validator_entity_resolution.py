from __future__ import annotations

import importlib.util
from pathlib import Path

from runtime_orchestrator.adapters.motor_036 import Motor036Adapter

_BASE_TEST_PATH = Path(__file__).with_name("test_system_consistency_validator_congruence.py")
_BASE_SPEC = importlib.util.spec_from_file_location(
    "test_system_consistency_validator_congruence_base",
    _BASE_TEST_PATH,
)
assert _BASE_SPEC and _BASE_SPEC.loader
_BASE_MODULE = importlib.util.module_from_spec(_BASE_SPEC)
_BASE_SPEC.loader.exec_module(_BASE_MODULE)
_base_inputs = _BASE_MODULE._base_inputs


def test_validator_blocks_unresolved_critical_entity_conflict():
    inputs = _base_inputs()
    inputs["motor_049"] = {
        "asset_family_research_profile": {
            "asset_family": "logistics_warehouse",
            "research_mode": "operator_integrated_congruence",
        },
        "local_evidence_binding_register": [],
        "entity_resolution_register": [
            {
                "source_id": "bill::foreign",
                "source_family": "utility_bill_record",
                "resolution_state": "foreign_asset_conflict",
            }
        ],
        "entity_conflict_register": [
            {
                "source_id": "bill::foreign",
                "source_family": "utility_bill_record",
                "severity": "critical",
                "resolution_state": "unresolved_conflict",
            }
        ],
        "asset_boundary_resolution_register": [
            {
                "boundary_dimension": "physical_asset_boundary",
                "boundary_state": "conflicted",
            }
        ],
    }

    out = Motor036Adapter().run(inputs)

    assert out["can_render_pdf"] is False
    assert any(
        row["check_id"] == "entity_resolution_conflicts_not_unresolved" and not row["passed"]
        for row in out["consistency_register"]
    )
