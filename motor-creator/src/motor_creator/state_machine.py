from __future__ import annotations

from datetime import datetime, timezone
from typing import Optional
import uuid

from .models import MotorState, MotorStatus, Stage, STAGE_SEQUENCE


# ─── Validation ────────────────────────────────────────────────────────────

def validate_state(state: MotorState) -> list[str]:
    """
    Check for invalid state combinations from motor_state_semantics.md.
    Returns list of violation descriptions. Empty = valid.
    """
    violations: list[str] = []

    # Rule: status=closed requires current_stage=closed
    if state.status == MotorStatus.CLOSED and state.current_stage != Stage.CLOSED:
        violations.append(
            f"status=closed but current_stage={state.current_stage} (expected 'closed')"
        )

    # Rule: closed → blocked/paused/waiting_on must be clear
    if state.closure.get("is_closed"):
        if state.blocked:
            violations.append("closure.is_closed=true but blocked=true")
        if state.paused:
            violations.append("closure.is_closed=true but paused=true")
        if state.waiting_on is not None:
            violations.append(f"closure.is_closed=true but waiting_on='{state.waiting_on}'")

    # Rule: blocked and paused are mutually exclusive
    if state.blocked and state.paused:
        violations.append("blocked=true and paused=true simultaneously")

    # Rule: status=waiting requires waiting_on to be set
    if state.status == MotorStatus.WAITING and not state.waiting_on:
        violations.append("status=waiting but waiting_on is null")

    # Rule: current_stage must be in stage_sequence or be "closed"
    valid_stages = set(state.stage_sequence) | {Stage.CLOSED.value}
    if state.current_stage not in valid_stages:
        violations.append(f"current_stage='{state.current_stage}' not in stage_sequence")

    return violations


# ─── Stage navigation ──────────────────────────────────────────────────────

def next_stage(current: Stage) -> Optional[Stage]:
    """Return the next stage in the sequence, or None if already at the last."""
    try:
        idx = STAGE_SEQUENCE.index(current)
    except ValueError:
        return None  # 'closed' or unknown
    if idx + 1 < len(STAGE_SEQUENCE):
        return STAGE_SEQUENCE[idx + 1]
    return None  # conformance_review is last; next is closed (handled separately)


def is_final_stage(stage: Stage) -> bool:
    return stage == Stage.CONFORMANCE_REVIEW


# ─── Transition functions ──────────────────────────────────────────────────
# Each returns a modified copy of state (does not mutate in place).

def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _new_validation_id() -> str:
    return f"val_{uuid.uuid4().hex[:8]}"


def _new_correction_id() -> str:
    return f"cor_{uuid.uuid4().hex[:8]}"


def transition_to_in_progress(state: MotorState, reason: str = "") -> MotorState:
    """not_started → in_progress (first activation)."""
    import dataclasses
    return dataclasses.replace(
        state,
        status=MotorStatus.IN_PROGRESS,
        blocked=False,
        paused=False,
        waiting_on=None,
        notes=reason or state.notes,
        updated_at=_now(),
    )


def transition_to_ready(state: MotorState) -> MotorState:
    """in_progress → ready_for_next_stage (gate passed)."""
    import dataclasses
    return dataclasses.replace(
        state,
        status=MotorStatus.READY_FOR_NEXT_STAGE,
        updated_at=_now(),
    )


def advance_to_next_stage(state: MotorState) -> MotorState:
    """ready_for_next_stage → in_progress of next stage."""
    import dataclasses
    current = Stage(state.current_stage)
    nxt = next_stage(current)
    if nxt is None:
        raise ValueError(
            f"advance_to_next_stage called on final stage {current}. Use transition_to_closed."
        )

    completed = list(state.completed_stages)
    if state.current_stage not in completed:
        completed.append(state.current_stage)

    return dataclasses.replace(
        state,
        current_stage=nxt.value,
        completed_stages=completed,
        status=MotorStatus.IN_PROGRESS,
        updated_at=_now(),
    )


def transition_to_closed(state: MotorState) -> MotorState:
    """Conformance review gate passed → motor is closed."""
    import dataclasses
    now = _now()
    completed = list(state.completed_stages)
    if state.current_stage not in completed:
        completed.append(state.current_stage)

    return dataclasses.replace(
        state,
        current_stage=Stage.CLOSED.value,
        completed_stages=completed,
        status=MotorStatus.CLOSED,
        blocked=False,
        paused=False,
        waiting_on=None,
        closure={
            "is_closed": True,
            "closed_at": now,
            "closure_notes": "All 6 gates passed. Conformance review approved.",
        },
        updated_at=now,
    )


def transition_to_blocked(state: MotorState, reason: str) -> MotorState:
    import dataclasses
    validation = {
        "validation_id": _new_validation_id(),
        "stage": state.current_stage,
        "type": "dependency_check",
        "result": "fail",
        "notes": reason,
    }
    return dataclasses.replace(
        state,
        status=MotorStatus.BLOCKED,
        blocked=True,
        paused=False,
        validations=state.validations + [validation],
        updated_at=_now(),
    )


def transition_to_paused(state: MotorState, waiting_on: str) -> MotorState:
    import dataclasses
    return dataclasses.replace(
        state,
        status=MotorStatus.PAUSED,
        paused=True,
        blocked=False,
        waiting_on=waiting_on,
        updated_at=_now(),
    )


def open_correction(
    state: MotorState,
    target_stage: Stage,
    reason: str,
) -> MotorState:
    """
    Revert current_stage to target_stage to fix an inconsistency.
    Registers correction in corrections[].
    Only valid for the 4 correction paths from workflow_rules.md §8.
    """
    import dataclasses
    current = Stage(state.current_stage)

    # Validate correction is a permitted path
    allowed_corrections = {
        Stage.SCHEMA_TECHNICAL: Stage.DOCUMENTATION_BASE,
        Stage.TESTS: Stage.SCHEMA_TECHNICAL,
        Stage.IMPLEMENTATION: Stage.SCHEMA_TECHNICAL,
        Stage.CONFORMANCE_REVIEW: Stage.IMPLEMENTATION,
    }
    allowed_target = allowed_corrections.get(current)
    if allowed_target is None or target_stage != allowed_target:
        raise ValueError(
            f"Correction from {current} to {target_stage} is not a permitted correction path. "
            f"Allowed target for {current}: {allowed_target}"
        )

    correction = {
        "correction_id": _new_correction_id(),
        "from_stage": state.current_stage,
        "to_stage": target_stage.value,
        "reason": reason,
        "status": "open",
    }

    # Remove the target stage and all subsequent stages from completed_stages
    stage_order = [s.value for s in STAGE_SEQUENCE]
    target_idx = stage_order.index(target_stage.value)
    completed = [s for s in state.completed_stages if stage_order.index(s) < target_idx]

    return dataclasses.replace(
        state,
        current_stage=target_stage.value,
        completed_stages=completed,
        status=MotorStatus.IN_PROGRESS,
        blocked=False,
        paused=False,
        corrections=state.corrections + [correction],
        updated_at=_now(),
    )


def record_gate_validation(
    state: MotorState,
    gate_number: int,
    passed: bool,
    failed_conditions: list[str],
) -> MotorState:
    """Append gate evaluation result to validations[]."""
    import dataclasses
    validation = {
        "validation_id": _new_validation_id(),
        "stage": state.current_stage,
        "type": f"gate_{gate_number}",
        "result": "pass" if passed else "fail",
        "notes": "; ".join(failed_conditions) if failed_conditions else "all conditions met",
    }
    return dataclasses.replace(
        state,
        validations=state.validations + [validation],
        updated_at=_now(),
    )
