from __future__ import annotations

import os
from typing import Any, Mapping

from .extraction_review import (
    build_extraction_promotion_registers,
    build_extraction_review_register,
)
from .extractor import build_extraction_seed_from_manifest
from .extractor import build_knowledge_extraction_record
from .licensed_playwright_fetch import fetch_licensed_document_with_persistent_session
from .provider_sessions import build_provider_session_plan
from .research_manifest import build_research_document_manifest


_LICENSED_BROWSER_FLAG = "ZLAB_ENABLE_LICENSED_RESEARCH_ACQUISITION"


def licensed_research_acquisition_enabled(env: Mapping[str, str] | None = None) -> bool:
    values = env if env is not None else os.environ
    return str(values.get(_LICENSED_BROWSER_FLAG, "")).strip().lower() in {"1", "true", "yes", "on"}


def plan_licensed_document_acquisition(
    *,
    url: str,
    retrieval_purpose: str,
    technical_scraping_allowed: bool,
    route_allowed: bool,
    session_label: str = "primary",
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    provider_plan = build_provider_session_plan(
        url=url,
        retrieval_purpose=retrieval_purpose,
        session_label=session_label,
        env=dict(env) if env is not None else None,
    )
    capability_enabled = licensed_research_acquisition_enabled(env)

    if not provider_plan.get("domain_allowed"):
        reason = "provider_not_supported"
        mode = "blocked"
        allowed = False
    elif not technical_scraping_allowed:
        reason = "technical_scraping_not_allowed"
        mode = "blocked"
        allowed = False
    elif not route_allowed:
        reason = "source_not_allowed_by_routing"
        mode = "blocked"
        allowed = False
    elif provider_plan.get("session_required") and not capability_enabled:
        reason = "licensed_research_capability_disabled"
        mode = "blocked"
        allowed = False
    elif provider_plan.get("session_required"):
        reason = "licensed_provider_session_required"
        mode = "playwright_persistent_session"
        allowed = True
    else:
        reason = "public_guidance_source"
        mode = "static_or_public_browser"
        allowed = True

    return {
        "allowed": allowed,
        "selection_reason": reason,
        "selected_mode": mode,
        "provider_session_plan": provider_plan,
        "provider_session_state": dict(provider_plan.get("session_state", {}) or {}),
        "licensed_research_capability_enabled": capability_enabled,
        "technical_scraping_allowed": technical_scraping_allowed,
        "route_allowed": route_allowed,
        "requested_url": str(url or "").strip(),
        "retrieval_purpose": str(retrieval_purpose or "").strip(),
    }


def execute_licensed_document_acquisition(
    *,
    url: str,
    retrieval_purpose: str,
    technical_scraping_allowed: bool,
    route_allowed: bool,
    metadata: dict[str, Any] | None = None,
    local_artifact_path: str = "",
    session_label: str = "primary",
    timeout_ms: int = 12_000,
    headless: bool = True,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    plan = plan_licensed_document_acquisition(
        url=url,
        retrieval_purpose=retrieval_purpose,
        technical_scraping_allowed=technical_scraping_allowed,
        route_allowed=route_allowed,
        session_label=session_label,
        env=env,
    )
    provider_session_plan = dict(plan.get("provider_session_plan", {}) or {})
    blocked_result = {
        "status": "blocked",
        "error": str(plan.get("selection_reason", "")).strip(),
        "requested_url": str(url or "").strip(),
        "final_url": str(url or "").strip(),
        "html": "",
        "visible_text": "",
        "selector_lineage": [],
        "acquisition_mode": str(plan.get("selected_mode", "")).strip() or "blocked",
    }
    if not plan.get("allowed"):
        manifest = build_research_document_manifest(
            provider_session_plan=provider_session_plan,
            acquisition_result=blocked_result,
            metadata=metadata,
            local_artifact_path=local_artifact_path,
        )
        return {
            "acquisition_plan": plan,
            "acquisition_result": blocked_result,
            "research_document_manifest": manifest,
            "extraction_seed": build_extraction_seed_from_manifest(
                research_document_manifest=manifest,
                retrieval_purpose=str(retrieval_purpose or "").strip(),
            ),
        }
    if plan.get("selected_mode") == "playwright_persistent_session":
        acquisition_result = fetch_licensed_document_with_persistent_session(
            url=url,
            provider_session_plan=provider_session_plan,
            timeout_ms=timeout_ms,
            headless=headless,
        )
    else:
        acquisition_result = {
            "status": "not_implemented",
            "error": "non_playwright_licensed_mode_not_implemented",
            "requested_url": str(url or "").strip(),
            "final_url": str(url or "").strip(),
            "html": "",
            "visible_text": "",
            "selector_lineage": [],
            "acquisition_mode": str(plan.get("selected_mode", "")).strip(),
        }
    manifest = build_research_document_manifest(
        provider_session_plan=provider_session_plan,
        acquisition_result=acquisition_result,
        metadata=metadata,
        local_artifact_path=local_artifact_path,
    )
    extraction_seed = build_extraction_seed_from_manifest(
        research_document_manifest=manifest,
        retrieval_purpose=str(retrieval_purpose or "").strip(),
    )
    return {
        "acquisition_plan": plan,
        "acquisition_result": acquisition_result,
        "research_document_manifest": manifest,
        "extraction_seed": extraction_seed,
    }


def ingest_licensed_research_document(
    *,
    url: str,
    retrieval_purpose: str,
    technical_scraping_allowed: bool,
    route_allowed: bool,
    metadata: dict[str, Any] | None = None,
    local_artifact_path: str = "",
    extraction_payload: dict[str, Any] | None = None,
    registry_bundle: dict[str, Any] | None = None,
    session_label: str = "primary",
    timeout_ms: int = 12_000,
    headless: bool = True,
    env: Mapping[str, str] | None = None,
) -> dict[str, Any]:
    acquisition_package = execute_licensed_document_acquisition(
        url=url,
        retrieval_purpose=retrieval_purpose,
        technical_scraping_allowed=technical_scraping_allowed,
        route_allowed=route_allowed,
        metadata=metadata,
        local_artifact_path=local_artifact_path,
        session_label=session_label,
        timeout_ms=timeout_ms,
        headless=headless,
        env=env,
    )
    if not extraction_payload:
        return acquisition_package
    extraction_record = build_knowledge_extraction_record(
        research_document_manifest=dict(acquisition_package.get("research_document_manifest", {}) or {}),
        extraction_payload=dict(extraction_payload or {}),
        registry_bundle=registry_bundle,
    )
    extraction_review_register = build_extraction_review_register([extraction_record])
    promotion_registers = build_extraction_promotion_registers(
        [extraction_record],
        registry_bundle=registry_bundle,
    )
    return {
        **acquisition_package,
        "knowledge_extraction_record": extraction_record,
        "extraction_review_register": extraction_review_register,
        **promotion_registers,
    }
