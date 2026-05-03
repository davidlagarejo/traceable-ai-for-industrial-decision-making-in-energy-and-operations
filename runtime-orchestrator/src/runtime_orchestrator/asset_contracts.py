from __future__ import annotations

import re
import unicodedata
from datetime import datetime, timezone
from typing import Any


_PHYSICAL_CLUSTERS = (
    "geometry_size_cluster",
    "vintage_structure_cluster",
    "operating_regime_cluster",
    "fuel_energy_cluster",
    "systems_cluster",
)

_MAILING_ADDRESS_RE = re.compile(r"\b(p\.?\s*o\.?\s*box|po box|mail(ing)?)\b", re.IGNORECASE)
_OFFICE_ADDRESS_RE = re.compile(r"\b(suite|ste\.?|floor|fl\b|unit|apt|#)\b", re.IGNORECASE)

_TECHNICAL_REPORT_TYPES = [
    "Full Technical Decision Intelligence Report",
    "Exploratory Prior / Minimum Evidence Report",
    "Decision-Blocked Asset Brief",
    "Pre-Verification Asset Brief",
    "TDIR Preliminary",
    "Decision-Grade TDIR",
]


def _nonempty(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, set, dict)):
        return len(value) > 0
    if isinstance(value, (int, float)):
        return value != 0
    return True


def _clean_list(values: list[Any]) -> list[str]:
    cleaned: list[str] = []
    for value in values:
        if not _nonempty(value):
            continue
        text = str(value).strip()
        if text and text not in cleaned:
            cleaned.append(text)
    return cleaned


def _first_nonempty(*values: Any) -> Any:
    for value in values:
        if _nonempty(value):
            return value
    return None


def _string(value: Any) -> str:
    if value is None:
        return ""
    return str(value).strip()


def _normalize_text(value: Any) -> str:
    text = _string(value).lower()
    if not text:
        return ""
    normalized = unicodedata.normalize("NFKD", text)
    stripped = "".join(ch for ch in normalized if not unicodedata.combining(ch))
    stripped = stripped.replace("&", " and ").replace("/", " ").replace("-", " ")
    return re.sub(r"\s+", " ", stripped).strip()


def _slugify(value: Any) -> str:
    normalized = _normalize_text(value)
    if not normalized:
        return ""
    return re.sub(r"[^a-z0-9]+", "-", normalized).strip("-")


def _contract_dict(pipeline: dict[str, Any], key: str) -> dict[str, Any]:
    value = pipeline.get(key, {})
    return value if isinstance(value, dict) else {}


def _location_dict(pipeline: dict[str, Any]) -> dict[str, Any]:
    fi = pipeline.get("facility_inputs", {})
    loc = fi.get("input_01_location", {})
    return loc if isinstance(loc, dict) else {}


def _sector_dict(pipeline: dict[str, Any]) -> dict[str, Any]:
    fi = pipeline.get("facility_inputs", {})
    sector = fi.get("input_03_sector", {})
    return sector if isinstance(sector, dict) else {}


def _declared_asset_name(
    subject_contract: dict[str, Any],
    target_contract: dict[str, Any],
    pipeline: dict[str, Any],
) -> str:
    explicit_name = _first_nonempty(
        subject_contract.get("declared_asset_name"),
        subject_contract.get("asset_name"),
    )
    if explicit_name is not None:
        return _string(explicit_name)
    target_name = _string(target_contract.get("target_name"))
    if target_contract and target_name and _nonempty(target_contract.get("target_scope")):
        loc = _location_dict(pipeline)
        sector = _sector_dict(pipeline)
        disallowed = {
            _string(loc.get("address")),
            _string(sector.get("owner_name")),
            _string(pipeline.get("case_title")),
        }
        if target_name not in disallowed:
            return target_name
    return ""


def _declared_asset_identifier(subject_contract: dict[str, Any], target_contract: dict[str, Any], pipeline: dict[str, Any]) -> str:
    explicit_identifier = _first_nonempty(
        subject_contract.get("declared_asset_identifier"),
        subject_contract.get("asset_identifier"),
    )
    if explicit_identifier is not None:
        return _string(explicit_identifier)
    target_identifier = target_contract.get("target_identifier")
    if _nonempty(target_identifier):
        loc = _location_dict(pipeline)
        sector = _sector_dict(pipeline)
        normalized = _string(target_identifier)
        disallowed = {
            _string(pipeline.get("case_id")),
            _string(loc.get("address")),
            _string(sector.get("owner_name")),
            _string(sector.get("owner_ticker")),
            _string(sector.get("owner_cik")),
        }
        if normalized not in disallowed:
            return normalized
    return ""


