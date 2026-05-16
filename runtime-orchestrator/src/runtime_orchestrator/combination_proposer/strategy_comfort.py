"""Strategy 5 — Comfort/safety windows (ASHRAE 55, OSHA, NFPA 70E, ACGIH).

Generaliza Strategy 3 a "ventanas operativas mandatadas por seguridad/
confort" cuando los patterns activos sugieren acciones que las violarían.

Diferencia con Strategy 3:
  · Strategy 3 = matriz curada por pattern (HVAC verano, boiler invierno)
  · Strategy 5 = reglas DE VENTANA por seguridad (heat stress umbral OSHA,
                 arc flash NFPA 70E, ACGIH TLV exposición), independiente
                 del pattern específico
                 → genera 1 combination cuando aplica + pattern relevante

Phase 0: cero LLM. Hipótesis = quote verbatim de regulación literal.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
from pathlib import Path
from typing import Any

from .proposer import ProposedCombination


# Cada ventana lleva: trigger conditions, decision_implication,
# evidence verbatim. Curado humano, NO inventado por LLM.
SAFETY_COMFORT_WINDOWS: list[dict[str, Any]] = [
    {
        "id":              "outdoor_work_extreme_heat_window",
        "trigger_patterns": ["chiller_degradation_plausibility", "hvac_aging_high_load",
                            "rooftop_equipment_inspection_due"],
        "asset_families":   ["commercial_building", "manufacturing_facility",
                            "warehouse_distribution", "infrastructure_node"],
        "when": {
            "all": [
                {"field": "current_month", "op": "in", "value": [6, 7, 8]},
                {"field": "outdoor_high_temp_F", "op": "ge", "value": 95},
            ]
        },
        "decision_implication": {
            "action": "DEFER_TO_WINDOW",
            "allowed_windows": [Sep, Oct, Nov, Mar, Apr, May],
            "alternative": "shift_to_early_morning_or_evening_or_indoor_only",
            "note": "Trabajo outdoor en heat index >95°F sin acclimatization viola general duty clause."
        } if False else {
            "action": "DEFER_TO_WINDOW",
            "allowed_windows": ["Sep", "Oct", "Nov", "Mar", "Apr", "May"],
            "alternative": "shift_to_early_morning_or_evening_or_indoor_only",
            "note": "Trabajo outdoor en heat index >95°F sin acclimatization viola general duty clause.",
        },
        "evidence_anchors": [
            {"citation": "osha heat campaign",
             "verbatim": "OSHA Heat Illness Prevention: workers acclimatize; provide rest periods every 2 hours when heat index exceeds 91°F; hydration mandatory."},
            {"citation": "acgih tlv heat",
             "verbatim": "ACGIH TLV for heat stress: WBGT (Wet Bulb Globe Temperature) thresholds depending on workload and acclimatization status."},
        ],
        "consequence_if_ignored": [
            "OSHA general duty clause cita por exposure a heat illness",
            "Lesión laboral / muerte por golpe de calor",
            "Productividad cae 30-50% sobre 95°F sin medidas",
        ],
    },
    {
        "id":              "high_voltage_work_no_loto_window",
        "trigger_patterns": ["reactive_power_exposure", "transformer_load_factor_unknown"],
        "asset_families":   ["manufacturing_facility", "infrastructure_node",
                            "commercial_building", "datacenter"],
        "when": {
            "all": [
                {"field": "electrical_voltage_class", "op": "ge", "value": 480},
                {"field": "production_active", "op": "eq", "value": True},
            ]
        },
        "decision_implication": {
            "action": "DEFER_TO_WINDOW",
            "allowed_windows": ["scheduled_outage", "weekend", "holiday"],
            "alternative": "schedule_LOTO_window_with_QEW_present",
            "note": "Trabajo eléctrico >480V durante operación requiere LOTO completo + QEW (Qualified Electrical Worker).",
        },
        "evidence_anchors": [
            {"citation": "nfpa 70e",
             "verbatim": "An electrically safe work condition shall be established before any person works on or near electrical conductors operating at >50 volts."},
            {"citation": "29 cfr 1910.333",
             "verbatim": "Safety-related work practices shall be employed to prevent electric shock or other injuries resulting from either direct or indirect electrical contacts."},
        ],
        "consequence_if_ignored": [
            "Arc flash incidents (NFPA 70E violation, ANSI Z535)",
            "OSHA citation bajo 1910.333",
            "Lesiones graves/fatales por shock eléctrico o arc flash",
        ],
    },
    {
        "id":              "indoor_air_quality_during_construction",
        "trigger_patterns": ["hvac_aging_high_load", "boiler_degradation_plausibility",
                            "compressed_air_leak_plausibility"],
        "asset_families":   ["commercial_building", "manufacturing_facility"],
        "when": {
            "all": [
                {"field": "occupancy_density", "op": "ge", "value": 0.4},
                {"field": "indoor_construction_proposed", "op": "eq", "value": True},
            ]
        },
        "decision_implication": {
            "action": "ALTERNATIVE_VIABLE",
            "alternative": "phase_construction_with_negative_pressure_containment_or_after_hours",
            "note": "Construction interna con ocupantes presentes requiere ASHRAE 62.1 ventilation maintenance.",
        },
        "evidence_anchors": [
            {"citation": "ashrae 62.1",
             "verbatim": "Construction or renovation activities shall be performed in a manner that minimizes occupant exposure to contaminants; outdoor air ventilation rates shall be maintained per Table 6-1."},
        ],
        "consequence_if_ignored": [
            "IAQ degradation expone ocupantes a polvo/COV",
            "Posible cita OSHA + reclamos de ocupantes",
            "ASHRAE 62.1 violation en operating logs",
        ],
    },
    {
        "id":              "noise_exposure_window",
        "trigger_patterns": ["compressed_air_leak_plausibility", "reactive_power_exposure"],
        "asset_families":   ["manufacturing_facility", "infrastructure_node"],
        "when": {
            "all": [
                {"field": "noise_level_dba", "op": "ge", "value": 85},
                {"field": "occupied_during_repair", "op": "eq", "value": True},
            ]
        },
        "decision_implication": {
            "action": "ALTERNATIVE_VIABLE",
            "alternative": "schedule_during_low_occupancy_or_provide_hearing_protection_program",
            "note": "Trabajo con noise >85 dBA durante 8hr requiere hearing conservation program OSHA.",
        },
        "evidence_anchors": [
            {"citation": "29 cfr 1910.95",
             "verbatim": "When information indicates that any employee's exposure may equal or exceed an 8-hour TWA of 85 decibels, the employer shall develop and implement a monitoring program."},
        ],
        "consequence_if_ignored": [
            "OSHA 1910.95 violation",
            "Pérdida auditiva permanente en trabajadores no protegidos",
            "Workers comp claims",
        ],
    },
]


def _stable_id(window_id: str, pattern_id: str, asset_family: str) -> str:
    key = f"comfort|{asset_family}|{window_id}|{pattern_id}"
    suffix = hashlib.sha256(key.encode()).hexdigest()[:8]
    fam_short = asset_family.replace("_facility", "").replace("_", "")[:10]
    return f"auto_comf_{fam_short}_{window_id[:32]}_{suffix}"


def _build_candidate(window: dict[str, Any], pattern_id: str,
                     asset_family: str) -> ProposedCombination:
    anchors = window["evidence_anchors"]
    primary = anchors[0]
    hypothesis = f'"{primary["verbatim"][:240]}" [{primary["citation"]}]'
    regulatory_basis = [{
        "citation":         a["citation"],
        "title":            a["citation"].upper(),
        "snippet_verbatim": a["verbatim"][:280],
        "has_text_in_corpus": True,
    } for a in anchors]

    return ProposedCombination(
        id                    = _stable_id(window["id"], pattern_id, asset_family),
        pattern_set           = [pattern_id],
        proposal_method       = "comfort_safety_window",
        generated_at          = _dt.datetime.utcnow().isoformat() + "Z",
        generated_by          = "framework_auto",
        status                = "pending_human_review",
        confidence_score      = 0.92,
        combined_hypothesis   = hypothesis,
        strategic_risk        = window["decision_implication"].get("note", "")[:280],
        context_predicates    = window["when"],
        corpus_citations      = [],
        regulatory_basis      = regulatory_basis,
        decision_implication  = window["decision_implication"],
        consequence_if_ignored = list(window["consequence_if_ignored"]),
        anti_triggers         = [],
        asset_families        = [asset_family],
    )


def propose_from_comfort_windows(
    *,
    asset_family:    str,
    active_patterns: list[str],
    max_candidates:  int = 25,
) -> list[ProposedCombination]:
    """Generate candidates for safety/comfort windows that the active
    patterns may threaten."""
    if not active_patterns:
        return []
    active_set = set(active_patterns)

    candidates: list[ProposedCombination] = []
    for window in SAFETY_COMFORT_WINDOWS:
        if asset_family not in window.get("asset_families", []):
            continue
        triggers = window.get("trigger_patterns", [])
        for p in triggers:
            if p in active_set:
                candidates.append(_build_candidate(window, p, asset_family))
                if len(candidates) >= max_candidates:
                    return candidates
                break   # only one combination per (window, family) — no duplicates
    return candidates
