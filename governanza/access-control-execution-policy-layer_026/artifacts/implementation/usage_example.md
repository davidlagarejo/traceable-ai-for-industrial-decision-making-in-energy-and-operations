# Usage Example — Access Control / Execution Policy Layer

Motor ID: motor_026

## example
Un proceso operacional solicita que `motor_023` lea una fuente interna durante la etapa `implementation`. El motor consulta un contrato de fase vigente, un `rights_profile` aprobado, una `access_class` interna y una política explícita `allow`; como todas las autoridades coinciden, emite una decisión `allow` trazable y un registro de auditoría.

## inputs_used
```python
from codebase import AccessControlExecutionPolicyLayer

execution_request = {
    "request_id": "req-026-demo-001",
    "actor_id": "orchestrator",
    "actor_type": "system",
    "motor_id": "motor_023",
    "stage_name": "implementation",
    "action": "read",
    "target_ref": "source:src-demo-001",
    "target_type": "source",
    "requested_at": "2026-04-18T12:00:00Z",
    "run_id": "run-demo-001",
    "correlation_id": "corr-demo-001",
    "declared_purpose": "internal_research",
}

phase_contracts = [
    {
        "contract_id": "phase-contract-motor-023",
        "version_id": "v1",
        "motor_id": "motor_023",
        "stages": [
            {
                "stage_name": "implementation",
                "allowed_actions": ["read", "write_audit_record"],
            }
        ],
        "status": "active",
    }
]

rights_profile = {
    "source_id": "src-demo-001",
    "license_basis": "internal-license",
    "permitted_uses": ["internal_research", "read"],
    "prohibited_uses": ["external_export"],
    "restriction_notes": "Internal use only.",
    "rights_status": "approved",
    "version_id": "rights-v1",
}

access_class = {
    "source_id": "src-demo-001",
    "access_class": "internal",
    "status": "active",
    "version_id": "access-v1",
}

execution_policy_set = [
    {
        "policy_id": "policy-internal-read",
        "policy_version": "policy-v1",
        "scope": "global",
        "effect": "allow",
        "subject_selector": {"actor_type": "system"},
        "action_selector": {"motor_id": "motor_023", "action": "read"},
        "target_selector": {"target_type": "source", "access_class": "internal"},
        "condition_set": {"declared_purpose": "internal_research"},
        "provenance_ref": "governed-policy-registry:policy-internal-read@policy-v1",
    }
]

result = AccessControlExecutionPolicyLayer().evaluate(
    execution_request=execution_request,
    phase_contracts=phase_contracts,
    rights_profile=rights_profile,
    access_class=access_class,
    execution_policy_set=execution_policy_set,
)
```

## expected_output
```python
{
    "policy_decision": {
        "request_id": "req-026-demo-001",
        "status": "allow",
        "reason_code": "ALLOW_POLICY_MATCHED",
        "policy_version": "policy-v1",
        "run_id": "run-demo-001",
        "correlation_id": "corr-demo-001",
        "decision_basis": [
            "phase_contract:phase-contract-motor-023@v1",
            "rights_profile:src-demo-001@rights-v1",
            "access_class:src-demo-001:internal@access-v1",
            "execution_policy:policy-internal-read@policy-v1",
        ],
    },
    "policy_violation_event": None,
    "conditional_execution_requirement": None,
    "access_audit_record": {
        "result_status": "allow",
        "actor_id": "orchestrator",
        "motor_id": "motor_023",
        "target_ref": "source:src-demo-001",
        "run_id": "run-demo-001",
        "correlation_id": "corr-demo-001",
    },
}
```

## notes
La decisión no ejecuta la acción solicitada; solo autoriza, deniega o condiciona la ejecución. Si una regla `deny` coincide, si falta un contrato de fase vigente, si el `rights_profile` no enlaza con `target_ref` o si la política aplicable exige evidencia externa, el resultado cambia de forma determinista a `deny` o `conditional` con razón estructurada.
