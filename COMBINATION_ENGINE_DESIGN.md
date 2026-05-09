# Structural Combination Engine — Design

> Reconstruye el corazón del framework: las **combinaciones estructurales** como
> objetos computables, versionadas, aprobables, auditables. La IA puede sugerir
> y redactar; **no aprueba combinaciones**, **no crea verdad**.
>
> Versión: 1.0.0 · 2026-05-09

---

## 1. Por qué combinations (y no solo patterns)

El framework ya tiene patterns asset-specific (Pattern Library JSON v1.0.0) y
los 4 estados epistemológicos. Pero **patterns aislados no producen
inteligencia**. La inteligencia emerge cuando 2-N patterns combinan:

> "Charging schedule" + "demand tariff" + "operating schedule"
> → Hipótesis: peak demand domina la economía, no el consumo anual.
> → TAD: VALIDATE DEMAND EXPOSURE; DO NOT UNDERWRITE EFFICIENCY YET.
> → Gold nugget: "If charging drives peak demand, the problem is tariff
>   orchestration disguised as energy inefficiency."

Esa **combinación** debe existir como objeto computable, no improvisada
por un LLM. Tiene:
- inputs explícitos (qué patterns activan la combinación);
- anti-patterns (con qué patterns NO debe coexistir);
- hipótesis combinada;
- riesgo estratégico;
- evidence pack específico;
- TAD actions;
- gold nugget;
- allowed/prohibited language.

## 2. Schema canónico

Cada combination es un JSON con esta forma:

```json
{
  "combination_id": "warehouse_charging_tariff_logic",
  "version": "1.0.0",
  "approved_at": "2026-05-09",
  "approved_by": "dashboard",
  "asset_families": ["warehouse_distribution", "cold_chain_facility"],
  "required_patterns": [
    "tariff_orchestration",
    "logistics_throughput"
  ],
  "anti_patterns": [
    "tenant_boundary",
    "process_heat"
  ],
  "combined_hypothesis": "Peak demand may dominate economics more than annual consumption.",
  "strategic_risk": "Energy retrofit may target the wrong variable.",
  "financial_translation": "Demand-charge exposure can dwarf consumption-cost reduction by 2-5x in short-cycle logistics nodes.",
  "evidence_needed": [
    "utility_bill_intervals",
    "tariff_schedule",
    "charging_schedule_evidence",
    "MHE_inventory"
  ],
  "falsification_conditions": [
    "Interval data shows demand peaks decoupled from charging windows.",
    "Tariff is energy-only (no demand component)."
  ],
  "TAD_actions": [
    {
      "action": "VALIDATE DEMAND EXPOSURE",
      "status": "ACT NOW",
      "evidence_path": ["utility_bill_intervals", "tariff_schedule"],
      "risk_avoided": "Funding efficiency CAPEX while demand charges drive cost"
    },
    {
      "action": "DO NOT UNDERWRITE EFFICIENCY YET",
      "status": "DEFER",
      "evidence_path": ["demand_curve_evidence"],
      "risk_avoided": "ROI overstatement"
    }
  ],
  "allowed_language": [
    "may dominate",
    "structurally suggests",
    "is consistent with"
  ],
  "prohibited_language": [
    "ROI",
    "savings",
    "payback",
    "bankability",
    "guaranteed"
  ],
  "gold_nugget": "If charging drives peak demand, the problem is tariff orchestration disguised as energy inefficiency.",
  "comparison_impact": "Generic warehouse EUI peer comparison becomes structurally invalid until demand profile is bounded.",
  "confidence_ceiling": "ARCHETYPAL_PRIOR until interval data confirms.",
  "report_sections": [
    "Cap. 5 Dominant Variables",
    "Cap. 7 Financial Exposure Under Uncertainty",
    "Cap. 11 TAD",
    "Cap. 12 Claim Permissions"
  ],
  "chart_support": [
    "demand_curve_overlay",
    "charging_window_overlay"
  ],
  "validator_requirements": [
    "tariff_pack_evidence_at_minimum_archetypal",
    "no_tenant_boundary_pattern_active"
  ]
}
```

## 3. Catálogo seed (v1.0.0)

10 combinations aprobadas para arrancar:

| ID | asset_families | concepto |
|---|---|---|
| `warehouse_charging_tariff_logic` | warehouse_distribution, cold_chain_facility | demand-charge dominance |
| `cold_chain_infiltration_logic` | cold_chain_facility | thermal exchange via docks/doors |
| `owner_operator_value_leakage` | commercial_building, warehouse_distribution | control-boundary mismatch |
| `manufacturing_compressed_air_maturity` | manufacturing_facility | leak rate × maintenance reality |
| `process_heat_unbounded_duty` | manufacturing_facility | thermal duty unbounded by process schedule |
| `building_after_hours_phantom_load` | commercial_building | BMS schedule decoupled from occupancy |
| `datacenter_pue_composition_unclear` | datacenter | IT load vs facility-load split unmeasured |
| `logistics_continuity_dispatch_dominance` | logistics_terminal, warehouse_distribution | reefer continuity drives base load |
| `wrong_denominator_area_normalized` | warehouse_distribution, manufacturing_facility, commercial_building | area-based EUI structurally misleading |
| `maintenance_reality_dominates_operations` | manufacturing_facility, cold_chain_facility | downtime/PM gap dominates economics |

