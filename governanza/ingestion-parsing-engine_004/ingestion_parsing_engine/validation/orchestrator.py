from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import datetime, timezone
import hashlib

from .._compat import dataclass
from ..domain.entities import (
    IngestionRequestRecord,
    ParsedBlockObject,
    ParsedDocumentObject,
    ParsedFieldObject,
    ParsedTableObject,
    ParserStrategyRecord,
    RawAssetRecord,
    RawAssetVersionRecord,
    RetrievalRecord,
)
from ..domain.records import (
    ExtractionMetadataRecord,
    ParsingConfidenceRecord,
    ParsingFailureRecord,
    ParsingWarningRecord,
    ReplayManifestRecord,
    StructuralLocationRecord,
)
from .collector import ViolationCollector, ViolationDraft
from .confidence_validator import validate_parsing_confidence_record
from .context import ValidationContext
from .extraction_validator import validate_extraction_metadata_record
from .location_validator import validate_structural_location_record
from .parsed_validator import (
    validate_parsed_block_object,
    validate_parsed_document_object,
    validate_parsed_field_object,
    validate_parsed_table_object,
)
from .raw_validator import validate_raw_asset_record, validate_raw_asset_version_record
from .replay_validator import validate_replay_manifest_record
from .request_validator import validate_ingestion_request_record
from .results import ValidationOutcome, ValidationReport, ValidationRun, ValidationViolation
from .retrieval_validator import validate_retrieval_record
from .strategy_validator import validate_parser_strategy_record
from .warning_failure_validator import (
    validate_parsing_failure_record,
    validate_parsing_warning_record,
)


DEFAULT_VALIDATOR_VERSION = "0.1.0"


@dataclass(frozen=True, slots=True)
class ValidationArtifacts:
    target_refs: tuple[str, ...]


