from __future__ import annotations

from datetime import datetime

from .._compat import dataclass
from .enums import ContractStatus, PhaseId, ScopeKind
from .errors import DomainInvariantError
from .value_objects import (
    EntityId,
    EpistemicPolicyFragment,
    MetadataKey,
    MetadataPreservationPolicy,
    ScopedContractRef,
    ContractVersion,
    _ensure_unique,
    _require_text,
    _require_timezone,
)


def _normalize_name_tuple(values: tuple[str, ...], field_name: str) -> tuple[str, ...]:
    normalized = tuple(_require_text(value, field_name) for value in values)
    _ensure_unique(normalized, field_name)
    return normalized


@dataclass(frozen=True, slots=True)
class PhaseContract:
    phase_contract_id: EntityId
    phase_id: PhaseId
    contract_version: ContractVersion
    contract_status: ContractStatus
    canonical_name: str
    source_of_authority_ref: str
    allowed_output_names: tuple[str, ...]
    forbidden_output_names: tuple[str, ...]
    required_metadata_keys: tuple[MetadataKey, ...]
    epistemic_policy_fragments: tuple[EpistemicPolicyFragment, ...]
    object_contract_ids: tuple[EntityId, ...]
    transition_contract_ids: tuple[EntityId, ...]
    supersedes_contract_id: EntityId | None
    created_at: datetime
    published_at: datetime | None
    checksum: str

    @property
    def reference(self) -> ScopedContractRef:
        return ScopedContractRef(
            scope_kind=ScopeKind.PHASE_CONTRACT,
            identifier=self.phase_contract_id,
            version=self.contract_version,
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "canonical_name", _require_text(self.canonical_name, "canonical_name"))
        object.__setattr__(
            self,
            "source_of_authority_ref",
            _require_text(self.source_of_authority_ref, "source_of_authority_ref"),
        )
        object.__setattr__(self, "checksum", _require_text(self.checksum, "checksum"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        if self.published_at is not None:
            object.__setattr__(self, "published_at", _require_timezone(self.published_at, "published_at"))

        object.__setattr__(
            self, "allowed_output_names", _normalize_name_tuple(self.allowed_output_names, "allowed_output_names")
        )
        object.__setattr__(
            self,
            "forbidden_output_names",
            _normalize_name_tuple(self.forbidden_output_names, "forbidden_output_names"),
        )
        overlap = set(self.allowed_output_names) & set(self.forbidden_output_names)
        if overlap:
            raise DomainInvariantError("allowed_output_names and forbidden_output_names must be disjoint.")

        _ensure_unique(self.required_metadata_keys, "required_metadata_keys")
        _ensure_unique(self.object_contract_ids, "object_contract_ids")
        _ensure_unique(self.transition_contract_ids, "transition_contract_ids")

        if not self.object_contract_ids:
            raise DomainInvariantError("PhaseContract must reference at least one object_contract_id.")
        if not self.epistemic_policy_fragments:
            raise DomainInvariantError(
                "PhaseContract must declare at least one epistemic_policy_fragment."
            )
        if self.contract_status.is_published_lineage and self.published_at is None:
            raise DomainInvariantError("published lineage contracts require published_at.")
        if not self.contract_status.is_published_lineage and self.published_at is not None:
            raise DomainInvariantError("draft or staged contracts must not define published_at.")

        for fragment in self.epistemic_policy_fragments:
            if fragment.scope_kind != ScopeKind.PHASE_CONTRACT:
                raise DomainInvariantError(
                    "PhaseContract epistemic_policy_fragments must have scope_kind=phase_contract."
                )
            if fragment.scope_ref != self.reference:
                raise DomainInvariantError(
                    "PhaseContract epistemic_policy_fragments must reference the owning phase contract."
                )


@dataclass(frozen=True, slots=True)
class ObjectContract:
    object_contract_id: EntityId
    phase_contract_id: EntityId
    object_name: str
    object_role: str
    canonical_purpose: str
    required_fields: tuple[str, ...]
    optional_fields: tuple[str, ...]
    forbidden_fields: tuple[str, ...]
    required_metadata_keys: tuple[MetadataKey, ...]
    metadata_preservation_policy: MetadataPreservationPolicy
    allowed_epistemic_state_tokens: tuple[str, ...]
    forbidden_epistemic_state_tokens: tuple[str, ...]
    created_at: datetime
    checksum: str

    @property
    def reference(self) -> ScopedContractRef:
        return ScopedContractRef(
            scope_kind=ScopeKind.OBJECT_CONTRACT,
            identifier=self.object_contract_id,
            version=None,
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "object_name", _require_text(self.object_name, "object_name"))
        object.__setattr__(self, "object_role", _require_text(self.object_role, "object_role"))
        object.__setattr__(
            self, "canonical_purpose", _require_text(self.canonical_purpose, "canonical_purpose")
        )
        object.__setattr__(self, "checksum", _require_text(self.checksum, "checksum"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))
        object.__setattr__(self, "required_fields", _normalize_name_tuple(self.required_fields, "required_fields"))
        object.__setattr__(self, "optional_fields", _normalize_name_tuple(self.optional_fields, "optional_fields"))
        object.__setattr__(
            self, "forbidden_fields", _normalize_name_tuple(self.forbidden_fields, "forbidden_fields")
        )
        object.__setattr__(
            self,
            "allowed_epistemic_state_tokens",
            _normalize_name_tuple(self.allowed_epistemic_state_tokens, "allowed_epistemic_state_tokens"),
        )
        object.__setattr__(
            self,
            "forbidden_epistemic_state_tokens",
            _normalize_name_tuple(self.forbidden_epistemic_state_tokens, "forbidden_epistemic_state_tokens"),
        )
        _ensure_unique(self.required_metadata_keys, "required_metadata_keys")

        field_overlap = (
            set(self.required_fields) & set(self.optional_fields)
            or set(self.required_fields) & set(self.forbidden_fields)
            or set(self.optional_fields) & set(self.forbidden_fields)
        )
        if field_overlap:
            raise DomainInvariantError("required_fields, optional_fields and forbidden_fields must be disjoint.")

        token_overlap = set(self.allowed_epistemic_state_tokens) & set(self.forbidden_epistemic_state_tokens)
        if token_overlap:
            raise DomainInvariantError(
                "allowed_epistemic_state_tokens and forbidden_epistemic_state_tokens must be disjoint."
            )

        if self.required_metadata_keys:
            if not self.metadata_preservation_policy.required_keys:
                raise DomainInvariantError(
                    "metadata_preservation_policy.required_keys cannot be empty when required_metadata_keys exist."
                )
            missing = set(self.required_metadata_keys) - set(self.metadata_preservation_policy.required_keys)
            if missing:
                raise DomainInvariantError(
                    "metadata_preservation_policy.required_keys must include required_metadata_keys."
                )


@dataclass(frozen=True, slots=True)
class TransitionContract:
    transition_contract_id: EntityId
    source_phase_contract_id: EntityId
    target_phase_contract_id: EntityId
    transition_name: str
    source_object_refs: tuple[ScopedContractRef, ...]
    target_object_refs: tuple[ScopedContractRef, ...]
    required_preconditions: tuple[str, ...]
    required_metadata_keys: tuple[MetadataKey, ...]
    prohibited_transforms: tuple[str, ...]
    allowed_status_transforms: tuple[str, ...]
    blocked_status_transforms: tuple[str, ...]
    epistemic_policy_fragments: tuple[EpistemicPolicyFragment, ...]
    created_at: datetime
    checksum: str

    @property
    def reference(self) -> ScopedContractRef:
        return ScopedContractRef(
            scope_kind=ScopeKind.TRANSITION_CONTRACT,
            identifier=self.transition_contract_id,
            version=None,
        )

    def __post_init__(self) -> None:
        object.__setattr__(self, "transition_name", _require_text(self.transition_name, "transition_name"))
        object.__setattr__(self, "checksum", _require_text(self.checksum, "checksum"))
        object.__setattr__(self, "created_at", _require_timezone(self.created_at, "created_at"))

        if not self.source_object_refs:
            raise DomainInvariantError("source_object_refs must not be empty.")
        if not self.target_object_refs:
            raise DomainInvariantError("target_object_refs must not be empty.")
        _ensure_unique(self.source_object_refs, "source_object_refs")
        _ensure_unique(self.target_object_refs, "target_object_refs")

        object.__setattr__(
            self,
            "required_preconditions",
            tuple(_require_text(value, "required_precondition") for value in self.required_preconditions),
        )
        object.__setattr__(
            self,
            "prohibited_transforms",
            _normalize_name_tuple(self.prohibited_transforms, "prohibited_transforms"),
        )
        object.__setattr__(
            self,
            "allowed_status_transforms",
            _normalize_name_tuple(self.allowed_status_transforms, "allowed_status_transforms"),
        )
        object.__setattr__(
            self,
            "blocked_status_transforms",
            _normalize_name_tuple(self.blocked_status_transforms, "blocked_status_transforms"),
        )
        _ensure_unique(self.required_metadata_keys, "required_metadata_keys")

        transform_overlap = set(self.allowed_status_transforms) & set(self.blocked_status_transforms)
        if transform_overlap:
            raise DomainInvariantError(
                "allowed_status_transforms and blocked_status_transforms must be disjoint."
            )

        for ref in (*self.source_object_refs, *self.target_object_refs):
            if ref.scope_kind != ScopeKind.OBJECT_CONTRACT:
                raise DomainInvariantError("source_object_refs and target_object_refs must reference object_contract.")

        for fragment in self.epistemic_policy_fragments:
            if fragment.scope_kind != ScopeKind.TRANSITION_CONTRACT:
                raise DomainInvariantError(
                    "TransitionContract epistemic_policy_fragments must have scope_kind=transition_contract."
                )
            if fragment.scope_ref != self.reference:
                raise DomainInvariantError(
                    "TransitionContract epistemic_policy_fragments must reference the owning transition contract."
                )