def _anchor_from_pipeline(
    pipeline: dict[str, Any],
    subject_contract: dict[str, Any],
    target_contract: dict[str, Any],
    declared_asset_name: str,
) -> tuple[str, str, str]:
    loc = _location_dict(pipeline)
    explicit_type = _string(subject_contract.get("asset_anchor_type"))
    explicit_value = _string(subject_contract.get("asset_anchor_value"))
    explicit_confidence = _string(subject_contract.get("asset_anchor_confidence"))
    if explicit_type and explicit_value:
        return explicit_type, explicit_value, explicit_confidence or "declared"

    parcel_id = _string(
        _first_nonempty(
            subject_contract.get("parcel_id"),
            target_contract.get("parcel_id"),
            loc.get("parcel_id"),
            loc.get("assessor_id"),
        )
    )
    if parcel_id:
        return "parcel_id", parcel_id, "medium"

    assessor_record = _string(
        _first_nonempty(
            subject_contract.get("assessor_record"),
            target_contract.get("assessor_record"),
            loc.get("assessor_record"),
        )
    )
    if assessor_record:
        return "assessor_record", assessor_record, "medium"

    benchmark_record = _string(
        _first_nonempty(
            subject_contract.get("benchmark_record"),
            target_contract.get("benchmark_record"),
            loc.get("benchmark_record"),
            loc.get("benchmark_building_id"),
        )
    )
    if benchmark_record:
        return "benchmark_record", benchmark_record, "medium"

    permit_record = _string(
        _first_nonempty(
            subject_contract.get("permit_record"),
            target_contract.get("permit_record"),
            loc.get("permit_record"),
        )
    )
    if permit_record:
        return "permit_record", permit_record, "medium"

    facility_registry_id = _string(
        _first_nonempty(
            subject_contract.get("facility_registry_id"),
            target_contract.get("facility_registry_id"),
            loc.get("facility_registry_id"),
        )
    )
    if facility_registry_id:
        return "facility_registry_id", facility_registry_id, "medium"

    latitude = _first_nonempty(
        subject_contract.get("latitude"),
        target_contract.get("latitude"),
        loc.get("latitude"),
        loc.get("lat"),
    )
    longitude = _first_nonempty(
        subject_contract.get("longitude"),
        target_contract.get("longitude"),
        loc.get("longitude"),
        loc.get("lon"),
        loc.get("lng"),
    )
    if _nonempty(latitude) and _nonempty(longitude):
        return "lat_lon", f"{latitude},{longitude}", "medium"

    address_raw = _string(_first_nonempty(subject_contract.get("address_raw"), target_contract.get("address_raw"), loc.get("address")))
    if address_raw and declared_asset_name:
        return "building_name_plus_address", f"{declared_asset_name} @ {address_raw}", "low"
    if address_raw:
        return "postal_address", address_raw, "low"
    return "", "", "none"


