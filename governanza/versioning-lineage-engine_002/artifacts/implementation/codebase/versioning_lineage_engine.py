"""Deterministic version and lineage registry for motor_002.

The engine records append-only object versions, explicit lineage nodes, and
directed impact edges. It does not decide object validity, phase approval,
truth, quality, source freshness, or operational re-evaluation.
"""

from __future__ import annotations

from collections import deque
from dataclasses import asdict, dataclass, field
import hashlib
import json
import re
from typing import Any, Iterable, Mapping, Sequence


PRODUCED_BY_MOTOR = "motor_002"
DEFAULT_CREATED_AT = "1970-01-01T00:00:00Z"

MUTATION_TYPES = {"create", "update", "supersede", "withdraw", "restore"}
NODE_TYPES = {"object_version", "source_reference", "transformation", "phase_contract"}
EDGE_TYPES = {
    "depends_on",
    "derived_from",
    "supersedes",
    "invalidates",
    "uses_source",
    "produced_by",
    "governed_by_phase_contract",
}
NON_CAUSAL_EDGE_TYPES = {"governed_by_phase_contract"}
PRIOR_REQUIRED_MUTATIONS = {"update", "supersede", "withdraw", "restore"}


@dataclass(frozen=True)
class VersionRecord:
    version_id: str
    record_id: str
    object_id: str
    object_type: str
    object_ref: str
    mutation_type: str
    phase_contract_ref: str
    parent_id: str | None
    prior_version_ref: str | None
    source_ref: str
    provenance_refs: list[str]
    transformation_refs: list[str]
    dependency_version_refs: list[str]
    produced_by_motor: str
    produced_at: str
    created_at: str
    updated_at: str
    version_hash: str
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineageNode:
    lineage_node_id: str
    node_type: str
    ref_id: str
    version_ref: str | None
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ImpactEdge:
    impact_edge_id: str
    source_node_id: str
    target_node_id: str
    edge_type: str
    evidence_ref: str
    is_causal: bool
    created_at: str
    updated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineageGraph:
    graph_id: str
    root_ref: str
    node_ids: list[str]
    edge_ids: list[str]
    generated_at: str
    traversal_policy: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ImpactSet:
    impact_set_id: str
    root_ref: str
    affected_refs: list[str]
    edge_ids: list[str]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RebuildManifest:
    manifest_id: str
    target_version_ref: str
    required_version_refs: list[str]
    required_source_refs: list[str]
    required_transformation_refs: list[str]
    generated_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class LineageValidationError:
    status: str
    error_code: str
    message: str
    field_violations: list[dict[str, str]]
    detected_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RegistrationResult:
    status: str
    version_record: VersionRecord | None
    lineage_graph: LineageGraph | None
    impact_set: ImpactSet | None
    rebuild_manifest: RebuildManifest | None
    lineage_validation_error: LineageValidationError | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "version_record": (
                self.version_record.to_dict() if self.version_record is not None else None
            ),
            "lineage_graph": (
                self.lineage_graph.to_dict() if self.lineage_graph is not None else None
            ),
            "impact_set": self.impact_set.to_dict() if self.impact_set is not None else None,
            "rebuild_manifest": (
                self.rebuild_manifest.to_dict()
                if self.rebuild_manifest is not None
                else None
            ),
            "lineage_validation_error": (
                self.lineage_validation_error.to_dict()
                if self.lineage_validation_error is not None
                else None
            ),
        }


