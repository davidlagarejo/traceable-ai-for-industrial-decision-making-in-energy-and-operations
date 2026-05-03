# Functional Contract — Executive Synthesis / Thesis Engine

Motor ID: motor_047

## inputs

- `motor_034.canonical_problem_frame`
  Tipo: `dict`
  Productor: `motor_034`
  Uso: fijar contradiccion dominante, reframe y minimum discriminating evidence.
- `motor_034.claim_contract_register`
  Tipo: `list[dict]`
  Productor: `motor_034`
  Uso: mantener bounded claim discipline dentro de la tesis.
- `motor_034.report_output_mode_classifier_table`
  Tipo: `list[dict]`
  Productor: `motor_034`
  Uso: seleccionar el `report_mode` visible correcto o detectar un caso inadmisible.
- `motor_037.system_abstraction`
  Tipo: `dict`
  Productor: `motor_037`
  Uso: dar contexto de asset type, archetype y process type a la tesis.
- `motor_038.dominant_variable_register`
  Tipo: `list[dict]`
  Productor: `motor_038`
  Uso: escoger pocas variables dominantes con impacto interpretivo.
- `motor_040.cross_layer_conflict_register`
  Tipo: `list[dict]`
  Productor: `motor_040`
  Uso: rankear contradicciones y elegir la dominante.
- `motor_041.problem_framing_register`
  Tipo: `list[dict]`
  Productor: `motor_041`
  Uso: preservar el declared problem y el reframed problem.
- `motor_014.scenario_space`
  Tipo: `list[dict]`
  Productor: `motor_014`
  Uso: sostener `top_scenarios` y consecuencias financieras bounded.
- `motor_045.structural_financial_exposure_register`
  Tipo: `list[dict]`
  Productor: `motor_045`
  Uso: traducir la contradiccion a capital logic y risk if wrong.
- `motor_043.competitive_comparison_register`, `motor_044.conditional_redesign_register`, `motor_046.minimum_evidence_for_discrimination_register`
  Tipo: `list[dict]`
  Productor: lane estructural
  Uso: bounded peer logic, redesign hypothesis y discriminating evidence pack.
- `motor_033.expanded_structural_tad_action_register`
  Tipo: `list[dict]`
  Productor: `motor_033`
  Uso: derivar `top_actions` y la parte accionable de la tesis.
- `motor_051`, `motor_052`, `motor_053`, `motor_054`
  Tipo: `dict` o `list[dict]`
  Productor: congruence and strategic insight lane
  Uso: inyectar invalid problem frame, comparison risk, loss logic, measurement minimality, regulatory physics, finance-to-physics dependency, gold nuggets y congruence action priority.

## outputs

- `executive_thesis`
  Tipo: `dict`
  Consumidores: `motor_048`, structural executive summary, `motor_036`
  Contenido: una sola tesis ejecutiva bounded, o una tesis estructural inadmisible cuando el caso no merece compresion estructural.
- `dominant_contradiction`
  Tipo: `str`
  Consumidores: observabilidad y compresion downstream
  Contenido: contradiccion estructural dominante seleccionada para la tesis.
- `supporting_mode_count`
  Tipo: `int`
  Consumidores: observabilidad
  Contenido: numero de modos de soporte visibles en la tesis.
- `client_facing_action_count`
  Tipo: `int`
  Consumidores: observabilidad y `motor_048`
  Contenido: numero de acciones top-level expuestas al cliente.

## limits

- the thesis must stay singular; it may not become a dump of all conflicts and all actions;
- inadmissible cases must remain explicitly inadmissible instead of receiving a fake structural thesis;
- congruence bridge fields may only populate when structural admissibility is active;
- the thesis may not convert bounded financial exposure into ROI closure or unrestricted recommendation;
- top actions must stay small and client-facing, not exhaustively procedural.

## validations

- the chosen dominant contradiction must be traceable to the ranked conflict register;
- rejected contradiction candidates must remain preserved when applicable;
- interpretive signals and congruence takes must stay consistent with bounded evidence posture;
- `report_mode` must match the selected visible output mode coming from `motor_034`.
