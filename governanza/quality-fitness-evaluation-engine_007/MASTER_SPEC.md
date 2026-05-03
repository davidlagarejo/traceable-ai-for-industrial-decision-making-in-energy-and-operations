# QUALITY / FITNESS EVALUATION ENGINE  
## MASTER_SPEC

## 1. Qué es exactamente el Quality / Fitness Evaluation Engine

El Quality / Fitness Evaluation Engine es el motor transversal que evalúa objetos ya estructurados contra reglas explícitas para determinar:

- integridad estructural;
- completitud mínima;
- consistencia interna;
- preservación de provenance, lineage y versionado;
- conformidad con contratos;
- aptitud para un uso, fase o handoff concreto.

Su output no es “verdad”, ni “calidad soberana”, ni “verificación”. Su output es un juicio disciplinado y auditable sobre si un objeto:

- está estructuralmente sano;
- conserva los metadatos críticos que exige el framework;
- respeta su contrato;
- y es apto o no apto para el uso declarado.

## 2. Qué problema resuelve y qué problema no resuelve

### 2.1 Problema que resuelve

Resuelve el problema de impedir que objetos estructuralmente rotos, contractualmente inválidos, no trazables o no aptos para un uso concreto avancen silenciosamente aguas abajo.

Resuelve, en particular:

- chequeo sistemático de campos obligatorios;
- chequeo de coherencia de referencias y versiones;
- chequeo de preservación de provenance;
- chequeo de integridad mínima por tipo de objeto;
- chequeo de fitness por fase, output o handoff;
- emisión disciplinada de `PASS`, `PASS_WITH_WARNINGS` o `FAIL`;
- explicación trazable de por qué pasó, pasó con warnings o falló.

### 2.2 Problema que no resuelve

No resuelve:

- si un claim es verdadero;
- si una fuente es epistemológicamente suficiente en sentido soberano;
- si una hipótesis debe aceptarse;
- si una entidad está bien resuelta semánticamente;
- si una taxonomía es correcta;
- si un benchmark representa evidencia local;
- si un output ya es verification-grade por mérito propio.

## 3. Qué rol cumple dentro del framework completo

Este motor ocupa la capa de evaluación disciplinada entre producción de objetos y handoff entre fases o motores.

Su rol es:

- traducir contratos y reglas en evaluaciones ejecutables;
- separar salud estructural de aptitud para uso;
- bloquear contaminación aguas abajo;
- producir evidencia auditable de gating;
- permitir reevaluación determinista con nuevas versiones de reglas o contratos.

No define contratos. No define gobernanza. No redefine outputs válidos. Ejecuta y registra evaluación contra definiciones externas controladas.

## 4. Qué NO debe hacer

No debe:

- ingerir ni parsear;
- normalizar valores;
- resolver identidad;
- curar bibliotecas;
- inferir significado faltante;
- corregir objetos silenciosamente;
- completar campos por heurística;
- convertir un score en autoridad soberana;
- reemplazar Governance Layer;
- aprobar por estética un objeto materialmente defectuoso;
- promover un objeto a verification-grade por score;
- esconder fallos detrás de dashboards o scorecards.

## 5. Qué SÍ debe hacer

Sí debe:

- consumir objetos ya estructurados y sus contratos relevantes;
- evaluar reglas por dimensión y por contexto de uso;
- distinguir estructura, trazabilidad, contrato y fitness;
- producir findings tipados, severos y auditables;
- producir outcome global derivado de findings;
- registrar reglas, versiones y rationale de la evaluación;
- soportar reevaluación sobre el mismo objeto con reglas o contratos nuevos;
- permitir gating por fase, por object type y por handoff.

## 6. Qué dimensiones de calidad debe evaluar ZLab

ZLab debe evaluar, como mínimo, estas dimensiones de calidad:

