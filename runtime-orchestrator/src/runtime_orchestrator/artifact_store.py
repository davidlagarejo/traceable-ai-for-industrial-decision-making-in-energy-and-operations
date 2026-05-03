"""Immutable, content-addressed artifact store.

Artifacts are stored as JSON files under:
  {store_dir}/{motor_id}/{inputs_hash}.json

The file name IS the lookup key — same inputs always hit the same file.
Files are never overwritten; a second write with the same key is a no-op.
"""
from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


class ArtifactStore:
    def __init__(self, store_dir: Path) -> None:
        self._root = Path(store_dir)
        self._root.mkdir(parents=True, exist_ok=True)

    # ── Public API ────────────────────────────────────────────────────────────

    def exists(self, motor_id: str, inputs_hash: str) -> bool:
        return self._path(motor_id, inputs_hash).exists()

    def get(self, motor_id: str, inputs_hash: str) -> dict[str, Any] | None:
        p = self._path(motor_id, inputs_hash)
        if not p.exists():
            return None
        return json.loads(p.read_text(encoding="utf-8"))

    def put(
        self,
        motor_id: str,
        inputs_hash: str,
        output: dict[str, Any],
        *,
        run_id: str,
        adapter_class: str,
    ) -> str:
        """Persist output. Returns output_hash. Idempotent: won't overwrite."""
        p = self._path(motor_id, inputs_hash)
        if p.exists():
            existing = json.loads(p.read_text(encoding="utf-8"))
            return existing["output_hash"]

        output_hash = _hash_dict(output)
        envelope = {
            "motor_id": motor_id,
            "inputs_hash": inputs_hash,
            "output_hash": output_hash,
            "run_id": run_id,
            "adapter_class": adapter_class,
            "produced_at": datetime.now(timezone.utc).isoformat(),
            "output": output,
        }
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(json.dumps(envelope, ensure_ascii=False, indent=2), encoding="utf-8")
        return output_hash

    def get_output(self, motor_id: str, inputs_hash: str) -> dict[str, Any] | None:
        """Return only the output dict (not the envelope)."""
        envelope = self.get(motor_id, inputs_hash)
        if envelope is None:
            return None
        return envelope.get("output")

    def list_runs(self, motor_id: str) -> list[dict[str, Any]]:
        motor_dir = self._root / motor_id
        if not motor_dir.exists():
            return []
        results = []
        for p in sorted(motor_dir.glob("*.json")):
            try:
                data = json.loads(p.read_text(encoding="utf-8"))
                results.append({
                    "inputs_hash": data.get("inputs_hash"),
                    "output_hash": data.get("output_hash"),
                    "produced_at": data.get("produced_at"),
                    "run_id": data.get("run_id"),
                    "adapter_class": data.get("adapter_class"),
                })
            except Exception:
                continue
        return results

    def all_motor_ids(self) -> list[str]:
        return sorted(p.name for p in self._root.iterdir() if p.is_dir())

    # ── Internal ──────────────────────────────────────────────────────────────

    def _path(self, motor_id: str, inputs_hash: str) -> Path:
        return self._root / motor_id / f"{inputs_hash}.json"


def hash_inputs(inputs: dict[str, Any]) -> str:
    return _hash_dict(inputs)


def _hash_dict(d: dict[str, Any]) -> str:
    canonical = json.dumps(d, sort_keys=True, ensure_ascii=False, default=str)
    return "sha256:" + hashlib.sha256(canonical.encode()).hexdigest()[:16]