def derive_subject_definition(pipeline: dict[str, Any]) -> dict[str, Any]:
    subject_contract = _contract_dict(pipeline, "subject_definition_contract")
    target_contract = _contract_dict(pipeline, "target_definition_contract")
    loc = _location_dict(pipeline)
    sector = _sector_dict(pipeline)

    has_owner_context = any(
        _nonempty(value)
        for value in (
            sector.get("owner_name"),
            sector.get("owner_ticker"),
            sector.get("owner_cik"),
            subject_contract.get("owner_context_optional"),
            target_contract.get("owner_entity"),
        )
    )
    declared_asset_name = _declared_asset_name(subject_contract, target_contract, pipeline)
    declared_asset_identifier = _declared_asset_identifier(subject_contract, target_contract, pipeline)
    asset_anchor_type, asset_anchor_value, asset_anchor_confidence = _anchor_from_pipeline(
        pipeline,
        subject_contract,
        target_contract,
        declared_asset_name,
    )

    explicit_subject_kind = _string(subject_contract.get("subject_kind"))
    if explicit_subject_kind:
        subject_kind = explicit_subject_kind
    elif asset_anchor_type in {"parcel_id", "assessor_record", "benchmark_record", "permit_record", "facility_registry_id"}:
        subject_kind = "site_candidate"
    elif asset_anchor_type == "lat_lon":
        subject_kind = "site_candidate"
    elif asset_anchor_type == "building_name_plus_address":
        subject_kind = "asset_candidate"
    elif asset_anchor_type == "postal_address":
        subject_kind = "address_candidate"
    elif has_owner_context:
        subject_kind = "issuer"
    else:
        subject_kind = "issuer"

    explicit_subject_scope = _string(subject_contract.get("subject_scope"))
    if explicit_subject_scope:
        subject_scope = explicit_subject_scope
    elif subject_kind in {"issuer"}:
        subject_scope = "issuer"
    elif subject_kind in {"portfolio", "campus"}:
        subject_scope = subject_kind
    elif subject_kind == "subsystem":
        subject_scope = "subsystem"
    else:
        subject_scope = "asset"

    contract_status = "declared" if subject_contract else "bridged_target_contract" if target_contract else "inferred"
    if subject_contract:
        subject_origin = _string(subject_contract.get("subject_origin")) or "declared_subject_contract"
    elif target_contract:
        subject_origin = "bridged_target_contract"
    elif asset_anchor_type == "postal_address" and has_owner_context:
        subject_origin = "issuer_plus_address_seed"
    elif asset_anchor_type == "postal_address":
        subject_origin = "address_seed"
    elif has_owner_context:
        subject_origin = "issuer_seed"
    else:
        subject_origin = "pipeline_inferred"

    explicit_seed_state = _string(subject_contract.get("seed_state"))
    if explicit_seed_state:
        seed_state = explicit_seed_state
    elif subject_kind == "issuer":
        seed_state = "issuer_seeded"
    elif subject_kind == "address_candidate":
        seed_state = "address_seeded"
    elif subject_kind == "site_candidate":
        seed_state = "site_seeded"
    else:
        seed_state = "asset_seeded"

    if subject_kind == "bounded_asset":
        asset_identity_evidence_class = "multi-source_asset_bounded"
    elif asset_anchor_type == "benchmark_record":
        asset_identity_evidence_class = "benchmark_record_linked"
    elif asset_anchor_type in {"permit_record", "facility_registry_id", "assessor_record"}:
        asset_identity_evidence_class = "local_asset_record_linked"
    elif asset_anchor_type == "parcel_id":
        asset_identity_evidence_class = "parcel_or_record_linked"
    elif asset_anchor_type == "lat_lon":
        asset_identity_evidence_class = "geocoded_only"
    elif asset_anchor_type == "building_name_plus_address":
        asset_identity_evidence_class = "declared_only"
    elif asset_anchor_type == "postal_address" and has_owner_context:
        asset_identity_evidence_class = "issuer_address_only"
    elif asset_anchor_type == "postal_address":
        asset_identity_evidence_class = "declared_only"
    else:
        asset_identity_evidence_class = "declared_only" if declared_asset_name or declared_asset_identifier else "none"

    return {
        "subject_kind": subject_kind,
        "subject_scope": subject_scope,
        "subject_origin": subject_origin,
        "seed_state": seed_state,
        "asset_anchor_type": asset_anchor_type,
        "asset_anchor_value": asset_anchor_value,
        "asset_anchor_confidence": asset_anchor_confidence or "none",
        "asset_identity_evidence_class": asset_identity_evidence_class,
        "owner_context_optional": _string(
            _first_nonempty(subject_contract.get("owner_context_optional"), target_contract.get("owner_entity"), sector.get("owner_name"))
        ),
        "operator_context_optional": _string(
            _first_nonempty(subject_contract.get("operator_context_optional"), target_contract.get("operator_entity"), sector.get("owner_name"))
        ),
        "declared_asset_name": declared_asset_name,
        "declared_asset_identifier": declared_asset_identifier,
        "address_raw": _string(_first_nonempty(subject_contract.get("address_raw"), target_contract.get("address_raw"), loc.get("address"))),
        "contract_status": contract_status,
    }


def derive_subject_contract_admissibility(
    subject_definition: dict[str, Any],
    target_definition: dict[str, Any] | None = None,
) -> tuple[str, list[dict[str, Any]]]:
    target_definition = target_definition or {}
    warnings: list[dict[str, Any]] = []
    subject_kind = _string(subject_definition.get("subject_kind"))
    asset_anchor_type = _string(subject_definition.get("asset_anchor_type"))
    asset_anchor_value = _string(subject_definition.get("asset_anchor_value"))
    target_scope = _string(target_definition.get("target_scope"))

    def _warn(code: str, message: str, *, severity: str = "warning") -> None:
        warnings.append({
            "code": code,
            "severity": severity,
            "message": message,
        })

    if subject_kind == "issuer":
        admissibility = "issuer_only"
        _warn("issuer_context_only", "Issuer context was identified without a bounded physical asset anchor.")
    elif subject_kind == "address_candidate":
        admissibility = "ambiguous_subject"
        _warn("address_without_asset_evidence", "Address-only seed detected; physical asset identity has not been corroborated yet.")
    elif subject_kind in {"portfolio", "campus"}:
        admissibility = "invalid_for_asset_pipeline"
        _warn("target_scope_claim_exceeds_declared_anchor", "Declared subject is broader than a single admissible asset case.", severity="error")
    elif subject_kind in {"site_candidate", "asset_candidate", "bounded_asset", "subsystem"}:
        admissibility = "valid_asset_candidate"
    else:
        admissibility = "invalid_for_asset_pipeline"
        _warn("missing_asset_anchor", "No admissible physical anchor was found for an asset pipeline case.", severity="error")

    if admissibility != "issuer_only" and not asset_anchor_type and not asset_anchor_value:
        admissibility = "invalid_for_asset_pipeline"
        _warn("missing_asset_anchor", "Subject contract does not contain a usable physical anchor.", severity="error")

    if target_scope == "asset" and admissibility in {"issuer_only", "ambiguous_subject", "invalid_for_asset_pipeline"}:
        _warn(
            "target_scope_claim_exceeds_declared_anchor",
            "The target contract claims asset scope, but the declared subject anchor does not yet justify an asset case.",
            severity="error" if admissibility == "invalid_for_asset_pipeline" else "warning",
        )

    return admissibility, warnings


