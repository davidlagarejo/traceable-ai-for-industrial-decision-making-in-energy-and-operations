import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent / "src"))

from runtime_orchestrator.artifact_store import ArtifactStore
from runtime_orchestrator.dependency_resolver import DependencyResolver
from runtime_orchestrator.motor_registry import MotorRegistry
from runtime_orchestrator.pipeline_orchestrator import PipelineOrchestrator


@pytest.fixture
def store(tmp_path):
    return ArtifactStore(tmp_path / "artifacts")


@pytest.fixture
def deps_file(tmp_path):
    deps = {
        "motors": {
            "motor_001": {"requires": [], "group": "A"},
            "motor_002": {"requires": ["motor_001"], "group": "A"},
            "motor_003": {"requires": ["motor_001"], "group": "A"},
            "motor_004": {"requires": ["motor_001", "motor_002"], "group": "A"},
            "motor_005": {"requires": ["motor_004", "motor_003"], "group": "B"},
        }
    }
    f = tmp_path / "motor_dependencies.json"
    f.write_text(json.dumps(deps))
    return f


@pytest.fixture
def resolver(deps_file):
    r = DependencyResolver(deps_file)
    r.load()
    return r


class EchoAdapter:
    """Test adapter — returns its inputs as output."""
    def __init__(self, motor_id, input_motor_ids=None):
        self._motor_id = motor_id
        self._input_motor_ids = input_motor_ids or []

    @property
    def motor_id(self):
        return self._motor_id

    @property
    def input_motor_ids(self):
        return self._input_motor_ids

    def run(self, inputs):
        return {"motor_id": self._motor_id, "received": list(inputs.keys())}


@pytest.fixture
def registry():
    r = MotorRegistry()
    r.register(EchoAdapter("motor_001"))
    r.register(EchoAdapter("motor_002", ["motor_001"]))
    r.register(EchoAdapter("motor_003", ["motor_001"]))
    r.register(EchoAdapter("motor_004", ["motor_001", "motor_002"]))
    r.register(EchoAdapter("motor_005", ["motor_004", "motor_003"]))
    return r


@pytest.fixture
def orchestrator(registry, store, resolver):
    return PipelineOrchestrator(
        registry=registry,
        artifact_store=store,
        resolver=resolver,
        max_workers=2,
    )
