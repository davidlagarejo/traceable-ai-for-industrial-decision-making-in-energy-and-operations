from __future__ import annotations

from dataclasses import asdict, dataclass, field, is_dataclass
from enum import Enum
from typing import Any


def _serialize(value: Any) -> Any:
    if isinstance(value, Enum):
        return value.value
    if is_dataclass(value):
        return {key: _serialize(item) for key, item in asdict(value).items()}
    if isinstance(value, dict):
        return {key: _serialize(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_serialize(item) for item in value]
    if isinstance(value, tuple):
        return [_serialize(item) for item in value]
    return value


class TargetClassification(str, Enum):
    OPERATING_ASSET = "OPERATING_ASSET"
    CORPORATE_HEADQUARTERS = "CORPORATE_HEADQUARTERS"
    MAILING_ADDRESS = "MAILING_ADDRESS"
    PORTFOLIO_ENTITY = "PORTFOLIO_ENTITY"
    PROPERTY_LISTING = "PROPERTY_LISTING"
    INDUSTRIAL_FACILITY = "INDUSTRIAL_FACILITY"
    DATA_CENTER = "DATA_CENTER"
    AMBIGUOUS_TARGET = "AMBIGUOUS_TARGET"
    INVALID_TARGET = "INVALID_TARGET"


class AssetType(str, Enum):
    COMMERCIAL_BUILDING = "commercial_building"
    MULTIFAMILY = "multifamily"
    INDUSTRIAL_FACILITY = "industrial_facility"
    WAREHOUSE_LOGISTICS = "warehouse_logistics"
    DATA_CENTER = "data_center"


class DecisionType(str, Enum):
    TARGET_IDENTIFICATION = "target_identification"
    ACQUISITION_UNDERWRITING = "acquisition_underwriting"
    RETROFIT_CAPEX = "retrofit_capex"
    COMPLIANCE_INVESTMENT = "compliance_investment"
    PROCESS_CHANGE = "process_change"
    REFINANCING = "refinancing"


class JurisdictionClass(str, Enum):
    HIGH_DATA_AVAILABILITY_BUILDING = "high_data_availability_building"
    UTILITY_AND_PERMIT_BUILDING = "utility_and_permit_building"
    INDUSTRIAL_REGULATED = "industrial_regulated"
    LOW_PUBLIC_DATA_ASSET = "low_public_data_asset"
    AMBIGUOUS_JURISDICTION = "ambiguous_jurisdiction"


class SourceLayer(str, Enum):
    ENERGY = "energy"
    REGULATORY = "regulatory"
    PROPERTY = "property"
    PERMIT = "permit"
    UTILITY = "utility"
    CLIMATE = "climate"
    ENTITY_FINANCE = "entity_finance"
    INDUSTRIAL_ENVIRONMENT = "industrial_environment"
    BENCHMARK = "benchmark"
    SEARCH_FALLBACK = "search_fallback"


class AccessMethod(str, Enum):
    API = "api"
    DOWNLOAD = "download"
    PORTAL = "portal"
    WEB_PAGE = "web_page"
    FILE_EXPORT = "file_export"
    ROUTED_SEARCH = "routed_search"


class AuthorityTier(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class RoutingPriority(str, Enum):
    MANDATORY = "mandatory"
    HIGH_PRIORITY = "high_priority"
    OPTIONAL = "optional"


@dataclass(frozen=True)
class TargetClassificationResult:
    target_type: TargetClassification
    classification_confidence: str
    asset_identity_confirmed: bool
    technical_scraping_allowed: bool
    report_type_if_blocked: str
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class JurisdictionResolution:
    country: str
    state: str
    city: str
    county: str
    utility_territory: str
    climate_zone_ashrae: str
    jurisdiction_class: JurisdictionClass
    regulatory_stack: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class SourceRoutingEntry:
    source_key: str
    source_name: str
    layer: SourceLayer
    access_method: AccessMethod
    fields: list[str]
    authority: AuthorityTier
    update_frequency: str
    use: str
    limitations: str
    priority: RoutingPriority
    disallowed_as_substitute_for: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class SourceRegistryRecord:
    jurisdiction: str
    asset_type: AssetType
    source: SourceRoutingEntry

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class SourceRoutingPlan:
    jurisdiction: str
    asset_type: AssetType
    decision_type: DecisionType
    mandatory_sources: list[SourceRoutingEntry] = field(default_factory=list)
    high_priority_sources: list[SourceRoutingEntry] = field(default_factory=list)
    optional_sources: list[SourceRoutingEntry] = field(default_factory=list)
    disallowed_substitutions: list[str] = field(default_factory=list)
    routing_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class AssetTypeRoute:
    asset_type: AssetType
    route_name: str
    primary_decision_anchors: list[str] = field(default_factory=list)
    critical_field_family: list[str] = field(default_factory=list)
    prohibited_shortcuts: list[str] = field(default_factory=list)
    routing_notes: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class CriticalFieldRequirement:
    field_name: str
    rationale: str
    blocking_if_missing: bool
    minimum_source_layer: SourceLayer
    prohibited_substitutions: list[str] = field(default_factory=list)

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class CriticalFieldStatus:
    field_name: str
    required: bool
    current_status: str
    rationale: str
    minimum_source_layer: SourceLayer
    prohibited_substitutions: list[str] = field(default_factory=list)
    notes: str = ""

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class EvidenceGatingPlan:
    critical_fields: list[CriticalFieldRequirement]
    max_missing_critical_fields: int
    blocked_report_type: str
    partial_report_type: str
    sufficient_report_type: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)


@dataclass(frozen=True)
class ReportTypeSwitchRecommendation:
    recommended_report_type: str
    prohibited_report_types: list[str]
    reason: str

    def to_dict(self) -> dict[str, Any]:
        return _serialize(self)
