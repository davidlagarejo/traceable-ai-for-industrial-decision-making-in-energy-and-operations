#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from datetime import datetime, timezone
from json import JSONDecodeError
from pathlib import Path
from typing import Any


def _repo_root() -> Path:
    return Path(__file__).resolve().parents[2]


def _runtime_root() -> Path:
    return Path(__file__).resolve().parents[1]


def _baseline_path() -> Path:
    return _repo_root() / "governanza" / "automation-base" / "us_public_data_routing_v1_release_baseline.json"


def _cli_path() -> Path:
    return _runtime_root() / "cli.py"


def _default_output_json() -> Path:
    return _repo_root() / "governanza" / "automation-base" / "us_public_data_routing_v1_certification_latest.json"


def _default_output_md() -> Path:
    return _repo_root() / "governanza" / "automation-base" / "us_public_data_routing_v1_certification_latest.md"


def _load_json(path: Path) -> dict[str, Any]:
    with path.open() as handle:
        return json.load(handle)


def _safe_load_json(path: Path) -> dict[str, Any]:
    try:
        if not path.exists() or path.stat().st_size == 0:
            return {}
        return _load_json(path)
    except (JSONDecodeError, OSError):
        return {}


def _motors_for_scope(scope: str) -> list[str]:
    if scope == "routing_evidence_subgraph":
        return ["motor_035", "motor_028", "motor_012", "motor_034"]
    return []


def _report_family_ok(report_family: str, recommended: str) -> bool:
    if report_family == "target_classification_brief_only":
        return "classification brief" in recommended.lower()
    if report_family == "target_clarification_brief_only":
        return recommended.strip() == "Target Clarification Brief"
    if report_family == "routing_path_active_with_ca_guidance_visible":
        return bool(recommended)
    if report_family == "industrial_route_active_with_tceq_context":
        return bool(recommended)
    if report_family == "manufacturing_route_active_with_process_context":
        return bool(recommended)
    if report_family == "technical_asset_route_allowed_with_downgrade_if_needed":
        return bool(recommended)
    return True


def _run_case(case: dict[str, Any], allow_cache: bool) -> dict[str, Any]:
    seed_path = _repo_root() / case["seed_path"]
    cli = _cli_path()
    motors = _motors_for_scope(case["validation_scope"])
    with tempfile.NamedTemporaryFile(prefix="us-routing-cert-", suffix=".json", delete=False) as tmp:
        output_path = Path(tmp.name)
    cmd = [sys.executable, str(cli), "run", "--inputs", str(seed_path), "--output", str(output_path)]
    if not allow_cache:
        cmd.append("--no-cache")
    if motors:
        cmd.extend(["--motors", ",".join(motors)])
    started_at = datetime.now(timezone.utc).isoformat()
    proc = subprocess.run(cmd, capture_output=True, text=True)
    finished_at = datetime.now(timezone.utc).isoformat()
    run_data = _safe_load_json(output_path)
    expected_target = case["target_classification_expected"]
    observed_target = str(run_data.get("target_type_classification", "")).strip()
    recommended_report = str(run_data.get("recommended_report_type", "")).strip()
    status = str(run_data.get("status", "")).strip()
    passed = (
        proc.returncode == 0
        and status == "completed"
        and observed_target == expected_target
        and _report_family_ok(case["expected_report_family"], recommended_report)
    )
    return {
        "case_key": case["case_key"],
        "seed_path": case["seed_path"],
        "validation_scope": case["validation_scope"],
        "command": cmd,
        "started_at": started_at,
        "finished_at": finished_at,
        "returncode": proc.returncode,
        "run_id": run_data.get("run_id", ""),
        "status": status,
        "expected_target_classification": expected_target,
        "observed_target_classification": observed_target,
        "expected_report_family": case["expected_report_family"],
        "recommended_report_type": recommended_report,
        "passed": passed,
        "stdout_tail": "\n".join(proc.stdout.splitlines()[-20:]),
        "stderr_tail": "\n".join(proc.stderr.splitlines()[-20:]),
        "output_json": str(output_path),
    }


def _write_markdown(
    baseline: dict[str, Any],
    selected_cases: list[dict[str, Any]],
    results: list[dict[str, Any]],
    path: Path,
) -> None:
    lines = [
        "# US Public Data Routing v1 Certification Snapshot",
        "",
        f"Generated on: `{datetime.now(timezone.utc).isoformat()}`",
        "",
        f"Baseline: `{baseline['baseline_name']}`",
        "",
        "| Case | Scope | Run ID | Status | Target | Report Type | Pass |",
        "|---|---|---|---|---|---|---|",
    ]
    result_by_key = {row["case_key"]: row for row in results}
    for case in selected_cases:
        row = result_by_key[case["case_key"]]
        lines.append(
            f"| {case['case_key']} | {case['validation_scope']} | "
            f"`{row['run_id']}` | `{row['status']}` | `{row['observed_target_classification']}` | "
            f"`{row['recommended_report_type']}` | `{'PASS' if row['passed'] else 'FAIL'}` |"
        )
    lines.extend(
        [
            "",
            "## Notes",
            "",
            "- This snapshot re-runs the frozen baseline seeds against the current runtime.",
            "- `routing_evidence_subgraph` cases are certified on `motor_035,motor_028,motor_012,motor_034`.",
            "- `full_run` cases are certified on the full pipeline.",
        ]
    )
    path.write_text("\n".join(lines) + "\n")


def main() -> int:
    parser = argparse.ArgumentParser(description="Certify the frozen US Public Data Routing v1 baseline.")
    parser.add_argument("--baseline-json", default=str(_baseline_path()))
    parser.add_argument("--output-json", default=str(_default_output_json()))
    parser.add_argument("--output-md", default=str(_default_output_md()))
    parser.add_argument("--cases", default="", help="Comma-separated case keys to certify. Default: all.")
    parser.add_argument("--allow-cache", action="store_true", help="Allow runtime cache during certification.")
    args = parser.parse_args()

    baseline = _load_json(Path(args.baseline_json))
    all_cases = list(baseline.get("golden_cases", []))
    selected_keys = [item.strip() for item in args.cases.split(",") if item.strip()]
    if selected_keys:
        selected_cases = [case for case in all_cases if case["case_key"] in selected_keys]
    else:
        selected_cases = all_cases

    results = [_run_case(case, allow_cache=args.allow_cache) for case in selected_cases]
    payload = {
        "baseline_name": baseline.get("baseline_name", ""),
        "frozen_on": baseline.get("frozen_on", ""),
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "allow_cache": args.allow_cache,
        "cases": results,
        "summary": {
            "total_cases": len(results),
            "passed_cases": sum(1 for row in results if row["passed"]),
            "failed_cases": sum(1 for row in results if not row["passed"]),
            "overall_pass": all(row["passed"] for row in results),
        },
    }

    output_json = Path(args.output_json)
    output_md = Path(args.output_md)
    output_json.write_text(json.dumps(payload, indent=2) + "\n")
    _write_markdown(baseline, selected_cases, results, output_md)

    failed = [row for row in results if not row["passed"]]
    if failed:
        for row in failed:
            print(
                f"FAIL {row['case_key']} run={row['run_id']} target={row['observed_target_classification']} "
                f"report={row['recommended_report_type']}",
                file=sys.stderr,
            )
        return 1

    for row in results:
        print(
            f"PASS {row['case_key']} run={row['run_id']} target={row['observed_target_classification']} "
            f"report={row['recommended_report_type']}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
