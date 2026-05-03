from __future__ import annotations

from collections.abc import Callable
from datetime import datetime, timezone
import hashlib
import mimetypes
from pathlib import Path

from ..._compat import dataclass
from ...domain.entities import (
    IngestionRequestRecord,
    RawAssetRecord,
    RawAssetVersionRecord,
    RetrievalRecord,
)
from ...domain.enums import (
    RawAssetKind,
    RetrievalStatus,
    RightsRestrictionLevel,
    SourceFormatFamily,
)
from ...domain.value_objects import (
    ContentChecksum,
    ContentType,
    EndpointReference,
    IngestionRequestRecordId,
    PreservationPointer,
    RawAssetRecordId,
    RawAssetVersionRecordId,
    RequestFingerprint,
    RetrievalRecordId,
    SourceAccessPolicyRef,
    SourceAdapterRef,
    SourceIdRef,
    SourceVisibleVersion,
    UriReference,
)


def _stable_id(prefix: str, *parts: str) -> str:
    digest = hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()[:24]
    return f"{prefix}:{digest}"


def _checksum_bytes(raw_bytes: bytes) -> ContentChecksum:
    return ContentChecksum(f"sha256:{hashlib.sha256(raw_bytes).hexdigest()}")


def _content_type_for_format(source_format: SourceFormatFamily) -> ContentType:
    return {
        SourceFormatFamily.CSV: ContentType("text/csv"),
        SourceFormatFamily.JSON: ContentType("application/json"),
        SourceFormatFamily.API_JSON: ContentType("application/json"),
        SourceFormatFamily.API_TABULAR: ContentType("application/json"),
        SourceFormatFamily.HTML: ContentType("text/html"),
        SourceFormatFamily.TEXT_DOCUMENT: ContentType("text/plain"),
        SourceFormatFamily.PDF: ContentType("application/pdf"),
        SourceFormatFamily.XLSX: ContentType(
            "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        ),
        SourceFormatFamily.BINARY_DOCUMENT: ContentType("application/octet-stream"),
        SourceFormatFamily.UNKNOWN: ContentType("application/octet-stream"),
    }[source_format]


def _default_raw_asset_kind(source_format: SourceFormatFamily) -> RawAssetKind:
    return {
        SourceFormatFamily.CSV: RawAssetKind.CSV_FILE,
        SourceFormatFamily.JSON: RawAssetKind.JSON_PAYLOAD,
        SourceFormatFamily.API_JSON: RawAssetKind.API_RESPONSE,
        SourceFormatFamily.API_TABULAR: RawAssetKind.API_RESPONSE,
        SourceFormatFamily.HTML: RawAssetKind.HTML_PAGE,
        SourceFormatFamily.TEXT_DOCUMENT: RawAssetKind.TEXT_DOCUMENT,
        SourceFormatFamily.PDF: RawAssetKind.PDF_DOCUMENT,
        SourceFormatFamily.XLSX: RawAssetKind.XLSX_WORKBOOK,
        SourceFormatFamily.BINARY_DOCUMENT: RawAssetKind.BINARY_BLOB,
        SourceFormatFamily.UNKNOWN: RawAssetKind.BINARY_BLOB,
    }[source_format]


def _guess_format_from_path(path: Path) -> SourceFormatFamily:
    suffix = path.suffix.lower()
    return {
        ".csv": SourceFormatFamily.CSV,
        ".json": SourceFormatFamily.JSON,
        ".html": SourceFormatFamily.HTML,
        ".htm": SourceFormatFamily.HTML,
        ".txt": SourceFormatFamily.TEXT_DOCUMENT,
        ".pdf": SourceFormatFamily.PDF,
        ".xlsx": SourceFormatFamily.XLSX,
    }.get(suffix, SourceFormatFamily.UNKNOWN)


def _coerce_source_id_ref(value: SourceIdRef | str) -> SourceIdRef:
    return value if isinstance(value, SourceIdRef) else SourceIdRef(value)


def _coerce_access_policy_ref(value: SourceAccessPolicyRef | str) -> SourceAccessPolicyRef:
    return value if isinstance(value, SourceAccessPolicyRef) else SourceAccessPolicyRef(value)


def _coerce_source_visible_version(
    value: SourceVisibleVersion | str | None,
) -> SourceVisibleVersion | None:
    if value is None or isinstance(value, SourceVisibleVersion):
        return value
    return SourceVisibleVersion(value)


@dataclass(frozen=True, slots=True)
class CapturedRawAsset:
    ingestion_request_record: IngestionRequestRecord
    retrieval_record: RetrievalRecord
    raw_asset_record: RawAssetRecord
    raw_asset_version_record: RawAssetVersionRecord
    raw_bytes: bytes

    def __post_init__(self) -> None:
        object.__setattr__(self, "raw_bytes", bytes(self.raw_bytes))

    def decode_text(self, *, encoding: str | None = None) -> str:
        resolved_encoding = encoding or self.raw_asset_version_record.charset or "utf-8"
        return self.raw_bytes.decode(resolved_encoding, errors="replace")


class BasicSourceAdapter:
    def __init__(
        self,
        *,
        clock: Callable[[], datetime] | None = None,
    ) -> None:
        self._clock = clock or (lambda: datetime.now(timezone.utc))

    def capture_text_payload(
        self,
        *,
        source_id_ref: SourceIdRef | str,
        source_access_policy_ref: SourceAccessPolicyRef | str,
        text_payload: str,
        rights_restriction_level: RightsRestrictionLevel = RightsRestrictionLevel.PUBLIC,
        source_visible_version: SourceVisibleVersion | str | None = None,
        original_uri: str | None = None,
        charset: str = "utf-8",
    ) -> CapturedRawAsset:
        raw_bytes = text_payload.encode(charset)
        return self._capture_bytes(
            source_id_ref=_coerce_source_id_ref(source_id_ref),
            source_access_policy_ref=_coerce_access_policy_ref(source_access_policy_ref),
            raw_bytes=raw_bytes,
            raw_asset_kind=RawAssetKind.TEXT_DOCUMENT,
            declared_format=SourceFormatFamily.TEXT_DOCUMENT,
            rights_restriction_level=rights_restriction_level,
            source_visible_version=_coerce_source_visible_version(source_visible_version),
            original_uri=original_uri,
            charset=charset,
            source_adapter_ref=SourceAdapterRef("adapter:basic:text-memory"),
        )

    def capture_csv_content(
        self,
        *,
        source_id_ref: SourceIdRef | str,
        source_access_policy_ref: SourceAccessPolicyRef | str,
        csv_content: str,
        rights_restriction_level: RightsRestrictionLevel = RightsRestrictionLevel.PUBLIC,
        source_visible_version: SourceVisibleVersion | str | None = None,
        original_uri: str | None = None,
        charset: str = "utf-8",
    ) -> CapturedRawAsset:
        raw_bytes = csv_content.encode(charset)
        return self._capture_bytes(
            source_id_ref=_coerce_source_id_ref(source_id_ref),
            source_access_policy_ref=_coerce_access_policy_ref(source_access_policy_ref),
            raw_bytes=raw_bytes,
            raw_asset_kind=RawAssetKind.CSV_FILE,
            declared_format=SourceFormatFamily.CSV,
            rights_restriction_level=rights_restriction_level,
            source_visible_version=_coerce_source_visible_version(source_visible_version),
            original_uri=original_uri,
            charset=charset,
            source_adapter_ref=SourceAdapterRef("adapter:basic:csv-memory"),
        )

    def capture_json_payload(
        self,
        *,
        source_id_ref: SourceIdRef | str,
        source_access_policy_ref: SourceAccessPolicyRef | str,
        json_payload: str,
        rights_restriction_level: RightsRestrictionLevel = RightsRestrictionLevel.PUBLIC,
        source_visible_version: SourceVisibleVersion | str | None = None,
        original_uri: str | None = None,
        charset: str = "utf-8",
    ) -> CapturedRawAsset:
        raw_bytes = json_payload.encode(charset)
        return self._capture_bytes(
            source_id_ref=_coerce_source_id_ref(source_id_ref),
            source_access_policy_ref=_coerce_access_policy_ref(source_access_policy_ref),
            raw_bytes=raw_bytes,
            raw_asset_kind=RawAssetKind.JSON_PAYLOAD,
            declared_format=SourceFormatFamily.JSON,
            rights_restriction_level=rights_restriction_level,
            source_visible_version=_coerce_source_visible_version(source_visible_version),
            original_uri=original_uri,
            charset=charset,
            source_adapter_ref=SourceAdapterRef("adapter:basic:json-memory"),
        )

    def capture_html_content(
        self,
        *,
        source_id_ref: SourceIdRef | str,
        source_access_policy_ref: SourceAccessPolicyRef | str,
        html_content: str,
        rights_restriction_level: RightsRestrictionLevel = RightsRestrictionLevel.PUBLIC,
        source_visible_version: SourceVisibleVersion | str | None = None,
        original_uri: str | None = None,
        charset: str = "utf-8",
    ) -> CapturedRawAsset:
        raw_bytes = html_content.encode(charset)
        return self._capture_bytes(
            source_id_ref=_coerce_source_id_ref(source_id_ref),
            source_access_policy_ref=_coerce_access_policy_ref(source_access_policy_ref),
            raw_bytes=raw_bytes,
            raw_asset_kind=RawAssetKind.HTML_PAGE,
            declared_format=SourceFormatFamily.HTML,
            rights_restriction_level=rights_restriction_level,
            source_visible_version=_coerce_source_visible_version(source_visible_version),
            original_uri=original_uri,
            charset=charset,
            source_adapter_ref=SourceAdapterRef("adapter:basic:html-memory"),
        )

    def capture_local_file(
        self,
        *,
        source_id_ref: SourceIdRef | str,
        source_access_policy_ref: SourceAccessPolicyRef | str,
        file_path: str | Path,
        declared_format: SourceFormatFamily | None = None,
        raw_asset_kind: RawAssetKind | None = None,
        rights_restriction_level: RightsRestrictionLevel = RightsRestrictionLevel.PUBLIC,
        source_visible_version: SourceVisibleVersion | str | None = None,
        charset: str | None = None,
    ) -> CapturedRawAsset:
        path = Path(file_path).expanduser().resolve()
        raw_bytes = path.read_bytes()
        detected_format = declared_format or _guess_format_from_path(path)
        resolved_raw_asset_kind = raw_asset_kind or _default_raw_asset_kind(detected_format)
        guessed_content_type, _ = mimetypes.guess_type(path.name)
        return self._capture_bytes(
            source_id_ref=_coerce_source_id_ref(source_id_ref),
            source_access_policy_ref=_coerce_access_policy_ref(source_access_policy_ref),
            raw_bytes=raw_bytes,
            raw_asset_kind=resolved_raw_asset_kind,
            declared_format=detected_format,
            rights_restriction_level=rights_restriction_level,
            source_visible_version=_coerce_source_visible_version(source_visible_version),
            original_uri=path.as_uri(),
            charset=charset,
            source_adapter_ref=SourceAdapterRef("adapter:basic:local-file"),
            content_type=(
                _content_type_for_format(detected_format)
                if guessed_content_type is None
                else ContentType(guessed_content_type)
            ),
            raw_preservation_pointer=PreservationPointer(path.as_uri()),
        )

    def _capture_bytes(
        self,
        *,
        source_id_ref: SourceIdRef,
        source_access_policy_ref: SourceAccessPolicyRef,
        raw_bytes: bytes,
        raw_asset_kind: RawAssetKind,
        declared_format: SourceFormatFamily,
        rights_restriction_level: RightsRestrictionLevel,
        source_visible_version: SourceVisibleVersion | None,
        original_uri: str | None,
        charset: str | None,
        source_adapter_ref: SourceAdapterRef,
        content_type: ContentType | None = None,
        raw_preservation_pointer: PreservationPointer | None = None,
    ) -> CapturedRawAsset:
        now = self._clock()
        raw_bytes = bytes(raw_bytes)
        normalized_original_uri = original_uri or (
            f"memory://{source_id_ref.value}/{declared_format.value}/"
            f"{hashlib.sha256(raw_bytes).hexdigest()[:12]}"
        )
        original_uri_ref = UriReference(normalized_original_uri)
        request_fingerprint = RequestFingerprint(
            _stable_id(
                "request_fingerprint",
                source_id_ref.value,
                source_access_policy_ref.value,
                raw_asset_kind.value,
                declared_format.value,
                normalized_original_uri,
            )
        )
        ingestion_request_record = IngestionRequestRecord(
            ingestion_request_record_id=IngestionRequestRecordId(
                _stable_id(
                    "ingestion_request",
                    request_fingerprint.value,
                    normalized_original_uri,
                )
            ),
            source_id_ref=source_id_ref,
            source_access_policy_ref=source_access_policy_ref,
            raw_asset_kind=raw_asset_kind,
            declared_format=declared_format,
            rights_restriction_level=rights_restriction_level,
            request_fingerprint=request_fingerprint,
            original_uri=original_uri_ref,
            endpoint_reference=None,
            requested_at=now,
        )
        raw_asset_record = RawAssetRecord(
            raw_asset_record_id=RawAssetRecordId(
                _stable_id(
                    "raw_asset",
                    source_id_ref.value,
                    raw_asset_kind.value,
                    declared_format.value,
                    normalized_original_uri,
                )
            ),
            source_id_ref=source_id_ref,
            source_access_policy_ref=source_access_policy_ref,
            raw_asset_kind=raw_asset_kind,
            declared_format=declared_format,
            rights_restriction_level=rights_restriction_level,
            original_uri=original_uri_ref,
            endpoint_reference=None,
            created_at=now,
        )
        checksum = _checksum_bytes(raw_bytes)
        retrieval_record = RetrievalRecord(
            retrieval_record_id=RetrievalRecordId(
                _stable_id(
                    "retrieval",
                    ingestion_request_record.ingestion_request_record_id.value,
                    source_adapter_ref.value,
                    checksum.value,
                )
            ),
            ingestion_request_record_id=ingestion_request_record.ingestion_request_record_id,
            raw_asset_record_id=raw_asset_record.raw_asset_record_id,
            source_adapter_ref=source_adapter_ref,
            retrieval_status=RetrievalStatus.SUCCEEDED,
            request_fingerprint=request_fingerprint,
            response_status_code=None,
            retrieval_started_at=now,
            retrieval_completed_at=now,
        )
        raw_asset_version_record = RawAssetVersionRecord(
            raw_asset_version_record_id=RawAssetVersionRecordId(
                _stable_id(
                    "raw_asset_version",
                    raw_asset_record.raw_asset_record_id.value,
                    checksum.value,
                )
            ),
            raw_asset_record_id=raw_asset_record.raw_asset_record_id,
            retrieval_record_id=retrieval_record.retrieval_record_id,
            content_checksum=checksum,
            content_type=content_type or _content_type_for_format(declared_format),
            content_length=len(raw_bytes),
            detected_format=declared_format,
            source_visible_version=source_visible_version,
            raw_preservation_pointer=raw_preservation_pointer
            or PreservationPointer(
                f"memory://raw/{raw_asset_record.raw_asset_record_id.value}/"
                f"{checksum.value.split(':', 1)[-1][:24]}"
            ),
            charset=charset,
            captured_at=now,
        )
        return CapturedRawAsset(
            ingestion_request_record=ingestion_request_record,
            retrieval_record=retrieval_record,
            raw_asset_record=raw_asset_record,
            raw_asset_version_record=raw_asset_version_record,
            raw_bytes=raw_bytes,
        )
