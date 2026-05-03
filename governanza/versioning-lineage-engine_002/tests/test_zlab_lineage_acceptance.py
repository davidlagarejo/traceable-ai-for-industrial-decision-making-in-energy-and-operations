from __future__ import annotations

from datetime import datetime, timezone
import unittest

from versioning_lineage_engine.domain.entities import (  # noqa: E402
    DependencyEdge,
    DependencySnapshot,
    ObjectIdentity,
    ObjectVersion,
    ReferenceVersionRecord,
    VersionLineageNode,
)
from versioning_lineage_engine.domain.enums import (  # noqa: E402
    ComparabilityStatus,
    DependencyType,
    IdentityStatus,
    ObjectKind,
    PhaseId,
    RebuildabilityStatus,
    ReferenceKind,
    VersionLifecycleStatus,
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
    ObjectIdentityId,
    ObjectVersionId,
    ReferenceVersionRecordId,
    RebuildManifest,
    StableKey,
    VersionIndex,
    VersionLineageNodeId,
)
from versioning_lineage_engine.evolution import (  # noqa: E402
    BasicImpactAnalyzer,
    BasicVersionDiffer,
    ChangeTrigger,
    DiffClassification,
    LineageGraphIndex,
)
from versioning_lineage_engine.validation import (  # noqa: E402
    BasicLineageIntegrityValidator,
    ValidationOutcome,
)


def utc(hour: int = 12) -> datetime:
    return datetime(2026, 4, 9, hour, 0, tzinfo=timezone.utc)


def make_identity(
    *,
    suffix: str,
    object_kind: ObjectKind,
    phase_scope: PhaseId | None,
    identity_status: IdentityStatus = IdentityStatus.ACTIVE,
    replacement_of: ObjectIdentityId | None = None,
    replaced_by: ObjectIdentityId | None = None,
) -> ObjectIdentity:
    return ObjectIdentity(
        object_identity_id=ObjectIdentityId(f"identity:{suffix}"),
        object_kind=object_kind,
        phase_scope=phase_scope,
        stable_key=StableKey(f"stable:{suffix}"),
        canonical_name=suffix,
        identity_status=identity_status,
        replacement_of_identity_id=replacement_of,
        replaced_by_identity_id=replaced_by,
        created_at=utc(),
    )


def make_reference(
    *,
    suffix: str,
    reference_kind: ReferenceKind,
    version_label: str,
) -> ReferenceVersionRecord:
    return ReferenceVersionRecord(
        reference_version_record_id=ReferenceVersionRecordId(f"reference:{suffix}:{version_label}"),
        reference_kind=reference_kind,
        reference_key=StableKey(f"reference-key:{suffix}"),
        reference_name=f"{suffix}-reference",
        version_label=version_label,
        content_fingerprint=Fingerprint(f"reference-fingerprint:{suffix}:{version_label}"),
        created_at=utc(),
    )


def external_ref(record: ReferenceVersionRecord) -> ExternalDependencyRef:
    return ExternalDependencyRef(
        reference_kind=record.reference_kind,
        reference_version_record_id=record.reference_version_record_id,
        reference_key=record.reference_key,
        version_label=record.version_label,
    )


def make_manifest(
    *,
    target_object_version_id: ObjectVersionId,
    checksum: str,
    required_dependency_refs=(),
    contract_version_refs=(),
    taxonomy_version_refs=(),
    rule_pack_version_refs=(),
    rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
) -> RebuildManifest:
    return RebuildManifest(
        target_object_version_id=target_object_version_id,
        required_dependency_refs=tuple(required_dependency_refs),
        contract_version_refs=tuple(contract_version_refs),
        taxonomy_version_refs=tuple(taxonomy_version_refs),
        rule_pack_version_refs=tuple(rule_pack_version_refs),
        library_version_refs=(),
        model_version_refs=(),
        producer_engine_name=EngineName("lineage-engine"),
        producer_engine_version=EngineVersion("0.1.0"),
        schema_fingerprint=Fingerprint("schema:v1"),
        execution_fingerprint=Fingerprint(f"exec:{target_object_version_id}"),
        expected_content_checksum=ContentChecksum(checksum),
        rebuildability_status=rebuildability_status,
    )


