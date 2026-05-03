from __future__ import annotations

from datetime import datetime
from decimal import Decimal, InvalidOperation
from typing import Iterable

from .._compat import dataclass
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


def _require_decimal(
    value: Decimal | str | int | float,
    field_name: str,
    *,
    minimum: Decimal | None = None,
    maximum: Decimal | None = None,
) -> Decimal:
    try:
        decimal_value = value if isinstance(value, Decimal) else Decimal(str(value))
    except (InvalidOperation, ValueError) as exc:
        raise DomainInvariantError(f"{field_name} must be a valid decimal.") from exc
    if minimum is not None and decimal_value < minimum:
        raise DomainInvariantError(f"{field_name} must be >= {minimum}.")
    if maximum is not None and decimal_value > maximum:
        raise DomainInvariantError(f"{field_name} must be <= {maximum}.")
    return decimal_value


@dataclass(frozen=True, slots=True)
class ObservedRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ObservedRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObservedNameRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "ObservedNameRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EntityId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EntityId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EntityAliasRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EntityAliasRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CandidateMatchRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CandidateMatchRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class CandidateMatchSetId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "CandidateMatchSetId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ResolutionDecisionRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ResolutionDecisionRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ResolutionEvidenceRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ResolutionEvidenceRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ResolutionConfidenceRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ResolutionConfidenceRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class MergeEventRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "MergeEventRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class SplitEventRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "SplitEventRecordId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class EntityHistoryRecordId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "EntityHistoryRecordId.value"),
        )

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedRecordRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "NormalizedRecordRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class NormalizedFieldRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "NormalizedFieldRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class TaxonomyRef:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "TaxonomyRef.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ObservedLabel:
    value: str
    normalized: str | None = None

    def __post_init__(self) -> None:
        value = _require_text(self.value, "ObservedLabel.value")
        normalized = value.casefold() if self.normalized is None else _require_text(
            self.normalized,
            "ObservedLabel.normalized",
        )
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "normalized", normalized)


@dataclass(frozen=True, slots=True)
class AliasLabel:
    value: str
    normalized: str | None = None

    def __post_init__(self) -> None:
        value = _require_text(self.value, "AliasLabel.value")
        normalized = value.casefold() if self.normalized is None else _require_text(
            self.normalized,
            "AliasLabel.normalized",
        )
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "normalized", normalized)


@dataclass(frozen=True, slots=True)
class CanonicalName:
    value: str
    normalized: str | None = None

    def __post_init__(self) -> None:
        value = _require_text(self.value, "CanonicalName.value")
        normalized = value.casefold() if self.normalized is None else _require_text(
            self.normalized,
            "CanonicalName.normalized",
        )
        object.__setattr__(self, "value", value)
        object.__setattr__(self, "normalized", normalized)


@dataclass(frozen=True, slots=True)
class Rationale:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "Rationale.value"))


@dataclass(frozen=True, slots=True)
class AmbiguityBasis:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "AmbiguityBasis.value"))


@dataclass(frozen=True, slots=True)
class RelationBasis:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "RelationBasis.value"))


@dataclass(frozen=True, slots=True)
class EvidenceSummary:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EvidenceSummary.value"))


@dataclass(frozen=True, slots=True)
class ConfidenceMethod:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "ConfidenceMethod.value"),
        )


@dataclass(frozen=True, slots=True)
class ConfidenceValue:
    value: Decimal

    def __init__(self, value: Decimal | str | int | float) -> None:
        object.__setattr__(
            self,
            "value",
            _require_decimal(
                value,
                "ConfidenceValue.value",
                minimum=Decimal("0"),
                maximum=Decimal("1"),
            ),
        )


@dataclass(frozen=True, slots=True)
class EntityHistorySummary:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "value",
            _require_text(self.value, "EntityHistorySummary.value"),
        )


@dataclass(frozen=True, slots=True)
class SourceProvenanceRefs:
    normalized_record_ref: NormalizedRecordRef | None
    normalized_field_refs: tuple[NormalizedFieldRef, ...] = ()
    taxonomy_refs: tuple[TaxonomyRef, ...] = ()

    def __post_init__(self) -> None:
        _ensure_unique(self.normalized_field_refs, "SourceProvenanceRefs.normalized_field_refs")
        _ensure_unique(self.taxonomy_refs, "SourceProvenanceRefs.taxonomy_refs")
        if self.normalized_record_ref is None and not self.normalized_field_refs:
            raise DomainInvariantError(
                "SourceProvenanceRefs requires normalized_record_ref or normalized_field_refs."
            )
