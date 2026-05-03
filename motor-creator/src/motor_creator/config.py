from __future__ import annotations

from pathlib import Path


# Absolute path to the repo root
FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]

# Key directories
AUTOMATION_BASE = FRAMEWORK_ROOT / "governanza" / "automation-base"
GOVERNANZA = FRAMEWORK_ROOT / "governanza"
MOTOR_CREATOR_ROOT = FRAMEWORK_ROOT / "motor-creator"
RUNTIME_DIR = MOTOR_CREATOR_ROOT / "runtime"

# Key source-of-truth files
MOTOR_DEPENDENCIES_FILE = AUTOMATION_BASE / "motor_dependencies.json"
MOTOR_SCHEMA_FILE = AUTOMATION_BASE / "motor_schema.json"
MOTOR_CONTEXT_REGISTRY_FILE = AUTOMATION_BASE / "motor_context_registry.json"

# Runtime files
EVENT_LOG_FILE = RUNTIME_DIR / "events.jsonl"
MANUAL_APPROVALS_FILE = RUNTIME_DIR / "manual_approvals.json"

# Markers that signal incomplete content (from stage_gates.md)
OPEN_MARKERS = {"TODO", "TBD", "[PENDIENTE]", "[DEFINIR]", "[FALTA]", "???"}

# Minimum file size to count as non-empty (bytes, from stage_gates.md)
MIN_FILE_SIZE_BYTES = 500

# Paths within a motor directory
MOTOR_STATE_FILENAME = "motor_state.json"
ARTIFACTS_DIR = "artifacts"