def make_version(
    identity: ObjectIdentity,
    *,
    label: str,
    index: int,
    checksum: str,
    version_status: VersionLifecycleStatus = VersionLifecycleStatus.ACTIVE,
    required_dependency_refs=(),
    contract_version_refs=(),
    taxonomy_version_refs=(),
    rule_pack_version_refs=(),
    rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
) -> ObjectVersion:
    version_id = ObjectVersionId(f"version:{label}:v{index}")
    return ObjectVersion(
        object_version_id=version_id,
        object_identity_id=identity.object_identity_id,
        version_index=VersionIndex(index),
        content_checksum=ContentChecksum(checksum),
        schema_fingerprint=Fingerprint("schema:v1"),
        version_status=version_status,
        created_at=utc(),
        producer_engine_name=EngineName("lineage-engine"),
        producer_engine_version=EngineVersion("0.1.0"),
        rebuild_manifest=make_manifest(
            target_object_version_id=version_id,
            checksum=checksum,
            required_dependency_refs=required_dependency_refs,
            contract_version_refs=contract_version_refs,
            taxonomy_version_refs=taxonomy_version_refs,
            rule_pack_version_refs=rule_pack_version_refs,
            rebuildability_status=rebuildability_status,
        ),
    )


def make_edge(
    origin: ObjectVersion,
    target_ref,
    *,
    suffix: str,
    dependency_type: DependencyType = DependencyType.DERIVES_FROM,
    required: bool = True,
    input_role: str = "input",
) -> DependencyEdge:
    return DependencyEdge(
        dependency_edge_id=DependencyEdgeId(f"edge:{suffix}"),
        from_object_version_id=origin.object_version_id,
        target_kind=target_ref.target_kind,
        target_ref=target_ref,
        dependency_type=dependency_type,
        required=required,
        contributes_to_rebuild=True,
        input_role=DependencyRole(input_role),
        created_at=utc(),
    )


def make_snapshot(version: ObjectVersion, *edges: DependencyEdge, suffix: str) -> DependencySnapshot:
    return DependencySnapshot(
        dependency_snapshot_id=DependencySnapshotId(f"snapshot:{suffix}"),
        object_version_id=version.object_version_id,
        dependency_edge_ids=tuple(item.dependency_edge_id for item in edges),
        snapshot_fingerprint=Fingerprint(f"snapshot-fingerprint:{suffix}"),
        captured_at=utc(),
    )


def make_lineage_node(
    version: ObjectVersion,
    snapshot: DependencySnapshot,
    *,
    suffix: str,
    reference_versions: tuple[ReferenceVersionRecord, ...] = (),
    comparability_status: ComparabilityStatus = ComparabilityStatus.COMPARABLE,
    rebuildability_status: RebuildabilityStatus = RebuildabilityStatus.REBUILDABLE,
) -> VersionLineageNode:
    return VersionLineageNode(
        version_lineage_node_id=VersionLineageNodeId(f"node:{suffix}"),
        object_version_id=version.object_version_id,
        dependency_snapshot_id=snapshot.dependency_snapshot_id,
        upstream_object_version_ids=tuple(
            item.identifier for item in version.rebuild_manifest.required_dependency_refs if item.target_kind.value == "object_version"
        ),
        reference_version_ids=tuple(item.reference_version_record_id for item in reference_versions),
        comparability_status=comparability_status,
        rebuildability_status=rebuildability_status,
        created_at=utc(),
    )


