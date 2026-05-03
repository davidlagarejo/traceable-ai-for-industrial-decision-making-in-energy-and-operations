from __future__ import annotations

from enum import Enum


class PhaseId(str, Enum):
    PHASE_1 = "phase_1"
    PHASE_2 = "phase_2"
    PHASE_3 = "phase_3"
    PHASE_4 = "phase_4"


class ContractStatus(str, Enum):
    DRAFT = "draft"
    STAGED = "staged"
    PUBLISHED = "published"
    DEPRECATED = "deprecated"
    RETIRED = "retired"

    @property
    def is_published_lineage(self) -> bool:
        return self in {self.PUBLISHED, self.DEPRECATED, self.RETIRED}


class ValidationStatus(str, Enum):
    PASSED = "passed"
    FAILED = "failed"


class ViolationSeverity(str, Enum):
    ERROR = "error"
    WARNING = "warning"


class CompatibilityStatus(str, Enum):
    COMPATIBLE = "compatible"
    CONDITIONALLY_COMPATIBLE = "conditionally_compatible"
    INCOMPATIBLE = "incompatible"


class MigrationKind(str, Enum):
    PATCH = "patch"
    MINOR = "minor"
    MAJOR = "major"
    BREAKING = "breaking"


class ServingStatus(str, Enum):
    INACTIVE = "inactive"
    ACTIVE = "active"
    SUPERSEDED = "superseded"


class ScopeKind(str, Enum):
    PHASE_CONTRACT = "phase_contract"
    OBJECT_CONTRACT = "object_contract"
    TRANSITION_CONTRACT = "transition_contract"
    CONTRACT_SET = "contract_set"
    SNAPSHOT = "snapshot"


class ChangeKind(str, Enum):
    ADDITIVE = "additive"
    RESTRICTIVE = "restrictive"
    REMOVAL = "removal"
    RENAME = "rename"
    SEMANTIC_CHANGE = "semantic_change"
    METADATA_CHANGE = "metadata_change"

    @property
    def is_breaking_by_default(self) -> bool:
        return self in {
            self.RESTRICTIVE,
            self.REMOVAL,
            self.SEMANTIC_CHANGE,
        }

