from __future__ import annotations

from datetime import datetime, timezone
import unittest

from entity_identity_resolution_engine.domain import (
    AmbiguityBasis,
    AmbiguityStatus,
    AmbiguousResolutionRecord,
    CandidateMatchRecord,
    CandidateMatchRecordId,
    CandidateMatchSet,
    CandidateMatchSetId,
    CandidateMatchStatus,
    CanonicalEntity,
    CanonicalEntityStatus,
    CanonicalName,
    ConfidenceMethod,
    ConfidenceStatus,
    ConfidenceValue,
    ConfirmedMatchRecord,
    EntityHistoryRecord,
    EntityHistoryRecordId,
    EntityHistorySummary,
    EntityId,
    EntityType,
    EvidenceBasisType,
    EvidenceSummary,
    HistoricalEventType,
    HistoryStatus,
    MergeEventRecord,
    MergeEventRecordId,
    NoMatchRecord,
    NormalizedFieldRef,
    NormalizedRecordRef,
    ObservedLabel,
    ObservedNameRecord,
    ObservedNameRecordId,
    ObservedRecord,
    ObservedRecordId,
    ResolutionConfidenceRecord,
    ResolutionConfidenceRecordId,
    ResolutionDecisionRecord,
    ResolutionDecisionRecordId,
    ResolutionEvidenceRecord,
    ResolutionEvidenceRecordId,
    ResolutionMode,
    ResolutionStatus,
    Rationale,
    SourceProvenanceRefs,
    SplitEventRecord,
    SplitEventRecordId,
)
from entity_identity_resolution_engine.validation import (
    BasicIdentityIntegrityValidator,
    ValidationOutcome,
)


UTC = timezone.utc


def fixed_now() -> datetime:
    return datetime(2026, 4, 10, 22, 30, tzinfo=UTC)


class IdentityResolutionOutcomeTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicIdentityIntegrityValidator(clock=fixed_now)

    def test_no_match_record_valid_and_reason_preserved(self) -> None:
        graph = self._build_no_match_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        self.assertEqual(
            graph["no_match_records"][0].rationale.value,
            "Same surface label but conflicting company context.",
        )
        codes = {item.code for item in report.violations}
        self.assertIn("no_match.declared", codes)
        self.assertNotIn("ambiguous.declared", codes)
        self.assertNotIn("confirmed_match.decision_status_mismatch", codes)

    def test_ambiguous_resolution_valid_and_not_presented_as_closed(self) -> None:
        graph = self._build_ambiguous_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        self.assertEqual(
            graph["ambiguous_resolution_records"][0].ambiguity_basis.value,
            "Same label, insufficient parent context.",
        )
        codes = {item.code for item in report.violations}
        self.assertIn("ambiguous.declared", codes)
        self.assertNotIn("confirmed_match.decision_status_mismatch", codes)
        self.assertNotIn("no_match.decision_status_mismatch", codes)

    def test_confirmed_match_record_keeps_clear_entity_target_and_decision_link(self) -> None:
        graph = self._build_confirmed_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        confirmed = graph["confirmed_match_records"][0]
        decision = graph["resolution_decision_records"][0]
        entity = graph["canonical_entities"][0]
        self.assertEqual(confirmed.entity_id, entity.entity_id)
        self.assertEqual(
            confirmed.resolution_decision_record_id,
            decision.resolution_decision_record_id,
        )

    def test_merge_event_record_valid_with_minimal_historical_coherence(self) -> None:
        graph = self._build_merge_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        merge_event = graph["merge_event_records"][0]
        self.assertEqual(len(merge_event.merged_entity_ids), 2)
        self.assertEqual(merge_event.event_type, HistoricalEventType.MERGE)

    def test_split_event_record_valid_with_prior_entity_reference(self) -> None:
        graph = self._build_split_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        split_event = graph["split_event_records"][0]
        self.assertEqual(split_event.source_entity_id, EntityId("entity:plant:1"))
        self.assertEqual(len(split_event.successor_entity_ids), 2)

    def test_resolution_does_not_overwrite_observed_labels(self) -> None:
        graph = self._build_confirmed_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        observed_labels = [
            item.observed_label.value for item in graph["observed_name_records"]
        ]
        self.assertEqual(observed_labels, ["Con Edison", "Consolidated Edison"])
        self.assertNotEqual(
            graph["canonical_entities"][0].canonical_name.value,
            graph["observed_name_records"][0].observed_label.value,
        )

    def _build_confirmed_graph(self) -> dict[str, tuple]:
        observed_1, name_1 = self._observed(
            "observed:1",
            "name:1",
            "Con Edison",
            EntityType.UTILITY,
        )
        observed_2, name_2 = self._observed(
            "observed:2",
            "name:2",
            "Consolidated Edison",
            EntityType.UTILITY,
        )
        entity = self._entity(
            "entity:utility:1",
            "Consolidated Edison Company of New York",
            EntityType.UTILITY,
        )
        evidence = self._evidence(
            "evidence:1",
            observed_1.source_provenance,
            EvidenceBasisType.GOVERNED_ALIAS,
            True,
            "Governed alias plus utility context.",
        )
        confidence = self._confidence(
            "confidence:1",
            ConfidenceStatus.HIGH,
            "rule_based_exact_alias",
            "0.97",
            "Alias and context are governed and consistent.",
        )
        candidate_set = CandidateMatchSet(
            candidate_match_set_id=CandidateMatchSetId("candidate-set:1"),
            anchor_observed_record_ids=(observed_1.observed_record_id,),
            candidate_match_record_ids=(CandidateMatchRecordId("candidate-match:1"),),
            candidate_match_status=CandidateMatchStatus.CONFIRMED,
            created_at=fixed_now(),
        )
        candidate_match = CandidateMatchRecord(
            candidate_match_record_id=CandidateMatchRecordId("candidate-match:1"),
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            source_observed_record_id=observed_1.observed_record_id,
            candidate_observed_record_ids=(observed_2.observed_record_id,),
            candidate_entity_id=entity.entity_id,
            candidate_match_status=CandidateMatchStatus.CONFIRMED,
            rationale=Rationale(
                "Observed names and governed context support the same utility identity."
            ),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:1"),
            resolution_status=ResolutionStatus.CONFIRMED,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            decision_scope_observed_record_ids=(
                observed_1.observed_record_id,
                observed_2.observed_record_id,
            ),
            rationale=Rationale(
                "Identity confirmed under explicit alias and context rules."
            ),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        confirmed = ConfirmedMatchRecord(
            resolution_decision_record_id=decision.resolution_decision_record_id,
            entity_id=entity.entity_id,
            observed_record_ids=(
                observed_1.observed_record_id,
                observed_2.observed_record_id,
            ),
            created_at=fixed_now(),
        )
        history = EntityHistoryRecord(
            entity_history_record_id=EntityHistoryRecordId("history:confirmed"),
            entity_id=entity.entity_id,
            history_status=HistoryStatus.ACTIVE,
            resolution_decision_record_id=decision.resolution_decision_record_id,
            merge_event_record_id=None,
            split_event_record_id=None,
            summary=EntityHistorySummary("Active confirmed utility identity."),
            effective_from=fixed_now(),
            effective_to=None,
            created_at=fixed_now(),
        )
        return {
            "observed_records": (observed_1, observed_2),
            "observed_name_records": (name_1, name_2),
            "canonical_entities": (entity,),
            "entity_alias_records": (),
            "candidate_match_records": (candidate_match,),
            "candidate_match_sets": (candidate_set,),
            "resolution_decision_records": (decision,),
            "confirmed_match_records": (confirmed,),
            "no_match_records": (),
            "ambiguous_resolution_records": (),
            "related_records": (),
            "resolution_evidence_records": (evidence,),
            "resolution_confidence_records": (confidence,),
            "merge_event_records": (),
            "split_event_records": (),
            "entity_history_records": (history,),
        }

    def _build_no_match_graph(self) -> dict[str, tuple]:
        observed_1, name_1 = self._observed(
            "observed:n1",
            "name:n1",
            "Plant 2",
            EntityType.PLANT,
        )
        observed_2, name_2 = self._observed(
            "observed:n2",
            "name:n2",
            "Plant 2",
            EntityType.PLANT,
        )
        evidence = self._evidence(
            "evidence:n1",
            observed_1.source_provenance,
            EvidenceBasisType.NORMALIZED_NAME,
            False,
            "Same label but conflicting company context.",
        )
        confidence = self._confidence(
            "confidence:n1",
            ConfidenceStatus.MODERATE,
            "context_conflict_rule",
            "0.62",
            "Conflict in parent company context rejects shared identity.",
        )
        candidate_set = CandidateMatchSet(
            candidate_match_set_id=CandidateMatchSetId("candidate-set:n1"),
            anchor_observed_record_ids=(observed_1.observed_record_id,),
            candidate_match_record_ids=(CandidateMatchRecordId("candidate-match:n1"),),
            candidate_match_status=CandidateMatchStatus.REJECTED,
            created_at=fixed_now(),
        )
        candidate_match = CandidateMatchRecord(
            candidate_match_record_id=CandidateMatchRecordId("candidate-match:n1"),
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            source_observed_record_id=observed_1.observed_record_id,
            candidate_observed_record_ids=(observed_2.observed_record_id,),
            candidate_entity_id=None,
            candidate_match_status=CandidateMatchStatus.REJECTED,
            rationale=Rationale("Conflicting parent context prevents a shared entity."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:n1"),
            resolution_status=ResolutionStatus.NO_MATCH,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            decision_scope_observed_record_ids=(
                observed_1.observed_record_id,
                observed_2.observed_record_id,
            ),
            rationale=Rationale("Same surface label but conflicting company context."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        no_match = NoMatchRecord(
            resolution_decision_record_id=decision.resolution_decision_record_id,
            subject_observed_record_id=observed_1.observed_record_id,
            rejected_observed_record_ids=(observed_2.observed_record_id,),
            rejected_entity_id=None,
            rationale=Rationale("Same surface label but conflicting company context."),
            created_at=fixed_now(),
        )
        return {
            "observed_records": (observed_1, observed_2),
            "observed_name_records": (name_1, name_2),
            "canonical_entities": (),
            "entity_alias_records": (),
            "candidate_match_records": (candidate_match,),
            "candidate_match_sets": (candidate_set,),
            "resolution_decision_records": (decision,),
            "confirmed_match_records": (),
            "no_match_records": (no_match,),
            "ambiguous_resolution_records": (),
            "related_records": (),
            "resolution_evidence_records": (evidence,),
            "resolution_confidence_records": (confidence,),
            "merge_event_records": (),
            "split_event_records": (),
            "entity_history_records": (),
        }

    def _build_ambiguous_graph(self) -> dict[str, tuple]:
        observed_1, name_1 = self._observed(
            "observed:a1",
            "name:a1",
            "Plant 2",
            EntityType.PLANT,
        )
        observed_2, name_2 = self._observed(
            "observed:a2",
            "name:a2",
            "Plant 2",
            EntityType.PLANT,
        )
        evidence = self._evidence(
            "evidence:a1",
            observed_1.source_provenance,
            EvidenceBasisType.NORMALIZED_NAME,
            True,
            "Name similarity only.",
        )
        confidence = self._confidence(
            "confidence:a1",
            ConfidenceStatus.INSUFFICIENT,
            "label_similarity_only",
            None,
            "Textual similarity alone is insufficient.",
        )
        candidate_set = CandidateMatchSet(
            candidate_match_set_id=CandidateMatchSetId("candidate-set:a1"),
            anchor_observed_record_ids=(observed_1.observed_record_id,),
            candidate_match_record_ids=(CandidateMatchRecordId("candidate-match:a1"),),
            candidate_match_status=CandidateMatchStatus.OPEN,
            created_at=fixed_now(),
        )
        candidate_match = CandidateMatchRecord(
            candidate_match_record_id=CandidateMatchRecordId("candidate-match:a1"),
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            source_observed_record_id=observed_1.observed_record_id,
            candidate_observed_record_ids=(observed_2.observed_record_id,),
            candidate_entity_id=None,
            candidate_match_status=CandidateMatchStatus.OPEN,
            rationale=Rationale(
                "Candidate remains open under superficial label similarity."
            ),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:a1"),
            resolution_status=ResolutionStatus.AMBIGUOUS,
            resolution_mode=ResolutionMode.CARRIED_FORWARD,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            decision_scope_observed_record_ids=(
                observed_1.observed_record_id,
                observed_2.observed_record_id,
            ),
            rationale=Rationale("Insufficient context to confirm or reject."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        ambiguous = AmbiguousResolutionRecord(
            resolution_decision_record_id=decision.resolution_decision_record_id,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            observed_record_ids=(
                observed_1.observed_record_id,
                observed_2.observed_record_id,
            ),
            plausible_entity_ids=(),
            ambiguity_status=AmbiguityStatus.OPEN,
            ambiguity_basis=AmbiguityBasis("Same label, insufficient parent context."),
            created_at=fixed_now(),
        )
        return {
            "observed_records": (observed_1, observed_2),
            "observed_name_records": (name_1, name_2),
            "canonical_entities": (),
            "entity_alias_records": (),
            "candidate_match_records": (candidate_match,),
            "candidate_match_sets": (candidate_set,),
            "resolution_decision_records": (decision,),
            "confirmed_match_records": (),
            "no_match_records": (),
            "ambiguous_resolution_records": (ambiguous,),
            "related_records": (),
            "resolution_evidence_records": (evidence,),
            "resolution_confidence_records": (confidence,),
            "merge_event_records": (),
            "split_event_records": (),
            "entity_history_records": (),
        }

    def _build_merge_graph(self) -> dict[str, tuple]:
        observed_1, name_1 = self._observed(
            "observed:m1",
            "name:m1",
            "Con Edison",
            EntityType.UTILITY,
        )
        observed_2, name_2 = self._observed(
            "observed:m2",
            "name:m2",
            "Consolidated Edison",
            EntityType.UTILITY,
        )
        entity_1 = self._entity("entity:utility:1", "Con Edison", EntityType.UTILITY)
        entity_2 = self._entity(
            "entity:utility:2",
            "Consolidated Edison",
            EntityType.UTILITY,
        )
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:m1"),
            resolution_status=ResolutionStatus.MERGED,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=None,
            decision_scope_observed_record_ids=(
                observed_1.observed_record_id,
                observed_2.observed_record_id,
            ),
            rationale=Rationale(
                "Governed identity merge after confirming historical alias continuity."
            ),
            evidence_record_ids=(),
            confidence_record_id=None,
            created_at=fixed_now(),
        )
        merge_event = MergeEventRecord(
            merge_event_record_id=MergeEventRecordId("merge:1"),
            merged_entity_ids=(entity_1.entity_id, entity_2.entity_id),
            surviving_entity_id=entity_1.entity_id,
            resolution_decision_record_id=decision.resolution_decision_record_id,
            rationale=Rationale(
                "Entity 2 merged into entity 1 after identity confirmation."
            ),
            event_type=HistoricalEventType.MERGE,
            effective_from=fixed_now(),
            created_at=fixed_now(),
        )
        history = EntityHistoryRecord(
            entity_history_record_id=EntityHistoryRecordId("history:m1"),
            entity_id=entity_1.entity_id,
            history_status=HistoryStatus.MERGED,
            resolution_decision_record_id=decision.resolution_decision_record_id,
            merge_event_record_id=merge_event.merge_event_record_id,
            split_event_record_id=None,
            summary=EntityHistorySummary("Merged identity lineage preserved."),
            effective_from=fixed_now(),
            effective_to=None,
            created_at=fixed_now(),
        )
        return {
            "observed_records": (observed_1, observed_2),
            "observed_name_records": (name_1, name_2),
            "canonical_entities": (entity_1, entity_2),
            "entity_alias_records": (),
            "candidate_match_records": (),
            "candidate_match_sets": (),
            "resolution_decision_records": (decision,),
            "confirmed_match_records": (),
            "no_match_records": (),
            "ambiguous_resolution_records": (),
            "related_records": (),
            "resolution_evidence_records": (),
            "resolution_confidence_records": (),
            "merge_event_records": (merge_event,),
            "split_event_records": (),
            "entity_history_records": (history,),
        }

    def _build_split_graph(self) -> dict[str, tuple]:
        observed_1, name_1 = self._observed(
            "observed:s1",
            "name:s1",
            "Plant 2",
            EntityType.PLANT,
        )
        entity_1 = self._entity("entity:plant:1", "Plant 2", EntityType.PLANT)
        entity_2 = self._entity("entity:plant:2", "Plant 2A", EntityType.PLANT)
        entity_3 = self._entity("entity:plant:3", "Plant 2B", EntityType.PLANT)
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:s1"),
            resolution_status=ResolutionStatus.SPLIT,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=None,
            decision_scope_observed_record_ids=(observed_1.observed_record_id,),
            rationale=Rationale(
                "New evidence shows the previous entity represented two distinct plants."
            ),
            evidence_record_ids=(),
            confidence_record_id=None,
            created_at=fixed_now(),
        )
        split_event = SplitEventRecord(
            split_event_record_id=SplitEventRecordId("split:1"),
            source_entity_id=entity_1.entity_id,
            successor_entity_ids=(entity_2.entity_id, entity_3.entity_id),
            resolution_decision_record_id=decision.resolution_decision_record_id,
            rationale=Rationale(
                "Entity split preserves historical lineage and successor entities."
            ),
            event_type=HistoricalEventType.SPLIT,
            effective_from=fixed_now(),
            created_at=fixed_now(),
        )
        history = EntityHistoryRecord(
            entity_history_record_id=EntityHistoryRecordId("history:s1"),
            entity_id=entity_1.entity_id,
            history_status=HistoryStatus.SPLIT,
            resolution_decision_record_id=decision.resolution_decision_record_id,
            merge_event_record_id=None,
            split_event_record_id=split_event.split_event_record_id,
            summary=EntityHistorySummary("Source entity split into two successors."),
            effective_from=fixed_now(),
            effective_to=None,
            created_at=fixed_now(),
        )
        return {
            "observed_records": (observed_1,),
            "observed_name_records": (name_1,),
            "canonical_entities": (entity_1, entity_2, entity_3),
            "entity_alias_records": (),
            "candidate_match_records": (),
            "candidate_match_sets": (),
            "resolution_decision_records": (decision,),
            "confirmed_match_records": (),
            "no_match_records": (),
            "ambiguous_resolution_records": (),
            "related_records": (),
            "resolution_evidence_records": (),
            "resolution_confidence_records": (),
            "merge_event_records": (),
            "split_event_records": (split_event,),
            "entity_history_records": (history,),
        }

    def _observed(
        self,
        record_id: str,
        name_id: str,
        label: str,
        entity_type: EntityType,
    ) -> tuple[ObservedRecord, ObservedNameRecord]:
        observed_name = ObservedNameRecord(
            observed_name_record_id=ObservedNameRecordId(name_id),
            observed_record_id=ObservedRecordId(record_id),
            observed_label=ObservedLabel(label),
            is_primary=True,
            source_normalized_field_ref=NormalizedFieldRef(f"normalized-field:{record_id}"),
            created_at=fixed_now(),
        )
        observed_record = ObservedRecord(
            observed_record_id=ObservedRecordId(record_id),
            entity_type=entity_type,
            source_provenance=SourceProvenanceRefs(
                normalized_record_ref=NormalizedRecordRef(f"normalized-record:{record_id}"),
                normalized_field_refs=(NormalizedFieldRef(f"normalized-field:{record_id}"),),
            ),
            primary_observed_name_record_id=observed_name.observed_name_record_id,
            observed_name_record_ids=(observed_name.observed_name_record_id,),
            created_at=fixed_now(),
        )
        return observed_record, observed_name

    def _entity(
        self,
        entity_id: str,
        canonical_name: str,
        entity_type: EntityType,
    ) -> CanonicalEntity:
        return CanonicalEntity(
            entity_id=EntityId(entity_id),
            entity_type=entity_type,
            canonical_name=CanonicalName(canonical_name),
            entity_status=CanonicalEntityStatus.ACTIVE,
            created_at=fixed_now(),
            effective_from=fixed_now(),
        )

    def _evidence(
        self,
        evidence_id: str,
        provenance: SourceProvenanceRefs,
        basis_type: EvidenceBasisType,
        supports_match: bool,
        summary: str,
    ) -> ResolutionEvidenceRecord:
        return ResolutionEvidenceRecord(
            resolution_evidence_record_id=ResolutionEvidenceRecordId(evidence_id),
            evidence_basis_type=basis_type,
            source_provenance=provenance,
            supports_match=supports_match,
            evidence_summary=EvidenceSummary(summary),
            created_at=fixed_now(),
        )

    def _confidence(
        self,
        confidence_id: str,
        status: ConfidenceStatus,
        method: str,
        value: str | None,
        rationale: str,
    ) -> ResolutionConfidenceRecord:
        return ResolutionConfidenceRecord(
            resolution_confidence_record_id=ResolutionConfidenceRecordId(confidence_id),
            confidence_status=status,
            confidence_method=ConfidenceMethod(method),
            confidence_value=ConfidenceValue(value) if value is not None else None,
            rationale=Rationale(rationale),
            created_at=fixed_now(),
        )


if __name__ == "__main__":
    unittest.main()
