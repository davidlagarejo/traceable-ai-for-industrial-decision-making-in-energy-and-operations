from runtime_orchestrator.evidence_maturity import (
    CLAIM_TEMPLATES,
    DECISION_TEMPLATES,
    DERIVED_VARIABLE_DEPENDENCIES,
    EvidenceMaturityLevel,
    VARIABLE_CATALOG,
    derive_dependency_bottleneck,
)
from runtime_orchestrator.evidence_maturity.domain_packs import NYC_BUILDING_VARIABLE_MATRIX, NYC_DATASETS, get_nyc_building_domain_pack


def test_evidence_maturity_levels_are_ordered():
    assert EvidenceMaturityLevel.L0 < EvidenceMaturityLevel.L1 < EvidenceMaturityLevel.L2 < EvidenceMaturityLevel.L3 < EvidenceMaturityLevel.L4
    assert EvidenceMaturityLevel.L3.label == "Local Measured / Documented"


def test_variable_catalog_contains_minimum_nyc_critical_variables():
    expected = {
        "address",
        "asset_vs_entity_classification",
        "GFA",
        "EUI",
        "utility_bills",
        "tariff_class",
        "HVAC_type",
        "compliance_filing",
        "CAPEX",
        "ROI",
    }
    assert expected.issubset(VARIABLE_CATALOG.keys())
    assert VARIABLE_CATALOG["ROI"].dependencies == ["savings", "CAPEX", "owner_control_boundary"]


def test_nyc_domain_pack_contains_required_datasets():
    expected = {
        "nyc_dof_property_record",
        "nyc_pluto",
        "nyc_dob_permits",
        "nyc_ll84_benchmarking",
        "nyc_ll97_emissions",
    }
    assert expected.issubset(NYC_DATASETS.keys())
    assert "EUI" in NYC_DATASETS["nyc_ll84_benchmarking"].coverage_variables
    assert "regulated_floor_area" in NYC_DATASETS["nyc_ll97_emissions"].coverage_variables


def test_nyc_variable_matrix_has_core_ladders():
    gfa = NYC_BUILDING_VARIABLE_MATRIX["GFA"]
    eui = NYC_BUILDING_VARIABLE_MATRIX["EUI"]
    roi = NYC_BUILDING_VARIABLE_MATRIX["ROI"]
    assert gfa.level_definitions[EvidenceMaturityLevel.L3].startswith("PLUTO")
    assert eui.level_definitions[EvidenceMaturityLevel.L3] == "LL84 or bill-derived public asset-specific intensity."
    assert "directional economics" in roi.outputs_allowed[EvidenceMaturityLevel.L1]


def test_claim_templates_capture_roi_and_compliance_bottlenecks():
    roi_range = CLAIM_TEMPLATES["roi_range_claim"]
    compliance_screening = CLAIM_TEMPLATES["compliance_screening_claim"]
    assert roi_range.minimum_maturity_by_variable["GFA"] == EvidenceMaturityLevel.L2
    assert roi_range.minimum_maturity_by_variable["CAPEX"] == EvidenceMaturityLevel.L1
    assert compliance_screening.minimum_maturity_by_variable["applicable_rule_family"] == EvidenceMaturityLevel.L1
    assert "compliant/non-compliant conclusion" in compliance_screening.prohibited_outputs


def test_decision_templates_surface_identity_and_retrofit_logic():
    identity = DECISION_TEMPLATES["asset_identity_confirmation"]
    retrofit = DECISION_TEMPLATES["retrofit_capex"]
    assert identity.minimum_maturity_by_variable["asset_vs_entity_classification"] == EvidenceMaturityLevel.L3
    assert "ACT NOW" in identity.allowed_actions
    assert retrofit.minimum_maturity_by_variable["utility_bills"] == EvidenceMaturityLevel.L3
    assert "INVESTMENT-GRADE COMMITMENT" in retrofit.blocked_actions


def test_dependency_bottleneck_uses_weakest_required_variable():
    bottleneck, deps = derive_dependency_bottleneck(
        "ROI",
        {
            "savings": EvidenceMaturityLevel.L2,
            "CAPEX": EvidenceMaturityLevel.L1,
            "owner_control_boundary": EvidenceMaturityLevel.L3,
        },
    )
    assert deps == DERIVED_VARIABLE_DEPENDENCIES["ROI"]
    assert bottleneck == EvidenceMaturityLevel.L1


def test_nyc_domain_pack_export_is_runtime_friendly():
    pack = get_nyc_building_domain_pack()
    assert pack["jurisdiction"] == "US-NY-NYC"
    assert "datasets" in pack
    assert "variable_matrix" in pack
    assert pack["required_dataset_sequence"][0] == "nyc_dof_property_record"
