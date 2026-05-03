"""Adapter for motor_020 — Propagation / Belief Revision Engine.

When source changes (motor_009), quality degradation (motor_007), or other
upstream shifts occur, propagate the impact through the active claim graph and
the visible report chain:

source / quality change -> affected inference case -> affected output blocks ->
affected report sections -> publication consequence

This motor does not decide truth. It decides what must be re-scored, degraded,
held, blocked, or reviewed for upgrade before downstream publication remains
admissible.
"""
from __future__ import annotations

import re
from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter

# Impact type definitions
_IMPACT_NEW_EVIDENCE = "new_evidence"
_IMPACT_SOURCE_CHANGED = "source_changed"
_IMPACT_SOURCE_STALE = "source_stale"
_IMPACT_SOURCE_DISAPPEARED = "source_disappeared"
_IMPACT_QUALITY_DEGRADED = "quality_degraded"

# Recommended action thresholds
_URGENCY_BLOCK = 0.90
_URGENCY_DOWNGRADE = 0.75
_URGENCY_RESCORE = 0.55
_URGENCY_UPGRADE_CANDIDATE = 0.40


def _recommended_action(impact_type: str, fitness_status: str | None, urgency: float) -> str:
    """Derive recommended_action from impact type, fitness, and urgency score."""
    if impact_type == _IMPACT_QUALITY_DEGRADED:
        if fitness_status == "unfit":
            return "block"
        return "downgrade"
    if impact_type == _IMPACT_SOURCE_DISAPPEARED:
        if urgency >= _URGENCY_DOWNGRADE:
            return "block"
        return "downgrade"
    if impact_type == _IMPACT_SOURCE_STALE:
        if urgency >= _URGENCY_BLOCK:
            return "block"
        if urgency >= _URGENCY_RESCORE:
            return "downgrade"
        return "re_score"
    if impact_type == _IMPACT_SOURCE_CHANGED:
        if urgency >= _URGENCY_BLOCK:
            return "block"
        if urgency >= _URGENCY_DOWNGRADE:
            return "downgrade"
        return "re_score"
    if impact_type == _IMPACT_NEW_EVIDENCE:
        if urgency >= _URGENCY_UPGRADE_CANDIDATE:
            return "upgrade_candidate"
        return "re_score"
    return "re_score"


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _split_tokens(value: Any) -> set[str]:
    text = _normalize_text(value)
    return {token for token in re.split(r"[^a-z0-9]+|_+", text) if token}


def _identifier_aliases(value: Any) -> set[str]:
    text = _normalize_text(value)
    if not text:
        return set()
    aliases = {text}
    if "::" in text:
        aliases.add(text.split("::", 1)[0])
    if "." in text:
        aliases.add(text.split(".", 1)[0])
    return {alias for alias in aliases if alias}


def _identifier_hint_tokens(value: Any) -> set[str]:
    return {token for token in _split_tokens(value) if token}


def _case_trace_atoms(case: dict) -> set[str]:
    atoms: set[str] = set()
    for trace in case.get("base_support_traces", []) or []:
        atoms |= _identifier_aliases(trace)
    return atoms


def _case_text_tokens(case: dict) -> set[str]:
    tokens: set[str] = set()
    for value in [
        case.get("conditional_statement", ""),
        case.get("validation_requirement", ""),
        *list(case.get("dependency_assumptions", []) or []),
        *list(case.get("base_support_traces", []) or []),
    ]:
        tokens |= _split_tokens(value)
    return tokens


def _flatten_value_tokens(value: Any) -> set[str]:
    if isinstance(value, dict):
        tokens: set[str] = set()
        for inner in value.values():
            tokens |= _flatten_value_tokens(inner)
        return tokens
    if isinstance(value, list):
        tokens: set[str] = set()
        for inner in value:
            tokens |= _flatten_value_tokens(inner)
        return tokens
    return _split_tokens(value)


def _versioned_context_tokens(versioned_objects: list[dict[str, Any]]) -> set[str]:
    tokens: set[str] = set()
    for obj in versioned_objects:
        tokens |= _flatten_value_tokens(obj)
    return tokens


def _source_id_in_traces(source_id: str, case: dict) -> bool:
    """Check whether a source_id or its source family appears in a case trace."""
    aliases = _identifier_aliases(source_id)
    trace_atoms = _case_trace_atoms(case)
    return bool(aliases & trace_atoms)


