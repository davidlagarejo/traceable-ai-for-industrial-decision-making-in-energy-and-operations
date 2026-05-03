"""Deterministic implementation for motor_016.

The engine assembles approved OutputBlock references into one ReportPackage and
two view manifests. It validates phase-contract scope, version lineage, view
membership, and trace coverage without generating prose, rendering documents,
or mutating upstream block content.
"""

from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from dataclasses import dataclass
import hashlib
import json
from typing import Any

from .errors import ReportPackageAssemblyError
from .models import AssemblyResult, ExecutiveView, ReportPackage, TechnicalView


MOTOR_ID = "motor_016"
DEFAULT_RULE_VERSION = "m016-rules-v1"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
REQUIRED_VIEW_TYPES = ("technical_view", "executive_view")
CURRENT_VERSION_STATES = frozenset({"current", "active"})
SUPERSEDED_VERSION_STATES = frozenset({"superseded", "deprecated", "archived"})
PARENT_REF_FIELDS = (
    "parent_version_id",
    "parent_version_refs",
    "supersedes_version_id",
    "supersedes_version_refs",
)


@dataclass(frozen=True)
class _ContractContext:
    raw: Mapping[str, Any]
    contract_ref: str
    target_phase_ref: str
    permitted_view_types: list[str]
    optional_view_types: list[str]
    required_block_categories: list[str]
    ordering_rule_ref: str
    category_order: list[str]
    source_version_refs: list[str]


@dataclass(frozen=True)
class _BlockContext:
    raw: Mapping[str, Any]
    block_id: str
    block_type: str
    status: str
    phase_ref: str
    view_tags: list[str]
    block_trace_ref: str
    provenance_ref: str
    source_version_refs: list[str]
    current_version_ids: list[str]
    superseded_version_ids: list[str]
    all_version_ids: list[str]

    @property
    def resolved_version_id(self) -> str:
        return self.current_version_ids[0] if len(self.current_version_ids) == 1 else ""


