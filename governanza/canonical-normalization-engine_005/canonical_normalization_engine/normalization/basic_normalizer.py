from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from .currency_converter import BasicCurrencyConverter
from .field_mapper import BasicFieldMapper
from .inputs import ParsedFieldInput
from .results import FieldMappingStatus, NormalizationExecutionResult, WarningDraft
from .type_coercer import BasicTypeCoercer
from .unit_converter import BasicUnitConverter
from .warning_builder import NormalizationWarningBuilder
from ..domain.entities import (
    CanonicalFieldDefinition,
    CanonicalSchemaVersion,
    CurrencyConversionRule,
    FieldMappingRule,
    TypeCoercionRule,
    UnitConversionRule,
)
from ..domain.enums import (
    MissingnessStatus,
    NormalizationStatus,
    PartialNormalizationStatus,
    ReplayabilityStatus,
    WarningSeverity,
)
from ..domain.records import (
    NonNormalizableFieldRecord,
    NormalizationReplayManifest,
    NormalizationRunRecord,
    NormalizedFieldRecord,
    NormalizedRecord,
    NormalizedRecordSet,
    PartialNormalizationRecord,
)
from ..domain.value_objects import (
    NonNormalizableFieldRecordId,
    NonNormalizableReason,
    NormalizationReplayManifestId,
    NormalizationRunRecordId,
    NormalizationScopeRef,
    NormalizedFieldRecordId,
    NormalizedRecordId,
    NormalizedRecordSetId,
    NormalizedValue,
    ParsedSourceProvenance,
    PartialNormalizationRecordId,
    PrecisionDescriptor,
    PrecisionKind,
    RawValue,
    RecordKey,
    ValueTriplet,
)


DEFAULT_NORMALIZER_VERSION = "0.1.0"