- **Integridad estructural**: presencia de campos requeridos, tipos permitidos, estados válidos, referencias internas coherentes.
- **Completitud mínima**: cobertura de campos y metadatos obligatorios para el tipo de objeto evaluado.
- **Consistencia interna**: ausencia de contradicciones entre campos, estados, refs, bundles y derivados.
- **Trazabilidad**: presencia y resolvibilidad de provenance, lineage, contract refs y version refs.
- **Disciplina de versionado**: uso de versiones explícitas, detectabilidad de staleness y dependencia de objetos correctos.
- **Conformidad contractual**: cumplimiento de contrato de objeto, contrato de fase y contrato de handoff.
- **Preservación de incertidumbre y conflicto**: presencia de uncertainty markers, conflict refs o límites epistemológicos cuando el objeto los requiere.
- **Transparencia de estado**: partial flags, warnings, missingness y degradaciones explícitas, no implícitas.

## 7. Qué dimensiones de fitness-for-use debe evaluar ZLab

Fitness-for-use no es “calidad general”. Es adecuación para un uso declarado. Debe evaluarse, como mínimo, en estas dimensiones:

- **Aptitud por fase**: si el objeto satisface exigencias mínimas de Fase 1, 2, 3 o 4.
- **Aptitud por transición**: si puede ser entregado de una fase o motor a otro sin degradar el proceso.
- **Aptitud por granularidad**: si tiene suficiente detalle para el uso declarado.
- **Aptitud por dependencia**: si los objetos upstream de los que depende siguen vigentes y compatibles.
- **Aptitud epistemológica contextual**: si preserva límites, incertidumbre y soporte requeridos para el uso pedido.
- **Aptitud operativa downstream**: si otro motor puede consumirlo sin ambigüedad material no declarada.
- **Aptitud de cobertura**: si cubre el mínimo necesario para la tarea específica, aunque no esté “completo” en abstracto.

## 8. Qué granularidad de evaluación conviene

| Nivel | Qué evalúa | Uso principal |
|---|---|---|
| Campo | missingness, tipo, rango, ref puntual, stale ref puntual | errores finos y diagnostics |
| Objeto | integridad, consistencia, provenance, contrato | gating básico |
| Bundle | cobertura, coherencia entre miembros, dependencia cruzada | packaging y handoff |
| Output | aptitud para entrega, audiencia o export | fase 3 y 4 |
| Fase | si el objeto satisface exigencias mínimas del contexto | phase gating |
| Transición/Handoff | si puede pasar a otro motor o fase | control de contaminación |

Regla clave:

- el motor debe poder emitir findings a nivel campo y objeto;
- el outcome operativo debe poder emitirse a nivel objeto, bundle, output o handoff;
- no debe existir solo evaluación global agregada.

## 9. Qué objetos internos necesita

Objetos internos mínimos del motor:

- **evaluation_target_record**: referencia al objeto evaluado, tipo, versión, contexto y uso declarado.
- **evaluation_profile_record**: define el perfil aplicable por object type, fase y uso.
- **validation_rule_record**: regla evaluable, dimensión, severidad por defecto, alcance y versión.
- **evaluation_run_record**: ejecución concreta con timestamp, evaluator version, profile version, contract refs y rule-set version.
- **evaluation_issue_record**: finding tipado con categoría, severidad, target path, rule ref, rationale y evidence refs.
- **dimension_assessment_record**: resultado por dimensión de calidad o fitness.
- **evaluation_decision_record**: outcome global y decisión de gating derivada.
- **evaluation_scorecard_record**: opcional; resumen numérico derivado, nunca soberano.
- **evaluation_replay_manifest**: refs exactas para reconstruir la evaluación meses después.

## 10. Qué metadatos debe preservar obligatoriamente

Toda evaluación debe preservar:

- `target_object_ref`
- `target_object_type`
- `target_object_version_ref`
- `declared_phase_context`
- `declared_intended_use`
- `contract_ref`
- `contract_version_ref`
- `profile_ref`
- `profile_version`
- `rule_set_version`
- `evaluator_version`
- `dependency_refs`
- `dependency_version_refs`
- `provenance_refs`
- `lineage_refs`
- `executed_at`
- `outcome`
- `issue_ids`
- `dimension_results`
- `gating_decision`
- `rationale_summary`
- `scorecard_formula_version` si existe scorecard

