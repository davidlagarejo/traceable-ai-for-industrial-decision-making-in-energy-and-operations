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
    EntityAliasRecord,
    EntityAliasRecordId,
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
    RelatedButNotEquivalentRecord,
    RelatedEntityRelationshipType,
    RelationBasis,
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
    return datetime(2026, 4, 10, 22, 0, tzinfo=UTC)


class BasicIdentityValidatorTest(unittest.TestCase):
    def setUp(self) -> None:
        self.validator = BasicIdentityIntegrityValidator(clock=fixed_now)

    def test_confirmed_resolution_graph_passes(self) -> None:
        graph = self._build_confirmed_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS)
        self.assertFalse(report.violations)

    def test_ambiguous_open_graph_returns_pass_with_warnings(self) -> None:
        graph = self._build_ambiguous_graph()

        report = self.validator.validate_graph(**graph)

        self.assertEqual(report.outcome, ValidationOutcome.PASS_WITH_WARNINGS)
        codes = {item.code for item in report.violations}
        self.assertIn("candidate_match.open_declared", codes)
        self.assertIn("ambiguous.declared", codes)
        self.assertIn("confidence.insufficient_declared", codes)

    def test_multiple_reference_breaks_fail_in_single_run(self) -> None:
        graph = self._build_confirmed_graph()
        bad_alias = EntityAliasRecord(
            entity_alias_record_id=EntityAliasRecordId("alias:broken"),
            entity_id=EntityId("entity:missing"),
            alias_label=graph["entity_alias_records"][0].alias_label,
            source_observed_name_record_id=ObservedNameRecordId("name:missing"),
            created_at=fixed_now(),
        )
        bad_match = CandidateMatchRecord(
            candidate_match_record_id=CandidateMatchRecordId("candidate-match:broken"),
            candidate_match_set_id=graph["candidate_match_sets"][0].candidate_match_set_id,
            source_observed_record_id=ObservedRecordId("observed:missing"),
            candidate_observed_record_ids=(ObservedRecordId("observed:missing-2"),),
            candidate_entity_id=EntityId("entity:missing"),
            candidate_match_status=CandidateMatchStatus.CONFIRMED,
            rationale=Rationale("Broken candidate"),
            evidence_record_ids=(ResolutionEvidenceRecordId("evidence:missing"),),
            confidence_record_id=ResolutionConfidenceRecordId("confidence:missing"),
            created_at=fixed_now(),
        )

        report = self.validator.validate_graph(
            **self._graph_with(
                graph,
            entity_alias_records=(*graph["entity_alias_records"], bad_alias),
            candidate_match_records=(*graph["candidate_match_records"], bad_match),
            )
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("alias.entity_reference_invalid", codes)
        self.assertIn("alias.observed_name_reference_invalid", codes)
        self.assertIn("candidate_match.source_reference_invalid", codes)
        self.assertIn("candidate_match.candidate_reference_invalid", codes)
        self.assertIn("candidate_match.entity_reference_invalid", codes)
        self.assertIn("candidate_match.evidence_reference_invalid", codes)
        self.assertIn("candidate_match.confidence_reference_invalid", codes)

    def test_confirmed_match_requires_confirmed_decision_and_entity(self) -> None:
        graph = self._build_confirmed_graph()
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:ambiguous"),
            resolution_status=ResolutionStatus.AMBIGUOUS,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=graph["candidate_match_sets"][0].candidate_match_set_id,
            decision_scope_observed_record_ids=graph["confirmed_match_records"][0].observed_record_ids,
            rationale=Rationale("Not actually confirmed."),
            evidence_record_ids=graph["resolution_decision_records"][0].evidence_record_ids,
            confidence_record_id=graph["resolution_decision_records"][0].confidence_record_id,
            created_at=fixed_now(),
        )
        confirmed = ConfirmedMatchRecord(
            resolution_decision_record_id=decision.resolution_decision_record_id,
            entity_id=EntityId("entity:missing"),
            observed_record_ids=graph["confirmed_match_records"][0].observed_record_ids,
            created_at=fixed_now(),
        )

        report = self.validator.validate_graph(
            **self._graph_with(
                graph,
            resolution_decision_records=(*graph["resolution_decision_records"], decision),
            confirmed_match_records=(confirmed,),
            )
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("confirmed_match.decision_status_mismatch", codes)
        self.assertIn("confirmed_match.entity_reference_invalid", codes)

    def test_merge_event_decision_status_mismatch_fails(self) -> None:
        graph = self._build_confirmed_graph()
        merge_event = MergeEventRecord(
            merge_event_record_id=MergeEventRecordId("merge:broken"),
            merged_entity_ids=(EntityId("entity:utility:1"), EntityId("entity:utility:2")),
            surviving_entity_id=EntityId("entity:utility:1"),
            resolution_decision_record_id=graph["resolution_decision_records"][0].resolution_decision_record_id,
            rationale=Rationale("Broken merge"),
            event_type=HistoricalEventType.MERGE,
            effective_from=fixed_now(),
            created_at=fixed_now(),
        )

        report = self.validator.validate_graph(
            **self._graph_with(
                graph,
            canonical_entities=(*graph["canonical_entities"], self._entity("entity:utility:2", "Utility Two")),
            merge_event_records=(merge_event,),
            )
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("merge_event.decision_status_mismatch", codes)

    def test_history_event_entity_mismatch_fails(self) -> None:
        graph = self._build_confirmed_graph()
        split_decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:split"),
            resolution_status=ResolutionStatus.SPLIT,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=None,
            decision_scope_observed_record_ids=(ObservedRecordId("observed:3"),),
            rationale=Rationale("Split decision"),
            evidence_record_ids=(),
            confidence_record_id=None,
            created_at=fixed_now(),
        )
        split_event = SplitEventRecord(
            split_event_record_id=SplitEventRecordId("split:1"),
            source_entity_id=EntityId("entity:utility:1"),
            successor_entity_ids=(EntityId("entity:utility:2"), EntityId("entity:utility:3")),
            resolution_decision_record_id=split_decision.resolution_decision_record_id,
            rationale=Rationale("Split entity"),
            event_type=HistoricalEventType.SPLIT,
            effective_from=fixed_now(),
            created_at=fixed_now(),
        )
        history = EntityHistoryRecord(
            entity_history_record_id=EntityHistoryRecordId("history:broken"),
            entity_id=EntityId("entity:utility:4"),
            history_status=HistoryStatus.SPLIT,
            resolution_decision_record_id=split_decision.resolution_decision_record_id,
            merge_event_record_id=None,
            split_event_record_id=split_event.split_event_record_id,
            summary=EntityHistorySummary("Broken split history"),
            effective_from=fixed_now(),
            effective_to=None,
            created_at=fixed_now(),
        )

        report = self.validator.validate_graph(
            **self._graph_with(
                graph,
            canonical_entities=(
                *graph["canonical_entities"],
                self._entity("entity:utility:2", "Utility Two"),
                self._entity("entity:utility:3", "Utility Three"),
                self._entity("entity:utility:4", "Utility Four"),
            ),
            resolution_decision_records=(*graph["resolution_decision_records"], split_decision),
            split_event_records=(split_event,),
            entity_history_records=(history,),
            )
        )

        self.assertEqual(report.outcome, ValidationOutcome.FAIL)
        codes = {item.code for item in report.violations}
        self.assertIn("history.event_entity_mismatch", codes)

    def _build_confirmed_graph(self) -> dict[str, tuple]:
        name_1 = ObservedNameRecord(
            observed_name_record_id=ObservedNameRecordId("name:1"),
            observed_record_id=ObservedRecordId("observed:1"),
            observed_label=ObservedLabel("Con Edison"),
            is_primary=True,
            source_normalized_field_ref=NormalizedFieldRef("normalized-field:1"),
            created_at=fixed_now(),
        )
        name_2 = ObservedNameRecord(
            observed_name_record_id=ObservedNameRecordId("name:2"),
            observed_record_id=ObservedRecordId("observed:2"),
            observed_label=ObservedLabel("Consolidated Edison"),
            is_primary=True,
            source_normalized_field_ref=NormalizedFieldRef("normalized-field:2"),
            created_at=fixed_now(),
        )
        observed_1 = ObservedRecord(
            observed_record_id=ObservedRecordId("observed:1"),
            entity_type=EntityType.UTILITY,
            source_provenance=SourceProvenanceRefs(
                normalized_record_ref=NormalizedRecordRef("normalized-record:1"),
                normalized_field_refs=(NormalizedFieldRef("normalized-field:1"),),
            ),
            primary_observed_name_record_id=name_1.observed_name_record_id,
            observed_name_record_ids=(name_1.observed_name_record_id,),
            created_at=fixed_now(),
        )
        observed_2 = ObservedRecord(
            observed_record_id=ObservedRecordId("observed:2"),
            entity_type=EntityType.UTILITY,
            source_provenance=SourceProvenanceRefs(
                normalized_record_ref=NormalizedRecordRef("normalized-record:2"),
                normalized_field_refs=(NormalizedFieldRef("normalized-field:2"),),
            ),
            primary_observed_name_record_id=name_2.observed_name_record_id,
            observed_name_record_ids=(name_2.observed_name_record_id,),
            created_at=fixed_now(),
        )
        entity = self._entity("entity:utility:1", "Consolidated Edison")
        alias = EntityAliasRecord(
            entity_alias_record_id=EntityAliasRecordId("alias:1"),
            entity_id=entity.entity_id,
            alias_label=entity_alias("Con Edison"),
            source_observed_name_record_id=name_1.observed_name_record_id,
            created_at=fixed_now(),
        )
        evidence = ResolutionEvidenceRecord(
            resolution_evidence_record_id=ResolutionEvidenceRecordId("evidence:1"),
            evidence_basis_type=EvidenceBasisType.GOVERNED_ALIAS,
            source_provenance=observed_1.source_provenance,
            supports_match=True,
            evidence_summary=EvidenceSummary("Governed alias plus matching utility context."),
            created_at=fixed_now(),
        )
        confidence = ResolutionConfidenceRecord(
            resolution_confidence_record_id=ResolutionConfidenceRecordId("confidence:1"),
            confidence_status=ConfidenceStatus.HIGH,
            confidence_method=ConfidenceMethod("rule_based_exact_alias"),
            confidence_value=ConfidenceValue("0.97"),
            rationale=Rationale("Alias and context are governed and consistent."),
            created_at=fixed_now(),
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
            rationale=Rationale("Observed names and context support the same utility identity."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:1"),
            resolution_status=ResolutionStatus.CONFIRMED,
            resolution_mode=ResolutionMode.HUMAN_CONFIRMED,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            decision_scope_observed_record_ids=(observed_1.observed_record_id, observed_2.observed_record_id),
            rationale=Rationale("Identity confirmed under explicit alias and context rules."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        confirmed = ConfirmedMatchRecord(
            resolution_decision_record_id=decision.resolution_decision_record_id,
            entity_id=entity.entity_id,
            observed_record_ids=(observed_1.observed_record_id, observed_2.observed_record_id),
            created_at=fixed_now(),
        )
        history = EntityHistoryRecord(
            entity_history_record_id=EntityHistoryRecordId("history:1"),
            entity_id=entity.entity_id,
            history_status=HistoryStatus.ACTIVE,
            resolution_decision_record_id=decision.resolution_decision_record_id,
            merge_event_record_id=None,
            split_event_record_id=None,
            summary=EntityHistorySummary("Active canonical utility identity."),
            effective_from=fixed_now(),
            effective_to=None,
            created_at=fixed_now(),
        )
        return {
            "observed_records": (observed_1, observed_2),
            "observed_name_records": (name_1, name_2),
            "canonical_entities": (entity,),
            "entity_alias_records": (alias,),
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

    def _build_ambiguous_graph(self) -> dict[str, tuple]:
        name_1 = ObservedNameRecord(
            observed_name_record_id=ObservedNameRecordId("name:a1"),
            observed_record_id=ObservedRecordId("observed:a1"),
            observed_label=ObservedLabel("Plant 2"),
            is_primary=True,
            source_normalized_field_ref=NormalizedFieldRef("normalized-field:a1"),
            created_at=fixed_now(),
        )
        name_2 = ObservedNameRecord(
            observed_name_record_id=ObservedNameRecordId("name:a2"),
            observed_record_id=ObservedRecordId("observed:a2"),
            observed_label=ObservedLabel("Plant 2"),
            is_primary=True,
            source_normalized_field_ref=NormalizedFieldRef("normalized-field:a2"),
            created_at=fixed_now(),
        )
        observed_1 = ObservedRecord(
            observed_record_id=ObservedRecordId("observed:a1"),
            entity_type=EntityType.PLANT,
            source_provenance=SourceProvenanceRefs(
                normalized_record_ref=NormalizedRecordRef("normalized-record:a1"),
                normalized_field_refs=(NormalizedFieldRef("normalized-field:a1"),),
            ),
            primary_observed_name_record_id=name_1.observed_name_record_id,
            observed_name_record_ids=(name_1.observed_name_record_id,),
            created_at=fixed_now(),
        )
        observed_2 = ObservedRecord(
            observed_record_id=ObservedRecordId("observed:a2"),
            entity_type=EntityType.PLANT,
            source_provenance=SourceProvenanceRefs(
                normalized_record_ref=NormalizedRecordRef("normalized-record:a2"),
                normalized_field_refs=(NormalizedFieldRef("normalized-field:a2"),),
            ),
            primary_observed_name_record_id=name_2.observed_name_record_id,
            observed_name_record_ids=(name_2.observed_name_record_id,),
            created_at=fixed_now(),
        )
        evidence = ResolutionEvidenceRecord(
            resolution_evidence_record_id=ResolutionEvidenceRecordId("evidence:a1"),
            evidence_basis_type=EvidenceBasisType.NORMALIZED_NAME,
            source_provenance=observed_1.source_provenance,
            supports_match=True,
            evidence_summary=EvidenceSummary("Name similarity only."),
            created_at=fixed_now(),
        )
        confidence = ResolutionConfidenceRecord(
            resolution_confidence_record_id=ResolutionConfidenceRecordId("confidence:a1"),
            confidence_status=ConfidenceStatus.INSUFFICIENT,
            confidence_method=ConfidenceMethod("label_similarity_only"),
            confidence_value=None,
            rationale=Rationale("Textual similarity alone is insufficient."),
            created_at=fixed_now(),
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
            rationale=Rationale("Candidate remains open under superficial label similarity."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        decision = ResolutionDecisionRecord(
            resolution_decision_record_id=ResolutionDecisionRecordId("decision:a1"),
            resolution_status=ResolutionStatus.AMBIGUOUS,
            resolution_mode=ResolutionMode.CARRIED_FORWARD,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            decision_scope_observed_record_ids=(observed_1.observed_record_id, observed_2.observed_record_id),
            rationale=Rationale("Insufficient context to confirm or reject."),
            evidence_record_ids=(evidence.resolution_evidence_record_id,),
            confidence_record_id=confidence.resolution_confidence_record_id,
            created_at=fixed_now(),
        )
        ambiguous = AmbiguousResolutionRecord(
            resolution_decision_record_id=decision.resolution_decision_record_id,
            candidate_match_set_id=candidate_set.candidate_match_set_id,
            observed_record_ids=(observed_1.observed_record_id, observed_2.observed_record_id),
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

    def _entity(self, entity_id: str, canonical_name: str) -> CanonicalEntity:
        return CanonicalEntity(
            entity_id=EntityId(entity_id),
            entity_type=EntityType.UTILITY,
            canonical_name=CanonicalName(canonical_name),
            entity_status=CanonicalEntityStatus.ACTIVE,
            created_at=fixed_now(),
            effective_from=fixed_now(),
        )

    def _graph_with(self, graph: dict[str, tuple], **overrides: tuple) -> dict[str, tuple]:
        merged = dict(graph)
        merged.update(overrides)
        return merged


def entity_alias(value: str):
    from entity_identity_resolution_engine.domain import AliasLabel

    return AliasLabel(value)


if __name__ == "__main__":
    unittest.main()
