from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from .schema import (
    RegistryValidationError,
    validate_combination_spec,
    validate_memory_policy_record,
    validate_pattern_spec,
    validate_source_basis_record,
    validate_validator_spec,
)


def default_registry_root() -> Path:
    return Path(__file__).resolve().parents[3] / "zlab_skill" / "registry"


def _load_json_documents(directory: Path) -> list[dict[str, Any]]:
    if not directory.exists():
        return []
    rows: list[dict[str, Any]] = []
    for path in sorted(directory.glob("*.json")):
        payload = json.loads(path.read_text(encoding="utf-8"))
        if not isinstance(payload, dict):
            raise RegistryValidationError(f"Registry document must be a JSON object: {path}")
        payload["__path__"] = str(path)
        rows.append(payload)
    return rows


def load_source_basis_records(root: Path | None = None) -> list[dict[str, Any]]:
    registry_root = root or default_registry_root()
    rows = []
    for payload in _load_json_documents(registry_root / "source_basis"):
        rows.append(validate_source_basis_record(payload))
    return rows


def load_pattern_specs(root: Path | None = None) -> list[dict[str, Any]]:
    registry_root = root or default_registry_root()
    rows = []
    for payload in _load_json_documents(registry_root / "patterns"):
        rows.append(validate_pattern_spec(payload))
    return rows


def load_combination_specs(root: Path | None = None) -> list[dict[str, Any]]:
    registry_root = root or default_registry_root()
    rows = []
    for payload in _load_json_documents(registry_root / "combinations"):
        rows.append(validate_combination_spec(payload))
    return rows


def load_validator_specs(root: Path | None = None) -> list[dict[str, Any]]:
    registry_root = root or default_registry_root()
    rows = []
    for payload in _load_json_documents(registry_root / "validators"):
        rows.append(validate_validator_spec(payload))
    return rows


def load_memory_policy_records(root: Path | None = None) -> list[dict[str, Any]]:
    registry_root = root or default_registry_root()
    rows = []
    for payload in _load_json_documents(registry_root / "memory_policies"):
        rows.append(validate_memory_policy_record(payload))
    return rows


def load_registry_bundle(root: Path | None = None) -> dict[str, Any]:
    registry_root = root or default_registry_root()
    source_basis = load_source_basis_records(registry_root)
    patterns = load_pattern_specs(registry_root)
    combinations = load_combination_specs(registry_root)
    validators = load_validator_specs(registry_root)
    memory_policies = load_memory_policy_records(registry_root)

    source_basis_by_id = {row["id"]: row for row in source_basis}
    if len(source_basis_by_id) != len(source_basis):
        raise RegistryValidationError("Duplicate source-basis ids detected in registry")

    patterns_by_id = {row["id"]: row for row in patterns}
    if len(patterns_by_id) != len(patterns):
        raise RegistryValidationError("Duplicate pattern ids detected in registry")

    combinations_by_id = {row["id"]: row for row in combinations}
    if len(combinations_by_id) != len(combinations):
        raise RegistryValidationError("Duplicate combination ids detected in registry")
    validators_by_id = {row["id"]: row for row in validators}
    if len(validators_by_id) != len(validators):
        raise RegistryValidationError("Duplicate validator ids detected in registry")
    memory_policies_by_id = {row["id"]: row for row in memory_policies}
    if len(memory_policies_by_id) != len(memory_policies):
        raise RegistryValidationError("Duplicate memory policy ids detected in registry")

    for row in patterns:
        unknown = sorted(set(row.get("source_basis", [])).difference(source_basis_by_id))
        if unknown:
            raise RegistryValidationError(
                f"Pattern {row['id']} references unknown source_basis ids: {', '.join(unknown)}"
            )

    for row in combinations:
        unknown_patterns = sorted(set(row.get("pattern_ids", [])).difference(patterns_by_id))
        if unknown_patterns:
            raise RegistryValidationError(
                f"Combination {row['id']} references unknown pattern ids: {', '.join(unknown_patterns)}"
            )
        unknown_sources = sorted(set(row.get("source_basis", [])).difference(source_basis_by_id))
        if unknown_sources:
            raise RegistryValidationError(
                f"Combination {row['id']} references unknown source_basis ids: {', '.join(unknown_sources)}"
            )

    return {
        "root": str(registry_root),
        "patterns": patterns,
        "patterns_by_id": patterns_by_id,
        "combinations": combinations,
        "combinations_by_id": combinations_by_id,
        "source_basis": source_basis,
        "source_basis_by_id": source_basis_by_id,
        "validators": validators,
        "validators_by_id": validators_by_id,
        "memory_policies": memory_policies,
        "memory_policies_by_id": memory_policies_by_id,
        "counts": {
            "patterns": len(patterns),
            "combinations": len(combinations),
            "source_basis": len(source_basis),
            "validators": len(validators),
            "memory_policies": len(memory_policies),
        },
    }
