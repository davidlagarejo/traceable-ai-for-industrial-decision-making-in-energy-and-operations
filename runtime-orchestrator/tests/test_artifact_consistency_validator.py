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


def _failure_ids(out: dict) -> set[str]:
    return {row["check_id"] for row in out["blocking_reason_register"]}


def test_artifact_consistency_validator_blocks_empty_critical_sections_without_fallback():
    inputs = deepcopy(_base_inputs())
    report_package = inputs["motor_016"]["report_package"]
    for section in report_package["approved_views"]["report_view"]["body_sections"]:
        if section.get("title") == "Peer / Competitive Comparison":
            section["blocks"] = [{"content": "No competitive-comparison rows were produced."}]
    for section in report_package["approved_views"]["report_view"]["appendix_sections"]:
        if section.get("title") == "Public Source Coverage Table":
            section["blocks"] = [{"content": "No routed public-source coverage rows were produced."}]
    report_package["section_population_status_register"] = []
    report_package["section_explanation_fallback_register"] = []

    out = Motor036Adapter().run(inputs)
    assert "section_nonempty_or_explained" in _failure_ids(out)


def test_artifact_consistency_validator_blocks_unactivated_source_families_and_mode_mismatch():
    inputs = deepcopy(_base_inputs())
    report_package = inputs["motor_016"]["report_package"]
    inputs["motor_028"]["source_register"] = [
        {"source_family": "benchmarking_disclosure_record", "source_type": "ll84_record", "title": "NYC LL84", "accepted": True}
    ]
    report_package["source_family_coverage_table"] = [
        {
            "source_family": "ghost_family",
            "source_name": "Ghost Family",
            "queried": True,
            "found": True,
            "scope": "ASSET_LEVEL",
            "fields_extracted": ["mystery_field"],
            "support_note": "bounded source note",
        }
    ]
    report_package["executive_thesis"]["report_mode"] = "Target Classification Brief"

    out = Motor036Adapter().run(inputs)
    failure_ids = _failure_ids(out)
    assert "source_family_activation_match" in failure_ids
    assert "report_mode_consistency_match" in failure_ids
