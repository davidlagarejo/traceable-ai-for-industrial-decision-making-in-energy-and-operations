from __future__ import annotations

import types

import runtime_orchestrator.adapters.motor_017 as motor_017_module
from runtime_orchestrator.adapters.motor_016 import Motor016Adapter
from runtime_orchestrator.adapters.motor_017 import Motor017Adapter
from runtime_orchestrator.adapters.motor_027 import Motor027Adapter
from runtime_orchestrator.adapters.motor_035 import Motor035Adapter
from runtime_orchestrator.adapters.motor_047 import Motor047Adapter
from runtime_orchestrator.adapters.motor_048 import Motor048Adapter
from runtime_orchestrator.adapters.motor_049 import Motor049Adapter
from runtime_orchestrator.adapters.motor_050 import Motor050Adapter
from runtime_orchestrator.adapters.motor_051 import Motor051Adapter
from runtime_orchestrator.adapters.motor_052 import Motor052Adapter
from runtime_orchestrator.adapters.motor_053 import Motor053Adapter
from runtime_orchestrator.adapters.motor_054 import Motor054Adapter
from runtime_orchestrator.zlab_skill.runtime_bridge import build_skill_first_runtime_wrapper_inputs
from tests.test_congruence_gold_nuggets import (
    _building_inputs as _gold_building_inputs,
    _manufacturing_inputs as _gold_manufacturing_inputs,
    _run as _run_gold_chain,
)
from tests.test_loss_pattern_activator import _warehouse_inputs as _raw_warehouse_inputs
from tests.test_system_consistency_validator import _report_package
from tests.test_warehouse_dynamic_congruence_acceptance import _run_warehouse_chain


def test_skill_cutover_authority_register_exposes_shadow_states_by_domain():
    bundle = _run_warehouse_chain()
    m53 = bundle["motor_053"]
    m54 = bundle["motor_054"]

    by_domain = {
        row["domain"]: row for row in m54["skill_cutover_authority_register"]
    }

    assert bundle["motor_052"]["pattern_authority_state"] == "skill_primary"
    assert by_domain["patterns"]["current_authority"] == "skill_primary"
    assert by_domain["patterns"]["coverage_state"] == "promoted"
    assert m53["financial_exposure_authority_state"] == "skill_primary"
    assert by_domain["financial_exposure"]["current_authority"] == "skill_primary"
    assert by_domain["financial_exposure"]["coverage_state"] == "promoted"
    assert by_domain["combinations"]["current_authority"] == "skill_primary_adjudicated"
    assert by_domain["combinations"]["coverage_state"] == "ready_for_adjudication"
    assert m54["tad_authority_state"] == "skill_primary"
    assert by_domain["tad"]["current_authority"] == "skill_primary"
    assert by_domain["tad"]["coverage_state"] == "promoted"
    assert m54["gold_nugget_authority_state"] == "skill_primary"
    assert by_domain["gold_nuggets"]["current_authority"] == "skill_primary"
    assert by_domain["gold_nuggets"]["coverage_state"] == "promoted"


def test_skill_cutover_authority_register_tracks_shared_keys_and_nonzero_counts():
    bundle = _run_warehouse_chain()
    m53 = bundle["motor_053"]
    m54 = bundle["motor_054"]

    by_domain = {
        row["domain"]: row for row in m54["skill_cutover_authority_register"]
    }

    assert m53["skill_financial_exposure_summary"]["total"] == m53["skill_financial_exposure_count"]
    assert m53["skill_financial_exposure_summary"]["authority_state"] == "skill_primary"
    assert "boundary leakage" in m53["skill_financial_exposure_summary"]["governed_categories"]
    assert by_domain["financial_exposure"]["legacy_count"] >= 1
    assert by_domain["financial_exposure"]["skill_count"] >= 1
    assert m54["authoritative_financial_exposure_register"] == m53["authoritative_financial_exposure_register"]
    assert m54["authoritative_tad_action_register"] == m54["skill_expanded_tad_action_register"]
    assert by_domain["tad"]["legacy_count"] >= 1
    assert by_domain["tad"]["skill_count"] >= 1
    assert by_domain["gold_nuggets"]["legacy_count"] >= 1
    assert by_domain["gold_nuggets"]["skill_count"] >= 3
    assert m54["authoritative_gold_nugget_register"] == m54["skill_gold_nugget_register"]
    gold_claim = next(
        row
        for row in m54["congruence_claim_contract_register"]
        if row["claim_id"] == "congruence_gold_nugget_claim"
    )
    assert gold_claim["supporting_sources"] == ["motor_054.authoritative_gold_nugget_register"]


def test_gold_nugget_cutover_state_varies_by_case_family():
    building = _run_gold_chain(_gold_building_inputs())
    manufacturing = _run_gold_chain(_gold_manufacturing_inputs())

    assert building["gold_nugget_authority_state"] == "skill_primary"
    assert manufacturing["gold_nugget_authority_state"] == "skill_primary"

    building_themes = {row["nugget_theme"] for row in building["skill_gold_nugget_register"]}
    manufacturing_themes = {row["nugget_theme"] for row in manufacturing["skill_gold_nugget_register"]}

    assert "controls_or_schedule" in building_themes
    assert "support_utility_loss" in manufacturing_themes
    assert "tariff_orchestration" in manufacturing_themes
    assert "model_prematurity" in building_themes
    assert "model_prematurity" in manufacturing_themes


