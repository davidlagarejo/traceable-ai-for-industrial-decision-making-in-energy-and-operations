from __future__ import annotations

from typing import Any, Mapping

from .provider_sessions import provider_spec


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


_SOURCE_FAMILY_CONTRACTS: dict[str, dict[str, Any]] = {
    "licensed_research_discovery": {
        "display_name": "Licensed discovery",
        "target_document_count": 10,
        "target_knowledge_atom_count": 6,
        "importance": "high",
        "provider_targets": ["scopus"],
        "capture_mode": "metadata_and_reference_capture",
        "admissible_capture_fields": ["doi", "title", "abstract", "keywords", "source_url"],
        "atomization_priority": "structural_prior_expansion",
        "search_focus": "Search for more candidate papers, metadata clusters, and DOI/title pivots.",
        "preferred_query_families": ["general_structural_prior_expansion"],
    },
    "licensed_research_fulltext": {
        "display_name": "Licensed full text",
        "target_document_count": 4,
        "target_knowledge_atom_count": 8,
        "importance": "high",
        "provider_targets": ["ieee", "springer", "elsevier"],
        "capture_mode": "visible_excerpt_or_fulltext_capture",
        "admissible_capture_fields": ["source_url", "reference_excerpt", "notes"],
        "atomization_priority": "deep_operational_and_financial_atoms",
        "search_focus": "Read more full text or visible reference excerpts to extract deeper structural atoms.",
        "preferred_query_families": ["general_structural_prior_expansion"],
    },
    "public_technical_guidance": {
        "display_name": "Public technical guidance",
        "target_document_count": 3,
        "target_knowledge_atom_count": 3,
        "importance": "medium",
        "provider_targets": ["ashrae", "doe", "epa"],
        "capture_mode": "guidance_reference_capture",
        "admissible_capture_fields": ["source_url", "title", "reference_excerpt", "notes"],
        "atomization_priority": "governance_and_guidance_atoms",
        "search_focus": "Add handbook, utility, DOE/EPA, or specialist technical guidance to widen the prior base.",
        "preferred_query_families": ["fair_comparison_normalization", "sensor_minimality", "digital_twin_prematurity"],
    },
    "licensed_research_local_artifact": {
        "display_name": "Local licensed artifact",
        "target_document_count": 2,
        "target_knowledge_atom_count": 4,
        "importance": "high",
        "provider_targets": ["manual_local"],
        "capture_mode": "local_pdf_or_excerpt_ingestion",
        "admissible_capture_fields": ["document_ref", "metadata_payload", "reference_excerpt"],
        "atomization_priority": "fulltext_extraction_from_local_artifacts",
        "search_focus": "Stage local licensed PDFs or curated excerpts for extraction.",
        "preferred_query_families": ["general_structural_prior_expansion"],
    },
    "specialist_web_case_signal": {
        "display_name": "Specialist web case signal",
        "target_document_count": 4,
        "target_knowledge_atom_count": 2,
        "importance": "medium",
        "provider_targets": ["manual"],
        "capture_mode": "manual_reference_capture",
        "admissible_capture_fields": ["source_url", "title_or_snippet", "notes"],
        "atomization_priority": "weak_signal_case_patterns",
        "search_focus": "Collect specialist web and practitioner case signals without promoting them to local truth.",
        "preferred_query_families": ["general_structural_prior_expansion", "maintenance_hidden_driver"],
    },
    "utility_tariff_billing_guidance": {
        "display_name": "Utility / tariff / billing guidance",
        "target_document_count": 3,
        "target_knowledge_atom_count": 4,
        "importance": "high",
        "provider_targets": ["manual", "doe", "epa"],
        "capture_mode": "manual_reference_capture",
        "admissible_capture_fields": ["source_url", "title_or_snippet", "tariff_terms", "notes"],
        "atomization_priority": "tariff_and_billing_translation",
        "search_focus": "Collect utility tariff sheets, billing guides, demand-charge explanations, and rate-schedule interpretations.",
        "preferred_query_families": ["tariff_demand_peak", "reactive_power_quality"],
    },
    "oem_handbook_technical_manuals": {
        "display_name": "OEM / handbook / technical manuals",
        "target_document_count": 3,
        "target_knowledge_atom_count": 4,
        "importance": "high",
        "provider_targets": ["manual"],
        "capture_mode": "manual_reference_capture",
        "admissible_capture_fields": ["source_url", "title_or_snippet", "equipment_family", "notes"],
        "atomization_priority": "process_and_maintenance_logic",
        "search_focus": "Collect OEM manuals, technical handbooks, datasheets, and equipment operating guidance relevant to the dominant variables.",
        "preferred_query_families": ["maintenance_hidden_driver", "controls_schedule_drift", "compressed_air_loss"],
    },
    "regulatory_code_compliance_guidance": {
        "display_name": "Regulatory / code / compliance guidance",
        "target_document_count": 3,
        "target_knowledge_atom_count": 3,
        "importance": "high",
        "provider_targets": ["manual", "epa"],
        "capture_mode": "manual_reference_capture",
        "admissible_capture_fields": ["source_url", "title_or_snippet", "jurisdiction", "notes"],
        "atomization_priority": "regulatory_physical_signal_and_claim_limits",
        "search_focus": "Collect official code text, compliance guidance, and jurisdiction-specific rule summaries that constrain physical or financial interpretation.",
        "preferred_query_families": ["sensor_minimality", "digital_twin_prematurity", "fair_comparison_normalization"],
    },
}

