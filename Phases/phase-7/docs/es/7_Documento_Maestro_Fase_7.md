# 7_Documento_Maestro_Fase_7
## Capa cognitiva y actualización de creencias

> Nota de espejo canónico: este documento es el reflejo en español de `Phases/phase-7/docs/en/7_Phase_7_Master_Document.md`. Debe mantenerse semánticamente alineado con ese documento. Si aparece una divergencia transitoria de traducción, la versión canónica en inglés gobierna hasta resincronización explícita.

## 1. Objetivo

Definir la Fase 7 como la capa gobernada de actualización de creencias del framework. Su función es decidir cómo cambian claims, rangos, frentes de aplicabilidad, estados del twin, exposición financiera y prioridades cuando entra nueva evidencia, cuando aparecen contradicciones o cuando falla un intento de endurecimiento.

## 2. Por qué importa

Sin una capa cognitiva gobernada, el framework sufriría una de dos fallas:

- nada se actualizaría rigurosamente y las hipótesis tempranas sobrevivirían sin ser desafiadas;
- o todo se actualizaría informalmente por intuición, tono o preferencia del analista.

La Fase 7 existe para volver la revisión una función arquitectónica de primera clase y no un efecto secundario invisible.

## 3. Qué es la Fase 7 y qué no es

La Fase 7 es:

- una capa de gobernanza de creencias,
- una capa de preservación de contradicción,
- una capa de transición de estados,
- y una capa de linaje de revisiones.

La Fase 7 no es:

- un motor de intuición,
- un editor libre de confianza,
- un simulador de consenso,
- ni un optimizador narrativo silencioso.

## 4. Unidad epistemológica central

La unidad central de la Fase 7 es el **`belief_revision_event`**.

Esta es la unidad correcta porque cualquier update legítimo debe quedar atado a:

- un claim u objeto previo,
- un trigger de evidencia o regla formal,
- una consecuencia de estado,
- y una razón trazable.

## 5. Problemas que resuelve la Fase 7

La Fase 7 existe para resolver:

- promoción silenciosa de claims;
- downgrades inexplicados;
- smoothing de contradicciones;
- cambios opacos de confianza;
- y evolución no reconstruible del modelo.

## 6. Inputs autorizados

La Fase 7 puede consumir:

- outputs de Fases 1 a 6, y estados ya emitidos por Fase 8 cuando deban revisarse;
- eventos de evidencia de todas las clases admitidas;
- contradiction records;
- resultados de validación fallidos y exitosos;
- override records;
- publication states;
- y reglas explícitas del framework provenientes de Fase 0.

## 7. Outputs autorizados

La Fase 7 está autorizada a producir:

- `belief_revision_log`
- `contradiction_register`
- `persistent_contradiction_register`
- `status_transition_map`
- `evidence_impact_map`
- `upgrade_hold_block_register`
- `dependency_propagation_map`
- `publication_consequence_register`
- `claim_lifecycle_register`

### 7.1 Objetos operativos requeridos

Para volver operable a la Fase 7 y no solo principista, se requieren los siguientes objetos operativos:

- `update_trigger_taxonomy`
- `dependency_edge_register`
- `revision_bundle`
- `persistent_contradiction_case`
- `publication_consequence_record`
- `claim_lifecycle_record`

Cada `belief_revision_event` debe registrar como mínimo:

- objeto objetivo;
- estado previo;
- evento disparador;
- tipo de dependencia;
- enunciado causal;
- impacto de alcance;
- alcance de propagación;
- consecuencia de publicación;
- y acción de ciclo de vida.

## 8. Outputs prohibidos

La Fase 7 no puede producir:

- reinterpretación no logueada;
- cambios de prioridad basados solo en intuición;
- borrado de historia contradictoria;
- certeza sintética por agregación;
- ni promoción de estado separada de un cambio explícito de soporte.

## 9. Familias de claims permitidas

Las siguientes son admisibles:

- `belief_state_change_claim`
- `contradiction_preservation_claim`
- `support_strength_change_claim`
- `do_not_upgrade_claim`
- `downgrade_justification_claim`
- `evidence_dependency_claim`

