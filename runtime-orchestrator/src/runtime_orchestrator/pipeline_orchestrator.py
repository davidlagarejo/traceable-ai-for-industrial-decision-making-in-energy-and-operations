"""PipelineOrchestrator — Layer 4.

Executes a set of motors in topological order, with:
- Automatic parallelism for independent motors (ThreadPoolExecutor)
- Content-hash caching via ArtifactStore (resume from any point)
- Force-rerun for specific motors
- Full PipelineRun manifest on completion
- Hot-swap: uses whatever adapter is registered at run time
"""
from __future__ import annotations

import hashlib
import json
import logging
import os
import time
from concurrent.futures import FIRST_COMPLETED, ThreadPoolExecutor, wait
from datetime import datetime, timezone
from pathlib import Path
from uuid import uuid4
from typing import Any

from .artifact_store import ArtifactStore, hash_inputs
from .layer_bundle import LayerBundle
from .layer_registry import MOTOR_LAYER_MAP
from .asset_contracts import (
    derive_asset_context_readiness,
    derive_dominant_evidence_scope,
    derive_observable_clusters,
    derive_report_identity_state,
    derive_subject_contract_admissibility,
    derive_subject_definition,
    derive_target_type_classification_seed,
    derive_target_definition,
    missing_observable_clusters,
)
from .config import DEFAULT_RUN_REGISTRY_DIR, MAX_PARALLEL_WORKERS
from .dependency_resolver import DependencyResolver
from .ingestion_learning_store import (
    load_pipeline_learning_summary,
    save_pipeline_learning_summary,
)
from .models import MotorRunResult, MotorRunStatus, PipelineRun, PipelineStatus
from .motor_registry import MotorRegistry

log = logging.getLogger(__name__)

_HEARTBEAT_INTERVAL_SECONDS = 5.0
# Default schema version emitted for any auto-constructed LayerBundle.
# Bumped per-motor when a producer changes its payload contract.
_DEFAULT_BUNDLE_VERSION = "1.0.0"
_RUNTIME_HASH_EXCLUDED_KEYS = {
    "run_id",
    "status",
    "runner_pid",
    "last_heartbeat_at",
    "summary",
    "truth_summary",
    "motor_results",
    "report_type_trace",
    "phase_self_evaluation_summary",
    "previous_run_id",
    "previous_run_summary",
    "case_delta_summary",
    "source_yield_memory_summary",
    "next_ingestion_priority_update",
    "ingestion_learning_summary",
}
_CONFIG_DEFAULT_RUN_REGISTRY_DIR = DEFAULT_RUN_REGISTRY_DIR
_ORIGINAL_LOAD_PIPELINE_LEARNING_SUMMARY = load_pipeline_learning_summary


