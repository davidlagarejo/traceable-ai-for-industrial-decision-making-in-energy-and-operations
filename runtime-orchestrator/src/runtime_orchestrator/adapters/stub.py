"""StubMotorAdapter — passthrough for motors not yet implemented.

Used for motors_008-033. Passes through all inputs and marks output
with __stub__=True so the orchestrator can report COMPLETED_WITH_STUBS.
"""
from __future__ import annotations

from typing import Any

from .base import BaseMotorAdapter, _stub_output


class StubMotorAdapter(BaseMotorAdapter):
    def __init__(self, motor_id: str, input_motor_ids: list[str]) -> None:
        self._motor_id = motor_id
        self._input_motor_ids = input_motor_ids

    @property
    def motor_id(self) -> str:
        return self._motor_id

    @property
    def input_motor_ids(self) -> list[str]:
        return self._input_motor_ids

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        return _stub_output(self._motor_id, inputs)
