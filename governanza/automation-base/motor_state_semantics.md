# motor_state_semantics.md

## 1. Objetivo

### Confirmado
Este archivo fija la semántica mínima del estado del motor para que `motor_schema.json` no produzca combinaciones incoherentes ni usos ambiguos de `closed`.

### Inferido con alta confianza
Su función es volver operables los campos ya existentes, no inventar estados nuevos.

### Pendiente o ambiguo
No está definido todavía si esta semántica se convertirá después en validación automática formal del JSON.

---

## 2. Campos de estado que ya existen

### Confirmado
Los campos mínimos ya existentes y relevantes para estado son:
- `current_stage`
- `stage_sequence`
- `completed_stages`
- `status`
- `blocked`
- `paused`
- `waiting_on`
- `closure`
- `updated_at`

### Inferido con alta confianza
La semántica correcta debe usar estos campos en combinación, no de forma aislada.

### Pendiente o ambiguo
No existe todavía un esquema más fino de subestados internos por etapa.

---

## 3. Significado exacto de `closed`

### Confirmado
La semántica mínima estable es esta:
- una etapa cerrada significa que esa etapa aparece en `completed_stages`;
- un motor cerrado significa que:
  - `current_stage = closed`
  - `status = closed`
  - `closure.is_closed = true`

Además:
- `closed_at` solo debe tener valor cuando `closure.is_closed = true`;
- `waiting_on` debe ser `null` cuando el motor está cerrado;
- `blocked` y `paused` deben ser `false` cuando el motor está cerrado.

### Inferido con alta confianza
Expresiones como:
- `closed for implementation`
- `closed for integration`
- `closed as stable reference`

pueden seguir usándose como lenguaje descriptivo en documentos, pero no deben tratarse todavía como estados serializables distintos dentro de `motor_schema.json`.

### Pendiente o ambiguo
No está definido todavía si en el futuro se agregará una tipificación formal adicional para distinguir esos cierres más finos.

---

## 4. Combinaciones mínimas válidas

### Confirmado
Las combinaciones mínimas válidas son estas:

### 4.1 Estado `not_started`
- `status = not_started`
- `closure.is_closed = false`
- `blocked = false`
- `paused = false`
- `waiting_on = null`
- `current_stage` debe ser una etapa del workflow, no `closed`

### 4.2 Estado `in_progress`
- `status = in_progress`
- `closure.is_closed = false`
- `blocked = false`
- `paused = false`
- `current_stage` debe ser una etapa del workflow, no `closed`

### 4.3 Estado `ready_for_next_stage`
- `status = ready_for_next_stage`
- `closure.is_closed = false`
- `blocked = false`
- `paused = false`
- `current_stage` debe seguir siendo una etapa del workflow, no `closed`
- la etapa actual debe estar suficientemente completada como para permitir transición

### 4.4 Estado `waiting`
- `status = waiting`
- `closure.is_closed = false`
- `waiting_on` no debe ser `null`
- `blocked = false`
- `paused = false`

### 4.5 Estado `blocked`
- `status = blocked`
- `closure.is_closed = false`
- `blocked = true`
- `paused = false`

### 4.6 Estado `paused`
- `status = paused`
- `closure.is_closed = false`
- `paused = true`
- `blocked = false`

### 4.7 Estado `closed`
- `status = closed`
- `current_stage = closed`
- `closure.is_closed = true`
- `blocked = false`
- `paused = false`
- `waiting_on = null`

### Inferido con alta confianza
Estas reglas son suficientes para evitar la mayoría de estados imposibles sin introducir nuevos enums ni nuevas etapas.

### Pendiente o ambiguo
No está definido todavía si `completed_stages` debe exigirse estrictamente en orden o si bastará con que sea un subconjunto válido de `stage_sequence`.

---

## 5. Combinaciones mínimas inválidas

### Confirmado
Deben tratarse como inválidas, al menos, estas combinaciones:
- `status = closed` con `current_stage` distinto de `closed`;
- `closure.is_closed = true` con `blocked = true`;
- `closure.is_closed = true` con `paused = true`;
- `closure.is_closed = true` con `waiting_on != null`;
- `blocked = true` y `paused = true` al mismo tiempo;
- `status = waiting` con `waiting_on = null`.

### Inferido con alta confianza
También debe tratarse como inválido marcar un motor como cerrado si todavía faltan etapas sustantivas del workflow sin completar.

### Pendiente o ambiguo
No está definido todavía si el propio `motor_schema.json` incorporará luego validadores formales para estas combinaciones.

---

## 6. Relación entre cierre de etapa y cierre de motor

### Confirmado
- `completed_stages` registra cierres de etapa.
- `closure` registra cierre del motor.
- Un motor puede tener varias etapas cerradas sin estar todavía cerrado como motor.
- El cierre del motor es posterior al cierre satisfactorio de todas las etapas requeridas por el workflow.

### Inferido con alta confianza
La automatización no debe confundir una etapa completa con un motor completo.

### Pendiente o ambiguo
No está completamente formalizado todavía si todos los motores exigirán siempre las seis etapas del workflow antes de poder cerrarse.
