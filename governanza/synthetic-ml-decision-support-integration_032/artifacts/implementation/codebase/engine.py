"""Deterministic implementation of motor_032.

Synthetic ML Decision Support Integration accepts a motor_031 capability
demonstration report, verifies that the Decision Core phase allows synthetic
support only as a subordinate signal, and emits an atomic bundle of labeled,
non-evidentiary support objects. The implementation performs no AI calls, no
model work, no validation bridge work, and no mutation of upstream objects.
"""

from __future__ import annotations

from collections.abc import Iterable, Mapping
from copy import deepcopy
import hashlib
import json
import re
from typing import Any

try:
    from .errors import (
        AmbiguousTargetInferenceRecordError,
        InvalidFieldTypeError,
        InvalidInputSchemaError,
        MissingEpistemicFlagsError,
        MissingLineageReferenceError,
        MissingRequiredFieldError,
        Motor032Error,
        NoTargetInferenceRecordError,
        OutputInvariantError,
        PhaseContractDisallowsSyntheticSupportError,
        PromotionRequestForbiddenError,
    )
    from .models import (
        CANNOT_SUBSTITUTE,
        DEFAULT_INTENDED_USE,
        DESTINATION_CONSUMERS,
        HANDOFF_LABELS,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        PERMITTED_EFFECTS,
        REJECTION_BOUNDARIES,
        SUPPORT_LEVELS,
        SYNTHETIC_SUPPORT_FLAG,
        HypothesisSignal,
        IntegrationResult,
        LabeledSupportRecord,
        SyntheticMLSupportRegister,
    )
except ImportError:  # pragma: no cover - supports direct execution from codebase/
    from errors import (
        AmbiguousTargetInferenceRecordError,
        InvalidFieldTypeError,
        InvalidInputSchemaError,
        MissingEpistemicFlagsError,
        MissingLineageReferenceError,
        MissingRequiredFieldError,
        Motor032Error,
        NoTargetInferenceRecordError,
        OutputInvariantError,
        PhaseContractDisallowsSyntheticSupportError,
        PromotionRequestForbiddenError,
    )
    from models import (
        CANNOT_SUBSTITUTE,
        DEFAULT_INTENDED_USE,
        DESTINATION_CONSUMERS,
        HANDOFF_LABELS,
        MOTOR_ID,
        NON_EVIDENTIARY_FLAG,
        PERMITTED_EFFECTS,
        REJECTION_BOUNDARIES,
        SUPPORT_LEVELS,
        SYNTHETIC_SUPPORT_FLAG,
        HypothesisSignal,
        IntegrationResult,
        LabeledSupportRecord,
        SyntheticMLSupportRegister,
    )


REQUIRED_REPORT_STRINGS = [
    "report_id",
    "source_problem_ref",
    "expert_spec_ref",
    "generator_version",
    "gap_to_real_validation",
    "gap_to_deployment",
    "domain_validity_limits",
    "limitations_note",
]

UPSTREAM_VERSION_KEYS = {
    "capability_report": [
        "capability_report",
        "capability_demonstration_report",
        "source_report",
        "capability_report_version",
        "source_report_version",
    ],
    "inference_record": [
        "inference_record",
        "target_inference_record",
        "inference_record_version",
        "target_inference_record_version",
    ],
    "phase_contract": [
        "phase_contract",
        "phase_contract_ref",
        "phase_contract_version",
    ],
}

LINEAGE_KEYS = ["lineage_id", "lineage", "support_lineage_id", "emitted_lineage_id"]
SOURCE_REF_KEYS = ["source_ref", "lineage_ref", "source_lineage_ref"]

FORBIDDEN_TRUE_FIELDS = {
    "decision_grade_change_allowed",
    "claim_closure_requested",
    "close_claim",
    "close_inference_case",
    "field_validation_claimed",
    "final_tad_requested",
    "produce_final_tad",
    "promote_to_decision_grade",
    "validation_data_replacement_requested",
    "verification_bridge_replacement_requested",
    "substitute_validation_data",
    "substitute_verification_bridge",
}

FORBIDDEN_EVIDENCE_LEVELS = {
    "decision_grade",
    "field_evidence",
    "validation_data",
    "verified_evidence",
    "verification_evidence",
}