Sin version refs o rule refs no hay evaluación reconstruible.

## 11. Qué diferencia debe existir entre categorías de resultado

| Categoría | Significado |
|---|---|
| **quality failure** | falla de estructura, completitud mínima o consistencia interna del objeto |
| **traceability failure** | falta o ruptura de provenance, lineage, dependency refs o version refs requeridas |
| **contract violation** | incumplimiento de contrato de objeto, fase o handoff, aunque el objeto esté bien formado |
| **fitness failure** | objeto usable en abstracto pero no apto para el uso o fase declarada |
| **epistemic insufficiency** | el objeto no preserva el soporte, incertidumbre o límites exigidos para el uso pretendido |
| **warning** | desviación no bloqueante que debe preservarse y explicarse |
| **block** | finding que impide handoff o uso específico; fuerza `FAIL` operativo |
| **pass** | no hay findings materiales para el perfil aplicado |

Reglas de separación:

- calidad estructural no equivale a suficiencia epistemológica;
- fitness failure no implica que el objeto esté roto;
- contract violation puede existir con estructura correcta;
- block es una consecuencia operativa, no un sustituto de categoría semántica.

## 12. Cómo representar severity y rationale

### 12.1 Severity mínima

Severidades mínimas:

- `warning`
- `error`
- `block`

### 12.2 Semántica

- `warning`: el objeto puede seguir vivo y, si el perfil lo permite, salir como `PASS_WITH_WARNINGS`.
- `error`: falla material; el objeto no pasa el perfil evaluado.
- `block`: error con efecto de gating explícito sobre fase, output o handoff.

### 12.3 Rationale

Cada finding debe incluir:

- `rule_id`
- `dimension`
- `issue_type`
- `severity`
- `target_ref`
- `target_path` cuando aplique
- `message`
- `rationale`
- `evidence_refs`
- `contract_ref` o `profile_ref` que justificó el check

No se permiten findings solo narrativos.

## 13. Cómo distinguir “estructuralmente correcto pero no apto” de “roto o insuficiente incluso para uso básico”

Distinción obligatoria:

- **Estructuralmente correcto pero no apto**:
  - pasa integridad, completitud mínima, consistencia y trazabilidad;
  - falla porque el uso declarado exige más granularidad, más frescura, otro contrato o otra cobertura.
  - clasificación: `fitness_failure` o `contract_violation`, no `quality_failure`.

- **Roto o insuficiente incluso para uso básico**:
  - faltan campos obligatorios, refs mínimas, provenance, lineage, uncertainty markers requeridos o coherencia interna básica.
  - clasificación: `quality_failure`, `traceability_failure` o `epistemic_insufficiency` material.
  - no debe pasar ni como objeto base.

Regla de diseño:

- el motor debe evaluar por capas separadas;
- una scorecard no puede compensar una falla material de capas básicas.

## 14. Cómo manejar sparse cases sin castigar indebidamente al sistema

Sparse no es automáticamente malo. Debe tratarse así:

- si el contrato permite sparsity y el objeto declara explícitamente su estado parcial, puede pasar;
- si la provenance está intacta y la falta de cobertura es visible, puede emitir `PASS_WITH_WARNINGS`;
- si el uso declarado es exploratorio o intermedio, la cobertura mínima puede ser menor;
- si la sparsity contradice el uso declarado o se oculta, debe fallar.

Reglas:

- sparse permitido requiere `partial`, `missing`, `incomplete` o equivalente explícito;
- sparse oculto es failure;
- sparse que rompe contractualmente un handoff es `FAIL`;
- sparse útil para un uso temprano no debe ser castigado como si fuera output final.

## 15. Cómo interactúa con otros motores

