# Technical Schema — Problem Framing Engine

Motor ID: motor_041

## entities
- `ProblemFramingRecord`
- `ProblemFramingRegister`
- `FallbackProblemTranslation`

## fields
- `problem_framing_register: list[ProblemFramingRecord]`
- `problem_framing_count: int`
- `ProblemFramingRecord.stated_problem: str`
- `ProblemFramingRecord.reframed_problem: str`
- `ProblemFramingRecord.why_original_framing_may_be_wrong: str`
- `ProblemFramingRecord.evidence_needed: list[str]`
- `ProblemFramingRecord.strategic_risk: str`
- `ProblemFramingRecord.evidence_state: str`
- `ProblemFramingRecord.linked_layers: list[str]`

## relationships
- `motor_037.system_abstraction` + `motor_038.dominant_variable_register` + `motor_040.cross_layer_conflict_register` -> framing estructural directo
- `motor_051.invalid_problem_frame_register` + `motor_051.cross_layer_congruence_register` -> traducción fallback cuando el framing directo no es admisible
- `problem_framing_count` referencia el cardinal del `problem_framing_register`

## identifiers
- `motor_id = motor_041`
- el identificador lógico de cada fila es el par `stated_problem` + `reframed_problem`
- las traducciones fallback deben poder rastrearse a `motor_051.invalid_problem_frame_register`

## versioning
- este schema documenta la superficie actual del runtime wrapper y del `Motor041Adapter`
- cualquier ampliación de campos debe preservar compatibilidad con `problem_framing_count`
- cambios en `linked_layers` o `evidence_needed` requieren revisar `test_spec.md` y `failure_modes_spec.md`

## lineage
- upstream principal: `motor_037`, `motor_038`, `motor_040`, `motor_051`
- downstream principal: `motor_044`, `motor_045`, `motor_046`, síntesis ejecutiva
- la lineage debe preservar si la fila nació del framing estructural o del fallback de congruencia

## input_dependencies
- `motor_037.system_abstraction`
- `motor_038.dominant_variable_register`
- `motor_040.cross_layer_conflict_register`
- `motor_051.invalid_problem_frame_register`
- `motor_051.cross_layer_congruence_register`
- contextual target definition from `motor_012` or `motor_007`

## output_schema
- `problem_framing_register: list[ProblemFramingRecord]`
- `problem_framing_count: int`

## allowed_evidence_states
- `OBSERVED_FACT`
- `CONDITIONAL_HYPOTHESIS`
- `ARCHETYPAL_PRIOR`
- `INADMISSIBLE_CLAIM`

## behavioral_constraints
- si el register estructural existe y es usable, tiene prioridad sobre el fallback;
- si el primer framing estructural queda vacío, `asset_screening` o `INADMISSIBLE_CLAIM`, puede traducirse el invalid frame;
- `linked_layers` puede estar vacío para framing estructural nativo, pero no debe perderse en traducciones de congruencia;
- `problem_framing_count == len(problem_framing_register)`.
