from __future__ import annotations

from ..domain.entities import RetrievalRecord
from ..domain.enums import RetrievalStatus
from .collector import ViolationCollector
from .context import ValidationContext
from .rules import RuleCode


def validate_retrieval_record(
    retrieval: RetrievalRecord,
    collector: ViolationCollector,
    *,
    context: ValidationContext | None = None,
) -> None:
    if retrieval.retrieval_status is not RetrievalStatus.SUCCEEDED:
        collector.add(
            RuleCode.RETRIEVAL_NON_SUCCESS_DECLARED,
            f"Retrieval declares non-success status {retrieval.retrieval_status.value}.",
            field_ref="retrieval_status",
        )

    if context is None:
        return

    request = context.requests_by_id.get(retrieval.ingestion_request_record_id)
    if request is None:
        collector.add(
            RuleCode.RETRIEVAL_REQUEST_REFERENCE_INVALID,
            "RetrievalRecord references an unknown ingestion_request_record.",
            field_ref="ingestion_request_record_id",
        )

    raw_asset = context.raw_assets_by_id.get(retrieval.raw_asset_record_id)
    if raw_asset is None:
        collector.add(
            RuleCode.RETRIEVAL_RAW_ASSET_REFERENCE_INVALID,
            "RetrievalRecord references an unknown raw_asset_record.",
            field_ref="raw_asset_record_id",
        )

    if request is not None and retrieval.request_fingerprint != request.request_fingerprint:
        collector.add(
            RuleCode.RETRIEVAL_REQUEST_FINGERPRINT_MISMATCH,
            "RetrievalRecord.request_fingerprint does not match its ingestion request.",
            field_ref="request_fingerprint",
        )

    if request is not None and raw_asset is not None:
        mismatches: list[str] = []
        if raw_asset.source_id_ref != request.source_id_ref:
            mismatches.append("source_id_ref")
        if raw_asset.source_access_policy_ref != request.source_access_policy_ref:
            mismatches.append("source_access_policy_ref")
        if raw_asset.raw_asset_kind != request.raw_asset_kind:
            mismatches.append("raw_asset_kind")
        if raw_asset.declared_format != request.declared_format:
            mismatches.append("declared_format")
        if raw_asset.rights_restriction_level != request.rights_restriction_level:
            mismatches.append("rights_restriction_level")
        if raw_asset.original_uri != request.original_uri:
            mismatches.append("original_uri")
        if raw_asset.endpoint_reference != request.endpoint_reference:
            mismatches.append("endpoint_reference")
        if mismatches:
            collector.add(
                RuleCode.RETRIEVAL_REQUEST_RAW_MISMATCH,
                (
                    "RetrievalRecord links a raw asset that diverges from its ingestion request on: "
                    + ", ".join(mismatches)
                    + "."
                ),
            )