_QUERY_FAMILY_TEMPLATE_LIBRARY: dict[str, dict[str, Any]] = {
    "tariff_demand_peak": {
        "seed_terms": ["demand charge", "peak demand", "load shifting", "charging schedule"],
        "evidence_targets": ["utility tariff", "billing demand", "interval load profile"],
        "search_intent": "Find structural evidence that timing and tariff structure dominate total annual energy interpretation.",
    },
    "owner_operator_boundary": {
        "seed_terms": ["owner operator boundary", "tenant control", "lease utility responsibility", "metering responsibility"],
        "evidence_targets": ["lease matrix", "meter map", "utility payment responsibility"],
        "search_intent": "Find contractual and operational patterns where the value capturer is not the actor funding the improvement.",
    },
    "fair_comparison_normalization": {
        "seed_terms": ["energy benchmark normalization", "peer comparison validity", "denominator error", "service level intensity"],
        "evidence_targets": ["normalization variables", "peer set requirements", "invalid comparison flags"],
        "search_intent": "Find evidence about when peer comparison becomes invalid without the right normalization dimensions.",
    },
    "dock_infiltration_interface": {
        "seed_terms": ["dock door infiltration", "logistics interface losses", "door cycle thermal loss", "dock seal performance"],
        "evidence_targets": ["door cycles", "dock seal condition", "temperature zones"],
        "search_intent": "Find structural evidence that logistics-interface losses can dominate HVAC or refrigeration narratives.",
    },
    "maintenance_hidden_driver": {
        "seed_terms": ["maintenance maturity", "hidden maintenance driver", "reliability economics", "downtime exposure"],
        "evidence_targets": ["maintenance program", "downtime history", "reliability degradation"],
        "search_intent": "Find evidence that maintenance and reliability dominate economics before generic efficiency measures do.",
    },
    "controls_schedule_drift": {
        "seed_terms": ["hvac schedule drift", "after-hours operation", "setback failure", "controls override"],
        "evidence_targets": ["schedule map", "after-hours runtime", "controls sequence"],
        "search_intent": "Find evidence that schedule and controls drift explain load before equipment retrofit is justified.",
    },
    "compressed_air_loss": {
        "seed_terms": ["compressed air leakage", "air system demand", "compressor part-load", "compressed air loss"],
        "evidence_targets": ["leak rate", "compressor controls", "pressure profile"],
        "search_intent": "Find hidden-loss evidence around compressed air plausibility and discriminator variables.",
    },
    "sensor_minimality": {
        "seed_terms": ["measurement minimality", "sensor prematurity", "minimum evidence first", "instrumentation waste"],
        "evidence_targets": ["minimum evidence", "decision objective", "measurement objective"],
        "search_intent": "Find evidence for measuring only what is necessary before escalating instrumentation.",
    },
    "digital_twin_prematurity": {
        "seed_terms": ["digital twin prematurity", "model scope", "dominant variable mapping", "model purpose"],
        "evidence_targets": ["boundary definition", "model objective", "topology completeness"],
        "search_intent": "Find evidence that detailed modeling is premature until drivers and boundaries are resolved.",
    },
    "reactive_power_quality": {
        "seed_terms": ["reactive power", "power factor", "power quality penalty", "harmonic compensation"],
        "evidence_targets": ["power factor", "kvarh", "compensation equipment"],
        "search_intent": "Find evidence that power quality can be a hidden cost and capacity driver.",
    },
    "general_structural_prior_expansion": {
        "seed_terms": ["structural prior", "operational loss pattern", "industrial case evidence", "technical handbook"],
        "evidence_targets": ["structural pattern", "minimum evidence", "falsification condition"],
        "search_intent": "Expand the structural prior base when the combination is still thinly supported.",
    },
}


def _normalize_target_rows(mode: str = "standard") -> list[dict[str, Any]]:
    _ = mode
    return [
        {
            "source_family": source_family,
            **dict(contract),
        }
        for source_family, contract in _SOURCE_FAMILY_CONTRACTS.items()
    ]


def _default_provider_targets_for_source_family(source_family: str) -> list[str]:
    contract = dict(_SOURCE_FAMILY_CONTRACTS.get(_text(source_family), {}) or {})
    return [_text(item) for item in list(contract.get("provider_targets", []) or []) if _text(item)]


def _source_family_contract(source_family: str) -> dict[str, Any]:
    return dict(_SOURCE_FAMILY_CONTRACTS.get(_text(source_family), {}) or {})


def _provider_display_name(provider_key: str) -> str:
    spec = provider_spec(provider_key)
    return _text(spec.get("display_name")) or _text(provider_key).replace("_", " ").title()


def _source_family_from_provider(
    provider_key: str,
    *,
    provider_session_register: list[dict[str, Any]] | None = None,
) -> str:
    normalized_provider = _text(provider_key)
    for row in list(provider_session_register or []):
        if _text(row.get("provider_key")) == normalized_provider:
            return _text(row.get("source_family"))
    if normalized_provider == "manual":
        return "specialist_web_case_signal"
    if normalized_provider == "manual_local":
        return "licensed_research_local_artifact"
    return ""


def _declared_source_family(
    row: Mapping[str, Any] | None,
    *,
    provider_session_register: list[dict[str, Any]] | None = None,
) -> str:
    data = dict(row or {})
    metadata_payload = dict(data.get("metadata_payload", {}) or {})
    manifest = dict(data.get("manifest", {}) or {})
    research_document_manifest = dict(data.get("research_document_manifest", {}) or {})
    provenance_manifest = dict(data.get("provenance_manifest", {}) or {})
    acquisition_result = dict(data.get("acquisition_result", {}) or {})
    for value in [
        data.get("source_family"),
        metadata_payload.get("source_family"),
        manifest.get("source_family"),
        research_document_manifest.get("source_family"),
        provenance_manifest.get("source_family"),
        acquisition_result.get("source_family"),
    ]:
        normalized = _text(value)
        if normalized:
            return normalized
    return _source_family_from_provider(
        _text(data.get("provider_key")),
        provider_session_register=provider_session_register,
    )


