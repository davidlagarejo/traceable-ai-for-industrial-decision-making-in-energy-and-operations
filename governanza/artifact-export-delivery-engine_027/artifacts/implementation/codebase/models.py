"""Data objects emitted by motor_027."""

from __future__ import annotations

from dataclasses import asdict, dataclass, field as dataclass_field
from typing import Any


@dataclass(frozen=True)
class DeliveryBundle:
    bundle_id: str
    request_id: str
    destination_id: str
    delivery_mode: str
    bundle_path: str
    manifest_path: str
    file_count: int
    total_size_bytes: int
    checksum_algorithm: str
    compression: str
    created_at: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DeliveryManifest:
    manifest_id: str
    bundle_id: str
    request_id: str
    destination_id: str
    created_at: str
    files: list[dict[str, Any]]
    manifest_hash: str
    checksum_algorithm: str
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DeliveryReceipt:
    delivery_id: str
    request_id: str
    status: str
    created_at: str
    destination_id: str
    bundle_id: str | None
    manifest_id: str | None
    files_included: list[dict[str, Any]]
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    version_id: str
    version_hash: str
    source_ref: str
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class RejectionReport:
    rejection_id: str
    request_id: str | None
    status: str
    created_at: str
    destination_id: str | None
    errors: list[dict[str, Any]]
    warnings: list[dict[str, Any]]
    source_ref: str | None
    produced_by_motor: str
    produced_at: str

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class DeliveryResult:
    delivery_bundle: DeliveryBundle | None
    delivery_manifest: DeliveryManifest | None
    delivery_receipt: DeliveryReceipt
    rejection_report: RejectionReport | None = None
    degradation_signals: list[dict[str, Any]] = dataclass_field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return {
            "delivery_bundle": (
                self.delivery_bundle.to_dict()
                if self.delivery_bundle is not None
                else None
            ),
            "delivery_manifest": (
                self.delivery_manifest.to_dict()
                if self.delivery_manifest is not None
                else None
            ),
            "delivery_receipt": self.delivery_receipt.to_dict(),
            "rejection_report": (
                self.rejection_report.to_dict()
                if self.rejection_report is not None
                else None
            ),
            "degradation_signals": [dict(item) for item in self.degradation_signals],
        }
