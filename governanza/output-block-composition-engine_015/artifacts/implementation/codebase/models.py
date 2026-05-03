"""Data objects emitted by motor_015."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class OutputBlock:
    block_id: str
    motor_id: str
    phase_id: str
    block_type: str
    visible_payload: dict[str, Any]
    source_inference_ids: list[str]
    phase_contract_ref: str
    contract_version: str
    version_refs: list[str]
    lineage_refs: list[str]
    trace_id: str
    rule_version: str
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
class BlockTrace:
    trace_id: str
    block_id: str
    motor_id: str
    segment_refs: list[dict[str, Any]]
    source_inference_ids: list[str]
    version_refs: list[str]
    lineage_refs: list[str]
    phase_contract_ref: str
    contract_version: str
    rule_version: str
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
class CompositionRecord:
    composition_id: str
    motor_id: str
    input_refs: list[str]
    accepted_refs: list[str]
    rejected_refs: list[dict[str, Any]]
    emitted_block_ids: list[str]
    trace_ids: list[str]
    phase_contract_refs: list[str]
    version_refs: list[str]
    rule_version: str
    status: str
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
class CompositionResult:
    output_blocks: list[OutputBlock]
    block_traces: list[BlockTrace]
    composition_log: list[CompositionRecord]

    def to_dict(self) -> dict[str, Any]:
        return {
            "output_blocks": [item.to_dict() for item in self.output_blocks],
            "block_traces": [item.to_dict() for item in self.block_traces],
            "composition_log": [item.to_dict() for item in self.composition_log],
        }
