from runtime_orchestrator.adapters.motor_013 import Motor013Adapter
from runtime_orchestrator.adapters.motor_014 import Motor014Adapter


def test_manufacturing_family_suppresses_leasing_style_concentration_case():
    adapter = Motor013Adapter()
    out = adapter.run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_type": "manufacturing_facility",
                    "asset_name": "Deer Park Manufacturing Campus",
                    "facility_prior_id": "fp:mfg-test",
                    "entities": {
                        "Facility": {
                            "jurisdiction": ["US-TX"],
                        },
                        "SectorArchetype": {
                            "anchor_tenant": "Example Counterparty",
                            "anchor_tenant_sqft": 100000,
                            "customer_concentration": 0.42,
                        },
                        "AssetIdentity": {
                            "asset_context_readiness": "asset_context_insufficient",
                            "missing_observable_clusters": [
                                "geometry_size_cluster",
                                "systems_cluster",
                            ],
                        },
                    },
                    "uncertainty_markers": [
                        {"dimension": "throughput_not_observed"},
                    ],
                }
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    case_ids = {row["case_id"] for row in out["inference_case_register"]}
    assert "LC-OPS-01" not in case_ids
    assert "LC-ASSET-01" in case_ids
    assert "LC-OPS-05" in case_ids
    suppressed = [
        row for row in out["activation_log"]
        if row["case_id"] == "LC-OPS-01"
    ]
    assert suppressed
    assert suppressed[0]["status"] == "suppressed_by_target_family"


