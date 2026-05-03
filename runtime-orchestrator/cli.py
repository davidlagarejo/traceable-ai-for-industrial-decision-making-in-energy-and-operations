#!/usr/bin/env python3
"""Runtime Orchestrator CLI.

Commands:
  run       Execute the pipeline (all motors or a subset)
  status    Show status of past runs
  inspect   Show detail of a specific run or motor
  motors    List all registered motors and their adapter status
"""
from __future__ import annotations

import argparse
import json
import logging
import sys
import time
from pathlib import Path

# Make src importable when running as script
sys.path.insert(0, str(Path(__file__).parent / "src"))
sys.path.insert(0, str(Path(__file__).parent))

from runtime_orchestrator.config import ensure_motor_paths
ensure_motor_paths()
from runtime_orchestrator.adapters import build_registry
from runtime_orchestrator.asset_contracts import derive_target_definition
from runtime_orchestrator.artifact_store import ArtifactStore
from runtime_orchestrator.config import (
    DEFAULT_ARTIFACT_STORE_DIR,
    DEFAULT_RUN_REGISTRY_DIR,
    MOTOR_DEPENDENCIES_FILE,
)
from runtime_orchestrator.dependency_resolver import DependencyResolver
from runtime_orchestrator.pipeline_orchestrator import PipelineOrchestrator
from runtime_orchestrator.run_registry import load_run_manifest
from target_seeds import build_address_seed, normalize_input_files, write_seed_file

_HERE = Path(__file__).parent


def _pipeline_alias_stem(pipeline_id: str) -> str:
    slug = (pipeline_id or "").strip().lower()
    if not slug:
        return ""
    parts = slug.split("-")
    if len(parts) >= 2 and len(parts[-1]) == 4 and parts[-1].isdigit():
        return "-".join(parts[:-1]).strip()
    return slug


def _matches_input_alias(path: Path, pipeline_id: str) -> bool:
    alias = _pipeline_alias_stem(pipeline_id)
    if not alias:
        return False
    stem = path.stem[:-7] if path.stem.endswith("_inputs") else path.stem
    if stem.lower() == alias:
        return True
    try:
        pipeline = json.loads(path.read_text())
    except Exception:
        return False
    target_definition = derive_target_definition(pipeline)
    candidates = {
        str(target_definition.get("target_id", "")).strip().lower(),
        str(target_definition.get("target_slug", "")).strip().lower(),
        str(target_definition.get("target_identifier", "")).strip().lower(),
        str(target_definition.get("target_name", "")).strip().lower(),
        str(pipeline.get("case_id", "")).strip().lower(),
    }
    return alias in {c for c in candidates if c}


def _make_orchestrator(artifact_dir: Path | None = None) -> PipelineOrchestrator:
    registry = build_registry()
    store = ArtifactStore(artifact_dir or DEFAULT_ARTIFACT_STORE_DIR)
    resolver = DependencyResolver(MOTOR_DEPENDENCIES_FILE)
    resolver.load()
    return PipelineOrchestrator(registry=registry, artifact_store=store, resolver=resolver)


def _resolve_inputs_file(pipeline_id: str, explicit_path: str | None) -> Path | None:
    if explicit_path:
        candidate = Path(explicit_path)
        if candidate.exists():
            return candidate
        relative = (_HERE / explicit_path).resolve()
        if relative.exists():
            return relative

    slug = (pipeline_id or "").strip().lower()
    candidates: list[Path] = []
    if slug:
        candidates.append(_HERE / "inputs" / f"{slug}_inputs.json")
        prefix = slug.split("-", 1)[0].strip()
        if prefix and prefix != slug:
            candidates.append(_HERE / "inputs" / f"{prefix}_inputs.json")
    for guessed in candidates:
        if guessed.exists():
            return guessed
    inputs_dir = _HERE / "inputs"
    if inputs_dir.exists():
        for path in sorted(inputs_dir.glob("*_inputs.json")):
            if _matches_input_alias(path, pipeline_id):
                return path
    return None


def _truth_label(data: dict) -> str:
    truth = data.get("truth_summary") or {}
    if truth:
        real = truth.get("completed_real", 0) + truth.get("cached_real", 0)
        stub = truth.get("stub", 0) + truth.get("cached_stub", 0) + truth.get("completed_stub", 0)
        return f"real:{real} stub:{stub}"

    motor_results = data.get("motor_results", {}) or {}
    real = 0
    stub = 0
    for result in motor_results.values():
        truth_state = result.get("truth_state")
        adapter_class = result.get("adapter_class", "")
        raw_status = result.get("status", "")
        if truth_state in ("completed_real", "cached_real"):
            real += 1
        elif truth_state in ("stub", "cached_stub", "completed_stub"):
            stub += 1
        elif raw_status == "completed" and adapter_class != "StubMotorAdapter":
            real += 1
        elif raw_status in ("stub",) or adapter_class == "StubMotorAdapter":
            stub += 1
    return f"real:{real} stub:{stub}"