### 15.1 Phase Contract Registry

Provee:

- requerimientos obligatorios;
- outputs permitidos;
- criterios de handoff;
- versiones contractuales válidas.

Este motor consume esos contratos. No los redefine.

### 15.2 Versioning + Lineage Engine

Provee:

- object version refs;
- dependency refs;
- lineage resolvible;
- base para staleness y reconstrucción.

Este motor verifica presencia y coherencia de esas refs. No gestiona el lineage.

### 15.3 Taxonomy Service

Provee taxonomías y canonical refs. Este motor solo verifica:

- presencia cuando son requeridas;
- compatibilidad de versión;
- resolvibilidad mínima.

No clasifica ni remapea.

### 15.4 Canonical Normalization Engine

Evalúa sus outputs respecto a:

- triple valor preservado;
- conversion refs;
- partial normalization visible;
- normalized objects íntegros.

No normaliza nada.

### 15.5 Entity Identity / Resolution Engine

Evalúa:

- candidate sets consistentes;
- rationale/confidence presentes;
- merge/split history mínima;
- no-match y ambiguity explícitos.

No resuelve identidad.

### 15.6 Library Curation Engine

Puede consumir scorecards, findings y gating decisions para priorización. Este motor no cura.

### 15.7 Governance Layer

Puede definir política de bloqueo, perfiles permitidos y excepciones gobernadas. Este motor no cambia política constitucional.

### 15.8 Evaluation/Conformance Engine

Debe poder auditar:

- reglas aplicadas;
- estabilidad entre corridas;
- findings repetitivos;
- pass con warnings;
- coherencia de outcomes.

## 16. Qué partes pueden automatizarse y cuáles no

### Automatizable

- chequeos de schema y campos requeridos;
- chequeos de refs y versionado;
- chequeos de staleness contra ventanas explícitas;
- chequeos de coherencia de estados;
- aplicación de perfiles por object type y fase;
- derivación de `PASS`, `PASS_WITH_WARNINGS`, `FAIL`;
- generación de scorecards derivadas.

### No automatizable soberanamente

- redefinir si un contrato está bien diseñado;
- declarar que un objeto ya es decision-grade o verification-grade en sentido fuerte;
- levantar blocks por intuición fuera de regla explícita;
- reinterpretar un warning como irrelevante por conveniencia;
- compensar faltas materiales con “buen score”.

## 17. Qué rol permitido y prohibido puede tener un LLM dentro de este motor

### Permitido

- redactar resumen humano de findings ya calculados;
- ayudar offline a proponer nuevas reglas para revisión humana;
- agrupar patrones repetitivos para análisis posterior.

### Prohibido

- decidir `PASS` o `FAIL`;
- determinar severidad soberana;
- inferir provenance faltante;
- corregir objetos;
- levantar o bajar bloqueos;
- sustituir rule execution determinista.

El runtime del motor debe ser deterministic-first y rule-driven.

## 18. Qué acceptance tests mínimos debe tener

Acceptance tests mínimos:

- objeto íntegro y trazable que pasa sin findings;
- objeto con warnings no bloqueantes que sale `PASS_WITH_WARNINGS`;
- objeto con campos obligatorios faltantes que falla por calidad;
- objeto con lineage/provenance faltante que falla por trazabilidad;
- objeto estructuralmente correcto pero no apto para uso de fase superior;
- bundle con dependencia stale que falla por contract/traceability;
- parsed table parcial útil que pasa con warnings;
- objeto con contract version vieja que falla por contract violation;
- misma entrada + mismas versiones de reglas/contratos = mismo resultado;
- scorecard alta con block presente sigue terminando en `FAIL`.

## 19. Qué observabilidad debe exponer

Observabilidad mínima:

