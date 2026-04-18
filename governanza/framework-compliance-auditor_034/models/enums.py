from __future__ import annotations

from enum import Enum


class StrEnum(str, Enum):
    """Small compatibility enum for Python 3.10."""

    def __str__(self) -> str:
        return self.value


class DocumentRole(StrEnum):
    NORMATIVE_CONTRACT = "normative_contract"
    OBJECT_UNDER_REVIEW = "object_under_review"
    REFERENCE_ANCHOR = "reference_anchor"


class RuleKind(StrEnum):
    REQUIRED = "required"
    FORBIDDEN = "forbidden"
    ALLOWED = "allowed"
    DEFINITIONAL = "definitional"
    HARD_BOUNDARY = "hard_boundary"
    CAUTION = "caution"
    CONDITIONAL = "conditional"
    EXAMPLE = "example"
    NOTE = "note"
    SCOPE = "scope"
    ESCALATION_BOUNDARY = "escalation_boundary"
    SEMANTIC_OVERREACH = "semantic_overreach"
    CERTAINTY_CONSTRAINT = "certainty_constraint"
    VERIFICATION_BOUNDARY = "verification_boundary"
    REPORTING_CONSTRAINT = "reporting_constraint"
    TRACEABILITY_EXPECTATION = "traceability_expectation"


class RuleCategory(StrEnum):
    ADMISSIBILITY = "admissibility"
    SCOPE = "scope"
    REPORTING = "reporting"
    EVIDENCE = "evidence"
    TRACEABILITY = "traceability"
    CERTAINTY = "certainty"
    VERIFICATION = "verification"
    VALIDATION = "validation"
    ESCALATION = "escalation"
    RECOMMENDATION = "recommendation"
    FINANCIAL = "financial"
    REGULATORY = "regulatory"
    EXAMPLE = "example"
    GENERAL = "general"


class ClaimType(StrEnum):
    DESCRIPTIVE = "descriptive"
    BENCHMARK = "benchmark"
    INTERPRETIVE = "interpretive"
    DIAGNOSTIC = "diagnostic"
    CAUSAL = "causal"
    RECOMMENDATION = "recommendation"
    SAVINGS = "savings"
    VERIFICATION_LIKE = "verification_like"
    COMPLIANCE_LIKE = "compliance_like"
    UNCERTAINTY = "uncertainty"
    VALIDATION_PATH = "validation_path"


class ConfidenceLanguageLevel(StrEnum):
    LOW = "low"
    MODERATE = "moderate"
    HIGH = "high"
    ABSOLUTE = "absolute"
    VERIFICATION_GRADE = "verification_grade"
    COMPLIANCE_GRADE = "compliance_grade"
    UNKNOWN = "unknown"


class SourceUnitType(StrEnum):
    SECTION = "section"
    SUBSECTION = "subsection"
    PARAGRAPH = "paragraph"
    BULLET = "bullet"
    TABLE = "table"
    CAPTION = "caption"
    CALLOUT = "callout"


class ComplianceVerdict(StrEnum):
    COMPLIANT = "compliant"
    PARTIALLY_COMPLIANT = "partially_compliant"
    NON_COMPLIANT = "non_compliant"
    INDETERMINATE = "indeterminate"


class Severity(StrEnum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class GateStatus(StrEnum):
    PASS = "pass"
    WARN = "warn"
    FAIL = "fail"


class FixAction(StrEnum):
    KEEP = "keep"
    REMOVE = "remove"
    SOFTEN = "soften"
    QUALIFY = "qualify"
    SPLIT = "split"
    RELOCATE = "relocate"
    DEFER = "defer"
    BLOCK = "block"
    ADD_TRACEABILITY = "add_traceability"
    ADD_CAVEAT = "add_caveat"
    ADD_HARDENING_PATH = "add_hardening_path"


class ViolationType(StrEnum):
    SEMANTIC_OVERREACH = "semantic_overreach"
    VERIFICATION_WITHOUT_AUTHORIZATION = "verification_language_without_authorization"
    CAUSAL_CLOSURE_WITHOUT_SUPPORT = "causal_closure_without_support"
    RECOMMENDATION_ESCALATION = "recommendation_escalation_beyond_phase_scope"
    NARRATIVE_STRENGTHENING = "narrative_strengthening_of_claims"
    UNCERTAINTY_SUPPRESSION = "suppression_of_uncertainty"
    REPORT_PACKAGE_INFLATION = "report_package_inflation"
    BENCHMARK_TO_SITE_SLIPPAGE = "benchmark_to_site_slippage"
    PROXY_TO_HARD_CLAIM_SLIPPAGE = "proxy_to_hard_claim_slippage"
    MISSING_VALIDATION_CAVEAT = "missing_validation_caveat"
    HARDENING_PATH_OMISSION = "hardening_path_omission"
    TRACEABILITY_WEAKENING = "traceability_weakening"
    CONTRACT_RULE_MATCH = "contract_rule_match"


class ReferenceDimension(StrEnum):
    TECHNICAL_DENSITY = "technical_density"
    METHODOLOGICAL_EXPLICITNESS = "methodological_explicitness"
    UNCERTAINTY_HANDLING_MATURITY = "uncertainty_handling_maturity"
    FINANCIAL_SERIOUSNESS = "financial_seriousness"
    REGULATORY_SERIOUSNESS = "regulatory_seriousness"
    MARKET_COMPARISON_SHARPNESS = "market_comparison_sharpness"
    STRUCTURE_QUALITY = "structure_quality"
    RECOMMENDATION_MATURITY = "recommendation_maturity"
    EVIDENCE_DISCUSSION_DEPTH = "evidence_discussion_depth"
    SENIOR_REPORT_FEEL = "senior_report_feel"

