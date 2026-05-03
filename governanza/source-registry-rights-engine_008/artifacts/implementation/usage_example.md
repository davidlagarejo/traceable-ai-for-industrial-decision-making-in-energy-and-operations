# Usage Example — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.

All implementation-stage placeholders have been resolved for Gate 5 review.
-->

## example
Un operador de registro declara la fuente `src_eia_api` antes de que cualquier motor de ingesta pueda usarla. Motor_008 recibe la declaración, una referencia documental de licencia y una referencia de acuerdo de acceso para registrar la fuente, derivar un perfil de derechos, asignar clase de acceso y fijar una revisión mensual. El resultado esperado habilita uso público con atribución y API key, sin descargar datos ni evaluar calidad de la fuente.

## inputs_used
```json
{
  "phase_contract_ref": "phase_contract:motor_001:research_registry:v1",
  "emitted_at": "2026-04-01T10:05:00Z",
  "source_declarations": [
    {
      "source_id": "src_eia_api",
      "source_name": "U.S. Energy Information Administration API",
      "source_locator": "https://api.eia.gov",
      "source_type": "api",
      "declared_owner": "U.S. Energy Information Administration",
      "declared_use": "public_contextual_energy_data",
      "declared_refresh": "monthly",
      "declaration_ref": "declarations/src_eia_api_2026-04-01.json",
      "submitted_by": "source_registry_operator",
      "submitted_at": "2026-04-01T10:00:00Z"
    }
  ],
  "license_files": [
    {
      "license_ref_id": "lic_eia_terms_20260401",
      "source_id": "src_eia_api",
      "document_ref": "licenses/eia_terms_2026-04-01.pdf",
      "license_basis": "public government terms with attribution requirement",
      "permitted_uses": ["analysis", "reporting", "derived_metadata"],
      "prohibited_uses": ["misattribution", "source_impersonation"],
      "restriction_notes": "Attribution to EIA required; no claim of EIA endorsement.",
      "attribution_requirements": ["cite U.S. Energy Information Administration"],
      "effective_from": null,
      "effective_to": null,
      "observed_at": "2026-04-01T09:30:00Z"
    }
  ],
  "access_agreements": [
    {
      "agreement_ref_id": "agr_eia_api_key_20260401",
      "source_id": "src_eia_api",
      "document_ref": "agreements/eia_api_key_terms_2026-04-01.pdf",
      "access_basis": "public API key registration",
      "authentication_required": true,
      "payment_required": false,
      "quota_notes": "API key rate limit applies according to public terms.",
      "embargo_until": null,
      "territorial_restrictions": [],
      "permitted_uses": ["analysis", "reporting", "derived_metadata"],
      "prohibited_uses": ["credential_sharing"],
      "effective_from": "2026-04-01",
      "effective_to": null,
      "observed_at": "2026-04-01T09:40:00Z"
    }
  ]
}
```

## expected_output
```json
{
  "status": "accepted",
  "source_registration": {
    "source_id": "src_eia_api",
    "source_name": "U.S. Energy Information Administration API",
    "source_locator": "https://api.eia.gov",
    "source_type": "api",
    "declared_owner": "U.S. Energy Information Administration",
    "declared_use": "public_contextual_energy_data",
    "declared_refresh": "monthly",
    "registration_status": "active",
    "registration_reason": "Registered with allowed_with_attribution rights and public access classification.",
    "declaration_ref": "declarations/src_eia_api_2026-04-01.json",
    "evidence_refs": ["lic_eia_terms_20260401", "agr_eia_api_key_20260401"],
    "rights_profile_id": "rights_src_eia_api",
    "access_class_id": "access_src_eia_api",
    "refresh_schedule_id": "refresh_src_eia_api",
    "phase_contract_ref": "phase_contract:motor_001:research_registry:v1",
    "produced_by_motor": "motor_008",
    "parent_id": null
  },
  "rights_profile": {
    "rights_profile_id": "rights_src_eia_api",
    "source_id": "src_eia_api",
    "license_basis": "public government terms with attribution requirement",
    "license_document_refs": ["lic_eia_terms_20260401"],
    "agreement_refs": ["agr_eia_api_key_20260401"],
    "permitted_uses": ["analysis", "reporting", "derived_metadata"],
    "prohibited_uses": ["misattribution", "source_impersonation", "credential_sharing"],
    "restriction_notes": "Attribution to EIA required; no claim of EIA endorsement. | quota: API key rate limit applies according to public terms.",
    "attribution_requirements": ["cite U.S. Energy Information Administration"],
    "rights_status": "allowed_with_attribution",
    "effective_from": "2026-04-01",
    "effective_to": null,
    "evidence_observed_at": "2026-04-01T09:40:00Z",
    "phase_contract_ref": "phase_contract:motor_001:research_registry:v1",
    "produced_by_motor": "motor_008",
    "parent_id": null
  },
  "access_class": {
    "access_class_id": "access_src_eia_api",
    "source_id": "src_eia_api",
    "rights_profile_id": "rights_src_eia_api",
    "access_class": "public",
    "assignment_reason": "Rights evidence permits use without payment, contract, embargo, or territorial restriction.",
    "supporting_document_refs": ["lic_eia_terms_20260401", "agr_eia_api_key_20260401"],
    "authentication_required": true,
    "payment_required": false,
    "quota_notes": "API key rate limit applies according to public terms.",
    "embargo_until": null,
    "territorial_restrictions": [],
    "effective_from": "2026-04-01",
    "effective_to": null,
    "phase_contract_ref": "phase_contract:motor_001:research_registry:v1",
    "produced_by_motor": "motor_008",
    "parent_id": null
  },
  "refresh_schedule": {
    "refresh_schedule_id": "refresh_src_eia_api",
    "source_id": "src_eia_api",
    "periodicity": "monthly",
    "next_review_at": "2026-05-01",
    "manual_review_condition": null,
    "refresh_reason": "Declared source refresh cadence is monthly.",
    "schedule_basis_refs": [
      "declarations/src_eia_api_2026-04-01.json",
      "lic_eia_terms_20260401",
      "agr_eia_api_key_20260401"
    ],
    "phase_contract_ref": "phase_contract:motor_001:research_registry:v1",
    "produced_by_motor": "motor_008",
    "parent_id": null
  },
  "validation_errors": []
}
```

## notes
Precondición: `phase_contract:motor_001:research_registry:v1` debe existir como contrato de fase autorizado. El motor acepta el registro porque hay una declaración de fuente completa, evidencia documental trazable con `document_ref` y `observed_at`, permisos explícitos, restricciones preservadas y una cadencia de revisión. Este ejemplo no ingesta registros desde la API, no prueba disponibilidad de endpoints, no genera score de calidad y no emite outputs de normalización, identidad, inferencia o reporting.
