# Functional Contract — Versioning + Lineage Engine

Motor ID: motor_002

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Versionar objetos y registrar lineage, dependencias, impacto y reconstrucción.
why_it_exists:  Sin versionado no hay rebuild, stale detection ni auditoría seria.
key_inputs:     object mutations, source references, transformation records
key_outputs:    version_record, lineage_graph, impact_set, rebuild_manifest
key_objects:    VersionRecord, LineageNode, ImpactEdge
what_not_to_do: No decide si un objeto es válido. Solo registra versiones y dependencias.
design_notes:   Depende de motor_001 (phase contracts anclan el contexto de versión).

Sections below are complete for Gate 1 review.
-->

## inputs
- object_mutations: structured event list — origin: any governed motor that creates, updates, supersedes or withdraws an object under a phase contract from motor_001.
- source_references: reference list — origin: source-producing or source-consuming motors; contains source_id, source_version_id when available, citation or raw object reference, and access timestamp.
- transformation_records: structured transformation log — origin: motor that produced the derived object; contains transformation_id, input_object_refs, rule_or_process_ref, parameter_set, execution timestamp and output_object_ref.
- phase_contract_ref: string/object reference — source: motor_001; identifies the phase contract that authorizes the object type, handoff and output boundary for the versioned object.
- prior_version_ref: nullable string — source: existing VersionRecord registry in this motor; identifies the immediate predecessor when the mutation updates an existing object.

## outputs
- version_record: VersionRecord object — destination: version registry for audit, downstream consumers that need stable object history, and conformance review.
- lineage_graph: graph object — destination: downstream motors that need provenance traversal, reconstruction context or dependency inspection.
- impact_set: deterministic reference set — destination: propagation and re-evaluation consumers that decide operational follow-up outside this motor.
- rebuild_manifest: manifest object — destination: rebuild tooling or operators that need the ordered list of source, version and transformation references required to reconstruct an object.
- lineage_validation_error: structured error object — destination: orchestrator or calling motor when required versioning or lineage fields are missing or inconsistent.

## limits
- Never accepts a mutation without object_id, object_type, mutation_type, phase_contract_ref, timestamp and provenance references.
- Never accepts a dependency edge whose source or target cannot be represented as a registered object, source reference or transformation record.
- Never accepts a request to overwrite, delete or silently edit an existing VersionRecord; corrections must create a new version or explicit supersession edge.
- Never produces a quality decision, validity decision, epistemic decision or phase approval.
- Never produces normalized domain content, canonical entity merges, source refresh decisions or operational re-evaluation orders.
- Never emits a rebuild result; it emits only the manifest needed to reconstruct through another process.

## validations
- Reject input if `phase_contract_ref` is missing or cannot be tied to a known phase contract identifier supplied by motor_001.
- Reject input if `object_id`, `object_type`, `mutation_type`, `timestamp` or `provenance_refs` is null or empty.
- Reject updates when `prior_version_ref` is required by `mutation_type` but does not point to an existing VersionRecord.
- Reject dependency edges that create a directed cycle in the lineage graph unless the edge type is explicitly non-causal metadata.
- Reject transformation records whose declared output object does not match the mutation being versioned.
- Before emitting output, ensure every VersionRecord has version_id, object_ref, prior_version_ref field, created_at, mutation_type, phase_contract_ref, provenance_refs and content_hash or equivalent payload fingerprint.
- Before emitting output, ensure every lineage edge references existing nodes and has edge_type, created_at and evidence_ref.
- Before emitting a rebuild_manifest, ensure all listed dependencies are ordered so parents appear before dependent versions.
