from __future__ import annotations

from datetime import datetime

from ..domain.enums import ReplayabilityStatus
from ..domain.records import EvaluationReplayManifest
from ..domain.value_objects import EvaluatorVersion, EvaluationReplayManifestId
from .inputs import EvaluableObjectSnapshot
from .results import stable_id



def build_replay_manifest(
    *,
    evaluation_run_record_id,
    evaluation_request_record,
    evaluation_scope_record,
    subject: EvaluableObjectSnapshot,
    validation_rule_record_ids,
    evaluator_version: str,
    contract_version_ref,
    created_at: datetime,
) -> EvaluationReplayManifest:
    replayability_status = _derive_replayability_status(subject)
    return EvaluationReplayManifest(
        evaluation_replay_manifest_id=EvaluationReplayManifestId(
            stable_id(
                "evaluation_replay_manifest",
                evaluation_run_record_id.value,
                evaluation_request_record.evaluation_request_record_id.value,
                evaluation_scope_record.evaluation_scope_record_id.value,
                subject.evaluated_object_ref.value,
                subject.evaluated_object_version_ref.value if subject.evaluated_object_version_ref is not None else "noversion",
                *(item.value for item in validation_rule_record_ids),
            )
        ),
        evaluation_run_record_id=evaluation_run_record_id,
        evaluation_request_record_id=evaluation_request_record.evaluation_request_record_id,
        evaluation_scope_record_id=evaluation_scope_record.evaluation_scope_record_id,
        evaluated_object_refs=(subject.evaluated_object_ref,),
        evaluated_object_version_refs=(subject.evaluated_object_version_ref,) if subject.evaluated_object_version_ref is not None else (),
        validation_rule_record_ids=tuple(validation_rule_record_ids),
        contract_version_ref=contract_version_ref,
        evaluator_version=EvaluatorVersion(evaluator_version),
        replayability_status=replayability_status,
        created_at=created_at,
    )



def _derive_replayability_status(subject: EvaluableObjectSnapshot) -> ReplayabilityStatus:
    if subject.evaluated_object_version_ref is None:
        return ReplayabilityStatus.PARTIALLY_REPLAYABLE
    return ReplayabilityStatus.REPLAYABLE
