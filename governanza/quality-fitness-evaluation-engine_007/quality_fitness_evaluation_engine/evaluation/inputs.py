from __future__ import annotations

from enum import IntEnum

from .._compat import dataclass
from ..domain.enums import IssueType
from ..domain.value_objects import (
    ContractRef,
    EvaluatedObjectRef,
    EvaluatedObjectVersionRef,
    FitnessTarget,
    ObjectTypeName,
    TraceabilityAspect,
    TransitionRef,
    ValidationRuleRecordId,
    _ensure_unique,
    _require_text,
)


class GranularityLevel(IntEnum):
    BUNDLE = 10
    TABLE = 20
    RECORD = 30
    FIELD = 40

    def satisfies(self, minimum: "GranularityLevel") -> bool:
        return int(self) >= int(minimum)


@dataclass(frozen=True, slots=True)
class EvaluableObjectSnapshot:
    evaluated_object_ref: EvaluatedObjectRef
    evaluated_object_version_ref: EvaluatedObjectVersionRef | None
    object_type_name: ObjectTypeName
    present_fields: tuple[str, ...]
    semantic_content_present: bool
    lineage_refs: tuple[str, ...] = ()
    provenance_refs: tuple[str, ...] = ()
    contract_refs: tuple[ContractRef, ...] = ()
    transition_refs: tuple[TransitionRef, ...] = ()
    source_dependency_refs: tuple[str, ...] = ()
    stale_dependency_refs: tuple[str, ...] = ()
    component_keys: tuple[str, ...] = ()
    uncertainty_markers: tuple[str, ...] = ()
    granularity_level: GranularityLevel = GranularityLevel.BUNDLE
    is_sparse: bool = False
    is_partial: bool = False
    contract_version_current: bool | None = None

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "present_fields",
            tuple(_require_text(item, "present_field") for item in self.present_fields),
        )
        object.__setattr__(
            self,
            "lineage_refs",
            tuple(_require_text(item, "lineage_ref") for item in self.lineage_refs),
        )
        object.__setattr__(
            self,
            "provenance_refs",
            tuple(_require_text(item, "provenance_ref") for item in self.provenance_refs),
        )
        object.__setattr__(
            self,
            "source_dependency_refs",
            tuple(
                _require_text(item, "source_dependency_ref")
                for item in self.source_dependency_refs
            ),
        )
        object.__setattr__(
            self,
            "stale_dependency_refs",
            tuple(
                _require_text(item, "stale_dependency_ref")
                for item in self.stale_dependency_refs
            ),
        )
        object.__setattr__(
            self,
            "component_keys",
            tuple(_require_text(item, "component_key") for item in self.component_keys),
        )
        object.__setattr__(
            self,
            "uncertainty_markers",
            tuple(
                _require_text(item, "uncertainty_marker")
                for item in self.uncertainty_markers
            ),
        )
        _ensure_unique(self.present_fields, "EvaluableObjectSnapshot.present_fields")
        _ensure_unique(self.lineage_refs, "EvaluableObjectSnapshot.lineage_refs")
        _ensure_unique(self.provenance_refs, "EvaluableObjectSnapshot.provenance_refs")
        _ensure_unique(
            self.source_dependency_refs,
            "EvaluableObjectSnapshot.source_dependency_refs",
        )
        _ensure_unique(
            self.stale_dependency_refs,
            "EvaluableObjectSnapshot.stale_dependency_refs",
        )
        _ensure_unique(self.component_keys, "EvaluableObjectSnapshot.component_keys")
        _ensure_unique(
            self.uncertainty_markers,
            "EvaluableObjectSnapshot.uncertainty_markers",
        )
        _ensure_unique(self.contract_refs, "EvaluableObjectSnapshot.contract_refs")
        _ensure_unique(self.transition_refs, "EvaluableObjectSnapshot.transition_refs")


@dataclass(frozen=True, slots=True)
class StructuralRuleSpec:
    validation_rule_record_id: ValidationRuleRecordId
    required_fields: tuple[str, ...] = ()
    require_semantic_content: bool = False

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_fields",
            tuple(_require_text(item, "required_field") for item in self.required_fields),
        )
        _ensure_unique(self.required_fields, "StructuralRuleSpec.required_fields")


@dataclass(frozen=True, slots=True)
class TraceabilityRuleSpec:
    validation_rule_record_id: ValidationRuleRecordId
    traceability_aspect: TraceabilityAspect
    issue_type: IssueType = IssueType.TRACEABILITY_FAILURE
    require_lineage_refs: bool = False
    require_provenance_refs: bool = False
    require_version_ref: bool = False
    require_source_dependencies: bool = False
    require_uncertainty_markers: bool = False
    reject_stale_dependencies: bool = False


@dataclass(frozen=True, slots=True)
class ContractRuleSpec:
    validation_rule_record_id: ValidationRuleRecordId
    contract_ref: ContractRef
    require_subject_contract_refs: bool = True
    required_contract_refs: tuple[ContractRef, ...] = ()
    require_transition_ref: bool = False
    require_current_contract_version: bool = False

    def __post_init__(self) -> None:
        _ensure_unique(self.required_contract_refs, "ContractRuleSpec.required_contract_refs")


@dataclass(frozen=True, slots=True)
class FitnessRuleSpec:
    validation_rule_record_id: ValidationRuleRecordId
    fitness_target: FitnessTarget
    minimum_granularity: GranularityLevel | None = None
    required_component_keys: tuple[str, ...] = ()
    allow_sparse: bool = True
    allow_partial: bool = True

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "required_component_keys",
            tuple(
                _require_text(item, "required_component_key")
                for item in self.required_component_keys
            ),
        )
        _ensure_unique(
            self.required_component_keys,
            "FitnessRuleSpec.required_component_keys",
        )
