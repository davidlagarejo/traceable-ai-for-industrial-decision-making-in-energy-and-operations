from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from .._compat import dataclass
from ..domain.entities import DependencyEdge, DependencySnapshot, ObjectVersion, ReferenceVersionRecord
from ..domain.enums import ChangeKind, ChangeSeverity, LineageIntegrityStatus, ReferenceKind, VersionLifecycleStatus
from ..domain.errors import DomainInvariantError
from ..domain.records import LineageIntegrityRecord, VersionDiffRecord
from ..domain.value_objects import (
    ChangeDescriptor,
    ExternalDependencyRef,
    LineageLocator,
    ObjectVersionId,
    ReferenceVersionRecordId,
    VersionDiffRecordId,
)
from .change_classifier import classify_change_set
from .models import ChangeTrigger, DiffClassification, VersionDiffAnalysis


@dataclass(frozen=True, slots=True)
class _DependencyBinding:
    dependency_type: str
    required: bool
    contributes_to_rebuild: bool
    input_role: str
    target_ref: LineageLocator

    @property
    def relation_key(self) -> tuple[str, bool, bool, str]:
        return (
            self.dependency_type,
            self.required,
            self.contributes_to_rebuild,
            self.input_role,
        )


@dataclass(frozen=True, slots=True)
class _ExternalBinding:
    field_name: str
    reference_kind: ReferenceKind
    reference_key: str
    reference_id: ReferenceVersionRecordId
    version_label: str

    @property
    def relation_key(self) -> tuple[str, ReferenceKind, str]:
        return (self.field_name, self.reference_kind, self.reference_key)

    @property
    def locator(self) -> LineageLocator:
        return LineageLocator.for_reference_version(self.reference_id)


