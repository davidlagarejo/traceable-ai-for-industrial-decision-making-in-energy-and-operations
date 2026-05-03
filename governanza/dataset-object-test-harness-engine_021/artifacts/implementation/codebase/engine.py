"""Deterministic Dataset / Object Test Harness Engine for motor_021.

The harness validates supplied contracts, version records, taxonomy snapshots,
normalized records, identity records, and quality records as a read-only batch.
It emits structured test results, an aggregate harness report, and integration
failure records. It never repairs or mutates upstream objects.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from copy import deepcopy
from hashlib import sha256
import json
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .errors import HarnessInputError, UnsafeHarnessReportError
from .models import HarnessReport, IntegrationFailure, TestResult


MOTOR_ID = "motor_021"
DEFAULT_HARNESS_VERSION = "motor_021.harness.v1"
DEFAULT_CASE_VERSION = "motor_021.case.v1"
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"

APPROVED_CONTRACT_STATUSES = {
    "active",
    "approved",
    "closed",
    "final",
    "ready_for_test",
    "validated",
}
RESULT_STATUSES = {"pass", "warning", "fail", "skipped"}
RESULT_SEVERITIES = {"info", "warning", "critical"}
FAILURE_SEVERITIES = {"warning", "critical"}
ERROR_CODES = {
    "INVALID_HARNESS_INPUT",
    "UNRESOLVED_REFERENCE",
    "CONTRACT_MISMATCH",
    "TAXONOMY_MISMATCH",
    "LINEAGE_GAP",
    "UNSAFE_HARNESS_REPORT",
}
CASE_NAMES = [
    "contract_required_fields_present",
    "version_ref_resolves",
    "taxonomy_refs_allowed",
    "identity_ref_resolves",
    "quality_record_present",
]
TIME_FIELDS = {
    "created_at",
    "updated_at",
    "executed_at",
    "generated_at",
    "detected_at",
    "produced_at",
}


class DatasetObjectTestHarnessEngine:
    """Run deterministic integration tests across dataset and object handoffs."""

    def __init__(
        self,
        harness_version: str = DEFAULT_HARNESS_VERSION,
        case_version: str = DEFAULT_CASE_VERSION,
    ) -> None:
        self.harness_version = str(harness_version).strip() or DEFAULT_HARNESS_VERSION
        self.case_version = str(case_version).strip() or DEFAULT_CASE_VERSION

    def run(
        self,
        *,
        phase_contracts: Sequence[Mapping[str, Any]],
        version_records: Sequence[Mapping[str, Any]],
        canonical_taxonomy: Mapping[str, Any],
        normalized_records: Sequence[Mapping[str, Any]],
        identity_records: Sequence[Mapping[str, Any]],
        quality_records: Sequence[Mapping[str, Any]],
        executed_at: str = DEFAULT_TIMESTAMP,
    ) -> Dict[str, Any]:
        """Execute the required harness cases and return contract-shaped output."""

        input_snapshot = deepcopy(
            {
                "phase_contracts": phase_contracts,
                "version_records": version_records,
                "canonical_taxonomy": canonical_taxonomy,
                "normalized_records": normalized_records,
                "identity_records": identity_records,
                "quality_records": quality_records,
            }
        )

        accepted = self._validate_and_index_inputs(
            phase_contracts=phase_contracts,
            version_records=version_records,
            canonical_taxonomy=canonical_taxonomy,
            normalized_records=normalized_records,
            identity_records=identity_records,
            quality_records=quality_records,
        )
        harness_run_id = self._harness_run_id(accepted)

        results: List[TestResult] = []
        failures: List[IntegrationFailure] = []
        coverage_notes: List[Dict[str, Any]] = []

        for case_name, case_runner in (
            ("contract_required_fields_present", self._case_contract_required_fields),
            ("version_ref_resolves", self._case_version_ref_resolves),
            ("taxonomy_refs_allowed", self._case_taxonomy_refs_allowed),
            ("identity_ref_resolves", self._case_identity_ref_resolves),
            ("quality_record_present", self._case_quality_record_present),
        ):
            result, case_failures, case_notes = case_runner(
                harness_run_id,
                accepted,
                executed_at,
            )
            if result.case_name != case_name:
                raise UnsafeHarnessReportError(
                    "UNSAFE_HARNESS_REPORT",
                    "Case runner emitted a result for a different case name.",
                    {"expected_case_name": case_name, "observed_case_name": result.case_name},
                )
            results.append(result)
            failures.extend(case_failures)
            coverage_notes.extend(case_notes)

        report = self._build_report(
            harness_run_id,
            accepted,
            results,
            failures,
            coverage_notes,
            executed_at,
        )
        self._validate_report(report, results, failures)

        final_snapshot = {
            "phase_contracts": phase_contracts,
            "version_records": version_records,
            "canonical_taxonomy": canonical_taxonomy,
            "normalized_records": normalized_records,
            "identity_records": identity_records,
            "quality_records": quality_records,
        }
        if input_snapshot != final_snapshot:
            raise HarnessInputError(
                "INVALID_HARNESS_INPUT",
                "Source inputs changed during harness execution.",
                {"mutation_detected": True},
            )

        return {
            "test_result": [result.to_dict() for result in results],
            "harness_report": report.to_dict(),
            "integration_failure_log": [failure.to_dict() for failure in failures],
        }

    def safe_run(self, **kwargs: Any) -> Dict[str, Any]:
        """Return a structured rejection payload instead of raising."""

        try:
            return self.run(**kwargs)
        except (HarnessInputError, UnsafeHarnessReportError) as exc:
            return {
                "test_result": [],
                "harness_report": None,
                "integration_failure_log": [],
                "rejection": exc.to_dict(),
            }

    def _validate_and_index_inputs(
        self,
        *,
        phase_contracts: Any,
        version_records: Any,
        canonical_taxonomy: Any,
        normalized_records: Any,
        identity_records: Any,
        quality_records: Any,
    ) -> Dict[str, Any]:
        contracts = self._ensure_sequence_of_mappings(
            "phase_contracts",
            phase_contracts,
        )
        versions = self._ensure_sequence_of_mappings(
            "version_records",
            version_records,
        )
        normalized = self._ensure_sequence_of_mappings(
            "normalized_records",
            normalized_records,
        )
        identities = self._ensure_sequence_of_mappings(
            "identity_records",
            identity_records,
        )
        qualities = self._ensure_sequence_of_mappings(
            "quality_records",
            quality_records,
        )
        if not isinstance(canonical_taxonomy, Mapping):
            raise HarnessInputError(
                "INVALID_HARNESS_INPUT",
                "canonical_taxonomy must be a structured mapping.",
                {"input_name": "canonical_taxonomy"},
            )
        if (
            not contracts
            and not versions
            and not normalized
            and not identities
            and not qualities
            and not canonical_taxonomy
        ):
            raise HarnessInputError(
                "INVALID_HARNESS_INPUT",
                "At least one structured authority or object input is required.",
            )

        contract_index = self._index_contracts(contracts)
        version_index = self._index_version_records(versions)
        taxonomy_ref, allowed_terms = self._validate_taxonomy(canonical_taxonomy)
        normalized_index = self._index_by_required_id(
            "normalized_records",
            normalized,
            "record_id",
        )
        identity_index = self._index_by_required_id(
            "identity_records",
            identities,
            "identity_id",
        )
        quality_index = self._index_by_required_id(
            "quality_records",
            qualities,
            "quality_record_id",
        )

        self._validate_identity_records(identities)
        self._validate_quality_records(qualities)

        return {
            "phase_contracts": contracts,
            "contract_index": contract_index,
            "version_records": versions,
            "version_index": version_index,
            "canonical_taxonomy": canonical_taxonomy,
            "taxonomy_ref": taxonomy_ref,
            "allowed_terms": allowed_terms,
            "normalized_records": normalized,
            "normalized_index": normalized_index,
            "identity_records": identities,
            "identity_index": identity_index,
            "quality_records": qualities,
            "quality_index": quality_index,
            "quality_by_subject": self._group_by_string_field(qualities, "subject_ref"),
        }

    def _case_contract_required_fields(
        self,
        harness_run_id: str,
        accepted: Mapping[str, Any],
        executed_at: str,
    ) -> Tuple[TestResult, List[IntegrationFailure], List[Dict[str, Any]]]:
        case_name = "contract_required_fields_present"
        input_refs = self._case_input_refs(
            accepted,
            include_contracts=True,
            include_normalized=True,
        )
        test_id = self._test_id(harness_run_id, case_name, input_refs)
        failures: List[IntegrationFailure] = []
        notes: List[Dict[str, Any]] = []

        normalized_records = accepted["normalized_records"]
        if not normalized_records:
            result = self._make_result(
                harness_run_id=harness_run_id,
                test_id=test_id,
                case_name=case_name,
                status="skipped",
                input_refs=input_refs,
                expected_condition="normalized records satisfy active phase-contract required fields",
                observed_condition="no normalized records were supplied for contract field testing",
                failure_ids=[],
                severity="warning",
                error_code=None,
                source_ref=self._first_or_default(input_refs),
                timestamp=executed_at,
            )
            notes.append(
                self._coverage_note(case_name, "skipped", "normalized_records is empty")
            )
            return result, failures, notes

        observed_parts: List[str] = []
        for record in normalized_records:
            record_ref = self._record_ref(record)
            contract = self._contract_for_record(record, accepted["phase_contracts"])
            contract_ref = self._mapping_string(contract, "contract_id") if contract else None

            if not contract:
                observed_schema = self._mapping_string(record, "schema_ref") or "absent"
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="contract_mismatch",
                        affected_object_ref=record_ref,
                        expected_ref="phase_contracts.contract_id",
                        observed_value=observed_schema,
                        source_input_refs=[record_ref],
                        severity="critical",
                        owner_motor_ref="motor_005",
                        recommended_action=(
                            "Emit normalized records with schema_ref pointing to an approved phase contract."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(f"{record_ref}: no matching phase contract")
                continue

            required_fields = self._contract_required_fields(contract)
            missing_fields = [
                field for field in required_fields if not self._field_present(record, field)
            ]
            if missing_fields:
                for field in missing_fields:
                    failures.append(
                        self._make_failure(
                            harness_run_id=harness_run_id,
                            test_id=test_id,
                            failure_type="contract_mismatch",
                            affected_object_ref=record_ref,
                            expected_ref=f"{contract_ref}.field_requirements.{field}",
                            observed_value="missing",
                            source_input_refs=[record_ref, contract_ref],
                            severity="critical",
                            owner_motor_ref="motor_005",
                            recommended_action=(
                                "Regenerate or correct the normalized record in the owning motor so required contract fields are present."
                            ),
                            timestamp=executed_at,
                        )
                    )
                observed_parts.append(
                    f"{record_ref}: missing required fields {','.join(missing_fields)}"
                )
            else:
                observed_parts.append(f"{record_ref}: required fields present")

        status = "fail" if failures else "pass"
        result = self._make_result(
            harness_run_id=harness_run_id,
            test_id=test_id,
            case_name=case_name,
            status=status,
            input_refs=input_refs,
            expected_condition="each normalized record satisfies the field_requirements of its approved phase contract",
            observed_condition="; ".join(observed_parts),
            failure_ids=[failure.failure_id for failure in failures],
            severity="critical" if failures else "info",
            error_code="CONTRACT_MISMATCH" if failures else None,
            source_ref=self._first_or_default(input_refs),
            timestamp=executed_at,
        )
        return result, failures, notes

    def _case_version_ref_resolves(
        self,
        harness_run_id: str,
        accepted: Mapping[str, Any],
        executed_at: str,
    ) -> Tuple[TestResult, List[IntegrationFailure], List[Dict[str, Any]]]:
        case_name = "version_ref_resolves"
        input_refs = self._case_input_refs(
            accepted,
            include_versions=True,
            include_normalized=True,
        )
        test_id = self._test_id(harness_run_id, case_name, input_refs)
        failures: List[IntegrationFailure] = []
        notes: List[Dict[str, Any]] = []
        normalized_records = accepted["normalized_records"]

        if not normalized_records:
            result = self._make_result(
                harness_run_id=harness_run_id,
                test_id=test_id,
                case_name=case_name,
                status="skipped",
                input_refs=input_refs,
                expected_condition="normalized records provide version_ref values that resolve to version_records",
                observed_condition="no normalized records were supplied for version resolution",
                failure_ids=[],
                severity="warning",
                error_code=None,
                source_ref=self._first_or_default(input_refs),
                timestamp=executed_at,
            )
            notes.append(
                self._coverage_note(case_name, "skipped", "normalized_records is empty")
            )
            return result, failures, notes

        observed_parts: List[str] = []
        version_index = accepted["version_index"]
        for record in normalized_records:
            record_ref = self._record_ref(record)
            version_ref = self._mapping_string(record, "version_ref")
            if not version_ref or version_ref not in version_index:
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="unresolved_reference",
                        affected_object_ref=record_ref,
                        expected_ref="version_records.version_id",
                        observed_value=version_ref or "missing",
                        source_input_refs=[record_ref],
                        severity="critical",
                        owner_motor_ref="motor_005",
                        recommended_action=(
                            "Emit normalized records with a version_ref that exists in the supplied version_records batch."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(f"{record_ref}: version_ref unresolved")
                continue

            version_record = version_index[version_ref]
            if not self._has_lineage_or_provenance(record) and not self._has_lineage_or_provenance(
                version_record
            ):
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="lineage_gap",
                        affected_object_ref=record_ref,
                        expected_ref=version_ref,
                        observed_value="no lineage_refs or provenance_refs on record or version evidence",
                        source_input_refs=[record_ref, version_ref],
                        severity="critical",
                        owner_motor_ref="motor_005",
                        recommended_action=(
                            "Provide lineage_refs or provenance_refs sufficient to reconstruct the normalized object."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(f"{record_ref}: version resolves but lineage is absent")
            else:
                observed_parts.append(f"{record_ref}: {version_ref} resolves with trace evidence")

        status = "fail" if failures else "pass"
        error_code = self._first_error_code(
            failures,
            {
                "unresolved_reference": "UNRESOLVED_REFERENCE",
                "lineage_gap": "LINEAGE_GAP",
            },
        )
        result = self._make_result(
            harness_run_id=harness_run_id,
            test_id=test_id,
            case_name=case_name,
            status=status,
            input_refs=input_refs,
            expected_condition="each normalized record version_ref resolves and preserves lineage or provenance evidence",
            observed_condition="; ".join(observed_parts),
            failure_ids=[failure.failure_id for failure in failures],
            severity="critical" if failures else "info",
            error_code=error_code,
            source_ref=self._first_or_default(input_refs),
            timestamp=executed_at,
        )
        return result, failures, notes

    def _case_taxonomy_refs_allowed(
        self,
        harness_run_id: str,
        accepted: Mapping[str, Any],
        executed_at: str,
    ) -> Tuple[TestResult, List[IntegrationFailure], List[Dict[str, Any]]]:
        case_name = "taxonomy_refs_allowed"
        input_refs = self._case_input_refs(
            accepted,
            include_taxonomy=True,
            include_normalized=True,
        )
        test_id = self._test_id(harness_run_id, case_name, input_refs)
        failures: List[IntegrationFailure] = []
        notes: List[Dict[str, Any]] = []
        normalized_records = accepted["normalized_records"]

        if not normalized_records:
            result = self._make_result(
                harness_run_id=harness_run_id,
                test_id=test_id,
                case_name=case_name,
                status="skipped",
                input_refs=input_refs,
                expected_condition="observed taxonomy_refs appear in the canonical taxonomy snapshot",
                observed_condition="no normalized records were supplied for taxonomy validation",
                failure_ids=[],
                severity="warning",
                error_code=None,
                source_ref=self._first_or_default(input_refs),
                timestamp=executed_at,
            )
            notes.append(
                self._coverage_note(case_name, "skipped", "normalized_records is empty")
            )
            return result, failures, notes

        allowed_terms = accepted["allowed_terms"]
        taxonomy_ref = accepted["taxonomy_ref"]
        observed_parts: List[str] = []
        for record in normalized_records:
            record_ref = self._record_ref(record)
            taxonomy_refs = self._as_string_list(record.get("taxonomy_refs"))
            if not taxonomy_refs:
                observed_parts.append(f"{record_ref}: no observed taxonomy_refs")
                continue
            invalid_terms = [term for term in taxonomy_refs if term not in allowed_terms]
            if invalid_terms:
                for term in invalid_terms:
                    failures.append(
                        self._make_failure(
                            harness_run_id=harness_run_id,
                            test_id=test_id,
                            failure_type="taxonomy_mismatch",
                            affected_object_ref=record_ref,
                            expected_ref=taxonomy_ref,
                            observed_value=term,
                            source_input_refs=[record_ref, taxonomy_ref],
                            severity="critical",
                            owner_motor_ref="motor_005",
                            recommended_action=(
                                "Use only terms present in the supplied canonical taxonomy snapshot."
                            ),
                            timestamp=executed_at,
                        )
                    )
                observed_parts.append(
                    f"{record_ref}: invalid taxonomy_refs {','.join(invalid_terms)}"
                )
            else:
                observed_parts.append(
                    f"{record_ref}: taxonomy_refs allowed {','.join(taxonomy_refs)}"
                )

        status = "fail" if failures else "pass"
        result = self._make_result(
            harness_run_id=harness_run_id,
            test_id=test_id,
            case_name=case_name,
            status=status,
            input_refs=input_refs,
            expected_condition="each observed taxonomy_ref is present in the supplied canonical taxonomy snapshot",
            observed_condition="; ".join(observed_parts),
            failure_ids=[failure.failure_id for failure in failures],
            severity="critical" if failures else "info",
            error_code="TAXONOMY_MISMATCH" if failures else None,
            source_ref=self._first_or_default(input_refs),
            timestamp=executed_at,
        )
        return result, failures, notes

    def _case_identity_ref_resolves(
        self,
        harness_run_id: str,
        accepted: Mapping[str, Any],
        executed_at: str,
    ) -> Tuple[TestResult, List[IntegrationFailure], List[Dict[str, Any]]]:
        case_name = "identity_ref_resolves"
        input_refs = self._case_input_refs(
            accepted,
            include_normalized=True,
            include_identities=True,
        )
        test_id = self._test_id(harness_run_id, case_name, input_refs)
        failures: List[IntegrationFailure] = []
        notes: List[Dict[str, Any]] = []
        normalized_records = accepted["normalized_records"]

        if not normalized_records:
            result = self._make_result(
                harness_run_id=harness_run_id,
                test_id=test_id,
                case_name=case_name,
                status="skipped",
                input_refs=input_refs,
                expected_condition="entity references used by normalized records resolve to compatible identity records",
                observed_condition="no normalized records were supplied for identity validation",
                failure_ids=[],
                severity="warning",
                error_code=None,
                source_ref=self._first_or_default(input_refs),
                timestamp=executed_at,
            )
            notes.append(
                self._coverage_note(case_name, "skipped", "normalized_records is empty")
            )
            return result, failures, notes

        identities_by_entity = self._group_by_string_field(
            accepted["identity_records"],
            "entity_ref",
        )
        observed_parts: List[str] = []
        for record in normalized_records:
            record_ref = self._record_ref(record)
            entity_ref = self._entity_ref(record)
            if not entity_ref:
                observed_parts.append(f"{record_ref}: no entity_ref observed")
                continue

            matching = identities_by_entity.get(entity_ref, [])
            if not matching:
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="identity_conflict",
                        affected_object_ref=record_ref,
                        expected_ref="identity_records.entity_ref",
                        observed_value=entity_ref,
                        source_input_refs=[record_ref],
                        severity="critical",
                        owner_motor_ref="motor_006",
                        recommended_action=(
                            "Provide an identity record that resolves the normalized object's entity_ref."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(f"{record_ref}: {entity_ref} does not resolve")
                continue

            identity = matching[0]
            identity_ref = self._mapping_string(identity, "identity_id")
            canonical_entity_id = self._mapping_string(identity, "canonical_entity_id")
            if self._as_string_list(identity.get("alias_refs")):
                observed_parts.append(
                    f"{identity_ref} resolves {entity_ref} to {canonical_entity_id} with alias evidence"
                )
            else:
                observed_parts.append(
                    f"{identity_ref} resolves {entity_ref} to {canonical_entity_id} without alias evidence"
                )
                notes.append(
                    self._coverage_note(
                        case_name,
                        "optional_alias_absent",
                        f"{identity_ref} has no alias_refs",
                    )
                )

        status = "fail" if failures else "pass"
        result = self._make_result(
            harness_run_id=harness_run_id,
            test_id=test_id,
            case_name=case_name,
            status=status,
            input_refs=input_refs,
            expected_condition="entity references used by normalized records resolve to compatible identity records",
            observed_condition="; ".join(observed_parts),
            failure_ids=[failure.failure_id for failure in failures],
            severity="critical" if failures else "info",
            error_code="UNRESOLVED_REFERENCE" if failures else None,
            source_ref=self._first_or_default(input_refs),
            timestamp=executed_at,
        )
        return result, failures, notes

    def _case_quality_record_present(
        self,
        harness_run_id: str,
        accepted: Mapping[str, Any],
        executed_at: str,
    ) -> Tuple[TestResult, List[IntegrationFailure], List[Dict[str, Any]]]:
        case_name = "quality_record_present"
        input_refs = self._case_input_refs(
            accepted,
            include_contracts=True,
            include_normalized=True,
            include_quality=True,
        )
        test_id = self._test_id(harness_run_id, case_name, input_refs)
        failures: List[IntegrationFailure] = []
        notes: List[Dict[str, Any]] = []
        normalized_records = accepted["normalized_records"]

        if not normalized_records:
            result = self._make_result(
                harness_run_id=harness_run_id,
                test_id=test_id,
                case_name=case_name,
                status="skipped",
                input_refs=input_refs,
                expected_condition="quality records exist when phase handoff rules require them",
                observed_condition="no normalized records were supplied for quality evidence validation",
                failure_ids=[],
                severity="warning",
                error_code=None,
                source_ref=self._first_or_default(input_refs),
                timestamp=executed_at,
            )
            notes.append(
                self._coverage_note(case_name, "skipped", "normalized_records is empty")
            )
            return result, failures, notes

        quality_by_subject = accepted["quality_by_subject"]
        observed_parts: List[str] = []
        warning_detected = False

        for record in normalized_records:
            record_ref = self._record_ref(record)
            contract = self._contract_for_record(record, accepted["phase_contracts"])
            contract_ref = self._mapping_string(contract, "contract_id") if contract else ""
            requires_quality = self._contract_requires_quality(contract)
            if not requires_quality:
                observed_parts.append(f"{record_ref}: quality record not required")
                continue

            matching_quality = quality_by_subject.get(record_ref, [])
            if contract_ref:
                matching_quality = [
                    quality
                    for quality in matching_quality
                    if not self._mapping_string(quality, "phase_contract_ref")
                    or self._mapping_string(quality, "phase_contract_ref") == contract_ref
                ]

            if not matching_quality:
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="quality_missing",
                        affected_object_ref=record_ref,
                        expected_ref=contract_ref or "phase_contract.handoff_rules.requires_quality_record",
                        observed_value="missing quality_record",
                        source_input_refs=[record_ref] + ([contract_ref] if contract_ref else []),
                        severity="critical",
                        owner_motor_ref="motor_007",
                        recommended_action=(
                            "Produce a quality record for the normalized object before integration handoff."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(f"{record_ref}: required quality_record is missing")
                continue

            quality = matching_quality[0]
            quality_ref = self._mapping_string(quality, "quality_record_id")
            evaluation_status = self._mapping_string(quality, "evaluation_status")
            if evaluation_status == "pass":
                observed_parts.append(f"{record_ref}: quality_record {quality_ref} passes")
            elif evaluation_status == "conditional_pass" and self._contract_allows_conditional_quality(
                contract
            ):
                observed_parts.append(
                    f"{record_ref}: quality_record {quality_ref} conditionally passes under contract policy"
                )
            elif evaluation_status == "conditional_pass":
                warning_detected = True
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="quality_missing",
                        affected_object_ref=record_ref,
                        expected_ref=f"{contract_ref}.quality_status.pass",
                        observed_value="conditional_pass",
                        source_input_refs=[record_ref, quality_ref, contract_ref],
                        severity="warning",
                        owner_motor_ref="motor_007",
                        recommended_action=(
                            "Provide strict pass quality evidence or update the phase contract to permit conditional quality status."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(
                    f"{record_ref}: quality_record {quality_ref} is conditional while strict pass is required"
                )
            else:
                failures.append(
                    self._make_failure(
                        harness_run_id=harness_run_id,
                        test_id=test_id,
                        failure_type="quality_missing",
                        affected_object_ref=record_ref,
                        expected_ref=f"{contract_ref}.quality_status.pass",
                        observed_value=evaluation_status or "missing evaluation_status",
                        source_input_refs=[record_ref, quality_ref, contract_ref],
                        severity="critical",
                        owner_motor_ref="motor_007",
                        recommended_action=(
                            "Produce passing quality evidence for the object before integration handoff."
                        ),
                        timestamp=executed_at,
                    )
                )
                observed_parts.append(
                    f"{record_ref}: quality_record {quality_ref} has status {evaluation_status or 'missing'}"
                )

        critical_failures = [failure for failure in failures if failure.severity == "critical"]
        status = "fail" if critical_failures else "warning" if warning_detected else "pass"
        result = self._make_result(
            harness_run_id=harness_run_id,
            test_id=test_id,
            case_name=case_name,
            status=status,
            input_refs=input_refs,
            expected_condition="objects with required quality handoff rules have acceptable quality records",
            observed_condition="; ".join(observed_parts),
            failure_ids=[failure.failure_id for failure in failures],
            severity="critical" if critical_failures else "warning" if warning_detected else "info",
            error_code="CONTRACT_MISMATCH" if failures else None,
            source_ref=self._first_or_default(input_refs),
            timestamp=executed_at,
        )
        return result, failures, notes

    def _build_report(
        self,
        harness_run_id: str,
        accepted: Mapping[str, Any],
        results: Sequence[TestResult],
        failures: Sequence[IntegrationFailure],
        coverage_notes: Sequence[Mapping[str, Any]],
        timestamp: str,
    ) -> HarnessReport:
        result_counts = {status: 0 for status in ["pass", "warning", "fail", "skipped"]}
        result_counts.update(Counter(result.status for result in results))
        critical_failure_present = any(
            failure.severity == "critical" for failure in failures
        )
        failed_result_present = any(result.status == "fail" for result in results)
        warning_or_skipped_present = any(
            result.status in {"warning", "skipped"} for result in results
        ) or any(failure.severity == "warning" for failure in failures)

        if critical_failure_present or failed_result_present:
            status = "fail"
            decision_reason = "failed result or critical integration failure detected"
        elif warning_or_skipped_present:
            status = "warning"
            decision_reason = "required coverage was skipped or warning-level degradation was detected"
        else:
            status = "pass"
            decision_reason = "all required harness cases passed with no integration failures"

        tested_contract_refs = sorted(
            self._mapping_string(contract, "contract_id")
            for contract in accepted["phase_contracts"]
        )
        tested_object_refs = sorted(
            ref
            for ref in (
                [self._mapping_string(record, "record_id") for record in accepted["normalized_records"]]
                + [self._mapping_string(record, "identity_id") for record in accepted["identity_records"]]
                + [self._mapping_string(record, "quality_record_id") for record in accepted["quality_records"]]
                + [self._mapping_string(record, "version_id") for record in accepted["version_records"]]
                + [accepted["taxonomy_ref"]]
            )
            if ref
        )
        required_cases_skipped = [
            note for note in coverage_notes if note.get("status") == "skipped"
        ]
        coverage_summary = {
            "required_cases": list(CASE_NAMES),
            "required_cases_executed": [
                result.case_name for result in results if result.status != "skipped"
            ],
            "required_cases_skipped": required_cases_skipped,
            "coverage_notes": [dict(note) for note in coverage_notes],
            "objects_covered": len(tested_object_refs),
            "contracts_covered": len(tested_contract_refs),
            "input_ref_count": len(self._accepted_input_refs(accepted)),
        }
        failure_ids = [failure.failure_id for failure in failures]

        report_data = {
            "harness_run_id": harness_run_id,
            "harness_version": self.harness_version,
            "test_result_ids": [result.test_id for result in results],
            "tested_contract_refs": tested_contract_refs,
            "tested_object_refs": tested_object_refs,
            "result_counts": result_counts,
            "coverage_summary": coverage_summary,
            "failure_ids": failure_ids,
            "failure_log_ref": None,
            "status": status,
            "decision_reason": decision_reason,
            "generated_at": timestamp,
            "version_id": self._version_id("harness_report", harness_run_id),
            "created_at": timestamp,
            "updated_at": timestamp,
            "version_hash": "",
            "source_ref": self._source_ref_for_report(accepted),
            "produced_by_motor": MOTOR_ID,
            "produced_at": timestamp,
            "parent_id": None,
        }
        report_data["version_hash"] = self._semantic_hash(report_data)
        return HarnessReport(**report_data)

    def _validate_report(
        self,
        report: HarnessReport,
        results: Sequence[TestResult],
        failures: Sequence[IntegrationFailure],
    ) -> None:
        observed_counts = {status: 0 for status in ["pass", "warning", "fail", "skipped"]}
        observed_counts.update(Counter(result.status for result in results))
        if report.result_counts != observed_counts:
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "HarnessReport.result_counts does not match TestResult statuses.",
                {"expected": observed_counts, "observed": report.result_counts},
            )

        result_ids = [result.test_id for result in results]
        if report.test_result_ids != result_ids:
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "HarnessReport.test_result_ids does not match emitted TestResult records.",
            )

        failure_ids = [failure.failure_id for failure in failures]
        if report.failure_ids != failure_ids:
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "HarnessReport.failure_ids does not match integration_failure_log.",
            )

        failure_id_set = set(failure_ids)
        for result in results:
            missing_failure_ids = [
                failure_id
                for failure_id in result.failure_ids
                if failure_id not in failure_id_set
            ]
            if missing_failure_ids:
                raise UnsafeHarnessReportError(
                    "UNSAFE_HARNESS_REPORT",
                    "A TestResult links failure IDs absent from the failure log.",
                    {"test_id": result.test_id, "missing_failure_ids": missing_failure_ids},
                )

        if report.status == "pass" and (
            any(result.status == "fail" for result in results)
            or any(failure.severity == "critical" for failure in failures)
        ):
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "HarnessReport.status pass contradicts failed results or critical failures.",
            )

    def _make_result(
        self,
        *,
        harness_run_id: str,
        test_id: str,
        case_name: str,
        status: str,
        input_refs: Sequence[str],
        expected_condition: str,
        observed_condition: str,
        failure_ids: Sequence[str],
        severity: str,
        error_code: Optional[str],
        source_ref: str,
        timestamp: str,
    ) -> TestResult:
        if status not in RESULT_STATUSES or severity not in RESULT_SEVERITIES:
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "TestResult status or severity is outside the declared enum.",
                {"status": status, "severity": severity},
            )
        if error_code is not None and error_code not in ERROR_CODES:
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "TestResult error_code is outside the declared enum.",
                {"error_code": error_code},
            )
        result_data = {
            "test_id": test_id,
            "harness_run_id": harness_run_id,
            "case_name": case_name,
            "case_version": self.case_version,
            "status": status,
            "input_refs": list(input_refs),
            "expected_condition": expected_condition,
            "observed_condition": observed_condition,
            "failure_ids": list(failure_ids),
            "severity": severity,
            "error_code": error_code,
            "harness_version": self.harness_version,
            "executed_at": timestamp,
            "version_id": self._version_id("test_result", test_id),
            "created_at": timestamp,
            "updated_at": timestamp,
            "version_hash": "",
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "produced_at": timestamp,
            "parent_id": harness_run_id,
        }
        result_data["version_hash"] = self._semantic_hash(result_data)
        return TestResult(**result_data)

    def _make_failure(
        self,
        *,
        harness_run_id: str,
        test_id: str,
        failure_type: str,
        affected_object_ref: str,
        expected_ref: str,
        observed_value: str,
        source_input_refs: Sequence[str],
        severity: str,
        owner_motor_ref: str,
        recommended_action: str,
        timestamp: str,
    ) -> IntegrationFailure:
        if severity not in FAILURE_SEVERITIES:
            raise UnsafeHarnessReportError(
                "UNSAFE_HARNESS_REPORT",
                "IntegrationFailure severity is outside the declared enum.",
                {"severity": severity},
            )
        canonical_source_refs = [ref for ref in source_input_refs if ref]
        failure_id = self._failure_id(
            harness_run_id,
            test_id,
            failure_type,
            affected_object_ref,
            expected_ref,
            observed_value,
        )
        failure_data = {
            "failure_id": failure_id,
            "harness_run_id": harness_run_id,
            "test_id": test_id,
            "failure_type": failure_type,
            "affected_object_ref": affected_object_ref,
            "expected_ref": expected_ref,
            "observed_value": observed_value,
            "source_input_refs": canonical_source_refs,
            "severity": severity,
            "owner_motor_ref": owner_motor_ref,
            "recommended_action": recommended_action,
            "detected_at": timestamp,
            "version_id": self._version_id("integration_failure", failure_id),
            "created_at": timestamp,
            "updated_at": timestamp,
            "version_hash": "",
            "source_ref": self._first_or_default(canonical_source_refs),
            "produced_by_motor": MOTOR_ID,
            "produced_at": timestamp,
            "parent_id": test_id,
        }
        failure_data["version_hash"] = self._semantic_hash(failure_data)
        return IntegrationFailure(**failure_data)

    def _ensure_sequence_of_mappings(
        self,
        input_name: str,
        value: Any,
    ) -> List[Mapping[str, Any]]:
        if isinstance(value, (str, bytes)) or not isinstance(value, Sequence):
            raise HarnessInputError(
                "INVALID_HARNESS_INPUT",
                f"{input_name} must be a collection of structured objects.",
                {"input_name": input_name, "observed_type": type(value).__name__},
            )
        output: List[Mapping[str, Any]] = []
        for index, item in enumerate(value):
            if not isinstance(item, Mapping):
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    f"{input_name}[{index}] must be a structured object.",
                    {
                        "input_name": input_name,
                        "index": index,
                        "observed_type": type(item).__name__,
                    },
                )
            output.append(item)
        return output

    def _index_contracts(
        self,
        contracts: Sequence[Mapping[str, Any]],
    ) -> Dict[str, Mapping[str, Any]]:
        contract_index: Dict[str, Mapping[str, Any]] = {}
        for index, contract in enumerate(contracts):
            missing = [
                field
                for field in ["contract_id", "phase_id", "required_outputs", "field_requirements", "status"]
                if not self._field_present(contract, field)
            ]
            if not self._field_present(contract, "version") and not self._field_present(
                contract,
                "contract_version",
            ):
                missing.append("version")
            if missing:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "phase_contract is missing required contract fields.",
                    {"index": index, "missing_fields": missing},
                )
            status = self._mapping_string(contract, "status").lower()
            if status not in APPROVED_CONTRACT_STATUSES:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "phase_contract status is not approved for harness testing.",
                    {
                        "contract_id": self._mapping_string(contract, "contract_id"),
                        "status": status,
                    },
                )
            contract_id = self._mapping_string(contract, "contract_id")
            if contract_id in contract_index:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "phase_contract contract_id is duplicated.",
                    {"contract_id": contract_id},
                )
            contract_index[contract_id] = contract
        return contract_index

    def _index_version_records(
        self,
        version_records: Sequence[Mapping[str, Any]],
    ) -> Dict[str, Mapping[str, Any]]:
        version_index: Dict[str, Mapping[str, Any]] = {}
        required = ["version_id", "object_id", "object_type", "object_version", "created_at"]
        for index, version in enumerate(version_records):
            missing = [
                field for field in required if not self._field_present(version, field)
            ]
            if not self._has_lineage_or_provenance(version):
                missing.append("lineage_refs_or_provenance_refs")
            if missing:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "version_record is missing required version or traceability fields.",
                    {"index": index, "missing_fields": missing},
                )
            version_id = self._mapping_string(version, "version_id")
            if version_id in version_index:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "version_record version_id is duplicated.",
                    {"version_id": version_id},
                )
            version_index[version_id] = version
        return version_index

    def _validate_taxonomy(
        self,
        taxonomy: Mapping[str, Any],
    ) -> Tuple[str, set]:
        missing = [
            field
            for field in ["taxonomy_id", "taxonomy_version", "allowed_terms", "object_type_registry"]
            if not self._field_present(taxonomy, field)
        ]
        if missing:
            raise HarnessInputError(
                "INVALID_HARNESS_INPUT",
                "canonical_taxonomy is missing required authority fields.",
                {"missing_fields": missing},
            )
        taxonomy_ref = (
            f"{self._mapping_string(taxonomy, 'taxonomy_id')}:"
            f"{self._mapping_string(taxonomy, 'taxonomy_version')}"
        )
        allowed_terms = set(self._as_string_list(taxonomy.get("allowed_terms")))
        if not allowed_terms:
            raise HarnessInputError(
                "INVALID_HARNESS_INPUT",
                "canonical_taxonomy.allowed_terms must contain at least one term.",
                {"taxonomy_ref": taxonomy_ref},
            )
        return taxonomy_ref, allowed_terms

    def _index_by_required_id(
        self,
        input_name: str,
        objects: Sequence[Mapping[str, Any]],
        id_field: str,
    ) -> Dict[str, Mapping[str, Any]]:
        index: Dict[str, Mapping[str, Any]] = {}
        for position, item in enumerate(objects):
            item_id = self._mapping_string(item, id_field)
            if not item_id:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    f"{input_name}[{position}] is missing {id_field}.",
                    {"input_name": input_name, "index": position, "id_field": id_field},
                )
            if item_id in index:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    f"{input_name} contains duplicate {id_field}.",
                    {"input_name": input_name, "id": item_id},
                )
            index[item_id] = item
        return index

    def _validate_identity_records(
        self,
        identities: Sequence[Mapping[str, Any]],
    ) -> None:
        for index, identity in enumerate(identities):
            missing = [
                field
                for field in ["identity_id", "entity_ref", "canonical_entity_id"]
                if not self._field_present(identity, field)
            ]
            if not self._field_present(identity, "lineage_refs") and not self._field_present(
                identity,
                "version_ref",
            ):
                missing.append("lineage_refs_or_version_ref")
            if missing:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "identity_record is missing required identity fields.",
                    {"index": index, "missing_fields": missing},
                )

    def _validate_quality_records(
        self,
        quality_records: Sequence[Mapping[str, Any]],
    ) -> None:
        for index, quality in enumerate(quality_records):
            missing = [
                field
                for field in ["quality_record_id", "subject_ref", "evaluation_status", "evaluated_at"]
                if not self._field_present(quality, field)
            ]
            if not self._field_present(quality, "phase_contract_ref") and not self._field_present(
                quality,
                "version_ref",
            ):
                missing.append("phase_contract_ref_or_version_ref")
            if missing:
                raise HarnessInputError(
                    "INVALID_HARNESS_INPUT",
                    "quality_record is missing required quality fields.",
                    {"index": index, "missing_fields": missing},
                )

    def _contract_for_record(
        self,
        record: Mapping[str, Any],
        contracts: Sequence[Mapping[str, Any]],
    ) -> Optional[Mapping[str, Any]]:
        schema_ref = self._mapping_string(record, "schema_ref")
        if schema_ref:
            for contract in contracts:
                if self._mapping_string(contract, "contract_id") == schema_ref:
                    return contract
            return None

        for contract in contracts:
            if "normalized_record" in self._contract_required_outputs(contract):
                return contract
        return contracts[0] if contracts else None

    def _contract_required_fields(self, contract: Mapping[str, Any]) -> List[str]:
        raw = contract.get("field_requirements")
        if isinstance(raw, Mapping):
            if isinstance(raw.get("required_fields"), Sequence) and not isinstance(
                raw.get("required_fields"),
                (str, bytes),
            ):
                return self._as_string_list(raw.get("required_fields"))
            return [str(key).strip() for key in raw.keys() if str(key).strip()]
        return self._as_string_list(raw)

    def _contract_required_outputs(self, contract: Mapping[str, Any]) -> List[str]:
        return self._as_string_list(contract.get("required_outputs"))

    def _contract_requires_quality(self, contract: Optional[Mapping[str, Any]]) -> bool:
        if not contract:
            return False
        handoff_rules = contract.get("handoff_rules")
        if isinstance(handoff_rules, Mapping):
            value = handoff_rules.get("requires_quality_record")
            if isinstance(value, bool):
                return value
            if isinstance(value, str):
                return value.strip().lower() in {"true", "yes", "required", "1"}
        value = contract.get("requires_quality_record")
        if isinstance(value, bool):
            return value
        if isinstance(value, str):
            return value.strip().lower() in {"true", "yes", "required", "1"}
        return False

    def _contract_allows_conditional_quality(
        self,
        contract: Optional[Mapping[str, Any]],
    ) -> bool:
        if not contract:
            return False
        handoff_rules = contract.get("handoff_rules")
        if isinstance(handoff_rules, Mapping):
            if handoff_rules.get("allows_conditional_quality") is True:
                return True
            allowed_statuses = self._as_string_list(
                handoff_rules.get("allowed_quality_statuses")
            )
            if "conditional_pass" in allowed_statuses:
                return True
        policy = contract.get("quality_policy")
        if isinstance(policy, Mapping):
            allowed_statuses = self._as_string_list(policy.get("allowed_statuses"))
            if "conditional_pass" in allowed_statuses:
                return True
        return False

    def _field_present(self, item: Mapping[str, Any], field: str) -> bool:
        value = self._field_value(item, field)
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, (Sequence, Mapping)) and not isinstance(value, (str, bytes)):
            return bool(value)
        return True

    def _field_value(self, item: Mapping[str, Any], field: str) -> Any:
        if "." in field:
            current: Any = item
            for part in field.split("."):
                if not isinstance(current, Mapping) or part not in current:
                    return None
                current = current[part]
            return current
        if field in item:
            return item[field]
        field_values = item.get("field_values")
        if isinstance(field_values, Mapping) and field in field_values:
            return field_values[field]
        return None

    def _has_lineage_or_provenance(self, item: Mapping[str, Any]) -> bool:
        return self._field_present(item, "lineage_refs") or self._field_present(
            item,
            "provenance_refs",
        )

    def _entity_ref(self, record: Mapping[str, Any]) -> str:
        direct = self._mapping_string(record, "entity_ref")
        if direct:
            return direct
        field_values = record.get("field_values")
        if isinstance(field_values, Mapping):
            value = field_values.get("entity_ref")
            if value is not None:
                return str(value).strip()
        return ""

    def _mapping_string(self, item: Optional[Mapping[str, Any]], field: str) -> str:
        if not item:
            return ""
        value = item.get(field)
        if value is None:
            return ""
        return str(value).strip()

    def _as_string_list(self, value: Any) -> List[str]:
        if value is None:
            return []
        if isinstance(value, Mapping):
            return [
                str(key).strip()
                for key in value.keys()
                if str(key).strip()
            ]
        if isinstance(value, (str, bytes)):
            return [str(value).strip()] if str(value).strip() else []
        if isinstance(value, Sequence) or isinstance(value, set):
            output: List[str] = []
            for item in value:
                if isinstance(item, Mapping):
                    ref = (
                        item.get("term_id")
                        or item.get("id")
                        or item.get("name")
                        or item.get("ref")
                    )
                    if ref is not None and str(ref).strip():
                        output.append(str(ref).strip())
                elif item is not None and str(item).strip():
                    output.append(str(item).strip())
            return output
        return [str(value).strip()] if str(value).strip() else []

    def _record_ref(self, record: Mapping[str, Any]) -> str:
        return self._mapping_string(record, "record_id") or self._primary_ref(record)

    def _primary_ref(self, item: Mapping[str, Any]) -> str:
        for field in [
            "record_id",
            "contract_id",
            "version_id",
            "taxonomy_id",
            "identity_id",
            "quality_record_id",
            "object_id",
        ]:
            value = self._mapping_string(item, field)
            if value:
                return value
        return self._semantic_hash(dict(item))[:16]

    def _group_by_string_field(
        self,
        items: Sequence[Mapping[str, Any]],
        field: str,
    ) -> Dict[str, List[Mapping[str, Any]]]:
        grouped: Dict[str, List[Mapping[str, Any]]] = {}
        for item in items:
            ref = self._mapping_string(item, field)
            if ref:
                grouped.setdefault(ref, []).append(item)
        return grouped

    def _case_input_refs(
        self,
        accepted: Mapping[str, Any],
        *,
        include_contracts: bool = False,
        include_versions: bool = False,
        include_taxonomy: bool = False,
        include_normalized: bool = False,
        include_identities: bool = False,
        include_quality: bool = False,
    ) -> List[str]:
        refs: List[str] = []
        if include_contracts:
            refs.extend(
                self._mapping_string(contract, "contract_id")
                for contract in accepted["phase_contracts"]
            )
        if include_versions:
            refs.extend(
                self._mapping_string(version, "version_id")
                for version in accepted["version_records"]
            )
        if include_taxonomy:
            refs.append(accepted["taxonomy_ref"])
        if include_normalized:
            refs.extend(
                self._mapping_string(record, "record_id")
                for record in accepted["normalized_records"]
            )
        if include_identities:
            refs.extend(
                self._mapping_string(identity, "identity_id")
                for identity in accepted["identity_records"]
            )
        if include_quality:
            refs.extend(
                self._mapping_string(quality, "quality_record_id")
                for quality in accepted["quality_records"]
            )
        return sorted(ref for ref in refs if ref)

    def _accepted_input_refs(self, accepted: Mapping[str, Any]) -> List[str]:
        refs = (
            self._case_input_refs(
                accepted,
                include_contracts=True,
                include_versions=True,
                include_taxonomy=True,
                include_normalized=True,
                include_identities=True,
                include_quality=True,
            )
        )
        return sorted(refs)

    def _source_ref_for_report(self, accepted: Mapping[str, Any]) -> str:
        refs = self._accepted_input_refs(accepted)
        return "input-set:" + self._hash_payload(refs)

    def _coverage_note(
        self,
        case_name: str,
        status: str,
        reason: str,
    ) -> Dict[str, Any]:
        return {
            "case_name": case_name,
            "status": status,
            "reason": reason,
        }

    def _first_or_default(self, values: Sequence[str]) -> str:
        for value in values:
            if value:
                return value
        return "input-set:empty"

    def _first_error_code(
        self,
        failures: Sequence[IntegrationFailure],
        mapping: Mapping[str, str],
    ) -> Optional[str]:
        for failure in failures:
            code = mapping.get(failure.failure_type)
            if code:
                return code
        return None

    def _harness_run_id(self, accepted: Mapping[str, Any]) -> str:
        payload = {
            "motor_id": MOTOR_ID,
            "harness_version": self.harness_version,
            "case_names": CASE_NAMES,
            "input_refs": self._accepted_input_refs(accepted),
        }
        return "HR-021-" + self._hash_payload(payload)[:16]

    def _test_id(
        self,
        harness_run_id: str,
        case_name: str,
        input_refs: Sequence[str],
    ) -> str:
        payload = {
            "motor_id": MOTOR_ID,
            "harness_run_id": harness_run_id,
            "case_name": case_name,
            "input_refs": list(input_refs),
            "harness_version": self.harness_version,
        }
        return "TR-021-" + self._hash_payload(payload)[:16]

    def _failure_id(
        self,
        harness_run_id: str,
        test_id: str,
        failure_type: str,
        affected_object_ref: str,
        expected_ref: str,
        observed_value: str,
    ) -> str:
        payload = {
            "motor_id": MOTOR_ID,
            "harness_run_id": harness_run_id,
            "test_id": test_id,
            "failure_type": failure_type,
            "affected_object_ref": affected_object_ref,
            "expected_ref": expected_ref,
            "observed_value": observed_value,
        }
        return "IF-021-" + self._hash_payload(payload)[:16]

    def _version_id(self, entity_type: str, entity_id: str) -> str:
        return "VER-021-" + self._hash_payload(
            {
                "entity_type": entity_type,
                "entity_id": entity_id,
                "harness_version": self.harness_version,
            }
        )[:16]

    def _semantic_hash(self, payload: Mapping[str, Any]) -> str:
        semantic_payload = {
            key: value
            for key, value in payload.items()
            if key not in TIME_FIELDS and key != "version_hash"
        }
        return self._hash_payload(semantic_payload)

    def _hash_payload(self, payload: Any) -> str:
        serialized = json.dumps(
            self._canonicalize(payload),
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
        )
        return sha256(serialized.encode("utf-8")).hexdigest()

    def _canonicalize(self, value: Any) -> Any:
        if isinstance(value, Mapping):
            return {
                str(key): self._canonicalize(value[key])
                for key in sorted(value.keys(), key=lambda item: str(item))
            }
        if isinstance(value, (list, tuple)):
            return [self._canonicalize(item) for item in value]
        if isinstance(value, set):
            return [self._canonicalize(item) for item in sorted(value, key=str)]
        if value is None or isinstance(value, (str, int, float, bool)):
            return value
        return str(value)
