"""Deterministic implementation for motor_014.

The engine converts activated inference cases and authorized phase contracts
into inference records, tension records, gap agendas, and validation agendas.
It does not activate cases, verify claims, produce reports, ingest sources, or
mutate upstream records.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import asdict, dataclass, is_dataclass, replace
import copy
import hashlib
import json
from typing import Any

from .errors import DecisionCoreInferenceError
from .models import (
    DecisionCoreOutput,
    EvidenceRef,
    GapAgenda,
    GapItem,
    InferenceRecord,
    Tension,
    ValidationAgenda,
    ValidationItem,
)


MOTOR_ID = "motor_014"
DEFAULT_RULE_VERSION = "dicie_rules_v1"
DEFAULT_PRODUCED_AT = "1970-01-01T00:00:00Z"
REQUIRED_ALLOWED_OUTPUTS = frozenset(
    {"inference_record", "tension_record", "gap_agenda", "validation_agenda"}
)
FORBIDDEN_OUTPUT_KEYS = frozenset(
    {
        "final_report",
        "report",
        "report_block",
        "report_blocks",
        "rendered_document",
        "executive_summary",
        "technical_view",
        "verified_claim",
        "verified_claims",
        "verification_result",
        "field_evidence",
        "field_evidence_object",
        "claim_is_true",
        "decision_grade",
    }
)
REAL_EVIDENCE_LEVELS = frozenset({"contextual", "validation_data", "field_evidence"})
STRONG_EVIDENCE_LEVELS = frozenset({"validation_data", "field_evidence"})
SYNTHETIC_CLASSES = frozenset({"synthetic_support"})
SYNTHETIC_LEVELS = frozenset({"synthetic"})
SUPPORTIVE_TOKENS = frozenset(
    {"adequate", "sufficient", "supports", "support", "pass", "stable", "ok"}
)
ADVERSE_TOKENS = frozenset(
    {"failure", "fail", "risk", "conflict", "insufficient", "gap", "degraded"}
)
PRIORITY_RANK = {"blocking": 0, "high": 1, "medium": 2, "low": 3}


@dataclass(frozen=True)
class _ContractContext:
    raw: Mapping[str, Any]
    contract_id: str
    phase_id: str
    contract_version: str
    handoff_target: str


@dataclass(frozen=True)
class _TensionSpec:
    tension_type: str
    severity: str
    source_refs: list[str]
    description: str
    requires_validation: bool


@dataclass(frozen=True)
class _GapSpec:
    gap_type: str
    affected_ref_kind: str
    affected_ref: str | None
    tension_index: int | None
    missing_condition: str
    required_downstream_action: str
    priority: str
    source_refs: list[str]
    required_evidence_level: str
    validation_reason: str


class DecisionCoreInferenceEngine:
    """Core deterministic interface for Decision Core / Inference Engine."""

    def __init__(
        self,
        *,
        rule_version: str = DEFAULT_RULE_VERSION,
        produced_at: str = DEFAULT_PRODUCED_AT,
    ) -> None:
        self.rule_version = _require_text(
            rule_version, "rule_version", "INVALID_INPUT_TYPE"
        )
        self.produced_at = _require_text(
            produced_at, "produced_at", "INVALID_INPUT_TYPE"
        )

    def run(
        self,
        *,
        inference_cases: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
    ) -> list[DecisionCoreOutput]:
        """Validate the full batch and emit deterministic outputs per case."""

        case_items = _as_record_list("inference_cases", inference_cases)
        contract_items = _as_record_list("phase_contracts", phase_contracts)
        contract_index = self._index_contracts(contract_items)
        self._validate_case_ids(case_items)

        outputs: list[DecisionCoreOutput] = []
        for case in sorted(case_items, key=lambda item: str(item.get("case_id"))):
            normalized_case = copy.deepcopy(case)
            contract = self._contract_for_case(normalized_case, contract_index)
            output = self._emit_for_case(normalized_case, contract)
            _assert_output_contract(output)
            outputs.append(output)
        return outputs

    def infer(
        self,
        *,
        inference_cases: Sequence[Mapping[str, Any]],
        phase_contracts: Sequence[Mapping[str, Any]],
    ) -> list[DecisionCoreOutput]:
        """Alias for callers that name the operation by the motor purpose."""

        return self.run(
            inference_cases=inference_cases,
            phase_contracts=phase_contracts,
        )

    def _index_contracts(
        self, phase_contracts: list[Mapping[str, Any]]
    ) -> dict[str, _ContractContext]:
        by_phase: dict[str, list[Mapping[str, Any]]] = {}
        for index, contract in enumerate(phase_contracts):
            phase_id = _require_mapping_text(
                contract,
                "phase_id",
                f"phase_contracts[{index}].phase_id",
                "PHASE_CONTRACT_VIOLATION",
            )
            by_phase.setdefault(phase_id, []).append(contract)

        result: dict[str, _ContractContext] = {}
        for phase_id, contracts in by_phase.items():
            canonical_contracts = {_stable_json(item) for item in contracts}
            if len(canonical_contracts) > 1:
                raise DecisionCoreInferenceError(
                    code="PHASE_CONTRACT_VIOLATION",
                    message="multiple contradictory contracts exist for one phase_id",
                    field=f"phase_contracts[{phase_id}]",
                )
            contract = contracts[0]
            result[phase_id] = self._parse_contract(contract)
        return result

    def _parse_contract(self, contract: Mapping[str, Any]) -> _ContractContext:
        contract_id = _require_mapping_text(
            contract,
            "contract_id",
            "phase_contract.contract_id",
            "PHASE_CONTRACT_VIOLATION",
        )
        phase_id = _require_mapping_text(
            contract,
            "phase_id",
            "phase_contract.phase_id",
            "PHASE_CONTRACT_VIOLATION",
        )
        contract_version = _require_mapping_text(
            contract,
            "contract_version",
            "phase_contract.contract_version",
            "PHASE_CONTRACT_VIOLATION",
        )
        allowed_inputs = _string_set(contract.get("allowed_inputs"))
        if "inference_cases" not in allowed_inputs:
            raise DecisionCoreInferenceError(
                code="PHASE_CONTRACT_VIOLATION",
                message="phase contract does not authorize inference_cases input",
                field=f"phase_contracts[{contract_id}].allowed_inputs",
            )
        allowed_outputs = _string_set(contract.get("allowed_outputs"))
        missing_outputs = sorted(REQUIRED_ALLOWED_OUTPUTS - allowed_outputs)
        if missing_outputs:
            raise DecisionCoreInferenceError(
                code="PHASE_CONTRACT_VIOLATION",
                message="phase contract omits required motor_014 outputs",
                field=f"phase_contracts[{contract_id}].allowed_outputs",
                validation_records=[
                    {"field": item, "reason_code": "OUTPUT_NOT_AUTHORIZED"}
                    for item in missing_outputs
                ],
            )
        output_limits = contract.get("output_limits", {})
        if isinstance(output_limits, Mapping):
            if output_limits.get("may_verify_claims") is True:
                raise DecisionCoreInferenceError(
                    code="PHASE_CONTRACT_VIOLATION",
                    message="phase contract contradicts motor_014 verification limit",
                    field=f"phase_contracts[{contract_id}].output_limits",
                )
            if output_limits.get("may_render_reports") is True:
                raise DecisionCoreInferenceError(
                    code="PHASE_CONTRACT_VIOLATION",
                    message="phase contract contradicts motor_014 reporting limit",
                    field=f"phase_contracts[{contract_id}].output_limits",
                )
        handoff_target = _handoff_target(contract.get("handoff_rules"))
        if not handoff_target:
            raise DecisionCoreInferenceError(
                code="PHASE_CONTRACT_VIOLATION",
                message="phase contract must declare a validation handoff target",
                field=f"phase_contracts[{contract_id}].handoff_rules",
            )
        return _ContractContext(
            raw=contract,
            contract_id=contract_id,
            phase_id=phase_id,
            contract_version=contract_version,
            handoff_target=handoff_target,
        )

    def _validate_case_ids(self, inference_cases: list[Mapping[str, Any]]) -> None:
        seen: set[str] = set()
        failures: list[dict[str, Any]] = []
        for index, case in enumerate(inference_cases):
            case_id = _text(case.get("case_id"))
            if not case_id:
                failures.append(
                    {
                        "field": f"inference_cases[{index}].case_id",
                        "reason_code": "CASE_ID_REQUIRED",
                    }
                )
                continue
            if case_id in seen:
                failures.append(
                    {
                        "field": f"inference_cases[{index}].case_id",
                        "reason_code": "DUPLICATE_CASE_ID",
                    }
                )
            seen.add(case_id)
        if failures:
            raise DecisionCoreInferenceError(
                code="CASE_ID_REQUIRED",
                message="case_id must be non-empty and unique within the batch",
                field=", ".join(item["field"] for item in failures),
                validation_records=failures,
            )

    def _contract_for_case(
        self,
        case: Mapping[str, Any],
        contract_index: Mapping[str, _ContractContext],
    ) -> _ContractContext:
        case_id = _require_mapping_text(
            case,
            "case_id",
            "inference_case.case_id",
            "CASE_ID_REQUIRED",
        )
        case_status = _text(case.get("case_status"))
        activation_record_ref = _text(case.get("activation_record_ref"))
        trigger_log_ref = _text(case.get("trigger_log_ref"))
        if case_status != "activated" or not activation_record_ref or not trigger_log_ref:
            raise DecisionCoreInferenceError(
                code="INFERENCE_CASE_NOT_ACTIVATED",
                message="inference case must be activated by motor_013",
                field=f"inference_cases[{case_id}]",
            )
        phase_id = _require_mapping_text(
            case,
            "phase_id",
            f"inference_cases[{case_id}].phase_id",
            "PHASE_CONTRACT_MISSING",
        )
        contract = contract_index.get(phase_id)
        if contract is None:
            raise DecisionCoreInferenceError(
                code="PHASE_CONTRACT_MISSING",
                message="no matching PhaseContract exists for the case phase_id",
                field=f"inference_cases[{case_id}].phase_id",
            )
        return contract

    def _emit_for_case(
        self, case: Mapping[str, Any], contract: _ContractContext
    ) -> DecisionCoreOutput:
        case_id = _require_mapping_text(
            case, "case_id", "inference_case.case_id", "CASE_ID_REQUIRED"
        )
        phase_id = _require_mapping_text(
            case, "phase_id", f"inference_cases[{case_id}].phase_id", "INVALID_INPUT_TYPE"
        )
        if phase_id != contract.phase_id:
            raise DecisionCoreInferenceError(
                code="PHASE_CONTRACT_VIOLATION",
                message="case phase_id does not match selected phase contract",
                field=f"inference_cases[{case_id}].phase_id",
            )
        activation_record_ref = _require_mapping_text(
            case,
            "activation_record_ref",
            f"inference_cases[{case_id}].activation_record_ref",
            "INFERENCE_CASE_NOT_ACTIVATED",
        )
        trigger_log_ref = _require_mapping_text(
            case,
            "trigger_log_ref",
            f"inference_cases[{case_id}].trigger_log_ref",
            "INFERENCE_CASE_NOT_ACTIVATED",
        )
        analysis_question = _require_mapping_text(
            case,
            "analysis_question",
            f"inference_cases[{case_id}].analysis_question",
            "INVALID_INPUT_TYPE",
        )
        lineage_refs = _sorted_unique(
            [
                *_required_string_list(
                    case.get("lineage_refs"),
                    f"inference_cases[{case_id}].lineage_refs",
                    "PROVENANCE_REQUIRED",
                    allow_empty=False,
                ),
                activation_record_ref,
                trigger_log_ref,
                contract.contract_id,
            ]
        )
        evidence_refs, raw_evidence = self._normalize_evidence_refs(case)

        evidence_ids = [item.evidence_id for item in evidence_refs]
        real_evidence = [
            item
            for item in evidence_refs
            if item.evidence_level in REAL_EVIDENCE_LEVELS
            and item.source_class not in SYNTHETIC_CLASSES
        ]
        strong_evidence = [
            item for item in real_evidence if item.evidence_level in STRONG_EVIDENCE_LEVELS
        ]
        synthetic_support_present = any(
            item.source_class in SYNTHETIC_CLASSES
            or item.evidence_level in SYNTHETIC_LEVELS
            for item in evidence_refs
        )
        synthetic_only = bool(evidence_refs) and not real_evidence
        conflict_sources = _conflict_sources(raw_evidence)
        opportunity_sources = _opportunity_sources(raw_evidence)

        decision_trace = [
            "case_status_activated",
            "phase_contract_authorized",
            "evidence_refs_validated",
        ]
        tension_specs: list[_TensionSpec] = []
        gap_specs: list[_GapSpec] = []

        if synthetic_support_present:
            decision_trace.append("synthetic_support_flagged")

        if synthetic_only:
            inference_state = "hypothesis_only"
            decision_trace.append("state_hypothesis_only_synthetic_only")
            tension_specs.append(
                _TensionSpec(
                    tension_type="missing_evidence",
                    severity="high",
                    source_refs=evidence_ids,
                    description="only synthetic support is present; real evidence is required",
                    requires_validation=True,
                )
            )
            gap_specs.append(
                _GapSpec(
                    gap_type="missing_validation_data",
                    affected_ref_kind="inference",
                    affected_ref=None,
                    tension_index=0,
                    missing_condition="validation data or field evidence for synthetic-only support",
                    required_downstream_action=(
                        f"request validation data through {contract.handoff_target}"
                    ),
                    priority="high",
                    source_refs=evidence_ids,
                    required_evidence_level="validation_data",
                    validation_reason=(
                        "synthetic support cannot be treated as evidentiary support"
                    ),
                )
            )
        elif conflict_sources:
            inference_state = "blocked_by_gap"
            decision_trace.append("state_blocked_by_gap_unresolved_conflict")
            tension_specs.append(
                _TensionSpec(
                    tension_type="conflict",
                    severity="blocking",
                    source_refs=conflict_sources,
                    description="source references contain unresolved conflicting signals",
                    requires_validation=True,
                )
            )
            gap_specs.append(
                _GapSpec(
                    gap_type="unresolved_conflict",
                    affected_ref_kind="tension",
                    affected_ref=None,
                    tension_index=0,
                    missing_condition="deterministic resolution path for conflicting evidence",
                    required_downstream_action=(
                        f"route conflict validation through {contract.handoff_target}"
                    ),
                    priority="blocking",
                    source_refs=conflict_sources,
                    required_evidence_level="validation_data",
                    validation_reason="conflicting evidence cannot be collapsed by motor_014",
                )
            )
        elif not real_evidence:
            inference_state = "blocked_by_gap"
            decision_trace.append("state_blocked_by_gap_missing_real_evidence")
            tension_specs.append(
                _TensionSpec(
                    tension_type="missing_evidence",
                    severity="blocking",
                    source_refs=[case_id],
                    description="no real evidence reference is available for bounded inference",
                    requires_validation=True,
                )
            )
            gap_specs.append(
                _GapSpec(
                    gap_type="missing_evidence",
                    affected_ref_kind="inference",
                    affected_ref=None,
                    tension_index=0,
                    missing_condition="at least one real evidence reference with provenance",
                    required_downstream_action=(
                        f"request evidence acquisition through {contract.handoff_target}"
                    ),
                    priority="blocking",
                    source_refs=[case_id],
                    required_evidence_level="validation_data",
                    validation_reason="no real evidence exists for the activated case",
                )
            )
        elif len(real_evidence) == 1 and not strong_evidence:
            inference_state = "blocked_by_gap"
            decision_trace.append("state_blocked_by_gap_sparse_contextual_evidence")
            source_refs = [real_evidence[0].evidence_id]
            tension_specs.append(
                _TensionSpec(
                    tension_type="missing_evidence",
                    severity="medium",
                    source_refs=source_refs,
                    description="single contextual evidence reference is insufficient",
                    requires_validation=True,
                )
            )
            gap_specs.append(
                _GapSpec(
                    gap_type="missing_validation_data",
                    affected_ref_kind="inference",
                    affected_ref=None,
                    tension_index=0,
                    missing_condition="validation data for sparse contextual inference case",
                    required_downstream_action=(
                        f"request validation data through {contract.handoff_target}"
                    ),
                    priority="medium",
                    source_refs=source_refs,
                    required_evidence_level="validation_data",
                    validation_reason="single contextual reference cannot bound the inference",
                )
            )
        else:
            inference_state = "bounded_inference"
            decision_trace.append("state_bounded_inference_real_evidence")
            if not strong_evidence:
                source_refs = [item.evidence_id for item in real_evidence]
                decision_trace.append("gap_validation_data_required")
                tension_specs.append(
                    _TensionSpec(
                        tension_type="missing_evidence",
                        severity="medium",
                        source_refs=source_refs,
                        description="contextual evidence bounds the inference but lacks validation data",
                        requires_validation=True,
                    )
                )
                gap_specs.append(
                    _GapSpec(
                        gap_type="missing_validation_data",
                        affected_ref_kind="inference",
                        affected_ref=None,
                        tension_index=0,
                        missing_condition="site-level backup power validation data",
                        required_downstream_action=(
                            f"request validation data through {contract.handoff_target}"
                        ),
                        priority="medium",
                        source_refs=source_refs,
                        required_evidence_level="validation_data",
                        validation_reason="bounded contextual inference still requires validation data",
                    )
                )

        if opportunity_sources:
            tension_specs.append(
                _TensionSpec(
                    tension_type="opportunity",
                    severity="low",
                    source_refs=opportunity_sources,
                    description="source references contain an opportunity signal for validation planning",
                    requires_validation=False,
                )
            )
            decision_trace.append("opportunity_signal_recorded")

        content_version_payload = {
            "case_id": case_id,
            "contract_id": contract.contract_id,
            "contract_version": contract.contract_version,
            "rule_version": self.rule_version,
            "analysis_question": analysis_question,
            "inference_state": inference_state,
            "evidence_refs": [item.to_dict() for item in evidence_refs],
            "lineage_refs": lineage_refs,
            "decision_trace": decision_trace,
            "synthetic_support_present": synthetic_support_present,
            "tension_specs": [asdict(item) for item in tension_specs],
            "gap_specs": [asdict(item) for item in gap_specs],
        }
        version_id = f"dicie_v1_{_digest(content_version_payload)[:16]}"
        inference_id = f"{MOTOR_ID}:inference:{_safe_part(case_id)}:{version_id}"
        gap_agenda_id = (
            f"{MOTOR_ID}:gap_agenda:{_digest([inference_id, version_id])[:20]}"
        )
        validation_agenda_id = (
            f"{MOTOR_ID}:validation_agenda:{_digest([inference_id, version_id])[:20]}"
        )

        inference_record = InferenceRecord(
            inference_id=inference_id,
            motor_id=MOTOR_ID,
            case_id=case_id,
            activation_record_ref=activation_record_ref,
            trigger_log_ref=trigger_log_ref,
            phase_id=phase_id,
            phase_contract_ref=contract.contract_id,
            contract_version=contract.contract_version,
            analysis_question=analysis_question,
            inference_state=inference_state,
            inference_basis=_sorted_unique(
                [activation_record_ref, trigger_log_ref, *evidence_ids]
            ),
            evidence_refs=evidence_refs,
            lineage_refs=lineage_refs,
            rule_version=self.rule_version,
            decision_trace=decision_trace,
            synthetic_support_present=synthetic_support_present,
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_id=version_id,
            version_hash="",
            source_ref=case_id,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=_optional_parent_id(case),
        )
        inference_record = _with_version_hash(inference_record)

        tension_ids = [
            f"{MOTOR_ID}:tension:{_digest([inference_id, index, version_id])[:20]}"
            for index, _item in enumerate(tension_specs, start=1)
        ]
        gap_items: list[GapItem] = []
        validation_items: list[ValidationItem] = []
        gap_ids_by_tension: dict[int, list[str]] = {}
        for index, spec in enumerate(gap_specs, start=1):
            if spec.affected_ref_kind == "tension" and spec.tension_index is not None:
                affected_ref = tension_ids[spec.tension_index]
            else:
                affected_ref = spec.affected_ref or inference_id
            gap_item_id = (
                f"{MOTOR_ID}:gap_item:{_digest([gap_agenda_id, index])[:20]}"
            )
            gap_item = GapItem(
                gap_item_id=gap_item_id,
                gap_type=spec.gap_type,
                affected_ref=affected_ref,
                missing_condition=spec.missing_condition,
                required_downstream_action=spec.required_downstream_action,
                priority=spec.priority,
                source_refs=_sorted_unique(spec.source_refs),
            )
            gap_items.append(gap_item)
            if spec.tension_index is not None:
                gap_ids_by_tension.setdefault(spec.tension_index, []).append(gap_item_id)
            validation_item_id = (
                f"{MOTOR_ID}:validation_item:"
                f"{_digest([validation_agenda_id, gap_item_id, index])[:20]}"
            )
            validation_items.append(
                ValidationItem(
                    validation_item_id=validation_item_id,
                    gap_item_id=gap_item_id,
                    required_evidence_level=spec.required_evidence_level,
                    reason=spec.validation_reason,
                    handoff_target=contract.handoff_target,
                    priority=spec.priority,
                    source_refs=_sorted_unique([gap_item_id, *spec.source_refs]),
                )
            )

        tensions: list[Tension] = []
        for index, spec in enumerate(tension_specs, start=1):
            tension = Tension(
                tension_id=tension_ids[index - 1],
                motor_id=MOTOR_ID,
                inference_id=inference_id,
                case_id=case_id,
                phase_contract_ref=contract.contract_id,
                contract_version=contract.contract_version,
                tension_type=spec.tension_type,
                severity=spec.severity,
                source_refs=_sorted_unique(spec.source_refs),
                description=spec.description,
                requires_validation=spec.requires_validation,
                related_gap_item_ids=_sorted_unique(gap_ids_by_tension.get(index - 1, [])),
                lineage_refs=lineage_refs,
                rule_version=self.rule_version,
                created_at=self.produced_at,
                updated_at=self.produced_at,
                version_id=version_id,
                version_hash="",
                source_ref=inference_id,
                produced_by_motor=MOTOR_ID,
                produced_at=self.produced_at,
                parent_id=None,
            )
            tensions.append(_with_version_hash(tension))

        priority_order = [
            item.gap_item_id
            for item in sorted(
                gap_items,
                key=lambda item: (PRIORITY_RANK.get(item.priority, 99), item.gap_item_id),
            )
        ]
        validation_dependency_refs = [item.validation_item_id for item in validation_items]
        gap_agenda = GapAgenda(
            gap_agenda_id=gap_agenda_id,
            motor_id=MOTOR_ID,
            inference_id=inference_id,
            case_id=case_id,
            phase_contract_ref=contract.contract_id,
            contract_version=contract.contract_version,
            gap_items=gap_items,
            priority_order=priority_order,
            validation_dependency_refs=validation_dependency_refs,
            lineage_refs=lineage_refs,
            rule_version=self.rule_version,
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_id=version_id,
            version_hash="",
            source_ref=inference_id,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )
        gap_agenda = _with_version_hash(gap_agenda)

        required_evidence_level = _strongest_required_level(validation_items)
        validation_agenda = ValidationAgenda(
            validation_agenda_id=validation_agenda_id,
            motor_id=MOTOR_ID,
            inference_id=inference_id,
            case_id=case_id,
            gap_agenda_id=gap_agenda_id,
            phase_contract_ref=contract.contract_id,
            contract_version=contract.contract_version,
            validation_items=validation_items,
            required_evidence_level=required_evidence_level,
            handoff_target=contract.handoff_target,
            lineage_refs=lineage_refs,
            rule_version=self.rule_version,
            created_at=self.produced_at,
            updated_at=self.produced_at,
            version_id=version_id,
            version_hash="",
            source_ref=gap_agenda_id,
            produced_by_motor=MOTOR_ID,
            produced_at=self.produced_at,
            parent_id=None,
        )
        validation_agenda = _with_version_hash(validation_agenda)

        return DecisionCoreOutput(
            inference_record=inference_record,
            tension_record=tensions,
            gap_agenda=gap_agenda,
            validation_agenda=validation_agenda,
        )

    def _normalize_evidence_refs(
        self, case: Mapping[str, Any]
    ) -> tuple[list[EvidenceRef], list[Mapping[str, Any]]]:
        case_id = _text(case.get("case_id")) or "unknown_case"
        evidence_values = case.get("evidence_refs")
        if not isinstance(evidence_values, Sequence) or isinstance(
            evidence_values, (str, bytes, bytearray)
        ):
            raise DecisionCoreInferenceError(
                code="INVALID_INPUT_TYPE",
                message="evidence_refs must be a list of evidence reference objects",
                field=f"inference_cases[{case_id}].evidence_refs",
            )
        normalized: list[EvidenceRef] = []
        raw_items: list[Mapping[str, Any]] = []
        failures: list[dict[str, Any]] = []
        for index, item in enumerate(evidence_values):
            if not isinstance(item, Mapping):
                raise DecisionCoreInferenceError(
                    code="INVALID_INPUT_TYPE",
                    message="each evidence_refs item must be a structured object",
                    field=f"inference_cases[{case_id}].evidence_refs[{index}]",
                )
            evidence_id = _text(
                item.get("evidence_id")
                or item.get("source_ref")
                or item.get("record_id")
                or item.get("id")
            )
            source_class = _text(item.get("source_class"))
            evidence_level = _text(item.get("evidence_level"))
            provenance_ref = _text(item.get("provenance_ref"))
            lineage_ref = _text(item.get("lineage_ref"))
            missing = []
            if not evidence_id:
                missing.append("evidence_id")
            if not source_class:
                missing.append("source_class")
            if not evidence_level:
                missing.append("evidence_level")
            if not provenance_ref:
                missing.append("provenance_ref")
            if not lineage_ref:
                missing.append("lineage_ref")
            if missing:
                failures.extend(
                    {
                        "field": (
                            f"inference_cases[{case_id}].evidence_refs[{index}].{field}"
                        ),
                        "reason_code": "PROVENANCE_REQUIRED",
                    }
                    for field in missing
                )
                continue
            normalized.append(
                EvidenceRef(
                    evidence_id=evidence_id,
                    source_class=source_class,
                    evidence_level=evidence_level,
                    provenance_ref=provenance_ref,
                    lineage_ref=lineage_ref,
                )
            )
            raw_items.append(dict(item))
        if failures:
            raise DecisionCoreInferenceError(
                code="PROVENANCE_REQUIRED",
                message="evidence references must include identity, class, level, provenance, and lineage",
                field=", ".join(item["field"] for item in failures),
                validation_records=failures,
            )
        normalized_with_raw = sorted(
            zip(normalized, raw_items, strict=True),
            key=lambda pair: pair[0].evidence_id,
        )
        return (
            [pair[0] for pair in normalized_with_raw],
            [pair[1] for pair in normalized_with_raw],
        )


def run_decision_core_inference(
    *,
    inference_cases: Sequence[Mapping[str, Any]],
    phase_contracts: Sequence[Mapping[str, Any]],
    rule_version: str = DEFAULT_RULE_VERSION,
    produced_at: str = DEFAULT_PRODUCED_AT,
) -> list[dict[str, Any]]:
    """Convenience wrapper returning JSON-compatible dictionaries."""

    engine = DecisionCoreInferenceEngine(
        rule_version=rule_version,
        produced_at=produced_at,
    )
    return [
        output.to_dict()
        for output in engine.run(
            inference_cases=inference_cases,
            phase_contracts=phase_contracts,
        )
    ]


def _as_record_list(field: str, value: Any) -> list[Mapping[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise DecisionCoreInferenceError(
            code="INVALID_INPUT_TYPE",
            message=f"{field} must be a list of structured records",
            field=field,
        )
    result: list[Mapping[str, Any]] = []
    for index, item in enumerate(value):
        if not isinstance(item, Mapping):
            raise DecisionCoreInferenceError(
                code="INVALID_INPUT_TYPE",
                message=f"{field} items must be structured records",
                field=f"{field}[{index}]",
            )
        result.append(copy.deepcopy(item))
    return result


def _require_mapping_text(
    record: Mapping[str, Any], key: str, field: str, code: str
) -> str:
    value = _text(record.get(key))
    if not value:
        raise DecisionCoreInferenceError(
            code=code,
            message=f"{field} is required",
            field=field,
        )
    return value


def _require_text(value: Any, field: str, code: str) -> str:
    text = _text(value)
    if not text:
        raise DecisionCoreInferenceError(
            code=code,
            message=f"{field} is required",
            field=field,
        )
    return text


def _text(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    return None


def _string_set(value: Any) -> frozenset[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        return frozenset()
    return frozenset(item.strip() for item in value if isinstance(item, str) and item.strip())


def _required_string_list(
    value: Any, field: str, code: str, *, allow_empty: bool
) -> list[str]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes, bytearray)):
        raise DecisionCoreInferenceError(
            code=code,
            message=f"{field} must be a list of non-empty strings",
            field=field,
        )
    result: list[str] = []
    for index, item in enumerate(value):
        text = _text(item)
        if not text:
            raise DecisionCoreInferenceError(
                code=code,
                message=f"{field} must contain only non-empty strings",
                field=f"{field}[{index}]",
            )
        result.append(text)
    if not allow_empty and not result:
        raise DecisionCoreInferenceError(
            code=code,
            message=f"{field} must not be empty",
            field=field,
        )
    return result


def _handoff_target(value: Any) -> str | None:
    if isinstance(value, str) and value.strip():
        return value.strip()
    if isinstance(value, Mapping):
        for key in (
            "validation",
            "validation_agenda",
            "validation_target",
            "gap_validation",
            "handoff_target",
            "default",
            "verification",
        ):
            target = _text(value.get(key))
            if target:
                return target
        for child in value.values():
            if isinstance(child, Mapping):
                target = _handoff_target(child)
                if target:
                    return target
            elif isinstance(child, str) and child.strip():
                return child.strip()
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for child in value:
            target = _handoff_target(child)
            if target:
                return target
    return None


def _conflict_sources(evidence_refs: list[Mapping[str, Any]]) -> list[str]:
    explicit: list[str] = []
    supportive: list[str] = []
    adverse: list[str] = []
    for item in evidence_refs:
        evidence_id = _text(
            item.get("evidence_id") or item.get("source_ref") or item.get("record_id")
        )
        if not evidence_id:
            continue
        tokens = _tokens_for_evidence(item)
        if "conflict" in tokens or "inconsistency" in tokens:
            explicit.append(evidence_id)
        if SUPPORTIVE_TOKENS & tokens:
            supportive.append(evidence_id)
        if ADVERSE_TOKENS & tokens:
            adverse.append(evidence_id)
    if explicit:
        return _sorted_unique([*explicit, *supportive, *adverse])
    if supportive and adverse:
        return _sorted_unique([*supportive, *adverse])
    return []


def _opportunity_sources(evidence_refs: list[Mapping[str, Any]]) -> list[str]:
    result: list[str] = []
    for item in evidence_refs:
        evidence_id = _text(
            item.get("evidence_id") or item.get("source_ref") or item.get("record_id")
        )
        if evidence_id and "opportunity" in _tokens_for_evidence(item):
            result.append(evidence_id)
    return _sorted_unique(result)


def _tokens_for_evidence(item: Mapping[str, Any]) -> set[str]:
    fields = (
        "evidence_id",
        "signal",
        "evidence_signal",
        "polarity",
        "tension_type",
        "condition",
        "summary",
        "description",
        "status",
    )
    raw_values: list[Any] = [item.get(field) for field in fields]
    raw_values.extend(_list_like(item.get("tags")))
    raw_values.extend(_list_like(item.get("flags")))
    raw_values.extend(_list_like(item.get("signals")))
    tokens: set[str] = set()
    for value in raw_values:
        if value is None:
            continue
        serialized = json.dumps(value, sort_keys=True, default=str).lower()
        current = []
        for char in serialized:
            if char.isalnum() or char == "_":
                current.append(char)
            else:
                if current:
                    tokens.add("".join(current))
                    current = []
        if current:
            tokens.add("".join(current))
    if item.get("conflict") is True or item.get("is_conflict") is True:
        tokens.add("conflict")
    if item.get("opportunity") is True or item.get("is_opportunity") is True:
        tokens.add("opportunity")
    return tokens


def _list_like(value: Any) -> list[Any]:
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return list(value)
    if value is None:
        return []
    return [value]


def _strongest_required_level(validation_items: list[ValidationItem]) -> str:
    levels = [item.required_evidence_level for item in validation_items]
    if "field_evidence" in levels:
        return "field_evidence"
    return "validation_data"


def _optional_parent_id(case: Mapping[str, Any]) -> str | None:
    for key in ("parent_inference_id", "previous_inference_id", "supersedes_inference_id"):
        value = _text(case.get(key))
        if value:
            return value
    return None


def _sorted_unique(items: Sequence[Any]) -> list[str]:
    return sorted({item for item in items if isinstance(item, str) and item.strip()})


def _safe_part(value: str) -> str:
    chars = [char if char.isalnum() or char in ("_", "-") else "_" for char in value]
    safe = "".join(chars).strip("_")
    return safe or _digest(value)[:12]


def _with_version_hash(record: Any) -> Any:
    payload = record.to_dict() if hasattr(record, "to_dict") else asdict(record)
    version_hash = _version_hash(payload)
    return replace(record, version_hash=version_hash)


def _version_hash(payload: Any) -> str:
    return _digest(_strip_runtime_fields(payload))


def _strip_runtime_fields(value: Any) -> Any:
    if is_dataclass(value):
        value = asdict(value)
    if isinstance(value, Mapping):
        return {
            key: _strip_runtime_fields(child)
            for key, child in value.items()
            if key not in {"created_at", "updated_at", "produced_at", "version_hash"}
        }
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        return [_strip_runtime_fields(item) for item in value]
    return value


def _stable_json(payload: Any) -> str:
    return json.dumps(
        payload,
        sort_keys=True,
        separators=(",", ":"),
        ensure_ascii=True,
        default=str,
    )


def _digest(payload: Any) -> str:
    return hashlib.sha256(_stable_json(payload).encode("utf-8")).hexdigest()


def _assert_output_contract(output: DecisionCoreOutput) -> None:
    payload = output.to_dict()
    forbidden_paths = _forbidden_field_paths(payload)
    if forbidden_paths:
        raise DecisionCoreInferenceError(
            code="REPORTING_OR_VERIFICATION_LEAKAGE",
            message="motor_014 output contains forbidden output fields",
            field=", ".join(forbidden_paths),
        )
    for key in ("inference_record", "gap_agenda", "validation_agenda"):
        _assert_top_level_record(payload[key], key)
    for index, tension in enumerate(payload["tension_record"]):
        _assert_top_level_record(tension, f"tension_record[{index}]")
        if tension["inference_id"] != payload["inference_record"]["inference_id"]:
            raise DecisionCoreInferenceError(
                code="OUTPUT_VALIDATION_ERROR",
                message="tension_record references the wrong inference_id",
                field=f"tension_record[{index}].inference_id",
            )
    inference_id = payload["inference_record"]["inference_id"]
    if payload["gap_agenda"]["inference_id"] != inference_id:
        raise DecisionCoreInferenceError(
            code="OUTPUT_VALIDATION_ERROR",
            message="gap_agenda references the wrong inference_id",
            field="gap_agenda.inference_id",
        )
    if payload["validation_agenda"]["inference_id"] != inference_id:
        raise DecisionCoreInferenceError(
            code="OUTPUT_VALIDATION_ERROR",
            message="validation_agenda references the wrong inference_id",
            field="validation_agenda.inference_id",
        )


def _assert_top_level_record(record: Mapping[str, Any], field: str) -> None:
    required_fields = (
        "motor_id",
        "case_id",
        "phase_contract_ref",
        "contract_version",
        "lineage_refs",
        "rule_version",
        "created_at",
        "updated_at",
        "version_id",
        "version_hash",
        "source_ref",
        "produced_by_motor",
        "produced_at",
        "parent_id",
    )
    missing = [
        item
        for item in required_fields
        if item != "parent_id" and record.get(item) in (None, "", [], {})
    ]
    if record.get("motor_id") != MOTOR_ID or record.get("produced_by_motor") != MOTOR_ID:
        missing.append("motor_id")
    if "parent_id" not in record:
        missing.append("parent_id")
    if missing:
        raise DecisionCoreInferenceError(
            code="OUTPUT_VALIDATION_ERROR",
            message="top-level output record is missing required fields",
            field=f"{field}: {', '.join(sorted(set(missing)))}",
        )


def _forbidden_field_paths(value: Any, path: str = "") -> list[str]:
    paths: list[str] = []
    if isinstance(value, Mapping):
        for key, child in value.items():
            key_text = str(key)
            child_path = f"{path}.{key_text}" if path else key_text
            if key_text in FORBIDDEN_OUTPUT_KEYS:
                paths.append(child_path)
            paths.extend(_forbidden_field_paths(child, child_path))
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes, bytearray)):
        for index, child in enumerate(value):
            paths.extend(_forbidden_field_paths(child, f"{path}[{index}]"))
    return paths