class ReportPackageAssemblyEngine:
    """Core deterministic interface for the Report Package Assembly Engine."""

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
        output_blocks: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        version_records: Sequence[Mapping[str, Any]],
        parent_package_id: str | None = None,
    ) -> AssemblyResult:
        """Assemble one report package from approved blocks and contract data."""

        block_items, block_errors = _as_record_list("output_blocks", output_blocks)
        contract_items, contract_errors = _as_record_list("phase_contracts", phase_contracts)
        version_items, version_type_errors = _as_record_list(
            "version_records", version_records
        )
        errors = block_errors + contract_errors + version_type_errors
        if errors:
            return self._rejected(errors, parent_package_id=parent_package_id)

        if not block_items:
            errors.append(
                _validation_error(
                    "EMPTY_INPUT",
                    "output_blocks",
                    "input.output_blocks",
                    "output_blocks must contain at least one OutputBlock",
                )
            )
        if not contract_items:
            errors.append(
                _validation_error(
                    "PHASE_CONTRACT_MISSING",
                    "phase_contracts",
                    "input.phase_contracts",
                    "phase_contracts must contain at least one PhaseContract",
                )
            )
        if not version_items:
            errors.append(
                _validation_error(
                    "VERSION_RECORD_UNRESOLVED",
                    "version_records",
                    "input.version_records",
                    "version_records must contain records for blocks and contracts",
                )
            )
        if errors:
            return self._rejected(errors, parent_package_id=parent_package_id)

        version_index, version_errors = self._index_version_records(version_items)
        contract_contexts, parse_contract_errors = self._parse_contracts(contract_items)
        errors.extend(version_errors)
        errors.extend(parse_contract_errors)
        if errors:
            return self._rejected(errors, parent_package_id=parent_package_id)

        block_contexts, parse_block_errors = self._parse_blocks(block_items, version_index)
        errors.extend(parse_block_errors)
        if errors:
            return self._rejected(errors, parent_package_id=parent_package_id)

        target_phase_ref, selected_contracts, scope_errors = self._select_contract_scope(
            block_contexts, contract_contexts
        )
        errors.extend(scope_errors)
        if errors:
            return self._rejected(
                errors,
                target_phase_ref=target_phase_ref,
                parent_package_id=parent_package_id,
            )

        contract_version_refs, contract_version_errors = self._resolve_contract_versions(
            selected_contracts, version_index
        )
        errors.extend(contract_version_errors)
        if errors:
            return self._rejected(
                errors,
                target_phase_ref=target_phase_ref,
                parent_package_id=parent_package_id,
            )

        selected_blocks, excluded_superseded_versions, duplicate_errors = (
            self._select_current_blocks(block_contexts)
        )
        errors.extend(duplicate_errors)
        errors.extend(
            self._validate_selected_blocks(
                selected_blocks=selected_blocks,
                selected_contracts=selected_contracts,
            )
        )
        if errors:
            return self._rejected(
                errors,
                target_phase_ref=target_phase_ref,
                parent_package_id=parent_package_id,
            )

        package = self._emit_valid_package(
            blocks=selected_blocks,
            selected_contracts=selected_contracts,
            contract_version_refs=contract_version_refs,
            excluded_superseded_versions=excluded_superseded_versions,
            target_phase_ref=target_phase_ref,
            parent_package_id=parent_package_id,
        )
        if package.report_package.validation_errors:
            return self._rejected(
                package.report_package.validation_errors,
                target_phase_ref=target_phase_ref,
                parent_package_id=parent_package_id,
            )
        return package

    def assemble(
        self,
        *,
        output_blocks: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
        version_records: Sequence[Mapping[str, Any]],
        parent_package_id: str | None = None,
    ) -> AssemblyResult:
        """Alias for callers that name the operation by the motor purpose."""

        return self.run(
            output_blocks=output_blocks,
            phase_contracts=phase_contracts,
            version_records=version_records,
            parent_package_id=parent_package_id,
        )

    def _parse_contracts(
        self, phase_contracts: Sequence[Mapping[str, Any]]
    ) -> tuple[list[_ContractContext], list[dict[str, Any]]]:
        contracts: list[_ContractContext] = []
        errors: list[dict[str, Any]] = []
        for index, contract in enumerate(phase_contracts):
            object_ref = _contract_ref(contract) or f"phase_contracts[{index}]"
            contract_ref = _contract_ref(contract)
            target_phase_ref = _text(
                contract.get("target_phase_ref")
                or contract.get("phase_ref")
                or contract.get("phase_id")
            )
            permitted_view_types = _string_list(contract.get("permitted_view_types"))
            required_block_categories = _string_list(
                contract.get("required_block_categories")
            )
            ordering_rule_ref = _text(contract.get("ordering_rule_ref"))

            missing_fields: list[str] = []
            if not contract_ref:
                missing_fields.append("contract_id")
            if not target_phase_ref:
                missing_fields.append("target_phase_ref")
            if not permitted_view_types:
                missing_fields.append("permitted_view_types")
            if not ordering_rule_ref:
                missing_fields.append("ordering_rule_ref")
            if missing_fields:
                errors.append(
                    _validation_error(
                        "PHASE_CONTRACT_MISMATCH",
                        ",".join(missing_fields),
                        object_ref,
                        "phase contract is missing required assembly fields",
                    )
                )
                continue

            contracts.append(
                _ContractContext(
                    raw=contract,
                    contract_ref=contract_ref,
                    target_phase_ref=target_phase_ref,
                    permitted_view_types=sorted(set(permitted_view_types)),
                    optional_view_types=sorted(
                        set(_string_list(contract.get("optional_view_types")))
                    ),
                    required_block_categories=required_block_categories,
                    ordering_rule_ref=ordering_rule_ref,
                    category_order=_category_order(contract, required_block_categories),
                    source_version_refs=_string_list(
                        contract.get("source_version_refs")
                        or contract.get("version_refs")
                    ),
                )
            )
        return contracts, errors

    def _parse_blocks(
        self,
        output_blocks: Sequence[Mapping[str, Any]],
        version_index: Mapping[str, list[Mapping[str, Any]]],
    ) -> tuple[list[_BlockContext], list[dict[str, Any]]]:
        blocks: list[_BlockContext] = []
        errors: list[dict[str, Any]] = []
        for index, block in enumerate(output_blocks):
            block_id = _text(block.get("block_id"))
            object_ref = block_id or f"output_blocks[{index}]"
            block_type = _text(block.get("block_type"))
            status = _text(block.get("status"))
            phase_ref = _text(block.get("phase_ref") or block.get("phase_id"))
            view_tags = _string_list(block.get("view_tags"))
            block_trace_ref = _block_trace_ref(block)
            provenance_ref = _text(block.get("provenance_ref"))
            source_version_refs = _string_list(
                block.get("source_version_refs") or block.get("version_refs")
            )

            missing_fields: list[str] = []
            if not block_id:
                missing_fields.append("block_id")
            if not block_type:
                missing_fields.append("block_type")
            if not status:
                missing_fields.append("status")
            if not phase_ref:
                missing_fields.append("phase_ref")
            if not view_tags:
                missing_fields.append("view_tags")
            if not block_trace_ref:
                missing_fields.append("block_trace")
            if not provenance_ref:
                missing_fields.append("provenance_ref")
            if not source_version_refs:
                missing_fields.append("source_version_refs")
            if not _has_content_reference(block):
                missing_fields.append("content_payload_or_content_ref")

            if "block_trace" in missing_fields:
                errors.append(
                    _validation_error(
                        "BLOCK_TRACE_MISSING",
                        "block_trace",
                        object_ref,
                        "block_trace must be present and resolvable",
                    )
                )
            if "provenance_ref" in missing_fields:
                errors.append(
                    _validation_error(
                        "BLOCK_TRACE_MISSING",
                        "provenance_ref",
                        object_ref,
                        "provenance_ref must be present",
                    )
                )
            other_missing = [
                field
                for field in missing_fields
                if field not in {"block_trace", "provenance_ref"}
            ]
            if other_missing:
                errors.append(
                    _validation_error(
                        "MISSING_REQUIRED_FIELD",
                        ",".join(other_missing),
                        object_ref,
                        "OutputBlock is missing required assembly fields",
                    )
                )
            if status and status != "approved_for_assembly":
                errors.append(
                    _validation_error(
                        "BLOCK_STATUS_NOT_APPROVED",
                        "status",
                        object_ref,
                        "OutputBlock status must be approved_for_assembly",
                    )
                )

            version_resolution = self._resolve_block_version_refs(
                block_id=object_ref,
                source_version_refs=source_version_refs,
                version_index=version_index,
            )
            errors.extend(version_resolution[3])
            if missing_fields or status != "approved_for_assembly":
                continue

            blocks.append(
                _BlockContext(
                    raw=block,
                    block_id=block_id,
                    block_type=block_type,
                    status=status,
                    phase_ref=phase_ref,
                    view_tags=sorted(set(view_tags)),
                    block_trace_ref=block_trace_ref,
                    provenance_ref=provenance_ref,
                    source_version_refs=source_version_refs,
                    current_version_ids=version_resolution[0],
                    superseded_version_ids=version_resolution[1],
                    all_version_ids=version_resolution[2],
                )
            )
        return blocks, errors

    def _index_version_records(
        self, version_records: Sequence[Mapping[str, Any]]
    ) -> tuple[dict[str, list[Mapping[str, Any]]], list[dict[str, Any]]]:
        index: dict[str, list[Mapping[str, Any]]] = {}
        errors: list[dict[str, Any]] = []
        for item_index, record in enumerate(version_records):
            version_id = _version_id(record)
            if not version_id:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_CONFLICT",
                        "version_id",
                        f"version_records[{item_index}]",
                        "VersionRecord must include version_id",
                    )
                )
                continue
            index.setdefault(version_id, []).append(record)

        for version_id, records in index.items():
            if len({_stable_json(record) for record in records}) > 1:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_CONFLICT",
                        "version_id",
                        version_id,
                        "version_id resolves to conflicting VersionRecord records",
                    )
                )

        for version_id, records in index.items():
            if not records:
                continue
            for parent_ref in _parent_version_refs(records[0]):
                if parent_ref not in index:
                    errors.append(
                        _validation_error(
                            "VERSION_RECORD_CONFLICT",
                            "lineage_parent_ref",
                            version_id,
                            f"parent version {parent_ref!r} is not supplied",
                        )
                    )
        return index, errors

    def _resolve_block_version_refs(
        self,
        *,
        block_id: str,
        source_version_refs: Sequence[str],
        version_index: Mapping[str, list[Mapping[str, Any]]],
    ) -> tuple[list[str], list[str], list[str], list[dict[str, Any]]]:
        current_ids: list[str] = []
        superseded_ids: list[str] = []
        all_ids: list[str] = []
        errors: list[dict[str, Any]] = []
        for version_ref in source_version_refs:
            records = version_index.get(version_ref, [])
            if not records:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_UNRESOLVED",
                        "source_version_refs",
                        block_id,
                        f"source_version_ref {version_ref!r} has no VersionRecord",
                    )
                )
                continue
            record = records[0]
            all_ids.append(version_ref)
            object_ref = _text(record.get("object_ref") or record.get("block_id"))
            if object_ref and object_ref != block_id:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_CONFLICT",
                        "object_ref",
                        block_id,
                        f"VersionRecord {version_ref!r} does not reference the block",
                    )
                )
            if _is_current_version(record):
                current_ids.append(version_ref)
            elif _is_superseded_version(record):
                superseded_ids.append(version_ref)
            else:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_CONFLICT",
                        "status",
                        block_id,
                        f"VersionRecord {version_ref!r} is neither current nor superseded",
                    )
                )

        if len(set(current_ids)) > 1:
            errors.append(
                _validation_error(
                    "DUPLICATE_CURRENT_BLOCK",
                    "source_version_refs",
                    block_id,
                    "OutputBlock resolves to more than one current VersionRecord",
                )
            )
        return (
            sorted(set(current_ids)),
            sorted(set(superseded_ids)),
            sorted(set(all_ids)),
            errors,
        )

    def _select_contract_scope(
        self,
        blocks: Sequence[_BlockContext],
        contracts: Sequence[_ContractContext],
    ) -> tuple[str, list[_ContractContext], list[dict[str, Any]]]:
        errors: list[dict[str, Any]] = []
        phase_refs = sorted({block.phase_ref for block in blocks})
        target_phase_ref = phase_refs[0] if phase_refs else ""
        if len(phase_refs) > 1:
            errors.append(
                _validation_error(
                    "PHASE_CONTRACT_MISMATCH",
                    "phase_ref",
                    "input.output_blocks",
                    "one ReportPackage cannot assemble blocks from multiple phases",
                )
            )
            return target_phase_ref, [], errors

        selected_contracts = [
            contract for contract in contracts if contract.target_phase_ref == target_phase_ref
        ]
        if not selected_contracts:
            errors.append(
                _validation_error(
                    "PHASE_CONTRACT_MISMATCH",
                    "phase_ref",
                    target_phase_ref or "input.output_blocks",
                    "no supplied phase contract authorizes the block phase_ref",
                )
            )
            return target_phase_ref, [], errors

        permitted_views = set(
            view_type
            for contract in selected_contracts
            for view_type in contract.permitted_view_types
        )
        missing_views = sorted(set(REQUIRED_VIEW_TYPES) - permitted_views)
        if missing_views:
            errors.append(
                _validation_error(
                    "PHASE_CONTRACT_MISMATCH",
                    "permitted_view_types",
                    target_phase_ref,
                    "phase contract must permit technical_view and executive_view",
                    missing_view_types=missing_views,
                )
            )

        for block in blocks:
            unknown_tags = sorted(set(block.view_tags) - permitted_views)
            if unknown_tags:
                errors.append(
                    _validation_error(
                        "VIEW_SCOPE_DRIFT",
                        "view_tags",
                        block.block_id,
                        "OutputBlock view_tags are not permitted by the phase contract",
                        unknown_view_tags=unknown_tags,
                    )
                )
        return target_phase_ref, sorted(selected_contracts, key=lambda item: item.contract_ref), errors

    def _resolve_contract_versions(
        self,
        contracts: Sequence[_ContractContext],
        version_index: Mapping[str, list[Mapping[str, Any]]],
    ) -> tuple[list[str], list[dict[str, Any]]]:
        version_refs: list[str] = []
        errors: list[dict[str, Any]] = []
        for contract in contracts:
            declared_refs = contract.source_version_refs
            candidate_refs = declared_refs or [
                version_id
                for version_id, records in version_index.items()
                if records and _version_object_ref(records[0]) == contract.contract_ref
            ]
            if not candidate_refs:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_UNRESOLVED",
                        "phase_contract_refs",
                        contract.contract_ref,
                        "phase contract has no resolvable current VersionRecord",
                    )
                )
                continue

            current_refs = []
            for version_ref in candidate_refs:
                records = version_index.get(version_ref, [])
                if not records:
                    errors.append(
                        _validation_error(
                            "VERSION_RECORD_UNRESOLVED",
                            "phase_contract_refs",
                            contract.contract_ref,
                            f"contract version_ref {version_ref!r} has no VersionRecord",
                        )
                    )
                    continue
                if _is_current_version(records[0]):
                    current_refs.append(version_ref)
            if len(set(current_refs)) != 1:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_CONFLICT",
                        "phase_contract_refs",
                        contract.contract_ref,
                        "phase contract must resolve to exactly one current VersionRecord",
                    )
                )
                continue
            version_refs.append(current_refs[0])
        return sorted(set(version_refs)), errors

    def _select_current_blocks(
        self, blocks: Sequence[_BlockContext]
    ) -> tuple[list[_BlockContext], list[dict[str, Any]], list[dict[str, Any]]]:
        selected: list[_BlockContext] = []
        excluded_superseded_versions: list[dict[str, Any]] = []
        errors: list[dict[str, Any]] = []
        by_block_id: dict[str, list[_BlockContext]] = {}
        for block in blocks:
            by_block_id.setdefault(block.block_id, []).append(block)

        for block_id in sorted(by_block_id):
            candidates = by_block_id[block_id]
            current_candidates = [
                block for block in candidates if len(block.current_version_ids) == 1
            ]
            if len(current_candidates) > 1:
                errors.append(
                    _validation_error(
                        "DUPLICATE_CURRENT_BLOCK",
                        "block_id",
                        block_id,
                        "duplicate block_id entries resolve to multiple current versions",
                    )
                )
                continue
            if len(current_candidates) == 0:
                errors.append(
                    _validation_error(
                        "VERSION_RECORD_CONFLICT",
                        "source_version_refs",
                        block_id,
                        "block_id has no current VersionRecord",
                    )
                )
                continue

            selected_block = current_candidates[0]
            selected.append(selected_block)
            for candidate in candidates:
                for version_id in candidate.superseded_version_ids:
                    excluded_superseded_versions.append(
                        {"block_id": block_id, "version_id": version_id}
                    )
                if candidate is selected_block:
                    continue
                if candidate.current_version_ids:
                    errors.append(
                        _validation_error(
                            "DUPLICATE_CURRENT_BLOCK",
                            "block_id",
                            block_id,
                            "superseded duplicate entry also resolves as current",
                        )
                    )
                elif not candidate.superseded_version_ids:
                    errors.append(
                        _validation_error(
                            "VERSION_RECORD_CONFLICT",
                            "source_version_refs",
                            block_id,
                            "duplicate block entry is not marked superseded",
                        )
                    )

        return selected, sorted(
            excluded_superseded_versions,
            key=lambda item: (item["block_id"], item["version_id"]),
        ), errors

    def _validate_selected_blocks(
        self,
        *,
        selected_blocks: Sequence[_BlockContext],
        selected_contracts: Sequence[_ContractContext],
    ) -> list[dict[str, Any]]:
        errors: list[dict[str, Any]] = []
        required_categories = _merge_ordered(
            [
                category
                for contract in selected_contracts
                for category in contract.required_block_categories
            ]
        )
        present_categories = sorted({block.block_type for block in selected_blocks})
        missing_categories = [
            category for category in required_categories if category not in present_categories
        ]
        if missing_categories:
            errors.append(
                _validation_error(
                    "REQUIRED_BLOCK_CATEGORY_MISSING",
                    "required_block_categories",
                    ",".join(missing_categories),
                    "required block categories are absent from approved current blocks",
                    missing_block_categories=missing_categories,
                )
            )

        optional_views = set(
            view_type
            for contract in selected_contracts
            for view_type in contract.optional_view_types
        )
        for view_type in REQUIRED_VIEW_TYPES:
            if view_type in optional_views:
                continue
            if not any(view_type in block.view_tags for block in selected_blocks):
                errors.append(
                    _validation_error(
                        "VIEW_SCOPE_DRIFT",
                        "view_tags",
                        view_type,
                        f"{view_type} has no included blocks and is not optional",
                    )
                )
        return errors

    def _emit_valid_package(
        self,
        *,
        blocks: Sequence[_BlockContext],
        selected_contracts: Sequence[_ContractContext],
        contract_version_refs: Sequence[str],
        excluded_superseded_versions: Sequence[dict[str, Any]],
        target_phase_ref: str,
        parent_package_id: str | None,
    ) -> AssemblyResult:
        phase_contract_refs = [contract.contract_ref for contract in selected_contracts]
        ordering_rule_ref = _ordering_rule_ref(selected_contracts)
        category_order = _combined_category_order(selected_contracts)
        ordered_blocks = sorted(
            blocks,
            key=lambda block: _ordering_key(block, category_order),
        )
        block_refs = [block.block_id for block in ordered_blocks]
        block_version_refs = _unique_texts(
            [block.resolved_version_id for block in ordered_blocks]
            + [
                item["version_id"]
                for item in excluded_superseded_versions
                if _text(item.get("version_id"))
            ]
        )
        version_record_refs = _unique_texts(block_version_refs + list(contract_version_refs))
        package_id = _stable_id(
            "report_package",
            {
                "target_phase_ref": target_phase_ref,
                "block_refs": block_refs,
                "phase_contract_refs": phase_contract_refs,
                "version_record_refs": version_record_refs,
            },
        )
        motor_016_id = _stable_id(
            "motor_016_run",
            {
                "package_id": package_id,
                "rule_version": self.rule_version,
                "version_record_refs": version_record_refs,
            },
        )
        technical_view_ref = _stable_id(
            "view",
            {"package_id": package_id, "view_type": "technical_view"},
        )
        executive_view_ref = _stable_id(
            "view",
            {"package_id": package_id, "view_type": "executive_view"},
        )
        view_refs = [technical_view_ref, executive_view_ref]
        block_manifest = [
            _block_manifest_entry(
                block,
                ordering_key=_ordering_key(block, category_order),
                assembly_rule_ref=ordering_rule_ref,
            )
            for block in ordered_blocks
        ]
        block_manifest_by_id = {entry["block_id"]: entry for entry in block_manifest}

        technical_view = self._build_view(
            view_cls=TechnicalView,
            view_id=technical_view_ref,
            view_type="technical_view",
            package_id=package_id,
            motor_016_id=motor_016_id,
            ordered_blocks=ordered_blocks,
            block_manifest_by_id=block_manifest_by_id,
            selected_contracts=selected_contracts,
            ordering_rule_ref=ordering_rule_ref,
        )
        executive_view = self._build_view(
            view_cls=ExecutiveView,
            view_id=executive_view_ref,
            view_type="executive_view",
            package_id=package_id,
            motor_016_id=motor_016_id,
            ordered_blocks=ordered_blocks,
            block_manifest_by_id=block_manifest_by_id,
            selected_contracts=selected_contracts,
            ordering_rule_ref=ordering_rule_ref,
        )

        validation_errors = _view_validation_errors(
            block_refs=block_refs,
            technical_view=technical_view,
            executive_view=executive_view,
        )
        view_membership_summary = {
            "technical_view": {
                "included_count": len(technical_view.included_block_refs),
                "excluded_count": len(technical_view.excluded_block_refs),
            },
            "executive_view": {
                "included_count": len(executive_view.included_block_refs),
                "excluded_count": len(executive_view.excluded_block_refs),
            },
        }
        required_categories = _merge_ordered(
            [
                category
                for contract in selected_contracts
                for category in contract.required_block_categories
            ]
        )
        present_categories = sorted({block.block_type for block in ordered_blocks})
        package_hash_inputs = {
            "target_phase_ref": target_phase_ref,
            "block_refs": block_refs,
            "phase_contract_refs": phase_contract_refs,
            "version_record_refs": version_record_refs,
            "ordering_rule_ref": ordering_rule_ref,
        }
        assembly_manifest = {
            "ordering_rule_ref": ordering_rule_ref,
            "required_category_check": {
                "required_block_categories": required_categories,
                "present_block_categories": present_categories,
                "missing_block_categories": [],
            },
            "duplicate_resolution": {
                "duplicate_block_ids": sorted(
                    block_id
                    for block_id, count in Counter(block_refs).items()
                    if count > 1
                ),
                "included_current_versions": {
                    block.block_id: block.resolved_version_id for block in ordered_blocks
                },
            },
            "excluded_superseded_versions": list(excluded_superseded_versions),
            "package_hash_inputs": package_hash_inputs,
            "view_membership_summary": view_membership_summary,
        }
        package_manifest = {
            "package_id": package_id,
            "target_phase_ref": target_phase_ref,
            "block_refs": block_refs,
            "block_manifest": block_manifest,
            "view_refs": view_refs,
            "phase_contract_refs": phase_contract_refs,
            "version_record_refs": version_record_refs,
        }
        base = {
            "record_id": _stable_id("report_package_record", {"package_id": package_id}),
            "motor_016_id": motor_016_id,
            "package_id": package_id,
            "package_type": "report_package",
            "target_phase_ref": target_phase_ref,
            "phase_contract_refs": phase_contract_refs,
            "block_refs": block_refs,
            "block_manifest": block_manifest,
            "package_manifest": package_manifest,
            "view_refs": view_refs,
            "technical_view_ref": technical_view_ref,
            "executive_view_ref": executive_view_ref,
            "version_record_refs": version_record_refs,
            "assembly_manifest": assembly_manifest,
            "ordering_rule_ref": ordering_rule_ref,
            "validation_status": "valid" if not validation_errors else "rejected",
            "validation_errors": validation_errors,
            "version_id": "",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": _unique_texts(block_refs + phase_contract_refs + version_record_refs),
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": parent_package_id,
        }
        base["version_hash"] = _version_hash(base)
        base["version_id"] = _stable_id(
            "report_package_version",
            {"package_id": package_id, "version_hash": base["version_hash"]},
        )
        return AssemblyResult(
            report_package=ReportPackage(**base),
            technical_view=technical_view,
            executive_view=executive_view,
        )

    def _build_view(
        self,
        *,
        view_cls: type[TechnicalView] | type[ExecutiveView],
        view_id: str,
        view_type: str,
        package_id: str,
        motor_016_id: str,
        ordered_blocks: Sequence[_BlockContext],
        block_manifest_by_id: Mapping[str, dict[str, Any]],
        selected_contracts: Sequence[_ContractContext],
        ordering_rule_ref: str,
    ) -> TechnicalView | ExecutiveView:
        included_block_refs = [
            block.block_id for block in ordered_blocks if view_type in block.view_tags
        ]
        excluded_block_refs = [
            {"block_id": block.block_id, "reason_code": "view_tag_not_present"}
            for block in ordered_blocks
            if block.block_id not in included_block_refs
        ]
        trace_index = {
            block_id: {
                "block_trace_ref": block_manifest_by_id[block_id]["block_trace_ref"],
                "provenance_ref": block_manifest_by_id[block_id]["provenance_ref"],
                "resolved_version_id": block_manifest_by_id[block_id][
                    "resolved_version_id"
                ],
                "package_id": package_id,
                "source_output_block_ref": block_id,
            }
            for block_id in included_block_refs
        }
        phase_contract_refs = [contract.contract_ref for contract in selected_contracts]
        inclusion_rule_ref = _inclusion_rule_ref(selected_contracts, view_type)
        view_manifest = {
            "view_type": view_type,
            "inclusion_rule_ref": inclusion_rule_ref,
            "ordering_rule_ref": ordering_rule_ref,
            "included_count": len(included_block_refs),
            "excluded_count": len(excluded_block_refs),
            "contract_refs": phase_contract_refs,
            "included_block_refs": included_block_refs,
            "excluded_block_refs": excluded_block_refs,
        }
        validation_errors = _single_view_validation_errors(
            view_type=view_type,
            block_refs=[block.block_id for block in ordered_blocks],
            included_block_refs=included_block_refs,
            excluded_block_refs=excluded_block_refs,
            trace_index=trace_index,
        )
        base = {
            "record_id": _stable_id("view_record", {"view_id": view_id}),
            "motor_016_id": motor_016_id,
            "view_id": view_id,
            "package_id": package_id,
            "view_type": view_type,
            "inclusion_rule_ref": inclusion_rule_ref,
            "included_block_refs": included_block_refs,
            "excluded_block_refs": excluded_block_refs,
            "ordering_rule_ref": ordering_rule_ref,
            "trace_index": trace_index,
            "view_manifest": view_manifest,
            "validation_status": "valid" if not validation_errors else "rejected",
            "validation_errors": validation_errors,
            "version_id": "",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": _unique_texts(included_block_refs + [package_id] + phase_contract_refs),
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": package_id,
        }
        base["version_hash"] = _version_hash(base)
        base["version_id"] = _stable_id(
            f"{view_type}_version",
            {"view_id": view_id, "version_hash": base["version_hash"]},
        )
        return view_cls(**base)

    def _rejected(
        self,
        validation_errors: Sequence[dict[str, Any]],
        *,
        target_phase_ref: str = "",
        parent_package_id: str | None = None,
    ) -> AssemblyResult:
        error_list = sorted(
            [dict(error) for error in validation_errors],
            key=lambda item: (
                str(item.get("object_ref", "")),
                str(item.get("error_code", "")),
                str(item.get("field", "")),
                str(item.get("message", "")),
            ),
        )
        package_id = _stable_id(
            "report_package_rejected",
            {"target_phase_ref": target_phase_ref, "validation_errors": error_list},
        )
        base = {
            "record_id": _stable_id("report_package_record", {"package_id": package_id}),
            "motor_016_id": _stable_id(
                "motor_016_run",
                {"package_id": package_id, "rule_version": self.rule_version},
            ),
            "package_id": package_id,
            "package_type": "report_package",
            "target_phase_ref": target_phase_ref,
            "phase_contract_refs": [],
            "block_refs": [],
            "block_manifest": [],
            "package_manifest": {
                "package_id": package_id,
                "target_phase_ref": target_phase_ref,
                "block_refs": [],
                "block_manifest": [],
                "view_refs": [],
                "phase_contract_refs": [],
                "version_record_refs": [],
            },
            "view_refs": [],
            "technical_view_ref": "",
            "executive_view_ref": "",
            "version_record_refs": [],
            "assembly_manifest": {
                "ordering_rule_ref": "",
                "required_category_check": {
                    "required_block_categories": [],
                    "present_block_categories": [],
                    "missing_block_categories": [],
                },
                "duplicate_resolution": {
                    "duplicate_block_ids": [],
                    "included_current_versions": {},
                },
                "excluded_superseded_versions": [],
                "package_hash_inputs": {},
                "view_membership_summary": {},
            },
            "ordering_rule_ref": "",
            "validation_status": "rejected",
            "validation_errors": error_list,
            "version_id": "",
            "created_at": self.produced_at,
            "updated_at": self.produced_at,
            "version_hash": "",
            "source_ref": [],
            "produced_by_motor": MOTOR_ID,
            "produced_at": self.produced_at,
            "parent_id": parent_package_id,
        }
        base["version_hash"] = _version_hash(base)
        base["version_id"] = _stable_id(
            "report_package_version",
            {"package_id": package_id, "version_hash": base["version_hash"]},
        )
        return AssemblyResult(
            report_package=ReportPackage(**base),
            technical_view=None,
            executive_view=None,
        )


