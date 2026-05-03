# Technical Schema — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## entities
- `ArchetypeResolution`: primary selection object that names the chosen archetype, confidence level, resolver state, evidence-state of the selection, and why that archetype was chosen.
- `ArchetypeDefinition`: canonical library snapshot for the selected archetype. It describes business function, value-creation logic, dominant drivers, control structure, constraint structure, regulatory exposure, and the minimum evidence required to falsify or strengthen the prior.
- `ArchetypeSelectionBasis`: one observed basis row used to justify the selection, such as target type, target classification, jurisdiction scope, tower-scale signals, process clues, or utility-heavy clues.
- `DominantVariableHypothesis`: one structural prior about a variable that may dominate the case, including what would confirm it, what would falsify it, and how it would change decisions.
- `EvidenceBoundField`: one system-abstraction seed field emitted with an explicit evidence state, falsification condition, and minimum evidence required.
- `SystemAbstractionSeed`: dict-shaped envelope of evidence-bound structural fields that downstream structural-intelligence motors consume.
- `AntiHallucinationContract`: explicit usage rule stating that the archetype is an `ARCHETYPAL_PRIOR` or `INADMISSIBLE_CLAIM`, and forbidding decision closure, ROI, savings, or final redesign use.
- `ArchetypeResolverSurface`: flattened adapter-facing summary that republishes the selected archetype ID/label, match confidence, resolver state, and dominant-variable count.

## fields
`ArchetypeResolution`
- `selected_archetype_id: str` (required) — stable library key such as `commercial_office_tower_nyc`, `manufacturing_laminate`, or `target_not_yet_structurally_modelable`.
- `label: str` (required) — human-readable label of the selected archetype.
- `match_confidence: str` (required) — bounded confidence such as `high`, `medium`, or `low`.
- `resolver_state: str` (required) — resolver path like `selected`, `fallback_generic`, `fallback_unresolved`, or `non_operating_or_unresolved_target`.
- `archetype_evidence_state: str` (required) — `ARCHETYPAL_PRIOR` when modelable, `INADMISSIBLE_CLAIM` when not yet structurally modelable.
- `why_selected: str` (required) — bounded explanation of why the archetype was chosen.
- `selection_basis_register: list[dict]` (required) — observed bases that justified the selection.

`ArchetypeDefinition`
- `archetype_id: str` (required)
- `label: str` (required)
- `asset_type: str` (required)
- `business_function: str` (required)
- `value_creation_mechanism: str` (required)
- `dominant_process_type: str` (required)
- `dominant_physical_drivers: list[str]` (required)
- `dominant_operational_drivers: list[str]` (required)
- `control_structure: str` (required)
- `constraint_structure: str` (required)
- `economic_driver: str` (required)
- `regulatory_exposure: str` (required)
- `critical_systems: list[str]` (required)
- `operational_risks: list[str]` (required)
- `regulatory_risks: list[str]` (required)
- `relevant_metrics: list[str]` (required)
- `comparable_lenses: list[str]` (required)
- `minimum_evidence_required: list[str]` (required)
- `dominant_variable_hypotheses: list[dict]` (required)

`ArchetypeSelectionBasis`
- `dimension: str` (required) — basis dimension such as `target_type`, `target_classification`, `jurisdiction_scope`, or a bounded clue class.
- `value: str` (required)
- `evidence_state: str` (required) — currently expected to be based on observed routing facts rather than final local truth.
- `source: str` (required) — bounded origin of the basis.

`DominantVariableHypothesis`
- `variable: str` (required)
- `layer: str` (required) — structural layer such as `physical`, `operation`, `control`, `regulation`, `finance`, or `maintenance`.
- `dominance: str` (required)
- `evidence_state: str` (required)
- `why_it_could_matter: str` (required)
- `what_confirms_it: list[str]` (required)
- `what_falsifies_it: list[str]` (required)
- `decision_impact: list[str]` (required)

`EvidenceBoundField`
- `field_name: str` (required)
- `value: Any` (required)
- `evidence_state: str` (required)
- `falsification_condition: str` (required)
- `minimum_evidence_required: list[str]` (required)

