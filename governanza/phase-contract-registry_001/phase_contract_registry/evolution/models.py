from __future__ import annotations

from enum import Enum

from .._compat import dataclass
from ..domain.records import CompatibilityRecord, ContractDiffRecord
from ..domain.value_objects import ChangeDescriptor, ContractVersion


class VersionChangeKind(str, Enum):
    UNCHANGED = "unchanged"
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    DOWNGRADE = "downgrade"


@dataclass(frozen=True, slots=True)
class VersionDelta:
    source: ContractVersion
    target: ContractVersion
    change_kind: VersionChangeKind

    @property
    def changed(self) -> bool:
        return self.change_kind is not VersionChangeKind.UNCHANGED


class ChangeImpact(str, Enum):
    ADDITIVE = "additive"
    RESTRICTIVE = "restrictive"
    BREAKING = "breaking"
    UNKNOWN = "unknown"


@dataclass(frozen=True, slots=True)
class ClassifiedChange:
    descriptor: ChangeDescriptor
    impact: ChangeImpact
    migration_required: bool
    rationale: str


@dataclass(frozen=True, slots=True)
class ContractDiffResult:
    source_contract_type: str
    target_contract_type: str
    version_delta: VersionDelta | None
    changes: tuple[ChangeDescriptor, ...]
    classified_changes: tuple[ClassifiedChange, ...]
    diff_record: ContractDiffRecord | None

    @property
    def has_changes(self) -> bool:
        return bool(self.changes)

    @property
    def breaking_change_detected(self) -> bool:
        return any(change.impact is ChangeImpact.BREAKING for change in self.classified_changes)


class CompatibilityDecision(str, Enum):
    COMPATIBLE = "compatible"
    MIGRATION_REQUIRED = "migration_required"
    INCOMPATIBLE = "incompatible"


@dataclass(frozen=True, slots=True)
class CompatibilityEvaluation:
    decision: CompatibilityDecision
    migration_required: bool
    reasons: tuple[str, ...]
    diff_result: ContractDiffResult
    compatibility_record: CompatibilityRecord
