"""Industrial research taxonomy (V4 P0 item 8).

Per the user spec: declare the topic taxonomy used by research_routing
without authoring NEW content. Topics here are STRUCTURAL labels (not
hypotheses, not patterns) — they tell the framework what KIND of
investigation an asset family triggers.

The structural taxonomy is intentionally minimal. Each topic maps to
keywords the framework uses to filter sources; the actual extraction
that turns sources into patterns is V4 Phase 1 work (not here).
"""
from __future__ import annotations


# Topic → keyword(s). Keywords are domain-of-investigation labels, not
# claim content. The taxonomy is OPEN at the lookup level (callers can
# pass a free-text topic) — this map is the canonical structural set.
INDUSTRIAL_TAXONOMY: dict[str, dict[str, list[str]]] = {
    "thermal_process": {
        "keywords": ["thermal duty", "process heat", "curing", "thermal oil"],
        "machines": ["furnace", "press", "oven", "thermal_oil_loop"],
        "systems": ["combustion", "steam", "heat_recovery"],
    },
    "refrigeration": {
        "keywords": ["refrigeration", "defrost", "compressor staging", "refrigerant"],
        "machines": ["compressor", "evaporator", "condenser"],
        "systems": ["ammonia_loop", "co2_cascade", "hfo_blend"],
    },
    "compressed_air": {
        "keywords": ["compressed air", "leak", "pressure band", "demand control"],
        "machines": ["air_compressor", "dryer", "receiver"],
        "systems": ["distribution_network", "regulators"],
    },
    "steam": {
        "keywords": ["steam trap", "boiler", "feedwater", "condensate return"],
        "machines": ["boiler", "deaerator"],
        "systems": ["distribution_header", "condensate_loop"],
    },
    "control_boundary": {
        "keywords": ["bms", "scada", "tenant metering", "lease responsibility"],
        "machines": ["bms_controller", "submeter"],
        "systems": ["sequence_of_operations", "control_loops"],
    },
    "power_quality": {
        "keywords": ["harmonics", "power factor", "demand charge", "voltage quality"],
        "machines": ["vfd", "capacitor_bank", "transformer"],
        "systems": ["service_entrance", "grounding"],
    },
    "tariffs": {
        "keywords": ["demand charge", "time of use", "coincident peak", "ratchet"],
        "machines": [],
        "systems": ["utility_rate_schedule", "ercot_market"],
    },
    "logistics": {
        "keywords": ["dock cycles", "mhe charging", "throughput", "yard management"],
        "machines": ["forklift", "dock_door", "conveyor"],
        "systems": ["wms", "dock_scheduling"],
    },
    "maintenance": {
        "keywords": ["pm history", "downtime", "scrap", "reliability"],
        "machines": [],
        "systems": ["cmms", "tpm_program"],
    },
    "emissions": {
        "keywords": ["voc", "ghgrp", "ll97 carbon", "rmp"],
        "machines": ["abatement", "thermal_oxidizer", "rto"],
        "systems": ["air_permit", "stack_monitoring"],
    },
    "thermal_boundary": {
        "keywords": ["envelope conductance", "vapor barrier", "insulation r value"],
        "machines": [],
        "systems": ["wall_system", "roof_assembly"],
    },
}


# Family → ordered topics to investigate. This is structural routing,
# NOT content (no hypothesis, no claim). V4 Phase 1's research engine
# walks topics in this order when discovering sources for a case.
#
# Per user direction, we do NOT pre-populate per-family priorities here
# (that would be content — the framework should derive the order from
# observed activations + source authority). Callers default to the keys
# of INDUSTRIAL_TAXONOMY when no priority is registered.
_FAMILY_TOPIC_PRIORITY: dict[str, list[str]] = {}


def topics_for_family(asset_family: str) -> list[str]:
    """Return ordered topics for an asset family. Empty list when no
    priority is registered — caller should use INDUSTRIAL_TAXONOMY.keys()
    as the fallback."""
    return list(_FAMILY_TOPIC_PRIORITY.get(asset_family, []))


def family_for_topic(topic: str) -> list[str]:
    """Reverse lookup — return families that include `topic` in priority."""
    out: list[str] = []
    for fam, topics in _FAMILY_TOPIC_PRIORITY.items():
        if topic in topics:
            out.append(fam)
    return sorted(out)


def topic_is_known(topic: str) -> bool:
    return topic in INDUSTRIAL_TAXONOMY


def keywords_for_topic(topic: str) -> list[str]:
    info = INDUSTRIAL_TAXONOMY.get(topic, {})
    return list(info.get("keywords", []) or [])
