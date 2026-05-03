"""
task_generator.py — Generates precise Codex task instructions when a motor is blocked.

Architecture:
- The orchestrator detects what is blocked and WHY (gate conditions).
- This module converts that blockage into a CODEX TASK: a structured, actionable
  instruction file that Codex reads and executes.
- Codex edits files, writes code, fills artifacts.
- After Codex completes the task, it re-runs the orchestrator to advance the motor.

Task files are written to runtime/tasks/{motor_id}_{stage}.task.md
They are overwritten each time the motor is processed (always current).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

from .config import MOTOR_CONTEXT_REGISTRY_FILE, RUNTIME_DIR
from .models import GateResult, MotorEntry, Stage


# ─── Context loader ───────────────────────────────────────────────────────────

def _load_ctx(motor_id: str) -> dict:
    try:
        data = json.loads(MOTOR_CONTEXT_REGISTRY_FILE.read_text(encoding="utf-8"))
        return data.get("motors", {}).get(motor_id, {})
    except Exception:
        return {}


def _read_artifact(p: Path) -> str:
    """Read artifact content, return empty string if missing."""
    if not p.is_file():
        return ""
    return p.read_text(encoding="utf-8", errors="ignore")


# ─── Section-level guidance per artifact ─────────────────────────────────────

def _section_guidance(artifact_name: str, ctx: dict) -> str:
    """Return section-by-section writing guidance for a given artifact."""

    purpose = ctx.get("purpose", "")
    key_inputs = ctx.get("key_inputs", [])
    key_outputs = ctx.get("key_outputs", [])
    key_objects = ctx.get("key_objects", [])
    what_not_to_do = ctx.get("what_not_to_do", "")
    design_notes = ctx.get("design_notes", "")
    epistemic = ctx.get("epistemic_flags", [])

    guides = {
        "master_concept_doc": f"""\
### ## purpose
Write 2–4 sentences describing exactly what this motor does.
Base it on: "{purpose}"

### ## what_it_does
List the concrete actions this motor takes. Each item = one specific operation.
Example items: receives X, validates Y, produces Z, records W.

### ## what_it_does_not_do
List at least 3 explicit boundaries. What responsibility does NOT belong here.
{f'Specifically exclude: {what_not_to_do}' if what_not_to_do else ''}

### ## why_it_exists
1–2 sentences on why this is a separate motor and not part of another.
{f'Design rationale: {design_notes}' if design_notes else ''}""",

        "functional_contract": f"""\
### ## inputs
List each input on its own line: `name: type — source motor or origin`
{f'Known inputs: {chr(10).join("- " + i for i in key_inputs)}' if key_inputs else ''}

### ## outputs
List each output on its own line: `name: type — destination or consumer`
{f'Known outputs: {chr(10).join("- " + o for o in key_outputs)}' if key_outputs else ''}

### ## limits
At least 3 strict limits. What this motor never accepts and never produces.
{f'Known boundary: {what_not_to_do}' if what_not_to_do else ''}

### ## validations
Rules the motor enforces before processing and before emitting output.
E.g.: "rejects input if field X is null", "output always has field Y".""",

        "conceptual_schema": f"""\
### ## entities
Name each domain object this motor creates or transforms.
{f'Known objects: {", ".join(key_objects)}' if key_objects else ''}
For each: 1 line with name and what it represents.

### ## relationships
How entities relate to each other. Format: A → B (reason).

### ## key_fields
For each entity, list 3–5 minimum required fields with their types.""",

        "operational_rules": f"""\
### ## rules
Number each rule. Each rule = a condition that must ALWAYS hold.
At least 4 rules. Be specific and verifiable.

### ## invariants
Conditions true before AND after every operation. E.g.: "lineage_id is never null after create".

### ## forbidden_operations
List operations this motor is EXPLICITLY prohibited from executing.
{f'Start from: {what_not_to_do}' if what_not_to_do else ''}""",

        "acceptance_tests": f"""\
### ## happy_path
Describe: input → action → expected output. Use concrete values.

### ## edge_cases
At least 2 cases. Each: what extreme input, what correct behavior.

### ## rejection_criteria
At least 2 conditions where the motor returns an error instead of an output.
Specify what error signal is emitted.""",

        "failure_modes": f"""\
### ## failure_modes_list
At least 3 failure modes. Format: `MODE_NAME: symptom description`.

### ## anti_patterns
At least 2 patterns of wrong usage that damage this motor.

### ## degradation_signals
Observable signals (metrics, log entries, output patterns) that indicate the motor is degrading silently.""",

        "design_done_criteria": f"""\