# ── run ───────────────────────────────────────────────────────────────────────

def cmd_run(args: argparse.Namespace) -> None:
    orchestrator = _make_orchestrator(
        Path(args.artifact_dir) if args.artifact_dir else None
    )

    pipeline_inputs: dict = {}
    inputs_path = _resolve_inputs_file(args.pipeline_id, args.inputs)
    if args.inputs and inputs_path is None:
        print(f"Inputs file not found: {args.inputs}")
        sys.exit(1)
    if inputs_path is not None:
        pipeline_inputs = json.loads(inputs_path.read_text())
    if args.no_cache:
        control = dict(pipeline_inputs.get("__run_control__", {}))
        control["force_refresh_token"] = f"ts:{time.time_ns()}"
        pipeline_inputs["__run_control__"] = control

    motor_ids = args.motors.split(",") if args.motors else None
    force_rerun = args.force_rerun.split(",") if args.force_rerun else None

    print(f"Starting pipeline '{args.pipeline_id}' ...")
    if inputs_path is not None:
        print(f"Inputs : {inputs_path}")
    run = orchestrator.run(
        pipeline_id=args.pipeline_id,
        pipeline_inputs=pipeline_inputs,
        motor_ids=motor_ids,
        resume=not args.no_cache,
        force_rerun=force_rerun,
    )

    print(f"\nRun ID : {run.run_id}")
    print(f"Status : {run.status.value}")
    print(f"Started: {run.started_at}")
    print(f"Ended  : {run.completed_at}")
    print()

    summary = run._summary()
    for k, v in summary.items():
        if v:
            print(f"  {k:12s}: {v}")

    truth_summary = run._truth_summary()
    print("\nTruth summary:")
    for k in (
        "implemented_contract",
        "placeholder_contract",
        "completed_real",
        "cached_real",
        "stub",
        "cached_stub",
        "failed",
    ):
        v = truth_summary.get(k, 0)
        if v:
            print(f"  {k:20s}: {v}")

    if run.error:
        print(f"\nError: {run.error}")
        sys.exit(1)

    if args.output:
        Path(args.output).write_text(
            json.dumps(run.to_dict(), indent=2, ensure_ascii=False)
        )
        print(f"\nFull run manifest saved to {args.output}")


# ── status ────────────────────────────────────────────────────────────────────

def cmd_status(args: argparse.Namespace) -> None:
    registry_dir = DEFAULT_RUN_REGISTRY_DIR
    if not registry_dir.exists():
        print("No runs found.")
        return

    runs = sorted(registry_dir.glob("*.json"), key=lambda p: p.stat().st_mtime, reverse=True)
    if not runs:
        print("No runs found.")
        return

    limit = int(args.limit) if args.limit else 10
    print(f"{'RUN ID':24s}  {'PIPELINE':20s}  {'STATUS':24s}  {'TRUTH':22s}  STARTED")
    print("-" * 116)
    for p in runs[:limit]:
        try:
            data = load_run_manifest(p)
            truth_lbl = _truth_label(data)
            print(
                f"{data['run_id'][:22]:24s}  "
                f"{data['pipeline_id'][:18]:20s}  "
                f"{data['status']:24s}  "
                f"{truth_lbl[:22]:22s}  "
                f"{data.get('started_at', '')[:19]}"
            )
        except Exception:
            print(f"  (could not read {p.name})")


# ── inspect ───────────────────────────────────────────────────────────────────

def cmd_inspect(args: argparse.Namespace) -> None:
    registry_dir = DEFAULT_RUN_REGISTRY_DIR
    if args.run_id:
        matches = list(registry_dir.glob(f"*{args.run_id}*.json"))
        if not matches:
            print(f"Run not found: {args.run_id}")
            sys.exit(1)
        data = load_run_manifest(matches[0])
        if args.motor:
            motor_data = data.get("motor_results", {}).get(args.motor)
            if motor_data is None:
                print(f"Motor {args.motor} not in run {args.run_id}")
                sys.exit(1)
            print(json.dumps(motor_data, indent=2))
        else:
            print(json.dumps(data, indent=2))
    elif args.motor:
        store = ArtifactStore(DEFAULT_ARTIFACT_STORE_DIR)
        runs = store.list_runs(args.motor)
        print(f"Artifact store — {args.motor} ({len(runs)} runs):")
        for r in runs:
            print(f"  {r['inputs_hash'][:20]}  {r.get('produced_at','')[:19]}  {r.get('run_id','')[:20]}")
    else:
        print("Provide --run-id and/or --motor")


# ── motors ────────────────────────────────────────────────────────────────────

