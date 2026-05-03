# Conceptual Schema — System Consistency Validator

Motor ID: motor_036

## validator_model

The validator operates as a critical check matrix.

Every consistency rule becomes one row in `consistency_register`:

- `check_id`: stable semantic identifier of the rule;
- `passed`: whether the package satisfies the rule;
- `severity`: currently important because only critical failures block render;
- `message`: why the rule failed or what it protects;
- `location`: which upstream surface or report surface the rule refers to.

The validator therefore acts less like a scorer and more like an executable admissibility ledger.

## failure_projection

Two derivative outputs are built from the same check matrix:

- `critical_failures`: only critical failed rows;
- `blocking_reason_register`: same blocking set, preserved as a render-facing reason surface.

This means every render block must be traceable back to a named check in `consistency_register`.

## state_projection

The validator also emits a minimal `canonical_report_state`:

- `document_visible_type`
- `canonical_asset_context_state`
- `screening_supported`

This is not a substitute for the full report package. It is the compact state needed to understand what kind of document the validator believes it is checking.

## check_families

The checks span several families:

1. executive thesis and outline integrity;
2. claim summary and claim-contract coherence;
3. client-facing body vs appendix separation;
4. report-mode and classifier alignment;
5. asset identity and source-coverage integrity;
6. structural and congruence discipline;
7. declared-input, entity-resolution and case-isolation protection.

The motor is complete only when all of these families can be validated off the authoritative upstream registers without hidden local state.