def run_report_package_assembly(
    *,
    output_blocks: Sequence[Mapping[str, Any]],
    phase_contracts: Sequence[Mapping[str, Any]],
    version_records: Sequence[Mapping[str, Any]],
    rule_version: str = DEFAULT_RULE_VERSION,
    produced_at: str = DEFAULT_PRODUCED_AT,
    parent_package_id: str | None = None,
) -> AssemblyResult:
    """Convenience function for one-shot deterministic package assembly."""

    engine = ReportPackageAssemblyEngine(
        rule_version=rule_version,
        produced_at=produced_at,
    )
    return engine.run(
        output_blocks=output_blocks,
        phase_contracts=phase_contracts,
        version_records=version_records,
        parent_package_id=parent_package_id,
    )


def _as_record_list(
    field_name: str, value: Sequence[Mapping[str, Any]]
) -> tuple[list[Mapping[str, Any]], list[dict[str, Any]]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return [], [
            _validation_error(
                "INVALID_INPUT_TYPE",
                field_name,
                f"input.{field_name}",
                f"{field_name} must be a list of mapping records",
            )
        ]
    records: list[Mapping[str, Any]] = []
    errors: list[dict[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            errors.append(
                _validation_error(
                    "INVALID_INPUT_TYPE",
                    f"{field_name}[{index}]",
                    f"input.{field_name}[{index}]",
                    f"{field_name}[{index}] must be a mapping record",
                )
            )
            continue
        records.append(item)
    return records, errors


def _validation_error(
    error_code: str,
    field: str,
    object_ref: str,
    message: str,
    **extra: Any,
) -> dict[str, Any]:
    entry = {
        "error_code": error_code,
        "field": field,
        "object_ref": object_ref,
        "message": message,
    }
    for key in sorted(extra):
        value = extra[key]
        if value not in (None, "", [], {}):
            entry[key] = value
    return entry


def _require_text(value: Any, field_name: str) -> str:
    text = _text(value)
    if not text:
        raise ReportPackageAssemblyError(
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


def _merge_ordered(values: Sequence[str]) -> list[str]:
    result: list[str] = []
    seen: set[str] = set()
    for value in values:
        if value not in seen:
            seen.add(value)
            result.append(value)
    return result


def _unique_texts(values: Sequence[Any]) -> list[str]:
    return sorted({text for item in values if (text := _text(item))})


def _contract_ref(contract: Mapping[str, Any]) -> str:
    return (
        _text(contract.get("contract_id"))
        or _text(contract.get("contract_ref"))
        or _text(contract.get("phase_contract_ref"))
    )


def _version_id(record: Mapping[str, Any]) -> str:
    return _text(record.get("version_id") or record.get("id"))


def _version_object_ref(record: Mapping[str, Any]) -> str:
    return _text(
        record.get("object_ref")
        or record.get("contract_id")
        or record.get("phase_contract_ref")
        or record.get("block_id")
    )


def _block_trace_ref(block: Mapping[str, Any]) -> str:
    block_trace = block.get("block_trace")
    if isinstance(block_trace, Mapping):
        return _text(
            block_trace.get("trace_id")
            or block_trace.get("block_trace_ref")
            or block_trace.get("id")
        )
    return _text(block_trace or block.get("block_trace_ref") or block.get("trace_id"))


def _has_content_reference(block: Mapping[str, Any]) -> bool:
    return bool(
        _text(block.get("content_ref"))
        or block.get("content_payload") not in (None, "", [], {})
        or block.get("visible_payload") not in (None, "", [], {})
    )


def _version_status(record: Mapping[str, Any]) -> str:
    status = _text(record.get("status") or record.get("version_status") or record.get("state"))
    if status:
        return status
    is_current = record.get("is_current")
    if is_current is True:
        return "current"
    if is_current is False:
        return "superseded"
    return ""


def _is_current_version(record: Mapping[str, Any]) -> bool:
    return _version_status(record) in CURRENT_VERSION_STATES


def _is_superseded_version(record: Mapping[str, Any]) -> bool:
    return _version_status(record) in SUPERSEDED_VERSION_STATES


def _parent_version_refs(record: Mapping[str, Any]) -> list[str]:
    refs: list[str] = []
    for field_name in PARENT_REF_FIELDS:
        value = record.get(field_name)
        text = _text(value)
        if text:
            refs.append(text)
        refs.extend(_string_list(value))
    return sorted(set(refs))


def _category_order(
    contract: Mapping[str, Any], required_block_categories: Sequence[str]
) -> list[str]:
    ordering_rules = contract.get("ordering_rules")
    nested_order: list[str] = []
    if isinstance(ordering_rules, Mapping):
        nested_order = _string_list(
            ordering_rules.get("category_order")
            or ordering_rules.get("block_type_order")
            or ordering_rules.get("required_block_categories")
        )
    explicit_order = _string_list(
        contract.get("category_order")
        or contract.get("block_type_order")
        or contract.get("block_category_order")
    )
    return _merge_ordered(nested_order + explicit_order + list(required_block_categories))


def _ordering_rule_ref(contracts: Sequence[_ContractContext]) -> str:
    refs = _unique_texts([contract.ordering_rule_ref for contract in contracts])
    return refs[0] if refs else "contract_priority_block_type_block_id"


def _combined_category_order(contracts: Sequence[_ContractContext]) -> list[str]:
    return _merge_ordered(
        [category for contract in contracts for category in contract.category_order]
    )


def _ordering_key(block: _BlockContext, category_order: Sequence[str]) -> list[Any]:
    try:
        category_index = category_order.index(block.block_type)
    except ValueError:
        category_index = len(category_order)
    return [category_index, block.block_type, block.block_id]


def _block_manifest_entry(
    block: _BlockContext,
    *,
    ordering_key: Sequence[Any],
    assembly_rule_ref: str,
) -> dict[str, Any]:
    return {
        "block_id": block.block_id,
        "block_type": block.block_type,
        "phase_ref": block.phase_ref,
        "provenance_ref": block.provenance_ref,
        "block_trace_ref": block.block_trace_ref,
        "source_version_refs": block.source_version_refs,
        "resolved_version_id": block.resolved_version_id,
        "view_membership": [
            view_type for view_type in REQUIRED_VIEW_TYPES if view_type in block.view_tags
        ],
        "ordering_key": list(ordering_key),
        "assembly_rule_ref": assembly_rule_ref,
    }


def _inclusion_rule_ref(
    contracts: Sequence[_ContractContext], view_type: str
) -> str:
    for contract in contracts:
        inclusion_rules = contract.raw.get("view_inclusion_rule_refs")
        if isinstance(inclusion_rules, Mapping):
            rule_ref = _text(inclusion_rules.get(view_type))
            if rule_ref:
                return rule_ref
    return f"{view_type}_tag_membership"


def _single_view_validation_errors(
    *,
    view_type: str,
    block_refs: Sequence[str],
    included_block_refs: Sequence[str],
    excluded_block_refs: Sequence[Mapping[str, Any]],
    trace_index: Mapping[str, Mapping[str, Any]],
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    block_ref_set = set(block_refs)
    included_set = set(included_block_refs)
    if not included_set.issubset(block_ref_set):
        errors.append(
            _validation_error(
                "VIEW_SCOPE_DRIFT",
                "included_block_refs",
                view_type,
                "view includes a block outside ReportPackage.block_refs",
            )
        )
    for block_id in included_block_refs:
        trace_entry = trace_index.get(block_id, {})
        required_trace_fields = {
            "block_trace_ref",
            "provenance_ref",
            "resolved_version_id",
            "package_id",
            "source_output_block_ref",
        }
        missing = sorted(
            field for field in required_trace_fields if not _text(trace_entry.get(field))
        )
        if missing:
            errors.append(
                _validation_error(
                    "TRACE_INDEX_INCOMPLETE",
                    ",".join(missing),
                    block_id,
                    "view trace_index is missing required trace fields",
                )
            )
    excluded_ids = {_text(item.get("block_id")) for item in excluded_block_refs}
    expected_excluded_ids = block_ref_set - included_set
    if excluded_ids != expected_excluded_ids:
        errors.append(
            _validation_error(
                "EXCLUSION_REASON_LOSS",
                "excluded_block_refs",
                view_type,
                "view exclusions do not cover every package block omitted from the view",
            )
        )
    for item in excluded_block_refs:
        if not _text(item.get("reason_code")):
            errors.append(
                _validation_error(
                    "EXCLUSION_REASON_LOSS",
                    "reason_code",
                    _text(item.get("block_id")) or view_type,
                    "excluded block entry must include a concrete reason_code",
                )
            )
    return errors


def _view_validation_errors(
    *,
    block_refs: Sequence[str],
    technical_view: TechnicalView | ExecutiveView,
    executive_view: TechnicalView | ExecutiveView,
) -> list[dict[str, Any]]:
    errors: list[dict[str, Any]] = []
    for view in (technical_view, executive_view):
        if view.validation_errors:
            errors.extend(view.validation_errors)
        if not set(view.included_block_refs).issubset(set(block_refs)):
            errors.append(
                _validation_error(
                    "VIEW_SCOPE_DRIFT",
                    "included_block_refs",
                    view.view_id,
                    "view includes a block outside the package",
                )
            )
    return errors


def _stable_id(prefix: str, material: Mapping[str, Any]) -> str:
    return f"{prefix}:{_stable_hash(material)[:24]}"


def _version_hash(material: Mapping[str, Any]) -> str:
    clean_material = {
        key: value
        for key, value in material.items()
        if key
        not in {
            "version_hash",
            "version_id",
            "created_at",
            "updated_at",
            "produced_at",
        }
    }
    return "sha256:" + _stable_hash(clean_material)


def _stable_hash(material: Any) -> str:
    return hashlib.sha256(_stable_json(material).encode("utf-8")).hexdigest()


def _stable_json(material: Any) -> str:
    return json.dumps(material, sort_keys=True, separators=(",", ":"), default=str)
