"""Adapter for motor_005 — Canonical Normalization Engine."""
from __future__ import annotations
from typing import Any
from .base import BaseMotorAdapter


class Motor005Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_005"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_004", "motor_003"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        parsed_objects = inputs.get("motor_004", {}).get("parsed_objects", [])
        intake_observables = inputs.get("motor_004", {}).get("intake_observables", {})
        alias_index = inputs.get("motor_003", {}).get("alias_index", {})
        term_index = inputs.get("motor_003", {}).get("term_index", {})

        normalized = []
        for obj in parsed_objects:
            content = obj.get("parsed_content", {})
            canonical_terms: list[str] = []

            if isinstance(content, dict):
                for v in content.values():
                    val_str = str(v)
                    if val_str in term_index:
                        canonical_terms.append(val_str)
                    elif val_str in alias_index:
                        canonical_terms.append(alias_index[val_str])
            elif isinstance(content, str):
                for alias, canonical in alias_index.items():
                    if alias in content:
                        canonical_terms.append(canonical)
                for term in term_index:
                    if term in content:
                        canonical_terms.append(term)

            normalized.append({
                **obj,
                "canonical_terms": list(set(canonical_terms)),
                "normalization_status": "normalized",
                "produced_by_motor": "motor_005",
            })

        return {
            "normalized_objects": normalized,
            "total_normalized": len(normalized),
            "normalized_intake_observables": {
                **intake_observables,
                "normalization_status": "normalized",
            },
        }
