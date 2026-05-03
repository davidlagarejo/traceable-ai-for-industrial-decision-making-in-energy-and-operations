# synthetic_epistemology_rules.md
# Reglas epistémicas para la cadena sintética y ML de ZLab

## Autoridad
Este archivo es fuente de verdad para la semántica epistémica de todos los outputs
producidos por los motores 029–033 (cadena sintética y ML).

Complementa `document_authority.md` y `motor_state_semantics.md`.
En caso de conflicto sobre el significado o el uso permitido de un output sintético,
este archivo prevalece sobre cualquier otro documento del framework en esa materia.

Su posición en la jerarquía documental queda fijada en `document_authority.md`.

---

## 1. Reglas constitucionales

### Confirmado
Las siguientes reglas son vinculantes para todo output de la cadena sintética y ML.
No tienen excepciones automáticas. Solo pueden suspenderse mediante comando `--force`
registrado en el audit trail con justificación explícita.

1. **Un output sintético nunca puede elevar el nivel epistémico de un claim.**
   Un `capability_demonstration_report` no convierte una hipótesis en decisión.
   Un modelo con AUC 0.95 sobre datos sintéticos no es evidencia de que el fenómeno
   real sea predecible.

2. **Los datos sintéticos no son evidencia local.**
   Un `synthetic_generation_run` no es un dataset de campo.
   No puede citarse como fuente de validación ni como soporte de verificación.
   No puede usarse en `Validation Data Bridge` ni en `Verification Bridge`.

3. **La especificación experta no es evidencia de campo.**
   Un `expert_problem_spec` es una formalización de conocimiento y supuestos,
   no una medición. Puede ser incorrecto. Puede estar sesgado. El sistema lo trata
   como contrato del generador, no como dato del mundo.

4. **El rendimiento del modelo no prueba nada sobre el mundo real.**
   El modelo aprendió a predecir dentro de las reglas del generador.
   La confusión entre este plano y el plano real es el failure mode más peligroso
   de la cadena.

5. **La incertidumbre del generador debe propagarse al output del modelo.**
   Si el generador usa parámetros con rango de incertidumbre, el output del modelo
   debe reflejar ese rango. No puede colapsarse a un punto.

6. **Synthetic support no sustituye a Validation Data Bridge ni a Verification Bridge.**
   La jerarquía evidentiary es:
   - `field_evidence` (evidencia de sitio, más fuerte)
   - `validation_data` (datos reales estructurados, evidentiary bajo condiciones)
   - `synthetic_support` (exploración bajo supuestos explícitos, no evidentiary)
   Esta jerarquía no es intercambiable. No puede invertirse.

7. **Todo output de la cadena debe llevar sus etiquetas epistémicas completas.**
   Un objeto sin etiquetas no puede registrarse en el sistema.
   El orquestador rechaza artefactos de esta cadena que no incluyan los campos
   obligatorios definidos en la sección 3 de este documento.

8. **El Decision Core solo puede recibir synthetic_support como señal subordinada.**
   No puede ser la fuente principal de un inference_record.
   Si el soporte sintético es la única señal disponible, el inference_record
   queda en estado `hypothesis_only`, nunca en `decision_grade`.

9. **Un inference_record basado principalmente en synthetic_support no puede
   convertirse en TAD final.**
   TAD final requiere evidencia de campo o al menos Validation Data Bridge.

10. **Los outputs sintéticos son inmutables una vez registrados.**
    No se pueden reetiqutar, promover ni modificar retroactivamente para
    elevar su nivel epistémico.

### Inferido con alta confianza
Una herramienta que evalúa outputs de esta cadena debe verificar la presencia de
los flags obligatorios antes de procesar el objeto. Si los flags faltan, el objeto
debe tratarse como inválido.

### Pendiente o ambiguo
No está definido todavía si existirá validación automática formal de los flags
en el pipeline de procesamiento downstream.

---

## 2. Jerarquía evidentiary del sistema

### Confirmado
La jerarquía de evidencia del sistema ZLab es esta, en orden descendente de fuerza:

| Nivel | Fuente | Motor productor | Uso permitido |
|---|---|---|---|
| `field_evidence` | Datos de sitio recolectados directamente | motor_018 (Validation Data Bridge), motor_019 (Verification Bridge) | Verificación, cierre de claims |
| `validation_data` | Datos reales estructurados y auditados | motor_018 | Soporte de decisión con restricciones |
| `library_knowledge` | Conocimiento curado y evaluado | motor_011 | Contexto, prior |
| `inference_result` | Resultado de inferencia sobre datos reales | motor_014 | Decisión bajo contrato explícito |
| `synthetic_support` | Capability demo sobre datos sintéticos | motor_031, motor_032 | Exploración, priorización preliminar |
| `expert_spec` | Especificación formal de conocimiento experto | motor_029 | Contrato del generador, no dato |

