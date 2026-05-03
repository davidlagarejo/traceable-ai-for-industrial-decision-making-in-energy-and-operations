from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from phase_contract_registry import (  # noqa: E402
    BasicContractValidator,
    ContractStatus,
    ContractVersion,
    EntityId,
    EpistemicPolicyFragment,
    MetadataKey,
    MetadataPreservationPolicy,
    ObjectContract,
    PhaseContract,
    PhaseId,
    RuleCode,
    ScopeKind,
    ScopedContractRef,
    TransitionContract,
    ValidationOutcome,
    ValidationStatus,
    ViolationSeverity,
)


FIXED_AT = datetime(2026, 4, 9, 12, 0, tzinfo=timezone.utc)


def make_phase_contract(
    *,
    contract_id: str,
    phase_id: PhaseId,
    object_ids: tuple[str, ...],
    transition_ids: tuple[str, ...] = (),
) -> PhaseContract:
    phase_contract_id = EntityId(contract_id)
    version = ContractVersion(1, 0, 0)
    return PhaseContract(
        phase_contract_id=phase_contract_id,
        phase_id=phase_id,
        contract_version=version,
        contract_status=ContractStatus.PUBLISHED,
        canonical_name=f"{phase_id.value}_contract",
        source_of_authority_ref=f"spec://{phase_id.value}",
        allowed_output_names=("canonical_output",),
        forbidden_output_names=("forbidden_output",),
        required_metadata_keys=(MetadataKey("site_id"),),
        epistemic_policy_fragments=(
            EpistemicPolicyFragment(
                policy_key=f"{phase_id.value}.ceiling",
                scope_kind=ScopeKind.PHASE_CONTRACT,
                scope_ref=ScopedContractRef(
                    scope_kind=ScopeKind.PHASE_CONTRACT,
                    identifier=phase_contract_id,
                    version=version,
                ),
                allowed_state_tokens=("decision_grade",),
                forbidden_state_tokens=("verification_grade",),
                must_preserve_uncertainty=True,
                must_preserve_conflict=True,
                output_ceiling_rule="decision_grade_only",
            ),
        ),
        object_contract_ids=tuple(EntityId(item) for item in object_ids),
        transition_contract_ids=tuple(EntityId(item) for item in transition_ids),
        supersedes_contract_id=None,
        created_at=FIXED_AT,
        published_at=FIXED_AT,
        checksum=f"checksum:{contract_id}",
    )


def make_object_contract(
    *,
    contract_id: str,
    phase_contract_id: str,
    object_name: str,
    required_keys: tuple[str, ...] = ("site_id",),
    required_fields: tuple[str, ...] = ("id",),
    optional_fields: tuple[str, ...] = ("status",),
    forbidden_fields: tuple[str, ...] = ("llm_guess",),
    allowed_epistemic_tokens: tuple[str, ...] = ("decision_grade",),
    forbidden_epistemic_tokens: tuple[str, ...] = ("verification_grade",),
) -> ObjectContract:
    metadata_keys = tuple(MetadataKey(item) for item in required_keys)
    return ObjectContract(
        object_contract_id=EntityId(contract_id),
        phase_contract_id=EntityId(phase_contract_id),
        object_name=object_name,
        object_role="canonical_object",
        canonical_purpose="carry validated structure",
        required_fields=required_fields,
        optional_fields=optional_fields,
        forbidden_fields=forbidden_fields,
        required_metadata_keys=metadata_keys,
        metadata_preservation_policy=MetadataPreservationPolicy(
            required_keys=metadata_keys,
            immutable_keys=(MetadataKey("site_id"),),
            passthrough_keys=(MetadataKey("case_id"),),
            derivable_keys=(),
            missing_key_behavior="error",
            unknown_key_behavior="preserve",
        ),
        allowed_epistemic_state_tokens=allowed_epistemic_tokens,
        forbidden_epistemic_state_tokens=forbidden_epistemic_tokens,
        created_at=FIXED_AT,
        checksum=f"checksum:{contract_id}",
    )


