from __future__ import annotations

import importlib.util
from copy import deepcopy
from pathlib import Path

from runtime_orchestrator.adapters.motor_036 import Motor036Adapter

_BASE_TEST_PATH = Path(__file__).with_name("test_system_consistency_validator_congruence.py")
_BASE_SPEC = importlib.util.spec_from_file_location("test_validator_congruence_base", _BASE_TEST_PATH)
assert _BASE_SPEC and _BASE_SPEC.loader
_BASE_MODULE = importlib.util.module_from_spec(_BASE_SPEC)
_BASE_SPEC.loader.exec_module(_BASE_MODULE)
_base_inputs = _BASE_MODULE._base_inputs


def test_claim_consistency_engine_blocks_mismatched_summary_counts():
    inputs = deepcopy(_base_inputs())
    inputs["motor_014"]["claim_permission_summary"] = {
        "allowed_count": 99,
        "conditional_count": 0,
        "prohibited_count": 0,
        "deferred_count": 0,
    }

    out = Motor036Adapter().run(inputs)
    failure_ids = {row["check_id"] for row in out["blocking_reason_register"]}
    assert "claim_summary_count_match" in failure_ids
