"""Tests for motor_007 evidence-token derivation (V2-LIVE Item 2).

motor_061 admits justified hybrids (cold_chain + food_processing, mixed-
temperature DC, office + edge_datacenter, etc.) only when the right
trigger tokens are present in evidence. motor_007 must derive those
tokens from the case inputs and emit them through
target_definition_contract.facility_evidence_tokens / process_evidence_tokens.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_007 import derive_evidence_tokens


def test_no_inputs_returns_empty_tokens():
    f, p = derive_evidence_tokens({}, {}, {})
    assert f == []
    assert p == []


def test_passthrough_declared_facility_tokens():
    f, p = derive_evidence_tokens(
        target_definition={"facility_evidence_tokens": ["cook_chill_present"]},
        observable_clusters={},
        facility_inputs={},
    )
    assert "cook_chill_present" in f


def test_passthrough_declared_process_tokens():
    f, p = derive_evidence_tokens(
        target_definition={"process_evidence_tokens": ["sanitation_steam_present"]},
        observable_clusters={},
        facility_inputs={},
    )
    assert "sanitation_steam_present" in p


def test_passthrough_legacy_hybrid_evidence_tokens_to_facility():
    f, p = derive_evidence_tokens(
        target_definition={"hybrid_evidence_tokens": ["edge_dc_tenant_present"]},
        observable_clusters={},
        facility_inputs={},
    )
    assert "edge_dc_tenant_present" in f


def test_detects_cold_chain_signals_from_facility_inputs():
    f, p = derive_evidence_tokens(
        target_definition={},
        observable_clusters={},
        facility_inputs={
            "input_04_primary_use": {"uses": ["Frozen storage", "Chilled storage"]},
            "input_09_known_systems": {"known_systems": ["ammonia refrigeration plant"]},
        },
    )
    # "Frozen storage" → frozen_zone_present
    # "Chilled storage" → refrigerated_zone_present
    assert "frozen_zone_present" in f
    assert "refrigerated_zone_present" in f


def test_detects_cook_chill_and_dairy_in_input_text():
    f, p = derive_evidence_tokens(
        target_definition={},
        observable_clusters={},
        facility_inputs={
            "input_02_facility_type": {"asset_category": "Dairy processing plant with cook chill line"},
        },
    )
    assert "cook_chill_present" in f
    assert "dairy_processing_evidence" in f


def test_detects_process_heat_in_observable_clusters():
    f, p = derive_evidence_tokens(
        target_definition={},
        observable_clusters={"thermal_systems_cluster": ["process heat boiler", "thermal oil loop"]},
        facility_inputs={},
    )
    assert "process_heat_signature" in p


def test_detects_edge_datacenter_in_target_definition():
    f, p = derive_evidence_tokens(
        target_definition={"description": "Class A office with edge data center tenant on floor 12"},
        observable_clusters={},
        facility_inputs={},
    )
    assert "edge_dc_tenant_present" in f


def test_no_false_positive_on_unrelated_text():
    f, p = derive_evidence_tokens(
        target_definition={"target_name": "Acme Logistics Center"},
        observable_clusters={"misc": ["nothing here"]},
        facility_inputs={"input_04_primary_use": {"uses": ["Dry storage"]}},
    )
    assert f == []
    assert p == []


def test_deduplicates_when_declared_and_detected_overlap():
    f, p = derive_evidence_tokens(
        target_definition={
            "facility_evidence_tokens": ["frozen_zone_present"],
            "description": "frozen storage facility",
        },
        observable_clusters={},
        facility_inputs={},
    )
    assert f.count("frozen_zone_present") == 1


def test_case_insensitive_detection():
    f, p = derive_evidence_tokens(
        target_definition={},
        observable_clusters={},
        facility_inputs={"input_02_facility_type": {"asset_category": "BLAST FREEZER FACILITY"}},
    )
    assert "blast_freezer_with_cook_line" in f


def test_tokens_returned_sorted_for_determinism():
    f, p = derive_evidence_tokens(
        target_definition={},
        observable_clusters={},
        facility_inputs={
            "input_02_facility_type": {
                "asset_category": "Multi-temperature DC with frozen storage and refrigerated zones",
            },
        },
    )
    # The detected portion must be deterministic across runs
    detected_only = sorted(set(f) - set([]))
    assert detected_only == f  # Already sorted (only detection, no declared)


def test_manufacturing_with_attached_dc_signals():
    f, p = derive_evidence_tokens(
        target_definition={},
        observable_clusters={},
        facility_inputs={
            "input_02_facility_type": {"asset_category": "Furniture plant with attached distribution center"},
            "input_09_known_systems": {"known_systems": ["finished goods warehouse", "high bay storage"]},
        },
    )
    assert "attached_distribution_center" in f
    assert "finished_goods_dc_evidence" in f
    assert "high_bay_storage_volume_dominant" in f
