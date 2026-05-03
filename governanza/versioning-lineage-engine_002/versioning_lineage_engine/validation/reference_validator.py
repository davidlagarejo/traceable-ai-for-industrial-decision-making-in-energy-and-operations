from __future__ import annotations

from ..domain.entities import ReferenceVersionRecord
from ..domain.enums import ReferenceKind
from ..domain.value_objects import Fingerprint, ReferenceVersionRecordId, StableKey
from .collector import ViolationCollector
from .rules import RuleCode


def validate_reference_version_record(
    record: ReferenceVersionRecord,
    collector: ViolationCollector,
) -> None:
    if not isinstance(record.reference_version_record_id, ReferenceVersionRecordId):
        collector.add(
            RuleCode.REFERENCE_ID_INVALID,
            "reference_version_record_id must be a ReferenceVersionRecordId.",
        )
    if not isinstance(record.reference_kind, ReferenceKind):
        collector.add(
            RuleCode.REFERENCE_KIND_INVALID,
            "reference_kind must be a supported ReferenceKind enum value.",
            field_ref="reference_kind",
        )
    if not isinstance(record.reference_key, StableKey) or not record.version_label.strip():
        collector.add(
            RuleCode.REFERENCE_VERSION_EMPTY,
            "Reference version records must carry a stable key and explicit version label.",
            field_ref="version_label",
        )
    if not isinstance(record.content_fingerprint, Fingerprint):
        collector.add(
            RuleCode.REFERENCE_VERSION_EMPTY,
            "Reference version records must carry a content fingerprint.",
            field_ref="content_fingerprint",
        )