## 4. Engine architecture

```
┌──────────────────────────────────────────────────────┐
│ combination_engine.py                                │
│                                                      │
│  load_combination_catalog() → list[Combination]      │
│  activate_combinations(asset_family, active_patterns,│
│                        anti_patterns) → list[id]     │
│  get_combination(id) → Combination | None            │
│  validate_combination(c, ctx) → list[violation]      │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ asset_family_engine.py                               │
│                                                      │
│  detect_asset_family(target_definition) → family    │
│  family_isolation_rules(family) → AntiPatternSet    │
└────────────────┬─────────────────────────────────────┘
                 │
                 ▼
┌──────────────────────────────────────────────────────┐
│ motor_061  Asset Family Isolation Validator         │
│ motor_062  Combination Validator                    │
│ motor_063  Chart Validity Engine                    │
└──────────────────────────────────────────────────────┘
```

## 5. Activación de combinations

```python
def activate_combinations(
    asset_family: str,
    active_patterns: set[str],
    anti_patterns_present: set[str],
) -> list[Combination]:
    """Una combinación se activa SI y SOLO SI:
       1. asset_family ∈ combination.asset_families
       2. todos los required_patterns están en active_patterns
       3. ninguno de los anti_patterns está en anti_patterns_present
    """
```

## 6. Reglas absolutas

- **NO la IA aprueba** una combinación. El dashboard humano lo hace.
- **Para efectos de runtime**: todas las combinations en el catálogo
  JSON están **asumidas como aprobadas** (`approved_at` field).
- **NO se generan combinaciones en runtime**. Solo se activan o no.
- Si activación falla por anti-pattern presente → se **bloquea el reporte**
  (motor_061 / motor_062), no se silencia.

## 7. Asset Family Isolation rules

Cada asset_family tiene un set de patterns **incompatibles** que jamás deben
estar activos simultáneamente. Si el sistema detecta uno de esos en el run,
motor_061 bloquea el reporte:

```python
ISOLATION_RULES = {
    "warehouse_distribution": {
        "incompatible": [
            "tenant_boundary",      # office concept
            "process_heat",         # manufacturing concept
            "compressed_air",       # manufacturing concept
            "pue_composition",      # datacenter concept
        ],
    },
    "cold_chain_facility": {
        "incompatible": [
            "process_heat",
            "compressed_air",
            "tenant_boundary",
        ],
    },
    "manufacturing_facility": {
        "incompatible": [
            "logistics_throughput",  # warehouse concept
            "tariff_orchestration",  # warehouse concept
            "tenant_boundary",
            "pue_composition",
        ],
    },
    "commercial_building": {
        "incompatible": [
            "process_heat",
            "compressed_air",
            "logistics_throughput",
            "pue_composition",
        ],
    },
    "datacenter": {
        "incompatible": [
            "process_heat",
            "tenant_boundary",
            "logistics_throughput",
        ],
    },
}
```

## 8. Plan de implementación (este sprint)

| # | Commit | Contenido |
|---|---|---|
| 1 | `docs(combination)` | este documento |
| 2 | `feat(combinations)` | 10 JSON files en `governanza/.../combinations/` |
| 3 | `feat(combination_engine)` | `combination_engine.py` + tests |
| 4 | `feat(asset_family_engine)` | `asset_family_engine.py` + isolation rules |
| 5 | `recovery(motor_061)` | Asset Family Isolation Validator |
| 6 | `recovery(motor_062)` | Combination Validator |
| 7 | `recovery(motor_063)` | Chart Validity Engine |
| 8 | `feat(wiring)` | motor_054 emits activated combinations; composer renders them |

Suite target: ≥920 passed.

## 9. Reglas inviolables del Combination Engine

- 🔒 Las combinaciones son objetos computables, **no texto generado**.
- 🔒 La IA **NO** crea, modifica, ni aprueba combinaciones.
- 🔒 Las combinations son versionadas (SemVer); cambio de major requiere
  regresión sobre los últimos N reports.
- 🔒 Los anti-patterns son **bloqueantes**, no advertencias.
- 🔒 El composer **NO** lee combinations directamente — las lee del
  output ya gobernado por motor_062.
- 🔒 Si el catálogo está vacío (file faltante) el sistema NO puede
  emitir reports — emite error explícito.
