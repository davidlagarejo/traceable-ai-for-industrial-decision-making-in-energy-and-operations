# Technical Schema — Executive Synthesis / Thesis Engine

Motor ID: motor_047

## entities

- `ExecutiveThesis`
- `InterpretiveSignalRecord`
- `ConflictSelectionRecord`
- `TopActionRecord`

## fields

- `executive_thesis: ExecutiveThesis`
- `dominant_contradiction: str`
- `supporting_mode_count: int`
- `client_facing_action_count: int`
- `ExecutiveThesis.thesis_state: str`
- `ExecutiveThesis.report_mode: str`
- `ExecutiveThesis.declared_problem: str`
- `ExecutiveThesis.reframed_problem: str`
- `ExecutiveThesis.dominant_contradiction: str`
- `ExecutiveThesis.dominant_lens: str`
- `ExecutiveThesis.minimum_discriminating_evidence: list[str]`
- `ExecutiveThesis.hidden_assumption_at_risk: str`
- `ExecutiveThesis.why_current_question_is_premature: str`
- `ExecutiveThesis.what_reality_feature_changes_the_decision: str`
- `ExecutiveThesis.capital_logic_if_assumption_holds: str`
- `ExecutiveThesis.capital_logic_if_assumption_breaks: str`
- `ExecutiveThesis.surprising_but_evidenced_takeaway: str`
- `ExecutiveThesis.top_dominant_variables: list[dict]`
- `ExecutiveThesis.top_scenarios: list[dict]`
- `ExecutiveThesis.top_actions: list[TopActionRecord]`
- `ExecutiveThesis.supporting_modes: list[str]`
- `ExecutiveThesis.interpretive_signal_register: list[InterpretiveSignalRecord]`
- `ExecutiveThesis.dominant_contradiction_selection_basis: dict[str, Any]`
- `ExecutiveThesis.thesis_ranked_conflict_register: list[ConflictSelectionRecord]`
- `ExecutiveThesis.rejected_contradiction_candidates: list[ConflictSelectionRecord]`
- `ExecutiveThesis.inadmissibility_reason: str`
- `ExecutiveThesis.dominant_operational_misunderstanding: str`
- `ExecutiveThesis.hidden_system_boundary_error: str`
- `ExecutiveThesis.invalid_comparison_risk: str`
- `ExecutiveThesis.dominant_loss_logic: str`
- `ExecutiveThesis.measurement_minimality_take: str`
- `ExecutiveThesis.regulatory_physics_take: str`
- `ExecutiveThesis.finance_to_physics_take: str`
- `ExecutiveThesis.maintenance_reality_take: str`
- `ExecutiveThesis.congruence_action_priority_register: list[dict]`
- `InterpretiveSignalRecord.signal_type: str`
- `InterpretiveSignalRecord.signal: str`
- `InterpretiveSignalRecord.why_it_matters: str`
- `InterpretiveSignalRecord.evidence_state: str`
- `TopActionRecord.action: str`
- `TopActionRecord.status: str`
- `TopActionRecord.maps_to: str`
- `TopActionRecord.why: str`
- `ConflictSelectionRecord.conflict: str`
- `ConflictSelectionRecord.selection_basis: dict[str, Any]`

## relationships

- structural inputs from `motor_037`, `motor_038`, `motor_040`, `motor_041`, `motor_043`, `motor_044`, `motor_045`, `motor_046` -> structural spine of `executive_thesis`
- scenario and TAD inputs from `motor_014` and `motor_033` -> `top_scenarios` and `top_actions`
- mode and claim governance from `motor_034` -> `report_mode`, inadmissibility gating and bounded claim posture
- congruence inputs from `motor_051`, `motor_052`, `motor_053`, `motor_054` -> congruence-bridge fields inside `executive_thesis`
- `dominant_contradiction` is a convenience projection of `executive_thesis.dominant_contradiction`
- `supporting_mode_count == len(executive_thesis.supporting_modes)`
- `client_facing_action_count == len(executive_thesis.top_actions)`

## identifiers

- `motor_id = motor_047`
- the thesis object is keyed implicitly by the current case under synthesis
- interpretive signals are logically keyed by `signal_type`
- ranked and rejected contradiction rows are logically keyed by `conflict`

## versioning

- this schema documents the current wrapper surface around `Motor047Adapter`
- the wrapper must preserve the top-level keys listed above
- new thesis fields may be added, but the inadmissible-vs-admissible state distinction must remain stable
- downstream consumers depend on `executive_thesis.report_mode`, ranked conflicts and top actions staying present

## lineage

- upstream structural lineage: `motor_034`, `motor_037`, `motor_038`, `motor_040`, `motor_041`, `motor_043`, `motor_044`, `motor_045`, `motor_046`
- upstream action/scenario lineage: `motor_014`, `motor_033`
- upstream congruence lineage: `motor_051`, `motor_052`, `motor_053`, `motor_054`
- downstream lineage: `motor_048`, structural executive summary, client-facing hierarchy validation in `motor_036`

## input_dependencies

- `motor_014.scenario_space`
- `motor_033.expanded_structural_tad_action_register`
- `motor_034.canonical_problem_frame`
- `motor_034.claim_contract_register`
- `motor_034.report_output_mode_classifier_table`
- `motor_037.system_abstraction`
- `motor_038.dominant_variable_register`
- `motor_040.cross_layer_conflict_register`
- `motor_041.problem_framing_register`
- `motor_043.competitive_comparison_register`
- `motor_044.conditional_redesign_register`
- `motor_045.structural_financial_exposure_register`
- `motor_046.minimum_evidence_for_discrimination_register`
- `motor_051.invalid_problem_frame_register`
- `motor_051.invalid_comparison_risk_register`
- `motor_051.cross_layer_congruence_register`
- `motor_052.loss_pattern_hypothesis_register`
- `motor_052.maintenance_reality_register`
- `motor_052.measurement_strategy_register`
- `motor_053.regulatory_physics_register`
- `motor_053.finance_physics_dependency_register`
- `motor_054.strategic_gold_nugget_register`
- `motor_054.gold_nugget_strength_register`
- `motor_054.congruence_action_priority_register`

## behavioral_constraints

- inadmissible cases must emit `thesis_state = inadmissible_thesis` and keep structural/congruence take fields empty
- admissible cases must preserve a non-empty contradiction selection basis when a dominant contradiction is chosen
- top actions must remain bounded and client-facing
- `report_mode` must stay aligned with the selected visible output mode
- congruence-bridge fields may not populate in a way that outruns the bounded evidence posture
