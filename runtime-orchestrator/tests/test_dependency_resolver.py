import pytest

from runtime_orchestrator.dependency_resolver import DependencyResolver


def test_topological_sort_respects_order(resolver):
    order = resolver.topological_sort()
    idx = {m: i for i, m in enumerate(order)}
    assert idx["motor_001"] < idx["motor_002"]
    assert idx["motor_001"] < idx["motor_003"]
    assert idx["motor_002"] < idx["motor_004"]
    assert idx["motor_004"] < idx["motor_005"]
    assert idx["motor_003"] < idx["motor_005"]


def test_parallel_levels_first_level_is_roots(resolver):
    levels = resolver.parallel_levels()
    assert levels[0] == ["motor_001"]


def test_parallel_levels_002_and_003_same_level(resolver):
    levels = resolver.parallel_levels()
    level_flat = {m: i for i, level in enumerate(levels) for m in level}
    assert level_flat["motor_002"] == level_flat["motor_003"]


def test_get_dependencies(resolver):
    assert resolver.get_dependencies("motor_001") == []
    assert set(resolver.get_dependencies("motor_004")) == {"motor_001", "motor_002"}
    assert set(resolver.get_dependencies("motor_005")) == {"motor_004", "motor_003"}


def test_get_dependents(resolver):
    deps = resolver.get_dependents("motor_001")
    assert "motor_002" in deps
    assert "motor_003" in deps
    assert "motor_004" in deps


def test_transitive_deps(resolver):
    tdeps = resolver.transitive_deps("motor_005")
    assert tdeps == {"motor_001", "motor_002", "motor_003", "motor_004"}


def test_detect_cycles_none(resolver):
    assert resolver.detect_cycles() == []


def test_detect_cycles_found(tmp_path):
    import json
    cycle_deps = {
        "motors": {
            "motor_A": {"requires": ["motor_B"]},
            "motor_B": {"requires": ["motor_A"]},
        }
    }
    f = tmp_path / "cycle.json"
    f.write_text(json.dumps(cycle_deps))
    r = DependencyResolver(f)
    r.load()
    cycles = r.detect_cycles()
    assert set(cycles) == {"motor_A", "motor_B"}


def test_subgraph_includes_transitive_deps(resolver):
    sub = resolver.subgraph(["motor_005"])
    assert set(sub) == {"motor_001", "motor_002", "motor_003", "motor_004", "motor_005"}
    idx = {m: i for i, m in enumerate(sub)}
    assert idx["motor_001"] < idx["motor_004"]
    assert idx["motor_004"] < idx["motor_005"]


def test_topological_sort_subset(resolver):
    order = resolver.topological_sort(["motor_001", "motor_002"])
    assert order == ["motor_001", "motor_002"]
