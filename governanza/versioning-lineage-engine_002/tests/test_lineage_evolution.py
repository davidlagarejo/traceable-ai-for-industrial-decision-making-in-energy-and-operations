from __future__ import annotations

from datetime import datetime, timezone
import unittest

from versioning_lineage_engine.domain.entities import (  # noqa: E402
    DependencyEdge,
    DependencySnapshot,
    ObjectIdentity,
    ObjectVersion,
    ReferenceVersionRecord,
)
from versioning_lineage_engine.domain.enums import (  # noqa: E402
    DependencyType,
    IdentityStatus,
    ObjectKind,
    PhaseId,
    RebuildabilityStatus,
    ReferenceKind,
    VersionLifecycleStatus,
)
from versioning_lineage_engine.domain.errors import DomainInvariantError  # noqa: E402
from versioning_lineage_engine.domain.value_objects import (  # noqa: E402
    ContentChecksum,
    DependencyEdgeId,
    DependencyRole,
    DependencySnapshotId,
    EngineName,
    EngineVersion,
    ExternalDependencyRef,
    Fingerprint,
    LineageLocator,
    ObjectIdentityId,
    ObjectVersionId,
    ReferenceVersionRecordId,
    RebuildManifest,
    StableKey,
    VersionIndex,
)
from versioning_lineage_engine.evolution import (  # noqa: E402
    BasicImpactAnalyzer,
    BasicVersionDiffer,
    DiffClassification,
    LineageGraphIndex,
)


def utc() -> datetime:
    return datetime(2026, 4, 9, 12, 0, tzinfo=timezone.utc)


def make_identity(
    *,
    suffix: str,
    object_kind: ObjectKind = ObjectKind.TENSION_MAP,
    phase_scope: PhaseId = PhaseId.PHASE_2,
) -> ObjectIdentity:
    return ObjectIdentity(
        object_identity_id=ObjectIdentityId(f"identity:{suffix}"),
        object_kind=object_kind,
        phase_scope=phase_scope,
        stable_key=StableKey(f"stable:{suffix}"),
        canonical_name=f"object-{suffix}",
        identity_status=IdentityStatus.ACTIVE,
        replacement_of_identity_id=None,
        replaced_by_identity_id=None,
        created_at=utc(),
    )


def make_reference(
    *,
    suffix: str,
    reference_kind: ReferenceKind = ReferenceKind.CONTRACT_VERSION,
    version_label: str = "v1",
) -> ReferenceVersionRecord:
    return ReferenceVersionRecord(
        reference_version_record_id=ReferenceVersionRecordId(f"reference:{suffix}:{version_label}"),
        reference_kind=reference_kind,
        reference_key=StableKey(f"reference-key:{suffix}"),
        reference_name=f"reference-{suffix}",
        version_label=version_label,
        content_fingerprint=Fingerprint(f"reference-fp:{suffix}:{version_label}"),
        created_at=utc(),
    )


def make_manifest(
    *,
    target_version_id: ObjectVersionId,
    checksum: str,
    schema_fingerprint: str = "schema:v1",
    required_dependency_refs: tuple[LineageLocator, ...] = (),
    contract_version_refs: tuple[ExternalDependencyRef, ...] = (),
    taxonomy_version_refs: tuple[ExternalDependencyRef, ...] = (),
    rule_pack_version_refs: tuple[ExternalDependencyRef, ...] = (),
    library_version_refs: tuple[ExternalDependencyRef, ...] = (),
    model_version_refs: tuple[ExternalDependencyRef, ...] = (),
    producer_engine_name: str = "lineage-engine",
    producer_engine_version: str = "0.1.0",
    rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
) -> RebuildManifest:
    return RebuildManifest(
        target_object_version_id=target_version_id,
        required_dependency_refs=required_dependency_refs,
        contract_version_refs=contract_version_refs,
        taxonomy_version_refs=taxonomy_version_refs,
        rule_pack_version_refs=rule_pack_version_refs,
        library_version_refs=library_version_refs,
        model_version_refs=model_version_refs,
        producer_engine_name=EngineName(producer_engine_name),
        producer_engine_version=EngineVersion(producer_engine_version),
        schema_fingerprint=Fingerprint(schema_fingerprint),
        execution_fingerprint=Fingerprint(f"exec:{target_version_id}"),
        expected_content_checksum=ContentChecksum(checksum),
        rebuildability_status=rebuildability_status,
    )


