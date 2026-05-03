from __future__ import annotations

from datetime import datetime
from typing import Iterable, Union

from .._compat import dataclass
from .enums import (
    ChangeKind,
    ChangeSeverity,
    DependencyTargetKind,
    PhaseId,
    RebuildabilityStatus,
    ReferenceKind,
)
from .errors import DomainInvariantError


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainInvariantError(f"{field_name} must be non-empty.")
    return normalized


def _require_timezone(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise DomainInvariantError(f"{field_name} must be timezone-aware.")
    return value


def _ensure_unique(values: Iterable[object], field_name: str) -> None:
    materialized = tuple(values)
    if len(materialized) != len(set(materialized)):
        raise DomainInvariantError(f"{field_name} must not contain duplicates.")


@dataclass(frozen=True, slots=True)
class ObjectIdentityId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ObjectIdentityId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObjectVersionId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ObjectVersionId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VersionLineageNodeId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "VersionLineageNodeId.value"))


@dataclass(frozen=True, slots=True)
class DependencyEdgeId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "DependencyEdgeId.value"))


@dataclass(frozen=True, slots=True)
class DependencySnapshotId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "DependencySnapshotId.value"))


@dataclass(frozen=True, slots=True)
class VersionDiffRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "VersionDiffRecordId.value"))


@dataclass(frozen=True, slots=True)
class StaleStateRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "StaleStateRecordId.value"))


@dataclass(frozen=True, slots=True)
class ImpactSetRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ImpactSetRecordId.value"))


@dataclass(frozen=True, slots=True)
class VersionStatusRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "VersionStatusRecordId.value"))


@dataclass(frozen=True, slots=True)
class RetentionMarkerId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RetentionMarkerId.value"))


@dataclass(frozen=True, slots=True)
class LineageIntegrityRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "LineageIntegrityRecordId.value"))


@dataclass(frozen=True, slots=True)
class ReferenceVersionRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ReferenceVersionRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class StableKey:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "StableKey.value"))


@dataclass(frozen=True, slots=True)
class VersionIndex:
    value: int

    def __post_init__(self) -> None:
        if self.value <= 0:
            raise DomainInvariantError("VersionIndex.value must be > 0.")

    def __int__(self) -> int:
        return self.value


@dataclass(frozen=True, slots=True)
class ContentChecksum:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ContentChecksum.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class Fingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "Fingerprint.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EngineName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EngineName.value"))


@dataclass(frozen=True, slots=True)
class EngineVersion:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EngineVersion.value"))


@dataclass(frozen=True, slots=True)
class DependencyRole:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "DependencyRole.value"))


@dataclass(frozen=True, slots=True)
class ExternalDependencyRef:
    reference_kind: ReferenceKind
    reference_version_record_id: ReferenceVersionRecordId
    reference_key: StableKey
    version_label: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "version_label", _require_text(self.version_label, "version_label"))


LineageIdentifier = Union[ObjectIdentityId, ObjectVersionId, ReferenceVersionRecordId]


@dataclass(frozen=True, slots=True)
class LineageLocator:
    target_kind: DependencyTargetKind
    identifier: LineageIdentifier

    def __post_init__(self) -> None:
        expected_type = {
            DependencyTargetKind.OBJECT_IDENTITY: ObjectIdentityId,
            DependencyTargetKind.OBJECT_VERSION: ObjectVersionId,
            DependencyTargetKind.REFERENCE_VERSION: ReferenceVersionRecordId,
        }[self.target_kind]
        if not isinstance(self.identifier, expected_type):
            raise DomainInvariantError("LineageLocator.identifier does not match target_kind.")

    @classmethod
    def for_object_identity(cls, identifier: ObjectIdentityId) -> "LineageLocator":
        return cls(DependencyTargetKind.OBJECT_IDENTITY, identifier)

    @classmethod
    def for_object_version(cls, identifier: ObjectVersionId) -> "LineageLocator":
        return cls(DependencyTargetKind.OBJECT_VERSION, identifier)

    @classmethod
    def for_reference_version(cls, identifier: ReferenceVersionRecordId) -> "LineageLocator":
        return cls(DependencyTargetKind.REFERENCE_VERSION, identifier)


@dataclass(frozen=True, slots=True)
class ChangeDescriptor:
    path: str
    change_kind: ChangeKind
    old_ref: LineageLocator | None
    new_ref: LineageLocator | None
    severity: ChangeSeverity
    description: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _require_text(self.path, "path"))
        object.__setattr__(self, "description", _require_text(self.description, "description"))
        if self.old_ref is None and self.new_ref is None:
            raise DomainInvariantError("ChangeDescriptor must reference old_ref, new_ref or both.")


@dataclass(frozen=True, slots=True)
class RebuildManifest:
    target_object_version_id: ObjectVersionId
    required_dependency_refs: tuple[LineageLocator, ...]
    contract_version_refs: tuple[ExternalDependencyRef, ...]
    taxonomy_version_refs: tuple[ExternalDependencyRef, ...]
    rule_pack_version_refs: tuple[ExternalDependencyRef, ...]
    library_version_refs: tuple[ExternalDependencyRef, ...]
    model_version_refs: tuple[ExternalDependencyRef, ...]
    producer_engine_name: EngineName
    producer_engine_version: EngineVersion
    schema_fingerprint: Fingerprint
    execution_fingerprint: Fingerprint
    expected_content_checksum: ContentChecksum
    rebuildability_status: RebuildabilityStatus

    def __post_init__(self) -> None:
        _ensure_unique(self.required_dependency_refs, "required_dependency_refs")
        for field_name in (
            "contract_version_refs",
            "taxonomy_version_refs",
            "rule_pack_version_refs",
            "library_version_refs",
            "model_version_refs",
        ):
            _ensure_unique(getattr(self, field_name), field_name)

    @property
    def is_rebuildable(self) -> bool:
        return self.rebuildability_status is RebuildabilityStatus.REBUILDABLE


@dataclass(frozen=True, slots=True)
class PhaseOrigin:
    phase_id: PhaseId


__all__ = [
    "ChangeDescriptor",
    "ContentChecksum",
    "DependencyEdgeId",
    "DependencyRole",
    "DependencySnapshotId",
    "EngineName",
    "EngineVersion",
    "ExternalDependencyRef",
    "Fingerprint",
    "ImpactSetRecordId",
    "LineageIntegrityRecordId",
    "LineageLocator",
    "ObjectIdentityId",
    "ObjectVersionId",
    "PhaseOrigin",
    "ReferenceVersionRecordId",
    "RebuildManifest",
    "RetentionMarkerId",
    "StableKey",
    "StaleStateRecordId",
    "VersionDiffRecordId",
    "VersionIndex",
    "VersionLineageNodeId",
    "VersionStatusRecordId",
    "_ensure_unique",
    "_require_text",
    "_require_timezone",
]
