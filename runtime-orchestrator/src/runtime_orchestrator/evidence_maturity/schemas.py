from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any

from .levels import EvidenceMaturityLevel, PermissionState, RecencyState, SourceAuthority, SourceScope


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
class VariableCatalogEntry:
    variable_name: str
    variable_family: str
    description: str
    observed_kind: str
    criticality: str
    default_scope: SourceScope
    unit_hint: str | None = None
    dependencies: list[str] = field(default_factory=list)
    decision_relevance: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ClaimTemplate:
    claim_name: str
    description: str
    required_variables: list[str]
    minimum_maturity_by_variable: dict[str, EvidenceMaturityLevel]
    allowed_outputs: list[str]
    prohibited_outputs: list[str]
    required_evidence: list[str] = field(default_factory=list)
    upgrade_path: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class DecisionTemplate:
    decision_name: str
    description: str
    required_variables: list[str]
    minimum_maturity_by_variable: dict[str, EvidenceMaturityLevel]
    allowed_actions: list[str]
    blocked_actions: list[str]
    evidence_pack_focus: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class DatasetDefinition:
    dataset_key: str
    display_name: str
    jurisdiction: str
    authority: SourceAuthority
    scope: SourceScope
    coverage_variables: list[str]
    required_for: list[str]
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class VariableMatrixDefinition:
    variable_name: str
    level_definitions: dict[EvidenceMaturityLevel, str]
    outputs_allowed: dict[EvidenceMaturityLevel, list[str]]
    outputs_forbidden: dict[EvidenceMaturityLevel, list[str]]
    upgrade_evidence: list[str]
    decisions_unlocked: dict[EvidenceMaturityLevel, list[str]]

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass
class VariableMaturityRecord:
    variable_name: str
    variable_family: str
    value: Any
    maturity_level: EvidenceMaturityLevel
    evidence_source: str
    source_scope: SourceScope
    authority_score: SourceAuthority
    recency: RecencyState
    uncertainty_reason: str
    allowed_outputs: list[str] = field(default_factory=list)
    prohibited_outputs: list[str] = field(default_factory=list)
    upgrade_condition: str = ""
    downgrade_condition: str = ""
    decisions_unlocked: list[str] = field(default_factory=list)
    dependent_claims: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass
class ClusterMaturityRecord:
    cluster_name: str
    maturity_level: EvidenceMaturityLevel
    evidence: list[str] = field(default_factory=list)
    source: list[str] = field(default_factory=list)
    consequence: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass
class ClaimPermissionRecord:
    claim_name: str
    required_variables: list[str]
    minimum_maturity_level: dict[str, EvidenceMaturityLevel]
    current_permission: PermissionState
    reason_if_blocked: str
    required_evidence: list[str] = field(default_factory=list)
    dependency_variables: list[str] = field(default_factory=list)
    upgrade_path: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass
class DecisionPermissionRecord:
    decision_name: str
    required_variables: list[str]
    current_variable_bottleneck: str
    admissibility_state: PermissionState
    evidence_needed: list[str]
    allowed_action: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass
class ReportReadinessRecord:
    report_type_allowed: list[str]
    report_type_prohibited: list[str]
    reason: str
    minimum_evidence_missing: list[str]
    next_evidence_pack: list[str]

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
