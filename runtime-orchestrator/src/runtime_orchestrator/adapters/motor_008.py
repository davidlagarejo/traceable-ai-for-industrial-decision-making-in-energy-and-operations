"""Adapter for motor_008 — Source Registry Engine.

Builds a structured source registry with ingestion-facing semantics:

- scope
- authority score
- recency
- accepted / rejected
- rejection reason
- asset-level eligibility

This motor does not fetch. It only classifies declared sources and preserves
their epistemic boundary for downstream motors.
"""
from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from .base import BaseMotorAdapter


def _normalize_text(value: Any) -> str:
    return str(value or "").strip().lower()


def _infer_scope(source_id: str, meta: dict[str, Any], fetch_url: str) -> str:
    explicit = str(meta.get("scope") or meta.get("source_scope") or "").strip().upper()
    if explicit:
        return explicit
    haystack = " ".join([source_id, fetch_url, str(meta.get("title", "")), str(meta.get("fetch_type", ""))]).lower()
    if any(token in haystack for token in ("sec", "edgar", "10-k", "10q", "investor", "annual-report", "annual_report")):
        return "ENTITY_LEVEL"
    if any(token in haystack for token in ("portfolio", "esg", "sustainability", "global-metric", "global_metric")):
        return "PORTFOLIO_LEVEL"
    if any(token in haystack for token in ("benchmark", "cbecs", "ashrae", "doe", "energy star", "energystar")):
        return "BENCHMARK_LEVEL"
    if any(token in haystack for token in ("city", "county", "state", "permit", "assessor", "parcel", "zoning", "ordinance", "utility", "jurisdiction")):
        return "JURISDICTION_LEVEL"
    return "ASSET_LEVEL"


def _authority_score(source_id: str, meta: dict[str, Any], fetch_url: str) -> str:
    explicit = _normalize_text(meta.get("authority_score") or meta.get("authority_class"))
    if explicit in {"high", "medium", "low"}:
        return explicit
    authoritative = bool(meta.get("authoritative"))
    haystack = " ".join([source_id, fetch_url, str(meta.get("title", ""))]).lower()
    if authoritative or any(token in haystack for token in ("assessor", "permit", "benchmarking", "utility", "municipal", "regulatory", "sec", "edgar", ".gov")):
        return "high"
    if any(token in haystack for token in ("brochure", "leasing", "energy star", "energystar", "property", "sustainability", "investor")):
        return "medium"
    return "low"


def _source_family(source_id: str, meta: dict[str, Any], fetch_url: str, scope: str) -> str:
    explicit = str(meta.get("source_family") or "").strip()
    if explicit:
        return explicit
    haystack = " ".join([source_id, fetch_url]).lower()
    if "assessor" in haystack or "parcel" in haystack:
        return "parcel_assessor_record"
    if "permit" in haystack:
        return "building_permitting_record"
    if "benchmark" in haystack or "energystar" in haystack or "energy star" in haystack:
        return "benchmarking_disclosure_record"
    if "sec" in haystack or "edgar" in haystack:
        return "issuer_financial_record"
    if scope == "JURISDICTION_LEVEL":
        return "code_regulation_record"
    if scope == "BENCHMARK_LEVEL":
        return "sector_energy_intensity_reference"
    if scope == "PORTFOLIO_LEVEL":
        return "portfolio_context_record"
    if scope == "ENTITY_LEVEL":
        return "issuer_context_record"
    return "asset_context_record"


def _recency(meta: dict[str, Any]) -> str:
    explicit = _normalize_text(meta.get("recency"))
    if explicit in {"current", "stale", "unknown"}:
        return explicit
    published = meta.get("published_at") or meta.get("produced_at") or meta.get("updated_at")
    if not published:
        return "unknown"
    try:
        dt = datetime.fromisoformat(str(published).replace("Z", "+00:00"))
        age_days = (datetime.now(timezone.utc) - dt.astimezone(timezone.utc)).days
        return "current" if age_days <= 730 else "stale"
    except Exception:
        return "unknown"


def _asset_level_eligible(scope: str, authority_score: str) -> bool:
    return scope == "ASSET_LEVEL" and authority_score in {"high", "medium"}


class Motor008Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_008"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        pipeline = inputs.get("__pipeline__", {})
        contracts = inputs.get("motor_001", {}).get("validated_contracts", [])
        sources = pipeline.get("sources", [])
        subject = pipeline.get("subject", {})
        ingestion_contract_status = inputs.get("motor_001", {}).get("ingestion_contract_status", "")

        registry: dict[str, Any] = {}
        sources_requiring_fetch: list[str] = []
        sources_with_content: list[str] = []
        accepted_source_ids: list[str] = []
        rejected_source_ids: list[str] = []

        for src in sources:
            sid = src.get("source_id", "")
            meta = src.get("metadata", {}) if isinstance(src.get("metadata", {}), dict) else {}
            content = src.get("content", "")
            content_type = src.get("content_type", "text")
            fetch_url = str(meta.get("fetch_url", "")).strip()

            needs_fetch = (
                not str(content or "").strip()
                or content_type == "reference"
                or meta.get("retrieval_required", False)
            )
            scope = _infer_scope(sid, meta, fetch_url)
            authority_score = _authority_score(sid, meta, fetch_url)
            source_family = _source_family(sid, meta, fetch_url, scope)
            recency = _recency(meta)
            asset_level_eligible = _asset_level_eligible(scope, authority_score)

            accepted = True
            rejection_reason = ""
            if ingestion_contract_status in {"identity_gate_required", "context_only_ingestion"} and scope in {
                "BENCHMARK_LEVEL",
                "JURISDICTION_LEVEL",
            }:
                accepted = False
                rejection_reason = "deferred_until_identity_gate"
            elif ingestion_contract_status == "invalid_for_ingestion" and scope != "ENTITY_LEVEL":
                accepted = False
                rejection_reason = "invalid_subject_for_asset_first_ingestion"
            elif scope != "ASSET_LEVEL" and asset_level_eligible:
                accepted = False
                rejection_reason = "scope_authority_inconsistency"

            entry = {
                "source_id": sid,
                "content_type": content_type,
                "metadata": meta,
                "has_content": bool(str(content or "").strip()),
                "needs_fetch": needs_fetch,
                "fetch_url": fetch_url,
                "fetch_type": meta.get("fetch_type", "http"),
                "scope": scope,
                "authority_score": authority_score,
                "source_family": source_family,
                "recency": recency,
                "accepted": accepted,
                "rejection_reason": rejection_reason,
                "asset_level_eligible": asset_level_eligible,
                "produced_by_motor": "motor_008",
            }

            registry[sid] = entry

            if accepted:
                accepted_source_ids.append(sid)
                if needs_fetch:
                    sources_requiring_fetch.append(sid)
                else:
                    sources_with_content.append(sid)
            else:
                rejected_source_ids.append(sid)

        return {
            "source_registry": registry,
            "sources_requiring_fetch": sources_requiring_fetch,
            "sources_with_content": sources_with_content,
            "accepted_source_ids": accepted_source_ids,
            "rejected_source_ids": rejected_source_ids,
            "total_sources": len(sources),
            "total_needing_fetch": len(sources_requiring_fetch),
            "subject": subject,
            "phase_contracts_count": len(contracts),
            "ingestion_contract_status": ingestion_contract_status,
        }
