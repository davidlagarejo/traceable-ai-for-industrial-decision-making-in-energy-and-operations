"""Tests for runtime_orchestrator.layer_registry.

Cubre:
  - cada motor del catálogo (motor_dependencies.json) tiene una entrada
    en MOTOR_LAYER_MAP (forzando clasificación explícita)
  - layer_of devuelve el LayerId esperado para una muestra representativa
  - layer_of lanza KeyError para motor desconocido
  - motors_in_layer devuelve solo motores de esa capa
  - el conjunto unión de capas + None == catálogo completo
"""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from runtime_orchestrator.layer_bundle import LayerBundle
from runtime_orchestrator.layer_registry import (
    MOTOR_LAYER_MAP,
    layer_of,
    motors_in_layer,
    visible_bundles_for,
)


def _bundle(layer, produced_by, payload=None):
    return LayerBundle.make(
        layer_id=layer,
        bundle_version="1.0.0",
        produced_by=produced_by,
        produced_at="2026-05-08T00:00:00+00:00",
        payload=payload or {},
    )


_MOTOR_DEPENDENCIES_JSON = (
    Path(__file__).resolve().parents[2]
    / "governanza"
    / "automation-base"
    / "motor_dependencies.json"
)


def _catalog_motor_ids() -> set[str]:
    data = json.loads(_MOTOR_DEPENDENCIES_JSON.read_text(encoding="utf-8"))
    return set(data["motors"].keys())


def test_every_catalog_motor_has_a_layer_entry():
    catalog = _catalog_motor_ids()
    registered = set(MOTOR_LAYER_MAP.keys())
    missing = catalog - registered
    assert not missing, (
        f"motors in catalog without layer assignment: {sorted(missing)}. "
        "Update layer_registry.py."
    )


def test_no_extraneous_motor_in_registry():
    catalog = _catalog_motor_ids()
    registered = set(MOTOR_LAYER_MAP.keys())
    extra = registered - catalog
    assert not extra, (
        f"motors registered but not in catalog: {sorted(extra)}. "
        "Either remove from layer_registry.py or add to motor_dependencies.json."
    )


@pytest.mark.parametrize(
    "motor_id,expected_layer",
    [
        ("motor_011", "A"),  # Library Curation
        ("motor_039", "A"),  # Archetype Library Resolver
        ("motor_041", "B"),  # Problem Framing
        ("motor_038", "B"),  # Dominant Variable
        ("motor_034", "C"),  # Evidence Maturity & Claim Permission
        ("motor_054", "C"),  # Congruence Strategic Insight & Claim Governor
        ("motor_033", "D"),  # TAD Preliminary Prioritization
        ("motor_045", "D"),  # Financial Exposure Under Uncertainty
        ("motor_016", "E"),  # Report Package Assembly
        ("motor_047", "E"),  # Executive Synthesis
        ("motor_036", "F"),  # System Consistency Validator
        ("motor_040", "F"),  # Cross-Layer Conflict
    ],
)
def test_layer_of_known_motors(motor_id, expected_layer):
    assert layer_of(motor_id) == expected_layer


@pytest.mark.parametrize(
    "motor_id",
    [
        "motor_001",  # Phase Contract Registry (infra)
        "motor_004",  # Ingestion (ingesta)
        "motor_014",  # Decision Core (soporte)
        "motor_023",  # Pipeline Orchestration (infra)
    ],
)
def test_unassigned_motors_return_none(motor_id):
    assert layer_of(motor_id) is None


def test_layer_of_unknown_motor_raises():
    with pytest.raises(KeyError):
        layer_of("motor_999")


def test_motors_in_layer_a_contains_archetype_resolver():
    assert "motor_039" in motors_in_layer("A")


def test_motors_in_layer_c_contains_claim_governors():
    layer_c = motors_in_layer("C")
    assert "motor_034" in layer_c
    assert "motor_054" in layer_c
    assert "motor_025" in layer_c


def test_visible_bundles_for_filters_by_strict_predecessor():
    """Un motor de capa C solo ve bundles de A y B, no de C/D/E/F."""
    bundles = {
        "motor_011": _bundle("A", "motor_011"),
        "motor_041": _bundle("B", "motor_041"),
        "motor_054": _bundle("C", "motor_054"),
        "motor_033": _bundle("D", "motor_033"),
    }
    # motor_034 está en capa C, ve solo A y B (estrictamente anteriores)
    visible = visible_bundles_for("motor_034", bundles)
    assert set(visible.keys()) == {"motor_011", "motor_041"}


def test_visible_bundles_for_layer_a_consumer_sees_nothing():
    """Un motor de capa A no tiene predecesores."""
    bundles = {
        "motor_011": _bundle("A", "motor_011"),
        "motor_041": _bundle("B", "motor_041"),
    }
    # motor_039 está en capa A
    visible = visible_bundles_for("motor_039", bundles)
    assert visible == {}


def test_visible_bundles_for_layer_f_consumer_sees_all_predecessors():
    """Un motor de capa F ve A, B, C, D, E."""
    bundles = {
        "motor_011": _bundle("A", "motor_011"),
        "motor_041": _bundle("B", "motor_041"),
        "motor_054": _bundle("C", "motor_054"),
        "motor_033": _bundle("D", "motor_033"),
        "motor_016": _bundle("E", "motor_016"),
    }
    # motor_036 está en capa F
    visible = visible_bundles_for("motor_036", bundles)
    assert set(visible.keys()) == {"motor_011", "motor_041", "motor_054", "motor_033", "motor_016"}


def test_visible_bundles_for_unassigned_consumer_returns_empty():
    """Un motor sin capa (infra/ingest) no participa del bus."""
    bundles = {"motor_011": _bundle("A", "motor_011")}
    # motor_001 está en None (infra)
    assert visible_bundles_for("motor_001", bundles) == {}


def test_visible_bundles_for_unknown_consumer_raises():
    with pytest.raises(KeyError):
        visible_bundles_for("motor_999", {})


def test_visible_bundles_for_does_not_mutate_input():
    bundles = {
        "motor_011": _bundle("A", "motor_011"),
        "motor_041": _bundle("B", "motor_041"),
    }
    snapshot = dict(bundles)
    visible_bundles_for("motor_034", bundles)
    assert bundles == snapshot
    # El dict devuelto es independiente
    assert visible_bundles_for("motor_034", bundles) is not bundles


def test_layer_partition_is_disjoint_and_complete():
    """Cada motor está en exactamente una capa (o en None) — no hay duplicados."""
    catalog = _catalog_motor_ids()
    seen: dict[str, str | None] = {}
    for motor_id, layer in MOTOR_LAYER_MAP.items():
        seen[motor_id] = layer
    assert set(seen) == catalog
    # Conteos coherentes con el plan §3.3
    assert len(motors_in_layer("A")) >= 3
    assert len(motors_in_layer("E")) >= 5
