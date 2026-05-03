from __future__ import annotations

from datetime import datetime, timezone
from pathlib import Path
import sys
import unittest


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


from phase_contract_registry import (  # noqa: E402
    ChangeImpact,
    CompatibilityDecision,
    CompatibilityStatus,
    ContractStatus,
    ContractVersion,
    EntityId,
    EpistemicPolicyFragment,
    MetadataKey,
    MetadataPreservationPolicy,
    ObjectContract,
    PhaseContract,
    PhaseId,
    ScopeKind,
    ScopedContractRef,
    TransitionContract,
    VersionChangeKind,
    compare_versions,
    diff_contracts,
    evaluate_contract_compatibility,
)


FIXED_AT = datetime(2026, 4, 9, 12, 0, tzinfo=timezone.utc)


def make_phase_contract(
    *,
    contract_id: str,
    version: str,
    phase_id: PhaseId = PhaseId.PHASE_1,
    allowed_outputs: tuple[str, ...] = ("canonical_output",),
    required_metadata_keys: tuple[str, ...] = ("site_id",),
    object_ids: tuple[str, ...] = ("object:one",),
    transition_ids: tuple[str, ...] = (),
) -> PhaseContract:
    phase_contract_id = EntityId(contract_id)
    contract_version = ContractVersion.parse(version)
    return PhaseContract(
        phase_contract_id=phase_contract_id,
        phase_id=phase_id,
        contract_version=contract_version,
        contract_status=ContractStatus.PUBLISHED,
        canonical_name=f"{phase_id.value}_contract",
        source_of_authority_ref=f"spec://{phase_id.value}",
        allowed_output_names=allowed_outputs,
        forbidden_output_names=("forbidden_output",),
        required_metadata_keys=tuple(MetadataKey(item) for item in required_metadata_keys),
        epistemic_policy_fragments=(
            EpistemicPolicyFragment(
                policy_key=f"{phase_id.value}.ceiling",
                scope_kind=ScopeKind.PHASE_CONTRACT,
                scope_ref=ScopedContractRef(
                    scope_kind=ScopeKind.PHASE_CONTRACT,
                    identifier=phase_contract_id,
                    version=contract_version,
                ),
                allowed_state_tokens=("decision_grade",),
                forbidden_state_tokens=("verification_grade",),
                must_preserve_uncertainty=True,
                must_preserve_conflict=True,
                output_ceiling_rule="decision_only",
            ),
        ),
        object_contract_ids=tuple(EntityId(item) for item in object_ids),
        transition_contract_ids=tuple(EntityId(item) for item in transition_ids),
        supersedes_contract_id=None,
        created_at=FIXED_AT,
        published_at=FIXED_AT,
        checksum=f"checksum:{contract_id}:{version}",
    )


def make_object_contract(
    *,
    contract_id: str = "object:one",
    phase_contract_id: str = "phase-contract:1",
    required_fields: tuple[str, ...] = ("id",),
    optional_fields: tuple[str, ...] = ("status",),
    forbidden_fields: tuple[str, ...] = ("llm_guess",),
    required_metadata_keys: tuple[str, ...] = ("site_id",),
    immutable_keys: tuple[str, ...] = ("site_id",),
    passthrough_keys: tuple[str, ...] = ("case_id",),
) -> ObjectContract:
    return ObjectContract(
        object_contract_id=EntityId(contract_id),
        phase_contract_id=EntityId(phase_contract_id),
        object_name="canonical_object",
        object_role="contract_payload",
        canonical_purpose="carry contract payload",
        required_fields=required_fields,
        optional_fields=optional_fields,
        forbidden_fields=forbidden_fields,
        required_metadata_keys=tuple(MetadataKey(item) for item in required_metadata_keys),
        metadata_preservation_policy=MetadataPreservationPolicy(
            required_keys=tuple(MetadataKey(item) for item in required_metadata_keys),
            immutable_keys=tuple(MetadataKey(item) for item in immutable_keys),
            passthrough_keys=tuple(MetadataKey(item) for item in passthrough_keys),
            derivable_keys=(),
            missing_key_behavior="error",
            unknown_key_behavior="preserve",
        ),
        allowed_epistemic_state_tokens=("decision_grade",),
        forbidden_epistemic_state_tokens=("verification_grade",),
        created_at=FIXED_AT,
        checksum=f"checksum:{contract_id}",
    )


def make_transition_contract(
    *,
    contract_id: str = "transition:1-2",
    source_phase_contract_id: str = "phase-contract:1",
    target_phase_contract_id: str = "phase-contract:2",
    source_object_id: str = "object:source",
    target_object_id: str = "object:target",
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
                output_ceiling_rule="decision_only",
            ),
        ),
        created_at=FIXED_AT,
        checksum=f"checksum:{contract_id}:{source_phase_contract_id}:{target_phase_contract_id}",
    )


