"""V9 P1 — Fair Comparison Engine (10-dimensional peer comparability).

Chief Systems Architect § 4: "NO comparar warehouses genéricos / cold-chain
vs dry storage / activos con diferente thermal regime / throughput /
service intensity. Cada peer set debe incluir 10 dimensiones."

motor_051 hace fair_comparison parcial pero no emite un objeto estructurado
con las 10 dimensiones canónicas ni un `comparability_score` explícito.

V9 P1 cierra ese gap:
  - `PeerComparabilityContract` con 10 dimensiones.
  - `evaluate_peer_set(candidate, peer_set) → ComparabilityVerdict`.
  - `peer_set_admissible(verdict) → bool` (helper).
  - `R14_peer_ranking_with_incomplete_comparability` blocking rule.

Las 10 dimensiones canónicas:
  1. asset_family       — cold_chain, manufacturing, warehouse, ...
  2. process_family     — refrigeration, thermal_process, mhe_logistics, ...
  3. thermal_regime     — ambient / refrigerated / frozen / process_heat
  4. throughput_band    — small / medium / large
  5. operating_hours    — 8x5 / 16x5 / 24x7
  6. dock_density       — docks per kSF
  7. charging_profile   — battery_swap / opportunity / overnight / none
  8. tariff_profile     — flat / TOU / demand_billed / coincident_peak
  9. control_boundary   — owner_operator / triple_net / tenant_owned
 10. regulatory_context — IIAR / EPA NESHAP / state-permit / none

Match rules:
  - All 10 dims must be declared (otherwise comparability=incomplete).
  - Each dim matches if candidate_value == peer_value (case-insensitive).
  - `comparability_score` = matched_dims / 10.
  - admissible if score ≥ 0.70 AND all dims declared.

Phase 0 anchor: NO peer ranking si comparability incomplete.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


CANONICAL_PEER_DIMENSIONS: tuple[str, ...] = (
    "asset_family",
    "process_family",
    "thermal_regime",
    "throughput_band",
    "operating_hours",
    "dock_density",
    "charging_profile",
    "tariff_profile",
    "control_boundary",
    "regulatory_context",
)

_DEFAULT_ADMISSIBILITY_THRESHOLD: float = 0.70


@dataclass(frozen=True)
class PeerComparabilityContract:
    """A peer comparability contract: candidate vs peer_set with the 10
    canonical dimensions declared."""
    candidate_id: str
    peer_id: str
    matched_dimensions: tuple[str, ...]
    mismatched_dimensions: tuple[str, ...]
    missing_dimensions: tuple[str, ...]  # dimensions absent in either side
    comparability_score: float

    @property
    def all_dimensions_declared(self) -> bool:
        return not self.missing_dimensions

    @property
    def admissible(self) -> bool:
        """A peer is admissible only when ALL dimensions declared AND
        score ≥ threshold (default 0.70)."""
        return (
            self.all_dimensions_declared
            and self.comparability_score >= _DEFAULT_ADMISSIBILITY_THRESHOLD
        )

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id":             self.candidate_id,
            "peer_id":                  self.peer_id,
            "matched_dimensions":       list(self.matched_dimensions),
            "mismatched_dimensions":    list(self.mismatched_dimensions),
            "missing_dimensions":       list(self.missing_dimensions),
            "comparability_score":      round(self.comparability_score, 3),
            "all_dimensions_declared":  self.all_dimensions_declared,
            "admissible":               self.admissible,
        }


@dataclass(frozen=True)
class ComparabilityVerdict:
    """Verdict over an entire peer set."""
    candidate_id: str
    contracts: tuple[PeerComparabilityContract, ...]
    admissible_peers: tuple[str, ...]
    rejected_peers: tuple[str, ...]
    threshold: float

    @property
    def has_admissible_peer(self) -> bool:
        return len(self.admissible_peers) > 0

    @property
    def peer_set_admissible(self) -> bool:
        """V9 P1 doctrine: if NO peer in the set is admissible, the peer
        ranking section MUST NOT render."""
        return self.has_admissible_peer

    def as_dict(self) -> dict[str, Any]:
        return {
            "candidate_id":         self.candidate_id,
            "contracts":            [c.as_dict() for c in self.contracts],
            "admissible_peers":     list(self.admissible_peers),
            "rejected_peers":       list(self.rejected_peers),
            "threshold":            self.threshold,
            "has_admissible_peer":  self.has_admissible_peer,
            "peer_set_admissible":  self.peer_set_admissible,
        }


def _norm(v: Any) -> str:
    """Normalize value for comparison: trim + lower."""
    return str(v or "").strip().lower()


def _declared_dimensions(profile: Mapping[str, Any]) -> dict[str, str]:
    """Extract declared dimensions from a profile (case-insensitive, trim)."""
    if not isinstance(profile, Mapping):
        return {}
    return {
        dim: _norm(profile.get(dim))
        for dim in CANONICAL_PEER_DIMENSIONS
        if _norm(profile.get(dim))
    }


def build_peer_contract(
    candidate: Mapping[str, Any],
    peer: Mapping[str, Any],
) -> PeerComparabilityContract:
    """Build a per-peer comparability contract.

    Both candidate and peer must be dicts with the 10 canonical
    dimensions as top-level keys. Missing dimensions on EITHER side are
    flagged as `missing_dimensions`.
    """
    cand = _declared_dimensions(candidate)
    peer_d = _declared_dimensions(peer)
    matched: list[str] = []
    mismatched: list[str] = []
    missing: list[str] = []
    for dim in CANONICAL_PEER_DIMENSIONS:
        if dim not in cand or dim not in peer_d:
            missing.append(dim)
            continue
        if cand[dim] == peer_d[dim]:
            matched.append(dim)
        else:
            mismatched.append(dim)
    declared_total = len(CANONICAL_PEER_DIMENSIONS) - len(missing)
    score = (len(matched) / len(CANONICAL_PEER_DIMENSIONS)) if declared_total else 0.0
    cand_id = str(candidate.get("id") or candidate.get("candidate_id") or "candidate")
    peer_id = str(peer.get("id") or peer.get("peer_id") or "peer")
    return PeerComparabilityContract(
        candidate_id=cand_id,
        peer_id=peer_id,
        matched_dimensions=tuple(matched),
        mismatched_dimensions=tuple(mismatched),
        missing_dimensions=tuple(missing),
        comparability_score=score,
    )


def evaluate_peer_set(
    candidate: Mapping[str, Any],
    peer_set: Sequence[Mapping[str, Any]] | None,
    threshold: float = _DEFAULT_ADMISSIBILITY_THRESHOLD,
) -> ComparabilityVerdict:
    """Evaluate the entire peer set against the candidate.

    Returns a ComparabilityVerdict where:
      - admissible_peers = peers with score ≥ threshold AND all dims declared
      - rejected_peers   = the rest
    """
    contracts: list[PeerComparabilityContract] = []
    admissible: list[str] = []
    rejected: list[str] = []
    cand_id = str(candidate.get("id") or candidate.get("candidate_id") or "candidate")
    for peer in peer_set or []:
        if not isinstance(peer, Mapping):
            continue
        c = build_peer_contract(candidate, peer)
        contracts.append(c)
        is_admissible = c.all_dimensions_declared and c.comparability_score >= threshold
        if is_admissible:
            admissible.append(c.peer_id)
        else:
            rejected.append(c.peer_id)
    return ComparabilityVerdict(
        candidate_id=cand_id,
        contracts=tuple(contracts),
        admissible_peers=tuple(admissible),
        rejected_peers=tuple(rejected),
        threshold=threshold,
    )


def peer_set_admissible(verdict: ComparabilityVerdict) -> bool:
    """Helper: True iff the peer set has at least 1 admissible peer."""
    return verdict.peer_set_admissible


def summarize_for_motor_output(verdict: ComparabilityVerdict) -> dict[str, Any]:
    """Compact summary suitable for motor_051 output."""
    return {
        "peer_set_admissible":   verdict.peer_set_admissible,
        "admissible_peer_count": len(verdict.admissible_peers),
        "rejected_peer_count":   len(verdict.rejected_peers),
        "threshold":             verdict.threshold,
        "average_comparability_score": (
            sum(c.comparability_score for c in verdict.contracts) / len(verdict.contracts)
            if verdict.contracts else 0.0
        ),
        "incomplete_peer_count": sum(
            1 for c in verdict.contracts if not c.all_dimensions_declared
        ),
    }
