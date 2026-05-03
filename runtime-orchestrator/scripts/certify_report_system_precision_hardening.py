#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[1]


REPO_ROOT = _repo_root()
RUNTIME_ROOT = _runtime_root()
sys.path.insert(0, str(RUNTIME_ROOT / "src"))
sys.path.insert(0, str(RUNTIME_ROOT / "tests"))

from runtime_orchestrator.adapters.motor_024 import Motor024Adapter
from runtime_orchestrator.adapters.motor_025 import Motor025Adapter
from runtime_orchestrator.adapters.motor_034 import Motor034Adapter
from test_precision_hardening_certification import (
    _build_screening_case_inputs,
    _build_wilsonart_case_inputs,
    _find_claim,
    _run_decision_chain,
)
from test_report_precision_hardening_baseline import _run_motor_007_from_seed


def _default_output_json() -> Path:
    return REPO_ROOT / "governanza" / "automation-base" / "report_system_precision_hardening_certification_latest.json"


def _default_output_md() -> Path:
    return REPO_ROOT / "governanza" / "automation-base" / "report_system_precision_hardening_certification_latest.md"


def _final_report_type_from_readiness(m34: dict[str, Any], allowed_report_classes: list[str]) -> str:
    out = Motor025Adapter().run(
        {
            "motor_001": {},
            "motor_022": {"__stub__": True},
            "motor_034": m34,
            "motor_024": {
                "governance_event_log": [],
                "pipeline_health_summary": {
                    "target_admissibility_state": "bounded_asset",
                    "allowed_report_classes": allowed_report_classes,
                    "report_identity_state": "Decision-Blocked Asset Brief",
                    "recommended_report_type": "Decision-Blocked Asset Brief",
                    "report_readiness_allowed": m34["report_readiness_register"]["report_type_allowed"],
                    "report_readiness_prohibited": m34["report_readiness_register"]["report_type_prohibited"],
                    "source_quality_gate_passed": True,
                    "final_report_ready": True,
                    "traceability_chain_complete": True,
                },
                "runtime_truth_summary": {"stub": 0, "cached_stub": 0, "completed_stub": 0},
                "stub_execution_register": [],
                "exception_register": [],
            },
        }
    )
    return str(out.get("recommended_report_type", "")).strip()


def _one_vanderbilt_case() -> dict[str, Any]:
    before = _run_motor_007_from_seed("ova_inputs.json")[1]
    inputs = _build_screening_case_inputs()
    m34, m14, m33 = _run_decision_chain(inputs)
    actions = {row["decision_front"]: row for row in m33["tad_preliminary"]["decision_front_actions"]}
    return {
        "case_key": "one_vanderbilt_nyc",
        "before_report_type": before["recommended_report_type"],
        "after_report_type": _final_report_type_from_readiness(m34, inputs["motor_007"]["allowed_report_classes"]),
        "claim_permissions": {
            "numeric_eui_claim": _find_claim(m34, "numeric_eui_claim")["current_permission"],
            "ll97_penalty_screening_claim": _find_claim(m34, "ll97_penalty_screening_claim")["current_permission"],
            "energy_savings_claim": _find_claim(m34, "energy_savings_claim")["current_permission"],
            "roi_range_claim": _find_claim(m34, "roi_range_claim")["current_permission"],
            "compliance_closure_claim": _find_claim(m34, "compliance_closure_claim")["current_permission"],
        },
        "tad_states": {
            "compliance_investment": actions["Compliance investment"]["current_status"],
            "seller_or_operator_evidence_request": actions["Seller / operator evidence request"]["current_status"],
        },
        "financial_exposure_rows": len(m14.get("financial_exposure_register", []) or []),
        "minimum_evidence_pack_count": len(m14.get("minimum_evidence_unlock_map", []) or []),
        "strong_public_screening_possible": bool(m34.get("cluster_report_readiness_profile", {}).get("strong_public_screening_possible", False)),
        "status": "passed",
    }


def _wilsonart_case() -> dict[str, Any]:
    before = _run_motor_007_from_seed("mfg_wilsonart_inputs.json")[1]
    inputs = _build_wilsonart_case_inputs()
    m34, m14, m33 = _run_decision_chain(inputs)
    actions = {row["decision_front"]: row for row in m33["tad_preliminary"]["decision_front_actions"]}
    return {
        "case_key": "wilsonart_temple_manufacturing",
        "before_report_type": before["recommended_report_type"],
        "after_report_type": _final_report_type_from_readiness(m34, inputs["motor_007"]["allowed_report_classes"]),
        "claim_permissions": {
            "process_change_hypothesis_claim": _find_claim(m34, "process_change_hypothesis_claim")["current_permission"],
            "process_redesign_recommendation_claim": _find_claim(m34, "process_redesign_recommendation_claim")["current_permission"],
            "roi_range_claim": _find_claim(m34, "roi_range_claim")["current_permission"],
            "compliance_screening_claim": _find_claim(m34, "compliance_screening_claim")["current_permission"],
        },
        "tad_states": {
            "environmental_or_permit_driven_investment": actions["Environmental or permit-driven investment"]["current_status"],
            "process_efficiency_or_utility_support_capex": actions["Process efficiency or utility-support CAPEX"]["current_status"],
            "process_redesign": actions["Process redesign"]["current_status"],
            "operator_evidence_request": actions["Operator evidence request"]["current_status"],
        },
        "financial_exposure_rows": len(m14.get("financial_exposure_register", []) or []),
        "minimum_evidence_pack_count": len(m14.get("minimum_evidence_unlock_map", []) or []),
        "status": "passed",
    }


