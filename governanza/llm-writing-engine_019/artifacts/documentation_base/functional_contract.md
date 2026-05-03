# Functional Contract — LLM Writing Engine

Motor ID: motor_019

## inputs

- `motor_014` inference and governance surfaces
  Tipo: `dict`
  Productor: `motor_014`
  Uso: `inference_records`, `conflict_register`, `tension_records`, `opportunity_candidates`, `validation_queue`, `next_best_questions`, `decision_front_register`, `scenario_space`, `claim_permission_register`, `decision_permission_register`, `variable_maturity_register`, `claim_permission_summary` y `report_readiness_register`.
- `motor_012.facility_prior` y `motor_012.compliance_applicability_case`
  Tipo: `dict`
  Productor: `motor_012`
  Uso: asset context, system hypotheses, benchmark/regulatory priors y readiness base.
- `motor_028.enriched_data`
  Tipo: `dict`
  Productor: `motor_028`
  Uso: financial context, company/ticker y `extended_sources`.
- `motor_033.tad_preliminary`
  Tipo: `dict`
  Productor: `motor_033`
  Uso: action posture preliminar y frontier de validacion.
- `motor_034.maturity_summary` y `motor_034.report_readiness_register`
  Tipo: `dict`
  Productor: `motor_034`
  Uso: bottlenecks de madurez, blocked claims y constraints de report readiness.
- `motor_001.subject_definition`
  Tipo: `dict`
  Productor: `motor_001`
  Uso: subject kind y gating para report modes bloqueados.
- `__pipeline__.facility_inputs`
  Tipo: `dict`
  Productor: pipeline runtime
  Uso: declaraciones del operador que pueden aparecer como contexto pero no como verdad no verificada.

## outputs

- `written_sections`
  Tipo: `list[dict]`
  Consumidores: package assembly y render
  Contenido: texto English/Spanish, render mode, lint status, context sources y `section_packet` ligado.
- `section_packets`
  Tipo: `list[dict]`
  Consumidores: auditoria, smoke checks y governance review
  Contenido: packet id, section id, title, audience, writing task, style contract, allowed claims, forbidden claims, chart role, context snapshot y source facts.
- `codex_available`
  Tipo: `bool`
  Consumidores: observabilidad y fallback logic
  Contenido: disponibilidad de `codex` CLI.
- `llm_errors`
  Tipo: `list[dict]`
  Consumidores: observabilidad
  Contenido: timeouts, parse failures, lint failures y budget exhaustion.
- `total_sections_written`
  Tipo: `int`
  Consumidores: observabilidad
- `llm_governance_summary`
  Tipo: `dict`
  Consumidores: report conformance y observabilidad
  Contenido: sections attempted/rendered, lint failures, fallback sections, structured summary sections, budget exhaustion, unresolved breaches, report readiness reason y blocked claim count.
- `writing_runtime_profile`
  Tipo: `dict`
  Consumidores: observabilidad
  Contenido: elapsed time, total budget, section timeout y skipped sections due budget.
- `model_used`
  Tipo: `str`
  Consumidores: observabilidad
- `produced_at`
  Tipo: `str`
  Consumidores: tracing

## limits

- the writer may only use `source_facts` from each `section_packet`;
- it may not introduce unsupported numbers, forbidden phrases or hard-closure language;
- it may not exceed the bounded word budget per section;
- it may not treat operational assessment as due diligence, underwriting or acquisition analysis;
- when the LLM path is unavailable or unsafe, the engine must fall back instead of inventing safer-sounding prose.

## validations

- every written section must be traceable back to a `section_packet`;
- blocked claims and maturity bottlenecks must stay visible in the governance summary and relevant packets;
- structured-summary sections must bypass the LLM and still remain bilingual and bounded;
- fallback and lint paths must be surfaced explicitly, not silently swallowed.
