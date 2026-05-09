"""LayerBundle — bus inmutable entre las 6 capas A-F del framework.

Diseñado para reemplazar el patrón god-object actual de PipelineRun donde
múltiples motores mutan el mismo estado. Un LayerBundle es producido por una
capa específica, lleva su content_hash, y solo es consumible por capas
posteriores (A < B < C < D < E < F).

Esta infraestructura es aditiva al inicio: ningún motor la consume todavía.
La migración se hace motor por motor según RECOVERY_BACKLOG.md (R-14..R-23).

Ver RECOVERY_ARCHITECTURE_PLAN.md §3 para el diseño completo.
"""
from __future__ import annotations

import hashlib
import json
from dataclasses import dataclass, field
from typing import Any, Literal


LayerId = Literal["A", "B", "C", "D", "E", "F"]

LAYER_ORDER: tuple[LayerId, ...] = ("A", "B", "C", "D", "E", "F")


@dataclass(frozen=True)
class LayerBundle:
    """Read-only payload producido por una capa, consumible por capas posteriores.

    Campos:
        layer_id: identidad de la capa que produjo el bundle (A-F).
        bundle_version: SemVer del schema del payload (ej: "1.0.0").
        produced_by: motor_id productor.
        produced_at: ISO8601 UTC.
        payload: contenido inmutable (dict). Después de creación no debe mutarse.
        content_hash: sha256 truncado a 16 chars del payload serializado.
    """

    layer_id: LayerId
    bundle_version: str
    produced_by: str
    produced_at: str
    payload: dict[str, Any]
    content_hash: str = field(default="")

    @classmethod
    def make(
        cls,
        *,
        layer_id: LayerId,
        bundle_version: str,
        produced_by: str,
        produced_at: str,
        payload: dict[str, Any],
    ) -> "LayerBundle":
        """Construye un bundle calculando su content_hash determinísticamente."""
        if layer_id not in LAYER_ORDER:
            raise ValueError(f"Unknown layer_id: {layer_id!r}; expected one of {LAYER_ORDER}")
        if not isinstance(payload, dict):
            raise TypeError(f"payload must be dict, got {type(payload).__name__}")
        serialized = json.dumps(payload, sort_keys=True, default=str)
        digest = hashlib.sha256(serialized.encode("utf-8")).hexdigest()[:16]
        return cls(
            layer_id=layer_id,
            bundle_version=bundle_version,
            produced_by=produced_by,
            produced_at=produced_at,
            payload=payload,
            content_hash=digest,
        )

    def is_readable_from(self, consumer_layer: LayerId) -> bool:
        """Una capa solo puede leer bundles de capas estrictamente anteriores."""
        if consumer_layer not in LAYER_ORDER:
            raise ValueError(f"Unknown consumer_layer: {consumer_layer!r}")
        return LAYER_ORDER.index(self.layer_id) < LAYER_ORDER.index(consumer_layer)

    def to_dict(self) -> dict[str, Any]:
        return {
            "layer_id": self.layer_id,
            "bundle_version": self.bundle_version,
            "produced_by": self.produced_by,
            "produced_at": self.produced_at,
            "content_hash": self.content_hash,
            "payload": self.payload,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> "LayerBundle":
        return cls(
            layer_id=data["layer_id"],
            bundle_version=data["bundle_version"],
            produced_by=data["produced_by"],
            produced_at=data["produced_at"],
            payload=data["payload"],
            content_hash=data.get("content_hash", ""),
        )
