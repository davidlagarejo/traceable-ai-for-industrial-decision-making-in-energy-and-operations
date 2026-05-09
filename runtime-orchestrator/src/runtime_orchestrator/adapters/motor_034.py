from __future__ import annotations

from datetime import datetime, timezone
from typing import Any

from ..evidence_maturity import (
    CLAIM_TEMPLATES,
    DECISION_TEMPLATES,
    VARIABLE_CATALOG,
    EvidenceMaturityLevel,
    PermissionState,
    RecencyState,
    SourceAuthority,
    SourceScope,
    VariableMaturityRecord,
    ClaimPermissionRecord,
    DecisionPermissionRecord,
    ReportReadinessRecord,
    derive_cluster_maturity,
    derive_dependency_bottleneck,
    expand_dependency_variables,
)
from ..evidence_maturity.domain_packs import NYC_DATASETS
from .base import BaseMotorAdapter


_FIELD_TO_VARIABLE = {
    "asset_class": "asset_type",
    "occupancy_use": "occupancy",
    "renovations": "major_renovations",
    "current_EUI": "EUI",
    "compliance_filings": "compliance_filing",
    "BMS_control_system": "controls_architecture",
}

_REGULATORY_CONTEXT_VARIABLES = {
    "jurisdiction",
    "applicable_rule_family",
    "penalty_rate",
    "benchmarking_requirement",
    "compliance_period",
    "emissions_factor",
}

_CRITICAL_REPORT_VARIABLES = [
    "asset_vs_entity_classification",
    "address",
    "asset_type",
    "GFA",
    "operating_schedule",
    "primary_fuel",
    "HVAC_type",
    "jurisdiction",
]

_TECHNICAL_REPORT_TYPES = [
    "Full Technical Decision Intelligence Report",
    "Decision-Grade Asset Brief",
    "Decision-Grade TDIR",
    "Exploratory Prior / Minimum Evidence Report",
]

_CANONICAL_REPORT_TYPE_MAP = {
    "Address Candidate Brief": "Decision-Blocked Asset Brief",
    "Site Candidate Brief": "Decision-Blocked Asset Brief",
    "Asset Context Seed Brief": "Decision-Blocked Asset Brief",
    "Asset Context Insufficiency Brief": "Decision-Blocked Asset Brief",
    "Pre-Verification Asset Brief": "Decision-Blocked Asset Brief",
    "Issuer Context Memo": "Target Classification Brief",
}

_CANONICAL_OUTPUT_MODE_ALIAS_MAP = {
    "Entity Address Classification Brief": "Target Classification Brief",
    "Target Clarification Brief": "Target Classification Brief",
}

_CANONICAL_OUTPUT_MODES = [
    "Target Classification Brief",
    "Decision-Blocked Asset Brief",
    "Exploratory Prior Brief",
    "Compliance / Investment Screening Brief",
    "Structural Contradiction Brief",
    "System Redesign Hypothesis Brief",
    "Competitive Positioning Brief",
    "TAD Action Priority Brief",
    "Full Technical Decision Intelligence Report",
]

_STRUCTURAL_OUTPUT_MODES = {
    "Structural Contradiction Brief",
    "System Redesign Hypothesis Brief",
    "Competitive Positioning Brief",
    "TAD Action Priority Brief",
}

_SCREENING_BUILDING_TYPES = {
    "commercial_building",
    "multifamily_building",
    "data_center",
}

_BOUND_CONGRUENCE_STATES = {"partially_bound", "sufficiently_bound"}
_FULL_TDIR_READY_TYPES = {
    "commercial_building",
    "multifamily_building",
    "data_center",
    "manufacturing_facility",
}


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _canonical_report_type_label(report_type: str) -> str:
    label = str(report_type or "").strip()
    return _CANONICAL_REPORT_TYPE_MAP.get(label, label)


def _canonical_output_mode_label(report_type: str) -> str:
    label = _canonical_report_type_label(report_type)
    return _CANONICAL_OUTPUT_MODE_ALIAS_MAP.get(label, label)


def _format_problem_label(value: Any) -> str:
    text = str(value or "").strip().replace("_", " ")
    return " ".join(text.split())


def _has_sufficient_congruence_binding(local_evidence_binding_register: list[dict[str, Any]]) -> bool:
    return any(
        str(row.get("current_local_binding_state", "")).strip() == "sufficiently_bound"
        for row in local_evidence_binding_register
        if isinstance(row, dict)
    )


def _first_bound_congruence_claim(local_evidence_binding_register: list[dict[str, Any]]) -> dict[str, Any]:
    for row in local_evidence_binding_register:
        if not isinstance(row, dict):
            continue
        if str(row.get("current_local_binding_state", "")).strip() not in _BOUND_CONGRUENCE_STATES:
            continue
        return row
    return {}


def _normalize_variable_name(field_name: str) -> str:
    normalized = str(field_name or "").strip()
    return _FIELD_TO_VARIABLE.get(normalized, normalized)


def _is_nyc_target(target_definition: dict[str, Any]) -> bool:
    scopes = target_definition.get("jurisdiction_scope", []) if isinstance(target_definition, dict) else []
    if isinstance(scopes, list) and "US-NY-NYC" in scopes:
        return True
    address = str((target_definition or {}).get("address_raw", "")).upper()
    return "NEW YORK" in address and "NY" in address


def _dataset_status(source_register: list[dict[str, Any]], dataset_key: str) -> tuple[str, list[str]]:
    tokens = {
        "nyc_dof_property_record": ["dof", "property", "bbl", "parcel"],
        "nyc_pluto": ["pluto"],
        "nyc_dob_permits": ["dob", "permit"],
        "nyc_ll84_benchmarking": ["ll84", "benchmark", "energy star"],
        "nyc_ll97_emissions": ["ll97", "local law 97", "emission"],
    }.get(dataset_key, [dataset_key])
    matched: list[str] = []
    for row in source_register:
        haystack = " ".join(
            [
                str(row.get("source_id", "")),
                str(row.get("title", "")),
                str(row.get("url", "")),
                str(row.get("source_family", "")),
            ]
        ).lower()
        if any(token in haystack for token in tokens):
            matched.append(str(row.get("source_id", "")) or str(row.get("title", "")))
    if not matched:
        return "not_observed", []
    accepted_rows = [row for row in source_register if (str(row.get("source_id", "")) or str(row.get("title", ""))) in matched and row.get("accepted")]
    if accepted_rows:
        return "accepted", matched
    return "rejected_or_deferred", matched


