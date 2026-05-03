from __future__ import annotations

import copy
import json
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

_HERE = Path(__file__).resolve().parent
_SRC_DIR = _HERE / "src"
if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))

from runtime_orchestrator.asset_contracts import (  # noqa: E402
    derive_effective_case_id,
    derive_subject_definition,
    derive_target_definition,
)


_TARGET_TYPE_LABELS = {
    "commercial_building": "Commercial Building",
    "multifamily_building": "Multifamily Building",
    "industrial_plant": "Industrial Plant",
    "manufacturing_facility": "Manufacturing Facility",
    "food_processing_facility": "Food Processing Facility",
    "cold_chain_facility": "Cold-Chain Facility",
    "warehouse_distribution": "Warehouse / Distribution",
    "oil_gas_upstream_site": "Oil & Gas Upstream Site",
    "oil_gas_midstream_facility": "Oil & Gas Midstream Facility",
    "oil_gas_downstream_facility": "Oil & Gas Downstream Facility",
    "water_wastewater_facility": "Water / Wastewater Facility",
    "hospital": "Hospital",
    "data_center": "Data Center",
    "campus": "Campus",
    "infrastructure_node": "Infrastructure Node",
}


def _label_for_target_type(target_type: str) -> str:
    return _TARGET_TYPE_LABELS.get(target_type, str(target_type or "").replace("_", " ").title())


def _state_from_address(address_raw: str) -> str:
    match = re.search(r",\s*([A-Z]{2})\s*(?:,|\d|$)", str(address_raw or "").upper())
    return match.group(1) if match else "US"


def _base_inputs(
    address_raw: str,
    target_type: str,
    owner_name: str = "",
    owner_ticker: str = "",
    owner_cik: str = "",
    sector: str = "",
    sic: str = "",
    decision_intent: str = "target_identification_required",
    report_intent: str = "decision_admissibility_brief",
) -> dict[str, Any]:
    address_raw = str(address_raw or "").strip()
    state_code = _state_from_address(address_raw)
    produced_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    target_label = address_raw or "Unnamed address candidate"
    target_type = str(target_type or "commercial_building").strip() or "commercial_building"
    target_label_type = _label_for_target_type(target_type)
    owner_name = str(owner_name or "").strip()
    owner_ticker = str(owner_ticker or "").strip().upper()
    owner_cik = str(owner_cik or "").strip()
    sector = str(sector or "").strip() or target_label_type
    sic = str(sic or "").strip()

    pipeline: dict[str, Any] = {
        "produced_at": produced_at,
        "case_id": f"seed-{state_code.lower()}-{datetime.now().year}",
        "case_title": "Asset Context Prior",
        "case_subtitle": f"Address-first seed | {target_label_type}",
        "organization": "ZLab Operational Truth Framework",
        "analyst": "Autonomous Research System",
        "subject_definition_contract": {
            "subject_kind": "address_candidate",
            "subject_scope": "asset",
            "subject_origin": "address_first_manual_seed",
            "asset_anchor_type": "postal_address",
            "asset_anchor_value": address_raw,
            "asset_anchor_confidence": "declared",
            "owner_context_optional": owner_name,
            "operator_context_optional": owner_name,
            "declared_asset_name": "",
            "declared_asset_identifier": "",
            "address_raw": address_raw,
            "seed_state": "address_seeded",
        },
        "target_definition_contract": {
            "target_scope": "asset",
            "target_type": target_type,
            "target_identifier": address_raw,
            "target_name": address_raw,
            "target_label": address_raw,
            "address_raw": address_raw,
            "geocode_status": "address_declared",
            "jurisdiction_scope": [f"US-{state_code}"],
            "owner_entity": owner_name,
            "operator_entity": owner_name,
            "report_intent": report_intent,
            "decision_intent": decision_intent,
            "case_mode": "address_first",
        },
        "facility_inputs": {
            "input_01_location": {
                "address": address_raw,
                "city": "",
                "state": state_code,
                "country": "US",
                "jurisdiction_codes": [f"US-{state_code}"],
                "bbl": "",
                "bin": "",
                "boro": "",
                "block": "",
                "lot": "",
            },
            "input_02_facility_type": {
                "classification": target_label_type,
                "ownership_structure": "context_only" if owner_name or owner_ticker else "unknown",
                "issuer_sector_seed": sector,
            },
            "input_03_sector": {
                "sector": sector,
                "ownership_structure": "context_only" if owner_name or owner_ticker else "unknown",
                "owner_name": owner_name,
                "owner_ticker": owner_ticker,
                "owner_cik": owner_cik,
                "sic": sic,
                "exchange": "",
            },
            "input_04_primary_use": {"uses": [target_label_type]},
            "input_05_size": {},
            "input_06_vintage": {},
            "input_07_operating_schedule": {},
            "input_08_energy_fuel": {},
            "input_09_known_systems": {},
            "input_10_main_concern": {
                "primary_concern": "operational_performance",
                "decision_type": decision_intent,
            },
        },
        "phase_contracts": [],
        "taxonomy": {"version": "taxonomy_us_realestate_v1", "produced_by": "motor_003", "terms": []},
        "source_declarations": [],
        "sources": [],
    }
    subject_definition = derive_subject_definition(pipeline)
    target_definition = derive_target_definition(pipeline)
    pipeline["subject_definition_contract"] = subject_definition
    pipeline["target_definition_contract"] = target_definition
    pipeline["case_id"] = derive_effective_case_id(pipeline, target_definition)
    return pipeline


