from runtime_orchestrator.public_data_routing import (
    AssetType,
    TargetClassification,
    critical_fields_for_asset_type,
    default_evidence_gating_plan,
    make_target_classification_result,
    normalize_asset_type,
    technical_scraping_allowed_for_target_class,
)


def test_normalize_asset_type_maps_existing_runtime_labels():
    assert normalize_asset_type("warehouse_distribution") == AssetType.WAREHOUSE_LOGISTICS
    assert normalize_asset_type("industrial_plant") == AssetType.INDUSTRIAL_FACILITY
    assert normalize_asset_type("data_center") == AssetType.DATA_CENTER


def test_target_classification_result_blocks_technical_scraping_for_hq():
    result = make_target_classification_result(
        TargetClassification.CORPORATE_HEADQUARTERS,
        classification_confidence="high",
        asset_identity_confirmed=False,
        reason="Address resolves to headquarters context only.",
    )
    assert result.technical_scraping_allowed is False
    assert result.report_type_if_blocked == "Target Classification Brief"


def test_critical_fields_for_data_center_include_power_and_cooling_anchors():
    fields = {row.field_name for row in critical_fields_for_asset_type(AssetType.DATA_CENTER)}
    assert "critical_load_anchor" in fields
    assert "cooling_or_redundancy_clue" in fields
    assert "utility_tariff_or_power_context" in fields


def test_default_evidence_gating_plan_uses_threshold_of_three_missing_fields():
    plan = default_evidence_gating_plan(AssetType.COMMERCIAL_BUILDING)
    assert plan.max_missing_critical_fields == 3
    assert plan.blocked_report_type == "Decision-Blocked Brief"
    assert plan.partial_report_type == "Minimum Evidence Report"
    assert plan.sufficient_report_type == "Full Technical Report"


def test_only_operating_like_targets_allow_technical_scraping():
    assert technical_scraping_allowed_for_target_class(TargetClassification.OPERATING_ASSET) is True
    assert technical_scraping_allowed_for_target_class(TargetClassification.INDUSTRIAL_FACILITY) is True
    assert technical_scraping_allowed_for_target_class(TargetClassification.CORPORATE_HEADQUARTERS) is False
