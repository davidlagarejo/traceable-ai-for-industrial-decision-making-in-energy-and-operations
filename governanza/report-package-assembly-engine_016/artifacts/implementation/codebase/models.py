"""Data objects emitted by motor_016."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class ReportPackage:
    record_id: str
    motor_016_id: str
    package_id: str
    package_type: str
    target_phase_ref: str
    phase_contract_refs: list[str]
    block_refs: list[str]
    block_manifest: list[dict[str, Any]]
    package_manifest: dict[str, Any]
    view_refs: list[str]
    technical_view_ref: str
    executive_view_ref: str
    version_record_refs: list[str]
    assembly_manifest: dict[str, Any]
    ordering_rule_ref: str
    validation_status: str
    validation_errors: list[dict[str, Any]]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: list[str]
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class TechnicalView:
    record_id: str
    motor_016_id: str
    view_id: str
    package_id: str
    view_type: str
    inclusion_rule_ref: str
    included_block_refs: list[str]
    excluded_block_refs: list[dict[str, Any]]
    ordering_rule_ref: str
    trace_index: dict[str, dict[str, Any]]
    view_manifest: dict[str, Any]
    validation_status: str
    validation_errors: list[dict[str, Any]]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: list[str]
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ExecutiveView:
    record_id: str
    motor_016_id: str
    view_id: str
    package_id: str
    view_type: str
    inclusion_rule_ref: str
    included_block_refs: list[str]
    excluded_block_refs: list[dict[str, Any]]
    ordering_rule_ref: str
    trace_index: dict[str, dict[str, Any]]
    view_manifest: dict[str, Any]
    validation_status: str
    validation_errors: list[dict[str, Any]]
    version_id: str
    created_at: str
    updated_at: str
    version_hash: str
    source_ref: list[str]
    produced_by_motor: str
    produced_at: str
    parent_id: str | None

    def to_dict(self) -> dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AssemblyResult:
    report_package: ReportPackage
    technical_view: TechnicalView | None
    executive_view: ExecutiveView | None

    def to_dict(self) -> dict[str, Any]:
        return {
            "report_package": self.report_package.to_dict(),
            "technical_view": (
                self.technical_view.to_dict() if self.technical_view is not None else None
            ),
            "executive_view": (
                self.executive_view.to_dict() if self.executive_view is not None else None
            ),
        }
