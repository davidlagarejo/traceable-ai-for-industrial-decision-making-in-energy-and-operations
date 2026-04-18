from __future__ import annotations

import json
import uuid
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

from contracts.loader import hash_file
from engines.critique_packet_builder import build_revision_packet
from engines.phase_compliance_engine import evaluate_phase_compliance
from engines.phase_contract_loader import load_compiled_phase_contract
from engines.reference_comparator import (
    build_reference_anchor_profiles,
    compare_report_to_references,
    discover_reference_files,
)
from engines.report_assembler import write_audit_artifacts, write_json, write_manifest
from engines.report_normalizer import normalize_report
from engines.scoring_engine import build_scorecard
from models.datatypes import AuditManifest, ReAuditComparison, to_jsonable, utc_now_iso
from models.enums import GateStatus


def run_audit(
    *,
    contract_paths: list[str | Path],
    report_path: str | Path,
    reference_paths: list[str | Path] | None,
    output_dir: str | Path,
    settings: dict[str, Any],
) -> dict[str, Any]:
    audit_run_id = _new_run_id()
    started_at = utc_now_iso()
    compiled_contract = load_compiled_phase_contract(list(contract_paths))
    phase_ids = [phase.phase_id for phase in compiled_contract.phases]
    report = normalize_report(report_path, phase_ids=phase_ids)
    references = discover_reference_files(list(reference_paths or []))

    manifest = AuditManifest(
        audit_run_id=audit_run_id,
        report_id=report.report_id,
        started_at=started_at,
        completed_at=None,
        input_file_hashes={str(report_path): hash_file(report_path)},
        contract_file_hashes=compiled_contract.source_hashes,
        reference_file_hashes={str(path): hash_file(path) for path in references},
        output_artifact_locations={},
        settings=settings,
    )

    phase_evaluations = evaluate_phase_compliance(report, compiled_contract.phases)
    reference_profiles = build_reference_anchor_profiles(list(reference_paths or []))
    reference_gaps = compare_report_to_references(
        report,
        list(reference_paths or []),
        reference_profiles=reference_profiles,
    )
    findings = [finding for evaluation in phase_evaluations for finding in evaluation.findings]
    scorecard = build_scorecard(report, audit_run_id, phase_evaluations, reference_gaps, settings)
    revision_packet = build_revision_packet(
        report.report_id,
        audit_run_id,
        findings,
        compiled_contract,
        reference_gaps,
    )

    artifact_locations = write_audit_artifacts(
        output_dir,
        audit_run_id=audit_run_id,
        compiled_contract=compiled_contract,
        report=report,
        phase_evaluations=phase_evaluations,
        reference_gaps=reference_gaps,
        reference_profiles=reference_profiles,
        revision_packet=revision_packet,
        scorecard=scorecard,
        settings=settings,
    )
    manifest.completed_at = utc_now_iso()
    manifest.output_artifact_locations = dict(artifact_locations)
    manifest_path = write_manifest(output_dir, manifest)
    manifest.output_artifact_locations["audit_manifest.json"] = manifest_path
    write_manifest(output_dir, manifest)
    artifact_locations["audit_manifest.json"] = manifest_path

    return {
        "audit_run_id": audit_run_id,
        "compiled_contract": compiled_contract,
        "report": report,
        "phase_evaluations": phase_evaluations,
        "reference_gaps": reference_gaps,
        "scorecard": scorecard,
        "revision_packet": revision_packet,
        "manifest": manifest,
        "artifact_locations": artifact_locations,
    }


def compare_audit_runs(
    *,
    previous_output_dir: str | Path,
    current_output_dir: str | Path,
    output_path: str | Path | None = None,
) -> ReAuditComparison:
    previous = _load_run_outputs(previous_output_dir)
    current = _load_run_outputs(current_output_dir)

    previous_findings = {
        row["finding_id"]: row for row in previous["claim_violation_register.json"]
    }
    current_findings = {row["finding_id"]: row for row in current["claim_violation_register.json"]}
    previous_ids = set(previous_findings)
    current_ids = set(current_findings)

    previous_scores = _score_map(previous["audit_scorecard.json"])
    current_scores = _score_map(current["audit_scorecard.json"])
    score_delta = {
        name: current_scores.get(name, 0) - previous_scores.get(name, 0)
        for name in sorted(set(previous_scores) | set(current_scores))
    }
    threshold_met = (
        current["audit_scorecard.json"]["overall_compliance_gate"] == GateStatus.PASS.value
        and current["audit_scorecard.json"]["overall_quality_gate"] in {
            GateStatus.PASS.value,
            GateStatus.WARN.value,
        }
    )
    comparison = ReAuditComparison(
        previous_run_id=previous["audit_scorecard.json"]["audit_run_id"],
        current_run_id=current["audit_scorecard.json"]["audit_run_id"],
        resolved_findings=sorted(previous_ids - current_ids),
        unresolved_findings=sorted(previous_ids & current_ids),
        newly_introduced_findings=sorted(current_ids - previous_ids),
        score_delta=score_delta,
        threshold_met=threshold_met,
    )
    if output_path:
        write_json(output_path, to_jsonable(comparison))
    return comparison


def run_reaudit_loop(
    *,
    contract_paths: list[str | Path],
    report_versions: list[str | Path],
    reference_paths: list[str | Path] | None,
    output_root: str | Path,
    settings: dict[str, Any],
) -> list[dict[str, Any]]:
    max_iterations = int(settings.get("max_reaudit_iterations", 3))
    results: list[dict[str, Any]] = []
    for index, report_path in enumerate(report_versions[:max_iterations], start=1):
        output_dir = Path(output_root) / f"iteration_{index:02d}"
        result = run_audit(
            contract_paths=contract_paths,
            report_path=report_path,
            reference_paths=reference_paths,
            output_dir=output_dir,
            settings=settings,
        )
        results.append(result)
        scorecard = result["scorecard"]
        if scorecard.overall_compliance_gate == GateStatus.PASS and scorecard.overall_quality_gate in {
            GateStatus.PASS,
            GateStatus.WARN,
        }:
            break
    return results


def _new_run_id() -> str:
    timestamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    return f"audit-{timestamp}-{uuid.uuid4().hex[:8]}"


def _load_run_outputs(output_dir: str | Path) -> dict[str, Any]:
    out = Path(output_dir)
    required = ["audit_scorecard.json", "claim_violation_register.json"]
    data: dict[str, Any] = {}
    for filename in required:
        path = out / filename
        if not path.exists():
            raise FileNotFoundError(path)
        data[filename] = json.loads(path.read_text(encoding="utf-8"))
    return data


def _score_map(scorecard: dict[str, Any]) -> dict[str, int]:
    return {item["name"]: int(item["score"]) for item in scorecard.get("dimensions", [])}
