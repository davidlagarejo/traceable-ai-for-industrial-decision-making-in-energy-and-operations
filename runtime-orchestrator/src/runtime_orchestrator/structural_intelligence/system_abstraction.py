from __future__ import annotations

from typing import Any

from .schemas import StructuralEvidenceState, StructuralStatement


def _normalized_field_map(asset_field_register: list[dict[str, Any]]) -> dict[str, list[dict[str, Any]]]:
    by_field: dict[str, list[dict[str, Any]]] = {}
    for row in asset_field_register:
        field_name = str(row.get("field", "")).strip().lower()
        if not field_name:
            continue
        by_field.setdefault(field_name, []).append(row)
    return by_field


def _dataset_keys(dataset_coverage_register: list[dict[str, Any]]) -> set[str]:
    keys: set[str] = set()
    for row in dataset_coverage_register:
        key = str(row.get("dataset_key", "")).strip().lower()
        if key:
            keys.add(key)
    return keys


def _source_markers(source_register: list[dict[str, Any]]) -> set[str]:
    markers: set[str] = set()
    for row in source_register:
        for key in ("source_type", "source_family", "source_id"):
            value = str(row.get(key, "")).strip().lower()
            if value:
                markers.add(value)
    return markers


def _source_ids_for_fields(field_map: dict[str, list[dict[str, Any]]], *field_names: str) -> list[str]:
    source_ids: list[str] = []
    seen: set[str] = set()
    for field_name in field_names:
        for row in field_map.get(field_name.lower(), []):
            source_id = str(row.get("source_id", "")).strip()
            if source_id and source_id not in seen:
                seen.add(source_id)
                source_ids.append(source_id)
    return source_ids


def _statement(
    statement: str,
    evidence_state: StructuralEvidenceState,
    supporting_sources: list[str],
    falsification_condition: str,
    minimum_evidence_required: list[str],
) -> dict[str, Any]:
    return StructuralStatement(
        statement=statement,
        evidence_state=evidence_state,
        supporting_sources=supporting_sources,
        falsification_condition=falsification_condition,
        minimum_evidence_required=minimum_evidence_required,
    ).to_dict()


def _regulatory_observation(
    target_type: str,
    jurisdictions: list[str],
    dataset_keys: set[str],
    source_markers: set[str],
) -> tuple[str, StructuralEvidenceState, list[str]]:
    jurisdiction_set = {code.upper() for code in jurisdictions}
    if (
        target_type == "commercial_building"
        and any(code.startswith("US-NY-NYC") for code in jurisdiction_set)
        and (
            "nyc_ll84_energy_benchmarking" in dataset_keys
            or "nyc_ll97_covered_buildings_list" in dataset_keys
            or "nyc_ll97_public_filing_candidate" in dataset_keys
            or "nyc_pluto_property" in dataset_keys
        )
    ):
        return (
            "Public NYC LL84 and LL97 records support covered-building compliance and investment screening exposure, while closure still requires filing-grade evidence.",
            StructuralEvidenceState.OBSERVED_FACT,
            [
                key
                for key in (
                    "nyc_ll84_energy_benchmarking",
                    "nyc_ll97_covered_buildings_list",
                    "nyc_ll97_public_filing_candidate",
                    "nyc_pluto_property",
                )
                if key in dataset_keys
            ],
        )
    if target_type == "manufacturing_facility" and (
        "tceq_permits_and_emissions" in dataset_keys
        or "tceq_air_permit" in source_markers
        or "epa_echo" in source_markers
    ):
        return (
            "Public permit and emissions records indicate industrial environmental and compliance exposure, but not redesign closure.",
            StructuralEvidenceState.OBSERVED_FACT,
            [
                key
                for key in ("tceq_permits_and_emissions", "tceq_air_permit", "epa_echo")
                if key in dataset_keys or key in source_markers
            ],
        )
    if jurisdictions:
        return (
            "Jurisdiction-specific regulatory exposure is plausible but not yet bounded by asset-specific screening evidence.",
            StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
            jurisdictions,
        )
    return (
        "Regulatory exposure is not observed well enough to support structural framing yet.",
        StructuralEvidenceState.NOT_OBSERVED,
        [],
    )


