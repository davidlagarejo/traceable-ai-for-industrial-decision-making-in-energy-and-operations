"""Deterministic implementation for motor_013.

The engine activates governed inference cases from a facility prior, library
trigger definitions, and quality records. It does not analyze activated cases,
produce conclusions, recalculate quality, or mutate upstream inputs.
"""

from __future__ import annotations

from collections import defaultdict
from collections.abc import Mapping, Sequence
from dataclasses import dataclass, is_dataclass, replace
import copy
import hashlib
import json
from typing import Any

from .errors import InferenceActivationError
from .models import (
    ActivationRecord,
    ActivationResult,
    InferenceCase,
    TriggerCondition,
    TriggerLogEntry,
)


MOTOR_ID = "motor_013"
DEFAULT_ACTIVATION_RULE_VERSION = "icae_rules_v1"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
PASSING_QUALITY_STATUSES = frozenset({"PASS", "CONDITIONAL_PASS"})
SUPPORTED_CONDITION_TYPES = frozenset(
    {"field_threshold", "tag_match", "bundle_presence", "quality_gate", "compound"}
)
FORBIDDEN_OUTPUT_KEYS = frozenset(
    {
        "conclusion",
        "conclusions",
        "recommendation",
        "recommendations",
        "decision_grade",
        "confidence",
        "confidence_claim",
        "finding",
        "validated_finding",
        "tension",
        "opportunity",
        "evidence_claim",
        "decision_core_result",
    }
)


@dataclass(frozen=True)
class _PriorContext:
    raw: Mapping[str, Any]
    prior_id: str
    facility_id: str
    prior_version: str
    lineage_id: str
    lineage_refs: list[str]
    provenance_refs: list[str]
    contextual_bundles: list[Mapping[str, Any]]
    contextual_bundle_refs: list[str]
    declared_scopes: set[str]


@dataclass(frozen=True)
class _QualityGate:
    allowed: bool
    reason_code: str | None
    quality_record_refs: list[str]
    conditional_quality_notes: list[str]
    provenance_refs: list[str]
    lineage_refs: list[str]
    blocking_refs: list[str]


@dataclass(frozen=True)
class _EvaluatedTrigger:
    trigger: TriggerCondition
    library_object: Mapping[str, Any]
    quality_gate: _QualityGate
    evaluation_result: str
    reason_code: str
    evaluated_field_refs: list[str]
    matched_values: list[Any]


