from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from ...domain.entities import (
    DependencyEdge,
    DependencySnapshot,
    ObjectIdentity,
    ObjectVersion,
    ReferenceVersionRecord,
    VersionLineageNode,
)
from ...domain.enums import (
    ComparabilityStatus,
    DependencyType,
    IdentityStatus,
    ObjectKind,
    PhaseId,
    RebuildabilityStatus,
    ReferenceKind,
    VersionLifecycleStatus,
)
from ...domain.errors import DomainInvariantError
from ...domain.value_objects import (
    ContentChecksum,
    DependencyEdgeId,
    DependencyRole,
    DependencySnapshotId,
    EngineName,
    EngineVersion,
    Fingerprint,
    ObjectIdentityId,
    ObjectVersionId,
    ReferenceVersionRecordId,
    RebuildManifest,
    StableKey,
    VersionIndex,
    VersionLineageNodeId,
)
from .models import (
    BenchmarkBundle,
    ClaimUpgradeCandidateRegister,
    ContractVersion,
    FacilityPrior,
    IntegratedObjectVersion,
    IntegratedReferenceVersion,
    OutputBlock,
    ReportPackage,
    RulePackVersion,
    SourceRecord,
    SourceVersion,
    TaxonomyVersion,
    TensionMap,
    ZLabVersionedObject,
)