class BasicIngestionIntegrityValidator:
    def __init__(
        self,
        *,
        validator_version: str = DEFAULT_VALIDATOR_VERSION,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._validator_version = validator_version.strip()
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def validate_ingestion_request_record(
        self,
        request: IngestionRequestRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_request_ref(request))
        validate_ingestion_request_record(request, collector)
        return self._build_report(ValidationArtifacts((_request_ref(request),)), collector)

    def validate_retrieval_record(
        self,
        retrieval: RetrievalRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_retrieval_ref(retrieval))
        validate_retrieval_record(retrieval, collector, context=context)
        return self._build_report(ValidationArtifacts((_retrieval_ref(retrieval),)), collector)

    def validate_raw_asset_record(
        self,
        raw_asset: RawAssetRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_raw_asset_ref(raw_asset))
        validate_raw_asset_record(raw_asset, collector)
        return self._build_report(ValidationArtifacts((_raw_asset_ref(raw_asset),)), collector)

    def validate_raw_asset_version_record(
        self,
        raw_asset_version: RawAssetVersionRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_raw_asset_version_ref(raw_asset_version))
        validate_raw_asset_version_record(raw_asset_version, collector, context=context)
        return self._build_report(
            ValidationArtifacts((_raw_asset_version_ref(raw_asset_version),)),
            collector,
        )

    def validate_parsed_document_object(
        self,
        document: ParsedDocumentObject,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_parsed_document_ref(document))
        validate_parsed_document_object(document, collector, context=context)
        return self._build_report(ValidationArtifacts((_parsed_document_ref(document),)), collector)

    def validate_parsed_table_object(
        self,
        table: ParsedTableObject,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_parsed_table_ref(table))
        validate_parsed_table_object(table, collector, context=context)
        return self._build_report(ValidationArtifacts((_parsed_table_ref(table),)), collector)

    def validate_parsed_field_object(
        self,
        field: ParsedFieldObject,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_parsed_field_ref(field))
        validate_parsed_field_object(field, collector, context=context)
        return self._build_report(ValidationArtifacts((_parsed_field_ref(field),)), collector)

    def validate_parsed_block_object(
        self,
        block: ParsedBlockObject,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_parsed_block_ref(block))
        validate_parsed_block_object(block, collector, context=context)
        return self._build_report(ValidationArtifacts((_parsed_block_ref(block),)), collector)

    def validate_structural_location_record(
        self,
        location: StructuralLocationRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_location_ref(location))
        validate_structural_location_record(location, collector)
        return self._build_report(ValidationArtifacts((_location_ref(location),)), collector)

    def validate_extraction_metadata_record(
        self,
        metadata: ExtractionMetadataRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_extraction_ref(metadata))
        validate_extraction_metadata_record(metadata, collector, context=context)
        return self._build_report(ValidationArtifacts((_extraction_ref(metadata),)), collector)

    def validate_parsing_warning_record(
        self,
        warning: ParsingWarningRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_warning_ref(warning))
        validate_parsing_warning_record(warning, collector, context=context)
        return self._build_report(ValidationArtifacts((_warning_ref(warning),)), collector)

    def validate_parsing_failure_record(
        self,
        failure: ParsingFailureRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_failure_ref(failure))
        validate_parsing_failure_record(failure, collector, context=context)
        return self._build_report(ValidationArtifacts((_failure_ref(failure),)), collector)

    def validate_parsing_confidence_record(
        self,
        confidence: ParsingConfidenceRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_confidence_ref(confidence))
        validate_parsing_confidence_record(confidence, collector, context=context)
        return self._build_report(ValidationArtifacts((_confidence_ref(confidence),)), collector)

    def validate_parser_strategy_record(
        self,
        strategy: ParserStrategyRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_strategy_ref(strategy))
        validate_parser_strategy_record(strategy, collector)
        return self._build_report(ValidationArtifacts((_strategy_ref(strategy),)), collector)

    def validate_replay_manifest_record(
        self,
        manifest: ReplayManifestRecord,
        *,
        context: ValidationContext | None = None,
    ) -> ValidationReport:
        collector = ViolationCollector(_replay_ref(manifest))
        validate_replay_manifest_record(manifest, collector, context=context)
        return self._build_report(ValidationArtifacts((_replay_ref(manifest),)), collector)

    def validate_graph(
        self,
        *,
        ingestion_request_records: Iterable[IngestionRequestRecord] = (),
        retrieval_records: Iterable[RetrievalRecord] = (),
        raw_asset_records: Iterable[RawAssetRecord] = (),
        raw_asset_version_records: Iterable[RawAssetVersionRecord] = (),
        parsed_document_objects: Iterable[ParsedDocumentObject] = (),
        parsed_table_objects: Iterable[ParsedTableObject] = (),
        parsed_field_objects: Iterable[ParsedFieldObject] = (),
        parsed_block_objects: Iterable[ParsedBlockObject] = (),
        structural_location_records: Iterable[StructuralLocationRecord] = (),
        extraction_metadata_records: Iterable[ExtractionMetadataRecord] = (),
        parsing_warning_records: Iterable[ParsingWarningRecord] = (),
        parsing_failure_records: Iterable[ParsingFailureRecord] = (),
        parsing_confidence_records: Iterable[ParsingConfidenceRecord] = (),
        parser_strategy_records: Iterable[ParserStrategyRecord] = (),
        replay_manifest_records: Iterable[ReplayManifestRecord] = (),
    ) -> ValidationReport:
        ingestion_request_records = tuple(ingestion_request_records)
        retrieval_records = tuple(retrieval_records)
        raw_asset_records = tuple(raw_asset_records)
        raw_asset_version_records = tuple(raw_asset_version_records)
        parsed_document_objects = tuple(parsed_document_objects)
        parsed_table_objects = tuple(parsed_table_objects)
        parsed_field_objects = tuple(parsed_field_objects)
        parsed_block_objects = tuple(parsed_block_objects)
        structural_location_records = tuple(structural_location_records)
        extraction_metadata_records = tuple(extraction_metadata_records)
        parsing_warning_records = tuple(parsing_warning_records)
        parsing_failure_records = tuple(parsing_failure_records)
        parsing_confidence_records = tuple(parsing_confidence_records)
        parser_strategy_records = tuple(parser_strategy_records)
        replay_manifest_records = tuple(replay_manifest_records)

        context = ValidationContext.from_iterables(
            ingestion_request_records=ingestion_request_records,
            retrieval_records=retrieval_records,
            raw_asset_records=raw_asset_records,
            raw_asset_version_records=raw_asset_version_records,
            parsed_document_objects=parsed_document_objects,
            parsed_table_objects=parsed_table_objects,
            parsed_field_objects=parsed_field_objects,
            parsed_block_objects=parsed_block_objects,
            structural_location_records=structural_location_records,
            extraction_metadata_records=extraction_metadata_records,
            parsing_warning_records=parsing_warning_records,
            parsing_failure_records=parsing_failure_records,
            parsing_confidence_records=parsing_confidence_records,
            parser_strategy_records=parser_strategy_records,
            replay_manifest_records=replay_manifest_records,
        )
        collector = ViolationCollector("graph:ingestion")

        for item in ingestion_request_records:
            local = ViolationCollector(_request_ref(item))
            validate_ingestion_request_record(item, local)
            _merge_collector(collector, local)

        for item in raw_asset_records:
            local = ViolationCollector(_raw_asset_ref(item))
            validate_raw_asset_record(item, local)
            _merge_collector(collector, local)

        for item in retrieval_records:
            local = ViolationCollector(_retrieval_ref(item))
            validate_retrieval_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in parser_strategy_records:
            local = ViolationCollector(_strategy_ref(item))
            validate_parser_strategy_record(item, local)
            _merge_collector(collector, local)

        for item in raw_asset_version_records:
            local = ViolationCollector(_raw_asset_version_ref(item))
            validate_raw_asset_version_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in structural_location_records:
            local = ViolationCollector(_location_ref(item))
            validate_structural_location_record(item, local)
            _merge_collector(collector, local)

        for item in extraction_metadata_records:
            local = ViolationCollector(_extraction_ref(item))
            validate_extraction_metadata_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsed_document_objects:
            local = ViolationCollector(_parsed_document_ref(item))
            validate_parsed_document_object(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsed_table_objects:
            local = ViolationCollector(_parsed_table_ref(item))
            validate_parsed_table_object(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsed_block_objects:
            local = ViolationCollector(_parsed_block_ref(item))
            validate_parsed_block_object(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsed_field_objects:
            local = ViolationCollector(_parsed_field_ref(item))
            validate_parsed_field_object(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsing_warning_records:
            local = ViolationCollector(_warning_ref(item))
            validate_parsing_warning_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsing_failure_records:
            local = ViolationCollector(_failure_ref(item))
            validate_parsing_failure_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in parsing_confidence_records:
            local = ViolationCollector(_confidence_ref(item))
            validate_parsing_confidence_record(item, local, context=context)
            _merge_collector(collector, local)

        for item in replay_manifest_records:
            local = ViolationCollector(_replay_ref(item))
            validate_replay_manifest_record(item, local, context=context)
            _merge_collector(collector, local)

        target_refs = tuple(
            _unique_ordered(
                [
                    *(_request_ref(item) for item in ingestion_request_records),
                    *(_retrieval_ref(item) for item in retrieval_records),
                    *(_raw_asset_ref(item) for item in raw_asset_records),
                    *(_raw_asset_version_ref(item) for item in raw_asset_version_records),
                    *(_parsed_document_ref(item) for item in parsed_document_objects),
                    *(_parsed_table_ref(item) for item in parsed_table_objects),
                    *(_parsed_field_ref(item) for item in parsed_field_objects),
                    *(_parsed_block_ref(item) for item in parsed_block_objects),
                    *(_location_ref(item) for item in structural_location_records),
                    *(_extraction_ref(item) for item in extraction_metadata_records),
                    *(_warning_ref(item) for item in parsing_warning_records),
                    *(_failure_ref(item) for item in parsing_failure_records),
                    *(_confidence_ref(item) for item in parsing_confidence_records),
                    *(_strategy_ref(item) for item in parser_strategy_records),
                    *(_replay_ref(item) for item in replay_manifest_records),
                ]
            )
        ) or ("graph:ingestion",)

        return self._build_report(ValidationArtifacts(target_refs), collector)

    def _build_report(
        self,
        artifacts: ValidationArtifacts,
        collector: ViolationCollector,
    ) -> ValidationReport:
        outcome = _derive_outcome(collector)
        run_id = _stable_id(
            "ingestion_validation",
            self._validator_version,
            outcome.value,
            *artifacts.target_refs,
            *(_draft_signature(item) for item in collector.violations),
        )
        violations = tuple(
            ValidationViolation(
                violation_id=_stable_id(
                    "ingestion_violation",
                    run_id,
                    str(index),
                    draft.code.value,
                    draft.target_ref,
                    draft.field_ref or "nofield",
                ),
                code=draft.code.value,
                severity=draft.severity,
                message=draft.message,
                target_ref=draft.target_ref,
                field_ref=draft.field_ref,
                blocking=draft.blocking,
            )
            for index, draft in enumerate(collector.violations, start=1)
        )
        return ValidationReport(
            outcome=outcome,
            validation_run=ValidationRun(
                run_id=run_id,
                validator_version=self._validator_version,
                executed_at=self._clock(),
                target_refs=artifacts.target_refs,
            ),
            violations=violations,
        )


def _merge_collector(target: ViolationCollector, source: ViolationCollector) -> None:
    for item in source.violations:
        target.add(
            item.code,
            item.message,
            target_ref=item.target_ref,
            field_ref=item.field_ref,
            severity=item.severity,
            blocking=item.blocking,
        )


def _derive_outcome(collector: ViolationCollector) -> ValidationOutcome:
    if collector.has_errors:
        return ValidationOutcome.FAIL
    if collector.has_warnings:
        return ValidationOutcome.PASS_WITH_WARNINGS
    return ValidationOutcome.PASS


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _draft_signature(item: ViolationDraft) -> str:
    return "|".join(
        (
            item.code.value,
            item.severity.value,
            item.message,
            item.target_ref,
            item.field_ref or "nofield",
            "blocking" if item.blocking else "nonblocking",
        )
    )


def _request_ref(request: IngestionRequestRecord) -> str:
    return f"ingestion_request:{request.ingestion_request_record_id}"


def _retrieval_ref(retrieval: RetrievalRecord) -> str:
    return f"retrieval_record:{retrieval.retrieval_record_id}"


def _raw_asset_ref(raw_asset: RawAssetRecord) -> str:
    return f"raw_asset:{raw_asset.raw_asset_record_id}"


def _raw_asset_version_ref(raw_asset_version: RawAssetVersionRecord) -> str:
    return f"raw_asset_version:{raw_asset_version.raw_asset_version_record_id}"


def _parsed_document_ref(document: ParsedDocumentObject) -> str:
    return f"parsed_document:{document.parsed_document_object_id}"


def _parsed_table_ref(table: ParsedTableObject) -> str:
    return f"parsed_table:{table.parsed_table_object_id}"


def _parsed_field_ref(field: ParsedFieldObject) -> str:
    return f"parsed_field:{field.parsed_field_object_id}"


def _parsed_block_ref(block: ParsedBlockObject) -> str:
    return f"parsed_block:{block.parsed_block_object_id}"


def _location_ref(location: StructuralLocationRecord) -> str:
    return f"structural_location:{location.structural_location_record_id}"


def _extraction_ref(metadata: ExtractionMetadataRecord) -> str:
    return f"extraction_metadata:{metadata.extraction_metadata_record_id}"


def _warning_ref(warning: ParsingWarningRecord) -> str:
    return f"parsing_warning:{warning.parsing_warning_record_id}"


def _failure_ref(failure: ParsingFailureRecord) -> str:
    return f"parsing_failure:{failure.parsing_failure_record_id}"


def _confidence_ref(confidence: ParsingConfidenceRecord) -> str:
    return f"parsing_confidence:{confidence.parsing_confidence_record_id}"


def _strategy_ref(strategy: ParserStrategyRecord) -> str:
    return f"parser_strategy:{strategy.parser_strategy_record_id}"


def _replay_ref(manifest: ReplayManifestRecord) -> str:
    return f"replay_manifest:{manifest.replay_manifest_record_id}"


def _unique_ordered(values: Iterable[str]) -> list[str]:
    ordered: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value in seen:
            continue
        ordered.append(value)
        seen.add(value)
    return ordered