def cmd_motors(args: argparse.Namespace) -> None:
    registry = build_registry()
    resolver = DependencyResolver(MOTOR_DEPENDENCIES_FILE)
    resolver.load()
    store = ArtifactStore(DEFAULT_ARTIFACT_STORE_DIR)

    all_ids = resolver.all_motor_ids()
    print(f"{'MOTOR':12s}  {'ADAPTER':28s}  {'CACHED RUNS':>11s}  DEPS")
    print("-" * 80)
    for mid in all_ids:
        adapter = registry.get(mid)
        adapter_name = type(adapter).__name__ if adapter else "NOT REGISTERED"
        cached = len(store.list_runs(mid))
        deps = resolver.get_dependencies(mid)
        print(
            f"{mid:12s}  {adapter_name:28s}  {cached:>11d}  "
            f"{', '.join(deps) if deps else '—'}"
        )


def cmd_create_target(args: argparse.Namespace) -> None:
    pipeline = build_address_seed(
        address_raw=args.address,
        target_type=args.target_type,
        owner_name=args.owner_name,
        owner_ticker=args.owner_ticker,
        owner_cik=args.owner_cik,
        sector=args.sector,
        sic=args.sic,
        decision_intent=args.decision_intent,
        report_intent="decision_admissibility_brief",
    )
    inputs_dir = _HERE / "inputs"
    path = write_seed_file(inputs_dir, pipeline, stem_hint=args.stem)
    target_definition = pipeline.get("target_definition_contract", {})
    year = pipeline.get("case_id", "").split("-")[-1]
    pipeline_id = f"{target_definition.get('target_id', 'target')}-{year}"
    payload = {
        "ok": True,
        "pipeline_id": pipeline_id,
        "inputs_file": str(path),
        "target_id": target_definition.get("target_id", ""),
        "target_type": target_definition.get("target_type", ""),
        "address_raw": target_definition.get("address_raw", ""),
    }
    print(json.dumps(payload, indent=2, ensure_ascii=False))


def cmd_normalize_inputs(args: argparse.Namespace) -> None:
    inputs_dir = _HERE / "inputs"
    updated = normalize_input_files(inputs_dir)
    print(f"Normalized {len(updated)} input seed(s) in {inputs_dir}")
    for path in updated[:8]:
        print(f"  - {path.name}")
    if len(updated) > 8:
        print(f"  ... and {len(updated) - 8} more")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(prog="runtime-orchestrator")
    sub = parser.add_subparsers(dest="command", required=True)

    # run
    p_run = sub.add_parser("run", help="Execute the pipeline")
    p_run.add_argument("--log-level", default="INFO", choices=["DEBUG", "INFO", "WARNING", "ERROR"])
    p_run.add_argument("--pipeline-id", default="default", help="Logical pipeline name")
    p_run.add_argument("--inputs", help="Path to JSON file with pipeline inputs")
    p_run.add_argument("--motors", help="Comma-separated motor_ids to run (default: all)")
    p_run.add_argument("--no-cache", action="store_true", help="Ignore cached artifacts")
    p_run.add_argument("--force-rerun", help="Comma-separated motors to force re-execute")
    p_run.add_argument("--artifact-dir", help="Override artifact store directory")
    p_run.add_argument("--output", help="Save full run manifest to this JSON file")

    # status
    p_status = sub.add_parser("status", help="List recent pipeline runs")
    p_status.add_argument("--limit", default="10", help="Max runs to show")

    # inspect
    p_inspect = sub.add_parser("inspect", help="Inspect a run or motor artifacts")
    p_inspect.add_argument("--run-id", help="Run ID (partial match)")
    p_inspect.add_argument("--motor", help="Motor ID")

    # motors
    sub.add_parser("motors", help="List all motors and their adapter status")

    # create-target
    p_create = sub.add_parser("create-target", help="Create a target seed directly from an address")
    p_create.add_argument("--address", required=True, help="Asset or site address")
    p_create.add_argument("--target-type", default="commercial_building", help="Canonical target_type")
    p_create.add_argument("--owner-name", default="", help="Optional owner context")
    p_create.add_argument("--owner-ticker", default="", help="Optional owner ticker context")
    p_create.add_argument("--owner-cik", default="", help="Optional owner CIK context")
    p_create.add_argument("--sector", default="", help="Optional sector context")
    p_create.add_argument("--sic", default="", help="Optional SIC context")
    p_create.add_argument("--decision-intent", default="target_identification_required", help="Decision intent for the seed")
    p_create.add_argument("--stem", default="", help="Optional filename stem override")

    # normalize-inputs
    sub.add_parser("normalize-inputs", help="Normalize legacy input seeds to asset-first contracts")

    args = parser.parse_args()
    log_level = getattr(args, "log_level", "INFO")
    logging.basicConfig(
        level=getattr(logging, log_level),
        format="%(asctime)s %(levelname)-8s %(name)s — %(message)s",
        datefmt="%H:%M:%S",
    )

    dispatch = {
        "run": cmd_run,
        "status": cmd_status,
        "inspect": cmd_inspect,
        "motors": cmd_motors,
        "create-target": cmd_create_target,
        "normalize-inputs": cmd_normalize_inputs,
    }
    dispatch[args.command](args)


if __name__ == "__main__":
    main()