def derive_target_type_classification_seed(
    subject_definition: dict[str, Any],
    target_definition: dict[str, Any] | None = None,
) -> dict[str, Any]:
    target_definition = target_definition or {}
    subject_kind = _string(subject_definition.get("subject_kind"))
    subject_origin = _string(subject_definition.get("subject_origin"))
    address_raw = _string(subject_definition.get("address_raw") or target_definition.get("address_raw"))
    owner_context = _string(
        _first_nonempty(
            subject_definition.get("owner_context_optional"),
            target_definition.get("owner_entity"),
        )
    )
    asset_anchor_type = _string(subject_definition.get("asset_anchor_type"))
    asset_identity_evidence_class = _string(subject_definition.get("asset_identity_evidence_class"))

    target_type_classification = "AMBIGUOUS_TARGET"
    asset_identity_status = "ambiguous"
    classification_confidence = "low"
    reason = "The declared subject is not yet sufficiently corroborated as an operating asset."
    supporting_signals: list[str] = []

    if subject_kind == "bounded_asset":
        target_type_classification = "OPERATING_ASSET"
        asset_identity_status = "bounded"
        classification_confidence = "high"
        reason = "The declared subject already carries a bounded asset identity anchor."
        supporting_signals.append("bounded_asset_subject")
    elif subject_kind == "asset_candidate":
        target_type_classification = "PROPERTY_LISTING"
        asset_identity_status = "candidate"
        classification_confidence = "medium"
        reason = "The declared subject resembles a named asset or listing, but public identity corroboration remains incomplete."
        supporting_signals.append("named_asset_candidate")
    elif subject_kind == "site_candidate":
        target_type_classification = "AMBIGUOUS_TARGET"
        asset_identity_status = "candidate"
        classification_confidence = "medium" if asset_identity_evidence_class in {
            "parcel_or_record_linked",
            "local_asset_record_linked",
            "benchmark_record_linked",
        } else "low"
        reason = "A physical site candidate exists, but operating-asset identity remains unbounded."
        supporting_signals.append("site_candidate_anchor")
    elif subject_kind == "address_candidate":
        if address_raw and _MAILING_ADDRESS_RE.search(address_raw):
            target_type_classification = "REGISTERED_AGENT_OR_MAILING_ADDRESS"
            asset_identity_status = "issuer_only"
            classification_confidence = "high"
            reason = "The declared address reads as mailing or administrative context, not as a bounded operating asset."
            supporting_signals.append("mailing_address_seed")
        elif address_raw and owner_context and _OFFICE_ADDRESS_RE.search(address_raw):
            target_type_classification = "CORPORATE_HEADQUARTERS"
            asset_identity_status = "issuer_only"
            classification_confidence = "medium"
            reason = "The declared address reads as office or suite context and is not yet a bounded operating asset."
            supporting_signals.append("office_suite_seed")
        else:
            target_type_classification = "AMBIGUOUS_TARGET"
            asset_identity_status = "candidate"
            classification_confidence = "low"
            reason = "Only an address-level anchor exists; no bounded operating asset has been confirmed."
            supporting_signals.append("address_only_seed")
    elif subject_kind == "issuer":
        asset_identity_status = "issuer_only"
        classification_confidence = "medium" if address_raw and owner_context else "low"
        if address_raw:
            target_type_classification = "CORPORATE_HEADQUARTERS"
            reason = "Issuer context plus an address suggests headquarters, investor-relations, or executive-office context rather than a confirmed operating asset."
            supporting_signals.append("issuer_plus_address")
        else:
            target_type_classification = "PORTFOLIO_ENTITY"
            reason = "Only issuer or portfolio context exists; no physical asset anchor has been confirmed."
            supporting_signals.append("issuer_only_context")
    elif subject_kind in {"portfolio", "campus"}:
        target_type_classification = "PORTFOLIO_ENTITY"
        asset_identity_status = "invalid"
        classification_confidence = "high"
        reason = "The declared subject is broader than a single operating asset and is not admissible as an asset case."
        supporting_signals.append("multi_asset_scope")
    elif subject_kind == "subsystem":
        target_type_classification = "OPERATING_ASSET"
        asset_identity_status = "candidate"
        classification_confidence = "medium"
        reason = "A subsystem target was declared; it may be physically real but still requires asset-boundary confirmation."
        supporting_signals.append("subsystem_subject")
    else:
        target_type_classification = "INVALID_TARGET"
        asset_identity_status = "invalid"
        classification_confidence = "low"
        reason = "No admissible subject pattern was found for asset-first ingestion."

    if asset_anchor_type == "postal_address" and subject_origin == "issuer_plus_address_seed":
        target_type_classification = "AMBIGUOUS_TARGET"
        asset_identity_status = "candidate"
        classification_confidence = "low"
        reason = "Issuer-plus-address seeds remain ambiguous until public asset-level corroboration is found."
        supporting_signals.append("issuer_plus_address_seed")

    if target_type_classification == "OPERATING_ASSET":
        recommended_report_type = "Exploratory Prior / Minimum Evidence Report"
        prohibited_report_types = [
            "Entity Address Classification Brief",
            "Target Clarification Brief",
        ]
    elif target_type_classification in {"CORPORATE_HEADQUARTERS", "REGISTERED_AGENT_OR_MAILING_ADDRESS"}:
        recommended_report_type = "Entity Address Classification Brief"
        prohibited_report_types = list(_TECHNICAL_REPORT_TYPES)
    elif target_type_classification == "PORTFOLIO_ENTITY":
        recommended_report_type = "Issuer Context Memo"
        prohibited_report_types = list(_TECHNICAL_REPORT_TYPES)
    elif target_type_classification in {"PROPERTY_LISTING", "AMBIGUOUS_TARGET"}:
        recommended_report_type = "Target Clarification Brief"
        prohibited_report_types = [
            "Full Technical Decision Intelligence Report",
            "Pre-Verification Asset Brief",
            "TDIR Preliminary",
            "Decision-Grade TDIR",
        ]
    else:
        recommended_report_type = "No Technical Asset Report"
        prohibited_report_types = list(_TECHNICAL_REPORT_TYPES)

    return {
        "target_type_classification": target_type_classification,
        "asset_identity_status": asset_identity_status,
        "classification_confidence": classification_confidence,
        "reason": reason,
        "supporting_signals": supporting_signals,
        "report_type_recommendation": {
            "recommended_report_type": recommended_report_type,
            "reason": reason,
            "prohibited_report_types": prohibited_report_types,
        },
    }


