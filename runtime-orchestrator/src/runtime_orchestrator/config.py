from __future__ import annotations

import sys
from pathlib import Path

FRAMEWORK_ROOT = Path(__file__).resolve().parents[3]
GOVERNANZA = FRAMEWORK_ROOT / "governanza"
AUTOMATION_BASE = GOVERNANZA / "automation-base"
MOTOR_DEPENDENCIES_FILE = AUTOMATION_BASE / "motor_dependencies.json"

RUNTIME_ORCHESTRATOR_ROOT = Path(__file__).resolve().parents[2]
DEFAULT_ARTIFACT_STORE_DIR = RUNTIME_ORCHESTRATOR_ROOT / "artifact-store"
DEFAULT_RUN_REGISTRY_DIR = RUNTIME_ORCHESTRATOR_ROOT / "run-registry"
DEFAULT_INGESTION_LEARNING_STORE_DIR = RUNTIME_ORCHESTRATOR_ROOT / "ingestion-learning-store"

MOTOR_DIR_PATTERN = "{slug}_{id:03d}"
MAX_PARALLEL_WORKERS = 8

# Motors without setup.py — their package directories must be on sys.path
_MOTORS_WITHOUT_SETUP = [
    "phase-contract-registry_001",
    "quality-fitness-evaluation-engine_007",
]

def ensure_motor_paths() -> None:
    """Add motor package dirs that have no setup.py to sys.path."""
    for slug in _MOTORS_WITHOUT_SETUP:
        motor_dir = str(GOVERNANZA / slug)
        if motor_dir not in sys.path:
            sys.path.insert(0, motor_dir)