def build_source_family_coverage_register(
    *,
    provider_session_register: list[dict[str, Any]] | None,
    discovery_candidate_review_register: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None,
    extraction_records: list[dict[str, Any]] | None,
    knowledge_atom_register: list[dict[str, Any]] | None,
    mode: str = "standard",
) -> list[dict[str, Any]]:
    target_rows = _normalize_target_rows(mode=mode)
    targets_by_family = {
        _text(row.get("source_family")): dict(row)
        for row in target_rows
        if _text(row.get("source_family"))
    }
    coverage_by_family: dict[str, dict[str, Any]] = {}

    def _bucket(source_family: str) -> dict[str, Any]:
        family = _text(source_family)
        target = dict(targets_by_family.get(family, {}) or {})
        return coverage_by_family.setdefault(
            family,
            {
                "source_family": family,
                "display_name": _text(target.get("display_name")) or family.replace("_", " ").title(),
                "target_document_count": int(target.get("target_document_count", 0) or 0),
                "target_knowledge_atom_count": int(target.get("target_knowledge_atom_count", 0) or 0),
                "importance": _text(target.get("importance")) or "medium",
                "capture_mode": _text(target.get("capture_mode")) or "manual_reference_capture",
                "admissible_capture_fields": list(target.get("admissible_capture_fields", []) or []),
                "atomization_priority": _text(target.get("atomization_priority")) or "general_structural_prior_expansion",
                "search_focus": _text(target.get("search_focus")),
                "preferred_query_families": list(target.get("preferred_query_families", []) or []),
                "available_provider_keys": set(),
                "touched_provider_keys": set(),
                "document_refs": set(),
                "reference_ids": set(),
                "candidate_ids": set(),
                "knowledge_atom_ids": set(),
            },
        )

    for row in list(provider_session_register or []):
        family = _text(row.get("source_family"))
        if not family:
            continue
        _bucket(family)["available_provider_keys"].add(_text(row.get("provider_key")))

    for row in list(discovery_candidate_review_register or []):
        provider_key = _text(row.get("provider_key"))
        family = _declared_source_family(row, provider_session_register=provider_session_register)
        if not family:
            continue
        bucket = _bucket(family)
        bucket["candidate_ids"].add(_text(row.get("candidate_id")))
        if provider_key:
            bucket["touched_provider_keys"].add(provider_key)

    for row in list(article_reference_register or []):
        provider_key = _text(row.get("provider_key"))
        family = _declared_source_family(row, provider_session_register=provider_session_register)
        if not family:
            continue
        bucket = _bucket(family)
        bucket["reference_ids"].add(_text(row.get("candidate_id")))
        if provider_key:
            bucket["touched_provider_keys"].add(provider_key)
        if _text(row.get("source_url")):
            bucket["document_refs"].add(_text(row.get("source_url")))

    for row in list(extraction_records or []):
        provider_key = _text(row.get("provider_key"))
        family = _declared_source_family(row, provider_session_register=provider_session_register)
        if not family:
            continue
        bucket = _bucket(family)
        if provider_key:
            bucket["touched_provider_keys"].add(provider_key)
        if _text(row.get("document_ref")):
            bucket["document_refs"].add(_text(row.get("document_ref")))

    for row in list(knowledge_atom_register or []):
        provider_key = _text(row.get("provider_key"))
        family = _declared_source_family(row, provider_session_register=provider_session_register)
        if not family:
            continue
        bucket = _bucket(family)
        if provider_key:
            bucket["touched_provider_keys"].add(provider_key)
        if _text(row.get("document_ref")):
            bucket["document_refs"].add(_text(row.get("document_ref")))
        if _text(row.get("atom_id")):
            bucket["knowledge_atom_ids"].add(_text(row.get("atom_id")))

    for family, target in targets_by_family.items():
        _bucket(family)

    rows: list[dict[str, Any]] = []
    for row in coverage_by_family.values():
        document_count = len(set(row.get("document_refs", set()) or set()))
        knowledge_atom_count = len(set(row.get("knowledge_atom_ids", set()) or set()))
        available_provider_count = len(set(row.get("available_provider_keys", set()) or set()))
        touched_provider_count = len(set(row.get("touched_provider_keys", set()) or set()))
        target_document_count = int(row.get("target_document_count", 0) or 0)
        target_atom_count = int(row.get("target_knowledge_atom_count", 0) or 0)
        coverage_state = "untouched"
        if document_count >= target_document_count and knowledge_atom_count >= target_atom_count and target_document_count > 0:
            coverage_state = "strong"
        elif document_count > 0 or knowledge_atom_count > 0 or touched_provider_count > 0:
            coverage_state = "thin"
        elif available_provider_count == 0:
            coverage_state = "not_available"
        rows.append(
            {
                "source_family": _text(row.get("source_family")),
                "display_name": _text(row.get("display_name")),
                "target_document_count": target_document_count,
                "target_knowledge_atom_count": target_atom_count,
                "importance": _text(row.get("importance")) or "medium",
                "capture_mode": _text(row.get("capture_mode")) or "manual_reference_capture",
                "admissible_capture_fields": list(row.get("admissible_capture_fields", []) or []),
                "atomization_priority": _text(row.get("atomization_priority")) or "general_structural_prior_expansion",
                "search_focus": _text(row.get("search_focus")),
                "preferred_query_families": list(row.get("preferred_query_families", []) or []),
                "available_provider_count": available_provider_count,
                "available_provider_keys": sorted(set(row.get("available_provider_keys", set()) or set())),
                "touched_provider_count": touched_provider_count,
                "touched_provider_keys": sorted(set(row.get("touched_provider_keys", set()) or set())),
                "document_count": document_count,
                "reference_count": len(set(row.get("reference_ids", set()) or set())),
                "candidate_count": len(set(row.get("candidate_ids", set()) or set())),
                "knowledge_atom_count": knowledge_atom_count,
                "coverage_state": coverage_state,
            }
        )
    rows.sort(key=lambda row: (_text(row.get("source_family")), _text(row.get("display_name"))))
    return rows