class VersioningLineageEngine:
    """Append-only registry for versions, lineage nodes, impact edges, and manifests."""

    def __init__(
        self,
        known_phase_contract_refs: Iterable[str] | None = None,
        initial_version_records: Iterable[VersionRecord | Mapping[str, Any]] | None = None,
    ) -> None:
        self.known_phase_contract_refs = set(known_phase_contract_refs or ())
        self._versions: dict[str, VersionRecord] = {}
        self._nodes: dict[str, LineageNode] = {}
        self._edges: dict[str, ImpactEdge] = {}

        for record in initial_version_records or ():
            self.seed_version_record(record)

    @property
    def version_records(self) -> Mapping[str, VersionRecord]:
        return dict(self._versions)

    @property
    def lineage_nodes(self) -> Mapping[str, LineageNode]:
        return dict(self._nodes)

    @property
    def impact_edges(self) -> Mapping[str, ImpactEdge]:
        return dict(self._edges)

    def process(
        self,
        object_mutations: Sequence[Mapping[str, Any]],
        source_references: Sequence[Mapping[str, Any] | str] | None = None,
        transformation_records: Sequence[Mapping[str, Any]] | None = None,
        phase_contract_ref: str | None = None,
        prior_version_ref: str | None = None,
        emitted_at: str = DEFAULT_CREATED_AT,
    ) -> RegistrationResult | list[RegistrationResult]:
        """Process one or more declared object mutations in deterministic order."""

        results: list[RegistrationResult] = []
        for mutation in object_mutations:
            merged = dict(mutation)
            if phase_contract_ref is not None:
                merged["phase_contract_ref"] = phase_contract_ref
            if prior_version_ref is not None:
                merged["prior_version_ref"] = prior_version_ref
            results.append(
                self.register_mutation(
                    object_mutation=merged,
                    source_references=source_references,
                    transformation_records=transformation_records,
                    emitted_at=emitted_at,
                )
            )
        if len(results) == 1:
            return results[0]
        return results

    def seed_version_record(self, record: VersionRecord | Mapping[str, Any]) -> VersionRecord:
        """Load a previously accepted immutable VersionRecord into the registry."""

        version_record = record if isinstance(record, VersionRecord) else self._record_from_mapping(record)
        existing = self._versions.get(version_record.version_id)
        if existing is not None and existing != version_record:
            raise ValueError("VersionRecord identity already exists with different content.")
        if existing is not None:
            return existing

        self._versions[version_record.version_id] = version_record
        object_node = self._node_for_version(version_record)
        self._nodes.setdefault(object_node.lineage_node_id, object_node)

        phase_node = self._node_for_ref(
            node_type="phase_contract",
            ref_id=version_record.phase_contract_ref,
            produced_by_motor="motor_001",
            produced_at=version_record.produced_at,
            source_ref=version_record.phase_contract_ref,
            created_at=version_record.created_at,
        )
        self._nodes.setdefault(phase_node.lineage_node_id, phase_node)

        for source_ref in self._source_refs_from_record(version_record):
            source_node = self._node_for_ref(
                node_type="source_reference",
                ref_id=source_ref,
                produced_by_motor=version_record.produced_by_motor,
                produced_at=version_record.produced_at,
                source_ref=source_ref,
                created_at=version_record.created_at,
            )
            self._nodes.setdefault(source_node.lineage_node_id, source_node)
            self._commit_edge_if_valid(
                source_node.lineage_node_id,
                object_node.lineage_node_id,
                "uses_source",
                source_ref,
                True,
                version_record.created_at,
            )

        for transformation_ref in version_record.transformation_refs:
            transformation_node = self._node_for_ref(
                node_type="transformation",
                ref_id=transformation_ref,
                produced_by_motor=version_record.produced_by_motor,
                produced_at=version_record.produced_at,
                source_ref=version_record.source_ref,
                created_at=version_record.created_at,
            )
            self._nodes.setdefault(transformation_node.lineage_node_id, transformation_node)
            self._commit_edge_if_valid(
                transformation_node.lineage_node_id,
                object_node.lineage_node_id,
                "derived_from",
                transformation_ref,
                True,
                version_record.created_at,
            )

        self._commit_edge_if_valid(
            phase_node.lineage_node_id,
            object_node.lineage_node_id,
            "governed_by_phase_contract",
            version_record.phase_contract_ref,
            False,
            version_record.created_at,
        )
        return version_record

    def register_mutation(
        self,
        object_mutation: Mapping[str, Any],
        source_references: Sequence[Mapping[str, Any] | str] | None = None,
        transformation_records: Sequence[Mapping[str, Any]] | None = None,
        phase_contract_refs: Iterable[str] | None = None,
        emitted_at: str = DEFAULT_CREATED_AT,
    ) -> RegistrationResult:
        """Validate and append exactly one VersionRecord for one governed mutation."""

        known_phase_refs = set(self.known_phase_contract_refs)
        known_phase_refs.update(phase_contract_refs or ())

        source_ref_map = self._reference_map(source_references or (), ("source_id", "ref_id", "source_ref"))
        transformation_map = self._reference_map(
            transformation_records or (),
            ("transformation_id", "ref_id", "transformation_ref"),
        )

        errors = self._validate_mutation(
            object_mutation=object_mutation,
            known_phase_refs=known_phase_refs,
            source_ref_map=source_ref_map,
            transformation_map=transformation_map,
        )
        if errors:
            return self._rejected(errors, emitted_at)

        mutation = dict(object_mutation)
        object_id = str(mutation["object_id"])
        object_type = str(mutation["object_type"])
        mutation_type = str(mutation["mutation_type"])
        phase_contract_ref = str(mutation["phase_contract_ref"])
        source_ref = str(mutation["source_ref"])
        provenance_refs = self._string_list(mutation["provenance_refs"])
        transformation_refs = self._string_list(mutation.get("transformation_refs", ()))
        dependency_version_refs = self._string_list(mutation.get("dependency_version_refs", ()))
        produced_by_motor = str(mutation["produced_by_motor"])
        produced_at = str(mutation.get("produced_at") or mutation.get("timestamp"))
        version_hash = str(mutation.get("version_hash") or mutation.get("content_hash"))
        parent_id = self._nullable_ref(mutation.get("prior_version_ref", mutation.get("parent_id")))
        version_id = str(mutation.get("version_id") or self._next_version_id(object_type, object_id))
        object_ref = str(mutation.get("object_ref") or self._object_ref(object_type, object_id))

        if version_id in self._versions:
            return self._rejected(
                [
                    self._violation(
                        "HISTORY_REWRITE",
                        "version_id",
                        "VersionRecord identifiers are append-only and cannot be reused.",
                    )
                ],
                emitted_at,
            )

        version_record = VersionRecord(
            version_id=version_id,
            record_id=str(mutation.get("record_id") or version_id),
            object_id=object_id,
            object_type=object_type,
            object_ref=object_ref,
            mutation_type=mutation_type,
            phase_contract_ref=phase_contract_ref,
            parent_id=parent_id,
            prior_version_ref=parent_id,
            source_ref=source_ref,
            provenance_refs=provenance_refs,
            transformation_refs=transformation_refs,
            dependency_version_refs=dependency_version_refs,
            produced_by_motor=produced_by_motor,
            produced_at=produced_at,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            metadata=dict(mutation.get("metadata") or {}),
        )

        staged_nodes = dict(self._nodes)
        staged_edges = dict(self._edges)
        new_edges: list[ImpactEdge] = []

        target_node = self._node_for_version(version_record)
        staged_nodes.setdefault(target_node.lineage_node_id, target_node)

        phase_node = self._node_for_ref(
            node_type="phase_contract",
            ref_id=phase_contract_ref,
            produced_by_motor="motor_001",
            produced_at=produced_at,
            source_ref=phase_contract_ref,
            created_at=emitted_at,
        )
        staged_nodes.setdefault(phase_node.lineage_node_id, phase_node)
        new_edges.append(
            self._make_edge(
                phase_node.lineage_node_id,
                target_node.lineage_node_id,
                "governed_by_phase_contract",
                phase_contract_ref,
                False,
                emitted_at,
            )
        )

        for source_id in self._source_refs_for_mutation(
            source_ref, provenance_refs, transformation_refs, dependency_version_refs
        ):
            source_node = self._node_for_ref(
                node_type="source_reference",
                ref_id=source_id,
                produced_by_motor=produced_by_motor,
                produced_at=produced_at,
                source_ref=source_id,
                created_at=emitted_at,
            )
            staged_nodes.setdefault(source_node.lineage_node_id, source_node)
            new_edges.append(
                self._make_edge(
                    source_node.lineage_node_id,
                    target_node.lineage_node_id,
                    "uses_source",
                    source_id,
                    True,
                    emitted_at,
                )
            )

        for transformation_ref in transformation_refs:
            transformation_record = transformation_map[transformation_ref]
            transformation_node = self._node_for_ref(
                node_type="transformation",
                ref_id=transformation_ref,
                produced_by_motor=str(transformation_record.get("produced_by_motor") or produced_by_motor),
                produced_at=str(
                    transformation_record.get("produced_at")
                    or transformation_record.get("timestamp")
                    or produced_at
                ),
                source_ref=source_ref,
                created_at=emitted_at,
            )
            staged_nodes.setdefault(transformation_node.lineage_node_id, transformation_node)
            new_edges.append(
                self._make_edge(
                    transformation_node.lineage_node_id,
                    target_node.lineage_node_id,
                    "derived_from",
                    transformation_ref,
                    True,
                    emitted_at,
                )
            )

        for dependency_version_ref in self._unique_refs([parent_id, *dependency_version_refs]):
            if dependency_version_ref is None:
                continue
            dependency_node = self._node_for_existing_version(dependency_version_ref)
            staged_nodes.setdefault(dependency_node.lineage_node_id, dependency_node)
            edge_type = self._edge_type_for_version_dependency(mutation_type)
            new_edges.append(
                self._make_edge(
                    dependency_node.lineage_node_id,
                    target_node.lineage_node_id,
                    edge_type,
                    dependency_version_ref,
                    True,
                    emitted_at,
                )
            )

        edge_errors = self._validate_edges_for_commit(new_edges, staged_nodes, staged_edges)
        if edge_errors:
            return self._rejected(edge_errors, emitted_at)

        self._versions[version_record.version_id] = version_record
        self._nodes = staged_nodes
        for edge in new_edges:
            self._edges.setdefault(edge.impact_edge_id, edge)

        lineage_graph = self.build_lineage_graph(
            root_ref=version_record.version_id,
            traversal_policy="ancestors",
            generated_at=emitted_at,
        )
        impact_set = self.compute_impact_set(version_record.version_id, generated_at=emitted_at)
        rebuild_manifest = self.build_rebuild_manifest(version_record.version_id, generated_at=emitted_at)
        return RegistrationResult(
            status="ACCEPTED",
            version_record=version_record,
            lineage_graph=lineage_graph,
            impact_set=impact_set,
            rebuild_manifest=rebuild_manifest,
            lineage_validation_error=None,
        )

    def register_lineage_node(
        self,
        node_type: str,
        ref_id: str,
        source_ref: str,
        produced_by_motor: str,
        produced_at: str,
        version_ref: str | None = None,
        parent_id: str | None = None,
        created_at: str = DEFAULT_CREATED_AT,
    ) -> LineageNode:
        """Register a typed lineage node without inferring any edges."""

        if node_type not in NODE_TYPES:
            raise ValueError("Unsupported lineage node type.")
        node = self._node_for_ref(
            node_type=node_type,
            ref_id=ref_id,
            produced_by_motor=produced_by_motor,
            produced_at=produced_at,
            source_ref=source_ref,
            created_at=created_at,
            version_ref=version_ref,
            parent_id=parent_id,
        )
        existing = self._nodes.get(node.lineage_node_id)
        if existing is not None and existing != node:
            raise ValueError("LineageNode identity already exists with different content.")
        self._nodes.setdefault(node.lineage_node_id, node)
        return self._nodes[node.lineage_node_id]

    def register_impact_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: str,
        evidence_ref: str,
        is_causal: bool | None = None,
        created_at: str = DEFAULT_CREATED_AT,
    ) -> ImpactEdge | LineageValidationError:
        """Register one explicit ImpactEdge after endpoint and cycle checks."""

        causal = edge_type not in NON_CAUSAL_EDGE_TYPES if is_causal is None else is_causal
        edge = self._make_edge(
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            evidence_ref=evidence_ref,
            is_causal=causal,
            created_at=created_at,
        )
        errors = self._validate_edges_for_commit([edge], self._nodes, self._edges)
        if errors:
            return self._validation_error(errors, created_at)
        self._edges.setdefault(edge.impact_edge_id, edge)
        return self._edges[edge.impact_edge_id]

    def build_lineage_graph(
        self,
        root_ref: str,
        traversal_policy: str = "ancestors",
        generated_at: str = DEFAULT_CREATED_AT,
    ) -> LineageGraph:
        """Build a deterministic graph view from registered nodes and edges."""

        if traversal_policy not in {"ancestors", "descendants", "full_subgraph"}:
            raise ValueError("Unsupported traversal policy.")
        root_node_id = self._resolve_node_id(root_ref)
        node_ids, edge_ids = self._traverse(root_node_id, traversal_policy)
        graph_id = self._stable_id("graph", root_ref, traversal_policy, node_ids, edge_ids)
        return LineageGraph(
            graph_id=graph_id,
            root_ref=root_ref,
            node_ids=node_ids,
            edge_ids=edge_ids,
            generated_at=generated_at,
            traversal_policy=traversal_policy,
        )

    def compute_impact_set(
        self,
        root_ref: str,
        generated_at: str = DEFAULT_CREATED_AT,
    ) -> ImpactSet:
        """Compute affected refs by traversing outgoing causal ImpactEdge records."""

        root_node_id = self._resolve_node_id(root_ref)
        visited_nodes = {root_node_id}
        queue: deque[str] = deque([root_node_id])
        affected_refs: set[str] = set()
        edge_ids: set[str] = set()

        while queue:
            node_id = queue.popleft()
            for edge in self._outgoing_edges(node_id, causal_only=True):
                edge_ids.add(edge.impact_edge_id)
                if edge.target_node_id not in visited_nodes:
                    visited_nodes.add(edge.target_node_id)
                    queue.append(edge.target_node_id)
                target_node = self._nodes[edge.target_node_id]
                affected_refs.add(target_node.ref_id)

        sorted_affected = sorted(affected_refs)
        sorted_edges = sorted(edge_ids)
        impact_set_id = self._stable_id("impact", root_ref, sorted_affected, sorted_edges)
        return ImpactSet(
            impact_set_id=impact_set_id,
            root_ref=root_ref,
            affected_refs=sorted_affected,
            edge_ids=sorted_edges,
            generated_at=generated_at,
        )

    def build_rebuild_manifest(
        self,
        target_version_ref: str,
        generated_at: str = DEFAULT_CREATED_AT,
    ) -> RebuildManifest:
        """Build a parent-before-child manifest from registered lineage only."""

        if target_version_ref not in self._versions:
            raise ValueError("Unknown target VersionRecord.")
        target_node_id = self._resolve_node_id(target_version_ref)

        visited: set[str] = set()
        ordered_version_refs: list[str] = []

        def visit(node_id: str) -> None:
            if node_id in visited:
                return
            visited.add(node_id)
            for edge in self._incoming_edges(node_id, causal_only=True):
                visit(edge.source_node_id)
            node = self._nodes[node_id]
            if node.node_type == "object_version" and node.ref_id != target_version_ref:
                ordered_version_refs.append(node.ref_id)

        visit(target_node_id)

        ancestor_nodes = {target_node_id, *visited}
        required_sources = sorted(
            {
                self._nodes[node_id].ref_id
                for node_id in ancestor_nodes
                if self._nodes[node_id].node_type == "source_reference"
            }
        )
        required_transformations = sorted(
            {
                self._nodes[node_id].ref_id
                for node_id in ancestor_nodes
                if self._nodes[node_id].node_type == "transformation"
            }
        )
        required_versions = self._dedupe_preserve_order(ordered_version_refs)
        manifest_id = self._stable_id(
            "manifest",
            target_version_ref,
            required_versions,
            required_sources,
            required_transformations,
        )
        return RebuildManifest(
            manifest_id=manifest_id,
            target_version_ref=target_version_ref,
            required_version_refs=required_versions,
            required_source_refs=required_sources,
            required_transformation_refs=required_transformations,
            generated_at=generated_at,
        )

    def _record_from_mapping(self, raw_record: Mapping[str, Any]) -> VersionRecord:
        required_strings = (
            "version_id",
            "object_id",
            "object_type",
            "mutation_type",
            "phase_contract_ref",
            "source_ref",
            "produced_by_motor",
        )
        missing = [name for name in required_strings if not self._present(raw_record.get(name))]
        if not self._string_list(raw_record.get("provenance_refs")):
            missing.append("provenance_refs")
        produced_at = raw_record.get("produced_at") or raw_record.get("timestamp")
        if not self._present(produced_at):
            missing.append("produced_at")
        version_hash = raw_record.get("version_hash") or raw_record.get("content_hash")
        if not self._present(version_hash):
            missing.append("version_hash")
        if missing:
            raise ValueError(f"VersionRecord is missing required fields: {', '.join(missing)}")

        created_at = str(raw_record.get("created_at") or DEFAULT_CREATED_AT)
        parent_id = self._nullable_ref(raw_record.get("prior_version_ref", raw_record.get("parent_id")))
        object_type = str(raw_record["object_type"])
        object_id = str(raw_record["object_id"])
        version_id = str(raw_record["version_id"])
        return VersionRecord(
            version_id=version_id,
            record_id=str(raw_record.get("record_id") or version_id),
            object_id=object_id,
            object_type=object_type,
            object_ref=str(raw_record.get("object_ref") or self._object_ref(object_type, object_id)),
            mutation_type=str(raw_record["mutation_type"]),
            phase_contract_ref=str(raw_record["phase_contract_ref"]),
            parent_id=parent_id,
            prior_version_ref=parent_id,
            source_ref=str(raw_record["source_ref"]),
            provenance_refs=self._string_list(raw_record["provenance_refs"]),
            transformation_refs=self._string_list(raw_record.get("transformation_refs", ())),
            dependency_version_refs=self._string_list(raw_record.get("dependency_version_refs", ())),
            produced_by_motor=str(raw_record["produced_by_motor"]),
            produced_at=str(produced_at),
            created_at=created_at,
            updated_at=str(raw_record.get("updated_at") or created_at),
            version_hash=str(version_hash),
            metadata=dict(raw_record.get("metadata") or {}),
        )

    def _validate_mutation(
        self,
        object_mutation: Mapping[str, Any],
        known_phase_refs: set[str],
        source_ref_map: Mapping[str, Mapping[str, Any]],
        transformation_map: Mapping[str, Mapping[str, Any]],
    ) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        if not isinstance(object_mutation, Mapping):
            return [
                self._violation(
                    "LINEAGE_INPUT_INVALID_TYPE",
                    "object_mutation",
                    "Object mutation must be a mapping.",
                )
            ]

        mutation = object_mutation
        required_string_fields = (
            "object_id",
            "object_type",
            "mutation_type",
            "phase_contract_ref",
            "source_ref",
            "produced_by_motor",
        )
        for field_name in required_string_fields:
            value = mutation.get(field_name)
            if not isinstance(value, str) or not value.strip():
                code = (
                    "LINEAGE_INPUT_MISSING_PHASE_CONTRACT"
                    if field_name == "phase_contract_ref"
                    else "LINEAGE_INPUT_MISSING_REQUIRED_FIELD"
                )
                errors.append(
                    self._violation(
                        code,
                        field_name,
                        f"{field_name} must be a non-empty string.",
                    )
                )

        produced_at = mutation.get("produced_at") or mutation.get("timestamp")
        if not isinstance(produced_at, str) or not produced_at.strip():
            errors.append(
                self._violation(
                    "LINEAGE_INPUT_MISSING_REQUIRED_FIELD",
                    "produced_at",
                    "produced_at or timestamp must be a non-empty string.",
                )
            )

        fingerprint = mutation.get("version_hash") or mutation.get("content_hash")
        if not isinstance(fingerprint, str) or not fingerprint.strip():
            errors.append(
                self._violation(
                    "LINEAGE_INPUT_MISSING_REQUIRED_FIELD",
                    "version_hash",
                    "version_hash or content_hash must be a non-empty string.",
                )
            )

        mutation_type = mutation.get("mutation_type")
        if isinstance(mutation_type, str) and mutation_type.strip() and mutation_type not in MUTATION_TYPES:
            errors.append(
                self._violation(
                    "LINEAGE_INPUT_INVALID_MUTATION_TYPE",
                    "mutation_type",
                    "mutation_type is outside the allowed mutation set.",
                )
            )

        phase_contract_ref = mutation.get("phase_contract_ref")
        if (
            isinstance(phase_contract_ref, str)
            and phase_contract_ref.strip()
            and known_phase_refs
            and phase_contract_ref not in known_phase_refs
        ):
            errors.append(
                self._violation(
                    "LINEAGE_INPUT_MISSING_PHASE_CONTRACT",
                    "phase_contract_ref",
                    "phase_contract_ref is not present in the supplied motor_001 contract refs.",
                )
            )

        provenance_refs_raw = mutation.get("provenance_refs")
        provenance_refs = self._string_list(provenance_refs_raw)
        if not provenance_refs:
            errors.append(
                self._violation(
                    "LINEAGE_GAP",
                    "provenance_refs",
                    "provenance_refs must contain at least one explicit reference.",
                )
            )

        source_ref = mutation.get("source_ref")
        if isinstance(source_ref, str) and source_ref.strip():
            if provenance_refs and source_ref not in provenance_refs:
                errors.append(
                    self._violation(
                        "LINEAGE_GAP",
                        "provenance_refs",
                        "source_ref must be present in provenance_refs.",
                    )
                )
            if source_ref_map and source_ref not in source_ref_map:
                errors.append(
                    self._violation(
                        "LINEAGE_SOURCE_REFERENCE_UNRESOLVED",
                        "source_ref",
                        "source_ref is absent from the supplied source_references.",
                    )
                )

        prior_version_ref = self._nullable_ref(
            mutation.get("prior_version_ref", mutation.get("parent_id"))
        )
        if mutation_type in PRIOR_REQUIRED_MUTATIONS:
            if not prior_version_ref:
                errors.append(
                    self._violation(
                        "LINEAGE_PRIOR_VERSION_REQUIRED",
                        "prior_version_ref",
                        "This mutation_type requires an existing prior_version_ref.",
                    )
                )
            elif prior_version_ref not in self._versions:
                errors.append(
                    self._violation(
                        "LINEAGE_PRIOR_VERSION_UNRESOLVED",
                        "prior_version_ref",
                        "prior_version_ref does not identify an existing VersionRecord.",
                    )
                )
        elif mutation_type == "create" and prior_version_ref is not None:
            errors.append(
                self._violation(
                    "LINEAGE_PRIOR_VERSION_NOT_ALLOWED",
                    "prior_version_ref",
                    "create mutations must not declare a prior version.",
                )
            )

        dependency_refs = self._string_list(mutation.get("dependency_version_refs", ()))
        for dependency_ref in dependency_refs:
            if dependency_ref not in self._versions:
                errors.append(
                    self._violation(
                        "LINEAGE_DEPENDENCY_UNRESOLVED",
                        "dependency_version_refs",
                        f"dependency version {dependency_ref} is not registered.",
                    )
                )

        transformation_refs = self._string_list(mutation.get("transformation_refs", ()))
        for transformation_ref in transformation_refs:
            transformation_record = transformation_map.get(transformation_ref)
            if transformation_record is None:
                errors.append(
                    self._violation(
                        "LINEAGE_GAP",
                        "transformation_refs",
                        f"transformation ref {transformation_ref} has no supplied record.",
                    )
                )
            elif not self._transformation_output_matches(mutation, transformation_record):
                errors.append(
                    self._violation(
                        "LINEAGE_TRANSFORMATION_OUTPUT_MISMATCH",
                        "transformation_records.output_object_ref",
                        "transformation output does not match the object mutation.",
                    )
                )

        return errors

    def _validate_edges_for_commit(
        self,
        new_edges: Sequence[ImpactEdge],
        staged_nodes: Mapping[str, LineageNode],
        staged_edges: Mapping[str, ImpactEdge],
    ) -> list[dict[str, str]]:
        errors: list[dict[str, str]] = []
        accepted_edges = dict(staged_edges)
        for edge in new_edges:
            if edge.edge_type not in EDGE_TYPES:
                errors.append(
                    self._violation(
                        "LINEAGE_EDGE_INVALID_TYPE",
                        "edge_type",
                        "ImpactEdge edge_type is outside the allowed set.",
                    )
                )
                continue
            if edge.source_node_id not in staged_nodes:
                errors.append(
                    self._violation(
                        "LINEAGE_EDGE_UNKNOWN_SOURCE_NODE",
                        "source_node_id",
                        "ImpactEdge source_node_id does not resolve to a LineageNode.",
                    )
                )
                continue
            if edge.target_node_id not in staged_nodes:
                errors.append(
                    self._violation(
                        "LINEAGE_EDGE_UNKNOWN_TARGET_NODE",
                        "target_node_id",
                        "ImpactEdge target_node_id does not resolve to a LineageNode.",
                    )
                )
                continue
            existing = accepted_edges.get(edge.impact_edge_id)
            if existing is not None:
                if existing == edge:
                    continue
                errors.append(
                    self._violation(
                        "LINEAGE_EDGE_ID_CONFLICT",
                        "impact_edge_id",
                        "ImpactEdge identifier resolves to different edge content.",
                    )
                )
                continue
            if edge.is_causal and self._would_create_cycle(edge, accepted_edges):
                errors.append(
                    self._violation(
                        "LINEAGE_CYCLE_DETECTED",
                        "impact_edge",
                        "Causal ImpactEdge would create a directed lineage cycle.",
                    )
                )
                continue
            accepted_edges[edge.impact_edge_id] = edge
        return errors

    def _commit_edge_if_valid(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: str,
        evidence_ref: str,
        is_causal: bool,
        created_at: str,
    ) -> None:
        edge = self._make_edge(
            source_node_id,
            target_node_id,
            edge_type,
            evidence_ref,
            is_causal,
            created_at,
        )
        if not self._validate_edges_for_commit([edge], self._nodes, self._edges):
            self._edges.setdefault(edge.impact_edge_id, edge)

    def _would_create_cycle(self, edge: ImpactEdge, edges: Mapping[str, ImpactEdge]) -> bool:
        adjacency: dict[str, list[str]] = {}
        for existing in edges.values():
            if existing.is_causal:
                adjacency.setdefault(existing.source_node_id, []).append(existing.target_node_id)
        adjacency.setdefault(edge.source_node_id, []).append(edge.target_node_id)

        stack = [edge.target_node_id]
        visited: set[str] = set()
        while stack:
            node_id = stack.pop()
            if node_id == edge.source_node_id:
                return True
            if node_id in visited:
                continue
            visited.add(node_id)
            stack.extend(sorted(adjacency.get(node_id, ()), reverse=True))
        return False

    def _traverse(self, root_node_id: str, traversal_policy: str) -> tuple[list[str], list[str]]:
        visited_nodes = {root_node_id}
        visited_edges: set[str] = set()
        queue: deque[str] = deque([root_node_id])

        while queue:
            node_id = queue.popleft()
            candidate_edges: list[ImpactEdge] = []
            if traversal_policy in {"ancestors", "full_subgraph"}:
                candidate_edges.extend(self._incoming_edges(node_id, causal_only=False))
            if traversal_policy in {"descendants", "full_subgraph"}:
                candidate_edges.extend(self._outgoing_edges(node_id, causal_only=False))

            for edge in sorted(candidate_edges, key=lambda item: item.impact_edge_id):
                visited_edges.add(edge.impact_edge_id)
                other_node_id = (
                    edge.source_node_id if edge.target_node_id == node_id else edge.target_node_id
                )
                if other_node_id not in visited_nodes:
                    visited_nodes.add(other_node_id)
                    queue.append(other_node_id)

        return sorted(visited_nodes), sorted(visited_edges)

    def _incoming_edges(self, node_id: str, causal_only: bool) -> list[ImpactEdge]:
        return sorted(
            (
                edge
                for edge in self._edges.values()
                if edge.target_node_id == node_id and (edge.is_causal or not causal_only)
            ),
            key=lambda item: (self._nodes[item.source_node_id].ref_id, item.impact_edge_id),
        )

    def _outgoing_edges(self, node_id: str, causal_only: bool) -> list[ImpactEdge]:
        return sorted(
            (
                edge
                for edge in self._edges.values()
                if edge.source_node_id == node_id and (edge.is_causal or not causal_only)
            ),
            key=lambda item: (self._nodes[item.target_node_id].ref_id, item.impact_edge_id),
        )

    def _resolve_node_id(self, ref: str) -> str:
        if ref in self._nodes:
            return ref
        if ref in self._versions:
            return self._node_for_version(self._versions[ref]).lineage_node_id
        matches = [
            node.lineage_node_id
            for node in self._nodes.values()
            if node.ref_id == ref or node.version_ref == ref
        ]
        if not matches:
            raise ValueError("Unknown lineage root reference.")
        return sorted(matches)[0]

    def _node_for_version(self, record: VersionRecord) -> LineageNode:
        node_id = self._lineage_node_id("object_version", record.version_id)
        parent_node_id = None
        if record.parent_id and record.parent_id in self._versions:
            parent_node_id = self._node_for_existing_version(record.parent_id).lineage_node_id
        return LineageNode(
            lineage_node_id=node_id,
            node_type="object_version",
            ref_id=record.version_id,
            version_ref=record.version_id,
            source_ref=record.source_ref,
            produced_by_motor=record.produced_by_motor,
            produced_at=record.produced_at,
            parent_id=parent_node_id,
            created_at=record.created_at,
            updated_at=record.created_at,
        )

    def _node_for_existing_version(self, version_ref: str) -> LineageNode:
        record = self._versions[version_ref]
        node = self._node_for_version(record)
        return self._nodes.get(node.lineage_node_id, node)

    def _node_for_ref(
        self,
        node_type: str,
        ref_id: str,
        produced_by_motor: str,
        produced_at: str,
        source_ref: str,
        created_at: str,
        version_ref: str | None = None,
        parent_id: str | None = None,
    ) -> LineageNode:
        return LineageNode(
            lineage_node_id=self._lineage_node_id(node_type, ref_id),
            node_type=node_type,
            ref_id=ref_id,
            version_ref=version_ref,
            source_ref=source_ref,
            produced_by_motor=produced_by_motor,
            produced_at=produced_at,
            parent_id=parent_id,
            created_at=created_at,
            updated_at=created_at,
        )

    def _make_edge(
        self,
        source_node_id: str,
        target_node_id: str,
        edge_type: str,
        evidence_ref: str,
        is_causal: bool,
        created_at: str,
    ) -> ImpactEdge:
        edge_id = self._stable_id("edge", source_node_id, target_node_id, edge_type, evidence_ref)
        return ImpactEdge(
            impact_edge_id=edge_id,
            source_node_id=source_node_id,
            target_node_id=target_node_id,
            edge_type=edge_type,
            evidence_ref=evidence_ref,
            is_causal=is_causal,
            created_at=created_at,
            updated_at=created_at,
        )

    def _edge_type_for_version_dependency(self, mutation_type: str) -> str:
        if mutation_type == "supersede":
            return "supersedes"
        if mutation_type == "withdraw":
            return "invalidates"
        return "depends_on"

    def _source_refs_from_record(self, record: VersionRecord) -> list[str]:
        return self._source_refs_for_mutation(
            source_ref=record.source_ref,
            provenance_refs=record.provenance_refs,
            transformation_refs=record.transformation_refs,
            dependency_version_refs=record.dependency_version_refs,
        )

    def _source_refs_for_mutation(
        self,
        source_ref: str,
        provenance_refs: Sequence[str],
        transformation_refs: Sequence[str],
        dependency_version_refs: Sequence[str],
    ) -> list[str]:
        non_source_refs = set(transformation_refs)
        non_source_refs.update(dependency_version_refs)
        non_source_refs.update(self._versions.keys())
        source_refs = [source_ref]
        source_refs.extend(ref for ref in provenance_refs if ref not in non_source_refs)
        return self._dedupe_preserve_order(source_refs)

    def _reference_map(
        self,
        references: Sequence[Mapping[str, Any] | str],
        key_fields: Sequence[str],
    ) -> dict[str, Mapping[str, Any]]:
        mapped: dict[str, Mapping[str, Any]] = {}
        for reference in references:
            if isinstance(reference, str):
                if reference.strip():
                    mapped[reference] = {"ref_id": reference}
                continue
            if not isinstance(reference, Mapping):
                continue
            for field_name in key_fields:
                value = reference.get(field_name)
                if isinstance(value, str) and value.strip():
                    mapped[value] = reference
                    break
        return mapped

    def _transformation_output_matches(
        self,
        mutation: Mapping[str, Any],
        transformation_record: Mapping[str, Any],
    ) -> bool:
        output_ref = transformation_record.get("output_object_ref")
        if output_ref is None:
            return False
        object_id = mutation.get("object_id")
        object_ref = mutation.get("object_ref") or self._object_ref(
            str(mutation.get("object_type")), str(object_id)
        )
        if isinstance(output_ref, Mapping):
            candidates = {
                output_ref.get("object_id"),
                output_ref.get("object_ref"),
                output_ref.get("output_object_id"),
                output_ref.get("ref_id"),
            }
            return object_id in candidates or object_ref in candidates
        return str(output_ref) in {str(object_id), str(object_ref)}

    def _validation_error(
        self,
        violations: list[dict[str, str]],
        detected_at: str,
    ) -> LineageValidationError:
        primary_code = violations[0]["error_code"] if violations else "LINEAGE_VALIDATION_ERROR"
        for violation in violations:
            if violation["error_code"] == "LINEAGE_INPUT_MISSING_PHASE_CONTRACT":
                primary_code = violation["error_code"]
                break
        return LineageValidationError(
            status="REJECTED",
            error_code=primary_code,
            message="Versioning and lineage validation failed.",
            field_violations=violations,
            detected_at=detected_at,
        )

    def _rejected(
        self,
        violations: list[dict[str, str]],
        detected_at: str,
    ) -> RegistrationResult:
        return RegistrationResult(
            status="REJECTED",
            version_record=None,
            lineage_graph=None,
            impact_set=None,
            rebuild_manifest=None,
            lineage_validation_error=self._validation_error(violations, detected_at),
        )

    def _violation(self, error_code: str, field_path: str, message: str) -> dict[str, str]:
        return {
            "error_code": error_code,
            "field_path": field_path,
            "message": message,
        }

    def _next_version_id(self, object_type: str, object_id: str) -> str:
        prefix = f"vr_{self._slug(object_type)}_{self._slug(object_id)}"
        ordinal = 1 + sum(
            1
            for record in self._versions.values()
            if record.object_type == object_type and record.object_id == object_id
        )
        return f"{prefix}_v{ordinal}"

    def _lineage_node_id(self, node_type: str, ref_id: str) -> str:
        return f"ln_{node_type}_{self._hash(ref_id)[:16]}"

    def _stable_id(self, prefix: str, *parts: Any) -> str:
        return f"{prefix}_{self._hash(parts)[:24]}"

    def _hash(self, value: Any) -> str:
        payload = json.dumps(value, sort_keys=True, separators=(",", ":"), default=str)
        return hashlib.sha256(payload.encode("utf-8")).hexdigest()

    def _object_ref(self, object_type: str, object_id: str) -> str:
        if object_id.startswith(f"{object_type}:"):
            return object_id
        return f"{object_type}:{object_id}"

    def _string_list(self, value: Any) -> list[str]:
        if value is None:
            return []
        if isinstance(value, str):
            return [value] if value.strip() else []
        if not isinstance(value, Sequence):
            return []
        result: list[str] = []
        for item in value:
            if isinstance(item, str) and item.strip():
                result.append(item)
        return result

    def _nullable_ref(self, value: Any) -> str | None:
        if value is None:
            return None
        if isinstance(value, str) and value.strip():
            return value
        return None

    def _unique_refs(self, refs: Sequence[str | None]) -> list[str | None]:
        result: list[str | None] = []
        seen: set[str | None] = set()
        for ref in refs:
            if ref in seen:
                continue
            seen.add(ref)
            result.append(ref)
        return result

    def _dedupe_preserve_order(self, refs: Iterable[str]) -> list[str]:
        result: list[str] = []
        seen: set[str] = set()
        for ref in refs:
            if ref in seen:
                continue
            seen.add(ref)
            result.append(ref)
        return result

    def _present(self, value: Any) -> bool:
        return isinstance(value, str) and bool(value.strip())

    def _slug(self, value: str) -> str:
        lowered = value.lower()
        slug = re.sub(r"[^a-z0-9]+", "_", lowered).strip("_")
        return slug or "ref"


__all__ = [
    "ImpactEdge",
    "ImpactSet",
    "LineageGraph",
    "LineageNode",
    "LineageValidationError",
    "RegistrationResult",
    "RebuildManifest",
    "VersionRecord",
    "VersioningLineageEngine",
]
