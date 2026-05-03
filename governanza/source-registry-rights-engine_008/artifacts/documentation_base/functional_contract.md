# Functional Contract — Source Registry + Rights Engine

Motor ID: motor_008

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Registrar fuentes, licencias, restricciones, clase de acceso, periodicidad y uso permitido.
why_it_exists:  Sin este motor no hay control serio de fuentes públicas, premium o restringidas.
key_inputs:     source declarations, license files, access agreements
key_outputs:    source_registration, rights_profile, access_class, refresh_schedule
key_objects:    SourceRecord, RightsProfile, AccessClass
what_not_to_do: No ingesta datos. No evalúa calidad. Solo registra metadatos de fuentes y derechos.
design_notes:   Depende de motor_001. Puede construirse temprano en paralelo con el pipeline de normalización.
-->

## inputs
- source_declarations: list[SourceDeclaration] — originador humano, sistema de adquisición o catálogo institucional que declara una fuente candidata.
- license_files: list[LicenseDocumentRef] — archivo local, URI documental o referencia contractual que describe licencia, términos de uso o condiciones legales.
- access_agreements: list[AccessAgreementRef] — contrato, convenio, suscripción, credencial aprobada o documento de acceso asociado a una fuente.

## outputs
- source_registration: SourceRecord — registro gobernado para motores de ingesta, refresh, duplicados, curación y reporting.
- rights_profile: RightsProfile — perfil de permisos y restricciones consumible por ingesta, composición de reportes, gobernanza y revisión de conformidad.
- access_class: AccessClass — clasificación determinista de acceso para orquestación, operación y validaciones de uso permitido.
- refresh_schedule: RefreshSchedule — cadencia de revisión o recaptura documental para Source Change Detection / Refresh Intelligence Engine.

## limits
- No acepta registros de datos, filas parseadas, documentos raw de investigación ni payloads de fuente como material a ingerir.
- No acepta una fuente sin identificador estable, localizador o propietario declarado.
- No acepta licencia o acuerdo sin referencia documental, fecha de observación y provenance mínima.
- No produce datasets, parsed records, normalized records, quality scores, identity matches, inference records ni output blocks.
- No declara que una fuente es verdadera, completa, confiable o analíticamente apta.
- No transforma permisos ambiguos en permisos concedidos; si el derecho de uso no es explícito, el output debe restringir o bloquear el uso.

## validations
- Rechaza `source_declarations` sin `source_id`, `source_name`, `source_locator`, `declared_owner` o `declared_use`.
- Rechaza una fuente cuando no existe al menos una referencia documental trazable en `license_files` o `access_agreements`.
- Rechaza documentos de licencia con fecha de vigencia inválida, `observed_at` ausente o `document_ref` vacío.
- Verifica que todo `RightsProfile` tenga `source_id`, `license_basis`, `permitted_uses`, `prohibited_uses`, `restriction_notes` y `rights_status`.
- Verifica que todo `AccessClass` tenga un valor permitido, una razón de asignación y una referencia al documento que justifica la clasificación.
- Verifica que `refresh_schedule` incluya periodicidad, próxima fecha de revisión o condición explícita de revisión manual.
- Emite output solo si `source_registration`, `rights_profile`, `access_class` y `refresh_schedule` comparten el mismo `source_id` y preservan provenance documental.