def make_version(
    identity: ObjectIdentity,
    *,
    suffix: str,
    checksum: str | None = None,
    schema_fingerprint: str = "schema:v1",
    version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
    required_dependency_refs: tuple[LineageLocator, ...] = (),
    contract_version_refs: tuple[ExternalDependencyRef, ...] = (),
    taxonomy_version_refs: tuple[ExternalDependencyRef, ...] = (),
    rule_pack_version_refs: tuple[ExternalDependencyRef, ...] = (),
    library_version_refs: tuple[ExternalDependencyRef, ...] = (),
    model_version_refs: tuple[ExternalDependencyRef, ...] = (),
    producer_engine_version: str = "0.1.0",
) -> ObjectVersion:
    version_id = ObjectVersionId(f"version:{suffix}")
    checksum_value = checksum or f"checksum:{suffix}"
    manifest = make_manifest(
        target_version_id=version_id,
        checksum=checksum_value,
        schema_fingerprint=schema_fingerprint,
        required_dependency_refs=required_dependency_refs,
        contract_version_refs=contract_version_refs,
        taxonomy_version_refs=taxonomy_version_refs,
        rule_pack_version_refs=rule_pack_version_refs,
        library_version_refs=library_version_refs,
        model_version_refs=model_version_refs,
        producer_engine_version=producer_engine_version,
    )
    return ObjectVersion(
        object_version_id=version_id,
        object_identity_id=identity.object_identity_id,
        version_index=VersionIndex(int(suffix.split("-v")[-1])),
        content_checksum=ContentChecksum(checksum_value),
        schema_fingerprint=Fingerprint(schema_fingerprint),
        version_status=version_status,
        created_at=utc(),
        producer_engine_name=EngineName("lineage-engine"),
        producer_engine_version=EngineVersion(producer_engine_version),
        rebuild_manifest=manifest,
    )


def make_edge(
    origin: ObjectVersion,
    target_ref: LineageLocator,
    *,
    suffix: str,
    dependency_type: DependencyType = DependencyType.DERIVES_FROM,
    required: bool = True,
) -> DependencyEdge:
    return DependencyEdge(
        dependency_edge_id=DependencyEdgeId(f"edge:{suffix}"),
        from_object_version_id=origin.object_version_id,
        target_kind=target_ref.target_kind,
        target_ref=target_ref,
        dependency_type=dependency_type,
        required=required,
        contributes_to_rebuild=True,
        input_role=DependencyRole("input"),
        created_at=utc(),
    )


def make_snapshot(version: ObjectVersion, *edges: DependencyEdge, suffix: str) -> DependencySnapshot:
    return DependencySnapshot(
        dependency_snapshot_id=DependencySnapshotId(f"snapshot:{suffix}"),
        object_version_id=version.object_version_id,
        dependency_edge_ids=tuple(item.dependency_edge_id for item in edges),
        snapshot_fingerprint=Fingerprint(f"snapshot-fp:{suffix}"),
        captured_at=utc(),
    )


def external_ref(record: ReferenceVersionRecord) -> ExternalDependencyRef:
    return ExternalDependencyRef(
        reference_kind=record.reference_kind,
        reference_version_record_id=record.reference_version_record_id,
        reference_key=record.reference_key,
        version_label=record.version_label,
    )