class BasicVersionDiffer:
    def __init__(self, *, clock: Callable[[], datetime] | None = None) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def diff_versions(
        self,
        source_version: ObjectVersion,
        target_version: ObjectVersion,
        *,
        source_snapshot: DependencySnapshot | None = None,
        target_snapshot: DependencySnapshot | None = None,
        source_edges: Iterable[DependencyEdge] = (),
        target_edges: Iterable[DependencyEdge] = (),
        source_lineage_integrity: LineageIntegrityRecord | None = None,
        target_lineage_integrity: LineageIntegrityRecord | None = None,
    ) -> VersionDiffAnalysis:
        if source_version.object_identity_id != target_version.object_identity_id:
            raise DomainInvariantError(
                "BasicVersionDiffer can only compare versions from the same object identity."
            )

        source_edges = tuple(source_edges)
        target_edges = tuple(target_edges)
        change_set: list[ChangeDescriptor] = []

        change_set.extend(self._diff_version_metadata(source_version, target_version))
        change_set.extend(self._diff_dependency_snapshot(
            source_snapshot=source_snapshot,
            target_snapshot=target_snapshot,
            source_edges=source_edges,
            target_edges=target_edges,
        ))
        change_set.extend(self._diff_external_refs(
            "rebuild_manifest.contract_version_refs",
            source_version.rebuild_manifest.contract_version_refs,
            target_version.rebuild_manifest.contract_version_refs,
        ))
        change_set.extend(self._diff_external_refs(
            "rebuild_manifest.taxonomy_version_refs",
            source_version.rebuild_manifest.taxonomy_version_refs,
            target_version.rebuild_manifest.taxonomy_version_refs,
        ))
        change_set.extend(self._diff_external_refs(
            "rebuild_manifest.rule_pack_version_refs",
            source_version.rebuild_manifest.rule_pack_version_refs,
            target_version.rebuild_manifest.rule_pack_version_refs,
        ))
        change_set.extend(self._diff_external_refs(
            "rebuild_manifest.library_version_refs",
            source_version.rebuild_manifest.library_version_refs,
            target_version.rebuild_manifest.library_version_refs,
        ))
        change_set.extend(self._diff_external_refs(
            "rebuild_manifest.model_version_refs",
            source_version.rebuild_manifest.model_version_refs,
            target_version.rebuild_manifest.model_version_refs,
        ))
        change_set.extend(self._diff_required_dependency_refs(
            source_version=source_version,
            target_version=target_version,
            source_snapshot=source_snapshot,
            target_snapshot=target_snapshot,
        ))
        change_set.extend(self._diff_lineage_integrity(
            source_lineage_integrity=source_lineage_integrity,
            target_lineage_integrity=target_lineage_integrity,
        ))

        ordered_change_set = tuple(sorted(change_set, key=_change_sort_key))
        classification = classify_change_set(ordered_change_set)
        reasons = tuple(item.description for item in ordered_change_set) or (
            "No material changes detected between object versions.",
        )
        trigger = ChangeTrigger(
            trigger_ref=source_version.reference,
            replacement_ref=target_version.reference,
            classification=classification,
            reasons=reasons,
        )

        if not ordered_change_set:
            return VersionDiffAnalysis(
                version_diff_record=None,
                classification=DiffClassification.NON_MATERIAL,
                reasons=reasons,
                trigger=trigger,
            )

        version_diff_record = VersionDiffRecord.for_versions(
            version_diff_record_id=VersionDiffRecordId(
                _stable_digest(
                    "version_diff",
                    str(source_version.object_version_id),
                    str(target_version.object_version_id),
                    *(_change_signature(item) for item in ordered_change_set),
                )
            ),
            source_version=source_version,
            target_version=target_version,
            change_set=ordered_change_set,
            change_severity=_aggregate_severity(ordered_change_set),
            breaking_detected=any(item.severity is ChangeSeverity.BREAKING for item in ordered_change_set),
            generated_at=self._clock(),
        )
        return VersionDiffAnalysis(
            version_diff_record=version_diff_record,
            classification=classification,
            reasons=reasons,
            trigger=trigger,
        )

    def _diff_version_metadata(
        self,
        source_version: ObjectVersion,
        target_version: ObjectVersion,
    ) -> list[ChangeDescriptor]:
        changes: list[ChangeDescriptor] = []
        if source_version.content_checksum != target_version.content_checksum:
            changes.append(
                ChangeDescriptor(
                    path="content_checksum",
                    change_kind=ChangeKind.SEMANTIC_CHANGED,
                    old_ref=source_version.reference,
                    new_ref=target_version.reference,
                    severity=ChangeSeverity.RESTRICTIVE,
                    description="content_checksum changed between object versions.",
                )
            )
        if source_version.schema_fingerprint != target_version.schema_fingerprint:
            changes.append(
                ChangeDescriptor(
                    path="schema_fingerprint",
                    change_kind=ChangeKind.FINGERPRINT_CHANGED,
                    old_ref=source_version.reference,
                    new_ref=target_version.reference,
                    severity=ChangeSeverity.BREAKING,
                    description="schema_fingerprint changed between object versions.",
                )
            )
        if source_version.version_status != target_version.version_status:
            changes.append(
                ChangeDescriptor(
                    path="version_status",
                    change_kind=ChangeKind.STATUS_CHANGED,
                    old_ref=source_version.reference,
                    new_ref=target_version.reference,
                    severity=_status_change_severity(
                        source_version.version_status,
                        target_version.version_status,
                    ),
                    description=(
                        "version_status changed from "
                        f"{source_version.version_status.value} to {target_version.version_status.value}."
                    ),
                )
            )
        if source_version.producer_engine_name != target_version.producer_engine_name:
            changes.append(
                ChangeDescriptor(
                    path="producer_engine_name",
                    change_kind=ChangeKind.METADATA_CHANGED,
                    old_ref=source_version.reference,
                    new_ref=target_version.reference,
                    severity=ChangeSeverity.ADDITIVE,
                    description="producer_engine_name changed between object versions.",
                )
            )
        if source_version.producer_engine_version != target_version.producer_engine_version:
            changes.append(
                ChangeDescriptor(
                    path="producer_engine_version",
                    change_kind=ChangeKind.METADATA_CHANGED,
                    old_ref=source_version.reference,
                    new_ref=target_version.reference,
                    severity=ChangeSeverity.ADDITIVE,
                    description="producer_engine_version changed between object versions.",
                )
            )
        return changes

    def _diff_dependency_snapshot(
        self,
        *,
        source_snapshot: DependencySnapshot | None,
        target_snapshot: DependencySnapshot | None,
        source_edges: tuple[DependencyEdge, ...],
        target_edges: tuple[DependencyEdge, ...],
    ) -> list[ChangeDescriptor]:
        if source_snapshot is None or target_snapshot is None:
            return []

        source_bindings = _bindings_from_snapshot(source_snapshot, source_edges)
        target_bindings = _bindings_from_snapshot(target_snapshot, target_edges)
        return _diff_dependency_bindings(source_bindings, target_bindings)

    def _diff_external_refs(
        self,
        field_name: str,
        source_refs: tuple[ExternalDependencyRef, ...],
        target_refs: tuple[ExternalDependencyRef, ...],
    ) -> list[ChangeDescriptor]:
        source_bindings = tuple(_ExternalBinding(
            field_name=field_name,
            reference_kind=item.reference_kind,
            reference_key=item.reference_key.value,
            reference_id=item.reference_version_record_id,
            version_label=item.version_label,
        ) for item in source_refs)
        target_bindings = tuple(_ExternalBinding(
            field_name=field_name,
            reference_kind=item.reference_kind,
            reference_key=item.reference_key.value,
            reference_id=item.reference_version_record_id,
            version_label=item.version_label,
        ) for item in target_refs)
        return _diff_external_bindings(source_bindings, target_bindings)

    def _diff_required_dependency_refs(
        self,
        *,
        source_version: ObjectVersion,
        target_version: ObjectVersion,
        source_snapshot: DependencySnapshot | None,
        target_snapshot: DependencySnapshot | None,
    ) -> list[ChangeDescriptor]:
        if source_snapshot is not None and target_snapshot is not None:
            return []

        source_refs = tuple(sorted(
            source_version.rebuild_manifest.required_dependency_refs,
            key=_locator_sort_key,
        ))
        target_refs = tuple(sorted(
            target_version.rebuild_manifest.required_dependency_refs,
            key=_locator_sort_key,
        ))
        changes: list[ChangeDescriptor] = []
        removed = tuple(item for item in source_refs if item not in target_refs)
        added = tuple(item for item in target_refs if item not in source_refs)
        for item in removed:
            changes.append(
                ChangeDescriptor(
                    path="rebuild_manifest.required_dependency_refs",
                    change_kind=ChangeKind.CONTENT_REMOVED,
                    old_ref=item,
                    new_ref=None,
                    severity=ChangeSeverity.RESTRICTIVE,
                    description="required dependency ref removed from rebuild_manifest.",
                )
            )
        for item in added:
            changes.append(
                ChangeDescriptor(
                    path="rebuild_manifest.required_dependency_refs",
                    change_kind=ChangeKind.CONTENT_ADDED,
                    old_ref=None,
                    new_ref=item,
                    severity=ChangeSeverity.ADDITIVE,
                    description="required dependency ref added to rebuild_manifest.",
                )
            )
        return changes

    def _diff_lineage_integrity(
        self,
        *,
        source_lineage_integrity: LineageIntegrityRecord | None,
        target_lineage_integrity: LineageIntegrityRecord | None,
    ) -> list[ChangeDescriptor]:
        if source_lineage_integrity is None or target_lineage_integrity is None:
            return []
        if source_lineage_integrity.integrity_status == target_lineage_integrity.integrity_status:
            return []
        return [
            ChangeDescriptor(
                path="lineage_integrity_status",
                change_kind=ChangeKind.STATUS_CHANGED,
                old_ref=LineageLocator.for_object_version(source_lineage_integrity.object_version_id),
                new_ref=LineageLocator.for_object_version(target_lineage_integrity.object_version_id),
                severity=_integrity_change_severity(
                    source_lineage_integrity.integrity_status,
                    target_lineage_integrity.integrity_status,
                ),
                description=(
                    "lineage integrity status changed from "
                    f"{source_lineage_integrity.integrity_status.value} "
                    f"to {target_lineage_integrity.integrity_status.value}."
                ),
            )
        ]


