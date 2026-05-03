# Technical Schema — Phase Contract Registry

Motor ID: motor_001

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Definir y hacer cumplir contratos de fase: inputs, outputs, límites y handoffs entre motores.
why_it_exists:  Evita que los motores invadan fases o produzcan outputs indebidos sin contrato explícito.
key_inputs:     phase definitions, motor declarations, contract schemas
key_outputs:    phase_contract records, handoff definitions, limit enforcement signals
key_objects:    PhaseContract, Handoff, ContractViolation
what_not_to_do: No implementa lógica de negocio. No ejecuta motores. Solo registra y valida contratos.
design_notes:   Motor fundacional. No depende de ningún otro. Es el ancla de todo el sistema.
-->

## entities
- PhaseContract: versioned registry record that declares the inputs, outputs, limits, and allowed responsibilities of one motor inside one workflow phase. Stage: `schema_technical` defines the object shape; runtime instances are produced by motor_001 as `phase_contract_records` for gate checking, handoff validation, and conformance review.
- Handoff: versioned registry record that declares a permitted transfer from an allowed output on a source `PhaseContract` to an allowed input on a destination `PhaseContract`. Stage: `schema_technical` defines the object shape; runtime instances are produced by motor_001 as `handoff_definitions` only when both sides are explicitly declared.
- ContractViolation: immutable validation signal that records a missing field, schema breach, version conflict, boundary violation, or incompatible handoff detected by motor_001. Stage: `schema_technical` defines the object shape; runtime instances are produced by motor_001 as `limit_enforcement_signals` and consumed by gate checking, validation logs, and correction workflows.

## fields
PhaseContract:
- record_id: string (required) — immutable storage identifier for this persisted contract version.
- contract_id: string (required) — stable logical identifier for the contract across versions.
- motor_id: string (required) — authorized motor that owns the phase contract.
- phase_id: string (required) — workflow phase governed by the contract.
- version: string (required) — declared semver contract version received from the source declaration.
- version_id: string (required) — stable technical version key for this specific contract version.
- allowed_inputs: list[string] (required) — explicit input names the motor may receive in the phase.
- allowed_outputs: list[string] (required) — explicit output names the motor may emit in the phase.
- limits: list[string] (required) — explicit boundaries and prohibited responsibilities for the phase.
- contract_schema_ref: string (required) — reference to the contract schema used to validate this record.
- status: enum[active, superseded, rejected] (required) — registry state of this contract version without implying motor execution state.
- created_at: datetime (required) — timestamp when this contract version was first registered.
- updated_at: datetime (required) — timestamp when registry metadata for this version was last updated.
- version_hash: string (required) — deterministic hash of the normalized contractual content.
- source_ref: string (required) — document, registry entry, or schema reference that produced the record.
- produced_by_motor: string (required) — fixed value `motor_001`.
- produced_at: datetime (required) — timestamp when motor_001 emitted the record.
- parent_id: string|null (required) — previous `record_id` when this version supersedes another version; null for the first version.

Handoff:
- record_id: string (required) — immutable storage identifier for this persisted handoff version.
- handoff_id: string (required) — stable logical identifier for the handoff across versions.
- source_contract_id: string (required) — `contract_id` of the source `PhaseContract`.
- source_version_id: string (required) — `version_id` of the source contract version being referenced.
- destination_contract_id: string (required) — `contract_id` of the destination `PhaseContract`.
- destination_version_id: string (required) — `version_id` of the destination contract version being referenced.
- output_name: string (required) — output that must exist in the source contract's `allowed_outputs`.
- expected_input_name: string (required) — input that must exist in the destination contract's `allowed_inputs`.
- compatibility_rule_ref: string (required) — schema or rule reference used to judge compatibility.
- version_id: string (required) — stable technical version key for this specific handoff version.
- created_at: datetime (required) — timestamp when this handoff version was first registered.
- updated_at: datetime (required) — timestamp when registry metadata for this version was last updated.
- version_hash: string (required) — deterministic hash of the normalized handoff content.
- source_ref: string (required) — declaration or registry source that produced the handoff.
- produced_by_motor: string (required) — fixed value `motor_001`.
- produced_at: datetime (required) — timestamp when motor_001 emitted the record.
- parent_id: string|null (required) — previous `record_id` when this handoff version supersedes another version; null for the first version.

