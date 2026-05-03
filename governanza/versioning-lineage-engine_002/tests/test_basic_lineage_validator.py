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
    LineageIntegrityStatus,
    ObjectKind,
    PhaseId,
    RebuildabilityStatus,
    ReferenceKind,
    StaleState,
    VersionLifecycleStatus,
)
from versioning_lineage_engine.domain.records import (  # noqa: E402
    LineageIntegrityRecord,
    StaleStateRecord,
)
from versioning_lineage_engine.domain.value_objects import (  # noqa: E402
    ContentChecksum,
    DependencyEdgeId,
    DependencyRole,
    DependencySnapshotId,
    EngineName,
    EngineVersion,
    ExternalDependencyRef,
    Fingerprint,
    LineageIntegrityRecordId,
    LineageLocator,
    ObjectIdentityId,
    ObjectVersionId,
    ReferenceVersionRecordId,
    RebuildManifest,
    StableKey,
    StaleStateRecordId,
    VersionIndex,
)
from versioning_lineage_engine.validation import (  # noqa: E402
    BasicLineageIntegrityValidator,
    ValidationOutcome,
    ValidationContext,
)


def utc() -> datetime:
    return datetime(2026, 4, 9, 12, 0, tzinfo=timezone.utc)


def make_identity(
    *,
    suffix: str = "a",
    object_kind: object = ObjectKind.TENSION_MAP,
    phase_scope: object = PhaseId.PHASE_2,
    identity_status: object = IdentityStatus.ACTIVE,
) -> ObjectIdentity:
    return ObjectIdentity(
        object_identity_id=ObjectIdentityId(f"identity:{suffix}"),
        object_kind=object_kind,
        phase_scope=phase_scope,
        stable_key=StableKey(f"stable:{suffix}"),
        canonical_name=f"object-{suffix}",
        identity_status=identity_status,
        replacement_of_identity_id=None,
        replaced_by_identity_id=None,
        created_at=utc(),
    )


def make_reference(*, suffix: str = "contract", reference_kind: object = ReferenceKind.CONTRACT_VERSION) -> ReferenceVersionRecord:
    return ReferenceVersionRecord(
        reference_version_record_id=ReferenceVersionRecordId(f"ref:{suffix}"),
        reference_kind=reference_kind,
        reference_key=StableKey(f"ref-key:{suffix}"),
        reference_name=f"ref-{suffix}",
        version_label="v1",
        content_fingerprint=Fingerprint(f"fp-ref:{suffix}"),
        created_at=utc(),
    )


def make_manifest(
    *,
    target_version_id: ObjectVersionId,
    checksum: str,
    schema: str = "schema:v1",
    engine_name: str = "lineage-engine",
    engine_version: str = "0.1.0",
    required_dependency_refs: tuple[LineageLocator, ...] = (),
    contract_refs: tuple[ExternalDependencyRef, ...] = (),
    rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
) -> RebuildManifest:
    return RebuildManifest(
        target_object_version_id=target_version_id,
        required_dependency_refs=required_dependency_refs,
        contract_version_refs=contract_refs,
        taxonomy_version_refs=(),
        rule_pack_version_refs=(),
        library_version_refs=(),
        model_version_refs=(),
        producer_engine_name=EngineName(engine_name),
        producer_engine_version=EngineVersion(engine_version),
        schema_fingerprint=Fingerprint(schema),
        execution_fingerprint=Fingerprint(f"exec:{target_version_id}"),
        expected_content_checksum=ContentChecksum(checksum),
        rebuildability_status=rebuildability_status,
    )