class LineageEvolutionTest(unittest.TestCase):
    def setUp(self) -> None:
        self.differ = BasicVersionDiffer(clock=lambda: datetime(2026, 4, 9, 16, 0, tzinfo=timezone.utc))
        self.impact_analyzer = BasicImpactAnalyzer(
            clock=lambda: datetime(2026, 4, 9, 16, 30, tzinfo=timezone.utc)
        )

    def test_diff_without_material_change_is_non_material(self) -> None:
        identity = make_identity(suffix="main")
        source_version = make_version(
            identity,
            suffix="main-v1",
            checksum="checksum:main-stable",
            producer_engine_version="0.1.0",
        )
        target_version = make_version(
            identity,
            suffix="main-v2",
            checksum="checksum:main-stable",
            producer_engine_version="0.2.0",
        )

        analysis = self.differ.diff_versions(source_version, target_version)

        self.assertEqual(analysis.classification, DiffClassification.NON_MATERIAL)
        self.assertIsNotNone(analysis.version_diff_record)
        self.assertEqual(len(analysis.version_diff_record.change_set), 1)

    def test_diff_with_dependency_snapshot_change_is_rebuild_recommended(self) -> None:
        upstream_identity = make_identity(suffix="upstream")
        upstream_v1 = make_version(upstream_identity, suffix="upstream-v1")
        upstream_v2 = make_version(upstream_identity, suffix="upstream-v2")
        identity = make_identity(suffix="main")
        source_version = make_version(identity, suffix="main-v1")
        target_version = make_version(identity, suffix="main-v2")
        source_edge = make_edge(source_version, upstream_v1.reference, suffix="source")
        target_edge = make_edge(target_version, upstream_v2.reference, suffix="target")
        source_snapshot = make_snapshot(source_version, source_edge, suffix="source")
        target_snapshot = make_snapshot(target_version, target_edge, suffix="target")

        analysis = self.differ.diff_versions(
            source_version,
            target_version,
            source_snapshot=source_snapshot,
            target_snapshot=target_snapshot,
            source_edges=(source_edge,),
            target_edges=(target_edge,),
        )

        self.assertEqual(analysis.classification, DiffClassification.REBUILD_RECOMMENDED)
        self.assertTrue(
            any(item.path.startswith("dependency_snapshot") for item in analysis.version_diff_record.change_set)
        )

    def test_diff_between_distinct_identities_raises(self) -> None:
        left = make_version(make_identity(suffix="left"), suffix="left-v1")
        right = make_version(make_identity(suffix="right"), suffix="right-v1")

        with self.assertRaises(DomainInvariantError):
            self.differ.diff_versions(left, right)

    def test_stale_detection_when_required_dependency_changes(self) -> None:
        upstream_identity = make_identity(suffix="upstream")
        upstream_v1 = make_version(upstream_identity, suffix="upstream-v1")
        upstream_v2 = make_version(upstream_identity, suffix="upstream-v2")
        downstream_identity = make_identity(suffix="downstream")
        downstream_version = make_version(downstream_identity, suffix="downstream-v1")
        downstream_edge = make_edge(downstream_version, upstream_v1.reference, suffix="downstream")
        graph = LineageGraphIndex.from_iterables(
            object_versions=(upstream_v1, upstream_v2, downstream_version),
            dependency_edges=(downstream_edge,),
        )

        analysis = self.differ.diff_versions(
            upstream_v1,
            upstream_v2,
            source_snapshot=make_snapshot(upstream_v1, suffix="upstream-source"),
            target_snapshot=make_snapshot(upstream_v2, suffix="upstream-target"),
            source_edges=(),
            target_edges=(),
        )
        # Content checksum changed, so the diff is material even without dependency snapshot churn.
        self.assertEqual(analysis.classification, DiffClassification.MATERIAL)

        result = self.impact_analyzer.analyze_diff(analysis, graph_index=graph)

        self.assertEqual(len(result.stale_state_records), 1)
        self.assertEqual(
            result.stale_state_records[0].stale_state.value,
            "stale_rebuild_recommended",
        )

    def test_stale_detection_when_reference_version_changes_materially(self) -> None:
        contract_v1 = make_reference(suffix="contract", version_label="v1")
        contract_v2 = make_reference(suffix="contract", version_label="v2")
        downstream_identity = make_identity(suffix="downstream")
        downstream_version = make_version(downstream_identity, suffix="downstream-v1")
        downstream_edge = make_edge(
            downstream_version,
            contract_v1.reference,
            suffix="contract-downstream",
            dependency_type=DependencyType.USES_CONTRACT,
        )
        graph = LineageGraphIndex.from_iterables(
            object_versions=(downstream_version,),
            dependency_edges=(downstream_edge,),
            reference_versions=(contract_v1, contract_v2),
        )

        result = self.impact_analyzer.analyze_reference_change(
            source_ref=contract_v1.reference,
            replacement_ref=contract_v2.reference,
            classification=DiffClassification.REBUILD_REQUIRED,
            reasons=("contract version changed materially",),
            graph_index=graph,
        )

        self.assertEqual(len(result.stale_state_records), 1)
        self.assertEqual(
            result.stale_state_records[0].stale_state.value,
            "stale_migration_required",
        )

    def test_direct_impact_analysis_returns_downstream_version(self) -> None:
        upstream_identity = make_identity(suffix="upstream")
        upstream_v1 = make_version(upstream_identity, suffix="upstream-v1")
        upstream_v2 = make_version(upstream_identity, suffix="upstream-v2")
        downstream_identity = make_identity(suffix="downstream")
        downstream_version = make_version(downstream_identity, suffix="downstream-v1")
        downstream_edge = make_edge(downstream_version, upstream_v1.reference, suffix="downstream")
        graph = LineageGraphIndex.from_iterables(
            object_versions=(upstream_v1, upstream_v2, downstream_version),
            dependency_edges=(downstream_edge,),
        )
        analysis = self.differ.diff_versions(upstream_v1, upstream_v2)

        result = self.impact_analyzer.analyze_diff(analysis, graph_index=graph)

        self.assertEqual(result.affected_object_version_ids, (downstream_version.object_version_id,))

    def test_non_material_change_does_not_affect_downstream(self) -> None:
        upstream_identity = make_identity(suffix="upstream")
        upstream_v1 = make_version(
            upstream_identity,
            suffix="upstream-v1",
            checksum="checksum:upstream-stable",
            producer_engine_version="0.1.0",
        )
        upstream_v2 = make_version(
            upstream_identity,
            suffix="upstream-v2",
            checksum="checksum:upstream-stable",
            producer_engine_version="0.2.0",
        )
        downstream_identity = make_identity(suffix="downstream")
        downstream_version = make_version(downstream_identity, suffix="downstream-v1")
        downstream_edge = make_edge(downstream_version, upstream_v1.reference, suffix="downstream")
        graph = LineageGraphIndex.from_iterables(
            object_versions=(upstream_v1, upstream_v2, downstream_version),
            dependency_edges=(downstream_edge,),
        )
        analysis = self.differ.diff_versions(upstream_v1, upstream_v2)

        result = self.impact_analyzer.analyze_diff(analysis, graph_index=graph)

        self.assertIsNone(result.impact_set_record)
        self.assertFalse(result.stale_state_records)

    def test_contract_reference_change_is_rebuild_required(self) -> None:
        contract_v1 = make_reference(suffix="contract", version_label="v1")
        contract_v2 = make_reference(suffix="contract", version_label="v2")
        identity = make_identity(suffix="main")
        source_version = make_version(
            identity,
            suffix="main-v1",
            contract_version_refs=(external_ref(contract_v1),),
        )
        target_version = make_version(
            identity,
            suffix="main-v2",
            contract_version_refs=(external_ref(contract_v2),),
        )

        analysis = self.differ.diff_versions(source_version, target_version)

        self.assertEqual(analysis.classification, DiffClassification.REBUILD_REQUIRED)

    def test_dependency_snapshot_change_is_rebuild_recommended(self) -> None:
        upstream_identity = make_identity(suffix="upstream")
        upstream_v1 = make_version(upstream_identity, suffix="upstream-v1")
        upstream_v2 = make_version(upstream_identity, suffix="upstream-v2")
        identity = make_identity(suffix="main")
        source_version = make_version(identity, suffix="main-v1")
        target_version = make_version(identity, suffix="main-v2")
        source_edge = make_edge(source_version, upstream_v1.reference, suffix="source")
        target_edge = make_edge(target_version, upstream_v2.reference, suffix="target")

        analysis = self.differ.diff_versions(
            source_version,
            target_version,
            source_snapshot=make_snapshot(source_version, source_edge, suffix="source"),
            target_snapshot=make_snapshot(target_version, target_edge, suffix="target"),
            source_edges=(source_edge,),
            target_edges=(target_edge,),
        )

        self.assertEqual(analysis.classification, DiffClassification.REBUILD_RECOMMENDED)


if __name__ == "__main__":
    unittest.main()
