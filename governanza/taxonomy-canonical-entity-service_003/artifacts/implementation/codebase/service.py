"""Core deterministic logic for motor_003.

This module governs canonical vocabulary terms, alias mappings, taxonomy tree
placement, and semantic boundaries. It deliberately rejects operational records,
normalization payloads, identity records, quality records, duplicate clusters,
and analytical decisions because those belong to other motors.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
import hashlib
import json
from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple


MOTOR_ID = "motor_003"
DEFAULT_EMITTED_AT = "1970-01-01T00:00:00Z"

ACTIVE = "active"
PRODUCED_BY = MOTOR_ID

ERROR_MISSING_PROVENANCE = "MISSING_PROVENANCE"
ERROR_ALIAS_COLLISION = "ALIAS_COLLISION"
ERROR_TAXONOMY_PARENT_NOT_FOUND = "TAXONOMY_PARENT_NOT_FOUND"
ERROR_TAXONOMY_CYCLE = "TAXONOMY_CYCLE"
ERROR_CANONICAL_TERM_DUPLICATE = "CANONICAL_TERM_DUPLICATE"
ERROR_CONTRACT_SCOPE_VIOLATION = "CONTRACT_SCOPE_VIOLATION"
ERROR_BOUNDARY_DEFINITION_MISSING = "BOUNDARY_DEFINITION_MISSING"

UNSUPPORTED_OBJECT_FAMILIES = frozenset(
    {
        "parsed_record",
        "normalized_record",
        "identity_record",
        "identity_resolution_record",
        "quality_record",
        "duplicate_cluster",
        "analytical_report",
        "join_decision",
    }
)


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _optional_string(value: Any) -> Optional[str]:
    if _is_non_empty_string(value):
        return value
    return None


def _normalized_label(value: str) -> str:
    return " ".join(value.split()).casefold()


def _as_mapping(value: Any) -> Optional[Mapping[str, Any]]:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return None


def _string_list(value: Any) -> List[str]:
    if not isinstance(value, list):
        return []
    return [item for item in value if _is_non_empty_string(item)]


def _stable_json(payload: Mapping[str, Any]) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(payload: Mapping[str, Any]) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, payload: Mapping[str, Any], length: int = 20) -> str:
    return f"{prefix}_{_digest(payload)[:length]}"


def _version_hash(payload: Mapping[str, Any]) -> str:
    return _digest(payload)


@dataclass(frozen=True)
class SourceVocabularyManifest:
    source_vocab_id: str
    source_name: str
    vocabulary_version: str
    terms_ref: str
    authority_note: str
    source_ref: str
    submitted_at: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "SourceVocabularyManifest":
        return cls(
            source_vocab_id=payload.get("source_vocab_id", ""),
            source_name=payload.get("source_name", ""),
            vocabulary_version=payload.get("vocabulary_version", ""),
            terms_ref=payload.get("terms_ref", ""),
            authority_note=payload.get("authority_note", ""),
            source_ref=payload.get("source_ref", ""),
            submitted_at=payload.get("submitted_at", ""),
        )


@dataclass(frozen=True)
class RawTermCandidate:
    candidate_id: str
    term_text: str
    source_vocab_id: str
    taxonomy_id: str
    scope: str
    parent_node_id: Optional[str]
    boundary_include_rules: List[str]
    boundary_exclude_rules: List[str]
    boundary_scope_note: str
    provenance_ref: str
    phase_contract_ref: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "RawTermCandidate":
        return cls(
            candidate_id=payload.get("candidate_id", ""),
            term_text=payload.get("term_text", ""),
            source_vocab_id=payload.get("source_vocab_id", ""),
            taxonomy_id=payload.get("taxonomy_id", ""),
            scope=payload.get("scope", ""),
            parent_node_id=_optional_string(payload.get("parent_node_id")),
            boundary_include_rules=_string_list(payload.get("boundary_include_rules")),
            boundary_exclude_rules=_string_list(payload.get("boundary_exclude_rules")),
            boundary_scope_note=payload.get("boundary_scope_note", ""),
            provenance_ref=payload.get("provenance_ref", ""),
            phase_contract_ref=payload.get("phase_contract_ref", ""),
        )


@dataclass(frozen=True)
class AliasCandidate:
    candidate_id: str
    alias_text: str
    target_canonical_id: Optional[str]
    target_term_text: Optional[str]
    source_vocab_id: str
    taxonomy_id: str
    scope: str
    provenance_ref: str
    phase_contract_ref: str

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AliasCandidate":
        return cls(
            candidate_id=payload.get("candidate_id", ""),
            alias_text=payload.get("alias_text", ""),
            target_canonical_id=_optional_string(payload.get("target_canonical_id")),
            target_term_text=_optional_string(payload.get("target_term_text")),
            source_vocab_id=payload.get("source_vocab_id", ""),
            taxonomy_id=payload.get("taxonomy_id", ""),
            scope=payload.get("scope", ""),
            provenance_ref=payload.get("provenance_ref", ""),
            phase_contract_ref=payload.get("phase_contract_ref", ""),
        )


@dataclass(frozen=True)
class BoundaryDefinition:
    record_id: str
    boundary_id: str
    canonical_id: str
    taxonomy_id: str
    scope: str
    include_rules: List[str]
    exclude_rules: List[str]
    scope_note: str
    authority_ref: str
    phase_contract_ref: str
    status: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class CanonicalEntity:
    record_id: str
    canonical_id: str
    canonical_label: str
    taxonomy_id: str
    scope: str
    status: str
    phase_contract_ref: str
    boundary_id: str
    provenance_refs: List[str]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaxonomyNode:
    record_id: str
    node_id: str
    taxonomy_id: str
    canonical_id: str
    parent_node_id: Optional[str]
    path: List[str]
    sort_order: int
    status: str
    phase_contract_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AliasMappings:
    record_id: str
    alias_id: str
    alias_text: str
    canonical_id: str
    taxonomy_id: str
    scope: str
    source_vocab_id: str
    provenance_ref: str
    status: str
    phase_contract_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaxonomyValidationError:
    record_id: str
    error_id: str
    error_code: str
    rejected_input_ref: str
    taxonomy_id: Optional[str]
    scope: Optional[str]
    field_path: str
    message: str
    blocking: bool
    phase_contract_ref: Optional[str]
    emitted_at: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: Optional[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TaxonomyPublicationResult:
    canonical_term: Optional[CanonicalEntity]
    alias_map: List[AliasMappings]
    taxonomy_tree: List[TaxonomyNode]
    boundary_definition: Optional[BoundaryDefinition]
    taxonomy_rejection: List[TaxonomyValidationError]

    @property
    def accepted(self) -> bool:
        return self.canonical_term is not None and not self.taxonomy_rejection

    def to_dict(self) -> Dict[str, Any]:
        return {
            "canonical_term": self.canonical_term.to_dict()
            if self.canonical_term
            else None,
            "alias_map": [alias.to_dict() for alias in self.alias_map],
            "taxonomy_tree": [node.to_dict() for node in self.taxonomy_tree],
            "boundary_definition": self.boundary_definition.to_dict()
            if self.boundary_definition
            else None,
            "taxonomy_rejection": [
                rejection.to_dict() for rejection in self.taxonomy_rejection
            ],
        }


class TaxonomyCanonicalEntityService:
    """Publishes governed taxonomy vocabulary records with deterministic checks."""

    def __init__(
        self,
        *,
        authorized_phase_contract_refs: Optional[Iterable[str]] = None,
        existing_canonical_terms: Optional[Iterable[CanonicalEntity]] = None,
        existing_aliases: Optional[Iterable[AliasMappings]] = None,
        existing_nodes: Optional[Iterable[TaxonomyNode]] = None,
        default_emitted_at: str = DEFAULT_EMITTED_AT,
    ) -> None:
        self.authorized_phase_contract_refs = (
            set(authorized_phase_contract_refs)
            if authorized_phase_contract_refs is not None
            else None
        )
        self.default_emitted_at = default_emitted_at
        self._canonical_by_key: Dict[Tuple[str, str, str], CanonicalEntity] = {}
        self._canonical_by_id: Dict[str, CanonicalEntity] = {}
        self._alias_by_key: Dict[Tuple[str, str, str], AliasMappings] = {}
        self._node_by_taxonomy_and_id: Dict[Tuple[str, str], TaxonomyNode] = {}

        for canonical in existing_canonical_terms or []:
            self.register_existing_canonical(canonical)
        for alias in existing_aliases or []:
            self.register_existing_alias(alias)
        for node in existing_nodes or []:
            self.register_existing_node(node)

    def register_existing_canonical(self, canonical: CanonicalEntity) -> None:
        if canonical.status != ACTIVE:
            return
        key = (
            canonical.taxonomy_id,
            canonical.scope,
            _normalized_label(canonical.canonical_label),
        )
        self._canonical_by_key[key] = canonical
        self._canonical_by_id[canonical.canonical_id] = canonical

    def register_existing_alias(self, alias: AliasMappings) -> None:
        if alias.status != ACTIVE:
            return
        key = (alias.taxonomy_id, alias.scope, _normalized_label(alias.alias_text))
        self._alias_by_key[key] = alias

    def register_existing_node(self, node: TaxonomyNode) -> None:
        if node.status != ACTIVE:
            return
        self._node_by_taxonomy_and_id[(node.taxonomy_id, node.node_id)] = node

    def publish(
        self,
        *,
        raw_terms: Sequence[Mapping[str, Any]],
        aliases: Sequence[Mapping[str, Any]],
        source_vocabularies: Sequence[Mapping[str, Any]],
        phase_contract_ref: str,
        emitted_at: Optional[str] = None,
        **unsupported_objects: Any,
    ) -> TaxonomyPublicationResult:
        emitted = emitted_at or self.default_emitted_at
        errors: List[TaxonomyValidationError] = []

        errors.extend(
            self._reject_unsupported_top_level_objects(unsupported_objects, emitted)
        )

        if not self._is_authorized_phase_contract(phase_contract_ref):
            errors.append(
                self._error(
                    error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                    rejected_input_ref="phase_contract_ref",
                    taxonomy_id=None,
                    scope=None,
                    field_path="phase_contract_ref",
                    message="phase_contract_ref must reference an authorized motor_001 taxonomy governance contract.",
                    phase_contract_ref=_optional_string(phase_contract_ref),
                    source_ref="phase_contract_ref",
                    emitted_at=emitted,
                )
            )

        raw_sequence = self._sequence_or_error(
            "raw_terms", raw_terms, phase_contract_ref, emitted, errors
        )
        alias_sequence = self._sequence_or_error(
            "aliases", aliases, phase_contract_ref, emitted, errors
        )
        manifest_sequence = self._sequence_or_error(
            "source_vocabularies",
            source_vocabularies,
            phase_contract_ref,
            emitted,
            errors,
        )

        if len(raw_sequence) != 1:
            errors.append(
                self._error(
                    error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                    rejected_input_ref="raw_terms",
                    taxonomy_id=None,
                    scope=None,
                    field_path="raw_terms",
                    message="A deterministic publication request must carry exactly one RawTermCandidate for the canonical_term output.",
                    phase_contract_ref=_optional_string(phase_contract_ref),
                    source_ref="raw_terms",
                    emitted_at=emitted,
                )
            )

        manifests = self._validate_source_vocabularies(
            manifest_sequence, phase_contract_ref, emitted, errors
        )
        raw_candidates = self._validate_raw_terms(
            raw_sequence, manifests, phase_contract_ref, emitted, errors
        )
        alias_candidates = self._validate_aliases(
            alias_sequence, manifests, phase_contract_ref, emitted, errors
        )

        if errors or not raw_candidates:
            return self._rejected(errors)

        raw_candidate = raw_candidates[0]
        manifest = manifests.get(raw_candidate.source_vocab_id)
        if manifest is None:
            errors.append(
                self._error(
                    error_code=ERROR_MISSING_PROVENANCE,
                    rejected_input_ref=raw_candidate.candidate_id,
                    taxonomy_id=raw_candidate.taxonomy_id,
                    scope=raw_candidate.scope,
                    field_path="raw_terms.source_vocab_id",
                    message="RawTermCandidate source_vocab_id must reference a submitted SourceVocabularyManifest.",
                    phase_contract_ref=raw_candidate.phase_contract_ref,
                    source_ref=raw_candidate.provenance_ref,
                    emitted_at=emitted,
                )
            )
            return self._rejected(errors)

        canonical_id = _stable_id(
            "canon",
            {
                "taxonomy_id": raw_candidate.taxonomy_id,
                "scope": raw_candidate.scope,
                "canonical_label": _normalized_label(raw_candidate.term_text),
            },
        )
        boundary = self._build_boundary(raw_candidate, manifest, canonical_id, emitted)
        canonical = self._build_canonical(
            raw_candidate, manifest, canonical_id, boundary.boundary_id, emitted
        )
        node_or_error = self._build_taxonomy_node(raw_candidate, canonical, emitted)
        if isinstance(node_or_error, TaxonomyValidationError):
            return self._rejected([node_or_error])
        node = node_or_error

        duplicate = self._canonical_by_key.get(
            (
                canonical.taxonomy_id,
                canonical.scope,
                _normalized_label(canonical.canonical_label),
            )
        )
        if duplicate:
            if (
                duplicate.canonical_id == canonical.canonical_id
                and duplicate.version_hash == canonical.version_hash
            ):
                return self._idempotent_result(
                    duplicate, alias_candidates, canonical.canonical_id, emitted
                )
            return self._rejected(
                [
                    self._error(
                        error_code=ERROR_CANONICAL_TERM_DUPLICATE,
                        rejected_input_ref=raw_candidate.candidate_id,
                        taxonomy_id=raw_candidate.taxonomy_id,
                        scope=raw_candidate.scope,
                        field_path="raw_terms.term_text",
                        message="An active canonical term already exists for this taxonomy_id, scope, and canonical label.",
                        phase_contract_ref=raw_candidate.phase_contract_ref,
                        source_ref=raw_candidate.provenance_ref,
                        emitted_at=emitted,
                    )
                ]
            )

        alias_mappings_or_errors = self._build_alias_mappings(
            alias_candidates, raw_candidate, canonical, emitted
        )
        alias_errors = [
            item for item in alias_mappings_or_errors if isinstance(item, TaxonomyValidationError)
        ]
        if alias_errors:
            return self._rejected(alias_errors)
        alias_mappings = [
            item for item in alias_mappings_or_errors if isinstance(item, AliasMappings)
        ]

        self.register_existing_canonical(canonical)
        self.register_existing_node(node)
        for alias in alias_mappings:
            self.register_existing_alias(alias)

        return TaxonomyPublicationResult(
            canonical_term=canonical,
            alias_map=alias_mappings,
            taxonomy_tree=[node],
            boundary_definition=boundary,
            taxonomy_rejection=[],
        )

    def _is_authorized_phase_contract(self, phase_contract_ref: Any) -> bool:
        if not _is_non_empty_string(phase_contract_ref):
            return False
        if self.authorized_phase_contract_refs is not None:
            return phase_contract_ref in self.authorized_phase_contract_refs
        return phase_contract_ref.startswith("motor_001:") and "taxonomy_governance" in phase_contract_ref

    def _reject_unsupported_top_level_objects(
        self, unsupported_objects: Mapping[str, Any], emitted_at: str
    ) -> List[TaxonomyValidationError]:
        errors: List[TaxonomyValidationError] = []
        for key in unsupported_objects:
            if key in UNSUPPORTED_OBJECT_FAMILIES:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=key,
                        taxonomy_id=None,
                        scope=None,
                        field_path=key,
                        message=f"{key} is outside motor_003 scope; this motor only governs vocabulary records.",
                        phase_contract_ref=None,
                        source_ref=key,
                        emitted_at=emitted_at,
                    )
                )
        return errors

    def _sequence_or_error(
        self,
        field_name: str,
        value: Any,
        phase_contract_ref: str,
        emitted_at: str,
        errors: List[TaxonomyValidationError],
    ) -> List[Mapping[str, Any]]:
        if isinstance(value, list):
            sequence = value
        else:
            errors.append(
                self._error(
                    error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                    rejected_input_ref=field_name,
                    taxonomy_id=None,
                    scope=None,
                    field_path=field_name,
                    message=f"{field_name} must be a list and is not coerced from other shapes.",
                    phase_contract_ref=_optional_string(phase_contract_ref),
                    source_ref=field_name,
                    emitted_at=emitted_at,
                )
            )
            return []

        mappings: List[Mapping[str, Any]] = []
        for index, item in enumerate(sequence):
            mapped = _as_mapping(item)
            if mapped is None:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=f"{field_name}[{index}]",
                        taxonomy_id=None,
                        scope=None,
                        field_path=f"{field_name}[{index}]",
                        message=f"{field_name}[{index}] must be an object with declared fields.",
                        phase_contract_ref=_optional_string(phase_contract_ref),
                        source_ref=f"{field_name}[{index}]",
                        emitted_at=emitted_at,
                    )
                )
            else:
                mappings.append(mapped)
        return mappings

    def _validate_source_vocabularies(
        self,
        manifest_payloads: Sequence[Mapping[str, Any]],
        phase_contract_ref: str,
        emitted_at: str,
        errors: List[TaxonomyValidationError],
    ) -> Dict[str, SourceVocabularyManifest]:
        manifests: Dict[str, SourceVocabularyManifest] = {}
        required_fields = (
            "source_vocab_id",
            "source_name",
            "vocabulary_version",
            "terms_ref",
            "authority_note",
            "source_ref",
            "submitted_at",
        )
        for payload in manifest_payloads:
            unsupported_field = self._unsupported_field(payload)
            rejected_ref = payload.get("source_vocab_id", "source_vocabulary")
            if unsupported_field:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=rejected_ref,
                        taxonomy_id=None,
                        scope=None,
                        field_path=f"source_vocabularies.{unsupported_field}",
                        message=f"{unsupported_field} is outside motor_003 input scope.",
                        phase_contract_ref=_optional_string(phase_contract_ref),
                        source_ref=payload.get("source_ref", rejected_ref),
                        emitted_at=emitted_at,
                    )
                )
                continue
            for field_name in required_fields:
                if not _is_non_empty_string(payload.get(field_name)):
                    errors.append(
                        self._error(
                            error_code=ERROR_MISSING_PROVENANCE,
                            rejected_input_ref=rejected_ref,
                            taxonomy_id=None,
                            scope=None,
                            field_path=f"source_vocabularies.{field_name}",
                            message=f"SourceVocabularyManifest requires non-empty {field_name}.",
                            phase_contract_ref=_optional_string(phase_contract_ref),
                            source_ref=payload.get("source_ref", rejected_ref),
                            emitted_at=emitted_at,
                        )
                    )
            if all(_is_non_empty_string(payload.get(field)) for field in required_fields):
                manifest = SourceVocabularyManifest.from_mapping(payload)
                manifests[manifest.source_vocab_id] = manifest
        return manifests

    def _validate_raw_terms(
        self,
        raw_payloads: Sequence[Mapping[str, Any]],
        manifests: Mapping[str, SourceVocabularyManifest],
        phase_contract_ref: str,
        emitted_at: str,
        errors: List[TaxonomyValidationError],
    ) -> List[RawTermCandidate]:
        candidates: List[RawTermCandidate] = []
        required_fields = (
            "candidate_id",
            "term_text",
            "source_vocab_id",
            "taxonomy_id",
            "scope",
            "provenance_ref",
            "phase_contract_ref",
        )
        for payload in raw_payloads:
            candidate_ref = payload.get("candidate_id", "raw_term")
            unsupported_field = self._unsupported_field(payload)
            if unsupported_field:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path=f"raw_terms.{unsupported_field}",
                        message=f"{unsupported_field} is outside motor_003 input scope.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
                continue
            for field_name in required_fields:
                if not _is_non_empty_string(payload.get(field_name)):
                    error_code = (
                        ERROR_MISSING_PROVENANCE
                        if field_name in {"source_vocab_id", "provenance_ref", "phase_contract_ref"}
                        else ERROR_CONTRACT_SCOPE_VIOLATION
                    )
                    errors.append(
                        self._error(
                            error_code=error_code,
                            rejected_input_ref=candidate_ref,
                            taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                            scope=_optional_string(payload.get("scope")),
                            field_path=f"raw_terms.{field_name}",
                            message=f"RawTermCandidate requires non-empty {field_name}.",
                            phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                            source_ref=payload.get("provenance_ref", candidate_ref),
                            emitted_at=emitted_at,
                        )
                    )
            if payload.get("phase_contract_ref") != phase_contract_ref:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="raw_terms.phase_contract_ref",
                        message="RawTermCandidate phase_contract_ref must match the request contract reference.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if not self._is_authorized_phase_contract(payload.get("phase_contract_ref")):
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="raw_terms.phase_contract_ref",
                        message="RawTermCandidate phase_contract_ref is not authorized for taxonomy governance.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if _is_non_empty_string(payload.get("source_vocab_id")) and payload.get("source_vocab_id") not in manifests:
                errors.append(
                    self._error(
                        error_code=ERROR_MISSING_PROVENANCE,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="raw_terms.source_vocab_id",
                        message="RawTermCandidate source_vocab_id must reference a submitted source vocabulary manifest.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if not self._has_boundary(payload):
                errors.append(
                    self._error(
                        error_code=ERROR_BOUNDARY_DEFINITION_MISSING,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="raw_terms.boundary",
                        message="Canonical publication requires at least one inclusion rule, exclusion rule, or explicit boundary scope note.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if not errors:
                candidates.append(RawTermCandidate.from_mapping(payload))
        return candidates

    def _validate_aliases(
        self,
        alias_payloads: Sequence[Mapping[str, Any]],
        manifests: Mapping[str, SourceVocabularyManifest],
        phase_contract_ref: str,
        emitted_at: str,
        errors: List[TaxonomyValidationError],
    ) -> List[AliasCandidate]:
        candidates: List[AliasCandidate] = []
        required_fields = (
            "candidate_id",
            "alias_text",
            "source_vocab_id",
            "taxonomy_id",
            "scope",
            "provenance_ref",
            "phase_contract_ref",
        )
        for payload in alias_payloads:
            candidate_ref = payload.get("candidate_id", "alias")
            unsupported_field = self._unsupported_field(payload)
            if unsupported_field:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path=f"aliases.{unsupported_field}",
                        message=f"{unsupported_field} is outside motor_003 input scope.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
                continue
            for field_name in required_fields:
                if not _is_non_empty_string(payload.get(field_name)):
                    error_code = (
                        ERROR_MISSING_PROVENANCE
                        if field_name in {"source_vocab_id", "provenance_ref", "phase_contract_ref"}
                        else ERROR_CONTRACT_SCOPE_VIOLATION
                    )
                    errors.append(
                        self._error(
                            error_code=error_code,
                            rejected_input_ref=candidate_ref,
                            taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                            scope=_optional_string(payload.get("scope")),
                            field_path=f"aliases.{field_name}",
                            message=f"AliasCandidate requires non-empty {field_name}.",
                            phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                            source_ref=payload.get("provenance_ref", candidate_ref),
                            emitted_at=emitted_at,
                        )
                    )
            if payload.get("phase_contract_ref") != phase_contract_ref:
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="aliases.phase_contract_ref",
                        message="AliasCandidate phase_contract_ref must match the request contract reference.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if not self._is_authorized_phase_contract(payload.get("phase_contract_ref")):
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="aliases.phase_contract_ref",
                        message="AliasCandidate phase_contract_ref is not authorized for taxonomy governance.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if _is_non_empty_string(payload.get("source_vocab_id")) and payload.get("source_vocab_id") not in manifests:
                errors.append(
                    self._error(
                        error_code=ERROR_MISSING_PROVENANCE,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="aliases.source_vocab_id",
                        message="AliasCandidate source_vocab_id must reference a submitted source vocabulary manifest.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if not _is_non_empty_string(payload.get("target_canonical_id")) and not _is_non_empty_string(payload.get("target_term_text")):
                errors.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=candidate_ref,
                        taxonomy_id=_optional_string(payload.get("taxonomy_id")),
                        scope=_optional_string(payload.get("scope")),
                        field_path="aliases.target",
                        message="AliasCandidate must target an existing canonical id or same-request term text.",
                        phase_contract_ref=_optional_string(payload.get("phase_contract_ref")),
                        source_ref=payload.get("provenance_ref", candidate_ref),
                        emitted_at=emitted_at,
                    )
                )
            if not errors:
                candidates.append(AliasCandidate.from_mapping(payload))
        return candidates

    def _build_boundary(
        self,
        raw_candidate: RawTermCandidate,
        manifest: SourceVocabularyManifest,
        canonical_id: str,
        emitted_at: str,
    ) -> BoundaryDefinition:
        boundary_id = _stable_id(
            "boundary",
            {
                "canonical_id": canonical_id,
                "taxonomy_id": raw_candidate.taxonomy_id,
                "scope": raw_candidate.scope,
                "include_rules": raw_candidate.boundary_include_rules,
                "exclude_rules": raw_candidate.boundary_exclude_rules,
                "scope_note": raw_candidate.boundary_scope_note,
            },
        )
        material = {
            "entity_type": "BoundaryDefinition",
            "boundary_id": boundary_id,
            "canonical_id": canonical_id,
            "taxonomy_id": raw_candidate.taxonomy_id,
            "scope": raw_candidate.scope,
            "include_rules": raw_candidate.boundary_include_rules,
            "exclude_rules": raw_candidate.boundary_exclude_rules,
            "scope_note": raw_candidate.boundary_scope_note,
            "authority_ref": manifest.authority_note,
            "phase_contract_ref": raw_candidate.phase_contract_ref,
            "status": ACTIVE,
            "source_ref": manifest.source_ref,
            "parent_id": None,
        }
        version_hash = _version_hash(material)
        return BoundaryDefinition(
            record_id=_stable_id("rec_boundary", material),
            boundary_id=boundary_id,
            canonical_id=canonical_id,
            taxonomy_id=raw_candidate.taxonomy_id,
            scope=raw_candidate.scope,
            include_rules=list(raw_candidate.boundary_include_rules),
            exclude_rules=list(raw_candidate.boundary_exclude_rules),
            scope_note=raw_candidate.boundary_scope_note,
            authority_ref=manifest.authority_note,
            phase_contract_ref=raw_candidate.phase_contract_ref,
            status=ACTIVE,
            version_id=_stable_id("ver_boundary", material),
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=manifest.source_ref,
            produced_by_motor=PRODUCED_BY,
            produced_at=emitted_at,
            parent_id=None,
        )

    def _build_canonical(
        self,
        raw_candidate: RawTermCandidate,
        manifest: SourceVocabularyManifest,
        canonical_id: str,
        boundary_id: str,
        emitted_at: str,
    ) -> CanonicalEntity:
        material = {
            "entity_type": "CanonicalEntity",
            "canonical_id": canonical_id,
            "canonical_label": raw_candidate.term_text,
            "taxonomy_id": raw_candidate.taxonomy_id,
            "scope": raw_candidate.scope,
            "status": ACTIVE,
            "phase_contract_ref": raw_candidate.phase_contract_ref,
            "boundary_id": boundary_id,
            "provenance_refs": [raw_candidate.provenance_ref],
            "source_ref": manifest.source_ref,
            "parent_id": None,
        }
        version_hash = _version_hash(material)
        return CanonicalEntity(
            record_id=_stable_id("rec_canonical", material),
            canonical_id=canonical_id,
            canonical_label=raw_candidate.term_text,
            taxonomy_id=raw_candidate.taxonomy_id,
            scope=raw_candidate.scope,
            status=ACTIVE,
            phase_contract_ref=raw_candidate.phase_contract_ref,
            boundary_id=boundary_id,
            provenance_refs=[raw_candidate.provenance_ref],
            version_id=_stable_id("ver_canonical", material),
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=manifest.source_ref,
            produced_by_motor=PRODUCED_BY,
            produced_at=emitted_at,
            parent_id=None,
        )

    def _build_taxonomy_node(
        self,
        raw_candidate: RawTermCandidate,
        canonical: CanonicalEntity,
        emitted_at: str,
    ) -> TaxonomyNode | TaxonomyValidationError:
        node_id = _stable_id(
            "node",
            {
                "taxonomy_id": canonical.taxonomy_id,
                "canonical_id": canonical.canonical_id,
                "scope": canonical.scope,
            },
        )
        parent_node: Optional[TaxonomyNode] = None
        if raw_candidate.parent_node_id:
            parent_node = self._node_by_taxonomy_and_id.get(
                (raw_candidate.taxonomy_id, raw_candidate.parent_node_id)
            )
            if parent_node is None:
                return self._error(
                    error_code=ERROR_TAXONOMY_PARENT_NOT_FOUND,
                    rejected_input_ref=raw_candidate.candidate_id,
                    taxonomy_id=raw_candidate.taxonomy_id,
                    scope=raw_candidate.scope,
                    field_path="raw_terms.parent_node_id",
                    message="parent_node_id must reference an active node in the same taxonomy.",
                    phase_contract_ref=raw_candidate.phase_contract_ref,
                    source_ref=raw_candidate.provenance_ref,
                    emitted_at=emitted_at,
                )
            if len(set(parent_node.path)) != len(parent_node.path) or node_id in parent_node.path:
                return self._error(
                    error_code=ERROR_TAXONOMY_CYCLE,
                    rejected_input_ref=raw_candidate.candidate_id,
                    taxonomy_id=raw_candidate.taxonomy_id,
                    scope=raw_candidate.scope,
                    field_path="taxonomy_tree.path",
                    message="The proposed parent path would introduce a repeated node.",
                    phase_contract_ref=raw_candidate.phase_contract_ref,
                    source_ref=raw_candidate.provenance_ref,
                    emitted_at=emitted_at,
                )
            path = list(parent_node.path) + [node_id]
        else:
            path = [node_id]

        sort_order_payload = {
            "taxonomy_id": canonical.taxonomy_id,
            "scope": canonical.scope,
            "canonical_label": _normalized_label(canonical.canonical_label),
        }
        material = {
            "entity_type": "TaxonomyNode",
            "node_id": node_id,
            "taxonomy_id": canonical.taxonomy_id,
            "canonical_id": canonical.canonical_id,
            "parent_node_id": raw_candidate.parent_node_id,
            "path": path,
            "sort_order": int(_digest(sort_order_payload)[:8], 16),
            "status": ACTIVE,
            "phase_contract_ref": canonical.phase_contract_ref,
            "source_ref": canonical.source_ref,
            "parent_id": None,
        }
        version_hash = _version_hash(material)
        return TaxonomyNode(
            record_id=_stable_id("rec_node", material),
            node_id=node_id,
            taxonomy_id=canonical.taxonomy_id,
            canonical_id=canonical.canonical_id,
            parent_node_id=raw_candidate.parent_node_id,
            path=path,
            sort_order=material["sort_order"],
            status=ACTIVE,
            phase_contract_ref=canonical.phase_contract_ref,
            version_id=_stable_id("ver_node", material),
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=canonical.source_ref,
            produced_by_motor=PRODUCED_BY,
            produced_at=emitted_at,
            parent_id=None,
        )

    def _build_alias_mappings(
        self,
        alias_candidates: Sequence[AliasCandidate],
        raw_candidate: RawTermCandidate,
        canonical: CanonicalEntity,
        emitted_at: str,
    ) -> List[AliasMappings | TaxonomyValidationError]:
        outputs: List[AliasMappings | TaxonomyValidationError] = []
        seen_request_aliases: Dict[Tuple[str, str, str], str] = {}
        for alias_candidate in alias_candidates:
            target_id = self._resolve_alias_target(alias_candidate, raw_candidate, canonical)
            if target_id is None:
                outputs.append(
                    self._error(
                        error_code=ERROR_CONTRACT_SCOPE_VIOLATION,
                        rejected_input_ref=alias_candidate.candidate_id,
                        taxonomy_id=alias_candidate.taxonomy_id,
                        scope=alias_candidate.scope,
                        field_path="aliases.target",
                        message="Alias target must be an active canonical id or the same-request term text.",
                        phase_contract_ref=alias_candidate.phase_contract_ref,
                        source_ref=alias_candidate.provenance_ref,
                        emitted_at=emitted_at,
                    )
                )
                continue
            alias_key = (
                alias_candidate.taxonomy_id,
                alias_candidate.scope,
                _normalized_label(alias_candidate.alias_text),
            )
            existing_alias = self._alias_by_key.get(alias_key)
            if existing_alias and existing_alias.canonical_id != target_id:
                outputs.append(
                    self._error(
                        error_code=ERROR_ALIAS_COLLISION,
                        rejected_input_ref=alias_candidate.candidate_id,
                        taxonomy_id=alias_candidate.taxonomy_id,
                        scope=alias_candidate.scope,
                        field_path="aliases.alias_text",
                        message="An active alias already targets a different canonical_id inside this taxonomy and scope.",
                        phase_contract_ref=alias_candidate.phase_contract_ref,
                        source_ref=alias_candidate.provenance_ref,
                        emitted_at=emitted_at,
                    )
                )
                continue
            request_target = seen_request_aliases.get(alias_key)
            if request_target and request_target != target_id:
                outputs.append(
                    self._error(
                        error_code=ERROR_ALIAS_COLLISION,
                        rejected_input_ref=alias_candidate.candidate_id,
                        taxonomy_id=alias_candidate.taxonomy_id,
                        scope=alias_candidate.scope,
                        field_path="aliases.alias_text",
                        message="The same alias text targets more than one canonical_id in this request.",
                        phase_contract_ref=alias_candidate.phase_contract_ref,
                        source_ref=alias_candidate.provenance_ref,
                        emitted_at=emitted_at,
                    )
                )
                continue
            seen_request_aliases[alias_key] = target_id
            if existing_alias and existing_alias.canonical_id == target_id:
                outputs.append(existing_alias)
                continue
            outputs.append(self._build_alias_mapping(alias_candidate, target_id, emitted_at))
        return outputs

    def _resolve_alias_target(
        self,
        alias_candidate: AliasCandidate,
        raw_candidate: RawTermCandidate,
        canonical: CanonicalEntity,
    ) -> Optional[str]:
        if alias_candidate.taxonomy_id != raw_candidate.taxonomy_id or alias_candidate.scope != raw_candidate.scope:
            existing = (
                self._canonical_by_id.get(alias_candidate.target_canonical_id)
                if alias_candidate.target_canonical_id
                else None
            )
            if existing and existing.taxonomy_id == alias_candidate.taxonomy_id and existing.scope == alias_candidate.scope:
                return existing.canonical_id
            return None
        if alias_candidate.target_canonical_id:
            if alias_candidate.target_canonical_id == canonical.canonical_id:
                return canonical.canonical_id
            existing = self._canonical_by_id.get(alias_candidate.target_canonical_id)
            if existing and existing.taxonomy_id == alias_candidate.taxonomy_id and existing.scope == alias_candidate.scope:
                return existing.canonical_id
            return None
        if alias_candidate.target_term_text and _normalized_label(alias_candidate.target_term_text) == _normalized_label(raw_candidate.term_text):
            return canonical.canonical_id
        return None

    def _build_alias_mapping(
        self, alias_candidate: AliasCandidate, canonical_id: str, emitted_at: str
    ) -> AliasMappings:
        material = {
            "entity_type": "AliasMappings",
            "alias_text": alias_candidate.alias_text,
            "canonical_id": canonical_id,
            "taxonomy_id": alias_candidate.taxonomy_id,
            "scope": alias_candidate.scope,
            "source_vocab_id": alias_candidate.source_vocab_id,
            "provenance_ref": alias_candidate.provenance_ref,
            "status": ACTIVE,
            "phase_contract_ref": alias_candidate.phase_contract_ref,
            "source_ref": alias_candidate.source_vocab_id,
            "parent_id": None,
        }
        alias_id = _stable_id(
            "alias",
            {
                "taxonomy_id": alias_candidate.taxonomy_id,
                "scope": alias_candidate.scope,
                "alias_text": _normalized_label(alias_candidate.alias_text),
                "canonical_id": canonical_id,
            },
        )
        material["alias_id"] = alias_id
        version_hash = _version_hash(material)
        return AliasMappings(
            record_id=_stable_id("rec_alias", material),
            alias_id=alias_id,
            alias_text=alias_candidate.alias_text,
            canonical_id=canonical_id,
            taxonomy_id=alias_candidate.taxonomy_id,
            scope=alias_candidate.scope,
            source_vocab_id=alias_candidate.source_vocab_id,
            provenance_ref=alias_candidate.provenance_ref,
            status=ACTIVE,
            phase_contract_ref=alias_candidate.phase_contract_ref,
            version_id=_stable_id("ver_alias", material),
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=alias_candidate.source_vocab_id,
            produced_by_motor=PRODUCED_BY,
            produced_at=emitted_at,
            parent_id=None,
        )

    def _idempotent_result(
        self,
        canonical: CanonicalEntity,
        alias_candidates: Sequence[AliasCandidate],
        canonical_id: str,
        emitted_at: str,
    ) -> TaxonomyPublicationResult:
        alias_outputs: List[AliasMappings] = []
        alias_errors: List[TaxonomyValidationError] = []
        for alias_candidate in alias_candidates:
            key = (
                alias_candidate.taxonomy_id,
                alias_candidate.scope,
                _normalized_label(alias_candidate.alias_text),
            )
            existing = self._alias_by_key.get(key)
            if existing and existing.canonical_id == canonical_id:
                alias_outputs.append(existing)
            elif existing and existing.canonical_id != canonical_id:
                alias_errors.append(
                    self._error(
                        error_code=ERROR_ALIAS_COLLISION,
                        rejected_input_ref=alias_candidate.candidate_id,
                        taxonomy_id=alias_candidate.taxonomy_id,
                        scope=alias_candidate.scope,
                        field_path="aliases.alias_text",
                        message="An active alias already targets a different canonical_id inside this taxonomy and scope.",
                        phase_contract_ref=alias_candidate.phase_contract_ref,
                        source_ref=alias_candidate.provenance_ref,
                        emitted_at=emitted_at,
                    )
                )
        if alias_errors:
            return self._rejected(alias_errors)
        return TaxonomyPublicationResult(
            canonical_term=canonical,
            alias_map=alias_outputs,
            taxonomy_tree=[
                node
                for node in self._node_by_taxonomy_and_id.values()
                if node.canonical_id == canonical.canonical_id and node.taxonomy_id == canonical.taxonomy_id
            ],
            boundary_definition=None,
            taxonomy_rejection=[],
        )

    def _has_boundary(self, payload: Mapping[str, Any]) -> bool:
        return bool(
            _string_list(payload.get("boundary_include_rules"))
            or _string_list(payload.get("boundary_exclude_rules"))
            or _is_non_empty_string(payload.get("boundary_scope_note"))
        )

    def _unsupported_field(self, payload: Mapping[str, Any]) -> Optional[str]:
        for field_name in payload:
            if field_name in UNSUPPORTED_OBJECT_FAMILIES:
                return field_name
        return None

    def _error(
        self,
        *,
        error_code: str,
        rejected_input_ref: str,
        taxonomy_id: Optional[str],
        scope: Optional[str],
        field_path: str,
        message: str,
        phase_contract_ref: Optional[str],
        source_ref: str,
        emitted_at: str,
    ) -> TaxonomyValidationError:
        material = {
            "entity_type": "TaxonomyValidationError",
            "error_code": error_code,
            "rejected_input_ref": rejected_input_ref,
            "taxonomy_id": taxonomy_id,
            "scope": scope,
            "field_path": field_path,
            "message": message,
            "blocking": True,
            "phase_contract_ref": phase_contract_ref,
            "source_ref": source_ref,
            "parent_id": None,
        }
        version_hash = _version_hash(material)
        error_id = _stable_id("err", material)
        return TaxonomyValidationError(
            record_id=_stable_id("rec_error", material),
            error_id=error_id,
            error_code=error_code,
            rejected_input_ref=rejected_input_ref,
            taxonomy_id=taxonomy_id,
            scope=scope,
            field_path=field_path,
            message=message,
            blocking=True,
            phase_contract_ref=phase_contract_ref,
            emitted_at=emitted_at,
            version_id=_stable_id("ver_error", material),
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=PRODUCED_BY,
            produced_at=emitted_at,
            parent_id=None,
        )

    def _rejected(
        self, errors: Sequence[TaxonomyValidationError]
    ) -> TaxonomyPublicationResult:
        return TaxonomyPublicationResult(
            canonical_term=None,
            alias_map=[],
            taxonomy_tree=[],
            boundary_definition=None,
            taxonomy_rejection=list(errors),
        )