def _bindings_from_snapshot(
    snapshot: DependencySnapshot,
    edges: tuple[DependencyEdge, ...],
) -> tuple[_DependencyBinding, ...]:
    edges_by_id = {item.dependency_edge_id: item for item in edges}
    bindings: list[_DependencyBinding] = []
    for edge_id in snapshot.dependency_edge_ids:
        edge = edges_by_id.get(edge_id)
        if edge is None:
            raise DomainInvariantError(
                "Dependency snapshots passed to BasicVersionDiffer must resolve all dependency_edge_ids."
            )
        bindings.append(
            _DependencyBinding(
                dependency_type=edge.dependency_type.value,
                required=edge.required,
                contributes_to_rebuild=edge.contributes_to_rebuild,
                input_role=edge.input_role.value,
                target_ref=edge.target_ref,
            )
        )
    return tuple(sorted(bindings, key=_binding_sort_key))


def _diff_dependency_bindings(
    source_bindings: tuple[_DependencyBinding, ...],
    target_bindings: tuple[_DependencyBinding, ...],
) -> list[ChangeDescriptor]:
    changes: list[ChangeDescriptor] = []
    source_by_key = _group_dependency_bindings(source_bindings)
    target_by_key = _group_dependency_bindings(target_bindings)
    keys = sorted(set(source_by_key) | set(target_by_key))

    for key in keys:
        removed = list(source_by_key.get(key, ()))
        added = list(target_by_key.get(key, ()))

        while removed and added:
            old = removed.pop(0)
            new = added.pop(0)
            if old.target_ref == new.target_ref:
                continue
            changes.append(
                ChangeDescriptor(
                    path=f"dependency_snapshot.{key[0]}.{key[3]}",
                    change_kind=ChangeKind.DEPENDENCY_PIN_CHANGED,
                    old_ref=old.target_ref,
                    new_ref=new.target_ref,
                    severity=ChangeSeverity.RESTRICTIVE if old.required else ChangeSeverity.ADDITIVE,
                    description="dependency snapshot pin changed for an existing dependency role.",
                )
            )

        for old in removed:
            changes.append(
                ChangeDescriptor(
                    path=f"dependency_snapshot.{key[0]}.{key[3]}",
                    change_kind=ChangeKind.CONTENT_REMOVED,
                    old_ref=old.target_ref,
                    new_ref=None,
                    severity=ChangeSeverity.BREAKING if old.required else ChangeSeverity.RESTRICTIVE,
                    description="dependency removed from dependency snapshot.",
                )
            )
        for new in added:
            changes.append(
                ChangeDescriptor(
                    path=f"dependency_snapshot.{key[0]}.{key[3]}",
                    change_kind=ChangeKind.CONTENT_ADDED,
                    old_ref=None,
                    new_ref=new.target_ref,
                    severity=ChangeSeverity.RESTRICTIVE if new.required else ChangeSeverity.ADDITIVE,
                    description="dependency added to dependency snapshot.",
                )
            )
    return changes


