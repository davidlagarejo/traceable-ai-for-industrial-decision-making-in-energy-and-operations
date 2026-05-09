"""Adapter for motor_027 — Artifact Export / Delivery Engine.

Takes the final compiled PDF from motor_017 and the report_package from
motor_016, and delivers them to configured output destinations.

Delivery targets (configured via pipeline inputs):
- Local filesystem: copy to output_dir (default: ~/ZLab_Reports/)
- Artifact metadata: write manifest JSON alongside the PDF
- Optionally: open PDF after delivery (macOS: open command)

The manifest includes: case_id, run_id, pdf_path, package_id,
epistemic_grade, produced_at, motor_chain_hash, section_inventory.
"""
from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from ..asset_contracts import derive_effective_case_id
from .base import BaseMotorAdapter

_DEFAULT_OUTPUT_DIR = Path.home() / "ZLab_Reports"


def _motor_chain_hash(report_package: dict, pdf_path: str) -> str:
    """Compute a hash over report_package + pdf_path for chain integrity."""
    key = (
        report_package.get("package_id", "")
        + "|"
        + report_package.get("epistemic_grade", "")
        + "|"
        + pdf_path
    )
    return "chain:" + hashlib.sha256(key.encode()).hexdigest()[:12]


def _build_section_inventory(report_package: dict) -> list[dict]:
    """Build a compact section inventory from the report_package."""
    approved_views = report_package.get("approved_views", {})
    primary_view_key = report_package.get("primary_view_key", "report_view")
    tdir_view = approved_views.get(primary_view_key) or approved_views.get("report_view") or approved_views.get("tdir_view", {})
    sections = (
        tdir_view.get("body_sections", []) + tdir_view.get("appendix_sections", [])
    )
    return [
        {
            "section_id": sec.get("section_id", ""),
            "chapter_id": sec.get("chapter_id", ""),
            "title": sec.get("title", ""),
            "section_type": sec.get("section_type", ""),
            "epistemic_marker": sec.get("epistemic_marker", ""),
        }
        for sec in sections
    ]


def _build_traceability_summary(report_package: dict) -> dict[str, Any]:
    traceability = report_package.get("report_traceability", {})
    section_traces = traceability.get("section_traces", [])
    return {
        "report_traceability_id": traceability.get("report_traceability_id", ""),
        "source_lineage_id": traceability.get("source_lineage_id", ""),
        "decision_core_lineage_id": traceability.get("decision_core_lineage_id", ""),
        "block_traceability_id": traceability.get("block_traceability_id", ""),
        "coverage_gap_types": traceability.get("coverage_gap_types", []),
        "admitted_source_types": traceability.get("admitted_source_types", []),
        "section_trace_count": len(section_traces),
    }


def _resolve_gold_nugget_authority(
    report_package: dict[str, Any],
    motor_017_output: dict[str, Any] | None = None,
) -> tuple[str, str]:
    m17 = motor_017_output or {}
    authority_state = str(m17.get("gold_nugget_authority_state", "") or "").strip()
    source_register = str(m17.get("gold_nugget_source_register", "") or "").strip()
    if authority_state and source_register:
        return authority_state, source_register
    for key in (
        "main_report_outline",
        "structural_executive_summary",
        "structural_intelligence_summary",
        "executive_thesis",
    ):
        row = report_package.get(key, {})
        if not isinstance(row, dict):
            continue
        if not authority_state:
            authority_state = str(row.get("gold_nugget_authority_state", "") or "").strip()
        if not source_register:
            source_register = str(row.get("gold_nugget_source_register", "") or "").strip()
        if authority_state and source_register:
            break
    return (
        authority_state or "legacy_primary_skill_shadow",
        source_register or "motor_054.strategic_gold_nugget_register",
    )


