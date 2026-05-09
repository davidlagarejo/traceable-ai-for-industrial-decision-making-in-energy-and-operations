from __future__ import annotations

from typing import Any


_REFERENCE_VISIBLE_STATES = {"visible_text_enriched", "manual_text_enriched"}
_REFERENCE_SOURCE_FAMILY_KNOWLEDGE_TYPE = {
    "utility_tariff_billing_guidance": "FINANCIAL_TRANSLATION",
    "oem_handbook_technical_manuals": "PROCESS_LOGIC",
    "regulatory_code_compliance_guidance": "REGULATORY_PHYSICAL_SIGNAL",
    "specialist_web_case_signal": "LOSS_PATTERN",
}
_REFERENCE_SOURCE_FAMILY_MINIMUM_EVIDENCE = {
    "utility_tariff_billing_guidance": [
        "utility bills",
        "tariff sheet",
        "billing demand terms",
    ],
    "oem_handbook_technical_manuals": [
        "equipment model family",
        "manual section",
        "operating context",
    ],
    "regulatory_code_compliance_guidance": [
        "applicable code section",
        "asset boundary",
        "compliance scope",
    ],
    "specialist_web_case_signal": [
        "context match to the asset",
        "operator evidence",
        "case-specific verification",
    ],
}
_REFERENCE_SOURCE_FAMILY_FINANCIAL_MECHANISM = {
    "utility_tariff_billing_guidance": (
        "Tariff design can shift the cost driver away from annual kWh narratives "
        "toward timing, demand, and billing structure."
    ),
    "oem_handbook_technical_manuals": (
        "OEM guidance can reveal control, sequencing, and maintenance constraints "
        "before any local diagnosis is admissible."
    ),
    "regulatory_code_compliance_guidance": (
        "Regulatory obligations can imply physical or control exposure before "
        "asset-specific confirmation."
    ),
    "specialist_web_case_signal": (
        "External case signals can expose recurring loss or control modes, but "
        "they remain structured priors until locally falsified."
    ),
}


def _text(value: Any) -> str:
    if value is None:
        return ""
    if isinstance(value, str):
        return value.strip()
    return str(value).strip()


def _slug(value: Any) -> str:
    text = _text(value).lower()
    chars: list[str] = []
    previous_dash = False
    for ch in text:
        safe = ch if ch.isalnum() else "-"
        if safe == "-":
            if previous_dash:
                continue
            previous_dash = True
        else:
            previous_dash = False
        chars.append(safe)
    return "".join(chars).strip("-")


def _pattern_id_from_candidate(candidate_record: dict[str, Any]) -> str:
    return (
        _text(candidate_record.get("matched_registry_pattern_id"))
        or _slug(candidate_record.get("name"))
        or _slug(candidate_record.get("id"))
    )


def _combination_id_from_candidate(candidate_record: dict[str, Any]) -> str:
    return (
        _text(candidate_record.get("matched_registry_combination_id"))
        or _slug(candidate_record.get("name"))
        or _slug(candidate_record.get("id"))
    )


def _reference_excerpt(reference_record: dict[str, Any]) -> str:
    reference = dict(reference_record or {})
    acquisition_result = dict(reference.get("acquisition_result", {}) or {})
    return (
        _text(reference.get("reference_excerpt"))
        or _text(acquisition_result.get("visible_text"))
        or _text(acquisition_result.get("search_result_snippet"))
        or _text(acquisition_result.get("search_brief"))
        or _text(reference.get("notes"))
    )


