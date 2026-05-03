import pytest

from runtime_orchestrator.models import MotorRunStatus, PipelineStatus


def test_full_run_completes(orchestrator):
    run = orchestrator.run("test_pipeline", {"input": "data"})
    assert run.status in (PipelineStatus.COMPLETED, PipelineStatus.COMPLETED_WITH_STUBS)
    assert len(run.motor_results) == 5
    for mid, result in run.motor_results.items():
        assert result.status in (MotorRunStatus.COMPLETED, MotorRunStatus.STUB)


def test_resume_uses_cache(orchestrator, store):
    run1 = orchestrator.run("test_pipeline", {"input": "data"})
    run2 = orchestrator.run("test_pipeline", {"input": "data"}, resume=True)

    for mid, result in run2.motor_results.items():
        assert result.status == MotorRunStatus.CACHED, f"{mid} should be cached on 2nd run"


def test_no_cache_reruns(orchestrator):
    orchestrator.run("test_pipeline", {"input": "data"})
    run2 = orchestrator.run("test_pipeline", {"input": "data"}, resume=False)
    for result in run2.motor_results.values():
        assert result.status != MotorRunStatus.CACHED


def test_force_rerun_specific_motor(orchestrator):
    orchestrator.run("test_pipeline", {"input": "data"})
    run2 = orchestrator.run(
        "test_pipeline", {"input": "data"},
        resume=True, force_rerun=["motor_003"]
    )
    assert run2.motor_results["motor_003"].status != MotorRunStatus.CACHED
    # motor_001 should still be cached (not in force_rerun)
    assert run2.motor_results["motor_001"].status == MotorRunStatus.CACHED


def test_subset_run(orchestrator):
    run = orchestrator.run("test_pipeline", {}, motor_ids=["motor_002"])
    # motor_002 depends on motor_001, so both should run
    assert "motor_001" in run.motor_results
    assert "motor_002" in run.motor_results
    assert "motor_005" not in run.motor_results


def test_different_inputs_different_cache(orchestrator):
    run1 = orchestrator.run("test_pipeline", {"input": "data_A"})
    run2 = orchestrator.run("test_pipeline", {"input": "data_B"})
    # Different inputs → different hashes → both run fresh
    for result in run2.motor_results.values():
        assert result.status != MotorRunStatus.CACHED


def test_run_has_timestamps(orchestrator):
    run = orchestrator.run("test_pipeline", {})
    assert run.started_at
    assert run.completed_at
    assert run.run_id.startswith("run:")


def test_failed_motor_stops_pipeline(orchestrator, registry):
    class FailingAdapter:
        @property
        def motor_id(self): return "motor_001"
        @property
        def input_motor_ids(self): return []
        def run(self, inputs): raise RuntimeError("intentional failure")

    registry.register(FailingAdapter())
    run = orchestrator.run("test_pipeline", {})
    assert run.status == PipelineStatus.FAILED
    assert run.error is not None


def test_motor_registry_hot_swap(orchestrator, registry):
    class CustomAdapter:
        @property
        def motor_id(self): return "motor_003"
        @property
        def input_motor_ids(self): return ["motor_001"]
        def run(self, inputs): return {"custom": True, "source": "swapped"}

    registry.register(CustomAdapter())
    run = orchestrator.run("test_pipeline_swap", {"input": "x"}, resume=False)
    # motor_003 output should be from our custom adapter
    output = orchestrator._store.get_output(
        "motor_003", run.motor_results["motor_003"].inputs_hash
    )
    assert output == {"custom": True, "source": "swapped"}
