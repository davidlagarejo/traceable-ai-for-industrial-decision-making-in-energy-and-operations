from __future__ import annotations

from collections.abc import Mapping

from ..domain.value_objects import MetadataKey, MetadataPreservationPolicy, ScopedContractRef
from .collector import ViolationCollector
from .rules import RuleCode


def validate_required_metadata(
    *,
    scope_ref: ScopedContractRef,
    required_keys: tuple[MetadataKey, ...],
    payload_metadata: Mapping[str, object] | None,
    collector: ViolationCollector,
    evidence_root: str,
) -> None:
    if payload_metadata is None:
        return

    for metadata_key in required_keys:
        if metadata_key.value not in payload_metadata:
            collector.add(
                RuleCode.METADATA_REQUIRED_KEY_MISSING,
                message=f"Required metadata key '{metadata_key.value}' is missing.",
                evidence_ref=f"{evidence_root}.{metadata_key.value}",
                scope_ref=scope_ref,
            )


def validate_metadata_preservation(
    *,
    scope_ref: ScopedContractRef,
    policy: MetadataPreservationPolicy,
    source_metadata: Mapping[str, object] | None,
    target_metadata: Mapping[str, object] | None,
    collector: ViolationCollector,
    evidence_root: str,
) -> None:
    if source_metadata is None or target_metadata is None:
        return

    validate_required_metadata(
        scope_ref=scope_ref,
        required_keys=policy.required_keys,
        payload_metadata=target_metadata,
        collector=collector,
        evidence_root=f"{evidence_root}.target",
    )

    for metadata_key in policy.immutable_keys:
        key = metadata_key.value
        if key not in source_metadata:
            continue
        if key not in target_metadata:
            collector.add(
                RuleCode.METADATA_IMMUTABLE_KEY_DROPPED,
                message=f"Immutable metadata key '{key}' was dropped during handoff.",
                evidence_ref=f"{evidence_root}.target.{key}",
                scope_ref=scope_ref,
            )
            continue
        if source_metadata[key] != target_metadata[key]:
            collector.add(
                RuleCode.METADATA_IMMUTABLE_KEY_CHANGED,
                message=f"Immutable metadata key '{key}' changed during handoff.",
                evidence_ref=f"{evidence_root}.target.{key}",
                scope_ref=scope_ref,
            )

    for metadata_key in policy.passthrough_keys:
        key = metadata_key.value
        if key in source_metadata and key not in target_metadata:
            collector.add(
                RuleCode.METADATA_PASSTHROUGH_KEY_DROPPED,
                message=f"Passthrough metadata key '{key}' was not preserved.",
                evidence_ref=f"{evidence_root}.target.{key}",
                scope_ref=scope_ref,
            )