def _build_reference_knowledge_atom_rows(
    *,
    article_reference_register: list[dict[str, Any]] | None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for reference_record in list(article_reference_register or []):
        reference = dict(reference_record or {})
        reference_state = _text(reference.get("reference_state")) or "metadata_only"
        source_family = _text(reference.get("source_family"))
        if reference_state not in _REFERENCE_VISIBLE_STATES:
            continue
        if source_family not in _REFERENCE_SOURCE_FAMILY_KNOWLEDGE_TYPE:
            continue
        acquisition_result = dict(reference.get("acquisition_result", {}) or {})
        candidate_id = _text(reference.get("candidate_id"))
        document_title = _text(reference.get("title"))
        document_ref = (
            _text(reference.get("doi"))
            or _text(reference.get("source_url"))
            or _text(acquisition_result.get("final_url"))
            or candidate_id
            or document_title
        )
        source_locator = (
            _text(reference.get("source_url"))
            or _text(acquisition_result.get("final_url"))
            or candidate_id
            or document_ref
        )
        supporting_excerpt = _reference_excerpt(reference)
        if not supporting_excerpt:
            continue
        statement = supporting_excerpt[:400]
        matched_pattern_ids = sorted({
            _text(pattern_id)
            for pattern_id in list(reference.get("matched_pattern_ids", []) or [])
            if _text(pattern_id)
        })
        matched_combination_ids = sorted({
            _text(combination_id)
            for combination_id in list(reference.get("matched_combination_ids", []) or [])
            if _text(combination_id)
        })
        rows.append(
            {
                "atom_id": f"refatom::{source_family}::{_slug(candidate_id or document_ref or document_title)}",
                "knowledge_type": _REFERENCE_SOURCE_FAMILY_KNOWLEDGE_TYPE[source_family],
                "statement": statement,
                "asset_types": [],
                "applicable_industries": [],
                "applicable_contexts": [source_family],
                "anti_triggers": [],
                "falsification_conditions": [],
                "minimum_evidence": list(_REFERENCE_SOURCE_FAMILY_MINIMUM_EVIDENCE[source_family]),
                "financial_mechanism": _REFERENCE_SOURCE_FAMILY_FINANCIAL_MECHANISM[source_family],
                "supporting_excerpt": supporting_excerpt[:600],
                "source_locator": source_locator,
                "confidence_ceiling": "L2",
                "document_ref": document_ref,
                "document_title": document_title,
                "provider_key": _text(reference.get("provider_key")) or "manual",
                "source_family": source_family,
                "source_basis_id": _text(reference.get("source_basis_id")) or f"reference::{source_family}",
                "review_status": reference_state,
                "evidence_ceiling": "L2",
                "retrieval_purpose": _text(acquisition_result.get("status")) or "reference_capture",
                "supported_pattern_ids": matched_pattern_ids,
                "supported_combination_ids": matched_combination_ids,
            }
        )
    return rows


def build_knowledge_atom_register(
    *,
    extraction_records: list[dict[str, Any]] | None,
    article_reference_register: list[dict[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    atoms_by_key: dict[tuple[str, str], dict[str, Any]] = {}
    for extraction_record in list(extraction_records or []):
        record = dict(extraction_record or {})
        document_ref = _text(record.get("document_ref"))
        document_title = _text(record.get("document_title"))
        provider_key = _text(record.get("provider_key")) or "unknown_provider"
        source_family = _text(record.get("source_family"))
        source_basis_id = _text(record.get("source_basis_id"))
        review_status = _text(record.get("review_status")) or "draft"
        evidence_ceiling = _text(record.get("evidence_ceiling")) or "L2"
        retrieval_purpose = _text(record.get("retrieval_purpose"))
        pattern_support_by_atom: dict[str, set[str]] = {}
        pattern_candidate_by_id: dict[str, str] = {}
        for candidate_record in list(record.get("pattern_candidate_records", []) or []):
            candidate = dict(candidate_record or {})
            pattern_id = _pattern_id_from_candidate(candidate)
            candidate_id = _text(candidate.get("id"))
            if candidate_id and pattern_id:
                pattern_candidate_by_id[candidate_id] = pattern_id
            for atom_id in list(candidate.get("derived_from_atom_ids", []) or []):
                normalized_atom_id = _text(atom_id)
                if normalized_atom_id and pattern_id:
                    pattern_support_by_atom.setdefault(normalized_atom_id, set()).add(pattern_id)

        combination_support_by_atom: dict[str, set[str]] = {}
        for combination_candidate_record in list(record.get("combination_candidate_records", []) or []):
            candidate = dict(combination_candidate_record or {})
            combination_id = _combination_id_from_candidate(candidate)
            if not combination_id:
                continue
            pattern_candidate_ids = [
                _text(item)
                for item in list(candidate.get("derived_from_pattern_candidate_ids", []) or [])
                if _text(item)
            ]
            for pattern_candidate_id in pattern_candidate_ids:
                pattern_id = pattern_candidate_by_id.get(pattern_candidate_id)
                if not pattern_id:
                    continue
                for atom_id, supported_pattern_ids in pattern_support_by_atom.items():
                    if pattern_id in supported_pattern_ids:
                        combination_support_by_atom.setdefault(atom_id, set()).add(combination_id)

        for atom_record in list(record.get("knowledge_atoms", []) or []):
            atom = dict(atom_record or {})
            atom_id = _text(atom.get("id"))
            source_locator = _text(atom.get("source_locator"))
            if not atom_id and not source_locator:
                continue
            key = (atom_id or source_locator, document_ref or document_title or provider_key)
            existing = atoms_by_key.get(key, {})
            supported_pattern_ids = sorted(pattern_support_by_atom.get(atom_id, set()))
            supported_combination_ids = sorted(combination_support_by_atom.get(atom_id, set()))
            row = {
                "atom_id": atom_id or source_locator,
                "knowledge_type": _text(atom.get("knowledge_type")),
                "statement": _text(atom.get("statement")),
                "asset_types": list(atom.get("asset_types", []) or []),
                "applicable_industries": list(atom.get("applicable_industries", []) or []),
                "applicable_contexts": list(atom.get("applicable_contexts", []) or []),
                "anti_triggers": list(atom.get("anti_triggers", []) or []),
                "falsification_conditions": list(atom.get("falsification_conditions", []) or []),
                "minimum_evidence": list(atom.get("minimum_evidence", []) or []),
                "financial_mechanism": _text(atom.get("financial_mechanism")),
                "supporting_excerpt": _text(atom.get("supporting_excerpt")),
                "source_locator": source_locator,
                "confidence_ceiling": _text(atom.get("confidence_ceiling")) or "L2",
                "document_ref": document_ref,
                "document_title": document_title,
                "provider_key": provider_key,
                "source_family": source_family,
                "source_basis_id": source_basis_id,
                "review_status": review_status,
                "evidence_ceiling": evidence_ceiling,
                "retrieval_purpose": retrieval_purpose,
                "supported_pattern_ids": supported_pattern_ids,
                "supported_combination_ids": supported_combination_ids,
            }
            if existing:
                row["supported_pattern_ids"] = sorted(
                    set(list(existing.get("supported_pattern_ids", []) or [])).union(supported_pattern_ids)
                )
                row["supported_combination_ids"] = sorted(
                    set(list(existing.get("supported_combination_ids", []) or [])).union(supported_combination_ids)
                )
            atoms_by_key[key] = row

    for row in _build_reference_knowledge_atom_rows(
        article_reference_register=article_reference_register,
    ):
        key = (_text(row.get("atom_id")) or _text(row.get("source_locator")), _text(row.get("document_ref")))
        existing = atoms_by_key.get(key, {})
        if existing:
            row["supported_pattern_ids"] = sorted(
                set(list(existing.get("supported_pattern_ids", []) or [])).union(
                    list(row.get("supported_pattern_ids", []) or [])
                )
            )
            row["supported_combination_ids"] = sorted(
                set(list(existing.get("supported_combination_ids", []) or [])).union(
                    list(row.get("supported_combination_ids", []) or [])
                )
            )
        atoms_by_key[key] = row

    rows = list(atoms_by_key.values())
    rows.sort(
        key=lambda row: (
            _text(row.get("provider_key")),
            _text(row.get("document_ref")),
            _text(row.get("atom_id")),
        )
    )
    return rows


def summarize_source_coverage(
    *,
    knowledge_atom_register: list[dict[str, Any]] | None,
    extraction_records: list[dict[str, Any]] | None = None,
    article_reference_register: list[dict[str, Any]] | None = None,
    discovery_candidate_review_register: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    atoms = list(knowledge_atom_register or [])
    extraction_rows = list(extraction_records or [])
    article_rows = list(article_reference_register or [])
    discovery_rows = list(discovery_candidate_review_register or [])
    provider_keys = sorted({
        _text(row.get("provider_key"))
        for row in atoms
        if _text(row.get("provider_key"))
    })
    knowledge_types = sorted({
        _text(row.get("knowledge_type"))
        for row in atoms
        if _text(row.get("knowledge_type"))
    })
    supported_pattern_ids = sorted({
        _text(pattern_id)
        for row in atoms
        for pattern_id in list(row.get("supported_pattern_ids", []) or [])
        if _text(pattern_id)
    })
    document_refs = sorted({
        _text(row.get("document_ref"))
        for row in atoms
        if _text(row.get("document_ref"))
    })
    return {
        "knowledge_atom_count": len(atoms),
        "document_count": len(document_refs),
        "provider_count": len(provider_keys),
        "providers": provider_keys,
        "knowledge_types": knowledge_types,
        "supported_pattern_count": len(supported_pattern_ids),
        "supported_pattern_ids": supported_pattern_ids,
        "extraction_record_count": len(extraction_rows),
        "reference_record_count": len(article_rows),
        "visible_reference_count": sum(
            1
            for row in article_rows
            if _text(row.get("reference_state")) in {"visible_text_enriched", "manual_text_enriched"}
        ),
        "accepted_reference_count": sum(
            1
            for row in discovery_rows
            if _text(row.get("operator_decision")) == "accepted_for_reference_use"
        ),
        "coverage_strength": (
            "strong"
            if len(atoms) >= 8 and len(document_refs) >= 2
            else "moderate"
            if len(atoms) >= 3
            else "thin"
            if len(atoms) >= 1
            else "empty"
        ),
    }
