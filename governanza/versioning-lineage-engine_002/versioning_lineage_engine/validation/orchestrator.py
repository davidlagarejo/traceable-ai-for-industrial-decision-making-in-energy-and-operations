from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from .._compat import dataclass
from ..domain.entities import (
    DependencyEdge,
    DependencySnapshot,
    ObjectIdentity,
    ObjectVersion,
    ReferenceVersionRecord,
    VersionLineageNode,
)
from ..domain.records import LineageIntegrityRecord, StaleStateRecord
from ..domain.value_objects import RebuildManifest
from .collector import ViolationCollector, ViolationDraft
from .context import ValidationContext
from .edge_validator import validate_dependency_edge
from .identity_validator import validate_object_identity
from .lineage_status_validator import validate_lineage_integrity_record
from .rebuild_validator import validate_rebuild_manifest
from .reference_validator import validate_reference_version_record
from .results import ValidationOutcome, ValidationReport, ValidationRun, ValidationViolation
from .snapshot_validator import validate_dependency_snapshot
from .stale_validator import validate_stale_state_record
from .version_validator import validate_object_version


DEFAULT_VALIDATOR_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    target_refs: tuple[str, ...]


class BasicLineageIntegrityValidator:
    def __init__(
        self,
        *,
        validator_version: str = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_object_identity(
        self,
        identity: ObjectIdentity,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_identity_ref(identity))
        validate_object_identity(identity, collector)
        return self._build_report(ValidationArtifacts((_identity_ref(identity),)), collector)

    def validate_object_version(
        self,
        version: ObjectVersion,
        *,
        context: ValidationContext | None = None,
        object_identity: ObjectIdentity | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_version_ref(version))
        validate_object_version(version, collector, context=context, object_identity=object_identity)
        return self._build_report(ValidationArtifacts((_version_ref(version),)), collector)

    def validate_dependency_edge(
        self,
        edge: DependencyEdge,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_edge_ref(edge))
        validate_dependency_edge(edge, collector, context=context)
        return self._build_report(ValidationArtifacts((_edge_ref(edge),)), collector)

    def validate_dependency_snapshot(
        self,
        snapshot: DependencySnapshot,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_snapshot_ref(snapshot))
        validate_dependency_snapshot(snapshot, collector, context=context)
        return self._build_report(ValidationArtifacts((_snapshot_ref(snapshot),)), collector)

    def validate_reference_version_record(
        self,
        reference: ReferenceVersionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_reference_ref(reference))
        validate_reference_version_record(reference, collector)
        return self._build_report(ValidationArtifacts((_reference_ref(reference),)), collector)

    def validate_lineage_integrity_record(
        self,
        record: LineageIntegrityRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_lineage_record_ref(record))
        validate_lineage_integrity_record(record, collector, context=context)
        return self._build_report(ValidationArtifacts((_lineage_record_ref(record),)), collector)

    def validate_stale_state_record(
        self,
        record: StaleStateRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_stale_record_ref(record))
        validate_stale_state_record(record, collector, context=context)
        return self._build_report(ValidationArtifacts((_stale_record_ref(record),)), collector)

    def validate_rebuild_manifest(
        self,
        manifest: RebuildManifest,
        *,
        context: ValidationContext | None = None,
        object_version: ObjectVersion | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_rebuild_manifest_ref(manifest))
        validate_rebuild_manifest(manifest, collector, context=context, object_version=object_version)
        return self._build_report(ValidationArtifacts((_rebuild_manifest_ref(manifest),)), collector)

    def validate_graph(
        self,
        *,
        object_identities: Iterable[ObjectIdentity] = (),
        object_versions: Iterable[ObjectVersion] = (),
        dependency_edges: Iterable[DependencyEdge] = (),
        dependency_snapshots: Iterable[DependencySnapshot] = (),
        reference_versions: Iterable[ReferenceVersionRecord] = (),
        lineage_integrity_records: Iterable[LineageIntegrityRecord] = (),
        stale_state_records: Iterable[StaleStateRecord] = (),
        version_lineage_nodes: Iterable[VersionLineageNode] = (),
    ) -> ValidationReport:
        object_identities = tuple(object_identities)
        object_versions = tuple(object_versions)
        dependency_edges = tuple(dependency_edges)
        dependency_snapshots = tuple(dependency_snapshots)
        reference_versions = tuple(reference_versions)
        lineage_integrity_records = tuple(lineage_integrity_records)
        stale_state_records = tuple(stale_state_records)
        version_lineage_nodes = tuple(version_lineage_nodes)

        context = ValidationContext.from_iterables(
            object_identities=object_identities,
            object_versions=object_versions,
            dependency_edges=dependency_edges,
            dependency_snapshots=dependency_snapshots,
            reference_versions=reference_versions,
            version_lineage_nodes=version_lineage_nodes,
        )
        collector = ViolationCollector("graph:lineage")

        identities_by_id = context.identities_by_id
        for item in object_identities:
            local = ViolationCollector(_identity_ref(item))
            validate_object_identity(item, local)
            _merge_collector(collector, local)

        for item in reference_versions:
            local = ViolationCollector(_reference_ref(item))
            validate_reference_version_record(item, local)
            _merge_collector(collector, local)

        for item in object_versions:
            local = ViolationCollector(_version_ref(item))
            identity = identities_by_id.get(item.object_identity_id)
            validate_object_version(item, local, context=context, object_identity=identity)
            _merge_collector(collector, local)

        for item in dependency_edges:
            local = ViolationCollector(_edge_ref(item))
            validate_dependency_edge(item, local, context=context)
            _merge_collector(collector, local)

        for item in dependency_snapshots:
            local = ViolationCollector(_snapshot_ref(item))
            validate_dependency_snapshot(item, local, context=context)
            _merge_collector(collector, local)

        for item in lineage_integrity_records:
            local = ViolationCollector(_lineage_record_ref(item))
            validate_lineage_integrity_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in stale_state_records:
            local = ViolationCollector(_stale_record_ref(item))
            validate_stale_state_record(item, local, context=context)
            _merge_collector(collector, local)

        target_refs = tuple(
            _unique_ordered(
                [
                    *(_identity_ref(item) for item in object_identities),
                    *(_version_ref(item) for item in object_versions),
                    *(_edge_ref(item) for item in dependency_edges),
                    *(_snapshot_ref(item) for item in dependency_snapshots),
                    *(_reference_ref(item) for item in reference_versions),
                    *(_lineage_record_ref(item) for item in lineage_integrity_records),
                    *(_stale_record_ref(item) for item in stale_state_records),
                ]
            )
        ) or ("graph:lineage",)

        return self._build_report(ValidationArtifacts(target_refs), collector)

    def _build_report(
        self,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        run_id = _stable_id(
            "lineage_validation",
            self._validator_version,
            outcome.value,
            *artifacts.target_refs,
            *(_draft_signature(item) for item in collector.violations),
        )
        violations = tuple(
            ValidationViolation(
                violation_id=_stable_id(
                    "lineage_violation",
                    run_id,
                    str(index),
                    draft.code.value,
                    draft.target_ref,
                    draft.field_ref or "nofield",
                ),
                code=draft.code.value,
                severity=draft.severity,
                message=draft.message,
                target_ref=draft.target_ref,
                field_ref=draft.field_ref,
                blocking=draft.blocking,
            )
            for index, draft in enumerate(collector.violations, start=1)
        )
        return ValidationReport(
            outcome=outcome,
            validation_run=ValidationRun(
                run_id=run_id,
                validator_version=self._validator_version,
                executed_at=self._clock(),
                target_refs=artifacts.target_refs,
            ),
            violations=violations,
        )


def _merge_collector(target: ViolationCollector, source: ViolationCollector) -> None:
    for item in source.violations:
        target.add(
            item.code,
            item.message,
            target_ref=item.target_ref,
            field_ref=item.field_ref,
            severity=item.severity,
            blocking=item.blocking,
        )


def _derive_outcome(collector: ViolationCollector) -> ValidationOutcome:
    if collector.has_errors:
        return ValidationOutcome.FAIL
    if collector.has_warnings:
        return ValidationOutcome.PASS_WITH_WARNINGS
    return ValidationOutcome.PASS


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _draft_signature(item: ViolationDraft) -> str:
    return "|".join(
        (
            item.code.value,
            item.severity.value,
            item.message,
            item.target_ref,
            item.field_ref or "nofield",
            "blocking" if item.blocking else "nonblocking",
        )
    )


def _identity_ref(identity: ObjectIdentity) -> str:
    return f"object_identity:{identity.object_identity_id}"


def _version_ref(version: ObjectVersion) -> str:
    return f"object_version:{version.object_version_id}"


def _edge_ref(edge: DependencyEdge) -> str:
    return f"dependency_edge:{edge.dependency_edge_id}"


def _snapshot_ref(snapshot: DependencySnapshot) -> str:
    return f"dependency_snapshot:{snapshot.dependency_snapshot_id}"


def _reference_ref(reference: ReferenceVersionRecord) -> str:
    return f"reference_version:{reference.reference_version_record_id}"


def _lineage_record_ref(record: LineageIntegrityRecord) -> str:
    return f"lineage_integrity:{record.lineage_integrity_record_id}"


def _stale_record_ref(record: StaleStateRecord) -> str:
    return f"stale_state:{record.stale_state_record_id}"


def _rebuild_manifest_ref(manifest: RebuildManifest) -> str:
    return f"rebuild_manifest:{manifest.target_object_version_id}"


def _unique_ordered(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        ordered.append(value)
        seen.add(value)
    return ordered
