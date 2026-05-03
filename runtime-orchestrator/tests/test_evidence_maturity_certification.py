from __future__ import annotations

from runtime_orchestrator.adapters.motor_012 import _build_compliance_applicability_case
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
        "source_id": source_id or f"cert::{field}",
        "scope": scope,
        "authority_score": authority_score,
        "recency": "current",
        "admissibility": admissibility,
        "notes": "",
    }


def _base_inputs(
    asset_fields: list[dict],
    *,
    target_type: str = "OPERATING_ASSET",
    technical_substrate_readiness: str = "partial",
    recommended_report_type: str = "Decision-Blocked Asset Brief",
) -> dict:
    observed_gfa = next(
        (
            row["value"]
            for row in asset_fields
            if row["field"] == "GFA" and row["status"] == "OBSERVED"
        ),
        "",
    )
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "address_raw": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                "jurisdiction_scope": ["US-NY-NYC"],
                "target_type": "commercial_building",
            },
            "target_classification_object": {
                "target_type": target_type,
                "classification_confidence": "high",
            },
            "technical_substrate_readiness": technical_substrate_readiness,
            "recommended_report_type": recommended_report_type,
        },
        "motor_008": {},
        "motor_010": {},
        "motor_011": {},
        "motor_012": {
            "asset_field_register": asset_fields,
            "missing_evidence_register": [],
            "compliance_applicability_case": {
                "rule_family_record": [{"rule_family_name": "NYC Local Law 97"}],
                "trigger_field_register": [
                    {"field_name": "jurisdiction_codes", "field_state": "observed"},
                    {"field_name": "GFA_sqft", "field_state": "observed" if observed_gfa else "missing"},
                ],
                "applicability_state": "trigger_partially_supported",
                "compliance_posture_state": "trigger_plausible",
                "screening_basis_register": [
                    {
                        "basis_name": "regulated_floor_area_basis",
                        "basis_value": observed_gfa,
                        "basis_unit": "sqft",
                    },
                    {
                        "basis_name": "ll97_compliance_period",
                        "basis_value": "2024-2029",
                        "basis_unit": "",
                    },
                    {
                        "basis_name": "ll97_penalty_rate",
                        "basis_value": 268,
                        "basis_unit": "USD_per_metric_ton_CO2e",
                    },
                ]
                if observed_gfa
                else [],
            },
        },
        "motor_028": {
            "source_register": [],
            "dataset_coverage_register": [],
        },
    }


def _find_variable(output: dict, variable_name: str) -> dict:
    return next(row for row in output["variable_maturity_register"] if row["variable_name"] == variable_name)


def _find_claim(output: dict, claim_name: str) -> dict:
    return next(row for row in output["claim_permission_register"] if row["claim_name"] == claim_name)


