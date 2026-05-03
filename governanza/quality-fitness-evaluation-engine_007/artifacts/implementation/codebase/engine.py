"""Deterministic quality and fitness evaluation for motor_007."""

from __future__ import annotations

from copy import deepcopy
import hashlib
import json
from collections.abc import Mapping, Sequence
from typing import Any, Dict, Iterable, List, Optional, Tuple

from .errors import QualityFitnessEvaluationError
from .models import (
    DisqualificationReason,
    FitnessScore,
    QualityFlag,
    QualityRecord,
)


MOTOR_ID = "motor_007"
DEFAULT_TIMESTAMP = "1970-01-01T00:00:00Z"
DEFAULT_SCORING_RULE_VERSION = "quality_rules_v1"
EVALUATED_DIMENSIONS = [
    "completeness",
    "traceability",
    "contract_consistency",
    "fitness",
]
INACTIVE_CONTRACT_STATUSES = {"deprecated", "retired", "inactive", "superseded"}


class QualityFitnessEvaluationEngine:
    """Evaluate identity-resolved records against phase contracts without mutation."""

    def evaluate(
        self,
        identity_resolved_records: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        evaluation_context: Mapping[str, Any],
    ) -> Dict[str, List[Dict[str, Any]]]:
        records_snapshot = deepcopy(identity_resolved_records)
        contracts_snapshot = deepcopy(phase_contracts)

        self._validate_batch_inputs(
            identity_resolved_records,
            phase_contracts,
            evaluation_context,
        )

        valid_contracts = [
            self._validate_contract(contract) for contract in phase_contracts
        ]
        produced_at = self._context_timestamp(evaluation_context)

        quality_records: List[QualityRecord] = []
        for index, record in enumerate(identity_resolved_records):
            self._validate_record_shell(record, index)
            contract = self._select_contract(record, valid_contracts)
            quality_records.append(
                self._evaluate_record(record, contract, evaluation_context, produced_at)
            )

        if records_snapshot != identity_resolved_records:
            raise QualityFitnessEvaluationError(
                "QUALITY_INPUT_MUTATED",
                "identity_resolved_records changed during evaluation.",
            )
        if contracts_snapshot != phase_contracts:
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_MUTATED",
                "phase_contracts changed during evaluation.",
            )

        return {
            "quality_record": [record.to_dict() for record in quality_records],
        }

    def safe_evaluate(
        self,
        identity_resolved_records: Any,
        phase_contracts: Any,
        evaluation_context: Any,
    ) -> Dict[str, Any]:
        """Return a structured rejection payload instead of raising."""

        try:
            return self.evaluate(
                identity_resolved_records,
                phase_contracts,
                evaluation_context,
            )
        except QualityFitnessEvaluationError as exc:
            return exc.to_dict()

    def _evaluate_record(
        self,
        record: Mapping[str, Any],
        contract: Mapping[str, Any],
        evaluation_context: Mapping[str, Any],
        produced_at: str,
    ) -> QualityRecord:
        evaluation_run_id = str(evaluation_context["evaluation_run_id"]).strip()
        scoring_rule_version = str(
            evaluation_context.get("scoring_rule_version")
            or contract.get("scoring_rule_version")
            or DEFAULT_SCORING_RULE_VERSION
        ).strip()
        subject_ref = str(record["record_id"]).strip()
        subject_version_ref = self._subject_version(record)
        phase_contract_ref = str(contract["contract_id"]).strip()
        phase_contract_version = str(contract["contract_version"]).strip()
        threshold_applied = self._total_threshold(contract)
        dimension_thresholds = self._dimension_thresholds(contract)

        quality_record_id = self._quality_record_id(
            evaluation_run_id,
            subject_ref,
            phase_contract_ref,
            phase_contract_version,
        )
        score_basis = [
            "required_fields",
            "provenance",
            "lineage",
            "version",
            "identity_status",
            "phase_contract",
        ]

        flags: List[QualityFlag] = []
        missing_required = [
            field
            for field in contract["required_fields"]
            if not self._field_present(record, str(field))
        ]
        for field in missing_required:
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "missing_required_field",
                    "blocking",
                    "completeness",
                    f"Required field {field} is absent or empty.",
                    str(field),
                    f"required_fields.{field}",
                    produced_at,
                )
            )

        provenance_present = self._has_provenance(record)
        lineage_present = self._has_lineage(record)
        version_present = bool(subject_version_ref)
        producer_present = self._has_producer_ref(record)

        if not provenance_present:
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "missing_provenance",
                    self._metadata_severity(contract, "missing_provenance"),
                    "traceability",
                    "Required provenance metadata is absent.",
                    "provenance",
                    "traceability.provenance",
                    produced_at,
                )
            )
        if not lineage_present:
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "missing_lineage",
                    self._metadata_severity(contract, "missing_lineage"),
                    "traceability",
                    "Required lineage metadata is absent.",
                    "lineage",
                    "traceability.lineage",
                    produced_at,
                )
            )

        if self._identity_status(record) == "ambiguous":
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "ambiguous_identity",
                    self._metadata_severity(contract, "ambiguous_identity"),
                    "fitness",
                    "Identity ambiguity remains open; motor_007 does not resolve it.",
                    "identity_status",
                    "identity_status",
                    produced_at,
                )
            )

        if self._is_restricted_use(record):
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "restricted_use",
                    "blocking",
                    "fitness",
                    "Record is marked as restricted for the evaluated use.",
                    "rights_status",
                    "usage_restrictions",
                    produced_at,
                )
            )

        if self._declared_contract_drift(record, contract):
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "contract_mismatch",
                    "blocking",
                    "contract_consistency",
                    "Record declares a different phase contract or contract version.",
                    "phase_contract_ref",
                    "phase_contract",
                    produced_at,
                )
            )

        dimension_scores = {
            "completeness": self._completeness_score(
                len(contract["required_fields"]),
                len(missing_required),
            ),
            "traceability": self._traceability_score(
                provenance_present,
                lineage_present,
                version_present,
                producer_present,
            ),
            "contract_consistency": 0.0
            if any(flag.code == "contract_mismatch" for flag in flags)
            else 1.0,
            "fitness": self._fitness_dimension_score(record, flags),
        }

        for dimension, threshold in dimension_thresholds.items():
            if dimension not in dimension_scores:
                continue
            if dimension_scores[dimension] < threshold:
                flags.append(
                    self._make_flag(
                        quality_record_id,
                        "not_fit_for_phase",
                        "blocking",
                        dimension,
                        (
                            f"Dimension {dimension} score "
                            f"{dimension_scores[dimension]:.4f} is below threshold "
                            f"{threshold:.4f}."
                        ),
                        dimension,
                        f"fitness_thresholds.dimensions.{dimension}",
                        produced_at,
                    )
                )

        total_score = self._total_score(dimension_scores)
        if total_score < threshold_applied:
            flags.append(
                self._make_flag(
                    quality_record_id,
                    "not_fit_for_phase",
                    "blocking",
                    "fitness",
                    (
                        f"Total score {total_score:.4f} is below threshold "
                        f"{threshold_applied:.4f}."
                    ),
                    "total_score",
                    "fitness_thresholds.total",
                    produced_at,
                )
            )

        blocking_flag_present = any(flag.blocking for flag in flags)
        evaluation_status = self._evaluation_status(flags, blocking_flag_present)
        disqualification_reason = (
            self._make_disqualification_reason(
                quality_record_id,
                flags,
                dimension_scores,
                threshold_applied,
                dimension_thresholds,
                produced_at,
            )
            if evaluation_status == "disqualified"
            else None
        )

        fitness_score = self._make_fitness_score(
            quality_record_id,
            total_score,
            dimension_scores,
            threshold_applied,
            dimension_thresholds,
            scoring_rule_version,
            blocking_flag_present,
            score_basis,
            produced_at,
        )

        quality_record = QualityRecord(
            quality_record_id=quality_record_id,
            subject_ref=subject_ref,
            subject_version_ref=subject_version_ref,
            phase_contract_ref=phase_contract_ref,
            phase_contract_version=phase_contract_version,
            evaluation_run_id=evaluation_run_id,
            evaluation_status=evaluation_status,
            fitness_score=fitness_score,
            quality_flags=flags,
            disqualification_reason=disqualification_reason,
            evaluated_dimensions=list(EVALUATED_DIMENSIONS),
            evaluation_errors=[],
            version_id=f"{quality_record_id}:v1",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash="",
            source_ref=f"identity_resolved_record:{subject_ref}",
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=self._nullable_string(record.get("previous_quality_record_id")),
        )
        quality_record.version_hash = self._stable_hash(
            self._quality_record_hash_payload(quality_record)
        )
        return quality_record

    def _validate_batch_inputs(
        self,
        identity_resolved_records: Any,
        phase_contracts: Any,
        evaluation_context: Any,
    ) -> None:
        if not isinstance(identity_resolved_records, list):
            raise QualityFitnessEvaluationError(
                "QUALITY_INPUT_NOT_LIST",
                "identity_resolved_records must be a list.",
                {"received_type": type(identity_resolved_records).__name__},
            )
        if not isinstance(phase_contracts, list):
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "phase_contracts must be a list.",
                {"received_type": type(phase_contracts).__name__},
            )
        if not isinstance(evaluation_context, Mapping):
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTEXT_INVALID",
                "evaluation_context must be a mapping.",
            )
        if not str(evaluation_context.get("evaluation_run_id") or "").strip():
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTEXT_INVALID",
                "evaluation_context.evaluation_run_id is required.",
            )

    def _validate_record_shell(self, record: Any, index: int) -> None:
        if not isinstance(record, Mapping):
            raise QualityFitnessEvaluationError(
                "QUALITY_INPUT_INVALID_RECORD",
                "Each identity_resolved_records item must be a mapping.",
                {"index": index},
            )
        if not str(record.get("record_id") or "").strip():
            raise QualityFitnessEvaluationError(
                "QUALITY_INPUT_MISSING_SUBJECT_REF",
                "identity_resolved_records item lacks record_id.",
                {"index": index},
            )
        if not str(record.get("identity_status") or "").strip():
            raise QualityFitnessEvaluationError(
                "QUALITY_INPUT_MISSING_IDENTITY_STATUS",
                "identity_resolved_records item lacks identity_status.",
                {"record_id": record.get("record_id"), "index": index},
            )

    def _validate_contract(self, contract: Any) -> Mapping[str, Any]:
        if not isinstance(contract, Mapping):
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "Each phase_contracts item must be a mapping.",
            )
        required_keys = (
            "contract_id",
            "contract_version",
            "required_fields",
            "fitness_thresholds",
        )
        missing_keys = [
            key for key in required_keys if key not in contract or contract[key] in (None, "")
        ]
        if missing_keys:
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "Phase contract lacks required structural fields.",
                {"missing_keys": missing_keys},
            )
        if not self._is_non_string_sequence(contract["required_fields"]):
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "phase_contract.required_fields must be a list.",
                {"contract_id": contract.get("contract_id")},
            )
        thresholds = contract["fitness_thresholds"]
        if not isinstance(thresholds, Mapping):
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "phase_contract.fitness_thresholds must be a mapping.",
                {"contract_id": contract.get("contract_id")},
            )
        self._total_threshold(contract)
        self._dimension_thresholds(contract)
        return contract

    def _select_contract(
        self,
        record: Mapping[str, Any],
        contracts: Sequence[Mapping[str, Any]],
    ) -> Mapping[str, Any]:
        active_contracts = [
            contract for contract in contracts if self._contract_is_active(contract)
        ]
        declared_contract_ref = self._nullable_string(
            record.get("phase_contract_ref")
            or record.get("phase_contract_id")
            or record.get("contract_id")
        )
        if declared_contract_ref:
            candidates = [
                contract
                for contract in active_contracts
                if str(contract["contract_id"]) == declared_contract_ref
            ]
        else:
            candidates = [
                contract
                for contract in active_contracts
                if self._contract_matches_record(record, contract)
            ]

        if not candidates:
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_NOT_FOUND",
                "No applicable phase contract was found for the record.",
                {
                    "record_id": record.get("record_id"),
                    "object_type": self._record_object_type(record),
                    "phase_ref": self._record_phase_ref(record),
                },
            )

        declared_version = self._nullable_string(
            record.get("phase_contract_version") or record.get("contract_version")
        )
        if declared_version:
            versioned = [
                contract
                for contract in candidates
                if str(contract["contract_version"]) == declared_version
            ]
            if versioned:
                candidates = versioned

        return sorted(
            candidates,
            key=lambda contract: (
                str(contract["contract_id"]),
                str(contract["contract_version"]),
            ),
        )[-1]

    def _contract_is_active(self, contract: Mapping[str, Any]) -> bool:
        status = self._nullable_string(contract.get("status"))
        if status is None:
            return True
        return status.lower() not in INACTIVE_CONTRACT_STATUSES

    def _contract_matches_record(
        self,
        record: Mapping[str, Any],
        contract: Mapping[str, Any],
    ) -> bool:
        record_object_type = self._record_object_type(record)
        contract_object_type = self._nullable_string(
            contract.get("object_type") or contract.get("subject_type")
        )
        if contract_object_type and record_object_type:
            if contract_object_type != record_object_type:
                return False

        record_phase_ref = self._record_phase_ref(record)
        contract_phase_ref = self._nullable_string(
            contract.get("phase_ref")
            or contract.get("phase_id")
            or contract.get("phase")
        )
        if contract_phase_ref and record_phase_ref:
            if contract_phase_ref != record_phase_ref:
                return False
        return bool(contract_object_type or contract_phase_ref or contract.get("contract_id"))

    def _declared_contract_drift(
        self,
        record: Mapping[str, Any],
        contract: Mapping[str, Any],
    ) -> bool:
        declared_ref = self._nullable_string(
            record.get("phase_contract_ref")
            or record.get("phase_contract_id")
            or record.get("contract_id")
        )
        declared_version = self._nullable_string(
            record.get("phase_contract_version") or record.get("contract_version")
        )
        if declared_ref and declared_ref != str(contract["contract_id"]):
            return True
        if declared_version and declared_version != str(contract["contract_version"]):
            return True
        return False

    def _completeness_score(self, total_required: int, missing_required: int) -> float:
        if total_required == 0:
            return 1.0
        return self._clamp((total_required - missing_required) / total_required)

    def _traceability_score(
        self,
        provenance_present: bool,
        lineage_present: bool,
        version_present: bool,
        producer_present: bool,
    ) -> float:
        checks = [
            provenance_present,
            lineage_present,
            version_present,
            producer_present,
        ]
        return self._clamp(sum(1 for value in checks if value) / len(checks))

    def _fitness_dimension_score(
        self,
        record: Mapping[str, Any],
        flags: Sequence[QualityFlag],
    ) -> float:
        if any(flag.code == "restricted_use" for flag in flags):
            return 0.0
        if self._identity_status(record) == "ambiguous":
            return 0.75
        return 1.0

    def _total_score(self, dimension_scores: Mapping[str, float]) -> float:
        values = [dimension_scores[dimension] for dimension in EVALUATED_DIMENSIONS]
        return self._clamp(sum(values) / len(values))

    def _evaluation_status(
        self,
        flags: Sequence[QualityFlag],
        blocking_flag_present: bool,
    ) -> str:
        if blocking_flag_present:
            return "disqualified"
        if flags:
            return "conditional_pass"
        return "pass"

    def _make_fitness_score(
        self,
        quality_record_id: str,
        total_score: float,
        dimension_scores: Mapping[str, float],
        threshold_applied: float,
        dimension_thresholds: Mapping[str, float],
        scoring_rule_version: str,
        blocking_flag_present: bool,
        score_basis: Sequence[str],
        produced_at: str,
    ) -> FitnessScore:
        score_id = f"{quality_record_id}:score:{scoring_rule_version}"
        score = FitnessScore(
            score_id=score_id,
            total_score=total_score,
            dimension_scores=dict(dimension_scores),
            threshold_applied=threshold_applied,
            dimension_thresholds=dict(dimension_thresholds),
            scoring_rule_version=scoring_rule_version,
            blocking_flag_present=blocking_flag_present,
            score_basis=list(score_basis),
            version_id=f"{score_id}:v1",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash="",
            source_ref=quality_record_id,
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=None,
        )
        score.version_hash = self._stable_hash(
            {
                "total_score": score.total_score,
                "dimension_scores": score.dimension_scores,
                "threshold_applied": score.threshold_applied,
                "dimension_thresholds": score.dimension_thresholds,
                "scoring_rule_version": score.scoring_rule_version,
                "blocking_flag_present": score.blocking_flag_present,
                "score_basis": score.score_basis,
            }
        )
        return score

    def _make_flag(
        self,
        quality_record_id: str,
        code: str,
        severity: str,
        dimension: str,
        message: str,
        affected_field: Optional[str],
        contract_rule_ref: Optional[str],
        produced_at: str,
    ) -> QualityFlag:
        blocking = severity == "blocking"
        flag_id = self._stable_id(
            f"{quality_record_id}:flag",
            {
                "code": code,
                "affected_field": affected_field or "object",
                "contract_rule_ref": contract_rule_ref or "none",
            },
        )
        flag = QualityFlag(
            flag_id=flag_id,
            code=code,
            severity=severity,
            dimension=dimension,
            message=message,
            affected_field=affected_field,
            contract_rule_ref=contract_rule_ref,
            blocking=blocking,
            version_id=f"{flag_id}:v1",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash="",
            source_ref=quality_record_id,
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=None,
        )
        flag.version_hash = self._stable_hash(
            {
                "code": flag.code,
                "severity": flag.severity,
                "dimension": flag.dimension,
                "affected_field": flag.affected_field,
                "contract_rule_ref": flag.contract_rule_ref,
                "blocking": flag.blocking,
                "message": flag.message,
            }
        )
        return flag

    def _make_disqualification_reason(
        self,
        quality_record_id: str,
        flags: Sequence[QualityFlag],
        dimension_scores: Mapping[str, float],
        threshold_applied: float,
        dimension_thresholds: Mapping[str, float],
        produced_at: str,
    ) -> DisqualificationReason:
        blocking_flags = [flag for flag in flags if flag.blocking]
        reason_code, threshold_failed, explanation = self._reason_basis(
            blocking_flags,
            dimension_scores,
            threshold_applied,
            dimension_thresholds,
        )
        reason_id = f"{quality_record_id}:disqualification:{reason_code}"
        reason = DisqualificationReason(
            reason_id=reason_id,
            code=reason_code,
            severity="blocking",
            threshold_failed=threshold_failed,
            explanation=explanation,
            supporting_flags=[flag.flag_id for flag in blocking_flags],
            version_id=f"{reason_id}:v1",
            created_at=produced_at,
            updated_at=produced_at,
            version_hash="",
            source_ref=quality_record_id,
            produced_by_motor=MOTOR_ID,
            produced_at=produced_at,
            parent_id=None,
        )
        reason.version_hash = self._stable_hash(
            {
                "code": reason.code,
                "threshold_failed": reason.threshold_failed,
                "explanation": reason.explanation,
                "supporting_flags": reason.supporting_flags,
            }
        )
        return reason

    def _reason_basis(
        self,
        blocking_flags: Sequence[QualityFlag],
        dimension_scores: Mapping[str, float],
        threshold_applied: float,
        dimension_thresholds: Mapping[str, float],
    ) -> Tuple[str, str, str]:
        flag_codes = {flag.code for flag in blocking_flags}
        if {"missing_provenance", "missing_lineage"}.issubset(flag_codes):
            return (
                "critical_traceability_missing",
                "traceability.provenance_and_lineage",
                "Required provenance and lineage metadata are both absent.",
            )
        if "restricted_use" in flag_codes:
            return (
                "restricted_use",
                "usage_restrictions",
                "The evaluated object is restricted for the target use.",
            )
        if "contract_mismatch" in flag_codes:
            return (
                "contract_mismatch",
                "phase_contract",
                "The record is not aligned with the selected phase contract.",
            )
        if "missing_required_field" in flag_codes:
            return (
                "missing_required_field",
                "required_fields",
                "The evaluated object lacks one or more contract-required fields.",
            )
        for dimension, threshold in dimension_thresholds.items():
            if dimension_scores.get(dimension, 1.0) < threshold:
                return (
                    f"{dimension}_below_threshold",
                    f"fitness_thresholds.dimensions.{dimension}",
                    f"The {dimension} score is below the contract threshold.",
                )
        return (
            "total_score_below_threshold",
            "fitness_thresholds.total",
            f"The total score is below the contract threshold {threshold_applied:.4f}.",
        )

    def _quality_record_hash_payload(self, quality_record: QualityRecord) -> Dict[str, Any]:
        return {
            "subject_ref": quality_record.subject_ref,
            "subject_version_ref": quality_record.subject_version_ref,
            "phase_contract_ref": quality_record.phase_contract_ref,
            "phase_contract_version": quality_record.phase_contract_version,
            "evaluation_status": quality_record.evaluation_status,
            "fitness_score": quality_record.fitness_score.to_dict(),
            "quality_flags": [flag.to_dict() for flag in quality_record.quality_flags],
            "disqualification_reason": (
                quality_record.disqualification_reason.to_dict()
                if quality_record.disqualification_reason
                else None
            ),
            "evaluation_run_id": quality_record.evaluation_run_id,
        }

    def _field_present(self, record: Mapping[str, Any], field: str) -> bool:
        direct = self._get_path(record, field)
        if self._has_value(direct):
            return True
        for container_name in ("fields", "normalized_fields", "attributes"):
            container = record.get(container_name)
            if isinstance(container, Mapping) and self._has_value(
                self._get_path(container, field)
            ):
                return True
        return False

    def _has_provenance(self, record: Mapping[str, Any]) -> bool:
        if self._has_value(record.get("provenance_ref")):
            return True
        provenance = record.get("provenance")
        if isinstance(provenance, Mapping):
            return any(self._has_value(value) for value in provenance.values())
        return self._has_value(record.get("source_ref")) or self._has_value(
            record.get("source_id")
        )

    def _has_lineage(self, record: Mapping[str, Any]) -> bool:
        if self._has_value(record.get("lineage_ref")):
            return True
        lineage_refs = record.get("lineage_refs")
        if isinstance(lineage_refs, Sequence) and not isinstance(lineage_refs, (str, bytes)):
            return any(self._has_value(value) for value in lineage_refs)
        lineage = record.get("lineage")
        if isinstance(lineage, Mapping):
            return any(self._has_value(value) for value in lineage.values())
        return False

    def _has_producer_ref(self, record: Mapping[str, Any]) -> bool:
        if self._has_value(record.get("produced_by_motor")):
            return True
        if self._has_value(record.get("producer_ref")):
            return True
        provenance = record.get("provenance")
        if isinstance(provenance, Mapping):
            return self._has_value(provenance.get("source_id")) or self._has_value(
                provenance.get("producer_ref")
            )
        return self._has_value(record.get("source_ref"))

    def _subject_version(self, record: Mapping[str, Any]) -> str:
        value = (
            record.get("subject_version_ref")
            or record.get("version")
            or record.get("version_id")
            or record.get("record_version")
        )
        return str(value).strip() if value is not None else ""

    def _identity_status(self, record: Mapping[str, Any]) -> str:
        return str(record.get("identity_status") or "").strip().lower()

    def _is_restricted_use(self, record: Mapping[str, Any]) -> bool:
        truthy_fields = (
            "restricted_use",
            "use_restricted",
            "restricted",
        )
        for field in truthy_fields:
            if record.get(field) is True:
                return True
        rights_value = str(
            record.get("rights_status")
            or record.get("usage_restriction")
            or record.get("use_policy")
            or ""
        ).strip().lower()
        return rights_value in {"restricted", "blocked", "not_allowed", "prohibited"}

    def _metadata_severity(self, contract: Mapping[str, Any], flag_code: str) -> str:
        blocking_flags = contract.get("blocking_flags") or contract.get("block_on_flags")
        if isinstance(blocking_flags, Mapping):
            if bool(blocking_flags.get(flag_code)):
                return "blocking"
        elif self._is_non_string_sequence(blocking_flags):
            if flag_code in {str(item) for item in blocking_flags}:
                return "blocking"
        traceability_required = bool(
            contract.get("traceability_required")
            or contract.get("require_traceability")
            or contract.get("critical_traceability_required")
        )
        if flag_code in {"missing_provenance", "missing_lineage"} and traceability_required:
            return "blocking"
        if flag_code == "ambiguous_identity" and bool(contract.get("block_ambiguous_identity")):
            return "blocking"
        return "warning"

    def _total_threshold(self, contract: Mapping[str, Any]) -> float:
        thresholds = contract["fitness_thresholds"]
        value = (
            thresholds.get("total")
            if isinstance(thresholds, Mapping)
            else None
        )
        if value is None and isinstance(thresholds, Mapping):
            value = thresholds.get("total_score")
        if value is None:
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "fitness_thresholds.total is required.",
                {"contract_id": contract.get("contract_id")},
            )
        return self._score_float(value, "fitness_thresholds.total", contract)

    def _dimension_thresholds(self, contract: Mapping[str, Any]) -> Dict[str, float]:
        thresholds = contract["fitness_thresholds"]
        dimensions = thresholds.get("dimensions", {}) if isinstance(thresholds, Mapping) else {}
        if dimensions is None:
            return {}
        if not isinstance(dimensions, Mapping):
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                "fitness_thresholds.dimensions must be a mapping when present.",
                {"contract_id": contract.get("contract_id")},
            )
        parsed: Dict[str, float] = {}
        for dimension, value in dimensions.items():
            parsed[str(dimension)] = self._score_float(
                value,
                f"fitness_thresholds.dimensions.{dimension}",
                contract,
            )
        return parsed

    def _score_float(
        self,
        value: Any,
        field_name: str,
        contract: Mapping[str, Any],
    ) -> float:
        try:
            parsed = float(value)
        except (TypeError, ValueError) as exc:
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                f"{field_name} must be numeric.",
                {"contract_id": contract.get("contract_id"), "value": value},
            ) from exc
        if not 0.0 <= parsed <= 1.0:
            raise QualityFitnessEvaluationError(
                "QUALITY_CONTRACT_INVALID",
                f"{field_name} must be between 0.0 and 1.0.",
                {"contract_id": contract.get("contract_id"), "value": value},
            )
        return parsed

    def _context_timestamp(self, evaluation_context: Mapping[str, Any]) -> str:
        return str(
            evaluation_context.get("timestamp")
            or evaluation_context.get("produced_at")
            or evaluation_context.get("evaluated_at")
            or DEFAULT_TIMESTAMP
        )

    def _quality_record_id(
        self,
        evaluation_run_id: str,
        subject_ref: str,
        phase_contract_ref: str,
        phase_contract_version: str,
    ) -> str:
        return (
            f"{MOTOR_ID}:{evaluation_run_id}:{subject_ref}:"
            f"{phase_contract_ref}:{phase_contract_version}"
        )

    def _record_object_type(self, record: Mapping[str, Any]) -> Optional[str]:
        return self._nullable_string(
            record.get("object_type")
            or record.get("entity_type")
            or record.get("subject_type")
        )

    def _record_phase_ref(self, record: Mapping[str, Any]) -> Optional[str]:
        return self._nullable_string(
            record.get("phase_ref") or record.get("phase_id") or record.get("phase")
        )

    def _get_path(self, data: Mapping[str, Any], path: str) -> Any:
        current: Any = data
        for part in path.split("."):
            if not isinstance(current, Mapping) or part not in current:
                return None
            current = current[part]
        return current

    def _has_value(self, value: Any) -> bool:
        if value is None:
            return False
        if isinstance(value, str):
            return bool(value.strip())
        if isinstance(value, Mapping):
            return bool(value)
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
            return bool(value)
        return True

    def _nullable_string(self, value: Any) -> Optional[str]:
        if value is None:
            return None
        text = str(value).strip()
        return text or None

    def _is_non_string_sequence(self, value: Any) -> bool:
        return isinstance(value, Sequence) and not isinstance(value, (str, bytes))

    def _clamp(self, value: float) -> float:
        return max(0.0, min(1.0, round(float(value), 6)))

    def _stable_id(self, prefix: str, payload: Mapping[str, Any]) -> str:
        digest = self._stable_hash(payload)[:16]
        return f"{prefix}:{digest}"

    def _stable_hash(self, payload: Any) -> str:
        encoded = json.dumps(
            payload,
            sort_keys=True,
            separators=(",", ":"),
            ensure_ascii=True,
            default=str,
        ).encode("utf-8")
        return hashlib.sha256(encoded).hexdigest()