def test_manufacturing_family_does_not_emit_counterparty_opportunity_downstream():
    facility_prior = {
        "target_definition": {
            "target_type": "manufacturing_facility",
        },
        "asset_name": "Deer Park Manufacturing Campus",
        "facility_prior_id": "fp:mfg-chain",
        "entities": {
            "Facility": {
                "jurisdiction": ["US-TX"],
            },
            "SectorArchetype": {
                "anchor_tenant": "Example Counterparty",
                "anchor_tenant_sqft": 100000,
                "customer_concentration": 0.42,
                "primary_fuel": "natural_gas",
            },
            "RegulatoryContext": {
                "primary_regulation": "ASHRAE_90.1",
                "regulatory_flags": ["energy_code_screening"],
            },
            "AssetIdentity": {
                "asset_context_readiness": "asset_context_insufficient",
                "missing_observable_clusters": [
                    "geometry_size_cluster",
                    "systems_cluster",
                ],
            },
        },
        "uncertainty_markers": [
            {"marker_id": "UM-1", "dimension": "throughput_not_observed", "description": "Missing throughput", "impact": "High", "resolution_path": "Request operator records"},
        ],
        "missing_evidence_register": [
            {
                "missing_field": "throughput",
                "why_it_matters": "Process redesign depends on throughput.",
                "decision_blocked": "process redesign",
                "minimum_evidence_needed": "throughput profile",
                "suggested_source": "operator records",
            }
        ],
        "target_admissibility_state": "bounded_asset",
        "subject_gate_passed": True,
    }
    inference = Motor013Adapter().run(
        {
            "motor_012": {
                "facility_prior": facility_prior,
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    out = Motor014Adapter().run(
        {
            "motor_013": inference,
            "motor_012": {"facility_prior": facility_prior},
            "motor_034": {},
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
            "motor_001": {},
        }
    )
    tension_ids = {row["inference_case_id"] for row in out["tension_records"]}
    assert "LC-OPS-01" not in tension_ids
    opportunity_types = {row["opportunity_type"] for row in out["opportunity_candidates"]}
    assert "counterparty_risk_mitigation" not in opportunity_types
    serialized = str(out["opportunity_candidates"]).lower()
    assert "subletting" not in serialized
    assert "lease extension" not in serialized


def test_building_family_does_not_emit_certification_gap_without_actual_certifications():
    out = Motor013Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_type": "commercial_building",
                    "asset_name": "One Vanderbilt",
                    "facility_prior_id": "fp:ova-test",
                    "entities": {
                        "Facility": {
                            "jurisdiction": ["US-NY-NYC"],
                            "certifications": [],
                        },
                        "EnergyContext": {
                            "certifications_declared": [],
                            "current_EUI_status": "not_confirmed — declared certifications may not reflect current performance",
                        },
                        "RegulatoryContext": {
                            "primary_regulation": "NYC_Local_Law_97_2019",
                        },
                        "AssetIdentity": {
                            "asset_context_readiness": "partial",
                            "missing_observable_clusters": ["systems_cluster"],
                        },
                    },
                }
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    case_ids = {row["case_id"] for row in out["inference_case_register"]}
    assert "LC-REG-02" not in case_ids


def test_building_family_does_not_emit_fuel_transition_case_without_observed_fuel_basis():
    out = Motor013Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_type": "commercial_building",
                    "asset_name": "One Vanderbilt",
                    "facility_prior_id": "fp:ova-fuel-test",
                    "entities": {
                        "Facility": {
                            "jurisdiction": ["US-NY-NYC"],
                        },
                        "SectorArchetype": {
                            "primary_fuel": "",
                            "secondary_fuel": "",
                        },
                        "EnergyContext": {
                            "primary_fuel": "",
                            "secondary_fuel": "",
                        },
                        "AssetIdentity": {
                            "asset_context_readiness": "partial",
                            "missing_observable_clusters": ["fuel_energy_cluster"],
                        },
                    },
                }
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    case_ids = {row["case_id"] for row in out["inference_case_register"]}
    assert "LC-MKT-02" not in case_ids


def test_motor_014_uses_structural_problem_frame_as_default_reasoning_path():
    facility_prior = {
        "target_definition": {
            "target_type": "commercial_building",
        },
        "asset_name": "One Vanderbilt",
        "facility_prior_id": "fp:ova-structural-path",
        "entities": {
            "Facility": {
                "jurisdiction": ["US-NY-NYC"],
            },
            "RegulatoryContext": {
                "primary_regulation": "NYC_Local_Law_97_2019",
                "regulatory_flags": ["ll97_screening"],
            },
            "AssetIdentity": {
                "asset_context_readiness": "partial",
                "missing_observable_clusters": ["systems_cluster", "control_boundary_cluster"],
            },
        },
        "missing_evidence_register": [],
        "minimum_evidence_pack_seed": [],
        "target_admissibility_state": "bounded_asset",
        "subject_gate_passed": True,
    }
    inference = Motor013Adapter().run(
        {
            "motor_012": {"facility_prior": facility_prior},
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    out = Motor014Adapter().run(
        {
            "motor_013": inference,
            "motor_012": {"facility_prior": facility_prior},
            "motor_034": {
                "canonical_problem_frame": {
                    "reasoning_path": "structural_first",
                    "problem_frame_active": True,
                    "reframed_problem": "Need to distinguish owner-controlled systems from tenant-driven load.",
                },
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                },
            },
            "motor_038": {
                "dominant_variable_register": [
                    {"variable": "tenant_metering", "evidence_state": "CONDITIONAL_HYPOTHESIS"}
                ]
            },
            "motor_040": {
                "cross_layer_conflict_register": [
                    {"conflict": "Regulation vs control boundary"}
                ]
            },
            "motor_046": {
                "minimum_evidence_for_discrimination_register": [
                    {
                        "rival_hypotheses": [
                            "Owner-controlled base-building upside dominates.",
                            "Tenant-driven load dominates.",
                        ],
                        "minimum_evidence": "utility bills + tenant metering map + BMS topology",
                        "source": "operator request",
                        "what_it_falsifies": "Incorrect retrofit framing",
                        "unlocks": "bounded redesign path",
                    }
                ]
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
            "motor_001": {},
            "motor_037": {},
            "motor_041": {},
        }
    )

    assert out["canonical_problem_frame"]["reasoning_path"] == "structural_first"
    assert out["structural_reasoning_path"]["problem_frame_active"] is True
    assert out["minimum_evidence_unlock_map"][0]["structural_discrimination"] is True
    assert out["next_best_questions"][0]["linked_case"] == "STRUCTURAL-PROBLEM-FRAME"


def test_canonical_asset_context_reanchors_asset_case_validation_for_building_screening():
    out = Motor013Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_type": "commercial_building",
                    "asset_name": "One Vanderbilt",
                    "facility_prior_id": "fp:ova-canonical-test",
                    "canonical_asset_context_summary": {
                        "canonical_asset_context_state": "asset_context_minimal",
                        "missing_clusters": [
                            "boundary_cluster",
                            "operating_regime_cluster",
                            "fuel_energy_cluster",
                            "systems_cluster",
                            "control_boundary_cluster",
                        ],
                        "supported_clusters": [
                            "identity_cluster",
                            "geometry_size_cluster",
                            "vintage_structure_cluster",
                            "regulatory_cluster",
                        ],
                        "screening_supported": True,
                    },
                    "entities": {
                        "Facility": {
                            "jurisdiction": ["US-NY-NYC"],
                        },
                        "AssetIdentity": {
                            "asset_context_readiness": "asset_context_insufficient",
                            "missing_observable_clusters": [
                                "identity_cluster",
                                "geometry_size_cluster",
                                "systems_cluster",
                            ],
                        },
                    },
                }
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )

    asset_case = next(row for row in out["inference_case_register"] if row["case_id"] == "LC-ASSET-01")
    assert "identity and geometry" not in asset_case["validation_requirement"].lower()
    assert "tenant metering" in asset_case["validation_requirement"].lower()
    assert "hvac / bms / central-plant inventory" in asset_case["validation_requirement"].lower()


def test_building_family_reframes_ops01_as_control_boundary_exposure_when_anchor_exists():
    out = Motor013Adapter().run(
        {
            "motor_012": {
                "facility_prior": {
                    "target_type": "commercial_building",
                    "asset_name": "One Vanderbilt",
                    "facility_prior_id": "fp:ova-ops-test",
                    "entities": {
                        "Facility": {
                            "jurisdiction": ["US-NY-NYC"],
                        },
                        "SectorArchetype": {
                            "anchor_tenant": "Anchor Tenant",
                            "anchor_tenant_sqft": 300000,
                        },
                        "AssetIdentity": {
                            "asset_context_readiness": "partial",
                            "missing_observable_clusters": ["tenant_control_cluster"],
                        },
                    },
                }
            },
            "motor_007": {
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
            },
        }
    )
    case = next(row for row in out["inference_case_register"] if row["case_id"] == "LC-OPS-01")
    assert case["case_name"] == "Lease Concentration and Control-Boundary Exposure"
    assert "tenant metering" in case["conditional_statement"].lower()
    assert "lease responsibility matrix" in case["validation_requirement"].lower()
    assert "subletting" not in case["validation_requirement"].lower()