def infer_target_type_from_pipeline(pipeline: dict[str, Any]) -> str:
    contract = pipeline.get("target_definition_contract", {})
    if isinstance(contract, dict) and _nonempty(contract.get("target_type")):
        return str(contract.get("target_type")).strip()

    fi = pipeline.get("facility_inputs", {})
    facility_type = fi.get("input_02_facility_type", {}) if isinstance(fi.get("input_02_facility_type", {}), dict) else {}
    sector = fi.get("input_03_sector", {}) if isinstance(fi.get("input_03_sector", {}), dict) else {}
    uses = fi.get("input_04_primary_use", {}) if isinstance(fi.get("input_04_primary_use", {}), dict) else {}
    search_blob = _normalize_text(
        " ".join(
            _clean_list(
                [
                    facility_type.get("classification"),
                    sector.get("sector"),
                    sector.get("sic"),
                    sector.get("sic_code"),
                    sector.get("owner_name"),
                    *uses.get("uses", []),
                    pipeline.get("case_title"),
                    pipeline.get("case_subtitle"),
                ]
            )
        )
    )
    sic_raw = _string(
        _first_nonempty(
            sector.get("sic"),
            sector.get("sic_code"),
            facility_type.get("sic"),
            facility_type.get("sic_code"),
        )
    )
    sic_digits = "".join(ch for ch in sic_raw if ch.isdigit())

    def has_any(*tokens: str) -> bool:
        return any(token in search_blob for token in tokens if token)

    if has_any("data center", "datacenter", "centro de datos", "centros de datos", "colocation", "colo"):
        return "data_center"
    if has_any("hospital", "medical center", "clinic", "clinica", "centro medico"):
        return "hospital"
    if has_any("hotel", "hospitality", "hospitalidad"):
        return "hotel"
    if has_any("multifamily", "residential apartment", "apartment", "apartamento", "residencial"):
        return "multifamily_building"
    if has_any("warehouse", "distribution", "logistics", "logistica", "fulfillment", "industrial reit"):
        return "warehouse_distribution"
    if has_any("cold storage", "cold chain", "cadena de frio", "refrigerated warehouse"):
        return "cold_chain_facility"
    if has_any("food", "foods", "beverage", "alimentos", "bebida", "bebidas", "food processing"):
        return "food_processing_facility"
    if has_any("upstream", "midstream", "downstream", "lng", "refining", "refinery", "petrochemical", "petroquim", "oil and gas"):
        if "upstream" in search_blob:
            return "oil_gas_upstream_site"
        if "midstream" in search_blob or has_any("compression", "terminal", "pipeline transport"):
            return "oil_gas_midstream_facility"
        return "oil_gas_downstream_facility"
    if has_any("utilities", "utility", "renewable", "renovable", "power", "transmission", "grid", "substation", "ferrocarril", "rail", "railroad", "telecom tower", "torres telecomunicaciones", "gas electrica", "gas y electrica"):
        return "infrastructure_node"
    if has_any("manufactur", "manufactura", "fabrication", "fabricacion", "factory", "fabrica", "processing plant"):
        return "manufacturing_facility"
    if has_any("industrial", "conglomerado", "automatizacion", "automation", "maquinaria", "machinery", "equipment", "construction equipment", "agricultural equipment"):
        return "industrial_plant"
    if sic_digits.startswith(("49", "40", "42", "48")):
        return "infrastructure_node"
    if sic_digits.startswith(("20", "21")):
        return "food_processing_facility"
    if sic_digits.startswith(("13", "29")):
        if has_any("midstream", "compression", "terminal"):
            return "oil_gas_midstream_facility"
        return "oil_gas_downstream_facility"
    if sic_digits.startswith(("35", "36", "37", "38")):
        if has_any("manufactur", "factory", "plant", "fabricacion", "manufactura"):
            return "manufacturing_facility"
        return "industrial_plant"
    if any(token in search_blob for token in ("campus", "portfolio")):
        return "campus"
    if any(token in search_blob for token in ("office", "oficinas", "reit")):
        return "commercial_building"
    if any(token in search_blob for token in ("food", "beverage", "cold storage", "cold chain")):
        if "cold" in search_blob:
            return "cold_chain_facility"
        return "food_processing_facility"
    return "commercial_building"