### ## criteria
At least 4 items. Each must be a verifiable condition, not a vague goal.
Example: "functional_contract.md has no [PENDIENTE] markers"
Example: "technical_schema.json validates against motor_schema.json"
Format as markdown list items starting with `-`.""",

        "technical_schema": f"""\
### ## entities
For each entity: name, description, and what stage it lives in.
{f'Start from: {", ".join(key_objects)}' if key_objects else ''}

### ## fields
For each entity list every field: `field_name: type — description`
Mark required fields with `(required)`.

### ## relationships
Technical FK or reference relationships between entities.

### ## identifiers
The stable ID field for each entity. Convention: `{{motor_id}}_id` or `record_id`.

### ## versioning
Required fields: version_id, created_at, updated_at, version_hash.

### ## lineage
Required fields: source_ref, produced_by_motor, produced_at, parent_id.""",

        "test_spec": f"""\
### ## happy_path
Minimum valid input + expected output. Be concrete with field names and values.

### ## sparse_case
Input with optional fields missing. Motor should handle gracefully without fatal error.

### ## malformed_input
Input with wrong types or missing required fields. Motor must reject with specific error.

### ## edge_cases
At least 2: describe the extreme condition and the correct behavior.

### ## pass_criteria
Observable condition that means the test passed. E.g.: "output has field X with value Y".

### ## fail_criteria
Observable condition that means the test failed. E.g.: "exception raised" or "field Z is null".""",

        "failure_modes_spec": f"""\
### ## failure_modes_list
Technical list. Format: `FAILURE_ID: trigger condition → observable symptom → recovery path`
At least 3 modes.

### ## anti_patterns
Architectural or design patterns that break this motor. E.g.: "coupling output to motor_XXX directly".

### ## degradation_signals
Technical metrics or log patterns that indicate degradation before total failure.

### ## expensive_errors
Errors that are cheap to prevent but expensive to fix after they propagate.
For each: why it's expensive and what prevents it.""",

        "usage_example": f"""\
### ## example
A concrete scenario: who calls this motor, with what input, expecting what result.
2–3 sentences.

### ## inputs_used
The exact input structure. Use pseudo-JSON or field list with example values.

### ## expected_output
The exact output structure. Same format as inputs_used.

### ## notes
Any preconditions, caveats, or important context for this specific example.""",
    }

    guide = guides.get(artifact_name)
    if not guide:
        return f"Fill every [PENDIENTE] marker with specific, accurate content for {artifact_name}."

    # Inject epistemic flags for synthetic chain motors
    if epistemic and artifact_name in ("functional_contract", "operational_rules"):
        guide += f"\n\n**EPISTEMIC FLAGS — mandatory in contract and rules:**\n"
        for flag in epistemic:
            guide += f"- {flag}\n"

    return guide


# ─── Gate-specific task builders ──────────────────────────────────────────────

def _task_header(entry: MotorEntry, gate: GateResult, ctx: dict) -> str:
    purpose = ctx.get("purpose", "")
    why = ctx.get("why_it_exists", "")
    return f"""# CODEX TASK — {entry.name}
motor_id: {entry.motor_id}
stage:    {gate.from_stage.value}
gate:     {gate.gate_number}
advance_to: {gate.to_stage.value}

## Motor context
- **purpose:** {purpose}
- **why_it_exists:** {why}
- **group:** {entry.group}
- **depends_on:** {', '.join(entry.requires) if entry.requires else 'none'}

## Why this task was generated
Gate {gate.gate_number} failed with these conditions:
{chr(10).join(f'  - {c}' for c in gate.failed_conditions)}

## What you must do
Complete ALL files listed below. When done, run the verify command at the bottom.
Do NOT leave any [PENDIENTE], TODO, TBD, or ??? markers in any file.
Do NOT modify motor_state.json directly.
Do NOT invent motors or responsibilities outside this motor's scope.

"""


def _task_footer(entry: MotorEntry) -> str:
    return f"""
---
## How to verify

Run:
```bash
cd /Volumes/ZLab_Run/Zlab_Run/Repos/zlab-operational-truth-framework/motor-creator
.venv/bin/python cli.py run --motor {entry.motor_id} --auto-approve-gates
```

Expected result: `action=advanced` or `action=closed`.
If still blocked, read the new failure conditions and fix them.

## Rules
- Follow `governanza/automation-base/quality_rules.md` — no invented functionality
- Follow `governanza/automation-base/workflow_rules.md` — no skipping stages
- For motores 029–033: all outputs must include flags from `synthetic_epistemology_rules.md`
- If a file already has real content (no [PENDIENTE]), do NOT overwrite it
"""


