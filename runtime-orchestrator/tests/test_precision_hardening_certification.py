from __future__ import annotations

from copy import deepcopy

from runtime_orchestrator.adapters.motor_013 import Motor013Adapter
from runtime_orchestrator.adapters.motor_014 import Motor014Adapter
from runtime_orchestrator.adapters.motor_025 import Motor025Adapter
from runtime_orchestrator.adapters.motor_033 import Motor033Adapter
from runtime_orchestrator.adapters.motor_034 import Motor034Adapter


def _field(
    field: str,
    value,
    *,
    status: str = "OBSERVED",
    scope: str = "ASSET_LEVEL",
    authority_score: str = "high",
    admissibility: str = "CONFIRMED_ASSET_LEVEL",
    source_id: str | None = None,
) -> dict:
    return {
        "field": field,
        "value": value,
        "status": status,
        "source_id": source_id or f"case::{field}",
        "scope": scope,
        "authority_score": authority_score,
        "recency": "current",
        "admissibility": admissibility,
        "notes": "",
    }


def _find_claim(output: dict, claim_name: str) -> dict:
    return next(row for row in output["claim_permission_register"] if row["claim_name"] == claim_name)


def _build_screening_case_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
                "target_name": "One Vanderbilt",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "high",
            },
            "target_admissibility_state": "bounded_asset",
            "subject_gate_passed": True,
            "technical_substrate_readiness": "partial",
            "recommended_report_type": "Decision-Blocked Asset Brief",
            "allowed_report_classes": [
                "Decision-Blocked Asset Brief",
                "Exploratory Prior Brief",
                "Compliance / Investment Screening Brief",
            ],
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "asset_field_register": [
                _field("address", "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", source_id="nyc_dof_property_record::ova"),
                _field("asset_class", "commercial_building", source_id="nyc_pluto_property::ova"),
                _field("GFA", "1678135", source_id="nyc_pluto_property::ova"),
                _field("occupancy", "office", source_id="nyc_pluto_property::ova"),
                _field("year_built", "2020", source_id="nyc_pluto_property::ova"),
                _field("current_EUI", "120.5", source_id="nyc_ll84_energy_benchmarking::ova"),
                _field("emissions", "16184.23", source_id="nyc_ll84_energy_benchmarking::ova"),
                _field("compliance_filings", "LL84 public benchmarking disclosure observed (2024)", source_id="nyc_ll84_energy_benchmarking::ova"),
            ],
            "facility_prior": {
                "asset_name": "One Vanderbilt",
                "target_definition": {"target_type": "commercial_building"},
                "asset_context_readiness": "partial",
                "missing_physical_observables_register": [
                    "operating_regime_cluster",
                    "fuel_energy_cluster",
                    "systems_cluster",
                    "tenant_control_cluster",
                ],
                "missing_evidence_register": [
                    {
                        "evidence_item": "Utility bills and tenant metering basis",
                        "source": "owner / operator",
                        "why_needed": "Bound owner-controllable energy baseline.",
                        "unlocks": ["acquisition underwriting with energy upside", "energy retrofit CAPEX"],
                        "effort": "medium",
                    },
                    {
                        "evidence_item": "HVAC/BMS inventory and central-plant scope",
                        "source": "operator engineering records",
                        "why_needed": "Confirm systems and controllable intervention path.",
                        "unlocks": ["energy retrofit CAPEX", "compliance investment"],
                        "effort": "medium",
                    },
                    {
                        "evidence_item": "Lease responsibility and control boundary",
                        "source": "lease / operator records",
                        "why_needed": "Define who captures economics and controls loads.",
                        "unlocks": ["acquisition underwriting with energy upside", "compliance investment"],
                        "effort": "medium",
                    },
                ],
                "entities": {
                    "RegulatoryContext": {
                        "regulatory_flags": ["ll97_screening", "ll84_observed"],
                    }
                },
            },
            "compliance_applicability_case": {
                "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                "trigger_field_register": [
                    {"field_name": "jurisdiction_codes", "field_state": "observed"},
                    {"field_name": "GFA_sqft", "field_state": "observed"},
                ],
                "applicability_state": "trigger_partially_supported",
                "compliance_posture_state": "trigger_plausible",
                "screening_basis_register": [
                    {"basis_name": "regulated_floor_area_basis", "basis_value": 1678135, "basis_unit": "sqft"},
                    {"basis_name": "ll97_compliance_period", "basis_value": "2024-2029", "basis_unit": ""},
                    {"basis_name": "ll97_penalty_rate", "basis_value": 268, "basis_unit": "USD_per_metric_ton_CO2e"},
                ],
            },
        },
        "motor_028": {
            "source_register": [
                {"source_type": "nyc_pluto_property", "accepted": True},
                {"source_type": "nyc_ll84_energy_benchmarking", "accepted": True},
                {"source_type": "nyc_dof_property_record", "accepted": True},
                {"source_type": "nyc_dob_permits", "accepted": True},
            ],
            "dataset_coverage_register": [
                {"dataset_key": "nyc_dof_property_record", "status": "accepted", "field_coverage": ["address", "parcel_id"], "notes": "", "matched_sources": ["nyc_dof_property_record"]},
                {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA", "year_built"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
                {"dataset_key": "nyc_dob_permits", "status": "accepted", "field_coverage": ["systems"], "notes": "", "matched_sources": ["nyc_dob_permits"]},
                {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted", "field_coverage": ["EUI", "emissions"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
                {"dataset_key": "nyc_ll97_emissions", "status": "screened", "field_coverage": ["penalty_rate", "compliance_period"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
            ],
        },
    }


def _build_wilsonart_case_inputs() -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "2400 W ADAMS AVE, TEMPLE, TX, 76504",
                "jurisdiction_scope": ["US-TX"],
                "target_type": "manufacturing_facility",
                "target_name": "Wilsonart Temple North Laminate Facility",
            },
            "target_classification_object": {
                "target_type": "OPERATING_ASSET",
                "classification_confidence": "medium",
            },
            "target_admissibility_state": "bounded_asset",
            "subject_gate_passed": True,
            "technical_substrate_readiness": "partial",
            "recommended_report_type": "Decision-Blocked Asset Brief",
            "allowed_report_classes": [
                "Decision-Blocked Asset Brief",
                "Exploratory Prior Brief",
                "Compliance / Investment Screening Brief",
            ],
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "asset_field_register": [
                _field("address", "2400 W ADAMS AVE, TEMPLE, TX, 76504", source_id="tceq_facility_record::wilsonart"),
                _field("asset_class", "manufacturing_facility", source_id="tceq_facility_record::wilsonart"),
                _field("operating_schedule", "proxy: multi-shift manufacturing operations", source_id="company_facility_page::wilsonart", authority_score="medium"),
                _field("load_driver", "laminate pressing and curing duty", source_id="company_facility_page::wilsonart", authority_score="medium"),
                _field("process_flow", "public process description for laminate production", source_id="company_facility_page::wilsonart", authority_score="medium"),
                _field("permits", "TCEQ air permit record observed", source_id="tceq_air_permit::wilsonart"),
                _field("emissions", "VOC / criteria pollutant profile observed", source_id="epa_echo::wilsonart"),
                _field("compliance_filings", "Permit and emissions compliance references observed", source_id="tceq_air_permit::wilsonart"),
            ],
            "facility_prior": {
                "asset_name": "Wilsonart Temple North Laminate Facility",
                "target_definition": {"target_type": "manufacturing_facility"},
                "asset_context_readiness": "partial",
                "missing_physical_observables_register": [
                    "geometry_size_cluster",
                    "vintage_structure_cluster",
                    "operating_regime_cluster",
                    "fuel_energy_cluster",
                    "systems_cluster",
                    "tenant_control_cluster",
                ],
                "missing_evidence_register": [
                    {
                        "evidence_item": "Process and major energy-using equipment inventory",
                        "source": "operator engineering records",
                        "why_needed": "Bound the plant process and support systems.",
                        "unlocks": ["process efficiency or utility-support CAPEX", "process redesign"],
                        "effort": "high",
                    },
                    {
                        "evidence_item": "Throughput, shift schedule, and downtime profile",
                        "source": "operator production records",
                        "why_needed": "Separate structural process load from operational inefficiency.",
                        "unlocks": ["process efficiency or utility-support CAPEX", "utility cost optimization"],
                        "effort": "high",
                    },
                    {
                        "evidence_item": "Utility bills, tariff context, and meter map",
                        "source": "operator / utility records",
                        "why_needed": "Confirm load drivers and cost basis.",
                        "unlocks": ["utility cost optimization", "permit-driven investment"],
                        "effort": "high",
                    },
                ],
                "entities": {
                    "RegulatoryContext": {
                        "regulatory_flags": ["tceq_air_permit", "epa_echo", "tri_if_applicable"],
                    }
                },
            },
            "compliance_applicability_case": {
                "rule_family_record": [{"rule_family_name": "TCEQ air permitting"}],
                "trigger_field_register": [
                    {"field_name": "permit_record", "field_state": "observed"},
                ],
                "applicability_state": "trigger_partially_supported",
                "compliance_posture_state": "trigger_plausible",
                "screening_basis_register": [
                    {"basis_name": "tceq_permit_basis", "basis_value": "air permit observed", "basis_unit": ""},
                    {"basis_name": "echo_enforcement_context", "basis_value": "public screening only", "basis_unit": ""},
                ],
            },
        },
        "motor_028": {
            "source_register": [
                {"source_type": "tceq_air_permit", "accepted": True},
                {"source_type": "epa_echo", "accepted": True},
                {"source_type": "epa_tri", "accepted": True},
                {"source_type": "county_appraisal_district_property_record", "accepted": False},
            ],
            "dataset_coverage_register": [
                {"dataset_key": "tceq_permits_and_emissions", "status": "accepted", "field_coverage": ["permits", "emissions"], "notes": "", "matched_sources": ["tceq_air_permit"]},
                {"dataset_key": "epa_echo_screening", "status": "accepted", "field_coverage": ["compliance_filings"], "notes": "", "matched_sources": ["epa_echo"]},
                {"dataset_key": "epa_tri_screening", "status": "screened", "field_coverage": ["emissions"], "notes": "", "matched_sources": ["epa_tri"]},
            ],
        },
    }


