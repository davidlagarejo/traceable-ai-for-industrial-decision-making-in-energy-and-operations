from __future__ import annotations

from datetime import datetime, timezone
from decimal import Decimal
import unittest

from quality_fitness_evaluation_engine.domain import (
    ContractRef,
    DecisionStatus,
    DimensionDescription,
    EvaluatedObjectRef,
    EvaluatedObjectVersionRef,
    EvaluationRequestRecord,
    EvaluationRequestRecordId,
    EvaluationScopeRecord,
    EvaluationScopeRecordId,
    FitnessDimensionRecord,
    FitnessDimensionRecordId,
    FitnessDimensionType,
    FitnessTarget,
    IntendedUse,
    IssueType,
    ObjectTypeName,
    PhaseContext,
    QualityDimensionRecord,
    QualityDimensionRecordId,
    QualityDimensionType,
    RuleApplicabilityType,
    RuleCriterion,
    SeverityLevel,
    TraceabilityAspect,
    TransitionRef,
    ValidationRuleRecord,
    ValidationRuleRecordId,
)
from quality_fitness_evaluation_engine.evaluation import (
    BasicEvaluator,
    ContractRuleSpec,
    EvaluableObjectSnapshot,
    FitnessRuleSpec,
    GranularityLevel,
    StructuralRuleSpec,
    TraceabilityRuleSpec,
)
from quality_fitness_evaluation_engine.validation import (
    BasicQualityFitnessIntegrityValidator,
    ValidationOutcome as IntegrityOutcome,
)


UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 11, 12, 0, tzinfo=UTC)


class BasicEvaluatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.evaluator = BasicEvaluator(clock=fixed_now)
        self.integrity_validator = BasicQualityFitnessIntegrityValidator(clock=fixed_now)

    def test_pass_for_structurally_sound_and_traced_object(self) -> None:
        result = self._evaluate_default()

        self.assertEqual(result.decision_status, DecisionStatus.PASS)
        self.assertEqual(result.evaluation_scorecard_record.overall_score, Decimal("100"))
        self._assert_integrity_not_fail(result)

    def test_pass_with_warnings_for_tolerable_partial_object(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(is_partial=True),
            fitness_rule_specs=(self._fitness_spec(allow_partial=True),),
        )

        self.assertEqual(result.decision_status, DecisionStatus.PASS_WITH_WARNINGS)
        self.assertIn(IssueType.WARNING, {item.issue_type for item in result.evaluation_issue_records})

    def test_fail_for_structural_failure(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(present_fields=("bundle_id",)),
        )

        self.assertEqual(result.decision_status, DecisionStatus.FAIL)
        self.assertIn(IssueType.QUALITY_FAILURE, {item.issue_type for item in result.evaluation_issue_records})

    def test_fail_for_traceability_failure(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(lineage_refs=(), provenance_refs=()),
        )

        self.assertEqual(result.decision_status, DecisionStatus.FAIL)
        self.assertIn(IssueType.TRACEABILITY_FAILURE, {item.issue_type for item in result.evaluation_issue_records})

    def test_fail_for_fitness_gap_on_phase2_validation_agenda(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(granularity_level=GranularityLevel.BUNDLE),
            scope=self._scope(intended_use="phase-2.validation_agenda"),
            fitness_rule_specs=(self._fitness_spec(minimum_granularity=GranularityLevel.RECORD, allow_sparse=False, allow_partial=False),),
        )

        self.assertEqual(result.decision_status, DecisionStatus.FAIL)
        self.assertIn(IssueType.FITNESS_FAILURE, {item.issue_type for item in result.evaluation_issue_records})

    def test_fail_for_contract_violation(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(contract_version_current=False),
        )

        self.assertEqual(result.decision_status, DecisionStatus.FAIL)
        self.assertIn(IssueType.CONTRACT_VIOLATION, {item.issue_type for item in result.evaluation_issue_records})

    def test_blocked_for_stale_dependency_in_sensitive_use(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(stale_dependency_refs=("tension_map:v1",)),
            traceability_rule_specs=(self._traceability_spec(reject_stale_dependencies=True),),
            traceability_severity=SeverityLevel.BLOCK,
        )

        self.assertEqual(result.decision_status, DecisionStatus.BLOCKED)
        self.assertEqual(result.evaluation_scorecard_record.overall_score, Decimal("0"))

    def test_sparse_case_can_pass_with_warning_when_use_is_permissive(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(is_sparse=True),
            fitness_rule_specs=(self._fitness_spec(allow_sparse=True),),
        )

        self.assertEqual(result.decision_status, DecisionStatus.PASS_WITH_WARNINGS)

    def test_sparse_case_fails_when_use_is_strict(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(is_sparse=True),
            fitness_rule_specs=(self._fitness_spec(allow_sparse=False),),
        )

        self.assertEqual(result.decision_status, DecisionStatus.FAIL)
        self.assertIn(IssueType.EPISTEMIC_INSUFFICIENCY, {item.issue_type for item in result.evaluation_issue_records})

    def test_replay_manifest_contains_sufficient_refs(self) -> None:
        result = self._evaluate_default()

        manifest = result.evaluation_replay_manifest
        self.assertEqual(manifest.evaluated_object_refs, (EvaluatedObjectRef("benchmark_bundle:1"),))
        self.assertEqual(manifest.evaluation_request_record_id, result.evaluation_request_record.evaluation_request_record_id)
        self.assertEqual(manifest.validation_rule_record_ids, result.applied_rule_ids)

    def test_re_evaluate_rebuilds_same_decision(self) -> None:
        result = self._evaluate_default()

        replayed = self.evaluator.re_evaluate(
            replay_manifest=result.evaluation_replay_manifest,
            evaluation_scope_record=result.evaluation_scope_record,
            evaluation_request_record=result.evaluation_request_record,
            subject=self._subject(),
            quality_dimension_records=result.quality_dimension_records,
            fitness_dimension_records=result.fitness_dimension_records,
            validation_rule_records=result.validation_rule_records,
            structural_rule_specs=(self._structural_spec(),),
            traceability_rule_specs=(self._traceability_spec(),),
            contract_rule_specs=(self._contract_spec(),),
            fitness_rule_specs=(self._fitness_spec(),),
        )

        self.assertEqual(replayed.decision_status, result.decision_status)
        self.assertEqual(replayed.evaluation_scorecard_record.overall_score, result.evaluation_scorecard_record.overall_score)

    def test_rules_and_rationales_are_registered(self) -> None:
        result = self._evaluate_default(subject=self._subject(is_partial=True), fitness_rule_specs=(self._fitness_spec(allow_partial=True),))

        self.assertTrue(result.evaluation_rationale_records)
        self.assertEqual(result.applied_rule_ids, tuple(item.validation_rule_record_id for item in result.validation_rule_records))

    def test_facility_prior_without_uncertainty_or_sources_fails(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(
                object_ref="facility_prior:1",
                object_type_name="facility_prior",
                source_dependency_refs=(),
                uncertainty_markers=(),
            ),
            traceability_rule_specs=(
                self._traceability_spec(
                    issue_type=IssueType.EPISTEMIC_INSUFFICIENCY,
                    require_source_dependencies=True,
                    require_uncertainty_markers=True,
                ),
            ),
        )

        self.assertEqual(result.decision_status, DecisionStatus.FAIL)
        self.assertIn(IssueType.EPISTEMIC_INSUFFICIENCY, {item.issue_type for item in result.evaluation_issue_records})

    def test_partial_parsed_table_can_pass_with_warnings_for_normalization(self) -> None:
        result = self._evaluate_default(
            subject=self._subject(
                object_ref="parsed_table:1",
                object_type_name="parsed_table",
                granularity_level=GranularityLevel.TABLE,
                is_sparse=True,
                is_partial=True,
            ),
            scope=self._scope(intended_use="normalization.partial"),
            fitness_rule_specs=(
                self._fitness_spec(
                    fitness_target=FitnessTarget("normalization.partial"),
                    minimum_granularity=GranularityLevel.TABLE,
                    allow_sparse=True,
                    allow_partial=True,
                ),
            ),
        )

        self.assertEqual(result.decision_status, DecisionStatus.PASS_WITH_WARNINGS)
        self._assert_integrity_not_fail(result)

    def _evaluate_default(
        self,
        *,
        subject: EvaluableObjectSnapshot | None = None,
        scope: EvaluationScopeRecord | None = None,
        structural_rule_specs=None,
        traceability_rule_specs=None,
        contract_rule_specs=None,
        fitness_rule_specs=None,
        structural_severity: SeverityLevel = SeverityLevel.ERROR,
        traceability_severity: SeverityLevel = SeverityLevel.ERROR,
        contract_severity: SeverityLevel = SeverityLevel.ERROR,
        fitness_severity: SeverityLevel = SeverityLevel.ERROR,
    ):
        scope = scope or self._scope()
        request = self._request(scope, object_ref=(subject.evaluated_object_ref.value if subject else "benchmark_bundle:1"), version_ref=(subject.evaluated_object_version_ref.value if subject and subject.evaluated_object_version_ref else "benchmark_bundle:1@v1"))
        subject = subject or self._subject()
        structural_dim = self._quality_dimension("quality:structural", QualityDimensionType.STRUCTURAL_INTEGRITY)
        traceability_dim = self._quality_dimension("quality:traceability", QualityDimensionType.TRACEABILITY)
        contract_dim = self._quality_dimension("quality:contract", QualityDimensionType.CONTRACT_CONFORMANCE)
        fitness_dim = self._fitness_dimension("fitness:phase", FitnessDimensionType.PHASE_FITNESS)
        structural_rule = self._quality_rule("rule:structural", structural_dim.quality_dimension_record_id, structural_severity)
        traceability_rule = self._quality_rule("rule:traceability", traceability_dim.quality_dimension_record_id, traceability_severity)
        contract_rule = self._quality_rule("rule:contract", contract_dim.quality_dimension_record_id, contract_severity)
        fitness_rule = self._fitness_rule("rule:fitness", fitness_dim.fitness_dimension_record_id, fitness_severity)
        structural_rule_specs = structural_rule_specs or (self._structural_spec(),)
        traceability_rule_specs = traceability_rule_specs or (self._traceability_spec(),)
        contract_rule_specs = contract_rule_specs or (self._contract_spec(),)
        fitness_rule_specs = fitness_rule_specs or (self._fitness_spec(),)
        return self.evaluator.evaluate(
            evaluation_scope_record=scope,
            evaluation_request_record=request,
            subject=subject,
            quality_dimension_records=(structural_dim, traceability_dim, contract_dim),
            fitness_dimension_records=(fitness_dim,),
            validation_rule_records=(structural_rule, traceability_rule, contract_rule, fitness_rule),
            structural_rule_specs=structural_rule_specs,
            traceability_rule_specs=traceability_rule_specs,
            contract_rule_specs=contract_rule_specs,
            fitness_rule_specs=fitness_rule_specs,
        )

    def _scope(self, *, intended_use: str = "phase-1.bundle") -> EvaluationScopeRecord:
        return EvaluationScopeRecord(
            evaluation_scope_record_id=EvaluationScopeRecordId(f"scope:{intended_use}"),
            phase_context=PhaseContext("phase-1"),
            intended_use=IntendedUse(intended_use),
            transition_ref=None,
            created_at=fixed_now(),
        )

    def _request(self, scope: EvaluationScopeRecord, *, object_ref: str, version_ref: str | None) -> EvaluationRequestRecord:
        version_refs = (EvaluatedObjectVersionRef(version_ref),) if version_ref is not None else ()
        return EvaluationRequestRecord(
            evaluation_request_record_id=EvaluationRequestRecordId(f"request:{object_ref}"),
            evaluation_scope_record_id=scope.evaluation_scope_record_id,
            evaluated_object_refs=(EvaluatedObjectRef(object_ref),),
            evaluated_object_version_refs=version_refs,
            requested_at=fixed_now(),
        )

    def _subject(
        self,
        *,
        object_ref: str = "benchmark_bundle:1",
        object_type_name: str = "benchmark_bundle",
        present_fields=("bundle_id", "source_refs", "uncertainty_markers"),
        semantic_content_present: bool = True,
        lineage_refs=("lineage:1",),
        provenance_refs=("provenance:1",),
        contract_refs=(ContractRef("phase-contract://phase-1/benchmark-bundle"),),
        transition_refs=(),
        source_dependency_refs=("source:1",),
        stale_dependency_refs=(),
        component_keys=("table_summary",),
        uncertainty_markers=("uncertain:present",),
        granularity_level: GranularityLevel = GranularityLevel.RECORD,
        is_sparse: bool = False,
        is_partial: bool = False,
        contract_version_current: bool | None = True,
    ) -> EvaluableObjectSnapshot:
        return EvaluableObjectSnapshot(
            evaluated_object_ref=EvaluatedObjectRef(object_ref),
            evaluated_object_version_ref=EvaluatedObjectVersionRef(f"{object_ref}@v1"),
            object_type_name=ObjectTypeName(object_type_name),
            present_fields=present_fields,
            semantic_content_present=semantic_content_present,
            lineage_refs=lineage_refs,
            provenance_refs=provenance_refs,
            contract_refs=contract_refs,
            transition_refs=transition_refs,
            source_dependency_refs=source_dependency_refs,
            stale_dependency_refs=stale_dependency_refs,
            component_keys=component_keys,
            uncertainty_markers=uncertainty_markers,
            granularity_level=granularity_level,
            is_sparse=is_sparse,
            is_partial=is_partial,
            contract_version_current=contract_version_current,
        )

    def _quality_dimension(self, key: str, dimension_type: QualityDimensionType) -> QualityDimensionRecord:
        return QualityDimensionRecord(
            quality_dimension_record_id=QualityDimensionRecordId(key),
            quality_dimension_type=dimension_type,
            description=DimensionDescription(dimension_type.value),
            created_at=fixed_now(),
        )

    def _fitness_dimension(self, key: str, dimension_type: FitnessDimensionType) -> FitnessDimensionRecord:
        return FitnessDimensionRecord(
            fitness_dimension_record_id=FitnessDimensionRecordId(key),
            fitness_dimension_type=dimension_type,
            description=DimensionDescription(dimension_type.value),
            created_at=fixed_now(),
        )

    def _quality_rule(self, key: str, dimension_id, severity: SeverityLevel) -> ValidationRuleRecord:
        return ValidationRuleRecord(
            validation_rule_record_id=ValidationRuleRecordId(key),
            quality_dimension_record_id=dimension_id,
            fitness_dimension_record_id=None,
            rule_applicability_type=RuleApplicabilityType.GLOBAL,
            applicability_target=None,
            criterion=RuleCriterion(key),
            default_severity_level=severity,
            created_at=fixed_now(),
        )

    def _fitness_rule(self, key: str, dimension_id, severity: SeverityLevel) -> ValidationRuleRecord:
        return ValidationRuleRecord(
            validation_rule_record_id=ValidationRuleRecordId(key),
            quality_dimension_record_id=None,
            fitness_dimension_record_id=dimension_id,
            rule_applicability_type=RuleApplicabilityType.GLOBAL,
            applicability_target=None,
            criterion=RuleCriterion(key),
            default_severity_level=severity,
            created_at=fixed_now(),
        )

    def _structural_spec(self) -> StructuralRuleSpec:
        return StructuralRuleSpec(
            validation_rule_record_id=ValidationRuleRecordId("rule:structural"),
            required_fields=("bundle_id", "source_refs"),
            require_semantic_content=True,
        )

    def _traceability_spec(
        self,
        *,
        issue_type: IssueType = IssueType.TRACEABILITY_FAILURE,
        require_source_dependencies: bool = False,
        require_uncertainty_markers: bool = False,
        reject_stale_dependencies: bool = False,
    ) -> TraceabilityRuleSpec:
        return TraceabilityRuleSpec(
            validation_rule_record_id=ValidationRuleRecordId("rule:traceability"),
            traceability_aspect=TraceabilityAspect("provenance_and_lineage"),
            issue_type=issue_type,
            require_lineage_refs=True,
            require_provenance_refs=True,
            require_version_ref=True,
            require_source_dependencies=require_source_dependencies,
            require_uncertainty_markers=require_uncertainty_markers,
            reject_stale_dependencies=reject_stale_dependencies,
        )

    def _contract_spec(self) -> ContractRuleSpec:
        return ContractRuleSpec(
            validation_rule_record_id=ValidationRuleRecordId("rule:contract"),
            contract_ref=ContractRef("phase-contract://phase-1/benchmark-bundle"),
            require_subject_contract_refs=True,
            require_transition_ref=False,
            require_current_contract_version=True,
        )

    def _fitness_spec(
        self,
        *,
        fitness_target: FitnessTarget = FitnessTarget("phase-1.bundle"),
        minimum_granularity: GranularityLevel = GranularityLevel.RECORD,
        allow_sparse: bool = False,
        allow_partial: bool = False,
    ) -> FitnessRuleSpec:
        return FitnessRuleSpec(
            validation_rule_record_id=ValidationRuleRecordId("rule:fitness"),
            fitness_target=fitness_target,
            minimum_granularity=minimum_granularity,
            required_component_keys=("table_summary",),
            allow_sparse=allow_sparse,
            allow_partial=allow_partial,
        )

    def _assert_integrity_not_fail(self, result) -> None:
        report = self.integrity_validator.validate_graph(
            evaluation_scope_records=(result.evaluation_scope_record,),
            evaluation_request_records=(result.evaluation_request_record,),
            quality_dimension_records=result.quality_dimension_records,
            fitness_dimension_records=result.fitness_dimension_records,
            validation_rule_records=result.validation_rule_records,
            object_check_result_records=result.object_check_result_records,
            field_check_result_records=result.field_check_result_records,
            traceability_check_records=result.traceability_check_records,
            contract_conformance_check_records=result.contract_conformance_check_records,
            fitness_check_records=result.fitness_check_records,
            evaluation_issue_records=result.evaluation_issue_records,
            evaluation_severity_records=result.evaluation_severity_records,
            evaluation_rationale_records=result.evaluation_rationale_records,
            evaluation_evidence_records=result.evaluation_evidence_records,
            evaluation_scorecard_records=(result.evaluation_scorecard_record,),
            evaluation_decision_records=(result.evaluation_decision_record,),
            evaluation_run_records=(result.evaluation_run_record,),
            evaluation_replay_manifests=(result.evaluation_replay_manifest,),
        )
        self.assertNotEqual(report.outcome, IntegrityOutcome.FAIL)


if __name__ == "__main__":
    unittest.main()
