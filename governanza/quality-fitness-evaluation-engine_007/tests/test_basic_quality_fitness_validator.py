from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from quality_fitness_evaluation_engine.domain import (
    CheckResultClass,
    ContractConformanceCheckRecord,
    ContractConformanceCheckRecordId,
    ContractRef,
    ContractVersionRef,
    DecisionStatus,
    DimensionDescription,
    EvaluatedObjectRef,
    EvaluatedObjectVersionRef,
    EvaluationDecisionRecord,
    EvaluationDecisionRecordId,
    EvaluationEvidenceRecord,
    EvaluationEvidenceRecordId,
    EvaluationIssueRecord,
    EvaluationIssueRecordId,
    EvaluationRationaleRecord,
    EvaluationRationaleRecordId,
    EvaluationReplayManifest,
    EvaluationReplayManifestId,
    EvaluationRequestRecord,
    EvaluationRequestRecordId,
    EvaluationRunRecord,
    EvaluationRunRecordId,
    EvaluationScopeRecord,
    EvaluationScopeRecordId,
    EvaluationScorecardRecord,
    EvaluationScorecardRecordId,
    EvaluationSeverityRecord,
    EvaluationSeverityRecordId,
    EvaluationStatus,
    EvaluatorVersion,
    EvidenceRef,
    EvidenceSummary,
    FieldCheckResultRecord,
    FieldCheckResultRecordId,
    FieldPathRef,
    FitnessCheckRecord,
    FitnessCheckRecordId,
    FitnessDimensionRecord,
    FitnessDimensionRecordId,
    FitnessDimensionType,
    FitnessTarget,
    IntendedUse,
    IssueType,
    ObjectCheckResultRecord,
    ObjectCheckResultRecordId,
    PhaseContext,
    QualityDimensionRecord,
    QualityDimensionRecordId,
    QualityDimensionType,
    RationaleText,
    ReplayabilityStatus,
    RuleApplicabilityType,
    RuleCriterion,
    ScoreFormulaVersion,
    SeverityLevel,
    TraceabilityAspect,
    TraceabilityCheckRecord,
    TraceabilityCheckRecordId,
    ValidationRuleRecord,
    ValidationRuleRecordId,
)
from quality_fitness_evaluation_engine.validation import (
    BasicQualityFitnessIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 10, 23, 0, tzinfo=UTC)


class BasicQualityFitnessValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicQualityFitnessIntegrityValidator(clock=fixed_now)

    def test_complete_evaluation_graph_passes(self) -> None:
        graph = self._build_complete_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertFalse(report.violations)

    def test_partially_replayable_graph_returns_pass_with_warnings(self) -> None:
        graph = self._build_complete_graph(replayability_status=ReplayabilityStatus.PARTIALLY_REPLAYABLE)

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        codes = {item.code for item in report.violations}
        self.assertIn("replay.partially_replayable_declared", codes)

    def test_decision_severity_mismatch_and_missing_replay_rule_fail(self) -> None:
        graph = self._build_mismatched_decision_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("decision.warning_count_mismatch", codes)
        self.assertIn("decision.error_count_mismatch", codes)
        self.assertIn("decision.status_issue_mismatch", codes)
        self.assertIn("replay.rule_reference_invalid", codes)

    def _build_complete_graph(self, *, replayability_status: ReplayabilityStatus = ReplayabilityStatus.REPLAYABLE) -> dict[str, tuple]:
        scope = EvaluationScopeRecord(
            evaluation_scope_record_id=EvaluationScopeRecordId("scope:1"),
            phase_context=PhaseContext("phase-1"),
            intended_use=IntendedUse("benchmark_bundle_gate"),
            transition_ref=None,
            created_at=fixed_now(),
        )
        request = EvaluationRequestRecord(
            evaluation_request_record_id=EvaluationRequestRecordId("request:1"),
            evaluation_scope_record_id=scope.evaluation_scope_record_id,
            evaluated_object_refs=(EvaluatedObjectRef("benchmark_bundle:1"),),
            evaluated_object_version_refs=(EvaluatedObjectVersionRef("benchmark_bundle:1@v1"),),
            requested_at=fixed_now(),
        )
        quality_dimension = QualityDimensionRecord(
            quality_dimension_record_id=QualityDimensionRecordId("quality:1"),
            quality_dimension_type=QualityDimensionType.STRUCTURAL_INTEGRITY,
            description=DimensionDescription("Structural integrity checks."),
            created_at=fixed_now(),
        )
        fitness_dimension = FitnessDimensionRecord(
            fitness_dimension_record_id=FitnessDimensionRecordId("fitness:1"),
            fitness_dimension_type=FitnessDimensionType.PHASE_FITNESS,
            description=DimensionDescription("Phase fitness checks."),
            created_at=fixed_now(),
        )
        quality_rule = ValidationRuleRecord(
            validation_rule_record_id=ValidationRuleRecordId("rule:quality:1"),
            quality_dimension_record_id=quality_dimension.quality_dimension_record_id,
            fitness_dimension_record_id=None,
            rule_applicability_type=RuleApplicabilityType.GLOBAL,
            applicability_target=None,
            criterion=RuleCriterion("Required metadata must be present."),
            default_severity_level=SeverityLevel.ERROR,
            created_at=fixed_now(),
        )
        fitness_rule = ValidationRuleRecord(
            validation_rule_record_id=ValidationRuleRecordId("rule:fitness:1"),
            quality_dimension_record_id=None,
            fitness_dimension_record_id=fitness_dimension.fitness_dimension_record_id,
            rule_applicability_type=RuleApplicabilityType.GLOBAL,
            applicability_target=None,
            criterion=RuleCriterion("Object must be usable in the requested phase."),
            default_severity_level=SeverityLevel.ERROR,
            created_at=fixed_now(),
        )
        warning_severity = EvaluationSeverityRecord(
            evaluation_severity_record_id=EvaluationSeverityRecordId("severity:warning"),
            severity_level=SeverityLevel.WARNING,
            blocks_progression=False,
            created_at=fixed_now(),
        )
        error_severity = EvaluationSeverityRecord(
            evaluation_severity_record_id=EvaluationSeverityRecordId("severity:error"),
            severity_level=SeverityLevel.ERROR,
            blocks_progression=False,
            created_at=fixed_now(),
        )
        rationale = EvaluationRationaleRecord(
            evaluation_rationale_record_id=EvaluationRationaleRecordId("rationale:1"),
            rationale_text=RationaleText("Checks completed with coherent references."),
            created_at=fixed_now(),
        )
        evidence = EvaluationEvidenceRecord(
            evaluation_evidence_record_id=EvaluationEvidenceRecordId("evidence:1"),
            evidence_ref=EvidenceRef("lineage://benchmark_bundle/1"),
            evidence_summary=EvidenceSummary("Versioned bundle lineage is present."),
            created_at=fixed_now(),
        )
        object_check = ObjectCheckResultRecord(
            object_check_result_record_id=ObjectCheckResultRecordId("object-check:1"),
            evaluated_object_ref=request.evaluated_object_refs[0],
            evaluated_object_version_ref=request.evaluated_object_version_refs[0],
            validation_rule_record_id=quality_rule.validation_rule_record_id,
            quality_dimension_record_id=quality_dimension.quality_dimension_record_id,
            result_class=CheckResultClass.PASS,
            issue_record_ids=(),
            created_at=fixed_now(),
        )
        field_check = FieldCheckResultRecord(
            field_check_result_record_id=FieldCheckResultRecordId("field-check:1"),
            evaluated_object_ref=request.evaluated_object_refs[0],
            field_path_ref=FieldPathRef("uncertainty_markers[0]"),
            validation_rule_record_id=quality_rule.validation_rule_record_id,
            quality_dimension_record_id=quality_dimension.quality_dimension_record_id,
            result_class=CheckResultClass.PASS,
            issue_record_ids=(),
            created_at=fixed_now(),
        )
        traceability_check = TraceabilityCheckRecord(
            traceability_check_record_id=TraceabilityCheckRecordId("traceability-check:1"),
            evaluated_object_ref=request.evaluated_object_refs[0],
            validation_rule_record_id=quality_rule.validation_rule_record_id,
            traceability_aspect=TraceabilityAspect("source_provenance"),
            result_class=CheckResultClass.PASS,
            issue_record_ids=(),
            created_at=fixed_now(),
        )
        contract_check = ContractConformanceCheckRecord(
            contract_conformance_check_record_id=ContractConformanceCheckRecordId("contract-check:1"),
            evaluated_object_ref=request.evaluated_object_refs[0],
            validation_rule_record_id=quality_rule.validation_rule_record_id,
            contract_ref=ContractRef("phase-contract://phase-1/benchmark-bundle"),
            contract_version_ref=ContractVersionRef("2026-04-01"),
            result_class=CheckResultClass.PASS,
            issue_record_ids=(),
            created_at=fixed_now(),
        )
        fitness_check = FitnessCheckRecord(
            fitness_check_record_id=FitnessCheckRecordId("fitness-check:1"),
            evaluated_object_ref=request.evaluated_object_refs[0],
            validation_rule_record_id=fitness_rule.validation_rule_record_id,
            evaluation_scope_record_id=scope.evaluation_scope_record_id,
            fitness_dimension_record_id=fitness_dimension.fitness_dimension_record_id,
            fitness_target=FitnessTarget("phase-1.bundle"),
            result_class=CheckResultClass.PASS,
            issue_record_ids=(),
            created_at=fixed_now(),
        )
        run_id = EvaluationRunRecordId("run:1")
        scorecard = EvaluationScorecardRecord(
            evaluation_scorecard_record_id=EvaluationScorecardRecordId("scorecard:1"),
            evaluation_run_record_id=run_id,
            evaluation_scope_record_id=scope.evaluation_scope_record_id,
            evaluated_object_ref=request.evaluated_object_refs[0],
            structural_score=Decimal("96"),
            traceability_score=Decimal("99"),
            contract_score=Decimal("98"),
            fitness_score=Decimal("95"),
            overall_score=Decimal("97"),
            score_formula_version=ScoreFormulaVersion("score:v1"),
            created_at=fixed_now(),
        )
        decision = EvaluationDecisionRecord(
            evaluation_decision_record_id=EvaluationDecisionRecordId("decision:1"),
            evaluation_run_record_id=run_id,
            decision_status=DecisionStatus.PASS,
            issue_record_ids=(),
            warning_issue_count=0,
            error_issue_count=0,
            blocking_issue_count=0,
            evaluation_rationale_record_id=rationale.evaluation_rationale_record_id,
            created_at=fixed_now(),
        )
        run = EvaluationRunRecord(
            evaluation_run_record_id=run_id,
            evaluation_request_record_id=request.evaluation_request_record_id,
            evaluation_scope_record_id=scope.evaluation_scope_record_id,
            evaluation_status=EvaluationStatus.COMPLETED,
            validation_rule_record_ids=(
                quality_rule.validation_rule_record_id,
                fitness_rule.validation_rule_record_id,
            ),
            object_check_result_record_ids=(object_check.object_check_result_record_id,),
            field_check_result_record_ids=(field_check.field_check_result_record_id,),
            traceability_check_record_ids=(traceability_check.traceability_check_record_id,),
            contract_conformance_check_record_ids=(contract_check.contract_conformance_check_record_id,),
            fitness_check_record_ids=(fitness_check.fitness_check_record_id,),
            evaluation_issue_record_ids=(),
            evaluation_decision_record_id=decision.evaluation_decision_record_id,
            evaluation_scorecard_record_id=scorecard.evaluation_scorecard_record_id,
            evaluator_version=EvaluatorVersion("quality-validator:v1"),
            started_at=fixed_now(),
            completed_at=fixed_now(),
        )
        replay_manifest = EvaluationReplayManifest(
            evaluation_replay_manifest_id=EvaluationReplayManifestId("replay:1"),
            evaluation_run_record_id=run.evaluation_run_record_id,
            evaluation_request_record_id=request.evaluation_request_record_id,
            evaluation_scope_record_id=scope.evaluation_scope_record_id,
            evaluated_object_refs=request.evaluated_object_refs,
            evaluated_object_version_refs=request.evaluated_object_version_refs,
            validation_rule_record_ids=run.validation_rule_record_ids,
            contract_version_ref=contract_check.contract_version_ref,
            evaluator_version=run.evaluator_version,
            replayability_status=replayability_status,
            created_at=fixed_now(),
        )
        return {
            "evaluation_scope_records": (scope,),
            "evaluation_request_records": (request,),
            "quality_dimension_records": (quality_dimension,),
            "fitness_dimension_records": (fitness_dimension,),
            "validation_rule_records": (quality_rule, fitness_rule),
            "object_check_result_records": (object_check,),
            "field_check_result_records": (field_check,),
            "traceability_check_records": (traceability_check,),
            "contract_conformance_check_records": (contract_check,),
            "fitness_check_records": (fitness_check,),
            "evaluation_issue_records": (),
            "evaluation_severity_records": (warning_severity, error_severity),
            "evaluation_rationale_records": (rationale,),
            "evaluation_evidence_records": (evidence,),
            "evaluation_scorecard_records": (scorecard,),
            "evaluation_decision_records": (decision,),
            "evaluation_run_records": (run,),
            "evaluation_replay_manifests": (replay_manifest,),
        }

    def _build_mismatched_decision_graph(self) -> dict[str, tuple]:
        graph = self._build_complete_graph()
        warning_issue = EvaluationIssueRecord(
            evaluation_issue_record_id=EvaluationIssueRecordId("issue:warning:1"),
            issue_type=IssueType.WARNING,
            evaluation_severity_record_id=EvaluationSeverityRecordId("severity:warning"),
            evaluation_rationale_record_id=EvaluationRationaleRecordId("rationale:1"),
            evidence_record_ids=(EvaluationEvidenceRecordId("evidence:1"),),
            evaluated_object_ref=EvaluatedObjectRef("benchmark_bundle:1"),
            field_path_ref=None,
            message="Granularity is acceptable for phase 1 but not ideal.",
            created_at=fixed_now(),
        )
        object_check = ObjectCheckResultRecord(
            object_check_result_record_id=ObjectCheckResultRecordId("object-check:warning"),
            evaluated_object_ref=EvaluatedObjectRef("benchmark_bundle:1"),
            evaluated_object_version_ref=EvaluatedObjectVersionRef("benchmark_bundle:1@v1"),
            validation_rule_record_id=ValidationRuleRecordId("rule:quality:1"),
            quality_dimension_record_id=QualityDimensionRecordId("quality:1"),
            result_class=CheckResultClass.WARNING,
            issue_record_ids=(warning_issue.evaluation_issue_record_id,),
            created_at=fixed_now(),
        )
        decision = EvaluationDecisionRecord(
            evaluation_decision_record_id=EvaluationDecisionRecordId("decision:broken"),
            evaluation_run_record_id=EvaluationRunRecordId("run:1"),
            decision_status=DecisionStatus.FAIL,
            issue_record_ids=(warning_issue.evaluation_issue_record_id,),
            warning_issue_count=0,
            error_issue_count=1,
            blocking_issue_count=0,
            evaluation_rationale_record_id=EvaluationRationaleRecordId("rationale:1"),
            created_at=fixed_now(),
        )
        run = EvaluationRunRecord(
            evaluation_run_record_id=EvaluationRunRecordId("run:1"),
            evaluation_request_record_id=EvaluationRequestRecordId("request:1"),
            evaluation_scope_record_id=EvaluationScopeRecordId("scope:1"),
            evaluation_status=EvaluationStatus.COMPLETED,
            validation_rule_record_ids=(
                ValidationRuleRecordId("rule:quality:1"),
                ValidationRuleRecordId("rule:fitness:1"),
            ),
            object_check_result_record_ids=(object_check.object_check_result_record_id,),
            field_check_result_record_ids=(),
            traceability_check_record_ids=(),
            contract_conformance_check_record_ids=(),
            fitness_check_record_ids=(),
            evaluation_issue_record_ids=(warning_issue.evaluation_issue_record_id,),
            evaluation_decision_record_id=decision.evaluation_decision_record_id,
            evaluation_scorecard_record_id=EvaluationScorecardRecordId("scorecard:1"),
            evaluator_version=EvaluatorVersion("quality-validator:v1"),
            started_at=fixed_now(),
            completed_at=fixed_now(),
        )
        replay = EvaluationReplayManifest(
            evaluation_replay_manifest_id=EvaluationReplayManifestId("replay:broken"),
            evaluation_run_record_id=run.evaluation_run_record_id,
            evaluation_request_record_id=EvaluationRequestRecordId("request:1"),
            evaluation_scope_record_id=EvaluationScopeRecordId("scope:1"),
            evaluated_object_refs=(EvaluatedObjectRef("benchmark_bundle:1"),),
            evaluated_object_version_refs=(EvaluatedObjectVersionRef("benchmark_bundle:1@v1"),),
            validation_rule_record_ids=(
                ValidationRuleRecordId("rule:quality:1"),
                ValidationRuleRecordId("rule:missing"),
            ),
            contract_version_ref=ContractVersionRef("2026-04-01"),
            evaluator_version=EvaluatorVersion("quality-validator:v1"),
            replayability_status=ReplayabilityStatus.REPLAYABLE,
            created_at=fixed_now(),
        )
        return {
            **graph,
            "object_check_result_records": (object_check,),
            "field_check_result_records": (),
            "traceability_check_records": (),
            "contract_conformance_check_records": (),
            "fitness_check_records": (),
            "evaluation_issue_records": (warning_issue,),
            "evaluation_decision_records": (decision,),
            "evaluation_run_records": (run,),
            "evaluation_replay_manifests": (replay,),
        }


if __name__ == "__main__":
    unittest.main()
