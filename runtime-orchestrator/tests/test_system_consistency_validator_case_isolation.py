from __future__ import annotations

import importlib.util
from pathlib import Path

from runtime_orchestrator.adapters.motor_036 import Motor036Adapter

_BASE_TEST_PATH = Path(__file__).with_name("test_system_consistency_validator_congruence.py")
_BASE_SPEC = importlib.util.spec_from_file_location(
    "test_system_consistency_validator_congruence_case_isolation_base",
    _BASE_TEST_PATH,
)
assert _BASE_SPEC and _BASE_SPEC.loader
_BASE_MODULE = importlib.util.module_from_spec(_BASE_SPEC)
_BASE_SPEC.loader.exec_module(_BASE_MODULE)
_base_inputs = _BASE_MODULE._base_inputs


def test_validator_blocks_foreign_chart_case_context():
    inputs = _base_inputs()
    report_package = dict(inputs["motor_016"]["report_package"])
    report_package["case_metadata"] = {
        **dict(report_package.get("case_metadata", {}) or {}),
        "case_fingerprint": "expected123",
    }
    report_package["assets"] = [
        {
            "asset_id": "chart_foreign",
            "asset_type": "chart",
            "title": "Foreign chart",
            "chart_context": {
                "case_fingerprint": "foreign999",
                "target_identifier": "wrong-target",
            },
        }
    ]
    report_package["chart_case_match_register"] = [
        {
            "asset_id": "chart_foreign",
            "case_match_state": "foreign_case_fingerprint",
            "severity": "critical",
            "problem": "Chart asset fingerprint does not match the current case.",
            "action": "block_report_generation",
        }
    ]
    report_package["cross_case_contamination_scan"] = {
        "render_eligible": False,
        "issue_count": 1,
        "issues": [
            {
                "issue_code": "foreign_case_fingerprint",
                "severity": "critical",
                "asset_id": "chart_foreign",
            }
        ],
    }
    inputs["motor_016"]["report_package"] = report_package

    out = Motor036Adapter().run(inputs)

    assert out["can_render_pdf"] is False
    assert any(
        row["check_id"] == "chart_assets_match_current_case" and not row["passed"]
        for row in out["consistency_register"]
    )
