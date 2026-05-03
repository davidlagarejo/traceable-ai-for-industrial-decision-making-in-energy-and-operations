# Master Concept Document — Epistemic Governance Layer

Motor ID: motor_025

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Detectar tensiones estructurales, inflación de excepciones, insuficiencia taxonómica y distinguir cambio local, estructural o constitucional.
why_it_exists:  Evita que el framework crezca rompiendo su constitución en silencio.
key_inputs:     conformance_records (motor_022), governance_events (motor_024), phase_contracts (motor_001)
key_outputs:    epistemic_tension_record, constitutional_change_signal, governance_health_report
key_objects:    EpistemicTension, ConstitutionalSignal, GovernanceHealthReport
what_not_to_do: No modifica contratos ni políticas directamente. Solo detecta y señaliza tensiones estructurales.
design_notes:   Motor ligero (LIGHTWEIGHT_MOTOR). Capa de gobernanza de más alto nivel.

Documentation base completed for Gate 1 validation.
-->

## purpose
El Epistemic Governance Layer detecta tensiones estructurales en el framework a partir de registros de conformidad, eventos de gobernanza y contratos de fase. Su función es identificar inflación de excepciones, insuficiencia taxonómica y desviaciones que puedan indicar que un ajuste local ya no basta. Clasifica cada hallazgo como cambio local, estructural o constitucional sin modificar los contratos, políticas ni estados que analiza.

## what_it_does
- Recibe `conformance_records` producidos por motor_022 y extrae hallazgos de incumplimiento, severidad, alcance y referencias de contrato.
- Recibe `governance_events` producidos por motor_024 y agrupa excepciones, overrides, anomalías recurrentes y señales de tensión por clave de recurrencia.
- Recibe `phase_contracts` producidos por motor_001 y los usa como autoridad de límites, handoffs, inputs permitidos y outputs permitidos.
- Detecta patrones de excepción repetida, conflicto de límites entre fases, insuficiencia taxonómica declarada y drift de responsabilidades entre motores.
- Produce `epistemic_tension_record` con tipo de tensión, evidencia trazable, severidad, alcance afectado y regla de clasificación aplicada.
- Produce `constitutional_change_signal` cuando una tensión supera el nivel local y requiere revisión estructural o constitucional.
- Produce `governance_health_report` con un resumen del periodo evaluado, conteos por tipo de tensión, señales abiertas y estado de salud de gobernanza.

## what_it_does_not_do
- No modifica contratos, políticas, taxonomías, artefactos, estados de motor ni reglas de workflow directamente.
- No resuelve excepciones ni aprueba overrides; solo detecta y señaliza tensiones estructurales.
- No reemplaza a motor_022 en evaluación de conformidad ni recalcula sus resultados.
- No reemplaza a motor_024 en el registro primario de eventos y excepciones.
- No crea nuevas categorías taxonómicas ni decide canonical terms; solo identifica insuficiencia taxonómica cuando las entradas ya contienen señales trazables.
- No convierte señales de gobernanza en decisiones finales; toda señal estructural o constitucional requiere revisión externa al motor.

## why_it_exists
Existe como motor separado porque la conformidad local y el registro de excepciones no bastan para saber cuándo el framework está acumulando tensión sistémica. Es una capa ligera de gobernanza de alto nivel que observa contratos, eventos y revisiones para impedir que el sistema crezca rompiendo su constitución en silencio.
