from __future__ import annotations

from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode
from ..domain.enums import ReplayabilityStatus
from ..domain.records import NormalizationReplayManifest


def validate_normalization_replay_manifest(
    replay_manifest: NormalizationReplayManifest,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        if replay_manifest.replayability_status is not ReplayabilityStatus.REPLAYABLE:
            collector.add(
                RuleCode.REPLAY_NOT_FULLY_REPLAYABLE,
                "Normalization replay manifest is not fully replayable.",
                field_ref="replayability_status",
            )
        return
    run = context.runs_by_id.get(replay_manifest.normalization_run_record_id)
    if run is None:
        collector.add(
            RuleCode.REPLAY_RUN_REFERENCE_INVALID,
            "Normalization replay manifest references a normalization run that is not present in validation context.",
            field_ref="normalization_run_record_id",
        )
    schema_version = context.versions_by_id.get(replay_manifest.canonical_schema_version_id)
    if schema_version is None:
        collector.add(
            RuleCode.REPLAY_SCHEMA_VERSION_REFERENCE_INVALID,
            "Normalization replay manifest references a schema version that is not present in validation context.",
            field_ref="canonical_schema_version_id",
        )
    elif run is not None and schema_version.canonical_schema_version_id != run.canonical_schema_version_id:
        collector.add(
            RuleCode.REPLAY_RUN_SCHEMA_MISMATCH,
            "Normalization replay manifest schema version does not match the normalization run schema version.",
            field_ref="canonical_schema_version_id",
        )
    if replay_manifest.normalized_record_set_id is not None:
        record_set = context.normalized_record_sets_by_id.get(replay_manifest.normalized_record_set_id)
        if record_set is None:
            collector.add(
                RuleCode.REPLAY_RECORD_SET_REFERENCE_INVALID,
                "Normalization replay manifest references a normalized record set that is not present in validation context.",
                field_ref="normalized_record_set_id",
            )
        elif (
            record_set.normalization_run_record_id != replay_manifest.normalization_run_record_id
            or record_set.canonical_schema_version_id != replay_manifest.canonical_schema_version_id
        ):
            collector.add(
                RuleCode.REPLAY_RECORD_SET_MISMATCH,
                "Normalization replay manifest record set does not match the declared normalization run or schema version.",
                field_ref="normalized_record_set_id",
            )
    if run is not None and replay_manifest.source_provenance != run.source_provenance:
        collector.add(
            RuleCode.REPLAY_SOURCE_PROVENANCE_MISMATCH,
            "Normalization replay manifest source provenance does not match the normalization run provenance.",
            field_ref="source_provenance",
        )
    for rule_id in replay_manifest.field_mapping_rule_ids:
        mapping_rule = context.mapping_rules_by_id.get(rule_id)
        if mapping_rule is None:
            collector.add(
                RuleCode.REPLAY_MAPPING_RULE_REFERENCE_INVALID,
                "Normalization replay manifest references a field mapping rule that is not present in validation context.",
                field_ref="field_mapping_rule_ids",
            )
            continue
        if run is not None and mapping_rule.canonical_schema_version_id != run.canonical_schema_version_id:
            collector.add(
                RuleCode.REPLAY_MAPPING_RULE_SCHEMA_MISMATCH,
                "Normalization replay manifest field mapping rule belongs to a different schema version than the normalization run.",
                field_ref="field_mapping_rule_ids",
            )
    for rule_id in replay_manifest.type_coercion_rule_ids:
        coercion_rule = context.coercion_rules_by_id.get(rule_id)
        if coercion_rule is None:
            collector.add(
                RuleCode.REPLAY_COERCION_RULE_REFERENCE_INVALID,
                "Normalization replay manifest references a type coercion rule that is not present in validation context.",
                field_ref="type_coercion_rule_ids",
            )
            continue
        if run is not None and coercion_rule.canonical_schema_version_id != run.canonical_schema_version_id:
            collector.add(
                RuleCode.REPLAY_COERCION_RULE_SCHEMA_MISMATCH,
                "Normalization replay manifest type coercion rule belongs to a different schema version than the normalization run.",
                field_ref="type_coercion_rule_ids",
            )
    for rule_id in replay_manifest.unit_conversion_rule_ids:
        unit_rule = context.unit_rules_by_id.get(rule_id)
        if unit_rule is None:
            collector.add(
                RuleCode.REPLAY_UNIT_RULE_REFERENCE_INVALID,
                "Normalization replay manifest references a unit conversion rule that is not present in validation context.",
                field_ref="unit_conversion_rule_ids",
            )
            continue
        if run is not None and unit_rule.canonical_schema_version_id != run.canonical_schema_version_id:
            collector.add(
                RuleCode.REPLAY_UNIT_RULE_SCHEMA_MISMATCH,
                "Normalization replay manifest unit conversion rule belongs to a different schema version than the normalization run.",
                field_ref="unit_conversion_rule_ids",
            )
    for rule_id in replay_manifest.currency_conversion_rule_ids:
        currency_rule = context.currency_rules_by_id.get(rule_id)
        if currency_rule is None:
            collector.add(
                RuleCode.REPLAY_CURRENCY_RULE_REFERENCE_INVALID,
                "Normalization replay manifest references a currency conversion rule that is not present in validation context.",
                field_ref="currency_conversion_rule_ids",
            )
            continue
        if run is not None and currency_rule.canonical_schema_version_id != run.canonical_schema_version_id:
            collector.add(
                RuleCode.REPLAY_CURRENCY_RULE_SCHEMA_MISMATCH,
                "Normalization replay manifest currency conversion rule belongs to a different schema version than the normalization run.",
                field_ref="currency_conversion_rule_ids",
            )
    if replay_manifest.replayability_status is not ReplayabilityStatus.REPLAYABLE:
        collector.add(
            RuleCode.REPLAY_NOT_FULLY_REPLAYABLE,
            "Normalization replay manifest is not fully replayable.",
            field_ref="replayability_status",
        )
