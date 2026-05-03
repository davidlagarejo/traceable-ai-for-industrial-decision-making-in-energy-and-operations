# stage_artifact_semantics.md

## 1. Objetivo

### Confirmado
Este archivo fija la semántica mínima entre etapas del workflow y artefactos, para evitar que una herramienta confunda:
- una etapa del proceso;
- con un artefacto producido en esa etapa;
- o con un artefacto temprano que luego se refina en una etapa posterior.

### Inferido con alta confianza
La tensión principal a resolver es la relación entre:
- `acceptance_tests` y `test_spec`;
- `failure_modes` y `failure_modes_spec`;
- `conformance_review` y `conformance_review_report`.

### Pendiente o ambiguo
No está definido todavía si en el futuro esta semántica se volverá más detallada por tipo de motor.

---

## 2. Distinción mínima entre etapa y artefacto

### Confirmado
- Una etapa es un tramo del workflow del motor.
- Un artefacto es una salida documental o técnica producida, refinada o requerida por una etapa.
- Una etapa puede tener más de un artefacto.
- Un artefacto temprano puede ser refinado posteriormente por otra etapa sin que eso cree una etapa nueva.

### Inferido con alta confianza
La automatización debe pensar primero en etapas del workflow y después en artefactos requeridos o producidos por cada etapa.

### Pendiente o ambiguo
No está definido todavía si en algunos motores habrá subetapas internas formales.

---

## 3. Semántica de `acceptance_tests` y `test_spec`

### Confirmado
La semántica mínima estable es esta:
- `acceptance_tests` pertenece a `documentation_base`.
- `acceptance_tests` define, a nivel conceptual, qué debe probarse para considerar que el motor cumple su función mínima.
- `test_spec` pertenece a la etapa `tests`.
- `test_spec` refina técnicamente esa base y la convierte en especificación de pruebas más concreta y utilizable antes o durante la implementación.

Por tanto:
- `acceptance_tests` no sustituye a `test_spec`;
- `test_spec` no invalida a `acceptance_tests`;
- `test_spec` deriva y concreta lo ya definido en `acceptance_tests`.

### Inferido con alta confianza
Esto permite mantener coherencia entre documentación base y etapa posterior de tests sin duplicarlas como si fueran la misma cosa.

### Pendiente o ambiguo
No está definido todavía si `test_spec` será siempre solo documental o si incluirá siempre tests ejecutables ligados a implementación.

---

## 4. Semántica de `failure_modes` y `failure_modes_spec`

### Confirmado
La semántica mínima estable es esta:
- `failure_modes` pertenece a `documentation_base`.
- `failure_modes` enumera, a nivel conceptual, cómo puede degradarse el motor y qué riesgos deben vigilarse.
- `failure_modes_spec` pertenece a la etapa `failure_modes`.
- `failure_modes_spec` refina técnicamente esa base y la convierte en especificación más concreta para validación, diseño e implementación.

Por tanto:
- `failure_modes` no sustituye a `failure_modes_spec`;
- `failure_modes_spec` no elimina la necesidad de `failure_modes` en documentación base;
- `failure_modes_spec` deriva y concreta la base documental previa.

### Inferido con alta confianza
Esto resuelve la ambigüedad sin colapsar la etapa `failure_modes` dentro de `documentation_base`.

### Pendiente o ambiguo
No está definido todavía si `failure_modes_spec` será puramente documental o si luego se enlazará a validadores automáticos más formales.

---

## 5. Semántica de `conformance_review` y `conformance_review_report`

### Confirmado
La semántica mínima estable es esta:
- `conformance_review` es una etapa del workflow.
- `conformance_review_report` es el artefacto mínimo que resulta de esa etapa.
- La etapa existe para verificar que la implementación respeta contrato, límites, metadatos críticos y separación de responsabilidades.
- El reporte documenta el resultado de esa revisión.

### Inferido con alta confianza
La etapa puede estar asistida por validación automática o revisión humana, pero el artefacto mínimo persistente de salida sigue siendo el reporte.

### Pendiente o ambiguo
No está completamente formalizado todavía quién ejecuta esta revisión, qué mezcla exacta de automatización y revisión humana tendrá, o si dependerá después de un motor transversal más fuerte.

---

## 6. Regla operativa para automatización

### Confirmado
Una herramienta debe interpretar así la relación etapa/artefacto:
- `documentation_base` produce artefactos base de definición;
- `schema_technical` produce `technical_schema`;
- `tests` produce `test_spec` a partir de aceptación ya definida;
- `failure_modes` produce `failure_modes_spec` a partir de riesgos ya definidos;
- `implementation` produce `codebase` y `usage_example`;
- `conformance_review` produce `conformance_review_report`.

### Inferido con alta confianza
Esto permite automatizar transiciones sin tratar como contradicción lo que en realidad es relación entre definición temprana y refinamiento posterior.

### Pendiente o ambiguo
No está definido todavía si todos los motores producirán exactamente el mismo nivel de detalle en cada artefacto refinado.
