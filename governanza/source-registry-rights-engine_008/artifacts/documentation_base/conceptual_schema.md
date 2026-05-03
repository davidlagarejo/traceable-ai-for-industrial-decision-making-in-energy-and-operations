# Conceptual Schema — Source Registry + Rights Engine

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

## entities
- SourceRecord: representa una fuente registrada con identidad estable, propietario, localizador, tipo, provenance documental y estado registral.
- RightsProfile: representa el conjunto de permisos, prohibiciones, obligaciones y restricciones legales o contractuales aplicables a una fuente.
- AccessClass: representa la clasificación operativa de acceso que determina si una fuente es pública, premium, restringida, contractual, interna o bloqueada.

## relationships
- SourceRecord → RightsProfile (cada fuente registrada debe tener exactamente un perfil de derechos vigente para uso operativo).
- SourceRecord → AccessClass (cada fuente registrada debe tener exactamente una clase de acceso vigente derivada de licencia y acuerdos).
- RightsProfile → AccessClass (restricciones, permisos y obligaciones del perfil justifican la clase de acceso asignada).
- SourceRecord → source_registration output (el registro de fuente es la representación emitida del SourceRecord vigente).
- RightsProfile → rights_profile output (el perfil emitido conserva referencias a licencia, acuerdo y provenance documental).
- AccessClass → access_class output (la clase emitida conserva razón de asignación y estado de uso permitido).
- SourceRecord → refresh_schedule output (la periodicidad de revisión queda vinculada al identificador de fuente y a la razón de refresh).

## key_fields
SourceRecord:
- source_id: string
- source_name: string
- source_locator: string
- declared_owner: string
- registration_status: enum[active, restricted, blocked, retired]

RightsProfile:
- rights_profile_id: string
- source_id: string
- license_basis: string
- permitted_uses: list[string]
- prohibited_uses: list[string]

AccessClass:
- access_class_id: string
- source_id: string
- access_class: enum[public, premium, restricted, contractual, internal, blocked]
- assignment_reason: string
- effective_from: date
