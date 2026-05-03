from __future__ import annotations

from collections.abc import Iterable

from .._compat import dataclass
from ..domain.entities import (
    EvaluationRequestRecord,
    EvaluationScopeRecord,
    FitnessDimensionRecord,
    QualityDimensionRecord,
    ValidationRuleRecord,
)
from ..domain.records import (
    ContractConformanceCheckRecord,
    EvaluationDecisionRecord,
    EvaluationEvidenceRecord,
    EvaluationIssueRecord,
    EvaluationRationaleRecord,
    EvaluationReplayManifest,
    EvaluationRunRecord,
    EvaluationScorecardRecord,
    EvaluationSeverityRecord,
    FieldCheckResultRecord,
    FitnessCheckRecord,
    ObjectCheckResultRecord,
    TraceabilityCheckRecord,
)
from ..domain.value_objects import (
    ContractConformanceCheckRecordId,
    EvaluationDecisionRecordId,
    EvaluationEvidenceRecordId,
    EvaluationIssueRecordId,
    EvaluationRationaleRecordId,
    EvaluationRequestRecordId,
    EvaluationRunRecordId,
    EvaluationScopeRecordId,
    EvaluationScorecardRecordId,
    EvaluationSeverityRecordId,
    FieldCheckResultRecordId,
    FitnessCheckRecordId,
    FitnessDimensionRecordId,
    ObjectCheckResultRecordId,
    QualityDimensionRecordId,
    TraceabilityCheckRecordId,
    ValidationRuleRecordId,
)