def build_research_campaign_record(
    *,
    run_id: str,
    asset_context_vector: Mapping[str, Any] | None,
    source_family_coverage_register: list[dict[str, Any]] | None,
    source_coverage_summary: Mapping[str, Any] | None,
    combination_search_gap_record: Mapping[str, Any] | None,
    mode: str = "standard",
) -> dict[str, Any]:
    asset_vector = dict(asset_context_vector or {})
    coverage_rows = list(source_family_coverage_register or [])
    source_coverage = dict(source_coverage_summary or {})
    gap_record = dict(combination_search_gap_record or {})

    target_family_count = len(coverage_rows)
    strong_family_count = sum(1 for row in coverage_rows if _text(row.get("coverage_state")) == "strong")
    touched_family_count = sum(
        1 for row in coverage_rows if _text(row.get("coverage_state")) in {"thin", "strong"}
    )
    missing_family_count = sum(1 for row in coverage_rows if _text(row.get("coverage_state")) in {"untouched", "not_available"})
    high_importance_rows = [row for row in coverage_rows if _text(row.get("importance")) == "high"]
    high_importance_touched_count = sum(
        1 for row in high_importance_rows if _text(row.get("coverage_state")) in {"thin", "strong"}
    )
    high_importance_strong_count = sum(
        1 for row in high_importance_rows if _text(row.get("coverage_state")) == "strong"
    )

    campaign_status = "coverage_building"
    if _text(gap_record.get("search_status")) == "complete_enough_for_review":
        campaign_status = "review_ready"
    elif _text(gap_record.get("search_status")) == "thin_but_reviewable":
        campaign_status = "reviewable_but_expand_sources"
    elif touched_family_count == 0:
        campaign_status = "not_started"

    top_next_actions: list[str] = []
    for row in coverage_rows:
        if _text(row.get("coverage_state")) in {"untouched", "not_available"}:
            top_next_actions.append(f"Add coverage for {_text(row.get('display_name')) or _text(row.get('source_family'))}.")
    for action in list(gap_record.get("recommended_actions", []) or []):
        action_text = _text(action)
        if action_text and action_text not in top_next_actions:
            top_next_actions.append(action_text)

    return {
        "run_id": _text(run_id),
        "mode": _text(mode) or "standard",
        "asset_family": _text(asset_vector.get("asset_family")) or "unknown_asset_family",
        "context_signature": _text(asset_vector.get("context_signature")),
        "target_source_family_count": target_family_count,
        "strong_source_family_count": strong_family_count,
        "touched_source_family_count": touched_family_count,
        "missing_source_family_count": missing_family_count,
        "high_importance_source_family_count": len(high_importance_rows),
        "high_importance_touched_source_family_count": high_importance_touched_count,
        "high_importance_strong_source_family_count": high_importance_strong_count,
        "knowledge_atom_count": int(source_coverage.get("knowledge_atom_count", 0) or 0),
        "document_count": int(source_coverage.get("document_count", 0) or 0),
        "provider_count": int(source_coverage.get("provider_count", 0) or 0),
        "latent_candidate_count": int(gap_record.get("latent_candidate_count", 0) or 0),
        "admissible_candidate_count": int(gap_record.get("admissible_candidate_count", 0) or 0),
        "coverage_strength": _text(source_coverage.get("coverage_strength")) or "empty",
        "search_status": _text(gap_record.get("search_status")) or "unknown",
        "campaign_status": campaign_status,
        "top_next_actions": top_next_actions[:6],
        "summary": (
            f"{_text(asset_vector.get('asset_family')) or 'asset'} campaign in {_text(mode) or 'standard'} mode: "
            f"{touched_family_count}/{target_family_count} source families touched, "
            f"{int(gap_record.get('latent_candidate_count', 0) or 0)} latent candidates, "
            f"coverage {_text(source_coverage.get('coverage_strength')) or 'empty'}."
        ),
    }


