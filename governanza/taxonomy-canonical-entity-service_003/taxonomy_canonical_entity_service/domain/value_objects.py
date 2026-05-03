from __future__ import annotations

from datetime import datetime
from typing import Iterable, Union

from .._compat import dataclass
from .enums import (
    PhaseId,
    TaxonomyDomain,
    TaxonomyLocatorKind,
)
from .errors import DomainInvariantError


def _require_text(value: str, field_name: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise DomainInvariantError(f"{field_name} must be non-empty.")
    return normalized


def _require_timezone(value: datetime, field_name: str) -> datetime:
    if value.tzinfo is None or value.tzinfo.utcoffset(value) is None:
        raise DomainInvariantError(f"{field_name} must be timezone-aware.")
    return value


def _ensure_unique(values: Iterable[object], field_name: str) -> None:
    materialized = tuple(values)
    if len(materialized) != len(set(materialized)):
        raise DomainInvariantError(f"{field_name} must not contain duplicates.")


@dataclass(frozen=True, slots=True)
class TaxonomyRegistryId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TaxonomyRegistryId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TaxonomyVersionId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TaxonomyVersionId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TaxonomyNodeId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TaxonomyNodeId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalTermId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "CanonicalTermId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AliasRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "AliasRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class LegacyTermRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "LegacyTermRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalEntityId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "CanonicalEntityId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EntityMembershipRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EntityMembershipRecordId.value"))


@dataclass(frozen=True, slots=True)
class EquivalenceRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EquivalenceRecordId.value"))


@dataclass(frozen=True, slots=True)
class CandidateMatchRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "CandidateMatchRecordId.value"))


@dataclass(frozen=True, slots=True)
class BoundaryRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "BoundaryRecordId.value"))


@dataclass(frozen=True, slots=True)
class JoinKeySemanticRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "JoinKeySemanticRecordId.value"))


@dataclass(frozen=True, slots=True)
class DeprecationRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "DeprecationRecordId.value"))


@dataclass(frozen=True, slots=True)
class TaxonomyChangeRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TaxonomyChangeRecordId.value"))


@dataclass(frozen=True, slots=True)
class SemanticIntegrityRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SemanticIntegrityRecordId.value"))


@dataclass(frozen=True, slots=True)
class Label:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "Label.value"))

    @property
    def normalized(self) -> str:
        return " ".join(self.value.casefold().split())

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CanonicalName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "CanonicalName.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VersionLabel:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "VersionLabel.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class VersionFingerprint:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "VersionFingerprint.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class AuthoritySource:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "AuthoritySource.value"))


@dataclass(frozen=True, slots=True)
class SemanticText:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SemanticText.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class MatchRationale:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "MatchRationale.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class JoinKeyName:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "JoinKeyName.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ConfidenceScore:
    value: float

    def __post_init__(self) -> None:
        if self.value < 0.0 or self.value > 1.0:
            raise DomainInvariantError("ConfidenceScore.value must be between 0.0 and 1.0.")

    def __float__(self) -> float:
        return self.value


@dataclass(frozen=True, slots=True)
class PhaseApplicability:
    phase_ids: tuple[PhaseId, ...]

    def __post_init__(self) -> None:
        _ensure_unique(self.phase_ids, "phase_ids")

    @property
    def applies_globally(self) -> bool:
        return not self.phase_ids


@dataclass(frozen=True, slots=True)
class SemanticScope:
    scope_key: str
    taxonomy_domain: TaxonomyDomain | None
    phase_applicability: PhaseApplicability

    def __post_init__(self) -> None:
        object.__setattr__(self, "scope_key", _require_text(self.scope_key, "scope_key"))


TaxonomyLocatorIdentifier = Union[
    TaxonomyRegistryId,
    TaxonomyVersionId,
    TaxonomyNodeId,
    CanonicalTermId,
    AliasRecordId,
    LegacyTermRecordId,
    CanonicalEntityId,
]


@dataclass(frozen=True, slots=True)
class TaxonomyLocator:
    target_kind: TaxonomyLocatorKind
    identifier: TaxonomyLocatorIdentifier

    def __post_init__(self) -> None:
        expected_type = {
            TaxonomyLocatorKind.TAXONOMY_REGISTRY: TaxonomyRegistryId,
            TaxonomyLocatorKind.TAXONOMY_VERSION: TaxonomyVersionId,
            TaxonomyLocatorKind.TAXONOMY_NODE: TaxonomyNodeId,
            TaxonomyLocatorKind.CANONICAL_TERM: CanonicalTermId,
            TaxonomyLocatorKind.ALIAS_RECORD: AliasRecordId,
            TaxonomyLocatorKind.LEGACY_TERM_RECORD: LegacyTermRecordId,
            TaxonomyLocatorKind.CANONICAL_ENTITY: CanonicalEntityId,
        }[self.target_kind]
        if not isinstance(self.identifier, expected_type):
            raise DomainInvariantError("TaxonomyLocator.identifier does not match target_kind.")

    @classmethod
    def for_taxonomy_registry(cls, identifier: TaxonomyRegistryId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.TAXONOMY_REGISTRY, identifier)

    @classmethod
    def for_taxonomy_version(cls, identifier: TaxonomyVersionId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.TAXONOMY_VERSION, identifier)

    @classmethod
    def for_taxonomy_node(cls, identifier: TaxonomyNodeId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.TAXONOMY_NODE, identifier)

    @classmethod
    def for_canonical_term(cls, identifier: CanonicalTermId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.CANONICAL_TERM, identifier)

    @classmethod
    def for_alias_record(cls, identifier: AliasRecordId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.ALIAS_RECORD, identifier)

    @classmethod
    def for_legacy_term_record(cls, identifier: LegacyTermRecordId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.LEGACY_TERM_RECORD, identifier)

    @classmethod
    def for_canonical_entity(cls, identifier: CanonicalEntityId) -> "TaxonomyLocator":
        return cls(TaxonomyLocatorKind.CANONICAL_ENTITY, identifier)


__all__ = [
    "AliasRecordId",
    "AuthoritySource",
    "BoundaryRecordId",
    "CanonicalEntityId",
    "CanonicalName",
    "CanonicalTermId",
    "CandidateMatchRecordId",
    "ConfidenceScore",
    "DeprecationRecordId",
    "EntityMembershipRecordId",
    "EquivalenceRecordId",
    "JoinKeyName",
    "JoinKeySemanticRecordId",
    "Label",
    "LegacyTermRecordId",
    "MatchRationale",
    "PhaseApplicability",
    "SemanticIntegrityRecordId",
    "SemanticScope",
    "SemanticText",
    "TaxonomyChangeRecordId",
    "TaxonomyLocator",
    "TaxonomyNodeId",
    "TaxonomyRegistryId",
    "TaxonomyVersionId",
    "VersionFingerprint",
    "VersionLabel",
    "_ensure_unique",
    "_require_text",
    "_require_timezone",
]

