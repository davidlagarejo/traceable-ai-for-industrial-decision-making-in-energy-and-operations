# Usage Example — Public Data Engine

Motor ID: motor_012

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Materializar Fase 1 y producir facility_prior y bundles contextuales listos para Fase 2.
why_it_exists:  Convierte infraestructura base en output útil de Fase 1.
key_inputs:     library_objects (motor_011), source_registry (motor_008), quality_records (motor_007)
key_outputs:    facility_prior, contextual_bundle, phase1_package
key_objects:    FacilityPrior, ContextualBundle, Phase1Package
what_not_to_do: No hace inferencias. No produce TADs. Solo empaqueta el prior de Fase 1.
design_notes:   Materialización final de Fase 1. Depende de toda la infraestructura base.

All implementation-stage placeholders have been replaced with concrete content.
-->

## example
El orquestador invoca `PublicDataEngine` al cerrar Fase 1 para `facility_alpha`, usando dos objetos curados por `motor_011`, el snapshot de fuentes autorizado por `motor_008` y dos registros de calidad emitidos por `motor_007`. El motor valida que las fuentes resuelvan, que la curación permita reutilización y que cada objeto incluido tenga provenance, lineage, versión y referencia de calidad. El resultado esperado es un prior de facility, un bundle contextual mínimo y un paquete de handoff sin TADs, inferencias ni conclusiones.

## inputs_used
```python
library_objects = [
    {
        "library_object_id": "lib_obj_facility_profile_v1",
        "facility_ref": "facility_alpha",
        "source_refs": ["src_100"],
        "version": "1.0.0",
        "curation_status": "eligible_for_reuse",
        "provenance": ["prov_lib_100"],
        "lineage_refs": ["lin_lib_100"],
        "source_ref": "curated_bundle_facility_alpha_v1",
    },
    {
        "library_object_id": "lib_obj_utility_context_v1",
        "facility_ref": "facility_alpha",
        "source_refs": ["src_205"],
        "version": "1.0.0",
        "curation_status": "eligible_for_reuse",
        "provenance": ["prov_lib_205"],
        "lineage_refs": ["lin_lib_205"],
        "source_ref": "curated_bundle_facility_alpha_v1",
    },
]

source_registry = {
    "source_registry_snapshot_ref": "src_registry_snapshot_2026_04_01",
    "entries": [
        {
            "source_id": "src_100",
            "rights_profile_id": "rights_src_100",
            "refresh_schedule_id": "refresh_src_100",
            "evidence_refs": ["license_src_100"],
            "lineage_refs": ["lin_src_100"],
            "source_ref": "source_registration_src_100",
        },
        {
            "source_id": "src_205",
            "rights_profile_id": "rights_src_205",
            "refresh_schedule_id": "refresh_src_205",
            "evidence_refs": ["license_src_205"],
            "lineage_refs": ["lin_src_205"],
            "source_ref": "source_registration_src_205",
        },
    ],
}

quality_records = [
    {
        "quality_record_id": "qr_100",
        "target_ref": "lib_obj_facility_profile_v1",
        "fitness_status": "usable",
        "score_or_grade": "pass",
        "evaluation_provenance": ["eval_run_100"],
        "lineage_refs": ["lin_qr_100"],
        "source_ref": "quality_eval_src_100",
    },
    {
        "quality_record_id": "qr_205",
        "target_ref": "lib_obj_utility_context_v1",
        "fitness_status": "usable",
        "score_or_grade": "pass",
        "evaluation_provenance": ["eval_run_205"],
        "lineage_refs": ["lin_qr_205"],
        "source_ref": "quality_eval_src_205",
    },
]

packaging_config = {
    "facility_ref": "facility_alpha",
    "prior_scope": "facility",
    "package_scope": "facility_alpha_phase1",
    "package_version": "facility_alpha_phase1_v1",
    "packaging_run_id": "pkg_run_012_0001",
    "eligibility_rule_version": "pde_rules_v1",
    "bundle_rule_version": "pde_bundle_v1",
    "packaging_rule_version": "pde_package_v1",
    "context_scope": "minimal_prior",
    "produced_at": "2026-04-01T00:00:00Z",
    "input_snapshot_refs": {
        "library_objects_snapshot": "library_snapshot_2026_04_01",
        "source_registry_snapshot": "src_registry_snapshot_2026_04_01",
        "quality_records_snapshot": "quality_snapshot_2026_04_01",
    },
}
```

## expected_output
```python
{
    "status": "accepted",
    "facility_prior": {
        "produced_by_motor": "motor_012",
        "facility_ref": "facility_alpha",
        "prior_scope": "facility",
        "library_object_refs": [
            "lib_obj_facility_profile_v1",
            "lib_obj_utility_context_v1",
        ],
        "source_refs": ["src_100", "src_205"],
        "source_registry_snapshot_ref": "src_registry_snapshot_2026_04_01",
        "quality_record_refs": ["qr_100", "qr_205"],
        "contextual_bundle_refs": ["contextual_bundle_<deterministic_hash>"],
        "input_snapshot_refs": {
            "library_objects_snapshot": "library_snapshot_2026_04_01",
            "source_registry_snapshot": "src_registry_snapshot_2026_04_01",
            "quality_records_snapshot": "quality_snapshot_2026_04_01",
        },
        "exclusion_record_refs": [],
        "provenance_refs": [
            "eval_run_100",
            "eval_run_205",
            "license_src_100",
            "license_src_205",
            "prov_lib_100",
            "prov_lib_205",
        ],
        "lineage_refs": [
            "library_snapshot_2026_04_01",
            "quality_snapshot_2026_04_01",
            "src_registry_snapshot_2026_04_01",
            "lin_lib_100",
            "lin_lib_205",
            "lin_qr_100",
            "lin_qr_205",
            "lin_src_100",
            "lin_src_205",
        ],
        "version_id": "version_<deterministic_hash>",
        "version_hash": "<deterministic_sha256>",
    },
    "contextual_bundle": [
        {
            "produced_by_motor": "motor_012",
            "facility_prior_ref": "facility_prior_<deterministic_hash>",
            "facility_ref": "facility_alpha",
            "context_scope": "minimal_prior",
            "library_object_refs": [
                "lib_obj_facility_profile_v1",
                "lib_obj_utility_context_v1",
            ],
            "source_refs": ["src_100", "src_205"],
            "quality_record_refs": ["qr_100", "qr_205"],
            "bundle_rule_version": "pde_bundle_v1",
            "exclusion_record_refs": [],
        }
    ],
    "phase1_package": {
        "produced_by_motor": "motor_012",
        "package_scope": "facility_alpha_phase1",
        "package_version": "facility_alpha_phase1_v1",
        "facility_prior_ref": "facility_prior_<deterministic_hash>",
        "contextual_bundle_refs": ["contextual_bundle_<deterministic_hash>"],
        "validation_status": "accepted",
        "rejection_refs": [],
        "packaging_run_id": "pkg_run_012_0001",
        "packaging_rule_version": "pde_package_v1",
        "generated_at": "2026-04-01T00:00:00Z",
    },
    "packaging_rejection": [],
}
```

## notes
El ejemplo presupone que `src_registry_snapshot_2026_04_01`, `library_snapshot_2026_04_01` y `quality_snapshot_2026_04_01` ya fueron producidos por motores upstream y no son creados por `motor_012`. Si un objeto curado referencia una fuente ausente, carece de provenance/lineage, tiene `curation_status` no reutilizable o contiene campos de inferencia como `tad_status`, el motor debe emitir `PackagingRejection` y no reparar el registro silenciosamente.
