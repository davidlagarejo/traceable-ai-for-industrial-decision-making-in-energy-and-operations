"""Adapter for motor_003 — Taxonomy + Canonical Entity Service."""
from __future__ import annotations
from typing import Any

from ..asset_contracts import derive_target_definition
from .base import BaseMotorAdapter


class Motor003Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_003"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        target_definition_contract = derive_target_definition(pipeline)
        taxonomy = pipeline.get("taxonomy", {})
        terms = taxonomy.get("terms", [])
        fi = pipeline.get("facility_inputs", {})
        loc = fi.get("input_01_location", {}) if isinstance(fi.get("input_01_location", {}), dict) else {}
        sector = fi.get("input_03_sector", {}) if isinstance(fi.get("input_03_sector", {}), dict) else {}

        term_index = {
            t["term"]: t for t in terms
        }
        alias_index = {
            alias: t["term"]
            for t in terms
            for alias in t.get("aliases", [])
        }

        return {
            "canonical_taxonomy": taxonomy,
            "taxonomy_version": taxonomy.get("version", ""),
            "terms": terms,
            "term_index": term_index,
            "alias_index": alias_index,
            "total_terms": len(terms),
            "target_definition_contract": target_definition_contract,
            "canonical_entities": {
                "issuer_entity": {
                    "entity_name": sector.get("owner_name", ""),
                    "ticker": sector.get("owner_ticker", ""),
                    "cik": sector.get("owner_cik", ""),
                    "scope_level": "issuer",
                },
                "asset_entity": {
                    "entity_name": target_definition_contract.get("target_name", ""),
                    "identifier": target_definition_contract.get("target_identifier", ""),
                    "target_type": target_definition_contract.get("target_type", ""),
                    "scope_level": target_definition_contract.get("target_scope", "asset"),
                },
                "site_entity": {
                    "address": loc.get("address", ""),
                    "jurisdiction_codes": loc.get("jurisdiction_codes", []),
                    "scope_level": "site",
                },
            },
        }