def build_system_abstraction(
    *,
    target_definition: dict[str, Any],
    canonical_asset_context_summary: dict[str, Any],
    archetype_resolution: dict[str, Any],
    archetype_library_register: list[dict[str, Any]],
    asset_field_register: list[dict[str, Any]],
    dataset_coverage_register: list[dict[str, Any]],
    source_register: list[dict[str, Any]],
) -> dict[str, Any]:
    field_map = _normalized_field_map(asset_field_register)
    dataset_keys = _dataset_keys(dataset_coverage_register)
    source_markers = _source_markers(source_register)
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    jurisdictions = [str(code).strip() for code in target_definition.get("jurisdiction_scope", []) if str(code).strip()]
    archetype = dict(archetype_library_register[0] if archetype_library_register else {})
    selected_archetype = str(archetype_resolution.get("selected_archetype_id", "")).strip()
    screening_supported = bool(canonical_asset_context_summary.get("screening_supported"))
    supported_fields = list(canonical_asset_context_summary.get("supported_field_register", []) or [])

    asset_type_sources = ["target_definition.target_type"]
    business_min_evidence = list(archetype.get("minimum_evidence_required", []) or [])
    process_sources = _source_ids_for_fields(field_map, "process_flow", "load_driver", "asset_class", "HVAC_type")
    control_sources = _source_ids_for_fields(field_map, "owner_control_boundary", "tenant_metering", "lease_responsibility", "metering_topology")
    drivers_sources = _source_ids_for_fields(
        field_map,
        "utility_bills",
        "current_eui",
        "operating_schedule",
        "process_flow",
        "load_driver",
    )
    regulatory_statement, regulatory_state, regulatory_sources = _regulatory_observation(
        target_type,
        jurisdictions,
        dataset_keys,
        source_markers,
    )

    if selected_archetype == "target_not_yet_structurally_modelable":
        unresolved = _statement(
            "The target is not yet structurally modelable as a physical operating asset.",
            StructuralEvidenceState.INADMISSIBLE_CLAIM,
            ["motor_007.target_classification_object"],
            "The target is confirmed as a bounded physical operating asset with asset-level operating substrate evidence.",
            business_min_evidence,
        )
        return {
            "asset_type": unresolved,
            "business_function": unresolved,
            "value_creation_mechanism": unresolved,
            "dominant_process_type": unresolved,
            "dominant_physical_drivers": unresolved,
            "dominant_operational_drivers": unresolved,
            "control_structure": unresolved,
            "constraint_structure": unresolved,
            "economic_driver": unresolved,
            "regulatory_exposure": unresolved,
            "evidence_maturity": unresolved,
        }

    process_state = (
        StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
        if process_sources
        else StructuralEvidenceState.ARCHETYPAL_PRIOR
    )
    control_state = (
        StructuralEvidenceState.OBSERVED_FACT
        if control_sources
        else StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    )
    constraints_state = (
        StructuralEvidenceState.OBSERVED_FACT
        if regulatory_state == StructuralEvidenceState.OBSERVED_FACT and screening_supported
        else StructuralEvidenceState.CONDITIONAL_HYPOTHESIS
    )
    evidence_maturity_state = (
        StructuralEvidenceState.OBSERVED_FACT
        if screening_supported
        else StructuralEvidenceState.ARCHETYPAL_PRIOR
    )

    system_abstraction = {
        "asset_type": _statement(
            f"Target asset type is framed as `{target_type or 'unknown'}` for structural analysis.",
            StructuralEvidenceState.OBSERVED_FACT if target_type else StructuralEvidenceState.NOT_OBSERVED,
            asset_type_sources if target_type else [],
            "Target classification or target definition changes materially.",
            ["target definition confirmation"],
        ),
        "business_function": _statement(
            str(archetype.get("business_function", "Business function not yet observed.")),
            StructuralEvidenceState.ARCHETYPAL_PRIOR,
            [selected_archetype] if selected_archetype else [],
            "Observed operating or process records show a different value-generating function.",
            business_min_evidence,
        ),
        "value_creation_mechanism": _statement(
            str(archetype.get("value_creation_mechanism", "Value-creation mechanism not yet observed.")),
            StructuralEvidenceState.ARCHETYPAL_PRIOR,
            [selected_archetype] if selected_archetype else [],
            "Observed economics and operating data show a different mechanism of value capture.",
            business_min_evidence,
        ),
        "dominant_process_type": _statement(
            str(archetype.get("dominant_process_type", "Dominant process type not yet observed.")),
            process_state,
            process_sources or ([selected_archetype] if selected_archetype else []),
            "Observed process maps, system topology, or operating records show a materially different process structure.",
            business_min_evidence,
        ),
        "dominant_physical_drivers": _statement(
            f"Candidate dominant physical drivers: {', '.join(archetype.get('dominant_physical_drivers', []) or ['none yet'])}.",
            StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if drivers_sources else StructuralEvidenceState.ARCHETYPAL_PRIOR,
            drivers_sources or ([selected_archetype] if selected_archetype else []),
            "Observed load-driver or equipment evidence shows different physical dominance.",
            business_min_evidence,
        ),
        "dominant_operational_drivers": _statement(
            f"Candidate dominant operational drivers: {', '.join(archetype.get('dominant_operational_drivers', []) or ['none yet'])}.",
            StructuralEvidenceState.CONDITIONAL_HYPOTHESIS if drivers_sources else StructuralEvidenceState.ARCHETYPAL_PRIOR,
            drivers_sources or ([selected_archetype] if selected_archetype else []),
            "Observed schedule, throughput, or maintenance evidence shifts the operating bottleneck.",
            business_min_evidence,
        ),
        "control_structure": _statement(
            str(archetype.get("control_structure", "Control structure not yet bounded.")),
            control_state,
            control_sources or ([selected_archetype] if selected_archetype else []),
            "Meter maps, contracts, or operator records show a different control boundary.",
            business_min_evidence,
        ),
        "constraint_structure": _statement(
            str(archetype.get("constraint_structure", "Constraint structure not yet bounded.")),
            constraints_state,
            (regulatory_sources or []) + ([selected_archetype] if selected_archetype else []),
            "Observed permits, filings, or operating constraints show a different limiting structure.",
            business_min_evidence,
        ),
        "economic_driver": _statement(
            str(archetype.get("economic_driver", "Economic driver not yet bounded.")),
            StructuralEvidenceState.CONDITIONAL_HYPOTHESIS,
            ([selected_archetype] if selected_archetype else []) + regulatory_sources,
            "Observed cost, revenue, or operational records show that another variable dominates economics.",
            business_min_evidence,
        ),
        "regulatory_exposure": _statement(
            regulatory_statement,
            regulatory_state,
            regulatory_sources,
            "Observed filings, permits, or jurisdiction signals contradict the current regulatory framing.",
            business_min_evidence,
        ),
        "evidence_maturity": _statement(
            (
                f"Canonical public evidence supports screening-level structural framing across {len(supported_fields)} supported fields."
                if screening_supported
                else "Current structural framing remains archetypal and requires more asset-specific evidence."
            ),
            evidence_maturity_state,
            [row.get("field") for row in supported_fields if row.get("field")] if screening_supported else [selected_archetype],
            "New evidence shows the current structural abstraction is either stronger or materially wrong.",
            business_min_evidence,
        ),
    }
    return system_abstraction