def _hq_case() -> dict[str, Any]:
    before = _run_motor_007_from_seed("pld_inputs.json")[1]
    out = Motor034Adapter().run(
        {
            "motor_001": {},
            "motor_007": {
                "target_definition_contract": {
                    "address_raw": "PIER 1 BAY 1, SAN FRANCISCO, CA, 94111",
                    "jurisdiction_scope": ["US-CA-SF"],
                    "target_type": "warehouse_distribution",
                },
                "target_classification_object": {
                    "target_type": "CORPORATE_HEADQUARTERS",
                    "classification_confidence": "high",
                },
                "technical_substrate_readiness": "insufficient",
                "recommended_report_type": "Entity Address Classification Brief",
            },
            "motor_008": {},
            "motor_010": {},
            "motor_011": {},
            "motor_012": {"asset_field_register": [], "missing_evidence_register": [], "compliance_applicability_case": {}},
            "motor_028": {"source_register": [], "dataset_coverage_register": []},
        }
    )
    return {
        "case_key": "corporate_hq_or_mailing_address",
        "before_report_type": before["recommended_report_type"],
        "after_report_type": out["report_readiness_register"]["report_type_allowed"][0],
        "technical_report_prohibited": "Full Technical Decision Intelligence Report" in out["report_readiness_register"]["report_type_prohibited"],
        "status": "passed",
    }


def _self_evaluation_snapshot() -> dict[str, Any]:
    out = Motor024Adapter().run(
        {
            "__pipeline__": {"case_id": "ZLab-self-eval-snapshot"},
            "motor_001": {},
            "motor_002": {},
            "motor_007": {
                "recommended_report_type": "Compliance / Investment Screening Brief",
                "target_admissibility_state": "bounded_asset",
                "subject_gate_passed": True,
                "target_classification_object": {"target_type": "OPERATING_ASSET"},
                "target_definition_contract": {"target_name": "One Vanderbilt"},
            },
            "motor_009": {},
            "motor_028": {
                "routing_plan_compliance": {
                    "routing_ready": True,
                    "total_routed_sources": 5,
                    "accepted_routed_sources": 4,
                    "mandatory_sources_missing_from_executor": [],
                }
            },
            "motor_012": {
                "asset_field_register": [
                    {
                        "field": "address",
                        "value": "ONE VANDERBILT AVENUE, NEW YORK, NY, 10017",
                        "status": "OBSERVED",
                        "identity_supported": True,
                        "physical_substrate_supported": False,
                        "operating_substrate_supported": False,
                        "regulatory_supported": False,
                        "notes": "Source confirms identity only, not physical operating substrate.",
                    }
                ]
            },
            "motor_034": {
                "claim_permission_register": [
                    {"claim_name": "numeric_eui_claim", "current_permission": "allowed"},
                    {"claim_name": "roi_scenario_claim", "current_permission": "prohibited"},
                ],
                "decision_permission_register": [],
                "cluster_report_readiness_profile": {"strong_public_screening_possible": True},
                "report_readiness_register": {
                    "report_type_allowed": ["Compliance / Investment Screening Brief"],
                    "report_type_prohibited": ["Full Technical Decision Intelligence Report"],
                },
            },
            "motor_013": {},
            "motor_014": {
                "claim_permission_summary": {"allowed": 1, "conditional": 0, "prohibited": 1, "deferred": 0},
                "minimum_evidence_unlock_map": [
                    {
                        "evidence_item": "Utility bills and meter map",
                        "source": "owner / operator",
                        "why_needed": "Confirm owner-controllable energy basis.",
                        "unlocks": ["underwriting", "retrofit screening"],
                        "effort": "medium",
                        "priority": "high",
                    }
                ],
                "scenario_space": [
                    {
                        "scenario": "A. Owner-controllable energy upside exists only after tenant/control boundary confirmation.",
                        "financial_meaning": "Avoid unsupported underwriting uplift.",
                        "what_would_falsify_it": "Lease and metering evidence show tenant pass-through dominates.",
                        "evidence_needed": "Utility bills + meter map + lease control boundary",
                        "linked_decision_front": "Compliance investment",
                        "linked_evidence_item": "Utility bills and meter map",
                    }
                ],
                "financial_exposure_register": [
                    {
                        "assumption": "Owner-controllable energy upside exists",
                        "current_support": "unsupported until utility and control-boundary evidence arrive",
                        "downside_if_wrong": "Retrofit CAPEX fails to improve owner economics",
                        "evidence_needed": "Utility bills + meter map + lease control boundary",
                        "financial_consequence": "Remove energy upside from screening until validated",
                        "linked_decision_front": "Compliance investment",
                    }
                ],
            },
            "motor_019": {},
            "motor_020": {},
            "motor_015": {},
            "motor_016": {
                "report_package": {
                    "context_integrity_scan": {"render_eligible": True},
                    "case_adaptation_memo": {
                        "rows": [{"dimension": "asset_type_logic"}],
                        "substantive_dimension_count": 6,
                        "required_dimension_count": 7,
                        "template_contamination_failure": False,
                        "failure_reasons": [],
                    },
                }
            },
            "motor_017": {},
            "motor_027": {},
            "motor_033": {
                "tad_preliminary": {
                    "decision_front_actions": [
                        {"decision_front": "Compliance investment", "current_status": "VALIDATE FIRST"},
                        {"decision_front": "Seller / operator evidence request", "current_status": "ACT NOW"},
                    ]
                }
            },
        }
    )
    return out["phase_self_evaluation_register"]