def _derive_target_slug(
    subject_kind: str,
    target_name: str,
    target_identifier: str,
    owner_entity: str,
) -> str:
    if subject_kind == "issuer":
        base = owner_entity or target_name or target_identifier or "issuer"
    elif subject_kind == "address_candidate":
        base = target_identifier or target_name or owner_entity or "address"
    else:
        base = target_name or target_identifier or owner_entity or "target"
    slug = _slugify(base)
    return slug[:96] if slug else "unidentified-target"


_TARGET_TYPE_SLUG_ALIASES = {
    "commercial_building": "commercial-building",
    "multifamily_building": "multifamily-building",
    "industrial_plant": "industrial-plant",
    "manufacturing_facility": "manufacturing-facility",
    "food_processing_facility": "food-processing-facility",
    "cold_chain_facility": "cold-chain-facility",
    "warehouse_distribution": "warehouse-distribution",
    "oil_gas_upstream_site": "oil-gas-upstream-site",
    "oil_gas_midstream_facility": "oil-gas-midstream-facility",
    "oil_gas_downstream_facility": "oil-gas-downstream-facility",
    "water_wastewater_facility": "water-wastewater-facility",
    "hospital": "hospital",
    "data_center": "data-center",
    "campus": "campus",
    "infrastructure_node": "infrastructure-node",
}


def _target_type_slug(target_type: str) -> str:
    normalized = str(target_type or "").strip()
    if not normalized:
        return ""
    return _TARGET_TYPE_SLUG_ALIASES.get(normalized, _slugify(normalized))


def _derive_target_id(subject_kind: str, target_type: str, target_slug: str) -> str:
    prefix = {
        "issuer": "issuer",
        "address_candidate": "addr",
        "site_candidate": "site",
        "asset_candidate": "asset",
        "bounded_asset": "asset",
        "asset": "asset",
        "subsystem": "subsys",
        "campus": "campus",
        "portfolio": "portfolio",
    }.get((subject_kind or "").strip().lower(), "target")
    type_slug = _target_type_slug(target_type)
    pieces = [prefix]
    if prefix != "issuer" and type_slug:
        pieces.append(type_slug)
    base = "-".join(piece for piece in pieces if piece)
    if not target_slug:
        return base[:140]
    remaining = 140 - len(base) - 1
    if remaining <= 0:
        return base[:140]
    trimmed_target_slug = target_slug[:remaining].strip("-")
    return f"{base}-{trimmed_target_slug}"[:140]