def _run_decision_chain(inputs: dict) -> tuple[dict, dict, dict]:
    m34 = Motor034Adapter().run(inputs)
    m14 = Motor014Adapter().run(
        {
            "motor_001": inputs.get("motor_001", {}),
            "motor_007": inputs.get("motor_007", {}),
            "motor_012": inputs.get("motor_012", {}),
            "motor_013": {"inference_case_register": [], "facility_prior_id": "fp-test"},
            "motor_034": m34,
        }
    )
    m33 = Motor033Adapter().run(
        {
            "motor_012": inputs.get("motor_012", {}),
            "motor_014": m14,
            "motor_015": {},
            "motor_034": m34,
        }
    )
    return m34, m14, m33


def test_one_vanderbilt_expected_behavior_supports_screening_but_blocks_roi_and_closure():
    inputs = _build_screening_case_inputs()
    m34, m14, m33 = _run_decision_chain(inputs)

    assert m34["report_readiness_register"]["report_type_allowed"] == ["Compliance / Investment Screening Brief"]
    assert _find_claim(m34, "numeric_eui_claim")["current_permission"] in {"allowed", "conditional"}
    assert _find_claim(m34, "ll97_penalty_screening_claim")["current_permission"] in {"allowed", "conditional"}
    assert _find_claim(m34, "roi_range_claim")["current_permission"] == "prohibited"
    assert _find_claim(m34, "energy_savings_claim")["current_permission"] == "prohibited"
    assert _find_claim(m34, "compliance_closure_claim")["current_permission"] == "prohibited"
    assert m34["cluster_report_readiness_profile"]["strong_public_screening_possible"] is True

    evidence_items = [row["evidence_item"] for row in m14["minimum_evidence_unlock_map"]]
    questions = [row["question"] for row in m14["next_best_questions"]]
    assert len(evidence_items) <= 10
    assert len(evidence_items) == len(set(evidence_items))
    assert "Verified GFA / rentable area" not in evidence_items
    assert not any("bounded asset with its own area" in question for question in questions)
    assert m14["financial_exposure_register"]

    actions = {row["decision_front"]: row for row in m33["tad_preliminary"]["decision_front_actions"]}
    assert actions["Compliance investment"]["current_status"] == "VALIDATE FIRST"
    assert actions["Compliance investment"]["variable_bottleneck"] == "compliance_filing"
    assert actions["Seller / operator evidence request"]["current_status"] == "ACT NOW"

    m25 = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_022": {"__stub__": True},
            "motor_034": m34,
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": inputs["motor_007"]["allowed_report_classes"],
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "recommended_report_type": "Decision-Blocked Asset Brief",
                    "report_readiness_allowed": m34["report_readiness_register"]["report_type_allowed"],
                    "report_readiness_prohibited": m34["report_readiness_register"]["report_type_prohibited"],
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )
    assert m25["recommended_report_type"] == "Compliance / Investment Screening Brief"
    assert m25["report_type_trace"]["early_report_type_gate"] == "Decision-Blocked Asset Brief"
    assert m25["report_type_trace"]["final_published_report_type"] == "Compliance / Investment Screening Brief"