class InferenceCaseActivationEngine:
    """Core deterministic interface for Inference Case Activation Engine."""

    def __init__(
        self,
        *,
        activation_rule_version: str = DEFAULT_ACTIVATION_RULE_VERSION,
        produced_at: str = DEFAULT_PRODUCED_AT,
    ) -> None:
        self.activation_rule_version = _require_text(
            activation_rule_version,
            "activation_rule_version",
            "INPUT_VALIDATION_ERROR",
        )
        self.produced_at = _require_text(
            produced_at,
            "produced_at",
            "INPUT_VALIDATION_ERROR",
        )

    def activate(
        self,
        *,
        facility_prior: Mapping[str, Any],
        library_objects: Sequence[Mapping[str, Any]],
        quality_records: Sequence[Mapping[str, Any]],
    ) -> ActivationResult:
        """Validate inputs, evaluate triggers, and emit activation records."""

        prior_context = self._parse_prior(copy.deepcopy(_to_mapping(facility_prior)))
        library_items = self._parse_library_objects(library_objects)
        quality_items = _as_record_list(
            "quality_records", quality_records, "INPUT_VALIDATION_ERROR"
        )
        quality_index = self._index_quality_records(quality_items)

        evaluations: list[_EvaluatedTrigger] = []
        for library_object in library_items:
            library_ref = _library_object_id(library_object)
            required_refs = [
                prior_context.prior_id,
                *prior_context.contextual_bundle_refs,
                library_ref,
            ]
            quality_gate = self._quality_gate_for_refs(
                required_refs=required_refs,
                quality_index=quality_index,
            )
            triggers = self._normalize_triggers(library_object)
            for trigger in triggers:
                evaluations.append(
                    self._evaluate_trigger(
                        prior_context=prior_context,
                        library_object=library_object,
                        trigger=trigger,
                        quality_gate=quality_gate,
                        quality_records=quality_items,
                    )
                )

        return self._materialize_result(prior_context, evaluations)

    def _parse_prior(self, facility_prior: Mapping[str, Any]) -> _PriorContext:
        prior_id = _first_text(
            facility_prior,
            ("prior_id", "facility_prior_id", "record_id"),
        )
        facility_id = _first_text(
            facility_prior,
            ("facility_id", "facility_ref", "facility", "facility_record_id"),
        )
        prior_version = _first_text(
            facility_prior,
            ("prior_version", "version", "version_id", "package_version"),
        )
        lineage_refs = _string_list(facility_prior.get("lineage_refs"))
        lineage_id = _first_text(facility_prior, ("lineage_id",))
        if not lineage_id and lineage_refs:
            lineage_id = _stable_id("lineage", lineage_refs)
        provenance_refs = _string_list(facility_prior.get("provenance_refs"))

        missing = []
        if not prior_id:
            missing.append("facility_prior.prior_id")
        if not facility_id:
            missing.append("facility_prior.facility_id")
        if not prior_version:
            missing.append("facility_prior.prior_version")
        if not lineage_id and not lineage_refs:
            missing.append("facility_prior.lineage")
        if not provenance_refs:
            missing.append("facility_prior.provenance_refs")
        if missing:
            raise InferenceActivationError(
                code="INPUT_VALIDATION_ERROR",
                message="facility_prior is missing required identity, lineage, or provenance fields",
                field=", ".join(missing),
                validation_records=[
                    {"field": item, "reason_code": "INPUT_VALIDATION_ERROR"}
                    for item in missing
                ],
            )

        contextual_bundles = _as_optional_record_list(
            facility_prior.get("contextual_bundles", [])
        )
        contextual_bundle_refs = _ordered_unique(
            [
                *_string_list(facility_prior.get("contextual_bundle_refs")),
                *[
                    _first_text(bundle, ("bundle_id", "contextual_bundle_id", "record_id"))
                    for bundle in contextual_bundles
                ],
            ]
        )
        declared_scopes = _declared_scopes(facility_prior, contextual_bundles)

        return _PriorContext(
            raw=facility_prior,
            prior_id=prior_id,
            facility_id=facility_id,
            prior_version=prior_version,
            lineage_id=lineage_id,
            lineage_refs=_ordered_unique([lineage_id, *lineage_refs]),
            provenance_refs=provenance_refs,
            contextual_bundles=contextual_bundles,
            contextual_bundle_refs=contextual_bundle_refs,
            declared_scopes=declared_scopes,
        )

    def _parse_library_objects(
        self, library_objects: Sequence[Mapping[str, Any]]
    ) -> list[Mapping[str, Any]]:
        library_items = _as_record_list(
            "library_objects", library_objects, "LIBRARY_OBJECT_INVALID"
        )
        if not library_items:
            raise InferenceActivationError(
                code="LIBRARY_OBJECT_INVALID",
                message="library_objects must contain at least one governed library object",
                field="library_objects",
            )

        parsed: list[Mapping[str, Any]] = []
        for index, library_object in enumerate(library_items):
            library_ref = _library_object_id(library_object)
            library_version = _library_object_version(library_object)
            library_scope = _library_scope(library_object)
            triggers = _raw_triggers(library_object)
            missing = []
            if not library_ref:
                missing.append("library_object_id")
            if not library_version:
                missing.append("version")
            if not library_scope:
                missing.append("scope")
            if not triggers:
                missing.append("triggers")
            if missing:
                raise InferenceActivationError(
                    code="LIBRARY_OBJECT_INVALID",
                    message="library object lacks governed identity, version, scope, or trigger definitions",
                    field=f"library_objects[{index}].{','.join(missing)}",
                    validation_records=[
                        {
                            "library_object_index": index,
                            "field": item,
                            "reason_code": "LIBRARY_OBJECT_INVALID",
                        }
                        for item in missing
                    ],
                )
            parsed.append(copy.deepcopy(dict(library_object)))
        return parsed

    def _normalize_triggers(
        self, library_object: Mapping[str, Any]
    ) -> list[TriggerCondition]:
        triggers: list[TriggerCondition] = []
        library_ref = _library_object_id(library_object)
        library_version = _library_object_version(library_object)
        library_scope = _library_scope(library_object)
        library_provenance_refs = _string_list(library_object.get("provenance_refs"))
        library_lineage_refs = _string_list(library_object.get("lineage_refs"))
        for index, raw_trigger in enumerate(_raw_triggers(library_object)):
            trigger_mapping = _to_mapping(raw_trigger)
            trigger_id = _first_text(
                trigger_mapping,
                ("trigger_condition_id", "trigger_id", "record_id"),
            )
            condition_type = _first_text(trigger_mapping, ("condition_type",))
            trigger_scope = _first_text(trigger_mapping, ("scope",)) or library_scope
            required_fields = _string_list(trigger_mapping.get("required_fields"))
            activation_case_type = _first_text(
                trigger_mapping, ("activation_case_type", "case_type")
            )
            expression_ref = _first_text(
                trigger_mapping,
                (
                    "condition_expression_ref",
                    "expression_ref",
                    "expression_id",
                    "rule_ref",
                ),
            )
            trigger_version = _first_text(
                trigger_mapping, ("version", "trigger_version", "version_id")
            )

            missing = []
            if not trigger_id:
                missing.append("trigger_condition_id")
            if condition_type not in SUPPORTED_CONDITION_TYPES:
                missing.append("condition_type")
            if not trigger_scope:
                missing.append("scope")
            if not activation_case_type:
                missing.append("activation_case_type")
            if not expression_ref:
                missing.append("condition_expression_ref")
            if not trigger_version:
                missing.append("version")
            if missing:
                raise InferenceActivationError(
                    code="LIBRARY_OBJECT_INVALID",
                    message="trigger definition is not governed or evaluable",
                    field=f"{library_ref}.triggers[{index}].{','.join(missing)}",
                    validation_records=[
                        {
                            "library_object_ref": library_ref,
                            "trigger_index": index,
                            "field": item,
                            "reason_code": "LIBRARY_OBJECT_INVALID",
                        }
                        for item in missing
                    ],
                )

            priority = _int_value(trigger_mapping.get("trigger_priority"), default=1000)
            provenance_refs = _ordered_unique(
                [
                    *_string_list(trigger_mapping.get("provenance_refs")),
                    *library_provenance_refs,
                ]
            )
            lineage_refs = _ordered_unique(
                [
                    *_string_list(trigger_mapping.get("lineage_refs")),
                    *library_lineage_refs,
                    library_ref,
                    trigger_id,
                    trigger_version,
                ]
            )
            produced_at = (
                _first_text(trigger_mapping, ("produced_at", "created_at"))
                or _first_text(library_object, ("produced_at", "created_at"))
                or self.produced_at
            )
            base = {
                "trigger_condition_id": trigger_id,
                "record_id": trigger_id,
                "library_object_ref": library_ref,
                "library_object_version": library_version,
                "condition_type": condition_type,
                "scope": trigger_scope,
                "required_fields": required_fields,
                "activation_case_type": activation_case_type,
                "condition_expression_ref": expression_ref,
                "allowed_result_values": _string_list(
                    trigger_mapping.get("allowed_result_values")
                )
                or ["matched", "not_matched", "rejected"],
                "trigger_priority": priority,
                "version": trigger_version,
                "provenance_refs": provenance_refs,
                "lineage_refs": lineage_refs,
                "source_ref": library_ref,
                "produced_by_motor": _first_text(
                    trigger_mapping, ("produced_by_motor",)
                )
                or _first_text(library_object, ("produced_by_motor",))
                or "motor_011",
                "produced_at": produced_at,
                "parent_id": _optional_text(trigger_mapping.get("parent_id")),
                "version_id": _first_text(trigger_mapping, ("version_id",))
                or _stable_id(
                    "trigger_version",
                    library_ref,
                    library_version,
                    trigger_id,
                    trigger_version,
                ),
                "created_at": _first_text(trigger_mapping, ("created_at",))
                or produced_at,
                "updated_at": _first_text(trigger_mapping, ("updated_at",))
                or produced_at,
                "version_hash": "",
            }
            base["version_hash"] = _stable_hash(_without_hash(base))
            triggers.append(TriggerCondition(**base))

        return sorted(
            triggers,
            key=lambda trigger: (
                trigger.trigger_priority,
                trigger.trigger_condition_id,
                trigger.version,
            ),
        )

    def _index_quality_records(
        self, quality_records: Sequence[Mapping[str, Any]]
    ) -> dict[str, list[Mapping[str, Any]]]:
        quality_index: dict[str, list[Mapping[str, Any]]] = defaultdict(list)
        for index, record in enumerate(quality_records):
            quality_id = _first_text(record, ("quality_record_id", "record_id"))
            object_ref = _first_text(
                record,
                ("object_ref", "subject_ref", "source_ref", "target_ref"),
            )
            if not quality_id or not object_ref:
                raise InferenceActivationError(
                    code="INPUT_VALIDATION_ERROR",
                    message="quality_records must carry quality_record_id and object_ref",
                    field=f"quality_records[{index}]",
                )
            quality_index[object_ref].append(record)
        return quality_index

    def _quality_gate_for_refs(
        self,
        *,
        required_refs: Sequence[str],
        quality_index: Mapping[str, Sequence[Mapping[str, Any]]],
    ) -> _QualityGate:
        quality_record_refs: list[str] = []
        conditional_notes: list[str] = []
        provenance_refs: list[str] = []
        lineage_refs: list[str] = []
        blocking_refs: list[str] = []

        for object_ref in _ordered_unique(required_refs):
            records = list(quality_index.get(object_ref, []))
            if not records:
                blocking_refs.append(f"missing_quality_record:{object_ref}")
                continue

            object_allowed = False
            for record in records:
                quality_id = _first_text(record, ("quality_record_id", "record_id"))
                status = _quality_status(record)
                blocked = _quality_blocked(record)
                quality_record_refs.append(quality_id)
                provenance_refs.extend(_string_list(record.get("provenance_refs")))
                lineage_refs.extend(_string_list(record.get("lineage_refs")))
                if status == "CONDITIONAL_PASS":
                    conditional_notes.extend(_quality_notes(record))
                if status in PASSING_QUALITY_STATUSES and not blocked:
                    object_allowed = True
                else:
                    blocking_refs.append(quality_id or object_ref)
            if not object_allowed:
                blocking_refs.append(object_ref)

        allowed = not blocking_refs
        return _QualityGate(
            allowed=allowed,
            reason_code=None if allowed else "QUALITY_GATE_BLOCKED",
            quality_record_refs=_ordered_unique(quality_record_refs),
            conditional_quality_notes=_ordered_unique(conditional_notes),
            provenance_refs=_ordered_unique(provenance_refs),
            lineage_refs=_ordered_unique(lineage_refs),
            blocking_refs=_ordered_unique(blocking_refs),
        )

    def _evaluate_trigger(
        self,
        *,
        prior_context: _PriorContext,
        library_object: Mapping[str, Any],
        trigger: TriggerCondition,
        quality_gate: _QualityGate,
        quality_records: Sequence[Mapping[str, Any]],
    ) -> _EvaluatedTrigger:
        if not quality_gate.allowed:
            return _EvaluatedTrigger(
                trigger=trigger,
                library_object=library_object,
                quality_gate=quality_gate,
                evaluation_result="rejected",
                reason_code="QUALITY_GATE_BLOCKED",
                evaluated_field_refs=[],
                matched_values=[],
            )

        if not self._scope_matches(prior_context, library_object, trigger):
            return _EvaluatedTrigger(
                trigger=trigger,
                library_object=library_object,
                quality_gate=quality_gate,
                evaluation_result="rejected",
                reason_code="TRIGGER_SCOPE_MISMATCH",
                evaluated_field_refs=[],
                matched_values=[],
            )

        field_values: dict[str, list[Any]] = {}
        evaluated_refs: list[str] = []
        for required_field in trigger.required_fields:
            extracted = _extract_field_values(
                required_field,
                prior_context=prior_context,
                library_object=library_object,
                quality_records=quality_records,
            )
            if not extracted["present"]:
                return _EvaluatedTrigger(
                    trigger=trigger,
                    library_object=library_object,
                    quality_gate=quality_gate,
                    evaluation_result="rejected",
                    reason_code="REQUIRED_FIELD_MISSING",
                    evaluated_field_refs=_ordered_unique(evaluated_refs),
                    matched_values=[],
                )
            field_values[required_field] = extracted["values"]
            evaluated_refs.extend(extracted["refs"])

        matched = _condition_matches(
            trigger=trigger,
            raw_trigger=_find_raw_trigger(library_object, trigger.trigger_condition_id),
            library_object=library_object,
            field_values=field_values,
            quality_gate=quality_gate,
        )
        if matched:
            return _EvaluatedTrigger(
                trigger=trigger,
                library_object=library_object,
                quality_gate=quality_gate,
                evaluation_result="matched",
                reason_code="TRIGGER_MATCHED",
                evaluated_field_refs=_ordered_unique(evaluated_refs),
                matched_values=_flatten(list(field_values.values())),
            )
        return _EvaluatedTrigger(
            trigger=trigger,
            library_object=library_object,
            quality_gate=quality_gate,
            evaluation_result="not_matched",
            reason_code="TRIGGER_NOT_MATCHED",
            evaluated_field_refs=_ordered_unique(evaluated_refs),
            matched_values=[],
        )

    def _scope_matches(
        self,
        prior_context: _PriorContext,
        library_object: Mapping[str, Any],
        trigger: TriggerCondition,
    ) -> bool:
        library_scope = _library_scope(library_object)
        if library_scope and trigger.scope != library_scope:
            return False
        if prior_context.declared_scopes and trigger.scope not in prior_context.declared_scopes:
            return False
        return True

    def _materialize_result(
        self,
        prior_context: _PriorContext,
        evaluations: Sequence[_EvaluatedTrigger],
    ) -> ActivationResult:
        matched_groups: dict[tuple[str, str, str, str, str], list[_EvaluatedTrigger]] = defaultdict(list)
        passthrough_evaluations: list[_EvaluatedTrigger] = []
        for evaluation in evaluations:
            if evaluation.evaluation_result == "matched":
                group_key = (
                    prior_context.facility_id,
                    prior_context.prior_id,
                    prior_context.prior_version,
                    evaluation.trigger.activation_case_type,
                    self.activation_rule_version,
                )
                matched_groups[group_key].append(evaluation)
            else:
                passthrough_evaluations.append(evaluation)

        inference_cases: list[InferenceCase] = []
        activation_records: list[ActivationRecord] = []
        trigger_logs: list[TriggerLogEntry] = []

        matched_evaluation_refs: dict[str, tuple[str, str]] = {}
        for group_key in sorted(matched_groups):
            group = sorted(
                matched_groups[group_key],
                key=lambda item: (
                    item.trigger.trigger_priority,
                    item.trigger.trigger_condition_id,
                    item.trigger.version,
                ),
            )
            primary = group[0]
            supporting_trigger_refs = _ordered_unique(
                [item.trigger.trigger_condition_id for item in group]
            )
            activation_id = self._activation_id(
                prior_context=prior_context,
                trigger=primary.trigger,
                result="activated",
                reason_code="TRIGGER_MATCHED",
                evaluated_input_refs=self._evaluated_input_refs(
                    prior_context, primary
                ),
            )
            case_id = self._case_id(
                prior_context=prior_context,
                activation_case_type=primary.trigger.activation_case_type,
                primary_trigger_ref=primary.trigger.trigger_condition_id,
                supporting_trigger_refs=supporting_trigger_refs,
            )
            activation_record = self._build_activation_record(
                prior_context=prior_context,
                evaluation=primary,
                activation_id=activation_id,
                case_id=case_id,
                result="activated",
                reason_code="TRIGGER_MATCHED",
                decision_detail_refs=supporting_trigger_refs,
            )
            case = self._build_inference_case(
                prior_context=prior_context,
                primary=primary,
                group=group,
                case_id=case_id,
                activation_record_ref=activation_id,
                supporting_trigger_refs=supporting_trigger_refs,
            )
            inference_cases.append(case)
            activation_records.append(activation_record)
            for evaluation in group:
                matched_evaluation_refs[evaluation.trigger.trigger_condition_id] = (
                    activation_id,
                    case_id,
                )

        for evaluation in sorted(
            passthrough_evaluations,
            key=lambda item: (
                item.trigger.trigger_priority,
                item.trigger.trigger_condition_id,
                item.reason_code,
            ),
        ):
            activation_id = self._activation_id(
                prior_context=prior_context,
                trigger=evaluation.trigger,
                result=_activation_result_for_evaluation(evaluation.evaluation_result),
                reason_code=evaluation.reason_code,
                evaluated_input_refs=self._evaluated_input_refs(
                    prior_context, evaluation
                ),
            )
            activation_record = self._build_activation_record(
                prior_context=prior_context,
                evaluation=evaluation,
                activation_id=activation_id,
                case_id=None,
                result=_activation_result_for_evaluation(evaluation.evaluation_result),
                reason_code=evaluation.reason_code,
                decision_detail_refs=evaluation.quality_gate.blocking_refs,
            )
            activation_records.append(activation_record)
            trigger_logs.append(
                self._build_trigger_log(
                    prior_context=prior_context,
                    evaluation=evaluation,
                    activation_record_ref=activation_id,
                    case_ref=None,
                )
            )

        for evaluation in sorted(
            [item for group in matched_groups.values() for item in group],
            key=lambda item: (
                item.trigger.trigger_priority,
                item.trigger.trigger_condition_id,
                item.trigger.version,
            ),
        ):
            activation_record_ref, case_ref = matched_evaluation_refs[
                evaluation.trigger.trigger_condition_id
            ]
            trigger_logs.append(
                self._build_trigger_log(
                    prior_context=prior_context,
                    evaluation=evaluation,
                    activation_record_ref=activation_record_ref,
                    case_ref=case_ref,
                )
            )

        result = ActivationResult(
            inference_case=sorted(
                inference_cases,
                key=lambda item: (item.activation_case_type, item.case_id),
            ),
            activation_record=sorted(
                activation_records,
                key=lambda item: (item.trigger_condition_ref, item.activation_id),
            ),
            trigger_log=sorted(
                trigger_logs,
                key=lambda item: (item.trigger_condition_ref, item.trigger_log_id),
            ),
        )
        self._validate_result(result)
        return result

    def _build_inference_case(
        self,
        *,
        prior_context: _PriorContext,
        primary: _EvaluatedTrigger,
        group: Sequence[_EvaluatedTrigger],
        case_id: str,
        activation_record_ref: str,
        supporting_trigger_refs: list[str],
    ) -> InferenceCase:
        quality_refs = _ordered_unique(
            [
                ref
                for evaluation in group
                for ref in evaluation.quality_gate.quality_record_refs
            ]
        )
        conditional_notes = _ordered_unique(
            [
                note
                for evaluation in group
                for note in evaluation.quality_gate.conditional_quality_notes
            ]
        )
        library_refs = _ordered_unique(
            [_library_object_id(evaluation.library_object) for evaluation in group]
        )
        lineage_refs = _ordered_unique(
            [
                *prior_context.lineage_refs,
                *[
                    ref
                    for evaluation in group
                    for ref in evaluation.trigger.lineage_refs
                ],
                *[
                    ref
                    for evaluation in group
                    for ref in evaluation.quality_gate.lineage_refs
                ],
                self.activation_rule_version,
            ]
        )
        provenance_refs = _ordered_unique(
            [
                *prior_context.provenance_refs,
                *[
                    ref
                    for evaluation in group
                    for ref in evaluation.trigger.provenance_refs
                ],
                *[
                    ref
                    for evaluation in group
                    for ref in evaluation.quality_gate.provenance_refs
                ],
            ]
        )
        lineage_id = _stable_id(
            "case_lineage",
            prior_context.lineage_id,
            primary.trigger.trigger_condition_id,
            supporting_trigger_refs,
            self.activation_rule_version,
        )
        base = {
            "case_id": case_id,
            "record_id": case_id,
            "facility_id": prior_context.facility_id,
            "source_prior_ref": prior_context.prior_id,
            "source_prior_version": prior_context.prior_version,
            "contextual_bundle_refs": prior_context.contextual_bundle_refs,
            "library_object_refs": library_refs,
            "trigger_condition_ref": primary.trigger.trigger_condition_id,
            "supporting_trigger_refs": supporting_trigger_refs,
            "activation_record_ref": activation_record_ref,
            "activation_case_type": primary.trigger.activation_case_type,
            "case_status": "activated",
            "activation_rule_version": self.activation_rule_version,
            "quality_record_refs": quality_refs,
            "conditional_quality_notes": conditional_notes,
            "activation_rationale_code": "TRIGGER_MATCHED",
            "provenance_refs": provenance_refs,
            "lineage_id": lineage_id,
            "lineage_refs": lineage_refs,
            "source_ref": prior_context.prior_id,
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": None,
            "version_id": _stable_id("case_version", case_id),
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
        }
        base["version_hash"] = _stable_hash(_without_hash(base))
        return InferenceCase(**base)

    def _build_activation_record(
        self,
        *,
        prior_context: _PriorContext,
        evaluation: _EvaluatedTrigger,
        activation_id: str,
        case_id: str | None,
        result: str,
        reason_code: str,
        decision_detail_refs: Sequence[str],
    ) -> ActivationRecord:
        lineage_refs = _ordered_unique(
            [
                *prior_context.lineage_refs,
                *evaluation.trigger.lineage_refs,
                *evaluation.quality_gate.lineage_refs,
                self.activation_rule_version,
            ]
        )
        provenance_refs = _ordered_unique(
            [
                *prior_context.provenance_refs,
                *evaluation.trigger.provenance_refs,
                *evaluation.quality_gate.provenance_refs,
            ]
        )
        lineage_id = _stable_id(
            "activation_lineage",
            prior_context.lineage_id,
            evaluation.trigger.trigger_condition_id,
            result,
            reason_code,
            self.activation_rule_version,
        )
        base = {
            "activation_id": activation_id,
            "record_id": activation_id,
            "case_id": case_id,
            "facility_id": prior_context.facility_id,
            "source_prior_ref": prior_context.prior_id,
            "evaluated_input_refs": self._evaluated_input_refs(
                prior_context, evaluation
            ),
            "trigger_condition_ref": evaluation.trigger.trigger_condition_id,
            "trigger_version": evaluation.trigger.version,
            "activation_case_type": evaluation.trigger.activation_case_type,
            "result": result,
            "reason_code": reason_code,
            "decision_detail_refs": _ordered_unique(decision_detail_refs),
            "activation_rule_version": self.activation_rule_version,
            "provenance_refs": provenance_refs,
            "lineage_id": lineage_id,
            "lineage_refs": lineage_refs,
            "source_ref": f"{prior_context.prior_id}:{evaluation.trigger.trigger_condition_id}",
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": None,
            "version_id": _stable_id("activation_version", activation_id),
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
        }
        base["version_hash"] = _stable_hash(_without_hash(base))
        return ActivationRecord(**base)

    def _build_trigger_log(
        self,
        *,
        prior_context: _PriorContext,
        evaluation: _EvaluatedTrigger,
        activation_record_ref: str,
        case_ref: str | None,
    ) -> TriggerLogEntry:
        lineage_refs = _ordered_unique(
            [
                *prior_context.lineage_refs,
                *evaluation.trigger.lineage_refs,
                *evaluation.quality_gate.lineage_refs,
                self.activation_rule_version,
            ]
        )
        provenance_refs = _ordered_unique(
            [
                *prior_context.provenance_refs,
                *evaluation.trigger.provenance_refs,
                *evaluation.quality_gate.provenance_refs,
            ]
        )
        trigger_log_id = _stable_id(
            "trigger_log",
            MOTOR_ID,
            prior_context.prior_id,
            evaluation.trigger.trigger_condition_id,
            evaluation.evaluated_field_refs,
            evaluation.evaluation_result,
            evaluation.reason_code,
            self.activation_rule_version,
        )
        lineage_id = _stable_id(
            "trigger_log_lineage",
            prior_context.lineage_id,
            evaluation.trigger.trigger_condition_id,
            evaluation.evaluation_result,
            self.activation_rule_version,
        )
        base = {
            "trigger_log_id": trigger_log_id,
            "record_id": trigger_log_id,
            "trigger_condition_ref": evaluation.trigger.trigger_condition_id,
            "facility_prior_ref": prior_context.prior_id,
            "facility_id": prior_context.facility_id,
            "library_object_ref": evaluation.trigger.library_object_ref,
            "evaluated_field_refs": evaluation.evaluated_field_refs,
            "evaluation_result": evaluation.evaluation_result,
            "reason_code": evaluation.reason_code,
            "activation_record_ref": activation_record_ref,
            "case_ref": case_ref,
            "evaluated_at": self.produced_at,
            "activation_rule_version": self.activation_rule_version,
            "provenance_refs": provenance_refs,
            "lineage_id": lineage_id,
            "lineage_refs": lineage_refs,
            "source_ref": f"{prior_context.prior_id}:{evaluation.trigger.trigger_condition_id}",
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": None,
            "version_id": _stable_id("trigger_log_version", trigger_log_id),
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
        }
        base["version_hash"] = _stable_hash(_without_hash(base))
        return TriggerLogEntry(**base)

    def _evaluated_input_refs(
        self, prior_context: _PriorContext, evaluation: _EvaluatedTrigger
    ) -> list[str]:
        return _ordered_unique(
            [
                prior_context.prior_id,
                *prior_context.contextual_bundle_refs,
                evaluation.trigger.library_object_ref,
                *evaluation.quality_gate.quality_record_refs,
            ]
        )

    def _case_id(
        self,
        *,
        prior_context: _PriorContext,
        activation_case_type: str,
        primary_trigger_ref: str,
        supporting_trigger_refs: Sequence[str],
    ) -> str:
        return _stable_id(
            "case",
            MOTOR_ID,
            prior_context.facility_id,
            prior_context.prior_id,
            prior_context.prior_version,
            activation_case_type,
            primary_trigger_ref,
            sorted(supporting_trigger_refs),
            self.activation_rule_version,
        )

    def _activation_id(
        self,
        *,
        prior_context: _PriorContext,
        trigger: TriggerCondition,
        result: str,
        reason_code: str,
        evaluated_input_refs: Sequence[str],
    ) -> str:
        return _stable_id(
            "activation",
            MOTOR_ID,
            prior_context.prior_id,
            trigger.trigger_condition_id,
            trigger.version,
            sorted(evaluated_input_refs),
            result,
            reason_code,
            self.activation_rule_version,
        )

    def _validate_result(self, result: ActivationResult) -> None:
        payload = result.to_dict()
        _assert_no_forbidden_output_keys(payload)

        for case in result.inference_case:
            required = (
                "case_id",
                "facility_id",
                "source_prior_ref",
                "source_prior_version",
                "trigger_condition_ref",
                "activation_record_ref",
                "created_at",
                "lineage_id",
                "lineage_refs",
                "provenance_refs",
                "version_id",
                "version_hash",
            )
            _assert_required_output(case.to_dict(), required, "InferenceCase")
            if case.case_status != "activated":
                raise InferenceActivationError(
                    code="OUTPUT_VALIDATION_ERROR",
                    message="emitted inference cases must have case_status activated",
                    field="InferenceCase.case_status",
                )

        for record in result.activation_record:
            required = (
                "activation_id",
                "facility_id",
                "source_prior_ref",
                "evaluated_input_refs",
                "trigger_condition_ref",
                "trigger_version",
                "result",
                "reason_code",
                "lineage_id",
                "lineage_refs",
                "version_id",
                "version_hash",
            )
            _assert_required_output(record.to_dict(), required, "ActivationRecord")

        for log in result.trigger_log:
            required = (
                "trigger_log_id",
                "trigger_condition_ref",
                "facility_prior_ref",
                "evaluation_result",
                "reason_code",
                "activation_record_ref",
                "evaluated_at",
                "lineage_id",
                "lineage_refs",
                "version_id",
                "version_hash",
            )
            _assert_required_output(log.to_dict(), required, "TriggerLogEntry")