def derive_target_definition(pipeline: dict[str, Any]) -> dict[str, Any]:
    contract = pipeline.get("target_definition_contract", {})
    contract = contract if isinstance(contract, dict) else {}
    fi = pipeline.get("facility_inputs", {})
    loc = _location_dict(pipeline)
    sector = _sector_dict(pipeline)
    concern = fi.get("input_10_main_concern", {}) if isinstance(fi.get("input_10_main_concern", {}), dict) else {}
    subject_definition = derive_subject_definition(pipeline)

    has_address = _nonempty(loc.get("address"))
    has_owner = _nonempty(sector.get("owner_name")) or _nonempty(sector.get("owner_ticker")) or _nonempty(sector.get("owner_cik"))
    explicit_scope = _string(contract.get("target_scope"))
    if explicit_scope:
        target_scope = explicit_scope
        target_scope_basis = "declared_target_contract"
    elif subject_definition.get("subject_kind") == "issuer":
        target_scope = "issuer"
        target_scope_basis = "subject_kind:issuer"
    else:
        target_scope = "asset"
        target_scope_basis = f"subject_kind:{subject_definition.get('subject_kind', 'unknown')}"
    explicit_case_mode = _string(contract.get("case_mode"))
    if explicit_case_mode:
        case_mode = explicit_case_mode
    else:
        seed_state = _string(subject_definition.get("seed_state"))
        if seed_state == "issuer_seeded":
            case_mode = "issuer_seeded"
        elif seed_state == "address_seeded":
            case_mode = "address_first"
        elif seed_state == "site_seeded":
            case_mode = "site_first"
        else:
            case_mode = "asset_seeded"

    target_name = (
        contract.get("target_name")
        or subject_definition.get("declared_asset_name")
        or loc.get("address")
        or pipeline.get("case_title")
        or sector.get("owner_name")
        or "Unnamed target"
    )
    target_identifier = (
        contract.get("target_identifier")
        or subject_definition.get("declared_asset_identifier")
        or loc.get("address")
        or sector.get("owner_ticker")
        or pipeline.get("case_id")
        or "unidentified-target"
    )

    target_type = str(contract.get("target_type") or infer_target_type_from_pipeline(pipeline)).strip()
    owner_entity = contract.get("owner_entity") or sector.get("owner_name", "")
    target_slug = _derive_target_slug(
        str(subject_definition.get("subject_kind", "")).strip(),
        str(target_name).strip(),
        str(target_identifier).strip(),
        str(owner_entity).strip(),
    )
    target_id = _derive_target_id(
        str(subject_definition.get("subject_kind", "")).strip(),
        target_type,
        target_slug,
    )

    return {
        "target_scope": target_scope,
        "target_type": target_type,
        "target_identifier": str(target_identifier).strip(),
        "target_name": str(target_name).strip(),
        "target_label": str(target_name or target_identifier).strip(),
        "target_slug": target_slug,
        "target_id": target_id,
        "address_raw": str(contract.get("address_raw") or loc.get("address", "")).strip(),
        "geocode_status": str(contract.get("geocode_status") or ("address_declared" if has_address else "not_geocoded")).strip(),
        "jurisdiction_scope": contract.get("jurisdiction_scope") or loc.get("jurisdiction_codes", []),
        "owner_entity": owner_entity,
        "operator_entity": contract.get("operator_entity") or sector.get("owner_name", ""),
        "report_intent": str(contract.get("report_intent") or "asset_preverification_screening").strip(),
        "decision_intent": str(contract.get("decision_intent") or concern.get("decision_type") or "asset_screening").strip(),
        "case_mode": case_mode,
        "subject_kind": subject_definition.get("subject_kind"),
        "subject_seed_state": subject_definition.get("seed_state"),
        "target_scope_basis": target_scope_basis,
        "contract_status": "declared" if contract else "inferred",
    }


def derive_effective_case_id(
    pipeline: dict[str, Any],
    target_definition: dict[str, Any] | None = None,
) -> str:
    target_definition = target_definition or derive_target_definition(pipeline)
    target_id = _string(target_definition.get("target_id"))
    if not target_id:
        return _string(pipeline.get("case_id")) or "zlab-target-case"

    raw_case_id = _string(pipeline.get("case_id"))
    year_match = re.search(r"(20\d{2})(?!.*20\d{2})", raw_case_id)
    year = year_match.group(1) if year_match else str(datetime.now(timezone.utc).year)
    return f"ZLab-{target_id}-{year}"


