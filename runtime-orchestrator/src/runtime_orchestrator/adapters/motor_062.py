"""Adapter for motor_062 — Scenario Justification Validator (Layer F).

Implements Validator B of the new prompt RECOVERY_2026-05-10
("cerebro de congruencia operacional"):

  > B. SCENARIO JUSTIFICATION VALIDATOR
  > Cada escenario activo debe llevar:
  >   - trigger (qué dato/observación lo activó)
  >   - source (fuente industrial autoritativa)
  >   - process_clue (mecanismo físico/operacional)
  >   - industrial_reason (por qué importa industrialmente)
  >   - asset_family_reason (por qué aplica a esta familia)
  > Si falta alguno → bloquear render (o warn en modo soft).

Scenarios are produced by motor_014._build_scenario_space and surfaced
in motor_047 as `scenario_register`. Today they expose plausibility +
financial_meaning + evidence_needed, but not the 5 justification fields
above. This validator audits them and emits warnings; the render gate
in motor_017 honors the resulting `scenario_justification_failed` flag.

Default mode is `warn` (no block) so existing PDFs keep rendering while
upstream generators incrementally add the 5 fields. Flip
`__pipeline__.scenario_justification_mode = "block"` when ready to enforce.
"""
from __future__ import annotations

from typing import Any

from ..source_catalog import all_sources, is_known_source
from .base import BaseMotorAdapter


_REQUIRED_FIELDS: tuple[str, ...] = (
    "trigger",
    "source",
    "process_clue",
    "industrial_reason",
    "asset_family_reason",
)

# A scenario is considered "active" (and therefore subject to justification
# audit) when its plausibility_status falls in this set. Falsified / reduced
# scenarios are excluded — they cannot mislead the reader.
_ACTIVE_PLAUSIBILITY_PREFIXES: tuple[str, ...] = (
    "plausible",
    "currently dominant",
    "not ruled out",
    "possible",
)

# Critical threshold: when at least this many active scenarios have no
# justification fields at all, the report is flagged as
# `scenario_justification_failed = True` and the render gate may block.
_CRITICAL_MISSING_THRESHOLD = 3


def _text(value: Any) -> str:
    return str(value or "").strip()


def _is_active(scenario: dict) -> bool:
    status = _text(scenario.get("plausibility_status")).lower()
    if not status:
        return False
    return any(status.startswith(prefix) for prefix in _ACTIVE_PLAUSIBILITY_PREFIXES)


def _missing_fields(scenario: dict) -> list[str]:
    return [field for field in _REQUIRED_FIELDS if not _text(scenario.get(field))]


def _resolve_asset_family(inputs: dict[str, Any]) -> str:
    m007 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
    contract = m007.get("target_definition_contract") or {}
    if isinstance(contract, dict):
        family = _text(contract.get("asset_family") or contract.get("target_family"))
        if family:
            return family
    return ""


def _collect_scenarios(inputs: dict[str, Any]) -> list[dict]:
    """Pull scenarios from motor_014.scenario_space, falling back to motor_047.

    motor_014 is the authoritative producer; motor_047 only re-emits the
    same list. We accept either path so the validator works whether wired
    directly to m14 or downstream of the composer.
    """
    m014 = inputs.get("motor_014", {}) if isinstance(inputs.get("motor_014", {}), dict) else {}
    rows = list(m014.get("scenario_space", []) or [])
    if rows:
        return [r for r in rows if isinstance(r, dict)]
    m047 = inputs.get("motor_047", {}) if isinstance(inputs.get("motor_047", {}), dict) else {}
    thesis = m047.get("executive_thesis", {}) if isinstance(m047.get("executive_thesis", {}), dict) else {}
    rows = list(thesis.get("scenario_register", []) or [])
    return [r for r in rows if isinstance(r, dict)]


def _build_warnings(
    scenarios: list[dict],
    asset_family: str,
) -> list[dict]:
    warnings: list[dict] = []
    for idx, scenario in enumerate(scenarios):
        if not _is_active(scenario):
            continue
        scenario_label = _text(scenario.get("scenario")) or f"scenario_{idx + 1:02d}"
        # Rule SJ1: missing justification fields
        missing = _missing_fields(scenario)
        if missing:
            severity = "critical" if len(missing) == len(_REQUIRED_FIELDS) else "warning"
            warnings.append(
                {
                    "rule_id": "SJ1_scenario_missing_justification",
                    "severity": severity,
                    "scenario": scenario_label,
                    "asset_family": asset_family,
                    "missing_fields": missing,
                    "description": (
                        f"Active scenario '{scenario_label[:80]}' is missing "
                        f"required justification fields: {missing}. "
                        "Per RECOVERY_2026-05-10 §11.B every active scenario "
                        "must declare trigger, source, process_clue, "
                        "industrial_reason, and asset_family_reason."
                    ),
                }
            )
        # Rule SJ2: source field must reference an entry in the industrial
        # source catalog (139 sources, Gap C). Without this, a scenario can
        # claim "source: my uncle" and pass SJ1. We accept the source field
        # when ANY catalog source_id or canonical name appears as a substring.
        source_text = _text(scenario.get("source"))
        if source_text and not is_known_source(source_text):
            warnings.append(
                {
                    "rule_id": "SJ2_scenario_source_unknown",
                    "severity": "critical",
                    "scenario": scenario_label,
                    "asset_family": asset_family,
                    "source_value": source_text[:160],
                    "description": (
                        f"Scenario '{scenario_label[:80]}' cites source "
                        f"'{source_text[:80]}' which does not match any "
                        "entry in the industrial source catalog (139 "
                        "tier-1/tier-2/tier-3 sources). Cite a catalog "
                        "source_id (e.g. iiar_bulletin_109, ashrae_90_1, "
                        "doe_iac_database) or add the source to "
                        "industrial_source_catalog.json."
                    ),
                }
            )
    return warnings


class Motor062Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_062"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_007", "motor_014", "motor_047"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        asset_family = _resolve_asset_family(inputs)
        scenarios = _collect_scenarios(inputs)
        active_count = sum(1 for s in scenarios if _is_active(s))

        warnings = _build_warnings(scenarios, asset_family)
        critical_count = sum(1 for w in warnings if w.get("severity") == "critical")

        # Pipeline-level mode toggle. After V2-LIVE Item 1 + Item 3,
        # motor_014 emits the 5 justification fields for every scenario
        # and motor_062 validates the source against the 139-source
        # catalog, so `block` is now safe as the default. Cases that
        # have not yet been updated can opt back into warn mode via
        # __pipeline__.scenario_justification_mode='warn'.
        pipeline_inputs = inputs.get("__pipeline__", {}) if isinstance(inputs.get("__pipeline__", {}), dict) else {}
        mode = _text(pipeline_inputs.get("scenario_justification_mode") or "block").lower()
        enforce_block = mode == "block"

        # Failed = enough critical scenarios to justify blocking the render.
        scenario_justification_failed = (
            enforce_block and critical_count >= _CRITICAL_MISSING_THRESHOLD
        )

        return {
            "scenario_justification_warnings": warnings,
            "warning_count": len(warnings),
            "critical_count": critical_count,
            "active_scenario_count": active_count,
            "total_scenario_count": len(scenarios),
            "asset_family_evaluated": asset_family,
            "mode": mode,
            "scenario_justification_failed": scenario_justification_failed,
            "required_fields": list(_REQUIRED_FIELDS),
            "rules_evaluated": [
                "SJ1_scenario_missing_justification",
                "SJ2_scenario_source_unknown",
            ],
            "catalog_size": len(all_sources()),
        }