def run_inference_case_activation(
    *,
    facility_prior: Mapping[str, Any],
    library_objects: Sequence[Mapping[str, Any]],
    quality_records: Sequence[Mapping[str, Any]],
    activation_rule_version: str = DEFAULT_ACTIVATION_RULE_VERSION,
    produced_at: str = DEFAULT_PRODUCED_AT,
) -> ActivationResult:
    engine = InferenceCaseActivationEngine(
        activation_rule_version=activation_rule_version,
        produced_at=produced_at,
    )
    return engine.activate(
        facility_prior=facility_prior,
        library_objects=library_objects,
        quality_records=quality_records,
    )


def _to_mapping(value: Any) -> Mapping[str, Any]:
    if isinstance(value, Mapping):
        return value
    if is_dataclass(value):
        return value.to_dict() if hasattr(value, "to_dict") else vars(value)
    raise InferenceActivationError(
        code="INPUT_VALIDATION_ERROR",
        message="expected a structured mapping",
        field=type(value).__name__,
    )


def _as_record_list(
    field: str, value: Any, error_code: str
) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise InferenceActivationError(
            code=error_code,
            message=f"{field} must be a list of structured records",
            field=field,
        )
    records: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        try:
            records.append(copy.deepcopy(dict(_to_mapping(item))))
        except InferenceActivationError as exc:
            raise InferenceActivationError(
                code=error_code,
                message=f"{field} must contain only structured records",
                field=f"{field}[{index}]",
            ) from exc
    return records


