"""Deterministic implementation for motor_019.

The engine converts inference records and accepted real validation data into
explicit evidence-hardening routes. It validates phase-contract scope,
preserves immutable upstream references, rejects synthetic support, and emits
EvidenceGap records for missing or conflicting evidence.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass, replace
import hashlib
import json
from typing import Any

from .models import (
    EvidenceGap,
    HardeningAction,
    HardeningAgenda,
    LinkedEvidenceRef,
    RequiredEvidenceItem,
    TargetRef,
    VerificationBridgeResult,
    VerificationPath,
    VerificationStep,
)


MOTOR_ID = "motor_019"
DEFAULT_RULE_VERSION = "m019-rules-v1"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"

VALID_EVIDENCE_LEVELS = ("hypothesis", "inference_result", "validation_data", "field_evidence")
REAL_EVIDENCE_LEVELS = ("validation_data", "field_evidence")
INVALID_EVIDENCE_MARKERS = frozenset(
    {
        "synthetic_support",
        "synthetic_data",
        "expert_spec",
        "expert_specification",
        "capability_demo",
        "non_evidentiary",
    }
)
ACCEPTED_QUALITY_STATUSES = frozenset({"accepted", "accepted_with_warning"})
REQUIRED_OUTPUTS = frozenset(
    {"verification_path", "hardening_agenda", "evidence_gap_record"}
)
REQUIRED_INPUTS = frozenset({"inference_records", "validation_data"})
EVIDENCE_RANK = {
    "hypothesis": 0,
    "inference_result": 1,
    "validation_data": 2,
    "field_evidence": 3,
}


@dataclass(frozen=True)
class _InferenceContext:
    raw: Mapping[str, Any]
    inference_ref: str
    target_ref: TargetRef
    target_id: str
    lineage_refs: list[str]
    version_id: str
    evidentiary_basis: list[str]
    unresolved_gaps: list[str]


@dataclass(frozen=True)
class _ValidationContext:
    raw: Mapping[str, Any]
    validation_ref: str
    evidence_level: str
    quality_status: str
    lineage_refs: list[str]
    version_id: str
    source_provenance: str


@dataclass(frozen=True)
class _ContractContext:
    raw: Mapping[str, Any]
    phase_contract_id: str
    contract_version: str
    evidence_thresholds: Mapping[str, Any]
    owner_role: str


@dataclass(frozen=True)
class _PathAssembly:
    path: VerificationPath
    gaps: list[EvidenceGap]


class VerificationBridgeEngine:
    """Core deterministic interface for the Verification Bridge Engine."""

    def __init__(
        self,
        *,
        rule_version: str = DEFAULT_RULE_VERSION,
        produced_at: str = DEFAULT_PRODUCED_AT,
        owner_role: str = "field_validation_lead",
    ) -> None:
        self.rule_version = _require_text(rule_version, "rule_version")
        self.produced_at = _require_text(produced_at, "produced_at")
        self.owner_role = _require_text(owner_role, "owner_role")

    def run(
        self,
        *,
        inference_records: Sequence[Mapping[str, Any]],
        validation_data: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
    ) -> VerificationBridgeResult:
        """Build verification paths, gaps, and one hardening agenda."""

        errors: list[dict[str, Any]] = []
        inference_items, inference_errors = _as_record_list(
            "inference_records", inference_records
        )
        validation_items, validation_errors = _as_record_list(
            "validation_data", validation_data
        )
        contract_items, contract_errors = _as_record_list(
            "phase_contracts", phase_contracts
        )
        errors.extend(inference_errors)
        errors.extend(validation_errors)
        errors.extend(contract_errors)
        if errors:
            return self._rejected(errors)

        if not inference_items:
            return self._rejected(
                [
                    _validation_error(
                        "MISSING_INFERENCE_LINEAGE",
                        "inference_records",
                        "input.inference_records",
                        "at least one inference record is required",
                    )
                ]
            )

        contract, contract_scope_errors = self._select_contract(contract_items)
        if contract_scope_errors:
            return self._rejected(contract_scope_errors)

        validation_contexts, validation_context_errors = self._parse_validation_data(
            validation_items
        )
        if validation_context_errors:
            return self._rejected(validation_context_errors)

        inference_contexts, inference_context_errors = self._parse_inference_records(
            inference_items
        )
        if inference_context_errors:
            return self._rejected(inference_context_errors)

        paths: list[VerificationPath] = []
        gaps: list[EvidenceGap] = []
        for inference in sorted(
            inference_contexts,
            key=lambda item: (item.inference_ref, item.target_ref.target_type, item.target_id),
        ):
            linked_validation = self._linked_validation_for_target(
                inference, validation_contexts
            )
            assembly = self._build_path(inference, linked_validation, contract)
            paths.append(assembly.path)
            gaps.extend(assembly.gaps)

        agenda = self._build_agenda(paths, gaps, contract)
        if agenda is not None:
            paths = [
                self._with_agenda_ref(path, agenda.agenda_id)
                for path in paths
            ]

        return VerificationBridgeResult(
            verification_paths=paths,
            hardening_agenda=agenda,
            evidence_gap_records=gaps,
            errors=[],
        )

    def build_verification_bridge(
        self,
        *,
        inference_records: Sequence[Mapping[str, Any]],
        validation_data: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
    ) -> VerificationBridgeResult:
        """Alias named after the motor purpose."""

        return self.run(
            inference_records=inference_records,
            validation_data=validation_data,
            phase_contracts=phase_contracts,
        )

    def _parse_inference_records(
        self, inference_records: Sequence[Mapping[str, Any]]
    ) -> tuple[list[_InferenceContext], list[dict[str, Any]]]:
        contexts: list[_InferenceContext] = []
        errors: list[dict[str, Any]] = []
        for index, record in enumerate(inference_records):
            field_prefix = f"inference_records[{index}]"
            inference_ref = _text(
                record.get("inference_record_id")
                or record.get("inference_id")
                or record.get("source_inference_ref")
            )
            lineage_refs = _string_list(record.get("lineage_refs"))
            version_id = _text(record.get("version_id"))
            if not inference_ref or not lineage_refs or not version_id:
                errors.append(
                    _validation_error(
                        "MISSING_INFERENCE_LINEAGE",
                        inference_ref or field_prefix,
                        field_prefix,
                        "inference record requires source id, lineage_refs, and version_id",
                    )
                )
                continue

            target_ref, target_error = _target_ref_from_record(record)
            if target_error is not None:
                errors.append(
                    _validation_error(
                        "UNSUPPORTED_TARGET_REF",
                        inference_ref,
                        field_prefix,
                        target_error,
                    )
                )
                continue

            evidentiary_basis = _string_list(record.get("evidentiary_basis"))
            if _contains_invalid_marker(evidentiary_basis):
                errors.append(
                    _validation_error(
                        "INVALID_EVIDENCE_LEVEL",
                        inference_ref,
                        f"{field_prefix}.evidentiary_basis",
                        "inference evidentiary_basis contains non-real evidence",
                    )
                )
                continue

            contexts.append(
                _InferenceContext(
                    raw=record,
                    inference_ref=inference_ref,
                    target_ref=target_ref,
                    target_id=target_ref.claim_id or target_ref.tension_id or "",
                    lineage_refs=lineage_refs,
                    version_id=version_id,
                    evidentiary_basis=evidentiary_basis,
                    unresolved_gaps=_string_list(record.get("unresolved_gaps")),
                )
            )
        return contexts, errors

    def _parse_validation_data(
        self, validation_data: Sequence[Mapping[str, Any]]
    ) -> tuple[list[_ValidationContext], list[dict[str, Any]]]:
        contexts: list[_ValidationContext] = []
        errors: list[dict[str, Any]] = []
        for index, record in enumerate(validation_data):
            field_prefix = f"validation_data[{index}]"
            validation_ref = _text(
                record.get("validation_data_id")
                or record.get("validation_id")
                or record.get("evidence_ref_id")
            )
            evidence_level = _text(record.get("evidence_level"))
            quality_status = _text(record.get("quality_status"))
            lineage_refs = _string_list(record.get("lineage_refs"))
            version_id = _text(record.get("version_id"))
            source_provenance = _text(record.get("source_provenance"))
            invalid_reason = self._invalid_validation_reason(
                record=record,
                validation_ref=validation_ref,
                evidence_level=evidence_level,
                quality_status=quality_status,
                lineage_refs=lineage_refs,
                version_id=version_id,
                source_provenance=source_provenance,
            )
            if invalid_reason:
                errors.append(
                    _validation_error(
                        "INVALID_EVIDENCE_LEVEL",
                        validation_ref or field_prefix,
                        field_prefix,
                        invalid_reason,
                    )
                )
                continue
            contexts.append(
                _ValidationContext(
                    raw=record,
                    validation_ref=validation_ref,
                    evidence_level=evidence_level,
                    quality_status=quality_status,
                    lineage_refs=lineage_refs,
                    version_id=version_id,
                    source_provenance=source_provenance,
                )
            )
        return contexts, errors

    def _invalid_validation_reason(
        self,
        *,
        record: Mapping[str, Any],
        validation_ref: str,
        evidence_level: str,
        quality_status: str,
        lineage_refs: list[str],
        version_id: str,
        source_provenance: str,
    ) -> str | None:
        if not validation_ref:
            return "validation data requires validation_data_id"
        if evidence_level in INVALID_EVIDENCE_MARKERS:
            return "validation data evidence_level is not real verification evidence"
        if record.get("non_evidentiary_flag") is True:
            return "validation data is explicitly marked non-evidentiary"
        if _contains_invalid_marker(_flatten_text_values(record.get("evidentiary_basis"))):
            return "validation data evidentiary_basis contains non-real evidence"
        if evidence_level not in REAL_EVIDENCE_LEVELS:
            return "validation data evidence_level must be validation_data or field_evidence"
        if not source_provenance or source_provenance in INVALID_EVIDENCE_MARKERS:
            return "validation data requires traceable real-data source_provenance"
        if not lineage_refs or not version_id:
            return "validation data requires lineage_refs and version_id"
        if quality_status not in ACCEPTED_QUALITY_STATUSES:
            return "validation data quality_status is not accepted"
        return None

    def _select_contract(
        self, phase_contracts: Sequence[Mapping[str, Any]]
    ) -> tuple[_ContractContext | None, list[dict[str, Any]]]:
        errors: list[dict[str, Any]] = []
        candidates: list[_ContractContext] = []
        if not phase_contracts:
            return None, [
                _validation_error(
                    "CONTRACT_MISMATCH",
                    "phase_contracts",
                    "input.phase_contracts",
                    "at least one phase contract is required",
                )
            ]

        for index, contract in enumerate(phase_contracts):
            field_prefix = f"phase_contracts[{index}]"
            phase_contract_id = _text(
                contract.get("contract_id") or contract.get("phase_id")
            )
            contract_version = _text(contract.get("contract_version"))
            allowed_inputs = set(_string_list(contract.get("allowed_inputs")))
            allowed_outputs = set(_string_list(contract.get("allowed_outputs")))
            evidence_thresholds = contract.get("evidence_thresholds")
            handoff_rules = contract.get("handoff_rules")
            if not isinstance(evidence_thresholds, Mapping):
                evidence_thresholds = {}
            if not isinstance(handoff_rules, Mapping):
                handoff_rules = {}

            missing = []
            if not phase_contract_id:
                missing.append("contract_id or phase_id")
            if not contract_version:
                missing.append("contract_version")
            if missing:
                errors.append(
                    _validation_error(
                        "CONTRACT_MISMATCH",
                        phase_contract_id or field_prefix,
                        field_prefix,
                        f"phase contract missing {', '.join(missing)}",
                    )
                )
                continue
            if not REQUIRED_INPUTS.issubset(allowed_inputs):
                errors.append(
                    _validation_error(
                        "CONTRACT_MISMATCH",
                        phase_contract_id,
                        f"{field_prefix}.allowed_inputs",
                        "phase contract must allow inference_records and validation_data",
                    )
                )
                continue
            if not REQUIRED_OUTPUTS.issubset(allowed_outputs):
                errors.append(
                    _validation_error(
                        "CONTRACT_MISMATCH",
                        phase_contract_id,
                        f"{field_prefix}.allowed_outputs",
                        "phase contract must allow verification_path, hardening_agenda, and evidence_gap_record",
                    )
                )
                continue
            if handoff_rules.get("allow_synthetic_support") is True:
                errors.append(
                    _validation_error(
                        "CONTRACT_MISMATCH",
                        phase_contract_id,
                        f"{field_prefix}.handoff_rules",
                        "phase contract cannot authorize synthetic support as verification evidence",
                    )
                )
                continue
            candidates.append(
                _ContractContext(
                    raw=contract,
                    phase_contract_id=phase_contract_id,
                    contract_version=contract_version,
                    evidence_thresholds=evidence_thresholds,
                    owner_role=_text(contract.get("owner_role")) or self.owner_role,
                )
            )

        if candidates:
            selected = sorted(
                candidates,
                key=lambda item: (item.phase_contract_id, item.contract_version),
            )[0]
            return selected, []
        if errors:
            return None, errors
        return None, [
            _validation_error(
                "CONTRACT_MISMATCH",
                "phase_contracts",
                "input.phase_contracts",
                "no phase contract authorizes motor_019 handoff",
            )
        ]

    def _linked_validation_for_target(
        self,
        inference: _InferenceContext,
        validation_contexts: Sequence[_ValidationContext],
    ) -> list[_ValidationContext]:
        target_tokens = {
            inference.target_id,
            inference.inference_ref,
            *inference.evidentiary_basis,
        }
        linked: list[_ValidationContext] = []
        for validation in validation_contexts:
            if validation.validation_ref in inference.evidentiary_basis:
                linked.append(validation)
                continue
            if inference.target_id in _validation_target_tokens(validation.raw):
                linked.append(validation)
                continue
            if inference.inference_ref in _validation_target_tokens(validation.raw):
                linked.append(validation)
                continue
            if target_tokens.intersection(_string_list(validation.raw.get("source_refs"))):
                linked.append(validation)
        return sorted(linked, key=lambda item: item.validation_ref)

    def _build_path(
        self,
        inference: _InferenceContext,
        linked_validation: Sequence[_ValidationContext],
        contract: _ContractContext,
    ) -> _PathAssembly:
        has_conflict = _has_conflicting_validation(linked_validation)
        accepted_validation = [] if has_conflict else list(linked_validation)
        linked_refs = [
            self._linked_evidence_ref(validation)
            for validation in accepted_validation
        ]
        target_level = self._target_evidence_level(inference, contract)
        current_level = self._current_evidence_level(linked_refs, has_conflict)
        lineage_refs = _stable_unique(
            [
                *inference.lineage_refs,
                inference.version_id,
                f"{contract.phase_contract_id}@{contract.contract_version}",
                *[
                    ref
                    for validation in linked_validation
                    for ref in [*validation.lineage_refs, validation.version_id]
                ],
            ]
        )

        base_requirements = self._satisfied_requirements(linked_refs, target_level)
        gap_specs = self._gap_specs(
            inference=inference,
            linked_validation=linked_validation,
            has_conflict=has_conflict,
            target_level=target_level,
            current_level=current_level,
        )
        for gap_spec in gap_specs:
            base_requirements.append(
                {
                    "evidence_requirement_id": gap_spec["requirement_id"],
                    "evidence_type": gap_spec["evidence_type"],
                    "required_level": gap_spec["required_level"],
                    "satisfied_by_refs": [],
                    "is_satisfied": False,
                    "gap_ref": None,
                    "gap_spec": gap_spec,
                }
            )

        path_hash_content = {
            "target_ref": inference.target_ref.to_dict(),
            "source_inference_ref": inference.inference_ref,
            "phase_contract_id": contract.phase_contract_id,
            "contract_version": contract.contract_version,
            "current_evidence_level": current_level,
            "target_evidence_level": target_level,
            "linked_evidence_refs": [ref.to_dict() for ref in linked_refs],
            "required_evidence": [
                {
                    key: value
                    for key, value in requirement.items()
                    if key != "gap_spec"
                }
                for requirement in base_requirements
            ],
            "rule_version": self.rule_version,
            "lineage_refs": lineage_refs,
        }
        path_version_hash = _hash_content(path_hash_content)
        path_id = (
            "motor_019:verification_path:"
            f"{inference.inference_ref}:{inference.target_ref.target_type}:"
            f"{inference.target_id}:{contract.contract_version}:"
            f"{path_version_hash[:12]}"
        )

        gaps = [
            self._build_gap(
                path_id=path_id,
                inference=inference,
                contract=contract,
                gap_spec=requirement["gap_spec"],
                lineage_refs=lineage_refs,
            )
            for requirement in base_requirements
            if "gap_spec" in requirement
        ]
        gap_by_requirement = {
            gap.source_ref.rsplit(":", 1)[-1]: gap.gap_id
            for gap in gaps
        }
        required_evidence = [
            RequiredEvidenceItem(
                evidence_requirement_id=requirement["evidence_requirement_id"],
                evidence_type=requirement["evidence_type"],
                required_level=requirement["required_level"],
                satisfied_by_refs=list(requirement["satisfied_by_refs"]),
                is_satisfied=bool(requirement["is_satisfied"]),
                gap_ref=gap_by_requirement.get(requirement["evidence_requirement_id"]),
            )
            for requirement in base_requirements
        ]
        evidence_gap_refs = [gap.gap_id for gap in gaps]
        verification_steps = self._verification_steps(
            path_id=path_id,
            inference=inference,
            contract=contract,
            linked_refs=linked_refs,
            requirements=required_evidence,
        )
        review_trigger = _review_trigger(gaps, has_conflict)
        status = _path_status(current_level, target_level, bool(gaps), has_conflict)
        final_path_content = {
            **path_hash_content,
            "path_id": path_id,
            "required_evidence": [
                requirement.to_dict() for requirement in required_evidence
            ],
            "verification_steps": [step.to_dict() for step in verification_steps],
            "evidence_gap_refs": evidence_gap_refs,
            "status": status,
            "review_trigger": review_trigger,
        }
        version_hash = _hash_content(final_path_content)
        path = VerificationPath(
            path_id=path_id,
            motor_id=MOTOR_ID,
            target_ref=inference.target_ref,
            source_inference_ref=inference.inference_ref,
            source_tension_ref=(
                inference.target_ref.tension_id
                if inference.target_ref.target_type == "tension"
                else None
            ),
            phase_contract_id=contract.phase_contract_id,
            contract_version=contract.contract_version,
            current_evidence_level=current_level,
            target_evidence_level=target_level,
            required_evidence=required_evidence,
            linked_evidence_refs=linked_refs,
            verification_steps=verification_steps,
            evidence_gap_refs=evidence_gap_refs,
            agenda_ref=None,
            status=status,
            review_trigger=review_trigger,
            rule_version=self.rule_version,
            lineage_refs=lineage_refs,
            version_id=f"motor_019:v:verification_path:{version_hash[:16]}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=version_hash,
            source_ref=f"{inference.inference_ref}:{inference.target_ref.target_type}:{inference.target_id}",
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )
        return _PathAssembly(path=path, gaps=gaps)

    def _linked_evidence_ref(self, validation: _ValidationContext) -> LinkedEvidenceRef:
        evidence_hash = _hash_content(
            {
                "validation_ref": validation.validation_ref,
                "evidence_level": validation.evidence_level,
                "version_id": validation.version_id,
            }
        )
        return LinkedEvidenceRef(
            evidence_ref_id=f"motor_019:linked_evidence:{validation.validation_ref}:{evidence_hash[:10]}",
            upstream_motor_id=(
                "external_field_evidence"
                if validation.evidence_level == "field_evidence"
                else "motor_018"
            ),
            upstream_artifact_ref=validation.validation_ref,
            evidence_level=validation.evidence_level,
            quality_status=validation.quality_status,
            lineage_ref=validation.lineage_refs[0],
        )

    def _target_evidence_level(
        self, inference: _InferenceContext, contract: _ContractContext
    ) -> str:
        threshold = (
            contract.evidence_thresholds.get(inference.target_id)
            or contract.evidence_thresholds.get(inference.target_ref.target_type)
            or contract.evidence_thresholds.get("default")
            or "validation_data"
        )
        if isinstance(threshold, Mapping):
            threshold = threshold.get("target_evidence_level") or threshold.get("level")
        threshold_text = _text(threshold)
        if threshold_text in ("validation_data", "field_evidence"):
            return threshold_text
        return "validation_data"

    def _current_evidence_level(
        self,
        linked_refs: Sequence[LinkedEvidenceRef],
        has_conflict: bool,
    ) -> str:
        if has_conflict:
            return "inference_result"
        if not linked_refs:
            return "hypothesis"
        strongest = max(
            (ref.evidence_level for ref in linked_refs),
            key=lambda level: EVIDENCE_RANK[level],
        )
        return strongest

    def _satisfied_requirements(
        self,
        linked_refs: Sequence[LinkedEvidenceRef],
        target_level: str,
    ) -> list[dict[str, Any]]:
        requirements: list[dict[str, Any]] = []
        for index, evidence_ref in enumerate(linked_refs, start=1):
            evidence_type = (
                "site_validation"
                if evidence_ref.evidence_level == "field_evidence"
                else "measurement"
            )
            requirements.append(
                {
                    "evidence_requirement_id": f"req_real_evidence_{index:03d}",
                    "evidence_type": evidence_type,
                    "required_level": min_level(evidence_ref.evidence_level, target_level),
                    "satisfied_by_refs": [evidence_ref.upstream_artifact_ref],
                    "is_satisfied": True,
                    "gap_ref": None,
                }
            )
        return requirements

    def _gap_specs(
        self,
        *,
        inference: _InferenceContext,
        linked_validation: Sequence[_ValidationContext],
        has_conflict: bool,
        target_level: str,
        current_level: str,
    ) -> list[dict[str, Any]]:
        specs: list[dict[str, Any]] = []
        if has_conflict:
            refs = [validation.validation_ref for validation in linked_validation]
            specs.append(
                {
                    "requirement_id": "req_conflict_resolution",
                    "evidence_type": "conflict_resolution",
                    "required_level": target_level,
                    "severity": "blocking",
                    "blocking_reason": "accepted validation records conflict for the same target",
                    "recommended_next_action": "reconcile accepted validation records before evidence hardening",
                    "related_validation_data_refs": refs,
                }
            )

        seen_gap_types = {spec["evidence_type"] for spec in specs}
        for gap_index, gap_text in enumerate(inference.unresolved_gaps, start=1):
            evidence_type = _evidence_type_for_gap(gap_text)
            seen_gap_types.add(evidence_type)
            specs.append(
                {
                    "requirement_id": f"req_unresolved_gap_{gap_index:03d}_{evidence_type}",
                    "evidence_type": evidence_type,
                    "required_level": target_level,
                    "severity": "blocking",
                    "blocking_reason": f"upstream unresolved gap remains open: {gap_text}",
                    "recommended_next_action": _recommended_action_text(evidence_type),
                    "related_validation_data_refs": [],
                }
            )

        if not linked_validation and not inference.unresolved_gaps:
            evidence_type = "site_validation" if target_level == "field_evidence" else "measurement"
            specs.append(
                {
                    "requirement_id": f"req_missing_{evidence_type}",
                    "evidence_type": evidence_type,
                    "required_level": target_level,
                    "severity": "blocking",
                    "blocking_reason": "no linked real validation data exists for the target",
                    "recommended_next_action": _recommended_action_text(evidence_type),
                    "related_validation_data_refs": [],
                }
            )
            seen_gap_types.add(evidence_type)

        if (
            linked_validation
            and EVIDENCE_RANK[current_level] < EVIDENCE_RANK[target_level]
            and "site_validation" not in seen_gap_types
            and target_level == "field_evidence"
        ):
            specs.append(
                {
                    "requirement_id": "req_field_evidence_confirmation",
                    "evidence_type": "site_validation",
                    "required_level": "field_evidence",
                    "severity": "blocking",
                    "blocking_reason": "linked validation data is below the field_evidence threshold",
                    "recommended_next_action": _recommended_action_text("site_validation"),
                    "related_validation_data_refs": [
                        validation.validation_ref for validation in linked_validation
                    ],
                }
            )

        return specs

    def _build_gap(
        self,
        *,
        path_id: str,
        inference: _InferenceContext,
        contract: _ContractContext,
        gap_spec: Mapping[str, Any],
        lineage_refs: Sequence[str],
    ) -> EvidenceGap:
        source_ref = f"{path_id}:{gap_spec['requirement_id']}"
        content = {
            "path_id": path_id,
            "target_ref": inference.target_ref.to_dict(),
            "source_inference_ref": inference.inference_ref,
            "phase_contract_id": contract.phase_contract_id,
            "contract_version": contract.contract_version,
            "missing_evidence_type": gap_spec["evidence_type"],
            "gap_severity": gap_spec["severity"],
            "blocking_reason": gap_spec["blocking_reason"],
            "recommended_next_action": gap_spec["recommended_next_action"],
            "related_validation_data_refs": gap_spec["related_validation_data_refs"],
            "status": "open",
            "lineage_refs": list(lineage_refs),
            "source_ref": source_ref,
        }
        version_hash = _hash_content(content)
        gap_id = (
            "motor_019:evidence_gap:"
            f"{path_id.rsplit(':', 1)[-1]}:{gap_spec['requirement_id']}:{version_hash[:10]}"
        )
        return EvidenceGap(
            gap_id=gap_id,
            motor_id=MOTOR_ID,
            path_id=path_id,
            target_ref=inference.target_ref,
            source_inference_ref=inference.inference_ref,
            phase_contract_id=contract.phase_contract_id,
            contract_version=contract.contract_version,
            missing_evidence_type=gap_spec["evidence_type"],
            gap_severity=gap_spec["severity"],
            blocking_reason=gap_spec["blocking_reason"],
            recommended_next_action=gap_spec["recommended_next_action"],
            related_validation_data_refs=list(gap_spec["related_validation_data_refs"]),
            resolved_by_ref=None,
            status="open",
            lineage_refs=list(lineage_refs),
            version_id=f"motor_019:v:evidence_gap:{version_hash[:16]}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )

    def _verification_steps(
        self,
        *,
        path_id: str,
        inference: _InferenceContext,
        contract: _ContractContext,
        linked_refs: Sequence[LinkedEvidenceRef],
        requirements: Sequence[RequiredEvidenceItem],
    ) -> list[VerificationStep]:
        steps: list[VerificationStep] = []
        prior_step_ids: list[str] = []
        for index, linked_ref in enumerate(linked_refs, start=1):
            step_id = f"{path_id}:step_check_validation_data_{index:03d}"
            steps.append(
                VerificationStep(
                    step_id=step_id,
                    step_type="check_validation_data",
                    depends_on_step_ids=[],
                    input_refs=[
                        inference.inference_ref,
                        linked_ref.upstream_artifact_ref,
                        contract.phase_contract_id,
                    ],
                    expected_output="accepted real validation evidence remains linked to the path",
                    step_status="completed",
                )
            )
            prior_step_ids.append(step_id)

        for requirement in requirements:
            if requirement.is_satisfied:
                continue
            step_type = _step_type_for_evidence(requirement.evidence_type)
            step_id = f"{path_id}:step_{step_type}_{len(steps) + 1:03d}"
            steps.append(
                VerificationStep(
                    step_id=step_id,
                    step_type=step_type,
                    depends_on_step_ids=list(prior_step_ids),
                    input_refs=[
                        inference.inference_ref,
                        contract.phase_contract_id,
                        requirement.gap_ref or requirement.evidence_requirement_id,
                    ],
                    expected_output=f"{requirement.evidence_type} reaches {requirement.required_level}",
                    step_status="blocked",
                )
            )
            prior_step_ids.append(step_id)

        if not steps:
            steps.append(
                VerificationStep(
                    step_id=f"{path_id}:step_governance_review_001",
                    step_type="governance_review",
                    depends_on_step_ids=[],
                    input_refs=[inference.inference_ref, contract.phase_contract_id],
                    expected_output="confirm no additional evidence hardening is required",
                    step_status="ready",
                )
            )
        return steps

    def _build_agenda(
        self,
        paths: Sequence[VerificationPath],
        gaps: Sequence[EvidenceGap],
        contract: _ContractContext,
    ) -> HardeningAgenda | None:
        if not paths:
            return None
        path_refs = [path.path_id for path in sorted(paths, key=lambda item: item.path_id)]
        sorted_gaps = sorted(gaps, key=lambda item: (item.gap_severity, item.gap_id))
        actions = self._agenda_actions(paths, sorted_gaps, contract.owner_role)
        generated_from_version = _hash_content(
            {
                "path_versions": [path.version_id for path in paths],
                "gap_versions": [gap.version_id for gap in gaps],
                "rule_version": self.rule_version,
            }
        )
        dependency_order = [action.action_id for action in actions]
        blocking_gaps = [gap.gap_id for gap in sorted_gaps if gap.gap_severity == "blocking"]
        review_trigger = "blocking_evidence_gap" if blocking_gaps else "verification_review"
        status = (
            "partially_blocked"
            if blocking_gaps
            else "ready_for_execution"
        )
        lineage_refs = _stable_unique(
            [
                contract.phase_contract_id,
                contract.contract_version,
                *[ref for path in paths for ref in path.lineage_refs],
                *[gap.gap_id for gap in gaps],
            ]
        )
        content = {
            "path_refs": path_refs,
            "prioritized_actions": [action.to_dict() for action in actions],
            "dependency_order": dependency_order,
            "blocking_gaps": blocking_gaps,
            "owner_role": contract.owner_role,
            "review_trigger": review_trigger,
            "generated_from_version": generated_from_version,
            "phase_contract_id": contract.phase_contract_id,
            "contract_version": contract.contract_version,
            "status": status,
            "lineage_refs": lineage_refs,
        }
        version_hash = _hash_content(content)
        agenda_id = (
            "motor_019:hardening_agenda:"
            f"{generated_from_version[:12]}:{version_hash[:12]}"
        )
        return HardeningAgenda(
            agenda_id=agenda_id,
            motor_id=MOTOR_ID,
            path_refs=path_refs,
            prioritized_actions=actions,
            dependency_order=dependency_order,
            blocking_gaps=blocking_gaps,
            owner_role=contract.owner_role,
            review_trigger=review_trigger,
            generated_from_version=generated_from_version,
            phase_contract_id=contract.phase_contract_id,
            contract_version=contract.contract_version,
            status=status,
            lineage_refs=lineage_refs,
            version_id=f"motor_019:v:hardening_agenda:{version_hash[:16]}",
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_hash=version_hash,
            source_ref=f"{','.join(path_refs)}:{generated_from_version}",
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )

    def _agenda_actions(
        self,
        paths: Sequence[VerificationPath],
        gaps: Sequence[EvidenceGap],
        owner_role: str,
    ) -> list[HardeningAction]:
        action_inputs: list[tuple[str, str, str | None, str, str, str, str]] = []
        for path in sorted(paths, key=lambda item: item.path_id):
            for step in path.verification_steps:
                if step.step_type == "check_validation_data":
                    action_inputs.append(
                        (
                            step.step_id,
                            path.path_id,
                            None,
                            "confirm_source",
                            "medium",
                            path.current_evidence_level,
                            "completed",
                        )
                    )
        for gap in gaps:
            action_inputs.append(
                (
                    gap.gap_id,
                    gap.path_id,
                    gap.gap_id,
                    _action_type_for_gap(gap.missing_evidence_type),
                    gap.gap_severity,
                    "field_evidence"
                    if gap.missing_evidence_type == "site_validation"
                    else "validation_data",
                    "ready",
                )
            )

        actions: list[HardeningAction] = []
        prior_action_ids: list[str] = []
        for index, (source_id, path_ref, gap_ref, action_type, priority, level, status) in enumerate(
            sorted(action_inputs, key=_action_sort_key),
            start=1,
        ):
            action_hash = _hash_content(
                {
                    "source_id": source_id,
                    "path_ref": path_ref,
                    "gap_ref": gap_ref,
                    "action_type": action_type,
                    "priority": priority,
                }
            )
            depends_on = list(prior_action_ids) if gap_ref else []
            action_id = f"motor_019:hardening_action:{index:03d}:{action_hash[:10]}"
            actions.append(
                HardeningAction(
                    action_id=action_id,
                    path_ref=path_ref,
                    gap_ref=gap_ref,
                    action_type=action_type,
                    priority=priority,
                    depends_on_action_ids=depends_on,
                    expected_evidence_level=level,
                    owner_role=owner_role,
                    action_status=status,
                )
            )
            prior_action_ids.append(action_id)
        return actions

    def _with_agenda_ref(self, path: VerificationPath, agenda_id: str) -> VerificationPath:
        content = {
            **path.to_dict(),
            "agenda_ref": agenda_id,
        }
        version_hash = _hash_content(content)
        return replace(
            path,
            agenda_ref=agenda_id,
            version_hash=version_hash,
            version_id=f"motor_019:v:verification_path:{version_hash[:16]}",
        )

    def _rejected(self, errors: list[dict[str, Any]]) -> VerificationBridgeResult:
        return VerificationBridgeResult(
            verification_paths=[],
            hardening_agenda=None,
            evidence_gap_records=[],
            errors=errors,
        )


def run_verification_bridge(
    *,
    inference_records: Sequence[Mapping[str, Any]],
    validation_data: Sequence[Mapping[str, Any]],
    phase_contracts: Sequence[Mapping[str, Any]],
    rule_version: str = DEFAULT_RULE_VERSION,
    produced_at: str = DEFAULT_PRODUCED_AT,
) -> VerificationBridgeResult:
    """Convenience function for callers that do not need an engine instance."""

    return VerificationBridgeEngine(
        rule_version=rule_version,
        produced_at=produced_at,
    ).run(
        inference_records=inference_records,
        validation_data=validation_data,
        phase_contracts=phase_contracts,
    )


def _as_record_list(
    field_name: str,
    value: Sequence[Mapping[str, Any]],
) -> tuple[list[Mapping[str, Any]], list[dict[str, Any]]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return [], [
            _validation_error(
                "INVALID_INPUT_TYPE",
                field_name,
                f"input.{field_name}",
                f"{field_name} must be a sequence of mapping records",
            )
        ]
    records: list[Mapping[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(
                _validation_error(
                    "INVALID_INPUT_TYPE",
                    field_name,
                    f"input.{field_name}[{index}]",
                    "record must be a mapping",
                )
            )
            continue
        records.append(item)
    return records, errors


def _validation_error(
    code: str,
    object_ref: str,
    field: str,
    message: str,
) -> dict[str, Any]:
    return {
        "code": code,
        "object_ref": object_ref,
        "field": field,
        "message": message,
    }


def _require_text(value: Any, field: str) -> str:
    text = _text(value)
    if not text:
        raise ValueError(f"{field} must be a non-empty string")
    return text


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) else ""


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        return [value] if value else []
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [item.strip() for item in value if isinstance(item, str) and item.strip()]
    return []


def _flatten_text_values(value: Any) -> list[str]:
    if isinstance(value, str):
        return [value]
    if isinstance(value, Mapping):
        items: list[str] = []
        for nested in value.values():
            items.extend(_flatten_text_values(nested))
        return items
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        items = []
        for nested in value:
            items.extend(_flatten_text_values(nested))
        return items
    return []


def _contains_invalid_marker(values: Sequence[str]) -> bool:
    normalized = {value.strip().lower() for value in values}
    return any(marker in normalized for marker in INVALID_EVIDENCE_MARKERS)


def _target_ref_from_record(record: Mapping[str, Any]) -> tuple[TargetRef, str | None]:
    claim_value = record.get("claim_id")
    tension_value = record.get("tension_id")
    claim_id = _text(claim_value)
    tension_id = _text(tension_value)
    claim_present = claim_value is not None and claim_value != ""
    tension_present = tension_value is not None and tension_value != ""
    if claim_present and not claim_id:
        return TargetRef("claim", None, None), "claim_id must be a string when present"
    if tension_present and not tension_id:
        return TargetRef("tension", None, None), "tension_id must be a string when present"
    if bool(claim_id) == bool(tension_id):
        return (
            TargetRef("claim", claim_id or None, tension_id or None),
            "exactly one of claim_id or tension_id must be supplied",
        )
    if claim_id:
        return (
            TargetRef(
                target_type="claim",
                claim_id=claim_id,
                tension_id=None,
                target_label=_text(record.get("target_label")) or None,
            ),
            None,
        )
    return (
        TargetRef(
            target_type="tension",
            claim_id=None,
            tension_id=tension_id,
            target_label=_text(record.get("target_label")) or None,
        ),
        None,
    )


def _validation_target_tokens(record: Mapping[str, Any]) -> set[str]:
    tokens: set[str] = set()
    direct_fields = (
        "claim_id",
        "tension_id",
        "target_id",
        "target_ref",
        "source_inference_ref",
        "inference_record_id",
        "inference_id",
    )
    list_fields = (
        "claim_ids",
        "tension_ids",
        "target_refs",
        "linked_claim_ids",
        "linked_tension_ids",
        "related_claim_ids",
        "related_tension_ids",
    )
    for field in direct_fields:
        text = _text(record.get(field))
        if text:
            tokens.add(text)
    for field in list_fields:
        tokens.update(_string_list(record.get(field)))
    target_ref = record.get("target_ref")
    if isinstance(target_ref, Mapping):
        tokens.update(_string_list(target_ref.get("claim_id")))
        tokens.update(_string_list(target_ref.get("tension_id")))
        tokens.update(_string_list(target_ref.get("target_id")))
    return tokens


def _has_conflicting_validation(validation_contexts: Sequence[_ValidationContext]) -> bool:
    by_ref = {validation.validation_ref: validation for validation in validation_contexts}
    for validation in validation_contexts:
        conflicts_with = set(_string_list(validation.raw.get("conflicts_with")))
        if conflicts_with.intersection(by_ref):
            return True

    measurements: dict[tuple[str, str], Any] = {}
    for validation in validation_contexts:
        measured_value = validation.raw.get("measured_value")
        if not isinstance(measured_value, Mapping):
            continue
        metric = _text(measured_value.get("metric"))
        unit = _text(measured_value.get("unit"))
        value = measured_value.get("value")
        if not metric:
            continue
        key = (metric, unit)
        if key in measurements and measurements[key] != value:
            return True
        measurements[key] = value
    return False


def _evidence_type_for_gap(gap_text: str) -> str:
    normalized = gap_text.lower()
    if "conflict" in normalized or "reconcile" in normalized:
        return "conflict_resolution"
    if "provenance" in normalized or "lineage" in normalized:
        return "provenance"
    if "source" in normalized or "confirmation" in normalized or "log" in normalized:
        return "source_confirmation"
    if "site" in normalized or "field" in normalized or "validation" in normalized:
        return "site_validation"
    if "observation" in normalized:
        return "observation"
    return "measurement"


def _recommended_action_text(evidence_type: str) -> str:
    actions = {
        "measurement": "collect a real measurement record through motor_018 validation workflow",
        "observation": "obtain a structured observation record with lineage",
        "source_confirmation": "confirm the source record and attach traceable validation data",
        "site_validation": "collect authorized field evidence or site validation data",
        "conflict_resolution": "reconcile conflicting validation records under governance review",
        "provenance": "complete provenance and lineage before evidence hardening",
    }
    return actions[evidence_type]


def _step_type_for_evidence(evidence_type: str) -> str:
    mapping = {
        "measurement": "check_validation_data",
        "observation": "confirm_source",
        "source_confirmation": "confirm_source",
        "site_validation": "collect_field_evidence",
        "conflict_resolution": "reconcile_conflict",
        "provenance": "confirm_source",
    }
    return mapping[evidence_type]


def _action_type_for_gap(evidence_type: str) -> str:
    mapping = {
        "measurement": "collect_measurement",
        "observation": "obtain_observation",
        "source_confirmation": "confirm_source",
        "site_validation": "obtain_observation",
        "conflict_resolution": "reconcile_conflict",
        "provenance": "complete_provenance",
    }
    return mapping[evidence_type]


def _action_sort_key(item: tuple[str, str, str | None, str, str, str, str]) -> tuple[int, str]:
    priority_order = {"blocking": 0, "high": 1, "medium": 2, "low": 3}
    source_id, _path_ref, _gap_ref, _action_type, priority, _level, _status = item
    return priority_order.get(priority, 4), source_id


def _review_trigger(gaps: Sequence[EvidenceGap], has_conflict: bool) -> str | None:
    if has_conflict:
        return "conflicting_validation_data"
    if any(gap.gap_severity == "blocking" for gap in gaps):
        return "blocking_evidence_gap"
    return None


def _path_status(
    current_level: str,
    target_level: str,
    has_gaps: bool,
    has_conflict: bool,
) -> str:
    if has_conflict:
        return "blocked"
    if EVIDENCE_RANK[current_level] >= EVIDENCE_RANK[target_level] and not has_gaps:
        return "verified_evidence_ready"
    if current_level in REAL_EVIDENCE_LEVELS:
        return "actionable"
    return "blocked"


def min_level(level_a: str, level_b: str) -> str:
    return level_a if EVIDENCE_RANK[level_a] <= EVIDENCE_RANK[level_b] else level_b


def _stable_unique(values: Sequence[str]) -> list[str]:
    return sorted({value for value in values if value})


def _hash_content(value: Any) -> str:
    encoded = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(encoded.encode("utf-8")).hexdigest()
