"""Base class for motor adapters.

Concrete adapters subclass BaseMotorAdapter and implement:
  - motor_id (str property)
  - input_motor_ids (list[str] property)
  - _run_impl(inputs) -> dict

If the motor's Python package is not installed, the adapter falls back to
StubMotorAdapter behaviour automatically via the safe_run() wrapper.
"""
from __future__ import annotations

import logging
from typing import Any

log = logging.getLogger(__name__)


class BaseMotorAdapter:
    """Convenience base; not required by the Protocol but eliminates boilerplate."""

    @property
    def motor_id(self) -> str:
        raise NotImplementedError

    @property
    def input_motor_ids(self) -> list[str]:
        return []

    def run(self, inputs: dict[str, Any]) -> dict[str, Any]:
        try:
            return self._run_impl(inputs)
        except ImportError as exc:
            log.warning(
                "%s: motor package not installed (%s) — running as stub", self.motor_id, exc
            )
            return _stub_output(self.motor_id, inputs, reason=str(exc))
        except Exception:
            raise

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        raise NotImplementedError


def _stub_output(motor_id: str, inputs: dict[str, Any], reason: str = "") -> dict[str, Any]:
    return {
        "__stub__": True,
        "motor_id": motor_id,
        "input_motor_ids_received": [k for k in inputs if not k.startswith("__")],
        "reason": reason or "not implemented",
    }
