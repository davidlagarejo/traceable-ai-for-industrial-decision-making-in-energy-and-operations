# Test Spec — Phase Contract Registry

Motor ID: motor_001

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Definir y hacer cumplir contratos de fase: inputs, outputs, límites y handoffs entre motores.
why_it_exists:  Evita que los motores invadan fases o produzcan outputs indebidos sin contrato explícito.
key_inputs:     phase definitions, motor declarations, contract schemas
key_outputs:    phase_contract records, handoff definitions, limit enforcement signals
key_objects:    PhaseContract, Handoff, ContractViolation
what_not_to_do: No implementa lógica de negocio. No ejecuta motores. Solo registra y valida contratos.
design_notes:   Motor fundacional. No depende de ningún otro. Es el ancla de todo el sistema.

All placeholder markers have been replaced with concrete test content.
-->

## happy_path
Input fixture:
- `phase_definitions=[{"phase_id":"documentation_base","stage_sequence":["documentation_base","schema_technical","tests","failure_modes","implementation","conformance_review"]}]`
- `motor_declarations=[{"motor_id":"motor_001","phase_id":"documentation_base","contract_id":"phase-contract-registry.documentation_base","version":"1.0.0","allowed_inputs":["phase_definitions","motor_declarations","contract_schemas"],"allowed_outputs":["phase_contract_records","handoff_definitions","limit_enforcement_signals"],"limits":["no motor execution","no business logic","no direct motor_state mutation"],"source_ref":"governanza/automation-base/motor_registry.md#phase-contract-registry"}]`
- `contract_schemas={"phase_contract_v1":{"required_fields":["contract_id","motor_id","phase_id","version","allowed_inputs","allowed_outputs","limits","source_ref"]}}`
- `handoff_declarations=[]`

Expected behavior:
- The declaration is accepted because `motor_id=motor_001` is authorized, `phase_id=documentation_base` is recognized, required fields are present, and all input, output, and limit fields are explicit lists.
- The motor emits exactly one `PhaseContract` with `contract_id=phase-contract-registry.documentation_base`, `motor_id=motor_001`, `phase_id=documentation_base`, `version=1.0.0`, `status=active`, non-empty `record_id`, non-empty `version_id`, non-empty `version_hash`, `source_ref` matching the fixture, `produced_by_motor=motor_001`, non-empty `produced_at`, and `parent_id=null`.
- The motor emits `handoff_definitions=[]` because no downstream handoff was declared.
- The motor emits `limit_enforcement_signals=[]` because the contract is valid and no boundary violation is present.

## sparse_case
Input fixture:
- Same valid `phase_definitions`, `motor_declarations`, and `contract_schemas` as the happy path.
- The contract declaration omits downstream handoff data entirely instead of supplying an empty list.
- The first contract version has `parent_id` absent in the source declaration because there is no prior version.
- The source declaration includes `allowed_outputs=[]` for a terminal phase contract named `phase-contract-registry.conformance_review.terminal` and includes the explicit limit `no downstream emission`.

Expected behavior:
- Missing handoff data is handled as an empty handoff declaration set and does not create a fatal error.
- The emitted first-version `PhaseContract.parent_id` is `null`; the motor does not invent a predecessor.
- The terminal contract with `allowed_outputs=[]` is accepted because the output list exists and is deliberately empty.
- The result contains valid `PhaseContract` records and no `ContractViolation` unless a handoff attempts to consume the terminal contract.

## malformed_input
Input fixture:
- `motor_declarations=[{"motor_id":"motor_001","phase_id":"documentation_base","contract_id":"phase-contract-registry.documentation_base","version":"","allowed_inputs":["phase_definitions"],"allowed_outputs":"phase_contract_records","limits":["no motor execution"],"source_ref":""}]`
- `phase_definitions=[{"phase_id":"documentation_base"}]`
- `contract_schemas={"phase_contract_v1":{"required_fields":["contract_id","motor_id","phase_id","version","allowed_inputs","allowed_outputs","limits","source_ref"]}}`