`SystemAbstractionSeed`
- `asset_type: dict` (required)
- `business_function: dict` (required)
- `value_creation_mechanism: dict` (required)
- `dominant_process_type: dict` (required)
- `dominant_physical_drivers: dict` (required)
- `dominant_operational_drivers: dict` (required)
- `control_structure: dict` (required)
- `constraint_structure: dict` (required)
- `economic_driver: dict` (required)
- `regulatory_exposure: dict` (required)
- `evidence_maturity: dict` (required)

`AntiHallucinationContract`
- `selected_archetype_evidence_state: str` (required)
- `rule: str` (required)
- `allowed_use: list[str]` (required)
- `prohibited_use: list[str]` (required)

`ArchetypeResolverSurface`
- `selected_archetype_id: str` (required)
- `selected_archetype_label: str` (required)
- `match_confidence: str` (required)
- `resolver_state: str` (required)
- `dominant_variable_count: int` (required)

## relationships
- `ArchetypeResolution.selected_archetype_id` selects exactly one `ArchetypeDefinition` from the bounded in-code `ARCHETYPE_LIBRARY`.
- `ArchetypeResolution.selection_basis_register[]` contains serialized `ArchetypeSelectionBasis` rows explaining the route to that selection.
- `ArchetypeDefinition.dominant_variable_hypotheses[]` contains zero or more `DominantVariableHypothesis` rows; unresolved targets must emit none.
- `SystemAbstractionSeed` is derived directly from the selected `ArchetypeDefinition` and wrapped as `EvidenceBoundField` rows.
- `ArchetypeResolverSurface.selected_archetype_id`, `selected_archetype_label`, `match_confidence`, and `resolver_state` are flattened projections of `ArchetypeResolution`.
- `AntiHallucinationContract.selected_archetype_evidence_state` must mirror `ArchetypeResolution.archetype_evidence_state`.
- `dominant_variable_count` must equal the length of `dominant_variable_hypotheses`.
- When upstream target classification is non-operating or ambiguous, `ArchetypeResolution.selected_archetype_id` must collapse to `target_not_yet_structurally_modelable` and `SystemAbstractionSeed.evidence_maturity.value` must indicate unresolved maturity.

## identifiers
- `ArchetypeDefinition.archetype_id` is the canonical stable identifier of a structural prior in the library.
- `ArchetypeResolution.selected_archetype_id` is the canonical runtime selector for the chosen archetype.
- `ArchetypeSelectionBasis` rows are logically identified by `(dimension, source, value)`.
- `DominantVariableHypothesis` rows are logically identified by `(selected_archetype_id, variable, layer)`.
- `EvidenceBoundField.field_name` is the stable identifier for each seed field inside `SystemAbstractionSeed`.
- This motor does not emit independent persistent record IDs or storage UUIDs beyond library IDs and field names; output identity is anchored to the selected archetype plus the upstream target context.

## versioning
- Runtime output from `motor_039` does not currently expose `version_id`, `version_hash`, or `parent_id` fields.
- Version identity is therefore implicit in the in-code `ARCHETYPE_LIBRARY`, the resolver rule order, and the upstream target/field/source context used at run time.
- A material change to the library definitions, fallback map, or resolver precedence order should be treated as a schema-significant change even if the emitted dictionaries keep the same keys.
- `archetype_id` values are intended to be stable across compatible library revisions; semantic changes to an existing archetype should be treated with the same caution as a schema migration because downstream motors rely on these keys.
- `ArchetypeResolverSurface` is deterministic for the same target definition, target classification, observed asset fields, dataset coverage, and source-register inputs under the same library and resolver logic.

## lineage
- The resolver reads its bounded input from `target_definition`, `target_classification_object`, `facility_prior`, `asset_field_register`, `dataset_coverage_register`, and `source_register`.
- `selection_basis_register` is the primary lineage surface that explains how upstream observed context activated a particular archetype or fallback.
- `why_selected` preserves the short natural-language lineage for the selected path through the resolver.
- `SystemAbstractionSeed` preserves lineage by attaching `falsification_condition` and `minimum_evidence_required` to every seeded field.
- `AntiHallucinationContract` is part of lineage, not decoration: it records how the output may be used downstream and explicitly bans reclassification of archetypal priors as observed facts.
- This motor does not parse local evidence, close claims, or attach per-row provenance identifiers; its lineage is rule-based and bounded to structural-prior selection.
