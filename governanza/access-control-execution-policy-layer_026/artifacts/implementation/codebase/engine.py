"""Deterministic Access Control / Execution Policy Layer for motor_026.

The engine evaluates one execution request against phase-contract authority,
rights authority, access-class authority, and explicit execution policies. It
does not execute, retry, schedule, mutate contracts, rewrite rights data, or
repair upstream payloads.
"""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
from hashlib import sha256
import json
import re
from typing import Any, Dict, Iterable, List, Optional, Set, Tuple

from .errors import AccessPolicyInputError, UnsafePolicyOutputError
from .models import (
    AccessAuditRecord,
    ConditionalExecutionRequirement,
    PolicyDecision,
    PolicyEvaluationResult,
    PolicyViolationEvent,
)


MOTOR_ID = "motor_026"
DEFAULT_POLICY_VERSION = "motor_026.policy.unavailable"
REQUEST_REQUIRED_FIELDS = (
    "request_id",
    "actor_id",
    "actor_type",
    "motor_id",
    "stage_name",
    "action",
    "target_ref",
    "target_type",
    "requested_at",
    "run_id",
    "correlation_id",
    "declared_purpose",
)
POLICY_REQUIRED_FIELDS = (
    "policy_id",
    "policy_version",
    "scope",
    "effect",
    "provenance_ref",
)
VALID_POLICY_EFFECTS = {"allow", "deny", "conditional"}
POSITIVE_RIGHTS_STATUSES = {
    "active",
    "approved",
    "authorized",
    "cleared",
    "license_valid",
    "permitted",
    "rights_confirmed",
    "valid",
}
CONDITIONAL_RIGHTS_STATUSES = {
    "conditional",
    "requires_approval",
    "requires_review",
    "restricted_with_approval",
}
NEGATIVE_RIGHTS_STATUSES = {
    "blocked",
    "denied",
    "expired",
    "invalid",
    "pending",
    "revoked",
    "unknown",
}
FORBIDDEN_AUTHORITY_MUTATION_MARKERS = (
    "create_phase_contract",
    "update_phase_contract",
    "modify_phase_contract",
    "delete_phase_contract",
    "create_rights_profile",
    "update_rights_profile",
    "modify_rights_profile",
    "delete_rights_profile",
    "create_access_class",
    "update_access_class",
    "modify_access_class",
    "delete_access_class",
    "edit_motor_state",
    "modify_motor_state",
    "rewrite_payload",
    "rewrite_artifact",
    "repair_contract",
    "repair_rights",
)
WILDCARDS = {"*", "all", "any"}


@dataclass(frozen=True)
class PolicyRule:
    policy_id: str
    policy_version: str
    effect: str
    scope: Any
    subject_selector: Mapping[str, Any]
    action_selector: Mapping[str, Any]
    target_selector: Mapping[str, Any]
    condition_set: Any
    provenance_ref: str
    active_from: Optional[str]
    active_until: Optional[str]
    raw: Mapping[str, Any]

    @property
    def ref(self) -> str:
        return f"execution_policy:{self.policy_id}@{self.policy_version}"


@dataclass(frozen=True)
class PhaseEvaluation:
    allowed: bool
    reason_code: str
    authority_refs: Tuple[str, ...]
    evidence_refs: Tuple[str, ...]
    failed_rule_ref: str


@dataclass(frozen=True)
class AuthorityEvaluation:
    status: str
    reason_code: str
    authority_refs: Tuple[str, ...]
    evidence_refs: Tuple[str, ...]
    failed_rule_ref: str
    condition_type: Optional[str] = None
    required_evidence: Optional[str] = None
    responsible_role: Optional[str] = None
    expires_at: Optional[str] = None
    condition_ref: Optional[str] = None