def test_one_vanderbilt_decision_core_uses_canonical_context_for_screening_state():
    inputs = _build_screening_case_inputs()
    m34 = Motor034Adapter().run(inputs)
    facility_prior = deepcopy(inputs["motor_012"]["facility_prior"])
    facility_prior["canonical_asset_context_summary"] = m34["canonical_asset_context_summary"]
    m13 = Motor013Adapter().run(
        {
            "motor_012": {"facility_prior": facility_prior},
            "motor_007": inputs["motor_007"],
        }
    )
    m14 = Motor014Adapter().run(
        {
            "motor_001": inputs.get("motor_001", {}),
            "motor_007": inputs["motor_007"],
            "motor_012": {"facility_prior": facility_prior},
            "motor_013": m13,
            "motor_034": m34,
        }
    )

    assert m14["composite_reading"]["decision_state"].startswith("EPISTEMIC STATE: SCREENING ADMISSIBLE")
    questions = [row["question"] for row in m14["next_best_questions"]]
    assert not any("bounded asset with its own area" in question for question in questions)


def test_wilsonart_expected_behavior_stays_blocked_but_graduates_tad_and_industrial_evidence_requests():
    inputs = _build_wilsonart_case_inputs()
    m34, m14, m33 = _run_decision_chain(inputs)

    assert m34["report_readiness_register"]["report_type_allowed"] == ["Decision-Blocked Asset Brief"]
    assert _find_claim(m34, "process_change_hypothesis_claim")["current_permission"] in {"allowed", "conditional"}
    assert _find_claim(m34, "process_redesign_recommendation_claim")["current_permission"] == "prohibited"
    assert _find_claim(m34, "roi_range_claim")["current_permission"] == "prohibited"

    evidence_items = [row["evidence_item"] for row in m14["minimum_evidence_unlock_map"]]
    assert any("process" in item.lower() and "inventory" in item.lower() for item in evidence_items)
    assert m14["financial_exposure_register"]

    actions = {row["decision_front"]: row for row in m33["tad_preliminary"]["decision_front_actions"]}
    assert actions["Operator evidence request"]["current_status"] == "ACT NOW"
    assert actions["Environmental or permit-driven investment"]["current_status"] == "VALIDATE FIRST"
    assert actions["Process efficiency or utility-support CAPEX"]["current_status"] == "DEFER"
    assert actions["Process redesign"]["current_status"] == "NO-GO"
    assert "process-redesign recommendation" in actions["Process redesign"]["prohibited_action"].lower()

    m25 = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_022": {"__stub__": True},
            "motor_034": m34,
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": inputs["motor_007"]["allowed_report_classes"],
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "recommended_report_type": "Decision-Blocked Asset Brief",
                    "report_readiness_allowed": m34["report_readiness_register"]["report_type_allowed"],
                    "report_readiness_prohibited": m34["report_readiness_register"]["report_type_prohibited"],
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )
    assert m25["recommended_report_type"] == "Decision-Blocked Asset Brief"
    assert m25["report_type_trace"]["early_report_type_gate"] == "Decision-Blocked Asset Brief"
    assert m25["report_type_trace"]["final_published_report_type"] == "Decision-Blocked Asset Brief"


