# Functional Contract — Report Compression Engine

Motor ID: motor_048

## inputs

- `motor_047.executive_thesis`
  Tipo: `dict`
  Productor: `motor_047`
  Uso: fuente principal de visible report mode, dominant lens, supporting modes, body hierarchy y client-facing actions.
- `motor_034.canonical_problem_frame`
  Tipo: `dict`
  Productor: `motor_034`
  Uso: sostener el modo estructural dominante y la logica de compresion cuando el problema esta activo.
- `motor_034.claim_contract_register`
  Tipo: `list[dict]`
  Productor: `motor_034`
  Uso: mapear claims deduplicados y justificar surfaces cliente-facing.
- `motor_034.report_output_mode_classifier_table`
  Tipo: `list[dict]`
  Productor: `motor_034`
  Uso: fijar el modo visible seleccionado.
- `motor_054.congruence_claim_contract_register`
  Tipo: `list[dict]`
  Productor: `motor_054`
  Uso: integrar claims de congruencia en appendix, authority map y deduplicated claim map sin reabrir el body.

## outputs

- `main_report_outline`
  Tipo: `dict`
  Consumidores: `motor_016`, `motor_036`, render packing
  Contenido: modo visible, dominant lens, supporting modes, body budget, compression state, sections, body section titles y conteo de congruence signals visibles.
- `appendix_map`
  Tipo: `list[dict]`
  Consumidores: `motor_016`, render packing
  Contenido: capitulos y registros demotados al appendix.
- `section_authority_map`
  Tipo: `dict`
  Consumidores: trazabilidad y `motor_036`
  Contenido: autoridad upstream que sostiene cada seccion comprimida.
- `deduplicated_claim_map`
  Tipo: `dict`
  Consumidores: trazabilidad y compresion claim-aware
  Contenido: claims visibles y de congruencia agrupados por seccion semantica.
- `client_facing_tad`
  Tipo: `dict`
  Consumidores: report package y validadores de jerarquia
  Contenido: lista acotada de acciones cliente-facing.
- `congruence_visibility_register`
  Tipo: `list[dict]`
  Consumidores: observabilidad y `motor_036`
  Contenido: qué señales de congruencia se integraron al body existente.
- `section_demotions_register`
  Tipo: `list[dict]`
  Consumidores: observabilidad y appendix logic
  Contenido: secciones o bloques reubicados desde cuerpo a appendix.
- `body_to_appendix_justification_map`
  Tipo: `dict`
  Consumidores: auditoria de compresion
  Contenido: por qué ciertos soportes van a appendix.
- `prompt_block_mapping_register`
  Tipo: `list[dict]`
  Consumidores: trazabilidad del prompt y validadores
  Contenido: mapa de bloques prompt -> seccion visible o appendix de soporte.
- `compression_decision_log`
  Tipo: `list[dict]`
  Consumidores: auditoria y debugging
  Contenido: decisiones de primary mode, body budget, bypass o selective promotion.

## limits

- the body may not exceed the bounded section budget for structural cases;
- congruence technical registers may support the body, but may not reopen the body as new raw technical sections;
- inadmissible thesis cases must use explicit bypass instead of fake structural compression;
- the engine may not invent a stronger visible mode than the one selected upstream;
- appendix support must remain explainable through demotions and justification maps.

## validations

- `main_report_outline.visible_report_mode` must align with the selected output mode;
- structural admissible cases must stay bounded to the documented primary-section budget;
- inadmissible cases must produce zero primary sections and zero client-facing actions;
- prompt-block mapping must remain present for admissible compressed outputs.