class AccessControlExecutionPolicyLayer:
    """Evaluate governed execution requests without side effects."""

    def evaluate(
        self,
        *,
        execution_request: Mapping[str, Any],
        phase_contracts: Sequence[Mapping[str, Any]],
        rights_profile: Optional[Mapping[str, Any]],
        access_class: Optional[Mapping[str, Any]],
        execution_policy_set: Sequence[Mapping[str, Any]],
        evaluated_at: Optional[Any] = None,
    ) -> Dict[str, Any]:
        request = self._normalize_request(execution_request)
        requested_at = _parse_timestamp(request["requested_at"], "execution_request.requested_at")
        evaluated_at_value = _normalize_timestamp(
            request["requested_at"] if evaluated_at is None else evaluated_at,
            "evaluated_at",
        )

        policies = self._normalize_policy_set(execution_policy_set, requested_at)
        policy_version = self._policy_version_for(policies)
        policy_refs = [policy.ref for policy in policies]

        forbidden_reason = self._forbidden_authority_mutation_reason(request)
        if forbidden_reason:
            return self._build_result(
                request=request,
                status="deny",
                reason_code=forbidden_reason,
                evaluated_at=evaluated_at_value,
                policy_version=policy_version,
                decision_basis=["operational_rules:forbidden_operations"],
                authority_refs=[],
                evaluated_policy_refs=policy_refs,
                provenance_refs=[policy.provenance_ref for policy in policies],
                failed_rule_ref="operational_rules.forbidden_operations",
                evidence_refs=[f"execution_request.action:{request['action']}"],
            ).to_dict()

        phase = self._evaluate_phase_contracts(
            request=request,
            phase_contracts=phase_contracts,
        )
        if not phase.allowed:
            return self._build_result(
                request=request,
                status="deny",
                reason_code=phase.reason_code,
                evaluated_at=evaluated_at_value,
                policy_version=policy_version,
                decision_basis=list(phase.authority_refs),
                authority_refs=list(phase.authority_refs),
                evaluated_policy_refs=policy_refs,
                provenance_refs=[policy.provenance_ref for policy in policies],
                failed_rule_ref=phase.failed_rule_ref,
                evidence_refs=list(phase.evidence_refs),
            ).to_dict()

        authority = self._evaluate_rights_and_access(
            request=request,
            rights_profile=rights_profile,
            access_class=access_class,
        )
        if authority.status == "deny":
            return self._build_result(
                request=request,
                status="deny",
                reason_code=authority.reason_code,
                evaluated_at=evaluated_at_value,
                policy_version=policy_version,
                decision_basis=list(phase.authority_refs + authority.authority_refs),
                authority_refs=list(phase.authority_refs + authority.authority_refs),
                evaluated_policy_refs=policy_refs,
                provenance_refs=[policy.provenance_ref for policy in policies],
                failed_rule_ref=authority.failed_rule_ref,
                evidence_refs=list(authority.evidence_refs),
            ).to_dict()

        policy = self._evaluate_policies(
            request=request,
            policies=policies,
            rights_profile=rights_profile or {},
            access_class=access_class or {},
        )
        basis = list(phase.authority_refs + authority.authority_refs)
        authority_refs = list(phase.authority_refs + authority.authority_refs)
        provenance_refs = [policy_rule.provenance_ref for policy_rule in policies]

        if policy.status == "deny":
            return self._build_result(
                request=request,
                status="deny",
                reason_code=policy.reason_code,
                evaluated_at=evaluated_at_value,
                policy_version=policy_version,
                decision_basis=basis + list(policy.authority_refs),
                authority_refs=authority_refs + list(policy.authority_refs),
                evaluated_policy_refs=policy_refs,
                provenance_refs=provenance_refs,
                failed_rule_ref=policy.failed_rule_ref,
                evidence_refs=list(policy.evidence_refs),
            ).to_dict()

        if policy.status == "conditional" or authority.status == "conditional":
            condition = policy if policy.status == "conditional" else authority
            return self._build_result(
                request=request,
                status="conditional",
                reason_code=condition.reason_code,
                evaluated_at=evaluated_at_value,
                policy_version=policy_version,
                decision_basis=basis + list(policy.authority_refs),
                authority_refs=authority_refs + list(policy.authority_refs),
                evaluated_policy_refs=policy_refs,
                provenance_refs=provenance_refs,
                failed_rule_ref=condition.failed_rule_ref,
                evidence_refs=list(condition.evidence_refs),
                conditional=condition,
            ).to_dict()

        return self._build_result(
            request=request,
            status="allow",
            reason_code="ALLOW_POLICY_MATCHED",
            evaluated_at=evaluated_at_value,
            policy_version=policy_version,
            decision_basis=basis + list(policy.authority_refs),
            authority_refs=authority_refs + list(policy.authority_refs),
            evaluated_policy_refs=policy_refs,
            provenance_refs=provenance_refs,
        ).to_dict()

    def run(self, **kwargs: Any) -> Dict[str, Any]:
        """Alias for orchestrators that call motors through a run method."""

        return self.evaluate(**kwargs)

    def _normalize_request(self, execution_request: Mapping[str, Any]) -> Dict[str, Any]:
        if not isinstance(execution_request, Mapping):
            raise AccessPolicyInputError("execution_request must be a mapping")
        request = dict(execution_request)
        missing = [
            field
            for field in REQUEST_REQUIRED_FIELDS
            if field not in request or request[field] is None or str(request[field]).strip() == ""
        ]
        if missing:
            raise AccessPolicyInputError(
                "execution_request missing required fields: " + ", ".join(missing)
            )
        _parse_timestamp(request["requested_at"], "execution_request.requested_at")
        for field in REQUEST_REQUIRED_FIELDS:
            if field != "requested_at":
                request[field] = str(request[field]).strip()
        return request

    def _normalize_policy_set(
        self,
        execution_policy_set: Sequence[Mapping[str, Any]],
        requested_at: datetime,
    ) -> Tuple[PolicyRule, ...]:
        if execution_policy_set is None:
            return tuple()
        if not isinstance(execution_policy_set, Sequence) or isinstance(
            execution_policy_set, (str, bytes)
        ):
            raise AccessPolicyInputError("execution_policy_set must be a sequence")

        policies: List[PolicyRule] = []
        for index, raw_policy in enumerate(execution_policy_set):
            if not isinstance(raw_policy, Mapping):
                raise AccessPolicyInputError(
                    f"execution_policy_set[{index}] must be a mapping"
                )
            missing = [
                field
                for field in POLICY_REQUIRED_FIELDS
                if field not in raw_policy
                or raw_policy[field] is None
                or str(raw_policy[field]).strip() == ""
            ]
            if missing:
                raise AccessPolicyInputError(
                    f"execution_policy_set[{index}] missing required fields: "
                    + ", ".join(missing)
                )
            if "condition_set" in raw_policy:
                condition_set = raw_policy["condition_set"]
            elif "conditions" in raw_policy:
                condition_set = raw_policy["conditions"]
            elif "condition" in raw_policy:
                condition_set = raw_policy["condition"]
            else:
                raise AccessPolicyInputError(
                    f"execution_policy_set[{index}] missing condition_set"
                )
            if not _is_evaluable_condition(condition_set):
                raise AccessPolicyInputError(
                    f"execution_policy_set[{index}] has an unevaluable condition_set"
                )

            effect = _norm(raw_policy["effect"])
            if effect not in VALID_POLICY_EFFECTS:
                raise AccessPolicyInputError(
                    f"execution_policy_set[{index}] has invalid effect: {effect}"
                )

            active_from = _optional_timestamp(raw_policy.get("active_from"), "active_from")
            active_until = _optional_timestamp(
                raw_policy.get("active_until") or raw_policy.get("expires_at"),
                "active_until",
            )
            if active_from and requested_at < _parse_timestamp(active_from, "active_from"):
                continue
            if active_until and requested_at > _parse_timestamp(active_until, "active_until"):
                continue

            policy = PolicyRule(
                policy_id=str(raw_policy["policy_id"]).strip(),
                policy_version=str(raw_policy["policy_version"]).strip(),
                effect=effect,
                scope=raw_policy["scope"],
                subject_selector=_mapping_or_empty(raw_policy.get("subject_selector")),
                action_selector=_mapping_or_empty(raw_policy.get("action_selector")),
                target_selector=_mapping_or_empty(raw_policy.get("target_selector")),
                condition_set=condition_set,
                provenance_ref=str(raw_policy["provenance_ref"]).strip(),
                active_from=active_from,
                active_until=active_until,
                raw=raw_policy,
            )
            policies.append(policy)
        return tuple(policies)

    def _policy_version_for(self, policies: Sequence[PolicyRule]) -> str:
        versions = sorted({policy.policy_version for policy in policies})
        if not versions:
            return DEFAULT_POLICY_VERSION
        if len(versions) == 1:
            return versions[0]
        digest = _hash_value("policy_version", versions)
        return "multi:" + digest

    def _forbidden_authority_mutation_reason(self, request: Mapping[str, Any]) -> Optional[str]:
        action = _norm(request.get("action"))
        target_type = _norm(request.get("target_type"))
        declared_purpose = _norm(request.get("declared_purpose"))
        merged = " ".join((action, target_type, declared_purpose))
        for marker in FORBIDDEN_AUTHORITY_MUTATION_MARKERS:
            if marker in merged:
                return "UNSUPPORTED_AUTHORITY_MUTATION_REQUEST"
        return None

    def _evaluate_phase_contracts(
        self,
        *,
        request: Mapping[str, Any],
        phase_contracts: Sequence[Mapping[str, Any]],
    ) -> PhaseEvaluation:
        if not isinstance(phase_contracts, Sequence) or isinstance(phase_contracts, (str, bytes)):
            raise AccessPolicyInputError("phase_contracts must be a sequence")
        if not phase_contracts:
            return PhaseEvaluation(
                allowed=False,
                reason_code="MISSING_PHASE_CONTRACT",
                authority_refs=tuple(),
                evidence_refs=("phase_contracts:empty",),
                failed_rule_ref="functional_contract.limits.phase_contract_required",
            )

        motor_seen = False
        stage_seen = False
        action_authority_missing = False
        authority_refs: List[str] = []
        evidence_refs: List[str] = []

        for index, contract in enumerate(phase_contracts):
            if not isinstance(contract, Mapping):
                raise AccessPolicyInputError(f"phase_contracts[{index}] must be a mapping")
            if not _record_is_active(contract):
                continue
            contract_ref = _phase_contract_ref(contract, index)
            if not _contract_matches_motor(contract, request["motor_id"]):
                continue
            motor_seen = True
            authority_refs.append(contract_ref)

            if not _contract_matches_stage(contract, request["stage_name"]):
                evidence_refs.append(f"{contract_ref}:stage_mismatch")
                continue
            stage_seen = True

            actions = _contract_actions_for_stage(contract, request["stage_name"])
            if actions is None:
                action_authority_missing = True
                evidence_refs.append(f"{contract_ref}:missing_action_authority")
                continue
            if _matches_any(request["action"], actions):
                return PhaseEvaluation(
                    allowed=True,
                    reason_code="PHASE_CONTRACT_ALLOWED",
                    authority_refs=(contract_ref,),
                    evidence_refs=(f"{contract_ref}:motor_stage_action_match",),
                    failed_rule_ref="",
                )
            evidence_refs.append(f"{contract_ref}:action_mismatch")

        if not motor_seen:
            return PhaseEvaluation(
                allowed=False,
                reason_code="UNKNOWN_PHASE_CONTRACT_SCOPE",
                authority_refs=tuple(_unique(authority_refs)),
                evidence_refs=tuple(evidence_refs or [f"motor_id:{request['motor_id']}"]),
                failed_rule_ref="operational_rules.rule_1.phase_contract_first",
            )
        if not stage_seen:
            return PhaseEvaluation(
                allowed=False,
                reason_code="STAGE_NOT_ALLOWED_BY_PHASE_CONTRACT",
                authority_refs=tuple(_unique(authority_refs)),
                evidence_refs=tuple(evidence_refs or [f"stage_name:{request['stage_name']}"]),
                failed_rule_ref="functional_contract.validations.stage_name_exists",
            )
        if action_authority_missing:
            return PhaseEvaluation(
                allowed=False,
                reason_code="MISSING_PHASE_ACTION_AUTHORITY",
                authority_refs=tuple(_unique(authority_refs)),
                evidence_refs=tuple(evidence_refs),
                failed_rule_ref="functional_contract.validations.action_limits",
            )
        return PhaseEvaluation(
            allowed=False,
            reason_code="ACTION_NOT_ALLOWED_BY_PHASE_CONTRACT",
            authority_refs=tuple(_unique(authority_refs)),
            evidence_refs=tuple(evidence_refs or [f"action:{request['action']}"]),
            failed_rule_ref="functional_contract.validations.action_limits",
        )

    def _evaluate_rights_and_access(
        self,
        *,
        request: Mapping[str, Any],
        rights_profile: Optional[Mapping[str, Any]],
        access_class: Optional[Mapping[str, Any]],
    ) -> AuthorityEvaluation:
        if not isinstance(rights_profile, Mapping):
            return AuthorityEvaluation(
                status="deny",
                reason_code="MISSING_RIGHTS_PROFILE",
                authority_refs=tuple(),
                evidence_refs=("rights_profile:missing",),
                failed_rule_ref="operational_rules.rule_3.rights_profile_required",
            )
        if not isinstance(access_class, Mapping):
            return AuthorityEvaluation(
                status="deny",
                reason_code="MISSING_ACCESS_CLASS",
                authority_refs=(_rights_ref(rights_profile),),
                evidence_refs=("access_class:missing",),
                failed_rule_ref="operational_rules.rule_3.access_class_required",
            )

        rights_required = ("source_id", "license_basis", "permitted_uses", "prohibited_uses", "rights_status")
        missing_rights = [
            field
            for field in rights_required
            if field not in rights_profile
            or rights_profile[field] is None
            or str(rights_profile[field]).strip() == ""
        ]
        if missing_rights:
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_PROFILE_INCOMPLETE",
                authority_refs=(_rights_ref(rights_profile),),
                evidence_refs=[f"rights_profile.missing:{field}" for field in missing_rights],
                failed_rule_ref="functional_contract.inputs.rights_profile",
            )

        access_source = _first_present(
            access_class,
            "source_id",
            "target_ref",
            "artifact_id",
            "resource_id",
        )
        if not access_source:
            return AuthorityEvaluation(
                status="deny",
                reason_code="ACCESS_CLASS_INCOMPLETE",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=("access_class.missing:source_id",),
                failed_rule_ref="functional_contract.inputs.access_class",
            )

        if not _request_links_to_authority(request, rights_profile):
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_PROFILE_TARGET_MISMATCH",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(f"target_ref:{request['target_ref']}", _rights_ref(rights_profile)),
                failed_rule_ref="functional_contract.limits.target_ref_link_required",
            )
        if not _request_links_to_authority(request, access_class):
            return AuthorityEvaluation(
                status="deny",
                reason_code="ACCESS_CLASS_TARGET_MISMATCH",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(f"target_ref:{request['target_ref']}", _access_class_ref(access_class)),
                failed_rule_ref="functional_contract.limits.target_ref_link_required",
            )
        if not _authority_records_share_source(rights_profile, access_class):
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_ACCESS_SOURCE_MISMATCH",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                failed_rule_ref="functional_contract.validations.rights_access_same_source",
            )

        rights_status = _norm(rights_profile.get("rights_status"))
        if rights_status in NEGATIVE_RIGHTS_STATUSES:
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_STATUS_BLOCKED",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(f"rights_status:{rights_status}",),
                failed_rule_ref="operational_rules.rule_3.rights_profile_required",
            )
        if rights_status in CONDITIONAL_RIGHTS_STATUSES:
            conditional = _conditional_from_rights(rights_profile)
            if conditional:
                return AuthorityEvaluation(
                    status="conditional",
                    reason_code="RIGHTS_STATUS_CONDITIONAL",
                    authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                    evidence_refs=(f"rights_status:{rights_status}",),
                    failed_rule_ref="operational_rules.rule_5.conditional_requirements",
                    condition_type=conditional["condition_type"],
                    required_evidence=conditional["required_evidence"],
                    responsible_role=conditional["responsible_role"],
                    expires_at=conditional["expires_at"],
                    condition_ref=_rights_ref(rights_profile),
                )
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_CONDITION_INCOMPLETE",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(f"rights_status:{rights_status}",),
                failed_rule_ref="operational_rules.rule_5.conditional_requirements",
            )
        if rights_status and rights_status not in POSITIVE_RIGHTS_STATUSES:
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_STATUS_NOT_RECOGNIZED",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(f"rights_status:{rights_status}",),
                failed_rule_ref="functional_contract.inputs.rights_profile",
            )

        prohibited_uses = _values_as_list(rights_profile.get("prohibited_uses"))
        if _usage_matches_request(request, prohibited_uses):
            return AuthorityEvaluation(
                status="deny",
                reason_code="RIGHTS_PROHIBITED_USE",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=[f"prohibited_use:{use}" for use in prohibited_uses],
                failed_rule_ref="functional_contract.validations.rights_profile_restrictions",
            )

        permitted_uses = _values_as_list(rights_profile.get("permitted_uses"))
        if permitted_uses and not _contains_wildcard(permitted_uses):
            if not _usage_matches_request(request, permitted_uses):
                return AuthorityEvaluation(
                    status="deny",
                    reason_code="RIGHTS_USE_NOT_PERMITTED",
                    authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                    evidence_refs=[f"permitted_use:{use}" for use in permitted_uses],
                    failed_rule_ref="functional_contract.validations.rights_profile_restrictions",
                )

        access_status = _norm(
            _first_present(access_class, "status", "access_status", "classification_status")
        )
        if access_status in {"blocked", "revoked", "denied", "invalid"}:
            return AuthorityEvaluation(
                status="deny",
                reason_code="ACCESS_CLASS_BLOCKED",
                authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
                evidence_refs=(f"access_status:{access_status}",),
                failed_rule_ref="functional_contract.inputs.access_class",
            )

        return AuthorityEvaluation(
            status="allow",
            reason_code="RIGHTS_AND_ACCESS_ALLOWED",
            authority_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
            evidence_refs=(_rights_ref(rights_profile), _access_class_ref(access_class)),
            failed_rule_ref="",
        )

    def _evaluate_policies(
        self,
        *,
        request: Mapping[str, Any],
        policies: Sequence[PolicyRule],
        rights_profile: Mapping[str, Any],
        access_class: Mapping[str, Any],
    ) -> AuthorityEvaluation:
        if not policies:
            return AuthorityEvaluation(
                status="deny",
                reason_code="NO_ACTIVE_EXECUTION_POLICY",
                authority_refs=tuple(),
                evidence_refs=("execution_policy_set:empty_or_inactive",),
                failed_rule_ref="operational_rules.rule_3.policy_version_required",
            )

        matching = [
            policy
            for policy in policies
            if _policy_matches_request(
                policy=policy,
                request=request,
                rights_profile=rights_profile,
                access_class=access_class,
            )
        ]
        deny_matches = [policy for policy in matching if policy.effect == "deny"]
        if deny_matches:
            refs = tuple(policy.ref for policy in deny_matches)
            return AuthorityEvaluation(
                status="deny",
                reason_code="EXPLICIT_DENY_POLICY_MATCHED",
                authority_refs=refs,
                evidence_refs=refs,
                failed_rule_ref="operational_rules.rule_2.deny_precedence",
            )

        conditional_matches = [policy for policy in matching if policy.effect == "conditional"]
        if conditional_matches:
            policy = conditional_matches[0]
            condition = _conditional_from_policy(policy)
            if not condition:
                return AuthorityEvaluation(
                    status="deny",
                    reason_code="CONDITIONAL_POLICY_INCOMPLETE",
                    authority_refs=(policy.ref,),
                    evidence_refs=(policy.ref,),
                    failed_rule_ref="operational_rules.rule_5.conditional_requirements",
                )
            return AuthorityEvaluation(
                status="conditional",
                reason_code="CONDITIONAL_POLICY_MATCHED",
                authority_refs=(policy.ref,),
                evidence_refs=(policy.ref,),
                failed_rule_ref="operational_rules.rule_5.conditional_requirements",
                condition_type=condition["condition_type"],
                required_evidence=condition["required_evidence"],
                responsible_role=condition["responsible_role"],
                expires_at=condition["expires_at"],
                condition_ref=policy.ref,
            )

        allow_matches = [policy for policy in matching if policy.effect == "allow"]
        if allow_matches:
            refs = tuple(policy.ref for policy in allow_matches)
            return AuthorityEvaluation(
                status="allow",
                reason_code="ALLOW_POLICY_MATCHED",
                authority_refs=refs,
                evidence_refs=refs,
                failed_rule_ref="",
            )

        return AuthorityEvaluation(
            status="deny",
            reason_code="NO_APPLICABLE_ALLOW_POLICY",
            authority_refs=tuple(policy.ref for policy in policies),
            evidence_refs=tuple(policy.ref for policy in policies),
            failed_rule_ref="functional_contract.limits.no_implicit_permission",
        )

    def _build_result(
        self,
        *,
        request: Mapping[str, Any],
        status: str,
        reason_code: str,
        evaluated_at: str,
        policy_version: str,
        decision_basis: List[str],
        authority_refs: List[str],
        evaluated_policy_refs: List[str],
        provenance_refs: List[str],
        failed_rule_ref: str = "",
        evidence_refs: Optional[List[str]] = None,
        conditional: Optional[AuthorityEvaluation] = None,
    ) -> PolicyEvaluationResult:
        basis = _unique(decision_basis or ["operational_rules:no_implicit_permission"])
        authorities = _unique(authority_refs)
        policies = _unique(evaluated_policy_refs)
        provenance = _unique(provenance_refs)
        evidence = _unique(evidence_refs or [])
        decision_payload = {
            "request_id": request["request_id"],
            "actor_id": request["actor_id"],
            "motor_id": request["motor_id"],
            "stage_name": request["stage_name"],
            "action": request["action"],
            "target_ref": request["target_ref"],
            "status": status,
            "reason_code": reason_code,
            "decision_basis": basis,
            "policy_version": policy_version,
            "run_id": request["run_id"],
            "correlation_id": request["correlation_id"],
        }
        decision_id = _hash_value("decision", decision_payload)
        decision = PolicyDecision(
            decision_id=decision_id,
            request_id=request["request_id"],
            actor_id=request["actor_id"],
            motor_id=request["motor_id"],
            stage_name=request["stage_name"],
            action=request["action"],
            target_ref=request["target_ref"],
            target_type=request["target_type"],
            status=status,
            reason_code=reason_code,
            decision_basis=basis,
            evaluated_at=evaluated_at,
            policy_version=policy_version,
            run_id=request["run_id"],
            correlation_id=request["correlation_id"],
        )

        violation = None
        if status == "deny":
            violation = PolicyViolationEvent(
                violation_id=_hash_value(
                    "violation",
                    {
                        "decision_id": decision_id,
                        "request_id": request["request_id"],
                        "reason_code": reason_code,
                        "failed_rule_ref": failed_rule_ref,
                    },
                ),
                decision_id=decision_id,
                request_id=request["request_id"],
                severity=_severity_for(reason_code),
                violated_rule_ref=failed_rule_ref or "functional_contract.limits.no_implicit_permission",
                actor_id=request["actor_id"],
                motor_id=request["motor_id"],
                action=request["action"],
                target_ref=request["target_ref"],
                observed_at=evaluated_at,
                reason_code=reason_code,
                failed_authority_refs=authorities,
                evidence_refs=evidence,
            )

        requirement = None
        if status == "conditional":
            if not conditional:
                raise UnsafePolicyOutputError("conditional status requires a condition record")
            requirement = ConditionalExecutionRequirement(
                requirement_id=_hash_value(
                    "requirement",
                    {
                        "decision_id": decision_id,
                        "condition_type": conditional.condition_type,
                        "required_evidence": conditional.required_evidence,
                        "responsible_role": conditional.responsible_role,
                        "expires_at": conditional.expires_at,
                    },
                ),
                decision_id=decision_id,
                condition_type=str(conditional.condition_type),
                required_evidence=str(conditional.required_evidence),
                responsible_role=str(conditional.responsible_role),
                expires_at=str(conditional.expires_at),
                verification_status="pending",
                policy_ref=conditional.condition_ref or "authority:conditional",
                condition_ref=conditional.condition_ref or "authority:conditional",
            )

        request_snapshot_ref = _hash_value("request_snapshot", dict(request))
        audit = AccessAuditRecord(
            audit_id=_hash_value(
                "audit",
                {
                    "decision_id": decision_id,
                    "request_snapshot_ref": request_snapshot_ref,
                    "evaluated_policy_refs": policies,
                    "authority_refs": authorities,
                    "result_status": status,
                    "run_id": request["run_id"],
                    "correlation_id": request["correlation_id"],
                },
            ),
            decision_id=decision_id,
            request_snapshot_ref=request_snapshot_ref,
            request_snapshot=dict(request),
            evaluated_policy_refs=policies,
            authority_refs=authorities,
            result_status=status,
            actor_id=request["actor_id"],
            motor_id=request["motor_id"],
            action=request["action"],
            target_ref=request["target_ref"],
            run_id=request["run_id"],
            correlation_id=request["correlation_id"],
            decision_reason_code=reason_code,
            provenance_refs=provenance,
            created_at=evaluated_at,
        )
        self._validate_output(decision, violation, audit, requirement)
        return PolicyEvaluationResult(
            policy_decision=decision,
            policy_violation_event=violation,
            access_audit_record=audit,
            conditional_execution_requirement=requirement,
        )

    def _validate_output(
        self,
        decision: PolicyDecision,
        violation: Optional[PolicyViolationEvent],
        audit: AccessAuditRecord,
        requirement: Optional[ConditionalExecutionRequirement],
    ) -> None:
        if decision.status not in {"allow", "deny", "conditional"}:
            raise UnsafePolicyOutputError("policy_decision.status is invalid")
        required_decision = (
            decision.decision_id,
            decision.request_id,
            decision.actor_id,
            decision.motor_id,
            decision.action,
            decision.target_ref,
            decision.reason_code,
            decision.policy_version,
            decision.run_id,
            decision.correlation_id,
        )
        if any(not str(value).strip() for value in required_decision):
            raise UnsafePolicyOutputError("policy_decision is missing required fields")
        if decision.status == "deny" and violation is None:
            raise UnsafePolicyOutputError("deny decision requires PolicyViolationEvent")
        if decision.status == "conditional" and requirement is None:
            raise UnsafePolicyOutputError(
                "conditional decision requires ConditionalExecutionRequirement"
            )
        if decision.status == "allow" and violation is not None and violation.severity == "CRITICAL":
            raise UnsafePolicyOutputError("allow cannot coexist with a critical violation")
        if not audit.request_snapshot_ref or not audit.run_id or not audit.correlation_id:
            raise UnsafePolicyOutputError("access_audit_record is missing required lineage")