def _diff_external_bindings(
    source_bindings: tuple[_ExternalBinding, ...],
    target_bindings: tuple[_ExternalBinding, ...],
) -> list[ChangeDescriptor]:
    changes: list[ChangeDescriptor] = []
    source_by_key = {item.relation_key: item for item in source_bindings}
    target_by_key = {item.relation_key: item for item in target_bindings}
    keys = sorted(set(source_by_key) | set(target_by_key))

    for key in keys:
        old = source_by_key.get(key)
        new = target_by_key.get(key)
        field_name = key[0]
        severity = _external_ref_severity(field_name)
        if old is not None and new is not None:
            if old.reference_id == new.reference_id and old.version_label == new.version_label:
                continue
            changes.append(
                ChangeDescriptor(
                    path=field_name,
                    change_kind=ChangeKind.DEPENDENCY_PIN_CHANGED,
                    old_ref=old.locator,
                    new_ref=new.locator,
                    severity=severity,
                    description=f"{field_name} changed pinned reference version.",
                )
            )
        elif old is not None:
            changes.append(
                ChangeDescriptor(
                    path=field_name,
                    change_kind=ChangeKind.CONTENT_REMOVED,
                    old_ref=old.locator,
                    new_ref=None,
                    severity=severity,
                    description=f"{field_name} removed a pinned reference version.",
                )
            )
        elif new is not None:
            changes.append(
                ChangeDescriptor(
                    path=field_name,
                    change_kind=ChangeKind.CONTENT_ADDED,
                    old_ref=None,
                    new_ref=new.locator,
                    severity=severity,
                    description=f"{field_name} added a pinned reference version.",
                )
            )
    return changes