def build_address_seed(
    address_raw: str,
    target_type: str = "commercial_building",
    owner_name: str = "",
    owner_ticker: str = "",
    owner_cik: str = "",
    sector: str = "",
    sic: str = "",
    decision_intent: str = "target_identification_required",
    report_intent: str = "decision_admissibility_brief",
) -> dict[str, Any]:
    return _base_inputs(
        address_raw=address_raw,
        target_type=target_type,
        owner_name=owner_name,
        owner_ticker=owner_ticker,
        owner_cik=owner_cik,
        sector=sector,
        sic=sic,
        decision_intent=decision_intent,
        report_intent=report_intent,
    )


def build_bounded_asset_seed(
    *,
    address_raw: str,
    asset_name: str,
    target_type: str = "commercial_building",
    owner_name: str = "",
    owner_ticker: str = "",
    owner_cik: str = "",
    sector: str = "",
    sic: str = "",
    asset_identifier: str = "",
    asset_anchor_type: str = "benchmark_record",
    asset_anchor_value: str = "",
    asset_anchor_confidence: str = "high",
    jurisdiction_scope: list[str] | None = None,
    location_overrides: dict[str, Any] | None = None,
    size_overrides: dict[str, Any] | None = None,
    vintage_overrides: dict[str, Any] | None = None,
    primary_uses: list[str] | None = None,
    decision_intent: str = "asset_screening",
    report_intent: str = "asset_preverification_screening",
) -> dict[str, Any]:
    pipeline = _base_inputs(
        address_raw=address_raw,
        target_type=target_type,
        owner_name=owner_name,
        owner_ticker=owner_ticker,
        owner_cik=owner_cik,
        sector=sector,
        sic=sic,
        decision_intent=decision_intent,
        report_intent=report_intent,
    )

    state_code = _state_from_address(address_raw)
    jurisdiction_scope = list(jurisdiction_scope or ([f"US-{state_code}"]))
    if "NEW YORK" in address_raw.upper() and "US-NY-NYC" not in jurisdiction_scope:
        jurisdiction_scope = ["US-NY-NYC", *[code for code in jurisdiction_scope if code != "US-NY-NYC"]]

    subject_contract = dict(pipeline.get("subject_definition_contract", {}))
    target_contract = dict(pipeline.get("target_definition_contract", {}))
    facility_inputs = dict(pipeline.get("facility_inputs", {}))
    location = dict(facility_inputs.get("input_01_location", {}))

    subject_contract.update(
        {
            "subject_kind": "bounded_asset",
            "subject_scope": "asset",
            "subject_origin": "bounded_asset_seed",
            "asset_anchor_type": asset_anchor_type,
            "asset_anchor_value": asset_anchor_value or f"{asset_name} @ {address_raw}",
            "asset_anchor_confidence": asset_anchor_confidence,
            "owner_context_optional": owner_name,
            "operator_context_optional": owner_name,
            "declared_asset_name": asset_name,
            "declared_asset_identifier": asset_identifier or asset_name,
            "address_raw": address_raw,
            "seed_state": "asset_seeded",
        }
    )
    target_contract.update(
        {
            "target_scope": "asset",
            "target_type": target_type,
            "target_identifier": asset_identifier or asset_name,
            "target_name": asset_name,
            "target_label": asset_name,
            "address_raw": address_raw,
            "geocode_status": "address_declared",
            "jurisdiction_scope": jurisdiction_scope,
            "owner_entity": owner_name,
            "operator_entity": owner_name,
            "report_intent": report_intent,
            "decision_intent": decision_intent,
            "case_mode": "asset_seeded",
        }
    )

    location.update(
        {
            "address": address_raw,
            "state": state_code,
            "country": "US",
            "jurisdiction_codes": jurisdiction_scope,
        }
    )
    if location_overrides:
        location.update(location_overrides)

    facility_inputs["input_01_location"] = location
    facility_inputs["input_04_primary_use"] = {"uses": list(primary_uses or [_label_for_target_type(target_type)])}
    if size_overrides:
        facility_inputs["input_05_size"] = dict(size_overrides)
    if vintage_overrides:
        facility_inputs["input_06_vintage"] = dict(vintage_overrides)

    pipeline["case_title"] = "Asset Context Prior"
    pipeline["case_subtitle"] = f"Bounded asset seed | {_label_for_target_type(target_type)}"
    pipeline["subject_definition_contract"] = subject_contract
    pipeline["target_definition_contract"] = target_contract
    pipeline["facility_inputs"] = facility_inputs

    subject_definition = derive_subject_definition(pipeline)
    target_definition = derive_target_definition(pipeline)
    pipeline["subject_definition_contract"] = subject_definition
    pipeline["target_definition_contract"] = target_definition
    pipeline["case_id"] = derive_effective_case_id(pipeline, target_definition)
    return pipeline


