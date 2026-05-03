from __future__ import annotations

from .models import DependencyCheckResult, MotorEntry, MotorState, MotorStatus


def detect_cycles(motors: dict[str, MotorEntry]) -> list[str]:
    """
    Kahn's algorithm cycle detection.
    Returns list of motor IDs involved in cycles, or empty list if none.
    The orchestrator MUST abort if this returns non-empty.
    """
    in_degree: dict[str, int] = {m: 0 for m in motors}
    adj: dict[str, list[str]] = {m: [] for m in motors}

    for motor_id, entry in motors.items():
        for req in entry.requires:
            if req in motors:
                adj[req].append(motor_id)
                in_degree[motor_id] += 1

    queue = [m for m in in_degree if in_degree[m] == 0]
    visited = 0

    while queue:
        node = queue.pop(0)
        visited += 1
        for neighbor in adj[node]:
            in_degree[neighbor] -= 1
            if in_degree[neighbor] == 0:
                queue.append(neighbor)

    if visited != len(motors):
        return [m for m in in_degree if in_degree[m] > 0]
    return []


def check_motor_eligible(
    motor_entry: MotorEntry,
    all_states: dict[str, MotorState],
) -> DependencyCheckResult:
    """
    Check if a motor can be started (not_started → in_progress).

    Rules:
    1. Group C motors with orchestrator_eligible=False are never eligible.
    2. All motors in requires[] must have status=closed.
    """
    if motor_entry.is_group_c and not motor_entry.orchestrator_eligible:
        return DependencyCheckResult(
            motor_id=motor_entry.motor_id,
            eligible=False,
            reason=(
                f"Motor {motor_entry.motor_id} is Group C with orchestrator_eligible=false. "
                "Manual promotion required via motor_dependencies.json edit."
            ),
        )

    missing: list[str] = []
    for req_id in motor_entry.requires:
        req_state = all_states.get(req_id)
        if req_state is None:
            missing.append(f"{req_id} (no state file)")
            continue
        if req_state.status != MotorStatus.CLOSED:
            missing.append(f"{req_id} (status={req_state.status}, expected=closed)")

    if missing:
        return DependencyCheckResult(
            motor_id=motor_entry.motor_id,
            eligible=False,
            missing_deps=missing,
            reason=f"Unmet dependencies: {', '.join(missing)}",
        )

    return DependencyCheckResult(
        motor_id=motor_entry.motor_id,
        eligible=True,
    )


def get_eligible_motors(
    motors: dict[str, MotorEntry],
    all_states: dict[str, MotorState],
) -> list[tuple[MotorEntry, MotorState]]:
    """
    Return motors that are eligible for orchestrator processing,
    ordered by number of dependencies (topological preference).

    Eligible = dependencies satisfied AND not Group C blocked AND
               status in (not_started, in_progress, ready_for_next_stage).
    """
    eligible: list[tuple[MotorEntry, MotorState]] = []
    actionable_statuses = {
        MotorStatus.NOT_STARTED,
        MotorStatus.IN_PROGRESS,
        MotorStatus.READY_FOR_NEXT_STAGE,
    }

    for motor_id, entry in motors.items():
        state = all_states.get(motor_id)
        if state is None:
            continue
        if state.status not in actionable_statuses:
            continue
        result = check_motor_eligible(entry, all_states)
        if result.eligible:
            eligible.append((entry, state))

    # Sort: prefer motors already in_progress, then by fewest dependencies
    def sort_key(pair: tuple[MotorEntry, MotorState]) -> tuple[int, int]:
        entry, state = pair
        in_progress_priority = 0 if state.status == MotorStatus.IN_PROGRESS else 1
        return (in_progress_priority, len(entry.requires))

    eligible.sort(key=sort_key)
    return eligible