def _group_dependency_bindings(
    bindings: tuple[_DependencyBinding, ...],
) -> dict[tuple[str, bool, bool, str], tuple[_DependencyBinding, ...]]:
    grouped: dict[tuple[str, bool, bool, str], list[_DependencyBinding]] = {}
    for item in bindings:
        grouped.setdefault(item.relation_key, []).append(item)
    return {
        key: tuple(sorted(value, key=_binding_sort_key))
        for key, value in grouped.items()
    }


def _binding_sort_key(binding: _DependencyBinding) -> tuple[str, bool, bool, str, str]:
    return (
        binding.dependency_type,
        binding.required,
        binding.contributes_to_rebuild,
        binding.input_role,
        _locator_sort_key(binding.target_ref),
    )


def _locator_sort_key(locator: LineageLocator) -> str:
    return f"{locator.target_kind.value}:{locator.identifier}"


def _change_sort_key(change: ChangeDescriptor) -> tuple[str, str, str, str]:
    old_ref = _locator_sort_key(change.old_ref) if change.old_ref is not None else ""
    new_ref = _locator_sort_key(change.new_ref) if change.new_ref is not None else ""
    return (change.path, change.change_kind.value, old_ref, new_ref)


def _change_signature(change: ChangeDescriptor) -> str:
    old_ref = _locator_sort_key(change.old_ref) if change.old_ref is not None else "none"
    new_ref = _locator_sort_key(change.new_ref) if change.new_ref is not None else "none"
    return "|".join(
        (
            change.path,
            change.change_kind.value,
            change.severity.value,
            old_ref,
            new_ref,
            change.description,
        )
    )


def _stable_digest(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _aggregate_severity(change_set: tuple[ChangeDescriptor, ...]) -> ChangeSeverity:
    if any(item.severity is ChangeSeverity.BREAKING for item in change_set):
        return ChangeSeverity.BREAKING
    if any(item.severity is ChangeSeverity.RESTRICTIVE for item in change_set):
        return ChangeSeverity.RESTRICTIVE
    if any(item.severity is ChangeSeverity.UNKNOWN for item in change_set):
        return ChangeSeverity.UNKNOWN
    return ChangeSeverity.ADDITIVE


def _status_change_severity(
    source_status: VersionLifecycleStatus,
    target_status: VersionLifecycleStatus,
) -> ChangeSeverity:
    if target_status is VersionLifecycleStatus.RETIRED:
        return ChangeSeverity.BREAKING
    if target_status is VersionLifecycleStatus.SUPERSEDED:
        return ChangeSeverity.RESTRICTIVE
    if source_status is VersionLifecycleStatus.RECONSTRUCTED and target_status is VersionLifecycleStatus.ACTIVE:
        return ChangeSeverity.ADDITIVE
    return ChangeSeverity.ADDITIVE


def _integrity_change_severity(
    source_status: LineageIntegrityStatus,
    target_status: LineageIntegrityStatus,
) -> ChangeSeverity:
    if target_status is LineageIntegrityStatus.BROKEN:
        return ChangeSeverity.BREAKING
    if target_status is LineageIntegrityStatus.INCOMPLETE:
        return ChangeSeverity.RESTRICTIVE
    return ChangeSeverity.ADDITIVE


def _external_ref_severity(field_name: str) -> ChangeSeverity:
    if field_name.endswith(("contract_version_refs", "taxonomy_version_refs", "rule_pack_version_refs")):
        return ChangeSeverity.RESTRICTIVE
    return ChangeSeverity.ADDITIVE
