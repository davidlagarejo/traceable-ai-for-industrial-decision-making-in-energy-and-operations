"""Tests for the LayerBundle population helpers in pipeline_orchestrator.

Cubre:
  - _populate_layer_bundles auto-construye bundles para motores con capa
  - motores sin capa (None) son skipeados
  - motores no presentes en outputs son skipeados sin error
  - el bundle resultante tiene la layer correcta y un content_hash estable
  - _stable_inputs_for_hash neutraliza produced_at / produced_by (cache-safe)
"""
from __future__ import annotations

from runtime_orchestrator.pipeline_orchestrator import (
    _populate_layer_bundles,
    _publish_inferred_state_bundle,
    _stable_inputs_for_hash,
)


def test_populate_creates_bundle_for_motor_with_layer():
    outputs = {
        "motor_011": {"foo": "bar"},  # Layer A
        "__bundles__": {},
    }
    _populate_layer_bundles(outputs, level=["motor_011"])
    assert "motor_011" in outputs["__bundles__"]
    bundle = outputs["__bundles__"]["motor_011"]
    assert bundle["layer_id"] == "A"
    assert bundle["produced_by"] == "motor_011"
    assert bundle["payload"] == {"foo": "bar"}
    assert len(bundle["content_hash"]) == 16


def test_populate_skips_motors_without_layer():
    outputs = {
        "motor_001": {"infra": True},  # layer=None (infra)
        "motor_011": {"data": True},  # Layer A
        "__bundles__": {},
    }
    _populate_layer_bundles(outputs, level=["motor_001", "motor_011"])
    assert "motor_011" in outputs["__bundles__"]
    assert "motor_001" not in outputs["__bundles__"]


def test_populate_skips_motors_with_empty_or_missing_output():
    outputs = {
        "motor_011": {},  # empty output
        "__bundles__": {},
    }
    _populate_layer_bundles(outputs, level=["motor_011", "motor_039"])
    # Empty output is skipped; missing output is skipped silently
    assert outputs["__bundles__"] == {}


def test_populate_creates_bundles_section_if_missing():
    outputs = {"motor_011": {"x": 1}}  # no __bundles__ key
    _populate_layer_bundles(outputs, level=["motor_011"])
    assert "__bundles__" in outputs
    assert "motor_011" in outputs["__bundles__"]


def test_populate_overwrites_existing_bundle_for_same_motor():
    outputs = {
        "motor_011": {"version": 2},
        "__bundles__": {
            "motor_011": {
                "layer_id": "A",
                "bundle_version": "1.0.0",
                "produced_by": "motor_011",
                "produced_at": "old",
                "payload": {"version": 1},
                "content_hash": "old_hash_xxxxxxx",
            }
        },
    }
    _populate_layer_bundles(outputs, level=["motor_011"])
    bundle = outputs["__bundles__"]["motor_011"]
    assert bundle["payload"] == {"version": 2}
    assert bundle["content_hash"] != "old_hash_xxxxxxx"


def test_populate_assigns_correct_layer_for_known_motors():
    outputs = {
        "motor_011": {"a": 1},  # Layer A
        "motor_041": {"b": 2},  # Layer B
        "motor_054": {"c": 3},  # Layer C
        "motor_033": {"d": 4},  # Layer D
        "motor_016": {"e": 5},  # Layer E
        "motor_036": {"f": 6},  # Layer F
        "__bundles__": {},
    }
    _populate_layer_bundles(
        outputs,
        level=["motor_011", "motor_041", "motor_054", "motor_033", "motor_016", "motor_036"],
    )
    assert outputs["__bundles__"]["motor_011"]["layer_id"] == "A"
    assert outputs["__bundles__"]["motor_041"]["layer_id"] == "B"
    assert outputs["__bundles__"]["motor_054"]["layer_id"] == "C"
    assert outputs["__bundles__"]["motor_033"]["layer_id"] == "D"
    assert outputs["__bundles__"]["motor_016"]["layer_id"] == "E"
    assert outputs["__bundles__"]["motor_036"]["layer_id"] == "F"


def test_stable_inputs_for_hash_neutralizes_volatile_bundle_fields():
    """Two runs with same payload but different produced_at must hash identical."""
    inputs_a = {
        "__pipeline__": {"x": 1},
        "__bundles__": {
            "motor_011": {
                "layer_id": "A",
                "bundle_version": "1.0.0",
                "produced_by": "motor_011",
                "produced_at": "2026-05-08T10:00:00+00:00",
                "payload": {"data": 1},
                "content_hash": "deterministic_001",
            }
        },
    }
    inputs_b = {
        "__pipeline__": {"x": 1},
        "__bundles__": {
            "motor_011": {
                "layer_id": "A",
                "bundle_version": "1.0.0",
                "produced_by": "motor_011",
                "produced_at": "2026-05-08T20:00:00+00:00",  # different
                "payload": {"data": 1},
                "content_hash": "deterministic_001",
            }
        },
    }
    stable_a = _stable_inputs_for_hash(inputs_a)
    stable_b = _stable_inputs_for_hash(inputs_b)
    assert stable_a == stable_b


