"""Governance-stage implementation wrapper for motor_043."""

from __future__ import annotations

from collections.abc import Mapping
from pathlib import Path
import sys
from typing import Any


def _runtime_src() -> Path:
    return Path(__file__).resolve().parents[5] / "runtime-orchestrator" / "src"


def _ensure_runtime_import_path() -> None:
    runtime_src = _runtime_src()
    runtime_src_text = str(runtime_src)
    if runtime_src_text not in sys.path:
        sys.path.insert(0, runtime_src_text)


class CompetitiveComparisonEngine:
    """Thin deterministic wrapper around `Motor043Adapter`."""

    def __init__(self) -> None:
        _ensure_runtime_import_path()
        from runtime_orchestrator.adapters.motor_043 import Motor043Adapter

        self._adapter = Motor043Adapter()

    def run(self, inputs: Mapping[str, Any]) -> dict[str, Any]:
        if not isinstance(inputs, Mapping):
            raise TypeError("motor_043 inputs must be a mapping keyed by upstream motor ids")
        return self._adapter.run(dict(inputs))


def run_competitive_comparison_engine(inputs: Mapping[str, Any]) -> dict[str, Any]:
    return CompetitiveComparisonEngine().run(inputs)
