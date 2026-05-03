from __future__ import annotations

from .inputs import (
    ContractRuleSpec,
    EvaluableObjectSnapshot,
    FitnessRuleSpec,
    StructuralRuleSpec,
    TraceabilityRuleSpec,
)
from .results import IssueDraft, RuleExecutionDraft, RuleExecutionKind, derive_result_class
from ..domain.entities import ValidationRuleRecord
from ..domain.enums import IssueType, SeverityLevel
from ..domain.value_objects import FieldPathRef


def apply_structural_rules(
    *,
    subject: EvaluableObjectSnapshot,
    rule_specs: tuple[StructuralRuleSpec, ...],
    rule_lookup: dict,
) -> tuple[RuleExecutionDraft, ...]:
    executions: list[RuleExecutionDraft] = []
    present_fields = set(subject.present_fields)
    for spec in rule_specs:
        rule: ValidationRuleRecord = rule_lookup[spec.validation_rule_record_id]
        if spec.require_semantic_content:
            issues: tuple[IssueDraft, ...] = ()
            if not subject.semantic_content_present:
                issues = (
                    IssueDraft(
                        issue_type=IssueType.QUALITY_FAILURE,
                        severity_level=rule.default_severity_level,
                        message="Evaluated object is semantically empty.",
                        rationale_text="Structural evaluation requires real semantic content.",
                        evidence_ref=f"snapshot:{subject.evaluated_object_ref}:semantic_content",
                        evidence_summary="semantic_content_present=False",
                    ),
                )
            executions.append(
                RuleExecutionDraft(
                    execution_kind=RuleExecutionKind.OBJECT,
                    validation_rule_record_id=spec.validation_rule_record_id,
                    result_class=derive_result_class(issues),
                    issue_drafts=issues,
                )
            )
        for field_name in spec.required_fields:
            field_ref = FieldPathRef(field_name)
            issues = ()
            if field_name not in present_fields:
                issues = (
                    IssueDraft(
                        issue_type=IssueType.QUALITY_FAILURE,
                        severity_level=rule.default_severity_level,
                        message=f"Required field is missing: {field_name}.",
                        rationale_text="Structural evaluation requires configured mandatory fields.",
                        evidence_ref=f"snapshot:{subject.evaluated_object_ref}:field:{field_name}",
                        evidence_summary=f"present_fields do not include {field_name}.",
                        field_path_ref=field_ref,
                    ),
                )
            executions.append(
                RuleExecutionDraft(
                    execution_kind=RuleExecutionKind.FIELD,
                    validation_rule_record_id=spec.validation_rule_record_id,
                    result_class=derive_result_class(issues),
                    issue_drafts=issues,
                    field_path_ref=field_ref,
                )
            )
    return tuple(executions)



