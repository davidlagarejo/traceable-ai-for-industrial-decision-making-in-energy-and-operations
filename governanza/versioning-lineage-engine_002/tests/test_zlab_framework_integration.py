from __future__ import annotations

from datetime import datetime, timezone
import unittest

from versioning_lineage_engine.domain.enums import (
    ComparabilityStatus,
    IdentityStatus,
    StaleState,
)
from versioning_lineage_engine.evolution import (
    BasicImpactAnalyzer,
    BasicVersionDiffer,
    ChangeTrigger,
    DiffClassification,
)
from versioning_lineage_engine.integration.zlab import (
    BenchmarkBundle,
    ClaimUpgradeCandidateRegister,
    ContractVersion,
    FacilityPrior,
    IntegratedLineageGraph,
    OutputBlock,
    ReportPackage,
    RulePackVersion,
    SourceRecord,
    SourceVersion,
    TaxonomyVersion,
    TensionMap,
    ZLabLineageIntegrator,
)
from versioning_lineage_engine.validation import BasicLineageIntegrityValidator, ValidationOutcome


def utc(hour: int = 12) -> datetime:
    return datetime(2026, 4, 9, hour, 0, tzinfo=timezone.utc)


class ZLabFrameworkIntegrationTest(unittest.TestCase):
    def setUp(self) -> None:
        self.integrator = ZLabLineageIntegrator(clock=lambda: utc(12))
        self.differ = BasicVersionDiffer(clock=lambda: utc(13))
        self.impact_analyzer = BasicImpactAnalyzer(clock=lambda: utc(14))
        self.validator = BasicLineageIntegrityValidator(clock=lambda: utc(15))

    def test_source_to_report_chain_marks_real_objects_stale_without_mutating_history(self) -> None:
        source_record = SourceRecord(
            source_key="public-energy-benchmark",
            canonical_name="Public Energy Benchmark Source",
            publisher="City Open Data",
        )
        source_identity = self.integrator.integrate_source_record(source_record)
        contract_v1 = self.integrator.integrate_contract_version(
            ContractVersion(
                contract_key="phase-contract-registry",
                canonical_name="Phase Contract Registry",
                version_label="1.0.0",
                content_fingerprint="fingerprint:contract:1.0.0",
            )
        )
        taxonomy_v1 = self.integrator.integrate_taxonomy_version(
            TaxonomyVersion(
                taxonomy_key="building-taxonomy",
                canonical_name="Building Taxonomy",
                version_label="2026.01",
                content_fingerprint="fingerprint:taxonomy:2026.01",
            )
        )
        rule_pack_v1 = self.integrator.integrate_rule_pack_version(
            RulePackVersion(
                rule_pack_key="benchmark-rules",
                canonical_name="Benchmark Rules",
                version_label="2026.01",
                content_fingerprint="fingerprint:rule-pack:2026.01",
            )
        )

        source_v1 = self.integrator.integrate_source_version(
            source_record,
            SourceVersion(
                source_key=source_record.source_key,
                version_index=1,
                version_label="2026.01",
                content_checksum="checksum:source:v1",
            ),
            source_identity=source_identity,
        )
        source_v2 = self.integrator.integrate_source_version(
            source_record,
            SourceVersion(
                source_key=source_record.source_key,
                version_index=2,
                version_label="2026.02",
                content_checksum="checksum:source:v2",
            ),
            source_identity=source_identity,
        )

        benchmark_v1 = self.integrator.integrate_benchmark_bundle(
            BenchmarkBundle(
                bundle_key="benchmark-bundle:site-001",
                canonical_name="Benchmark Bundle Site 001",
                version_index=1,
                content_checksum="checksum:benchmark:v1",
            ),
            depends_on=(source_v1,),
            taxonomy_versions=(taxonomy_v1,),
            rule_pack_versions=(rule_pack_v1,),
        )
        benchmark_v2 = self.integrator.integrate_benchmark_bundle(
            BenchmarkBundle(
                bundle_key="benchmark-bundle:site-001",
                canonical_name="Benchmark Bundle Site 001",
                version_index=2,
                content_checksum="checksum:benchmark:v2",
            ),
            depends_on=(source_v2,),
            taxonomy_versions=(taxonomy_v1,),
            rule_pack_versions=(rule_pack_v1,),
        )
        prior_v1 = self.integrator.integrate_facility_prior(
            FacilityPrior(
                prior_key="facility-prior:site-001",
                canonical_name="Facility Prior Site 001",
                version_index=1,
                content_checksum="checksum:prior:v1",
            ),
            depends_on=(benchmark_v1,),
            contract_versions=(contract_v1,),
        )
        prior_v2 = self.integrator.integrate_facility_prior(
            FacilityPrior(
                prior_key="facility-prior:site-001",
                canonical_name="Facility Prior Site 001",
                version_index=2,
                content_checksum="checksum:prior:v2",
            ),
            depends_on=(benchmark_v2,),
            contract_versions=(contract_v1,),
        )
        tension_v1 = self.integrator.integrate_tension_map(
            TensionMap(
                tension_map_key="tension-map:site-001",
                canonical_name="Tension Map Site 001",
                version_index=1,
                content_checksum="checksum:tension:v1",
            ),
            depends_on=(prior_v1,),
            taxonomy_versions=(taxonomy_v1,),
        )
        tension_v2 = self.integrator.integrate_tension_map(
            TensionMap(
                tension_map_key="tension-map:site-001",
                canonical_name="Tension Map Site 001",
                version_index=2,
                content_checksum="checksum:tension:v2",
            ),
            depends_on=(prior_v2,),
            taxonomy_versions=(taxonomy_v1,),
        )
        block_v1 = self.integrator.integrate_output_block(
            OutputBlock(
                block_key="output-block:site-001:ops",
                canonical_name="Ops Output Block",
                version_index=1,
                content_checksum="checksum:block:v1",
            ),
            depends_on=(tension_v1,),
        )
        block_v2 = self.integrator.integrate_output_block(
            OutputBlock(
                block_key="output-block:site-001:ops",
                canonical_name="Ops Output Block",
                version_index=2,
                content_checksum="checksum:block:v2",
            ),
            depends_on=(tension_v2,),
        )
        report_v1 = self.integrator.integrate_report_package(
            ReportPackage(
                package_key="report-package:site-001",
                canonical_name="Report Package Site 001",
                version_index=1,
                content_checksum="checksum:report:v1",
            ),
            depends_on=(block_v1,),
            contract_versions=(contract_v1,),
            taxonomy_versions=(taxonomy_v1,),
            rule_pack_versions=(rule_pack_v1,),
        )

        source_change = self.differ.diff_versions(source_v1.version, source_v2.version)
        benchmark_impact = self.impact_analyzer.analyze_diff(
            source_change,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(source_v1, source_v2, benchmark_v1),
                identities=(source_identity,),
                references=(taxonomy_v1, rule_pack_v1),
            ).graph_index(),
        )

        benchmark_change = self.differ.diff_versions(
            benchmark_v1.version,
            benchmark_v2.version,
            source_snapshot=benchmark_v1.dependency_snapshot,
            target_snapshot=benchmark_v2.dependency_snapshot,
            source_edges=benchmark_v1.dependency_edges,
            target_edges=benchmark_v2.dependency_edges,
        )
        prior_impact = self.impact_analyzer.analyze_diff(
            benchmark_change,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(benchmark_v1, benchmark_v2, prior_v1),
                references=(contract_v1, taxonomy_v1, rule_pack_v1),
            ).graph_index(),
        )

        prior_change = self.differ.diff_versions(
            prior_v1.version,
            prior_v2.version,
            source_snapshot=prior_v1.dependency_snapshot,
            target_snapshot=prior_v2.dependency_snapshot,
            source_edges=prior_v1.dependency_edges,
            target_edges=prior_v2.dependency_edges,
        )
        tension_impact = self.impact_analyzer.analyze_diff(
            prior_change,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(prior_v1, prior_v2, tension_v1),
                references=(contract_v1,),
            ).graph_index(),
        )

        tension_change = self.differ.diff_versions(
            tension_v1.version,
            tension_v2.version,
            source_snapshot=tension_v1.dependency_snapshot,
            target_snapshot=tension_v2.dependency_snapshot,
            source_edges=tension_v1.dependency_edges,
            target_edges=tension_v2.dependency_edges,
        )
        block_impact = self.impact_analyzer.analyze_diff(
            tension_change,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(tension_v1, tension_v2, block_v1),
                references=(taxonomy_v1,),
            ).graph_index(),
        )

        block_change = self.differ.diff_versions(
            block_v1.version,
            block_v2.version,
            source_snapshot=block_v1.dependency_snapshot,
            target_snapshot=block_v2.dependency_snapshot,
            source_edges=block_v1.dependency_edges,
            target_edges=block_v2.dependency_edges,
        )
        report_impact = self.impact_analyzer.analyze_diff(
            block_change,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(block_v1, block_v2, report_v1),
                references=(contract_v1, taxonomy_v1, rule_pack_v1),
            ).graph_index(),
        )

        self.assertEqual(source_v1.identity.object_identity_id, source_v2.identity.object_identity_id)
        self.assertEqual(benchmark_impact.stale_state_records[0].object_version_id, benchmark_v1.version.object_version_id)
        self.assertEqual(prior_impact.stale_state_records[0].object_version_id, prior_v1.version.object_version_id)
        self.assertEqual(tension_impact.stale_state_records[0].object_version_id, tension_v1.version.object_version_id)
        self.assertEqual(block_impact.stale_state_records[0].object_version_id, block_v1.version.object_version_id)
        self.assertEqual(report_impact.stale_state_records[0].object_version_id, report_v1.version.object_version_id)
        self.assertEqual(benchmark_v1.version.rebuild_manifest.required_dependency_refs, (source_v1.reference,))
        self.assertEqual(report_v1.version.rebuild_manifest.required_dependency_refs, (block_v1.reference,))

    def test_replaced_facility_prior_marks_claim_register_stale_without_collapsing_history(self) -> None:
        replacement_prior = self.integrator.integrate_facility_prior(
            FacilityPrior(
                prior_key="facility-prior:site-001:replacement",
                canonical_name="Replacement Facility Prior",
                version_index=1,
                content_checksum="checksum:new-prior:v1",
            )
        )
        old_prior_replaced = self.integrator.integrate_facility_prior(
            FacilityPrior(
                prior_key="facility-prior:site-001:legacy",
                canonical_name="Legacy Facility Prior",
                version_index=1,
                content_checksum="checksum:legacy-prior:v1",
            ),
            identity_status=IdentityStatus.REPLACED,
            replaced_by_identity=replacement_prior.identity,
        )
        claim_v1 = self.integrator.integrate_claim_upgrade_candidate_register(
            ClaimUpgradeCandidateRegister(
                register_key="claim-upgrade-candidate:site-001",
                canonical_name="Claim Upgrade Candidate Register",
                version_index=1,
                content_checksum="checksum:claim:v1",
            ),
            depends_on=(old_prior_replaced,),
        )
        claim_v2 = self.integrator.integrate_claim_upgrade_candidate_register(
            ClaimUpgradeCandidateRegister(
                register_key="claim-upgrade-candidate:site-001",
                canonical_name="Claim Upgrade Candidate Register",
                version_index=2,
                content_checksum="checksum:claim:v2",
            ),
            depends_on=(replacement_prior,),
        )

        replacement_trigger = ChangeTrigger(
            trigger_ref=old_prior_replaced.reference,
            replacement_ref=replacement_prior.reference,
            classification=DiffClassification.BREAKING_FOR_DOWNSTREAM,
            reasons=("facility_prior was replaced by a successor identity.",),
        )
        impact = self.impact_analyzer.analyze_trigger(
            replacement_trigger,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(old_prior_replaced, replacement_prior, claim_v1),
            ).graph_index(),
        )

        stale_record = impact.stale_state_records[0]
        self.assertEqual(old_prior_replaced.identity.replaced_by_identity_id, replacement_prior.identity.object_identity_id)
        self.assertEqual(stale_record.object_version_id, claim_v1.version.object_version_id)
        self.assertEqual(stale_record.stale_state, StaleState.STALE_BLOCKED)
        self.assertEqual(claim_v1.version.rebuild_manifest.required_dependency_refs, (old_prior_replaced.reference,))
        self.assertEqual(claim_v2.version.rebuild_manifest.required_dependency_refs, (replacement_prior.reference,))
        self.assertEqual(claim_v1.version.object_identity_id, claim_v2.version.object_identity_id)
        self.assertNotEqual(claim_v1.version.object_version_id, claim_v2.version.object_version_id)

    def test_taxonomy_change_preserves_historical_version_and_marks_downstream_impact(self) -> None:
        taxonomy_v1 = self.integrator.integrate_taxonomy_version(
            TaxonomyVersion(
                taxonomy_key="facility-taxonomy",
                canonical_name="Facility Taxonomy",
                version_label="2026.01",
                content_fingerprint="fingerprint:taxonomy:2026.01",
            )
        )
        taxonomy_v2 = self.integrator.integrate_taxonomy_version(
            TaxonomyVersion(
                taxonomy_key="facility-taxonomy",
                canonical_name="Facility Taxonomy",
                version_label="2026.02",
                content_fingerprint="fingerprint:taxonomy:2026.02",
            )
        )
        prior_v1 = self.integrator.integrate_facility_prior(
            FacilityPrior(
                prior_key="facility-prior:site-002",
                canonical_name="Facility Prior Site 002",
                version_index=1,
                content_checksum="checksum:prior-002:v1",
            )
        )
        tension_v1 = self.integrator.integrate_tension_map(
            TensionMap(
                tension_map_key="tension-map:site-002",
                canonical_name="Tension Map Site 002",
                version_index=1,
                content_checksum="checksum:tension-002:v1",
            ),
            depends_on=(prior_v1,),
            taxonomy_versions=(taxonomy_v1,),
            comparability_status=ComparabilityStatus.COMPARABLE,
        )
        tension_v2 = self.integrator.integrate_tension_map(
            TensionMap(
                tension_map_key="tension-map:site-002",
                canonical_name="Tension Map Site 002",
                version_index=2,
                content_checksum="checksum:tension-002:v2",
            ),
            depends_on=(prior_v1,),
            taxonomy_versions=(taxonomy_v2,),
            comparability_status=ComparabilityStatus.CONDITIONALLY_COMPARABLE,
        )
        block_v1 = self.integrator.integrate_output_block(
            OutputBlock(
                block_key="output-block:site-002:ops",
                canonical_name="Ops Output Block Site 002",
                version_index=1,
                content_checksum="checksum:block-002:v1",
            ),
            depends_on=(tension_v1,),
        )

        diff = self.differ.diff_versions(
            tension_v1.version,
            tension_v2.version,
            source_snapshot=tension_v1.dependency_snapshot,
            target_snapshot=tension_v2.dependency_snapshot,
            source_edges=tension_v1.dependency_edges,
            target_edges=tension_v2.dependency_edges,
        )
        impact = self.impact_analyzer.analyze_diff(
            diff,
            graph_index=IntegratedLineageGraph.from_parts(
                objects=(tension_v1, tension_v2, block_v1),
                references=(taxonomy_v1, taxonomy_v2),
            ).graph_index(),
        )

        self.assertEqual(diff.classification, DiffClassification.REBUILD_REQUIRED)
        self.assertEqual(tension_v1.lineage_node.comparability_status, ComparabilityStatus.COMPARABLE)
        self.assertEqual(
            tension_v2.lineage_node.comparability_status,
            ComparabilityStatus.CONDITIONALLY_COMPARABLE,
        )
        self.assertEqual(
            tension_v1.version.rebuild_manifest.taxonomy_version_refs,
            (taxonomy_v1.external_dependency_ref,),
        )
        self.assertEqual(
            tension_v2.version.rebuild_manifest.taxonomy_version_refs,
            (taxonomy_v2.external_dependency_ref,),
        )
        self.assertEqual(impact.stale_state_records[0].stale_state, StaleState.STALE_MIGRATION_REQUIRED)
        self.assertEqual(impact.stale_state_records[0].object_version_id, block_v1.version.object_version_id)

    def test_historical_report_package_remains_minimally_reconstructible(self) -> None:
        source_record = SourceRecord(
            source_key="public-energy-benchmark",
            canonical_name="Public Energy Benchmark Source",
            publisher="City Open Data",
        )
        source_identity = self.integrator.integrate_source_record(source_record)
        contract_v1 = self.integrator.integrate_contract_version(
            ContractVersion(
                contract_key="phase-contract-registry",
                canonical_name="Phase Contract Registry",
                version_label="1.0.0",
                content_fingerprint="fingerprint:contract:1.0.0",
            )
        )
        taxonomy_v1 = self.integrator.integrate_taxonomy_version(
            TaxonomyVersion(
                taxonomy_key="building-taxonomy",
                canonical_name="Building Taxonomy",
                version_label="2026.01",
                content_fingerprint="fingerprint:taxonomy:2026.01",
            )
        )
        rule_pack_v1 = self.integrator.integrate_rule_pack_version(
            RulePackVersion(
                rule_pack_key="benchmark-rules",
                canonical_name="Benchmark Rules",
                version_label="2026.01",
                content_fingerprint="fingerprint:rule-pack:2026.01",
            )
        )

        source_v1 = self.integrator.integrate_source_version(
            source_record,
            SourceVersion(
                source_key=source_record.source_key,
                version_index=1,
                version_label="2026.01",
                content_checksum="checksum:source:v1",
            ),
            source_identity=source_identity,
        )
        benchmark_v1 = self.integrator.integrate_benchmark_bundle(
            BenchmarkBundle(
                bundle_key="benchmark-bundle:site-003",
                canonical_name="Benchmark Bundle Site 003",
                version_index=1,
                content_checksum="checksum:benchmark-003:v1",
            ),
            depends_on=(source_v1,),
            taxonomy_versions=(taxonomy_v1,),
            rule_pack_versions=(rule_pack_v1,),
        )
        prior_v1 = self.integrator.integrate_facility_prior(
            FacilityPrior(
                prior_key="facility-prior:site-003",
                canonical_name="Facility Prior Site 003",
                version_index=1,
                content_checksum="checksum:prior-003:v1",
            ),
            depends_on=(benchmark_v1,),
            contract_versions=(contract_v1,),
        )
        tension_v1 = self.integrator.integrate_tension_map(
            TensionMap(
                tension_map_key="tension-map:site-003",
                canonical_name="Tension Map Site 003",
                version_index=1,
                content_checksum="checksum:tension-003:v1",
            ),
            depends_on=(prior_v1,),
            taxonomy_versions=(taxonomy_v1,),
        )
        block_v1 = self.integrator.integrate_output_block(
            OutputBlock(
                block_key="output-block:site-003:ops",
                canonical_name="Ops Output Block Site 003",
                version_index=1,
                content_checksum="checksum:block-003:v1",
            ),
            depends_on=(tension_v1,),
        )
        report_v1 = self.integrator.integrate_report_package(
            ReportPackage(
                package_key="report-package:site-003",
                canonical_name="Report Package Site 003",
                version_index=1,
                content_checksum="checksum:report-003:v1",
            ),
            depends_on=(block_v1,),
            contract_versions=(contract_v1,),
            taxonomy_versions=(taxonomy_v1,),
            rule_pack_versions=(rule_pack_v1,),
        )

        graph = IntegratedLineageGraph.from_parts(
            identities=(source_identity,),
            objects=(source_v1, benchmark_v1, prior_v1, tension_v1, block_v1, report_v1),
            references=(contract_v1, taxonomy_v1, rule_pack_v1),
        )
        report = self.validator.validate_graph(
            object_identities=graph.object_identities,
            object_versions=graph.object_versions,
            dependency_edges=graph.dependency_edges,
            dependency_snapshots=graph.dependency_snapshots,
            reference_versions=graph.reference_versions,
            version_lineage_nodes=graph.version_lineage_nodes,
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertTrue(report_v1.version.rebuild_manifest.is_rebuildable)
        self.assertEqual(report_v1.version.rebuild_manifest.required_dependency_refs, (block_v1.reference,))
        self.assertEqual(
            report_v1.version.rebuild_manifest.contract_version_refs,
            (contract_v1.external_dependency_ref,),
        )
        self.assertEqual(
            report_v1.version.rebuild_manifest.taxonomy_version_refs,
            (taxonomy_v1.external_dependency_ref,),
        )
        self.assertEqual(
            report_v1.version.rebuild_manifest.rule_pack_version_refs,
            (rule_pack_v1.external_dependency_ref,),
        )


if __name__ == "__main__":
    unittest.main()
