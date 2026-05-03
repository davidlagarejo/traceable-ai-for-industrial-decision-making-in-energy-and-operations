from __future__ import annotations

from .schemas import AssetType, ReportTypeSwitchRecommendation, TargetClassification, TargetClassificationResult


TARGET_TYPE_ALIASES: dict[str, AssetType] = {
    "commercial_building": AssetType.COMMERCIAL_BUILDING,
    "multifamily_building": AssetType.MULTIFAMILY,
    "multifamily": AssetType.MULTIFAMILY,
    "industrial_plant": AssetType.INDUSTRIAL_FACILITY,
    "manufacturing_facility": AssetType.INDUSTRIAL_FACILITY,
    "industrial_facility": AssetType.INDUSTRIAL_FACILITY,
    "food_processing_facility": AssetType.INDUSTRIAL_FACILITY,
    "cold_chain_facility": AssetType.INDUSTRIAL_FACILITY,
    "warehouse_distribution": AssetType.WAREHOUSE_LOGISTICS,
    "warehouse_logistics": AssetType.WAREHOUSE_LOGISTICS,
    "data_center": AssetType.DATA_CENTER,
}


TECHNICAL_ROUTE_ELIGIBLE = {
    TargetClassification.OPERATING_ASSET,
    TargetClassification.INDUSTRIAL_FACILITY,
    TargetClassification.DATA_CENTER,
}


REPORT_SWITCH_BY_TARGET_CLASS: dict[TargetClassification, ReportTypeSwitchRecommendation] = {
    TargetClassification.OPERATING_ASSET: ReportTypeSwitchRecommendation(
        recommended_report_type="Decision-Blocked Brief",
        prohibited_report_types=["Target Classification Brief"],
        reason="Target is an operating asset, so technical routing may proceed subject to evidence gates.",
    ),
    TargetClassification.INDUSTRIAL_FACILITY: ReportTypeSwitchRecommendation(
        recommended_report_type="Decision-Blocked Brief",
        prohibited_report_types=["Target Classification Brief"],
        reason="Target is an industrial facility, so technical routing may proceed subject to evidence gates.",
    ),
    TargetClassification.DATA_CENTER: ReportTypeSwitchRecommendation(
        recommended_report_type="Decision-Blocked Brief",
        prohibited_report_types=["Target Classification Brief"],
        reason="Target is a data center asset, so technical routing may proceed subject to evidence gates.",
    ),
    TargetClassification.CORPORATE_HEADQUARTERS: ReportTypeSwitchRecommendation(
        recommended_report_type="Target Classification Brief",
        prohibited_report_types=["Full Technical Report", "Minimum Evidence Report"],
        reason="Headquarters context is not admissible as technical asset truth.",
    ),
    TargetClassification.MAILING_ADDRESS: ReportTypeSwitchRecommendation(
        recommended_report_type="Target Classification Brief",
        prohibited_report_types=["Full Technical Report", "Minimum Evidence Report"],
        reason="Mailing-address context is not admissible as technical asset truth.",
    ),
    TargetClassification.PORTFOLIO_ENTITY: ReportTypeSwitchRecommendation(
        recommended_report_type="Target Classification Brief",
        prohibited_report_types=["Full Technical Report", "Minimum Evidence Report"],
        reason="Portfolio-level context may not be treated as a single technical asset.",
    ),
    TargetClassification.PROPERTY_LISTING: ReportTypeSwitchRecommendation(
        recommended_report_type="Minimum Evidence Report",
        prohibited_report_types=["Full Technical Report"],
        reason="A property listing may support bounded prior-building work but not a strong technical report by itself.",
    ),
    TargetClassification.AMBIGUOUS_TARGET: ReportTypeSwitchRecommendation(
        recommended_report_type="Target Clarification Brief",
        prohibited_report_types=["Full Technical Report", "Minimum Evidence Report"],
        reason="Asset identity is still ambiguous.",
    ),
    TargetClassification.INVALID_TARGET: ReportTypeSwitchRecommendation(
        recommended_report_type="Target Classification Brief",
        prohibited_report_types=["Full Technical Report", "Minimum Evidence Report"],
        reason="The target is not evaluable under current public-routing rules.",
    ),
}


def normalize_asset_type(value: str | AssetType | None) -> AssetType | None:
    if isinstance(value, AssetType):
        return value
    key = str(value or "").strip().lower()
    return TARGET_TYPE_ALIASES.get(key)


def technical_scraping_allowed_for_target_class(target_class: TargetClassification | str) -> bool:
    normalized = normalize_target_classification(target_class)
    return normalized in TECHNICAL_ROUTE_ELIGIBLE


def normalize_target_classification(value: TargetClassification | str | None) -> TargetClassification:
    if isinstance(value, TargetClassification):
        return value
    normalized = str(value or "").strip().upper()
    alias_map = {
        "REGISTERED_AGENT_OR_MAILING_ADDRESS": TargetClassification.MAILING_ADDRESS,
        "OPERATING_ASSET": TargetClassification.OPERATING_ASSET,
        "CORPORATE_HEADQUARTERS": TargetClassification.CORPORATE_HEADQUARTERS,
        "PORTFOLIO_ENTITY": TargetClassification.PORTFOLIO_ENTITY,
        "PROPERTY_LISTING": TargetClassification.PROPERTY_LISTING,
        "INDUSTRIAL_FACILITY": TargetClassification.INDUSTRIAL_FACILITY,
        "DATA_CENTER": TargetClassification.DATA_CENTER,
        "AMBIGUOUS_TARGET": TargetClassification.AMBIGUOUS_TARGET,
        "INVALID_TARGET": TargetClassification.INVALID_TARGET,
    }
    return alias_map.get(normalized, TargetClassification.AMBIGUOUS_TARGET)


def make_target_classification_result(
    target_class: TargetClassification | str,
    *,
    classification_confidence: str,
    asset_identity_confirmed: bool,
    reason: str,
) -> TargetClassificationResult:
    normalized = normalize_target_classification(target_class)
    recommendation = REPORT_SWITCH_BY_TARGET_CLASS[normalized]
    return TargetClassificationResult(
        target_type=normalized,
        classification_confidence=classification_confidence,
        asset_identity_confirmed=asset_identity_confirmed,
        technical_scraping_allowed=technical_scraping_allowed_for_target_class(normalized),
        report_type_if_blocked=recommendation.recommended_report_type,
        reason=reason,
    )