def _as_optional_record_list(value: Any) -> list[Mapping[str, Any]]:
    if value in (None, ""):
        return []
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise InferenceActivationError(
            code="INPUT_VALIDATION_ERROR",
            message="contextual_bundles must be a list when present",
            field="facility_prior.contextual_bundles",
        )
    return [copy.deepcopy(dict(_to_mapping(item))) for item in value]


def _first_text(record: Mapping[str, Any], keys: Sequence[str]) -> str:
    for key in keys:
        value = record.get(key)
        if isinstance(value, str) and value.strip():
            return value.strip()
        if value is not None and not isinstance(value, (Mapping, list, tuple, set)):
            text = str(value).strip()
            if text:
                return text
    return ""


def _optional_text(value: Any) -> str | None:
    if value is None:
        return None
    text = str(value).strip()
    return text or None


def _require_text(value: Any, field: str, code: str) -> str:
    text = str(value).strip() if value is not None else ""
    if not text:
        raise InferenceActivationError(
            code=code,
            message=f"{field} must be non-empty",
            field=field,
        )
    return text


def _string_list(value: Any) -> list[str]:
    if value is None or value == "":
        return []
    if isinstance(value, str):
        return [value] if value.strip() else []
    if isinstance(value, Mapping):
        return [str(item).strip() for item in value.values() if str(item).strip()]
    if isinstance(value, Sequence) and not isinstance(value, (bytes, bytearray)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _ordered_unique(values: Sequence[Any]) -> list[Any]:
    seen: set[str] = set()
    unique: list[Any] = []
    for value in values:
        if value in (None, ""):
            continue
        marker = json.dumps(value, sort_keys=True, default=str)
        if marker in seen:
            continue
        seen.add(marker)
        unique.append(value)
    return unique


def _declared_scopes(
    facility_prior: Mapping[str, Any], contextual_bundles: Sequence[Mapping[str, Any]]
) -> set[str]:
    scope_values: list[str] = []
    for key in (
        "scope",
        "prior_scope",
        "context_scope",
        "scope_context",
        "facility_scope",
    ):
        scope_values.extend(_string_list(facility_prior.get(key)))
    scope_values.extend(_string_list(facility_prior.get("activation_scopes")))
    for bundle in contextual_bundles:
        for key in ("scope", "context_scope", "bundle_scope"):
            scope_values.extend(_string_list(bundle.get(key)))
    return {scope for scope in scope_values if scope}


def _library_object_id(library_object: Mapping[str, Any]) -> str:
    return _first_text(library_object, ("library_object_id", "record_id", "object_id"))


def _library_object_version(library_object: Mapping[str, Any]) -> str:
    return _first_text(
        library_object,
        ("version", "library_object_version", "version_id", "content_version"),
    )


def _library_scope(library_object: Mapping[str, Any]) -> str:
    return _first_text(library_object, ("scope", "bundle_scope", "object_scope"))


def _raw_triggers(library_object: Mapping[str, Any]) -> list[Mapping[str, Any]]:
    for key in ("triggers", "trigger_conditions", "activation_triggers"):
        value = library_object.get(key)
        if value:
            if not isinstance(value, Sequence) or isinstance(
                value, (str, bytes, bytearray)
            ):
                raise InferenceActivationError(
                    code="LIBRARY_OBJECT_INVALID",
                    message="trigger definitions must be a list",
                    field=f"{_library_object_id(library_object)}.{key}",
                )
            return [dict(_to_mapping(item)) for item in value]
    return []


def _find_raw_trigger(
    library_object: Mapping[str, Any], trigger_condition_id: str
) -> Mapping[str, Any]:
    for trigger in _raw_triggers(library_object):
        if _first_text(trigger, ("trigger_condition_id", "trigger_id", "record_id")) == trigger_condition_id:
            return trigger
    return {}


def _quality_status(record: Mapping[str, Any]) -> str:
    status = _first_text(
        record,
        ("fitness_status", "evaluation_status", "status", "quality_status"),
    )
    return status.upper()


def _quality_blocked(record: Mapping[str, Any]) -> bool:
    for key in ("blocking_flag", "blocking", "blocking_flag_present"):
        if bool(record.get(key)):
            return True
    flags = record.get("quality_flags") or record.get("flags") or []
    if isinstance(flags, Sequence) and not isinstance(flags, (str, bytes, bytearray)):
        for flag in flags:
            flag_mapping = _to_mapping(flag)
            if bool(flag_mapping.get("blocking")) or bool(
                flag_mapping.get("blocking_flag")
            ):
                return True
    return False


def _quality_notes(record: Mapping[str, Any]) -> list[str]:
    notes = []
    notes.extend(_string_list(record.get("condition_note")))
    notes.extend(_string_list(record.get("condition_notes")))
    flags = record.get("quality_flags") or record.get("flags") or []
    if isinstance(flags, Sequence) and not isinstance(flags, (str, bytes, bytearray)):
        for flag in flags:
            flag_mapping = _to_mapping(flag)
            if not bool(flag_mapping.get("blocking")):
                notes.extend(_string_list(flag_mapping.get("message")))
                notes.extend(_string_list(flag_mapping.get("code")))
    return _ordered_unique(notes)


def _extract_field_values(
    field_path: str,
    *,
    prior_context: _PriorContext,
    library_object: Mapping[str, Any],
    quality_records: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    field_path = field_path.strip()
    roots: list[tuple[str, Any, str]]
    if field_path.startswith("facility_prior."):
        roots = [("facility_prior", prior_context.raw, field_path.removeprefix("facility_prior."))]
    elif field_path.startswith("prior."):
        roots = [("facility_prior", prior_context.raw, field_path.removeprefix("prior."))]
    elif field_path.startswith("contextual_bundles."):
        roots = [
            (
                "contextual_bundles",
                prior_context.contextual_bundles,
                field_path.removeprefix("contextual_bundles."),
            )
        ]
    elif field_path.startswith("library_object."):
        roots = [
            ("library_object", library_object, field_path.removeprefix("library_object."))
        ]
    elif field_path.startswith("quality_records."):
        roots = [
            ("quality_records", quality_records, field_path.removeprefix("quality_records."))
        ]
    else:
        roots = [
            ("facility_prior", prior_context.raw, field_path),
            ("library_object", library_object, field_path),
        ]

    values: list[Any] = []
    refs: list[str] = []
    for root_name, root, path in roots:
        extracted = _walk_path(root, path.split("."))
        for value, ref_path in extracted:
            if value in (None, ""):
                continue
            values.append(value)
            refs.append(f"{root_name}.{ref_path}")
    flat_values = _flatten(values)
    return {
        "present": bool(flat_values),
        "values": flat_values,
        "refs": _ordered_unique(refs),
    }


def _walk_path(root: Any, parts: Sequence[str], prefix: str = "") -> list[tuple[Any, str]]:
    if not parts:
        return [(root, prefix.strip("."))]
    if isinstance(root, Mapping):
        key = parts[0]
        if key not in root:
            return []
        next_prefix = f"{prefix}.{key}" if prefix else key
        return _walk_path(root[key], parts[1:], next_prefix)
    if isinstance(root, Sequence) and not isinstance(root, (str, bytes, bytearray)):
        values: list[tuple[Any, str]] = []
        for index, item in enumerate(root):
            item_ref = _first_text(_to_mapping(item), ("bundle_id", "record_id", "quality_record_id")) if isinstance(item, Mapping) else str(index)
            next_prefix = f"{prefix}[{item_ref}]" if prefix else f"[{item_ref}]"
            values.extend(_walk_path(item, parts, next_prefix))
        return values
    return []


def _condition_matches(
    *,
    trigger: TriggerCondition,
    raw_trigger: Mapping[str, Any],
    library_object: Mapping[str, Any],
    field_values: Mapping[str, list[Any]],
    quality_gate: _QualityGate,
) -> bool:
    if trigger.condition_type == "quality_gate":
        return quality_gate.allowed

    if trigger.condition_type == "bundle_presence":
        expected_values = _expected_values(raw_trigger, library_object)
        if not expected_values:
            return all(field_values.values())
        return _any_expected_value_present(field_values, expected_values)

    if trigger.condition_type == "tag_match":
        expected_values = _expected_values(raw_trigger, library_object)
        if not expected_values:
            expected_values = _string_list(library_object.get("activation_tags"))
        if not expected_values:
            return bool(field_values) and all(field_values.values())
        return _any_expected_value_present(field_values, expected_values)

    if trigger.condition_type == "field_threshold":
        values = _flatten(list(field_values.values()))
        threshold = raw_trigger.get("threshold")
        if threshold is None:
            threshold = raw_trigger.get("threshold_value")
        if threshold is None:
            expected_values = _expected_values(raw_trigger, library_object)
            return _any_expected_value_present(field_values, expected_values)
        operator = str(raw_trigger.get("operator") or raw_trigger.get("comparison") or ">=").strip()
        return any(_compare_numeric(value, threshold, operator) for value in values)

    if trigger.condition_type == "compound":
        mode = str(raw_trigger.get("compound_operator") or raw_trigger.get("operator") or "all").lower()
        expected_values = _expected_values(raw_trigger, library_object)
        if expected_values:
            matched = _any_expected_value_present(field_values, expected_values)
        else:
            matched = all(bool(values) for values in field_values.values())
        if mode == "any":
            return matched
        return matched and all(bool(values) for values in field_values.values())

    return False


def _expected_values(
    raw_trigger: Mapping[str, Any], library_object: Mapping[str, Any]
) -> list[Any]:
    values: list[Any] = []
    for key in (
        "expected_value",
        "expected_values",
        "match_value",
        "match_values",
        "value",
        "values",
    ):
        value = raw_trigger.get(key)
        if value is None:
            continue
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            values.extend(value)
        else:
            values.append(value)
    if not values:
        values.extend(_string_list(raw_trigger.get("activation_tags")))
    if not values:
        values.extend(_string_list(library_object.get("activation_tags")))
    return _flatten(values)


def _any_expected_value_present(
    field_values: Mapping[str, list[Any]], expected_values: Sequence[Any]
) -> bool:
    expected = {_normalize_scalar(value) for value in expected_values}
    actual = {_normalize_scalar(value) for value in _flatten(list(field_values.values()))}
    return bool(expected & actual)


def _compare_numeric(value: Any, threshold: Any, operator: str) -> bool:
    try:
        left = float(value)
        right = float(threshold)
    except (TypeError, ValueError):
        return False
    if operator == ">":
        return left > right
    if operator == ">=":
        return left >= right
    if operator == "<":
        return left < right
    if operator == "<=":
        return left <= right
    if operator in ("=", "=="):
        return left == right
    if operator == "!=":
        return left != right
    return False


def _activation_result_for_evaluation(evaluation_result: str) -> str:
    if evaluation_result == "matched":
        return "activated"
    if evaluation_result == "not_matched":
        return "not_activated"
    return "rejected"


def _flatten(values: Sequence[Any]) -> list[Any]:
    flattened: list[Any] = []
    for value in values:
        if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
            flattened.extend(_flatten(list(value)))
        else:
            flattened.append(value)
    return [value for value in flattened if value not in (None, "")]


def _normalize_scalar(value: Any) -> str:
    if isinstance(value, str):
        return value.strip().lower()
    return json.dumps(value, sort_keys=True, default=str)


def _int_value(value: Any, *, default: int) -> int:
    try:
        return int(value)
    except (TypeError, ValueError):
        return default


def _without_hash(payload: Mapping[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in payload.items() if key != "version_hash"}


def _stable_hash(payload: Any) -> str:
    serialized = json.dumps(payload, sort_keys=True, separators=(",", ":"), default=str)
    return hashlib.sha256(serialized.encode("utf-8")).hexdigest()


def _stable_id(prefix: str, *parts: Any) -> str:
    return f"{prefix}_{_stable_hash(parts)[:24]}"


def _assert_no_forbidden_output_keys(value: Any) -> None:
    if isinstance(value, Mapping):
        for key, child in value.items():
            if str(key) in FORBIDDEN_OUTPUT_KEYS:
                raise InferenceActivationError(
                    code="ANALYSIS_LEAKAGE",
                    message="motor_013 output contains analysis-only field",
                    field=str(key),
                )
            _assert_no_forbidden_output_keys(child)
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            _assert_no_forbidden_output_keys(child)


def _assert_required_output(
    record: Mapping[str, Any], required_fields: Sequence[str], record_type: str
) -> None:
    missing = [
        field
        for field in required_fields
        if record.get(field) in (None, "", [], {})
    ]
    if missing:
        raise InferenceActivationError(
            code="OUTPUT_VALIDATION_ERROR",
            message=f"{record_type} is missing required output fields",
            field=", ".join(missing),
        )
