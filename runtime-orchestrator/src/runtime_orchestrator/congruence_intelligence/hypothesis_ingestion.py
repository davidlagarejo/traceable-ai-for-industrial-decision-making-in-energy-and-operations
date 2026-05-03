from __future__ import annotations

from typing import Any

from .schemas import text

_METADATA_GAP_BLOCKED_CLAIMS = ["claim_governance_metadata_missing"]


def _stop_map(stop_condition_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("path_id")): row
        for row in list(stop_condition_register or [])
        if text(row.get("path_id"))
    }


def _next_search_map(next_best_search_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    return {
        text(row.get("need_id")): row
        for row in list(next_best_search_register or [])
        if text(row.get("need_id"))
    }


def _question_ids(question: dict[str, Any]) -> list[str]:
    return [
        text(item)
        for item in list(question.get("linked_need_ids", []) or []) + list(question.get("linked_pack_names", []) or [])
        if text(item)
    ]


def _evidence_needed(question: dict[str, Any], stop_by_path: dict[str, dict[str, Any]]) -> list[str]:
    items: list[str] = []
    for path_id in _question_ids(question):
        row = stop_by_path.get(path_id, {})
        minimum = text(row.get("minimum_sufficient_evidence"))
        if minimum and minimum not in items:
            items.append(minimum)
    return items


def _next_public_search(question: dict[str, Any], next_by_need: dict[str, dict[str, Any]]) -> list[str]:
    items: list[str] = []
    for need_id in list(question.get("linked_need_ids", []) or []):
        row = next_by_need.get(text(need_id), {})
        target = text(row.get("next_search_target"))
        if target and target not in items:
            items.append(target)
    return items


def _question_strings(question: dict[str, Any], key: str) -> list[str]:
    return [text(item) for item in list(question.get(key, []) or []) if text(item)]


def _structured_hypotheses(question: dict[str, Any]) -> list[dict[str, str]]:
    discriminator = text(question.get("hypothesis_it_discriminates"))
    rows: list[dict[str, str]] = []
    seen: set[tuple[str, str]] = set()
    for relation, key in (
        ("supports", "supports_hypotheses"),
        ("falsifies", "falsifies_hypotheses"),
    ):
        for hypothesis in _question_strings(question, key):
            marker = (relation, hypothesis)
            if marker in seen:
                continue
            seen.add(marker)
            rows.append(
                {
                    "relation": relation,
                    "hypothesis": hypothesis,
                    "discriminator": discriminator,
                }
            )
    if rows:
        return rows
    for hypothesis in _question_strings(question, "rival_hypotheses"):
        marker = ("rival", hypothesis)
        if marker in seen:
            continue
        seen.add(marker)
        rows.append(
            {
                "relation": "rival",
                "hypothesis": hypothesis,
                "discriminator": discriminator,
            }
        )
    return rows


def _legacy_blocked_claims(question_id: str, hypothesis_text: str) -> list[str]:
    lower_id = question_id.lower()
    lower_hypothesis = hypothesis_text.lower()
    if "control_boundary" in lower_id:
        return ["owner_capturable_roi", "owner_capturable_retrofit"]
    if "charging" in lower_id or "tariff" in lower_hypothesis or "demand" in lower_hypothesis:
        return ["tariff_blind_cost_claim", "generic_efficiency_retrofit"]
    if "throughput" in lower_id or "dock" in lower_id or "subtype" in lower_id or "cold_chain" in lower_id:
        return ["generic_eui_interpretation", "peer_superiority"]
    if "maintenance" in lower_id:
        return ["maintenance_maturity_claim", "downtime_economics_claim"]
    if "compressed_air" in lower_id or "thermal" in lower_hypothesis or "process" in lower_hypothesis:
        return ["generic_benchmark_claim", "support_system_savings_claim"]
    return ["premature_strategic_claim"]


def _allow_legacy_string_fallback(question: dict[str, Any]) -> bool:
    return bool(question.get("allow_legacy_string_fallback"))


def _blocked_claims(question: dict[str, Any]) -> tuple[list[str], str]:
    structured_claims = _question_strings(question, "blocked_claims_if_missing")
    if structured_claims:
        return structured_claims, "structured_question_metadata"
    if _allow_legacy_string_fallback(question):
        question_id = text(question.get("question_id"))
        hypothesis_text = text(question.get("hypothesis_it_discriminates"))
        return _legacy_blocked_claims(question_id, hypothesis_text), "legacy_string_fallback_explicit"
    return _METADATA_GAP_BLOCKED_CLAIMS, "metadata_gap_prohibition"


def build_rival_hypothesis_register(
    *,
    dynamic_intake_question_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    stop_by_path = _stop_map(stop_condition_register)
    next_by_need = _next_search_map(next_best_search_register)
    rows: list[dict[str, Any]] = []
    for question in list(dynamic_intake_question_register or []):
        question_id = text(question.get("question_id"))
        if not question_id:
            continue
        rows.append(
            {
                "question_id": question_id,
                "rival_hypotheses": [text(item) for item in list(question.get("rival_hypotheses", []) or []) if text(item)],
                "supports_hypotheses": _question_strings(question, "supports_hypotheses"),
                "falsifies_hypotheses": _question_strings(question, "falsifies_hypotheses"),
                "structured_hypotheses": _structured_hypotheses(question),
                "evidence_needed": _evidence_needed(question, stop_by_path),
                "public_search_first": bool(list(question.get("public_search_context", []) or [])),
                "public_search_attempted": list(question.get("public_search_context", []) or []),
                "next_public_search_target": _next_public_search(question, next_by_need),
                "intake_if_missing": text(question.get("intake_question")),
                "claim_impact_if_missing": text(question.get("claim_impact_if_missing")),
                "priority": text(question.get("priority")),
            }
        )
    return rows


def build_hypothesis_discrimination_register(
    *,
    dynamic_intake_question_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
    next_best_search_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    stop_by_path = _stop_map(stop_condition_register)
    next_by_need = _next_search_map(next_best_search_register)
    rows: list[dict[str, Any]] = []
    for question in list(dynamic_intake_question_register or []):
        question_id = text(question.get("question_id"))
        if not question_id:
            continue
        rows.append(
            {
                "question_id": question_id,
                "hypothesis_it_discriminates": text(question.get("hypothesis_it_discriminates")),
                "supports_hypotheses": _question_strings(question, "supports_hypotheses"),
                "falsifies_hypotheses": _question_strings(question, "falsifies_hypotheses"),
                "structured_hypotheses": _structured_hypotheses(question),
                "evidence_needed": _evidence_needed(question, stop_by_path),
                "public_search_first": bool(list(question.get("public_search_context", []) or [])),
                "public_search_attempted": list(question.get("public_search_context", []) or []),
                "next_public_search_target": _next_public_search(question, next_by_need),
                "intake_if_missing": text(question.get("intake_question")),
                "claim_impact_if_missing": text(question.get("claim_impact_if_missing")),
                "linked_need_ids": [text(item) for item in list(question.get("linked_need_ids", []) or []) if text(item)],
                "linked_pack_names": [text(item) for item in list(question.get("linked_pack_names", []) or []) if text(item)],
                "comparison_requirements_unlocked": _question_strings(question, "comparison_requirements_unlocked"),
            }
        )
    return rows


def build_claim_impact_register(
    *,
    dynamic_intake_question_register: list[dict[str, Any]],
    stop_condition_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    stop_by_path = _stop_map(stop_condition_register)
    rows: list[dict[str, Any]] = []
    for question in list(dynamic_intake_question_register or []):
        question_id = text(question.get("question_id"))
        if not question_id:
            continue
        hypothesis_text = text(question.get("hypothesis_it_discriminates"))
        blocked_claims, governance_basis = _blocked_claims(question)
        rows.append(
            {
                "question_id": question_id,
                "claim_impact": text(question.get("claim_impact_if_missing")),
                "blocked_claims": blocked_claims,
                "claim_governance_basis": governance_basis,
                "evidence_needed": _evidence_needed(question, stop_by_path),
                "status_if_missing": "prohibited_or_conditional",
                "hypothesis_it_discriminates": hypothesis_text,
                "structured_hypotheses": _structured_hypotheses(question),
            }
        )
    return rows
