# Master Concept Document — Cross-Layer Conflict Engine

Motor ID: motor_040

## purpose
Cross-Layer Conflict Engine detecta contradicciones entre abstracción estructural, variables dominantes, supuestos financieros, permisos de claim y acciones de decisión. Su función es decir cuándo el caso contiene capas que parecen compatibles por separado pero se invalidan mutuamente al juntarlas. No reencuadra todavía el problema ni decide la acción final; deja explícito el registro de conflictos que los motores posteriores deben respetar.

## what_it_does
- toma `system_abstraction`, `dominant_variable_register`, supuestos financieros, permisos de claim y frentes de decisión;
- construye `cross_layer_conflict_register` con conflicto, capas involucradas, por qué importa, qué lo confirma, qué lo falsifica y posible dirección de rediseño;
- si la lógica estructural no produce conflictos propios, traduce el `cross_layer_congruence_register` de `motor_051` a la superficie de conflicto formal del lane estructural;
- expone `cross_layer_conflict_count` para observabilidad y gating downstream.

## what_it_does_not_do
- no reescribe el problem frame final; eso pertenece a `motor_041`;
- no convierte conflicto en decisión estratégica final;
- no borra conflictos porque el caso “se vea prometedor”;
- no trata contradicciones como errores de datos automáticamente: las deja explícitas hasta que haya evidencia para resolverlas;
- no sustituye fairness o correlation logic de `motor_051`.

## why_it_exists
Existe como motor separado porque el framework necesitaba una frontera entre “ya tengo variables y abstracción” y “esas capas son internamente coherentes”. Sin esta capa, el sistema podía avanzar con CAPEX, comparabilidad o claims sobre una mezcla inconsistente de regulación, control, proceso y finanzas.
