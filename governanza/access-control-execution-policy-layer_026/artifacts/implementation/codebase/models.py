"""Output models for motor_026."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from typing import Any, Dict, List, Optional


@dataclass(frozen=True)
class PolicyDecision:
    decision_id: str
    request_id: str
    actor_id: str
    motor_id: str
    stage_name: str
    action: str
    target_ref: str
    target_type: str
    status: str
    reason_code: str
    decision_basis: List[str]
    evaluated_at: str
    policy_version: str
    run_id: str
    correlation_id: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PolicyViolationEvent:
    violation_id: str
    decision_id: str
    request_id: str
    severity: str
    violated_rule_ref: str
    actor_id: str
    motor_id: str
    action: str
    target_ref: str
    observed_at: str
    reason_code: str
    failed_authority_refs: List[str]
    evidence_refs: List[str]

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class AccessAuditRecord:
    audit_id: str
    decision_id: str
    request_snapshot_ref: str
    request_snapshot: Dict[str, Any]
    evaluated_policy_refs: List[str]
    authority_refs: List[str]
    result_status: str
    actor_id: str
    motor_id: str
    action: str
    target_ref: str
    run_id: str
    correlation_id: str
    decision_reason_code: str
    provenance_refs: List[str]
    created_at: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class ConditionalExecutionRequirement:
    requirement_id: str
    decision_id: str
    condition_type: str
    required_evidence: str
    responsible_role: str
    expires_at: str
    verification_status: str
    policy_ref: str
    condition_ref: str

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)


@dataclass(frozen=True)
class PolicyEvaluationResult:
    policy_decision: PolicyDecision
    policy_violation_event: Optional[PolicyViolationEvent]
    access_audit_record: AccessAuditRecord
    conditional_execution_requirement: Optional[ConditionalExecutionRequirement]

    def to_dict(self) -> Dict[str, Any]:
        return {
            "policy_decision": self.policy_decision.to_dict(),
            "policy_violation_event": (
                self.policy_violation_event.to_dict()
                if self.policy_violation_event
                else None
            ),
            "access_audit_record": self.access_audit_record.to_dict(),
            "conditional_execution_requirement": (
                self.conditional_execution_requirement.to_dict()
                if self.conditional_execution_requirement
                else None
            ),
        }

