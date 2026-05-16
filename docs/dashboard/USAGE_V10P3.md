# ZLab Dashboard V10 P3 — Guía de uso

## Cómo abrir

1. Click en **ZLab Dashboard** del Dock (`/Applications/ZLab Dashboard.app`)
2. El launcher mata cualquier instancia previa y arranca la versión más reciente
3. Navegador se abre automáticamente en `http://localhost:7474/`

## Páginas principales

- `/curar` — 6 casos canónicos · botón ▶ Correr framework
- `/corpus_curar` — estado de los 6 índices · 🔭 Discover · 🔬 IEEE/Springer
- `/revisar` — revisión de runs · approve scenarios
- `/log` — historial completo de runs
- `/knowledge` — 144 reglas aprobadas

## Flujo al correr un caso

Cada click ▶ Correr framework dispara el pipeline de 64 motors. V10 P3 wires que se ejecutan automáticamente:

| Phase | Motor | Qué inyecta |
|---|---|---|
| 1 | motor_028 | Discovery en vivo (Census/EPA/EIA/OSM/Playwright) |
| 1 | motor_012 | `regulatory_applicability_bundle` (regs aplicables a la familia) |
| 7 | motor_054 | `industry_evidence` por combinación (citations + reg_basis) |
| 8 | motor_033 | TAD priority bumped por corpus + reg signals |
| 3 | motor_019 | Narrator cita verbatim `[source_id::chunk_id]` |

## Verificación rápida (vía API)

```bash
# Estado del corpus
curl http://localhost:7474/api/corpus/index-status

# Estado de sesiones licensed
curl http://localhost:7474/api/corpus/licensed-session-status

# Casos disponibles
curl http://localhost:7474/api/curation/cases

# Disparar un caso por API
curl -X POST -H "Content-Type: application/json" \
  -d '{"case_id":"manufacturing_wilsonart"}' \
  http://localhost:7474/api/curation/run-case
```

## Log

El launcher escribe a `~/.zlab_dashboard.log` para debugging.
