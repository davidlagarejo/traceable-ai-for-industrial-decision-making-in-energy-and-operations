from __future__ import annotations

from collections.abc import Iterable
from typing import Any

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
from ..domain.enums import ParsingScopeKind
from ..domain.records import (
    ExtractionMetadataRecord,
    ParsingConfidenceRecord,
    ParsingFailureRecord,
    ParsingWarningRecord,
    ReplayManifestRecord,
    StructuralLocationRecord,
)
from ..domain.value_objects import (
    ExtractionMetadataRecordId,
    IngestionRequestRecordId,
    ParsedBlockObjectId,
    ParsedDocumentObjectId,
    ParsedFieldObjectId,
    ParsedTableObjectId,
    ParserStrategyRecordId,
    ParsingScopeRef,
    RawAssetRecordId,
    RawAssetVersionRecordId,
    RetrievalRecordId,
    StructuralLocationRecordId,
)


@dataclass(frozen=True, slots=True)
class ValidationContext:
    ingestion_request_records: tuple[IngestionRequestRecord, ...] = ()
    retrieval_records: tuple[RetrievalRecord, ...] = ()
    raw_asset_records: tuple[RawAssetRecord, ...] = ()
    raw_asset_version_records: tuple[RawAssetVersionRecord, ...] = ()
    parsed_document_objects: tuple[ParsedDocumentObject, ...] = ()
    parsed_table_objects: tuple[ParsedTableObject, ...] = ()
    parsed_field_objects: tuple[ParsedFieldObject, ...] = ()
    parsed_block_objects: tuple[ParsedBlockObject, ...] = ()
    structural_location_records: tuple[StructuralLocationRecord, ...] = ()
    extraction_metadata_records: tuple[ExtractionMetadataRecord, ...] = ()
    parsing_warning_records: tuple[ParsingWarningRecord, ...] = ()
    parsing_failure_records: tuple[ParsingFailureRecord, ...] = ()
    parsing_confidence_records: tuple[ParsingConfidenceRecord, ...] = ()
    parser_strategy_records: tuple[ParserStrategyRecord, ...] = ()
    replay_manifest_records: tuple[ReplayManifestRecord, ...] = ()

    @classmethod
    def from_iterables(
        cls,
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
    ) -> "ValidationContext":
        return cls(
            ingestion_request_records=tuple(ingestion_request_records),
            retrieval_records=tuple(retrieval_records),
            raw_asset_records=tuple(raw_asset_records),
            raw_asset_version_records=tuple(raw_asset_version_records),
            parsed_document_objects=tuple(parsed_document_objects),
            parsed_table_objects=tuple(parsed_table_objects),
            parsed_field_objects=tuple(parsed_field_objects),
            parsed_block_objects=tuple(parsed_block_objects),
            structural_location_records=tuple(structural_location_records),
            extraction_metadata_records=tuple(extraction_metadata_records),
            parsing_warning_records=tuple(parsing_warning_records),
            parsing_failure_records=tuple(parsing_failure_records),
            parsing_confidence_records=tuple(parsing_confidence_records),
            parser_strategy_records=tuple(parser_strategy_records),
            replay_manifest_records=tuple(replay_manifest_records),
        )

    @property
    def requests_by_id(self) -> dict[IngestionRequestRecordId, IngestionRequestRecord]:
        return {item.ingestion_request_record_id: item for item in self.ingestion_request_records}

    @property
    def retrievals_by_id(self) -> dict[RetrievalRecordId, RetrievalRecord]:
        return {item.retrieval_record_id: item for item in self.retrieval_records}

    @property
    def raw_assets_by_id(self) -> dict[RawAssetRecordId, RawAssetRecord]:
        return {item.raw_asset_record_id: item for item in self.raw_asset_records}

    @property
    def raw_versions_by_id(self) -> dict[RawAssetVersionRecordId, RawAssetVersionRecord]:
        return {item.raw_asset_version_record_id: item for item in self.raw_asset_version_records}

    @property
    def parsed_documents_by_id(self) -> dict[ParsedDocumentObjectId, ParsedDocumentObject]:
        return {item.parsed_document_object_id: item for item in self.parsed_document_objects}

    @property
    def parsed_tables_by_id(self) -> dict[ParsedTableObjectId, ParsedTableObject]:
        return {item.parsed_table_object_id: item for item in self.parsed_table_objects}

    @property
    def parsed_fields_by_id(self) -> dict[ParsedFieldObjectId, ParsedFieldObject]:
        return {item.parsed_field_object_id: item for item in self.parsed_field_objects}

    @property
    def parsed_blocks_by_id(self) -> dict[ParsedBlockObjectId, ParsedBlockObject]:
        return {item.parsed_block_object_id: item for item in self.parsed_block_objects}

    @property
    def locations_by_id(self) -> dict[StructuralLocationRecordId, StructuralLocationRecord]:
        return {item.structural_location_record_id: item for item in self.structural_location_records}

    @property
    def extractions_by_id(self) -> dict[ExtractionMetadataRecordId, ExtractionMetadataRecord]:
        return {item.extraction_metadata_record_id: item for item in self.extraction_metadata_records}

    @property
    def strategies_by_id(self) -> dict[ParserStrategyRecordId, ParserStrategyRecord]:
        return {item.parser_strategy_record_id: item for item in self.parser_strategy_records}

    def contains_scope_ref(self, scope_ref: ParsingScopeRef) -> bool:
        return self.object_for_scope(scope_ref) is not None

    def object_for_scope(self, scope_ref: ParsingScopeRef) -> Any | None:
        if scope_ref.scope_kind is ParsingScopeKind.RAW_ASSET_VERSION:
            return self.raw_versions_by_id.get(scope_ref.identifier)
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_DOCUMENT:
            return self.parsed_documents_by_id.get(scope_ref.identifier)
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_TABLE:
            return self.parsed_tables_by_id.get(scope_ref.identifier)
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_FIELD:
            return self.parsed_fields_by_id.get(scope_ref.identifier)
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_BLOCK:
            return self.parsed_blocks_by_id.get(scope_ref.identifier)
        if scope_ref.scope_kind is ParsingScopeKind.STRUCTURAL_LOCATION:
            return self.locations_by_id.get(scope_ref.identifier)
        return self.extractions_by_id.get(scope_ref.identifier)

    def raw_version_id_for_scope(self, scope_ref: ParsingScopeRef) -> RawAssetVersionRecordId | None:
        if scope_ref.scope_kind is ParsingScopeKind.RAW_ASSET_VERSION:
            return scope_ref.identifier
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_DOCUMENT:
            item = self.parsed_documents_by_id.get(scope_ref.identifier)
            return None if item is None else item.raw_asset_version_record_id
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_TABLE:
            item = self.parsed_tables_by_id.get(scope_ref.identifier)
            return None if item is None else item.raw_asset_version_record_id
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_FIELD:
            item = self.parsed_fields_by_id.get(scope_ref.identifier)
            return None if item is None else item.raw_asset_version_record_id
        if scope_ref.scope_kind is ParsingScopeKind.PARSED_BLOCK:
            item = self.parsed_blocks_by_id.get(scope_ref.identifier)
            return None if item is None else item.raw_asset_version_record_id
        if scope_ref.scope_kind is ParsingScopeKind.EXTRACTION_METADATA:
            item = self.extractions_by_id.get(scope_ref.identifier)
            return None if item is None else item.raw_asset_version_record_id
        return None