def make_version(
    identity: ObjectIdentity,
    *,
    suffix: str = "a-v1",
    checksum: str = "checksum:a-v1",
    schema: str = "schema:v1",
    required_dependency_refs: tuple[LineageLocator, ...] = (),
    contract_refs: tuple[ExternalDependencyRef, ...] = (),
    rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
    producer_engine_name: str = "lineage-engine",
    producer_engine_version: str = "0.1.0",
) -> ObjectVersion:
    version_id = ObjectVersionId(f"version:{suffix}")
    manifest = make_manifest(
        target_version_id=version_id,
        checksum=checksum,
        schema=schema,
        required_dependency_refs=required_dependency_refs,
        contract_refs=contract_refs,
        rebuildability_status=rebuildability_status,
        engine_name=producer_engine_name,
        engine_version=producer_engine_version,
    )
    return ObjectVersion(
        object_version_id=version_id,
        object_identity_id=identity.object_identity_id,
        version_index=VersionIndex(1),
        content_checksum=ContentChecksum(checksum),
        schema_fingerprint=Fingerprint(schema),
        version_status=VersionLifecycleStatus.ACTIVE,
        created_at=utc(),
        producer_engine_name=EngineName(producer_engine_name),
        producer_engine_version=EngineVersion(producer_engine_version),
        rebuild_manifest=manifest,
    )


def make_edge(
    origin: ObjectVersion,
    target_locator: LineageLocator,
    *,
    suffix: str = "1",
    dependency_type: DependencyType = DependencyType.DERIVES_FROM,
    required: bool = True,
) -> DependencyEdge:
    return DependencyEdge(
        dependency_edge_id=DependencyEdgeId(f"edge:{suffix}"),
        from_object_version_id=origin.object_version_id,
        target_kind=target_locator.target_kind,
        target_ref=target_locator,
        dependency_type=dependency_type,
        required=required,
        contributes_to_rebuild=True,
        input_role=DependencyRole("input"),
        created_at=utc(),
    )


def make_snapshot(version: ObjectVersion, *edges: DependencyEdge, suffix: str = "1") -> DependencySnapshot:
    return DependencySnapshot(
        dependency_snapshot_id=DependencySnapshotId(f"snapshot:{suffix}"),
        object_version_id=version.object_version_id,
        dependency_edge_ids=tuple(edge.dependency_edge_id for edge in edges),
        snapshot_fingerprint=Fingerprint(f"snapshot-fp:{suffix}"),
        captured_at=utc(),
    )


class BasicLineageIntegrityValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicLineageIntegrityValidator(
            clock=lambda: datetime(2026, 4, 9, 16, 0, tzinfo=timezone.utc)
        )

    def test_valid_graph_passes(self) -> None:
        source_identity = make_identity(suffix="source", object_kind=ObjectKind.BENCHMARK_BUNDLE, phase_scope=PhaseId.PHASE_1)
        source_version = make_version(source_identity, suffix="source-v1")
        contract_ref = make_reference()
        main_identity = make_identity()
        contract_dependency = ExternalDependencyRef(
            reference_kind=ReferenceKind.CONTRACT_VERSION,
            reference_version_record_id=contract_ref.reference_version_record_id,
            reference_key=contract_ref.reference_key,
            version_label=contract_ref.version_label,
        )
        main_version = make_version(
            main_identity,
            required_dependency_refs=(source_version.reference, contract_ref.reference),
            contract_refs=(contract_dependency,),
        )
        edge = make_edge(main_version, source_version.reference)
        snapshot = make_snapshot(main_version, edge)

        report = self.validator.validate_graph(
            object_identities=(source_identity, main_identity),
            object_versions=(source_version, main_version),
            dependency_edges=(edge,),
            dependency_snapshots=(snapshot,),
            reference_versions=(contract_ref,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertFalse(report.violations)

    def test_identity_with_invalid_phase_scope_fails(self) -> None:
        identity = make_identity(phase_scope="bad-phase")

        report = self.validator.validate_object_identity(identity)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertEqual(report.violations[0].code, "identity.phase_scope_invalid")

    def test_object_version_without_known_identity_fails(self) -> None:
        identity = make_identity()
        version = make_version(identity)

        report = self.validator.validate_object_version(version, context=ValidationContext())

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(
            any(item.code == "version.identity_reference_invalid" for item in report.violations)
        )

    def test_dependency_edge_with_unresolved_target_fails(self) -> None:
        identity = make_identity()
        version = make_version(identity)
        missing_target = LineageLocator.for_object_version(ObjectVersionId("version:missing"))
        edge = make_edge(version, missing_target)

        report = self.validator.validate_graph(
            object_identities=(identity,),
            object_versions=(version,),
            dependency_edges=(edge,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "edge.target_unresolved" for item in report.violations))

    def test_dependency_snapshot_with_wrong_edge_origin_fails(self) -> None:
        source_identity = make_identity(suffix="source")
        source_version = make_version(source_identity, suffix="source-v1")
        main_identity = make_identity(suffix="main")
        main_version = make_version(main_identity, suffix="main-v1")
        wrong_origin_edge = make_edge(source_version, main_version.reference, suffix="bad-edge")
        snapshot = make_snapshot(main_version, wrong_origin_edge)

        report = self.validator.validate_graph(
            object_identities=(source_identity, main_identity),
            object_versions=(source_version, main_version),
            dependency_edges=(wrong_origin_edge,),
            dependency_snapshots=(snapshot,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(
            any(item.code == "snapshot.edge_origin_mismatch" for item in report.violations)
        )

    def test_reference_with_invalid_kind_fails(self) -> None:
        reference = make_reference(reference_kind="contract_version")

        report = self.validator.validate_reference_version_record(reference)

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(any(item.code == "reference.kind_invalid" for item in report.violations))

    def test_complete_lineage_with_missing_required_ref_fails(self) -> None:
        identity = make_identity()
        missing_ref = LineageLocator.for_object_version(ObjectVersionId("version:missing"))
        version = make_version(identity, required_dependency_refs=(missing_ref,))
        edge = make_edge(version, missing_ref, suffix="missing-edge")
        snapshot = make_snapshot(version, edge)
        record = LineageIntegrityRecord(
            lineage_integrity_record_id=LineageIntegrityRecordId("lineage:1"),
            object_version_id=version.object_version_id,
            integrity_status=LineageIntegrityStatus.COMPLETE,
            missing_required_refs=(),
            broken_dependency_edge_ids=(),
            details=(),
            checked_at=utc(),
        )

        report = self.validator.validate_graph(
            object_identities=(identity,),
            object_versions=(version,),
            dependency_edges=(edge,),
            dependency_snapshots=(snapshot,),
            lineage_integrity_records=(record,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(
            any(item.code == "lineage.complete_but_missing_required_ref" for item in report.violations)
        )

    def test_stale_record_with_resolved_trigger_warns(self) -> None:
        source_identity = make_identity(suffix="source")
        source_version = make_version(source_identity, suffix="source-v1")
        main_identity = make_identity(suffix="main")
        main_version = make_version(main_identity, suffix="main-v1")
        record = StaleStateRecord(
            stale_state_record_id=StaleStateRecordId("stale:1"),
            object_version_id=main_version.object_version_id,
            stale_state=StaleState.STALE_REBUILD_RECOMMENDED,
            reasons=("upstream source changed",),
            upstream_trigger_refs=(source_version.reference,),
            detected_at=utc(),
            cleared_at=None,
        )

        report = self.validator.validate_graph(
            object_identities=(source_identity, main_identity),
            object_versions=(source_version, main_version),
            stale_state_records=(record,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        self.assertTrue(any(item.code == "stale.declared" for item in report.violations))

    def test_rebuild_manifest_with_unresolved_reference_fails(self) -> None:
        identity = make_identity()
        missing_ref = LineageLocator.for_object_version(ObjectVersionId("version:missing"))
        version = make_version(identity, required_dependency_refs=(missing_ref,))

        report = self.validator.validate_graph(
            object_identities=(identity,),
            object_versions=(version,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertTrue(
            any(item.code == "rebuild.required_ref_unresolved" for item in report.violations)
        )

    def test_multiple_violations_accumulate_in_one_run(self) -> None:
        identity = make_identity(phase_scope="bad-phase")
        version = make_version(identity, required_dependency_refs=(LineageLocator.for_object_version(ObjectVersionId("version:missing")),))

        report = self.validator.validate_graph(
            object_identities=(identity,),
            object_versions=(version,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertGreaterEqual(len(report.violations), 2)


if __name__ == "__main__":
    unittest.main()
