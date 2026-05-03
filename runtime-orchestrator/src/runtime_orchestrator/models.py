from __future__ import annotations

from dataclasses import asdict, dataclass, field
from enum import Enum
from typing import Any


class MotorRunStatus(str, Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    CACHED = "cached"       # output reused from artifact store
    SKIPPED = "skipped"     # not in requested subset
    FAILED = "failed"
    STUB = "stub"           # adapter not yet implemented, ran as passthrough


class PipelineStatus(str, Enum):
    RUNNING = "running"
    COMPLETED = "completed"
    COMPLETED_WITH_STUBS = "completed_with_stubs"
    FAILED = "failed"
    PARTIAL = "partial"


@dataclass
class MotorRunResult:
    motor_id: str
    status: MotorRunStatus
    inputs_hash: str
    output_hash: str | None = None
    error: str | None = None
    duration_ms: float = 0.0
    adapter_class: str | None = None
    cached_from: str | None = None  # artifact path if CACHED
    implementation_state: str | None = None  # implemented | placeholder | missing
    output_state: str | None = None          # real | stub | unknown

    def to_dict(self) -> dict[str, Any]:
        d = asdict(self)
        d["status"] = self.status.value
        d["truth_state"] = self.truth_state
        return d

    @property
    def truth_state(self) -> str:
        """Operational truth label used by dashboards and governance.

        Distinguishes execution status from epistemically relevant cases like
        cached stub outputs, which must not be treated as healthy completion.
        """
        if self.status == MotorRunStatus.CACHED:
            if self.output_state == "stub":
                return "cached_stub"
            if self.output_state == "real":
                return "cached_real"
            return "cached"
        if self.status == MotorRunStatus.COMPLETED:
            if self.output_state == "real":
                return "completed_real"
            if self.output_state == "stub":
                return "completed_stub"
            return "completed"
        return self.status.value


@dataclass
class PipelineRun:
    run_id: str
    pipeline_id: str
    started_at: str
    completed_at: str | None = None
    runner_pid: int | None = None
    last_heartbeat_at: str | None = None
    status: PipelineStatus = PipelineStatus.RUNNING
    motor_results: dict[str, MotorRunResult] = field(default_factory=dict)
    pipeline_inputs_hash: str | None = None
    error: str | None = None
    subject_definition: dict[str, Any] | None = None
    subject_contract_status: str | None = None
    subject_contract_admissibility: str | None = None
    subject_contract_warning_register: list[dict[str, Any]] = field(default_factory=list)
    ingestion_contract_status: str | None = None
    subject_resolution_state: str | None = None
    asset_authenticity_state: str | None = None
    target_type_classification: str | None = None
    asset_identity_status: str | None = None
    classification_confidence: str | None = None
    target_admissibility_state: str | None = None
    subject_gate_passed: bool | None = None
    subject_gate_reason_register: list[dict[str, Any]] = field(default_factory=list)
    allowed_report_classes: list[str] = field(default_factory=list)
    target_definition: dict[str, Any] | None = None
    asset_context_readiness: str | None = None
    technical_substrate_readiness: str | None = None
    asset_level_evidence_found: bool | None = None
    issuer_only_evidence_found: bool | None = None
    recommended_report_type: str | None = None
    prohibited_report_types: list[str] = field(default_factory=list)
    report_identity_state: str | None = None
    dominant_evidence_scope: str | None = None
    missing_observable_clusters: list[str] = field(default_factory=list)
    evidence_maturity_summary: dict[str, Any] = field(default_factory=dict)
    key_variable_bottlenecks: list[str] = field(default_factory=list)
    report_readiness_reason: str | None = None
    report_type_trace: dict[str, Any] = field(default_factory=dict)
    phase_self_evaluation_summary: dict[str, Any] = field(default_factory=dict)
    previous_run_id: str | None = None
    previous_run_summary: dict[str, Any] = field(default_factory=dict)
    case_delta_summary: dict[str, Any] = field(default_factory=dict)
    source_yield_memory_summary: dict[str, Any] = field(default_factory=dict)
    next_ingestion_priority_update: dict[str, Any] = field(default_factory=dict)
    ingestion_learning_summary: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "run_id": self.run_id,
            "pipeline_id": self.pipeline_id,
            "started_at": self.started_at,
            "completed_at": self.completed_at,
            "runner_pid": self.runner_pid,
            "last_heartbeat_at": self.last_heartbeat_at,
            "status": self.status.value,
            "pipeline_inputs_hash": self.pipeline_inputs_hash,
            "error": self.error,
            "subject_definition": self.subject_definition or {},
            "subject_contract_status": self.subject_contract_status,
            "subject_contract_admissibility": self.subject_contract_admissibility,
            "subject_contract_warning_register": list(self.subject_contract_warning_register),
            "ingestion_contract_status": self.ingestion_contract_status,
            "subject_resolution_state": self.subject_resolution_state,
            "asset_authenticity_state": self.asset_authenticity_state,
            "target_type_classification": self.target_type_classification,
            "asset_identity_status": self.asset_identity_status,
            "classification_confidence": self.classification_confidence,
            "target_admissibility_state": self.target_admissibility_state,
            "subject_gate_passed": self.subject_gate_passed,
            "subject_gate_reason_register": list(self.subject_gate_reason_register),
            "allowed_report_classes": list(self.allowed_report_classes),
            "target_definition": self.target_definition or {},
            "asset_context_readiness": self.asset_context_readiness,
            "technical_substrate_readiness": self.technical_substrate_readiness,
            "asset_level_evidence_found": self.asset_level_evidence_found,
            "issuer_only_evidence_found": self.issuer_only_evidence_found,
            "recommended_report_type": self.recommended_report_type,
            "prohibited_report_types": list(self.prohibited_report_types),
            "report_identity_state": self.report_identity_state,
            "dominant_evidence_scope": self.dominant_evidence_scope,
            "missing_observable_clusters": list(self.missing_observable_clusters),
            "evidence_maturity_summary": dict(self.evidence_maturity_summary),
            "key_variable_bottlenecks": list(self.key_variable_bottlenecks),
            "report_readiness_reason": self.report_readiness_reason,
            "report_type_trace": dict(self.report_type_trace),
            "phase_self_evaluation_summary": dict(self.phase_self_evaluation_summary),
            "previous_run_id": self.previous_run_id,
            "previous_run_summary": dict(self.previous_run_summary),
            "case_delta_summary": dict(self.case_delta_summary),
            "source_yield_memory_summary": dict(self.source_yield_memory_summary),
            "next_ingestion_priority_update": dict(self.next_ingestion_priority_update),
            "ingestion_learning_summary": dict(self.ingestion_learning_summary),
            "motor_results": {mid: r.to_dict() for mid, r in self.motor_results.items()},
            "summary": self._summary(),
            "truth_summary": self._truth_summary(),
        }

    def _summary(self) -> dict[str, int]:
        counts: dict[str, int] = {s.value: 0 for s in MotorRunStatus}
        for r in self.motor_results.values():
            counts[r.status.value] += 1
        return counts

    def _truth_summary(self) -> dict[str, int]:
        counts: dict[str, int] = {
            "implemented_contract": 0,
            "placeholder_contract": 0,
            "missing_contract": 0,
            "completed_real": 0,
            "completed_stub": 0,
            "cached_real": 0,
            "cached_stub": 0,
            "running": 0,
            "pending": 0,
            "failed": 0,
            "skipped": 0,
            "stub": 0,
            "other": 0,
        }
        for r in self.motor_results.values():
            impl_state = r.implementation_state or "missing"
            impl_key = f"{impl_state}_contract"
            if impl_key in counts:
                counts[impl_key] += 1
            truth_state = r.truth_state
            if truth_state in counts:
                counts[truth_state] += 1
            elif r.status.value in counts:
                counts[r.status.value] += 1
            else:
                counts["other"] += 1
        return counts