## 10. Familias de claims prohibidas

Las siguientes están prohibidas:

- `intuition_resolution_claim`
- `silent_consensus_claim`
- `narrative_upgrade_claim`
- `history_erasure_claim`

## 11. Outcomes centrales de update

La Fase 7 gobierna los siguientes outcomes centrales:

- `upgrade`
- `maintain`
- `degrade`
- `hold`
- `block`
- `do_not_upgrade`

Estos son outcomes estructurales, no moods del analista.

### 11.1 Taxonomía canónica de triggers

No debe ocurrir ningún update material sin un trigger clasificado. La taxonomía mínima de triggers es:

| Trigger | Significado típico |
| --- | --- |
| `evidence_arrived` | nueva evidencia admitida afecta un frente vivo |
| `evidence_retracted` | soporte previo deja de ser admisible |
| `validation_passed` | un intento de endurecimiento fortalece materialmente un frente |
| `validation_failed` | un intento de endurecimiento debilita o estrecha materialmente un frente |
| `contradiction_opened` | apareció un nuevo conflicto vivo |
| `contradiction_strengthened` | un conflicto existente se volvió más material |
| `classification_changed` | cambió el boundary o la clase del caso |
| `boundary_narrowed` | el claim solo sobrevive dentro de un domain más estrecho |
| `rule_changed` | una regla normativa cambió implicaciones aguas abajo |
| `upstream_status_changed` | una dependencia cambió en soporte o postura |

### 11.2 Semántica de dependency edges

Los tipos mínimos de dependencia son:

| Tipo de dependencia | Consecuencia de propagación por defecto |
| --- | --- |
| `support_dependency` | requiere revaluación sustantiva aguas abajo |
| `boundary_dependency` | deben recomputarse alcance y lenguaje aguas abajo |
| `regime_dependency` | deben re-chequearse superficies por escenario o modo |
| `threshold_dependency` | la postura puede quedarse en hold hasta que entre evidencia decisiva |
| `publication_dependency` | las superficies externas deben revisarse aunque sobreviva el razonamiento central |
| `action_dependency` | las prioridades de Fase 8 deben revisarse |

Las dependencias directas requieren revisión inmediata. Las dependencias transitivas requieren revisión registrada o registro de no-materialidad.

## 12. Modo low-data

En low-data, la Fase 7 sigue teniendo un trabajo crítico:

- registrar estados de soporte tempranos;
- preservar contradicción;
- marcar qué importaría después;
- y evitar convergencia prematura.

Incluso antes de que entre evidencia fuerte, el framework ya debe saber qué haría que un claim suba o baje.

## 13. Modo local-evidence

Cuando entran historian, bills, inspección, mediciones o evidencia más fuerte de clasificación, la Fase 7 debe:

- re-evaluar claims dependientes;
- propagar implicaciones a finanzas, regulación y TAD;
- y preservar el camino por el cual ocurrió el update.

## 14. Modo endurecido

La Fase 7 se vuelve especialmente importante a medida que el framework se endurece, porque evidencia fuerte que entra tarde puede:

- validar un frente,
- debilitar otro,
- estrechar el dominio de validez,
- o forzar que una prioridad antes atractiva quede bloqueada.

Cuanto más serio sea el caso, más seria debe volverse la disciplina de gobernanza de creencias.

## 15. Relación con Decision-grade y Verification-grade

La Fase 7 no crea `Decision-grade` ni `Verification-grade` por sí misma.

Su rol es asegurar que:

- `Decision-grade` no se conceda demasiado pronto,
- `Verification-grade` no se conceda ilegítimamente,
- y los outputs más fuertes sigan siendo auditables cuando aparezcan.

La Fase 7 es, por tanto, una fase de meta-gobernanza con consecuencias directas aguas abajo.

## 16. Relación con las otras fases

**Con Fase 1**  
Determina cuándo los priors físicos se estrechan, se ensanchan o mueren.

**Con Fase 2**  
Rastrea cambios en la confianza estructural del twin y en la validez de relaciones.

