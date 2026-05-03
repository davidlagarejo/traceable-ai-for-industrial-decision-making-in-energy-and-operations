"""Motor Registry — Layer 3.

Maps motor_id → MotorAdapter instance.
Hot-swap: replace a registered adapter and the next pipeline run uses it.
"""
from __future__ import annotations

from typing import Any, Protocol, runtime_checkable


@runtime_checkable
class MotorAdapter(Protocol):
    """Contract every motor adapter must satisfy."""

    @property
    def motor_id(self) -> str:
        """The motor this adapter drives, e.g. 'motor_004'."""
        ...

    @property
    def input_motor_ids(self) -> list[str]:
        """motor_ids whose outputs this adapter needs as inputs."""
        ...

    def run(self, inputs: dict[str, dict[str, Any]]) -> dict[str, Any]:
        """Execute the motor.

        Args:
            inputs: keyed by motor_id, each value is that motor's output dict.
                    Also contains the special key '__pipeline__' with the
                    original pipeline inputs (raw data injected at run-time).

        Returns:
            Output dict that will be stored in the ArtifactStore.
        """
        ...


class MotorRegistry:
    def __init__(self) -> None:
        self._adapters: dict[str, MotorAdapter] = {}

    def register(self, adapter: MotorAdapter) -> None:
        if not isinstance(adapter, MotorAdapter):
            raise TypeError(f"{adapter!r} does not implement MotorAdapter protocol")
        self._adapters[adapter.motor_id] = adapter

    def register_many(self, adapters: list[MotorAdapter]) -> None:
        for a in adapters:
            self.register(a)

    def get(self, motor_id: str) -> MotorAdapter | None:
        return self._adapters.get(motor_id)

    def is_registered(self, motor_id: str) -> bool:
        return motor_id in self._adapters

    def all_motor_ids(self) -> list[str]:
        return sorted(self._adapters.keys())

    def __repr__(self) -> str:
        names = ", ".join(self.all_motor_ids())
        return f"MotorRegistry([{names}])"
