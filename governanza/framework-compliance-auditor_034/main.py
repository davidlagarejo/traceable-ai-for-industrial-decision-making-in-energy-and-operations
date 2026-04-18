from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from engines.re_audit_loop import compare_audit_runs, run_audit, run_reaudit_loop
from engines.settings import load_settings
from models.datatypes import to_jsonable


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="framework_compliance_auditor",
        description="Local-first framework phase compliance auditor.",
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    audit = subparsers.add_parser("audit", help="Audit one report against local contracts.")
    audit.add_argument("--contracts", nargs="+", required=True, help="Contract files or directories.")
    audit.add_argument("--report", required=True, help="Report file under review.")
    audit.add_argument("--references", nargs="*", default=[], help="Reference files or directories.")
    audit.add_argument("--output", default="outputs/latest", help="Output directory for audit artifacts.")
    audit.add_argument("--profile", default="config/profiles/default.yaml", help="Settings profile.")

    compare = subparsers.add_parser("compare-runs", help="Compare two completed audit output dirs.")
    compare.add_argument("--previous-output", required=True)
    compare.add_argument("--current-output", required=True)
    compare.add_argument("--output", default=None, help="Optional JSON output path for comparison.")

    loop = subparsers.add_parser("reaudit-loop", help="Audit a sequence of report versions.")
    loop.add_argument("--contracts", nargs="+", required=True)
    loop.add_argument("--reports", nargs="+", required=True)
    loop.add_argument("--references", nargs="*", default=[])
    loop.add_argument("--output-root", default="outputs/reaudit_loop")
    loop.add_argument("--profile", default="config/profiles/default.yaml")

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "audit":
        settings = load_settings(args.profile)
        result = run_audit(
            contract_paths=[Path(item) for item in args.contracts],
            report_path=Path(args.report),
            reference_paths=[Path(item) for item in args.references],
            output_dir=Path(args.output),
            settings=settings,
        )
        scorecard = result["scorecard"]
        print(f"audit_run_id: {result['audit_run_id']}")
        print(f"compliance_gate: {scorecard.overall_compliance_gate.value}")
        print(f"quality_gate: {scorecard.overall_quality_gate.value}")
        print("artifacts:")
        for name, location in sorted(result["artifact_locations"].items()):
            print(f"  {name}: {location}")
        return 0

    if args.command == "compare-runs":
        comparison = compare_audit_runs(
            previous_output_dir=args.previous_output,
            current_output_dir=args.current_output,
            output_path=args.output,
        )
        print(json.dumps(to_jsonable(comparison), indent=2, sort_keys=True))
        return 0

    if args.command == "reaudit-loop":
        settings = load_settings(args.profile)
        results = run_reaudit_loop(
            contract_paths=[Path(item) for item in args.contracts],
            report_versions=[Path(item) for item in args.reports],
            reference_paths=[Path(item) for item in args.references],
            output_root=Path(args.output_root),
            settings=settings,
        )
        print(f"iterations_run: {len(results)}")
        for result in results:
            scorecard = result["scorecard"]
            print(
                f"{result['audit_run_id']}: compliance={scorecard.overall_compliance_gate.value} "
                f"quality={scorecard.overall_quality_gate.value}"
            )
        return 0

    parser.error(f"unknown command: {args.command}")
    return 2


if __name__ == "__main__":
    sys.exit(main())
