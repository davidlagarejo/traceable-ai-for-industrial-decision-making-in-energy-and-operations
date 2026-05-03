from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


REPO_ROOT = Path(__file__).resolve().parents[2]
AUTOMATION_BASE = REPO_ROOT / "governanza" / "automation-base"
GOVERNANZA_ROOT = REPO_ROOT / "governanza"
MOTOR_DEPENDENCIES_PATH = AUTOMATION_BASE / "motor_dependencies.json"
ADAPTERS_DIR = REPO_ROOT / "runtime-orchestrator" / "src" / "runtime_orchestrator" / "adapters"

OUTPUT_JSON = AUTOMATION_BASE / "runtime_motor_reconciliation_snapshot_latest.json"
OUTPUT_MD = AUTOMATION_BASE / "runtime_motor_reconciliation_snapshot_latest.md"


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def _motor_suffix(motor_id: str) -> str:
    return motor_id.split("_")[-1]


def _motor_name_to_slug(name: str) -> str:
    # Mirror motor_creator.models.motor_name_to_slug so this snapshot matches cli.py status.
    slug = name.lower()
    slug = re.sub(r"\s*\+\s*", "-", slug)
    slug = re.sub(r"\s*/\s*", "-", slug)
    slug = re.sub(r"\s*&\s*", "-", slug)
    slug = re.sub(r"\s+", "-", slug)
    slug = re.sub(r"[^a-z0-9-]", "", slug)
    slug = re.sub(r"-+", "-", slug).strip("-")
    return slug


def _expected_governance_dir_name(motor_id: str, motor_name: str) -> str:
    return f"{_motor_name_to_slug(motor_name)}_{_motor_suffix(motor_id)}"


def _expected_governance_dir(motor_id: str, motor_name: str) -> Path | None:
    expected = GOVERNANZA_ROOT / _expected_governance_dir_name(motor_id, motor_name)
    if expected.is_dir():
        return expected
    return None


def _legacy_governance_dirs(motor_id: str, motor_name: str) -> list[Path]:
    suffix = f"_{_motor_suffix(motor_id)}"
    expected_name = _expected_governance_dir_name(motor_id, motor_name)
    matches = [
        path
        for path in GOVERNANZA_ROOT.iterdir()
        if path.is_dir()
        and path.name != "automation-base"
        and path.name.endswith(suffix)
        and path.name != expected_name
    ]
    return sorted(matches, key=lambda item: item.name)


def _governance_state(governance_dir: Path | None) -> dict[str, Any]:
    if governance_dir is None:
        return {
            "governance_dir": None,
            "motor_state_exists": False,
            "motor_name": "",
            "status": "",
            "current_stage": "",
        }
    state_path = governance_dir / "motor_state.json"
    if not state_path.exists():
        return {
            "governance_dir": str(governance_dir.relative_to(REPO_ROOT)),
            "motor_state_exists": False,
            "motor_name": "",
            "status": "",
            "current_stage": "",
        }
    payload = _load_json(state_path)
    return {
        "governance_dir": str(governance_dir.relative_to(REPO_ROOT)),
        "motor_state_exists": True,
        "motor_name": str(payload.get("motor_name", "") or ""),
        "status": str(payload.get("status", "") or ""),
        "current_stage": str(payload.get("current_stage", "") or ""),
    }


def _reconciliation_state(
    *,
    runtime_adapter_present: bool,
    governance_dir_present: bool,
    legacy_governance_present: bool,
    motor_state_exists: bool,
    governance_status: str,
) -> str:
    if runtime_adapter_present and governance_status == "closed":
        return "aligned_closed"
    if runtime_adapter_present and legacy_governance_present and not governance_dir_present:
        return "legacy_governance_identity_mismatch"
    if runtime_adapter_present and (not governance_dir_present or not motor_state_exists or governance_status == "not_started"):
        return "runtime_ahead_of_governance"
    if (not runtime_adapter_present) and governance_status == "closed":
        return "governance_only_closed"
    if runtime_adapter_present and governance_status and governance_status != "closed":
        return "partially_reconciled"
    if runtime_adapter_present:
        return "runtime_present_governance_unknown"
    if governance_dir_present or motor_state_exists:
        return "governance_present_runtime_missing"
    return "not_represented"


