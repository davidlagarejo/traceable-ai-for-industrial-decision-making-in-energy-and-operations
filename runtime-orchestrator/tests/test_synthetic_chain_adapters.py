from __future__ import annotations

from runtime_orchestrator.adapters.motor_026 import Motor026Adapter
from runtime_orchestrator.adapters.motor_029 import Motor029Adapter
from runtime_orchestrator.adapters.motor_030 import Motor030Adapter
from runtime_orchestrator.adapters.motor_031 import Motor031Adapter
from runtime_orchestrator.adapters.motor_032 import Motor032Adapter


def test_motor_026_emits_execution_policy_and_source_access_matrix():
    out = Motor026Adapter().run(
        {
            "motor_001": {
                "subject_definition_contract": {"subject_kind": "address_candidate"},
                "target_definition_contract": {"target_scope": "asset"},
                "subject_contract_admissibility": "ambiguous_subject",
            },
            "motor_008": {
                "source_registry": {
                    "src_inline": {
                        "has_content": True,
                        "needs_fetch": False,
                        "authoritative": True,
                        "content_type": "text",
                        "fetch_type": "http",
                        "metadata": {"source_scope": "asset_level"},
                    },
                    "src_fetch": {
                        "has_content": False,
                        "needs_fetch": True,
                        "authoritative": False,
                        "content_type": "reference",
                        "fetch_type": "http",
                        "metadata": {"premium": False},
                    },
                }
            },
            "motor_023": {
                "launch_contract": {
                    "pipeline_id": "addr-demo-2026",
                    "target_id": "addr-demo",
                    "case_mode": "address_first",
                }
            },
        }
    )
    assert out["policy_summary"]["total_sources"] == 2
    assert any(row["access_tier"] == "managed_fetch" for row in out["source_access_matrix"])
    assert all(policy["status"] == "enforced" for policy in out["execution_policy_register"])


def test_synthetic_chain_emits_non_evidentiary_outputs():
    m29 = Motor029Adapter().run(
        {
            "motor_001": {
                "target_definition_contract": {
                    "target_type": "warehouse_distribution",
                    "target_id": "addr-warehouse-demo",
                }
            },
            "motor_002": {"versioned_objects": []},
            "motor_003": {"taxonomy_version": "taxonomy_v1"},
            "motor_013": {
                "inference_case_register": [
                    {
                        "case_id": "LC-ASSET-01",
                        "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                        "claim_family": "conflict",
                        "validation_requirement": "Confirm target asset identity and geometry.",
                        "activation_basis": ["asset_context_readiness"],
                        "dependency_assumptions": ["Asset clusters remain incomplete."],
                        "conditional_statement": "This asset cannot be confirmed from public data alone.",
                    }
                ]
            },
        }
    )
    assert m29["expert_problem_specs"]
    assert m29["expert_problem_specs"][0]["non_evidentiary_flag"] is True

    m30 = Motor030Adapter().run({"motor_029": m29, "motor_002": {}})
    assert m30["generation_manifest"]["generated_dataset_count"] == 1
    assert m30["synthetic_datasets"][0]["synthetic_data_flag"] is True

    m31 = Motor031Adapter().run({"motor_030": m30, "motor_029": m29, "motor_002": {}})
    assert m31["capability_demonstration_reports"]
    assert m31["capability_demonstration_reports"][0]["non_evidentiary_flag"] is True
    assert "gap_to_real_validation" in m31["capability_demonstration_reports"][0]

    m32 = Motor032Adapter().run(
        {
            "motor_031": m31,
            "motor_014": {
                "inference_records": [
                    {
                        "case_id": "LC-ASSET-01",
                        "case_name": "Asset Technical Insufficiency and Scope Mismatch",
                        "claim_family": "conflict",
                    }
                ]
            },
            "motor_001": {},
            "motor_002": {},
        }
    )
    assert m32["synthetic_ml_support_register"]
    assert m32["synthetic_ml_support_register"][0]["synthetic_support_flag"] is True
    assert "validation_data_bridge" in m32["synthetic_ml_support_register"][0]["cannot_substitute"]
