"""V6 P5 — Pattern Asset-Family Isolation Engine.

V6 Stability prompt item 3: "AISLAMIENTO POR ASSET FAMILY".

Today, the 30 pattern_specs declare `asset_types` (where they apply)
but there is no canonical, read-only contract that says:

  "pattern X is ALLOWED for {family A, family B} and FORBIDDEN
   for {family C, family D}."

motor_061 detects cross-family contamination *after* it happens.
This module is the gate that lets us assert *before* activation
whether a pattern is even permitted on a target family.

Design choice (surgical, no JSON migration):
  - allowed_families is derived from pattern_spec["asset_types"]
    intersected with `ALL_KNOWN_ASSET_FAMILIES`.
  - forbidden_families = `ALL_KNOWN_ASSET_FAMILIES` − allowed_families.
  - The contract is computed on the fly from each spec — no schema
    change, no migration, no risk of stale duplication.

The contract is consumed by:
  - motor_061 (asset_family integrity) — already detects contamination
  - V6 P11 stability tests — feed forbidden families and assert block
  - QA score (qa_score.py) — cross_family_violations counter

Phase 0 anchor: a pattern that activates on a forbidden family is a
contamination event. It does NOT degrade — it BLOCKS.
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Mapping

from .industrial_research_engine.family_scope import (
    ALL_KNOWN_ASSET_FAMILIES,
)
from .zlab_skill.loader import load_pattern_specs

# Sentinel asset_type value declaring "applies to every operational
# asset family" (used by digital_twin_prematurity, sensor_prematurity).
_UNIVERSAL_SENTINEL = "all_operational_assets"


@dataclass(frozen=True)
class IsolationContract:
    pattern_id: str
    allowed_families: frozenset[str]
    forbidden_families: frozenset[str]
    declared_asset_types: tuple[str, ...]

    def allows(self, family: str) -> bool:
        return (family or "").strip() in self.allowed_families

    def forbids(self, family: str) -> bool:
        return (family or "").strip() in self.forbidden_families


class PatternIsolationViolation(Exception):
    """Raised when a pattern attempts to activate on a forbidden family."""


def _coerce_spec(pattern: str | Mapping[str, Any]) -> Mapping[str, Any]:
    if isinstance(pattern, Mapping):
        return pattern
    spec = _registry().get(pattern)
    if spec is None:
        raise KeyError(f"pattern_id not in registry: {pattern}")
    return spec


_REGISTRY_CACHE: dict[str, Mapping[str, Any]] | None = None


def _registry() -> dict[str, Mapping[str, Any]]:
    global _REGISTRY_CACHE
    if _REGISTRY_CACHE is None:
        _REGISTRY_CACHE = {row["id"]: row for row in load_pattern_specs()}
    return _REGISTRY_CACHE


def reset_registry_cache() -> None:
    """Test hook — invalidate cached pattern registry."""
    global _REGISTRY_CACHE
    _REGISTRY_CACHE = None


def pattern_isolation_contract(
    pattern: str | Mapping[str, Any],
) -> IsolationContract:
    """Compute the isolation contract for a pattern.

    The pattern spec's `asset_types` field is the canonical declaration.
    Allowed = asset_types ∩ ALL_KNOWN_ASSET_FAMILIES.
    Forbidden = ALL_KNOWN_ASSET_FAMILIES − allowed.
    """
    spec = _coerce_spec(pattern)
    declared = tuple(
        str(f).strip() for f in (spec.get("asset_types") or []) if str(f).strip()
    )
    # Sentinel for universally-applicable patterns (e.g. digital_twin_prematurity,
    # sensor_prematurity). These activate on ANY operational asset family.
    if _UNIVERSAL_SENTINEL in declared:
        allowed = frozenset(ALL_KNOWN_ASSET_FAMILIES)
    else:
        allowed = frozenset(declared) & ALL_KNOWN_ASSET_FAMILIES
    forbidden = ALL_KNOWN_ASSET_FAMILIES - allowed
    pid = str(spec.get("id") or pattern if isinstance(pattern, str) else spec.get("id", ""))
    return IsolationContract(
        pattern_id=pid,
        allowed_families=allowed,
        forbidden_families=forbidden,
        declared_asset_types=declared,
    )


def is_activation_allowed(
    pattern: str | Mapping[str, Any],
    target_family: str,
) -> bool:
    """True iff pattern may legitimately activate on target_family."""
    contract = pattern_isolation_contract(pattern)
    return contract.allows(target_family)


def validate_activation(
    pattern: str | Mapping[str, Any],
    target_family: str,
) -> None:
    """Raise PatternIsolationViolation if activation is forbidden."""
    contract = pattern_isolation_contract(pattern)
    if not contract.allows(target_family):
        raise PatternIsolationViolation(
            f"pattern '{contract.pattern_id}' is not declared for asset_family "
            f"'{target_family}' (allowed: {sorted(contract.allowed_families)})"
        )


def audit_isolation_violations(
    activations: list[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Audit a list of pattern activations.

    Args:
      activations: list of {"pattern_id": str, "asset_family": str, ...} rows
        (or {"pattern": ..., "family": ...}; both shapes accepted).

    Returns:
      List of violation rows (empty if all activations are isolated cleanly).
      Each row: {pattern_id, target_family, allowed_families, reason}.
    """
    violations: list[dict[str, Any]] = []
    for row in activations or []:
        if not isinstance(row, Mapping):
            continue
        pid = row.get("pattern_id") or row.get("pattern")
        fam = row.get("asset_family") or row.get("family")
        if not pid or not fam:
            continue
        try:
            contract = pattern_isolation_contract(pid)
        except KeyError:
            violations.append({
                "pattern_id": str(pid),
                "target_family": str(fam),
                "allowed_families": [],
                "reason": "unknown_pattern_id",
            })
            continue
        if not contract.allows(str(fam)):
            violations.append({
                "pattern_id": contract.pattern_id,
                "target_family": str(fam),
                "allowed_families": sorted(contract.allowed_families),
                "reason": "forbidden_family",
            })
    return violations


def list_registered_patterns() -> list[str]:
    """Return sorted ids of all patterns loaded from the registry."""
    return sorted(_registry().keys())