ContractViolation:
- record_id: string (required) — immutable storage identifier for this violation signal.
- violation_id: string (required) — stable identifier for the emitted violation.
- contract_id: string (required) — affected `PhaseContract.contract_id`.
- contract_version_id: string|null (required) — affected `PhaseContract.version_id` when known; null when the version field itself is missing.
- handoff_id: string|null (required) — affected `Handoff.handoff_id` when the violation is handoff-specific; null for contract-only violations.
- violation_code: enum[CONTRACT_FIELD_MISSING, CONTRACT_SCHEMA_INVALID, CONTRACT_VERSION_CONFLICT, MOTOR_NOT_AUTHORIZED, PHASE_NOT_RECOGNIZED, HANDOFF_OUTPUT_NOT_ALLOWED, HANDOFF_INPUT_NOT_ALLOWED, HANDOFF_VERSION_AMBIGUOUS, BOUNDARY_LEAKAGE] (required) — machine-readable reason for the signal.
- severity: enum[ERROR, WARNING] (required) — blocking level assigned by motor_001.
- field_path: string (required) — dotted path to the field or relationship that failed validation.
- message: string (required) — concise human-readable explanation of the violation.
- detected_at: datetime (required) — timestamp when the violation was detected.
- version_id: string (required) — stable technical version key for the violation record.
- created_at: datetime (required) — timestamp when the violation record was first emitted.
- updated_at: datetime (required) — timestamp when registry metadata for this violation was last updated.
- version_hash: string (required) — deterministic hash of normalized violation content.
- source_ref: string (required) — source declaration, schema, or document that caused the violation.
- produced_by_motor: string (required) — fixed value `motor_001`.
- produced_at: datetime (required) — timestamp when motor_001 emitted the signal.
- parent_id: string|null (required) — prior violation `record_id` if this signal supersedes an earlier signal; null for a new signal.

## relationships
- `Handoff.source_contract_id` + `Handoff.source_version_id` references `PhaseContract.contract_id` + `PhaseContract.version_id`; the referenced `output_name` must be present in `PhaseContract.allowed_outputs`.
- `Handoff.destination_contract_id` + `Handoff.destination_version_id` references `PhaseContract.contract_id` + `PhaseContract.version_id`; the referenced `expected_input_name` must be present in `PhaseContract.allowed_inputs`.
- `ContractViolation.contract_id` + `ContractViolation.contract_version_id` references the affected `PhaseContract` when a contract record exists.
- `ContractViolation.handoff_id` references the affected `Handoff` when the violation concerns an attempted or registered handoff.
- `PhaseContract.parent_id` references an earlier `PhaseContract.record_id` only when a new immutable version supersedes a prior version.
- `Handoff.parent_id` references an earlier `Handoff.record_id` only when a new immutable version supersedes a prior handoff version.
- `ContractViolation.parent_id` references an earlier `ContractViolation.record_id` only when a correction or revalidation supersedes an earlier signal.
- No relationship grants execution authority, gate approval, motor startup, or mutation of `motor_state.json`; those remain outside motor_001.

## identifiers
- PhaseContract stable storage identifier: `record_id`.
- PhaseContract canonical logical identifier: `contract_id`; uniqueness for active registry entries is enforced by `(contract_id, version_id)`.
- Handoff stable storage identifier: `record_id`.
- Handoff canonical logical identifier: `handoff_id`; uniqueness for active registry entries is enforced by `(handoff_id, version_id)`.
- ContractViolation stable storage identifier: `record_id`.
- ContractViolation canonical logical identifier: `violation_id`; violations are immutable signals and may reference the same contract or handoff without sharing identifiers.
- Identifier generation must be deterministic from normalized entity type, logical ID, version key, and content hash so duplicate identical declarations remain idempotent.
- Empty `record_id`, `contract_id`, `handoff_id`, `violation_id`, `motor_id`, `phase_id`, or `version_id` values are invalid and produce `ContractViolation` rather than silent completion.

## versioning
- Every persisted entity includes `version_id`, `created_at`, `updated_at`, and `version_hash`.
- `version_id` identifies one immutable version of a `PhaseContract`, `Handoff`, or `ContractViolation`; for `PhaseContract`, it is derived from the declared `version` plus normalized content.
- `created_at` is set once when the record is first emitted by motor_001.
- `updated_at` may change only for registry metadata about the same immutable content; material contract or handoff changes require a new `version_id` and a new `record_id`.
- `version_hash` is computed from normalized entity content excluding non-material registry timestamps, enabling deterministic duplicate detection.
- A duplicate `(contract_id, version_id)` or `(handoff_id, version_id)` with identical `version_hash` is idempotent.
- A duplicate `(contract_id, version_id)` or `(handoff_id, version_id)` with a different `version_hash` is rejected with `CONTRACT_VERSION_CONFLICT`.
- Current records, historical records, and derived violation signals remain separate: a superseding version links to the previous immutable record through `parent_id` instead of rewriting prior content.

## lineage
- Every persisted entity includes `source_ref`, `produced_by_motor`, `produced_at`, and `parent_id`.
- `source_ref` records the exact document, registry entry, schema, or declaration used to construct the entity.
- `produced_by_motor` is always `motor_001` for records emitted by the Phase Contract Registry.
- `produced_at` records when motor_001 produced the entity, independent of source document timestamps.
- `parent_id` links a superseding record to the previous immutable `record_id`; it is null when no predecessor exists.
- Lineage is required for both accepted records and rejected or warning signals so a validator can reconstruct why a contract passed, failed, or was superseded.
- Motor_001 does not repair missing lineage by inference. Missing `source_ref`, `produced_by_motor`, `produced_at`, or required parent linkage where applicable produces `ContractViolation`.
