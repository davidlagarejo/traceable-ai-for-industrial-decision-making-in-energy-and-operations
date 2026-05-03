from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any


class StructuralEvidenceState(str, Enum):
    OBSERVED_FACT = "OBSERVED_FACT"
    ARCHETYPAL_PRIOR = "ARCHETYPAL_PRIOR"
    CONDITIONAL_HYPOTHESIS = "CONDITIONAL_HYPOTHESIS"
    INADMISSIBLE_CLAIM = "INADMISSIBLE_CLAIM"
    NOT_OBSERVED = "NOT_OBSERVED"


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    return value


@dataclass(frozen=True)
class EvidenceBoundField:
    field_name: str
    value: Any
    evidence_state: StructuralEvidenceState
    falsification_condition: str
    minimum_evidence_required: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class StructuralStatement:
    statement: str
    evidence_state: StructuralEvidenceState
    supporting_sources: list[str]
    falsification_condition: str
    minimum_evidence_required: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class CrossLayerConflictRecord:
    conflict: str
    layers_involved: list[str]
    evidence_state: StructuralEvidenceState
    why_it_matters: str
    what_confirms_it: list[str] = field(default_factory=list)
    what_falsifies_it: list[str] = field(default_factory=list)
    potential_redesign_direction: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ProblemFramingRecord:
    stated_problem: str
    reframed_problem: str
    why_original_framing_may_be_wrong: str
    evidence_needed: list[str] = field(default_factory=list)
    strategic_risk: str = ""
    evidence_state: StructuralEvidenceState = StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    linked_layers: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class StructuralBenchmarkRecord:
    dimension: str
    subject_asset: str
    peer_or_benchmark: str
    difference: str
    evidence_state: StructuralEvidenceState
    interpretation: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class CompetitiveComparisonRecord:
    better_performer: str
    what_they_do_better: str
    structural_advantage: str
    why_it_matters: str
    transferability: str
    peer_type: str = ""
    what_it_proves: str = ""
    what_it_does_not_prove: str = ""
    source_reference: str = ""
    evidence_needed: list[str] = field(default_factory=list)
    evidence_state: StructuralEvidenceState = StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    comparison_mode: str = "conditional_comparison"

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ConditionalRedesignRecord:
    hypothesis: str
    evidence_state: StructuralEvidenceState
    if_confirmed: str
    redesign_direction: str
    if_falsified: str
    trigger_hypothesis: str = ""
    conflict_resolved: str = ""
    economic_logic: str = ""
    evidence_needed: list[str] = field(default_factory=list)
    kill_condition: str = ""
    next_evidence: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class StructuralFinancialExposureRecord:
    structural_assumption: str
    evidence_state: StructuralEvidenceState
    financial_exposure_if_wrong: str
    evidence_needed: list[str] = field(default_factory=list)
    allowed_financial_output: list[str] = field(default_factory=list)
    prohibited_financial_output: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class EvidenceStateByLayerRecord:
    layer: str
    evidence_state: StructuralEvidenceState
    dominant_open_questions: list[str] = field(default_factory=list)
    observed_support: list[str] = field(default_factory=list)
    structural_risk_if_wrong: str = ""
    linked_conflicts: list[str] = field(default_factory=list)
    linked_problem_frames: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class MinimumEvidenceDiscriminationRecord:
    rival_hypotheses: list[str]
    minimum_evidence: str
    source: str
    what_it_confirms: str
    what_it_falsifies: str
    unlocks: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ArchetypeSelectionBasis:
    dimension: str
    value: str
    evidence_state: StructuralEvidenceState
    source: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class DominantVariableHypothesis:
    variable: str
    layer: str
    dominance: str
    evidence_state: StructuralEvidenceState
    why_it_could_matter: str
    what_confirms_it: list[str] = field(default_factory=list)
    what_falsifies_it: list[str] = field(default_factory=list)
    decision_impact: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ArchetypeDefinition:
    archetype_id: str
    label: str
    asset_type: str
    business_function: str
    value_creation_mechanism: str
    dominant_process_type: str
    dominant_physical_drivers: list[str]
    dominant_operational_drivers: list[str]
    control_structure: str
    constraint_structure: str
    economic_driver: str
    regulatory_exposure: str
    critical_systems: list[str] = field(default_factory=list)
    operational_risks: list[str] = field(default_factory=list)
    regulatory_risks: list[str] = field(default_factory=list)
    relevant_metrics: list[str] = field(default_factory=list)
    comparable_lenses: list[str] = field(default_factory=list)
    minimum_evidence_required: list[str] = field(default_factory=list)
    dominant_variable_hypotheses: list[DominantVariableHypothesis] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ArchetypeResolution:
    selected_archetype_id: str
    label: str
    match_confidence: str
    resolver_state: str
    archetype_evidence_state: StructuralEvidenceState
    why_selected: str
    selection_basis_register: list[ArchetypeSelectionBasis] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
