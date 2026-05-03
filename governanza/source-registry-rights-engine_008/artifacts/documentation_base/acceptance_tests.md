# Acceptance Tests — Source Registry + Rights Engine

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

## happy_path
Input: `source_declarations` contains `source_id = "src_eia_api"`, `source_name = "U.S. Energy Information Administration API"`, `source_locator = "https://api.eia.gov"`, `declared_owner = "U.S. Energy Information Administration"`, `declared_use = "public contextual energy data"`, and `declared_refresh = "monthly"`. `license_files` contains `document_ref = "licenses/eia_terms_2026-04-01.pdf"`, `license_basis = "public government terms"`, `permitted_uses = ["analysis", "reporting", "derived_metadata"]`, `prohibited_uses = ["misattribution"]`, and `observed_at = "2026-04-01"`. `access_agreements` states `authentication_required = true` and `payment_required = false`.

Action: the motor validates required fields, links license and access references to `src_eia_api`, assigns the rights profile and computes the access class.

Expected output: `source_registration.source_id = "src_eia_api"`, `rights_profile.rights_status = "allowed_with_attribution"`, `access_class.access_class = "public"`, and `refresh_schedule.periodicity = "monthly"` with provenance pointing to the declaration and license document.

## edge_cases
- Publicly visible source with unclear reuse terms: if a source declaration has a public URL but no license file or access agreement, the motor rejects registration with `MISSING_RIGHTS_EVIDENCE` instead of assuming open use.
- Premium database with narrow contractual access: if an agreement allows internal analysis but prohibits redistribution, the motor emits `access_class = "contractual"` and a `RightsProfile` with reporting or redistribution listed in `prohibited_uses`.
- Expired agreement with otherwise complete metadata: if `effective_to` is earlier than the registration date, the motor emits an error `EXPIRED_ACCESS_AGREEMENT` and does not produce an allowed access class.
- Source with event-driven updates rather than fixed cadence: if no periodic interval is valid but the source publishes revision notices, the motor emits a `refresh_schedule` with `manual_review_condition = "on_source_revision_notice"`.

## rejection_criteria
- Reject with `MISSING_SOURCE_ID` when a source declaration lacks `source_id` or uses an empty identifier.
- Reject with `MISSING_RIGHTS_EVIDENCE` when neither a license reference nor an access agreement reference is attached to the source.
- Reject with `RIGHTS_CONFLICT` when one document permits external redistribution and another active agreement prohibits it without a precedence rule.
- Reject with `INVALID_ACCESS_CLASS` when the computed class is outside the allowed access class vocabulary.
- Reject with `UNTRACEABLE_DOCUMENT_REF` when a license or agreement lacks `document_ref` or `observed_at`.
