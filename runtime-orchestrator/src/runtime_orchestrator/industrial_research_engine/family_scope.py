"""Asset family scope enforcement (V4 P0 item 5).

Every knowledge object declares `asset_families` (it applies to) and
`anti_families` (it MUST NOT apply to). The validator enforces:
  - asset_families and anti_families are disjoint
  - every listed family is a known asset family
  - at least one asset_family is declared

motor_061 already enforces cross-family contamination at runtime; this
module is the proposal-time gate so nothing reaches knowledge_pending
that violates the family taxonomy.
"""
from __future__ import annotations

# Canonical asset family taxonomy. Aligns with motor_061 +
# asset_family_hybrids.json. New families enter ONLY by adding here and
# to motor_061 in lockstep — no orphan families.
ALL_KNOWN_ASSET_FAMILIES: frozenset[str] = frozenset({
    # core production families (V2 + V3)
    "cold_chain_facility",
    "cold_chain_distribution",
    "manufacturing_facility",
    "warehouse_distribution",
    "commercial_building",
    "datacenter",
    "logistics_terminal",
    "infrastructure_node",
    # process-specialized (V4 will expand these as research engine extracts)
    "food_processing",
    "thermal_process_facility",
    "pharma_facility",
    "fulfillment_center",
    "cross_dock",
    "mixed_process_facility",
    # retail-cold
    "supermarket",
    "food_retail",
})


def is_known_family(family: str) -> bool:
    return (family or "").strip() in ALL_KNOWN_ASSET_FAMILIES


def families_conflict(
    asset_families: list[str] | tuple[str, ...],
    anti_families: list[str] | tuple[str, ...],
) -> list[str]:
    """Return the intersection (conflicts). Empty list = no conflict."""
    a = {(f or "").strip() for f in (asset_families or [])}
    b = {(f or "").strip() for f in (anti_families or [])}
    return sorted(a & b)


def enforce_family_scope(
    asset_families: list[str] | tuple[str, ...],
    anti_families: list[str] | tuple[str, ...] | None = None,
) -> tuple[list[str], list[str]]:
    """Validate asset_families + anti_families.

    Returns (normalized_asset_families, normalized_anti_families).
    Raises ValueError on:
      - empty asset_families
      - unknown family in either list
      - asset_families ∩ anti_families non-empty
    """
    af = [str(f).strip() for f in (asset_families or []) if str(f).strip()]
    nf = [str(f).strip() for f in (anti_families or []) if str(f).strip()]
    if not af:
        raise ValueError("at least one asset_family is required")

    unknown_af = sorted(set(af) - ALL_KNOWN_ASSET_FAMILIES)
    unknown_nf = sorted(set(nf) - ALL_KNOWN_ASSET_FAMILIES)
    unknown_all = unknown_af + unknown_nf
    if unknown_all:
        raise ValueError(
            f"unknown asset family / anti-family: {unknown_all}. "
            f"Known families: {sorted(ALL_KNOWN_ASSET_FAMILIES)}"
        )

    conflicts = families_conflict(af, nf)
    if conflicts:
        raise ValueError(
            f"asset_families and anti_families must be disjoint; "
            f"conflicts: {conflicts}"
        )

    # Dedupe preserving order
    seen_af: set[str] = set()
    af_dedup = [f for f in af if not (f in seen_af or seen_af.add(f))]
    seen_nf: set[str] = set()
    nf_dedup = [f for f in nf if not (f in seen_nf or seen_nf.add(f))]
    return af_dedup, nf_dedup