Ningún nivel puede actuar como sustituto del nivel superior.
El Decision Core puede recibir señales de cualquier nivel pero debe registrar
qué nivel es cada señal y qué peso relativo tuvo.

### Confirmado
Un objeto en nivel `synthetic_support` no puede ser promovido a nivel superior
por ninguna operación automática. Solo por inserción de evidencia real de campo.

---

## 3. Etiquetas epistémicas obligatorias

### Confirmado
Todo objeto producido por los motores 029–033 debe incluir los siguientes campos.
El orquestador valida su presencia en el gate de conformance review del motor
que los produce.

### 3.1 Campos obligatorios en todo objeto de la cadena

| Campo | Tipo | Valor | Aplica a |
|---|---|---|---|
| `synthetic_data_flag` | boolean | `true` | Outputs de motor_030, motor_031 |
| `synthetic_support_flag` | boolean | `true` | Outputs de motor_032, motor_033 |
| `non_evidentiary_flag` | boolean | `true` | Todos los outputs de 029–033 |
| `source_problem_ref` | string | `inference_case_id` de origen | Todos |
| `expert_spec_ref` | string | `expert_problem_spec.spec_id` | Todos excepto motor_029 |
| `generator_version` | string | semver del generador | Outputs de motor_030, motor_031 |
| `parameter_set` | dict | parámetros exactos del run | Outputs de motor_030, motor_031 |
| `intended_use` | enum | `exploration`, `capability_demo`, `preliminary_support` | Todos |
| `domain_validity_limits` | string | descripción del scope válido | Todos |
| `limitations_note` | string | texto explícito de limitaciones | Todos |

### 3.2 Campos adicionales por objeto

**Para `training_run_record` y `model_eval_summary`:**
- `training_data_ref`: referencia al `synthetic_generation_run.run_id`
- `generator_sensitivity_test`: resultado del test de sensibilidad del modelo a cambios en parámetros del generador

**Para `capability_demonstration_report`:**
- `gap_to_real_validation`: qué datos reales serían necesarios para validar la capacidad
- `gap_to_deployment`: qué faltaría para un modelo real en producción
- `known_failure_modes`: condiciones bajo las cuales el modelo falla en el contexto sintético

**Para `synthetic_ml_support_register`:**
- `support_level`: `exploratory`, `preliminary_signal`, o `capability_demo`
- `cannot_substitute`: lista explícita de qué no reemplaza este objeto

**Para `preliminary_priority_register`:**
- `ranking_basis`: qué señales se usaron para el ranking
- `rank_is_preliminary`: `true` (campo boolean obligatorio)
- `requires_real_evidence`: lista de qué evidencia real invalidaría o confirmaría el ranking

### Inferido con alta confianza
Un objeto de la cadena que llega al Decision Core sin los campos obligatorios completos
debe ser rechazado por el orquestador antes de ser procesado.

---

## 4. Usos prohibidos

### Confirmado
Los siguientes usos están prohibidos para todos los outputs de los motores 029–033:

- Cerrar un inference case basándose exclusivamente en soporte sintético.
- Citar un `synthetic_generation_run` como fuente de datos en un reporte técnico formal sin declararla sintética explícitamente.
- Usar un `capability_demonstration_report` como evidencia de validación de campo.
- Elevar un `inference_record` de `hypothesis_only` a `decision_grade` usando solo señales sintéticas.
- Sustituir la etapa de Validation Data Bridge con datos sintéticos.
- Sustituir la etapa de Verification Bridge con datos sintéticos.
- Producir un modelo serializado listo para producción dentro del motor_031 (este motor produce solo `capability_demonstration_report`, no artefactos de producción).
- Elegir un modelo ML "porque suena mejor" en lugar de por adecuación al `problem_class` del spec.
- Usar un ranking de variables producido por ML sobre datos sintéticos como evidencia de causalidad real.
- Construir un `expert_problem_spec` desde texto libre sin estructura formal ni revisión experta.
- Ejecutar motor_030 sobre un spec en estado `draft` o con `ambiguity_register` con ítems críticos no resueltos.

