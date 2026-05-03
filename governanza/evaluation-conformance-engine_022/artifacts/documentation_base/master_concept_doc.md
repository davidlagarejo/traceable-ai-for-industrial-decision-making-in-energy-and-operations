# Master Concept Document — Evaluation / Conformance Engine

Motor ID: motor_022

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Verificar que motores, datasets y artefactos respetan contrato, límites y conformidad arquitectónica.
why_it_exists:  Evita degradación silenciosa del sistema con el tiempo.
key_inputs:     phase_contracts (motor_001), version_records (motor_002), quality_records (motor_007), harness_results (motor_021)
key_outputs:    conformance_record, violation_log, architectural_drift_signal
key_objects:    ConformanceRecord, ViolationRecord, DriftSignal
what_not_to_do: No corrige violaciones. No modifica el sistema. Solo detecta y registra conformidad.
design_notes:   Evaluación formal de conformidad. Depende de motor_001, motor_002, motor_007 y motor_021.

Sections below are completed with motor-specific content.
-->

## purpose
El Evaluation / Conformance Engine verifica que motores, datasets y artefactos respeten los contratos, limites y criterios de conformidad arquitectonica ya definidos por el framework. Recibe contratos de fase, registros de versionado, evaluaciones de calidad y resultados de harness para emitir una lectura formal de cumplimiento. Su salida no altera los objetos evaluados: registra conformidad, violaciones y senales de drift arquitectonico.

## what_it_does
- Recibe `phase_contracts` producidos por `motor_001` como autoridad de obligaciones, limites y handoffs por fase.
- Recibe `version_records` producidos por `motor_002` para verificar lineage, versionado y comparabilidad historica de los objetos evaluados.
- Recibe `quality_records` producidos por `motor_007` para incorporar resultados de aptitud estructural, completitud y trazabilidad.
- Recibe `harness_results` producidos por `motor_021` para evaluar evidencia de pruebas sobre datasets, contratos, handoffs y objetos.
- Compara cada objeto evaluado contra el contrato aplicable y clasifica el resultado como `PASS`, `WARNING` o `FAIL`.
- Genera un `conformance_record` por unidad evaluada con referencias a contrato, version, quality record y harness result usados.
- Genera un `violation_log` con violaciones materiales, severidad, regla incumplida y evidencia de entrada.
- Genera un `architectural_drift_signal` cuando las violaciones o warnings indican desviacion persistente respecto al contrato o a los limites del motor.

## what_it_does_not_do
- No corrige violaciones detectadas ni propone parches automaticos.
- No modifica motores, datasets, artefactos, contratos, registros de versionado, quality records ni resultados del harness.
- No decide cierre de motor por si solo; solo produce evidencia de conformidad consumible por procesos de gobernanza o revision.
- No reemplaza a `motor_007`: usa sus quality records como input, pero no recalcula calidad estructural desde cero.
- No reemplaza a `motor_021`: usa resultados de harness existentes, pero no ejecuta pruebas sobre objetos ni datasets.
- No inventa reglas de conformidad fuera de los contratos, registros y artefactos recibidos.

## why_it_exists
Existe como motor separado porque la conformidad formal requiere integrar evidencia de contrato, versionado, calidad y harness sin mezclarse con la produccion de esas evidencias. Su rol transversal evita degradacion silenciosa del sistema con el tiempo al convertir incumplimientos y drift arquitectonico en registros explicitos, auditables y no mutantes.
