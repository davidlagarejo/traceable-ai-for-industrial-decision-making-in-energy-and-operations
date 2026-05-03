"""Output models for motor_025 — Epistemic Governance Layer."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class EpistemicTension:
    tension_id: str
    tension_type: str
    affected_scope: Dict[str, List[str]]
    severity: str
    change_pressure: str
    evidence_refs: List[str]
    governing_contract_refs: List[str]
    recurrence_key: Optional[str]
    classification_basis: str
    detected_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: List[str]
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConstitutionalSignal:
    signal_id: str
    originating_tension_ids: List[str]
    change_class: str
    escalation_reason: str
    affected_contract_refs: List[str]
    recommended_review_path: str
    signal_severity: str
    emitted_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: List[str]
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class GovernanceHealthReport:
    report_id: str
    window_start: str
    window_end: str
    evaluated_contract_refs: List[str]
    tension_ids: List[str]
    constitutional_signal_ids: List[str]
    tension_counts_by_type: Dict[str, int]
    severity_counts: Dict[str, int]
    exception_inflation_score: float
    unresolved_signal_ids: List[str]
    evidence_coverage: Dict[str, int]
    governance_status: str
    classification_basis_summary: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: List[str]
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)
