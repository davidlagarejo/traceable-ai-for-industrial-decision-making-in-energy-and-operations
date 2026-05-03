from __future__ import annotations

import importlib.util
from pathlib import Path

from runtime_orchestrator.adapters.motor_036 import Motor036Adapter

_BASE_TEST_PATH = Path(__file__).with_name("test_system_consistency_validator_congruence.py")
_BASE_SPEC = importlib.util.spec_from_file_location(
    "test_system_consistency_validator_congruence_declared_input_base",
    _BASE_TEST_PATH,
)
assert _BASE_SPEC and _BASE_SPEC.loader
_BASE_MODULE = importlib.util.module_from_spec(_BASE_SPEC)
_BASE_SPEC.loader.exec_module(_BASE_MODULE)
_base_inputs = _BASE_MODULE._base_inputs


def test_validator_blocks_promoted_declared_input_rows():
    inputs = _base_inputs()
    inputs["motor_012"] = {
        "asset_field_register": [
            {
                "field": "address",
                "value": "1450 Logistics Parkway, Dallas, TX 75201",
                "status": "OBSERVED",
                "source_id": "declared_input::address",
                "scope": "ASSET_LEVEL",
                "authority_score": "declared_input",
                "recency": "current",
                "admissibility": "CONFIRMED_ASSET_LEVEL",
                "confirmation_state": "DECLARED_BY_USER",
                "notes": "",
            }
        ],
        "declared_input_downgrade_register": [
            {
                "field": "address",
                "confirmation_state": "DECLARED_BY_USER",
                "downgraded_admissibility": "DECLARED_INPUT_ONLY",
            }
        ],
    }

    out = Motor036Adapter().run(inputs)

    assert out["can_render_pdf"] is False
    assert any(
        row["check_id"] == "declared_inputs_not_promoted_as_verified_evidence" and not row["passed"]
        for row in out["consistency_register"]
    )
