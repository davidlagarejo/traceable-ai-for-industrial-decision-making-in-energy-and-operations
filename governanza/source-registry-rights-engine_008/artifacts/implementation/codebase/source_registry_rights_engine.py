"""Deterministic Source Registry + Rights Engine for motor_008.

The engine registers source metadata, documented rights, access class, and
refresh discipline. It deliberately avoids ingestion, payload parsing, source
quality evaluation, identity resolution, inference, and reporting behavior.
"""

from __future__ import annotations

from calendar import monthrange
from dataclasses import asdict, dataclass
from datetime import date, datetime, timedelta
import hashlib
import json
from typing import Any, Iterable, Mapping, Sequence


MOTOR_ID = "motor_008"
DEFAULT_EMITTED_AT = "1970-01-01T00:00:00Z"

RIGHTS_STATUSES = {
    "allowed",
    "allowed_with_attribution",
    "restricted",
    "blocked",
    "expired",
    "conflict",
}
ACCESS_CLASS_VALUES = {"public", "premium", "restricted", "contractual", "internal", "blocked"}
REGISTRATION_STATUSES = {"active", "restricted", "blocked", "retired"}
PERIODICITIES = {"daily", "weekly", "monthly", "quarterly", "annual", "event_driven", "manual_review"}
VALIDATION_ERROR_CODES = {
    "MISSING_SOURCE_ID",
    "MISSING_SOURCE_LOCATOR",
    "MISSING_OWNER",
    "MISSING_DECLARED_USE",
    "MISSING_RIGHTS_EVIDENCE",
    "UNTRACEABLE_DOCUMENT_REF",
    "INVALID_LICENSE_DATES",
    "EXPIRED_ACCESS_AGREEMENT",
    "RIGHTS_CONFLICT",
    "INVALID_ACCESS_CLASS",
    "MISSING_REFRESH_DISCIPLINE",
    "CONTRACT_SCOPE_VIOLATION",
}

FORBIDDEN_INPUT_FIELDS = {
    "raw_payload",
    "payload",
    "payload_records",
    "records",
    "rows",
    "data_rows",
    "parsed_records",
    "normalized_records",
    "quality_score",
    "quality_scores",
    "identity_matches",
    "identity_resolution",
    "inference_records",
    "output_blocks",
    "report_blocks",
    "raw_content",
    "source_content",
}

SUBSCRIPTION_TERMS = ("subscription", "paid", "paywalled", "licensed seat")
CONTRACT_TERMS = ("contract", "agreement", "vendor", "credential approval", "authorization")
INTERNAL_TERMS = ("internal", "private")


def _as_mapping(value: Any) -> Mapping[str, Any] | None:
    if isinstance(value, Mapping):
        return value
    if hasattr(value, "__dataclass_fields__"):
        return asdict(value)
    return None


def _is_non_empty_string(value: Any) -> bool:
    return isinstance(value, str) and value.strip() != ""


def _optional_string(value: Any) -> str | None:
    if value is None:
        return None
    if _is_non_empty_string(value):
        return value
    return None


def _string_list(value: Any) -> list[str] | None:
    if not isinstance(value, list):
        return None
    result: list[str] = []
    for item in value:
        if not _is_non_empty_string(item):
            return None
        result.append(item)
    return result


def _dedupe(items: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    result: list[str] = []
    for item in items:
        if item not in seen:
            seen.add(item)
            result.append(item)
    return result


def _stable_json(payload: Any) -> str:
    return json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def _digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _stable_id(prefix: str, payload: Any, length: int = 20) -> str:
    return f"{prefix}_{_digest(payload)[:length]}"


def _parse_datetime(value: Any) -> datetime | None:
    if not _is_non_empty_string(value):
        return None
    normalized = value.strip()
    if normalized.endswith("Z"):
        normalized = normalized[:-1] + "+00:00"
    try:
        return datetime.fromisoformat(normalized)
    except ValueError:
        return None


def _parse_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, date) and not isinstance(value, datetime):
        return value
    if isinstance(value, datetime):
        return value.date()
    if not _is_non_empty_string(value):
        return None
    try:
        return date.fromisoformat(value.strip())
    except ValueError:
        return None


def _date_to_str(value: date | None) -> str | None:
    return value.isoformat() if value is not None else None


def _max_datetime(values: Iterable[str | None]) -> str:
    parsed = [_parse_datetime(value) for value in values if value is not None]
    usable = [value for value in parsed if value is not None]
    if not usable:
        return DEFAULT_EMITTED_AT
    latest = max(usable)
    if latest.tzinfo is not None:
        return latest.isoformat().replace("+00:00", "Z")
    return latest.isoformat()


def _add_months(value: date, months: int) -> date:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    day = min(value.day, monthrange(year, month)[1])
    return date(year, month, day)


def _next_review_date(anchor: date, periodicity: str) -> date | None:
    if periodicity == "daily":
        return anchor + timedelta(days=1)
    if periodicity == "weekly":
        return anchor + timedelta(days=7)
    if periodicity == "monthly":
        return _add_months(anchor, 1)
    if periodicity == "quarterly":
        return _add_months(anchor, 3)
    if periodicity == "annual":
        return _add_months(anchor, 12)
    return None


def _lower_text(*values: str | None) -> str:
    return " ".join(value for value in values if value).casefold()


@dataclass(frozen=True)
class SourceDeclaration:
    source_id: Any
    source_name: Any
    source_locator: Any
    source_type: Any
    declared_owner: Any
    declared_use: Any
    declared_refresh: Any
    declaration_ref: Any
    submitted_by: Any
    submitted_at: Any

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "SourceDeclaration":
        return cls(
            source_id=payload.get("source_id"),
            source_name=payload.get("source_name"),
            source_locator=payload.get("source_locator"),
            source_type=payload.get("source_type"),
            declared_owner=payload.get("declared_owner"),
            declared_use=payload.get("declared_use"),
            declared_refresh=payload.get("declared_refresh"),
            declaration_ref=payload.get("declaration_ref"),
            submitted_by=payload.get("submitted_by"),
            submitted_at=payload.get("submitted_at"),
        )


@dataclass(frozen=True)
class LicenseDocumentRef:
    license_ref_id: Any
    source_id: Any
    document_ref: Any
    license_basis: Any
    permitted_uses: Any
    prohibited_uses: Any
    restriction_notes: Any
    attribution_requirements: Any
    effective_from: Any
    effective_to: Any
    observed_at: Any

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "LicenseDocumentRef":
        return cls(
            license_ref_id=payload.get("license_ref_id"),
            source_id=payload.get("source_id"),
            document_ref=payload.get("document_ref"),
            license_basis=payload.get("license_basis"),
            permitted_uses=payload.get("permitted_uses"),
            prohibited_uses=payload.get("prohibited_uses"),
            restriction_notes=payload.get("restriction_notes"),
            attribution_requirements=payload.get("attribution_requirements"),
            effective_from=payload.get("effective_from"),
            effective_to=payload.get("effective_to"),
            observed_at=payload.get("observed_at"),
        )


@dataclass(frozen=True)
class AccessAgreementRef:
    agreement_ref_id: Any
    source_id: Any
    document_ref: Any
    access_basis: Any
    authentication_required: Any
    payment_required: Any
    quota_notes: Any
    embargo_until: Any
    territorial_restrictions: Any
    permitted_uses: Any
    prohibited_uses: Any
    effective_from: Any
    effective_to: Any
    observed_at: Any

    @classmethod
    def from_mapping(cls, payload: Mapping[str, Any]) -> "AccessAgreementRef":
        return cls(
            agreement_ref_id=payload.get("agreement_ref_id"),
            source_id=payload.get("source_id"),
            document_ref=payload.get("document_ref"),
            access_basis=payload.get("access_basis"),
            authentication_required=payload.get("authentication_required"),
            payment_required=payload.get("payment_required"),
            quota_notes=payload.get("quota_notes"),
            embargo_until=payload.get("embargo_until"),
            territorial_restrictions=payload.get("territorial_restrictions"),
            permitted_uses=payload.get("permitted_uses"),
            prohibited_uses=payload.get("prohibited_uses"),
            effective_from=payload.get("effective_from"),
            effective_to=payload.get("effective_to"),
            observed_at=payload.get("observed_at"),
        )


