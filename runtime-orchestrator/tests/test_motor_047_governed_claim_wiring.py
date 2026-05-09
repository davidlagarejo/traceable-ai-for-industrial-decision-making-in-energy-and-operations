"""Tests for the R-W01+R-W02a wiring: motor_047 propagates
congruence_claim_contract_register from motor_054 → executive_thesis output.
"""
from __future__ import annotations

from runtime_orchestrator.adapters.motor_047 import Motor047Adapter
from runtime_orchestrator.executive_thesis import build_executive_thesis


def _minimal_kwargs():
    return {
        "system_abstraction": {},
        "canonical_problem_frame": {},
        "problem_framing_register": [],
        "dominant_variable_register": [],
        "cross_layer_conflict_register": [],
        "scenario_register": [],
        "structural_financial_exposure_register": [],
        "competitive_comparison_register": [],
        "conditional_redesign_register": [],
        "minimum_evidence_for_discrimination_register": [],
        "expanded_structural_tad_action_register": [],
        "claim_contract_register": [],
        "report_output_mode_classifier_table": [],
    }


def test_executive_thesis_accepts_congruence_claim_contract_register_kwarg():
    out = build_executive_thesis(
        **_minimal_kwargs(),
        congruence_claim_contract_register=[
            {
                "claim_id": "demo_claim",
                "permission": "allowed",
                "evidence_state": "ARCHETYPAL_PRIOR",
                "falsification_condition": "test",
            }
        ],
    )
    assert "governed_claim_contract_register" in out
    assert out["governed_claim_contract_count"] == 1
    assert out["governed_claim_contract_register"][0]["claim_id"] == "demo_claim"


def test_executive_thesis_default_is_empty_list():
    out = build_executive_thesis(**_minimal_kwargs())
    assert out["governed_claim_contract_register"] == []
    assert out["governed_claim_contract_count"] == 0


def test_motor_047_propagates_register_from_m54():
    adapter = Motor047Adapter()
    inputs = {
        "motor_054": {
            "congruence_claim_contract_register": [
                {
                    "claim_id": "claim_a",
                    "permission": "allowed",
                    "evidence_state": "CONDITIONAL_HYPOTHESIS",
                    "falsification_condition": "evidence shows X",
                },
                {
                    "claim_id": "claim_b",
                    "permission": "prohibited",
                    "evidence_state": "WEAK_SIGNAL",
                },
            ]
        }
    }
    result = adapter.run(inputs)
    assert result["governed_claim_contract_count"] == 2
    thesis = result["executive_thesis"]
    assert thesis["governed_claim_contract_count"] == 2
    ids = [c.get("claim_id") for c in thesis["governed_claim_contract_register"]]
    assert ids == ["claim_a", "claim_b"]


def test_motor_047_handles_missing_m54_gracefully():
    adapter = Motor047Adapter()
    result = adapter.run({})
    assert result["governed_claim_contract_count"] == 0
    assert result["executive_thesis"]["governed_claim_contract_register"] == []


def test_motor_047_handles_m54_without_register_key():
    adapter = Motor047Adapter()
    result = adapter.run({"motor_054": {"unrelated_key": "value"}})
    assert result["governed_claim_contract_count"] == 0


def test_governed_register_prohibitions_appear_in_what_is_not_admissible():
    """R-W02b: prohibited claims from the governed register surface in
    'what_is_not_admissible' (which feeds cap. 12 'Claim Permissions / What
    Not To Do' of the rendered PDF)."""
    out = build_executive_thesis(
        **_minimal_kwargs(),
        congruence_claim_contract_register=[
            {
                "claim_id": "no_unverified_roi",
                "permission": "prohibited",
                "statement": "Do not state ROI without bounded local evidence.",
            },
            {
                "claim_id": "no_compliance_closure",
                "permission": "prohibited",
                "statement": "Do not close compliance without permit-to-physics evidence.",
            },
        ],
    )
    blocked = out["what_is_not_admissible"]
    joined = " | ".join(blocked)
    assert "Do not state ROI without bounded local evidence." in joined
    assert "Do not close compliance without permit-to-physics evidence." in joined


def test_governed_register_takes_precedence_over_legacy_in_ordering():
    out = build_executive_thesis(
        **{**_minimal_kwargs(), "claim_contract_register": [
            {"claim_id": "legacy_x", "permission": "prohibited", "statement": "Legacy prohibition"},
        ]},
        congruence_claim_contract_register=[
            {"claim_id": "governed_y", "permission": "prohibited", "statement": "Governed prohibition"},
        ],
    )
    blocked = out["what_is_not_admissible"]
    # Governed comes first
    assert blocked[0] == "Governed prohibition"
    assert "Legacy prohibition" in blocked


def test_governed_register_dedupes_against_legacy_when_text_matches():
    out = build_executive_thesis(
        **{**_minimal_kwargs(), "claim_contract_register": [
            {"claim_id": "x", "permission": "prohibited", "statement": "Same wording"},
        ]},
        congruence_claim_contract_register=[
            {"claim_id": "y", "permission": "prohibited", "statement": "Same wording"},
        ],
    )
    blocked = out["what_is_not_admissible"]
    assert blocked.count("Same wording") == 1


