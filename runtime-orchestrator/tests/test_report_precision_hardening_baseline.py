from __future__ import annotations

import json
from pathlib import Path

from runtime_orchestrator.adapters.motor_001 import Motor001Adapter
from runtime_orchestrator.adapters.motor_006 import Motor006Adapter
from runtime_orchestrator.adapters.motor_007 import Motor007Adapter
from runtime_orchestrator.asset_contracts import derive_observable_clusters, derive_target_definition


_INPUTS_DIR = Path(__file__).resolve().parents[1] / "inputs"


def _load_pipeline(filename: str) -> dict:
    with (_INPUTS_DIR / filename).open("r", encoding="utf-8") as handle:
        return json.load(handle)


def _run_motor_007_from_seed(filename: str) -> tuple[dict, dict]:
    pipeline = _load_pipeline(filename)
    m01 = Motor001Adapter().run({"__pipeline__": pipeline})
    target_definition = derive_target_definition(pipeline)
    observable_clusters = derive_observable_clusters(pipeline, target_definition)
    m06 = Motor006Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_003": {"term_index": {}, "target_definition_contract": target_definition},
            "motor_005": {
                "normalized_objects": [],
                "normalized_intake_observables": {"observable_clusters": observable_clusters},
            },
        }
    )
    m07 = Motor007Adapter().run({"__pipeline__": pipeline, "motor_006": m06})
    return pipeline, m07


def test_baseline_current_classifier_collapses_ova_and_wilsonart_into_same_blocked_report_type():
    ova_pipeline, ova = _run_motor_007_from_seed("ova_inputs.json")
    wilsonart_pipeline, wilsonart = _run_motor_007_from_seed("mfg_wilsonart_inputs.json")

    assert ova_pipeline["target_definition_contract"]["target_type"] == "commercial_building"
    assert wilsonart_pipeline["target_definition_contract"]["target_type"] == "manufacturing_facility"

    assert ova["target_classification_object"]["target_type"] == "OPERATING_ASSET"
    assert wilsonart["target_classification_object"]["target_type"] == "OPERATING_ASSET"
    assert ova["target_admissibility_state"] == "bounded_asset"
    assert wilsonart["target_admissibility_state"] == "bounded_asset"

    # Baseline symptom to be fixed by the hardening program:
    # two materially different bounded assets still collapse into the same report identity.
    assert ova["recommended_report_type"] == "Decision-Blocked Asset Brief"
    assert wilsonart["recommended_report_type"] == "Decision-Blocked Asset Brief"


def test_baseline_hq_seed_still_degrades_to_nontechnical_report_identity():
    pipeline, out = _run_motor_007_from_seed("pld_inputs.json")

    assert pipeline["target_definition_contract"]["target_type"] == "warehouse_distribution"
    assert out["target_classification_object"]["target_type"] == "CORPORATE_HEADQUARTERS"
    assert out["target_admissibility_state"] == "address_candidate_only"
    assert out["recommended_report_type"] == "Entity Address Classification Brief"
    assert "Full Technical Decision Intelligence Report" in out["prohibited_report_types"]
