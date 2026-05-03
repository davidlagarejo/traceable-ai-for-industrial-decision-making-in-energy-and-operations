"""Adapter for motor_001 — Phase Contract Registry.

Validates that pipeline phase_contracts have the minimum required fields.
Rather than constructing the full PhaseContract domain objects (which require
internal ZLab EntityId, PhaseId, etc.), this adapter performs structural
validation and passes the contracts downstream as-is for motors that need them.

For full domain validation, instantiate motor_001 directly with its own API.
"""
from __future__ import annotations

from typing import Any

from ..asset_contracts import (
    derive_subject_contract_admissibility,
    derive_subject_definition,
    derive_target_type_classification_seed,
    derive_target_definition,
)
from .base import BaseMotorAdapter

_REQUIRED_FIELDS = {"phase_id", "phase_name", "allowed_inputs", "allowed_outputs", "constraints"}


def _identity_gate_preconditions(
    subject_definition_contract: dict[str, Any],
    target_definition_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    address_raw = str(subject_definition_contract.get("address_raw") or target_definition_contract.get("address_raw") or "").strip()
    asset_anchor_type = str(subject_definition_contract.get("asset_anchor_type") or "").strip()
    target_type = str(target_definition_contract.get("target_type") or "").strip()
    owner_context = str(subject_definition_contract.get("owner_context_optional") or target_definition_contract.get("owner_entity") or "").strip()
    return [
        {
            "field": "address_raw",
            "required": True,
            "status": "present" if address_raw else "missing",
            "detail": "A declared physical address is required before identity confirmation can begin.",
        },
        {
            "field": "asset_anchor",
            "required": True,
            "status": "present" if asset_anchor_type else "missing",
            "detail": "A physical anchor type is required to distinguish asset, site, or issuer context.",
        },
        {
            "field": "target_type",
            "required": False,
            "status": "present" if target_type else "missing",
            "detail": "Target type can be inferred, but an explicit declaration improves route discipline.",
        },
        {
            "field": "owner_context",
            "required": False,
            "status": "present" if owner_context else "missing",
            "detail": "Owner context may help entity separation, but it must not substitute asset evidence.",
        },
        {
            "field": "asset_level_public_record",
            "required": True,
            "status": "unconfirmed",
            "detail": "Asset-level corroboration is still required before physical or technical scraping rounds may proceed.",
        },
    ]


def _ingestion_contract_status(
    subject_contract_admissibility: str,
    target_type_classification_seed: dict[str, Any],
) -> str:
    classification = str(target_type_classification_seed.get("target_type_classification") or "").strip()
    if subject_contract_admissibility == "invalid_for_asset_pipeline":
        return "invalid_for_ingestion"
    if classification in {"CORPORATE_HEADQUARTERS", "PORTFOLIO_ENTITY", "REGISTERED_AGENT_OR_MAILING_ADDRESS"}:
        return "context_only_ingestion"
    if classification in {"AMBIGUOUS_TARGET", "PROPERTY_LISTING"}:
        return "identity_gate_required"
    if classification == "OPERATING_ASSET":
        return "ready_for_identity_gate"
    return "identity_gate_required"


def _prohibited_scrape_rounds(
    ingestion_contract_status: str,
    target_type_classification_seed: dict[str, Any],
) -> list[str]:
    classification = str(target_type_classification_seed.get("target_type_classification") or "").strip()
    if ingestion_contract_status == "invalid_for_ingestion":
        return [
            "round_2_asset_physical_substrate",
            "round_3_energy_utility_compliance",
            "round_4_owner_issuer_context",
            "round_5_benchmarks",
        ]
    if classification in {"CORPORATE_HEADQUARTERS", "REGISTERED_AGENT_OR_MAILING_ADDRESS", "PORTFOLIO_ENTITY"}:
        return [
            "round_2_asset_physical_substrate",
            "round_3_energy_utility_compliance",
            "round_4_owner_issuer_context",
            "round_5_benchmarks",
        ]
    if classification in {"AMBIGUOUS_TARGET", "PROPERTY_LISTING"}:
        return [
            "round_2_asset_physical_substrate",
            "round_3_energy_utility_compliance",
            "round_4_owner_issuer_context",
            "round_5_benchmarks",
        ]
    return []


class Motor001Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_001"

    @property
    def input_motor_ids(self) -> list[str]:
        return []

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        raw_contracts = pipeline.get("phase_contracts", [])
        subject_definition_contract = derive_subject_definition(pipeline)
        target_definition_contract = derive_target_definition(pipeline)
        subject_contract_admissibility, subject_contract_warning_register = derive_subject_contract_admissibility(
            subject_definition_contract,
            target_definition_contract,
        )
        target_type_classification_seed = derive_target_type_classification_seed(
            subject_definition_contract,
            target_definition_contract,
        )
        identity_gate_preconditions = _identity_gate_preconditions(
            subject_definition_contract,
            target_definition_contract,
        )
        ingestion_contract_status = _ingestion_contract_status(
            subject_contract_admissibility,
            target_type_classification_seed,
        )
        prohibited_scrape_rounds = _prohibited_scrape_rounds(
            ingestion_contract_status,
            target_type_classification_seed,
        )

        validated: list[dict[str, Any]] = []
        rejected: list[dict[str, Any]] = []
        target_contract_warnings: list[str] = []
        subject_contract_warnings: list[str] = []

        for contract in raw_contracts:
            missing = _REQUIRED_FIELDS - set(contract.keys())
            if missing:
                rejected.append({
                    "phase_id": contract.get("phase_id", "unknown"),
                    "reason": f"missing fields: {sorted(missing)}",
                })
            else:
                validated.append(contract)

        if target_definition_contract.get("contract_status") == "inferred":
            target_contract_warnings.append(
                "target_definition_contract was inferred from pipeline inputs; explicit target contract is recommended."
            )
        if target_definition_contract.get("target_scope") == "asset" and not target_definition_contract.get("address_raw"):
            target_contract_warnings.append(
                "asset-scoped case declared without address or explicit physical identifier."
            )
        for warning in subject_contract_warning_register:
            message = str(warning.get("message", "")).strip()
            if message:
                subject_contract_warnings.append(message)

        subject_contract_status = str(subject_definition_contract.get("contract_status") or "inferred")

        return {
            "validated_contracts": validated,
            "rejected_contracts": rejected,
            "total_input": len(raw_contracts),
            "total_valid": len(validated),
            "subject_definition_contract": subject_definition_contract,
            "subject_contract_status": subject_contract_status,
            "subject_contract_admissibility": subject_contract_admissibility,
            "subject_contract_warning_register": subject_contract_warning_register,
            "subject_contract_warnings": subject_contract_warnings,
            "target_definition_contract": target_definition_contract,
            "target_contract_status": target_definition_contract.get("contract_status", "inferred"),
            "target_contract_warnings": target_contract_warnings,
            "target_type_classification_seed": target_type_classification_seed,
            "ingestion_contract_status": ingestion_contract_status,
            "identity_gate_preconditions": identity_gate_preconditions,
            "prohibited_scrape_rounds": prohibited_scrape_rounds,
        }