class BasicNormalizer:
    def __init__(
        self,
        *,
        normalizer_version: str = DEFAULT_NORMALIZER_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._normalizer_version = normalizer_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))
        self._field_mapper = BasicFieldMapper()
        self._type_coercer = BasicTypeCoercer()
        self._unit_converter = BasicUnitConverter()
        self._currency_converter = BasicCurrencyConverter()
        self._warning_builder = NormalizationWarningBuilder(clock=self._clock)

    def normalize_record(
        self,
        *,
        canonical_schema_version: CanonicalSchemaVersion,
        record_key: RecordKey,
        field_inputs: Iterable[ParsedFieldInput],
        canonical_field_definitions: Iterable[CanonicalFieldDefinition],
        field_mapping_rules: Iterable[FieldMappingRule],
        type_coercion_rules: Iterable[TypeCoercionRule] = (),
        unit_conversion_rules: Iterable[UnitConversionRule] = (),
        currency_conversion_rules: Iterable[CurrencyConversionRule] = (),
        normalization_run_record_id: NormalizationRunRecordId | None = None,
    ) -> NormalizationExecutionResult:
        field_inputs = tuple(field_inputs)
        canonical_field_definitions = tuple(canonical_field_definitions)
        field_mapping_rules = tuple(field_mapping_rules)
        type_coercion_rules = tuple(type_coercion_rules)
        unit_conversion_rules = tuple(unit_conversion_rules)
        currency_conversion_rules = tuple(currency_conversion_rules)

        if not field_inputs:
            raise ValueError("BasicNormalizer.normalize_record requires at least one parsed field input.")

        run_provenance = _derive_common_provenance(field_inputs)
        record_provenance = _derive_record_provenance(field_inputs)
        run_id = normalization_run_record_id or NormalizationRunRecordId(
            _stable_id(
                "normalization_run",
                canonical_schema_version.canonical_schema_version_id.value,
                record_key.value,
                run_provenance.raw_asset_version_ref.value,
                run_provenance.parsed_document_object_ref.value,
            )
        )
        normalized_record_id = NormalizedRecordId(
            _stable_id("normalized_record", run_id.value, record_key.value)
        )
        normalized_record_set_id = NormalizedRecordSetId(
            _stable_id("normalized_record_set", run_id.value, record_key.value)
        )

        warnings: list = []
        normalized_fields: list[NormalizedFieldRecord] = []
        non_normalizable_fields: list[NonNormalizableFieldRecord] = []
        used_mapping_rule_ids: list = []
        used_coercion_rule_ids: list = []
        used_unit_rule_ids: list = []
        used_currency_rule_ids: list = []

        for field_input in field_inputs:
            mapping_result = self._field_mapper.map_field(
                field_input=field_input,
                canonical_field_definitions=canonical_field_definitions,
                field_mapping_rules=field_mapping_rules,
                canonical_schema_version_id=canonical_schema_version.canonical_schema_version_id,
            )
            if mapping_result.status is not FieldMappingStatus.MATCHED:
                non_normalizable = self._build_non_normalizable_from_mapping(
                    run_id=run_id,
                    field_input=field_input,
                    mapping_result=mapping_result,
                )
                non_normalizable_fields.append(non_normalizable)
                warnings.extend(
                    self._build_warnings(
                        run_id=run_id,
                        scope_ref=NormalizationScopeRef.for_non_normalizable_field(
                            non_normalizable.non_normalizable_field_record_id
                        ),
                        warning_drafts=(
                            *mapping_result.warning_drafts,
                            WarningDraft(
                                code="normalization.non_normalizable_field",
                                severity=WarningSeverity.MODERATE,
                                message="Parsed field could not be normalized under the available explicit mapping and typing rules.",
                            ),
                        ),
                    )
                )
                continue

            field_definition = mapping_result.canonical_field_definition
            assert field_definition is not None
            coercion_result = self._type_coercer.coerce_value(
                field_input=field_input,
                canonical_field_definition=field_definition,
                type_coercion_rules=type_coercion_rules,
            )
            if coercion_result.normalization_status is NormalizationStatus.NON_NORMALIZABLE:
                non_normalizable = self._build_non_normalizable_from_typed_field(
                    run_id=run_id,
                    field_input=field_input,
                    field_definition=field_definition,
                    mapping_rule_id=mapping_result.field_mapping_rule_id,
                    reason=coercion_result.non_normalizable_reason
                    or NonNormalizableReason(
                        "Field coercion failed under the available explicit typing rules."
                    ),
                )
                non_normalizable_fields.append(non_normalizable)
                warnings.extend(
                    self._build_warnings(
                        run_id=run_id,
                        scope_ref=NormalizationScopeRef.for_non_normalizable_field(
                            non_normalizable.non_normalizable_field_record_id
                        ),
                        warning_drafts=(
                            *coercion_result.warning_drafts,
                            WarningDraft(
                                code="normalization.non_normalizable_field",
                                severity=WarningSeverity.MODERATE,
                                message="Parsed field could not be coerced into the canonical field type under the available explicit rules.",
                            ),
                        ),
                    )
                )
                if mapping_result.field_mapping_rule_id is not None:
                    used_mapping_rule_ids.append(mapping_result.field_mapping_rule_id)
                if coercion_result.type_coercion_rule_id is not None:
                    used_coercion_rule_ids.append(coercion_result.type_coercion_rule_id)
                continue
            final_status = coercion_result.normalization_status
            normalized_text = coercion_result.normalized_value_text
            normalized_unit = field_input.original_unit
            normalized_currency = field_input.original_currency
            unit_rule_id = None
            currency_rule_id = None

            if field_definition.canonical_field_type.value == "measure_with_unit":
                unit_result = self._unit_converter.convert_value(
                    canonical_field_definition=field_definition,
                    original_unit=field_input.original_unit,
                    numeric_value=coercion_result.numeric_value,
                    unit_conversion_rules=unit_conversion_rules,
                )
                final_status = _combine_statuses(final_status, unit_result.normalization_status)
                if unit_result.normalized_value_text is not None:
                    normalized_text = unit_result.normalized_value_text
                normalized_unit = unit_result.normalized_unit
                unit_rule_id = unit_result.unit_conversion_rule_id
                warnings.extend(
                    self._build_warnings(
                        run_id=run_id,
                        scope_ref=NormalizationScopeRef.for_normalized_field(
                            self._normalized_field_id(run_id, field_input, field_definition)
                        ),
                        warning_drafts=unit_result.warning_drafts,
                    )
                )
                if unit_rule_id is not None:
                    used_unit_rule_ids.append(unit_rule_id)

            if field_definition.canonical_field_type.value == "currency_amount":
                currency_result = self._currency_converter.convert_value(
                    canonical_field_definition=field_definition,
                    original_currency=field_input.original_currency,
                    currency_year=field_input.currency_year,
                    numeric_value=coercion_result.numeric_value,
                    currency_conversion_rules=currency_conversion_rules,
                )
                final_status = _combine_statuses(final_status, currency_result.normalization_status)
                if currency_result.normalized_value_text is not None:
                    normalized_text = currency_result.normalized_value_text
                normalized_currency = currency_result.normalized_currency
                currency_rule_id = currency_result.currency_conversion_rule_id
                warnings.extend(
                    self._build_warnings(
                        run_id=run_id,
                        scope_ref=NormalizationScopeRef.for_normalized_field(
                            self._normalized_field_id(run_id, field_input, field_definition)
                        ),
                        warning_drafts=currency_result.warning_drafts,
                    )
                )
                if currency_rule_id is not None:
                    used_currency_rule_ids.append(currency_rule_id)

            normalized_field = self._build_normalized_field(
                run_id=run_id,
                normalized_record_id=normalized_record_id,
                field_input=field_input,
                field_definition=field_definition,
                mapping_rule_id=mapping_result.field_mapping_rule_id,
                coercion_result=coercion_result,
                normalized_value_text=normalized_text,
                normalized_unit=normalized_unit,
                normalized_currency=normalized_currency,
                final_status=final_status,
                unit_rule_id=unit_rule_id,
                currency_rule_id=currency_rule_id,
            )
            normalized_fields.append(normalized_field)
            used_mapping_rule_ids.append(mapping_result.field_mapping_rule_id)
            if coercion_result.type_coercion_rule_id is not None:
                used_coercion_rule_ids.append(coercion_result.type_coercion_rule_id)
            warnings.extend(
                self._build_warnings(
                    run_id=run_id,
                    scope_ref=NormalizationScopeRef.for_normalized_field(
                        normalized_field.normalized_field_record_id
                    ),
                    warning_drafts=_field_warning_drafts(
                        field_status=final_status,
                        coercion_warning_drafts=coercion_result.warning_drafts,
                    ),
                )
            )

        record_status = _derive_record_status(normalized_fields)
        run_status = _derive_run_status(normalized_fields, non_normalizable_fields)
        replayability_status = _derive_replayability_status(run_status)
        normalization_run_record = NormalizationRunRecord.for_schema_version(
            normalization_run_record_id=run_id,
            schema_version=canonical_schema_version,
            source_provenance=run_provenance,
            normalization_status=run_status,
            replayability_status=replayability_status,
            created_at=self._clock(),
        )

        normalized_record = None
        normalized_record_set = None
        if normalized_fields:
            normalized_record = NormalizedRecord(
                normalized_record_id=normalized_record_id,
                normalized_record_set_id=normalized_record_set_id,
                normalization_run_record_id=run_id,
                source_provenance=record_provenance,
                record_key=record_key,
                normalization_status=record_status,
                normalized_field_record_ids=tuple(
                    item.normalized_field_record_id for item in normalized_fields
                ),
                created_at=self._clock(),
            )
            normalized_record_set = NormalizedRecordSet(
                normalized_record_set_id=normalized_record_set_id,
                normalization_run_record_id=run_id,
                canonical_schema_version_id=canonical_schema_version.canonical_schema_version_id,
                normalization_status=record_status,
                normalized_record_ids=(normalized_record.normalized_record_id,),
                created_at=self._clock(),
            )

        partial_record = None
        if run_status is NormalizationStatus.PARTIAL:
            partial_record = PartialNormalizationRecord(
                partial_normalization_record_id=PartialNormalizationRecordId(
                    _stable_id("partial_normalization", run_id.value, record_key.value)
                ),
                normalization_run_record_id=run_id,
                normalization_status=NormalizationStatus.PARTIAL,
                partial_normalization_status=PartialNormalizationStatus.PARTIAL_USEFUL
                if normalized_fields
                else PartialNormalizationStatus.PARTIAL_LIMITED,
                normalized_field_record_ids=tuple(
                    item.normalized_field_record_id for item in normalized_fields
                ),
                non_normalizable_field_record_ids=tuple(
                    item.non_normalizable_field_record_id for item in non_normalizable_fields
                ),
                rationale=NonNormalizableReason(
                    "The normalization run contains a mix of normalized and unresolved fields."
                ),
                created_at=self._clock(),
            )
            warnings.extend(
                self._build_warnings(
                    run_id=run_id,
                    scope_ref=NormalizationScopeRef.for_partial_normalization(
                        partial_record.partial_normalization_record_id
                    ),
                    warning_drafts=(
                        WarningDraft(
                            code="normalization.partial_record",
                            severity=WarningSeverity.MODERATE,
                            message="The record was only partially normalized under the available explicit rules.",
                        ),
                    ),
                )
            )

        replay_manifest = None
        if any((used_mapping_rule_ids, used_coercion_rule_ids, used_unit_rule_ids, used_currency_rule_ids)):
            replay_manifest = NormalizationReplayManifest(
                normalization_replay_manifest_id=NormalizationReplayManifestId(
                    _stable_id("normalization_replay", run_id.value, record_key.value)
                ),
                normalization_run_record_id=run_id,
                canonical_schema_version_id=canonical_schema_version.canonical_schema_version_id,
                source_provenance=run_provenance,
                field_mapping_rule_ids=tuple(_unique_ordered(used_mapping_rule_ids)),
                type_coercion_rule_ids=tuple(_unique_ordered(used_coercion_rule_ids)),
                unit_conversion_rule_ids=tuple(_unique_ordered(used_unit_rule_ids)),
                currency_conversion_rule_ids=tuple(_unique_ordered(used_currency_rule_ids)),
                normalized_record_set_id=None
                if normalized_record_set is None
                else normalized_record_set.normalized_record_set_id,
                replayability_status=replayability_status,
                created_at=self._clock(),
            )

        return NormalizationExecutionResult(
            canonical_schema_version=canonical_schema_version,
            normalization_run_record=normalization_run_record,
            normalized_record_set=normalized_record_set,
            normalized_record=normalized_record,
            normalized_field_records=tuple(normalized_fields),
            normalization_warning_records=tuple(warnings),
            non_normalizable_field_records=tuple(non_normalizable_fields),
            partial_normalization_record=partial_record,
            normalization_replay_manifest=replay_manifest,
        )

    def _build_normalized_field(
        self,
        *,
        run_id: NormalizationRunRecordId,
        normalized_record_id: NormalizedRecordId,
        field_input: ParsedFieldInput,
        field_definition: CanonicalFieldDefinition,
        mapping_rule_id: object,
        coercion_result: object,
        normalized_value_text: str | None,
        normalized_unit: object | None,
        normalized_currency: object | None,
        final_status: NormalizationStatus,
        unit_rule_id: object | None,
        currency_rule_id: object | None,
    ) -> NormalizedFieldRecord:
        value_triplet = ValueTriplet(
            raw_value=field_input.raw_value,
            parsed_value=field_input.parsed_value,
            normalized_value=None
            if normalized_value_text is None
            else NormalizedValue(normalized_value_text),
        )
        return NormalizedFieldRecord.for_canonical_field(
            normalized_field_record_id=self._normalized_field_id(
                run_id,
                field_input,
                field_definition,
            ),
            normalization_run_record_id=run_id,
            normalized_record_id=normalized_record_id,
            canonical_field_definition=field_definition,
            source_provenance=field_input.source_provenance,
            original_label=field_input.original_label,
            value_triplet=value_triplet,
            original_unit=field_input.original_unit,
            normalized_unit=normalized_unit,
            original_currency=field_input.original_currency,
            normalized_currency=normalized_currency,
            precision_descriptor=coercion_result.precision_descriptor,
            missingness_status=coercion_result.missingness_status,
            mixed_value_status=coercion_result.mixed_value_status,
            range_check_result=coercion_result.range_check_result,
            normalization_status=final_status,
            field_mapping_rule_id=mapping_rule_id,
            type_coercion_rule_id=coercion_result.type_coercion_rule_id,
            unit_conversion_rule_id=unit_rule_id,
            currency_conversion_rule_id=currency_rule_id,
            created_at=self._clock(),
        )

    def _build_non_normalizable_from_mapping(
        self,
        *,
        run_id: NormalizationRunRecordId,
        field_input: ParsedFieldInput,
        mapping_result: object,
    ) -> NonNormalizableFieldRecord:
        return NonNormalizableFieldRecord(
            non_normalizable_field_record_id=NonNormalizableFieldRecordId(
                _stable_id(
                    "non_normalizable_field",
                    run_id.value,
                    field_input.source_provenance.parsed_field_object_ref.value,
                )
            ),
            normalization_run_record_id=run_id,
            source_provenance=field_input.source_provenance,
            original_label=field_input.original_label,
            value_triplet=ValueTriplet(
                raw_value=field_input.raw_value,
                parsed_value=field_input.parsed_value,
                normalized_value=None,
            ),
            candidate_canonical_field_definition_id=None
            if mapping_result.canonical_field_definition is None
            else mapping_result.canonical_field_definition.canonical_field_definition_id,
            field_mapping_rule_id=mapping_result.field_mapping_rule_id,
            original_unit=field_input.original_unit,
            original_currency=field_input.original_currency,
            missingness_status=MissingnessStatus.NOT_NORMALIZABLE,
            mixed_value_status=field_input_mixed_status(field_input.parsed_value.value),
            reason=mapping_result.non_normalizable_reason
            or NonNormalizableReason("Field could not be normalized."),
            created_at=self._clock(),
        )

    def _build_non_normalizable_from_typed_field(
        self,
        *,
        run_id: NormalizationRunRecordId,
        field_input: ParsedFieldInput,
        field_definition: CanonicalFieldDefinition,
        mapping_rule_id: object | None,
        reason: NonNormalizableReason,
    ) -> NonNormalizableFieldRecord:
        return NonNormalizableFieldRecord(
            non_normalizable_field_record_id=NonNormalizableFieldRecordId(
                _stable_id(
                    "non_normalizable_field",
                    run_id.value,
                    field_input.source_provenance.parsed_field_object_ref.value,
                    field_definition.canonical_field_definition_id.value,
                )
            ),
            normalization_run_record_id=run_id,
            source_provenance=field_input.source_provenance,
            original_label=field_input.original_label,
            value_triplet=ValueTriplet(
                raw_value=field_input.raw_value,
                parsed_value=field_input.parsed_value,
                normalized_value=None,
            ),
            candidate_canonical_field_definition_id=field_definition.canonical_field_definition_id,
            field_mapping_rule_id=mapping_rule_id,
            original_unit=field_input.original_unit,
            original_currency=field_input.original_currency,
            missingness_status=MissingnessStatus.NOT_NORMALIZABLE,
            mixed_value_status=field_input_mixed_status(field_input.parsed_value.value),
            reason=reason,
            created_at=self._clock(),
        )

    def _build_warnings(
        self,
        *,
        run_id: NormalizationRunRecordId,
        scope_ref: NormalizationScopeRef,
        warning_drafts: Iterable[WarningDraft],
    ) -> tuple:
        return tuple(
            self._warning_builder.build(
                normalization_run_record_id=run_id,
                scope_ref=scope_ref,
                warning_draft=item,
            )
            for item in warning_drafts
        )

    def _normalized_field_id(
        self,
        run_id: NormalizationRunRecordId,
        field_input: ParsedFieldInput,
        field_definition: CanonicalFieldDefinition,
    ) -> NormalizedFieldRecordId:
        return NormalizedFieldRecordId(
            _stable_id(
                "normalized_field",
                run_id.value,
                field_input.source_provenance.parsed_field_object_ref.value,
                field_definition.canonical_field_definition_id.value,
            )
        )