def test_motor_047_builds_skill_first_family_thesis_for_warehouse_with_minimal_inputs():
    bundle = _run_warehouse_chain()
    out = Motor047Adapter().run(
        {
            **bundle["inputs"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["gold_nugget_authority_state"] == "skill_primary"
    assert thesis["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert thesis["report_mode"] == "Compliance / Investment Screening Brief"
    assert thesis["minimum_discriminating_evidence"]
    assert thesis["top_actions"]
    assert thesis["dominant_contradiction"]


def test_motor_047_builds_skill_first_family_thesis_for_manufacturing_with_minimal_inputs():
    bundle = _run_gold_bundle(_gold_manufacturing_inputs())
    out = Motor047Adapter().run(
        {
            **bundle["inputs"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["gold_nugget_authority_state"] == "skill_primary"
    assert thesis["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert thesis["report_mode"] == "Industrial Process Diagnostic Brief"
    assert thesis["minimum_discriminating_evidence"]
    assert thesis["top_actions"]
    assert thesis["dominant_contradiction"]


def test_motor_047_builds_skill_first_family_thesis_for_building_with_minimal_inputs():
    bundle = _run_gold_bundle(_gold_building_inputs())
    out = Motor047Adapter().run(
        {
            **bundle["inputs"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    thesis = out["executive_thesis"]

    assert thesis["thesis_state"] == "admissible_structural_thesis"
    assert thesis["gold_nugget_authority_state"] == "skill_primary"
    assert thesis["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert thesis["report_mode"] == "Compliance / Investment Screening Brief"
    assert thesis["minimum_discriminating_evidence"]
    assert thesis["top_actions"]
    assert thesis["dominant_contradiction"]


def test_motor_048_builds_skill_first_outline_for_warehouse_with_minimal_inputs():
    bundle = _run_warehouse_chain()
    m47 = Motor047Adapter().run(
        {
            **bundle["inputs"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    out = Motor048Adapter().run(
        {
            "motor_047": m47,
            "motor_054": bundle["motor_054"],
        }
    )
    outline = out["main_report_outline"]

    assert outline["visible_report_mode"] == "Compliance / Investment Screening Brief"
    assert outline["gold_nugget_authority_state"] == "skill_primary"
    assert outline["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert outline["compression_state"] == "thesis_compressed"
    assert len(outline["sections"]) == 12


def test_motor_048_builds_skill_first_outline_for_manufacturing_with_minimal_inputs():
    bundle = _run_gold_bundle(_gold_manufacturing_inputs())
    m47 = Motor047Adapter().run(
        {
            **bundle["inputs"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    out = Motor048Adapter().run(
        {
            "motor_047": m47,
            "motor_054": bundle["motor_054"],
        }
    )
    outline = out["main_report_outline"]

    assert outline["visible_report_mode"] == "Industrial Process Diagnostic Brief"
    assert outline["gold_nugget_authority_state"] == "skill_primary"
    assert outline["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert outline["compression_state"] == "thesis_compressed"
    assert len(outline["sections"]) == 12


def test_motor_048_builds_skill_first_outline_for_building_with_minimal_inputs():
    bundle = _run_gold_bundle(_gold_building_inputs())
    m47 = Motor047Adapter().run(
        {
            **bundle["inputs"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    out = Motor048Adapter().run(
        {
            "motor_047": m47,
            "motor_054": bundle["motor_054"],
        }
    )
    outline = out["main_report_outline"]

    assert outline["visible_report_mode"] == "Compliance / Investment Screening Brief"
    assert outline["gold_nugget_authority_state"] == "skill_primary"
    assert outline["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert outline["compression_state"] == "thesis_compressed"
    assert len(outline["sections"]) == 12


def _expected_gold_nugget_source(authority_state: str) -> str:
    return (
        "motor_054.authoritative_gold_nugget_register"
        if authority_state == "skill_primary"
        else "motor_054.strategic_gold_nugget_register"
    )


def _run_gold_bundle(inputs: dict) -> dict:
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run(
        {**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52}
    )
    m54 = Motor054Adapter().run(
        {
            **inputs,
            "motor_049": m49,
            "motor_050": m50,
            "motor_051": m51,
            "motor_052": m52,
            "motor_053": m53,
        }
    )
    return {
        "inputs": inputs,
        "motor_049": m49,
        "motor_050": m50,
        "motor_051": m51,
        "motor_052": m52,
        "motor_053": m53,
        "motor_054": m54,
    }


def _raw_family_inputs(family: str) -> dict:
    if family == "warehouse":
        return _raw_warehouse_inputs()
    if family == "manufacturing":
        return _gold_manufacturing_inputs()
    return _gold_building_inputs()


def _family_case_config(family: str) -> dict[str, str]:
    if family == "warehouse":
        return {
            "family": family,
            "case_id": "warehouse:mixed-runtime",
            "case_title": "Sunrise Logistics Hub",
            "address": "1450 Logistics Parkway, Dallas, TX 75201",
            "target_type": "warehouse_distribution",
            "owner_name": "Sunrise Logistics Owner",
            "owner_ticker": "NOT OBSERVED",
            "exchange": "",
            "document_type": "Compliance / Investment Screening Brief",
            "reframed_problem": (
                "Need to determine whether tariff structure, service intensity and control boundary "
                "are making area-based efficiency framing conceptually invalid."
            ),
            "dominant_conflict": "Tariff / control boundary vs generic warehouse efficiency framing",
            "dominant_variable": "charging schedule and service-level intensity",
            "comparison_peer": "logistics peers normalized by dock density and charging profile",
            "redesign_direction": "tariff orchestration and boundary validation before efficiency CAPEX",
        }
    if family == "manufacturing":
        return {
            "family": family,
            "case_id": "manufacturing:mixed-runtime",
            "case_title": "Wilsonart Manufacturing Site",
            "address": "TEMPLE, TX",
            "target_type": "manufacturing_facility",
            "owner_name": "Wilsonart",
            "owner_ticker": "NOT OBSERVED",
            "exchange": "",
            "document_type": "Compliance / Investment Screening Brief",
            "reframed_problem": (
                "Need to distinguish structural process duty from support-utility, maintenance "
                "and tariff exposure before underwriting plant efficiency logic."
            ),
            "dominant_conflict": "Process duty vs support-utility / maintenance interpretation",
            "dominant_variable": "support-utility load and tariff structure",
            "comparison_peer": "industrial peers normalized by throughput and thermal duty",
            "redesign_direction": "maintenance, tariff and support-utility validation before replacement CAPEX",
        }
    return {
        "family": "building",
        "case_id": "building:mixed-runtime",
        "case_title": "One Vanderbilt",
        "address": "ONE VANDERBILT AVE, NEW YORK, NY 10017",
        "target_type": "commercial_building",
        "owner_name": "SL Green",
        "owner_ticker": "SLG",
        "exchange": "NYSE",
        "document_type": "Compliance / Investment Screening Brief",
        "reframed_problem": (
            "Need to prove whether owner-controlled base-building systems dominate the economic "
            "boundary before underwriting retrofit value."
        ),
        "dominant_conflict": "Benchmark signal vs owner control boundary",
        "dominant_variable": "owner control over the covered load boundary",
        "comparison_peer": "Class A office peers normalized by boundary and schedule control",
        "redesign_direction": "boundary closure and submetering before owner-side retrofit logic",
    }


def _family_bundle(family: str) -> dict:
    if family == "warehouse":
        return _run_warehouse_chain()
    if family == "manufacturing":
        return _run_gold_bundle(_gold_manufacturing_inputs())
    return _run_gold_bundle(_gold_building_inputs())


def _family_minimum_evidence(bundle: dict) -> list[str]:
    actions = list(bundle["motor_054"].get("authoritative_tad_action_register", []) or [])
    for row in actions:
        evidence = [str(item).strip() for item in list(row.get("evidence_needed", []) or []) if str(item).strip()]
        if evidence:
            return evidence
    return ["bounded minimum discriminating evidence"]


def _family_tad_rows(bundle: dict) -> list[dict]:
    rows = list(bundle["motor_054"].get("authoritative_tad_action_register", []) or [])
    if rows:
        return rows[:5]
    return list(bundle["motor_054"].get("congruence_action_priority_register", []) or [])[:5]


def _family_financial_rows(bundle: dict) -> list[dict]:
    return list(bundle["motor_053"].get("authoritative_financial_exposure_register", []) or [])[:3]


def _build_family_motor_015(bundle: dict, cfg: dict[str, str]) -> dict:
    evidence_items = _family_minimum_evidence(bundle)
    tad_rows = _family_tad_rows(bundle)
    first_action = tad_rows[0] if tad_rows else {}
    first_exposure = (_family_financial_rows(bundle) or [{}])[0]
    first_nugget = (list(bundle["motor_054"].get("authoritative_gold_nugget_register", []) or [{}]) or [{}])[0]
    return {
        "output_blocks": [
            {
                "block_type": "decision_admissibility_block",
                "decision_state": "bounded screening only",
                "primary_block_reason": str(first_action.get("why", "")).strip()
                or "Minimum discriminating evidence remains open.",
                "decision_evaluated": str(first_action.get("strategic_action", "")).strip() or "REQUEST_MINIMUM_EVIDENCE",
                "recommended_action": str(first_action.get("prohibited_action", "")).strip()
                or "Keep the case bounded until the discriminating evidence is observed.",
            },
            {
                "block_type": "minimum_evidence_pack_block",
                "rows": [
                    {
                        "evidence_item": item,
                        "source": "runtime family congruence bridge",
                        "why_needed": str(first_nugget.get("why_it_matters", "")).strip()
                        or "Discriminates the leading structural hypotheses.",
                        "cases_resolved": [cfg["family"]],
                        "effort": "CRITICAL",
                        "decision_unlock": str(first_action.get("strategic_action", "")).strip()
                        or "bounded decision advance",
                    }
                    for item in evidence_items
                ],
            },
            {
                "block_type": "scenario_space_block",
                "rows": [
                    {
                        "scenario": str(first_nugget.get("gold_nugget", "")).strip()
                        or cfg["reframed_problem"],
                        "plausibility_status": "plausible",
                        "financial_meaning": str(first_nugget.get("why_it_matters", "")).strip()
                        or str(first_exposure.get("why_it_matters", "")).strip(),
                        "what_would_make_it_true": ", ".join(evidence_items),
                        "what_would_falsify_it": "Asset-specific evidence closes the wrong problem frame.",
                        "linked_decision_front": str(first_action.get("strategic_action", "")).strip()
                        or "REQUEST_MINIMUM_EVIDENCE",
                        "linked_evidence_item": evidence_items[0],
                        "evidence_needed": ", ".join(evidence_items),
                    }
                ],
            },
            {
                "block_type": "financial_exposure_block",
                "rows": [
                    {
                        "assumption": cfg["reframed_problem"],
                        "current_support": str(first_exposure.get("why_it_matters", "")).strip()
                        or "Bounded structural reading only.",
                        "downside_if_wrong": str(first_exposure.get("governed_exposure_category", "")).strip()
                        or "Capital can target the wrong variable.",
                        "evidence_needed": ", ".join(evidence_items),
                        "financial_consequence": str(first_exposure.get("tad_consequence", "")).strip()
                        or "Do not harden financial claims yet.",
                        "linked_decision_front": str(first_action.get("strategic_action", "")).strip()
                        or "REQUEST_MINIMUM_EVIDENCE",
                    }
                ],
            },
            {
                "block_type": "decision_fronts_block",
                "rows": [
                    {
                        "decision_front": str(row.get("strategic_action", "")).strip(),
                        "current_status": str(row.get("status", "")).strip(),
                        "why": str(row.get("why", "")).strip(),
                        "required_evidence": ", ".join(list(row.get("evidence_needed", []) or [])),
                        "admissible_action": str(row.get("prohibited_action", "")).strip()
                        or "Keep the case bounded.",
                    }
                    for row in tad_rows[:3]
                ],
            },
        ],
        "composite_reading": {"decision_state": "Blocked pending minimum discriminating evidence."},
        "facility_prior_id": f"prior::{cfg['family']}",
        "traceability_register": {"block_traces": []},
    }


def _build_family_motor_014(bundle: dict, cfg: dict[str, str]) -> dict:
    evidence_items = _family_minimum_evidence(bundle)
    first_action = (_family_tad_rows(bundle) or [{}])[0]
    nugget_rows = list(bundle["motor_054"].get("authoritative_gold_nugget_register", []) or [])
    return {
        "inference_records": [],
        "tension_records": [],
        "conflict_register": [],
        "opportunity_candidates": [],
        "uncertainty_register": [],
        "evidence_gap_register": [],
        "validation_queue": [],
        "next_best_questions": [],
        "claim_permission_summary": {
            "allowed": 3,
            "allowed_count": 3,
            "conditional": 0,
            "conditional_count": 0,
            "prohibited": 8,
            "prohibited_count": 8,
        },
        "variable_bottleneck_register": [
            {"variable_name": item}
            for item in evidence_items[:3]
        ],
        "decision_front_register": [
            {
                "decision_front": str(row.get("strategic_action", "")).strip(),
                "current_status": str(row.get("status", "")).strip(),
            }
            for row in _family_tad_rows(bundle)[:3]
        ],
        "scenario_space": [
            {
                "scenario": str(row.get("gold_nugget", "")).strip(),
                "financial_meaning": str(row.get("why_it_matters", "")).strip(),
                "evidence_needed": ", ".join(list(row.get("minimum_evidence", []) or evidence_items)),
                "falsification_condition": "Asset-specific evidence closes the live contradiction differently.",
            }
            for row in nugget_rows[:2]
        ],
        "report_readiness_register": {
            "report_type_allowed": [cfg["document_type"]],
            "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
            "reason": str(first_action.get("why", "")).strip()
            or "Bounded public and structural evidence supports screening only.",
        },
        "canonical_asset_context_summary": {
            "canonical_asset_context_state": "asset_context_minimal",
            "missing_clusters": ["control_boundary_cluster", "operating_regime_cluster"],
            "supported_clusters": ["identity_cluster", "geometry_size_cluster", "regulatory_cluster"],
            "screening_supported": True,
        },
    }


def _build_family_motor_034(bundle: dict, cfg: dict[str, str]) -> dict:
    evidence_items = _family_minimum_evidence(bundle)
    claim_contract_register = list(bundle["motor_054"].get("congruence_claim_contract_register", []) or [])
    return {
        "canonical_problem_frame": {
            "stated_problem": f"Should {cfg['case_title']} be advanced as an efficiency / underwriting case?",
            "reframed_problem": cfg["reframed_problem"],
            "dominant_conflict": cfg["dominant_conflict"],
            "minimum_evidence_to_discriminate": " + ".join(evidence_items),
            "minimum_evidence_source": "runtime_skill_family_bridge",
            "problem_frame_active": True,
            "reasoning_path": "structural_first",
            "leading_structural_output_mode": cfg["document_type"],
        },
        "claim_contract_register": claim_contract_register,
        "structural_claim_permission_register": [
            {
                "claim": "peer_comparison_claim",
                "permission": "hypothesis_only",
                "evidence_required": evidence_items,
                "current_evidence": "Family runtime signals remain bounded.",
                "allowed_language": "Conditional structural framing only.",
                "forbidden_language": "Local truth or superiority as fact.",
            }
        ],
        "report_output_mode_classifier_table": [
            {
                "canonical_output_mode": cfg["document_type"],
                "selected_for_publication": True,
                "classification_state": "selected_primary_default",
            }
        ],
        "report_type_classifier_table": [
            {
                "asset": cfg["case_title"],
                "recommended_report_type": cfg["document_type"],
                "why": "Family runtime signals support bounded screening only.",
                "allowed_claims": ["congruence_invalid_comparison_claim (conditional)"],
                "blocked_claims": ["roi_claim", "savings_claim"],
            }
        ],
        "report_readiness_register": {
            "report_type_allowed": [cfg["document_type"]],
            "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
            "reason": "Family runtime signals remain bounded and conditional.",
        },
        "structural_output_mode_classifier_table": [
            {
                "asset": cfg["case_title"],
                "recommended_output_mode": cfg["document_type"],
                "activation_state": "activated_secondary",
                "activation_reason": "Structural surfaces remain admissible as bounded overlays.",
                "required_claims": ["peer_comparison_claim"],
                "primary_report_type_guard": [cfg["document_type"]],
                "why": cfg["reframed_problem"],
            }
        ],
        "structural_output_mode_summary": {
            "primary_report_type": cfg["document_type"],
            "activated_secondary_modes": [cfg["document_type"]],
            "blocked_secondary_modes": [],
            "policy_note": "Structural output modes remain secondary governed surfaces.",
            "eligible_primary_modes": [cfg["document_type"]],
            "non_promotable_primary_modes": [],
            "leading_primary_promotion_candidate": cfg["document_type"],
            "primary_promotion_policy_note": "Promotion remains bounded by the evidence ceiling.",
            "activation_count": 1,
            "blocked_count": 0,
            "eligible_primary_count": 1,
        },
        "canonical_asset_context_summary": {
            "canonical_asset_context_state": "asset_context_minimal",
            "missing_clusters": ["control_boundary_cluster", "operating_regime_cluster"],
            "supported_clusters": ["identity_cluster", "geometry_size_cluster", "regulatory_cluster"],
            "screening_supported": True,
        },
    }


def _build_family_structural_bridge(bundle: dict, cfg: dict[str, str]) -> dict:
    evidence_items = _family_minimum_evidence(bundle)
    tad_rows = _family_tad_rows(bundle)
    first_action = tad_rows[0] if tad_rows else {}
    first_exposure = (_family_financial_rows(bundle) or [{}])[0]
    first_nugget = (list(bundle["motor_054"].get("authoritative_gold_nugget_register", []) or [{}]) or [{}])[0]
    return {
        "motor_033": {
            "expanded_structural_tad_action_register": tad_rows,
        },
        "motor_037": {
            "system_abstraction": {
                "selected_archetype_id": f"{cfg['family']}_mixed_runtime_screening",
                "asset_type": {"statement": cfg["target_type"]},
                "dominant_process_type": {"statement": cfg["dominant_variable"]},
            }
        },
        "motor_038": {
            "dominant_variable_register": [
                {
                    "variable": cfg["dominant_variable"],
                    "layer": "operations",
                    "dominance": "high",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_could_matter": str(first_nugget.get("why_it_matters", "")).strip()
                    or cfg["reframed_problem"],
                    "what_confirms_it": ", ".join(evidence_items),
                    "what_falsifies_it": "Asset-specific evidence shows a different dominant driver.",
                    "decision_impact": str(first_action.get("strategic_action", "")).strip()
                    or "bounded screening logic",
                }
            ]
        },
        "motor_040": {
            "cross_layer_conflict_register": [
                {
                    "conflict": cfg["dominant_conflict"],
                    "layers_involved": ["operations", "finance", "comparison"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "why_it_matters": str(first_nugget.get("what_to_do_next", "")).strip()
                    or cfg["reframed_problem"],
                    "what_confirms_it": evidence_items,
                    "what_falsifies_it": ["Asset-specific evidence closes the problem differently."],
                    "potential_redesign_direction": cfg["redesign_direction"],
                }
            ]
        },
        "motor_041": {
            "problem_framing_register": [
                {
                    "stated_problem": f"Advance {cfg['case_title']} as an efficiency / underwriting case.",
                    "reframed_problem": cfg["reframed_problem"],
                    "why_original_framing_may_be_wrong": str(first_nugget.get("gold_nugget", "")).strip()
                    or cfg["dominant_conflict"],
                    "evidence_needed": ", ".join(evidence_items),
                    "strategic_risk": str(first_exposure.get("governed_exposure_category", "")).strip()
                    or "Capital can target the wrong variable.",
                }
            ]
        },
        "motor_043": {
            "competitive_comparison_register": [
                {
                    "peer_type": cfg["comparison_peer"],
                    "evidence_state": "ARCHETYPAL_PRIOR",
                    "transferability": "conditional on normalized comparison basis",
                }
            ]
        },
        "motor_044": {
            "conditional_redesign_register": [
                {
                    "hypothesis": cfg["reframed_problem"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "if_confirmed": cfg["redesign_direction"],
                    "redesign_direction": cfg["redesign_direction"],
                    "if_falsified": "Shift the redesign path once the real dominant variable is bounded.",
                    "next_evidence": evidence_items,
                }
            ]
        },
        "motor_045": {
            "structural_financial_exposure_register": [
                {
                    "structural_assumption": cfg["reframed_problem"],
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "financial_exposure_if_wrong": str(first_exposure.get("why_it_matters", "")).strip()
                    or "Capital can target the wrong variable.",
                    "evidence_needed": ", ".join(evidence_items),
                    "allowed_financial_output": ["scenario framing"],
                    "prohibited_financial_output": ["ROI", "IRR", "NPV", "payback", "bankability", "savings claim"],
                }
            ],
            "evidence_state_by_layer_register": [
                {
                    "layer": "control / tariff / comparison",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "dominant_open_questions": evidence_items,
                    "observed_support": [],
                    "structural_risk_if_wrong": str(first_exposure.get("governed_exposure_category", "")).strip()
                    or "Wrong capital logic.",
                    "linked_conflicts": [cfg["dominant_conflict"]],
                    "linked_problem_frames": [cfg["reframed_problem"]],
                }
            ],
        },
        "motor_046": {
            "minimum_evidence_for_discrimination_register": [
                {
                    "rival_hypotheses": [
                        "The visible symptom reflects the right economic or physical denominator.",
                        "The visible symptom is hiding a different dominant driver or boundary problem.",
                    ],
                    "minimum_evidence": ", ".join(evidence_items),
                    "source": "runtime_skill_family_bridge",
                    "what_it_confirms": cfg["reframed_problem"],
                    "what_it_falsifies": cfg["dominant_conflict"],
                    "unlocks": str(first_action.get("strategic_action", "")).strip() or "bounded decision advance",
                }
            ]
        },
    }


def _build_family_pipeline_runtime_inputs(bundle: dict, cfg: dict[str, str]) -> dict:
    base_inputs = build_skill_first_runtime_wrapper_inputs(
        motor_007_output=bundle["inputs"].get("motor_007", {}),
        motor_012_output=bundle["inputs"].get("motor_012", {}),
        motor_028_output=bundle["inputs"].get("motor_028", {}),
        case_id=cfg["case_id"],
        case_title=cfg["case_title"],
        sector_context={
            "owner_name": cfg["owner_name"],
            "owner_ticker": cfg["owner_ticker"],
            "exchange": cfg["exchange"],
        },
        report_mode_override=cfg["document_type"],
        address_override=cfg["address"],
        address_source_id=f"declared_input::{cfg['family']}::address",
    )
    base_inputs["motor_014"] = _build_family_motor_014(bundle, cfg)
    base_inputs["motor_015"] = _build_family_motor_015(bundle, cfg)
    return base_inputs


def _render_runtime_package_case_with_thesis_overrides(
    tmp_path,
    monkeypatch,
    family: str,
    thesis_overrides: dict[str, object] | None = None,
) -> tuple[dict, dict, dict]:
    cfg = _family_case_config(family)
    bundle = _family_bundle(family)
    base_inputs = _build_family_pipeline_runtime_inputs(bundle, cfg)
    base_inputs.pop("motor_014", None)
    base_inputs.pop("motor_015", None)

    m47 = Motor047Adapter().run(
        {
            **base_inputs,
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    if thesis_overrides:
        m47["executive_thesis"] = {
            **dict(m47.get("executive_thesis", {}) or {}),
            **dict(thesis_overrides or {}),
        }
    m48 = Motor048Adapter().run(
        {
            "motor_047": m47,
            "motor_054": bundle["motor_054"],
        }
    )
    m16 = Motor016Adapter().run(
        {
            **base_inputs,
            "motor_047": m47,
            "motor_048": m48,
            "motor_049": bundle["motor_049"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )

    template_dir = tmp_path / f"template_{cfg['family']}"
    output_dir = tmp_path / f"output_{cfg['family']}"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)

    m17 = Motor017Adapter().run(
        {
            "motor_016": m16,
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )
    m27 = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / f"delivered_{cfg['family']}"),
                "run_id": f"run:{cfg['family']}:mixed-runtime",
            },
            "motor_016": m16,
            "motor_017": m17,
        }
    )
    return m16, m17, m27


def _render_runtime_package_case(tmp_path, monkeypatch, family: str) -> tuple[dict, dict, dict]:
    return _render_runtime_package_case_with_thesis_overrides(
        tmp_path,
        monkeypatch,
        family,
        thesis_overrides=None,
    )


def _rendered_tex_bundle(m17: dict) -> str:
    pdf_path = motor_017_module.Path(str(m17.get("pdf_path", "")).strip())
    job_dir = pdf_path.parent
    parts = [(job_dir / "main.tex").read_text(encoding="utf-8")]
    chapters_dir = job_dir / "Chapters"
    for chapter_name in list(m17.get("written_chapter_inventory", []) or []):
        parts.append((chapters_dir / str(chapter_name)).read_text(encoding="utf-8"))
    return "\n\n".join(parts)


def _bundle_default_report_mode(target_type: str) -> str:
    text = str(target_type or "").strip().lower()
    if "manufacturing" in text:
        return "Industrial Process Diagnostic Brief"
    return "Compliance / Investment Screening Brief"


def _build_live_bundle_runtime_inputs(bundle: dict, family: str) -> dict:
    target_definition = dict(bundle["inputs"]["motor_007"]["target_definition_contract"])
    target_type = str(target_definition.get("target_type", "")).strip()
    return build_skill_first_runtime_wrapper_inputs(
        motor_007_output=bundle["inputs"].get("motor_007", {}),
        motor_012_output=bundle["inputs"].get("motor_012", {}),
        motor_028_output=bundle["inputs"].get("motor_028", {}),
        case_id=f"live-bundle:{family}",
        case_title=str(target_definition.get("target_name", "")).strip() or family,
        report_mode_override=_bundle_default_report_mode(target_type),
        address_source_id=f"live_bundle::{family}::address",
    )


def _render_live_bundle_runtime_package_case(tmp_path, monkeypatch, family: str) -> tuple[dict, dict, dict]:
    bundle = _family_bundle(family)
    base_inputs = _build_live_bundle_runtime_inputs(bundle, family)

    m47 = Motor047Adapter().run(
        {
            **base_inputs,
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    m48 = Motor048Adapter().run(
        {
            "motor_047": m47,
            "motor_054": bundle["motor_054"],
        }
    )
    m16 = Motor016Adapter().run(
        {
            **base_inputs,
            "motor_047": m47,
            "motor_048": m48,
            "motor_049": bundle["motor_049"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )

    template_dir = tmp_path / f"live_bundle_template_{family}"
    output_dir = tmp_path / f"live_bundle_output_{family}"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)

    m17 = Motor017Adapter().run(
        {
            "motor_016": m16,
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )
    m27 = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / f"live_bundle_delivered_{family}"),
                "run_id": f"run:{family}:live-bundle",
            },
            "motor_016": m16,
            "motor_017": m17,
        }
    )
    return m16, m17, m27


def _render_live_bundle_routing_ready_package_case(tmp_path, monkeypatch, family: str) -> tuple[dict, dict, dict]:
    bundle = _family_bundle(family)
    m7 = dict(bundle["inputs"].get("motor_007", {}) or {})
    m35 = Motor035Adapter().run(
        {
            "motor_001": {},
            "motor_006": {},
            "motor_007": m7,
        }
    )

    target_definition = dict(m7.get("target_definition_contract", {}) or {})
    base_inputs = build_skill_first_runtime_wrapper_inputs(
        motor_007_output=m7,
        motor_012_output=bundle["inputs"].get("motor_012", {}),
        motor_028_output=bundle["inputs"].get("motor_028", {}),
        motor_035_output=m35,
        case_id=f"live-bundle-routing:{family}",
        case_title=str(target_definition.get("target_name", "")).strip() or family,
        report_mode_override=_bundle_default_report_mode(str(target_definition.get("target_type", ""))),
        address_source_id=f"live_bundle_routing::{family}::address",
    )

    m47 = Motor047Adapter().run(
        {
            **base_inputs,
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )
    m48 = Motor048Adapter().run(
        {
            "motor_047": m47,
            "motor_054": bundle["motor_054"],
        }
    )
    m16 = Motor016Adapter().run(
        {
            **base_inputs,
            "motor_047": m47,
            "motor_048": m48,
            "motor_049": bundle["motor_049"],
            "motor_051": bundle["motor_051"],
            "motor_052": bundle["motor_052"],
            "motor_053": bundle["motor_053"],
            "motor_054": bundle["motor_054"],
        }
    )

    template_dir = tmp_path / f"live_bundle_routing_template_{family}"
    output_dir = tmp_path / f"live_bundle_routing_output_{family}"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)

    m17 = Motor017Adapter().run(
        {
            "motor_016": m16,
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )
    m27 = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / f"live_bundle_routing_delivered_{family}"),
                "run_id": f"run:{family}:live-bundle-routing",
            },
            "motor_016": m16,
            "motor_017": m17,
        }
    )
    return m16, m17, m27


def _render_raw_input_routing_skill_chain_case(tmp_path, monkeypatch, family: str) -> tuple[dict, dict, dict]:
    inputs = _raw_family_inputs(family)
    m35 = Motor035Adapter().run(
        {
            "motor_001": {},
            "motor_006": {},
            "motor_007": dict(inputs.get("motor_007", {}) or {}),
        }
    )
    m49 = Motor049Adapter().run(inputs)
    m50 = Motor050Adapter().run({**inputs, "motor_049": m49})
    m51 = Motor051Adapter().run({**inputs, "motor_049": m49, "motor_050": m50})
    m52 = Motor052Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51})
    m53 = Motor053Adapter().run({**inputs, "motor_049": m49, "motor_050": m50, "motor_051": m51, "motor_052": m52})
    m54 = Motor054Adapter().run(
        {
            **inputs,
            "motor_049": m49,
            "motor_050": m50,
            "motor_051": m51,
            "motor_052": m52,
            "motor_053": m53,
        }
    )

    target_definition = dict((dict(inputs.get("motor_007", {}) or {}).get("target_definition_contract", {}) or {}))
    base_inputs = build_skill_first_runtime_wrapper_inputs(
        motor_007_output=inputs.get("motor_007", {}),
        motor_012_output=inputs.get("motor_012", {}),
        motor_028_output=inputs.get("motor_028", {}),
        motor_035_output=m35,
        case_id=f"raw-routing-skill:{family}",
        case_title=str(target_definition.get("target_name", "")).strip() or family,
        address_source_id=f"raw_routing_skill::{family}::address",
    )

    m47 = Motor047Adapter().run(
        {
            **base_inputs,
            "motor_051": m51,
            "motor_052": m52,
            "motor_053": m53,
            "motor_054": m54,
        }
    )
    m48 = Motor048Adapter().run({"motor_047": m47, "motor_054": m54})
    m16 = Motor016Adapter().run(
        {
            **base_inputs,
            "motor_047": m47,
            "motor_048": m48,
            "motor_049": m49,
            "motor_051": m51,
            "motor_052": m52,
            "motor_053": m53,
            "motor_054": m54,
        }
    )

    template_dir = tmp_path / f"raw_routing_skill_template_{family}"
    output_dir = tmp_path / f"raw_routing_skill_output_{family}"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)
    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)
    m17 = Motor017Adapter().run(
        {
            "motor_016": m16,
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )
    m27 = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / f"raw_routing_skill_delivered_{family}"),
                "run_id": f"run:{family}:raw-routing-skill",
            },
            "motor_016": m16,
            "motor_017": m17,
        }
    )
    return m16, m17, m27


def test_skill_runtime_wrapper_builder_uses_runtime_helper_for_compliance_and_routing():
    bundle = _family_bundle("warehouse")
    m7 = dict(bundle["inputs"].get("motor_007", {}) or {})
    m35 = Motor035Adapter().run(
        {
            "motor_001": {},
            "motor_006": {},
            "motor_007": m7,
        }
    )
    base_inputs = build_skill_first_runtime_wrapper_inputs(
        motor_007_output=m7,
        motor_012_output=bundle["inputs"].get("motor_012", {}),
        motor_028_output=bundle["inputs"].get("motor_028", {}),
        motor_035_output=m35,
        case_id="runtime-helper:warehouse",
        case_title="Warehouse Helper Case",
        address_source_id="runtime_helper::warehouse::address",
    )

    comp_case = base_inputs["motor_012"]["compliance_applicability_case"]
    assert comp_case["applicability_state"] == "screening_only"
    assert comp_case["compliance_posture_state"] == "validate_first"
    assert base_inputs["motor_012"]["facility_prior"]["compliance_applicability_case"] == comp_case
    assert base_inputs["__runtime__"]["report_identity_state"] == base_inputs["motor_035"]["report_type_allowed"]
    assert base_inputs["motor_035"]["jurisdiction_resolution"]["jurisdiction_scope"]
    assert any(
        str(row.get("field", "")).strip().lower() == "address"
        for row in list(base_inputs["motor_012"].get("asset_field_register", []) or [])
    )


def _render_and_deliver_case_with_gold_nugget_authority(
    *,
    tmp_path,
    monkeypatch,
    authority_state: str,
    source_register: str,
    case_id: str,
    document_type: str = "Compliance / Investment Screening Brief",
) -> tuple[dict, dict]:
    template_dir = tmp_path / f"template_{case_id}"
    output_dir = tmp_path / f"output_{case_id}"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)

    base_pkg = _report_package(
        exec_content="ok",
        c2_content="ok",
        a0_content="ok",
        document_type=document_type,
        extra_appendix_sections=[
            {"title": "Public Source Coverage Table", "chapter_id": "A6", "blocks": [{"content": "bounded source coverage"}]},
            {"title": "Report Type Classifier Table", "chapter_id": "A7", "blocks": [{"content": "recommended output mode remains screening"}]},
        ],
    )
    pkg = _report_package(
        exec_content="ok",
        c2_content="ok",
        a0_content="ok",
        document_type=document_type,
        extra_appendix_sections=[
            {"title": "Public Source Coverage Table", "chapter_id": "A6", "blocks": [{"content": "bounded source coverage"}]},
            {"title": "Report Type Classifier Table", "chapter_id": "A7", "blocks": [{"content": "recommended output mode remains screening"}]},
        ],
        executive_thesis={
            **base_pkg["executive_thesis"],
            "gold_nugget_authority_state": authority_state,
            "gold_nugget_source_register": source_register,
        },
        main_report_outline={
            **base_pkg["main_report_outline"],
            "gold_nugget_authority_state": authority_state,
            "gold_nugget_source_register": source_register,
        },
    )
    pkg["case_metadata"] = {**pkg["case_metadata"], "case_id": case_id}

    m17 = Motor017Adapter().run(
        {
            "motor_016": {"report_package": pkg},
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )
    m27 = Motor027Adapter().run(
        {
            "__pipeline__": {
                "output_dir": str(tmp_path / f"delivered_{case_id}"),
                "run_id": f"run:{case_id}",
            },
            "motor_016": {"report_package": pkg},
            "motor_017": m17,
        }
    )
    return m17, m27


def test_gold_nugget_authority_survives_end_to_end_render_delivery_for_warehouse(tmp_path, monkeypatch):
    bundle = _run_warehouse_chain()
    m54 = bundle["motor_054"]
    expected_state = m54["gold_nugget_authority_state"]
    expected_source = _expected_gold_nugget_source(expected_state)

    m17, m27 = _render_and_deliver_case_with_gold_nugget_authority(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        authority_state=expected_state,
        source_register=expected_source,
        case_id="warehouse:test",
    )

    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m17["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    manifest = m27["delivery_manifest"]
    assert manifest["gold_nugget_authority_state"] == "skill_primary"
    assert manifest["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert manifest["governance_summary"]["gold_nugget_authority_state"] == "skill_primary"


def test_gold_nugget_authority_survives_end_to_end_render_delivery_for_manufacturing(tmp_path, monkeypatch):
    m54 = _run_gold_chain(_gold_manufacturing_inputs())
    expected_state = m54["gold_nugget_authority_state"]
    expected_source = _expected_gold_nugget_source(expected_state)

    m17, m27 = _render_and_deliver_case_with_gold_nugget_authority(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        authority_state=expected_state,
        source_register=expected_source,
        case_id="manufacturing:test",
    )

    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m17["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    manifest = m27["delivery_manifest"]
    assert manifest["gold_nugget_authority_state"] == "skill_primary"
    assert manifest["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert manifest["governance_summary"]["gold_nugget_authority_state"] == "skill_primary"


def test_gold_nugget_authority_survives_end_to_end_render_delivery_for_building(tmp_path, monkeypatch):
    m54 = _run_gold_chain(_gold_building_inputs())
    expected_state = m54["gold_nugget_authority_state"]
    expected_source = _expected_gold_nugget_source(expected_state)

    m17, m27 = _render_and_deliver_case_with_gold_nugget_authority(
        tmp_path=tmp_path,
        monkeypatch=monkeypatch,
        authority_state=expected_state,
        source_register=expected_source,
        case_id="building:test",
    )

    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m17["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    manifest = m27["delivery_manifest"]
    assert manifest["gold_nugget_authority_state"] == "skill_primary"
    assert manifest["gold_nugget_source_register"] == "motor_054.authoritative_gold_nugget_register"
    assert manifest["governance_summary"]["gold_nugget_authority_state"] == "skill_primary"


def test_gold_nugget_authority_survives_mixed_runtime_motor_016_render_delivery_for_warehouse(tmp_path, monkeypatch):
    m16, m17, m27 = _render_runtime_package_case(tmp_path, monkeypatch, "warehouse")

    report_package = m16["report_package"]
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_intelligence_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_executive_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_gold_nugget_authority_survives_mixed_runtime_motor_016_render_delivery_for_manufacturing(tmp_path, monkeypatch):
    m16, m17, m27 = _render_runtime_package_case(tmp_path, monkeypatch, "manufacturing")

    report_package = m16["report_package"]
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_intelligence_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_executive_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_gold_nugget_authority_survives_mixed_runtime_motor_016_render_delivery_for_building(tmp_path, monkeypatch):
    m16, m17, m27 = _render_runtime_package_case(tmp_path, monkeypatch, "building")

    report_package = m16["report_package"]
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_intelligence_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_executive_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_motor_016_skill_first_package_support_survives_without_motor_014_or_motor_015(tmp_path, monkeypatch):
    m16, _, _ = _render_runtime_package_case(tmp_path, monkeypatch, "warehouse")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    questions_section = next(
        (row for row in report_view_sections if row.get("title") == "Detailed Validation Questions"),
        {},
    )
    questions_text = str(((questions_section.get("blocks", []) or [{}])[0] or {}).get("content", ""))

    assert report_package["output_block_count"] >= 4
    assert report_package["evidence_maturity_registers"]["report_readiness_register"]["reason"]
    assert report_package["evidence_maturity_registers"]["claim_permission_register"]
    assert report_package["evidence_maturity_registers"]["decision_permission_register"]
    assert report_view_sections
    assert "skill_q_01" in questions_text
    assert "Can the case produce bounded evidence for:" in questions_text
    assert report_package["structural_intelligence_summary"]["executive_thesis_present"] is True
    assert m16["motor_014_enrichment_state"] == "optional_legacy_absent_skill_backfilled"
    assert m16["motor_015_enrichment_state"] == "optional_legacy_absent_skill_backfilled"
    assert m16["legacy_enrichment_dependency_state"] == "optional_legacy_enrichment_only"
    assert report_package["legacy_enrichment_boundary"]["motor_014_enrichment_state"] == "optional_legacy_absent_skill_backfilled"
    assert report_package["legacy_enrichment_boundary"]["motor_015_enrichment_state"] == "optional_legacy_absent_skill_backfilled"


def test_live_bundle_runtime_cutover_chain_for_warehouse_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_live_bundle_runtime_package_case(tmp_path, monkeypatch, "warehouse")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_intelligence_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert "skill_q_01" in str(report_view_sections)
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_live_bundle_runtime_cutover_chain_for_manufacturing_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_live_bundle_runtime_package_case(tmp_path, monkeypatch, "manufacturing")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_intelligence_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert "skill_q_01" in str(report_view_sections)
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_live_bundle_runtime_cutover_chain_for_building_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_live_bundle_runtime_package_case(tmp_path, monkeypatch, "building")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["structural_intelligence_summary"]["gold_nugget_authority_state"] == "skill_primary"
    assert "skill_q_01" in str(report_view_sections)
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_routing_ready_live_bundle_cutover_chain_for_warehouse_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_live_bundle_routing_ready_package_case(tmp_path, monkeypatch, "warehouse")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert "skill_q_01" in str(report_view_sections)
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_routing_ready_live_bundle_cutover_chain_for_manufacturing_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_live_bundle_routing_ready_package_case(tmp_path, monkeypatch, "manufacturing")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert "skill_q_01" in str(report_view_sections)
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_routing_ready_live_bundle_cutover_chain_for_building_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_live_bundle_routing_ready_package_case(tmp_path, monkeypatch, "building")

    report_package = m16["report_package"]
    report_view_sections = list(
        (((report_package.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("sections", []) or [])
    )
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert "skill_q_01" in str(report_view_sections)
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_raw_input_routing_skill_chain_for_warehouse_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_raw_input_routing_skill_chain_case(tmp_path, monkeypatch, "warehouse")

    report_package = m16["report_package"]
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert m16["legacy_enrichment_dependency_state"] == "optional_legacy_enrichment_only"
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_raw_input_routing_skill_chain_for_manufacturing_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_raw_input_routing_skill_chain_case(tmp_path, monkeypatch, "manufacturing")

    report_package = m16["report_package"]
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert m16["legacy_enrichment_dependency_state"] == "optional_legacy_enrichment_only"
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_raw_input_routing_skill_chain_for_building_preserves_authority(tmp_path, monkeypatch):
    m16, m17, m27 = _render_raw_input_routing_skill_chain_case(tmp_path, monkeypatch, "building")

    report_package = m16["report_package"]
    assert report_package["executive_thesis"]["gold_nugget_authority_state"] == "skill_primary"
    assert report_package["main_report_outline"]["gold_nugget_authority_state"] == "skill_primary"
    assert m16["legacy_enrichment_dependency_state"] == "optional_legacy_enrichment_only"
    assert m17["gold_nugget_authority_state"] == "skill_primary"
    assert m27["delivery_manifest"]["gold_nugget_authority_state"] == "skill_primary"


def test_runtime_render_preserves_conditional_strategic_language_and_chart_surfaces_for_warehouse(
    tmp_path,
    monkeypatch,
):
    m16, m17, m27 = _render_runtime_package_case(tmp_path, monkeypatch, "warehouse")

    rendered = _rendered_tex_bundle(m17).lower()
    pdf_path = motor_017_module.Path(m17["pdf_path"])
    report_package = m16["report_package"]

    assert pdf_path.exists()
    assert "fair comparison basis" in rendered
    assert "wrong variable" in rendered
    assert "wrong denominator" in rendered
    assert "charging profile" in rendered
    assert "gold nugget estratégico" in rendered
    assert "prohibit roi" in rendered or "roi_claim" in rendered
    assert report_package["executive_thesis"]["thesis_state"] in {
        "admissible_structural_thesis",
        "conditional_structural_intelligence",
    }
    assert m27["delivery_manifest"]["document_type"] == "Compliance / Investment Screening Brief"


def test_render_engine_embeds_chart_surface_end_to_end_when_report_package_carries_chart_assets(
    tmp_path,
    monkeypatch,
):
    template_dir = tmp_path / "chart_template"
    output_dir = tmp_path / "chart_output"
    chapters_dir = template_dir / "Chapters"
    (template_dir / "Metadata").mkdir(parents=True, exist_ok=True)
    (template_dir / "Matter").mkdir(parents=True, exist_ok=True)
    (template_dir / "Bibliography").mkdir(parents=True, exist_ok=True)
    (template_dir / "Configurations").mkdir(parents=True, exist_ok=True)
    chapters_dir.mkdir(parents=True, exist_ok=True)

    monkeypatch.setattr(motor_017_module, "_TEMPLATE_DIR", template_dir)
    monkeypatch.setattr(motor_017_module, "_OUTPUT_DIR", output_dir)

    def _fake_run(cmd, cwd, capture_output, text, timeout):
        pdf_path = motor_017_module.Path(cwd) / "main.pdf"
        pdf_path.write_bytes(b"%PDF-1.4\n% fake pdf\n")
        return types.SimpleNamespace(returncode=0, stdout="", stderr="")

    monkeypatch.setattr(motor_017_module.subprocess, "run", _fake_run)

    pkg = _report_package(
        exec_content="ok",
        c2_content="ok",
        a0_content="ok",
        document_type="Compliance / Investment Screening Brief",
        extra_appendix_sections=[
            {"title": "Public Source Coverage Table", "chapter_id": "A6", "blocks": [{"content": "bounded source coverage"}]},
            {"title": "Report Type Classifier Table", "chapter_id": "A7", "blocks": [{"content": "recommended output mode remains screening"}]},
        ],
    )
    body_sections = list(
        (((pkg.get("approved_views", {}) or {}).get("report_view", {}) or {}).get("body_sections", []) or [])
    )
    comparison_section = next(
        row for row in body_sections if str(row.get("title", "")).strip() == "Peer / Competitive Comparison"
    )
    comparison_section["chart_b64"] = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mP8/x8AAwMCAO+aI/gAAAAASUVORK5CYII="
    comparison_section["chart_assets"] = [
        {
            "title": "Conditional Comparison Gate",
            "description": "Comparison remains conditional until the denominator and boundary are normalized.",
        }
    ]

    m17 = Motor017Adapter().run(
        {
            "motor_016": {"report_package": pkg},
            "motor_036": {"can_render_pdf": True, "critical_failures": []},
        }
    )

    job_dir = motor_017_module.Path(m17["pdf_path"]).parent
    rendered = _rendered_tex_bundle(m17)

    assert motor_017_module.Path(m17["pdf_path"]).exists()
    assert "\\includegraphics" in rendered
    assert "Chart: Conditional Comparison Gate" in rendered
    assert "Comparison remains conditional until the denominator and boundary are normalized." in rendered
    assert any((job_dir / "Figures" / "Charts").iterdir())


def test_runtime_render_preserves_problem_may_not_be_energy_and_fair_comparison_bounds(
    tmp_path,
    monkeypatch,
):
    m16, m17, _ = _render_runtime_package_case_with_thesis_overrides(
        tmp_path,
        monkeypatch,
        "warehouse",
        thesis_overrides={
            "surprising_but_evidenced_takeaway": "The problem may not be energy.",
            "dominant_operational_misunderstanding": "The asset may be measured with the wrong denominator.",
            "invalid_comparison_risk": (
                "Fair comparison is not admissible until dock intensity, charging regime and service boundary "
                "are normalized."
            ),
            "dominant_loss_logic": (
                "The dominant loss may sit in charging windows, tariff exposure or boundary leakage rather than "
                "generic efficiency."
            ),
            "what_is_not_admissible": [
                "Close ROI, savings, superiority, compliance or diagnosis claims before local evidence arrives."
            ],
        },
    )

    rendered = _rendered_tex_bundle(m17)
    executive_thesis = m16["report_package"]["executive_thesis"]

    assert "The problem may not be energy." in rendered
    assert "wrong denominator" in rendered.lower()
    assert "fair comparison is not admissible" in rendered.lower()
    assert "charging windows, tariff exposure or boundary leakage" in rendered.lower()
    assert "close roi, savings, superiority, compliance or diagnosis claims" in rendered.lower()
    assert executive_thesis["local_claim_closure_state"] != "local_truth_closed"
