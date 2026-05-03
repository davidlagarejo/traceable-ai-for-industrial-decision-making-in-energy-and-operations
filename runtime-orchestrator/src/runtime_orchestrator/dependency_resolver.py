"""DependencyResolver — reads motor_dependencies.json and exposes the DAG.

Key capabilities:
- topological_sort: ordered list respecting all dependencies
- parallel_levels: groups of motors that can run concurrently
- transitive_deps: full upstream chain for any motor
- detect_cycles: abort-safe check
"""
from __future__ import annotations

import json
from collections import defaultdict, deque
from pathlib import Path
from typing import Any


class DependencyResolver:
    def __init__(self, dependencies_file: Path) -> None:
        self._file = dependencies_file
        self._motors: dict[str, dict[str, Any]] = {}
        self._loaded = False

    # ── Loading ───────────────────────────────────────────────────────────────

    def load(self) -> None:
        data = json.loads(self._file.read_text(encoding="utf-8"))
        self._motors = data["motors"]
        self._loaded = True

    def _ensure_loaded(self) -> None:
        if not self._loaded:
            self.load()

    # ── DAG queries ───────────────────────────────────────────────────────────

    def all_motor_ids(self) -> list[str]:
        self._ensure_loaded()
        return sorted(self._motors.keys())

    def get_dependencies(self, motor_id: str) -> list[str]:
        """Direct upstream dependencies of motor_id."""
        self._ensure_loaded()
        entry = self._motors.get(motor_id, {})
        return list(entry.get("requires", []))

    def get_dependents(self, motor_id: str) -> list[str]:
        """Direct downstream motors that depend on motor_id."""
        self._ensure_loaded()
        return [mid for mid, e in self._motors.items() if motor_id in e.get("requires", [])]

    def transitive_deps(self, motor_id: str) -> set[str]:
        """All motors that must complete before motor_id can start."""
        self._ensure_loaded()
        visited: set[str] = set()
        queue = deque(self.get_dependencies(motor_id))
        while queue:
            dep = queue.popleft()
            if dep not in visited:
                visited.add(dep)
                queue.extend(self.get_dependencies(dep))
        return visited

    def detect_cycles(self) -> list[str]:
        """Returns motor_ids involved in cycles. Empty list = no cycles."""
        self._ensure_loaded()
        in_degree: dict[str, int] = {m: 0 for m in self._motors}
        adj: dict[str, list[str]] = defaultdict(list)
        for mid, entry in self._motors.items():
            for req in entry.get("requires", []):
                if req in self._motors:
                    adj[req].append(mid)
                    in_degree[mid] += 1

        queue = deque(m for m, d in in_degree.items() if d == 0)
        visited = 0
        while queue:
            node = queue.popleft()
            visited += 1
            for neighbor in adj[node]:
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        return [m for m, d in in_degree.items() if d > 0]

    def topological_sort(self, motor_ids: list[str] | None = None) -> list[str]:
        """Return motors in dependency-safe execution order.

        If motor_ids is given, only those motors are sorted (still respects
        their mutual dependencies within the set).
        """
        self._ensure_loaded()
        cycles = self.detect_cycles()
        if cycles:
            raise RuntimeError(f"Dependency cycles detected: {cycles}")

        subset = set(motor_ids) if motor_ids is not None else set(self._motors.keys())
        in_degree: dict[str, int] = {m: 0 for m in subset}
        adj: dict[str, list[str]] = defaultdict(list)

        for mid in subset:
            for req in self._motors.get(mid, {}).get("requires", []):
                if req in subset:
                    adj[req].append(mid)
                    in_degree[mid] += 1

        queue = deque(sorted(m for m, d in in_degree.items() if d == 0))
        result: list[str] = []
        while queue:
            node = queue.popleft()
            result.append(node)
            for neighbor in sorted(adj[node]):
                in_degree[neighbor] -= 1
                if in_degree[neighbor] == 0:
                    queue.append(neighbor)

        if len(result) != len(subset):
            raise RuntimeError("Topological sort incomplete — possible cycle in subset")
        return result

    def parallel_levels(self, motor_ids: list[str] | None = None) -> list[list[str]]:
        """Group motors into levels that can run in parallel.

        All motors in a level have no dependency on any other motor
        in the same level. Levels must run sequentially; within each
        level all motors can run concurrently.
        """
        self._ensure_loaded()
        subset = set(motor_ids) if motor_ids is not None else set(self._motors.keys())
        remaining_in_degree: dict[str, int] = {m: 0 for m in subset}
        adj: dict[str, list[str]] = defaultdict(list)

        for mid in subset:
            for req in self._motors.get(mid, {}).get("requires", []):
                if req in subset:
                    adj[req].append(mid)
                    remaining_in_degree[mid] += 1

        levels: list[list[str]] = []
        while remaining_in_degree:
            current_level = sorted(m for m, d in remaining_in_degree.items() if d == 0)
            if not current_level:
                raise RuntimeError("Cycle detected while building parallel levels")
            levels.append(current_level)
            for node in current_level:
                del remaining_in_degree[node]
                for neighbor in adj[node]:
                    if neighbor in remaining_in_degree:
                        remaining_in_degree[neighbor] -= 1

        return levels

    def subgraph(self, motor_ids: list[str]) -> list[str]:
        """Return motor_ids plus all their transitive deps, sorted topologically."""
        self._ensure_loaded()
        full: set[str] = set(motor_ids)
        for mid in motor_ids:
            full.update(self.transitive_deps(mid))
        return self.topological_sort(list(full))
