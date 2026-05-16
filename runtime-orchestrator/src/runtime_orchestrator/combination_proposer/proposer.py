"""Combination Proposer — orquestador de las 6 estrategias.

Phase 0 inscribed: lee __init__.py del package.
"""
from __future__ import annotations

import datetime as _dt
import hashlib
import json
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Any


# ── Public dataclass ──────────────────────────────────────────────────


@dataclass
class ProposedCombination:
    """Una combination candidate producida deterministicamente.

    Compatible con el shape de combinations existentes en
    zlab_skill/registry/combinations/, con campos adicionales V10 P4.
    """
    # Identidad
    id:                       str
    pattern_set:              list[str]
    proposal_method:          str            # corpus_cooccurrence | regulatory_comention | constraint_x_pattern | compliance_violation | comfort_safety_window | investment_trap
    generated_at:             str            # ISO8601
    generated_by:             str = "framework_auto"
    status:                   str = "pending_human_review"
    confidence_score:         float = 0.0    # 0-1

    # Hipótesis y narrativa
    combined_hypothesis:      str = ""       # MUST be verbatim corpus quote
    strategic_risk:           str = ""

    # Contexto de activación
    context_predicates:       dict[str, Any] = field(default_factory=dict)

    # Evidencia
    corpus_citations:         list[dict[str, Any]] = field(default_factory=list)
    regulatory_basis:         list[dict[str, Any]] = field(default_factory=list)

    # Implicación para TAD
    decision_implication:     dict[str, Any] = field(default_factory=dict)
    consequence_if_ignored:   list[str] = field(default_factory=list)

    # Anti-triggers (cuándo NO usar)
    anti_triggers:            list[str] = field(default_factory=list)

    # Familias aplicables
    asset_families:           list[str] = field(default_factory=list)

    def stable_signature(self) -> str:
        """Hash determinístico = sorted(pattern_set) + sorted(predicate keys)
        + decision_implication.action. Usado para dedup contra approved/rejected."""
        keys = [
            ",".join(sorted(self.pattern_set)),
            ",".join(sorted((self.context_predicates.get("all") or [{}])[0].keys() if isinstance(self.context_predicates.get("all"), list) else self.context_predicates.keys())),
            str(self.decision_implication.get("action", "")),
        ]
        return hashlib.sha256("|".join(keys).encode()).hexdigest()[:16]

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


# ── Output path / dedup ───────────────────────────────────────────────


def _pending_dir() -> Path:
    """zlab_skill/registry/combinations_pending/"""
    return Path(__file__).resolve().parents[3] / "zlab_skill" / "registry" / "combinations_pending"


def _approved_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "zlab_skill" / "registry" / "combinations"


def _rejected_dir() -> Path:
    return Path(__file__).resolve().parents[3] / "zlab_skill" / "registry" / "combinations_rejected"


def _existing_signatures() -> set[str]:
    """Read every combination already in pending/approved/rejected to dedup."""
    seen: set[str] = set()
    for d in (_pending_dir(), _approved_dir(), _rejected_dir()):
        if not d.exists():
            continue
        for jp in d.glob("*.json"):
            try:
                data = json.loads(jp.read_text(encoding="utf-8"))
            except Exception:
                continue
            # Approved combinations may not have stable_signature stored —
            # reconstruct from pattern_set + decision_implication.
            pset = sorted(data.get("pattern_set") or data.get("pattern_ids") or [])
            action = (data.get("decision_implication") or {}).get("action", "")
            sig_keys = [",".join(pset), "", str(action)]
            sig = hashlib.sha256("|".join(sig_keys).encode()).hexdigest()[:16]
            seen.add(sig)
            # Also store any explicit signature field
            if data.get("stable_signature"):
                seen.add(data["stable_signature"])
    return seen


def write_candidate(candidate: ProposedCombination) -> Path:
    """Persist a candidate to combinations_pending/<id>.json. Idempotent."""
    out_dir = _pending_dir()
    out_dir.mkdir(parents=True, exist_ok=True)
    target = out_dir / f"{candidate.id}.json"
    payload = candidate.to_dict()
    payload["stable_signature"] = candidate.stable_signature()
    target.write_text(json.dumps(payload, indent=2, ensure_ascii=False),
                      encoding="utf-8")
    return target


# ── Orquestador ───────────────────────────────────────────────────────


def propose_combinations(
    asset_family:     str,
    active_patterns:  list[str],
    *,
    facility_prior:   dict[str, Any] | None = None,
    real_discovery:   dict[str, Any] | None = None,
    current_date:     _dt.datetime | None = None,
    write_to_disk:    bool = True,
    strategies:       tuple[str, ...] | None = None,
    max_per_strategy: int = 30,
) -> list[ProposedCombination]:
    """Run every enabled strategy and produce candidates.

    `strategies` filters which strategies to run (default: all 6).
    """
    if not asset_family or not active_patterns:
        return []
    current_date = current_date or _dt.datetime.utcnow()
    facility_prior = facility_prior or {}
    real_discovery = real_discovery or {}

    enabled = set(strategies or (
        "corpus_cooccurrence",
        "regulatory_comention",
        "constraint_x_pattern",
        "compliance_violation",
        "comfort_safety_window",
        "investment_trap",
    ))

    all_candidates: list[ProposedCombination] = []
    method_counts: dict[str, int] = {}

    # ── Strategy 1: corpus co-occurrence ──
    if "corpus_cooccurrence" in enabled:
        try:
            from .strategy_corpus import propose_from_corpus
            cands = propose_from_corpus(
                asset_family=asset_family,
                active_patterns=active_patterns,
                max_candidates=max_per_strategy,
            )
            method_counts["corpus_cooccurrence"] = len(cands)
            all_candidates.extend(cands)
        except Exception as exc:
            method_counts["corpus_cooccurrence_error"] = str(exc)[:120]

    # ── Strategy 2: regulatory co-mention ──
    if "regulatory_comention" in enabled:
        try:
            from .strategy_regulatory import propose_from_regulations
            cands = propose_from_regulations(
                asset_family=asset_family,
                active_patterns=active_patterns,
                max_candidates=max_per_strategy,
            )
            method_counts["regulatory_comention"] = len(cands)
            all_candidates.extend(cands)
        except Exception as exc:
            method_counts["regulatory_comention_error"] = str(exc)[:120]

    # ── Strategy 3: constraint × pattern matrix (HVAC summer, etc.) ──
    if "constraint_x_pattern" in enabled:
        try:
            from .strategy_context import propose_from_context_matrix
            cands = propose_from_context_matrix(
                asset_family=asset_family,
                active_patterns=active_patterns,
                max_candidates=max_per_strategy,
            )
            method_counts["constraint_x_pattern"] = len(cands)
            all_candidates.extend(cands)
        except Exception as exc:
            method_counts["constraint_x_pattern_error"] = str(exc)[:120]

    # ── Strategies 4-6 will be added in subsequent phases ──
    # strategy_compliance.propose_from_compliance_violations(...)
    # strategy_comfort.propose_from_comfort_windows(...)
    # strategy_invest_trap.propose_from_investment_traps(...)

    # Dedup against approved + rejected + pending already on disk
    seen = _existing_signatures()
    deduped: list[ProposedCombination] = []
    for c in all_candidates:
        if c.stable_signature() in seen:
            continue
        seen.add(c.stable_signature())
        deduped.append(c)

    # Persist + audit
    if write_to_disk:
        from .audit_log import write_audit_entry
        for c in deduped:
            write_candidate(c)
            write_audit_entry(c, asset_family=asset_family)

    return deduped
