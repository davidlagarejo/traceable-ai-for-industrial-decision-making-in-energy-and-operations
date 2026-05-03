from runtime_orchestrator.adapters.motor_033 import Motor033Adapter


def test_motor_033_canonicalizes_front_statuses_and_derives_prohibited_actions():
    out = Motor033Adapter().run(
        {
            "motor_014": {
                "inference_records": [],
                "conflict_register": [],
                "evidence_gap_register": [],
                "validation_queue": [],
                "next_best_questions": [],
                "decision_front_register": [
                    {
                        "decision_front": "Seller / operator evidence request",
                        "current_status": "ACT NOW",
                        "why": "Need owner evidence immediately.",
                        "required_evidence": "Minimum evidence pack",
                        "admissible_action": "Issue a targeted request now.",
                        "maturity_decision_name": "seller_or_operator_evidence_request",
                        "allowed_action_by_maturity": "ACT NOW",
                    },
                    {
                        "decision_front": "Compliance investment",
                        "current_status": "VALIDATE FIRST",
                        "why": "Current filing evidence is incomplete.",
                        "required_evidence": "Current compliance filing + GFA + utility / fuel profile",
                        "admissible_action": "Screen only; avoid closure.",
                        "maturity_decision_name": "compliance_investment",
                        "allowed_action_by_maturity": "VALIDATE FIRST",
                        "maturity_admissibility_state": "conditional",
                        "variable_bottleneck": "compliance_filing",
                    },
                    {
                        "decision_front": "Full technical diligence scope",
                        "current_status": "INVESTIGATE THEN DECIDE",
                        "why": "Critical clusters remain missing.",
                        "required_evidence": "Top blocking fields and subject-to-asset confirmation",
                        "admissible_action": "Sequence minimum pack first.",
                    },
                    {
                        "decision_front": "Process redesign",
                        "current_status": "NO-GO",
                        "why": "Process map and throughput are missing.",
                        "required_evidence": "Process map + throughput profile + control boundary + downtime tolerance",
                        "admissible_action": "Do not redesign the process.",
                        "maturity_decision_name": "process_redesign",
                    },
                ],
                "information_deficit_score": 0.71,
            },
            "motor_015": {},
            "motor_034": {
                "report_readiness_register": {
                    "reason": "Public evidence supports screening only; verification-grade decisions remain blocked."
                }
            },
            "motor_012": {},
        }
    )

    tad = out["tad_preliminary"]
    actions = {row["decision_front"]: row for row in tad["decision_front_actions"]}

    assert actions["Seller / operator evidence request"]["current_status"] == "ACT NOW"
    assert actions["Seller / operator evidence request"]["recommended_posture"] == "act_now"

    assert actions["Compliance investment"]["current_status"] == "VALIDATE FIRST"
    assert "LEGAL CLOSURE" in actions["Compliance investment"]["prohibited_action"]

    assert actions["Full technical diligence scope"]["current_status"] == "INVESTIGATE"
    assert actions["Full technical diligence scope"]["recommended_posture"] == "investigate"

    assert actions["Process redesign"]["current_status"] == "NO-GO"
    assert "NO PROCESS REDESIGN RECOMMENDATION" in actions["Process redesign"]["prohibited_action"]

    summary = tad["posture_summary"]
    assert summary["act_now"] == 1
    assert summary["validation_first"] == 1
    assert summary["investigate"] == 1
    assert summary["defer"] == 0
    assert summary["no_go"] == 1
    assert summary["investigate_then_decide"] == 1
    assert summary["bounded_candidate_action"] == 0