def _entity_id_in_traces(entity_id: str, case: dict) -> bool:
    """Check whether an entity_id or entity dimension appears in a case's traces."""
    aliases = _identifier_aliases(entity_id)
    return bool(aliases & (_case_trace_atoms(case) | _case_text_tokens(case)))


def _source_fallback_relevance(source_id: str, case: dict, versioned_tokens: set[str]) -> int:
    source_tokens = {token for token in _identifier_hint_tokens(source_id) if len(token) >= 3}
    if not source_tokens:
        return 0
    case_tokens = _case_text_tokens(case)
    direct_overlap = len(source_tokens & case_tokens)
    lineage_overlap = len(source_tokens & versioned_tokens)
    urgency = float(case.get("validation_urgency_score", 0.0) or 0.0)
    if direct_overlap >= 2:
        return direct_overlap + lineage_overlap
    if direct_overlap >= 1 and (lineage_overlap >= 1 or urgency >= 0.85):
        return direct_overlap + lineage_overlap
    return 0


def _dependency_type(case: dict) -> str:
    family = case.get("claim_family", "")
    if family == "conflict":
        return "blocking_conflict_dependency"
    if family == "tension":
        return "bounded_inference_dependency"
    if family == "opportunity":
        return "conditional_action_dependency"
    return "evidence_support_dependency"


def _scope_impact(case: dict) -> str:
    family = case.get("claim_family", "")
    if family == "conflict":
        return "decision_blocking_scope"
    if family == "tension":
        return "multi_section_reading_scope"
    if family == "opportunity":
        return "conditional_decision_scope"
    return "case_local_scope"


def _claim_lifecycle_state(impact_type: str, action: str) -> str:
    if action == "block":
        return "frozen_pending_resolution"
    if action == "downgrade":
        return "degraded_pending_validation"
    if action == "upgrade_candidate":
        return "candidate_for_promotion"
    if impact_type == _IMPACT_NEW_EVIDENCE:
        return "under_review_with_new_evidence"
    return "under_review"


def _publication_consequence(action: str, case: dict) -> str:
    family = case.get("claim_family", "")
    if action == "block":
        return "freeze_publication"
    if action == "downgrade" and family in {"conflict", "tension"}:
        return "hold_for_validation"
    if action == "downgrade":
        return "publish_with_degradation"
    if action == "upgrade_candidate":
        return "review_for_upgrade"
    return "re_score_required"


def _persistent_contradiction_mode(case: dict, action: str) -> str:
    family = case.get("claim_family", "")
    if family == "conflict" and action in {"block", "downgrade"}:
        return "freeze_publication"
    if family == "tension" and action in {"block", "downgrade"}:
        return "escalate_validation"
    return "coexist"


def _affected_blocks_sections(
    case_id: str,
    traceability_register: dict,
    report_traceability: dict,
) -> tuple[list[str], list[str]]:
    block_traces = traceability_register.get("block_traces", [])
    section_traces = report_traceability.get("section_traces", [])
    affected_blocks = [
        block.get("block_id", "")
        for block in block_traces
        if case_id in block.get("upstream_traces", []) or "all_inference_records" in block.get("upstream_traces", [])
    ]
    affected_sections = [
        section.get("section_id", "")
        for section in section_traces
        if case_id in section.get("upstream_traces", [])
        or any(block_id in section.get("block_ids", []) for block_id in affected_blocks)
    ]
    return sorted(set(filter(None, affected_blocks))), sorted(set(filter(None, affected_sections)))