def test_certification_nyc_with_ll84_supports_screening_and_numeric_eui():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", source_id="nyc_dof_property_record::ova"),
            _field("asset_class", "commercial_building", source_id="nyc_pluto_property::ova"),
            _field("GFA", "1678135", source_id="nyc_pluto_property::ova"),
            _field("current_EUI", "120.5", source_id="nyc_ll84_energy_benchmarking::ova"),
            _field("emissions", "16184.23", source_id="nyc_ll84_energy_benchmarking::ova"),
            _field("compliance_filings", "LL84 public benchmarking disclosure observed (2024)", source_id="nyc_ll84_energy_benchmarking::ova"),
        ]
    )
    inputs["motor_028"]["dataset_coverage_register"] = [
        {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
        {"dataset_key": "nyc_ll84_benchmarking", "status": "accepted", "field_coverage": ["EUI", "emissions"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
        {"dataset_key": "nyc_ll97_emissions", "status": "screened", "field_coverage": ["penalty_rate", "compliance_period"], "notes": "", "matched_sources": ["nyc_ll84_energy_benchmarking"]},
    ]
    out = adapter.run(inputs)
    assert _find_variable(out, "GFA")["maturity_level"] == 3
    assert _find_variable(out, "EUI")["maturity_level"] == 3
    assert _find_variable(out, "emissions")["maturity_level"] == 3
    assert _find_claim(out, "numeric_eui_claim")["current_permission"] in {"allowed", "conditional"}
    assert _find_claim(out, "compliance_screening_claim")["current_permission"] in {"allowed", "conditional"}


def test_certification_nyc_without_ll84_stays_bounded_and_blocks_savings_claim():
    adapter = Motor034Adapter()
    inputs = _base_inputs(
        [
            _field("address", "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017", source_id="nyc_dof_property_record::ova"),
            _field("asset_class", "commercial_building", source_id="nyc_pluto_property::ova"),
            _field("GFA", "1678135", source_id="nyc_pluto_property::ova"),
        ],
        technical_substrate_readiness="partial",
    )
    inputs["motor_028"]["dataset_coverage_register"] = [
        {"dataset_key": "nyc_pluto", "status": "accepted", "field_coverage": ["GFA"], "notes": "", "matched_sources": ["nyc_pluto_property"]},
        {"dataset_key": "nyc_ll84_benchmarking", "status": "no_data", "field_coverage": [], "notes": "", "matched_sources": []},
    ]
    out = adapter.run(inputs)
    assert _find_variable(out, "GFA")["maturity_level"] == 3
    assert _find_variable(out, "EUI")["maturity_level"] == 0
    assert _find_claim(out, "energy_savings_claim")["current_permission"] == "prohibited"
    assert "Full Technical Decision Intelligence Report" in out["report_readiness_register"]["report_type_prohibited"]


def test_certification_hq_routes_to_entity_address_classification_brief():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [],
            target_type="CORPORATE_HEADQUARTERS",
            technical_substrate_readiness="insufficient",
            recommended_report_type="Entity Address Classification Brief",
        )
    )
    assert out["report_readiness_register"]["report_type_allowed"] == ["Entity Address Classification Brief"]
    assert "Full Technical Decision Intelligence Report" in out["report_readiness_register"]["report_type_prohibited"]


def test_certification_ambiguous_routes_to_target_clarification_brief():
    adapter = Motor034Adapter()
    out = adapter.run(
        _base_inputs(
            [],
            target_type="AMBIGUOUS_TARGET",
            technical_substrate_readiness="insufficient",
            recommended_report_type="Target Clarification Brief",
        )
    )
    assert out["report_readiness_register"]["report_type_allowed"] == ["Target Clarification Brief"]
    assert "Full Technical Decision Intelligence Report" in out["report_readiness_register"]["report_type_prohibited"]


def test_ll97_public_guidance_hardens_upgrade_path_without_implying_public_filing_registry():
    case = _build_compliance_applicability_case(
        fi={"input_05_size": {"GFA_sqft": 1678135}},
        regulatory_context={
            "GFA_sqft": 1678135,
            "primary_regulation": "NYC_Local_Law_97_2019",
            "secondary_regulations": [],
            "jurisdiction_codes": ["US-NY-NYC"],
            "regulatory_flags": [],
            "landmark_status": "",
            "data_provenance": "nyc_ll97_screening",
        },
        jurisdiction_bundle={"data_provenance": "nyc_jurisdiction_bundle"},
        improvement_constraint={"regulatory_constraints": [], "data_provenance": "improvement_constraints"},
        target_definition={"target_type": "commercial_building"},
        enriched={
            "ll97_cbl_covered_buildings_list": {},
            "ll97_cbl_record": {},
            "ll97_filing_guidance": {
                "official_urls": ["https://www.nyc.gov/assets/buildings/pdf/article320_simple.pdf"],
                "public_filing_registry_available": False,
            },
        },
    )
    assert case["public_filing_registry_state"] == "not_publicly_observed"
    assert any(
        row["basis_name"] == "ll97_filing_process_guidance"
        for row in case["screening_basis_register"]
    )
    assert any(
        "No public building-level LL97 filing registry was observed" in requirement
        for requirement in case["hardening_requirements"]
    )