def build_source_family_trigger_plan(
    *,
    source_family_row: Mapping[str, Any],
    research_campaign_record: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    row = dict(source_family_row or {})
    campaign = dict(research_campaign_record or {})
    source_family = _text(row.get("source_family"))
    display_name = _text(row.get("display_name")) or source_family.replace("_", " ").title()
    current_docs = int(row.get("document_count", 0) or 0)
    target_docs = int(row.get("target_document_count", 0) or 0)
    current_atoms = int(row.get("knowledge_atom_count", 0) or 0)
    target_atoms = int(row.get("target_knowledge_atom_count", 0) or 0)
    provider_keys = list(row.get("available_provider_keys", []) or [])
    touched_provider_keys = list(row.get("touched_provider_keys", []) or [])
    if not provider_keys:
        provider_keys = list(touched_provider_keys)
    if not provider_keys:
        provider_keys = _default_provider_targets_for_source_family(source_family)
    contract = _source_family_contract(source_family)
    search_focus = _text(row.get("search_focus")) or _text(contract.get("search_focus")) or (
        "Expand this source family to increase structural coverage and latent-combination depth."
    )
    return {
        "source_family": source_family,
        "display_name": display_name,
        "trigger_type": "deeper_search",
        "campaign_mode": _text(campaign.get("mode")) or "standard",
        "campaign_status": _text(campaign.get("campaign_status")) or "coverage_building",
        "recommended_provider_keys": provider_keys,
        "current_document_count": current_docs,
        "target_document_count": target_docs,
        "current_knowledge_atom_count": current_atoms,
        "target_knowledge_atom_count": target_atoms,
        "target_document_delta": max(target_docs - current_docs, 1) if target_docs > 0 else 1,
        "target_knowledge_atom_delta": max(target_atoms - current_atoms, 1) if target_atoms > 0 else 1,
        "search_focus": search_focus,
        "capture_mode": _text(row.get("capture_mode")) or _text(contract.get("capture_mode")) or "manual_reference_capture",
        "admissible_capture_fields": list(row.get("admissible_capture_fields", []) or contract.get("admissible_capture_fields", []) or []),
        "atomization_priority": _text(row.get("atomization_priority")) or _text(contract.get("atomization_priority")) or "general_structural_prior_expansion",
        "preferred_query_families": list(row.get("preferred_query_families", []) or contract.get("preferred_query_families", []) or []),
        "reason": (
            f"{display_name} is still {_text(row.get('coverage_state')) or 'thin'}; "
            f"campaign {_text(campaign.get('campaign_status')) or 'coverage_building'} still needs more coverage here."
        ),
    }


def build_research_campaign_trigger_register(
    *,
    source_family_coverage_register: list[dict[str, Any]] | None,
    research_campaign_record: Mapping[str, Any] | None = None,
    stored_trigger_records: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    coverage_rows = list(source_family_coverage_register or [])
    campaign = dict(research_campaign_record or {})
    stored_by_family = {
        _text(row.get("source_family")): dict(row)
        for row in list(stored_trigger_records or [])
        if _text(row.get("source_family"))
    }
    rows: list[dict[str, Any]] = []
    seen_families: set[str] = set()

    for coverage_row in coverage_rows:
        source_family = _text(coverage_row.get("source_family"))
        if not source_family:
            continue
        seen_families.add(source_family)
        plan = build_source_family_trigger_plan(
            source_family_row=coverage_row,
            research_campaign_record=campaign,
        )
        stored = dict(stored_by_family.get(source_family, {}) or {})
        recommended_provider_keys = [
            _text(item)
            for item in list(stored.get("recommended_provider_keys", []) or plan.get("recommended_provider_keys", []) or [])
            if _text(item)
        ]
        rows.append(
            {
                **plan,
                "coverage_state": _text(coverage_row.get("coverage_state")) or "untouched",
                "importance": _text(coverage_row.get("importance")) or "medium",
                "available_provider_keys": [
                    _text(item)
                    for item in list(coverage_row.get("available_provider_keys", []) or [])
                    if _text(item)
                ],
                "touched_provider_keys": [
                    _text(item)
                    for item in list(coverage_row.get("touched_provider_keys", []) or [])
                    if _text(item)
                ],
                "document_count": int(coverage_row.get("document_count", 0) or 0),
                "reference_count": int(coverage_row.get("reference_count", 0) or 0),
                "candidate_count": int(coverage_row.get("candidate_count", 0) or 0),
                "knowledge_atom_count": int(coverage_row.get("knowledge_atom_count", 0) or 0),
                "status": _text(stored.get("status")) or "not_queued",
                "queued": bool(stored),
                "queued_at": _text(stored.get("queued_at")),
                "updated_at": _text(stored.get("updated_at")),
                "reason": _text(stored.get("reason")) or _text(plan.get("reason")),
                "search_focus": _text(stored.get("search_focus")) or _text(plan.get("search_focus")),
                "recommended_provider_keys": recommended_provider_keys,
                "target_document_delta": int(
                    stored.get("target_document_delta", plan.get("target_document_delta", 0)) or 0
                ),
                "target_knowledge_atom_delta": int(
                    stored.get("target_knowledge_atom_delta", plan.get("target_knowledge_atom_delta", 0)) or 0
                ),
                "capture_mode": _text(stored.get("capture_mode")) or _text(plan.get("capture_mode")),
                "admissible_capture_fields": list(stored.get("admissible_capture_fields", []) or plan.get("admissible_capture_fields", []) or []),
                "atomization_priority": _text(stored.get("atomization_priority")) or _text(plan.get("atomization_priority")),
                "preferred_query_families": list(stored.get("preferred_query_families", []) or plan.get("preferred_query_families", []) or []),
                "trigger_source": "persisted" if stored else "suggested",
            }
        )

    for source_family, stored in stored_by_family.items():
        if source_family in seen_families:
            continue
        rows.append(
            {
                "source_family": source_family,
                "display_name": _text(stored.get("display_name")) or source_family.replace("_", " ").title(),
                "trigger_type": _text(stored.get("trigger_type")) or "deeper_search",
                "campaign_mode": _text(campaign.get("mode")) or "standard",
                "campaign_status": _text(campaign.get("campaign_status")) or "coverage_building",
                "recommended_provider_keys": [
                    _text(item)
                    for item in list(stored.get("recommended_provider_keys", []) or [])
                    if _text(item)
                ],
                "current_document_count": int(stored.get("current_document_count", 0) or 0),
                "target_document_count": int(stored.get("target_document_count", 0) or 0),
                "current_knowledge_atom_count": int(stored.get("current_knowledge_atom_count", 0) or 0),
                "target_knowledge_atom_count": int(stored.get("target_knowledge_atom_count", 0) or 0),
                "target_document_delta": int(stored.get("target_document_delta", 0) or 0),
                "target_knowledge_atom_delta": int(stored.get("target_knowledge_atom_delta", 0) or 0),
                "search_focus": _text(stored.get("search_focus")),
                "capture_mode": _text(stored.get("capture_mode")) or "manual_reference_capture",
                "admissible_capture_fields": list(stored.get("admissible_capture_fields", []) or []),
                "atomization_priority": _text(stored.get("atomization_priority")),
                "preferred_query_families": list(stored.get("preferred_query_families", []) or []),
                "reason": _text(stored.get("reason")),
                "coverage_state": "unknown",
                "importance": "medium",
                "available_provider_keys": [],
                "touched_provider_keys": [],
                "document_count": int(stored.get("current_document_count", 0) or 0),
                "reference_count": 0,
                "candidate_count": 0,
                "knowledge_atom_count": int(stored.get("current_knowledge_atom_count", 0) or 0),
                "status": _text(stored.get("status")) or "queued",
                "queued": True,
                "queued_at": _text(stored.get("queued_at")),
                "updated_at": _text(stored.get("updated_at")),
                "trigger_source": "orphaned",
            }
        )

    rows.sort(
        key=lambda row: (
            _text(row.get("status")) != "queued",
            _text(row.get("importance")) != "high",
            _text(row.get("source_family")),
        )
    )
    return rows


def build_combination_follow_on_research_register(
    *,
    combination_review_sequence_register: list[dict[str, Any]] | None,
    source_family_coverage_register: list[dict[str, Any]] | None,
    research_campaign_record: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    coverage_rows = list(source_family_coverage_register or [])
    coverage_by_family = {
        _text(row.get("source_family")): dict(row)
        for row in coverage_rows
        if _text(row.get("source_family"))
    }
    campaign = dict(research_campaign_record or {})
    rows: list[dict[str, Any]] = []

    for combination_row in list(combination_review_sequence_register or []):
        combination_id = _text(combination_row.get("combination_id"))
        if not combination_id:
            continue
        text_blob = " ".join(
            [
                _text(combination_row.get("combination_name")),
                _text(combination_row.get("combined_hypothesis")),
                _text(combination_row.get("strategic_risk")),
                _text(combination_row.get("allowed_language")),
                " ".join([_text(item) for item in list(combination_row.get("pattern_layers", []) or []) if _text(item)]),
                " ".join([_text(item) for item in list(combination_row.get("pattern_ids", []) or []) if _text(item)]),
                " ".join([_text(item) for item in list(combination_row.get("minimum_evidence", []) or []) if _text(item)]),
            ]
        ).lower()
        knowledge_atom_count = int(combination_row.get("knowledge_atom_count", 0) or 0)
        document_refs = [_text(item) for item in list(combination_row.get("supporting_document_refs", []) or []) if _text(item)]
        pattern_layers = {_text(item).lower() for item in list(combination_row.get("pattern_layers", []) or []) if _text(item)}

        recommended_source_families: list[str] = []
        reasoning_flags: list[str] = []

        if knowledge_atom_count < 2 or not document_refs:
            recommended_source_families.append("licensed_research_discovery")
            reasoning_flags.append("thin_combination_support")

        if (
            {"loss_pattern", "financial_translation", "maintenance_reality_pattern", "process_logic"}.intersection(pattern_layers)
            or any(keyword in text_blob for keyword in ["tariff", "demand", "reactive", "dock", "mhe", "charging", "compressed air", "steam", "boiler", "chiller", "maintenance", "process", "hvac"])
        ):
            recommended_source_families.append("licensed_research_fulltext")
            reasoning_flags.append("deep_operational_support_needed")

        if (
            {"fair_comparison_rule", "measurement_minimality_rule", "regulatory_physical_signal", "culture_execution_proxy"}.intersection(pattern_layers)
            or any(keyword in text_blob for keyword in ["benchmark", "comparison", "boundary", "owner", "operator", "sensor", "digital twin", "fair comparison", "regulatory", "measurement"])
        ):
            recommended_source_families.append("public_technical_guidance")
            reasoning_flags.append("governance_and_guidance_support_needed")

        if not recommended_source_families:
            recommended_source_families.append("licensed_research_fulltext")
            reasoning_flags.append("default_fulltext_expansion")

        deduped_families: list[str] = []
        for source_family in recommended_source_families:
            normalized_family = _text(source_family)
            if normalized_family and normalized_family not in deduped_families:
                deduped_families.append(normalized_family)

        trigger_rows: list[dict[str, Any]] = []
        for source_family in deduped_families:
            source_family_row = dict(coverage_by_family.get(source_family, {}) or {"source_family": source_family})
            trigger_plan = build_source_family_trigger_plan(
                source_family_row=source_family_row,
                research_campaign_record=campaign,
            )
            trigger_rows.append(
                {
                    **trigger_plan,
                    "reason": (
                        f"Combination {combination_id} needs deeper follow-on research through "
                        f"{_text(trigger_plan.get('display_name')) or source_family.replace('_', ' ')}."
                    ),
                    "combination_id": combination_id,
                    "combination_name": _text(combination_row.get("combination_name")) or combination_id,
                }
            )

        rows.append(
            {
                "combination_id": combination_id,
                "combination_name": _text(combination_row.get("combination_name")) or combination_id,
                "operator_decision": _text(combination_row.get("operator_decision")) or "candidate",
                "review_origin": _text(combination_row.get("review_origin")) or "registered",
                "recommended_source_families": deduped_families,
                "reasoning_flags": reasoning_flags,
                "trigger_rows": trigger_rows,
            }
        )

    rows.sort(key=lambda row: (_text(row.get("combination_name")), _text(row.get("combination_id"))))
    return rows


def _infer_query_families(combination_row: Mapping[str, Any]) -> list[str]:
    text_blob = " ".join(
        [
            _text(combination_row.get("combination_name")),
            _text(combination_row.get("combined_hypothesis")),
            _text(combination_row.get("strategic_risk")),
            " ".join([_text(item) for item in list(combination_row.get("pattern_ids", []) or []) if _text(item)]),
            " ".join([_text(item) for item in list(combination_row.get("minimum_evidence", []) or []) if _text(item)]),
        ]
    ).lower()
    query_families: list[str] = []

    def _add(query_family: str) -> None:
        normalized = _text(query_family)
        if normalized and normalized not in query_families:
            query_families.append(normalized)

    keyword_map = {
        "tariff_demand_peak": ["tariff", "demand", "peak", "mhe", "charging", "power factor", "reactive"],
        "owner_operator_boundary": ["boundary", "owner", "operator", "lease", "meter map", "tenant"],
        "fair_comparison_normalization": ["benchmark", "comparison", "normalization", "denominator", "peer"],
        "dock_infiltration_interface": ["dock", "infiltration", "door", "seal", "cold-chain", "refrigeration interface"],
        "maintenance_hidden_driver": ["maintenance", "lubrication", "downtime", "maturity", "reliability"],
        "controls_schedule_drift": ["schedule", "hvac", "controls", "after-hours", "setback"],
        "compressed_air_loss": ["compressed air", "compressor", "leak"],
        "sensor_minimality": ["sensor", "instrumentation", "measurement", "minimum evidence"],
        "digital_twin_prematurity": ["digital twin", "model", "topology", "dominant variable"],
        "reactive_power_quality": ["reactive", "power quality", "power factor"],
    }
    for query_family, keywords in keyword_map.items():
        if any(keyword in text_blob for keyword in keywords):
            _add(query_family)
    if not query_families:
        _add("general_structural_prior_expansion")
    return query_families


def _infer_asset_focus_terms(combination_row: Mapping[str, Any]) -> list[str]:
    text_blob = " ".join(
        [
            _text(combination_row.get("combination_name")),
            _text(combination_row.get("combined_hypothesis")),
            _text(combination_row.get("strategic_risk")),
            " ".join([_text(item) for item in list(combination_row.get("pattern_ids", []) or []) if _text(item)]),
        ]
    ).lower()
    focus_terms: list[str] = []

    def _add(*terms: str) -> None:
        for term in terms:
            normalized = _text(term)
            if normalized and normalized not in focus_terms:
                focus_terms.append(normalized)

    if any(keyword in text_blob for keyword in ["warehouse", "dock", "mhe", "forklift", "logistics", "cold-chain"]):
        _add("warehouse", "distribution center", "logistics facility")
    if any(keyword in text_blob for keyword in ["manufacturing", "process", "compressed air", "steam", "boiler", "chiller", "reactive"]):
        _add("manufacturing facility", "industrial plant", "process operation")
    if any(keyword in text_blob for keyword in ["hvac", "tenant", "building", "office", "schedule", "controls"]):
        _add("commercial building", "multi-tenant facility", "building operations")
    if any(keyword in text_blob for keyword in ["hospital", "healthcare", "clinical"]):
        _add("hospital", "clinical facility", "healthcare operations")
    if not focus_terms:
        _add("facility operations", "asset performance")
    return focus_terms


def _query_family_spec(query_family: str) -> dict[str, Any]:
    return dict(_QUERY_FAMILY_TEMPLATE_LIBRARY.get(_text(query_family), _QUERY_FAMILY_TEMPLATE_LIBRARY["general_structural_prior_expansion"]))


def _preferred_query_families_for_source_family(source_family: str) -> list[str]:
    contract = _source_family_contract(source_family)
    return [_text(item) for item in list(contract.get("preferred_query_families", []) or []) if _text(item)]


def _provider_search_surface(provider_key: str, source_family: str) -> str:
    provider = _text(provider_key)
    family = _text(source_family)
    if provider == "scopus":
        return "TITLE-ABS-KEY"
    if provider == "ieee":
        return "IEEE metadata + abstract + index terms"
    if provider == "springer":
        return "Springer title + abstract + chapter/book metadata"
    if provider == "elsevier":
        return "Elsevier metadata + abstract + visible reference text"
    if provider in {"ashrae", "doe", "epa"}:
        return f"{_provider_display_name(provider)} guidance search"
    if family == "utility_tariff_billing_guidance":
        return "Utility tariff / billing guide search"
    if family == "oem_handbook_technical_manuals":
        return "OEM manual / technical handbook search"
    if family == "regulatory_code_compliance_guidance":
        return "Regulatory code / compliance guidance search"
    if family == "licensed_research_local_artifact":
        return "Local PDF / excerpt intake"
    if family == "specialist_web_case_signal":
        return "Specialist web case search"
    return "General structured search"


def _build_provider_query_strings(
    *,
    provider_key: str,
    query_family: str,
    asset_focus_terms: list[str],
    query_spec: Mapping[str, Any],
) -> dict[str, str]:
    focus_terms = asset_focus_terms[:2] or ["facility operations"]
    seed_terms = [_text(item) for item in list(query_spec.get("seed_terms", []) or []) if _text(item)]
    evidence_terms = [_text(item) for item in list(query_spec.get("evidence_targets", []) or []) if _text(item)]
    focus_group = " OR ".join(f'"{item}"' for item in focus_terms[:2])
    seed_group = " OR ".join(f'"{item}"' for item in seed_terms[:2])
    evidence_group = " OR ".join(f'"{item}"' for item in evidence_terms[:2])
    provider = _text(provider_key)

    if provider == "scopus":
        primary_query = f'TITLE-ABS-KEY(({focus_group}) AND ({seed_group}) AND ({evidence_group}))'
        pivot_query = f'TITLE-ABS-KEY(({focus_group}) AND ({seed_group}))'
    elif provider in {"ieee", "springer", "elsevier"}:
        primary_query = f'({focus_group}) AND ({seed_group}) AND ({evidence_group})'
        pivot_query = f'({focus_group}) AND ({seed_group})'
    elif provider in {"ashrae", "doe", "epa"}:
        primary_query = f'{focus_terms[0]} {seed_terms[0] if seed_terms else query_family.replace("_", " ")} {evidence_terms[0] if evidence_terms else ""}'.strip()
        pivot_query = f'{focus_terms[0]} {seed_terms[1] if len(seed_terms) > 1 else seed_terms[0] if seed_terms else query_family.replace("_", " ")}'.strip()
    else:
        primary_query = f'{focus_terms[0]} {seed_terms[0] if seed_terms else query_family.replace("_", " ")} {evidence_terms[0] if evidence_terms else ""}'.strip()
        pivot_query = f'{focus_terms[0]} {seed_terms[1] if len(seed_terms) > 1 else seed_terms[0] if seed_terms else query_family.replace("_", " ")}'.strip()

    return {
        "primary_query": primary_query,
        "pivot_query": pivot_query,
    }


def build_provider_query_template_rows(
    *,
    provider_targets: list[str] | None,
    source_family: str,
    query_families: list[str] | None,
    combination_row: Mapping[str, Any] | None = None,
) -> list[dict[str, Any]]:
    providers = [_text(item) for item in list(provider_targets or []) if _text(item)]
    if not providers:
        providers = _default_provider_targets_for_source_family(source_family)
    query_family_rows = [_text(item) for item in list(query_families or []) if _text(item)]
    asset_focus_terms = _infer_asset_focus_terms(combination_row or {})
    rows: list[dict[str, Any]] = []
    for provider_key in providers:
        for query_family in query_family_rows:
            query_spec = _query_family_spec(query_family)
            query_strings = _build_provider_query_strings(
                provider_key=provider_key,
                query_family=query_family,
                asset_focus_terms=asset_focus_terms,
                query_spec=query_spec,
            )
            rows.append(
                {
                    "provider_key": provider_key,
                    "provider_display_name": _provider_display_name(provider_key),
                    "source_family": _text(source_family),
                    "query_family": query_family,
                    "search_surface": _provider_search_surface(provider_key, source_family),
                    "asset_focus_terms": list(asset_focus_terms),
                    "seed_terms": [_text(item) for item in list(query_spec.get("seed_terms", []) or []) if _text(item)],
                    "evidence_targets": [_text(item) for item in list(query_spec.get("evidence_targets", []) or []) if _text(item)],
                    "search_intent": _text(query_spec.get("search_intent")),
                    "primary_query": _text(query_strings.get("primary_query")),
                    "pivot_query": _text(query_strings.get("pivot_query")),
                    "execution_hint": (
                        f"Start with {_provider_display_name(provider_key)} using {_provider_search_surface(provider_key, source_family).lower()} "
                        f"to pursue {query_family.replace('_', ' ')}."
                    ),
                }
            )
    return rows


def build_combination_campaign_execution_manifest_register(
    *,
    combination_follow_on_research_register: list[dict[str, Any]] | None,
    source_family_coverage_register: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    source_family_rows = {
        _text(row.get("source_family")): dict(row)
        for row in list(source_family_coverage_register or [])
        if _text(row.get("source_family"))
    }
    manifest_rows: list[dict[str, Any]] = []

    for follow_on_row in list(combination_follow_on_research_register or []):
        combination_id = _text(follow_on_row.get("combination_id"))
        if not combination_id:
            continue
        inferred_query_families = _infer_query_families(follow_on_row)
        execution_rows: list[dict[str, Any]] = []
        for trigger_row in list(follow_on_row.get("trigger_rows", []) or []):
            source_family = _text(trigger_row.get("source_family"))
            source_family_row = dict(source_family_rows.get(source_family, {}) or {})
            provider_targets = [
                _text(item)
                for item in list(trigger_row.get("recommended_provider_keys", []) or source_family_row.get("available_provider_keys", []) or [])
                if _text(item)
            ]
            if not provider_targets:
                provider_targets = _default_provider_targets_for_source_family(source_family)
            query_families: list[str] = []
            for query_family in [
                *list(trigger_row.get("preferred_query_families", []) or []),
                *_preferred_query_families_for_source_family(source_family),
                *inferred_query_families,
            ]:
                normalized_query_family = _text(query_family)
                if normalized_query_family and normalized_query_family not in query_families:
                    query_families.append(normalized_query_family)
            provider_query_templates = build_provider_query_template_rows(
                provider_targets=provider_targets,
                source_family=source_family,
                query_families=query_families,
                combination_row=follow_on_row,
            )
            execution_rows.append(
                {
                    "source_family": source_family,
                    "display_name": _text(trigger_row.get("display_name")) or source_family.replace("_", " ").title(),
                    "provider_targets": provider_targets,
                    "query_families": list(query_families),
                    "provider_query_templates": provider_query_templates,
                    "provider_query_template_count": len(provider_query_templates),
                    "target_document_delta": int(trigger_row.get("target_document_delta", 0) or 0),
                    "target_knowledge_atom_delta": int(trigger_row.get("target_knowledge_atom_delta", 0) or 0),
                    "search_focus": _text(trigger_row.get("search_focus")),
                    "execution_priority": "high" if _text(source_family_row.get("importance")) == "high" else "medium",
                    "execution_note": (
                        f"Use {(_text(trigger_row.get('display_name')) or source_family).lower()} "
                        f"to pursue {', '.join(query_families)} for {combination_id}."
                    ),
                }
            )
        manifest_rows.append(
            {
                "combination_id": combination_id,
                "combination_name": _text(follow_on_row.get("combination_name")) or combination_id,
                "recommended_source_families": list(follow_on_row.get("recommended_source_families", []) or []),
                "reasoning_flags": list(follow_on_row.get("reasoning_flags", []) or []),
                "query_families": inferred_query_families,
                "provider_query_template_count": sum(
                    int(item.get("provider_query_template_count", 0) or 0)
                    for item in execution_rows
                ),
                "execution_rows": execution_rows,
            }
        )

    manifest_rows.sort(key=lambda row: (_text(row.get("combination_name")), _text(row.get("combination_id"))))
    return manifest_rows