- conteo de evaluaciones por object type y fase;
- conteo de outcomes `PASS`, `PASS_WITH_WARNINGS`, `FAIL`;
- distribución por severidad;
- top rules que más fallan;
- top object types con fallos repetitivos;
- tasa de pass con warnings;
- tasa de fallos por trazabilidad;
- tasa de fallos por staleness;
- drift entre versiones de reglas;
- re-evaluation reproducibility rate.

No como dashboard obligatorio, sino como eventos y registros consultables.

## 20. Qué failure modes deben bloquearse desde el día 1

Debe bloquearse desde el inicio:

- objeto sin provenance mínima que pasa;
- objeto sin version refs críticas que pasa;
- scorecard que oculta hard failures;
- evaluación sin contract version registrada;
- evaluación sin declared intended use cuando se pide fitness;
- profile implícito o adivinado;
- dependencia stale permitida en handoff crítico;
- uncertainty/conflict omitidos en objetos que los requieren;
- pass emitido sin guardar rules aplicadas;
- evaluación que muta el objeto evaluado.

## 21. Qué errores de arquitectura serían muy caros de corregir después

Errores caros:

- un único score global como output principal;
- mezclar evaluación estructural con fitness en una sola capa opaca;
- no versionar reglas, perfiles y contratos usados;
- hardcodear checks por objeto en un único archivo monolítico;
- no separar findings por categoría semántica;
- no preservar rationale y evidence refs;
- permitir side effects sobre el objeto evaluado;
- no modelar handoff como contexto explícito;
- no distinguir sparse declarado de sparse oculto.

## 22. Cómo diseñarlo para MVP sin volverlo mediocre

MVP serio significa:

- reglas explícitas, no cientos de heurísticas;
- perfiles mínimos por object family y fase;
- severidades simples pero duras;
- outcomes simples pero disciplinados;
- findings tipados;
- replay garantizable;
- scorecard opcional y subordinada.

No hace falta:

- engine de policy complejo;
- UI;
- explainability ornamental;
- weighting sofisticado desde el día 1.

Sí hace falta:

- determinismo;
- trazabilidad;
- rule versioning;
- gating claro;
- separación entre calidad, trazabilidad y fitness.

## 23. Cómo escalarlo sin volverlo un monolito

Escalabilidad sana:

- separar profiles por object family;
- separar rules por dimensión;
- separar object checks de handoff checks;
- mantener issue model único y estable;
- versionar rule sets y profiles;
- permitir agregar nuevos object types sin reescribir el core;
- mantener orquestación pequeña y rules modulares.

No escalar mediante:

- `if/elif` infinitos por fase;
- reglas mezcladas con acceso a infraestructura;
- scores especiales por cliente o caso sin profile formal;
- excepciones invisibles.

## 24. Una estructura mínima sugerida para pasar luego a código

```text
quality_fitness_evaluation_engine/
  domain/
    enums.py
    value_objects.py
    models.py
  profiles/
    object_profiles.py
    phase_profiles.py
    handoff_profiles.py
  rules/
    structural_rules.py
    traceability_rules.py
    contract_rules.py
    fitness_rules.py
  evaluation/
    structural_evaluator.py
    traceability_evaluator.py
    contract_evaluator.py
    fitness_evaluator.py
    orchestrator.py
  results/
    issue.py
    dimension_result.py
    evaluation_report.py
    scorecard.py
    replay_manifest.py
  tests/
    test_structural_evaluation.py
    test_traceability_evaluation.py
    test_contract_evaluation.py
    test_fitness_evaluation.py
    test_replay_stability.py
```

## Ejemplos obligatorios

### Ejemplo 1. Benchmark bundle correcto en calidad, insuficiente para agenda de validación Fase 2

Caso:

- `benchmark_bundle` con schema correcto;
- provenance presente;
- source refs válidas;
- uncertainty markers presentes;
- coverage adecuada para Fase 1 comparativa;
- pero sin granularidad por subsistema ni evidencia gap linkage para Fase 2.

Evaluación correcta:

- **quality**: `PASS`
- **traceability**: `PASS`
- **contract** para bundle de Fase 1: `PASS`
- **fitness para uso “alimentar validation_queue Fase 2”**: `FAIL`