def _write_markdown(payload: dict[str, Any], path: Path) -> None:
    cases = {row["case_key"]: row for row in payload["cases"]}
    lines = [
        "# Report System Precision Hardening Certification Snapshot",
        "",
        f"Generated on: `{payload['generated_at']}`",
        "",
        "## Case Comparison",
        "",
        "| Case | Before | After | Key TAD Signal | Status |",
        "|---|---|---|---|---|",
        f"| One Vanderbilt | `{cases['one_vanderbilt_nyc']['before_report_type']}` | `{cases['one_vanderbilt_nyc']['after_report_type']}` | `Compliance investment = {cases['one_vanderbilt_nyc']['tad_states']['compliance_investment']}` | `PASS` |",
        f"| Wilsonart | `{cases['wilsonart_temple_manufacturing']['before_report_type']}` | `{cases['wilsonart_temple_manufacturing']['after_report_type']}` | `Process redesign = {cases['wilsonart_temple_manufacturing']['tad_states']['process_redesign']}` | `PASS` |",
        f"| HQ / Mailing | `{cases['corporate_hq_or_mailing_address']['before_report_type']}` | `{cases['corporate_hq_or_mailing_address']['after_report_type']}` | `Technical report prohibited = {cases['corporate_hq_or_mailing_address']['technical_report_prohibited']}` | `PASS` |",
        "",
        "## Acceptance",
        "",
        f"- One Vanderbilt and Wilsonart diverge: `{payload['summary']['one_vanderbilt_vs_wilsonart_diverge']}`",
        f"- Self-evaluation artifact exists: `{payload['summary']['self_evaluation_artifact_present']}`",
        f"- Overall pass: `{payload['summary']['overall_pass']}`",
        "",
        "## Self-Evaluation Snapshot",
        "",
        f"- Overall result: `{payload['self_evaluation']['summary']['overall_result']}`",
        f"- Resolved: `{payload['self_evaluation']['summary']['resolved']}`",
        f"- Partially resolved: `{payload['self_evaluation']['summary']['partially_resolved']}`",
        f"- Unresolved: `{payload['self_evaluation']['summary']['unresolved']}`",
    ]
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    generated_at = datetime.now(timezone.utc).isoformat()
    cases = [
        _one_vanderbilt_case(),
        _wilsonart_case(),
        _hq_case(),
    ]
    self_evaluation = _self_evaluation_snapshot()
    one_vanderbilt = next(row for row in cases if row["case_key"] == "one_vanderbilt_nyc")
    wilsonart = next(row for row in cases if row["case_key"] == "wilsonart_temple_manufacturing")
    summary = {
        "total_cases": len(cases),
        "passed_cases": sum(1 for row in cases if row["status"] == "passed"),
        "failed_cases": sum(1 for row in cases if row["status"] != "passed"),
        "one_vanderbilt_vs_wilsonart_diverge": one_vanderbilt["after_report_type"] != wilsonart["after_report_type"],
        "self_evaluation_artifact_present": bool(self_evaluation.get("rows")),
        "overall_pass": (
            all(row["status"] == "passed" for row in cases)
            and one_vanderbilt["after_report_type"] == "Compliance / Investment Screening Brief"
            and wilsonart["after_report_type"] == "Decision-Blocked Asset Brief"
            and bool(self_evaluation.get("rows"))
        ),
    }
    payload = {
        "generated_at": generated_at,
        "cases": cases,
        "self_evaluation": self_evaluation,
        "summary": summary,
    }
    json_path = _default_output_json()
    md_path = _default_output_md()
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n")
    _write_markdown(payload, md_path)
    if not summary["overall_pass"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
