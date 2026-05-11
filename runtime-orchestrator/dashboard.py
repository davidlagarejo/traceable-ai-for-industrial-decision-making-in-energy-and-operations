#!/usr/bin/env python3
"""ZLab OTF — Monitor de control en tiempo real.

Uso:
    python dashboard.py           # http://localhost:7474
    python dashboard.py --open    # abre el navegador automáticamente
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import threading
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Mapping

from flask import Flask, jsonify, render_template_string, request, send_file
from target_seeds import build_address_seed, write_seed_file

_HERE            = Path(__file__).resolve().parent
_REPO_ROOT       = _HERE.parent
_SRC_DIR         = _HERE / "src"
_RUNS_DIR        = _HERE / "run-registry"
_COMBINATION_DECISION_DIR = _RUNS_DIR / "combination-decisions"
_COMBINATION_EDIT_DIR = _RUNS_DIR / "combination-edits"
_COMBINATION_REVIEW_CONTROL_DIR = _RUNS_DIR / "combination-review-controls"
_COMBINATION_FOLLOW_ON_MANIFEST_DIR = _RUNS_DIR / "combination-follow-on-manifests"
_LATENT_CLUSTER_OVERRIDE_DIR = _RUNS_DIR / "latent-cluster-overrides"
_PROMOTION_DECISION_DIR = _RUNS_DIR / "promotion-decisions"
_PROMOTION_EDIT_DIR = _RUNS_DIR / "promotion-edits"
_DISCOVERY_CANDIDATE_DECISION_DIR = _RUNS_DIR / "discovery-candidate-decisions"
_DISCOVERY_CANDIDATE_EDIT_DIR = _RUNS_DIR / "discovery-candidate-edits"
_DISCOVERY_QUEUE_MANIFEST_DIR = _RUNS_DIR / "licensed-discovery-queues"
_ARTICLE_REFERENCE_DIR = _RUNS_DIR / "article-reference-records"
_ACCEPTED_DISCOVERY_BUNDLE_DIR = _RUNS_DIR / "accepted-discovery-candidate-bundles"
_REFERENCE_BACKED_PROMOTION_DIR = _RUNS_DIR / "reference-backed-promotions"
_KNOWLEDGE_ATOM_REFRESH_DIR = _RUNS_DIR / "knowledge-atom-refresh"
_COMBINATION_RERANK_DIR = _RUNS_DIR / "combination-rerank"
_SEARCH_QUERY_EXECUTION_MANIFEST_DIR = _RUNS_DIR / "search-query-execution-manifests"
_SEARCH_QUERY_EXECUTION_SESSION_DIR = _RUNS_DIR / "search-query-execution-sessions"
_SEARCH_QUERY_RESULT_IMPORT_DIR = _RUNS_DIR / "search-query-result-imports"
_RESEARCH_CAMPAIGN_TRIGGER_DIR = _RUNS_DIR / "research-campaign-triggers"
_RESEARCH_LOOP_STATE_DIR = _RUNS_DIR / "research-loop-state"
_RESEARCH_LOOP_EVENT_DIR = _RUNS_DIR / "research-loop-events"
_RESEARCH_LOOP_JOB_DIR = _RUNS_DIR / "research-loop-jobs"
_RESEARCH_LOOP_METRIC_DIR = _RUNS_DIR / "research-loop-metrics"
_RESEARCH_LOOP_CONTROL_DIR = _RUNS_DIR / "research-loop-controls"
_REGISTRY_STAGE_CANDIDATE_DIR = _RUNS_DIR / "registry-stage-candidates"
_PROVIDER_SESSION_HANDOFF_DIR = _RUNS_DIR / "provider-session-handoffs"
_STORE_DIR       = _HERE / "artifact-store"
_OUTPUT_DIR      = _HERE / "output"
_SOURCE_REFRESH_STATUS = _HERE / "source_refresh_status.json"
_SOURCE_REFRESH_PID    = _HERE / "source_refresh.pid"
_LAUNCH_LOG_DIR  = Path("/tmp/zlab_runtime_launch_logs")
_MOTOR_CONTRACT  = _REPO_ROOT / "governanza" / "automation-base" / "motor_dependencies.json"

if str(_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_SRC_DIR))
try:
    from runtime_orchestrator.adapters import build_registry
    from runtime_orchestrator.adapters.motor_028 import (
        PRIMARY_SOURCE_CONTRACT,
        _EXTENDED_SOURCE_REGISTRY,
    )
    from runtime_orchestrator.asset_contracts import (
        derive_subject_definition,
        derive_target_definition,
    )
    from runtime_orchestrator.output_taxonomy import canonicalize_output_mode
    from runtime_orchestrator.run_registry import load_run_manifest
    from runtime_orchestrator.zlab_skill import (
        ALLOWED_COMBINATION_DECISIONS,
        apply_combination_validators,
        build_active_skill_pattern_state,
        build_admissible_combination_review_register,
        build_asset_context_vector,
        build_licensed_discovery_candidate_queue,
        build_combination_activation_register,
        build_combination_review_register,
        build_context_differentiator_register,
        build_latent_combination_cluster_register,
        build_latent_combination_candidate_register,
        build_combination_search_gap_record,
        build_combination_campaign_execution_manifest_register,
        build_combination_follow_on_research_register,
        build_query_seed_candidate_records as materialize_query_seed_candidate_records,
        build_research_campaign_record,
        build_research_campaign_trigger_register,
        build_research_loop_event_records,
        build_research_loop_snapshot,
        build_search_query_execution_batch_plan,
        build_search_query_execution_register,
        build_search_query_result_option_batch_plan,
        build_search_query_result_option_review_sequence,
        build_search_query_execution_sequence,
        build_search_query_result_option_register,
        build_search_result_capture_register,
        build_search_result_capture_sequence,
        build_reference_resolution_prefill,
        build_source_family_coverage_register,
        build_source_family_trigger_plan,
        build_provider_session_plan,
        build_provider_bootstrap_plan,
        build_structured_prior_candidates_from_text,
        build_registry_pattern_activation_register,
        build_extraction_seed_from_manifest,
        build_extraction_review_register,
        build_extraction_promotion_registers,
        execute_licensed_document_acquisition,
        default_registry_root,
        default_provider_launch_url,
        licensed_research_acquisition_enabled,
        load_registry_bundle,
        build_knowledge_atom_register,
        build_knowledge_atom_refresh_summary,
        materialize_licensed_discovery_candidate_queue,
        merge_combination_review_with_decisions,
        normalize_combination_decision_record,
        rebuild_licensed_discovery_candidate_row,
        build_combination_rerank_summary,
        summarize_source_coverage,
        summarize_combination_decisions,
        validate_combination_spec,
        validate_pattern_spec,
    )
except Exception:
    build_registry = None
    PRIMARY_SOURCE_CONTRACT = []
    _EXTENDED_SOURCE_REGISTRY = []
    derive_subject_definition = None
    derive_target_definition = None
    canonicalize_output_mode = lambda value: str(value or "").strip()
    load_run_manifest = None
    ALLOWED_COMBINATION_DECISIONS = {"candidate", "accepted_for_case_use", "rejected_for_case_use", "needs_review", "blocked_by_validator"}
    apply_combination_validators = None
    build_active_skill_pattern_state = None
    build_admissible_combination_review_register = None
    build_asset_context_vector = None
    build_licensed_discovery_candidate_queue = None
    build_combination_activation_register = None
    build_combination_review_register = None
    build_context_differentiator_register = None
    build_latent_combination_cluster_register = None
    build_latent_combination_candidate_register = None
    build_combination_search_gap_record = None
    build_combination_campaign_execution_manifest_register = None
    build_combination_follow_on_research_register = None
    materialize_query_seed_candidate_records = None
    build_research_campaign_record = None
    build_research_campaign_trigger_register = None
    build_research_loop_event_records = None
    build_research_loop_snapshot = None
    build_search_query_execution_batch_plan = None
    build_search_query_execution_register = None
    build_search_query_result_option_batch_plan = None
    build_search_query_result_option_review_sequence = None
    build_search_query_execution_sequence = None
    build_search_query_result_option_register = None
    build_search_result_capture_register = None
    build_search_result_capture_sequence = None
    build_reference_resolution_prefill = None
    build_source_family_coverage_register = None
    build_source_family_trigger_plan = None
    build_provider_session_plan = None
    build_provider_bootstrap_plan = None
    build_structured_prior_candidates_from_text = None
    build_registry_pattern_activation_register = None
    build_extraction_seed_from_manifest = None
    build_extraction_review_register = None
    build_extraction_promotion_registers = None
    execute_licensed_document_acquisition = None
    default_registry_root = None
    default_provider_launch_url = None
    licensed_research_acquisition_enabled = None
    load_registry_bundle = None
    build_knowledge_atom_register = None
    build_knowledge_atom_refresh_summary = None
    materialize_licensed_discovery_candidate_queue = None
    merge_combination_review_with_decisions = None
    normalize_combination_decision_record = None
    rebuild_licensed_discovery_candidate_row = None
    build_combination_rerank_summary = None
    summarize_source_coverage = None
    summarize_combination_decisions = None
    validate_combination_spec = None
    validate_pattern_spec = None

app = Flask(__name__)


@app.after_request
def _disable_cache(resp):
    resp.headers["Cache-Control"] = "no-store, no-cache, must-revalidate, max-age=0"
    resp.headers["Pragma"] = "no-cache"
    resp.headers["Expires"] = "0"
    return resp

# ── Motores críticos de análisis / reporte ───────────────────────────────────
_FOCUS_MOTORS = {
    "motor_013": "Activación de casos de inferencia",
    "motor_014": "Decision Core / inferencia",
    "motor_015": "Composición de bloques de salida",
    "motor_016": "Ensamble del paquete de reporte",
    "motor_018": "Generación de charts",
    "motor_019": "Escritura LLM",
}

_PRIMARY_FALLBACK_CONTRACT = [
    {
        "source_type": "sec_edgar_submissions",
        "locator_tpl": "https://data.sec.gov/submissions/CIK{cik}.json",
        "discovery_reason": "CIK found in pipeline.subject.cik",
    },
    {
        "source_type": "sec_edgar_xbrl_facts",
        "locator_tpl": "https://data.sec.gov/api/xbrl/companyfacts/CIK{cik}.json",
        "discovery_reason": "XBRL structured financials from SEC EDGAR",
    },
    {
        "source_type": "nyc_open_data_property",
        "locator_tpl": "https://data.cityofnewyork.us/resource/yjxr-fw8i.json?parid={bbl}&$limit=5",
        "discovery_reason": "NYC DOF property assessment record for subject asset",
    },
]

_SKILL_PATTERN_NAME_TO_ID = {
    "forklift_charging_and_demand_spike_plausible": "warehouse_mhe_charging_demand_peak",
    "dock_infiltration_and_door_discipline_plausible": "warehouse_dock_infiltration_loss",
    "compressed_air_leakage_or_pressure_overuse_plausible": "compressed_air_leak_plausibility",
    "poor_lubrication_or_reactive_maintenance_plausible": "maintenance_maturity_not_evidenced",
    "schedule_and_after_hours_waste_plausible": "hvac_schedule_drift",
    "missing_control_boundary_visibility": "tenant_operator_boundary_unresolved",
}

_SKILL_POWER_QUALITY_HYPOTHESIS_TO_ID = {
    "power_quality_and_reactive_exposure_plausible": "reactive_power_exposure",
}

_SKILL_INVALID_COMPARISON_TO_ID = {
    "warehouse_area_only_comparison": "fair_comparison_invalid_area_metric",
    "area_based_energy_intensity_comparison": "benchmark_denominator_error",
}

_SKILL_COMPARISON_FAMILY_DEFAULTS = {
    "logistics_warehouse": "fair_comparison_invalid_area_metric",
    "cold_chain": "fair_comparison_invalid_area_metric",
}

_LICENSED_PROVIDER_STATUS_URLS = {
    "scopus": "https://www.scopus.com/record/display.uri?eid=2-s2.0-dashboard-status",
    "elsevier": "https://www.sciencedirect.com/science/article/pii/S0000000000000000",
    "ieee": "https://ieeexplore.ieee.org/document/1234567",
    "springer": "https://link.springer.com/article/10.1007/dashboard-status",
}

_ALLOWED_PROMOTION_DECISIONS = {
    "candidate",
    "accepted_for_registry_review",
    "rejected_for_registry_review",
    "needs_review",
    "blocked_by_validator",
}

_ALLOWED_DISCOVERY_CANDIDATE_DECISIONS = {
    "candidate",
    "accepted_for_reference_use",
    "rejected_for_reference_use",
    "needs_review",
}

_ALLOWED_RESEARCH_LOOP_CONTROL_STATES = {
    "active",
    "paused_by_operator",
    "stopped_by_operator",
}


# ── Helpers ───────────────────────────────────────────────────────────────────

def _contract_adapter_map() -> dict[str, str]:
    if build_registry is None:
        return {}
    try:
        registry = build_registry()
    except Exception:
        return {}
    adapters: dict[str, str] = {}
    for mid, _ in _motor_contract_list():
        adapter = registry.get(mid)
        adapters[mid] = type(adapter).__name__ if adapter is not None else ""
    return adapters


_CONTRACT_ADAPTERS: dict[str, str] = {}

def _load_json(path: Path) -> dict:
    try:
        return json.loads(path.read_text())
    except Exception:
        return {}


def _safe_store_component(value: str) -> str:
    return "".join(ch if ch.isalnum() or ch in {"-", "_", "."} else "_" for ch in str(value or "").strip()) or "default"


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _is_truthy_flag(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    normalized = _text(value).lower()
    return normalized in {"1", "true", "yes", "y", "on", "selected"}


def _looks_like_url_value(value: Any) -> bool:
    normalized = _text(value).lower()
    return normalized.startswith("https://") or normalized.startswith("http://") or normalized.startswith("www.")


def _extract_embedded_link_value(value: Any) -> tuple[str, str]:
    text = _text(value)
    if not text:
        return "", ""
    if text.startswith("[") and "](" in text and text.endswith(")"):
        try:
            label, remainder = text[1:].split("](", 1)
        except ValueError:
            return "", ""
        url = remainder[:-1].strip()
        if _looks_like_url_value(url):
            return label.strip(), url
    if " (" in text and text.endswith(")"):
        label, url = text.rsplit(" (", 1)
        url = url[:-1].strip()
        if _looks_like_url_value(url):
            return label.strip(), url
    return "", ""


def _is_rank_like_value(value: Any) -> bool:
    normalized = _text(value)
    if not normalized:
        return False
    compact = normalized.replace(".", "").replace(")", "").strip()
    return compact.isdigit()


def _normalize_clipboard_header_label(value: Any) -> str:
    text = _text(value).lower()
    return "".join(ch for ch in text if ch.isalnum())


def _strip_clipboard_header_prefix(value: Any) -> str:
    text = _text(value)
    return text[1:].strip() if text.startswith("#") else text


def _split_clipboard_header_parts(header_line: str) -> list[str]:
    first_line = _strip_clipboard_header_prefix(header_line)
    if "\t" in first_line:
        return [part.strip() for part in first_line.split("\t")]
    if "<TAB>" in first_line:
        return [part.strip() for part in first_line.split("<TAB>")]
    if "|" in first_line and ":" not in first_line:
        return [part.strip() for part in first_line.split("|")]
    return []


_CLIPBOARD_URL_HEADERS = {
    "url",
    "link",
    "href",
    "documentlink",
    "articlelink",
    "recordlink",
    "documenturl",
    "articleurl",
    "recordurl",
    "sourceurl",
}
_CLIPBOARD_TITLE_HEADERS = {
    "title",
    "documenttitle",
    "articletitle",
    "recordtitle",
    "name",
}
_CLIPBOARD_SNIPPET_HEADERS = {
    "snippet",
    "abstract",
    "abstracttext",
    "summary",
    "description",
    "preview",
    "indexterms",
    "keywords",
    "authorkeywords",
    "keyterms",
    "subjectareas",
    "subjectarea",
    "topics",
    "terms",
}
_CLIPBOARD_EXCERPT_HEADERS = {
    "excerpt",
    "referenceexcerpt",
    "visibleexcerpt",
    "fulltextexcerpt",
}
_CLIPBOARD_SELECTED_HEADERS = {
    "selected",
    "chosen",
    "pick",
    "picked",
}
_CLIPBOARD_NOTES_HEADERS = {
    "notes",
    "note",
    "comment",
    "comments",
}
_CLIPBOARD_IGNORED_HEADERS = {
    "rank",
    "position",
    "index",
}


def _detect_clipboard_header_mapping(parts: list[str]) -> dict[str, int]:
    normalized_headers = [_normalize_clipboard_header_label(part) for part in parts]
    if any(_looks_like_url_value(part) for part in parts):
        return {}
    mapping: dict[str, int] = {}
    for idx, header in enumerate(normalized_headers):
        if not header:
            continue
        if header in _CLIPBOARD_URL_HEADERS and "source_url" not in mapping:
            mapping["source_url"] = idx
        elif header in _CLIPBOARD_TITLE_HEADERS and "search_result_title" not in mapping:
            mapping["search_result_title"] = idx
        elif header in _CLIPBOARD_SNIPPET_HEADERS and "search_result_snippet" not in mapping:
            mapping["search_result_snippet"] = idx
        elif header in _CLIPBOARD_EXCERPT_HEADERS and "reference_excerpt" not in mapping:
            mapping["reference_excerpt"] = idx
        elif header in _CLIPBOARD_SELECTED_HEADERS and "selected" not in mapping:
            mapping["selected"] = idx
        elif header in _CLIPBOARD_NOTES_HEADERS and "notes" not in mapping:
            mapping["notes"] = idx
    if "source_url" not in mapping and "search_result_title" not in mapping:
        return {}
    return mapping


def _map_clipboard_cells_from_mapping(
    *,
    cells: list[str],
    header_parts: list[str],
    header_mapping: Mapping[str, int],
) -> dict[str, str]:
    source_url = _text(cells[header_mapping["source_url"]]) if "source_url" in header_mapping and header_mapping["source_url"] < len(cells) else ""
    search_result_title = _text(cells[header_mapping["search_result_title"]]) if "search_result_title" in header_mapping and header_mapping["search_result_title"] < len(cells) else ""
    embedded_title, embedded_url = _extract_embedded_link_value(search_result_title)
    if embedded_url and not source_url:
        source_url = embedded_url
        search_result_title = embedded_title
    search_result_snippet = _text(cells[header_mapping["search_result_snippet"]]) if "search_result_snippet" in header_mapping and header_mapping["search_result_snippet"] < len(cells) else ""
    reference_excerpt = _text(cells[header_mapping["reference_excerpt"]]) if "reference_excerpt" in header_mapping and header_mapping["reference_excerpt"] < len(cells) else ""
    selected = _text(cells[header_mapping["selected"]]) if "selected" in header_mapping and header_mapping["selected"] < len(cells) else ""
    explicit_notes = _text(cells[header_mapping["notes"]]) if "notes" in header_mapping and header_mapping["notes"] < len(cells) else ""
    used_indexes = set(header_mapping.values())
    extra_note_parts: list[str] = []
    for cell_index, cell_value in enumerate(cells):
        value = _text(cell_value)
        if not value or cell_index in used_indexes:
            continue
        header_label = header_parts[cell_index] if cell_index < len(header_parts) else ""
        normalized_header = _normalize_clipboard_header_label(header_label)
        if normalized_header in _CLIPBOARD_IGNORED_HEADERS:
            continue
        if header_label:
            extra_note_parts.append(f"{header_label}: {value}")
        else:
            extra_note_parts.append(value)
    note_segments = [segment for segment in [explicit_notes, " | ".join(extra_note_parts)] if segment]
    return {
        "source_url": source_url,
        "search_result_title": search_result_title,
        "search_result_snippet": search_result_snippet,
        "reference_excerpt": reference_excerpt,
        "selected": selected,
        "notes": " | ".join(note_segments),
    }


def _map_flexible_tsv_without_headers(parts: list[str]) -> dict[str, str]:
    url_index = -1
    source_url = ""
    embedded_url_index = -1
    embedded_title = ""
    for idx, part in enumerate(parts):
        candidate_title, candidate_url = _extract_embedded_link_value(part)
        if candidate_url:
            embedded_title = candidate_title
            source_url = candidate_url
            url_index = idx
            embedded_url_index = idx
            break
        if _looks_like_url_value(part):
            source_url = part.strip()
            url_index = idx
            break
    if url_index < 0 or not source_url:
        raise ValueError("ordered TSV import row must include a URL in one of its columns")

    title_index = -1
    search_result_title = embedded_title
    if not search_result_title:
        preceding_candidates = [
            (idx, value)
            for idx, value in enumerate(parts[:url_index])
            if _text(value) and not _looks_like_url_value(value) and not _is_rank_like_value(value)
        ]
        following_candidates = [
            (url_index + 1 + idx, value)
            for idx, value in enumerate(parts[url_index + 1 :])
            if _text(value) and not _looks_like_url_value(value) and not _is_rank_like_value(value)
        ]
        if preceding_candidates:
            title_index, title_value = preceding_candidates[0]
            search_result_title = _text(title_value)
        elif following_candidates:
            title_index, title_value = following_candidates[0]
            search_result_title = _text(title_value)

    used_indexes = {url_index}
    if embedded_url_index >= 0:
        used_indexes.add(embedded_url_index)
    if title_index >= 0:
        used_indexes.add(title_index)

    remaining_cells = [
        (idx, _text(value))
        for idx, value in enumerate(parts)
        if idx not in used_indexes and _text(value)
    ]
    after_cells = [(idx, value) for idx, value in remaining_cells if idx > url_index]
    before_cells = [(idx, value) for idx, value in remaining_cells if idx < url_index]
    snippet_index = -1
    if after_cells:
        snippet_index, search_result_snippet = after_cells[0]
    elif before_cells:
        snippet_index, search_result_snippet = before_cells[-1]
    else:
        search_result_snippet = ""
    note_cells = [
        value
        for idx, value in remaining_cells
        if idx != snippet_index and not (
            idx == 0
            and _is_rank_like_value(value)
        )
    ]
    return {
        "source_url": source_url,
        "search_result_title": search_result_title,
        "search_result_snippet": search_result_snippet,
        "reference_excerpt": "",
        "selected": "",
        "notes": " | ".join(note_cells),
    }


def _combination_decision_path(run_id: str) -> Path:
    return _COMBINATION_DECISION_DIR / f"{_safe_store_component(run_id)}.json"


def _combination_edit_path(run_id: str) -> Path:
    return _COMBINATION_EDIT_DIR / f"{_safe_store_component(run_id)}.json"


def _combination_review_control_path(run_id: str) -> Path:
    return _COMBINATION_REVIEW_CONTROL_DIR / f"{_safe_store_component(run_id)}.json"


def _combination_follow_on_manifest_path(run_id: str) -> Path:
    return _COMBINATION_FOLLOW_ON_MANIFEST_DIR / f"{_safe_store_component(run_id)}.json"


def _latent_cluster_override_path(run_id: str) -> Path:
    return _LATENT_CLUSTER_OVERRIDE_DIR / f"{_safe_store_component(run_id)}.json"


def _promotion_decision_path(run_id: str) -> Path:
    return _PROMOTION_DECISION_DIR / f"{_safe_store_component(run_id)}.json"


def _promotion_edit_path(run_id: str) -> Path:
    return _PROMOTION_EDIT_DIR / f"{_safe_store_component(run_id)}.json"


def _discovery_candidate_decision_path(run_id: str) -> Path:
    return _DISCOVERY_CANDIDATE_DECISION_DIR / f"{_safe_store_component(run_id)}.json"


def _discovery_candidate_edit_path(run_id: str) -> Path:
    return _DISCOVERY_CANDIDATE_EDIT_DIR / f"{_safe_store_component(run_id)}.json"


def _licensed_discovery_queue_manifest_path(run_id: str) -> Path:
    return _DISCOVERY_QUEUE_MANIFEST_DIR / f"{_safe_store_component(run_id)}.json"


def _article_reference_record_path(run_id: str) -> Path:
    return _ARTICLE_REFERENCE_DIR / f"{_safe_store_component(run_id)}.json"


def _accepted_discovery_candidate_bundle_path(run_id: str) -> Path:
    return _ACCEPTED_DISCOVERY_BUNDLE_DIR / f"{_safe_store_component(run_id)}.json"


def _reference_backed_promotion_manifest_path(run_id: str) -> Path:
    return _REFERENCE_BACKED_PROMOTION_DIR / f"{_safe_store_component(run_id)}.json"


def _knowledge_atom_refresh_path(run_id: str) -> Path:
    return _KNOWLEDGE_ATOM_REFRESH_DIR / f"{_safe_store_component(run_id)}.json"


def _combination_rerank_path(run_id: str) -> Path:
    return _COMBINATION_RERANK_DIR / f"{_safe_store_component(run_id)}.json"


def _search_query_execution_manifest_path(run_id: str) -> Path:
    return _SEARCH_QUERY_EXECUTION_MANIFEST_DIR / f"{_safe_store_component(run_id)}.json"


def _search_query_execution_session_path(run_id: str) -> Path:
    return _SEARCH_QUERY_EXECUTION_SESSION_DIR / f"{_safe_store_component(run_id)}.json"


def _search_query_result_import_path(run_id: str) -> Path:
    return _SEARCH_QUERY_RESULT_IMPORT_DIR / f"{_safe_store_component(run_id)}.json"


def _research_campaign_trigger_path(run_id: str) -> Path:
    return _RESEARCH_CAMPAIGN_TRIGGER_DIR / f"{_safe_store_component(run_id)}.json"


def _registry_stage_candidate_run_dir(run_id: str) -> Path:
    return _REGISTRY_STAGE_CANDIDATE_DIR / _safe_store_component(run_id)


def _registry_stage_candidate_manifest_path(run_id: str) -> Path:
    return _registry_stage_candidate_run_dir(run_id) / "manifest.json"


def _registry_stage_merge_manifest_path(run_id: str) -> Path:
    return _registry_stage_candidate_run_dir(run_id) / "merge-manifest.json"


def _provider_session_handoff_manifest_path(run_id: str) -> Path:
    return _PROVIDER_SESSION_HANDOFF_DIR / f"{_safe_store_component(run_id)}.json"


def _research_loop_state_path(run_id: str) -> Path:
    return _RESEARCH_LOOP_STATE_DIR / f"{_safe_store_component(run_id)}.json"


def _research_loop_event_path(run_id: str) -> Path:
    return _RESEARCH_LOOP_EVENT_DIR / f"{_safe_store_component(run_id)}.json"


def _research_loop_job_path(run_id: str) -> Path:
    return _RESEARCH_LOOP_JOB_DIR / f"{_safe_store_component(run_id)}.json"


def _research_loop_metric_path(run_id: str) -> Path:
    return _RESEARCH_LOOP_METRIC_DIR / f"{_safe_store_component(run_id)}.json"


def _research_loop_control_path(run_id: str) -> Path:
    return _RESEARCH_LOOP_CONTROL_DIR / f"{_safe_store_component(run_id)}.json"


def _load_combination_decision_store(run_id: str) -> dict[str, Any]:
    path = _combination_decision_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    decisions = list(payload.get("decisions", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "decisions": [row for row in decisions if str(row.get("combination_id", "")).strip()],
        "path": str(path),
    }


def _load_combination_edit_store(run_id: str) -> dict[str, Any]:
    path = _combination_edit_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    edits = list(payload.get("edits", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "edits": [row for row in edits if _text(row.get("combination_id"))],
        "path": str(path),
    }


def _load_combination_review_control_store(run_id: str) -> dict[str, Any]:
    path = _combination_review_control_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    deferred_combination_ids = [
        _text(item)
        for item in list(payload.get("deferred_combination_ids", []) or [])
        if _text(item)
    ]
    batch_size = int(payload.get("batch_size", 1) or 1)
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "deferred_combination_ids": deferred_combination_ids,
        "batch_size": max(min(batch_size, 10), 1),
        "path": str(path),
    }


def _load_combination_follow_on_manifest_store(run_id: str) -> dict[str, Any]:
    path = _combination_follow_on_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    manifests = list(payload.get("manifests", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "manifests": [row for row in manifests if _text(row.get("combination_id"))],
        "path": str(path),
        "exists": path.exists(),
    }


def _load_latent_cluster_override_store(run_id: str) -> dict[str, Any]:
    path = _latent_cluster_override_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    split_assignments = [
        row
        for row in list(payload.get("split_assignments", []) or [])
        if _text(row.get("candidate_id"))
    ]
    merge_assignments = [
        row
        for row in list(payload.get("merge_assignments", []) or [])
        if _text(row.get("source_cluster_id"))
    ]
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "split_assignments": split_assignments,
        "merge_assignments": merge_assignments,
        "path": str(path),
    }


def _load_promotion_decision_store(run_id: str) -> dict[str, Any]:
    path = _promotion_decision_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    decisions = list(payload.get("decisions", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "decisions": [row for row in decisions if str(row.get("promotion_id", "")).strip()],
        "path": str(path),
    }


def _load_promotion_edit_store(run_id: str) -> dict[str, Any]:
    path = _promotion_edit_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    edits = list(payload.get("edits", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "edits": [row for row in edits if str(row.get("promotion_id", "")).strip()],
        "path": str(path),
    }


def _load_discovery_candidate_decision_store(run_id: str) -> dict[str, Any]:
    path = _discovery_candidate_decision_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    decisions = list(payload.get("decisions", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "decisions": [row for row in decisions if str(row.get("candidate_id", "")).strip()],
        "path": str(path),
    }


def _load_discovery_candidate_edit_store(run_id: str) -> dict[str, Any]:
    path = _discovery_candidate_edit_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    edits = list(payload.get("edits", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "edits": [row for row in edits if str(row.get("candidate_id", "")).strip()],
        "path": str(path),
    }


def _load_licensed_discovery_queue_manifest(run_id: str) -> dict[str, Any]:
    path = _licensed_discovery_queue_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_article_reference_record_store(run_id: str) -> dict[str, Any]:
    path = _article_reference_record_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    records = list(payload.get("records", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "records": [row for row in records if str(row.get("candidate_id", "")).strip()],
        "path": str(path),
        "exists": path.exists(),
    }


def _load_accepted_discovery_candidate_bundle_manifest(run_id: str) -> dict[str, Any]:
    path = _accepted_discovery_candidate_bundle_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_reference_backed_promotion_manifest(run_id: str) -> dict[str, Any]:
    path = _reference_backed_promotion_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_knowledge_atom_refresh_summary(run_id: str) -> dict[str, Any]:
    path = _knowledge_atom_refresh_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_combination_rerank_summary(run_id: str) -> dict[str, Any]:
    path = _combination_rerank_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_search_query_execution_manifest(run_id: str) -> dict[str, Any]:
    path = _search_query_execution_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_search_query_execution_session_store(run_id: str) -> dict[str, Any]:
    path = _search_query_execution_session_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    rows = list(payload.get("rows", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "rows": [row for row in rows if _text(row.get("candidate_id"))],
        "path": str(path),
        "exists": path.exists(),
    }


def _load_search_query_result_import_store(run_id: str) -> dict[str, Any]:
    path = _search_query_result_import_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    rows = list(payload.get("result_records", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "result_records": [
            row
            for row in rows
            if _text(row.get("candidate_id")) and _text(row.get("source_url"))
        ],
        "path": str(path),
        "exists": path.exists(),
    }


def _load_research_campaign_trigger_store(run_id: str) -> dict[str, Any]:
    path = _research_campaign_trigger_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    triggers = list(payload.get("triggers", []) or [])
    return {
        "run_id": str(payload.get("run_id") or run_id).strip(),
        "updated_at": str(payload.get("updated_at", "")).strip(),
        "triggers": [row for row in triggers if _text(row.get("source_family"))],
        "path": str(path),
        "exists": path.exists(),
    }


def _load_registry_stage_candidate_manifest(run_id: str) -> dict[str, Any]:
    path = _registry_stage_candidate_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_registry_stage_merge_manifest(run_id: str) -> dict[str, Any]:
    path = _registry_stage_merge_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_provider_session_handoff_manifest(run_id: str) -> dict[str, Any]:
    path = _provider_session_handoff_manifest_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    payload["path"] = str(path)
    payload["exists"] = path.exists()
    return payload


def _load_research_loop_state_store(run_id: str) -> dict[str, Any]:
    path = _research_loop_state_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    state = dict(payload.get("state", {}) or {})
    current_job = dict(payload.get("current_job", {}) or {})
    return {
        "run_id": _text(payload.get("run_id")) or _text(run_id),
        "updated_at": _text(payload.get("updated_at")),
        "state": state,
        "current_job": current_job,
        "path": str(path),
        "exists": path.exists(),
    }


def _load_research_loop_job_store(run_id: str) -> dict[str, Any]:
    path = _research_loop_job_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    jobs = [
        dict(row)
        for row in list(payload.get("jobs", []) or [])
        if _text(row.get("job_id"))
    ]
    return {
        "run_id": _text(payload.get("run_id")) or _text(run_id),
        "updated_at": _text(payload.get("updated_at")),
        "jobs": jobs,
        "current_job": dict(payload.get("current_job", {}) or {}),
        "path": str(path),
        "exists": path.exists(),
    }


def _load_research_loop_metric_store(run_id: str) -> dict[str, Any]:
    path = _research_loop_metric_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    metrics = dict(payload.get("metrics", {}) or {})
    depth_enforcement = dict(payload.get("depth_enforcement", {}) or {})
    stop_condition = dict(payload.get("stop_condition", {}) or {})
    return {
        "run_id": _text(payload.get("run_id")) or _text(run_id),
        "updated_at": _text(payload.get("updated_at")),
        "metrics": metrics,
        "depth_enforcement": depth_enforcement,
        "stop_condition": stop_condition,
        "path": str(path),
        "exists": path.exists(),
    }


def _load_research_loop_event_store(run_id: str) -> dict[str, Any]:
    path = _research_loop_event_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    events = [
        dict(row)
        for row in list(payload.get("events", []) or [])
        if _text(row.get("event_id"))
    ]
    return {
        "run_id": _text(payload.get("run_id")) or _text(run_id),
        "updated_at": _text(payload.get("updated_at")),
        "events": events,
        "path": str(path),
        "exists": path.exists(),
    }


def _load_research_loop_control_store(run_id: str) -> dict[str, Any]:
    path = _research_loop_control_path(run_id)
    payload = _load_json(path) if path.exists() else {}
    control_state = _text(payload.get("control_state")) or "active"
    if control_state not in _ALLOWED_RESEARCH_LOOP_CONTROL_STATES:
        control_state = "active"
    return {
        "run_id": _text(payload.get("run_id")) or _text(run_id),
        "updated_at": _text(payload.get("updated_at")),
        "control_state": control_state,
        "requested_action": _text(payload.get("requested_action")) or "resume",
        "control_reason": _text(payload.get("control_reason")),
        "path": str(path),
        "exists": path.exists(),
    }


def _persist_combination_decision_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_combination_decision_store(run_id)
    decisions_by_id = {
        str(row.get("combination_id", "")).strip(): dict(row)
        for row in list(store.get("decisions", []) or [])
        if str(row.get("combination_id", "")).strip()
    }
    decisions_by_id[str(record.get("combination_id", "")).strip()] = dict(record)
    path = _combination_decision_path(run_id)
    _COMBINATION_DECISION_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": str(record.get("decision_timestamp", "")).strip(),
        "decisions": sorted(
            decisions_by_id.values(),
            key=lambda row: str(row.get("combination_id", "")).strip(),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_combination_edit_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_combination_edit_store(run_id)
    edits_by_id = {
        _text(row.get("combination_id")): dict(row)
        for row in list(store.get("edits", []) or [])
        if _text(row.get("combination_id"))
    }
    edits_by_id[_text(record.get("combination_id"))] = dict(record)
    path = _combination_edit_path(run_id)
    _COMBINATION_EDIT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _text(record.get("edit_timestamp")) or _utc_now_iso(),
        "edits": sorted(
            edits_by_id.values(),
            key=lambda row: _text(row.get("combination_id")),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_combination_review_control_store(
    run_id: str,
    *,
    deferred_combination_ids: list[str] | None = None,
    batch_size: int | None = None,
) -> dict[str, Any]:
    existing = _load_combination_review_control_store(run_id)
    normalized_batch_size = int(batch_size if batch_size is not None else existing.get("batch_size", 1) or 1)
    normalized_batch_size = max(min(normalized_batch_size, 10), 1)
    normalized_deferred = [
        _text(item)
        for item in list(deferred_combination_ids if deferred_combination_ids is not None else existing.get("deferred_combination_ids", []) or [])
        if _text(item)
    ]
    path = _combination_review_control_path(run_id)
    _COMBINATION_REVIEW_CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "deferred_combination_ids": sorted(set(normalized_deferred)),
        "batch_size": normalized_batch_size,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_combination_follow_on_manifest_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_combination_follow_on_manifest_store(run_id)
    manifests_by_id = {
        _text(row.get("combination_id")): dict(row)
        for row in list(store.get("manifests", []) or [])
        if _text(row.get("combination_id"))
    }
    manifests_by_id[_text(record.get("combination_id"))] = dict(record)
    path = _combination_follow_on_manifest_path(run_id)
    _COMBINATION_FOLLOW_ON_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "manifests": sorted(
            manifests_by_id.values(),
            key=lambda row: _text(row.get("combination_id")),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_latent_cluster_override_store(
    run_id: str,
    *,
    split_assignments: list[dict[str, Any]] | None = None,
    merge_assignments: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    path = _latent_cluster_override_path(run_id)
    _LATENT_CLUSTER_OVERRIDE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": _utc_now_iso(),
        "split_assignments": sorted(
            list(split_assignments or []),
            key=lambda row: (_text(row.get("target_cluster_id")), _text(row.get("candidate_id"))),
        ),
        "merge_assignments": sorted(
            list(merge_assignments or []),
            key=lambda row: (_text(row.get("target_cluster_id")), _text(row.get("source_cluster_id"))),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_latent_cluster_split_assignments(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_latent_cluster_override_store(run_id)
    split_by_candidate = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(store.get("split_assignments", []) or [])
        if _text(row.get("candidate_id"))
    }
    for candidate_id in list(record.get("candidate_ids", []) or []):
        split_by_candidate[_text(candidate_id)] = {
            "candidate_id": _text(candidate_id),
            "source_cluster_id": _text(record.get("source_cluster_id")),
            "target_cluster_id": _text(record.get("target_cluster_id")),
            "cluster_label": _text(record.get("cluster_label")),
            "decision_reason": _text(record.get("decision_reason")),
            "updated_at": _text(record.get("updated_at")) or _utc_now_iso(),
        }
    return _persist_latent_cluster_override_store(
        run_id,
        split_assignments=list(split_by_candidate.values()),
        merge_assignments=list(store.get("merge_assignments", []) or []),
    )


def _persist_latent_cluster_merge_assignment(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_latent_cluster_override_store(run_id)
    merge_by_source = {
        _text(row.get("source_cluster_id")): dict(row)
        for row in list(store.get("merge_assignments", []) or [])
        if _text(row.get("source_cluster_id"))
    }
    source_cluster_id = _text(record.get("source_cluster_id"))
    target_cluster_id = _text(record.get("target_cluster_id"))
    if source_cluster_id == target_cluster_id:
        merge_by_source.pop(source_cluster_id, None)
    else:
        merge_by_source[source_cluster_id] = {
            "source_cluster_id": source_cluster_id,
            "target_cluster_id": target_cluster_id,
            "decision_reason": _text(record.get("decision_reason")),
            "updated_at": _text(record.get("updated_at")) or _utc_now_iso(),
        }
    return _persist_latent_cluster_override_store(
        run_id,
        split_assignments=list(store.get("split_assignments", []) or []),
        merge_assignments=list(merge_by_source.values()),
    )


def _persist_promotion_decision_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_promotion_decision_store(run_id)
    decisions_by_id = {
        str(row.get("promotion_id", "")).strip(): dict(row)
        for row in list(store.get("decisions", []) or [])
        if str(row.get("promotion_id", "")).strip()
    }
    decisions_by_id[str(record.get("promotion_id", "")).strip()] = dict(record)
    path = _promotion_decision_path(run_id)
    _PROMOTION_DECISION_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": str(record.get("decision_timestamp", "")).strip(),
        "decisions": sorted(
            decisions_by_id.values(),
            key=lambda row: str(row.get("promotion_id", "")).strip(),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_promotion_edit_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_promotion_edit_store(run_id)
    edits_by_id = {
        str(row.get("promotion_id", "")).strip(): dict(row)
        for row in list(store.get("edits", []) or [])
        if str(row.get("promotion_id", "")).strip()
    }
    edits_by_id[str(record.get("promotion_id", "")).strip()] = dict(record)
    path = _promotion_edit_path(run_id)
    _PROMOTION_EDIT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": str(record.get("edit_timestamp", "")).strip(),
        "edits": sorted(
            edits_by_id.values(),
            key=lambda row: str(row.get("promotion_id", "")).strip(),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_discovery_candidate_decision_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_discovery_candidate_decision_store(run_id)
    decisions_by_id = {
        str(row.get("candidate_id", "")).strip(): dict(row)
        for row in list(store.get("decisions", []) or [])
        if str(row.get("candidate_id", "")).strip()
    }
    decisions_by_id[str(record.get("candidate_id", "")).strip()] = dict(record)
    path = _discovery_candidate_decision_path(run_id)
    _DISCOVERY_CANDIDATE_DECISION_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": str(record.get("decision_timestamp", "")).strip(),
        "decisions": sorted(
            decisions_by_id.values(),
            key=lambda row: str(row.get("candidate_id", "")).strip(),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_discovery_candidate_edit_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_discovery_candidate_edit_store(run_id)
    edits_by_id = {
        str(row.get("candidate_id", "")).strip(): dict(row)
        for row in list(store.get("edits", []) or [])
        if str(row.get("candidate_id", "")).strip()
    }
    edits_by_id[str(record.get("candidate_id", "")).strip()] = dict(record)
    path = _discovery_candidate_edit_path(run_id)
    _DISCOVERY_CANDIDATE_EDIT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": str(record.get("edit_timestamp", "")).strip(),
        "edits": sorted(
            edits_by_id.values(),
            key=lambda row: str(row.get("candidate_id", "")).strip(),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    return payload


def _persist_licensed_discovery_queue_manifest(run_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    path = _licensed_discovery_queue_manifest_path(run_id)
    _DISCOVERY_QUEUE_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    payload = dict(manifest or {})
    payload["run_id"] = run_id
    payload["stored_at"] = _utc_now_iso()
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _refresh_discovery_queue_manifest_summary(manifest: dict[str, Any]) -> dict[str, Any]:
    payload = dict(manifest or {})
    candidate_rows = list(payload.get("candidate_rows", []) or [])
    payload["summary"] = {
        "candidate_count": len(candidate_rows),
        "pattern_promotion_count": sum(int(row.get("pattern_promotion_count", 0) or 0) for row in candidate_rows),
        "combination_promotion_count": sum(int(row.get("combination_promotion_count", 0) or 0) for row in candidate_rows),
    }
    provider_keys = sorted({
        _text((row.get("metadata_payload", {}) or {}).get("provider_key")) or _text(row.get("provider_key"))
        for row in candidate_rows
        if _text((row.get("metadata_payload", {}) or {}).get("provider_key")) or _text(row.get("provider_key"))
    })
    payload["provider_key"] = provider_keys[0] if len(provider_keys) == 1 else ("mixed" if provider_keys else _text(payload.get("provider_key")))
    return payload


def _persist_discovery_candidate_manifest_row(
    run_id: str,
    candidate_row: dict[str, Any],
) -> dict[str, Any]:
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    candidate_rows = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(manifest.get("candidate_rows", []) or [])
        if _text(row.get("candidate_id"))
    }
    candidate_rows[_text(candidate_row.get("candidate_id"))] = dict(candidate_row)
    updated_manifest = dict(manifest or {})
    updated_manifest["candidate_rows"] = sorted(
        candidate_rows.values(),
        key=lambda row: _text(row.get("candidate_id")),
    )
    updated_manifest = _refresh_discovery_queue_manifest_summary(updated_manifest)
    return _persist_licensed_discovery_queue_manifest(run_id, updated_manifest)


def _persist_article_reference_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_article_reference_record_store(run_id)
    records_by_id = {
        str(row.get("candidate_id", "")).strip(): dict(row)
        for row in list(store.get("records", []) or [])
        if str(row.get("candidate_id", "")).strip()
    }
    records_by_id[str(record.get("candidate_id", "")).strip()] = dict(record)
    path = _article_reference_record_path(run_id)
    _ARTICLE_REFERENCE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": run_id,
        "updated_at": str(record.get("updated_at", "")).strip() or _utc_now_iso(),
        "records": sorted(
            records_by_id.values(),
            key=lambda row: str(row.get("candidate_id", "")).strip(),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _materialize_accepted_discovery_candidate_bundle(run_id: str, bundle: dict[str, Any]) -> dict[str, Any]:
    path = _accepted_discovery_candidate_bundle_path(run_id)
    _ACCEPTED_DISCOVERY_BUNDLE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "materialized_at": _utc_now_iso(),
        **dict(bundle or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_reference_backed_promotion_manifest(run_id: str, bundle: dict[str, Any]) -> dict[str, Any]:
    path = _reference_backed_promotion_manifest_path(run_id)
    _REFERENCE_BACKED_PROMOTION_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        **dict(bundle or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_search_query_execution_manifest(run_id: str, manifest: dict[str, Any]) -> dict[str, Any]:
    path = _search_query_execution_manifest_path(run_id)
    _SEARCH_QUERY_EXECUTION_MANIFEST_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        **dict(manifest or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_search_query_execution_session_store(
    run_id: str,
    rows: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    path = _search_query_execution_session_path(run_id)
    _SEARCH_QUERY_EXECUTION_SESSION_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "rows": list(rows or []),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _build_search_query_execution_session_bundle(
    *,
    batch_plan: Mapping[str, Any] | None,
    rows: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    plan = dict(batch_plan or {})
    all_rows = [dict(row) for row in list(rows or [])]
    candidate_ids = {_text(candidate_id) for candidate_id in list(plan.get("candidate_ids", []) or []) if _text(candidate_id)}
    session_rows: list[dict[str, Any]] = []
    for index, row in enumerate(all_rows, start=1):
        candidate_id = _text(row.get("candidate_id"))
        if candidate_ids and candidate_id not in candidate_ids:
            continue
        if _text(row.get("queue_status")) != "pending":
            continue
        if _text(row.get("execution_status")) != "search_ready_capture_pending":
            continue
        query_variants = list(row.get("query_variants", []) or [])
        session_rows.append(
            {
                "row_index": len(session_rows) + 1,
                "candidate_id": candidate_id,
                "title": _text(row.get("title")) or candidate_id,
                "provider_key": _text(row.get("provider_key")),
                "provider_display_name": _text(row.get("provider_display_name")),
                "source_family": _text(row.get("source_family")),
                "query_family": _text(row.get("query_family")),
                "launch_url": _text(row.get("launch_url")) or _text(row.get("source_url")),
                "search_line_1": _text(query_variants[0]) if len(query_variants) >= 1 else _text(row.get("primary_query")),
                "search_line_2": _text(query_variants[1]) if len(query_variants) >= 2 else _text(row.get("pivot_query")),
                "search_line_3": _text(query_variants[2]) if len(query_variants) >= 3 else "",
                "evidence_targets": [_text(item) for item in list(row.get("evidence_targets", []) or []) if _text(item)],
                "source_url": "",
                "search_result_title": "",
                "search_result_snippet": "",
                "reference_excerpt": "",
                "selected": False,
                "notes": "",
                "row_state": "awaiting_visible_result_capture",
            }
        )
    return {
        "available": bool(session_rows),
        "provider_key": _text(plan.get("provider_key")),
        "source_family": _text(plan.get("source_family")),
        "query_family": _text(plan.get("query_family")),
        "candidate_count": len(session_rows),
        "candidate_ids": [_text(row.get("candidate_id")) for row in session_rows if _text(row.get("candidate_id"))],
        "search_execution_provider_guide": dict(plan.get("search_execution_provider_guide", {}) or {}),
        "ordered_result_import_provider_capture_guide": dict(plan.get("ordered_result_import_provider_capture_guide", {}) or {}),
        "search_execution_provider_sheet_template": _text(plan.get("search_execution_provider_sheet_template")),
        "ordered_result_import_provider_capture_sheet_template": _text(plan.get("ordered_result_import_provider_capture_sheet_template")),
        "search_execution_capture_workbook_template": _text(plan.get("search_execution_capture_workbook_template")),
        "rows": session_rows,
        "summary": _summarize_search_query_execution_session_rows(session_rows),
    }


def _is_search_query_execution_session_row_ready(row: Mapping[str, Any] | None) -> bool:
    data = dict(row or {})
    return bool(
        _text(data.get("source_url"))
        and (
            _text(data.get("search_result_title"))
            or _text(data.get("search_result_snippet"))
            or _text(data.get("reference_excerpt"))
        )
    )


def _merge_search_query_execution_session_rows(
    *,
    base_rows: list[dict[str, Any]] | None,
    override_rows: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    merged_rows = [dict(row) for row in list(base_rows or [])]
    override_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(override_rows or [])
        if _text(row.get("candidate_id"))
    }
    editable_fields = {
        "source_url",
        "search_result_title",
        "search_result_snippet",
        "reference_excerpt",
        "selected",
        "notes",
    }
    for row in merged_rows:
        candidate_id = _text(row.get("candidate_id"))
        override = dict(override_by_id.get(candidate_id, {}) or {})
        if not override:
            continue
        for key in editable_fields:
            if key == "selected":
                if key in override:
                    row[key] = bool(override.get(key))
                continue
            value = _text(override.get(key))
            if value or key in override:
                row[key] = value
    return merged_rows


def _summarize_search_query_execution_session_rows(rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    session_rows = [dict(row) for row in list(rows or [])]
    filled_rows = sum(
        1
        for row in session_rows
        if any(
            _text(row.get(field))
            for field in (
                "source_url",
                "search_result_title",
                "search_result_snippet",
                "reference_excerpt",
                "notes",
            )
        )
        or bool(row.get("selected"))
    )
    ready_rows = sum(
        1 for row in session_rows if _is_search_query_execution_session_row_ready(row)
    )
    return {
        "candidate_count": len(session_rows),
        "pending_rows": len(session_rows),
        "filled_rows": filled_rows,
        "ready_rows": ready_rows,
        "row_state": "awaiting_visible_result_capture" if session_rows else "idle",
    }


def _persist_search_query_result_import_store(run_id: str, records: list[dict[str, Any]] | None) -> dict[str, Any]:
    path = _search_query_result_import_path(run_id)
    _SEARCH_QUERY_RESULT_IMPORT_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "result_records": list(records or []),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _find_imported_result_option_index(
    *,
    execution_row: Mapping[str, Any] | None,
    import_record: Mapping[str, Any] | None,
) -> int:
    row = dict(execution_row or {})
    record = dict(import_record or {})
    target_url = _text(record.get("source_url"))
    target_title = _text(record.get("search_result_title"))
    target_snippet = _text(record.get("search_result_snippet"))
    target_rank = int(_text(record.get("rank")) or 0)
    best_index = 0
    best_score = -1
    for option in list(row.get("imported_result_options", []) or []):
        option_url = _text((option or {}).get("source_url"))
        if not option_url or option_url != target_url:
            continue
        score = 8
        if target_rank and int((option or {}).get("rank", 0) or 0) == target_rank:
            score += 4
        if target_title and _text((option or {}).get("search_result_title")) == target_title:
            score += 2
        if target_snippet and _text((option or {}).get("search_result_snippet")) == target_snippet:
            score += 1
        if score > best_score:
            best_score = score
            best_index = int((option or {}).get("option_index", 0) or 0)
    return best_index


def _promote_search_query_result_option(
    *,
    run_id: str,
    candidate_id: str,
    option_index: int,
    notes_override: str = "",
) -> dict[str, Any]:
    imported_store = _load_search_query_result_import_store(run_id)
    candidate_options = [
        dict(row)
        for row in list(imported_store.get("result_records", []) or [])
        if _text(row.get("candidate_id")) == candidate_id
    ]
    candidate_options.sort(
        key=lambda row: (
            int(row.get("rank", 0) or 0) if int(row.get("rank", 0) or 0) > 0 else 9999,
            _text(row.get("search_result_title")) or _text(row.get("source_url")),
            _text(row.get("source_url")),
        )
    )
    if not candidate_options:
        raise ValueError("no imported search results available for candidate")
    selected_index = max(min(int(option_index or 1), len(candidate_options)), 1) - 1
    selected = dict(candidate_options[selected_index] or {})
    edit_record = _normalize_article_reference_search_result_capture_record(
        {
            "candidate_id": candidate_id,
            "source_url": selected.get("source_url"),
            "search_result_title": selected.get("search_result_title"),
            "search_result_snippet": selected.get("search_result_snippet"),
            "notes": notes_override or _text(selected.get("notes")) or "Promoted from imported search result option.",
        }
    )
    result = _execute_article_reference_edit(
        run_id=run_id,
        candidate_id=candidate_id,
        edit_record=edit_record,
    )
    return {
        "selected_option": {
            "option_index": selected_index + 1,
            **selected,
        },
        **result,
    }


def _resolve_search_query_result_option_with_excerpt(
    *,
    run_id: str,
    candidate_id: str,
    option_index: int,
    reference_excerpt: str,
    notes_override: str = "",
    auto_accept_discovery_candidate: bool = True,
) -> dict[str, Any]:
    imported_store = _load_search_query_result_import_store(run_id)
    candidate_options = [
        dict(row)
        for row in list(imported_store.get("result_records", []) or [])
        if _text(row.get("candidate_id")) == candidate_id
    ]
    candidate_options.sort(
        key=lambda row: (
            int(row.get("rank", 0) or 0) if int(row.get("rank", 0) or 0) > 0 else 9999,
            _text(row.get("search_result_title")) or _text(row.get("source_url")),
            _text(row.get("source_url")),
        )
    )
    if not candidate_options:
        raise ValueError("no imported search results available for candidate")
    selected_index = max(min(int(option_index or 1), len(candidate_options)), 1) - 1
    selected = dict(candidate_options[selected_index] or {})
    if not _text(selected.get("source_url")):
        raise ValueError("selected imported result is missing source_url")
    if not _text(reference_excerpt):
        raise ValueError("reference_excerpt is required")
    edit_record = _normalize_article_reference_edit_record(
        {
            "candidate_id": candidate_id,
            "auto_accept_discovery_candidate": auto_accept_discovery_candidate,
            "patch": {
                "source_url": _text(selected.get("source_url")),
                "search_result_title": _text(selected.get("search_result_title")),
                "search_result_snippet": _text(selected.get("search_result_snippet")),
                "reference_excerpt": _text(reference_excerpt),
                "notes": notes_override or _text(selected.get("notes")) or "Resolved from imported search result option.",
                "reference_state": "manual_text_enriched",
            },
        }
    )
    result = _execute_article_reference_edit(
        run_id=run_id,
        candidate_id=candidate_id,
        edit_record=edit_record,
    )
    return {
        "selected_option": {
            "option_index": selected_index + 1,
            **selected,
        },
        **result,
    }


def _persist_knowledge_atom_refresh_summary(run_id: str, summary: dict[str, Any]) -> dict[str, Any]:
    path = _knowledge_atom_refresh_path(run_id)
    _KNOWLEDGE_ATOM_REFRESH_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        **dict(summary or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_combination_rerank_summary(run_id: str, summary: dict[str, Any]) -> dict[str, Any]:
    path = _combination_rerank_path(run_id)
    _COMBINATION_RERANK_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        **dict(summary or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_research_campaign_trigger_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    store = _load_research_campaign_trigger_store(run_id)
    triggers_by_family = {
        _text(row.get("source_family")): dict(row)
        for row in list(store.get("triggers", []) or [])
        if _text(row.get("source_family"))
    }
    triggers_by_family[_text(record.get("source_family"))] = dict(record)
    path = _research_campaign_trigger_path(run_id)
    _RESEARCH_CAMPAIGN_TRIGGER_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _text(record.get("updated_at")) or _utc_now_iso(),
        "triggers": sorted(
            triggers_by_family.values(),
            key=lambda row: _text(row.get("source_family")),
        ),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_research_loop_state_record(run_id: str, state_record: dict[str, Any], current_job: dict[str, Any] | None = None) -> dict[str, Any]:
    path = _research_loop_state_path(run_id)
    _RESEARCH_LOOP_STATE_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "state": dict(state_record or {}),
        "current_job": dict(current_job or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_research_loop_job_store(run_id: str, jobs: list[dict[str, Any]] | None, current_job: dict[str, Any] | None = None) -> dict[str, Any]:
    path = _research_loop_job_path(run_id)
    _RESEARCH_LOOP_JOB_DIR.mkdir(parents=True, exist_ok=True)
    normalized_jobs = [
        dict(row)
        for row in list(jobs or [])
        if _text(row.get("job_id"))
    ]
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "jobs": normalized_jobs,
        "current_job": dict(current_job or (normalized_jobs[0] if normalized_jobs else {})),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_research_loop_metric_record(
    run_id: str,
    metrics: dict[str, Any],
    depth_enforcement: dict[str, Any] | None = None,
    stop_condition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    path = _research_loop_metric_path(run_id)
    _RESEARCH_LOOP_METRIC_DIR.mkdir(parents=True, exist_ok=True)
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "metrics": dict(metrics or {}),
        "depth_enforcement": dict(depth_enforcement or {}),
        "stop_condition": dict(stop_condition or {}),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _append_research_loop_events(run_id: str, event_rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    store = _load_research_loop_event_store(run_id)
    events_by_id = {
        _text(row.get("event_id")): dict(row)
        for row in list(store.get("events", []) or [])
        if _text(row.get("event_id"))
    }
    for row in list(event_rows or []):
        event_id = _text(row.get("event_id"))
        if not event_id:
            continue
        events_by_id[event_id] = dict(row)
    path = _research_loop_event_path(run_id)
    _RESEARCH_LOOP_EVENT_DIR.mkdir(parents=True, exist_ok=True)
    events = sorted(
        events_by_id.values(),
        key=lambda row: (_text(row.get("created_at")), _text(row.get("event_id"))),
    )
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "events": events,
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _persist_research_loop_control_record(run_id: str, record: dict[str, Any]) -> dict[str, Any]:
    path = _research_loop_control_path(run_id)
    _RESEARCH_LOOP_CONTROL_DIR.mkdir(parents=True, exist_ok=True)
    control_state = _text(record.get("control_state")) or "active"
    if control_state not in _ALLOWED_RESEARCH_LOOP_CONTROL_STATES:
        control_state = "active"
    payload = {
        "run_id": _text(run_id),
        "updated_at": _utc_now_iso(),
        "requested_action": _text(record.get("requested_action")) or "resume",
        "control_state": control_state,
        "control_reason": _text(record.get("control_reason")),
    }
    path.write_text(json.dumps(payload, indent=2, sort_keys=True), encoding="utf-8")
    payload["path"] = str(path)
    payload["exists"] = True
    return payload


def _utc_now_iso() -> str:
    return datetime.utcnow().replace(microsecond=0).isoformat() + "Z"


def _normalize_research_loop_control_record(payload: dict[str, Any]) -> dict[str, Any]:
    run_id = _text((payload or {}).get("run_id"))
    if not run_id:
        raise ValueError("`run_id` is required.")
    requested_action = _text((payload or {}).get("requested_action")).lower() or "resume"
    action_to_state = {
        "resume": "active",
        "active": "active",
        "pause": "paused_by_operator",
        "paused_by_operator": "paused_by_operator",
        "stop": "stopped_by_operator",
        "stopped_by_operator": "stopped_by_operator",
    }
    control_state = action_to_state.get(requested_action, "")
    if control_state not in _ALLOWED_RESEARCH_LOOP_CONTROL_STATES:
        raise ValueError("`requested_action` must be one of: resume, pause, stop.")
    control_reason = _text((payload or {}).get("control_reason"))
    if control_state in {"paused_by_operator", "stopped_by_operator"} and not control_reason:
        control_reason = "operator requested loop hold"
    return {
        "run_id": run_id,
        "requested_action": requested_action,
        "control_state": control_state,
        "control_reason": control_reason,
    }


def _normalize_promotion_decision_record(payload: dict[str, Any]) -> dict[str, Any]:
    promotion_id = _text((payload or {}).get("promotion_id"))
    if not promotion_id:
        raise ValueError("promotion_id is required")
    operator_decision = _text((payload or {}).get("operator_decision")) or "candidate"
    if operator_decision not in _ALLOWED_PROMOTION_DECISIONS:
        raise ValueError(f"operator_decision must be one of: {sorted(_ALLOWED_PROMOTION_DECISIONS)}")
    decision_scope = _text((payload or {}).get("decision_scope")) or "run"
    if decision_scope not in {"run", "session"}:
        raise ValueError("decision_scope must be one of: ['run', 'session']")
    return {
        "promotion_id": promotion_id,
        "promotion_type": _text((payload or {}).get("promotion_type")),
        "operator_decision": operator_decision,
        "decision_reason": _text((payload or {}).get("decision_reason")),
        "decision_scope": decision_scope,
        "decision_timestamp": _text((payload or {}).get("decision_timestamp")) or _utc_now_iso(),
    }


def _normalize_promotion_edit_record(payload: dict[str, Any]) -> dict[str, Any]:
    promotion_id = _text((payload or {}).get("promotion_id"))
    if not promotion_id:
        raise ValueError("promotion_id is required")
    promotion_type = _text((payload or {}).get("promotion_type"))
    if promotion_type not in {"pattern", "combination"}:
        raise ValueError("promotion_type must be one of: ['pattern', 'combination']")
    patch = dict((payload or {}).get("patch", {}) or {})
    if promotion_type == "pattern":
        normalized_patch = {
            "name": _text(patch.get("name")),
            "hypothesis": _text(patch.get("hypothesis")),
            "minimum_evidence_to_activate": [_text(item) for item in list(patch.get("minimum_evidence_to_activate", []) or []) if _text(item)],
            "minimum_evidence_to_confirm": [_text(item) for item in list(patch.get("minimum_evidence_to_confirm", []) or []) if _text(item)],
            "falsification_conditions": [_text(item) for item in list(patch.get("falsification_conditions", []) or []) if _text(item)],
            "allowed_claim_language": _text(patch.get("allowed_claim_language")),
            "prohibited_claim_language": _text(patch.get("prohibited_claim_language")),
            "financial_exposure_if_true": [_text(item) for item in list(patch.get("financial_exposure_if_true", []) or []) if _text(item)],
            "financial_exposure_if_false": [_text(item) for item in list(patch.get("financial_exposure_if_false", []) or []) if _text(item)],
            "tad_actions": [_text(item) for item in list(patch.get("tad_actions", []) or []) if _text(item)],
        }
    else:
        normalized_patch = {
            "name": _text(patch.get("name")),
            "combined_hypothesis": _text(patch.get("combined_hypothesis")),
            "minimum_evidence": [_text(item) for item in list(patch.get("minimum_evidence", []) or []) if _text(item)],
            "financial_exposure": [_text(item) for item in list(patch.get("financial_exposure", []) or []) if _text(item)],
            "tad_action": _text(patch.get("tad_action")),
            "prohibited_claims": [_text(item) for item in list(patch.get("prohibited_claims", []) or []) if _text(item)],
            "allowed_language": _text(patch.get("allowed_language")),
        }
    return {
        "promotion_id": promotion_id,
        "promotion_type": promotion_type,
        "patch": normalized_patch,
        "edit_timestamp": _utc_now_iso(),
    }


def _normalize_discovery_candidate_decision_record(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _text((payload or {}).get("candidate_id"))
    if not candidate_id:
        raise ValueError("candidate_id is required")
    operator_decision = _text((payload or {}).get("operator_decision")) or "candidate"
    if operator_decision not in _ALLOWED_DISCOVERY_CANDIDATE_DECISIONS:
        raise ValueError(f"operator_decision must be one of: {sorted(_ALLOWED_DISCOVERY_CANDIDATE_DECISIONS)}")
    return {
        "candidate_id": candidate_id,
        "operator_decision": operator_decision,
        "decision_reason": _text((payload or {}).get("decision_reason")),
        "decision_scope": "run",
        "decision_timestamp": _text((payload or {}).get("decision_timestamp")) or _utc_now_iso(),
    }


def _normalize_discovery_candidate_edit_record(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _text((payload or {}).get("candidate_id"))
    if not candidate_id:
        raise ValueError("candidate_id is required")
    patch = dict((payload or {}).get("patch", {}) or {})
    return {
        "candidate_id": candidate_id,
        "patch": {
            "title": _text(patch.get("title")),
            "abstract": _text(patch.get("abstract")),
            "source_url": _text(patch.get("source_url")),
            "notes": _text(patch.get("notes")),
            "expected_pdf_name": _text(patch.get("expected_pdf_name")),
            "keywords": list(patch.get("keywords", []) or []),
        },
        "edit_timestamp": _utc_now_iso(),
    }


def _normalize_combination_edit_record(payload: dict[str, Any]) -> dict[str, Any]:
    combination_id = _text((payload or {}).get("combination_id"))
    if not combination_id:
        raise ValueError("combination_id is required")
    patch = dict((payload or {}).get("patch", {}) or {})
    return {
        "combination_id": combination_id,
        "patch": {
            "combination_name": _text(patch.get("combination_name")) or _text(patch.get("name")),
            "combined_hypothesis": _text(patch.get("combined_hypothesis")),
            "strategic_risk": _text(patch.get("strategic_risk")),
            "minimum_evidence": [_text(item) for item in list(patch.get("minimum_evidence", []) or []) if _text(item)],
            "financial_exposure": [_text(item) for item in list(patch.get("financial_exposure", []) or []) if _text(item)],
            "tad_action": _text(patch.get("tad_action")),
            "prohibited_claims": [_text(item) for item in list(patch.get("prohibited_claims", []) or []) if _text(item)],
            "allowed_language": _text(patch.get("allowed_language")),
        },
        "edit_timestamp": _utc_now_iso(),
    }


def _normalize_combination_review_control_record(payload: dict[str, Any]) -> dict[str, Any]:
    deferred_combination_ids = [
        _text(item)
        for item in list((payload or {}).get("deferred_combination_ids", []) or [])
        if _text(item)
    ]
    batch_size = int((payload or {}).get("batch_size", 1) or 1)
    batch_size = max(min(batch_size, 10), 1)
    return {
        "deferred_combination_ids": sorted(set(deferred_combination_ids)),
        "batch_size": batch_size,
        "updated_at": _utc_now_iso(),
    }


def _normalize_latent_cluster_split_record(payload: dict[str, Any]) -> dict[str, Any]:
    source_cluster_id = _text((payload or {}).get("source_cluster_id"))
    if not source_cluster_id:
        raise ValueError("source_cluster_id is required")
    raw_candidate_ids = list((payload or {}).get("candidate_ids", []) or [])
    candidate_ids = [_text(item) for item in raw_candidate_ids if _text(item)]
    if not candidate_ids:
        raise ValueError("candidate_ids must include at least one candidate")
    cluster_label = _text((payload or {}).get("cluster_label"))
    target_cluster_id = _text((payload or {}).get("target_cluster_id"))
    if not target_cluster_id:
        split_seed = cluster_label or candidate_ids[0]
        target_cluster_id = f"cluster::split::{_safe_store_component(split_seed).lower()}"
    return {
        "source_cluster_id": source_cluster_id,
        "candidate_ids": candidate_ids,
        "target_cluster_id": target_cluster_id,
        "cluster_label": cluster_label,
        "decision_reason": _text((payload or {}).get("decision_reason")),
        "updated_at": _utc_now_iso(),
    }


def _normalize_latent_cluster_merge_record(payload: dict[str, Any]) -> dict[str, Any]:
    source_cluster_id = _text((payload or {}).get("source_cluster_id"))
    if not source_cluster_id:
        raise ValueError("source_cluster_id is required")
    target_cluster_id = _text((payload or {}).get("target_cluster_id"))
    if not target_cluster_id:
        raise ValueError("target_cluster_id is required")
    return {
        "source_cluster_id": source_cluster_id,
        "target_cluster_id": target_cluster_id,
        "decision_reason": _text((payload or {}).get("decision_reason")),
        "updated_at": _utc_now_iso(),
    }


def _normalize_research_campaign_trigger_record(payload: dict[str, Any]) -> dict[str, Any]:
    source_family = _text((payload or {}).get("source_family"))
    if not source_family:
        raise ValueError("source_family is required")
    status = _text((payload or {}).get("status")) or "queued"
    if status not in {"queued", "completed", "cancelled", "exhausted"}:
        raise ValueError("status must be one of: ['queued', 'completed', 'cancelled', 'exhausted']")
    recommended_provider_keys = [
        _text(item)
        for item in list((payload or {}).get("recommended_provider_keys", []) or [])
        if _text(item)
    ]
    return {
        "source_family": source_family,
        "display_name": _text((payload or {}).get("display_name")),
        "trigger_type": _text((payload or {}).get("trigger_type")) or "deeper_search",
        "campaign_mode": _text((payload or {}).get("campaign_mode")) or "standard",
        "campaign_status": _text((payload or {}).get("campaign_status")) or "coverage_building",
        "coverage_state": _text((payload or {}).get("coverage_state")) or "untouched",
        "status": status,
        "reason": _text((payload or {}).get("reason")),
        "search_focus": _text((payload or {}).get("search_focus")),
        "recommended_provider_keys": recommended_provider_keys,
        "current_document_count": int((payload or {}).get("current_document_count", 0) or 0),
        "target_document_count": int((payload or {}).get("target_document_count", 0) or 0),
        "current_knowledge_atom_count": int((payload or {}).get("current_knowledge_atom_count", 0) or 0),
        "target_knowledge_atom_count": int((payload or {}).get("target_knowledge_atom_count", 0) or 0),
        "target_document_delta": max(int((payload or {}).get("target_document_delta", 0) or 0), 0),
        "target_knowledge_atom_delta": max(int((payload or {}).get("target_knowledge_atom_delta", 0) or 0), 0),
        "queued_at": _text((payload or {}).get("queued_at")) or _utc_now_iso(),
        "updated_at": _utc_now_iso(),
    }


def _persist_follow_on_research_for_combination(
    run_id: str,
    *,
    combination_id: str,
    reason_prefix: str,
    combination_follow_on_research_register: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    follow_on_rows = list(combination_follow_on_research_register or [])
    target_row = next(
        (
            row
            for row in follow_on_rows
            if _text(row.get("combination_id")) == _text(combination_id)
        ),
        {},
    )
    persisted_rows: list[dict[str, Any]] = []
    for trigger_row in list(target_row.get("trigger_rows", []) or []):
        try:
            record = _normalize_research_campaign_trigger_record(
                {
                    **dict(trigger_row or {}),
                    "reason": f"{_text(reason_prefix)} {_text(trigger_row.get('reason'))}".strip(),
                    "status": "queued",
                }
            )
        except ValueError:
            continue
        _persist_research_campaign_trigger_record(run_id, record)
        persisted_rows.append(record)
    return persisted_rows


def _materialize_follow_on_execution_manifest_for_combination(
    run_id: str,
    *,
    combination_id: str,
    combination_follow_on_execution_manifest_register: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    manifest_rows = list(combination_follow_on_execution_manifest_register or [])
    target_row = next(
        (
            row
            for row in manifest_rows
            if _text(row.get("combination_id")) == _text(combination_id)
        ),
        {},
    )
    if not target_row:
        return {}
    record = {
        **dict(target_row),
        "materialized_at": _utc_now_iso(),
    }
    _persist_combination_follow_on_manifest_record(run_id, record)
    return record


def _apply_latent_cluster_overrides(
    *,
    latent_combination_candidate_register: list[dict[str, Any]],
    latent_combination_cluster_register: list[dict[str, Any]],
    admissible_combination_review_register: list[dict[str, Any]],
    override_store: dict[str, Any] | None = None,
) -> dict[str, Any]:
    candidate_rows_by_id = {
        _text(row.get("combination_id")): dict(row)
        for row in list(latent_combination_candidate_register or [])
        if _text(row.get("combination_id"))
    }
    base_cluster_by_candidate: dict[str, str] = {}
    base_cluster_rows_by_id = {
        _text(row.get("cluster_id")): dict(row)
        for row in list(latent_combination_cluster_register or [])
        if _text(row.get("cluster_id"))
    }
    for cluster_row in list(latent_combination_cluster_register or []):
        cluster_id = _text(cluster_row.get("cluster_id"))
        for candidate_id in list(cluster_row.get("candidate_ids", []) or []):
            if _text(candidate_id):
                base_cluster_by_candidate[_text(candidate_id)] = cluster_id

    split_target_by_candidate: dict[str, str] = {}
    split_label_by_target: dict[str, str] = {}
    for row in list((override_store or {}).get("split_assignments", []) or []):
        candidate_id = _text(row.get("candidate_id"))
        target_cluster_id = _text(row.get("target_cluster_id"))
        if candidate_id and target_cluster_id and candidate_id in candidate_rows_by_id:
            split_target_by_candidate[candidate_id] = target_cluster_id
            if _text(row.get("cluster_label")):
                split_label_by_target[target_cluster_id] = _text(row.get("cluster_label"))

    merge_target_by_source: dict[str, str] = {}
    for row in list((override_store or {}).get("merge_assignments", []) or []):
        source_cluster_id = _text(row.get("source_cluster_id"))
        target_cluster_id = _text(row.get("target_cluster_id"))
        if source_cluster_id and target_cluster_id and source_cluster_id != target_cluster_id:
            merge_target_by_source[source_cluster_id] = target_cluster_id

    def _resolve_cluster_id(cluster_id: str) -> str:
        current = _text(cluster_id)
        seen: set[str] = set()
        while current in merge_target_by_source and current not in seen:
            seen.add(current)
            current = _text(merge_target_by_source.get(current))
        return current

    effective_cluster_by_candidate: dict[str, str] = {}
    source_clusters_by_effective: dict[str, set[str]] = {}
    effective_clusters: dict[str, dict[str, Any]] = {}
    for candidate_id, row in candidate_rows_by_id.items():
        source_cluster_id = base_cluster_by_candidate.get(candidate_id) or f"cluster::unassigned::{_safe_store_component(candidate_id).lower()}"
        starting_cluster_id = split_target_by_candidate.get(candidate_id) or source_cluster_id
        effective_cluster_id = _resolve_cluster_id(starting_cluster_id)
        effective_cluster_by_candidate[candidate_id] = effective_cluster_id
        source_clusters_by_effective.setdefault(effective_cluster_id, set()).add(source_cluster_id)
        source_clusters_by_effective.setdefault(effective_cluster_id, set()).add(starting_cluster_id)

        bucket = effective_clusters.setdefault(
            effective_cluster_id,
            {
                "cluster_id": effective_cluster_id,
                "candidate_ids": [],
                "pattern_ids": set(),
                "top_score": 0,
                "context_binding_insufficiency_risk": "clear",
                "combination_families": set(),
                "context_signatures": set(),
                "override_state": "base",
            },
        )
        bucket["candidate_ids"].append(candidate_id)
        bucket["pattern_ids"].update(list(row.get("pattern_ids", []) or []))
        bucket["top_score"] = max(int(bucket.get("top_score", 0) or 0), int(row.get("score", 0) or 0))
        if _text(row.get("context_binding_insufficiency_risk")) == "raised":
            bucket["context_binding_insufficiency_risk"] = "raised"
        bucket["combination_families"].add(_text(row.get("combination_family")) or "cross_layer_structural")
        bucket["context_signatures"].add(_text((row.get("asset_context_vector", {}) or {}).get("context_signature")) or "")
        if starting_cluster_id != source_cluster_id and effective_cluster_id != starting_cluster_id:
            bucket["override_state"] = "split_and_merged"
        elif starting_cluster_id != source_cluster_id:
            bucket["override_state"] = "split"
        elif effective_cluster_id != source_cluster_id and bucket.get("override_state") == "base":
            bucket["override_state"] = "merged"

    adjusted_clusters: list[dict[str, Any]] = []
    for cluster_id, bucket in effective_clusters.items():
        family_candidates = sorted({value for value in bucket.get("combination_families", set()) if value})
        combination_family = family_candidates[0] if len(family_candidates) == 1 else "merged_cross_layer_structural"
        context_candidates = sorted({value for value in bucket.get("context_signatures", set()) if value})
        context_signature = context_candidates[0] if len(context_candidates) == 1 else "mixed-context"
        cluster_label = split_label_by_target.get(cluster_id, "")
        adjusted_clusters.append(
            {
                "cluster_id": cluster_id,
                "combination_family": combination_family,
                "context_signature": context_signature,
                "candidate_count": len(list(bucket.get("candidate_ids", []) or [])),
                "candidate_ids": list(bucket.get("candidate_ids", []) or []),
                "pattern_ids": sorted(set(bucket.get("pattern_ids", set()) or set())),
                "top_score": int(bucket.get("top_score", 0) or 0),
                "context_binding_insufficiency_risk": _text(bucket.get("context_binding_insufficiency_risk")) or "clear",
                "source_cluster_ids": sorted(source_clusters_by_effective.get(cluster_id, set()) or set()),
                "override_state": _text(bucket.get("override_state")) or "base",
                "cluster_label": cluster_label,
            }
        )
    adjusted_clusters.sort(
        key=lambda row: (
            -int(row.get("top_score", 0) or 0),
            -int(row.get("candidate_count", 0) or 0),
            _text(row.get("cluster_id")),
        )
    )

    adjusted_candidates: list[dict[str, Any]] = []
    for row in list(latent_combination_candidate_register or []):
        candidate_id = _text(row.get("combination_id"))
        adjusted_row = dict(row)
        adjusted_row["effective_cluster_id"] = effective_cluster_by_candidate.get(candidate_id, base_cluster_by_candidate.get(candidate_id, ""))
        adjusted_row["source_cluster_id"] = base_cluster_by_candidate.get(candidate_id, "")
        adjusted_candidates.append(adjusted_row)

    adjusted_admissible: list[dict[str, Any]] = []
    for row in list(admissible_combination_review_register or []):
        candidate_id = _text(row.get("combination_id"))
        adjusted_row = dict(row)
        adjusted_row["effective_cluster_id"] = effective_cluster_by_candidate.get(candidate_id, base_cluster_by_candidate.get(candidate_id, ""))
        adjusted_row["source_cluster_id"] = base_cluster_by_candidate.get(candidate_id, "")
        adjusted_admissible.append(adjusted_row)

    return {
        "latent_combination_candidate_register": adjusted_candidates,
        "latent_combination_cluster_register": adjusted_clusters,
        "admissible_combination_review_register": adjusted_admissible,
    }


def _merge_promotion_review_with_decisions(
    *,
    promotion_review_register: list[dict[str, Any]],
    decision_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    decisions_by_id = {
        _text(row.get("promotion_id")): dict(row)
        for row in list(decision_records or [])
        if _text(row.get("promotion_id"))
    }
    rows: list[dict[str, Any]] = []
    for row in list(promotion_review_register or []):
        normalized = dict(row)
        decision = decisions_by_id.get(_text(row.get("promotion_id")))
        if decision:
            normalized["operator_decision"] = _text(decision.get("operator_decision")) or "candidate"
            normalized["decision_reason"] = _text(decision.get("decision_reason"))
            normalized["decision_scope"] = _text(decision.get("decision_scope")) or "run"
            normalized["decision_timestamp"] = _text(decision.get("decision_timestamp"))
        else:
            normalized.setdefault("operator_decision", _text(row.get("operator_decision")) or "candidate")
            normalized.setdefault("decision_reason", "")
            normalized.setdefault("decision_scope", "run")
            normalized.setdefault("decision_timestamp", "")
        rows.append(normalized)
    return rows


def _summarize_promotion_decisions(promotion_review_register: list[dict[str, Any]] | None) -> dict[str, Any]:
    rows = list(promotion_review_register or [])
    counts = {key: 0 for key in sorted(_ALLOWED_PROMOTION_DECISIONS)}
    for row in rows:
        decision = _text(row.get("operator_decision")) or "candidate"
        if decision not in counts:
            counts[decision] = 0
        counts[decision] += 1
    return {
        "total": len(rows),
        "by_decision": counts,
        "accepted": counts.get("accepted_for_registry_review", 0),
        "rejected": counts.get("rejected_for_registry_review", 0),
        "needs_review": counts.get("needs_review", 0),
        "blocked": counts.get("blocked_by_validator", 0),
        "candidate": counts.get("candidate", 0),
    }


def _apply_promotion_edit(
    promotion_row: dict[str, Any],
    edit_record: dict[str, Any] | None,
) -> dict[str, Any]:
    row = dict(promotion_row or {})
    if not edit_record:
        return row
    proposed_spec = dict(row.get("proposed_spec", {}) or {})
    patch = dict((edit_record or {}).get("patch", {}) or {})
    for key, value in patch.items():
        if isinstance(value, list):
            if value:
                proposed_spec[key] = list(value)
        else:
            text_value = _text(value)
            if text_value:
                proposed_spec[key] = text_value
    row["proposed_spec"] = proposed_spec
    row["edit_timestamp"] = _text(edit_record.get("edit_timestamp"))
    return row


def _apply_combination_edit(
    combination_row: dict[str, Any],
    edit_record: dict[str, Any] | None,
) -> dict[str, Any]:
    row = dict(combination_row or {})
    if not edit_record:
        return row
    patch = dict((edit_record or {}).get("patch", {}) or {})
    for key, value in patch.items():
        if isinstance(value, list):
            if value:
                row[key] = list(value)
        else:
            text_value = _text(value)
            if text_value:
                row[key] = text_value
    row["edit_timestamp"] = _text(edit_record.get("edit_timestamp"))
    return row


def _apply_discovery_candidate_edit(
    candidate_row: dict[str, Any],
    edit_record: dict[str, Any] | None,
    *,
    registry_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    row = dict(candidate_row or {})
    if not edit_record:
        return row
    metadata_payload = dict(row.get("metadata_payload", {}) or {})
    patch = dict((edit_record or {}).get("patch", {}) or {})
    if _text(patch.get("title")):
        metadata_payload["title"] = _text(patch.get("title"))
    if _text(patch.get("abstract")):
        metadata_payload["abstract"] = _text(patch.get("abstract"))
    if _text(patch.get("source_url")):
        metadata_payload["source_url"] = _text(patch.get("source_url"))
    if _text(patch.get("notes")):
        metadata_payload["notes"] = _text(patch.get("notes"))
    keywords = list(patch.get("keywords", []) or [])
    if keywords:
        metadata_payload["keywords"] = [_text(item) for item in keywords if _text(item)]
    row["metadata_payload"] = metadata_payload
    if _text(patch.get("expected_pdf_name")):
        row["expected_pdf_name"] = _text(patch.get("expected_pdf_name"))
    if rebuild_licensed_discovery_candidate_row is None:
        row["edit_timestamp"] = _text(edit_record.get("edit_timestamp"))
        return row
    rebuilt = rebuild_licensed_discovery_candidate_row(
        candidate_row=row,
        registry_bundle=registry_bundle,
    )
    if _text(row.get("expected_pdf_name")):
        rebuilt["expected_pdf_name"] = _text(row.get("expected_pdf_name"))
    rebuilt["edit_timestamp"] = _text(edit_record.get("edit_timestamp"))
    return rebuilt


def _merge_discovery_review_with_decisions(
    *,
    discovery_review_register: list[dict[str, Any]],
    decision_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    decisions_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(decision_records or [])
        if _text(row.get("candidate_id"))
    }
    rows: list[dict[str, Any]] = []
    for row in list(discovery_review_register or []):
        normalized = dict(row)
        decision = decisions_by_id.get(_text(row.get("candidate_id")))
        if decision:
            normalized["operator_decision"] = _text(decision.get("operator_decision")) or "candidate"
            normalized["decision_reason"] = _text(decision.get("decision_reason"))
            normalized["decision_timestamp"] = _text(decision.get("decision_timestamp"))
        else:
            normalized.setdefault("operator_decision", _text(row.get("operator_decision")) or "candidate")
            normalized.setdefault("decision_reason", "")
            normalized.setdefault("decision_timestamp", "")
        rows.append(normalized)
    return rows


def _summarize_discovery_candidate_decisions(rows: list[dict[str, Any]] | None) -> dict[str, Any]:
    queue_rows = list(rows or [])
    counts = {key: 0 for key in sorted(_ALLOWED_DISCOVERY_CANDIDATE_DECISIONS)}
    for row in queue_rows:
        decision = _text(row.get("operator_decision")) or "candidate"
        if decision not in counts:
            counts[decision] = 0
        counts[decision] += 1
    return {
        "total": len(queue_rows),
        "by_decision": counts,
        "accepted": counts.get("accepted_for_reference_use", 0),
        "rejected": counts.get("rejected_for_reference_use", 0),
        "needs_review": counts.get("needs_review", 0),
        "candidate": counts.get("candidate", 0),
    }


def _build_combination_review_sequence(
    *,
    combination_review_register: list[dict[str, Any]] | None,
    admissible_combination_review_register: list[dict[str, Any]] | None,
    review_control_store: dict[str, Any] | None = None,
) -> dict[str, Any]:
    sequence_rows: list[dict[str, Any]] = []
    seen_ids: set[str] = set()
    deferred_ids = {
        _text(item)
        for item in list((review_control_store or {}).get("deferred_combination_ids", []) or [])
        if _text(item)
    }
    batch_size = max(min(int((review_control_store or {}).get("batch_size", 1) or 1), 10), 1)

    def _append_rows(rows: list[dict[str, Any]] | None, origin: str) -> None:
        for row in list(rows or []):
            combination_id = _text(row.get("combination_id"))
            if not combination_id or combination_id in seen_ids:
                continue
            seen_ids.add(combination_id)
            normalized = dict(row)
            normalized["review_origin"] = origin
            is_reviewable = _text(row.get("operator_decision")) == "candidate" and _text(row.get("validator_state")) != "blocked"
            normalized["queue_status"] = "pending" if is_reviewable else "closed"
            normalized["deferred"] = combination_id in deferred_ids
            sequence_rows.append(normalized)

    _append_rows(combination_review_register, "registered")
    _append_rows(admissible_combination_review_register, "latent")

    def _sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        queue_status = _text(row.get("queue_status"))
        decision = _text(row.get("operator_decision")) or "candidate"
        origin = _text(row.get("review_origin"))
        score = float(row.get("score", 0) or 0)
        origin_rank = 0 if origin == "registered" else 1
        decision_rank = 0 if decision == "candidate" else 1
        status_rank = 0 if queue_status == "pending" else 1
        deferred_rank = 1 if bool(row.get("deferred")) and queue_status == "pending" else 0
        return (status_rank, deferred_rank, decision_rank, origin_rank, -score, _text(row.get("combination_name")), _text(row.get("combination_id")))

    sequence_rows.sort(key=_sort_key)
    pending_rows = [row for row in sequence_rows if _text(row.get("queue_status")) == "pending"]
    current_row = dict(pending_rows[0]) if pending_rows else {}
    closed_count = len(sequence_rows) - len(pending_rows)
    return {
        "rows": sequence_rows,
        "current_row": current_row,
        "next_rows": pending_rows[1:max(batch_size, 1)],
        "summary": {
            "total": len(sequence_rows),
            "pending": len(pending_rows),
            "closed": closed_count,
            "deferred": sum(1 for row in pending_rows if bool(row.get("deferred"))),
            "current_position": (closed_count + 1) if pending_rows else 0,
            "batch_size": batch_size,
        },
    }


def _build_article_reference_record(
    *,
    candidate_row: dict[str, Any],
    reference_record: dict[str, Any] | None = None,
) -> dict[str, Any]:
    row = dict(candidate_row or {})
    reference = dict(reference_record or {})
    metadata = dict(row.get("metadata_payload", {}) or {})
    manifest = dict(row.get("manifest", {}) or {})
    acquisition_result = dict(reference.get("acquisition_result", {}) or {})
    visible_text = _text(acquisition_result.get("visible_text"))
    search_brief = _text(acquisition_result.get("search_brief"))
    notes = _text(acquisition_result.get("notes"))
    abstract = _text(metadata.get("abstract"))
    excerpt = visible_text[:400] if visible_text else (search_brief[:400] if search_brief else abstract[:400])
    state = _text(reference.get("reference_state")) or ("visible_text_enriched" if visible_text else "metadata_only")
    resolution_prefill = (
        build_reference_resolution_prefill(
            candidate_row=row,
            reference_record=reference,
        )
        if build_reference_resolution_prefill is not None
        else {}
    )
    provider_key = _text(metadata.get("provider_key")) or _text(reference.get("provider_key"))
    source_family = (
        _text(row.get("source_family"))
        or _text(metadata.get("source_family"))
        or _text(manifest.get("source_family"))
        or _text(reference.get("source_family"))
        or _text(acquisition_result.get("source_family"))
        or (
            "licensed_research_discovery"
            if provider_key == "scopus"
            else "licensed_research_fulltext"
            if provider_key in {"ieee", "springer", "elsevier"}
            else "public_technical_guidance"
        )
    )
    if state == "query_seed_draft":
        query_seed_parts = [
            _text(metadata.get("search_surface")),
            _text(metadata.get("execution_hint")),
            _text(metadata.get("primary_query")),
            _text(metadata.get("pivot_query")),
            _text(acquisition_result.get("search_result_title")),
            _text(acquisition_result.get("search_result_snippet")),
        ]
        enriched_search_brief = " | ".join(part for part in query_seed_parts if _text(part))
        if enriched_search_brief:
            acquisition_result["search_brief"] = enriched_search_brief
    return {
        "candidate_id": _text(row.get("candidate_id")),
        "provider_key": provider_key,
        "source_family": source_family,
        "title": _text(metadata.get("title")) or _text(row.get("title")),
        "doi": _text(metadata.get("doi")) or _text(row.get("doi")),
        "journal": _text(metadata.get("journal")) or _text(row.get("journal")),
        "published_year": _text(metadata.get("published_year")) or _text(row.get("published_year")),
        "source_url": _text(reference.get("source_url")) or _text(acquisition_result.get("final_url")) or _text(metadata.get("source_url")) or _text(row.get("source_url")),
        "reference_state": state,
        "reference_excerpt": excerpt,
        "keywords": list(metadata.get("keywords", []) or row.get("keywords", []) or []),
        "matched_pattern_ids": list(row.get("matched_pattern_ids", []) or []),
        "matched_combination_ids": list(row.get("matched_combination_ids", []) or []),
        "research_document_manifest": dict(reference.get("research_document_manifest", {}) or manifest),
        "acquisition_result": acquisition_result,
        "notes": notes,
        "draft_resolution_prefill": resolution_prefill,
        "updated_at": _text(reference.get("updated_at")),
    }


def _build_reference_resolution_sequence(
    *,
    article_reference_register: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    sequence_rows: list[dict[str, Any]] = []
    for row in list(article_reference_register or []):
        reference_state = _text(row.get("reference_state")) or "metadata_only"
        normalized = dict(row)
        normalized["queue_status"] = "pending" if reference_state == "query_seed_draft" else "closed"
        sequence_rows.append(normalized)

    def _sort_key(row: dict[str, Any]) -> tuple[Any, ...]:
        return (
            0 if _text(row.get("queue_status")) == "pending" else 1,
            _text(row.get("provider_key")),
            _text(row.get("title")) or _text(row.get("candidate_id")),
            _text(row.get("candidate_id")),
        )

    sequence_rows.sort(key=_sort_key)
    pending_rows = [row for row in sequence_rows if _text(row.get("queue_status")) == "pending"]
    current_row = dict(pending_rows[0]) if pending_rows else {}
    closed_count = len(sequence_rows) - len(pending_rows)
    return {
        "rows": sequence_rows,
        "current_row": current_row,
        "next_rows": pending_rows[1:4],
        "summary": {
            "total": len(sequence_rows),
            "pending": len(pending_rows),
            "closed": closed_count,
            "current_position": (closed_count + 1) if pending_rows else 0,
        },
    }


def _build_reference_resolution_batch_plan(
    *,
    article_reference_register: list[dict[str, Any]] | None,
    reference_resolution_sequence: dict[str, Any] | None,
) -> dict[str, Any]:
    def _packet_template_for_row(
        row: dict[str, Any],
        *,
        detailed: bool,
        include_url: bool,
    ) -> str:
        prefill = _prefill(row)
        hint_lines = [
            f"# Provider: {_text(prefill.get('provider_display_name')) or _text(row.get('provider_key')) or 'unknown'}",
            f"# Launch URL: {_text(prefill.get('launch_url')) or _text(row.get('source_url'))}",
            f"# Search surface: {_text(prefill.get('search_surface'))}",
            f"# Query family: {_text(prefill.get('query_family'))}",
            f"# Primary query: {_text(prefill.get('primary_query'))}",
            f"# Pivot query: {_text(prefill.get('pivot_query'))}",
            (
                f"# Evidence targets: {', '.join(_evidence_targets(row))}"
                if _evidence_targets(row)
                else ""
            ),
            f"# Execution hint: {_text(prefill.get('execution_hint'))}",
            f"# Search brief: {_text(prefill.get('search_brief')) or _text((row.get('acquisition_result', {}) or {}).get('search_brief'))}",
        ]
        hint_block = [line for line in hint_lines if _text(line)]
        body_lines: list[str] = []
        if include_url:
            body_lines.append(f"URL: {_text(row.get('source_url')) or _text(prefill.get('source_url'))}")
        if detailed:
            body_lines.extend(
                [
                    f"Title: {_text(prefill.get('title')) or _text(row.get('title'))}",
                    f"DOI: {_text(prefill.get('doi')) or _text(row.get('doi'))}",
                    f"Journal: {_text(prefill.get('journal')) or _text(row.get('journal'))}",
                    f"Year: {_text(prefill.get('published_year')) or _text(row.get('published_year'))}",
                ]
            )
        body_lines.extend(
            [
                f"Notes: {_text(row.get('notes')) or _text(prefill.get('suggested_notes')) or 'Resolved from query-seed draft.'}",
                "Excerpt:",
                "",
            ]
        )
        return "\n".join([*hint_block, *body_lines] if hint_block else body_lines)

    def _json_template_for_rows(
        rows: list[dict[str, Any]],
        *,
        detailed: bool,
        include_url: bool,
    ) -> str:
        payload_rows: list[dict[str, Any]] = []
        for row in rows:
            prefill = _prefill(row)
            payload: dict[str, Any] = {
                "candidate_id": _text(row.get("candidate_id")),
                "notes": _text(row.get("notes")) or _text(prefill.get("suggested_notes")) or "",
                "reference_excerpt": "",
            }
            if include_url:
                payload["source_url"] = _text(row.get("source_url")) or _text(prefill.get("source_url"))
            if detailed:
                payload["resolved_title"] = _text(prefill.get("title")) or _text(row.get("title"))
                payload["resolved_doi"] = _text(prefill.get("doi")) or _text(row.get("doi"))
                payload["resolved_journal"] = _text(prefill.get("journal")) or _text(row.get("journal"))
                payload["resolved_published_year"] = _text(prefill.get("published_year")) or _text(row.get("published_year"))
            payload_rows.append(payload)
        return json.dumps(payload_rows, indent=2, ensure_ascii=True)

    def _prefill(row: dict[str, Any]) -> dict[str, Any]:
        return dict(row.get("draft_resolution_prefill", {}) or {})

    def _query_family(row: dict[str, Any]) -> str:
        return _text(_prefill(row).get("query_family"))

    def _evidence_targets(row: dict[str, Any]) -> list[str]:
        prefill = _prefill(row)
        targets = [
            _text(item)
            for item in list(prefill.get("evidence_targets", []) or [])
            if _text(item)
        ]
        if targets:
            return list(dict.fromkeys(targets))
        search_intent = _text(prefill.get("search_intent"))
        return [search_intent] if search_intent else []

    def _evidence_signature(row: dict[str, Any]) -> str:
        targets = _evidence_targets(row)
        if targets:
            return " | ".join(sorted(targets))
        return _text(_prefill(row).get("search_intent"))

    def _select_rows(
        *,
        pending_rows: list[dict[str, Any]],
        current_provider: str,
        current_family: str,
        current_query_family: str,
        current_evidence_signature: str,
    ) -> tuple[list[dict[str, Any]], str]:
        tiers: list[tuple[str, list[dict[str, Any]]]] = []
        if current_provider and current_query_family and current_evidence_signature:
            tiers.append(
                (
                    "same_provider_same_query_family_same_evidence_intent",
                    [
                        row
                        for row in pending_rows
                        if _text(row.get("provider_key")) == current_provider
                        and _query_family(row) == current_query_family
                        and _evidence_signature(row) == current_evidence_signature
                    ],
                )
            )
        if current_family and current_query_family and current_evidence_signature:
            tiers.append(
                (
                    "same_source_family_same_query_family_same_evidence_intent",
                    [
                        row
                        for row in pending_rows
                        if _text(row.get("source_family")) == current_family
                        and _query_family(row) == current_query_family
                        and _evidence_signature(row) == current_evidence_signature
                    ],
                )
            )
        if current_provider and current_query_family:
            tiers.append(
                (
                    "same_provider_same_query_family",
                    [
                        row
                        for row in pending_rows
                        if _text(row.get("provider_key")) == current_provider
                        and _query_family(row) == current_query_family
                    ],
                )
            )
        if current_family and current_query_family:
            tiers.append(
                (
                    "same_source_family_same_query_family",
                    [
                        row
                        for row in pending_rows
                        if _text(row.get("source_family")) == current_family
                        and _query_family(row) == current_query_family
                    ],
                )
            )
        if current_provider:
            tiers.append(
                (
                    "same_provider",
                    [
                        row
                        for row in pending_rows
                        if _text(row.get("provider_key")) == current_provider
                    ],
                )
            )
        if current_family:
            tiers.append(
                (
                    "same_source_family",
                    [
                        row
                        for row in pending_rows
                        if _text(row.get("source_family")) == current_family
                    ],
                )
            )
        tiers.append(("mixed_pending", list(pending_rows)))

        first_non_empty: tuple[str, list[dict[str, Any]]] | None = None
        for mode, rows in tiers:
            if rows and first_non_empty is None:
                first_non_empty = (mode, rows)
            if len(rows) >= 2:
                return rows[:3], mode
        if first_non_empty is not None:
            return first_non_empty[1][:3], first_non_empty[0]
        return [], "none"

    sequence = dict(reference_resolution_sequence or {})
    current_row = dict(sequence.get("current_row", {}) or {})
    pending_rows = [
        dict(row)
        for row in list(sequence.get("rows", []) or [])
        if _text(row.get("queue_status")) == "pending"
    ]
    if not current_row or not pending_rows:
        return {
            "available": False,
            "batch_mode": "none",
            "candidate_count": 0,
            "candidate_rows": [],
            "provider_keys": [],
            "source_family": "",
            "packet_template": "",
            "summary": "",
            "query_families": [],
            "evidence_targets": [],
            "evidence_intent_signature": "",
            "batch_reason": "",
            "quick_packet_template": "",
            "full_packet_template": "",
            "captured_ready": False,
            "captured_quick_packet_template": "",
            "quick_json_template": "[]",
            "full_json_template": "[]",
            "captured_quick_json_template": "[]",
        }

    current_provider = _text(current_row.get("provider_key"))
    current_family = _text(current_row.get("source_family"))
    current_query_family = _query_family(current_row)
    current_evidence_signature = _evidence_signature(current_row)
    selected_rows, batch_mode = _select_rows(
        pending_rows=pending_rows,
        current_provider=current_provider,
        current_family=current_family,
        current_query_family=current_query_family,
        current_evidence_signature=current_evidence_signature,
    )

    provider_keys = []
    query_families = []
    evidence_targets = []
    for row in selected_rows:
        provider_key = _text(row.get("provider_key"))
        if provider_key and provider_key not in provider_keys:
            provider_keys.append(provider_key)
        query_family = _query_family(row)
        if query_family and query_family not in query_families:
            query_families.append(query_family)
        for target in _evidence_targets(row):
            if target not in evidence_targets:
                evidence_targets.append(target)

    batch_reason_map = {
        "same_provider_same_query_family_same_evidence_intent": "Grouped by same provider, same query family, and same evidence intent.",
        "same_source_family_same_query_family_same_evidence_intent": "Grouped by same source family, same query family, and same evidence intent.",
        "same_provider_same_query_family": "Grouped by same provider and same query family.",
        "same_source_family_same_query_family": "Grouped by same source family and same query family.",
        "same_provider": "Grouped by same provider when stronger query/evidence alignment was unavailable.",
        "same_source_family": "Grouped by same source family when provider/query alignment was unavailable.",
        "mixed_pending": "Mixed pending drafts because no stronger provider/query grouping was available.",
        "none": "No guided batch grouping available.",
    }
    batch_reason = batch_reason_map.get(batch_mode, batch_reason_map["mixed_pending"])

    packet_blocks: list[str] = []
    quick_packet_blocks: list[str] = []
    captured_quick_packet_blocks: list[str] = []
    captured_ready = all(
        bool(_text(row.get("source_url")) or _text(_prefill(row).get("source_url")))
        for row in selected_rows
    )
    for row in selected_rows:
        packet_blocks.append(
            "\n".join(
                [
                    f"Candidate ID: {_text(row.get('candidate_id'))}",
                    _packet_template_for_row(row, detailed=True, include_url=True),
                ]
            )
        )
        quick_packet_blocks.append(
            "\n".join(
                [
                    f"Candidate ID: {_text(row.get('candidate_id'))}",
                    _packet_template_for_row(row, detailed=False, include_url=True),
                ]
            )
        )
        if captured_ready:
            captured_quick_packet_blocks.append(
                "\n".join(
                    [
                        f"Candidate ID: {_text(row.get('candidate_id'))}",
                        _packet_template_for_row(row, detailed=False, include_url=False),
                    ]
                )
            )

    return {
        "available": True,
        "batch_mode": batch_mode,
        "candidate_count": len(selected_rows),
        "candidate_rows": selected_rows,
        "provider_keys": provider_keys,
        "source_family": current_family,
        "query_families": query_families,
        "evidence_targets": evidence_targets,
        "evidence_intent_signature": current_evidence_signature,
        "batch_reason": batch_reason,
        "resolution_hints": [
            {
                "candidate_id": _text(row.get("candidate_id")),
                "provider_key": _text(row.get("provider_key")),
                "launch_url": _text(_prefill(row).get("launch_url")) or _text(row.get("source_url")),
                "search_surface": _text(_prefill(row).get("search_surface")),
                "execution_hint": _text(_prefill(row).get("execution_hint")),
            }
            for row in selected_rows
        ],
        "packet_template": "\n---\n".join(quick_packet_blocks),
        "quick_packet_template": "\n---\n".join(quick_packet_blocks),
        "full_packet_template": "\n---\n".join(packet_blocks),
        "captured_ready": captured_ready,
        "captured_quick_packet_template": "\n---\n".join(captured_quick_packet_blocks),
        "quick_json_template": _json_template_for_rows(selected_rows, detailed=False, include_url=True),
        "full_json_template": _json_template_for_rows(selected_rows, detailed=True, include_url=True),
        "captured_quick_json_template": _json_template_for_rows(selected_rows, detailed=False, include_url=False) if captured_ready else "[]",
        "summary": (
            f"{batch_mode}: {len(selected_rows)} pending draft(s), "
            f"providers {', '.join(provider_keys) or 'unknown'}, "
            f"source family {current_family or 'unknown'}, "
            f"query families {', '.join(query_families) or 'unknown'}, "
            f"evidence targets {', '.join(evidence_targets) or 'unknown'}."
        ),
    }


def _reference_state_has_text(state: Any) -> bool:
    normalized = _text(state)
    return normalized in {"visible_text_enriched", "manual_text_enriched"}


def _is_query_seed_candidate(candidate_row: dict[str, Any] | None) -> bool:
    row = dict(candidate_row or {})
    candidate_id = _text(row.get("candidate_id"))
    notes = _text((row.get("metadata_payload", {}) or {}).get("notes"))
    return candidate_id.startswith("queryseed-") or "Primary query:" in notes


def _build_dashboard_extraction_record(
    *,
    extraction_payload: dict[str, Any] | None,
    candidate_row: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(extraction_payload or {})
    candidate = dict(candidate_row or {})
    metadata = dict(candidate.get("metadata_payload", {}) or {})
    payload["id"] = _text(payload.get("id")) or f"extract::dashboard::{_text(candidate.get('candidate_id')) or 'candidate'}"
    payload["provider_key"] = _text(payload.get("provider_key")) or _text(metadata.get("provider_key")) or _text(candidate.get("provider_key")) or "unknown_provider"
    payload["document_title"] = _text(payload.get("document_title")) or _text(metadata.get("title")) or _text(candidate.get("title"))
    payload["document_ref"] = (
        _text(payload.get("document_ref"))
        or _text(metadata.get("doi"))
        or _text(metadata.get("source_url"))
        or _text(candidate.get("doi"))
        or _text(candidate.get("source_url"))
        or _text(candidate.get("candidate_id"))
    )
    payload["source_basis_id"] = _text(payload.get("source_basis_id")) or "licensed_research_public_technical_priors"
    payload["retrieval_purpose"] = _text(payload.get("retrieval_purpose")) or "dashboard_discovery_candidate"
    payload["review_status"] = _text(payload.get("review_status")) or "auto_draft"
    payload["evidence_ceiling"] = _text(payload.get("evidence_ceiling")) or "L2"
    payload["structured_prior_only"] = bool(payload.get("structured_prior_only", True))
    payload["knowledge_atoms"] = list(payload.get("knowledge_atoms", []) or [])
    payload["pattern_candidate_records"] = list(payload.get("pattern_candidate_records", []) or [])
    payload["combination_candidate_records"] = list(payload.get("combination_candidate_records", []) or [])
    return payload


def _collect_licensed_extraction_records(
    *,
    knowledge_extraction_record: dict[str, Any] | None,
    discovery_candidate_rows: list[dict[str, Any]] | None,
    reference_backed_promotion_manifest: dict[str, Any] | None,
    activity: dict[str, Any] | None = None,
    run_d: dict[str, Any] | None = None,
) -> list[dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}

    def _store(record: dict[str, Any] | None) -> None:
        normalized = dict(record or {})
        record_id = _text(normalized.get("id"))
        if not record_id:
            return
        rows_by_id[record_id] = normalized

    if _text((knowledge_extraction_record or {}).get("id")):
        _store(dict(knowledge_extraction_record or {}))

    for record in list(dict(activity or {}).get("extraction_records", []) or []):
        _store(dict(record or {}))
    for record in list(dict(run_d or {}).get("extraction_records", []) or []):
        _store(dict(record or {}))
    for candidate_row in list(discovery_candidate_rows or []):
        extraction_payload = dict((candidate_row or {}).get("extraction_payload", {}) or {})
        if not extraction_payload:
            continue
        _store(
            _build_dashboard_extraction_record(
                extraction_payload=extraction_payload,
                candidate_row=dict(candidate_row or {}),
            )
        )
    for record in list(dict(reference_backed_promotion_manifest or {}).get("extraction_records", []) or []):
        _store(dict(record or {}))

    rows = list(rows_by_id.values())
    rows.sort(key=lambda row: (_text(row.get("provider_key")), _text(row.get("document_ref")), _text(row.get("id"))))
    return rows


def _build_accepted_discovery_candidate_bundle(
    *,
    run_id: str,
    discovery_review_register: list[dict[str, Any]] | None,
    discovery_candidate_rows: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
) -> dict[str, Any]:
    review_rows = list(discovery_review_register or [])
    candidate_rows = list(discovery_candidate_rows or [])
    reference_rows = list(article_reference_register or [])
    candidate_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in candidate_rows
        if _text(row.get("candidate_id"))
    }
    reference_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in reference_rows
        if _text(row.get("candidate_id"))
    }
    accepted_rows = [
        dict(row)
        for row in review_rows
        if _text(row.get("operator_decision")) == "accepted_for_reference_use"
    ]
    bundle_rows: list[dict[str, Any]] = []
    for review_row in accepted_rows:
        candidate_id = _text(review_row.get("candidate_id"))
        candidate_row = dict(candidate_by_id.get(candidate_id, {}) or {})
        reference_row = dict(reference_by_id.get(candidate_id, {}) or {})
        metadata_payload = dict(candidate_row.get("metadata_payload", {}) or {})
        bundle_rows.append(
            {
                "candidate_id": candidate_id,
                "provider_key": _text(review_row.get("provider_key")) or _text(metadata_payload.get("provider_key")),
                "title": _text(review_row.get("title")) or _text(metadata_payload.get("title")),
                "source_url": _text(review_row.get("source_url")) or _text(metadata_payload.get("source_url")),
                "doi": _text(review_row.get("doi")) or _text(metadata_payload.get("doi")),
                "journal": _text(review_row.get("journal")) or _text(metadata_payload.get("journal")),
                "published_year": _text(review_row.get("published_year")) or _text(metadata_payload.get("published_year")),
                "expected_pdf_name": _text(review_row.get("expected_pdf_name")) or _text(candidate_row.get("expected_pdf_name")),
                "priority_score": int(candidate_row.get("priority_score", review_row.get("priority_score", 0)) or 0),
                "matched_pattern_ids": list(review_row.get("matched_pattern_ids", []) or candidate_row.get("matched_pattern_ids", []) or []),
                "matched_combination_ids": list(review_row.get("matched_combination_ids", []) or candidate_row.get("matched_combination_ids", []) or []),
                "keywords": list(metadata_payload.get("keywords", []) or reference_row.get("keywords", []) or []),
                "reference_state": _text(reference_row.get("reference_state")) or _text(review_row.get("reference_state")) or "metadata_only",
                "reference_excerpt": _text(reference_row.get("reference_excerpt")),
                "decision_reason": _text(review_row.get("decision_reason")),
                "decision_timestamp": _text(review_row.get("decision_timestamp")),
                "updated_at": _text(reference_row.get("updated_at")),
            }
        )
    return {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        "summary": {
            "accepted_count": len(bundle_rows),
            "visible_text_enriched_count": sum(1 for row in bundle_rows if _reference_state_has_text(row.get("reference_state"))),
            "metadata_only_count": sum(1 for row in bundle_rows if _text(row.get("reference_state")) == "metadata_only"),
        },
        "accepted_rows": bundle_rows,
    }


def _build_reference_backed_promotion_bundle(
    *,
    run_id: str,
    discovery_candidate_rows: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
    accepted_discovery_candidate_bundle: dict[str, Any] | None,
    registry_bundle: dict[str, Any] | None,
) -> dict[str, Any]:
    if (
        build_structured_prior_candidates_from_text is None
        or build_extraction_seed_from_manifest is None
        or build_extraction_review_register is None
        or build_extraction_promotion_registers is None
    ):
        return {
            "run_id": _text(run_id),
            "generated_at": _utc_now_iso(),
            "summary": {"accepted_reference_count": 0, "extraction_count": 0, "pattern_promotion_count": 0, "combination_promotion_count": 0},
            "extraction_records": [],
            "extraction_review_register": [],
            "approved_pattern_promotion_register": [],
            "approved_combination_promotion_register": [],
        }

    candidate_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(discovery_candidate_rows or [])
        if _text(row.get("candidate_id"))
    }
    reference_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(article_reference_register or [])
        if _text(row.get("candidate_id"))
    }
    accepted_rows = list(dict(accepted_discovery_candidate_bundle or {}).get("accepted_rows", []) or [])
    extraction_records: list[dict[str, Any]] = []

    for accepted_row in accepted_rows:
        candidate_id = _text(accepted_row.get("candidate_id"))
        candidate_row = dict(candidate_by_id.get(candidate_id, {}) or {})
        reference_row = dict(reference_by_id.get(candidate_id, {}) or {})
        metadata = dict(candidate_row.get("metadata_payload", {}) or {})
        manifest = dict(reference_row.get("research_document_manifest", {}) or candidate_row.get("manifest", {}) or {})
        acquisition_result = dict(reference_row.get("acquisition_result", {}) or {})
        visible_text = _text(acquisition_result.get("visible_text"))
        abstract = _text(metadata.get("abstract")) or _text(accepted_row.get("reference_excerpt"))
        candidate_bundle = build_structured_prior_candidates_from_text(
            document_slug=candidate_id or "accepted-reference",
            title=_text(metadata.get("title")) or _text(accepted_row.get("title")),
            abstract=abstract,
            keywords=list(metadata.get("keywords", []) or accepted_row.get("keywords", []) or []),
            notes=_text(reference_row.get("notes")) or _text(metadata.get("notes")) or _text(accepted_row.get("decision_reason")),
            supplemental_text=visible_text,
            source_locator_prefix=f"dashboard_reference::{_text(run_id)}::{candidate_id}",
            registry_bundle=registry_bundle,
        )
        extraction_payload = dict(
            build_extraction_seed_from_manifest(
                research_document_manifest=manifest,
                source_basis_id="licensed_research_public_technical_priors",
                retrieval_purpose="dashboard_reference_refresh",
            )
        )
        extraction_payload.update(
            {
                "id": f"extract::dashboard_reference::{candidate_id}",
                "document_ref": _text(metadata.get("doi")) or _text(metadata.get("source_url")) or candidate_id,
                "review_status": "auto_draft",
                "notes": (
                    "Auto-draft regenerated from accepted discovery reference metadata plus visible reference text. "
                    "Requires operator review before registry promotion."
                ),
                "document_title": _text(metadata.get("title")) or _text(accepted_row.get("title")),
                "provider_key": _text(metadata.get("provider_key")) or _text(accepted_row.get("provider_key")),
                "structured_prior_only": True,
                **candidate_bundle,
            }
        )
        extraction_records.append(extraction_payload)

    extraction_review_register = build_extraction_review_register(extraction_records)
    promotion_bundle = build_extraction_promotion_registers(
        extraction_records,
        registry_bundle=registry_bundle,
    )
    return {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        "summary": {
            "accepted_reference_count": len(accepted_rows),
            "extraction_count": len(extraction_records),
            "pattern_promotion_count": len(list(promotion_bundle.get("approved_pattern_promotion_register", []) or [])),
            "combination_promotion_count": len(list(promotion_bundle.get("approved_combination_promotion_register", []) or [])),
        },
        "extraction_records": extraction_records,
        "extraction_review_register": extraction_review_register,
        **promotion_bundle,
    }


def _refresh_reference_backed_promotions_state(
    *,
    run_id: str,
    run_d: dict[str, Any] | None = None,
    candidate_id: str = "",
) -> dict[str, Any]:
    base_run = dict(run_d or _load_run(run_id) or {"run_id": run_id})
    previous_brain = _congruence_brain_activity(base_run)
    previous_licensed = dict(previous_brain.get("licensed_research", {}) or {})
    refreshed = previous_brain
    licensed = previous_licensed
    accepted_bundle = dict(licensed.get("accepted_discovery_candidate_bundle", {}) or {})
    accepted_count = int((accepted_bundle.get("summary", {}) or {}).get("accepted_count", 0) or 0)
    accepted_bundle_manifest = (
        _materialize_accepted_discovery_candidate_bundle(run_id, accepted_bundle)
        if accepted_count > 0
        else _load_accepted_discovery_candidate_bundle_manifest(run_id)
    )
    target_candidate_id = _text(candidate_id)
    if not accepted_count or load_registry_bundle is None:
        return {
            "refreshed": refreshed,
            "licensed": licensed,
            "accepted_bundle_manifest": accepted_bundle_manifest,
            "reference_backed_promotion_manifest": _load_reference_backed_promotion_manifest(run_id),
            "knowledge_atom_refresh_summary": _load_knowledge_atom_refresh_summary(run_id),
            "combination_rerank_summary": _load_combination_rerank_summary(run_id),
        }
    if target_candidate_id:
        accepted_rows = list(accepted_bundle.get("accepted_rows", []) or [])
        target_row = next(
            (
                row for row in accepted_rows
                if _text(row.get("candidate_id")) == target_candidate_id
            ),
            {},
        )
        if not target_row or not _reference_state_has_text(target_row.get("reference_state")):
            return {
                "refreshed": refreshed,
                "licensed": licensed,
                "accepted_bundle_manifest": accepted_bundle_manifest,
                "reference_backed_promotion_manifest": _load_reference_backed_promotion_manifest(run_id),
                "knowledge_atom_refresh_summary": _load_knowledge_atom_refresh_summary(run_id),
                "combination_rerank_summary": _load_combination_rerank_summary(run_id),
            }
    bundle = _build_reference_backed_promotion_bundle(
        run_id=run_id,
        discovery_candidate_rows=list(licensed.get("discovery_candidate_review_register", []) or []),
        article_reference_register=list(licensed.get("article_reference_register", []) or []),
        accepted_discovery_candidate_bundle=accepted_bundle,
        registry_bundle=load_registry_bundle(),
    )
    manifest = _persist_reference_backed_promotion_manifest(run_id, bundle)
    refreshed = _congruence_brain_activity(base_run)
    licensed = dict(refreshed.get("licensed_research", {}) or {})
    accepted_bundle = dict(licensed.get("accepted_discovery_candidate_bundle", {}) or {})
    accepted_count = int((accepted_bundle.get("summary", {}) or {}).get("accepted_count", 0) or 0)
    accepted_bundle_manifest = (
        _materialize_accepted_discovery_candidate_bundle(run_id, accepted_bundle)
        if accepted_count > 0
        else _load_accepted_discovery_candidate_bundle_manifest(run_id)
    )
    knowledge_atom_refresh_summary = (
        build_knowledge_atom_refresh_summary(
            run_id=run_id,
            candidate_id=target_candidate_id,
            previous_knowledge_atom_register=list(previous_licensed.get("knowledge_atom_register", []) or []),
            current_knowledge_atom_register=list(licensed.get("knowledge_atom_register", []) or []),
            previous_source_coverage_summary=dict(previous_licensed.get("source_coverage_summary", {}) or {}),
            current_source_coverage_summary=dict(licensed.get("source_coverage_summary", {}) or {}),
            previous_reference_backed_promotion_manifest=dict(previous_licensed.get("reference_backed_promotion_manifest", {}) or {}),
            current_reference_backed_promotion_manifest=manifest,
        )
        if build_knowledge_atom_refresh_summary is not None
        else {}
    )
    combination_rerank_summary = (
        build_combination_rerank_summary(
            run_id=run_id,
            previous_latent_combination_candidate_register=list(previous_brain.get("latent_combination_candidate_register", []) or []),
            current_latent_combination_candidate_register=list(refreshed.get("latent_combination_candidate_register", []) or []),
            previous_admissible_combination_review_register=list(previous_brain.get("admissible_combination_review_register", []) or []),
            current_admissible_combination_review_register=list(refreshed.get("admissible_combination_review_register", []) or []),
            previous_current_combination_review_row=dict(previous_brain.get("current_combination_review_row", {}) or {}),
            current_current_combination_review_row=dict(refreshed.get("current_combination_review_row", {}) or {}),
            previous_combination_review_sequence_register=list(previous_brain.get("combination_review_sequence_register", []) or []),
            current_combination_review_sequence_register=list(refreshed.get("combination_review_sequence_register", []) or []),
        )
        if build_combination_rerank_summary is not None
        else {}
    )
    if knowledge_atom_refresh_summary:
        knowledge_atom_refresh_summary = _persist_knowledge_atom_refresh_summary(run_id, knowledge_atom_refresh_summary)
    if combination_rerank_summary:
        combination_rerank_summary = _persist_combination_rerank_summary(run_id, combination_rerank_summary)
    licensed["knowledge_atom_refresh_summary"] = knowledge_atom_refresh_summary
    licensed["combination_rerank_summary"] = combination_rerank_summary
    refreshed["licensed_research"] = licensed
    return {
        "refreshed": refreshed,
        "licensed": licensed,
        "accepted_bundle_manifest": accepted_bundle_manifest,
        "reference_backed_promotion_manifest": manifest,
        "knowledge_atom_refresh_summary": knowledge_atom_refresh_summary,
        "combination_rerank_summary": combination_rerank_summary,
    }


def _merge_promotion_rows(
    *groups: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    rows_by_id: dict[str, dict[str, Any]] = {}
    ordered_ids: list[str] = []
    for group in groups:
        for row in list(group or []):
            normalized = dict(row or {})
            promotion_id = _text(normalized.get("promotion_id"))
            if not promotion_id:
                subject_id = _text(normalized.get("pattern_id")) or _text(normalized.get("combination_id"))
                prefix = "pattern" if _text(normalized.get("pattern_id")) else "combination"
                promotion_id = f"{prefix}::{subject_id}" if subject_id else ""
                if promotion_id:
                    normalized["promotion_id"] = promotion_id
            if not promotion_id:
                continue
            if promotion_id not in rows_by_id:
                ordered_ids.append(promotion_id)
            rows_by_id[promotion_id] = normalized
    return [rows_by_id[promotion_id] for promotion_id in ordered_ids]


def _read_article_reference_for_candidate(*, run_id: str, candidate_row: dict[str, Any]) -> dict[str, Any]:
    row = dict(candidate_row or {})
    metadata_payload = dict(row.get("metadata_payload", {}) or {})
    candidate_id = _text(row.get("candidate_id"))
    reference_record: dict[str, Any] = {
        "candidate_id": candidate_id,
        "provider_key": _text(metadata_payload.get("provider_key")),
        "reference_state": "metadata_only",
        "updated_at": _utc_now_iso(),
    }
    source_url = _text(metadata_payload.get("source_url")) or _text(row.get("source_url"))
    if _is_query_seed_candidate(row):
        search_brief = " ".join(
            part
            for part in [
                _text(metadata_payload.get("title")),
                _text(metadata_payload.get("notes")),
            ]
            if _text(part)
        ).strip()
        reference_record.update(
            {
                "reference_state": "query_seed_draft",
                "acquisition_result": {
                    "status": "query_seed_draft",
                    "error": "",
                    "requested_url": source_url,
                    "final_url": source_url,
                    "search_brief": search_brief,
                    "visible_text": "",
                    "notes": "Query-seed draft generated from combination follow-on research plan. Replace with real article excerpt when a concrete source is selected.",
                },
                "updated_at": _utc_now_iso(),
            }
        )
        store = _persist_article_reference_record(run_id, reference_record)
        return {
            "candidate_id": candidate_id,
            "reference_record": reference_record,
            "article_reference_store": {
                "updated_at": _text(store.get("updated_at")),
                "stored_record_count": len(list(store.get("records", []) or [])),
            },
        }
    if execute_licensed_document_acquisition is not None and source_url:
        try:
            package = execute_licensed_document_acquisition(
                url=source_url,
                retrieval_purpose="article_reference_read",
                technical_scraping_allowed=True,
                route_allowed=True,
                metadata=metadata_payload,
                session_label="licensed",
                headless=True,
                env=os.environ,
            )
            reference_record.update(
                {
                    "reference_state": "visible_text_enriched"
                    if _text(((package.get("acquisition_result", {}) or {}).get("visible_text")))
                    else "metadata_only",
                    "research_document_manifest": dict(package.get("research_document_manifest", {}) or {}),
                    "acquisition_result": dict(package.get("acquisition_result", {}) or {}),
                    "updated_at": _utc_now_iso(),
                }
            )
        except Exception as exc:
            reference_record.update(
                {
                    "reference_state": "metadata_only",
                    "acquisition_result": {"status": "error", "error": str(exc)},
                    "updated_at": _utc_now_iso(),
                }
            )
    store = _persist_article_reference_record(run_id, reference_record)
    return {
        "reference_record": reference_record,
        "article_reference_store": {
            "updated_at": _text(store.get("updated_at")),
            "stored_record_count": len(list(store.get("records", []) or [])),
        },
    }


def _normalize_article_reference_edit_record(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _text((payload or {}).get("candidate_id"))
    if not candidate_id:
        raise ValueError("candidate_id is required")
    patch = dict((payload or {}).get("patch", {}) or {})
    reference_excerpt = _text(patch.get("reference_excerpt"))
    notes = _text(patch.get("notes"))
    source_url = _text(patch.get("source_url"))
    resolved_title = _text(patch.get("resolved_title"))
    resolved_doi = _text(patch.get("resolved_doi"))
    resolved_journal = _text(patch.get("resolved_journal"))
    resolved_published_year = _text(patch.get("resolved_published_year"))
    search_result_title = _text(patch.get("search_result_title"))
    search_result_snippet = _text(patch.get("search_result_snippet"))
    return {
        "candidate_id": candidate_id,
        "auto_accept_discovery_candidate": bool((payload or {}).get("auto_accept_discovery_candidate", False)),
        "patch": {
            "reference_excerpt": reference_excerpt,
            "notes": notes,
            "source_url": source_url,
            "resolved_title": resolved_title,
            "resolved_doi": resolved_doi,
            "resolved_journal": resolved_journal,
            "resolved_published_year": resolved_published_year,
            "search_result_title": search_result_title,
            "search_result_snippet": search_result_snippet,
            "reference_state": _text(patch.get("reference_state")) or ("manual_text_enriched" if reference_excerpt else ""),
        },
        "updated_at": _utc_now_iso(),
    }


def _normalize_article_reference_quick_resolve_record(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _text((payload or {}).get("candidate_id"))
    if not candidate_id:
        raise ValueError("candidate_id is required")
    source_url = _text((payload or {}).get("source_url"))
    reference_excerpt = _text((payload or {}).get("reference_excerpt"))
    notes = _text((payload or {}).get("notes"))
    if not source_url:
        raise ValueError("source_url is required")
    if not reference_excerpt:
        raise ValueError("reference_excerpt is required")
    return _normalize_article_reference_edit_record(
        {
            "candidate_id": candidate_id,
            "auto_accept_discovery_candidate": (payload or {}).get("auto_accept_discovery_candidate", True),
            "patch": {
                "source_url": source_url,
                "reference_excerpt": reference_excerpt,
                "notes": notes,
                "reference_state": "manual_text_enriched",
            },
        }
    )


def _normalize_article_reference_search_result_capture_record(payload: dict[str, Any]) -> dict[str, Any]:
    candidate_id = _text((payload or {}).get("candidate_id"))
    if not candidate_id:
        raise ValueError("candidate_id is required")
    source_url = _text((payload or {}).get("source_url"))
    search_result_title = _text((payload or {}).get("search_result_title"))
    search_result_snippet = _text((payload or {}).get("search_result_snippet"))
    notes = _text((payload or {}).get("notes"))
    if not source_url:
        raise ValueError("source_url is required")
    if not search_result_title and not search_result_snippet:
        raise ValueError("search_result_title or search_result_snippet is required")
    return _normalize_article_reference_edit_record(
        {
            "candidate_id": candidate_id,
            "auto_accept_discovery_candidate": False,
            "patch": {
                "source_url": source_url,
                "search_result_title": search_result_title,
                "search_result_snippet": search_result_snippet,
                "notes": notes,
                "reference_state": "query_seed_draft",
            },
        }
    )


def _hydrate_reference_resolution_patch(
    *,
    candidate_row: dict[str, Any] | None,
    reference_record: dict[str, Any] | None,
    patch: dict[str, Any] | None,
) -> dict[str, str]:
    candidate = dict(candidate_row or {})
    reference = dict(reference_record or {})
    normalized_patch = dict(patch or {})
    metadata_payload = dict(candidate.get("metadata_payload", {}) or {})
    acquisition_result = dict(reference.get("acquisition_result", {}) or {})
    prefill = (
        build_reference_resolution_prefill(
            candidate_row=candidate,
            reference_record=reference,
        )
        if build_reference_resolution_prefill is not None
        else {}
    )
    hydrated = {
        "source_url": _text(normalized_patch.get("source_url"))
        or _text(reference.get("source_url"))
        or _text(acquisition_result.get("final_url"))
        or _text(prefill.get("source_url"))
        or _text(metadata_payload.get("source_url"))
        or _text(candidate.get("source_url")),
        "resolved_title": _text(normalized_patch.get("resolved_title"))
        or _text(acquisition_result.get("search_result_title"))
        or _text(prefill.get("title"))
        or _text(metadata_payload.get("title"))
        or _text(candidate.get("title")),
        "resolved_doi": _text(normalized_patch.get("resolved_doi"))
        or _text(prefill.get("doi"))
        or _text(metadata_payload.get("doi"))
        or _text(candidate.get("doi")),
        "resolved_journal": _text(normalized_patch.get("resolved_journal"))
        or _text(prefill.get("journal"))
        or _text(metadata_payload.get("journal"))
        or _text(candidate.get("journal")),
        "resolved_published_year": _text(normalized_patch.get("resolved_published_year"))
        or _text(prefill.get("published_year"))
        or _text(metadata_payload.get("published_year"))
        or _text(candidate.get("published_year")),
        "notes": _text(normalized_patch.get("notes"))
        or _text(acquisition_result.get("notes"))
        or _text(prefill.get("suggested_notes"))
        or "Resolved from query-seed draft.",
        "reference_excerpt": _text(normalized_patch.get("reference_excerpt")),
        "reference_state": _text(normalized_patch.get("reference_state")) or "manual_text_enriched",
    }
    if not _text(hydrated.get("source_url")):
        raise ValueError("source_url is required or must already be captured")
    if not _text(hydrated.get("reference_excerpt")):
        raise ValueError("reference_excerpt is required")
    return hydrated


def _parse_reference_resolution_packet(packet_text: Any, *, require_url: bool = True) -> dict[str, str]:
    packet = str(packet_text or "").strip()
    if not packet:
        raise ValueError("resolution_packet is required")
    parsed: dict[str, str] = {
        "source_url": "",
        "resolved_title": "",
        "resolved_doi": "",
        "resolved_journal": "",
        "resolved_published_year": "",
        "notes": "",
        "reference_excerpt": "",
    }
    current_key = ""
    excerpt_lines: list[str] = []
    key_map = {
        "url": "source_url",
        "source url": "source_url",
        "title": "resolved_title",
        "doi": "resolved_doi",
        "journal": "resolved_journal",
        "year": "resolved_published_year",
        "published year": "resolved_published_year",
        "notes": "notes",
        "excerpt": "reference_excerpt",
        "visible excerpt": "reference_excerpt",
    }
    for raw_line in packet.splitlines():
        line = raw_line.rstrip()
        if ":" in line:
            raw_key, raw_value = line.split(":", 1)
            normalized_key = _text(raw_key).lower()
            mapped_key = key_map.get(normalized_key, "")
            if mapped_key:
                current_key = mapped_key
                value = raw_value.lstrip()
                if mapped_key == "reference_excerpt":
                    excerpt_lines = [value] if value else []
                else:
                    parsed[mapped_key] = value
                continue
        if current_key == "reference_excerpt":
            excerpt_lines.append(line)
        elif current_key:
            existing = parsed.get(current_key, "")
            parsed[current_key] = f"{existing}\n{line}".strip() if existing else line
    parsed["reference_excerpt"] = "\n".join(line for line in excerpt_lines if line).strip()
    if require_url and not _text(parsed.get("source_url")):
        raise ValueError("resolution_packet must include URL:")
    if not _text(parsed.get("reference_excerpt")):
        raise ValueError("resolution_packet must include Excerpt:")
    return parsed


def _parse_reference_resolution_batch_packet(
    batch_text: Any,
    *,
    require_url: bool = True,
) -> list[dict[str, str]]:
    packet = str(batch_text or "").strip()
    if not packet:
        raise ValueError("resolution_batch_packet is required")
    blocks: list[list[str]] = []
    current_lines: list[str] = []
    for raw_line in packet.splitlines():
        line = raw_line.rstrip("\n")
        if _text(line) == "---":
            if current_lines:
                blocks.append(current_lines)
                current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        blocks.append(current_lines)
    if not blocks:
        raise ValueError("resolution_batch_packet must contain at least one packet block")

    parsed_blocks: list[dict[str, str]] = []
    for block in blocks:
        candidate_id = ""
        payload_lines: list[str] = []
        for line in block:
            if ":" in line:
                raw_key, raw_value = line.split(":", 1)
                if _text(raw_key).lower() == "candidate id":
                    candidate_id = _text(raw_value)
                    continue
            payload_lines.append(line)
        if not candidate_id:
            raise ValueError("each batch packet block must include Candidate ID:")
        parsed_blocks.append(
            {
                "candidate_id": candidate_id,
                **_parse_reference_resolution_packet("\n".join(payload_lines), require_url=require_url),
            }
        )
    return parsed_blocks


def _parse_search_result_capture_batch_packet(batch_text: Any) -> list[dict[str, str]]:
    packet = str(batch_text or "").strip()
    if not packet:
        raise ValueError("search_result_batch_packet is required")
    blocks: list[list[str]] = []
    current_lines: list[str] = []
    for raw_line in packet.splitlines():
        line = raw_line.rstrip("\n")
        if _text(line) == "---":
            if current_lines:
                blocks.append(current_lines)
                current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        blocks.append(current_lines)
    if not blocks:
        raise ValueError("search_result_batch_packet must contain at least one packet block")

    parsed_blocks: list[dict[str, str]] = []
    for block in blocks:
        parsed: dict[str, str] = {
            "candidate_id": "",
            "source_url": "",
            "search_result_title": "",
            "search_result_snippet": "",
            "notes": "",
        }
        current_key = ""
        for raw_line in block:
            line = raw_line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            if ":" in line:
                raw_key, raw_value = line.split(":", 1)
                key = _text(raw_key).lower()
                value = raw_value.lstrip()
                if key == "candidate id":
                    parsed["candidate_id"] = _text(value)
                    current_key = ""
                    continue
                if key == "url":
                    parsed["source_url"] = _text(value)
                    current_key = ""
                    continue
                if key == "title":
                    parsed["search_result_title"] = _text(value)
                    current_key = ""
                    continue
                if key == "snippet":
                    parsed["search_result_snippet"] = _text(value)
                    current_key = "search_result_snippet"
                    continue
                if key == "notes":
                    parsed["notes"] = _text(value)
                    current_key = "notes"
                    continue
            if current_key in {"search_result_snippet", "notes"}:
                existing = _text(parsed.get(current_key))
                parsed[current_key] = f"{existing}\n{line}".strip() if existing else line
        if not _text(parsed.get("candidate_id")):
            raise ValueError("each search-result batch block must include Candidate ID:")
        if not _text(parsed.get("source_url")):
            raise ValueError("each search-result batch block must include URL:")
        if not _text(parsed.get("search_result_title")) and not _text(parsed.get("search_result_snippet")):
            raise ValueError("each search-result batch block must include Title: or Snippet:")
        parsed_blocks.append(parsed)
    return parsed_blocks


def _normalize_search_result_capture_batch_record(
    raw_record: Mapping[str, Any] | None,
    *,
    default_format: str = "structured_records",
) -> dict[str, str]:
    record = dict(raw_record or {})
    normalized = {
        "candidate_id": _text(record.get("candidate_id") or record.get("candidateId")),
        "source_url": _text(record.get("source_url") or record.get("url")),
        "search_result_title": _text(record.get("search_result_title") or record.get("title")),
        "search_result_snippet": _text(record.get("search_result_snippet") or record.get("snippet")),
        "notes": _text(record.get("notes") or record.get("comment")),
        "capture_format": _text(record.get("capture_format")) or default_format,
    }
    if not normalized["candidate_id"]:
        raise ValueError("each structured search-result capture record must include candidate_id")
    if not normalized["source_url"]:
        raise ValueError("each structured search-result capture record must include source_url or url")
    if not normalized["search_result_title"] and not normalized["search_result_snippet"]:
        raise ValueError(
            "each structured search-result capture record must include search_result_title/title or search_result_snippet/snippet"
        )
    return normalized


def _parse_search_result_capture_batch_payload(
    payload: Mapping[str, Any] | None,
) -> list[dict[str, str]]:
    data = dict(payload or {})
    raw_records = data.get("search_result_batch_records")
    if isinstance(raw_records, list) and raw_records:
        return [
            _normalize_search_result_capture_batch_record(record)
            for record in raw_records
        ]

    raw_packet = data.get("search_result_batch_packet")
    packet = str(raw_packet or "").strip()
    if packet.startswith("[") or packet.startswith("{"):
        try:
            decoded = json.loads(packet)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list) and decoded:
            return [
                _normalize_search_result_capture_batch_record(
                    record,
                    default_format="json_array",
                )
                for record in decoded
            ]
        if isinstance(decoded, dict):
            nested_records = decoded.get("records") or decoded.get("rows") or decoded.get("results")
            if isinstance(nested_records, list) and nested_records:
                return [
                    _normalize_search_result_capture_batch_record(
                        record,
                        default_format="json_array",
                    )
                    for record in nested_records
                ]
    return _parse_search_result_capture_batch_packet(raw_packet)


def _normalize_search_query_result_promote_batch_record(
    raw_record: Mapping[str, Any] | None,
    *,
    default_format: str = "structured_records",
) -> dict[str, Any]:
    record = dict(raw_record or {})
    candidate_id = _text(record.get("candidate_id") or record.get("candidateId"))
    option_index_raw = record.get("option_index", record.get("optionIndex", 0))
    option_index = int(option_index_raw or 0)
    if not candidate_id:
        raise ValueError("each structured promote record must include candidate_id")
    if option_index < 1:
        raise ValueError("each structured promote record must include option_index >= 1")
    return {
        "candidate_id": candidate_id,
        "option_index": option_index,
        "notes": _text(record.get("notes") or record.get("comment")),
        "promotion_format": _text(record.get("promotion_format")) or default_format,
    }


def _parse_search_query_result_promote_batch_payload(
    payload: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    data = dict(payload or {})
    raw_records = data.get("promotion_batch_records")
    if isinstance(raw_records, list) and raw_records:
        return [
            _normalize_search_query_result_promote_batch_record(record)
            for record in raw_records
        ]

    raw_packet = data.get("promotion_batch_packet")
    packet = str(raw_packet or "").strip()
    if packet.startswith("[") or packet.startswith("{"):
        try:
            decoded = json.loads(packet)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list) and decoded:
            return [
                _normalize_search_query_result_promote_batch_record(
                    record,
                    default_format="json_array",
                )
                for record in decoded
            ]
        if isinstance(decoded, dict):
            nested_records = decoded.get("records") or decoded.get("rows") or decoded.get("results")
            if isinstance(nested_records, list) and nested_records:
                return [
                    _normalize_search_query_result_promote_batch_record(
                        record,
                        default_format="json_array",
                    )
                    for record in nested_records
                ]
    return []


def _normalize_search_query_result_resolve_batch_record(
    raw_record: Mapping[str, Any] | None,
    *,
    default_format: str = "structured_records",
) -> dict[str, Any]:
    record = dict(raw_record or {})
    candidate_id = _text(record.get("candidate_id") or record.get("candidateId"))
    option_index_raw = record.get("option_index", record.get("optionIndex", 0))
    option_index = int(option_index_raw or 0)
    reference_excerpt = _text(record.get("reference_excerpt") or record.get("excerpt"))
    if not candidate_id:
        raise ValueError("each structured resolve record must include candidate_id")
    if option_index < 1:
        raise ValueError("each structured resolve record must include option_index >= 1")
    if not reference_excerpt:
        raise ValueError("each structured resolve record must include reference_excerpt or excerpt")
    return {
        "candidate_id": candidate_id,
        "option_index": option_index,
        "reference_excerpt": reference_excerpt,
        "notes": _text(record.get("notes") or record.get("comment")),
        "resolution_format": _text(record.get("resolution_format")) or default_format,
    }


def _parse_search_query_result_resolve_batch_packet(raw_packet: Any) -> list[dict[str, Any]]:
    packet = str(raw_packet or "").strip()
    if not packet:
        raise ValueError("resolution_batch_packet is required")
    blocks: list[list[str]] = []
    current_lines: list[str] = []
    for raw_line in packet.splitlines():
        line = raw_line.rstrip("\n")
        if line.strip() == "---":
            if current_lines:
                blocks.append(current_lines)
                current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        blocks.append(current_lines)
    if not blocks:
        raise ValueError("resolution_batch_packet must contain at least one packet block")

    parsed_blocks: list[dict[str, Any]] = []
    for block in blocks:
        parsed: dict[str, Any] = {
            "candidate_id": "",
            "option_index": 0,
            "reference_excerpt": "",
            "notes": "",
        }
        current_key = ""
        for raw_line in block:
            line = raw_line.rstrip("\n")
            if not line or line.lstrip().startswith("#"):
                continue
            if ":" in line:
                raw_key, raw_value = line.split(":", 1)
                key = _text(raw_key).lower()
                value = raw_value.lstrip()
                if key == "candidate id":
                    parsed["candidate_id"] = _text(value)
                    current_key = ""
                    continue
                if key == "option index":
                    parsed["option_index"] = int(_text(value) or 0)
                    current_key = ""
                    continue
                if key == "notes":
                    parsed["notes"] = _text(value)
                    current_key = "notes"
                    continue
                if key == "excerpt":
                    parsed["reference_excerpt"] = _text(value)
                    current_key = "reference_excerpt"
                    continue
            if current_key in {"reference_excerpt", "notes"}:
                existing = _text(parsed.get(current_key))
                parsed[current_key] = f"{existing}\n{line}".strip() if existing else line
        parsed_blocks.append(
            _normalize_search_query_result_resolve_batch_record(
                parsed,
                default_format="packet",
            )
        )
    return parsed_blocks


def _parse_search_query_result_resolve_batch_payload(
    payload: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    data = dict(payload or {})
    raw_records = data.get("resolution_batch_records")
    if isinstance(raw_records, list) and raw_records:
        return [
            _normalize_search_query_result_resolve_batch_record(record)
            for record in raw_records
        ]

    raw_packet = data.get("resolution_batch_packet")
    packet = str(raw_packet or "").strip()
    if packet.startswith("[") or packet.startswith("{"):
        try:
            decoded = json.loads(packet)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list) and decoded:
            return [
                _normalize_search_query_result_resolve_batch_record(
                    record,
                    default_format="json_array",
                )
                for record in decoded
            ]
        if isinstance(decoded, dict):
            nested_records = decoded.get("records") or decoded.get("rows") or decoded.get("results")
            if isinstance(nested_records, list) and nested_records:
                return [
                    _normalize_search_query_result_resolve_batch_record(
                        record,
                        default_format="json_array",
                    )
                    for record in nested_records
                ]
    return _parse_search_query_result_resolve_batch_packet(raw_packet)


def _normalize_reference_resolution_batch_record(
    raw_record: Mapping[str, Any] | None,
    *,
    require_url: bool,
    default_format: str = "structured_records",
) -> dict[str, str]:
    record = dict(raw_record or {})
    normalized = {
        "candidate_id": _text(record.get("candidate_id") or record.get("candidateId")),
        "source_url": _text(record.get("source_url") or record.get("url")),
        "resolved_title": _text(record.get("resolved_title") or record.get("title")),
        "resolved_doi": _text(record.get("resolved_doi") or record.get("doi")),
        "resolved_journal": _text(record.get("resolved_journal") or record.get("journal")),
        "resolved_published_year": _text(record.get("resolved_published_year") or record.get("year") or record.get("published_year")),
        "notes": _text(record.get("notes") or record.get("comment")),
        "reference_excerpt": _text(record.get("reference_excerpt") or record.get("excerpt")),
        "resolution_format": _text(record.get("resolution_format")) or default_format,
    }
    if not normalized["candidate_id"]:
        raise ValueError("each structured resolution record must include candidate_id")
    if require_url and not normalized["source_url"]:
        raise ValueError("each structured resolution record must include source_url or url")
    if not normalized["reference_excerpt"]:
        raise ValueError("each structured resolution record must include reference_excerpt or excerpt")
    return normalized


def _parse_reference_resolution_batch_payload(
    payload: Mapping[str, Any] | None,
    *,
    require_url: bool = True,
) -> list[dict[str, str]]:
    data = dict(payload or {})
    raw_records = data.get("resolution_batch_records")
    if isinstance(raw_records, list) and raw_records:
        return [
            _normalize_reference_resolution_batch_record(
                record,
                require_url=require_url,
            )
            for record in raw_records
        ]

    raw_packet = data.get("resolution_batch_packet")
    packet = str(raw_packet or "").strip()
    if packet.startswith("[") or packet.startswith("{"):
        try:
            decoded = json.loads(packet)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list) and decoded:
            return [
                _normalize_reference_resolution_batch_record(
                    record,
                    require_url=require_url,
                    default_format="json_array",
                )
                for record in decoded
            ]
        if isinstance(decoded, dict):
            nested_records = decoded.get("records") or decoded.get("rows") or decoded.get("results")
            if isinstance(nested_records, list) and nested_records:
                return [
                    _normalize_reference_resolution_batch_record(
                        record,
                        require_url=require_url,
                        default_format="json_array",
                    )
                    for record in nested_records
                ]
    return _parse_reference_resolution_batch_packet(
        raw_packet,
        require_url=require_url,
    )


def _parse_search_query_result_import_packet(
    batch_text: Any,
    *,
    ordered_candidate_ids: list[str] | None = None,
) -> list[dict[str, Any]]:
    packet = str(batch_text or "").strip()
    if not packet:
        raise ValueError("search_result_import_packet is required")
    blocks: list[list[str]] = []
    current_lines: list[str] = []
    for raw_line in packet.splitlines():
        line = raw_line.rstrip("\n")
        if _text(line) == "---":
            if current_lines:
                blocks.append(current_lines)
                current_lines = []
            continue
        current_lines.append(line)
    if current_lines:
        blocks.append(current_lines)
    if not blocks:
        raise ValueError("search_result_import_packet must contain at least one packet block")

    normalized_ordered_ids = [_text(candidate_id) for candidate_id in list(ordered_candidate_ids or []) if _text(candidate_id)]
    parsed_blocks: list[dict[str, str]] = []
    for block_index, block in enumerate(blocks, start=1):
        parsed = {
            "candidate_id": "",
            "rank": "",
            "source_url": "",
            "search_result_title": "",
            "search_result_snippet": "",
            "notes": "",
            "reference_excerpt": "",
            "selected": False,
        }
        current_key = ""
        snippet_lines: list[str] = []
        excerpt_lines: list[str] = []
        for raw_line in block:
            line = raw_line.rstrip()
            if ":" in line:
                raw_key, raw_value = line.split(":", 1)
                normalized_key = _text(raw_key).lower()
                value = raw_value.lstrip()
                if normalized_key == "candidate id":
                    parsed["candidate_id"] = _text(value)
                    current_key = ""
                    continue
                if normalized_key == "rank":
                    parsed["rank"] = _text(value)
                    current_key = ""
                    continue
                if normalized_key == "url":
                    parsed["source_url"] = _text(value)
                    current_key = ""
                    continue
                if normalized_key == "title":
                    parsed["search_result_title"] = _text(value)
                    current_key = ""
                    continue
                if normalized_key == "notes":
                    parsed["notes"] = value
                    current_key = "notes"
                    continue
                if normalized_key == "selected":
                    parsed["selected"] = _is_truthy_flag(value)
                    current_key = ""
                    continue
                if normalized_key == "snippet":
                    snippet_lines = [value] if value else []
                    current_key = "search_result_snippet"
                    continue
                if normalized_key == "excerpt":
                    excerpt_lines = [value] if value else []
                    current_key = "reference_excerpt"
                    continue
            if current_key == "search_result_snippet":
                snippet_lines.append(line)
            elif current_key == "reference_excerpt":
                excerpt_lines.append(line)
            elif current_key == "notes":
                existing_notes = parsed.get("notes", "")
                parsed["notes"] = f"{existing_notes}\n{line}".strip() if existing_notes else line
        parsed["search_result_snippet"] = "\n".join(item for item in snippet_lines if item).strip()
        parsed["reference_excerpt"] = "\n".join(item for item in excerpt_lines if item).strip()
        if not _text(parsed.get("candidate_id")):
            if block_index <= len(normalized_ordered_ids):
                parsed["candidate_id"] = normalized_ordered_ids[block_index - 1]
                parsed["import_format"] = "ordered_packet"
            else:
                raise ValueError("each search_result_import_packet block must include Candidate ID: unless an ordered batch plan is active")
        if not _text(parsed.get("source_url")):
            raise ValueError("each search_result_import_packet block must include URL:")
        if not _text(parsed.get("search_result_title")) and not _text(parsed.get("search_result_snippet")):
            raise ValueError("each search_result_import_packet block must include Title: or Snippet:")
        if not _text(parsed.get("import_format")):
            parsed["import_format"] = "packet"
        parsed_blocks.append(parsed)
    return parsed_blocks


def _normalize_search_query_result_import_record(
    raw_record: Mapping[str, Any] | None,
    *,
    default_rank: int,
    default_import_format: str = "structured_records",
) -> dict[str, Any]:
    record = dict(raw_record or {})
    normalized = {
        "candidate_id": _text(record.get("candidate_id") or record.get("candidateId")),
        "rank": _text(record.get("rank") or record.get("position") or default_rank),
        "source_url": _text(record.get("source_url") or record.get("url")),
        "search_result_title": _text(record.get("search_result_title") or record.get("title")),
        "search_result_snippet": _text(record.get("search_result_snippet") or record.get("snippet")),
        "notes": _text(record.get("notes") or record.get("comment")),
        "reference_excerpt": _text(record.get("reference_excerpt") or record.get("excerpt")),
        "selected": _is_truthy_flag(
            record.get("selected") if "selected" in record else (
                record.get("is_selected") if "is_selected" in record else record.get("chosen")
            )
        ),
        "import_format": _text(record.get("import_format")) or default_import_format,
    }
    if not normalized["candidate_id"]:
        raise ValueError("each structured search-result record must include candidate_id")
    if not normalized["source_url"]:
        raise ValueError("each structured search-result record must include source_url or url")
    if not normalized["search_result_title"] and not normalized["search_result_snippet"]:
        raise ValueError("each structured search-result record must include search_result_title/title or search_result_snippet/snippet")
    return normalized


def _parse_search_query_result_import_records(records: Any) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise ValueError("search_result_import_records must contain at least one record")
    return [
        _normalize_search_query_result_import_record(record, default_rank=index)
        for index, record in enumerate(records, start=1)
    ]


def _parse_search_query_execution_session_rows(records: Any) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise ValueError("search_query_execution_session_rows must contain at least one row")
    return [
        _normalize_search_query_result_import_record(
            record,
            default_rank=index,
            default_import_format="session_rows",
        )
        for index, record in enumerate(records, start=1)
    ]


def _parse_search_query_execution_session_payload(
    payload: Mapping[str, Any] | None,
) -> list[dict[str, Any]]:
    data = dict(payload or {})
    raw_rows = data.get("search_query_execution_session_rows")
    if isinstance(raw_rows, list) and raw_rows:
        return _parse_search_query_execution_session_rows(raw_rows)
    raw_bundle = data.get("search_query_execution_session_bundle")
    if isinstance(raw_bundle, Mapping):
        bundle_rows = list(dict(raw_bundle).get("rows", []) or [])
        if bundle_rows:
            return _parse_search_query_execution_session_rows(bundle_rows)
    raise ValueError("search_query_execution_session_rows or search_query_execution_session_bundle.rows is required")


def _parse_search_query_execution_session_row_text(
    *,
    candidate_id: str,
    row_text: Any,
    provider_capture_guide: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    payload = {
        "search_result_import_packet": row_text,
    }
    parsed_rows = _parse_search_query_result_import_payload(
        payload,
        ordered_candidate_ids=[candidate_id],
        ordered_provider_capture_guide=provider_capture_guide,
    )
    if not parsed_rows:
        raise ValueError("no search-result row could be parsed")
    return dict(parsed_rows[0] or {})


def _parse_ordered_search_query_result_import_records(
    records: Any,
    *,
    candidate_ids: list[str],
) -> list[dict[str, Any]]:
    if not isinstance(records, list) or not records:
        raise ValueError("search_result_import_ordered_records must contain at least one record")
    if len(records) > len(candidate_ids):
        raise ValueError("ordered import contains more records than the current batch plan candidates")
    normalized_rows: list[dict[str, Any]] = []
    for index, record in enumerate(records, start=1):
        candidate_id = _text(candidate_ids[index - 1]) if index - 1 < len(candidate_ids) else ""
        if not candidate_id:
            raise ValueError("ordered import candidate mapping is unavailable for this batch position")
        merged = {
            **dict(record or {}),
            "candidate_id": candidate_id,
        }
        normalized = _normalize_search_query_result_import_record(
            merged,
            default_rank=index,
            default_import_format="ordered_records",
        )
        normalized["import_format"] = "ordered_records"
        normalized_rows.append(normalized)
    return normalized_rows


def _parse_ordered_search_query_result_import_compact_lines(
    raw_text: Any,
    *,
    candidate_ids: list[str],
    provider_capture_guide: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    text = str(raw_text or "").strip()
    if not text:
        raise ValueError("ordered compact import text is required")
    raw_lines = [
        line.rstrip()
        for line in text.splitlines()
        if line.strip()
    ]
    if not raw_lines:
        raise ValueError("ordered compact import must contain at least one data line")
    header_parts = _split_clipboard_header_parts(raw_lines[0])
    header_mapping = _detect_clipboard_header_mapping(header_parts) if header_parts else {}
    provider_layouts = [
        [str(cell).strip() for cell in layout if _text(cell)]
        for layout in list((dict(provider_capture_guide or {})).get("positional_layouts", []) or [])
        if isinstance(layout, list) and layout
    ]
    row_lines = [
        line.strip()
        for line in (raw_lines[1:] if header_mapping else raw_lines)
        if line.strip() and not line.strip().startswith("#")
    ]
    if len(row_lines) > len(candidate_ids):
        raise ValueError("ordered compact import contains more records than the current batch plan candidates")

    normalized_rows: list[dict[str, Any]] = []
    for index, line in enumerate(row_lines, start=1):
        candidate_id = _text(candidate_ids[index - 1]) if index - 1 < len(candidate_ids) else ""
        if not candidate_id:
            raise ValueError("ordered compact import candidate mapping is unavailable for this batch position")
        delimiter = "\t" if "\t" in line else "|"
        parts = [part.strip() for part in line.split(delimiter)]
        if header_mapping:
            mapped = _map_clipboard_cells_from_mapping(
                cells=list(parts),
                header_parts=header_parts,
                header_mapping=header_mapping,
            )
            source_url = mapped["source_url"]
            search_result_title = mapped["search_result_title"]
            search_result_snippet = mapped["search_result_snippet"]
            reference_excerpt = mapped["reference_excerpt"]
            selected = mapped["selected"]
            notes = mapped["notes"]
        else:
            embedded_title, embedded_url = _extract_embedded_link_value(parts[0] if parts else "")
            if embedded_url:
                payload_parts = [part.strip() for part in parts[1:]]
                while len(payload_parts) < 4:
                    payload_parts.append("")
                if len(payload_parts) > 4:
                    payload_parts = payload_parts[:4] + [delimiter.join(payload_parts[4:]).strip()]
                source_url = embedded_url
                search_result_title = embedded_title
                search_result_snippet = payload_parts[0]
                reference_excerpt = payload_parts[1]
                selected = payload_parts[2]
                notes = payload_parts[3] if len(payload_parts) >= 4 else ""
            elif delimiter == "\t" and provider_layouts:
                provider_mapped: dict[str, str] | None = None
                for layout in provider_layouts:
                    if len(parts) != len(layout):
                        continue
                    positional_mapping = _detect_clipboard_header_mapping(layout)
                    if not positional_mapping:
                        continue
                    candidate = _map_clipboard_cells_from_mapping(
                        cells=list(parts),
                        header_parts=layout,
                        header_mapping=positional_mapping,
                    )
                    if _text(candidate.get("source_url")) and (
                        _text(candidate.get("search_result_title")) or _text(candidate.get("search_result_snippet"))
                    ):
                        provider_mapped = candidate
                        break
                if provider_mapped:
                    source_url = provider_mapped["source_url"]
                    search_result_title = provider_mapped["search_result_title"]
                    search_result_snippet = provider_mapped["search_result_snippet"]
                    reference_excerpt = provider_mapped["reference_excerpt"]
                    selected = provider_mapped["selected"]
                    notes = provider_mapped["notes"]
                else:
                    generic_mapped = _map_flexible_tsv_without_headers(parts)
                    source_url = generic_mapped["source_url"]
                    search_result_title = generic_mapped["search_result_title"]
                    search_result_snippet = generic_mapped["search_result_snippet"]
                    reference_excerpt = generic_mapped["reference_excerpt"]
                    selected = generic_mapped["selected"]
                    notes = generic_mapped["notes"]
            elif delimiter == "\t" and len(parts) > 2 and not (
                _looks_like_url_value(parts[0]) or (len(parts) >= 2 and _looks_like_url_value(parts[1]))
            ):
                generic_mapped = _map_flexible_tsv_without_headers(parts)
                source_url = generic_mapped["source_url"]
                search_result_title = generic_mapped["search_result_title"]
                search_result_snippet = generic_mapped["search_result_snippet"]
                reference_excerpt = generic_mapped["reference_excerpt"]
                selected = generic_mapped["selected"]
                notes = generic_mapped["notes"]
            else:
                while len(parts) < 6:
                    parts.append("")
                if len(parts) > 6:
                    parts = parts[:5] + [delimiter.join(parts[5:]).strip()]
                source_url = parts[0]
                search_result_title = parts[1]
                if len(parts) >= 2 and _looks_like_url_value(parts[1]) and not _looks_like_url_value(parts[0]):
                    search_result_title = parts[0]
                    source_url = parts[1]
                search_result_snippet = parts[2]
                reference_excerpt = parts[3]
                selected = parts[4]
                notes = parts[5]
        merged = {
            "candidate_id": candidate_id,
            "rank": index,
            "source_url": source_url,
            "search_result_title": search_result_title,
            "search_result_snippet": search_result_snippet,
            "reference_excerpt": reference_excerpt,
            "selected": selected,
            "notes": notes,
        }
        normalized = _normalize_search_query_result_import_record(
            merged,
            default_rank=index,
            default_import_format="ordered_tsv_lines" if delimiter == "\t" else "ordered_compact_lines",
        )
        normalized["import_format"] = "ordered_tsv_lines" if delimiter == "\t" else "ordered_compact_lines"
        normalized_rows.append(normalized)
    return normalized_rows


def _parse_search_query_result_import_payload(
    payload: Mapping[str, Any] | None,
    *,
    ordered_candidate_ids: list[str] | None = None,
    ordered_provider_capture_guide: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    data = dict(payload or {})
    normalized_ordered_ids = [_text(candidate_id) for candidate_id in list(ordered_candidate_ids or []) if _text(candidate_id)]
    raw_records = data.get("search_result_import_records")
    if isinstance(raw_records, list) and raw_records:
        return _parse_search_query_result_import_records(raw_records)
    raw_session_rows = data.get("search_query_execution_session_rows")
    if isinstance(raw_session_rows, list) and raw_session_rows:
        return _parse_search_query_execution_session_rows(raw_session_rows)
    raw_ordered_records = data.get("search_result_import_ordered_records")
    if isinstance(raw_ordered_records, list) and raw_ordered_records:
        return _parse_ordered_search_query_result_import_records(
            raw_ordered_records,
            candidate_ids=normalized_ordered_ids,
        )

    raw_packet = data.get("search_result_import_packet")
    packet = str(raw_packet or "").strip()
    if normalized_ordered_ids:
        compact_lines = [
            line.strip()
            for line in packet.splitlines()
            if line.strip() and not line.strip().startswith("#")
        ]
        labeled_prefixes = (
            "candidate id:",
            "rank:",
            "url:",
            "title:",
            "snippet:",
            "excerpt:",
            "selected:",
            "notes:",
        )
        if compact_lines and all(("|" in line or "\t" in line) for line in compact_lines) and not any(
            _text(line).lower().startswith(labeled_prefixes) for line in compact_lines
        ):
            return _parse_ordered_search_query_result_import_compact_lines(
                packet,
                candidate_ids=normalized_ordered_ids,
                provider_capture_guide=ordered_provider_capture_guide,
            )
    if packet.startswith("[") or packet.startswith("{"):
        try:
            decoded = json.loads(packet)
        except json.JSONDecodeError:
            decoded = None
        if isinstance(decoded, list) and decoded:
            if ordered_candidate_ids:
                decoded_candidate_present = any(_text((dict(item or {})).get("candidate_id") or (dict(item or {})).get("candidateId")) for item in decoded)
                if not decoded_candidate_present:
                    return _parse_ordered_search_query_result_import_records(
                        decoded,
                        candidate_ids=normalized_ordered_ids,
                    )
            return [
                _normalize_search_query_result_import_record(
                    record,
                    default_rank=index,
                    default_import_format="json_array",
                )
                for index, record in enumerate(decoded, start=1)
            ]
        if isinstance(decoded, dict):
            nested_records = decoded.get("records") or decoded.get("rows") or decoded.get("results")
            if isinstance(nested_records, list) and nested_records:
                return [
                    _normalize_search_query_result_import_record(
                        record,
                        default_rank=index,
                        default_import_format="json_array",
                    )
                    for index, record in enumerate(nested_records, start=1)
                ]
    return _parse_search_query_result_import_packet(
        raw_packet,
        ordered_candidate_ids=ordered_candidate_ids,
    )


def _apply_search_query_result_import_blocks(
    *,
    run_id: str,
    parsed_blocks: list[dict[str, Any]] | None,
    auto_capture_singleton_candidates: bool = False,
) -> dict[str, Any]:
    normalized_blocks = [dict(block) for block in list(parsed_blocks or [])]
    run_d = _load_run(run_id)
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    candidate_rows = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(manifest.get("candidate_rows", []) or [])
        if _text(row.get("candidate_id"))
    }
    selected_imports_by_candidate: dict[str, dict[str, Any]] = {}
    for block in normalized_blocks:
        candidate_id = _text(block.get("candidate_id"))
        if candidate_id not in candidate_rows:
            raise ValueError(f"candidate not found in imported queue: {candidate_id}")
        if not bool(block.get("selected")):
            continue
        if candidate_id in selected_imports_by_candidate:
            raise ValueError(f"multiple selected imported results for candidate: {candidate_id}")
        selected_imports_by_candidate[candidate_id] = dict(block)

    current_store = _load_search_query_result_import_store(run_id)
    incoming_candidate_ids = {
        _text(block.get("candidate_id"))
        for block in normalized_blocks
        if _text(block.get("candidate_id"))
    }
    retained_records = [
        dict(row)
        for row in list(current_store.get("result_records", []) or [])
        if _text(row.get("candidate_id")) not in incoming_candidate_ids
    ]
    normalized_records = list(retained_records)
    for order, block in enumerate(normalized_blocks, start=1):
        rank_value = int(_text(block.get("rank")) or order)
        normalized_records.append(
            {
                "candidate_id": _text(block.get("candidate_id")),
                "rank": rank_value,
                "source_url": _text(block.get("source_url")),
                "search_result_title": _text(block.get("search_result_title")),
                "search_result_snippet": _text(block.get("search_result_snippet")),
                "notes": _text(block.get("notes")),
                "reference_excerpt": _text(block.get("reference_excerpt")),
                "selected": bool(block.get("selected")),
                "import_format": _text(block.get("import_format")) or "packet",
                "imported_at": _utc_now_iso(),
            }
        )

    store = _persist_search_query_result_import_store(run_id, normalized_records)
    refreshed = _congruence_brain_activity(run_d or {"run_id": run_id})
    auto_captured_candidate_ids: list[str] = []
    auto_selected_candidate_ids: list[str] = []
    auto_resolved_selected_candidate_ids: list[str] = []
    last_result: dict[str, Any] = {}
    processed_candidate_ids: set[str] = set()
    if selected_imports_by_candidate:
        execution_rows_by_candidate = {
            _text(row.get("candidate_id")): dict(row)
            for row in list(refreshed.get("search_query_execution_register", []) or [])
            if _text(row.get("candidate_id"))
        }
        for candidate_id, selected_record in sorted(selected_imports_by_candidate.items()):
            execution_row = dict(execution_rows_by_candidate.get(candidate_id, {}) or {})
            if _text(execution_row.get("execution_status")) != "search_ready_capture_pending":
                continue
            option_index = _find_imported_result_option_index(
                execution_row=execution_row,
                import_record=selected_record,
            )
            if option_index < 1:
                continue
            try:
                if _text(selected_record.get("reference_excerpt")):
                    last_result = _resolve_search_query_result_option_with_excerpt(
                        run_id=run_id,
                        candidate_id=candidate_id,
                        option_index=option_index,
                        reference_excerpt=_text(selected_record.get("reference_excerpt")),
                        notes_override=_text(selected_record.get("notes")) or "Resolved selected imported search result.",
                        auto_accept_discovery_candidate=True,
                    )
                    auto_resolved_selected_candidate_ids.append(candidate_id)
                else:
                    last_result = _promote_search_query_result_option(
                        run_id=run_id,
                        candidate_id=candidate_id,
                        option_index=option_index,
                        notes_override=_text(selected_record.get("notes")) or "Promoted selected imported search result.",
                    )
            except ValueError:
                continue
            auto_selected_candidate_ids.append(candidate_id)
            processed_candidate_ids.add(candidate_id)
        if last_result:
            refreshed = dict(last_result.get("congruence_brain", {}) or {})
    if auto_capture_singleton_candidates:
        execution_rows_by_candidate = {
            _text(row.get("candidate_id")): dict(row)
            for row in list(refreshed.get("search_query_execution_register", []) or [])
            if _text(row.get("candidate_id"))
        }
        for candidate_id in sorted(incoming_candidate_ids):
            if candidate_id in processed_candidate_ids:
                continue
            execution_row = dict(execution_rows_by_candidate.get(candidate_id, {}) or {})
            if _text(execution_row.get("execution_status")) != "search_ready_capture_pending":
                continue
            if int(execution_row.get("imported_result_option_count", 0) or 0) != 1:
                continue
            singleton_record = next(
                (
                    dict(block)
                    for block in normalized_blocks
                    if _text(block.get("candidate_id")) == candidate_id
                ),
                {},
            )
            try:
                if _text(singleton_record.get("reference_excerpt")):
                    last_result = _resolve_search_query_result_option_with_excerpt(
                        run_id=run_id,
                        candidate_id=candidate_id,
                        option_index=1,
                        reference_excerpt=_text(singleton_record.get("reference_excerpt")),
                        notes_override=_text(singleton_record.get("notes")) or "Auto-resolved singleton imported search result.",
                        auto_accept_discovery_candidate=True,
                    )
                else:
                    last_result = _promote_search_query_result_option(
                        run_id=run_id,
                        candidate_id=candidate_id,
                        option_index=1,
                        notes_override="Auto-captured singleton imported search result.",
                    )
            except ValueError:
                continue
            auto_captured_candidate_ids.append(candidate_id)
        if last_result:
            refreshed = dict(last_result.get("congruence_brain", {}) or {})
    return {
        "ok": True,
        "run_id": run_id,
        "summary": {
            "imported_count": len(normalized_blocks),
            "candidate_count": len(incoming_candidate_ids),
            "auto_captured_singleton_count": len(auto_captured_candidate_ids),
            "auto_captured_candidate_ids": auto_captured_candidate_ids,
            "auto_selected_count": len(auto_selected_candidate_ids),
            "auto_selected_candidate_ids": auto_selected_candidate_ids,
            "auto_resolved_selected_count": len(auto_resolved_selected_candidate_ids),
            "auto_resolved_selected_candidate_ids": auto_resolved_selected_candidate_ids,
            "import_formats": sorted(
                {
                    _text(block.get("import_format")) or "packet"
                    for block in normalized_blocks
                }
            ),
        },
        "search_query_result_import_store": store,
        "licensed_research": dict((refreshed.get("licensed_research", {}) if refreshed else {}) or {}),
        "congruence_brain": refreshed,
    }


def _normalize_manual_discovery_candidate_record(payload: dict[str, Any]) -> dict[str, Any]:
    provider_key = _text((payload or {}).get("provider_key")) or "manual"
    title = _text((payload or {}).get("title"))
    if not title:
        raise ValueError("title is required")
    return {
        "provider_key": provider_key,
        "title": title,
        "doi": _text((payload or {}).get("doi")),
        "journal": _text((payload or {}).get("journal")),
        "published_year": _text((payload or {}).get("published_year")),
        "source_url": _text((payload or {}).get("source_url")),
        "keywords": [_text(item) for item in list((payload or {}).get("keywords", []) or []) if _text(item)],
        "abstract": _text((payload or {}).get("abstract")),
        "notes": _text((payload or {}).get("notes")),
        "reference_excerpt": _text((payload or {}).get("reference_excerpt")),
        "operator_decision": _text((payload or {}).get("operator_decision")) or "candidate",
        "source_family": _text((payload or {}).get("source_family")),
    }


def _upsert_manual_discovery_candidate(
    *,
    run_id: str,
    record: dict[str, Any],
    candidate_id_override: str = "",
    creation_reason: str = "Created manually from dashboard.",
    refresh_after: bool = True,
) -> dict[str, Any]:
    if rebuild_licensed_discovery_candidate_row is None or load_registry_bundle is None:
        raise ValueError("licensed discovery candidate rebuild is unavailable")

    provider_key = _text(record.get("provider_key")) or "manual"
    slug_basis = _text(candidate_id_override) or _text(record.get("doi")) or _text(record.get("title"))
    candidate_id = _text(candidate_id_override) or f"manual-{_safe_store_component(provider_key)}-{_safe_store_component(slug_basis)}"
    metadata_payload = {
        "provider_key": provider_key,
        "title": _text(record.get("title")),
        "doi": _text(record.get("doi")),
        "journal": _text(record.get("journal")),
        "published_year": _text(record.get("published_year")),
        "authors": [],
        "keywords": list(record.get("keywords", []) or []),
        "source_url": _text(record.get("source_url")),
        "abstract": _text(record.get("abstract")),
        "notes": _text(record.get("notes")),
        "provider_display_name": _text(record.get("provider_display_name")),
        "launch_url": _text(record.get("launch_url")),
        "search_surface": _text(record.get("search_surface")),
        "search_intent": _text(record.get("search_intent")),
        "primary_query": _text(record.get("primary_query")),
        "pivot_query": _text(record.get("pivot_query")),
        "execution_hint": _text(record.get("execution_hint")),
        "query_family": _text(record.get("query_family")),
        "source_family": _text(record.get("source_family")),
        "evidence_targets": [
            _text(item)
            for item in list(record.get("evidence_targets", []) or [])
            if _text(item)
        ],
        "seed_terms": [
            _text(item)
            for item in list(record.get("seed_terms", []) or [])
            if _text(item)
        ],
        "asset_focus_terms": [
            _text(item)
            for item in list(record.get("asset_focus_terms", []) or [])
            if _text(item)
        ],
    }
    registry_bundle = load_registry_bundle()
    rebuilt_row = rebuild_licensed_discovery_candidate_row(
        candidate_row={
            "candidate_id": candidate_id,
            "provider_key": provider_key,
            "title": _text(record.get("title")),
            "doi": _text(record.get("doi")),
            "journal": _text(record.get("journal")),
            "published_year": _text(record.get("published_year")),
            "keywords": list(record.get("keywords", []) or []),
            "source_url": _text(record.get("source_url")),
            "source_family": _text(record.get("source_family")),
            "metadata_payload": metadata_payload,
        },
        registry_bundle=registry_bundle,
    )
    explicit_source_family = _text(record.get("source_family"))
    if explicit_source_family:
        rebuilt_row["source_family"] = explicit_source_family
        rebuilt_metadata = dict(rebuilt_row.get("metadata_payload", {}) or {})
        rebuilt_metadata["source_family"] = explicit_source_family
        rebuilt_row["metadata_payload"] = rebuilt_metadata

    manifest = _load_licensed_discovery_queue_manifest(run_id)
    candidate_rows = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(manifest.get("candidate_rows", []) or [])
        if _text(row.get("candidate_id"))
    }
    candidate_rows[candidate_id] = rebuilt_row
    updated_manifest = dict(manifest or {})
    updated_manifest["candidate_rows"] = sorted(candidate_rows.values(), key=lambda row: _text(row.get("candidate_id")))
    updated_manifest = _refresh_discovery_queue_manifest_summary(updated_manifest)
    stored_manifest = _persist_licensed_discovery_queue_manifest(run_id, updated_manifest)

    operator_decision = _text(record.get("operator_decision")) or "candidate"
    if operator_decision in _ALLOWED_DISCOVERY_CANDIDATE_DECISIONS and operator_decision != "candidate":
        _persist_discovery_candidate_decision_record(
            run_id,
            {
                "candidate_id": candidate_id,
                "operator_decision": operator_decision,
                "decision_reason": creation_reason,
                "decision_scope": "run",
                "decision_timestamp": _utc_now_iso(),
            },
        )

    reference_excerpt = _text(record.get("reference_excerpt"))
    if reference_excerpt:
        _persist_article_reference_record(
            run_id,
            {
                "candidate_id": candidate_id,
                "provider_key": provider_key,
                "reference_state": "manual_text_enriched",
                "acquisition_result": {
                    "visible_text": reference_excerpt,
                    "notes": _text(record.get("notes")),
                    "status": "manual",
                },
                "research_document_manifest": dict(rebuilt_row.get("manifest", {}) or {}),
                "updated_at": _utc_now_iso(),
            },
        )

    if not refresh_after:
        return {
            "run_id": run_id,
            "candidate_id": candidate_id,
            "discovery_queue_manifest": stored_manifest,
            "updated_candidate_row": rebuilt_row,
        }

    auto_refresh = _refresh_reference_backed_promotions_state(
        run_id=run_id,
        candidate_id=candidate_id,
    )
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    refreshed_licensed = dict(auto_refresh.get("licensed", {}) or {})
    accepted_bundle_manifest = dict(auto_refresh.get("accepted_bundle_manifest", {}) or {})
    updated_candidate_row = next(
        (
            row for row in list(refreshed_licensed.get("discovery_candidate_review_register", []) or [])
            if _text(row.get("candidate_id")) == candidate_id
        ),
        {},
    )
    updated_reference_row = next(
        (
            row for row in list(refreshed_licensed.get("article_reference_register", []) or [])
            if _text(row.get("candidate_id")) == candidate_id
        ),
        {},
    )
    return {
        "run_id": run_id,
        "candidate_id": candidate_id,
        "discovery_queue_manifest": stored_manifest,
        "accepted_discovery_candidate_bundle_manifest": accepted_bundle_manifest,
        "reference_backed_promotion_manifest": dict(auto_refresh.get("reference_backed_promotion_manifest", {}) or {}),
        "updated_candidate_row": updated_candidate_row,
        "updated_reference_row": updated_reference_row,
        "licensed_research": refreshed_licensed,
        "congruence_brain": refreshed,
    }


def _execute_article_reference_edit(
    *,
    run_id: str,
    candidate_id: str,
    edit_record: dict[str, Any],
) -> dict[str, Any]:
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    rows = list(manifest.get("candidate_rows", []) or [])
    candidate_row = next((dict(row) for row in rows if _text(row.get("candidate_id")) == candidate_id), {})
    if not candidate_row:
        raise ValueError("candidate not found in imported queue")
    current_store = _load_article_reference_record_store(run_id)
    current_records = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(current_store.get("records", []) or [])
        if _text(row.get("candidate_id"))
    }
    current_record = dict(current_records.get(candidate_id, {}) or {})
    acquisition_result = dict(current_record.get("acquisition_result", {}) or {})
    patch = dict(edit_record.get("patch", {}) or {})
    reference_excerpt = _text(patch.get("reference_excerpt"))
    source_url = _text(patch.get("source_url"))
    resolved_title = _text(patch.get("resolved_title"))
    resolved_doi = _text(patch.get("resolved_doi"))
    resolved_journal = _text(patch.get("resolved_journal"))
    resolved_published_year = _text(patch.get("resolved_published_year"))
    search_result_title = _text(patch.get("search_result_title"))
    search_result_snippet = _text(patch.get("search_result_snippet"))
    if reference_excerpt:
        acquisition_result["visible_text"] = reference_excerpt
    if source_url:
        acquisition_result["final_url"] = source_url
        if not _text(acquisition_result.get("requested_url")):
            acquisition_result["requested_url"] = source_url
    if search_result_title:
        acquisition_result["search_result_title"] = search_result_title
    if search_result_snippet:
        acquisition_result["search_result_snippet"] = search_result_snippet
    acquisition_result["notes"] = _text(patch.get("notes"))
    if _text(current_record.get("reference_state")) == "query_seed_draft" and reference_excerpt:
        acquisition_result["status"] = "query_seed_manual_capture"
    elif _text(current_record.get("reference_state")) == "query_seed_draft" and (
        source_url or search_result_title or search_result_snippet
    ):
        acquisition_result["status"] = "query_seed_result_captured"
    updated_record = {
        "candidate_id": candidate_id,
        "provider_key": _text(current_record.get("provider_key")) or _text((candidate_row.get("metadata_payload", {}) or {}).get("provider_key")),
        "source_url": source_url or _text(current_record.get("source_url")) or _text(acquisition_result.get("final_url")),
        "reference_state": _text(patch.get("reference_state")) or ("manual_text_enriched" if reference_excerpt else _text(current_record.get("reference_state")) or "metadata_only"),
        "acquisition_result": acquisition_result,
        "research_document_manifest": dict(current_record.get("research_document_manifest", {}) or candidate_row.get("manifest", {}) or {}),
        "updated_at": _text(edit_record.get("updated_at")) or _utc_now_iso(),
    }
    if source_url or resolved_title or resolved_doi or resolved_journal or resolved_published_year:
        metadata_payload = dict(candidate_row.get("metadata_payload", {}) or {})
        if source_url:
            metadata_payload["source_url"] = source_url
            candidate_row["source_url"] = source_url
        if resolved_title:
            metadata_payload["title"] = resolved_title
            candidate_row["title"] = resolved_title
        if resolved_doi:
            metadata_payload["doi"] = resolved_doi
            candidate_row["doi"] = resolved_doi
        if resolved_journal:
            metadata_payload["journal"] = resolved_journal
            candidate_row["journal"] = resolved_journal
        if resolved_published_year:
            metadata_payload["published_year"] = resolved_published_year
            candidate_row["published_year"] = resolved_published_year
        candidate_row["metadata_payload"] = metadata_payload
        if rebuild_licensed_discovery_candidate_row is not None and load_registry_bundle is not None:
            candidate_row = rebuild_licensed_discovery_candidate_row(
                candidate_row=candidate_row,
                registry_bundle=load_registry_bundle(),
            )
            candidate_row["metadata_payload"] = metadata_payload
            if source_url:
                candidate_row["source_url"] = source_url
            if resolved_title:
                candidate_row["title"] = resolved_title
            if resolved_doi:
                candidate_row["doi"] = resolved_doi
            if resolved_journal:
                candidate_row["journal"] = resolved_journal
            if resolved_published_year:
                candidate_row["published_year"] = resolved_published_year
        _persist_discovery_candidate_manifest_row(run_id, candidate_row)
    if bool(edit_record.get("auto_accept_discovery_candidate")) and reference_excerpt:
        _persist_discovery_candidate_decision_record(
            run_id,
            {
                "candidate_id": candidate_id,
                "operator_decision": "accepted_for_reference_use",
                "decision_reason": "Accepted automatically when resolving query-seed draft.",
                "decision_scope": "run",
                "decision_timestamp": _utc_now_iso(),
            },
        )
    store = _persist_article_reference_record(run_id, updated_record)
    auto_refresh = _refresh_reference_backed_promotions_state(
        run_id=run_id,
        candidate_id=candidate_id,
    )
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    refreshed_licensed = dict(auto_refresh.get("licensed", {}) or {})
    accepted_bundle_manifest = dict(auto_refresh.get("accepted_bundle_manifest", {}) or {})
    updated_row = next(
        (
            row for row in list(refreshed_licensed.get("article_reference_register", []) or [])
            if _text(row.get("candidate_id")) == candidate_id
        ),
        {},
    )
    return {
        "run_id": run_id,
        "article_reference_store": {
            "updated_at": _text(store.get("updated_at")),
            "path": _text(store.get("path")),
            "stored_record_count": len(list(store.get("records", []) or [])),
            "exists": bool(store.get("exists")),
        },
        "accepted_discovery_candidate_bundle_manifest": accepted_bundle_manifest,
        "reference_backed_promotion_manifest": dict(auto_refresh.get("reference_backed_promotion_manifest", {}) or {}),
        "knowledge_atom_refresh_summary": dict(auto_refresh.get("knowledge_atom_refresh_summary", {}) or {}),
        "combination_rerank_summary": dict(auto_refresh.get("combination_rerank_summary", {}) or {}),
        "updated_row": updated_row,
        "licensed_research": refreshed_licensed,
        "congruence_brain": refreshed,
    }


def _build_query_seed_candidate_records(
    *,
    combination_id: str,
    follow_on_manifest_row: dict[str, Any],
) -> list[dict[str, Any]]:
    if materialize_query_seed_candidate_records is not None:
        return materialize_query_seed_candidate_records(
            combination_id=combination_id,
            follow_on_manifest_row=follow_on_manifest_row,
            default_launch_url_builder=default_provider_launch_url,
        )
    return []


def _seed_follow_on_candidates_for_combination(
    *,
    run_id: str,
    combination_id: str,
    follow_on_manifest_row: dict[str, Any],
) -> dict[str, Any]:
    seed_records = _build_query_seed_candidate_records(
        combination_id=combination_id,
        follow_on_manifest_row=dict(follow_on_manifest_row or {}),
    )
    if not seed_records:
        return {
            "seeded_count": 0,
            "seed_records": [],
        }
    seeded_rows: list[dict[str, Any]] = []
    for record in seed_records:
        result = _upsert_manual_discovery_candidate(
            run_id=run_id,
            record=record,
            candidate_id_override=_text(record.get("candidate_id")),
            creation_reason="Seeded automatically from research-loop advance.",
            refresh_after=False,
        )
        seeded_rows.append(
            {
                "candidate_id": _text(result.get("candidate_id")),
                "provider_key": _text(record.get("provider_key")),
                "query_family": _text(record.get("query_family")),
            }
        )
    return {
        "seeded_count": len(seeded_rows),
        "seed_records": seeded_rows,
    }


def _execute_research_loop_advance(
    *,
    run_id: str,
    run_d: dict[str, Any],
) -> dict[str, Any]:
    congruence_brain = _congruence_brain_activity(run_d)
    control = dict(congruence_brain.get("research_loop_control_record", {}) or {})
    if _text(control.get("control_state")) == "paused_by_operator":
        return {
            "ok": False,
            "execution_status": "blocked_by_operator_pause",
            "message": _text(control.get("control_reason")) or "research loop is paused by operator",
            "congruence_brain": congruence_brain,
        }
    if _text(control.get("control_state")) == "stopped_by_operator":
        return {
            "ok": False,
            "execution_status": "blocked_by_operator_stop",
            "message": _text(control.get("control_reason")) or "research loop is stopped by operator",
            "congruence_brain": congruence_brain,
        }

    current_job = dict(congruence_brain.get("current_research_job", {}) or {})
    job_type = _text(current_job.get("job_type"))
    candidate_id = _text(current_job.get("candidate_id"))
    combination_id = _text(current_job.get("combination_id"))
    source_family = _text(current_job.get("source_family"))

    if not job_type:
        return {
            "ok": True,
            "execution_status": "no_current_job",
            "message": "no current research job is available for this run",
            "congruence_brain": congruence_brain,
        }

    if job_type == "seed_query_candidates":
        manifest_row = next(
            (
                row
                for row in list(congruence_brain.get("combination_follow_on_execution_manifest_register", []) or [])
                if _text(row.get("combination_id")) == combination_id
            ),
            {},
        )
        if not manifest_row:
            return {
                "ok": False,
                "execution_status": "missing_follow_on_manifest",
                "message": "no follow-on execution manifest exists for the current combination",
                "congruence_brain": congruence_brain,
            }
        seed_result = _seed_follow_on_candidates_for_combination(
            run_id=run_id,
            combination_id=combination_id,
            follow_on_manifest_row=dict(manifest_row),
        )
        refreshed = _congruence_brain_activity(run_d)
        return {
            "ok": True,
            "execution_status": "executed",
            "executed_action": "SEED_QUERY_CANDIDATES",
            "message": f"seeded {int(seed_result.get('seeded_count', 0) or 0)} discovery candidates",
            "seed_result": seed_result,
            "congruence_brain": refreshed,
        }

    if job_type == "draft_reference":
        manifest = _load_licensed_discovery_queue_manifest(run_id)
        rows = list(manifest.get("candidate_rows", []) or [])
        candidate_row = next((dict(row) for row in rows if _text(row.get("candidate_id")) == candidate_id), {})
        if not candidate_row:
            return {
                "ok": False,
                "execution_status": "candidate_missing",
                "message": "candidate required for draft_reference is missing",
                "congruence_brain": congruence_brain,
            }
        reference_result = _read_article_reference_for_candidate(run_id=run_id, candidate_row=candidate_row)
        auto_refresh = _refresh_reference_backed_promotions_state(
            run_id=run_id,
            candidate_id=candidate_id,
        )
        refreshed = dict(auto_refresh.get("refreshed", {}) or {})
        return {
            "ok": True,
            "execution_status": "executed",
            "executed_action": "READ_OR_DRAFT_REFERENCE",
            "message": "drafted article reference from current query seed",
            "article_reference_store": dict(reference_result.get("article_reference_store", {}) or {}),
            "congruence_brain": refreshed,
        }

    if job_type == "refresh_reference_backed_promotions":
        auto_refresh = _refresh_reference_backed_promotions_state(
            run_id=run_id,
            candidate_id=candidate_id,
        )
        refreshed = dict(auto_refresh.get("refreshed", {}) or {})
        return {
            "ok": True,
            "execution_status": "executed",
            "executed_action": "REFRESH_REFERENCE_BACKED_PROMOTIONS",
            "message": "refreshed atoms, promotions and reranking from enriched references",
            "knowledge_atom_refresh_summary": dict(auto_refresh.get("knowledge_atom_refresh_summary", {}) or {}),
            "combination_rerank_summary": dict(auto_refresh.get("combination_rerank_summary", {}) or {}),
            "congruence_brain": refreshed,
        }

    if job_type == "capture_search_result":
        return {
            "ok": False,
            "execution_status": "manual_search_result_capture_required",
            "message": "current job requires capturing a real search-result URL/title/snippet before excerpt resolution",
            "congruence_brain": congruence_brain,
        }

    if job_type in {"resolve_reference_draft", "resolve_reference_excerpt"}:
        return {
            "ok": False,
            "execution_status": "manual_resolution_required",
            "message": (
                "current job requires manual excerpt resolution before the loop can continue"
                if job_type == "resolve_reference_excerpt"
                else "current job requires manual reference resolution before the loop can continue"
            ),
            "congruence_brain": congruence_brain,
        }

    if job_type == "trigger_deeper_source_family_search":
        return {
            "ok": False,
            "execution_status": "external_research_required",
            "message": (
                f"source-family search for {source_family or 'this family'} is queued, "
                "but still requires external research or provider interaction"
            ),
            "congruence_brain": congruence_brain,
        }

    return {
        "ok": False,
        "execution_status": "job_type_not_supported",
        "message": f"unsupported research job type: {job_type}",
        "congruence_brain": congruence_brain,
    }


def _build_registry_review_bundle(
    *,
    run_id: str,
    licensed_research: dict[str, Any],
) -> dict[str, Any]:
    licensed = dict(licensed_research or {})
    review_rows = list(licensed.get("promotion_review_register", []) or [])
    pattern_rows = list(licensed.get("approved_pattern_promotion_register", []) or [])
    combination_rows = list(licensed.get("approved_combination_promotion_register", []) or [])
    pattern_by_promotion_id = {
        _text(row.get("promotion_id")) or f"pattern::{_text(row.get('pattern_id'))}": dict(row)
        for row in pattern_rows
    }
    combination_by_promotion_id = {
        _text(row.get("promotion_id")) or f"combination::{_text(row.get('combination_id'))}": dict(row)
        for row in combination_rows
    }
    accepted_rows = [
        row
        for row in review_rows
        if _text(row.get("operator_decision")) == "accepted_for_registry_review"
    ]
    accepted_pattern_promotions: list[dict[str, Any]] = []
    accepted_combination_promotions: list[dict[str, Any]] = []
    for row in accepted_rows:
        promotion_id = _text(row.get("promotion_id"))
        promotion_type = _text(row.get("promotion_type"))
        if promotion_type == "pattern":
            source_row = dict(pattern_by_promotion_id.get(promotion_id, {}) or {})
            accepted_pattern_promotions.append(
                {
                    "promotion_id": promotion_id,
                    "pattern_id": _text(source_row.get("pattern_id")) or _text(row.get("subject_id")),
                    "decision_reason": _text(row.get("decision_reason")),
                    "decision_timestamp": _text(row.get("decision_timestamp")),
                    "document_ref": _text(source_row.get("document_ref")) or _text(row.get("document_ref")),
                    "source_basis_id": _text(source_row.get("source_basis_id")) or _text(row.get("source_basis_id")),
                    "proposed_spec": dict(source_row.get("proposed_spec", {}) or {}),
                }
            )
        elif promotion_type == "combination":
            source_row = dict(combination_by_promotion_id.get(promotion_id, {}) or {})
            accepted_combination_promotions.append(
                {
                    "promotion_id": promotion_id,
                    "combination_id": _text(source_row.get("combination_id")) or _text(row.get("subject_id")),
                    "decision_reason": _text(row.get("decision_reason")),
                    "decision_timestamp": _text(row.get("decision_timestamp")),
                    "document_ref": _text(source_row.get("document_ref")) or _text(row.get("document_ref")),
                    "source_basis_id": _text(source_row.get("source_basis_id")) or _text(row.get("source_basis_id")),
                    "proposed_spec": dict(source_row.get("proposed_spec", {}) or {}),
                }
            )
    summary = {
        "accepted_pattern_count": len(accepted_pattern_promotions),
        "accepted_combination_count": len(accepted_combination_promotions),
        "accepted_total": len(accepted_pattern_promotions) + len(accepted_combination_promotions),
    }
    return {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        "summary": summary,
        "accepted_pattern_promotions": accepted_pattern_promotions,
        "accepted_combination_promotions": accepted_combination_promotions,
    }


def _version_file_tag(version: Any) -> str:
    text = _text(version)
    if not text:
        return "v1"
    if text.lower().startswith("v"):
        return text.lower()
    major = text.split(".", 1)[0].strip()
    if not major:
        major = "1"
    return f"v{major}"


def _build_registry_stage_preview(
    *,
    registry_bundle: dict[str, Any],
    registry_review_bundle: dict[str, Any],
) -> dict[str, Any]:
    bundle = dict(registry_bundle or {})
    review_bundle = dict(registry_review_bundle or {})
    registry_root = Path(_text(bundle.get("root")) or str(default_registry_root() if default_registry_root else ""))
    pattern_ids = set(dict(bundle.get("patterns_by_id", {}) or {}))
    combination_ids = set(dict(bundle.get("combinations_by_id", {}) or {}))
    stage_rows: list[dict[str, Any]] = []

    for row in list(review_bundle.get("accepted_pattern_promotions", []) or []):
        spec = dict(row.get("proposed_spec", {}) or {})
        item_id = _text(spec.get("id")) or _text(row.get("pattern_id"))
        version_tag = _version_file_tag(spec.get("version"))
        target_path = registry_root / "patterns" / f"{item_id}.{version_tag}.json"
        stage_rows.append(
            {
                "item_type": "pattern",
                "item_id": item_id,
                "version": _text(spec.get("version")) or "1.0.0",
                "target_path": str(target_path),
                "target_exists": target_path.exists(),
                "stage_action": "skip_existing_id" if item_id in pattern_ids else "write_candidate_file",
                "promotion_id": _text(row.get("promotion_id")),
            }
        )

    for row in list(review_bundle.get("accepted_combination_promotions", []) or []):
        spec = dict(row.get("proposed_spec", {}) or {})
        item_id = _text(spec.get("id")) or _text(row.get("combination_id"))
        version_tag = _version_file_tag(spec.get("version"))
        target_path = registry_root / "combinations" / f"{item_id}.{version_tag}.json"
        stage_rows.append(
            {
                "item_type": "combination",
                "item_id": item_id,
                "version": _text(spec.get("version")) or "1.0.0",
                "target_path": str(target_path),
                "target_exists": target_path.exists(),
                "stage_action": "skip_existing_id" if item_id in combination_ids else "write_candidate_file",
                "promotion_id": _text(row.get("promotion_id")),
            }
        )

    return {
        "generated_at": _utc_now_iso(),
        "registry_root": str(registry_root),
        "summary": {
            "total_rows": len(stage_rows),
            "write_candidate_file_count": sum(1 for row in stage_rows if row.get("stage_action") == "write_candidate_file"),
            "skip_existing_id_count": sum(1 for row in stage_rows if row.get("stage_action") == "skip_existing_id"),
        },
        "stage_rows": stage_rows,
    }


def _recommended_provider_action(
    *,
    auth_state: str,
    capability_enabled: bool,
    session_required: bool,
    access_route: str = "",
) -> str:
    if not session_required:
        return "public_fetch_ready"
    if not capability_enabled:
        return "enable_capability_flag"
    if access_route == "institutional_gateway":
        if auth_state == "profile_missing":
            return "initialize_institution_session_and_login"
        if auth_state == "profile_initialized_session_unknown":
            return "login_via_institution_and_validate_provider_access"
        if auth_state == "profile_present_session_unknown":
            return "validate_provider_access_via_institution_session"
        return "review_institution_provider_state"
    if auth_state == "profile_missing":
        return "initialize_profile_and_login"
    if auth_state == "profile_initialized_session_unknown":
        return "login_and_validate"
    if auth_state == "profile_present_session_unknown":
        return "validate_live_session"
    return "review_provider_state"


def _build_provider_handoff_bundle(*, licensed_research: dict[str, Any]) -> dict[str, Any]:
    licensed = dict(licensed_research or {})
    capability_enabled = bool(licensed.get("licensed_research_capability_enabled", False))
    provider_rows = list(licensed.get("provider_session_register", []) or [])
    handoff_rows: list[dict[str, Any]] = []
    for row in provider_rows:
        session_state = dict(row.get("session_state", {}) or {})
        provider_key = _text(row.get("provider_key"))
        auth_state = _text(session_state.get("auth_state"))
        session_required = bool(row.get("session_required", False))
        access_route = _text(row.get("access_route")) or _text(session_state.get("access_route"))
        handoff_rows.append(
            {
                "provider_key": provider_key,
                "display_name": _text(row.get("display_name")) or provider_key,
                "source_family": _text(row.get("source_family")),
                "session_required": session_required,
                "access_route": access_route,
                "profile_scope": _text(row.get("profile_scope")) or _text(session_state.get("profile_scope")),
                "auth_state": auth_state,
                "institution_name": _text(row.get("institution_name")) or _text(session_state.get("institution_name")),
                "institution_entry_url": _text(row.get("institution_entry_url")) or _text(session_state.get("institution_entry_url")),
                "validation_url": _text(row.get("validation_url")) or _text(session_state.get("validation_url")),
                "profile_path": _text(session_state.get("profile_path")),
                "profile_exists": bool(session_state.get("profile_exists", False)),
                "has_profile_contents": bool(session_state.get("has_profile_contents", False)),
                "sample_entry_url": _text(row.get("launch_url")) or _text(session_state.get("launch_url")) or _LICENSED_PROVIDER_STATUS_URLS.get(provider_key, ""),
                "recommended_action": _recommended_provider_action(
                    auth_state=auth_state,
                    capability_enabled=capability_enabled,
                    session_required=session_required,
                    access_route=access_route,
                ),
                **(
                    build_provider_bootstrap_plan(
                        provider_key=provider_key,
                        session_label="licensed",
                        launch_url=_LICENSED_PROVIDER_STATUS_URLS.get(provider_key, ""),
                        headless=False,
                        env=os.environ,
                    )
                    if build_provider_bootstrap_plan is not None and provider_key
                    else {}
                ),
            }
        )
    return {
        "generated_at": _utc_now_iso(),
        "capability_enabled": capability_enabled,
        "summary": {
            "provider_count": len(handoff_rows),
            "login_required_count": sum(1 for row in handoff_rows if row.get("session_required")),
            "ready_like_count": sum(
                1
                for row in handoff_rows
                if row.get("recommended_action") in {"public_fetch_ready", "validate_live_session"}
            ),
        },
        "provider_rows": handoff_rows,
    }


def _materialize_registry_stage_candidates(
    *,
    run_id: str,
    registry_review_bundle: dict[str, Any],
    registry_stage_preview: dict[str, Any],
) -> dict[str, Any]:
    run_dir = _registry_stage_candidate_run_dir(run_id)
    patterns_dir = run_dir / "patterns"
    combinations_dir = run_dir / "combinations"
    patterns_dir.mkdir(parents=True, exist_ok=True)
    combinations_dir.mkdir(parents=True, exist_ok=True)

    review_bundle = dict(registry_review_bundle or {})
    preview = dict(registry_stage_preview or {})
    pattern_promotions = {
        _text(row.get("promotion_id")): dict(row)
        for row in list(review_bundle.get("accepted_pattern_promotions", []) or [])
        if _text(row.get("promotion_id"))
    }
    combination_promotions = {
        _text(row.get("promotion_id")): dict(row)
        for row in list(review_bundle.get("accepted_combination_promotions", []) or [])
        if _text(row.get("promotion_id"))
    }

    materialized_rows: list[dict[str, Any]] = []
    for row in list(preview.get("stage_rows", []) or []):
        stage_row = dict(row)
        promotion_id = _text(stage_row.get("promotion_id"))
        stage_action = _text(stage_row.get("stage_action"))
        item_type = _text(stage_row.get("item_type"))
        item_id = _text(stage_row.get("item_id"))
        version = _text(stage_row.get("version")) or "1.0.0"
        version_tag = _version_file_tag(version)
        if item_type == "pattern":
            candidate_path = patterns_dir / f"{item_id}.{version_tag}.json"
            source_row = pattern_promotions.get(promotion_id, {})
        else:
            candidate_path = combinations_dir / f"{item_id}.{version_tag}.json"
            source_row = combination_promotions.get(promotion_id, {})
        if stage_action == "write_candidate_file":
            candidate_path.write_text(
                json.dumps(dict(source_row.get("proposed_spec", {}) or {}), indent=2, sort_keys=True),
                encoding="utf-8",
            )
        materialized_rows.append(
            {
                **stage_row,
                "candidate_path": str(candidate_path),
                "candidate_written": candidate_path.exists() if stage_action == "write_candidate_file" else False,
            }
        )

    manifest = {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        "stage_root": str(run_dir),
        "summary": {
            "total_rows": len(materialized_rows),
            "materialized_count": sum(1 for row in materialized_rows if row.get("candidate_written")),
            "skipped_count": sum(1 for row in materialized_rows if not row.get("candidate_written")),
        },
        "rows": materialized_rows,
    }
    manifest_path = _registry_stage_candidate_manifest_path(run_id)
    manifest_path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    manifest["path"] = str(manifest_path)
    return manifest


def _merge_registry_stage_candidates_to_registry(
    *,
    run_id: str,
    registry_stage_candidate_manifest: dict[str, Any],
) -> dict[str, Any]:
    manifest = dict(registry_stage_candidate_manifest or {})
    merged_rows: list[dict[str, Any]] = []

    for row in list(manifest.get("rows", []) or []):
        merge_row = dict(row)
        stage_action = _text(merge_row.get("stage_action"))
        item_type = _text(merge_row.get("item_type"))
        candidate_path = Path(_text(merge_row.get("candidate_path")))
        target_path = Path(_text(merge_row.get("target_path")))
        merge_action = "not_attempted"
        merged = False
        validation_error = ""

        if stage_action != "write_candidate_file":
            merge_action = "skip_non_write_stage_action"
        elif not candidate_path.exists():
            merge_action = "missing_candidate_file"
        elif target_path.exists():
            merge_action = "skip_existing_target"
        else:
            try:
                payload = json.loads(candidate_path.read_text(encoding="utf-8"))
                if item_type == "pattern" and validate_pattern_spec is not None:
                    payload = validate_pattern_spec(payload)
                elif item_type == "combination" and validate_combination_spec is not None:
                    payload = validate_combination_spec(payload)
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(
                    json.dumps(payload, indent=2, sort_keys=True),
                    encoding="utf-8",
                )
                merge_action = "merged_to_registry"
                merged = True
            except Exception as exc:
                merge_action = "validation_or_write_error"
                validation_error = str(exc)

        merged_rows.append(
            {
                **merge_row,
                "merge_action": merge_action,
                "merged_to_registry": merged,
                "validation_error": validation_error,
                "target_exists_after_merge": target_path.exists(),
            }
        )

    merge_manifest = {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        "stage_root": _text(manifest.get("stage_root")),
        "summary": {
            "total_rows": len(merged_rows),
            "merged_count": sum(1 for row in merged_rows if row.get("merged_to_registry")),
            "skip_existing_target_count": sum(1 for row in merged_rows if row.get("merge_action") == "skip_existing_target"),
            "missing_candidate_file_count": sum(1 for row in merged_rows if row.get("merge_action") == "missing_candidate_file"),
            "validation_or_write_error_count": sum(1 for row in merged_rows if row.get("merge_action") == "validation_or_write_error"),
            "skip_non_write_stage_action_count": sum(1 for row in merged_rows if row.get("merge_action") == "skip_non_write_stage_action"),
        },
        "rows": merged_rows,
    }
    path = _registry_stage_merge_manifest_path(run_id)
    path.write_text(json.dumps(merge_manifest, indent=2, sort_keys=True), encoding="utf-8")
    merge_manifest["path"] = str(path)
    merge_manifest["exists"] = True
    return merge_manifest


def _materialize_provider_session_handoff(
    *,
    run_id: str,
    provider_handoff_bundle: dict[str, Any],
) -> dict[str, Any]:
    manifest = {
        "run_id": _text(run_id),
        "generated_at": _utc_now_iso(),
        **dict(provider_handoff_bundle or {}),
    }
    path = _provider_session_handoff_manifest_path(run_id)
    _PROVIDER_SESSION_HANDOFF_DIR.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(manifest, indent=2, sort_keys=True), encoding="utf-8")
    manifest["path"] = str(path)
    manifest["exists"] = True
    return manifest


def _active_skill_pattern_state(run_d: dict[str, Any]) -> tuple[list[str], list[dict[str, Any]], list[str]]:
    if build_active_skill_pattern_state is None:
        return [], [], []
    return build_active_skill_pattern_state(
        motor_049_output=_load_motor_output(run_d, "motor_049"),
        motor_051_output=_load_motor_output(run_d, "motor_051"),
        motor_052_output=_load_motor_output(run_d, "motor_052"),
        motor_053_output=_load_motor_output(run_d, "motor_053"),
    )


def _licensed_research_activity(run_d: dict[str, Any]) -> dict[str, Any]:
    capability_enabled = (
        licensed_research_acquisition_enabled(os.environ)
        if licensed_research_acquisition_enabled is not None
        else False
    )
    provider_rows: list[dict[str, Any]] = []
    if build_provider_session_plan is not None:
        for provider_key, url in _LICENSED_PROVIDER_STATUS_URLS.items():
            try:
                plan = build_provider_session_plan(
                    url=url,
                    retrieval_purpose="dashboard_operational_status",
                    session_label="licensed",
                    env=os.environ,
                )
            except Exception:
                continue
            provider_rows.append(
                {
                    "provider_key": provider_key,
                    "display_name": str(plan.get("display_name", provider_key)).strip() or provider_key,
                    "source_family": str(plan.get("source_family", "")).strip(),
                    "session_required": bool(plan.get("session_required", False)),
                    "access_route": str(plan.get("access_route", "")).strip(),
                    "profile_scope": str(plan.get("profile_scope", "")).strip(),
                    "institution_name": str(plan.get("institution_name", "")).strip(),
                    "institution_entry_url": str(plan.get("institution_entry_url", "")).strip(),
                    "launch_url": str(plan.get("launch_url", "")).strip(),
                    "validation_url": str(plan.get("validation_url", "")).strip(),
                    "session_state": dict(plan.get("session_state", {}) or {}),
                }
            )
    activity = dict((run_d or {}).get("licensed_research_activity", {}) or {})
    run_id = str((run_d or {}).get("run_id", "")).strip()
    discovery_queue_manifest = _load_licensed_discovery_queue_manifest(run_id) if run_id else {"exists": False}
    direct_discovery_queue = dict(activity.get("discovery_candidate_queue", {}) or {})
    active_discovery_queue = (
        discovery_queue_manifest
        if discovery_queue_manifest.get("exists")
        else direct_discovery_queue
    )
    acquisition_plan = dict(activity.get("acquisition_plan", (run_d or {}).get("acquisition_plan", {})) or {})
    acquisition_result = dict(activity.get("acquisition_result", (run_d or {}).get("acquisition_result", {})) or {})
    research_document_manifest = dict(
        activity.get("research_document_manifest", (run_d or {}).get("research_document_manifest", {})) or {}
    )
    knowledge_extraction_record = dict(
        activity.get("knowledge_extraction_record", (run_d or {}).get("knowledge_extraction_record", {})) or {}
    )
    extraction_review_register = list(
        activity.get("extraction_review_register", (run_d or {}).get("extraction_review_register", [])) or []
    )
    approved_pattern_promotion_register = list(
        activity.get(
            "approved_pattern_promotion_register",
            (run_d or {}).get("approved_pattern_promotion_register", []),
        )
        or []
    )
    approved_combination_promotion_register = list(
        activity.get(
            "approved_combination_promotion_register",
            (run_d or {}).get("approved_combination_promotion_register", []),
        )
        or []
    )
    extraction_review_register.extend(list(active_discovery_queue.get("extraction_review_register", []) or []))
    approved_pattern_promotion_register.extend(list(active_discovery_queue.get("approved_pattern_promotion_register", []) or []))
    approved_combination_promotion_register.extend(list(active_discovery_queue.get("approved_combination_promotion_register", []) or []))

    discovery_edit_store = _load_discovery_candidate_edit_store(run_id) if run_id else {"edits": [], "path": ""}
    discovery_edit_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(discovery_edit_store.get("edits", []) or [])
        if _text(row.get("candidate_id"))
    }
    try:
        registry_bundle = load_registry_bundle() if load_registry_bundle is not None else {}
    except Exception:
        registry_bundle = {}
    discovery_candidate_rows: list[dict[str, Any]] = []
    for row in list(active_discovery_queue.get("candidate_rows", []) or []):
        candidate_row = dict(row or {})
        candidate_id = _text(candidate_row.get("candidate_id"))
        edited_row = _apply_discovery_candidate_edit(
            candidate_row,
            discovery_edit_by_id.get(candidate_id),
            registry_bundle=registry_bundle,
        )
        discovery_candidate_rows.append(edited_row)

    discovery_review_register = [
        {
            "candidate_id": _text(row.get("candidate_id")),
            "provider_key": _text((row.get("metadata_payload", {}) or {}).get("provider_key")),
            "title": _text(row.get("title")),
            "source_url": _text(row.get("source_url")),
            "doi": _text(row.get("doi")),
            "journal": _text(row.get("journal")),
            "published_year": _text(row.get("published_year")),
            "expected_pdf_name": _text(row.get("expected_pdf_name")),
            "notes": _text((row.get("metadata_payload", {}) or {}).get("notes")),
            "metadata_payload": dict(row.get("metadata_payload", {}) or {}),
            "matched_pattern_ids": list(row.get("matched_pattern_ids", []) or []),
            "matched_combination_ids": list(row.get("matched_combination_ids", []) or []),
            "priority_score": int(row.get("priority_score", 0) or 0),
            "reference_state": "metadata_only",
            "operator_decision": "candidate",
            "decision_reason": "",
        }
        for row in discovery_candidate_rows
    ]
    discovery_decision_store = _load_discovery_candidate_decision_store(run_id) if run_id else {"decisions": [], "path": ""}
    discovery_review_register = _merge_discovery_review_with_decisions(
        discovery_review_register=discovery_review_register,
        decision_records=list(discovery_decision_store.get("decisions", []) or []),
    )
    discovery_decision_summary = _summarize_discovery_candidate_decisions(discovery_review_register)
    article_reference_store = _load_article_reference_record_store(run_id) if run_id else {"records": [], "path": "", "exists": False}
    article_reference_by_id = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(article_reference_store.get("records", []) or [])
        if _text(row.get("candidate_id"))
    }
    article_reference_register = [
        _build_article_reference_record(
            candidate_row=row,
            reference_record=article_reference_by_id.get(_text(row.get("candidate_id"))),
        )
        for row in discovery_candidate_rows
    ]
    search_result_capture_register = (
        build_search_result_capture_register(
            discovery_candidate_review_register=discovery_review_register,
            article_reference_register=article_reference_register,
        )
        if build_search_result_capture_register is not None
        else []
    )
    search_result_capture_sequence = (
        build_search_result_capture_sequence(
            search_result_capture_register=search_result_capture_register,
            batch_size=4,
        )
        if build_search_result_capture_sequence is not None
        else {
            "rows": search_result_capture_register,
            "current_row": {},
            "next_rows": [],
            "summary": {
                "total": len(search_result_capture_register),
                "pending": 0,
                "closed": len(search_result_capture_register),
                "needs_draft": 0,
                "seed_only": 0,
                "result_captured": 0,
                "excerpt_resolved": 0,
                "current_position": 0,
                "batch_size": 4,
            },
        }
    )
    search_query_execution_register = (
        build_search_query_execution_register(
            search_result_capture_register=list(search_result_capture_sequence.get("rows", []) or []),
        )
        if build_search_query_execution_register is not None
        else []
    )
    search_query_result_import_store = (
        _load_search_query_result_import_store(run_id)
        if run_id
        else {"result_records": [], "path": "", "exists": False}
    )
    search_query_execution_register = (
        build_search_query_result_option_register(
            search_query_execution_register=search_query_execution_register,
            imported_result_records=list(search_query_result_import_store.get("result_records", []) or []),
        )
        if build_search_query_result_option_register is not None
        else search_query_execution_register
    )
    search_query_execution_sequence = (
        build_search_query_execution_sequence(
            search_query_execution_register=search_query_execution_register,
            batch_size=4,
        )
        if build_search_query_execution_sequence is not None
        else {
            "rows": search_query_execution_register,
            "current_row": {},
            "next_rows": [],
            "summary": {
                "total": len(search_query_execution_register),
                "pending": 0,
                "closed": len(search_query_execution_register),
                "search_ready_needs_reference_draft": 0,
                "search_ready_capture_pending": 0,
                "result_captured_ready_for_excerpt": 0,
                "current_position": 0,
                "batch_size": 4,
            },
        }
    )
    search_query_result_option_review_sequence = (
        build_search_query_result_option_review_sequence(
            search_query_execution_register=list(search_query_execution_sequence.get("rows", []) or []),
            batch_size=4,
        )
        if build_search_query_result_option_review_sequence is not None
        else {
            "rows": [],
            "current_row": {},
            "next_rows": [],
            "summary": {
                "total": 0,
                "pending": 0,
                "current_position": 0,
                "candidate_count": 0,
                "option_count": 0,
                "batch_size": 4,
            },
        }
    )
    search_query_result_option_batch_plan = (
        build_search_query_result_option_batch_plan(
            search_query_result_option_review_register=list(search_query_result_option_review_sequence.get("rows", []) or []),
            batch_size=4,
        )
        if build_search_query_result_option_batch_plan is not None
        else {
            "available": False,
            "option_count": 0,
            "candidate_count": 0,
            "candidate_ids": [],
            "option_review_ids": [],
            "batch_reason": "imported-result batch planning unavailable",
            "promote_records_json_template": "[]",
            "accepted_promote_formats": ["structured_records", "json_array"],
        }
    )
    search_query_execution_batch_plan = (
        build_search_query_execution_batch_plan(
            search_query_execution_register=list(search_query_execution_sequence.get("rows", []) or []),
            batch_size=4,
        )
        if build_search_query_execution_batch_plan is not None
        else {
            "available": False,
            "candidate_count": 0,
            "candidate_ids": [],
            "packet_template": "",
            "batch_reason": "search query batch planning unavailable",
        }
    )
    reference_resolution_sequence = _build_reference_resolution_sequence(
        article_reference_register=article_reference_register,
    )
    reference_resolution_batch_plan = _build_reference_resolution_batch_plan(
        article_reference_register=article_reference_register,
        reference_resolution_sequence=reference_resolution_sequence,
    )
    reference_state_by_id = {
        _text(row.get("candidate_id")): _text(row.get("reference_state"))
        for row in article_reference_register
    }
    for row in discovery_review_register:
        row["reference_state"] = reference_state_by_id.get(_text(row.get("candidate_id")), _text(row.get("reference_state")) or "metadata_only")
    accepted_discovery_candidate_bundle = _build_accepted_discovery_candidate_bundle(
        run_id=run_id,
        discovery_review_register=discovery_review_register,
        discovery_candidate_rows=discovery_candidate_rows,
        article_reference_register=article_reference_register,
    )
    accepted_discovery_candidate_bundle_manifest = (
        _load_accepted_discovery_candidate_bundle_manifest(run_id) if run_id else {"exists": False, "path": ""}
    )
    reference_backed_promotion_manifest = (
        _load_reference_backed_promotion_manifest(run_id) if run_id else {"exists": False, "path": ""}
    )
    knowledge_atom_refresh_summary = (
        _load_knowledge_atom_refresh_summary(run_id) if run_id else {"exists": False, "path": ""}
    )
    combination_rerank_summary = (
        _load_combination_rerank_summary(run_id) if run_id else {"exists": False, "path": ""}
    )
    search_query_execution_manifest = (
        _load_search_query_execution_manifest(run_id) if run_id else {"exists": False, "path": ""}
    )
    search_query_execution_session_store = (
        _load_search_query_execution_session_store(run_id) if run_id else {"rows": [], "path": "", "exists": False}
    )
    search_query_execution_session_bundle = dict(search_query_execution_manifest.get("session_bundle", {}) or {})
    if not bool(search_query_execution_session_bundle.get("available")):
        search_query_execution_session_bundle = _build_search_query_execution_session_bundle(
            batch_plan=dict(search_query_execution_batch_plan or {}),
            rows=list(search_query_execution_sequence.get("rows", []) or []),
        )
    merged_session_rows = _merge_search_query_execution_session_rows(
        base_rows=list(search_query_execution_session_bundle.get("rows", []) or []),
        override_rows=list(search_query_execution_session_store.get("rows", []) or []),
    )
    search_query_execution_session_bundle["rows"] = merged_session_rows
    search_query_execution_session_bundle["summary"] = _summarize_search_query_execution_session_rows(merged_session_rows)
    search_query_execution_session_bundle["materialized"] = bool(search_query_execution_manifest.get("exists"))
    search_query_execution_session_bundle["manifest_path"] = _text(search_query_execution_manifest.get("path"))
    extraction_records = _collect_licensed_extraction_records(
        knowledge_extraction_record=knowledge_extraction_record,
        discovery_candidate_rows=discovery_candidate_rows,
        reference_backed_promotion_manifest=reference_backed_promotion_manifest,
        activity=activity,
        run_d=run_d,
    )
    knowledge_atom_register = (
        build_knowledge_atom_register(
            extraction_records=extraction_records,
            article_reference_register=article_reference_register,
        )
        if build_knowledge_atom_register is not None
        else []
    )
    source_coverage_summary = (
        summarize_source_coverage(
            knowledge_atom_register=knowledge_atom_register,
            extraction_records=extraction_records,
            article_reference_register=article_reference_register,
            discovery_candidate_review_register=discovery_review_register,
        )
        if summarize_source_coverage is not None
        else {
            "knowledge_atom_count": len(knowledge_atom_register),
            "document_count": len(extraction_records),
            "provider_count": 0,
            "providers": [],
            "knowledge_types": [],
            "supported_pattern_count": 0,
            "supported_pattern_ids": [],
            "extraction_record_count": len(extraction_records),
            "reference_record_count": len(article_reference_register),
            "visible_reference_count": 0,
            "accepted_reference_count": 0,
            "coverage_strength": "empty",
        }
    )
    source_family_coverage_register = (
        build_source_family_coverage_register(
            provider_session_register=provider_rows,
            discovery_candidate_review_register=discovery_review_register,
            article_reference_register=article_reference_register,
            extraction_records=extraction_records,
            knowledge_atom_register=knowledge_atom_register,
            mode="standard",
        )
        if build_source_family_coverage_register is not None
        else []
    )
    approved_pattern_promotion_register = _merge_promotion_rows(
        approved_pattern_promotion_register,
        list(reference_backed_promotion_manifest.get("approved_pattern_promotion_register", []) or []),
    )
    approved_combination_promotion_register = _merge_promotion_rows(
        approved_combination_promotion_register,
        list(reference_backed_promotion_manifest.get("approved_combination_promotion_register", []) or []),
    )
    promotion_edit_store = _load_promotion_edit_store(run_id) if run_id else {"edits": [], "path": "", "updated_at": ""}
    promotion_edit_by_id = {
        _text(row.get("promotion_id")): dict(row)
        for row in list(promotion_edit_store.get("edits", []) or [])
        if _text(row.get("promotion_id"))
    }
    approved_pattern_promotion_register = [
        _apply_promotion_edit(row, promotion_edit_by_id.get(_text(row.get("promotion_id")) or f"pattern::{_text(row.get('pattern_id'))}"))
        for row in approved_pattern_promotion_register
    ]
    approved_combination_promotion_register = [
        _apply_promotion_edit(row, promotion_edit_by_id.get(_text(row.get("promotion_id")) or f"combination::{_text(row.get('combination_id'))}"))
        for row in approved_combination_promotion_register
    ]
    promotion_review_register = [
        {
            "promotion_id": _text(row.get("promotion_id")) or f"pattern::{_text(row.get('pattern_id'))}",
            "promotion_type": "pattern",
            "subject_id": _text(row.get("pattern_id")),
            "subject_name": _text((row.get("proposed_spec", {}) or {}).get("name")) or _text(row.get("pattern_id")),
            "promotion_state": _text(row.get("promotion_state")) or "ready_for_registry_review",
            "document_ref": _text(row.get("document_ref")),
            "source_basis_id": _text(row.get("source_basis_id")),
            "minimum_evidence": list((row.get("proposed_spec", {}) or {}).get("minimum_evidence_to_activate", []) or []),
            "knowledge_type": ", ".join(list((row.get("proposed_spec", {}) or {}).get("knowledge_type", []) or [])),
            "operator_decision": "candidate",
            "edit_timestamp": _text(row.get("edit_timestamp")),
        }
        for row in approved_pattern_promotion_register
    ]
    promotion_review_register.extend(
        {
            "promotion_id": _text(row.get("promotion_id")) or f"combination::{_text(row.get('combination_id'))}",
            "promotion_type": "combination",
            "subject_id": _text(row.get("combination_id")),
            "subject_name": _text((row.get("proposed_spec", {}) or {}).get("name")) or _text(row.get("combination_id")),
            "promotion_state": _text(row.get("promotion_state")) or "ready_for_registry_review",
            "document_ref": _text(row.get("document_ref")),
            "source_basis_id": _text(row.get("source_basis_id")),
            "minimum_evidence": list((row.get("proposed_spec", {}) or {}).get("minimum_evidence", []) or []),
            "knowledge_type": "combination",
            "operator_decision": "candidate",
            "edit_timestamp": _text(row.get("edit_timestamp")),
        }
        for row in approved_combination_promotion_register
    )
    decision_store = _load_promotion_decision_store(run_id) if run_id else {"run_id": "", "updated_at": "", "decisions": [], "path": ""}
    promotion_review_register = _merge_promotion_review_with_decisions(
        promotion_review_register=promotion_review_register,
        decision_records=list(decision_store.get("decisions", []) or []),
    )
    promotion_decision_summary = _summarize_promotion_decisions(promotion_review_register)
    registry_review_bundle = _build_registry_review_bundle(
        run_id=run_id,
        licensed_research={
            "promotion_review_register": promotion_review_register,
            "approved_pattern_promotion_register": approved_pattern_promotion_register,
            "approved_combination_promotion_register": approved_combination_promotion_register,
        },
    )
    provider_handoff_bundle = _build_provider_handoff_bundle(
        licensed_research={
            "licensed_research_capability_enabled": capability_enabled,
            "provider_session_register": provider_rows,
        }
    )
    registry_stage_preview = _build_registry_stage_preview(
        registry_bundle=registry_bundle,
        registry_review_bundle=registry_review_bundle,
    )
    registry_stage_candidate_manifest = _load_registry_stage_candidate_manifest(run_id) if run_id else {"exists": False, "path": ""}
    registry_stage_merge_manifest = _load_registry_stage_merge_manifest(run_id) if run_id else {"exists": False, "path": ""}
    provider_session_handoff_manifest = _load_provider_session_handoff_manifest(run_id) if run_id else {"exists": False, "path": ""}
    ready_provider_count = sum(
        1
        for row in provider_rows
        if str((row.get("session_state", {}) or {}).get("auth_state", "")).strip()
        in {"profile_present_session_unknown", "session_not_required"}
    )
    return {
        "available": bool(build_provider_session_plan is not None),
        "licensed_research_capability_enabled": capability_enabled,
        "provider_session_register": provider_rows,
        "provider_summary": {
            "provider_count": len(provider_rows),
            "ready_provider_count": ready_provider_count,
            "session_required_count": sum(1 for row in provider_rows if row.get("session_required")),
        },
        "acquisition_plan": acquisition_plan,
        "acquisition_result": acquisition_result,
        "research_document_manifest": research_document_manifest,
        "knowledge_extraction_record": knowledge_extraction_record,
        "extraction_records": extraction_records,
        "extraction_review_register": extraction_review_register,
        "knowledge_atom_register": knowledge_atom_register,
        "source_coverage_summary": source_coverage_summary,
        "source_family_coverage_register": source_family_coverage_register,
        "approved_pattern_promotion_register": approved_pattern_promotion_register,
        "approved_combination_promotion_register": approved_combination_promotion_register,
        "promotion_review_register": promotion_review_register,
        "promotion_decision_summary": promotion_decision_summary,
        "promotion_decision_store": {
            "updated_at": _text(decision_store.get("updated_at")),
            "path": _text(decision_store.get("path")),
            "stored_decision_count": len(list(decision_store.get("decisions", []) or [])),
        },
        "promotion_edit_store": {
            "updated_at": _text(promotion_edit_store.get("updated_at")),
            "path": _text(promotion_edit_store.get("path")),
            "stored_edit_count": len(list(promotion_edit_store.get("edits", []) or [])),
        },
        "discovery_candidate_queue": active_discovery_queue,
        "discovery_candidate_review_register": discovery_review_register,
        "discovery_candidate_decision_summary": discovery_decision_summary,
        "discovery_candidate_decision_store": {
            "updated_at": _text(discovery_decision_store.get("updated_at")),
            "path": _text(discovery_decision_store.get("path")),
            "stored_decision_count": len(list(discovery_decision_store.get("decisions", []) or [])),
        },
        "discovery_candidate_edit_store": {
            "updated_at": _text(discovery_edit_store.get("updated_at")),
            "path": _text(discovery_edit_store.get("path")),
            "stored_edit_count": len(list(discovery_edit_store.get("edits", []) or [])),
        },
        "article_reference_register": article_reference_register,
        "search_result_capture_register": list(search_result_capture_sequence.get("rows", []) or []),
        "current_search_result_capture_row": dict(search_result_capture_sequence.get("current_row", {}) or {}),
        "next_search_result_capture_rows": list(search_result_capture_sequence.get("next_rows", []) or []),
        "search_result_capture_summary": dict(search_result_capture_sequence.get("summary", {}) or {}),
        "search_query_execution_register": list(search_query_execution_sequence.get("rows", []) or []),
        "current_search_query_execution_row": dict(search_query_execution_sequence.get("current_row", {}) or {}),
        "next_search_query_execution_rows": list(search_query_execution_sequence.get("next_rows", []) or []),
        "search_query_execution_summary": dict(search_query_execution_sequence.get("summary", {}) or {}),
        "search_query_result_option_review_register": list(search_query_result_option_review_sequence.get("rows", []) or []),
        "current_search_query_result_option_row": dict(search_query_result_option_review_sequence.get("current_row", {}) or {}),
        "next_search_query_result_option_rows": list(search_query_result_option_review_sequence.get("next_rows", []) or []),
        "search_query_result_option_summary": dict(search_query_result_option_review_sequence.get("summary", {}) or {}),
        "search_query_result_option_batch_plan": dict(search_query_result_option_batch_plan or {}),
        "search_query_execution_batch_plan": dict(search_query_execution_batch_plan or {}),
        "search_query_execution_session_bundle": dict(search_query_execution_session_bundle or {}),
        "search_query_execution_manifest": search_query_execution_manifest,
        "search_query_execution_session_store": {
            "updated_at": _text(search_query_execution_session_store.get("updated_at")),
            "path": _text(search_query_execution_session_store.get("path")),
            "stored_row_count": len(list(search_query_execution_session_store.get("rows", []) or [])),
            "exists": bool(search_query_execution_session_store.get("exists")),
        },
        "search_query_result_import_store": search_query_result_import_store,
        "reference_resolution_sequence_register": list(reference_resolution_sequence.get("rows", []) or []),
        "current_reference_resolution_row": dict(reference_resolution_sequence.get("current_row", {}) or {}),
        "next_reference_resolution_rows": list(reference_resolution_sequence.get("next_rows", []) or []),
        "reference_resolution_queue_summary": dict(reference_resolution_sequence.get("summary", {}) or {}),
        "reference_resolution_batch_plan": reference_resolution_batch_plan,
        "article_reference_store": {
            "updated_at": _text(article_reference_store.get("updated_at")),
            "path": _text(article_reference_store.get("path")),
            "stored_record_count": len(list(article_reference_store.get("records", []) or [])),
            "exists": bool(article_reference_store.get("exists")),
        },
        "accepted_discovery_candidate_bundle": accepted_discovery_candidate_bundle,
        "accepted_discovery_candidate_bundle_manifest": accepted_discovery_candidate_bundle_manifest,
        "reference_backed_promotion_manifest": reference_backed_promotion_manifest,
        "knowledge_atom_refresh_summary": knowledge_atom_refresh_summary,
        "combination_rerank_summary": combination_rerank_summary,
        "provider_handoff_bundle": provider_handoff_bundle,
        "provider_session_handoff_manifest": provider_session_handoff_manifest,
        "registry_review_bundle": registry_review_bundle,
        "registry_stage_preview": registry_stage_preview,
        "registry_stage_candidate_manifest": registry_stage_candidate_manifest,
        "registry_stage_merge_manifest": registry_stage_merge_manifest,
    }


def _congruence_brain_activity(run_d: dict[str, Any]) -> dict[str, Any]:
    if load_registry_bundle is None or build_combination_activation_register is None or build_combination_review_register is None:
        return {
            "available": False,
            "reason": "zlab_skill_unavailable",
            "active_pattern_ids": [],
            "active_pattern_sources": [],
            "combination_activation_register": [],
            "combination_review_register": [],
            "decision_summary": {"total": 0, "by_decision": {}},
            "licensed_research": _licensed_research_activity(run_d),
            "promotion_summary": {"approved_patterns": 0, "approved_combinations": 0, "reviewed_extractions": 0},
        }

    try:
        registry_bundle = load_registry_bundle()
    except Exception as exc:
        return {
            "available": False,
            "reason": f"registry_load_failed:{str(exc)[:120]}",
            "active_pattern_ids": [],
            "active_pattern_sources": [],
            "combination_activation_register": [],
            "combination_review_register": [],
            "decision_summary": {"total": 0, "by_decision": {}},
            "licensed_research": _licensed_research_activity(run_d),
            "promotion_summary": {"approved_patterns": 0, "approved_combinations": 0, "reviewed_extractions": 0},
        }

    motor_052_output = _load_motor_output(run_d, "motor_052")
    motor_049_output = _load_motor_output(run_d, "motor_049")
    motor_051_output = _load_motor_output(run_d, "motor_051")
    motor_053_output = _load_motor_output(run_d, "motor_053")
    active_pattern_ids, active_pattern_sources, anti_trigger_signals = _active_skill_pattern_state(run_d)
    activation_register = build_combination_activation_register(
        registry_bundle=registry_bundle,
        active_pattern_ids=active_pattern_ids,
        anti_trigger_signals=anti_trigger_signals,
    )
    if apply_combination_validators is not None:
        activation_register = apply_combination_validators(
            activation_register,
            registry_bundle=registry_bundle,
        )
    registry_pattern_activation_register = (
        build_registry_pattern_activation_register(
            registry_bundle=registry_bundle,
            active_pattern_sources=active_pattern_sources,
        )
        if build_registry_pattern_activation_register is not None
        else []
    )
    licensed_research = _licensed_research_activity(run_d)
    asset_family_research_profile = dict((motor_049_output or {}).get("asset_family_research_profile", {}) or {})
    asset_context_vector = (
        build_asset_context_vector(
            asset_family_research_profile=asset_family_research_profile,
            runtime_context=dict((run_d or {}).get("asset_context", {}) or {}),
            motor_051_output=motor_051_output,
            motor_052_output=motor_052_output,
            motor_053_output=motor_053_output,
        )
        if build_asset_context_vector is not None
        else {}
    )
    context_differentiator_register = (
        build_context_differentiator_register(asset_context_vector=asset_context_vector)
        if build_context_differentiator_register is not None
        else []
    )
    latent_combination_candidate_register = (
        build_latent_combination_candidate_register(
            registry_bundle=registry_bundle,
            active_pattern_ids=active_pattern_ids,
            active_pattern_rows=registry_pattern_activation_register,
            asset_context_vector=asset_context_vector,
            knowledge_atom_register=list(licensed_research.get("knowledge_atom_register", []) or []),
        )
        if build_latent_combination_candidate_register is not None
        else []
    )
    latent_combination_cluster_register = (
        build_latent_combination_cluster_register(
            latent_combination_candidate_register=latent_combination_candidate_register,
        )
        if build_latent_combination_cluster_register is not None
        else []
    )
    admissible_combination_review_register = (
        build_admissible_combination_review_register(
            latent_combination_candidate_register=latent_combination_candidate_register,
            default_decision="needs_review",
        )
        if build_admissible_combination_review_register is not None
        else []
    )
    review_register = build_combination_review_register(
        combination_activation_register=activation_register,
    )

    run_id = str((run_d or {}).get("run_id", "")).strip()
    latent_cluster_override_store = (
        _load_latent_cluster_override_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "split_assignments": [], "merge_assignments": [], "path": ""}
    )
    latent_cluster_override_result = _apply_latent_cluster_overrides(
        latent_combination_candidate_register=latent_combination_candidate_register,
        latent_combination_cluster_register=latent_combination_cluster_register,
        admissible_combination_review_register=admissible_combination_review_register,
        override_store=latent_cluster_override_store,
    )
    latent_combination_candidate_register = list(
        latent_cluster_override_result.get("latent_combination_candidate_register", []) or []
    )
    latent_combination_cluster_register = list(
        latent_cluster_override_result.get("latent_combination_cluster_register", []) or []
    )
    admissible_combination_review_register = list(
        latent_cluster_override_result.get("admissible_combination_review_register", []) or []
    )
    decision_store = _load_combination_decision_store(run_id) if run_id else {"run_id": "", "updated_at": "", "decisions": [], "path": ""}
    if merge_combination_review_with_decisions is not None:
        review_register = merge_combination_review_with_decisions(
            combination_review_register=review_register,
            decision_records=list(decision_store.get("decisions", []) or []),
        )
        admissible_combination_review_register = merge_combination_review_with_decisions(
            combination_review_register=admissible_combination_review_register,
            decision_records=list(decision_store.get("decisions", []) or []),
        )
    combination_edit_store = _load_combination_edit_store(run_id) if run_id else {"run_id": "", "updated_at": "", "edits": [], "path": ""}
    combination_edit_by_id = {
        _text(row.get("combination_id")): dict(row)
        for row in list(combination_edit_store.get("edits", []) or [])
        if _text(row.get("combination_id"))
    }
    review_register = [
        _apply_combination_edit(row, combination_edit_by_id.get(_text(row.get("combination_id"))))
        for row in review_register
    ]
    admissible_combination_review_register = [
        _apply_combination_edit(row, combination_edit_by_id.get(_text(row.get("combination_id"))))
        for row in admissible_combination_review_register
    ]
    combination_review_control_store = (
        _load_combination_review_control_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "deferred_combination_ids": [], "batch_size": 1, "path": ""}
    )
    combination_review_sequence = _build_combination_review_sequence(
        combination_review_register=review_register,
        admissible_combination_review_register=admissible_combination_review_register,
        review_control_store=combination_review_control_store,
    )
    combination_search_gap_record = (
        build_combination_search_gap_record(
            latent_combination_candidate_register=latent_combination_candidate_register,
            admissible_combination_review_register=admissible_combination_review_register,
            source_coverage_summary=dict(licensed_research.get("source_coverage_summary", {}) or {}),
            source_family_coverage_register=list(licensed_research.get("source_family_coverage_register", []) or []),
            asset_context_vector=asset_context_vector,
            active_pattern_ids=active_pattern_ids,
        )
        if build_combination_search_gap_record is not None
        else {
            "search_status": "unknown",
            "severity": "low",
            "gap_flags": [],
            "recommended_actions": [],
            "summary": "",
        }
    )
    research_campaign_record = (
        build_research_campaign_record(
            run_id=run_id,
            asset_context_vector=asset_context_vector,
            source_family_coverage_register=list(licensed_research.get("source_family_coverage_register", []) or []),
            source_coverage_summary=dict(licensed_research.get("source_coverage_summary", {}) or {}),
            combination_search_gap_record=combination_search_gap_record,
            mode="standard",
        )
        if build_research_campaign_record is not None
        else {
            "run_id": run_id,
            "mode": "standard",
            "campaign_status": "unknown",
            "top_next_actions": [],
            "summary": "",
        }
    )
    combination_follow_on_research_register = (
        build_combination_follow_on_research_register(
            combination_review_sequence_register=list(combination_review_sequence.get("rows", []) or []),
            source_family_coverage_register=list(licensed_research.get("source_family_coverage_register", []) or []),
            research_campaign_record=research_campaign_record,
        )
        if build_combination_follow_on_research_register is not None
        else []
    )
    combination_follow_on_execution_manifest_register = (
        build_combination_campaign_execution_manifest_register(
            combination_follow_on_research_register=combination_follow_on_research_register,
            source_family_coverage_register=list(licensed_research.get("source_family_coverage_register", []) or []),
        )
        if build_combination_campaign_execution_manifest_register is not None
        else []
    )
    research_campaign_trigger_store = (
        _load_research_campaign_trigger_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "triggers": [], "path": "", "exists": False}
    )
    combination_follow_on_manifest_store = (
        _load_combination_follow_on_manifest_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "manifests": [], "path": "", "exists": False}
    )
    research_loop_state_store = (
        _load_research_loop_state_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "state": {}, "current_job": {}, "path": "", "exists": False}
    )
    research_loop_job_store = (
        _load_research_loop_job_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "jobs": [], "current_job": {}, "path": "", "exists": False}
    )
    research_loop_metric_store = (
        _load_research_loop_metric_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "metrics": {}, "stop_condition": {}, "path": "", "exists": False}
    )
    research_loop_control_store = (
        _load_research_loop_control_store(run_id)
        if run_id
        else {
            "run_id": "",
            "updated_at": "",
            "control_state": "active",
            "requested_action": "resume",
            "control_reason": "",
            "path": "",
            "exists": False,
        }
    )
    research_loop_event_store = (
        _load_research_loop_event_store(run_id)
        if run_id
        else {"run_id": "", "updated_at": "", "events": [], "path": "", "exists": False}
    )
    research_campaign_trigger_register = (
        build_research_campaign_trigger_register(
            source_family_coverage_register=list(licensed_research.get("source_family_coverage_register", []) or []),
            research_campaign_record=research_campaign_record,
            stored_trigger_records=list(research_campaign_trigger_store.get("triggers", []) or []),
        )
        if build_research_campaign_trigger_register is not None
        else []
    )
    research_loop_snapshot = (
        build_research_loop_snapshot(
            run_id=run_id,
            current_combination_review_row=dict(combination_review_sequence.get("current_row", {}) or {}),
            combination_follow_on_execution_manifest_register=combination_follow_on_execution_manifest_register,
            discovery_candidate_review_register=list(licensed_research.get("discovery_candidate_review_register", []) or []),
            article_reference_register=list(licensed_research.get("article_reference_register", []) or []),
            research_campaign_trigger_register=research_campaign_trigger_register,
            knowledge_atom_register=list(licensed_research.get("knowledge_atom_register", []) or []),
            latent_combination_candidate_register=latent_combination_candidate_register,
            admissible_combination_review_register=admissible_combination_review_register,
            combination_review_queue_summary=dict(combination_review_sequence.get("summary", {}) or {}),
            source_coverage_summary=dict(licensed_research.get("source_coverage_summary", {}) or {}),
            source_family_coverage_register=list(licensed_research.get("source_family_coverage_register", []) or []),
            combination_search_gap_record=combination_search_gap_record,
            research_campaign_record=research_campaign_record,
            asset_context_vector=asset_context_vector,
            research_loop_control_record=research_loop_control_store,
            search_query_execution_register=list(licensed_research.get("search_query_execution_register", []) or []),
        )
        if build_research_loop_snapshot is not None
        else {
            "state": {},
            "jobs": [],
            "current_job": {},
            "metrics": {},
            "control": {},
            "stop_condition": {},
        }
    )
    if run_id and build_research_loop_snapshot is not None:
        previous_research_loop_state = dict(research_loop_state_store.get("state", {}) or {})
        previous_research_loop_current_job = dict(research_loop_state_store.get("current_job", {}) or {})
        research_loop_state_store = _persist_research_loop_state_record(
            run_id,
            dict(research_loop_snapshot.get("state", {}) or {}),
            dict(research_loop_snapshot.get("current_job", {}) or {}),
        )
        research_loop_job_store = _persist_research_loop_job_store(
            run_id,
            list(research_loop_snapshot.get("jobs", []) or []),
            dict(research_loop_snapshot.get("current_job", {}) or {}),
        )
        research_loop_metric_store = _persist_research_loop_metric_record(
            run_id,
            dict(research_loop_snapshot.get("metrics", {}) or {}),
            dict(research_loop_snapshot.get("depth_enforcement", {}) or {}),
            dict(research_loop_snapshot.get("stop_condition", {}) or {}),
        )
        event_rows = (
            build_research_loop_event_records(
                previous_state=previous_research_loop_state,
                previous_current_job=previous_research_loop_current_job,
                snapshot=research_loop_snapshot,
                event_timestamp=_utc_now_iso(),
            )
            if build_research_loop_event_records is not None
            else []
        )
        research_loop_event_store = _append_research_loop_events(run_id, event_rows)

    pattern_authority_state = str(motor_052_output.get("pattern_authority_state", "")).strip() or "legacy_primary_skill_shadow"
    pattern_authority_summary = dict(motor_052_output.get("pattern_authority_summary", {}) or {})
    authoritative_pattern_activation_register = list(
        motor_052_output.get(
            "authoritative_pattern_activation_register",
            registry_pattern_activation_register if pattern_authority_state == "skill_primary" else [],
        )
        or []
    )
    promotion_summary = {
        "reviewed_extractions": len(list(licensed_research.get("extraction_review_register", []) or [])),
        "approved_patterns": len(list(licensed_research.get("approved_pattern_promotion_register", []) or [])),
        "approved_combinations": len(
            list(licensed_research.get("approved_combination_promotion_register", []) or [])
        ),
    }
    decision_summary = (
        summarize_combination_decisions(review_register)
        if summarize_combination_decisions is not None
        else {"total": len(review_register), "by_decision": {}}
    )
    registry_counts = dict((registry_bundle or {}).get("counts", {}) or {})
    note = ""
    if not active_pattern_ids:
        note = "La skill está cargada, pero este run todavía no activa patrones que formen combinaciones registry-first."
    elif not review_register:
        note = "Hay patrones activos, pero ninguna combinación registry-first cumple todavía su conjunto mínimo."

    return {
        "available": True,
        "registry": registry_counts,
        "active_pattern_ids": active_pattern_ids,
        "active_pattern_sources": active_pattern_sources,
        "pattern_authority_state": pattern_authority_state,
        "pattern_authority_summary": pattern_authority_summary,
        "registry_pattern_activation_register": registry_pattern_activation_register,
        "authoritative_pattern_activation_register": authoritative_pattern_activation_register,
        "asset_context_vector": asset_context_vector,
        "context_differentiator_register": context_differentiator_register,
        "anti_trigger_signals": anti_trigger_signals,
        "combination_activation_register": activation_register,
        "combination_review_register": review_register,
        "latent_combination_candidate_register": latent_combination_candidate_register,
        "latent_combination_cluster_register": latent_combination_cluster_register,
        "admissible_combination_review_register": admissible_combination_review_register,
        "combination_review_sequence_register": list(combination_review_sequence.get("rows", []) or []),
        "current_combination_review_row": dict(combination_review_sequence.get("current_row", {}) or {}),
        "next_combination_review_rows": list(combination_review_sequence.get("next_rows", []) or []),
        "combination_review_queue_summary": dict(combination_review_sequence.get("summary", {}) or {}),
        "combination_follow_on_research_register": combination_follow_on_research_register,
        "combination_follow_on_execution_manifest_register": combination_follow_on_execution_manifest_register,
        "current_combination_follow_on_execution_manifest": next(
            (
                dict(row)
                for row in list(combination_follow_on_execution_manifest_register or [])
                if _text(row.get("combination_id")) == _text((combination_review_sequence.get("current_row", {}) or {}).get("combination_id"))
            ),
            {},
        ),
        "combination_search_gap_record": combination_search_gap_record,
        "research_campaign_record": research_campaign_record,
        "research_campaign_trigger_register": research_campaign_trigger_register,
        "research_loop_state": dict(research_loop_snapshot.get("state", {}) or {}),
        "research_loop_job_register": list(research_loop_snapshot.get("jobs", []) or []),
        "current_research_job": dict(research_loop_snapshot.get("current_job", {}) or {}),
        "research_loop_metrics": dict(research_loop_snapshot.get("metrics", {}) or {}),
        "research_loop_control_record": dict(research_loop_snapshot.get("control", {}) or {}),
        "research_depth_enforcement_record": dict(research_loop_snapshot.get("depth_enforcement", {}) or {}),
        "research_stop_condition_record": dict(research_loop_snapshot.get("stop_condition", {}) or {}),
        "search_result_capture_register": list(licensed_research.get("search_result_capture_register", []) or []),
        "current_search_result_capture_row": dict(licensed_research.get("current_search_result_capture_row", {}) or {}),
        "next_search_result_capture_rows": list(licensed_research.get("next_search_result_capture_rows", []) or []),
        "search_result_capture_summary": dict(licensed_research.get("search_result_capture_summary", {}) or {}),
        "search_query_execution_register": list(licensed_research.get("search_query_execution_register", []) or []),
        "current_search_query_execution_row": dict(licensed_research.get("current_search_query_execution_row", {}) or {}),
        "next_search_query_execution_rows": list(licensed_research.get("next_search_query_execution_rows", []) or []),
        "search_query_execution_summary": dict(licensed_research.get("search_query_execution_summary", {}) or {}),
        "search_query_result_option_review_register": list(licensed_research.get("search_query_result_option_review_register", []) or []),
        "current_search_query_result_option_row": dict(licensed_research.get("current_search_query_result_option_row", {}) or {}),
        "next_search_query_result_option_rows": list(licensed_research.get("next_search_query_result_option_rows", []) or []),
        "search_query_result_option_summary": dict(licensed_research.get("search_query_result_option_summary", {}) or {}),
        "search_query_result_option_batch_plan": dict(licensed_research.get("search_query_result_option_batch_plan", {}) or {}),
        "search_query_execution_batch_plan": dict(licensed_research.get("search_query_execution_batch_plan", {}) or {}),
        "search_query_execution_session_bundle": dict(licensed_research.get("search_query_execution_session_bundle", {}) or {}),
        "search_query_execution_manifest": dict(licensed_research.get("search_query_execution_manifest", {}) or {}),
        "search_query_execution_session_store": dict(licensed_research.get("search_query_execution_session_store", {}) or {}),
        "search_query_result_import_store": dict(licensed_research.get("search_query_result_import_store", {}) or {}),
        "reference_resolution_sequence_register": list(licensed_research.get("reference_resolution_sequence_register", []) or []),
        "current_reference_resolution_row": dict(licensed_research.get("current_reference_resolution_row", {}) or {}),
        "next_reference_resolution_rows": list(licensed_research.get("next_reference_resolution_rows", []) or []),
        "reference_resolution_queue_summary": dict(licensed_research.get("reference_resolution_queue_summary", {}) or {}),
        "reference_resolution_batch_plan": dict(licensed_research.get("reference_resolution_batch_plan", {}) or {}),
        "decision_summary": decision_summary,
        "licensed_research": licensed_research,
        "promotion_summary": promotion_summary,
        "decision_store": {
            "updated_at": str(decision_store.get("updated_at", "")).strip(),
            "path": str(decision_store.get("path", "")).strip(),
            "stored_decision_count": len(list(decision_store.get("decisions", []) or [])),
        },
        "combination_edit_store": {
            "updated_at": str(combination_edit_store.get("updated_at", "")).strip(),
            "path": str(combination_edit_store.get("path", "")).strip(),
            "stored_edit_count": len(list(combination_edit_store.get("edits", []) or [])),
        },
        "combination_review_control_store": {
            "updated_at": str(combination_review_control_store.get("updated_at", "")).strip(),
            "path": str(combination_review_control_store.get("path", "")).strip(),
            "deferred_count": len(list(combination_review_control_store.get("deferred_combination_ids", []) or [])),
            "batch_size": int(combination_review_control_store.get("batch_size", 1) or 1),
        },
        "latent_cluster_override_store": {
            "updated_at": str(latent_cluster_override_store.get("updated_at", "")).strip(),
            "path": str(latent_cluster_override_store.get("path", "")).strip(),
            "split_assignment_count": len(list(latent_cluster_override_store.get("split_assignments", []) or [])),
            "merge_assignment_count": len(list(latent_cluster_override_store.get("merge_assignments", []) or [])),
        },
        "research_campaign_trigger_store": {
            "updated_at": str(research_campaign_trigger_store.get("updated_at", "")).strip(),
            "path": str(research_campaign_trigger_store.get("path", "")).strip(),
            "stored_trigger_count": len(list(research_campaign_trigger_store.get("triggers", []) or [])),
        },
        "combination_follow_on_manifest_store": {
            "updated_at": str(combination_follow_on_manifest_store.get("updated_at", "")).strip(),
            "path": str(combination_follow_on_manifest_store.get("path", "")).strip(),
            "stored_manifest_count": len(list(combination_follow_on_manifest_store.get("manifests", []) or [])),
            "exists": bool(combination_follow_on_manifest_store.get("exists")),
        },
        "research_loop_state_store": {
            "updated_at": str(research_loop_state_store.get("updated_at", "")).strip(),
            "path": str(research_loop_state_store.get("path", "")).strip(),
            "exists": bool(research_loop_state_store.get("exists")),
        },
        "research_loop_job_store": {
            "updated_at": str(research_loop_job_store.get("updated_at", "")).strip(),
            "path": str(research_loop_job_store.get("path", "")).strip(),
            "stored_job_count": len(list(research_loop_job_store.get("jobs", []) or [])),
            "exists": bool(research_loop_job_store.get("exists")),
        },
        "research_loop_metric_store": {
            "updated_at": str(research_loop_metric_store.get("updated_at", "")).strip(),
            "path": str(research_loop_metric_store.get("path", "")).strip(),
            "depth_state": str(dict(research_loop_metric_store.get("depth_enforcement", {}) or {}).get("depth_state", "")).strip(),
            "exists": bool(research_loop_metric_store.get("exists")),
        },
        "research_loop_control_store": {
            "updated_at": str(research_loop_control_store.get("updated_at", "")).strip(),
            "path": str(research_loop_control_store.get("path", "")).strip(),
            "control_state": str(research_loop_control_store.get("control_state", "")).strip(),
            "requested_action": str(research_loop_control_store.get("requested_action", "")).strip(),
            "exists": bool(research_loop_control_store.get("exists")),
        },
        "research_loop_event_store": {
            "updated_at": str(research_loop_event_store.get("updated_at", "")).strip(),
            "path": str(research_loop_event_store.get("path", "")).strip(),
            "stored_event_count": len(list(research_loop_event_store.get("events", []) or [])),
            "exists": bool(research_loop_event_store.get("exists")),
        },
        "note": note,
    }


def _load_run(run_id: str) -> dict:
    path = _RUNS_DIR / f"{run_id}.json"
    if not path.exists():
        return {}
    if load_run_manifest is not None:
        return load_run_manifest(path)
    return _load_json(path)


def _runs_for_pipeline(pipeline_id: str) -> list[dict[str, Any]]:
    if not _RUNS_DIR.exists():
        return []
    matches: list[dict[str, Any]] = []
    for path in _RUNS_DIR.glob("*.json"):
        data = load_run_manifest(path) if load_run_manifest is not None else _load_json(path)
        if data.get("pipeline_id") == pipeline_id:
            data["_mtime"] = path.stat().st_mtime
            matches.append(data)
    matches.sort(key=lambda item: item.get("_mtime", 0.0), reverse=True)
    return matches


def _tail_text(path: Path, max_chars: int = 2000) -> str:
    try:
        text = path.read_text(encoding="utf-8", errors="replace")
    except Exception:
        return ""
    return text[-max_chars:]


def _canonicalize_report_type_trace(trace: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(trace or {})
    for key in (
        "early_report_type_gate",
        "maturity_refined_report_type",
        "final_published_report_type",
        "leading_primary_structural_output_mode",
        "default_structural_output_mode",
    ):
        if key in normalized:
            normalized[key] = canonicalize_output_mode(normalized.get(key, ""))
    normalized["secondary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("secondary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    normalized["blocked_secondary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("blocked_secondary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    normalized["eligible_primary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("eligible_primary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    normalized["non_promotable_primary_structural_output_modes"] = [
        canonicalize_output_mode(value)
        for value in list(normalized.get("non_promotable_primary_structural_output_modes", []) or [])
        if canonicalize_output_mode(value)
    ]
    return normalized


def _canonicalize_ingestion_payload(payload: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(payload or {})
    classification = dict(normalized.get("classification", {}) or {})
    if classification:
        classification["recommended_report_type_internal"] = classification.get(
            "recommended_report_type_internal",
            classification.get("recommended_report_type", ""),
        )
        classification["recommended_report_type"] = canonicalize_output_mode(
            classification.get("recommended_report_type", "")
        )
        classification["report_identity_state_internal"] = classification.get(
            "report_identity_state_internal",
            classification.get("report_identity_state", ""),
        )
        classification["report_identity_state"] = canonicalize_output_mode(
            classification.get("report_identity_state", "")
        )
        classification["report_type_trace"] = _canonicalize_report_type_trace(
            dict(classification.get("report_type_trace", {}) or {})
        )
        normalized["classification"] = classification
    return normalized


def _pipeline_alias_stem(pipeline_id: str) -> str:
    slug = (pipeline_id or "").strip().lower()
    if not slug:
        return ""
    parts = slug.split("-")
    if len(parts) >= 2 and len(parts[-1]) == 4 and parts[-1].isdigit():
        return "-".join(parts[:-1]).strip()
    return slug


def _matches_input_alias(path: Path, pipeline_id: str) -> bool:
    alias = _pipeline_alias_stem(pipeline_id)
    if not alias:
        return False
    stem = path.stem[:-7] if path.stem.endswith("_inputs") else path.stem
    if stem.lower() == alias:
        return True
    pipeline = _load_json(path)
    if not pipeline:
        return False
    target_definition = derive_target_definition(pipeline) if derive_target_definition is not None else {}
    candidates = {
        str(target_definition.get("target_id", "")).strip().lower(),
        str(target_definition.get("target_slug", "")).strip().lower(),
        str(target_definition.get("target_identifier", "")).strip().lower(),
        str(target_definition.get("target_name", "")).strip().lower(),
        str(pipeline.get("case_id", "")).strip().lower(),
    }
    return alias in {c for c in candidates if c}


def _resolve_inputs_file(pipeline_id: str, inputs_file: str) -> str:
    if inputs_file:
        candidate = Path(inputs_file)
        if candidate.exists():
            return str(candidate)
        relative = (_HERE / inputs_file).resolve()
        if relative.exists():
            return str(relative)
    slug = (pipeline_id or "").strip().lower()
    candidates: list[Path] = []
    if slug:
        candidates.append(_HERE / "inputs" / f"{slug}_inputs.json")
        prefix = slug.split("-", 1)[0].strip()
        if prefix and prefix != slug:
            candidates.append(_HERE / "inputs" / f"{prefix}_inputs.json")
    for guessed in candidates:
        if guessed.exists():
            return str(guessed)
    inputs_dir = _HERE / "inputs"
    if inputs_dir.exists():
        for path in sorted(inputs_dir.glob("*_inputs.json")):
            if _matches_input_alias(path, pipeline_id):
                return str(path)
    return inputs_file


def _load_inputs_for_run(run_d: dict[str, Any]) -> dict[str, Any]:
    pipeline_id = str(run_d.get("pipeline_id", "")).strip()
    candidate = _resolve_inputs_file(pipeline_id, "")
    if candidate and Path(candidate).exists():
        return _load_json(Path(candidate))
    return {}


def _artifact_path_for_motor_result(motor_id: str, motor_result: dict[str, Any]) -> Path | None:
    cached_from = motor_result.get("cached_from", "")
    if cached_from:
        p = Path(cached_from)
        return p if p.exists() else None
    inputs_hash = motor_result.get("inputs_hash", "")
    if inputs_hash:
        p = _STORE_DIR / motor_id / f"{inputs_hash}.json"
        return p if p.exists() else None
    return None


def _motor_contract_map() -> dict[str, dict[str, Any]]:
    data = _load_json(_MOTOR_CONTRACT)
    motors = data.get("motors", {})
    return motors if isinstance(motors, dict) else {}


def _motor_contract_list() -> list[tuple[str, dict[str, Any]]]:
    motors = _motor_contract_map()
    return [(mid, motors[mid]) for mid in sorted(motors)]


if not _CONTRACT_ADAPTERS:
    _CONTRACT_ADAPTERS = _contract_adapter_map()


def _load_motor_output(run_d: dict, motor_id: str) -> dict:
    motor = run_d.get("motor_results", {}).get(motor_id, {})
    artifact_path = _artifact_path_for_motor_result(motor_id, motor)
    if artifact_path is None:
        return {}
    art = _load_json(artifact_path)
    return art.get("output", art)


def _expected_motor_count() -> int:
    contract = _motor_contract_list()
    return len(contract) if contract else 34


def _is_full_framework_run(run_d: dict[str, Any]) -> bool:
    if not run_d:
        return False
    if "motor_results" in run_d:
        return len(run_d.get("motor_results", {})) >= _expected_motor_count()
    counts = run_d.get("motor_counts", {})
    return int(counts.get("total", 0)) >= _expected_motor_count()


def _display_status(status: str, *, pdf_available: bool) -> str:
    if status == "not_started":
        return "not_started"
    if status == "completed_with_stubs":
        return "completed_partial"
    if status == "partial":
        return "partial"
    if status == "completed" and not pdf_available:
        return "completed_no_pdf"
    return status


def _duration(run_d: dict) -> float | None:
    try:
        s = datetime.fromisoformat(run_d["started_at"].replace("Z", "+00:00"))
        e = datetime.fromisoformat(run_d["completed_at"].replace("Z", "+00:00"))
        return round((e - s).total_seconds(), 1)
    except Exception:
        return None


def _case_title_from_run(run_d: dict) -> str:
    fp = _load_motor_output(run_d, "motor_012").get("facility_prior", {})
    t = fp.get("case_title") or fp.get("case_id")
    if t:
        return t
    return run_d.get("pipeline_id", "")


def _company_info(run_d: dict) -> dict:
    """Lee owner / issuer context desde motor_028."""
    out = _load_motor_output(run_d, "motor_028")
    if not out:
        return {}
    ed  = out.get("enriched_data", {})
    return {
        "name":     ed.get("company_name", ""),
        "ticker":   ed.get("ticker", ""),
        "sic":      ed.get("sic_description", ""),
        "state":    ed.get("state_of_incorporation", ""),
        "gaps":     out.get("coverage_gaps", []),
        "status":   out.get("discovery_status", ""),
    }


def _target_code(subject_kind: str = "", target_type: str = "", pipeline_id: str = "") -> str:
    kind = str(subject_kind or "").strip().lower()
    if kind == "address_candidate":
        return "ADDR"
    if kind == "site_candidate":
        return "SITE"
    if kind == "asset_candidate":
        return "ASET"
    if kind == "asset":
        return "ASST"
    if kind == "issuer":
        return "ISSR"
    typ = str(target_type or "").strip().lower()
    if typ:
        words = [w for w in typ.replace("-", " ").split() if w]
        if len(words) >= 2:
            code = "".join(word[0] for word in words[:4]).upper()
            if len(code) >= 3:
                return code[:4]
        compact = "".join(ch for ch in typ if ch.isalpha()).upper()
        if compact:
            return compact[:4]
    if pipeline_id:
        return pipeline_id.split("-", 1)[0][:4].upper()
    return "TGT"


def _fallback_target_from_pipeline(pipeline: dict[str, Any], *, pipeline_id: str = "", inputs_file: str = "") -> dict[str, Any]:
    target_definition = derive_target_definition(pipeline) if derive_target_definition is not None else (pipeline.get("target_definition_contract", {}) if isinstance(pipeline.get("target_definition_contract", {}), dict) else {})
    subject_definition = derive_subject_definition(pipeline) if derive_subject_definition is not None else (pipeline.get("subject_definition_contract", {}) if isinstance(pipeline.get("subject_definition_contract", {}), dict) else {})
    target_label = (
        target_definition.get("address_raw")
        or subject_definition.get("declared_asset_name")
        or target_definition.get("target_name")
        or pipeline.get("case_title")
        or pipeline_id
        or "Unnamed target"
    )
    owner_name = (
        target_definition.get("owner_entity")
        or subject_definition.get("owner_context_optional")
        or ""
    )
    target_type = target_definition.get("target_type", "")
    target_id = target_definition.get("target_id", "")
    target_slug = target_definition.get("target_slug", "")
    subject_kind = subject_definition.get("subject_kind", "")
    return {
        "label": str(target_label).strip(),
        "address": str(target_definition.get("address_raw", "")).strip(),
        "target_type": str(target_type).strip(),
        "target_id": str(target_id).strip(),
        "target_slug": str(target_slug).strip(),
        "subject_kind": str(subject_kind).strip(),
        "owner_name": str(owner_name).strip(),
        "ticker": str((pipeline.get("facility_inputs", {}) or {}).get("input_03_sector", {}).get("owner_ticker", "")).strip() if isinstance((pipeline.get("facility_inputs", {}) or {}).get("input_03_sector", {}), dict) else "",
        "target_code": _target_code(subject_kind, target_type, pipeline_id),
        "pipeline_id": pipeline_id,
        "inputs_file": inputs_file,
    }


def _target_info(run_d: dict) -> dict:
    pipeline = _load_inputs_for_run(run_d)
    runtime_target = run_d.get("target_definition", {}) or {}
    runtime_subject = run_d.get("subject_definition", {}) or {}
    fallback = _fallback_target_from_pipeline(
        pipeline,
        pipeline_id=run_d.get("pipeline_id", ""),
        inputs_file=_resolve_inputs_file(run_d.get("pipeline_id", ""), ""),
    )
    if not runtime_target and not runtime_subject:
        return fallback
    label = (
        runtime_target.get("address_raw")
        or runtime_subject.get("declared_asset_name")
        or runtime_target.get("target_name")
        or fallback.get("label")
        or run_d.get("pipeline_id", "")
    )
    owner_name = (
        runtime_target.get("owner_entity")
        or runtime_subject.get("owner_context_optional")
        or fallback.get("owner_name", "")
    )
    return {
        "label": str(label).strip(),
        "address": str(runtime_target.get("address_raw", "") or fallback.get("address", "")).strip(),
        "target_type": str(runtime_target.get("target_type", "") or fallback.get("target_type", "")).strip(),
        "target_id": str(runtime_target.get("target_id", "") or fallback.get("target_id", "")).strip(),
        "target_slug": str(runtime_target.get("target_slug", "") or fallback.get("target_slug", "")).strip(),
        "subject_kind": str(runtime_subject.get("subject_kind", "") or runtime_target.get("subject_kind", "") or fallback.get("subject_kind", "")).strip(),
        "owner_name": str(owner_name).strip(),
        "ticker": str(fallback.get("ticker", "")).strip(),
        "target_code": str(fallback.get("target_code", "")).strip() or _target_code(
            runtime_subject.get("subject_kind", "") or runtime_target.get("subject_kind", ""),
            runtime_target.get("target_type", "") or fallback.get("target_type", ""),
            run_d.get("pipeline_id", ""),
        ),
        "pipeline_id": run_d.get("pipeline_id", ""),
        "inputs_file": fallback.get("inputs_file", ""),
    }


def _target_seed_records() -> list[dict[str, Any]]:
    inputs_dir = _HERE / "inputs"
    if not inputs_dir.exists():
        return []
    records: list[dict[str, Any]] = []
    for path in sorted(inputs_dir.glob("*_inputs.json")):
        pipeline = _load_json(path)
        stem = path.stem[:-7] if path.stem.endswith("_inputs") else path.stem
        target = _fallback_target_from_pipeline(
            pipeline,
            pipeline_id=f"{stem}-{datetime.now().year}",
            inputs_file=str(path),
        )
        target_id = str(target.get("target_id", "")).strip() or stem
        pipeline_id = f"{target_id}-{datetime.now().year}"
        legacy_pipeline_id = f"{stem}-{datetime.now().year}"
        pipeline_aliases = []
        if legacy_pipeline_id != pipeline_id:
            pipeline_aliases.append(legacy_pipeline_id)
        subject_kind = target.get("subject_kind", "")
        owner_name = target.get("owner_name", "")
        context_parts = [p for p in [target.get("target_type", ""), subject_kind, owner_name] if p]
        records.append({
            "pipeline_id": pipeline_id,
            "pipeline_aliases": pipeline_aliases,
            "inputs_file": str(path),
            "has_inputs": True,
            "target_label": target.get("label", stem),
            "target_address": target.get("address", ""),
            "target_type": target.get("target_type", ""),
            "target_id": target_id,
            "target_slug": target.get("target_slug", ""),
            "subject_kind": subject_kind,
            "owner_name": owner_name,
            "ticker": target.get("ticker", stem.upper()),
            "target_code": target.get("target_code", _target_code(subject_kind, target.get("target_type", ""), pipeline_id)),
            "context_line": " · ".join(context_parts),
        })
    return records


def _target_seed_lookup(pipeline_id: str) -> dict[str, Any]:
    if not pipeline_id:
        return {}
    for seed in _target_seed_records():
        aliases = [seed.get("pipeline_id", ""), *seed.get("pipeline_aliases", [])]
        if pipeline_id in aliases:
            return seed
    return {}


def _target_from_seed_record(seed: dict[str, Any]) -> dict[str, Any]:
    if not seed:
        return {}
    return {
        "label": str(seed.get("target_label") or seed.get("name") or seed.get("pipeline_id") or "Unnamed target").strip(),
        "address": str(seed.get("target_address", "")).strip(),
        "target_type": str(seed.get("target_type", "")).strip(),
        "target_id": str(seed.get("target_id", "")).strip(),
        "target_slug": str(seed.get("target_slug", "")).strip(),
        "subject_kind": str(seed.get("subject_kind", "")).strip(),
        "owner_name": str(seed.get("owner_name", "")).strip(),
        "ticker": str(seed.get("ticker", "")).strip(),
        "target_code": str(seed.get("target_code", "")).strip(),
        "pipeline_id": str(seed.get("pipeline_id", "")).strip(),
        "inputs_file": str(seed.get("inputs_file", "")).strip(),
    }


def _focus_activity(run_d: dict, motors: list[dict[str, Any]]) -> list[dict]:
    motor_map = {m["motor_id"]: m for m in motors}
    result = []
    for mid, label in _FOCUS_MOTORS.items():
        m       = motor_map.get(mid, {})
        status  = m.get("status", "pending")
        snippet = ""
        # Intentar extraer un snippet del bloque narrativo
        if status in ("completed", "cached"):
            out = _load_motor_output(run_d, mid)
            blocks = out.get("output_blocks", [])
            if blocks and isinstance(blocks[0], dict):
                paras = blocks[0].get("content_paragraphs", [])
                if paras:
                    snippet = paras[0][:180]
        result.append({
            "motor_id":    mid,
            "label":       label,
            "status":      status,
            "duration_ms": m.get("duration_ms"),
            "snippet":     snippet,
            "error":       m.get("error"),
            "name":        m.get("motor_name", ""),
        })
    return result


def _source_contract() -> list[dict[str, Any]]:
    primary = PRIMARY_SOURCE_CONTRACT or _PRIMARY_FALLBACK_CONTRACT
    contract: list[dict[str, Any]] = []
    for spec in primary:
        contract.append({
            "source_type": spec.get("source_type", ""),
            "locator_tpl": spec.get("locator_tpl", ""),
            "discovery_reason": spec.get("discovery_reason", ""),
            "attempt_kind": spec.get("attempt_kind", "primary"),
            "source_scope": _source_scope(spec.get("source_type", "")),
        })
    for spec in _EXTENDED_SOURCE_REGISTRY:
        contract.append({
            "source_type": spec.get("source_type", ""),
            "locator_tpl": spec.get("locator_tpl", ""),
            "discovery_reason": spec.get("discovery_reason", ""),
            "attempt_kind": "extended",
            "source_scope": _source_scope(spec.get("source_type", "")),
        })
    return contract


def _source_label(source_type: str) -> str:
    labels = {
        "census_geocoder_validation": "Census geocoder validation",
        "ashrae_climate_zone_lookup": "ASHRAE climate zone lookup",
        "asset_energy_behavior_reference": "Asset energy behavior reference",
        "city_benchmarking_boston": "Boston building benchmarking reference",
        "sec_edgar_submissions": "SEC EDGAR submissions",
        "sec_edgar_xbrl_facts": "SEC EDGAR XBRL facts",
        "nyc_open_data_property": "NYC DOF property assessment",
        "nyc_ll84_energy_benchmarking": "NYC LL84 benchmarking",
        "nyc_pluto_property": "NYC PLUTO property",
        "nyc_dob_permits": "NYC DOB permits",
        "nyc_acris_mortgage_records": "NYC ACRIS mortgage records",
        "sec_edgar_efts_fulltext": "SEC EDGAR full-text search",
        "sec_edgar_8k_events": "SEC EDGAR 8-K events",
        "sec_10k_full_text_extraction": "SEC 10-K full-text extraction",
        "esrt_ir_html_scrape": "Issuer-specific IR page (ESRT only)",
        "esrt_10k_html_extraction": "Issuer-specific 10-K extraction (ESRT only)",
        "eia_commercial_electricity_rates": "EIA electricity rates",
        "epa_energy_star_benchmarks": "EPA Energy Star benchmarks",
    }
    if source_type in labels:
        return labels[source_type]
    return source_type.replace("_", " ")


def _source_family(source_type: str) -> str:
    if source_type.startswith("sec_") or source_type.startswith("esrt_"):
        return "issuer_context"
    if source_type.startswith("census_") or source_type.startswith("parcel_"):
        return "asset_identity"
    if source_type.startswith("ashrae_") or source_type.startswith("noaa_"):
        return "climate_context"
    if source_type.startswith("city_benchmarking_") or source_type.startswith("asset_energy_behavior_"):
        return "asset_energy_context"
    if source_type.startswith("nyc_") or source_type.startswith("city_"):
        return "city_property"
    if source_type.startswith("epa_") or source_type.startswith("eia_") or source_type.startswith("noaa_"):
        return "energy_environment"
    if source_type.startswith("web_search_"):
        return "web_search"
    if source_type.startswith("census_") or source_type.startswith("bls_") or source_type.startswith("fred_"):
        return "economic_context"
    return "other"


def _source_scope(source_type: str) -> str:
    if source_type.startswith("esrt_"):
        return "issuer_specific"
    if source_type.startswith("census_") or source_type.startswith("parcel_"):
        return "asset_identity_level"
    if source_type.startswith("ashrae_") or source_type.startswith("noaa_"):
        return "asset_environment_level"
    if source_type.startswith("asset_energy_behavior_") or source_type.startswith("city_benchmarking_"):
        return "asset_benchmark_level"
    if source_type.startswith("nyc_"):
        return "asset_jurisdiction_specific"
    if source_type.startswith("sec_"):
        return "entity_level"
    if source_type.startswith("web_search_"):
        return "market_signal"
    if source_type.startswith(("eia_", "epa_", "noaa_")):
        return "energy_environment_context"
    if source_type.startswith(("census_", "bls_", "fred_", "fhfa_", "hud_")):
        return "macro_context"
    return "extended_context"


def _gap_to_source_type(gap: dict[str, Any]) -> str:
    mapping = {
        "company_submissions": "sec_edgar_submissions",
        "financial_metrics": "sec_edgar_xbrl_facts",
        "property_assessment": "nyc_open_data_property",
    }
    return mapping.get(gap.get("gap_type", ""), gap.get("gap_type", ""))


def _fallback_source_activity(m28_out: dict) -> dict[str, Any]:
    contract = _source_contract()
    attempts: dict[str, dict[str, Any]] = {
        item["source_type"]: {
            "source_type": item["source_type"],
            "label": _source_label(item["source_type"]),
            "locator": item.get("locator_tpl", ""),
            "status": "untracked",
            "attempt_kind": item.get("attempt_kind", ""),
            "source_scope": item.get("source_scope", _source_scope(item["source_type"])),
            "family": _source_family(item["source_type"]),
            "discovery_reason": item.get("discovery_reason", ""),
            "detail": "Este run no registró el intento por fuente; solo dejó éxitos / errores parciales.",
            "matched_terms": [],
            "error": "",
        }
        for item in contract
        if item.get("source_type")
    }
    for candidate in m28_out.get("discovery_candidates", []):
        source_type = candidate.get("source_type", "")
        if not source_type:
            continue
        attempts[source_type] = {
            "source_type": source_type,
            "label": _source_label(source_type),
            "locator": candidate.get("locator", ""),
            "status": "found",
            "attempt_kind": attempts.get(source_type, {}).get("attempt_kind", ""),
            "source_scope": attempts.get(source_type, {}).get("source_scope", _source_scope(source_type)),
            "family": _source_family(source_type),
            "discovery_reason": candidate.get("discovery_reason", ""),
            "detail": "",
            "matched_terms": candidate.get("matched_terms", []),
            "error": "",
        }
    primary_rejections = {
        "src_001": "sec_edgar_submissions",
        "src_002": "sec_edgar_xbrl_facts",
        "src_003": "nyc_open_data_property",
        "src_003_nyc_property": "nyc_open_data_property",
    }
    for rejection in m28_out.get("discovery_rejections", []):
        source_type = primary_rejections.get(rejection.get("source_id", ""), "")
        if not source_type:
            continue
        attempts[source_type] = {
            "source_type": source_type,
            "label": _source_label(source_type),
            "locator": rejection.get("locator", ""),
            "status": "failed",
            "attempt_kind": attempts.get(source_type, {}).get("attempt_kind", "primary"),
            "source_scope": attempts.get(source_type, {}).get("source_scope", _source_scope(source_type)),
            "family": _source_family(source_type),
            "discovery_reason": attempts.get(source_type, {}).get("discovery_reason", ""),
            "detail": "",
            "matched_terms": [],
            "error": rejection.get("reason_detail", ""),
        }
    for gap in m28_out.get("coverage_gaps", []):
        source_type = _gap_to_source_type(gap)
        if not source_type or source_type not in attempts:
            continue
        if attempts[source_type]["status"] == "untracked":
            attempts[source_type]["status"] = "failed"
            attempts[source_type]["error"] = gap.get("detail", "") or ", ".join(gap.get("scope_terms", []))
    ordered = sorted(attempts.values(), key=lambda item: (item["status"] != "found", item["label"]))
    summary = {
        "contract_total": len(contract),
        "applicable_contract_total": len(contract),
        "attempted": len([a for a in ordered if a["status"] != "untracked"]),
        "applicable_attempted": len([a for a in ordered if a["status"] in ("found", "no_data", "failed")]),
        "found": len([a for a in ordered if a["status"] == "found"]),
        "admitted": len(m28_out.get("discovery_candidates", [])),
        "no_data": len([a for a in ordered if a["status"] == "no_data"]),
        "failed": len([a for a in ordered if a["status"] == "failed"]),
        "context_missing": 0,
        "not_applicable": 0,
        "untracked": len([a for a in ordered if a["status"] == "untracked"]),
        "tracking_complete": False,
        "applicable_tracking_complete": False,
        "candidates": len(m28_out.get("discovery_candidates", [])),
        "rejections": len(m28_out.get("discovery_rejections", [])),
        "coverage_gaps": len(m28_out.get("coverage_gaps", [])),
    }
    return {
        "summary": summary,
        "attempts": ordered,
        "note": "Este artifact no registró intentos por fuente. El dashboard expone el contrato de fuentes y marca qué quedó realmente trazado.",
    }


def _research_activity(run_d: dict) -> dict[str, Any]:
    out = _load_motor_output(run_d, "motor_028")
    if not out:
        return {"summary": {}, "attempts": [], "note": "motor_028 no dejó artifact para este run."}
    attempts = out.get("discovery_attempts", [])
    if attempts:
        normalized = []
        for attempt in attempts:
            source_type = attempt.get("source_type", "")
            normalized.append({
                **attempt,
                "label": _source_label(source_type),
                "family": _source_family(source_type),
                "source_scope": attempt.get("source_scope", _source_scope(source_type)),
            })
        summary = out.get("discovery_summary", {}).copy()
        summary.setdefault("contract_total", len(_source_contract()))
        summary.setdefault("applicable_contract_total", summary.get("contract_total", 0) - summary.get("not_applicable", 0))
        summary.setdefault("untracked", max(summary.get("contract_total", 0) - summary.get("attempted", 0), 0))
        summary.setdefault("applicable_attempted", summary.get("found", 0) + summary.get("no_data", 0) + summary.get("failed", 0) + summary.get("context_missing", 0))
        summary.setdefault("admitted", summary.get("candidates", 0))
        summary.setdefault("context_missing", 0)
        summary.setdefault("not_applicable", 0)
        summary.setdefault("applicable_tracking_complete", summary.get("applicable_attempted", 0) == summary.get("applicable_contract_total", 0))
        return {
            "summary": summary,
            "attempts": sorted(normalized, key=lambda item: (item.get("status") != "found", item.get("label", ""))),
            "note": "",
        }
    return _fallback_source_activity(out)


def _ingestion_activity(run_d: dict) -> dict[str, Any]:
    m28 = _load_motor_output(run_d, "motor_028")
    m12 = _load_motor_output(run_d, "motor_012")
    m14 = _load_motor_output(run_d, "motor_014")
    m35 = _load_motor_output(run_d, "motor_035")
    if not m28 and not m12 and not m14 and not m35:
        return {
            "available": False,
            "classification": {},
            "summary": {},
            "blocking_fields": [],
            "missing_evidence": [],
        }

    source_register = list((m28 or {}).get("source_register", []) or [])
    asset_field_register = list((m12 or {}).get("asset_field_register", []) or [])
    missing_evidence_register = list((m14 or {}).get("missing_evidence_register", []) or (m12 or {}).get("missing_evidence_register", []) or [])
    accepted_count = len([row for row in source_register if row.get("accepted")])
    rejected_count = len([row for row in source_register if not row.get("accepted")])
    scope_counts: dict[str, int] = {}
    for row in source_register:
        scope = str(row.get("scope", "")).strip() or "UNKNOWN_SCOPE"
        scope_counts[scope] = scope_counts.get(scope, 0) + 1
    blocking_fields = [
        {
            "field": row.get("field", ""),
            "admissibility": row.get("admissibility", ""),
            "scope": row.get("scope", ""),
            "notes": row.get("notes", ""),
        }
        for row in asset_field_register
        if row.get("status") == "BLOCKING_FIELD"
    ]
    classification = {
        "target_type": run_d.get("target_type_classification", ""),
        "classification_confidence": run_d.get("classification_confidence", ""),
        "asset_identity_status": run_d.get("asset_identity_status", ""),
        "target_admissibility_state": run_d.get("target_admissibility_state", ""),
        "technical_substrate_readiness": run_d.get("technical_substrate_readiness", ""),
        "recommended_report_type_internal": run_d.get("recommended_report_type", ""),
        "recommended_report_type": run_d.get("recommended_report_type", ""),
        "report_identity_state_internal": run_d.get("report_identity_state", ""),
        "report_identity_state": run_d.get("report_identity_state", ""),
        "report_type_trace": dict(run_d.get("report_type_trace", {}) or {}),
        "phase_self_evaluation_summary": dict(run_d.get("phase_self_evaluation_summary", {}) or {}),
        "ingestion_contract_status": run_d.get("ingestion_contract_status", ""),
        "subject_gate_passed": bool(run_d.get("subject_gate_passed", False)),
    }
    ingestion_learning_summary = dict(run_d.get("ingestion_learning_summary", {}) or {})
    case_delta_summary = dict(run_d.get("case_delta_summary", {}) or {})
    source_yield_memory_summary = dict(run_d.get("source_yield_memory_summary", {}) or {})
    next_ingestion_priority_update = dict(run_d.get("next_ingestion_priority_update", {}) or {})
    routing_plan = dict((m35 or {}).get("source_routing_plan", {}) or (m28 or {}).get("source_routing_plan", {}) or {})
    routing_plan_compliance = dict((m28 or {}).get("routing_plan_compliance", {}) or {})
    jurisdiction_resolution = dict((m35 or {}).get("jurisdiction_resolution", {}) or {})
    critical_field_contract = list((m35 or {}).get("critical_field_contract", []) or [])
    return {
        "available": True,
        "classification": classification,
        "summary": {
            "sources_total": len(source_register),
            "sources_accepted": accepted_count,
            "sources_rejected": rejected_count,
            "asset_fields_total": len(asset_field_register),
            "blocking_fields_total": len(blocking_fields),
            "missing_evidence_total": len(missing_evidence_register),
            "scope_counts": scope_counts,
        },
        "learning": {
            "summary": ingestion_learning_summary,
            "case_delta_summary": case_delta_summary,
            "source_yield_memory_summary": source_yield_memory_summary,
            "next_ingestion_priority_update": next_ingestion_priority_update,
        },
        "jurisdiction_resolution": jurisdiction_resolution,
        "routing_plan": {
            "mandatory_sources": list(routing_plan.get("mandatory_sources", []) or []),
            "high_priority_sources": list(routing_plan.get("high_priority_sources", []) or []),
            "optional_sources": list(routing_plan.get("optional_sources", []) or []),
            "disallowed_substitutions": list(routing_plan.get("disallowed_substitutions", []) or []),
            "routing_notes": list(routing_plan.get("routing_notes", []) or []),
        },
        "routing_plan_compliance": routing_plan_compliance,
        "critical_field_contract": critical_field_contract[:12],
        "blocking_fields": blocking_fields[:8],
        "missing_evidence": [
            {
                "missing_field": row.get("missing_field", ""),
                "minimum_evidence_needed": row.get("minimum_evidence_needed", ""),
                "suggested_source": row.get("suggested_source", ""),
            }
            for row in missing_evidence_register[:8]
        ],
    }


def _chart_activity(run_d: dict) -> dict[str, Any]:
    motor = run_d.get("motor_results", {}).get("motor_018", {})
    out = _load_motor_output(run_d, "motor_018")
    if not motor:
        return {"status": "missing", "total_charts": 0, "assets": [], "errors": []}
    assets = out.get("chart_assets", []) if out else []
    errors = out.get("chart_errors", []) if out else []
    return {
        "status": motor.get("status", "missing"),
        "adapter_class": motor.get("adapter_class", ""),
        "total_charts": out.get("total_charts", len(assets)) if out else 0,
        "assets": [
            {
                "asset_id": asset.get("asset_id", ""),
                "title": asset.get("title", asset.get("asset_id", "")),
                "description": asset.get("description", ""),
                "section_hint": asset.get("section_hint", ""),
            }
            for asset in assets
        ],
        "errors": errors,
    }


def _all_runs() -> list[dict]:
    if not _RUNS_DIR.exists():
        return []
    runs = []
    # Ordenar por fecha de modificación real (más reciente primero)
    for p in sorted(_RUNS_DIR.glob("*.json"), key=lambda x: x.stat().st_mtime, reverse=True)[:50]:
        d  = load_run_manifest(p) if load_run_manifest is not None else _load_json(p)
        mr = d.get("motor_results", {})
        runs.append({
            "run_id":      d.get("run_id", p.stem),
            "pipeline_id": d.get("pipeline_id", ""),
            "status":      d.get("status", "unknown"),
            "started_at":  d.get("started_at", ""),
            "completed_at": d.get("completed_at", ""),
            "duration_s":  _duration(d),
            "case_title":  _case_title_from_run(d),
            "mtime":       p.stat().st_mtime,
            "motor_counts": {
                "total":     len(mr),
                "completed": sum(1 for v in mr.values() if v.get("status") == "completed"),
                "cached":    sum(1 for v in mr.values() if v.get("status") == "cached"),
                "stub":      sum(1 for v in mr.values() if v.get("status") == "stub"),
                "failed":    sum(1 for v in mr.values() if v.get("status") == "failed"),
                "running":   sum(1 for v in mr.values() if v.get("status") == "running"),
            },
            "is_full_framework_run": len(mr) >= _expected_motor_count(),
        })
    return runs


def _select_active_run(
    runs: list[dict[str, Any]],
    *,
    requested_run_id: str = "",
    requested_pipeline_id: str = "",
) -> dict[str, Any] | None:
    if requested_run_id:
        exact = next((r for r in runs if r["run_id"] == requested_run_id), None)
        if exact is not None:
            return exact
    full_runs = [r for r in runs if r.get("is_full_framework_run")]
    if requested_pipeline_id:
        pipeline_runs = [r for r in full_runs if r.get("pipeline_id") == requested_pipeline_id]
        if not pipeline_runs:
            return None
        running = next((r for r in pipeline_runs if r.get("status") == "running"), None)
        return running or pipeline_runs[0]
    running = next((r for r in full_runs if r["status"] == "running"), None)
    full = next((r for r in full_runs if r["motor_counts"]["total"] >= 30), None)
    return running or full or (runs[0] if runs else None)


def _legacy_truth_state(motor_result: dict[str, Any], is_placeholder_contract: bool) -> str:
    raw_status = motor_result.get("status", "missing")
    if raw_status == "cached":
        if motor_result.get("output_state") == "stub" or is_placeholder_contract:
            return "cached_stub"
        return "cached_real"
    if raw_status == "completed":
        if is_placeholder_contract or motor_result.get("output_state") == "stub":
            return "completed_stub"
        return "completed_real"
    return raw_status


def _run_detail(run_id: str) -> dict:
    d = _load_run(run_id)
    if not d:
        return {}
    mr = d.get("motor_results", {})
    motors = []
    status_counts = {
        "pending": 0,
        "completed": 0,
        "cached": 0,
        "stub": 0,
        "cached_stub": 0,
        "completed_stub": 0,
        "failed": 0,
        "running": 0,
        "skipped": 0,
        "missing": 0,
        "pending_real": 0,
        "completed_real": 0,
        "cached_real": 0,
        "failed_real": 0,
        "running_real": 0,
        "missing_real": 0,
    }
    placeholder_contract = 0
    implemented_contract = 0
    for mid, spec in _motor_contract_list():
        r = mr.get(mid, {})
        contract_adapter = _CONTRACT_ADAPTERS.get(mid, "")
        is_placeholder_contract = contract_adapter == "StubMotorAdapter"
        raw_status = r.get("status", "missing")
        truth_state = r.get("truth_state") or _legacy_truth_state(r, is_placeholder_contract)
        status = truth_state or raw_status
        if is_placeholder_contract:
            placeholder_contract += 1
        else:
            implemented_contract += 1
        if status not in status_counts:
            status_counts["missing"] += 1
        else:
            status_counts[status] += 1
        if not is_placeholder_contract:
            if status in ("running", "failed", "pending", "missing"):
                real_key = f"{status}_real"
                if real_key in status_counts:
                    status_counts[real_key] += 1
                else:
                    status_counts["missing_real"] += 1
        motors.append({
            "motor_id": mid,
            "motor_name": spec.get("name", ""),
            "status": status,
            "raw_status": raw_status,
            "truth_state": truth_state,
            "duration_ms": r.get("duration_ms"),
            "adapter_class": r.get("adapter_class", ""),
            "contract_adapter_class": contract_adapter,
            "implementation_state": r.get("implementation_state") or ("placeholder" if is_placeholder_contract else "implemented"),
            "output_state": r.get("output_state", ""),
            "error": r.get("error"),
            "cached_from": str(_artifact_path_for_motor_result(mid, r) or ""),
            "is_stub": r.get("adapter_class", "") == "StubMotorAdapter" or is_placeholder_contract,
            "is_placeholder_contract": is_placeholder_contract,
        })
    return {
        "run_id":       d.get("run_id"),
        "pipeline_id":  d.get("pipeline_id"),
        "status":       d.get("status"),
        "started_at":   d.get("started_at"),
        "completed_at": d.get("completed_at"),
        "duration_s":   _duration(d),
        "case_title":   _case_title_from_run(d),
        "error":        d.get("error"),
        "motors":       motors,
        "summary":      d.get("summary", {}),
        "motor_overview": {
            **status_counts,
            "total_expected": len(motors),
            "implemented_contract": implemented_contract,
            "placeholder_contract": placeholder_contract,
        },
    }


def _audit_failures(run_id: str) -> dict:
    d = _load_run(run_id)
    if not d:
        return {"available": False, "failures": []}
    mr = d.get("motor_results", {})
    m24 = mr.get("motor_024", {})
    out = _load_motor_output(d, "motor_024")
    if not m24 or not out:
        # Fallback: motores con status failed
        failed = [
            {"type": "Motor fallido", "motor": mid, "message": r.get("error", ""), "severity": "error"}
            for mid, r in mr.items() if r.get("status") == "failed"
        ]
        return {"available": bool(failed), "failures": failed}
    if out.get("__stub__"):
        return {"available": False, "failures": []}
    failures = []
    for exc in out.get("exception_register", []):
        failures.append({
            "type":     exc.get("event_type", "Error"),
            "motor":    exc.get("motor_id", ""),
            "message":  exc.get("description", exc.get("outcome", "")),
            "severity": exc.get("severity", "error"),
        })
    for ev in out.get("governance_event_log", []):
        if ev.get("severity") in ("error", "critical"):
            failures.append({
                "type":     ev.get("event_type", "Error"),
                "motor":    ev.get("motor_id", ""),
                "message":  ev.get("description", ""),
                "severity": ev.get("severity"),
            })
    health = out.get("pipeline_health_summary", {})
    return {
        "available": True,
        "failures":  failures,
        "health":    health,
    }


def _latest_pdf() -> dict | None:
    search = [_OUTPUT_DIR, Path.home() / "ZLab_Reports"]
    pdfs   = []
    for base in search:
        if not base.exists():
            continue
        for p in base.rglob("*.pdf"):
            try:
                pdfs.append((p.stat().st_mtime, p))
            except Exception:
                pass
    if not pdfs:
        return None
    _, p = max(pdfs)
    stat = p.stat()
    return {
        "path":     str(p),
        "name":     p.name,
        "size_kb":  round(stat.st_size / 1024, 1),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "mtime":    stat.st_mtime,
    }


def _pdf_metadata(path_str: str) -> dict | None:
    if not path_str:
        return None
    p = Path(path_str)
    if not p.exists():
        return None
    stat = p.stat()
    return {
        "path": str(p),
        "name": p.name,
        "size_kb": round(stat.st_size / 1024, 1),
        "modified": datetime.fromtimestamp(stat.st_mtime).strftime("%d/%m/%Y %H:%M"),
        "mtime": stat.st_mtime,
    }


def _pdf_variants_for_run(run_d: dict) -> dict[str, dict]:
    if not run_d:
        return {}
    variants: dict[str, dict] = {}
    for motor_id, key in (
        ("motor_027", "pdf_output_paths"),
        ("motor_027", "pdf_source_paths"),
        ("motor_017", "pdf_paths"),
    ):
        out = _load_motor_output(run_d, motor_id)
        raw = out.get(key, {})
        if not isinstance(raw, dict):
            continue
        for language, path_str in raw.items():
            meta = _pdf_metadata(path_str)
            if meta is not None:
                variants[str(language)] = meta
        if variants:
            return variants
    single = None
    for motor_id, key in (
        ("motor_027", "pdf_output_path"),
        ("motor_027", "pdf_source_path"),
        ("motor_017", "pdf_path"),
    ):
        out = _load_motor_output(run_d, motor_id)
        single = _pdf_metadata(out.get(key, ""))
        if single is not None:
            break
    return {"en": single} if single is not None else {}


def _pdf_for_run(run_d: dict, *, allow_global_fallback: bool = False) -> dict | None:
    if not run_d:
        return _latest_pdf() if allow_global_fallback else None
    variants = _pdf_variants_for_run(run_d)
    if variants:
        return variants.get("en") or next(iter(variants.values()))
    for motor_id, key in (
        ("motor_027", "pdf_output_path"),
        ("motor_027", "pdf_source_path"),
        ("motor_017", "pdf_path"),
    ):
        out = _load_motor_output(run_d, motor_id)
        meta = _pdf_metadata(out.get(key, ""))
        if meta is not None:
            return meta
    return _latest_pdf() if allow_global_fallback else None


def _source_refresh_status() -> dict:
    pid_running = False
    if _SOURCE_REFRESH_PID.exists():
        try:
            import os as _os
            _os.kill(int(_SOURCE_REFRESH_PID.read_text().strip()), 0)
            pid_running = True
        except Exception:
            pass
    if not _SOURCE_REFRESH_STATUS.exists():
        return {
            "enabled": False,
            "running": False,
            "mode": "manual_only",
            "companies": [],
            "log": [],
            "total_sweeps": 0,
            "message": "Refresco automático desactivado. El análisis solo corre al pulsar Analizar.",
        }
    try:
        d = json.loads(_SOURCE_REFRESH_STATUS.read_text())
        d["enabled"] = False
        d["running"] = False
        d["mode"] = "manual_only"
        d["message"] = "Refresco automático desactivado. El análisis solo corre al pulsar Analizar."
        return d
    except Exception:
        return {
            "enabled": False,
            "running": False,
            "mode": "manual_only",
            "companies": [],
            "log": [],
            "total_sweeps": 0,
            "message": "Refresco automático desactivado. El análisis solo corre al pulsar Analizar.",
        }


# ── API ───────────────────────────────────────────────────────────────────────

@app.route("/api/live")
def api_live():
    """Endpoint principal: todo lo necesario para el dashboard en una llamada."""
    runs = _all_runs()
    requested_run_id = (request.args.get("run_id") or "").strip()
    requested_pipeline_id = (request.args.get("pipeline_id") or "").strip()
    requested_seed = _target_seed_lookup(requested_pipeline_id)
    if not runs:
        if requested_seed:
            return jsonify({
                "has_run": False,
                "pipeline_id": requested_pipeline_id,
                "display_status": "not_started",
                "target": _target_from_seed_record(requested_seed),
                "case_title": requested_seed.get("target_label", requested_pipeline_id),
            })
        return jsonify({
            "has_run": False,
            "pipeline_id": requested_pipeline_id,
        })

    active = _select_active_run(
        runs,
        requested_run_id=requested_run_id,
        requested_pipeline_id=requested_pipeline_id,
    )
    if active is None:
        if requested_seed:
            return jsonify({
                "has_run": False,
                "pipeline_id": requested_pipeline_id,
                "display_status": "not_started",
                "target": _target_from_seed_record(requested_seed),
                "case_title": requested_seed.get("target_label", requested_pipeline_id),
                "all_runs": runs[:8],
            })
        return jsonify({
            "has_run": False,
            "pipeline_id": requested_pipeline_id,
            "all_runs": runs[:8],
        })
    run_id  = active["run_id"]
    raw_run = _load_run(run_id)
    detail = _run_detail(run_id)
    motors = detail.get("motors", [])

    company  = _company_info(raw_run)
    target   = _target_info(raw_run)
    research = _research_activity(raw_run)
    ingestion = _canonicalize_ingestion_payload(_ingestion_activity(raw_run))
    focus    = _focus_activity(raw_run, motors)
    charts   = _chart_activity(raw_run)
    congruence_brain = _congruence_brain_activity(raw_run)
    audit    = _audit_failures(run_id)
    pdf      = _pdf_for_run(
        raw_run,
        allow_global_fallback=not requested_run_id and not requested_pipeline_id,
    )
    pdf_variants = _pdf_variants_for_run(raw_run)
    display_status = _display_status(active["status"], pdf_available=pdf is not None)
    return jsonify({
        "has_run":     True,
        "run_id":      run_id,
        "status":      active["status"],
        "display_status": display_status,
        "case_title":  detail.get("case_title") or active.get("pipeline_id", ""),
        "pipeline_id": active.get("pipeline_id", ""),
        "started_at":  detail.get("started_at", ""),
        "duration_s":  detail.get("duration_s"),
        "error":       detail.get("error"),
        "summary":     detail.get("summary", {}),
        "report_type_trace": _canonicalize_report_type_trace(dict(raw_run.get("report_type_trace", {}) or {})),
        "phase_self_evaluation_summary": raw_run.get("phase_self_evaluation_summary", {}),
        "previous_run_id": raw_run.get("previous_run_id"),
        "case_delta_summary": raw_run.get("case_delta_summary", {}),
        "source_yield_memory_summary": raw_run.get("source_yield_memory_summary", {}),
        "next_ingestion_priority_update": raw_run.get("next_ingestion_priority_update", {}),
        "ingestion_learning_summary": raw_run.get("ingestion_learning_summary", {}),
        "motor_overview": detail.get("motor_overview", {}),
        "motors":      motors,
        "target":      target,
        "company":     company,
        "research":    research,
        "ingestion":   ingestion,
        "focus":       focus,
        "charts":      charts,
        "congruence_brain": congruence_brain,
        "audit":       audit,
        "pdf":         pdf,
        "pdf_variants": pdf_variants,
        "requested_pipeline_id": requested_pipeline_id,
        "all_runs":    runs[:8],
    })


@app.route("/api/latest-pdf")
def api_latest_pdf():
    pdf = _latest_pdf()
    if not pdf:
        return jsonify({"available": False})
    return jsonify({"available": True, **pdf})


@app.route("/api/combination-decision", methods=["POST"])
def api_combination_decision():
    data = request.get_json() or {}
    run_id = str(data.get("run_id", "")).strip()
    combination_id = str(data.get("combination_id", "")).strip()
    if not run_id or not combination_id:
        return jsonify({"ok": False, "error": "run_id and combination_id are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    review_rows = list(congruence_brain.get("combination_review_register", []) or [])
    admissible_rows = list(congruence_brain.get("admissible_combination_review_register", []) or [])
    valid_combination_ids = {
        str(row.get("combination_id", "")).strip()
        for row in [*review_rows, *admissible_rows]
        if str(row.get("combination_id", "")).strip()
    }
    if combination_id not in valid_combination_ids:
        return jsonify({"ok": False, "error": "combination is not active for this run"}), 400

    if normalize_combination_decision_record is None:
        return jsonify({"ok": False, "error": "adjudication engine unavailable"}), 500

    try:
        record = normalize_combination_decision_record(
            {
                "combination_id": combination_id,
                "operator_decision": data.get("operator_decision"),
                "decision_reason": data.get("decision_reason"),
                "decision_scope": data.get("decision_scope") or "run",
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    target_row = next(
        (
            row
            for row in [*review_rows, *admissible_rows]
            if str(row.get("combination_id", "")).strip() == combination_id
        ),
        {},
    )
    if str(target_row.get("validator_state", "")).strip() == "blocked" and record.get("operator_decision") != "blocked_by_validator":
        return jsonify({"ok": False, "error": "combination is blocked by validator"}), 400

    decision_store = _persist_combination_decision_record(run_id, record)
    control_store = _load_combination_review_control_store(run_id)
    deferred_ids = [
        item
        for item in list(control_store.get("deferred_combination_ids", []) or [])
        if _text(item) and _text(item) != combination_id
    ]
    _persist_combination_review_control_store(
        run_id,
        deferred_combination_ids=deferred_ids,
        batch_size=int(control_store.get("batch_size", 1) or 1),
    )
    if record.get("operator_decision") in {"needs_review", "rejected_for_case_use"}:
        _persist_follow_on_research_for_combination(
            run_id,
            combination_id=combination_id,
            reason_prefix="Decision-driven follow-on research:",
            combination_follow_on_research_register=list(congruence_brain.get("combination_follow_on_research_register", []) or []),
        )
    refreshed = _congruence_brain_activity(run_d)
    updated_row = next(
        (
            row
            for row in [
                *list(refreshed.get("combination_review_register", []) or []),
                *list(refreshed.get("admissible_combination_review_register", []) or []),
            ]
            if str(row.get("combination_id", "")).strip() == combination_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "decision_store": {
                "updated_at": str(decision_store.get("updated_at", "")).strip(),
                "stored_decision_count": len(list(decision_store.get("decisions", []) or [])),
            },
            "updated_row": updated_row,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/combination-edit", methods=["POST"])
def api_combination_edit():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    combination_id = _text(data.get("combination_id"))
    if not run_id or not combination_id:
        return jsonify({"ok": False, "error": "run_id and combination_id are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    valid_combination_ids = {
        _text(row.get("combination_id"))
        for row in [
            *list(congruence_brain.get("combination_review_register", []) or []),
            *list(congruence_brain.get("admissible_combination_review_register", []) or []),
        ]
        if _text(row.get("combination_id"))
    }
    if combination_id not in valid_combination_ids:
        return jsonify({"ok": False, "error": "combination is not active for this run"}), 400

    try:
        record = _normalize_combination_edit_record(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    edit_store = _persist_combination_edit_record(run_id, record)
    auto_close = bool(data.get("auto_close_review", True))
    decision_store = None
    if auto_close and normalize_combination_decision_record is not None:
        decision_record = normalize_combination_decision_record(
            {
                "combination_id": combination_id,
                "operator_decision": "needs_review",
                "decision_reason": _text(data.get("decision_reason")) or "Modified from dashboard sequential review.",
                "decision_scope": "run",
            }
        )
        decision_store = _persist_combination_decision_record(run_id, decision_record)
    control_store = _load_combination_review_control_store(run_id)
    deferred_ids = [
        item
        for item in list(control_store.get("deferred_combination_ids", []) or [])
        if _text(item) and _text(item) != combination_id
    ]
    _persist_combination_review_control_store(
        run_id,
        deferred_combination_ids=deferred_ids,
        batch_size=int(control_store.get("batch_size", 1) or 1),
    )
    _persist_follow_on_research_for_combination(
        run_id,
        combination_id=combination_id,
        reason_prefix="Modification-driven follow-on research:",
        combination_follow_on_research_register=list(congruence_brain.get("combination_follow_on_research_register", []) or []),
    )

    refreshed = _congruence_brain_activity(run_d)
    updated_row = next(
        (
            row
            for row in list(refreshed.get("combination_review_sequence_register", []) or [])
            if _text(row.get("combination_id")) == combination_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "edit_store": {
                "updated_at": _text(edit_store.get("updated_at")),
                "stored_edit_count": len(list(edit_store.get("edits", []) or [])),
            },
            "decision_store": {
                "updated_at": _text((decision_store or {}).get("updated_at")),
                "stored_decision_count": len(list((decision_store or {}).get("decisions", []) or [])),
            },
            "updated_row": updated_row,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/combination-review-control", methods=["POST"])
def api_combination_review_control():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    current_store = _load_combination_review_control_store(run_id)
    current_deferred = [
        _text(item)
        for item in list(current_store.get("deferred_combination_ids", []) or [])
        if _text(item)
    ]
    batch_size = int(current_store.get("batch_size", 1) or 1)
    action = _text(data.get("action")) or "set"
    combination_id = _text(data.get("combination_id"))

    if action == "defer_current":
        if not combination_id:
            return jsonify({"ok": False, "error": "combination_id is required for defer_current"}), 400
        if combination_id not in current_deferred:
            current_deferred.append(combination_id)
    elif action == "undefer":
        if not combination_id:
            return jsonify({"ok": False, "error": "combination_id is required for undefer"}), 400
        current_deferred = [item for item in current_deferred if item != combination_id]
    elif action == "set_batch_size":
        try:
            control_record = _normalize_combination_review_control_record({"batch_size": data.get("batch_size")})
        except Exception as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400
        batch_size = int(control_record.get("batch_size", 1) or 1)
    elif action != "set":
        return jsonify({"ok": False, "error": "action must be one of: ['set', 'defer_current', 'undefer', 'set_batch_size']"}), 400

    try:
        control_record = _normalize_combination_review_control_record(
            {
                "deferred_combination_ids": current_deferred,
                "batch_size": batch_size,
            }
        )
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    store = _persist_combination_review_control_store(
        run_id,
        deferred_combination_ids=list(control_record.get("deferred_combination_ids", []) or []),
        batch_size=int(control_record.get("batch_size", 1) or 1),
    )
    if action == "defer_current" and combination_id:
        congruence_brain = _congruence_brain_activity(run_d)
        _persist_follow_on_research_for_combination(
            run_id,
            combination_id=combination_id,
            reason_prefix="Deferred-review follow-on research:",
            combination_follow_on_research_register=list(congruence_brain.get("combination_follow_on_research_register", []) or []),
        )
    refreshed = _congruence_brain_activity(run_d)
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "control_store": {
                "updated_at": _text(store.get("updated_at")),
                "deferred_count": len(list(store.get("deferred_combination_ids", []) or [])),
                "batch_size": int(store.get("batch_size", 1) or 1),
            },
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/research-loop-control", methods=["POST"])
def api_research_loop_control():
    data = request.get_json() or {}
    try:
        record = _normalize_research_loop_control_record(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    run_id = _text(record.get("run_id"))
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    store = _persist_research_loop_control_record(run_id, record)
    refreshed = _congruence_brain_activity(run_d)
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "control_store": {
                "updated_at": _text(store.get("updated_at")),
                "control_state": _text(store.get("control_state")) or "active",
                "requested_action": _text(store.get("requested_action")) or "resume",
                "control_reason": _text(store.get("control_reason")),
            },
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/research-loop-advance", methods=["POST"])
def api_research_loop_advance():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    result = _execute_research_loop_advance(
        run_id=run_id,
        run_d=run_d,
    )
    status_code = 200 if bool(result.get("ok")) else 400
    return jsonify({"run_id": run_id, **result}), status_code


@app.route("/api/research-loop-force-rerank", methods=["POST"])
def api_research_loop_force_rerank():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    auto_refresh = _refresh_reference_backed_promotions_state(run_id=run_id)
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "knowledge_atom_refresh_summary": dict(auto_refresh.get("knowledge_atom_refresh_summary", {}) or {}),
            "combination_rerank_summary": dict(auto_refresh.get("combination_rerank_summary", {}) or {}),
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/latent-cluster-decision", methods=["POST"])
def api_latent_cluster_decision():
    data = request.get_json() or {}
    run_id = str(data.get("run_id", "")).strip()
    cluster_id = str(data.get("cluster_id", "")).strip()
    if not run_id or not cluster_id:
        return jsonify({"ok": False, "error": "run_id and cluster_id are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    cluster_rows = list(congruence_brain.get("latent_combination_cluster_register", []) or [])
    admissible_rows = list(congruence_brain.get("admissible_combination_review_register", []) or [])
    cluster_row = next(
        (
            row
            for row in cluster_rows
            if str(row.get("cluster_id", "")).strip() == cluster_id
        ),
        {},
    )
    if not cluster_row:
        return jsonify({"ok": False, "error": "latent cluster is not active for this run"}), 400

    admissible_ids = {
        str(row.get("combination_id", "")).strip()
        for row in admissible_rows
        if str(row.get("combination_id", "")).strip()
    }
    target_ids = [
        str(candidate_id).strip()
        for candidate_id in list(cluster_row.get("candidate_ids", []) or [])
        if str(candidate_id).strip() in admissible_ids
    ]
    if not target_ids:
        return jsonify({"ok": False, "error": "latent cluster has no admissible candidates for adjudication"}), 400

    if normalize_combination_decision_record is None:
        return jsonify({"ok": False, "error": "adjudication engine unavailable"}), 500

    operator_decision = data.get("operator_decision")
    decision_reason = data.get("decision_reason")
    stored_records: list[dict[str, Any]] = []
    for combination_id in target_ids:
        try:
            record = normalize_combination_decision_record(
                {
                    "combination_id": combination_id,
                    "operator_decision": operator_decision,
                    "decision_reason": decision_reason,
                    "decision_scope": data.get("decision_scope") or "run",
                }
            )
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400
        _persist_combination_decision_record(run_id, record)
        stored_records.append(record)

    refreshed = _congruence_brain_activity(run_d)
    updated_rows = [
        row
        for row in list(refreshed.get("admissible_combination_review_register", []) or [])
        if str(row.get("combination_id", "")).strip() in target_ids
    ]
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "cluster_id": cluster_id,
            "stored_records": stored_records,
            "updated_rows": updated_rows,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/latent-cluster-split", methods=["POST"])
def api_latent_cluster_split():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    source_cluster_id = _text(data.get("source_cluster_id"))
    if not run_id or not source_cluster_id:
        return jsonify({"ok": False, "error": "run_id and source_cluster_id are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    cluster_rows = list(congruence_brain.get("latent_combination_cluster_register", []) or [])
    source_cluster = next((row for row in cluster_rows if _text(row.get("cluster_id")) == source_cluster_id), {})
    if not source_cluster:
        return jsonify({"ok": False, "error": "source latent cluster is not active for this run"}), 400

    try:
        record = _normalize_latent_cluster_split_record(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    allowed_candidate_ids = {_text(item) for item in list(source_cluster.get("candidate_ids", []) or []) if _text(item)}
    requested_candidate_ids = [_text(item) for item in list(record.get("candidate_ids", []) or []) if _text(item)]
    if not requested_candidate_ids or not set(requested_candidate_ids).issubset(allowed_candidate_ids):
        return jsonify({"ok": False, "error": "candidate_ids must belong to the source latent cluster"}), 400

    override_store = _persist_latent_cluster_split_assignments(run_id, record)
    refreshed = _congruence_brain_activity(run_d)
    updated_clusters = [
        row
        for row in list(refreshed.get("latent_combination_cluster_register", []) or [])
        if set(requested_candidate_ids).intersection({_text(item) for item in list(row.get("candidate_ids", []) or []) if _text(item)})
    ]
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "override_store": {
                "updated_at": _text(override_store.get("updated_at")),
                "split_assignment_count": len(list(override_store.get("split_assignments", []) or [])),
                "merge_assignment_count": len(list(override_store.get("merge_assignments", []) or [])),
            },
            "updated_clusters": updated_clusters,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/latent-cluster-merge", methods=["POST"])
def api_latent_cluster_merge():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    source_cluster_id = _text(data.get("source_cluster_id"))
    target_cluster_id = _text(data.get("target_cluster_id"))
    if not run_id or not source_cluster_id or not target_cluster_id:
        return jsonify({"ok": False, "error": "run_id, source_cluster_id and target_cluster_id are required"}), 400
    if source_cluster_id == target_cluster_id:
        return jsonify({"ok": False, "error": "source and target cluster must differ"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    cluster_rows = list(congruence_brain.get("latent_combination_cluster_register", []) or [])
    cluster_ids = {_text(row.get("cluster_id")) for row in cluster_rows if _text(row.get("cluster_id"))}
    if source_cluster_id not in cluster_ids or target_cluster_id not in cluster_ids:
        return jsonify({"ok": False, "error": "both source and target clusters must be active for this run"}), 400

    try:
        record = _normalize_latent_cluster_merge_record(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    existing_store = _load_latent_cluster_override_store(run_id)
    merge_map = {
        _text(row.get("source_cluster_id")): _text(row.get("target_cluster_id"))
        for row in list(existing_store.get("merge_assignments", []) or [])
        if _text(row.get("source_cluster_id")) and _text(row.get("target_cluster_id"))
    }
    seen: set[str] = {source_cluster_id}
    current = target_cluster_id
    while current in merge_map:
        current = _text(merge_map.get(current))
        if current in seen:
            return jsonify({"ok": False, "error": "merge would create a latent cluster cycle"}), 400
        seen.add(current)

    override_store = _persist_latent_cluster_merge_assignment(run_id, record)
    refreshed = _congruence_brain_activity(run_d)
    updated_clusters = [
        row
        for row in list(refreshed.get("latent_combination_cluster_register", []) or [])
        if _text(row.get("cluster_id")) == target_cluster_id or source_cluster_id in set(list(row.get("source_cluster_ids", []) or []))
    ]
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "override_store": {
                "updated_at": _text(override_store.get("updated_at")),
                "split_assignment_count": len(list(override_store.get("split_assignments", []) or [])),
                "merge_assignment_count": len(list(override_store.get("merge_assignments", []) or [])),
            },
            "updated_clusters": updated_clusters,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/source-family-trigger", methods=["POST"])
def api_source_family_trigger():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    source_family = _text(data.get("source_family"))
    if not run_id or not source_family:
        return jsonify({"ok": False, "error": "run_id and source_family are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    trigger_rows = list(congruence_brain.get("research_campaign_trigger_register", []) or [])
    trigger_row = next(
        (row for row in trigger_rows if _text(row.get("source_family")) == source_family),
        {},
    )
    if not trigger_row:
        return jsonify({"ok": False, "error": "source_family is not active for this run"}), 400

    if build_source_family_trigger_plan is None:
        return jsonify({"ok": False, "error": "research campaign trigger planner unavailable"}), 500

    try:
        record = _normalize_research_campaign_trigger_record(
            {
                **dict(trigger_row),
                "reason": _text(data.get("reason")) or _text(trigger_row.get("reason")) or "Queued from dashboard.",
                "status": _text(data.get("status")) or "queued",
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    store = _persist_research_campaign_trigger_record(run_id, record)
    refreshed = _congruence_brain_activity(run_d)
    updated_row = next(
        (
            row
            for row in list(refreshed.get("research_campaign_trigger_register", []) or [])
            if _text(row.get("source_family")) == source_family
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "trigger_store": {
                "updated_at": _text(store.get("updated_at")),
                "stored_trigger_count": len(list(store.get("triggers", []) or [])),
            },
            "updated_row": updated_row,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/source-family-exhausted", methods=["POST"])
def api_source_family_exhausted():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    source_family = _text(data.get("source_family"))
    if not run_id or not source_family:
        return jsonify({"ok": False, "error": "run_id and source_family are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    trigger_rows = list(congruence_brain.get("research_campaign_trigger_register", []) or [])
    trigger_row = next(
        (row for row in trigger_rows if _text(row.get("source_family")) == source_family),
        {},
    )
    if not trigger_row:
        return jsonify({"ok": False, "error": "source_family is not active for this run"}), 400

    try:
        record = _normalize_research_campaign_trigger_record(
            {
                **dict(trigger_row),
                "status": "exhausted",
                "reason": _text(data.get("reason")) or f"Marked exhausted from dashboard for {source_family}.",
                "target_document_delta": 0,
                "target_knowledge_atom_delta": 0,
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    store = _persist_research_campaign_trigger_record(run_id, record)
    refreshed = _congruence_brain_activity(run_d)
    updated_row = next(
        (
            row
            for row in list(refreshed.get("research_campaign_trigger_register", []) or [])
            if _text(row.get("source_family")) == source_family
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "trigger_store": {
                "updated_at": _text(store.get("updated_at")),
                "stored_trigger_count": len(list(store.get("triggers", []) or [])),
            },
            "updated_row": updated_row,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/combination-follow-on-manifest-materialize", methods=["POST"])
def api_combination_follow_on_manifest_materialize():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    combination_id = _text(data.get("combination_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    if not combination_id:
        combination_id = _text((congruence_brain.get("current_combination_review_row", {}) or {}).get("combination_id"))
    if not combination_id:
        return jsonify({"ok": False, "error": "no current combination to materialize"}), 400

    record = _materialize_follow_on_execution_manifest_for_combination(
        run_id,
        combination_id=combination_id,
        combination_follow_on_execution_manifest_register=list(
            congruence_brain.get("combination_follow_on_execution_manifest_register", []) or []
        ),
    )
    if not record:
        return jsonify({"ok": False, "error": "no follow-on execution manifest is available for this combination"}), 400

    refreshed = _congruence_brain_activity(run_d)
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "manifest_store": dict(refreshed.get("combination_follow_on_manifest_store", {}) or {}),
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/combination-follow-on-seed-candidates", methods=["POST"])
def api_combination_follow_on_seed_candidates():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    combination_id = _text(data.get("combination_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    if not combination_id:
        combination_id = _text((congruence_brain.get("current_combination_review_row", {}) or {}).get("combination_id"))
    if not combination_id:
        return jsonify({"ok": False, "error": "no current combination is available to seed"}), 400

    target_manifest = next(
        (
            row for row in list(congruence_brain.get("combination_follow_on_execution_manifest_register", []) or [])
            if _text(row.get("combination_id")) == combination_id
        ),
        {},
    )
    if not target_manifest:
        return jsonify({"ok": False, "error": "no follow-on execution manifest exists for this combination"}), 400

    seed_records = _build_query_seed_candidate_records(
        combination_id=combination_id,
        follow_on_manifest_row=dict(target_manifest or {}),
    )
    if not seed_records:
        return jsonify({"ok": False, "error": "no provider query templates exist for this combination"}), 400

    seeded_candidate_ids: list[str] = []
    for seed_record in seed_records:
        candidate_id = _text(seed_record.get("candidate_id"))
        try:
            _upsert_manual_discovery_candidate(
                run_id=run_id,
                record=seed_record,
                candidate_id_override=candidate_id,
                creation_reason="Seeded from combination follow-on research plan.",
                refresh_after=False,
            )
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400
        seeded_candidate_ids.append(candidate_id)

    auto_refresh = _refresh_reference_backed_promotions_state(
        run_id=run_id,
        run_d=run_d,
    )
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    refreshed_licensed = dict(auto_refresh.get("licensed", {}) or {})
    seeded_id_set = set(seeded_candidate_ids)
    updated_rows = [
        row
        for row in list(refreshed_licensed.get("discovery_candidate_review_register", []) or [])
        if _text(row.get("candidate_id")) in seeded_id_set
    ]
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "combination_id": combination_id,
            "seeded_candidate_ids": seeded_candidate_ids,
            "updated_rows": updated_rows,
            "discovery_queue_manifest": _load_licensed_discovery_queue_manifest(run_id),
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/promotion-decision", methods=["POST"])
def api_promotion_decision():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    promotion_id = _text(data.get("promotion_id"))
    if not run_id or not promotion_id:
        return jsonify({"ok": False, "error": "run_id and promotion_id are required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    review_rows = list(licensed.get("promotion_review_register", []) or [])
    valid_promotion_ids = {
        _text(row.get("promotion_id"))
        for row in review_rows
        if _text(row.get("promotion_id"))
    }
    if promotion_id not in valid_promotion_ids:
        return jsonify({"ok": False, "error": "promotion is not active for this run"}), 400

    try:
        record = _normalize_promotion_decision_record(
            {
                "promotion_id": promotion_id,
                "promotion_type": data.get("promotion_type"),
                "operator_decision": data.get("operator_decision"),
                "decision_reason": data.get("decision_reason"),
                "decision_scope": data.get("decision_scope") or "run",
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    target_row = next(
        (
            row
            for row in review_rows
            if _text(row.get("promotion_id")) == promotion_id
        ),
        {},
    )
    if _text(target_row.get("operator_decision")) == "blocked_by_validator" and record.get("operator_decision") != "blocked_by_validator":
        return jsonify({"ok": False, "error": "promotion is blocked by validator"}), 400

    decision_store = _persist_promotion_decision_record(run_id, record)
    refreshed = _congruence_brain_activity(run_d)
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    updated_row = next(
        (
            row
            for row in list(refreshed_licensed.get("promotion_review_register", []) or [])
            if _text(row.get("promotion_id")) == promotion_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "decision_store": {
                "updated_at": _text(decision_store.get("updated_at")),
                "stored_decision_count": len(list(decision_store.get("decisions", []) or [])),
            },
            "updated_row": updated_row,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/promotion-edit", methods=["POST"])
def api_promotion_edit():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    promotion_id = _text(data.get("promotion_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not promotion_id:
        return jsonify({"ok": False, "error": "promotion_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    review_rows = list(licensed.get("promotion_review_register", []) or [])
    target_row = next(
        (
            row
            for row in review_rows
            if _text(row.get("promotion_id")) == promotion_id
        ),
        {},
    )
    if not target_row:
        return jsonify({"ok": False, "error": "promotion is not active for this run"}), 400
    if _text(target_row.get("operator_decision")) == "blocked_by_validator":
        return jsonify({"ok": False, "error": "promotion is blocked by validator"}), 400
    try:
        edit_record = _normalize_promotion_edit_record(
            {
                "promotion_id": promotion_id,
                "promotion_type": data.get("promotion_type") or target_row.get("promotion_type"),
                "patch": data.get("patch"),
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    edit_store = _persist_promotion_edit_record(run_id, edit_record)
    refreshed = _congruence_brain_activity(run_d)
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    updated_row = next(
        (
            row
            for row in list(refreshed_licensed.get("promotion_review_register", []) or [])
            if _text(row.get("promotion_id")) == promotion_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": edit_record,
            "edit_store": {
                "updated_at": _text(edit_store.get("updated_at")),
                "stored_edit_count": len(list(edit_store.get("edits", []) or [])),
            },
            "updated_row": updated_row,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/discovery-queue-import", methods=["POST"])
def api_discovery_queue_import():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    export_path = _text(data.get("export_path"))
    provider_key = _text(data.get("provider_key")) or "scopus"
    intake_dir = _text(data.get("intake_dir")) or str(Path.home() / "Desktop" / "ZLab_Licensed_Research_Intake")
    top_k = int(data.get("top_k") or 25)
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not export_path:
        return jsonify({"ok": False, "error": "export_path is required"}), 400
    if materialize_licensed_discovery_candidate_queue is None or load_registry_bundle is None:
        return jsonify({"ok": False, "error": "licensed discovery queue is unavailable"}), 400
    try:
        manifest = materialize_licensed_discovery_candidate_queue(
            export_path=export_path,
            intake_dir=intake_dir,
            provider_key=provider_key,
            registry_bundle=load_registry_bundle(),
            top_k=top_k,
        )
        stored = _persist_licensed_discovery_queue_manifest(run_id, manifest)
    except Exception as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    run_d = _load_run(run_id)
    refreshed = _congruence_brain_activity(run_d or {"run_id": run_id})
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "discovery_queue_manifest": stored,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/discovery-candidate-decision", methods=["POST"])
def api_discovery_candidate_decision():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    run_d = _load_run(run_id)
    congruence_brain = _congruence_brain_activity(run_d or {"run_id": run_id})
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    review_rows = list(licensed.get("discovery_candidate_review_register", []) or [])
    valid_ids = {_text(row.get("candidate_id")) for row in review_rows if _text(row.get("candidate_id"))}
    if candidate_id not in valid_ids:
        return jsonify({"ok": False, "error": "candidate is not active for this run"}), 400
    try:
        record = _normalize_discovery_candidate_decision_record(
            {
                "candidate_id": candidate_id,
                "operator_decision": data.get("operator_decision"),
                "decision_reason": data.get("decision_reason"),
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    decision_store = _persist_discovery_candidate_decision_record(run_id, record)
    refreshed = _congruence_brain_activity(run_d or {"run_id": run_id})
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    updated_row = next(
        (
            row for row in list(refreshed_licensed.get("discovery_candidate_review_register", []) or [])
            if _text(row.get("candidate_id")) == candidate_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "record": record,
            "decision_store": {
                "updated_at": _text(decision_store.get("updated_at")),
                "stored_decision_count": len(list(decision_store.get("decisions", []) or [])),
            },
            "updated_row": updated_row,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/discovery-candidate-edit", methods=["POST"])
def api_discovery_candidate_edit():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    if not manifest.get("exists"):
        return jsonify({"ok": False, "error": "no discovery queue imported for this run"}), 400
    rows = list(manifest.get("candidate_rows", []) or [])
    target_idx = next((idx for idx, row in enumerate(rows) if _text(row.get("candidate_id")) == candidate_id), -1)
    if target_idx < 0:
        return jsonify({"ok": False, "error": "candidate not found in imported queue"}), 400
    try:
        edit_record = _normalize_discovery_candidate_edit_record(
            {
                "candidate_id": candidate_id,
                "patch": data.get("patch"),
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    registry_bundle = load_registry_bundle() if load_registry_bundle is not None else {}
    edited_row = _apply_discovery_candidate_edit(
        rows[target_idx],
        edit_record,
        registry_bundle=registry_bundle,
    )
    rows[target_idx] = edited_row
    manifest["candidate_rows"] = rows
    _persist_licensed_discovery_queue_manifest(run_id, manifest)
    edit_store = _persist_discovery_candidate_edit_record(run_id, edit_record)
    refreshed = _congruence_brain_activity(_load_run(run_id) or {"run_id": run_id})
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    updated_row = next(
        (
            row for row in list(refreshed_licensed.get("discovery_candidate_review_register", []) or [])
            if _text(row.get("candidate_id")) == candidate_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "edit_store": {
                "updated_at": _text(edit_store.get("updated_at")),
                "stored_edit_count": len(list(edit_store.get("edits", []) or [])),
            },
            "updated_row": updated_row,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/discovery-candidate-create", methods=["POST"])
def api_discovery_candidate_create():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    try:
        record = _normalize_manual_discovery_candidate_record(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    try:
        result = _upsert_manual_discovery_candidate(
            run_id=run_id,
            record=record,
            creation_reason="Created manually from dashboard.",
            refresh_after=True,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            **result,
        }
    )


@app.route("/api/article-reference-read", methods=["POST"])
def api_article_reference_read():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    rows = list(manifest.get("candidate_rows", []) or [])
    candidate_row = next((dict(row) for row in rows if _text(row.get("candidate_id")) == candidate_id), {})
    if not candidate_row:
        return jsonify({"ok": False, "error": "candidate not found in imported queue"}), 400
    reference_result = _read_article_reference_for_candidate(run_id=run_id, candidate_row=candidate_row)
    auto_refresh = _refresh_reference_backed_promotions_state(
        run_id=run_id,
        candidate_id=candidate_id,
    )
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    refreshed_licensed = dict(auto_refresh.get("licensed", {}) or {})
    accepted_bundle_manifest = dict(auto_refresh.get("accepted_bundle_manifest", {}) or {})
    updated_row = next(
        (
            row for row in list(refreshed_licensed.get("article_reference_register", []) or [])
            if _text(row.get("candidate_id")) == candidate_id
        ),
        {},
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "article_reference_store": dict(reference_result.get("article_reference_store", {}) or {}),
            "accepted_discovery_candidate_bundle_manifest": accepted_bundle_manifest,
            "reference_backed_promotion_manifest": dict(auto_refresh.get("reference_backed_promotion_manifest", {}) or {}),
            "knowledge_atom_refresh_summary": dict(auto_refresh.get("knowledge_atom_refresh_summary", {}) or {}),
            "combination_rerank_summary": dict(auto_refresh.get("combination_rerank_summary", {}) or {}),
            "updated_row": updated_row,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/article-reference-edit", methods=["POST"])
def api_article_reference_edit():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    rows = list(manifest.get("candidate_rows", []) or [])
    candidate_row = next((dict(row) for row in rows if _text(row.get("candidate_id")) == candidate_id), {})
    if not candidate_row:
        return jsonify({"ok": False, "error": "candidate not found in imported queue"}), 400
    try:
        edit_record = _normalize_article_reference_edit_record(
            {
                "candidate_id": candidate_id,
                "auto_accept_discovery_candidate": data.get("auto_accept_discovery_candidate"),
                "patch": data.get("patch"),
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            **_execute_article_reference_edit(
                run_id=run_id,
                candidate_id=candidate_id,
                edit_record=edit_record,
            ),
        }
    )


@app.route("/api/article-reference-quick-resolve", methods=["POST"])
def api_article_reference_quick_resolve():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    try:
        manifest = _load_licensed_discovery_queue_manifest(run_id)
        rows = list(manifest.get("candidate_rows", []) or [])
        candidate_row = next((dict(row) for row in rows if _text(row.get("candidate_id")) == candidate_id), {})
        if not candidate_row:
            return jsonify({"ok": False, "error": "candidate not found in imported queue"}), 400
        current_store = _load_article_reference_record_store(run_id)
        current_records = {
            _text(row.get("candidate_id")): dict(row)
            for row in list(current_store.get("records", []) or [])
            if _text(row.get("candidate_id"))
        }
        hydrated_patch = _hydrate_reference_resolution_patch(
            candidate_row=candidate_row,
            reference_record=current_records.get(candidate_id, {}),
            patch={
                "source_url": data.get("source_url"),
                "reference_excerpt": data.get("reference_excerpt"),
                "notes": data.get("notes"),
                "reference_state": "manual_text_enriched",
            },
        )
        edit_record = _normalize_article_reference_quick_resolve_record(
            {
                "candidate_id": candidate_id,
                "source_url": hydrated_patch.get("source_url"),
                "reference_excerpt": hydrated_patch.get("reference_excerpt"),
                "notes": hydrated_patch.get("notes"),
                "auto_accept_discovery_candidate": data.get("auto_accept_discovery_candidate", True),
            }
        )
        result = _execute_article_reference_edit(
            run_id=run_id,
            candidate_id=candidate_id,
            edit_record=edit_record,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            **result,
        }
    )


@app.route("/api/article-reference-capture-search-result", methods=["POST"])
def api_article_reference_capture_search_result():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    try:
        edit_record = _normalize_article_reference_search_result_capture_record(
            {
                "candidate_id": candidate_id,
                "source_url": data.get("source_url"),
                "search_result_title": data.get("search_result_title"),
                "search_result_snippet": data.get("search_result_snippet"),
                "notes": data.get("notes"),
            }
        )
        result = _execute_article_reference_edit(
            run_id=run_id,
            candidate_id=candidate_id,
            edit_record=edit_record,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            **result,
        }
    )


@app.route("/api/article-reference-capture-search-result-batch", methods=["POST"])
def api_article_reference_capture_search_result_batch():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    try:
        parsed_blocks = _parse_search_result_capture_batch_payload(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    manifest = _load_licensed_discovery_queue_manifest(run_id)
    candidate_rows = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(manifest.get("candidate_rows", []) or [])
        if _text(row.get("candidate_id"))
    }
    seen_ids: set[str] = set()
    for block in parsed_blocks:
        candidate_id = _text(block.get("candidate_id"))
        if candidate_id in seen_ids:
            return jsonify({"ok": False, "error": f"duplicate candidate_id in batch: {candidate_id}"}), 400
        seen_ids.add(candidate_id)
        if candidate_id not in candidate_rows:
            return jsonify({"ok": False, "error": f"candidate not found in imported queue: {candidate_id}"}), 400

    results: list[dict[str, Any]] = []
    last_result: dict[str, Any] = {}
    for block in parsed_blocks:
        edit_record = _normalize_article_reference_search_result_capture_record(
            {
                "candidate_id": _text(block.get("candidate_id")),
                "source_url": block.get("source_url"),
                "search_result_title": block.get("search_result_title"),
                "search_result_snippet": block.get("search_result_snippet"),
                "notes": block.get("notes"),
            }
        )
        last_result = _execute_article_reference_edit(
            run_id=run_id,
            candidate_id=_text(block.get("candidate_id")),
            edit_record=edit_record,
        )
        results.append(
            {
                "candidate_id": _text(block.get("candidate_id")),
                "updated_row": dict(last_result.get("updated_row", {}) or {}),
            }
        )

    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "summary": {
                "captured_count": len(results),
                "capture_formats": sorted(
                    {
                        _text(block.get("capture_format")) or "packet"
                        for block in parsed_blocks
                    }
                ),
            },
            "rows": results,
            "article_reference_store": dict(last_result.get("article_reference_store", {}) or {}),
            "accepted_discovery_candidate_bundle_manifest": dict(
                last_result.get("accepted_discovery_candidate_bundle_manifest", {}) or {}
            ),
            "reference_backed_promotion_manifest": dict(
                last_result.get("reference_backed_promotion_manifest", {}) or {}
            ),
            "knowledge_atom_refresh_summary": dict(
                last_result.get("knowledge_atom_refresh_summary", {}) or {}
            ),
            "combination_rerank_summary": dict(
                last_result.get("combination_rerank_summary", {}) or {}
            ),
            "licensed_research": dict(last_result.get("licensed_research", {}) or {}),
            "congruence_brain": dict(last_result.get("congruence_brain", {}) or {}),
        }
    )


@app.route("/api/search-query-execution-import-results", methods=["POST"])
def api_search_query_execution_import_results():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    auto_capture_singleton_candidates = bool(data.get("auto_capture_singleton_candidates", False))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    preview = _congruence_brain_activity(run_d or {"run_id": run_id})
    preview_licensed = dict(preview.get("licensed_research", {}) or {})
    batch_plan = dict(
        preview.get("search_query_execution_batch_plan", {})
        or preview_licensed.get("search_query_execution_batch_plan", {})
        or {}
    )
    try:
        parsed_blocks = _parse_search_query_result_import_payload(
            data,
            ordered_candidate_ids=list(batch_plan.get("candidate_ids", []) or []),
            ordered_provider_capture_guide=dict(batch_plan.get("ordered_result_import_provider_capture_guide", {}) or {}),
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    try:
        payload = _apply_search_query_result_import_blocks(
            run_id=run_id,
            parsed_blocks=parsed_blocks,
            auto_capture_singleton_candidates=auto_capture_singleton_candidates,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(payload)


@app.route("/api/search-query-result-promote", methods=["POST"])
def api_search_query_result_promote():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    option_index = int(data.get("option_index", 1) or 1)
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    try:
        result = _promote_search_query_result_option(
            run_id=run_id,
            candidate_id=candidate_id,
            option_index=option_index,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            **result,
        }
    )


@app.route("/api/search-query-result-promote-and-resolve", methods=["POST"])
def api_search_query_result_promote_and_resolve():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    option_index = int(data.get("option_index", 1) or 1)
    reference_excerpt = _text(data.get("reference_excerpt"))
    notes = _text(data.get("notes"))
    auto_accept_discovery_candidate = bool(data.get("auto_accept_discovery_candidate", True))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    if not reference_excerpt:
        return jsonify({"ok": False, "error": "reference_excerpt is required"}), 400
    try:
        result = _resolve_search_query_result_option_with_excerpt(
            run_id=run_id,
            candidate_id=candidate_id,
            option_index=option_index,
            reference_excerpt=reference_excerpt,
            notes_override=notes,
            auto_accept_discovery_candidate=auto_accept_discovery_candidate,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            **result,
        }
    )


@app.route("/api/search-query-result-promote-batch", methods=["POST"])
def api_search_query_result_promote_batch():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    congruence_brain = _congruence_brain_activity(run_d or {"run_id": run_id})
    batch_plan = dict(congruence_brain.get("search_query_result_option_batch_plan", {}) or {})
    try:
        promotion_rows = _parse_search_query_result_promote_batch_payload(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    if not promotion_rows:
        promotion_rows = [
            {
                "candidate_id": _text(candidate_id),
                "option_index": int(option_index or 0),
                "notes": "",
                "promotion_format": "visible_batch",
            }
            for candidate_id, option_index in zip(
                list(batch_plan.get("candidate_ids", []) or []),
                [
                    int(row.get("current_option_index", 0) or 0)
                    for row in list(batch_plan.get("rows", []) or [])
                ],
            )
            if _text(candidate_id) and int(option_index or 0) > 0
        ]
    if not promotion_rows:
        return jsonify({"ok": False, "error": "no imported result options are available for batch promotion"}), 400

    seen_ids: set[str] = set()
    for row in promotion_rows:
        candidate_id = _text(row.get("candidate_id"))
        if candidate_id in seen_ids:
            return jsonify({"ok": False, "error": f"duplicate candidate_id in batch: {candidate_id}"}), 400
        seen_ids.add(candidate_id)

    results: list[dict[str, Any]] = []
    last_result: dict[str, Any] = {}
    for row in promotion_rows:
        try:
            last_result = _promote_search_query_result_option(
                run_id=run_id,
                candidate_id=_text(row.get("candidate_id")),
                option_index=int(row.get("option_index", 0) or 0),
                notes_override=_text(row.get("notes")),
            )
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400
        results.append(
            {
                "candidate_id": _text(row.get("candidate_id")),
                "selected_option": dict(last_result.get("selected_option", {}) or {}),
                "updated_row": dict(last_result.get("updated_row", {}) or {}),
            }
        )

    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "summary": {
                "promoted_count": len(results),
                "promotion_formats": sorted(
                    {
                        _text(row.get("promotion_format")) or "structured_records"
                        for row in promotion_rows
                    }
                ),
            },
            "rows": results,
            "article_reference_store": dict(last_result.get("article_reference_store", {}) or {}),
            "accepted_discovery_candidate_bundle_manifest": dict(
                last_result.get("accepted_discovery_candidate_bundle_manifest", {}) or {}
            ),
            "reference_backed_promotion_manifest": dict(
                last_result.get("reference_backed_promotion_manifest", {}) or {}
            ),
            "knowledge_atom_refresh_summary": dict(
                last_result.get("knowledge_atom_refresh_summary", {}) or {}
            ),
            "combination_rerank_summary": dict(
                last_result.get("combination_rerank_summary", {}) or {}
            ),
            "licensed_research": dict(last_result.get("licensed_research", {}) or {}),
            "congruence_brain": dict(last_result.get("congruence_brain", {}) or {}),
        }
    )


@app.route("/api/search-query-result-promote-and-resolve-batch", methods=["POST"])
def api_search_query_result_promote_and_resolve_batch():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    try:
        resolution_rows = _parse_search_query_result_resolve_batch_payload(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    if not resolution_rows:
        return jsonify({"ok": False, "error": "no imported result resolutions were provided"}), 400

    seen_ids: set[str] = set()
    results: list[dict[str, Any]] = []
    last_result: dict[str, Any] = {}
    for row in resolution_rows:
        candidate_id = _text(row.get("candidate_id"))
        if candidate_id in seen_ids:
            return jsonify({"ok": False, "error": f"duplicate candidate_id in batch: {candidate_id}"}), 400
        seen_ids.add(candidate_id)
        try:
            last_result = _resolve_search_query_result_option_with_excerpt(
                run_id=run_id,
                candidate_id=candidate_id,
                option_index=int(row.get("option_index", 0) or 0),
                reference_excerpt=_text(row.get("reference_excerpt")),
                notes_override=_text(row.get("notes")),
                auto_accept_discovery_candidate=bool(data.get("auto_accept_discovery_candidate", True)),
            )
        except ValueError as exc:
            return jsonify({"ok": False, "error": str(exc)}), 400
        results.append(
            {
                "candidate_id": candidate_id,
                "selected_option": dict(last_result.get("selected_option", {}) or {}),
                "updated_row": dict(last_result.get("updated_row", {}) or {}),
            }
        )

    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "summary": {
                "resolved_count": len(results),
                "resolution_formats": sorted(
                    {
                        _text(row.get("resolution_format")) or "structured_records"
                        for row in resolution_rows
                    }
                ),
            },
            "rows": results,
            "article_reference_store": dict(last_result.get("article_reference_store", {}) or {}),
            "accepted_discovery_candidate_bundle_manifest": dict(
                last_result.get("accepted_discovery_candidate_bundle_manifest", {}) or {}
            ),
            "reference_backed_promotion_manifest": dict(
                last_result.get("reference_backed_promotion_manifest", {}) or {}
            ),
            "knowledge_atom_refresh_summary": dict(
                last_result.get("knowledge_atom_refresh_summary", {}) or {}
            ),
            "combination_rerank_summary": dict(
                last_result.get("combination_rerank_summary", {}) or {}
            ),
            "licensed_research": dict(last_result.get("licensed_research", {}) or {}),
            "congruence_brain": dict(last_result.get("congruence_brain", {}) or {}),
        }
    )


@app.route("/api/search-query-execution-materialize", methods=["POST"])
def api_search_query_execution_materialize():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400

    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404

    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    session_bundle = _build_search_query_execution_session_bundle(
        batch_plan=dict(licensed.get("search_query_execution_batch_plan", {}) or {}),
        rows=list(licensed.get("search_query_execution_register", []) or []),
    )
    manifest = _persist_search_query_execution_manifest(
        run_id,
        {
            "summary": dict(licensed.get("search_query_execution_summary", {}) or {}),
            "batch_plan": dict(licensed.get("search_query_execution_batch_plan", {}) or {}),
            "session_bundle": session_bundle,
            "rows": list(licensed.get("search_query_execution_register", []) or []),
            "current_row": dict(licensed.get("current_search_query_execution_row", {}) or {}),
            "next_rows": list(licensed.get("next_search_query_execution_rows", []) or []),
        },
    )
    refreshed = _congruence_brain_activity(run_d)
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "search_query_execution_manifest": manifest,
            "licensed_research": dict(refreshed.get("licensed_research", {}) or {}),
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/search-query-execution-session-save", methods=["POST"])
def api_search_query_execution_session_save():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    try:
        session_rows = _parse_search_query_execution_session_payload(data)
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    store = _persist_search_query_execution_session_store(run_id, session_rows)
    run_d = _load_run(run_id)
    refreshed = _congruence_brain_activity(run_d or {"run_id": run_id})
    session_bundle = dict(refreshed.get("search_query_execution_session_bundle", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "search_query_execution_session_store": {
                "updated_at": _text(store.get("updated_at")),
                "path": _text(store.get("path")),
                "stored_row_count": len(list(store.get("rows", []) or [])),
                "exists": bool(store.get("exists")),
            },
            "session_bundle": session_bundle,
            "licensed_research": dict((refreshed.get("licensed_research", {}) if refreshed else {}) or {}),
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/search-query-execution-session-parse-row", methods=["POST"])
def api_search_query_execution_session_parse_row():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    row_text = data.get("row_text")
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    if not _text(row_text):
        return jsonify({"ok": False, "error": "row_text is required"}), 400

    run_d = _load_run(run_id)
    refreshed = _congruence_brain_activity(run_d or {"run_id": run_id})
    session_bundle = dict(refreshed.get("search_query_execution_session_bundle", {}) or {})
    session_rows = [
        dict(row)
        for row in list(session_bundle.get("rows", []) or [])
        if _text(row.get("candidate_id")) == candidate_id
    ]
    if not session_rows:
        return jsonify({"ok": False, "error": f"candidate not found in search session: {candidate_id}"}), 404
    provider_capture_guide = dict(
        session_bundle.get("ordered_result_import_provider_capture_guide", {})
        or {}
    )
    try:
        parsed_row = _parse_search_query_execution_session_row_text(
            candidate_id=candidate_id,
            row_text=row_text,
            provider_capture_guide=provider_capture_guide,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    merged_row = dict(session_rows[0] or {})
    merged_row.update(
        {
            "source_url": _text(parsed_row.get("source_url")),
            "search_result_title": _text(parsed_row.get("search_result_title")),
            "search_result_snippet": _text(parsed_row.get("search_result_snippet")),
            "reference_excerpt": _text(parsed_row.get("reference_excerpt")),
            "notes": _text(parsed_row.get("notes")),
            "selected": bool(parsed_row.get("selected")),
        }
    )
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "candidate_id": candidate_id,
            "parsed_row": parsed_row,
            "merged_row": merged_row,
            "provider_capture_guide": provider_capture_guide,
        }
    )


@app.route("/api/search-query-execution-session-import", methods=["POST"])
def api_search_query_execution_session_import():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    auto_capture_singleton_candidates = bool(data.get("auto_capture_singleton_candidates", False))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    refreshed = _congruence_brain_activity(run_d or {"run_id": run_id})
    session_bundle = dict(refreshed.get("search_query_execution_session_bundle", {}) or {})
    session_rows = list(session_bundle.get("rows", []) or [])
    ready_rows = [
        dict(row)
        for row in session_rows
        if _is_search_query_execution_session_row_ready(row)
    ]
    if not ready_rows:
        return jsonify({"ok": False, "error": "no ready search session rows were found"}), 400
    try:
        parsed_blocks = _parse_search_query_execution_session_rows(ready_rows)
        payload = _apply_search_query_result_import_blocks(
            run_id=run_id,
            parsed_blocks=parsed_blocks,
            auto_capture_singleton_candidates=auto_capture_singleton_candidates,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    payload["search_query_execution_session_store"] = dict(
        (payload.get("licensed_research", {}) or {}).get("search_query_execution_session_store", {})
        or {}
    )
    payload["session_bundle"] = dict(
        (payload.get("congruence_brain", {}) or {}).get("search_query_execution_session_bundle", {})
        or {}
    )
    return jsonify(payload)


@app.route("/api/article-reference-resolve-packet", methods=["POST"])
def api_article_reference_resolve_packet():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    candidate_id = _text(data.get("candidate_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    if not candidate_id:
        return jsonify({"ok": False, "error": "candidate_id is required"}), 400
    try:
        packet = _parse_reference_resolution_packet(data.get("resolution_packet"), require_url=False)
        manifest = _load_licensed_discovery_queue_manifest(run_id)
        rows = list(manifest.get("candidate_rows", []) or [])
        candidate_row = next((dict(row) for row in rows if _text(row.get("candidate_id")) == candidate_id), {})
        if not candidate_row:
            return jsonify({"ok": False, "error": "candidate not found in imported queue"}), 400
        current_store = _load_article_reference_record_store(run_id)
        current_records = {
            _text(row.get("candidate_id")): dict(row)
            for row in list(current_store.get("records", []) or [])
            if _text(row.get("candidate_id"))
        }
        hydrated_patch = _hydrate_reference_resolution_patch(
            candidate_row=candidate_row,
            reference_record=current_records.get(candidate_id, {}),
            patch={
                **packet,
                "reference_state": "manual_text_enriched",
            },
        )
        edit_record = _normalize_article_reference_edit_record(
            {
                "candidate_id": candidate_id,
                "auto_accept_discovery_candidate": data.get("auto_accept_discovery_candidate", True),
                "patch": hydrated_patch,
            }
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    try:
        result = _execute_article_reference_edit(
            run_id=run_id,
            candidate_id=candidate_id,
            edit_record=edit_record,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400
    return jsonify(
        {
            "ok": True,
            **result,
        }
    )


@app.route("/api/article-reference-resolve-batch", methods=["POST"])
def api_article_reference_resolve_batch():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    try:
        parsed_blocks = _parse_reference_resolution_batch_payload(
            data,
            require_url=False,
        )
    except ValueError as exc:
        return jsonify({"ok": False, "error": str(exc)}), 400

    manifest = _load_licensed_discovery_queue_manifest(run_id)
    candidate_rows = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(manifest.get("candidate_rows", []) or [])
        if _text(row.get("candidate_id"))
    }
    current_store = _load_article_reference_record_store(run_id)
    current_records = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(current_store.get("records", []) or [])
        if _text(row.get("candidate_id"))
    }
    seen_ids: set[str] = set()
    for block in parsed_blocks:
        candidate_id = _text(block.get("candidate_id"))
        if candidate_id in seen_ids:
            return jsonify({"ok": False, "error": f"duplicate candidate_id in batch: {candidate_id}"}), 400
        seen_ids.add(candidate_id)
        if candidate_id not in candidate_rows:
            return jsonify({"ok": False, "error": f"candidate not found in imported queue: {candidate_id}"}), 400

    auto_accept = bool(data.get("auto_accept_discovery_candidate", True))
    results: list[dict[str, Any]] = []
    last_result: dict[str, Any] = {}
    for block in parsed_blocks:
        candidate_id = _text(block.get("candidate_id"))
        hydrated_patch = _hydrate_reference_resolution_patch(
            candidate_row=candidate_rows.get(candidate_id, {}),
            reference_record=current_records.get(candidate_id, {}),
            patch={
                **block,
                "reference_state": "manual_text_enriched",
            },
        )
        edit_record = _normalize_article_reference_edit_record(
            {
                "candidate_id": candidate_id,
                "auto_accept_discovery_candidate": auto_accept,
                "patch": hydrated_patch,
            }
        )
        last_result = _execute_article_reference_edit(
            run_id=run_id,
            candidate_id=candidate_id,
            edit_record=edit_record,
        )
        results.append(
            {
                "candidate_id": candidate_id,
                "updated_row": dict(last_result.get("updated_row", {}) or {}),
            }
        )

    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "summary": {
                "resolved_count": len(results),
                "resolution_formats": sorted(
                    {
                        _text(block.get("resolution_format")) or "packet"
                        for block in parsed_blocks
                    }
                ),
            },
            "rows": results,
            "article_reference_store": dict(last_result.get("article_reference_store", {}) or {}),
            "accepted_discovery_candidate_bundle_manifest": dict(
                last_result.get("accepted_discovery_candidate_bundle_manifest", {}) or {}
            ),
            "reference_backed_promotion_manifest": dict(
                last_result.get("reference_backed_promotion_manifest", {}) or {}
            ),
            "knowledge_atom_refresh_summary": dict(
                last_result.get("knowledge_atom_refresh_summary", {}) or {}
            ),
            "combination_rerank_summary": dict(
                last_result.get("combination_rerank_summary", {}) or {}
            ),
            "licensed_research": dict(last_result.get("licensed_research", {}) or {}),
            "congruence_brain": dict(last_result.get("congruence_brain", {}) or {}),
        }
    )


@app.route("/api/article-reference-read-batch", methods=["POST"])
def api_article_reference_read_batch():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    congruence_brain = _congruence_brain_activity(run_d or {"run_id": run_id})
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    review_rows = list(licensed.get("discovery_candidate_review_register", []) or [])
    accepted_ids = {
        _text(row.get("candidate_id"))
        for row in review_rows
        if _text(row.get("operator_decision")) == "accepted_for_reference_use" and _text(row.get("candidate_id"))
    }
    requested_ids = {
        _text(candidate_id)
        for candidate_id in list(data.get("candidate_ids", []) or [])
        if _text(candidate_id)
    }
    target_ids = sorted(accepted_ids & requested_ids) if requested_ids else sorted(accepted_ids)
    if not target_ids:
        return jsonify({"ok": False, "error": "no accepted discovery candidates for this run"}), 400
    manifest = _load_licensed_discovery_queue_manifest(run_id)
    candidate_rows = {
        _text(row.get("candidate_id")): dict(row)
        for row in list(manifest.get("candidate_rows", []) or [])
        if _text(row.get("candidate_id"))
    }
    batch_rows: list[dict[str, Any]] = []
    for candidate_id in target_ids:
        candidate_row = dict(candidate_rows.get(candidate_id, {}) or {})
        if not candidate_row:
            batch_rows.append(
                {
                    "candidate_id": candidate_id,
                    "reference_state": "metadata_only",
                    "status": "error",
                    "error": "candidate_not_found_in_manifest",
                }
            )
            continue
        reference_result = _read_article_reference_for_candidate(run_id=run_id, candidate_row=candidate_row)
        reference_record = dict(reference_result.get("reference_record", {}) or {})
        batch_rows.append(
            {
                "candidate_id": candidate_id,
                "reference_state": _text(reference_record.get("reference_state")) or "metadata_only",
                "status": _text(((reference_record.get("acquisition_result", {}) or {}).get("status"))) or "ok",
                "error": _text(((reference_record.get("acquisition_result", {}) or {}).get("error"))),
            }
        )
    auto_refresh = _refresh_reference_backed_promotions_state(
        run_id=run_id,
        run_d=run_d or {"run_id": run_id},
    )
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    refreshed_licensed = dict(auto_refresh.get("licensed", {}) or {})
    accepted_bundle_manifest = dict(auto_refresh.get("accepted_bundle_manifest", {}) or {})
    summary = {
        "attempted_count": len(batch_rows),
        "visible_text_enriched_count": sum(1 for row in batch_rows if _reference_state_has_text(row.get("reference_state"))),
        "metadata_only_count": sum(1 for row in batch_rows if _text(row.get("reference_state")) == "metadata_only"),
        "error_count": sum(1 for row in batch_rows if _text(row.get("status")) == "error"),
    }
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "summary": summary,
            "rows": batch_rows,
            "accepted_discovery_candidate_bundle_manifest": accepted_bundle_manifest,
            "reference_backed_promotion_manifest": dict(auto_refresh.get("reference_backed_promotion_manifest", {}) or {}),
            "knowledge_atom_refresh_summary": dict(auto_refresh.get("knowledge_atom_refresh_summary", {}) or {}),
            "combination_rerank_summary": dict(auto_refresh.get("combination_rerank_summary", {}) or {}),
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/accepted-discovery-candidates")
def api_accepted_discovery_candidates():
    run_id = _text(request.args.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    bundle = dict(licensed.get("accepted_discovery_candidate_bundle", {}) or {})
    manifest = dict(licensed.get("accepted_discovery_candidate_bundle_manifest", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "accepted_discovery_candidate_bundle": bundle,
            "accepted_discovery_candidate_bundle_manifest": manifest,
        }
    )


@app.route("/api/reference-backed-promotions-refresh", methods=["POST"])
def api_reference_backed_promotions_refresh():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    auto_refresh = _refresh_reference_backed_promotions_state(
        run_id=run_id,
        run_d=run_d,
    )
    refreshed = dict(auto_refresh.get("refreshed", {}) or {})
    refreshed_licensed = dict(auto_refresh.get("licensed", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "reference_backed_promotion_manifest": dict(auto_refresh.get("reference_backed_promotion_manifest", {}) or {}),
            "knowledge_atom_refresh_summary": dict(auto_refresh.get("knowledge_atom_refresh_summary", {}) or {}),
            "combination_rerank_summary": dict(auto_refresh.get("combination_rerank_summary", {}) or {}),
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/registry-review-bundle")
def api_registry_review_bundle():
    run_id = _text(request.args.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    bundle = dict(licensed.get("registry_review_bundle", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "registry_review_bundle": bundle,
        }
    )


@app.route("/api/registry-stage-preview")
def api_registry_stage_preview():
    run_id = _text(request.args.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    preview = dict(licensed.get("registry_stage_preview", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "registry_stage_preview": preview,
        }
    )


@app.route("/api/registry-stage-materialize", methods=["POST"])
def api_registry_stage_materialize():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    registry_review_bundle = dict(licensed.get("registry_review_bundle", {}) or {})
    registry_stage_preview = dict(licensed.get("registry_stage_preview", {}) or {})
    if not list(registry_stage_preview.get("stage_rows", []) or []):
        return jsonify({"ok": False, "error": "no stage rows available for this run"}), 400
    manifest = _materialize_registry_stage_candidates(
        run_id=run_id,
        registry_review_bundle=registry_review_bundle,
        registry_stage_preview=registry_stage_preview,
    )
    refreshed = _congruence_brain_activity(run_d)
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "registry_stage_candidate_manifest": manifest,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/registry-stage-merge", methods=["POST"])
def api_registry_stage_merge():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    stage_manifest = _load_registry_stage_candidate_manifest(run_id)
    if not bool(stage_manifest.get("exists")):
        return jsonify({"ok": False, "error": "registry stage candidate manifest not found"}), 404
    if not list(stage_manifest.get("rows", []) or []):
        return jsonify({"ok": False, "error": "registry stage candidate manifest has no rows"}), 400
    merge_manifest = _merge_registry_stage_candidates_to_registry(
        run_id=run_id,
        registry_stage_candidate_manifest=stage_manifest,
    )
    run_d = _load_run(run_id)
    refreshed = _congruence_brain_activity(run_d) if run_d else {}
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {}) if refreshed else {}
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "registry_stage_merge_manifest": merge_manifest,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/provider-session-handoff")
def api_provider_session_handoff():
    run_id = _text(request.args.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    bundle = dict(licensed.get("provider_handoff_bundle", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "provider_handoff_bundle": bundle,
        }
    )


@app.route("/api/provider-session-handoff-materialize", methods=["POST"])
def api_provider_session_handoff_materialize():
    data = request.get_json() or {}
    run_id = _text(data.get("run_id"))
    if not run_id:
        return jsonify({"ok": False, "error": "run_id is required"}), 400
    run_d = _load_run(run_id)
    if not run_d:
        return jsonify({"ok": False, "error": "run not found"}), 404
    congruence_brain = _congruence_brain_activity(run_d)
    licensed = dict(congruence_brain.get("licensed_research", {}) or {})
    handoff_bundle = dict(licensed.get("provider_handoff_bundle", {}) or {})
    manifest = _materialize_provider_session_handoff(
        run_id=run_id,
        provider_handoff_bundle=handoff_bundle,
    )
    refreshed = _congruence_brain_activity(run_d)
    refreshed_licensed = dict(refreshed.get("licensed_research", {}) or {})
    return jsonify(
        {
            "ok": True,
            "run_id": run_id,
            "provider_session_handoff_manifest": manifest,
            "licensed_research": refreshed_licensed,
            "congruence_brain": refreshed,
        }
    )


@app.route("/api/serve-pdf/<path:pdf_path>")
def api_serve_pdf(pdf_path: str):
    full = Path("/" + pdf_path)
    if not full.exists() or full.suffix.lower() != ".pdf":
        return jsonify({"error": "no encontrado"}), 404
    return send_file(str(full), mimetype="application/pdf")


@app.route("/api/open-pdf/<path:pdf_path>")
def api_open_pdf(pdf_path: str):
    full = "/" + pdf_path
    if Path(full).exists():
        subprocess.Popen(["open", full])
        return jsonify({"ok": True})
    return jsonify({"ok": False})


@app.route("/api/start-run", methods=["POST"])
def api_start_run():
    data        = request.get_json() or {}
    pipeline_id = (data.get("pipeline_id") or "default").strip()
    inputs_file = _resolve_inputs_file(pipeline_id, (data.get("inputs_file") or "").strip())
    no_cache    = bool(data.get("no_cache", True))

    existing_runs = _runs_for_pipeline(pipeline_id)
    running_existing = next((r for r in existing_runs if r.get("status") == "running"), None)
    if running_existing is not None:
        return jsonify({
            "ok": True,
            "already_running": True,
            "pipeline_id": pipeline_id,
            "inputs_file": inputs_file,
            "no_cache": no_cache,
            "run_id": running_existing.get("run_id", ""),
            "message": "Ya existe un run activo para este target.",
        })

    cmd = [sys.executable, str(_HERE / "cli.py"), "run", f"--pipeline-id={pipeline_id}"]
    if inputs_file and Path(inputs_file).exists():
        cmd += [f"--inputs={inputs_file}"]
    if no_cache:
        cmd += ["--no-cache"]
    try:
        _LAUNCH_LOG_DIR.mkdir(parents=True, exist_ok=True)
        launch_started_at = time.time()
        known_run_ids = {r.get("run_id", "") for r in _runs_for_pipeline(pipeline_id)}
        log_path = _LAUNCH_LOG_DIR / f"{pipeline_id}_{int(launch_started_at)}.log"
        log_handle = open(log_path, "a", encoding="utf-8")
        proc = subprocess.Popen(
            cmd,
            cwd=str(_HERE),
            stdout=log_handle,
            stderr=subprocess.STDOUT,
        )
        log_handle.close()

        observed_run_id = ""
        deadline = time.time() + 5.0
        while time.time() < deadline:
            new_runs = [
                r for r in _runs_for_pipeline(pipeline_id)
                if r.get("run_id", "") not in known_run_ids
            ]
            if new_runs:
                observed_run_id = new_runs[0].get("run_id", "")
                break
            if proc.poll() is not None:
                break
            time.sleep(0.15)

        if not observed_run_id and proc.poll() is not None:
            return jsonify({
                "ok": False,
                "error": "El proceso terminó antes de registrar el run.",
                "pipeline_id": pipeline_id,
                "inputs_file": inputs_file,
                "launch_log": str(log_path),
                "log_tail": _tail_text(log_path),
                "returncode": proc.returncode,
            }), 500

        if not observed_run_id:
            return jsonify({
                "ok": False,
                "error": "No apareció un run nuevo en el registro dentro del tiempo esperado.",
                "pipeline_id": pipeline_id,
                "inputs_file": inputs_file,
                "launch_log": str(log_path),
                "log_tail": _tail_text(log_path),
                "pid": proc.pid,
            }), 500

        return jsonify({
            "ok": True,
            "pid": proc.pid,
            "pipeline_id": pipeline_id,
            "inputs_file": inputs_file,
            "no_cache": no_cache,
            "run_id": observed_run_id,
            "launch_log": str(log_path),
        })
    except Exception as e:
        return jsonify({"ok": False, "error": str(e)}), 500


@app.route("/api/create-target", methods=["POST"])
def api_create_target():
    data = request.get_json() or {}
    address = str(data.get("address") or "").strip()
    if not address:
        return jsonify({"ok": False, "error": "Address is required."}), 400
    target_type = str(data.get("target_type") or "commercial_building").strip() or "commercial_building"
    pipeline = build_address_seed(
        address_raw=address,
        target_type=target_type,
        owner_name=str(data.get("owner_name") or "").strip(),
        owner_ticker=str(data.get("owner_ticker") or "").strip(),
        owner_cik=str(data.get("owner_cik") or "").strip(),
        sector=str(data.get("sector") or "").strip(),
        sic=str(data.get("sic") or "").strip(),
        decision_intent=str(data.get("decision_intent") or "target_identification_required").strip(),
        report_intent="decision_admissibility_brief",
    )
    path = write_seed_file(_HERE / "inputs", pipeline, stem_hint=str(data.get("stem") or "").strip())
    target_definition = pipeline.get("target_definition_contract", {})
    year = str(pipeline.get("case_id", "")).split("-")[-1]
    pipeline_id = f"{target_definition.get('target_id', 'target')}-{year}"
    return jsonify({
        "ok": True,
        "pipeline_id": pipeline_id,
        "inputs_file": str(path),
        "target_id": target_definition.get("target_id", ""),
        "target_type": target_definition.get("target_type", ""),
        "target_label": target_definition.get("target_label", address),
    })
@app.route("/api/targets")
@app.route("/api/companies")
def api_targets():
    """Lista de target seeds físicos con su último run."""
    seeds = _target_seed_records()
    if not seeds:
        return jsonify([])
    runs = _all_runs()
    # Indexar runs por pipeline_id
    run_by_pid: dict = {}
    for r in runs:
        if not r.get("is_full_framework_run"):
            continue
        pid = r.get("pipeline_id", "")
        if pid not in run_by_pid:
            run_by_pid[pid] = r
    result = []
    for seed in seeds:
        pid_key = seed.get("pipeline_id", "")
        aliases = [pid_key, *seed.get("pipeline_aliases", [])]
        run = next((run_by_pid.get(alias) for alias in aliases if run_by_pid.get(alias)), None)
        inp_file = Path(seed.get("inputs_file", ""))
        run_pdf = _pdf_for_run(_load_run(run.get("run_id", "")), allow_global_fallback=False) if run else None
        last_run_status = run.get("status") if run else None
        result.append({
            "ticker":      seed.get("ticker", ""),
            "name":        seed.get("target_label", pid_key),
            "target_label": seed.get("target_label", pid_key),
            "target_address": seed.get("target_address", ""),
            "target_type": seed.get("target_type", ""),
            "target_id": seed.get("target_id", ""),
            "target_slug": seed.get("target_slug", ""),
            "subject_kind": seed.get("subject_kind", ""),
            "owner_name": seed.get("owner_name", ""),
            "target_code": seed.get("target_code", ""),
            "sector":      seed.get("context_line", ""),
            "has_inputs":  inp_file.exists(),
            "last_run":    last_run_status,
            "last_run_display_status": _display_status(last_run_status or "unknown", pdf_available=run_pdf is not None) if run else "not_started",
            "last_run_report_ready": bool(run_pdf),
            "last_run_id": run.get("run_id") if run else None,
            "pipeline_id": pid_key,
            "pipeline_aliases": seed.get("pipeline_aliases", []),
            "inputs_file": str(inp_file) if inp_file.exists() else "",
        })
    return jsonify(result)


@app.route("/api/financials/<run_id>")
def api_financials(run_id: str):
    """Compat: devuelve research + charts en vez de la vista financiera vieja."""
    raw_run = _load_run(run_id)
    company = _company_info(raw_run)
    return jsonify({
        "company": company,
        "research": _research_activity(raw_run),
        "charts": _chart_activity(raw_run),
    })


@app.route("/api/source-refresh")
def api_source_refresh():
    return jsonify(_source_refresh_status())


@app.route("/api/source-refresh/control", methods=["POST"])
def api_source_refresh_control():
    return jsonify({
        "ok": False,
        "enabled": False,
        "mode": "manual_only",
        "error": "El refresco automático está desactivado. El análisis solo se ejecuta manualmente por target.",
    }), 403


# ── HTML ──────────────────────────────────────────────────────────────────────

_HTML = r"""<!DOCTYPE html>
<html lang="es">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>ZLab — Monitor</title>
<style>
:root{
  --bg:#f7f7f8;--surface:#fff;--border:#e4e4e7;--text:#18181b;--text2:#3f3f46;
  --muted:#71717a;--faint:#a1a1aa;--accent:#2563eb;--green:#16a34a;
  --red:#dc2626;--amber:#b45309;
  --blue-bg:#eff6ff;--green-bg:#f0fdf4;--red-bg:#fef2f2;--amber-bg:#fffbeb;
  --blue-bd:#bfdbfe;--green-bd:#bbf7d0;--red-bd:#fecaca;--amber-bd:#fde68a;
}
*,*::before,*::after{box-sizing:border-box;margin:0;padding:0;}
body{background:var(--bg);color:var(--text);font-family:-apple-system,BlinkMacSystemFont,"SF Pro Text","Segoe UI",sans-serif;font-size:13px;line-height:1.5;}

/* ── Header ── */
#hdr{position:sticky;top:0;z-index:20;height:48px;padding:0 16px;
  background:rgba(255,255,255,.94);backdrop-filter:blur(12px);
  border-bottom:1px solid var(--border);
  display:flex;align-items:center;justify-content:space-between;}
.logo{font-size:14px;font-weight:700;letter-spacing:-.3px;}
.logo-sub{font-size:12px;color:var(--muted);font-weight:400;}
#hdr-right{display:flex;align-items:center;gap:8px;}
.pill{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;border-radius:20px;
  font-size:11px;font-weight:500;border:1px solid var(--border);background:var(--surface);color:var(--muted);}
.pill .dot{width:6px;height:6px;border-radius:50%;background:var(--faint);}
.pill.running{border-color:var(--blue-bd);color:var(--accent);background:var(--blue-bg);}
.pill.running .dot{background:var(--accent);animation:blink 1.4s infinite;}
.pill.done{border-color:var(--green-bd);color:var(--green);background:var(--green-bg);}
.pill.done .dot{background:var(--green);}
.pill.warn{border-color:var(--amber-bd);color:var(--amber);background:var(--amber-bg);}
.pill.warn .dot{background:var(--amber);}
.pill.fail{border-color:var(--red-bd);color:var(--red);background:var(--red-bg);}
.pill.fail .dot{background:var(--red);}
@keyframes blink{0%,100%{opacity:1}50%{opacity:.3}}

/* ── Layout ── */
#body{display:flex;height:calc(100vh - 48px);overflow:hidden;}

/* Sidebar targets */
#sidebar{width:240px;flex-shrink:0;border-right:1px solid var(--border);
  background:var(--surface);display:flex;flex-direction:column;overflow:hidden;}
#sb-hdr{padding:12px 14px;border-bottom:1px solid var(--border);flex-shrink:0;}
#sb-hdr .sb-title{font-size:10.5px;font-weight:700;text-transform:uppercase;
  letter-spacing:.07em;color:var(--muted);margin-bottom:8px;}
#sb-search{width:100%;padding:6px 10px;border:1px solid var(--border);border-radius:7px;
  font-size:12px;background:var(--bg);color:var(--text);outline:none;}
#sb-search:focus{border-color:var(--accent);}
#sb-list{flex:1;overflow-y:auto;}
.sb-item{padding:9px 14px;border-bottom:1px solid #f4f4f5;cursor:pointer;
  transition:background .1s;display:flex;align-items:center;gap:8px;}
.sb-item:hover{background:var(--bg);}
.sb-item.active{background:var(--blue-bg);border-left:3px solid var(--accent);}
.sb-code{font-size:10px;font-weight:700;color:var(--muted);width:38px;flex-shrink:0;
  letter-spacing:.08em;text-transform:uppercase;}
.sb-info{flex:1;min-width:0;}
.sb-name{font-size:12px;font-weight:500;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sb-sector{font-size:10px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.sb-meta{font-size:10px;color:var(--faint);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:1px;}
.sb-status{width:7px;height:7px;border-radius:50%;flex-shrink:0;}
.ss-done{background:var(--green);}
.ss-partial{background:var(--amber);}
.ss-failed{background:var(--red);}
.ss-pending{background:var(--faint);}
.ss-running{background:var(--accent);animation:blink 1s infinite;}
#sb-footer{padding:10px 14px;border-top:1px solid var(--border);flex-shrink:0;}

/* Main content */
#main{flex:1;min-width:0;display:flex;flex-direction:column;overflow:hidden;}

/* Hero target */
#hero{padding:18px 20px 14px;border-bottom:1px solid var(--border);
  background:var(--surface);display:flex;align-items:flex-start;
  justify-content:space-between;gap:16px;flex-shrink:0;}
#hero-left{flex:1;min-width:0;}
#hero-tag{font-size:10px;font-weight:600;text-transform:uppercase;letter-spacing:.08em;
  color:var(--faint);margin-bottom:4px;}
#hero-name{font-size:32px;font-weight:800;letter-spacing:-1px;line-height:1.1;
  white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
#hero-sub{font-size:13px;color:var(--muted);margin-top:5px;}
#hero-badge{margin-top:8px;display:flex;align-items:center;gap:8px;flex-wrap:wrap;}
#hero-right{display:flex;gap:8px;align-items:flex-start;flex-shrink:0;}
#btn-run{padding:11px 22px;background:var(--text);color:#fff;border:none;
  border-radius:8px;font-size:13px;font-weight:700;cursor:pointer;white-space:nowrap;}
#btn-run:hover{opacity:.84;}
#btn-run:disabled{opacity:.4;cursor:not-allowed;}
.e-badge{display:inline-flex;align-items:center;gap:5px;padding:3px 10px;
  border-radius:20px;font-size:11px;font-weight:600;}
.eb-running{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);}
.eb-done{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
.eb-failed{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}
.eb-stub{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.eb-failed{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}
.eb-warn{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.eb-idle{background:#f4f4f5;color:var(--muted);border:1px solid var(--border);}

/* Content area */
#content{flex:1;overflow-y:auto;padding:18px 20px;display:flex;flex-direction:column;gap:14px;}

/* Cards */
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:16px 18px;}
.card-title{font-size:10.5px;font-weight:600;text-transform:uppercase;letter-spacing:.07em;
  color:var(--muted);margin-bottom:12px;}
.card-hdr{display:flex;align-items:baseline;justify-content:space-between;margin-bottom:12px;}
.card-sub{font-size:11px;color:var(--muted);}

.stats-grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(120px,1fr));gap:10px;margin-bottom:14px;}
.stat-card{background:var(--bg);border:1px solid var(--border);border-radius:8px;padding:10px 12px;}
.stat-val{font-size:18px;font-weight:800;letter-spacing:-.03em;}
.stat-lbl{font-size:10.5px;color:var(--muted);margin-top:2px;text-transform:uppercase;letter-spacing:.05em;}

/* Motores */
.prog-track{height:5px;background:#f0f0f0;border-radius:3px;overflow:hidden;margin-bottom:10px;}
.prog-fill{height:100%;border-radius:3px;transition:width .6s;}
.prog-fill.s-running{background:linear-gradient(90deg,var(--accent),#60a5fa);animation:shimmer 2s infinite;}
.prog-fill.s-done{background:var(--green);}
.prog-fill.s-partial{background:var(--amber);}
.prog-fill.s-failed{background:var(--red);}
.prog-fill.s-failed{background:var(--red);}
@keyframes shimmer{0%,100%{opacity:1}50%{opacity:.7}}
.prog-row{display:flex;justify-content:space-between;font-size:12px;color:var(--muted);margin-bottom:6px;}
.motor-dots{display:flex;flex-wrap:wrap;gap:4px;}
.mdot{width:26px;height:26px;border-radius:6px;display:flex;align-items:center;
  justify-content:center;font-size:8.5px;font-weight:700;cursor:default;
  transition:transform .12s;position:relative;user-select:none;}
.mdot:hover{transform:scale(1.4);z-index:10;}
.mdot::after{content:attr(data-tip);position:absolute;bottom:115%;left:50%;
  transform:translateX(-50%);background:var(--text);color:#fff;white-space:nowrap;
  font-size:10px;padding:3px 8px;border-radius:5px;opacity:0;pointer-events:none;transition:opacity .12s;}
.mdot:hover::after{opacity:1;}
.md-completed{background:#dcfce7;color:#15803d;}
.md-cached{background:#dbeafe;color:#1d4ed8;}
.md-stub{background:#fef9c3;color:#a16207;}
.md-failed{background:#fee2e2;color:var(--red);}
.md-running{background:#dbeafe;color:var(--accent);animation:blink 1s infinite;}
.md-missing{background:#f4f4f5;color:var(--faint);}
.md-unknown{background:#f4f4f5;color:var(--faint);}

/* Fuentes */
.sources-grid{display:grid;grid-template-columns:1fr 1fr;gap:7px;}
.src-item{display:flex;align-items:flex-start;gap:8px;padding:9px 11px;
  border-radius:7px;background:#fafafa;border:1px solid var(--border);}
.src-dot{width:7px;height:7px;border-radius:50%;flex-shrink:0;margin-top:3px;}
.sd-found{background:var(--green);}
.sd-ok{background:var(--green);}
.sd-no_data{background:var(--amber);}
.sd-untracked{background:var(--faint);}
.sd-enriched{background:var(--accent);}
.sd-proposed{background:var(--faint);}
.sd-failed{background:var(--red);}
.src-body{flex:1;min-width:0;}
.src-name{font-size:12px;font-weight:600;}
.src-val{font-size:11px;color:var(--muted);margin-top:1px;}
.src-meta{font-size:10.5px;color:var(--faint);margin-top:2px;line-height:1.4;}

.chart-list{display:grid;grid-template-columns:1fr 1fr;gap:8px;}
.chart-item{padding:10px 12px;border-radius:8px;background:#fafafa;border:1px solid var(--border);}
.chart-name{font-size:12px;font-weight:700;}
.chart-meta{font-size:10.5px;color:var(--muted);margin-top:2px;line-height:1.4;}

.brain-list{display:grid;grid-template-columns:1fr;gap:9px;}
.brain-item{padding:12px 14px;border-radius:8px;background:#fafafa;border:1px solid var(--border);}
.brain-editor-wrap{margin-top:10px;border:1px dashed var(--border);border-radius:8px;background:#fff;padding:10px 12px;}
.brain-editor-wrap summary{cursor:pointer;font-weight:700;color:var(--text);}
.brain-editor-meta{margin-top:8px;font-size:12px;color:var(--muted);}
.brain-editor-area{width:100%;min-height:220px;margin-top:10px;border:1px solid var(--border);border-radius:8px;padding:10px 12px;font:12px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;color:var(--text);background:#fcfcfc;resize:vertical;}
.brain-session-grid{display:grid;grid-template-columns:1fr;gap:10px;margin-top:10px;}
.brain-session-row{border:1px solid var(--border);border-radius:8px;background:#fcfcfc;padding:10px 12px;}
.brain-session-row-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;}
.brain-session-row-name{font-size:12px;font-weight:700;color:var(--text);}
.brain-session-row-meta{font-size:10.5px;color:var(--muted);margin-top:3px;line-height:1.45;}
.brain-session-fields{display:grid;grid-template-columns:1fr 1fr;gap:8px;margin-top:10px;}
.brain-session-field{display:flex;flex-direction:column;gap:4px;}
.brain-session-field.wide{grid-column:1 / -1;}
.brain-session-field label{font-size:10.5px;font-weight:700;color:var(--muted);}
.brain-session-field input[type="text"],.brain-session-field textarea{width:100%;border:1px solid var(--border);border-radius:7px;padding:7px 9px;font-size:11px;color:var(--text);background:#fff;}
.brain-session-field textarea{min-height:72px;resize:vertical;font:11px/1.45 ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;}
.brain-session-check{display:flex;align-items:center;gap:6px;font-size:11px;color:var(--text2);margin-top:2px;}
.brain-head{display:flex;justify-content:space-between;align-items:flex-start;gap:10px;}
.brain-name{font-size:12.5px;font-weight:700;}
.brain-state{display:inline-block;padding:3px 8px;border-radius:20px;font-size:10px;font-weight:700;border:1px solid var(--border);background:#fff;color:var(--text2);}
.brain-state.accepted_for_case_use{background:var(--green-bg);color:var(--green);border-color:var(--green-bd);}
.brain-state.rejected_for_case_use{background:var(--red-bg);color:var(--red);border-color:var(--red-bd);}
.brain-state.needs_review{background:var(--amber-bg);color:var(--amber);border-color:var(--amber-bd);}
.brain-state.candidate{background:var(--blue-bg);color:var(--accent);border-color:var(--blue-bd);}
.brain-meta{font-size:11px;color:var(--muted);margin-top:5px;line-height:1.5;}
.brain-tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:8px;}
.brain-tag{display:inline-flex;align-items:center;padding:3px 8px;border-radius:999px;background:#fff;border:1px solid var(--border);font-size:10px;color:var(--text2);}
.brain-actions{display:flex;flex-wrap:wrap;gap:7px;margin-top:10px;}
.brain-btn{border:1px solid var(--border);background:#fff;color:var(--text2);padding:6px 10px;border-radius:7px;font-size:11px;font-weight:700;cursor:pointer;}
.brain-btn:hover{background:#f4f4f5;}
.brain-btn.accept{border-color:var(--green-bd);color:var(--green);}
.brain-btn.reject{border-color:var(--red-bd);color:var(--red);}
.brain-btn.review{border-color:var(--amber-bd);color:var(--amber);}

/* Auditoría */
.audit-ok{display:flex;align-items:center;gap:10px;padding:12px 14px;
  background:var(--green-bg);border:1px solid var(--green-bd);border-radius:8px;
  font-size:13px;font-weight:500;color:var(--green);}
.audit-fail{padding:11px 14px;border-radius:8px;margin-bottom:8px;border-left:3px solid;}
.af-error{border-color:var(--red);background:var(--red-bg);}
.af-warning{border-color:var(--amber);background:var(--amber-bg);}
.af-type{font-size:10.5px;font-weight:700;text-transform:uppercase;margin-bottom:3px;}
.af-error .af-type{color:var(--red);}
.af-warning .af-type{color:var(--amber);}
.af-msg{font-size:12px;color:var(--text2);}

/* LLM */
.llm-note{font-size:12px;color:var(--accent);background:var(--blue-bg);
  border:1px solid var(--blue-bd);border-radius:7px;padding:9px 12px;margin-bottom:10px;}
.llm-table{width:100%;border-collapse:collapse;}
.llm-table tr{border-bottom:1px solid #f4f4f5;}
.llm-table tr:last-child{border-bottom:none;}
.llm-table td{padding:8px 6px;vertical-align:top;}
.lt-num{font-size:10px;font-family:monospace;color:var(--faint);width:36px;padding-top:10px;}
.lt-label{font-size:12.5px;font-weight:600;}
.lt-snippet{font-size:11px;color:var(--muted);margin-top:2px;line-height:1.5;
  display:-webkit-box;-webkit-line-clamp:2;-webkit-box-orient:vertical;overflow:hidden;}
.lt-status{text-align:right;padding-top:8px;}
.st-badge{display:inline-block;padding:2px 8px;border-radius:20px;font-size:10px;font-weight:700;white-space:nowrap;}
.st-completed{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
.st-completed_real{background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
.st-cached{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);}
.st-cached_real{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);}
.st-running{background:var(--blue-bg);color:var(--accent);border:1px solid var(--blue-bd);animation:blink 1s infinite;}
.st-stub{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.st-cached_stub,.st-completed_stub{background:var(--amber-bg);color:var(--amber);border:1px solid var(--amber-bd);}
.st-failed{background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}
.st-pending,.st-missing,.st-skipped{background:#f4f4f5;color:var(--faint);border:1px solid var(--border);}

/* PDF panel */
#right{width:38%;max-width:520px;min-width:240px;border-left:1px solid var(--border);
  background:var(--surface);display:flex;flex-direction:column;flex-shrink:0;}
#pdf-hdr{padding:12px 16px;border-bottom:1px solid var(--border);flex-shrink:0;
  display:flex;align-items:center;justify-content:space-between;}
.pdf-title{font-size:12.5px;font-weight:600;}
.pdf-sub{font-size:11px;color:var(--muted);margin-top:1px;}
.pdf-empty{font-size:13px;font-weight:600;color:var(--muted);}
.pdf-actions{display:flex;align-items:center;gap:8px;}
.lang-sel{display:none;align-items:center;gap:4px;padding:3px;background:#f4f4f5;border:1px solid var(--border);border-radius:8px;}
.lang-btn{border:none;background:transparent;color:var(--muted);padding:4px 10px;border-radius:6px;font-size:11px;font-weight:700;cursor:pointer;}
.lang-btn.active{background:var(--surface);color:var(--text);box-shadow:0 1px 2px rgba(0,0,0,.06);}
.lang-btn:hover{color:var(--text);}
.btn-ext{font-size:11px;padding:5px 11px;border:1px solid var(--border);
  border-radius:6px;background:var(--surface);color:var(--text2);cursor:pointer;}
.btn-ext:hover{background:#f4f4f5;}
#pdf-frame{flex:1;border:none;background:#e8e8e8;}
#pdf-ph{flex:1;display:flex;flex-direction:column;align-items:center;
  justify-content:center;gap:10px;padding:30px;text-align:center;color:var(--faint);}
.ph-icon{font-size:36px;}
.ph-title{font-size:14px;font-weight:600;color:var(--muted);}
.ph-sub{font-size:12px;line-height:1.6;}

/* Modal */
#modal-bg{position:fixed;inset:0;background:rgba(0,0,0,.3);backdrop-filter:blur(4px);
  z-index:50;display:none;align-items:center;justify-content:center;}
#modal-bg.open{display:flex;}
#modal{background:var(--surface);border:1px solid var(--border);border-radius:12px;
  padding:24px;width:420px;max-width:95vw;box-shadow:0 20px 60px rgba(0,0,0,.12);}
.modal-title{font-size:16px;font-weight:700;margin-bottom:4px;}
.modal-sub{font-size:12px;color:var(--muted);margin-bottom:18px;}
.field{margin-bottom:13px;}
.field label{display:block;font-size:12px;font-weight:600;margin-bottom:5px;}
.field .hint{font-size:11px;color:var(--muted);margin-top:3px;}
.field input[type=text]{width:100%;padding:8px 10px;background:var(--bg);
  border:1px solid var(--border);border-radius:7px;font-size:13px;color:var(--text);outline:none;}
.field input[type=text]:focus{border-color:var(--accent);}
.field-check{display:flex;align-items:center;gap:8px;cursor:pointer;font-size:12px;}
.field-check input{accent-color:var(--accent);}
.modal-btns{display:flex;gap:8px;margin-top:18px;}
.modal-ok{flex:1;padding:9px 0;background:var(--text);color:#fff;border:none;
  border-radius:7px;font-size:13px;font-weight:600;cursor:pointer;}
.modal-ok:hover{opacity:.85;}
.modal-ok:disabled{opacity:.4;cursor:not-allowed;}
.modal-cancel{padding:9px 16px;border:1px solid var(--border);border-radius:7px;
  background:var(--surface);font-size:13px;cursor:pointer;color:var(--text2);}
.modal-cancel:hover{background:#f4f4f5;}
#modal-msg{font-size:12px;padding:8px 12px;border-radius:7px;margin-top:10px;display:none;}
#modal-msg.ok{display:block;background:var(--green-bg);color:var(--green);border:1px solid var(--green-bd);}
#modal-msg.err{display:block;background:var(--red-bg);color:var(--red);border:1px solid var(--red-bd);}

.empty{font-size:12px;color:var(--faint);padding:6px 0;}
.na-note{font-size:12px;color:var(--faint);text-align:center;padding:12px;}
::-webkit-scrollbar{width:5px;}
::-webkit-scrollbar-track{background:transparent;}
::-webkit-scrollbar-thumb{background:var(--border);border-radius:3px;}
</style>
</head>
<body>

<!-- Header -->
<div id="hdr">
  <div style="display:flex;align-items:center;gap:12px;">
    <span class="logo">ZLab <span class="logo-sub">Monitor</span></span>
    <div class="pill" id="status-pill"><span class="dot"></span><span id="status-txt">Cargando…</span></div>
  </div>
  <div id="hdr-right">
    <button class="btn-ext" onclick="openCreateModal()" style="font-weight:600">+ Registrar target</button>
  </div>
</div>

<div id="body">

<!-- Sidebar: lista de activos / targets -->
<div id="sidebar">
  <div id="sb-hdr">
    <div class="sb-title">Targets registrados</div>
    <input id="sb-search" type="text" placeholder="Buscar activo o dirección…" oninput="filterTargets(this.value)">
  </div>
  <div id="sb-list"><div style="padding:14px;color:var(--faint);font-size:12px">Cargando…</div></div>
  <div id="sb-footer">
    <button onclick="openCreateModal()" style="width:100%;padding:7px;background:var(--text);color:#fff;border:none;border-radius:7px;font-size:12px;font-weight:600;cursor:pointer;">+ Registrar target</button>
  </div>
</div>

<!-- Main -->
<div id="main">

  <!-- Hero: target principal -->
  <div id="hero">
    <div id="hero-left">
      <div id="hero-tag">Target seleccionado</div>
      <div id="hero-name">—</div>
      <div id="hero-sub"></div>
      <div id="hero-badge"></div>
    </div>
    <div id="hero-right">
      <button id="btn-run" onclick="correr()">▶ Iniciar investigación</button>
    </div>
  </div>

  <!-- Contenido -->
  <div id="content">

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Investigación de fuentes por activo · motor_028</span>
        <span id="src-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="research-stats"></div>
      <div class="llm-note" id="research-note" style="display:none;margin-bottom:12px"></div>
      <div class="sources-grid" id="sources-grid">
        <div class="empty">Sin datos aún — corre el framework para consultar las fuentes</div>
      </div>
    </div>

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Admisibilidad de ingestión · motores 007 / 012 / 014</span>
        <span id="ingestion-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="ingestion-stats"></div>
      <div class="llm-note" id="ingestion-classification" style="margin-bottom:12px"></div>
      <div class="llm-note" id="ingestion-learning" style="margin-bottom:12px"></div>
      <div class="sources-grid" id="ingestion-fields">
        <div class="empty">Sin registros de admisibilidad todavía</div>
      </div>
      <div class="chart-list" id="ingestion-evidence" style="margin-top:12px">
        <div class="empty">Sin evidencia mínima registrada todavía</div>
      </div>
      <div class="chart-list" id="ingestion-priorities" style="margin-top:12px">
        <div class="empty">Sin prioridades de siguiente ingesta todavía</div>
      </div>
    </div>

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Motor de charts · motor_018</span>
        <span id="chart-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="chart-stats"></div>
      <div class="chart-list" id="chart-list">
        <div class="empty">Sin datos del motor de charts todavía</div>
      </div>
    </div>

    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Congruence Brain · combinaciones adjudicables</span>
        <span id="brain-count" class="card-sub"></span>
      </div>
      <div class="stats-grid" id="brain-stats"></div>
      <div class="llm-note" id="brain-note" style="display:none;margin-bottom:12px"></div>
      <div class="brain-list" id="brain-list">
        <div class="empty">Sin combinaciones activas todavía</div>
      </div>
    </div>

    <!-- Motores -->
    <div class="card">
      <div class="card-hdr">
        <span class="card-title">Estado de los motores</span>
        <span id="motor-counts" class="card-sub"></span>
      </div>
      <div class="prog-row"><span id="prog-lbl">—</span><span id="prog-pct" style="font-weight:700">—</span></div>
      <div class="prog-track"><div class="prog-fill" id="prog-fill" style="width:0%"></div></div>
      <div class="motor-dots" id="motor-dots"></div>
    </div>

    <!-- LLM -->
    <div class="card">
      <div class="card-hdr"><span class="card-title">Motores críticos de análisis y reporte</span></div>
      <div class="llm-note" id="llm-note">Esta tabla ya no pretende describir “la IA” en abstracto. Resume los motores que más afectan análisis, charts y ensamblado del reporte.</div>
      <table class="llm-table" id="llm-table"></table>
    </div>

    <!-- Auditoría -->
    <div class="card">
      <div class="card-hdr"><span class="card-title">Auditoría — fallos detectados</span></div>
      <div id="audit-body"><div class="empty">Sin datos</div></div>
    </div>

  </div>
</div>

<!-- Panel derecho: PDF -->
<div id="right">
  <div id="pdf-hdr">
    <div>
      <div class="pdf-empty" id="pdf-title">Reporte generado</div>
      <div class="pdf-sub" id="pdf-sub">La investigación se inicia manualmente</div>
    </div>
    <div class="pdf-actions">
      <div class="lang-sel" id="pdf-lang-sel">
        <button class="lang-btn active" id="pdf-lang-en" onclick="selectPdfLanguage('en')">EN</button>
        <button class="lang-btn" id="pdf-lang-es" onclick="selectPdfLanguage('es')">ES</button>
      </div>
      <button class="btn-ext" id="btn-ext" onclick="openPdfExt()" style="display:none">Abrir ↗</button>
    </div>
  </div>
  <iframe id="pdf-frame" style="display:none;flex:1;border:none;"></iframe>
  <div id="pdf-ph">
    <div class="ph-icon">📄</div>
    <div class="ph-title">Sin reporte aún</div>
    <div class="ph-sub">El PDF aparecerá aquí<br>cuando inicies una investigación y termine el run.</div>
  </div>
</div>

</div><!-- #body -->

<!-- Modal -->
<div id="modal-bg" onclick="onBgClick(event)">
  <div id="modal">
    <div class="modal-title" id="modal-title">Registrar target</div>
    <div class="modal-sub" id="modal-sub">Crea el target primero. La investigación se lanza solo si tú lo indicas.</div>
    <div class="field">
      <label>Dirección del activo <span style="color:var(--muted);font-weight:400">(opcional si ya seleccionaste un target)</span></label>
      <input type="text" id="f-address" placeholder="ej. 5900 HIGHWAY 225, DEER PARK, TX, 77536">
      <div class="hint" id="modal-address-hint">Si rellenas esta dirección, el sistema registra un target nuevo. La investigación solo correrá si activas la opción de ejecutar inmediatamente.</div>
    </div>
    <div class="field">
      <label>Tipo de activo</label>
      <input type="text" id="f-target-type" list="target-type-options" placeholder="ej. oil_gas_downstream_facility">
      <datalist id="target-type-options">
        <option value="commercial_building">
        <option value="data_center">
        <option value="warehouse_distribution">
        <option value="industrial_plant">
        <option value="manufacturing_facility">
        <option value="food_processing_facility">
        <option value="cold_chain_facility">
        <option value="infrastructure_node">
        <option value="oil_gas_upstream_site">
        <option value="oil_gas_midstream_facility">
        <option value="oil_gas_downstream_facility">
      </datalist>
    </div>
    <div class="field">
      <label>Owner context <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
      <input type="text" id="f-owner-name" placeholder="Nombre del owner o operador si ya lo sabes">
    </div>
    <div class="field">
      <label>Ticker owner <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
      <input type="text" id="f-owner-ticker" placeholder="ej. PLD, BXP, NEE">
    </div>
    <div class="field">
      <label>ID del análisis</label>
      <input type="text" id="f-pid" placeholder="ej. esrt-2026">
    </div>
    <div class="field">
      <label>Archivo de entradas <span style="color:var(--muted);font-weight:400">(opcional)</span></label>
      <input type="text" id="f-inputs" placeholder="Ruta al .json — se auto-completa si seleccionas un activo">
      <div class="hint">Deja vacío para usar las entradas del target seleccionado.</div>
    </div>
    <div class="field">
      <label class="field-check">
        <input type="checkbox" id="f-auto-run">
        Iniciar investigación inmediatamente después de guardar el target
      </label>
    </div>
    <div class="field">
      <label class="field-check">
        <input type="checkbox" id="f-nocache">
        Re-ejecutar todos los motores (sin caché)
      </label>
    </div>
    <div id="modal-msg"></div>
    <div class="modal-btns">
      <button class="modal-cancel" onclick="closeModal()">Cancelar</button>
      <button class="modal-ok" id="btn-launch" onclick="launchRun()">▶ Ejecutar ahora</button>
    </div>
  </div>
</div>

<script>
const ESTADO={completed:'Completado',completed_real:'Completado',completed_with_stubs:'Completado (parcial)',
  completed_partial:'Completado parcial',completed_no_pdf:'Completado sin PDF',partial:'Parcial',
  cached:'En caché',cached_real:'En caché',cached_stub:'Caché de stub',completed_stub:'Completado como stub',
  failed:'Fallido',running:'Ejecutando',stub:'Placeholder',skipped:'No corrido',missing:'Sin correr',
  not_started:'No investigado',unknown:'Desconocido'};
const FOCUS_COUNT=6;

let liveData=null, selectedRunId=null, selectedPipelineId=null, selectedInputsFile='', allTargets=[], lastPdfMtime=null, currentPdfPath=null, selectedTarget=null, currentPdfVariants={}, currentPdfLanguage='en', modalIntent='create';

async function init(){
  await Promise.all([refresh(), loadTargets()]);
  document.getElementById('f-address').addEventListener('input', updateLaunchButtonLabel);
  document.getElementById('f-auto-run').addEventListener('change', updateLaunchButtonLabel);
  setInterval(refresh,4000);
  setInterval(loadTargets,15000);
}

async function refresh(){
  try{
    let url='/api/live';
    if(selectedPipelineId)url=`/api/live?pipeline_id=${encodeURIComponent(selectedPipelineId)}`;
    else if(selectedRunId)url=`/api/live?run_id=${encodeURIComponent(selectedRunId)}`;
    const d=await fj(url); liveData=d;
    if(!selectedPipelineId&&d.pipeline_id)selectedPipelineId=d.pipeline_id;
    renderPill(d); renderHero(d); renderResearch(d); renderIngestion(d); renderChartEngine(d); renderCongruenceBrain(d); renderMotores(d); renderLLM(d); renderAuditoria(d);
    renderPdf(d.pdf,pdfPlaceholderFor(d),d.pdf_variants||{});
  }catch(e){console.warn(e);}
}

async function fj(u){return(await fetch(u)).json();}

function displayState(d){return d.display_status||d.status||'unknown';}

function pdfPlaceholderFor(d){
  const s=displayState(d);
  if(!d.has_run){
    if((d.target&&d.target.label)||selectedTarget?.name||selectedPipelineId){
      return 'Target registrado sin investigación. Iníciala manualmente cuando quieras.';
    }
    return 'Sin reporte aún';
  }
  if(s==='running')return `Ejecutando ${selectedTarget?.name||d.target?.label||d.pipeline_id||'análisis'}… el PDF aparecerá al finalizar este run.`;
  if(s==='completed_partial')return 'El framework terminó de forma parcial: hay placeholders contractuales activos y no debe leerse como cierre total.';
  if(s==='partial')return 'El framework terminó sin un entregable final íntegro. Revisa renderizado, exportación y trazabilidad del PDF.';
  if(s==='completed_no_pdf')return 'El análisis terminó pero no dejó un PDF renderizable. Revisa motor_016 y motor_017.';
  if(s==='failed')return 'El análisis falló antes de generar un PDF.';
  return 'Sin reporte aún';
}

// ── Pill ──────────────────────────────────────────────────────
function renderPill(d){
  const pill=document.getElementById('status-pill');
  const txt=document.getElementById('status-txt');
  if(!d.has_run){
    pill.className='pill';
    txt.textContent=((d.target&&d.target.label)||selectedTarget?.name||selectedPipelineId)?'No investigado':'Sin análisis';
    return;
  }
  const s=displayState(d);
  if(s==='running'){pill.className='pill running';txt.textContent='Ejecutando';}
  else if(s==='completed'){pill.className='pill done';txt.textContent='Completado';}
  else if(s==='completed_partial'||s==='completed_no_pdf'||s==='partial'){pill.className='pill warn';txt.textContent=ESTADO[s]||s;}
  else if(s==='failed'){pill.className='pill fail';txt.textContent='Fallido';}
  else{pill.className='pill';txt.textContent=ESTADO[s]||s;}
}

// ── Hero ──────────────────────────────────────────────────────
function renderHero(d){
  const tg=d.target||{};
  const co=d.company||{};
  const selectedName=selectedTarget?.name||'';
  const name=tg.label||selectedName||(d.has_run?(d.case_title||d.pipeline_id||''):'');
  document.getElementById('hero-name').textContent=name||'Sin activo seleccionado';
  const heroAddress=tg.address||selectedTarget?.target_address||'';
  const heroType=tg.target_type||selectedTarget?.target_type||'';
  const heroOwner=tg.owner_name||co.name||selectedTarget?.owner_name||'';
  document.getElementById('hero-sub').textContent=[heroAddress,heroType,heroOwner].filter(Boolean).join(' · ');
  const badge=document.getElementById('hero-badge');
  const btn=document.getElementById('btn-run');
  const samePipeline=!selectedPipelineId||selectedPipelineId===d.pipeline_id;
  if(d.has_run&&samePipeline){
    const s=displayState(d);
    let cls='eb-idle';
    if(s==='running')cls='eb-running';
    else if(s==='completed')cls='eb-done';
    else if(s==='completed_partial'||s==='completed_no_pdf'||s==='partial')cls='eb-warn';
    else if(s==='failed')cls='eb-failed';
    const dur=d.duration_s?(d.duration_s>60?`${Math.floor(d.duration_s/60)}m ${Math.round(d.duration_s%60)}s`:`${d.duration_s}s`):'';
    badge.innerHTML=`<span class="e-badge ${cls}">${ESTADO[s]||s}</span>${dur?`<span style="font-size:12px;color:var(--faint)">${dur}</span>`:''}`;
    if(s==='running'){btn.textContent='⏳ Ejecutando…';btn.disabled=true;}
    else{btn.innerHTML='▶ Iniciar investigación';btn.disabled=false;}
  }else{
    if(name||selectedPipelineId){
      badge.innerHTML='<span class="e-badge eb-idle">No investigado</span><span style="font-size:12px;color:var(--faint)">La investigación se lanza manualmente</span>';
    }else{
      badge.innerHTML='';
    }
    btn.innerHTML='▶ Iniciar investigación';btn.disabled=false;
  }
}

// ── Investigación de fuentes ───────────────────────────────────
function statCard(value,label){
  return `<div class="stat-card"><div class="stat-val">${esc(value)}</div><div class="stat-lbl">${esc(label)}</div></div>`;
}

function sourceStatusLabel(status){
  const map={
    found:'Con datos',
    no_data:'Sin datos',
    failed:'Falló',
    context_missing:'Contexto insuficiente',
    not_applicable:'No aplicable',
    untracked:'Sin rastro',
    proposed:'Propuesto'
  };
  return map[status]||status;
}

function sourceScopeLabel(scope){
  const map={
    entity_level:'entity-level',
    issuer_specific:'issuer-specific',
    asset_jurisdiction_specific:'asset/jurisdiction-specific',
    market_signal:'market-signal',
    energy_environment_context:'energy/environment',
    macro_context:'macro-context',
    extended_context:'extended-context'
  };
  return map[scope]||scope||'';
}

function renderResearch(d){
  const research=d.research||{};
  const summary=research.summary||{};
  const attempts=research.attempts||[];
  const grid=document.getElementById('sources-grid');
  const cnt=document.getElementById('src-count');
  const stats=document.getElementById('research-stats');
  const note=document.getElementById('research-note');
  cnt.textContent=summary.contract_total?`${summary.applicable_contract_total??summary.contract_total}/${summary.contract_total} fuentes aplicables/contractuales`:'';
  stats.innerHTML=[
    statCard(summary.contract_total??'—','Contrato'),
    statCard(summary.applicable_contract_total??'—','Aplicables'),
    statCard(summary.attempted??'—','Intentos trazados'),
    statCard(summary.found??'—','Con datos'),
    statCard(summary.admitted??'—','Admitidas'),
    statCard(summary.no_data??'—','Sin datos'),
    statCard(summary.failed??'—','Fallidas'),
    statCard(summary.context_missing??'—','Contexto insuficiente'),
    statCard(summary.not_applicable??'—','No aplicables'),
    statCard(summary.untracked??'—','Sin rastro'),
  ].join('');
  if(research.note){
    note.style.display='block';
    note.textContent=research.note;
  }else{
    note.style.display='none';
    note.textContent='';
  }
  if(!attempts.length){
    grid.innerHTML='<div class="empty">Sin fuentes consultadas aún. Ejecuta el framework.</div>';return;
  }
  const dc=s=>(s==='found'||s==='ok'||s==='enriched'||s==='accepted')
    ?'sd-found'
    :(s==='failed')
      ?'sd-failed'
      :(s==='no_data')
        ?'sd-no_data'
        :'sd-untracked';
  grid.innerHTML=attempts.map(s=>`
    <div class="src-item">
      <span class="src-dot ${dc(s.status)}"></span>
      <div class="src-body">
        <div class="src-name">${esc(s.label||s.source_type||'Fuente')}</div>
        <div class="src-val">${esc(sourceStatusLabel(s.status))}${s.family?` · ${esc(s.family)}`:''}${s.source_scope?` · ${esc(sourceScopeLabel(s.source_scope))}`:''}${s.lifecycle_stage?` · ${esc(s.lifecycle_stage)}`:''}</div>
        ${s.locator?`<div class="src-meta">${esc(s.locator)}</div>`:''}
        ${s.discovery_reason?`<div class="src-meta">${esc(s.discovery_reason)}</div>`:''}
        ${(s.error||s.detail)?`<div class="src-meta">${esc(s.error||s.detail)}</div>`:''}
      </div>
    </div>`).join('');
}

function renderIngestion(d){
  const ing=d.ingestion||{};
  const summary=ing.summary||{};
  const cls=ing.classification||{};
  const learning=ing.learning||{};
  const learningSummary=learning.summary||{};
  const caseDelta=learning.case_delta_summary||{};
  const yieldSummary=learning.source_yield_memory_summary||{};
  const nextUpdate=learning.next_ingestion_priority_update||{};
  const stats=document.getElementById('ingestion-stats');
  const info=document.getElementById('ingestion-classification');
  const learn=document.getElementById('ingestion-learning');
  const fields=document.getElementById('ingestion-fields');
  const evidence=document.getElementById('ingestion-evidence');
  const priorities=document.getElementById('ingestion-priorities');
  const cnt=document.getElementById('ingestion-count');
  const reportTrace=cls.report_type_trace||{};
  const selfEval=cls.phase_self_evaluation_summary||{};
  if(!ing.available){
    cnt.textContent='';
    stats.innerHTML='';
    info.textContent='Sin registros de ingestión todavía.';
    learn.textContent='Sin memoria de aprendizaje todavía.';
    fields.innerHTML='<div class="empty">Sin campos bloqueantes registrados</div>';
    evidence.innerHTML='<div class="empty">Sin evidencia mínima registrada</div>';
    priorities.innerHTML='<div class="empty">Sin prioridades de siguiente ingesta</div>';
    return;
  }
  cnt.textContent=`${summary.sources_accepted||0}/${summary.sources_total||0} fuentes aceptadas · ${summary.blocking_fields_total||0} campos bloqueantes`;
  stats.innerHTML=[
    statCard(cls.target_type||'—','Target type'),
    statCard(cls.recommended_report_type||'—','Reporte recomendado'),
    statCard(reportTrace.final_published_report_type||cls.report_identity_state||'—','Reporte final'),
    statCard(summary.sources_accepted??'—','Fuentes aceptadas'),
    statCard(summary.sources_rejected??'—','Fuentes rechazadas'),
    statCard(summary.blocking_fields_total??'—','Campos bloqueantes'),
    statCard(summary.missing_evidence_total??'—','Evidencia faltante'),
    statCard(learningSummary.net_progress_state||'—','Delta'),
    statCard(learningSummary.priority_count??'—','Próx. ingesta'),
  ].join('');
  const scopeBits=Object.entries(summary.scope_counts||{}).map(([k,v])=>`${k}: ${v}`).join(' · ');
  info.textContent=[
    `Clasificación: ${cls.target_type||'—'} (${cls.classification_confidence||'—'})`,
    `Admisibilidad: ${cls.target_admissibility_state||'—'}`,
    `Readiness: ${cls.technical_substrate_readiness||'—'}`,
    reportTrace.early_report_type_gate?`Trace: ${reportTrace.early_report_type_gate} → ${reportTrace.final_published_report_type||cls.report_identity_state||'—'}`:'',
    selfEval.overall_result?`Autoeval: ${selfEval.overall_result} (${selfEval.resolved||0}/${selfEval.total_phases||0} resolved)`:'',
    `Ingestion status: ${cls.ingestion_contract_status||'—'}`,
    scopeBits?`Scopes: ${scopeBits}`:''
  ].filter(Boolean).join(' | ');
  learn.textContent=[
    learningSummary.previous_run_id?`Run previo: ${learningSummary.previous_run_id}`:'Primera corrida con memoria inter-ingesta.',
    learningSummary.net_progress_state?`Delta: ${learningSummary.net_progress_state}`:'',
    `Fuentes productivas: ${yieldSummary.productive_source_count??0}/${yieldSummary.sources_evaluated??0}`,
    nextUpdate.top_priority_action?`Acción top: ${nextUpdate.top_priority_action}`:'',
    (caseDelta.progress_signals||[]).length?`Señales+: ${(caseDelta.progress_signals||[]).slice(0,3).join(', ')}`:'',
    (caseDelta.regression_signals||[]).length?`Señales-: ${(caseDelta.regression_signals||[]).slice(0,3).join(', ')}`:''
  ].filter(Boolean).join(' | ');
  const blocking=ing.blocking_fields||[];
  if(!blocking.length){
    fields.innerHTML='<div class="empty">Sin campos bloqueantes registrados</div>';
  }else{
    fields.innerHTML=blocking.map(row=>`
      <div class="src-item">
        <span class="src-dot sd-failed"></span>
        <div class="src-body">
          <div class="src-name">${esc(row.field||'Field')}</div>
          <div class="src-val">${esc(row.admissibility||'')} · ${esc(row.scope||'')}</div>
          ${row.notes?`<div class="src-meta">${esc(row.notes)}</div>`:''}
        </div>
      </div>`).join('');
  }
  const missing=ing.missing_evidence||[];
  if(!missing.length){
    evidence.innerHTML='<div class="empty">Sin evidencia mínima registrada</div>';
  }else{
    evidence.innerHTML=missing.map(row=>`
      <div class="chart-item">
        <div class="chart-name">${esc(row.missing_field||'Campo faltante')}</div>
        ${row.minimum_evidence_needed?`<div class="chart-meta">${esc(row.minimum_evidence_needed)}</div>`:''}
        ${row.suggested_source?`<div class="chart-meta">Fuente sugerida: ${esc(row.suggested_source)}</div>`:''}
      </div>`).join('');
  }
  const priorityRows=nextUpdate.priorities||[];
  if(!priorityRows.length){
    priorities.innerHTML='<div class="empty">Sin prioridades de siguiente ingesta</div>';
  }else{
    priorities.innerHTML=priorityRows.slice(0,5).map(row=>`
      <div class="chart-item">
        <div class="chart-name">${esc(row.priority_rank||'')} · ${esc(row.action_type||'Acción')}</div>
        ${row.target?`<div class="chart-meta">${esc(row.target)}</div>`:''}
        ${row.reason?`<div class="chart-meta">${esc(row.reason)}</div>`:''}
        ${row.expected_unlock?`<div class="chart-meta">Desbloquea: ${esc(row.expected_unlock)}</div>`:''}
        ${row.basis?`<div class="chart-meta">Base: ${esc(row.basis)}</div>`:''}
      </div>`).join('');
  }
}

function renderChartEngine(d){
  const charts=d.charts||{};
  const assets=charts.assets||[];
  const errors=charts.errors||[];
  document.getElementById('chart-count').textContent=`${charts.total_charts||0} charts · ${errors.length||0} errores`;
  document.getElementById('chart-stats').innerHTML=[
    statCard(ESTADO[charts.status]||charts.status||'Sin correr','Estado'),
    statCard(charts.total_charts||0,'Charts'),
    statCard(errors.length||0,'Errores'),
    statCard(charts.adapter_class||'—','Adapter'),
  ].join('');
  const list=document.getElementById('chart-list');
  if(!assets.length&&!errors.length){
    list.innerHTML='<div class="empty">motor_018 no dejó charts trazables en este run.</div>';
    return;
  }
  list.innerHTML=[
    ...assets.map(asset=>`
      <div class="chart-item">
        <div class="chart-name">${esc(asset.title||asset.asset_id||'Chart')}</div>
        ${asset.section_hint?`<div class="chart-meta">${esc(asset.section_hint)}</div>`:''}
        ${asset.description?`<div class="chart-meta">${esc(asset.description)}</div>`:''}
      </div>`),
    ...errors.map(err=>`
      <div class="chart-item">
        <div class="chart-name">Error</div>
        <div class="chart-meta">${esc(typeof err==='string'?err:JSON.stringify(err))}</div>
      </div>`),
  ].join('');
}

function decisionLabel(value){
  const map={
    candidate:'Candidate',
    accepted_for_case_use:'Accepted',
    accepted_for_reference_use:'Accepted',
    accepted_for_registry_review:'Accepted',
    rejected_for_case_use:'Rejected',
    rejected_for_reference_use:'Rejected',
    rejected_for_registry_review:'Rejected',
    needs_review:'Needs review',
    blocked_by_validator:'Blocked'
  };
  return map[value]||value||'Candidate';
}

function renderCongruenceBrain(d){
  const brain=d.congruence_brain||{};
  const review=brain.combination_review_register||[];
  const summary=brain.decision_summary||{};
  const counts=summary.by_decision||{};
  const registry=brain.registry||{};
  const patternAuthorityState=brain.pattern_authority_state||'legacy_primary_skill_shadow';
  const authoritativePatterns=brain.authoritative_pattern_activation_register||[];
  const assetContextVector=brain.asset_context_vector||{};
  const contextDifferentiators=brain.context_differentiator_register||[];
  const latentCandidates=brain.latent_combination_candidate_register||[];
  const latentClusters=brain.latent_combination_cluster_register||[];
  const admissibleLatent=brain.admissible_combination_review_register||[];
  const reviewSequence=brain.combination_review_sequence_register||[];
  const currentCombinationReview=brain.current_combination_review_row||{};
  const nextCombinationReviews=brain.next_combination_review_rows||[];
  const reviewQueueSummary=brain.combination_review_queue_summary||{};
  const combinationFollowOnResearch=brain.combination_follow_on_research_register||[];
  const combinationFollowOnExecutionManifests=brain.combination_follow_on_execution_manifest_register||[];
  const searchGap=brain.combination_search_gap_record||{};
  const researchCampaign=brain.research_campaign_record||{};
  const researchCampaignTriggers=brain.research_campaign_trigger_register||[];
  const researchLoopState=brain.research_loop_state||{};
  const researchLoopJobs=brain.research_loop_job_register||[];
  const currentResearchJob=brain.current_research_job||{};
  const researchLoopMetrics=brain.research_loop_metrics||{};
  const researchLoopControl=brain.research_loop_control_record||{};
  const researchDepth=brain.research_depth_enforcement_record||{};
  const researchStop=brain.research_stop_condition_record||{};
  const licensed=brain.licensed_research||{};
  const providerRows=licensed.provider_session_register||[];
  const promotionReview=licensed.promotion_review_register||[];
  const discoveryReview=licensed.discovery_candidate_review_register||[];
  const discoveryDecisionSummary=licensed.discovery_candidate_decision_summary||{};
  const articleReferences=licensed.article_reference_register||[];
  const searchResultCaptureRegister=brain.search_result_capture_register||licensed.search_result_capture_register||[];
  const currentSearchResultCapture=brain.current_search_result_capture_row||licensed.current_search_result_capture_row||{};
  const nextSearchResultCaptureRows=brain.next_search_result_capture_rows||licensed.next_search_result_capture_rows||[];
  const searchResultCaptureSummary=brain.search_result_capture_summary||licensed.search_result_capture_summary||{};
  const searchQueryExecutionRegister=brain.search_query_execution_register||licensed.search_query_execution_register||[];
  const currentSearchQueryExecution=brain.current_search_query_execution_row||licensed.current_search_query_execution_row||{};
  const nextSearchQueryExecutionRows=brain.next_search_query_execution_rows||licensed.next_search_query_execution_rows||[];
  const searchQueryExecutionSummary=brain.search_query_execution_summary||licensed.search_query_execution_summary||{};
  const searchQueryResultOptionReviewRegister=brain.search_query_result_option_review_register||licensed.search_query_result_option_review_register||[];
  const currentSearchQueryResultOption=brain.current_search_query_result_option_row||licensed.current_search_query_result_option_row||{};
  const nextSearchQueryResultOptionRows=brain.next_search_query_result_option_rows||licensed.next_search_query_result_option_rows||[];
  const searchQueryResultOptionSummary=brain.search_query_result_option_summary||licensed.search_query_result_option_summary||{};
  const searchQueryResultOptionBatchPlan=brain.search_query_result_option_batch_plan||licensed.search_query_result_option_batch_plan||{};
  const searchQueryExecutionBatchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  const searchQueryExecutionManifest=brain.search_query_execution_manifest||licensed.search_query_execution_manifest||{};
  const searchQueryExecutionSessionBundle=brain.search_query_execution_session_bundle||licensed.search_query_execution_session_bundle||searchQueryExecutionManifest.session_bundle||{};
  const searchQueryExecutionSessionStore=brain.search_query_execution_session_store||licensed.search_query_execution_session_store||{};
  const searchSessionFormRows=buildEffectiveSearchSessionRows(searchQueryExecutionSessionBundle);
  const defaultSearchSessionEditorText=searchQueryExecutionSessionBundle.available?JSON.stringify(searchQueryExecutionSessionBundle, null, 2):'';
  const searchSessionEditorText=window._searchSessionEditorDraft||defaultSearchSessionEditorText;
  const searchSessionEditorOpen=!!window._searchSessionEditorOpen;
  const searchSessionFormOpen=!!window._searchSessionFormOpen;
  const searchQueryResultImportStore=brain.search_query_result_import_store||licensed.search_query_result_import_store||{};
  const referenceResolutionSequence=brain.reference_resolution_sequence_register||licensed.reference_resolution_sequence_register||[];
  const currentReferenceResolution=brain.current_reference_resolution_row||licensed.current_reference_resolution_row||{};
  const nextReferenceResolutionRows=brain.next_reference_resolution_rows||licensed.next_reference_resolution_rows||[];
  const referenceResolutionQueueSummary=brain.reference_resolution_queue_summary||licensed.reference_resolution_queue_summary||{};
  const referenceResolutionBatchPlan=brain.reference_resolution_batch_plan||licensed.reference_resolution_batch_plan||{};
  const acceptedDiscoveryBundle=licensed.accepted_discovery_candidate_bundle||{};
  const acceptedDiscoverySummary=acceptedDiscoveryBundle.summary||{};
  const acceptedDiscoveryManifest=licensed.accepted_discovery_candidate_bundle_manifest||{};
  const referenceBackedPromotionManifest=licensed.reference_backed_promotion_manifest||{};
  const referenceBackedPromotionSummary=referenceBackedPromotionManifest.summary||{};
  const knowledgeAtomRefreshSummary=licensed.knowledge_atom_refresh_summary||{};
  const combinationRerankSummary=licensed.combination_rerank_summary||{};
  const discoveryQueue=licensed.discovery_candidate_queue||{};
  const knowledgeAtoms=licensed.knowledge_atom_register||[];
  const sourceCoverage=licensed.source_coverage_summary||{};
  const sourceFamilyCoverage=licensed.source_family_coverage_register||[];
  const promotionDecisionSummary=licensed.promotion_decision_summary||{};
  const registryReviewBundle=licensed.registry_review_bundle||{};
  const registryReviewSummary=registryReviewBundle.summary||{};
  const registryStagePreview=licensed.registry_stage_preview||{};
  const registryStageSummary=registryStagePreview.summary||{};
  const registryStageCandidateManifest=licensed.registry_stage_candidate_manifest||{};
  const registryStageCandidateSummary=registryStageCandidateManifest.summary||{};
  const registryStageMergeManifest=licensed.registry_stage_merge_manifest||{};
  const registryStageMergeSummary=registryStageMergeManifest.summary||{};
  const providerHandoffBundle=licensed.provider_handoff_bundle||{};
  const providerHandoffSummary=providerHandoffBundle.summary||{};
  const providerSessionHandoffManifest=licensed.provider_session_handoff_manifest||{};
  const promotionSummary=brain.promotion_summary||{};
  const promotionEditStore=licensed.promotion_edit_store||{};
  const combinationReviewControlStore=brain.combination_review_control_store||{};
  const combinationFollowOnManifestStore=brain.combination_follow_on_manifest_store||{};
  const stats=document.getElementById('brain-stats');
  const note=document.getElementById('brain-note');
  const list=document.getElementById('brain-list');
  const cnt=document.getElementById('brain-count');
  cnt.textContent=brain.available?`${review.length||0} combinaciones activas · ${summary.accepted||0} aceptadas · ${summary.rejected||0} rechazadas`:'Skill no disponible';
  stats.innerHTML=[
    statCard(registry.patterns??'—','Patterns'),
    statCard(registry.combinations??'—','Combinations'),
    statCard((brain.active_pattern_ids||[]).length||0,'Patterns activos'),
    statCard(authoritativePatterns.length||0,'Patterns autoridad'),
    statCard(patternAuthorityState,'Pattern authority'),
    statCard(review.length||0,'Combos activos'),
    statCard(reviewQueueSummary.pending??0,'Combos pendientes'),
    statCard(latentCandidates.length||0,'Latent combos'),
    statCard(latentClusters.length||0,'Latent clusters'),
    statCard(admissibleLatent.length||0,'Admissible latent'),
    statCard(knowledgeAtoms.length||0,'Knowledge atoms'),
    statCard(sourceCoverage.document_count??0,'Research docs'),
    statCard(searchGap.search_status||'unknown','Search gap'),
    statCard(researchCampaign.campaign_status||'unknown','Campaign'),
    statCard(researchLoopState.loop_status||'planning','Loop state'),
    statCard(researchLoopJobs.length||0,'Loop jobs'),
    statCard(researchLoopMetrics.resolved_reference_count??0,'Resolved refs'),
    statCard(researchLoopMetrics.latent_candidate_count??0,'Latent pool'),
    statCard(researchCampaignTriggers.filter(row=>row.status==='queued').length||0,'Queued triggers'),
    statCard(providerRows.length||0,'Providers'),
    statCard(discoveryReview.length||0,'Discovery candidates'),
    statCard(acceptedDiscoverySummary.accepted_count??0,'Accepted refs'),
    statCard(articleReferences.length||0,'Article refs'),
    statCard(searchResultCaptureSummary.pending??0,'Search captures'),
    statCard(searchQueryExecutionSummary.pending??0,'Search executions'),
    statCard(referenceResolutionQueueSummary.pending??0,'Draft refs'),
    statCard(referenceBackedPromotionSummary.pattern_promotion_count??0,'Ref-backed promotions'),
    statCard(knowledgeAtomRefreshSummary.delta_atom_count??0,'Atom delta'),
    statCard(combinationRerankSummary.current_latent_candidate_count??0,'Reranked latent'),
    statCard(providerHandoffSummary.login_required_count??0,'Provider logins'),
    statCard(promotionSummary.approved_patterns??0,'Pattern promotions'),
    statCard(promotionSummary.approved_combinations??0,'Combo promotions'),
    statCard(promotionDecisionSummary.accepted??0,'Promotions accepted'),
    statCard(promotionEditStore.stored_edit_count??0,'Promotion edits'),
    statCard(registryReviewSummary.accepted_total??0,'Registry bundle'),
    statCard(registryStageSummary.write_candidate_file_count??0,'Registry stage'),
    statCard(registryStageCandidateSummary.materialized_count??0,'Stage files'),
    statCard(registryStageMergeSummary.merged_count??0,'Registry merged'),
    statCard(counts.needs_review??0,'Needs review'),
    statCard(counts.accepted_for_case_use??0,'Accepted'),
  ].join('');
  if(brain.note){
    note.style.display='block';
    note.textContent=brain.note;
  }else{
    note.style.display='none';
    note.textContent='';
  }
  if(!brain.available){
    list.innerHTML='<div class="empty">La skill soberana todavía no está disponible en este runtime.</div>';
    return;
  }
  const sections=[];
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Pattern Authority</div>
          <div class="brain-meta">Estado actual: ${esc(patternAuthorityState)}</div>
        </div>
        <span class="brain-state ${esc(patternAuthorityState)}">${esc(patternAuthorityState)}</span>
      </div>
      <div class="brain-meta"><strong>Patterns activos:</strong> ${esc((brain.active_pattern_ids||[]).join(' · ')||'—')}</div>
      <div class="brain-meta"><strong>Patterns autoritativos:</strong> ${esc(authoritativePatterns.map(row=>row.pattern_id||row.pattern_name||'').filter(Boolean).join(' · ')||'—')}</div>
    </div>`);
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Asset Context</div>
          <div class="brain-meta">Contexto específico usado para evitar combinaciones tipo plantilla.</div>
        </div>
        <span class="brain-state candidate">${esc(assetContextVector.context_signature||'context-unbound')}</span>
      </div>
      <div class="brain-meta"><strong>Asset family:</strong> ${esc(assetContextVector.asset_family||'—')} · <strong>Solar:</strong> ${esc(assetContextVector.solar_profile||'—')} · <strong>Ops:</strong> ${esc(assetContextVector.operating_rhythm||'—')}</div>
      <div class="brain-meta"><strong>Tariff:</strong> ${esc(assetContextVector.utility_tariff_context||'—')} · <strong>Boundary:</strong> ${esc(assetContextVector.control_boundary||'—')} · <strong>Service:</strong> ${esc(assetContextVector.service_intensity||'—')}</div>
      <div class="brain-meta"><strong>Specificity:</strong> ${esc(String(assetContextVector.context_specificity_score||0))} · <strong>Differentiators:</strong> ${esc(contextDifferentiators.map(row=>row.implication||row.signal||'').filter(Boolean).join(' | ')||'—')}</div>
    </div>`);
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Research Coverage</div>
          <div class="brain-meta">Atoms y cobertura documental que sostienen la búsqueda latente.</div>
        </div>
        <span class="brain-state candidate">${esc(sourceCoverage.coverage_strength||'empty')}</span>
      </div>
      <div class="brain-meta"><strong>Knowledge atoms:</strong> ${esc(String(sourceCoverage.knowledge_atom_count||0))} · <strong>Docs:</strong> ${esc(String(sourceCoverage.document_count||0))} · <strong>Providers:</strong> ${esc((sourceCoverage.providers||[]).join(' | ')||'—')}</div>
      <div class="brain-meta"><strong>Knowledge types:</strong> ${esc((sourceCoverage.knowledge_types||[]).join(' | ')||'—')}</div>
      <div class="brain-meta"><strong>Supported patterns:</strong> ${esc((sourceCoverage.supported_pattern_ids||[]).join(' · ')||'—')}</div>
    </div>`);
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Combination Search Gap</div>
          <div class="brain-meta">Diagnostica si el pool latente todavía es superficial por investigación insuficiente.</div>
        </div>
        <span class="brain-state ${esc(searchGap.severity||'candidate')}">${esc(searchGap.search_status||'unknown')}</span>
      </div>
      <div class="brain-meta"><strong>Summary:</strong> ${esc(searchGap.summary||'—')}</div>
      <div class="brain-meta"><strong>Flags:</strong> ${esc((searchGap.gap_flags||[]).join(' | ')||'—')}</div>
      <div class="brain-meta"><strong>Actions:</strong> ${esc((searchGap.recommended_actions||[]).join(' | ')||'—')}</div>
    </div>`);
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Research Campaign</div>
          <div class="brain-meta">Estado de la campaña de investigación multi-fuente para este activo.</div>
        </div>
        <span class="brain-state ${esc(researchCampaign.campaign_status||'candidate')}">${esc(researchCampaign.campaign_status||'unknown')}</span>
      </div>
      <div class="brain-meta"><strong>Summary:</strong> ${esc(researchCampaign.summary||'—')}</div>
      <div class="brain-meta"><strong>Mode:</strong> ${esc(researchCampaign.mode||'standard')} · <strong>Touched families:</strong> ${esc(String(researchCampaign.touched_source_family_count||0))}/${esc(String(researchCampaign.target_source_family_count||0))} · <strong>Missing:</strong> ${esc(String(researchCampaign.missing_source_family_count||0))}</div>
      <div class="brain-meta"><strong>Next actions:</strong> ${esc((researchCampaign.top_next_actions||[]).join(' | ')||'—')}</div>
    </div>`);
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Research Loop State</div>
          <div class="brain-meta">Estado soberano del loop autónomo de búsqueda, captura y reranking.</div>
        </div>
        <span class="brain-state ${esc(researchLoopState.loop_status||'candidate')}">${esc(researchLoopState.loop_status||'planning')}</span>
      </div>
      <div class="brain-meta"><strong>Next action:</strong> ${esc(researchLoopState.next_action||'PRESENT_NEXT_COMBINATION')} · <strong>Current job:</strong> ${esc(currentResearchJob.job_type||'—')}</div>
      <div class="brain-meta"><strong>Operator control:</strong> ${esc(researchLoopControl.control_state||'active')}${researchLoopControl.control_reason?` · <strong>Reason:</strong> ${esc(researchLoopControl.control_reason)}`:''}</div>
      <div class="brain-meta"><strong>Current job summary:</strong> ${esc(currentResearchJob.summary||'—')}</div>
      <div class="brain-meta"><strong>Metrics:</strong> latent ${esc(String(researchLoopMetrics.latent_candidate_count||0))} / admissible ${esc(String(researchLoopMetrics.admissible_candidate_count||0))} / atoms ${esc(String(researchLoopMetrics.knowledge_atom_count||0))} / drafts ${esc(String(researchLoopMetrics.query_seed_draft_count||0))} / resolved ${esc(String(researchLoopMetrics.resolved_reference_count||0))}</div>
      <div class="brain-meta"><strong>Stop state:</strong> ${esc(researchStop.stop_state||'continue_research')} · <strong>Target floor:</strong> ${esc(String(researchStop.target_combination_floor||0))} · <strong>Pool sufficiency:</strong> ${esc(researchStop.combination_pool_sufficiency||'unknown')}</div>
      <div class="brain-meta"><strong>Stop reasons:</strong> ${esc((researchStop.reasons||[]).join(' | ')||'—')}</div>
      <div class="brain-actions">
        <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="advanceResearchLoop()">Advance loop</button>
        <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="forceResearchLoopRerank()">Force rerank</button>
        <button class="brain-btn review" ${!liveData?.run_id||(researchLoopControl.control_state||'active')!=='active'?'disabled':''} onclick="setResearchLoopControl('pause')">Pause loop</button>
        <button class="brain-btn accept" ${!liveData?.run_id||(researchLoopControl.control_state||'active')==='active'?'disabled':''} onclick="setResearchLoopControl('resume')">Resume loop</button>
        <button class="brain-btn reject" ${!liveData?.run_id?'disabled':''} onclick="setResearchLoopControl('stop')">Stop loop</button>
      </div>
    </div>`);
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Research Depth Enforcement</div>
          <div class="brain-meta">Gate duro para impedir que el loop pare temprano con cobertura débil o combinaciones genéricas.</div>
        </div>
        <span class="brain-state ${esc(researchDepth.depth_state||'candidate')}">${esc(researchDepth.depth_state||'unknown')}</span>
      </div>
      <div class="brain-meta"><strong>Must continue:</strong> ${esc(String(!!researchDepth.must_continue_research))} · <strong>Saturation proof:</strong> ${esc(String(!!researchDepth.saturation_proof_strong))}</div>
      <div class="brain-meta"><strong>Latent floor:</strong> ${esc(String(researchLoopMetrics.latent_candidate_count||0))}/${esc(String(researchDepth.target_combination_floor||0))} · <strong>Strong families:</strong> ${esc(String(researchDepth.strong_source_family_count||0))}/${esc(String(researchDepth.minimum_strong_source_family_count||0))}</div>
      <div class="brain-meta"><strong>High-priority families:</strong> ${esc(String(researchDepth.strong_high_priority_source_family_count||0))} strong / ${esc(String(researchDepth.touched_high_priority_source_family_count||0))} touched / ${esc(String(researchDepth.high_priority_source_family_count||0))} total</div>
      <div class="brain-meta"><strong>Blockers:</strong> ${esc((researchDepth.policy_reasons||[]).join(' | ')||'—')}</div>
      <div class="brain-meta"><strong>Next source families:</strong> ${esc((researchDepth.required_next_source_families||[]).join(' | ')||'—')}</div>
    </div>`);
  const sourceFamilyCards=researchCampaignTriggers.length?researchCampaignTriggers:sourceFamilyCoverage;
  if(sourceFamilyCards.length){
    sections.push(...sourceFamilyCards.map(row=>`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Source Family · ${esc(row.display_name||row.source_family||'family')}</div>
            <div class="brain-meta">${esc(row.source_family||'')}</div>
          </div>
          <span class="brain-state ${esc(row.coverage_state||'candidate')}">${esc(row.coverage_state||'unknown')}</span>
        </div>
        <div class="brain-meta"><strong>Importance:</strong> ${esc(row.importance||'medium')} · <strong>Providers:</strong> ${esc((row.touched_provider_keys||[]).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Docs:</strong> ${esc(String(row.document_count||0))}/${esc(String(row.target_document_count||0))} · <strong>Atoms:</strong> ${esc(String(row.knowledge_atom_count||0))}/${esc(String(row.target_knowledge_atom_count||0))}</div>
        <div class="brain-meta"><strong>Refs:</strong> ${esc(String(row.reference_count||0))} · <strong>Candidates:</strong> ${esc(String(row.candidate_count||0))}</div>
        <div class="brain-meta"><strong>Capture mode:</strong> ${esc(row.capture_mode||'—')} · <strong>Atomization priority:</strong> ${esc(row.atomization_priority||'—')}</div>
        <div class="brain-meta"><strong>Preferred query families:</strong> ${esc((row.preferred_query_families||[]).join(' | ')||'—')}</div>
        ${row.search_focus?`<div class="brain-meta"><strong>Search focus:</strong> ${esc(row.search_focus)}</div>`:''}
        <div class="brain-meta"><strong>Trigger:</strong> ${esc(row.status||'not_queued')} · <strong>Next providers:</strong> ${esc((row.recommended_provider_keys||[]).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Target delta:</strong> ${esc(String(row.target_document_delta||0))} docs · ${esc(String(row.target_knowledge_atom_delta||0))} atoms${row.queued_at?` · <strong>Queued at:</strong> ${esc(row.queued_at)}`:''}</div>
        ${row.reason?`<div class="brain-meta"><strong>Reason:</strong> ${esc(row.reason)}</div>`:''}
        <div class="brain-actions">
          <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="triggerSourceFamilySearch('${esc(row.source_family)}')">${row.status==='queued'?'Queue again':'Trigger deeper search'}</button>
          <button class="brain-btn reject" ${!liveData?.run_id?'disabled':''} onclick="markSourceFamilyExhausted('${esc(row.source_family)}')">Mark exhausted</button>
        </div>
      </div>`));
  }
  if(licensed.available){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Licensed Research Lane</div>
            <div class="brain-meta">Capability enabled: ${esc(String(licensed.licensed_research_capability_enabled||false))}</div>
          </div>
          <span class="brain-state ${licensed.licensed_research_capability_enabled?'accepted_for_case_use':'candidate'}">${licensed.licensed_research_capability_enabled?'Enabled':'Disabled'}</span>
        </div>
        <div class="brain-meta"><strong>Providers:</strong> ${esc(providerRows.map(row=>`${row.display_name||row.provider_key}: ${((row.session_state||{}).auth_state)||'unknown'}`).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Extraction review:</strong> ${esc(String((licensed.extraction_review_register||[]).length||0))} · <strong>Pattern promotions:</strong> ${esc(String((licensed.approved_pattern_promotion_register||[]).length||0))} · <strong>Combo promotions:</strong> ${esc(String((licensed.approved_combination_promotion_register||[]).length||0))}</div>
        <div class="brain-meta"><strong>Discovery queue:</strong> ${esc(String((discoveryQueue.summary||{}).candidate_count||0))} · <strong>Accepted refs:</strong> ${esc(String(acceptedDiscoverySummary.accepted_count||0))} · <strong>Article refs:</strong> ${esc(String(articleReferences.length||0))}</div>
      </div>`);
  }
  sections.push(`
    <div class="brain-item">
      <div class="brain-head">
        <div>
          <div class="brain-name">Licensed Discovery Import</div>
          <div class="brain-meta">Importa un export de discovery para generar candidatos, sidecars y referencias revisables.</div>
        </div>
        <span class="brain-state candidate">${esc(String((discoveryQueue.summary||{}).candidate_count||0))} candidates</span>
      </div>
        <div class="brain-meta"><strong>Provider:</strong> ${esc(discoveryQueue.provider_key||'—')} · <strong>Export:</strong> ${esc(discoveryQueue.export_path||'—')}</div>
        <div class="brain-actions">
          <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importLicensedDiscovery()">Import discovery export</button>
          <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="createManualDiscoveryCandidate()">Add manual article</button>
          <button class="brain-btn accept" ${!liveData?.run_id||!(acceptedDiscoverySummary.accepted_count>0)?'disabled':''} onclick="readAcceptedArticleReferences()">Read accepted refs</button>
        </div>
      </div>`);
  if((acceptedDiscoverySummary.accepted_count||0)>0){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Accepted Discovery Bundle</div>
            <div class="brain-meta">Candidates approved for reference follow-up and ready for downstream handoff.</div>
          </div>
          <span class="brain-state accepted_for_reference_use">${esc(String(acceptedDiscoverySummary.accepted_count||0))} accepted</span>
        </div>
        <div class="brain-meta"><strong>Visible text:</strong> ${esc(String(acceptedDiscoverySummary.visible_text_enriched_count||0))} · <strong>Metadata only:</strong> ${esc(String(acceptedDiscoverySummary.metadata_only_count||0))}</div>
        <div class="brain-meta"><strong>Titles:</strong> ${esc((acceptedDiscoveryBundle.accepted_rows||[]).map(row=>row.title||row.candidate_id||'').filter(Boolean).join(' | ')||'—')}</div>
        <div class="brain-actions">
          <button class="brain-btn review" ${!liveData?.run_id||!(acceptedDiscoverySummary.accepted_count>0)?'disabled':''} onclick="refreshReferenceBackedPromotions()">Refresh promotions from refs</button>
        </div>
        ${(acceptedDiscoveryManifest.exists)?`<div class="brain-meta"><strong>Manifest:</strong> ${esc(acceptedDiscoveryManifest.path||'—')}</div>`:''}
        ${(referenceBackedPromotionManifest.exists)?`<div class="brain-meta"><strong>Ref-backed promotions:</strong> ${esc(String(referenceBackedPromotionSummary.pattern_promotion_count||0))} patterns · ${esc(String(referenceBackedPromotionSummary.combination_promotion_count||0))} combinations · <strong>Manifest:</strong> ${esc(referenceBackedPromotionManifest.path||'—')}</div>`:''}
      </div>`);
  }
  if(searchResultCaptureRegister.length){
    if(currentSearchQueryResultOption && currentSearchQueryResultOption.candidate_id){
      const row=currentSearchQueryResultOption;
      const currentOption=row.current_imported_option||{};
      const top=row.top_imported_result||{};
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Imported Search Result Review</div>
              <div class="brain-meta">Imported source-hit options queue · ${esc(String(searchQueryResultOptionSummary.current_position||0))}/${esc(String(searchQueryResultOptionSummary.total||0))}</div>
            </div>
            <span class="brain-state candidate">${esc(row.imported_result_state||'imported_options_available')}</span>
          </div>
          <div class="brain-meta"><strong>Provider:</strong> ${esc(row.provider_key||'—')} · <strong>Title:</strong> ${esc(row.title||row.candidate_id||'—')}</div>
          <div class="brain-meta"><strong>Imported options:</strong> ${esc(String(row.imported_result_option_count||0))} · <strong>Current option:</strong> ${esc(String(row.current_option_index||0))}/${esc(String(row.current_option_count||0))} · <strong>Query family:</strong> ${esc(row.query_family||'—')}</div>
          <div class="brain-meta"><strong>Current imported result:</strong> ${esc(currentOption.search_result_title||currentOption.source_url||'—')}</div>
          ${currentOption.search_result_snippet?`<div class="brain-meta"><strong>Current snippet:</strong> ${esc(currentOption.search_result_snippet||'—')}</div>`:''}
          ${top.source_url&&top.source_url!==currentOption.source_url?`<div class="brain-meta"><strong>Top imported result:</strong> ${esc(top.search_result_title||top.source_url||'—')}</div>`:''}
          ${searchQueryResultOptionBatchPlan.available?`<div class="brain-meta"><strong>Batch plan:</strong> ${esc(searchQueryResultOptionBatchPlan.batch_reason||'—')} · <strong>Visible options:</strong> ${esc(String(searchQueryResultOptionBatchPlan.option_count||0))} · <strong>Candidates:</strong> ${esc(String(searchQueryResultOptionBatchPlan.candidate_count||0))}</div>`:''}
          <div class="brain-actions">
            <button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="promoteImportedSearchResult('${esc(row.candidate_id)}', ${Number(row.current_option_index||0)})">Promote current option</button>
            <button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="resolveImportedSearchResult('${esc(row.candidate_id)}', ${Number(row.current_option_index||0)})">Resolve current option</button>
            <button class="brain-btn accept" ${!liveData?.run_id||!searchQueryResultOptionBatchPlan.available||Number(searchQueryResultOptionBatchPlan.option_count||0)<2?'disabled':''} onclick="promoteImportedSearchResultBatch()">Promote visible batch</button>
            <button class="brain-btn accept" ${!liveData?.run_id||!searchQueryResultOptionBatchPlan.available||!searchQueryResultOptionBatchPlan.resolve_available||Number(searchQueryResultOptionBatchPlan.resolve_candidate_count||0)<2?'disabled':''} onclick="resolveImportedSearchResultBatch()">Resolve visible batch</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchQueryResults()">Import more results</button>
          </div>
          ${nextSearchQueryResultOptionRows.length?`<div class="brain-meta"><strong>Next imported reviews:</strong> ${esc(nextSearchQueryResultOptionRows.map(item=>`${item.provider_key||'provider'}:${item.query_family||'query'}:opt${item.current_option_index||0}`).join(' | ')||'—')}</div>`:''}
        </div>`);
    }
    if(currentSearchResultCapture && currentSearchResultCapture.candidate_id){
      const row=currentSearchResultCapture;
      const action=row.next_capture_action||'NO_CAPTURE_REQUIRED';
      const executionRow=currentSearchQueryExecution&&currentSearchQueryExecution.candidate_id===row.candidate_id
        ? currentSearchQueryExecution
        : (searchQueryExecutionRegister.find(item=>item.candidate_id===row.candidate_id)||{});
      const providerGuide=searchQueryExecutionBatchPlan.ordered_result_import_provider_capture_guide||{};
      const searchGuide=searchQueryExecutionBatchPlan.search_execution_provider_guide||{};
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Search Result Capture</div>
              <div class="brain-meta">Query-seed search context queue · ${esc(String(searchResultCaptureSummary.current_position||0))}/${esc(String(searchResultCaptureSummary.total||0))}</div>
            </div>
            <span class="brain-state candidate">${esc(row.capture_state||'needs_draft')}</span>
          </div>
          <div class="brain-meta"><strong>Provider:</strong> ${esc(row.provider_key||'—')} · <strong>Title:</strong> ${esc(row.title||row.candidate_id||'—')}</div>
          <div class="brain-meta"><strong>Next action:</strong> ${esc(action)} · <strong>Reference state:</strong> ${esc(row.reference_state||'metadata_only')}</div>
          <div class="brain-meta"><strong>Launch URL:</strong> ${esc(row.launch_url||'—')}</div>
          <div class="brain-meta"><strong>Primary query:</strong> ${esc(row.primary_query||'—')} · <strong>Pivot query:</strong> ${esc(row.pivot_query||'—')}</div>
          ${(executionRow.query_variants||[]).length?`<div class="brain-meta"><strong>Query variants:</strong> ${esc((executionRow.query_variants||[]).join(' | ')||'—')}</div>`:''}
          ${(row.evidence_targets||[]).length?`<div class="brain-meta"><strong>Evidence targets:</strong> ${esc((row.evidence_targets||[]).join(' | ')||'—')}</div>`:''}
          ${row.execution_hint?`<div class="brain-meta"><strong>Execution hint:</strong> ${esc(row.execution_hint||'—')}</div>`:''}
          ${searchGuide.preferred_surface?`<div class="brain-meta"><strong>Preferred search surface:</strong> ${esc(searchGuide.preferred_surface||'—')}</div>`:''}
          ${(searchGuide.search_tips||[]).length?`<div class="brain-meta"><strong>Search tips:</strong> ${esc((searchGuide.search_tips||[]).join(' | ')||'—')}</div>`:''}
          ${providerGuide.summary?`<div class="brain-meta"><strong>Provider capture guide:</strong> ${esc(providerGuide.summary||'—')}</div>`:''}
          ${(providerGuide.preferred_headers||[]).length?`<div class="brain-meta"><strong>Preferred headers:</strong> ${esc((providerGuide.preferred_headers||[]).join(' | ')||'—')}</div>`:''}
          ${(providerGuide.snippet_header_fallbacks||[]).length?`<div class="brain-meta"><strong>Visible-text fallback headers:</strong> ${esc((providerGuide.snippet_header_fallbacks||[]).join(' | ')||'—')}</div>`:''}
          ${searchQueryExecutionSessionBundle.available?`<div class="brain-meta"><strong>Search session:</strong> ${esc(String((searchQueryExecutionSessionBundle.summary||{}).pending_rows||0))}/${esc(String(searchQueryExecutionSessionBundle.candidate_count||0))} pending · <strong>Ready:</strong> ${esc(String((searchQueryExecutionSessionBundle.summary||{}).ready_rows||0))} · <strong>Materialized:</strong> ${esc(String(!!searchQueryExecutionSessionBundle.materialized))}</div>`:''}
          ${searchQueryExecutionSessionStore.exists?`<div class="brain-meta"><strong>Session store:</strong> ${esc(String(searchQueryExecutionSessionStore.stored_row_count||0))} rows · ${esc(searchQueryExecutionSessionStore.path||'—')}</div>`:''}
          ${searchQueryExecutionBatchPlan.ordered_result_import_provider_capture_sheet_template?`<div class="brain-meta"><strong>Provider sheet:</strong> row-guided capture sheet ready for copy/paste.</div>`:''}
          ${searchQueryExecutionBatchPlan.search_execution_provider_sheet_template?`<div class="brain-meta"><strong>Search sheet:</strong> provider-guided search worksheet ready for copy/use before import.</div>`:''}
          ${searchQueryExecutionBatchPlan.search_execution_capture_workbook_template?`<div class="brain-meta"><strong>Search workbook:</strong> combined search-and-capture worksheet ready for copy/fill/import.</div>`:''}
          ${executionRow.execution_status?`<div class="brain-meta"><strong>Execution status:</strong> ${esc(executionRow.execution_status||'—')} · <strong>Search group:</strong> ${esc(executionRow.search_group_key||'—')}</div>`:''}
          ${searchQueryExecutionBatchPlan.available?`<div class="brain-meta"><strong>Batch plan:</strong> ${esc(searchQueryExecutionBatchPlan.batch_reason||'—')} · <strong>Count:</strong> ${esc(String(searchQueryExecutionBatchPlan.candidate_count||0))}</div>`:''}
          ${(executionRow.imported_result_option_count||0)>0?`<div class="brain-meta"><strong>Imported options:</strong> ${esc(String(executionRow.imported_result_option_count||0))} · <strong>Top imported:</strong> ${esc((executionRow.top_imported_result||{}).search_result_title||(executionRow.top_imported_result||{}).source_url||'—')}</div>`:''}
          ${row.captured_result_title?`<div class="brain-meta"><strong>Captured result title:</strong> ${esc(row.captured_result_title||'—')}</div>`:''}
          ${row.captured_result_snippet?`<div class="brain-meta"><strong>Captured result snippet:</strong> ${esc(row.captured_result_snippet||'—')}</div>`:''}
          ${row.search_brief?`<div class="brain-meta"><strong>Search brief:</strong> ${esc(row.search_brief||'—')}</div>`:''}
          <div class="brain-actions">
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="showSearchQueryExecutionPacket('${esc(row.candidate_id)}')">Show search packet</button>
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionBatchPlan.available?'disabled':''} onclick="showProviderSearchSheet()">Show provider search sheet</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionBatchPlan.available?'disabled':''} onclick="showProviderSearchWorkbook()">Show search workbook</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionBatchPlan.available?'disabled':''} onclick="showProviderCaptureSheet()">Show provider sheet</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionSessionBundle.available?'disabled':''} onclick="showSearchSessionBundle()">Show session bundle</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionSessionBundle.available?'disabled':''} onclick="saveSearchSessionBundle()">Save session bundle</button>`:''}
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="materializeSearchQueryExecutionPlan()">Materialize search plan</button>
            ${action==='READ_OR_DRAFT_REFERENCE'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="readArticleReference('${esc(row.candidate_id)}')">Draft ref</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchQueryResults()">Import results</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchQueryResultsOrdered(false)">Import ordered</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionSessionBundle.available?'disabled':''} onclick="importSearchQueryExecutionSessionRows(false)">Import session rows</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||Number((searchQueryExecutionSessionBundle.summary||{}).ready_rows||0)<1?'disabled':''} onclick="importSavedSearchQueryExecutionSessionRows(false)">Import saved ready rows</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchQueryResultsAndCaptureSingletons()">Import + capture singletons</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchQueryResultsOrdered(true)">Import ordered + capture singletons</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionSessionBundle.available?'disabled':''} onclick="importSearchQueryExecutionSessionRows(true)">Import session rows + capture singletons</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||Number((searchQueryExecutionSessionBundle.summary||{}).ready_rows||0)<1?'disabled':''} onclick="importSavedSearchQueryExecutionSessionRows(true)">Import saved ready rows + capture singletons</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="captureQuerySeedSearchResult('${esc(row.candidate_id)}')">Capture result</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn review" ${!liveData?.run_id||!searchQueryExecutionBatchPlan.available||Number(searchQueryExecutionBatchPlan.candidate_count||0)<2?'disabled':''} onclick="captureSearchResultBatch()">Capture source batch</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn accept" ${!liveData?.run_id||(executionRow.imported_result_option_count||0)<1?'disabled':''} onclick="promoteImportedSearchResult('${esc(row.candidate_id)}')">Promote imported</button>`:''}
            ${action==='CAPTURE_SEARCH_RESULT'?`<button class="brain-btn accept" ${!liveData?.run_id||(executionRow.imported_result_option_count||0)<1?'disabled':''} onclick="resolveImportedSearchResult('${esc(row.candidate_id)}')">Resolve imported excerpt</button>`:''}
            ${action==='RESOLVE_REFERENCE_EXCERPT'?`<button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="resolveQuerySeedDraft('${esc(row.candidate_id)}')">Resolve excerpt</button>`:''}
            ${action==='RESOLVE_REFERENCE_EXCERPT'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="resolveQuerySeedDraftFull('${esc(row.candidate_id)}')">Resolve full packet</button>`:''}
          </div>
          ${action==='CAPTURE_SEARCH_RESULT'&&searchSessionFormRows.length?`
            <details class="brain-editor-wrap" ${searchSessionFormOpen?'open':''} ontoggle="syncSearchSessionFormOpen(this)">
              <summary>Inline visible-result capture</summary>
              <div class="brain-editor-meta">Captura nativa por fila. Edita URL, título, snippet, excerpt, selección y notas aquí; luego guarda o importa las filas ready sin pasar por JSON ni prompts.</div>
              <div class="brain-session-grid">
                ${searchSessionFormRows.map(sessionRow=>`
                  <div class="brain-session-row">
                    <div class="brain-session-row-head">
                      <div>
                        <div class="brain-session-row-name">${esc(sessionRow.title||sessionRow.candidate_id||'candidate')}</div>
                        <div class="brain-session-row-meta">Candidate: ${esc(sessionRow.candidate_id||'—')} · Row ${esc(String(sessionRow.row_index||0))} · ${esc(sessionRow.provider_display_name||sessionRow.provider_key||'provider')} · ${esc(sessionRow.query_family||'query')}</div>
                        <div class="brain-session-row-meta">Search line 1: ${esc(sessionRow.search_line_1||'—')}</div>
                        ${sessionRow.search_line_2?`<div class="brain-session-row-meta">Search line 2: ${esc(sessionRow.search_line_2||'—')}</div>`:''}
                        ${(sessionRow.evidence_targets||[]).length?`<div class="brain-session-row-meta">Evidence targets: ${esc((sessionRow.evidence_targets||[]).join(' | ')||'—')}</div>`:''}
                      </div>
                      <span class="brain-state ${sessionRow.reference_excerpt?'accepted_for_case_use':((sessionRow.source_url&&(sessionRow.search_result_title||sessionRow.search_result_snippet))?'needs_review':'candidate')}">${esc(sessionRow.reference_excerpt?'ready_excerpt':((sessionRow.source_url&&(sessionRow.search_result_title||sessionRow.search_result_snippet))?'ready_import':'draft'))}</span>
                    </div>
                    <div class="brain-session-fields">
                      <div class="brain-session-field wide">
                        <label>Source URL</label>
                        <input type="text" data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="source_url" value="${esc(sessionRow.source_url||'')}" oninput="updateSearchSessionRowFieldFromElement(this)">
                      </div>
                      <div class="brain-session-field wide">
                        <label>Search result title</label>
                        <input type="text" data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="search_result_title" value="${esc(sessionRow.search_result_title||'')}" oninput="updateSearchSessionRowFieldFromElement(this)">
                      </div>
                      <div class="brain-session-field wide">
                        <label>Visible result snippet</label>
                        <textarea data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="search_result_snippet" oninput="updateSearchSessionRowFieldFromElement(this)">${esc(sessionRow.search_result_snippet||'')}</textarea>
                      </div>
                      <div class="brain-session-field wide">
                        <label>Paste provider row</label>
                        <textarea id="search-session-parse-${esc(sessionRow.candidate_id||'')}" data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="parse_input" oninput="updateSearchSessionRowFieldFromElement(this)" placeholder="Paste one provider row here. TSV, compact line, packet block, or provider-native row are accepted.">${esc((window._searchSessionRowDrafts||{})[sessionRow.candidate_id||'']?.parse_input||'')}</textarea>
                      </div>
                      <div class="brain-session-field wide">
                        <label>Reference excerpt</label>
                        <textarea data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="reference_excerpt" oninput="updateSearchSessionRowFieldFromElement(this)">${esc(sessionRow.reference_excerpt||'')}</textarea>
                      </div>
                      <div class="brain-session-field">
                        <label>Selected visible hit</label>
                        <label class="brain-session-check"><input type="checkbox" data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="selected" ${sessionRow.selected?'checked':''} onchange="updateSearchSessionRowFieldFromElement(this)"> Mark selected</label>
                      </div>
                      <div class="brain-session-field wide">
                        <label>Notes</label>
                        <textarea data-candidate-id="${esc(sessionRow.candidate_id||'')}" data-field="notes" oninput="updateSearchSessionRowFieldFromElement(this)">${esc(sessionRow.notes||'')}</textarea>
                      </div>
                    </div>
                    <div class="brain-actions" style="margin-top:8px">
                      <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="parseVisibleSearchSessionRow('${esc(sessionRow.candidate_id||'')}')">Parse row</button>
                    </div>
                  </div>`).join('')}
              </div>
              <div class="brain-actions" style="margin-top:10px">
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="loadSearchSessionFormFromBundle()">Load live rows</button>
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="saveVisibleSearchSessionRows()">Save visible rows</button>
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importVisibleSearchSessionRows(false)">Import visible ready rows</button>
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importVisibleSearchSessionRows(true)">Import visible ready rows + capture singletons</button>
              </div>
            </details>`:''}
          ${action==='CAPTURE_SEARCH_RESULT'&&searchQueryExecutionSessionBundle.available?`
            <details class="brain-editor-wrap" ${searchSessionEditorOpen?'open':''} ontoggle="syncSearchSessionEditorOpen(this)">
              <summary>Inline search session editor</summary>
              <div class="brain-editor-meta">Editor stateful para search session rows. Puedes cargar la sesión viva, editar filas, guardar el store run-scoped e importar las filas ready sin volver a abrir prompts.</div>
              <textarea id="search-session-editor" class="brain-editor-area" oninput="updateSearchSessionEditorDraft(this)">${esc(searchSessionEditorText)}</textarea>
              <div class="brain-actions" style="margin-top:10px">
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="loadSearchSessionEditorFromBundle()">Load live session</button>
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="saveSearchSessionEditorFromInline()">Save editor</button>
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchSessionEditorFromInline(false)">Import editor ready rows</button>
                <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="importSearchSessionEditorFromInline(true)">Import editor ready rows + capture singletons</button>
              </div>
            </details>`:''}
          ${nextSearchResultCaptureRows.length?`<div class="brain-meta"><strong>Next search rows:</strong> ${esc(nextSearchResultCaptureRows.map(item=>`${item.provider_key||'provider'}:${item.next_capture_action||'NO_ACTION'}:${item.title||item.candidate_id||''}`).join(' | ')||'—')}</div>`:''}
          ${nextSearchQueryExecutionRows.length?`<div class="brain-meta"><strong>Next search executions:</strong> ${esc(nextSearchQueryExecutionRows.map(item=>`${item.provider_key||'provider'}:${item.query_family||'query'}:${item.execution_status||'state'}`).join(' | ')||'—')}</div>`:''}
          ${searchQueryExecutionManifest.exists?`<div class="brain-meta"><strong>Manifest:</strong> ${esc(searchQueryExecutionManifest.path||'—')}</div>`:''}
          ${searchQueryResultImportStore.exists?`<div class="brain-meta"><strong>Imported results store:</strong> ${esc(searchQueryResultImportStore.path||'—')}</div>`:''}
        </div>`);
    }else{
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Search Result Capture</div>
              <div class="brain-meta">No pending query-seed search capture work remains.</div>
            </div>
            <span class="brain-state accepted_for_case_use">queue_clear</span>
          </div>
          <div class="brain-meta"><strong>Closed:</strong> ${esc(String(searchResultCaptureSummary.closed||0))}/${esc(String(searchResultCaptureSummary.total||0))} · <strong>Captured:</strong> ${esc(String(searchResultCaptureSummary.result_captured||0))}</div>
        </div>`);
    }
  }
  if(referenceResolutionSequence.length){
    if(currentReferenceResolution && currentReferenceResolution.candidate_id){
      const row=currentReferenceResolution;
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Reference Draft Review</div>
              <div class="brain-meta">One-by-one resolution queue · ${esc(String(referenceResolutionQueueSummary.current_position||0))}/${esc(String(referenceResolutionQueueSummary.total||0))}</div>
            </div>
            <span class="brain-state candidate">${esc(row.reference_state||'query_seed_draft')}</span>
          </div>
          <div class="brain-meta"><strong>Provider:</strong> ${esc(row.provider_key||'—')} · <strong>Title:</strong> ${esc(row.title||row.candidate_id||'—')}</div>
          <div class="brain-meta"><strong>URL:</strong> ${esc(row.source_url||'—')}</div>
          <div class="brain-meta"><strong>Excerpt:</strong> ${esc(row.reference_excerpt||'—')}</div>
          ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.query_family)?`<div class="brain-meta"><strong>Query family:</strong> ${esc(row.draft_resolution_prefill.query_family||'—')} · <strong>Primary query:</strong> ${esc(row.draft_resolution_prefill.primary_query||'—')}</div>`:''}
          ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.evidence_targets&&row.draft_resolution_prefill.evidence_targets.length)?`<div class="brain-meta"><strong>Evidence targets:</strong> ${esc((row.draft_resolution_prefill.evidence_targets||[]).join(' | ')||'—')}</div>`:''}
          ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.search_surface)?`<div class="brain-meta"><strong>Search surface:</strong> ${esc(row.draft_resolution_prefill.search_surface||'—')}</div>`:''}
          ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.execution_hint)?`<div class="brain-meta"><strong>Execution hint:</strong> ${esc(row.draft_resolution_prefill.execution_hint||'—')}</div>`:''}
          ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.captured_result_title)?`<div class="brain-meta"><strong>Captured result title:</strong> ${esc(row.draft_resolution_prefill.captured_result_title||'—')}</div>`:''}
          ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.captured_result_snippet)?`<div class="brain-meta"><strong>Captured result snippet:</strong> ${esc(row.draft_resolution_prefill.captured_result_snippet||'—')}</div>`:''}
          ${(row.acquisition_result&&row.acquisition_result.search_brief)?`<div class="brain-meta"><strong>Search brief:</strong> ${esc(row.acquisition_result.search_brief||'—')}</div>`:''}
          ${referenceResolutionBatchPlan.available?`<div class="brain-meta"><strong>Batch plan:</strong> ${esc(referenceResolutionBatchPlan.summary||'—')}</div>`:''}
          ${referenceResolutionBatchPlan.available&&referenceResolutionBatchPlan.batch_reason?`<div class="brain-meta"><strong>Batch reason:</strong> ${esc(referenceResolutionBatchPlan.batch_reason||'—')}</div>`:''}
          ${referenceResolutionBatchPlan.available&&(referenceResolutionBatchPlan.query_families||[]).length?`<div class="brain-meta"><strong>Batch query families:</strong> ${esc((referenceResolutionBatchPlan.query_families||[]).join(' | ')||'—')}</div>`:''}
          ${referenceResolutionBatchPlan.available&&(referenceResolutionBatchPlan.evidence_targets||[]).length?`<div class="brain-meta"><strong>Batch evidence targets:</strong> ${esc((referenceResolutionBatchPlan.evidence_targets||[]).join(' | ')||'—')}</div>`:''}
          <div class="brain-actions">
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="captureQuerySeedSearchResult('${esc(row.candidate_id)}')">Capture result</button>
            <button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="resolveQuerySeedDraft('${esc(row.candidate_id)}')">Resolve excerpt</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="resolveQuerySeedDraftFull('${esc(row.candidate_id)}')">Resolve full packet</button>
            <button class="brain-btn review" ${!liveData?.run_id||!referenceResolutionBatchPlan.available||!referenceResolutionBatchPlan.captured_ready||Number(referenceResolutionBatchPlan.candidate_count||0)<2?'disabled':''} onclick="resolveCapturedReferenceDraftBatch()">Resolve captured batch</button>
            <button class="brain-btn review" ${!liveData?.run_id||!referenceResolutionBatchPlan.available||Number(referenceResolutionBatchPlan.candidate_count||0)<2?'disabled':''} onclick="resolveReferenceDraftBatch()">Resolve source batch</button>
            <button class="brain-btn review" ${!liveData?.run_id||!referenceResolutionBatchPlan.available||Number(referenceResolutionBatchPlan.candidate_count||0)<2?'disabled':''} onclick="resolveReferenceDraftBatchFull()">Resolve full source batch</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="editArticleReference('${esc(row.candidate_id)}')">Modify</button>
          </div>
          ${nextReferenceResolutionRows.length?`<div class="brain-meta"><strong>Next drafts:</strong> ${esc(nextReferenceResolutionRows.map(item=>item.title||item.candidate_id||'').join(' | ')||'—')}</div>`:''}
        </div>`);
    }else{
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Reference Draft Review</div>
              <div class="brain-meta">No pending query-seed drafts remain in the reference-resolution queue.</div>
            </div>
            <span class="brain-state accepted_for_case_use">queue_clear</span>
          </div>
          <div class="brain-meta"><strong>Closed:</strong> ${esc(String(referenceResolutionQueueSummary.closed||0))}/${esc(String(referenceResolutionQueueSummary.total||0))}</div>
        </div>`);
    }
  }
  if(knowledgeAtomRefreshSummary.exists||knowledgeAtomRefreshSummary.summary||combinationRerankSummary.exists||combinationRerankSummary.summary){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Atom Refresh And Rerank</div>
            <div class="brain-meta">Closed loop from enriched reference to atoms, source coverage and latent combination rerank.</div>
          </div>
          <span class="brain-state ${esc((combinationRerankSummary.rerank_changed||knowledgeAtomRefreshSummary.meaningful_delta)?'needs_review':'candidate')}">${esc((combinationRerankSummary.rerank_changed||knowledgeAtomRefreshSummary.meaningful_delta)?'updated':'steady')}</span>
        </div>
        <div class="brain-meta"><strong>Atom refresh:</strong> ${esc(knowledgeAtomRefreshSummary.summary||'—')}</div>
        <div class="brain-meta"><strong>Added atoms:</strong> ${esc((knowledgeAtomRefreshSummary.added_atom_ids||[]).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Rerank:</strong> ${esc(combinationRerankSummary.summary||'—')}</div>
        <div class="brain-meta"><strong>Top change:</strong> ${esc(String(combinationRerankSummary.next_combination_changed||false))} · <strong>Sequence changed:</strong> ${esc(String(combinationRerankSummary.top_sequence_changed||false))}</div>
        <div class="brain-meta"><strong>Latent added:</strong> ${esc((combinationRerankSummary.added_combination_ids||[]).join(' | ')||'—')}</div>
      </div>`);
  }
  if(discoveryReview.length){
    sections.push(...discoveryReview.map(row=>{
      const decision=row.operator_decision||'candidate';
      const refState=row.reference_state||'metadata_only';
      const patternText=(row.matched_pattern_ids||[]).join(' · ')||'—';
      const comboText=(row.matched_combination_ids||[]).join(' · ')||'—';
      return `
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Discovery Candidate · ${esc(row.title||row.candidate_id||'Candidate')}</div>
              <div class="brain-meta">${esc(row.provider_key||'provider')} · priority ${esc(String(row.priority_score||0))} · ref ${esc(refState)}</div>
            </div>
            <span class="brain-state ${esc(decision)}">${esc(decisionLabel(decision))}</span>
          </div>
          <div class="brain-meta"><strong>DOI:</strong> ${esc(row.doi||'—')} · <strong>Journal:</strong> ${esc(row.journal||'—')} · <strong>Year:</strong> ${esc(row.published_year||'—')}</div>
          <div class="brain-meta"><strong>URL:</strong> ${esc(row.source_url||'—')}</div>
          <div class="brain-meta"><strong>Expected PDF:</strong> ${esc(row.expected_pdf_name||'—')}</div>
          <div class="brain-meta"><strong>Patterns:</strong> ${esc(patternText)}</div>
          <div class="brain-meta"><strong>Combinations:</strong> ${esc(comboText)}</div>
          ${((row.metadata_payload||{}).notes)?`<div class="brain-meta"><strong>Notes:</strong> ${esc((row.metadata_payload||{}).notes||'')}</div>`:''}
          ${row.decision_reason?`<div class="brain-meta"><strong>Decision note:</strong> ${esc(row.decision_reason)}</div>`:''}
          <div class="brain-actions">
            <button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="adjudicateDiscoveryCandidate('${esc(row.candidate_id)}','accepted_for_reference_use')">Accept</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="adjudicateDiscoveryCandidate('${esc(row.candidate_id)}','needs_review')">Needs review</button>
            <button class="brain-btn reject" ${!liveData?.run_id?'disabled':''} onclick="adjudicateDiscoveryCandidate('${esc(row.candidate_id)}','rejected_for_reference_use')">Reject</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="editDiscoveryCandidate('${esc(row.candidate_id)}')">Modify</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="readArticleReference('${esc(row.candidate_id)}')">${esc((String(row.candidate_id||'').startsWith('queryseed-'))?'Draft ref':'Read reference')}</button>
          </div>
        </div>`;
    }));
  }
  if(articleReferences.length){
    sections.push(...articleReferences.map(row=>`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Article Reference · ${esc(row.title||row.candidate_id||'Reference')}</div>
            <div class="brain-meta">${esc(row.provider_key||'provider')} · ${esc(row.reference_state||'metadata_only')}</div>
          </div>
          <span class="brain-state ${esc(((row.reference_state||'metadata_only')==='visible_text_enriched'||(row.reference_state||'metadata_only')==='manual_text_enriched')?'accepted_for_case_use':'candidate')}">${esc(row.reference_state||'metadata_only')}</span>
        </div>
        <div class="brain-meta"><strong>URL:</strong> ${esc(row.source_url||'—')}</div>
        <div class="brain-meta"><strong>Excerpt:</strong> ${esc(row.reference_excerpt||'—')}</div>
        ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.query_family)?`<div class="brain-meta"><strong>Query family:</strong> ${esc(row.draft_resolution_prefill.query_family||'—')} · <strong>Primary query:</strong> ${esc(row.draft_resolution_prefill.primary_query||'—')}</div>`:''}
        ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.evidence_targets&&row.draft_resolution_prefill.evidence_targets.length)?`<div class="brain-meta"><strong>Evidence targets:</strong> ${esc((row.draft_resolution_prefill.evidence_targets||[]).join(' | ')||'—')}</div>`:''}
        ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.search_surface)?`<div class="brain-meta"><strong>Search surface:</strong> ${esc(row.draft_resolution_prefill.search_surface||'—')}</div>`:''}
        ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.execution_hint)?`<div class="brain-meta"><strong>Execution hint:</strong> ${esc(row.draft_resolution_prefill.execution_hint||'—')}</div>`:''}
        ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.captured_result_title)?`<div class="brain-meta"><strong>Captured result title:</strong> ${esc(row.draft_resolution_prefill.captured_result_title||'—')}</div>`:''}
        ${(row.draft_resolution_prefill&&row.draft_resolution_prefill.captured_result_snippet)?`<div class="brain-meta"><strong>Captured result snippet:</strong> ${esc(row.draft_resolution_prefill.captured_result_snippet||'—')}</div>`:''}
        ${(row.acquisition_result&&row.acquisition_result.search_brief)?`<div class="brain-meta"><strong>Search brief:</strong> ${esc(row.acquisition_result.search_brief||'—')}</div>`:''}
        ${row.notes?`<div class="brain-meta"><strong>Notes:</strong> ${esc(row.notes)}</div>`:''}
        <div class="brain-meta"><strong>Patterns:</strong> ${esc((row.matched_pattern_ids||[]).join(' · ')||'—')}</div>
        <div class="brain-actions">
          ${row.reference_state==='query_seed_draft'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="captureQuerySeedSearchResult('${esc(row.candidate_id)}')">Capture result</button>`:''}
          ${row.reference_state==='query_seed_draft'?`<button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="resolveQuerySeedDraft('${esc(row.candidate_id)}')">Resolve excerpt</button>`:''}
          ${row.reference_state==='query_seed_draft'?`<button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="resolveQuerySeedDraftFull('${esc(row.candidate_id)}')">Resolve full packet</button>`:''}
          <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="editArticleReference('${esc(row.candidate_id)}')">Modify</button>
        </div>
      </div>
    `));
  }
  if(latentClusters.length){
    sections.push(...latentClusters.map(cluster=>{
      const memberRows=admissibleLatent.filter(row=>(cluster.candidate_ids||[]).includes(row.combination_id));
      const decisions=new Set(memberRows.map(row=>row.operator_decision||'needs_review'));
      const clusterDecision=(decisions.size===1?[...decisions][0]:'needs_review');
      const differentiators=memberRows.flatMap(row=>row.context_differentiators||[]).filter(Boolean);
      const whyGeneric=memberRows.map(row=>row.why_this_asset_is_not_generic||'').filter(Boolean)[0]||'—';
      return `
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Latent Cluster · ${esc(cluster.cluster_label||cluster.combination_family||cluster.cluster_id||'cluster')}</div>
              <div class="brain-meta">${esc(cluster.context_signature||'context-unbound')} · ${esc(String(cluster.candidate_count||0))} candidates</div>
            </div>
            <span class="brain-state ${esc(clusterDecision)}">${esc(decisionLabel(clusterDecision))}</span>
          </div>
          <div class="brain-meta"><strong>Patterns:</strong> ${esc((cluster.pattern_ids||[]).join(' · ')||'—')}</div>
          <div class="brain-meta"><strong>Top score:</strong> ${esc(String(cluster.top_score||0))} · <strong>Context risk:</strong> ${esc(cluster.context_binding_insufficiency_risk||'clear')}</div>
          <div class="brain-meta"><strong>Override:</strong> ${esc(cluster.override_state||'base')} · <strong>Source clusters:</strong> ${esc((cluster.source_cluster_ids||[]).join(' | ')||'—')}</div>
          <div class="brain-meta"><strong>Why this asset is not generic:</strong> ${esc(whyGeneric)}</div>
          <div class="brain-meta"><strong>Differentiators:</strong> ${esc(differentiators.join(' | ')||'—')}</div>
          <div class="brain-actions">
            <button class="brain-btn accept" ${!liveData?.run_id?'disabled':''} onclick="adjudicateLatentCluster('${esc(cluster.cluster_id)}','accepted_for_case_use')">Accept cluster</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="adjudicateLatentCluster('${esc(cluster.cluster_id)}','needs_review')">Needs review</button>
            <button class="brain-btn reject" ${!liveData?.run_id?'disabled':''} onclick="adjudicateLatentCluster('${esc(cluster.cluster_id)}','rejected_for_case_use')">Reject cluster</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="splitLatentCluster('${esc(cluster.cluster_id)}')">Split cluster</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="mergeLatentCluster('${esc(cluster.cluster_id)}')">Merge cluster</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="explainLatentCluster('${esc(cluster.cluster_id)}')">Explain context divergence</button>
            <button class="brain-btn reject" ${!liveData?.run_id?'disabled':''} onclick="suppressGenericTemplate('${esc(cluster.cluster_id)}')">Suppress generic template</button>
          </div>
        </div>`;
    }));
  }
  if(reviewSequence.length){
    if(currentCombinationReview && currentCombinationReview.combination_id){
      const row=currentCombinationReview;
      const followOnRow=combinationFollowOnResearch.find(item=>item.combination_id===row.combination_id)||{};
      const followOnManifest=combinationFollowOnExecutionManifests.find(item=>item.combination_id===row.combination_id)||{};
      const decision=row.operator_decision||'candidate';
      const isBlocked=row.validator_state==='blocked';
      const actionDisabled=(!liveData?.run_id||isBlocked)?'disabled':'';
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Combination Review</div>
              <div class="brain-meta">One-by-one adjudication queue · ${esc(String(reviewQueueSummary.current_position||0))}/${esc(String(reviewQueueSummary.total||0))} · batch ${esc(String(reviewQueueSummary.batch_size||1))}</div>
            </div>
            <span class="brain-state ${esc(decision)}">${esc(decisionLabel(decision))}</span>
          </div>
          <div class="brain-meta"><strong>Origin:</strong> ${esc(row.review_origin||'registered')} · <strong>Name:</strong> ${esc(row.combination_name||row.combination_id||'Combination')}</div>
          <div class="brain-meta"><strong>Deferred count:</strong> ${esc(String(reviewQueueSummary.deferred||0))} · <strong>Control batch:</strong> ${esc(String(combinationReviewControlStore.batch_size||1))}</div>
          <div class="brain-meta"><strong>Hypothesis:</strong> ${esc(row.combined_hypothesis||'—')}</div>
          ${row.strategic_risk?`<div class="brain-meta"><strong>Risk:</strong> ${esc(row.strategic_risk)}</div>`:''}
          <div class="brain-meta"><strong>Layers:</strong> ${esc((row.pattern_layers||[]).join(' · ')||'—')} · <strong>Score:</strong> ${esc(String(row.score||0))}</div>
          <div class="brain-meta"><strong>Why this asset is not generic:</strong> ${esc(row.why_this_asset_is_not_generic||'—')}</div>
          <div class="brain-meta"><strong>Context differentiators:</strong> ${esc((row.context_differentiators||[]).join(' | ')||'—')}</div>
          <div class="brain-meta"><strong>Knowledge atoms:</strong> ${esc(String(row.knowledge_atom_count||0))} · <strong>Docs:</strong> ${esc((row.supporting_document_refs||[]).join(' | ')||'—')}</div>
          <div class="brain-meta"><strong>Minimum evidence:</strong> ${esc((row.minimum_evidence||[]).join(' · ')||'—')}</div>
          <div class="brain-meta"><strong>TAD:</strong> ${esc(row.tad_action||'—')} · <strong>Allowed language:</strong> ${esc(row.allowed_language||'—')}</div>
          <div class="brain-meta"><strong>Follow-on research:</strong> ${esc((followOnRow.recommended_source_families||[]).join(' | ')||'—')} · <strong>Flags:</strong> ${esc((followOnRow.reasoning_flags||[]).join(' | ')||'—')}</div>
          <div class="brain-meta"><strong>Execution queries:</strong> ${esc((followOnManifest.query_families||[]).join(' | ')||'—')}</div>
          <div class="brain-meta"><strong>Execution plan:</strong> ${esc((followOnManifest.execution_rows||[]).map(item=>`${item.source_family}: ${(item.provider_targets||[]).join(', ')} -> ${(item.query_families||[]).join(', ')}`).join(' | ')||'—')}</div>
          <div class="brain-meta"><strong>Provider query templates:</strong> ${esc((followOnManifest.execution_rows||[]).flatMap(item=>(item.provider_query_templates||[]).map(template=>`${template.provider_key} [${template.query_family}] ${template.primary_query}`)).join(' | ')||'—')}</div>
          ${row.edit_timestamp?`<div class="brain-meta"><strong>Edited:</strong> ${esc(row.edit_timestamp)}</div>`:''}
          ${isBlocked?`<div class="brain-meta"><strong>Validator block:</strong> ${esc((row.validator_findings||[]).map(v=>v.message).join(' | ')||'Combination blocked by validator.')}</div>`:''}
          <div class="brain-actions">
            <button class="brain-btn accept" ${actionDisabled} onclick="adjudicateCombination('${esc(row.combination_id)}','accepted_for_case_use')">Accept</button>
            <button class="brain-btn review" ${actionDisabled} onclick="editCombination('${esc(row.combination_id)}')">Modify</button>
            <button class="brain-btn review" ${actionDisabled} onclick="deferCombinationReview('${esc(row.combination_id)}')">Defer</button>
            <button class="brain-btn reject" ${actionDisabled} onclick="adjudicateCombination('${esc(row.combination_id)}','rejected_for_case_use')">Reject</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="setCombinationReviewBatchSize()">Set batch size</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="materializeCombinationFollowOnManifest('${esc(row.combination_id)}')">Materialize research plan</button>
            <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="seedCombinationResearchCandidates('${esc(row.combination_id)}')">Seed research leads</button>
          </div>
          ${(combinationFollowOnManifestStore.exists)?`<div class="brain-meta"><strong>Stored manifests:</strong> ${esc(String(combinationFollowOnManifestStore.stored_manifest_count||0))} · <strong>Path:</strong> ${esc(combinationFollowOnManifestStore.path||'—')}</div>`:''}
          ${nextCombinationReviews.length?`<div class="brain-meta"><strong>Next:</strong> ${esc(nextCombinationReviews.map(item=>item.combination_name||item.combination_id||'').join(' | ')||'—')}</div>`:''}
        </div>`);
    }else{
      sections.push(`
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Current Combination Review</div>
              <div class="brain-meta">No pending combinations remain in the sequential review queue.</div>
            </div>
            <span class="brain-state accepted_for_case_use">queue_clear</span>
          </div>
          <div class="brain-meta"><strong>Closed:</strong> ${esc(String(reviewQueueSummary.closed||0))}/${esc(String(reviewQueueSummary.total||0))}</div>
        </div>`);
    }
  }
  if((providerHandoffSummary.provider_count||0)>0){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Provider Session Handoff</div>
            <div class="brain-meta">Per-provider next step before live licensed acquisition.</div>
          </div>
          <span class="brain-state candidate">${esc(String(providerHandoffSummary.provider_count||0))} providers</span>
        </div>
        <div class="brain-meta"><strong>Plan:</strong> ${esc((providerHandoffBundle.provider_rows||[]).map(row=>`${row.provider_key}: ${row.recommended_action}`).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Access route:</strong> ${esc((providerHandoffBundle.provider_rows||[]).map(row=>`${row.provider_key}: ${row.access_route||'direct_provider'}${row.institution_name?` (${row.institution_name})`:''}`).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Bootstrap:</strong> ${esc((providerHandoffBundle.provider_rows||[]).map(row=>`${row.provider_key}: ${row.display_command||'—'}`).join(' | ')||'—')}</div>
        <div class="brain-meta"><strong>Validate:</strong> ${esc((providerHandoffBundle.provider_rows||[]).map(row=>`${row.provider_key}: ${row.validate_display_command||'—'}`).join(' | ')||'—')}</div>
        <div class="brain-actions">
          <button class="brain-btn review" ${!liveData?.run_id?'disabled':''} onclick="materializeProviderHandoff()">Materialize provider handoff</button>
        </div>
        ${(providerSessionHandoffManifest.exists)?`<div class="brain-meta"><strong>Manifest:</strong> ${esc(providerSessionHandoffManifest.path||'—')}</div>`:''}
      </div>`);
  }
  if((licensed.extraction_review_register||[]).length||(licensed.approved_pattern_promotion_register||[]).length||(licensed.approved_combination_promotion_register||[]).length){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Extraction Promotion Review</div>
            <div class="brain-meta">La lane licenciada ya puede producir promotion rows versionables.</div>
          </div>
          <span class="brain-state needs_review">Ready for review</span>
        </div>
        <div class="brain-meta"><strong>Reviewed extractions:</strong> ${esc((licensed.extraction_review_register||[]).map(row=>row.extraction_id||row.id||'').filter(Boolean).join(' · ')||'—')}</div>
        <div class="brain-meta"><strong>Pattern promotions:</strong> ${esc((licensed.approved_pattern_promotion_register||[]).map(row=>row.pattern_id||row.promotion_id||'').filter(Boolean).join(' · ')||'—')}</div>
        <div class="brain-meta"><strong>Combination promotions:</strong> ${esc((licensed.approved_combination_promotion_register||[]).map(row=>row.combination_id||row.promotion_id||'').filter(Boolean).join(' · ')||'—')}</div>
      </div>`);
  }
  if(promotionReview.length){
    sections.push(...promotionReview.map(row=>{
      const decision=row.operator_decision||'candidate';
      const actionDisabled=!liveData?.run_id?'disabled':'';
      return `
        <div class="brain-item">
          <div class="brain-head">
            <div>
              <div class="brain-name">Promotion · ${esc(row.subject_name||row.subject_id||row.promotion_id||'Promotion')}</div>
              <div class="brain-meta">${esc(row.promotion_type||'promotion')} · ${esc(row.promotion_state||'ready_for_registry_review')}</div>
            </div>
            <span class="brain-state ${esc(decision)}">${esc(decisionLabel(decision))}</span>
          </div>
          <div class="brain-meta"><strong>Source basis:</strong> ${esc(row.source_basis_id||'—')} · <strong>Document:</strong> ${esc(row.document_ref||'—')}</div>
          ${row.knowledge_type?`<div class="brain-meta"><strong>Knowledge:</strong> ${esc(row.knowledge_type)}</div>`:''}
          <div class="brain-meta"><strong>Minimum evidence:</strong> ${esc((row.minimum_evidence||[]).join(' · ')||'—')}</div>
          ${row.edit_timestamp?`<div class="brain-meta"><strong>Edited:</strong> ${esc(row.edit_timestamp)}</div>`:''}
          ${row.decision_reason?`<div class="brain-meta"><strong>Decision note:</strong> ${esc(row.decision_reason)}</div>`:''}
          <div class="brain-actions">
            <button class="brain-btn accept" ${actionDisabled} onclick="adjudicatePromotion('${esc(row.promotion_id)}','${esc(row.promotion_type)}','accepted_for_registry_review')">Accept</button>
            <button class="brain-btn review" ${actionDisabled} onclick="adjudicatePromotion('${esc(row.promotion_id)}','${esc(row.promotion_type)}','needs_review')">Needs review</button>
            <button class="brain-btn reject" ${actionDisabled} onclick="adjudicatePromotion('${esc(row.promotion_id)}','${esc(row.promotion_type)}','rejected_for_registry_review')">Reject</button>
            <button class="brain-btn review" ${actionDisabled} onclick="editPromotion('${esc(row.promotion_id)}','${esc(row.promotion_type)}')">Modify</button>
          </div>
        </div>`;
    }));
  }
  if((registryReviewSummary.accepted_total||0)>0){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Registry Review Bundle</div>
            <div class="brain-meta">Accepted promotions ready for registry review export.</div>
          </div>
          <span class="brain-state accepted_for_registry_review">${esc(String(registryReviewSummary.accepted_total||0))} ready</span>
        </div>
        <div class="brain-meta"><strong>Patterns:</strong> ${esc(String(registryReviewSummary.accepted_pattern_count||0))} · <strong>Combinations:</strong> ${esc(String(registryReviewSummary.accepted_combination_count||0))}</div>
      </div>`);
  }
  if((registryStageSummary.total_rows||0)>0){
    sections.push(`
      <div class="brain-item">
        <div class="brain-head">
          <div>
            <div class="brain-name">Registry Stage Preview</div>
            <div class="brain-meta">Candidate file plan before writing to registry.</div>
          </div>
          <span class="brain-state accepted_for_registry_review">${esc(String(registryStageSummary.write_candidate_file_count||0))} files</span>
        </div>
        <div class="brain-meta"><strong>Root:</strong> ${esc(registryStagePreview.registry_root||'—')}</div>
        <div class="brain-meta"><strong>Writes:</strong> ${esc(String(registryStageSummary.write_candidate_file_count||0))} · <strong>Skips:</strong> ${esc(String(registryStageSummary.skip_existing_id_count||0))}</div>
        <div class="brain-meta"><strong>Plan:</strong> ${esc((registryStagePreview.stage_rows||[]).map(row=>`${row.item_type}:${row.item_id} -> ${row.stage_action}`).join(' | ')||'—')}</div>
        <div class="brain-actions">
          <button class="brain-btn accept" ${!liveData?.run_id||!(registryStageSummary.write_candidate_file_count>0)?'disabled':''} onclick="materializeRegistryStage()">Materialize stage files</button>
          <button class="brain-btn review" ${!liveData?.run_id||!(registryStageCandidateSummary.materialized_count>0)?'disabled':''} onclick="mergeRegistryStage()">Merge to registry</button>
        </div>
        ${(registryStageCandidateManifest.exists)?`<div class="brain-meta"><strong>Materialized:</strong> ${esc(String(registryStageCandidateSummary.materialized_count||0))} · <strong>Manifest:</strong> ${esc(registryStageCandidateManifest.path||'—')}</div>`:''}
        ${(registryStageMergeManifest.exists)?`<div class="brain-meta"><strong>Merged:</strong> ${esc(String(registryStageMergeSummary.merged_count||0))} · <strong>Merge manifest:</strong> ${esc(registryStageMergeManifest.path||'—')}</div>`:''}
      </div>`);
  }
  if(!reviewSequence.length){
    sections.push('<div class="empty">Sin combinaciones revisables para este run.</div>');
  }
  list.innerHTML=sections.join('');
}

async function adjudicateCombination(combinationId, operatorDecision){
  if(!liveData?.run_id)return;
  const defaultReasons={
    accepted_for_case_use:'Accepted from dashboard review.',
    needs_review:'Flagged for deeper review from dashboard.',
    rejected_for_case_use:'Rejected from dashboard review.'
  };
  const res=await fetch('/api/combination-decision',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      combination_id:combinationId,
      operator_decision:operatorDecision,
      decision_reason:defaultReasons[operatorDecision]||''
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo guardar la decisión.');
    return;
  }
  await refresh();
}

async function editCombination(combinationId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const rows=brain.combination_review_sequence_register||[];
  const row=rows.find(item=>item.combination_id===combinationId)||{};
  const name=window.prompt('Combination name:', row.combination_name||'');
  if(name===null)return;
  const combinedHypothesis=window.prompt('Combined hypothesis:', row.combined_hypothesis||'');
  if(combinedHypothesis===null)return;
  const strategicRisk=window.prompt('Strategic risk:', row.strategic_risk||'');
  if(strategicRisk===null)return;
  const minimumEvidence=window.prompt('Minimum evidence, separada por |:', (row.minimum_evidence||[]).join(' | '));
  if(minimumEvidence===null)return;
  const financialExposure=window.prompt('Financial exposure, separada por |:', (row.financial_exposure||[]).join(' | '));
  if(financialExposure===null)return;
  const tadAction=window.prompt('TAD action:', row.tad_action||'');
  if(tadAction===null)return;
  const prohibitedClaims=window.prompt('Prohibited claims, separadas por |:', (row.prohibited_claims||[]).join(' | '));
  if(prohibitedClaims===null)return;
  const allowedLanguage=window.prompt('Allowed language:', row.allowed_language||'');
  if(allowedLanguage===null)return;
  const res=await fetch('/api/combination-edit',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      combination_id:combinationId,
      patch:{
        combination_name:name,
        combined_hypothesis:combinedHypothesis,
        strategic_risk:strategicRisk,
        minimum_evidence:minimumEvidence.split('|').map(v=>v.trim()).filter(Boolean),
        financial_exposure:financialExposure.split('|').map(v=>v.trim()).filter(Boolean),
        tad_action:tadAction,
        prohibited_claims:prohibitedClaims.split('|').map(v=>v.trim()).filter(Boolean),
        allowed_language:allowedLanguage
      },
      auto_close_review:true,
      decision_reason:'Modified from sequential dashboard review.'
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo modificar la combinación.');
    return;
  }
  await refresh();
}

async function deferCombinationReview(combinationId){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/combination-review-control',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      action:'defer_current',
      combination_id:combinationId
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo diferir la combinación.');
    return;
  }
  await refresh();
}

async function setCombinationReviewBatchSize(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const currentBatchSize=((brain.combination_review_control_store||{}).batch_size)||1;
  const raw=window.prompt('Review batch size (1-10):', String(currentBatchSize));
  if(raw===null)return;
  const batchSize=Number(raw);
  if(!Number.isFinite(batchSize)){
    window.alert('Batch size inválido.');
    return;
  }
  const res=await fetch('/api/combination-review-control',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      action:'set_batch_size',
      batch_size:batchSize
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo actualizar el batch size.');
    return;
  }
  await refresh();
}

async function materializeCombinationFollowOnManifest(combinationId){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/combination-follow-on-manifest-materialize',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      combination_id:combinationId
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo materializar el research plan.');
    return;
  }
  await refresh();
}

async function adjudicateLatentCluster(clusterId, operatorDecision, decisionReason=''){
  if(!liveData?.run_id)return;
  const defaultReasons={
    accepted_for_case_use:'Accepted latent cluster from dashboard review.',
    needs_review:'Flagged latent cluster for deeper review from dashboard.',
    rejected_for_case_use:'Rejected latent cluster from dashboard review.'
  };
  const res=await fetch('/api/latent-cluster-decision',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      cluster_id:clusterId,
      operator_decision:operatorDecision,
      decision_reason:decisionReason||defaultReasons[operatorDecision]||''
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo guardar la decisión del cluster latente.');
    return;
  }
  await refresh();
}

async function splitLatentCluster(clusterId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const cluster=(brain.latent_combination_cluster_register||[]).find(row=>row.cluster_id===clusterId)||{};
  const candidateIds=cluster.candidate_ids||[];
  const candidateIdsRaw=window.prompt(
    `Candidate IDs to split, separadas por |:\n\n${candidateIds.join('\n')||'—'}`,
    candidateIds[0]||''
  );
  if(candidateIdsRaw===null)return;
  const selectedIds=(candidateIdsRaw||'').split('|').map(v=>v.trim()).filter(Boolean);
  if(!selectedIds.length){
    window.alert('Debes indicar al menos un candidate_id para hacer split.');
    return;
  }
  const clusterLabel=window.prompt('Split cluster label (optional):', `${cluster.combination_family||'latent'} split`);
  if(clusterLabel===null)return;
  const res=await fetch('/api/latent-cluster-split',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      source_cluster_id:clusterId,
      candidate_ids:selectedIds,
      cluster_label:(clusterLabel||'').trim(),
      decision_reason:'Split latent cluster from dashboard review.'
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo hacer split del cluster latente.');
    return;
  }
  await refresh();
}

async function mergeLatentCluster(clusterId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const clusterRows=(brain.latent_combination_cluster_register||[]).filter(row=>row.cluster_id!==clusterId);
  const targetDefault=(clusterRows[0]||{}).cluster_id||'';
  const targetClusterId=window.prompt(
    `Target cluster id:\n\n${clusterRows.map(row=>row.cluster_id).join('\n')||'—'}`,
    targetDefault
  );
  if(targetClusterId===null)return;
  const normalizedTarget=(targetClusterId||'').trim();
  if(!normalizedTarget){
    window.alert('Debes indicar un target cluster id.');
    return;
  }
  const res=await fetch('/api/latent-cluster-merge',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      source_cluster_id:clusterId,
      target_cluster_id:normalizedTarget,
      decision_reason:'Merged latent cluster from dashboard review.'
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo hacer merge del cluster latente.');
    return;
  }
  await refresh();
}

function explainLatentCluster(clusterId){
  const brain=liveData?.congruence_brain||{};
  const clusters=brain.latent_combination_cluster_register||[];
  const admissible=brain.admissible_combination_review_register||[];
  const cluster=clusters.find(row=>row.cluster_id===clusterId)||{};
  const members=admissible.filter(row=>(cluster.candidate_ids||[]).includes(row.combination_id));
  const message=[
    `Cluster: ${cluster.combination_family||cluster.cluster_id||'cluster'}`,
    `Context: ${cluster.context_signature||'context-unbound'}`,
    `Patterns: ${(cluster.pattern_ids||[]).join(' · ')||'—'}`,
    `Why not generic: ${members.map(row=>row.why_this_asset_is_not_generic||'').filter(Boolean)[0]||'—'}`,
    `Differentiators: ${members.flatMap(row=>row.context_differentiators||[]).filter(Boolean).join(' | ')||'—'}`
  ].join('\n\n');
  window.alert(message);
}

async function suppressGenericTemplate(clusterId){
  await adjudicateLatentCluster(
    clusterId,
    'rejected_for_case_use',
    'Suppressed from dashboard because the cluster still reads like a generic template and needs stronger asset-context rebinding.'
  );
}

async function triggerSourceFamilySearch(sourceFamily){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const rows=brain.research_campaign_trigger_register||[];
  const row=rows.find(item=>item.source_family===sourceFamily)||{};
  const reason=window.prompt(
    `Reason for deeper search on ${row.display_name||sourceFamily}:`,
    row.reason||'Queue deeper search from dashboard.'
  );
  if(reason===null)return;
  const res=await fetch('/api/source-family-trigger',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      source_family:sourceFamily,
      reason:reason
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo encolar el deeper-search trigger.');
    return;
  }
  await refresh();
}

async function setResearchLoopControl(action){
  if(!liveData?.run_id)return;
  let reason='';
  if(action==='pause' || action==='stop'){
    reason=window.prompt(
      action==='pause'?'Reason for pausing the research loop:':'Reason for stopping the research loop:',
      action==='pause'?'waiting for manual adjudication':'operator requested loop stop'
    );
    if(reason===null)return;
  }
  const res=await fetch('/api/research-loop-control',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      requested_action:action,
      control_reason:reason
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo actualizar el control del research loop.');
    return;
  }
  await refresh();
}

async function advanceResearchLoop(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/research-loop-advance',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.message||payload.error||'No se pudo avanzar el research loop.');
    return;
  }
  if(payload.execution_status && payload.execution_status!=='executed' && payload.execution_status!=='no_current_job'){
    window.alert(payload.message||payload.execution_status);
  }
  await refresh();
}

async function forceResearchLoopRerank(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/research-loop-force-rerank',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo forzar el rerank del research loop.');
    return;
  }
  await refresh();
}

async function markSourceFamilyExhausted(sourceFamily){
  if(!liveData?.run_id)return;
  const reason=window.prompt(
    `Reason for marking ${sourceFamily} as exhausted:`,
    'Relevant providers and obvious searches have been exhausted for this run.'
  );
  if(reason===null)return;
  const res=await fetch('/api/source-family-exhausted',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      source_family:sourceFamily,
      reason:reason
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo marcar la source family como exhausted.');
    return;
  }
  await refresh();
}

async function adjudicatePromotion(promotionId, promotionType, operatorDecision){
  if(!liveData?.run_id)return;
  const defaultReasons={
    accepted_for_registry_review:'Accepted for registry review from dashboard.',
    needs_review:'Flagged for deeper registry review from dashboard.',
    rejected_for_registry_review:'Rejected for registry review from dashboard.'
  };
  const res=await fetch('/api/promotion-decision',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      promotion_id:promotionId,
      promotion_type:promotionType,
      operator_decision:operatorDecision,
      decision_reason:defaultReasons[operatorDecision]||''
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo guardar la decisión de promotion.');
    return;
  }
  await refresh();
}

async function editPromotion(promotionId, promotionType){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const reviewRows=licensed.promotion_review_register||[];
  const patternRows=licensed.approved_pattern_promotion_register||[];
  const combinationRows=licensed.approved_combination_promotion_register||[];
  const reviewRow=reviewRows.find(item=>item.promotion_id===promotionId)||{};
  const sourceRow=(promotionType==='pattern'
    ? patternRows.find(item=>(item.promotion_id||`pattern::${item.pattern_id||''}`)===promotionId)
    : combinationRows.find(item=>(item.promotion_id||`combination::${item.combination_id||''}`)===promotionId)
  )||{};
  const spec=sourceRow.proposed_spec||{};
  let patch={};
  if(promotionType==='pattern'){
    const name=window.prompt('Pattern name:', spec.name||reviewRow.subject_name||'');
    if(name===null)return;
    const hypothesis=window.prompt('Hypothesis:', spec.hypothesis||'');
    if(hypothesis===null)return;
    const minimumActivate=window.prompt('Minimum evidence to activate, separada por |:', (spec.minimum_evidence_to_activate||[]).join(' | '));
    if(minimumActivate===null)return;
    const minimumConfirm=window.prompt('Minimum evidence to confirm, separada por |:', (spec.minimum_evidence_to_confirm||[]).join(' | '));
    if(minimumConfirm===null)return;
    const falsification=window.prompt('Falsification conditions, separadas por |:', (spec.falsification_conditions||[]).join(' | '));
    if(falsification===null)return;
    const allowedClaim=window.prompt('Allowed claim language:', spec.allowed_claim_language||'');
    if(allowedClaim===null)return;
    const prohibitedClaim=window.prompt('Prohibited claim language:', spec.prohibited_claim_language||'');
    if(prohibitedClaim===null)return;
    const exposureTrue=window.prompt('Financial exposure if true, separada por |:', (spec.financial_exposure_if_true||[]).join(' | '));
    if(exposureTrue===null)return;
    const exposureFalse=window.prompt('Financial exposure if false, separada por |:', (spec.financial_exposure_if_false||[]).join(' | '));
    if(exposureFalse===null)return;
    const tadActions=window.prompt('TAD actions, separadas por |:', (spec.tad_actions||[]).join(' | '));
    if(tadActions===null)return;
    patch={
      name:name,
      hypothesis:hypothesis,
      minimum_evidence_to_activate:minimumActivate.split('|').map(v=>v.trim()).filter(Boolean),
      minimum_evidence_to_confirm:minimumConfirm.split('|').map(v=>v.trim()).filter(Boolean),
      falsification_conditions:falsification.split('|').map(v=>v.trim()).filter(Boolean),
      allowed_claim_language:allowedClaim,
      prohibited_claim_language:prohibitedClaim,
      financial_exposure_if_true:exposureTrue.split('|').map(v=>v.trim()).filter(Boolean),
      financial_exposure_if_false:exposureFalse.split('|').map(v=>v.trim()).filter(Boolean),
      tad_actions:tadActions.split('|').map(v=>v.trim()).filter(Boolean)
    };
  }else{
    const name=window.prompt('Combination name:', spec.name||reviewRow.subject_name||'');
    if(name===null)return;
    const combinedHypothesis=window.prompt('Combined hypothesis:', spec.combined_hypothesis||'');
    if(combinedHypothesis===null)return;
    const minimumEvidence=window.prompt('Minimum evidence, separada por |:', (spec.minimum_evidence||[]).join(' | '));
    if(minimumEvidence===null)return;
    const financialExposure=window.prompt('Financial exposure, separada por |:', (spec.financial_exposure||[]).join(' | '));
    if(financialExposure===null)return;
    const tadAction=window.prompt('TAD action:', spec.tad_action||'');
    if(tadAction===null)return;
    const prohibitedClaims=window.prompt('Prohibited claims, separadas por |:', (spec.prohibited_claims||[]).join(' | '));
    if(prohibitedClaims===null)return;
    const allowedLanguage=window.prompt('Allowed language:', spec.allowed_language||'');
    if(allowedLanguage===null)return;
    patch={
      name:name,
      combined_hypothesis:combinedHypothesis,
      minimum_evidence:minimumEvidence.split('|').map(v=>v.trim()).filter(Boolean),
      financial_exposure:financialExposure.split('|').map(v=>v.trim()).filter(Boolean),
      tad_action:tadAction,
      prohibited_claims:prohibitedClaims.split('|').map(v=>v.trim()).filter(Boolean),
      allowed_language:allowedLanguage
    };
  }
  const res=await fetch('/api/promotion-edit',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      promotion_id:promotionId,
      promotion_type:promotionType,
      patch:patch
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo modificar la promotion.');
    return;
  }
  await refresh();
}

async function importLicensedDiscovery(){
  if(!liveData?.run_id)return;
  const exportPath=window.prompt('Ruta del export de discovery (.csv/.json):','');
  if(!exportPath)return;
  const providerKey=(window.prompt('Provider key (scopus|ieee|elsevier|springer):','scopus')||'scopus').trim().toLowerCase();
  const intakeDir=(window.prompt('Intake dir:','/Users/davidlagarejo/Desktop/ZLab_Licensed_Research_Intake')||'').trim();
  const topK=Number(window.prompt('Top K candidatos:','25')||'25');
  const res=await fetch('/api/discovery-queue-import',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      export_path:exportPath,
      provider_key:providerKey,
      intake_dir:intakeDir,
      top_k:Number.isFinite(topK)?topK:25
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo importar el export de discovery.');
    return;
  }
  await refresh();
}

async function seedCombinationResearchCandidates(combinationId){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/combination-follow-on-seed-candidates',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      combination_id:combinationId
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron sembrar research leads desde esta combinación.');
    return;
  }
  await refresh();
}

async function createManualDiscoveryCandidate(){
  if(!liveData?.run_id)return;
  const providerKey=(window.prompt('Provider key (scopus|ieee|elsevier|springer|manual):','manual')||'manual').trim().toLowerCase();
  const sourceFamily=window.prompt('Source family (optional: utility_tariff_billing_guidance|oem_handbook_technical_manuals|regulatory_code_compliance_guidance|specialist_web_case_signal):','');
  if(sourceFamily===null)return;
  const title=window.prompt('Title:','');
  if(title===null||!title.trim())return;
  const sourceUrl=window.prompt('Source URL:','');
  if(sourceUrl===null)return;
  const doi=window.prompt('DOI:','');
  if(doi===null)return;
  const journal=window.prompt('Journal:','');
  if(journal===null)return;
  const publishedYear=window.prompt('Published year:','');
  if(publishedYear===null)return;
  const keywordsRaw=window.prompt('Keywords separadas por |:','');
  if(keywordsRaw===null)return;
  const abstractText=window.prompt('Abstract / metadata summary:','');
  if(abstractText===null)return;
  const referenceExcerpt=window.prompt('Visible text / reference excerpt (optional):','');
  if(referenceExcerpt===null)return;
  const notes=window.prompt('Notes:','');
  if(notes===null)return;
  const autoAcceptRaw=window.prompt('Accept immediately for reference use? (y/n):','y');
  if(autoAcceptRaw===null)return;
  const autoAccept=(autoAcceptRaw||'y').trim().toLowerCase().startsWith('y');
  const res=await fetch('/api/discovery-candidate-create',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      provider_key:providerKey,
      source_family:(sourceFamily||'').trim(),
      title:title,
      source_url:sourceUrl,
      doi:doi,
      journal:journal,
      published_year:publishedYear,
      keywords:keywordsRaw.split('|').map(v=>v.trim()).filter(Boolean),
      abstract:abstractText,
      reference_excerpt:referenceExcerpt,
      notes:notes,
      operator_decision:autoAccept?'accepted_for_reference_use':'candidate'
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo crear el artículo manual.');
    return;
  }
  await refresh();
}

async function adjudicateDiscoveryCandidate(candidateId, operatorDecision){
  if(!liveData?.run_id)return;
  const defaultReasons={
    accepted_for_reference_use:'Accepted from dashboard for article/reference follow-up.',
    needs_review:'Flagged for deeper candidate review from dashboard.',
    rejected_for_reference_use:'Rejected from dashboard candidate review.'
  };
  const res=await fetch('/api/discovery-candidate-decision',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      operator_decision:operatorDecision,
      decision_reason:defaultReasons[operatorDecision]||''
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo guardar la decisión del candidato.');
    return;
  }
  await refresh();
}

async function editDiscoveryCandidate(candidateId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const rows=licensed.discovery_candidate_review_register||[];
  const refs=licensed.article_reference_register||[];
  const row=rows.find(item=>item.candidate_id===candidateId)||{};
  const ref=refs.find(item=>item.candidate_id===candidateId)||{};
  const title=window.prompt('Title:', row.title||ref.title||'');
  if(title===null)return;
  const abstractText=window.prompt('Abstract / excerpt:', ref.reference_excerpt||'');
  if(abstractText===null)return;
  const sourceUrl=window.prompt('Source URL:', row.source_url||ref.source_url||'');
  if(sourceUrl===null)return;
  const keywordsRaw=window.prompt('Keywords separadas por |:', ((ref.keywords||[]).join(' | '))||'');
  if(keywordsRaw===null)return;
  const notes=window.prompt('Notes:', '');
  if(notes===null)return;
  const expectedPdfName=window.prompt('Expected PDF name:', row.expected_pdf_name||'');
  if(expectedPdfName===null)return;
  const res=await fetch('/api/discovery-candidate-edit',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      patch:{
        title:title,
        abstract:abstractText,
        source_url:sourceUrl,
        keywords:keywordsRaw.split('|').map(v=>v.trim()).filter(Boolean),
        notes:notes,
        expected_pdf_name:expectedPdfName
      }
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo modificar el candidato.');
    return;
  }
  await refresh();
}

async function readArticleReference(candidateId){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/article-reference-read',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo leer la referencia del artículo.');
    return;
  }
  await refresh();
}

async function editArticleReference(candidateId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const refs=licensed.article_reference_register||[];
  const ref=refs.find(item=>item.candidate_id===candidateId)||{};
  const sourceUrl=window.prompt('Resolved article URL (optional):', ref.source_url||'');
  if(sourceUrl===null)return;
  const excerpt=window.prompt('Reference excerpt / visible text:', ref.reference_excerpt||'');
  if(excerpt===null)return;
  const notes=window.prompt('Reference notes:', ref.notes||'');
  if(notes===null)return;
  const res=await fetch('/api/article-reference-edit',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      patch:{
        source_url:sourceUrl,
        reference_excerpt:excerpt,
        notes:notes
      }
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo modificar la referencia.');
    return;
  }
  await refresh();
}

async function resolveQuerySeedDraft(candidateId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const refs=licensed.article_reference_register||[];
  const ref=refs.find(item=>item.candidate_id===candidateId)||{};
  const prefill=ref.draft_resolution_prefill||{};
  const fallbackUrl=(ref.source_url&&ref.source_url!==prefill.launch_url)?ref.source_url:(prefill.source_url||'');
  const urlInstructions=[
    `Resolve excerpt for ${prefill.provider_key||'provider'}${prefill.query_family?` · ${prefill.query_family}`:''}.`,
    prefill.launch_url?`Launch/search URL: ${prefill.launch_url}`:'',
    prefill.primary_query?`Primary query: ${prefill.primary_query}`:'',
    prefill.pivot_query?`Pivot query: ${prefill.pivot_query}`:'',
    (prefill.evidence_targets||[]).length?`Evidence targets: ${(prefill.evidence_targets||[]).join(', ')}`:'',
    '',
    fallbackUrl?'Leave the URL unchanged to reuse the captured article URL.':'Paste the real article URL, not the provider search page.',
  ].filter(Boolean).join('\n');
  const sourceUrlInput=window.prompt(urlInstructions, fallbackUrl);
  if(sourceUrlInput===null)return;
  const sourceUrl=(sourceUrlInput||'').trim()||fallbackUrl;
  if(!sourceUrl){
    window.alert('Se requiere una URL real del artículo o una URL ya capturada.');
    return;
  }
  const excerptPrompt=[
    `Paste the visible excerpt for ${prefill.provider_display_name||prefill.provider_key||'provider'}.`,
    prefill.search_surface?`Search surface: ${prefill.search_surface}`:'',
    prefill.execution_hint?`Execution hint: ${prefill.execution_hint}`:'',
    prefill.captured_result_title?`Captured result title: ${prefill.captured_result_title}`:'',
    prefill.captured_result_snippet?`Captured result snippet: ${prefill.captured_result_snippet}`:'',
  ].filter(Boolean).join('\n');
  const excerpt=window.prompt(excerptPrompt, '');
  if(excerpt===null||!excerpt.trim())return;
  const notes=window.prompt('Reference notes:', ref.notes||prefill.suggested_notes||'Resolved from query-seed draft.');
  if(notes===null)return;
  const res=await fetch('/api/article-reference-quick-resolve',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      auto_accept_discovery_candidate:true,
      source_url:sourceUrl,
      reference_excerpt:excerpt,
      notes:notes
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el draft de referencia.');
    return;
  }
  await refresh();
}

async function captureQuerySeedSearchResult(candidateId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const refs=licensed.article_reference_register||[];
  const ref=refs.find(item=>item.candidate_id===candidateId)||{};
  const prefill=ref.draft_resolution_prefill||{};
  const sourceUrl=window.prompt(
    [
      `Capture search result for ${prefill.provider_key||'provider'}${prefill.query_family?` · ${prefill.query_family}`:''}.`,
      prefill.launch_url?`Launch/search URL: ${prefill.launch_url}`:'',
      prefill.primary_query?`Primary query: ${prefill.primary_query}`:'',
      'Paste the real article URL you found from the search result.',
    ].filter(Boolean).join('\n'),
    (ref.source_url&&ref.source_url!==prefill.launch_url?ref.source_url:'')
  );
  if(sourceUrl===null||!sourceUrl.trim())return;
  const searchResultTitle=window.prompt('Search result title / article title (optional):', prefill.captured_result_title||prefill.title||'');
  if(searchResultTitle===null)return;
  const searchResultSnippet=window.prompt(
    [
      `Paste the visible search-result snippet for ${prefill.provider_display_name||prefill.provider_key||'provider'}.`,
      prefill.execution_hint?`Execution hint: ${prefill.execution_hint}`:'',
    ].filter(Boolean).join('\n'),
    prefill.captured_result_snippet||''
  );
  if(searchResultSnippet===null)return;
  const notes=window.prompt('Search-result notes:', ref.notes||prefill.suggested_notes||'Captured from provider search result.');
  if(notes===null)return;
  const res=await fetch('/api/article-reference-capture-search-result',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      source_url:sourceUrl,
      search_result_title:searchResultTitle,
      search_result_snippet:searchResultSnippet,
      notes:notes
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo capturar el search result.');
    return;
  }
  await refresh();
}

function showSearchQueryExecutionPacket(candidateId){
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const rows=brain.search_query_execution_register||licensed.search_query_execution_register||[];
  const row=rows.find(item=>item.candidate_id===candidateId)||{};
  if(!row.candidate_id){
    window.alert('No search execution packet is available for this candidate.');
    return;
  }
  const instructions=[
    `Search execution packet for ${row.provider_key||'provider'}${row.query_family?` · ${row.query_family}`:''}.`,
    row.execution_status?`Execution status: ${row.execution_status}`:'',
    row.launch_url?`Launch URL: ${row.launch_url}`:'',
    '',
    'Copy this packet to guide the provider search. It does not create evidence by itself.',
  ].filter(Boolean).join('\n');
  window.prompt(instructions, row.search_packet_template||'');
}

async function materializeSearchQueryExecutionPlan(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/search-query-execution-materialize',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo materializar el search query execution plan.');
    return;
  }
  await refresh();
}

async function importSearchQueryResults(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  if(!batchPlan.available)return;
  const instructions=[
    `Import visible search results for up to ${Number(batchPlan.candidate_count||0)} pending query seed(s).`,
    `Provider: ${batchPlan.provider_key||'unknown'} · Source family: ${batchPlan.source_family||'unknown'} · Query family: ${batchPlan.query_family||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Each block must include Candidate ID, URL, and either Title or Snippet.',
    'Optional Selected: yes or "selected": true marks the correct visible result for that candidate and can skip imported-result review.',
    'Optional Excerpt/reference_excerpt is allowed; singleton imports with excerpt can resolve faster downstream.',
    'You can also paste a JSON array of records with candidate_id, source_url/url, title/search_result_title, snippet/search_result_snippet, optional reference_excerpt/excerpt, and notes.',
    'Duplicate Candidate ID blocks are allowed to import multiple result options for one query seed.',
    'Separate blocks with a line containing only ---',
  ].filter(Boolean).join('\n');
  const importPacket=window.prompt(instructions, batchPlan.result_import_packet_template||batchPlan.packet_template||'');
  if(importPacket===null||!importPacket.trim())return;
  const res=await fetch('/api/search-query-execution-import-results',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      search_result_import_packet:importPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron importar los search results.');
    return;
  }
  await refresh();
}

async function importSearchQueryResultsAndCaptureSingletons(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  if(!batchPlan.available)return;
  const instructions=[
    `Import visible search results and auto-capture singleton candidates for up to ${Number(batchPlan.candidate_count||0)} pending query seed(s).`,
    `Provider: ${batchPlan.provider_key||'unknown'} · Source family: ${batchPlan.source_family||'unknown'} · Query family: ${batchPlan.query_family||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Candidates with exactly one imported result will be auto-captured as source hits.',
    'For multi-option candidates, Selected: yes or "selected": true can promote the chosen result immediately.',
    'If a singleton record also includes a real Excerpt/reference_excerpt, it will resolve directly to an excerpt-backed reference.',
    'If a selected multi-option record also includes a real Excerpt/reference_excerpt, it will resolve directly too.',
    'Candidates with multiple imported options will stay in imported-result review.',
    'You can paste packet blocks or a JSON array of records.',
  ].filter(Boolean).join('\n');
  const importPacket=window.prompt(instructions, batchPlan.result_import_packet_template||batchPlan.packet_template||'');
  if(importPacket===null||!importPacket.trim())return;
  const res=await fetch('/api/search-query-execution-import-results',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      search_result_import_packet:importPacket,
      auto_capture_singleton_candidates:true
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron importar/capturar los search results.');
    return;
  }
  await refresh();
}

async function importSearchQueryResultsOrdered(autoCaptureSingletons=false){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  const providerGuide=batchPlan.ordered_result_import_provider_capture_guide||{};
  if(!batchPlan.available)return;
  const instructions=[
    `Import ordered visible results for ${Number(batchPlan.candidate_count||0)} pending query seed(s).`,
    `Provider: ${batchPlan.provider_key||'unknown'} · Source family: ${batchPlan.source_family||'unknown'} · Query family: ${batchPlan.query_family||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    providerGuide.summary?`Provider capture guide: ${providerGuide.summary}`:'',
    (providerGuide.preferred_headers||[]).length?`Preferred headers: ${(providerGuide.preferred_headers||[]).join(' | ')}`:'',
    (providerGuide.snippet_header_fallbacks||[]).length?`Visible-text fallback headers: ${(providerGuide.snippet_header_fallbacks||[]).join(', ')}`:'',
    (providerGuide.carried_note_headers||[]).length?`Extra headers preserved in notes: ${(providerGuide.carried_note_headers||[]).join(', ')}`:'',
    providerGuide.selection_hint?`Selection hint: ${providerGuide.selection_hint}`:'',
    (providerGuide.positional_layouts||[]).length?'Provider-native TSV rows without a header are also accepted when they match one of the provider layouts.':'',
    'Use the same order as the current batch plan. candidate_id is not required.',
    'Optional Selected: yes or "selected": true marks the correct visible result for that ordered row.',
    'Optional reference_excerpt/excerpt is allowed per row.',
    'You can paste ordered packet blocks, a JSON array, compact ordered lines, or tab-separated clipboard rows.',
    'Compact line format: URL | Title | Snippet | Excerpt | Selected | Notes',
    'Clipboard/TSV format: URL<TAB>Title<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes',
    'Also accepts Title<TAB>URL<TAB>Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes when the clipboard puts title first.',
    'Also accepts a first-column link shortcut like [Title](URL) or Title (URL), followed by Snippet<TAB>Excerpt<TAB>Selected<TAB>Notes.',
    'TSV rows may also include extra leading/intermediate columns; if a URL appears anywhere in the row, the runtime will infer title/url/snippet and fold the rest into notes.',
    'Header rows are also accepted, including commented headers like # Title<TAB>URL<TAB>Abstract<TAB>Year<TAB>Source<TAB>Selected<TAB>Notes in any reasonable column order.',
    'When available, the default template is provider-aware so you can paste closer to the provider table as-is.',
    autoCaptureSingletons?'Singleton results will be auto-captured as source hits.':'Imported results will stay in review unless you capture/promote them later.',
  ].filter(Boolean).join('\n');
  const importPacket=window.prompt(instructions, batchPlan.search_execution_capture_workbook_template||batchPlan.ordered_result_import_provider_capture_sheet_template||batchPlan.ordered_result_import_provider_tsv_template||batchPlan.ordered_result_import_tsv_template||batchPlan.ordered_result_import_compact_template||batchPlan.ordered_result_import_packet_template||batchPlan.ordered_result_import_json_template||'[]');
  if(importPacket===null||!importPacket.trim())return;
  const res=await fetch('/api/search-query-execution-import-results',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      search_result_import_packet:importPacket,
      auto_capture_singleton_candidates:!!autoCaptureSingletons
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron importar los search results ordered.');
    return;
  }
  await refresh();
}

function showProviderCaptureSheet(){
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  if(!batchPlan.available)return;
  const providerGuide=batchPlan.ordered_result_import_provider_capture_guide||{};
  const instructions=[
    `Provider-native capture sheet for ${batchPlan.provider_key||'provider'}${batchPlan.query_family?` · ${batchPlan.query_family}`:''}.`,
    providerGuide.summary?`Guide: ${providerGuide.summary}`:'',
    (providerGuide.preferred_headers||[]).length?`Preferred headers: ${(providerGuide.preferred_headers||[]).join(' | ')}`:'',
    (providerGuide.snippet_header_fallbacks||[]).length?`Visible-text fallbacks: ${(providerGuide.snippet_header_fallbacks||[]).join(', ')}`:'',
    (providerGuide.carried_note_headers||[]).length?`Preserved in notes: ${(providerGuide.carried_note_headers||[]).join(', ')}`:'',
    providerGuide.selection_hint?`Selection hint: ${providerGuide.selection_hint}`:'',
    '',
    'This sheet is safe to copy, fill, and paste back into Import ordered.',
  ].filter(Boolean).join('\n');
  window.prompt(instructions, batchPlan.ordered_result_import_provider_capture_sheet_template||batchPlan.ordered_result_import_provider_tsv_template||'');
}

function showProviderSearchSheet(){
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  if(!batchPlan.available)return;
  const guide=batchPlan.search_execution_provider_guide||{};
  const instructions=[
    `Provider search sheet for ${batchPlan.provider_key||'provider'}${batchPlan.query_family?` · ${batchPlan.query_family}`:''}.`,
    guide.preferred_surface?`Preferred surface: ${guide.preferred_surface}`:'',
    (guide.preferred_fields||[]).length?`Preferred fields: ${(guide.preferred_fields||[]).join(' | ')}`:'',
    (guide.search_tips||[]).length?`Search tips: ${(guide.search_tips||[]).join(' | ')}`:'',
    guide.result_capture_goal?`Result capture goal: ${guide.result_capture_goal}`:'',
    '',
    'This sheet is safe to copy and use while searching. It does not create evidence by itself.',
  ].filter(Boolean).join('\n');
  window.prompt(instructions, batchPlan.search_execution_provider_sheet_template||batchPlan.packet_template||'');
}

function showProviderSearchWorkbook(){
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  if(!batchPlan.available)return;
  const guide=batchPlan.search_execution_provider_guide||{};
  const instructions=[
    `Provider search workbook for ${batchPlan.provider_key||'provider'}${batchPlan.query_family?` · ${batchPlan.query_family}`:''}.`,
    guide.preferred_surface?`Preferred surface: ${guide.preferred_surface}`:'',
    guide.result_capture_goal?`Result capture goal: ${guide.result_capture_goal}`:'',
    '',
    'This workbook combines search guidance and import-ready result fields in one artifact.',
    'You can fill URL / Title / Snippet / Selected / Excerpt / Notes and paste it back into Import ordered.',
  ].filter(Boolean).join('\n');
  window.prompt(instructions, batchPlan.search_execution_capture_workbook_template||batchPlan.search_execution_provider_sheet_template||batchPlan.packet_template||'');
}

function getSearchQueryExecutionSessionBundle(){
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const manifest=brain.search_query_execution_manifest||licensed.search_query_execution_manifest||{};
  return brain.search_query_execution_session_bundle||licensed.search_query_execution_session_bundle||manifest.session_bundle||{};
}

function buildEffectiveSearchSessionRows(bundle){
  const rows=Array.isArray(bundle?.rows)?bundle.rows:[];
  const drafts=window._searchSessionRowDrafts||{};
  return rows.map(row=>{
    const candidateId=String(row?.candidate_id||'').trim();
    const draft=drafts[candidateId]||{};
    return {
      ...row,
      source_url:draft.source_url!==undefined?draft.source_url:(row?.source_url||''),
      search_result_title:draft.search_result_title!==undefined?draft.search_result_title:(row?.search_result_title||''),
      search_result_snippet:draft.search_result_snippet!==undefined?draft.search_result_snippet:(row?.search_result_snippet||''),
      reference_excerpt:draft.reference_excerpt!==undefined?draft.reference_excerpt:(row?.reference_excerpt||''),
      notes:draft.notes!==undefined?draft.notes:(row?.notes||''),
      selected:draft.selected!==undefined?!!draft.selected:!!row?.selected,
    };
  });
}

function updateSearchSessionEditorDraft(el){
  window._searchSessionEditorDraft=el?.value||'';
}

function syncSearchSessionEditorOpen(el){
  window._searchSessionEditorOpen=!!el?.open;
}

function syncSearchSessionFormOpen(el){
  window._searchSessionFormOpen=!!el?.open;
}

function updateSearchSessionRowFieldFromElement(el){
  const candidateId=String(el?.dataset?.candidateId||'').trim();
  const field=String(el?.dataset?.field||'').trim();
  if(!candidateId||!field)return;
  const drafts={...(window._searchSessionRowDrafts||{})};
  const next={...(drafts[candidateId]||{})};
  next[field]=el?.type==='checkbox'?!!el.checked:(el?.value||'');
  drafts[candidateId]=next;
  window._searchSessionRowDrafts=drafts;
}

function setSearchSessionEditorText(text){
  const normalized=String(text||'');
  window._searchSessionEditorDraft=normalized;
  const el=document.getElementById('search-session-editor');
  if(el)el.value=normalized;
}

function currentSearchSessionEditorText(){
  const el=document.getElementById('search-session-editor');
  if(el)return el.value||'';
  return window._searchSessionEditorDraft||'';
}

function collectVisibleSearchSessionRows(){
  const bundle=getSearchQueryExecutionSessionBundle();
  return buildEffectiveSearchSessionRows(bundle).map(row=>{
    const candidateId=String(row?.candidate_id||'').trim();
    const query=(field)=>{
      const selector=`[data-candidate-id="${CSS.escape(candidateId)}"][data-field="${field}"]`;
      return document.querySelector(selector);
    };
    const sourceUrl=query('source_url');
    const title=query('search_result_title');
    const snippet=query('search_result_snippet');
    const excerpt=query('reference_excerpt');
    const notes=query('notes');
    const selected=query('selected');
    return {
      ...row,
      source_url:sourceUrl?sourceUrl.value:(row.source_url||''),
      search_result_title:title?title.value:(row.search_result_title||''),
      search_result_snippet:snippet?snippet.value:(row.search_result_snippet||''),
      reference_excerpt:excerpt?excerpt.value:(row.reference_excerpt||''),
      notes:notes?notes.value:(row.notes||''),
      selected:selected?!!selected.checked:!!row.selected,
    };
  });
}

function applySearchSessionRowToDraft(candidateId, patch){
  const drafts={...(window._searchSessionRowDrafts||{})};
  drafts[candidateId]={...(drafts[candidateId]||{}), ...patch};
  window._searchSessionRowDrafts=drafts;
}

async function ensureSearchQueryExecutionSessionBundle(){
  let bundle=getSearchQueryExecutionSessionBundle();
  if(bundle?.available)return bundle;
  if(!liveData?.run_id)return {};
  const res=await fetch('/api/search-query-execution-materialize',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo materializar el search session bundle.');
    return {};
  }
  await refresh();
  bundle=getSearchQueryExecutionSessionBundle();
  return bundle?.available ? bundle : {};
}

async function showSearchSessionBundle(){
  const bundle=await ensureSearchQueryExecutionSessionBundle();
  if(!bundle.available)return;
  const instructions=[
    `Search session bundle for ${bundle.provider_key||'provider'}${bundle.query_family?` · ${bundle.query_family}`:''}.`,
    `Rows: ${Number(bundle.candidate_count||0)} · Pending: ${Number((bundle.summary||{}).pending_rows||0)}.`,
    bundle.manifest_path?`Manifest path: ${bundle.manifest_path}`:'',
    'This bundle is safe to copy, fill, and paste back into Import session rows.',
    'Fill source_url, search_result_title, search_result_snippet, optional reference_excerpt, selected, and notes per row.',
  ].filter(Boolean).join('\n');
  window.prompt(instructions, JSON.stringify(bundle, null, 2));
}

async function loadSearchSessionEditorFromBundle(){
  const bundle=await ensureSearchQueryExecutionSessionBundle();
  if(!bundle.available)return;
  setSearchSessionEditorText(JSON.stringify(bundle, null, 2));
  window._searchSessionEditorOpen=true;
  await refresh();
}

async function loadSearchSessionFormFromBundle(){
  const bundle=await ensureSearchQueryExecutionSessionBundle();
  if(!bundle.available)return;
  window._searchSessionRowDrafts={};
  window._searchSessionFormOpen=true;
  await refresh();
}

async function parseVisibleSearchSessionRow(candidateId){
  if(!liveData?.run_id)return;
  const parseField=document.getElementById(`search-session-parse-${candidateId}`);
  const rowText=parseField?.value||'';
  if(!rowText.trim()){
    window.alert('Paste a provider row before parsing.');
    return;
  }
  const res=await fetch('/api/search-query-execution-session-parse-row',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      row_text:rowText
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo parsear la fila del provider.');
    return;
  }
  const merged=payload.merged_row||{};
  applySearchSessionRowToDraft(candidateId,{
    source_url:merged.source_url||'',
    search_result_title:merged.search_result_title||'',
    search_result_snippet:merged.search_result_snippet||'',
    reference_excerpt:merged.reference_excerpt||'',
    notes:merged.notes||'',
    selected:!!merged.selected,
    parse_input:rowText
  });
  window._searchSessionFormOpen=true;
  await refresh();
}

function parseSearchSessionEditorPayload(){
  const raw=currentSearchSessionEditorText();
  if(!raw.trim())throw new Error('Search session editor is empty.');
  let decoded;
  try{
    decoded=JSON.parse(raw);
  }catch(_err){
    throw new Error('Search session editor must contain valid JSON.');
  }
  if(Array.isArray(decoded)){
    return {search_query_execution_session_rows:decoded};
  }
  if(Array.isArray(decoded?.rows)){
    return {search_query_execution_session_bundle:decoded};
  }
  throw new Error('Search session editor JSON must be an array of rows or an object with rows.');
}

async function saveSearchSessionEditorFromInline(){
  if(!liveData?.run_id)return;
  let payloadBody;
  try{
    payloadBody=parseSearchSessionEditorPayload();
  }catch(err){
    window.alert(err.message||'No se pudo parsear el editor inline.');
    return;
  }
  const res=await fetch('/api/search-query-execution-session-save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id, ...payloadBody})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo guardar el search session editor.');
    return;
  }
  setSearchSessionEditorText(JSON.stringify(payload.session_bundle||payloadBody.search_query_execution_session_bundle||payloadBody.search_query_execution_session_rows||[], null, 2));
  await refresh();
}

async function importSearchSessionEditorFromInline(autoCaptureSingletons=false){
  if(!liveData?.run_id)return;
  let payloadBody;
  try{
    payloadBody=parseSearchSessionEditorPayload();
  }catch(err){
    window.alert(err.message||'No se pudo parsear el editor inline.');
    return;
  }
  const saveRes=await fetch('/api/search-query-execution-session-save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id, ...payloadBody})
  });
  const savePayload=await saveRes.json();
  if(!savePayload.ok){
    window.alert(savePayload.error||'No se pudo guardar el search session editor antes del import.');
    return;
  }
  const importRes=await fetch('/api/search-query-execution-session-import',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      auto_capture_singleton_candidates:!!autoCaptureSingletons
    })
  });
  const importPayload=await importRes.json();
  if(!importPayload.ok){
    window.alert(importPayload.error||'No se pudieron importar los ready rows desde el editor inline.');
    return;
  }
  await refresh();
}

async function saveVisibleSearchSessionRows(){
  if(!liveData?.run_id)return false;
  const sessionRows=collectVisibleSearchSessionRows();
  const res=await fetch('/api/search-query-execution-session-save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      search_query_execution_session_rows:sessionRows
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron guardar las visible search session rows.');
    return false;
  }
  window._searchSessionRowDrafts={};
  window._searchSessionFormOpen=true;
  await refresh();
  return true;
}

async function importVisibleSearchSessionRows(autoCaptureSingletons=false){
  if(!liveData?.run_id)return;
  const saved=await saveVisibleSearchSessionRows();
  if(!saved)return;
  await importSavedSearchQueryExecutionSessionRows(autoCaptureSingletons);
}

async function saveSearchSessionBundle(){
  if(!liveData?.run_id)return;
  const bundle=await ensureSearchQueryExecutionSessionBundle();
  if(!bundle.available)return;
  const instructions=[
    `Save structured search session rows for ${Number(bundle.candidate_count||0)} pending query seed(s).`,
    `Provider: ${bundle.provider_key||'unknown'} · Source family: ${bundle.source_family||'unknown'} · Query family: ${bundle.query_family||'unknown'}.`,
    'Paste a JSON array of session rows, or the full session bundle object with a rows array.',
    'This store is run-scoped and survives refresh so you do not have to rebuild the workbook every time.',
  ].filter(Boolean).join('\n');
  const sessionText=window.prompt(instructions, JSON.stringify(bundle, null, 2));
  if(sessionText===null||!sessionText.trim())return;
  let decoded;
  try{
    decoded=JSON.parse(sessionText);
  }catch(_err){
    window.alert('Search session bundle must be valid JSON.');
    return;
  }
  const body=Array.isArray(decoded)
    ? {run_id:liveData.run_id, search_query_execution_session_rows:decoded}
    : {run_id:liveData.run_id, search_query_execution_session_bundle:decoded};
  const res=await fetch('/api/search-query-execution-session-save',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify(body)
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo guardar el search session bundle.');
    return;
  }
  await refresh();
}

async function importSearchQueryExecutionSessionRows(autoCaptureSingletons=false){
  if(!liveData?.run_id)return;
  const bundle=await ensureSearchQueryExecutionSessionBundle();
  if(!bundle.available)return;
  const instructions=[
    `Import structured search session rows for ${Number(bundle.candidate_count||0)} pending query seed(s).`,
    `Provider: ${bundle.provider_key||'unknown'} · Source family: ${bundle.source_family||'unknown'} · Query family: ${bundle.query_family||'unknown'}.`,
    (bundle.candidate_ids||[]).length?`Candidate IDs: ${(bundle.candidate_ids||[]).join(' | ')}`:'',
    'Paste a JSON array of session rows, or the full session bundle object with a rows array.',
    'Per row you can fill source_url, search_result_title, search_result_snippet, optional reference_excerpt, selected, and notes.',
    autoCaptureSingletons?'Singleton rows can auto-capture to source-hit state when applicable.':'Rows will be imported without forced singleton auto-capture unless selected/excerpt rules apply.',
  ].filter(Boolean).join('\n');
  const sessionText=window.prompt(instructions, JSON.stringify(bundle.rows||[], null, 2));
  if(sessionText===null||!sessionText.trim())return;
  let decoded;
  try{
    decoded=JSON.parse(sessionText);
  }catch(_err){
    window.alert('Session rows must be valid JSON.');
    return;
  }
  const sessionRows=Array.isArray(decoded) ? decoded : (Array.isArray(decoded?.rows) ? decoded.rows : []);
  if(!sessionRows.length){
    window.alert('No session rows were found in the JSON payload.');
    return;
  }
  const res=await fetch('/api/search-query-execution-import-results',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      search_query_execution_session_rows:sessionRows,
      auto_capture_singleton_candidates:!!autoCaptureSingletons
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron importar los search session rows.');
    return;
  }
  await refresh();
}

async function importSavedSearchQueryExecutionSessionRows(autoCaptureSingletons=false){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/search-query-execution-session-import',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      auto_capture_singleton_candidates:!!autoCaptureSingletons
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron importar los ready session rows guardados.');
    return;
  }
  await refresh();
}

async function captureSearchResultBatch(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_execution_batch_plan||licensed.search_query_execution_batch_plan||{};
  if(!batchPlan.available)return;
  const instructions=[
    `Capture up to ${Number(batchPlan.candidate_count||0)} source hit(s) from the current search batch.`,
    `Provider: ${batchPlan.provider_key||'unknown'} · Source family: ${batchPlan.source_family||'unknown'} · Query family: ${batchPlan.query_family||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Each block must include Candidate ID, URL, and either Title or Snippet.',
    'You can also paste a JSON array of records with candidate_id, source_url/url, title/search_result_title, snippet/search_result_snippet, and notes.',
    'Separate blocks with a line containing only ---',
  ].filter(Boolean).join('\n');
  const batchPacket=window.prompt(instructions, batchPlan.capture_result_json_template||batchPlan.packet_template||'');
  if(batchPacket===null||!batchPacket.trim())return;
  const res=await fetch('/api/article-reference-capture-search-result-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      search_result_batch_packet:batchPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo capturar el batch de search results.');
    return;
  }
  await refresh();
}

async function promoteImportedSearchResult(candidateId, optionIndex=null){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const rows=brain.search_query_execution_register||licensed.search_query_execution_register||[];
  const row=rows.find(item=>item.candidate_id===candidateId)||{};
  const options=row.imported_result_options||[];
  if(!options.length){
    window.alert('No imported search results are available for this candidate.');
    return;
  }
  let resolvedOptionIndex=Number(optionIndex)||0;
  if(resolvedOptionIndex<1){
    const optionLines=options.slice(0,9).map((option, index)=>`${index+1}. ${(option.search_result_title||option.source_url||'Option').slice(0,140)}`);
    const optionInput=window.prompt(
      [
        `Select imported result to promote for ${row.provider_key||'provider'}${row.query_family?` · ${row.query_family}`:''}.`,
        ...optionLines,
        '',
        'Enter option number:',
      ].join('\n'),
      '1'
    );
    if(optionInput===null)return;
    resolvedOptionIndex=Math.max(1, Math.min(options.length, Number(optionInput)||1));
  }
  const res=await fetch('/api/search-query-result-promote',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      option_index:resolvedOptionIndex
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo promover el imported search result.');
    return;
  }
  await refresh();
}

async function resolveImportedSearchResult(candidateId, optionIndex=null){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const rows=brain.search_query_execution_register||licensed.search_query_execution_register||[];
  const currentOptionRow=brain.current_search_query_result_option_row||{};
  const row=rows.find(item=>item.candidate_id===candidateId)||{};
  const options=row.imported_result_options||[];
  if(!options.length){
    window.alert('No imported search results are available for this candidate.');
    return;
  }
  let resolvedOptionIndex=Number(optionIndex)||0;
  if(resolvedOptionIndex<1){
    if(currentOptionRow.candidate_id===candidateId && Number(currentOptionRow.current_option_index||0)>0){
      resolvedOptionIndex=Number(currentOptionRow.current_option_index||0);
    }else{
      const optionLines=options.slice(0,9).map((option, index)=>`${index+1}. ${(option.search_result_title||option.source_url||'Option').slice(0,140)}`);
      const optionInput=window.prompt(
        [
          `Select imported result to resolve for ${row.provider_key||'provider'}${row.query_family?` · ${row.query_family}`:''}.`,
          ...optionLines,
          '',
          'Enter option number:',
        ].join('\n'),
        '1'
      );
      if(optionInput===null)return;
      resolvedOptionIndex=Math.max(1, Math.min(options.length, Number(optionInput)||1));
    }
  }
  const selectedOption=options[Math.max(0, resolvedOptionIndex-1)]||{};
  const excerptPrompt=[
    `Resolve imported result ${resolvedOptionIndex}/${options.length} for ${row.provider_key||'provider'}${row.query_family?` · ${row.query_family}`:''}.`,
    selectedOption.search_result_title?`Imported title: ${selectedOption.search_result_title}`:'',
    selectedOption.search_result_snippet?`Imported snippet: ${selectedOption.search_result_snippet}`:'',
    selectedOption.source_url?`Captured URL: ${selectedOption.source_url}`:'',
    '',
    'Paste the real visible excerpt. The imported snippet is not evidence.',
  ].filter(Boolean).join('\n');
  const excerpt=window.prompt(excerptPrompt, '');
  if(excerpt===null||!excerpt.trim())return;
  const notes=window.prompt('Reference notes:', selectedOption.notes||'Resolved from imported search result option.');
  if(notes===null)return;
  const res=await fetch('/api/search-query-result-promote-and-resolve',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      option_index:resolvedOptionIndex,
      reference_excerpt:excerpt,
      notes:notes,
      auto_accept_discovery_candidate:true
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el imported search result.');
    return;
  }
  await refresh();
}

async function promoteImportedSearchResultBatch(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/search-query-result-promote-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo promover el batch de resultados importados.');
    return;
  }
  await refresh();
}

async function resolveImportedSearchResultBatch(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const batchPlan=brain.search_query_result_option_batch_plan||licensed.search_query_result_option_batch_plan||{};
  if(!batchPlan.available||!batchPlan.resolve_available)return;
  const instructions=[
    `Resolve visible imported-result batch for up to ${Number(batchPlan.resolve_candidate_count||0)} candidate(s).`,
    `Provider: ${batchPlan.provider_key||'unknown'} · Source family: ${batchPlan.source_family||'unknown'} · Query family: ${batchPlan.query_family||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Each block must include Candidate ID, Option Index and Excerpt.',
    'You can also paste a JSON array of records with candidate_id, option_index, reference_excerpt/excerpt and notes.',
    'Imported titles/snippets are context only; the excerpt must be real visible text.',
    'Separate blocks with a line containing only ---',
  ].filter(Boolean).join('\n');
  const resolutionPacket=window.prompt(instructions, batchPlan.resolve_records_json_template||'[]');
  if(resolutionPacket===null||!resolutionPacket.trim())return;
  const res=await fetch('/api/search-query-result-promote-and-resolve-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      auto_accept_discovery_candidate:true,
      resolution_batch_packet:resolutionPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el batch de imported search results.');
    return;
  }
  await refresh();
}

async function resolveQuerySeedDraftFull(candidateId){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const licensed=brain.licensed_research||{};
  const refs=licensed.article_reference_register||[];
  const ref=refs.find(item=>item.candidate_id===candidateId)||{};
  const prefill=ref.draft_resolution_prefill||{};
  const hintLines=[
    prefill.provider_display_name||prefill.provider_key?`# Provider: ${prefill.provider_display_name||prefill.provider_key}`:'',
    prefill.launch_url?`# Launch URL: ${prefill.launch_url}`:'',
    prefill.search_surface?`# Search surface: ${prefill.search_surface}`:'',
    prefill.query_family?`# Query family: ${prefill.query_family}`:'',
    prefill.primary_query?`# Primary query: ${prefill.primary_query}`:'',
    prefill.pivot_query?`# Pivot query: ${prefill.pivot_query}`:'',
    (prefill.evidence_targets||[]).length?`# Evidence targets: ${(prefill.evidence_targets||[]).join(', ')}`:'',
    prefill.execution_hint?`# Execution hint: ${prefill.execution_hint}`:'',
    prefill.search_brief?`# Search brief: ${prefill.search_brief}`:'',
  ].filter(Boolean);
  const packetTemplate=[
    ...hintLines,
    `URL: ${ref.source_url||prefill.source_url||''}`,
    `Title: ${prefill.title||ref.title||''}`,
    `DOI: ${prefill.doi||ref.doi||''}`,
    `Journal: ${prefill.journal||ref.journal||''}`,
    `Year: ${prefill.published_year||ref.published_year||''}`,
    `Notes: ${ref.notes||prefill.suggested_notes||'Resolved from query-seed draft.'}`,
    'Excerpt:',
    '',
  ].join('\n');
  const instructions=[
    `Resolve draft for ${prefill.provider_key||'provider'}${prefill.query_family?` · ${prefill.query_family}`:''}.`,
    prefill.primary_query?`Primary query: ${prefill.primary_query}`:'',
    prefill.pivot_query?`Pivot query: ${prefill.pivot_query}`:'',
    (prefill.evidence_targets||[]).length?`Evidence targets: ${(prefill.evidence_targets||[]).join(', ')}`:'',
    '',
    'Paste or edit this packet. URL and Excerpt are required.',
  ].filter(Boolean).join('\n');
  const resolutionPacket=window.prompt(instructions, packetTemplate);
  if(resolutionPacket===null||!resolutionPacket.trim())return;
  const res=await fetch('/api/article-reference-resolve-packet',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      candidate_id:candidateId,
      auto_accept_discovery_candidate:true,
      resolution_packet:resolutionPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el draft de referencia.');
    return;
  }
  await refresh();
}

async function resolveReferenceDraftBatch(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const batchPlan=brain.reference_resolution_batch_plan||{};
  if(!batchPlan.available)return;
  const instructions=[
    `Resolve up to ${Number(batchPlan.candidate_count||0)} draft(s) from ${batchPlan.batch_mode||'guided'} batch.`,
    `Providers: ${(batchPlan.provider_keys||[]).join(', ')||'unknown'}. Source family: ${batchPlan.source_family||'unknown'}.`,
    `Query families: ${(batchPlan.query_families||[]).join(', ')||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Each block must include Candidate ID and Excerpt. URL is recommended but may be omitted when already captured.',
    'You can also paste a JSON array of records with candidate_id, source_url/url, reference_excerpt/excerpt, notes, and optional title/doi/journal/year fields.',
    'Separate blocks with a line containing only ---',
  ].join('\n');
  const resolutionBatchPacket=window.prompt(instructions, batchPlan.quick_packet_template||batchPlan.packet_template||'');
  if(resolutionBatchPacket===null||!resolutionBatchPacket.trim())return;
  const res=await fetch('/api/article-reference-resolve-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      auto_accept_discovery_candidate:true,
      resolution_batch_packet:resolutionBatchPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el batch de drafts.');
    return;
  }
  await refresh();
}

async function resolveCapturedReferenceDraftBatch(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const batchPlan=brain.reference_resolution_batch_plan||{};
  if(!batchPlan.available||!batchPlan.captured_ready)return;
  const instructions=[
    `Resolve captured batch for up to ${Number(batchPlan.candidate_count||0)} draft(s) from ${batchPlan.batch_mode||'guided'} batch.`,
    `Providers: ${(batchPlan.provider_keys||[]).join(', ')||'unknown'}. Source family: ${batchPlan.source_family||'unknown'}.`,
    `Query families: ${(batchPlan.query_families||[]).join(', ')||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Each block must include Candidate ID and Excerpt. Captured article URLs will be reused automatically.',
    'You can also paste a JSON array of records with candidate_id, reference_excerpt/excerpt, notes, and optional title/doi/journal/year fields.',
    'Separate blocks with a line containing only ---',
  ].join('\n');
  const resolutionBatchPacket=window.prompt(instructions, batchPlan.captured_quick_packet_template||batchPlan.quick_packet_template||batchPlan.packet_template||'');
  if(resolutionBatchPacket===null||!resolutionBatchPacket.trim())return;
  const res=await fetch('/api/article-reference-resolve-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      auto_accept_discovery_candidate:true,
      resolution_batch_packet:resolutionBatchPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el batch capturado de drafts.');
    return;
  }
  await refresh();
}

async function resolveReferenceDraftBatchFull(){
  if(!liveData?.run_id)return;
  const brain=liveData?.congruence_brain||{};
  const batchPlan=brain.reference_resolution_batch_plan||{};
  if(!batchPlan.available)return;
  const instructions=[
    `Resolve full batch for up to ${Number(batchPlan.candidate_count||0)} draft(s) from ${batchPlan.batch_mode||'guided'} batch.`,
    `Providers: ${(batchPlan.provider_keys||[]).join(', ')||'unknown'}. Source family: ${batchPlan.source_family||'unknown'}.`,
    `Query families: ${(batchPlan.query_families||[]).join(', ')||'unknown'}.`,
    (batchPlan.evidence_targets||[]).length?`Evidence targets: ${(batchPlan.evidence_targets||[]).join(', ')}`:'',
    batchPlan.batch_reason?`Batch reason: ${batchPlan.batch_reason}`:'',
    'Each block must include Candidate ID, URL and Excerpt. Title/DOI/Journal/Year are optional but supported.',
    'You can also paste a JSON array of records with candidate_id, source_url/url, reference_excerpt/excerpt, notes, and optional title/doi/journal/year fields.',
    'Separate blocks with a line containing only ---',
  ].join('\n');
  const resolutionBatchPacket=window.prompt(instructions, batchPlan.full_packet_template||batchPlan.packet_template||'');
  if(resolutionBatchPacket===null||!resolutionBatchPacket.trim())return;
  const res=await fetch('/api/article-reference-resolve-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id,
      auto_accept_discovery_candidate:true,
      resolution_batch_packet:resolutionBatchPacket
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo resolver el batch completo de drafts.');
    return;
  }
  await refresh();
}

async function readAcceptedArticleReferences(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/article-reference-read-batch',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron leer las referencias aceptadas.');
    return;
  }
  await refresh();
}

async function refreshReferenceBackedPromotions(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/reference-backed-promotions-refresh',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({
      run_id:liveData.run_id
    })
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudieron reconstruir las promotions desde referencias aceptadas.');
    return;
  }
  await refresh();
}

async function materializeRegistryStage(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/registry-stage-materialize',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo materializar el staging de registry.');
    return;
  }
  await refresh();
}

async function mergeRegistryStage(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/registry-stage-merge',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo fusionar el staging hacia la registry.');
    return;
  }
  await refresh();
}

async function materializeProviderHandoff(){
  if(!liveData?.run_id)return;
  const res=await fetch('/api/provider-session-handoff-materialize',{
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body:JSON.stringify({run_id:liveData.run_id})
  });
  const payload=await res.json();
  if(!payload.ok){
    window.alert(payload.error||'No se pudo materializar el handoff de providers.');
    return;
  }
  await refresh();
}

// ── Motores ────────────────────────────────────────────────────
function renderMotores(d){
  const motors=d.motors||[];
  const ov=d.motor_overview||{};
  const total=ov.total_expected||motors.length||34;
  const implemented=ov.implemented_contract||Math.max(total-(ov.placeholder_contract||0),0);
  const healthy=(ov.completed_real||0)+(ov.cached_real||0);
  const active=healthy+(ov.running_real||0)+(ov.failed_real||0);
  const pct=implemented?Math.round(active/implemented*100):0;
  const s=displayState(d);
  document.getElementById('prog-lbl').textContent=`${healthy} motores reales listos · ${(ov.running_real||0)} corriendo · ${(ov.pending_real||0)} pendientes · ${(ov.placeholder_contract||0)} placeholder contractuales · ${(ov.failed_real||0)} reales fallidos`;
  document.getElementById('prog-pct').textContent=`${pct}%`;
  document.getElementById('motor-counts').textContent=total?`${total} motores contractuales · ${implemented} implementados · ${(ov.placeholder_contract||0)} placeholder`:'';
  const fill=document.getElementById('prog-fill');
  fill.style.width=pct+'%';
  fill.className='prog-fill '+(s==='running'?'s-running':s==='completed_partial'||s==='completed_no_pdf'||s==='partial'?'s-partial':((ov.failed||0)>0||s==='failed')?'s-failed':'s-done');
  const dotsEl=document.getElementById('motor-dots');
  if(!motors.length){dotsEl.innerHTML='<div class="empty">Sin datos — corre el framework</div>';return;}
  dotsEl.innerHTML=motors.map(m=>{
    const num=m.motor_id.replace('motor_','');
    const st=m.status||'unknown';
    const dur=m.duration_ms!=null?(m.duration_ms<1000?Math.round(m.duration_ms)+'ms':(m.duration_ms/1000).toFixed(1)+'s'):(st==='cached'?'caché':'');
    const stub=m.is_stub?' · placeholder':'';
    const name=m.motor_name?` · ${m.motor_name}`:'';
    const adapter=m.adapter_class?` · ${m.adapter_class}`:'';
    return`<div class="mdot md-${st}" data-tip="M-${num}${name} · ${ESTADO[st]||st}${dur?' · '+dur:''}${stub}${adapter}">${num}</div>`;
  }).join('');
}

// ── Motores críticos ───────────────────────────────────────────
function renderLLM(d){
  const motors=d.motors||[];
  const total=motors.length||34;
  document.getElementById('llm-note').textContent=
    `Aquí se muestran ${FOCUS_COUNT} motores críticos para inferencia, charts y paquete de reporte. El panel completo del framework queda arriba; esta tabla resume solo la parte más sensible del pipeline.`;
  const llm=d.focus||[];
  const tbl=document.getElementById('llm-table');
  if(!llm.length){tbl.innerHTML='<tr><td class="empty">Sin datos aún</td></tr>';return;}
  const stLbl={completed:'Listo',cached:'En caché',running:'Ejecutando',stub:'Placeholder',failed:'Error',pending:'En espera',missing:'Sin correr'};
  tbl.innerHTML=llm.map(m=>{
    const st=m.status||'pending';
    const dur=m.duration_ms!=null?(m.duration_ms<1000?Math.round(m.duration_ms)+'ms':(m.duration_ms/1000).toFixed(1)+'s'):'';
    const snip=m.snippet?esc(m.snippet)+'…':'';
    return`<tr>
      <td class="lt-num">${m.motor_id.replace('motor_','M-')}</td>
      <td><div class="lt-label">${esc(m.label)}</div>${m.name?`<div class="lt-snippet">${esc(m.name)}</div>`:''}${snip?`<div class="lt-snippet">${snip}</div>`:''}</td>
      <td class="lt-status"><span class="st-badge st-${st}">${stLbl[st]||st}${dur?' · '+dur:''}</span></td>
    </tr>`;
  }).join('');
}

// ── Auditoría ──────────────────────────────────────────────────
function renderAuditoria(d){
  const el=document.getElementById('audit-body');
  const audit=d.audit||{};
  const fails=audit.failures||[];
  if(!d.has_run){el.innerHTML='<div class="empty">Sin análisis activo</div>';return;}
  if(!audit.available&&!fails.length){
    el.innerHTML='<div class="na-note">La auditoría aparecerá al finalizar el análisis (requiere motor_024).</div>';return;
  }
  if(!fails.length){el.innerHTML='<div class="audit-ok">✓ Sin fallos de auditoría detectados</div>';return;}
  el.innerHTML=fails.map(f=>`
    <div class="audit-fail ${f.severity==='warning'?'af-warning':'af-error'}">
      <div class="af-type">${esc(f.type)}</div>
      <div class="af-msg">${esc(f.message)}${f.motor?` <span style="color:var(--faint)">(${esc(f.motor)})</span>`:''}</div>
    </div>`).join('');
}

// ── Targets sidebar ───────────────────────────────────────────
async function loadTargets(){
  try{
    const data=await fj('/api/targets');
    allTargets=data;
    if(selectedPipelineId){
      selectedTarget=data.find(c=>c.pipeline_id===selectedPipelineId)||selectedTarget;
    }else if(liveData?.pipeline_id){
      selectedTarget=data.find(c=>c.pipeline_id===liveData.pipeline_id)||selectedTarget;
    }
    renderTargetList(data,'');
  }catch(e){}
}

function filterTargets(q){renderTargetList(allTargets,q);}

function renderTargetList(data,q){
  const el=document.getElementById('sb-list');
  const filtered=q?data.filter(c=>
    c.name.toLowerCase().includes(q.toLowerCase())||
    (c.target_address||'').toLowerCase().includes(q.toLowerCase())||
    (c.ticker||'').toLowerCase().includes(q.toLowerCase())||
    (c.owner_name||'').toLowerCase().includes(q.toLowerCase())||
    (c.sector||'').toLowerCase().includes(q.toLowerCase())
  ):data;
  if(!filtered.length){
    el.innerHTML='<div style="padding:14px;color:var(--faint);font-size:12px">Sin resultados</div>';return;
  }
  el.innerHTML=filtered.map(c=>{
    const active=selectedPipelineId===c.pipeline_id?'active':'';
    const ds=c.last_run_display_status||c.last_run||'unknown';
    const running=ds==='running';
    const done=ds==='completed';
    const partial=ds==='completed_partial'||ds==='completed_no_pdf'||ds==='partial';
    const failed=ds==='failed';
    const dotCls=running?'ss-running':done?'ss-done':partial?'ss-partial':failed?'ss-failed':'ss-pending';
    return`<div class="sb-item ${active}" onclick="selectTarget('${esc(c.pipeline_id)}','${esc(c.inputs_file||'')}','${esc(c.last_run_id||'')}')">
      <span class="sb-code">${esc(c.target_code||'TGT')}</span>
      <div class="sb-info">
        <div class="sb-name">${esc(c.target_label||c.name)}</div>
        <div class="sb-sector">${esc(c.target_address||c.sector||'')}</div>
        <div class="sb-meta">${esc(c.sector||'')}</div>
      </div>
      <span class="sb-status ${dotCls}" title="${esc(ESTADO[ds]||ds||'Sin analizar')}"></span>
    </div>`;
  }).join('');
}

function selectTarget(pipelineId,inputsFile,runId){
  selectedTarget=allTargets.find(c=>c.pipeline_id===pipelineId)||{pipeline_id:pipelineId,name:pipelineId};
  selectedPipelineId=pipelineId||null;
  selectedInputsFile=inputsFile||'';
  selectedRunId=null;
  document.getElementById('f-pid').value=pipelineId;
  document.getElementById('f-inputs').value=inputsFile;
  document.getElementById('f-nocache').checked=true;
  renderPdf(null, `Target ${selectedTarget?.name||pipelineId} seleccionado. La investigación sigue manual hasta que inicies un run.`, {});
  renderTargetList(allTargets,document.getElementById('sb-search').value||'');
  refresh();
}

// ── PDF ────────────────────────────────────────────────────────
function activePdfVariant(pdf, variants){
  const keys=Object.keys(variants||{});
  if(!keys.length)return pdf||null;
  if(currentPdfLanguage&&variants[currentPdfLanguage])return variants[currentPdfLanguage];
  if(variants.en)return variants.en;
  return variants[keys[0]];
}

function renderPdfLanguageSelector(variants){
  const sel=document.getElementById('pdf-lang-sel');
  const en=document.getElementById('pdf-lang-en');
  const es=document.getElementById('pdf-lang-es');
  const keys=Object.keys(variants||{});
  const hasEn=!!variants?.en;
  const hasEs=!!variants?.es;
  sel.style.display=keys.length>1?'inline-flex':'none';
  en.style.display=hasEn?'inline-block':'none';
  es.style.display=hasEs?'inline-block':'none';
  en.classList.toggle('active', currentPdfLanguage==='en');
  es.classList.toggle('active', currentPdfLanguage==='es');
}

function renderPdf(pdf, placeholderText='Sin reporte aún', variants={}){
  const frame=document.getElementById('pdf-frame');
  const ph=document.getElementById('pdf-ph');
  const ext=document.getElementById('btn-ext');
  currentPdfVariants=variants||{};
  if(currentPdfLanguage && !currentPdfVariants[currentPdfLanguage]){
    currentPdfLanguage=currentPdfVariants.en?'en':(Object.keys(currentPdfVariants)[0]||'en');
  }
  renderPdfLanguageSelector(currentPdfVariants);
  const activePdf=activePdfVariant(pdf,currentPdfVariants);
  if(!activePdf){
    currentPdfPath=null;
    lastPdfMtime=null;
    frame.removeAttribute('src');
    frame.style.display='none';
    ph.style.display='flex';
    ext.style.display='none';
    document.getElementById('pdf-title').textContent='Reporte generado';
    document.getElementById('pdf-title').className='pdf-empty';
    document.getElementById('pdf-sub').textContent=placeholderText;
    return;
  }
  if(activePdf.mtime===lastPdfMtime&&activePdf.path===currentPdfPath)return;
  lastPdfMtime=activePdf.mtime; currentPdfPath=activePdf.path;
  const label=currentPdfLanguage==='es'?'ES':'EN';
  document.getElementById('pdf-title').textContent=activePdf.name;
  document.getElementById('pdf-title').className='pdf-title';
  document.getElementById('pdf-sub').textContent=`${label} · ${activePdf.size_kb} KB · ${activePdf.modified}`;
  frame.src=`/api/serve-pdf/${activePdf.path.replace(/^\//,'')}`;
  frame.style.display='block'; frame.style.flex='1';
  ph.style.display='none'; ext.style.display='inline-block';
}
function selectPdfLanguage(language){
  if(!currentPdfVariants || !currentPdfVariants[language])return;
  currentPdfLanguage=language;
  lastPdfMtime=null;
  renderPdf(liveData?.pdf||null,pdfPlaceholderFor(liveData||{}),currentPdfVariants);
}
function openPdfExt(){if(currentPdfPath)fetch('/api/open-pdf/'+currentPdfPath.replace(/^\//,''));}

// ── Modal ──────────────────────────────────────────────────────
function correr(){openModal('run');}
function openCreateModal(){openModal('create');}
function updateLaunchButtonLabel(){
  const hasAddress=!!document.getElementById('f-address').value.trim();
  const autoRun=document.getElementById('f-auto-run').checked;
  const btn=document.getElementById('btn-launch');
  const hasRunnableTarget=!!(document.getElementById('f-pid').value.trim()||selectedPipelineId);
  if(hasAddress){
    btn.disabled=false;
    btn.textContent=autoRun?'Guardar y ejecutar':'Guardar target';
    return;
  }
  if(modalIntent==='create'){
    btn.textContent='Guardar target';
    btn.disabled=true;
    return;
  }
  btn.disabled=!hasRunnableTarget;
  btn.textContent='▶ Ejecutar ahora';
}
function applyModalIntent(intent){
  const runIntent=intent==='run';
  document.getElementById('modal-title').textContent=runIntent?'Iniciar investigación':'Registrar target';
  document.getElementById('modal-sub').textContent=runIntent
    ?'Lanza manualmente la investigación para el target seleccionado o crea uno nuevo y ejecútalo si así lo indicas.'
    :'Crea el target primero. La investigación se lanza solo si tú lo indicas.';
  document.getElementById('modal-address-hint').textContent=runIntent
    ?'Si rellenas esta dirección, el sistema registra un target nuevo antes de iniciar la investigación.'
    :'Si rellenas esta dirección, el sistema registra un target nuevo. No investigará nada hasta que tú lo decidas.';
}
function openModal(intent='create'){
  modalIntent=intent;
  document.getElementById('modal-bg').classList.add('open');
  document.getElementById('modal-msg').className='';
  document.getElementById('modal-msg').textContent='';
  document.getElementById('btn-launch').disabled=false;
  document.getElementById('f-address').value='';
  document.getElementById('f-nocache').checked=true;
  applyModalIntent(intent);
  if(intent==='run'){
    document.getElementById('f-auto-run').checked=true;
    document.getElementById('f-target-type').value=selectedTarget?.target_type||document.getElementById('f-target-type').value||'';
    document.getElementById('f-owner-name').value=selectedTarget?.owner_name||document.getElementById('f-owner-name').value||'';
    document.getElementById('f-pid').value=selectedPipelineId||liveData?.pipeline_id||'';
    document.getElementById('f-inputs').value=selectedInputsFile||'';
  }else{
    document.getElementById('f-auto-run').checked=false;
    document.getElementById('f-pid').value='';
    document.getElementById('f-inputs').value='';
  }
  updateLaunchButtonLabel();
}
function closeModal(){document.getElementById('modal-bg').classList.remove('open');}
function onBgClick(e){if(e.target.id==='modal-bg')closeModal();}

async function launchRun(){
  const btn=document.getElementById('btn-launch');
  const msgEl=document.getElementById('modal-msg');
  let pid=document.getElementById('f-pid').value.trim()||selectedPipelineId||'';
  let inp=document.getElementById('f-inputs').value.trim()||selectedInputsFile||'';
  const address=document.getElementById('f-address').value.trim();
  const targetType=(document.getElementById('f-target-type').value.trim()||'commercial_building');
  const ownerName=document.getElementById('f-owner-name').value.trim();
  const ownerTicker=document.getElementById('f-owner-ticker').value.trim();
  const autoRun=document.getElementById('f-auto-run').checked;
  const nc=document.getElementById('f-nocache').checked;
  btn.disabled=true;btn.textContent='Lanzando…';msgEl.className='';
  try{
    if(address){
      const createRes=await fetch('/api/create-target',{method:'POST',headers:{'Content-Type':'application/json'},
        body:JSON.stringify({address:address,target_type:targetType,owner_name:ownerName,owner_ticker:ownerTicker})});
      const created=await createRes.json();
      if(!created.ok){
        msgEl.className='err';
        msgEl.textContent=`Error: ${created.error||'No se pudo crear el target.'}`;
        btn.disabled=false;btn.textContent='▶ Ejecutar ahora';
        return;
      }
      pid=created.pipeline_id||pid;
      inp=created.inputs_file||inp;
      selectedPipelineId=pid;
      selectedRunId=null;
      selectedInputsFile=inp;
      document.getElementById('f-pid').value=pid;
      document.getElementById('f-inputs').value=inp;
      await loadTargets();
      selectedTarget=allTargets.find(c=>c.pipeline_id===pid)||selectedTarget||{name:created.target_label||pid,pipeline_id:pid};
      if(!autoRun){
        renderPdf(null, `Target ${selectedTarget?.name||pid} registrado. La investigación no se ha iniciado todavía.`, {});
        msgEl.className='ok';
        msgEl.textContent=`"${pid}" registrado. La investigación sigue manual; iníciala cuando quieras.`;
        setTimeout(()=>{closeModal();refresh();loadTargets();},1200);
        btn.disabled=false;
        updateLaunchButtonLabel();
        return;
      }
    }else if(!pid){
      msgEl.className='err';
      msgEl.textContent='Selecciona un target existente o registra una dirección nueva antes de investigar.';
      btn.disabled=false;
      updateLaunchButtonLabel();
      return;
    }
    const res=await fetch('/api/start-run',{method:'POST',headers:{'Content-Type':'application/json'},
      body:JSON.stringify({pipeline_id:pid,inputs_file:inp,no_cache:nc})});
    const data=await res.json();
    if(data.ok){
      selectedPipelineId=pid;
      selectedRunId=data.run_id||null;
      selectedInputsFile=data.inputs_file||inp;
      if(allTargets.length){
        selectedTarget=allTargets.find(c=>c.pipeline_id===pid)||selectedTarget;
      }
      const runMsg=data.already_running
        ? `Ya había un análisis corriendo para ${selectedTarget?.name||pid}. Se sigue ese run en vivo.`
        : `Ejecutando ${selectedTarget?.name||pid}… el PDF aparecerá al finalizar este run.`;
      renderPdf(null, runMsg, {});
      msgEl.className='ok';
      msgEl.textContent=data.already_running
        ? `"${pid}" ya estaba corriendo. El monitor quedó atado a ese run.`
        : `"${pid}" iniciado. El análisis aparecerá en el monitor en segundos.`;
      setTimeout(()=>{closeModal();refresh();loadTargets();},2000);
    }else{msgEl.className='err';msgEl.textContent=`Error: ${data.error||'No se pudo iniciar.'}`;}
  }catch(e){msgEl.className='err';msgEl.textContent=`Error: ${e.message}`;}
  btn.disabled=false;updateLaunchButtonLabel();
}

function esc(s){
  if(!s)return'';
  return String(s).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
}

init();
</script>
</body>
</html>"""


@app.route("/")
def index():
    return render_template_string(_HTML)


# ── Combination Approval Workflow (V2-LIVE Item 7) ─────────────────────────
# Lifecycle: AI proposes → combinations_pending/ → user approves → combinations/
#                                                → user rejects → combinations_rejected/
# Rule: AI does NOT approve combinations. The dashboard owner does.

try:
    from runtime_orchestrator import combination_approval as _ca
except Exception:  # pragma: no cover - dashboard tolerates import failure
    _ca = None


@app.route("/api/combinations/summary")
def api_combinations_summary():
    if _ca is None:
        return jsonify({"error": "combination_approval module unavailable"}), 503
    return jsonify(_ca.summary())


@app.route("/api/combinations/pending")
def api_combinations_pending():
    if _ca is None:
        return jsonify([])
    return jsonify(_ca.list_pending())


@app.route("/api/combinations/approved")
def api_combinations_approved():
    if _ca is None:
        return jsonify([])
    return jsonify(_ca.list_approved())


@app.route("/api/combinations/rejected")
def api_combinations_rejected():
    if _ca is None:
        return jsonify([])
    return jsonify(_ca.list_rejected())


@app.route("/api/combinations/<state>/<combination_id>")
def api_combinations_get_full(state: str, combination_id: str):
    if _ca is None:
        return jsonify({"error": "combination_approval module unavailable"}), 503
    try:
        return jsonify(_ca.get_full(combination_id, state=state))
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/combinations/approve", methods=["POST"])
def api_combinations_approve():
    if _ca is None:
        return jsonify({"error": "combination_approval module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    combination_id = (body.get("combination_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    if not combination_id:
        return jsonify({"error": "combination_id required"}), 400
    try:
        out = _ca.approve(combination_id, reviewer=reviewer)
        return jsonify({"status": "approved", "combination": out})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except (FileExistsError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/combinations/reject", methods=["POST"])
def api_combinations_reject():
    if _ca is None:
        return jsonify({"error": "combination_approval module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    combination_id = (body.get("combination_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    reason = (body.get("reason") or "").strip()
    if not combination_id:
        return jsonify({"error": "combination_id required"}), 400
    if not reason:
        return jsonify({"error": "rejection reason required"}), 400
    try:
        out = _ca.reject(combination_id, reviewer=reviewer, reason=reason)
        return jsonify({"status": "rejected", "combination": out})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/combinations/edit", methods=["POST"])
def api_combinations_edit():
    if _ca is None:
        return jsonify({"error": "combination_approval module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    combination_id = (body.get("combination_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    patch = body.get("patch") or {}
    if not combination_id:
        return jsonify({"error": "combination_id required"}), 400
    if not isinstance(patch, dict) or not patch:
        return jsonify({"error": "patch (dict) required"}), 400
    try:
        out = _ca.edit(combination_id, reviewer=reviewer, patch=patch)
        return jsonify({"status": "edited", "combination": out})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/combinations/editable-fields")
def api_combinations_editable_fields():
    if _ca is None:
        return jsonify([])
    return jsonify(list(_ca.editable_fields()))


@app.route("/api/combinations/reset", methods=["POST"])
def api_combinations_reset():
    if _ca is None:
        return jsonify({"error": "combination_approval module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    combination_id = (body.get("combination_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    if not combination_id:
        return jsonify({"error": "combination_id required"}), 400
    try:
        out = _ca.reset_to_pending(combination_id, reviewer=reviewer)
        return jsonify({"status": "reset_to_pending", "combination": out})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except (FileExistsError, ValueError) as exc:
        return jsonify({"error": str(exc)}), 400


_COMBINATION_APPROVAL_HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Combinations — ZLab</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:24px;}
h1{font-size:20px;margin:0 0 16px 0;}
h2{font-size:14px;margin:24px 0 8px 0;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;}
.tabs{display:flex;gap:8px;margin-bottom:16px;}
.tab{padding:8px 14px;background:#161b22;border:1px solid #30363d;border-radius:6px;cursor:pointer;}
.tab.active{background:#1f6feb;border-color:#1f6feb;color:#fff;}
.card{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:16px;margin-bottom:12px;}
.card h3{margin:0 0 4px 0;font-size:16px;}
.card .sub{color:#7d8590;font-size:12px;margin-bottom:8px;}
.card .meta{font-size:12px;color:#7d8590;margin-bottom:8px;}
.card .pid{display:inline-block;background:#21262d;border:1px solid #30363d;border-radius:4px;padding:2px 8px;margin:2px 4px 2px 0;font-size:11px;font-family:monospace;}
.card .body{font-size:13px;line-height:1.5;color:#c9d1d9;margin-bottom:8px;}
.btn{padding:6px 12px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:12px;margin-right:6px;}
.btn-approve{background:#238636;color:#fff;}
.btn-reject{background:#da3633;color:#fff;}
.btn-edit{background:#bf8700;color:#fff;}
.btn-reset{background:#1f6feb;color:#fff;}
.edit-badge{display:inline-block;background:#bf8700;color:#fff;border-radius:4px;padding:1px 6px;font-size:10px;margin-left:6px;font-weight:600;}
.empty{color:#7d8590;font-style:italic;padding:16px;}
.summary{display:flex;gap:24px;margin-bottom:24px;}
.stat{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:12px 20px;}
.stat .label{font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;}
.stat .value{font-size:24px;font-weight:600;color:#e6edf3;}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);align-items:center;justify-content:center;}
.modal.open{display:flex;}
.modal-box{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:24px;width:480px;max-width:90vw;}
.modal-box textarea{width:100%;height:100px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:8px;font-family:inherit;}
</style></head>
<body>
<h1>Combination Approval — ZLab OTF</h1>

<div class="summary" id="summary"></div>

<div class="tabs">
  <div class="tab active" data-state="pending" onclick="loadState('pending')">Pending</div>
  <div class="tab" data-state="approved" onclick="loadState('approved')">Approved</div>
  <div class="tab" data-state="rejected" onclick="loadState('rejected')">Rejected</div>
</div>

<div id="list"></div>

<div class="modal" id="rejectModal">
  <div class="modal-box">
    <h2>Reject combination</h2>
    <p id="rejectId" style="color:#7d8590;font-family:monospace;"></p>
    <textarea id="rejectReason" placeholder="Reason for rejection (required, max 1000 chars)..."></textarea>
    <div style="margin-top:12px;">
      <button class="btn btn-reject" onclick="confirmReject()">Reject</button>
      <button class="btn" style="background:#30363d;color:#fff;" onclick="closeReject()">Cancel</button>
    </div>
  </div>
</div>

<div class="modal" id="editModal">
  <div class="modal-box" style="width:640px;max-height:85vh;overflow-y:auto;">
    <h2>Edit combination</h2>
    <p id="editId" style="color:#7d8590;font-family:monospace;"></p>
    <div style="font-size:12px;color:#7d8590;margin-bottom:12px;">Modify the fields below; leave a field unchanged to keep its current value. After saving, the combination stays in <em>pending</em> for approval.</div>

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Name</label>
    <input type="text" id="editName" style="width:100%;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;margin-bottom:10px;">

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Pattern IDs (comma-separated)</label>
    <input type="text" id="editPatternIds" style="width:100%;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;margin-bottom:10px;font-family:monospace;font-size:12px;">

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Combined hypothesis</label>
    <textarea id="editHypothesis" style="width:100%;height:60px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-family:inherit;margin-bottom:10px;"></textarea>

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Strategic risk</label>
    <textarea id="editRisk" style="width:100%;height:60px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-family:inherit;margin-bottom:10px;"></textarea>

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">TAD action</label>
    <input type="text" id="editTadAction" style="width:100%;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;margin-bottom:10px;">

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Minimum evidence (one per line)</label>
    <textarea id="editMinEvidence" style="width:100%;height:80px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-family:monospace;font-size:12px;margin-bottom:10px;"></textarea>

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Trigger logic (one per line)</label>
    <textarea id="editTriggerLogic" style="width:100%;height:60px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-family:monospace;font-size:12px;margin-bottom:10px;"></textarea>

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Anti-triggers (one per line)</label>
    <textarea id="editAntiTriggers" style="width:100%;height:60px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-family:monospace;font-size:12px;margin-bottom:10px;"></textarea>

    <label style="font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;">Prohibited claims (one per line)</label>
    <textarea id="editProhibitedClaims" style="width:100%;height:60px;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:6px;font-family:monospace;font-size:12px;margin-bottom:10px;"></textarea>

    <div style="margin-top:12px;">
      <button class="btn btn-edit" onclick="confirmEdit()">Save changes</button>
      <button class="btn" style="background:#30363d;color:#fff;" onclick="closeEdit()">Cancel</button>
    </div>
  </div>
</div>

<script>
const REVIEWER = (function(){
  let r = localStorage.getItem('zlab_reviewer');
  if (!r) { r = prompt('Your reviewer name:') || 'dashboard_user'; localStorage.setItem('zlab_reviewer', r); }
  return r;
})();

let currentState = 'pending';

async function loadSummary() {
  const r = await fetch('/api/combinations/summary'); const d = await r.json();
  document.getElementById('summary').innerHTML =
    `<div class="stat"><div class="label">Pending</div><div class="value">${d.pending_count||0}</div></div>` +
    `<div class="stat"><div class="label">Approved</div><div class="value">${d.approved_count||0}</div></div>` +
    `<div class="stat"><div class="label">Rejected</div><div class="value">${d.rejected_count||0}</div></div>`;
}

async function loadState(state) {
  currentState = state;
  document.querySelectorAll('.tab').forEach(t => t.classList.toggle('active', t.dataset.state===state));
  const r = await fetch('/api/combinations/'+state); const rows = await r.json();
  const list = document.getElementById('list');
  if (!rows.length) { list.innerHTML = '<div class="empty">No combinations in this state.</div>'; return; }
  list.innerHTML = rows.map(c => renderCard(c, state)).join('');
}

function renderCard(c, state) {
  const pids = (c.pattern_ids||[]).map(p => `<span class="pid">${p}</span>`).join('');
  let actions = '';
  if (state === 'pending') {
    actions = `<button class="btn btn-approve" onclick="doApprove('${c.combination_id}')">✓ Approve</button>` +
              `<button class="btn btn-edit" onclick="openEdit('${c.combination_id}')">✎ Edit</button>` +
              `<button class="btn btn-reject" onclick="openReject('${c.combination_id}')">✗ Reject</button>`;
  } else if (state === 'rejected') {
    actions = `<button class="btn btn-reset" onclick="doReset('${c.combination_id}')">↺ Re-review</button>`;
  }
  let metaLine = '';
  if (state === 'pending') metaLine = `proposed by ${c.proposed_by||'?'} at ${c.proposed_at||'?'}`;
  else if (state === 'approved') metaLine = `approved by ${c.approved_by||'?'} at ${c.approved_at||'?'}`;
  else if (state === 'rejected') metaLine = `rejected by ${c.rejected_by||'?'} at ${c.rejected_at||'?'} — reason: ${c.rejection_reason||'(none)'}`;
  const editBadge = (c.edit_count && c.edit_count > 0)
    ? `<span class="edit-badge">edited ${c.edit_count}× by ${c.edited_by||'?'}</span>` : '';
  return `<div class="card">
    <h3>${c.name || c.combination_id}${editBadge}</h3>
    <div class="sub">${c.combination_id} · v${c.version||'?'} · TAD: ${c.tad_action||'(none)'}</div>
    <div class="meta">${metaLine}</div>
    <div>${pids}</div>
    <div class="body"><strong>Hypothesis:</strong> ${c.combined_hypothesis||'(none)'}</div>
    <div class="body"><strong>Strategic risk:</strong> ${c.strategic_risk||'(none)'}</div>
    <div class="body"><strong>Min evidence items:</strong> ${c.minimum_evidence_count}</div>
    <div>${actions}</div>
  </div>`;
}

async function doApprove(id) {
  if (!confirm(`Approve "${id}"? It will be loaded by the skill on the next pipeline run.`)) return;
  const r = await fetch('/api/combinations/approve', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({combination_id: id, reviewer: REVIEWER})});
  if (!r.ok) { const e = await r.json(); alert('Approve failed: ' + (e.error||r.statusText)); return; }
  await loadSummary(); await loadState(currentState);
}

let _rejectingId = null;
function openReject(id) { _rejectingId = id; document.getElementById('rejectId').textContent = id; document.getElementById('rejectReason').value = ''; document.getElementById('rejectModal').classList.add('open'); }
function closeReject() { _rejectingId = null; document.getElementById('rejectModal').classList.remove('open'); }
async function confirmReject() {
  const reason = document.getElementById('rejectReason').value.trim();
  if (!reason) { alert('Reason required'); return; }
  const r = await fetch('/api/combinations/reject', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({combination_id: _rejectingId, reviewer: REVIEWER, reason})});
  if (!r.ok) { const e = await r.json(); alert('Reject failed: ' + (e.error||r.statusText)); return; }
  closeReject(); await loadSummary(); await loadState(currentState);
}

async function doReset(id) {
  if (!confirm(`Move "${id}" back to pending for re-review?`)) return;
  const r = await fetch('/api/combinations/reset', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({combination_id: id, reviewer: REVIEWER})});
  if (!r.ok) { const e = await r.json(); alert('Reset failed: ' + (e.error||r.statusText)); return; }
  await loadSummary(); await loadState(currentState);
}

let _editingId = null;
let _editingOriginal = null;
async function openEdit(id) {
  _editingId = id;
  const r = await fetch('/api/combinations/pending/' + id);
  if (!r.ok) { alert('Could not load combination'); return; }
  const full = await r.json();
  _editingOriginal = full;
  document.getElementById('editId').textContent = id;
  document.getElementById('editName').value = full.name || '';
  document.getElementById('editPatternIds').value = (full.pattern_ids||[]).join(', ');
  document.getElementById('editHypothesis').value = full.combined_hypothesis || '';
  document.getElementById('editRisk').value = full.strategic_risk || '';
  document.getElementById('editTadAction').value = full.tad_action || '';
  document.getElementById('editMinEvidence').value = (full.minimum_evidence||[]).join('\\n');
  document.getElementById('editTriggerLogic').value = (full.trigger_logic||[]).join('\\n');
  document.getElementById('editAntiTriggers').value = (full.anti_triggers||[]).join('\\n');
  document.getElementById('editProhibitedClaims').value = (full.prohibited_claims||[]).join('\\n');
  document.getElementById('editModal').classList.add('open');
}
function closeEdit() {
  _editingId = null; _editingOriginal = null;
  document.getElementById('editModal').classList.remove('open');
}
function _parseLines(v) {
  return (v||'').split('\\n').map(s => s.trim()).filter(s => s.length);
}
function _parseCsv(v) {
  return (v||'').split(',').map(s => s.trim()).filter(s => s.length);
}
async function confirmEdit() {
  const patch = {};
  const orig = _editingOriginal || {};
  const candidates = {
    name: document.getElementById('editName').value.trim(),
    pattern_ids: _parseCsv(document.getElementById('editPatternIds').value),
    combined_hypothesis: document.getElementById('editHypothesis').value.trim(),
    strategic_risk: document.getElementById('editRisk').value.trim(),
    tad_action: document.getElementById('editTadAction').value.trim(),
    minimum_evidence: _parseLines(document.getElementById('editMinEvidence').value),
    trigger_logic: _parseLines(document.getElementById('editTriggerLogic').value),
    anti_triggers: _parseLines(document.getElementById('editAntiTriggers').value),
    prohibited_claims: _parseLines(document.getElementById('editProhibitedClaims').value),
  };
  // Only include fields that actually changed.
  for (const k in candidates) {
    const newVal = candidates[k];
    const oldVal = orig[k];
    const newStr = JSON.stringify(newVal);
    const oldStr = JSON.stringify(oldVal === undefined ? (Array.isArray(newVal) ? [] : '') : oldVal);
    if (newStr !== oldStr) patch[k] = newVal;
  }
  if (Object.keys(patch).length === 0) {
    alert('No changes to save.'); return;
  }
  const r = await fetch('/api/combinations/edit', {
    method:'POST',
    headers:{'Content-Type':'application/json'},
    body: JSON.stringify({combination_id: _editingId, reviewer: REVIEWER, patch})
  });
  if (!r.ok) { const e = await r.json(); alert('Edit failed: ' + (e.error||r.statusText)); return; }
  closeEdit(); await loadSummary(); await loadState(currentState);
}

loadSummary(); loadState('pending');
setInterval(()=>{loadSummary();loadState(currentState);}, 30000);
</script>
</body></html>"""


@app.route("/combinations")
def combinations_page():
    return render_template_string(_COMBINATION_APPROVAL_HTML)


# ── Scenario Review Workflow (V2-CRITICAL course correction) ───────────────
# Dashboard is the review center. The PDF only renders after the user
# approves every active scenario for the case.

try:
    from runtime_orchestrator import scenario_review as _sr
except Exception:  # pragma: no cover
    _sr = None


@app.route("/api/scenarios/cases")
def api_scenarios_cases():
    if _sr is None:
        return jsonify([])
    return jsonify(_sr.list_cases())


@app.route("/api/scenarios/<path:case_id>")
def api_scenarios_get_case(case_id: str):
    if _sr is None:
        return jsonify({"error": "scenario_review module unavailable"}), 503
    try:
        return jsonify(_sr.get_case(case_id))
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/scenarios/approve", methods=["POST"])
def api_scenarios_approve():
    if _sr is None:
        return jsonify({"error": "scenario_review module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    case_id = (body.get("case_id") or "").strip()
    scenario_id = (body.get("scenario_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    if not case_id or not scenario_id:
        return jsonify({"error": "case_id and scenario_id required"}), 400
    try:
        return jsonify({"status": "approved", "case": _sr.approve(case_id, scenario_id, reviewer)})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/scenarios/reject", methods=["POST"])
def api_scenarios_reject():
    if _sr is None:
        return jsonify({"error": "scenario_review module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    case_id = (body.get("case_id") or "").strip()
    scenario_id = (body.get("scenario_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    reason = (body.get("reason") or "").strip()
    if not case_id or not scenario_id:
        return jsonify({"error": "case_id and scenario_id required"}), 400
    if not reason:
        return jsonify({"error": "rejection reason required"}), 400
    try:
        return jsonify({"status": "rejected", "case": _sr.reject(case_id, scenario_id, reviewer, reason)})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/scenarios/edit", methods=["POST"])
def api_scenarios_edit():
    if _sr is None:
        return jsonify({"error": "scenario_review module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    case_id = (body.get("case_id") or "").strip()
    scenario_id = (body.get("scenario_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    patch = body.get("patch") or {}
    if not case_id or not scenario_id:
        return jsonify({"error": "case_id and scenario_id required"}), 400
    if not isinstance(patch, dict) or not patch:
        return jsonify({"error": "patch (dict) required"}), 400
    try:
        return jsonify({"status": "edited", "case": _sr.edit(case_id, scenario_id, reviewer, patch)})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


@app.route("/api/scenarios/approve-all", methods=["POST"])
def api_scenarios_approve_all():
    if _sr is None:
        return jsonify({"error": "scenario_review module unavailable"}), 503
    body = request.get_json(silent=True) or {}
    case_id = (body.get("case_id") or "").strip()
    reviewer = (body.get("reviewer") or "dashboard_user").strip()
    if not case_id:
        return jsonify({"error": "case_id required"}), 400
    try:
        return jsonify({"status": "all_approved", "case": _sr.approve_all(case_id, reviewer)})
    except FileNotFoundError as exc:
        return jsonify({"error": str(exc)}), 404
    except ValueError as exc:
        return jsonify({"error": str(exc)}), 400


_SCENARIO_REVIEW_HTML = """<!doctype html>
<html lang="es"><head><meta charset="utf-8"><title>Scenarios — ZLab Review Center</title>
<style>
body{font-family:-apple-system,BlinkMacSystemFont,"Segoe UI",sans-serif;background:#0d1117;color:#e6edf3;margin:0;padding:24px;}
h1{font-size:20px;margin:0 0 8px 0;}
.subtitle{color:#7d8590;font-size:13px;margin-bottom:20px;}
.case{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:18px;margin-bottom:18px;}
.case h2{font-size:16px;margin:0 0 4px 0;}
.case .meta{color:#7d8590;font-size:12px;margin-bottom:14px;}
.case.ready{border-left:4px solid #238636;}
.case.pending{border-left:4px solid #bf8700;}
.scenario{background:#0d1117;border:1px solid #30363d;border-radius:6px;padding:14px;margin-bottom:10px;}
.scenario h3{font-size:14px;margin:0 0 8px 0;}
.state{display:inline-block;font-size:10px;padding:2px 8px;border-radius:4px;text-transform:uppercase;font-weight:600;letter-spacing:.5px;margin-left:8px;}
.state.pending{background:#bf8700;color:#fff;}
.state.approved{background:#238636;color:#fff;}
.state.rejected{background:#da3633;color:#fff;}
.state.edited{background:#1f6feb;color:#fff;}
.field{font-size:12px;line-height:1.5;margin-bottom:4px;}
.field .lbl{color:#7d8590;display:inline-block;width:130px;}
.btn{padding:5px 11px;border:none;border-radius:6px;cursor:pointer;font-weight:600;font-size:11px;margin-right:6px;}
.btn-approve{background:#238636;color:#fff;}
.btn-reject{background:#da3633;color:#fff;}
.btn-edit{background:#bf8700;color:#fff;}
.btn-approve-all{background:#238636;color:#fff;padding:7px 14px;font-size:12px;}
.empty{color:#7d8590;font-style:italic;padding:24px;text-align:center;}
.modal{display:none;position:fixed;top:0;left:0;width:100%;height:100%;background:rgba(0,0,0,0.7);align-items:center;justify-content:center;z-index:1000;}
.modal.open{display:flex;}
.modal-box{background:#161b22;border:1px solid #30363d;border-radius:8px;padding:24px;width:540px;max-width:90vw;max-height:85vh;overflow-y:auto;}
.modal-box label{display:block;font-size:11px;color:#7d8590;text-transform:uppercase;letter-spacing:.5px;margin-top:10px;}
.modal-box textarea,.modal-box input{width:100%;background:#0d1117;color:#e6edf3;border:1px solid #30363d;border-radius:6px;padding:7px;font-family:inherit;font-size:13px;}
.modal-box textarea{height:60px;}
.summary-bar{display:flex;gap:12px;margin-bottom:20px;}
.chip{background:#161b22;border:1px solid #30363d;border-radius:18px;padding:6px 14px;font-size:12px;color:#7d8590;}
.chip.pending{color:#bf8700;}
.chip.approved{color:#238636;}
.chip.rejected{color:#da3633;}
</style></head>
<body>
<h1>Scenario Review — ZLab Operations Center</h1>
<div class="subtitle">Pipeline runs seed scenarios here. PDF only renders when every scenario is approved or rejected.</div>

<div id="cases"></div>

<div class="modal" id="rejectModal"><div class="modal-box">
  <h2>Reject scenario</h2>
  <p id="rejectLabel" style="color:#7d8590;font-size:12px;font-family:monospace;"></p>
  <label>Reason (required, max 1000 chars)</label>
  <textarea id="rejectReason"></textarea>
  <div style="margin-top:14px;">
    <button class="btn btn-reject" onclick="confirmReject()">Reject</button>
    <button class="btn" style="background:#30363d;color:#fff;" onclick="closeReject()">Cancel</button>
  </div>
</div></div>

<div class="modal" id="editModal"><div class="modal-box">
  <h2>Edit justification</h2>
  <p id="editLabel" style="color:#7d8590;font-size:12px;font-family:monospace;"></p>
  <label>Trigger</label><textarea id="editTrigger"></textarea>
  <label>Source (catalog source_ids)</label><textarea id="editSource"></textarea>
  <label>Process Clue</label><textarea id="editProcessClue"></textarea>
  <label>Industrial Reason</label><textarea id="editIndustrialReason"></textarea>
  <label>Asset Family Reason</label><textarea id="editAssetFamilyReason"></textarea>
  <div style="margin-top:14px;">
    <button class="btn btn-edit" onclick="confirmEdit()">Save changes</button>
    <button class="btn" style="background:#30363d;color:#fff;" onclick="closeEdit()">Cancel</button>
  </div>
</div></div>

<script>
const REVIEWER = (function(){
  let r = localStorage.getItem('zlab_reviewer');
  if (!r) { r = prompt('Your reviewer name:') || 'dashboard_user'; localStorage.setItem('zlab_reviewer', r); }
  return r;
})();

let _cases = [];

async function load() {
  const r = await fetch('/api/scenarios/cases');
  _cases = await r.json();
  render();
}

function render() {
  const root = document.getElementById('cases');
  if (!_cases.length) { root.innerHTML = '<div class="empty">No cases under review yet. Run a pipeline to seed scenarios.</div>'; return; }
  root.innerHTML = _cases.map(renderCase).join('');
  _cases.forEach(c => loadCaseDetail(c.case_id));
}

async function loadCaseDetail(caseId) {
  const r = await fetch('/api/scenarios/' + encodeURIComponent(caseId));
  if (!r.ok) return;
  const data = await r.json();
  const el = document.getElementById('case-' + cssEscape(caseId));
  if (!el) return;
  const scenarios = data.scenarios || {};
  const ordered = Object.keys(scenarios).sort();
  const items = ordered.map(sid => renderScenario(caseId, sid, scenarios[sid])).join('');
  el.querySelector('.scenarios').innerHTML = items || '<div class="empty">No scenarios.</div>';
}

function cssEscape(s) { return s.replace(/[^a-zA-Z0-9_-]/g, '_'); }

function renderCase(c) {
  const cls = c.ready_to_render ? 'ready' : 'pending';
  const banner = c.ready_to_render
    ? '<span style="color:#238636;font-weight:600;">✓ Ready to render</span>'
    : '<span style="color:#bf8700;font-weight:600;">⏳ ' + (c.pending_count + c.edited_count) + ' awaiting review</span>';
  return `<div class="case ${cls}" id="case-${cssEscape(c.case_id)}">
    <h2>${c.case_id}</h2>
    <div class="meta">${c.asset_family||'?'} · ${c.scenario_count} scenarios · updated ${c.updated_at||'never'} · ${banner}</div>
    <div class="summary-bar">
      <div class="chip pending">${c.pending_count} pending</div>
      <div class="chip" style="color:#1f6feb;">${c.edited_count} edited</div>
      <div class="chip approved">${c.approved_count} approved</div>
      <div class="chip rejected">${c.rejected_count} rejected</div>
      <button class="btn btn-approve-all" onclick="approveAll('${c.case_id}')">✓ Approve all remaining</button>
    </div>
    <div class="scenarios"><div class="empty">Loading...</div></div>
  </div>`;
}

function renderScenario(caseId, sid, sc) {
  const state = sc.state || 'pending';
  let actions = '';
  if (state !== 'rejected') {
    actions = `<button class="btn btn-approve" onclick="approveScenario('${caseId}','${sid}')">✓ Approve</button>` +
              `<button class="btn btn-edit" onclick="openEdit('${caseId}','${sid}')">✎ Edit</button>` +
              `<button class="btn btn-reject" onclick="openReject('${caseId}','${sid}')">✗ Reject</button>`;
  }
  let footer = '';
  if (sc.reviewer) footer += `<div class="field" style="color:#7d8590;margin-top:8px;">reviewed by ${sc.reviewer} at ${sc.reviewed_at||'?'}`;
  if (sc.rejection_reason) footer += ` — reason: ${escapeHtml(sc.rejection_reason)}`;
  if (sc.edit_count > 0) footer += ` (edited ${sc.edit_count}×)`;
  footer += '</div>';
  return `<div class="scenario">
    <h3>${escapeHtml(sc.scenario || sid)}<span class="state ${state}">${state}</span></h3>
    <div class="field"><span class="lbl">Trigger:</span> ${escapeHtml(sc.trigger||'(missing)')}</div>
    <div class="field"><span class="lbl">Source:</span> <code>${escapeHtml(sc.source||'(missing)')}</code></div>
    <div class="field"><span class="lbl">Process clue:</span> ${escapeHtml(sc.process_clue||'(missing)')}</div>
    <div class="field"><span class="lbl">Industrial reason:</span> ${escapeHtml(sc.industrial_reason||'(missing)')}</div>
    <div class="field"><span class="lbl">Asset-family reason:</span> ${escapeHtml(sc.asset_family_reason||'(missing)')}</div>
    ${footer}
    <div style="margin-top:10px;">${actions}</div>
  </div>`;
}

function escapeHtml(s) { return String(s||'').replace(/[&<>"]/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;'})[c]); }

async function approveScenario(caseId, sid) {
  const r = await fetch('/api/scenarios/approve', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({case_id:caseId, scenario_id:sid, reviewer:REVIEWER})});
  if (!r.ok) { const e = await r.json(); alert('Approve failed: '+(e.error||r.statusText)); return; }
  load();
}

async function approveAll(caseId) {
  if (!confirm(`Approve every remaining scenario in "${caseId}"?`)) return;
  const r = await fetch('/api/scenarios/approve-all', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({case_id:caseId, reviewer:REVIEWER})});
  if (!r.ok) { const e = await r.json(); alert('Approve-all failed: '+(e.error||r.statusText)); return; }
  load();
}

let _rejecting = null;
function openReject(caseId, sid) { _rejecting = {caseId, sid}; document.getElementById('rejectLabel').textContent = `${caseId} / ${sid}`; document.getElementById('rejectReason').value=''; document.getElementById('rejectModal').classList.add('open'); }
function closeReject() { _rejecting = null; document.getElementById('rejectModal').classList.remove('open'); }
async function confirmReject() {
  const reason = document.getElementById('rejectReason').value.trim();
  if (!reason) { alert('Reason required'); return; }
  const r = await fetch('/api/scenarios/reject', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({case_id:_rejecting.caseId, scenario_id:_rejecting.sid, reviewer:REVIEWER, reason})});
  if (!r.ok) { const e = await r.json(); alert('Reject failed: '+(e.error||r.statusText)); return; }
  closeReject(); load();
}

let _editing = null;
async function openEdit(caseId, sid) {
  _editing = {caseId, sid};
  const r = await fetch('/api/scenarios/' + encodeURIComponent(caseId));
  if (!r.ok) { alert('Could not load case'); return; }
  const data = await r.json();
  const sc = (data.scenarios||{})[sid] || {};
  document.getElementById('editLabel').textContent = `${caseId} / ${sid}`;
  document.getElementById('editTrigger').value = sc.trigger || '';
  document.getElementById('editSource').value = sc.source || '';
  document.getElementById('editProcessClue').value = sc.process_clue || '';
  document.getElementById('editIndustrialReason').value = sc.industrial_reason || '';
  document.getElementById('editAssetFamilyReason').value = sc.asset_family_reason || '';
  document.getElementById('editModal').classList.add('open');
}
function closeEdit() { _editing = null; document.getElementById('editModal').classList.remove('open'); }
async function confirmEdit() {
  const patch = {
    trigger: document.getElementById('editTrigger').value.trim(),
    source: document.getElementById('editSource').value.trim(),
    process_clue: document.getElementById('editProcessClue').value.trim(),
    industrial_reason: document.getElementById('editIndustrialReason').value.trim(),
    asset_family_reason: document.getElementById('editAssetFamilyReason').value.trim(),
  };
  const r = await fetch('/api/scenarios/edit', {method:'POST', headers:{'Content-Type':'application/json'}, body: JSON.stringify({case_id:_editing.caseId, scenario_id:_editing.sid, reviewer:REVIEWER, patch})});
  if (!r.ok) { const e = await r.json(); alert('Edit failed: '+(e.error||r.statusText)); return; }
  closeEdit(); load();
}

load();
setInterval(load, 30000);
</script>
</body></html>"""


@app.route("/scenarios")
def scenarios_page():
    return render_template_string(_SCENARIO_REVIEW_HTML)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="ZLab OTF — Monitor")
    parser.add_argument("--port", type=int, default=7474)
    parser.add_argument("--open", action="store_true", dest="auto_open")
    args = parser.parse_args()

    os.chdir(_HERE)
    if args.auto_open:
        def _open():
            time.sleep(1.2)
            subprocess.Popen(["open", f"http://localhost:{args.port}"])
        threading.Thread(target=_open, daemon=True).start()

    print(f"ZLab OTF Monitor → http://localhost:{args.port}")
    app.run(host="0.0.0.0", port=args.port, debug=False, use_reloader=False)


if __name__ == "__main__":
    main()
