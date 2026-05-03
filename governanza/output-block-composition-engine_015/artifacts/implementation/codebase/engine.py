"""Deterministic implementation for motor_015.

The engine composes atomic visible output blocks from governed inference
records, supplied phase contracts, and resolvable version records. It does not
assemble reports, render documents, create new claims, or mutate upstream
objects.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import copy
import hashlib
import json
from typing import Any

from .errors import OutputBlockCompositionError
from .models import BlockTrace, CompositionRecord, CompositionResult, OutputBlock


MOTOR_ID = "motor_015"
DEFAULT_RULE_VERSION = "m015-rules-v1"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
REQUIRED_INFERENCE_TEXT_FIELDS = (
    "inference_id",
    "case_id",
    "phase_id",
    "phase_contract_ref",
    "contract_version",
    "rule_version",
    "created_at",
)
REQUIRED_ALLOWED_OUTPUTS = frozenset(
    {"output_block", "block_trace", "composition_log"}
)
FORBIDDEN_VISIBLE_FIELDS = frozenset(
    {
        "appendix",
        "audience_hint",
        "dashboard",
        "display_order",
        "document_outline",
        "executive_summary",
        "final_report",
        "html",
        "layout_hint",
        "layout_hints",
        "pagination",
        "pdf",
        "recommended_section",
        "rendered_document",
        "rendered_fragment",
        "report",
        "report_outline",
        "report_package",
        "section_order",
        "slide",
        "technical_view",
    }
)


@dataclass(frozen=True)
class _ContractContext:
    raw: Mapping[str, Any]
    contract_ref: str
    phase_id: str
    contract_version: str
    allowed_visible_fields: list[str]
    block_type_map: Mapping[str, Any]


@dataclass(frozen=True)
class _AcceptedCandidate:
    input_ref: str
    inference_id: str
    phase_id: str
    phase_contract_ref: str
    contract_version: str
    block_type: str
    visible_payload: dict[str, Any]
    version_refs: list[str]
    lineage_refs: list[str]


class OutputBlockCompositionEngine:
    """Core deterministic interface for Output Block Composition Engine."""

    def __init__(
        self,
        *,
        rule_version: str = DEFAULT_RULE_VERSION,
        produced_at: str = DEFAULT_PRODUCED_AT,
    ) -> None:
        self.rule_version = _require_text(rule_version, "rule_version")
        self.produced_at = _require_text(produced_at, "produced_at")

    def run(
        self,
        *,
        inference_records: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        version_records: Sequence[Mapping[str, Any]],
    ) -> CompositionResult:
        """Compose a deterministic batch of output blocks, traces, and log."""

        inference_items = _as_record_list("inference_records", inference_records)
        contract_items = _as_record_list("phase_contracts", phase_contracts)
        version_items = _as_record_list("version_records", version_records)
        contract_index = self._index_contracts(contract_items)
        version_index = self._index_versions(version_items)
        duplicate_ids = _duplicate_inference_ids(inference_items)

        accepted: list[_AcceptedCandidate] = []
        rejected: list[dict[str, Any]] = []

        sorted_inferences = sorted(
            enumerate(inference_items),
            key=lambda item: (_input_ref(item[1]), _stable_json(item[1]), item[0]),
        )
        for original_index, inference in sorted_inferences:
            candidate, rejection = self._validate_candidate(
                inference=inference,
                input_index=original_index,
                contract_index=contract_index,
                version_index=version_index,
                duplicate_ids=duplicate_ids,
            )
            if rejection is not None:
                rejected.append(rejection)
            elif candidate is not None:
                accepted.append(candidate)

        output_blocks: list[OutputBlock] = []
        block_traces: list[BlockTrace] = []
        for candidate in sorted(accepted, key=lambda item: item.input_ref):
            block, trace = self._emit_candidate(candidate)
            output_blocks.append(block)
            block_traces.append(trace)

        if not inference_items:
            rejected.append(
                _rejection(
                    input_ref="batch:empty",
                    code="EMPTY_INPUT_BATCH",
                    reason="inference_records must contain at least one record",
                )
            )

        composition = self._emit_composition_record(
            input_refs=sorted(_input_ref(item) for item in inference_items),
            accepted_refs=[item.input_ref for item in sorted(accepted, key=lambda i: i.input_ref)],
            rejected_refs=sorted(
                rejected,
                key=lambda item: (
                    str(item.get("input_ref", "")),
                    str(item.get("rejection_code", "")),
                    str(item.get("rejection_reason", "")),
                ),
            ),
            output_blocks=output_blocks,
            block_traces=block_traces,
            phase_contract_refs=sorted(
                _unique_texts(
                    [
                        item.phase_contract_ref
                        for item in accepted
                    ]
                    + [
                        str(entry.get("phase_contract_ref", ""))
                        for entry in rejected
                    ]
                )
            ),
            version_refs=sorted(
                _unique_texts(
                    [
                        version_ref
                        for item in accepted
                        for version_ref in item.version_refs
                    ]
                    + [
                        version_ref
                        for entry in rejected
                        for version_ref in _string_list(entry.get("version_refs"))
                    ]
                )
            ),
        )

        return CompositionResult(
            output_blocks=output_blocks,
            block_traces=block_traces,
            composition_log=[composition],
        )

    def compose(
        self,
        *,
        inference_records: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        version_records: Sequence[Mapping[str, Any]],
    ) -> CompositionResult:
        """Alias for callers that name the operation by the motor purpose."""

        return self.run(
            inference_records=inference_records,
            phase_contracts=phase_contracts,
            version_records=version_records,
        )

    def _index_contracts(
        self, phase_contracts: list[Mapping[str, Any]]
    ) -> dict[str, list[Mapping[str, Any]]]:
        result: dict[str, list[Mapping[str, Any]]] = {}
        for contract in phase_contracts:
            contract_ref = _contract_ref(contract)
            if contract_ref:
                result.setdefault(contract_ref, []).append(contract)
        return result

    def _index_versions(
        self, version_records: list[Mapping[str, Any]]
    ) -> dict[str, list[Mapping[str, Any]]]:
        result: dict[str, list[Mapping[str, Any]]] = {}
        for version_record in version_records:
            object_ref = _text(version_record.get("object_ref"))
            if object_ref:
                result.setdefault(object_ref, []).append(version_record)
        return result

    def _validate_candidate(
        self,
        *,
        inference: Mapping[str, Any],
        input_index: int,
        contract_index: Mapping[str, list[Mapping[str, Any]]],
        version_index: Mapping[str, list[Mapping[str, Any]]],
        duplicate_ids: set[str],
    ) -> tuple[_AcceptedCandidate | None, dict[str, Any] | None]:
        input_ref = _input_ref(inference)
        malformed_fields = self._malformed_inference_fields(inference)
        inference_id = _text(inference.get("inference_id"))
        if inference_id in duplicate_ids:
            malformed_fields.append("inference_id")
        if malformed_fields:
            return None, _rejection(
                input_ref=input_ref,
                code="MALFORMED_INFERENCE_RECORD",
                reason="invalid required fields: " + ", ".join(sorted(set(malformed_fields))),
                phase_contract_ref=_text(inference.get("phase_contract_ref")),
                contract_version=_text(inference.get("contract_version")),
                fields=sorted(set(malformed_fields)),
                input_index=input_index,
            )

        contract_ref = _text(inference.get("phase_contract_ref"))
        contract_candidates = contract_index.get(contract_ref, [])
        if not contract_candidates:
            return None, _rejection(
                input_ref=input_ref,
                code="MISSING_TRACEABILITY",
                reason=f"phase_contract_ref {contract_ref!r} cannot be resolved",
                phase_contract_ref=contract_ref,
                contract_version=_text(inference.get("contract_version")),
                input_index=input_index,
            )
        if len({_stable_json(item) for item in contract_candidates}) > 1:
            return None, _rejection(
                input_ref=input_ref,
                code="PHASE_CONTRACT_VIOLATION",
                reason=f"phase_contract_ref {contract_ref!r} resolves to conflicting contracts",
                phase_contract_ref=contract_ref,
                contract_version=_text(inference.get("contract_version")),
                input_index=input_index,
            )

        contract = self._parse_contract(contract_candidates[0], input_ref)
        contract_rejection = self._validate_contract_against_inference(
            contract, inference, input_ref, input_index
        )
        if contract_rejection is not None:
            return None, contract_rejection

        block_type, block_rejection = self._block_type_for_inference(
            contract, inference, input_ref, input_index
        )
        if block_rejection is not None:
            return None, block_rejection

        visible_payload, payload_rejection = self._visible_payload(
            contract, inference, input_ref, input_index
        )
        if payload_rejection is not None:
            return None, payload_rejection

        version_refs, lineage_refs, version_rejection = self._resolve_versions(
            inference=inference,
            version_records=version_index.get(inference_id, []),
            input_ref=input_ref,
            input_index=input_index,
        )
        if version_rejection is not None:
            return None, version_rejection

        return (
            _AcceptedCandidate(
                input_ref=input_ref,
                inference_id=inference_id,
                phase_id=_text(inference.get("phase_id")),
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                block_type=block_type,
                visible_payload=visible_payload,
                version_refs=version_refs,
                lineage_refs=lineage_refs,
            ),
            None,
        )

    def _malformed_inference_fields(self, inference: Mapping[str, Any]) -> list[str]:
        fields: list[str] = []
        for field_name in REQUIRED_INFERENCE_TEXT_FIELDS:
            if not _text(inference.get(field_name)):
                fields.append(field_name)
        lineage_refs = inference.get("lineage_refs")
        if not isinstance(lineage_refs, Sequence) or isinstance(
            lineage_refs, (str, bytes)
        ):
            fields.append("lineage_refs")
        elif not [_text(item) for item in lineage_refs if _text(item)]:
            fields.append("lineage_refs")
        return fields

    def _parse_contract(
        self, contract: Mapping[str, Any], input_ref: str
    ) -> _ContractContext:
        contract_ref = _contract_ref(contract)
        if not contract_ref:
            raise OutputBlockCompositionError(
                code="PHASE_CONTRACT_VIOLATION",
                message=f"contract for {input_ref} has no contract_ref",
                field="phase_contracts.contract_ref",
            )
        return _ContractContext(
            raw=contract,
            contract_ref=contract_ref,
            phase_id=_text(contract.get("phase_id")),
            contract_version=_text(
                contract.get("contract_version") or contract.get("version")
            ),
            allowed_visible_fields=_string_list(
                contract.get("allowed_visible_fields")
            ),
            block_type_map=_mapping(contract.get("block_type_map")),
        )

    def _validate_contract_against_inference(
        self,
        contract: _ContractContext,
        inference: Mapping[str, Any],
        input_ref: str,
        input_index: int,
    ) -> dict[str, Any] | None:
        allowed_inputs = set(_string_list(contract.raw.get("allowed_inputs")))
        if "inference_records" not in allowed_inputs:
            return _rejection(
                input_ref=input_ref,
                code="PHASE_CONTRACT_VIOLATION",
                reason="phase contract does not authorize inference_records input",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        allowed_outputs = set(_string_list(contract.raw.get("allowed_outputs")))
        missing_outputs = sorted(REQUIRED_ALLOWED_OUTPUTS - allowed_outputs)
        if missing_outputs:
            return _rejection(
                input_ref=input_ref,
                code="PHASE_CONTRACT_VIOLATION",
                reason="phase contract omits required outputs: "
                + ", ".join(missing_outputs),
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        inference_phase_id = _text(inference.get("phase_id"))
        if contract.phase_id and contract.phase_id != inference_phase_id:
            return _rejection(
                input_ref=input_ref,
                code="CONTRACT_DRIFT",
                reason="inference phase_id does not match phase contract",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        inference_contract_version = _text(inference.get("contract_version"))
        if contract.contract_version != inference_contract_version:
            return _rejection(
                input_ref=input_ref,
                code="CONTRACT_DRIFT",
                reason="inference contract_version does not match phase contract",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        if not contract.allowed_visible_fields:
            return _rejection(
                input_ref=input_ref,
                code="PHASE_CONTRACT_VIOLATION",
                reason="phase contract declares no allowed_visible_fields",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        return None

    def _block_type_for_inference(
        self,
        contract: _ContractContext,
        inference: Mapping[str, Any],
        input_ref: str,
        input_index: int,
    ) -> tuple[str, dict[str, Any] | None]:
        inference_category = _text(inference.get("inference_category"))
        if not inference_category or inference_category not in contract.block_type_map:
            return "", _rejection(
                input_ref=input_ref,
                code="UNSUPPORTED_BLOCK_MAPPING",
                reason=f"inference_category {inference_category!r} has no block_type mapping",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        block_type = _text(contract.block_type_map.get(inference_category))
        if not block_type:
            return "", _rejection(
                input_ref=input_ref,
                code="UNSUPPORTED_BLOCK_MAPPING",
                reason=f"inference_category {inference_category!r} maps to an empty block_type",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        allowed_block_types = set(_string_list(contract.raw.get("allowed_block_types")))
        if allowed_block_types and block_type not in allowed_block_types:
            return "", _rejection(
                input_ref=input_ref,
                code="CONTRACT_DRIFT",
                reason=f"block_type {block_type!r} is not allowed by the phase contract",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        return block_type, None

    def _visible_payload(
        self,
        contract: _ContractContext,
        inference: Mapping[str, Any],
        input_ref: str,
        input_index: int,
    ) -> tuple[dict[str, Any], dict[str, Any] | None]:
        payload: dict[str, Any] = {}
        for field_name in contract.allowed_visible_fields:
            output_key = _payload_key(field_name)
            if field_name in FORBIDDEN_VISIBLE_FIELDS or output_key in FORBIDDEN_VISIBLE_FIELDS:
                return {}, _rejection(
                    input_ref=input_ref,
                    code="BLOCK_SCOPE_CREEP",
                    reason=f"contract-allowed visible field {field_name!r} is report-level or rendering scope",
                    phase_contract_ref=contract.contract_ref,
                    contract_version=contract.contract_version,
                    input_index=input_index,
                )
            value = inference.get(field_name)
            if _has_value(value):
                payload[output_key] = copy.deepcopy(value)

        if not payload:
            return {}, _rejection(
                input_ref=input_ref,
                code="EMPTY_VISIBLE_PAYLOAD",
                reason="no contract-allowed visible field contains non-empty content",
                phase_contract_ref=contract.contract_ref,
                contract_version=contract.contract_version,
                input_index=input_index,
            )

        return {key: payload[key] for key in sorted(payload)}, None

    def _resolve_versions(
        self,
        *,
        inference: Mapping[str, Any],
        version_records: Sequence[Mapping[str, Any]],
        input_ref: str,
        input_index: int,
    ) -> tuple[list[str], list[str], dict[str, Any] | None]:
        inference_id = _text(inference.get("inference_id"))
        inference_contract_ref = _text(inference.get("phase_contract_ref"))
        inference_lineage_refs = _string_list(inference.get("lineage_refs"))

        usable_versions: list[Mapping[str, Any]] = []
        mismatched_fields: set[str] = set()
        for version_record in version_records:
            version_id = _text(version_record.get("version_id"))
            if not version_id:
                mismatched_fields.add("version_id")
                continue
            object_ref = _text(version_record.get("object_ref"))
            object_type = _text(version_record.get("object_type"))
            phase_contract_ref = _text(version_record.get("phase_contract_ref"))
            if object_ref != inference_id:
                mismatched_fields.add("object_ref")
                continue
            if object_type and object_type != "InferenceRecord":
                mismatched_fields.add("object_type")
                continue
            if phase_contract_ref != inference_contract_ref:
                mismatched_fields.add("phase_contract_ref")
                continue
            inference_hash = _text(inference.get("content_hash"))
            version_hash = _text(version_record.get("content_hash"))
            if inference_hash and version_hash and inference_hash != version_hash:
                mismatched_fields.add("content_hash")
                continue
            usable_versions.append(version_record)

        if not usable_versions:
            code = "VERSION_MISMATCH" if mismatched_fields else "MISSING_TRACEABILITY"
            reason = (
                "no supplied VersionRecord matches the inference metadata"
                if mismatched_fields
                else "no supplied VersionRecord resolves the source inference"
            )
            return [], [], _rejection(
                input_ref=input_ref,
                code=code,
                reason=reason,
                phase_contract_ref=inference_contract_ref,
                contract_version=_text(inference.get("contract_version")),
                fields=sorted(mismatched_fields),
                input_index=input_index,
            )

        declared_version_refs = _string_list(inference.get("version_refs"))
        version_refs = sorted(_unique_texts([item["version_id"] for item in usable_versions]))
        if declared_version_refs and not set(declared_version_refs).issubset(version_refs):
            return [], [], _rejection(
                input_ref=input_ref,
                code="VERSION_MISMATCH",
                reason="inference version_refs are not resolved by supplied VersionRecord entries",
                phase_contract_ref=inference_contract_ref,
                contract_version=_text(inference.get("contract_version")),
                version_refs=declared_version_refs,
                input_index=input_index,
            )

        version_lineage_refs = sorted(
            _unique_texts(
                [
                    lineage_ref
                    for version_record in usable_versions
                    for lineage_ref in (
                        _string_list(version_record.get("lineage_refs"))
                        + _string_list(version_record.get("provenance_refs"))
                    )
                ]
            )
        )
        if not version_lineage_refs:
            return [], [], _rejection(
                input_ref=input_ref,
                code="MISSING_TRACEABILITY",
                reason="matched VersionRecord entries do not carry lineage or provenance references",
                phase_contract_ref=inference_contract_ref,
                contract_version=_text(inference.get("contract_version")),
                version_refs=version_refs,
                input_index=input_index,
            )

        if not set(inference_lineage_refs).issubset(version_lineage_refs):
            return [], [], _rejection(
                input_ref=input_ref,
                code="MISSING_TRACEABILITY",
                reason="inference lineage_refs are not traceable through supplied VersionRecord entries",
                phase_contract_ref=inference_contract_ref,
                contract_version=_text(inference.get("contract_version")),
                version_refs=version_refs,
                input_index=input_index,
            )

        lineage_refs = sorted(_unique_texts(inference_lineage_refs + version_lineage_refs))
        return version_refs, lineage_refs, None

    def _emit_candidate(
        self, candidate: _AcceptedCandidate
    ) -> tuple[OutputBlock, BlockTrace]:
        source_inference_ids = [candidate.inference_id]
        block_id = _stable_id(
            "output_block",
            {
                "motor_id": MOTOR_ID,
                "phase_id": candidate.phase_id,
                "block_type": candidate.block_type,
                "source_inference_ids": source_inference_ids,
                "phase_contract_ref": candidate.phase_contract_ref,
                "contract_version": candidate.contract_version,
                "version_refs": candidate.version_refs,
                "rule_version": self.rule_version,
            },
        )
        segment_refs = self._segment_refs(block_id, candidate)
        trace_id = _stable_id(
            "block_trace",
            {
                "motor_id": MOTOR_ID,
                "block_id": block_id,
                "segment_refs": segment_refs,
                "contract_version": candidate.contract_version,
                "rule_version": self.rule_version,
            },
        )
        trace = self._build_trace(
            trace_id=trace_id,
            block_id=block_id,
            segment_refs=segment_refs,
            candidate=candidate,
        )
        block = self._build_block(
            block_id=block_id,
            trace_id=trace_id,
            candidate=candidate,
        )
        return block, trace

    def _segment_refs(
        self, block_id: str, candidate: _AcceptedCandidate
    ) -> list[dict[str, Any]]:
        version_ref = candidate.version_refs[0]
        lineage_ref = candidate.lineage_refs[0]
        segment_refs: list[dict[str, Any]] = []
        for payload_key in sorted(candidate.visible_payload):
            payload_path = f"visible_payload.{payload_key}"
            segment_refs.append(
                {
                    "segment_id": _stable_id(
                        "block_segment",
                        {
                            "block_id": block_id,
                            "payload_path": payload_path,
                            "source_inference_id": candidate.inference_id,
                            "version_ref": version_ref,
                            "lineage_ref": lineage_ref,
                            "phase_contract_ref": candidate.phase_contract_ref,
                        },
                    ),
                    "payload_path": payload_path,
                    "source_inference_id": candidate.inference_id,
                    "version_ref": version_ref,
                    "lineage_ref": lineage_ref,
                    "phase_contract_ref": candidate.phase_contract_ref,
                }
            )
        return segment_refs

    def _build_block(
        self, *, block_id: str, trace_id: str, candidate: _AcceptedCandidate
    ) -> OutputBlock:
        base = {
            "block_id": block_id,
            "motor_id": MOTOR_ID,
            "phase_id": candidate.phase_id,
            "block_type": candidate.block_type,
            "visible_payload": candidate.visible_payload,
            "source_inference_ids": [candidate.inference_id],
            "phase_contract_ref": candidate.phase_contract_ref,
            "contract_version": candidate.contract_version,
            "version_refs": candidate.version_refs,
            "lineage_refs": candidate.lineage_refs,
            "trace_id": trace_id,
            "rule_version": self.rule_version,
            "version_id": "",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": [candidate.inference_id],
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": None,
        }
        base["version_hash"] = _version_hash(base)
        base["version_id"] = _stable_id(
            "output_block_version",
            {"block_id": block_id, "version_hash": base["version_hash"]},
        )
        return OutputBlock(**base)

    def _build_trace(
        self,
        *,
        trace_id: str,
        block_id: str,
        segment_refs: list[dict[str, Any]],
        candidate: _AcceptedCandidate,
    ) -> BlockTrace:
        base = {
            "trace_id": trace_id,
            "block_id": block_id,
            "motor_id": MOTOR_ID,
            "segment_refs": segment_refs,
            "source_inference_ids": [candidate.inference_id],
            "version_refs": candidate.version_refs,
            "lineage_refs": candidate.lineage_refs,
            "phase_contract_ref": candidate.phase_contract_ref,
            "contract_version": candidate.contract_version,
            "rule_version": self.rule_version,
            "version_id": "",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": [block_id, candidate.inference_id],
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": None,
        }
        base["version_hash"] = _version_hash(base)
        base["version_id"] = _stable_id(
            "block_trace_version",
            {"trace_id": trace_id, "version_hash": base["version_hash"]},
        )
        return BlockTrace(**base)

    def _emit_composition_record(
        self,
        *,
        input_refs: list[str],
        accepted_refs: list[str],
        rejected_refs: list[dict[str, Any]],
        output_blocks: list[OutputBlock],
        block_traces: list[BlockTrace],
        phase_contract_refs: list[str],
        version_refs: list[str],
    ) -> CompositionRecord:
        emitted_block_ids = [item.block_id for item in output_blocks]
        trace_ids = [item.trace_id for item in block_traces]
        if accepted_refs and rejected_refs:
            status = "PARTIAL_REJECTION"
        elif rejected_refs:
            status = "REJECTED"
        else:
            status = "PASS"

        composition_id = _stable_id(
            "composition_record",
            {
                "motor_id": MOTOR_ID,
                "input_refs": input_refs,
                "accepted_refs": accepted_refs,
                "rejected_refs": rejected_refs,
                "emitted_block_ids": emitted_block_ids,
                "trace_ids": trace_ids,
                "rule_version": self.rule_version,
            },
        )
        base = {
            "composition_id": composition_id,
            "motor_id": MOTOR_ID,
            "input_refs": input_refs,
            "accepted_refs": accepted_refs,
            "rejected_refs": rejected_refs,
            "emitted_block_ids": emitted_block_ids,
            "trace_ids": trace_ids,
            "phase_contract_refs": phase_contract_refs,
            "version_refs": version_refs,
            "rule_version": self.rule_version,
            "status": status,
            "version_id": "",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": input_refs,
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": None,
        }
        base["version_hash"] = _version_hash(base)
        base["version_id"] = _stable_id(
            "composition_record_version",
            {
                "composition_id": composition_id,
                "version_hash": base["version_hash"],
            },
        )
        return CompositionRecord(**base)


def run_output_block_composition(
    *,
    inference_records: Sequence[Mapping[str, Any]],
    phase_contracts: Sequence[Mapping[str, Any]],
    version_records: Sequence[Mapping[str, Any]],
    rule_version: str = DEFAULT_RULE_VERSION,
    produced_at: str = DEFAULT_PRODUCED_AT,
) -> CompositionResult:
    """Convenience function for one-shot deterministic composition."""

    engine = OutputBlockCompositionEngine(
        rule_version=rule_version, produced_at=produced_at
    )
    return engine.run(
        inference_records=inference_records,
        phase_contracts=phase_contracts,
        version_records=version_records,
    )


def _as_record_list(
    field_name: str, value: Sequence[Mapping[str, Any]]
) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise OutputBlockCompositionError(
            code="INVALID_INPUT_TYPE",
            message=f"{field_name} must be a sequence of mapping records",
            field=field_name,
        )
    records: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise OutputBlockCompositionError(
                code="INVALID_INPUT_TYPE",
                message=f"{field_name}[{index}] must be a mapping record",
                field=f"{field_name}[{index}]",
            )
        records.append(item)
    return records


def _require_text(value: Any, field_name: str) -> str:
    text = _text(value)
    if not text:
        raise OutputBlockCompositionError(
            code="INVALID_INPUT_TYPE",
            message=f"{field_name} must be a non-empty string",
            field=field_name,
        )
    return text


def _text(value: Any) -> str:
    return value.strip() if isinstance(value, str) and value.strip() else ""


def _string_list(value: Any) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    result: list[str] = []
    for item in value:
        text = _text(item)
        if text:
            result.append(text)
    return result


def _mapping(value: Any) -> Mapping[str, Any]:
    return value if isinstance(value, Mapping) else {}


def _contract_ref(contract: Mapping[str, Any]) -> str:
    return (
        _text(contract.get("contract_ref"))
        or _text(contract.get("contract_id"))
        or _text(contract.get("phase_contract_ref"))
    )


def _payload_key(field_name: str) -> str:
    return field_name.removeprefix("visible_") if field_name.startswith("visible_") else field_name


def _has_value(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, Mapping):
        return bool(value)
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return bool(value)
    return True


def _unique_texts(values: Sequence[Any]) -> list[str]:
    return sorted({text for item in values if (text := _text(item))})


def _duplicate_inference_ids(inference_records: Sequence[Mapping[str, Any]]) -> set[str]:
    counts = Counter(
        _text(item.get("inference_id"))
        for item in inference_records
        if _text(item.get("inference_id"))
    )
    return {inference_id for inference_id, count in counts.items() if count > 1}


def _input_ref(inference: Mapping[str, Any]) -> str:
    inference_id = _text(inference.get("inference_id"))
    if inference_id:
        return inference_id
    return "unidentified:" + _stable_hash(inference)[:16]


def _rejection(
    *,
    input_ref: str,
    code: str,
    reason: str,
    phase_contract_ref: str = "",
    contract_version: str = "",
    version_refs: Sequence[str] | None = None,
    fields: Sequence[str] | None = None,
    input_index: int | None = None,
) -> dict[str, Any]:
    entry: dict[str, Any] = {
        "input_ref": input_ref,
        "rejection_code": code,
        "rejection_reason": reason,
    }
    if phase_contract_ref:
        entry["phase_contract_ref"] = phase_contract_ref
    if contract_version:
        entry["contract_version"] = contract_version
    clean_version_refs = _unique_texts(version_refs or [])
    if clean_version_refs:
        entry["version_refs"] = clean_version_refs
    clean_fields = _unique_texts(fields or [])
    if clean_fields:
        entry["fields"] = clean_fields
    if input_index is not None:
        entry["input_index"] = input_index
    return entry


def _stable_id(prefix: str, material: Mapping[str, Any]) -> str:
    return f"{prefix}:{_stable_hash(material)[:24]}"


def _version_hash(material: Mapping[str, Any]) -> str:
    clean_material = {
        key: value
        for key, value in material.items()
        if key not in {"version_hash", "version_id"}
    }
    return "sha256:" + _stable_hash(clean_material)


def _stable_hash(material: Any) -> str:
    return hashlib.sha256(_stable_json(material).encode("utf-8")).hexdigest()


def _stable_json(material: Any) -> str:
    return json.dumps(material, sort_keys=True, separators=(",", ":"), default=str)
