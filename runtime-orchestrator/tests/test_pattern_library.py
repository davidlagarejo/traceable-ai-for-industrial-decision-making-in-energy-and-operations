"""Tests for runtime_orchestrator.pattern_library."""
from __future__ import annotations

import pytest

from runtime_orchestrator import pattern_library
from runtime_orchestrator.pattern_library import (
    asset_family_concept_markers,
    list_registered_families,
    load_pattern_library,
    patterns_directory,
    reset_cache,
)


@pytest.fixture(autouse=True)
def _reset():
    reset_cache()
    yield
    reset_cache()


def test_patterns_directory_exists():
    assert patterns_directory().exists()
    assert patterns_directory().is_dir()


def test_list_registered_families_includes_known():
    registered = set(list_registered_families())
    assert "warehouse_distribution" in registered
    assert "manufacturing_facility" in registered
    assert "commercial_building" in registered
    assert "datacenter" in registered
    assert "logistics_terminal" in registered


def test_load_warehouse_pattern_returns_dict():
    pattern = load_pattern_library("warehouse_distribution")
    assert pattern is not None
    assert pattern["asset_family"] == "warehouse_distribution"
    assert "library_version" in pattern
    assert "concept_markers" in pattern
    assert "axes" in pattern


def test_warehouse_concept_markers_include_dock_and_charging():
    tokens = asset_family_concept_markers("warehouse_distribution")
    assert "dock" in tokens
    assert "charging" in tokens
    assert "refrigeration" in tokens


def test_manufacturing_concept_markers_include_process_heat():
    tokens = asset_family_concept_markers("manufacturing_facility")
    assert "process heat" in tokens or "process_heat" in tokens
    assert "compressed air" in tokens or "compressed_air" in tokens


def test_unknown_family_returns_none():
    assert load_pattern_library("nonexistent_family") is None


def test_unknown_family_returns_empty_set():
    assert asset_family_concept_markers("nonexistent_family") == set()


def test_empty_string_returns_none():
    assert load_pattern_library("") is None


def test_path_traversal_attempt_returns_none():
    """Defensive: '..' or slashes in family name must be rejected."""
    assert load_pattern_library("../etc/passwd") is None
    assert load_pattern_library("foo/bar") is None


def test_axis_concept_markers_are_aggregated_into_flat_set():
    """asset_family_concept_markers should include axis-specific tokens too."""
    tokens = asset_family_concept_markers("warehouse_distribution")
    pattern = load_pattern_library("warehouse_distribution")
    axis_tokens: set[str] = set()
    for axis_data in (pattern["axes"] or {}).values():
        for token in axis_data.get("concept_markers", []) or []:
            axis_tokens.add(str(token).lower().strip())
    assert axis_tokens.issubset(tokens)


def test_cache_returns_same_object():
    """Repeated loads return the cached payload (fast path)."""
    a = load_pattern_library("datacenter")
    b = load_pattern_library("datacenter")
    assert a is b


def test_reset_cache_clears():
    load_pattern_library("datacenter")
    reset_cache()
    # After reset, the function still returns valid data.
    pattern = load_pattern_library("datacenter")
    assert pattern is not None
    assert pattern["asset_family"] == "datacenter"