### Confirmado
Un output del motor_033 (`preliminary_priority_register`) nunca puede ser TAD final.
Solo puede ser insumo para orientar el esfuerzo analítico hacia evidencia real.

---

## 5. Política de selección de modelos

### Confirmado
La política de selección de modelos es vinculante para el motor_031.
El `experiment_config` de un experimento debe declarar el `problem_class` tomado
del `expert_problem_spec`, y los modelos a evaluar deben ser coherentes con ese class.

### 5.1 Mapeo problem_class → familias candidatas

| Problem class | Baseline obligatorio | Nivel 2 | Nivel 3 | Cuándo no usar ML |
|---|---|---|---|---|
| `anomaly_detection` (labeled) | Logistic Regression | Random Forest | Isolation Forest | Si control estadístico (±3σ) ya detecta 90%+ |
| `anomaly_detection` (unlabeled) | Control estadístico | Isolation Forest | DBSCAN | Si el spec tiene <50 muestras |
| `classification_binary` | Logistic Regression | Random Forest | Gradient Boosting | Si regla determinista resuelve el problema |
| `classification_multiclass` | Decision Tree (depth≤4) | Random Forest | Gradient Boosting | Si el spec tiene ambigüedades críticas no resueltas |
| `regression_continuous` | Linear Regression | Random Forest Regressor | Gradient Boosting | Si la relación es lineal y el spec lo confirma |
| `regression_interval` | Quantile Regression | Gradient Boosting (quantile) | Bayesian Ridge | Raramente justificado en cadena sintética |
| `ranking` | Spearman correlation | RF feature importance | SHAP values | Si el experto ya tiene ranking basado en dominio |
| `clustering_exploratory` | k-Means (k por Elbow+Silhouette) | DBSCAN | PCA + visualización | Si el objetivo es predictivo, no exploratorio |
| `survival_hazard` | Kaplan-Meier | Cox PH | — | Si el spec no declara explícitamente tiempo-hasta-evento |
| `sensitivity_analysis` | ANOVA / índices de Sobol | Surrogate model | — | Si el análisis es paramétrico y el spec lo soporta |

### 5.2 Criterio de selección del modelo final

El modelo seleccionado es el que cumple estos cuatro criterios en orden de precedencia:

1. Supera el threshold de `primary_metric` definido en `experiment_config`
2. Es estable entre scenarios del bundle (variación ≤15% relativa)
3. Pasa el `generator_sensitivity_test` (cambio de parámetros del generador no colapsa la métrica)
4. Es tan simple como sea posible (entre modelos que cumplen 1, 2 y 3, gana el más interpretable)

Si ningún modelo cumple los cuatro criterios, `model_eval_summary.selected_model` queda en `null`
y el `capability_demonstration_report` documenta que la capacidad no pudo demostrarse bajo
las condiciones del spec. Esto es información válida, no un fracaso del sistema.

### 5.3 Cuándo NO usar ML

- El problema es resoluble con reglas deterministas derivadas del spec.
- El dataset sintético tiene menos de 50 muestras.
- El `ambiguity_register` del spec tiene ítems con `impact_if_unresolved = critical`.
- El `generator_sensitivity_test` muestra inestabilidad severa (>20% de variación en métrica ante cambio de parámetro dentro de rango de incertidumbre del spec).
- El objetivo real es producir una cifra para justificar una decisión ya tomada.
- La pregunta del spec es causal. ML sobre datos sintéticos no puede responder preguntas causales.

### Inferido con alta confianza
Un experimento que elige nivel 3 (gradient boosting, modelos complejos) sin haber
evaluado el baseline obligatorio primero no cumple la política y no puede pasar
el conformance review del motor_031.

---

## 6. Qué sigue abierto o ambiguo

### Confirmado
Siguen abiertos o ambiguos, y no deben cerrarse automáticamente:

- Si existirá validación automática formal de los flags epistémicos en el pipeline downstream.
- El umbral exacto de variación aceptable en el `generator_sensitivity_test` (hoy: 20% como referencia, pero puede ajustarse por dominio).
- Si el `preliminary_priority_register` requerirá revisión humana explícita antes de ser consumido por el Decision Core.
- Si se permitirá en el futuro que algunos outputs de nivel `synthetic_support` sean promovidos a `validation_data` mediante un proceso formal de campo que los corrobore.

### Inferido con alta confianza
La regla de no-promoción automática de outputs sintéticos debe mantenerse mientras no
exista un protocolo formal y auditado de corroboración de campo.