def test_stable_inputs_for_hash_distinguishes_different_payload_hashes():
    """Different content_hash must lead to different stable inputs."""
    inputs_a = {
        "__bundles__": {
            "motor_011": {
                "layer_id": "A",
                "bundle_version": "1.0.0",
                "produced_by": "motor_011",
                "produced_at": "2026-05-08T10:00:00+00:00",
                "payload": {"data": 1},
                "content_hash": "hash_one_xxxxxxx",
            }
        },
    }
    inputs_b = {
        "__bundles__": {
            "motor_011": {
                "layer_id": "A",
                "bundle_version": "1.0.0",
                "produced_by": "motor_011",
                "produced_at": "2026-05-08T10:00:00+00:00",
                "payload": {"data": 2},
                "content_hash": "hash_two_yyyyyyy",
            }
        },
    }
    stable_a = _stable_inputs_for_hash(inputs_a)
    stable_b = _stable_inputs_for_hash(inputs_b)
    assert stable_a != stable_b


def test_stable_inputs_for_hash_handles_missing_bundles_key():
    inputs = {"__pipeline__": {"x": 1}, "__runtime__": {}}
    out = _stable_inputs_for_hash(inputs)
    assert "__bundles__" not in out  # not introduced when absent


# ── Inferred-state bundle (god-object migration scaffolding, R-14b) ────────


def test_publish_inferred_state_bundle_creates_bus_entry():
    outputs = {}
    runtime_context = {
        "subject_definition": {"target_name": "X"},
        "target_admissibility_state": "address_candidate_only",
        "asset_context_readiness": "asset_context_minimal",
        "recommended_report_type": "Exploratory Prior Brief",
    }
    _publish_inferred_state_bundle(outputs, runtime_context)
    assert "pipeline_run.inferred_state" in outputs["__bundles__"]


def test_inferred_state_bundle_has_layer_a_and_pipeline_run_producer():
    outputs = {}
    runtime_context = {"subject_definition": {"a": 1}}
    _publish_inferred_state_bundle(outputs, runtime_context)
    bundle = outputs["__bundles__"]["pipeline_run.inferred_state"]
    assert bundle["layer_id"] == "A"
    assert bundle["produced_by"] == "pipeline_run.inferred_state"


def test_inferred_state_bundle_payload_includes_known_keys():
    outputs = {}
    runtime_context = {
        "subject_definition": {"target_name": "X"},
        "target_admissibility_state": "address_candidate_only",
        "asset_context_readiness": "asset_context_minimal",
        "recommended_report_type": "Exploratory Prior Brief",
        "prohibited_report_types": ["Full Technical Decision Intelligence Report"],
        "report_identity_state": "Exploratory Prior Brief",
        "dominant_evidence_scope": "asset",
        "missing_observable_clusters": ["geometry_size_cluster"],
    }
    _publish_inferred_state_bundle(outputs, runtime_context)
    payload = outputs["__bundles__"]["pipeline_run.inferred_state"]["payload"]
    assert payload["subject_definition"] == {"target_name": "X"}
    assert payload["target_admissibility_state"] == "address_candidate_only"
    assert payload["asset_context_readiness"] == "asset_context_minimal"
    assert payload["recommended_report_type"] == "Exploratory Prior Brief"
    assert payload["missing_observable_clusters"] == ["geometry_size_cluster"]


def test_inferred_state_bundle_payload_keys_are_present_even_when_runtime_lacks_them():
    """Payload includes a stable key set, with None values for unset keys."""
    outputs = {}
    _publish_inferred_state_bundle(outputs, {})
    payload = outputs["__bundles__"]["pipeline_run.inferred_state"]["payload"]
    # Stable schema: known keys are always present
    expected_keys = {
        "subject_definition",
        "target_admissibility_state",
        "asset_context_readiness",
        "recommended_report_type",
        "report_identity_state",
        "dominant_evidence_scope",
        "missing_observable_clusters",
    }
    assert expected_keys.issubset(set(payload.keys()))


def test_inferred_state_bundle_does_not_clobber_existing_bundles():
    outputs = {
        "__bundles__": {
            "motor_011": {"layer_id": "A", "produced_by": "motor_011", "payload": {}}
        }
    }
    _publish_inferred_state_bundle(outputs, {"subject_definition": {"x": 1}})
    assert "motor_011" in outputs["__bundles__"]
    assert "pipeline_run.inferred_state" in outputs["__bundles__"]