@dataclass(frozen=True)
class SourceRecord:
    record_id: str
    source_id: str
    source_name: str
    source_locator: str
    source_type: str
    declared_owner: str
    declared_use: str
    declared_refresh: str | None
    registration_status: str
    registration_reason: str
    declaration_ref: str
    evidence_refs: list[str]
    rights_profile_id: str
    access_class_id: str
    refresh_schedule_id: str
    phase_contract_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RightsProfile:
    record_id: str
    rights_profile_id: str
    source_id: str
    license_basis: str
    license_document_refs: list[str]
    agreement_refs: list[str]
    permitted_uses: list[str]
    prohibited_uses: list[str]
    restriction_notes: str
    attribution_requirements: list[str]
    rights_status: str
    effective_from: str | None
    effective_to: str | None
    evidence_observed_at: str
    phase_contract_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AccessClass:
    record_id: str
    access_class_id: str
    source_id: str
    rights_profile_id: str
    access_class: str
    assignment_reason: str
    supporting_document_refs: list[str]
    authentication_required: bool
    payment_required: bool
    quota_notes: str | None
    embargo_until: str | None
    territorial_restrictions: list[str]
    effective_from: str | None
    effective_to: str | None
    phase_contract_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RefreshSchedule:
    record_id: str
    refresh_schedule_id: str
    source_id: str
    periodicity: str
    next_review_at: str | None
    manual_review_condition: str | None
    refresh_reason: str
    schedule_basis_refs: list[str]
    phase_contract_ref: str
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceRightsValidationError:
    record_id: str
    error_id: str
    error_code: str
    source_id: str | None
    rejected_input_ref: str
    field_path: str
    message: str
    blocking: bool
    detected_at: str
    phase_contract_ref: str | None
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class SourceRegistryRightsResult:
    source_registration: SourceRecord | None
    rights_profile: RightsProfile | None
    access_class: AccessClass | None
    refresh_schedule: RefreshSchedule | None
    validation_errors: list[SourceRightsValidationError]

    @property
    def status(self) -> str:
        if self.validation_errors and self.source_registration is None:
            return "rejected"
        if self.validation_errors:
            return "accepted_with_warnings"
        return "accepted"

    def to_dict(self) -> dict[str, Any]:
        return {
            "status": self.status,
            "source_registration": (
                self.source_registration.to_dict()
                if self.source_registration is not None
                else None
            ),
            "rights_profile": self.rights_profile.to_dict() if self.rights_profile else None,
            "access_class": self.access_class.to_dict() if self.access_class else None,
            "refresh_schedule": self.refresh_schedule.to_dict() if self.refresh_schedule else None,
            "validation_errors": [error.to_dict() for error in self.validation_errors],
        }