def normalize_pipeline_seed(pipeline: dict[str, Any]) -> dict[str, Any]:
    normalized = copy.deepcopy(pipeline)
    facility_inputs = normalized.get("facility_inputs", {}) if isinstance(normalized.get("facility_inputs", {}), dict) else {}
    location = facility_inputs.get("input_01_location", {}) if isinstance(facility_inputs.get("input_01_location", {}), dict) else {}
    sector = facility_inputs.get("input_03_sector", {}) if isinstance(facility_inputs.get("input_03_sector", {}), dict) else {}
    concern = facility_inputs.get("input_10_main_concern", {}) if isinstance(facility_inputs.get("input_10_main_concern", {}), dict) else {}

    subject_definition = derive_subject_definition(normalized)
    target_definition = derive_target_definition(normalized)
    address_raw = str(
        target_definition.get("address_raw")
        or location.get("address")
        or target_definition.get("target_identifier")
        or ""
    ).strip()
    state_code = _state_from_address(address_raw)
    target_type = str(target_definition.get("target_type") or "commercial_building").strip()
    target_label_type = _label_for_target_type(target_type)

    decision_intent = str(
        target_definition.get("decision_intent")
        or concern.get("decision_type")
        or "target_identification_required"
    ).strip()
    if decision_intent in {"investment_evaluation", "investment_screening"} and subject_definition.get("subject_kind") in {"address_candidate", "site_candidate"}:
        decision_intent = "target_identification_required"

    report_intent = str(target_definition.get("report_intent") or "decision_admissibility_brief").strip()

    normalized["case_title"] = "Asset Context Prior"
    normalized["case_subtitle"] = f"Address-first seed | {target_label_type}"
    normalized["organization"] = normalized.get("organization") or "ZLab Operational Truth Framework"
    normalized["analyst"] = normalized.get("analyst") or "Autonomous Research System"

    subject_definition.update({
        "subject_origin": subject_definition.get("subject_origin") or "normalized_legacy_seed",
        "address_raw": address_raw,
        "seed_state": subject_definition.get("seed_state") or "address_seeded",
    })
    target_definition.update({
        "target_scope": "asset",
        "target_identifier": address_raw or target_definition.get("target_identifier", ""),
        "target_name": address_raw or target_definition.get("target_name", ""),
        "target_label": address_raw or target_definition.get("target_label", ""),
        "address_raw": address_raw,
        "geocode_status": target_definition.get("geocode_status") or "address_declared",
        "jurisdiction_scope": target_definition.get("jurisdiction_scope") or [f"US-{state_code}"],
        "report_intent": report_intent,
        "decision_intent": decision_intent,
        "case_mode": "address_first",
    })

    normalized["subject_definition_contract"] = subject_definition
    normalized["target_definition_contract"] = target_definition
    normalized["case_id"] = derive_effective_case_id(normalized, target_definition)

    facility_inputs.setdefault("input_01_location", {})
    facility_inputs["input_01_location"].setdefault("address", address_raw)
    facility_inputs["input_01_location"].setdefault("state", state_code)
    facility_inputs["input_01_location"].setdefault("country", "US")
    facility_inputs["input_01_location"].setdefault("jurisdiction_codes", [f"US-{state_code}"])

    facility_inputs.setdefault("input_02_facility_type", {})
    facility_inputs["input_02_facility_type"].setdefault("issuer_sector_seed", sector.get("sector", ""))
    if not str(facility_inputs["input_02_facility_type"].get("classification", "")).strip():
        facility_inputs["input_02_facility_type"]["classification"] = target_label_type

    facility_inputs.setdefault("input_10_main_concern", {})
    facility_inputs["input_10_main_concern"]["decision_type"] = decision_intent
    normalized["facility_inputs"] = facility_inputs
    return normalized


def write_seed_file(inputs_dir: Path, pipeline: dict[str, Any], stem_hint: str | None = None) -> Path:
    inputs_dir.mkdir(parents=True, exist_ok=True)
    target_definition = pipeline.get("target_definition_contract", {})
    stem = (
        str(stem_hint or "").strip()
        or str(target_definition.get("target_id") or target_definition.get("target_slug") or pipeline.get("case_id") or "target")
    )
    safe_stem = re.sub(r"[^a-zA-Z0-9_-]+", "-", stem).strip("-").lower() or "target"
    path = inputs_dir / f"{safe_stem}_inputs.json"
    path.write_text(json.dumps(pipeline, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return path


def normalize_input_files(inputs_dir: Path) -> list[Path]:
    updated: list[Path] = []
    for path in sorted(inputs_dir.glob("*_inputs.json")):
        pipeline = json.loads(path.read_text(encoding="utf-8"))
        normalized = normalize_pipeline_seed(pipeline)
        path.write_text(json.dumps(normalized, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
        updated.append(path)
    return updated
