# Asset Pattern Library

Versioned, asset-family-specific knowledge that the framework consumes
**as a read-only library**. The library does not know which asset is being
analyzed; consumers (Layer B / Layer F motors) load it and pick the slice
they need.

## File layout

```
patterns/
  warehouse_distribution.json
  manufacturing_facility.json
  commercial_building.json
  datacenter.json
  logistics_terminal.json
  README.md   ← this file
```

## Schema

Each file is a JSON object with this shape:

```json
{
  "asset_family": "<canonical id>",
  "library_version": "<SemVer>",
  "last_validated_at": "<ISO date>",
  "concept_markers": ["dock", "charging", ...],
  "axes": {
    "<axis name>": {
      "concept_markers": ["..."],
      "falsifiers": ["..."]
    }
  }
}
```

### Fields

- `asset_family` — canonical id used in `target_definition_contract.target_type`.
- `library_version` — SemVer. Bumping major triggers regression on the last
  50 reports (RECOVERY_BACKLOG.md R-37).
- `last_validated_at` — ISO date of last manual review.
- `concept_markers` — flat list of asset-specific tokens. Used by
  Gold Nugget Quality Validator (motor_057) to detect archetype-replay
  nuggets. Lower-case, can be multi-word.
- `axes` — optional structured grouping by analytical axis (e.g. `tariff`,
  `thermal`, `boundary`). Each axis can carry its own concept_markers and
  falsifiers.

## Adding a pattern

1. Edit the relevant `<asset_family>.json` file.
2. Bump `library_version` per SemVer rules.
3. Update `last_validated_at`.
4. Run `pytest -q runtime-orchestrator/tests/test_pattern_library.py`.
5. Open a PR — CI will replay the last N reports for regression
   (RECOVERY_BACKLOG.md F8).

## Adding a new asset family

1. Create `<new_family>.json` following the schema above.
2. Add the family to `runtime-orchestrator/src/runtime_orchestrator/adapters/motor_057.py`
   token-table fallback (kept for backward-compat).
3. Open a PR.

## Why a separate JSON library

The pattern library used to live inside `executive_thesis.py` as a Python
dict (`_CONCEPT_MARKER_MAP`). That made it asset-specific and drifted with
the composer. The recovery moves it here so:

- the library can be versioned independently
- motor_057 (Gold Nugget Quality Validator) can rely on it as ground truth
- non-Python contributors can edit patterns
- regression CI can diff library changes against historical reports
