"""Deterministic Evaluation / Conformance Engine for motor_022.

The engine checks one evaluated object/version against phase-contract authority,
version lineage, quality evidence, and harness evidence. It is read-only over all
upstream inputs and emits conformance records, violation records, and optional
drift signals without correcting or mutating the system under evaluation.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .errors import ConformanceInputError, UnsafeConformanceOutputError
from .models import ConformanceRecord, DriftSignal, ViolationRecord


MOTOR_ID = "motor_022"
DEFAULT_CONFORMANCE_VERSION = "motor_022.conformance.v1"
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
STATUS_VALUES = {"PASS", "WARNING", "FAIL"}
OBJECT_TYPES = {"motor", "dataset", "artifact", "handoff", "phase"}
SEVERITY_ORDER = {"LOW": 1, "MEDIUM": 2, "HIGH": 3, "CRITICAL": 4}


class EvaluationConformanceEngine:
    """Evaluate formal conformance for a single object/version input bundle."""

    def __init__(self, conformance_version: str = DEFAULT_CONFORMANCE_VERSION) -> None:
        self.conformance_version = (
            str(conformance_version).strip() or DEFAULT_CONFORMANCE_VERSION
        )

    def run(
        self,
        *,
        phase_contracts: Sequence[Mapping[str, Any]],
        version_records: Sequence[Mapping[str, Any]],
        quality_records: Sequence[Mapping[str, Any]],
        harness_results: Sequence[Mapping[str, Any]],
        evaluated_object_id: Optional[str] = None,
        evaluated_version_id: Optional[str] = None,
        evaluated_object_type: str = "dataset",
        evaluated_artifact: Optional[Mapping[str, Any]] = None,
        prior_violation_log: Optional[Sequence[Mapping[str, Any]]] = None,
        evaluated_at: str = DEFAULT_TIMESTAMP,
        parent_id: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Return the contract-shaped conformance output bundle.

        Required inputs match the functional contract. Optional context only
        narrows target selection, supplies observed boundary evidence, or links
        prior violations used for deterministic drift detection.
        """

        input_snapshot = deepcopy(
            {
                "phase_contracts": phase_contracts,
                "version_records": version_records,
                "quality_records": quality_records,
                "harness_results": harness_results,
                "evaluated_artifact": evaluated_artifact,
                "prior_violation_log": prior_violation_log,
            }
        )

        accepted = self._validate_and_index_inputs(
            phase_contracts=phase_contracts,
            version_records=version_records,
            quality_records=quality_records,
            harness_results=harness_results,
            prior_violation_log=prior_violation_log,
        )

        object_type = self._normalize_object_type(evaluated_object_type)
        object_id, version_id = self._resolve_target(
            accepted,
            evaluated_object_id=evaluated_object_id,
            evaluated_version_id=evaluated_version_id,
        )
        version_record = self._require_version_record(accepted, object_id, version_id)
        contract = self._require_contract(
            accepted["phase_contracts"],
            object_id=object_id,
            object_type=object_type,
            evaluated_artifact=evaluated_artifact,
        )

        contract_id = self._string_field(contract, "contract_id")
        contract_version_id = self._contract_version_id(contract)
        record_id = self._record_id(
            object_type=object_type,
            object_id=object_id,
            version_id=version_id,
            contract_id=contract_id,
            contract_version_id=contract_version_id,
        )
        source_ref = f"{object_id}@{version_id}"

        target_quality = accepted["quality_by_key"].get((object_id, version_id), [])
        target_harness = accepted["harness_by_key"].get((object_id, version_id), [])
        quality_record_ids = [self._quality_record_id(record) for record in target_quality]
        harness_result_ids = [self._harness_result_id(record) for record in target_harness]
        evidence_refs = self._collect_evidence_refs(
            contract=contract,
            version_record=version_record,
            quality_records=target_quality,
            harness_results=target_harness,
        )

        violations: List[ViolationRecord] = []
        violations.extend(
            self._lineage_violations(
                record_id=record_id,
                object_id=object_id,
                version_id=version_id,
                version_record=version_record,
                timestamp=evaluated_at,
            )
        )
        violations.extend(
            self._quality_violations(
                record_id=record_id,
                object_id=object_id,
                version_id=version_id,
                quality_records=target_quality,
                timestamp=evaluated_at,
            )
        )
        violations.extend(
            self._harness_violations(
                record_id=record_id,
                object_id=object_id,
                version_id=version_id,
                harness_results=target_harness,
                timestamp=evaluated_at,
            )
        )
        violations.extend(
            self._boundary_violations(
                record_id=record_id,
                object_id=object_id,
                version_id=version_id,
                contract=contract,
                evaluated_artifact=evaluated_artifact,
                timestamp=evaluated_at,
            )
        )

        if not target_quality:
            violations.append(
                self._make_violation(
                    conformance_record_id=record_id,
                    evaluated_object_id=object_id,
                    evaluated_version_id=version_id,
                    violation_type="missing_evidence",
                    rule_ref="quality_records.required_when_available",
                    severity="LOW",
                    input_ref=f"quality_records:{object_id}@{version_id}",
                    expected_condition="quality_evidence_present_or_declared_not_applicable",
                    observed_value="quality_records_absent_for_evaluated_version",
                    material=False,
                    evidence_refs=[f"quality_records:{object_id}@{version_id}:missing"],
                    timestamp=evaluated_at,
                )
            )
        if not target_harness:
            violations.append(
                self._make_violation(
                    conformance_record_id=record_id,
                    evaluated_object_id=object_id,
                    evaluated_version_id=version_id,
                    violation_type="missing_evidence",
                    rule_ref=f"handoff.{object_id}.harness_evidence_expected_when_available",
                    severity="LOW",
                    input_ref=f"harness_results:{object_id}@{version_id}",
                    expected_condition="harness_result_present_when_available_for_target_version",
                    observed_value="harness_results_absent_for_evaluated_version",
                    material=False,
                    evidence_refs=[f"harness_results:{object_id}@{version_id}:missing"],
                    timestamp=evaluated_at,
                )
            )

        violation_ids = [violation.violation_id for violation in violations]
        drift_signal = self._build_drift_signal(
            object_type=object_type,
            object_id=object_id,
            record_id=record_id,
            violations=violations,
            prior_violation_log=accepted["prior_violation_log"],
            timestamp=evaluated_at,
        )
        drift_signal_ids = [drift_signal.signal_id] if drift_signal else []
        status, status_reason = self._status_from_violations(violations)

        record = self._make_conformance_record(
            record_id=record_id,
            evaluated_object_id=object_id,
            evaluated_object_type=object_type,
            evaluated_version_id=version_id,
            contract_id=contract_id,
            contract_version_id=contract_version_id,
            lineage_id=self._string_field(version_record, "lineage_id", allow_empty=True),
            quality_record_ids=quality_record_ids,
            harness_result_ids=harness_result_ids,
            status=status,
            status_reason=status_reason,
            violation_ids=violation_ids,
            drift_signal_ids=drift_signal_ids,
            evidence_refs=self._unique_preserve_order(evidence_refs),
            timestamp=evaluated_at,
            source_ref=source_ref,
            parent_id=parent_id,
        )

        self._validate_output_bundle(record, violations, drift_signal)

        final_snapshot = {
            "phase_contracts": phase_contracts,
            "version_records": version_records,
            "quality_records": quality_records,
            "harness_results": harness_results,
            "evaluated_artifact": evaluated_artifact,
            "prior_violation_log": prior_violation_log,
        }
        if input_snapshot != final_snapshot:
            raise ConformanceInputError(
                "ERROR_UPSTREAM_MUTATION_DURING_EVALUATION",
                "Source inputs changed while motor_022 was evaluating conformance.",
                input_ref="input_bundle",
                expected_condition="input_collections_remain_read_only",
                observed_value="input_bundle_changed_during_run",
            )

        return {
            "conformance_record": record.to_dict(),
            "violation_log": [violation.to_dict() for violation in violations],
            "architectural_drift_signal": (
                drift_signal.to_dict() if drift_signal else None
            ),
        }

    def safe_run(self, **kwargs: Any) -> Dict[str, Any]:
        """Return a structured rejection payload instead of raising."""

        try:
            return self.run(**kwargs)
        except (ConformanceInputError, UnsafeConformanceOutputError) as exc:
            return {
                "conformance_record": None,
                "violation_log": [],
                "architectural_drift_signal": None,
                "rejection": exc.to_dict(),
            }

    def _validate_and_index_inputs(
        self,
        *,
        phase_contracts: Any,
        version_records: Any,
        quality_records: Any,
        harness_results: Any,
        prior_violation_log: Optional[Any],
    ) -> Dict[str, Any]:
        contracts = self._ensure_sequence_of_mappings("phase_contracts", phase_contracts)
        versions = self._ensure_sequence_of_mappings("version_records", version_records)
        qualities = self._ensure_sequence_of_mappings("quality_records", quality_records)
        harnesses = self._ensure_sequence_of_mappings("harness_results", harness_results)
        prior_violations = self._ensure_sequence_of_mappings(
            "prior_violation_log",
            prior_violation_log or [],
        )

        for index, contract in enumerate(contracts):
            self._validate_contract(contract, index)
        version_index: Dict[Tuple[str, str], Mapping[str, Any]] = {}
        for index, version_record in enumerate(versions):
            self._validate_version_record(version_record, index)
            key = (
                self._string_field(version_record, "object_id"),
                self._string_field(version_record, "version_id"),
            )
            version_index[key] = version_record

        quality_by_key: Dict[Tuple[str, str], List[Mapping[str, Any]]] = {}
        for index, quality_record in enumerate(qualities):
            self._validate_quality_record(quality_record, index)
            key = (
                self._string_field(quality_record, "object_id"),
                self._string_field(quality_record, "version_id"),
            )
            if key not in version_index:
                raise ConformanceInputError(
                    "ERROR_MISSING_VERSION_RECORD",
                    "Quality evidence references an object/version absent from version_records.",
                    input_ref=f"quality_records[{index}]",
                    expected_condition="matching_version_record_exists",
                    observed_value=f"{key[0]}@{key[1]}",
                )
            quality_by_key.setdefault(key, []).append(quality_record)

        harness_by_key: Dict[Tuple[str, str], List[Mapping[str, Any]]] = {}
        for index, harness_result in enumerate(harnesses):
            self._validate_harness_result(harness_result, index)
            key = (
                self._string_field(harness_result, "target_id"),
                self._string_field(harness_result, "target_version_id"),
            )
            if key not in version_index:
                raise ConformanceInputError(
                    "ERROR_MISSING_VERSION_RECORD",
                    "Harness evidence references an object/version absent from version_records.",
                    input_ref=f"harness_results[{index}]",
                    expected_condition="matching_version_record_exists",
                    observed_value=f"{key[0]}@{key[1]}",
                )
            harness_by_key.setdefault(key, []).append(harness_result)

        return {
            "phase_contracts": contracts,
            "version_records": versions,
            "version_index": version_index,
            "quality_records": qualities,
            "quality_by_key": quality_by_key,
            "harness_results": harnesses,
            "harness_by_key": harness_by_key,
            "prior_violation_log": prior_violations,
        }

    def _validate_contract(self, contract: Mapping[str, Any], index: int) -> None:
        for field in (
            "contract_id",
            "phase_id",
            "required_outputs",
            "allowed_inputs",
            "handoff_rules",
            "boundary_rules",
        ):
            self._require_field(contract, field, f"phase_contracts[{index}]")
        if not (
            self._string_field(contract, "version_id", allow_empty=True)
            or self._string_field(contract, "contract_version_id", allow_empty=True)
        ):
            raise ConformanceInputError(
                "ERROR_UNTRACEABLE_INPUT",
                "Phase contract lacks a version identifier.",
                input_ref=f"phase_contracts[{index}].version_id",
                expected_condition="version_id_or_contract_version_id_present",
                observed_value="missing",
            )
        for list_field in ("required_outputs", "allowed_inputs", "handoff_rules", "boundary_rules"):
            self._ensure_list_value(
                contract[list_field],
                f"phase_contracts[{index}].{list_field}",
            )

    def _validate_version_record(self, record: Mapping[str, Any], index: int) -> None:
        for field in ("object_id", "version_id", "created_at", "provenance_ref"):
            self._require_field(record, field, f"version_records[{index}]")
        if "lineage_id" not in record:
            return
        self._string_field(record, "lineage_id", allow_empty=True)

    def _validate_quality_record(self, record: Mapping[str, Any], index: int) -> None:
        for field in (
            "object_id",
            "version_id",
            "quality_status",
            "fitness_score",
            "failed_checks",
            "evidence_refs",
        ):
            self._require_field(record, field, f"quality_records[{index}]")
        self._normalize_status(
            record["quality_status"],
            input_ref=f"quality_records[{index}].quality_status",
        )
        self._ensure_list_value(record["failed_checks"], f"quality_records[{index}].failed_checks")
        self._require_nonempty_refs(record["evidence_refs"], f"quality_records[{index}].evidence_refs")

    def _validate_harness_result(self, record: Mapping[str, Any], index: int) -> None:
        if not self._string_field(record, "target_version_id", allow_empty=True):
            raise ConformanceInputError(
                "ERROR_MISSING_TARGET_VERSION",
                "Harness result omits target_version_id.",
                input_ref=f"harness_results[{index}].target_version_id",
                expected_condition="target_version_id_present",
                observed_value="missing",
            )
        for field in (
            "test_run_id",
            "target_id",
            "target_version_id",
            "result_status",
            "failed_assertions",
            "evidence_refs",
        ):
            self._require_field(record, field, f"harness_results[{index}]")
        self._normalize_status(
            record["result_status"],
            input_ref=f"harness_results[{index}].result_status",
        )
        self._ensure_list_value(
            record["failed_assertions"],
            f"harness_results[{index}].failed_assertions",
        )
        self._require_nonempty_refs(record["evidence_refs"], f"harness_results[{index}].evidence_refs")

    def _resolve_target(
        self,
        accepted: Mapping[str, Any],
        *,
        evaluated_object_id: Optional[str],
        evaluated_version_id: Optional[str],
    ) -> Tuple[str, str]:
        explicit_id = self._clean_optional(evaluated_object_id)
        explicit_version = self._clean_optional(evaluated_version_id)
        if explicit_id or explicit_version:
            if not explicit_id or not explicit_version:
                raise ConformanceInputError(
                    "ERROR_UNTRACEABLE_INPUT",
                    "Explicit target selection must include both object id and version id.",
                    input_ref="evaluated_object_id/evaluated_version_id",
                    expected_condition="evaluated_object_id_and_evaluated_version_id_present_together",
                    observed_value=f"{explicit_id or 'missing'}@{explicit_version or 'missing'}",
                )
            return explicit_id, explicit_version

        candidate_keys = set(accepted["harness_by_key"].keys())
        candidate_keys.update(accepted["quality_by_key"].keys())
        candidate_keys.update(accepted["version_index"].keys())
        if not candidate_keys:
            raise ConformanceInputError(
                "ERROR_MISSING_VERSION_RECORD",
                "No versioned object evidence was supplied for evaluation.",
                input_ref="version_records",
                expected_condition="at_least_one_version_record_present",
                observed_value="empty",
            )
        return sorted(candidate_keys)[0]

    def _require_version_record(
        self,
        accepted: Mapping[str, Any],
        object_id: str,
        version_id: str,
    ) -> Mapping[str, Any]:
        version_record = accepted["version_index"].get((object_id, version_id))
        if not version_record:
            raise ConformanceInputError(
                "ERROR_MISSING_VERSION_RECORD",
                "The evaluated object/version is absent from version_records.",
                input_ref=f"version_records:{object_id}@{version_id}",
                expected_condition="matching_version_record_exists",
                observed_value="missing",
            )
        return version_record

    def _require_contract(
        self,
        contracts: Sequence[Mapping[str, Any]],
        *,
        object_id: str,
        object_type: str,
        evaluated_artifact: Optional[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        phase_hint = None
        if evaluated_artifact:
            phase_hint = self._clean_optional(evaluated_artifact.get("phase_id"))

        matching: List[Mapping[str, Any]] = []
        for contract in contracts:
            required_outputs = self._string_list(contract.get("required_outputs", []))
            allowed_inputs = self._string_list(contract.get("allowed_inputs", []))
            phase_id = self._string_field(contract, "phase_id", allow_empty=True)
            if object_id in required_outputs or object_id in allowed_inputs:
                matching.append(contract)
            elif phase_hint and phase_id == phase_hint:
                matching.append(contract)
            elif object_type == "phase" and object_id == phase_id:
                matching.append(contract)

        if matching:
            return sorted(
                matching,
                key=lambda item: (
                    self._string_field(item, "contract_id"),
                    self._contract_version_id(item),
                ),
            )[0]
        if len(contracts) == 1:
            return contracts[0]
        raise ConformanceInputError(
            "ERROR_MISSING_CONTRACT",
            "No phase contract can be matched to the evaluated object, phase or handoff.",
            input_ref=f"phase_contracts:{object_id}",
            expected_condition="applicable_phase_contract_present",
            observed_value="no_matching_contract",
        )

    def _lineage_violations(
        self,
        *,
        record_id: str,
        object_id: str,
        version_id: str,
        version_record: Mapping[str, Any],
        timestamp: str,
    ) -> List[ViolationRecord]:
        lineage_id = self._string_field(version_record, "lineage_id", allow_empty=True)
        if lineage_id:
            return []
        return [
            self._make_violation(
                conformance_record_id=record_id,
                evaluated_object_id=object_id,
                evaluated_version_id=version_id,
                violation_type="lineage",
                rule_ref="version_records.lineage_id.required",
                severity="CRITICAL",
                input_ref=f"version_records:{object_id}@{version_id}.lineage_id",
                expected_condition="lineage_id_is_non_empty",
                observed_value="missing",
                material=True,
                evidence_refs=[self._version_record_ref(version_record)],
                timestamp=timestamp,
            )
        ]

    def _quality_violations(
        self,
        *,
        record_id: str,
        object_id: str,
        version_id: str,
        quality_records: Sequence[Mapping[str, Any]],
        timestamp: str,
    ) -> List[ViolationRecord]:
        violations: List[ViolationRecord] = []
        for record in quality_records:
            status = self._normalize_status(record["quality_status"], input_ref="quality_status")
            failed_checks = self._string_list(record.get("failed_checks", []))
            checks = failed_checks or [f"quality_status.{status}"]
            if status == "FAIL":
                for check in checks:
                    violations.append(
                        self._make_violation(
                            conformance_record_id=record_id,
                            evaluated_object_id=object_id,
                            evaluated_version_id=version_id,
                            violation_type="quality",
                            rule_ref=check,
                            severity="HIGH",
                            input_ref=self._quality_record_id(record),
                            expected_condition="quality_status_is_PASS_or_non_material_WARNING",
                            observed_value=status,
                            material=True,
                            evidence_refs=self._refs(record),
                            timestamp=timestamp,
                        )
                    )
            elif status == "WARNING":
                for check in checks:
                    violations.append(
                        self._make_violation(
                            conformance_record_id=record_id,
                            evaluated_object_id=object_id,
                            evaluated_version_id=version_id,
                            violation_type="quality",
                            rule_ref=check,
                            severity="LOW",
                            input_ref=self._quality_record_id(record),
                            expected_condition="quality_status_PASS_for_clean_conformance",
                            observed_value=status,
                            material=False,
                            evidence_refs=self._refs(record),
                            timestamp=timestamp,
                        )
                    )
        return violations

    def _harness_violations(
        self,
        *,
        record_id: str,
        object_id: str,
        version_id: str,
        harness_results: Sequence[Mapping[str, Any]],
        timestamp: str,
    ) -> List[ViolationRecord]:
        violations: List[ViolationRecord] = []
        for record in harness_results:
            status = self._normalize_status(record["result_status"], input_ref="result_status")
            assertions = self._string_list(record.get("failed_assertions", []))
            if status == "FAIL":
                for assertion in assertions or ["harness_result_status.FAIL"]:
                    violations.append(
                        self._make_violation(
                            conformance_record_id=record_id,
                            evaluated_object_id=object_id,
                            evaluated_version_id=version_id,
                            violation_type="harness",
                            rule_ref=assertion,
                            severity="HIGH",
                            input_ref=self._harness_result_id(record),
                            expected_condition="required_harness_assertions_pass",
                            observed_value=status,
                            material=True,
                            evidence_refs=self._refs(record),
                            timestamp=timestamp,
                        )
                    )
            elif status == "WARNING":
                for assertion in assertions or ["harness_result_status.WARNING"]:
                    violations.append(
                        self._make_violation(
                            conformance_record_id=record_id,
                            evaluated_object_id=object_id,
                            evaluated_version_id=version_id,
                            violation_type="harness",
                            rule_ref=assertion,
                            severity="MEDIUM",
                            input_ref=self._harness_result_id(record),
                            expected_condition="harness_result_status_PASS_for_clean_conformance",
                            observed_value=status,
                            material=False,
                            evidence_refs=self._refs(record),
                            timestamp=timestamp,
                        )
                    )
        return violations

    def _boundary_violations(
        self,
        *,
        record_id: str,
        object_id: str,
        version_id: str,
        contract: Mapping[str, Any],
        evaluated_artifact: Optional[Mapping[str, Any]],
        timestamp: str,
    ) -> List[ViolationRecord]:
        if not evaluated_artifact:
            return []

        violations: List[ViolationRecord] = []
        explicit_boundary_violations = evaluated_artifact.get("boundary_violations", [])
        if explicit_boundary_violations:
            for index, observed in enumerate(
                self._ensure_sequence_of_mappings(
                    "evaluated_artifact.boundary_violations",
                    explicit_boundary_violations,
                )
            ):
                rule_ref = self._string_field(observed, "rule_ref")
                violations.append(
                    self._make_violation(
                        conformance_record_id=record_id,
                        evaluated_object_id=object_id,
                        evaluated_version_id=version_id,
                        violation_type="boundary",
                        rule_ref=rule_ref,
                        severity=self._severity_or_default(observed.get("severity"), "HIGH"),
                        input_ref=self._string_field(
                            observed,
                            "input_ref",
                            default=f"evaluated_artifact.boundary_violations[{index}]",
                        ),
                        expected_condition=self._string_field(
                            observed,
                            "expected_condition",
                            default=f"boundary_rule_{rule_ref}_is_satisfied",
                        ),
                        observed_value=self._string_field(
                            observed,
                            "observed_value",
                            default="boundary_violation_observed",
                        ),
                        material=True,
                        evidence_refs=self._refs(observed)
                        or [f"evaluated_artifact:{object_id}@{version_id}:boundary"],
                        timestamp=timestamp,
                    )
                )

        boundary_rules = set(self._string_list(contract.get("boundary_rules", [])))
        output_fields = self._artifact_output_fields(evaluated_artifact)
        if "no_cross_phase_reporting_fields" in boundary_rules:
            prohibited = sorted(
                field for field in output_fields if "cross_phase_reporting" in field
            )
            if prohibited:
                violations.append(
                    self._make_violation(
                        conformance_record_id=record_id,
                        evaluated_object_id=object_id,
                        evaluated_version_id=version_id,
                        violation_type="boundary",
                        rule_ref="no_cross_phase_reporting_fields",
                        severity="HIGH",
                        input_ref=f"evaluated_artifact:{object_id}@{version_id}.output_fields",
                        expected_condition="artifact_outputs_exclude_cross_phase_reporting_fields",
                        observed_value=",".join(prohibited),
                        material=True,
                        evidence_refs=[
                            f"evaluated_artifact:{object_id}@{version_id}:output_fields"
                        ],
                        timestamp=timestamp,
                    )
                )
        return violations

    def _build_drift_signal(
        self,
        *,
        object_type: str,
        object_id: str,
        record_id: str,
        violations: Sequence[ViolationRecord],
        prior_violation_log: Sequence[Mapping[str, Any]],
        timestamp: str,
    ) -> Optional[DriftSignal]:
        material_violations = [violation for violation in violations if violation.material]
        if not material_violations:
            return None

        for current in material_violations:
            related_violation_ids = [current.violation_id]
            related_record_ids = [record_id]
            evidence_refs = list(current.evidence_refs)
            for prior in prior_violation_log:
                if not self._is_matching_prior_violation(current, prior, object_id):
                    continue
                prior_id = self._string_field(prior, "violation_id", allow_empty=True)
                prior_record_id = self._string_field(
                    prior,
                    "conformance_record_id",
                    allow_empty=True,
                )
                if prior_id:
                    related_violation_ids.append(prior_id)
                if prior_record_id:
                    related_record_ids.append(prior_record_id)
                evidence_refs.extend(self._refs(prior))
            if len(related_violation_ids) > 1:
                severity = self._max_severity(
                    [current.severity]
                    + [
                        self._severity_or_default(prior.get("severity"), "LOW")
                        for prior in prior_violation_log
                        if self._is_matching_prior_violation(current, prior, object_id)
                    ]
                )
                return self._make_drift_signal(
                    scope=object_type,
                    scope_ref=object_id,
                    basis="repeated_violation",
                    severity=severity,
                    related_violation_ids=self._unique_preserve_order(related_violation_ids),
                    related_conformance_record_ids=self._unique_preserve_order(related_record_ids),
                    evidence_refs=self._unique_preserve_order(evidence_refs),
                    source_ref=record_id,
                    timestamp=timestamp,
                )

        critical = [violation for violation in material_violations if violation.severity == "CRITICAL"]
        if critical:
            violation = critical[0]
            return self._make_drift_signal(
                scope=object_type,
                scope_ref=object_id,
                basis="critical_single_violation",
                severity="CRITICAL",
                related_violation_ids=[violation.violation_id],
                related_conformance_record_ids=[record_id],
                evidence_refs=list(violation.evidence_refs),
                source_ref=record_id,
                timestamp=timestamp,
            )
        return None

    def _is_matching_prior_violation(
        self,
        current: ViolationRecord,
        prior: Mapping[str, Any],
        object_id: str,
    ) -> bool:
        if not prior:
            return False
        prior_object_id = self._string_field(prior, "evaluated_object_id", allow_empty=True)
        prior_rule_ref = self._string_field(prior, "rule_ref", allow_empty=True)
        prior_type = self._string_field(prior, "violation_type", allow_empty=True)
        prior_material = bool(prior.get("material", False))
        return (
            prior_material
            and prior_object_id == object_id
            and prior_rule_ref == current.rule_ref
            and prior_type == current.violation_type
        )

    def _status_from_violations(
        self,
        violations: Sequence[ViolationRecord],
    ) -> Tuple[str, str]:
        if any(violation.material for violation in violations):
            return "FAIL", "material_conformance_violation_detected"
        if violations:
            if any(violation.violation_type == "missing_evidence" for violation in violations):
                return "WARNING", "quality_warning_or_missing_nonblocking_harness_evidence"
            return "WARNING", "non_material_conformance_warning_detected"
        return "PASS", "all_required_contract_lineage_quality_and_harness_checks_passed"

    def _make_conformance_record(
        self,
        *,
        record_id: str,
        evaluated_object_id: str,
        evaluated_object_type: str,
        evaluated_version_id: str,
        contract_id: str,
        contract_version_id: str,
        lineage_id: str,
        quality_record_ids: List[str],
        harness_result_ids: List[str],
        status: str,
        status_reason: str,
        violation_ids: List[str],
        drift_signal_ids: List[str],
        evidence_refs: List[str],
        timestamp: str,
        source_ref: str,
        parent_id: Optional[str],
    ) -> ConformanceRecord:
        semantic = {
            "record_id": record_id,
            "evaluated_object_id": evaluated_object_id,
            "evaluated_object_type": evaluated_object_type,
            "evaluated_version_id": evaluated_version_id,
            "contract_id": contract_id,
            "contract_version_id": contract_version_id,
            "lineage_id": lineage_id,
            "quality_record_ids": quality_record_ids,
            "harness_result_ids": harness_result_ids,
            "status": status,
            "status_reason": status_reason,
            "violation_ids": violation_ids,
            "drift_signal_ids": drift_signal_ids,
            "evidence_refs": evidence_refs,
        }
        version_hash = self._hash_payload(semantic)
        return ConformanceRecord(
            record_id=record_id,
            evaluated_object_id=evaluated_object_id,
            evaluated_object_type=evaluated_object_type,
            evaluated_version_id=evaluated_version_id,
            contract_id=contract_id,
            contract_version_id=contract_version_id,
            lineage_id=lineage_id,
            quality_record_ids=quality_record_ids,
            harness_result_ids=harness_result_ids,
            status=status,
            status_reason=status_reason,
            violation_ids=violation_ids,
            drift_signal_ids=drift_signal_ids,
            evidence_refs=evidence_refs,
            evaluated_at=timestamp,
            version_id=f"{record_id}:version:{version_hash[:12]}",
            created_at=timestamp,
            updated_at=timestamp,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=timestamp,
            parent_id=parent_id,
        )

    def _make_violation(
        self,
        *,
        conformance_record_id: str,
        evaluated_object_id: str,
        evaluated_version_id: str,
        violation_type: str,
        rule_ref: str,
        severity: str,
        input_ref: str,
        expected_condition: str,
        observed_value: str,
        material: bool,
        evidence_refs: List[str],
        timestamp: str,
    ) -> ViolationRecord:
        severity = self._severity_or_default(severity, "HIGH")
        evidence_refs = self._unique_preserve_order(evidence_refs)
        violation_id = (
            f"{conformance_record_id}:violation:{violation_type}:{rule_ref}:{input_ref}:"
            f"{self._hash_text(expected_condition)[:12]}:{self._hash_text(observed_value)[:12]}"
        )
        semantic = {
            "violation_id": violation_id,
            "conformance_record_id": conformance_record_id,
            "evaluated_object_id": evaluated_object_id,
            "evaluated_version_id": evaluated_version_id,
            "violation_type": violation_type,
            "rule_ref": rule_ref,
            "severity": severity,
            "input_ref": input_ref,
            "expected_condition": expected_condition,
            "observed_value": observed_value,
            "material": material,
            "evidence_refs": evidence_refs,
        }
        version_hash = self._hash_payload(semantic)
        return ViolationRecord(
            violation_id=violation_id,
            conformance_record_id=conformance_record_id,
            evaluated_object_id=evaluated_object_id,
            evaluated_version_id=evaluated_version_id,
            violation_type=violation_type,
            rule_ref=rule_ref,
            severity=severity,
            input_ref=input_ref,
            expected_condition=expected_condition,
            observed_value=observed_value,
            material=material,
            evidence_refs=evidence_refs,
            detected_at=timestamp,
            version_id=f"{violation_id}:version:{version_hash[:12]}",
            created_at=timestamp,
            updated_at=timestamp,
            version_hash=version_hash,
            source_ref=input_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=timestamp,
            parent_id=conformance_record_id,
        )

    def _make_drift_signal(
        self,
        *,
        scope: str,
        scope_ref: str,
        basis: str,
        severity: str,
        related_violation_ids: List[str],
        related_conformance_record_ids: List[str],
        evidence_refs: List[str],
        source_ref: str,
        timestamp: str,
    ) -> DriftSignal:
        related_hash = self._hash_text("|".join(sorted(related_violation_ids)))[:16]
        signal_id = f"{MOTOR_ID}:drift:{scope}:{scope_ref}:{basis}:{severity}:{related_hash}"
        semantic = {
            "signal_id": signal_id,
            "scope": scope,
            "scope_ref": scope_ref,
            "basis": basis,
            "severity": severity,
            "related_violation_ids": related_violation_ids,
            "related_conformance_record_ids": related_conformance_record_ids,
            "evidence_refs": evidence_refs,
        }
        version_hash = self._hash_payload(semantic)
        return DriftSignal(
            signal_id=signal_id,
            scope=scope,
            scope_ref=scope_ref,
            basis=basis,
            severity=severity,
            related_violation_ids=related_violation_ids,
            related_conformance_record_ids=related_conformance_record_ids,
            evidence_refs=evidence_refs,
            emitted_at=timestamp,
            version_id=f"{signal_id}:version:{version_hash[:12]}",
            created_at=timestamp,
            updated_at=timestamp,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=timestamp,
            parent_id=None,
        )

    def _validate_output_bundle(
        self,
        record: ConformanceRecord,
        violations: Sequence[ViolationRecord],
        drift_signal: Optional[DriftSignal],
    ) -> None:
        if record.status not in STATUS_VALUES:
            raise UnsafeConformanceOutputError(
                "ERROR_INVALID_STATUS",
                "Conformance status is outside the declared enum.",
                input_ref=record.record_id,
                expected_condition="status_in_PASS_WARNING_FAIL",
                observed_value=record.status,
            )
        if record.status == "PASS" and record.violation_ids:
            raise UnsafeConformanceOutputError(
                "ERROR_UNSAFE_CONFORMANCE_OUTPUT",
                "PASS records cannot contain violations.",
                input_ref=record.record_id,
                expected_condition="PASS_has_no_violation_ids",
                observed_value="violation_ids_present",
            )
        if record.status == "FAIL" and not any(violation.material for violation in violations):
            raise UnsafeConformanceOutputError(
                "ERROR_UNSAFE_CONFORMANCE_OUTPUT",
                "FAIL records require at least one material violation.",
                input_ref=record.record_id,
                expected_condition="FAIL_has_material_violation",
                observed_value="no_material_violation",
            )
        for violation in violations:
            if violation.conformance_record_id != record.record_id:
                raise UnsafeConformanceOutputError(
                    "ERROR_ORPHAN_OUTPUT_RECORD",
                    "ViolationRecord is not linked to its parent ConformanceRecord.",
                    input_ref=violation.violation_id,
                    expected_condition=record.record_id,
                    observed_value=violation.conformance_record_id,
                )
        if drift_signal:
            known_violation_ids = {violation.violation_id for violation in violations}
            unknown_ids = [
                violation_id
                for violation_id in drift_signal.related_violation_ids
                if violation_id not in known_violation_ids
            ]
            if unknown_ids and drift_signal.basis != "repeated_violation":
                raise UnsafeConformanceOutputError(
                    "ERROR_DRIFT_SIGNAL_WITHOUT_EVIDENCE",
                    "DriftSignal references unknown current-run violations.",
                    input_ref=drift_signal.signal_id,
                    expected_condition="related_violation_ids_link_to_current_or_prior_evidence",
                    observed_value=",".join(unknown_ids),
                )
            if not drift_signal.related_violation_ids or not drift_signal.evidence_refs:
                raise UnsafeConformanceOutputError(
                    "ERROR_DRIFT_SIGNAL_WITHOUT_EVIDENCE",
                    "DriftSignal lacks linked violation evidence.",
                    input_ref=drift_signal.signal_id,
                    expected_condition="non_empty_related_violation_ids_and_evidence_refs",
                    observed_value="missing",
                )

    def _ensure_sequence_of_mappings(self, name: str, value: Any) -> List[Mapping[str, Any]]:
        if value is None or isinstance(value, (str, bytes)) or isinstance(value, Mapping):
            raise ConformanceInputError(
                "ERROR_INVALID_INPUT_COLLECTION",
                f"{name} must be a collection of structured records.",
                input_ref=name,
                expected_condition="collection_of_mappings",
                observed_value=type(value).__name__,
            )
        if not isinstance(value, Sequence):
            raise ConformanceInputError(
                "ERROR_INVALID_INPUT_COLLECTION",
                f"{name} must be a collection of structured records.",
                input_ref=name,
                expected_condition="collection_of_mappings",
                observed_value=type(value).__name__,
            )
        records: List[Mapping[str, Any]] = []
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                raise ConformanceInputError(
                    "ERROR_INVALID_INPUT_COLLECTION",
                    f"{name}[{index}] must be a structured mapping.",
                    input_ref=f"{name}[{index}]",
                    expected_condition="mapping",
                    observed_value=type(item).__name__,
                )
            records.append(item)
        return records

    def _require_field(self, record: Mapping[str, Any], field: str, input_ref: str) -> None:
        if not self._string_field(record, field, allow_empty=True) and field not in (
            "failed_checks",
            "evidence_refs",
            "required_outputs",
            "allowed_inputs",
            "handoff_rules",
            "boundary_rules",
        ):
            raise ConformanceInputError(
                "ERROR_UNTRACEABLE_INPUT",
                f"{input_ref}.{field} is required.",
                input_ref=f"{input_ref}.{field}",
                expected_condition=f"{field}_present",
                observed_value="missing",
            )
        if field in (
            "failed_checks",
            "evidence_refs",
            "required_outputs",
            "allowed_inputs",
            "handoff_rules",
            "boundary_rules",
        ) and field not in record:
            raise ConformanceInputError(
                "ERROR_UNTRACEABLE_INPUT",
                f"{input_ref}.{field} is required.",
                input_ref=f"{input_ref}.{field}",
                expected_condition=f"{field}_present",
                observed_value="missing",
            )

    def _ensure_list_value(self, value: Any, input_ref: str) -> None:
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise ConformanceInputError(
                "ERROR_INVALID_INPUT_COLLECTION",
                f"{input_ref} must be a list value.",
                input_ref=input_ref,
                expected_condition="list",
                observed_value=type(value).__name__,
            )

    def _require_nonempty_refs(self, value: Any, input_ref: str) -> None:
        self._ensure_list_value(value, input_ref)
        refs = [str(item).strip() for item in value if str(item).strip()]
        if not refs:
            raise ConformanceInputError(
                "ERROR_UNTRACEABLE_INPUT",
                f"{input_ref} must contain at least one evidence reference.",
                input_ref=input_ref,
                expected_condition="non_empty_evidence_refs",
                observed_value="empty",
            )

    def _normalize_status(self, value: Any, *, input_ref: str) -> str:
        status = str(value).strip().upper()
        if status not in STATUS_VALUES:
            raise ConformanceInputError(
                "ERROR_INVALID_STATUS",
                "Status value is outside the declared enum.",
                input_ref=input_ref,
                expected_condition="PASS|WARNING|FAIL",
                observed_value=str(value),
            )
        return status

    def _normalize_object_type(self, value: Any) -> str:
        object_type = str(value).strip().lower()
        if object_type not in OBJECT_TYPES:
            raise ConformanceInputError(
                "ERROR_UNTRACEABLE_INPUT",
                "Evaluated object type is outside the declared enum.",
                input_ref="evaluated_object_type",
                expected_condition="motor|dataset|artifact|handoff|phase",
                observed_value=str(value),
            )
        return object_type

    def _string_field(
        self,
        record: Mapping[str, Any],
        field: str,
        *,
        allow_empty: bool = False,
        default: Optional[str] = None,
    ) -> str:
        if field not in record:
            return default or ""
        value = record.get(field)
        if value is None:
            return default or ""
        text = str(value).strip()
        if text or allow_empty:
            return text
        return default or ""

    def _clean_optional(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _string_list(self, value: Any) -> List[str]:
        if isinstance(value, Mapping):
            return [str(key).strip() for key in value.keys() if str(key).strip()]
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return [str(item).strip() for item in value if str(item).strip()]
        if value is None:
            return []
        text = str(value).strip()
        return [text] if text else []

    def _refs(self, record: Mapping[str, Any]) -> List[str]:
        for field in ("evidence_refs", "source_input_refs"):
            refs = record.get(field)
            if isinstance(refs, Sequence) and not isinstance(refs, (str, bytes)):
                return self._unique_preserve_order(
                    [str(ref).strip() for ref in refs if str(ref).strip()]
                )
        source_ref = self._string_field(record, "source_ref", allow_empty=True)
        return [source_ref] if source_ref else []

    def _collect_evidence_refs(
        self,
        *,
        contract: Mapping[str, Any],
        version_record: Mapping[str, Any],
        quality_records: Sequence[Mapping[str, Any]],
        harness_results: Sequence[Mapping[str, Any]],
    ) -> List[str]:
        refs = [
            f"phase_contract:{self._string_field(contract, 'contract_id')}:{self._contract_version_id(contract)}",
            self._version_record_ref(version_record),
        ]
        refs.extend(self._refs(version_record))
        for record in quality_records:
            refs.extend(self._refs(record))
        for record in harness_results:
            refs.extend(self._refs(record))
        return self._unique_preserve_order(refs)

    def _version_record_ref(self, record: Mapping[str, Any]) -> str:
        object_id = self._string_field(record, "object_id", allow_empty=True)
        version_id = self._string_field(record, "version_id", allow_empty=True)
        provenance_ref = self._string_field(record, "provenance_ref", allow_empty=True)
        return provenance_ref or f"version_record:{object_id}@{version_id}"

    def _quality_record_id(self, record: Mapping[str, Any]) -> str:
        for field in ("quality_record_id", "record_id", "id"):
            value = self._string_field(record, field, allow_empty=True)
            if value:
                return value
        refs = self._refs(record)
        if refs:
            return refs[0].split(":")[-1]
        return f"quality:{self._string_field(record, 'object_id')}@{self._string_field(record, 'version_id')}"

    def _harness_result_id(self, record: Mapping[str, Any]) -> str:
        for field in ("harness_result_id", "result_id", "test_run_id", "id"):
            value = self._string_field(record, field, allow_empty=True)
            if value:
                return value
        return f"harness:{self._string_field(record, 'target_id')}@{self._string_field(record, 'target_version_id')}"

    def _contract_version_id(self, contract: Mapping[str, Any]) -> str:
        return self._string_field(contract, "contract_version_id", allow_empty=True) or self._string_field(
            contract,
            "version_id",
        )

    def _record_id(
        self,
        *,
        object_type: str,
        object_id: str,
        version_id: str,
        contract_id: str,
        contract_version_id: str,
    ) -> str:
        return f"{MOTOR_ID}:{object_type}:{object_id}:{version_id}:{contract_id}:{contract_version_id}"

    def _artifact_output_fields(self, artifact: Mapping[str, Any]) -> List[str]:
        if "output_fields" in artifact:
            return self._string_list(artifact.get("output_fields"))
        if "fields" in artifact:
            return self._string_list(artifact.get("fields"))
        outputs = artifact.get("outputs")
        if isinstance(outputs, Mapping):
            return self._string_list(outputs)
        return self._string_list(outputs)

    def _severity_or_default(self, value: Any, default: str) -> str:
        severity = str(value or default).strip().upper()
        if severity not in SEVERITY_ORDER:
            return default
        return severity

    def _max_severity(self, severities: Iterable[str]) -> str:
        values = [self._severity_or_default(severity, "LOW") for severity in severities]
        if not values:
            return "LOW"
        return max(values, key=lambda severity: SEVERITY_ORDER[severity])

    def _unique_preserve_order(self, values: Iterable[str]) -> List[str]:
        seen = set()
        result: List[str] = []
        for value in values:
            text = str(value).strip()
            if not text or text in seen:
                continue
            seen.add(text)
            result.append(text)
        return result

    def _hash_payload(self, payload: Mapping[str, Any]) -> str:
        canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
        return self._hash_text(canonical)

    def _hash_text(self, value: str) -> str:
        return sha256(str(value).encode("utf-8")).hexdigest()
