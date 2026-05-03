# Legacy Governance Directory Disposition — Latest

Produced at: 2026-05-03

## Purpose

This document fixes the correct handling of the preserved legacy governance directories for `motor_018` and `motor_019`.

It exists to prevent future cleanup work from deleting historical closure evidence just because the current catalog names are already reconciled.

## Current legacy dirs

The preserved historical directories are:

- `governanza/validation-data-bridge_018`
- `governanza/verification-bridge-engine_019`

Current catalog-aligned directories also exist:

- `governanza/chart-generation-engine_018`
- `governanza/llm-writing-engine_019`

## Current interpretation

The reconciliation snapshot already treats the current state correctly:

- both motors are `aligned_closed`;
- current catalog identity mismatch count is `0`;
- these legacy dirs are preserved history, not active mismatches.

## Measured historical payload

Each preserved legacy dir currently contains `22` files.

They retain a full historical documentary chain, including:

- `motor_state.json`
- `documentation_base/*`
- `schema_technical/technical_schema.md`
- `tests/test_spec.md`
- `failure_modes/failure_modes_spec.md`
- `implementation/codebase/*`
- `implementation/usage_example.md`
- `conformance_review/conformance_review_report.json`

They also contain local `__pycache__` residue under `implementation/codebase/`, which should not be treated as historical evidence.

## Correct disposition now

The correct current disposition is:

1. preserve both legacy dirs during the first versioning wave
2. include them as historical governance residue, not as active framework source
3. rely on `.gitignore` to suppress their `__pycache__` residue
4. do not rename, delete or archive them in the same pass that versions the main runtime closure

## Why preservation is safer than immediate archival

Immediate archival is not the safest first move because:

- the runtime/governance closure was only just reconciled;
- the root repository still needs a clean first source-of-truth versioning pass;
- the snapshot already neutralizes the historical mismatch at interpretation level;
- and a separate archival pass later will be easier to review than mixing closure versioning with historical reshaping.

## Recommended later options

Only after the main source-of-truth versioning wave is stable should one of these be chosen:

1. keep the legacy dirs in place indefinitely as explicit historical residue
2. move them into a clearly named archival location in a separate commit
3. compress or externalize them only if their closure evidence is preserved elsewhere with traceability

## Do not do this

- do not delete the legacy dirs because the current names already exist
- do not treat them as active catalog conflicts
- do not mix their archival with the first source-of-truth commit of the reconciled framework