Expected behavior:
- The malformed declaration is rejected as a valid `PhaseContract`.
- The motor emits `ContractViolation` with `violation_code=CONTRACT_FIELD_MISSING`, `severity=ERROR`, `field_path=version`, and a `source_ref` pointing to the submitted declaration because `version` is empty.
- The motor emits `ContractViolation` with `violation_code=CONTRACT_FIELD_MISSING`, `severity=ERROR`, `field_path=source_ref`, because provenance is empty.
- The motor emits `ContractViolation` with `violation_code=CONTRACT_SCHEMA_INVALID`, `severity=ERROR`, `field_path=allowed_outputs`, because `allowed_outputs` is a string instead of `list[string]`.
- No accepted `PhaseContract` record is emitted for this declaration.

## edge_cases
- Identical duplicate declaration: submit the same `contract_id=phase-contract-registry.documentation_base`, same `version=1.0.0`, same normalized content, and same `source_ref` twice. Expected behavior: one active `PhaseContract` exists for the `(contract_id, version_id)` pair; the second declaration is idempotent, shares the same deterministic `version_hash`, and produces no `CONTRACT_VERSION_CONFLICT`.
- Conflicting duplicate version: submit the same `contract_id=phase-contract-registry.documentation_base` and declared `version=1.0.0` with a different `limits` list, such as replacing `no direct motor_state mutation` with `may update motor_state`. Expected behavior: the second declaration is rejected and `limit_enforcement_signals` includes `ContractViolation.violation_code=CONTRACT_VERSION_CONFLICT`, `severity=ERROR`, and `field_path=limits`.
- Undeclared output handoff: register a source contract whose `allowed_outputs=["phase_contract_records"]`, then submit a handoff with `output_name=quality_score` to a destination contract that expects `quality_score`. Expected behavior: the handoff is rejected and a `ContractViolation` is emitted with `violation_code=HANDOFF_OUTPUT_NOT_ALLOWED`, `handoff_id` set to the attempted handoff, and `field_path=output_name`.
- Boundary leakage declaration: submit a contract for `motor_001` whose `allowed_outputs` includes `business_decision` or whose `limits` authorize motor execution. Expected behavior: the contract is rejected or marked with blocking `ContractViolation.violation_code=BOUNDARY_LEAKAGE`, because motor_001 may register and validate contracts but may not execute motors or produce business decisions.

## pass_criteria
A test case passes when all observable outputs match the contract:
- Every accepted `PhaseContract` contains non-empty `record_id`, `contract_id`, `motor_id`, `phase_id`, `version`, `version_id`, `allowed_inputs`, `allowed_outputs`, `limits`, `contract_schema_ref`, `status`, `version_hash`, `source_ref`, `produced_by_motor=motor_001`, and `produced_at`.
- Empty lists are preserved only when explicitly allowed by the test case, such as `handoff_definitions=[]` or a terminal contract with `allowed_outputs=[]`.
- Every accepted `Handoff` references an output present in the source contract's `allowed_outputs` and an input present in the destination contract's `allowed_inputs`.
- Every rejected contract or handoff produces a `ContractViolation` with the expected `violation_code`, `severity`, `field_path`, `source_ref`, `produced_by_motor=motor_001`, and non-empty lineage fields.
- Duplicate identical declarations are idempotent, while duplicate version conflicts emit `CONTRACT_VERSION_CONFLICT`.

## fail_criteria
A test case fails if any of these conditions is observed:
- A malformed declaration is accepted without a blocking `ContractViolation`.
- The motor silently fills missing `version`, `source_ref`, `allowed_inputs`, `allowed_outputs`, or `limits` instead of emitting a violation.
- A handoff is accepted when `output_name` is absent from the source contract's `allowed_outputs` or `expected_input_name` is absent from the destination contract's `allowed_inputs`.
- A conflicting duplicate `(contract_id, version_id)` overwrites an existing record or passes without `CONTRACT_VERSION_CONFLICT`.
- A record emitted by motor_001 lacks provenance, versioning, or lineage fields required by the technical schema.
- The output includes responsibilities outside this motor's scope, such as executing a motor, mutating `motor_state.json`, approving a gate, or producing business or analytical decisions.
