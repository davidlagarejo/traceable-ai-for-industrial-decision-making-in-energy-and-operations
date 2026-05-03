from __future__ import annotations

from target_seeds import build_bounded_asset_seed
from runtime_orchestrator.adapters.motor_001 import Motor001Adapter
from runtime_orchestrator.adapters.motor_006 import Motor006Adapter
from runtime_orchestrator.adapters.motor_007 import Motor007Adapter
from runtime_orchestrator.adapters.motor_012 import Motor012Adapter
from runtime_orchestrator.asset_contracts import derive_observable_clusters, derive_target_definition


def test_motor_012_downgrades_declared_input_fields_until_publicly_confirmed():
    pipeline = build_bounded_asset_seed(
        address_raw="1450 LOGISTICS PARKWAY, DALLAS, TX, 75201",
        asset_name="Sunrise Logistics Hub",
        target_type="warehouse_distribution",
        owner_name="Warehouse Income REIT",
        owner_ticker="WIRE",
        asset_identifier="sunrise-logistics-hub-2026",
        asset_anchor_type="operator_assertion",
        asset_anchor_value="operator::sunrise",
        jurisdiction_scope=["US-TX"],
        primary_uses=["Warehouse / distribution"],
    )
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

    out = Motor012Adapter().run(
        {
            "__pipeline__": pipeline,
            "motor_001": m01,
            "motor_004": {"parsed_objects": []},
            "motor_005": {"normalized_objects": []},
            "motor_007": m07,
            "motor_008": {"total_sources": 0},
            "motor_011": {"library_objects": []},
            "motor_028": {
                "quality_gate_passed": True,
                "dataset_coverage_register": [],
                "source_register": [],
                "enriched_data": {
                    "requestable_evidence_items": [],
                    "coverage_gaps": [],
                    "benchmark_routing_register": {},
                },
            },
        }
    )

    field_rows = {row["field"]: row for row in out["asset_field_register"]}
    assert field_rows["address"]["confirmation_state"] == "DECLARED_BY_USER"
    assert field_rows["address"]["admissibility"] == "DECLARED_INPUT_ONLY"
    assert out["canonical_asset_context_summary"]["screening_supported"] is False
    assert any(row["field"] == "address" for row in out["declared_input_downgrade_register"])
    assert any(row["missing_field"] == "address" for row in out["missing_evidence_register"])
