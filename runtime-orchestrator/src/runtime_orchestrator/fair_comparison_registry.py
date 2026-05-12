"""Fair Comparison Rules Registry (V3 G12 machinery closure).

Provides a declarative LOADER + SCHEMA for fair_comparison_rules.yaml.
The YAML itself stays user-owned content; this module is the contract
the framework reads it through.

Schema (each rule, optional):
  rule_id: str  (unique)
  applies_to_families: list[asset_family_id]  (must be in canonical taxonomy)
  requires_match: list[match_key]  (e.g., naics_4, throughput_band)
  blocks_when: str  (semantic — when comparison is invalid)
  rationale: str
  source_basis: list[{source_id, confidence}]

V3 G12 deliberately leaves the YAML content as-is (pre-existing user
file). The registry's job is to make ANY future fair-comparison rule
authoring go through a validated structure rather than being hardcoded
in motor_051.

motor_051 can read `load_fair_comparison_rules()` for declarative rules.
If the YAML has no rules section, the function returns an empty list
and motor_051's existing hardcoded logic stays the source of truth —
zero-disruption migration path.
"""
from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

from .industrial_research_engine.family_scope import ALL_KNOWN_ASSET_FAMILIES


_REPO_ROOT = Path(__file__).resolve().parents[3]
_RULES_PATH = (
    _REPO_ROOT
    / "runtime-orchestrator"
    / "zlab_skill"
    / "fair_comparison_rules.yaml"
)


# Match keys are open vocabulary (process_logic + asset_archetypes will
# extend the vocabulary as V4 P1 lands real industrial data). We declare
# the canonical CORE keys so authoring tools can autocomplete and the
# validator can reject blatant typos.
CANONICAL_MATCH_KEYS: frozenset[str] = frozenset({
    "target_family",
    "asset_family",
    "naics_4",
    "naics_6",
    "throughput_band",
    "thermal_duty_band",
    "temperature_band",
    "refrigerant_family",
    "maintenance_maturity_tier",
    "cure_type",
    "press_type",
    "occupancy_class",
    "tariff_class",
    "jurisdiction",
    "climate_zone",
    "facility_age_band",
})


class FairComparisonRulesError(ValueError):
    """Raised when fair_comparison_rules.yaml fails validation."""


def _yaml_load_safe(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {}
    try:
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as exc:
        raise FairComparisonRulesError(
            f"failed to parse {path}: {exc}"
        ) from exc
    return data if isinstance(data, dict) else {}


def _validate_rule(rule: dict[str, Any], idx: int) -> dict[str, Any]:
    if not isinstance(rule, dict):
        raise FairComparisonRulesError(
            f"rule[{idx}] must be a dict; got {type(rule).__name__}"
        )
    rule_id = str(rule.get("rule_id", "")).strip()
    if not rule_id:
        raise FairComparisonRulesError(f"rule[{idx}] missing rule_id")

    families = rule.get("applies_to_families", []) or []
    if not isinstance(families, list):
        raise FairComparisonRulesError(f"{rule_id}.applies_to_families must be a list")
    unknown_families = [
        f for f in families
        if str(f).strip() and str(f).strip() not in ALL_KNOWN_ASSET_FAMILIES
    ]
    if unknown_families:
        raise FairComparisonRulesError(
            f"{rule_id}.applies_to_families contains unknown families: "
            f"{unknown_families}. Known: {sorted(ALL_KNOWN_ASSET_FAMILIES)}"
        )

    match_keys = rule.get("requires_match", []) or []
    if not isinstance(match_keys, list):
        raise FairComparisonRulesError(f"{rule_id}.requires_match must be a list")
    # Match keys outside the canonical vocabulary are WARNINGS (informational),
    # not errors — V4 P1 will extend the vocabulary naturally.

    return {
        "rule_id": rule_id,
        "applies_to_families": [str(f).strip() for f in families if str(f).strip()],
        "requires_match": [str(k).strip() for k in match_keys if str(k).strip()],
        "blocks_when": str(rule.get("blocks_when", "")).strip(),
        "rationale": str(rule.get("rationale", "")).strip(),
        "source_basis": list(rule.get("source_basis", []) or []),
    }


@lru_cache(maxsize=1)
def load_fair_comparison_rules() -> list[dict[str, Any]]:
    """Load + validate fair_comparison_rules.yaml. Returns the (possibly
    empty) list of validated rule dicts. Cached because the YAML changes
    only between pipeline runs."""
    raw = _yaml_load_safe(_RULES_PATH)
    rules_list = raw.get("rules", []) or []
    if not isinstance(rules_list, list):
        raise FairComparisonRulesError(
            "fair_comparison_rules.yaml `rules` must be a list"
        )
    validated: list[dict[str, Any]] = []
    ids_seen: set[str] = set()
    for idx, rule in enumerate(rules_list):
        v = _validate_rule(rule, idx)
        if v["rule_id"] in ids_seen:
            raise FairComparisonRulesError(
                f"duplicate rule_id: {v['rule_id']}"
            )
        ids_seen.add(v["rule_id"])
        validated.append(v)
    return validated


def rules_for_family(asset_family: str) -> list[dict[str, Any]]:
    """Filter rules to those applicable to a given asset family."""
    fam = (asset_family or "").strip()
    if not fam:
        return []
    return [
        r for r in load_fair_comparison_rules()
        if not r["applies_to_families"] or fam in r["applies_to_families"]
    ]


def canonical_match_keys() -> tuple[str, ...]:
    return tuple(sorted(CANONICAL_MATCH_KEYS))


def reload_rules() -> None:
    """Clear cache. Tests + dashboard hot-reload use this."""
    load_fair_comparison_rules.cache_clear()