def apply_traceability_rules(
    *,
    subject: EvaluableObjectSnapshot,
    rule_specs: tuple[TraceabilityRuleSpec, ...],
    rule_lookup: dict,
) -> tuple[RuleExecutionDraft, ...]:
    executions: list[RuleExecutionDraft] = []
    for spec in rule_specs:
        rule: ValidationRuleRecord = rule_lookup[spec.validation_rule_record_id]
        issues: list[IssueDraft] = []
        if spec.require_lineage_refs and not subject.lineage_refs:
            issues.append(
                IssueDraft(
                    issue_type=spec.issue_type,
                    severity_level=rule.default_severity_level,
                    message="Lineage references are missing.",
                    rationale_text="Traceability evaluation requires explicit lineage references.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:lineage",
                    evidence_summary="lineage_refs=()",
                )
            )
        if spec.require_provenance_refs and not subject.provenance_refs:
            issues.append(
                IssueDraft(
                    issue_type=spec.issue_type,
                    severity_level=rule.default_severity_level,
                    message="Provenance references are missing.",
                    rationale_text="Traceability evaluation requires explicit provenance references.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:provenance",
                    evidence_summary="provenance_refs=()",
                )
            )
        if spec.require_version_ref and subject.evaluated_object_version_ref is None:
            issues.append(
                IssueDraft(
                    issue_type=spec.issue_type,
                    severity_level=rule.default_severity_level,
                    message="Evaluated object version reference is missing.",
                    rationale_text="Replayable evaluation requires a version reference.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:version",
                    evidence_summary="evaluated_object_version_ref=None",
                )
            )
        if spec.require_source_dependencies and not subject.source_dependency_refs:
            issues.append(
                IssueDraft(
                    issue_type=spec.issue_type,
                    severity_level=rule.default_severity_level,
                    message="Source dependency references are missing.",
                    rationale_text="This use requires explicit source dependency references.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:source_dependencies",
                    evidence_summary="source_dependency_refs=()",
                )
            )
        if spec.require_uncertainty_markers and not subject.uncertainty_markers:
            issues.append(
                IssueDraft(
                    issue_type=spec.issue_type,
                    severity_level=rule.default_severity_level,
                    message="Uncertainty markers are missing.",
                    rationale_text="Epistemically sensitive objects must preserve uncertainty markers.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:uncertainty_markers",
                    evidence_summary="uncertainty_markers=()",
                )
            )
        if spec.reject_stale_dependencies and subject.stale_dependency_refs:
            issues.append(
                IssueDraft(
                    issue_type=spec.issue_type,
                    severity_level=rule.default_severity_level,
                    message="Stale dependencies are present.",
                    rationale_text="Sensitive uses must fail or block when dependencies are stale.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:stale_dependencies",
                    evidence_summary=",".join(subject.stale_dependency_refs),
                )
            )
        executions.append(
            RuleExecutionDraft(
                execution_kind=RuleExecutionKind.TRACEABILITY,
                validation_rule_record_id=spec.validation_rule_record_id,
                result_class=derive_result_class(tuple(issues)),
                issue_drafts=tuple(issues),
                traceability_aspect=spec.traceability_aspect,
            )
        )
    return tuple(executions)



def apply_contract_rules(
    *,
    subject: EvaluableObjectSnapshot,
    rule_specs: tuple[ContractRuleSpec, ...],
    rule_lookup: dict,
) -> tuple[RuleExecutionDraft, ...]:
    executions: list[RuleExecutionDraft] = []
    subject_contract_refs = set(subject.contract_refs)
    for spec in rule_specs:
        rule: ValidationRuleRecord = rule_lookup[spec.validation_rule_record_id]
        issues: list[IssueDraft] = []
        required_contract_refs = spec.required_contract_refs or (spec.contract_ref,)
        if spec.require_subject_contract_refs:
            for contract_ref in required_contract_refs:
                if contract_ref not in subject_contract_refs:
                    issues.append(
                        IssueDraft(
                            issue_type=IssueType.CONTRACT_VIOLATION,
                            severity_level=rule.default_severity_level,
                            message=f"Required contract reference is missing: {contract_ref}.",
                            rationale_text="Contract evaluation requires configured contract references.",
                            evidence_ref=f"snapshot:{subject.evaluated_object_ref}:contract_refs",
                            evidence_summary="Subject contract refs do not include the required contract.",
                        )
                    )
        if spec.require_transition_ref and not subject.transition_refs:
            issues.append(
                IssueDraft(
                    issue_type=IssueType.CONTRACT_VIOLATION,
                    severity_level=rule.default_severity_level,
                    message="Required transition reference is missing.",
                    rationale_text="This contract-sensitive evaluation requires an explicit transition reference.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:transition_refs",
                    evidence_summary="transition_refs=()",
                )
            )
        if spec.require_current_contract_version and subject.contract_version_current is not True:
            issues.append(
                IssueDraft(
                    issue_type=IssueType.CONTRACT_VIOLATION,
                    severity_level=rule.default_severity_level,
                    message="Contract version is missing or stale.",
                    rationale_text="Strict contract evaluation requires a current contract version.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:contract_version",
                    evidence_summary=f"contract_version_current={subject.contract_version_current}",
                )
            )
        executions.append(
            RuleExecutionDraft(
                execution_kind=RuleExecutionKind.CONTRACT,
                validation_rule_record_id=spec.validation_rule_record_id,
                result_class=derive_result_class(tuple(issues)),
                issue_drafts=tuple(issues),
                contract_ref=spec.contract_ref,
                contract_version_ref=None,
            )
        )
    return tuple(executions)



