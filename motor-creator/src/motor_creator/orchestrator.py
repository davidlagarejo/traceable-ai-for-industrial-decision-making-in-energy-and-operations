from __future__ import annotations

from pathlib import Path
from typing import Optional

from .artifact_manager import check_all_artifacts, create_stage_placeholders
from .config import GOVERNANZA, MOTOR_DEPENDENCIES_FILE
from .task_generator import generate_task, get_task_path
from .dependency_checker import (
    check_motor_eligible,
    detect_cycles,
    get_eligible_motors,
)
from .event_log import EventType, append_event
from .gate_checker import evaluate_current_gate
from .loader import (
    get_or_init_state,
    load_all_states,
    load_motor_dependencies,
    motor_dir,
)
from .models import MotorEntry, MotorState, MotorStatus, OrchestratorResult, Stage
from .state_machine import (
    advance_to_next_stage,
    is_final_stage,
    open_correction,
    record_gate_validation,
    transition_to_blocked,
    transition_to_closed,
    transition_to_in_progress,
    transition_to_paused,
    transition_to_ready,
    validate_state,
)
from .state_writer import get_motor_dir, write_motor_state


class Orchestrator:
    def __init__(
        self,
        governanza: Path = GOVERNANZA,
        dependencies_file: Path = MOTOR_DEPENDENCIES_FILE,
        dry_run: bool = False,
        auto_approve_gates: bool = False,
    ):
        self.governanza = governanza
        self.dry_run = dry_run
        self.auto_approve_gates = auto_approve_gates
        self.motors = load_motor_dependencies(dependencies_file)

    def _log(self, event_type: EventType, motor_id: str, **payload) -> None:
        append_event(event_type, motor_id, payload, dry_run=self.dry_run)

    def _write(self, entry: MotorEntry, state: MotorState) -> None:
        write_motor_state(entry, state, self.governanza, dry_run=self.dry_run)
        self._log(EventType.STATE_WRITTEN, entry.motor_id, stage=state.current_stage, status=state.status)

    def startup_checks(self) -> bool:
        """
        Run mandatory startup checks.
        Returns False and logs abort if any check fails.
        """
        self._log(EventType.ORCHESTRATOR_START, "system", dry_run=self.dry_run)

        cycles = detect_cycles(self.motors)
        if cycles:
            self._log(
                EventType.CYCLE_DETECTED,
                "system",
                motors_in_cycle=cycles,
            )
            self._log(
                EventType.ORCHESTRATOR_ABORT,
                "system",
                reason=f"Cycle detected in dependency graph: {cycles}",
            )
            print(f"[ABORT] Cycle detected in dependency graph: {cycles}")
            print("Fix motor_dependencies.json before running the orchestrator.")
            return False
        return True

    def run_one(self, motor_id: str) -> OrchestratorResult:
        """Process a single motor by ID."""
        if not self.startup_checks():
            return OrchestratorResult(
                motor_id=motor_id,
                action="error",
                from_stage=None,
                to_stage=None,
                reason="Startup checks failed (cycle detected)",
            )

        entry = self.motors.get(motor_id)
        if entry is None:
            return OrchestratorResult(
                motor_id=motor_id,
                action="error",
                from_stage=None,
                to_stage=None,
                reason=f"Motor {motor_id} not found in motor_dependencies.json",
            )

        all_states = load_all_states(self.motors, self.governanza)
        return self._process_motor(entry, all_states)

    def run_next(self) -> Optional[OrchestratorResult]:
        """
        Select and process the next eligible motor.
        Returns None if no motor is eligible.
        """
        if not self.startup_checks():
            return OrchestratorResult(
                motor_id="system",
                action="error",
                from_stage=None,
                to_stage=None,
                reason="Startup checks failed",
            )

        all_states = load_all_states(self.motors, self.governanza)
        eligible = get_eligible_motors(self.motors, all_states)

        if not eligible:
            print("[INFO] No eligible motors to process.")
            return None

        entry, _ = eligible[0]
        self._log(EventType.MOTOR_SELECTED, entry.motor_id, slug=entry.slug)
        return self._process_motor(entry, all_states)

    def run_all(self) -> list[OrchestratorResult]:
        """
        Process all eligible motors in topological order.
        Stops after first error but collects all results.
        """
        if not self.startup_checks():
            return []

        all_states = load_all_states(self.motors, self.governanza)
        eligible = get_eligible_motors(self.motors, all_states)
        results: list[OrchestratorResult] = []

        for entry, _ in eligible:
            # Reload states after each motor to pick up changes
            all_states = load_all_states(self.motors, self.governanza)
            self._log(EventType.MOTOR_SELECTED, entry.motor_id, slug=entry.slug)
            result = self._process_motor(entry, all_states)
            results.append(result)
            if result.action == "error":
                break

        return results

    def run_until_done(self, max_rounds: int = 200, interval: float = 0.0) -> dict:
        """
        Loop run_all() until no further progress is made or all motors are closed.
        Returns a summary dict with total_rounds, closed, blocked, paused, errors.
        Safe to interrupt (Ctrl+C): state is always persisted to disk before each pause.
        """
        import time

        if not self.startup_checks():
            return {"error": "startup_checks_failed", "rounds": 0}

        total_rounds = 0
        total_results: list[OrchestratorResult] = []

        while total_rounds < max_rounds:
            total_rounds += 1
            all_states = load_all_states(self.motors, self.governanza)
            eligible = get_eligible_motors(self.motors, all_states)

            if not eligible:
                break  # Nothing left to process

            round_results: list[OrchestratorResult] = []
            progress_made = False

            for entry, _ in eligible:
                all_states = load_all_states(self.motors, self.governanza)
                result = self._process_motor(entry, all_states)
                round_results.append(result)
                total_results.append(result)

                if result.action in ("advanced", "closed"):
                    progress_made = True
                if result.action == "error":
                    progress_made = False
                    break

            if not progress_made:
                break  # All remaining motors are blocked/paused — nothing to do

            if interval > 0:
                time.sleep(interval)

        # Build summary
        final_states = load_all_states(self.motors, self.governanza)
        counts: dict[str, int] = {
            "closed": 0, "in_progress": 0, "not_started": 0,
            "blocked": 0, "paused": 0,
        }
        for motor_id, entry in self.motors.items():
            if not entry.orchestrator_eligible:
                continue
            s = final_states.get(motor_id)
            if s is None:
                counts["not_started"] += 1
                continue
            if s.status == MotorStatus.CLOSED:
                counts["closed"] += 1
            elif s.blocked:
                counts["blocked"] += 1
            elif s.paused:
                counts["paused"] += 1
            elif s.status == MotorStatus.IN_PROGRESS:
                counts["in_progress"] += 1
            else:
                counts["not_started"] += 1

        return {
            "rounds": total_rounds,
            "total_actions": len(total_results),
            **counts,
        }

    def _process_motor(
        self,
        entry: MotorEntry,
        all_states: dict[str, MotorState],
    ) -> OrchestratorResult:
        """Core processing logic for a single motor."""
        m_dir = get_motor_dir(entry, self.governanza)
        state = get_or_init_state(entry, self.governanza)
        from_stage = state.current_stage

        # ── 1. Validate current state ──────────────────────────────────────
        violations = validate_state(state)
        if violations:
            reason = f"Invalid state detected: {'; '.join(violations)}"
            self._log(EventType.ERROR, entry.motor_id, violations=violations)
            state = transition_to_blocked(state, reason)
            self._write(entry, state)
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="blocked",
                from_stage=from_stage,
                to_stage=state.current_stage,
                reason=reason,
            )

        # ── 2. Already closed ──────────────────────────────────────────────
        if state.status == MotorStatus.CLOSED:
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="skipped",
                from_stage=from_stage,
                to_stage=from_stage,
                reason="Motor is already closed.",
            )

        # ── 3. Blocked / paused / waiting ──────────────────────────────────
        if state.blocked or state.paused or state.waiting_on:
            reason = (
                f"blocked={state.blocked}, paused={state.paused}, "
                f"waiting_on={state.waiting_on}"
            )
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="skipped",
                from_stage=from_stage,
                to_stage=from_stage,
                reason=f"Motor is halted: {reason}",
            )

        # ── 4. Check dependencies ──────────────────────────────────────────
        dep_result = check_motor_eligible(entry, all_states)
        if not dep_result.eligible:
            self._log(
                EventType.DEPENDENCY_CHECK_FAIL,
                entry.motor_id,
                reason=dep_result.reason,
                missing=dep_result.missing_deps,
            )
            if state.status == MotorStatus.NOT_STARTED:
                state = transition_to_blocked(state, dep_result.reason)
                self._write(entry, state)
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="blocked",
                from_stage=from_stage,
                to_stage=state.current_stage,
                reason=dep_result.reason,
            )
        self._log(EventType.DEPENDENCY_CHECK_PASS, entry.motor_id)

        # ── 5. Activate motor if not started ──────────────────────────────
        if state.status == MotorStatus.NOT_STARTED:
            state = transition_to_in_progress(state, "Dependencies satisfied. Motor activated.")
            self._write(entry, state)
            self._log(EventType.STAGE_ADVANCED, entry.motor_id, to_stage=state.current_stage)

        # ── 6. Create placeholders for current stage ───────────────────────
        current_stage = Stage(state.current_stage)
        artifacts_created: list[str] = []

        created = create_stage_placeholders(m_dir, current_stage, entry, self.dry_run)
        for p in created:
            artifacts_created.append(p.name)
            self._log(EventType.ARTIFACT_CREATED, entry.motor_id, artifact=str(p))

        # ── 7. Evaluate gate ───────────────────────────────────────────────
        gate_result = evaluate_current_gate(m_dir, current_stage)
        if gate_result is None:
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="skipped",
                from_stage=from_stage,
                to_stage=from_stage,
                reason="Motor is at 'closed' stage, no gate to evaluate.",
            )

        # Record gate evaluation in validations
        state = record_gate_validation(
            state, gate_result.gate_number, gate_result.passed, gate_result.failed_conditions
        )

        self._log(
            EventType.GATE_EVALUATED,
            entry.motor_id,
            gate=gate_result.gate_number,
            passed=gate_result.passed,
            failed=gate_result.failed_conditions,
        )

        # ── 8. Handle gate failure — generate Codex task ──────────────────
        if not gate_result.passed:
            self._log(
                EventType.GATE_FAILED,
                entry.motor_id,
                gate=gate_result.gate_number,
                conditions=gate_result.failed_conditions,
            )

            # Generate a Codex task file describing exactly what needs to be done
            task_path = None
            if not self.dry_run:
                try:
                    generate_task(entry, gate_result, m_dir, write_to_file=True)
                    task_path = get_task_path(entry.motor_id, current_stage)
                except Exception as exc:
                    print(f"[WARN] Task generation failed: {exc}")

            self._write(entry, state)
            reason = (
                f"Gate {gate_result.gate_number} failed: "
                + "; ".join(gate_result.failed_conditions)
            )
            if task_path:
                reason += f"\nCodex task written to: {task_path}"

            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="blocked",
                from_stage=from_stage,
                to_stage=current_stage.value,
                reason=reason,
                artifacts_created=artifacts_created,
            )

        # ── 9. Handle manual checks pending ──────────────────────────────
        if gate_result.is_blocked_by_manual and not self.auto_approve_gates:
            self._log(
                EventType.GATE_MANUAL_PENDING,
                entry.motor_id,
                gate=gate_result.gate_number,
                checks=gate_result.manual_checks_pending,
            )
            state = transition_to_paused(
                state,
                waiting_on=f"manual_approval:gate_{gate_result.gate_number}",
            )
            self._write(entry, state)
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="paused",
                from_stage=from_stage,
                to_stage=current_stage.value,
                reason=(
                    f"Gate {gate_result.gate_number} needs manual approval: "
                    + "; ".join(gate_result.manual_checks_pending)
                ),
                artifacts_created=artifacts_created,
            )

        if gate_result.is_blocked_by_manual and self.auto_approve_gates:
            self._log(
                EventType.MANUAL_APPROVED,
                entry.motor_id,
                gate=f"gate_{gate_result.gate_number}",
                auto=True,
                checks=gate_result.manual_checks_pending,
            )

        # ── 10. Gate passed — advance ─────────────────────────────────────
        self._log(EventType.GATE_PASSED, entry.motor_id, gate=gate_result.gate_number)
        state = transition_to_ready(state)

        if is_final_stage(current_stage):
            # conformance_review passed → close motor
            state = transition_to_closed(state)
            self._write(entry, state)
            self._log(EventType.MOTOR_CLOSED, entry.motor_id)
            return OrchestratorResult(
                motor_id=entry.motor_id,
                action="closed",
                from_stage=from_stage,
                to_stage=Stage.CLOSED.value,
                reason="All 6 gates passed. Conformance review approved.",
                artifacts_created=artifacts_created,
            )

        # Advance to next stage
        state = advance_to_next_stage(state)
        self._write(entry, state)
        self._log(
            EventType.STAGE_ADVANCED,
            entry.motor_id,
            from_stage=from_stage,
            to_stage=state.current_stage,
        )

        return OrchestratorResult(
            motor_id=entry.motor_id,
            action="advanced",
            from_stage=from_stage,
            to_stage=state.current_stage,
            reason=f"Gate {gate_result.gate_number} passed.",
            artifacts_created=artifacts_created,
        )

    def open_correction_for_motor(
        self,
        motor_id: str,
        target_stage: Stage,
        reason: str,
    ) -> OrchestratorResult:
        """
        Open a correction loop: revert motor to target_stage.
        Only valid for the 4 permitted correction paths.
        """
        entry = self.motors.get(motor_id)
        if entry is None:
            return OrchestratorResult(
                motor_id=motor_id,
                action="error",
                from_stage=None,
                to_stage=None,
                reason=f"Motor {motor_id} not found",
            )

        state = get_or_init_state(entry, self.governanza)
        from_stage = state.current_stage

        try:
            state = open_correction(state, target_stage, reason)
        except ValueError as e:
            return OrchestratorResult(
                motor_id=motor_id,
                action="error",
                from_stage=from_stage,
                to_stage=None,
                reason=str(e),
            )

        self._write(entry, state)
        self._log(
            EventType.CORRECTION_OPENED,
            motor_id,
            from_stage=from_stage,
            to_stage=target_stage.value,
            reason=reason,
        )
        return OrchestratorResult(
            motor_id=motor_id,
            action="correction",
            from_stage=from_stage,
            to_stage=target_stage.value,
            reason=reason,
        )

    def approve_manual_gate(self, motor_id: str, gate_name: str) -> OrchestratorResult:
        """
        Mark a manual_check gate as approved, unblocking the motor.
        """
        entry = self.motors.get(motor_id)
        if entry is None:
            return OrchestratorResult(
                motor_id=motor_id,
                action="error",
                from_stage=None,
                to_stage=None,
                reason=f"Motor {motor_id} not found",
            )

        state = get_or_init_state(entry, self.governanza)
        if state.waiting_on != f"manual_approval:{gate_name}":
            return OrchestratorResult(
                motor_id=motor_id,
                action="error",
                from_stage=state.current_stage,
                to_stage=state.current_stage,
                reason=(
                    f"Motor is not waiting on manual_approval:{gate_name}. "
                    f"waiting_on={state.waiting_on}"
                ),
            )

        import dataclasses
        from datetime import datetime, timezone
        state = dataclasses.replace(
            state,
            status=MotorStatus.IN_PROGRESS,
            paused=False,
            waiting_on=None,
            updated_at=datetime.now(timezone.utc).isoformat(),
        )
        self._write(entry, state)
        self._log(
            EventType.MANUAL_APPROVED,
            motor_id,
            gate=gate_name,
        )
        return OrchestratorResult(
            motor_id=motor_id,
            action="approved",
            from_stage=state.current_stage,
            to_stage=state.current_stage,
            reason=f"Manual approval granted for {gate_name}. Motor returned to in_progress.",
        )

    def status(self) -> list[dict]:
        """Return a summary of all motors and their current status."""
        all_states = load_all_states(self.motors, self.governanza)
        summary: list[dict] = []
        for motor_id, entry in self.motors.items():
            state = all_states.get(motor_id)
            if state is None:
                continue
            summary.append({
                "motor_id": motor_id,
                "name": entry.name,
                "group": entry.group,
                "status": state.status,
                "current_stage": state.current_stage,
                "completed_stages": len(state.completed_stages),
                "missing_artifacts": len(state.missing_artifacts),
                "blocked": state.blocked,
                "paused": state.paused,
                "waiting_on": state.waiting_on,
                "orchestrator_eligible": entry.orchestrator_eligible,
            })
        return summary
