from __future__ import annotations

from .inputs import ParsedFieldInput
from .results import FieldMappingResult, FieldMappingStatus, WarningDraft
from ..domain.entities import CanonicalFieldDefinition, FieldMappingRule
from ..domain.enums import FieldLifecycleStatus, RuleLifecycleStatus, WarningSeverity
from ..domain.value_objects import NonNormalizableReason


class BasicFieldMapper:
    def map_field(
        self,
        *,
        field_input: ParsedFieldInput,
        canonical_field_definitions: tuple[CanonicalFieldDefinition, ...],
        field_mapping_rules: tuple[FieldMappingRule, ...],
        canonical_schema_version_id: object,
    ) -> FieldMappingResult:
        active_fields = {
            item.canonical_field_definition_id: item
            for item in canonical_field_definitions
            if item.canonical_schema_version_id == canonical_schema_version_id
            and item.field_status is FieldLifecycleStatus.ACTIVE
        }
        exact_matches: list[tuple[FieldMappingRule, CanonicalFieldDefinition]] = []
        insufficient_matches: list[tuple[FieldMappingRule, CanonicalFieldDefinition]] = []

        for rule in field_mapping_rules:
            if rule.canonical_schema_version_id != canonical_schema_version_id:
                continue
            if rule.rule_status is not RuleLifecycleStatus.ACTIVE:
                continue
            field_definition = active_fields.get(rule.canonical_field_definition_id)
            if field_definition is None:
                continue
            evaluation = _evaluate_rule(rule, field_input)
            if evaluation == "exact":
                exact_matches.append((rule, field_definition))
            elif evaluation == "context_insufficient":
                insufficient_matches.append((rule, field_definition))

        if len(exact_matches) == 1:
            rule, field_definition = exact_matches[0]
            return FieldMappingResult(
                status=FieldMappingStatus.MATCHED,
                canonical_field_definition=field_definition,
                field_mapping_rule_id=rule.field_mapping_rule_id,
                warning_drafts=(),
                non_normalizable_reason=None,
            )
        if len(exact_matches) > 1:
            return FieldMappingResult(
                status=FieldMappingStatus.AMBIGUOUS,
                canonical_field_definition=None,
                field_mapping_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="mapping.ambiguous_rule_match",
                        severity=WarningSeverity.HIGH,
                        message=(
                            "Multiple explicit field mapping rules matched the same parsed field."
                        ),
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Multiple explicit mapping rules matched this parsed field."
                ),
            )

        unique_insufficient_fields = {
            item[1].canonical_field_definition_id: item for item in insufficient_matches
        }
        if len(unique_insufficient_fields) == 1:
            rule, field_definition = next(iter(unique_insufficient_fields.values()))
            return FieldMappingResult(
                status=FieldMappingStatus.CONTEXT_INSUFFICIENT,
                canonical_field_definition=field_definition,
                field_mapping_rule_id=rule.field_mapping_rule_id,
                warning_drafts=(
                    WarningDraft(
                        code="mapping.context_insufficient",
                        severity=WarningSeverity.MODERATE,
                        message=(
                            "A mapping rule exists for this label, but the available context is not sufficient to apply it safely."
                        ),
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Mapping context is insufficient to apply the available explicit rule."
                ),
            )
        if len(unique_insufficient_fields) > 1:
            return FieldMappingResult(
                status=FieldMappingStatus.AMBIGUOUS,
                canonical_field_definition=None,
                field_mapping_rule_id=None,
                warning_drafts=(
                    WarningDraft(
                        code="mapping.context_ambiguous",
                        severity=WarningSeverity.HIGH,
                        message=(
                            "Several mapping rules remain plausible, but the parsed field does not carry enough context to disambiguate them."
                        ),
                    ),
                ),
                non_normalizable_reason=NonNormalizableReason(
                    "Multiple mapping candidates remain plausible without sufficient context."
                ),
            )

        return FieldMappingResult(
            status=FieldMappingStatus.NO_MATCH,
            canonical_field_definition=None,
            field_mapping_rule_id=None,
            warning_drafts=(
                WarningDraft(
                    code="mapping.no_rule_match",
                    severity=WarningSeverity.MODERATE,
                    message="No explicit field mapping rule matched the parsed field.",
                ),
            ),
            non_normalizable_reason=NonNormalizableReason(
                "No explicit mapping rule matched the parsed field."
            ),
        )


def _evaluate_rule(rule: FieldMappingRule, field_input: ParsedFieldInput) -> str:
    missing_context = False
    if rule.original_label is not None and rule.original_label.normalized != field_input.original_label.normalized:
        return "no_match"
    if rule.source_path_hint is not None:
        if field_input.source_path_hint is None:
            missing_context = True
        elif field_input.source_path_hint != rule.source_path_hint:
            return "no_match"
    if rule.source_format_hint is not None:
        if field_input.source_format_hint is None:
            missing_context = True
        elif field_input.source_format_hint != rule.source_format_hint:
            return "no_match"
    if rule.required_unit_hint is not None:
        if field_input.original_unit is None:
            missing_context = True
        elif field_input.original_unit != rule.required_unit_hint:
            return "no_match"
    if rule.mapping_context is not None:
        if field_input.mapping_context is None:
            missing_context = True
        elif field_input.mapping_context != rule.mapping_context:
            return "no_match"
    return "context_insufficient" if missing_context else "exact"