Finding principal:

- `fitness_failure.granularity_insufficient`

Regla crucial:

- el motor no debe degradar este objeto a “malo” en general;
- debe registrar que es estructuralmente correcto pero no apto para ese uso específico.

### Ejemplo 2. `facility_prior` sin uncertainty markers y sin source dependencies

Caso:

- `facility_prior` completo en campos descriptivos;
- pero sin `uncertainty_markers`;
- sin `source_dependencies`;
- sin lineage explícito hacia supuestos previos.

Evaluación correcta:

- no es solo warning;
- es **failure material** porque el objeto pierde límites epistemológicos y trazabilidad de soporte.

Clasificación:

- `traceability_failure.missing_source_dependencies`
- `epistemic_insufficiency.missing_uncertainty_markers`

Outcome:

- `FAIL`

El motor no debe:

- inventar uncertainty markers;
- asumir que el prior “ya se entiende”.

### Ejemplo 3. `output_block` bien formado pero dependiente de `tension_map` stale

Caso:

- `output_block` cumple schema;
- audience metadata correcta;
- export metadata correcta;
- pero depende de `tension_map` versión vieja respecto del contract vigente.

Evaluación correcta:

- calidad estructural: `PASS`
- trazabilidad: puede pasar si la ref existe
- contract/fitness de handoff: `FAIL`

Finding principal:

- `contract_violation.stale_dependency`
- o `traceability_failure.dependency_version_stale` según profile

El motor no debe:

- refrescar el `tension_map`;
- reemplazar refs;
- recomputar dependencias.

Solo debe bloquear y explicar.

### Ejemplo 4. `required_site_evidence_register` completo en campos, con contract refs viejas

Caso:

- objeto bien formado;
- campos presentes;
- lineage presente;
- pero `contract_version_ref` apunta a versión anterior al contract activo para Fase 4.

Evaluación correcta:

- calidad estructural: `PASS`
- traceability: `PASS`
- contract: `FAIL`

Finding principal:

- `contract_violation.contract_version_outdated`

Esto demuestra:

- “bien formado” no equivale a “válido para uso actual”.

### Ejemplo 5. `parsed_table` incompleto pero útil para normalización parcial

Caso:

- tabla parseada con filas válidas;
- algunas columnas no extraídas;
- provenance por página y tabla preservada;
- `partial_parse_status` explícito;
- warnings registrados.

Evaluación correcta para uso “normalización parcial”:

- calidad: `PASS_WITH_WARNINGS`
- traceability: `PASS`
- fitness para normalización parcial: `PASS_WITH_WARNINGS`

Warnings:

- `quality_warning.partial_table_extraction`
- `quality_warning.missing_columns_declared`

No debe ocurrir:

- pasar como tabla completa;
- ocultar el carácter parcial.

### Ejemplo 6. Reconstrucción de por qué un objeto pasó hace meses

Para reconstrucción exacta, este motor debe guardar:

- `evaluation_run_record`
- `target_object_version_ref`
- `dependency_version_refs`
- `contract_ref`
- `contract_version_ref`
- `evaluation_profile_ref`
- `profile_version`
- `rule_set_version`
- `evaluator_version`
- findings completos
- dimension assessments
- outcome final
- gating decision
- rationale summary
- `executed_at`

Con eso se puede responder:

- qué objeto exacto fue evaluado;
- contra qué contrato;
- con qué reglas;
- con qué dependencias;
- y por qué pasó, pasó con warnings o falló.

## Cierre conceptual

Definición operativa final:

- **calidad** en ZLab es conformidad estructural, trazable y contractual con límites explícitos;
- **fitness-for-use** es adecuación para un uso declarado, no bondad abstracta;
- este motor no decide verdad ni soberanía epistemológica;
- este motor decide si un objeto puede o no puede usarse de una manera concreta sin violar disciplina del framework.
