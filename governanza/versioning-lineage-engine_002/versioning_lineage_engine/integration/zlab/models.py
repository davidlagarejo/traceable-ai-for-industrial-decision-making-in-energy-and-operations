from __future__ import annotations

from collections.abc import Iterable
from typing import Union

from ..._compat import dataclass
from ...domain.entities import (
    DependencyEdge,
    DependencySnapshot,
    ObjectIdentity,
    ObjectVersion,
    ReferenceVersionRecord,
    VersionLineageNode,
)
from ...domain.errors import DomainInvariantError
from ...domain.value_objects import ExternalDependencyRef, LineageLocator


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainInvariantError(f"{field_name} must be non-empty.")
    return normalized


def _require_version_index(value: int, field_name: str) -> int:
    if value <= 0:
        raise DomainInvariantError(f"{field_name} must be > 0.")
    return value


@dataclass(frozen=True, slots=True)
class SourceRecord:
    source_key: str
    canonical_name: str
    publisher: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_key", _require_text(self.source_key, "source_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "publisher", _require_text(self.publisher, "publisher"))


@dataclass(frozen=True, slots=True)
class SourceVersion:
    source_key: str
    version_index: int
    version_label: str
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "source_key", _require_text(self.source_key, "source_key"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "version_label", _require_text(self.version_label, "version_label"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class BenchmarkBundle:
    bundle_key: str
    canonical_name: str
    version_index: int
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "bundle_key", _require_text(self.bundle_key, "bundle_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class FacilityPrior:
    prior_key: str
    canonical_name: str
    version_index: int
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "prior_key", _require_text(self.prior_key, "prior_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class TensionMap:
    tension_map_key: str
    canonical_name: str
    version_index: int
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "tension_map_key", _require_text(self.tension_map_key, "tension_map_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class OutputBlock:
    block_key: str
    canonical_name: str
    version_index: int
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "block_key", _require_text(self.block_key, "block_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class ReportPackage:
    package_key: str
    canonical_name: str
    version_index: int
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "package_key", _require_text(self.package_key, "package_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class ClaimUpgradeCandidateRegister:
    register_key: str
    canonical_name: str
    version_index: int
    content_checksum: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "register_key", _require_text(self.register_key, "register_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_index", _require_version_index(self.version_index, "version_index"))
        object.__setattr__(self, "content_checksum", _require_text(self.content_checksum, "content_checksum"))


@dataclass(frozen=True, slots=True)
class ContractVersion:
    contract_key: str
    canonical_name: str
    version_label: str
    content_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "contract_key", _require_text(self.contract_key, "contract_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_label", _require_text(self.version_label, "version_label"))
        object.__setattr__(self, "content_fingerprint", _require_text(self.content_fingerprint, "content_fingerprint"))


@dataclass(frozen=True, slots=True)
class TaxonomyVersion:
    taxonomy_key: str
    canonical_name: str
    version_label: str
    content_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "taxonomy_key", _require_text(self.taxonomy_key, "taxonomy_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_label", _require_text(self.version_label, "version_label"))
        object.__setattr__(self, "content_fingerprint", _require_text(self.content_fingerprint, "content_fingerprint"))


@dataclass(frozen=True, slots=True)
class RulePackVersion:
    rule_pack_key: str
    canonical_name: str
    version_label: str
    content_fingerprint: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "rule_pack_key", _require_text(self.rule_pack_key, "rule_pack_key"))
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(self, "version_label", _require_text(self.version_label, "version_label"))
        object.__setattr__(self, "content_fingerprint", _require_text(self.content_fingerprint, "content_fingerprint"))


ZLabVersionedObject = Union[
    SourceVersion,
    BenchmarkBundle,
    FacilityPrior,
    TensionMap,
    OutputBlock,
    ReportPackage,
    ClaimUpgradeCandidateRegister,
]

ZLabReferenceObject = Union[ContractVersion, TaxonomyVersion, RulePackVersion]


@dataclass(frozen=True, slots=True)
class IntegratedReferenceVersion:
    source_object: ZLabReferenceObject
    reference_version: ReferenceVersionRecord

    @property
    def external_dependency_ref(self) -> ExternalDependencyRef:
        return ExternalDependencyRef(
            reference_kind=self.reference_version.reference_kind,
            reference_version_record_id=self.reference_version.reference_version_record_id,
            reference_key=self.reference_version.reference_key,
            version_label=self.reference_version.version_label,
        )

    @property
    def reference(self) -> LineageLocator:
        return self.reference_version.reference


@dataclass(frozen=True, slots=True)
class IntegratedObjectVersion:
    source_object: ZLabVersionedObject
    identity: ObjectIdentity
    version: ObjectVersion
    dependency_snapshot: DependencySnapshot
    dependency_edges: tuple[DependencyEdge, ...]
    lineage_node: VersionLineageNode

    @property
    def reference(self) -> LineageLocator:
        return self.version.reference


@dataclass(frozen=True, slots=True)
class IntegratedLineageGraph:
    object_identities: tuple[ObjectIdentity, ...]
    object_versions: tuple[ObjectVersion, ...]
    dependency_edges: tuple[DependencyEdge, ...]
    dependency_snapshots: tuple[DependencySnapshot, ...]
    reference_versions: tuple[ReferenceVersionRecord, ...]
    version_lineage_nodes: tuple[VersionLineageNode, ...]

    @classmethod
    def from_parts(
        cls,
        *,
        objects: Iterable[IntegratedObjectVersion] = (),
        references: Iterable[IntegratedReferenceVersion] = (),
        identities: Iterable[ObjectIdentity] = (),
    ) -> "IntegratedLineageGraph":
        identities_out: list[ObjectIdentity] = []
        seen_identities: dict[object, ObjectIdentity] = {}

        for item in identities:
            _append_unique_or_raise_conflict(
                seen=seen_identities,
                key=item.object_identity_id,
                value=item,
                field_name="object_identities",
                output=identities_out,
            )

        object_versions: list[ObjectVersion] = []
        seen_versions: dict[object, ObjectVersion] = {}
        dependency_edges: list[DependencyEdge] = []
        seen_edges: dict[object, DependencyEdge] = {}
        dependency_snapshots: list[DependencySnapshot] = []
        seen_snapshots: dict[object, DependencySnapshot] = {}
        version_lineage_nodes: list[VersionLineageNode] = []
        seen_nodes: dict[object, VersionLineageNode] = {}

        for item in objects:
            _append_unique_or_raise_conflict(
                seen=seen_identities,
                key=item.identity.object_identity_id,
                value=item.identity,
                field_name="object_identities",
                output=identities_out,
            )
            _append_unique_or_raise_conflict(
                seen=seen_versions,
                key=item.version.object_version_id,
                value=item.version,
                field_name="object_versions",
                output=object_versions,
            )
            _append_unique_or_raise_conflict(
                seen=seen_snapshots,
                key=item.dependency_snapshot.dependency_snapshot_id,
                value=item.dependency_snapshot,
                field_name="dependency_snapshots",
                output=dependency_snapshots,
            )
            _append_unique_or_raise_conflict(
                seen=seen_nodes,
                key=item.lineage_node.version_lineage_node_id,
                value=item.lineage_node,
                field_name="version_lineage_nodes",
                output=version_lineage_nodes,
            )
            for edge in item.dependency_edges:
                _append_unique_or_raise_conflict(
                    seen=seen_edges,
                    key=edge.dependency_edge_id,
                    value=edge,
                    field_name="dependency_edges",
                    output=dependency_edges,
                )

        reference_versions: list[ReferenceVersionRecord] = []
        seen_references: dict[object, ReferenceVersionRecord] = {}
        for item in references:
            _append_unique_or_raise_conflict(
                seen=seen_references,
                key=item.reference_version.reference_version_record_id,
                value=item.reference_version,
                field_name="reference_versions",
                output=reference_versions,
            )

        return cls(
            object_identities=tuple(identities_out),
            object_versions=tuple(object_versions),
            dependency_edges=tuple(dependency_edges),
            dependency_snapshots=tuple(dependency_snapshots),
            reference_versions=tuple(reference_versions),
            version_lineage_nodes=tuple(version_lineage_nodes),
        )

    def graph_index(self):
        from ...evolution import LineageGraphIndex

        return LineageGraphIndex.from_iterables(
            object_versions=self.object_versions,
            dependency_edges=self.dependency_edges,
            dependency_snapshots=self.dependency_snapshots,
            reference_versions=self.reference_versions,
        )


def _append_unique_or_raise_conflict(*, seen: dict[object, object], key: object, value: object, field_name: str, output: list[object]) -> None:
    existing = seen.get(key)
    if existing is None:
        seen[key] = value
        output.append(value)
        return
    if existing != value:
        raise DomainInvariantError(
            f"{field_name} contains conflicting entries for the same identifier: {key}."
        )


__all__ = [
    "BenchmarkBundle",
    "ClaimUpgradeCandidateRegister",
    "ContractVersion",
    "FacilityPrior",
    "IntegratedLineageGraph",
    "IntegratedObjectVersion",
    "IntegratedReferenceVersion",
    "OutputBlock",
    "ReportPackage",
    "RulePackVersion",
    "SourceRecord",
    "SourceVersion",
    "TaxonomyVersion",
    "TensionMap",
]
