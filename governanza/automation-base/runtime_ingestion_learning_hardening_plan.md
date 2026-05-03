# Runtime Ingestion Learning Hardening Plan

## Objetivo

Cerrar el gap entre:

- propagacion reactiva de `motor_020`
- scorecard del run en `motor_024`

y un loop real de mejora entre ingestas sucesivas.

## Motores duenos

- `motor_009`: deteccion de cambios de fuente
- `motor_020`: belief revision / propagacion causal
- `motor_024`: evaluacion estructural del run
- `pipeline_orchestrator`: persistencia y contexto entre corridas

## Artefactos a agregar

- `case_delta_register`
- `source_yield_memory_register`
- `next_ingestion_priority_update`
- `ingestion_learning_register`

## Fases

### IL-01

Persistir resumen del run previo por `pipeline_id` en `__runtime__`.

### IL-02

Comparar corrida actual vs corrida previa y emitir `case_delta_register`.

### IL-03

Calcular memoria de rendimiento por fuente ruteada a partir de `source_family_coverage_table`.

### IL-04

Traducir delta + yield + evidence gaps a `next_ingestion_priority_update`.

### IL-05

Persistir el resumen de aprendizaje en `PipelineRun` para cerrar el loop de la siguiente ingesta.

### IL-06

Endurecer `motor_020` con matching causal mas preciso y menos fallback global.

### IL-07

Incorporar degradacion por staleness / disappearance de fuente.

### IL-08

Exponer la memoria de aprendizaje en dashboard / API / manifests cuando la base ya este estable.

## Reglas que no se pueden debilitar

- no inventar mejora si no hubo delta real
- no subir report type sin soporte estructurado
- no confundir yield de fuente con verdad del activo
- no usar aprendizaje para suavizar gates epistemicos
- no cerrar publication si el preflight sigue en rojo