class ContractEvolutionTests(unittest.TestCase):
    def test_compare_versions_detects_change_kind(self) -> None:
        delta = compare_versions(ContractVersion.parse("1.2.0"), ContractVersion.parse("2.0.0"))
        self.assertEqual(delta.change_kind, VersionChangeKind.MAJOR)
        self.assertTrue(delta.changed)

    def test_same_contract_same_version_has_no_changes(self) -> None:
        source = make_phase_contract(contract_id="phase-contract:1", version="1.0.0")
        target = make_phase_contract(contract_id="phase-contract:1", version="1.0.0")

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertFalse(diff_result.has_changes)
        self.assertIsNone(diff_result.diff_record)
        self.assertEqual(compatibility.decision, CompatibilityDecision.COMPATIBLE)
        self.assertEqual(compatibility.compatibility_record.compatibility_status, CompatibilityStatus.COMPATIBLE)

    def test_adding_optional_field_is_additive_and_compatible(self) -> None:
        source = make_object_contract(optional_fields=("status",))
        target = make_object_contract(optional_fields=("status", "explanation"))

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertEqual(len(diff_result.classified_changes), 1)
        self.assertEqual(diff_result.classified_changes[0].impact, ChangeImpact.ADDITIVE)
        self.assertEqual(compatibility.decision, CompatibilityDecision.COMPATIBLE)

    def test_removing_required_field_is_breaking(self) -> None:
        source = make_object_contract(required_fields=("id", "site_id"))
        target = make_object_contract(required_fields=("id",))

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertIn(ChangeImpact.BREAKING, {item.impact for item in diff_result.classified_changes})
        self.assertEqual(compatibility.decision, CompatibilityDecision.INCOMPATIBLE)

    def test_optional_to_required_field_requires_migration(self) -> None:
        source = make_object_contract(required_fields=("id",), optional_fields=("status",))
        target = make_object_contract(required_fields=("id", "status"), optional_fields=())

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertIn(ChangeImpact.RESTRICTIVE, {item.impact for item in diff_result.classified_changes})
        self.assertEqual(compatibility.decision, CompatibilityDecision.MIGRATION_REQUIRED)
        self.assertTrue(compatibility.migration_required)
        self.assertEqual(
            compatibility.compatibility_record.compatibility_status,
            CompatibilityStatus.CONDITIONALLY_COMPATIBLE,
        )

    def test_required_metadata_change_requires_migration(self) -> None:
        source = make_object_contract(required_metadata_keys=("site_id",))
        target = make_object_contract(required_metadata_keys=("site_id", "case_id"))

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertTrue(
            any(change.descriptor.path.startswith("required_metadata_keys.") for change in diff_result.classified_changes)
        )
        self.assertEqual(compatibility.decision, CompatibilityDecision.MIGRATION_REQUIRED)

    def test_transition_phase_change_is_incompatible(self) -> None:
        source = make_transition_contract(
            contract_id="transition:1-2",
            source_phase_contract_id="phase-contract:1",
            target_phase_contract_id="phase-contract:2",
        )
        target = make_transition_contract(
            contract_id="transition:1-2",
            source_phase_contract_id="phase-contract:1",
            target_phase_contract_id="phase-contract:3",
        )

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertTrue(
            any(change.descriptor.path == "target_phase_contract_id" for change in diff_result.classified_changes)
        )
        self.assertEqual(compatibility.decision, CompatibilityDecision.INCOMPATIBLE)

    def test_new_contract_can_require_migration_without_becoming_fully_incompatible(self) -> None:
        source = make_phase_contract(
            contract_id="phase-contract:1",
            version="1.0.0",
            required_metadata_keys=("site_id",),
        )
        target = make_phase_contract(
            contract_id="phase-contract:2",
            version="1.1.0",
            required_metadata_keys=("site_id", "case_id"),
        )

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertEqual(diff_result.version_delta.change_kind, VersionChangeKind.MINOR)
        self.assertEqual(compatibility.decision, CompatibilityDecision.MIGRATION_REQUIRED)
        self.assertTrue(compatibility.migration_required)

    def test_removing_allowed_status_transform_is_breaking(self) -> None:
        source = make_transition_contract(allowed_status_transforms=("promote", "maintain"))
        target = make_transition_contract(allowed_status_transforms=("promote",))

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertIn(ChangeImpact.BREAKING, {item.impact for item in diff_result.classified_changes})
        self.assertEqual(compatibility.decision, CompatibilityDecision.INCOMPATIBLE)

    def test_clearly_compatible_phase_change_is_additive(self) -> None:
        source = make_phase_contract(
            contract_id="phase-contract:1",
            version="1.0.0",
            allowed_outputs=("canonical_output",),
        )
        target = make_phase_contract(
            contract_id="phase-contract:2",
            version="1.1.0",
            allowed_outputs=("canonical_output", "secondary_output"),
        )

        diff_result = diff_contracts(source, target, generated_at=FIXED_AT)
        compatibility = evaluate_contract_compatibility(source, target, generated_at=FIXED_AT)

        self.assertTrue(diff_result.has_changes)
        self.assertTrue(all(item.impact is ChangeImpact.ADDITIVE for item in diff_result.classified_changes))
        self.assertEqual(compatibility.decision, CompatibilityDecision.COMPATIBLE)


if __name__ == "__main__":
    unittest.main()