def make_transition_contract(
    *,
    contract_id: str,
    source_phase_contract_id: str,
    target_phase_contract_id: str,
    source_object_id: str,
    target_object_id: str,
    required_metadata_keys: tuple[str, ...] = ("site_id",),
    required_preconditions: tuple[str, ...] = ("source_ready",),
    allowed_status_transforms: tuple[str, ...] = ("promote",),
    blocked_status_transforms: tuple[str, ...] = ("block",),
) -> TransitionContract:
    transition_contract_id = EntityId(contract_id)
    return TransitionContract(
        transition_contract_id=transition_contract_id,
        source_phase_contract_id=EntityId(source_phase_contract_id),
        target_phase_contract_id=EntityId(target_phase_contract_id),
        transition_name=f"{source_phase_contract_id}_to_{target_phase_contract_id}",
        source_object_refs=(
            ScopedContractRef(
                scope_kind=ScopeKind.OBJECT_CONTRACT,
                identifier=EntityId(source_object_id),
            ),
        ),
        target_object_refs=(
            ScopedContractRef(
                scope_kind=ScopeKind.OBJECT_CONTRACT,
                identifier=EntityId(target_object_id),
            ),
        ),
        required_preconditions=required_preconditions,
        required_metadata_keys=tuple(MetadataKey(item) for item in required_metadata_keys),
        prohibited_transforms=("silent_upgrade",),
        allowed_status_transforms=allowed_status_transforms,
        blocked_status_transforms=blocked_status_transforms,
        epistemic_policy_fragments=(
            EpistemicPolicyFragment(
                policy_key=f"{contract_id}.handoff",
                scope_kind=ScopeKind.TRANSITION_CONTRACT,
                scope_ref=ScopedContractRef(
                    scope_kind=ScopeKind.TRANSITION_CONTRACT,
                    identifier=transition_contract_id,
                ),
                allowed_state_tokens=("decision_grade",),
                forbidden_state_tokens=("verification_grade",),
                must_preserve_uncertainty=True,
                must_preserve_conflict=True,
                output_ceiling_rule="no_epistemic_upgrade",
            ),
        ),
        created_at=FIXED_AT,
        checksum=f"checksum:{contract_id}",
    )


class BasicContractValidatorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicContractValidator(clock=lambda: FIXED_AT)

    def test_validate_phase_contract_passes_with_complete_context(self) -> None:
        phase_1 = make_phase_contract(
            contract_id="phase-contract:1",
            phase_id=PhaseId.PHASE_1,
            object_ids=("object:phase1",),
            transition_ids=("transition:1-2",),
        )
        object_1 = make_object_contract(
            contract_id="object:phase1",
            phase_contract_id="phase-contract:1",
            object_name="phase_1_object",
        )
        transition = make_transition_contract(
            contract_id="transition:1-2",
            source_phase_contract_id="phase-contract:1",
            target_phase_contract_id="phase-contract:2",
            source_object_id="object:phase1",
            target_object_id="object:phase2",
        )

        report = self.validator.validate_phase_contract(
            phase_1,
            object_contracts=(object_1,),
            transition_contracts=(transition,),
            payload_metadata={"site_id": "SITE-001"},
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertEqual(report.validation_run_record.validation_status, ValidationStatus.PASSED)
        self.assertEqual(report.violation_records, ())

    def test_validate_object_contract_fails_on_missing_required_metadata(self) -> None:
        phase_1 = make_phase_contract(
            contract_id="phase-contract:1",
            phase_id=PhaseId.PHASE_1,
            object_ids=("object:phase1",),
        )
        object_1 = make_object_contract(
            contract_id="object:phase1",
            phase_contract_id="phase-contract:1",
            object_name="phase_1_object",
            required_keys=("site_id", "case_id"),
        )

        report = self.validator.validate_object_contract(
            object_1,
            phase_contract=phase_1,
            payload_metadata={"site_id": "SITE-001"},
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertEqual(report.validation_run_record.validation_status, ValidationStatus.FAILED)
        self.assertEqual(len(report.violation_records), 1)
        violation = report.violation_records[0]
        self.assertEqual(violation.rule_code, RuleCode.METADATA_REQUIRED_KEY_MISSING.value)
        self.assertEqual(violation.violation_severity, ViolationSeverity.ERROR)
        self.assertTrue(violation.blocking)

    def test_validate_object_contract_passes_with_warnings_when_shape_is_too_thin(self) -> None:
        phase_1 = make_phase_contract(
            contract_id="phase-contract:1",
            phase_id=PhaseId.PHASE_1,
            object_ids=("object:thin",),
        )
        object_1 = make_object_contract(
            contract_id="object:thin",
            phase_contract_id="phase-contract:1",
            object_name="thin_object",
            required_fields=(),
            optional_fields=(),
            forbidden_fields=(),
            allowed_epistemic_tokens=(),
            forbidden_epistemic_tokens=(),
        )

        report = self.validator.validate_object_contract(object_1, phase_contract=phase_1)

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        self.assertEqual(report.validation_run_record.validation_status, ValidationStatus.PASSED)
        self.assertEqual(
            {item.rule_code for item in report.violation_records},
            {
                RuleCode.OBJECT_EMPTY_FIELD_SHAPE.value,
                RuleCode.OBJECT_EMPTY_EPISTEMIC_TOKEN_SET.value,
            },
        )

    def test_validate_transition_contract_passes_for_allowed_handoff(self) -> None:
        source_phase = make_phase_contract(
            contract_id="phase-contract:1",
            phase_id=PhaseId.PHASE_1,
            object_ids=("object:source",),
            transition_ids=("transition:1-2",),
        )
        target_phase = make_phase_contract(
            contract_id="phase-contract:2",
            phase_id=PhaseId.PHASE_2,
            object_ids=("object:target",),
            transition_ids=("transition:1-2",),
        )
        source_object = make_object_contract(
            contract_id="object:source",
            phase_contract_id="phase-contract:1",
            object_name="source_object",
        )
        target_object = make_object_contract(
            contract_id="object:target",
            phase_contract_id="phase-contract:2",
            object_name="target_object",
            required_keys=("site_id", "case_id"),
        )
        transition = make_transition_contract(
            contract_id="transition:1-2",
            source_phase_contract_id="phase-contract:1",
            target_phase_contract_id="phase-contract:2",
            source_object_id="object:source",
            target_object_id="object:target",
            required_metadata_keys=("site_id",),
            required_preconditions=("source_ready",),
            allowed_status_transforms=("promote",),
            blocked_status_transforms=("block",),
        )

        report = self.validator.validate_transition_contract(
            transition,
            source_phase_contract=source_phase,
            target_phase_contract=target_phase,
            source_object_contracts=(source_object,),
            target_object_contracts=(target_object,),
            handoff_metadata={"site_id": "SITE-001"},
            source_metadata={"site_id": "SITE-001", "case_id": "CASE-001"},
            target_metadata={"site_id": "SITE-001", "case_id": "CASE-001"},
            completed_preconditions=("source_ready",),
            requested_status_transform="promote",
        )

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertEqual(report.violation_records, ())

    def test_validate_transition_contract_collects_multiple_violations(self) -> None:
        phase_1 = make_phase_contract(
            contract_id="phase-contract:1",
            phase_id=PhaseId.PHASE_1,
            object_ids=("object:source", "object:target"),
            transition_ids=("transition:self",),
        )
        source_object = make_object_contract(
            contract_id="object:source",
            phase_contract_id="phase-contract:1",
            object_name="source_object",
        )
        target_object = make_object_contract(
            contract_id="object:target",
            phase_contract_id="phase-contract:1",
            object_name="target_object",
            required_keys=("site_id", "case_id"),
        )
        transition = make_transition_contract(
            contract_id="transition:self",
            source_phase_contract_id="phase-contract:1",
            target_phase_contract_id="phase-contract:1",
            source_object_id="object:source",
            target_object_id="object:target",
            required_metadata_keys=("site_id",),
            required_preconditions=("source_ready", "metadata_locked"),
            allowed_status_transforms=("promote",),
            blocked_status_transforms=("block",),
        )

        report = self.validator.validate_transition_contract(
            transition,
            source_phase_contract=phase_1,
            target_phase_contract=phase_1,
            source_object_contracts=(source_object,),
            target_object_contracts=(target_object,),
            handoff_metadata={},
            source_metadata={"site_id": "SITE-001", "case_id": "CASE-001"},
            target_metadata={"site_id": "SITE-999"},
            completed_preconditions=(),
            requested_status_transform="block",
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        self.assertEqual(report.validation_run_record.validation_status, ValidationStatus.FAILED)
        self.assertGreaterEqual(len(report.violation_records), 5)
        self.assertEqual(
            report.validation_run_record.violation_ids,
            tuple(item.violation_record_id for item in report.violation_records),
        )
        self.assertIn(
            RuleCode.TRANSITION_SELF_HANDOFF.value,
            {item.rule_code for item in report.violation_records},
        )
        self.assertIn(
            RuleCode.TRANSITION_STATUS_TRANSFORM_BLOCKED.value,
            {item.rule_code for item in report.violation_records},
        )
        self.assertIn(
            RuleCode.METADATA_REQUIRED_KEY_MISSING.value,
            {item.rule_code for item in report.violation_records},
        )


if __name__ == "__main__":
    unittest.main()
