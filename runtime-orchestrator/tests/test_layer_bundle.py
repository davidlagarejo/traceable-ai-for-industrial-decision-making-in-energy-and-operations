"""Tests for runtime_orchestrator.layer_bundle.

Cubre:
  - construcción via .make() con content_hash determinista
  - frozen dataclass (no mutación)
  - json roundtrip via to_dict / from_dict
  - layer ordering: A < B < C < D < E < F
  - validación de layer_id desconocido
"""
from __future__ import annotations

import dataclasses

import pytest

from runtime_orchestrator.layer_bundle import LAYER_ORDER, LayerBundle


def _sample_payload() -> dict:
    return {"hypothesis_id": "h1", "claim": "denominator may be wrong"}


def test_make_produces_deterministic_content_hash():
    payload = _sample_payload()
    bundle_a = LayerBundle.make(
        layer_id="B",
        bundle_version="1.0.0",
        produced_by="motor_041",
        produced_at="2026-05-08T00:00:00+00:00",
        payload=payload,
    )
    bundle_b = LayerBundle.make(
        layer_id="B",
        bundle_version="1.0.0",
        produced_by="motor_041",
        produced_at="2026-05-08T00:00:00+00:00",
        payload=dict(payload),
    )
    assert bundle_a.content_hash == bundle_b.content_hash
    assert len(bundle_a.content_hash) == 16


def test_make_changes_hash_when_payload_changes():
    base = LayerBundle.make(
        layer_id="B",
        bundle_version="1.0.0",
        produced_by="motor_041",
        produced_at="2026-05-08T00:00:00+00:00",
        payload={"a": 1},
    )
    other = LayerBundle.make(
        layer_id="B",
        bundle_version="1.0.0",
        produced_by="motor_041",
        produced_at="2026-05-08T00:00:00+00:00",
        payload={"a": 2},
    )
    assert base.content_hash != other.content_hash


def test_bundle_is_frozen():
    bundle = LayerBundle.make(
        layer_id="A",
        bundle_version="1.0.0",
        produced_by="motor_011",
        produced_at="2026-05-08T00:00:00+00:00",
        payload=_sample_payload(),
    )
    with pytest.raises(dataclasses.FrozenInstanceError):
        bundle.layer_id = "B"  # type: ignore[misc]


def test_to_dict_from_dict_roundtrip():
    original = LayerBundle.make(
        layer_id="C",
        bundle_version="2.1.0",
        produced_by="motor_054",
        produced_at="2026-05-08T12:00:00+00:00",
        payload={"epistemic_class": "archetypal_prior"},
    )
    restored = LayerBundle.from_dict(original.to_dict())
    assert restored == original


def test_layer_ordering_constant():
    assert LAYER_ORDER == ("A", "B", "C", "D", "E", "F")


def test_is_readable_from_enforces_strict_predecessor():
    bundle_a = LayerBundle.make(
        layer_id="A",
        bundle_version="1.0.0",
        produced_by="motor_011",
        produced_at="2026-05-08T00:00:00+00:00",
        payload={},
    )
    bundle_e = LayerBundle.make(
        layer_id="E",
        bundle_version="1.0.0",
        produced_by="motor_016",
        produced_at="2026-05-08T00:00:00+00:00",
        payload={},
    )
    # A es legible desde B, C, D, E, F (estrictamente posteriores)
    assert bundle_a.is_readable_from("B") is True
    assert bundle_a.is_readable_from("F") is True
    # A no es legible desde A (no es estrictamente anterior)
    assert bundle_a.is_readable_from("A") is False
    # E no es legible desde A, B, C, D
    assert bundle_e.is_readable_from("A") is False
    assert bundle_e.is_readable_from("D") is False
    # E no es legible desde E
    assert bundle_e.is_readable_from("E") is False
    # E es legible desde F
    assert bundle_e.is_readable_from("F") is True


def test_make_rejects_unknown_layer():
    with pytest.raises(ValueError):
        LayerBundle.make(
            layer_id="Z",  # type: ignore[arg-type]
            bundle_version="1.0.0",
            produced_by="motor_001",
            produced_at="2026-05-08T00:00:00+00:00",
            payload={},
        )


def test_make_rejects_non_dict_payload():
    with pytest.raises(TypeError):
        LayerBundle.make(
            layer_id="A",
            bundle_version="1.0.0",
            produced_by="motor_001",
            produced_at="2026-05-08T00:00:00+00:00",
            payload=["not a dict"],  # type: ignore[arg-type]
        )


def test_is_readable_from_rejects_unknown_consumer():
    bundle = LayerBundle.make(
        layer_id="A",
        bundle_version="1.0.0",
        produced_by="motor_001",
        produced_at="2026-05-08T00:00:00+00:00",
        payload={},
    )
    with pytest.raises(ValueError):
        bundle.is_readable_from("Z")  # type: ignore[arg-type]
