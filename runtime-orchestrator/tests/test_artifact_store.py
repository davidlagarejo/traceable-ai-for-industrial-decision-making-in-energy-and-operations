from runtime_orchestrator.artifact_store import ArtifactStore, hash_inputs


def test_put_and_get(store):
    output = {"result": "ok", "count": 42}
    h = store.put("motor_001", "hash_abc", output, run_id="run1", adapter_class="TestAdapter")
    assert h.startswith("sha256:")
    envelope = store.get("motor_001", "hash_abc")
    assert envelope["output"] == output
    assert envelope["motor_id"] == "motor_001"


def test_exists(store):
    assert not store.exists("motor_001", "hash_xyz")
    store.put("motor_001", "hash_xyz", {}, run_id="r", adapter_class="A")
    assert store.exists("motor_001", "hash_xyz")


def test_put_is_idempotent(store):
    output = {"v": 1}
    h1 = store.put("motor_001", "hash_dup", output, run_id="r1", adapter_class="A")
    h2 = store.put("motor_001", "hash_dup", {"v": 99}, run_id="r2", adapter_class="B")
    assert h1 == h2
    # second write is ignored, original preserved
    assert store.get_output("motor_001", "hash_dup") == output


def test_get_output(store):
    store.put("motor_002", "h1", {"x": 1}, run_id="r", adapter_class="A")
    assert store.get_output("motor_002", "h1") == {"x": 1}
    assert store.get_output("motor_002", "nonexistent") is None


def test_list_runs(store):
    store.put("motor_003", "h1", {"a": 1}, run_id="r1", adapter_class="A")
    store.put("motor_003", "h2", {"b": 2}, run_id="r2", adapter_class="A")
    runs = store.list_runs("motor_003")
    assert len(runs) == 2
    hashes = {r["inputs_hash"] for r in runs}
    assert hashes == {"h1", "h2"}


def test_list_runs_empty(store):
    assert store.list_runs("motor_999") == []


def test_hash_inputs_deterministic():
    inputs = {"motor_001": {"a": 1}, "__pipeline__": {"x": "y"}}
    h1 = hash_inputs(inputs)
    h2 = hash_inputs(inputs)
    assert h1 == h2
    assert h1.startswith("sha256:")


def test_hash_inputs_different_for_different_content():
    h1 = hash_inputs({"a": 1})
    h2 = hash_inputs({"a": 2})
    assert h1 != h2


def test_all_motor_ids(store):
    store.put("motor_001", "h", {}, run_id="r", adapter_class="A")
    store.put("motor_005", "h", {}, run_id="r", adapter_class="A")
    ids = store.all_motor_ids()
    assert "motor_001" in ids
    assert "motor_005" in ids