class Motor027Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_027"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_016", "motor_017"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = datetime.now(timezone.utc).isoformat()
        pipeline = inputs.get("__pipeline__", {})
        runtime = inputs.get("__runtime__", {}) if isinstance(inputs.get("__runtime__", {}), dict) else {}

        m16 = inputs.get("motor_016", {})
        m17 = inputs.get("motor_017", {})

        report_package = m16.get("report_package", {})
        pdf_path_str = m17.get("pdf_path", "")
        pdf_paths = m17.get("pdf_paths", {})
        compilation_status = m17.get("compilation_status", "unknown")
        render_job_id = m17.get("render_job_id", "")
        package_id = m17.get("package_id", report_package.get("package_id", "unknown"))
        gold_nugget_authority_state, gold_nugget_source_register = _resolve_gold_nugget_authority(
            report_package,
            m17,
        )

        # Pipeline delivery config
        output_dir_str = pipeline.get("output_dir", str(_DEFAULT_OUTPUT_DIR))
        open_after_delivery = pipeline.get("open_pdf_after_delivery", False)
        run_id = pipeline.get("run_id", "")
        case_id = report_package.get("case_metadata", {}).get("case_id") or derive_effective_case_id(pipeline)

        output_dir = Path(output_dir_str).expanduser().resolve()
        delivered = False
        delivery_errors: list[str] = []
        output_path_str = ""
        output_paths: dict[str, str] = {}
        manifest_path_str = ""
        governance_summary = report_package.get("governance_summary", {}) if isinstance(report_package.get("governance_summary", {}), dict) else {}
        routing_plan_summary = dict(governance_summary.get("routing_plan_summary", {}) or {})
        routing_bundle_summary = dict(governance_summary.get("routing_bundle_summary", {}) or {})
        report_preflight_summary = dict(governance_summary.get("report_preflight_summary", {}) or {})
        case_adaptation_memo = dict(report_package.get("case_adaptation_memo", {}) or {})
        source_family_coverage_table = list(report_package.get("source_family_coverage_table", []) or [])
        if not routing_plan_summary:
            mandatory_source_gaps = list(
                (governance_summary.get("scraping_admissibility_summary", {}) or {}).get("mandatory_sources_missing_from_executor", []) or []
            )
            routing_plan_summary = {
                "routing_plan_total": 0,
                "mandatory_source_gap_count": len(mandatory_source_gaps),
                "mandatory_sources_missing_from_executor": mandatory_source_gaps,
                "routing_plan_gate_passed": len(mandatory_source_gaps) == 0,
            }

        mandatory_source_gaps = list(routing_plan_summary.get("mandatory_sources_missing_from_executor", []) or [])
        disclosed_routing_gaps = {
            str(row.get("source_family", "")).strip()
            for row in source_family_coverage_table
            if str(row.get("source_family", "")).strip()
            and not bool(row.get("found", False))
            and not bool(row.get("queried", True))
            and str(row.get("scope", "")).strip() == "NOT_QUERIED"
        }
        exploratory_prior_routing_override = (
            str(report_package.get("document_type", "")).strip() == "Exploratory Prior Brief"
            and str(report_package.get("report_product_state", "")).strip() == "technical_report"
            and bool(mandatory_source_gaps)
            and set(mandatory_source_gaps).issubset(disclosed_routing_gaps)
        )
        if exploratory_prior_routing_override:
            routing_plan_summary = {
                **routing_plan_summary,
                "routing_plan_gate_passed": True,
                "delivery_override_applied": True,
                "delivery_override_reason": (
                    "Exploratory Prior Brief may deliver with disclosed routing gaps when the missing public sources are explicitly surfaced in the source-coverage appendix."
                ),
            }

        if not bool(routing_plan_summary.get("routing_plan_gate_passed", True)):
            return {
                "delivered": False,
                "delivery_manifest": {
                    "document_type": report_package.get("document_type", ""),
                    "report_product_state": report_package.get("report_product_state", ""),
                    "gold_nugget_authority_state": gold_nugget_authority_state,
                    "gold_nugget_source_register": gold_nugget_source_register,
                    "routing_plan_summary": routing_plan_summary,
                    "report_preflight_summary": report_preflight_summary,
                    "case_adaptation_summary": {
                        "substantive_dimension_count": case_adaptation_memo.get("substantive_dimension_count", 0),
                        "template_contamination_failure": case_adaptation_memo.get("template_contamination_failure", False),
                    },
                },
                "output_path": "",
                "manifest_path": "",
                "delivery_errors": [
                    "Routing-plan governance blocked delivery because one or more mandatory public sources were not executed."
                ],
                "produced_at": produced_at,
            }

        # Only attempt delivery if PDF compiled successfully
        if compilation_status != "success":
            return {
                "delivered": False,
                "delivery_manifest": {},
                "output_path": "",
                "manifest_path": "",
                "delivery_errors": [
                    f"PDF compilation status is '{compilation_status}' — delivery skipped."
                ],
                "produced_at": produced_at,
            }

        if not pdf_path_str:
            return {
                "delivered": False,
                "delivery_manifest": {},
                "output_path": "",
                "manifest_path": "",
                "delivery_errors": ["motor_017 did not produce a pdf_path — delivery skipped."],
                "produced_at": produced_at,
            }

        # Ensure output directory exists
        try:
            output_dir.mkdir(parents=True, exist_ok=True)
        except OSError as e:
            delivery_errors.append(f"Could not create output_dir {output_dir}: {e}")
            return {
                "delivered": False,
                "delivery_manifest": {},
                "output_path": "",
                "manifest_path": "",
                "delivery_errors": delivery_errors,
                "produced_at": produced_at,
            }

        source_pdf_map = pdf_paths if isinstance(pdf_paths, dict) and pdf_paths else {}
        if not source_pdf_map and pdf_path_str:
            source_pdf_map = {"en": pdf_path_str}

        for language, source_path in source_pdf_map.items():
            pdf_source = Path(source_path)
            pdf_dest = output_dir / pdf_source.name
            if not pdf_dest.parent.exists():
                pdf_dest.parent.mkdir(parents=True, exist_ok=True)
            try:
                if pdf_source.exists():
                    shutil.copy2(str(pdf_source), str(pdf_dest))
                    output_paths[language] = str(pdf_dest)
                    delivered = True
                else:
                    delivery_errors.append(f"PDF source not found [{language}]: {pdf_source}")
            except OSError as e:
                delivery_errors.append(f"Failed to copy PDF [{language}] to {pdf_dest}: {e}")

        output_path_str = output_paths.get("en") or next(iter(output_paths.values()), "")

        # Build delivery manifest
        case_meta = report_package.get("case_metadata", {})
        allowed_use = case_meta.get("allowed_use", [
            "Evidence request",
            "Diligence scoping",
            "Validation sequencing",
        ])
        prohibited_use = case_meta.get("prohibited_use", [
            "Investment recommendation",
            "Compliance conclusion",
            "Savings estimate",
            "Bankability claim",
        ])
        epistemic_grade = report_package.get("epistemic_grade", "Decision-grade")
        publication_ceiling = report_package.get("publication_ceiling", "publish_bounded")
        section_inventory = _build_section_inventory(report_package)
        traceability_summary = _build_traceability_summary(report_package)
        context_integrity_scan = report_package.get("context_integrity_scan", {})
        if context_integrity_scan and not context_integrity_scan.get("render_eligible", True):
            return {
                "delivered": False,
                "delivery_manifest": {
                    "document_type": report_package.get("document_type", ""),
                    "report_product_state": report_package.get("report_product_state", ""),
                    "gold_nugget_authority_state": gold_nugget_authority_state,
                    "gold_nugget_source_register": gold_nugget_source_register,
                    "context_integrity_summary": {
                        "scan_status": context_integrity_scan.get("scan_status", "blocked"),
                        "issue_count": context_integrity_scan.get("issue_count", 0),
                        "render_eligible": False,
                    },
                    "report_preflight_summary": report_preflight_summary,
                    "case_adaptation_summary": {
                        "substantive_dimension_count": case_adaptation_memo.get("substantive_dimension_count", 0),
                        "template_contamination_failure": case_adaptation_memo.get("template_contamination_failure", False),
                    },
                },
                "output_path": "",
                "manifest_path": "",
                "delivery_errors": [
                    "Context integrity guard blocked delivery because visible report content failed contamination or empty-field checks."
                ],
                "produced_at": produced_at,
            }
        chain_hash = _motor_chain_hash(report_package, pdf_path_str)
        financial_exposure_case = report_package.get("financial_exposure_case", {})
        compliance_applicability_case = report_package.get("compliance_applicability_case", {})
        report_type_classifier_table = list(report_package.get("report_type_classifier_table", []) or [])
        industry_adaptation_table = list(report_package.get("industry_adaptation_table", []) or [])
        structural_output_mode_classifier_table = list(report_package.get("structural_output_mode_classifier_table", []) or [])
        structural_output_mode_summary = dict(report_package.get("structural_output_mode_summary", {}) or {})
        structural_primary_promotion_gate = dict(report_package.get("structural_primary_promotion_gate", {}) or {})
        claim_contract_register = list(report_package.get("claim_contract_register", []) or [])
        structural_executive_summary = dict(report_package.get("structural_executive_summary", {}) or {})
        structural_intelligence_summary = dict(report_package.get("structural_intelligence_summary", {}) or {})
        structural_intelligence_registers = dict(report_package.get("structural_intelligence_registers", {}) or {})
        ingestion_learning_summary = dict(runtime.get("ingestion_learning_summary", {}) or {})
        case_delta_summary = dict(runtime.get("case_delta_summary", {}) or {})
        source_yield_memory_summary = dict(runtime.get("source_yield_memory_summary", {}) or {})
        next_ingestion_priority_update = dict(runtime.get("next_ingestion_priority_update", {}) or {})

        delivery_manifest: dict[str, Any] = {
            "manifest_version": "1.0",
            "case_id": case_id,
            "run_id": run_id,
            "package_id": package_id,
            "render_job_id": render_job_id,
            "document_type": report_package.get("document_type", ""),
            "report_product_state": report_package.get("report_product_state", ""),
            "pdf_source_path": pdf_path_str,
            "pdf_source_paths": source_pdf_map,
            "pdf_output_path": output_path_str,
            "pdf_output_paths": output_paths,
            "gold_nugget_authority_state": gold_nugget_authority_state,
            "gold_nugget_source_register": gold_nugget_source_register,
            "epistemic_grade": epistemic_grade,
            "publication_ceiling": publication_ceiling,
            "framework_constraint": report_package.get("framework_constraint", ""),
            "governance_summary": {
                "epistemic_grade": governance_summary.get("epistemic_grade", epistemic_grade),
                "publication_ceiling": governance_summary.get("publication_ceiling", publication_ceiling),
                "gold_nugget_authority_state": gold_nugget_authority_state,
                "gold_nugget_source_register": gold_nugget_source_register,
                "traceability_chain_complete": governance_summary.get("traceability_chain_complete", False),
                "blocking_conflicts": governance_summary.get("blocking_conflicts", 0),
                "stubs_active": governance_summary.get("stubs_active", 0),
                "scraping_admissibility_summary": governance_summary.get("scraping_admissibility_summary", {}),
                "routing_plan_summary": routing_plan_summary,
                "routing_bundle_summary": routing_bundle_summary,
                "report_preflight_summary": report_preflight_summary,
                "structural_output_mode_summary": structural_output_mode_summary,
                "structural_primary_promotion_gate": structural_primary_promotion_gate,
                "claim_contract_count": len(claim_contract_register),
                "structural_executive_summary": structural_executive_summary,
                "structural_intelligence_summary": structural_intelligence_summary,
                "ingestion_learning_summary": ingestion_learning_summary,
                "case_adaptation_summary": {
                    "substantive_dimension_count": case_adaptation_memo.get("substantive_dimension_count", 0),
                    "template_contamination_failure": case_adaptation_memo.get("template_contamination_failure", False),
                },
            },
            "produced_at": produced_at,
            "case_metadata": case_meta,
            "motor_chain_hash": chain_hash,
            "section_inventory": section_inventory,
            "total_sections": len(section_inventory),
            "traceability_summary": traceability_summary,
            "context_integrity_summary": {
                "scan_status": context_integrity_scan.get("scan_status", "unknown"),
                "issue_count": context_integrity_scan.get("issue_count", 0),
                "render_eligible": context_integrity_scan.get("render_eligible", True),
            },
            "routing_plan_summary": routing_plan_summary,
            "routing_bundle_summary": routing_bundle_summary,
            "report_preflight_summary": report_preflight_summary,
            "source_family_coverage_table": source_family_coverage_table,
            "report_type_classifier_table": report_type_classifier_table,
            "industry_adaptation_table": industry_adaptation_table,
            "structural_output_mode_classifier_table": structural_output_mode_classifier_table,
            "structural_output_mode_summary": structural_output_mode_summary,
            "structural_primary_promotion_gate": structural_primary_promotion_gate,
            "claim_contract_register": claim_contract_register,
            "structural_executive_summary": structural_executive_summary,
            "structural_intelligence_summary": structural_intelligence_summary,
            "structural_intelligence_registers": structural_intelligence_registers,
            "ingestion_learning_summary": ingestion_learning_summary,
            "case_delta_summary": case_delta_summary,
            "source_yield_memory_summary": source_yield_memory_summary,
            "next_ingestion_priority_update": next_ingestion_priority_update,
            "case_adaptation_summary": {
                "substantive_dimension_count": case_adaptation_memo.get("substantive_dimension_count", 0),
                "template_contamination_failure": case_adaptation_memo.get("template_contamination_failure", False),
                "failure_reasons": case_adaptation_memo.get("failure_reasons", []),
                "reference_count": (case_adaptation_memo.get("comparison_summary", {}) or {}).get("reference_count", 0),
                "closest_reference_key": (case_adaptation_memo.get("comparison_summary", {}) or {}).get("closest_reference_key", ""),
                "closest_reference_difference_count": (case_adaptation_memo.get("comparison_summary", {}) or {}).get("closest_reference_difference_count", 0),
            },
            "allowed_use": allowed_use,
            "prohibited_use": prohibited_use,
            "financial_readiness_summary": {
                "finance_readiness_state": financial_exposure_case.get("finance_readiness_state", ""),
                "scope_boundary": financial_exposure_case.get("scope_boundary", ""),
                "publication_ceiling": financial_exposure_case.get("publication_ceiling", ""),
                "bankability_posture": financial_exposure_case.get("bankability_posture", ""),
            },
            "compliance_posture_summary": {
                "applicability_state": compliance_applicability_case.get("applicability_state", ""),
                "compliance_posture_state": compliance_applicability_case.get("compliance_posture_state", ""),
                "determination_status": compliance_applicability_case.get("determination_status", ""),
                "publication_ceiling": compliance_applicability_case.get("publication_ceiling", ""),
            },
            "compilation_status": compilation_status,
            "available_languages": sorted(output_paths.keys()),
            "delivery_status": "delivered" if delivered else "failed",
            "delivery_errors": delivery_errors,
        }

        # Write manifest JSON alongside the PDF
        if delivered and output_path_str:
            manifest_name = Path(output_path_str).stem + "_manifest.json"
            manifest_dest = output_dir / manifest_name
            try:
                manifest_dest.write_text(
                    json.dumps(delivery_manifest, indent=2, default=str),
                    encoding="utf-8",
                )
                manifest_path_str = str(manifest_dest)
            except OSError as e:
                delivery_errors.append(f"Failed to write manifest to {manifest_dest}: {e}")

        # Optionally open PDF (macOS only)
        if delivered and open_after_delivery and output_path_str:
            try:
                subprocess.run(
                    ["open", output_path_str],
                    check=False,
                    timeout=5,
                )
            except (OSError, subprocess.TimeoutExpired):
                pass  # Non-fatal: open is optional

        return {
            "delivered": delivered,
            "delivery_manifest": delivery_manifest,
            "output_path": output_path_str,
            "output_paths": output_paths,
            "manifest_path": manifest_path_str,
            "delivery_errors": delivery_errors,
            "produced_at": produced_at,
        }