def test_hq_expected_behavior_stays_nontechnical_and_blocks_asset_report():
    out = Motor034Adapter().run(
        {
            "motor_001": {},
            "motor_007": {
                "target_definition_contract": {
                    "address_raw": "PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
                    "jurisdiction_scope": ["US-CA-SF"],
                    "target_type": "warehouse_distribution",
                },
                "target_classification_object": {
                    "target_type": "CORPORATE_HEADQUARTERS",
                    "classification_confidence": "high",
                },
                "technical_substrate_readiness": "insufficient",
                "recommended_report_type": "Entity Address Classification Brief",
            },
            "motor_008": {},
            "motor_010": {},
            "motor_011": {},
            "motor_012": {
                "asset_field_register": [],
                "missing_evidence_register": [],
                "compliance_applicability_case": {},
            },
            "motor_028": {"source_register": [], "dataset_coverage_register": []},
        }
    )

    assert out["report_readiness_register"]["report_type_allowed"] == ["Entity Address Classification Brief"]
    assert "Full Technical Decision Intelligence Report" in out["report_readiness_register"]["report_type_prohibited"]

    m25 = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_022": {"__stub__": True},
            "motor_034": out,
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "target_admissibility_state": "address_candidate_only",
                    "allowed_report_classes": ["Address Candidate Brief", "Entity Address Classification Brief"],
                    "report_identity_state": "Address Candidate Brief",
                    "recommended_report_type": "Entity Address Classification Brief",
                    "report_readiness_allowed": out["report_readiness_register"]["report_type_allowed"],
                    "report_readiness_prohibited": out["report_readiness_register"]["report_type_prohibited"],
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )
    assert m25["report_type_trace"]["early_report_type_gate"] == "Entity Address Classification Brief"
    assert m25["report_type_trace"]["final_published_report_type"] == "Entity Address Classification Brief"
