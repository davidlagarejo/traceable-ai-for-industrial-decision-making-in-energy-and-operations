# Usage Example — Dataset / Object Test Harness Engine

Motor ID: motor_021

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Correr pruebas sobre datasets, handoffs, contratos y objetos del sistema.
why_it_exists:  Los motores pueden pasar solos y aun así fallar juntos en integración.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003), normalized_records (motor_005), identity_records (motor_006), quality_records (motor_007)
key_outputs:    test_result, harness_report, integration_failure_log
key_objects:    TestResult, HarnessReport, IntegrationFailure
what_not_to_do: No modifica datos. No produce outputs analíticos. Solo prueba y reporta.
design_notes:   Harness transversal. Prueba el sistema integrado, no motores individuales.

Implementation-stage usage example completed for Gate 5 review.
-->

## example
Un operador de integracion ejecuta `DatasetObjectTestHarnessEngine` despues de que los motores 001, 002, 003, 005, 006 y 007 producen sus handoffs para el dataset `DS-55`. El harness recibe el contrato aprobado, el version record, la taxonomia canonica, un normalized record, una identidad resuelta y su quality record; debe reportar si el lote integrado puede pasar como consistente sin modificar ningun objeto fuente.

## inputs_used
```python
from codebase import DatasetObjectTestHarnessEngine

engine = DatasetObjectTestHarnessEngine()
output = engine.run(
    phase_contracts=[
        {
            "contract_id": "PC-001-normalized-handoff",
            "phase_id": "normalization",
            "required_outputs": ["normalized_record"],
            "field_requirements": [
                "record_id",
                "dataset_id",
                "taxonomy_refs",
                "version_ref",
                "lineage_refs",
            ],
            "handoff_rules": {"requires_quality_record": True},
            "version": "1.0.0",
            "status": "approved",
            "provenance_refs": ["PROV-PC-001"],
        }
    ],
    version_records=[
        {
            "version_id": "VR-002-NR-884-v1",
            "object_id": "NR-884",
            "object_type": "normalized_record",
            "object_version": 1,
            "lineage_refs": ["LN-SRC-12", "LN-NORM-884"],
            "provenance_refs": ["PROV-NR-884"],
            "created_at": "2026-04-18T00:00:00Z",
            "change_reason": "initial_normalization",
        }
    ],
    canonical_taxonomy={
        "taxonomy_id": "TAX-003-main",
        "taxonomy_version": "2026.04",
        "allowed_terms": ["sector.energy", "geography.us.tx"],
        "object_type_registry": ["normalized_record", "identity_record", "quality_record"],
        "relationship_types": ["describes_entity"],
        "status": "active",
        "effective_at": "2026-04-01T00:00:00Z",
        "provenance_refs": ["PROV-TAX-003"],
    },
    normalized_records=[
        {
            "record_id": "NR-884",
            "dataset_id": "DS-55",
            "schema_ref": "PC-001-normalized-handoff",
            "field_values": {"entity_ref": "supplier:acme-grid", "amount": 1200},
            "taxonomy_refs": ["sector.energy", "geography.us.tx"],
            "version_ref": "VR-002-NR-884-v1",
            "lineage_refs": ["LN-SRC-12", "LN-NORM-884"],
            "normalized_at": "2026-04-18T00:05:00Z",
            "provenance_refs": ["PROV-NR-884"],
        }
    ],
    identity_records=[
        {
            "identity_id": "ID-006-ENT-17",
            "entity_ref": "supplier:acme-grid",
            "canonical_entity_id": "ENT-17",
            "alias_refs": ["ACME Grid"],
            "confidence_policy_ref": "CP-006-default",
            "lineage_refs": ["LN-ID-17"],
            "version_ref": "VR-002-ID-17-v2",
            "resolved_at": "2026-04-18T00:06:00Z",
        }
    ],
    quality_records=[
        {
            "quality_record_id": "QR-007-NR-884",
            "subject_ref": "NR-884",
            "phase_contract_ref": "PC-001-normalized-handoff",
            "evaluation_status": "pass",
            "quality_flags": [],
            "fitness_score": 0.97,
            "evaluated_at": "2026-04-18T00:07:00Z",
            "version_ref": "VR-002-QR-884-v1",
            "provenance_refs": ["PROV-QR-884"],
        }
    ],
    executed_at="2026-04-18T00:10:00Z",
)
```

## expected_output
```python
{
    "test_result": [
        {"case_name": "contract_required_fields_present", "status": "pass", "severity": "info", "failure_ids": []},
        {"case_name": "version_ref_resolves", "status": "pass", "severity": "info", "failure_ids": []},
        {"case_name": "taxonomy_refs_allowed", "status": "pass", "severity": "info", "failure_ids": []},
        {"case_name": "identity_ref_resolves", "status": "pass", "severity": "info", "failure_ids": []},
        {"case_name": "quality_record_present", "status": "pass", "severity": "info", "failure_ids": []},
    ],
    "harness_report": {
        "status": "pass",
        "tested_contract_refs": ["PC-001-normalized-handoff"],
        "tested_object_refs": [
            "ID-006-ENT-17",
            "NR-884",
            "QR-007-NR-884",
            "TAX-003-main:2026.04",
            "VR-002-NR-884-v1",
        ],
        "result_counts": {"pass": 5, "warning": 0, "fail": 0, "skipped": 0},
        "failure_ids": [],
        "failure_log_ref": None,
        "produced_by_motor": "motor_021",
    },
    "integration_failure_log": [],
}
```

## notes
El ejemplo presupone que los contratos estan aprobados para prueba y que el snapshot de taxonomia recibido es la autoridad vigente para el lote. El motor solo prueba y reporta: no corrige `schema_ref`, no crea version records, no remapea terminos, no fusiona identidades y no cambia quality scores; cualquier falla se expresa como `IntegrationFailure` con owner sugerido para el motor productor.
