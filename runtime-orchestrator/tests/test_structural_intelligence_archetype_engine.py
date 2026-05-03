from __future__ import annotations

from runtime_orchestrator.adapters.motor_039 import Motor039Adapter


def _field(field: str, value: str, *, source_id: str = "test::field") -> dict:
    return {
        "field": field,
        "value": value,
        "status": "OBSERVED",
        "scope": "ASSET_LEVEL",
        "authority_score": "high",
        "admissibility": "CONFIRMED_ASSET_LEVEL",
        "source_id": source_id,
        "notes": "",
    }


def _base_inputs(*, target_type: str, asset_name: str, jurisdiction_scope: list[str], target_classification: str = "OPERATING_ASSET") -> dict:
    return {
        "motor_001": {},
        "motor_007": {
            "target_definition_contract": {
                "target_type": target_type,
                "target_name": asset_name,
                "jurisdiction_scope": jurisdiction_scope,
            },
            "target_classification_object": {
                "target_type": target_classification,
                "classification_confidence": "high",
            },
        },
        "motor_012": {
            "facility_prior": {
                "asset_name": asset_name,
                "target_definition": {
                    "target_type": target_type,
                    "target_name": asset_name,
                    "jurisdiction_scope": jurisdiction_scope,
                },
            },
            "asset_field_register": [],
            "dataset_coverage_register": [],
        },
        "motor_028": {"source_register": []},
    }


def test_motor_039_selects_nyc_office_tower_archetype_from_public_signals():
    adapter = Motor039Adapter()
    inputs = _base_inputs(
        target_type="commercial_building",
        asset_name="One Vanderbilt",
        jurisdiction_scope=["US-NY-NYC"],
    )
    inputs["motor_012"]["asset_field_register"] = [
        _field("GFA", "1700000", source_id="nyc_pluto::one-vanderbilt"),
        _field("floor_count", "73", source_id="nyc_pluto::one-vanderbilt"),
        _field("current_EUI", "72.1", source_id="nyc_ll84::one-vanderbilt"),
    ]
    inputs["motor_012"]["dataset_coverage_register"] = [
        {"dataset_key": "nyc_pluto_property", "status": "accepted"},
        {"dataset_key": "nyc_ll84_energy_benchmarking", "status": "accepted"},
    ]
    inputs["motor_028"]["source_register"] = [
        {"source_type": "nyc_pluto_property", "accepted": True},
        {"source_type": "nyc_ll84_energy_benchmarking", "accepted": True},
    ]

    out = adapter.run(inputs)

    assert out["selected_archetype_id"] == "commercial_office_tower_nyc"
    assert out["match_confidence"] == "high"
    assert any(row["variable"] == "central_plant" for row in out["dominant_variable_hypotheses"])
    assert all(row["evidence_state"] == "ARCHETYPAL_PRIOR" for row in out["dominant_variable_hypotheses"])


def test_motor_039_selects_manufacturing_laminate_when_process_clues_are_observed():
    adapter = Motor039Adapter()
    inputs = _base_inputs(
        target_type="manufacturing_facility",
        asset_name="Wilsonart Temple North Laminate Facility",
        jurisdiction_scope=["US-TX"],
    )
    inputs["motor_012"]["asset_field_register"] = [
        _field("process_flow", "Public process description for laminate production", source_id="company_facility_page::wilsonart"),
        _field("load_driver", "Laminate pressing and curing duty", source_id="company_facility_page::wilsonart"),
        _field("operating_schedule", "proxy: multi-shift manufacturing operations", source_id="company_facility_page::wilsonart"),
    ]
    inputs["motor_012"]["dataset_coverage_register"] = [
        {"dataset_key": "tceq_permits_and_emissions", "status": "accepted"},
    ]
    inputs["motor_028"]["source_register"] = [
        {"source_type": "tceq_air_permit", "accepted": True},
        {"source_type": "epa_echo", "accepted": True},
    ]

    out = adapter.run(inputs)

    assert out["selected_archetype_id"] == "manufacturing_laminate"
    assert out["match_confidence"] == "high"
    assert any(row["variable"] == "resin_curing_profile" for row in out["dominant_variable_hypotheses"])
    assert all(row["evidence_state"] == "ARCHETYPAL_PRIOR" for row in out["dominant_variable_hypotheses"])


def test_motor_039_degrades_non_operating_targets_to_not_modelable_yet():
    adapter = Motor039Adapter()
    inputs = _base_inputs(
        target_type="warehouse_distribution",
        asset_name="PLD Corporate HQ",
        jurisdiction_scope=["US-CA-SF"],
        target_classification="CORPORATE_HEADQUARTERS",
    )

    out = adapter.run(inputs)

    assert out["selected_archetype_id"] == "target_not_yet_structurally_modelable"
    assert out["dominant_variable_count"] == 0
    assert out["anti_hallucination_contract"]["selected_archetype_evidence_state"] == "INADMISSIBLE_CLAIM"


def test_motor_039_selects_generic_logistics_warehouse_archetype_for_operating_asset():
    adapter = Motor039Adapter()
    inputs = _base_inputs(
        target_type="warehouse_distribution",
        asset_name="Sunrise Logistics Hub",
        jurisdiction_scope=["US-IL"],
    )

    out = adapter.run(inputs)

    assert out["selected_archetype_id"] == "logistics_warehouse_generic"
    assert out["match_confidence"] == "medium"
    assert any(row["variable"] == "service_level_complexity" for row in out["dominant_variable_hypotheses"])
    assert out["anti_hallucination_contract"]["selected_archetype_evidence_state"] == "ARCHETYPAL_PRIOR"


def test_motor_039_selects_generic_cold_chain_archetype_for_operating_asset():
    adapter = Motor039Adapter()
    inputs = _base_inputs(
        target_type="cold_chain_facility",
        asset_name="Lakeshore Cold Storage Campus",
        jurisdiction_scope=["US-IL"],
    )

    out = adapter.run(inputs)

    assert out["selected_archetype_id"] == "cold_chain_generic"
    assert out["match_confidence"] == "medium"
    assert any(row["variable"] == "refrigeration_duty" for row in out["dominant_variable_hypotheses"])
    assert out["anti_hallucination_contract"]["selected_archetype_evidence_state"] == "ARCHETYPAL_PRIOR"


def test_motor_039_selects_utility_heavy_archetype_when_industrial_plant_has_explicit_support_utility_clues():
    adapter = Motor039Adapter()
    inputs = _base_inputs(
        target_type="industrial_plant",
        asset_name="Prairie Central Utility Island",
        jurisdiction_scope=["US-TX"],
    )
    inputs["motor_012"]["asset_field_register"] = [
        _field("asset_category", "central utility island"),
        _field("major_equipment", "large motors and drives, compressor trains, cooling water pumps"),
        _field("tariff_signal", "power factor and reactive-charge exposure"),
    ]

    out = adapter.run(inputs)

    assert out["selected_archetype_id"] == "utility_heavy_site_generic"
    assert out["match_confidence"] == "high"
    assert any(row["variable"] == "demand_structure" for row in out["dominant_variable_hypotheses"])
    assert out["anti_hallucination_contract"]["selected_archetype_evidence_state"] == "ARCHETYPAL_PRIOR"