def derive_observable_clusters(pipeline: dict[str, Any], target_definition: dict[str, Any] | None = None) -> dict[str, dict[str, Any]]:
    fi = pipeline.get("facility_inputs", {})
    loc = fi.get("input_01_location", {}) if isinstance(fi.get("input_01_location", {}), dict) else {}
    size = fi.get("input_05_size", {}) if isinstance(fi.get("input_05_size", {}), dict) else {}
    vintage = fi.get("input_06_vintage", {}) if isinstance(fi.get("input_06_vintage", {}), dict) else {}
    uses = fi.get("input_04_primary_use", {}) if isinstance(fi.get("input_04_primary_use", {}), dict) else {}
    schedule = fi.get("input_07_operating_schedule", {}) if isinstance(fi.get("input_07_operating_schedule", {}), dict) else {}
    energy = fi.get("input_08_energy_fuel", {}) if isinstance(fi.get("input_08_energy_fuel", {}), dict) else {}
    systems = fi.get("input_09_known_systems", {}) if isinstance(fi.get("input_09_known_systems", {}), dict) else {}
    facility_type = fi.get("input_02_facility_type", {}) if isinstance(fi.get("input_02_facility_type", {}), dict) else {}

    target_type = (target_definition or {}).get("target_type") or infer_target_type_from_pipeline(pipeline)
    target_scope = (target_definition or {}).get("target_scope") or "asset"

    def _cluster(name: str, values: list[Any], *, note: str = "") -> dict[str, Any]:
        populated_fields = [str(v).strip() if not isinstance(v, (list, dict)) else v for v in values if _nonempty(v)]
        return {
            "cluster_id": name,
            "populated": len(populated_fields) > 0,
            "populated_count": len(populated_fields),
            "note": note,
        }

    clusters = {
        "location_cluster": _cluster(
            "location_cluster",
            [loc.get("address"), loc.get("city"), loc.get("state"), loc.get("country")],
            note="Physical location primitives.",
        ),
        "jurisdiction_cluster": _cluster(
            "jurisdiction_cluster",
            [loc.get("jurisdiction_codes"), loc.get("state"), loc.get("country")],
            note="Jurisdiction and regulatory anchoring.",
        ),
        "geometry_size_cluster": _cluster(
            "geometry_size_cluster",
            [*size.values()],
            note="Scale and geometry descriptors.",
        ),
        "vintage_structure_cluster": _cluster(
            "vintage_structure_cluster",
            [*vintage.values()],
            note="Age, structure, renovation, and historical fabric.",
        ),
        "use_program_cluster": _cluster(
            "use_program_cluster",
            [facility_type.get("classification"), uses.get("uses")],
            note="Use mix and typology identity.",
        ),
        "operating_regime_cluster": _cluster(
            "operating_regime_cluster",
            [*schedule.values()],
            note="Schedules, shifts, occupancy, operating windows.",
        ),
        "fuel_energy_cluster": _cluster(
            "fuel_energy_cluster",
            [*energy.values()],
            note="Fuel, utility, or energy-system hints.",
        ),
        "systems_cluster": _cluster(
            "systems_cluster",
            [*systems.values()],
            note="Known system and equipment descriptors.",
        ),
        "regulatory_cluster": _cluster(
            "regulatory_cluster",
            [loc.get("jurisdiction_codes"), target_scope],
            note="Minimum rule-routing context.",
        ),
        "benchmark_mapping_cluster": _cluster(
            "benchmark_mapping_cluster",
            [target_type, facility_type.get("classification"), uses.get("uses")],
            note="Enough typology context to route benchmark families.",
        ),
    }
    return clusters


def derive_asset_context_readiness(
    pipeline: dict[str, Any],
    target_definition: dict[str, Any] | None = None,
    clusters: dict[str, dict[str, Any]] | None = None,
) -> str:
    target_definition = target_definition or derive_target_definition(pipeline)
    clusters = clusters or derive_observable_clusters(pipeline, target_definition)
    populated_count = sum(1 for c in clusters.values() if c.get("populated"))
    physical_count = sum(1 for key in _PHYSICAL_CLUSTERS if clusters.get(key, {}).get("populated"))

    if target_definition.get("target_scope") == "issuer" and not clusters.get("location_cluster", {}).get("populated"):
        return "issuer_context_only"
    if clusters.get("location_cluster", {}).get("populated") and populated_count <= 2:
        return "location_only"
    if populated_count < 4 or physical_count == 0:
        return "asset_context_insufficient"
    if populated_count >= 4 and physical_count >= 1:
        if populated_count >= 6 and physical_count >= 3:
            if all(clusters.get(k, {}).get("populated") for k in ("geometry_size_cluster", "use_program_cluster", "systems_cluster")):
                return "asset_context_operable"
            return "asset_context_minimal"
        return "asset_context_minimal"
    return "asset_context_insufficient"


def derive_report_identity_state(
    target_definition: dict[str, Any],
    asset_context_readiness: str,
) -> str:
    scope = target_definition.get("target_scope", "asset")
    if scope == "issuer" and asset_context_readiness in {"issuer_context_only", "location_only"}:
        return "Issuer Context Memo"
    mapping = {
        "issuer_context_only": "Issuer Context Memo",
        "location_only": "Asset Context Seed Brief",
        "asset_context_insufficient": "Asset Context Insufficiency Brief",
        "asset_context_minimal": "Pre-Verification Asset Brief",
        "asset_context_operable": "TDIR Preliminary",
        "asset_context_hardened": "Decision-Grade TDIR",
    }
    return mapping.get(asset_context_readiness, "Asset Context Insufficiency Brief")


def derive_dominant_evidence_scope(
    target_definition: dict[str, Any],
    asset_context_readiness: str,
) -> str:
    scope = target_definition.get("target_scope", "asset")
    if scope == "issuer":
        return "issuer_context_dominant"
    if asset_context_readiness in {"issuer_context_only", "location_only"}:
        return "issuer_context_dominant"
    if asset_context_readiness == "asset_context_insufficient":
        return "mixed_scope_with_issuer_bias"
    if asset_context_readiness == "asset_context_minimal":
        return "mixed_scope_preliminary"
    return "asset_context_dominant"


def missing_observable_clusters(clusters: dict[str, dict[str, Any]]) -> list[str]:
    return [name for name, entry in clusters.items() if not entry.get("populated")]