def _dataset_coverage_register(target_definition: dict[str, Any], source_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not _is_nyc_target(target_definition):
        return []
    rows: list[dict[str, Any]] = []
    for key, definition in NYC_DATASETS.items():
        status, matched = _dataset_status(source_register, key)
        rows.append(
            {
                "dataset_key": key,
                "dataset_name": definition.display_name,
                "status": status,
                "field_coverage": list(definition.coverage_variables),
                "notes": definition.notes,
                "matched_sources": matched,
            }
        )
    return rows


def _explicit_dataset_coverage_register(target_definition: dict[str, Any], explicit_register: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not _is_nyc_target(target_definition):
        return []
    rows: list[dict[str, Any]] = []
    for row in explicit_register:
        if not isinstance(row, dict):
            continue
        dataset_key = str(row.get("dataset_key", "")).strip()
        if not dataset_key:
            continue
        definition = NYC_DATASETS.get(dataset_key)
        rows.append(
            {
                "dataset_key": dataset_key,
                "dataset_name": row.get("dataset_name") or (definition.display_name if definition else dataset_key),
                "status": row.get("status", "not_observed"),
                "field_coverage": list(row.get("field_coverage", []) or (list(definition.coverage_variables) if definition else [])),
                "notes": row.get("notes", "") or (definition.notes if definition else ""),
                "matched_sources": list(row.get("matched_sources", []) or []),
            }
        )
    return rows


def _build_field_row_map(asset_field_register: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    rows: dict[str, dict[str, Any]] = {}
    for row in asset_field_register:
        variable_name = _normalize_variable_name(str(row.get("field", "")))
        if variable_name:
            rows[variable_name] = row
            if variable_name == "controls_architecture" and row.get("value") not in {"", "NOT_OBSERVED", "BLOCKING_FIELD"}:
                rows.setdefault(
                    "BMS_presence",
                    {
                        **row,
                        "field": "BMS_presence",
                        "value": "present",
                    },
                )
    return rows


def _row_attr(row: Any, key: str, default: Any = None) -> Any:
    if isinstance(row, dict):
        return row.get(key, default)
    return getattr(row, key, default)


def _has_observed_value(row: Any) -> bool:
    value = _row_attr(row, "value")
    status = str(_row_attr(row, "status", "")).upper()
    if status in {"NOT_OBSERVED", "BLOCKING_FIELD", "NOT_PUBLICLY_AVAILABLE", "REQUIRES_CLIENT_INPUT"}:
        return False
    text = str(value).strip().upper()
    return bool(text and text not in {"NOT_OBSERVED", "BLOCKING_FIELD", "NOT_PUBLICLY_AVAILABLE", "REQUIRES_CLIENT_INPUT"})


def _maturity_from_field_row(variable_name: str, row: dict[str, Any]) -> EvidenceMaturityLevel:
    if not row or not _has_observed_value(row):
        return EvidenceMaturityLevel.L0
    admissibility = str(row.get("admissibility", "")).upper()
    scope = str(row.get("scope", "")).upper()
    authority = str(row.get("authority_score", "")).lower()
    confirmation_state = str(row.get("confirmation_state", "")).upper()
    if confirmation_state == "FIELD_VERIFIED":
        return EvidenceMaturityLevel.L4
    if confirmation_state == "DECLARED_BY_USER" or admissibility == "DECLARED_INPUT_ONLY":
        return EvidenceMaturityLevel.L1
    if confirmation_state in {"AUTHORITY_CONFIRMED", "OPERATOR_CONFIRMED"} and scope == "ASSET_LEVEL":
        return EvidenceMaturityLevel.L3
    if admissibility == "BENCHMARK_ONLY":
        return EvidenceMaturityLevel.L1
    if admissibility in {"ENTITY_CONTEXT_ONLY", "PORTFOLIO_CONTEXT_ONLY"}:
        if variable_name in {"owner", "operator", "financing_cost", "debt_schedule"}:
            return EvidenceMaturityLevel.L2 if authority in {"high", "medium"} else EvidenceMaturityLevel.L1
        return EvidenceMaturityLevel.L1
    if admissibility == "JURISDICTION_CONTEXT_ONLY":
        if variable_name in _REGULATORY_CONTEXT_VARIABLES:
            return EvidenceMaturityLevel.L3 if authority in {"high", "medium"} else EvidenceMaturityLevel.L2
        return EvidenceMaturityLevel.L2
    if admissibility == "INFERRED_ASSET_LEVEL":
        return EvidenceMaturityLevel.L2
    if admissibility == "OBSERVED_PUBLIC_ASSET_LEVEL":
        return EvidenceMaturityLevel.L2
    if admissibility == "CONFIRMED_ASSET_LEVEL":
        return EvidenceMaturityLevel.L3
    if scope == "BENCHMARK_LEVEL":
        return EvidenceMaturityLevel.L1
    if scope == "JURISDICTION_LEVEL":
        return EvidenceMaturityLevel.L2
    return EvidenceMaturityLevel.L2


def _build_base_record(variable_name: str) -> VariableMaturityRecord:
    catalog = VARIABLE_CATALOG[variable_name]
    return VariableMaturityRecord(
        variable_name=variable_name,
        variable_family=catalog.variable_family,
        value="NOT_OBSERVED",
        maturity_level=EvidenceMaturityLevel.L0,
        evidence_source=f"not_observed::{variable_name}",
        source_scope=catalog.default_scope,
        authority_score=SourceAuthority.UNKNOWN,
        recency=RecencyState.UNKNOWN,
        uncertainty_reason="No admissible evidence registered for this variable yet.",
        allowed_outputs=["missing field flag", "evidence request"],
        prohibited_outputs=["strong claim", "decision-grade use"],
        upgrade_condition="Add admissible source evidence for this variable.",
        downgrade_condition="Conflict, contamination, stale evidence, or weaker scope substitution.",
        decisions_unlocked=[],
        dependent_claims=[],
    )


def _source_scope(value: str | None) -> SourceScope:
    try:
        return SourceScope(str(value or "").upper())
    except Exception:
        return SourceScope.UNKNOWN


def _source_authority(value: str | None) -> SourceAuthority:
    try:
        return SourceAuthority(str(value or "").lower())
    except Exception:
        return SourceAuthority.UNKNOWN


def _recency_state(value: str | None) -> RecencyState:
    try:
        return RecencyState(str(value or "").lower())
    except Exception:
        return RecencyState.UNKNOWN


def _allowed_outputs_for_level(variable_name: str, level: EvidenceMaturityLevel) -> list[str]:
    if variable_name in {"ROI", "payback", "NPV", "IRR"}:
        if level == EvidenceMaturityLevel.L0:
            return ["no ROI"]
        if level == EvidenceMaturityLevel.L1:
            return ["directional economics"]
        if level == EvidenceMaturityLevel.L2:
            return ["preliminary ROI range"]
        if level == EvidenceMaturityLevel.L3:
            return ["scenario-based ROI"]
        return ["strong bounded ROI"]
    if level == EvidenceMaturityLevel.L0:
        return ["missing field flag", "evidence request"]
    if level == EvidenceMaturityLevel.L1:
        return ["screening", "plausibility framing"]
    if level == EvidenceMaturityLevel.L2:
        return ["preliminary scenario", "directional range"]
    if level == EvidenceMaturityLevel.L3:
        return ["decision-grade screening", "bounded numeric output"]
    return ["strongest bounded output"]


def _prohibited_outputs_for_level(variable_name: str, level: EvidenceMaturityLevel) -> list[str]:
    if level == EvidenceMaturityLevel.L0:
        return ["ROI", "compliance closure", "verified savings", "final recommendation"]
    if level == EvidenceMaturityLevel.L1:
        return ["closed ROI", "compliance closure", "asset truth substitution"]
    if level == EvidenceMaturityLevel.L2:
        return ["verification-grade output", "bankability"]
    if level == EvidenceMaturityLevel.L3:
        return ["verified savings without hardening", "claims outside bounded validity"]
    return ["universal extrapolation beyond verified boundary"]


def _build_record_from_field(variable_name: str, row: dict[str, Any]) -> VariableMaturityRecord:
    catalog = VARIABLE_CATALOG[variable_name]
    level = _maturity_from_field_row(variable_name, row)
    confirmation_state = str(row.get("confirmation_state", "")).strip()
    uncertainty = {
        EvidenceMaturityLevel.L0: "Variable not observed or not admissible.",
        EvidenceMaturityLevel.L1: "Variable supported only by benchmark, proxy, or weak context.",
        EvidenceMaturityLevel.L2: "Variable is asset-specific but not yet strongly verified.",
        EvidenceMaturityLevel.L3: "Variable is locally documented or measured from strong public evidence.",
        EvidenceMaturityLevel.L4: "Variable is independently verified or hardened.",
    }[level]
    if confirmation_state == "DECLARED_BY_USER":
        uncertainty = "Variable currently exists only as declared input and cannot be treated as verified evidence."
    return VariableMaturityRecord(
        variable_name=variable_name,
        variable_family=catalog.variable_family,
        value=row.get("value", "NOT_OBSERVED"),
        maturity_level=level,
        evidence_source=str(row.get("source_id", "")) or f"declared_input::{variable_name}",
        source_scope=_source_scope(row.get("scope")),
        authority_score=_source_authority(row.get("authority_score")),
        recency=_recency_state(row.get("recency")),
        uncertainty_reason=uncertainty,
        allowed_outputs=_allowed_outputs_for_level(variable_name, level),
        prohibited_outputs=_prohibited_outputs_for_level(variable_name, level),
        upgrade_condition="Provide stronger asset-level or verified evidence for this variable.",
        downgrade_condition="Contamination, weaker scope substitution, stale evidence, or contradiction.",
        decisions_unlocked=[],
        dependent_claims=[],
    )


def _source_matches(record: VariableMaturityRecord, *tokens: str) -> bool:
    haystack = " ".join(
        [
            str(record.evidence_source),
            str(record.value),
            str(record.uncertainty_reason),
        ]
    ).lower()
    return any(token.lower() in haystack for token in tokens)


def _replace_record_level(
    record: VariableMaturityRecord,
    *,
    level: EvidenceMaturityLevel,
    value: Any | None = None,
    evidence_source: str | None = None,
    source_scope: SourceScope | None = None,
    authority_score: SourceAuthority | None = None,
    uncertainty_reason: str | None = None,
    decisions_unlocked: list[str] | None = None,
) -> VariableMaturityRecord:
    return VariableMaturityRecord(
        variable_name=record.variable_name,
        variable_family=record.variable_family,
        value=record.value if value is None else value,
        maturity_level=level,
        evidence_source=evidence_source or record.evidence_source,
        source_scope=source_scope or record.source_scope,
        authority_score=authority_score or record.authority_score,
        recency=record.recency,
        uncertainty_reason=uncertainty_reason or record.uncertainty_reason,
        allowed_outputs=_allowed_outputs_for_level(record.variable_name, level),
        prohibited_outputs=_prohibited_outputs_for_level(record.variable_name, level),
        upgrade_condition=record.upgrade_condition,
        downgrade_condition=record.downgrade_condition,
        decisions_unlocked=decisions_unlocked if decisions_unlocked is not None else record.decisions_unlocked,
        dependent_claims=record.dependent_claims,
    )


def _screening_basis_row(compliance_case: dict[str, Any], basis_name: str) -> dict[str, Any]:
    for row in compliance_case.get("screening_basis_register", []) if isinstance(compliance_case.get("screening_basis_register", []), list) else []:
        if str(row.get("basis_name", "")).strip() == basis_name:
            return row
    return {}


def _is_nyc_context(
    target_definition: dict[str, Any],
    dataset_coverage_register: list[dict[str, Any]] | None = None,
) -> bool:
    jurisdiction_scope = (
        target_definition.get("jurisdiction_scope", [])
        if isinstance(target_definition.get("jurisdiction_scope", []), list)
        else []
    )
    for entry in jurisdiction_scope:
        entry_text = str(entry).strip().lower()
        if entry_text in {"nyc", "new york city"}:
            return True
    for row in dataset_coverage_register or []:
        dataset_key = str(row.get("dataset_key", "")).strip().lower()
        if dataset_key.startswith("nyc_"):
            return True
    return False


def _overlay_identity_and_regulatory_records(
    records: dict[str, VariableMaturityRecord],
    target_definition: dict[str, Any],
    target_classification: dict[str, Any],
    compliance_case: dict[str, Any],
    dataset_coverage_register: list[dict[str, Any]] | None = None,
) -> None:
    target_type = str(target_classification.get("target_type", "")).strip()
    classification_confidence = str(target_classification.get("classification_confidence", "")).strip().lower()
    is_nyc_context = _is_nyc_context(target_definition, dataset_coverage_register)
    if "asset_vs_entity_classification" in records:
        level = EvidenceMaturityLevel.L3 if target_type else EvidenceMaturityLevel.L0
        if classification_confidence == "low":
            level = EvidenceMaturityLevel.L2 if level > EvidenceMaturityLevel.L0 else level
        records["asset_vs_entity_classification"] = VariableMaturityRecord(
            variable_name="asset_vs_entity_classification",
            variable_family="identity",
            value=target_type or "NOT_OBSERVED",
            maturity_level=level,
            evidence_source="motor_007.target_classification_object",
            source_scope=SourceScope.ASSET_LEVEL,
            authority_score=SourceAuthority.HIGH,
            recency=RecencyState.CURRENT,
            uncertainty_reason="Classification is bounded by currently available public identity evidence.",
            allowed_outputs=_allowed_outputs_for_level("asset_vs_entity_classification", level),
            prohibited_outputs=_prohibited_outputs_for_level("asset_vs_entity_classification", level),
            upgrade_condition="Add stronger parcel, registry, or asset-page confirmation.",
            downgrade_condition="Identity conflict or contamination emerges.",
            decisions_unlocked=["target admissibility", "report-type switching"] if level >= EvidenceMaturityLevel.L2 else [],
            dependent_claims=["asset_identity_confirmed_claim"],
        )
    jurisdiction_scope = target_definition.get("jurisdiction_scope", []) if isinstance(target_definition.get("jurisdiction_scope", []), list) else []
    if "jurisdiction" in records and jurisdiction_scope:
        records["jurisdiction"] = VariableMaturityRecord(
            variable_name="jurisdiction",
            variable_family="regulatory",
            value=",".join(jurisdiction_scope),
            maturity_level=EvidenceMaturityLevel.L3,
            evidence_source="target_definition.jurisdiction_scope",
            source_scope=SourceScope.JURISDICTION_LEVEL,
            authority_score=SourceAuthority.HIGH,
            recency=RecencyState.CURRENT,
            uncertainty_reason="Jurisdiction is strong for routing and screening, but local filing status may still be incomplete.",
            allowed_outputs=_allowed_outputs_for_level("jurisdiction", EvidenceMaturityLevel.L3),
            prohibited_outputs=_prohibited_outputs_for_level("jurisdiction", EvidenceMaturityLevel.L3),
            upgrade_condition="Confirm regulated building identifiers or filing path.",
            downgrade_condition="Address or municipality mismatch.",
            decisions_unlocked=["regulatory screening", "dataset routing"],
            dependent_claims=(
                ["compliance_screening_claim", "ll97_penalty_screening_claim"]
                if is_nyc_context
                else ["compliance_screening_claim"]
            ),
        )
    rule_family = ""
    for row in compliance_case.get("rule_family_record", []) if isinstance(compliance_case.get("rule_family_record", []), list) else []:
        name = str(row.get("rule_family_name", "")).strip()
        if name:
            rule_family = name
            break
    if "applicable_rule_family" in records and rule_family:
        posture = str(compliance_case.get("applicability_state", ""))
        level = EvidenceMaturityLevel.L1
        if posture in {"trigger_partially_supported", "applicability_likely", "applicability_confirmed_publicly"}:
            level = EvidenceMaturityLevel.L2
        records["applicable_rule_family"] = VariableMaturityRecord(
            variable_name="applicable_rule_family",
            variable_family="regulatory",
            value=rule_family,
            maturity_level=level,
            evidence_source="motor_012.compliance_applicability_case.rule_family_record",
            source_scope=SourceScope.JURISDICTION_LEVEL,
            authority_score=SourceAuthority.HIGH,
            recency=RecencyState.CURRENT,
            uncertainty_reason="Rule family is screened from public jurisdiction and applicability context, not legal closure.",
            allowed_outputs=_allowed_outputs_for_level("applicable_rule_family", level),
            prohibited_outputs=_prohibited_outputs_for_level("applicable_rule_family", level),
            upgrade_condition="Confirm rule trigger fields and current regulated filing.",
            downgrade_condition="Jurisdiction or asset-class mismatch.",
            decisions_unlocked=["compliance screening"] if level >= EvidenceMaturityLevel.L1 else [],
            dependent_claims=(
                ["compliance_screening_claim", "ll97_penalty_screening_claim"]
                if is_nyc_context
                else ["compliance_screening_claim"]
            ),
        )
    if "trigger_fields" in records:
        trigger_fields = compliance_case.get("trigger_field_register", [])
        observed = [row for row in trigger_fields if str(row.get("field_state", "")).lower() == "observed"]
        if observed:
            level = EvidenceMaturityLevel.L2 if len(observed) >= 2 else EvidenceMaturityLevel.L1
            records["trigger_fields"] = VariableMaturityRecord(
                variable_name="trigger_fields",
                variable_family="regulatory",
                value=[row.get("field_name", "") for row in observed],
                maturity_level=level,
                evidence_source="motor_012.compliance_applicability_case.trigger_field_register",
                source_scope=SourceScope.ASSET_LEVEL,
                authority_score=SourceAuthority.MEDIUM,
                recency=RecencyState.CURRENT,
                uncertainty_reason="Trigger fields are partially public and still require local filing hardening.",
                allowed_outputs=_allowed_outputs_for_level("trigger_fields", level),
                prohibited_outputs=_prohibited_outputs_for_level("trigger_fields", level),
                upgrade_condition="Add measured filing-backed trigger values.",
                downgrade_condition="Trigger values prove inapplicable or stale.",
                decisions_unlocked=["screening"] if level >= EvidenceMaturityLevel.L1 else [],
                dependent_claims=["compliance_screening_claim"],
            )
    if "compliance_status" in records:
        posture = str(compliance_case.get("compliance_posture_state", "")).strip()
        if posture:
            if posture == "trigger_plausible":
                level = EvidenceMaturityLevel.L1
            elif posture in {"compliance_open", "applicability_likely", "covered_building_pathway_observed"}:
                level = EvidenceMaturityLevel.L2
            else:
                level = EvidenceMaturityLevel.L1
            records["compliance_status"] = VariableMaturityRecord(
                variable_name="compliance_status",
                variable_family="regulatory",
                value=posture,
                maturity_level=level,
                evidence_source="motor_012.compliance_applicability_case.compliance_posture_state",
                source_scope=SourceScope.DERIVED_INTERNAL,
                authority_score=SourceAuthority.MEDIUM,
                recency=RecencyState.CURRENT,
                uncertainty_reason="Compliance posture is a bounded screening output until official filing evidence exists.",
                allowed_outputs=_allowed_outputs_for_level("compliance_status", level),
                prohibited_outputs=_prohibited_outputs_for_level("compliance_status", level),
                upgrade_condition="Add filing-backed compliance evidence and verified trigger values.",
                downgrade_condition="Loss of jurisdictional fit or filing contradiction.",
                decisions_unlocked=["compliance screening"] if level >= EvidenceMaturityLevel.L1 else [],
                dependent_claims=["compliance_screening_claim", "compliance_closure_claim"],
            )


def _overlay_nyc_dataset_records(
    records: dict[str, VariableMaturityRecord],
    dataset_coverage_register: list[dict[str, Any]],
    compliance_case: dict[str, Any],
) -> None:
    dataset_status = {
        str(row.get("dataset_key", "")).strip(): str(row.get("status", "")).strip().lower()
        for row in dataset_coverage_register
        if isinstance(row, dict)
    }

    gfa_record = records.get("GFA")
    if gfa_record and _has_observed_value(gfa_record) and _source_matches(gfa_record, "nyc_pluto", "pluto", "nyc_dof_property_record"):
        records["GFA"] = _replace_record_level(
            gfa_record,
            level=EvidenceMaturityLevel.L3,
            authority_score=SourceAuthority.HIGH,
            source_scope=SourceScope.ASSET_LEVEL,
            uncertainty_reason="GFA is supported by NYC PLUTO / property-record evidence.",
            decisions_unlocked=["compliance screening", "numeric EUI support"],
        )

    for variable_name in ("EUI", "emissions"):
        record = records.get(variable_name)
        if record and _has_observed_value(record) and _source_matches(record, "nyc_ll84", "ll84", "energy benchmarking"):
            records[variable_name] = _replace_record_level(
                record,
                level=EvidenceMaturityLevel.L3,
                authority_score=SourceAuthority.HIGH,
                source_scope=SourceScope.ASSET_LEVEL,
                uncertainty_reason="Variable is supported by NYC LL84 public asset-level disclosure.",
                decisions_unlocked=["baseline screening", "regulatory screening"] if variable_name != "compliance_filing" else ["benchmarking filing observed"],
            )

    compliance_record = records.get("compliance_filing")
    if compliance_record and _has_observed_value(compliance_record) and _source_matches(
        compliance_record,
        "nyc_ll84",
        "ll84",
        "energy benchmarking",
        "nyc_ll97_covered_buildings_list",
        "cbl26",
    ):
        records["compliance_filing"] = _replace_record_level(
            compliance_record,
            level=EvidenceMaturityLevel.L2,
            authority_score=SourceAuthority.HIGH,
            source_scope=SourceScope.ASSET_LEVEL,
            uncertainty_reason=(
                "Official NYC LL97 covered-building pathway context and LL84 public disclosure are observed, but they do not by themselves prove a certified LL97 compliance filing or compliance closure."
            ),
            decisions_unlocked=[
                "covered-building pathway observed",
                "benchmarking filing observed",
                "regulatory screening",
            ],
        )
    public_filing_basis = _screening_basis_row(compliance_case, "ll97_public_filing_artifact")
    if (
        compliance_record
        and _has_observed_value(compliance_record)
        and dataset_status.get("nyc_ll97_public_filing_artifact") == "accepted"
        and public_filing_basis
        and _source_matches(
            compliance_record,
            "nyc_ll97_public_filing_candidate",
            "article_321_submission_candidate",
            "ll97_filing_report_candidate",
            "beam_export_candidate",
            "public ll97 filing artifact observed",
        )
    ):
        records["compliance_filing"] = _replace_record_level(
            compliance_record,
            level=EvidenceMaturityLevel.L3,
            authority_score=SourceAuthority.HIGH,
            source_scope=SourceScope.ASSET_LEVEL,
            uncertainty_reason=(
                "A public asset-specific LL97 filing artifact is observed from owner or authority source, but filing scope, period, and result still require review before compliance closure."
            ),
            decisions_unlocked=[
                "preliminary compliance path",
                "filing-backed validation path",
                "regulatory screening",
            ],
        )

    hvac_record = records.get("HVAC_type")
    if hvac_record and _has_observed_value(hvac_record) and _source_matches(hvac_record, "nyc_dob_permits", "dob", "permit clue"):
        records["HVAC_type"] = _replace_record_level(
            hvac_record,
            level=EvidenceMaturityLevel.L2,
            authority_score=SourceAuthority.HIGH,
            source_scope=SourceScope.ASSET_LEVEL,
            uncertainty_reason="HVAC basis is inferred from official NYC DOB permit clues, not field-verified equipment inventory.",
            decisions_unlocked=["measure family screening"],
        )

    if dataset_status.get("nyc_ll97_emissions") in {"screened", "accepted"}:
        rule_family_record = records.get("applicable_rule_family")
        if rule_family_record and _has_observed_value(rule_family_record):
            records["applicable_rule_family"] = _replace_record_level(
                rule_family_record,
                level=EvidenceMaturityLevel.L3,
                evidence_source="nyc_ll97_rule_screening",
                source_scope=SourceScope.JURISDICTION_LEVEL,
                authority_score=SourceAuthority.HIGH,
                uncertainty_reason=(
                    "NYC LL97 rule-family applicability is explicitly confirmed at the jurisdiction level; covered-building pathway and filing closure still require local confirmation."
                ),
                decisions_unlocked=["regulatory screening", "penalty scenario support"],
            )

        gfa_record = records.get("GFA")
        regulated_floor_area_record = records.get("regulated_floor_area")
        regulated_floor_area_basis = _screening_basis_row(compliance_case, "regulated_floor_area_basis")
        if regulated_floor_area_record and gfa_record and _has_observed_value(gfa_record):
            regulated_value = regulated_floor_area_basis.get("basis_value") or gfa_record.value
            records["regulated_floor_area"] = _replace_record_level(
                regulated_floor_area_record,
                level=min(gfa_record.maturity_level, EvidenceMaturityLevel.L3),
                value=regulated_value,
                evidence_source=f"{gfa_record.evidence_source} + motor_012.compliance_applicability_case.screening_basis_register",
                source_scope=SourceScope.DERIVED_INTERNAL,
                authority_score=gfa_record.authority_score,
                uncertainty_reason=(
                    "Regulated floor area currently uses public whole-building gross floor area as the LL97 screening basis. "
                    "BIN-specific pathway, exception, or dispute outcomes may still narrow the final regulated scope."
                ),
                decisions_unlocked=["LL97 screening", "penalty scenario support"],
            )

        ll97_period_basis = _screening_basis_row(compliance_case, "ll97_compliance_period")
        ll97_penalty_basis = _screening_basis_row(compliance_case, "ll97_penalty_rate")
        for variable_name, value, reason in (
            (
                "benchmarking_requirement",
                "Annual LL84 benchmarking disclosure required for covered buildings.",
                "NYC public rule family and benchmarking regime are strongly known.",
            ),
            (
                "penalty_rate",
                f"{ll97_penalty_basis.get('basis_value', 268)} USD/tCO2e over annual emissions limit",
                "Penalty-rate basis is public jurisdictional evidence for LL97 Article 320 screening, not a local penalty determination.",
            ),
            (
                "compliance_period",
                f"{ll97_period_basis.get('basis_value', '2024-2029')} Article 320 screening period",
                "Compliance period is publicly defined for NYC LL97 screening; building-specific pathway should still be checked against the Covered Buildings List.",
            ),
        ):
            record = records.get(variable_name)
            if record:
                records[variable_name] = _replace_record_level(
                    record,
                    level=EvidenceMaturityLevel.L3,
                    value=value,
                    evidence_source="nyc_ll97_rule_screening",
                    source_scope=SourceScope.JURISDICTION_LEVEL,
                    authority_score=SourceAuthority.HIGH,
                    uncertainty_reason=reason,
                    decisions_unlocked=["regulatory screening", "penalty scenario support"],
                )


def _derive_variable_records(inputs: dict[str, Any]) -> tuple[list[VariableMaturityRecord], list[dict[str, Any]]]:
    m07 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
    m12 = inputs.get("motor_012", {}) if isinstance(inputs.get("motor_012", {}), dict) else {}
    m28 = inputs.get("motor_028", {}) if isinstance(inputs.get("motor_028", {}), dict) else {}
    target_definition = m07.get("target_definition_contract") or inputs.get("__runtime__", {}).get("target_definition", {}) or {}
    target_classification = m07.get("target_classification_object", {})
    compliance_case = m12.get("compliance_applicability_case", {}) if isinstance(m12.get("compliance_applicability_case", {}), dict) else {}
    source_register = list(m28.get("source_register", []) or [])
    field_rows = _build_field_row_map(list(m12.get("asset_field_register", []) or []))
    explicit_dataset_coverage = list(
        m28.get("dataset_coverage_register", []) or m12.get("dataset_coverage_register", []) or []
    )

    records: dict[str, VariableMaturityRecord] = {name: _build_base_record(name) for name in VARIABLE_CATALOG}
    for variable_name, row in field_rows.items():
        if variable_name in records:
            records[variable_name] = _build_record_from_field(variable_name, row)

    dataset_coverage_register = _explicit_dataset_coverage_register(target_definition, explicit_dataset_coverage)
    if not dataset_coverage_register:
        dataset_coverage_register = _dataset_coverage_register(target_definition, source_register)
    _overlay_identity_and_regulatory_records(
        records,
        target_definition,
        target_classification,
        compliance_case,
        dataset_coverage_register,
    )
    _overlay_nyc_dataset_records(records, dataset_coverage_register, compliance_case)

    current_levels = {name: record.maturity_level for name, record in records.items()}
    for variable_name, record in list(records.items()):
        if record.variable_family == "finance" or record.source_scope == SourceScope.DERIVED_INTERNAL:
            bottleneck, dependencies = derive_dependency_bottleneck(variable_name, current_levels)
            if dependencies:
                has_custom_observed_basis = _has_observed_value(record) and not str(record.evidence_source).startswith("not_observed::")
                level = min(record.maturity_level, bottleneck) if has_custom_observed_basis else bottleneck
                reason = (
                    f"{record.uncertainty_reason} Derived variable remains capped by the weakest required dependency."
                    if has_custom_observed_basis
                    else "Derived variable capped by the weakest required dependency."
                )
                records[variable_name] = VariableMaturityRecord(
                    variable_name=record.variable_name,
                    variable_family=record.variable_family,
                    value=record.value if record.value != "NOT_OBSERVED" else record.value,
                    maturity_level=level,
                    evidence_source=record.evidence_source if record.evidence_source != f"not_observed::{variable_name}" else "derived_dependency_rule",
                    source_scope=SourceScope.DERIVED_INTERNAL,
                    authority_score=SourceAuthority.MEDIUM if level >= EvidenceMaturityLevel.L1 else SourceAuthority.UNKNOWN,
                    recency=RecencyState.CURRENT if level >= EvidenceMaturityLevel.L1 else RecencyState.UNKNOWN,
                    uncertainty_reason=reason,
                    allowed_outputs=_allowed_outputs_for_level(variable_name, level),
                    prohibited_outputs=_prohibited_outputs_for_level(variable_name, level),
                    upgrade_condition=f"Upgrade weakest dependency among: {', '.join(dependencies)}.",
                    downgrade_condition="Any supporting dependency degrades or conflicts.",
                    decisions_unlocked=record.decisions_unlocked if has_custom_observed_basis else [],
                    dependent_claims=record.dependent_claims if has_custom_observed_basis else [],
                )
                current_levels[variable_name] = level

    return list(records.values()), dataset_coverage_register


def _claim_permissions(
    variable_records: list[VariableMaturityRecord],
    target_definition: dict[str, Any],
    dataset_coverage_register: list[dict[str, Any]],
) -> list[ClaimPermissionRecord]:
    levels = {record.variable_name: record.maturity_level for record in variable_records}
    permissions: list[ClaimPermissionRecord] = []
    is_nyc_context = _is_nyc_context(target_definition, dataset_coverage_register)
    strict_prohibition_if_unmet = {
        "compliance_closure_claim",
        "process_redesign_recommendation_claim",
    }
    for claim_name, template in CLAIM_TEMPLATES.items():
        if claim_name == "ll97_penalty_screening_claim" and not is_nyc_context:
            continue
        unmet = []
        unmet_l0 = []
        for variable_name, minimum in template.minimum_maturity_by_variable.items():
            current = levels.get(variable_name, EvidenceMaturityLevel.L0)
            if current < minimum:
                unmet.append(f"{variable_name}={current.code}<{minimum.code}")
                if current == EvidenceMaturityLevel.L0:
                    unmet_l0.append(variable_name)
        if not unmet:
            state = PermissionState.ALLOWED
            reason = ""
        elif claim_name in strict_prohibition_if_unmet:
            state = PermissionState.PROHIBITED
            reason = "Claim remains prohibited until all required variables reach the minimum maturity: " + ", ".join(unmet)
        elif unmet_l0:
            state = PermissionState.PROHIBITED
            reason = "Critical variables remain at Level 0: " + ", ".join(unmet_l0)
        else:
            state = PermissionState.CONDITIONAL
            reason = "Required variables are present but below the minimum maturity: " + ", ".join(unmet)
        permissions.append(
            ClaimPermissionRecord(
                claim_name=claim_name,
                required_variables=template.required_variables,
                minimum_maturity_level=template.minimum_maturity_by_variable,
                current_permission=state,
                reason_if_blocked=reason,
                required_evidence=list(template.required_evidence),
                dependency_variables=expand_dependency_variables(template.required_variables),
                upgrade_path=list(template.upgrade_path),
            )
        )
    return permissions


def _decision_permissions(
    variable_records: list[VariableMaturityRecord],
    target_classification: dict[str, Any],
    target_definition: dict[str, Any],
) -> list[DecisionPermissionRecord]:
    levels = {record.variable_name: record.maturity_level for record in variable_records}
    permissions: list[DecisionPermissionRecord] = []
    target_type = str(target_classification.get("target_type", "")).strip()
    target_asset_type = str(target_definition.get("target_type", "")).strip().lower()
    industrial_asset_types = {
        "manufacturing_facility",
        "industrial_facility",
        "warehouse_distribution",
        "warehouse_logistics",
        "oil_gas_downstream_facility",
        "data_center_infrastructure",
        "power_generation_facility",
        "infrastructure_asset",
    }
    for decision_name, template in DECISION_TEMPLATES.items():
        minimum_maturity_by_variable = dict(template.minimum_maturity_by_variable)
        required_variables = list(template.required_variables)
        evidence_pack_focus = list(template.evidence_pack_focus)
        if decision_name == "compliance_investment" and target_asset_type in industrial_asset_types:
            minimum_maturity_by_variable = {
                "jurisdiction": EvidenceMaturityLevel.L3,
                "applicable_rule_family": EvidenceMaturityLevel.L2,
                "emissions": EvidenceMaturityLevel.L2,
                "compliance_filing": EvidenceMaturityLevel.L2,
                "trigger_fields": EvidenceMaturityLevel.L1,
            }
            required_variables = list(minimum_maturity_by_variable.keys())
            evidence_pack_focus = [
                "public permit records",
                "emissions basis",
                "current rule thresholds",
                "filing evidence",
            ]
        unmet = []
        weakest_variable = ""
        weakest_level = EvidenceMaturityLevel.L4
        for variable_name, minimum in minimum_maturity_by_variable.items():
            current = levels.get(variable_name, EvidenceMaturityLevel.L0)
            if current < weakest_level:
                weakest_variable = variable_name
                weakest_level = current
            if current < minimum:
                unmet.append(variable_name)
        if not unmet:
            state = PermissionState.ALLOWED
            allowed_action = template.allowed_actions[0] if template.allowed_actions else "ACT NOW"
            evidence_needed: list[str] = []
        elif weakest_level == EvidenceMaturityLevel.L0:
            state = PermissionState.DEFERRED
            allowed_action = "REQUEST EVIDENCE" if decision_name == "asset_identity_confirmation" or target_type in {"AMBIGUOUS_TARGET", "CORPORATE_HEADQUARTERS", "REGISTERED_AGENT_OR_MAILING_ADDRESS"} else "DEFER"
            evidence_needed = evidence_pack_focus
        else:
            state = PermissionState.CONDITIONAL
            allowed_action = "VALIDATE FIRST" if decision_name != "seller_or_operator_evidence_request" else "ACT NOW"
            evidence_needed = evidence_pack_focus
        permissions.append(
            DecisionPermissionRecord(
                decision_name=decision_name,
                required_variables=required_variables,
                current_variable_bottleneck=weakest_variable or (required_variables[0] if required_variables else ""),
                admissibility_state=state,
                evidence_needed=evidence_needed,
                allowed_action=allowed_action,
            )
        )
    return permissions


def _report_readiness(
    variable_records: list[VariableMaturityRecord],
    missing_evidence_register: list[dict[str, Any]],
    recommended_report_type: str,
    target_classification: dict[str, Any],
    technical_substrate_readiness: str,
    cluster_report_readiness_profile: dict[str, Any],
    target_definition: dict[str, Any],
) -> ReportReadinessRecord:
    levels = {record.variable_name: record.maturity_level for record in variable_records}
    target_type = str(target_classification.get("target_type", "")).strip()
    target_asset_type = str(target_definition.get("target_type", "")).strip().lower()
    cluster_levels = cluster_report_readiness_profile.get("cluster_levels", {}) if isinstance(cluster_report_readiness_profile, dict) else {}
    strong_public_screening_possible = bool(cluster_report_readiness_profile.get("strong_public_screening_possible", False))
    identity_cluster_level = str(cluster_levels.get("identity_cluster", "L0"))
    geometry_cluster_level = str(cluster_levels.get("geometry_size_cluster", "L0"))
    regulatory_cluster_level = str(cluster_levels.get("regulatory_cluster", "L0"))
    systems_cluster_level = str(cluster_levels.get("systems_cluster", "L0"))
    energy_cluster_level = str(cluster_levels.get("fuel_energy_cluster", "L0"))
    operating_cluster_level = str(cluster_levels.get("operating_regime_cluster", "L0"))
    critical_l0 = [name for name in _CRITICAL_REPORT_VARIABLES if levels.get(name, EvidenceMaturityLevel.L0) == EvidenceMaturityLevel.L0]
    critical_l01 = [name for name in _CRITICAL_REPORT_VARIABLES if levels.get(name, EvidenceMaturityLevel.L0) <= EvidenceMaturityLevel.L1]
    minimum_missing = [str(row.get("missing_field", "")).strip() for row in missing_evidence_register if str(row.get("missing_field", "")).strip()]
    next_evidence_pack = [
        str(row.get("minimum_evidence_needed", "") or row.get("why_needed", "") or row.get("missing_field", "")).strip()
        for row in missing_evidence_register[:8]
    ]

    def _bounded_nontechnical_fallback() -> str:
        normalized_recommended = _canonical_report_type_label(recommended_report_type)
        if normalized_recommended and normalized_recommended != "Full Technical Decision Intelligence Report":
            return normalized_recommended
        if (
            strong_public_screening_possible
            and target_asset_type in _SCREENING_BUILDING_TYPES
            and identity_cluster_level == "L3"
            and geometry_cluster_level == "L3"
            and regulatory_cluster_level == "L3"
        ):
            return "Compliance / Investment Screening Brief"
        if target_type == "OPERATING_ASSET" and any(
            level in {"L2", "L3"}
            for level in (
                identity_cluster_level,
                geometry_cluster_level,
                systems_cluster_level,
                energy_cluster_level,
                operating_cluster_level,
            )
        ):
            return "Exploratory Prior Brief"
        return "Decision-Blocked Asset Brief"

    if target_type in {"CORPORATE_HEADQUARTERS", "REGISTERED_AGENT_OR_MAILING_ADDRESS"}:
        return ReportReadinessRecord(
            report_type_allowed=[recommended_report_type or "Entity Address Classification Brief"],
            report_type_prohibited=list(_TECHNICAL_REPORT_TYPES),
            reason="Target classified as entity-address context rather than a bounded operating asset.",
            minimum_evidence_missing=minimum_missing,
            next_evidence_pack=next_evidence_pack,
        )
    if target_type == "AMBIGUOUS_TARGET":
        return ReportReadinessRecord(
            report_type_allowed=[recommended_report_type or "Target Clarification Brief"],
            report_type_prohibited=list(_TECHNICAL_REPORT_TYPES),
            reason="Target remains ambiguous; asset identity is not sufficiently bounded for technical reporting.",
            minimum_evidence_missing=minimum_missing,
            next_evidence_pack=next_evidence_pack,
        )
    if technical_substrate_readiness == "sufficient" and not critical_l0 and target_asset_type in _FULL_TDIR_READY_TYPES:
        return ReportReadinessRecord(
            report_type_allowed=["Full Technical Decision Intelligence Report"],
            report_type_prohibited=["Entity Address Classification Brief", "Target Clarification Brief"],
            reason="Target is an operating asset and critical technical substrate is sufficiently populated.",
            minimum_evidence_missing=minimum_missing,
            next_evidence_pack=next_evidence_pack,
        )
    if (
        target_type == "OPERATING_ASSET"
        and strong_public_screening_possible
        and identity_cluster_level == "L3"
        and geometry_cluster_level == "L3"
        and regulatory_cluster_level == "L3"
    ):
        if target_asset_type in _SCREENING_BUILDING_TYPES:
            return ReportReadinessRecord(
                report_type_allowed=["Compliance / Investment Screening Brief"],
                report_type_prohibited=["Full Technical Decision Intelligence Report"],
                reason=(
                    "Strong public asset-level identity, geometry, and regulatory evidence support screening-grade compliance and investment framing, "
                    "but internal systems, control-boundary, or bill-grade evidence still block verification or ROI closure."
                ),
                minimum_evidence_missing=minimum_missing,
                next_evidence_pack=next_evidence_pack,
            )
        return ReportReadinessRecord(
            report_type_allowed=["Exploratory Prior Brief"],
            report_type_prohibited=["Full Technical Decision Intelligence Report"],
            reason=(
                "Strong public asset-level identity and geometry support exploratory screening, "
                "but operating, systems, or energy-depth evidence still block stronger technical or financial claims."
            ),
            minimum_evidence_missing=minimum_missing,
            next_evidence_pack=next_evidence_pack,
        )
    if technical_substrate_readiness == "partial" and len(critical_l01) <= 2:
        return ReportReadinessRecord(
            report_type_allowed=["Exploratory Prior Brief"],
            report_type_prohibited=["Full Technical Decision Intelligence Report"],
            reason="Target is asset-like but still requires validation across some critical variables.",
            minimum_evidence_missing=minimum_missing,
            next_evidence_pack=next_evidence_pack,
        )
    fallback_report_type = _bounded_nontechnical_fallback()
    return ReportReadinessRecord(
        report_type_allowed=[fallback_report_type],
        report_type_prohibited=["Full Technical Decision Intelligence Report"],
        reason="Critical variable bottlenecks keep the case below normal technical-report maturity.",
        minimum_evidence_missing=minimum_missing,
        next_evidence_pack=next_evidence_pack,
    )


def _fallback_canonical_asset_context_summary(
    cluster_report_readiness_profile: dict[str, Any],
    early_asset_context_readiness: str,
) -> dict[str, Any]:
    cluster_levels = dict(cluster_report_readiness_profile.get("cluster_levels", {}) or {})
    supported_clusters = [
        cluster_name
        for cluster_name in (
            "identity_cluster",
            "boundary_cluster",
            "geometry_size_cluster",
            "vintage_structure_cluster",
            "operating_regime_cluster",
            "fuel_energy_cluster",
            "systems_cluster",
            "control_boundary_cluster",
            "regulatory_cluster",
        )
        if cluster_levels.get(cluster_name) not in {"L0", ""}
    ]
    missing_clusters = [
        cluster_name
        for cluster_name in (
            "identity_cluster",
            "boundary_cluster",
            "geometry_size_cluster",
            "vintage_structure_cluster",
            "operating_regime_cluster",
            "fuel_energy_cluster",
            "systems_cluster",
            "control_boundary_cluster",
            "regulatory_cluster",
        )
        if cluster_name not in supported_clusters
    ]
    screening_supported = bool(cluster_report_readiness_profile.get("strong_public_screening_possible", False))
    canonical_state = "location_only"
    if screening_supported:
        canonical_state = "asset_context_minimal"
    elif "identity_cluster" in supported_clusters:
        canonical_state = "asset_context_insufficient"
    return {
        "early_asset_context_readiness": str(early_asset_context_readiness or "").strip(),
        "canonical_asset_context_state": canonical_state,
        "screening_supported": screening_supported,
        "supported_clusters": supported_clusters,
        "missing_clusters": missing_clusters,
        "cluster_register": [],
        "supported_field_count": 0,
        "supported_field_register": [],
    }


def _canonical_asset_context_summary(
    m12: dict[str, Any],
    cluster_report_readiness_profile: dict[str, Any],
    early_asset_context_readiness: str,
) -> dict[str, Any]:
    summary = dict(m12.get("canonical_asset_context_summary", {}) or {})
    if not summary:
        summary = _fallback_canonical_asset_context_summary(
            cluster_report_readiness_profile,
            early_asset_context_readiness,
        )
    summary["screening_supported"] = bool(
        summary.get("screening_supported", False)
        or cluster_report_readiness_profile.get("strong_public_screening_possible", False)
    )
    summary["cluster_levels"] = dict(cluster_report_readiness_profile.get("cluster_levels", {}) or {})
    summary["weak_or_missing_clusters"] = list(
        cluster_report_readiness_profile.get("weak_or_missing_clusters", []) or []
    )
    return summary


def _build_report_type_classifier_table(
    *,
    target_definition: dict[str, Any],
    report_readiness: ReportReadinessRecord,
    claim_permissions: list[ClaimPermissionRecord],
) -> list[dict[str, Any]]:
    asset_label = (
        str(target_definition.get("target_name", "")).strip()
        or str(target_definition.get("target_label", "")).strip()
        or str(target_definition.get("address_raw", "")).strip()
        or "UNKNOWN ASSET"
    )
    recommended = _canonical_report_type_label((report_readiness.report_type_allowed or ["Decision-Blocked Asset Brief"])[0])
    allowed_claims: list[str] = []
    blocked_claims: list[str] = []
    for record in claim_permissions:
        claim_name = str(record.claim_name or "").strip()
        if not claim_name:
            continue
        if record.current_permission == PermissionState.PROHIBITED:
            blocked_claims.append(claim_name)
            continue
        if record.current_permission == PermissionState.CONDITIONAL:
            allowed_claims.append(f"{claim_name} (conditional)")
            continue
        allowed_claims.append(claim_name)
    return [
        {
            "asset": asset_label,
            "recommended_report_type": recommended,
            "why": str(report_readiness.reason or "").strip(),
            "allowed_claims": allowed_claims,
            "blocked_claims": blocked_claims,
        }
    ]


def _structural_claim_permission_register(
    *,
    target_definition: dict[str, Any],
    canonical_asset_context_summary: dict[str, Any],
    claim_permissions: list[ClaimPermissionRecord],
    dominant_variable_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    structural_financial_exposure_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    target_type = str(target_definition.get("target_type", "")).strip().lower()
    screening_supported = bool(canonical_asset_context_summary.get("screening_supported", False))
    supported_fields = {
        str(row.get("field", "")).strip()
        for row in list(canonical_asset_context_summary.get("supported_field_register", []) or [])
        if str(row.get("field", "")).strip()
    }
    var_map = {
        str(row.get("variable", "")).strip(): row
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
    }
    base_claims = {
        str(record.claim_name).strip(): str(record.current_permission.value if hasattr(record.current_permission, "value") else record.current_permission).strip()
        for record in claim_permissions
    }

    def _var_state(name: str) -> str:
        return str(var_map.get(name, {}).get("evidence_state", "NOT_OBSERVED")).strip()

    return [
        {
            "claim": "public_asset_identity_claim",
            "permission": "allowed" if screening_supported or "address" in supported_fields else "conditional",
            "evidence_required": ["asset-level identity anchors", "address", "site / parcel reference"],
            "current_evidence": "Strong public identity support." if screening_supported else "Identity partially bounded but still needs stronger asset-level anchors.",
            "allowed_language": "Public records support bounded asset identity or screening posture.",
            "forbidden_language": "Full technical certainty about the operating substrate.",
        },
        {
            "claim": "operational_boundary_claim",
            "permission": "allowed" if _var_state("owner_control_boundary") == "OBSERVED_FACT" else "conditional",
            "evidence_required": ["metering topology", "responsibility / control boundary evidence"],
            "current_evidence": f"owner_control_boundary={_var_state('owner_control_boundary') or 'NOT_OBSERVED'}",
            "allowed_language": "The control boundary can be discussed as observed or conditional, never assumed closed.",
            "forbidden_language": "The owner fully controls the value boundary unless observed.",
        },
        {
            "claim": "process_driver_claim",
            "permission": (
                "hypothesis_only"
                if target_type == "manufacturing_facility" and _var_state("throughput") in {"CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "OBSERVED_FACT"}
                else "conditional" if target_type == "commercial_building" else "prohibited"
            ),
            "evidence_required": ["process map or system topology", "dominant-load evidence"],
            "current_evidence": "Structural driver lane active." if dominant_variable_register else "No structural driver evidence yet.",
            "allowed_language": "Process or system drivers may be hypothesized conditionally.",
            "forbidden_language": "Closed process-driver truth without asset-specific support.",
        },
        {
            "claim": "energy_baseline_claim",
            "permission": (
                "allowed" if _var_state("utility_baseline") == "OBSERVED_FACT"
                else "screening_only" if "current_EUI" in supported_fields or screening_supported
                else "prohibited"
            ),
            "evidence_required": ["utility bills", "interval data or public benchmarking context", "scale basis"],
            "current_evidence": "Public baseline context available." if screening_supported else "No bounded baseline yet.",
            "allowed_language": "Screening-grade baseline framing with explicit caveats.",
            "forbidden_language": "Verification-grade baseline or savings closure.",
        },
        {
            "claim": "energy_savings_claim",
            "permission": "prohibited",
            "evidence_required": ["control boundary", "system inventory", "bill-grade baseline", "measure basis"],
            "current_evidence": "Structural lane does not close savings claims.",
            "allowed_language": "Only downside or conditional hypothesis framing.",
            "forbidden_language": "Savings claim, guaranteed savings, hard underwriting upside.",
        },
        {
            "claim": "compliance_screening_claim",
            "permission": (
                "allowed" if base_claims.get("compliance_screening_claim") == "allowed"
                else "screening_only" if screening_supported
                else "conditional"
            ),
            "evidence_required": ["jurisdiction", "rule-family trigger evidence", "public filing or dataset support"],
            "current_evidence": "Public screening support observed." if screening_supported else "Partial screening support only.",
            "allowed_language": "Compliance screening or bounded exposure framing.",
            "forbidden_language": "Compliance closure or final legal posture.",
        },
        {
            "claim": "compliance_closure_claim",
            "permission": "allowed" if base_claims.get("compliance_closure_claim") == "allowed" else "prohibited",
            "evidence_required": ["official filing", "validated baseline", "filing-grade status evidence"],
            "current_evidence": "No closure support unless the sovereign claim engine already allowed it.",
            "allowed_language": "Only filing-backed closure.",
            "forbidden_language": "Closure by screening or archetype.",
        },
        {
            "claim": "financial_exposure_claim",
            "permission": "allowed" if structural_financial_exposure_register else "prohibited",
            "evidence_required": ["structural assumptions", "evidence-state framing", "downside-if-wrong path"],
            "current_evidence": "Structural financial exposure register present." if structural_financial_exposure_register else "No structural financial exposure output.",
            "allowed_language": "Downside, value of information, capital-at-risk narrative.",
            "forbidden_language": "Closed ROI or bankability.",
        },
        {
            "claim": "ROI_claim",
            "permission": "prohibited",
            "evidence_required": ["finance-grade baseline", "CAPEX", "control boundary", "measure and tariff closure"],
            "current_evidence": "Structural lane deliberately keeps ROI closed.",
            "allowed_language": "No ROI language unless sovereign ROI claims are separately allowed downstream.",
            "forbidden_language": "ROI, IRR, NPV, payback, bankability.",
        },
        {
            "claim": "redesign_hypothesis_claim",
            "permission": "hypothesis_only" if conditional_redesign_register else "prohibited",
            "evidence_required": ["dominant variables", "cross-layer conflicts", "reframed problem"],
            "current_evidence": "Conditional redesign register present." if conditional_redesign_register else "No redesign hypothesis yet.",
            "allowed_language": "Conditional redesign hypothesis.",
            "forbidden_language": "Final redesign recommendation.",
        },
        {
            "claim": "redesign_recommendation_claim",
            "permission": "prohibited",
            "evidence_required": ["verified redesign basis", "implementation-grade evidence", "closed action path"],
            "current_evidence": "Structural lane does not emit final redesign recommendations.",
            "allowed_language": "None beyond hypothesis framing.",
            "forbidden_language": "Recommendation, final design choice, implementation closure.",
        },
        {
            "claim": "peer_comparison_claim",
            "permission": "hypothesis_only" if competitive_comparison_register else "prohibited",
            "evidence_required": ["bounded peer context", "evidence_state on comparison"],
            "current_evidence": "Competitive comparison register present." if competitive_comparison_register else "No bounded peer comparison yet.",
            "allowed_language": "Conditional or archetypal peer comparison.",
            "forbidden_language": "Peer superiority presented as observed fact without evidence state.",
        },
        {
            "claim": "competitive_advantage_claim",
            "permission": "prohibited",
            "evidence_required": ["observed peer advantage", "transferability evidence", "subject-vs-peer structural delta"],
            "current_evidence": "Current lane supports comparison, not closed competitive advantage claims.",
            "allowed_language": "Possible or conditional structural advantage only.",
            "forbidden_language": "Definitive competitive superiority.",
        },
        {
            "claim": "TAD_action_claim",
            "permission": "allowed" if cross_layer_conflict_register or conditional_redesign_register else "conditional",
            "evidence_required": ["dominant variables", "conflicts", "evidence discrimination path"],
            "current_evidence": "Structural action lane is populated." if (cross_layer_conflict_register or conditional_redesign_register) else "Structural action basis remains partial.",
            "allowed_language": "Action priority, compare-to-peers, redesign-hypothesis, or do-not-model-yet posture.",
            "forbidden_language": "Action posture disconnected from evidence state or claim permissions.",
        },
    ]


def _permission_string(value: Any) -> str:
    if hasattr(value, "value"):
        return str(value.value).strip()
    return str(value or "").strip()


def _claim_contract_evidence_state(permission: str) -> str:
    normalized = str(permission or "").strip().lower()
    if normalized == "allowed":
        return "OBSERVED_FACT"
    if normalized in {"conditional", "screening_only", "hypothesis_only"}:
        return "CONDITIONAL_HYPOTHESIS"
    return "INADMISSIBLE_CLAIM"


def _legacy_claim_contract_register(
    *,
    claim_permissions: list[ClaimPermissionRecord],
    variable_records: list[VariableMaturityRecord],
) -> list[dict[str, Any]]:
    variable_map = {record.variable_name: record for record in variable_records}
    rows: list[dict[str, Any]] = []
    for record in claim_permissions:
        claim_name = str(record.claim_name).strip()
        if not claim_name:
            continue
        template = CLAIM_TEMPLATES.get(claim_name)
        permission = _permission_string(record.current_permission)
        supporting_sources: list[str] = []
        for variable_name in list(record.required_variables or []) + list(record.dependency_variables or []):
            var_record = variable_map.get(variable_name)
            if not var_record:
                continue
            source = str(var_record.evidence_source or "").strip()
            if source and source not in supporting_sources:
                supporting_sources.append(source)
        if not supporting_sources:
            supporting_sources = ["motor_034.variable_maturity_register"]
        rows.append(
            {
                "claim_id": claim_name,
                "claim_family": "legacy_maturity_lane",
                "statement": str(template.description if template else claim_name.replace("_", " ")).strip(),
                "permission": permission,
                "evidence_state": _claim_contract_evidence_state(permission),
                "supporting_sources": supporting_sources,
                "assumptions": [
                    "Required variables must remain at or above their minimum maturity threshold.",
                    (
                        "Dependency variables must remain materially consistent: "
                        + ", ".join(record.dependency_variables)
                    ) if list(record.dependency_variables or []) else "No additional dependency variables are required beyond the primary maturity gate.",
                ],
                "falsification_condition": "Any required variable drops below its minimum maturity threshold, or stronger contradictory asset-level evidence invalidates the current basis.",
                "minimum_evidence_required": list(record.required_evidence or []),
                "allowed_use": list(template.allowed_outputs if template else []),
                "prohibited_use": list(template.prohibited_outputs if template else []),
                "current_evidence_summary": (
                    "Minimum maturity thresholds currently met."
                    if permission == "allowed"
                    else str(record.reason_if_blocked or "Evidence threshold not fully met.").strip()
                ),
            }
        )
    return rows


def _structural_claim_contract_register(
    *,
    structural_claim_permission_register: list[dict[str, Any]],
    system_abstraction: dict[str, Any],
    structural_financial_exposure_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    abstraction_source_map = {
        "public_asset_identity_claim": ["asset_type", "evidence_maturity"],
        "operational_boundary_claim": ["control_structure", "constraint_structure"],
        "process_driver_claim": ["dominant_process_type", "dominant_physical_drivers", "dominant_operational_drivers"],
        "energy_baseline_claim": ["dominant_physical_drivers", "economic_driver"],
        "compliance_screening_claim": ["regulatory_exposure", "constraint_structure"],
        "compliance_closure_claim": ["regulatory_exposure"],
        "financial_exposure_claim": ["economic_driver", "control_structure"],
        "redesign_hypothesis_claim": ["dominant_operational_drivers", "constraint_structure"],
        "redesign_recommendation_claim": ["dominant_operational_drivers"],
        "peer_comparison_claim": ["asset_type", "economic_driver"],
        "competitive_advantage_claim": ["economic_driver"],
        "TAD_action_claim": ["constraint_structure", "economic_driver"],
    }
    extra_register_sources = {
        "financial_exposure_claim": ["motor_045.structural_financial_exposure_register"] if structural_financial_exposure_register else [],
        "redesign_hypothesis_claim": ["motor_044.conditional_redesign_register"] if conditional_redesign_register else [],
        "redesign_recommendation_claim": ["motor_044.conditional_redesign_register"] if conditional_redesign_register else [],
        "peer_comparison_claim": ["motor_043.competitive_comparison_register"] if competitive_comparison_register else [],
        "competitive_advantage_claim": ["motor_043.competitive_comparison_register"] if competitive_comparison_register else [],
        "TAD_action_claim": (
            ["motor_040.cross_layer_conflict_register"] if cross_layer_conflict_register else []
        ) + (
            ["motor_046.minimum_evidence_for_discrimination_register"] if minimum_evidence_for_discrimination_register else []
        ),
    }
    claim_statement_map = {
        "public_asset_identity_claim": "Public records can support bounded asset identity, but not automatically the full operating substrate.",
        "operational_boundary_claim": "Operational boundary can only be treated as closed when owner or operator control is directly evidenced.",
        "process_driver_claim": "Process or system drivers can be framed only as observed or conditional, never assumed closed from archetype alone.",
        "energy_baseline_claim": "Energy baseline can support screening or stronger use only to the degree that the baseline itself is evidenced.",
        "energy_savings_claim": "Energy savings remain inadmissible until control, baseline, systems, and measure basis are sufficiently evidenced.",
        "compliance_screening_claim": "Compliance screening can be used when jurisdiction and trigger logic are evidenced, without implying closure.",
        "compliance_closure_claim": "Compliance closure requires filing-grade evidence and cannot be inferred from screening support.",
        "financial_exposure_claim": "Financial exposure under uncertainty can be framed from structural downside without inventing ROI.",
        "ROI_claim": "ROI-style claims remain prohibited unless a separate finance-grade lane closes the evidence threshold.",
        "redesign_hypothesis_claim": "Redesign can be proposed only as a conditional hypothesis tied to evidence and falsification.",
        "redesign_recommendation_claim": "Final redesign recommendations remain prohibited without implementation-grade evidence.",
        "peer_comparison_claim": "Peer comparison must remain conditional or explicitly evidence-stated.",
        "competitive_advantage_claim": "Competitive advantage cannot be presented as observed fact without evidence-stated comparison support.",
        "TAD_action_claim": "TAD actions are admissible only when they remain linked to structural evidence, contradictions, or discrimination paths.",
    }
    rows: list[dict[str, Any]] = []
    for row in structural_claim_permission_register:
        claim_name = str(row.get("claim", "")).strip()
        if not claim_name:
            continue
        permission = str(row.get("permission", "")).strip()
        supporting_sources: list[str] = []
        for field_name in abstraction_source_map.get(claim_name, []):
            source_ids = list((system_abstraction.get(field_name, {}) or {}).get("supporting_sources", []) or [])
            for source_id in source_ids:
                sid = str(source_id).strip()
                if sid and sid not in supporting_sources:
                    supporting_sources.append(sid)
        for source_id in extra_register_sources.get(claim_name, []):
            sid = str(source_id).strip()
            if sid and sid not in supporting_sources:
                supporting_sources.append(sid)
        if not supporting_sources:
            supporting_sources = ["motor_034.structural_claim_permission_register"]
        rows.append(
            {
                "claim_id": claim_name,
                "claim_family": "structural_intelligence_lane",
                "statement": claim_statement_map.get(claim_name, claim_name.replace("_", " ")),
                "permission": permission,
                "evidence_state": _claim_contract_evidence_state(permission),
                "supporting_sources": supporting_sources,
                "assumptions": [
                    "Archetypal priors must never be rendered as observed facts.",
                    str(row.get("current_evidence", "") or "Current evidence remains bounded and must stay tied to its evidence state.").strip(),
                ],
                "falsification_condition": "Asset-specific evidence destroys the current framing, closes the claim more strongly, or proves that the current conditional pathway is wrong.",
                "minimum_evidence_required": list(row.get("evidence_required", []) or []),
                "allowed_use": [str(row.get("allowed_language", "")).strip()] if str(row.get("allowed_language", "")).strip() else [],
                "prohibited_use": [str(row.get("forbidden_language", "")).strip()] if str(row.get("forbidden_language", "")).strip() else [],
                "current_evidence_summary": str(row.get("current_evidence", "")).strip(),
            }
        )
    return rows


def _claim_contract_register(
    *,
    claim_permissions: list[ClaimPermissionRecord],
    variable_records: list[VariableMaturityRecord],
    structural_claim_permission_register: list[dict[str, Any]],
    system_abstraction: dict[str, Any],
    structural_financial_exposure_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    return _legacy_claim_contract_register(
        claim_permissions=claim_permissions,
        variable_records=variable_records,
    ) + _structural_claim_contract_register(
        structural_claim_permission_register=structural_claim_permission_register,
        system_abstraction=system_abstraction,
        structural_financial_exposure_register=structural_financial_exposure_register,
        competitive_comparison_register=competitive_comparison_register,
        conditional_redesign_register=conditional_redesign_register,
        minimum_evidence_for_discrimination_register=minimum_evidence_for_discrimination_register,
        cross_layer_conflict_register=cross_layer_conflict_register,
    )


def _structural_output_mode_classifier_table(
    *,
    target_definition: dict[str, Any],
    report_readiness: ReportReadinessRecord,
    structural_claim_permission_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    dominant_variable_register: list[dict[str, Any]],
    problem_framing_register: list[dict[str, Any]],
    structural_benchmark_register: list[dict[str, Any]],
    competitive_comparison_register: list[dict[str, Any]],
    conditional_redesign_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    asset_label = (
        str(target_definition.get("target_name", "")).strip()
        or str(target_definition.get("target_label", "")).strip()
        or str(target_definition.get("address_raw", "")).strip()
        or "UNKNOWN ASSET"
    )
    claim_map = {
        str(row.get("claim", "")).strip(): str(row.get("permission", "")).strip()
        for row in structural_claim_permission_register
        if str(row.get("claim", "")).strip()
    }
    primary_types = [str(item).strip() for item in (report_readiness.report_type_allowed or []) if str(item).strip()]
    primary_guard_passed = bool(
        {
            "Decision-Blocked Asset Brief",
            "Exploratory Prior Brief",
            "Compliance / Investment Screening Brief",
            "Full Technical Decision Intelligence Report",
        }
        & set(primary_types)
    )

    def _activation(required_claims: list[str]) -> tuple[str, str]:
        if not primary_guard_passed:
            return (
                "blocked_secondary",
                "Primary report lane is not yet asset-bounded enough to activate structural secondary modes.",
            )
        blocked_claims = [
            claim for claim in required_claims
            if claim_map.get(claim) == "prohibited"
        ]
        if blocked_claims:
            return (
                "blocked_secondary",
                "Linked structural claims remain prohibited: " + ", ".join(blocked_claims),
            )
        return (
            "activated_secondary",
            "Mode is admissible as a secondary structural surface and does not override the primary report type.",
        )

    dominant_signal_count = len(
        [
            row
            for row in dominant_variable_register
            if str(row.get("evidence_state", "")).strip() in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "WEAK_SIGNAL"}
        ]
    )

    modes: list[dict[str, Any]] = []
    if len(cross_layer_conflict_register) >= 2:
        activation_state, activation_reason = _activation(["TAD_action_claim"])
        modes.append({
            "asset": asset_label,
            "recommended_output_mode": "Structural Contradiction Brief",
            "activation_state": activation_state,
            "activation_reason": activation_reason,
            "required_claims": ["TAD_action_claim"],
            "primary_report_type_guard": primary_types,
            "why": "Multiple cross-layer contradictions are active and materially affect interpretation.",
        })
    if conditional_redesign_register:
        activation_state, activation_reason = _activation(["redesign_hypothesis_claim"])
        modes.append({
            "asset": asset_label,
            "recommended_output_mode": "System Redesign Hypothesis Brief",
            "activation_state": activation_state,
            "activation_reason": activation_reason,
            "required_claims": ["redesign_hypothesis_claim"],
            "primary_report_type_guard": primary_types,
            "why": "Conditional redesign hypotheses are present but remain evidence-bounded.",
        })
    if competitive_comparison_register:
        activation_state, activation_reason = _activation(["peer_comparison_claim"])
        modes.append({
            "asset": asset_label,
            "recommended_output_mode": "Competitive Positioning Brief",
            "activation_state": activation_state,
            "activation_reason": activation_reason,
            "required_claims": ["peer_comparison_claim"],
            "primary_report_type_guard": primary_types,
            "why": "Bounded peer or competitive comparison context is available.",
        })
    if minimum_evidence_for_discrimination_register:
        activation_state, activation_reason = _activation(["TAD_action_claim"])
        modes.append({
            "asset": asset_label,
            "recommended_output_mode": "TAD Action Priority Brief",
            "activation_state": activation_state,
            "activation_reason": activation_reason,
            "required_claims": ["TAD_action_claim"],
            "primary_report_type_guard": primary_types,
            "why": "A bounded minimum-evidence discrimination path exists and can drive immediate action priority.",
        })

    for row in modes:
        mode_name = str(row.get("recommended_output_mode", "")).strip()
        activation_state = str(row.get("activation_state", "")).strip()
        promotion_state = "not_eligible_primary"
        promotion_reason = "Mode is not yet eligible for promotion into the primary published output."
        if activation_state != "activated_secondary":
            promotion_reason = "Mode is not active even as a secondary structural surface."
        elif mode_name == "Structural Contradiction Brief":
            if problem_framing_register and dominant_signal_count >= 1:
                promotion_state = "eligible_primary"
                promotion_reason = (
                    "Cross-layer contradictions are materially populated, problem framing is active, "
                    "and at least one dominant variable has non-archetypal support."
                )
            else:
                promotion_reason = (
                    "Cross-layer conflicts exist, but problem framing or dominant-variable support "
                    "is still too thin for primary-mode promotion."
                )
        elif mode_name == "System Redesign Hypothesis Brief":
            redesign_rows = list(conditional_redesign_register or [])
            redesign_rows_ready = bool(redesign_rows) and all(
                list(item.get("next_evidence", []) or [])
                and str(item.get("hypothesis", "")).strip()
                and str(item.get("if_confirmed", "")).strip()
                and str(item.get("if_falsified", "")).strip()
                for item in redesign_rows
            )
            redesign_evidence_ready = any(
                str(item.get("evidence_state", "")).strip() in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "WEAK_SIGNAL"}
                for item in redesign_rows
            )
            if redesign_rows_ready and redesign_evidence_ready:
                promotion_state = "eligible_primary"
                promotion_reason = (
                    "Conditional redesign paths are evidence-bounded and retain explicit falsification and next-evidence contracts."
                )
            else:
                promotion_reason = (
                    "Redesign remains visible as a secondary hypothesis surface, but lacks enough bounded next-evidence structure for primary promotion."
                )
        elif mode_name == "Competitive Positioning Brief":
            has_conditional_peer_frame = any(
                str(item.get("comparison_mode", "")).strip() == "conditional_comparison"
                and str(item.get("evidence_state", "")).strip() in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "WEAK_SIGNAL"}
                for item in competitive_comparison_register
            )
            if has_conditional_peer_frame and structural_benchmark_register:
                promotion_state = "eligible_primary"
                promotion_reason = (
                    "Peer comparison is materially populated and anchored to structural benchmarking rather than archetype-only best practice."
                )
            else:
                promotion_reason = (
                    "Competitive comparison exists, but remains too archetypal or insufficiently benchmark-anchored for primary promotion."
                )
        elif mode_name == "TAD Action Priority Brief":
            if claim_map.get("TAD_action_claim") == "allowed" and minimum_evidence_for_discrimination_register and (
                cross_layer_conflict_register or problem_framing_register
            ):
                promotion_state = "eligible_primary"
                promotion_reason = (
                    "Action-priority logic is supported by structural conflicts/problem framing plus a bounded minimum-evidence discrimination path."
                )
            else:
                promotion_reason = (
                    "Action-priority mode remains secondary until structural action claims and minimum-evidence discrimination are both materially populated."
                )
        row["primary_promotion_state"] = promotion_state
        row["primary_promotion_reason"] = promotion_reason
    return modes


def _structural_output_mode_summary(
    *,
    primary_report_type: str,
    structural_output_mode_classifier_table: list[dict[str, Any]],
) -> dict[str, Any]:
    activated_secondary_modes = [
        str(row.get("recommended_output_mode", "")).strip()
        for row in structural_output_mode_classifier_table
        if str(row.get("activation_state", "")).strip() == "activated_secondary"
        and str(row.get("recommended_output_mode", "")).strip()
    ]
    blocked_secondary_modes = [
        str(row.get("recommended_output_mode", "")).strip()
        for row in structural_output_mode_classifier_table
        if str(row.get("activation_state", "")).strip() == "blocked_secondary"
        and str(row.get("recommended_output_mode", "")).strip()
    ]
    eligible_primary_modes = [
        str(row.get("recommended_output_mode", "")).strip()
        for row in structural_output_mode_classifier_table
        if str(row.get("primary_promotion_state", "")).strip() == "eligible_primary"
        and str(row.get("recommended_output_mode", "")).strip()
    ]
    non_promotable_primary_modes = [
        str(row.get("recommended_output_mode", "")).strip()
        for row in structural_output_mode_classifier_table
        if str(row.get("primary_promotion_state", "")).strip() != "eligible_primary"
        and str(row.get("recommended_output_mode", "")).strip()
    ]
    return {
        "primary_report_type": primary_report_type,
        "activated_secondary_modes": activated_secondary_modes,
        "blocked_secondary_modes": blocked_secondary_modes,
        "policy_note": "Structural output modes are secondary governed surfaces. They cannot override the primary report type or the claim-permission ceiling.",
        "eligible_primary_modes": eligible_primary_modes,
        "non_promotable_primary_modes": non_promotable_primary_modes,
        "leading_primary_promotion_candidate": eligible_primary_modes[0] if eligible_primary_modes else "",
        "primary_promotion_policy_note": (
            "Primary structural promotion remains advisory until the sovereign classifier explicitly elects it. "
            "Eligible modes cannot override the currently published report type without a dedicated promotion gate."
        ),
        "activation_count": len(activated_secondary_modes),
        "blocked_count": len(blocked_secondary_modes),
        "eligible_primary_count": len(eligible_primary_modes),
    }


def _build_report_output_mode_classifier_table(
    *,
    target_definition: dict[str, Any],
    report_readiness: ReportReadinessRecord,
    report_type_classifier_table: list[dict[str, Any]],
    structural_output_mode_classifier_table: list[dict[str, Any]],
    structural_output_mode_summary: dict[str, Any],
    structural_primary_promotion_gate: dict[str, Any],
) -> list[dict[str, Any]]:
    asset_label = (
        str(target_definition.get("target_name", "")).strip()
        or str(target_definition.get("target_label", "")).strip()
        or str(target_definition.get("address_raw", "")).strip()
        or "UNKNOWN ASSET"
    )
    legacy_row = report_type_classifier_table[0] if report_type_classifier_table else {}
    base_visible_mode = str(
        legacy_row.get("recommended_report_type")
        or (report_readiness.report_type_allowed or ["Decision-Blocked Asset Brief"])[0]
    ).strip()
    base_canonical_mode = _canonical_output_mode_label(base_visible_mode)
    override_allowed = bool(structural_primary_promotion_gate.get("override_allowed", False))
    selected_visible_mode = str(
        structural_primary_promotion_gate.get("elected_primary_report_type", "") or base_visible_mode
    ).strip() or base_visible_mode
    selected_canonical_mode = _canonical_output_mode_label(selected_visible_mode)
    requested_structural_mode = str(structural_primary_promotion_gate.get("requested_structural_primary_mode", "") or "").strip()
    request_basis = str(structural_primary_promotion_gate.get("request_basis", "") or "").strip()
    selected_reason = str(structural_primary_promotion_gate.get("reason", "") or str(report_readiness.reason or "") or "").strip()
    default_reasoning_path = str(structural_primary_promotion_gate.get("default_reasoning_path", "") or "legacy_decision_gating_only").strip()
    problem_frame_active = bool(structural_primary_promotion_gate.get("problem_frame_active", False))

    allowed_legacy_modes = {
        _canonical_output_mode_label(str(item).strip())
        for item in list(report_readiness.report_type_allowed or [])
        if str(item).strip()
    }
    prohibited_legacy_modes = {
        _canonical_output_mode_label(str(item).strip())
        for item in list(report_readiness.report_type_prohibited or [])
        if str(item).strip()
    }
    structural_rows = {
        _canonical_output_mode_label(str(row.get("recommended_output_mode", "")).strip()): row
        for row in structural_output_mode_classifier_table
        if str(row.get("recommended_output_mode", "")).strip()
    }
    allowed_claims = list(legacy_row.get("allowed_claims", []) or [])
    blocked_claims = list(legacy_row.get("blocked_claims", []) or [])

    rows: list[dict[str, Any]] = []
    for mode in _CANONICAL_OUTPUT_MODES:
        row: dict[str, Any] = {
            "asset": asset_label,
            "canonical_output_mode": mode,
            "visible_output_mode": selected_visible_mode if mode == selected_canonical_mode else (base_visible_mode if mode == base_canonical_mode else mode),
            "lane": "structural" if mode in _STRUCTURAL_OUTPUT_MODES else "legacy",
            "classification_state": "inactive",
            "selected_for_publication": mode == selected_canonical_mode,
            "primary_eligible": False,
            "request_basis": request_basis if mode in _STRUCTURAL_OUTPUT_MODES else "",
            "requested_structural_primary_mode": requested_structural_mode if mode in _STRUCTURAL_OUTPUT_MODES else "",
            "default_reasoning_path": default_reasoning_path,
            "problem_frame_active": problem_frame_active,
            "selection_basis": selected_reason if mode == selected_canonical_mode else "",
            "why": "",
            "allowed_claims": allowed_claims if mode not in _STRUCTURAL_OUTPUT_MODES else [],
            "blocked_claims": blocked_claims if mode not in _STRUCTURAL_OUTPUT_MODES else [],
            "required_claims": [],
            "activation_state": "inactive",
            "primary_promotion_state": "",
        }
        if mode in _STRUCTURAL_OUTPUT_MODES:
            structural_row = dict(structural_rows.get(mode, {}) or {})
            activation_state = str(structural_row.get("activation_state", "inactive") or "inactive").strip()
            promotion_state = str(structural_row.get("primary_promotion_state", "") or "").strip()
            row.update(
                {
                    "why": str(structural_row.get("why", "") or "").strip(),
                    "required_claims": list(structural_row.get("required_claims", []) or []),
                    "activation_state": activation_state,
                    "primary_promotion_state": promotion_state,
                    "primary_eligible": promotion_state == "eligible_primary",
                }
            )
            if mode == selected_canonical_mode and override_allowed:
                row["classification_state"] = "selected_primary_structural"
            elif promotion_state == "eligible_primary":
                row["classification_state"] = "eligible_primary_structural"
            elif activation_state == "activated_secondary":
                row["classification_state"] = "active_secondary_structural"
            elif activation_state == "blocked_secondary":
                row["classification_state"] = "blocked_structural"
            else:
                row["classification_state"] = "inactive"
        else:
            row["why"] = str(legacy_row.get("why", "") or str(report_readiness.reason or "") or "").strip()
            if mode == selected_canonical_mode and not override_allowed:
                row["classification_state"] = "selected_primary_default"
            elif mode in allowed_legacy_modes:
                row["classification_state"] = "eligible_primary_legacy"
            elif mode in prohibited_legacy_modes:
                row["classification_state"] = "prohibited_legacy"
            else:
                row["classification_state"] = "inactive"
            row["primary_eligible"] = row["classification_state"] in {"selected_primary_default", "eligible_primary_legacy"}
        rows.append(row)
    return rows


def _canonical_problem_frame(
    *,
    target_definition: dict[str, Any],
    archetype_resolution: dict[str, Any],
    problem_framing_register: list[dict[str, Any]],
    cross_layer_conflict_register: list[dict[str, Any]],
    dominant_variable_register: list[dict[str, Any]],
    minimum_evidence_for_discrimination_register: list[dict[str, Any]],
    structural_output_mode_summary: dict[str, Any],
    local_evidence_binding_register: list[dict[str, Any]],
    cross_layer_congruence_register: list[dict[str, Any]],
    invalid_problem_frame_register: list[dict[str, Any]],
) -> dict[str, Any]:
    target_label = (
        str(target_definition.get("target_name", "")).strip()
        or str(target_definition.get("target_label", "")).strip()
        or str(target_definition.get("address_raw", "")).strip()
        or "UNKNOWN ASSET"
    )
    primary_frame = problem_framing_register[0] if problem_framing_register else {}
    primary_conflict = cross_layer_conflict_register[0] if cross_layer_conflict_register else {}
    primary_discrimination = minimum_evidence_for_discrimination_register[0] if minimum_evidence_for_discrimination_register else {}
    primary_congruence_conflict = cross_layer_congruence_register[0] if cross_layer_congruence_register else {}
    primary_invalid_problem = invalid_problem_frame_register[0] if invalid_problem_frame_register else {}
    primary_bound_congruence_claim = _first_bound_congruence_claim(local_evidence_binding_register)
    dominant_variables = [
        str(row.get("variable", "")).strip()
        for row in dominant_variable_register
        if str(row.get("variable", "")).strip()
        and str(row.get("evidence_state", "")).strip() in {"OBSERVED_FACT", "CONDITIONAL_HYPOTHESIS", "ARCHETYPAL_PRIOR", "WEAK_SIGNAL"}
    ][:5]
    structural_modelable = (
        str(archetype_resolution.get("selected_archetype_id", "")).strip()
        != "target_not_yet_structurally_modelable"
    )
    primary_frame_active = bool(primary_frame) and str(primary_frame.get("evidence_state", "")).strip() != "INADMISSIBLE_CLAIM"
    congruence_active = all(
        [
            structural_modelable,
            _has_sufficient_congruence_binding(local_evidence_binding_register),
            bool(primary_congruence_conflict),
            bool(primary_invalid_problem),
            bool(dominant_variables),
            bool(primary_discrimination),
        ]
    )
    structural_active = any(
        [
            primary_frame_active,
            primary_conflict,
            dominant_variables,
            minimum_evidence_for_discrimination_register,
        ]
    ) and structural_modelable
    structural_active = structural_active or congruence_active
    stated_problem = str(primary_frame.get("stated_problem", "")).strip()
    reframed_problem = str(primary_frame.get("reframed_problem", "")).strip()
    dominant_conflict = str(primary_conflict.get("conflict", "")).strip()
    if congruence_active:
        stated_problem = (
            stated_problem
            if primary_frame_active and stated_problem
            else _format_problem_label(primary_invalid_problem.get("apparent_problem"))
        )
        reframed_problem = (
            reframed_problem
            if primary_frame_active and reframed_problem
            else str(primary_invalid_problem.get("what_problem_should_be_tested_instead", "")).strip()
        )
        dominant_conflict = dominant_conflict or str(primary_congruence_conflict.get("contradiction", "")).strip()
    if not structural_modelable:
        evidence_state = "INADMISSIBLE_CLAIM"
    elif primary_frame_active or congruence_active:
        evidence_state = "CONDITIONAL_HYPOTHESIS"
    elif dominant_variables:
        evidence_state = "ARCHETYPAL_PRIOR"
    else:
        evidence_state = "NOT_OBSERVED"
    return {
        "target": target_label,
        "reasoning_path": "structural_first" if structural_active else "legacy_decision_gating_only",
        "problem_frame_active": structural_active,
        "stated_problem": stated_problem,
        "reframed_problem": reframed_problem,
        "dominant_conflict": dominant_conflict,
        "dominant_variables": dominant_variables,
        "minimum_evidence_to_discriminate": str(primary_discrimination.get("minimum_evidence", "")).strip(),
        "minimum_evidence_source": str(primary_discrimination.get("source", "")).strip(),
        "minimum_evidence_unlocks": str(primary_discrimination.get("unlocks", "")).strip(),
        "leading_structural_output_mode": str(structural_output_mode_summary.get("leading_primary_promotion_candidate", "")).strip(),
        "evidence_state": evidence_state,
        "congruence_binding_state": str(primary_bound_congruence_claim.get("current_local_binding_state", "")).strip(),
    }


def _requested_structural_primary_mode(target_definition: dict[str, Any]) -> tuple[str, str]:
    explicit_mode = str(
        target_definition.get("structural_output_mode_request")
        or target_definition.get("requested_output_mode")
        or ""
    ).strip()
    if explicit_mode in {
        "Structural Contradiction Brief",
        "System Redesign Hypothesis Brief",
        "Competitive Positioning Brief",
        "TAD Action Priority Brief",
    }:
        return explicit_mode, "explicit_target_request"

    report_intent = str(target_definition.get("report_intent", "")).strip().lower()
    decision_intent = str(target_definition.get("decision_intent", "")).strip().lower()
    if report_intent == "structural_contradiction_brief" or decision_intent in {
        "structural_contradiction",
        "wrong_problem",
        "problem_reframing",
    }:
        return "Structural Contradiction Brief", "intent_mapping"
    if report_intent == "system_redesign_hypothesis_brief" or decision_intent in {
        "process_change",
        "process_redesign",
        "redesign_hypothesis",
        "retrofit_reframing",
    }:
        return "System Redesign Hypothesis Brief", "intent_mapping"
    if report_intent == "competitive_positioning_brief" or decision_intent in {
        "competitive_positioning",
        "peer_comparison",
        "peer_screening",
    }:
        return "Competitive Positioning Brief", "intent_mapping"
    if report_intent == "tad_action_priority_brief" or decision_intent in {
        "action_priority",
        "action_prioritization",
        "what_to_do_now",
        "evidence_request_priority",
    }:
        return "TAD Action Priority Brief", "intent_mapping"
    return "", ""


def _structural_primary_promotion_gate(
    *,
    target_definition: dict[str, Any],
    report_readiness: ReportReadinessRecord,
    structural_output_mode_classifier_table: list[dict[str, Any]],
    structural_output_mode_summary: dict[str, Any],
    canonical_problem_frame: dict[str, Any],
) -> dict[str, Any]:
    base_primary_report_type = _canonical_report_type_label(
        (report_readiness.report_type_allowed or ["Decision-Blocked Asset Brief"])[0]
    )
    requested_mode, request_basis = _requested_structural_primary_mode(target_definition)
    eligible_primary_modes = [
        str(item).strip()
        for item in list(structural_output_mode_summary.get("eligible_primary_modes", []) or [])
        if str(item).strip()
    ]
    default_reasoning_path = str(canonical_problem_frame.get("reasoning_path", "") or "legacy_decision_gating_only")
    problem_frame_active = bool(canonical_problem_frame.get("problem_frame_active", False))
    default_structural_output_mode = str(
        canonical_problem_frame.get("leading_structural_output_mode", "")
        or structural_output_mode_summary.get("leading_primary_promotion_candidate", "")
        or ""
    ).strip()
    available_modes = {
        str(row.get("recommended_output_mode", "")).strip(): row
        for row in structural_output_mode_classifier_table
        if str(row.get("recommended_output_mode", "")).strip()
    }
    if not requested_mode:
        if default_reasoning_path == "structural_first" and problem_frame_active:
            return {
                "base_primary_report_type": base_primary_report_type,
                "requested_structural_primary_mode": "",
                "request_basis": "",
                "promotion_state": "structural_first_default_active",
                "eligible_primary_modes": eligible_primary_modes,
                "elected_primary_report_type": "",
                "override_allowed": False,
                "default_reasoning_path": default_reasoning_path,
                "problem_frame_active": problem_frame_active,
                "default_structural_output_mode": default_structural_output_mode,
                "reason": (
                    "Structural reasoning is now the default interpretation path for this case, "
                    "but no primary structural output mode was explicitly elected."
                ),
            }
        return {
            "base_primary_report_type": base_primary_report_type,
            "requested_structural_primary_mode": "",
            "request_basis": "",
            "promotion_state": "not_requested",
            "eligible_primary_modes": eligible_primary_modes,
            "elected_primary_report_type": "",
            "override_allowed": False,
            "default_reasoning_path": default_reasoning_path,
            "problem_frame_active": problem_frame_active,
            "default_structural_output_mode": default_structural_output_mode,
            "reason": "No explicit structural primary-mode request was detected in the target intent.",
        }
    if requested_mode not in available_modes:
        return {
            "base_primary_report_type": base_primary_report_type,
            "requested_structural_primary_mode": requested_mode,
            "request_basis": request_basis,
            "promotion_state": "requested_mode_not_available",
            "eligible_primary_modes": eligible_primary_modes,
            "elected_primary_report_type": "",
            "override_allowed": False,
            "default_reasoning_path": default_reasoning_path,
            "problem_frame_active": problem_frame_active,
            "default_structural_output_mode": default_structural_output_mode,
            "reason": "Requested structural primary mode is not materially populated by the current structural lane.",
        }
    if requested_mode not in eligible_primary_modes:
        return {
            "base_primary_report_type": base_primary_report_type,
            "requested_structural_primary_mode": requested_mode,
            "request_basis": request_basis,
            "promotion_state": "requested_but_ineligible",
            "eligible_primary_modes": eligible_primary_modes,
            "elected_primary_report_type": "",
            "override_allowed": False,
            "default_reasoning_path": default_reasoning_path,
            "problem_frame_active": problem_frame_active,
            "default_structural_output_mode": default_structural_output_mode,
            "reason": "Requested structural primary mode is present but not eligible for primary promotion under current evidence discipline.",
        }
    return {
        "base_primary_report_type": base_primary_report_type,
        "requested_structural_primary_mode": requested_mode,
        "request_basis": request_basis,
        "promotion_state": "elected_primary_structural_mode",
        "eligible_primary_modes": eligible_primary_modes,
        "elected_primary_report_type": requested_mode,
        "override_allowed": True,
        "default_reasoning_path": default_reasoning_path,
        "problem_frame_active": problem_frame_active,
        "default_structural_output_mode": default_structural_output_mode,
        "reason": "Structural primary-mode promotion was explicitly requested and passed the governed eligibility gate.",
    }


class Motor034Adapter(BaseMotorAdapter):
    @property
    def motor_id(self) -> str:
        return "motor_034"

    @property
    def input_motor_ids(self) -> list[str]:
        return ["motor_001", "motor_007", "motor_008", "motor_010", "motor_011", "motor_012", "motor_028", "motor_035", "motor_037", "motor_038", "motor_039", "motor_040", "motor_041", "motor_042", "motor_043", "motor_044", "motor_045", "motor_046", "motor_049", "motor_051"]

    def _run_impl(self, inputs: dict[str, Any]) -> dict[str, Any]:
        produced_at = _now()
        m07 = inputs.get("motor_007", {}) if isinstance(inputs.get("motor_007", {}), dict) else {}
        m12 = inputs.get("motor_012", {}) if isinstance(inputs.get("motor_012", {}), dict) else {}
        target_definition = m07.get("target_definition_contract") or inputs.get("__runtime__", {}).get("target_definition", {}) or {}

        variable_records, dataset_coverage_register = _derive_variable_records(inputs)
        cluster_maturity_register, cluster_report_readiness_profile = derive_cluster_maturity(variable_records)
        claim_permissions = _claim_permissions(variable_records, target_definition, dataset_coverage_register)
        decision_permissions = _decision_permissions(
            variable_records,
            m07.get("target_classification_object", {}),
            target_definition,
        )
        report_readiness = _report_readiness(
            variable_records,
            list(m12.get("missing_evidence_register", []) or []),
            str(m07.get("recommended_report_type", "")).strip(),
            m07.get("target_classification_object", {}),
            str(m07.get("technical_substrate_readiness", "")).strip(),
            cluster_report_readiness_profile,
            target_definition,
        )
        canonical_asset_context_summary = _canonical_asset_context_summary(
            m12,
            cluster_report_readiness_profile,
            str(m07.get("asset_context_readiness", "")).strip(),
        )
        cluster_report_readiness_profile = {
            **cluster_report_readiness_profile,
            "canonical_asset_context_state": canonical_asset_context_summary.get("canonical_asset_context_state", ""),
            "canonical_missing_clusters": list(canonical_asset_context_summary.get("missing_clusters", []) or []),
            "canonical_supported_clusters": list(canonical_asset_context_summary.get("supported_clusters", []) or []),
            "canonical_screening_supported": bool(canonical_asset_context_summary.get("screening_supported", False)),
        }
        report_type_classifier_table = _build_report_type_classifier_table(
            target_definition=target_definition,
            report_readiness=report_readiness,
            claim_permissions=claim_permissions,
        )
        structural_claim_permission_register = _structural_claim_permission_register(
            target_definition=target_definition,
            canonical_asset_context_summary=canonical_asset_context_summary,
            claim_permissions=claim_permissions,
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            competitive_comparison_register=list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
            structural_financial_exposure_register=list(inputs.get("motor_045", {}).get("structural_financial_exposure_register", []) or []),
        )
        claim_contract_register = _claim_contract_register(
            claim_permissions=claim_permissions,
            variable_records=variable_records,
            structural_claim_permission_register=structural_claim_permission_register,
            system_abstraction=dict(inputs.get("motor_037", {}).get("system_abstraction", {}) or {}),
            structural_financial_exposure_register=list(inputs.get("motor_045", {}).get("structural_financial_exposure_register", []) or []),
            competitive_comparison_register=list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
            minimum_evidence_for_discrimination_register=list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
        )
        structural_output_mode_classifier_table = _structural_output_mode_classifier_table(
            target_definition=target_definition,
            report_readiness=report_readiness,
            structural_claim_permission_register=structural_claim_permission_register,
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
            structural_benchmark_register=list(inputs.get("motor_042", {}).get("structural_benchmark_register", []) or []),
            competitive_comparison_register=list(inputs.get("motor_043", {}).get("competitive_comparison_register", []) or []),
            conditional_redesign_register=list(inputs.get("motor_044", {}).get("conditional_redesign_register", []) or []),
            minimum_evidence_for_discrimination_register=list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or []),
        )
        structural_output_mode_summary = _structural_output_mode_summary(
            primary_report_type=report_type_classifier_table[0]["recommended_report_type"] if report_type_classifier_table else report_readiness.recommended_report_type,
            structural_output_mode_classifier_table=structural_output_mode_classifier_table,
        )
        canonical_problem_frame = _canonical_problem_frame(
            target_definition=target_definition,
            archetype_resolution=dict(inputs.get("motor_039", {}) or {}),
            problem_framing_register=list(inputs.get("motor_041", {}).get("problem_framing_register", []) or []),
            cross_layer_conflict_register=list(inputs.get("motor_040", {}).get("cross_layer_conflict_register", []) or []),
            dominant_variable_register=list(inputs.get("motor_038", {}).get("dominant_variable_register", []) or []),
            minimum_evidence_for_discrimination_register=list(inputs.get("motor_046", {}).get("minimum_evidence_for_discrimination_register", []) or []),
            structural_output_mode_summary=structural_output_mode_summary,
            local_evidence_binding_register=list(inputs.get("motor_049", {}).get("local_evidence_binding_register", []) or []),
            cross_layer_congruence_register=list(inputs.get("motor_051", {}).get("cross_layer_congruence_register", []) or []),
            invalid_problem_frame_register=list(inputs.get("motor_051", {}).get("invalid_problem_frame_register", []) or []),
        )
        structural_primary_promotion_gate = _structural_primary_promotion_gate(
            target_definition=target_definition,
            report_readiness=report_readiness,
            structural_output_mode_classifier_table=structural_output_mode_classifier_table,
            structural_output_mode_summary=structural_output_mode_summary,
            canonical_problem_frame=canonical_problem_frame,
        )
        report_output_mode_classifier_table = _build_report_output_mode_classifier_table(
            target_definition=target_definition,
            report_readiness=report_readiness,
            report_type_classifier_table=report_type_classifier_table,
            structural_output_mode_classifier_table=structural_output_mode_classifier_table,
            structural_output_mode_summary=structural_output_mode_summary,
            structural_primary_promotion_gate=structural_primary_promotion_gate,
        )

        level_counts = {f"L{idx}": 0 for idx in range(5)}
        for record in variable_records:
            level_counts[record.maturity_level.code] += 1
        key_bottlenecks = [
            record.variable_name
            for record in variable_records
            if VARIABLE_CATALOG.get(record.variable_name)
            and VARIABLE_CATALOG[record.variable_name].criticality == "critical"
            and record.maturity_level <= EvidenceMaturityLevel.L1
        ][:10]

        return {
            "produced_at": produced_at,
            "motor_id": self.motor_id,
            "target_classification_context": m07.get("target_classification_object", {}),
            "dataset_coverage_register": dataset_coverage_register,
            "variable_maturity_register": [record.to_dict() for record in variable_records],
            "cluster_maturity_register": [record.to_dict() for record in cluster_maturity_register],
            "cluster_report_readiness_profile": cluster_report_readiness_profile,
            "canonical_asset_context_summary": canonical_asset_context_summary,
            "claim_permission_register": [record.to_dict() for record in claim_permissions],
            "structural_claim_permission_register": structural_claim_permission_register,
            "claim_contract_register": claim_contract_register,
            "decision_permission_register": [record.to_dict() for record in decision_permissions],
            "report_readiness_register": report_readiness.to_dict(),
            "report_type_classifier_table": report_type_classifier_table,
            "structural_output_mode_classifier_table": structural_output_mode_classifier_table,
            "structural_output_mode_summary": structural_output_mode_summary,
            "report_output_mode_classifier_table": report_output_mode_classifier_table,
            "canonical_problem_frame": canonical_problem_frame,
            "structural_primary_promotion_gate": structural_primary_promotion_gate,
            "maturity_summary": {
                "counts_by_level": level_counts,
                "key_bottlenecks": key_bottlenecks,
                "cluster_levels": cluster_report_readiness_profile.get("cluster_levels", {}),
                "screening_ready_clusters": cluster_report_readiness_profile.get("screening_ready_clusters", []),
                "nyc_domain_pack_active": bool(dataset_coverage_register),
                "allowed_report_types": report_readiness.report_type_allowed,
                "prohibited_report_types": report_readiness.report_type_prohibited,
                "canonical_asset_context_state": canonical_asset_context_summary.get("canonical_asset_context_state", ""),
                "canonical_missing_clusters": list(canonical_asset_context_summary.get("missing_clusters", []) or []),
                "canonical_supported_clusters": list(canonical_asset_context_summary.get("supported_clusters", []) or []),
                "structural_claim_permission_count": len(structural_claim_permission_register),
                "claim_contract_count": len(claim_contract_register),
                "structural_output_mode_count": len(structural_output_mode_classifier_table),
                "report_output_mode_classifier_count": len(report_output_mode_classifier_table),
                "structural_output_mode_activation_count": int(structural_output_mode_summary.get("activation_count", 0) or 0),
                "structural_output_mode_primary_eligibility_count": int(structural_output_mode_summary.get("eligible_primary_count", 0) or 0),
                "canonical_problem_frame_active": bool(canonical_problem_frame.get("problem_frame_active", False)),
                "structural_primary_promotion_state": str(structural_primary_promotion_gate.get("promotion_state", "") or ""),
            },
        }