class ZLabLineageAcceptanceTest(unittest.TestCase):
    def setUp(self) -> None:
        self.differ = BasicVersionDiffer(clock=lambda: utc(16))
        self.impact_analyzer = BasicImpactAnalyzer(clock=lambda: utc(17))
        self.validator = BasicLineageIntegrityValidator(clock=lambda: utc(18))

    def test_public_source_change_cascades_stale_across_phase_chain(self) -> None:
        source_identity = make_identity(
            suffix="public-source",
            object_kind=ObjectKind.SOURCE_VERSION,
            phase_scope=None,
        )
        benchmark_identity = make_identity(
            suffix="benchmark-bundle",
            object_kind=ObjectKind.BENCHMARK_BUNDLE,
            phase_scope=PhaseId.PHASE_1,
        )
        facility_prior_identity = make_identity(
            suffix="facility-prior",
            object_kind=ObjectKind.FACILITY_PRIOR,
            phase_scope=PhaseId.PHASE_1,
        )
        tension_map_identity = make_identity(
            suffix="tension-map",
            object_kind=ObjectKind.TENSION_MAP,
            phase_scope=PhaseId.PHASE_2,
        )
        output_block_identity = make_identity(
            suffix="output-block",
            object_kind=ObjectKind.OUTPUT_BLOCK,
            phase_scope=PhaseId.PHASE_3,
        )
        report_package_identity = make_identity(
            suffix="report-package",
            object_kind=ObjectKind.REPORT_PACKAGE,
            phase_scope=PhaseId.PHASE_3,
        )

        source_v1 = make_version(source_identity, label="public-source", index=1, checksum="checksum:source:v1")
        source_v2 = make_version(source_identity, label="public-source", index=2, checksum="checksum:source:v2")
        benchmark_v1 = make_version(
            benchmark_identity,
            label="benchmark-bundle",
            index=1,
            checksum="checksum:benchmark:v1",
            required_dependency_refs=(source_v1.reference,),
        )
        benchmark_v2 = make_version(
            benchmark_identity,
            label="benchmark-bundle",
            index=2,
            checksum="checksum:benchmark:v2",
            required_dependency_refs=(source_v2.reference,),
        )
        facility_prior_v1 = make_version(
            facility_prior_identity,
            label="facility-prior",
            index=1,
            checksum="checksum:prior:v1",
            required_dependency_refs=(benchmark_v1.reference,),
        )
        facility_prior_v2 = make_version(
            facility_prior_identity,
            label="facility-prior",
            index=2,
            checksum="checksum:prior:v2",
            required_dependency_refs=(benchmark_v2.reference,),
        )
        tension_map_v1 = make_version(
            tension_map_identity,
            label="tension-map",
            index=1,
            checksum="checksum:tension:v1",
            required_dependency_refs=(facility_prior_v1.reference,),
        )
        tension_map_v2 = make_version(
            tension_map_identity,
            label="tension-map",
            index=2,
            checksum="checksum:tension:v2",
            required_dependency_refs=(facility_prior_v2.reference,),
        )
        output_block_v1 = make_version(
            output_block_identity,
            label="output-block",
            index=1,
            checksum="checksum:block:v1",
            required_dependency_refs=(tension_map_v1.reference,),
        )
        output_block_v2 = make_version(
            output_block_identity,
            label="output-block",
            index=2,
            checksum="checksum:block:v2",
            required_dependency_refs=(tension_map_v2.reference,),
        )
        report_package_v1 = make_version(
            report_package_identity,
            label="report-package",
            index=1,
            checksum="checksum:report:v1",
            required_dependency_refs=(output_block_v1.reference,),
        )

        benchmark_edge = make_edge(benchmark_v1, source_v1.reference, suffix="source-to-benchmark")
        facility_prior_edge = make_edge(facility_prior_v1, benchmark_v1.reference, suffix="benchmark-to-prior")
        tension_map_edge = make_edge(tension_map_v1, facility_prior_v1.reference, suffix="prior-to-tension")
        output_block_edge = make_edge(output_block_v1, tension_map_v1.reference, suffix="tension-to-block")
        report_package_edge = make_edge(report_package_v1, output_block_v1.reference, suffix="block-to-report")

        source_change = self.differ.diff_versions(source_v1, source_v2)
        benchmark_impact = self.impact_analyzer.analyze_diff(
            source_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(source_v1, source_v2, benchmark_v1),
                dependency_edges=(benchmark_edge,),
            ),
        )
        benchmark_change = self.differ.diff_versions(benchmark_v1, benchmark_v2)
        facility_prior_impact = self.impact_analyzer.analyze_diff(
            benchmark_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(benchmark_v1, benchmark_v2, facility_prior_v1),
                dependency_edges=(facility_prior_edge,),
            ),
        )
        facility_prior_change = self.differ.diff_versions(facility_prior_v1, facility_prior_v2)
        tension_impact = self.impact_analyzer.analyze_diff(
            facility_prior_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(facility_prior_v1, facility_prior_v2, tension_map_v1),
                dependency_edges=(tension_map_edge,),
            ),
        )
        tension_change = self.differ.diff_versions(tension_map_v1, tension_map_v2)
        output_block_impact = self.impact_analyzer.analyze_diff(
            tension_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(tension_map_v1, tension_map_v2, output_block_v1),
                dependency_edges=(output_block_edge,),
            ),
        )
        output_block_change = self.differ.diff_versions(output_block_v1, output_block_v2)
        report_impact = self.impact_analyzer.analyze_diff(
            output_block_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(output_block_v1, output_block_v2, report_package_v1),
                dependency_edges=(report_package_edge,),
            ),
        )

        self.assertEqual(
            benchmark_impact.stale_state_records[0].object_version_id,
            benchmark_v1.object_version_id,
        )
        self.assertEqual(
            facility_prior_impact.stale_state_records[0].object_version_id,
            facility_prior_v1.object_version_id,
        )
        self.assertEqual(
            tension_impact.stale_state_records[0].object_version_id,
            tension_map_v1.object_version_id,
        )
        self.assertEqual(
            output_block_impact.stale_state_records[0].object_version_id,
            output_block_v1.object_version_id,
        )
        self.assertEqual(
            report_impact.stale_state_records[0].object_version_id,
            report_package_v1.object_version_id,
        )
        self.assertEqual(
            benchmark_v1.rebuild_manifest.required_dependency_refs,
            (source_v1.reference,),
        )
        self.assertEqual(
            report_package_v1.rebuild_manifest.required_dependency_refs,
            (output_block_v1.reference,),
        )

    def test_benchmark_correction_distinguishes_history_stale_and_new_version(self) -> None:
        benchmark_identity = make_identity(
            suffix="benchmark-bundle",
            object_kind=ObjectKind.BENCHMARK_BUNDLE,
            phase_scope=PhaseId.PHASE_1,
        )
        facility_prior_identity = make_identity(
            suffix="facility-prior",
            object_kind=ObjectKind.FACILITY_PRIOR,
            phase_scope=PhaseId.PHASE_1,
        )
        tension_map_identity = make_identity(
            suffix="tension-map",
            object_kind=ObjectKind.TENSION_MAP,
            phase_scope=PhaseId.PHASE_2,
        )

        benchmark_v1 = make_version(benchmark_identity, label="benchmark-bundle", index=1, checksum="checksum:benchmark:v1")
        benchmark_v2 = make_version(benchmark_identity, label="benchmark-bundle", index=2, checksum="checksum:benchmark:v2")
        facility_prior_v1 = make_version(
            facility_prior_identity,
            label="facility-prior",
            index=1,
            checksum="checksum:prior:v1",
            required_dependency_refs=(benchmark_v1.reference,),
        )
        facility_prior_v2 = make_version(
            facility_prior_identity,
            label="facility-prior",
            index=2,
            checksum="checksum:prior:v2",
            required_dependency_refs=(benchmark_v2.reference,),
        )
        tension_map_v1 = make_version(
            tension_map_identity,
            label="tension-map",
            index=1,
            checksum="checksum:tension:v1",
            required_dependency_refs=(facility_prior_v1.reference,),
        )

        facility_prior_edge = make_edge(facility_prior_v1, benchmark_v1.reference, suffix="benchmark-to-prior")
        tension_edge = make_edge(tension_map_v1, facility_prior_v1.reference, suffix="prior-to-tension")

        benchmark_change = self.differ.diff_versions(benchmark_v1, benchmark_v2)
        facility_prior_impact = self.impact_analyzer.analyze_diff(
            benchmark_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(benchmark_v1, benchmark_v2, facility_prior_v1),
                dependency_edges=(facility_prior_edge,),
            ),
        )
        facility_prior_change = self.differ.diff_versions(facility_prior_v1, facility_prior_v2)
        tension_impact = self.impact_analyzer.analyze_diff(
            facility_prior_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(facility_prior_v1, facility_prior_v2, tension_map_v1),
                dependency_edges=(tension_edge,),
            ),
        )

        self.assertEqual(benchmark_v1.object_identity_id, benchmark_v2.object_identity_id)
        self.assertNotEqual(benchmark_v1.object_version_id, benchmark_v2.object_version_id)
        self.assertEqual(
            facility_prior_impact.stale_state_records[0].object_version_id,
            facility_prior_v1.object_version_id,
        )
        self.assertEqual(
            tension_impact.stale_state_records[0].object_version_id,
            tension_map_v1.object_version_id,
        )

    def test_output_block_built_with_old_tension_map_is_marked_stale_with_explicit_reason(self) -> None:
        tension_map_identity = make_identity(
            suffix="tension-map",
            object_kind=ObjectKind.TENSION_MAP,
            phase_scope=PhaseId.PHASE_2,
        )
        output_block_identity = make_identity(
            suffix="output-block",
            object_kind=ObjectKind.OUTPUT_BLOCK,
            phase_scope=PhaseId.PHASE_3,
        )

        tension_map_v1 = make_version(tension_map_identity, label="tension-map", index=1, checksum="checksum:tension:v1")
        tension_map_v2 = make_version(tension_map_identity, label="tension-map", index=2, checksum="checksum:tension:v2")
        output_block_v1 = make_version(
            output_block_identity,
            label="output-block",
            index=1,
            checksum="checksum:block:v1",
            required_dependency_refs=(tension_map_v1.reference,),
        )
        output_block_v2 = make_version(
            output_block_identity,
            label="output-block",
            index=2,
            checksum="checksum:block:v2",
            required_dependency_refs=(tension_map_v2.reference,),
        )
        old_edge = make_edge(output_block_v1, tension_map_v1.reference, suffix="old-block")
        new_edge = make_edge(output_block_v2, tension_map_v2.reference, suffix="new-block")

        tension_change = self.differ.diff_versions(tension_map_v1, tension_map_v2)
        impact = self.impact_analyzer.analyze_diff(
            tension_change,
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(tension_map_v1, tension_map_v2, output_block_v1),
                dependency_edges=(old_edge,),
            ),
        )

        stale_record = impact.stale_state_records[0]
        self.assertEqual(stale_record.object_version_id, output_block_v1.object_version_id)
        self.assertTrue(any(str(tension_map_v1.object_version_id) in reason for reason in stale_record.reasons))
        self.assertEqual(old_edge.target_ref, tension_map_v1.reference)
        self.assertEqual(new_edge.target_ref, tension_map_v2.reference)

    def test_claim_upgrade_candidate_from_replaced_prior_preserves_history_and_surfaces_stale(self) -> None:
        new_prior_identity_id = ObjectIdentityId("identity:facility-prior-new")
        old_prior_identity = make_identity(
            suffix="facility-prior-old",
            object_kind=ObjectKind.FACILITY_PRIOR,
            phase_scope=PhaseId.PHASE_1,
            identity_status=IdentityStatus.REPLACED,
            replaced_by=new_prior_identity_id,
        )
        new_prior_identity = make_identity(
            suffix="facility-prior-new",
            object_kind=ObjectKind.FACILITY_PRIOR,
            phase_scope=PhaseId.PHASE_1,
            identity_status=IdentityStatus.REPLACEMENT,
            replacement_of=old_prior_identity.object_identity_id,
        )
        claim_identity = make_identity(
            suffix="claim-upgrade-register",
            object_kind=ObjectKind.CLAIM_UPGRADE_CANDIDATE_REGISTER,
            phase_scope=PhaseId.PHASE_4,
        )

        old_prior_v1 = make_version(old_prior_identity, label="facility-prior-old", index=1, checksum="checksum:prior-old:v1")
        new_prior_v1 = make_version(new_prior_identity, label="facility-prior-new", index=1, checksum="checksum:prior-new:v1")
        claim_v1 = make_version(
            claim_identity,
            label="claim-register",
            index=1,
            checksum="checksum:claim:v1",
            required_dependency_refs=(old_prior_v1.reference,),
        )
        claim_v2 = make_version(
            claim_identity,
            label="claim-register",
            index=2,
            checksum="checksum:claim:v2",
            required_dependency_refs=(new_prior_v1.reference,),
        )
        claim_edge_old = make_edge(claim_v1, old_prior_v1.reference, suffix="claim-old")
        claim_edge_new = make_edge(claim_v2, new_prior_v1.reference, suffix="claim-new")

        impact = self.impact_analyzer.analyze_trigger(
            ChangeTrigger(
                trigger_ref=old_prior_v1.reference,
                replacement_ref=new_prior_v1.reference,
                classification=DiffClassification.BREAKING_FOR_DOWNSTREAM,
                reasons=("facility_prior boundary changed and old prior was replaced.",),
            ),
            graph_index=LineageGraphIndex.from_iterables(
                object_versions=(old_prior_v1, new_prior_v1, claim_v1),
                dependency_edges=(claim_edge_old,),
            ),
        )

        self.assertEqual(old_prior_identity.identity_status, IdentityStatus.REPLACED)
        self.assertEqual(new_prior_identity.identity_status, IdentityStatus.REPLACEMENT)
        self.assertEqual(impact.stale_state_records[0].stale_state.value, "stale_blocked")
        self.assertEqual(claim_edge_old.target_ref, old_prior_v1.reference)
        self.assertEqual(claim_edge_new.target_ref, new_prior_v1.reference)

    def test_taxonomy_change_preserves_history_and_marks_comparability_conditionally(self) -> None:
        taxonomy_v1 = make_reference(
            suffix="taxonomy",
            reference_kind=ReferenceKind.TAXONOMY_VERSION,
            version_label="v1",
        )
        taxonomy_v2 = make_reference(
            suffix="taxonomy",
            reference_kind=ReferenceKind.TAXONOMY_VERSION,
            version_label="v2",
        )
        facility_prior_identity = make_identity(
            suffix="facility-prior",
            object_kind=ObjectKind.FACILITY_PRIOR,
            phase_scope=PhaseId.PHASE_1,
        )
        facility_prior_v1 = make_version(
            facility_prior_identity,
            label="facility-prior",
            index=1,
            checksum="checksum:prior:v1",
            taxonomy_version_refs=(external_ref(taxonomy_v1),),
            required_dependency_refs=(taxonomy_v1.reference,),
        )
        facility_prior_v2 = make_version(
            facility_prior_identity,
            label="facility-prior",
            index=2,
            checksum="checksum:prior:v2",
            taxonomy_version_refs=(external_ref(taxonomy_v2),),
            required_dependency_refs=(taxonomy_v2.reference,),
        )
        old_edge = make_edge(
            facility_prior_v1,
            taxonomy_v1.reference,
            suffix="taxonomy-old",
            dependency_type=DependencyType.USES_TAXONOMY,
        )
        new_edge = make_edge(
            facility_prior_v2,
            taxonomy_v2.reference,
            suffix="taxonomy-new",
            dependency_type=DependencyType.USES_TAXONOMY,
        )
        old_snapshot = make_snapshot(facility_prior_v1, old_edge, suffix="taxonomy-old")
        new_snapshot = make_snapshot(facility_prior_v2, new_edge, suffix="taxonomy-new")
        old_node = make_lineage_node(
            facility_prior_v1,
            old_snapshot,
            suffix="taxonomy-old",
            reference_versions=(taxonomy_v1,),
            comparability_status=ComparabilityStatus.COMPARABLE,
        )
        new_node = make_lineage_node(
            facility_prior_v2,
            new_snapshot,
            suffix="taxonomy-new",
            reference_versions=(taxonomy_v2,),
            comparability_status=ComparabilityStatus.CONDITIONALLY_COMPARABLE,
        )
        graph = LineageGraphIndex.from_iterables(
            object_versions=(facility_prior_v1, facility_prior_v2),
            dependency_edges=(old_edge, new_edge),
            dependency_snapshots=(old_snapshot, new_snapshot),
            reference_versions=(taxonomy_v1, taxonomy_v2),
        )

        change = self.differ.diff_versions(
            facility_prior_v1,
            facility_prior_v2,
            source_snapshot=old_snapshot,
            target_snapshot=new_snapshot,
            source_edges=(old_edge,),
            target_edges=(new_edge,),
        )

        self.assertEqual(change.classification, DiffClassification.REBUILD_REQUIRED)
        self.assertEqual(
            facility_prior_v1.rebuild_manifest.taxonomy_version_refs[0].reference_version_record_id,
            taxonomy_v1.reference_version_record_id,
        )
        self.assertEqual(
            facility_prior_v2.rebuild_manifest.taxonomy_version_refs[0].reference_version_record_id,
            taxonomy_v2.reference_version_record_id,
        )
        self.assertEqual(graph.downstream_edges_for_trigger(taxonomy_v1.reference), (old_edge,))
        self.assertEqual(graph.downstream_edges_for_trigger(taxonomy_v2.reference), (new_edge,))
        self.assertEqual(old_node.comparability_status, ComparabilityStatus.COMPARABLE)
        self.assertEqual(new_node.comparability_status, ComparabilityStatus.CONDITIONALLY_COMPARABLE)

    def test_old_report_package_is_minimally_reconstructible(self) -> None:
        contract_v1 = make_reference(
            suffix="phase-contract",
            reference_kind=ReferenceKind.CONTRACT_VERSION,
            version_label="v1",
        )
        output_block_identity = make_identity(
            suffix="output-block",
            object_kind=ObjectKind.OUTPUT_BLOCK,
            phase_scope=PhaseId.PHASE_3,
        )
        report_package_identity = make_identity(
            suffix="report-package",
            object_kind=ObjectKind.REPORT_PACKAGE,
            phase_scope=PhaseId.PHASE_3,
        )
        output_block_v1 = make_version(
            output_block_identity,
            label="output-block",
            index=1,
            checksum="checksum:block:v1",
        )
        report_package_v1 = make_version(
            report_package_identity,
            label="report-package",
            index=1,
            checksum="checksum:report:v1",
            required_dependency_refs=(output_block_v1.reference, contract_v1.reference),
            contract_version_refs=(external_ref(contract_v1),),
        )
        output_edge = make_edge(report_package_v1, output_block_v1.reference, suffix="report-to-output")
        contract_edge = make_edge(
            report_package_v1,
            contract_v1.reference,
            suffix="report-to-contract",
            dependency_type=DependencyType.USES_CONTRACT,
            input_role="contract",
        )
        report_snapshot = make_snapshot(report_package_v1, output_edge, contract_edge, suffix="report-v1")

        report = self.validator.validate_graph(
            object_identities=(output_block_identity, report_package_identity),
            object_versions=(output_block_v1, report_package_v1),
            dependency_edges=(output_edge, contract_edge),
            dependency_snapshots=(report_snapshot,),
            reference_versions=(contract_v1,),
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertTrue(report_package_v1.rebuild_manifest.is_rebuildable)
        self.assertEqual(report_snapshot.object_version_id, report_package_v1.object_version_id)
        self.assertEqual(
            report_package_v1.rebuild_manifest.required_dependency_refs,
            (output_block_v1.reference, contract_v1.reference),
        )


if __name__ == "__main__":
    unittest.main()