class ZLabLineageIntegrator:
    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
        producer_engine_name: str = "versioning-lineage-engine",
        producer_engine_version: str = "0.1.0",
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._producer_engine_name = EngineName(producer_engine_name)
        self._producer_engine_version = EngineVersion(producer_engine_version)

    def integrate_source_record(
        self,
        source_record: SourceRecord,
        *,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> ObjectIdentity:
        return self._build_identity(
            object_kind=ObjectKind.SOURCE_RECORD,
            phase_scope=None,
            object_key=source_record.source_key,
            canonical_name=source_record.canonical_name,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_source_version(
        self,
        source_record: SourceRecord,
        source_version: SourceVersion,
        *,
        source_identity: ObjectIdentity | None = None,
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
    ) -> IntegratedObjectVersion:
        if source_record.source_key != source_version.source_key:
            raise DomainInvariantError("SourceVersion.source_key must match SourceRecord.source_key.")
        identity = source_identity or self.integrate_source_record(source_record)
        if identity.object_kind is not ObjectKind.SOURCE_RECORD:
            raise DomainInvariantError("source_identity must belong to a source_record identity.")
        if identity.stable_key != self._stable_key(ObjectKind.SOURCE_RECORD, source_record.source_key):
            raise DomainInvariantError("source_identity does not match the provided source_record.")
        return self._integrate_versioned_object(
            source_object=source_version,
            object_kind=ObjectKind.SOURCE_RECORD,
            phase_scope=None,
            object_key=source_record.source_key,
            canonical_name=source_record.canonical_name,
            version_index=source_version.version_index,
            content_checksum=source_version.content_checksum,
            identity=identity,
            upstream_objects=(),
            upstream_dependency_type=DependencyType.SOURCE_INPUT,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
        )

    def integrate_benchmark_bundle(
        self,
        benchmark_bundle: BenchmarkBundle,
        *,
        depends_on: Iterable[IntegratedObjectVersion] = (),
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        return self._integrate_versioned_object(
            source_object=benchmark_bundle,
            object_kind=ObjectKind.BENCHMARK_BUNDLE,
            phase_scope=PhaseId.PHASE_1,
            object_key=benchmark_bundle.bundle_key,
            canonical_name=benchmark_bundle.canonical_name,
            version_index=benchmark_bundle.version_index,
            content_checksum=benchmark_bundle.content_checksum,
            upstream_objects=depends_on,
            upstream_dependency_type=DependencyType.SOURCE_INPUT,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_facility_prior(
        self,
        facility_prior: FacilityPrior,
        *,
        depends_on: Iterable[IntegratedObjectVersion] = (),
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        return self._integrate_versioned_object(
            source_object=facility_prior,
            object_kind=ObjectKind.FACILITY_PRIOR,
            phase_scope=PhaseId.PHASE_1,
            object_key=facility_prior.prior_key,
            canonical_name=facility_prior.canonical_name,
            version_index=facility_prior.version_index,
            content_checksum=facility_prior.content_checksum,
            upstream_objects=depends_on,
            upstream_dependency_type=DependencyType.DERIVES_FROM,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_tension_map(
        self,
        tension_map: TensionMap,
        *,
        depends_on: Iterable[IntegratedObjectVersion] = (),
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        return self._integrate_versioned_object(
            source_object=tension_map,
            object_kind=ObjectKind.TENSION_MAP,
            phase_scope=PhaseId.PHASE_2,
            object_key=tension_map.tension_map_key,
            canonical_name=tension_map.canonical_name,
            version_index=tension_map.version_index,
            content_checksum=tension_map.content_checksum,
            upstream_objects=depends_on,
            upstream_dependency_type=DependencyType.DERIVES_FROM,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_output_block(
        self,
        output_block: OutputBlock,
        *,
        depends_on: Iterable[IntegratedObjectVersion] = (),
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        return self._integrate_versioned_object(
            source_object=output_block,
            object_kind=ObjectKind.OUTPUT_BLOCK,
            phase_scope=PhaseId.PHASE_3,
            object_key=output_block.block_key,
            canonical_name=output_block.canonical_name,
            version_index=output_block.version_index,
            content_checksum=output_block.content_checksum,
            upstream_objects=depends_on,
            upstream_dependency_type=DependencyType.DERIVES_FROM,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_report_package(
        self,
        report_package: ReportPackage,
        *,
        depends_on: Iterable[IntegratedObjectVersion] = (),
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        return self._integrate_versioned_object(
            source_object=report_package,
            object_kind=ObjectKind.REPORT_PACKAGE,
            phase_scope=PhaseId.PHASE_3,
            object_key=report_package.package_key,
            canonical_name=report_package.canonical_name,
            version_index=report_package.version_index,
            content_checksum=report_package.content_checksum,
            upstream_objects=depends_on,
            upstream_dependency_type=DependencyType.AGGREGATES,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_claim_upgrade_candidate_register(
        self,
        register: ClaimUpgradeCandidateRegister,
        *,
        depends_on: Iterable[IntegratedObjectVersion] = (),
        contract_versions: Iterable[IntegratedReferenceVersion] = (),
        taxonomy_versions: Iterable[IntegratedReferenceVersion] = (),
        rule_pack_versions: Iterable[IntegratedReferenceVersion] = (),
        version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
        comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
        rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        return self._integrate_versioned_object(
            source_object=register,
            object_kind=ObjectKind.CLAIM_UPGRADE_CANDIDATE_REGISTER,
            phase_scope=PhaseId.PHASE_4,
            object_key=register.register_key,
            canonical_name=register.canonical_name,
            version_index=register.version_index,
            content_checksum=register.content_checksum,
            upstream_objects=depends_on,
            upstream_dependency_type=DependencyType.DERIVES_FROM,
            contract_versions=contract_versions,
            taxonomy_versions=taxonomy_versions,
            rule_pack_versions=rule_pack_versions,
            version_status=version_status,
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )

    def integrate_contract_version(self, contract_version: ContractVersion) -> IntegratedReferenceVersion:
        return self._integrate_reference_version(
            reference_kind=ReferenceKind.CONTRACT_VERSION,
            reference_key=contract_version.contract_key,
            reference_name=contract_version.canonical_name,
            version_label=contract_version.version_label,
            content_fingerprint=contract_version.content_fingerprint,
            source_object=contract_version,
        )

    def integrate_taxonomy_version(self, taxonomy_version: TaxonomyVersion) -> IntegratedReferenceVersion:
        return self._integrate_reference_version(
            reference_kind=ReferenceKind.TAXONOMY_VERSION,
            reference_key=taxonomy_version.taxonomy_key,
            reference_name=taxonomy_version.canonical_name,
            version_label=taxonomy_version.version_label,
            content_fingerprint=taxonomy_version.content_fingerprint,
            source_object=taxonomy_version,
        )

    def integrate_rule_pack_version(self, rule_pack_version: RulePackVersion) -> IntegratedReferenceVersion:
        return self._integrate_reference_version(
            reference_kind=ReferenceKind.RULE_PACK_VERSION,
            reference_key=rule_pack_version.rule_pack_key,
            reference_name=rule_pack_version.canonical_name,
            version_label=rule_pack_version.version_label,
            content_fingerprint=rule_pack_version.content_fingerprint,
            source_object=rule_pack_version,
        )

    def _integrate_reference_version(
        self,
        *,
        reference_kind: ReferenceKind,
        reference_key: str,
        reference_name: str,
        version_label: str,
        content_fingerprint: str,
        source_object,
    ) -> IntegratedReferenceVersion:
        record = ReferenceVersionRecord(
            reference_version_record_id=ReferenceVersionRecordId(
                f"reference_version:{reference_kind.value}:{reference_key}:{version_label}"
            ),
            reference_kind=reference_kind,
            reference_key=StableKey(f"reference:{reference_kind.value}:{reference_key}"),
            reference_name=reference_name,
            version_label=version_label,
            content_fingerprint=Fingerprint(content_fingerprint),
            created_at=self._clock(),
        )
        return IntegratedReferenceVersion(
            source_object=source_object,
            reference_version=record,
        )

    def _integrate_versioned_object(
        self,
        *,
        source_object: ZLabVersionedObject,
        object_kind: ObjectKind,
        phase_scope: PhaseId | None,
        object_key: str,
        canonical_name: str,
        version_index: int,
        content_checksum: str,
        upstream_objects: Iterable[IntegratedObjectVersion],
        upstream_dependency_type: DependencyType,
        contract_versions: Iterable[IntegratedReferenceVersion],
        taxonomy_versions: Iterable[IntegratedReferenceVersion],
        rule_pack_versions: Iterable[IntegratedReferenceVersion],
        version_status: VersionLifecycleStatus,
        comparability_status: ComparabilityStatus,
        rebuildability_status: RebuildabilityStatus,
        identity_status: IdentityStatus = IdentityStatus.ACTIVE,
        replacement_of_identity: ObjectIdentity | None = None,
        replaced_by_identity: ObjectIdentity | None = None,
        identity: ObjectIdentity | None = None,
    ) -> IntegratedObjectVersion:
        resolved_identity = identity or self._build_identity(
            object_kind=object_kind,
            phase_scope=phase_scope,
            object_key=object_key,
            canonical_name=canonical_name,
            identity_status=identity_status,
            replacement_of_identity=replacement_of_identity,
            replaced_by_identity=replaced_by_identity,
        )
        version_id = ObjectVersionId(
            f"object_version:{object_kind.value}:{object_key}:v{version_index}"
        )
        upstream_objects = tuple(upstream_objects)
        contract_versions = tuple(contract_versions)
        taxonomy_versions = tuple(taxonomy_versions)
        rule_pack_versions = tuple(rule_pack_versions)

        required_dependency_refs = tuple(item.reference for item in upstream_objects)
        contract_version_refs = tuple(item.external_dependency_ref for item in contract_versions)
        taxonomy_version_refs = tuple(item.external_dependency_ref for item in taxonomy_versions)
        rule_pack_version_refs = tuple(item.external_dependency_ref for item in rule_pack_versions)

        version = ObjectVersion(
            object_version_id=version_id,
            object_identity_id=resolved_identity.object_identity_id,
            version_index=VersionIndex(version_index),
            content_checksum=ContentChecksum(content_checksum),
            schema_fingerprint=Fingerprint(f"schema:{object_kind.value}:v1"),
            version_status=version_status,
            created_at=self._clock(),
            producer_engine_name=self._producer_engine_name,
            producer_engine_version=self._producer_engine_version,
            rebuild_manifest=RebuildManifest(
                target_object_version_id=version_id,
                required_dependency_refs=required_dependency_refs,
                contract_version_refs=contract_version_refs,
                taxonomy_version_refs=taxonomy_version_refs,
                rule_pack_version_refs=rule_pack_version_refs,
                library_version_refs=(),
                model_version_refs=(),
                producer_engine_name=self._producer_engine_name,
                producer_engine_version=self._producer_engine_version,
                schema_fingerprint=Fingerprint(f"schema:{object_kind.value}:v1"),
                execution_fingerprint=Fingerprint(
                    _stable_digest(
                        "execution",
                        object_kind.value,
                        object_key,
                        str(version_index),
                        content_checksum,
                        *(str(item.version.object_version_id) for item in upstream_objects),
                        *(str(item.reference_version.reference_version_record_id) for item in contract_versions),
                        *(str(item.reference_version.reference_version_record_id) for item in taxonomy_versions),
                        *(str(item.reference_version.reference_version_record_id) for item in rule_pack_versions),
                    )
                ),
                expected_content_checksum=ContentChecksum(content_checksum),
                rebuildability_status=rebuildability_status,
            ),
        )

        dependency_edges = (
            *self._build_object_dependency_edges(
                origin_version=version,
                upstream_objects=upstream_objects,
                dependency_type=upstream_dependency_type,
            ),
            *self._build_reference_dependency_edges(
                origin_version=version,
                reference_versions=contract_versions,
                dependency_type=DependencyType.USES_CONTRACT,
            ),
            *self._build_reference_dependency_edges(
                origin_version=version,
                reference_versions=taxonomy_versions,
                dependency_type=DependencyType.USES_TAXONOMY,
            ),
            *self._build_reference_dependency_edges(
                origin_version=version,
                reference_versions=rule_pack_versions,
                dependency_type=DependencyType.USES_RULE_PACK,
            ),
        )

        snapshot = DependencySnapshot(
            dependency_snapshot_id=DependencySnapshotId(f"dependency_snapshot:{version_id.value}"),
            object_version_id=version.object_version_id,
            dependency_edge_ids=tuple(item.dependency_edge_id for item in dependency_edges),
            snapshot_fingerprint=Fingerprint(
                _stable_digest(
                    "dependency_snapshot",
                    version_id.value,
                    *(item.dependency_edge_id.value for item in dependency_edges),
                )
            ),
            captured_at=self._clock(),
        )

        lineage_node = VersionLineageNode(
            version_lineage_node_id=VersionLineageNodeId(f"version_lineage_node:{version_id.value}"),
            object_version_id=version.object_version_id,
            dependency_snapshot_id=snapshot.dependency_snapshot_id,
            upstream_object_version_ids=tuple(item.version.object_version_id for item in upstream_objects),
            reference_version_ids=tuple(
                item.reference_version.reference_version_record_id
                for item in (*contract_versions, *taxonomy_versions, *rule_pack_versions)
            ),
            comparability_status=comparability_status,
            rebuildability_status=rebuildability_status,
            created_at=self._clock(),
        )

        return IntegratedObjectVersion(
            source_object=source_object,
            identity=resolved_identity,
            version=version,
            dependency_snapshot=snapshot,
            dependency_edges=tuple(dependency_edges),
            lineage_node=lineage_node,
        )

    def _build_identity(
        self,
        *,
        object_kind: ObjectKind,
        phase_scope: PhaseId | None,
        object_key: str,
        canonical_name: str,
        identity_status: IdentityStatus,
        replacement_of_identity: ObjectIdentity | None,
        replaced_by_identity: ObjectIdentity | None,
    ) -> ObjectIdentity:
        return ObjectIdentity(
            object_identity_id=ObjectIdentityId(f"object_identity:{object_kind.value}:{object_key}"),
            object_kind=object_kind,
            phase_scope=phase_scope,
            stable_key=self._stable_key(object_kind, object_key),
            canonical_name=canonical_name,
            identity_status=identity_status,
            replacement_of_identity_id=(
                None if replacement_of_identity is None else replacement_of_identity.object_identity_id
            ),
            replaced_by_identity_id=(
                None if replaced_by_identity is None else replaced_by_identity.object_identity_id
            ),
            created_at=self._clock(),
        )

    def _build_object_dependency_edges(
        self,
        *,
        origin_version: ObjectVersion,
        upstream_objects: tuple[IntegratedObjectVersion, ...],
        dependency_type: DependencyType,
    ) -> tuple[DependencyEdge, ...]:
        return tuple(
            DependencyEdge(
                dependency_edge_id=DependencyEdgeId(
                    f"dependency_edge:{origin_version.object_version_id.value}:{dependency_type.value}:{item.version.object_version_id.value}"
                ),
                from_object_version_id=origin_version.object_version_id,
                target_kind=item.reference.target_kind,
                target_ref=item.reference,
                dependency_type=dependency_type,
                required=True,
                contributes_to_rebuild=True,
                input_role=DependencyRole(_input_role_for_object_kind(item.identity.object_kind)),
                created_at=self._clock(),
            )
            for item in upstream_objects
        )

    def _build_reference_dependency_edges(
        self,
        *,
        origin_version: ObjectVersion,
        reference_versions: tuple[IntegratedReferenceVersion, ...],
        dependency_type: DependencyType,
    ) -> tuple[DependencyEdge, ...]:
        return tuple(
            DependencyEdge(
                dependency_edge_id=DependencyEdgeId(
                    f"dependency_edge:{origin_version.object_version_id.value}:{dependency_type.value}:{item.reference_version.reference_version_record_id.value}"
                ),
                from_object_version_id=origin_version.object_version_id,
                target_kind=item.reference.target_kind,
                target_ref=item.reference,
                dependency_type=dependency_type,
                required=True,
                contributes_to_rebuild=True,
                input_role=DependencyRole(_input_role_for_reference_kind(item.reference_version.reference_kind)),
                created_at=self._clock(),
            )
            for item in reference_versions
        )

    @staticmethod
    def _stable_key(object_kind: ObjectKind, object_key: str) -> StableKey:
        return StableKey(f"zlab:{object_kind.value}:{object_key}")


def _input_role_for_object_kind(object_kind: ObjectKind) -> str:
    return {
        ObjectKind.SOURCE_RECORD: "source_version",
        ObjectKind.BENCHMARK_BUNDLE: "benchmark_bundle",
        ObjectKind.FACILITY_PRIOR: "facility_prior",
        ObjectKind.TENSION_MAP: "tension_map",
        ObjectKind.OUTPUT_BLOCK: "output_block",
        ObjectKind.REPORT_PACKAGE: "report_package",
        ObjectKind.CLAIM_UPGRADE_CANDIDATE_REGISTER: "claim_upgrade_candidate_register",
    }[object_kind]


def _input_role_for_reference_kind(reference_kind: ReferenceKind) -> str:
    return {
        ReferenceKind.CONTRACT_VERSION: "contract_version",
        ReferenceKind.TAXONOMY_VERSION: "taxonomy_version",
        ReferenceKind.RULE_PACK_VERSION: "rule_pack_version",
        ReferenceKind.LIBRARY_VERSION: "library_version",
        ReferenceKind.MODEL_VERSION: "model_version",
        ReferenceKind.ENGINE_VERSION: "engine_version",
    }[reference_kind]


def _stable_digest(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


__all__ = ["ZLabLineageIntegrator"]
