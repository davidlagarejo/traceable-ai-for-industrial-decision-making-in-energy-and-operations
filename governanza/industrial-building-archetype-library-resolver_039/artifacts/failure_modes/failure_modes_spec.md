# Failure Modes Spec — Industrial / Building Archetype Library Resolver

Motor ID: motor_039

## failure_modes_list
- `NON_OPERATING_TARGET_MODELED_AS_REAL_ASSET`: a headquarters, mailing address, or ambiguous target receives a structurally modelable archetype -> every downstream structural motor starts reasoning from a false physical substrate -> force selection to `target_not_yet_structurally_modelable` and emit zero dominant hypotheses.
- `OVER-SPECIFIC_ARCHETYPE_SELECTION`: a narrow archetype such as `commercial_office_tower_nyc` or `manufacturing_laminate` is selected without the bounded clues required by the resolver -> the rest of the lane inherits an unjustified process, control, and regulatory frame -> keep resolver precedence strict and require observable basis rows for specific activation.
- `GENERIC_FALLBACK_OVERUSE`: cases with strong clues keep falling back to generic archetypes -> the lane loses diagnostic resolution and understates the real structural variables -> review resolver rules and clue extraction before widening downstream reasoning.
- `ANTI_HALLUCINATION_BREACH`: downstream consumers treat `ARCHETYPAL_PRIOR` output as observed local truth -> redesign, ROI, or savings logic hardens without admissible evidence -> preserve the anti-hallucination contract and fail any consumer that upgrades evidence state silently.
- `SEED_FIELD_DRIFT`: `system_abstraction_seed` diverges from the selected archetype definition -> downstream abstraction and framing operate on a schema that no longer matches the archetype that was actually selected -> derive seed fields only from the chosen `ArchetypeDefinition`.

## anti_patterns
- Selecting archetypes from asset prestige or naming vibe instead of from bounded resolver clues.
- Using specific source-family presence as automatic proof of a narrow operating archetype.
- Treating generic archetypes as placeholders that can later justify any downstream story.
- Letting downstream motors reinterpret `dominant_variable_hypotheses` as observations instead of falsable priors.
- Expanding the archetype library ad hoc without preserving stable `archetype_id` semantics.

## degradation_signals
- rising frequency of `match_confidence = high` without rich `selection_basis_register` support;
- unresolved targets that still show non-zero `dominant_variable_count`;
- generic archetypes appearing repeatedly in cases where tests and field clues indicate a narrower bounded prior should be reachable;
- differences between flattened resolver fields and nested `archetype_resolution`;
- downstream structural reports citing seeded fields as if they came from local evidence rather than archetypal priors.

## expensive_errors
- Selecting the wrong narrow archetype early. It is expensive because every later structural artifact compounds the wrong frame. Prevent it by requiring bounded clue activation and preserving fallback discipline.
- Treating unresolved identity as structurally modelable. It is expensive because later fixes require unwinding not just one motor but the full structural lane. Prevent it by keeping the non-operating downgrade path strict.
- Collapsing anti-hallucination boundaries. It is expensive because it contaminates executive outputs with false evidence posture. Prevent it by preserving evidence-state separation and explicit prohibited uses.
- Allowing `system_abstraction_seed` to drift from library definitions. It is expensive because downstream motors silently inherit inconsistent structure. Prevent it by deriving every seed field from the chosen `ArchetypeDefinition`, not from freehand edits.
