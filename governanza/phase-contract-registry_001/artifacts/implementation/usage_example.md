# Usage Example — Phase Contract Registry

Motor ID: motor_001

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Definir y hacer cumplir contratos de fase: inputs, outputs, límites y handoffs entre motores.
why_it_exists:  Evita que los motores invadan fases o produzcan outputs indebidos sin contrato explícito.
key_inputs:     phase definitions, motor declarations, contract schemas
key_outputs:    phase_contract records, handoff definitions, limit enforcement signals
key_objects:    PhaseContract, Handoff, ContractViolation
what_not_to_do: No implementa lógica de negocio. No ejecuta motores. Solo registra y valida contratos.
design_notes:   Motor fundacional. No depende de ningún otro. Es el ancla de todo el sistema.

Implementation example completed for the implementation gate.
-->

## example
El orquestador prepara el contrato de fase para `motor_001` antes de permitir que otros motores consuman sus artefactos. Llama al `PhaseContractRegistry` con la definición de la fase `documentation_base`, la declaración contractual de `motor_001` y el schema `phase_contract_v1`; espera un registro contractual activo y ninguna señal de violación. No se declara handoff downstream en este caso, por lo que el resultado conserva `handoff_definitions=[]`.

## inputs_used
```json
{
  "phase_definitions": [
    {
      "phase_id": "documentation_base",
      "stage_sequence": [
        "documentation_base",
        "schema_technical",
        "tests",
        "failure_modes",
        "implementation",
        "conformance_review"
      ]
    }
  ],
  "motor_declarations": [
    {
      "contract_id": "phase-contract-registry.documentation_base",
      "motor_id": "motor_001",
      "phase_id": "documentation_base",
      "version": "1.0.0",
      "allowed_inputs": [
        "phase_definitions",
        "motor_declarations",
        "contract_schemas"
      ],
      "allowed_outputs": [
        "phase_contract_records",
        "handoff_definitions",
        "limit_enforcement_signals"
      ],
      "limits": [
        "no motor execution",
        "no business logic",
        "no direct motor_state mutation"
      ],
      "contract_schema_ref": "phase_contract_v1",
      "source_ref": "governanza/automation-base/motor_registry.md#phase-contract-registry"
    }
  ],
  "contract_schemas": {
    "phase_contract_v1": {
      "required_fields": [
        "contract_id",
        "motor_id",
        "phase_id",
        "version",
        "allowed_inputs",
        "allowed_outputs",
        "limits",
        "source_ref"
      ]
    }
  },
  "handoff_declarations": []
}
```

## expected_output
```json
{
  "phase_contract_records": [
    {
      "record_id": "phase_contract_<deterministic_id>",
      "contract_id": "phase-contract-registry.documentation_base",
      "motor_id": "motor_001",
      "phase_id": "documentation_base",
      "version": "1.0.0",
      "version_id": "contract-version_<deterministic_id>",
      "allowed_inputs": [
        "phase_definitions",
        "motor_declarations",
        "contract_schemas"
      ],
      "allowed_outputs": [
        "phase_contract_records",
        "handoff_definitions",
        "limit_enforcement_signals"
      ],
      "limits": [
        "no motor execution",
        "no business logic",
        "no direct motor_state mutation"
      ],
      "contract_schema_ref": "phase_contract_v1",
      "status": "active",
      "created_at": "2026-04-16T00:00:00Z",
      "updated_at": "2026-04-16T00:00:00Z",
      "version_hash": "<deterministic_hash>",
      "source_ref": "governanza/automation-base/motor_registry.md#phase-contract-registry",
      "produced_by_motor": "motor_001",
      "produced_at": "2026-04-16T00:00:00Z",
      "parent_id": null
    }
  ],
  "handoff_definitions": [],
  "limit_enforcement_signals": []
}
```

## notes
El ejemplo presupone que `motor_001` proviene del catálogo autorizado y que `documentation_base` está en la secuencia reconocida del workflow. La ausencia de handoffs es explícita y válida; si luego se declara un handoff, el `output_name` debe existir en `allowed_outputs` del contrato origen y el `expected_input_name` debe existir en `allowed_inputs` del contrato destino. El motor solo registra contratos y emite violaciones; no ejecuta motores, no aprueba gates y no modifica `motor_state.json`.