def _field_warning_drafts(
    *,
    field_status: NormalizationStatus,
    coercion_warning_drafts: tuple[WarningDraft, ...],
) -> tuple[WarningDraft, ...]:
    drafts = list(coercion_warning_drafts)
    if field_status is NormalizationStatus.PARTIAL:
        drafts.append(
            WarningDraft(
                code="normalization.partial_field",
                severity=WarningSeverity.MODERATE,
                message="Field normalization completed only partially under the available explicit rules.",
            )
        )
    return tuple(drafts)


def _derive_common_provenance(field_inputs: tuple[ParsedFieldInput, ...]) -> ParsedSourceProvenance:
    first = field_inputs[0].source_provenance
    same_table_ref = first.parsed_table_object_ref
    for item in field_inputs[1:]:
        provenance = item.source_provenance
        if provenance.raw_asset_version_ref != first.raw_asset_version_ref:
            raise ValueError("All parsed field inputs in one normalization run must share raw_asset_version_ref.")
        if provenance.extraction_metadata_ref != first.extraction_metadata_ref:
            raise ValueError("All parsed field inputs in one normalization run must share extraction_metadata_ref.")
        if provenance.parsed_document_object_ref != first.parsed_document_object_ref:
            raise ValueError("All parsed field inputs in one normalization run must share parsed_document_object_ref.")
        if provenance.parser_strategy_ref != first.parser_strategy_ref:
            raise ValueError("All parsed field inputs in one normalization run must share parser_strategy_ref.")
        if provenance.parsed_table_object_ref != same_table_ref:
            same_table_ref = None
    return ParsedSourceProvenance(
        raw_asset_version_ref=first.raw_asset_version_ref,
        extraction_metadata_ref=first.extraction_metadata_ref,
        parsed_document_object_ref=first.parsed_document_object_ref,
        parser_strategy_ref=first.parser_strategy_ref,
        parsed_table_object_ref=same_table_ref,
        parsed_field_object_ref=None,
    )