@dataclass(frozen=True, slots=True)
class ValidationContext:
    evaluation_scope_records: tuple[EvaluationScopeRecord, ...] = ()
    evaluation_request_records: tuple[EvaluationRequestRecord, ...] = ()
    quality_dimension_records: tuple[QualityDimensionRecord, ...] = ()
    fitness_dimension_records: tuple[FitnessDimensionRecord, ...] = ()
    validation_rule_records: tuple[ValidationRuleRecord, ...] = ()
    object_check_result_records: tuple[ObjectCheckResultRecord, ...] = ()
    field_check_result_records: tuple[FieldCheckResultRecord, ...] = ()
    traceability_check_records: tuple[TraceabilityCheckRecord, ...] = ()
    contract_conformance_check_records: tuple[ContractConformanceCheckRecord, ...] = ()
    fitness_check_records: tuple[FitnessCheckRecord, ...] = ()
    evaluation_issue_records: tuple[EvaluationIssueRecord, ...] = ()
    evaluation_severity_records: tuple[EvaluationSeverityRecord, ...] = ()
    evaluation_rationale_records: tuple[EvaluationRationaleRecord, ...] = ()
    evaluation_evidence_records: tuple[EvaluationEvidenceRecord, ...] = ()
    evaluation_scorecard_records: tuple[EvaluationScorecardRecord, ...] = ()
    evaluation_decision_records: tuple[EvaluationDecisionRecord, ...] = ()
    evaluation_run_records: tuple[EvaluationRunRecord, ...] = ()
    evaluation_replay_manifests: tuple[EvaluationReplayManifest, ...] = ()

    @classmethod
    def from_iterables(
        cls,
        *,
        evaluation_scope_records: Iterable[EvaluationScopeRecord] = (),
        evaluation_request_records: Iterable[EvaluationRequestRecord] = (),
        quality_dimension_records: Iterable[QualityDimensionRecord] = (),
        fitness_dimension_records: Iterable[FitnessDimensionRecord] = (),
        validation_rule_records: Iterable[ValidationRuleRecord] = (),
        object_check_result_records: Iterable[ObjectCheckResultRecord] = (),
        field_check_result_records: Iterable[FieldCheckResultRecord] = (),
        traceability_check_records: Iterable[TraceabilityCheckRecord] = (),
        contract_conformance_check_records: Iterable[ContractConformanceCheckRecord] = (),
        fitness_check_records: Iterable[FitnessCheckRecord] = (),
        evaluation_issue_records: Iterable[EvaluationIssueRecord] = (),
        evaluation_severity_records: Iterable[EvaluationSeverityRecord] = (),
        evaluation_rationale_records: Iterable[EvaluationRationaleRecord] = (),
        evaluation_evidence_records: Iterable[EvaluationEvidenceRecord] = (),
        evaluation_scorecard_records: Iterable[EvaluationScorecardRecord] = (),
        evaluation_decision_records: Iterable[EvaluationDecisionRecord] = (),
        evaluation_run_records: Iterable[EvaluationRunRecord] = (),
        evaluation_replay_manifests: Iterable[EvaluationReplayManifest] = (),
    ) -> "ValidationContext":
        return cls(
            evaluation_scope_records=tuple(evaluation_scope_records),
            evaluation_request_records=tuple(evaluation_request_records),
            quality_dimension_records=tuple(quality_dimension_records),
            fitness_dimension_records=tuple(fitness_dimension_records),
            validation_rule_records=tuple(validation_rule_records),
            object_check_result_records=tuple(object_check_result_records),
            field_check_result_records=tuple(field_check_result_records),
            traceability_check_records=tuple(traceability_check_records),
            contract_conformance_check_records=tuple(contract_conformance_check_records),
            fitness_check_records=tuple(fitness_check_records),
            evaluation_issue_records=tuple(evaluation_issue_records),
            evaluation_severity_records=tuple(evaluation_severity_records),
            evaluation_rationale_records=tuple(evaluation_rationale_records),
            evaluation_evidence_records=tuple(evaluation_evidence_records),
            evaluation_scorecard_records=tuple(evaluation_scorecard_records),
            evaluation_decision_records=tuple(evaluation_decision_records),
            evaluation_run_records=tuple(evaluation_run_records),
            evaluation_replay_manifests=tuple(evaluation_replay_manifests),
        )

    @property
    def scopes_by_id(self) -> dict[EvaluationScopeRecordId, EvaluationScopeRecord]:
        return {
            item.evaluation_scope_record_id: item
            for item in self.evaluation_scope_records
        }

    @property
    def requests_by_id(self) -> dict[EvaluationRequestRecordId, EvaluationRequestRecord]:
        return {
            item.evaluation_request_record_id: item
            for item in self.evaluation_request_records
        }

    @property
    def quality_dimensions_by_id(self) -> dict[QualityDimensionRecordId, QualityDimensionRecord]:
        return {
            item.quality_dimension_record_id: item
            for item in self.quality_dimension_records
        }

    @property
    def fitness_dimensions_by_id(self) -> dict[FitnessDimensionRecordId, FitnessDimensionRecord]:
        return {
            item.fitness_dimension_record_id: item
            for item in self.fitness_dimension_records
        }

    @property
    def rules_by_id(self) -> dict[ValidationRuleRecordId, ValidationRuleRecord]:
        return {item.validation_rule_record_id: item for item in self.validation_rule_records}

    @property
    def object_checks_by_id(self) -> dict[ObjectCheckResultRecordId, ObjectCheckResultRecord]:
        return {
            item.object_check_result_record_id: item
            for item in self.object_check_result_records
        }

    @property
    def field_checks_by_id(self) -> dict[FieldCheckResultRecordId, FieldCheckResultRecord]:
        return {
            item.field_check_result_record_id: item
            for item in self.field_check_result_records
        }

    @property
    def traceability_checks_by_id(self) -> dict[TraceabilityCheckRecordId, TraceabilityCheckRecord]:
        return {
            item.traceability_check_record_id: item
            for item in self.traceability_check_records
        }

    @property
    def contract_checks_by_id(self) -> dict[ContractConformanceCheckRecordId, ContractConformanceCheckRecord]:
        return {
            item.contract_conformance_check_record_id: item
            for item in self.contract_conformance_check_records
        }

    @property
    def fitness_checks_by_id(self) -> dict[FitnessCheckRecordId, FitnessCheckRecord]:
        return {item.fitness_check_record_id: item for item in self.fitness_check_records}

    @property
    def issues_by_id(self) -> dict[EvaluationIssueRecordId, EvaluationIssueRecord]:
        return {item.evaluation_issue_record_id: item for item in self.evaluation_issue_records}

    @property
    def severities_by_id(self) -> dict[EvaluationSeverityRecordId, EvaluationSeverityRecord]:
        return {
            item.evaluation_severity_record_id: item
            for item in self.evaluation_severity_records
        }

    @property
    def rationales_by_id(self) -> dict[EvaluationRationaleRecordId, EvaluationRationaleRecord]:
        return {
            item.evaluation_rationale_record_id: item
            for item in self.evaluation_rationale_records
        }

    @property
    def evidence_by_id(self) -> dict[EvaluationEvidenceRecordId, EvaluationEvidenceRecord]:
        return {
            item.evaluation_evidence_record_id: item
            for item in self.evaluation_evidence_records
        }

    @property
    def scorecards_by_id(self) -> dict[EvaluationScorecardRecordId, EvaluationScorecardRecord]:
        return {
            item.evaluation_scorecard_record_id: item
            for item in self.evaluation_scorecard_records
        }

    @property
    def decisions_by_id(self) -> dict[EvaluationDecisionRecordId, EvaluationDecisionRecord]:
        return {
            item.evaluation_decision_record_id: item
            for item in self.evaluation_decision_records
        }

    @property
    def runs_by_id(self) -> dict[EvaluationRunRecordId, EvaluationRunRecord]:
        return {item.evaluation_run_record_id: item for item in self.evaluation_run_records}