def build_snapshot() -> dict[str, Any]:
    dependencies = _load_json(MOTOR_DEPENDENCIES_PATH)
    motors = dict(dependencies.get("motors", {}) or {})
    adapter_files = {path.stem for path in ADAPTERS_DIR.glob("motor_*.py")}

    rows: list[dict[str, Any]] = []
    for motor_id in sorted(motors):
        meta = dict(motors.get(motor_id, {}) or {})
        motor_name = str(meta.get("name", "") or "")
        expected_governance_dir_name = _expected_governance_dir_name(motor_id, motor_name)
        governance_dir = _expected_governance_dir(motor_id, motor_name)
        legacy_governance_dirs = _legacy_governance_dirs(motor_id, motor_name)
        governance_state = _governance_state(governance_dir)
        legacy_governance_states = [_governance_state(path) for path in legacy_governance_dirs]
        runtime_adapter_present = motor_id in adapter_files
        governance_dir_present = governance_dir is not None
        legacy_governance_present = bool(legacy_governance_dirs)
        reconciliation_state = _reconciliation_state(
            runtime_adapter_present=runtime_adapter_present,
            governance_dir_present=governance_dir_present,
            legacy_governance_present=legacy_governance_present,
            motor_state_exists=bool(governance_state["motor_state_exists"]),
            governance_status=governance_state["status"],
        )
        rows.append(
            {
                "motor_id": motor_id,
                "name": motor_name,
                "group": str(meta.get("group", "") or ""),
                "catalog_status": str(meta.get("catalog_status", "") or ""),
                "runtime_adapter_present": runtime_adapter_present,
                "runtime_adapter_path": str((ADAPTERS_DIR / f"{motor_id}.py").relative_to(REPO_ROOT))
                if runtime_adapter_present
                else "",
                "expected_governance_dir": f"governanza/{expected_governance_dir_name}",
                "governance_dir_present": governance_dir_present,
                "governance_dir": governance_state["governance_dir"],
                "legacy_governance_dirs": [
                    str(path.relative_to(REPO_ROOT)) for path in legacy_governance_dirs
                ],
                "legacy_governance_motor_names": [
                    state.get("motor_name", "") for state in legacy_governance_states if state.get("motor_name", "")
                ],
                "motor_state_exists": bool(governance_state["motor_state_exists"]),
                "governance_status": governance_state["status"],
                "governance_stage": governance_state["current_stage"],
                "reconciliation_state": reconciliation_state,
            }
        )

    summary = {
        "catalog_total": len(rows),
        "runtime_adapter_total": sum(1 for row in rows if row["runtime_adapter_present"]),
        "governance_dir_total": sum(1 for row in rows if row["governance_dir_present"]),
        "legacy_governance_dir_total": sum(1 for row in rows if row["legacy_governance_dirs"]),
        "motor_state_total": sum(1 for row in rows if row["motor_state_exists"]),
        "governance_closed_total": sum(1 for row in rows if row["governance_status"] == "closed"),
        "aligned_closed_total": sum(1 for row in rows if row["reconciliation_state"] == "aligned_closed"),
        "runtime_ahead_of_governance_total": sum(1 for row in rows if row["reconciliation_state"] == "runtime_ahead_of_governance"),
        "legacy_governance_identity_mismatch_total": sum(
            1 for row in rows if row["reconciliation_state"] == "legacy_governance_identity_mismatch"
        ),
        "governance_only_closed_total": sum(1 for row in rows if row["reconciliation_state"] == "governance_only_closed"),
        "partially_reconciled_total": sum(1 for row in rows if row["reconciliation_state"] == "partially_reconciled"),
    }
    return {
        "generated_at": _now(),
        "source_files": {
            "motor_dependencies": str(MOTOR_DEPENDENCIES_PATH.relative_to(REPO_ROOT)),
            "adapters_dir": str(ADAPTERS_DIR.relative_to(REPO_ROOT)),
            "governanza_root": str(GOVERNANZA_ROOT.relative_to(REPO_ROOT)),
        },
        "summary": summary,
        "motors": rows,
    }