class PipelineOrchestrator:
    def __init__(
        self,
        registry: MotorRegistry,
        artifact_store: ArtifactStore,
        resolver: DependencyResolver,
        *,
        max_workers: int = MAX_PARALLEL_WORKERS,
    ) -> None:
        self._registry = registry
        self._store = artifact_store
        self._resolver = resolver
        self._max_workers = max_workers

    # ── Main entry point ──────────────────────────────────────────────────────

    def run(
        self,
        pipeline_id: str,
        pipeline_inputs: dict[str, Any],
        *,
        motor_ids: list[str] | None = None,
        resume: bool = True,
        force_rerun: list[str] | None = None,
    ) -> PipelineRun:
        """Execute the pipeline.

        Args:
            pipeline_id: logical name for this pipeline (e.g. 'phase1_data').
            pipeline_inputs: raw data injected into every motor as
                             inputs['__pipeline__'].
            motor_ids: run only these motors (+ their transitive deps).
                       None = run all motors in motor_dependencies.json.
            resume: if True, reuse cached outputs from ArtifactStore.
            force_rerun: list of motor_ids to re-execute even if cached.
        """
        force_set = set(force_rerun or [])
        run_id = _make_run_id(pipeline_id, pipeline_inputs)
        previous_run_summary = _load_previous_pipeline_run_summary(pipeline_id, run_id)
        subject_definition = derive_subject_definition(pipeline_inputs)
        target_definition = derive_target_definition(pipeline_inputs)
        subject_contract_admissibility, subject_contract_warning_register = derive_subject_contract_admissibility(
            subject_definition,
            target_definition,
        )
        target_type_classification_seed = derive_target_type_classification_seed(
            subject_definition,
            target_definition,
        )
        initial_asset_context_readiness = derive_asset_context_readiness(
            pipeline_inputs,
            target_definition=target_definition,
        )
        pipeline_run = PipelineRun(
            run_id=run_id,
            pipeline_id=pipeline_id,
            started_at=_now(),
            runner_pid=os.getpid(),
            last_heartbeat_at=_now(),
            pipeline_inputs_hash=hash_inputs(pipeline_inputs),
            subject_definition=subject_definition,
            subject_contract_status=subject_definition.get("contract_status"),
            subject_contract_admissibility=subject_contract_admissibility,
            subject_contract_warning_register=subject_contract_warning_register,
            ingestion_contract_status=None,
            subject_resolution_state=None,
            asset_authenticity_state=subject_definition.get("asset_identity_evidence_class"),
            target_type_classification=target_type_classification_seed.get("target_type_classification"),
            asset_identity_status=target_type_classification_seed.get("asset_identity_status"),
            classification_confidence=target_type_classification_seed.get("classification_confidence"),
            target_admissibility_state=None,
            subject_gate_passed=None,
            subject_gate_reason_register=[],
            allowed_report_classes=[],
            target_definition=target_definition,
            asset_context_readiness=initial_asset_context_readiness,
            technical_substrate_readiness=None,
            asset_level_evidence_found=None,
            issuer_only_evidence_found=None,
            recommended_report_type=target_type_classification_seed.get("report_type_recommendation", {}).get("recommended_report_type"),
            prohibited_report_types=list(target_type_classification_seed.get("report_type_recommendation", {}).get("prohibited_report_types", [])),
            report_identity_state=derive_report_identity_state(
                target_definition,
                initial_asset_context_readiness,
            ),
            dominant_evidence_scope=derive_dominant_evidence_scope(
                target_definition,
                initial_asset_context_readiness,
            ),
            missing_observable_clusters=missing_observable_clusters(
                derive_observable_clusters(pipeline_inputs, target_definition)
            ),
            previous_run_id=str(previous_run_summary.get("run_id", "")).strip() or None,
            previous_run_summary=previous_run_summary,
        )

        # Build execution plan
        if motor_ids is not None:
            ordered = self._resolver.subgraph(motor_ids)
        else:
            ordered = self._resolver.topological_sort()

        for mid in ordered:
            adapter = self._registry.get(mid)
            pipeline_run.motor_results[mid] = MotorRunResult(
                motor_id=mid,
                status=MotorRunStatus.PENDING,
                inputs_hash="",
                adapter_class=type(adapter).__name__ if adapter is not None else None,
                implementation_state=_implementation_state(adapter),
                output_state="unknown",
            )
        self._persist_run(pipeline_run)

        levels = self._resolver.parallel_levels(ordered)
        log.info(
            "[%s] Starting pipeline '%s' — %d motors across %d levels",
            run_id[:8],
            pipeline_id,
            len(ordered),
            len(levels),
        )

        # Accumulated outputs: motor_id → output dict
        outputs: dict[str, dict[str, Any]] = {"__pipeline__": pipeline_inputs}

        try:
            for level_idx, level in enumerate(levels):
                log.info("[%s] Level %d — motors: %s", run_id[:8], level_idx, level)
                for mid in level:
                    current = pipeline_run.motor_results.get(mid)
                    if current is not None:
                        current.status = MotorRunStatus.RUNNING
                self._persist_run(pipeline_run)

                level_results = self._run_level(
                    level=level,
                    outputs=outputs,
                    run_id=run_id,
                    resume=resume,
                    force_set=force_set,
                    runtime_context=self._runtime_context(pipeline_run),
                    pipeline_run=pipeline_run,
                )
                for mid, result in level_results.items():
                    pipeline_run.motor_results[mid] = result
                    if result.status == MotorRunStatus.FAILED:
                        raise _MotorFailed(mid, result.error or "unknown error")
                    # Make output available downstream
                    if result.output_hash:
                        cached = self._store.get_output(mid, result.inputs_hash)
                        if cached is not None:
                            outputs[mid] = cached
                # Populate the LayerBundle bus for motors with a layer assigned.
                # Auto-built from the just-produced output; adapters do not need
                # to know about LayerBundle. Motors with layer=None are skipped
                # (infrastructure / ingestion / support — see layer_registry.py).
                _populate_layer_bundles(outputs, level)
                self._refresh_run_semantics(pipeline_run, outputs)
                # Mirror the post-refresh inferred state into the bus so
                # downstream consumers can opt in to bundle-reads. The
                # __runtime__ legacy path is kept fully intact during this
                # transition (RECOVERY_BACKLOG.md R-14b..R-23).
                _publish_inferred_state_bundle(outputs, self._runtime_context(pipeline_run))
                self._persist_run(pipeline_run)

        except _MotorFailed as exc:
            pipeline_run.status = PipelineStatus.FAILED
            pipeline_run.error = str(exc)
            log.error("[%s] Pipeline FAILED at %s: %s", run_id[:8], exc.motor_id, exc.reason)
        else:
            pipeline_run.status = _overall_status(pipeline_run.motor_results, outputs)
            log.info("[%s] Pipeline %s", run_id[:8], pipeline_run.status.value.upper())

        pipeline_run.completed_at = _now()
        self._persist_run(pipeline_run)
        return pipeline_run

    # ── Level execution ───────────────────────────────────────────────────────

    def _run_level(
        self,
        level: list[str],
        outputs: dict[str, dict[str, Any]],
        run_id: str,
        resume: bool,
        force_set: set[str],
        runtime_context: dict[str, Any],
        pipeline_run: PipelineRun,
    ) -> dict[str, MotorRunResult]:
        results: dict[str, MotorRunResult] = {}
        with ThreadPoolExecutor(max_workers=min(self._max_workers, len(level))) as pool:
            futures = {
                pool.submit(
                    self._execute_motor,
                    mid,
                    outputs,
                    run_id,
                    resume,
                    force_set,
                    runtime_context,
                ): mid
                for mid in level
            }
            pending = set(futures)
            while pending:
                done, pending = wait(
                    pending,
                    timeout=_HEARTBEAT_INTERVAL_SECONDS,
                    return_when=FIRST_COMPLETED,
                )
                if not done:
                    self._persist_run(pipeline_run)
                    continue

                for future in done:
                    mid = futures[future]
                    try:
                        results[mid] = future.result()
                    except Exception as exc:
                        results[mid] = MotorRunResult(
                            motor_id=mid,
                            status=MotorRunStatus.FAILED,
                            inputs_hash="",
                            error=str(exc),
                            implementation_state=_implementation_state(self._registry.get(mid)),
                            output_state="unknown",
                        )
                    pipeline_run.motor_results[mid] = results[mid]
                    self._persist_run(pipeline_run)

                if pending:
                    self._persist_run(pipeline_run)
        return results

    # ── Single motor execution ────────────────────────────────────────────────

    def _execute_motor(
        self,
        motor_id: str,
        outputs: dict[str, dict[str, Any]],
        run_id: str,
        resume: bool,
        force_set: set[str],
        runtime_context: dict[str, Any],
    ) -> MotorRunResult:
        adapter = self._registry.get(motor_id)
        if adapter is None:
            log.warning("[%s] No adapter for %s — skipping", run_id[:8], motor_id)
            return MotorRunResult(
                motor_id=motor_id,
                status=MotorRunStatus.SKIPPED,
                inputs_hash="",
                implementation_state="missing",
                output_state="unknown",
            )

        motor_inputs = self._collect_inputs(motor_id, adapter, outputs, runtime_context)
        inputs_hash = hash_inputs(_stable_inputs_for_hash(motor_inputs))

        # Cache check
        if resume and motor_id not in force_set and self._store.exists(motor_id, inputs_hash):
            envelope = self._store.get(motor_id, inputs_hash)
            output_state = _output_state_from_envelope(envelope)
            implementation_state = _implementation_state(adapter)
            if not (output_state == "stub" and implementation_state == "implemented"):
                log.debug("[%s] CACHED  %s (%s)", run_id[:8], motor_id, inputs_hash[:16])
                return MotorRunResult(
                    motor_id=motor_id,
                    status=MotorRunStatus.CACHED,
                    inputs_hash=inputs_hash,
                    output_hash=envelope["output_hash"] if envelope else None,
                    adapter_class=type(adapter).__name__,
                    cached_from=str(self._store._path(motor_id, inputs_hash)),
                    implementation_state=implementation_state,
                    output_state=output_state,
                )
            log.info(
                "[%s] RECACHE %s — cached artifact is stub but adapter is now implemented",
                run_id[:8],
                motor_id,
            )

        # Execute
        t0 = time.monotonic()
        try:
            log.debug("[%s] RUNNING %s", run_id[:8], motor_id)
            output = adapter.run(motor_inputs)
            duration_ms = (time.monotonic() - t0) * 1000

            output_hash = self._store.put(
                motor_id,
                inputs_hash,
                output,
                run_id=run_id,
                adapter_class=type(adapter).__name__,
            )
            status = (
                MotorRunStatus.STUB
                if output.get("__stub__") is True
                else MotorRunStatus.COMPLETED
            )
            log.debug("[%s] %-8s %s (%.0fms)", run_id[:8], status.value.upper(), motor_id, duration_ms)
            return MotorRunResult(
                motor_id=motor_id,
                status=status,
                inputs_hash=inputs_hash,
                output_hash=output_hash,
                duration_ms=duration_ms,
                adapter_class=type(adapter).__name__,
                implementation_state=_implementation_state(adapter),
                output_state="stub" if output.get("__stub__") is True else "real",
            )

        except Exception as exc:
            duration_ms = (time.monotonic() - t0) * 1000
            log.error("[%s] FAILED  %s: %s", run_id[:8], motor_id, exc)
            return MotorRunResult(
                motor_id=motor_id,
                status=MotorRunStatus.FAILED,
                inputs_hash=inputs_hash,
                error=str(exc),
                duration_ms=duration_ms,
                adapter_class=type(adapter).__name__,
                implementation_state=_implementation_state(adapter),
                output_state="unknown",
            )

    # ── Input resolution ──────────────────────────────────────────────────────

    def _collect_inputs(
        self,
        motor_id: str,
        adapter: Any,
        outputs: dict[str, dict[str, Any]],
        runtime_context: dict[str, Any],
    ) -> dict[str, Any]:
        # __bundles__ is the LayerBundle bus (RECOVERY_ARCHITECTURE_PLAN.md §3).
        # Populated by run() after each motor with a layer assignment finishes.
        # A motor that does not consume LayerBundle simply ignores this key.
        collected: dict[str, Any] = {
            "__pipeline__": outputs.get("__pipeline__", {}),
            "__runtime__": runtime_context,
            "__bundles__": dict(outputs.get("__bundles__", {})),
        }
        for dep_id in adapter.input_motor_ids:
            if dep_id in outputs:
                collected[dep_id] = outputs[dep_id]
            else:
                # Upstream not in outputs — try artifact store with latest run
                runs = self._store.list_runs(dep_id)
                if runs:
                    latest = max(runs, key=lambda r: r.get("produced_at", ""))
                    cached = self._store.get_output(dep_id, latest["inputs_hash"])
                    if cached:
                        collected[dep_id] = cached
                        log.debug(
                            "  %s: loaded %s from artifact store (latest run)",
                            motor_id, dep_id,
                        )
                    else:
                        collected[dep_id] = {}
                else:
                    collected[dep_id] = {}
        return collected

    # ── Persistence ───────────────────────────────────────────────────────────

    def _persist_run(self, run: PipelineRun) -> None:
        registry_dir = DEFAULT_RUN_REGISTRY_DIR
        registry_dir.mkdir(parents=True, exist_ok=True)
        if run.status == PipelineStatus.RUNNING:
            run.last_heartbeat_at = _now()
        path = registry_dir / f"{run.run_id}.json"
        path.write_text(
            json.dumps(run.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        if run.status != PipelineStatus.RUNNING:
            save_pipeline_learning_summary(run.to_dict())
        log.debug("Run manifest saved to %s", path)

    def _runtime_context(self, run: PipelineRun) -> dict[str, Any]:
        payload = run.to_dict()
        return {
            "run_id": payload.get("run_id"),
            "pipeline_id": payload.get("pipeline_id"),
            "status": payload.get("status"),
            "runner_pid": payload.get("runner_pid"),
            "last_heartbeat_at": payload.get("last_heartbeat_at"),
            "subject_definition": payload.get("subject_definition", {}),
            "subject_contract_status": payload.get("subject_contract_status"),
            "subject_contract_admissibility": payload.get("subject_contract_admissibility"),
            "subject_contract_warning_register": payload.get("subject_contract_warning_register", []),
            "ingestion_contract_status": payload.get("ingestion_contract_status"),
            "subject_resolution_state": payload.get("subject_resolution_state"),
            "asset_authenticity_state": payload.get("asset_authenticity_state"),
            "target_type_classification": payload.get("target_type_classification"),
            "asset_identity_status": payload.get("asset_identity_status"),
            "classification_confidence": payload.get("classification_confidence"),
            "target_admissibility_state": payload.get("target_admissibility_state"),
            "subject_gate_passed": payload.get("subject_gate_passed"),
            "subject_gate_reason_register": payload.get("subject_gate_reason_register", []),
            "allowed_report_classes": payload.get("allowed_report_classes", []),
            "target_definition": payload.get("target_definition", {}),
            "asset_context_readiness": payload.get("asset_context_readiness"),
            "technical_substrate_readiness": payload.get("technical_substrate_readiness"),
            "asset_level_evidence_found": payload.get("asset_level_evidence_found"),
            "issuer_only_evidence_found": payload.get("issuer_only_evidence_found"),
            "recommended_report_type": payload.get("recommended_report_type"),
            "prohibited_report_types": payload.get("prohibited_report_types", []),
            "report_identity_state": payload.get("report_identity_state"),
            "dominant_evidence_scope": payload.get("dominant_evidence_scope"),
            "missing_observable_clusters": payload.get("missing_observable_clusters", []),
            "evidence_maturity_summary": payload.get("evidence_maturity_summary", {}),
            "key_variable_bottlenecks": payload.get("key_variable_bottlenecks", []),
            "report_readiness_reason": payload.get("report_readiness_reason"),
            "report_type_trace": payload.get("report_type_trace", {}),
            "phase_self_evaluation_summary": payload.get("phase_self_evaluation_summary", {}),
            "previous_run_id": payload.get("previous_run_id"),
            "previous_run_summary": payload.get("previous_run_summary", {}),
            "case_delta_summary": payload.get("case_delta_summary", {}),
            "source_yield_memory_summary": payload.get("source_yield_memory_summary", {}),
            "next_ingestion_priority_update": payload.get("next_ingestion_priority_update", {}),
            "ingestion_learning_summary": payload.get("ingestion_learning_summary", {}),
            "summary": payload.get("summary", {}),
            "truth_summary": payload.get("truth_summary", {}),
            "motor_results": payload.get("motor_results", {}),
        }

    def _refresh_run_semantics(self, run: PipelineRun, outputs: dict[str, dict[str, Any]]) -> None:
        if isinstance(outputs.get("motor_001"), dict):
            m01 = outputs["motor_001"]
            run.subject_definition = m01.get("subject_definition_contract", run.subject_definition)
            run.subject_contract_status = m01.get("subject_contract_status", run.subject_contract_status)
            run.subject_contract_admissibility = m01.get(
                "subject_contract_admissibility",
                run.subject_contract_admissibility,
            )
            run.subject_contract_warning_register = list(
                m01.get("subject_contract_warning_register", run.subject_contract_warning_register)
            )
            run.ingestion_contract_status = m01.get("ingestion_contract_status", run.ingestion_contract_status)
            target_seed = m01.get("target_type_classification_seed", {})
            run.target_type_classification = target_seed.get("target_type_classification", run.target_type_classification)
            run.asset_identity_status = target_seed.get("asset_identity_status", run.asset_identity_status)
            run.classification_confidence = target_seed.get("classification_confidence", run.classification_confidence)
            if isinstance(target_seed.get("report_type_recommendation"), dict):
                run.recommended_report_type = target_seed["report_type_recommendation"].get(
                    "recommended_report_type",
                    run.recommended_report_type,
                )
                run.prohibited_report_types = list(
                    target_seed["report_type_recommendation"].get(
                        "prohibited_report_types",
                        run.prohibited_report_types,
                    )
                )
        if isinstance(outputs.get("motor_006"), dict):
            m06 = outputs["motor_006"].get("asset_identity_resolution", {})
            run.subject_resolution_state = m06.get("subject_resolution_state", run.subject_resolution_state)
            run.asset_authenticity_state = m06.get("asset_authenticity_state", run.asset_authenticity_state)
            hypothesis = m06.get("target_classification_hypothesis", {})
            run.target_type_classification = hypothesis.get("target_type", run.target_type_classification)
            run.classification_confidence = hypothesis.get("classification_confidence", run.classification_confidence)
        if isinstance(outputs.get("motor_003"), dict):
            run.target_definition = outputs["motor_003"].get("target_definition_contract", run.target_definition)
        if isinstance(outputs.get("motor_007"), dict):
            m07 = outputs["motor_007"]
            run.asset_context_readiness = m07.get("asset_context_readiness", run.asset_context_readiness)
            run.technical_substrate_readiness = m07.get(
                "technical_substrate_readiness",
                run.technical_substrate_readiness,
            )
            run.target_type_classification = m07.get("target_type_classification", run.target_type_classification)
            run.asset_identity_status = m07.get("asset_identity_status", run.asset_identity_status)
            run.classification_confidence = m07.get("classification_confidence", run.classification_confidence)
            run.target_admissibility_state = m07.get("target_admissibility_state", run.target_admissibility_state)
            run.subject_gate_passed = m07.get("subject_gate_passed", run.subject_gate_passed)
            run.subject_gate_reason_register = list(
                m07.get("subject_gate_reason_register", run.subject_gate_reason_register)
            )
            run.allowed_report_classes = list(
                m07.get("allowed_report_classes", run.allowed_report_classes)
            )
            run.asset_level_evidence_found = m07.get(
                "asset_level_evidence_found",
                run.asset_level_evidence_found,
            )
            run.issuer_only_evidence_found = m07.get(
                "issuer_only_evidence_found",
                run.issuer_only_evidence_found,
            )
            run.recommended_report_type = m07.get("recommended_report_type", run.recommended_report_type)
            run.prohibited_report_types = list(
                m07.get("prohibited_report_types", run.prohibited_report_types)
            )
            run.missing_observable_clusters = list(
                m07.get("missing_observable_clusters", run.missing_observable_clusters)
            )
            run.dominant_evidence_scope = m07.get("dominant_evidence_scope", run.dominant_evidence_scope)
            run.report_identity_state = m07.get("report_identity_state", run.report_identity_state)
        if isinstance(outputs.get("motor_025"), dict):
            m25 = outputs["motor_025"]
            run.report_identity_state = m25.get("report_identity_state", run.report_identity_state)
            run.recommended_report_type = m25.get("recommended_report_type", run.recommended_report_type)
            run.dominant_evidence_scope = m25.get("dominant_evidence_scope", run.dominant_evidence_scope)
            run.report_type_trace = dict(m25.get("report_type_trace", run.report_type_trace))
        if isinstance(outputs.get("motor_034"), dict):
            m34 = outputs["motor_034"]
            summary = m34.get("maturity_summary", {})
            readiness = m34.get("report_readiness_register", {})
            run.evidence_maturity_summary = dict(summary) if isinstance(summary, dict) else run.evidence_maturity_summary
            run.key_variable_bottlenecks = list(summary.get("key_bottlenecks", run.key_variable_bottlenecks)) if isinstance(summary, dict) else run.key_variable_bottlenecks
            if isinstance(readiness, dict):
                run.report_readiness_reason = readiness.get("reason", run.report_readiness_reason)
                allowed = readiness.get("report_type_allowed", [])
                prohibited = readiness.get("report_type_prohibited", [])
                if allowed and not run.allowed_report_classes:
                    run.allowed_report_classes = list(allowed)
                if prohibited:
                    run.prohibited_report_types = list(prohibited)
        if isinstance(outputs.get("motor_024"), dict):
            m24 = outputs["motor_024"]
            run.phase_self_evaluation_summary = dict(
                (m24.get("phase_self_evaluation_register", {}) or {}).get(
                    "summary",
                    run.phase_self_evaluation_summary,
                )
            )
            run.case_delta_summary = dict(m24.get("case_delta_register", run.case_delta_summary))
            run.source_yield_memory_summary = dict(
                m24.get("source_yield_memory_register", run.source_yield_memory_summary)
            )
            run.next_ingestion_priority_update = dict(
                m24.get("next_ingestion_priority_update", run.next_ingestion_priority_update)
            )
            ingestion_learning_register = dict(m24.get("ingestion_learning_register", {}) or {})
            run.ingestion_learning_summary = dict(
                ingestion_learning_register.get("summary", run.ingestion_learning_summary)
            )


# ── Helpers ───────────────────────────────────────────────────────────────────

def _make_run_id(pipeline_id: str, inputs: dict[str, Any]) -> str:
    raw = json.dumps(
        {
            "pipeline_id": pipeline_id,
            "inputs_hash": hash_inputs(inputs),
            "started_at": _now(),
            "nonce": uuid4().hex,
        },
        sort_keys=True,
        default=str,
    )
    return "run:" + hashlib.sha256(raw.encode()).hexdigest()[:16]


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _full_report_incomplete(results: dict[str, MotorRunResult], outputs: dict[str, dict[str, Any]]) -> bool:
    """Detecta runs completos que terminaron sin un entregable PDF utilizable.

    Esta condición no debe aparecer como `completed`, porque rompería la
    semántica del framework: el pipeline pudo no lanzar excepciones, pero el
    paquete final no quedó realmente disponible para revisión.
    """
    motor_ids = set(results)
    if "motor_017" not in motor_ids and "motor_027" not in motor_ids:
        return False

    m17 = outputs.get("motor_017", {})
    if "motor_017" in motor_ids:
        pdf_path = str(m17.get("pdf_path", "") or "")
        if m17.get("compilation_status") != "success" or not pdf_path or not Path(pdf_path).exists():
            return True

    m27 = outputs.get("motor_027", {})
    if "motor_027" in motor_ids:
        output_path = str(
            m27.get("output_path", "")
            or m27.get("pdf_output_path", "")
            or m27.get("pdf_source_path", "")
            or ""
        )
        delivered = bool(m27.get("delivered"))
        if not delivered or not output_path or not Path(output_path).exists():
            return True

    return False


def _has_stub_truth(results: dict[str, MotorRunResult]) -> bool:
    return any(r.output_state == "stub" or r.truth_state in {"stub", "cached_stub", "completed_stub"} for r in results.values())


def _overall_status(
    results: dict[str, MotorRunResult],
    outputs: dict[str, dict[str, Any]],
) -> PipelineStatus:
    statuses = {r.status for r in results.values()}
    if MotorRunStatus.FAILED in statuses:
        return PipelineStatus.FAILED
    if _full_report_incomplete(results, outputs):
        return PipelineStatus.PARTIAL
    if _has_stub_truth(results):
        return PipelineStatus.COMPLETED_WITH_STUBS
    return PipelineStatus.COMPLETED


def _implementation_state(adapter: Any) -> str:
    if adapter is None:
        return "missing"
    return "placeholder" if type(adapter).__name__ == "StubMotorAdapter" else "implemented"


def _output_state_from_envelope(envelope: dict[str, Any] | None) -> str:
    if not envelope:
        return "unknown"
    output = envelope.get("output", {})
    if isinstance(output, dict) and output.get("__stub__") is True:
        return "stub"
    if envelope.get("adapter_class") == "StubMotorAdapter":
        return "stub"
    return "real"


class _MotorFailed(Exception):
    def __init__(self, motor_id: str, reason: str) -> None:
        super().__init__(f"{motor_id}: {reason}")
        self.motor_id = motor_id
        self.reason = reason


def _stable_inputs_for_hash(inputs: dict[str, Any]) -> dict[str, Any]:
    if not isinstance(inputs, dict):
        return inputs
    stable = dict(inputs)
    runtime = stable.get("__runtime__")
    if isinstance(runtime, dict):
        stable["__runtime__"] = {
            key: value
            for key, value in runtime.items()
            if key not in _RUNTIME_HASH_EXCLUDED_KEYS
        }
    bundles = stable.get("__bundles__")
    if isinstance(bundles, dict):
        # Hash bundles by content_hash only; produced_at/produced_by are
        # volatile and would invalidate cache on every run otherwise.
        stable["__bundles__"] = {
            mid: {
                "layer_id": entry.get("layer_id"),
                "bundle_version": entry.get("bundle_version"),
                "content_hash": entry.get("content_hash"),
            }
            for mid, entry in bundles.items()
            if isinstance(entry, dict)
        }
    return stable


def _publish_inferred_state_bundle(
    outputs: dict[str, dict[str, Any]],
    runtime_context: dict[str, Any],
) -> None:
    """Mirror the state mutated by _refresh_run_semantics into a LayerBundle.

    `_refresh_run_semantics` propagates inferred state (subject_definition,
    target_admissibility_state, asset_context_readiness, etc.) into the
    PipelineRun god-object so downstream motors can read it via
    `__runtime__`. That mutation is the legacy path; this helper publishes
    the same payload as a versioned LayerBundle (`pipeline_run` producer,
    layer="A") so downstream motors can opt in to the bus.

    Migration policy: emit both for now. Future commits can move motors one
    by one to read from the bundle, then retire `_refresh_run_semantics`.
    See RECOVERY_BACKLOG.md R-14b..R-23.
    """
    inferred_keys = (
        "subject_definition",
        "subject_contract_status",
        "subject_contract_admissibility",
        "subject_contract_warning_register",
        "ingestion_contract_status",
        "subject_resolution_state",
        "asset_authenticity_state",
        "target_type_classification",
        "asset_identity_status",
        "classification_confidence",
        "target_admissibility_state",
        "subject_gate_passed",
        "subject_gate_reason_register",
        "allowed_report_classes",
        "target_definition",
        "asset_context_readiness",
        "technical_substrate_readiness",
        "asset_level_evidence_found",
        "issuer_only_evidence_found",
        "recommended_report_type",
        "prohibited_report_types",
        "report_identity_state",
        "dominant_evidence_scope",
        "missing_observable_clusters",
        "evidence_maturity_summary",
        "key_variable_bottlenecks",
        "report_readiness_reason",
    )
    payload = {key: runtime_context.get(key) for key in inferred_keys}
    bundle = LayerBundle.make(
        layer_id="A",
        bundle_version=_DEFAULT_BUNDLE_VERSION,
        produced_by="pipeline_run.inferred_state",
        produced_at=_now(),
        payload=payload,
    )
    bundles: dict[str, dict[str, Any]] = outputs.setdefault("__bundles__", {})
    bundles["pipeline_run.inferred_state"] = bundle.to_dict()


def _populate_layer_bundles(
    outputs: dict[str, dict[str, Any]],
    level: list[str],
) -> None:
    """Auto-build LayerBundles for finished motors with a layer assignment.

    Mutates `outputs["__bundles__"]` in place. Idempotent: if a bundle for a
    motor already exists, it is overwritten with the latest payload (handles
    the rare case of force-rerun within the same level).

    Motors not in MOTOR_LAYER_MAP or assigned layer=None are skipped.
    """
    bundles: dict[str, dict[str, Any]] = outputs.setdefault("__bundles__", {})
    for motor_id in level:
        layer = MOTOR_LAYER_MAP.get(motor_id)
        if layer is None:
            continue
        motor_output = outputs.get(motor_id)
        if not isinstance(motor_output, dict) or not motor_output:
            continue
        bundle = LayerBundle.make(
            layer_id=layer,
            bundle_version=_DEFAULT_BUNDLE_VERSION,
            produced_by=motor_id,
            produced_at=_now(),
            payload=motor_output,
        )
        bundles[motor_id] = bundle.to_dict()


def _load_previous_pipeline_run_summary(
    pipeline_id: str,
    current_run_id: str,
) -> dict[str, Any]:
    # When the run-registry root is overridden, do not silently mix it with the
    # default on-disk learning store unless the caller explicitly injects a
    # custom loader. Tests and ad hoc reruns rely on that isolation.
    use_learning_store = not (
        DEFAULT_RUN_REGISTRY_DIR != _CONFIG_DEFAULT_RUN_REGISTRY_DIR
        and load_pipeline_learning_summary is _ORIGINAL_LOAD_PIPELINE_LEARNING_SUMMARY
    )
    learning_summary = load_pipeline_learning_summary(pipeline_id) if use_learning_store else {}
    if learning_summary and str(learning_summary.get("run_id", "")).strip() != str(current_run_id).strip():
        return learning_summary
    if not DEFAULT_RUN_REGISTRY_DIR.exists():
        return {}
    latest_payload: dict[str, Any] | None = None
    latest_sort_key = ""
    for path in DEFAULT_RUN_REGISTRY_DIR.glob("run:*.json"):
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if str(payload.get("pipeline_id", "")).strip() != str(pipeline_id).strip():
            continue
        if str(payload.get("run_id", "")).strip() == str(current_run_id).strip():
            continue
        sort_key = str(payload.get("completed_at") or payload.get("started_at") or "")
        if not sort_key:
            continue
        if sort_key > latest_sort_key:
            latest_sort_key = sort_key
            latest_payload = payload
    if latest_payload is None:
        return {}
    return {
        "run_id": latest_payload.get("run_id"),
        "pipeline_id": latest_payload.get("pipeline_id"),
        "completed_at": latest_payload.get("completed_at"),
        "status": latest_payload.get("status"),
        "recommended_report_type": latest_payload.get("recommended_report_type"),
        "report_type_trace": latest_payload.get("report_type_trace", {}),
        "phase_self_evaluation_summary": latest_payload.get("phase_self_evaluation_summary", {}),
        "evidence_maturity_summary": latest_payload.get("evidence_maturity_summary", {}),
        "key_variable_bottlenecks": latest_payload.get("key_variable_bottlenecks", []),
        "previous_run_id": latest_payload.get("previous_run_id"),
        "case_delta_summary": latest_payload.get("case_delta_summary", {}),
        "source_yield_memory_summary": latest_payload.get("source_yield_memory_summary", {}),
        "next_ingestion_priority_update": latest_payload.get("next_ingestion_priority_update", {}),
        "ingestion_learning_summary": latest_payload.get("ingestion_learning_summary", {}),
    }
