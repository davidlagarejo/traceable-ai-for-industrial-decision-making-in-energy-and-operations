from __future__ import annotations

from ..domain.enums import EvaluationStatus, ReplayabilityStatus
from ..domain.records import EvaluationReplayManifest
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_evaluation_replay_manifest(
    replay_manifest: EvaluationReplayManifest,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if context is None:
        return
    run = context.runs_by_id.get(replay_manifest.evaluation_run_record_id)
    if run is None:
        collector.add(
            RuleCode.REPLAY_RUN_REFERENCE_INVALID,
            "Replay manifest references an unknown evaluation run.",
        )
    request = context.requests_by_id.get(replay_manifest.evaluation_request_record_id)
    if request is None:
        collector.add(
            RuleCode.REPLAY_REQUEST_REFERENCE_INVALID,
            "Replay manifest references an unknown evaluation request.",
        )
    if replay_manifest.evaluation_scope_record_id not in context.scopes_by_id:
        collector.add(
            RuleCode.REPLAY_SCOPE_REFERENCE_INVALID,
            "Replay manifest references an unknown evaluation scope.",
        )
    if run is not None:
        if run.evaluation_request_record_id != replay_manifest.evaluation_request_record_id:
            collector.add(
                RuleCode.REPLAY_RUN_REQUEST_MISMATCH,
                "Replay manifest request does not match the referenced run.",
            )
        if run.evaluation_scope_record_id != replay_manifest.evaluation_scope_record_id:
            collector.add(
                RuleCode.REPLAY_RUN_SCOPE_MISMATCH,
                "Replay manifest scope does not match the referenced run.",
            )
        if run.evaluation_status is not EvaluationStatus.COMPLETED:
            collector.add(
                RuleCode.REPLAY_RUN_NOT_COMPLETED,
                "Replay manifest must reference a completed evaluation run.",
            )
        registered_rules = set(run.validation_rule_record_ids)
        for rule_id in replay_manifest.validation_rule_record_ids:
            if rule_id in context.rules_by_id and rule_id not in registered_rules:
                collector.add(
                    RuleCode.REPLAY_RULE_NOT_REGISTERED_IN_RUN,
                    f"Replay manifest rule is not registered on the referenced run: {rule_id}.",
                )
    if request is not None:
        if request.evaluation_scope_record_id != replay_manifest.evaluation_scope_record_id:
            collector.add(
                RuleCode.REPLAY_REQUEST_SCOPE_MISMATCH,
                "Replay manifest scope does not match the referenced request.",
            )
        requested_objects = set(request.evaluated_object_refs)
        for object_ref in replay_manifest.evaluated_object_refs:
            if object_ref not in requested_objects:
                collector.add(
                    RuleCode.REPLAY_OBJECT_NOT_REQUESTED,
                    f"Replay manifest object is not part of the referenced request: {object_ref}.",
                )
        requested_versions = set(request.evaluated_object_version_refs)
        if requested_versions:
            for version_ref in replay_manifest.evaluated_object_version_refs:
                if version_ref not in requested_versions:
                    collector.add(
                        RuleCode.REPLAY_OBJECT_VERSION_NOT_REQUESTED,
                        f"Replay manifest object version is not part of the referenced request: {version_ref}.",
                    )
    for rule_id in replay_manifest.validation_rule_record_ids:
        if rule_id not in context.rules_by_id:
            collector.add(
                RuleCode.REPLAY_RULE_REFERENCE_INVALID,
                f"Replay manifest references an unknown validation rule: {rule_id}.",
            )
    if replay_manifest.replayability_status is ReplayabilityStatus.PARTIALLY_REPLAYABLE:
        collector.add(
            RuleCode.REPLAY_PARTIALLY_REPLAYABLE_DECLARED,
            "Replay manifest is only partially replayable.",
        )
    elif replay_manifest.replayability_status is ReplayabilityStatus.NOT_REPLAYABLE:
        collector.add(
            RuleCode.REPLAY_NOT_REPLAYABLE_DECLARED,
            "Replay manifest is explicitly not replayable.",
        )