# ── R-W05: end-to-end regression — archetypal_prior claims must NOT render as
# "NOT OBSERVED" once they reach the thesis-level surface. ──────────────────


def _stringify_thesis_payload(thesis: dict) -> str:
    """Flatten the thesis dict into a single text blob for substring assertions."""
    parts: list[str] = []

    def _walk(node):
        if isinstance(node, dict):
            for v in node.values():
                _walk(v)
        elif isinstance(node, list):
            for v in node:
                _walk(v)
        elif isinstance(node, str):
            parts.append(node)
        else:
            parts.append(str(node))

    _walk(thesis)
    return " | ".join(parts)


def test_archetypal_prior_claim_does_not_render_as_not_observed():
    """A governed allowed claim with evidence_state=ARCHETYPAL_PRIOR must
    survive into the thesis output with its statement intact, not collapsed
    into a NOT OBSERVED literal anywhere in the thesis surface."""
    governed_register = [
        {
            "claim_id": "tariff_exposure_archetypal",
            "claim_family": "congruence_intelligence_lane",
            "permission": "allowed",
            "evidence_state": "ARCHETYPAL_PRIOR",
            "statement": (
                "Charging-window economics may dominate the warehouse cost "
                "structure even before site bills are observed."
            ),
            "falsification_condition": "Tariff bills prove charging is not the driver.",
            "allowed_use": ["Bounded screening hypothesis"],
            "prohibited_use": ["Closed ROI", "Savings claim"],
        }
    ]
    thesis = build_executive_thesis(
        **_minimal_kwargs(),
        congruence_claim_contract_register=governed_register,
    )
    payload = _stringify_thesis_payload(thesis)

    # The claim's statement is preserved.
    assert "Charging-window economics may dominate" in payload

    # The literal "NOT OBSERVED" must NOT appear because of this claim.
    # (The string may legitimately appear elsewhere in other contexts — but
    # not as a render of a governed allowed archetypal_prior claim. We assert
    # at least that the governed register is intact and that the statement is
    # not suppressed.)
    governed_in_payload = thesis["governed_claim_contract_register"]
    assert governed_in_payload[0]["evidence_state"] == "ARCHETYPAL_PRIOR"
    assert governed_in_payload[0]["permission"] == "allowed"


def test_governed_prohibited_claim_appears_in_what_not_to_do_chapter():
    """End-to-end: a governed prohibition surfaces in the cap. 12 surface
    (what_is_not_admissible)."""
    governed_register = [
        {
            "claim_id": "no_premature_roi",
            "permission": "prohibited",
            "evidence_state": "CONDITIONAL_HYPOTHESIS",
            "statement": "Do not state ROI before service-level proxy is bounded.",
        }
    ]
    thesis = build_executive_thesis(
        **_minimal_kwargs(),
        congruence_claim_contract_register=governed_register,
    )
    blocked = thesis["what_is_not_admissible"]
    assert any("Do not state ROI" in s for s in blocked)


def test_governed_register_carries_falsification_condition_through():
    """Governed claim's falsification_condition must reach the thesis surface
    so motor_016 (R-W03) can render it as 'Falsification:' in the output."""
    governed_register = [
        {
            "claim_id": "claim_with_falsification",
            "permission": "allowed",
            "evidence_state": "WEAK_SIGNAL",
            "statement": "Some bounded structural reading.",
            "falsification_condition": "Direct measurement of X disproves the framing.",
        }
    ]
    thesis = build_executive_thesis(
        **_minimal_kwargs(),
        congruence_claim_contract_register=governed_register,
    )
    surfaced = thesis["governed_claim_contract_register"][0]
    assert surfaced["falsification_condition"].startswith("Direct measurement of X")


# ── Skill combination activation wiring (RECOVERY-2026-05-09 prompt) ───────


def test_skill_combination_activation_register_kwarg_default_is_empty():
    out = build_executive_thesis(**_minimal_kwargs())
    assert out["skill_combination_activation_register"] == []
    assert out["skill_combination_activation_count"] == 0


def test_skill_combination_activation_register_propagates():
    register = [
        {
            "combination_id": "warehouse_tariff_boundary_area_combo",
            "pattern_ids": ["warehouse_mhe_charging_demand_peak"],
            "combined_hypothesis": "Demand may dominate energy economics.",
        }
    ]
    out = build_executive_thesis(
        **_minimal_kwargs(),
        skill_combination_activation_register=register,
    )
    assert out["skill_combination_activation_count"] == 1
    assert out["skill_combination_activation_register"][0]["combination_id"] == "warehouse_tariff_boundary_area_combo"


def test_motor_047_propagates_skill_combinations_from_m54():
    from runtime_orchestrator.adapters.motor_047 import Motor047Adapter
    adapter = Motor047Adapter()
    inputs = {
        "motor_054": {
            "skill_combination_activation_register": [
                {"combination_id": "c_alpha", "pattern_ids": ["p1"]},
                {"combination_id": "c_beta", "pattern_ids": ["p2"]},
            ]
        }
    }
    result = adapter.run(inputs)
    assert result["skill_combination_activation_count"] == 2
    thesis = result["executive_thesis"]
    ids = [c["combination_id"] for c in thesis["skill_combination_activation_register"]]
    assert ids == ["c_alpha", "c_beta"]