class SyntheticMLDecisionSupportIntegration:
    """Core deterministic motor_032 implementation."""

    def run(
        self,
        *,
        capability_demonstration_report: dict[str, Any],
        inference_records: Any,
        phase_contracts: Any,
        version_records: dict[str, Any],
        target_inference_case_id: str | None = None,
        target_inference_record_id: str | None = None,
        support_level: str | None = None,
        permitted_effect: str | None = None,
        produced_at: str | None = None,
        parent_ids: dict[str, str | None] | None = None,
    ) -> dict[str, Any]:
        """Integrate synthetic capability support or return a structured rejection."""

        try:
            bundle = self._validated_bundle(
                capability_demonstration_report=capability_demonstration_report,
                inference_records=inference_records,
                phase_contracts=phase_contracts,
                version_records=version_records,
                target_inference_case_id=target_inference_case_id,
                target_inference_record_id=target_inference_record_id,
                support_level=support_level,
                permitted_effect=permitted_effect,
                parent_ids=parent_ids,
            )
            emitted_at = self._resolved_timestamp(
                explicit=produced_at,
                report=bundle["report"],
                version_records=bundle["version_records"],
            )
            result = self._build_result(bundle=bundle, produced_at=emitted_at)
            self._validate_output_bundle(result)
            return result.to_dict()
        except Motor032Error as rejection:
            return {
                "status": "rejected",
                "error_code": rejection.error_code,
                "message": str(rejection),
                "field_paths": rejection.field_paths,
                "details": rejection.details,
                "synthetic_ml_support_register": None,
                "hypothesis_signal": None,
                "labeled_support_record": None,
            }

    def _validated_bundle(
        self,
        *,
        capability_demonstration_report: dict[str, Any],
        inference_records: Any,
        phase_contracts: Any,
        version_records: dict[str, Any],
        target_inference_case_id: str | None,
        target_inference_record_id: str | None,
        support_level: str | None,
        permitted_effect: str | None,
        parent_ids: dict[str, str | None] | None,
    ) -> dict[str, Any]:
        if not isinstance(capability_demonstration_report, Mapping):
            raise InvalidInputSchemaError(
                "capability_demonstration_report must be a mapping",
                field_paths=["capability_demonstration_report"],
            )
        if not isinstance(version_records, Mapping):
            raise InvalidInputSchemaError(
                "version_records must be a mapping",
                field_paths=["version_records"],
            )
        if parent_ids is not None and not isinstance(parent_ids, Mapping):
            raise InvalidInputSchemaError(
                "parent_ids must be a mapping when supplied",
                field_paths=["parent_ids"],
            )

        report = deepcopy(dict(capability_demonstration_report))
        versions = deepcopy(dict(version_records))
        parents = deepcopy(dict(parent_ids)) if parent_ids else {}

        self._reject_promotion_requests(
            {
                "capability_demonstration_report": report,
                "inference_records": inference_records,
                "phase_contracts": phase_contracts,
            }
        )
        self._validate_report(report)

        target_record = self._target_inference_record(
            inference_records=inference_records,
            source_problem_ref=report["source_problem_ref"],
            target_inference_case_id=target_inference_case_id,
            target_inference_record_id=target_inference_record_id,
        )
        phase_contract = self._phase_contract(phase_contracts)
        phase_contract_ref = self._contract_ref(phase_contract)
        upstream_refs = self._upstream_version_refs(
            versions=versions,
            report=report,
            target_record=target_record,
            phase_contract=phase_contract,
            phase_contract_ref=phase_contract_ref,
        )
        selected_support_level = self._support_level(
            supplied=support_level,
            report=report,
        )
        selected_permitted_effect = self._permitted_effect(
            supplied=permitted_effect,
            support_level=selected_support_level,
        )
        source_ref = self._source_ref(report=report, versions=versions)

        return {
            "report": report,
            "target_record": target_record,
            "phase_contract": phase_contract,
            "phase_contract_ref": phase_contract_ref,
            "version_records": versions,
            "source_ref": source_ref,
            "upstream_refs": upstream_refs,
            "lineage_id": self._lineage_id(versions),
            "support_level": selected_support_level,
            "permitted_effect": selected_permitted_effect,
            "parent_ids": parents,
        }

    def _validate_report(self, report: dict[str, Any]) -> None:
        missing = [
            f"capability_demonstration_report.{field}"
            for field in REQUIRED_REPORT_STRINGS
            if not self._non_empty_string(report.get(field))
        ]
        if missing:
            raise MissingRequiredFieldError(
                "capability demonstration report is missing required fields",
                field_paths=missing,
            )

        if report.get("non_evidentiary_flag") is not True:
            raise MissingEpistemicFlagsError(
                "capability demonstration report must declare non_evidentiary_flag=true",
                field_paths=["capability_demonstration_report.non_evidentiary_flag"],
            )
        if report.get("synthetic_data_flag") is not True:
            raise MissingEpistemicFlagsError(
                "capability demonstration report must declare synthetic_data_flag=true",
                field_paths=["capability_demonstration_report.synthetic_data_flag"],
            )

        known_failure_modes = report.get("known_failure_modes")
        if not isinstance(known_failure_modes, list):
            raise InvalidFieldTypeError(
                "known_failure_modes must be a list of strings",
                field_paths=["capability_demonstration_report.known_failure_modes"],
                details={"field": "known_failure_modes"},
            )
        if not known_failure_modes:
            raise MissingRequiredFieldError(
                "known_failure_modes must not be empty",
                field_paths=["capability_demonstration_report.known_failure_modes"],
            )
        if any(not self._non_empty_string(item) for item in known_failure_modes):
            raise InvalidFieldTypeError(
                "known_failure_modes must contain only non-empty strings",
                field_paths=["capability_demonstration_report.known_failure_modes"],
                details={"field": "known_failure_modes"},
            )

    def _target_inference_record(
        self,
        *,
        inference_records: Any,
        source_problem_ref: str,
        target_inference_case_id: str | None,
        target_inference_record_id: str | None,
    ) -> dict[str, Any]:
        records = self._as_record_list(
            inference_records,
            "inference_records",
        )
        if target_inference_case_id and target_inference_case_id != source_problem_ref:
            raise NoTargetInferenceRecordError(
                "explicit target case must match report source_problem_ref",
                field_paths=[
                    "target_inference_case_id",
                    "capability_demonstration_report.source_problem_ref",
                ],
            )

        exact_matches = [
            record
            for record in records
            if record.get("inference_case_id") == source_problem_ref
        ]
        if target_inference_record_id:
            exact_matches = [
                record
                for record in exact_matches
                if record.get("inference_record_id") == target_inference_record_id
            ]

        if not exact_matches:
            raise NoTargetInferenceRecordError(
                "no inference record has an exact inference_case_id match",
                field_paths=["inference_records[].inference_case_id"],
                details={"source_problem_ref": source_problem_ref},
            )
        if len(exact_matches) > 1:
            raise AmbiguousTargetInferenceRecordError(
                "more than one inference record matches the source_problem_ref",
                field_paths=["inference_records[].inference_case_id"],
                details={"source_problem_ref": source_problem_ref},
            )

        target = deepcopy(exact_matches[0])
        if not self._non_empty_string(target.get("inference_record_id")):
            raise MissingRequiredFieldError(
                "target inference record must have inference_record_id",
                field_paths=["inference_records[].inference_record_id"],
            )
        return target

    def _phase_contract(self, phase_contracts: Any) -> dict[str, Any]:
        contracts = self._as_record_list(phase_contracts, "phase_contracts")
        allowed_contracts = [
            contract
            for contract in contracts
            if "synthetic_support"
            in self._string_list(
                contract.get("allowed_subordinate_signal_classes")
                or contract.get("allowed_subordinate_signals")
                or contract.get("accepted_subordinate_signal_classes")
                or contract.get("accepted_signal_classes")
            )
        ]
        if not allowed_contracts:
            raise PhaseContractDisallowsSyntheticSupportError(
                "phase contract does not allow subordinate synthetic_support",
                field_paths=[
                    "phase_contracts[].allowed_subordinate_signal_classes",
                ],
            )
        return deepcopy(allowed_contracts[0])

    def _contract_ref(self, phase_contract: dict[str, Any]) -> str:
        for field in ["phase_contract_ref", "contract_ref", "phase_contract_id", "id"]:
            value = phase_contract.get(field)
            if self._non_empty_string(value):
                return str(value)
        raise MissingRequiredFieldError(
            "phase contract must provide a stable phase_contract_ref",
            field_paths=["phase_contracts[].phase_contract_ref"],
        )

    def _upstream_version_refs(
        self,
        *,
        versions: dict[str, Any],
        report: dict[str, Any],
        target_record: dict[str, Any],
        phase_contract: dict[str, Any],
        phase_contract_ref: str,
    ) -> dict[str, str]:
        capability_report_version = self._version_value(
            versions,
            UPSTREAM_VERSION_KEYS["capability_report"],
            report.get("report_id"),
        )
        inference_record_version = self._version_value(
            versions,
            UPSTREAM_VERSION_KEYS["inference_record"],
            target_record.get("inference_record_id"),
        )
        phase_contract_version = self._version_value(
            versions,
            UPSTREAM_VERSION_KEYS["phase_contract"],
            phase_contract_ref,
            phase_contract.get("version_id"),
        )
        missing = []
        if not capability_report_version:
            missing.append("version_records.capability_report")
        if not inference_record_version:
            missing.append("version_records.inference_record")
        if not phase_contract_version:
            missing.append("version_records.phase_contract")
        if missing:
            raise MissingLineageReferenceError(
                "version_records must include stable upstream version references",
                field_paths=missing,
            )
        return {
            "capability_report": str(capability_report_version),
            "inference_record": str(inference_record_version),
            "phase_contract": str(phase_contract_version),
        }

    def _lineage_id(self, versions: dict[str, Any]) -> str:
        for key in LINEAGE_KEYS:
            value = versions.get(key)
            if self._non_empty_string(value):
                return str(value)
        raise MissingLineageReferenceError(
            "version_records must include a lineage_id for emitted motor_032 objects",
            field_paths=["version_records.lineage_id"],
        )

    def _source_ref(self, *, report: dict[str, Any], versions: dict[str, Any]) -> str:
        for container, prefix in [(report, "capability_demonstration_report"), (versions, "version_records")]:
            for key in SOURCE_REF_KEYS:
                value = container.get(key)
                if self._non_empty_string(value):
                    return str(value)
        raise MissingLineageReferenceError(
            "source_ref must be supplied by the report or version records",
            field_paths=[
                "capability_demonstration_report.source_ref",
                "version_records.source_ref",
            ],
        )

    def _support_level(self, *, supplied: str | None, report: dict[str, Any]) -> str:
        candidate = supplied or report.get("support_level")
        if candidate is None:
            status = str(report.get("demonstration_status", "")).lower()
            candidate = "exploratory" if status in {"weak", "not_demonstrated"} else "capability_demo"
        if candidate not in SUPPORT_LEVELS:
            raise InvalidFieldTypeError(
                "support_level must be exploratory, preliminary_signal, or capability_demo",
                field_paths=["support_level"],
                details={"value": candidate},
            )
        return str(candidate)

    def _permitted_effect(self, *, supplied: str | None, support_level: str) -> str:
        candidate = supplied or (
            "exploration" if support_level == "exploratory" else "preliminary_prioritization"
        )
        if candidate not in PERMITTED_EFFECTS:
            raise PromotionRequestForbiddenError(
                "permitted_effect cannot request decision grade, closure, validation, or verification",
                field_paths=["permitted_effect"],
                details={"value": candidate},
            )
        return str(candidate)

    def _build_result(
        self,
        *,
        bundle: dict[str, Any],
        produced_at: str,
    ) -> IntegrationResult:
        report = bundle["report"]
        target = bundle["target_record"]
        parents = bundle["parent_ids"]
        source_report_id = str(report["report_id"])
        target_record_id = str(target["inference_record_id"])
        source_problem_ref = str(report["source_problem_ref"])
        expert_spec_ref = str(report["expert_spec_ref"])
        phase_contract_ref = bundle["phase_contract_ref"]
        source_ref = bundle["source_ref"]
        lineage_id = bundle["lineage_id"]
        upstream_refs = bundle["upstream_refs"]
        support_level = bundle["support_level"]
        permitted_effect = bundle["permitted_effect"]

        support_register_id = self._object_id(
            prefix="smr",
            source_report_id=source_report_id,
            target_record_id=target_record_id,
            parent_id=parents.get("support_register_id"),
        )
        hypothesis_signal_id = self._object_id(
            prefix="hs",
            source_report_id=source_report_id,
            target_record_id=target_record_id,
            parent_id=parents.get("hypothesis_signal_id"),
        )
        labeled_support_record_id = self._object_id(
            prefix="lsr",
            source_report_id=source_report_id,
            target_record_id=target_record_id,
            parent_id=parents.get("labeled_support_record_id"),
        )

        base_versions = dict(upstream_refs)
        register_version_id = self._stable_label(
            "smr_v",
            {
                "support_register_id": support_register_id,
                "upstream_refs": upstream_refs,
                "lineage_id": lineage_id,
            },
        )
        register_version_refs = {
            **base_versions,
            "support_register": register_version_id,
        }
        register_payload = {
            "support_register_id": support_register_id,
            "source_report_id": source_report_id,
            "source_ref": source_ref,
            "source_problem_ref": source_problem_ref,
            "expert_spec_ref": expert_spec_ref,
            "target_inference_record_id": target_record_id,
            "phase_contract_ref": phase_contract_ref,
            "version_refs": register_version_refs,
            "generator_version": str(report["generator_version"]),
            "support_level": support_level,
            "intended_use": DEFAULT_INTENDED_USE,
            "domain_validity_limits": str(report["domain_validity_limits"]),
            "limitations_note": str(report["limitations_note"]),
            "gap_to_real_validation": str(report["gap_to_real_validation"]),
            "gap_to_deployment": str(report["gap_to_deployment"]),
            "known_failure_modes": list(report["known_failure_modes"]),
            "cannot_substitute": list(CANNOT_SUBSTITUTE),
            "lineage_id": lineage_id,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parents.get("support_register_id"),
            "version_id": register_version_id,
            "created_at": produced_at,
            "updated_at": produced_at,
        }
        register = SyntheticMLSupportRegister(
            **register_payload,
            version_hash=self._stable_hash(register_payload),
        )

        signal_version_id = self._stable_label(
            "hs_v",
            {
                "hypothesis_signal_id": hypothesis_signal_id,
                "support_register_version": register.version_id,
                "lineage_id": lineage_id,
            },
        )
        signal_version_refs = {
            **register.version_refs,
            "hypothesis_signal": signal_version_id,
        }
        signal_payload = {
            "hypothesis_signal_id": hypothesis_signal_id,
            "support_register_id": support_register_id,
            "source_report_id": source_report_id,
            "source_ref": source_ref,
            "source_problem_ref": source_problem_ref,
            "expert_spec_ref": expert_spec_ref,
            "target_inference_record_id": target_record_id,
            "signal_role": "subordinate",
            "evidence_level": "synthetic_support",
            "intended_use": DEFAULT_INTENDED_USE,
            "permitted_effect": permitted_effect,
            "decision_grade_change_allowed": False,
            "domain_validity_limits": register.domain_validity_limits,
            "limitations_note": register.limitations_note,
            "version_refs": signal_version_refs,
            "lineage_id": lineage_id,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parents.get("hypothesis_signal_id"),
            "version_id": signal_version_id,
            "created_at": produced_at,
            "updated_at": produced_at,
        }
        signal = HypothesisSignal(
            **signal_payload,
            version_hash=self._stable_hash(signal_payload),
        )

        record_version_id = self._stable_label(
            "lsr_v",
            {
                "labeled_support_record_id": labeled_support_record_id,
                "support_register_version": register.version_id,
                "hypothesis_signal_version": signal.version_id,
                "lineage_id": lineage_id,
            },
        )
        record_version_refs = {
            **signal.version_refs,
            "labeled_support_record": record_version_id,
        }
        record_payload = {
            "labeled_support_record_id": labeled_support_record_id,
            "support_register_id": support_register_id,
            "hypothesis_signal_id": hypothesis_signal_id,
            "source_report_id": source_report_id,
            "source_ref": source_ref,
            "source_problem_ref": source_problem_ref,
            "expert_spec_ref": expert_spec_ref,
            "target_inference_record_id": target_record_id,
            "labels": list(HANDOFF_LABELS),
            "support_level": support_level,
            "intended_use": DEFAULT_INTENDED_USE,
            "destination_consumers": list(DESTINATION_CONSUMERS),
            "rejection_boundaries": list(REJECTION_BOUNDARIES),
            "cannot_substitute": list(CANNOT_SUBSTITUTE),
            "upstream_version_refs": [
                upstream_refs["capability_report"],
                upstream_refs["inference_record"],
                upstream_refs["phase_contract"],
            ],
            "version_refs": record_version_refs,
            "generator_version": str(report["generator_version"]),
            "domain_validity_limits": register.domain_validity_limits,
            "limitations_note": register.limitations_note,
            "lineage_id": lineage_id,
            "synthetic_support_flag": SYNTHETIC_SUPPORT_FLAG,
            "non_evidentiary_flag": NON_EVIDENTIARY_FLAG,
            "produced_by_motor": MOTOR_ID,
            "produced_at": produced_at,
            "parent_id": parents.get("labeled_support_record_id"),
            "version_id": record_version_id,
            "created_at": produced_at,
            "updated_at": produced_at,
        }
        labeled_record = LabeledSupportRecord(
            **record_payload,
            version_hash=self._stable_hash(record_payload),
        )

        return IntegrationResult(
            synthetic_ml_support_register=register,
            hypothesis_signal=signal,
            labeled_support_record=labeled_record,
        )

    def _validate_output_bundle(self, result: IntegrationResult) -> None:
        objects = [
            result.synthetic_ml_support_register.to_dict(),
            result.hypothesis_signal.to_dict(),
            result.labeled_support_record.to_dict(),
        ]
        for output in objects:
            if output.get("synthetic_support_flag") is not True:
                raise OutputInvariantError(
                    "emitted object lost synthetic_support_flag=true",
                    field_paths=["synthetic_support_flag"],
                )
            if output.get("non_evidentiary_flag") is not True:
                raise OutputInvariantError(
                    "emitted object lost non_evidentiary_flag=true",
                    field_paths=["non_evidentiary_flag"],
                )
            if output.get("produced_by_motor") != MOTOR_ID:
                raise OutputInvariantError(
                    "emitted object has wrong produced_by_motor",
                    field_paths=["produced_by_motor"],
                )
            for required in [
                "source_problem_ref",
                "expert_spec_ref",
                "source_ref",
                "lineage_id",
                "version_id",
                "version_hash",
                "domain_validity_limits",
                "limitations_note",
            ]:
                if not self._non_empty_string(output.get(required)):
                    raise OutputInvariantError(
                        "emitted object is missing required output metadata",
                        field_paths=[required],
                    )

        signal = result.hypothesis_signal
        if (
            signal.signal_role != "subordinate"
            or signal.evidence_level != "synthetic_support"
            or signal.decision_grade_change_allowed is not False
        ):
            raise OutputInvariantError(
                "hypothesis signal is not subordinate synthetic support",
                field_paths=[
                    "hypothesis_signal.signal_role",
                    "hypothesis_signal.evidence_level",
                    "hypothesis_signal.decision_grade_change_allowed",
                ],
            )

        register = result.synthetic_ml_support_register
        labeled = result.labeled_support_record
        for required in CANNOT_SUBSTITUTE:
            if required not in register.cannot_substitute:
                raise OutputInvariantError(
                    "register cannot_substitute is missing a required boundary",
                    field_paths=["synthetic_ml_support_register.cannot_substitute"],
                    details={"missing_boundary": required},
                )
            if required not in labeled.cannot_substitute:
                raise OutputInvariantError(
                    "labeled support record cannot_substitute is missing a boundary",
                    field_paths=["labeled_support_record.cannot_substitute"],
                    details={"missing_boundary": required},
                )

    def _reject_promotion_requests(self, payload: Any) -> None:
        for path, key, value in self._walk_payload(payload):
            normalized_key = key.lower()
            if normalized_key in FORBIDDEN_TRUE_FIELDS and value is True:
                raise PromotionRequestForbiddenError(
                    "input requests a forbidden promotion, closure, validation, or replacement operation",
                    field_paths=[path],
                    details={"field": key},
                )
            if normalized_key in {"evidence_level", "requested_evidence_level"}:
                if str(value).lower() in FORBIDDEN_EVIDENCE_LEVELS:
                    raise PromotionRequestForbiddenError(
                        "input requests a forbidden evidence level",
                        field_paths=[path],
                        details={"field": key, "value": value},
                    )

    def _walk_payload(self, payload: Any, path: str = "") -> Iterable[tuple[str, str, Any]]:
        if isinstance(payload, Mapping):
            for key, value in payload.items():
                child_path = f"{path}.{key}" if path else str(key)
                yield child_path, str(key), value
                yield from self._walk_payload(value, child_path)
        elif isinstance(payload, list):
            for index, item in enumerate(payload):
                yield from self._walk_payload(item, f"{path}[{index}]")

    def _as_record_list(self, value: Any, field_path: str) -> list[dict[str, Any]]:
        if isinstance(value, Mapping):
            if isinstance(value.get("records"), list):
                candidate_records = value["records"]
            elif isinstance(value.get("items"), list):
                candidate_records = value["items"]
            elif all(isinstance(item, Mapping) for item in value.values()):
                candidate_records = list(value.values())
            else:
                candidate_records = [value]
        elif isinstance(value, list):
            candidate_records = value
        else:
            raise InvalidInputSchemaError(
                f"{field_path} must be a list or mapping collection",
                field_paths=[field_path],
            )

        records: list[dict[str, Any]] = []
        for index, record in enumerate(candidate_records):
            if not isinstance(record, Mapping):
                raise InvalidInputSchemaError(
                    f"{field_path} entries must be mappings",
                    field_paths=[f"{field_path}[{index}]"],
                )
            records.append(deepcopy(dict(record)))
        return records

    def _version_value(
        self,
        versions: dict[str, Any],
        keys: list[str],
        object_id: Any,
        fallback: Any = None,
    ) -> str | None:
        for key in keys:
            value = versions.get(key)
            if self._non_empty_string(value):
                return str(value)
        if object_id is not None:
            value = versions.get(str(object_id))
            if self._non_empty_string(value):
                return str(value)
        if self._non_empty_string(fallback):
            return str(fallback)
        return None

    def _resolved_timestamp(
        self,
        *,
        explicit: str | None,
        report: dict[str, Any],
        version_records: dict[str, Any],
    ) -> str:
        for candidate in [
            explicit,
            report.get("produced_at"),
            report.get("created_at"),
            version_records.get("produced_at"),
            version_records.get("created_at"),
        ]:
            if self._non_empty_string(candidate):
                return str(candidate)
        return "1970-01-01T00:00:00Z"

    def _object_id(
        self,
        *,
        prefix: str,
        source_report_id: str,
        target_record_id: str,
        parent_id: str | None,
    ) -> str:
        base = (
            f"{prefix}-032-"
            f"{self._clean_component(source_report_id)}-"
            f"{self._clean_component(target_record_id)}"
        )
        if self._non_empty_string(parent_id):
            return f"{base}-corr-{self._stable_hash({'parent_id': parent_id})[:8]}"
        return base

    def _stable_label(self, prefix: str, payload: dict[str, Any]) -> str:
        return f"{prefix}-{self._stable_hash(payload)[:12]}"

    def _stable_hash(self, payload: dict[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(canonical.encode("utf-8")).hexdigest()

    def _clean_component(self, value: str) -> str:
        return re.sub(r"[^a-zA-Z0-9_-]+", "-", value).strip("-").lower()

    def _string_list(self, value: Any) -> list[str]:
        if not isinstance(value, list):
            return []
        return [item for item in value if isinstance(item, str)]

    def _non_empty_string(self, value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())


def integrate_synthetic_ml_support(
    *,
    capability_demonstration_report: dict[str, Any],
    inference_records: Any,
    phase_contracts: Any,
    version_records: dict[str, Any],
    target_inference_case_id: str | None = None,
    target_inference_record_id: str | None = None,
    support_level: str | None = None,
    permitted_effect: str | None = None,
    produced_at: str | None = None,
    parent_ids: dict[str, str | None] | None = None,
) -> dict[str, Any]:
    """Functional entry point for motor_032."""

    return SyntheticMLDecisionSupportIntegration().run(
        capability_demonstration_report=capability_demonstration_report,
        inference_records=inference_records,
        phase_contracts=phase_contracts,
        version_records=version_records,
        target_inference_case_id=target_inference_case_id,
        target_inference_record_id=target_inference_record_id,
        support_level=support_level,
        permitted_effect=permitted_effect,
        produced_at=produced_at,
        parent_ids=parent_ids,
    )
