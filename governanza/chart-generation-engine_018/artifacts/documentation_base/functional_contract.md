# Functional Contract — Chart Generation Engine

Motor ID: motor_018

## inputs

- `__pipeline__.case_title`
  Tipo: `str`
  Productor: pipeline runtime
  Uso: estampar contexto de caso en los chart assets.
- `motor_007.report_identity_state`
  Tipo: `str`
  Productor: `motor_007`
  Uso: distinguir blocked, exploratory y structural copy regimes.
- `motor_047.report_mode`
  Tipo: `str`
  Productor: `motor_047`
  Uso: reforzar el modo visible de tesis para chart curation.
- `motor_012.facility_prior`
  Tipo: `dict`
  Productor: `motor_012`
  Uso: target definition, priors físicos y technical ceiling base.
- `motor_014`
  Tipo: `dict`
  Productor: `motor_014`
  Uso: decision fronts, scenario space, evidence unlocks y readiness context para charts legacy y estructurales.
- `motor_028`
  Tipo: `dict`
  Productor: `motor_028`
  Uso: enriched discovery, geocoder, benchmark routing y extended sources.
- `motor_049`
  Tipo: `dict`
  Productor: `motor_049`
  Uso: local truth confidence, tariff exposure, utility breakdown, gap taxonomy, next-best-search y stop conditions.
- `motor_051`
  Tipo: `dict`
  Productor: `motor_051`
  Uso: normalization requirements, invalid comparison risks, cross-layer congruence y peer requirements.
- `motor_052`
  Tipo: `dict`
  Productor: `motor_052`
  Uso: measurement strategy y hardware minimality.
- `motor_053`
  Tipo: `dict`
  Productor: `motor_053`
  Uso: finance-to-physics dependency y cost-driver dependency.

## outputs

- `chart_assets`
  Tipo: `list[dict]`
  Consumidores: package assembly, writing, render validation
  Contenido: chart id, taxonomy metadata, bilingual title/description, governance markers, section hint, image payload y stamped case context.
- `total_charts`
  Tipo: `int`
  Consumidores: observabilidad
- `chart_errors`
  Tipo: `list[dict]`
  Consumidores: observabilidad y debugging
- `case_namespace_register`
  Tipo: `dict`
  Consumidores: case isolation y stamping

## limits

- the motor may only visualize governed upstream objects;
- it may not generate charts that imply stronger certainty than the supporting evidence state;
- it may not emit unstamped chart assets detached from the current case;
- it may not collapse blocked and structural curation modes into one generic copy surface.

## validations

- chart assets must preserve taxonomy fields, case context and case match state;
- structural, exploratory and blocked modes must produce distinct copy where the runtime expects it;
- chart images must be present for emitted chart assets;
- chart taxonomy defaults must remain stable for known and unknown chart ids.