class SourceRegistryRightsEngine:
    """Register source rights metadata with deterministic validations."""

    def __init__(
        self,
        known_phase_contract_refs: Iterable[str] | None = None,
        current_records: Iterable[SourceRegistryRightsResult | Mapping[str, Any]] | None = None,
    ) -> None:
        self.known_phase_contract_refs = set(known_phase_contract_refs or ())
        self._current_by_source_id: dict[str, SourceRegistryRightsResult] = {}
        for record in current_records or ():
            self.seed_current_record(record)

    def process(
        self,
        source_declarations: Sequence[Mapping[str, Any]],
        license_files: Sequence[Mapping[str, Any]] | None,
        access_agreements: Sequence[Mapping[str, Any]] | None,
        phase_contract_ref: str | None,
        emitted_at: str = DEFAULT_EMITTED_AT,
        as_of_date: str | date | None = None,
        parent_ids: Mapping[str, str | None] | None = None,
    ) -> SourceRegistryRightsResult | list[SourceRegistryRightsResult]:
        return self.register(
            source_declarations=source_declarations,
            license_files=license_files,
            access_agreements=access_agreements,
            phase_contract_ref=phase_contract_ref,
            emitted_at=emitted_at,
            as_of_date=as_of_date,
            parent_ids=parent_ids,
        )

    def register(
        self,
        source_declarations: Sequence[Mapping[str, Any]],
        license_files: Sequence[Mapping[str, Any]] | None,
        access_agreements: Sequence[Mapping[str, Any]] | None,
        phase_contract_ref: str | None,
        emitted_at: str = DEFAULT_EMITTED_AT,
        as_of_date: str | date | None = None,
        parent_ids: Mapping[str, str | None] | None = None,
    ) -> SourceRegistryRightsResult | list[SourceRegistryRightsResult]:
        """Validate declarations and emit governed source rights outputs.

        Inputs are source declarations plus license and access references. The
        method returns one result per source declaration, preserving the exact
        output families declared by the motor contract.
        """

        licenses = self._coerce_licenses(license_files or ())
        agreements = self._coerce_agreements(access_agreements or ())
        reference_date = self._reference_date(
            source_declarations=source_declarations,
            licenses=licenses,
            agreements=agreements,
            emitted_at=emitted_at,
            as_of_date=as_of_date,
        )

        if not isinstance(source_declarations, Sequence) or isinstance(source_declarations, (str, bytes)):
            error = self._error(
                error_code="CONTRACT_SCOPE_VIOLATION",
                source_id=None,
                rejected_input_ref="source_declarations",
                field_path="source_declarations",
                message="source_declarations must be a sequence of declaration mappings.",
                blocking=True,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
            return SourceRegistryRightsResult(None, None, None, None, [error])

        results: list[SourceRegistryRightsResult] = []
        for index, raw_declaration in enumerate(source_declarations):
            results.append(
                self._register_one(
                    raw_declaration=raw_declaration,
                    declaration_index=index,
                    declaration_count=len(source_declarations),
                    licenses=licenses,
                    agreements=agreements,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                    reference_date=reference_date,
                    parent_ids=parent_ids or {},
                )
            )

        if len(results) == 1:
            return results[0]
        return results

    def seed_current_record(
        self, record: SourceRegistryRightsResult | Mapping[str, Any]
    ) -> SourceRegistryRightsResult:
        result = record if isinstance(record, SourceRegistryRightsResult) else self._result_from_mapping(record)
        if result.source_registration is None:
            return result
        existing = self._current_by_source_id.get(result.source_registration.source_id)
        if existing is not None and existing.to_dict() != result.to_dict():
            raise ValueError("Current source registration already exists with different content.")
        self._current_by_source_id[result.source_registration.source_id] = result
        return result

    def _register_one(
        self,
        raw_declaration: Mapping[str, Any],
        declaration_index: int,
        declaration_count: int,
        licenses: Sequence[tuple[LicenseDocumentRef | None, Mapping[str, Any] | None]],
        agreements: Sequence[tuple[AccessAgreementRef | None, Mapping[str, Any] | None]],
        phase_contract_ref: str | None,
        emitted_at: str,
        reference_date: date,
        parent_ids: Mapping[str, str | None],
    ) -> SourceRegistryRightsResult:
        raw_mapping = _as_mapping(raw_declaration)
        if raw_mapping is None:
            error = self._error(
                error_code="CONTRACT_SCOPE_VIOLATION",
                source_id=None,
                rejected_input_ref=f"source_declarations[{declaration_index}]",
                field_path=f"source_declarations[{declaration_index}]",
                message="Each SourceDeclaration must be a mapping.",
                blocking=True,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
            return SourceRegistryRightsResult(None, None, None, None, [error])

        declaration = SourceDeclaration.from_mapping(raw_mapping)
        source_id = declaration.source_id if _is_non_empty_string(declaration.source_id) else None
        declaration_ref = (
            declaration.declaration_ref
            if _is_non_empty_string(declaration.declaration_ref)
            else f"source_declarations[{declaration_index}]"
        )

        errors: list[SourceRightsValidationError] = []
        errors.extend(
            self._validate_phase_contract(
                phase_contract_ref=phase_contract_ref,
                source_id=source_id,
                declaration_ref=declaration_ref,
                emitted_at=emitted_at,
            )
        )
        errors.extend(
            self._validate_forbidden_fields(
                payload=raw_mapping,
                source_id=source_id,
                rejected_input_ref=declaration_ref,
                field_prefix=f"source_declarations[{declaration_index}]",
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )
        errors.extend(
            self._validate_declaration(
                declaration=declaration,
                declaration_index=declaration_index,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )

        related_licenses = self._related_licenses(source_id, declaration_count, licenses)
        related_agreements = self._related_agreements(source_id, declaration_count, agreements)

        if not related_licenses and not related_agreements:
            errors.append(
                self._error(
                    error_code="MISSING_RIGHTS_EVIDENCE",
                    source_id=source_id,
                    rejected_input_ref=declaration_ref,
                    field_path="license_files|access_agreements",
                    message="At least one traceable license file or access agreement is required.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        for license_index, license_ref, raw_license in related_licenses:
            if raw_license is not None:
                errors.extend(
                    self._validate_forbidden_fields(
                        payload=raw_license,
                        source_id=source_id,
                        rejected_input_ref=self._license_rejected_ref(license_ref, license_index),
                        field_prefix=f"license_files[{license_index}]",
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )
            if license_ref is None:
                errors.append(
                    self._error(
                        error_code="CONTRACT_SCOPE_VIOLATION",
                        source_id=source_id,
                        rejected_input_ref=f"license_files[{license_index}]",
                        field_path=f"license_files[{license_index}]",
                        message="LicenseDocumentRef must be a mapping.",
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )
                continue
            errors.extend(
                self._validate_license(
                    license_ref=license_ref,
                    license_index=license_index,
                    expected_source_id=source_id,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                    reference_date=reference_date,
                )
            )

        for agreement_index, agreement_ref, raw_agreement in related_agreements:
            if raw_agreement is not None:
                errors.extend(
                    self._validate_forbidden_fields(
                        payload=raw_agreement,
                        source_id=source_id,
                        rejected_input_ref=self._agreement_rejected_ref(agreement_ref, agreement_index),
                        field_prefix=f"access_agreements[{agreement_index}]",
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )
            if agreement_ref is None:
                errors.append(
                    self._error(
                        error_code="CONTRACT_SCOPE_VIOLATION",
                        source_id=source_id,
                        rejected_input_ref=f"access_agreements[{agreement_index}]",
                        field_path=f"access_agreements[{agreement_index}]",
                        message="AccessAgreementRef must be a mapping.",
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )
                continue
            errors.extend(
                self._validate_agreement(
                    agreement_ref=agreement_ref,
                    agreement_index=agreement_index,
                    expected_source_id=source_id,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                    reference_date=reference_date,
                )
            )

        active_licenses = [license_ref for _, license_ref, _ in related_licenses if license_ref is not None]
        active_agreements = [
            agreement_ref for _, agreement_ref, _ in related_agreements if agreement_ref is not None
        ]
        errors.extend(
            self._validate_rights_evidence(
                declaration=declaration,
                declaration_index=declaration_index,
                declaration_ref=declaration_ref,
                licenses=active_licenses,
                agreements=active_agreements,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )

        if any(error.blocking for error in errors):
            return SourceRegistryRightsResult(None, None, None, None, errors)

        accepted = self._build_accepted_result(
            declaration=declaration,
            licenses=active_licenses,
            agreements=active_agreements,
            phase_contract_ref=phase_contract_ref or "",
            emitted_at=emitted_at,
            reference_date=reference_date,
            parent_ids=parent_ids,
        )
        duplicate_error = self._validate_current_record(accepted, parent_ids, emitted_at)
        if duplicate_error is not None:
            return SourceRegistryRightsResult(None, None, None, None, [duplicate_error])

        self._current_by_source_id[accepted.source_registration.source_id] = accepted
        return accepted

    def _coerce_licenses(
        self, license_files: Sequence[Mapping[str, Any]]
    ) -> list[tuple[LicenseDocumentRef | None, Mapping[str, Any] | None]]:
        result: list[tuple[LicenseDocumentRef | None, Mapping[str, Any] | None]] = []
        for raw in license_files:
            mapping = _as_mapping(raw)
            if mapping is None:
                result.append((None, None))
            else:
                result.append((LicenseDocumentRef.from_mapping(mapping), mapping))
        return result

    def _coerce_agreements(
        self, access_agreements: Sequence[Mapping[str, Any]]
    ) -> list[tuple[AccessAgreementRef | None, Mapping[str, Any] | None]]:
        result: list[tuple[AccessAgreementRef | None, Mapping[str, Any] | None]] = []
        for raw in access_agreements:
            mapping = _as_mapping(raw)
            if mapping is None:
                result.append((None, None))
            else:
                result.append((AccessAgreementRef.from_mapping(mapping), mapping))
        return result

    def _related_licenses(
        self,
        source_id: str | None,
        declaration_count: int,
        licenses: Sequence[tuple[LicenseDocumentRef | None, Mapping[str, Any] | None]],
    ) -> list[tuple[int, LicenseDocumentRef | None, Mapping[str, Any] | None]]:
        related: list[tuple[int, LicenseDocumentRef | None, Mapping[str, Any] | None]] = []
        for index, (license_ref, raw_license) in enumerate(licenses):
            if source_id is None:
                if declaration_count == 1 or license_ref is None or not _is_non_empty_string(license_ref.source_id):
                    related.append((index, license_ref, raw_license))
            elif license_ref is not None and license_ref.source_id == source_id:
                related.append((index, license_ref, raw_license))
        return related

    def _related_agreements(
        self,
        source_id: str | None,
        declaration_count: int,
        agreements: Sequence[tuple[AccessAgreementRef | None, Mapping[str, Any] | None]],
    ) -> list[tuple[int, AccessAgreementRef | None, Mapping[str, Any] | None]]:
        related: list[tuple[int, AccessAgreementRef | None, Mapping[str, Any] | None]] = []
        for index, (agreement_ref, raw_agreement) in enumerate(agreements):
            if source_id is None:
                if (
                    declaration_count == 1
                    or agreement_ref is None
                    or not _is_non_empty_string(agreement_ref.source_id)
                ):
                    related.append((index, agreement_ref, raw_agreement))
            elif agreement_ref is not None and agreement_ref.source_id == source_id:
                related.append((index, agreement_ref, raw_agreement))
        return related

    def _validate_phase_contract(
        self,
        phase_contract_ref: str | None,
        source_id: str | None,
        declaration_ref: str,
        emitted_at: str,
    ) -> list[SourceRightsValidationError]:
        if not _is_non_empty_string(phase_contract_ref):
            return [
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=source_id,
                    rejected_input_ref=declaration_ref,
                    field_path="phase_contract_ref",
                    message="phase_contract_ref is required and must reference motor_001 authority.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            ]
        if self.known_phase_contract_refs and phase_contract_ref not in self.known_phase_contract_refs:
            return [
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=source_id,
                    rejected_input_ref=declaration_ref,
                    field_path="phase_contract_ref",
                    message="phase_contract_ref is not in the authorized contract reference set.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            ]
        return []

    def _validate_forbidden_fields(
        self,
        payload: Mapping[str, Any],
        source_id: str | None,
        rejected_input_ref: str,
        field_prefix: str,
        phase_contract_ref: str | None,
        emitted_at: str,
    ) -> list[SourceRightsValidationError]:
        errors: list[SourceRightsValidationError] = []
        for key in sorted(payload):
            if key in FORBIDDEN_INPUT_FIELDS:
                errors.append(
                    self._error(
                        error_code="CONTRACT_SCOPE_VIOLATION",
                        source_id=source_id,
                        rejected_input_ref=rejected_input_ref,
                        field_path=f"{field_prefix}.{key}",
                        message="Source payload, quality, identity, inference, or reporting fields are outside motor_008 scope.",
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )
        return errors

    def _validate_declaration(
        self,
        declaration: SourceDeclaration,
        declaration_index: int,
        phase_contract_ref: str | None,
        emitted_at: str,
    ) -> list[SourceRightsValidationError]:
        source_id = declaration.source_id if _is_non_empty_string(declaration.source_id) else None
        rejected_ref = (
            declaration.declaration_ref
            if _is_non_empty_string(declaration.declaration_ref)
            else f"source_declarations[{declaration_index}]"
        )
        checks = (
            ("source_id", declaration.source_id, "MISSING_SOURCE_ID", "source_id is required."),
            ("source_name", declaration.source_name, "CONTRACT_SCOPE_VIOLATION", "source_name is required."),
            (
                "source_locator",
                declaration.source_locator,
                "MISSING_SOURCE_LOCATOR",
                "source_locator is required.",
            ),
            ("source_type", declaration.source_type, "CONTRACT_SCOPE_VIOLATION", "source_type is required."),
            (
                "declared_owner",
                declaration.declared_owner,
                "MISSING_OWNER",
                "declared_owner is required.",
            ),
            (
                "declaration_ref",
                declaration.declaration_ref,
                "CONTRACT_SCOPE_VIOLATION",
                "declaration_ref is required.",
            ),
            (
                "submitted_by",
                declaration.submitted_by,
                "CONTRACT_SCOPE_VIOLATION",
                "submitted_by is required.",
            ),
            (
                "submitted_at",
                declaration.submitted_at,
                "CONTRACT_SCOPE_VIOLATION",
                "submitted_at is required.",
            ),
        )

        errors: list[SourceRightsValidationError] = []
        for field_name, value, error_code, message in checks:
            if not _is_non_empty_string(value):
                errors.append(
                    self._error(
                        error_code=error_code,
                        source_id=source_id,
                        rejected_input_ref=rejected_ref,
                        field_path=f"source_declarations[{declaration_index}].{field_name}",
                        message=message,
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )

        if declaration.declared_refresh is not None and not _is_non_empty_string(declaration.declared_refresh):
            errors.append(
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"source_declarations[{declaration_index}].declared_refresh",
                    message="declared_refresh must be a non-empty string or null.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        if declaration.declared_use is None or (
            isinstance(declaration.declared_use, str) and not declaration.declared_use.strip()
        ):
            errors.append(
                self._error(
                    error_code="MISSING_DECLARED_USE",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"source_declarations[{declaration_index}].declared_use",
                    message="declared_use is required.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )
        elif not isinstance(declaration.declared_use, str):
            errors.append(
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"source_declarations[{declaration_index}].declared_use",
                    message="declared_use must be a string and must not be coerced.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        if _is_non_empty_string(declaration.submitted_at) and _parse_datetime(declaration.submitted_at) is None:
            errors.append(
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"source_declarations[{declaration_index}].submitted_at",
                    message="submitted_at must be an ISO datetime.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        return errors

    def _validate_license(
        self,
        license_ref: LicenseDocumentRef,
        license_index: int,
        expected_source_id: str | None,
        phase_contract_ref: str | None,
        emitted_at: str,
        reference_date: date,
    ) -> list[SourceRightsValidationError]:
        rejected_ref = self._license_rejected_ref(license_ref, license_index)
        source_id = license_ref.source_id if _is_non_empty_string(license_ref.source_id) else expected_source_id
        errors: list[SourceRightsValidationError] = []
        required_string_checks = (
            ("license_ref_id", license_ref.license_ref_id, "UNTRACEABLE_DOCUMENT_REF", "license_ref_id is required."),
            ("source_id", license_ref.source_id, "UNTRACEABLE_DOCUMENT_REF", "source_id is required."),
            ("document_ref", license_ref.document_ref, "UNTRACEABLE_DOCUMENT_REF", "document_ref is required."),
            ("license_basis", license_ref.license_basis, "MISSING_RIGHTS_EVIDENCE", "license_basis is required."),
            (
                "restriction_notes",
                license_ref.restriction_notes,
                "MISSING_RIGHTS_EVIDENCE",
                "restriction_notes is required, even when the note states no additional restrictions.",
            ),
            ("observed_at", license_ref.observed_at, "UNTRACEABLE_DOCUMENT_REF", "observed_at is required."),
        )
        for field_name, value, error_code, message in required_string_checks:
            if not _is_non_empty_string(value):
                errors.append(
                    self._error(
                        error_code=error_code,
                        source_id=source_id,
                        rejected_input_ref=rejected_ref,
                        field_path=f"license_files[{license_index}].{field_name}",
                        message=message,
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )

        if expected_source_id is not None and license_ref.source_id != expected_source_id:
            errors.append(
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=expected_source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"license_files[{license_index}].source_id",
                    message="LicenseDocumentRef.source_id must match SourceDeclaration.source_id.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        errors.extend(
            self._validate_string_list_field(
                value=license_ref.permitted_uses,
                field_path=f"license_files[{license_index}].permitted_uses",
                source_id=source_id,
                rejected_ref=rejected_ref,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )
        errors.extend(
            self._validate_string_list_field(
                value=license_ref.prohibited_uses,
                field_path=f"license_files[{license_index}].prohibited_uses",
                source_id=source_id,
                rejected_ref=rejected_ref,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )
        errors.extend(
            self._validate_string_list_field(
                value=license_ref.attribution_requirements,
                field_path=f"license_files[{license_index}].attribution_requirements",
                source_id=source_id,
                rejected_ref=rejected_ref,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )

        errors.extend(
            self._validate_date_window(
                effective_from=license_ref.effective_from,
                effective_to=license_ref.effective_to,
                source_id=source_id,
                rejected_ref=rejected_ref,
                field_prefix=f"license_files[{license_index}]",
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
                reference_date=reference_date,
                expired_error_code="INVALID_LICENSE_DATES",
            )
        )

        if _is_non_empty_string(license_ref.observed_at) and _parse_datetime(license_ref.observed_at) is None:
            errors.append(
                self._error(
                    error_code="UNTRACEABLE_DOCUMENT_REF",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"license_files[{license_index}].observed_at",
                    message="observed_at must be an ISO datetime.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        return errors

    def _validate_agreement(
        self,
        agreement_ref: AccessAgreementRef,
        agreement_index: int,
        expected_source_id: str | None,
        phase_contract_ref: str | None,
        emitted_at: str,
        reference_date: date,
    ) -> list[SourceRightsValidationError]:
        rejected_ref = self._agreement_rejected_ref(agreement_ref, agreement_index)
        source_id = agreement_ref.source_id if _is_non_empty_string(agreement_ref.source_id) else expected_source_id
        errors: list[SourceRightsValidationError] = []

        required_string_checks = (
            (
                "agreement_ref_id",
                agreement_ref.agreement_ref_id,
                "UNTRACEABLE_DOCUMENT_REF",
                "agreement_ref_id is required.",
            ),
            ("source_id", agreement_ref.source_id, "UNTRACEABLE_DOCUMENT_REF", "source_id is required."),
            ("document_ref", agreement_ref.document_ref, "UNTRACEABLE_DOCUMENT_REF", "document_ref is required."),
            ("access_basis", agreement_ref.access_basis, "MISSING_RIGHTS_EVIDENCE", "access_basis is required."),
            ("observed_at", agreement_ref.observed_at, "UNTRACEABLE_DOCUMENT_REF", "observed_at is required."),
        )
        for field_name, value, error_code, message in required_string_checks:
            if not _is_non_empty_string(value):
                errors.append(
                    self._error(
                        error_code=error_code,
                        source_id=source_id,
                        rejected_input_ref=rejected_ref,
                        field_path=f"access_agreements[{agreement_index}].{field_name}",
                        message=message,
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )

        if expected_source_id is not None and agreement_ref.source_id != expected_source_id:
            errors.append(
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=expected_source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"access_agreements[{agreement_index}].source_id",
                    message="AccessAgreementRef.source_id must match SourceDeclaration.source_id.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        for field_name, value in (
            ("authentication_required", agreement_ref.authentication_required),
            ("payment_required", agreement_ref.payment_required),
        ):
            if not isinstance(value, bool):
                errors.append(
                    self._error(
                        error_code="CONTRACT_SCOPE_VIOLATION",
                        source_id=source_id,
                        rejected_input_ref=rejected_ref,
                        field_path=f"access_agreements[{agreement_index}].{field_name}",
                        message=f"{field_name} must be a boolean.",
                        blocking=True,
                        phase_contract_ref=phase_contract_ref,
                        emitted_at=emitted_at,
                    )
                )

        if agreement_ref.quota_notes is not None and not _is_non_empty_string(agreement_ref.quota_notes):
            errors.append(
                self._error(
                    error_code="CONTRACT_SCOPE_VIOLATION",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"access_agreements[{agreement_index}].quota_notes",
                    message="quota_notes must be a non-empty string or null.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        errors.extend(
            self._validate_string_list_field(
                value=agreement_ref.territorial_restrictions,
                field_path=f"access_agreements[{agreement_index}].territorial_restrictions",
                source_id=source_id,
                rejected_ref=rejected_ref,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )
        errors.extend(
            self._validate_string_list_field(
                value=agreement_ref.permitted_uses,
                field_path=f"access_agreements[{agreement_index}].permitted_uses",
                source_id=source_id,
                rejected_ref=rejected_ref,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )
        errors.extend(
            self._validate_string_list_field(
                value=agreement_ref.prohibited_uses,
                field_path=f"access_agreements[{agreement_index}].prohibited_uses",
                source_id=source_id,
                rejected_ref=rejected_ref,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        )

        if agreement_ref.embargo_until is not None and _parse_date(agreement_ref.embargo_until) is None:
            errors.append(
                self._error(
                    error_code="INVALID_LICENSE_DATES",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"access_agreements[{agreement_index}].embargo_until",
                    message="embargo_until must be an ISO date or null.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        errors.extend(
            self._validate_date_window(
                effective_from=agreement_ref.effective_from,
                effective_to=agreement_ref.effective_to,
                source_id=source_id,
                rejected_ref=rejected_ref,
                field_prefix=f"access_agreements[{agreement_index}]",
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
                reference_date=reference_date,
                expired_error_code="EXPIRED_ACCESS_AGREEMENT",
            )
        )

        if _is_non_empty_string(agreement_ref.observed_at) and _parse_datetime(agreement_ref.observed_at) is None:
            errors.append(
                self._error(
                    error_code="UNTRACEABLE_DOCUMENT_REF",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"access_agreements[{agreement_index}].observed_at",
                    message="observed_at must be an ISO datetime.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        return errors

    def _validate_string_list_field(
        self,
        value: Any,
        field_path: str,
        source_id: str | None,
        rejected_ref: str,
        phase_contract_ref: str | None,
        emitted_at: str,
    ) -> list[SourceRightsValidationError]:
        if _string_list(value) is not None:
            return []
        return [
            self._error(
                error_code="CONTRACT_SCOPE_VIOLATION",
                source_id=source_id,
                rejected_input_ref=rejected_ref,
                field_path=field_path,
                message="Field must be a list of non-empty strings and must not be coerced.",
                blocking=True,
                phase_contract_ref=phase_contract_ref,
                emitted_at=emitted_at,
            )
        ]

    def _validate_date_window(
        self,
        effective_from: Any,
        effective_to: Any,
        source_id: str | None,
        rejected_ref: str,
        field_prefix: str,
        phase_contract_ref: str | None,
        emitted_at: str,
        reference_date: date,
        expired_error_code: str,
    ) -> list[SourceRightsValidationError]:
        errors: list[SourceRightsValidationError] = []
        start = _parse_date(effective_from)
        end = _parse_date(effective_to)

        if effective_from is not None and start is None:
            errors.append(
                self._error(
                    error_code="INVALID_LICENSE_DATES",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"{field_prefix}.effective_from",
                    message="effective_from must be an ISO date or null.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )
        if effective_to is not None and end is None:
            errors.append(
                self._error(
                    error_code="INVALID_LICENSE_DATES",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"{field_prefix}.effective_to",
                    message="effective_to must be an ISO date or null.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )
        if start is not None and end is not None and end < start:
            errors.append(
                self._error(
                    error_code="INVALID_LICENSE_DATES",
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"{field_prefix}.effective_to",
                    message="effective_to cannot be earlier than effective_from.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )
        if end is not None and end < reference_date:
            errors.append(
                self._error(
                    error_code=expired_error_code,
                    source_id=source_id,
                    rejected_input_ref=rejected_ref,
                    field_path=f"{field_prefix}.effective_to",
                    message="Rights or access evidence expired before the validation date.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )
        return errors

    def _validate_rights_evidence(
        self,
        declaration: SourceDeclaration,
        declaration_index: int,
        declaration_ref: str,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
        phase_contract_ref: str | None,
        emitted_at: str,
    ) -> list[SourceRightsValidationError]:
        source_id = declaration.source_id if _is_non_empty_string(declaration.source_id) else None
        permitted = _dedupe(
            use
            for evidence in [*licenses, *agreements]
            for use in (_string_list(evidence.permitted_uses) or [])
        )
        prohibited = _dedupe(
            use
            for evidence in [*licenses, *agreements]
            for use in (_string_list(evidence.prohibited_uses) or [])
        )
        errors: list[SourceRightsValidationError] = []

        if not permitted and (licenses or agreements):
            errors.append(
                self._error(
                    error_code="MISSING_RIGHTS_EVIDENCE",
                    source_id=source_id,
                    rejected_input_ref=declaration_ref,
                    field_path="license_files.permitted_uses|access_agreements.permitted_uses",
                    message="At least one documented permitted use is required before registration.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        conflicting_uses = sorted(set(permitted).intersection(prohibited))
        if conflicting_uses:
            errors.append(
                self._error(
                    error_code="RIGHTS_CONFLICT",
                    source_id=source_id,
                    rejected_input_ref=declaration_ref,
                    field_path="license_files|access_agreements",
                    message=f"Evidence both permits and prohibits: {', '.join(conflicting_uses)}.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        if isinstance(declaration.declared_use, str) and declaration.declared_use in prohibited:
            errors.append(
                self._error(
                    error_code="RIGHTS_CONFLICT",
                    source_id=source_id,
                    rejected_input_ref=declaration_ref,
                    field_path=f"source_declarations[{declaration_index}].declared_use",
                    message="Declared use is explicitly prohibited by active rights evidence.",
                    blocking=True,
                    phase_contract_ref=phase_contract_ref,
                    emitted_at=emitted_at,
                )
            )

        return errors

    def _build_accepted_result(
        self,
        declaration: SourceDeclaration,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
        phase_contract_ref: str,
        emitted_at: str,
        reference_date: date,
        parent_ids: Mapping[str, str | None],
    ) -> SourceRegistryRightsResult:
        source_id = declaration.source_id
        license_refs = [license_ref.license_ref_id for license_ref in licenses]
        agreement_refs = [agreement_ref.agreement_ref_id for agreement_ref in agreements]
        evidence_refs = _dedupe([*license_refs, *agreement_refs])
        permitted_uses = _dedupe(
            use
            for evidence in [*licenses, *agreements]
            for use in (_string_list(evidence.permitted_uses) or [])
        )
        prohibited_uses = _dedupe(
            use
            for evidence in [*licenses, *agreements]
            for use in (_string_list(evidence.prohibited_uses) or [])
        )
        attribution_requirements = _dedupe(
            requirement
            for license_ref in licenses
            for requirement in (_string_list(license_ref.attribution_requirements) or [])
        )
        restriction_notes = self._restriction_notes(licenses, agreements)
        license_basis = self._license_basis(licenses, agreements)
        effective_from = self._effective_from(licenses, agreements)
        effective_to = self._effective_to(licenses, agreements)
        evidence_observed_at = _max_datetime(
            [license_ref.observed_at for license_ref in licenses]
            + [agreement_ref.observed_at for agreement_ref in agreements]
        )
        rights_status = self._rights_status(
            attribution_requirements=attribution_requirements,
            agreements=agreements,
        )

        rights_profile_id = f"rights_{source_id}"
        access_class_id = f"access_{source_id}"
        refresh_schedule_id = f"refresh_{source_id}"

        access_class_value, assignment_reason = self._derive_access_class(
            rights_status=rights_status,
            agreements=agreements,
        )
        authentication_required = any(bool(agreement.authentication_required) for agreement in agreements)
        payment_required = any(bool(agreement.payment_required) for agreement in agreements)
        quota_notes = self._combined_optional_notes(agreement.quota_notes for agreement in agreements)
        embargo_until = self._earliest_date([agreement.embargo_until for agreement in agreements])
        territorial_restrictions = _dedupe(
            restriction
            for agreement in agreements
            for restriction in (_string_list(agreement.territorial_restrictions) or [])
        )
        periodicity, next_review_at, manual_condition, refresh_reason = self._derive_refresh_schedule(
            declaration=declaration,
            licenses=licenses,
            agreements=agreements,
            reference_date=reference_date,
        )
        schedule_basis_refs = _dedupe([declaration.declaration_ref, *evidence_refs])
        registration_status = self._registration_status(access_class_value)
        registration_reason = self._registration_reason(access_class_value, rights_status)

        rights_profile = self._rights_profile(
            rights_profile_id=rights_profile_id,
            source_id=source_id,
            license_basis=license_basis,
            license_document_refs=license_refs,
            agreement_refs=agreement_refs,
            permitted_uses=permitted_uses,
            prohibited_uses=prohibited_uses,
            restriction_notes=restriction_notes,
            attribution_requirements=attribution_requirements,
            rights_status=rights_status,
            effective_from=effective_from,
            effective_to=effective_to,
            evidence_observed_at=evidence_observed_at,
            phase_contract_ref=phase_contract_ref,
            source_ref=self._rights_source_ref(licenses, agreements),
            emitted_at=emitted_at,
            parent_id=parent_ids.get("rights_profile"),
        )
        access_class = self._access_class(
            access_class_id=access_class_id,
            source_id=source_id,
            rights_profile_id=rights_profile.rights_profile_id,
            access_class=access_class_value,
            assignment_reason=assignment_reason,
            supporting_document_refs=evidence_refs,
            authentication_required=authentication_required,
            payment_required=payment_required,
            quota_notes=quota_notes,
            embargo_until=embargo_until,
            territorial_restrictions=territorial_restrictions,
            effective_from=effective_from,
            effective_to=effective_to,
            phase_contract_ref=phase_contract_ref,
            source_ref=rights_profile.rights_profile_id,
            emitted_at=emitted_at,
            parent_id=parent_ids.get("access_class"),
        )
        refresh_schedule = self._refresh_schedule(
            refresh_schedule_id=refresh_schedule_id,
            source_id=source_id,
            periodicity=periodicity,
            next_review_at=next_review_at,
            manual_review_condition=manual_condition,
            refresh_reason=refresh_reason,
            schedule_basis_refs=schedule_basis_refs,
            phase_contract_ref=phase_contract_ref,
            source_ref=declaration.declaration_ref,
            emitted_at=emitted_at,
            parent_id=parent_ids.get("refresh_schedule"),
        )
        source_record = self._source_record(
            declaration=declaration,
            registration_status=registration_status,
            registration_reason=registration_reason,
            evidence_refs=evidence_refs,
            rights_profile_id=rights_profile.rights_profile_id,
            access_class_id=access_class.access_class_id,
            refresh_schedule_id=refresh_schedule.refresh_schedule_id,
            phase_contract_ref=phase_contract_ref,
            emitted_at=emitted_at,
            parent_id=parent_ids.get("source_registration"),
        )

        return SourceRegistryRightsResult(
            source_registration=source_record,
            rights_profile=rights_profile,
            access_class=access_class,
            refresh_schedule=refresh_schedule,
            validation_errors=[],
        )

    def _rights_status(
        self,
        attribution_requirements: Sequence[str],
        agreements: Sequence[AccessAgreementRef],
    ) -> str:
        if attribution_requirements:
            return "allowed_with_attribution"
        if any(_string_list(agreement.territorial_restrictions) for agreement in agreements):
            return "restricted"
        if any(_parse_date(agreement.embargo_until) is not None for agreement in agreements):
            return "restricted"
        return "allowed"

    def _derive_access_class(
        self,
        rights_status: str,
        agreements: Sequence[AccessAgreementRef],
    ) -> tuple[str, str]:
        if rights_status in {"blocked", "expired", "conflict"}:
            return "blocked", "Rights status blocks access classification."

        basis_text = _lower_text(*(agreement.access_basis for agreement in agreements))
        has_territorial_limits = any(_string_list(agreement.territorial_restrictions) for agreement in agreements)
        has_embargo = any(_parse_date(agreement.embargo_until) is not None for agreement in agreements)
        payment_required = any(bool(agreement.payment_required) for agreement in agreements)

        if any(term in basis_text for term in INTERNAL_TERMS):
            return "internal", "Access basis is documented as internal or private."
        if any(term in basis_text for term in CONTRACT_TERMS) and payment_required:
            return "contractual", "Paid or vendor contractual access is documented."
        if "contract" in basis_text or "agreement" in basis_text:
            return "contractual", "Contractual access agreement is documented."
        if payment_required or any(term in basis_text for term in SUBSCRIPTION_TERMS):
            return "premium", "Payment or subscription is required by access evidence."
        if has_territorial_limits or has_embargo or rights_status == "restricted":
            return "restricted", "Documented rights or access restrictions require restricted handling."
        return "public", "Rights evidence permits use without payment, contract, embargo, or territorial restriction."

    def _derive_refresh_schedule(
        self,
        declaration: SourceDeclaration,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
        reference_date: date,
    ) -> tuple[str, str | None, str | None, str]:
        declared = declaration.declared_refresh if isinstance(declaration.declared_refresh, str) else None
        normalized = declared.strip().casefold() if declared else None
        if normalized in {"daily", "weekly", "monthly", "quarterly", "annual"}:
            next_review = _next_review_date(reference_date, normalized)
            return (
                normalized,
                _date_to_str(next_review),
                None,
                f"Declared source refresh cadence is {normalized}.",
            )
        if normalized == "event_driven":
            return (
                "event_driven",
                None,
                "on_source_revision_notice",
                "Declared source cadence is event driven.",
            )
        if normalized == "manual_review":
            return (
                "manual_review",
                None,
                "on_manual_rights_review",
                "Declaration requires manual rights review.",
            )
        if normalized:
            return (
                "manual_review",
                None,
                normalized,
                "Declaration supplied a non-periodic review trigger.",
            )

        notes = " ".join(
            license_ref.restriction_notes
            for license_ref in licenses
            if _is_non_empty_string(license_ref.restriction_notes)
        ).casefold()
        if "terms page" in notes or "terms" in notes:
            return (
                "manual_review",
                None,
                "on_terms_page_change",
                "No fixed cadence was declared; rights notes require review when terms change.",
            )
        if agreements:
            return (
                "manual_review",
                None,
                "on_access_agreement_change",
                "No fixed cadence was declared; access agreement changes trigger review.",
            )
        return (
            "manual_review",
            None,
            "on_documented_rights_change",
            "No fixed cadence was declared; documented rights changes trigger review.",
        )

    def _registration_status(self, access_class_value: str) -> str:
        if access_class_value == "blocked":
            return "blocked"
        if access_class_value == "restricted":
            return "restricted"
        return "active"

    def _registration_reason(self, access_class_value: str, rights_status: str) -> str:
        if access_class_value == "blocked":
            return "Registration blocked by rights status."
        if access_class_value == "restricted":
            return "Registered with restricted handling due to documented rights constraints."
        return f"Registered with {rights_status} rights and {access_class_value} access classification."

    def _source_record(
        self,
        declaration: SourceDeclaration,
        registration_status: str,
        registration_reason: str,
        evidence_refs: list[str],
        rights_profile_id: str,
        access_class_id: str,
        refresh_schedule_id: str,
        phase_contract_ref: str,
        emitted_at: str,
        parent_id: str | None,
    ) -> SourceRecord:
        material = {
            "source_id": declaration.source_id,
            "source_name": declaration.source_name,
            "source_locator": declaration.source_locator,
            "source_type": declaration.source_type,
            "declared_owner": declaration.declared_owner,
            "declared_use": declaration.declared_use,
            "declared_refresh": declaration.declared_refresh,
            "registration_status": registration_status,
            "registration_reason": registration_reason,
            "declaration_ref": declaration.declaration_ref,
            "evidence_refs": evidence_refs,
            "rights_profile_id": rights_profile_id,
            "access_class_id": access_class_id,
            "refresh_schedule_id": refresh_schedule_id,
            "phase_contract_ref": phase_contract_ref,
            "source_ref": declaration.declaration_ref,
            "produced_by_motor": MOTOR_ID,
            "parent_id": parent_id,
        }
        record_id, version_id, version_hash = self._ids_for("source", material)
        return SourceRecord(
            record_id=record_id,
            source_id=declaration.source_id,
            source_name=declaration.source_name,
            source_locator=declaration.source_locator,
            source_type=declaration.source_type,
            declared_owner=declaration.declared_owner,
            declared_use=declaration.declared_use,
            declared_refresh=declaration.declared_refresh,
            registration_status=registration_status,
            registration_reason=registration_reason,
            declaration_ref=declaration.declaration_ref,
            evidence_refs=evidence_refs,
            rights_profile_id=rights_profile_id,
            access_class_id=access_class_id,
            refresh_schedule_id=refresh_schedule_id,
            phase_contract_ref=phase_contract_ref,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=declaration.declaration_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=emitted_at,
            parent_id=parent_id,
        )

    def _rights_profile(
        self,
        rights_profile_id: str,
        source_id: str,
        license_basis: str,
        license_document_refs: list[str],
        agreement_refs: list[str],
        permitted_uses: list[str],
        prohibited_uses: list[str],
        restriction_notes: str,
        attribution_requirements: list[str],
        rights_status: str,
        effective_from: str | None,
        effective_to: str | None,
        evidence_observed_at: str,
        phase_contract_ref: str,
        source_ref: str,
        emitted_at: str,
        parent_id: str | None,
    ) -> RightsProfile:
        material = {
            "rights_profile_id": rights_profile_id,
            "source_id": source_id,
            "license_basis": license_basis,
            "license_document_refs": license_document_refs,
            "agreement_refs": agreement_refs,
            "permitted_uses": permitted_uses,
            "prohibited_uses": prohibited_uses,
            "restriction_notes": restriction_notes,
            "attribution_requirements": attribution_requirements,
            "rights_status": rights_status,
            "effective_from": effective_from,
            "effective_to": effective_to,
            "evidence_observed_at": evidence_observed_at,
            "phase_contract_ref": phase_contract_ref,
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "parent_id": parent_id,
        }
        record_id, version_id, version_hash = self._ids_for("rights", material)
        return RightsProfile(
            record_id=record_id,
            rights_profile_id=rights_profile_id,
            source_id=source_id,
            license_basis=license_basis,
            license_document_refs=license_document_refs,
            agreement_refs=agreement_refs,
            permitted_uses=permitted_uses,
            prohibited_uses=prohibited_uses,
            restriction_notes=restriction_notes,
            attribution_requirements=attribution_requirements,
            rights_status=rights_status,
            effective_from=effective_from,
            effective_to=effective_to,
            evidence_observed_at=evidence_observed_at,
            phase_contract_ref=phase_contract_ref,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=emitted_at,
            parent_id=parent_id,
        )

    def _access_class(
        self,
        access_class_id: str,
        source_id: str,
        rights_profile_id: str,
        access_class: str,
        assignment_reason: str,
        supporting_document_refs: list[str],
        authentication_required: bool,
        payment_required: bool,
        quota_notes: str | None,
        embargo_until: str | None,
        territorial_restrictions: list[str],
        effective_from: str | None,
        effective_to: str | None,
        phase_contract_ref: str,
        source_ref: str,
        emitted_at: str,
        parent_id: str | None,
    ) -> AccessClass:
        material = {
            "access_class_id": access_class_id,
            "source_id": source_id,
            "rights_profile_id": rights_profile_id,
            "access_class": access_class,
            "assignment_reason": assignment_reason,
            "supporting_document_refs": supporting_document_refs,
            "authentication_required": authentication_required,
            "payment_required": payment_required,
            "quota_notes": quota_notes,
            "embargo_until": embargo_until,
            "territorial_restrictions": territorial_restrictions,
            "effective_from": effective_from,
            "effective_to": effective_to,
            "phase_contract_ref": phase_contract_ref,
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "parent_id": parent_id,
        }
        record_id, version_id, version_hash = self._ids_for("access", material)
        return AccessClass(
            record_id=record_id,
            access_class_id=access_class_id,
            source_id=source_id,
            rights_profile_id=rights_profile_id,
            access_class=access_class,
            assignment_reason=assignment_reason,
            supporting_document_refs=supporting_document_refs,
            authentication_required=authentication_required,
            payment_required=payment_required,
            quota_notes=quota_notes,
            embargo_until=embargo_until,
            territorial_restrictions=territorial_restrictions,
            effective_from=effective_from,
            effective_to=effective_to,
            phase_contract_ref=phase_contract_ref,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=emitted_at,
            parent_id=parent_id,
        )

    def _refresh_schedule(
        self,
        refresh_schedule_id: str,
        source_id: str,
        periodicity: str,
        next_review_at: str | None,
        manual_review_condition: str | None,
        refresh_reason: str,
        schedule_basis_refs: list[str],
        phase_contract_ref: str,
        source_ref: str,
        emitted_at: str,
        parent_id: str | None,
    ) -> RefreshSchedule:
        material = {
            "refresh_schedule_id": refresh_schedule_id,
            "source_id": source_id,
            "periodicity": periodicity,
            "next_review_at": next_review_at,
            "manual_review_condition": manual_review_condition,
            "refresh_reason": refresh_reason,
            "schedule_basis_refs": schedule_basis_refs,
            "phase_contract_ref": phase_contract_ref,
            "source_ref": source_ref,
            "produced_by_motor": MOTOR_ID,
            "parent_id": parent_id,
        }
        record_id, version_id, version_hash = self._ids_for("refresh", material)
        return RefreshSchedule(
            record_id=record_id,
            refresh_schedule_id=refresh_schedule_id,
            source_id=source_id,
            periodicity=periodicity,
            next_review_at=next_review_at,
            manual_review_condition=manual_review_condition,
            refresh_reason=refresh_reason,
            schedule_basis_refs=schedule_basis_refs,
            phase_contract_ref=phase_contract_ref,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=source_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=emitted_at,
            parent_id=parent_id,
        )

    def _validate_current_record(
        self,
        accepted: SourceRegistryRightsResult,
        parent_ids: Mapping[str, str | None],
        emitted_at: str,
    ) -> SourceRightsValidationError | None:
        source = accepted.source_registration
        if source is None:
            return None
        existing = self._current_by_source_id.get(source.source_id)
        if existing is None:
            return None
        if (
            existing.source_registration
            and existing.rights_profile
            and existing.access_class
            and existing.refresh_schedule
            and accepted.rights_profile
            and accepted.access_class
            and accepted.refresh_schedule
            and existing.source_registration.version_hash == source.version_hash
            and existing.rights_profile.version_hash == accepted.rights_profile.version_hash
            and existing.access_class.version_hash == accepted.access_class.version_hash
            and existing.refresh_schedule.version_hash == accepted.refresh_schedule.version_hash
        ):
            return None
        if not any(parent_ids.values()):
            return self._error(
                error_code="RIGHTS_CONFLICT",
                source_id=source.source_id,
                rejected_input_ref=source.declaration_ref,
                field_path="source_declarations[0].source_id",
                message="A current registration for source_id exists with different material rights content and no governed parent_id.",
                blocking=True,
                phase_contract_ref=source.phase_contract_ref,
                emitted_at=emitted_at,
            )
        return None

    def _error(
        self,
        error_code: str,
        source_id: str | None,
        rejected_input_ref: str,
        field_path: str,
        message: str,
        blocking: bool,
        phase_contract_ref: str | None,
        emitted_at: str,
        parent_id: str | None = None,
    ) -> SourceRightsValidationError:
        if error_code not in VALIDATION_ERROR_CODES:
            error_code = "CONTRACT_SCOPE_VIOLATION"
        material = {
            "error_code": error_code,
            "source_id": source_id,
            "rejected_input_ref": rejected_input_ref,
            "field_path": field_path,
            "message": message,
            "blocking": blocking,
            "phase_contract_ref": phase_contract_ref,
            "source_ref": rejected_input_ref,
            "produced_by_motor": MOTOR_ID,
            "parent_id": parent_id,
        }
        digest = _digest(material)
        error_id = f"err_{digest[:20]}"
        record_id = f"rec_validation_{digest[:20]}"
        version_id = f"ver_validation_{digest[:20]}"
        version_hash = _digest({**material, "error_id": error_id})
        return SourceRightsValidationError(
            record_id=record_id,
            error_id=error_id,
            error_code=error_code,
            source_id=source_id,
            rejected_input_ref=rejected_input_ref,
            field_path=field_path,
            message=message,
            blocking=blocking,
            detected_at=emitted_at,
            phase_contract_ref=phase_contract_ref,
            version_id=version_id,
            created_at=emitted_at,
            updated_at=emitted_at,
            version_hash=version_hash,
            source_ref=rejected_input_ref,
            produced_by_motor=MOTOR_ID,
            produced_at=emitted_at,
            parent_id=parent_id,
        )

    def _ids_for(self, prefix: str, material: Mapping[str, Any]) -> tuple[str, str, str]:
        version_hash = _digest(material)
        return (
            f"rec_{prefix}_{version_hash[:20]}",
            f"ver_{prefix}_{version_hash[:20]}",
            version_hash,
        )

    def _reference_date(
        self,
        source_declarations: Sequence[Mapping[str, Any]],
        licenses: Sequence[tuple[LicenseDocumentRef | None, Mapping[str, Any] | None]],
        agreements: Sequence[tuple[AccessAgreementRef | None, Mapping[str, Any] | None]],
        emitted_at: str,
        as_of_date: str | date | None,
    ) -> date:
        explicit = _parse_date(as_of_date)
        if explicit is not None:
            return explicit
        emitted = _parse_datetime(emitted_at)
        if emitted is not None and emitted_at != DEFAULT_EMITTED_AT:
            return emitted.date()

        observed: list[datetime] = []
        for raw_declaration in source_declarations if isinstance(source_declarations, Sequence) else ():
            mapping = _as_mapping(raw_declaration)
            if mapping is None:
                continue
            parsed = _parse_datetime(mapping.get("submitted_at"))
            if parsed is not None:
                observed.append(parsed)
        for license_ref, _ in licenses:
            if license_ref is None:
                continue
            parsed = _parse_datetime(license_ref.observed_at)
            if parsed is not None:
                observed.append(parsed)
        for agreement_ref, _ in agreements:
            if agreement_ref is None:
                continue
            parsed = _parse_datetime(agreement_ref.observed_at)
            if parsed is not None:
                observed.append(parsed)
        if observed:
            return max(observed).date()
        return date(1970, 1, 1)

    def _license_rejected_ref(self, license_ref: LicenseDocumentRef | None, index: int) -> str:
        if license_ref is not None and _is_non_empty_string(license_ref.license_ref_id):
            return license_ref.license_ref_id
        return f"license_files[{index}]"

    def _agreement_rejected_ref(self, agreement_ref: AccessAgreementRef | None, index: int) -> str:
        if agreement_ref is not None and _is_non_empty_string(agreement_ref.agreement_ref_id):
            return agreement_ref.agreement_ref_id
        return f"access_agreements[{index}]"

    def _license_basis(
        self,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
    ) -> str:
        license_parts = [license_ref.license_basis for license_ref in licenses]
        if license_parts:
            return " | ".join(_dedupe(license_parts))
        agreement_parts = [f"access agreement: {agreement.access_basis}" for agreement in agreements]
        return " | ".join(_dedupe(agreement_parts))

    def _restriction_notes(
        self,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
    ) -> str:
        notes = [license_ref.restriction_notes for license_ref in licenses]
        for agreement in agreements:
            agreement_notes: list[str] = []
            if _is_non_empty_string(agreement.quota_notes):
                agreement_notes.append(f"quota: {agreement.quota_notes}")
            if _parse_date(agreement.embargo_until) is not None:
                agreement_notes.append(f"embargo_until: {agreement.embargo_until}")
            restrictions = _string_list(agreement.territorial_restrictions) or []
            if restrictions:
                agreement_notes.append(f"territorial_restrictions: {', '.join(restrictions)}")
            if agreement_notes:
                notes.append("; ".join(agreement_notes))
        combined = " | ".join(_dedupe(note for note in notes if _is_non_empty_string(note)))
        if combined:
            return combined
        return "No additional restrictions documented beyond cited rights evidence."

    def _effective_from(
        self,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
    ) -> str | None:
        dates = [
            parsed
            for parsed in (
                _parse_date(evidence.effective_from) for evidence in [*licenses, *agreements]
            )
            if parsed is not None
        ]
        return _date_to_str(min(dates)) if dates else None

    def _effective_to(
        self,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
    ) -> str | None:
        dates = [
            parsed
            for parsed in (
                _parse_date(evidence.effective_to) for evidence in [*licenses, *agreements]
            )
            if parsed is not None
        ]
        return _date_to_str(min(dates)) if dates else None

    def _earliest_date(self, values: Iterable[Any]) -> str | None:
        dates = [parsed for parsed in (_parse_date(value) for value in values) if parsed is not None]
        return _date_to_str(min(dates)) if dates else None

    def _combined_optional_notes(self, values: Iterable[Any]) -> str | None:
        notes = _dedupe(value for value in values if _is_non_empty_string(value))
        if not notes:
            return None
        return " | ".join(notes)

    def _rights_source_ref(
        self,
        licenses: Sequence[LicenseDocumentRef],
        agreements: Sequence[AccessAgreementRef],
    ) -> str:
        if licenses:
            return licenses[0].document_ref
        return agreements[0].document_ref

    def _result_from_mapping(self, payload: Mapping[str, Any]) -> SourceRegistryRightsResult:
        source_registration = payload.get("source_registration")
        rights_profile = payload.get("rights_profile")
        access_class = payload.get("access_class")
        refresh_schedule = payload.get("refresh_schedule")
        validation_errors = payload.get("validation_errors") or []
        return SourceRegistryRightsResult(
            source_registration=SourceRecord(**source_registration) if source_registration else None,
            rights_profile=RightsProfile(**rights_profile) if rights_profile else None,
            access_class=AccessClass(**access_class) if access_class else None,
            refresh_schedule=RefreshSchedule(**refresh_schedule) if refresh_schedule else None,
            validation_errors=[SourceRightsValidationError(**error) for error in validation_errors],
        )


__all__ = [
    "AccessAgreementRef",
    "AccessClass",
    "LicenseDocumentRef",
    "RefreshSchedule",
    "RIGHTS_STATUSES",
    "SourceDeclaration",
    "SourceRecord",
    "SourceRegistryRightsEngine",
    "SourceRegistryRightsResult",
    "SourceRightsValidationError",
    "RightsProfile",
]