class Motor020Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_020"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_002", "motor_007", "motor_009", "motor_013", "motor_015", "motor_016"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()

        # Read upstream inputs
        change_events = inputs.get("motor_009", {}).get("change_detection_events", [])
        evaluated_entities = inputs.get("motor_007", {}).get("evaluated_entities", [])
        inference_cases = inputs.get("motor_013", {}).get("inference_case_register", [])
        versioned_objects = inputs.get("motor_002", {}).get("versioned_objects", [])
        traceability_register = inputs.get("motor_015", {}).get("traceability_register", {})
        report_traceability = (
            inputs.get("motor_016", {}).get("report_package", {}).get("report_traceability", {})
        )
        versioned_context_tokens = _versioned_context_tokens(versioned_objects)

        # Build propagation map: source_id → list of affected case_ids
        propagation_map: dict[str, list[str]] = {}
        re_evaluation_register: list[dict] = []
        belief_revision_register: list[dict] = []
        publication_consequence_register: list[dict] = []
        dependency_edge_register: list[dict] = []
        events_processed: list[dict] = []

        # Process change_detection_events from motor_009
        for event in change_events:
            source_id = event.get("source_id", "")
            change_type = event.get("change_type", "")
            content_hash = event.get("content_hash", "")

            if change_type not in ("new", "updated", "stale", "disappeared"):
                continue

            # Determine impact type
            if change_type == "new":
                impact_type = _IMPACT_NEW_EVIDENCE
            elif change_type == "updated":
                impact_type = _IMPACT_SOURCE_CHANGED
            elif change_type == "stale":
                impact_type = _IMPACT_SOURCE_STALE
            else:
                impact_type = _IMPACT_SOURCE_DISAPPEARED

            # Find affected cases: any case whose traces reference this source
            affected_cases: list[str] = []
            for case in inference_cases:
                if _source_id_in_traces(source_id, case):
                    affected_cases.append(case.get("case_id", ""))

            if not affected_cases:
                relevance_scored_cases = []
                for case in inference_cases:
                    score = _source_fallback_relevance(source_id, case, versioned_context_tokens)
                    if score > 0:
                        relevance_scored_cases.append((score, case.get("case_id", "")))
                relevance_scored_cases.sort(key=lambda item: (-item[0], item[1]))
                affected_cases = [case_id for _, case_id in relevance_scored_cases]

            if affected_cases:
                propagation_map[source_id] = affected_cases

                for case_id in affected_cases:
                    # Find urgency from case
                    case_obj = next((c for c in inference_cases if c.get("case_id") == case_id), {})
                    urgency = case_obj.get("validation_urgency_score", 0.60)

                    action = _recommended_action(impact_type, None, urgency)
                    affected_blocks, affected_sections = _affected_blocks_sections(
                        case_id,
                        traceability_register,
                        report_traceability,
                    )
                    publication_consequence = _publication_consequence(action, case_obj)
                    affected_outputs = [
                        "decision_core",
                        "validation_queue",
                    ]
                    if affected_blocks:
                        affected_outputs.append("output_block_register")
                    if affected_sections:
                        affected_outputs.extend(["report_package", "pdf_output"])
                    re_evaluation_register.append({
                        "case_id": case_id,
                        "trigger_event": {
                            "source_id": source_id,
                            "change_type": change_type,
                            "content_hash": content_hash,
                            "detected_at": event.get("detected_at", produced_at),
                        },
                        "impact_type": impact_type,
                        "recommended_action": action,
                        "urgency_at_propagation": urgency,
                        "propagation_reason": (
                            f"Source {source_id} ({change_type}) referenced in case traces."
                            if _source_id_in_traces(source_id, case_obj)
                            else f"Source {source_id} ({change_type}) matched case relevance heuristics without direct trace identity."
                        ),
                        "produced_by_motor": "motor_020",
                    })
                    dependency_edge_register.append({
                        "case_id": case_id,
                        "dependency_type": _dependency_type(case_obj),
                        "affected_block_ids": affected_blocks,
                        "affected_section_ids": affected_sections,
                        "affected_outputs": sorted(set(affected_outputs)),
                    })
                    belief_revision_register.append({
                        "case_id": case_id,
                        "case_name": case_obj.get("case_name", ""),
                        "trigger_type": (
                            "evidence_arrived"
                            if impact_type == _IMPACT_NEW_EVIDENCE
                            else "source_stale"
                            if impact_type == _IMPACT_SOURCE_STALE
                            else "source_disappeared"
                            if impact_type == _IMPACT_SOURCE_DISAPPEARED
                            else "source_changed"
                        ),
                        "impact_type": impact_type,
                        "dependency_type": _dependency_type(case_obj),
                        "scope_impact": _scope_impact(case_obj),
                        "recommended_action": action,
                        "claim_lifecycle_state": _claim_lifecycle_state(impact_type, action),
                        "publication_consequence": publication_consequence,
                        "persistent_contradiction_mode": _persistent_contradiction_mode(case_obj, action),
                        "affected_outputs": sorted(set(affected_outputs)),
                        "affected_block_ids": affected_blocks,
                        "affected_section_ids": affected_sections,
                        "causal_statement": (
                            f"Upstream source event {change_type} on {source_id} changes the admissibility of "
                            f"case {case_id} and its downstream rendered sections."
                        ),
                    })
                    publication_consequence_register.append({
                        "case_id": case_id,
                        "publication_consequence": publication_consequence,
                        "affected_outputs": sorted(set(affected_outputs)),
                        "affected_section_ids": affected_sections,
                    })

            events_processed.append({
                "event_type": "source_change",
                "source_id": source_id,
                "change_type": change_type,
                "affected_cases_count": len(affected_cases),
                "matching_mode": "direct_trace" if affected_cases and any(
                    _source_id_in_traces(source_id, c) for c in inference_cases if c.get("case_id", "") in affected_cases
                ) else "relevance_scoped" if affected_cases else "none",
                "processed_at": produced_at,
            })

        # Process quality-degraded entities from motor_007
        unfit_entities = [
            e for e in evaluated_entities
            if e.get("fitness_status") in ("unfit", "marginal")
        ]

        for entity in unfit_entities:
            entity_id = entity.get("entity_id", "")
            fitness_status = entity.get("fitness_status", "unfit")
            fitness_score = entity.get("fitness_score", 0.0)

            # Find affected cases: any case whose traces or statement reference this entity
            affected_cases: list[str] = []
            for case in inference_cases:
                if entity_id and _entity_id_in_traces(entity_id, case):
                    affected_cases.append(case.get("case_id", ""))

            # For unfit entities with no specific match, flag high-urgency cases conservatively
            if not affected_cases and fitness_status == "unfit":
                affected_cases = [
                    c.get("case_id", "") for c in inference_cases
                    if c.get("validation_urgency_score", 0) >= 0.75
                ]

            if affected_cases:
                # Add to propagation map
                key = f"entity:{entity_id}" if entity_id else f"unfit_entity_score_{fitness_score}"
                propagation_map[key] = list(set(propagation_map.get(key, []) + affected_cases))

                for case_id in affected_cases:
                    action = _recommended_action(_IMPACT_QUALITY_DEGRADED, fitness_status, fitness_score)
                    case_obj = next((c for c in inference_cases if c.get("case_id") == case_id), {})
                    affected_blocks, affected_sections = _affected_blocks_sections(
                        case_id,
                        traceability_register,
                        report_traceability,
                    )
                    publication_consequence = _publication_consequence(action, case_obj)
                    affected_outputs = [
                        "decision_core",
                        "validation_queue",
                    ]
                    if affected_blocks:
                        affected_outputs.append("output_block_register")
                    if affected_sections:
                        affected_outputs.extend(["report_package", "pdf_output"])
                    re_evaluation_register.append({
                        "case_id": case_id,
                        "trigger_event": {
                            "entity_id": entity_id,
                            "fitness_status": fitness_status,
                            "fitness_score": fitness_score,
                            "quality_checks": entity.get("quality_checks", {}),
                        },
                        "impact_type": _IMPACT_QUALITY_DEGRADED,
                        "recommended_action": action,
                        "urgency_at_propagation": 1.0 - fitness_score,
                        "propagation_reason": (
                            f"Entity {entity_id} has fitness_status={fitness_status} "
                            f"(score={fitness_score:.2f}), degrading analytical support."
                        ),
                        "produced_by_motor": "motor_020",
                    })
                    dependency_edge_register.append({
                        "case_id": case_id,
                        "dependency_type": _dependency_type(case_obj),
                        "affected_block_ids": affected_blocks,
                        "affected_section_ids": affected_sections,
                        "affected_outputs": sorted(set(affected_outputs)),
                    })
                    belief_revision_register.append({
                        "case_id": case_id,
                        "case_name": case_obj.get("case_name", ""),
                        "trigger_type": "quality_degraded",
                        "impact_type": _IMPACT_QUALITY_DEGRADED,
                        "dependency_type": _dependency_type(case_obj),
                        "scope_impact": _scope_impact(case_obj),
                        "recommended_action": action,
                        "claim_lifecycle_state": _claim_lifecycle_state(_IMPACT_QUALITY_DEGRADED, action),
                        "publication_consequence": publication_consequence,
                        "persistent_contradiction_mode": _persistent_contradiction_mode(case_obj, action),
                        "affected_outputs": sorted(set(affected_outputs)),
                        "affected_block_ids": affected_blocks,
                        "affected_section_ids": affected_sections,
                        "causal_statement": (
                            f"Quality degradation on entity {entity_id} weakens the evidentiary basis of case {case_id} "
                            f"and requires downstream review."
                        ),
                    })
                    publication_consequence_register.append({
                        "case_id": case_id,
                        "publication_consequence": publication_consequence,
                        "affected_outputs": sorted(set(affected_outputs)),
                        "affected_section_ids": affected_sections,
                    })

            events_processed.append({
                "event_type": "quality_degradation",
                "entity_id": entity_id,
                "fitness_status": fitness_status,
                "fitness_score": fitness_score,
                "affected_cases_count": len(affected_cases),
                "processed_at": produced_at,
            })

        # De-duplicate re_evaluation_register: keep highest urgency per case_id
        deduped: dict[str, dict] = {}
        for entry in re_evaluation_register:
            cid = entry["case_id"]
            if cid not in deduped:
                deduped[cid] = entry
            else:
                if entry.get("urgency_at_propagation", 0) > deduped[cid].get("urgency_at_propagation", 0):
                    deduped[cid] = entry

        final_register = list(deduped.values())
        deduped_belief_revisions: dict[str, dict] = {}
        for entry in belief_revision_register:
            cid = entry["case_id"]
            if cid not in deduped_belief_revisions:
                deduped_belief_revisions[cid] = entry
                continue
            existing = deduped_belief_revisions[cid]
            priority = {
                "freeze_publication": 4,
                "hold_for_validation": 3,
                "publish_with_degradation": 2,
                "re_score_required": 1,
                "review_for_upgrade": 0,
            }
            if priority.get(entry.get("publication_consequence", ""), 0) > priority.get(existing.get("publication_consequence", ""), 0):
                deduped_belief_revisions[cid] = entry
        publication_priority = {
            "freeze_publication": 4,
            "hold_for_validation": 3,
            "publish_with_degradation": 2,
            "re_score_required": 1,
            "review_for_upgrade": 0,
        }
        consequence_by_output: dict[str, dict] = {}
        for entry in publication_consequence_register:
            for output_id in entry.get("affected_outputs", []):
                current = consequence_by_output.get(output_id)
                candidate = {
                    "output_id": output_id,
                    "publication_consequence": entry.get("publication_consequence", "re_score_required"),
                    "case_id": entry.get("case_id", ""),
                    "affected_section_ids": entry.get("affected_section_ids", []),
                }
                if current is None or publication_priority.get(candidate["publication_consequence"], 0) > publication_priority.get(current["publication_consequence"], 0):
                    consequence_by_output[output_id] = candidate

        # Summarize action distribution
        action_counts: dict[str, int] = {}
        for entry in final_register:
            action = entry.get("recommended_action", "re_score")
            action_counts[action] = action_counts.get(action, 0) + 1

        update_trigger_taxonomy = sorted({
            entry.get("trigger_type", "")
            for entry in deduped_belief_revisions.values()
            if entry.get("trigger_type")
        })
        freeze_publication_recommended = any(
            entry.get("publication_consequence") == "freeze_publication"
            for entry in consequence_by_output.values()
        )

        return {
            "propagation_map": propagation_map,
            "re_evaluation_register": final_register,
            "belief_revision_register": list(deduped_belief_revisions.values()),
            "dependency_edge_register": dependency_edge_register,
            "publication_consequence_register": list(consequence_by_output.values()),
            "update_trigger_taxonomy": update_trigger_taxonomy,
            "freeze_publication_recommended": freeze_publication_recommended,
            "affected_case_count": len(final_register),
            "propagation_events": events_processed,
            "action_distribution": action_counts,
            "total_change_events_processed": len([e for e in events_processed if e["event_type"] == "source_change"]),
            "total_quality_events_processed": len([e for e in events_processed if e["event_type"] == "quality_degradation"]),
            "unfit_entity_count": len(unfit_entities),
            "produced_at": produced_at,
        }