def _mapping_or_empty(value: Any) -> Mapping[str, Any]:
    if value is None:
        return {}
    if not isinstance(value, Mapping):
        raise AccessPolicyInputError("selector fields must be mappings")
    return value


def _is_evaluable_condition(value: Any) -> bool:
    return isinstance(value, (Mapping, Sequence, str, bool, int, float)) and not isinstance(
        value, bytes
    )


def _parse_timestamp(value: Any, field_name: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    elif isinstance(value, str):
        raw = value.strip()
        if not raw:
            raise AccessPolicyInputError(f"{field_name} must not be empty")
        if raw.endswith("Z"):
            raw = raw[:-1] + "+00:00"
        try:
            parsed = datetime.fromisoformat(raw)
        except ValueError as exc:
            raise AccessPolicyInputError(f"{field_name} is not parseable") from exc
    else:
        raise AccessPolicyInputError(f"{field_name} must be an ISO timestamp")
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _normalize_timestamp(value: Any, field_name: str) -> str:
    parsed = _parse_timestamp(value, field_name)
    return parsed.isoformat().replace("+00:00", "Z")


def _optional_timestamp(value: Any, field_name: str) -> Optional[str]:
    if value is None or str(value).strip() == "":
        return None
    return _normalize_timestamp(value, field_name)


def _norm(value: Any) -> str:
    text = "" if value is None else str(value)
    normalized = re.sub(r"[\s\-]+", "_", text.strip().lower())
    return normalized


def _values_as_list(value: Any) -> List[str]:
    if value is None:
        return []
    if isinstance(value, Mapping):
        return [str(item).strip() for item in value.values() if str(item).strip()]
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [str(item).strip() for item in value if str(item).strip()]
    return [str(value).strip()] if str(value).strip() else []


def _contains_wildcard(values: Iterable[Any]) -> bool:
    return any(_norm(value) in WILDCARDS for value in values)


def _matches_any(value: Any, allowed_values: Iterable[Any]) -> bool:
    allowed = list(allowed_values)
    if _contains_wildcard(allowed):
        return True
    value_norm = _norm(value)
    return any(value_norm == _norm(item) for item in allowed)


def _usage_matches_request(request: Mapping[str, Any], usage_values: Iterable[Any]) -> bool:
    usage = [_norm(value) for value in usage_values]
    if not usage:
        return False
    if _contains_wildcard(usage):
        return True
    action = _norm(request.get("action"))
    purpose = _norm(request.get("declared_purpose"))
    target_type = _norm(request.get("target_type"))
    candidates = {action, purpose, target_type, f"{action}_{purpose}", f"{purpose}_{action}"}
    for item in usage:
        if item in candidates:
            return True
        if action and action in item:
            return True
        if purpose and purpose in item:
            return True
    return False


def _record_is_active(record: Mapping[str, Any]) -> bool:
    status = _norm(_first_present(record, "status", "state", "lifecycle_state"))
    if not status:
        return True
    return status not in {"inactive", "revoked", "deprecated", "archived", "closed", "blocked"}


def _phase_contract_ref(contract: Mapping[str, Any], index: int) -> str:
    contract_id = _first_present(
        contract,
        "contract_id",
        "phase_contract_id",
        "id",
        "contract_ref",
        "phase_id",
    )
    version = _first_present(contract, "contract_version", "version_id", "version", "policy_version")
    if not contract_id:
        contract_id = f"phase_contract_index_{index}"
    if version:
        return f"phase_contract:{contract_id}@{version}"
    return f"phase_contract:{contract_id}"


def _contract_matches_motor(contract: Mapping[str, Any], motor_id: str) -> bool:
    motor_values = _collect_values(
        contract,
        (
            "motor_id",
            "motor_ids",
            "allowed_motor_ids",
            "allowed_motors",
            "contracted_motor_id",
            "target_motor_id",
            "produced_by_motor",
        ),
    )
    scope = contract.get("scope")
    if isinstance(scope, Mapping):
        motor_values.extend(
            _collect_values(
                scope,
                ("motor_id", "motor_ids", "allowed_motor_ids", "allowed_motors"),
            )
        )
    if not motor_values:
        return True
    return _matches_any(motor_id, motor_values)


def _contract_matches_stage(contract: Mapping[str, Any], stage_name: str) -> bool:
    stage_values = _collect_values(
        contract,
        (
            "stage_name",
            "stage_names",
            "allowed_stages",
            "valid_stages",
            "stages",
        ),
    )
    stage_values.extend(_stage_names_from_stage_items(contract.get("stages")))
    stage_values.extend(_stage_names_from_stage_items(contract.get("stage_contracts")))
    if not stage_values:
        return True
    return _matches_any(stage_name, stage_values)


def _contract_actions_for_stage(contract: Mapping[str, Any], stage_name: str) -> Optional[List[str]]:
    actions: List[str] = []
    global_keys = (
        "allowed_actions",
        "actions",
        "compatible_actions",
        "permitted_actions",
        "allowed_operations",
        "operation_names",
    )
    actions.extend(_collect_values(contract, global_keys))

    stage_actions = contract.get("stage_actions")
    if isinstance(stage_actions, Mapping):
        if stage_name in stage_actions:
            actions.extend(_values_as_list(stage_actions[stage_name]))
        normalized = {_norm(key): value for key, value in stage_actions.items()}
        if _norm(stage_name) in normalized:
            actions.extend(_values_as_list(normalized[_norm(stage_name)]))

    for container_key in ("stages", "stage_contracts", "phase_limits"):
        container = contract.get(container_key)
        if isinstance(container, Mapping):
            iterable = container.values()
        elif isinstance(container, Sequence) and not isinstance(container, (str, bytes)):
            iterable = container
        else:
            iterable = []
        for item in iterable:
            if isinstance(item, Mapping) and _stage_item_matches(item, stage_name):
                actions.extend(_collect_values(item, global_keys))

    if not actions:
        return None
    return _unique(actions)


def _stage_names_from_stage_items(value: Any) -> List[str]:
    names: List[str] = []
    if isinstance(value, Mapping):
        names.extend(str(key) for key in value.keys())
        iterable = value.values()
    elif isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        iterable = value
    else:
        return names
    for item in iterable:
        if isinstance(item, str):
            names.append(item)
        elif isinstance(item, Mapping):
            names.extend(
                _collect_values(
                    item,
                    ("stage_name", "name", "id", "stage_id", "phase_name"),
                )
            )
    return _unique(names)


def _stage_item_matches(item: Mapping[str, Any], stage_name: str) -> bool:
    names = _collect_values(item, ("stage_name", "name", "id", "stage_id", "phase_name"))
    return not names or _matches_any(stage_name, names)


def _collect_values(record: Mapping[str, Any], keys: Iterable[str]) -> List[str]:
    values: List[str] = []
    for key in keys:
        if key in record:
            value = record[key]
            if isinstance(value, Mapping):
                values.extend(str(item) for item in value.keys())
                values.extend(_values_as_list(value))
            else:
                values.extend(_values_as_list(value))
    return _unique(values)


def _first_present(record: Mapping[str, Any], *keys: str) -> Optional[Any]:
    for key in keys:
        if key in record and record[key] is not None and str(record[key]).strip() != "":
            return record[key]
    return None


def _rights_ref(rights_profile: Mapping[str, Any]) -> str:
    source_id = _first_present(rights_profile, "source_id", "target_ref", "artifact_id", "resource_id")
    version = _first_present(rights_profile, "version_id", "rights_version", "policy_version")
    if not source_id:
        source_id = _hash_value("rights_profile", rights_profile)
    if version:
        return f"rights_profile:{source_id}@{version}"
    return f"rights_profile:{source_id}"


def _access_class_ref(access_class: Mapping[str, Any]) -> str:
    source_id = _first_present(access_class, "source_id", "target_ref", "artifact_id", "resource_id")
    class_value = _access_class_value(access_class) or "unclassified"
    version = _first_present(access_class, "version_id", "access_version", "policy_version")
    if not source_id:
        source_id = _hash_value("access_class", access_class)
    if version:
        return f"access_class:{source_id}:{class_value}@{version}"
    return f"access_class:{source_id}:{class_value}"


def _access_class_value(access_class: Mapping[str, Any]) -> str:
    return str(
        _first_present(
            access_class,
            "access_class",
            "class_id",
            "classification",
            "level",
            "access_level",
        )
        or ""
    ).strip()


def _request_links_to_authority(request: Mapping[str, Any], authority: Mapping[str, Any]) -> bool:
    request_refs = {
        str(value).strip()
        for value in (
            request.get("target_ref"),
            request.get("source_id"),
            request.get("artifact_id"),
            request.get("target_id"),
            request.get("resource_id"),
        )
        if value is not None and str(value).strip()
    }
    authority_refs = {
        str(value).strip()
        for value in (
            authority.get("source_id"),
            authority.get("target_ref"),
            authority.get("artifact_id"),
            authority.get("resource_id"),
            authority.get("source_ref"),
        )
        if value is not None and str(value).strip()
    }
    if not authority_refs:
        return False
    for req_ref in request_refs:
        for authority_ref in authority_refs:
            if _references_match(req_ref, authority_ref):
                return True
    return False


def _authority_records_share_source(
    rights_profile: Mapping[str, Any],
    access_class: Mapping[str, Any],
) -> bool:
    rights_source = _first_present(rights_profile, "source_id", "target_ref", "artifact_id", "resource_id")
    access_source = _first_present(access_class, "source_id", "target_ref", "artifact_id", "resource_id")
    if not rights_source or not access_source:
        return False
    return _references_match(str(rights_source), str(access_source))


def _references_match(left: str, right: str) -> bool:
    left_norm = _norm_ref(left)
    right_norm = _norm_ref(right)
    if left_norm == right_norm:
        return True
    return (
        left_norm.endswith(":" + right_norm)
        or left_norm.endswith("/" + right_norm)
        or left_norm.endswith("#" + right_norm)
        or right_norm.endswith(":" + left_norm)
        or right_norm.endswith("/" + left_norm)
        or right_norm.endswith("#" + left_norm)
    )


def _norm_ref(value: str) -> str:
    return str(value).strip().lower()


def _conditional_from_rights(rights_profile: Mapping[str, Any]) -> Optional[Dict[str, str]]:
    condition_type = str(
        _first_present(rights_profile, "condition_type", "required_condition", "approval_type")
        or "rights_approval"
    ).strip()
    required_evidence = _first_present(
        rights_profile,
        "required_evidence",
        "evidence_expected",
        "approval_evidence",
    )
    responsible_role = _first_present(
        rights_profile,
        "responsible_role",
        "verification_owner",
        "approver_role",
    )
    expires_at = _first_present(rights_profile, "expires_at", "approval_expires_at")
    if not required_evidence or not responsible_role or not expires_at:
        return None
    return {
        "condition_type": condition_type,
        "required_evidence": str(required_evidence).strip(),
        "responsible_role": str(responsible_role).strip(),
        "expires_at": _normalize_timestamp(expires_at, "rights_profile.expires_at"),
    }


def _policy_matches_request(
    *,
    policy: PolicyRule,
    request: Mapping[str, Any],
    rights_profile: Mapping[str, Any],
    access_class: Mapping[str, Any],
) -> bool:
    context = _policy_context(request, rights_profile, access_class)
    return (
        _scope_matches(policy.scope, context)
        and _selector_matches(policy.subject_selector, context)
        and _selector_matches(policy.action_selector, context)
        and _selector_matches(policy.target_selector, context)
        and _condition_matches(policy.condition_set, context)
    )


def _policy_context(
    request: Mapping[str, Any],
    rights_profile: Mapping[str, Any],
    access_class: Mapping[str, Any],
) -> Dict[str, Any]:
    context = dict(request)
    context["source_id"] = _first_present(rights_profile, "source_id", "target_ref", "artifact_id")
    context["rights_status"] = rights_profile.get("rights_status")
    context["access_class"] = _access_class_value(access_class)
    context["license_basis"] = rights_profile.get("license_basis")
    return context


def _scope_matches(scope: Any, context: Mapping[str, Any]) -> bool:
    if isinstance(scope, Mapping):
        return _selector_matches(scope, context)
    values = _values_as_list(scope)
    if not values or _contains_wildcard(values):
        return True
    normalized = [_norm(value) for value in values]
    comparables = {
        _norm(context.get("motor_id")),
        _norm(context.get("stage_name")),
        _norm(context.get("target_type")),
        _norm(context.get("access_class")),
        _norm(context.get("declared_purpose")),
        "global",
        "framework",
    }
    return any(value in comparables for value in normalized)


def _selector_matches(selector: Mapping[str, Any], context: Mapping[str, Any]) -> bool:
    for key, expected in selector.items():
        normalized_key = _selector_key(key)
        if normalized_key.endswith("s") and normalized_key[:-1] in context:
            normalized_key = normalized_key[:-1]
        if normalized_key not in context:
            if isinstance(expected, bool):
                if not expected:
                    return False
                continue
            return False
        if not _matches_any(context.get(normalized_key), _values_as_list(expected)):
            return False
    return True


def _condition_matches(condition_set: Any, context: Mapping[str, Any]) -> bool:
    if isinstance(condition_set, bool):
        return condition_set
    if isinstance(condition_set, str):
        condition = _norm(condition_set)
        return condition in WILDCARDS or condition in {"always", "true", "unconditional"}
    if isinstance(condition_set, Sequence) and not isinstance(condition_set, (str, bytes)):
        return all(_condition_matches(item, context) for item in condition_set)
    if not isinstance(condition_set, Mapping):
        return False

    for key, expected in condition_set.items():
        normalized_key = _selector_key(key)
        if normalized_key in {
            "condition_type",
            "required_condition",
            "required_evidence",
            "evidence_expected",
            "responsible_role",
            "verification_owner",
            "approver_role",
            "expires_at",
            "approval_expires_at",
        }:
            continue
        if normalized_key in {"declared_purposes", "purposes", "permitted_purposes"}:
            normalized_key = "declared_purpose"
        elif normalized_key in {"actions", "allowed_actions"}:
            normalized_key = "action"
        elif normalized_key in {"motor_ids", "allowed_motors"}:
            normalized_key = "motor_id"
        elif normalized_key in {"target_types"}:
            normalized_key = "target_type"
        elif normalized_key in {"access_classes"}:
            normalized_key = "access_class"
        elif normalized_key in {"actor_ids", "actors"}:
            normalized_key = "actor_id"
        elif normalized_key in {"actor_types"}:
            normalized_key = "actor_type"

        if normalized_key not in context:
            if isinstance(expected, bool):
                if not expected:
                    return False
                continue
            return False
        if not _matches_any(context.get(normalized_key), _values_as_list(expected)):
            return False
    return True


def _selector_key(key: Any) -> str:
    normalized = _norm(key)
    replacements = {
        "declared_purposes": "declared_purposes",
        "permitted_purposes": "permitted_purposes",
        "purpose": "declared_purpose",
        "purposes": "purposes",
        "actors": "actor_ids",
        "actor": "actor_id",
        "motors": "motor_ids",
        "motor": "motor_id",
        "targets": "target_refs",
        "target": "target_ref",
        "sources": "source_ids",
        "source": "source_id",
    }
    return replacements.get(normalized, normalized)


def _conditional_from_policy(policy: PolicyRule) -> Optional[Dict[str, str]]:
    if not isinstance(policy.condition_set, Mapping):
        return None
    condition_type = _first_present(
        policy.condition_set,
        "condition_type",
        "required_condition",
        "approval_type",
    )
    required_evidence = _first_present(
        policy.condition_set,
        "required_evidence",
        "evidence_expected",
        "approval_evidence",
    )
    responsible_role = _first_present(
        policy.condition_set,
        "responsible_role",
        "verification_owner",
        "approver_role",
    )
    expires_at = _first_present(policy.condition_set, "expires_at", "approval_expires_at")
    if not condition_type or not required_evidence or not responsible_role or not expires_at:
        return None
    return {
        "condition_type": str(condition_type).strip(),
        "required_evidence": str(required_evidence).strip(),
        "responsible_role": str(responsible_role).strip(),
        "expires_at": _normalize_timestamp(expires_at, "policy.condition_set.expires_at"),
    }


def _hash_value(prefix: str, payload: Any) -> str:
    encoded = json.dumps(payload, sort_keys=True, default=str, separators=(",", ":"))
    return f"{prefix}_{sha256(encoded.encode('utf-8')).hexdigest()[:20]}"


def _unique(values: Iterable[Any]) -> List[str]:
    seen: Set[str] = set()
    result: List[str] = []
    for value in values:
        text = str(value).strip()
        if not text or text in seen:
            continue
        seen.add(text)
        result.append(text)
    return result


def _severity_for(reason_code: str) -> str:
    if reason_code in {
        "UNSUPPORTED_AUTHORITY_MUTATION_REQUEST",
        "MISSING_PHASE_CONTRACT",
        "MISSING_RIGHTS_PROFILE",
        "MISSING_ACCESS_CLASS",
        "RIGHTS_STATUS_BLOCKED",
        "EXPLICIT_DENY_POLICY_MATCHED",
    }:
        return "CRITICAL"
    if reason_code.startswith("RIGHTS_") or reason_code.startswith("ACCESS_"):
        return "HIGH"
    return "MEDIUM"