def apply_fitness_rules(
    *,
    subject: EvaluableObjectSnapshot,
    rule_specs: tuple[FitnessRuleSpec, ...],
    rule_lookup: dict,
) -> tuple[RuleExecutionDraft, ...]:
    executions: list[RuleExecutionDraft] = []
    component_keys = set(subject.component_keys)
    for spec in rule_specs:
        rule: ValidationRuleRecord = rule_lookup[spec.validation_rule_record_id]
        issues: list[IssueDraft] = []
        if (
            spec.minimum_granularity is not None
            and not subject.granularity_level.satisfies(spec.minimum_granularity)
        ):
            issues.append(
                IssueDraft(
                    issue_type=IssueType.FITNESS_FAILURE,
                    severity_level=rule.default_severity_level,
                    message=(
                        f"Granularity {subject.granularity_level.name.lower()} is insufficient for "
                        f"target {spec.fitness_target}."
                    ),
                    rationale_text="Fitness evaluation requires the configured minimum granularity.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:granularity",
                    evidence_summary=(
                        f"granularity={subject.granularity_level.name.lower()}, "
                        f"minimum={spec.minimum_granularity.name.lower()}"
                    ),
                )
            )
        missing_components = sorted(set(spec.required_component_keys) - component_keys)
        for component_key in missing_components:
            issues.append(
                IssueDraft(
                    issue_type=IssueType.FITNESS_FAILURE,
                    severity_level=rule.default_severity_level,
                    message=f"Required component is missing for target use: {component_key}.",
                    rationale_text="Fitness evaluation requires configured components for the target use.",
                    evidence_ref=f"snapshot:{subject.evaluated_object_ref}:component:{component_key}",
                    evidence_summary=f"component_keys do not include {component_key}.",
                )
            )
        if subject.is_sparse:
            if spec.allow_sparse:
                issues.append(
                    IssueDraft(
                        issue_type=IssueType.WARNING,
                        severity_level=SeverityLevel.WARNING,
                        message="Sparse object accepted with warning for the configured use.",
                        rationale_text="This use tolerates sparse inputs, but the sparse state remains explicit.",
                        evidence_ref=f"snapshot:{subject.evaluated_object_ref}:sparse",
                        evidence_summary="is_sparse=True",
                    )
                )
            else:
                issues.append(
                    IssueDraft(
                        issue_type=IssueType.EPISTEMIC_INSUFFICIENCY,
                        severity_level=rule.default_severity_level,
                        message="Sparse object is not acceptable for the configured use.",
                        rationale_text="This use requires denser support than the current sparse object provides.",
                        evidence_ref=f"snapshot:{subject.evaluated_object_ref}:sparse",
                        evidence_summary="is_sparse=True",
                    )
                )
        if subject.is_partial:
            if spec.allow_partial:
                issues.append(
                    IssueDraft(
                        issue_type=IssueType.WARNING,
                        severity_level=SeverityLevel.WARNING,
                        message="Partial object accepted with warning for the configured use.",
                        rationale_text="This use tolerates partial state, but the partial condition remains explicit.",
                        evidence_ref=f"snapshot:{subject.evaluated_object_ref}:partial",
                        evidence_summary="is_partial=True",
                    )
                )
            else:
                issues.append(
                    IssueDraft(
                        issue_type=IssueType.EPISTEMIC_INSUFFICIENCY,
                        severity_level=rule.default_severity_level,
                        message="Partial object is not acceptable for the configured use.",
                        rationale_text="This use requires a complete enough object and cannot accept the current partial state.",
                        evidence_ref=f"snapshot:{subject.evaluated_object_ref}:partial",
                        evidence_summary="is_partial=True",
                    )
                )
        executions.append(
            RuleExecutionDraft(
                execution_kind=RuleExecutionKind.FITNESS,
                validation_rule_record_id=spec.validation_rule_record_id,
                result_class=derive_result_class(tuple(issues)),
                issue_drafts=tuple(issues),
                fitness_target=spec.fitness_target,
            )
        )
    return tuple(executions)