def _artifact_section(
    artifact_name: str,
    artifact_path: Path,
    ctx: dict,
    i: int,
) -> str:
    exists = artifact_path.is_file()
    has_pending = exists and any(
        m in artifact_path.read_text(encoding="utf-8", errors="ignore")
        for m in {"[PENDIENTE]", "TODO", "TBD", "[DEFINIR]", "[FALTA]", "???"}
    )

    status = "MISSING — create this file" if not exists else (
        "HAS [PENDIENTE] MARKERS — fill all markers" if has_pending else "ALREADY FILLED — skip"
    )

    if not exists or not has_pending and exists:
        # Already filled, just show status
        return f"### {i}. `{artifact_path.name}`\nStatus: {status}\n"

    guide = _section_guidance(artifact_name, ctx)
    return f"""### {i}. `{artifact_path.name}`
**Path:** `{artifact_path}`
**Status:** {status}

**Writing guide:**
{guide}

"""


# ─── Public API ───────────────────────────────────────────────────────────────

def generate_task(
    entry: MotorEntry,
    gate_result: GateResult,
    motor_dir: Path,
    write_to_file: bool = True,
) -> str:
    """
    Generate a Codex task instruction for a blocked motor gate.

    Returns the task content as a string.
    If write_to_file=True, also writes it to runtime/tasks/{motor_id}_{stage}.task.md
    """
    from .config import ARTIFACTS_DIR
    from .models import STAGE_ARTIFACTS, ARTIFACT_EXT

    ctx = _load_ctx(entry.motor_id)
    stage = gate_result.from_stage

    # Build header
    content = _task_header(entry, gate_result, ctx)
    content += "## Files to fill\n\n"

    # Build per-artifact sections
    artifacts = STAGE_ARTIFACTS.get(stage, [])
    for i, artifact_name in enumerate(artifacts, 1):
        ext = ARTIFACT_EXT.get(artifact_name, ".md")
        if ext == "":
            p = motor_dir / ARTIFACTS_DIR / stage.value / artifact_name
        else:
            p = motor_dir / ARTIFACTS_DIR / stage.value / f"{artifact_name}{ext}"

        # Only include artifacts that have failed conditions related to them
        # or that are missing/have pending markers
        content += _artifact_section(artifact_name, p, ctx, i)

    # Special: for gate 5 (implementation), add code generation guidance
    if gate_result.gate_number == 5:
        content += _implementation_guidance(entry, ctx, motor_dir)

    content += _task_footer(entry)

    if write_to_file:
        tasks_dir = RUNTIME_DIR / "tasks"
        tasks_dir.mkdir(parents=True, exist_ok=True)
        task_file = tasks_dir / f"{entry.motor_id}_{stage.value}.task.md"
        task_file.write_text(content, encoding="utf-8")

    return content


def _implementation_guidance(entry: MotorEntry, ctx: dict, motor_dir: Path) -> str:
    """Extra guidance for gate 5 (implementation stage)."""
    key_objects = ctx.get("key_objects", [])
    key_inputs = ctx.get("key_inputs", [])
    key_outputs = ctx.get("key_outputs", [])

    codebase_dir = motor_dir / "artifacts" / "implementation" / "codebase"

    return f"""
---
## Implementation guidance (gate 5 specific)

### Codebase directory
Create: `{codebase_dir}/`

This directory must contain at minimum:
- `__init__.py` — module entry point
- One or more `.py` files implementing the motor's core logic
- The implementation must match the `functional_contract.md` exactly

### Core class / interface
Based on the functional contract for {entry.name}:
- Create a class `{entry.name.replace(' ', '').replace('/', '').replace('+', '')}` (or equivalent)
- It must accept the declared inputs and produce the declared outputs
- It must enforce the declared limits and validations
- It must NOT implement logic belonging to another motor

### Minimal implementation requirements
- Input types must match `functional_contract.md ## inputs`
- Output structure must match `functional_contract.md ## outputs`
- All operational rules from `operational_rules.md` must be enforced
- All failure modes from `failure_modes_spec.md` must be handled explicitly
{"- Key objects to implement: " + ', '.join(key_objects) if key_objects else ''}

### Determinism rule
This motor must be deterministic. No AI calls in the core logic.
If AI assistance is needed, it must be clearly isolated as an optional auxiliary layer.

"""


def get_task_path(motor_id: str, stage: Stage) -> Path:
    """Return the path where a task file would be written."""
    return RUNTIME_DIR / "tasks" / f"{motor_id}_{stage.value}.task.md"
