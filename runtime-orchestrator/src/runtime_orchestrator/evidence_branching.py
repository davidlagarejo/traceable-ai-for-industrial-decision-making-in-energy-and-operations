"""V8 P5 — Evidence Branching Engine.

Chief QA Architect § Error 5 + § E: el output actual repite un mismo
primary discriminator pack across casos / hipótesis. V8 P5 emite la
matriz per-hypothesis explícita.

Salida (`build_evidence_branches`):

  [
    {
      "hypothesis_id": "refrigeration_duty",
      "minimum_evidence":    [...],     # de pattern_spec.evidence_required + minimum_evidence_to_activate
      "cheapest_path":       [...],     # subset de minimum_evidence (heurística: 2-3 first items)
      "escalation_path":     [...],     # remaining items
      "confirms_when":       [...],     # de pattern_spec.minimum_evidence_to_confirm
      "falsifies_when":      [...],     # de pattern_spec.falsification_conditions
      "tad_impact":          [...],     # de pattern_spec.tad_actions (canonical)
    },
    ...
  ]

Además: helper `audit_branch_repetition` detecta cuando ≥ N branches
comparten Jaccard > threshold en minimum_evidence. Refuerza RU6
(motor_058 V7 P6) pero opera al nivel de la matriz, no del register.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Mapping, Sequence


# Heuristic split: first 3 items are "cheapest", rest is escalation.
_CHEAPEST_TAKE = 3


@dataclass(frozen=True)
class EvidenceBranch:
    hypothesis_id: str
    minimum_evidence:  tuple[str, ...]
    cheapest_path:     tuple[str, ...]
    escalation_path:   tuple[str, ...]
    confirms_when:     tuple[str, ...]
    falsifies_when:    tuple[str, ...]
    tad_impact:        tuple[str, ...]

    def as_dict(self) -> dict[str, Any]:
        return {
            "hypothesis_id":   self.hypothesis_id,
            "minimum_evidence": list(self.minimum_evidence),
            "cheapest_path":    list(self.cheapest_path),
            "escalation_path":  list(self.escalation_path),
            "confirms_when":    list(self.confirms_when),
            "falsifies_when":   list(self.falsifies_when),
            "tad_impact":       list(self.tad_impact),
        }


def _clean(items: Sequence[Any] | None) -> list[str]:
    """Strip + dedupe (preserving order)."""
    if not items:
        return []
    seen: set[str] = set()
    out: list[str] = []
    for it in items:
        s = str(it or "").strip()
        if not s or s in seen:
            continue
        seen.add(s)
        out.append(s)
    return out


def build_evidence_branch_from_spec(
    spec: Mapping[str, Any] | None,
) -> EvidenceBranch | None:
    """Build a single EvidenceBranch from a pattern_spec dict.

    Returns None when the spec is malformed or has no evidence path.
    """
    if not isinstance(spec, Mapping):
        return None
    hypothesis_id = str(spec.get("id") or spec.get("hypothesis_id") or "").strip()
    if not hypothesis_id:
        return None

    # Minimum evidence = union of evidence_required + minimum_evidence_to_activate.
    minimum_evidence = _clean(
        list(spec.get("evidence_required", []) or [])
        + list(spec.get("minimum_evidence_to_activate", []) or [])
    )

    cheapest_path = minimum_evidence[:_CHEAPEST_TAKE]
    escalation_path = minimum_evidence[_CHEAPEST_TAKE:]

    confirms_when = _clean(spec.get("minimum_evidence_to_confirm", []))
    falsifies_when = _clean(
        list(spec.get("falsification_conditions", []) or [])
        + list(spec.get("anti_triggers", []) or [])
    )
    tad_impact = _clean(spec.get("tad_actions", []))

    if not minimum_evidence:
        return None

    return EvidenceBranch(
        hypothesis_id=hypothesis_id,
        minimum_evidence=tuple(minimum_evidence),
        cheapest_path=tuple(cheapest_path),
        escalation_path=tuple(escalation_path),
        confirms_when=tuple(confirms_when),
        falsifies_when=tuple(falsifies_when),
        tad_impact=tuple(tad_impact),
    )


def build_evidence_branches(
    pattern_specs: Sequence[Mapping[str, Any]] | None,
) -> list[EvidenceBranch]:
    """Build the per-hypothesis matrix from a list of pattern_specs."""
    out: list[EvidenceBranch] = []
    for spec in pattern_specs or []:
        branch = build_evidence_branch_from_spec(spec)
        if branch is not None:
            out.append(branch)
    return out


# ── Repetition audit ───────────────────────────────────────────────


def _jaccard(a: set[str], b: set[str]) -> float:
    if not a and not b:
        return 0.0
    union = a | b
    if not union:
        return 0.0
    return len(a & b) / len(union)


_BRANCH_REPETITION_THRESHOLD: float = 0.80


def audit_branch_repetition(
    branches: Sequence[EvidenceBranch] | None,
    threshold: float = _BRANCH_REPETITION_THRESHOLD,
) -> list[dict[str, Any]]:
    """Cross-branch repetition audit.

    Returns one violation per pair (i, j) with Jaccard(minimum_evidence) > threshold.
    Refuerzo de motor_058 RU6 — opera sobre la matriz en lugar del register
    crudo de motor_054.
    """
    out: list[dict[str, Any]] = []
    pairs: set[tuple[str, str]] = set()
    branches = list(branches or [])
    for i in range(len(branches)):
        for j in range(i + 1, len(branches)):
            a = branches[i]
            b = branches[j]
            key = tuple(sorted((a.hypothesis_id, b.hypothesis_id)))
            if key in pairs:
                continue
            pairs.add(key)
            sim = _jaccard(set(a.minimum_evidence), set(b.minimum_evidence))
            if sim > threshold:
                out.append({
                    "rule_id": "EB1_branch_evidence_repetition",
                    "severity": "warning",
                    "hypothesis_a": a.hypothesis_id,
                    "hypothesis_b": b.hypothesis_id,
                    "jaccard": round(sim, 3),
                    "description": (
                        f"Evidence branches for {a.hypothesis_id!r} and "
                        f"{b.hypothesis_id!r} are {sim:.0%} similar — "
                        "each hypothesis should have a specialized evidence "
                        "path."
                    ),
                })
    return out


def summarize_branches(branches: Sequence[EvidenceBranch] | None) -> dict[str, Any]:
    """Cross-branch summary suitable for motor_016 / motor_017 consumption."""
    branches = list(branches or [])
    return {
        "branch_count": len(branches),
        "total_min_evidence_items": sum(len(b.minimum_evidence) for b in branches),
        "branches_with_falsifiers": sum(1 for b in branches if b.falsifies_when),
        "branches_without_tad_impact": sum(1 for b in branches if not b.tad_impact),
    }
