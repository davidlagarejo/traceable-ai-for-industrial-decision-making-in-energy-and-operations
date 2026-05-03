from __future__ import annotations

from datetime import datetime
from typing import Iterable

from .._compat import dataclass
from .enums import ChangeKind, ScopeKind
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
class EntityId:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "EntityId.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, order=True, slots=True)
class ContractVersion:
    major: int
    minor: int
    patch: int

    def __post_init__(self) -> None:
        for field_name in ("major", "minor", "patch"):
            if getattr(self, field_name) < 0:
                raise DomainInvariantError(f"{field_name} must be >= 0.")

    @classmethod
    def parse(cls, raw: str) -> "ContractVersion":
        normalized = _require_text(raw, "ContractVersion.raw")
        parts = normalized.split(".")
        if len(parts) != 3 or not all(part.isdigit() for part in parts):
            raise DomainInvariantError("ContractVersion must use major.minor.patch.")
        return cls(*(int(part) for part in parts))

    def __str__(self) -> str:
        return f"{self.major}.{self.minor}.{self.patch}"


@dataclass(frozen=True, slots=True)
class MetadataKey:
    value: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "value", _require_text(self.value, "MetadataKey.value"))

    def __str__(self) -> str:
        return self.value


@dataclass(frozen=True, slots=True)
class ScopedContractRef:
    scope_kind: ScopeKind
    identifier: EntityId
    version: ContractVersion | None = None

    def __post_init__(self) -> None:
        if self.scope_kind in {ScopeKind.PHASE_CONTRACT, ScopeKind.SNAPSHOT} and self.version is None:
            raise DomainInvariantError(
                "Versioned contract references must include a contract version."
            )


@dataclass(frozen=True, slots=True)
class EpistemicPolicyFragment:
    policy_key: str
    scope_kind: ScopeKind
    scope_ref: ScopedContractRef
    allowed_state_tokens: tuple[str, ...]
    forbidden_state_tokens: tuple[str, ...]
    must_preserve_uncertainty: bool
    must_preserve_conflict: bool
    output_ceiling_rule: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "policy_key", _require_text(self.policy_key, "policy_key"))
        object.__setattr__(
            self,
            "output_ceiling_rule",
            _require_text(self.output_ceiling_rule, "output_ceiling_rule"),
        )
        object.__setattr__(
            self,
            "allowed_state_tokens",
            tuple(_require_text(token, "allowed_state_token") for token in self.allowed_state_tokens),
        )
        object.__setattr__(
            self,
            "forbidden_state_tokens",
            tuple(
                _require_text(token, "forbidden_state_token")
                for token in self.forbidden_state_tokens
            ),
        )
        _ensure_unique(self.allowed_state_tokens, "allowed_state_tokens")
        _ensure_unique(self.forbidden_state_tokens, "forbidden_state_tokens")
        overlap = set(self.allowed_state_tokens) & set(self.forbidden_state_tokens)
        if overlap:
            raise DomainInvariantError(
                "allowed_state_tokens and forbidden_state_tokens must be disjoint."
            )
        if self.scope_ref.scope_kind != self.scope_kind:
            raise DomainInvariantError("scope_ref.scope_kind must match scope_kind.")


@dataclass(frozen=True, slots=True)
class MetadataPreservationPolicy:
    required_keys: tuple[MetadataKey, ...]
    immutable_keys: tuple[MetadataKey, ...]
    passthrough_keys: tuple[MetadataKey, ...]
    derivable_keys: tuple[MetadataKey, ...]
    missing_key_behavior: str
    unknown_key_behavior: str

    def __post_init__(self) -> None:
        object.__setattr__(
            self, "missing_key_behavior", _require_text(self.missing_key_behavior, "missing_key_behavior")
        )
        object.__setattr__(
            self, "unknown_key_behavior", _require_text(self.unknown_key_behavior, "unknown_key_behavior")
        )
        for field_name in (
            "required_keys",
            "immutable_keys",
            "passthrough_keys",
            "derivable_keys",
        ):
            _ensure_unique(getattr(self, field_name), field_name)

        immutable_not_required = set(self.immutable_keys) - set(self.required_keys)
        if immutable_not_required:
            raise DomainInvariantError("immutable_keys must be a subset of required_keys.")


@dataclass(frozen=True, slots=True)
class ChangeDescriptor:
    change_kind: ChangeKind
    path: str
    description: str

    def __post_init__(self) -> None:
        object.__setattr__(self, "path", _require_text(self.path, "path"))
        object.__setattr__(self, "description", _require_text(self.description, "description"))

    @property
    def is_breaking_by_default(self) -> bool:
        return self.change_kind.is_breaking_by_default