def _write_markdown(payload: dict[str, Any]) -> None:
    summary = dict(payload.get("summary", {}) or {})
    rows = list(payload.get("motors", []) or [])
    lines = [
        "# Runtime Motor Reconciliation Snapshot",
        "",
        f"Generated at: `{payload.get('generated_at', '')}`",
        "",
        "> This snapshot tracks post-closure documentary reconciliation only.",
        "> It is not evidence that the May 2 DCI runtime closure remains implementation-open.",
        "",
        "## Summary",
        "",
        f"- catalog motors: `{summary.get('catalog_total', 0)}`",
        f"- runtime adapters present: `{summary.get('runtime_adapter_total', 0)}`",
        f"- expected governance dirs present: `{summary.get('governance_dir_total', 0)}`",
        f"- legacy governance dirs conflicting with catalog identity: `{summary.get('legacy_governance_dir_total', 0)}`",
        f"- motor_state files present: `{summary.get('motor_state_total', 0)}`",
        f"- governance closed: `{summary.get('governance_closed_total', 0)}`",
        f"- aligned closed: `{summary.get('aligned_closed_total', 0)}`",
        f"- runtime ahead of governance: `{summary.get('runtime_ahead_of_governance_total', 0)}`",
        f"- legacy governance identity mismatches: `{summary.get('legacy_governance_identity_mismatch_total', 0)}`",
        f"- governance only closed: `{summary.get('governance_only_closed_total', 0)}`",
        f"- partially reconciled: `{summary.get('partially_reconciled_total', 0)}`",
        "",
        "## Legacy Governance Directory Conflicts",
        "",
        "| Motor | Catalog name | Expected governance dir | Legacy governance names on disk | Legacy governance dirs on disk | Current reconciliation state |",
        "|---|---|---|---|---|---|",
    ]
    for row in rows:
        if not row.get("legacy_governance_dirs"):
            continue
        lines.append(
            "| {motor_id} | {name} | {expected_governance_dir} | {legacy_governance_motor_names} | {legacy_governance_dirs} | {reconciliation_state} |".format(
                motor_id=row.get("motor_id", ""),
                name=row.get("name", ""),
                expected_governance_dir=row.get("expected_governance_dir", ""),
                legacy_governance_motor_names=", ".join(row.get("legacy_governance_motor_names", [])) or "missing",
                legacy_governance_dirs=", ".join(row.get("legacy_governance_dirs", [])) or "missing",
                reconciliation_state=row.get("reconciliation_state", ""),
            )
        )
    lines.extend(
        [
            "",
        "## Legacy Governance Identity Mismatches",
        "",
        "| Motor | Catalog name | Expected governance dir | Legacy governance names on disk | Legacy governance dirs on disk | Adapter |",
        "|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        if row.get("reconciliation_state") != "legacy_governance_identity_mismatch":
            continue
        lines.append(
            "| {motor_id} | {name} | {expected_governance_dir} | {legacy_governance_motor_names} | {legacy_governance_dirs} | {runtime_adapter_path} |".format(
                motor_id=row.get("motor_id", ""),
                name=row.get("name", ""),
                expected_governance_dir=row.get("expected_governance_dir", ""),
                legacy_governance_motor_names=", ".join(row.get("legacy_governance_motor_names", [])) or "missing",
                legacy_governance_dirs=", ".join(row.get("legacy_governance_dirs", [])) or "missing",
                runtime_adapter_path=row.get("runtime_adapter_path", ""),
            )
        )
    lines.extend(
        [
            "",
        "## Runtime Ahead Of Governance",
        "",
        "| Motor | Name | Expected governance dir | Governance status | Governance stage | Adapter |",
        "|---|---|---|---|---|---|",
        ]
    )
    for row in rows:
        if row.get("reconciliation_state") != "runtime_ahead_of_governance":
            continue
        lines.append(
            "| {motor_id} | {name} | {expected_governance_dir} | {governance_status} | {governance_stage} | {runtime_adapter_path} |".format(
                motor_id=row.get("motor_id", ""),
                name=row.get("name", ""),
                expected_governance_dir=row.get("expected_governance_dir", ""),
                governance_status=row.get("governance_status", "") or "missing",
                governance_stage=row.get("governance_stage", "") or "missing",
                runtime_adapter_path=row.get("runtime_adapter_path", ""),
            )
        )
    lines.extend(
        [
            "",
            "## Aligned Closed",
            "",
            "| Motor | Name | Governance dir | Adapter |",
            "|---|---|---|---|",
        ]
    )
    for row in rows:
        if row.get("reconciliation_state") != "aligned_closed":
            continue
        lines.append(
            "| {motor_id} | {name} | {governance_dir} | {runtime_adapter_path} |".format(
                motor_id=row.get("motor_id", ""),
                name=row.get("name", ""),
                governance_dir=row.get("governance_dir", "") or "missing",
                runtime_adapter_path=row.get("runtime_adapter_path", ""),
            )
        )
    OUTPUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> None:
    payload = build_snapshot()
    OUTPUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    _write_markdown(payload)
    print(json.dumps(payload.get("summary", {}), ensure_ascii=False))


if __name__ == "__main__":
    main()
