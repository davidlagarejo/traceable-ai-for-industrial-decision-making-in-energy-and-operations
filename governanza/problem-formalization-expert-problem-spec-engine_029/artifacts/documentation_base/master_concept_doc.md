# Master Concept Document — Problem Formalization / Expert Problem Spec Engine

Motor ID: motor_029

<!-- MOTOR CONTEXT (read this before filling sections below)

purpose:        Convertir inference cases activados en especificaciones formales del problema: conocimiento experto, restricciones reales y supuestos explícitos del dominio.
why_it_exists:  Un dataset sintético sin especificación formal es ruido estructurado. Este motor produce el contrato del que depende toda la cadena sintética.
key_inputs:     inference_cases (motor_013), phase_contracts (motor_001), version_records (motor_002), canonical_taxonomy (motor_003)
key_outputs:    expert_problem_spec, ambiguity_register, parameter_constraints
key_objects:    ExpertProblemSpec, AmbiguityRegister, ParameterConstraint
what_not_to_do: No genera datos sintéticos. No corre ML. No puede ejecutarse sobre inference_cases con ambiguity_register crítico no resuelto.
design_notes:   Prerequisito obligatorio de toda la cadena sintética. No genera datos. No diseña modelos. Su output es non_evidentiary_flag=true.
epistemic_flags: non_evidentiary_flag=true, intended_use=exploration

All placeholder markers in this document have been replaced with concrete content.
-->

## purpose
Este motor convierte `inference_cases` activados en una especificación formal del problema lista para condicionar la cadena sintética. Su trabajo es explicitar conocimiento experto, restricciones reales del dominio, supuestos operativos, limites de validez y parametros que el generador sintetico podra respetar despues. El resultado no es evidencia de campo: es un contrato exploratorio, trazable y no evidentiary que define bajo que condiciones puede construirse soporte sintetico.

## what_it_does
- Recibe `inference_cases` activados desde `motor_013` y verifica que esten dentro de una fase permitida por `phase_contracts`.
- Lee `version_records` para preservar versionado, provenance y lineage de la formalizacion producida.
- Usa `canonical_taxonomy` para nombrar variables, entidades, dominios, unidades y categorias con terminos canonicos.
- Extrae del caso inferencial la pregunta formal, el objetivo analitico, el tipo de problema, los supuestos declarados y las restricciones del dominio.
- Produce `expert_problem_spec` con `non_evidentiary_flag=true`, `intended_use=exploration`, `source_problem_ref`, `domain_validity_limits` y `limitations_note`.
- Produce `ambiguity_register` con ambiguedades, severidad, decision requerida e impacto si no se resuelven.
- Produce `parameter_constraints` con rangos permitidos, unidades, dominios categoricos y reglas de compatibilidad para parametros de generacion.
- Registra handoff explicito hacia `motor_030` solo cuando no existen ambiguedades criticas sin resolver.

## what_it_does_not_do
- No genera datos sinteticos ni muestras simuladas.
- No corre ML, no entrena modelos y no compara algoritmos.
- No puede ejecutarse sobre `inference_cases` con `ambiguity_register` critico no resuelto.
- No valida claims con evidencia de campo ni reemplaza `Validation Data Bridge` o `Verification Bridge`.
- No modifica `inference_cases`, `phase_contracts`, `version_records` ni `canonical_taxonomy`; solo los consume como autoridad de entrada.
- No promueve el nivel epistemico de un claim; todo output permanece no evidentiary y de uso exploratorio.

## why_it_exists
Existe como motor separado porque la cadena sintetica necesita un contrato formal antes de generar datos, entrenar modelos o producir soporte preliminar. Sin esta capa, `motor_030` recibiria instrucciones ambiguas y produciria ruido estructurado; con esta capa, la generacion sintetica queda subordinada a conocimiento experto, restricciones reales, supuestos explicitos y limites epistemicos trazables.
