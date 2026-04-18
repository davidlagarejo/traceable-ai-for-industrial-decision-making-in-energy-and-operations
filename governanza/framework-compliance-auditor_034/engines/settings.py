from __future__ import annotations

from pathlib import Path
from typing import Any


DEFAULT_SETTINGS: dict[str, Any] = {
    "compliance_min_score": 80,
    "quality_min_score": 70,
    "allow_critical_findings": False,
    "max_reaudit_iterations": 3,
}


def load_settings(profile_path: str | Path | None = None) -> dict[str, Any]:
    settings = dict(DEFAULT_SETTINGS)
    if not profile_path:
        return settings
    path = Path(profile_path)
    if not path.exists():
        raise FileNotFoundError(path)
    loaded = _load_mapping(path)
    settings.update(_flatten_settings(loaded))
    return settings


def _load_mapping(path: Path) -> dict[str, Any]:
    if path.suffix.lower() == ".json":
        import json

        return json.loads(path.read_text(encoding="utf-8"))
    try:
        import yaml  # type: ignore

        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        return data or {}
    except Exception:
        return _load_simple_yaml(path)


def _load_simple_yaml(path: Path) -> dict[str, Any]:
    """Tiny fallback parser for the simple profiles shipped with this project."""

    result: dict[str, Any] = {}
    current_parent: str | None = None
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.split("#", 1)[0].rstrip()
        if not line.strip():
            continue
        if not line.startswith(" ") and line.endswith(":"):
            current_parent = line[:-1].strip()
            result[current_parent] = {}
            continue
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        parsed = _parse_scalar(value.strip())
        if raw_line.startswith(" ") and current_parent:
            result.setdefault(current_parent, {})[key.strip()] = parsed
        else:
            result[key.strip()] = parsed
            current_parent = None
    return result


def _parse_scalar(value: str) -> Any:
    if value.lower() in {"true", "false"}:
        return value.lower() == "true"
    try:
        return int(value)
    except ValueError:
        pass
    try:
        return float(value)
    except ValueError:
        pass
    return value.strip('"').strip("'")


def _flatten_settings(data: dict[str, Any]) -> dict[str, Any]:
    flattened: dict[str, Any] = {}
    for key, value in data.items():
        if isinstance(value, dict):
            flattened.update(value)
        else:
            flattened[key] = value
    return flattened