**Con Fase 3**  
Gobierna cómo se fortalecen o debilitan las hipótesis de régimen.

**Con Fase 4**  
Convierte resultados de endurecimiento en consecuencias formales de estado.

**Con Fase 5**  
Propaga revisiones técnicas hacia revisiones financieras.

**Con Fase 6**  
Propaga confirmación o colapso de triggers hacia postura de compliance.

**Con Fase 8**  
Reordena admisibilidad y prioridad cuando importan cambios del estado de creencias.

## 17. Regla mínima de update

Ningún cambio material de estado es legítimo salvo que estén presentes todos los siguientes elementos:

- objeto objetivo identificado;
- evento disparador identificado;
- relación causal o de dependencia declarada;
- estado de outcome asignado;
- techo semántico recomputado;
- consecuencia de publicación asignada;
- acción de ciclo de vida registrada;
- y linaje de revisión registrado.

## 18. Política de contradicción

La contradicción no es una falla que deba esconderse. Es una salida admisible y con frecuencia valiosa.

Cuando dos frentes materialmente vivos chocan:

- preserva ambos;
- baja fuerza injustificada cuando haga falta;
- eleva prioridad de validación si el conflicto importa;
- y no suavices narrativamente la colisión.

### 18.1 Outcomes para contradicción persistente

Cuando una contradicción no se resuelve rápido, la Fase 7 debe elegir un modo de manejo explícito:

- `coexist` cuando ambos frentes siguen vivos y la publicación puede seguir acotada;
- `split_scope` cuando cada frente solo sobrevive en un alcance distinto;
- `escalate_validation` cuando la contradicción debe subir prioridad de validación;
- `freeze_publication` cuando la publicación externa sería materialmente engañosa.

La contradicción persistente nunca debe tratarse como incomodidad silenciosa del analista.

### 18.2 Claim lifecycle y disciplina de memoria

La Fase 7 debe preservar estado de ciclo de vida para frentes materiales. Las acciones mínimas de lifecycle son:

- `retain`
- `narrow_scope`
- `supersede`
- `split_scope`
- `retire_from_surface`

Ningún frente previo puede desaparecer sin que quede registrada una de esas acciones.

### 18.3 Consecuencias de publicación

Todo update material debe declarar si causa:

- ningún cambio de publicación;
- publicación más estrecha;
- hold sobre superficies externas;
- block sobre superficies externas;
- o reapertura de una superficie antes held.

## 19. Reglas de upgrade

La Fase 7 solo puede autorizar upgrade cuando:

- un evento real de evidencia aumenta materialmente el soporte;
- cae incertidumbre decisiva;
- el boundary se preserva;
- y el lenguaje más fuerte sigue siendo proporcional al nuevo soporte.

## 20. Reglas de downgrade, hold y block

`degrade` aplica cuando evidencia más fuerte debilita la fuerza previa sin matar del todo el frente.

`hold` aplica cuando el frente sigue siendo material, pero una dependencia decisiva todavía impide cierre más fuerte.

`block` aplica cuando ya no se justifica seguir dedicando espacio metodológico o inversión metodológica a ese frente.

`do_not_upgrade` aplica cuando mejoró algo del soporte, pero una barrera nombrada todavía prohíbe lenguaje más fuerte.

## 21. Techo de lenguaje

El lenguaje preferido incluye:

- la evidencia ahora soporta una lectura más estrecha
- este frente sigue en hold a la espera de
- contradicción preservada entre
- solo se fortalece dentro de
- degradado porque
- bloqueado como frente activo porque

El lenguaje bloqueado incluye:

- ahora confirmado en general
- resuelto por juicio experto
- el consenso indica
- efectivamente cierto

## 22. Criterio de completitud

La Fase 7 se considera epistemológicamente cerrada cuando el framework puede:

- revisar cualquier frente material sin mutación silenciosa;
- explicar por qué ocurrió la revisión;
- preservar contradicción;
- propagar actualizaciones entre fases dependientes;
- preservar claim lifecycle y consecuencias de publicación;
- e impedir que emerja estatus más fuerte por retórica sola.