def _derive_record_provenance(field_inputs: tuple[ParsedFieldInput, ...]) -> ParsedSourceProvenance:
    return _derive_common_provenance(field_inputs)


def _derive_record_status(
    normalized_fields: list[NormalizedFieldRecord],
) -> NormalizationStatus:
    if not normalized_fields:
        return NormalizationStatus.NON_NORMALIZABLE
    if any(item.normalization_status is not NormalizationStatus.COMPLETE for item in normalized_fields):
        return NormalizationStatus.PARTIAL
    return NormalizationStatus.COMPLETE


def _derive_run_status(
    normalized_fields: list[NormalizedFieldRecord],
    non_normalizable_fields: list[NonNormalizableFieldRecord],
) -> NormalizationStatus:
    if not normalized_fields and non_normalizable_fields:
        return NormalizationStatus.NON_NORMALIZABLE
    if non_normalizable_fields:
        return NormalizationStatus.PARTIAL
    return _derive_record_status(normalized_fields)


def _derive_replayability_status(run_status: NormalizationStatus) -> ReplayabilityStatus:
    if run_status is NormalizationStatus.COMPLETE:
        return ReplayabilityStatus.REPLAYABLE
    if run_status is NormalizationStatus.PARTIAL:
        return ReplayabilityStatus.PARTIALLY_REPLAYABLE
    return ReplayabilityStatus.NOT_REPLAYABLE


def _combine_statuses(
    left: NormalizationStatus,
    right: NormalizationStatus,
) -> NormalizationStatus:
    if left is NormalizationStatus.NON_NORMALIZABLE or right is NormalizationStatus.NON_NORMALIZABLE:
        return NormalizationStatus.PARTIAL
    if left is NormalizationStatus.PARTIAL or right is NormalizationStatus.PARTIAL:
        return NormalizationStatus.PARTIAL
    return NormalizationStatus.COMPLETE


def field_input_mixed_status(value: str):
    normalized = value.strip()
    if "-" in normalized and any(char.isdigit() for char in normalized):
        from ..domain.enums import MixedValueStatus

        return MixedValueStatus.RANGE_EXPRESSION
    from ..domain.enums import MixedValueStatus

    return MixedValueStatus.NOT_MIXED


def _unique_ordered(values: Iterable[object]) -> list[object]:
    ordered: list[object] = []
    seen: set[object] = set()
    for value in values:
        if value in seen:
            continue
        seen.add(value)
        ordered.append(value)
    return ordered


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"
